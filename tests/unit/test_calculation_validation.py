import json
import os
import shutil
from pathlib import Path

from mingli_engine import calculation_validation
from mingli_engine import project_completion, report_acceptance, report_release
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


def _copy_fixtures(tmp_path: Path) -> Path:
    fixture_dir = tmp_path / "bazi_calculation"
    shutil.copytree(calculation_validation.DEFAULT_FIXTURE_DIR, fixture_dir)
    return fixture_dir


def _load_fixture(fixture_dir: Path, name: str) -> tuple[Path, dict]:
    path = fixture_dir / name
    return path, json.loads(path.read_text(encoding="utf-8"))


def _write_fixture(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_calculation_checks_pass_the_v1_release_baseline():
    assert build_calculation_checks() == EXPECTED_CHECKS


def test_verified_fixture_gate_rejects_a_forged_pillar_artifact(
    tmp_path: Path,
):
    fixture_dir = _copy_fixtures(tmp_path)
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
    fixture_dir = _copy_fixtures(tmp_path)
    fixture_path = fixture_dir / "luck_cycle_boundary_cases.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    payload["cases"][0]["fixture_metadata"]["demonstrated_behaviors"] = [
        "unbacked_label"
    ]
    fixture_path.write_text(json.dumps(payload), encoding="utf-8")

    checks = build_calculation_checks(fixture_dir=fixture_dir)

    assert checks["boundary_fixture_count"] == "failed"


def test_verified_gate_executes_second_record_input(tmp_path: Path):
    fixture_dir = _copy_fixtures(tmp_path)
    path, payload = _load_fixture(fixture_dir, "verified_charts.json")
    payload["records"][1]["input"]["birth_date"] = "1990-01-01"
    _write_fixture(path, payload)

    checks = build_calculation_checks(fixture_dir=fixture_dir)

    assert checks["verified_fixture_count"] == "failed"


def test_verified_gate_recomputes_downstream_expected_values(tmp_path: Path):
    fixture_dir = _copy_fixtures(tmp_path)
    path, payload = _load_fixture(fixture_dir, "verified_charts.json")
    payload["records"][0]["expected"]["strength"]["score"] += 1
    _write_fixture(path, payload)

    checks = build_calculation_checks(fixture_dir=fixture_dir)

    assert checks["verified_fixture_count"] == "failed"


def test_boundary_gate_executes_luck_direction(tmp_path: Path):
    fixture_dir = _copy_fixtures(tmp_path)
    path, payload = _load_fixture(
        fixture_dir, "luck_cycle_boundary_cases.json"
    )
    payload["cases"][0]["expected"]["forward"] = not payload["cases"][0][
        "expected"
    ]["forward"]
    _write_fixture(path, payload)

    checks = build_calculation_checks(fixture_dir=fixture_dir)

    assert checks["boundary_fixture_count"] == "failed"


def test_boundary_gate_executes_strength_ranges(tmp_path: Path):
    fixture_dir = _copy_fixtures(tmp_path)
    path, payload = _load_fixture(fixture_dir, "strength_boundary_cases.json")
    case = next(
        item
        for item in payload["cases"]
        if item["expected"]["strength"].get("sensitivity_boundary")
    )
    case["expected"]["strength"]["score_range"] = [999.0, 1000.0]
    _write_fixture(path, payload)

    checks = build_calculation_checks(fixture_dir=fixture_dir)

    assert checks["boundary_fixture_count"] == "failed"


def test_boundary_gate_executes_pattern_semantics(tmp_path: Path):
    fixture_dir = _copy_fixtures(tmp_path)
    path, payload = _load_fixture(fixture_dir, "pattern_counterexamples.json")
    case = next(item for item in payload["counterexamples"] if item["expected_damage"])
    case["expected_damage"] = ["not_the_calculated_damage"]
    _write_fixture(path, payload)

    checks = build_calculation_checks(fixture_dir=fixture_dir)

    assert checks["boundary_fixture_count"] == "failed"


def test_boundary_gate_validates_false_count_cases(tmp_path: Path):
    fixture_dir = _copy_fixtures(tmp_path)
    path, payload = _load_fixture(fixture_dir, "pattern_counterexamples.json")
    case = next(item for item in payload["counterexamples"] if item["expected_damage"])
    case["fixture_metadata"]["counts_toward_boundary_gate"] = False
    case["expected_damage"] = ["not_the_calculated_damage"]
    _write_fixture(path, payload)

    checks = build_calculation_checks(fixture_dir=fixture_dir)

    assert checks["boundary_fixture_count"] == "failed"


def test_corrupted_fixture_blocks_all_completion_gates(monkeypatch, tmp_path: Path):
    fixture_dir = _copy_fixtures(tmp_path)
    path, payload = _load_fixture(fixture_dir, "verified_charts.json")
    payload["records"][1]["input"]["birth_date"] = "1990-01-01"
    _write_fixture(path, payload)
    checks = build_calculation_checks(fixture_dir=fixture_dir)
    assert checks["verified_fixture_count"] == "failed"

    monkeypatch.setattr(
        report_acceptance,
        "build_calculation_checks",
        lambda: checks,
    )
    acceptance = report_acceptance.build_report_acceptance_summary()
    assert acceptance.acceptance_status == "blocked"

    monkeypatch.setattr(
        report_release,
        "build_calculation_checks",
        lambda: checks,
    )
    monkeypatch.setattr(
        report_release,
        "build_report_acceptance_summary",
        lambda **_kwargs: acceptance,
    )
    release = report_release.build_report_release_summary()
    assert release.release_status == "blocked"

    monkeypatch.setattr(project_completion, "build_calculation_checks", lambda: checks)
    monkeypatch.setattr(
        project_completion,
        "validate_curation_quality",
        lambda sources, evidence, conflicts: [],
    )
    monkeypatch.setattr(
        project_completion,
        "validate_materials_audit_quality",
        lambda: [],
    )
    monkeypatch.setattr(
        project_completion,
        "validate_learning_reference_quality",
        lambda: [],
    )
    monkeypatch.setattr(
        project_completion,
        "build_report_acceptance_summary",
        lambda **_kwargs: acceptance,
    )
    monkeypatch.setattr(
        project_completion,
        "build_report_release_summary",
        lambda **_kwargs: release,
    )
    completion = project_completion.build_project_completion_summary()
    assert completion.completion_status == "blocked"
    assert completion.completion_checks["calculation_validation"] == "failed"
    assert "calculation_validation" in completion.remaining_local_blockers


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


def test_validator_snapshots_custom_fixture_root(monkeypatch, tmp_path: Path):
    fixture_dir = _copy_fixtures(tmp_path)
    original = calculation_validation._verified_fixture_ready

    def verify_with_write(path: Path):
        result = original(path)
        (path / "birth-profile-private.json").write_text(
            "private", encoding="utf-8"
        )
        return result

    monkeypatch.setattr(
        calculation_validation,
        "_verified_fixture_ready",
        verify_with_write,
    )

    checks = build_calculation_checks(fixture_dir=fixture_dir)

    assert checks["no_persistence"] == "failed"


def _checks_with_workspace_mutation(
    monkeypatch,
    workspace: Path,
    mutate,
):
    original = calculation_validation._run_runtime_probes

    def probe_with_mutation():
        result = original()
        mutate()
        return result

    monkeypatch.setattr(
        calculation_validation,
        "_run_runtime_probes",
        probe_with_mutation,
    )
    monkeypatch.setattr(
        calculation_validation,
        "_verified_fixture_ready",
        lambda fixture_dir: True,
    )
    monkeypatch.setattr(
        calculation_validation,
        "_boundary_fixture_ready",
        lambda fixture_dir: True,
    )
    return build_calculation_checks(
        workspace_root=workspace,
        snapshot_roots=(),
    )


def test_validator_detects_same_byte_overwrite(monkeypatch, tmp_path: Path):
    watched = tmp_path / "notes.txt"
    watched.write_bytes(b"unchanged bytes")
    original = watched.stat()

    def overwrite():
        watched.write_bytes(b"unchanged bytes")
        os.utime(
            watched,
            ns=(original.st_atime_ns, original.st_mtime_ns + 1_000_000),
        )

    checks = _checks_with_workspace_mutation(monkeypatch, tmp_path, overwrite)

    assert checks["no_persistence"] == "failed"


def test_validator_detects_new_file_outside_critical_roots(
    monkeypatch,
    tmp_path: Path,
):
    def create_unscoped_file():
        target = tmp_path / "formerly-unscoped"
        target.mkdir()
        (target / "runtime-created.txt").write_text("created", encoding="utf-8")

    checks = _checks_with_workspace_mutation(
        monkeypatch,
        tmp_path,
        create_unscoped_file,
    )

    assert checks["no_persistence"] == "failed"


def test_validator_detects_cache_creation(monkeypatch, tmp_path: Path):
    def create_cache():
        cache = tmp_path / "nested" / "__pycache__"
        cache.mkdir(parents=True)
        (cache / "runtime.pyc").write_bytes(b"cache")

    checks = _checks_with_workspace_mutation(monkeypatch, tmp_path, create_cache)

    assert checks["no_persistence"] == "failed"


def test_validator_detects_personal_report_artifact(monkeypatch, tmp_path: Path):
    def create_report():
        output = tmp_path / "outputs"
        output.mkdir()
        (output / "personal-report.json").write_text("{}", encoding="utf-8")

    checks = _checks_with_workspace_mutation(monkeypatch, tmp_path, create_report)

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
