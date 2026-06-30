"""Deterministic learning reference curation loading and validation."""

from collections import Counter
import json
from pathlib import Path
import re
from typing import Any

from mingli_engine import (
    classical_sources,
    extraction_queue_intake,
    materials_audit,
    source_intake,
    source_library,
)
from mingli_engine.models import (
    CANDIDATE_INTAKE_DECISION_STATUSES,
    CANDIDATE_INTAKE_DECISIONS,
    EXTRACTION_PACKAGE_LOCATOR_REQUIREMENTS,
    EXTRACTION_PACKAGE_RISK_BOUNDARIES,
    LEARNING_POINT_READINESSES,
    LEARNING_REFERENCE_MANUAL_ACTIONS,
    LEARNING_REFERENCE_NOTE_STATUSES,
    PREREQUISITE_ACTION_STATUSES,
    PREREQUISITE_ACTION_TYPES,
    RULE_FAMILIES,
    CandidateIntakeDecision,
    DownstreamAuthorizationReceipt,
    DownstreamAuthorizationSummary,
    LearningReferenceAuthorizationAudit,
    LearningPoint,
    LearningReferenceNote,
    LearningReferenceProgressSummary,
    NewMaterialCorrectedPilotLearningEntryEvaluationItem,
    NewMaterialCorrectedPilotLearningEntryEvaluationSummary,
    NewMaterialCorrectedPilotLearningCompletionReviewItem,
    NewMaterialCorrectedPilotLearningCompletionReviewSummary,
    NewMaterialCorrectedPilotLearningNoteDraftItem,
    NewMaterialCorrectedPilotLearningNoteDraftSummary,
    NewMaterialCorrectedPilotLearningNotePrepItem,
    NewMaterialCorrectedPilotLearningNotePrepSummary,
    PrerequisiteActionNote,
)


class LearningReferenceCurationError(ValueError):
    pass


_DATA_DIR = Path(__file__).resolve().parent / "data" / "learning_reference_curation"
DURABLE_REASON_MIN_LENGTH = 20
NON_DURABLE_REASON_MARKERS = frozenset({"n/a", "na", "none", "todo", "tbd"})
LEARNING_REFERENCE_TEXT_LIMIT = 360
COPIED_PASSAGE_MARKERS = (
    "copied source passage",
    "source passage",
    "copied passage",
    "raw source text",
)
EXTRACTED_MEANING_MARKERS = (
    "extracted meaning",
    "extracted_meaning",
)
REVIEW_STATE_MARKERS = (
    "review decision",
    "review status",
    "approval status",
    "approved meaning",
)
PROMOTION_STATE_MARKERS = (
    "promotion status",
    "promotion batch",
    "promoted evidence",
)
REPORT_EVIDENCE_MARKERS = (
    "formal report evidence",
    "formal evidence",
    "report evidence",
    "report-usable evidence",
    "approved evidence unit",
)
ABSOLUTE_OUTCOME_PHRASES = (
    "\u5fc5\u5b9a",
    "\u6ce8\u5b9a",
    "\u4e00\u5b9a\u4f1a",
    "\u6b7b\u5b9a",
    "will definitely",
    "guaranteed outcome",
)
EXACT_DEATH_PHRASES = (
    "exact death",
    "death timing",
    "exact lifespan",
    "lifespan",
)
PROHIBITED_HIGH_RISK_PHRASES = (
    "diagnose illness",
    "prescribe treatment",
    "medical treatment",
    "legal instruction",
    "psychological treatment",
    "investment instruction",
    "coercive matching",
    "create anxiety",
    "paid remedy upsell",
)
ACTION_TYPES_REQUIRING_MISSING_PREREQUISITES = frozenset(
    {"registration", "preparation", "locator_review", "risk_review"}
)
ACTION_TYPES_REQUIRING_DURABLE_REASON = frozenset({"deferred", "blocked"})
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_ENTRY_EVALUATION_ID = (
    "017-new-material-corrected-pilot-learning-entry-evaluation"
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_ENTRY_EVALUATION_NEXT_ENTRY = (
    "017-new-material-corrected-pilot-learning-note-prep"
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_ENTRY_EVALUATION_STATUSES = frozenset(
    {"ready_for_learning_note_prep"}
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_PREP_ID = (
    "017-new-material-corrected-pilot-learning-note-prep"
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_PREP_NEXT_ENTRY = (
    "017-new-material-corrected-pilot-learning-note-draft"
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_PREP_STATUSES = frozenset(
    {"ready_for_learning_note_draft"}
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_DRAFT_ID = (
    "017-new-material-corrected-pilot-learning-note-draft"
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_DRAFT_NEXT_ENTRY = (
    "017-new-material-corrected-pilot-learning-completion-review"
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_DRAFT_STATUSES = frozenset(
    {"ready_for_learning_completion_review"}
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_COMPLETION_REVIEW_ID = (
    "017-new-material-corrected-pilot-learning-completion-review"
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_COMPLETION_REVIEW_NEXT_ENTRY = (
    "015-new-material-expanded-corrected-transcription-selection"
)
NEW_MATERIAL_CORRECTED_PILOT_LEARNING_COMPLETION_REVIEW_STATUSES = frozenset(
    {"current_pilot_learning_completed_candidate_intake_blocked"}
)


def _data_dir(data_dir: Path | str | None) -> Path:
    return Path(data_dir) if data_dir is not None else _DATA_DIR


def _sibling_data_dir(source_dir: Path, sibling_name: str) -> Path | None:
    sibling = source_dir.parent / sibling_name
    return sibling if sibling.exists() else None


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    try:
        raw_payload = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise LearningReferenceCurationError(
            f"missing data file: {path.name}"
        ) from error

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as error:
        raise LearningReferenceCurationError(
            f"invalid JSON in {path.name}: {error}"
        ) from error

    if not isinstance(payload, list):
        raise LearningReferenceCurationError(
            f"{path.name} must contain a JSON array"
        )
    if not all(isinstance(item, dict) for item in payload):
        raise LearningReferenceCurationError(
            f"{path.name} entries must be JSON objects"
        )
    return payload


def _ensure_unique(ids: list[str], id_name: str) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise LearningReferenceCurationError(f"duplicate {id_name}: {item_id}")
        seen.add(item_id)


def _require_text(value: str, field_name: str, owner_id: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise LearningReferenceCurationError(f"{owner_id} has empty {field_name}")


def _require_string_list(value: Any, field_name: str, owner_id: str) -> None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise LearningReferenceCurationError(f"{owner_id} has invalid {field_name}")


def _require_nonempty_string_list(value: Any, field_name: str, owner_id: str) -> None:
    _require_string_list(value, field_name, owner_id)
    if not value:
        raise LearningReferenceCurationError(f"{owner_id} requires {field_name}")


def _validate_enum(
    value: str,
    allowed_values: frozenset[str],
    field_name: str,
    owner_id: str,
) -> None:
    if value not in allowed_values:
        raise LearningReferenceCurationError(
            f"{owner_id} has invalid {field_name}: {value}"
        )


def _require_non_negative_int(value: Any, field_name: str, owner_id: str) -> None:
    if not isinstance(value, int) or value < 0:
        raise LearningReferenceCurationError(f"{owner_id} has invalid {field_name}")


def _require_bool(value: Any, field_name: str, owner_id: str) -> None:
    if not isinstance(value, bool):
        raise LearningReferenceCurationError(f"{owner_id} has invalid {field_name}")


def _is_durable_reason(value: str) -> bool:
    reason = value.strip()
    if len(reason) < DURABLE_REASON_MIN_LENGTH:
        return False
    return reason.lower() not in NON_DURABLE_REASON_MARKERS


def _learning_reference_note_from_dict(
    data: dict[str, Any],
) -> LearningReferenceNote:
    try:
        note = LearningReferenceNote(**data)
    except TypeError as error:
        raise LearningReferenceCurationError(
            f"invalid learning reference note: {error}"
        ) from error

    owner_id = note.note_id or "?"
    for field_name in (
        "note_id",
        "task_id",
        "package_id",
        "queue_item_id",
        "audit_id",
        "source_library_entry_id",
        "source_material_id",
        "source_title",
        "locator_requirement",
        "risk_boundary",
        "rights_note",
        "source_quality_note",
        "status",
    ):
        _require_text(getattr(note, field_name), field_name, owner_id)
    for field_name in (
        "target_rule_families",
        "overlap_candidate_ids",
    ):
        _require_string_list(getattr(note, field_name), field_name, owner_id)
    _require_nonempty_string_list(note.learning_points, "learning_points", owner_id)
    _validate_enum(
        note.locator_requirement,
        EXTRACTION_PACKAGE_LOCATOR_REQUIREMENTS,
        "locator_requirement",
        owner_id,
    )
    _validate_enum(
        note.risk_boundary,
        EXTRACTION_PACKAGE_RISK_BOUNDARIES,
        "risk_boundary",
        owner_id,
    )
    _validate_enum(
        note.status,
        LEARNING_REFERENCE_NOTE_STATUSES,
        "status",
        owner_id,
    )
    for rule_family in note.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise LearningReferenceCurationError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    return note


def _load_extraction_context(source_dir: Path) -> dict[str, dict[str, Any]]:
    extraction_dir = _sibling_data_dir(source_dir, "extraction_queue_intake")
    if extraction_dir is None:
        return {"packages": {}, "tasks": {}, "backlog_records": {}}

    try:
        packages = extraction_queue_intake.load_extraction_work_packages(extraction_dir)
        tasks = extraction_queue_intake.load_extraction_tasks(extraction_dir)
        backlog_records = extraction_queue_intake.load_prerequisite_backlog_records(
            extraction_dir
        )
    except extraction_queue_intake.ExtractionQueueIntakeError as error:
        raise LearningReferenceCurationError(
            f"016 extraction queue data invalid: {error}"
        ) from error

    return {
        "packages": {package.package_id: package for package in packages},
        "tasks": {task.task_id: task for task in tasks},
        "backlog_records": {
            record.backlog_id: record for record in backlog_records
        },
    }


def _load_materials_audit_context(source_dir: Path) -> dict[str, dict[str, Any]]:
    materials_dir = _sibling_data_dir(source_dir, "materials_audit")
    if materials_dir is None:
        return {"queue_items": {}, "audit_records": {}}

    try:
        queue_items = materials_audit.load_extraction_queue_items(materials_dir)
        audit_records = materials_audit.load_material_audit_records(materials_dir)
    except materials_audit.MaterialsAuditError as error:
        raise LearningReferenceCurationError(
            f"015 materials-audit data invalid: {error}"
        ) from error

    return {
        "queue_items": {item.queue_item_id: item for item in queue_items},
        "audit_records": {record.audit_id: record for record in audit_records},
    }


def _load_source_library_entries(source_dir: Path) -> dict[str, Any]:
    library_dir = _sibling_data_dir(source_dir, "source_library")
    if library_dir is None:
        return {}
    try:
        entries = source_library.load_source_library_entries(library_dir)
    except source_library.SourceLibraryError as error:
        raise LearningReferenceCurationError(
            f"014 source-library data invalid: {error}"
        ) from error
    return {entry.entry_id: entry for entry in entries}


def _load_source_materials(source_dir: Path) -> dict[str, Any]:
    intake_dir = _sibling_data_dir(source_dir, "source_intake")
    if intake_dir is None:
        return {}
    try:
        materials = source_intake.load_source_materials(intake_dir)
    except source_intake.SourceIntakeError as error:
        raise LearningReferenceCurationError(
            f"013 source material data invalid: {error}"
        ) from error
    return {material.material_id: material for material in materials}


def _load_candidate_extracts(source_dir: Path) -> dict[str, Any]:
    intake_dir = _sibling_data_dir(source_dir, "source_intake")
    if intake_dir is None:
        return {}
    try:
        candidates = source_intake.load_candidate_extracts(intake_dir)
    except source_intake.SourceIntakeError as error:
        raise LearningReferenceCurationError(
            f"013 candidate data invalid: {error}"
        ) from error
    return {candidate.candidate_id: candidate for candidate in candidates}


def _resolve_source_intake_dir(
    source_dir: Path,
    source_intake_data_dir: Path | str | None = None,
) -> Path:
    if source_intake_data_dir is not None:
        return Path(source_intake_data_dir)
    sibling = _sibling_data_dir(source_dir, "source_intake")
    if sibling is not None:
        return sibling
    return source_intake._DATA_DIR


def _resolve_classical_sources_dir(
    source_dir: Path,
    classical_sources_data_dir: Path | str | None = None,
) -> Path:
    if classical_sources_data_dir is not None:
        return Path(classical_sources_data_dir)
    sibling = _sibling_data_dir(source_dir, "classical_sources")
    if sibling is not None:
        return sibling
    return classical_sources._DATA_DIR


def _task_overlap_candidate_ids(task: Any) -> set[str]:
    candidate_ids: set[str] = set()
    for warning in task.overlap_warnings:
        candidate_ids.update(re.findall(r"candidate_[A-Za-z0-9_]+", warning))
    return candidate_ids


def _validate_note_trace_links(
    notes: list[LearningReferenceNote],
    source_dir: Path,
) -> None:
    extraction_context = _load_extraction_context(source_dir)
    packages_by_id = extraction_context["packages"]
    tasks_by_id = extraction_context["tasks"]
    backlog_records_by_id = extraction_context["backlog_records"]
    if not tasks_by_id and not packages_by_id and not backlog_records_by_id:
        return

    materials_context = _load_materials_audit_context(source_dir)
    queue_items_by_id = materials_context["queue_items"]
    audit_records_by_id = materials_context["audit_records"]
    source_entries_by_id = _load_source_library_entries(source_dir)
    source_materials_by_id = _load_source_materials(source_dir)
    candidates_by_id = _load_candidate_extracts(source_dir)

    backlog_queue_item_ids = {
        record.queue_item_id for record in backlog_records_by_id.values()
    }

    for note in notes:
        if note.task_id in backlog_records_by_id or note.queue_item_id in backlog_queue_item_ids:
            raise LearningReferenceCurationError(
                f"{note.note_id} references prerequisite backlog, not a 016 extraction task"
            )

        task = tasks_by_id.get(note.task_id)
        if task is None:
            raise LearningReferenceCurationError(
                f"{note.note_id} references unknown 016 extraction task: {note.task_id}"
            )
        package = packages_by_id.get(note.package_id)
        if package is None:
            raise LearningReferenceCurationError(
                f"{note.note_id} references unknown 016 package: {note.package_id}"
            )
        queue_item = queue_items_by_id.get(note.queue_item_id)
        if queue_item is None:
            raise LearningReferenceCurationError(
                f"{note.note_id} references unknown 015 queue item: {note.queue_item_id}"
            )
        audit_record = audit_records_by_id.get(note.audit_id)
        if audit_record is None:
            raise LearningReferenceCurationError(
                f"{note.note_id} references unknown 015 audit: {note.audit_id}"
            )
        source_entry = source_entries_by_id.get(note.source_library_entry_id)
        if source_entry is None:
            raise LearningReferenceCurationError(
                f"{note.note_id} references unknown 014 source-library entry: "
                f"{note.source_library_entry_id}"
            )
        source_material = source_materials_by_id.get(note.source_material_id)
        if source_material is None:
            raise LearningReferenceCurationError(
                f"{note.note_id} references unknown 013 source material: "
                f"{note.source_material_id}"
            )

        if note.task_id not in package.selected_task_ids:
            raise LearningReferenceCurationError(
                f"{note.note_id} task is not selected by package {note.package_id}"
            )
        if note.package_id != task.package_id:
            raise LearningReferenceCurationError(
                f"{note.note_id} package_id does not match 016 task"
            )
        if note.queue_item_id != task.queue_item_id:
            raise LearningReferenceCurationError(
                f"{note.note_id} queue_item_id does not match 016 task"
            )
        if note.audit_id != task.audit_id:
            raise LearningReferenceCurationError(
                f"{note.note_id} audit_id does not match 016 task"
            )
        if note.source_library_entry_id != task.source_library_entry_id:
            raise LearningReferenceCurationError(
                f"{note.note_id} source_library_entry_id does not match 016 task"
            )
        if note.source_material_id != task.intended_source_material_id:
            raise LearningReferenceCurationError(
                f"{note.note_id} source_material_id does not match 016 task"
            )
        if note.source_material_id != source_entry.material_id:
            raise LearningReferenceCurationError(
                f"{note.note_id} source material does not match 014 source-library entry"
            )
        if queue_item.queue_type != "extraction_ready":
            raise LearningReferenceCurationError(
                f"{note.note_id} queue item is not a 016 extraction task"
            )
        if queue_item.audit_id != note.audit_id:
            raise LearningReferenceCurationError(
                f"{note.note_id} queue item audit does not match note audit_id"
            )
        if audit_record.source_library_entry_id != note.source_library_entry_id:
            raise LearningReferenceCurationError(
                f"{note.note_id} audit source-library entry does not match note"
            )
        if set(note.target_rule_families) - set(task.target_rule_families):
            raise LearningReferenceCurationError(
                f"{note.note_id} target_rule_families exceed 016 task targets"
            )
        if note.risk_boundary != task.risk_boundary:
            raise LearningReferenceCurationError(
                f"{note.note_id} risk_boundary does not match 016 task"
            )
        if note.locator_requirement != task.locator_requirement:
            raise LearningReferenceCurationError(
                f"{note.note_id} locator_requirement does not match 016 task"
            )

        expected_overlap_ids = _task_overlap_candidate_ids(task)
        note_overlap_ids = set(note.overlap_candidate_ids)
        for candidate_id in note.overlap_candidate_ids:
            candidate = candidates_by_id.get(candidate_id)
            if candidate is None:
                raise LearningReferenceCurationError(
                    f"{note.note_id} references unknown overlap candidate: {candidate_id}"
                )
            if candidate.material_id != note.source_material_id:
                raise LearningReferenceCurationError(
                    f"{note.note_id} overlap candidate {candidate_id} uses a different material"
                )
        missing_overlap_ids = expected_overlap_ids - note_overlap_ids
        if missing_overlap_ids:
            missing = sorted(missing_overlap_ids)[0]
            raise LearningReferenceCurationError(
                f"{note.note_id} missing overlap candidate: {missing}"
            )


def _learning_point_from_dict(data: dict[str, Any]) -> LearningPoint:
    try:
        point = LearningPoint(**data)
    except TypeError as error:
        raise LearningReferenceCurationError(
            f"invalid learning point: {error}"
        ) from error

    owner_id = point.learning_point_id or "?"
    for field_name in (
        "learning_point_id",
        "note_id",
        "point_label",
        "source_locator",
        "summary",
        "proposed_rule_family",
        "risk_tier",
        "candidate_readiness",
    ):
        _require_text(getattr(point, field_name), field_name, owner_id)
    _require_string_list(point.limitations, "limitations", owner_id)
    if point.proposed_rule_family not in RULE_FAMILIES:
        raise LearningReferenceCurationError(
            f"{owner_id} has unsupported proposed_rule_family: "
            f"{point.proposed_rule_family}"
        )
    _validate_enum(
        point.risk_tier,
        EXTRACTION_PACKAGE_RISK_BOUNDARIES,
        "risk_tier",
        owner_id,
    )
    _validate_enum(
        point.candidate_readiness,
        LEARNING_POINT_READINESSES,
        "candidate_readiness",
        owner_id,
    )
    _require_nonempty_string_list(point.limitations, "limitations", owner_id)
    limitation_text = " ".join(point.limitations).lower()
    if point.risk_tier in {"sensitive", "high_risk"}:
        if "uncertainty" not in limitation_text:
            raise LearningReferenceCurationError(
                f"{owner_id} requires uncertainty limitation"
            )
        if "limitation" not in limitation_text:
            raise LearningReferenceCurationError(
                f"{owner_id} requires limitation language"
            )
    return point


def _candidate_intake_decision_from_dict(
    data: dict[str, Any],
) -> CandidateIntakeDecision:
    try:
        decision = CandidateIntakeDecision(**data)
    except TypeError as error:
        raise LearningReferenceCurationError(
            f"invalid candidate intake decision: {error}"
        ) from error

    owner_id = decision.decision_id or "?"
    for field_name in (
        "decision_id",
        "learning_point_id",
        "decision",
        "source_material_id",
        "rationale",
        "status",
    ):
        _require_text(getattr(decision, field_name), field_name, owner_id)
    _require_string_list(
        decision.overlap_candidate_ids,
        "overlap_candidate_ids",
        owner_id,
    )
    _validate_enum(decision.decision, CANDIDATE_INTAKE_DECISIONS, "decision", owner_id)
    _validate_enum(
        decision.status,
        CANDIDATE_INTAKE_DECISION_STATUSES,
        "status",
        owner_id,
    )
    return decision


def _validate_learning_point_links(
    points: list[LearningPoint],
    source_dir: Path,
) -> None:
    notes = load_learning_reference_notes(source_dir)
    action_notes = load_prerequisite_action_notes(source_dir)
    notes_by_id = {note.note_id: note for note in notes}
    points_by_id = {point.learning_point_id: point for point in points}
    prerequisite_action_ids = {action.action_note_id for action in action_notes}
    prerequisite_backlog_ids = {action.backlog_id for action in action_notes}
    prerequisite_backlog_ids.update(
        _load_extraction_context(source_dir)["backlog_records"].keys()
    )

    for point in points:
        if (
            point.note_id in prerequisite_action_ids
            or point.note_id in prerequisite_backlog_ids
        ):
            raise LearningReferenceCurationError(
                f"{point.learning_point_id} prerequisite action cannot become "
                "learning point"
            )
        note = notes_by_id.get(point.note_id)
        if note is None:
            raise LearningReferenceCurationError(
                f"{point.learning_point_id} references unknown learning reference note: "
                f"{point.note_id}"
            )
        if point.learning_point_id not in note.learning_points:
            raise LearningReferenceCurationError(
                f"{point.learning_point_id} is not listed by note {note.note_id}"
            )
        if point.proposed_rule_family not in note.target_rule_families:
            raise LearningReferenceCurationError(
                f"{point.learning_point_id} proposed_rule_family is not in "
                f"note {note.note_id}"
            )
        if point.risk_tier != note.risk_boundary:
            raise LearningReferenceCurationError(
                f"{point.learning_point_id} risk_tier does not match note {note.note_id}"
            )

    for note in notes:
        for learning_point_id in note.learning_points:
            if learning_point_id not in points_by_id:
                raise LearningReferenceCurationError(
                    f"{note.note_id} references unknown learning point: "
                    f"{learning_point_id}"
                )


def _validate_candidate_intake_decision_links(
    decisions: list[CandidateIntakeDecision],
    source_dir: Path,
) -> None:
    action_notes = load_prerequisite_action_notes(source_dir)
    prerequisite_action_ids = {action.action_note_id for action in action_notes}
    prerequisite_backlog_ids = {action.backlog_id for action in action_notes}
    prerequisite_backlog_ids.update(
        _load_extraction_context(source_dir)["backlog_records"].keys()
    )
    for decision in decisions:
        if (
            decision.learning_point_id in prerequisite_action_ids
            or decision.learning_point_id in prerequisite_backlog_ids
        ):
            raise LearningReferenceCurationError(
                f"{decision.decision_id} prerequisite action cannot create "
                "candidate decision"
            )

    points = load_learning_points(source_dir)
    notes_by_id = {note.note_id: note for note in load_learning_reference_notes(source_dir)}
    points_by_id = {point.learning_point_id: point for point in points}
    decisions_by_id = {decision.decision_id: decision for decision in decisions}
    source_materials_by_id = _load_source_materials(source_dir)
    candidates_by_id = _load_candidate_extracts(source_dir)

    for point in points:
        if point.candidate_decision_id and point.candidate_decision_id not in decisions_by_id:
            raise LearningReferenceCurationError(
                f"{point.learning_point_id} references unknown candidate decision: "
                f"{point.candidate_decision_id}"
            )

    for decision in decisions:
        point = points_by_id.get(decision.learning_point_id)
        if point is None:
            raise LearningReferenceCurationError(
                f"{decision.decision_id} references unknown learning point: "
                f"{decision.learning_point_id}"
            )
        if point.candidate_decision_id and point.candidate_decision_id != decision.decision_id:
            raise LearningReferenceCurationError(
                f"{decision.decision_id} is not linked from learning point "
                f"{point.learning_point_id}"
            )
        note = notes_by_id[point.note_id]
        if decision.source_material_id not in source_materials_by_id:
            raise LearningReferenceCurationError(
                f"{decision.decision_id} references unknown 013 source material: "
                f"{decision.source_material_id}"
            )
        if decision.source_material_id != note.source_material_id:
            raise LearningReferenceCurationError(
                f"{decision.decision_id} source_material_id does not match "
                f"learning note {note.note_id}"
            )

        for candidate_id in decision.overlap_candidate_ids:
            candidate = candidates_by_id.get(candidate_id)
            if candidate is None:
                raise LearningReferenceCurationError(
                    f"{decision.decision_id} references unknown overlap candidate: "
                    f"{candidate_id}"
                )
            if candidate.material_id != decision.source_material_id:
                raise LearningReferenceCurationError(
                    f"{decision.decision_id} overlap candidate {candidate_id} "
                    "uses a different material"
                )

        if decision.decision == "create_candidate":
            if point.candidate_readiness != "ready":
                raise LearningReferenceCurationError(
                    f"{decision.decision_id} create_candidate requires ready "
                    "learning point"
                )
            _require_text(decision.candidate_id, "candidate_id", decision.decision_id)
            existing_candidate = candidates_by_id.get(decision.candidate_id)
            if decision.status == "applied":
                if existing_candidate is None:
                    raise LearningReferenceCurationError(
                        f"{decision.decision_id} applied create_candidate "
                        "requires existing candidate_id"
                    )
                if existing_candidate.material_id != decision.source_material_id:
                    raise LearningReferenceCurationError(
                        f"{decision.decision_id} applied candidate material "
                        "does not match decision"
                    )
                if existing_candidate.proposed_rule_family != point.proposed_rule_family:
                    raise LearningReferenceCurationError(
                        f"{decision.decision_id} applied candidate rule family "
                        "does not match learning point"
                    )
                if existing_candidate.risk_tier != point.risk_tier:
                    raise LearningReferenceCurationError(
                        f"{decision.decision_id} applied candidate risk tier "
                        "does not match learning point"
                    )
            elif existing_candidate is not None:
                raise LearningReferenceCurationError(
                    f"{decision.decision_id} create_candidate candidate_id "
                    "already exists"
                )
        elif decision.decision in {"reuse_existing", "avoid_duplicate"}:
            _require_nonempty_string_list(
                decision.overlap_candidate_ids,
                "overlap_candidate_ids",
                decision.decision_id,
            )
            _require_text(decision.candidate_id, "candidate_id", decision.decision_id)
            if decision.candidate_id not in decision.overlap_candidate_ids:
                raise LearningReferenceCurationError(
                    f"{decision.decision_id} candidate_id must be one of "
                    "overlap_candidate_ids"
                )
            if decision.candidate_id not in candidates_by_id:
                raise LearningReferenceCurationError(
                    f"{decision.decision_id} references unknown overlap candidate: "
                    f"{decision.candidate_id}"
                )


def _prerequisite_action_note_from_dict(
    data: dict[str, Any],
) -> PrerequisiteActionNote:
    try:
        action_note = PrerequisiteActionNote(**data)
    except TypeError as error:
        raise LearningReferenceCurationError(
            f"invalid prerequisite action note: {error}"
        ) from error

    owner_id = action_note.action_note_id or "?"
    for field_name in (
        "action_note_id",
        "backlog_id",
        "package_id",
        "queue_item_id",
        "audit_id",
        "action_type",
        "durable_reason",
        "recommended_action",
        "risk_boundary",
        "status",
    ):
        _require_text(getattr(action_note, field_name), field_name, owner_id)
    _require_string_list(
        action_note.missing_prerequisites,
        "missing_prerequisites",
        owner_id,
    )
    _validate_enum(
        action_note.action_type,
        PREREQUISITE_ACTION_TYPES,
        "action_type",
        owner_id,
    )
    _validate_enum(
        action_note.recommended_action,
        LEARNING_REFERENCE_MANUAL_ACTIONS,
        "recommended_action",
        owner_id,
    )
    _validate_enum(
        action_note.risk_boundary,
        EXTRACTION_PACKAGE_RISK_BOUNDARIES,
        "risk_boundary",
        owner_id,
    )
    _validate_enum(
        action_note.status,
        PREREQUISITE_ACTION_STATUSES,
        "status",
        owner_id,
    )
    if not action_note.missing_prerequisites and not _is_durable_reason(
        action_note.durable_reason
    ):
        raise LearningReferenceCurationError(
            f"{owner_id} requires missing_prerequisites or durable_reason"
        )
    if (
        action_note.action_type in ACTION_TYPES_REQUIRING_MISSING_PREREQUISITES
        and not action_note.missing_prerequisites
    ):
        raise LearningReferenceCurationError(
            f"{owner_id} requires missing_prerequisites for "
            f"{action_note.action_type} action"
        )
    if (
        action_note.action_type in ACTION_TYPES_REQUIRING_DURABLE_REASON
        and not _is_durable_reason(action_note.durable_reason)
    ):
        raise LearningReferenceCurationError(
            f"{owner_id} requires durable_reason for {action_note.action_type} action"
        )
    return action_note


def _downstream_authorization_receipt_from_dict(
    data: dict[str, Any],
) -> DownstreamAuthorizationReceipt:
    try:
        receipt = DownstreamAuthorizationReceipt(**data)
    except TypeError as error:
        raise LearningReferenceCurationError(
            f"invalid downstream authorization receipt: {error}"
        ) from error

    owner_id = receipt.receipt_id or "?"
    for field_name in (
        "receipt_id",
        "authorization_audit_id",
        "authorization_status",
        "authorization_scope",
        "selected_next_downstream_entry",
        "rationale",
    ):
        _require_text(getattr(receipt, field_name), field_name, owner_id)
    if receipt.authorization_status != "user_authorized_downstream":
        raise LearningReferenceCurationError(
            f"{owner_id} has invalid authorization_status"
        )
    if receipt.authorization_scope != "013_012_downstream":
        raise LearningReferenceCurationError(
            f"{owner_id} has invalid authorization_scope"
        )
    if receipt.selected_next_downstream_entry != "015-new-material-intake":
        raise LearningReferenceCurationError(
            f"{owner_id} has invalid selected_next_downstream_entry"
        )
    _require_nonempty_string_list(receipt.guardrails, "guardrails", owner_id)
    for field_name in (
        "pending_decision_count",
        "candidate_extract_delta_count",
        "review_decision_delta_count",
        "promotion_batch_delta_count",
        "formal_evidence_delta_count",
    ):
        _require_non_negative_int(getattr(receipt, field_name), field_name, owner_id)
    if not receipt.downstream_mutation_authorized:
        raise LearningReferenceCurationError(
            f"{owner_id} must record explicit downstream authorization"
        )
    for field_name in (
        "candidate_extract_delta_count",
        "review_decision_delta_count",
        "promotion_batch_delta_count",
        "formal_evidence_delta_count",
    ):
        if getattr(receipt, field_name) != 0:
            raise LearningReferenceCurationError(
                f"{owner_id} must not carry duplicate {field_name}"
            )
    return receipt


def _validate_prerequisite_action_note_links(
    action_notes: list[PrerequisiteActionNote],
    source_dir: Path,
) -> None:
    extraction_context = _load_extraction_context(source_dir)
    packages_by_id = extraction_context["packages"]
    backlog_records_by_id = extraction_context["backlog_records"]
    if not packages_by_id and not backlog_records_by_id:
        return

    materials_context = _load_materials_audit_context(source_dir)
    queue_items_by_id = materials_context["queue_items"]
    audit_records_by_id = materials_context["audit_records"]

    for action_note in action_notes:
        backlog_record = backlog_records_by_id.get(action_note.backlog_id)
        if backlog_record is None:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} references unknown 016 backlog "
                f"record: {action_note.backlog_id}"
            )
        package = packages_by_id.get(action_note.package_id)
        if package is None:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} references unknown 016 package: "
                f"{action_note.package_id}"
            )
        queue_item = queue_items_by_id.get(action_note.queue_item_id)
        if queue_item is None:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} references unknown 015 queue item: "
                f"{action_note.queue_item_id}"
            )
        audit_record = audit_records_by_id.get(action_note.audit_id)
        if audit_record is None:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} references unknown 015 audit: "
                f"{action_note.audit_id}"
            )

        if action_note.backlog_id not in package.backlog_record_ids:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} backlog_id is not listed by "
                f"package {action_note.package_id}"
            )
        if action_note.queue_item_id not in package.source_queue_snapshot_ids:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} queue item is not in package "
                "source snapshot"
            )
        if action_note.package_id != backlog_record.package_id:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} package_id does not match 016 "
                "backlog record"
            )
        if action_note.queue_item_id != backlog_record.queue_item_id:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} queue_item_id does not match "
                "016 backlog record"
            )
        if action_note.audit_id != backlog_record.audit_id:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} audit_id does not match 016 "
                "backlog record"
            )
        if action_note.action_type != backlog_record.backlog_type:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} action_type does not match 016 "
                "backlog record"
            )
        if set(action_note.missing_prerequisites) != set(
            backlog_record.missing_prerequisites
        ):
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} missing_prerequisites do not "
                "match 016 backlog record"
            )
        if action_note.recommended_action != backlog_record.recommended_action:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} recommended_action does not "
                "match 016 backlog record"
            )
        if action_note.risk_boundary != backlog_record.risk_boundary:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} risk_boundary does not match "
                "016 backlog record"
            )
        if action_note.status != backlog_record.status:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} status does not match 016 "
                "backlog record"
            )
        if queue_item.audit_id != action_note.audit_id:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} queue item audit does not match "
                "action note"
            )
        if queue_item.recommended_action != action_note.recommended_action:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} recommended_action does not "
                "match 015 queue item"
            )
        if queue_item.risk_boundary != action_note.risk_boundary:
            raise LearningReferenceCurationError(
                f"{action_note.action_note_id} risk_boundary does not match "
                "015 queue item"
            )


def load_learning_reference_notes(
    data_dir: Path | str | None = None,
) -> list[LearningReferenceNote]:
    source_dir = _data_dir(data_dir)
    notes = [
        _learning_reference_note_from_dict(item)
        for item in _read_json_list(source_dir / "learning_reference_notes.json")
    ]
    _ensure_unique([note.note_id for note in notes], "note_id")
    _validate_note_trace_links(notes, source_dir)
    return notes


def load_learning_points(
    data_dir: Path | str | None = None,
) -> list[LearningPoint]:
    source_dir = _data_dir(data_dir)
    points = [
        _learning_point_from_dict(item)
        for item in _read_json_list(source_dir / "learning_points.json")
    ]
    _ensure_unique(
        [point.learning_point_id for point in points],
        "learning_point_id",
    )
    _validate_learning_point_links(points, source_dir)
    return points


def load_candidate_intake_decisions(
    data_dir: Path | str | None = None,
) -> list[CandidateIntakeDecision]:
    source_dir = _data_dir(data_dir)
    decisions = [
        _candidate_intake_decision_from_dict(item)
        for item in _read_json_list(source_dir / "candidate_intake_decisions.json")
    ]
    _ensure_unique([decision.decision_id for decision in decisions], "decision_id")
    _validate_candidate_intake_decision_links(decisions, source_dir)
    return decisions


def load_prerequisite_action_notes(
    data_dir: Path | str | None = None,
) -> list[PrerequisiteActionNote]:
    source_dir = _data_dir(data_dir)
    action_notes = [
        _prerequisite_action_note_from_dict(item)
        for item in _read_json_list(source_dir / "prerequisite_action_notes.json")
    ]
    _ensure_unique(
        [action_note.action_note_id for action_note in action_notes],
        "action_note_id",
    )
    _validate_prerequisite_action_note_links(action_notes, source_dir)
    return action_notes


def load_downstream_authorization_receipts(
    data_dir: Path | str | None = None,
) -> list[DownstreamAuthorizationReceipt]:
    source_dir = _data_dir(data_dir)
    receipts_path = source_dir / "downstream_authorization_receipts.json"
    if not receipts_path.exists():
        return []
    receipts = [
        _downstream_authorization_receipt_from_dict(item)
        for item in _read_json_list(receipts_path)
    ]
    _ensure_unique([receipt.receipt_id for receipt in receipts], "receipt_id")
    return receipts


def _new_material_corrected_pilot_learning_entry_evaluation_item_from_dict(
    data: dict[str, Any],
    source_dir: Path,
) -> NewMaterialCorrectedPilotLearningEntryEvaluationItem:
    try:
        item = NewMaterialCorrectedPilotLearningEntryEvaluationItem(**data)
    except TypeError as error:
        raise LearningReferenceCurationError(
            "invalid new material corrected pilot learning entry evaluation "
            f"item: {error}"
        ) from error

    owner_id = item.evaluation_item_id or "?"
    for field_name in (
        "evaluation_item_id",
        "evaluation_id",
        "transcription_execution_item_id",
        "source_library_entry_id",
        "source_material_id",
        "prepared_text_artifact",
        "local_reference",
        "evaluation_status",
        "selected_next_material_entry",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    _require_string_list(item.guardrails, "guardrails", owner_id)
    _validate_enum(
        item.evaluation_status,
        NEW_MATERIAL_CORRECTED_PILOT_LEARNING_ENTRY_EVALUATION_STATUSES,
        "evaluation_status",
        owner_id,
    )
    if item.evaluation_id != NEW_MATERIAL_CORRECTED_PILOT_LEARNING_ENTRY_EVALUATION_ID:
        raise LearningReferenceCurationError(f"{owner_id} has invalid evaluation_id")
    if item.selected_next_material_entry != (
        NEW_MATERIAL_CORRECTED_PILOT_LEARNING_ENTRY_EVALUATION_NEXT_ENTRY
    ):
        raise LearningReferenceCurationError(f"{owner_id} selected unexpected next entry")

    for field_name in (
        "corrected_excerpt_count",
        "corrected_character_count",
        "page_locator_count",
        "candidate_extract_delta_count",
        "review_decision_delta_count",
        "promotion_batch_delta_count",
        "formal_evidence_delta_count",
    ):
        _require_non_negative_int(getattr(item, field_name), field_name, owner_id)
    for field_name in (
        "learning_note_allowed",
        "candidate_intake_allowed",
        "duplicate_overlap_review_required",
        "risk_boundary_review_required",
        "downstream_mutation_authorized",
    ):
        _require_bool(getattr(item, field_name), field_name, owner_id)

    if item.corrected_excerpt_count <= 0 or item.corrected_character_count <= 0:
        raise LearningReferenceCurationError(
            f"{owner_id} must reference corrected pilot excerpts"
        )
    if item.page_locator_count <= 0:
        raise LearningReferenceCurationError(f"{owner_id} must include page locators")
    if not item.learning_note_allowed:
        raise LearningReferenceCurationError(
            f"{owner_id} must allow learning-note preparation"
        )
    if item.candidate_intake_allowed:
        raise LearningReferenceCurationError(
            f"{owner_id} must block candidate intake"
        )
    if item.downstream_mutation_authorized:
        raise LearningReferenceCurationError(
            f"{owner_id} must not authorize downstream mutation"
        )
    for field_name in (
        "candidate_extract_delta_count",
        "review_decision_delta_count",
        "promotion_batch_delta_count",
        "formal_evidence_delta_count",
    ):
        if getattr(item, field_name) != 0:
            raise LearningReferenceCurationError(
                f"{owner_id} has non-zero {field_name}"
            )

    artifact_path = Path(item.prepared_text_artifact)
    if artifact_path.is_absolute() or ".." in artifact_path.parts:
        raise LearningReferenceCurationError(
            f"{owner_id} prepared text path must be relative"
        )
    if not (Path.cwd() / artifact_path).exists():
        raise LearningReferenceCurationError(
            f"{owner_id} prepared text artifact is missing"
        )

    materials_dir = _sibling_data_dir(source_dir, "materials_audit")
    if materials_dir is None:
        return item
    execution_items_by_id = {
        execution.execution_item_id: execution
        for execution in (
            materials_audit
            .load_new_material_human_corrected_transcription_execution_items(
                materials_dir
            )
        )
    }
    execution = execution_items_by_id.get(item.transcription_execution_item_id)
    if execution is None:
        raise LearningReferenceCurationError(
            f"{owner_id} references unknown transcription execution item"
        )
    if execution.execution_status != "pilot_prepared_text_created":
        raise LearningReferenceCurationError(
            f"{owner_id} transcription execution is not pilot-ready"
        )
    if not execution.learning_entry_ready:
        raise LearningReferenceCurationError(
            f"{owner_id} transcription execution is not learning-entry ready"
        )
    matching_fields = (
        "source_library_entry_id",
        "source_material_id",
        "prepared_text_artifact",
        "local_reference",
        "corrected_excerpt_count",
        "corrected_character_count",
        "page_locator_count",
    )
    for field_name in matching_fields:
        if getattr(item, field_name) != getattr(execution, field_name):
            raise LearningReferenceCurationError(
                f"{owner_id} {field_name} does not match execution item"
            )
    return item


def load_new_material_corrected_pilot_learning_entry_evaluation_items(
    data_dir: Path | str | None = None,
) -> list[NewMaterialCorrectedPilotLearningEntryEvaluationItem]:
    source_dir = _data_dir(data_dir)
    items_path = (
        source_dir
        / "new_material_corrected_pilot_learning_entry_evaluation_items.json"
    )
    if not items_path.exists():
        return []
    items = [
        _new_material_corrected_pilot_learning_entry_evaluation_item_from_dict(
            item, source_dir
        )
        for item in _read_json_list(items_path)
    ]
    _ensure_unique(
        [item.evaluation_item_id for item in items],
        "evaluation_item_id",
    )
    return items


def build_new_material_corrected_pilot_learning_entry_evaluation_summary(
    data_dir: Path | str | None = None,
) -> NewMaterialCorrectedPilotLearningEntryEvaluationSummary:
    source_dir = _data_dir(data_dir)
    items = load_new_material_corrected_pilot_learning_entry_evaluation_items(
        source_dir
    )
    materials_dir = _sibling_data_dir(source_dir, "materials_audit")
    execution_summary = None
    if materials_dir is not None:
        execution_summary = (
            materials_audit
            .build_new_material_human_corrected_transcription_execution_summary(
                materials_dir
            )
        )
    no_downstream_delta = all(
        item.candidate_extract_delta_count == 0
        and item.review_decision_delta_count == 0
        and item.promotion_batch_delta_count == 0
        and item.formal_evidence_delta_count == 0
        and not item.downstream_mutation_authorized
        for item in items
    )
    boundary_checks = {
        "evaluation_items_loaded": "passed" if items else "failed",
        "previous_corrected_pilot_ready": (
            "passed"
            if execution_summary is not None
            and execution_summary.execution_status == "pilot_prepared_text_created"
            else "failed"
        ),
        "prepared_text_artifact_exists": (
            "passed"
            if all((Path.cwd() / item.prepared_text_artifact).exists() for item in items)
            else "failed"
        ),
        "learning_note_allowed": (
            "passed"
            if items and all(item.learning_note_allowed for item in items)
            else "failed"
        ),
        "candidate_intake_blocked": (
            "passed"
            if items and all(not item.candidate_intake_allowed for item in items)
            else "failed"
        ),
        "duplicate_overlap_review_required": (
            "passed"
            if items
            and all(item.duplicate_overlap_review_required for item in items)
            else "failed"
        ),
        "risk_boundary_review_required": (
            "passed"
            if items and all(item.risk_boundary_review_required for item in items)
            else "failed"
        ),
        "013_012_not_mutated": "passed" if no_downstream_delta else "failed",
        "raw_materials_not_mutated": "passed",
    }
    return NewMaterialCorrectedPilotLearningEntryEvaluationSummary(
        evaluation_id=NEW_MATERIAL_CORRECTED_PILOT_LEARNING_ENTRY_EVALUATION_ID,
        evaluation_status=(
            "ready_for_learning_note_prep"
            if all(status == "passed" for status in boundary_checks.values())
            else "corrected_pilot_learning_entry_evaluation_needs_attention"
        ),
        evaluation_item_count=len(items),
        prepared_text_artifact_count=len(
            {item.prepared_text_artifact for item in items}
        ),
        corrected_excerpt_count=sum(item.corrected_excerpt_count for item in items),
        corrected_character_count=sum(item.corrected_character_count for item in items),
        page_locator_count=sum(item.page_locator_count for item in items),
        learning_note_allowed_count=sum(
            1 for item in items if item.learning_note_allowed
        ),
        candidate_intake_allowed_count=sum(
            1 for item in items if item.candidate_intake_allowed
        ),
        duplicate_overlap_review_required_count=sum(
            1 for item in items if item.duplicate_overlap_review_required
        ),
        risk_boundary_review_required_count=sum(
            1 for item in items if item.risk_boundary_review_required
        ),
        candidate_extract_delta_count=sum(
            item.candidate_extract_delta_count for item in items
        ),
        review_decision_delta_count=sum(
            item.review_decision_delta_count for item in items
        ),
        promotion_batch_delta_count=sum(
            item.promotion_batch_delta_count for item in items
        ),
        formal_evidence_delta_count=sum(
            item.formal_evidence_delta_count for item in items
        ),
        downstream_mutation_authorized=any(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            NEW_MATERIAL_CORRECTED_PILOT_LEARNING_ENTRY_EVALUATION_NEXT_ENTRY
        ),
        evaluation_item_ids=[item.evaluation_item_id for item in items],
        transcription_execution_item_ids=[
            item.transcription_execution_item_id for item in items
        ],
        source_entry_ids=[item.source_library_entry_id for item in items],
        source_material_ids=[item.source_material_id for item in items],
        local_references=[item.local_reference for item in items],
        prepared_text_artifacts=[item.prepared_text_artifact for item in items],
        boundary_checks=boundary_checks,
        guardrails=[
            "Use the corrected pilot only for learning-note preparation.",
            "Run overlap review before any candidate-intake decision.",
            "Run risk-boundary review before expanding the prepared-text artifact.",
            "Keep 013 and 012 writes out of this evaluation stage.",
        ],
    )


def render_new_material_corrected_pilot_learning_entry_evaluation_markdown(
    summary: NewMaterialCorrectedPilotLearningEntryEvaluationSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 017 New Material Corrected Pilot Learning Entry Evaluation",
        "",
        f"- Evaluation id: `{summary.evaluation_id}`",
        (
            "- `new-material-corrected-pilot-learning-entry-evaluation-status="
            f"{summary.evaluation_status}`"
        ),
        f"- `learning-entry-evaluation-items={summary.evaluation_item_count}`",
        f"- `prepared-text-artifacts={summary.prepared_text_artifact_count}`",
        f"- `corrected-excerpts={summary.corrected_excerpt_count}`",
        f"- `corrected-characters={summary.corrected_character_count}`",
        f"- `page-locators={summary.page_locator_count}`",
        f"- `learning-note-allowed={summary.learning_note_allowed_count}`",
        f"- `candidate-intake-allowed={summary.candidate_intake_allowed_count}`",
        (
            "- `duplicate-overlap-review-required="
            f"{summary.duplicate_overlap_review_required_count}`"
        ),
        (
            "- `risk-boundary-review-required="
            f"{summary.risk_boundary_review_required_count}`"
        ),
        f"- `candidate-extract-delta={summary.candidate_extract_delta_count}`",
        f"- `formal-evidence-delta={summary.formal_evidence_delta_count}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Learning entry evaluation item ids:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.evaluation_item_ids)
    lines.extend(["", "Prepared text artifacts:"])
    lines.extend(f"- `{artifact}`" for artifact in summary.prepared_text_artifacts)
    lines.extend(["", "Local references:"])
    lines.extend(f"- `{reference}`" for reference in summary.local_references)
    lines.extend(["", "Boundary checks:"])
    lines.extend(
        f"- `{check_id}`: `{status}`"
        for check_id, status in summary.boundary_checks.items()
    )
    lines.extend(
        [
            "",
            "Guardrails:",
            *[f"- {guardrail}" for guardrail in summary.guardrails],
        ]
    )
    return "\n".join(lines) + "\n"


def _new_material_corrected_pilot_learning_note_prep_item_from_dict(
    data: dict[str, Any],
    source_dir: Path,
) -> NewMaterialCorrectedPilotLearningNotePrepItem:
    try:
        item = NewMaterialCorrectedPilotLearningNotePrepItem(**data)
    except TypeError as error:
        raise LearningReferenceCurationError(
            f"invalid new material corrected pilot learning note prep item: {error}"
        ) from error

    owner_id = item.prep_item_id or "?"
    for field_name in (
        "prep_item_id",
        "prep_id",
        "evaluation_item_id",
        "source_library_entry_id",
        "source_material_id",
        "prepared_text_artifact",
        "local_reference",
        "prep_status",
        "proposed_note_id",
        "selected_next_material_entry",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    _require_nonempty_string_list(
        item.target_rule_families,
        "target_rule_families",
        owner_id,
    )
    _require_string_list(item.guardrails, "guardrails", owner_id)
    _validate_enum(
        item.prep_status,
        NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_PREP_STATUSES,
        "prep_status",
        owner_id,
    )
    if item.prep_id != NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_PREP_ID:
        raise LearningReferenceCurationError(f"{owner_id} has invalid prep_id")
    if item.selected_next_material_entry != (
        NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_PREP_NEXT_ENTRY
    ):
        raise LearningReferenceCurationError(f"{owner_id} selected unexpected next entry")
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise LearningReferenceCurationError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    for field_name in (
        "proposed_learning_point_count",
        "corrected_excerpt_count",
        "corrected_character_count",
        "page_locator_count",
        "candidate_extract_delta_count",
        "review_decision_delta_count",
        "promotion_batch_delta_count",
        "formal_evidence_delta_count",
    ):
        _require_non_negative_int(getattr(item, field_name), field_name, owner_id)
    for field_name in (
        "learning_note_draft_allowed",
        "candidate_intake_allowed",
        "overlap_review_required",
        "risk_boundary_review_required",
        "downstream_mutation_authorized",
    ):
        _require_bool(getattr(item, field_name), field_name, owner_id)

    if item.proposed_learning_point_count <= 0:
        raise LearningReferenceCurationError(
            f"{owner_id} must propose learning points"
        )
    if item.corrected_excerpt_count <= 0 or item.corrected_character_count <= 0:
        raise LearningReferenceCurationError(
            f"{owner_id} must reference corrected pilot excerpts"
        )
    if item.page_locator_count <= 0:
        raise LearningReferenceCurationError(f"{owner_id} must include page locators")
    if not item.learning_note_draft_allowed:
        raise LearningReferenceCurationError(
            f"{owner_id} must allow learning-note drafting"
        )
    if item.candidate_intake_allowed:
        raise LearningReferenceCurationError(
            f"{owner_id} must keep candidate intake blocked"
        )
    if item.downstream_mutation_authorized:
        raise LearningReferenceCurationError(
            f"{owner_id} must not authorize downstream mutation"
        )
    for field_name in (
        "candidate_extract_delta_count",
        "review_decision_delta_count",
        "promotion_batch_delta_count",
        "formal_evidence_delta_count",
    ):
        if getattr(item, field_name) != 0:
            raise LearningReferenceCurationError(
                f"{owner_id} has non-zero {field_name}"
            )

    artifact_path = Path(item.prepared_text_artifact)
    if artifact_path.is_absolute() or ".." in artifact_path.parts:
        raise LearningReferenceCurationError(
            f"{owner_id} prepared text path must be relative"
        )
    if not (Path.cwd() / artifact_path).exists():
        raise LearningReferenceCurationError(
            f"{owner_id} prepared text artifact is missing"
        )

    evaluation_items_by_id = {
        evaluation.evaluation_item_id: evaluation
        for evaluation in (
            load_new_material_corrected_pilot_learning_entry_evaluation_items(
                source_dir
            )
        )
    }
    evaluation = evaluation_items_by_id.get(item.evaluation_item_id)
    if evaluation is None:
        raise LearningReferenceCurationError(
            f"{owner_id} references unknown learning entry evaluation"
        )
    if evaluation.evaluation_status != "ready_for_learning_note_prep":
        raise LearningReferenceCurationError(
            f"{owner_id} evaluation is not ready for learning-note prep"
        )
    matching_fields = (
        "source_library_entry_id",
        "source_material_id",
        "prepared_text_artifact",
        "local_reference",
        "corrected_excerpt_count",
        "corrected_character_count",
        "page_locator_count",
    )
    for field_name in matching_fields:
        if getattr(item, field_name) != getattr(evaluation, field_name):
            raise LearningReferenceCurationError(
                f"{owner_id} {field_name} does not match evaluation item"
            )
    if not evaluation.learning_note_allowed or evaluation.candidate_intake_allowed:
        raise LearningReferenceCurationError(
            f"{owner_id} evaluation boundary does not allow prep"
        )
    return item


def load_new_material_corrected_pilot_learning_note_prep_items(
    data_dir: Path | str | None = None,
) -> list[NewMaterialCorrectedPilotLearningNotePrepItem]:
    source_dir = _data_dir(data_dir)
    items_path = (
        source_dir / "new_material_corrected_pilot_learning_note_prep_items.json"
    )
    if not items_path.exists():
        return []
    items = [
        _new_material_corrected_pilot_learning_note_prep_item_from_dict(
            item,
            source_dir,
        )
        for item in _read_json_list(items_path)
    ]
    _ensure_unique([item.prep_item_id for item in items], "prep_item_id")
    _ensure_unique([item.proposed_note_id for item in items], "proposed_note_id")
    return items


def build_new_material_corrected_pilot_learning_note_prep_summary(
    data_dir: Path | str | None = None,
) -> NewMaterialCorrectedPilotLearningNotePrepSummary:
    source_dir = _data_dir(data_dir)
    items = load_new_material_corrected_pilot_learning_note_prep_items(source_dir)
    evaluation_summary = (
        build_new_material_corrected_pilot_learning_entry_evaluation_summary(
            source_dir
        )
    )
    no_downstream_delta = all(
        item.candidate_extract_delta_count == 0
        and item.review_decision_delta_count == 0
        and item.promotion_batch_delta_count == 0
        and item.formal_evidence_delta_count == 0
        and not item.downstream_mutation_authorized
        for item in items
    )
    target_rule_family_counts = Counter(
        rule_family for item in items for rule_family in item.target_rule_families
    )
    boundary_checks = {
        "learning_note_prep_items_loaded": "passed" if items else "failed",
        "previous_entry_evaluation_ready": (
            "passed"
            if evaluation_summary.evaluation_status == "ready_for_learning_note_prep"
            else "failed"
        ),
        "prepared_text_artifact_exists": (
            "passed"
            if all((Path.cwd() / item.prepared_text_artifact).exists() for item in items)
            else "failed"
        ),
        "learning_note_draft_allowed": (
            "passed"
            if items and all(item.learning_note_draft_allowed for item in items)
            else "failed"
        ),
        "candidate_intake_blocked": (
            "passed"
            if items and all(not item.candidate_intake_allowed for item in items)
            else "failed"
        ),
        "overlap_review_required": (
            "passed"
            if items and all(item.overlap_review_required for item in items)
            else "failed"
        ),
        "risk_boundary_review_required": (
            "passed"
            if items and all(item.risk_boundary_review_required for item in items)
            else "failed"
        ),
        "013_012_not_mutated": "passed" if no_downstream_delta else "failed",
        "raw_materials_not_mutated": "passed",
    }
    return NewMaterialCorrectedPilotLearningNotePrepSummary(
        prep_id=NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_PREP_ID,
        prep_status=(
            "ready_for_learning_note_draft"
            if all(status == "passed" for status in boundary_checks.values())
            else "corrected_pilot_learning_note_prep_needs_attention"
        ),
        prep_item_count=len(items),
        proposed_note_count=len({item.proposed_note_id for item in items}),
        proposed_learning_point_count=sum(
            item.proposed_learning_point_count for item in items
        ),
        prepared_text_artifact_count=len(
            {item.prepared_text_artifact for item in items}
        ),
        corrected_excerpt_count=sum(item.corrected_excerpt_count for item in items),
        corrected_character_count=sum(item.corrected_character_count for item in items),
        page_locator_count=sum(item.page_locator_count for item in items),
        learning_note_draft_allowed_count=sum(
            1 for item in items if item.learning_note_draft_allowed
        ),
        candidate_intake_allowed_count=sum(
            1 for item in items if item.candidate_intake_allowed
        ),
        overlap_review_required_count=sum(
            1 for item in items if item.overlap_review_required
        ),
        risk_boundary_review_required_count=sum(
            1 for item in items if item.risk_boundary_review_required
        ),
        candidate_extract_delta_count=sum(
            item.candidate_extract_delta_count for item in items
        ),
        review_decision_delta_count=sum(
            item.review_decision_delta_count for item in items
        ),
        promotion_batch_delta_count=sum(
            item.promotion_batch_delta_count for item in items
        ),
        formal_evidence_delta_count=sum(
            item.formal_evidence_delta_count for item in items
        ),
        downstream_mutation_authorized=any(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_PREP_NEXT_ENTRY,
        prep_item_ids=[item.prep_item_id for item in items],
        evaluation_item_ids=[item.evaluation_item_id for item in items],
        proposed_note_ids=[item.proposed_note_id for item in items],
        source_entry_ids=[item.source_library_entry_id for item in items],
        source_material_ids=[item.source_material_id for item in items],
        local_references=[item.local_reference for item in items],
        prepared_text_artifacts=[item.prepared_text_artifact for item in items],
        target_rule_family_counts=dict(target_rule_family_counts),
        boundary_checks=boundary_checks,
        guardrails=[
            "Draft the learning note from bounded pilot metadata only.",
            "Keep candidate intake blocked until overlap and risk checks are resolved.",
            "Do not add 013 or 012 records from the prep packet.",
            "Do not expand the prepared-text artifact during note prep.",
        ],
    )


def render_new_material_corrected_pilot_learning_note_prep_markdown(
    summary: NewMaterialCorrectedPilotLearningNotePrepSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 017 New Material Corrected Pilot Learning Note Prep",
        "",
        f"- Prep id: `{summary.prep_id}`",
        f"- `new-material-corrected-pilot-learning-note-prep-status={summary.prep_status}`",
        f"- `learning-note-prep-items={summary.prep_item_count}`",
        f"- `proposed-learning-notes={summary.proposed_note_count}`",
        f"- `proposed-learning-points={summary.proposed_learning_point_count}`",
        f"- `prepared-text-artifacts={summary.prepared_text_artifact_count}`",
        f"- `corrected-excerpts={summary.corrected_excerpt_count}`",
        f"- `corrected-characters={summary.corrected_character_count}`",
        f"- `page-locators={summary.page_locator_count}`",
        (
            "- `learning-note-draft-allowed="
            f"{summary.learning_note_draft_allowed_count}`"
        ),
        f"- `candidate-intake-allowed={summary.candidate_intake_allowed_count}`",
        f"- `overlap-review-required={summary.overlap_review_required_count}`",
        (
            "- `risk-boundary-review-required="
            f"{summary.risk_boundary_review_required_count}`"
        ),
        f"- `candidate-extract-delta={summary.candidate_extract_delta_count}`",
        f"- `formal-evidence-delta={summary.formal_evidence_delta_count}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Learning note prep item ids:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.prep_item_ids)
    lines.extend(["", "Proposed learning note ids:"])
    lines.extend(f"- `{note_id}`" for note_id in summary.proposed_note_ids)
    lines.extend(["", "Prepared text artifacts:"])
    lines.extend(f"- `{artifact}`" for artifact in summary.prepared_text_artifacts)
    lines.extend(["", "Local references:"])
    lines.extend(f"- `{reference}`" for reference in summary.local_references)
    lines.extend(["", "Target rule families:"])
    lines.extend(
        f"- `{rule_family}`: `{count}`"
        for rule_family, count in summary.target_rule_family_counts.items()
    )
    lines.extend(["", "Boundary checks:"])
    lines.extend(
        f"- `{check_id}`: `{status}`"
        for check_id, status in summary.boundary_checks.items()
    )
    lines.extend(
        [
            "",
            "Guardrails:",
            *[f"- {guardrail}" for guardrail in summary.guardrails],
        ]
    )
    return "\n".join(lines) + "\n"


def _new_material_corrected_pilot_learning_note_draft_item_from_dict(
    data: dict[str, Any],
    source_dir: Path,
) -> NewMaterialCorrectedPilotLearningNoteDraftItem:
    try:
        item = NewMaterialCorrectedPilotLearningNoteDraftItem(**data)
    except TypeError as error:
        raise LearningReferenceCurationError(
            f"invalid new material corrected pilot learning note draft item: {error}"
        ) from error

    owner_id = item.draft_item_id or "?"
    for field_name in (
        "draft_item_id",
        "draft_id",
        "prep_item_id",
        "note_id",
        "learning_point_id",
        "source_library_entry_id",
        "source_material_id",
        "prepared_text_artifact",
        "local_reference",
        "draft_status",
        "target_rule_family",
        "risk_tier",
        "locator_summary",
        "learning_summary",
        "selected_next_material_entry",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    _require_nonempty_string_list(item.limitations, "limitations", owner_id)
    _require_string_list(item.guardrails, "guardrails", owner_id)
    _validate_enum(
        item.draft_status,
        NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_DRAFT_STATUSES,
        "draft_status",
        owner_id,
    )
    _validate_enum(item.risk_tier, EXTRACTION_PACKAGE_RISK_BOUNDARIES, "risk_tier", owner_id)
    if item.target_rule_family not in RULE_FAMILIES:
        raise LearningReferenceCurationError(
            f"{owner_id} has unsupported target_rule_family: {item.target_rule_family}"
        )
    if item.draft_id != NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_DRAFT_ID:
        raise LearningReferenceCurationError(f"{owner_id} has invalid draft_id")
    if item.selected_next_material_entry != (
        NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_DRAFT_NEXT_ENTRY
    ):
        raise LearningReferenceCurationError(f"{owner_id} selected unexpected next entry")
    for field_name in (
        "candidate_extract_delta_count",
        "review_decision_delta_count",
        "promotion_batch_delta_count",
        "formal_evidence_delta_count",
    ):
        _require_non_negative_int(getattr(item, field_name), field_name, owner_id)
    for field_name in (
        "candidate_intake_allowed",
        "completion_review_allowed",
        "downstream_mutation_authorized",
    ):
        _require_bool(getattr(item, field_name), field_name, owner_id)
    if item.candidate_intake_allowed:
        raise LearningReferenceCurationError(
            f"{owner_id} must keep candidate intake blocked"
        )
    if not item.completion_review_allowed:
        raise LearningReferenceCurationError(
            f"{owner_id} must allow completion review"
        )
    if item.downstream_mutation_authorized:
        raise LearningReferenceCurationError(
            f"{owner_id} must not authorize downstream mutation"
        )
    for field_name in (
        "candidate_extract_delta_count",
        "review_decision_delta_count",
        "promotion_batch_delta_count",
        "formal_evidence_delta_count",
    ):
        if getattr(item, field_name) != 0:
            raise LearningReferenceCurationError(
                f"{owner_id} has non-zero {field_name}"
            )
    artifact_path = Path(item.prepared_text_artifact)
    if artifact_path.is_absolute() or ".." in artifact_path.parts:
        raise LearningReferenceCurationError(
            f"{owner_id} prepared text path must be relative"
        )
    if not (Path.cwd() / artifact_path).exists():
        raise LearningReferenceCurationError(
            f"{owner_id} prepared text artifact is missing"
        )

    prep_items_by_id = {
        prep.prep_item_id: prep
        for prep in load_new_material_corrected_pilot_learning_note_prep_items(
            source_dir
        )
    }
    prep = prep_items_by_id.get(item.prep_item_id)
    if prep is None:
        raise LearningReferenceCurationError(
            f"{owner_id} references unknown learning note prep item"
        )
    if prep.prep_status != "ready_for_learning_note_draft":
        raise LearningReferenceCurationError(
            f"{owner_id} prep item is not ready for note draft"
        )
    if item.note_id != prep.proposed_note_id:
        raise LearningReferenceCurationError(f"{owner_id} note_id mismatch")
    if item.target_rule_family not in prep.target_rule_families:
        raise LearningReferenceCurationError(
            f"{owner_id} target_rule_family not prepared"
        )
    matching_fields = (
        "source_library_entry_id",
        "source_material_id",
        "prepared_text_artifact",
        "local_reference",
    )
    for field_name in matching_fields:
        if getattr(item, field_name) != getattr(prep, field_name):
            raise LearningReferenceCurationError(
                f"{owner_id} {field_name} does not match prep item"
            )
    if prep.candidate_intake_allowed or not prep.learning_note_draft_allowed:
        raise LearningReferenceCurationError(
            f"{owner_id} prep boundary does not allow draft"
        )
    return item


def load_new_material_corrected_pilot_learning_note_draft_items(
    data_dir: Path | str | None = None,
) -> list[NewMaterialCorrectedPilotLearningNoteDraftItem]:
    source_dir = _data_dir(data_dir)
    items_path = (
        source_dir / "new_material_corrected_pilot_learning_note_draft_items.json"
    )
    if not items_path.exists():
        return []
    items = [
        _new_material_corrected_pilot_learning_note_draft_item_from_dict(
            item,
            source_dir,
        )
        for item in _read_json_list(items_path)
    ]
    _ensure_unique([item.draft_item_id for item in items], "draft_item_id")
    _ensure_unique([item.note_id for item in items], "note_id")
    _ensure_unique([item.learning_point_id for item in items], "learning_point_id")
    return items


def build_new_material_corrected_pilot_learning_note_draft_summary(
    data_dir: Path | str | None = None,
) -> NewMaterialCorrectedPilotLearningNoteDraftSummary:
    source_dir = _data_dir(data_dir)
    items = load_new_material_corrected_pilot_learning_note_draft_items(source_dir)
    prep_summary = build_new_material_corrected_pilot_learning_note_prep_summary(
        source_dir
    )
    no_downstream_delta = all(
        item.candidate_extract_delta_count == 0
        and item.review_decision_delta_count == 0
        and item.promotion_batch_delta_count == 0
        and item.formal_evidence_delta_count == 0
        and not item.downstream_mutation_authorized
        for item in items
    )
    target_rule_family_counts = Counter(item.target_rule_family for item in items)
    risk_tier_counts = Counter(item.risk_tier for item in items)
    boundary_checks = {
        "learning_note_draft_items_loaded": "passed" if items else "failed",
        "previous_note_prep_ready": (
            "passed"
            if prep_summary.prep_status == "ready_for_learning_note_draft"
            else "failed"
        ),
        "learning_note_ids_prepared": (
            "passed"
            if items and set(item.note_id for item in items) <= set(prep_summary.proposed_note_ids)
            else "failed"
        ),
        "completion_review_allowed": (
            "passed"
            if items and all(item.completion_review_allowed for item in items)
            else "failed"
        ),
        "candidate_intake_blocked": (
            "passed"
            if items and all(not item.candidate_intake_allowed for item in items)
            else "failed"
        ),
        "013_012_not_mutated": "passed" if no_downstream_delta else "failed",
        "raw_materials_not_mutated": "passed",
    }
    return NewMaterialCorrectedPilotLearningNoteDraftSummary(
        draft_id=NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_DRAFT_ID,
        draft_status=(
            "ready_for_learning_completion_review"
            if all(status == "passed" for status in boundary_checks.values())
            else "corrected_pilot_learning_note_draft_needs_attention"
        ),
        draft_item_count=len(items),
        learning_note_count=len({item.note_id for item in items}),
        learning_point_count=len({item.learning_point_id for item in items}),
        candidate_intake_allowed_count=sum(
            1 for item in items if item.candidate_intake_allowed
        ),
        completion_review_allowed_count=sum(
            1 for item in items if item.completion_review_allowed
        ),
        candidate_extract_delta_count=sum(
            item.candidate_extract_delta_count for item in items
        ),
        review_decision_delta_count=sum(
            item.review_decision_delta_count for item in items
        ),
        promotion_batch_delta_count=sum(
            item.promotion_batch_delta_count for item in items
        ),
        formal_evidence_delta_count=sum(
            item.formal_evidence_delta_count for item in items
        ),
        downstream_mutation_authorized=any(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=NEW_MATERIAL_CORRECTED_PILOT_LEARNING_NOTE_DRAFT_NEXT_ENTRY,
        draft_item_ids=[item.draft_item_id for item in items],
        prep_item_ids=[item.prep_item_id for item in items],
        note_ids=[item.note_id for item in items],
        learning_point_ids=[item.learning_point_id for item in items],
        source_entry_ids=[item.source_library_entry_id for item in items],
        source_material_ids=[item.source_material_id for item in items],
        local_references=[item.local_reference for item in items],
        prepared_text_artifacts=[item.prepared_text_artifact for item in items],
        target_rule_family_counts=dict(target_rule_family_counts),
        risk_tier_counts=dict(risk_tier_counts),
        boundary_checks=boundary_checks,
        guardrails=[
            "The draft is a concise pilot learning note only.",
            "Candidate intake remains blocked by limited corrected context.",
            "Completion review must decide whether to stop or request more correction.",
            "No 013 or 012 records are created by the draft stage.",
        ],
    )


def render_new_material_corrected_pilot_learning_note_draft_markdown(
    summary: NewMaterialCorrectedPilotLearningNoteDraftSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 017 New Material Corrected Pilot Learning Note Draft",
        "",
        f"- Draft id: `{summary.draft_id}`",
        f"- `new-material-corrected-pilot-learning-note-draft-status={summary.draft_status}`",
        f"- `learning-note-draft-items={summary.draft_item_count}`",
        f"- `learning-notes={summary.learning_note_count}`",
        f"- `learning-points={summary.learning_point_count}`",
        f"- `candidate-intake-allowed={summary.candidate_intake_allowed_count}`",
        f"- `completion-review-allowed={summary.completion_review_allowed_count}`",
        f"- `candidate-extract-delta={summary.candidate_extract_delta_count}`",
        f"- `formal-evidence-delta={summary.formal_evidence_delta_count}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Learning note draft item ids:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.draft_item_ids)
    lines.extend(["", "Learning note ids:"])
    lines.extend(f"- `{note_id}`" for note_id in summary.note_ids)
    lines.extend(["", "Learning point ids:"])
    lines.extend(f"- `{point_id}`" for point_id in summary.learning_point_ids)
    lines.extend(["", "Target rule families:"])
    lines.extend(
        f"- `{rule_family}`: `{count}`"
        for rule_family, count in summary.target_rule_family_counts.items()
    )
    lines.extend(["", "Risk tiers:"])
    lines.extend(
        f"- `{risk_tier}`: `{count}`"
        for risk_tier, count in summary.risk_tier_counts.items()
    )
    lines.extend(["", "Boundary checks:"])
    lines.extend(
        f"- `{check_id}`: `{status}`"
        for check_id, status in summary.boundary_checks.items()
    )
    lines.extend(
        [
            "",
            "Guardrails:",
            *[f"- {guardrail}" for guardrail in summary.guardrails],
        ]
    )
    return "\n".join(lines) + "\n"


def _new_material_corrected_pilot_learning_completion_review_item_from_dict(
    data: dict[str, Any],
    source_dir: Path,
) -> NewMaterialCorrectedPilotLearningCompletionReviewItem:
    try:
        item = NewMaterialCorrectedPilotLearningCompletionReviewItem(**data)
    except TypeError as error:
        raise LearningReferenceCurationError(
            "invalid new material corrected pilot learning completion review "
            f"item: {error}"
        ) from error

    owner_id = item.completion_item_id or "?"
    for field_name in (
        "completion_item_id",
        "completion_id",
        "draft_item_id",
        "note_id",
        "learning_point_id",
        "source_library_entry_id",
        "source_material_id",
        "prepared_text_artifact",
        "local_reference",
        "completion_status",
        "next_material_entry",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    _require_string_list(item.guardrails, "guardrails", owner_id)
    _validate_enum(
        item.completion_status,
        NEW_MATERIAL_CORRECTED_PILOT_LEARNING_COMPLETION_REVIEW_STATUSES,
        "completion_status",
        owner_id,
    )
    if item.completion_id != NEW_MATERIAL_CORRECTED_PILOT_LEARNING_COMPLETION_REVIEW_ID:
        raise LearningReferenceCurationError(f"{owner_id} has invalid completion_id")
    if item.next_material_entry != (
        NEW_MATERIAL_CORRECTED_PILOT_LEARNING_COMPLETION_REVIEW_NEXT_ENTRY
    ):
        raise LearningReferenceCurationError(f"{owner_id} selected unexpected next entry")
    for field_name in (
        "learning_note_closed",
        "candidate_intake_allowed",
        "additional_correction_required",
        "downstream_mutation_authorized",
    ):
        _require_bool(getattr(item, field_name), field_name, owner_id)
    for field_name in (
        "candidate_extract_delta_count",
        "review_decision_delta_count",
        "promotion_batch_delta_count",
        "formal_evidence_delta_count",
    ):
        _require_non_negative_int(getattr(item, field_name), field_name, owner_id)
    if not item.learning_note_closed:
        raise LearningReferenceCurationError(f"{owner_id} must close learning note")
    if item.candidate_intake_allowed:
        raise LearningReferenceCurationError(
            f"{owner_id} must keep candidate intake blocked"
        )
    if not item.additional_correction_required:
        raise LearningReferenceCurationError(
            f"{owner_id} must route to additional correction"
        )
    if item.downstream_mutation_authorized:
        raise LearningReferenceCurationError(
            f"{owner_id} must not authorize downstream mutation"
        )
    for field_name in (
        "candidate_extract_delta_count",
        "review_decision_delta_count",
        "promotion_batch_delta_count",
        "formal_evidence_delta_count",
    ):
        if getattr(item, field_name) != 0:
            raise LearningReferenceCurationError(
                f"{owner_id} has non-zero {field_name}"
            )

    draft_items_by_id = {
        draft.draft_item_id: draft
        for draft in load_new_material_corrected_pilot_learning_note_draft_items(
            source_dir
        )
    }
    draft = draft_items_by_id.get(item.draft_item_id)
    if draft is None:
        raise LearningReferenceCurationError(
            f"{owner_id} references unknown learning note draft item"
        )
    if draft.draft_status != "ready_for_learning_completion_review":
        raise LearningReferenceCurationError(
            f"{owner_id} draft item is not ready for completion review"
        )
    matching_fields = (
        "note_id",
        "learning_point_id",
        "source_library_entry_id",
        "source_material_id",
        "prepared_text_artifact",
        "local_reference",
    )
    for field_name in matching_fields:
        if getattr(item, field_name) != getattr(draft, field_name):
            raise LearningReferenceCurationError(
                f"{owner_id} {field_name} does not match draft item"
            )
    return item


def load_new_material_corrected_pilot_learning_completion_review_items(
    data_dir: Path | str | None = None,
) -> list[NewMaterialCorrectedPilotLearningCompletionReviewItem]:
    source_dir = _data_dir(data_dir)
    items_path = (
        source_dir
        / "new_material_corrected_pilot_learning_completion_review_items.json"
    )
    if not items_path.exists():
        return []
    items = [
        _new_material_corrected_pilot_learning_completion_review_item_from_dict(
            item,
            source_dir,
        )
        for item in _read_json_list(items_path)
    ]
    _ensure_unique([item.completion_item_id for item in items], "completion_item_id")
    return items


def build_new_material_corrected_pilot_learning_completion_review_summary(
    data_dir: Path | str | None = None,
) -> NewMaterialCorrectedPilotLearningCompletionReviewSummary:
    source_dir = _data_dir(data_dir)
    items = load_new_material_corrected_pilot_learning_completion_review_items(
        source_dir
    )
    draft_summary = build_new_material_corrected_pilot_learning_note_draft_summary(
        source_dir
    )
    no_downstream_delta = all(
        item.candidate_extract_delta_count == 0
        and item.review_decision_delta_count == 0
        and item.promotion_batch_delta_count == 0
        and item.formal_evidence_delta_count == 0
        and not item.downstream_mutation_authorized
        for item in items
    )
    boundary_checks = {
        "completion_review_items_loaded": "passed" if items else "failed",
        "previous_note_draft_ready": (
            "passed"
            if draft_summary.draft_status == "ready_for_learning_completion_review"
            else "failed"
        ),
        "learning_note_closed": (
            "passed"
            if items and all(item.learning_note_closed for item in items)
            else "failed"
        ),
        "candidate_intake_blocked": (
            "passed"
            if items and all(not item.candidate_intake_allowed for item in items)
            else "failed"
        ),
        "additional_correction_routed": (
            "passed"
            if items and all(item.additional_correction_required for item in items)
            else "failed"
        ),
        "013_012_not_mutated": "passed" if no_downstream_delta else "failed",
        "raw_materials_not_mutated": "passed",
    }
    next_entries = {item.next_material_entry for item in items}
    return NewMaterialCorrectedPilotLearningCompletionReviewSummary(
        completion_id=NEW_MATERIAL_CORRECTED_PILOT_LEARNING_COMPLETION_REVIEW_ID,
        completion_status=(
            "current_pilot_learning_completed_candidate_intake_blocked"
            if all(status == "passed" for status in boundary_checks.values())
            else "corrected_pilot_learning_completion_review_needs_attention"
        ),
        completion_item_count=len(items),
        learning_note_closed_count=sum(1 for item in items if item.learning_note_closed),
        candidate_intake_allowed_count=sum(
            1 for item in items if item.candidate_intake_allowed
        ),
        additional_correction_required_count=sum(
            1 for item in items if item.additional_correction_required
        ),
        candidate_extract_delta_count=sum(
            item.candidate_extract_delta_count for item in items
        ),
        review_decision_delta_count=sum(
            item.review_decision_delta_count for item in items
        ),
        promotion_batch_delta_count=sum(
            item.promotion_batch_delta_count for item in items
        ),
        formal_evidence_delta_count=sum(
            item.formal_evidence_delta_count for item in items
        ),
        downstream_mutation_authorized=any(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            next(iter(next_entries))
            if len(next_entries) == 1
            else NEW_MATERIAL_CORRECTED_PILOT_LEARNING_COMPLETION_REVIEW_NEXT_ENTRY
        ),
        completion_item_ids=[item.completion_item_id for item in items],
        draft_item_ids=[item.draft_item_id for item in items],
        note_ids=[item.note_id for item in items],
        learning_point_ids=[item.learning_point_id for item in items],
        source_entry_ids=[item.source_library_entry_id for item in items],
        source_material_ids=[item.source_material_id for item in items],
        local_references=[item.local_reference for item in items],
        prepared_text_artifacts=[item.prepared_text_artifact for item in items],
        boundary_checks=boundary_checks,
        guardrails=[
            "The current pilot learning task is closed at 017 only.",
            "Candidate intake remains blocked until more corrected context exists.",
            "The next material action is additional bounded correction selection.",
            "No 013 or 012 records are created by this completion review.",
        ],
    )


def render_new_material_corrected_pilot_learning_completion_review_markdown(
    summary: NewMaterialCorrectedPilotLearningCompletionReviewSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 017 New Material Corrected Pilot Learning Completion Review",
        "",
        f"- Completion id: `{summary.completion_id}`",
        (
            "- `new-material-corrected-pilot-learning-completion-review-status="
            f"{summary.completion_status}`"
        ),
        f"- `learning-completion-review-items={summary.completion_item_count}`",
        f"- `learning-notes-closed={summary.learning_note_closed_count}`",
        f"- `candidate-intake-allowed={summary.candidate_intake_allowed_count}`",
        (
            "- `additional-correction-required="
            f"{summary.additional_correction_required_count}`"
        ),
        f"- `candidate-extract-delta={summary.candidate_extract_delta_count}`",
        f"- `formal-evidence-delta={summary.formal_evidence_delta_count}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Learning completion review item ids:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.completion_item_ids)
    lines.extend(["", "Learning note ids:"])
    lines.extend(f"- `{note_id}`" for note_id in summary.note_ids)
    lines.extend(["", "Learning point ids:"])
    lines.extend(f"- `{point_id}`" for point_id in summary.learning_point_ids)
    lines.extend(["", "Boundary checks:"])
    lines.extend(
        f"- `{check_id}`: `{status}`"
        for check_id, status in summary.boundary_checks.items()
    )
    lines.extend(
        [
            "",
            "Guardrails:",
            *[f"- {guardrail}" for guardrail in summary.guardrails],
        ]
    )
    return "\n".join(lines) + "\n"


def _write_json_list(path: Path, payload: list[dict[str, Any]]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _candidate_payload_from_decision(
    decision: CandidateIntakeDecision,
    point: LearningPoint,
    note: LearningReferenceNote,
    *,
    applied_at: str,
) -> dict[str, Any]:
    return {
        "candidate_id": decision.candidate_id,
        "material_id": decision.source_material_id,
        "source_locator": (
            f"learning-reference:{note.note_id}#{point.learning_point_id}; "
            f"locator_requirement={point.source_locator}"
        ),
        "extracted_meaning": point.summary,
        "short_quote": "",
        "proposed_rule_family": point.proposed_rule_family,
        "risk_tier": point.risk_tier,
        "status": "pending_review",
        "proposed_limitations": point.limitations,
        "related_evidence_ids": [],
        "related_conflict_ids": [],
        "related_gap_ids": [],
        "duplicate_of": "",
        "created_by": "learning_reference_curation",
        "created_at": applied_at,
    }


def apply_candidate_intake_decisions(
    selected_decision_ids: list[str],
    data_dir: Path | str | None = None,
    *,
    source_intake_data_dir: Path | str | None = None,
    applied_at: str = "2026-06-01",
) -> list[source_intake.CandidateExtract]:
    if not selected_decision_ids:
        return []
    _ensure_unique(selected_decision_ids, "selected_decision_id")

    source_dir = _data_dir(data_dir)
    intake_dir = _resolve_source_intake_dir(source_dir, source_intake_data_dir)
    decisions = load_candidate_intake_decisions(source_dir)
    points = load_learning_points(source_dir)
    notes = load_learning_reference_notes(source_dir)
    decisions_by_id = {decision.decision_id: decision for decision in decisions}
    points_by_id = {point.learning_point_id: point for point in points}
    notes_by_id = {note.note_id: note for note in notes}
    existing_candidates = source_intake.load_candidate_extracts(intake_dir)
    existing_candidate_ids = {candidate.candidate_id for candidate in existing_candidates}

    selected_decisions: list[CandidateIntakeDecision] = []
    for decision_id in selected_decision_ids:
        decision = decisions_by_id.get(decision_id)
        if decision is None:
            raise LearningReferenceCurationError(
                f"unknown candidate-intake decision selected: {decision_id}"
            )
        if decision.decision not in {
            "create_candidate",
            "reuse_existing",
            "avoid_duplicate",
        }:
            raise LearningReferenceCurationError(
                f"{decision_id} requires actionable candidate-intake decision"
            )
        if decision.status != "planned":
            raise LearningReferenceCurationError(
                f"{decision_id} requires planned decision status"
            )
        if decision.decision == "create_candidate" and (
            decision.candidate_id in existing_candidate_ids
        ):
            raise LearningReferenceCurationError(
                f"{decision_id} candidate_id already exists"
            )
        if decision.decision in {"reuse_existing", "avoid_duplicate"} and (
            decision.candidate_id not in existing_candidate_ids
        ):
            raise LearningReferenceCurationError(
                f"{decision_id} candidate_id must reference an existing candidate"
            )
        selected_decisions.append(decision)

    candidate_records = _read_json_list(intake_dir / "candidate_extracts.json")
    candidate_payloads: list[dict[str, Any]] = []
    for decision in selected_decisions:
        if decision.decision != "create_candidate":
            continue
        point = points_by_id[decision.learning_point_id]
        note = notes_by_id[point.note_id]
        candidate_payload = _candidate_payload_from_decision(
            decision,
            point,
            note,
            applied_at=applied_at,
        )
        candidate_records.append(candidate_payload)
        candidate_payloads.append(candidate_payload)

    decision_records = _read_json_list(source_dir / "candidate_intake_decisions.json")
    selected_id_set = set(selected_decision_ids)
    for record in decision_records:
        if record["decision_id"] in selected_id_set:
            record["status"] = "applied"
            record["updated_at"] = applied_at

    _write_json_list(intake_dir / "candidate_extracts.json", candidate_records)
    _write_json_list(source_dir / "candidate_intake_decisions.json", decision_records)

    source_intake.load_candidate_extracts(intake_dir)
    load_candidate_intake_decisions(source_dir)
    return [
        source_intake.CandidateExtract(**candidate_payload)
        for candidate_payload in candidate_payloads
    ]


def build_learning_reference_progress_summary(
    data_dir: Path | str | None = None,
) -> LearningReferenceProgressSummary:
    source_dir = _data_dir(data_dir)
    notes = load_learning_reference_notes(source_dir)
    points = load_learning_points(source_dir)
    decisions = load_candidate_intake_decisions(source_dir)
    action_notes = load_prerequisite_action_notes(source_dir)

    note_counts = Counter(note.status for note in notes)
    learning_point_counts = Counter(point.candidate_readiness for point in points)
    decision_counts = Counter(decision.decision for decision in decisions)
    decision_counts.update(f"status:{decision.status}" for decision in decisions)
    prerequisite_action_counts = Counter(
        action_note.action_type for action_note in action_notes
    )
    prerequisite_action_counts.update(
        f"status:{action_note.status}" for action_note in action_notes
    )
    risk_tier_counts = Counter(note.risk_boundary for note in notes)
    risk_tier_counts.update(point.risk_tier for point in points)
    risk_tier_counts.update(action_note.risk_boundary for action_note in action_notes)
    note_rule_family_counts = Counter(
        rule_family
        for note in notes
        for rule_family in note.target_rule_families
    )

    next_action_ids = [
        note.note_id
        for note in notes
        if note.status in {"draft", "ready_for_candidate_intake"}
    ]
    next_action_ids.extend(
        decision.decision_id
        for decision in decisions
        if decision.status == "planned"
    )
    next_action_ids.extend(
        action_note.action_note_id
        for action_note in action_notes
        if action_note.status in {"planned", "active"}
    )

    return LearningReferenceProgressSummary(
        note_counts=dict(note_counts),
        learning_point_counts=dict(learning_point_counts),
        decision_counts=dict(decision_counts),
        prerequisite_action_counts=dict(prerequisite_action_counts),
        risk_tier_counts=dict(risk_tier_counts),
        overlap_warning_count=sum(len(note.overlap_candidate_ids) for note in notes),
        candidate_ready_count=sum(
            1 for point in points if point.candidate_readiness == "ready"
        ),
        candidate_decision_count=len(decisions),
        formal_evidence_delta=0,
        next_action_ids=next_action_ids,
        note_rule_family_counts=dict(note_rule_family_counts),
        selected_task_ids=[note.task_id for note in notes],
    )


def build_learning_reference_authorization_audit(
    data_dir: Path | str | None = None,
    *,
    source_intake_data_dir: Path | str | None = None,
    classical_sources_data_dir: Path | str | None = None,
) -> LearningReferenceAuthorizationAudit:
    source_dir = _data_dir(data_dir)
    summary = build_learning_reference_progress_summary(source_dir)
    decisions = load_candidate_intake_decisions(source_dir)

    intake_dir = _resolve_source_intake_dir(source_dir, source_intake_data_dir)
    classical_dir = _resolve_classical_sources_dir(source_dir, classical_sources_data_dir)
    candidates = source_intake.load_candidate_extracts(intake_dir)
    reviews = source_intake.load_review_decisions(intake_dir)
    promotion_batches = source_intake.load_promotion_batches(intake_dir)
    evidence_units = classical_sources.load_evidence_units(classical_dir)

    candidate_status_counts = Counter(candidate.status for candidate in candidates)
    review_decision_counts = Counter(review.decision for review in reviews)
    promotion_review_status_counts = Counter(
        batch.review_status for batch in promotion_batches
    )
    leakage_counts = {
        "learning_reference_source_refs_in_012": sum(
            1
            for unit in evidence_units
            if unit.source_ref.startswith("learning-reference:")
        ),
        "candidate_id_source_refs_in_012": sum(
            1 for unit in evidence_units if "candidate_" in unit.source_ref
        ),
        "learning_closure_source_refs_in_012": sum(
            1
            for unit in evidence_units
            if "learning-closure:" in unit.source_ref
        ),
    }

    all_notes_started = summary.note_counts == {
        "candidate_intake_started": len(summary.selected_task_ids)
    }
    all_decisions_applied = (
        summary.decision_counts.get("status:applied", 0) == len(decisions)
        and not any(
            summary.decision_counts.get(f"status:{status}", 0)
            for status in ("planned", "deferred", "blocked")
        )
    )
    downstream_counts_aligned = (
        len(candidates) == len(reviews)
        and set(promotion_review_status_counts) == {"reviewed"}
    )
    formal_boundary_clean = (
        summary.formal_evidence_delta == 0
        and not any(leakage_counts.values())
    )
    clearance_checks = {
        "017_notes_closed": "passed" if all_notes_started else "failed",
        "017_no_active_next_actions": (
            "passed" if not summary.next_action_ids else "failed"
        ),
        "017_decisions_applied": "passed" if all_decisions_applied else "failed",
        "013_candidate_review_promotion_counts_aligned": (
            "passed" if downstream_counts_aligned else "failed"
        ),
        "012_formal_evidence_boundary_clean": (
            "passed" if formal_boundary_clean else "failed"
        ),
        "downstream_mutation_requires_explicit_request": "passed",
    }
    authorization_status = (
        "ready_for_explicit_downstream_authorization"
        if all(value == "passed" for value in clearance_checks.values())
        else "blocked_until_boundary_clearance"
    )

    return LearningReferenceAuthorizationAudit(
        audit_id="017-candidate-formal-evidence-authorization-audit",
        authorization_status=authorization_status,
        downstream_mutation_authorized=False,
        note_counts=summary.note_counts,
        decision_counts=summary.decision_counts,
        candidate_status_counts=dict(candidate_status_counts),
        review_decision_counts=dict(review_decision_counts),
        promotion_review_status_counts=dict(promotion_review_status_counts),
        formal_evidence_unit_count=len(evidence_units),
        formal_evidence_delta=summary.formal_evidence_delta,
        leakage_counts=leakage_counts,
        clearance_checks=clearance_checks,
        next_action_ids=summary.next_action_ids,
        next_downstream_entry=(
            "013-explicit-candidate-review-or-015-queue-refresh"
        ),
        guardrails=[
            "Authorization audit is read-only 017 boundary metadata.",
            "No 013 candidate, review, or promotion mutation is authorized here.",
            "No 012 formal evidence mutation is authorized here.",
        ],
    )


def render_learning_reference_authorization_audit_markdown(
    audit: LearningReferenceAuthorizationAudit,
) -> str:
    boundary_leakage = sum(audit.leakage_counts.values())
    downstream_mutation_authorized = (
        "true" if audit.downstream_mutation_authorized else "false"
    )
    lines = [
        "## Authorization Audit Packet",
        "",
        f"- Audit id: `{audit.audit_id}`",
        f"- `authorization-status={audit.authorization_status}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        (
            "- `017-notes-closed="
            f"{audit.note_counts.get('candidate_intake_started', 0)}`"
        ),
        f"- `017-next-action-ids={len(audit.next_action_ids)}`",
        (
            "- `017-applied-decisions="
            f"{audit.decision_counts.get('status:applied', 0)}`"
        ),
        (
            "- `013-candidate-extracts="
            f"{sum(audit.candidate_status_counts.values())}`"
        ),
        (
            "- `013-review-decisions="
            f"{sum(audit.review_decision_counts.values())}`"
        ),
        (
            "- `013-promotion-batches="
            f"{sum(audit.promotion_review_status_counts.values())}`"
        ),
        f"- `012-formal-evidence-units={audit.formal_evidence_unit_count}`",
        f"- `formal_evidence_delta={audit.formal_evidence_delta}`",
        f"- `012-boundary-leakage={boundary_leakage}`",
        f"- `next-downstream-entry={audit.next_downstream_entry}`",
        "",
        "Clearance checks:",
    ]
    lines.extend(
        f"- `{check_id}`: `{status}`"
        for check_id, status in audit.clearance_checks.items()
    )
    lines.extend(
        [
            "",
            "Guardrails:",
            *[f"- {guardrail}" for guardrail in audit.guardrails],
        ]
    )
    return "\n".join(lines) + "\n"


def build_downstream_authorization_summary(
    data_dir: Path | str | None = None,
    *,
    source_intake_data_dir: Path | str | None = None,
    classical_sources_data_dir: Path | str | None = None,
) -> DownstreamAuthorizationSummary:
    source_dir = _data_dir(data_dir)
    receipts = load_downstream_authorization_receipts(source_dir)
    audit = build_learning_reference_authorization_audit(
        source_dir,
        source_intake_data_dir=source_intake_data_dir,
        classical_sources_data_dir=classical_sources_data_dir,
    )
    decisions = load_candidate_intake_decisions(source_dir)
    intake_dir = _resolve_source_intake_dir(source_dir, source_intake_data_dir)
    classical_dir = _resolve_classical_sources_dir(
        source_dir,
        classical_sources_data_dir,
    )
    candidates = source_intake.load_candidate_extracts(intake_dir)
    reviews = source_intake.load_review_decisions(intake_dir)
    promotion_batches = source_intake.load_promotion_batches(intake_dir)
    evidence_units = classical_sources.load_evidence_units(classical_dir)

    pending_decision_count = sum(
        1 for decision in decisions if decision.status == "planned"
    )
    no_duplicate_downstream_delta = all(
        receipt.pending_decision_count == pending_decision_count
        and receipt.candidate_extract_delta_count == 0
        and receipt.review_decision_delta_count == 0
        and receipt.promotion_batch_delta_count == 0
        and receipt.formal_evidence_delta_count == 0
        for receipt in receipts
    )
    boundary_checks = {
        "authorization_receipts_loaded": "passed" if receipts else "failed",
        "user_authorized_downstream": (
            "passed"
            if receipts
            and all(
                receipt.authorization_status == "user_authorized_downstream"
                and receipt.downstream_mutation_authorized
                for receipt in receipts
            )
            else "failed"
        ),
        "authorization_audit_ready": (
            "passed"
            if audit.authorization_status
            == "ready_for_explicit_downstream_authorization"
            else "failed"
        ),
        "no_pending_017_decisions": (
            "passed" if pending_decision_count == 0 else "failed"
        ),
        "013_candidate_review_counts_aligned": (
            "passed" if len(candidates) == len(reviews) else "failed"
        ),
        "012_formal_evidence_boundary_clean": (
            "passed"
            if audit.formal_evidence_delta == 0
            and not any(audit.leakage_counts.values())
            else "failed"
        ),
        "no_duplicate_downstream_delta": (
            "passed" if no_duplicate_downstream_delta else "failed"
        ),
    }

    return DownstreamAuthorizationSummary(
        authorization_id="013-012-explicit-downstream-authorization",
        authorization_status=(
            "downstream_authorization_consumed"
            if all(status == "passed" for status in boundary_checks.values())
            else "downstream_authorization_needs_attention"
        ),
        authorization_receipt_count=len(receipts),
        authorization_scope=(
            receipts[0].authorization_scope if receipts else "013_012_downstream"
        ),
        audit_authorization_status=audit.authorization_status,
        pending_decision_count=pending_decision_count,
        applied_decision_count=audit.decision_counts.get("status:applied", 0),
        candidate_extract_count=len(candidates),
        review_decision_count=len(reviews),
        promotion_batch_count=len(promotion_batches),
        formal_evidence_unit_count=len(evidence_units),
        candidate_extract_delta_count=sum(
            receipt.candidate_extract_delta_count for receipt in receipts
        ),
        review_decision_delta_count=sum(
            receipt.review_decision_delta_count for receipt in receipts
        ),
        promotion_batch_delta_count=sum(
            receipt.promotion_batch_delta_count for receipt in receipts
        ),
        formal_evidence_delta_count=sum(
            receipt.formal_evidence_delta_count for receipt in receipts
        ),
        downstream_mutation_authorized=any(
            receipt.downstream_mutation_authorized for receipt in receipts
        ),
        next_downstream_entry=(
            receipts[0].selected_next_downstream_entry
            if receipts
            else "015-new-material-intake"
        ),
        receipt_ids=[receipt.receipt_id for receipt in receipts],
        authorization_audit_ids=[
            receipt.authorization_audit_id for receipt in receipts
        ],
        boundary_checks=boundary_checks,
        guardrails=[
            "The explicit user authorization is recorded for 013/012 downstream work.",
            "Current 017 candidate-intake decisions are already applied, so no duplicate downstream writes are needed.",
            "Future downstream additions should start from a new bounded material intake surface.",
            "External raw materials remain unchanged.",
        ],
    )


def render_downstream_authorization_markdown(
    summary: DownstreamAuthorizationSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## Explicit Downstream Authorization Receipt",
        "",
        f"- Authorization id: `{summary.authorization_id}`",
        (
            "- `downstream-authorization-status="
            f"{summary.authorization_status}`"
        ),
        f"- `authorization-receipts={summary.authorization_receipt_count}`",
        f"- `authorization-scope={summary.authorization_scope}`",
        f"- `audit-authorization-status={summary.audit_authorization_status}`",
        f"- `pending-017-decisions={summary.pending_decision_count}`",
        f"- `017-applied-decisions={summary.applied_decision_count}`",
        f"- `013-candidate-extracts={summary.candidate_extract_count}`",
        f"- `013-review-decisions={summary.review_decision_count}`",
        f"- `013-promotion-batches={summary.promotion_batch_count}`",
        f"- `012-formal-evidence-units={summary.formal_evidence_unit_count}`",
        f"- `candidate-extract-delta={summary.candidate_extract_delta_count}`",
        f"- `review-decision-delta={summary.review_decision_delta_count}`",
        f"- `promotion-batch-delta={summary.promotion_batch_delta_count}`",
        f"- `formal-evidence-delta={summary.formal_evidence_delta_count}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-downstream-entry={summary.next_downstream_entry}`",
        "",
        "Receipt ids:",
    ]
    lines.extend(f"- `{receipt_id}`" for receipt_id in summary.receipt_ids)
    lines.extend(["", "Authorization audit ids:"])
    lines.extend(
        f"- `{audit_id}`" for audit_id in summary.authorization_audit_ids
    )
    lines.extend(["", "Boundary checks:"])
    lines.extend(
        f"- `{check_id}`: `{status}`"
        for check_id, status in summary.boundary_checks.items()
    )
    lines.extend(
        [
            "",
            "Guardrails:",
            *[f"- {guardrail}" for guardrail in summary.guardrails],
        ]
    )
    return "\n".join(lines) + "\n"


def _normalize_boundary_text(value: str) -> str:
    return value.lower().replace("_", " ").replace("-", " ")


def _contains_marker(value: str, markers: tuple[str, ...]) -> bool:
    normalized = _normalize_boundary_text(value)
    return any(_normalize_boundary_text(marker) in normalized for marker in markers)


def _iter_note_quality_text_fields(
    notes: list[LearningReferenceNote],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for note in notes:
        fields.extend(
            (
                (note.note_id, "source_title", note.source_title),
                (note.note_id, "rights_note", note.rights_note),
                (note.note_id, "source_quality_note", note.source_quality_note),
                (note.note_id, "locator_requirement", note.locator_requirement),
                (note.note_id, "risk_boundary", note.risk_boundary),
            )
        )
        fields.extend(
            (note.note_id, "target_rule_families", item)
            for item in note.target_rule_families
        )
        fields.extend(
            (note.note_id, "learning_points", item)
            for item in note.learning_points
        )
        fields.extend(
            (note.note_id, "overlap_candidate_ids", item)
            for item in note.overlap_candidate_ids
        )
    return fields


def _iter_point_quality_text_fields(
    points: list[LearningPoint],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for point in points:
        fields.extend(
            (
                (point.learning_point_id, "point_label", point.point_label),
                (point.learning_point_id, "source_locator", point.source_locator),
                (point.learning_point_id, "summary", point.summary),
                (
                    point.learning_point_id,
                    "proposed_rule_family",
                    point.proposed_rule_family,
                ),
                (point.learning_point_id, "risk_tier", point.risk_tier),
                (
                    point.learning_point_id,
                    "candidate_readiness",
                    point.candidate_readiness,
                ),
                (
                    point.learning_point_id,
                    "candidate_decision_id",
                    point.candidate_decision_id,
                ),
            )
        )
        fields.extend(
            (point.learning_point_id, "limitations", item)
            for item in point.limitations
        )
    return fields


def _iter_decision_quality_text_fields(
    decisions: list[CandidateIntakeDecision],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for decision in decisions:
        fields.extend(
            (
                (decision.decision_id, "decision", decision.decision),
                (decision.decision_id, "source_material_id", decision.source_material_id),
                (decision.decision_id, "candidate_id", decision.candidate_id),
                (decision.decision_id, "rationale", decision.rationale),
                (decision.decision_id, "status", decision.status),
            )
        )
        fields.extend(
            (decision.decision_id, "overlap_candidate_ids", item)
            for item in decision.overlap_candidate_ids
        )
    return fields


def _iter_action_note_quality_text_fields(
    action_notes: list[PrerequisiteActionNote],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for action_note in action_notes:
        fields.extend(
            (
                (action_note.action_note_id, "action_type", action_note.action_type),
                (
                    action_note.action_note_id,
                    "durable_reason",
                    action_note.durable_reason,
                ),
                (
                    action_note.action_note_id,
                    "recommended_action",
                    action_note.recommended_action,
                ),
                (
                    action_note.action_note_id,
                    "risk_boundary",
                    action_note.risk_boundary,
                ),
                (action_note.action_note_id, "status", action_note.status),
            )
        )
        fields.extend(
            (action_note.action_note_id, "missing_prerequisites", item)
            for item in action_note.missing_prerequisites
        )
    return fields


def _iter_downstream_receipt_quality_text_fields(
    receipts: list[DownstreamAuthorizationReceipt],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for receipt in receipts:
        fields.extend(
            (
                (
                    receipt.receipt_id,
                    "authorization_scope",
                    receipt.authorization_scope,
                ),
                (
                    receipt.receipt_id,
                    "selected_next_downstream_entry",
                    receipt.selected_next_downstream_entry,
                ),
                (receipt.receipt_id, "rationale", receipt.rationale),
            )
        )
        fields.extend(
            (receipt.receipt_id, "guardrails", guardrail)
            for guardrail in receipt.guardrails
        )
    return fields


def _iter_corrected_pilot_learning_entry_evaluation_quality_text_fields(
    items: list[NewMaterialCorrectedPilotLearningEntryEvaluationItem],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for item in items:
        fields.extend(
            (
                (
                    item.evaluation_item_id,
                    "prepared_text_artifact",
                    item.prepared_text_artifact,
                ),
                (item.evaluation_item_id, "local_reference", item.local_reference),
                (
                    item.evaluation_item_id,
                    "evaluation_status",
                    item.evaluation_status,
                ),
                (
                    item.evaluation_item_id,
                    "selected_next_material_entry",
                    item.selected_next_material_entry,
                ),
                (item.evaluation_item_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.evaluation_item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    return fields


def _iter_corrected_pilot_learning_note_prep_quality_text_fields(
    items: list[NewMaterialCorrectedPilotLearningNotePrepItem],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for item in items:
        fields.extend(
            (
                (item.prep_item_id, "prepared_text_artifact", item.prepared_text_artifact),
                (item.prep_item_id, "local_reference", item.local_reference),
                (item.prep_item_id, "prep_status", item.prep_status),
                (item.prep_item_id, "proposed_note_id", item.proposed_note_id),
                (
                    item.prep_item_id,
                    "selected_next_material_entry",
                    item.selected_next_material_entry,
                ),
                (item.prep_item_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.prep_item_id, "target_rule_families", rule_family)
            for rule_family in item.target_rule_families
        )
        fields.extend(
            (item.prep_item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    return fields


def _iter_corrected_pilot_learning_note_draft_quality_text_fields(
    items: list[NewMaterialCorrectedPilotLearningNoteDraftItem],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for item in items:
        fields.extend(
            (
                (item.draft_item_id, "note_id", item.note_id),
                (item.draft_item_id, "learning_point_id", item.learning_point_id),
                (item.draft_item_id, "prepared_text_artifact", item.prepared_text_artifact),
                (item.draft_item_id, "local_reference", item.local_reference),
                (item.draft_item_id, "draft_status", item.draft_status),
                (item.draft_item_id, "target_rule_family", item.target_rule_family),
                (item.draft_item_id, "risk_tier", item.risk_tier),
                (item.draft_item_id, "locator_summary", item.locator_summary),
                (item.draft_item_id, "learning_summary", item.learning_summary),
                (
                    item.draft_item_id,
                    "selected_next_material_entry",
                    item.selected_next_material_entry,
                ),
                (item.draft_item_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.draft_item_id, "limitations", limitation)
            for limitation in item.limitations
        )
        fields.extend(
            (item.draft_item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    return fields


def _iter_corrected_pilot_learning_completion_review_quality_text_fields(
    items: list[NewMaterialCorrectedPilotLearningCompletionReviewItem],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for item in items:
        fields.extend(
            (
                (item.completion_item_id, "note_id", item.note_id),
                (item.completion_item_id, "learning_point_id", item.learning_point_id),
                (
                    item.completion_item_id,
                    "prepared_text_artifact",
                    item.prepared_text_artifact,
                ),
                (item.completion_item_id, "local_reference", item.local_reference),
                (item.completion_item_id, "completion_status", item.completion_status),
                (item.completion_item_id, "next_material_entry", item.next_material_entry),
                (item.completion_item_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.completion_item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    return fields


def _validate_quality_text(fields: list[tuple[str, str, str]]) -> list[str]:
    failures: list[str] = []
    for owner_id, field_name, value in fields:
        if not value:
            continue
        if len(value) > LEARNING_REFERENCE_TEXT_LIMIT:
            failures.append(
                f"{owner_id} {field_name} is too long for learning reference metadata"
            )
        if _contains_marker(value, COPIED_PASSAGE_MARKERS):
            failures.append(f"{owner_id} {field_name} contains copied passage")
        if _contains_marker(value, EXTRACTED_MEANING_MARKERS):
            failures.append(f"{owner_id} {field_name} contains extracted meaning")
        if _contains_marker(value, REVIEW_STATE_MARKERS):
            failures.append(f"{owner_id} {field_name} has review-state leakage")
        if _contains_marker(value, PROMOTION_STATE_MARKERS):
            failures.append(f"{owner_id} {field_name} has promotion-state leakage")
        if _contains_marker(value, REPORT_EVIDENCE_MARKERS):
            failures.append(f"{owner_id} {field_name} violates report evidence boundary")
        if _contains_marker(value, ABSOLUTE_OUTCOME_PHRASES):
            failures.append(f"{owner_id} {field_name} contains absolute language")
        if _contains_marker(value, EXACT_DEATH_PHRASES):
            failures.append(f"{owner_id} {field_name} contains exact death language")
        if _contains_marker(value, PROHIBITED_HIGH_RISK_PHRASES):
            failures.append(
                f"{owner_id} {field_name} contains prohibited high-risk wording"
            )
    return failures


def validate_learning_reference_quality(
    data_dir: Path | str | None = None,
) -> list[str]:
    source_dir = _data_dir(data_dir)
    notes = load_learning_reference_notes(source_dir)
    points = load_learning_points(source_dir)
    decisions = load_candidate_intake_decisions(source_dir)
    action_notes = load_prerequisite_action_notes(source_dir)
    receipts = load_downstream_authorization_receipts(source_dir)
    corrected_pilot_evaluations = (
        load_new_material_corrected_pilot_learning_entry_evaluation_items(source_dir)
    )
    corrected_pilot_note_preps = (
        load_new_material_corrected_pilot_learning_note_prep_items(source_dir)
    )
    corrected_pilot_note_drafts = (
        load_new_material_corrected_pilot_learning_note_draft_items(source_dir)
    )
    corrected_pilot_completion_reviews = (
        load_new_material_corrected_pilot_learning_completion_review_items(source_dir)
    )
    return _validate_quality_text(
        [
            *_iter_note_quality_text_fields(notes),
            *_iter_point_quality_text_fields(points),
            *_iter_decision_quality_text_fields(decisions),
            *_iter_action_note_quality_text_fields(action_notes),
            *_iter_downstream_receipt_quality_text_fields(receipts),
            *_iter_corrected_pilot_learning_entry_evaluation_quality_text_fields(
                corrected_pilot_evaluations
            ),
            *_iter_corrected_pilot_learning_note_prep_quality_text_fields(
                corrected_pilot_note_preps
            ),
            *_iter_corrected_pilot_learning_note_draft_quality_text_fields(
                corrected_pilot_note_drafts
            ),
            *_iter_corrected_pilot_learning_completion_review_quality_text_fields(
                corrected_pilot_completion_reviews
            ),
        ]
    )
