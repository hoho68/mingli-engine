"""Deterministic extraction queue intake loading and validation."""

from collections import Counter
import json
from pathlib import Path
from typing import Any

from mingli_engine import materials_audit, source_intake, source_library
from mingli_engine.models import (
    CANDIDATE_DRAFT_SLOT_STATUSES,
    EXTRACTION_PACKAGE_LOCATOR_REQUIREMENTS,
    EXTRACTION_PACKAGE_MANUAL_ACTIONS,
    EXTRACTION_PACKAGE_PRIORITY_LEVELS,
    EXTRACTION_PACKAGE_RISK_BOUNDARIES,
    EXTRACTION_PACKAGE_STATUSES,
    EXTRACTION_TASK_STATUSES,
    PREREQUISITE_BACKLOG_TYPES,
    CandidateDraftSlot,
    ExtractionTask,
    ExtractionWorkPackage,
    PackageProgressSummary,
    PrerequisiteBacklogRecord,
    RULE_FAMILIES,
)


class ExtractionQueueIntakeError(ValueError):
    pass


_DATA_DIR = Path(__file__).resolve().parent / "data" / "extraction_queue_intake"
DURABLE_REASON_MIN_LENGTH = 20
NON_DURABLE_REASON_MARKERS = frozenset({"n/a", "na", "none", "todo", "tbd"})
EXTRACTION_PACKAGE_TEXT_LIMIT = 360
FORBIDDEN_DRAFT_SLOT_FIELDS = frozenset(
    {
        "source_passage",
        "source_passages",
        "copied_source_passage",
        "raw_source_text",
        "extracted_meaning",
        "review_decision",
        "review_status",
        "approval_status",
        "approved_meaning",
        "promotion_status",
        "formal_evidence_id",
    }
)
EXTRACTED_MEANING_MARKERS = (
    "extracted meaning",
    "extracted_meaning",
    "copied source",
    "source passage",
    "copied passage",
)
REVIEW_STATE_MARKERS = (
    "review decision",
    "review status",
    "approval status",
    "approved meaning",
    "promotion status",
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
BACKLOG_TYPES_REQUIRING_MISSING_PREREQUISITES = frozenset(
    {"registration", "preparation", "locator_review", "risk_review"}
)
BACKLOG_TYPES_REQUIRING_DURABLE_REASON = frozenset({"deferred", "blocked"})
ROUTINE_EXTRACTION_BLOCKING_BACKLOG_TYPES = frozenset(
    {"risk_review", "deferred", "blocked"}
)
BACKLOG_TYPE_QUEUE_TYPES = {
    "registration": frozenset({"registration_backlog"}),
    "preparation": frozenset({"preparation_backlog"}),
    "locator_review": frozenset({"preparation_backlog"}),
    "risk_review": frozenset({"risk_review_backlog"}),
    "deferred": frozenset({"blocked_backlog"}),
    "blocked": frozenset({"blocked_backlog"}),
}
BACKLOG_TYPE_READINESS_STATES = {
    "registration": frozenset(
        {"needs_source_registration", "needs_identity_clarification"}
    ),
    "preparation": frozenset({"needs_cleaning", "preparation_backlog"}),
    "locator_review": frozenset({"needs_locator_review"}),
    "risk_review": frozenset({"needs_risk_review"}),
    "deferred": frozenset({"deferred"}),
    "blocked": frozenset({"blocked"}),
}
BACKLOG_TYPE_ACTIONS = {
    "registration": frozenset({"register_source", "clarify_identity"}),
    "preparation": frozenset({"prepare_text", "review_cleaned_text"}),
    "locator_review": frozenset({"clarify_identity", "review_cleaned_text"}),
    "risk_review": frozenset({"risk_review"}),
    "deferred": frozenset({"defer"}),
    "blocked": frozenset({"block"}),
}
CANDIDATE_OVERLAP_STATUSES = frozenset(
    {"pending_review", "approved", "rejected", "blocked"}
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
        raise ExtractionQueueIntakeError(
            f"missing data file: {path.name}"
        ) from error

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as error:
        raise ExtractionQueueIntakeError(
            f"invalid JSON in {path.name}: {error}"
        ) from error

    if not isinstance(payload, list):
        raise ExtractionQueueIntakeError(f"{path.name} must contain a JSON array")
    if not all(isinstance(item, dict) for item in payload):
        raise ExtractionQueueIntakeError(
            f"{path.name} entries must be JSON objects"
        )
    return payload


def _ensure_unique(ids: list[str], id_name: str) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise ExtractionQueueIntakeError(f"duplicate {id_name}: {item_id}")
        seen.add(item_id)


def _require_text(value: str, field_name: str, owner_id: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ExtractionQueueIntakeError(f"{owner_id} has empty {field_name}")


def _require_string_list(value: Any, field_name: str, owner_id: str) -> None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ExtractionQueueIntakeError(f"{owner_id} has invalid {field_name}")


def _require_nonempty_string_list(value: Any, field_name: str, owner_id: str) -> None:
    _require_string_list(value, field_name, owner_id)
    if not value:
        raise ExtractionQueueIntakeError(f"{owner_id} requires {field_name}")


def _validate_enum(
    value: str,
    allowed_values: frozenset[str],
    field_name: str,
    owner_id: str,
) -> None:
    if value not in allowed_values:
        raise ExtractionQueueIntakeError(
            f"{owner_id} has invalid {field_name}: {value}"
        )


def _is_durable_reason(value: str) -> bool:
    reason = value.strip()
    if len(reason) < DURABLE_REASON_MIN_LENGTH:
        return False
    return reason.lower() not in NON_DURABLE_REASON_MARKERS


def _normalize_boundary_text(value: str) -> str:
    return value.lower().replace("_", " ").replace("-", " ")


def _contains_marker(value: str, markers: tuple[str, ...]) -> bool:
    normalized = _normalize_boundary_text(value)
    return any(_normalize_boundary_text(marker) in normalized for marker in markers)


def _extraction_work_package_from_dict(
    data: dict[str, Any],
) -> ExtractionWorkPackage:
    try:
        package = ExtractionWorkPackage(**data)
    except TypeError as error:
        raise ExtractionQueueIntakeError(
            f"invalid extraction work package: {error}"
        ) from error

    owner_id = package.package_id or "?"
    for field_name in ("package_id", "package_label", "status"):
        _require_text(getattr(package, field_name), field_name, owner_id)
    for field_name in (
        "source_queue_snapshot_ids",
        "selected_task_ids",
        "backlog_record_ids",
    ):
        _require_string_list(getattr(package, field_name), field_name, owner_id)
    _validate_enum(package.status, EXTRACTION_PACKAGE_STATUSES, "status", owner_id)

    if (
        package.status == "completed"
        and not package.selected_task_ids
        and not package.backlog_record_ids
        and not _is_durable_reason(package.notes)
    ):
        raise ExtractionQueueIntakeError(
            f"{owner_id} completed package requires selected tasks, backlog "
            "records, or durable notes"
        )

    return package


def _extraction_task_from_dict(data: dict[str, Any]) -> ExtractionTask:
    try:
        task = ExtractionTask(**data)
    except TypeError as error:
        raise ExtractionQueueIntakeError(f"invalid extraction task: {error}") from error

    owner_id = task.task_id or "?"
    for field_name in (
        "task_id",
        "package_id",
        "queue_item_id",
        "audit_id",
        "priority_level",
        "priority_rationale",
        "risk_boundary",
        "locator_requirement",
        "source_quality_note",
        "rights_note",
        "recommended_action",
        "status",
    ):
        _require_text(getattr(task, field_name), field_name, owner_id)
    for field_name in (
        "target_rule_families",
        "target_gap_ids",
        "pre_extraction_checks",
        "overlap_warnings",
    ):
        _require_string_list(getattr(task, field_name), field_name, owner_id)
    _validate_enum(
        task.priority_level,
        EXTRACTION_PACKAGE_PRIORITY_LEVELS,
        "priority_level",
        owner_id,
    )
    _validate_enum(
        task.risk_boundary,
        EXTRACTION_PACKAGE_RISK_BOUNDARIES,
        "risk_boundary",
        owner_id,
    )
    _validate_enum(
        task.locator_requirement,
        EXTRACTION_PACKAGE_LOCATOR_REQUIREMENTS,
        "locator_requirement",
        owner_id,
    )
    _validate_enum(
        task.recommended_action,
        EXTRACTION_PACKAGE_MANUAL_ACTIONS,
        "recommended_action",
        owner_id,
    )
    _validate_enum(task.status, EXTRACTION_TASK_STATUSES, "status", owner_id)
    for rule_family in task.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise ExtractionQueueIntakeError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    if not task.target_rule_families and not task.target_gap_ids:
        raise ExtractionQueueIntakeError(f"{owner_id} requires target")
    if not task.pre_extraction_checks:
        raise ExtractionQueueIntakeError(f"{owner_id} requires pre_extraction_checks")
    return task


def _candidate_draft_slot_from_dict(data: dict[str, Any]) -> CandidateDraftSlot:
    owner_id = data.get("draft_slot_id") if isinstance(data.get("draft_slot_id"), str) else "?"
    forbidden_fields = sorted(FORBIDDEN_DRAFT_SLOT_FIELDS.intersection(data))
    if forbidden_fields:
        raise ExtractionQueueIntakeError(
            f"{owner_id} has forbidden draft slot field: {forbidden_fields[0]}"
        )

    try:
        slot = CandidateDraftSlot(**data)
    except TypeError as error:
        raise ExtractionQueueIntakeError(
            f"invalid candidate draft slot: {error}"
        ) from error

    owner_id = slot.draft_slot_id or "?"
    for field_name in (
        "draft_slot_id",
        "task_id",
        "intended_candidate_label",
        "target_rule_family",
        "locator_requirement",
        "risk_boundary",
        "status",
    ):
        _require_text(getattr(slot, field_name), field_name, owner_id)
    for field_name in ("expected_review_notes", "safety_requirements"):
        _require_nonempty_string_list(getattr(slot, field_name), field_name, owner_id)
    if slot.target_rule_family not in RULE_FAMILIES:
        raise ExtractionQueueIntakeError(
            f"{owner_id} has unsupported target_rule_family: "
            f"{slot.target_rule_family}"
        )
    _validate_enum(
        slot.locator_requirement,
        EXTRACTION_PACKAGE_LOCATOR_REQUIREMENTS,
        "locator_requirement",
        owner_id,
    )
    _validate_enum(
        slot.risk_boundary,
        EXTRACTION_PACKAGE_RISK_BOUNDARIES,
        "risk_boundary",
        owner_id,
    )
    _validate_enum(slot.status, CANDIDATE_DRAFT_SLOT_STATUSES, "status", owner_id)
    if slot.status == "ready_for_manual_extraction":
        _require_text(slot.locator_requirement, "locator_requirement", owner_id)
        _require_nonempty_string_list(
            slot.expected_review_notes,
            "expected_review_notes",
            owner_id,
        )
        _require_nonempty_string_list(
            slot.safety_requirements,
            "safety_requirements",
            owner_id,
        )
    return slot


def _prerequisite_backlog_record_from_dict(
    data: dict[str, Any],
) -> PrerequisiteBacklogRecord:
    try:
        record = PrerequisiteBacklogRecord(**data)
    except TypeError as error:
        raise ExtractionQueueIntakeError(
            f"invalid prerequisite backlog record: {error}"
        ) from error

    owner_id = record.backlog_id or "?"
    for field_name in (
        "backlog_id",
        "package_id",
        "queue_item_id",
        "audit_id",
        "backlog_type",
        "durable_reason",
        "recommended_action",
        "risk_boundary",
        "status",
    ):
        _require_text(getattr(record, field_name), field_name, owner_id)
    _require_string_list(
        record.missing_prerequisites,
        "missing_prerequisites",
        owner_id,
    )
    _validate_enum(record.backlog_type, PREREQUISITE_BACKLOG_TYPES, "backlog_type", owner_id)
    _validate_enum(
        record.recommended_action,
        EXTRACTION_PACKAGE_MANUAL_ACTIONS,
        "recommended_action",
        owner_id,
    )
    _validate_enum(
        record.risk_boundary,
        EXTRACTION_PACKAGE_RISK_BOUNDARIES,
        "risk_boundary",
        owner_id,
    )
    _validate_enum(record.status, EXTRACTION_PACKAGE_STATUSES, "status", owner_id)
    if not record.missing_prerequisites and not _is_durable_reason(
        record.durable_reason
    ):
        raise ExtractionQueueIntakeError(
            f"{owner_id} requires missing_prerequisites or durable_reason"
        )
    if (
        record.backlog_type in BACKLOG_TYPES_REQUIRING_MISSING_PREREQUISITES
        and not record.missing_prerequisites
    ):
        raise ExtractionQueueIntakeError(
            f"{owner_id} requires missing_prerequisites for "
            f"{record.backlog_type} backlog"
        )
    if (
        record.backlog_type in BACKLOG_TYPES_REQUIRING_DURABLE_REASON
        and not _is_durable_reason(record.durable_reason)
    ):
        raise ExtractionQueueIntakeError(
            f"{owner_id} requires durable_reason for {record.backlog_type} backlog"
        )
    return record


def load_extraction_work_packages(
    data_dir: Path | str | None = None,
) -> list[ExtractionWorkPackage]:
    source_dir = _data_dir(data_dir)
    packages = [
        _extraction_work_package_from_dict(item)
        for item in _read_json_list(source_dir / "extraction_work_packages.json")
    ]
    _ensure_unique([package.package_id for package in packages], "package_id")
    return packages


def _load_materials_audit_context(source_dir: Path) -> dict[str, dict[str, Any]]:
    materials_dir = _sibling_data_dir(source_dir, "materials_audit")
    if materials_dir is None:
        return {
            "audit_records": {},
            "queue_items": {},
            "readiness": {},
            "alignments": {},
        }

    try:
        records = materials_audit.load_material_audit_records(materials_dir)
        queue_items = materials_audit.load_extraction_queue_items(materials_dir)
        readiness = materials_audit.load_preparation_readiness_findings(materials_dir)
        alignments = materials_audit.load_source_alignment_findings(materials_dir)
    except materials_audit.MaterialsAuditError as error:
        raise ExtractionQueueIntakeError(
            f"materials-audit data invalid: {error}"
        ) from error

    alignments_by_audit_id: dict[str, list[Any]] = {}
    for alignment in alignments:
        alignments_by_audit_id.setdefault(alignment.audit_id, []).append(alignment)

    return {
        "audit_records": {record.audit_id: record for record in records},
        "queue_items": {item.queue_item_id: item for item in queue_items},
        "readiness": {finding.audit_id: finding for finding in readiness},
        "alignments": alignments_by_audit_id,
    }


def _load_source_library_entries(source_dir: Path) -> dict[str, Any]:
    library_dir = _sibling_data_dir(source_dir, "source_library")
    if library_dir is None:
        return {}
    try:
        entries = source_library.load_source_library_entries(library_dir)
    except source_library.SourceLibraryError as error:
        raise ExtractionQueueIntakeError(
            f"source-library data invalid: {error}"
        ) from error
    return {entry.entry_id: entry for entry in entries}


def _load_source_materials(source_dir: Path) -> dict[str, Any]:
    intake_dir = _sibling_data_dir(source_dir, "source_intake")
    if intake_dir is None:
        return {}
    try:
        materials = source_intake.load_source_materials(intake_dir)
    except source_intake.SourceIntakeError as error:
        raise ExtractionQueueIntakeError(
            f"source-intake data invalid: {error}"
        ) from error
    return {material.material_id: material for material in materials}


def _validate_task_package_links(
    tasks: list[ExtractionTask],
    packages: list[ExtractionWorkPackage],
) -> None:
    packages_by_id = {package.package_id: package for package in packages}
    selected_task_ids = {
        task_id for package in packages for task_id in package.selected_task_ids
    }
    task_ids = {task.task_id for task in tasks}

    for task in tasks:
        package = packages_by_id.get(task.package_id)
        if package is None:
            raise ExtractionQueueIntakeError(
                f"{task.task_id} references unknown package: {task.package_id}"
            )
        if task.task_id not in package.selected_task_ids:
            raise ExtractionQueueIntakeError(
                f"{task.task_id} is not selected by package {package.package_id}"
            )
    for selected_task_id in selected_task_ids:
        if selected_task_id not in task_ids:
            raise ExtractionQueueIntakeError(
                f"package references unknown selected task: {selected_task_id}"
            )


def _validate_task_trace_links(
    task: ExtractionTask,
    *,
    audit_records: dict[str, Any],
    queue_items: dict[str, Any],
    readiness_by_audit_id: dict[str, Any],
    alignments_by_audit_id: dict[str, list[Any]],
    source_entries_by_id: dict[str, Any],
    source_materials_by_id: dict[str, Any],
) -> None:
    if not queue_items:
        return

    queue_item = queue_items.get(task.queue_item_id)
    if queue_item is None:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} references unknown 015 queue item: {task.queue_item_id}"
        )
    if task.audit_id != queue_item.audit_id:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} audit mismatch for {task.queue_item_id}"
        )
    if queue_item.queue_type != "extraction_ready":
        raise ExtractionQueueIntakeError(
            f"{task.task_id} requires extraction_ready queue item"
        )
    if queue_item.recommended_action != "extract_candidates":
        raise ExtractionQueueIntakeError(
            f"{task.task_id} requires extract_candidates queue action"
        )

    record = audit_records.get(task.audit_id)
    if record is None:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} references unknown audit: {task.audit_id}"
        )
    readiness = readiness_by_audit_id.get(task.audit_id)
    if readiness is None:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} requires readiness finding"
        )
    if readiness.readiness_state != "ready_for_extraction_review":
        raise ExtractionQueueIntakeError(
            f"{task.task_id} requires ready_for_extraction_review readiness"
        )
    if readiness.recommended_next_action != "extract_candidates":
        raise ExtractionQueueIntakeError(
            f"{task.task_id} readiness must recommend extract_candidates"
        )

    alignments = alignments_by_audit_id.get(task.audit_id, [])
    ready_alignments = [
        alignment
        for alignment in alignments
        if alignment.match_type in {"exact", "likely"}
        and alignment.source_library_entry_id
    ]
    if not ready_alignments:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} requires source-library alignment"
        )

    alignment_entry_ids = {
        alignment.source_library_entry_id for alignment in ready_alignments
    }
    if not task.source_library_entry_id:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} requires source_library_entry_id"
        )
    if task.source_library_entry_id not in alignment_entry_ids:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} source_library_entry_id does not match 015 alignment"
        )
    if (
        record.source_library_entry_id
        and task.source_library_entry_id != record.source_library_entry_id
    ):
        raise ExtractionQueueIntakeError(
            f"{task.task_id} source_library_entry_id does not match audit record"
        )
    if (
        source_entries_by_id
        and task.source_library_entry_id not in source_entries_by_id
    ):
        raise ExtractionQueueIntakeError(
            f"{task.task_id} references unknown source-library entry: "
            f"{task.source_library_entry_id}"
        )

    alignment_material_ids = {
        alignment.source_material_id
        for alignment in ready_alignments
        if alignment.source_material_id
    }
    if alignment_material_ids and not task.intended_source_material_id:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} requires intended_source_material_id"
        )
    if (
        task.intended_source_material_id
        and alignment_material_ids
        and task.intended_source_material_id not in alignment_material_ids
    ):
        raise ExtractionQueueIntakeError(
            f"{task.task_id} intended_source_material_id does not match 015 alignment"
        )
    if (
        source_materials_by_id
        and task.intended_source_material_id
        and task.intended_source_material_id not in source_materials_by_id
    ):
        raise ExtractionQueueIntakeError(
            f"{task.task_id} references unknown source material: "
            f"{task.intended_source_material_id}"
        )

    if task.risk_boundary != queue_item.risk_boundary:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} risk_boundary does not match queue item"
        )
    if task.risk_boundary != readiness.risk_boundary:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} risk_boundary does not match readiness finding"
        )
    if task.priority_level != queue_item.priority_level:
        raise ExtractionQueueIntakeError(
            f"{task.task_id} priority_level does not match queue item"
        )
    if not set(task.target_rule_families).issubset(set(queue_item.target_rule_families)):
        raise ExtractionQueueIntakeError(
            f"{task.task_id} target_rule_families exceed 015 queue targets"
        )
    if not set(task.target_gap_ids).issubset(set(queue_item.target_gap_ids)):
        raise ExtractionQueueIntakeError(
            f"{task.task_id} target_gap_ids exceed 015 queue targets"
        )
    for check in queue_item.pre_extraction_checks:
        if check not in task.pre_extraction_checks:
            raise ExtractionQueueIntakeError(
                f"{task.task_id} missing 015 pre_extraction_checks"
            )


def _validate_draft_slot_task_links(
    slots: list[CandidateDraftSlot],
    tasks: list[ExtractionTask],
) -> None:
    tasks_by_id = {task.task_id: task for task in tasks}
    for slot in slots:
        task = tasks_by_id.get(slot.task_id)
        if task is None:
            raise ExtractionQueueIntakeError(
                f"{slot.draft_slot_id} references unknown extraction task: "
                f"{slot.task_id}"
            )
        if slot.risk_boundary != task.risk_boundary:
            raise ExtractionQueueIntakeError(
                f"{slot.draft_slot_id} risk_boundary does not match parent task"
            )
        if (
            task.target_rule_families
            and slot.target_rule_family not in task.target_rule_families
        ):
            raise ExtractionQueueIntakeError(
                f"{slot.draft_slot_id} target_rule_family is not in parent task"
            )
        if slot.target_gap_id and slot.target_gap_id not in task.target_gap_ids:
            raise ExtractionQueueIntakeError(
                f"{slot.draft_slot_id} target_gap_id is not in parent task"
            )
        if slot.status == "ready_for_manual_extraction" and not task.pre_extraction_checks:
            raise ExtractionQueueIntakeError(
                f"{slot.draft_slot_id} requires parent task pre_extraction_checks"
            )

        safety_text = " ".join(slot.safety_requirements).lower()
        if slot.risk_boundary in {"sensitive", "high_risk"}:
            if "uncertainty" not in safety_text:
                raise ExtractionQueueIntakeError(
                    f"{slot.draft_slot_id} sensitive slot requires uncertainty "
                    "safety requirement"
                )
            if "limitation" not in safety_text:
                raise ExtractionQueueIntakeError(
                    f"{slot.draft_slot_id} sensitive slot requires limitation "
                    "safety requirement"
                )
        if slot.risk_boundary == "high_risk" and (
            "risk-review" not in safety_text and "risk review" not in safety_text
        ):
            raise ExtractionQueueIntakeError(
                f"{slot.draft_slot_id} high_risk slot requires risk-review "
                "safety requirement"
            )


def _validate_backlog_package_links(
    records: list[PrerequisiteBacklogRecord],
    packages: list[ExtractionWorkPackage],
) -> None:
    packages_by_id = {package.package_id: package for package in packages}
    records_by_id = {record.backlog_id: record for record in records}
    package_backlog_ids = {
        backlog_id for package in packages for backlog_id in package.backlog_record_ids
    }

    for record in records:
        package = packages_by_id.get(record.package_id)
        if package is None:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} references unknown package: "
                f"{record.package_id}"
            )
        if record.backlog_id not in package.backlog_record_ids:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} is not listed by package "
                f"{package.package_id}"
            )

    for backlog_id in package_backlog_ids:
        if backlog_id not in records_by_id:
            raise ExtractionQueueIntakeError(
                f"package references unknown backlog record: {backlog_id}"
            )


def _validate_backlog_trace_and_routing(
    records: list[PrerequisiteBacklogRecord],
    packages: list[ExtractionWorkPackage],
    tasks: list[ExtractionTask],
    *,
    audit_records: dict[str, Any],
    queue_items: dict[str, Any],
    readiness_by_audit_id: dict[str, Any],
) -> None:
    if not audit_records and not queue_items:
        return

    packages_by_id = {package.package_id: package for package in packages}
    tasks_by_queue_id = {task.queue_item_id: task for task in tasks}

    for record in records:
        if record.queue_item_id in tasks_by_queue_id:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} cannot also be scheduled as routine "
                "extraction task"
            )

        queue_item = queue_items.get(record.queue_item_id)
        if queue_item is None:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} references unknown 015 queue item: "
                f"{record.queue_item_id}"
            )
        if record.audit_id != queue_item.audit_id:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} audit mismatch for {record.queue_item_id}"
            )
        if record.audit_id not in audit_records:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} references unknown audit: {record.audit_id}"
            )

        package = packages_by_id[record.package_id]
        if record.queue_item_id not in package.source_queue_snapshot_ids:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} queue item is missing from source queue "
                f"snapshot for {package.package_id}"
            )

        readiness = readiness_by_audit_id.get(record.audit_id)
        if readiness is None:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} requires readiness finding"
            )

        allowed_queue_types = BACKLOG_TYPE_QUEUE_TYPES[record.backlog_type]
        if queue_item.queue_type not in allowed_queue_types:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} {record.backlog_type} backlog requires "
                f"queue_type {sorted(allowed_queue_types)}"
            )
        allowed_readiness_states = BACKLOG_TYPE_READINESS_STATES[record.backlog_type]
        if readiness.readiness_state not in allowed_readiness_states:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} {record.backlog_type} backlog requires "
                f"readiness {sorted(allowed_readiness_states)}"
            )
        allowed_actions = BACKLOG_TYPE_ACTIONS[record.backlog_type]
        if record.recommended_action not in allowed_actions:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} {record.backlog_type} backlog requires "
                f"recommended_action {sorted(allowed_actions)}"
            )
        if queue_item.recommended_action != record.recommended_action:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} recommended_action does not match 015 "
                "queue item"
            )
        if readiness.recommended_next_action != record.recommended_action:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} recommended_action does not match "
                "readiness finding"
            )
        if record.risk_boundary != queue_item.risk_boundary:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} risk_boundary does not match queue item"
            )
        if record.risk_boundary != readiness.risk_boundary:
            raise ExtractionQueueIntakeError(
                f"{record.backlog_id} risk_boundary does not match readiness "
                "finding"
            )


def _load_candidate_extracts(source_dir: Path) -> list[Any]:
    intake_dir = _sibling_data_dir(source_dir, "source_intake")
    if intake_dir is None:
        return []
    try:
        return source_intake.load_candidate_extracts(intake_dir)
    except source_intake.SourceIntakeError as error:
        raise ExtractionQueueIntakeError(
            f"source-intake candidate data invalid: {error}"
        ) from error


def _detect_task_candidate_overlaps(
    tasks: list[ExtractionTask],
    source_dir: Path,
) -> dict[str, list[tuple[str, str, str]]]:
    candidates = _load_candidate_extracts(source_dir)
    overlaps: dict[str, list[tuple[str, str, str]]] = {}
    for task in tasks:
        if not task.intended_source_material_id:
            continue
        task_rule_families = set(task.target_rule_families)
        task_gap_ids = set(task.target_gap_ids)
        for candidate in candidates:
            if candidate.status not in CANDIDATE_OVERLAP_STATUSES:
                continue
            if candidate.material_id != task.intended_source_material_id:
                continue
            rule_overlaps = (
                candidate.proposed_rule_family
                and candidate.proposed_rule_family in task_rule_families
            )
            gap_overlaps = bool(task_gap_ids.intersection(candidate.related_gap_ids))
            if not rule_overlaps and not gap_overlaps:
                continue
            warning = (
                f"013 candidate overlap {candidate.candidate_id} "
                f"({candidate.status})"
            )
            overlaps.setdefault(task.task_id, []).append(
                (candidate.candidate_id, candidate.status, warning)
            )
    return overlaps


def _count_overlap_warnings(
    tasks: list[ExtractionTask],
    source_dir: Path,
) -> int:
    detected_count = sum(
        len(warnings)
        for warnings in _detect_task_candidate_overlaps(tasks, source_dir).values()
    )
    stored_count = sum(len(task.overlap_warnings) for task in tasks)
    return max(stored_count, detected_count)


def _validate_stored_overlap_warnings(
    tasks: list[ExtractionTask],
    source_dir: Path,
) -> list[str]:
    failures: list[str] = []
    tasks_by_id = {task.task_id: task for task in tasks}
    for task_id, overlaps in _detect_task_candidate_overlaps(tasks, source_dir).items():
        warning_text = " ".join(tasks_by_id[task_id].overlap_warnings)
        for candidate_id, _, _ in overlaps:
            if candidate_id not in warning_text:
                failures.append(
                    f"{task_id} missing overlap warning for 013 candidate "
                    f"{candidate_id}"
                )
    return failures


def load_extraction_tasks(
    data_dir: Path | str | None = None,
) -> list[ExtractionTask]:
    source_dir = _data_dir(data_dir)
    tasks = [
        _extraction_task_from_dict(item)
        for item in _read_json_list(source_dir / "extraction_tasks.json")
    ]
    _ensure_unique([task.task_id for task in tasks], "task_id")

    packages = load_extraction_work_packages(source_dir)
    _validate_task_package_links(tasks, packages)

    context = _load_materials_audit_context(source_dir)
    source_entries_by_id = _load_source_library_entries(source_dir)
    source_materials_by_id = _load_source_materials(source_dir)
    for task in tasks:
        _validate_task_trace_links(
            task,
            audit_records=context["audit_records"],
            queue_items=context["queue_items"],
            readiness_by_audit_id=context["readiness"],
            alignments_by_audit_id=context["alignments"],
            source_entries_by_id=source_entries_by_id,
            source_materials_by_id=source_materials_by_id,
        )
    return tasks


def load_candidate_draft_slots(
    data_dir: Path | str | None = None,
) -> list[CandidateDraftSlot]:
    source_dir = _data_dir(data_dir)
    slots = [
        _candidate_draft_slot_from_dict(item)
        for item in _read_json_list(source_dir / "candidate_draft_slots.json")
    ]
    _ensure_unique([slot.draft_slot_id for slot in slots], "draft_slot_id")
    tasks = load_extraction_tasks(source_dir)
    _validate_draft_slot_task_links(slots, tasks)
    return slots


def load_prerequisite_backlog_records(
    data_dir: Path | str | None = None,
) -> list[PrerequisiteBacklogRecord]:
    source_dir = _data_dir(data_dir)
    records = [
        _prerequisite_backlog_record_from_dict(item)
        for item in _read_json_list(source_dir / "prerequisite_backlog_records.json")
    ]
    _ensure_unique([record.backlog_id for record in records], "backlog_id")
    packages = load_extraction_work_packages(source_dir)
    _validate_backlog_package_links(records, packages)
    tasks = load_extraction_tasks(source_dir)
    context = _load_materials_audit_context(source_dir)
    _validate_backlog_trace_and_routing(
        records,
        packages,
        tasks,
        audit_records=context["audit_records"],
        queue_items=context["queue_items"],
        readiness_by_audit_id=context["readiness"],
    )
    return records


def build_package_progress_summary(
    data_dir: Path | str | None = None,
) -> PackageProgressSummary:
    source_dir = _data_dir(data_dir)
    packages = load_extraction_work_packages(source_dir)
    tasks = load_extraction_tasks(source_dir)
    draft_slots = load_candidate_draft_slots(source_dir)
    backlog_records = load_prerequisite_backlog_records(source_dir)

    package_counts = Counter(package.status for package in packages)
    task_counts = Counter(task.status for task in tasks)
    priority_counts = Counter(task.priority_level for task in tasks)
    draft_slot_counts = Counter(slot.status for slot in draft_slots)
    draft_slot_rule_family_counts = Counter(
        slot.target_rule_family for slot in draft_slots
    )
    draft_slot_readiness_counts = Counter(
        "ready" if slot.status == "ready_for_manual_extraction" else slot.status
        for slot in draft_slots
    )
    backlog_counts = Counter(record.backlog_type for record in backlog_records)
    backlog_counts.update(f"status:{record.status}" for record in backlog_records)

    risk_boundary_counts = Counter(task.risk_boundary for task in tasks)
    risk_boundary_counts.update(slot.risk_boundary for slot in draft_slots)
    risk_boundary_counts.update(record.risk_boundary for record in backlog_records)

    blocked_or_deferred_count = sum(
        1
        for item in [*packages, *tasks, *draft_slots, *backlog_records]
        if item.status in {"blocked", "deferred"}
    )
    next_manual_action_ids = [
        task.task_id for task in tasks if task.status in {"planned", "active"}
    ]
    next_manual_action_ids.extend(
        record.backlog_id
        for record in backlog_records
        if record.status in {"planned", "active"}
    )
    selected_source_queue_ids = [
        queue_item_id
        for package in packages
        for queue_item_id in package.source_queue_snapshot_ids
    ]

    return PackageProgressSummary(
        package_counts=dict(package_counts),
        task_counts=dict(task_counts),
        draft_slot_counts=dict(draft_slot_counts),
        backlog_counts=dict(backlog_counts),
        risk_boundary_counts=dict(risk_boundary_counts),
        overlap_warning_count=_count_overlap_warnings(tasks, source_dir),
        extraction_task_count=len(tasks),
        candidate_draft_slot_count=len(draft_slots),
        blocked_or_deferred_count=blocked_or_deferred_count,
        next_manual_action_ids=next_manual_action_ids,
        priority_counts=dict(priority_counts),
        selected_source_queue_ids=selected_source_queue_ids,
        draft_slot_rule_family_counts=dict(draft_slot_rule_family_counts),
        draft_slot_readiness_counts=dict(draft_slot_readiness_counts),
    )


def _iter_quality_text_fields(
    packages: list[ExtractionWorkPackage],
    tasks: list[ExtractionTask],
    draft_slots: list[CandidateDraftSlot],
    backlog_records: list[PrerequisiteBacklogRecord],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for package in packages:
        fields.extend(
            (
                (package.package_id, "package_label", package.package_label),
                (package.package_id, "notes", package.notes),
            )
        )
    for task in tasks:
        fields.extend(
            (
                (task.task_id, "priority_rationale", task.priority_rationale),
                (task.task_id, "source_quality_note", task.source_quality_note),
                (task.task_id, "rights_note", task.rights_note),
            )
        )
        fields.extend(
            (task.task_id, "pre_extraction_checks", item)
            for item in task.pre_extraction_checks
        )
        fields.extend(
            (task.task_id, "overlap_warnings", item)
            for item in task.overlap_warnings
        )
    for slot in draft_slots:
        fields.extend(
            (
                (
                    slot.draft_slot_id,
                    "intended_candidate_label",
                    slot.intended_candidate_label,
                ),
                (slot.draft_slot_id, "target_gap_id", slot.target_gap_id),
            )
        )
        fields.extend(
            (slot.draft_slot_id, "expected_review_notes", item)
            for item in slot.expected_review_notes
        )
        fields.extend(
            (slot.draft_slot_id, "safety_requirements", item)
            for item in slot.safety_requirements
        )
    for record in backlog_records:
        fields.extend(
            (
                (record.backlog_id, "durable_reason", record.durable_reason),
                (record.backlog_id, "recommended_action", record.recommended_action),
            )
        )
        fields.extend(
            (record.backlog_id, "missing_prerequisites", item)
            for item in record.missing_prerequisites
        )
    return fields


def _validate_quality_text(
    fields: list[tuple[str, str, str]],
) -> list[str]:
    failures: list[str] = []
    for owner_id, field_name, value in fields:
        if not value:
            continue
        if len(value) > EXTRACTION_PACKAGE_TEXT_LIMIT:
            failures.append(
                f"{owner_id} {field_name} is too long for extraction package metadata"
            )
        if _contains_marker(value, EXTRACTED_MEANING_MARKERS):
            failures.append(f"{owner_id} {field_name} contains extracted meaning")
        if _contains_marker(value, REVIEW_STATE_MARKERS):
            failures.append(f"{owner_id} {field_name} has review-state leakage")
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


def validate_extraction_package_quality(
    data_dir: Path | str | None = None,
) -> list[str]:
    source_dir = _data_dir(data_dir)
    packages = load_extraction_work_packages(source_dir)
    tasks = load_extraction_tasks(source_dir)
    draft_slots = load_candidate_draft_slots(source_dir)
    backlog_records = load_prerequisite_backlog_records(source_dir)
    failures = _validate_quality_text(
        _iter_quality_text_fields(packages, tasks, draft_slots, backlog_records)
    )
    failures.extend(_validate_stored_overlap_warnings(tasks, source_dir))
    return failures
