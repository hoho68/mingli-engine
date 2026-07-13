from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from inspect import signature
import subprocess
from pathlib import Path
from shutil import copy2, copytree
from zipfile import ZipFile

import pytest

import mingli_engine.packaging_validation as packaging_validation


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPO_ROOT / "src" / "mingli_engine"


class _InstalledDistribution:
    version = "0.1.0"

    def __init__(self, installed_root: Path, *, editable: bool = False) -> None:
        self._installed_root = installed_root
        self._editable = editable

    def locate_file(self, path: str) -> Path:
        return self._installed_root / path

    def read_text(self, filename: str) -> str | None:
        if filename == "WHEEL":
            return "Wheel-Version: 1.0\n"
        if filename == "direct_url.json" and self._editable:
            return '{"dir_info":{"editable":true}}'
        return None


@pytest.fixture(scope="session")
def built_wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    work_dir = tmp_path_factory.mktemp("wheel-runtime-assets")
    staged_project = work_dir / "project"
    output_dir = work_dir / "wheel"
    staged_project.mkdir()
    output_dir.mkdir()
    copy2(REPO_ROOT / "pyproject.toml", staged_project / "pyproject.toml")
    copytree(REPO_ROOT / "src", staged_project / "src")
    completed = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(output_dir)],
        cwd=staged_project,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    wheels = tuple(output_dir.glob("*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def _source_json_assets() -> set[str]:
    return {
        path.relative_to(PACKAGE_ROOT).as_posix()
        for path in (PACKAGE_ROOT / "data").rglob("*.json")
    }


def _asset_hashes(package_root: Path) -> dict[str, str]:
    return {
        path.relative_to(package_root).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in sorted((package_root / "data").rglob("*.json"))
    }


def _copy_package_data(tmp_path: Path) -> tuple[Path, Path]:
    installed_root = tmp_path / "target"
    package_root = installed_root / "mingli_engine"
    package_root.mkdir(parents=True)
    copytree(PACKAGE_ROOT / "data", package_root / "data")
    return installed_root, package_root


def _patch_package_context(
    monkeypatch: pytest.MonkeyPatch,
    installed_root: Path,
    package_root: Path,
) -> None:
    monkeypatch.setattr(
        packaging_validation.resources,
        "files",
        lambda package: package_root,
    )
    monkeypatch.setattr(
        packaging_validation.metadata,
        "distribution",
        lambda name: _InstalledDistribution(installed_root),
    )


def test_wheel_contains_complete_runtime_json_closure(built_wheel: Path) -> None:
    with ZipFile(built_wheel) as wheel:
        wheel_assets = {
            name.removeprefix("mingli_engine/")
            for name in wheel.namelist()
            if name.startswith("mingli_engine/data/") and name.endswith(".json")
        }

    source_assets = _source_json_assets()
    assert "data/calculation/strength_weights.json" in source_assets
    assert "data/calculation/school_profiles.json" in source_assets
    assert "data/classical_sources/evidence_units.json" in source_assets
    assert wheel_assets == source_assets


def test_verifier_manifest_freezes_complete_runtime_json_closure() -> None:
    assert packaging_validation.EXPECTED_RUNTIME_JSON_ASSETS == tuple(
        sorted(_source_json_assets())
    )


def test_missing_data_root_returns_exact_failed_verification(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installed_root = tmp_path / "target"
    package_root = installed_root / "mingli_engine"
    package_root.mkdir(parents=True)
    _patch_package_context(monkeypatch, installed_root, package_root)

    result = packaging_validation.build_packaging_verification()

    assert asdict(result) == {
        "asset_sha256": {},
        "distribution_version": "0.1.0",
        "overall_status": "failed",
        "source_isolated": False,
    }


def test_resource_read_failure_returns_exact_failed_verification(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    _patch_package_context(monkeypatch, installed_root, package_root)
    original_read_bytes = Path.read_bytes

    def fail_package_reads(path: Path) -> bytes:
        if path.is_relative_to(package_root):
            raise PermissionError("private resource read failure")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", fail_package_reads)

    result = packaging_validation.build_packaging_verification()

    assert asdict(result) == {
        "asset_sha256": {},
        "distribution_version": "0.1.0",
        "overall_status": "failed",
        "source_isolated": False,
    }


def test_missing_metadata_returns_exact_failed_verification(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    _patch_package_context(monkeypatch, installed_root, package_root)

    def missing_distribution(name: str) -> _InstalledDistribution:
        raise packaging_validation.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(
        packaging_validation.metadata,
        "distribution",
        missing_distribution,
    )

    result = packaging_validation.build_packaging_verification()

    assert asdict(result) == {
        "asset_sha256": _asset_hashes(package_root),
        "distribution_version": "not_installed",
        "overall_status": "failed",
        "source_isolated": False,
    }


def test_nonisolated_paths_return_exact_failed_verification(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    _patch_package_context(monkeypatch, installed_root, package_root)

    result = packaging_validation.build_packaging_verification()

    assert asdict(result) == {
        "asset_sha256": _asset_hashes(package_root),
        "distribution_version": "0.1.0",
        "overall_status": "failed",
        "source_isolated": False,
    }


def test_source_checkout_without_context_never_reports_isolated() -> None:
    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is False
    assert result.overall_status == "failed"


def test_packaging_verifier_public_contract_is_parameterless() -> None:
    parameters = signature(
        packaging_validation.build_packaging_verification
    ).parameters
    assert tuple(parameters) == ()


def test_editable_wheel_metadata_never_reports_isolated(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    monkeypatch.setattr(
        packaging_validation.resources,
        "files",
        lambda package: package_root,
    )
    monkeypatch.setattr(
        packaging_validation.metadata,
        "distribution",
        lambda name: _InstalledDistribution(installed_root, editable=True),
    )
    monkeypatch.setattr(
        packaging_validation,
        "_loaded_package_paths",
        lambda: (package_root / "packaging_validation.py",),
    )

    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is False
    assert result.overall_status == "failed"


def test_task_one_wheel_keeps_distribution_version_0_1_0(
    built_wheel: Path,
) -> None:
    with ZipFile(built_wheel) as wheel:
        metadata_name = next(
            name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")
        )
        metadata = wheel.read(metadata_name).decode("utf-8")

    assert "Version: 0.1.0\n" in metadata.replace("\r\n", "\n")
