"""Deterministic learning reference curation loading and validation."""

from collections import Counter
import json
from pathlib import Path
import re
from typing import Any

from mingli_engine import (
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
    LearningPoint,
    LearningReferenceNote,
    LearningReferenceProgressSummary,
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
    return _validate_quality_text(
        [
            *_iter_note_quality_text_fields(notes),
            *_iter_point_quality_text_fields(points),
            *_iter_decision_quality_text_fields(decisions),
            *_iter_action_note_quality_text_fields(action_notes),
        ]
    )
