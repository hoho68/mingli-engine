from dataclasses import dataclass, field
from typing import Literal


SOURCE_TYPES = frozenset({"pdf", "markdown"})
CalculationStatus = Literal[
    "not_computed", "computed", "indeterminate", "disputed"
]
CalculationConfidence = Literal["high", "medium", "low"]
CALCULATION_STATUSES = frozenset(
    {"not_computed", "computed", "indeterminate", "disputed"}
)
CALCULATION_CONFIDENCES = frozenset({"high", "medium", "low"})
EXTRACTION_STATUSES = frozenset({"not_started", "converted", "partial", "failed"})
REVIEW_STATUSES = frozenset({"unreviewed", "reviewed", "approved", "blocked"})
REPORT_USABLE_REVIEW_STATUS = "approved"
RISK_TIERS = frozenset({"ordinary", "sensitive", "high_risk"})
CURATION_BATCH_REVIEW_STATUSES = frozenset(
    {"draft", "reviewed", "approved", "blocked"}
)
REPORT_USABLE_BATCH_REVIEW_STATUSES = frozenset({"reviewed", "approved"})
CONFIDENCE_LEVELS = frozenset({"strong", "moderate", "weak"})
SOURCE_QUALITIES = frozenset(
    {"direct_extract", "review_note", "secondary_index", "needs_recheck"}
)
MATERIAL_TYPES = frozenset({"pdf", "markdown", "review_note", "other"})
MATERIAL_TRACKING_STATUSES = frozenset(
    {"external_untracked", "project_tracked", "derived_note"}
)
MATERIAL_PREPARATION_STATUSES = frozenset(
    {"not_started", "indexed", "partially_reviewed", "reviewed", "blocked"}
)
CANDIDATE_EXTRACT_STATUSES = frozenset(
    {"draft", "pending_review", "returned", "approved", "rejected", "blocked", "promoted"}
)
REVIEW_DECISIONS = frozenset({"approved", "returned", "rejected", "blocked"})
PROMOTION_BATCH_REVIEW_STATUSES = frozenset(
    {"draft", "reviewed", "approved", "blocked"}
)
SOURCE_LIBRARY_MATERIAL_TYPES = frozenset(
    {"pdf", "markdown", "review_note", "book_excerpt", "other"}
)
SOURCE_LIBRARY_READINESS_STATUSES = frozenset(
    {
        "not_started",
        "needs_preparation",
        "ready_for_extraction",
        "in_extraction",
        "review_completed",
        "exhausted",
        "deferred",
        "duplicate",
        "blocked",
    }
)
SOURCE_LIBRARY_PRIORITY_LEVELS = frozenset(
    {"critical", "high", "medium", "low", "deferred"}
)
SOURCE_LIBRARY_EXPECTED_VALUES = frozenset(
    {
        "fills_gap",
        "clarifies_conflict",
        "confirms_existing_rule",
        "improves_high_risk_boundary",
        "broadens_school_coverage",
        "documents_non_usefulness",
    }
)
SOURCE_LIBRARY_EFFORT_LEVELS = frozenset({"low", "medium", "high"})
SOURCE_LIBRARY_NEXT_ACTIONS = frozenset(
    {
        "prepare_material",
        "extract_candidates",
        "review_candidates",
        "promote_approved",
        "revisit_conflict",
        "defer",
        "block",
        "no_action",
    }
)
SOURCE_LIBRARY_BATCH_STATUSES = frozenset(
    {"planned", "active", "review_ready", "completed", "deferred", "blocked"}
)
SOURCE_LIBRARY_VALUE_STATUSES = frozenset(
    {
        "not_started",
        "in_progress",
        "value_produced",
        "non_useful_documented",
        "deferred",
        "blocked",
    }
)
SOURCE_LIBRARY_SUBJECT_TYPES = frozenset({"source", "batch"})
MATERIAL_AUDIT_SCOPES = frozenset(
    {"bazi", "ziwei", "qimen", "ritual_remedy", "mixed", "out_of_scope"}
)
MATERIAL_REPRESENTATION_TYPES = frozenset(
    {
        "root_pdf",
        "raw_markdown",
        "cleaned_markdown",
        "learning_note",
        "processing_status_note",
        "knowledge_skeleton",
        "image_asset",
        "raw_folder",
        "other",
    }
)
MATERIAL_AUDIT_SOURCE_BOUNDARIES = frozenset(
    {"external_untracked", "project_tracked_metadata", "derived_note_only"}
)
MATERIAL_AUDIT_IDENTITY_CONFIDENCES = frozenset(
    {"confirmed", "likely", "uncertain", "conflicting"}
)
MATERIAL_AUDIT_PREPARATION_STATES = frozenset(
    {
        "not_started",
        "raw_available",
        "prepared_text_available",
        "cleaned_text_available",
        "notes_available",
        "candidate_skeleton_available",
        "ready_for_extraction_review",
        "deferred",
        "blocked",
    }
)
MATERIAL_AUDIT_MATCH_TYPES = frozenset(
    {
        "exact",
        "likely",
        "possible_duplicate",
        "edition_variant",
        "missing_source_library_entry",
        "blocked_source_library_entry",
        "out_of_scope",
        "uncertain",
    }
)
MATERIAL_AUDIT_READINESS_STATES = frozenset(
    {
        "ready_for_extraction_review",
        "needs_cleaning",
        "needs_locator_review",
        "needs_source_registration",
        "needs_identity_clarification",
        "needs_rights_review",
        "needs_risk_review",
        "preparation_backlog",
        "deferred",
        "blocked",
    }
)
MATERIAL_AUDIT_QUEUE_TYPES = frozenset(
    {
        "extraction_ready",
        "preparation_backlog",
        "registration_backlog",
        "risk_review_backlog",
        "blocked_backlog",
    }
)
MATERIAL_AUDIT_ACTIONS = frozenset(
    {
        "register_source",
        "clarify_identity",
        "prepare_text",
        "review_cleaned_text",
        "risk_review",
        "select_bounded_source",
        "extract_candidates",
        "defer",
        "block",
        "no_action",
    }
)
MATERIAL_AUDIT_TEXT_QUALITIES = frozenset(
    {"unknown", "raw_ocr", "noisy", "usable", "cleaned", "summary_only", "not_text"}
)
MATERIAL_AUDIT_LOCATOR_QUALITIES = frozenset(
    {
        "none",
        "folder_only",
        "file_only",
        "heading",
        "line_window",
        "page_or_section",
        "review_anchor",
    }
)
MATERIAL_AUDIT_TEXT_PREPARATION_STATUSES = frozenset(
    {"not_started", "raw_only", "prepared", "cleaned", "summary_only", "not_applicable"}
)
MATERIAL_AUDIT_LOCATOR_CONFIDENCES = frozenset(
    {"none", "weak", "moderate", "strong"}
)
MATERIAL_AUDIT_SOURCE_QUALITIES = frozenset(
    {"strong", "moderate", "weak", "needs_recheck"}
)
MATERIAL_AUDIT_QUEUE_STATUSES = frozenset(
    {"planned", "active", "completed", "deferred", "blocked"}
)
EXTRACTION_PACKAGE_STATUSES = frozenset(
    {"planned", "active", "completed", "deferred", "blocked"}
)
EXTRACTION_TASK_STATUSES = frozenset(
    {"planned", "active", "completed", "deferred", "blocked"}
)
CANDIDATE_DRAFT_SLOT_STATUSES = frozenset(
    {"planned", "ready_for_manual_extraction", "deferred", "blocked"}
)
PREREQUISITE_BACKLOG_TYPES = frozenset(
    {"registration", "preparation", "locator_review", "risk_review", "deferred", "blocked"}
)
EXTRACTION_PACKAGE_PRIORITY_LEVELS = frozenset(
    {"critical", "high", "medium", "low"}
)
EXTRACTION_PACKAGE_RISK_BOUNDARIES = RISK_TIERS
EXTRACTION_PACKAGE_LOCATOR_REQUIREMENTS = frozenset(
    {"file_only", "heading", "line_window", "page_or_section", "review_anchor"}
)
EXTRACTION_PACKAGE_MANUAL_ACTIONS = frozenset(
    {
        "extract_candidates",
        "register_source",
        "clarify_identity",
        "prepare_text",
        "review_cleaned_text",
        "risk_review",
        "defer",
        "block",
        "no_action",
    }
)
LEARNING_REFERENCE_NOTE_STATUSES = frozenset(
    {
        "draft",
        "ready_for_candidate_intake",
        "candidate_intake_started",
        "deferred",
        "blocked",
    }
)
LEARNING_POINT_READINESSES = frozenset(
    {
        "ready",
        "needs_locator",
        "needs_risk_review",
        "duplicate_review",
        "deferred",
        "blocked",
    }
)
CANDIDATE_INTAKE_DECISIONS = frozenset(
    {
        "create_candidate",
        "reuse_existing",
        "avoid_duplicate",
        "defer",
        "manual_review",
    }
)
CANDIDATE_INTAKE_DECISION_STATUSES = frozenset(
    {"planned", "applied", "deferred", "blocked"}
)
PREREQUISITE_ACTION_TYPES = PREREQUISITE_BACKLOG_TYPES
PREREQUISITE_ACTION_STATUSES = EXTRACTION_PACKAGE_STATUSES
LEARNING_REFERENCE_MANUAL_ACTIONS = frozenset(
    {
        "create_candidate",
        "reuse_existing",
        "avoid_duplicate",
        "manual_review",
        "register_source",
        "clarify_identity",
        "prepare_text",
        "review_cleaned_text",
        "risk_review",
        "defer",
        "block",
        "no_action",
    }
)
CONFLICT_TYPES = frozenset(
    {
        "school_difference",
        "textual_disagreement",
        "scope_mismatch",
        "insufficient_context",
    }
)
CONFLICT_SEVERITIES = frozenset({"minor", "moderate", "severe"})
CONFLICT_RESOLUTION_STATUSES = frozenset({"open", "documented", "resolved"})
CONCLUSION_STRENGTHS = frozenset(
    {"decided", "candidate", "weakly_supported", "disputed", "unavailable"}
)
RULE_FAMILIES = frozenset(
    {
        "pattern_strength",
        "useful_god_candidate",
        "taboo_god_candidate",
        "ten_god_relation",
        "five_element_balance",
        "branch_interaction",
        "blind_image_method",
        "luck_cycle",
        "remedy_boundary",
        "high_risk_signal",
    }
)


@dataclass(frozen=True)
class BirthProfile:
    calendar_type: str
    birth_date: str
    birth_time: str
    birthplace: str
    gender: str
    focus_topic: str


@dataclass(frozen=True)
class IntakeValidationResult:
    report_ready: bool
    missing_fields: list[str] = field(default_factory=list)
    clarification_questions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SafetyReviewResult:
    allowed: bool
    red_line_categories: list[str] = field(default_factory=list)
    prohibited_phrases: list[str] = field(default_factory=list)
    disclaimer_present: bool = False
    redirect_message: str = ""


@dataclass(frozen=True)
class ClassicalSource:
    source_id: str
    title: str
    file_name: str
    source_type: str
    extraction_status: str
    review_status: str
    scope_notes: str
    risk_notes: list[str] = field(default_factory=list)
    curation_gap_reason: str = ""
    review_reference: str = ""


@dataclass(frozen=True)
class EvidenceUnit:
    evidence_id: str
    source_id: str
    source_ref: str
    theme: str
    rule_family: str
    risk_tier: str
    summary: str
    applicability: list[str]
    limitations: list[str]
    school: str = ""
    curation_batch_id: str = ""
    confidence: str = "moderate"
    source_quality: str = "review_note"
    conflict_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CurationBatch:
    batch_id: str
    source_ids: list[str]
    evidence_ids: list[str]
    review_status: str
    review_notes: str
    unresolved_issues: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SourceConflict:
    conflict_id: str
    rule_family: str
    evidence_ids: list[str]
    conflict_type: str
    reader_note: str
    severity: str
    resolution_status: str


@dataclass(frozen=True)
class CurationGap:
    gap_id: str
    source_id: str
    reason: str
    rule_family: str = ""
    blocks_report_use: bool = False


@dataclass(frozen=True)
class CoverageReport:
    source_counts: dict[str, int]
    rule_family_counts: dict[str, int]
    risk_tier_counts: dict[str, int]
    approved_evidence_count: int
    sources_with_gaps: list[str] = field(default_factory=list)
    open_conflicts: list[str] = field(default_factory=list)
    high_risk_without_limitations: list[str] = field(default_factory=list)
    long_summary_violations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class KnowledgeActivationSummary:
    activation_status: str
    source_count: int
    report_usable_source_count: int
    approved_evidence_count: int
    required_rule_families: list[str]
    enabled_rule_families: list[str]
    missing_rule_families: list[str]
    rule_family_counts: dict[str, int]
    risk_tier_counts: dict[str, int]
    sources_with_gaps: list[str]
    open_conflicts: list[str]
    quality_failures: list[str]
    formal_conclusion_count: int
    unavailable_conclusion_count: int
    next_action: str
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReportAcceptanceCaseResult:
    case_id: str
    scenario_type: str
    status: str
    checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReportAcceptanceSummary:
    baseline_id: str
    acceptance_status: str
    case_count: int
    passed_case_count: int
    activation_status: str
    report_audit_status: str
    approved_evidence_count: int
    rule_family_count: int
    traced_evidence_unit_count: int
    missing_rule_families: list[str]
    open_conflicts: list[str]
    cases: list[ReportAcceptanceCaseResult]
    guardrails: list[str]
    next_action: str


@dataclass(frozen=True)
class ReportReleaseCaseResult:
    case_id: str
    scenario_type: str
    status: str
    output_formats: list[str]
    checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReportReleaseSummary:
    release_id: str
    release_status: str
    manifest_case_count: int
    passed_case_count: int
    failed_case_count: int
    safe_report_case_count: int
    guarded_report_case_count: int
    rejected_request_case_count: int
    distinct_report_output_count: int
    acceptance_baseline_id: str
    acceptance_status: str
    approved_evidence_count: int
    rule_family_count: int
    action_track_count: int
    cases: list[ReportReleaseCaseResult]
    guardrails: list[str]
    next_action: str


@dataclass(frozen=True)
class ProjectCompletionFeatureResult:
    feature_id: str
    artifact_status: str
    spec_present: bool
    plan_present: bool
    functional_requirement_count: int
    success_criteria_count: int
    task_tracking_status: str
    checked_task_count: int
    unchecked_task_count: int
    checklist_status: str
    checked_checklist_item_count: int
    unchecked_checklist_item_count: int


@dataclass(frozen=True)
class ProjectCompletionSummary:
    baseline_id: str
    completion_status: str
    feature_count: int
    spec_count: int
    plan_count: int
    task_tracked_feature_count: int
    legacy_feature_count: int
    functional_requirement_count: int
    success_criteria_count: int
    checked_task_count: int
    unchecked_task_count: int
    checklist_file_count: int
    checked_checklist_item_count: int
    unchecked_checklist_item_count: int
    quality_checks: dict[str, str]
    completion_checks: dict[str, str]
    release_id: str
    release_status: str
    acceptance_baseline_id: str
    acceptance_status: str
    approved_evidence_count: int
    rule_family_count: int
    action_track_count: int
    open_conflicts: list[str]
    legacy_feature_ids: list[str]
    features: list[ProjectCompletionFeatureResult]
    controlled_boundaries: list[str]
    remaining_local_blockers: list[str]
    next_action: str


@dataclass(frozen=True)
class SourceMaterial:
    material_id: str
    title: str
    material_type: str
    file_label: str
    tracking_status: str
    preparation_status: str
    related_source_id: str = ""
    scope_notes: str = ""
    rights_notes: str = ""
    gap_reason: str = ""


@dataclass(frozen=True)
class CandidateExtract:
    candidate_id: str
    material_id: str
    source_locator: str
    extracted_meaning: str
    proposed_rule_family: str
    risk_tier: str
    status: str
    proposed_limitations: list[str] = field(default_factory=list)
    short_quote: str = ""
    related_evidence_ids: list[str] = field(default_factory=list)
    related_conflict_ids: list[str] = field(default_factory=list)
    related_gap_ids: list[str] = field(default_factory=list)
    duplicate_of: str = ""
    created_by: str = ""
    created_at: str = ""


@dataclass(frozen=True)
class ReviewDecision:
    decision_id: str
    candidate_id: str
    decision: str
    reviewer: str
    reviewed_at: str
    rationale: str
    required_changes: list[str] = field(default_factory=list)
    rejection_reason: str = ""
    approval_limitations: list[str] = field(default_factory=list)
    source_quality: str = "review_note"
    confidence: str = "moderate"


@dataclass(frozen=True)
class PromotionBatch:
    promotion_batch_id: str
    candidate_ids: list[str]
    target_evidence_ids: list[str]
    review_status: str
    review_notes: str
    unresolved_issues: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class IntakeProgressReport:
    material_counts: dict[str, int]
    candidate_counts: dict[str, int]
    risk_tier_counts: dict[str, int]
    rule_family_counts: dict[str, int]
    pending_review_count: int
    approved_not_promoted_count: int
    blocked_or_rejected_count: int
    duplicate_candidates: list[str] = field(default_factory=list)
    conflict_link_count: int = 0
    gap_link_count: int = 0


@dataclass(frozen=True)
class PromotionPlan:
    """Read-only plan describing the evidence units a promotion would create."""

    promotion_batch_id: str
    evidence_units: list[EvidenceUnit] = field(default_factory=list)
    promoted_count: int = 0
    target_evidence_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PromotionResult:
    """Outcome of an explicitly applied promotion."""

    promotion_batch_id: str
    promoted_count: int
    target_evidence_ids: list[str] = field(default_factory=list)
    promoted_candidate_ids: list[str] = field(default_factory=list)



@dataclass(frozen=True)
class CandidateReviewWorkItem:
    candidate_id: str
    material_id: str
    status: str
    proposed_rule_family: str
    risk_tier: str
    source_locator: str
    required_review_actions: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewDecisionPacket:
    candidate_id: str
    material_id: str
    candidate_status: str
    decision_options: list[str]
    required_review_inputs: list[str] = field(default_factory=list)
    approval_blockers: list[str] = field(default_factory=list)
    packet_actions: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewPacketSummary:
    packet_count: int
    candidate_ids: list[str]
    decision_option_counts: dict[str, int]
    required_input_counts: dict[str, int]
    approval_blocker_counts: dict[str, int]
    packet_action_counts: dict[str, int]
    review_decision_delta: int = 0
    formal_evidence_delta: int = 0


@dataclass(frozen=True)
class CandidateReviewActionQueueItem:
    candidate_id: str
    priority: str
    primary_action: str
    reason: str
    blocking_inputs: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewInputTemplate:
    candidate_id: str
    material_id: str
    candidate_status: str
    decision_id_hint: str
    current_source_locator: str
    base_fields: list[str] = field(default_factory=list)
    outcome_fields: dict[str, list[str]] = field(default_factory=dict)
    conditional_fields: list[str] = field(default_factory=list)
    blocking_inputs: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewDraftValidationResult:
    candidate_id: str
    decision_id: str
    review_outcome: str
    ready_for_manual_application: bool
    missing_fields: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    normalized_review_decision: dict[str, object] = field(default_factory=dict)
    review_decision_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewApplicationGuardResult:
    candidate_id: str
    decision_id: str
    review_outcome: str
    ready_to_apply: bool
    current_candidate_status: str = ""
    next_candidate_status: str = ""
    review_decision_preview: dict[str, object] = field(default_factory=dict)
    candidate_status_preview: dict[str, str] = field(default_factory=dict)
    validation_missing_fields: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    preview_review_decision_delta: int = 0
    preview_candidate_status_delta: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewApplicationPacket:
    candidate_id: str
    decision_id: str
    ready_to_export: bool
    review_decision_json: dict[str, object] = field(default_factory=dict)
    candidate_status_update: dict[str, str] = field(default_factory=dict)
    manual_checklist: list[str] = field(default_factory=list)
    rollback_notes: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    preview_review_decision_delta: int = 0
    preview_candidate_status_delta: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewApplicationAuditSummary:
    pending_template_count: int
    draft_count: int
    validation_ready_count: int
    validation_blocked_count: int
    guard_ready_count: int
    packet_exportable_count: int
    packet_blocked_count: int
    pending_candidate_ids: list[str] = field(default_factory=list)
    draft_candidate_ids: list[str] = field(default_factory=list)
    exportable_candidate_ids: list[str] = field(default_factory=list)
    blocked_candidate_ids: list[str] = field(default_factory=list)
    missing_draft_candidate_ids: list[str] = field(default_factory=list)
    candidate_next_actions: dict[str, str] = field(default_factory=dict)
    preview_review_decision_delta: int = 0
    preview_candidate_status_delta: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualActionDashboard:
    pending_candidate_count: int
    action_counts: dict[str, int]
    candidates_by_action: dict[str, list[str]]
    recommended_action_sequence: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    preview_review_decision_delta: int = 0
    preview_candidate_status_delta: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationDryRunStep:
    candidate_id: str
    action: str
    dry_run_status: str
    required_inputs: list[str] = field(default_factory=list)
    manual_steps: list[str] = field(default_factory=list)
    ready_criteria: list[str] = field(default_factory=list)
    post_apply_checks: list[str] = field(default_factory=list)
    rollback_notes: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationDryRunGuide:
    pending_candidate_count: int
    step_count: int
    steps: list[CandidateReviewManualApplicationDryRunStep]
    recommended_processing_order: list[str] = field(default_factory=list)
    preview_review_decision_delta: int = 0
    preview_candidate_status_delta: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationPreflightCheck:
    candidate_id: str
    decision_id: str
    ready_for_manual_application: bool
    decision_id_unique: bool
    candidate_status_patch_matches_pending: bool
    packet_delta_matches_preview: bool
    expected_review_decision_delta: int = 0
    expected_candidate_status_delta: int = 0
    expected_candidate_status_update: dict[str, str] = field(default_factory=dict)
    preflight_blockers: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationPreflightReport:
    pending_candidate_count: int
    preflight_check_count: int
    checks: list[CandidateReviewManualApplicationPreflightCheck]
    ready_candidate_ids: list[str] = field(default_factory=list)
    blocked_candidate_ids: list[str] = field(default_factory=list)
    preview_review_decision_delta: int = 0
    preview_candidate_status_delta: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationHandoffItem:
    candidate_id: str
    action: str
    readiness_status: str
    shortest_next_action: str
    decision_id: str = ""
    required_inputs: list[str] = field(default_factory=list)
    manual_steps: list[str] = field(default_factory=list)
    preflight_checks: list[str] = field(default_factory=list)
    post_apply_checks: list[str] = field(default_factory=list)
    rollback_notes: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    expected_candidate_status_update: dict[str, str] = field(default_factory=dict)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationHandoffSummary:
    pending_candidate_count: int
    handoff_item_count: int
    items: list[CandidateReviewManualApplicationHandoffItem]
    ready_candidate_ids: list[str] = field(default_factory=list)
    blocked_candidate_ids: list[str] = field(default_factory=list)
    missing_draft_candidate_ids: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    preview_review_decision_delta: int = 0
    preview_candidate_status_delta: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationReadinessLedgerRow:
    candidate_id: str
    sequence_number: int
    ledger_status: str
    action: str
    checkboxes: list[str] = field(default_factory=list)
    required_inputs: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    expected_candidate_status_update: dict[str, str] = field(default_factory=dict)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationReadinessLedger:
    pending_candidate_count: int
    ledger_row_count: int
    rows: list[CandidateReviewManualApplicationReadinessLedgerRow]
    ready_candidate_ids: list[str] = field(default_factory=list)
    blocked_candidate_ids: list[str] = field(default_factory=list)
    missing_draft_candidate_ids: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    unchecked_checkbox_count: int = 0
    preview_review_decision_delta: int = 0
    preview_candidate_status_delta: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationSessionAction:
    candidate_id: str
    sequence_number: int
    action_type: str
    ledger_status: str
    checkboxes: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    expected_candidate_status_update: dict[str, str] = field(default_factory=dict)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationSessionPacket:
    session_id: str
    session_title: str
    session_scope: str
    pending_candidate_count: int
    ready_action_queue: list[CandidateReviewManualApplicationSessionAction]
    blocked_follow_ups: list[CandidateReviewManualApplicationSessionAction]
    missing_draft_follow_ups: list[CandidateReviewManualApplicationSessionAction]
    post_session_verification: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    unchecked_checkbox_count: int = 0
    preview_review_decision_delta: int = 0
    preview_candidate_status_delta: int = 0
    ready_action_count: int = 0
    blocked_follow_up_count: int = 0
    missing_draft_follow_up_count: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationSessionOutcomeItem:
    candidate_id: str
    sequence_number: int
    session_lane: str
    action_type: str
    current_candidate_status: str
    projected_candidate_status: str
    projected_outcome: str
    projected_review_decision_delta: int = 0
    projected_candidate_status_delta: int = 0
    remaining_follow_up_action: str = ""
    blocking_issues: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationSessionOutcomePreview:
    session_id: str
    preview_scope: str
    pending_candidate_count: int
    preview_item_count: int
    items: list[CandidateReviewManualApplicationSessionOutcomeItem]
    ready_applied_candidate_ids: list[str] = field(default_factory=list)
    projected_non_pending_candidate_ids: list[str] = field(default_factory=list)
    projected_remaining_pending_candidate_ids: list[str] = field(default_factory=list)
    follow_up_candidate_ids: list[str] = field(default_factory=list)
    post_session_next_actions: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    projected_review_decision_delta: int = 0
    projected_candidate_status_delta: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationPostSessionVerificationItem:
    candidate_id: str
    sequence_number: int
    verification_lane: str
    expected_candidate_status: str
    actual_candidate_status: str
    expected_review_decision_id: str = ""
    actual_review_decision_id: str = ""
    actual_review_decision: str = ""
    verification_status: str = ""
    blocking_issues: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationPostSessionVerificationReport:
    session_id: str
    verification_scope: str
    post_session_status: str
    verification_item_count: int
    items: list[CandidateReviewManualApplicationPostSessionVerificationItem]
    expected_ready_candidate_count: int = 0
    verified_ready_candidate_ids: list[str] = field(default_factory=list)
    blocked_ready_candidate_ids: list[str] = field(default_factory=list)
    verified_follow_up_candidate_ids: list[str] = field(default_factory=list)
    blocked_follow_up_candidate_ids: list[str] = field(default_factory=list)
    expected_review_decision_delta: int = 0
    expected_candidate_status_delta: int = 0
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationReconciliationItem:
    candidate_id: str
    sequence_number: int
    source_verification_lane: str
    verification_status: str
    recommended_action: str
    reason_codes: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationReconciliationDashboard:
    session_id: str
    reconciliation_scope: str
    post_session_status: str
    reconciliation_item_count: int
    items: list[CandidateReviewManualApplicationReconciliationItem]
    action_counts: dict[str, int] = field(default_factory=dict)
    candidates_by_action: dict[str, list[str]] = field(default_factory=dict)
    recommended_action_sequence: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationClosureItem:
    candidate_id: str
    sequence_number: int
    closure_lane: str
    closure_action: str
    closure_status: str
    source_reconciliation_action: str
    reason_codes: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationClosurePacket:
    session_id: str
    closure_scope: str
    closure_status: str
    closure_item_count: int
    items: list[CandidateReviewManualApplicationClosureItem]
    close_candidate_ids: list[str] = field(default_factory=list)
    carry_forward_candidate_ids: list[str] = field(default_factory=list)
    closure_action_counts: dict[str, int] = field(default_factory=dict)
    candidates_by_closure_action: dict[str, list[str]] = field(default_factory=dict)
    recommended_next_session_setup: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionStarterItem:
    candidate_id: str
    sequence_number: int
    starter_lane: str
    starter_action: str
    starter_status: str
    source_closure_action: str
    checklist: list[str] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionStarter:
    session_id: str
    starter_scope: str
    starter_status: str
    starter_item_count: int
    items: list[CandidateReviewManualApplicationNextSessionStarterItem]
    starter_lane_counts: dict[str, int] = field(default_factory=dict)
    candidates_by_starter_lane: dict[str, list[str]] = field(default_factory=dict)
    recommended_start_order: list[str] = field(default_factory=list)
    kickoff_checklist: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionPacketItem:
    candidate_id: str
    sequence_number: int
    packet_lane: str
    starter_lane: str
    packet_action: str
    starter_action: str
    packet_status: str
    source_closure_action: str
    checklist: list[str] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionPacket:
    session_id: str
    packet_scope: str
    packet_status: str
    packet_item_count: int
    items: list[CandidateReviewManualApplicationNextSessionPacketItem]
    correction_queue: list[CandidateReviewManualApplicationNextSessionPacketItem]
    follow_up_queue: list[CandidateReviewManualApplicationNextSessionPacketItem]
    correction_candidate_ids: list[str] = field(default_factory=list)
    follow_up_candidate_ids: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    kickoff_checklist: list[str] = field(default_factory=list)
    post_session_verification: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionAuditSummary:
    session_id: str
    audit_scope: str
    audit_status: str
    closure_status: str
    starter_status: str
    packet_status: str
    closure_item_count: int
    starter_item_count: int
    packet_item_count: int
    correction_queue_count: int
    follow_up_queue_count: int
    correction_candidate_ids: list[str] = field(default_factory=list)
    follow_up_candidate_ids: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    shortest_next_actions: list[str] = field(default_factory=list)
    coverage_checks: dict[str, str] = field(default_factory=dict)
    kickoff_checklist: list[str] = field(default_factory=list)
    post_session_verification: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionOperatorChecklistItem:
    action_id: str
    sequence_number: int
    operator_action: str
    action_status: str
    target_candidates: list[str] = field(default_factory=list)
    ready_criteria: list[str] = field(default_factory=list)
    operator_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionOperatorChecklist:
    session_id: str
    checklist_scope: str
    checklist_status: str
    checklist_item_count: int
    items: list[CandidateReviewManualApplicationNextSessionOperatorChecklistItem]
    action_sequence: list[str] = field(default_factory=list)
    target_candidates_by_action: dict[str, list[str]] = field(default_factory=dict)
    recommended_processing_order: list[str] = field(default_factory=list)
    kickoff_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionExecutionHandoff:
    session_id: str
    handoff_scope: str
    handoff_status: str
    first_action: str
    first_action_targets: list[str] = field(default_factory=list)
    ready_conditions: list[str] = field(default_factory=list)
    blocked_conditions: list[str] = field(default_factory=list)
    action_sequence: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    kickoff_checklist: list[str] = field(default_factory=list)
    verification_chain: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionCompletionCriteria:
    session_id: str
    criteria_scope: str
    criteria_status: str
    first_action: str
    first_action_targets: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    done_conditions: list[str] = field(default_factory=list)
    blocked_conditions: list[str] = field(default_factory=list)
    retry_conditions: list[str] = field(default_factory=list)
    verification_entrypoints: list[str] = field(default_factory=list)
    action_sequence: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionRetryPlanner:
    session_id: str
    retry_scope: str
    retry_status: str
    first_action: str
    first_action_targets: list[str] = field(default_factory=list)
    failure_entrypoints: list[str] = field(default_factory=list)
    retry_conditions: list[str] = field(default_factory=list)
    retry_sequence: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    verification_entrypoints: list[str] = field(default_factory=list)
    return_to_handoff_path: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionFinalReadinessSummary:
    session_id: str
    readiness_scope: str
    readiness_status: str
    start_gate: str
    first_action: str
    first_action_targets: list[str] = field(default_factory=list)
    ready_conditions: list[str] = field(default_factory=list)
    blocked_conditions: list[str] = field(default_factory=list)
    retry_conditions: list[str] = field(default_factory=list)
    failure_entrypoints: list[str] = field(default_factory=list)
    verification_entrypoints: list[str] = field(default_factory=list)
    return_to_handoff_path: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    recommended_processing_order: list[str] = field(default_factory=list)
    final_readiness_checks: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchNote:
    session_id: str
    launch_scope: str
    launch_status: str
    start_gate: str
    first_command: str
    first_command_targets: list[str] = field(default_factory=list)
    candidate_order: list[str] = field(default_factory=list)
    abort_conditions: list[str] = field(default_factory=list)
    return_paths: list[str] = field(default_factory=list)
    verification_commands: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    launch_checks: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchAudit:
    session_id: str
    audit_scope: str
    audit_status: str
    readiness_status: str
    launch_status: str
    start_gate: str
    first_command: str
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: list[str] = field(default_factory=list)
    candidate_order: list[str] = field(default_factory=list)
    return_paths: list[str] = field(default_factory=list)
    verification_commands: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    audit_status: str
    launch_status: str
    start_gate: str
    sealed_first_command: str
    sealed_candidate_order: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    verification_commands: list[str] = field(default_factory=list)
    rollback_entrypoints: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbook:
    session_id: str
    runbook_scope: str
    runbook_status: str
    seal_status: str
    start_gate: str
    first_step: str
    execution_order: list[str] = field(default_factory=list)
    step_verification: dict[str, list[str]] = field(default_factory=dict)
    failure_rollback: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    runbook_checks: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAudit:
    session_id: str
    audit_scope: str
    audit_status: str
    runbook_status: str
    seal_status: str
    start_gate: str
    first_step: str
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: list[str] = field(default_factory=list)
    candidate_order: list[str] = field(default_factory=list)
    execution_order: list[str] = field(default_factory=list)
    step_verification: dict[str, list[str]] = field(default_factory=dict)
    failure_rollback: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    verification_commands: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    audit_status: str
    runbook_status: str
    launch_seal_status: str
    start_gate: str
    sealed_first_step: str
    sealed_candidate_order: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    verification_commands: list[str] = field(default_factory=list)
    rollback_entrypoints: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacket:
    session_id: str
    launch_packet_scope: str
    launch_packet_status: str
    audit_seal_status: str
    sealed_first_step: str
    candidate_order: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAudit:
    session_id: str
    handoff_audit_scope: str
    handoff_readiness: str
    launch_packet_status: str
    audit_seal_status: str
    sealed_first_step: str
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    operator_safe_start_boundary: list[str] = field(default_factory=list)
    candidate_order: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    handoff_readiness: str
    go_no_go_decision: str
    launch_packet_status: str
    audit_seal_status: str
    sealed_first_step: str
    sealed_candidate_order: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    operator_safe_start_boundary: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionOperatorGoNoGoSealLaunchReceipt:
    session_id: str
    receipt_scope: str
    receipt_status: str
    seal_status: str
    handoff_readiness: str
    go_no_go_decision: str
    receipt_decision: str
    signed_first_step: str
    signed_candidate_order: list[str] = field(default_factory=list)
    operator_receipt_checklist: list[str] = field(default_factory=list)
    pre_execution_confirmation: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAudit:
    session_id: str
    boundary_audit_scope: str
    final_boundary_readiness: str
    receipt_status: str
    seal_status: str
    go_no_go_decision: str
    receipt_decision: str
    signed_first_step: str
    receipt_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    final_boundary_confirmation: list[str] = field(default_factory=list)
    signed_candidate_order: list[str] = field(default_factory=list)
    operator_receipt_checklist: list[str] = field(default_factory=list)
    pre_execution_confirmation: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    final_boundary_readiness: str
    receipt_status: str
    go_no_go_decision: str
    receipt_decision: str
    sealed_first_step: str
    sealed_candidate_order: list[str] = field(default_factory=list)
    receipt_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    final_boundary_confirmation: list[str] = field(default_factory=list)
    pre_execution_confirmation: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacket:
    session_id: str
    packet_scope: str
    packet_status: str
    seal_status: str
    final_boundary_readiness: str
    receipt_status: str
    go_no_go_decision: str
    receipt_decision: str
    start_authorization: str
    sealed_first_step: str
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    pre_execution_confirmation: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    packet_checks: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAudit:
    session_id: str
    audit_scope: str
    audit_status: str
    packet_status: str
    seal_status: str
    start_authorization: str
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    audit_status: str
    packet_status: str
    start_authorization: str
    blocked_reasons: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceipt:
    session_id: str
    receipt_scope: str
    receipt_status: str
    seal_status: str
    audit_status: str
    packet_status: str
    start_authorization: str
    sealed_first_step: str
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    receipt_checks: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAudit:
    session_id: str
    audit_scope: str
    coverage_audit_status: str
    receipt_status: str
    seal_status: str
    operator_start_packet_audit_status: str
    packet_status: str
    start_authorization: str
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    coverage_audit_status: str
    receipt_status: str
    operator_start_packet_audit_seal_status: str
    operator_start_packet_audit_status: str
    packet_status: str
    start_authorization: str
    blocked_reasons: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacket:
    session_id: str
    packet_scope: str
    packet_status: str
    seal_status: str
    coverage_audit_status: str
    receipt_status: str
    operator_start_packet_audit_status: str
    start_authorization: str
    sealed_first_step: str
    authorization_checks: list[str] = field(default_factory=list)
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAudit:
    session_id: str
    audit_scope: str
    audit_status: str
    packet_status: str
    seal_status: str
    coverage_audit_status: str
    receipt_status: str
    operator_start_packet_audit_status: str
    start_authorization: str
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    audit_status: str
    packet_status: str
    authorization_packet_seal_status: str
    coverage_audit_status: str
    receipt_status: str
    operator_start_packet_audit_status: str
    start_authorization: str
    seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSealStartDocket:
    session_id: str
    docket_scope: str
    docket_status: str
    seal_status: str
    audit_status: str
    packet_status: str
    authorization_packet_seal_status: str
    coverage_audit_status: str
    receipt_status: str
    operator_start_packet_audit_status: str
    start_authorization: str
    docket_checks: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAudit:
    session_id: str
    audit_scope: str
    audit_status: str
    docket_status: str
    seal_status: str
    audit_source_status: str
    packet_status: str
    authorization_packet_seal_status: str
    coverage_audit_status: str
    receipt_status: str
    operator_start_packet_audit_status: str
    start_authorization: str
    docket_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    audit_status: str
    docket_status: str
    source_seal_status: str
    audit_source_status: str
    packet_status: str
    authorization_packet_seal_status: str
    coverage_audit_status: str
    receipt_status: str
    operator_start_packet_audit_status: str
    start_authorization: str
    seal_checks: list[str] = field(default_factory=list)
    docket_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSealFinalStartPacket:
    session_id: str
    packet_scope: str
    packet_status: str
    seal_status: str
    audit_status: str
    docket_status: str
    source_seal_status: str
    audit_source_status: str
    packet_source_status: str
    authorization_packet_seal_status: str
    coverage_audit_status: str
    receipt_status: str
    operator_start_packet_audit_status: str
    start_authorization: str
    packet_checks: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAudit:
    session_id: str
    handoff_audit_scope: str
    handoff_readiness: str
    packet_status: str
    seal_status: str
    audit_status: str
    docket_status: str
    source_seal_status: str
    audit_source_status: str
    packet_source_status: str
    authorization_packet_seal_status: str
    coverage_audit_status: str
    receipt_status: str
    operator_start_packet_audit_status: str
    start_authorization: str
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    operator_safe_start_boundary: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    packet_status: str
    seal_source_status: str
    audit_status: str
    docket_status: str
    start_authorization: str
    seal_checks: list[str] = field(default_factory=list)
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    operator_safe_start_boundary: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSealStartAuthorizationPacket:
    session_id: str
    packet_scope: str
    packet_status: str
    seal_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    audit_status: str
    docket_status: str
    authorization_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAudit:
    session_id: str
    audit_scope: str
    audit_status: str
    packet_status: str
    seal_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    authorization_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    audit_status: str
    packet_status: str
    seal_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    authorization_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacket:
    session_id: str
    packet_scope: str
    packet_status: str
    seal_status: str
    audit_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAudit:
    session_id: str
    audit_scope: str
    audit_status: str
    packet_status: str
    seal_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    audit_status: str
    packet_status: str
    seal_source_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorization:
    session_id: str
    authorization_scope: str
    authorization_status: str
    seal_status: str
    audit_status: str
    packet_status: str
    seal_source_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    authorization_checks: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAudit:
    session_id: str
    audit_scope: str
    audit_status: str
    authorization_status: str
    seal_status: str
    packet_status: str
    seal_source_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    authorization_coverage_checks: dict[str, str] = field(default_factory=dict)
    authorization_checks: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    audit_status: str
    authorization_status: str
    seal_source_status: str
    packet_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    seal_checks: list[str] = field(default_factory=list)
    authorization_coverage_checks: dict[str, str] = field(default_factory=dict)
    authorization_checks: list[str] = field(default_factory=list)
    coverage_seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacket:
    session_id: str
    packet_scope: str
    handoff_packet_status: str
    handoff_status: str
    seal_status: str
    audit_status: str
    authorization_status: str
    seal_source_status: str
    packet_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    handoff_checks: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    authorization_coverage_checks: dict[str, str] = field(default_factory=dict)
    authorization_checks: list[str] = field(default_factory=list)
    coverage_seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAudit:
    session_id: str
    audit_scope: str
    audit_status: str
    handoff_packet_status: str
    handoff_status: str
    seal_status: str
    coverage_audit_status: str
    authorization_status: str
    packet_status: str
    seal_source_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    handoff_checks: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    authorization_coverage_checks: dict[str, str] = field(default_factory=dict)
    authorization_checks: list[str] = field(default_factory=list)
    coverage_seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    audit_status: str
    handoff_packet_status: str
    handoff_status: str
    final_start_authorization_coverage_audit_seal_status: str
    coverage_audit_status: str
    authorization_status: str
    packet_status: str
    seal_source_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    seal_checks: list[str] = field(default_factory=list)
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    handoff_checks: list[str] = field(default_factory=list)
    source_seal_checks: list[str] = field(default_factory=list)
    authorization_coverage_checks: dict[str, str] = field(default_factory=dict)
    authorization_checks: list[str] = field(default_factory=list)
    coverage_seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacket:
    session_id: str
    packet_scope: str
    start_packet_status: str
    seal_status: str
    audit_status: str
    handoff_packet_status: str
    handoff_status: str
    final_start_authorization_coverage_audit_seal_status: str
    coverage_audit_status: str
    authorization_status: str
    packet_status: str
    seal_source_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    start_checks: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    handoff_checks: list[str] = field(default_factory=list)
    source_seal_checks: list[str] = field(default_factory=list)
    authorization_coverage_checks: dict[str, str] = field(default_factory=dict)
    authorization_checks: list[str] = field(default_factory=list)
    coverage_seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAudit:
    session_id: str
    audit_scope: str
    audit_status: str
    start_packet_status: str
    seal_status: str
    start_packet_source_audit_status: str
    handoff_packet_status: str
    handoff_status: str
    final_start_authorization_coverage_audit_seal_status: str
    coverage_audit_status: str
    authorization_status: str
    packet_status: str
    seal_source_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    coverage_checks: dict[str, str] = field(default_factory=dict)
    source_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    start_checks: list[str] = field(default_factory=list)
    seal_checks: list[str] = field(default_factory=list)
    handoff_checks: list[str] = field(default_factory=list)
    source_seal_checks: list[str] = field(default_factory=list)
    authorization_coverage_checks: dict[str, str] = field(default_factory=dict)
    authorization_checks: list[str] = field(default_factory=list)
    coverage_seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAuditSeal:
    session_id: str
    seal_scope: str
    seal_status: str
    audit_status: str
    start_packet_status: str
    start_packet_source_audit_status: str
    start_handoff_packet_coverage_audit_seal_status: str
    handoff_packet_status: str
    handoff_status: str
    final_start_authorization_coverage_audit_seal_status: str
    coverage_audit_status: str
    authorization_status: str
    packet_status: str
    seal_source_status: str
    packet_source_status: str
    handoff_readiness: str
    go_no_go_start_decision: str
    start_authorization: str
    source_audit_status: str
    docket_status: str
    seal_checks: list[str] = field(default_factory=list)
    coverage_checks: dict[str, str] = field(default_factory=dict)
    source_coverage_checks: dict[str, str] = field(default_factory=dict)
    missing_coverage: list[str] = field(default_factory=list)
    boundary_checks: dict[str, str] = field(default_factory=dict)
    start_checks: list[str] = field(default_factory=list)
    source_seal_checks: list[str] = field(default_factory=list)
    handoff_checks: list[str] = field(default_factory=list)
    authorization_coverage_checks: dict[str, str] = field(default_factory=dict)
    authorization_checks: list[str] = field(default_factory=list)
    coverage_seal_checks: list[str] = field(default_factory=list)
    packet_coverage_checks: dict[str, str] = field(default_factory=dict)
    clearance_checklist: list[str] = field(default_factory=list)
    sealed_first_step: str = ""
    sealed_candidate_order: list[str] = field(default_factory=list)
    operator_authorization_checklist: list[str] = field(default_factory=list)
    operator_start_checklist: list[str] = field(default_factory=list)
    verification_checklist: list[str] = field(default_factory=list)
    rollback_path: list[str] = field(default_factory=list)
    post_completion_review: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary_confirmation: list[str] = field(default_factory=list)
    applied_review_decision_delta: int = 0
    applied_candidate_status_delta: int = 0
    formal_evidence_delta: int = 0
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SourceLibraryEntry:
    entry_id: str
    title: str
    material_type: str
    local_reference: str
    tracking_status: str
    readiness_status: str
    material_id: str = ""
    topic_tags: list[str] = field(default_factory=list)
    rule_families: list[str] = field(default_factory=list)
    source_quality_notes: str = ""
    rights_notes: str = ""
    risk_tier: str = "ordinary"
    risk_notes: list[str] = field(default_factory=list)
    priority_level: str = "medium"
    next_action: str = "no_action"
    outcome_reason: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class SourcePriorityAssessment:
    assessment_id: str
    entry_id: str
    priority_level: str
    expected_value: str
    rationale: str
    target_gap_ids: list[str] = field(default_factory=list)
    target_rule_families: list[str] = field(default_factory=list)
    source_quality: str = "moderate"
    effort_level: str = "medium"
    risk_tier: str = "ordinary"
    assessed_by: str = ""
    assessed_at: str = ""


@dataclass(frozen=True)
class CurationBatchPlan:
    batch_plan_id: str
    title: str
    goal: str
    entry_ids: list[str]
    target_gap_ids: list[str] = field(default_factory=list)
    target_rule_families: list[str] = field(default_factory=list)
    risk_boundary: str = "ordinary"
    expected_output: list[str] = field(default_factory=list)
    status: str = "planned"
    review_capacity: str = ""
    completion_summary: str = ""
    recommended_next_batch: str = ""


@dataclass(frozen=True)
class EvidenceGapTarget:
    gap_target_id: str
    description: str
    rule_family: str = ""
    source_entry_ids: list[str] = field(default_factory=list)
    related_gap_ids: list[str] = field(default_factory=list)
    related_conflict_ids: list[str] = field(default_factory=list)
    priority_level: str = "medium"
    blocks_report_use: bool = False


@dataclass(frozen=True)
class SourceValueSummary:
    subject_id: str
    subject_type: str
    candidate_count: int = 0
    approved_candidate_count: int = 0
    rejected_or_blocked_count: int = 0
    conflict_count: int = 0
    gap_count: int = 0
    promoted_evidence_count: int = 0
    value_status: str = "not_started"
    recommended_next_action: str = "no_action"


@dataclass(frozen=True)
class SourceLibraryProgressReport:
    readiness_counts: dict[str, int]
    priority_counts: dict[str, int]
    risk_tier_counts: dict[str, int]
    rule_family_counts: dict[str, int]
    ready_for_extraction_count: int = 0
    high_priority_count: int = 0
    blocked_or_deferred_count: int = 0
    next_source_ids: list[str] = field(default_factory=list)
    value_status_counts: dict[str, int] = field(default_factory=dict)
    high_risk_entry_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MaterialAuditRecord:
    audit_id: str
    canonical_title: str
    material_scope: str
    primary_material_type: str
    source_identity_confidence: str
    preparation_state: str
    source_boundary: str
    alternate_titles: list[str] = field(default_factory=list)
    representations: list[str] = field(default_factory=list)
    source_library_entry_id: str = ""
    topic_tags: list[str] = field(default_factory=list)
    rule_families: list[str] = field(default_factory=list)
    risk_tier: str = "ordinary"
    risk_notes: list[str] = field(default_factory=list)
    rights_notes: str = ""
    missing_prerequisites: list[str] = field(default_factory=list)
    recommended_next_action: str = "no_action"
    outcome_reason: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class MaterialRepresentation:
    representation_id: str
    audit_id: str
    representation_type: str
    local_reference: str
    tracking_status: str
    text_quality: str = "unknown"
    locator_quality: str = "none"
    size_hint: str = ""
    modified_hint: str = ""
    contains_images: bool = False
    notes: str = ""


@dataclass(frozen=True)
class SourceAlignmentFinding:
    alignment_id: str
    audit_id: str
    match_type: str
    confidence: str
    evidence: str
    source_library_entry_id: str = ""
    source_material_id: str = ""
    registration_recommendation: str = ""
    duplicate_or_variant_notes: str = ""
    reviewer: str = ""
    reviewed_at: str = ""


@dataclass(frozen=True)
class PreparationReadinessFinding:
    readiness_id: str
    audit_id: str
    readiness_state: str
    text_preparation_status: str
    locator_confidence: str
    source_quality: str
    risk_boundary: str
    missing_prerequisites: list[str] = field(default_factory=list)
    ready_reasons: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    recommended_next_action: str = "no_action"
    assessed_by: str = ""
    assessed_at: str = ""


@dataclass(frozen=True)
class ExtractionQueueItem:
    queue_item_id: str
    audit_id: str
    queue_type: str
    priority_level: str
    priority_rationale: str
    risk_boundary: str
    recommended_action: str
    target_rule_families: list[str] = field(default_factory=list)
    target_gap_ids: list[str] = field(default_factory=list)
    pre_extraction_checks: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    status: str = "planned"
    created_at: str = ""
    updated_at: str = ""
    risk_review_findings: list[dict] = field(default_factory=list)


@dataclass(frozen=True)
class AuditProgressSummary:
    material_group_counts: dict[str, int]
    representation_counts: dict[str, int]
    source_alignment_counts: dict[str, int]
    readiness_counts: dict[str, int]
    queue_counts: dict[str, int]
    risk_tier_counts: dict[str, int]
    out_of_scope_count: int = 0
    missing_registration_count: int = 0
    extraction_ready_count: int = 0
    preparation_backlog_count: int = 0
    registration_backlog_count: int = 0
    risk_review_backlog_count: int = 0
    blocked_backlog_count: int = 0
    deferred_queue_count: int = 0
    blocked_queue_count: int = 0
    next_action_ids: list[str] = field(default_factory=list)
    source_boundary_counts: dict[str, int] = field(default_factory=dict)
    material_scope_counts: dict[str, int] = field(default_factory=dict)
    text_preparation_counts: dict[str, int] = field(default_factory=dict)
    locator_confidence_counts: dict[str, int] = field(default_factory=dict)
    source_quality_counts: dict[str, int] = field(default_factory=dict)
    risk_boundary_counts: dict[str, int] = field(default_factory=dict)
    missing_prerequisite_counts: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class MaterialQueueRefreshSummary:
    refresh_id: str
    refresh_status: str
    queue_item_count: int
    covered_queue_item_count: int
    uncovered_queue_item_ids: list[str]
    legacy_next_action_ids: list[str]
    refreshed_next_action_ids: list[str]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    covered_queue_item_ids: list[str] = field(default_factory=list)
    locally_completed_queue_item_ids: list[str] = field(default_factory=list)
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExplicitCandidateReviewOrQueueRefreshItem:
    routing_item_id: str
    routing_entry_id: str
    sensitive_reading_item_id: str
    authorization_audit_id: str
    queue_refresh_id: str
    routing_status: str
    authorization_status: str
    queue_refresh_status: str
    selected_next_material_entry: str
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class ExplicitCandidateReviewOrQueueRefreshSummary:
    routing_id: str
    routing_status: str
    routing_item_count: int
    sensitive_reading_item_ids: list[str]
    authorization_audit_ids: list[str]
    queue_refresh_ids: list[str]
    authorization_status: str
    queue_refresh_status: str
    selected_next_material_entry: str
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExternalMaterialInventoryRefreshSummary:
    refresh_id: str
    refresh_status: str
    external_entry_counts: dict[str, int]
    scanned_entry_count: int
    tracked_external_entry_ids: list[str]
    untracked_material_entry_ids: list[str]
    excluded_work_artifact_ids: list[str]
    newly_registered_representation_ids: list[str]
    new_queue_item_ids: list[str]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExternalMaterialInventoryRefreshConfirmationItem:
    confirmation_item_id: str
    refresh_id: str
    routing_id: str
    confirmation_status: str
    external_inventory_status: str
    selected_next_material_entry: str
    untracked_material_entry_count: int
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class ExternalMaterialInventoryRefreshConfirmationSummary:
    confirmation_id: str
    confirmation_status: str
    confirmation_item_count: int
    refresh_ids: list[str]
    routing_ids: list[str]
    external_inventory_status: str
    scanned_entry_count: int
    untracked_material_entry_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialExtractionLearningLoopClosureItem:
    closure_item_id: str
    closure_id: str
    source_selection_id: str
    sensitive_reading_id: str
    authorization_audit_id: str
    routing_id: str
    inventory_confirmation_id: str
    closure_status: str
    selected_next_material_entry: str
    completed_stage_count: int
    source_selection_item_count: int
    registered_source_entry_count: int
    preparation_reading_item_count: int
    candidate_intake_ready_count: int
    formal_evidence_ready_count: int = 0
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    downstream_mutation_authorized: bool = False
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialExtractionLearningLoopClosureSummary:
    closure_id: str
    closure_status: str
    closure_item_count: int
    completed_stage_count: int
    source_selection_item_count: int
    registered_source_entry_count: int
    preparation_reading_item_count: int
    candidate_intake_ready_count: int
    formal_evidence_ready_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    authorization_status: str
    downstream_mutation_authorized: bool
    next_material_entry: str
    closure_item_ids: list[str]
    source_selection_ids: list[str]
    sensitive_reading_ids: list[str]
    authorization_audit_ids: list[str]
    routing_ids: list[str]
    inventory_confirmation_ids: list[str]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialIntakeItem:
    intake_item_id: str
    intake_id: str
    authorization_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    source_label: str
    intake_status: str
    risk_boundary: str
    recommended_next_action: str
    relative_paths: list[str]
    file_count: int
    priority_text_candidate_count: int
    target_rule_families: list[str]
    selected_next_material_entry: str
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialIntakeSummary:
    intake_id: str
    intake_status: str
    intake_item_count: int
    source_file_count: int
    priority_text_candidate_count: int
    selected_for_identity_review_count: int
    authorization_status: str
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    selected_item_ids: list[str]
    cluster_ids: list[str]
    source_selection_ids: list[str]
    relative_paths: list[str]
    target_rule_family_counts: dict[str, int]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialSourceIdentityReviewItem:
    review_item_id: str
    review_id: str
    intake_item_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    source_label: str
    canonical_title_label: str
    identity_status: str
    source_library_overlap_status: str
    registration_readiness: str
    recommended_next_action: str
    risk_boundary: str
    relative_paths: list[str]
    file_count: int
    priority_text_candidate_count: int
    target_rule_families: list[str]
    matched_source_library_entry_ids: list[str] = field(default_factory=list)
    selected_next_material_entry: str = ""
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    identity_review_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialSourceIdentityReviewSummary:
    review_id: str
    review_status: str
    review_item_count: int
    identity_completed_count: int
    registration_prep_ready_count: int
    source_library_overlap_found_count: int
    source_file_count: int
    priority_text_candidate_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    review_item_ids: list[str]
    intake_item_ids: list[str]
    cluster_ids: list[str]
    source_selection_ids: list[str]
    canonical_title_labels: list[str]
    relative_paths: list[str]
    target_rule_family_counts: dict[str, int]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialRegistrationPrepItem:
    prep_item_id: str
    prep_id: str
    identity_review_item_id: str
    review_id: str
    source_library_entry_id: str
    source_material_id: str
    registration_status: str
    proposed_title: str
    proposed_material_type: str
    proposed_local_reference: str
    proposed_tracking_status: str
    proposed_readiness_status: str
    proposed_priority_level: str
    proposed_next_action: str
    risk_tier: str
    topic_tags: list[str]
    rule_families: list[str]
    source_quality_notes: str
    rights_notes: str
    source_library_overlap_policy: str
    selected_next_material_entry: str
    source_library_mutation_authorized: bool = True
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialRegistrationPrepSummary:
    prep_id: str
    prep_status: str
    prep_item_count: int
    proposed_source_file_count: int
    proposed_entry_ids: list[str]
    proposed_material_ids: list[str]
    prep_item_ids: list[str]
    identity_review_item_ids: list[str]
    local_references: list[str]
    registered_source_entry_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialSourceRegistrationItem:
    registration_item_id: str
    registration_id: str
    prep_item_id: str
    source_library_entry_id: str
    source_material_id: str
    registration_status: str
    local_reference: str
    source_library_mutation_authorized: bool = True
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    selected_next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialSourceRegistrationSummary:
    registration_id: str
    registration_status: str
    registration_item_count: int
    registered_entry_count: int
    registered_source_file_count: int
    registered_entry_ids: list[str]
    registered_material_ids: list[str]
    prep_item_ids: list[str]
    local_references: list[str]
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialPreparationBoundaryItem:
    boundary_item_id: str
    boundary_id: str
    registration_item_id: str
    source_library_entry_id: str
    source_material_id: str
    boundary_status: str
    reading_status: str
    local_reference: str
    file_count: int
    text_preparation_required: bool
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    selected_next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialPreparationBoundarySummary:
    boundary_id: str
    boundary_status: str
    boundary_item_count: int
    source_file_count: int
    text_preparation_required_count: int
    blocked_reading_count: int
    source_entry_ids: list[str]
    source_material_ids: list[str]
    registration_item_ids: list[str]
    local_references: list[str]
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialControlledTextPreparationItem:
    preparation_item_id: str
    preparation_id: str
    boundary_item_id: str
    source_library_entry_id: str
    source_material_id: str
    preparation_status: str
    probe_method: str
    local_reference: str
    page_count: int
    text_layer_nonempty_page_count: int
    extracted_text_char_count: int
    usable_text_layer: bool
    blocked_reason: str
    selected_next_material_entry: str
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialControlledTextPreparationSummary:
    preparation_id: str
    preparation_status: str
    preparation_item_count: int
    source_file_count: int
    page_count: int
    text_layer_nonempty_page_count: int
    extracted_text_char_count: int
    usable_text_layer_count: int
    blocked_item_count: int
    preparation_item_ids: list[str]
    boundary_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialOcrOrManualTranscriptionItem:
    transcription_item_id: str
    transcription_id: str
    controlled_text_preparation_item_id: str
    source_library_entry_id: str
    source_material_id: str
    transcription_status: str
    selected_path: str
    local_reference: str
    page_count: int
    pdftoppm_available: bool
    tesseract_available: bool
    ocrmypdf_available: bool
    python_ocr_package_available: bool
    prepared_text_artifact_created: bool
    blocker_reason: str
    selected_next_material_entry: str
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialOcrOrManualTranscriptionSummary:
    transcription_id: str
    transcription_status: str
    transcription_item_count: int
    source_file_count: int
    page_count: int
    pdftoppm_available_count: int
    ocr_runtime_available_count: int
    prepared_text_artifact_count: int
    blocked_item_count: int
    transcription_item_ids: list[str]
    controlled_text_preparation_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialOcrRuntimeSetupItem:
    setup_item_id: str
    setup_id: str
    ocr_or_manual_transcription_item_id: str
    source_library_entry_id: str
    source_material_id: str
    setup_status: str
    selected_path: str
    local_reference: str
    page_count: int
    probe_page_count: int
    probe_dpi: int
    pdftoppm_available: bool
    tesseract_available: bool
    tesseract_version: str
    tessdata_language_codes: list[str]
    chi_sim_available: bool
    probe_psm_values: list[str]
    prepared_text_artifact_created: bool
    blocker_reason: str
    selected_next_material_entry: str
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialOcrRuntimeSetupSummary:
    setup_id: str
    setup_status: str
    setup_item_count: int
    source_file_count: int
    page_count: int
    probe_page_count: int
    probe_dpi_values: list[int]
    pdftoppm_available_count: int
    tesseract_available_count: int
    chi_sim_available_count: int
    prepared_text_artifact_count: int
    blocked_item_count: int
    setup_item_ids: list[str]
    ocr_or_manual_transcription_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialOcrQualityRemediationItem:
    remediation_item_id: str
    remediation_id: str
    ocr_runtime_setup_item_id: str
    source_library_entry_id: str
    source_material_id: str
    remediation_status: str
    local_reference: str
    page_count: int
    probe_page_count: int
    probe_dpi: int
    vertical_tessdata_available: bool
    tessdata_language_codes: list[str]
    preprocessing_methods: list[str]
    probe_page_numbers: list[int]
    best_probe_region: str
    best_probe_han_count: int
    best_probe_ascii_count: int
    best_probe_noise_count: int
    assistive_ocr_route_available: bool
    prepared_text_artifact_created: bool
    human_correction_required: bool
    blocker_reason: str
    selected_next_material_entry: str
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialOcrQualityRemediationSummary:
    remediation_id: str
    remediation_status: str
    remediation_item_count: int
    source_file_count: int
    page_count: int
    probe_page_count: int
    probe_dpi_values: list[int]
    vertical_tessdata_available_count: int
    assistive_ocr_route_count: int
    prepared_text_artifact_count: int
    human_correction_required_count: int
    machine_unusable_closed_count: int
    blocked_item_count: int
    remediation_item_ids: list[str]
    ocr_runtime_setup_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialMachineDispositionSummary:
    disposition_id: str
    disposition_status: str
    source_file_count: int
    disposition_counts: dict[str, int]
    source_dispositions: dict[str, str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifact_count: int
    machine_unusable_closed_count: int
    learning_note_allowed_count: int
    candidate_intake_allowed_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialHumanCorrectedTranscriptionPrepItem:
    prep_item_id: str
    prep_id: str
    ocr_quality_remediation_item_id: str
    source_library_entry_id: str
    source_material_id: str
    prep_status: str
    local_reference: str
    page_count: int
    correction_packet_ready: bool
    selected_page_ranges: list[str]
    layout_profile: str
    assistive_ocr_method: str
    draft_source_policy: str
    planned_output_artifact: str
    validation_requirements: list[str]
    uncorrected_ocr_committed: bool
    prepared_text_artifact_created: bool
    human_corrected_text_available: bool
    blocker_reason: str
    selected_next_material_entry: str
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialHumanCorrectedTranscriptionPrepSummary:
    prep_id: str
    prep_status: str
    prep_item_count: int
    source_file_count: int
    page_count: int
    correction_packet_ready_count: int
    selected_page_range_count: int
    uncorrected_ocr_committed_count: int
    prepared_text_artifact_count: int
    human_corrected_text_available_count: int
    blocked_item_count: int
    prep_item_ids: list[str]
    ocr_quality_remediation_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    planned_output_artifacts: list[str]
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialHumanCorrectedTranscriptionExecutionItem:
    execution_item_id: str
    execution_id: str
    transcription_prep_item_id: str
    source_library_entry_id: str
    source_material_id: str
    execution_status: str
    local_reference: str
    prepared_text_artifact: str
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    selected_page_locators: list[str]
    uncorrected_ocr_committed: bool
    long_form_transcription_committed: bool
    prepared_text_artifact_created: bool
    human_corrected_text_available: bool
    learning_entry_ready: bool
    selected_next_material_entry: str
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialHumanCorrectedTranscriptionExecutionSummary:
    execution_id: str
    execution_status: str
    execution_item_count: int
    source_file_count: int
    prepared_text_artifact_count: int
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    learning_entry_ready_count: int
    uncorrected_ocr_committed_count: int
    long_form_transcription_committed_count: int
    execution_item_ids: list[str]
    transcription_prep_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifacts: list[str]
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedTranscriptionSelectionItem:
    selection_item_id: str
    selection_id: str
    completion_review_item_id: str
    source_library_entry_id: str
    source_material_id: str
    local_reference: str
    selection_status: str
    selected_page_ranges: list[str]
    selected_page_locators: list[str]
    selected_page_count: int
    planned_output_artifact: str
    learning_purpose: str
    risk_boundary: str
    candidate_intake_allowed: bool
    correction_prep_allowed: bool
    downstream_mutation_authorized: bool
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    selected_next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedTranscriptionSelectionSummary:
    selection_id: str
    selection_status: str
    selection_item_count: int
    selected_page_range_count: int
    selected_page_locator_count: int
    selected_page_count: int
    correction_prep_allowed_count: int
    candidate_intake_allowed_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    selection_item_ids: list[str]
    completion_review_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    planned_output_artifacts: list[str]
    risk_boundary_counts: dict[str, int]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedTranscriptionPrepItem:
    prep_item_id: str
    prep_id: str
    selection_item_id: str
    source_library_entry_id: str
    source_material_id: str
    local_reference: str
    prep_status: str
    selected_page_ranges: list[str]
    selected_page_locators: list[str]
    selected_page_count: int
    correction_packet_ready: bool
    planned_output_artifact: str
    validation_requirements: list[str]
    uncorrected_ocr_committed: bool
    prepared_text_artifact_created: bool
    human_corrected_text_available: bool
    candidate_intake_allowed: bool
    downstream_mutation_authorized: bool
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    selected_next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedTranscriptionPrepSummary:
    prep_id: str
    prep_status: str
    prep_item_count: int
    selected_page_range_count: int
    selected_page_locator_count: int
    selected_page_count: int
    correction_packet_ready_count: int
    uncorrected_ocr_committed_count: int
    prepared_text_artifact_count: int
    human_corrected_text_available_count: int
    candidate_intake_allowed_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    prep_item_ids: list[str]
    selection_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    planned_output_artifacts: list[str]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedTranscriptionExecutionItem:
    execution_item_id: str
    execution_id: str
    prep_item_id: str
    source_library_entry_id: str
    source_material_id: str
    execution_status: str
    local_reference: str
    prepared_text_artifact: str
    selected_page_ranges: list[str]
    selected_page_locators: list[str]
    selected_page_count: int
    expanded_window_count: int
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    uncorrected_ocr_committed: bool
    long_form_transcription_committed: bool
    prepared_text_artifact_created: bool
    human_corrected_text_available: bool
    learning_entry_ready: bool
    candidate_intake_allowed: bool
    selected_next_material_entry: str
    downstream_mutation_authorized: bool = False
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedTranscriptionExecutionSummary:
    execution_id: str
    execution_status: str
    execution_item_count: int
    source_file_count: int
    prepared_text_artifact_count: int
    selected_page_range_count: int
    selected_page_locator_count: int
    selected_page_count: int
    expanded_window_count: int
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    learning_entry_ready_count: int
    human_corrected_text_available_count: int
    uncorrected_ocr_committed_count: int
    long_form_transcription_committed_count: int
    candidate_intake_allowed_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    execution_item_ids: list[str]
    prep_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifacts: list[str]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialCorrectedPilotLearningEntryEvaluationItem:
    evaluation_item_id: str
    evaluation_id: str
    transcription_execution_item_id: str
    source_library_entry_id: str
    source_material_id: str
    prepared_text_artifact: str
    local_reference: str
    evaluation_status: str
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    learning_note_allowed: bool
    candidate_intake_allowed: bool
    duplicate_overlap_review_required: bool
    risk_boundary_review_required: bool
    downstream_mutation_authorized: bool
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    selected_next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialCorrectedPilotLearningEntryEvaluationSummary:
    evaluation_id: str
    evaluation_status: str
    evaluation_item_count: int
    prepared_text_artifact_count: int
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    learning_note_allowed_count: int
    candidate_intake_allowed_count: int
    duplicate_overlap_review_required_count: int
    risk_boundary_review_required_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    evaluation_item_ids: list[str]
    transcription_execution_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifacts: list[str]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialMachineDispositionLearningGateSummary:
    gate_id: str
    gate_status: str
    machine_text_usable_count: int
    machine_unusable_closed_count: int
    learning_entry_source_count: int
    learning_entry_machine_usable_count: int
    closed_source_learning_entry_count: int
    missing_learning_entry_count: int
    candidate_intake_allowed_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    machine_text_usable_source_entry_ids: list[str]
    machine_unusable_closed_source_entry_ids: list[str]
    learning_entry_source_entry_ids: list[str]
    excluded_closed_source_entry_ids: list[str]
    missing_learning_entry_source_entry_ids: list[str]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialCorrectedPilotLearningNotePrepItem:
    prep_item_id: str
    prep_id: str
    evaluation_item_id: str
    source_library_entry_id: str
    source_material_id: str
    prepared_text_artifact: str
    local_reference: str
    prep_status: str
    proposed_note_id: str
    proposed_learning_point_count: int
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    target_rule_families: list[str]
    learning_note_draft_allowed: bool
    candidate_intake_allowed: bool
    overlap_review_required: bool
    risk_boundary_review_required: bool
    downstream_mutation_authorized: bool
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    selected_next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialCorrectedPilotLearningNotePrepSummary:
    prep_id: str
    prep_status: str
    prep_item_count: int
    proposed_note_count: int
    proposed_learning_point_count: int
    prepared_text_artifact_count: int
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    learning_note_draft_allowed_count: int
    candidate_intake_allowed_count: int
    overlap_review_required_count: int
    risk_boundary_review_required_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    prep_item_ids: list[str]
    evaluation_item_ids: list[str]
    proposed_note_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifacts: list[str]
    target_rule_family_counts: dict[str, int]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialCorrectedPilotLearningNoteDraftItem:
    draft_item_id: str
    draft_id: str
    prep_item_id: str
    note_id: str
    learning_point_id: str
    source_library_entry_id: str
    source_material_id: str
    prepared_text_artifact: str
    local_reference: str
    draft_status: str
    target_rule_family: str
    risk_tier: str
    locator_summary: str
    learning_summary: str
    limitations: list[str]
    candidate_intake_allowed: bool
    completion_review_allowed: bool
    downstream_mutation_authorized: bool
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    selected_next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialCorrectedPilotLearningNoteDraftSummary:
    draft_id: str
    draft_status: str
    draft_item_count: int
    learning_note_count: int
    learning_point_count: int
    candidate_intake_allowed_count: int
    completion_review_allowed_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    draft_item_ids: list[str]
    prep_item_ids: list[str]
    note_ids: list[str]
    learning_point_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifacts: list[str]
    target_rule_family_counts: dict[str, int]
    risk_tier_counts: dict[str, int]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialCorrectedPilotLearningCompletionReviewItem:
    completion_item_id: str
    completion_id: str
    draft_item_id: str
    note_id: str
    learning_point_id: str
    source_library_entry_id: str
    source_material_id: str
    prepared_text_artifact: str
    local_reference: str
    completion_status: str
    learning_note_closed: bool
    candidate_intake_allowed: bool
    additional_correction_required: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialCorrectedPilotLearningCompletionReviewSummary:
    completion_id: str
    completion_status: str
    completion_item_count: int
    learning_note_closed_count: int
    candidate_intake_allowed_count: int
    additional_correction_required_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    completion_item_ids: list[str]
    draft_item_ids: list[str]
    note_ids: list[str]
    learning_point_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifacts: list[str]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedLearningEntryEvaluationItem:
    evaluation_item_id: str
    evaluation_id: str
    expanded_transcription_execution_item_id: str
    source_library_entry_id: str
    source_material_id: str
    prepared_text_artifact: str
    local_reference: str
    evaluation_status: str
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    learning_note_allowed: bool
    candidate_intake_allowed: bool
    duplicate_overlap_review_required: bool
    risk_boundary_review_required: bool
    downstream_mutation_authorized: bool
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    selected_next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedLearningEntryEvaluationSummary:
    evaluation_id: str
    evaluation_status: str
    evaluation_item_count: int
    prepared_text_artifact_count: int
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    learning_note_allowed_count: int
    candidate_intake_allowed_count: int
    duplicate_overlap_review_required_count: int
    risk_boundary_review_required_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    evaluation_item_ids: list[str]
    expanded_transcription_execution_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifacts: list[str]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedLearningNotePrepItem:
    prep_item_id: str
    prep_id: str
    evaluation_item_id: str
    source_library_entry_id: str
    source_material_id: str
    prepared_text_artifact: str
    local_reference: str
    prep_status: str
    proposed_note_id: str
    proposed_learning_point_count: int
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    target_rule_families: list[str]
    learning_note_draft_allowed: bool
    candidate_intake_allowed: bool
    overlap_review_required: bool
    risk_boundary_review_required: bool
    downstream_mutation_authorized: bool
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    selected_next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedLearningNotePrepSummary:
    prep_id: str
    prep_status: str
    prep_item_count: int
    proposed_note_count: int
    proposed_learning_point_count: int
    prepared_text_artifact_count: int
    corrected_excerpt_count: int
    corrected_character_count: int
    page_locator_count: int
    learning_note_draft_allowed_count: int
    candidate_intake_allowed_count: int
    overlap_review_required_count: int
    risk_boundary_review_required_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    prep_item_ids: list[str]
    evaluation_item_ids: list[str]
    proposed_note_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifacts: list[str]
    target_rule_family_counts: dict[str, int]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedLearningNoteDraftItem:
    draft_item_id: str
    draft_id: str
    prep_item_id: str
    note_id: str
    learning_point_id: str
    source_library_entry_id: str
    source_material_id: str
    prepared_text_artifact: str
    local_reference: str
    draft_status: str
    target_rule_family: str
    risk_tier: str
    locator_summary: str
    learning_summary: str
    limitations: list[str]
    candidate_intake_allowed: bool
    completion_review_allowed: bool
    downstream_mutation_authorized: bool
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    selected_next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedLearningNoteDraftSummary:
    draft_id: str
    draft_status: str
    draft_item_count: int
    learning_note_count: int
    learning_point_count: int
    candidate_intake_allowed_count: int
    completion_review_allowed_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    draft_item_ids: list[str]
    prep_item_ids: list[str]
    note_ids: list[str]
    learning_point_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifacts: list[str]
    target_rule_family_counts: dict[str, int]
    risk_tier_counts: dict[str, int]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedLearningCompletionReviewItem:
    completion_item_id: str
    completion_id: str
    draft_item_id: str
    note_id: str
    learning_point_id: str
    source_library_entry_id: str
    source_material_id: str
    prepared_text_artifact: str
    local_reference: str
    completion_status: str
    learning_note_closed: bool
    candidate_intake_allowed: bool
    additional_correction_required: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class NewMaterialExpandedCorrectedLearningCompletionReviewSummary:
    completion_id: str
    completion_status: str
    completion_item_count: int
    learning_note_closed_count: int
    candidate_intake_allowed_count: int
    additional_correction_required_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_material_entry: str
    completion_item_ids: list[str]
    draft_item_ids: list[str]
    note_ids: list[str]
    learning_point_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    prepared_text_artifacts: list[str]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextMaterialTriageGroup:
    group_id: str
    source_root: str
    group_label: str
    triage_status: str
    risk_boundary: str
    file_count: int
    priority_text_candidate_count: int
    extension_counts: dict[str, int]
    recommended_next_action: str
    target_rule_families: list[str] = field(default_factory=list)
    filename_markers: list[str] = field(default_factory=list)
    representative_paths: list[str] = field(default_factory=list)
    next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextMaterialTriageSummary:
    triage_id: str
    triage_status: str
    source_root: str
    total_file_count: int
    priority_text_candidate_count: int
    triage_group_count: int
    triage_status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    extension_counts: dict[str, int]
    next_group_ids: list[str]
    risk_review_group_ids: list[str]
    deferred_group_ids: list[str]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextSourceSelectionItem:
    selection_id: str
    triage_group_id: str
    source_root: str
    relative_path: str
    title_label: str
    selection_status: str
    risk_boundary: str
    recommended_next_action: str
    source_library_entry_id: str
    source_material_id: str
    target_rule_families: list[str] = field(default_factory=list)
    existing_learning_reference_ids: list[str] = field(default_factory=list)
    existing_candidate_ids: list[str] = field(default_factory=list)
    source_batch_status: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextSourceSelectionSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    source_selection_item_count: int
    selected_for_individual_review_count: int
    existing_batch_covered_count: int
    variant_review_required_count: int
    sensitive_boundary_deferred_count: int
    status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    selected_item_ids: list[str]
    deferred_item_ids: list[str]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextSourceClusterSelectionItem:
    cluster_id: str
    triage_group_id: str
    source_root: str
    cluster_label: str
    cluster_status: str
    risk_boundary: str
    file_count: int
    priority_text_candidate_count: int
    extension_counts: dict[str, int]
    recommended_next_action: str
    target_rule_families: list[str] = field(default_factory=list)
    filename_markers: list[str] = field(default_factory=list)
    representative_paths: list[str] = field(default_factory=list)
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextSourceClusterSelectionSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    cluster_count: int
    clustered_file_count: int
    clustered_priority_text_candidate_count: int
    selected_cluster_count: int
    deferred_cluster_count: int
    cluster_status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    extension_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    selected_cluster_ids: list[str]
    deferred_cluster_ids: list[str]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleSourceSelectionItem:
    selection_id: str
    triage_group_id: str
    cluster_id: str
    source_root: str
    selection_label: str
    selection_status: str
    risk_boundary: str
    recommended_next_action: str
    file_count: int
    priority_text_candidate_count: int
    target_rule_families: list[str] = field(default_factory=list)
    next_material_entry: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleSourceSelectionSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    selection_item_count: int
    selected_for_identity_review_count: int
    deferred_cluster_count: int
    risk_review_cluster_count: int
    status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    selected_cluster_ids: list[str]
    deferred_cluster_ids: list[str]
    risk_review_cluster_ids: list[str]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleIdentityReviewItem:
    review_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    canonical_cluster_label: str
    identity_status: str
    source_library_overlap_status: str
    registration_readiness: str
    recommended_next_action: str
    next_review_target: str
    risk_boundary: str
    file_count: int
    priority_text_candidate_count: int
    matched_source_library_entry_ids: list[str] = field(default_factory=list)
    target_rule_families: list[str] = field(default_factory=list)
    identity_review_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleIdentityReviewSummary:
    review_id: str
    review_status: str
    triage_group_id: str
    source_root: str
    identity_review_item_count: int
    cluster_source_selection_required_count: int
    registration_prep_ready_count: int
    source_library_overlap_found_count: int
    identity_status_counts: dict[str, int]
    source_library_overlap_counts: dict[str, int]
    registration_readiness_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    cluster_source_selection_required_ids: list[str]
    registration_prep_ready_ids: list[str]
    source_library_overlap_ids: list[str]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleClusterSourceSelectionItem:
    selection_id: str
    identity_review_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    title_label: str
    selection_status: str
    risk_boundary: str
    recommended_next_action: str
    relative_paths: list[str]
    file_count: int
    priority_text_candidate_count: int
    target_rule_families: list[str]
    source_library_entry_id: str
    source_material_id: str
    audit_id: str
    queue_item_id: str
    candidate_id: str
    evidence_id: str
    priority_score: int = 0
    identity_review_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleClusterSourceSelectionSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    source_selection_item_count: int
    source_file_count: int
    priority_text_candidate_count: int
    selected_for_registration_count: int
    registered_source_entry_count: int
    candidate_extract_count: int
    formal_evidence_count: int
    selected_item_ids: list[str]
    registered_entry_ids: list[str]
    registered_material_ids: list[str]
    audit_ids: list[str]
    queue_item_ids: list[str]
    candidate_ids: list[str]
    evidence_ids: list[str]
    status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleFollowupSelectionItem:
    selection_id: str
    prior_selection_id: str
    cluster_id: str
    source_selection_id: str
    triage_group_id: str
    source_root: str
    title_label: str
    selection_status: str
    risk_boundary: str
    recommended_next_action: str
    relative_paths: list[str]
    file_count: int
    priority_text_candidate_count: int
    target_rule_families: list[str]
    source_library_entry_id: str
    source_material_id: str
    audit_id: str
    queue_item_id: str
    candidate_id: str
    evidence_id: str
    priority_score: int = 0
    selection_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleFollowupSelectionSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    source_selection_item_count: int
    source_file_count: int
    priority_text_candidate_count: int
    selected_for_registration_count: int
    registered_source_entry_count: int
    candidate_extract_count: int
    formal_evidence_count: int
    selected_item_ids: list[str]
    registered_entry_ids: list[str]
    registered_material_ids: list[str]
    audit_ids: list[str]
    queue_item_ids: list[str]
    candidate_ids: list[str]
    evidence_ids: list[str]
    status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleGatedClusterReviewPrepItem:
    prep_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    prep_label: str
    prep_status: str
    risk_boundary: str
    recommended_next_action: str
    file_count: int
    priority_text_candidate_count: int
    target_rule_families: list[str] = field(default_factory=list)
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    boundary_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleGatedClusterReviewPrepSummary:
    prep_id: str
    prep_status: str
    triage_group_id: str
    source_root: str
    prep_item_count: int
    selected_for_source_selection_count: int
    risk_review_required_count: int
    deferred_after_prep_count: int
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    prepared_source_selection_ids: list[str]
    risk_review_item_ids: list[str]
    deferred_item_ids: list[str]
    status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleGatedOrdinarySourceSelectionItem:
    selection_id: str
    prep_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    title_label: str
    selection_status: str
    risk_boundary: str
    recommended_next_action: str
    relative_paths: list[str]
    file_count: int
    priority_text_candidate_count: int
    source_library_entry_id: str
    source_material_id: str
    audit_id: str
    queue_item_id: str
    candidate_id: str
    evidence_id: str
    target_rule_families: list[str] = field(default_factory=list)
    source_library_mutation_authorized: bool = True
    downstream_mutation_authorized: bool = True
    priority_score: int = 0
    selection_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleGatedOrdinarySourceSelectionSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    source_selection_item_count: int
    source_file_count: int
    priority_text_candidate_count: int
    selected_for_registration_count: int
    registered_source_entry_count: int
    candidate_extract_count: int
    formal_evidence_count: int
    selected_item_ids: list[str]
    prep_item_ids: list[str]
    sensitive_risk_review_item_ids: list[str]
    registered_entry_ids: list[str]
    registered_material_ids: list[str]
    audit_ids: list[str]
    queue_item_ids: list[str]
    candidate_ids: list[str]
    evidence_ids: list[str]
    status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleGatedOrdinaryFollowupSelectionItem:
    selection_id: str
    prior_selection_id: str
    prep_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    title_label: str
    selection_status: str
    risk_boundary: str
    recommended_next_action: str
    relative_paths: list[str]
    file_count: int
    priority_text_candidate_count: int
    source_library_entry_id: str
    source_material_id: str
    audit_id: str
    queue_item_id: str
    candidate_id: str
    evidence_id: str
    target_rule_families: list[str] = field(default_factory=list)
    source_library_mutation_authorized: bool = True
    downstream_mutation_authorized: bool = True
    priority_score: int = 0
    selection_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleGatedOrdinaryFollowupSelectionSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    source_selection_item_count: int
    source_file_count: int
    priority_text_candidate_count: int
    selected_for_registration_count: int
    registered_source_entry_count: int
    candidate_extract_count: int
    formal_evidence_count: int
    selected_item_ids: list[str]
    prior_selection_item_ids: list[str]
    prep_item_ids: list[str]
    sensitive_risk_review_item_ids: list[str]
    registered_entry_ids: list[str]
    registered_material_ids: list[str]
    audit_ids: list[str]
    queue_item_ids: list[str]
    candidate_ids: list[str]
    evidence_ids: list[str]
    status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleGatedOrdinaryFinalSelectionItem:
    selection_id: str
    prior_selection_id: str
    prep_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    title_label: str
    selection_status: str
    risk_boundary: str
    recommended_next_action: str
    relative_paths: list[str]
    file_count: int
    priority_text_candidate_count: int
    source_library_entry_id: str
    source_material_id: str
    audit_id: str
    queue_item_id: str
    candidate_id: str
    evidence_id: str
    target_rule_families: list[str] = field(default_factory=list)
    source_library_mutation_authorized: bool = True
    downstream_mutation_authorized: bool = True
    priority_score: int = 0
    selection_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleGatedOrdinaryFinalSelectionSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    source_selection_item_count: int
    source_file_count: int
    priority_text_candidate_count: int
    selected_for_registration_count: int
    registered_source_entry_count: int
    candidate_extract_count: int
    formal_evidence_count: int
    selected_item_ids: list[str]
    prior_selection_item_ids: list[str]
    prep_item_ids: list[str]
    sensitive_risk_review_item_ids: list[str]
    registered_entry_ids: list[str]
    registered_material_ids: list[str]
    audit_ids: list[str]
    queue_item_ids: list[str]
    candidate_ids: list[str]
    evidence_ids: list[str]
    status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleSensitiveRiskReviewPrepItem:
    prep_item_id: str
    prep_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    title_label: str
    prep_status: str
    risk_boundary: str
    recommended_next_action: str
    relative_paths: list[str]
    file_count: int
    priority_text_candidate_count: int
    target_rule_families: list[str] = field(default_factory=list)
    risk_review_topics: list[str] = field(default_factory=list)
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    priority_score: int = 0
    boundary_decision: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleSensitiveRiskReviewPrepSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    prep_item_count: int
    source_file_count: int
    priority_text_candidate_count: int
    source_level_risk_review_count: int
    blocked_count: int
    deferred_count: int
    registered_source_entry_count: int
    candidate_extract_count: int
    formal_evidence_count: int
    prep_item_ids: list[str]
    source_level_risk_review_item_ids: list[str]
    blocked_item_ids: list[str]
    deferred_item_ids: list[str]
    relative_paths: list[str]
    status_counts: dict[str, int]
    action_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleSensitiveSourceLevelRiskReviewItem:
    review_item_id: str
    prep_item_id: str
    prep_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    title_label: str
    review_status: str
    risk_boundary: str
    recommended_next_action: str
    relative_paths: list[str]
    file_count: int
    priority_text_candidate_count: int
    registration_prep_allowed: bool = False
    target_rule_families: list[str] = field(default_factory=list)
    risk_review_topics: list[str] = field(default_factory=list)
    risk_findings: list[str] = field(default_factory=list)
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    priority_score: int = 0
    boundary_decision: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleSensitiveSourceLevelRiskReviewSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    review_item_count: int
    source_file_count: int
    priority_text_candidate_count: int
    cleared_for_registration_prep_count: int
    registered_source_entry_count: int
    candidate_extract_count: int
    formal_evidence_count: int
    review_item_ids: list[str]
    cleared_for_registration_prep_item_ids: list[str]
    prep_item_ids: list[str]
    blocked_prep_item_ids: list[str]
    deferred_prep_item_ids: list[str]
    relative_paths: list[str]
    status_counts: dict[str, int]
    action_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleSensitiveRegistrationPrepItem:
    prep_item_id: str
    source_level_review_id: str
    prep_review_item_id: str
    prep_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    registration_status: str
    proposed_entry_id: str
    proposed_material_id: str
    proposed_title: str
    proposed_material_type: str
    proposed_local_references: list[str]
    proposed_tracking_status: str
    proposed_readiness_status: str
    proposed_priority_level: str
    proposed_next_action: str
    risk_tier: str
    topic_tags: list[str] = field(default_factory=list)
    rule_families: list[str] = field(default_factory=list)
    source_quality_notes: str = ""
    rights_notes: str = ""
    risk_notes: list[str] = field(default_factory=list)
    source_library_overlap_policy: str = ""
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleSensitiveRegistrationPrepSummary:
    prep_id: str
    prep_status: str
    triage_group_id: str
    source_root: str
    registration_prep_item_count: int
    proposed_source_file_count: int
    registered_source_entry_count: int
    candidate_extract_count: int
    formal_evidence_count: int
    registration_status_counts: dict[str, int]
    proposed_readiness_counts: dict[str, int]
    proposed_next_action_counts: dict[str, int]
    risk_tier_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    proposed_entry_ids: list[str]
    proposed_material_ids: list[str]
    registration_prep_item_ids: list[str]
    source_level_review_item_ids: list[str]
    blocked_prep_item_ids: list[str]
    deferred_prep_item_ids: list[str]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleSensitiveSourceRegistrationItem:
    registration_item_id: str
    registration_prep_item_id: str
    registered_entry_id: str
    registered_material_id: str
    registration_status: str
    registered_local_references: list[str]
    source_library_mutation_authorized: bool = True
    downstream_mutation_authorized: bool = False
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleSensitiveSourceRegistrationSummary:
    registration_id: str
    registration_status: str
    triage_group_id: str
    source_root: str
    registered_entry_count: int
    registered_source_file_count: int
    candidate_extract_count: int
    formal_evidence_count: int
    registered_entry_ids: list[str]
    registered_material_ids: list[str]
    registration_prep_item_ids: list[str]
    blocked_prep_item_ids: list[str]
    deferred_prep_item_ids: list[str]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleSensitivePreparationBoundaryItem:
    boundary_item_id: str
    source_registration_item_id: str
    source_library_entry_id: str
    source_material_id: str
    boundary_status: str
    risk_boundary: str
    recommended_next_action: str
    local_references: list[str]
    file_count: int
    preparation_allowed: bool = False
    reading_allowed: bool = False
    downstream_mutation_authorized: bool = False
    target_rule_families: list[str] = field(default_factory=list)
    preparation_topics: list[str] = field(default_factory=list)
    risk_controls: list[str] = field(default_factory=list)
    boundary_decision: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleSensitivePreparationBoundarySummary:
    boundary_id: str
    boundary_status: str
    triage_group_id: str
    source_root: str
    boundary_item_count: int
    source_file_count: int
    preparation_allowed_count: int
    reading_allowed_count: int
    candidate_extract_count: int
    formal_evidence_count: int
    boundary_item_ids: list[str]
    source_registration_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    status_counts: dict[str, int]
    action_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextNextCycleSensitivePreparationReadingItem:
    reading_item_id: str
    boundary_item_id: str
    source_library_entry_id: str
    source_material_id: str
    reading_status: str
    risk_boundary: str
    local_references: list[str]
    safe_reading_note_count: int
    candidate_intake_ready: bool = False
    formal_evidence_ready: bool = False
    downstream_mutation_authorized: bool = False
    target_rule_families: list[str] = field(default_factory=list)
    safe_reading_notes: list[str] = field(default_factory=list)
    sensitive_controls: list[str] = field(default_factory=list)
    reading_decision: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextNextCycleSensitivePreparationReadingSummary:
    reading_id: str
    reading_status: str
    triage_group_id: str
    source_root: str
    reading_item_count: int
    source_file_count: int
    safe_reading_note_count: int
    candidate_intake_ready_count: int
    formal_evidence_ready_count: int
    candidate_extract_count: int
    review_decision_count: int
    promotion_batch_count: int
    formal_evidence_count: int
    reading_item_ids: list[str]
    boundary_item_ids: list[str]
    source_entry_ids: list[str]
    source_material_ids: list[str]
    local_references: list[str]
    status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextClusterSourceSelectionItem:
    selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    title_label: str
    selection_status: str
    risk_boundary: str
    recommended_next_action: str
    relative_paths: list[str]
    file_count: int
    priority_text_candidate_count: int
    extension_counts: dict[str, int]
    target_rule_families: list[str] = field(default_factory=list)
    priority_score: int = 0
    size_mb_total: float = 0.0
    identity_review_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextClusterSourceSelectionSummary:
    selection_id: str
    selection_status: str
    triage_group_id: str
    source_root: str
    selected_cluster_ids: list[str]
    source_selection_item_count: int
    source_file_count: int
    priority_text_candidate_count: int
    selected_for_identity_review_count: int
    variant_identity_review_count: int
    deferred_after_cluster_selection_count: int
    status_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    extension_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    selected_item_ids: list[str]
    variant_review_item_ids: list[str]
    deferred_item_ids: list[str]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextSourceIdentityReviewItem:
    review_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    canonical_title_label: str
    identity_status: str
    source_library_overlap_status: str
    registration_readiness: str
    recommended_next_action: str
    next_review_target: str
    risk_boundary: str = "ordinary"
    matched_source_library_entry_ids: list[str] = field(default_factory=list)
    target_rule_families: list[str] = field(default_factory=list)
    identity_review_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextSourceIdentityReviewSummary:
    review_id: str
    review_status: str
    triage_group_id: str
    source_root: str
    identity_review_item_count: int
    existing_batch_overlap_count: int
    registration_prep_ready_count: int
    variant_choice_required_count: int
    deferred_large_source_count: int
    identity_status_counts: dict[str, int]
    source_library_overlap_counts: dict[str, int]
    registration_readiness_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    existing_batch_overlap_ids: list[str]
    registration_prep_item_ids: list[str]
    variant_choice_item_ids: list[str]
    deferred_item_ids: list[str]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextSourceRegistrationPrepItem:
    prep_id: str
    identity_review_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    registration_status: str
    proposed_entry_id: str
    proposed_material_id: str
    proposed_title: str
    proposed_material_type: str
    proposed_local_references: list[str]
    proposed_tracking_status: str
    proposed_readiness_status: str
    proposed_priority_level: str
    proposed_next_action: str
    risk_tier: str
    topic_tags: list[str] = field(default_factory=list)
    rule_families: list[str] = field(default_factory=list)
    source_quality_notes: str = ""
    rights_notes: str = ""
    risk_notes: list[str] = field(default_factory=list)
    source_library_overlap_policy: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class RawTextSourceRegistrationPrepSummary:
    prep_id: str
    prep_status: str
    triage_group_id: str
    source_root: str
    registration_prep_item_count: int
    proposed_source_file_count: int
    skipped_existing_batch_overlap_count: int
    blocked_variant_choice_count: int
    deferred_large_source_count: int
    registration_status_counts: dict[str, int]
    proposed_readiness_counts: dict[str, int]
    proposed_next_action_counts: dict[str, int]
    risk_tier_counts: dict[str, int]
    target_rule_family_counts: dict[str, int]
    proposed_entry_ids: list[str]
    proposed_material_ids: list[str]
    registration_prep_item_ids: list[str]
    skipped_existing_batch_overlap_ids: list[str]
    blocked_variant_choice_ids: list[str]
    deferred_item_ids: list[str]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawTextSourceRegistrationSummary:
    registration_id: str
    registration_status: str
    triage_group_id: str
    source_root: str
    registered_entry_count: int
    registered_source_file_count: int
    skipped_existing_batch_overlap_count: int
    blocked_variant_choice_count: int
    deferred_large_source_count: int
    registered_entry_ids: list[str]
    registered_material_ids: list[str]
    skipped_existing_batch_overlap_ids: list[str]
    blocked_variant_choice_ids: list[str]
    deferred_item_ids: list[str]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BaziGeneralVariantDeferredReviewItem:
    item_id: str
    identity_review_id: str
    source_selection_id: str
    cluster_id: str
    triage_group_id: str
    source_root: str
    review_kind: str
    review_status: str
    decision: str
    canonical_choice_status: str
    local_references: list[str]
    candidate_rule_families: list[str]
    selected_local_reference: str = ""
    selected_source_library_entry_id: str = ""
    source_library_mutation_authorized: bool = False
    downstream_mutation_authorized: bool = False
    review_note: str = ""
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class BaziGeneralVariantDeferredReviewSummary:
    review_id: str
    review_status: str
    triage_group_id: str
    source_root: str
    review_item_count: int
    variant_review_item_count: int
    deferred_review_item_count: int
    selected_canonical_variant_count: int
    source_library_registration_authorized_count: int
    variant_review_item_ids: list[str]
    deferred_review_item_ids: list[str]
    selected_canonical_variant_ids: list[str]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BaziGeneralSourcePreparationReadingSummary:
    reading_id: str
    reading_status: str
    triage_group_id: str
    source_root: str
    source_entry_count: int
    source_file_count: int
    material_audit_record_count: int
    extraction_task_count: int
    learning_note_count: int
    candidate_extract_count: int
    review_decision_count: int
    promotion_batch_count: int
    formal_source_count: int
    formal_evidence_count: int
    source_entry_ids: list[str]
    source_material_ids: list[str]
    candidate_ids: list[str]
    evidence_ids: list[str]
    source_library_mutation_authorized: bool
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExtractionWorkPackage:
    package_id: str
    package_label: str
    source_queue_snapshot_ids: list[str]
    selected_task_ids: list[str]
    backlog_record_ids: list[str]
    status: str
    created_at: str = ""
    updated_at: str = ""
    notes: str = ""


@dataclass(frozen=True)
class ExtractionTask:
    task_id: str
    package_id: str
    queue_item_id: str
    audit_id: str
    priority_level: str
    priority_rationale: str
    risk_boundary: str
    locator_requirement: str
    source_quality_note: str
    rights_note: str
    source_library_entry_id: str = ""
    intended_source_material_id: str = ""
    target_rule_families: list[str] = field(default_factory=list)
    target_gap_ids: list[str] = field(default_factory=list)
    pre_extraction_checks: list[str] = field(default_factory=list)
    overlap_warnings: list[str] = field(default_factory=list)
    recommended_action: str = "extract_candidates"
    status: str = "planned"
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class CandidateDraftSlot:
    draft_slot_id: str
    task_id: str
    intended_candidate_label: str
    target_rule_family: str
    locator_requirement: str
    risk_boundary: str
    target_gap_id: str = ""
    expected_review_notes: list[str] = field(default_factory=list)
    safety_requirements: list[str] = field(default_factory=list)
    status: str = "planned"


@dataclass(frozen=True)
class PrerequisiteBacklogRecord:
    backlog_id: str
    package_id: str
    queue_item_id: str
    audit_id: str
    backlog_type: str
    durable_reason: str
    recommended_action: str
    risk_boundary: str
    missing_prerequisites: list[str] = field(default_factory=list)
    status: str = "planned"
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class PackageProgressSummary:
    package_counts: dict[str, int]
    task_counts: dict[str, int]
    draft_slot_counts: dict[str, int]
    backlog_counts: dict[str, int]
    risk_boundary_counts: dict[str, int]
    overlap_warning_count: int = 0
    extraction_task_count: int = 0
    candidate_draft_slot_count: int = 0
    blocked_or_deferred_count: int = 0
    next_manual_action_ids: list[str] = field(default_factory=list)
    priority_counts: dict[str, int] = field(default_factory=dict)
    selected_source_queue_ids: list[str] = field(default_factory=list)
    draft_slot_rule_family_counts: dict[str, int] = field(default_factory=dict)
    draft_slot_readiness_counts: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningReferenceNote:
    note_id: str
    task_id: str
    package_id: str
    queue_item_id: str
    audit_id: str
    source_library_entry_id: str
    source_material_id: str
    source_title: str
    locator_requirement: str
    risk_boundary: str
    rights_note: str
    source_quality_note: str
    target_rule_families: list[str] = field(default_factory=list)
    learning_points: list[str] = field(default_factory=list)
    overlap_candidate_ids: list[str] = field(default_factory=list)
    status: str = "draft"
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class LearningPoint:
    learning_point_id: str
    note_id: str
    point_label: str
    source_locator: str
    summary: str
    proposed_rule_family: str
    risk_tier: str
    candidate_readiness: str
    limitations: list[str] = field(default_factory=list)
    candidate_decision_id: str = ""


@dataclass(frozen=True)
class CandidateIntakeDecision:
    decision_id: str
    learning_point_id: str
    decision: str
    source_material_id: str
    rationale: str
    candidate_id: str = ""
    overlap_candidate_ids: list[str] = field(default_factory=list)
    status: str = "planned"
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class PrerequisiteActionNote:
    action_note_id: str
    backlog_id: str
    package_id: str
    queue_item_id: str
    audit_id: str
    action_type: str
    durable_reason: str
    recommended_action: str
    risk_boundary: str
    missing_prerequisites: list[str] = field(default_factory=list)
    status: str = "planned"
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class LearningReferenceProgressSummary:
    note_counts: dict[str, int]
    learning_point_counts: dict[str, int]
    decision_counts: dict[str, int]
    prerequisite_action_counts: dict[str, int]
    risk_tier_counts: dict[str, int]
    overlap_warning_count: int = 0
    candidate_ready_count: int = 0
    candidate_decision_count: int = 0
    formal_evidence_delta: int = 0
    next_action_ids: list[str] = field(default_factory=list)
    note_rule_family_counts: dict[str, int] = field(default_factory=dict)
    selected_task_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class LearningReferenceAuthorizationAudit:
    audit_id: str
    authorization_status: str
    downstream_mutation_authorized: bool
    note_counts: dict[str, int]
    decision_counts: dict[str, int]
    candidate_status_counts: dict[str, int]
    review_decision_counts: dict[str, int]
    promotion_review_status_counts: dict[str, int]
    formal_evidence_unit_count: int
    formal_evidence_delta: int
    leakage_counts: dict[str, int]
    clearance_checks: dict[str, str]
    next_action_ids: list[str] = field(default_factory=list)
    next_downstream_entry: str = ""
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DownstreamAuthorizationReceipt:
    receipt_id: str
    authorization_audit_id: str
    authorization_status: str
    authorization_scope: str
    selected_next_downstream_entry: str
    pending_decision_count: int
    candidate_extract_delta_count: int = 0
    review_decision_delta_count: int = 0
    promotion_batch_delta_count: int = 0
    formal_evidence_delta_count: int = 0
    downstream_mutation_authorized: bool = False
    rationale: str = ""
    guardrails: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class DownstreamAuthorizationSummary:
    authorization_id: str
    authorization_status: str
    authorization_receipt_count: int
    authorization_scope: str
    audit_authorization_status: str
    pending_decision_count: int
    applied_decision_count: int
    candidate_extract_count: int
    review_decision_count: int
    promotion_batch_count: int
    formal_evidence_unit_count: int
    candidate_extract_delta_count: int
    review_decision_delta_count: int
    promotion_batch_delta_count: int
    formal_evidence_delta_count: int
    downstream_mutation_authorized: bool
    next_downstream_entry: str
    receipt_ids: list[str]
    authorization_audit_ids: list[str]
    boundary_checks: dict[str, str]
    guardrails: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvidenceTrace:
    trace_id: str
    conclusion_id: str
    chart_signals: list[str]
    evidence_ids: list[str]
    assumptions: list[str]
    disagreement_note: str = ""
    calculation_status: CalculationStatus = "not_computed"
    calculation_confidence: CalculationConfidence = "low"
    supporting_signals: list[str] = field(default_factory=list)
    opposing_signals: list[str] = field(default_factory=list)
    rule_ids: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    school_views: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.calculation_status not in CALCULATION_STATUSES:
            raise ValueError(
                f"unsupported calculation status: {self.calculation_status}"
            )
        if self.calculation_confidence not in CALCULATION_CONFIDENCES:
            raise ValueError(
                "unsupported calculation confidence: "
                f"{self.calculation_confidence}"
            )


@dataclass(frozen=True)
class FormalConclusion:
    conclusion_id: str
    title: str
    body: str
    rule_family: str
    strength: str
    risk_tier: str
    trace: EvidenceTrace


@dataclass(frozen=True)
class ActionReflectionItem:
    action_id: str
    title: str
    status: str
    rule_families: list[str]
    evidence_ids: list[str]
    conditions: list[str]
    observation_prompt: str
    feedback_metric: str
    stop_boundary: str


@dataclass(frozen=True)
class ExpandedReportEvidence:
    source_summary: list[str]
    formal_conclusions: list[FormalConclusion]
    high_risk_notes: list[str] = field(default_factory=list)
    unavailable_conclusions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReportEvidenceAudit:
    audit_status: str
    rule_family_count: int
    formal_conclusion_count: int
    traced_evidence_unit_count: int
    enabled_rule_families: list[str]
    conclusion_rule_families: list[str]
    missing_rule_families: list[str]
    open_conflicts: list[str]
    guardrail_count: int
    unavailable_conclusion_count: int
    computed_rule_family_count: int = 0
    indeterminate_rule_family_count: int = 0
    disputed_rule_family_count: int = 0
    not_computed_rule_family_count: int = 0


@dataclass(frozen=True)
class ChartSource:
    source_type: str
    source_note: str
    calendar_assumption: str
    timezone_assumption: str
    solar_terms_assumption: str
    true_solar_time_applied: bool | None
    confidence: str


@dataclass(frozen=True)
class Pillar:
    name: str
    heavenly_stem: str
    earthly_branch: str
    hidden_stems: list[str]
    ten_god: str
    element: str


@dataclass(frozen=True)
class BaziChart:
    birth_profile: BirthProfile
    chart_source: ChartSource
    pillars: list[Pillar]
    day_master: str
    five_elements_summary: dict[str, str]
    ten_gods_summary: str
    strength_assessment: str
    pattern_candidates: list[str]
    useful_god_candidates: list[str]
    luck_cycle_summary: str


@dataclass(frozen=True)
class Report:
    title: str
    disclaimer: str
    quick_guide: str
    chart_card: str
    assumptions: str
    four_pillars_summary: str
    five_elements_summary: str
    ten_gods_summary: str
    evidence_notes: str
    formal_synthesis: str
    integrated_synthesis: str
    structure_analysis: str
    personality_tendencies: str
    strengths_and_issues: str
    phase_overview: str
    action_reflection_items: list[ActionReflectionItem]
    action_suggestions: str
    interpretation_boundaries: str
    glossary: str
    ethics_reminder: str
    report_evidence_audit: ReportEvidenceAudit
    knowledge_activation: KnowledgeActivationSummary
    expanded_evidence: ExpandedReportEvidence
    safety_review: SafetyReviewResult
