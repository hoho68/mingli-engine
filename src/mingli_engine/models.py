from dataclasses import dataclass, field


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
    structure_analysis: str
    personality_tendencies: str
    strengths_and_issues: str
    phase_overview: str
    action_suggestions: str
    interpretation_boundaries: str
    glossary: str
    ethics_reminder: str
    safety_review: SafetyReviewResult
