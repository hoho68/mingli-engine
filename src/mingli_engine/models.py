from dataclasses import dataclass, field


SOURCE_TYPES = frozenset({"pdf"})
EXTRACTION_STATUSES = frozenset({"not_started", "converted", "partial", "failed"})
REVIEW_STATUSES = frozenset({"unreviewed", "reviewed", "approved", "blocked"})
REPORT_USABLE_REVIEW_STATUS = "approved"
RISK_TIERS = frozenset({"ordinary", "sensitive", "high_risk"})
CONCLUSION_STRENGTHS = frozenset(
    {"decided", "candidate", "weakly_supported", "disputed", "unavailable"}
)
RULE_FAMILIES = frozenset(
    {
        "pattern_strength",
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
