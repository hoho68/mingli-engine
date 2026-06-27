"""Deterministic existing-materials audit loading and validation."""

from collections import Counter
import json
from pathlib import Path
from typing import Any

from mingli_engine import source_library
from mingli_engine.models import (
    AuditProgressSummary,
    CONFIDENCE_LEVELS,
    ExtractionQueueItem,
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


def _data_dir(data_dir: Path | str | None) -> Path:
    return Path(data_dir) if data_dir is not None else _DATA_DIR


def _sibling_data_dir(source_dir: Path, sibling_name: str) -> Path | None:
    sibling = source_dir.parent / sibling_name
    return sibling if sibling.exists() else None


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
    queue_item_ids = [item.queue_item_id for item in queue_items]
    uncovered_items = [
        item for item in queue_items if item.queue_item_id not in covered_id_set
    ]
    uncovered_queue_item_ids = [item.queue_item_id for item in uncovered_items]
    refreshed_next_action_ids = _select_next_queue_item_ids(uncovered_items)
    all_queue_items_covered = not uncovered_queue_item_ids and bool(queue_items)

    return MaterialQueueRefreshSummary(
        refresh_id="015-materials-audit-next-action-queue-refresh",
        refresh_status=(
            "covered_queue_exhausted"
            if all_queue_items_covered
            else "uncovered_queue_items_available"
        ),
        queue_item_count=len(queue_items),
        covered_queue_item_count=sum(
            1 for queue_item_id in queue_item_ids if queue_item_id in covered_id_set
        ),
        covered_queue_item_ids=[
            queue_item_id for queue_item_id in queue_item_ids if queue_item_id in covered_id_set
        ],
        uncovered_queue_item_ids=uncovered_queue_item_ids,
        legacy_next_action_ids=progress.next_action_ids,
        refreshed_next_action_ids=refreshed_next_action_ids,
        downstream_mutation_authorized=False,
        next_material_entry="015-external-material-inventory-refresh",
        boundary_checks={
            "015_queue_loaded": "passed" if queue_items else "failed",
            "016_coverage_loaded": "passed" if covered_ids else "failed",
            "covered_items_excluded": (
                "passed"
                if not set(refreshed_next_action_ids) & covered_id_set
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
    except MaterialsAuditError as error:
        return [str(error)]

    failures: list[str] = []
    for owner_id, field_name, value in _iter_quality_text_fields(
        records,
        representations,
        alignments,
        readiness,
        queue_items,
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
    return fields
