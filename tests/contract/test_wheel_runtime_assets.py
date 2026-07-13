from __future__ import annotations

import subprocess
from pathlib import Path
from shutil import copy2, copytree
from zipfile import ZipFile

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPO_ROOT / "src" / "mingli_engine"


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


def test_task_one_wheel_keeps_distribution_version_0_1_0(
    built_wheel: Path,
) -> None:
    with ZipFile(built_wheel) as wheel:
        metadata_name = next(
            name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")
        )
        metadata = wheel.read(metadata_name).decode("utf-8")

    assert "Version: 0.1.0\n" in metadata.replace("\r\n", "\n")
