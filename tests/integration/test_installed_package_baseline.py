from __future__ import annotations

from hashlib import sha256
import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest


pytest_plugins = ("tests.contract.test_wheel_runtime_assets",)

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPO_ROOT / "src" / "mingli_engine"


@pytest.fixture(scope="module")
def installed_target(
    tmp_path_factory: pytest.TempPathFactory,
    built_wheel: Path,
) -> Path:
    work_dir = tmp_path_factory.mktemp("installed-package-build")
    target_dir = work_dir / "target"
    target_dir.mkdir()

    installed = subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--target",
            str(target_dir),
            "--no-deps",
            str(built_wheel),
        ],
        cwd=work_dir,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    assert installed.returncode == 0, installed.stderr
    return target_dir


def _run_isolated(
    installed_target: Path,
    cwd: Path,
    script: str,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(installed_target)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=cwd,
        env=environment,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def _source_asset_hashes() -> dict[str, str]:
    return {
        path.relative_to(PACKAGE_ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in sorted((PACKAGE_ROOT / "data").rglob("*.json"))
    }


def test_installed_package_runs_chart_analysis_and_evidence_report_outside_checkout(
    installed_target: Path,
    tmp_path: Path,
) -> None:
    script = dedent(
        """
        from datetime import datetime
        import json
        from pathlib import Path

        import mingli_engine
        from mingli_engine.bazi import analyze_bazi_chart
        from mingli_engine.chart_calculator import calculate_bazi_chart
        from mingli_engine.models import BirthProfile
        from mingli_engine.report_schema import build_report

        profile = BirthProfile(
            calendar_type="gregorian",
            birth_date="1950-03-22",
            birth_time="09:30",
            birthplace="Shanghai",
            gender="female",
            focus_topic="career",
        )
        chart = calculate_bazi_chart(profile)
        analysis = analyze_bazi_chart(
            chart,
            birth_datetime=datetime.fromisoformat("1950-03-22T09:30"),
            selected_year=2030,
        )
        report = build_report(chart, analysis)
        print(json.dumps({
            "package_file": str(Path(mingli_engine.__file__).resolve()),
            "pillar_count": len(chart.pillars),
            "engine_version": analysis.engine_version,
            "formal_conclusion_count": len(
                report.expanded_evidence.formal_conclusions
            ),
            "evidence_status": report.report_evidence_audit.audit_status,
        }, sort_keys=True))
        """
    )

    completed = _run_isolated(installed_target, tmp_path, script)

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    result = json.loads(completed.stdout)
    assert Path(result["package_file"]).is_relative_to(installed_target)
    assert result == {
        "engine_version": "bazi-core-v1",
        "evidence_status": "complete_with_guardrails",
        "formal_conclusion_count": 10,
        "package_file": result["package_file"],
        "pillar_count": 4,
    }
    assert list(tmp_path.iterdir()) == []


def test_installed_packaging_verifier_is_exact_read_only_and_deterministic(
    installed_target: Path,
    tmp_path: Path,
) -> None:
    script = dedent(
        """
        from dataclasses import asdict
        import json

        from mingli_engine.packaging_validation import build_packaging_verification

        first = asdict(build_packaging_verification())
        second = asdict(build_packaging_verification())
        assert first == second
        print(json.dumps(first, sort_keys=True))
        """
    )
    target_before = {
        path.relative_to(installed_target).as_posix()
        for path in installed_target.rglob("*")
    }

    completed = _run_isolated(installed_target, tmp_path, script)

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    result = json.loads(completed.stdout)
    assert result == {
        "asset_sha256": _source_asset_hashes(),
        "distribution_version": "0.1.0",
        "overall_status": "verified",
        "source_isolated": True,
    }
    assert list(result["asset_sha256"]) == sorted(result["asset_sha256"])
    assert list(tmp_path.iterdir()) == []
    assert {
        path.relative_to(installed_target).as_posix()
        for path in installed_target.rglob("*")
    } == target_before
