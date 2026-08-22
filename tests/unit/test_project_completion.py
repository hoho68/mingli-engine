import json
import shutil
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from mingli_engine import project_completion
from mingli_engine import cli
from mingli_engine.project_completion import build_project_completion_summary
from mingli_engine.report_acceptance import build_report_acceptance_summary
from mingli_engine.report_release import build_report_release_summary


REPO_ROOT = Path(__file__).resolve().parents[2]
LEGACY_FEATURE_IDS = [
    "001-bazi-report-engine",
    "002-bazi-auto-chart",
    "003-bazi-interpretation-rules",
    "004-report-readability",
    "005-plain-language-report",
]
BASELINE_ACCEPTANCE = build_report_acceptance_summary()
BASELINE_RELEASE = build_report_release_summary()
CALCULATION_CHECKS = {
    "stages_present": "passed",
    "placeholder_integrity": "passed",
    "verified_fixture_count": "passed",
    "boundary_fixture_count": "passed",
    "three_school_profiles": "passed",
    "evidence_calculation_separation": "passed",
    "high_risk_guardrails": "passed",
    "no_persistence": "passed",
}
MALFORMED_CHECK_MAPS = [
    {"stages_present": "passed"},
    {"fake": "passed"},
    CALCULATION_CHECKS | {"extra": "passed"},
    {},
    {"stages_present": "invalid"},
]


@pytest.fixture(autouse=True)
def _stable_runtime_gates(monkeypatch):
    monkeypatch.setattr(
        project_completion,
        "build_calculation_checks",
        lambda: CALCULATION_CHECKS.copy(),
    )
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
        lambda **_kwargs: BASELINE_ACCEPTANCE,
    )
    monkeypatch.setattr(
        project_completion,
        "build_report_release_summary",
        lambda **_kwargs: BASELINE_RELEASE,
    )


def _feature(summary, feature_id: str):
    return next(item for item in summary.features if item.feature_id == feature_id)


def _copy_specs(tmp_path: Path) -> Path:
    target = tmp_path / "specs"
    shutil.copytree(REPO_ROOT / "specs", target)
    return target


def _copy_completion_docs(tmp_path: Path) -> Path:
    target = tmp_path / "classical_sources"
    shutil.copytree(REPO_ROOT / "docs" / "classical_sources", target)
    return target


def test_project_completion_summary_certifies_local_delivery():
    summary = build_project_completion_summary()

    assert summary.baseline_id == "project_completion_v1"
    assert summary.completion_status == "complete_with_guardrails"
    assert summary.feature_count == 17
    assert summary.spec_count == 17
    assert summary.plan_count == 17
    assert summary.task_tracked_feature_count == 12
    assert summary.legacy_feature_count == 5
    assert summary.functional_requirement_count == 240
    assert summary.success_criteria_count == 122
    assert summary.checked_task_count == 1081
    assert summary.unchecked_task_count == 0
    assert summary.checklist_file_count == 17
    assert summary.checked_checklist_item_count == 272
    assert summary.unchecked_checklist_item_count == 0
    assert summary.quality_checks == {
        "evidence_curation": "passed",
        "materials_audit": "passed",
        "learning_reference": "passed",
    }
    assert summary.calculation_checks == CALCULATION_CHECKS
    assert summary.completion_checks == {
        "feature_baseline": "passed",
        "specification_artifacts": "passed",
        "requirements_inventory": "passed",
        "task_closure": "passed",
        "checklist_closure": "passed",
        "learning_archive_closure": "passed",
        "documentation_navigation": "passed",
        "quality_gates": "passed",
        "calculation_validation": "passed",
        "report_acceptance": "passed",
        "report_release": "passed",
    }
    assert summary.release_id == "report_release_v1"
    assert summary.release_status == "ready_with_guardrails"
    assert summary.acceptance_baseline_id == "report_acceptance_v1"
    assert summary.acceptance_status == "ready_with_guardrails"
    assert summary.approved_evidence_count == 996
    assert summary.rule_family_count == 10
    assert summary.action_track_count == 4
    assert summary.open_conflicts == ["conflict_high_risk_scope_001"]
    assert summary.legacy_feature_ids == LEGACY_FEATURE_IDS
    assert summary.remaining_local_blockers == []
    assert summary.next_action == (
        "local_delivery_complete_wait_for_new_material_or_explicit_remote_request"
    )


def test_completion_blocks_and_names_failed_calculation_validation(monkeypatch):
    failed_checks = CALCULATION_CHECKS | {"placeholder_integrity": "failed"}
    monkeypatch.setattr(
        project_completion,
        "build_calculation_checks",
        lambda: failed_checks,
    )

    summary = build_project_completion_summary()

    assert summary.completion_status == "blocked"
    assert summary.calculation_checks == failed_checks
    assert summary.completion_checks["calculation_validation"] == "failed"
    assert "calculation_validation" in summary.remaining_local_blockers


def test_completion_computes_one_check_map_and_propagates_it(monkeypatch):
    calls = 0
    acceptance_inputs = []
    release_inputs = []

    def build_checks():
        nonlocal calls
        calls += 1
        return CALCULATION_CHECKS.copy()

    def build_acceptance(*, calculation_checks=None):
        acceptance_inputs.append(calculation_checks)
        return BASELINE_ACCEPTANCE

    def build_release(*, calculation_checks=None, acceptance_summary=None):
        release_inputs.append((calculation_checks, acceptance_summary))
        return BASELINE_RELEASE

    monkeypatch.setattr(project_completion, "build_calculation_checks", build_checks)
    monkeypatch.setattr(
        project_completion,
        "build_report_acceptance_summary",
        build_acceptance,
    )
    monkeypatch.setattr(
        project_completion,
        "build_report_release_summary",
        build_release,
    )

    summary = build_project_completion_summary()

    assert calls == 1
    assert acceptance_inputs == [CALCULATION_CHECKS]
    assert release_inputs == [(CALCULATION_CHECKS, BASELINE_ACCEPTANCE)]
    assert summary.calculation_checks == CALCULATION_CHECKS
    assert summary.calculation_checks is not acceptance_inputs[0]


@pytest.mark.parametrize("checks", MALFORMED_CHECK_MAPS)
def test_completion_rejects_noncanonical_calculation_check_maps(checks):
    summary = build_project_completion_summary(calculation_checks=checks)

    assert summary.completion_status == "blocked"
    assert summary.completion_checks["calculation_validation"] == "failed"
    assert "calculation_validation" in summary.remaining_local_blockers


def test_feature_results_distinguish_legacy_and_task_tracked_features():
    summary = build_project_completion_summary()

    for feature_id in LEGACY_FEATURE_IDS:
        feature = _feature(summary, feature_id)
        assert feature.artifact_status == "complete"
        assert feature.task_tracking_status == "legacy_implemented_baseline"
        assert feature.checked_task_count == 0
        assert feature.unchecked_task_count == 0
        assert feature.checklist_status == "complete"

    tracked = _feature(summary, "017-learning-reference-curation")
    assert tracked.task_tracking_status == "complete"
    assert tracked.checked_task_count == 100
    assert tracked.unchecked_task_count == 0


def test_completion_blocks_missing_plan_without_mutating_specs(tmp_path):
    specs_dir = _copy_specs(tmp_path)
    missing_plan = specs_dir / "010-html-visual-report" / "plan.md"
    missing_plan.unlink()

    summary = build_project_completion_summary(specs_dir=specs_dir)
    feature = _feature(summary, "010-html-visual-report")

    assert summary.completion_status == "blocked"
    assert summary.completion_checks["specification_artifacts"] == "failed"
    assert "specification_artifacts" in summary.remaining_local_blockers
    assert feature.plan_present is False
    assert feature.artifact_status == "incomplete"


def test_completion_blocks_feature_baseline_drift(tmp_path):
    specs_dir = _copy_specs(tmp_path)
    (specs_dir / "017-learning-reference-curation").rename(
        specs_dir / "018-renamed-feature"
    )

    summary = build_project_completion_summary(specs_dir=specs_dir)

    assert summary.completion_status == "blocked"
    assert summary.completion_checks["feature_baseline"] == "failed"
    assert "feature_baseline" in summary.remaining_local_blockers


def test_completion_blocks_unchecked_task(tmp_path):
    specs_dir = _copy_specs(tmp_path)
    tasks_path = specs_dir / "017-learning-reference-curation" / "tasks.md"
    text = tasks_path.read_text(encoding="utf-8")
    tasks_path.write_text(text.replace("- [X] T001", "- [ ] T001", 1), encoding="utf-8")

    summary = build_project_completion_summary(specs_dir=specs_dir)
    feature = _feature(summary, "017-learning-reference-curation")

    assert summary.completion_status == "blocked"
    assert summary.unchecked_task_count == 1
    assert summary.completion_checks["task_closure"] == "failed"
    assert feature.task_tracking_status == "incomplete"


def test_completion_reports_actual_task_tracking_count_when_file_is_missing(
    tmp_path,
):
    specs_dir = _copy_specs(tmp_path)
    tasks_path = specs_dir / "010-html-visual-report" / "tasks.md"
    tasks_path.unlink()

    summary = build_project_completion_summary(specs_dir=specs_dir)
    feature = _feature(summary, "010-html-visual-report")

    assert summary.completion_status == "blocked"
    assert summary.task_tracked_feature_count == 11
    assert summary.completion_checks["task_closure"] == "failed"
    assert feature.task_tracking_status == "missing"


def test_completion_blocks_unchecked_requirements_checklist(tmp_path):
    specs_dir = _copy_specs(tmp_path)
    checklist = (
        specs_dir
        / "017-learning-reference-curation"
        / "checklists"
        / "requirements.md"
    )
    text = checklist.read_text(encoding="utf-8")
    checklist.write_text(text.replace("- [X]", "- [ ]", 1), encoding="utf-8")

    summary = build_project_completion_summary(specs_dir=specs_dir)
    feature = _feature(summary, "017-learning-reference-curation")

    assert summary.completion_status == "blocked"
    assert summary.unchecked_checklist_item_count == 1
    assert summary.completion_checks["checklist_closure"] == "failed"
    assert feature.checklist_status == "incomplete"


def test_completion_blocks_missing_archive_closure_marker(tmp_path):
    docs_dir = _copy_completion_docs(tmp_path)
    handoff = docs_dir / "new_material_learning_handoff.md"
    text = handoff.read_text(encoding="utf-8")
    handoff.write_text(
        text.replace("archive-local-commit-created=1", "archive-marker-removed"),
        encoding="utf-8",
    )

    summary = build_project_completion_summary(docs_dir=docs_dir)

    assert summary.completion_status == "blocked"
    assert summary.completion_checks["learning_archive_closure"] == "failed"
    assert "learning_archive_closure" in summary.remaining_local_blockers


def test_completion_blocks_missing_completion_navigation(tmp_path):
    docs_dir = _copy_completion_docs(tmp_path)
    (docs_dir / "project_completion.md").unlink()

    summary = build_project_completion_summary(docs_dir=docs_dir)

    assert summary.completion_status == "blocked"
    assert summary.completion_checks["documentation_navigation"] == "failed"


def test_completion_propagates_quality_and_release_failures(monkeypatch):
    monkeypatch.setattr(
        project_completion,
        "validate_materials_audit_quality",
        lambda: ["controlled failure"],
    )
    blocked_release = replace(
        build_report_release_summary(),
        release_status="blocked",
        next_action="repair_report_release_matrix",
    )
    monkeypatch.setattr(
        project_completion,
        "build_report_release_summary",
        lambda **_kwargs: blocked_release,
    )

    summary = build_project_completion_summary()

    assert summary.completion_status == "blocked"
    assert summary.quality_checks["materials_audit"] == "failed"
    assert summary.completion_checks["quality_gates"] == "failed"
    assert summary.completion_checks["report_release"] == "failed"
    assert "quality_gates" in summary.remaining_local_blockers
    assert "report_release" in summary.remaining_local_blockers


def test_completion_blocks_release_acceptance_baseline_drift(monkeypatch):
    drifted_release = replace(
        BASELINE_RELEASE,
        acceptance_baseline_id="stale_acceptance_baseline",
    )
    monkeypatch.setattr(
        project_completion,
        "build_report_release_summary",
        lambda **_kwargs: drifted_release,
    )

    summary = build_project_completion_summary()

    assert summary.completion_status == "blocked"
    assert summary.completion_checks["report_acceptance"] == "passed"
    assert summary.completion_checks["report_release"] == "failed"
    assert "report_release" in summary.remaining_local_blockers


def test_completion_summary_serialization_excludes_private_and_raw_content():
    serialized = json.dumps(
        asdict(build_project_completion_summary()),
        ensure_ascii=False,
    )

    for token in (
        "birth_date",
        "birth_time",
        "birthplace",
        "focus_topic",
        "1992-08-18",
        "上海市",
        "资料原文/",
        ".pdf",
        "https://",
        "origin/",
    ):
        assert token not in serialized


def test_completion_cli_handler_returns_nonzero_for_blocked_packet(
    monkeypatch,
    capsys,
):
    blocked = replace(
        build_project_completion_summary(),
        completion_status="blocked",
        remaining_local_blockers=["task_closure"],
        next_action="repair_project_completion_checks",
    )
    monkeypatch.setattr(cli, "build_project_completion_summary", lambda: blocked)

    exit_code = cli._project_completion_summary(None)
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 4
    assert payload["completion_status"] == "blocked"
