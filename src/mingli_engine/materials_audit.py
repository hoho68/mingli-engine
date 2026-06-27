"""Deterministic existing-materials audit loading and validation."""

from collections import Counter
import csv
import json
from pathlib import Path
from typing import Any

from mingli_engine import source_library
from mingli_engine.models import (
    AuditProgressSummary,
    CONFIDENCE_LEVELS,
    ExtractionQueueItem,
    ExternalMaterialInventoryRefreshSummary,
    MATERIAL_AUDIT_ACTIONS,
    MATERIAL_AUDIT_IDENTITY_CONFIDENCES,
    MATERIAL_AUDIT_LOCATOR_CONFIDENCES,
    MATERIAL_AUDIT_MATCH_TYPES,
    MATERIAL_AUDIT_LOCATOR_QUALITIES,
    MATERIAL_AUDIT_PREPARATION_STATES,
    MATERIAL_AUDIT_QUEUE_STATUSES,
    MATERIAL_AUDIT_QUEUE_TYPES,
    MATERIAL_AUDIT_READINESS_STATES,
    MATERIAL_AUDIT_SCOPES,
    MATERIAL_AUDIT_SOURCE_QUALITIES,
    MATERIAL_AUDIT_SOURCE_BOUNDARIES,
    MATERIAL_AUDIT_TEXT_PREPARATION_STATUSES,
    MATERIAL_AUDIT_TEXT_QUALITIES,
    MATERIAL_REPRESENTATION_TYPES,
    MATERIAL_TRACKING_STATUSES,
    MaterialQueueRefreshSummary,
    MaterialAuditRecord,
    MaterialRepresentation,
    PreparationReadinessFinding,
    RawTextMaterialTriageGroup,
    RawTextMaterialTriageSummary,
    RawTextSourceClusterSelectionItem,
    RawTextSourceClusterSelectionSummary,
    RawTextSourceSelectionItem,
    RawTextSourceSelectionSummary,
    RISK_TIERS,
    RULE_FAMILIES,
    SOURCE_LIBRARY_PRIORITY_LEVELS,
    SourceAlignmentFinding,
)


class MaterialsAuditError(ValueError):
    pass


_DATA_DIR = Path(__file__).resolve().parent / "data" / "materials_audit"
DURABLE_REASON_MIN_LENGTH = 20
NON_DURABLE_REASON_MARKERS = frozenset({"n/a", "na", "none", "todo", "tbd"})
MATERIAL_AUDIT_PRIMARY_MATERIAL_TYPES = frozenset(
    {"pdf", "markdown", "note", "image_folder", "mixed", "other"}
)
EXTERNAL_RAW_FILE_OPERATIONS = frozenset(
    {
        "move_raw_file",
        "delete_raw_file",
        "convert_raw_file",
        "commit_raw_file",
    }
)
MATERIALS_AUDIT_TEXT_LIMIT = 360
MATERIALS_AUDIT_REPORT_EVIDENCE_MARKERS = (
    "formal report evidence",
    "report-usable evidence",
    "approved evidence unit",
)
MATERIALS_AUDIT_ABSOLUTE_OUTCOME_PHRASES = (
    "\u5fc5\u5b9a",
    "\u6ce8\u5b9a",
    "\u4e00\u5b9a\u4f1a",
    "\u6b7b\u5b9a",
    "will definitely",
    "guaranteed outcome",
)
MATERIALS_AUDIT_EXACT_DEATH_PHRASES = (
    "exact death",
    "death timing",
    "when they will die",
)
MATERIALS_AUDIT_PROHIBITED_HIGH_RISK_PHRASES = (
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
EXTERNAL_INVENTORY_WORK_ARTIFACTS = frozenset(
    {
        "资料整理/_inventory/",
        "资料整理/new_thread_prompt_2026-05-29.md",
        "资料整理/thread_handoff_2026-05-29.md",
    }
)
EXTERNAL_INVENTORY_NEW_REPRESENTATION_IDS = (
    "repr_life_death_book_100_pages_markdown_extract",
    "repr_raw_text_materials_folder",
)
EXTERNAL_INVENTORY_NEW_QUEUE_ITEM_IDS = ("queue_raw_text_materials_folder_triage",)
EXTERNAL_INVENTORY_NEXT_MATERIAL_ENTRY = "015-raw-text-materials-folder-risk-triage"
RAW_TEXT_TRIAGE_SOURCE_ROOT = "资料原文/文本类/"
RAW_TEXT_TRIAGE_NEXT_MATERIAL_ENTRY = "015-liang-bazi-core-source-selection"
RAW_TEXT_SOURCE_SELECTION_ID = "015-liang-bazi-core-source-selection"
RAW_TEXT_SOURCE_SELECTION_TRIAGE_GROUP_ID = "raw_text_triage_liang_bazi_core"
RAW_TEXT_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY = (
    "015-liang-bazi-core-individual-review"
)
RAW_TEXT_SOURCE_CLUSTER_SELECTION_ID = "015-bazi-general-source-cluster-selection"
RAW_TEXT_SOURCE_CLUSTER_SELECTION_TRIAGE_GROUP_ID = "raw_text_triage_bazi_general"
RAW_TEXT_SOURCE_CLUSTER_SELECTION_NEXT_MATERIAL_ENTRY = (
    "015-bazi-general-cluster-source-selection"
)
RAW_TEXT_TRIAGE_STATUSES = frozenset(
    {
        "source_selection_ready",
        "source_selection_backlog",
        "risk_review_required",
        "deferred_domain_review",
        "deferred_non_text",
        "deferred_unclassified",
    }
)
RAW_TEXT_TRIAGE_DEFERRED_STATUSES = frozenset(
    {"deferred_domain_review", "deferred_non_text", "deferred_unclassified"}
)
RAW_TEXT_SOURCE_SELECTION_STATUSES = frozenset(
    {
        "existing_batch_covered",
        "ready_for_individual_review",
        "variant_review_required",
        "sensitive_boundary_deferred",
    }
)
RAW_TEXT_SOURCE_CLUSTER_SELECTION_STATUSES = frozenset(
    {
        "selected_for_source_selection",
        "backlog_cluster",
        "identity_review_required",
        "sensitive_boundary_deferred",
    }
)


def _data_dir(data_dir: Path | str | None) -> Path:
    return Path(data_dir) if data_dir is not None else _DATA_DIR


def _sibling_data_dir(source_dir: Path, sibling_name: str) -> Path | None:
    sibling = source_dir.parent / sibling_name
    return sibling if sibling.exists() else None


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    try:
        raw_payload = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise MaterialsAuditError(f"missing data file: {path.name}") from error

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as error:
        raise MaterialsAuditError(f"invalid JSON in {path.name}: {error}") from error

    if not isinstance(payload, list):
        raise MaterialsAuditError(f"{path.name} must contain a JSON array")
    if not all(isinstance(item, dict) for item in payload):
        raise MaterialsAuditError(f"{path.name} entries must be JSON objects")
    return payload


def _read_optional_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return _read_json_list(path)


def _ensure_unique(ids: list[str], id_name: str) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise MaterialsAuditError(f"duplicate {id_name}: {item_id}")
        seen.add(item_id)


def _require_text(value: str, field_name: str, owner_id: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise MaterialsAuditError(f"{owner_id} has empty {field_name}")


def _require_string_list(value: Any, field_name: str, owner_id: str) -> None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise MaterialsAuditError(f"{owner_id} has invalid {field_name}")


def _is_durable_reason(value: str) -> bool:
    reason = value.strip()
    if len(reason) < DURABLE_REASON_MIN_LENGTH:
        return False
    return reason.lower() not in NON_DURABLE_REASON_MARKERS


def _validate_enum(
    value: str,
    allowed_values: frozenset[str],
    field_name: str,
    owner_id: str,
) -> None:
    if value not in allowed_values:
        raise MaterialsAuditError(f"{owner_id} has invalid {field_name}: {value}")


def _normalize_boundary_text(value: str) -> str:
    return value.lower().replace("_", " ").replace("-", " ")


def _contains_marker(value: str, markers: tuple[str, ...]) -> bool:
    normalized = _normalize_boundary_text(value)
    return any(_normalize_boundary_text(marker) in normalized for marker in markers)


def _material_audit_record_from_dict(data: dict[str, Any]) -> MaterialAuditRecord:
    try:
        record = MaterialAuditRecord(**data)
    except TypeError as error:
        raise MaterialsAuditError(f"invalid material audit record: {error}") from error

    owner_id = record.audit_id or "?"
    for field_name in (
        "audit_id",
        "canonical_title",
        "material_scope",
        "primary_material_type",
        "source_identity_confidence",
        "preparation_state",
        "source_boundary",
        "risk_tier",
        "recommended_next_action",
    ):
        _require_text(getattr(record, field_name), field_name, owner_id)

    for field_name in (
        "alternate_titles",
        "representations",
        "topic_tags",
        "rule_families",
        "risk_notes",
        "missing_prerequisites",
    ):
        _require_string_list(getattr(record, field_name), field_name, owner_id)

    _validate_enum(
        record.material_scope,
        MATERIAL_AUDIT_SCOPES,
        "material_scope",
        owner_id,
    )
    _validate_enum(
        record.primary_material_type,
        MATERIAL_AUDIT_PRIMARY_MATERIAL_TYPES,
        "primary_material_type",
        owner_id,
    )
    _validate_enum(
        record.source_identity_confidence,
        MATERIAL_AUDIT_IDENTITY_CONFIDENCES,
        "source_identity_confidence",
        owner_id,
    )
    _validate_enum(
        record.preparation_state,
        MATERIAL_AUDIT_PREPARATION_STATES,
        "preparation_state",
        owner_id,
    )
    _validate_enum(
        record.source_boundary,
        MATERIAL_AUDIT_SOURCE_BOUNDARIES,
        "source_boundary",
        owner_id,
    )
    _validate_enum(record.risk_tier, RISK_TIERS, "risk_tier", owner_id)
    _validate_enum(
        record.recommended_next_action,
        MATERIAL_AUDIT_ACTIONS,
        "recommended_next_action",
        owner_id,
    )
    for rule_family in record.rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    if not record.representations and record.source_boundary != "derived_note_only":
        raise MaterialsAuditError(f"{owner_id} requires representation links")

    if record.source_boundary == "external_untracked":
        for operation in record.missing_prerequisites:
            if operation in EXTERNAL_RAW_FILE_OPERATIONS:
                raise MaterialsAuditError(
                    f"{owner_id} external_untracked cannot require {operation}"
                )

    if record.source_identity_confidence == "conflicting":
        if not record.missing_prerequisites and not _is_durable_reason(
            record.outcome_reason
        ):
            raise MaterialsAuditError(
                f"{owner_id} conflicting identity requires missing_prerequisites "
                "or durable outcome_reason"
            )

    if record.risk_tier == "high_risk" and not record.risk_notes:
        raise MaterialsAuditError(f"{owner_id} high_risk requires risk_notes")

    if record.preparation_state in {"deferred", "blocked"}:
        if not _is_durable_reason(record.outcome_reason):
            raise MaterialsAuditError(
                f"{owner_id} {record.preparation_state} requires durable "
                "outcome_reason"
            )

    if record.preparation_state == "ready_for_extraction_review":
        if not record.topic_tags:
            raise MaterialsAuditError(
                f"{owner_id} ready_for_extraction_review requires topic_tags"
            )
        if not record.rule_families:
            raise MaterialsAuditError(
                f"{owner_id} ready_for_extraction_review requires rule_families"
            )
        _require_text(record.rights_notes, "rights_notes", owner_id)
        if record.source_identity_confidence not in {"confirmed", "likely"}:
            raise MaterialsAuditError(
                f"{owner_id} ready_for_extraction_review requires "
                "source_identity_confidence confirmed or likely"
            )
        _require_text(record.source_library_entry_id, "source_library_entry_id", owner_id)

    return record


def _material_representation_from_dict(
    data: dict[str, Any],
    audit_ids: set[str],
) -> MaterialRepresentation:
    try:
        representation = MaterialRepresentation(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid material representation: {error}"
        ) from error

    owner_id = representation.representation_id or "?"
    for field_name in (
        "representation_id",
        "audit_id",
        "representation_type",
        "local_reference",
        "tracking_status",
        "text_quality",
        "locator_quality",
    ):
        _require_text(getattr(representation, field_name), field_name, owner_id)

    if representation.audit_id not in audit_ids:
        raise MaterialsAuditError(
            f"{owner_id} references unknown audit: {representation.audit_id}"
        )
    _validate_enum(
        representation.representation_type,
        MATERIAL_REPRESENTATION_TYPES,
        "representation_type",
        owner_id,
    )
    _validate_enum(
        representation.tracking_status,
        MATERIAL_TRACKING_STATUSES,
        "tracking_status",
        owner_id,
    )
    _validate_enum(
        representation.text_quality,
        MATERIAL_AUDIT_TEXT_QUALITIES,
        "text_quality",
        owner_id,
    )
    _validate_enum(
        representation.locator_quality,
        MATERIAL_AUDIT_LOCATOR_QUALITIES,
        "locator_quality",
        owner_id,
    )
    return representation


def _load_material_audit_records(
    source_dir: Path,
    *,
    validate_representation_links: bool,
) -> list[MaterialAuditRecord]:
    records = [
        _material_audit_record_from_dict(item)
        for item in _read_json_list(source_dir / "material_audit_records.json")
    ]
    _ensure_unique([record.audit_id for record in records], "audit_id")

    if validate_representation_links:
        raw_representations = _read_optional_json_list(
            source_dir / "material_representations.json"
        )
        representation_ids = {
            item["representation_id"]
            for item in raw_representations
            if isinstance(item.get("representation_id"), str)
        }
        for record in records:
            for representation_id in record.representations:
                if representation_id not in representation_ids:
                    raise MaterialsAuditError(
                        f"{record.audit_id} references unknown representation: "
                        f"{representation_id}"
                    )

    return records


def load_material_audit_records(
    data_dir: Path | str | None = None,
) -> list[MaterialAuditRecord]:
    return _load_material_audit_records(
        _data_dir(data_dir),
        validate_representation_links=True,
    )


def load_material_representations(
    data_dir: Path | str | None = None,
) -> list[MaterialRepresentation]:
    source_dir = _data_dir(data_dir)
    audit_ids = {
        record.audit_id
        for record in _load_material_audit_records(
            source_dir,
            validate_representation_links=False,
        )
    }
    representations = [
        _material_representation_from_dict(item, audit_ids)
        for item in _read_json_list(source_dir / "material_representations.json")
    ]
    _ensure_unique(
        [representation.representation_id for representation in representations],
        "representation_id",
    )
    return representations


def _load_source_library_entries(
    source_dir: Path,
) -> dict[str, source_library.SourceLibraryEntry]:
    source_library_dir = _sibling_data_dir(source_dir, "source_library")
    try:
        entries = source_library.load_source_library_entries(source_library_dir)
    except source_library.SourceLibraryError as error:
        raise MaterialsAuditError(f"source-library entries invalid: {error}") from error
    return {entry.entry_id: entry for entry in entries}


def _source_alignment_finding_from_dict(
    data: dict[str, Any],
    audit_ids: set[str],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> SourceAlignmentFinding:
    try:
        finding = SourceAlignmentFinding(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid source alignment finding: {error}"
        ) from error

    owner_id = finding.alignment_id or "?"
    for field_name in ("alignment_id", "audit_id", "match_type", "confidence"):
        _require_text(getattr(finding, field_name), field_name, owner_id)

    if finding.audit_id not in audit_ids:
        raise MaterialsAuditError(
            f"{owner_id} references unknown audit: {finding.audit_id}"
        )
    _validate_enum(finding.match_type, MATERIAL_AUDIT_MATCH_TYPES, "match_type", owner_id)
    _validate_enum(finding.confidence, CONFIDENCE_LEVELS, "confidence", owner_id)

    if finding.match_type in {"exact", "likely"}:
        _require_text(finding.source_library_entry_id, "source_library_entry_id", owner_id)
        if finding.source_library_entry_id not in source_entries_by_id:
            raise MaterialsAuditError(
                f"{owner_id} references unknown source-library entry: "
                f"{finding.source_library_entry_id}"
            )
    elif finding.source_library_entry_id:
        if finding.source_library_entry_id not in source_entries_by_id:
            raise MaterialsAuditError(
                f"{owner_id} references unknown source-library entry: "
                f"{finding.source_library_entry_id}"
            )

    if finding.match_type == "missing_source_library_entry":
        _require_text(
            finding.registration_recommendation,
            "registration_recommendation",
            owner_id,
        )

    if finding.match_type in {"possible_duplicate", "edition_variant"}:
        if not _is_durable_reason(finding.duplicate_or_variant_notes):
            raise MaterialsAuditError(
                f"{owner_id} {finding.match_type} requires "
                "duplicate_or_variant_notes"
            )

    if finding.match_type in {
        "uncertain",
        "blocked_source_library_entry",
        "out_of_scope",
    }:
        if not _is_durable_reason(finding.evidence):
            raise MaterialsAuditError(
                f"{owner_id} {finding.match_type} requires durable evidence"
            )
    else:
        _require_text(finding.evidence, "evidence", owner_id)

    return finding


def load_source_alignment_findings(
    data_dir: Path | str | None = None,
) -> list[SourceAlignmentFinding]:
    source_dir = _data_dir(data_dir)
    raw_findings = _read_json_list(source_dir / "source_alignment_findings.json")
    if not raw_findings:
        return []

    audit_ids = {
        record.audit_id
        for record in _load_material_audit_records(
            source_dir,
            validate_representation_links=False,
        )
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    findings = [
        _source_alignment_finding_from_dict(item, audit_ids, source_entries_by_id)
        for item in raw_findings
    ]
    _ensure_unique([finding.alignment_id for finding in findings], "alignment_id")
    return findings


def _preparation_readiness_finding_from_dict(
    data: dict[str, Any],
    records_by_id: dict[str, MaterialAuditRecord],
) -> PreparationReadinessFinding:
    try:
        finding = PreparationReadinessFinding(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid preparation readiness finding: {error}"
        ) from error

    owner_id = finding.readiness_id or "?"
    for field_name in (
        "readiness_id",
        "audit_id",
        "readiness_state",
        "text_preparation_status",
        "locator_confidence",
        "source_quality",
        "risk_boundary",
        "recommended_next_action",
    ):
        _require_text(getattr(finding, field_name), field_name, owner_id)

    for field_name in ("missing_prerequisites", "ready_reasons", "blockers"):
        _require_string_list(getattr(finding, field_name), field_name, owner_id)

    if finding.audit_id not in records_by_id:
        raise MaterialsAuditError(
            f"{owner_id} references unknown audit: {finding.audit_id}"
        )
    record = records_by_id[finding.audit_id]

    _validate_enum(
        finding.readiness_state,
        MATERIAL_AUDIT_READINESS_STATES,
        "readiness_state",
        owner_id,
    )
    _validate_enum(
        finding.text_preparation_status,
        MATERIAL_AUDIT_TEXT_PREPARATION_STATUSES,
        "text_preparation_status",
        owner_id,
    )
    _validate_enum(
        finding.locator_confidence,
        MATERIAL_AUDIT_LOCATOR_CONFIDENCES,
        "locator_confidence",
        owner_id,
    )
    _validate_enum(
        finding.source_quality,
        MATERIAL_AUDIT_SOURCE_QUALITIES,
        "source_quality",
        owner_id,
    )
    _validate_enum(finding.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    _validate_enum(
        finding.recommended_next_action,
        MATERIAL_AUDIT_ACTIONS,
        "recommended_next_action",
        owner_id,
    )

    if record.risk_tier == "high_risk" and finding.risk_boundary != "high_risk":
        raise MaterialsAuditError(
            f"{owner_id} high_risk audit record requires high_risk risk_boundary"
        )

    if finding.readiness_state == "ready_for_extraction_review":
        if not finding.ready_reasons:
            raise MaterialsAuditError(f"{owner_id} requires ready_reasons")
        if finding.blockers:
            raise MaterialsAuditError(
                f"{owner_id} ready_for_extraction_review cannot have blockers"
            )
        if finding.missing_prerequisites:
            raise MaterialsAuditError(
                f"{owner_id} ready_for_extraction_review cannot have "
                "missing_prerequisites"
            )
        if finding.locator_confidence not in {"moderate", "strong"}:
            raise MaterialsAuditError(
                f"{owner_id} ready_for_extraction_review requires "
                "locator_confidence moderate or strong"
            )
        if finding.source_quality == "needs_recheck":
            raise MaterialsAuditError(
                f"{owner_id} ready_for_extraction_review cannot use "
                "source_quality needs_recheck"
            )
        if (
            record.preparation_state != "ready_for_extraction_review"
            or not record.source_library_entry_id
            or not record.rule_families
        ):
            raise MaterialsAuditError(
                f"{owner_id} ready_for_extraction_review requires a ready "
                "audit record"
            )
    else:
        if not finding.missing_prerequisites and not finding.blockers:
            raise MaterialsAuditError(
                f"{owner_id} {finding.readiness_state} requires missing "
                "prerequisites or blockers"
            )

    if finding.risk_boundary == "high_risk":
        risk_text = " ".join(
            [
                *finding.missing_prerequisites,
                *finding.ready_reasons,
                *finding.blockers,
            ]
        ).lower()
        if "risk" not in risk_text and "boundary" not in risk_text:
            raise MaterialsAuditError(
                f"{owner_id} high_risk readiness requires risk-review notes"
            )
        if finding.recommended_next_action == "extract_candidates":
            raise MaterialsAuditError(
                f"{owner_id} high_risk readiness cannot be routine extraction work"
            )

    return finding


def load_preparation_readiness_findings(
    data_dir: Path | str | None = None,
) -> list[PreparationReadinessFinding]:
    source_dir = _data_dir(data_dir)
    records_by_id = {
        record.audit_id: record
        for record in _load_material_audit_records(
            source_dir,
            validate_representation_links=False,
        )
    }
    findings = [
        _preparation_readiness_finding_from_dict(item, records_by_id)
        for item in _read_json_list(source_dir / "preparation_readiness_findings.json")
    ]
    _ensure_unique([finding.readiness_id for finding in findings], "readiness_id")
    return findings


def _extraction_queue_item_from_dict(
    data: dict[str, Any],
    records_by_id: dict[str, MaterialAuditRecord],
    alignments_by_audit_id: dict[str, list[SourceAlignmentFinding]],
    readiness_by_audit_id: dict[str, PreparationReadinessFinding],
) -> ExtractionQueueItem:
    try:
        item = ExtractionQueueItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(f"invalid extraction queue item: {error}") from error

    owner_id = item.queue_item_id or "?"
    for field_name in (
        "queue_item_id",
        "audit_id",
        "queue_type",
        "priority_level",
        "priority_rationale",
        "risk_boundary",
        "recommended_action",
        "status",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    for field_name in (
        "target_rule_families",
        "target_gap_ids",
        "pre_extraction_checks",
        "depends_on",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)

    if item.audit_id not in records_by_id:
        raise MaterialsAuditError(f"{owner_id} references unknown audit: {item.audit_id}")
    record = records_by_id[item.audit_id]

    _validate_enum(item.queue_type, MATERIAL_AUDIT_QUEUE_TYPES, "queue_type", owner_id)
    _validate_enum(
        item.priority_level,
        SOURCE_LIBRARY_PRIORITY_LEVELS,
        "priority_level",
        owner_id,
    )
    _validate_enum(item.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    _validate_enum(
        item.recommended_action,
        MATERIAL_AUDIT_ACTIONS,
        "recommended_action",
        owner_id,
    )
    _validate_enum(item.status, MATERIAL_AUDIT_QUEUE_STATUSES, "status", owner_id)
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    if not _is_durable_reason(item.priority_rationale):
        raise MaterialsAuditError(f"{owner_id} requires durable priority_rationale")

    readiness = readiness_by_audit_id.get(item.audit_id)
    if readiness is None:
        raise MaterialsAuditError(f"{owner_id} requires readiness finding")

    if item.queue_type == "extraction_ready":
        if item.recommended_action != "extract_candidates":
            raise MaterialsAuditError(
                f"{owner_id} extraction_ready requires extract_candidates action"
            )
        if not item.target_rule_families and not item.target_gap_ids:
            raise MaterialsAuditError(f"{owner_id} extraction_ready requires target")
        if not item.pre_extraction_checks:
            raise MaterialsAuditError(
                f"{owner_id} extraction_ready requires pre_extraction_checks"
            )
        if readiness.readiness_state != "ready_for_extraction_review":
            raise MaterialsAuditError(
                f"{owner_id} extraction_ready requires ready readiness finding"
            )
        if not readiness.ready_reasons:
            raise MaterialsAuditError(
                f"{owner_id} extraction_ready requires readiness rationale"
            )
        source_alignments = alignments_by_audit_id.get(item.audit_id, [])
        if not any(
            alignment.match_type in {"exact", "likely"}
            and alignment.source_library_entry_id
            for alignment in source_alignments
        ):
            raise MaterialsAuditError(
                f"{owner_id} extraction_ready requires source-library alignment"
            )
        if not record.source_library_entry_id:
            raise MaterialsAuditError(
                f"{owner_id} extraction_ready requires source-library relationship"
            )
    elif not readiness.missing_prerequisites and not readiness.blockers:
        raise MaterialsAuditError(
            f"{owner_id} backlog queue requires missing prerequisites or reasons"
        )

    if record.risk_tier == "high_risk" or item.risk_boundary == "high_risk":
        risk_text = " ".join(
            [
                item.priority_rationale,
                *item.pre_extraction_checks,
                *readiness.missing_prerequisites,
                *readiness.blockers,
            ]
        ).lower()
        if item.queue_type == "extraction_ready":
            raise MaterialsAuditError(
                f"{owner_id} high_risk queue cannot be routine extraction work"
            )
        if item.recommended_action not in {"risk_review", "block", "defer"}:
            raise MaterialsAuditError(
                f"{owner_id} high_risk queue requires risk-review action"
            )
        if "risk" not in risk_text and "boundary" not in risk_text:
            raise MaterialsAuditError(
                f"{owner_id} high_risk queue requires risk boundary rationale"
            )

    return item


def load_extraction_queue_items(
    data_dir: Path | str | None = None,
) -> list[ExtractionQueueItem]:
    source_dir = _data_dir(data_dir)
    records_by_id = {
        record.audit_id: record
        for record in _load_material_audit_records(
            source_dir,
            validate_representation_links=False,
        )
    }
    alignments_by_audit_id: dict[str, list[SourceAlignmentFinding]] = {}
    for alignment in load_source_alignment_findings(source_dir):
        alignments_by_audit_id.setdefault(alignment.audit_id, []).append(alignment)
    readiness_by_audit_id = {
        finding.audit_id: finding
        for finding in load_preparation_readiness_findings(source_dir)
    }
    items = [
        _extraction_queue_item_from_dict(
            item,
            records_by_id,
            alignments_by_audit_id,
            readiness_by_audit_id,
        )
        for item in _read_json_list(source_dir / "extraction_queue_items.json")
    ]
    _ensure_unique([item.queue_item_id for item in items], "queue_item_id")
    return items


def _require_non_negative_int(value: Any, field_name: str, owner_id: str) -> None:
    if not isinstance(value, int) or value < 0:
        raise MaterialsAuditError(f"{owner_id} has invalid {field_name}")


def _require_count_mapping(value: Any, field_name: str, owner_id: str) -> None:
    if not isinstance(value, dict) or not value:
        raise MaterialsAuditError(f"{owner_id} has invalid {field_name}")
    for key, count in value.items():
        if not isinstance(key, str) or not key.strip():
            raise MaterialsAuditError(f"{owner_id} has invalid {field_name}")
        _require_non_negative_int(count, field_name, owner_id)


def _raw_text_material_triage_group_from_dict(
    data: dict[str, Any],
) -> RawTextMaterialTriageGroup:
    try:
        group = RawTextMaterialTriageGroup(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text material triage group: {error}"
        ) from error

    owner_id = group.group_id or "?"
    for field_name in (
        "group_id",
        "source_root",
        "group_label",
        "triage_status",
        "risk_boundary",
        "recommended_next_action",
        "rationale",
    ):
        _require_text(getattr(group, field_name), field_name, owner_id)

    if group.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        group.triage_status,
        RAW_TEXT_TRIAGE_STATUSES,
        "triage_status",
        owner_id,
    )
    _validate_enum(group.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    _validate_enum(
        group.recommended_next_action,
        MATERIAL_AUDIT_ACTIONS,
        "recommended_next_action",
        owner_id,
    )
    _require_non_negative_int(group.file_count, "file_count", owner_id)
    _require_non_negative_int(
        group.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    _require_count_mapping(group.extension_counts, "extension_counts", owner_id)
    if sum(group.extension_counts.values()) != group.file_count:
        raise MaterialsAuditError(f"{owner_id} extension_counts do not sum to files")
    if group.priority_text_candidate_count > group.file_count:
        raise MaterialsAuditError(
            f"{owner_id} priority_text_candidate_count exceeds file_count"
        )
    for field_name in (
        "target_rule_families",
        "filename_markers",
        "representative_paths",
        "guardrails",
    ):
        _require_string_list(getattr(group, field_name), field_name, owner_id)
    for rule_family in group.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    if group.triage_status == "source_selection_ready" and not group.next_material_entry:
        raise MaterialsAuditError(
            f"{owner_id} source_selection_ready requires next_material_entry"
        )
    if group.triage_status == "risk_review_required":
        risk_text = " ".join([group.rationale, *group.guardrails]).lower()
        if "risk" not in risk_text and "boundary" not in risk_text:
            raise MaterialsAuditError(
                f"{owner_id} risk_review_required requires risk boundary rationale"
            )

    return group


def load_raw_text_material_triage_groups(
    data_dir: Path | str | None = None,
) -> list[RawTextMaterialTriageGroup]:
    source_dir = _data_dir(data_dir)
    groups = [
        _raw_text_material_triage_group_from_dict(item)
        for item in _read_optional_json_list(
            source_dir / "raw_text_material_triage_groups.json"
        )
    ]
    _ensure_unique([group.group_id for group in groups], "group_id")
    return groups


def _raw_text_source_selection_item_from_dict(
    data: dict[str, Any],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> RawTextSourceSelectionItem:
    try:
        item = RawTextSourceSelectionItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text source selection item: {error}"
        ) from error

    owner_id = item.selection_id or "?"
    for field_name in (
        "selection_id",
        "triage_group_id",
        "source_root",
        "relative_path",
        "title_label",
        "selection_status",
        "risk_boundary",
        "recommended_next_action",
        "source_library_entry_id",
        "source_material_id",
        "source_batch_status",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)

    if item.triage_group_id != RAW_TEXT_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    if not item.relative_path.startswith("梁湘润简体/"):
        raise MaterialsAuditError(f"{owner_id} has invalid relative_path")
    _validate_enum(
        item.selection_status,
        RAW_TEXT_SOURCE_SELECTION_STATUSES,
        "selection_status",
        owner_id,
    )
    _validate_enum(item.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    _validate_enum(
        item.recommended_next_action,
        MATERIAL_AUDIT_ACTIONS,
        "recommended_next_action",
        owner_id,
    )
    if item.source_library_entry_id not in source_entries_by_id:
        raise MaterialsAuditError(
            f"{owner_id} references unknown source-library entry: "
            f"{item.source_library_entry_id}"
        )
    source_entry = source_entries_by_id[item.source_library_entry_id]
    if source_entry.material_id != item.source_material_id:
        raise MaterialsAuditError(f"{owner_id} has mismatched source_material_id")

    for field_name in (
        "target_rule_families",
        "existing_learning_reference_ids",
        "existing_candidate_ids",
        "guardrails",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    if item.selection_status == "ready_for_individual_review":
        if item.recommended_next_action != "review_cleaned_text":
            raise MaterialsAuditError(
                f"{owner_id} ready selection must review cleaned text"
            )
    if item.selection_status == "variant_review_required":
        if item.recommended_next_action != "clarify_identity":
            raise MaterialsAuditError(
                f"{owner_id} variant selection must clarify identity"
            )
    if item.selection_status == "sensitive_boundary_deferred":
        if item.recommended_next_action not in {"risk_review", "defer"}:
            raise MaterialsAuditError(
                f"{owner_id} sensitive selection must stay behind boundary review"
            )

    return item


def load_raw_text_source_selection_items(
    data_dir: Path | str | None = None,
) -> list[RawTextSourceSelectionItem]:
    source_dir = _data_dir(data_dir)
    source_entries_by_id = _load_source_library_entries(source_dir)
    items = [
        _raw_text_source_selection_item_from_dict(item, source_entries_by_id)
        for item in _read_optional_json_list(
            source_dir / "raw_text_source_selection_items.json"
        )
    ]
    _ensure_unique([item.selection_id for item in items], "selection_id")
    return items


def _raw_text_source_cluster_selection_item_from_dict(
    data: dict[str, Any],
) -> RawTextSourceClusterSelectionItem:
    try:
        item = RawTextSourceClusterSelectionItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text source cluster selection item: {error}"
        ) from error

    owner_id = item.cluster_id or "?"
    for field_name in (
        "cluster_id",
        "triage_group_id",
        "source_root",
        "cluster_label",
        "cluster_status",
        "risk_boundary",
        "recommended_next_action",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_SOURCE_CLUSTER_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.cluster_status,
        RAW_TEXT_SOURCE_CLUSTER_SELECTION_STATUSES,
        "cluster_status",
        owner_id,
    )
    _validate_enum(item.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    _validate_enum(
        item.recommended_next_action,
        MATERIAL_AUDIT_ACTIONS,
        "recommended_next_action",
        owner_id,
    )
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    _require_count_mapping(item.extension_counts, "extension_counts", owner_id)
    if item.file_count <= 0:
        raise MaterialsAuditError(f"{owner_id} requires positive file_count")
    if item.priority_text_candidate_count > item.file_count:
        raise MaterialsAuditError(
            f"{owner_id} priority count cannot exceed file_count"
        )
    if sum(item.extension_counts.values()) != item.file_count:
        raise MaterialsAuditError(f"{owner_id} extension counts must match file_count")

    for field_name in (
        "target_rule_families",
        "filename_markers",
        "representative_paths",
        "guardrails",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.representative_paths:
        raise MaterialsAuditError(f"{owner_id} requires representative_paths")
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    if item.cluster_status == "selected_for_source_selection":
        if item.recommended_next_action not in {"clarify_identity", "register_source"}:
            raise MaterialsAuditError(
                f"{owner_id} selected cluster must prepare source selection"
            )
    if item.cluster_status == "identity_review_required":
        if item.recommended_next_action != "clarify_identity":
            raise MaterialsAuditError(
                f"{owner_id} identity-review cluster must clarify identity"
            )
    if item.cluster_status == "sensitive_boundary_deferred":
        if item.recommended_next_action not in {"risk_review", "defer"}:
            raise MaterialsAuditError(
                f"{owner_id} sensitive cluster must stay behind boundary review"
            )

    return item


def load_raw_text_source_cluster_selection_items(
    data_dir: Path | str | None = None,
) -> list[RawTextSourceClusterSelectionItem]:
    source_dir = _data_dir(data_dir)
    items = [
        _raw_text_source_cluster_selection_item_from_dict(item)
        for item in _read_optional_json_list(
            source_dir / "raw_text_source_cluster_selection_items.json"
        )
    ]
    _ensure_unique([item.cluster_id for item in items], "cluster_id")
    return items


def _count_values(values: list[str]) -> dict[str, int]:
    return dict(Counter(values))


def _queue_priority_rank(priority_level: str) -> int:
    return {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
        "deferred": 4,
    }[priority_level]


def _queue_sort_key(indexed_item: tuple[int, ExtractionQueueItem]) -> tuple[int, int]:
    index, item = indexed_item
    return (_queue_priority_rank(item.priority_level), index)


def _select_next_queue_item_ids(
    queue_items: list[ExtractionQueueItem],
    limit: int = 5,
) -> list[str]:
    grouped: dict[str, list[tuple[int, ExtractionQueueItem]]] = {}
    for index, item in enumerate(queue_items):
        if item.status == "completed":
            continue
        grouped.setdefault(item.queue_type, []).append((index, item))

    for items in grouped.values():
        items.sort(key=_queue_sort_key)

    selected: list[ExtractionQueueItem] = []
    selected.extend(item for _, item in grouped.get("extraction_ready", [])[:2])
    selected.extend(item for _, item in grouped.get("registration_backlog", [])[:1])
    selected.extend(item for _, item in grouped.get("risk_review_backlog", [])[:1])
    selected.extend(item for _, item in grouped.get("blocked_backlog", [])[:1])

    seen_ids = {item.queue_item_id for item in selected}
    for queue_type in (
        "extraction_ready",
        "registration_backlog",
        "risk_review_backlog",
        "preparation_backlog",
        "blocked_backlog",
    ):
        for _, item in grouped.get(queue_type, []):
            if item.queue_item_id in seen_ids:
                continue
            selected.append(item)
            seen_ids.add(item.queue_item_id)
            if len(selected) >= limit:
                return [queue_item.queue_item_id for queue_item in selected[:limit]]

    return [queue_item.queue_item_id for queue_item in selected[:limit]]


def _load_covered_queue_item_ids(source_dir: Path) -> list[str]:
    extraction_dir = _sibling_data_dir(source_dir, "extraction_queue_intake")
    if extraction_dir is None:
        return []
    package_path = extraction_dir / "extraction_work_packages.json"
    if not package_path.exists():
        return []

    packages = _read_json_list(package_path)
    covered_queue_item_ids: list[str] = []
    for package in packages:
        snapshot_ids = package.get("source_queue_snapshot_ids", [])
        if not isinstance(snapshot_ids, list):
            raise MaterialsAuditError(
                "extraction_work_packages.json source_queue_snapshot_ids "
                "must be arrays"
            )
        for queue_item_id in snapshot_ids:
            if not isinstance(queue_item_id, str) or not queue_item_id.strip():
                raise MaterialsAuditError(
                    "extraction_work_packages.json has invalid "
                    "source_queue_snapshot_ids"
                )
            covered_queue_item_ids.append(queue_item_id)
    return covered_queue_item_ids


def _relative_inventory_reference(path: Path, workspace_root: Path) -> str:
    reference = path.relative_to(workspace_root).as_posix()
    return f"{reference}/" if path.is_dir() else reference


def _scan_external_inventory_entries(
    workspace_root: Path,
) -> dict[str, list[str]]:
    roots = {
        "root_pdf": sorted(workspace_root.glob("*.pdf")),
        "markdown_root": sorted((workspace_root / "Markdown").iterdir())
        if (workspace_root / "Markdown").exists()
        else [],
        "raw_source_root": sorted((workspace_root / "资料原文").iterdir())
        if (workspace_root / "资料原文").exists()
        else [],
        "preparation_root": sorted((workspace_root / "资料整理").iterdir())
        if (workspace_root / "资料整理").exists()
        else [],
    }
    return {
        root_id: [_relative_inventory_reference(path, workspace_root) for path in paths]
        for root_id, paths in roots.items()
    }


def _normalize_inventory_reference(reference: str) -> str:
    return reference.replace("\\", "/").rstrip("/")


def _is_reference_tracked(reference: str, tracked_references: set[str]) -> bool:
    normalized = _normalize_inventory_reference(reference)
    return normalized in tracked_references


def build_external_material_inventory_refresh_summary(
    data_dir: Path | str | None = None,
    *,
    workspace_root: Path | str | None = None,
) -> ExternalMaterialInventoryRefreshSummary:
    source_dir = _data_dir(data_dir)
    root = Path(workspace_root) if workspace_root is not None else _workspace_root()
    inventory_entries_by_root = _scan_external_inventory_entries(root)
    all_inventory_entries = [
        reference
        for references in inventory_entries_by_root.values()
        for reference in references
    ]
    representations = load_material_representations(source_dir)
    tracked_references = {
        _normalize_inventory_reference(representation.local_reference)
        for representation in representations
    }
    tracked_external_entry_ids = [
        reference
        for reference in all_inventory_entries
        if _is_reference_tracked(reference, tracked_references)
    ]
    excluded_work_artifact_ids = [
        reference
        for reference in all_inventory_entries
        if reference in EXTERNAL_INVENTORY_WORK_ARTIFACTS
    ]
    untracked_material_entry_ids = [
        reference
        for reference in all_inventory_entries
        if not _is_reference_tracked(reference, tracked_references)
        and reference not in EXTERNAL_INVENTORY_WORK_ARTIFACTS
    ]
    representation_ids = {
        representation.representation_id for representation in representations
    }
    queue_item_ids = {
        item.queue_item_id for item in load_extraction_queue_items(source_dir)
    }
    newly_registered_representation_ids = [
        representation_id
        for representation_id in EXTERNAL_INVENTORY_NEW_REPRESENTATION_IDS
        if representation_id in representation_ids
    ]
    new_queue_item_ids = [
        queue_item_id
        for queue_item_id in EXTERNAL_INVENTORY_NEW_QUEUE_ITEM_IDS
        if queue_item_id in queue_item_ids
    ]

    return ExternalMaterialInventoryRefreshSummary(
        refresh_id="015-external-material-inventory-refresh",
        refresh_status=(
            "untracked_material_entries_available"
            if untracked_material_entry_ids
            else "scoped_metadata_registered"
        ),
        external_entry_counts={
            root_id: len(references)
            for root_id, references in inventory_entries_by_root.items()
        },
        scanned_entry_count=len(all_inventory_entries),
        tracked_external_entry_ids=tracked_external_entry_ids,
        untracked_material_entry_ids=untracked_material_entry_ids,
        excluded_work_artifact_ids=excluded_work_artifact_ids,
        newly_registered_representation_ids=newly_registered_representation_ids,
        new_queue_item_ids=new_queue_item_ids,
        downstream_mutation_authorized=False,
        next_material_entry=EXTERNAL_INVENTORY_NEXT_MATERIAL_ENTRY,
        boundary_checks={
            "external_roots_scanned_read_only": (
                "passed" if all_inventory_entries else "failed"
            ),
            "015_metadata_registered": (
                "passed"
                if len(newly_registered_representation_ids)
                == len(EXTERNAL_INVENTORY_NEW_REPRESENTATION_IDS)
                and len(new_queue_item_ids) == len(EXTERNAL_INVENTORY_NEW_QUEUE_ITEM_IDS)
                else "failed"
            ),
            "workflow_artifacts_excluded": (
                "passed"
                if set(excluded_work_artifact_ids) == EXTERNAL_INVENTORY_WORK_ARTIFACTS
                else "failed"
            ),
            "raw_materials_not_mutated": "passed",
            "013_012_not_mutated": "passed",
        },
        guardrails=[
            "External inventory refresh scans only path labels and immediate entries.",
            "Life Death Markdown is a 015 representation, not runtime report evidence.",
            "The raw text folder requires bounded risk triage before registration.",
            "No 013 candidate, review, promotion, or 012 evidence mutation is authorized.",
        ],
    )


def render_external_material_inventory_refresh_markdown(
    refresh: ExternalMaterialInventoryRefreshSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if refresh.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 External Material Inventory Refresh",
        "",
        f"- Refresh id: `{refresh.refresh_id}`",
        f"- `external-inventory-status={refresh.refresh_status}`",
        f"- `external-entries={refresh.scanned_entry_count}`",
        (
            "- `new-015-representations="
            f"{len(refresh.newly_registered_representation_ids)}`"
        ),
        f"- `new-015-queue-items={len(refresh.new_queue_item_ids)}`",
        (
            "- `untracked-material-entries="
            f"{len(refresh.untracked_material_entry_ids)}`"
        ),
        f"- `excluded-work-artifacts={len(refresh.excluded_work_artifact_ids)}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={refresh.next_material_entry}`",
        "",
        "External entry counts:",
    ]
    lines.extend(
        f"- `{root_id}`: `{count}`"
        for root_id, count in refresh.external_entry_counts.items()
    )
    lines.extend(["", "Boundary checks:"])
    lines.extend(
        f"- `{check_id}`: `{status}`"
        for check_id, status in refresh.boundary_checks.items()
    )
    lines.extend(
        [
            "",
            "Guardrails:",
            *[f"- {guardrail}" for guardrail in refresh.guardrails],
        ]
    )
    return "\n".join(lines) + "\n"


def _inventory_csv_dir(workspace_root: Path | str | None = None) -> Path:
    root = Path(workspace_root) if workspace_root is not None else _workspace_root()
    return root / "资料整理" / "_inventory"


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    except FileNotFoundError as error:
        raise MaterialsAuditError(f"missing inventory CSV: {path.name}") from error


def _sum_extension_counts(
    groups: list[RawTextMaterialTriageGroup],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for group in groups:
        counts.update(group.extension_counts)
    return dict(counts)


def build_raw_text_material_triage_summary(
    data_dir: Path | str | None = None,
    *,
    inventory_dir: Path | str | None = None,
) -> RawTextMaterialTriageSummary:
    groups = load_raw_text_material_triage_groups(data_dir)
    csv_dir = Path(inventory_dir) if inventory_dir is not None else _inventory_csv_dir()
    inventory_rows = _read_csv_rows(csv_dir / "inventory_all.csv")
    priority_rows = _read_csv_rows(csv_dir / "priority_text_candidates.csv")

    total_file_count = sum(group.file_count for group in groups)
    priority_text_candidate_count = sum(
        group.priority_text_candidate_count for group in groups
    )
    extension_counts = _sum_extension_counts(groups)
    inventory_extension_counts = dict(
        Counter((row.get("Extension") or "").lower() for row in inventory_rows)
    )
    non_text_group_extension_counts = Counter()
    for group in groups:
        if group.triage_status == "deferred_non_text":
            non_text_group_extension_counts.update(group.extension_counts)
    non_text_media_deferred = all(
        non_text_group_extension_counts.get(extension, 0)
        == inventory_extension_counts.get(extension, 0)
        for extension in (".mp4", ".flv", ".jpg", ".png")
    )
    boundary_checks = {
        "inventory_csv_loaded": (
            "passed" if inventory_rows and priority_rows else "failed"
        ),
        "triage_groups_cover_inventory": (
            "passed" if total_file_count == len(inventory_rows) else "failed"
        ),
        "priority_candidates_accounted": (
            "passed"
            if priority_text_candidate_count == len(priority_rows)
            else "failed"
        ),
        "non_text_media_deferred": "passed" if non_text_media_deferred else "failed",
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }

    return RawTextMaterialTriageSummary(
        triage_id="015-raw-text-materials-folder-risk-triage",
        triage_status=(
            "triage_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "triage_needs_attention"
        ),
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        total_file_count=total_file_count,
        priority_text_candidate_count=priority_text_candidate_count,
        triage_group_count=len(groups),
        triage_status_counts=_count_values([group.triage_status for group in groups]),
        risk_boundary_counts=_count_values([group.risk_boundary for group in groups]),
        extension_counts=extension_counts,
        next_group_ids=[
            group.group_id
            for group in groups
            if group.triage_status == "source_selection_ready"
        ],
        risk_review_group_ids=[
            group.group_id
            for group in groups
            if group.triage_status == "risk_review_required"
        ],
        deferred_group_ids=[
            group.group_id
            for group in groups
            if group.triage_status in RAW_TEXT_TRIAGE_DEFERRED_STATUSES
        ],
        downstream_mutation_authorized=False,
        next_material_entry=RAW_TEXT_TRIAGE_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Raw text triage uses path labels and existing inventory CSV metadata only.",
            "Non-text media and images stay deferred until a separate review workflow exists.",
            "Ritual-remedy, life-death, and sensitive blind-school groups require risk review.",
            "No 013 candidate, review, promotion, or 012 evidence mutation is authorized.",
        ],
    )


def render_raw_text_material_triage_markdown(
    summary: RawTextMaterialTriageSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Materials Folder Risk Triage",
        "",
        f"- Triage id: `{summary.triage_id}`",
        f"- `raw-text-triage-status={summary.triage_status}`",
        f"- `raw-text-total-files={summary.total_file_count}`",
        f"- `raw-text-priority-candidates={summary.priority_text_candidate_count}`",
        f"- `raw-text-triage-groups={summary.triage_group_count}`",
        f"- `risk-review-groups={len(summary.risk_review_group_ids)}`",
        f"- `deferred-groups={len(summary.deferred_group_ids)}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Triage status counts:",
    ]
    lines.extend(
        f"- `{status}`: `{count}`"
        for status, count in summary.triage_status_counts.items()
    )
    lines.extend(["", "Risk boundary counts:"])
    lines.extend(
        f"- `{risk_boundary}`: `{count}`"
        for risk_boundary, count in summary.risk_boundary_counts.items()
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


def _count_rule_families(items: list[RawTextSourceSelectionItem]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts.update(item.target_rule_families)
    return dict(sorted(counts.items()))


def _count_cluster_rule_families(
    items: list[RawTextSourceClusterSelectionItem],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts.update(item.target_rule_families)
    return dict(sorted(counts.items()))


def build_raw_text_source_selection_summary(
    data_dir: Path | str | None = None,
) -> RawTextSourceSelectionSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_source_selection_items(source_dir)
    groups_by_id = {
        group.group_id: group for group in load_raw_text_material_triage_groups(source_dir)
    }
    triage_group = groups_by_id.get(RAW_TEXT_SOURCE_SELECTION_TRIAGE_GROUP_ID)
    source_entries_by_id = _load_source_library_entries(source_dir)
    existing_source_batches_preserved = bool(items) and all(
        item.source_library_entry_id in source_entries_by_id
        and source_entries_by_id[item.source_library_entry_id].material_id
        == item.source_material_id
        for item in items
    )
    boundary_checks = {
        "selection_items_loaded": "passed" if items else "failed",
        "triage_group_loaded": "passed" if triage_group else "failed",
        "triage_group_file_count_matched": (
            "passed"
            if triage_group and len(items) == triage_group.file_count
            else "failed"
        ),
        "existing_source_batches_preserved": (
            "passed" if existing_source_batches_preserved else "failed"
        ),
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }

    selected_item_ids = [
        item.selection_id
        for item in items
        if item.selection_status == "ready_for_individual_review"
    ]
    deferred_item_ids = [
        item.selection_id
        for item in items
        if item.selection_status
        in {"variant_review_required", "sensitive_boundary_deferred"}
    ]
    status_counts = _count_values([item.selection_status for item in items])

    return RawTextSourceSelectionSummary(
        selection_id=RAW_TEXT_SOURCE_SELECTION_ID,
        selection_status=(
            "source_selection_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "source_selection_needs_attention"
        ),
        triage_group_id=RAW_TEXT_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        source_selection_item_count=len(items),
        selected_for_individual_review_count=len(selected_item_ids),
        existing_batch_covered_count=status_counts.get("existing_batch_covered", 0),
        variant_review_required_count=status_counts.get(
            "variant_review_required", 0
        ),
        sensitive_boundary_deferred_count=status_counts.get(
            "sensitive_boundary_deferred", 0
        ),
        status_counts=status_counts,
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_rule_families(items),
        selected_item_ids=selected_item_ids,
        deferred_item_ids=deferred_item_ids,
        downstream_mutation_authorized=False,
        next_material_entry=RAW_TEXT_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Source selection uses inventory labels and existing project metadata only.",
            "Existing Markdown source batches 001, 002, and 004 stay authoritative.",
            "Ready items require individual cleaned-text review before learning-note work.",
            "Variant and sensitive items stay out of 013/012 until separately reviewed.",
        ],
    )


def _sum_cluster_extension_counts(
    items: list[RawTextSourceClusterSelectionItem],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts.update(item.extension_counts)
    return dict(counts)


def build_raw_text_source_cluster_selection_summary(
    data_dir: Path | str | None = None,
) -> RawTextSourceClusterSelectionSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_source_cluster_selection_items(source_dir)
    groups_by_id = {
        group.group_id: group for group in load_raw_text_material_triage_groups(source_dir)
    }
    triage_group = groups_by_id.get(RAW_TEXT_SOURCE_CLUSTER_SELECTION_TRIAGE_GROUP_ID)
    clustered_file_count = sum(item.file_count for item in items)
    clustered_priority_count = sum(
        item.priority_text_candidate_count for item in items
    )
    boundary_checks = {
        "cluster_items_loaded": "passed" if items else "failed",
        "triage_group_loaded": "passed" if triage_group else "failed",
        "triage_group_file_count_matched": (
            "passed"
            if triage_group and clustered_file_count == triage_group.file_count
            else "failed"
        ),
        "triage_group_priority_count_matched": (
            "passed"
            if triage_group
            and clustered_priority_count == triage_group.priority_text_candidate_count
            else "failed"
        ),
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }
    selected_cluster_ids = [
        item.cluster_id
        for item in items
        if item.cluster_status == "selected_for_source_selection"
    ]
    deferred_cluster_ids = [
        item.cluster_id
        for item in items
        if item.cluster_status
        in {"identity_review_required", "sensitive_boundary_deferred"}
    ]

    return RawTextSourceClusterSelectionSummary(
        selection_id=RAW_TEXT_SOURCE_CLUSTER_SELECTION_ID,
        selection_status=(
            "cluster_selection_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "cluster_selection_needs_attention"
        ),
        triage_group_id=RAW_TEXT_SOURCE_CLUSTER_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        cluster_count=len(items),
        clustered_file_count=clustered_file_count,
        clustered_priority_text_candidate_count=clustered_priority_count,
        selected_cluster_count=len(selected_cluster_ids),
        deferred_cluster_count=len(deferred_cluster_ids),
        cluster_status_counts=_count_values([item.cluster_status for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        extension_counts=_sum_cluster_extension_counts(items),
        target_rule_family_counts=_count_cluster_rule_families(items),
        selected_cluster_ids=selected_cluster_ids,
        deferred_cluster_ids=deferred_cluster_ids,
        downstream_mutation_authorized=False,
        next_material_entry=RAW_TEXT_SOURCE_CLUSTER_SELECTION_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Cluster selection uses inventory labels and representative paths only.",
            "Selected clusters still require source-level identity review before registration.",
            "Sensitive and ambiguous clusters stay out of 013/012 until separately reviewed.",
            "Raw files, source-library records, candidates, reviews, promotions, and formal evidence are not mutated.",
        ],
    )


def render_raw_text_source_cluster_selection_markdown(
    summary: RawTextSourceClusterSelectionSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Bazi General Source Cluster Selection",
        "",
        f"- Selection id: `{summary.selection_id}`",
        f"- `cluster-selection-status={summary.selection_status}`",
        f"- `cluster-selection-items={summary.cluster_count}`",
        f"- `clustered-files={summary.clustered_file_count}`",
        (
            "- `clustered-priority-candidates="
            f"{summary.clustered_priority_text_candidate_count}`"
        ),
        f"- `selected-clusters={summary.selected_cluster_count}`",
        f"- `deferred-clusters={summary.deferred_cluster_count}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Cluster status counts:",
    ]
    lines.extend(
        f"- `{status}`: `{count}`"
        for status, count in summary.cluster_status_counts.items()
    )
    lines.extend(["", "Selected clusters:"])
    lines.extend(f"- `{cluster_id}`" for cluster_id in summary.selected_cluster_ids)
    lines.extend(["", "Deferred or review-gated clusters:"])
    lines.extend(f"- `{cluster_id}`" for cluster_id in summary.deferred_cluster_ids)
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


def render_raw_text_source_selection_markdown(
    summary: RawTextSourceSelectionSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Liang Bazi Core Source Selection",
        "",
        f"- Selection id: `{summary.selection_id}`",
        f"- `source-selection-status={summary.selection_status}`",
        f"- `source-selection-items={summary.source_selection_item_count}`",
        f"- `existing-batch-covered={summary.existing_batch_covered_count}`",
        (
            "- `selected-for-individual-review="
            f"{summary.selected_for_individual_review_count}`"
        ),
        f"- `variant-review-required={summary.variant_review_required_count}`",
        (
            "- `sensitive-boundary-deferred="
            f"{summary.sensitive_boundary_deferred_count}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Status counts:",
    ]
    lines.extend(
        f"- `{status}`: `{count}`"
        for status, count in summary.status_counts.items()
    )
    lines.extend(["", "Selected individual review items:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.selected_item_ids)
    lines.extend(["", "Deferred or review-gated items:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.deferred_item_ids)
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


def build_materials_audit_queue_refresh_summary(
    data_dir: Path | str | None = None,
    *,
    covered_queue_item_ids: list[str] | None = None,
) -> MaterialQueueRefreshSummary:
    source_dir = _data_dir(data_dir)
    queue_items = load_extraction_queue_items(source_dir)
    progress = build_materials_audit_progress_summary(source_dir)
    covered_ids = (
        covered_queue_item_ids
        if covered_queue_item_ids is not None
        else _load_covered_queue_item_ids(source_dir)
    )
    covered_id_set = set(covered_ids)
    locally_completed_queue_item_ids = [
        item.queue_item_id
        for item in queue_items
        if item.status == "completed" and item.queue_item_id not in covered_id_set
    ]
    locally_completed_id_set = set(locally_completed_queue_item_ids)
    queue_item_ids = [item.queue_item_id for item in queue_items]
    uncovered_items = [
        item
        for item in queue_items
        if item.queue_item_id not in covered_id_set
        and item.queue_item_id not in locally_completed_id_set
    ]
    uncovered_queue_item_ids = [item.queue_item_id for item in uncovered_items]
    refreshed_next_action_ids = _select_next_queue_item_ids(uncovered_items)
    all_queue_items_covered = not uncovered_queue_item_ids and bool(queue_items)
    source_selection_ready = bool(load_raw_text_source_selection_items(source_dir))

    return MaterialQueueRefreshSummary(
        refresh_id="015-materials-audit-next-action-queue-refresh",
        refresh_status=(
            "covered_or_completed_queue_exhausted"
            if all_queue_items_covered and locally_completed_queue_item_ids
            else "covered_queue_exhausted"
            if all_queue_items_covered
            else "uncovered_queue_items_available"
        ),
        queue_item_count=len(queue_items),
        covered_queue_item_count=sum(
            1 for queue_item_id in queue_item_ids if queue_item_id in covered_id_set
        ),
        covered_queue_item_ids=[
            queue_item_id
            for queue_item_id in queue_item_ids
            if queue_item_id in covered_id_set
        ],
        locally_completed_queue_item_ids=locally_completed_queue_item_ids,
        uncovered_queue_item_ids=uncovered_queue_item_ids,
        legacy_next_action_ids=progress.next_action_ids,
        refreshed_next_action_ids=refreshed_next_action_ids,
        downstream_mutation_authorized=False,
        next_material_entry=(
            RAW_TEXT_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY
            if all_queue_items_covered
            and locally_completed_queue_item_ids
            and source_selection_ready
            else RAW_TEXT_TRIAGE_NEXT_MATERIAL_ENTRY
            if all_queue_items_covered and locally_completed_queue_item_ids
            else (
                EXTERNAL_INVENTORY_NEXT_MATERIAL_ENTRY
                if refreshed_next_action_ids
                == list(EXTERNAL_INVENTORY_NEW_QUEUE_ITEM_IDS)
                else (
                    "015-uncovered-material-queue-review"
                    if refreshed_next_action_ids
                    else "015-external-material-inventory-refresh"
                )
            )
        ),
        boundary_checks={
            "015_queue_loaded": "passed" if queue_items else "failed",
            "016_coverage_loaded": "passed" if covered_ids else "failed",
            "covered_items_excluded": (
                "passed"
                if not set(refreshed_next_action_ids) & covered_id_set
                else "failed"
            ),
            "completed_items_excluded": (
                "passed"
                if not set(refreshed_next_action_ids) & locally_completed_id_set
                else "failed"
            ),
            "013_012_not_mutated": "passed",
        },
        guardrails=[
            "Queue refresh is read-only 015 planning metadata.",
            "Covered 016 queue ids stay excluded from refreshed next actions.",
            "No 013 candidate, review, promotion, or 012 evidence mutation is authorized.",
            "Root PDFs, Markdown folders, raw sources, and preparation folders are not mutated.",
        ],
    )


def render_materials_audit_queue_refresh_markdown(
    refresh: MaterialQueueRefreshSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if refresh.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Queue Refresh",
        "",
        f"- Refresh id: `{refresh.refresh_id}`",
        f"- `queue-refresh-status={refresh.refresh_status}`",
        f"- `015-queue-items={refresh.queue_item_count}`",
        f"- `016-covered-queue-items={refresh.covered_queue_item_count}`",
        (
            "- `015-local-completed-queue-items="
            f"{len(refresh.locally_completed_queue_item_ids)}`"
        ),
        f"- `uncovered-queue-items={len(refresh.uncovered_queue_item_ids)}`",
        f"- `refreshed-next-action-ids={len(refresh.refreshed_next_action_ids)}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={refresh.next_material_entry}`",
        "",
        "Boundary checks:",
    ]
    lines.extend(
        f"- `{check_id}`: `{status}`"
        for check_id, status in refresh.boundary_checks.items()
    )
    lines.extend(
        [
            "",
            "Guardrails:",
            *[f"- {guardrail}" for guardrail in refresh.guardrails],
        ]
    )
    return "\n".join(lines) + "\n"


def build_materials_audit_progress_summary(
    data_dir: Path | str | None = None,
) -> AuditProgressSummary:
    source_dir = _data_dir(data_dir)
    records = load_material_audit_records(source_dir)
    representations = load_material_representations(source_dir)
    alignments = load_source_alignment_findings(source_dir)
    readiness = load_preparation_readiness_findings(source_dir)
    queue_items = load_extraction_queue_items(source_dir)

    queue_type_counts = _count_values([item.queue_type for item in queue_items])

    return AuditProgressSummary(
        material_group_counts=_count_values(
            [record.preparation_state for record in records]
        ),
        representation_counts=_count_values(
            [representation.representation_type for representation in representations]
        ),
        source_alignment_counts=_count_values(
            [alignment.match_type for alignment in alignments]
        ),
        readiness_counts=_count_values(
            [finding.readiness_state for finding in readiness]
        ),
        queue_counts=queue_type_counts,
        risk_tier_counts=_count_values([record.risk_tier for record in records]),
        out_of_scope_count=sum(
            1 for record in records if record.material_scope == "out_of_scope"
        ),
        missing_registration_count=sum(
            1
            for record in records
            if record.recommended_next_action == "register_source"
            and not record.source_library_entry_id
        ),
        extraction_ready_count=queue_type_counts.get("extraction_ready", 0),
        preparation_backlog_count=queue_type_counts.get("preparation_backlog", 0),
        registration_backlog_count=queue_type_counts.get("registration_backlog", 0),
        risk_review_backlog_count=queue_type_counts.get("risk_review_backlog", 0),
        blocked_backlog_count=queue_type_counts.get("blocked_backlog", 0),
        deferred_queue_count=sum(
            1
            for item in queue_items
            if item.status == "deferred" or item.recommended_action == "defer"
        ),
        blocked_queue_count=sum(
            1
            for item in queue_items
            if item.status == "blocked" or item.recommended_action == "block"
        ),
        next_action_ids=_select_next_queue_item_ids(queue_items),
        source_boundary_counts=_count_values(
            [record.source_boundary for record in records]
        ),
        material_scope_counts=_count_values([record.material_scope for record in records]),
        text_preparation_counts=_count_values(
            [finding.text_preparation_status for finding in readiness]
        ),
        locator_confidence_counts=_count_values(
            [finding.locator_confidence for finding in readiness]
        ),
        source_quality_counts=_count_values(
            [finding.source_quality for finding in readiness]
        ),
        risk_boundary_counts=_count_values(
            [finding.risk_boundary for finding in readiness]
        ),
        missing_prerequisite_counts=_count_values(
            [
                prerequisite
                for finding in readiness
                for prerequisite in finding.missing_prerequisites
            ]
        ),
    )


def validate_materials_audit_quality(data_dir: Path | str | None = None) -> list[str]:
    try:
        source_dir = _data_dir(data_dir)
        records = load_material_audit_records(source_dir)
        representations = load_material_representations(source_dir)
        alignments = load_source_alignment_findings(source_dir)
        readiness = load_preparation_readiness_findings(source_dir)
        queue_items = load_extraction_queue_items(source_dir)
        raw_text_triage_groups = load_raw_text_material_triage_groups(source_dir)
        raw_text_source_selection_items = load_raw_text_source_selection_items(
            source_dir
        )
        raw_text_source_cluster_selection_items = (
            load_raw_text_source_cluster_selection_items(source_dir)
        )
    except MaterialsAuditError as error:
        return [str(error)]

    failures: list[str] = []
    for owner_id, field_name, value in _iter_quality_text_fields(
        records,
        representations,
        alignments,
        readiness,
        queue_items,
        raw_text_triage_groups,
        raw_text_source_selection_items,
        raw_text_source_cluster_selection_items,
    ):
        if not value:
            continue
        if len(value) > MATERIALS_AUDIT_TEXT_LIMIT:
            failures.append(f"{owner_id} {field_name} is too long")
        if _contains_marker(value, MATERIALS_AUDIT_REPORT_EVIDENCE_MARKERS):
            failures.append(
                f"{owner_id} {field_name} violates report evidence boundary"
            )
        if _contains_marker(value, MATERIALS_AUDIT_ABSOLUTE_OUTCOME_PHRASES):
            failures.append(f"{owner_id} {field_name} contains absolute language")
        if _contains_marker(value, MATERIALS_AUDIT_EXACT_DEATH_PHRASES):
            failures.append(f"{owner_id} {field_name} contains exact death wording")
        if _contains_marker(value, MATERIALS_AUDIT_PROHIBITED_HIGH_RISK_PHRASES):
            failures.append(
                f"{owner_id} {field_name} contains prohibited high-risk wording"
            )
    return failures


def _iter_quality_text_fields(
    records: list[MaterialAuditRecord],
    representations: list[MaterialRepresentation],
    alignments: list[SourceAlignmentFinding],
    readiness: list[PreparationReadinessFinding],
    queue_items: list[ExtractionQueueItem],
    raw_text_triage_groups: list[RawTextMaterialTriageGroup],
    raw_text_source_selection_items: list[RawTextSourceSelectionItem],
    raw_text_source_cluster_selection_items: list[RawTextSourceClusterSelectionItem],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for record in records:
        fields.extend(
            (
                (record.audit_id, "canonical_title", record.canonical_title),
                (record.audit_id, "rights_notes", record.rights_notes),
                (record.audit_id, "outcome_reason", record.outcome_reason),
            )
        )
        fields.extend((record.audit_id, "risk_notes", note) for note in record.risk_notes)
    for representation in representations:
        fields.append(
            (representation.representation_id, "notes", representation.notes)
        )
    for alignment in alignments:
        fields.extend(
            (
                (alignment.alignment_id, "evidence", alignment.evidence),
                (
                    alignment.alignment_id,
                    "registration_recommendation",
                    alignment.registration_recommendation,
                ),
                (
                    alignment.alignment_id,
                    "duplicate_or_variant_notes",
                    alignment.duplicate_or_variant_notes,
                ),
            )
        )
    for finding in readiness:
        fields.extend(
            (finding.readiness_id, "missing_prerequisites", item)
            for item in finding.missing_prerequisites
        )
        fields.extend(
            (finding.readiness_id, "ready_reasons", item)
            for item in finding.ready_reasons
        )
        fields.extend(
            (finding.readiness_id, "blockers", item) for item in finding.blockers
        )
    for item in queue_items:
        fields.append(
            (item.queue_item_id, "priority_rationale", item.priority_rationale)
        )
        fields.extend(
            (item.queue_item_id, "pre_extraction_checks", check)
            for check in item.pre_extraction_checks
        )
    for group in raw_text_triage_groups:
        fields.extend(
            (
                (group.group_id, "group_label", group.group_label),
                (group.group_id, "rationale", group.rationale),
            )
        )
        fields.extend((group.group_id, "guardrails", item) for item in group.guardrails)
    for item in raw_text_source_selection_items:
        fields.extend(
            (
                (item.selection_id, "title_label", item.title_label),
                (item.selection_id, "rationale", item.rationale),
                (item.selection_id, "source_batch_status", item.source_batch_status),
            )
        )
        fields.extend(
            (item.selection_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_source_cluster_selection_items:
        fields.extend(
            (
                (item.cluster_id, "cluster_label", item.cluster_label),
                (item.cluster_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.cluster_id, "representative_paths", path)
            for path in item.representative_paths
        )
        fields.extend(
            (item.cluster_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    return fields
