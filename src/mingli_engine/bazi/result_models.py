from dataclasses import dataclass, field
from typing import Literal


ComputationStatus = Literal[
    "not_computed", "computed", "indeterminate", "disputed"
]
Confidence = Literal["high", "medium", "low"]

_STATUSES = frozenset({"not_computed", "computed", "indeterminate", "disputed"})
_CONFIDENCES = frozenset({"high", "medium", "low"})


@dataclass(frozen=True)
class ReasonedResult:
    status: ComputationStatus
    conclusion: str
    confidence: Confidence
    supporting_signals: tuple[str, ...] = field(default_factory=tuple)
    opposing_signals: tuple[str, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    missing_inputs: tuple[str, ...] = field(default_factory=tuple)
    rule_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.status not in _STATUSES:
            raise ValueError(f"unsupported computation status: {self.status}")
        if self.confidence not in _CONFIDENCES:
            raise ValueError(f"unsupported confidence: {self.confidence}")


@dataclass(frozen=True)
class StemFact:
    pillar_name: str
    stem: str
    element: str
    polarity: str
    ten_god: str


@dataclass(frozen=True)
class HiddenStemFact:
    pillar_name: str
    branch: str
    stem: str
    role: str
    element: str
    polarity: str
    ten_god: str


@dataclass(frozen=True)
class RootFact:
    stem: str
    stem_pillar: str
    branch: str
    branch_pillar: str
    role: str
    exact_stem_root: bool


@dataclass(frozen=True)
class ChartFacts:
    day_master: str
    month_branch: str
    exposed_stems: tuple[StemFact, ...]
    hidden_stems: tuple[HiddenStemFact, ...]
    roots: tuple[RootFact, ...]
    twelve_growth_by_pillar: tuple[tuple[str, str], ...]
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class BranchRelationResult:
    relation_type: str
    branches: tuple[str, ...]
    pillar_names: tuple[str, ...]
    state: str
    transformed_element: str
    conditions: tuple[str, ...]
    blockers: tuple[str, ...]
    rule_id: str


@dataclass(frozen=True)
class StrengthContribution:
    category: str
    signal: str
    value: float
    rule_id: str


@dataclass(frozen=True)
class StrengthResult:
    reasoning: ReasonedResult
    score: float
    lower_bound: float
    upper_bound: float
    label: str
    contributions: tuple[StrengthContribution, ...]


@dataclass(frozen=True)
class PatternCandidateResult:
    pattern_id: str
    name: str
    rank: int
    reasoning: ReasonedResult
    formation_conditions: tuple[str, ...]
    damage_conditions: tuple[str, ...]
    rescue_conditions: tuple[str, ...]


@dataclass(frozen=True)
class UsefulGodCandidateResult:
    method: str
    element: str
    rank: int
    reasoning: ReasonedResult


@dataclass(frozen=True)
class LuckPillar:
    index: int
    gan_zhi: str
    start_year: int
    end_year: int
    start_age: int
    end_age: int


@dataclass(frozen=True)
class LuckCycleResult:
    reasoning: ReasonedResult
    forward: bool
    start_years: int
    start_months: int
    start_days: int
    start_solar: str
    pillars: tuple[LuckPillar, ...]
    selected_year_relations: tuple[BranchRelationResult, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class SchoolInterpretation:
    school_id: str
    profile_version: str
    reasoning: ReasonedResult
    preferred_pattern_ids: tuple[str, ...]
    preferred_useful_god_elements: tuple[str, ...]


@dataclass(frozen=True)
class CalculationBundle:
    engine_version: str
    ruleset_version: str
    facts: ChartFacts
    branch_relations: tuple[BranchRelationResult, ...]
    strength: StrengthResult
    patterns: tuple[PatternCandidateResult, ...]
    useful_gods: tuple[UsefulGodCandidateResult, ...]
    luck_cycles: LuckCycleResult
    schools: tuple[SchoolInterpretation, ...]
