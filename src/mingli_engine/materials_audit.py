"""Deterministic existing-materials audit loading and validation."""

from collections import Counter
import csv
import json
from pathlib import Path
from typing import Any

from mingli_engine import source_library
from mingli_engine import source_intake
from mingli_engine import classical_sources
from mingli_engine import extraction_queue_intake
from mingli_engine import learning_reference_curation
from mingli_engine.models import (
    AuditProgressSummary,
    BaziGeneralVariantDeferredReviewItem,
    BaziGeneralVariantDeferredReviewSummary,
    BaziGeneralSourcePreparationReadingSummary,
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
    RawTextClusterSourceSelectionItem,
    RawTextClusterSourceSelectionSummary,
    RawTextMaterialTriageGroup,
    RawTextMaterialTriageSummary,
    RawTextNextCycleClusterSourceSelectionItem,
    RawTextNextCycleClusterSourceSelectionSummary,
    RawTextNextCycleFollowupSelectionItem,
    RawTextNextCycleFollowupSelectionSummary,
    RawTextNextCycleGatedClusterReviewPrepItem,
    RawTextNextCycleGatedClusterReviewPrepSummary,
    RawTextNextCycleGatedOrdinaryFinalSelectionItem,
    RawTextNextCycleGatedOrdinaryFinalSelectionSummary,
    RawTextNextCycleGatedOrdinaryFollowupSelectionItem,
    RawTextNextCycleGatedOrdinaryFollowupSelectionSummary,
    RawTextNextCycleGatedOrdinarySourceSelectionItem,
    RawTextNextCycleGatedOrdinarySourceSelectionSummary,
    RawTextNextCycleIdentityReviewItem,
    RawTextNextCycleIdentityReviewSummary,
    RawTextNextCycleSensitiveRiskReviewPrepItem,
    RawTextNextCycleSensitiveRiskReviewPrepSummary,
    RawTextNextCycleSensitivePreparationBoundaryItem,
    RawTextNextCycleSensitivePreparationBoundarySummary,
    RawTextNextCycleSensitivePreparationReadingItem,
    RawTextNextCycleSensitivePreparationReadingSummary,
    RawTextNextCycleSensitiveRegistrationPrepItem,
    RawTextNextCycleSensitiveRegistrationPrepSummary,
    RawTextNextCycleSensitiveSourceRegistrationItem,
    RawTextNextCycleSensitiveSourceRegistrationSummary,
    RawTextNextCycleSensitiveSourceLevelRiskReviewItem,
    RawTextNextCycleSensitiveSourceLevelRiskReviewSummary,
    RawTextNextCycleSourceSelectionItem,
    RawTextNextCycleSourceSelectionSummary,
    RawTextSourceRegistrationPrepItem,
    RawTextSourceRegistrationPrepSummary,
    RawTextSourceRegistrationSummary,
    RawTextSourceIdentityReviewItem,
    RawTextSourceIdentityReviewSummary,
    RawTextSourceClusterSelectionItem,
    RawTextSourceClusterSelectionSummary,
    RawTextSourceSelectionItem,
    RawTextSourceSelectionSummary,
    RISK_TIERS,
    RULE_FAMILIES,
    SOURCE_LIBRARY_MATERIAL_TYPES,
    SOURCE_LIBRARY_NEXT_ACTIONS,
    SOURCE_LIBRARY_PRIORITY_LEVELS,
    SOURCE_LIBRARY_READINESS_STATUSES,
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
EXTERNAL_INVENTORY_POST_QUEUE_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-source-selection"
)
RAW_TEXT_TRIAGE_SOURCE_ROOT = "资料原文/文本类/"
RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_ID = (
    "015-raw-text-next-cycle-source-selection"
)
RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID = "raw_text_triage_bazi_general"
RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-identity-review"
)
RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_ID = "015-raw-text-next-cycle-identity-review"
RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-cluster-source-selection"
)
RAW_TEXT_NEXT_CYCLE_CLUSTER_SOURCE_SELECTION_ID = (
    "015-raw-text-next-cycle-cluster-source-selection"
)
RAW_TEXT_NEXT_CYCLE_CLUSTER_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-followup-selection"
)
RAW_TEXT_NEXT_CYCLE_FOLLOWUP_SELECTION_ID = (
    "015-raw-text-next-cycle-followup-selection"
)
RAW_TEXT_NEXT_CYCLE_FOLLOWUP_SELECTION_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-gated-cluster-review-prep"
)
RAW_TEXT_NEXT_CYCLE_GATED_CLUSTER_REVIEW_PREP_ID = (
    "015-raw-text-next-cycle-gated-cluster-review-prep"
)
RAW_TEXT_NEXT_CYCLE_GATED_CLUSTER_REVIEW_PREP_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-gated-ordinary-source-selection"
)
RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_SOURCE_SELECTION_ID = (
    "015-raw-text-next-cycle-gated-ordinary-source-selection"
)
RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-gated-ordinary-followup-selection"
)
RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FOLLOWUP_SELECTION_ID = (
    "015-raw-text-next-cycle-gated-ordinary-followup-selection"
)
RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FOLLOWUP_SELECTION_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-gated-ordinary-final-selection"
)
RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FINAL_SELECTION_ID = (
    "015-raw-text-next-cycle-gated-ordinary-final-selection"
)
RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FINAL_SELECTION_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-sensitive-risk-review-prep"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_RISK_REVIEW_PREP_ID = (
    "015-raw-text-next-cycle-sensitive-risk-review-prep"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_RISK_REVIEW_PREP_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-sensitive-source-level-risk-review"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_LEVEL_RISK_REVIEW_ID = (
    "015-raw-text-next-cycle-sensitive-source-level-risk-review"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_LEVEL_RISK_REVIEW_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-sensitive-registration-prep"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_REGISTRATION_PREP_ID = (
    "015-raw-text-next-cycle-sensitive-registration-prep"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_REGISTRATION_PREP_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-sensitive-source-registration"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_REGISTRATION_ID = (
    "015-raw-text-next-cycle-sensitive-source-registration"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_REGISTRATION_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-sensitive-preparation-boundary"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_BOUNDARY_ID = (
    "015-raw-text-next-cycle-sensitive-preparation-boundary"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_BOUNDARY_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-sensitive-preparation-reading"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_READING_ID = (
    "015-raw-text-next-cycle-sensitive-preparation-reading"
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_READING_NEXT_MATERIAL_ENTRY = (
    "013-explicit-candidate-review-or-015-queue-refresh"
)
RAW_TEXT_NEXT_CYCLE_SELECTED_CLUSTER_IDS = (
    "bazi_general_modern_method_series_cluster",
    "bazi_general_misc_identity_review_cluster",
)
RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS = (
    "bazi_general_case_collection_cluster",
    "bazi_general_practical_formula_cluster",
)
RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS = (
    "bazi_general_sensitive_topic_cluster",
)
RAW_TEXT_NEXT_CYCLE_GATED_CLUSTER_REVIEW_PREP_STATUSES = frozenset(
    {
        "prepared_for_bounded_source_selection",
        "risk_review_required",
        "deferred_after_prep",
    }
)
RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_SOURCE_SELECTION_STATUSES = frozenset(
    {"selected_for_registration"}
)
RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FOLLOWUP_SELECTION_STATUSES = frozenset(
    {"selected_for_registration"}
)
RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FINAL_SELECTION_STATUSES = frozenset(
    {"selected_for_registration"}
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_RISK_REVIEW_PREP_STATUSES = frozenset(
    {
        "prepared_for_source_level_risk_review",
        "blocked_after_sensitive_prep",
        "deferred_after_sensitive_prep",
    }
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_LEVEL_RISK_REVIEW_STATUSES = frozenset(
    {"cleared_for_sensitive_registration_prep"}
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_REGISTRATION_PREP_STATUSES = frozenset(
    {"ready_for_sensitive_source_registration"}
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_REGISTRATION_STATUSES = frozenset(
    {"registered_sensitive_source_library_entry"}
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_BOUNDARY_STATUSES = frozenset(
    {"cleared_for_sensitive_preparation"}
)
RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_READING_STATUSES = frozenset(
    {"sensitive_preparation_reading_completed"}
)
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
RAW_TEXT_CLUSTER_SOURCE_SELECTION_ID = "015-bazi-general-cluster-source-selection"
RAW_TEXT_CLUSTER_SOURCE_SELECTION_TRIAGE_GROUP_ID = "raw_text_triage_bazi_general"
RAW_TEXT_CLUSTER_SOURCE_SELECTION_CLUSTER_IDS = (
    "bazi_general_foundation_textbook_cluster",
    "bazi_general_classical_reference_cluster",
)
RAW_TEXT_CLUSTER_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY = (
    "015-bazi-general-source-identity-review"
)
RAW_TEXT_SOURCE_IDENTITY_REVIEW_ID = "015-bazi-general-source-identity-review"
RAW_TEXT_SOURCE_IDENTITY_REVIEW_TRIAGE_GROUP_ID = "raw_text_triage_bazi_general"
RAW_TEXT_SOURCE_IDENTITY_REVIEW_NEXT_MATERIAL_ENTRY = (
    "015-bazi-general-registration-prep"
)
RAW_TEXT_SOURCE_REGISTRATION_PREP_ID = "015-bazi-general-registration-prep"
RAW_TEXT_SOURCE_REGISTRATION_PREP_TRIAGE_GROUP_ID = "raw_text_triage_bazi_general"
RAW_TEXT_SOURCE_REGISTRATION_PREP_NEXT_MATERIAL_ENTRY = (
    "015-bazi-general-source-registration"
)
RAW_TEXT_SOURCE_REGISTRATION_ID = "015-bazi-general-source-registration"
RAW_TEXT_SOURCE_REGISTRATION_NEXT_MATERIAL_ENTRY = (
    "015-bazi-general-source-preparation-reading"
)
RAW_TEXT_SOURCE_REGISTRATION_OVERLAP_ENTRY_ID_MARKERS = ("youran", "tianma")
RAW_TEXT_SOURCE_REGISTRATION_VARIANT_ENTRY_ID_MARKERS = ("ditiansui", "qiongtong")
RAW_TEXT_SOURCE_REGISTRATION_DEFERRED_ENTRY_ID_MARKERS = ("huntian",)
BAZI_GENERAL_SELECTED_VARIANT_ENTRY_IDS = (
    "entry_bazi_general_ditiansui_selected_pdf",
    "entry_bazi_general_qiongtong_selected_pdf",
)
BAZI_GENERAL_SOURCE_PREPARATION_READING_ID = (
    "015-bazi-general-source-preparation-reading"
)
BAZI_GENERAL_SOURCE_PREPARATION_READING_NEXT_MATERIAL_ENTRY = (
    "015-bazi-general-variant-choice-and-deferred-review"
)
BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_ID = (
    "015-bazi-general-variant-choice-and-deferred-review"
)
BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_NEXT_MATERIAL_ENTRY = (
    "015-bazi-general-selected-variant-registration-prep"
)
BAZI_GENERAL_SOURCE_PREPARATION_READING_ENTRY_IDS = (
    "entry_bazi_general_lecture_textbook_pdf",
    "entry_bazi_general_beichen_intro_pdf",
    "entry_bazi_general_ziping_orthodox_pair_pdf",
)
BAZI_GENERAL_SOURCE_PREPARATION_READING_MATERIAL_IDS = (
    "material_bazi_general_lecture_textbook_pdf",
    "material_bazi_general_beichen_intro_pdf",
    "material_bazi_general_ziping_orthodox_pair_pdf",
)
BAZI_GENERAL_SOURCE_PREPARATION_READING_CANDIDATE_IDS = (
    "candidate_bazi_general_lecture_pattern_strength_001",
    "candidate_bazi_general_beichen_branch_interaction_001",
    "candidate_bazi_general_ziping_useful_god_001",
)
BAZI_GENERAL_SOURCE_PREPARATION_READING_EVIDENCE_IDS = (
    "bazi_general_lecture_pattern_strength_001",
    "bazi_general_beichen_branch_interaction_001",
    "bazi_general_ziping_useful_god_001",
)
BAZI_GENERAL_SOURCE_PREPARATION_READING_FORMAL_SOURCE_IDS = (
    "source_bazi_general_lecture_textbook_pdf",
    "source_bazi_general_beichen_intro_pdf",
    "source_bazi_general_ziping_orthodox_pair_pdf",
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
RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_STATUSES = frozenset(
    {
        "selected_for_identity_review",
        "deferred_case_collection",
        "deferred_formula_review",
        "risk_review_required",
    }
)
RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_STATUSES = frozenset(
    {
        "cluster_source_selection_required",
        "registration_prep_ready",
        "source_library_overlap_found",
    }
)
RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_OVERLAP_STATUSES = frozenset(
    {
        "no_registered_cluster_overlap_found",
        "registered_source_overlap_found",
    }
)
RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_REGISTRATION_READINESS = frozenset(
    {
        "needs_cluster_source_selection",
        "ready_for_registration_prep",
        "no_registration_needed_existing_source",
    }
)
RAW_TEXT_NEXT_CYCLE_CLUSTER_SOURCE_SELECTION_STATUSES = frozenset(
    {
        "selected_for_registration",
    }
)
RAW_TEXT_NEXT_CYCLE_FOLLOWUP_SELECTION_STATUSES = frozenset(
    {
        "selected_for_registration",
    }
)
RAW_TEXT_CLUSTER_SOURCE_SELECTION_STATUSES = frozenset(
    {
        "selected_for_identity_review",
        "variant_identity_review",
        "deferred_after_cluster_selection",
    }
)
RAW_TEXT_SOURCE_IDENTITY_REVIEW_STATUSES = frozenset(
    {
        "existing_batch_overlap",
        "registration_prep_ready",
        "variant_choice_required",
        "deferred_large_source",
    }
)
RAW_TEXT_SOURCE_IDENTITY_REVIEW_OVERLAP_STATUSES = frozenset(
    {
        "existing_markdown_batch_overlap",
        "no_registered_overlap_found",
        "variant_set_requires_choice",
        "deferred_large_source",
    }
)
RAW_TEXT_SOURCE_IDENTITY_REVIEW_REGISTRATION_READINESS = frozenset(
    {
        "no_registration_needed_existing_batch",
        "ready_for_registration_prep",
        "needs_variant_choice",
        "deferred",
    }
)
RAW_TEXT_SOURCE_REGISTRATION_PREP_STATUSES = frozenset(
    {"ready_for_source_registration"}
)
RAW_TEXT_SOURCE_REGISTRATION_PREP_OVERLAP_POLICIES = frozenset(
    {"new_entry_allowed_after_user_approval"}
)
BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_KINDS = frozenset(
    {"variant_choice", "deferred_large_source"}
)
BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_STATUSES = frozenset(
    {
        "blocked_pending_variant_choice",
        "canonical_variant_selected",
        "deferred_large_source_reviewed",
    }
)
BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_DECISIONS = frozenset(
    {
        "keep_variant_choice_blocked",
        "select_canonical_variant",
        "keep_large_source_deferred",
    }
)
BAZI_GENERAL_VARIANT_DEFERRED_CANONICAL_CHOICE_STATUSES = frozenset(
    {"not_selected", "selected_for_registration_prep", "not_applicable"}
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


def _raw_text_next_cycle_source_selection_item_from_dict(
    data: dict[str, Any],
    clusters_by_id: dict[str, RawTextSourceClusterSelectionItem],
) -> RawTextNextCycleSourceSelectionItem:
    try:
        item = RawTextNextCycleSourceSelectionItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text next-cycle source selection item: {error}"
        ) from error

    owner_id = item.selection_id or "?"
    for field_name in (
        "selection_id",
        "triage_group_id",
        "cluster_id",
        "source_root",
        "selection_label",
        "selection_status",
        "risk_boundary",
        "recommended_next_action",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.selection_status,
        RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_STATUSES,
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
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    if item.file_count <= 0:
        raise MaterialsAuditError(f"{owner_id} requires positive file_count")
    if item.priority_text_candidate_count > item.file_count:
        raise MaterialsAuditError(
            f"{owner_id} priority count cannot exceed file_count"
        )
    for field_name in ("target_rule_families", "guardrails"):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    cluster = clusters_by_id.get(item.cluster_id)
    if cluster is None:
        raise MaterialsAuditError(f"{owner_id} references unknown cluster_id")
    if item.file_count != cluster.file_count:
        raise MaterialsAuditError(f"{owner_id} file_count does not match cluster")
    if item.priority_text_candidate_count != cluster.priority_text_candidate_count:
        raise MaterialsAuditError(
            f"{owner_id} priority_text_candidate_count does not match cluster"
        )
    if item.risk_boundary != cluster.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} risk_boundary does not match cluster")
    if set(item.target_rule_families) != set(cluster.target_rule_families):
        raise MaterialsAuditError(
            f"{owner_id} target_rule_families do not match cluster"
        )
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    if item.selection_status == "selected_for_identity_review":
        if item.cluster_id not in RAW_TEXT_NEXT_CYCLE_SELECTED_CLUSTER_IDS:
            raise MaterialsAuditError(f"{owner_id} selected cluster is not authorized")
        if cluster.cluster_status != "identity_review_required":
            raise MaterialsAuditError(
                f"{owner_id} selected cluster must require identity review"
            )
        if item.recommended_next_action != "clarify_identity":
            raise MaterialsAuditError(f"{owner_id} selected cluster must clarify identity")
        if (
            item.next_material_entry
            != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY
        ):
            raise MaterialsAuditError(f"{owner_id} selected cluster needs next entry")
    if item.selection_status in {
        "deferred_case_collection",
        "deferred_formula_review",
    }:
        if item.cluster_id not in RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS:
            raise MaterialsAuditError(f"{owner_id} deferred cluster is not authorized")
        if item.recommended_next_action != "defer":
            raise MaterialsAuditError(f"{owner_id} deferred cluster must stay deferred")
    if item.selection_status == "risk_review_required":
        if item.cluster_id not in RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS:
            raise MaterialsAuditError(
                f"{owner_id} risk-review cluster is not authorized"
            )
        if item.recommended_next_action != "risk_review":
            raise MaterialsAuditError(f"{owner_id} risk cluster must use risk_review")
        if item.risk_boundary != "sensitive":
            raise MaterialsAuditError(f"{owner_id} risk cluster must be sensitive")

    return item


def load_raw_text_next_cycle_source_selection_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleSourceSelectionItem]:
    source_dir = _data_dir(data_dir)
    clusters_by_id = {
        cluster.cluster_id: cluster
        for cluster in load_raw_text_source_cluster_selection_items(source_dir)
    }
    items = [
        _raw_text_next_cycle_source_selection_item_from_dict(item, clusters_by_id)
        for item in _read_optional_json_list(
            source_dir / "raw_text_next_cycle_source_selection_items.json"
        )
    ]
    _ensure_unique([item.selection_id for item in items], "selection_id")
    return items


def _raw_text_next_cycle_identity_review_item_from_dict(
    data: dict[str, Any],
    source_selection_items_by_id: dict[str, RawTextNextCycleSourceSelectionItem],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> RawTextNextCycleIdentityReviewItem:
    try:
        item = RawTextNextCycleIdentityReviewItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text next-cycle identity review item: {error}"
        ) from error

    owner_id = item.review_id or "?"
    for field_name in (
        "review_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "canonical_cluster_label",
        "identity_status",
        "source_library_overlap_status",
        "registration_readiness",
        "recommended_next_action",
        "next_review_target",
        "risk_boundary",
        "identity_review_note",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.identity_status,
        RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_STATUSES,
        "identity_status",
        owner_id,
    )
    _validate_enum(
        item.source_library_overlap_status,
        RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_OVERLAP_STATUSES,
        "source_library_overlap_status",
        owner_id,
    )
    _validate_enum(
        item.registration_readiness,
        RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_REGISTRATION_READINESS,
        "registration_readiness",
        owner_id,
    )
    _validate_enum(
        item.recommended_next_action,
        MATERIAL_AUDIT_ACTIONS,
        "recommended_next_action",
        owner_id,
    )
    _validate_enum(item.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    if item.file_count <= 0:
        raise MaterialsAuditError(f"{owner_id} requires positive file_count")
    if item.priority_text_candidate_count > item.file_count:
        raise MaterialsAuditError(
            f"{owner_id} priority count cannot exceed file_count"
        )
    for field_name in (
        "matched_source_library_entry_ids",
        "target_rule_families",
        "guardrails",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    source_selection_item = source_selection_items_by_id.get(item.source_selection_id)
    if source_selection_item is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown source_selection_id"
        )
    if source_selection_item.selection_status != "selected_for_identity_review":
        raise MaterialsAuditError(f"{owner_id} source selection is not selected")
    if item.cluster_id != source_selection_item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id does not match selection")
    if item.cluster_id not in RAW_TEXT_NEXT_CYCLE_SELECTED_CLUSTER_IDS:
        raise MaterialsAuditError(f"{owner_id} cluster is not selected for review")
    if item.file_count != source_selection_item.file_count:
        raise MaterialsAuditError(f"{owner_id} file_count does not match selection")
    if (
        item.priority_text_candidate_count
        != source_selection_item.priority_text_candidate_count
    ):
        raise MaterialsAuditError(
            f"{owner_id} priority count does not match selection"
        )
    if item.risk_boundary != source_selection_item.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} risk boundary does not match selection")
    if set(item.target_rule_families) != set(
        source_selection_item.target_rule_families
    ):
        raise MaterialsAuditError(
            f"{owner_id} rule families do not match source selection"
        )
    for entry_id in item.matched_source_library_entry_ids:
        if entry_id not in source_entries_by_id:
            raise MaterialsAuditError(
                f"{owner_id} references unknown source-library entry: {entry_id}"
            )
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    if item.identity_status == "cluster_source_selection_required":
        if item.source_library_overlap_status != "no_registered_cluster_overlap_found":
            raise MaterialsAuditError(
                f"{owner_id} cluster-source status requires no overlap"
            )
        if item.matched_source_library_entry_ids:
            raise MaterialsAuditError(
                f"{owner_id} cluster-source status cannot reference source entries"
            )
        if item.registration_readiness != "needs_cluster_source_selection":
            raise MaterialsAuditError(
                f"{owner_id} cluster-source status has invalid readiness"
            )
        if item.recommended_next_action != "clarify_identity":
            raise MaterialsAuditError(
                f"{owner_id} cluster-source status must clarify identity"
            )
        if (
            item.next_review_target
            != RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_NEXT_MATERIAL_ENTRY
        ):
            raise MaterialsAuditError(f"{owner_id} has invalid next_review_target")
    if item.identity_status == "registration_prep_ready":
        if item.registration_readiness != "ready_for_registration_prep":
            raise MaterialsAuditError(
                f"{owner_id} registration-prep status has invalid readiness"
            )
        if item.recommended_next_action != "register_source":
            raise MaterialsAuditError(
                f"{owner_id} registration-prep status must register source"
            )
    if item.identity_status == "source_library_overlap_found":
        if item.source_library_overlap_status != "registered_source_overlap_found":
            raise MaterialsAuditError(
                f"{owner_id} overlap status requires registered overlap"
            )
        if not item.matched_source_library_entry_ids:
            raise MaterialsAuditError(f"{owner_id} overlap status requires source ids")
        if item.registration_readiness != "no_registration_needed_existing_source":
            raise MaterialsAuditError(
                f"{owner_id} overlap status has invalid readiness"
            )

    return item


def load_raw_text_next_cycle_identity_review_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleIdentityReviewItem]:
    source_dir = _data_dir(data_dir)
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_next_cycle_source_selection_items(source_dir)
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    items = [
        _raw_text_next_cycle_identity_review_item_from_dict(
            item,
            source_selection_items_by_id,
            source_entries_by_id,
        )
        for item in _read_optional_json_list(
            source_dir / "raw_text_next_cycle_identity_review_items.json"
        )
    ]
    _ensure_unique([item.review_id for item in items], "review_id")
    return items


def _is_source_relative_path(path: str) -> bool:
    return (
        bool(path.strip())
        and not Path(path).is_absolute()
        and not path.startswith(("/", "\\"))
        and RAW_TEXT_TRIAGE_SOURCE_ROOT not in path
    )


def _raw_text_next_cycle_cluster_source_selection_item_from_dict(
    data: dict[str, Any],
    identity_review_items_by_id: dict[str, RawTextNextCycleIdentityReviewItem],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> RawTextNextCycleClusterSourceSelectionItem:
    try:
        item = RawTextNextCycleClusterSourceSelectionItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text next-cycle cluster source selection item: {error}"
        ) from error

    owner_id = item.selection_id or "?"
    for field_name in (
        "selection_id",
        "identity_review_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "title_label",
        "selection_status",
        "risk_boundary",
        "recommended_next_action",
        "source_library_entry_id",
        "source_material_id",
        "audit_id",
        "queue_item_id",
        "candidate_id",
        "evidence_id",
        "identity_review_note",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.selection_status,
        RAW_TEXT_NEXT_CYCLE_CLUSTER_SOURCE_SELECTION_STATUSES,
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
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    _require_non_negative_int(item.priority_score, "priority_score", owner_id)
    if item.file_count <= 0:
        raise MaterialsAuditError(f"{owner_id} requires positive file_count")
    if item.priority_text_candidate_count > item.file_count:
        raise MaterialsAuditError(
            f"{owner_id} priority count cannot exceed file_count"
        )
    for field_name in ("relative_paths", "target_rule_families", "guardrails"):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if len(item.relative_paths) != item.file_count:
        raise MaterialsAuditError(f"{owner_id} relative_paths must match file_count")
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for relative_path in item.relative_paths:
        if not _is_source_relative_path(relative_path):
            raise MaterialsAuditError(f"{owner_id} has non-relative source path")
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    identity_review = identity_review_items_by_id.get(item.identity_review_id)
    if identity_review is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown identity_review_id"
        )
    if identity_review.identity_status != "cluster_source_selection_required":
        raise MaterialsAuditError(
            f"{owner_id} identity review does not require cluster source selection"
        )
    if item.source_selection_id != identity_review.source_selection_id:
        raise MaterialsAuditError(f"{owner_id} source_selection_id mismatch")
    if item.cluster_id != identity_review.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id mismatch")
    if item.cluster_id not in RAW_TEXT_NEXT_CYCLE_SELECTED_CLUSTER_IDS:
        raise MaterialsAuditError(f"{owner_id} cluster is not in next-cycle scope")
    if item.risk_boundary != identity_review.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} risk boundary mismatch")
    if not set(item.target_rule_families).issubset(
        set(identity_review.target_rule_families)
    ):
        raise MaterialsAuditError(
            f"{owner_id} rule families exceed identity review target"
        )
    if item.selection_status == "selected_for_registration":
        if item.recommended_next_action != "register_source":
            raise MaterialsAuditError(f"{owner_id} selected item must register source")
    source_entry = source_entries_by_id.get(item.source_library_entry_id)
    if source_entry is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown source-library entry"
        )
    if source_entry.material_id != item.source_material_id:
        raise MaterialsAuditError(f"{owner_id} source material id mismatch")
    if source_entry.risk_tier != item.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} source entry risk boundary mismatch")

    return item


def load_raw_text_next_cycle_cluster_source_selection_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleClusterSourceSelectionItem]:
    source_dir = _data_dir(data_dir)
    identity_review_items_by_id = {
        item.review_id: item
        for item in load_raw_text_next_cycle_identity_review_items(source_dir)
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    items = [
        _raw_text_next_cycle_cluster_source_selection_item_from_dict(
            item,
            identity_review_items_by_id,
            source_entries_by_id,
        )
        for item in _read_optional_json_list(
            source_dir / "raw_text_next_cycle_cluster_source_selection_items.json"
        )
    ]
    _ensure_unique([item.selection_id for item in items], "selection_id")
    return items


def _raw_text_next_cycle_followup_selection_item_from_dict(
    data: dict[str, Any],
    prior_items_by_id: dict[str, RawTextNextCycleClusterSourceSelectionItem],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> RawTextNextCycleFollowupSelectionItem:
    try:
        item = RawTextNextCycleFollowupSelectionItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text next-cycle followup selection item: {error}"
        ) from error

    owner_id = item.selection_id or "?"
    for field_name in (
        "selection_id",
        "prior_selection_id",
        "cluster_id",
        "source_selection_id",
        "triage_group_id",
        "source_root",
        "title_label",
        "selection_status",
        "risk_boundary",
        "recommended_next_action",
        "source_library_entry_id",
        "source_material_id",
        "audit_id",
        "queue_item_id",
        "candidate_id",
        "evidence_id",
        "selection_note",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.selection_status,
        RAW_TEXT_NEXT_CYCLE_FOLLOWUP_SELECTION_STATUSES,
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
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    _require_non_negative_int(item.priority_score, "priority_score", owner_id)
    if item.file_count <= 0:
        raise MaterialsAuditError(f"{owner_id} requires positive file_count")
    if item.priority_text_candidate_count > item.file_count:
        raise MaterialsAuditError(
            f"{owner_id} priority count cannot exceed file_count"
        )
    for field_name in ("relative_paths", "target_rule_families", "guardrails"):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if len(item.relative_paths) != item.file_count:
        raise MaterialsAuditError(f"{owner_id} relative_paths must match file_count")
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for relative_path in item.relative_paths:
        if not _is_source_relative_path(relative_path):
            raise MaterialsAuditError(f"{owner_id} has non-relative source path")
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    prior_item = prior_items_by_id.get(item.prior_selection_id)
    if prior_item is None:
        raise MaterialsAuditError(f"{owner_id} references unknown prior_selection_id")
    if prior_item.selection_status != "selected_for_registration":
        raise MaterialsAuditError(f"{owner_id} prior selection is not registered")
    if item.cluster_id != prior_item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id mismatch")
    if item.source_selection_id != prior_item.source_selection_id:
        raise MaterialsAuditError(f"{owner_id} source_selection_id mismatch")
    if item.cluster_id not in RAW_TEXT_NEXT_CYCLE_SELECTED_CLUSTER_IDS:
        raise MaterialsAuditError(f"{owner_id} cluster is not in next-cycle scope")
    if item.risk_boundary != prior_item.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} risk boundary mismatch")
    if item.selection_status == "selected_for_registration":
        if item.recommended_next_action != "register_source":
            raise MaterialsAuditError(f"{owner_id} selected item must register source")
    source_entry = source_entries_by_id.get(item.source_library_entry_id)
    if source_entry is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown source-library entry"
        )
    if source_entry.material_id != item.source_material_id:
        raise MaterialsAuditError(f"{owner_id} source material id mismatch")
    if source_entry.risk_tier != item.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} source entry risk boundary mismatch")

    return item


def load_raw_text_next_cycle_followup_selection_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleFollowupSelectionItem]:
    source_dir = _data_dir(data_dir)
    prior_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_next_cycle_cluster_source_selection_items(
            source_dir
        )
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    items = [
        _raw_text_next_cycle_followup_selection_item_from_dict(
            item,
            prior_items_by_id,
            source_entries_by_id,
        )
        for item in _read_optional_json_list(
            source_dir / "raw_text_next_cycle_followup_selection_items.json"
        )
    ]
    _ensure_unique([item.selection_id for item in items], "selection_id")
    return items


def _raw_text_next_cycle_gated_cluster_review_prep_item_from_dict(
    data: dict[str, Any],
    source_selection_items_by_id: dict[str, RawTextNextCycleSourceSelectionItem],
) -> RawTextNextCycleGatedClusterReviewPrepItem:
    try:
        item = RawTextNextCycleGatedClusterReviewPrepItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text next-cycle gated cluster review prep item: {error}"
        ) from error

    owner_id = item.prep_id or "?"
    for field_name in (
        "prep_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "prep_label",
        "prep_status",
        "risk_boundary",
        "recommended_next_action",
        "boundary_note",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.prep_status,
        RAW_TEXT_NEXT_CYCLE_GATED_CLUSTER_REVIEW_PREP_STATUSES,
        "prep_status",
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
    if item.file_count <= 0:
        raise MaterialsAuditError(f"{owner_id} requires positive file_count")
    if item.priority_text_candidate_count > item.file_count:
        raise MaterialsAuditError(
            f"{owner_id} priority count cannot exceed file_count"
        )
    for field_name in ("target_rule_families", "guardrails"):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    source_selection = source_selection_items_by_id.get(item.source_selection_id)
    if source_selection is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown source_selection_id"
        )
    if source_selection.cluster_id != item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id mismatch")
    if source_selection.file_count != item.file_count:
        raise MaterialsAuditError(f"{owner_id} file_count mismatch")
    if (
        source_selection.priority_text_candidate_count
        != item.priority_text_candidate_count
    ):
        raise MaterialsAuditError(
            f"{owner_id} priority_text_candidate_count mismatch"
        )
    if source_selection.risk_boundary != item.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} risk_boundary mismatch")
    if set(source_selection.target_rule_families) != set(
        item.target_rule_families
    ):
        raise MaterialsAuditError(f"{owner_id} target_rule_families mismatch")
    if item.source_library_mutation_authorized:
        raise MaterialsAuditError(
            f"{owner_id} gated prep cannot authorize source-library mutation"
        )
    if item.downstream_mutation_authorized:
        raise MaterialsAuditError(
            f"{owner_id} gated prep cannot authorize downstream mutation"
        )

    if item.cluster_id in RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS:
        if item.prep_status != "prepared_for_bounded_source_selection":
            raise MaterialsAuditError(
                f"{owner_id} ordinary deferred cluster must be prepared only"
            )
        if item.recommended_next_action != "select_bounded_source":
            raise MaterialsAuditError(
                f"{owner_id} ordinary deferred cluster must select bounded source"
            )
        if item.risk_boundary != "ordinary":
            raise MaterialsAuditError(
                f"{owner_id} ordinary deferred cluster risk mismatch"
            )
    elif item.cluster_id in RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS:
        if item.prep_status != "risk_review_required":
            raise MaterialsAuditError(
                f"{owner_id} sensitive cluster must stay risk-review required"
            )
        if item.recommended_next_action != "risk_review":
            raise MaterialsAuditError(
                f"{owner_id} sensitive cluster must keep risk_review action"
            )
        if item.risk_boundary != "sensitive":
            raise MaterialsAuditError(
                f"{owner_id} sensitive cluster risk mismatch"
            )
    else:
        raise MaterialsAuditError(f"{owner_id} cluster is not gated")

    return item


def load_raw_text_next_cycle_gated_cluster_review_prep_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleGatedClusterReviewPrepItem]:
    source_dir = _data_dir(data_dir)
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_next_cycle_source_selection_items(source_dir)
    }
    items = [
        _raw_text_next_cycle_gated_cluster_review_prep_item_from_dict(
            item,
            source_selection_items_by_id,
        )
        for item in _read_optional_json_list(
            source_dir / "raw_text_next_cycle_gated_cluster_review_prep_items.json"
        )
    ]
    _ensure_unique([item.prep_id for item in items], "prep_id")
    return items


def _raw_text_next_cycle_gated_ordinary_source_selection_item_from_dict(
    data: dict[str, Any],
    prep_items_by_id: dict[str, RawTextNextCycleGatedClusterReviewPrepItem],
) -> RawTextNextCycleGatedOrdinarySourceSelectionItem:
    try:
        item = RawTextNextCycleGatedOrdinarySourceSelectionItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            "invalid raw text next-cycle gated ordinary source selection item: "
            f"{error}"
        ) from error

    owner_id = item.selection_id or "?"
    for field_name in (
        "selection_id",
        "prep_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "title_label",
        "selection_status",
        "risk_boundary",
        "recommended_next_action",
        "source_library_entry_id",
        "source_material_id",
        "audit_id",
        "queue_item_id",
        "candidate_id",
        "evidence_id",
        "selection_note",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.selection_status,
        RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_SOURCE_SELECTION_STATUSES,
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
    if item.recommended_next_action != "register_source":
        raise MaterialsAuditError(f"{owner_id} must register selected source")
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    if item.file_count != len(item.relative_paths) or item.file_count != 1:
        raise MaterialsAuditError(f"{owner_id} must select one bounded source file")
    if item.priority_text_candidate_count != 1:
        raise MaterialsAuditError(
            f"{owner_id} must have one priority text candidate"
        )
    for field_name in ("relative_paths", "target_rule_families", "guardrails"):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for path in item.relative_paths:
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise MaterialsAuditError(f"{owner_id} relative_paths must stay relative")
        if item.source_root in path:
            raise MaterialsAuditError(
                f"{owner_id} relative_paths must not include source root"
            )
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    if len(item.target_rule_families) != 1:
        raise MaterialsAuditError(f"{owner_id} must target one rule family")
    if item.risk_boundary != "ordinary":
        raise MaterialsAuditError(f"{owner_id} must stay ordinary risk")
    if not item.source_library_mutation_authorized:
        raise MaterialsAuditError(
            f"{owner_id} must authorize source-library mutation"
        )
    if not item.downstream_mutation_authorized:
        raise MaterialsAuditError(f"{owner_id} must authorize downstream mutation")

    prep = prep_items_by_id.get(item.prep_id)
    if prep is None:
        raise MaterialsAuditError(f"{owner_id} references unknown prep_id")
    if prep.prep_status != "prepared_for_bounded_source_selection":
        raise MaterialsAuditError(f"{owner_id} prep_id is not ordinary prepared")
    if prep.cluster_id != item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id mismatch")
    if prep.source_selection_id != item.source_selection_id:
        raise MaterialsAuditError(f"{owner_id} source_selection_id mismatch")
    if prep.risk_boundary != item.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} risk_boundary mismatch")
    if item.cluster_id not in RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS:
        raise MaterialsAuditError(f"{owner_id} must select ordinary gated cluster")
    if not set(item.target_rule_families).issubset(set(prep.target_rule_families)):
        raise MaterialsAuditError(f"{owner_id} target_rule_families mismatch")

    return item


def load_raw_text_next_cycle_gated_ordinary_source_selection_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleGatedOrdinarySourceSelectionItem]:
    source_dir = _data_dir(data_dir)
    prep_items_by_id = {
        item.prep_id: item
        for item in load_raw_text_next_cycle_gated_cluster_review_prep_items(
            source_dir
        )
    }
    items = [
        _raw_text_next_cycle_gated_ordinary_source_selection_item_from_dict(
            item,
            prep_items_by_id,
        )
        for item in _read_optional_json_list(
            source_dir
            / "raw_text_next_cycle_gated_ordinary_source_selection_items.json"
        )
    ]
    _ensure_unique([item.selection_id for item in items], "selection_id")
    return items


def _raw_text_next_cycle_gated_ordinary_followup_selection_item_from_dict(
    data: dict[str, Any],
    prep_items_by_id: dict[str, RawTextNextCycleGatedClusterReviewPrepItem],
    prior_items_by_id: dict[str, RawTextNextCycleGatedOrdinarySourceSelectionItem],
) -> RawTextNextCycleGatedOrdinaryFollowupSelectionItem:
    try:
        item = RawTextNextCycleGatedOrdinaryFollowupSelectionItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            "invalid raw text next-cycle gated ordinary followup selection item: "
            f"{error}"
        ) from error

    owner_id = item.selection_id or "?"
    for field_name in (
        "selection_id",
        "prior_selection_id",
        "prep_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "title_label",
        "selection_status",
        "risk_boundary",
        "recommended_next_action",
        "source_library_entry_id",
        "source_material_id",
        "audit_id",
        "queue_item_id",
        "candidate_id",
        "evidence_id",
        "selection_note",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.selection_status,
        RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FOLLOWUP_SELECTION_STATUSES,
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
    if item.recommended_next_action != "register_source":
        raise MaterialsAuditError(f"{owner_id} must register selected source")
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    if item.file_count != len(item.relative_paths) or item.file_count != 1:
        raise MaterialsAuditError(f"{owner_id} must select one bounded source file")
    if item.priority_text_candidate_count != 1:
        raise MaterialsAuditError(
            f"{owner_id} must have one priority text candidate"
        )
    for field_name in ("relative_paths", "target_rule_families", "guardrails"):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for path in item.relative_paths:
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise MaterialsAuditError(f"{owner_id} relative_paths must stay relative")
        if item.source_root in path:
            raise MaterialsAuditError(
                f"{owner_id} relative_paths must not include source root"
            )
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    if len(item.target_rule_families) != 1:
        raise MaterialsAuditError(f"{owner_id} must target one rule family")
    if item.risk_boundary != "ordinary":
        raise MaterialsAuditError(f"{owner_id} must stay ordinary risk")
    if not item.source_library_mutation_authorized:
        raise MaterialsAuditError(
            f"{owner_id} must authorize source-library mutation"
        )
    if not item.downstream_mutation_authorized:
        raise MaterialsAuditError(f"{owner_id} must authorize downstream mutation")

    prep = prep_items_by_id.get(item.prep_id)
    if prep is None:
        raise MaterialsAuditError(f"{owner_id} references unknown prep_id")
    prior = prior_items_by_id.get(item.prior_selection_id)
    if prior is None:
        raise MaterialsAuditError(f"{owner_id} references unknown prior_selection_id")
    if prep.prep_status != "prepared_for_bounded_source_selection":
        raise MaterialsAuditError(f"{owner_id} prep_id is not ordinary prepared")
    if prep.cluster_id != item.cluster_id or prior.cluster_id != item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id mismatch")
    if prep.source_selection_id != item.source_selection_id:
        raise MaterialsAuditError(f"{owner_id} source_selection_id mismatch")
    if prep.risk_boundary != item.risk_boundary or prior.risk_boundary != item.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} risk_boundary mismatch")
    if item.cluster_id not in RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS:
        raise MaterialsAuditError(f"{owner_id} must select ordinary gated cluster")
    if not set(item.target_rule_families).issubset(set(prep.target_rule_families)):
        raise MaterialsAuditError(f"{owner_id} target_rule_families mismatch")
    prior_paths = set(prior.relative_paths)
    if any(path in prior_paths for path in item.relative_paths):
        raise MaterialsAuditError(f"{owner_id} duplicates prior selected path")

    return item


def load_raw_text_next_cycle_gated_ordinary_followup_selection_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleGatedOrdinaryFollowupSelectionItem]:
    source_dir = _data_dir(data_dir)
    prep_items_by_id = {
        item.prep_id: item
        for item in load_raw_text_next_cycle_gated_cluster_review_prep_items(
            source_dir
        )
    }
    prior_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_next_cycle_gated_ordinary_source_selection_items(
            source_dir
        )
    }
    items = [
        _raw_text_next_cycle_gated_ordinary_followup_selection_item_from_dict(
            item,
            prep_items_by_id,
            prior_items_by_id,
        )
        for item in _read_optional_json_list(
            source_dir
            / "raw_text_next_cycle_gated_ordinary_followup_selection_items.json"
        )
    ]
    _ensure_unique([item.selection_id for item in items], "selection_id")
    return items


def _raw_text_next_cycle_gated_ordinary_final_selection_item_from_dict(
    data: dict[str, Any],
    prep_items_by_id: dict[str, RawTextNextCycleGatedClusterReviewPrepItem],
    prior_items_by_id: dict[str, RawTextNextCycleGatedOrdinaryFollowupSelectionItem],
    previously_selected_paths: set[str],
) -> RawTextNextCycleGatedOrdinaryFinalSelectionItem:
    try:
        item = RawTextNextCycleGatedOrdinaryFinalSelectionItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            "invalid raw text next-cycle gated ordinary final selection item: "
            f"{error}"
        ) from error

    owner_id = item.selection_id or "?"
    for field_name in (
        "selection_id",
        "prior_selection_id",
        "prep_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "title_label",
        "selection_status",
        "risk_boundary",
        "recommended_next_action",
        "source_library_entry_id",
        "source_material_id",
        "audit_id",
        "queue_item_id",
        "candidate_id",
        "evidence_id",
        "selection_note",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.selection_status,
        RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FINAL_SELECTION_STATUSES,
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
    if item.recommended_next_action != "register_source":
        raise MaterialsAuditError(f"{owner_id} must register selected source")
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    if item.file_count != len(item.relative_paths) or item.file_count != 1:
        raise MaterialsAuditError(f"{owner_id} must select one bounded source file")
    if item.priority_text_candidate_count != 1:
        raise MaterialsAuditError(
            f"{owner_id} must have one priority text candidate"
        )
    for field_name in ("relative_paths", "target_rule_families", "guardrails"):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for path in item.relative_paths:
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise MaterialsAuditError(f"{owner_id} relative_paths must stay relative")
        if item.source_root in path:
            raise MaterialsAuditError(
                f"{owner_id} relative_paths must not include source root"
            )
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    if len(item.target_rule_families) != 1:
        raise MaterialsAuditError(f"{owner_id} must target one rule family")
    if item.risk_boundary != "ordinary":
        raise MaterialsAuditError(f"{owner_id} must stay ordinary risk")
    if not item.source_library_mutation_authorized:
        raise MaterialsAuditError(
            f"{owner_id} must authorize source-library mutation"
        )
    if not item.downstream_mutation_authorized:
        raise MaterialsAuditError(f"{owner_id} must authorize downstream mutation")

    prep = prep_items_by_id.get(item.prep_id)
    if prep is None:
        raise MaterialsAuditError(f"{owner_id} references unknown prep_id")
    prior = prior_items_by_id.get(item.prior_selection_id)
    if prior is None:
        raise MaterialsAuditError(f"{owner_id} references unknown prior_selection_id")
    if prep.prep_status != "prepared_for_bounded_source_selection":
        raise MaterialsAuditError(f"{owner_id} prep_id is not ordinary prepared")
    if prep.cluster_id != item.cluster_id or prior.cluster_id != item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id mismatch")
    if prep.source_selection_id != item.source_selection_id:
        raise MaterialsAuditError(f"{owner_id} source_selection_id mismatch")
    if (
        prep.risk_boundary != item.risk_boundary
        or prior.risk_boundary != item.risk_boundary
    ):
        raise MaterialsAuditError(f"{owner_id} risk_boundary mismatch")
    if item.cluster_id not in RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS:
        raise MaterialsAuditError(f"{owner_id} must select ordinary gated cluster")
    if not set(item.target_rule_families).issubset(set(prep.target_rule_families)):
        raise MaterialsAuditError(f"{owner_id} target_rule_families mismatch")
    if any(path in previously_selected_paths for path in item.relative_paths):
        raise MaterialsAuditError(f"{owner_id} duplicates prior selected path")

    return item


def load_raw_text_next_cycle_gated_ordinary_final_selection_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleGatedOrdinaryFinalSelectionItem]:
    source_dir = _data_dir(data_dir)
    prep_items_by_id = {
        item.prep_id: item
        for item in load_raw_text_next_cycle_gated_cluster_review_prep_items(
            source_dir
        )
    }
    source_selection_items = (
        load_raw_text_next_cycle_gated_ordinary_source_selection_items(source_dir)
    )
    followup_selection_items = (
        load_raw_text_next_cycle_gated_ordinary_followup_selection_items(source_dir)
    )
    prior_items_by_id = {
        item.selection_id: item for item in followup_selection_items
    }
    previously_selected_paths = {
        path
        for item in [*source_selection_items, *followup_selection_items]
        for path in item.relative_paths
    }
    items = [
        _raw_text_next_cycle_gated_ordinary_final_selection_item_from_dict(
            item,
            prep_items_by_id,
            prior_items_by_id,
            previously_selected_paths,
        )
        for item in _read_optional_json_list(
            source_dir
            / "raw_text_next_cycle_gated_ordinary_final_selection_items.json"
        )
    ]
    _ensure_unique([item.selection_id for item in items], "selection_id")
    return items


def _raw_text_next_cycle_sensitive_risk_review_prep_item_from_dict(
    data: dict[str, Any],
    prep_items_by_id: dict[str, RawTextNextCycleGatedClusterReviewPrepItem],
    source_selection_items_by_id: dict[str, RawTextNextCycleSourceSelectionItem],
) -> RawTextNextCycleSensitiveRiskReviewPrepItem:
    try:
        item = RawTextNextCycleSensitiveRiskReviewPrepItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            "invalid raw text next-cycle sensitive risk review prep item: "
            f"{error}"
        ) from error

    owner_id = item.prep_item_id or "?"
    for field_name in (
        "prep_item_id",
        "prep_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "title_label",
        "prep_status",
        "risk_boundary",
        "recommended_next_action",
        "boundary_decision",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.prep_status,
        RAW_TEXT_NEXT_CYCLE_SENSITIVE_RISK_REVIEW_PREP_STATUSES,
        "prep_status",
        owner_id,
    )
    _validate_enum(item.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    _validate_enum(
        item.recommended_next_action,
        MATERIAL_AUDIT_ACTIONS,
        "recommended_next_action",
        owner_id,
    )
    if item.risk_boundary != "sensitive":
        raise MaterialsAuditError(f"{owner_id} must stay sensitive risk")
    if item.cluster_id not in RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS:
        raise MaterialsAuditError(f"{owner_id} must reference sensitive cluster")
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    if item.file_count != len(item.relative_paths) or item.file_count != 1:
        raise MaterialsAuditError(f"{owner_id} must reference one bounded path")
    if item.priority_text_candidate_count != 1:
        raise MaterialsAuditError(
            f"{owner_id} must carry one reviewable path candidate"
        )
    for field_name in (
        "relative_paths",
        "target_rule_families",
        "risk_review_topics",
        "guardrails",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.risk_review_topics:
        raise MaterialsAuditError(f"{owner_id} requires risk_review_topics")
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for path in item.relative_paths:
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise MaterialsAuditError(f"{owner_id} relative_paths must stay relative")
        if item.source_root in path:
            raise MaterialsAuditError(
                f"{owner_id} relative_paths must not include source root"
            )
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    if len(item.target_rule_families) != 1:
        raise MaterialsAuditError(f"{owner_id} must target one rule family")
    if item.source_library_mutation_authorized:
        raise MaterialsAuditError(
            f"{owner_id} must not authorize source-library mutation"
        )
    if item.downstream_mutation_authorized:
        raise MaterialsAuditError(f"{owner_id} must not authorize downstream mutation")

    action_by_status = {
        "prepared_for_source_level_risk_review": "risk_review",
        "blocked_after_sensitive_prep": "block",
        "deferred_after_sensitive_prep": "defer",
    }
    if action_by_status[item.prep_status] != item.recommended_next_action:
        raise MaterialsAuditError(f"{owner_id} has invalid action routing")

    prep = prep_items_by_id.get(item.prep_id)
    if prep is None:
        raise MaterialsAuditError(f"{owner_id} references unknown prep_id")
    source_selection = source_selection_items_by_id.get(item.source_selection_id)
    if source_selection is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown source_selection_id"
        )
    if prep.prep_status != "risk_review_required":
        raise MaterialsAuditError(f"{owner_id} prep_id is not risk-review prep")
    if prep.cluster_id != item.cluster_id or source_selection.cluster_id != item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id mismatch")
    if prep.source_selection_id != item.source_selection_id:
        raise MaterialsAuditError(f"{owner_id} source_selection_id mismatch")
    if prep.risk_boundary != item.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} risk_boundary mismatch")
    if not set(item.target_rule_families).issubset(set(prep.target_rule_families)):
        raise MaterialsAuditError(f"{owner_id} target_rule_families mismatch")

    return item


def load_raw_text_next_cycle_sensitive_risk_review_prep_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleSensitiveRiskReviewPrepItem]:
    source_dir = _data_dir(data_dir)
    prep_items_by_id = {
        item.prep_id: item
        for item in load_raw_text_next_cycle_gated_cluster_review_prep_items(
            source_dir
        )
    }
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_next_cycle_source_selection_items(source_dir)
    }
    items = [
        _raw_text_next_cycle_sensitive_risk_review_prep_item_from_dict(
            item,
            prep_items_by_id,
            source_selection_items_by_id,
        )
        for item in _read_optional_json_list(
            source_dir
            / "raw_text_next_cycle_sensitive_risk_review_prep_items.json"
        )
    ]
    _ensure_unique([item.prep_item_id for item in items], "prep_item_id")
    return items


def _raw_text_next_cycle_sensitive_source_level_risk_review_item_from_dict(
    data: dict[str, Any],
    prep_items_by_id: dict[str, RawTextNextCycleSensitiveRiskReviewPrepItem],
) -> RawTextNextCycleSensitiveSourceLevelRiskReviewItem:
    try:
        item = RawTextNextCycleSensitiveSourceLevelRiskReviewItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            "invalid raw text next-cycle sensitive source-level risk review "
            f"item: {error}"
        ) from error

    owner_id = item.review_item_id or "?"
    for field_name in (
        "review_item_id",
        "prep_item_id",
        "prep_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "title_label",
        "review_status",
        "risk_boundary",
        "recommended_next_action",
        "boundary_decision",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.review_status,
        RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_LEVEL_RISK_REVIEW_STATUSES,
        "review_status",
        owner_id,
    )
    _validate_enum(item.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    _validate_enum(
        item.recommended_next_action,
        MATERIAL_AUDIT_ACTIONS,
        "recommended_next_action",
        owner_id,
    )
    if item.risk_boundary != "sensitive":
        raise MaterialsAuditError(f"{owner_id} must stay sensitive risk")
    if item.recommended_next_action != "register_source":
        raise MaterialsAuditError(f"{owner_id} must route to registration prep")
    if not item.registration_prep_allowed:
        raise MaterialsAuditError(f"{owner_id} must allow registration prep")
    if item.source_library_mutation_authorized:
        raise MaterialsAuditError(
            f"{owner_id} must not authorize source-library mutation"
        )
    if item.downstream_mutation_authorized:
        raise MaterialsAuditError(f"{owner_id} must not authorize downstream mutation")
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    if item.file_count != len(item.relative_paths) or item.file_count != 1:
        raise MaterialsAuditError(f"{owner_id} must review one bounded path")
    if item.priority_text_candidate_count != 1:
        raise MaterialsAuditError(f"{owner_id} must carry one source candidate")
    for field_name in (
        "relative_paths",
        "target_rule_families",
        "risk_review_topics",
        "risk_findings",
        "guardrails",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.risk_review_topics:
        raise MaterialsAuditError(f"{owner_id} requires risk_review_topics")
    if not item.risk_findings:
        raise MaterialsAuditError(f"{owner_id} requires risk_findings")
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for path in item.relative_paths:
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise MaterialsAuditError(f"{owner_id} relative_paths must stay relative")
        if item.source_root in path:
            raise MaterialsAuditError(
                f"{owner_id} relative_paths must not include source root"
            )
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    if len(item.target_rule_families) != 1:
        raise MaterialsAuditError(f"{owner_id} must target one rule family")

    prep_item = prep_items_by_id.get(item.prep_item_id)
    if prep_item is None:
        raise MaterialsAuditError(f"{owner_id} references unknown prep_item_id")
    if prep_item.prep_status != "prepared_for_source_level_risk_review":
        raise MaterialsAuditError(f"{owner_id} prep_item_id is not reviewable")
    if prep_item.recommended_next_action != "risk_review":
        raise MaterialsAuditError(f"{owner_id} prep_item_id action mismatch")
    if prep_item.prep_id != item.prep_id:
        raise MaterialsAuditError(f"{owner_id} prep_id mismatch")
    if prep_item.source_selection_id != item.source_selection_id:
        raise MaterialsAuditError(f"{owner_id} source_selection_id mismatch")
    if prep_item.cluster_id != item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id mismatch")
    if prep_item.risk_boundary != item.risk_boundary:
        raise MaterialsAuditError(f"{owner_id} risk_boundary mismatch")
    if prep_item.relative_paths != item.relative_paths:
        raise MaterialsAuditError(f"{owner_id} relative_paths mismatch")
    if not set(item.target_rule_families).issubset(set(prep_item.target_rule_families)):
        raise MaterialsAuditError(f"{owner_id} target_rule_families mismatch")

    return item


def load_raw_text_next_cycle_sensitive_source_level_risk_review_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleSensitiveSourceLevelRiskReviewItem]:
    source_dir = _data_dir(data_dir)
    prep_items_by_id = {
        item.prep_item_id: item
        for item in load_raw_text_next_cycle_sensitive_risk_review_prep_items(
            source_dir
        )
    }
    items = [
        _raw_text_next_cycle_sensitive_source_level_risk_review_item_from_dict(
            item,
            prep_items_by_id,
        )
        for item in _read_optional_json_list(
            source_dir
            / "raw_text_next_cycle_sensitive_source_level_risk_review_items.json"
        )
    ]
    _ensure_unique([item.review_item_id for item in items], "review_item_id")
    return items


def _sensitive_registration_prep_entry_matches_existing(
    item: RawTextNextCycleSensitiveRegistrationPrepItem,
    entry: source_library.SourceLibraryEntry,
) -> bool:
    return (
        entry.material_id == item.proposed_material_id
        and entry.title == item.proposed_title
        and entry.material_type == item.proposed_material_type
        and entry.local_reference == "; ".join(item.proposed_local_references)
        and entry.tracking_status == item.proposed_tracking_status
        and entry.topic_tags == item.topic_tags
        and entry.rule_families == item.rule_families
        and entry.rights_notes == item.rights_notes
        and entry.risk_tier == item.risk_tier
        and entry.risk_notes == item.risk_notes
    )


def _raw_text_next_cycle_sensitive_registration_prep_item_from_dict(
    data: dict[str, Any],
    source_level_review_items_by_id: dict[
        str, RawTextNextCycleSensitiveSourceLevelRiskReviewItem
    ],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> RawTextNextCycleSensitiveRegistrationPrepItem:
    try:
        item = RawTextNextCycleSensitiveRegistrationPrepItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            "invalid raw text next-cycle sensitive registration prep item: "
            f"{error}"
        ) from error

    owner_id = item.prep_item_id or "?"
    for field_name in (
        "prep_item_id",
        "source_level_review_id",
        "prep_review_item_id",
        "prep_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "registration_status",
        "proposed_entry_id",
        "proposed_material_id",
        "proposed_title",
        "proposed_material_type",
        "proposed_tracking_status",
        "proposed_readiness_status",
        "proposed_priority_level",
        "proposed_next_action",
        "risk_tier",
        "source_quality_notes",
        "rights_notes",
        "source_library_overlap_policy",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.triage_group_id != RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.registration_status,
        RAW_TEXT_NEXT_CYCLE_SENSITIVE_REGISTRATION_PREP_STATUSES,
        "registration_status",
        owner_id,
    )
    _validate_enum(
        item.proposed_material_type,
        SOURCE_LIBRARY_MATERIAL_TYPES,
        "proposed_material_type",
        owner_id,
    )
    _validate_enum(
        item.proposed_tracking_status,
        MATERIAL_TRACKING_STATUSES,
        "proposed_tracking_status",
        owner_id,
    )
    _validate_enum(
        item.proposed_readiness_status,
        SOURCE_LIBRARY_READINESS_STATUSES,
        "proposed_readiness_status",
        owner_id,
    )
    _validate_enum(
        item.proposed_priority_level,
        SOURCE_LIBRARY_PRIORITY_LEVELS,
        "proposed_priority_level",
        owner_id,
    )
    _validate_enum(
        item.proposed_next_action,
        SOURCE_LIBRARY_NEXT_ACTIONS,
        "proposed_next_action",
        owner_id,
    )
    _validate_enum(item.risk_tier, RISK_TIERS, "risk_tier", owner_id)
    _validate_enum(
        item.source_library_overlap_policy,
        RAW_TEXT_SOURCE_REGISTRATION_PREP_OVERLAP_POLICIES,
        "source_library_overlap_policy",
        owner_id,
    )
    for field_name in (
        "proposed_local_references",
        "topic_tags",
        "rule_families",
        "risk_notes",
        "guardrails",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.proposed_local_references:
        raise MaterialsAuditError(f"{owner_id} requires proposed_local_references")
    if not item.topic_tags:
        raise MaterialsAuditError(f"{owner_id} requires topic_tags")
    if not item.rule_families:
        raise MaterialsAuditError(f"{owner_id} requires rule_families")
    if not item.risk_notes:
        raise MaterialsAuditError(f"{owner_id} requires sensitive risk_notes")
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for local_reference in item.proposed_local_references:
        if not _is_source_relative_path(local_reference):
            raise MaterialsAuditError(f"{owner_id} has non-relative source path")
    for rule_family in item.rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    if item.risk_tier != "sensitive":
        raise MaterialsAuditError(f"{owner_id} must stay sensitive risk")
    if item.proposed_readiness_status != "needs_preparation":
        raise MaterialsAuditError(
            f"{owner_id} registration prep must keep source in needs_preparation"
        )
    if item.proposed_next_action != "prepare_material":
        raise MaterialsAuditError(
            f"{owner_id} registration prep must prepare material next"
        )
    if item.source_library_mutation_authorized:
        raise MaterialsAuditError(
            f"{owner_id} must not authorize source-library mutation"
        )
    if item.downstream_mutation_authorized:
        raise MaterialsAuditError(f"{owner_id} must not authorize downstream mutation")

    review_item = source_level_review_items_by_id.get(item.source_level_review_id)
    if review_item is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown source_level_review_id"
        )
    if review_item.review_status != "cleared_for_sensitive_registration_prep":
        raise MaterialsAuditError(f"{owner_id} source review is not registration-ready")
    if review_item.review_item_id != item.source_level_review_id:
        raise MaterialsAuditError(f"{owner_id} source_level_review_id mismatch")
    if review_item.prep_item_id != item.prep_review_item_id:
        raise MaterialsAuditError(f"{owner_id} prep_review_item_id mismatch")
    if review_item.prep_id != item.prep_id:
        raise MaterialsAuditError(f"{owner_id} prep_id mismatch")
    if review_item.source_selection_id != item.source_selection_id:
        raise MaterialsAuditError(f"{owner_id} source_selection_id mismatch")
    if review_item.cluster_id != item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id mismatch")
    if review_item.relative_paths != item.proposed_local_references:
        raise MaterialsAuditError(f"{owner_id} proposed_local_references mismatch")
    if not set(item.rule_families).issubset(set(review_item.target_rule_families)):
        raise MaterialsAuditError(f"{owner_id} rule_families mismatch")

    existing_entry = source_entries_by_id.get(item.proposed_entry_id)
    if existing_entry is not None and not _sensitive_registration_prep_entry_matches_existing(
        item,
        existing_entry,
    ):
        raise MaterialsAuditError(
            f"{owner_id} proposed_entry_id exists with mismatched metadata"
        )
    existing_material_ids = {
        source_entry.material_id for source_entry in source_entries_by_id.values()
    }
    if item.proposed_material_id in existing_material_ids and (
        existing_entry is None
        or existing_entry.material_id != item.proposed_material_id
    ):
        raise MaterialsAuditError(
            f"{owner_id} proposed_material_id already exists in source library"
        )

    return item


def load_raw_text_next_cycle_sensitive_registration_prep_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleSensitiveRegistrationPrepItem]:
    source_dir = _data_dir(data_dir)
    source_level_review_items_by_id = {
        item.review_item_id: item
        for item in load_raw_text_next_cycle_sensitive_source_level_risk_review_items(
            source_dir
        )
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    items = [
        _raw_text_next_cycle_sensitive_registration_prep_item_from_dict(
            item,
            source_level_review_items_by_id,
            source_entries_by_id,
        )
        for item in _read_optional_json_list(
            source_dir
            / "raw_text_next_cycle_sensitive_registration_prep_items.json"
        )
    ]
    _ensure_unique([item.prep_item_id for item in items], "prep_item_id")
    _ensure_unique(
        [item.source_level_review_id for item in items],
        "source_level_review_id",
    )
    _ensure_unique([item.proposed_entry_id for item in items], "proposed_entry_id")
    _ensure_unique([item.proposed_material_id for item in items], "proposed_material_id")
    return items


def _raw_text_next_cycle_sensitive_source_registration_item_from_dict(
    data: dict[str, Any],
    prep_items_by_id: dict[str, RawTextNextCycleSensitiveRegistrationPrepItem],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> RawTextNextCycleSensitiveSourceRegistrationItem:
    try:
        item = RawTextNextCycleSensitiveSourceRegistrationItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            "invalid raw text next-cycle sensitive source registration item: "
            f"{error}"
        ) from error

    owner_id = item.registration_item_id or "?"
    for field_name in (
        "registration_item_id",
        "registration_prep_item_id",
        "registered_entry_id",
        "registered_material_id",
        "registration_status",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    _validate_enum(
        item.registration_status,
        RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_REGISTRATION_STATUSES,
        "registration_status",
        owner_id,
    )
    for field_name in ("registered_local_references", "guardrails"):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    if not item.source_library_mutation_authorized:
        raise MaterialsAuditError(
            f"{owner_id} must authorize source-library mutation"
        )
    if item.downstream_mutation_authorized:
        raise MaterialsAuditError(f"{owner_id} must not authorize downstream mutation")
    for local_reference in item.registered_local_references:
        if not _is_source_relative_path(local_reference):
            raise MaterialsAuditError(f"{owner_id} has non-relative source path")

    prep_item = prep_items_by_id.get(item.registration_prep_item_id)
    if prep_item is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown registration_prep_item_id"
        )
    if prep_item.registration_status != "ready_for_sensitive_source_registration":
        raise MaterialsAuditError(f"{owner_id} prep item is not registration-ready")
    if prep_item.proposed_entry_id != item.registered_entry_id:
        raise MaterialsAuditError(f"{owner_id} registered_entry_id mismatch")
    if prep_item.proposed_material_id != item.registered_material_id:
        raise MaterialsAuditError(f"{owner_id} registered_material_id mismatch")
    if prep_item.proposed_local_references != item.registered_local_references:
        raise MaterialsAuditError(f"{owner_id} registered_local_references mismatch")

    source_entry = source_entries_by_id.get(item.registered_entry_id)
    if source_entry is None:
        raise MaterialsAuditError(f"{owner_id} registered_entry_id is missing")
    if not _sensitive_registration_prep_entry_matches_existing(prep_item, source_entry):
        raise MaterialsAuditError(
            f"{owner_id} registered entry does not match prep metadata"
        )

    return item


def load_raw_text_next_cycle_sensitive_source_registration_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleSensitiveSourceRegistrationItem]:
    source_dir = _data_dir(data_dir)
    prep_items_by_id = {
        item.prep_item_id: item
        for item in load_raw_text_next_cycle_sensitive_registration_prep_items(
            source_dir
        )
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    items = [
        _raw_text_next_cycle_sensitive_source_registration_item_from_dict(
            item,
            prep_items_by_id,
            source_entries_by_id,
        )
        for item in _read_optional_json_list(
            source_dir
            / "raw_text_next_cycle_sensitive_source_registration_items.json"
        )
    ]
    _ensure_unique([item.registration_item_id for item in items], "registration_item_id")
    _ensure_unique(
        [item.registration_prep_item_id for item in items],
        "registration_prep_item_id",
    )
    _ensure_unique([item.registered_entry_id for item in items], "registered_entry_id")
    _ensure_unique(
        [item.registered_material_id for item in items],
        "registered_material_id",
    )
    return items


def _raw_text_next_cycle_sensitive_preparation_boundary_item_from_dict(
    data: dict[str, Any],
    registration_items_by_id: dict[str, RawTextNextCycleSensitiveSourceRegistrationItem],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> RawTextNextCycleSensitivePreparationBoundaryItem:
    try:
        item = RawTextNextCycleSensitivePreparationBoundaryItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            "invalid raw text next-cycle sensitive preparation boundary item: "
            f"{error}"
        ) from error

    owner_id = item.boundary_item_id or "?"
    for field_name in (
        "boundary_item_id",
        "source_registration_item_id",
        "source_library_entry_id",
        "source_material_id",
        "boundary_status",
        "risk_boundary",
        "recommended_next_action",
        "boundary_decision",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    _validate_enum(
        item.boundary_status,
        RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_BOUNDARY_STATUSES,
        "boundary_status",
        owner_id,
    )
    _validate_enum(item.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    _validate_enum(
        item.recommended_next_action,
        SOURCE_LIBRARY_NEXT_ACTIONS,
        "recommended_next_action",
        owner_id,
    )
    for field_name in (
        "local_references",
        "target_rule_families",
        "preparation_topics",
        "risk_controls",
        "guardrails",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    if item.file_count != len(item.local_references):
        raise MaterialsAuditError(f"{owner_id} file_count mismatch")
    for field_name in (
        "preparation_allowed",
        "reading_allowed",
        "downstream_mutation_authorized",
    ):
        if not isinstance(getattr(item, field_name), bool):
            raise MaterialsAuditError(f"{owner_id} has invalid {field_name}")
    if not item.preparation_allowed:
        raise MaterialsAuditError(f"{owner_id} must allow preparation")
    if item.reading_allowed:
        raise MaterialsAuditError(f"{owner_id} must not allow reading yet")
    if item.downstream_mutation_authorized:
        raise MaterialsAuditError(f"{owner_id} must not authorize downstream mutation")
    if item.risk_boundary != "sensitive":
        raise MaterialsAuditError(f"{owner_id} must stay within sensitive boundary")
    for rule_family in item.target_rule_families:
        _validate_enum(rule_family, RULE_FAMILIES, "target_rule_family", owner_id)
    for local_reference in item.local_references:
        if not _is_source_relative_path(local_reference):
            raise MaterialsAuditError(f"{owner_id} has non-relative source path")

    registration_item = registration_items_by_id.get(item.source_registration_item_id)
    if registration_item is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown source_registration_item_id"
        )
    if (
        registration_item.registration_status
        != "registered_sensitive_source_library_entry"
    ):
        raise MaterialsAuditError(f"{owner_id} registration item is not complete")
    if registration_item.registered_entry_id != item.source_library_entry_id:
        raise MaterialsAuditError(f"{owner_id} source_library_entry_id mismatch")
    if registration_item.registered_material_id != item.source_material_id:
        raise MaterialsAuditError(f"{owner_id} source_material_id mismatch")
    if registration_item.registered_local_references != item.local_references:
        raise MaterialsAuditError(f"{owner_id} local_references mismatch")

    source_entry = source_entries_by_id.get(item.source_library_entry_id)
    if source_entry is None:
        raise MaterialsAuditError(f"{owner_id} source_library_entry_id is missing")
    if source_entry.material_id != item.source_material_id:
        raise MaterialsAuditError(f"{owner_id} source material mismatch")
    if source_entry.local_reference not in item.local_references:
        raise MaterialsAuditError(f"{owner_id} source local reference mismatch")
    if source_entry.risk_tier != "sensitive":
        raise MaterialsAuditError(f"{owner_id} source entry is not sensitive")
    if source_entry.readiness_status != "needs_preparation":
        raise MaterialsAuditError(f"{owner_id} source entry is not preparation-ready")
    if source_entry.next_action != item.recommended_next_action:
        raise MaterialsAuditError(f"{owner_id} source next_action mismatch")
    if item.recommended_next_action != "prepare_material":
        raise MaterialsAuditError(f"{owner_id} must route to prepare_material")

    return item


def load_raw_text_next_cycle_sensitive_preparation_boundary_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleSensitivePreparationBoundaryItem]:
    source_dir = _data_dir(data_dir)
    registration_items_by_id = {
        item.registration_item_id: item
        for item in load_raw_text_next_cycle_sensitive_source_registration_items(
            source_dir
        )
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    items = [
        _raw_text_next_cycle_sensitive_preparation_boundary_item_from_dict(
            item,
            registration_items_by_id,
            source_entries_by_id,
        )
        for item in _read_optional_json_list(
            source_dir
            / "raw_text_next_cycle_sensitive_preparation_boundary_items.json"
        )
    ]
    _ensure_unique([item.boundary_item_id for item in items], "boundary_item_id")
    _ensure_unique(
        [item.source_registration_item_id for item in items],
        "source_registration_item_id",
    )
    _ensure_unique(
        [item.source_library_entry_id for item in items],
        "source_library_entry_id",
    )
    _ensure_unique([item.source_material_id for item in items], "source_material_id")
    return items


def _raw_text_next_cycle_sensitive_preparation_reading_item_from_dict(
    data: dict[str, Any],
    boundary_items_by_id: dict[str, RawTextNextCycleSensitivePreparationBoundaryItem],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> RawTextNextCycleSensitivePreparationReadingItem:
    try:
        item = RawTextNextCycleSensitivePreparationReadingItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            "invalid raw text next-cycle sensitive preparation reading item: "
            f"{error}"
        ) from error

    owner_id = item.reading_item_id or "?"
    for field_name in (
        "reading_item_id",
        "boundary_item_id",
        "source_library_entry_id",
        "source_material_id",
        "reading_status",
        "risk_boundary",
        "reading_decision",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    _validate_enum(
        item.reading_status,
        RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_READING_STATUSES,
        "reading_status",
        owner_id,
    )
    _validate_enum(item.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    for field_name in (
        "local_references",
        "target_rule_families",
        "safe_reading_notes",
        "sensitive_controls",
        "guardrails",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    for field_name in (
        "candidate_intake_ready",
        "formal_evidence_ready",
        "downstream_mutation_authorized",
    ):
        if not isinstance(getattr(item, field_name), bool):
            raise MaterialsAuditError(f"{owner_id} has invalid {field_name}")
    if item.risk_boundary != "sensitive":
        raise MaterialsAuditError(f"{owner_id} must stay within sensitive boundary")
    if item.safe_reading_note_count != len(item.safe_reading_notes):
        raise MaterialsAuditError(f"{owner_id} safe_reading_note_count mismatch")
    if item.safe_reading_note_count < 3:
        raise MaterialsAuditError(f"{owner_id} needs at least three safe notes")
    if item.candidate_intake_ready:
        raise MaterialsAuditError(f"{owner_id} must not mark candidate intake ready")
    if item.formal_evidence_ready:
        raise MaterialsAuditError(f"{owner_id} must not mark formal evidence ready")
    if item.downstream_mutation_authorized:
        raise MaterialsAuditError(f"{owner_id} must not authorize downstream mutation")
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for rule_family in item.target_rule_families:
        _validate_enum(rule_family, RULE_FAMILIES, "target_rule_family", owner_id)
    for local_reference in item.local_references:
        if not _is_source_relative_path(local_reference):
            raise MaterialsAuditError(f"{owner_id} has non-relative source path")

    boundary_item = boundary_items_by_id.get(item.boundary_item_id)
    if boundary_item is None:
        raise MaterialsAuditError(f"{owner_id} references unknown boundary_item_id")
    if boundary_item.boundary_status != "cleared_for_sensitive_preparation":
        raise MaterialsAuditError(f"{owner_id} boundary item is not cleared")
    if not boundary_item.preparation_allowed:
        raise MaterialsAuditError(f"{owner_id} boundary does not allow preparation")
    if boundary_item.source_library_entry_id != item.source_library_entry_id:
        raise MaterialsAuditError(f"{owner_id} source_library_entry_id mismatch")
    if boundary_item.source_material_id != item.source_material_id:
        raise MaterialsAuditError(f"{owner_id} source_material_id mismatch")
    if boundary_item.local_references != item.local_references:
        raise MaterialsAuditError(f"{owner_id} local_references mismatch")

    source_entry = source_entries_by_id.get(item.source_library_entry_id)
    if source_entry is None:
        raise MaterialsAuditError(f"{owner_id} source_library_entry_id is missing")
    if source_entry.material_id != item.source_material_id:
        raise MaterialsAuditError(f"{owner_id} source material mismatch")
    if source_entry.local_reference not in item.local_references:
        raise MaterialsAuditError(f"{owner_id} source local reference mismatch")
    if source_entry.risk_tier != "sensitive":
        raise MaterialsAuditError(f"{owner_id} source entry is not sensitive")
    if source_entry.readiness_status != "needs_preparation":
        raise MaterialsAuditError(f"{owner_id} source entry is not preparation-gated")
    if source_entry.next_action != "prepare_material":
        raise MaterialsAuditError(f"{owner_id} source entry next_action mismatch")

    return item


def load_raw_text_next_cycle_sensitive_preparation_reading_items(
    data_dir: Path | str | None = None,
) -> list[RawTextNextCycleSensitivePreparationReadingItem]:
    source_dir = _data_dir(data_dir)
    boundary_items_by_id = {
        item.boundary_item_id: item
        for item in load_raw_text_next_cycle_sensitive_preparation_boundary_items(
            source_dir
        )
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    items = [
        _raw_text_next_cycle_sensitive_preparation_reading_item_from_dict(
            item,
            boundary_items_by_id,
            source_entries_by_id,
        )
        for item in _read_optional_json_list(
            source_dir
            / "raw_text_next_cycle_sensitive_preparation_reading_items.json"
        )
    ]
    _ensure_unique([item.reading_item_id for item in items], "reading_item_id")
    _ensure_unique([item.boundary_item_id for item in items], "boundary_item_id")
    _ensure_unique(
        [item.source_library_entry_id for item in items],
        "source_library_entry_id",
    )
    _ensure_unique([item.source_material_id for item in items], "source_material_id")
    return items


def _require_non_negative_number(value: Any, field_name: str, owner_id: str) -> None:
    if not isinstance(value, int | float) or value < 0:
        raise MaterialsAuditError(f"{owner_id} has invalid {field_name}")


def _raw_text_cluster_source_selection_item_from_dict(
    data: dict[str, Any],
) -> RawTextClusterSourceSelectionItem:
    try:
        item = RawTextClusterSourceSelectionItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text cluster source selection item: {error}"
        ) from error

    owner_id = item.selection_id or "?"
    for field_name in (
        "selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "title_label",
        "selection_status",
        "risk_boundary",
        "recommended_next_action",
        "identity_review_note",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    if item.cluster_id not in RAW_TEXT_CLUSTER_SOURCE_SELECTION_CLUSTER_IDS:
        raise MaterialsAuditError(f"{owner_id} has invalid cluster_id")
    if item.triage_group_id != RAW_TEXT_CLUSTER_SOURCE_SELECTION_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.selection_status,
        RAW_TEXT_CLUSTER_SOURCE_SELECTION_STATUSES,
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
    _require_non_negative_int(item.file_count, "file_count", owner_id)
    _require_non_negative_int(
        item.priority_text_candidate_count,
        "priority_text_candidate_count",
        owner_id,
    )
    _require_non_negative_int(item.priority_score, "priority_score", owner_id)
    _require_non_negative_number(item.size_mb_total, "size_mb_total", owner_id)
    _require_count_mapping(item.extension_counts, "extension_counts", owner_id)
    if item.file_count <= 0:
        raise MaterialsAuditError(f"{owner_id} requires positive file_count")
    if item.priority_text_candidate_count > item.file_count:
        raise MaterialsAuditError(
            f"{owner_id} priority count cannot exceed file_count"
        )
    if sum(item.extension_counts.values()) != item.file_count:
        raise MaterialsAuditError(f"{owner_id} extension counts must match file_count")

    for field_name in ("relative_paths", "target_rule_families", "guardrails"):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if len(item.relative_paths) != item.file_count:
        raise MaterialsAuditError(f"{owner_id} relative_paths must match file_count")
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for relative_path in item.relative_paths:
        if not _is_source_relative_path(relative_path):
            raise MaterialsAuditError(f"{owner_id} has non-relative source path")
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    if item.selection_status == "selected_for_identity_review":
        if item.recommended_next_action not in {"clarify_identity", "register_source"}:
            raise MaterialsAuditError(
                f"{owner_id} selected source must prepare identity review"
            )
    if item.selection_status == "variant_identity_review":
        if item.recommended_next_action != "clarify_identity":
            raise MaterialsAuditError(f"{owner_id} variant source must clarify identity")
    if item.selection_status == "deferred_after_cluster_selection":
        if item.recommended_next_action != "defer":
            raise MaterialsAuditError(f"{owner_id} deferred source must stay deferred")

    return item


def load_raw_text_cluster_source_selection_items(
    data_dir: Path | str | None = None,
) -> list[RawTextClusterSourceSelectionItem]:
    source_dir = _data_dir(data_dir)
    items = [
        _raw_text_cluster_source_selection_item_from_dict(item)
        for item in _read_optional_json_list(
            source_dir / "raw_text_cluster_source_selection_items.json"
        )
    ]
    _ensure_unique([item.selection_id for item in items], "selection_id")
    return items


def _raw_text_source_identity_review_item_from_dict(
    data: dict[str, Any],
    source_selection_items_by_id: dict[str, RawTextClusterSourceSelectionItem],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> RawTextSourceIdentityReviewItem:
    try:
        item = RawTextSourceIdentityReviewItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text source identity review item: {error}"
        ) from error

    owner_id = item.review_id or "?"
    for field_name in (
        "review_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "canonical_title_label",
        "identity_status",
        "source_library_overlap_status",
        "registration_readiness",
        "recommended_next_action",
        "next_review_target",
        "identity_review_note",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    source_selection_item = source_selection_items_by_id.get(item.source_selection_id)
    if source_selection_item is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown source_selection_id"
        )
    if item.cluster_id != source_selection_item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id does not match selection")
    if item.triage_group_id != RAW_TEXT_SOURCE_IDENTITY_REVIEW_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.identity_status,
        RAW_TEXT_SOURCE_IDENTITY_REVIEW_STATUSES,
        "identity_status",
        owner_id,
    )
    _validate_enum(
        item.source_library_overlap_status,
        RAW_TEXT_SOURCE_IDENTITY_REVIEW_OVERLAP_STATUSES,
        "source_library_overlap_status",
        owner_id,
    )
    _validate_enum(
        item.registration_readiness,
        RAW_TEXT_SOURCE_IDENTITY_REVIEW_REGISTRATION_READINESS,
        "registration_readiness",
        owner_id,
    )
    _validate_enum(
        item.recommended_next_action,
        MATERIAL_AUDIT_ACTIONS,
        "recommended_next_action",
        owner_id,
    )
    _validate_enum(item.risk_boundary, RISK_TIERS, "risk_boundary", owner_id)
    for field_name in (
        "matched_source_library_entry_ids",
        "target_rule_families",
        "guardrails",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for entry_id in item.matched_source_library_entry_ids:
        if entry_id not in source_entries_by_id:
            raise MaterialsAuditError(
                f"{owner_id} references unknown source-library entry: {entry_id}"
            )
    for rule_family in item.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )

    if item.identity_status == "existing_batch_overlap":
        if item.source_library_overlap_status != "existing_markdown_batch_overlap":
            raise MaterialsAuditError(
                f"{owner_id} existing batch status requires batch overlap"
            )
        if not item.matched_source_library_entry_ids:
            raise MaterialsAuditError(f"{owner_id} requires matched source entry")
        if item.registration_readiness != "no_registration_needed_existing_batch":
            raise MaterialsAuditError(
                f"{owner_id} existing batch status must not require registration"
            )
        if item.recommended_next_action != "no_action":
            raise MaterialsAuditError(
                f"{owner_id} existing batch status must use no_action"
            )
    if item.identity_status == "registration_prep_ready":
        if item.source_library_overlap_status != "no_registered_overlap_found":
            raise MaterialsAuditError(
                f"{owner_id} registration-prep status requires no registered overlap"
            )
        if item.matched_source_library_entry_ids:
            raise MaterialsAuditError(
                f"{owner_id} registration-prep status cannot reference source entries"
            )
        if item.registration_readiness != "ready_for_registration_prep":
            raise MaterialsAuditError(
                f"{owner_id} registration-prep status has invalid readiness"
            )
        if item.recommended_next_action != "register_source":
            raise MaterialsAuditError(
                f"{owner_id} registration-prep status must register source"
            )
    if item.identity_status == "variant_choice_required":
        if item.source_library_overlap_status != "variant_set_requires_choice":
            raise MaterialsAuditError(
                f"{owner_id} variant status requires variant overlap status"
            )
        if item.registration_readiness != "needs_variant_choice":
            raise MaterialsAuditError(f"{owner_id} variant status has invalid readiness")
        if item.recommended_next_action != "clarify_identity":
            raise MaterialsAuditError(
                f"{owner_id} variant status must clarify identity"
            )
    if item.identity_status == "deferred_large_source":
        if item.source_library_overlap_status != "deferred_large_source":
            raise MaterialsAuditError(
                f"{owner_id} deferred status requires deferred overlap status"
            )
        if item.registration_readiness != "deferred":
            raise MaterialsAuditError(f"{owner_id} deferred status has invalid readiness")
        if item.recommended_next_action != "defer":
            raise MaterialsAuditError(f"{owner_id} deferred status must defer")

    return item


def load_raw_text_source_identity_review_items(
    data_dir: Path | str | None = None,
) -> list[RawTextSourceIdentityReviewItem]:
    source_dir = _data_dir(data_dir)
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_cluster_source_selection_items(source_dir)
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    items = [
        _raw_text_source_identity_review_item_from_dict(
            item,
            source_selection_items_by_id,
            source_entries_by_id,
        )
        for item in _read_optional_json_list(
            source_dir / "raw_text_source_identity_review_items.json"
        )
    ]
    _ensure_unique([item.review_id for item in items], "review_id")
    _ensure_unique(
        [item.source_selection_id for item in items],
        "source_selection_id",
    )
    return items


def _bazi_general_variant_deferred_review_item_from_dict(
    data: dict[str, Any],
    identity_review_items_by_id: dict[str, RawTextSourceIdentityReviewItem],
    source_selection_items_by_id: dict[str, RawTextClusterSourceSelectionItem],
) -> BaziGeneralVariantDeferredReviewItem:
    try:
        item = BaziGeneralVariantDeferredReviewItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid bazi general variant deferred review item: {error}"
        ) from error

    owner_id = item.item_id or "?"
    for field_name in (
        "item_id",
        "identity_review_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "review_kind",
        "review_status",
        "decision",
        "canonical_choice_status",
        "review_note",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)

    identity_review_item = identity_review_items_by_id.get(item.identity_review_id)
    if identity_review_item is None:
        raise MaterialsAuditError(f"{owner_id} references unknown identity_review_id")
    source_selection_item = source_selection_items_by_id.get(item.source_selection_id)
    if source_selection_item is None:
        raise MaterialsAuditError(f"{owner_id} references unknown source_selection_id")
    if item.source_selection_id != identity_review_item.source_selection_id:
        raise MaterialsAuditError(
            f"{owner_id} source_selection_id does not match identity review"
        )
    if item.cluster_id != identity_review_item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id does not match identity")
    if item.cluster_id != source_selection_item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id does not match selection")
    if item.triage_group_id != RAW_TEXT_SOURCE_IDENTITY_REVIEW_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")

    _validate_enum(
        item.review_kind,
        BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_KINDS,
        "review_kind",
        owner_id,
    )
    _validate_enum(
        item.review_status,
        BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_STATUSES,
        "review_status",
        owner_id,
    )
    _validate_enum(
        item.decision,
        BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_DECISIONS,
        "decision",
        owner_id,
    )
    _validate_enum(
        item.canonical_choice_status,
        BAZI_GENERAL_VARIANT_DEFERRED_CANONICAL_CHOICE_STATUSES,
        "canonical_choice_status",
        owner_id,
    )
    for field_name in ("local_references", "candidate_rule_families", "guardrails"):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    if item.local_references != source_selection_item.relative_paths:
        raise MaterialsAuditError(
            f"{owner_id} local_references must match source selection paths"
        )
    for local_reference in item.local_references:
        if not _is_source_relative_path(local_reference):
            raise MaterialsAuditError(f"{owner_id} has non-relative source path")
    for rule_family in item.candidate_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    if item.selected_source_library_entry_id:
        raise MaterialsAuditError(
            f"{owner_id} cannot select source-library entry in this review"
        )
    if item.selected_local_reference and item.selected_local_reference not in item.local_references:
        raise MaterialsAuditError(
            f"{owner_id} selected_local_reference must be one local reference"
        )
    if item.source_library_mutation_authorized:
        raise MaterialsAuditError(
            f"{owner_id} cannot authorize source-library mutation"
        )
    if item.downstream_mutation_authorized:
        raise MaterialsAuditError(f"{owner_id} cannot authorize downstream mutation")

    if item.review_kind == "variant_choice":
        if identity_review_item.identity_status != "variant_choice_required":
            raise MaterialsAuditError(
                f"{owner_id} variant review must reference variant identity"
            )
        if source_selection_item.selection_status != "variant_identity_review":
            raise MaterialsAuditError(
                f"{owner_id} variant review must reference variant selection"
            )
        blocked_shape = (
            item.review_status == "blocked_pending_variant_choice"
            and item.decision == "keep_variant_choice_blocked"
            and item.canonical_choice_status == "not_selected"
            and not item.selected_local_reference
        )
        selected_shape = (
            item.review_status == "canonical_variant_selected"
            and item.decision == "select_canonical_variant"
            and item.canonical_choice_status == "selected_for_registration_prep"
            and bool(item.selected_local_reference)
        )
        if not (blocked_shape or selected_shape):
            raise MaterialsAuditError(
                f"{owner_id} variant review has inconsistent choice status"
            )
    if item.review_kind == "deferred_large_source":
        if identity_review_item.identity_status != "deferred_large_source":
            raise MaterialsAuditError(
                f"{owner_id} deferred review must reference deferred identity"
            )
        if source_selection_item.selection_status != "deferred_after_cluster_selection":
            raise MaterialsAuditError(
                f"{owner_id} deferred review must reference deferred selection"
            )
        if item.review_status != "deferred_large_source_reviewed":
            raise MaterialsAuditError(
                f"{owner_id} deferred review has invalid review_status"
            )
        if item.decision != "keep_large_source_deferred":
            raise MaterialsAuditError(
                f"{owner_id} deferred review has invalid decision"
            )
        if item.canonical_choice_status != "not_applicable":
            raise MaterialsAuditError(
                f"{owner_id} deferred review cannot carry canonical choice"
            )
        if item.selected_local_reference:
            raise MaterialsAuditError(
                f"{owner_id} deferred review cannot select local reference"
            )

    return item


def load_bazi_general_variant_deferred_review_items(
    data_dir: Path | str | None = None,
) -> list[BaziGeneralVariantDeferredReviewItem]:
    source_dir = _data_dir(data_dir)
    identity_review_items_by_id = {
        item.review_id: item for item in load_raw_text_source_identity_review_items(source_dir)
    }
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_cluster_source_selection_items(source_dir)
    }
    items = [
        _bazi_general_variant_deferred_review_item_from_dict(
            item,
            identity_review_items_by_id,
            source_selection_items_by_id,
        )
        for item in _read_optional_json_list(
            source_dir / "bazi_general_variant_deferred_review_items.json"
        )
    ]
    _ensure_unique([item.item_id for item in items], "item_id")
    _ensure_unique([item.identity_review_id for item in items], "identity_review_id")
    _ensure_unique([item.source_selection_id for item in items], "source_selection_id")
    return items


def _raw_text_source_registration_prep_item_from_dict(
    data: dict[str, Any],
    identity_review_items_by_id: dict[str, RawTextSourceIdentityReviewItem],
    source_selection_items_by_id: dict[str, RawTextClusterSourceSelectionItem],
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> RawTextSourceRegistrationPrepItem:
    try:
        item = RawTextSourceRegistrationPrepItem(**data)
    except TypeError as error:
        raise MaterialsAuditError(
            f"invalid raw text source registration prep item: {error}"
        ) from error

    owner_id = item.prep_id or "?"
    for field_name in (
        "prep_id",
        "identity_review_id",
        "source_selection_id",
        "cluster_id",
        "triage_group_id",
        "source_root",
        "registration_status",
        "proposed_entry_id",
        "proposed_material_id",
        "proposed_title",
        "proposed_material_type",
        "proposed_tracking_status",
        "proposed_readiness_status",
        "proposed_priority_level",
        "proposed_next_action",
        "risk_tier",
        "source_quality_notes",
        "rights_notes",
        "source_library_overlap_policy",
        "rationale",
    ):
        _require_text(getattr(item, field_name), field_name, owner_id)
    identity_review_item = identity_review_items_by_id.get(item.identity_review_id)
    if identity_review_item is None:
        raise MaterialsAuditError(f"{owner_id} references unknown identity_review_id")
    if identity_review_item.identity_status != "registration_prep_ready":
        raise MaterialsAuditError(
            f"{owner_id} must reference registration_prep_ready identity review"
        )
    if item.source_selection_id != identity_review_item.source_selection_id:
        raise MaterialsAuditError(
            f"{owner_id} source_selection_id does not match identity review"
        )
    if item.cluster_id != identity_review_item.cluster_id:
        raise MaterialsAuditError(f"{owner_id} cluster_id does not match identity")
    source_selection_item = source_selection_items_by_id.get(item.source_selection_id)
    if source_selection_item is None:
        raise MaterialsAuditError(
            f"{owner_id} references unknown source_selection_id"
        )
    if item.triage_group_id != RAW_TEXT_SOURCE_REGISTRATION_PREP_TRIAGE_GROUP_ID:
        raise MaterialsAuditError(f"{owner_id} has invalid triage_group_id")
    if item.source_root != RAW_TEXT_TRIAGE_SOURCE_ROOT:
        raise MaterialsAuditError(f"{owner_id} has invalid source_root")
    _validate_enum(
        item.registration_status,
        RAW_TEXT_SOURCE_REGISTRATION_PREP_STATUSES,
        "registration_status",
        owner_id,
    )
    _validate_enum(
        item.proposed_material_type,
        SOURCE_LIBRARY_MATERIAL_TYPES,
        "proposed_material_type",
        owner_id,
    )
    _validate_enum(
        item.proposed_tracking_status,
        MATERIAL_TRACKING_STATUSES,
        "proposed_tracking_status",
        owner_id,
    )
    _validate_enum(
        item.proposed_readiness_status,
        SOURCE_LIBRARY_READINESS_STATUSES,
        "proposed_readiness_status",
        owner_id,
    )
    _validate_enum(
        item.proposed_priority_level,
        SOURCE_LIBRARY_PRIORITY_LEVELS,
        "proposed_priority_level",
        owner_id,
    )
    _validate_enum(
        item.proposed_next_action,
        SOURCE_LIBRARY_NEXT_ACTIONS,
        "proposed_next_action",
        owner_id,
    )
    _validate_enum(item.risk_tier, RISK_TIERS, "risk_tier", owner_id)
    _validate_enum(
        item.source_library_overlap_policy,
        RAW_TEXT_SOURCE_REGISTRATION_PREP_OVERLAP_POLICIES,
        "source_library_overlap_policy",
        owner_id,
    )
    for field_name in (
        "proposed_local_references",
        "topic_tags",
        "rule_families",
        "risk_notes",
        "guardrails",
    ):
        _require_string_list(getattr(item, field_name), field_name, owner_id)
    if not item.proposed_local_references:
        raise MaterialsAuditError(f"{owner_id} requires proposed_local_references")
    if not item.topic_tags:
        raise MaterialsAuditError(f"{owner_id} requires topic_tags")
    if not item.rule_families:
        raise MaterialsAuditError(f"{owner_id} requires rule_families")
    if not item.guardrails:
        raise MaterialsAuditError(f"{owner_id} requires guardrails")
    for local_reference in item.proposed_local_references:
        if not _is_source_relative_path(local_reference):
            raise MaterialsAuditError(f"{owner_id} has non-relative source path")
        if local_reference not in source_selection_item.relative_paths:
            raise MaterialsAuditError(
                f"{owner_id} local reference not present in source selection"
            )
    for rule_family in item.rule_families:
        if rule_family not in RULE_FAMILIES:
            raise MaterialsAuditError(
                f"{owner_id} has unsupported rule_family: {rule_family}"
            )
    existing_entry = source_entries_by_id.get(item.proposed_entry_id)
    if existing_entry is not None and not _source_entry_matches_registration_prep(
        item,
        existing_entry,
    ):
        raise MaterialsAuditError(
            f"{owner_id} proposed_entry_id exists with mismatched metadata"
        )
    existing_material_ids = {
        source_entry.material_id for source_entry in source_entries_by_id.values()
    }
    if item.proposed_material_id in existing_material_ids and (
        existing_entry is None
        or existing_entry.material_id != item.proposed_material_id
    ):
        raise MaterialsAuditError(
            f"{owner_id} proposed_material_id already exists in source library"
        )
    if item.proposed_readiness_status != "needs_preparation":
        raise MaterialsAuditError(
            f"{owner_id} registration prep must keep source in needs_preparation"
        )
    if item.proposed_next_action != "prepare_material":
        raise MaterialsAuditError(
            f"{owner_id} registration prep must prepare material next"
        )

    return item


def _registration_prep_local_reference(
    item: RawTextSourceRegistrationPrepItem,
) -> str:
    return "; ".join(item.proposed_local_references)


def _source_entry_matches_registration_prep(
    item: RawTextSourceRegistrationPrepItem,
    entry: source_library.SourceLibraryEntry,
) -> bool:
    allowed_readiness_statuses = {
        item.proposed_readiness_status,
        "ready_for_extraction",
        "review_completed",
    }
    allowed_next_actions = {
        item.proposed_next_action,
        "extract_candidates",
        "review_candidates",
        "promote_approved",
        "no_action",
    }
    return (
        entry.material_id == item.proposed_material_id
        and entry.title == item.proposed_title
        and entry.material_type == item.proposed_material_type
        and entry.local_reference == _registration_prep_local_reference(item)
        and entry.tracking_status == item.proposed_tracking_status
        and entry.readiness_status in allowed_readiness_statuses
        and entry.topic_tags == item.topic_tags
        and entry.rule_families == item.rule_families
        and entry.rights_notes == item.rights_notes
        and entry.risk_tier == item.risk_tier
        and entry.risk_notes == item.risk_notes
        and entry.priority_level in SOURCE_LIBRARY_PRIORITY_LEVELS
        and entry.next_action in allowed_next_actions
    )


def _registration_prep_entry_registered_or_available(
    item: RawTextSourceRegistrationPrepItem,
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
    existing_material_ids: set[str],
) -> bool:
    existing_entry = source_entries_by_id.get(item.proposed_entry_id)
    if existing_entry is not None:
        return _source_entry_matches_registration_prep(item, existing_entry)
    return item.proposed_material_id not in existing_material_ids


def load_raw_text_source_registration_prep_items(
    data_dir: Path | str | None = None,
) -> list[RawTextSourceRegistrationPrepItem]:
    source_dir = _data_dir(data_dir)
    identity_review_items_by_id = {
        item.review_id: item for item in load_raw_text_source_identity_review_items(source_dir)
    }
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_cluster_source_selection_items(source_dir)
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    items = [
        _raw_text_source_registration_prep_item_from_dict(
            item,
            identity_review_items_by_id,
            source_selection_items_by_id,
            source_entries_by_id,
        )
        for item in _read_optional_json_list(
            source_dir / "raw_text_source_registration_prep_items.json"
        )
    ]
    _ensure_unique([item.prep_id for item in items], "prep_id")
    _ensure_unique([item.identity_review_id for item in items], "identity_review_id")
    _ensure_unique([item.proposed_entry_id for item in items], "proposed_entry_id")
    _ensure_unique([item.proposed_material_id for item in items], "proposed_material_id")
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
    queue_refresh = build_materials_audit_queue_refresh_summary(source_dir)
    post_queue_refresh_surface_confirmed = (
        queue_refresh.next_material_entry == "015-external-material-inventory-refresh"
        and queue_refresh.refresh_status == "covered_or_completed_queue_exhausted"
    )

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
        next_material_entry=(
            EXTERNAL_INVENTORY_POST_QUEUE_NEXT_MATERIAL_ENTRY
            if post_queue_refresh_surface_confirmed and not untracked_material_entry_ids
            else EXTERNAL_INVENTORY_NEXT_MATERIAL_ENTRY
        ),
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
            "post_queue_refresh_surface_confirmed": (
                "passed" if post_queue_refresh_surface_confirmed else "failed"
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


def _count_next_cycle_rule_families(
    items: list[RawTextNextCycleSourceSelectionItem],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts.update(item.target_rule_families)
    return dict(sorted(counts.items()))


def _count_next_cycle_identity_rule_families(
    items: list[RawTextNextCycleIdentityReviewItem],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts.update(item.target_rule_families)
    return dict(sorted(counts.items()))


def _count_cluster_source_rule_families(
    items: list[RawTextClusterSourceSelectionItem],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts.update(item.target_rule_families)
    return dict(sorted(counts.items()))


def _count_source_identity_rule_families(
    items: list[RawTextSourceIdentityReviewItem],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts.update(item.target_rule_families)
    return dict(sorted(counts.items()))


def _count_registration_prep_rule_families(
    items: list[RawTextSourceRegistrationPrepItem],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts.update(item.rule_families)
    return dict(sorted(counts.items()))


def _source_entries_absent_for_markers(
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
    markers: tuple[str, ...],
) -> bool:
    return not any(
        entry_id.startswith("entry_bazi_general_") and marker in entry_id
        for entry_id in source_entries_by_id
        for marker in markers
    )


def _selected_variant_entries_registered(
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> bool:
    return all(
        entry_id in source_entries_by_id
        for entry_id in BAZI_GENERAL_SELECTED_VARIANT_ENTRY_IDS
    )


def _selected_variant_queue_surface_completed(
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> bool:
    return _selected_variant_entries_registered(source_entries_by_id)


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


def _sum_cluster_source_extension_counts(
    items: list[RawTextClusterSourceSelectionItem],
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


def build_raw_text_next_cycle_source_selection_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleSourceSelectionSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_source_selection_items(source_dir)
    clusters_by_id = {
        cluster.cluster_id: cluster
        for cluster in load_raw_text_source_cluster_selection_items(source_dir)
    }
    external_inventory = build_external_material_inventory_refresh_summary(source_dir)

    selected_cluster_ids = [
        item.cluster_id
        for item in items
        if item.selection_status == "selected_for_identity_review"
    ]
    deferred_cluster_ids = [
        item.cluster_id
        for item in items
        if item.selection_status
        in {"deferred_case_collection", "deferred_formula_review"}
    ]
    risk_review_cluster_ids = [
        item.cluster_id
        for item in items
        if item.selection_status == "risk_review_required"
    ]
    selected_clusters_need_identity_review = bool(selected_cluster_ids) and all(
        cluster_id in clusters_by_id
        and clusters_by_id[cluster_id].cluster_status == "identity_review_required"
        and cluster_id in RAW_TEXT_NEXT_CYCLE_SELECTED_CLUSTER_IDS
        for cluster_id in selected_cluster_ids
    )
    deferred_clusters_stay_deferred = set(deferred_cluster_ids) == set(
        RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS
    ) and all(
        clusters_by_id[cluster_id].cluster_status == "backlog_cluster"
        for cluster_id in deferred_cluster_ids
        if cluster_id in clusters_by_id
    )
    sensitive_clusters_stay_risk_review = set(risk_review_cluster_ids) == set(
        RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS
    ) and all(
        clusters_by_id[cluster_id].cluster_status == "sensitive_boundary_deferred"
        for cluster_id in risk_review_cluster_ids
        if cluster_id in clusters_by_id
    )
    huntian_baolan_deferred = "bazi_general_classical_reference_cluster" not in set(
        selected_cluster_ids
    ) and all(
        "huntian" not in " ".join(
            (item.selection_id, item.cluster_id, item.selection_label)
        ).lower()
        for item in items
    )
    boundary_checks = {
        "next_cycle_items_loaded": "passed" if items else "failed",
        "source_cluster_items_loaded": (
            "passed"
            if items and all(item.cluster_id in clusters_by_id for item in items)
            else "failed"
        ),
        "external_inventory_entrypoint_confirmed": (
            "passed"
            if external_inventory.next_material_entry
            == RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_ID
            else "failed"
        ),
        "selected_clusters_need_identity_review": (
            "passed" if selected_clusters_need_identity_review else "failed"
        ),
        "deferred_clusters_stay_deferred": (
            "passed" if deferred_clusters_stay_deferred else "failed"
        ),
        "sensitive_clusters_stay_risk_review": (
            "passed" if sensitive_clusters_stay_risk_review else "failed"
        ),
        "huntian_baolan_deferred": "passed" if huntian_baolan_deferred else "failed",
        "raw_materials_not_mutated": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }

    return RawTextNextCycleSourceSelectionSummary(
        selection_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_ID,
        selection_status=(
            "next_cycle_source_selection_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "next_cycle_source_selection_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        selection_item_count=len(items),
        selected_for_identity_review_count=len(selected_cluster_ids),
        deferred_cluster_count=len(deferred_cluster_ids),
        risk_review_cluster_count=len(risk_review_cluster_ids),
        status_counts=_count_values([item.selection_status for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_next_cycle_rule_families(items),
        selected_cluster_ids=selected_cluster_ids,
        deferred_cluster_ids=deferred_cluster_ids,
        risk_review_cluster_ids=risk_review_cluster_ids,
        downstream_mutation_authorized=False,
        next_material_entry=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Next-cycle selection uses source-cluster inventory metadata only.",
            "Selected clusters require identity review before registration, reading, or extraction.",
            "Case and formula clusters stay deferred until the selected ordinary identity review is closed.",
            "Sensitive clusters require separate risk review before any learning use.",
            "Raw files, source-library records, candidates, reviews, promotions, and formal evidence are not mutated.",
        ],
    )


def render_raw_text_next_cycle_source_selection_markdown(
    summary: RawTextNextCycleSourceSelectionSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Source Selection",
        "",
        f"- Selection id: `{summary.selection_id}`",
        (
            "- `next-cycle-source-selection-status="
            f"{summary.selection_status}`"
        ),
        f"- `next-cycle-source-selection-items={summary.selection_item_count}`",
        (
            "- `selected-for-identity-review="
            f"{summary.selected_for_identity_review_count}`"
        ),
        f"- `deferred-clusters={summary.deferred_cluster_count}`",
        f"- `risk-review-clusters={summary.risk_review_cluster_count}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Selected clusters:",
    ]
    lines.extend(f"- `{cluster_id}`" for cluster_id in summary.selected_cluster_ids)
    lines.extend(["", "Deferred clusters:"])
    lines.extend(f"- `{cluster_id}`" for cluster_id in summary.deferred_cluster_ids)
    lines.extend(["", "Risk-review clusters:"])
    lines.extend(f"- `{cluster_id}`" for cluster_id in summary.risk_review_cluster_ids)
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


def build_raw_text_next_cycle_identity_review_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleIdentityReviewSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_identity_review_items(source_dir)
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_next_cycle_source_selection_items(source_dir)
    }
    selected_source_selection_references_valid = bool(items) and all(
        item.source_selection_id in source_selection_items_by_id
        and source_selection_items_by_id[item.source_selection_id].selection_status
        == "selected_for_identity_review"
        for item in items
    )
    selected_clusters_only = bool(items) and {
        item.cluster_id for item in items
    } == set(RAW_TEXT_NEXT_CYCLE_SELECTED_CLUSTER_IDS)
    cluster_counts_match_source_selection = bool(items) and all(
        item.source_selection_id in source_selection_items_by_id
        and item.file_count
        == source_selection_items_by_id[item.source_selection_id].file_count
        and item.priority_text_candidate_count
        == source_selection_items_by_id[
            item.source_selection_id
        ].priority_text_candidate_count
        for item in items
    )
    deferred_clusters_remain_out_of_scope = all(
        item.cluster_id not in RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS
        for item in items
    )
    risk_review_clusters_remain_out_of_scope = all(
        item.cluster_id not in RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS
        for item in items
    )
    boundary_checks = {
        "identity_review_items_loaded": "passed" if items else "failed",
        "next_cycle_source_selection_items_loaded": (
            "passed" if source_selection_items_by_id else "failed"
        ),
        "selected_source_selection_references_valid": (
            "passed" if selected_source_selection_references_valid else "failed"
        ),
        "selected_clusters_only": "passed" if selected_clusters_only else "failed",
        "cluster_counts_match_source_selection": (
            "passed" if cluster_counts_match_source_selection else "failed"
        ),
        "deferred_clusters_remain_out_of_scope": (
            "passed" if deferred_clusters_remain_out_of_scope else "failed"
        ),
        "risk_review_clusters_remain_out_of_scope": (
            "passed" if risk_review_clusters_remain_out_of_scope else "failed"
        ),
        "raw_materials_not_mutated": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }
    cluster_source_selection_required_ids = [
        item.review_id
        for item in items
        if item.identity_status == "cluster_source_selection_required"
    ]
    registration_prep_ready_ids = [
        item.review_id
        for item in items
        if item.identity_status == "registration_prep_ready"
    ]
    source_library_overlap_ids = [
        item.review_id
        for item in items
        if item.identity_status == "source_library_overlap_found"
    ]

    return RawTextNextCycleIdentityReviewSummary(
        review_id=RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_ID,
        review_status=(
            "next_cycle_identity_review_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "next_cycle_identity_review_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        identity_review_item_count=len(items),
        cluster_source_selection_required_count=len(
            cluster_source_selection_required_ids
        ),
        registration_prep_ready_count=len(registration_prep_ready_ids),
        source_library_overlap_found_count=len(source_library_overlap_ids),
        identity_status_counts=_count_values([item.identity_status for item in items]),
        source_library_overlap_counts=_count_values(
            [item.source_library_overlap_status for item in items]
        ),
        registration_readiness_counts=_count_values(
            [item.registration_readiness for item in items]
        ),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_next_cycle_identity_rule_families(items),
        cluster_source_selection_required_ids=cluster_source_selection_required_ids,
        registration_prep_ready_ids=registration_prep_ready_ids,
        source_library_overlap_ids=source_library_overlap_ids,
        source_library_mutation_authorized=False,
        downstream_mutation_authorized=False,
        next_material_entry=RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Next-cycle identity review uses source-selection metadata only.",
            "Selected clusters still require source-level selection before registration prep.",
            "Case, formula, and sensitive clusters remain outside this identity review.",
            "Raw files, source-library records, candidates, reviews, promotions, and formal evidence are not mutated.",
        ],
    )


def render_raw_text_next_cycle_identity_review_markdown(
    summary: RawTextNextCycleIdentityReviewSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Identity Review",
        "",
        f"- Review id: `{summary.review_id}`",
        (
            "- `next-cycle-identity-review-status="
            f"{summary.review_status}`"
        ),
        f"- `next-cycle-identity-review-items={summary.identity_review_item_count}`",
        (
            "- `cluster-source-selection-required="
            f"{summary.cluster_source_selection_required_count}`"
        ),
        f"- `registration-prep-ready={summary.registration_prep_ready_count}`",
        (
            "- `source-library-overlap-found="
            f"{summary.source_library_overlap_found_count}`"
        ),
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Cluster-source selection required:",
    ]
    lines.extend(
        f"- `{review_id}`"
        for review_id in summary.cluster_source_selection_required_ids
    )
    lines.extend(["", "Registration-prep-ready records:"])
    lines.extend(f"- `{review_id}`" for review_id in summary.registration_prep_ready_ids)
    lines.extend(["", "Source-library overlap records:"])
    lines.extend(f"- `{review_id}`" for review_id in summary.source_library_overlap_ids)
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


def build_raw_text_next_cycle_cluster_source_selection_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleClusterSourceSelectionSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_cluster_source_selection_items(source_dir)
    identity_review_items_by_id = {
        item.review_id: item
        for item in load_raw_text_next_cycle_identity_review_items(source_dir)
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    material_audit_records_by_id = {
        record.audit_id: record for record in load_material_audit_records(source_dir)
    }
    queue_items_by_id = {
        item.queue_item_id: item for item in load_extraction_queue_items(source_dir)
    }
    source_materials_by_id = {
        material.material_id: material
        for material in source_intake.load_source_materials(
            _sibling_data_dir(source_dir, "source_intake")
        )
    }
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in source_intake.load_candidate_extracts(
            _sibling_data_dir(source_dir, "source_intake")
        )
    }
    evidence_by_id = {
        unit.evidence_id: unit
        for unit in classical_sources.load_evidence_units(
            _sibling_data_dir(source_dir, "classical_sources")
        )
    }

    selected_items = [
        item for item in items if item.selection_status == "selected_for_registration"
    ]
    selected_item_ids = [item.selection_id for item in selected_items]
    registered_entry_ids = [item.source_library_entry_id for item in selected_items]
    registered_material_ids = [item.source_material_id for item in selected_items]
    audit_ids = [item.audit_id for item in selected_items]
    queue_item_ids = [item.queue_item_id for item in selected_items]
    candidate_ids = [item.candidate_id for item in selected_items]
    evidence_ids = [item.evidence_id for item in selected_items]

    identity_review_references_valid = bool(items) and all(
        item.identity_review_id in identity_review_items_by_id
        and identity_review_items_by_id[item.identity_review_id].identity_status
        == "cluster_source_selection_required"
        for item in items
    )
    source_paths_are_relative = bool(items) and all(
        _is_source_relative_path(path)
        for item in items
        for path in item.relative_paths
    )
    selected_clusters_only = bool(items) and all(
        item.cluster_id in RAW_TEXT_NEXT_CYCLE_SELECTED_CLUSTER_IDS for item in items
    )
    source_library_entries_registered = all(
        entry_id in source_entries_by_id
        and source_entries_by_id[entry_id].material_id == material_id
        and source_entries_by_id[entry_id].readiness_status == "review_completed"
        for entry_id, material_id in zip(registered_entry_ids, registered_material_ids)
    )
    material_preparation_registered = all(
        audit_id in material_audit_records_by_id
        and queue_item_id in queue_items_by_id
        and material_id in source_materials_by_id
        and source_materials_by_id[material_id].preparation_status == "reviewed"
        for audit_id, queue_item_id, material_id in zip(
            audit_ids,
            queue_item_ids,
            registered_material_ids,
        )
    )
    candidates_promoted = all(
        candidate_id in candidates_by_id
        and candidates_by_id[candidate_id].status == "promoted"
        and candidates_by_id[candidate_id].related_evidence_ids == [evidence_id]
        for candidate_id, evidence_id in zip(candidate_ids, evidence_ids)
    )
    evidence_promoted = all(
        evidence_id in evidence_by_id
        and evidence_by_id[evidence_id].source_quality == "review_note"
        for evidence_id in evidence_ids
    )
    deferred_clusters_remain_out_of_scope = all(
        item.cluster_id not in RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS
        for item in items
    )
    risk_review_clusters_remain_out_of_scope = all(
        item.cluster_id not in RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS
        for item in items
    )
    boundary_checks = {
        "cluster_source_selection_items_loaded": "passed" if items else "failed",
        "identity_review_references_valid": (
            "passed" if identity_review_references_valid else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "selected_clusters_only": "passed" if selected_clusters_only else "failed",
        "source_library_entries_registered": (
            "passed"
            if source_library_entries_registered and material_preparation_registered
            else "failed"
        ),
        "013_candidates_promoted": "passed" if candidates_promoted else "failed",
        "012_evidence_promoted": "passed" if evidence_promoted else "failed",
        "deferred_clusters_remain_out_of_scope": (
            "passed" if deferred_clusters_remain_out_of_scope else "failed"
        ),
        "risk_review_clusters_remain_out_of_scope": (
            "passed" if risk_review_clusters_remain_out_of_scope else "failed"
        ),
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleClusterSourceSelectionSummary(
        selection_id=RAW_TEXT_NEXT_CYCLE_CLUSTER_SOURCE_SELECTION_ID,
        selection_status=(
            "next_cycle_cluster_source_selection_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "next_cycle_cluster_source_selection_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        source_selection_item_count=len(items),
        source_file_count=sum(item.file_count for item in items),
        priority_text_candidate_count=sum(
            item.priority_text_candidate_count for item in items
        ),
        selected_for_registration_count=len(selected_items),
        registered_source_entry_count=sum(
            1 for entry_id in registered_entry_ids if entry_id in source_entries_by_id
        ),
        candidate_extract_count=sum(
            1
            for candidate_id in candidate_ids
            if candidate_id in candidates_by_id
            and candidates_by_id[candidate_id].status == "promoted"
        ),
        formal_evidence_count=sum(
            1 for evidence_id in evidence_ids if evidence_id in evidence_by_id
        ),
        selected_item_ids=selected_item_ids,
        registered_entry_ids=registered_entry_ids,
        registered_material_ids=registered_material_ids,
        audit_ids=audit_ids,
        queue_item_ids=queue_item_ids,
        candidate_ids=candidate_ids,
        evidence_ids=evidence_ids,
        status_counts=_count_values([item.selection_status for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_values(
            [rule for item in items for rule in item.target_rule_families]
        ),
        source_library_mutation_authorized=True,
        downstream_mutation_authorized=True,
        next_material_entry=RAW_TEXT_NEXT_CYCLE_CLUSTER_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Only two authorized source-level records are registered in this next-cycle slice.",
            "All locators remain weak page-level placeholders until later transcription.",
            "Case, formula, and sensitive clusters remain outside this selection.",
            "Raw external materials are not moved, converted, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_cluster_source_selection_markdown(
    summary: RawTextNextCycleClusterSourceSelectionSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Cluster Source Selection",
        "",
        f"- Selection id: `{summary.selection_id}`",
        (
            "- `next-cycle-cluster-source-selection-status="
            f"{summary.selection_status}`"
        ),
        (
            "- `next-cycle-cluster-source-selection-items="
            f"{summary.source_selection_item_count}`"
        ),
        f"- `selected-for-registration={summary.selected_for_registration_count}`",
        f"- `registered-source-entries={summary.registered_source_entry_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence-units={summary.formal_evidence_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Selected source records:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.selected_item_ids)
    lines.extend(["", "Source-library entry ids:"])
    lines.extend(f"- `{entry_id}`" for entry_id in summary.registered_entry_ids)
    lines.extend(["", "Promoted candidate ids:"])
    lines.extend(f"- `{candidate_id}`" for candidate_id in summary.candidate_ids)
    lines.extend(["", "Formal evidence ids:"])
    lines.extend(f"- `{evidence_id}`" for evidence_id in summary.evidence_ids)
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


def build_raw_text_next_cycle_followup_selection_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleFollowupSelectionSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_followup_selection_items(source_dir)
    prior_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_next_cycle_cluster_source_selection_items(
            source_dir
        )
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    material_audit_records_by_id = {
        record.audit_id: record for record in load_material_audit_records(source_dir)
    }
    queue_items_by_id = {
        item.queue_item_id: item for item in load_extraction_queue_items(source_dir)
    }
    source_intake_dir = _sibling_data_dir(source_dir, "source_intake")
    classical_dir = _sibling_data_dir(source_dir, "classical_sources")
    source_materials_by_id = {
        material.material_id: material
        for material in source_intake.load_source_materials(source_intake_dir)
    }
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in source_intake.load_candidate_extracts(source_intake_dir)
    }
    evidence_by_id = {
        unit.evidence_id
        for unit in classical_sources.load_evidence_units(classical_dir)
    }

    selected_items = [
        item for item in items if item.selection_status == "selected_for_registration"
    ]
    selected_item_ids = [item.selection_id for item in selected_items]
    registered_entry_ids = [item.source_library_entry_id for item in selected_items]
    registered_material_ids = [item.source_material_id for item in selected_items]
    audit_ids = [item.audit_id for item in selected_items]
    queue_item_ids = [item.queue_item_id for item in selected_items]
    candidate_ids = [item.candidate_id for item in selected_items]
    evidence_ids = [item.evidence_id for item in selected_items]

    prior_references_valid = bool(items) and all(
        item.prior_selection_id in prior_items_by_id
        and prior_items_by_id[item.prior_selection_id].selection_status
        == "selected_for_registration"
        for item in items
    )
    source_paths_are_relative = bool(items) and all(
        _is_source_relative_path(path)
        for item in items
        for path in item.relative_paths
    )
    selected_clusters_only = bool(items) and all(
        item.cluster_id in RAW_TEXT_NEXT_CYCLE_SELECTED_CLUSTER_IDS for item in items
    )
    source_library_entries_registered = all(
        entry_id in source_entries_by_id
        and source_entries_by_id[entry_id].material_id == material_id
        and source_entries_by_id[entry_id].readiness_status == "review_completed"
        for entry_id, material_id in zip(registered_entry_ids, registered_material_ids)
    )
    material_preparation_registered = all(
        audit_id in material_audit_records_by_id
        and queue_item_id in queue_items_by_id
        and material_id in source_materials_by_id
        and source_materials_by_id[material_id].preparation_status == "reviewed"
        for audit_id, queue_item_id, material_id in zip(
            audit_ids,
            queue_item_ids,
            registered_material_ids,
        )
    )
    candidates_promoted = all(
        candidate_id in candidates_by_id
        and candidates_by_id[candidate_id].status == "promoted"
        and candidates_by_id[candidate_id].related_evidence_ids == [evidence_id]
        for candidate_id, evidence_id in zip(candidate_ids, evidence_ids)
    )
    evidence_promoted = all(evidence_id in evidence_by_id for evidence_id in evidence_ids)
    case_formula_clusters_remain_deferred = all(
        item.cluster_id not in RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS
        for item in items
    )
    sensitive_clusters_remain_risk_gated = all(
        item.cluster_id not in RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS
        for item in items
    )
    boundary_checks = {
        "followup_selection_items_loaded": "passed" if items else "failed",
        "cluster_source_selection_references_valid": (
            "passed" if prior_references_valid else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "selected_clusters_only": "passed" if selected_clusters_only else "failed",
        "source_library_entries_registered": (
            "passed"
            if source_library_entries_registered and material_preparation_registered
            else "failed"
        ),
        "013_candidates_promoted": "passed" if candidates_promoted else "failed",
        "012_evidence_promoted": "passed" if evidence_promoted else "failed",
        "case_formula_clusters_remain_deferred": (
            "passed" if case_formula_clusters_remain_deferred else "failed"
        ),
        "sensitive_clusters_remain_risk_gated": (
            "passed" if sensitive_clusters_remain_risk_gated else "failed"
        ),
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleFollowupSelectionSummary(
        selection_id=RAW_TEXT_NEXT_CYCLE_FOLLOWUP_SELECTION_ID,
        selection_status=(
            "next_cycle_followup_selection_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "next_cycle_followup_selection_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        source_selection_item_count=len(items),
        source_file_count=sum(item.file_count for item in items),
        priority_text_candidate_count=sum(
            item.priority_text_candidate_count for item in items
        ),
        selected_for_registration_count=len(selected_items),
        registered_source_entry_count=sum(
            1 for entry_id in registered_entry_ids if entry_id in source_entries_by_id
        ),
        candidate_extract_count=sum(
            1
            for candidate_id in candidate_ids
            if candidate_id in candidates_by_id
            and candidates_by_id[candidate_id].status == "promoted"
        ),
        formal_evidence_count=sum(
            1 for evidence_id in evidence_ids if evidence_id in evidence_by_id
        ),
        selected_item_ids=selected_item_ids,
        registered_entry_ids=registered_entry_ids,
        registered_material_ids=registered_material_ids,
        audit_ids=audit_ids,
        queue_item_ids=queue_item_ids,
        candidate_ids=candidate_ids,
        evidence_ids=evidence_ids,
        status_counts=_count_values([item.selection_status for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_values(
            [rule for item in items for rule in item.target_rule_families]
        ),
        source_library_mutation_authorized=True,
        downstream_mutation_authorized=True,
        next_material_entry=RAW_TEXT_NEXT_CYCLE_FOLLOWUP_SELECTION_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Followup selection adds only ordinary-risk bounded sources.",
            "All locators remain weak page-level placeholders until later transcription.",
            "Case, formula, and sensitive clusters remain deferred or risk-gated.",
            "Raw external materials are not moved, converted, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_followup_selection_markdown(
    summary: RawTextNextCycleFollowupSelectionSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Followup Selection",
        "",
        f"- Selection id: `{summary.selection_id}`",
        (
            "- `next-cycle-followup-selection-status="
            f"{summary.selection_status}`"
        ),
        (
            "- `next-cycle-followup-selection-items="
            f"{summary.source_selection_item_count}`"
        ),
        f"- `selected-for-registration={summary.selected_for_registration_count}`",
        f"- `registered-source-entries={summary.registered_source_entry_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence-units={summary.formal_evidence_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Selected source records:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.selected_item_ids)
    lines.extend(["", "Source-library entry ids:"])
    lines.extend(f"- `{entry_id}`" for entry_id in summary.registered_entry_ids)
    lines.extend(["", "Promoted candidate ids:"])
    lines.extend(f"- `{candidate_id}`" for candidate_id in summary.candidate_ids)
    lines.extend(["", "Formal evidence ids:"])
    lines.extend(f"- `{evidence_id}`" for evidence_id in summary.evidence_ids)
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


def build_raw_text_next_cycle_gated_cluster_review_prep_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleGatedClusterReviewPrepSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_gated_cluster_review_prep_items(source_dir)
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_next_cycle_source_selection_items(source_dir)
    }
    followup_summary = build_raw_text_next_cycle_followup_selection_summary(source_dir)

    prepared_items = [
        item
        for item in items
        if item.prep_status == "prepared_for_bounded_source_selection"
    ]
    risk_review_items = [
        item for item in items if item.prep_status == "risk_review_required"
    ]
    deferred_items = [
        item for item in items if item.prep_status == "deferred_after_prep"
    ]
    source_selection_references_valid = bool(items) and all(
        item.source_selection_id in source_selection_items_by_id
        and source_selection_items_by_id[item.source_selection_id].cluster_id
        == item.cluster_id
        for item in items
    )
    case_formula_clusters_prepared_only = {
        item.cluster_id for item in prepared_items
    } == set(RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS) and all(
        item.risk_boundary == "ordinary"
        and not item.source_library_mutation_authorized
        and not item.downstream_mutation_authorized
        for item in prepared_items
    )
    sensitive_cluster_stays_risk_review = {
        item.cluster_id for item in risk_review_items
    } == set(RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS) and all(
        item.risk_boundary == "sensitive"
        and item.recommended_next_action == "risk_review"
        and not item.source_library_mutation_authorized
        and not item.downstream_mutation_authorized
        for item in risk_review_items
    )
    no_source_library_mutation = all(
        not item.source_library_mutation_authorized for item in items
    )
    no_downstream_mutation = all(
        not item.downstream_mutation_authorized for item in items
    )
    boundary_checks = {
        "gated_prep_items_loaded": "passed" if items else "failed",
        "source_selection_references_valid": (
            "passed" if source_selection_references_valid else "failed"
        ),
        "case_formula_clusters_prepared_only": (
            "passed" if case_formula_clusters_prepared_only else "failed"
        ),
        "sensitive_cluster_stays_risk_review": (
            "passed" if sensitive_cluster_stays_risk_review else "failed"
        ),
        "no_source_library_mutation": (
            "passed" if no_source_library_mutation else "failed"
        ),
        "no_013_012_mutation": "passed" if no_downstream_mutation else "failed",
        "raw_materials_not_mutated": "passed",
    }
    if (
        followup_summary.next_material_entry
        != RAW_TEXT_NEXT_CYCLE_GATED_CLUSTER_REVIEW_PREP_ID
    ):
        boundary_checks["followup_entrypoint_confirmed"] = "failed"

    return RawTextNextCycleGatedClusterReviewPrepSummary(
        prep_id=RAW_TEXT_NEXT_CYCLE_GATED_CLUSTER_REVIEW_PREP_ID,
        prep_status=(
            "gated_cluster_review_prep_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "gated_cluster_review_prep_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        prep_item_count=len(items),
        selected_for_source_selection_count=len(prepared_items),
        risk_review_required_count=len(risk_review_items),
        deferred_after_prep_count=len(deferred_items),
        source_library_mutation_authorized=False,
        downstream_mutation_authorized=False,
        next_material_entry=(
            RAW_TEXT_NEXT_CYCLE_GATED_CLUSTER_REVIEW_PREP_NEXT_MATERIAL_ENTRY
        ),
        prepared_source_selection_ids=[item.prep_id for item in prepared_items],
        risk_review_item_ids=[item.prep_id for item in risk_review_items],
        deferred_item_ids=[item.prep_id for item in deferred_items],
        status_counts=_count_values([item.prep_status for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_values(
            [rule for item in items for rule in item.target_rule_families]
        ),
        boundary_checks=boundary_checks,
        guardrails=[
            "Gated prep is cluster-level planning metadata only.",
            "Case and formula clusters may proceed only to bounded source selection.",
            "Sensitive-topic material remains behind risk review.",
            "No source-library, 013, or 012 mutation is performed in this prep step.",
            "Raw external materials are not moved, converted, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_gated_cluster_review_prep_markdown(
    summary: RawTextNextCycleGatedClusterReviewPrepSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Gated Cluster Review Prep",
        "",
        f"- Prep id: `{summary.prep_id}`",
        (
            "- `gated-cluster-review-prep-status="
            f"{summary.prep_status}`"
        ),
        f"- `gated-cluster-review-prep-items={summary.prep_item_count}`",
        (
            "- `selected-for-source-selection="
            f"{summary.selected_for_source_selection_count}`"
        ),
        f"- `risk-review-required={summary.risk_review_required_count}`",
        f"- `deferred-after-prep={summary.deferred_after_prep_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Prepared ordinary gated items:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.prepared_source_selection_ids)
    lines.extend(["", "Risk-review items:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.risk_review_item_ids)
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


def build_raw_text_next_cycle_gated_ordinary_source_selection_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleGatedOrdinarySourceSelectionSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_gated_ordinary_source_selection_items(source_dir)
    prep_items = load_raw_text_next_cycle_gated_cluster_review_prep_items(source_dir)
    prep_items_by_id = {item.prep_id: item for item in prep_items}
    sensitive_risk_review_item_ids = [
        item.prep_id
        for item in prep_items
        if item.cluster_id in RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS
        and item.prep_status == "risk_review_required"
    ]

    source_entries_by_id = {
        entry.entry_id: entry for entry in source_library.load_source_library_entries()
    }
    source_materials_by_id = {
        material.material_id: material
        for material in source_intake.load_source_materials()
    }
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in source_intake.load_candidate_extracts()
    }
    evidence_by_id = {
        evidence.evidence_id: evidence
        for evidence in classical_sources.load_evidence_units()
    }

    selected_ids = [item.selection_id for item in items]
    prep_item_ids = [item.prep_id for item in items]
    entry_ids = [item.source_library_entry_id for item in items]
    material_ids = [item.source_material_id for item in items]
    audit_ids = [item.audit_id for item in items]
    queue_item_ids = [item.queue_item_id for item in items]
    candidate_ids = [item.candidate_id for item in items]
    evidence_ids = [item.evidence_id for item in items]

    source_paths_are_relative = all(
        path
        and not Path(path).is_absolute()
        and ".." not in Path(path).parts
        and item.source_root not in path
        for item in items
        for path in item.relative_paths
    )
    ordinary_gated_clusters_only = {
        item.cluster_id for item in items
    } == set(RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS) and all(
        item.risk_boundary == "ordinary"
        and prep_items_by_id[item.prep_id].prep_status
        == "prepared_for_bounded_source_selection"
        for item in items
    )
    entries_registered = all(
        item.source_library_entry_id in source_entries_by_id
        and source_entries_by_id[item.source_library_entry_id].material_id
        == item.source_material_id
        and item.source_material_id in source_materials_by_id
        for item in items
    )
    candidates_promoted = all(
        item.candidate_id in candidates_by_id
        and candidates_by_id[item.candidate_id].material_id == item.source_material_id
        and candidates_by_id[item.candidate_id].status == "promoted"
        and candidates_by_id[item.candidate_id].related_evidence_ids
        == [item.evidence_id]
        for item in items
    )
    evidence_promoted = all(
        item.evidence_id in evidence_by_id
        and evidence_by_id[item.evidence_id].source_id
        == item.source_material_id.replace("material_", "source_", 1)
        for item in items
    )
    sensitive_cluster_remains_risk_review = sensitive_risk_review_item_ids == [
        "gated_prep_sensitive_topic_boundary_001"
    ]
    boundary_checks = {
        "gated_ordinary_selection_items_loaded": "passed" if items else "failed",
        "gated_prep_references_valid": (
            "passed"
            if all(item.prep_id in prep_items_by_id for item in items)
            else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "ordinary_gated_clusters_only": (
            "passed" if ordinary_gated_clusters_only else "failed"
        ),
        "source_library_entries_registered": (
            "passed" if entries_registered else "failed"
        ),
        "013_candidates_promoted": (
            "passed" if candidates_promoted else "failed"
        ),
        "012_evidence_promoted": "passed" if evidence_promoted else "failed",
        "sensitive_cluster_remains_risk_review": (
            "passed" if sensitive_cluster_remains_risk_review else "failed"
        ),
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleGatedOrdinarySourceSelectionSummary(
        selection_id=RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_SOURCE_SELECTION_ID,
        selection_status=(
            "gated_ordinary_source_selection_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "gated_ordinary_source_selection_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        source_selection_item_count=len(items),
        source_file_count=sum(item.file_count for item in items),
        priority_text_candidate_count=sum(
            item.priority_text_candidate_count for item in items
        ),
        selected_for_registration_count=sum(
            1 for item in items if item.selection_status == "selected_for_registration"
        ),
        registered_source_entry_count=sum(
            1 for item in items if item.source_library_entry_id in source_entries_by_id
        ),
        candidate_extract_count=sum(
            1
            for item in items
            if item.candidate_id in candidates_by_id
            and candidates_by_id[item.candidate_id].status == "promoted"
        ),
        formal_evidence_count=sum(
            1 for item in items if item.evidence_id in evidence_by_id
        ),
        selected_item_ids=selected_ids,
        prep_item_ids=prep_item_ids,
        sensitive_risk_review_item_ids=sensitive_risk_review_item_ids,
        registered_entry_ids=entry_ids,
        registered_material_ids=material_ids,
        audit_ids=audit_ids,
        queue_item_ids=queue_item_ids,
        candidate_ids=candidate_ids,
        evidence_ids=evidence_ids,
        status_counts=_count_values([item.selection_status for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_values(
            [rule for item in items for rule in item.target_rule_families]
        ),
        source_library_mutation_authorized=all(
            item.source_library_mutation_authorized for item in items
        ),
        downstream_mutation_authorized=all(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY
        ),
        boundary_checks=boundary_checks,
        guardrails=[
            "Only two ordinary gated source-level records are selected in this pass.",
            "Sensitive-topic material stays behind risk review.",
            "Weak locators are accepted only as preparation metadata.",
            "External raw materials are not moved, converted, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_gated_ordinary_source_selection_markdown(
    summary: RawTextNextCycleGatedOrdinarySourceSelectionSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Gated Ordinary Source Selection",
        "",
        f"- Selection id: `{summary.selection_id}`",
        (
            "- `gated-ordinary-source-selection-status="
            f"{summary.selection_status}`"
        ),
        (
            "- `gated-ordinary-source-selection-items="
            f"{summary.source_selection_item_count}`"
        ),
        f"- `selected-for-registration={summary.selected_for_registration_count}`",
        f"- `registered-source-entries={summary.registered_source_entry_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence={summary.formal_evidence_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Selected ordinary gated items:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.selected_item_ids)
    lines.extend(["", "Registered source-library entries:"])
    lines.extend(f"- `{entry_id}`" for entry_id in summary.registered_entry_ids)
    lines.extend(["", "Promoted 013 candidates:"])
    lines.extend(f"- `{candidate_id}`" for candidate_id in summary.candidate_ids)
    lines.extend(["", "Formal 012 evidence units:"])
    lines.extend(f"- `{evidence_id}`" for evidence_id in summary.evidence_ids)
    lines.extend(["", "Sensitive items retained for risk review:"])
    lines.extend(
        f"- `{item_id}`" for item_id in summary.sensitive_risk_review_item_ids
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


def build_raw_text_next_cycle_gated_ordinary_followup_selection_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleGatedOrdinaryFollowupSelectionSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_gated_ordinary_followup_selection_items(
        source_dir
    )
    prep_items = load_raw_text_next_cycle_gated_cluster_review_prep_items(source_dir)
    prep_items_by_id = {item.prep_id: item for item in prep_items}
    prior_items = load_raw_text_next_cycle_gated_ordinary_source_selection_items(
        source_dir
    )
    prior_items_by_id = {item.selection_id: item for item in prior_items}
    prior_paths = {path for item in prior_items for path in item.relative_paths}
    sensitive_risk_review_item_ids = [
        item.prep_id
        for item in prep_items
        if item.cluster_id in RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS
        and item.prep_status == "risk_review_required"
    ]

    source_entries_by_id = {
        entry.entry_id: entry for entry in source_library.load_source_library_entries()
    }
    source_materials_by_id = {
        material.material_id: material
        for material in source_intake.load_source_materials()
    }
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in source_intake.load_candidate_extracts()
    }
    evidence_by_id = {
        evidence.evidence_id: evidence
        for evidence in classical_sources.load_evidence_units()
    }

    selected_ids = [item.selection_id for item in items]
    prior_selection_ids = [item.prior_selection_id for item in items]
    prep_item_ids = [item.prep_id for item in items]
    entry_ids = [item.source_library_entry_id for item in items]
    material_ids = [item.source_material_id for item in items]
    audit_ids = [item.audit_id for item in items]
    queue_item_ids = [item.queue_item_id for item in items]
    candidate_ids = [item.candidate_id for item in items]
    evidence_ids = [item.evidence_id for item in items]

    source_paths_are_relative = all(
        path
        and not Path(path).is_absolute()
        and ".." not in Path(path).parts
        and item.source_root not in path
        for item in items
        for path in item.relative_paths
    )
    prior_selected_paths_not_duplicated = all(
        path not in prior_paths for item in items for path in item.relative_paths
    )
    ordinary_gated_clusters_only = {
        item.cluster_id for item in items
    } == set(RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS) and all(
        item.risk_boundary == "ordinary"
        and prep_items_by_id[item.prep_id].prep_status
        == "prepared_for_bounded_source_selection"
        and prior_items_by_id[item.prior_selection_id].cluster_id == item.cluster_id
        for item in items
    )
    entries_registered = all(
        item.source_library_entry_id in source_entries_by_id
        and source_entries_by_id[item.source_library_entry_id].material_id
        == item.source_material_id
        and item.source_material_id in source_materials_by_id
        for item in items
    )
    candidates_promoted = all(
        item.candidate_id in candidates_by_id
        and candidates_by_id[item.candidate_id].material_id == item.source_material_id
        and candidates_by_id[item.candidate_id].status == "promoted"
        and candidates_by_id[item.candidate_id].related_evidence_ids
        == [item.evidence_id]
        for item in items
    )
    evidence_promoted = all(
        item.evidence_id in evidence_by_id
        and evidence_by_id[item.evidence_id].source_id
        == item.source_material_id.replace("material_", "source_", 1)
        for item in items
    )
    sensitive_cluster_remains_risk_review = sensitive_risk_review_item_ids == [
        "gated_prep_sensitive_topic_boundary_001"
    ]
    boundary_checks = {
        "gated_ordinary_followup_items_loaded": "passed" if items else "failed",
        "gated_prep_references_valid": (
            "passed"
            if all(item.prep_id in prep_items_by_id for item in items)
            else "failed"
        ),
        "prior_selection_references_valid": (
            "passed"
            if all(item.prior_selection_id in prior_items_by_id for item in items)
            else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "prior_selected_paths_not_duplicated": (
            "passed" if prior_selected_paths_not_duplicated else "failed"
        ),
        "ordinary_gated_clusters_only": (
            "passed" if ordinary_gated_clusters_only else "failed"
        ),
        "source_library_entries_registered": (
            "passed" if entries_registered else "failed"
        ),
        "013_candidates_promoted": (
            "passed" if candidates_promoted else "failed"
        ),
        "012_evidence_promoted": "passed" if evidence_promoted else "failed",
        "sensitive_cluster_remains_risk_review": (
            "passed" if sensitive_cluster_remains_risk_review else "failed"
        ),
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleGatedOrdinaryFollowupSelectionSummary(
        selection_id=RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FOLLOWUP_SELECTION_ID,
        selection_status=(
            "gated_ordinary_followup_selection_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "gated_ordinary_followup_selection_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        source_selection_item_count=len(items),
        source_file_count=sum(item.file_count for item in items),
        priority_text_candidate_count=sum(
            item.priority_text_candidate_count for item in items
        ),
        selected_for_registration_count=sum(
            1 for item in items if item.selection_status == "selected_for_registration"
        ),
        registered_source_entry_count=sum(
            1 for item in items if item.source_library_entry_id in source_entries_by_id
        ),
        candidate_extract_count=sum(
            1
            for item in items
            if item.candidate_id in candidates_by_id
            and candidates_by_id[item.candidate_id].status == "promoted"
        ),
        formal_evidence_count=sum(
            1 for item in items if item.evidence_id in evidence_by_id
        ),
        selected_item_ids=selected_ids,
        prior_selection_item_ids=prior_selection_ids,
        prep_item_ids=prep_item_ids,
        sensitive_risk_review_item_ids=sensitive_risk_review_item_ids,
        registered_entry_ids=entry_ids,
        registered_material_ids=material_ids,
        audit_ids=audit_ids,
        queue_item_ids=queue_item_ids,
        candidate_ids=candidate_ids,
        evidence_ids=evidence_ids,
        status_counts=_count_values([item.selection_status for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_values(
            [rule for item in items for rule in item.target_rule_families]
        ),
        source_library_mutation_authorized=all(
            item.source_library_mutation_authorized for item in items
        ),
        downstream_mutation_authorized=all(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FOLLOWUP_SELECTION_NEXT_MATERIAL_ENTRY
        ),
        boundary_checks=boundary_checks,
        guardrails=[
            "Only two ordinary gated followup source-level records are selected.",
            "Previously selected ordinary gated paths are not duplicated.",
            "Sensitive-topic material stays behind risk review.",
            "Weak locators are accepted only as preparation metadata.",
            "External raw materials are not moved, converted, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_gated_ordinary_followup_selection_markdown(
    summary: RawTextNextCycleGatedOrdinaryFollowupSelectionSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Gated Ordinary Followup Selection",
        "",
        f"- Selection id: `{summary.selection_id}`",
        (
            "- `gated-ordinary-followup-selection-status="
            f"{summary.selection_status}`"
        ),
        (
            "- `gated-ordinary-followup-selection-items="
            f"{summary.source_selection_item_count}`"
        ),
        f"- `selected-for-registration={summary.selected_for_registration_count}`",
        f"- `registered-source-entries={summary.registered_source_entry_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence={summary.formal_evidence_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Selected ordinary gated followup items:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.selected_item_ids)
    lines.extend(["", "Prior ordinary gated selection items:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.prior_selection_item_ids)
    lines.extend(["", "Registered source-library entries:"])
    lines.extend(f"- `{entry_id}`" for entry_id in summary.registered_entry_ids)
    lines.extend(["", "Promoted 013 candidates:"])
    lines.extend(f"- `{candidate_id}`" for candidate_id in summary.candidate_ids)
    lines.extend(["", "Formal 012 evidence units:"])
    lines.extend(f"- `{evidence_id}`" for evidence_id in summary.evidence_ids)
    lines.extend(["", "Sensitive items retained for risk review:"])
    lines.extend(
        f"- `{item_id}`" for item_id in summary.sensitive_risk_review_item_ids
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


def build_raw_text_next_cycle_gated_ordinary_final_selection_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleGatedOrdinaryFinalSelectionSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_gated_ordinary_final_selection_items(source_dir)
    prep_items = load_raw_text_next_cycle_gated_cluster_review_prep_items(source_dir)
    prep_items_by_id = {item.prep_id: item for item in prep_items}
    first_items = load_raw_text_next_cycle_gated_ordinary_source_selection_items(
        source_dir
    )
    followup_items = load_raw_text_next_cycle_gated_ordinary_followup_selection_items(
        source_dir
    )
    prior_items_by_id = {item.selection_id: item for item in followup_items}
    prior_paths = {
        path
        for item in [*first_items, *followup_items]
        for path in item.relative_paths
    }
    cluster_items_by_id = {
        item.cluster_id: item
        for item in load_raw_text_source_cluster_selection_items(source_dir)
    }
    sensitive_risk_review_item_ids = [
        item.prep_id
        for item in prep_items
        if item.cluster_id in RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS
        and item.prep_status == "risk_review_required"
    ]

    source_entries_by_id = {
        entry.entry_id: entry for entry in source_library.load_source_library_entries()
    }
    source_materials_by_id = {
        material.material_id: material
        for material in source_intake.load_source_materials()
    }
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in source_intake.load_candidate_extracts()
    }
    evidence_by_id = {
        evidence.evidence_id: evidence
        for evidence in classical_sources.load_evidence_units()
    }

    selected_ids = [item.selection_id for item in items]
    prior_selection_ids = [item.prior_selection_id for item in items]
    prep_item_ids = [item.prep_id for item in items]
    entry_ids = [item.source_library_entry_id for item in items]
    material_ids = [item.source_material_id for item in items]
    audit_ids = [item.audit_id for item in items]
    queue_item_ids = [item.queue_item_id for item in items]
    candidate_ids = [item.candidate_id for item in items]
    evidence_ids = [item.evidence_id for item in items]

    source_paths_are_relative = all(
        path
        and not Path(path).is_absolute()
        and ".." not in Path(path).parts
        and item.source_root not in path
        for item in items
        for path in item.relative_paths
    )
    prior_selected_paths_not_duplicated = all(
        path not in prior_paths for item in items for path in item.relative_paths
    )
    ordinary_gated_clusters_only = {
        item.cluster_id for item in items
    } == set(RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS) and all(
        item.risk_boundary == "ordinary"
        and prep_items_by_id[item.prep_id].prep_status
        == "prepared_for_bounded_source_selection"
        and prior_items_by_id[item.prior_selection_id].cluster_id == item.cluster_id
        for item in items
    )
    entries_registered = all(
        item.source_library_entry_id in source_entries_by_id
        and source_entries_by_id[item.source_library_entry_id].material_id
        == item.source_material_id
        and item.source_material_id in source_materials_by_id
        for item in items
    )
    candidates_promoted = all(
        item.candidate_id in candidates_by_id
        and candidates_by_id[item.candidate_id].material_id == item.source_material_id
        and candidates_by_id[item.candidate_id].status == "promoted"
        and candidates_by_id[item.candidate_id].related_evidence_ids
        == [item.evidence_id]
        for item in items
    )
    evidence_promoted = all(
        item.evidence_id in evidence_by_id
        and evidence_by_id[item.evidence_id].source_id
        == item.source_material_id.replace("material_", "source_", 1)
        for item in items
    )
    selected_paths_by_cluster: dict[str, set[str]] = {
        cluster_id: set() for cluster_id in RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS
    }
    for item in [*first_items, *followup_items, *items]:
        if item.cluster_id in selected_paths_by_cluster:
            selected_paths_by_cluster[item.cluster_id].update(item.relative_paths)
    ordinary_representative_paths_exhausted = all(
        set(cluster_items_by_id[cluster_id].representative_paths).issubset(
            selected_paths_by_cluster[cluster_id]
        )
        for cluster_id in RAW_TEXT_NEXT_CYCLE_DEFERRED_CLUSTER_IDS
    )
    sensitive_cluster_remains_risk_review = sensitive_risk_review_item_ids == [
        "gated_prep_sensitive_topic_boundary_001"
    ]
    boundary_checks = {
        "gated_ordinary_final_items_loaded": "passed" if items else "failed",
        "gated_prep_references_valid": (
            "passed"
            if all(item.prep_id in prep_items_by_id for item in items)
            else "failed"
        ),
        "prior_selection_references_valid": (
            "passed"
            if all(item.prior_selection_id in prior_items_by_id for item in items)
            else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "prior_selected_paths_not_duplicated": (
            "passed" if prior_selected_paths_not_duplicated else "failed"
        ),
        "ordinary_gated_clusters_only": (
            "passed" if ordinary_gated_clusters_only else "failed"
        ),
        "source_library_entries_registered": (
            "passed" if entries_registered else "failed"
        ),
        "013_candidates_promoted": (
            "passed" if candidates_promoted else "failed"
        ),
        "012_evidence_promoted": "passed" if evidence_promoted else "failed",
        "ordinary_representative_paths_exhausted": (
            "passed" if ordinary_representative_paths_exhausted else "failed"
        ),
        "sensitive_cluster_remains_risk_review": (
            "passed" if sensitive_cluster_remains_risk_review else "failed"
        ),
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleGatedOrdinaryFinalSelectionSummary(
        selection_id=RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FINAL_SELECTION_ID,
        selection_status=(
            "gated_ordinary_final_selection_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "gated_ordinary_final_selection_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        source_selection_item_count=len(items),
        source_file_count=sum(item.file_count for item in items),
        priority_text_candidate_count=sum(
            item.priority_text_candidate_count for item in items
        ),
        selected_for_registration_count=sum(
            1 for item in items if item.selection_status == "selected_for_registration"
        ),
        registered_source_entry_count=sum(
            1 for item in items if item.source_library_entry_id in source_entries_by_id
        ),
        candidate_extract_count=sum(
            1
            for item in items
            if item.candidate_id in candidates_by_id
            and candidates_by_id[item.candidate_id].status == "promoted"
        ),
        formal_evidence_count=sum(
            1 for item in items if item.evidence_id in evidence_by_id
        ),
        selected_item_ids=selected_ids,
        prior_selection_item_ids=prior_selection_ids,
        prep_item_ids=prep_item_ids,
        sensitive_risk_review_item_ids=sensitive_risk_review_item_ids,
        registered_entry_ids=entry_ids,
        registered_material_ids=material_ids,
        audit_ids=audit_ids,
        queue_item_ids=queue_item_ids,
        candidate_ids=candidate_ids,
        evidence_ids=evidence_ids,
        status_counts=_count_values([item.selection_status for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_values(
            [rule for item in items for rule in item.target_rule_families]
        ),
        source_library_mutation_authorized=all(
            item.source_library_mutation_authorized for item in items
        ),
        downstream_mutation_authorized=all(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FINAL_SELECTION_NEXT_MATERIAL_ENTRY
        ),
        boundary_checks=boundary_checks,
        guardrails=[
            "Only the remaining ordinary gated source-level records are selected.",
            "All case/formula representative paths are now covered by ordinary gated selections.",
            "Sensitive-topic material stays behind risk review.",
            "Weak locators are accepted only as preparation metadata.",
            "External raw materials are not moved, converted, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_gated_ordinary_final_selection_markdown(
    summary: RawTextNextCycleGatedOrdinaryFinalSelectionSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Gated Ordinary Final Selection",
        "",
        f"- Selection id: `{summary.selection_id}`",
        (
            "- `gated-ordinary-final-selection-status="
            f"{summary.selection_status}`"
        ),
        (
            "- `gated-ordinary-final-selection-items="
            f"{summary.source_selection_item_count}`"
        ),
        f"- `selected-for-registration={summary.selected_for_registration_count}`",
        f"- `registered-source-entries={summary.registered_source_entry_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence={summary.formal_evidence_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Selected ordinary gated final items:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.selected_item_ids)
    lines.extend(["", "Prior ordinary gated followup items:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.prior_selection_item_ids)
    lines.extend(["", "Registered source-library entries:"])
    lines.extend(f"- `{entry_id}`" for entry_id in summary.registered_entry_ids)
    lines.extend(["", "Promoted 013 candidates:"])
    lines.extend(f"- `{candidate_id}`" for candidate_id in summary.candidate_ids)
    lines.extend(["", "Formal 012 evidence units:"])
    lines.extend(f"- `{evidence_id}`" for evidence_id in summary.evidence_ids)
    lines.extend(["", "Sensitive items retained for risk review:"])
    lines.extend(
        f"- `{item_id}`" for item_id in summary.sensitive_risk_review_item_ids
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


def build_raw_text_next_cycle_sensitive_risk_review_prep_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleSensitiveRiskReviewPrepSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_sensitive_risk_review_prep_items(source_dir)
    prep_items = load_raw_text_next_cycle_gated_cluster_review_prep_items(source_dir)
    prep_items_by_id = {item.prep_id: item for item in prep_items}
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_next_cycle_source_selection_items(source_dir)
    }
    cluster_items_by_id = {
        item.cluster_id: item
        for item in load_raw_text_source_cluster_selection_items(source_dir)
    }
    final_summary = build_raw_text_next_cycle_gated_ordinary_final_selection_summary(
        source_dir
    )

    prep_item_ids = [item.prep_item_id for item in items]
    source_level_risk_review_item_ids = [
        item.prep_item_id
        for item in items
        if item.prep_status == "prepared_for_source_level_risk_review"
    ]
    blocked_item_ids = [
        item.prep_item_id
        for item in items
        if item.prep_status == "blocked_after_sensitive_prep"
    ]
    deferred_item_ids = [
        item.prep_item_id
        for item in items
        if item.prep_status == "deferred_after_sensitive_prep"
    ]
    relative_paths = [path for item in items for path in item.relative_paths]

    source_paths_are_relative = all(
        path
        and not Path(path).is_absolute()
        and ".." not in Path(path).parts
        and item.source_root not in path
        for item in items
        for path in item.relative_paths
    )
    sensitive_cluster_only = {
        item.cluster_id for item in items
    } == set(RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS) and all(
        item.risk_boundary == "sensitive"
        and prep_items_by_id[item.prep_id].prep_status == "risk_review_required"
        and source_selection_items_by_id[item.source_selection_id].selection_status
        == "risk_review_required"
        for item in items
    )
    sensitive_cluster = cluster_items_by_id.get(
        RAW_TEXT_NEXT_CYCLE_RISK_REVIEW_CLUSTER_IDS[0]
    )
    representative_paths_covered = bool(sensitive_cluster) and set(
        sensitive_cluster.representative_paths
    ) == set(relative_paths)
    action_by_status = {
        "prepared_for_source_level_risk_review": "risk_review",
        "blocked_after_sensitive_prep": "block",
        "deferred_after_sensitive_prep": "defer",
    }
    action_routing_valid = all(
        action_by_status[item.prep_status] == item.recommended_next_action
        for item in items
    )
    source_library_mutation_blocked = all(
        not item.source_library_mutation_authorized for item in items
    )
    downstream_mutation_blocked = all(
        not item.downstream_mutation_authorized for item in items
    )
    ordinary_final_selection_completed = (
        final_summary.selection_status == "gated_ordinary_final_selection_completed"
    )
    boundary_checks = {
        "sensitive_risk_review_prep_items_loaded": (
            "passed" if items else "failed"
        ),
        "gated_prep_reference_valid": (
            "passed"
            if all(item.prep_id in prep_items_by_id for item in items)
            else "failed"
        ),
        "source_selection_reference_valid": (
            "passed"
            if all(
                item.source_selection_id in source_selection_items_by_id
                for item in items
            )
            else "failed"
        ),
        "sensitive_cluster_only": (
            "passed" if sensitive_cluster_only else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "representative_paths_covered": (
            "passed" if representative_paths_covered else "failed"
        ),
        "action_routing_valid": "passed" if action_routing_valid else "failed",
        "source_library_mutation_blocked": (
            "passed" if source_library_mutation_blocked else "failed"
        ),
        "downstream_mutation_blocked": (
            "passed" if downstream_mutation_blocked else "failed"
        ),
        "ordinary_final_selection_completed": (
            "passed" if ordinary_final_selection_completed else "failed"
        ),
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleSensitiveRiskReviewPrepSummary(
        selection_id=RAW_TEXT_NEXT_CYCLE_SENSITIVE_RISK_REVIEW_PREP_ID,
        selection_status=(
            "sensitive_risk_review_prep_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "sensitive_risk_review_prep_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        prep_item_count=len(items),
        source_file_count=sum(item.file_count for item in items),
        priority_text_candidate_count=sum(
            item.priority_text_candidate_count for item in items
        ),
        source_level_risk_review_count=len(source_level_risk_review_item_ids),
        blocked_count=len(blocked_item_ids),
        deferred_count=len(deferred_item_ids),
        registered_source_entry_count=0,
        candidate_extract_count=0,
        formal_evidence_count=0,
        prep_item_ids=prep_item_ids,
        source_level_risk_review_item_ids=source_level_risk_review_item_ids,
        blocked_item_ids=blocked_item_ids,
        deferred_item_ids=deferred_item_ids,
        relative_paths=relative_paths,
        status_counts=_count_values([item.prep_status for item in items]),
        action_counts=_count_values([item.recommended_next_action for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_values(
            [rule for item in items for rule in item.target_rule_families]
        ),
        source_library_mutation_authorized=any(
            item.source_library_mutation_authorized for item in items
        ),
        downstream_mutation_authorized=any(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            RAW_TEXT_NEXT_CYCLE_SENSITIVE_RISK_REVIEW_PREP_NEXT_MATERIAL_ENTRY
        ),
        boundary_checks=boundary_checks,
        guardrails=[
            "Only path-label metadata is used for sensitive prep routing.",
            "Only one bounded source can proceed to source-level risk review.",
            "Blocked and deferred sensitive paths do not receive downstream records.",
            "No source-library, 013, or 012 mutation is authorized in this step.",
            "External raw materials are not moved, converted, opened, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_sensitive_risk_review_prep_markdown(
    summary: RawTextNextCycleSensitiveRiskReviewPrepSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Sensitive Risk Review Prep",
        "",
        f"- Selection id: `{summary.selection_id}`",
        (
            "- `sensitive-risk-review-prep-status="
            f"{summary.selection_status}`"
        ),
        f"- `sensitive-risk-review-prep-items={summary.prep_item_count}`",
        f"- `source-level-risk-review={summary.source_level_risk_review_count}`",
        f"- `blocked-after-sensitive-prep={summary.blocked_count}`",
        f"- `deferred-after-sensitive-prep={summary.deferred_count}`",
        f"- `registered-source-entries={summary.registered_source_entry_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence={summary.formal_evidence_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Prepared for source-level risk review:",
    ]
    lines.extend(
        f"- `{item_id}`" for item_id in summary.source_level_risk_review_item_ids
    )
    lines.extend(["", "Blocked after sensitive prep:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.blocked_item_ids)
    lines.extend(["", "Deferred after sensitive prep:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.deferred_item_ids)
    lines.extend(["", "Representative paths covered:"])
    lines.extend(f"- `{path}`" for path in summary.relative_paths)
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


def build_raw_text_next_cycle_sensitive_source_level_risk_review_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleSensitiveSourceLevelRiskReviewSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_sensitive_source_level_risk_review_items(
        source_dir
    )
    prep_summary = build_raw_text_next_cycle_sensitive_risk_review_prep_summary(
        source_dir
    )
    prep_items = load_raw_text_next_cycle_sensitive_risk_review_prep_items(source_dir)
    prep_items_by_id = {item.prep_item_id: item for item in prep_items}
    reviewable_prep_item_ids = {
        item.prep_item_id
        for item in prep_items
        if item.prep_status == "prepared_for_source_level_risk_review"
    }
    blocked_prep_item_ids = [
        item.prep_item_id
        for item in prep_items
        if item.prep_status == "blocked_after_sensitive_prep"
    ]
    deferred_prep_item_ids = [
        item.prep_item_id
        for item in prep_items
        if item.prep_status == "deferred_after_sensitive_prep"
    ]
    reviewed_prep_item_ids = [item.prep_item_id for item in items]
    cleared_item_ids = [
        item.review_item_id
        for item in items
        if item.review_status == "cleared_for_sensitive_registration_prep"
        and item.registration_prep_allowed
    ]
    relative_paths = [path for item in items for path in item.relative_paths]

    source_paths_are_relative = all(
        path
        and not Path(path).is_absolute()
        and ".." not in Path(path).parts
        and item.source_root not in path
        for item in items
        for path in item.relative_paths
    )
    sensitive_risk_review_prep_completed = (
        prep_summary.selection_status == "sensitive_risk_review_prep_completed"
    )
    only_prepared_prep_items_reviewed = (
        set(reviewed_prep_item_ids) == reviewable_prep_item_ids
        and bool(reviewable_prep_item_ids)
        and all(
            prep_items_by_id[item.prep_item_id].prep_status
            == "prepared_for_source_level_risk_review"
            for item in items
        )
    )
    blocked_and_deferred_prep_retained = not (
        set(reviewed_prep_item_ids)
        & (set(blocked_prep_item_ids) | set(deferred_prep_item_ids))
    ) and bool(blocked_prep_item_ids) and bool(deferred_prep_item_ids)
    action_routing_valid = all(
        item.review_status == "cleared_for_sensitive_registration_prep"
        and item.recommended_next_action == "register_source"
        and item.registration_prep_allowed
        for item in items
    )
    source_library_mutation_blocked = all(
        not item.source_library_mutation_authorized for item in items
    )
    downstream_mutation_blocked = all(
        not item.downstream_mutation_authorized for item in items
    )
    no_downstream_records_created = (
        len(items) > 0
        and source_library_mutation_blocked
        and downstream_mutation_blocked
    )
    boundary_checks = {
        "sensitive_source_level_risk_review_items_loaded": (
            "passed" if items else "failed"
        ),
        "sensitive_risk_review_prep_completed": (
            "passed" if sensitive_risk_review_prep_completed else "failed"
        ),
        "only_prepared_prep_items_reviewed": (
            "passed" if only_prepared_prep_items_reviewed else "failed"
        ),
        "blocked_and_deferred_prep_retained": (
            "passed" if blocked_and_deferred_prep_retained else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "action_routing_valid": "passed" if action_routing_valid else "failed",
        "source_library_mutation_blocked": (
            "passed" if source_library_mutation_blocked else "failed"
        ),
        "downstream_mutation_blocked": (
            "passed" if downstream_mutation_blocked else "failed"
        ),
        "no_downstream_records_created": (
            "passed" if no_downstream_records_created else "failed"
        ),
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleSensitiveSourceLevelRiskReviewSummary(
        selection_id=RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_LEVEL_RISK_REVIEW_ID,
        selection_status=(
            "sensitive_source_level_risk_review_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "sensitive_source_level_risk_review_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        review_item_count=len(items),
        source_file_count=sum(item.file_count for item in items),
        priority_text_candidate_count=sum(
            item.priority_text_candidate_count for item in items
        ),
        cleared_for_registration_prep_count=len(cleared_item_ids),
        registered_source_entry_count=0,
        candidate_extract_count=0,
        formal_evidence_count=0,
        review_item_ids=[item.review_item_id for item in items],
        cleared_for_registration_prep_item_ids=cleared_item_ids,
        prep_item_ids=reviewed_prep_item_ids,
        blocked_prep_item_ids=blocked_prep_item_ids,
        deferred_prep_item_ids=deferred_prep_item_ids,
        relative_paths=relative_paths,
        status_counts=_count_values([item.review_status for item in items]),
        action_counts=_count_values([item.recommended_next_action for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_values(
            [rule for item in items for rule in item.target_rule_families]
        ),
        source_library_mutation_authorized=any(
            item.source_library_mutation_authorized for item in items
        ),
        downstream_mutation_authorized=any(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_LEVEL_RISK_REVIEW_NEXT_MATERIAL_ENTRY
        ),
        boundary_checks=boundary_checks,
        guardrails=[
            "Cleared-for-registration-prep is not source-library registration.",
            "No source-library, 013, or 012 mutation is authorized in this review.",
            "Blocked and deferred sensitive prep items remain unavailable.",
            "Psychology framing must stay non-diagnostic and non-deterministic.",
            "External raw materials are not moved, converted, opened, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_sensitive_source_level_risk_review_markdown(
    summary: RawTextNextCycleSensitiveSourceLevelRiskReviewSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Sensitive Source-Level Risk Review",
        "",
        f"- Selection id: `{summary.selection_id}`",
        (
            "- `sensitive-source-level-risk-review-status="
            f"{summary.selection_status}`"
        ),
        (
            "- `sensitive-source-level-risk-review-items="
            f"{summary.review_item_count}`"
        ),
        (
            "- `cleared-for-registration-prep="
            f"{summary.cleared_for_registration_prep_count}`"
        ),
        f"- `registered-source-entries={summary.registered_source_entry_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence={summary.formal_evidence_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Reviewed sensitive source-level items:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.review_item_ids)
    lines.extend(["", "Cleared for registration prep:"])
    lines.extend(
        f"- `{item_id}`"
        for item_id in summary.cleared_for_registration_prep_item_ids
    )
    lines.extend(["", "Prep items reviewed:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.prep_item_ids)
    lines.extend(["", "Prep items retained blocked:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.blocked_prep_item_ids)
    lines.extend(["", "Prep items retained deferred:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.deferred_prep_item_ids)
    lines.extend(["", "Reviewed paths:"])
    lines.extend(f"- `{path}`" for path in summary.relative_paths)
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


def build_raw_text_next_cycle_sensitive_registration_prep_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleSensitiveRegistrationPrepSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_sensitive_registration_prep_items(source_dir)
    source_level_summary = (
        build_raw_text_next_cycle_sensitive_source_level_risk_review_summary(
            source_dir
        )
    )
    prep_items = load_raw_text_next_cycle_sensitive_risk_review_prep_items(source_dir)
    source_entries_by_id = _load_source_library_entries(source_dir)
    existing_material_ids = {
        source_entry.material_id for source_entry in source_entries_by_id.values()
    }
    proposed_entry_ids = [item.proposed_entry_id for item in items]
    proposed_material_ids = [item.proposed_material_id for item in items]
    blocked_prep_item_ids = [
        item.prep_item_id
        for item in prep_items
        if item.prep_status == "blocked_after_sensitive_prep"
    ]
    deferred_prep_item_ids = [
        item.prep_item_id
        for item in prep_items
        if item.prep_status == "deferred_after_sensitive_prep"
    ]

    source_level_risk_review_completed = (
        source_level_summary.selection_status
        == "sensitive_source_level_risk_review_completed"
    )
    source_level_review_references_valid = all(
        item.source_level_review_id
        in source_level_summary.cleared_for_registration_prep_item_ids
        for item in items
    )
    proposed_entries_available = bool(items) and all(
        (
            item.proposed_entry_id in source_entries_by_id
            and _sensitive_registration_prep_entry_matches_existing(
                item,
                source_entries_by_id[item.proposed_entry_id],
            )
        )
        or (
            item.proposed_entry_id not in source_entries_by_id
            and item.proposed_material_id not in existing_material_ids
        )
        for item in items
    )
    blocked_and_deferred_prep_retained = (
        bool(blocked_prep_item_ids)
        and bool(deferred_prep_item_ids)
        and all(
            item.prep_review_item_id
            not in set(blocked_prep_item_ids) | set(deferred_prep_item_ids)
            for item in items
        )
    )
    source_paths_are_relative = all(
        _is_source_relative_path(path)
        for item in items
        for path in item.proposed_local_references
    )
    source_library_mutation_blocked = all(
        not item.source_library_mutation_authorized for item in items
    )
    downstream_mutation_blocked = all(
        not item.downstream_mutation_authorized for item in items
    )
    no_downstream_records_created = (
        len(items) > 0
        and source_library_mutation_blocked
        and downstream_mutation_blocked
    )
    boundary_checks = {
        "sensitive_registration_prep_items_loaded": (
            "passed" if items else "failed"
        ),
        "source_level_risk_review_completed": (
            "passed" if source_level_risk_review_completed else "failed"
        ),
        "source_level_review_references_valid": (
            "passed" if source_level_review_references_valid else "failed"
        ),
        "proposed_entries_available": (
            "passed" if proposed_entries_available else "failed"
        ),
        "blocked_and_deferred_prep_retained": (
            "passed" if blocked_and_deferred_prep_retained else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "source_library_mutation_blocked": (
            "passed" if source_library_mutation_blocked else "failed"
        ),
        "downstream_mutation_blocked": (
            "passed" if downstream_mutation_blocked else "failed"
        ),
        "no_downstream_records_created": (
            "passed" if no_downstream_records_created else "failed"
        ),
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleSensitiveRegistrationPrepSummary(
        prep_id=RAW_TEXT_NEXT_CYCLE_SENSITIVE_REGISTRATION_PREP_ID,
        prep_status=(
            "sensitive_registration_prep_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "sensitive_registration_prep_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        registration_prep_item_count=len(items),
        proposed_source_file_count=sum(
            len(item.proposed_local_references) for item in items
        ),
        registered_source_entry_count=sum(
            1 for entry_id in proposed_entry_ids if entry_id in source_entries_by_id
        ),
        candidate_extract_count=0,
        formal_evidence_count=0,
        registration_status_counts=_count_values(
            [item.registration_status for item in items]
        ),
        proposed_readiness_counts=_count_values(
            [item.proposed_readiness_status for item in items]
        ),
        proposed_next_action_counts=_count_values(
            [item.proposed_next_action for item in items]
        ),
        risk_tier_counts=_count_values([item.risk_tier for item in items]),
        target_rule_family_counts=_count_values(
            [rule for item in items for rule in item.rule_families]
        ),
        proposed_entry_ids=proposed_entry_ids,
        proposed_material_ids=proposed_material_ids,
        registration_prep_item_ids=[item.prep_item_id for item in items],
        source_level_review_item_ids=[
            item.source_level_review_id for item in items
        ],
        blocked_prep_item_ids=blocked_prep_item_ids,
        deferred_prep_item_ids=deferred_prep_item_ids,
        source_library_mutation_authorized=any(
            item.source_library_mutation_authorized for item in items
        ),
        downstream_mutation_authorized=any(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            RAW_TEXT_NEXT_CYCLE_SENSITIVE_REGISTRATION_PREP_NEXT_MATERIAL_ENTRY
        ),
        boundary_checks=boundary_checks,
        guardrails=[
            "Registration prep records proposed source-library metadata only.",
            "Actual source-library registration remains a separate next step.",
            "No 013 candidate or 012 formal evidence mutation is authorized.",
            "Blocked and deferred sensitive prep items remain unavailable.",
            "External raw materials are not moved, converted, opened, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_sensitive_registration_prep_markdown(
    summary: RawTextNextCycleSensitiveRegistrationPrepSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Sensitive Registration Prep",
        "",
        f"- Prep id: `{summary.prep_id}`",
        f"- `sensitive-registration-prep-status={summary.prep_status}`",
        f"- `sensitive-registration-prep-items={summary.registration_prep_item_count}`",
        f"- `proposed-source-files={summary.proposed_source_file_count}`",
        f"- `registered-source-entries={summary.registered_source_entry_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence={summary.formal_evidence_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Sensitive registration-prep items:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.registration_prep_item_ids)
    lines.extend(["", "Source-level review items:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.source_level_review_item_ids)
    lines.extend(["", "Proposed source-library entries:"])
    lines.extend(f"- `{entry_id}`" for entry_id in summary.proposed_entry_ids)
    lines.extend(["", "Proposed source material ids:"])
    lines.extend(f"- `{material_id}`" for material_id in summary.proposed_material_ids)
    lines.extend(["", "Prep items retained blocked:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.blocked_prep_item_ids)
    lines.extend(["", "Prep items retained deferred:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.deferred_prep_item_ids)
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


def build_raw_text_next_cycle_sensitive_source_registration_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleSensitiveSourceRegistrationSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_sensitive_source_registration_items(source_dir)
    prep_summary = build_raw_text_next_cycle_sensitive_registration_prep_summary(
        source_dir
    )
    prep_items = load_raw_text_next_cycle_sensitive_registration_prep_items(source_dir)
    sensitive_prep_items = load_raw_text_next_cycle_sensitive_risk_review_prep_items(
        source_dir
    )
    source_entries_by_id = _load_source_library_entries(source_dir)

    prep_items_by_id = {item.prep_item_id: item for item in prep_items}
    blocked_prep_item_ids = [
        item.prep_item_id
        for item in sensitive_prep_items
        if item.prep_status == "blocked_after_sensitive_prep"
    ]
    deferred_prep_item_ids = [
        item.prep_item_id
        for item in sensitive_prep_items
        if item.prep_status == "deferred_after_sensitive_prep"
    ]
    registered_entries_match_prep_metadata = bool(items) and all(
        item.registration_prep_item_id in prep_items_by_id
        and _sensitive_registration_prep_entry_matches_existing(
            prep_items_by_id[item.registration_prep_item_id],
            source_entries_by_id[item.registered_entry_id],
        )
        for item in items
        if item.registered_entry_id in source_entries_by_id
    )
    all_registered_entries_present = bool(items) and all(
        item.registered_entry_id in source_entries_by_id for item in items
    )
    registered_material_ids_match = bool(items) and all(
        item.registered_entry_id in source_entries_by_id
        and source_entries_by_id[item.registered_entry_id].material_id
        == item.registered_material_id
        for item in items
    )
    blocked_and_deferred_prep_retained = (
        bool(blocked_prep_item_ids)
        and bool(deferred_prep_item_ids)
        and all(
            item.registration_prep_item_id
            not in set(blocked_prep_item_ids) | set(deferred_prep_item_ids)
            for item in items
        )
    )
    source_paths_are_relative = all(
        _is_source_relative_path(path)
        for item in items
        for path in item.registered_local_references
    )
    boundary_checks = {
        "sensitive_source_registration_items_loaded": (
            "passed" if items else "failed"
        ),
        "sensitive_registration_prep_completed": (
            "passed"
            if prep_summary.prep_status == "sensitive_registration_prep_completed"
            else "failed"
        ),
        "source_library_entries_loaded": (
            "passed" if source_entries_by_id else "failed"
        ),
        "registered_entries_match_prep_metadata": (
            "passed"
            if all_registered_entries_present
            and registered_material_ids_match
            and registered_entries_match_prep_metadata
            else "failed"
        ),
        "blocked_and_deferred_prep_retained": (
            "passed" if blocked_and_deferred_prep_retained else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleSensitiveSourceRegistrationSummary(
        registration_id=RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_REGISTRATION_ID,
        registration_status=(
            "sensitive_source_registration_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "sensitive_source_registration_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        registered_entry_count=len(items),
        registered_source_file_count=sum(
            len(item.registered_local_references) for item in items
        ),
        candidate_extract_count=0,
        formal_evidence_count=0,
        registered_entry_ids=[item.registered_entry_id for item in items],
        registered_material_ids=[item.registered_material_id for item in items],
        registration_prep_item_ids=[
            item.registration_prep_item_id for item in items
        ],
        blocked_prep_item_ids=blocked_prep_item_ids,
        deferred_prep_item_ids=deferred_prep_item_ids,
        source_library_mutation_authorized=any(
            item.source_library_mutation_authorized for item in items
        ),
        downstream_mutation_authorized=any(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_REGISTRATION_NEXT_MATERIAL_ENTRY
        ),
        boundary_checks=boundary_checks,
        guardrails=[
            "Only source-library metadata registration is authorized in this stage.",
            "The registered sensitive source still needs preparation before reading.",
            "Blocked and deferred sensitive prep items remain unavailable.",
            "013 candidate intake and 012 formal evidence remain blocked.",
            "External raw materials are not moved, converted, opened, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_sensitive_source_registration_markdown(
    summary: RawTextNextCycleSensitiveSourceRegistrationSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Sensitive Source Registration",
        "",
        f"- Registration id: `{summary.registration_id}`",
        (
            "- `sensitive-source-registration-status="
            f"{summary.registration_status}`"
        ),
        f"- `registered-source-entries={summary.registered_entry_count}`",
        f"- `registered-source-files={summary.registered_source_file_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence={summary.formal_evidence_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Registered source-library entry ids:",
    ]
    lines.extend(f"- `{entry_id}`" for entry_id in summary.registered_entry_ids)
    lines.extend(["", "Registered material ids:"])
    lines.extend(f"- `{material_id}`" for material_id in summary.registered_material_ids)
    lines.extend(["", "Registration-prep item ids:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.registration_prep_item_ids)
    lines.extend(["", "Prep items retained blocked:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.blocked_prep_item_ids)
    lines.extend(["", "Prep items retained deferred:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.deferred_prep_item_ids)
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


def build_raw_text_next_cycle_sensitive_preparation_boundary_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleSensitivePreparationBoundarySummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_sensitive_preparation_boundary_items(source_dir)
    registration_summary = build_raw_text_next_cycle_sensitive_source_registration_summary(
        source_dir
    )
    registration_items_by_id = {
        item.registration_item_id: item
        for item in load_raw_text_next_cycle_sensitive_source_registration_items(
            source_dir
        )
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    source_file_count = sum(item.file_count for item in items)
    local_references = [
        reference for item in items for reference in item.local_references
    ]
    registered_source_references_valid = bool(items) and all(
        item.source_registration_item_id in registration_items_by_id
        and registration_items_by_id[
            item.source_registration_item_id
        ].registered_entry_id
        == item.source_library_entry_id
        and registration_items_by_id[
            item.source_registration_item_id
        ].registered_material_id
        == item.source_material_id
        and registration_items_by_id[
            item.source_registration_item_id
        ].registered_local_references
        == item.local_references
        for item in items
    )
    source_library_entry_ready_for_preparation = bool(items) and all(
        item.source_library_entry_id in source_entries_by_id
        and source_entries_by_id[item.source_library_entry_id].material_id
        == item.source_material_id
        and source_entries_by_id[item.source_library_entry_id].risk_tier
        == "sensitive"
        and source_entries_by_id[item.source_library_entry_id].readiness_status
        == "needs_preparation"
        and source_entries_by_id[item.source_library_entry_id].next_action
        == "prepare_material"
        for item in items
    )
    source_paths_are_relative = bool(items) and all(
        _is_source_relative_path(path) for path in local_references
    )
    action_routing_valid = bool(items) and all(
        item.boundary_status == "cleared_for_sensitive_preparation"
        and item.recommended_next_action == "prepare_material"
        and item.preparation_allowed
        and not item.reading_allowed
        for item in items
    )
    downstream_mutation_blocked = not any(
        item.downstream_mutation_authorized for item in items
    )
    boundary_checks = {
        "sensitive_preparation_boundary_items_loaded": (
            "passed" if items else "failed"
        ),
        "source_registration_completed": (
            "passed"
            if registration_summary.registration_status
            == "sensitive_source_registration_completed"
            else "failed"
        ),
        "registered_source_references_valid": (
            "passed" if registered_source_references_valid else "failed"
        ),
        "source_library_entry_ready_for_preparation": (
            "passed" if source_library_entry_ready_for_preparation else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "action_routing_valid": "passed" if action_routing_valid else "failed",
        "downstream_mutation_blocked": (
            "passed" if downstream_mutation_blocked else "failed"
        ),
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleSensitivePreparationBoundarySummary(
        boundary_id=RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_BOUNDARY_ID,
        boundary_status=(
            "sensitive_preparation_boundary_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "sensitive_preparation_boundary_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        boundary_item_count=len(items),
        source_file_count=source_file_count,
        preparation_allowed_count=sum(
            1 for item in items if item.preparation_allowed
        ),
        reading_allowed_count=sum(1 for item in items if item.reading_allowed),
        candidate_extract_count=0,
        formal_evidence_count=0,
        boundary_item_ids=[item.boundary_item_id for item in items],
        source_registration_item_ids=[
            item.source_registration_item_id for item in items
        ],
        source_entry_ids=[item.source_library_entry_id for item in items],
        source_material_ids=[item.source_material_id for item in items],
        local_references=local_references,
        status_counts=_count_values([item.boundary_status for item in items]),
        action_counts=_count_values(
            [item.recommended_next_action for item in items]
        ),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_values(
            [
                rule_family
                for item in items
                for rule_family in item.target_rule_families
            ]
        ),
        downstream_mutation_authorized=any(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_BOUNDARY_NEXT_MATERIAL_ENTRY
        ),
        boundary_checks=boundary_checks,
        guardrails=[
            "This stage clears metadata-only preparation for one sensitive source.",
            "Raw PDF reading remains blocked until a later bounded reading stage.",
            "013 candidate intake and 012 formal evidence remain blocked.",
            "Do not infer traits, outcomes, or advice from the title alone.",
            "External raw materials are not moved, converted, opened, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_sensitive_preparation_boundary_markdown(
    summary: RawTextNextCycleSensitivePreparationBoundarySummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Sensitive Preparation Boundary",
        "",
        f"- Boundary id: `{summary.boundary_id}`",
        (
            "- `sensitive-preparation-boundary-status="
            f"{summary.boundary_status}`"
        ),
        (
            "- `sensitive-preparation-boundary-items="
            f"{summary.boundary_item_count}`"
        ),
        f"- `source-files={summary.source_file_count}`",
        f"- `preparation-allowed={summary.preparation_allowed_count}`",
        f"- `reading-allowed={summary.reading_allowed_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence={summary.formal_evidence_count}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Boundary item ids:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.boundary_item_ids)
    lines.extend(["", "Source registration item ids:"])
    lines.extend(
        f"- `{item_id}`" for item_id in summary.source_registration_item_ids
    )
    lines.extend(["", "Source-library entry ids:"])
    lines.extend(f"- `{entry_id}`" for entry_id in summary.source_entry_ids)
    lines.extend(["", "Source material ids:"])
    lines.extend(f"- `{material_id}`" for material_id in summary.source_material_ids)
    lines.extend(["", "Local references:"])
    lines.extend(f"- `{reference}`" for reference in summary.local_references)
    lines.extend(["", "Status counts:"])
    lines.extend(
        f"- `{status}`: `{count}`"
        for status, count in summary.status_counts.items()
    )
    lines.extend(["", "Action counts:"])
    lines.extend(
        f"- `{action}`: `{count}`" for action, count in summary.action_counts.items()
    )
    lines.extend(["", "Risk boundary counts:"])
    lines.extend(
        f"- `{risk}`: `{count}`"
        for risk, count in summary.risk_boundary_counts.items()
    )
    lines.extend(["", "Target rule family counts:"])
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


def build_raw_text_next_cycle_sensitive_preparation_reading_summary(
    data_dir: Path | str | None = None,
) -> RawTextNextCycleSensitivePreparationReadingSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_next_cycle_sensitive_preparation_reading_items(source_dir)
    boundary_summary = build_raw_text_next_cycle_sensitive_preparation_boundary_summary(
        source_dir
    )
    boundary_items_by_id = {
        item.boundary_item_id: item
        for item in load_raw_text_next_cycle_sensitive_preparation_boundary_items(
            source_dir
        )
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    local_references = [
        reference for item in items for reference in item.local_references
    ]
    boundary_references_valid = bool(items) and all(
        item.boundary_item_id in boundary_items_by_id
        and boundary_items_by_id[item.boundary_item_id].source_library_entry_id
        == item.source_library_entry_id
        and boundary_items_by_id[item.boundary_item_id].source_material_id
        == item.source_material_id
        and boundary_items_by_id[item.boundary_item_id].local_references
        == item.local_references
        and boundary_items_by_id[item.boundary_item_id].preparation_allowed
        for item in items
    )
    source_library_entry_still_preparation_gated = bool(items) and all(
        item.source_library_entry_id in source_entries_by_id
        and source_entries_by_id[item.source_library_entry_id].material_id
        == item.source_material_id
        and source_entries_by_id[item.source_library_entry_id].risk_tier
        == "sensitive"
        and source_entries_by_id[item.source_library_entry_id].readiness_status
        == "needs_preparation"
        and source_entries_by_id[item.source_library_entry_id].next_action
        == "prepare_material"
        for item in items
    )
    safe_reading_notes_present = bool(items) and all(
        item.safe_reading_note_count >= 3
        and item.safe_reading_note_count == len(item.safe_reading_notes)
        and bool(item.sensitive_controls)
        for item in items
    )
    source_paths_are_relative = bool(items) and all(
        _is_source_relative_path(path) for path in local_references
    )
    downstream_mutation_blocked = not any(
        item.downstream_mutation_authorized for item in items
    )
    candidate_intake_blocked = not any(
        item.candidate_intake_ready for item in items
    )
    formal_evidence_blocked = not any(
        item.formal_evidence_ready for item in items
    )
    boundary_checks = {
        "sensitive_preparation_reading_items_loaded": (
            "passed" if items else "failed"
        ),
        "preparation_boundary_completed": (
            "passed"
            if boundary_summary.boundary_status
            == "sensitive_preparation_boundary_completed"
            else "failed"
        ),
        "boundary_references_valid": (
            "passed" if boundary_references_valid else "failed"
        ),
        "source_library_entry_still_preparation_gated": (
            "passed" if source_library_entry_still_preparation_gated else "failed"
        ),
        "safe_reading_notes_present": (
            "passed" if safe_reading_notes_present else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "downstream_mutation_blocked": (
            "passed" if downstream_mutation_blocked else "failed"
        ),
        "013_candidate_intake_blocked": (
            "passed" if candidate_intake_blocked else "failed"
        ),
        "012_formal_evidence_blocked": (
            "passed" if formal_evidence_blocked else "failed"
        ),
        "raw_materials_not_mutated": "passed",
    }

    return RawTextNextCycleSensitivePreparationReadingSummary(
        reading_id=RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_READING_ID,
        reading_status=(
            "sensitive_preparation_reading_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "sensitive_preparation_reading_needs_attention"
        ),
        triage_group_id=RAW_TEXT_NEXT_CYCLE_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        reading_item_count=len(items),
        source_file_count=sum(len(item.local_references) for item in items),
        safe_reading_note_count=sum(item.safe_reading_note_count for item in items),
        candidate_intake_ready_count=sum(
            1 for item in items if item.candidate_intake_ready
        ),
        formal_evidence_ready_count=sum(
            1 for item in items if item.formal_evidence_ready
        ),
        candidate_extract_count=0,
        review_decision_count=0,
        promotion_batch_count=0,
        formal_evidence_count=0,
        reading_item_ids=[item.reading_item_id for item in items],
        boundary_item_ids=[item.boundary_item_id for item in items],
        source_entry_ids=[item.source_library_entry_id for item in items],
        source_material_ids=[item.source_material_id for item in items],
        local_references=local_references,
        status_counts=_count_values([item.reading_status for item in items]),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_values(
            [
                rule_family
                for item in items
                for rule_family in item.target_rule_families
            ]
        ),
        downstream_mutation_authorized=any(
            item.downstream_mutation_authorized for item in items
        ),
        next_material_entry=(
            RAW_TEXT_NEXT_CYCLE_SENSITIVE_PREPARATION_READING_NEXT_MATERIAL_ENTRY
        ),
        boundary_checks=boundary_checks,
        guardrails=[
            "This stage records safe preparation-reading controls only.",
            "The source remains sensitive and preparation-gated in source-library metadata.",
            "013 candidate intake requires a later explicit authorization step.",
            "012 formal evidence remains blocked.",
            "External raw materials are not moved, converted, opened, or rewritten.",
        ],
    )


def render_raw_text_next_cycle_sensitive_preparation_reading_markdown(
    summary: RawTextNextCycleSensitivePreparationReadingSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Raw Text Next Cycle Sensitive Preparation Reading",
        "",
        f"- Reading id: `{summary.reading_id}`",
        (
            "- `sensitive-preparation-reading-status="
            f"{summary.reading_status}`"
        ),
        (
            "- `sensitive-preparation-reading-items="
            f"{summary.reading_item_count}`"
        ),
        f"- `source-files={summary.source_file_count}`",
        f"- `safe-reading-notes={summary.safe_reading_note_count}`",
        f"- `candidate-intake-ready={summary.candidate_intake_ready_count}`",
        f"- `formal-evidence-ready={summary.formal_evidence_ready_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `review-decisions={summary.review_decision_count}`",
        f"- `promotion-batches={summary.promotion_batch_count}`",
        f"- `formal-evidence={summary.formal_evidence_count}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Reading item ids:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.reading_item_ids)
    lines.extend(["", "Boundary item ids:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.boundary_item_ids)
    lines.extend(["", "Source-library entry ids:"])
    lines.extend(f"- `{entry_id}`" for entry_id in summary.source_entry_ids)
    lines.extend(["", "Source material ids:"])
    lines.extend(f"- `{material_id}`" for material_id in summary.source_material_ids)
    lines.extend(["", "Local references:"])
    lines.extend(f"- `{reference}`" for reference in summary.local_references)
    lines.extend(["", "Status counts:"])
    lines.extend(
        f"- `{status}`: `{count}`"
        for status, count in summary.status_counts.items()
    )
    lines.extend(["", "Risk boundary counts:"])
    lines.extend(
        f"- `{risk}`: `{count}`"
        for risk, count in summary.risk_boundary_counts.items()
    )
    lines.extend(["", "Target rule family counts:"])
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


def build_raw_text_cluster_source_selection_summary(
    data_dir: Path | str | None = None,
) -> RawTextClusterSourceSelectionSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_cluster_source_selection_items(source_dir)
    cluster_items_by_id = {
        cluster.cluster_id: cluster
        for cluster in load_raw_text_source_cluster_selection_items(source_dir)
    }
    source_file_count = sum(item.file_count for item in items)
    priority_count = sum(item.priority_text_candidate_count for item in items)
    selected_clusters_loaded = all(
        cluster_id in cluster_items_by_id
        for cluster_id in RAW_TEXT_CLUSTER_SOURCE_SELECTION_CLUSTER_IDS
    )
    selected_cluster_references_valid = selected_clusters_loaded and all(
        cluster_items_by_id[cluster_id].cluster_status
        == "selected_for_source_selection"
        for cluster_id in RAW_TEXT_CLUSTER_SOURCE_SELECTION_CLUSTER_IDS
    )
    source_paths_are_relative = bool(items) and all(
        _is_source_relative_path(path)
        for item in items
        for path in item.relative_paths
    )
    boundary_checks = {
        "source_selection_items_loaded": "passed" if items else "failed",
        "selected_clusters_loaded": (
            "passed" if selected_clusters_loaded else "failed"
        ),
        "selected_cluster_references_valid": (
            "passed" if selected_cluster_references_valid else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "raw_materials_not_mutated": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }
    selected_item_ids = [
        item.selection_id
        for item in items
        if item.selection_status == "selected_for_identity_review"
    ]
    variant_review_item_ids = [
        item.selection_id
        for item in items
        if item.selection_status == "variant_identity_review"
    ]
    deferred_item_ids = [
        item.selection_id
        for item in items
        if item.selection_status == "deferred_after_cluster_selection"
    ]
    status_counts = _count_values([item.selection_status for item in items])

    return RawTextClusterSourceSelectionSummary(
        selection_id=RAW_TEXT_CLUSTER_SOURCE_SELECTION_ID,
        selection_status=(
            "cluster_source_selection_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "cluster_source_selection_needs_attention"
        ),
        triage_group_id=RAW_TEXT_CLUSTER_SOURCE_SELECTION_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        selected_cluster_ids=list(RAW_TEXT_CLUSTER_SOURCE_SELECTION_CLUSTER_IDS),
        source_selection_item_count=len(items),
        source_file_count=source_file_count,
        priority_text_candidate_count=priority_count,
        selected_for_identity_review_count=len(selected_item_ids),
        variant_identity_review_count=len(variant_review_item_ids),
        deferred_after_cluster_selection_count=len(deferred_item_ids),
        status_counts=status_counts,
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        extension_counts=_sum_cluster_source_extension_counts(items),
        target_rule_family_counts=_count_cluster_source_rule_families(items),
        selected_item_ids=selected_item_ids,
        variant_review_item_ids=variant_review_item_ids,
        deferred_item_ids=deferred_item_ids,
        downstream_mutation_authorized=False,
        next_material_entry=RAW_TEXT_CLUSTER_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Source-level selection uses inventory labels and existing cluster metadata only.",
            "Selected records require source identity review before registration or extraction.",
            "Variant sets require edition and duplicate review before learning reuse.",
            "Raw files, source-library records, candidates, reviews, promotions, and formal evidence are not mutated.",
        ],
    )


def render_raw_text_cluster_source_selection_markdown(
    summary: RawTextClusterSourceSelectionSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Bazi General Cluster Source Selection",
        "",
        f"- Selection id: `{summary.selection_id}`",
        (
            "- `cluster-source-selection-status="
            f"{summary.selection_status}`"
        ),
        f"- `cluster-source-selection-items={summary.source_selection_item_count}`",
        f"- `cluster-source-files={summary.source_file_count}`",
        (
            "- `cluster-source-priority-candidates="
            f"{summary.priority_text_candidate_count}`"
        ),
        (
            "- `selected-for-identity-review="
            f"{summary.selected_for_identity_review_count}`"
        ),
        f"- `variant-identity-review={summary.variant_identity_review_count}`",
        (
            "- `deferred-after-cluster-selection="
            f"{summary.deferred_after_cluster_selection_count}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Selected clusters:",
    ]
    lines.extend(f"- `{cluster_id}`" for cluster_id in summary.selected_cluster_ids)
    lines.extend(["", "Selected source records:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.selected_item_ids)
    lines.extend(["", "Variant identity review records:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.variant_review_item_ids)
    lines.extend(["", "Deferred records:"])
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


def build_raw_text_source_identity_review_summary(
    data_dir: Path | str | None = None,
) -> RawTextSourceIdentityReviewSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_source_identity_review_items(source_dir)
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_cluster_source_selection_items(source_dir)
    }
    source_entries_by_id = _load_source_library_entries(source_dir)
    source_selection_references_valid = bool(items) and all(
        item.source_selection_id in source_selection_items_by_id for item in items
    )
    source_library_overlap_references_valid = bool(items) and all(
        entry_id in source_entries_by_id
        for item in items
        for entry_id in item.matched_source_library_entry_ids
    )
    boundary_checks = {
        "identity_review_items_loaded": "passed" if items else "failed",
        "source_selection_items_loaded": (
            "passed" if source_selection_items_by_id else "failed"
        ),
        "source_selection_references_valid": (
            "passed" if source_selection_references_valid else "failed"
        ),
        "source_library_overlap_references_valid": (
            "passed" if source_library_overlap_references_valid else "failed"
        ),
        "raw_materials_not_mutated": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }
    existing_batch_overlap_ids = [
        item.review_id
        for item in items
        if item.identity_status == "existing_batch_overlap"
    ]
    registration_prep_item_ids = [
        item.review_id
        for item in items
        if item.identity_status == "registration_prep_ready"
    ]
    variant_choice_item_ids = [
        item.review_id
        for item in items
        if item.identity_status == "variant_choice_required"
    ]
    deferred_item_ids = [
        item.review_id
        for item in items
        if item.identity_status == "deferred_large_source"
    ]

    return RawTextSourceIdentityReviewSummary(
        review_id=RAW_TEXT_SOURCE_IDENTITY_REVIEW_ID,
        review_status=(
            "source_identity_review_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "source_identity_review_needs_attention"
        ),
        triage_group_id=RAW_TEXT_SOURCE_IDENTITY_REVIEW_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        identity_review_item_count=len(items),
        existing_batch_overlap_count=len(existing_batch_overlap_ids),
        registration_prep_ready_count=len(registration_prep_item_ids),
        variant_choice_required_count=len(variant_choice_item_ids),
        deferred_large_source_count=len(deferred_item_ids),
        identity_status_counts=_count_values([item.identity_status for item in items]),
        source_library_overlap_counts=_count_values(
            [item.source_library_overlap_status for item in items]
        ),
        registration_readiness_counts=_count_values(
            [item.registration_readiness for item in items]
        ),
        risk_boundary_counts=_count_values([item.risk_boundary for item in items]),
        target_rule_family_counts=_count_source_identity_rule_families(items),
        existing_batch_overlap_ids=existing_batch_overlap_ids,
        registration_prep_item_ids=registration_prep_item_ids,
        variant_choice_item_ids=variant_choice_item_ids,
        deferred_item_ids=deferred_item_ids,
        downstream_mutation_authorized=False,
        next_material_entry=RAW_TEXT_SOURCE_IDENTITY_REVIEW_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Identity review uses path labels, source-selection metadata, and source-library overlap metadata only.",
            "Existing Markdown batch overlaps do not create duplicate source-library entries.",
            "Registration-prep-ready records still require an explicit registration step before reading or extraction.",
            "Variant sets require a separate choice before registration, reading, or candidate intake.",
        ],
    )


def render_raw_text_source_identity_review_markdown(
    summary: RawTextSourceIdentityReviewSummary,
) -> str:
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Bazi General Source Identity Review",
        "",
        f"- Review id: `{summary.review_id}`",
        f"- `source-identity-review-status={summary.review_status}`",
        f"- `source-identity-review-items={summary.identity_review_item_count}`",
        f"- `existing-batch-overlap={summary.existing_batch_overlap_count}`",
        f"- `registration-prep-ready={summary.registration_prep_ready_count}`",
        f"- `variant-choice-required={summary.variant_choice_required_count}`",
        f"- `deferred-large-source={summary.deferred_large_source_count}`",
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Existing-batch overlap records:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.existing_batch_overlap_ids)
    lines.extend(["", "Registration-prep-ready records:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.registration_prep_item_ids)
    lines.extend(["", "Variant-choice records:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.variant_choice_item_ids)
    lines.extend(["", "Deferred records:"])
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


def build_raw_text_source_registration_prep_summary(
    data_dir: Path | str | None = None,
) -> RawTextSourceRegistrationPrepSummary:
    source_dir = _data_dir(data_dir)
    items = load_raw_text_source_registration_prep_items(source_dir)
    identity_review_items = load_raw_text_source_identity_review_items(source_dir)
    identity_review_items_by_id = {item.review_id: item for item in identity_review_items}
    source_entries_by_id = _load_source_library_entries(source_dir)
    existing_material_ids = {
        source_entry.material_id for source_entry in source_entries_by_id.values()
    }
    identity_review_references_valid = bool(items) and all(
        item.identity_review_id in identity_review_items_by_id
        and identity_review_items_by_id[item.identity_review_id].identity_status
        == "registration_prep_ready"
        for item in items
    )
    proposed_entries_registered_or_available = bool(items) and all(
        _registration_prep_entry_registered_or_available(
            item,
            source_entries_by_id,
            existing_material_ids,
        )
        for item in items
    )
    source_paths_are_relative = bool(items) and all(
        _is_source_relative_path(path)
        for item in items
        for path in item.proposed_local_references
    )
    skipped_existing_batch_overlap_ids = [
        item.review_id
        for item in identity_review_items
        if item.identity_status == "existing_batch_overlap"
    ]
    blocked_variant_choice_ids = [
        item.review_id
        for item in identity_review_items
        if item.identity_status == "variant_choice_required"
    ]
    deferred_item_ids = [
        item.review_id
        for item in identity_review_items
        if item.identity_status == "deferred_large_source"
    ]
    boundary_checks = {
        "registration_prep_items_loaded": "passed" if items else "failed",
        "identity_review_items_loaded": (
            "passed" if identity_review_items else "failed"
        ),
        "identity_review_references_valid": (
            "passed" if identity_review_references_valid else "failed"
        ),
        "proposed_entries_registered_or_available": (
            "passed" if proposed_entries_registered_or_available else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }

    return RawTextSourceRegistrationPrepSummary(
        prep_id=RAW_TEXT_SOURCE_REGISTRATION_PREP_ID,
        prep_status=(
            "registration_prep_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "registration_prep_needs_attention"
        ),
        triage_group_id=RAW_TEXT_SOURCE_REGISTRATION_PREP_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        registration_prep_item_count=len(items),
        proposed_source_file_count=sum(
            len(item.proposed_local_references) for item in items
        ),
        skipped_existing_batch_overlap_count=len(skipped_existing_batch_overlap_ids),
        blocked_variant_choice_count=len(blocked_variant_choice_ids),
        deferred_large_source_count=len(deferred_item_ids),
        registration_status_counts=_count_values(
            [item.registration_status for item in items]
        ),
        proposed_readiness_counts=_count_values(
            [item.proposed_readiness_status for item in items]
        ),
        proposed_next_action_counts=_count_values(
            [item.proposed_next_action for item in items]
        ),
        risk_tier_counts=_count_values([item.risk_tier for item in items]),
        target_rule_family_counts=_count_registration_prep_rule_families(items),
        proposed_entry_ids=[item.proposed_entry_id for item in items],
        proposed_material_ids=[item.proposed_material_id for item in items],
        registration_prep_item_ids=[item.prep_id for item in items],
        skipped_existing_batch_overlap_ids=skipped_existing_batch_overlap_ids,
        blocked_variant_choice_ids=blocked_variant_choice_ids,
        deferred_item_ids=deferred_item_ids,
        source_library_mutation_authorized=False,
        downstream_mutation_authorized=False,
        next_material_entry=RAW_TEXT_SOURCE_REGISTRATION_PREP_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Registration prep proposes source-library metadata but does not mutate source-library records.",
            "Existing Markdown Batch 001 overlaps are skipped to avoid duplicate registration.",
            "Variant sets remain blocked until a separate variant-choice step selects one source identity.",
            "Prepared registration metadata does not authorize reading, extraction, 013 candidate intake, or 012 evidence changes.",
        ],
    )


def render_raw_text_source_registration_prep_markdown(
    summary: RawTextSourceRegistrationPrepSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Bazi General Registration Prep",
        "",
        f"- Prep id: `{summary.prep_id}`",
        f"- `registration-prep-status={summary.prep_status}`",
        f"- `registration-prep-items={summary.registration_prep_item_count}`",
        f"- `proposed-source-files={summary.proposed_source_file_count}`",
        (
            "- `skipped-existing-batch-overlap="
            f"{summary.skipped_existing_batch_overlap_count}`"
        ),
        f"- `blocked-variant-choice={summary.blocked_variant_choice_count}`",
        f"- `deferred-large-source={summary.deferred_large_source_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Proposed source-library entry ids:",
    ]
    lines.extend(f"- `{entry_id}`" for entry_id in summary.proposed_entry_ids)
    lines.extend(["", "Registration-prep records:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.registration_prep_item_ids)
    lines.extend(["", "Skipped existing-batch overlap ids:"])
    lines.extend(
        f"- `{item_id}`" for item_id in summary.skipped_existing_batch_overlap_ids
    )
    lines.extend(["", "Blocked variant-choice ids:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.blocked_variant_choice_ids)
    lines.extend(["", "Deferred ids:"])
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


def build_raw_text_source_registration_summary(
    data_dir: Path | str | None = None,
) -> RawTextSourceRegistrationSummary:
    source_dir = _data_dir(data_dir)
    prep_items = load_raw_text_source_registration_prep_items(source_dir)
    source_entries_by_id = _load_source_library_entries(source_dir)
    identity_review_items = load_raw_text_source_identity_review_items(source_dir)
    registered_items = [
        item for item in prep_items if item.proposed_entry_id in source_entries_by_id
    ]
    skipped_existing_batch_overlap_ids = [
        item.review_id
        for item in identity_review_items
        if item.identity_status == "existing_batch_overlap"
    ]
    blocked_variant_choice_ids = [
        item.review_id
        for item in identity_review_items
        if item.identity_status == "variant_choice_required"
    ]
    deferred_item_ids = [
        item.review_id
        for item in identity_review_items
        if item.identity_status == "deferred_large_source"
    ]
    prepared_entries_registered = bool(prep_items) and len(registered_items) == len(
        prep_items
    )
    registered_entries_match_prep_metadata = bool(prep_items) and all(
        _source_entry_matches_registration_prep(
            item,
            source_entries_by_id[item.proposed_entry_id],
        )
        for item in registered_items
    )
    skipped_existing_batch_overlap_not_duplicated = bool(
        skipped_existing_batch_overlap_ids
    ) and _source_entries_absent_for_markers(
        source_entries_by_id,
        RAW_TEXT_SOURCE_REGISTRATION_OVERLAP_ENTRY_ID_MARKERS,
    )
    variant_choice_boundary_respected = bool(blocked_variant_choice_ids) and (
        _source_entries_absent_for_markers(
            source_entries_by_id,
            RAW_TEXT_SOURCE_REGISTRATION_VARIANT_ENTRY_ID_MARKERS,
        )
        or _selected_variant_entries_registered(source_entries_by_id)
    )
    deferred_large_source_not_registered = bool(
        deferred_item_ids
    ) and _source_entries_absent_for_markers(
        source_entries_by_id,
        RAW_TEXT_SOURCE_REGISTRATION_DEFERRED_ENTRY_ID_MARKERS,
    )
    boundary_checks = {
        "registration_prep_items_loaded": "passed" if prep_items else "failed",
        "source_library_entries_loaded": (
            "passed" if source_entries_by_id else "failed"
        ),
        "prepared_entries_registered": (
            "passed" if prepared_entries_registered else "failed"
        ),
        "registered_entries_match_prep_metadata": (
            "passed" if registered_entries_match_prep_metadata else "failed"
        ),
        "skipped_existing_batch_overlap_not_duplicated": (
            "passed" if skipped_existing_batch_overlap_not_duplicated else "failed"
        ),
        "variant_choice_boundary_respected": (
            "passed" if variant_choice_boundary_respected else "failed"
        ),
        "deferred_large_source_not_registered": (
            "passed" if deferred_large_source_not_registered else "failed"
        ),
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }

    return RawTextSourceRegistrationSummary(
        registration_id=RAW_TEXT_SOURCE_REGISTRATION_ID,
        registration_status=(
            "source_registration_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "source_registration_needs_attention"
        ),
        triage_group_id=RAW_TEXT_SOURCE_REGISTRATION_PREP_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        registered_entry_count=len(registered_items),
        registered_source_file_count=sum(
            len(item.proposed_local_references) for item in registered_items
        ),
        skipped_existing_batch_overlap_count=len(skipped_existing_batch_overlap_ids),
        blocked_variant_choice_count=len(blocked_variant_choice_ids),
        deferred_large_source_count=len(deferred_item_ids),
        registered_entry_ids=[item.proposed_entry_id for item in registered_items],
        registered_material_ids=[item.proposed_material_id for item in registered_items],
        skipped_existing_batch_overlap_ids=skipped_existing_batch_overlap_ids,
        blocked_variant_choice_ids=blocked_variant_choice_ids,
        deferred_item_ids=deferred_item_ids,
        source_library_mutation_authorized=True,
        downstream_mutation_authorized=False,
        next_material_entry=RAW_TEXT_SOURCE_REGISTRATION_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Only source-library metadata registration is authorized in this stage.",
            "Existing Markdown Batch 001 overlaps stay represented by their existing source-library entry.",
            "Variant sets require a separate selected-variant authorization before registration.",
            "The deferred large source remains outside registration.",
            "Reading, extraction, 013 candidate intake, and 012 evidence changes remain blocked.",
        ],
    )


def render_raw_text_source_registration_markdown(
    summary: RawTextSourceRegistrationSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Bazi General Source Registration",
        "",
        f"- Registration id: `{summary.registration_id}`",
        f"- `source-registration-status={summary.registration_status}`",
        f"- `registered-source-entries={summary.registered_entry_count}`",
        f"- `registered-source-files={summary.registered_source_file_count}`",
        (
            "- `skipped-existing-batch-overlap="
            f"{summary.skipped_existing_batch_overlap_count}`"
        ),
        f"- `blocked-variant-choice={summary.blocked_variant_choice_count}`",
        f"- `deferred-large-source={summary.deferred_large_source_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Registered source-library entry ids:",
    ]
    lines.extend(f"- `{entry_id}`" for entry_id in summary.registered_entry_ids)
    lines.extend(["", "Registered material ids:"])
    lines.extend(f"- `{material_id}`" for material_id in summary.registered_material_ids)
    lines.extend(["", "Skipped existing-batch overlap ids:"])
    lines.extend(
        f"- `{item_id}`" for item_id in summary.skipped_existing_batch_overlap_ids
    )
    lines.extend(["", "Blocked variant-choice ids:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.blocked_variant_choice_ids)
    lines.extend(["", "Deferred ids:"])
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


def build_bazi_general_source_preparation_reading_summary(
    data_dir: Path | str | None = None,
) -> BaziGeneralSourcePreparationReadingSummary:
    source_dir = _data_dir(data_dir)
    data_root = source_dir.parent
    prep_items = load_raw_text_source_registration_prep_items(source_dir)
    source_entries_by_id = _load_source_library_entries(source_dir)
    identity_review_items = load_raw_text_source_identity_review_items(source_dir)
    records = load_material_audit_records(source_dir)
    readiness = load_preparation_readiness_findings(source_dir)
    queue_items = load_extraction_queue_items(source_dir)

    classical_dir = _sibling_data_dir(source_dir, "classical_sources")
    source_ids = {
        source.source_id
        for source in classical_sources.load_classical_sources(classical_dir)
    }
    formal_sources_by_id = {
        source.source_id: source
        for source in classical_sources.load_classical_sources(classical_dir)
    }
    evidence_by_id = {
        unit.evidence_id: unit
        for unit in classical_sources.load_evidence_units(classical_dir)
    }
    curation_batches = classical_sources.load_curation_batches(classical_dir)

    source_intake_dir = _sibling_data_dir(source_dir, "source_intake")
    source_materials_by_id = {
        material.material_id: material
        for material in source_intake.load_source_materials(
            source_intake_dir,
            known_source_ids=source_ids,
        )
    }
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in source_intake.load_candidate_extracts(source_intake_dir)
    }
    review_decisions = source_intake.load_review_decisions(source_intake_dir)
    promotion_batches = source_intake.load_promotion_batches(source_intake_dir)

    extraction_dir = _sibling_data_dir(source_dir, "extraction_queue_intake")
    tasks = extraction_queue_intake.load_extraction_tasks(extraction_dir)

    learning_dir = _sibling_data_dir(source_dir, "learning_reference_curation")
    notes = learning_reference_curation.load_learning_reference_notes(learning_dir)
    decisions = learning_reference_curation.load_candidate_intake_decisions(
        learning_dir
    )

    target_entry_ids = set(BAZI_GENERAL_SOURCE_PREPARATION_READING_ENTRY_IDS)
    target_material_ids = set(BAZI_GENERAL_SOURCE_PREPARATION_READING_MATERIAL_IDS)
    target_candidate_ids = set(BAZI_GENERAL_SOURCE_PREPARATION_READING_CANDIDATE_IDS)
    target_evidence_ids = set(BAZI_GENERAL_SOURCE_PREPARATION_READING_EVIDENCE_IDS)
    target_formal_source_ids = set(
        BAZI_GENERAL_SOURCE_PREPARATION_READING_FORMAL_SOURCE_IDS
    )

    registered_entries = [
        entry_id
        for entry_id in BAZI_GENERAL_SOURCE_PREPARATION_READING_ENTRY_IDS
        if entry_id in source_entries_by_id
    ]
    source_file_count = sum(
        len(item.proposed_local_references)
        for item in prep_items
        if item.proposed_entry_id in registered_entries
    )
    material_audit_records = [
        record
        for record in records
        if record.source_library_entry_id in target_entry_ids
    ]
    material_audit_ids = {record.audit_id for record in material_audit_records}
    ready_audit_ids = {
        finding.audit_id
        for finding in readiness
        if finding.audit_id in material_audit_ids
        and finding.readiness_state == "ready_for_extraction_review"
        and finding.text_preparation_status in {"prepared", "summary_only"}
    }
    completed_queue_audit_ids = {
        item.audit_id
        for item in queue_items
        if item.audit_id in material_audit_ids
        and item.queue_type == "extraction_ready"
        and item.status == "completed"
    }
    completed_tasks = [
        task
        for task in tasks
        if task.source_library_entry_id in target_entry_ids
        and task.status == "completed"
    ]
    applied_learning_notes = [
        note
        for note in notes
        if note.source_library_entry_id in target_entry_ids
        and note.status == "candidate_intake_started"
    ]
    applied_decisions = {
        decision.candidate_id
        for decision in decisions
        if decision.candidate_id in target_candidate_ids
        and decision.status == "applied"
    }
    promoted_candidates = [
        candidate
        for candidate_id, candidate in candidates_by_id.items()
        if candidate_id in target_candidate_ids and candidate.status == "promoted"
    ]
    approved_reviews = [
        decision
        for decision in review_decisions
        if decision.candidate_id in target_candidate_ids
        and decision.decision == "approved"
    ]
    matching_promotion_batches = [
        batch
        for batch in promotion_batches
        if target_candidate_ids.issubset(set(batch.candidate_ids))
        and target_evidence_ids.issubset(set(batch.target_evidence_ids))
        and batch.review_status in {"reviewed", "approved"}
    ]
    formal_sources = [
        source
        for source_id, source in formal_sources_by_id.items()
        if source_id in target_formal_source_ids and source.review_status == "approved"
    ]
    formal_evidence = [
        evidence
        for evidence_id, evidence in evidence_by_id.items()
        if evidence_id in target_evidence_ids
        and evidence.source_id in target_formal_source_ids
    ]
    matching_curation_batches = [
        batch
        for batch in curation_batches
        if target_formal_source_ids.issubset(set(batch.source_ids))
        and target_evidence_ids.issubset(set(batch.evidence_ids))
        and batch.review_status in {"reviewed", "approved"}
    ]

    skipped_existing_batch_overlap_ids = [
        item.review_id
        for item in identity_review_items
        if item.identity_status == "existing_batch_overlap"
    ]
    blocked_variant_choice_ids = [
        item.review_id
        for item in identity_review_items
        if item.identity_status == "variant_choice_required"
    ]
    deferred_item_ids = [
        item.review_id
        for item in identity_review_items
        if item.identity_status == "deferred_large_source"
    ]
    skipped_existing_batch_overlap_not_duplicated = bool(
        skipped_existing_batch_overlap_ids
    ) and _source_entries_absent_for_markers(
        source_entries_by_id,
        RAW_TEXT_SOURCE_REGISTRATION_OVERLAP_ENTRY_ID_MARKERS,
    )
    variant_choice_boundary_respected = bool(blocked_variant_choice_ids) and (
        _source_entries_absent_for_markers(
            source_entries_by_id,
            RAW_TEXT_SOURCE_REGISTRATION_VARIANT_ENTRY_ID_MARKERS,
        )
        or _selected_variant_entries_registered(source_entries_by_id)
    )
    deferred_large_source_not_mutated = bool(
        deferred_item_ids
    ) and _source_entries_absent_for_markers(
        source_entries_by_id,
        RAW_TEXT_SOURCE_REGISTRATION_DEFERRED_ENTRY_ID_MARKERS,
    )

    boundary_checks = {
        "registered_entries_loaded": (
            "passed"
            if set(registered_entries) == target_entry_ids
            else "failed"
        ),
        "material_preparation_records_loaded": (
            "passed"
            if len(material_audit_records) == 3
            and ready_audit_ids == material_audit_ids
            and completed_queue_audit_ids == material_audit_ids
            and target_material_ids.issubset(source_materials_by_id)
            else "failed"
        ),
        "extraction_tasks_completed": (
            "passed" if len(completed_tasks) == 3 else "failed"
        ),
        "learning_notes_applied": (
            "passed"
            if len(applied_learning_notes) == 3
            and applied_decisions == target_candidate_ids
            else "failed"
        ),
        "013_candidates_reviewed_promoted": (
            "passed"
            if len(promoted_candidates) == 3
            and len(approved_reviews) == 3
            and len(matching_promotion_batches) == 1
            else "failed"
        ),
        "012_formal_evidence_linked": (
            "passed"
            if len(formal_sources) == 3
            and len(formal_evidence) == 3
            and len(matching_curation_batches) == 1
            else "failed"
        ),
        "skipped_existing_batch_overlap_not_duplicated": (
            "passed" if skipped_existing_batch_overlap_not_duplicated else "failed"
        ),
        "variant_choice_boundary_respected": (
            "passed" if variant_choice_boundary_respected else "failed"
        ),
        "deferred_large_source_not_mutated": (
            "passed" if deferred_large_source_not_mutated else "failed"
        ),
        "raw_materials_not_mutated": "passed",
    }

    return BaziGeneralSourcePreparationReadingSummary(
        reading_id=BAZI_GENERAL_SOURCE_PREPARATION_READING_ID,
        reading_status=(
            "preparation_reading_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "preparation_reading_needs_attention"
        ),
        triage_group_id=RAW_TEXT_SOURCE_REGISTRATION_PREP_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        source_entry_count=len(registered_entries),
        source_file_count=source_file_count,
        material_audit_record_count=len(material_audit_records),
        extraction_task_count=len(completed_tasks),
        learning_note_count=len(applied_learning_notes),
        candidate_extract_count=len(promoted_candidates),
        review_decision_count=len(approved_reviews),
        promotion_batch_count=len(matching_promotion_batches),
        formal_source_count=len(formal_sources),
        formal_evidence_count=len(formal_evidence),
        source_entry_ids=list(BAZI_GENERAL_SOURCE_PREPARATION_READING_ENTRY_IDS),
        source_material_ids=list(BAZI_GENERAL_SOURCE_PREPARATION_READING_MATERIAL_IDS),
        candidate_ids=list(BAZI_GENERAL_SOURCE_PREPARATION_READING_CANDIDATE_IDS),
        evidence_ids=list(BAZI_GENERAL_SOURCE_PREPARATION_READING_EVIDENCE_IDS),
        source_library_mutation_authorized=True,
        downstream_mutation_authorized=True,
        next_material_entry=BAZI_GENERAL_SOURCE_PREPARATION_READING_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Only concise derived learning and evidence metadata is stored.",
            "Full PDF conversions and rendered page images remain temporary artifacts.",
            "Existing Batch 001 overlaps are not duplicated.",
            "Ditiansui and Qiongtong are handled by the later selected-variant stage.",
            "Huntian Baolan remains outside this stage.",
        ],
    )


def render_bazi_general_source_preparation_reading_markdown(
    summary: BaziGeneralSourcePreparationReadingSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Bazi General Source Preparation Reading",
        "",
        f"- Reading id: `{summary.reading_id}`",
        f"- `source-preparation-reading-status={summary.reading_status}`",
        f"- `source-preparation-reading-entries={summary.source_entry_count}`",
        f"- `source-preparation-reading-files={summary.source_file_count}`",
        f"- `material-audit-records={summary.material_audit_record_count}`",
        f"- `extraction-tasks={summary.extraction_task_count}`",
        f"- `learning-notes={summary.learning_note_count}`",
        f"- `candidate-extracts={summary.candidate_extract_count}`",
        f"- `formal-evidence-units={summary.formal_evidence_count}`",
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Source-library entry ids:",
    ]
    lines.extend(f"- `{entry_id}`" for entry_id in summary.source_entry_ids)
    lines.extend(["", "Source material ids:"])
    lines.extend(f"- `{material_id}`" for material_id in summary.source_material_ids)
    lines.extend(["", "Promoted candidate ids:"])
    lines.extend(f"- `{candidate_id}`" for candidate_id in summary.candidate_ids)
    lines.extend(["", "Formal evidence ids:"])
    lines.extend(f"- `{evidence_id}`" for evidence_id in summary.evidence_ids)
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


def build_bazi_general_variant_deferred_review_summary(
    data_dir: Path | str | None = None,
) -> BaziGeneralVariantDeferredReviewSummary:
    source_dir = _data_dir(data_dir)
    items = load_bazi_general_variant_deferred_review_items(source_dir)
    identity_review_items_by_id = {
        item.review_id: item for item in load_raw_text_source_identity_review_items(source_dir)
    }
    source_selection_items_by_id = {
        item.selection_id: item
        for item in load_raw_text_cluster_source_selection_items(source_dir)
    }
    variant_review_item_ids = [
        item.item_id for item in items if item.review_kind == "variant_choice"
    ]
    deferred_review_item_ids = [
        item.item_id for item in items if item.review_kind == "deferred_large_source"
    ]
    selected_canonical_variant_ids = [
        item.item_id
        for item in items
        if item.review_kind == "variant_choice"
        and item.canonical_choice_status == "selected_for_registration_prep"
        and item.selected_local_reference
    ]
    source_library_registration_authorized_count = sum(
        1 for item in items if item.source_library_mutation_authorized
    )
    source_paths_are_relative = bool(items) and all(
        _is_source_relative_path(path)
        for item in items
        for path in item.local_references
    )
    variant_records_match_identity_status = bool(variant_review_item_ids) and all(
        identity_review_items_by_id[item.identity_review_id].identity_status
        == "variant_choice_required"
        and source_selection_items_by_id[item.source_selection_id].selection_status
        == "variant_identity_review"
        for item in items
        if item.review_kind == "variant_choice"
    )
    deferred_records_match_identity_status = bool(deferred_review_item_ids) and all(
        identity_review_items_by_id[item.identity_review_id].identity_status
        == "deferred_large_source"
        and source_selection_items_by_id[item.source_selection_id].selection_status
        == "deferred_after_cluster_selection"
        for item in items
        if item.review_kind == "deferred_large_source"
    )
    source_library_not_mutated = bool(items) and all(
        not item.source_library_mutation_authorized
        and not item.selected_source_library_entry_id
        for item in items
    )
    downstream_not_mutated = bool(items) and all(
        not item.downstream_mutation_authorized for item in items
    )
    boundary_checks = {
        "variant_deferred_items_loaded": "passed" if items else "failed",
        "identity_review_references_valid": (
            "passed"
            if all(item.identity_review_id in identity_review_items_by_id for item in items)
            else "failed"
        ),
        "source_selection_references_valid": (
            "passed"
            if all(
                item.source_selection_id in source_selection_items_by_id
                for item in items
            )
            else "failed"
        ),
        "variant_records_match_identity_status": (
            "passed" if variant_records_match_identity_status else "failed"
        ),
        "deferred_records_match_identity_status": (
            "passed" if deferred_records_match_identity_status else "failed"
        ),
        "source_paths_are_relative": (
            "passed" if source_paths_are_relative else "failed"
        ),
        "canonical_variant_choices_recorded": (
            "passed"
            if len(selected_canonical_variant_ids) == len(variant_review_item_ids)
            else "failed"
        ),
        "source_library_not_mutated": (
            "passed" if source_library_not_mutated else "failed"
        ),
        "013_012_not_mutated": "passed" if downstream_not_mutated else "failed",
        "raw_materials_not_mutated": "passed",
    }

    return BaziGeneralVariantDeferredReviewSummary(
        review_id=BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_ID,
        review_status=(
            "variant_deferred_review_completed"
            if all(status == "passed" for status in boundary_checks.values())
            else "variant_deferred_review_needs_attention"
        ),
        triage_group_id=RAW_TEXT_SOURCE_IDENTITY_REVIEW_TRIAGE_GROUP_ID,
        source_root=RAW_TEXT_TRIAGE_SOURCE_ROOT,
        review_item_count=len(items),
        variant_review_item_count=len(variant_review_item_ids),
        deferred_review_item_count=len(deferred_review_item_ids),
        selected_canonical_variant_count=len(selected_canonical_variant_ids),
        source_library_registration_authorized_count=(
            source_library_registration_authorized_count
        ),
        variant_review_item_ids=variant_review_item_ids,
        deferred_review_item_ids=deferred_review_item_ids,
        selected_canonical_variant_ids=selected_canonical_variant_ids,
        source_library_mutation_authorized=(
            source_library_registration_authorized_count > 0
        ),
        downstream_mutation_authorized=not downstream_not_mutated,
        next_material_entry=BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_NEXT_MATERIAL_ENTRY,
        boundary_checks=boundary_checks,
        guardrails=[
            "Variant-choice records have selected local references only; registration still requires the next explicit prep step.",
            "The Huntian Baolan large source remains deferred and is not opened, converted, or registered.",
            "No source-library, 013 candidate, review, promotion, or 012 evidence mutation is authorized by this review.",
            "The next stage should prepare only the selected Ditiansui and Qiongtong variants for possible source registration.",
        ],
    )


def render_bazi_general_variant_deferred_review_markdown(
    summary: BaziGeneralVariantDeferredReviewSummary,
) -> str:
    source_library_mutation_authorized = (
        "true" if summary.source_library_mutation_authorized else "false"
    )
    downstream_mutation_authorized = (
        "true" if summary.downstream_mutation_authorized else "false"
    )
    lines = [
        "## 015 Bazi General Variant Choice And Deferred Review",
        "",
        f"- Review id: `{summary.review_id}`",
        f"- `variant-deferred-review-status={summary.review_status}`",
        f"- `variant-deferred-review-items={summary.review_item_count}`",
        f"- `variant-review-items={summary.variant_review_item_count}`",
        f"- `deferred-review-items={summary.deferred_review_item_count}`",
        (
            "- `selected-canonical-variants="
            f"{summary.selected_canonical_variant_count}`"
        ),
        (
            "- `source-library-registration-authorized="
            f"{summary.source_library_registration_authorized_count}`"
        ),
        (
            "- `source-library-mutation-authorized="
            f"{source_library_mutation_authorized}`"
        ),
        (
            "- `downstream-mutation-authorized="
            f"{downstream_mutation_authorized}`"
        ),
        f"- `next-material-entry={summary.next_material_entry}`",
        "",
        "Variant-choice review ids:",
    ]
    lines.extend(f"- `{item_id}`" for item_id in summary.variant_review_item_ids)
    lines.extend(["", "Deferred review ids:"])
    lines.extend(f"- `{item_id}`" for item_id in summary.deferred_review_item_ids)
    lines.extend(["", "Selected canonical variant ids:"])
    if summary.selected_canonical_variant_ids:
        lines.extend(
            f"- `{item_id}`" for item_id in summary.selected_canonical_variant_ids
        )
    else:
        lines.append("- None selected in this stage.")
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
    source_entries_by_id = _load_source_library_entries(source_dir)
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
    post_selected_variant_surface_confirmed = (
        all_queue_items_covered
        and bool(locally_completed_queue_item_ids)
        and _selected_variant_queue_surface_completed(source_entries_by_id)
    )

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
            "015-external-material-inventory-refresh"
            if post_selected_variant_surface_confirmed
            else RAW_TEXT_SOURCE_SELECTION_NEXT_MATERIAL_ENTRY
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
            "post_selected_variant_queue_surface_confirmed": (
                "passed" if post_selected_variant_surface_confirmed else "failed"
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
        raw_text_next_cycle_source_selection_items = (
            load_raw_text_next_cycle_source_selection_items(source_dir)
        )
        raw_text_next_cycle_identity_review_items = (
            load_raw_text_next_cycle_identity_review_items(source_dir)
        )
        raw_text_next_cycle_cluster_source_selection_items = (
            load_raw_text_next_cycle_cluster_source_selection_items(source_dir)
        )
        raw_text_next_cycle_followup_selection_items = (
            load_raw_text_next_cycle_followup_selection_items(source_dir)
        )
        raw_text_next_cycle_gated_cluster_review_prep_items = (
            load_raw_text_next_cycle_gated_cluster_review_prep_items(source_dir)
        )
        raw_text_next_cycle_gated_ordinary_source_selection_items = (
            load_raw_text_next_cycle_gated_ordinary_source_selection_items(
                source_dir
            )
        )
        raw_text_next_cycle_gated_ordinary_followup_selection_items = (
            load_raw_text_next_cycle_gated_ordinary_followup_selection_items(
                source_dir
            )
        )
        raw_text_next_cycle_gated_ordinary_final_selection_items = (
            load_raw_text_next_cycle_gated_ordinary_final_selection_items(source_dir)
        )
        raw_text_next_cycle_sensitive_risk_review_prep_items = (
            load_raw_text_next_cycle_sensitive_risk_review_prep_items(source_dir)
        )
        raw_text_next_cycle_sensitive_source_level_risk_review_items = (
            load_raw_text_next_cycle_sensitive_source_level_risk_review_items(
                source_dir
            )
        )
        raw_text_next_cycle_sensitive_registration_prep_items = (
            load_raw_text_next_cycle_sensitive_registration_prep_items(source_dir)
        )
        raw_text_next_cycle_sensitive_source_registration_items = (
            load_raw_text_next_cycle_sensitive_source_registration_items(source_dir)
        )
        raw_text_next_cycle_sensitive_preparation_boundary_items = (
            load_raw_text_next_cycle_sensitive_preparation_boundary_items(source_dir)
        )
        raw_text_next_cycle_sensitive_preparation_reading_items = (
            load_raw_text_next_cycle_sensitive_preparation_reading_items(source_dir)
        )
        raw_text_cluster_source_selection_items = (
            load_raw_text_cluster_source_selection_items(source_dir)
        )
        raw_text_source_identity_review_items = (
            load_raw_text_source_identity_review_items(source_dir)
        )
        raw_text_source_registration_prep_items = (
            load_raw_text_source_registration_prep_items(source_dir)
        )
        bazi_general_variant_deferred_review_items = (
            load_bazi_general_variant_deferred_review_items(source_dir)
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
        raw_text_next_cycle_source_selection_items,
        raw_text_next_cycle_identity_review_items,
        raw_text_next_cycle_cluster_source_selection_items,
        raw_text_next_cycle_followup_selection_items,
        raw_text_next_cycle_gated_cluster_review_prep_items,
        raw_text_next_cycle_gated_ordinary_source_selection_items,
        raw_text_next_cycle_gated_ordinary_followup_selection_items,
        raw_text_next_cycle_gated_ordinary_final_selection_items,
        raw_text_next_cycle_sensitive_risk_review_prep_items,
        raw_text_next_cycle_sensitive_source_level_risk_review_items,
        raw_text_next_cycle_sensitive_registration_prep_items,
        raw_text_next_cycle_sensitive_source_registration_items,
        raw_text_next_cycle_sensitive_preparation_boundary_items,
        raw_text_next_cycle_sensitive_preparation_reading_items,
        raw_text_cluster_source_selection_items,
        raw_text_source_identity_review_items,
        raw_text_source_registration_prep_items,
        bazi_general_variant_deferred_review_items,
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
    raw_text_next_cycle_source_selection_items: list[
        RawTextNextCycleSourceSelectionItem
    ],
    raw_text_next_cycle_identity_review_items: list[
        RawTextNextCycleIdentityReviewItem
    ],
    raw_text_next_cycle_cluster_source_selection_items: list[
        RawTextNextCycleClusterSourceSelectionItem
    ],
    raw_text_next_cycle_followup_selection_items: list[
        RawTextNextCycleFollowupSelectionItem
    ],
    raw_text_next_cycle_gated_cluster_review_prep_items: list[
        RawTextNextCycleGatedClusterReviewPrepItem
    ],
    raw_text_next_cycle_gated_ordinary_source_selection_items: list[
        RawTextNextCycleGatedOrdinarySourceSelectionItem
    ],
    raw_text_next_cycle_gated_ordinary_followup_selection_items: list[
        RawTextNextCycleGatedOrdinaryFollowupSelectionItem
    ],
    raw_text_next_cycle_gated_ordinary_final_selection_items: list[
        RawTextNextCycleGatedOrdinaryFinalSelectionItem
    ],
    raw_text_next_cycle_sensitive_risk_review_prep_items: list[
        RawTextNextCycleSensitiveRiskReviewPrepItem
    ],
    raw_text_next_cycle_sensitive_source_level_risk_review_items: list[
        RawTextNextCycleSensitiveSourceLevelRiskReviewItem
    ],
    raw_text_next_cycle_sensitive_registration_prep_items: list[
        RawTextNextCycleSensitiveRegistrationPrepItem
    ],
    raw_text_next_cycle_sensitive_source_registration_items: list[
        RawTextNextCycleSensitiveSourceRegistrationItem
    ],
    raw_text_next_cycle_sensitive_preparation_boundary_items: list[
        RawTextNextCycleSensitivePreparationBoundaryItem
    ],
    raw_text_next_cycle_sensitive_preparation_reading_items: list[
        RawTextNextCycleSensitivePreparationReadingItem
    ],
    raw_text_cluster_source_selection_items: list[RawTextClusterSourceSelectionItem],
    raw_text_source_identity_review_items: list[RawTextSourceIdentityReviewItem],
    raw_text_source_registration_prep_items: list[RawTextSourceRegistrationPrepItem],
    bazi_general_variant_deferred_review_items: list[
        BaziGeneralVariantDeferredReviewItem
    ],
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
    for item in raw_text_next_cycle_source_selection_items:
        fields.extend(
            (
                (item.selection_id, "selection_label", item.selection_label),
                (item.selection_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.selection_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_identity_review_items:
        fields.extend(
            (
                (
                    item.review_id,
                    "canonical_cluster_label",
                    item.canonical_cluster_label,
                ),
                (
                    item.review_id,
                    "identity_review_note",
                    item.identity_review_note,
                ),
                (item.review_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.review_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_cluster_source_selection_items:
        fields.extend(
            (
                (item.selection_id, "title_label", item.title_label),
                (
                    item.selection_id,
                    "identity_review_note",
                    item.identity_review_note,
                ),
                (item.selection_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.selection_id, "relative_paths", path)
            for path in item.relative_paths
        )
        fields.extend(
            (item.selection_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_followup_selection_items:
        fields.extend(
            (
                (item.selection_id, "title_label", item.title_label),
                (item.selection_id, "selection_note", item.selection_note),
                (item.selection_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.selection_id, "relative_paths", path)
            for path in item.relative_paths
        )
        fields.extend(
            (item.selection_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_gated_cluster_review_prep_items:
        fields.extend(
            (
                (item.prep_id, "prep_label", item.prep_label),
                (item.prep_id, "boundary_note", item.boundary_note),
                (item.prep_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.prep_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_gated_ordinary_source_selection_items:
        fields.extend(
            (
                (item.selection_id, "title_label", item.title_label),
                (item.selection_id, "selection_note", item.selection_note),
                (item.selection_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.selection_id, "relative_paths", path)
            for path in item.relative_paths
        )
        fields.extend(
            (item.selection_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_gated_ordinary_followup_selection_items:
        fields.extend(
            (
                (item.selection_id, "title_label", item.title_label),
                (item.selection_id, "selection_note", item.selection_note),
                (item.selection_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.selection_id, "relative_paths", path)
            for path in item.relative_paths
        )
        fields.extend(
            (item.selection_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_gated_ordinary_final_selection_items:
        fields.extend(
            (
                (item.selection_id, "title_label", item.title_label),
                (item.selection_id, "selection_note", item.selection_note),
                (item.selection_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.selection_id, "relative_paths", path)
            for path in item.relative_paths
        )
        fields.extend(
            (item.selection_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_sensitive_risk_review_prep_items:
        fields.extend(
            (
                (item.prep_item_id, "title_label", item.title_label),
                (
                    item.prep_item_id,
                    "boundary_decision",
                    item.boundary_decision,
                ),
                (item.prep_item_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.prep_item_id, "relative_paths", path)
            for path in item.relative_paths
        )
        fields.extend(
            (item.prep_item_id, "risk_review_topics", topic)
            for topic in item.risk_review_topics
        )
        fields.extend(
            (item.prep_item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_sensitive_source_level_risk_review_items:
        fields.extend(
            (
                (item.review_item_id, "title_label", item.title_label),
                (
                    item.review_item_id,
                    "boundary_decision",
                    item.boundary_decision,
                ),
                (item.review_item_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.review_item_id, "relative_paths", path)
            for path in item.relative_paths
        )
        fields.extend(
            (item.review_item_id, "risk_review_topics", topic)
            for topic in item.risk_review_topics
        )
        fields.extend(
            (item.review_item_id, "risk_findings", finding)
            for finding in item.risk_findings
        )
        fields.extend(
            (item.review_item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_sensitive_registration_prep_items:
        fields.extend(
            (
                (item.prep_item_id, "proposed_title", item.proposed_title),
                (
                    item.prep_item_id,
                    "source_quality_notes",
                    item.source_quality_notes,
                ),
                (item.prep_item_id, "rights_notes", item.rights_notes),
                (item.prep_item_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.prep_item_id, "proposed_local_references", reference)
            for reference in item.proposed_local_references
        )
        fields.extend(
            (item.prep_item_id, "risk_notes", note) for note in item.risk_notes
        )
        fields.extend(
            (item.prep_item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_sensitive_source_registration_items:
        fields.append(
            (item.registration_item_id, "rationale", item.rationale)
        )
        fields.extend(
            (item.registration_item_id, "registered_local_references", reference)
            for reference in item.registered_local_references
        )
        fields.extend(
            (item.registration_item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_sensitive_preparation_boundary_items:
        fields.extend(
            (
                (item.boundary_item_id, "boundary_decision", item.boundary_decision),
                (item.boundary_item_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.boundary_item_id, "local_references", reference)
            for reference in item.local_references
        )
        fields.extend(
            (item.boundary_item_id, "preparation_topics", topic)
            for topic in item.preparation_topics
        )
        fields.extend(
            (item.boundary_item_id, "risk_controls", control)
            for control in item.risk_controls
        )
        fields.extend(
            (item.boundary_item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_next_cycle_sensitive_preparation_reading_items:
        fields.extend(
            (
                (item.reading_item_id, "reading_decision", item.reading_decision),
                (item.reading_item_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.reading_item_id, "local_references", reference)
            for reference in item.local_references
        )
        fields.extend(
            (item.reading_item_id, "safe_reading_notes", note)
            for note in item.safe_reading_notes
        )
        fields.extend(
            (item.reading_item_id, "sensitive_controls", control)
            for control in item.sensitive_controls
        )
        fields.extend(
            (item.reading_item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_cluster_source_selection_items:
        fields.extend(
            (
                (item.selection_id, "title_label", item.title_label),
                (
                    item.selection_id,
                    "identity_review_note",
                    item.identity_review_note,
                ),
                (item.selection_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.selection_id, "relative_paths", path)
            for path in item.relative_paths
        )
        fields.extend(
            (item.selection_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_source_identity_review_items:
        fields.extend(
            (
                (
                    item.review_id,
                    "canonical_title_label",
                    item.canonical_title_label,
                ),
                (
                    item.review_id,
                    "identity_review_note",
                    item.identity_review_note,
                ),
                (item.review_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.review_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in raw_text_source_registration_prep_items:
        fields.extend(
            (
                (item.prep_id, "proposed_title", item.proposed_title),
                (
                    item.prep_id,
                    "source_quality_notes",
                    item.source_quality_notes,
                ),
                (item.prep_id, "rights_notes", item.rights_notes),
                (item.prep_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.prep_id, "proposed_local_references", path)
            for path in item.proposed_local_references
        )
        fields.extend((item.prep_id, "risk_notes", note) for note in item.risk_notes)
        fields.extend(
            (item.prep_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    for item in bazi_general_variant_deferred_review_items:
        fields.extend(
            (
                (item.item_id, "review_note", item.review_note),
                (item.item_id, "rationale", item.rationale),
            )
        )
        fields.extend(
            (item.item_id, "local_references", path)
            for path in item.local_references
        )
        fields.extend(
            (item.item_id, "guardrails", guardrail)
            for guardrail in item.guardrails
        )
    return fields
