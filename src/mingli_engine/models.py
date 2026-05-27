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
