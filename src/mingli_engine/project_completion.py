from pathlib import Path
import re
from typing import Callable

from mingli_engine.classical_sources import (
    load_approved_evidence_units,
    load_classical_sources,
    load_source_conflicts,
)
from mingli_engine.evidence_curation import validate_curation_quality
from mingli_engine.learning_reference_curation import (
    validate_learning_reference_quality,
)
from mingli_engine.materials_audit import validate_materials_audit_quality
from mingli_engine.models import (
    ProjectCompletionFeatureResult,
    ProjectCompletionSummary,
)
from mingli_engine.report_acceptance import build_report_acceptance_summary
from mingli_engine.report_release import build_report_release_summary


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPECS_DIR = REPO_ROOT / "specs"
DEFAULT_DOCS_DIR = REPO_ROOT / "docs" / "classical_sources"
BASELINE_ID = "project_completion_v1"
EXPECTED_FEATURE_IDS = (
    "001-bazi-report-engine",
    "002-bazi-auto-chart",
    "003-bazi-interpretation-rules",
    "004-report-readability",
    "005-plain-language-report",
    "006-structure-observation-language",
    "007-report-transition-language",
    "008-report-regression-cases",
    "009-report-evidence-notes",
    "010-html-visual-report",
    "011-classical-evidence-core",
    "012-classical-evidence-curation",
    "013-source-extraction-workflow",
    "014-source-library-expansion",
    "015-existing-materials-audit",
    "016-extraction-queue-intake",
    "017-learning-reference-curation",
)
LEGACY_FEATURE_IDS = EXPECTED_FEATURE_IDS[:5]
EXPECTED_FUNCTIONAL_REQUIREMENT_COUNT = 240
EXPECTED_SUCCESS_CRITERIA_COUNT = 122
EXPECTED_CHECKED_TASK_COUNT = 1081
EXPECTED_CHECKLIST_ITEM_COUNT = 272
PASS = "passed"
FAIL = "failed"

FR_PATTERN = re.compile(r"^\s*[-*]?\s*\*\*FR-\d+", re.MULTILINE)
SC_PATTERN = re.compile(r"^\s*[-*]?\s*\*\*SC-\d+", re.MULTILINE)
CHECKED_TASK_PATTERN = re.compile(r"^- \[[xX]\]\s+T\d+", re.MULTILINE)
UNCHECKED_TASK_PATTERN = re.compile(r"^- \[ \]\s+T\d+", re.MULTILINE)
CHECKED_ITEM_PATTERN = re.compile(r"^- \[[xX]\]", re.MULTILINE)
UNCHECKED_ITEM_PATTERN = re.compile(r"^- \[ \]", re.MULTILINE)


class ProjectCompletionError(ValueError):
    pass


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise ProjectCompletionError("project completion artifact is unreadable") from error


def _count(pattern: re.Pattern[str], text: str) -> int:
    return len(pattern.findall(text))


def _feature_result(
    feature_id: str,
    specs_dir: Path,
) -> tuple[ProjectCompletionFeatureResult, int]:
    feature_dir = specs_dir / feature_id
    spec_path = feature_dir / "spec.md"
    plan_path = feature_dir / "plan.md"
    tasks_path = feature_dir / "tasks.md"
    spec_present = spec_path.is_file()
    plan_present = plan_path.is_file()
    spec_text = _read_text(spec_path) if spec_present else ""
    functional_requirement_count = _count(FR_PATTERN, spec_text)
    success_criteria_count = _count(SC_PATTERN, spec_text)

    checked_task_count = 0
    unchecked_task_count = 0
    if tasks_path.is_file():
        tasks_text = _read_text(tasks_path)
        checked_task_count = _count(CHECKED_TASK_PATTERN, tasks_text)
        unchecked_task_count = _count(UNCHECKED_TASK_PATTERN, tasks_text)

    if feature_id in LEGACY_FEATURE_IDS:
        task_tracking_status = (
            "legacy_implemented_baseline"
            if not tasks_path.exists()
            else "baseline_drift"
        )
    elif not tasks_path.is_file():
        task_tracking_status = "missing"
    elif unchecked_task_count:
        task_tracking_status = "incomplete"
    else:
        task_tracking_status = "complete"

    checklist_files = sorted((feature_dir / "checklists").glob("*.md"))
    checked_checklist_item_count = 0
    unchecked_checklist_item_count = 0
    for checklist_path in checklist_files:
        checklist_text = _read_text(checklist_path)
        checked_checklist_item_count += _count(
            CHECKED_ITEM_PATTERN,
            checklist_text,
        )
        unchecked_checklist_item_count += _count(
            UNCHECKED_ITEM_PATTERN,
            checklist_text,
        )
    checklist_status = (
        "complete"
        if checklist_files
        and checked_checklist_item_count
        and not unchecked_checklist_item_count
        else "incomplete"
    )

    return (
        ProjectCompletionFeatureResult(
            feature_id=feature_id,
            artifact_status=(
                "complete" if spec_present and plan_present else "incomplete"
            ),
            spec_present=spec_present,
            plan_present=plan_present,
            functional_requirement_count=functional_requirement_count,
            success_criteria_count=success_criteria_count,
            task_tracking_status=task_tracking_status,
            checked_task_count=checked_task_count,
            unchecked_task_count=unchecked_task_count,
            checklist_status=checklist_status,
            checked_checklist_item_count=checked_checklist_item_count,
            unchecked_checklist_item_count=unchecked_checklist_item_count,
        ),
        len(checklist_files),
    )


def _quality_status(check: Callable[[], list[str]]) -> str:
    try:
        return PASS if not check() else FAIL
    except Exception:
        return FAIL


def _documentation_checks(docs_dir: Path) -> tuple[bool, bool]:
    required_files = (
        "README.md",
        "coverage.md",
        "new_material_learning_handoff.md",
        "report_acceptance.md",
        "report_release.md",
        "project_completion.md",
    )
    if not all((docs_dir / name).is_file() for name in required_files):
        return False, False

    readme = _read_text(docs_dir / "README.md")
    coverage = _read_text(docs_dir / "coverage.md")
    handoff = _read_text(docs_dir / "new_material_learning_handoff.md")
    navigation_ready = all(
        marker in readme
        for marker in (
            "new_material_learning_handoff.md",
            "report_acceptance.md",
            "report_release.md",
            "project_completion.md",
        )
    ) and all(
        marker in coverage
        for marker in (
            "report_acceptance_v1",
            "report_release_v1",
            "project_completion_v1",
            "enable_report_cli_with_guardrails",
        )
    )
    archive_ready = all(
        marker in handoff
        for marker in (
            "new-material-pending-sources=0",
            "archive-local-commit-created=1",
            "post-archive-resume-status=waiting_for_new_material_or_push_request",
        )
    )
    return navigation_ready, archive_ready


def build_project_completion_summary(
    *,
    specs_dir: Path | None = None,
    docs_dir: Path | None = None,
) -> ProjectCompletionSummary:
    resolved_specs_dir = specs_dir or DEFAULT_SPECS_DIR
    resolved_docs_dir = docs_dir or DEFAULT_DOCS_DIR
    if not resolved_specs_dir.is_dir() or not resolved_docs_dir.is_dir():
        raise ProjectCompletionError("project completion root is unavailable")

    actual_feature_ids = tuple(
        path.name
        for path in sorted(resolved_specs_dir.iterdir())
        if path.is_dir() and re.match(r"^\d{3}-", path.name)
    )
    feature_baseline_ready = actual_feature_ids == EXPECTED_FEATURE_IDS
    feature_pairs = [
        _feature_result(feature_id, resolved_specs_dir)
        for feature_id in EXPECTED_FEATURE_IDS
    ]
    features = [feature for feature, _ in feature_pairs]
    checklist_file_count = sum(count for _, count in feature_pairs)

    spec_count = sum(feature.spec_present for feature in features)
    plan_count = sum(feature.plan_present for feature in features)
    functional_requirement_count = sum(
        feature.functional_requirement_count for feature in features
    )
    success_criteria_count = sum(
        feature.success_criteria_count for feature in features
    )
    checked_task_count = sum(feature.checked_task_count for feature in features)
    unchecked_task_count = sum(
        feature.unchecked_task_count for feature in features
    )
    checked_checklist_item_count = sum(
        feature.checked_checklist_item_count for feature in features
    )
    unchecked_checklist_item_count = sum(
        feature.unchecked_checklist_item_count for feature in features
    )

    artifacts_ready = all(
        feature.artifact_status == "complete" for feature in features
    )
    requirements_ready = (
        functional_requirement_count == EXPECTED_FUNCTIONAL_REQUIREMENT_COUNT
        and success_criteria_count == EXPECTED_SUCCESS_CRITERIA_COUNT
        and all(feature.functional_requirement_count for feature in features)
        and all(feature.success_criteria_count for feature in features)
    )
    tasks_ready = (
        checked_task_count == EXPECTED_CHECKED_TASK_COUNT
        and not unchecked_task_count
        and all(
            feature.task_tracking_status == "legacy_implemented_baseline"
            for feature in features[: len(LEGACY_FEATURE_IDS)]
        )
        and all(
            feature.task_tracking_status == "complete"
            for feature in features[len(LEGACY_FEATURE_IDS) :]
        )
    )
    checklists_ready = (
        checklist_file_count == len(EXPECTED_FEATURE_IDS)
        and checked_checklist_item_count == EXPECTED_CHECKLIST_ITEM_COUNT
        and not unchecked_checklist_item_count
        and all(feature.checklist_status == "complete" for feature in features)
    )
    navigation_ready, archive_ready = _documentation_checks(resolved_docs_dir)

    quality_checks = {
        "evidence_curation": _quality_status(
            lambda: validate_curation_quality(
                load_classical_sources(),
                load_approved_evidence_units(),
                load_source_conflicts(),
            )
        ),
        "materials_audit": _quality_status(validate_materials_audit_quality),
        "learning_reference": _quality_status(
            validate_learning_reference_quality
        ),
    }
    quality_ready = all(status == PASS for status in quality_checks.values())

    try:
        acceptance = build_report_acceptance_summary()
        acceptance_ready = acceptance.acceptance_status in {
            "ready",
            "ready_with_guardrails",
        }
    except Exception:
        acceptance = None
        acceptance_ready = False
    try:
        release = build_report_release_summary()
        release_ready = (
            release.release_status in {"ready", "ready_with_guardrails"}
            and acceptance is not None
            and release.acceptance_baseline_id == acceptance.baseline_id
            and release.acceptance_status == acceptance.acceptance_status
            and release.approved_evidence_count
            == acceptance.approved_evidence_count
            and release.rule_family_count == acceptance.rule_family_count
        )
    except Exception:
        release = None
        release_ready = False

    completion_checks = {
        "feature_baseline": PASS if feature_baseline_ready else FAIL,
        "specification_artifacts": PASS if artifacts_ready else FAIL,
        "requirements_inventory": PASS if requirements_ready else FAIL,
        "task_closure": PASS if tasks_ready else FAIL,
        "checklist_closure": PASS if checklists_ready else FAIL,
        "learning_archive_closure": PASS if archive_ready else FAIL,
        "documentation_navigation": PASS if navigation_ready else FAIL,
        "quality_gates": PASS if quality_ready else FAIL,
        "report_acceptance": PASS if acceptance_ready else FAIL,
        "report_release": PASS if release_ready else FAIL,
    }
    remaining_local_blockers = [
        check for check, status in completion_checks.items() if status == FAIL
    ]
    has_guardrails = (
        acceptance is not None and bool(acceptance.open_conflicts)
    ) or (
        release is not None
        and release.release_status == "ready_with_guardrails"
    )
    if remaining_local_blockers:
        completion_status = "blocked"
        next_action = "repair_project_completion_checks"
    elif has_guardrails:
        completion_status = "complete_with_guardrails"
        next_action = (
            "local_delivery_complete_wait_for_new_material_or_explicit_remote_request"
        )
    else:
        completion_status = "complete"
        next_action = "local_delivery_complete"

    controlled_boundaries = [
        "legacy_001_005_implemented_before_task_artifacts",
        "controlled_material_backlog_not_a_delivery_blocker",
        "raw_materials_outside_runtime",
        "remote_operations_out_of_scope",
        "future_extensions_out_of_scope",
        "waiting_for_new_material_or_explicit_remote_request",
    ]
    if acceptance is not None and acceptance.open_conflicts:
        controlled_boundaries.insert(
            0,
            "known_high_risk_scope_conflict_retained",
        )

    return ProjectCompletionSummary(
        baseline_id=BASELINE_ID,
        completion_status=completion_status,
        feature_count=len(actual_feature_ids),
        spec_count=spec_count,
        plan_count=plan_count,
        task_tracked_feature_count=sum(
            feature.task_tracking_status in {"complete", "incomplete"}
            for feature in features
        ),
        legacy_feature_count=sum(
            feature.task_tracking_status == "legacy_implemented_baseline"
            for feature in features
        ),
        functional_requirement_count=functional_requirement_count,
        success_criteria_count=success_criteria_count,
        checked_task_count=checked_task_count,
        unchecked_task_count=unchecked_task_count,
        checklist_file_count=checklist_file_count,
        checked_checklist_item_count=checked_checklist_item_count,
        unchecked_checklist_item_count=unchecked_checklist_item_count,
        quality_checks=quality_checks,
        completion_checks=completion_checks,
        release_id=release.release_id if release is not None else "unavailable",
        release_status=(
            release.release_status if release is not None else "unavailable"
        ),
        acceptance_baseline_id=(
            acceptance.baseline_id if acceptance is not None else "unavailable"
        ),
        acceptance_status=(
            acceptance.acceptance_status if acceptance is not None else "unavailable"
        ),
        approved_evidence_count=(
            acceptance.approved_evidence_count if acceptance is not None else 0
        ),
        rule_family_count=(
            acceptance.rule_family_count if acceptance is not None else 0
        ),
        action_track_count=(release.action_track_count if release is not None else 0),
        open_conflicts=(acceptance.open_conflicts if acceptance is not None else []),
        legacy_feature_ids=list(LEGACY_FEATURE_IDS),
        features=features,
        controlled_boundaries=controlled_boundaries,
        remaining_local_blockers=remaining_local_blockers,
        next_action=next_action,
    )
