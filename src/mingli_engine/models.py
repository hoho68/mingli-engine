from dataclasses import dataclass, field


SOURCE_TYPES = frozenset({"pdf"})
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
class EvidenceTrace:
    trace_id: str
    conclusion_id: str
    chart_signals: list[str]
    evidence_ids: list[str]
    assumptions: list[str]
    disagreement_note: str = ""


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
class ExpandedReportEvidence:
    source_summary: list[str]
    formal_conclusions: list[FormalConclusion]
    high_risk_notes: list[str] = field(default_factory=list)
    unavailable_conclusions: list[str] = field(default_factory=list)


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
    structure_analysis: str
    personality_tendencies: str
    strengths_and_issues: str
    phase_overview: str
    action_suggestions: str
    interpretation_boundaries: str
    glossary: str
    ethics_reminder: str
    expanded_evidence: ExpandedReportEvidence
    safety_review: SafetyReviewResult
