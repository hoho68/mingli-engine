import json
import shutil
from pathlib import Path

from mingli_engine import calculation_validation
from mingli_engine.calculation_validation import build_calculation_checks


EXPECTED_CHECKS = {
    "stages_present": "passed",
    "placeholder_integrity": "passed",
    "verified_fixture_count": "passed",
    "boundary_fixture_count": "passed",
    "three_school_profiles": "passed",
    "evidence_calculation_separation": "passed",
    "high_risk_guardrails": "passed",
    "no_persistence": "passed",
}


def test_calculation_checks_pass_the_v1_release_baseline():
    assert build_calculation_checks() == EXPECTED_CHECKS


def test_verified_fixture_gate_rejects_a_forged_pillar_artifact(
    tmp_path: Path,
):
    fixture_dir = tmp_path / "bazi_calculation"
    shutil.copytree(calculation_validation.DEFAULT_FIXTURE_DIR, fixture_dir)
    fixture_path = fixture_dir / "verified_charts.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    payload["records"][0]["verification"]["cross_provider_artifact"][
        "pillars"
    ][0]["gan_zhi"] = "forged"
    fixture_path.write_text(json.dumps(payload), encoding="utf-8")

    checks = build_calculation_checks(fixture_dir=fixture_dir)

    assert checks["verified_fixture_count"] == "failed"


def test_boundary_gate_rejects_metadata_without_the_backed_behavior(
    tmp_path: Path,
):
    fixture_dir = tmp_path / "bazi_calculation"
    shutil.copytree(calculation_validation.DEFAULT_FIXTURE_DIR, fixture_dir)
    fixture_path = fixture_dir / "luck_cycle_boundary_cases.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    payload["cases"][0]["fixture_metadata"]["demonstrated_behaviors"] = [
        "unbacked_label"
    ]
    fixture_path.write_text(json.dumps(payload), encoding="utf-8")

    checks = build_calculation_checks(fixture_dir=fixture_dir)

    assert checks["boundary_fixture_count"] == "failed"


def test_validator_detects_runtime_probe_writes(monkeypatch, tmp_path: Path):
    watched = tmp_path / "watched"
    watched.mkdir()
    original = calculation_validation._run_runtime_probes

    def probe_with_write():
        result = original()
        (watched / "birth-profile-private.json").write_text(
            "private", encoding="utf-8"
        )
        return result

    monkeypatch.setattr(
        calculation_validation,
        "_run_runtime_probes",
        probe_with_write,
    )

    checks = build_calculation_checks(snapshot_roots=(watched,))

    assert checks["no_persistence"] == "failed"


def test_validator_fails_closed_when_runtime_probe_raises(monkeypatch):
    def fail_probe():
        raise RuntimeError("private runtime detail")

    monkeypatch.setattr(calculation_validation, "_run_runtime_probes", fail_probe)

    checks = build_calculation_checks()

    assert checks["stages_present"] == "failed"
    assert checks["placeholder_integrity"] == "failed"
    assert checks["evidence_calculation_separation"] == "failed"
    assert checks["high_risk_guardrails"] == "failed"
    assert set(checks.values()) <= {"passed", "failed"}


def test_runtime_probe_constructs_legacy_and_calculated_reports(monkeypatch):
    original = calculation_validation.build_report
    calculations = []

    def recording_build_report(chart, calculation=None):
        calculations.append(calculation)
        return original(chart, calculation)

    monkeypatch.setattr(
        calculation_validation,
        "build_report",
        recording_build_report,
    )

    calculation_validation._run_runtime_probes()

    assert len(calculations) == 2
    assert all(calculation is not None for calculation in calculations)
    assert calculations[0] != calculations[1]
