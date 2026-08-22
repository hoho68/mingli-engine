from __future__ import annotations

from base64 import urlsafe_b64encode
from dataclasses import asdict
from hashlib import sha256
from inspect import signature
import json
import subprocess
from pathlib import Path, PurePosixPath
from shutil import copy2, copytree, ignore_patterns
from zipfile import ZipFile

import pytest

import mingli_engine.packaging_validation as packaging_validation


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPO_ROOT / "src" / "mingli_engine"
SOURCE_ONLY_DATA_ROOT = PACKAGE_ROOT / "data" / "new_material_learning"
NON_DISCLOSURE_FILENAME_MARKER = "内部资料、不能外泄"


class _InstalledDistribution:
    def __init__(
        self,
        installed_root: Path,
        package_root: Path,
        *,
        name: str = "Mingli.Engine",
        version: str | None = "0.1.0",
        wheel_exists: bool = True,
        record_exists: bool = True,
        direct_url: str | None = None,
        omitted_files: frozenset[str] = frozenset(),
        omitted_record_entries: frozenset[str] = frozenset(),
        extra_entries: frozenset[str] = frozenset(),
        record_overrides: dict[str, tuple[str, str]] | None = None,
    ) -> None:
        self._installed_root = installed_root
        self._wheel_exists = wheel_exists
        self._record_exists = record_exists
        self._direct_url = direct_url
        self.metadata = {"Name": name}
        if version is not None:
            self.metadata["Version"] = version
        package_entries = {
            f"mingli_engine/{path.relative_to(package_root).as_posix()}"
            for path in package_root.rglob("*")
            if path.is_file() and path.suffix in {".py", ".json", ".pdf", ".docx"}
        }
        dist_info = "mingli_engine-0.1.0.dist-info"
        metadata_entries = {
            f"{dist_info}/METADATA",
            f"{dist_info}/WHEEL",
            f"{dist_info}/RECORD",
        }
        metadata_payloads = {
            f"{dist_info}/METADATA": b"Name: mingli-engine\nVersion: 0.1.0\n",
            f"{dist_info}/WHEEL": b"Wheel-Version: 1.0\n",
        }
        if direct_url is not None:
            direct_url_path = f"{dist_info}/direct_url.json"
            metadata_entries.add(direct_url_path)
            metadata_payloads[direct_url_path] = direct_url.encode("utf-8")
        for path, payload in metadata_payloads.items():
            installed_path = self._installed_root / path
            installed_path.parent.mkdir(parents=True, exist_ok=True)
            installed_path.write_bytes(payload)
        all_entries = package_entries | metadata_entries | extra_entries
        self.files = tuple(
            PurePosixPath(path) for path in sorted(all_entries - omitted_files)
        )
        self._record_entries = tuple(
            sorted(all_entries - omitted_record_entries)
        )
        self._record_overrides = record_overrides or {}
        record_rows: list[str] = []
        for path in self._record_entries:
            installed_path = self._installed_root / path
            if path in self._record_overrides:
                record_hash, record_size = self._record_overrides[path]
            elif installed_path.is_file() and not path.endswith(".dist-info/RECORD"):
                payload = installed_path.read_bytes()
                record_hash = "sha256=" + urlsafe_b64encode(
                    sha256(payload).digest()
                ).rstrip(b"=").decode("ascii")
                record_size = str(len(payload))
            else:
                record_hash, record_size = "", ""
            record_rows.append(f"{path},{record_hash},{record_size}\n")
        self._record_text = "".join(record_rows)
        record_path = self._installed_root / f"{dist_info}/RECORD"
        record_path.write_text(self._record_text, encoding="utf-8", newline="")

    @property
    def version(self) -> str:
        return self.metadata.get("Version", "")

    def locate_file(self, path: str) -> Path:
        return self._installed_root / path

    def read_text(self, filename: str) -> str | None:
        if filename == "WHEEL" and self._wheel_exists:
            return "Wheel-Version: 1.0\n"
        if filename == "RECORD" and self._record_exists:
            return self._record_text
        if filename == "direct_url.json":
            return self._direct_url
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
        ["uv", "build", "--offline", "--wheel", "--out-dir", str(output_dir)],
        cwd=staged_project,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    wheels = tuple(output_dir.glob("*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def _source_runtime_json_assets() -> set[str]:
    return {
        path.relative_to(PACKAGE_ROOT).as_posix()
        for path in (PACKAGE_ROOT / "data").rglob("*.json")
        if not path.is_relative_to(SOURCE_ONLY_DATA_ROOT)
        and not _is_governance_only_liuyao_asset(path)
    }


def _is_governance_only_liuyao_asset(path: Path) -> bool:
    liuyao_root = PACKAGE_ROOT / "data" / "liuyao"
    if not path.is_relative_to(liuyao_root):
        return False
    return path.name not in {"gua_reference.json", "analysis_config.json"}


def _asset_hashes(package_root: Path) -> dict[str, str]:
    source_only_root = package_root / "data" / "new_material_learning"
    return {
        path.relative_to(package_root).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in sorted((package_root / "data").rglob("*.json"))
        if not path.is_relative_to(source_only_root)
    }


def _copy_package_data(
    tmp_path: Path,
    *,
    include_source_only_data: bool = False,
) -> tuple[Path, Path]:
    installed_root = tmp_path / "target"
    package_root = installed_root / "mingli_engine"
    liuyao_governance_names = (
        "liuyao_sources.json",
        "liuyao_candidates.json",
        "liuyao_review_decisions.json",
        "liuyao_promotion_batches.json",
        "liuyao_evidence_units.json",
        "batch_20260714_liuyao_family_map.json",
        "calibration",
    )
    copytree(
        PACKAGE_ROOT,
        package_root,
        ignore=ignore_patterns(
            *(".gitkeep", "__pycache__", "new_material_learning", *liuyao_governance_names)
            if not include_source_only_data
            else (".gitkeep", "__pycache__")
        ),
    )
    return installed_root, package_root


def _patch_package_context(
    monkeypatch: pytest.MonkeyPatch,
    installed_root: Path,
    package_root: Path,
) -> None:
    distribution = _InstalledDistribution(installed_root, package_root)
    monkeypatch.setattr(
        packaging_validation.resources,
        "files",
        lambda package: package_root,
    )
    monkeypatch.setattr(
        packaging_validation.metadata,
        "distribution",
        lambda name: distribution,
    )


def _patch_isolated_distribution(
    monkeypatch: pytest.MonkeyPatch,
    package_root: Path,
    distribution: _InstalledDistribution,
) -> None:
    monkeypatch.setattr(
        packaging_validation.resources,
        "files",
        lambda package: package_root,
    )
    monkeypatch.setattr(
        packaging_validation.metadata,
        "distribution",
        lambda name: distribution,
    )
    monkeypatch.setattr(
        packaging_validation,
        "_loaded_package_paths",
        lambda: tuple(sorted(package_root.rglob("*.py"))),
    )


def test_wheel_contains_complete_runtime_json_closure(built_wheel: Path) -> None:
    with ZipFile(built_wheel) as wheel:
        wheel_assets = {
            name.removeprefix("mingli_engine/")
            for name in wheel.namelist()
            if name.startswith("mingli_engine/data/") and name.endswith(".json")
        }

    source_assets = _source_runtime_json_assets()
    source_only_assets = {
        path.relative_to(PACKAGE_ROOT).as_posix()
        for path in SOURCE_ONLY_DATA_ROOT.glob("*.json")
    }
    assert "data/calculation/strength_weights.json" in source_assets
    assert "data/calculation/school_profiles.json" in source_assets
    assert "data/classical_sources/evidence_units.json" in source_assets
    assert "data/domain_calibration/v2/executable_fixtures.json" in wheel_assets
    assert source_only_assets
    assert wheel_assets.isdisjoint(source_only_assets)
    assert wheel_assets == source_assets


def test_wheel_contains_only_declared_package_members(built_wheel: Path) -> None:
    expected = {
        f"mingli_engine/{path.relative_to(PACKAGE_ROOT).as_posix()}"
        for path in PACKAGE_ROOT.rglob("*.py")
    } | {
        f"mingli_engine/{path}" for path in packaging_validation.EXPECTED_RUNTIME_JSON_ASSETS
    }
    with ZipFile(built_wheel) as wheel:
        actual = {
            name
            for name in wheel.namelist()
            if name.startswith("mingli_engine/") and not name.endswith("/")
        }

    assert actual == expected


def test_verifier_manifest_freezes_complete_runtime_json_closure() -> None:
    assert packaging_validation.EXPECTED_RUNTIME_JSON_ASSETS == tuple(
        sorted(_source_runtime_json_assets())
    )


def test_wheel_does_not_disclose_source_only_ledger_values(
    built_wheel: Path,
) -> None:
    manifest = json.loads(
        (SOURCE_ONLY_DATA_ROOT / "batch_20260714_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    intake_root = manifest["intake_root"]
    source_hashes = {record["sha256"] for record in manifest["files"]}
    assert Path(intake_root).is_absolute()
    assert source_hashes
    assert any(
        NON_DISCLOSURE_FILENAME_MARKER in record["relative_path"]
        for record in manifest["files"]
    )

    with ZipFile(built_wheel) as wheel:
        member_names = wheel.namelist()
        member_payload = b"\0".join(
            wheel.read(name) for name in member_names if not name.endswith("/")
        )

    assert not any(
        name.startswith("mingli_engine/data/new_material_learning/")
        for name in member_names
    )
    disclosure_values = {
        intake_root,
        NON_DISCLOSURE_FILENAME_MARKER,
        *source_hashes,
        *(value.lower() for value in source_hashes),
    }
    for value in disclosure_values:
        direct = value.encode("utf-8")
        json_escaped = json.dumps(value, ensure_ascii=False)[1:-1].encode("utf-8")
        assert direct not in member_payload
        assert json_escaped not in member_payload


@pytest.mark.parametrize("metadata_location", ("distribution_files", "record"))
def test_verifier_rejects_source_only_operational_ledgers_in_metadata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    metadata_location: str,
) -> None:
    installed_root, package_root = _copy_package_data(
        tmp_path,
        include_source_only_data=True,
    )
    source_only_entries = frozenset(
        f"mingli_engine/{path.relative_to(package_root).as_posix()}"
        for path in (package_root / "data" / "new_material_learning").rglob("*")
        if path.is_file()
    )
    assert source_only_entries
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        omitted_files=(
            source_only_entries
            if metadata_location == "record"
            else frozenset()
        ),
        omitted_record_entries=(
            source_only_entries
            if metadata_location == "distribution_files"
            else frozenset()
        ),
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.overall_status == "failed"
    assert result.source_isolated is False
    assert result.asset_sha256 == _asset_hashes(package_root)
    assert not any(
        path.startswith("data/new_material_learning/")
        for path in result.asset_sha256
    )


def test_verifier_rejects_unexpected_raw_package_member(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    raw_path = package_root / "private" / "raw_material.pdf"
    raw_path.parent.mkdir()
    raw_path.write_bytes(b"private")
    distribution = _InstalledDistribution(installed_root, package_root)
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.overall_status == "failed"
    assert result.source_isolated is False


@pytest.mark.parametrize(
    "unexpected_kind",
    ("python_module", "top_level_package", "unrecorded_member"),
)
def test_verifier_rejects_every_unexpected_distribution_member(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    unexpected_kind: str,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    extra_entries: frozenset[str] = frozenset()
    if unexpected_kind == "python_module":
        (package_root / "unexpected.py").write_text("VALUE = 1\n", encoding="utf-8")
    elif unexpected_kind == "top_level_package":
        extra_entries = frozenset({"other_package/__init__.py"})
    else:
        hidden = package_root / "private" / "hidden.txt"
        hidden.parent.mkdir()
        hidden.write_text("private", encoding="utf-8")
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        extra_entries=extra_entries,
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.overall_status == "failed"
    assert result.source_isolated is False


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
        lambda name: _InstalledDistribution(
            installed_root,
            package_root,
            direct_url='{"dir_info":{"editable":true}}',
        ),
    )
    monkeypatch.setattr(
        packaging_validation,
        "_loaded_package_paths",
        lambda: (package_root / "packaging_validation.py",),
    )

    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is False
    assert result.overall_status == "failed"


def test_missing_record_metadata_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        record_exists=False,
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is False
    assert result.overall_status == "failed"


def test_missing_version_metadata_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        version=None,
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.distribution_version == "not_installed"
    assert result.source_isolated is False
    assert result.overall_status == "failed"


@pytest.mark.parametrize(
    "direct_url",
    (
        "not-json",
        "{}",
        '{"dir_info":{}}',
        '{"dir_info":{"editable":"false"}}',
        '{"dir_info":{"editable":null}}',
    ),
)
def test_malformed_direct_url_editable_metadata_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    direct_url: str,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        direct_url=direct_url,
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is False
    assert result.overall_status == "failed"


@pytest.mark.parametrize(
    "direct_url",
    (
        '{"url":"file:///tmp/mingli.whl","archive_info":{}}',
        (
            '{"url":"https://example.com/mingli.whl","archive_info":'
            '{"hash":"sha256=0123456789abcdef"}}'
        ),
        (
            '{"url":"https://example.com/repo.git","vcs_info":'
            '{"vcs":"git","requested_revision":"main",'
            '"commit_id":"0123456789abcdef"},"subdirectory":"package"}'
        ),
        '{"url":"file:///tmp/source","dir_info":{"editable":false}}',
    ),
)
def test_valid_pep610_direct_url_metadata_is_accepted(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    direct_url: str,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        direct_url=direct_url,
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is True
    assert result.overall_status == "verified"


@pytest.mark.parametrize(
    "direct_url",
    (
        (
            '{"url":"file:///tmp/mingli.whl","archive_info":{},'
            '"dir_info":{"editable":false}}'
        ),
        '{"url":"file:///tmp/mingli.whl","wheel_info":{}}',
        (
            '{"url":"file:///tmp/mingli.whl","archive_info":'
            '{"unknown":"value"}}'
        ),
        '{"url":"relative/path.whl","archive_info":{}}',
        (
            '{"url":"https://user:secret@example.com/mingli.whl",'
            '"archive_info":{}}'
        ),
        '{"url":"file://","archive_info":{}}',
        '{"dir_info":{"editable":false}}',
    ),
)
def test_unknown_conflicting_or_invalid_pep610_metadata_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    direct_url: str,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        direct_url=direct_url,
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is False
    assert result.overall_status == "failed"


def test_record_must_cover_every_runtime_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    missing_entry = (
        "mingli_engine/data/source_library/source_priority_assessments.json"
    )
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        omitted_record_entries=frozenset({missing_entry}),
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is False
    assert result.overall_status == "failed"


@pytest.mark.parametrize(
    "record_value",
    (
        ("", "1"),
        ("sha256=" + "0" * 64, "1"),
        ("sha256=invalid+standard/base64=", "1"),
        ("sha256=" + "A" * 43, "01"),
    ),
)
def test_record_requires_canonical_hash_and_size_for_every_package_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    record_value: tuple[str, str],
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    target = "mingli_engine/packaging_validation.py"
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        record_overrides={target: record_value},
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is False
    assert result.overall_status == "failed"


@pytest.mark.parametrize(
    "relative_path",
    (
        "mingli_engine/packaging_validation.py",
        "mingli_engine-0.1.0.dist-info/METADATA",
    ),
)
def test_record_rejects_same_path_content_tampering(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    relative_path: str,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    distribution = _InstalledDistribution(installed_root, package_root)
    target = installed_root / relative_path
    payload = target.read_bytes()
    target.write_bytes(bytes([payload[0] ^ 1]) + payload[1:])
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is False
    assert result.overall_status == "failed"


def test_record_rejects_duplicate_normalized_paths() -> None:
    assert packaging_validation._record_entries("a.py,,\na.py,,\n") is None


@pytest.mark.parametrize(
    "extra_path",
    (
        "other.dist-info/private.json",
        "mingli_engine-0.1.0.dist-info/private.json",
        "mingli_engine/nested.dist-info/private.json",
    ),
)
def test_distribution_rejects_undeclared_dist_info_payloads(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    extra_path: str,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        extra_entries=frozenset({extra_path}),
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

    result = packaging_validation.build_packaging_verification()

    assert result.source_isolated is False
    assert result.overall_status == "failed"


def test_distribution_files_must_cover_every_package_module(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    installed_root, package_root = _copy_package_data(tmp_path)
    distribution = _InstalledDistribution(
        installed_root,
        package_root,
        omitted_files=frozenset({"mingli_engine/packaging_validation.py"}),
    )
    _patch_isolated_distribution(monkeypatch, package_root, distribution)

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
