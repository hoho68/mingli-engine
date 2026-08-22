from dataclasses import dataclass, field, fields
import math
from typing import Literal, get_args, get_origin


ComputationStatus = Literal[
    "not_computed", "computed", "indeterminate", "disputed"
]
Confidence = Literal["high", "medium", "low"]

_STATUSES = frozenset({"not_computed", "computed", "indeterminate", "disputed"})
_CONFIDENCES = frozenset({"high", "medium", "low"})


def _normalize_tuple_value(value: object, annotation: object) -> object:
    if get_origin(annotation) is not tuple or not isinstance(value, (list, tuple)):
        return value

    item_annotations = get_args(annotation)
    if len(item_annotations) == 2 and item_annotations[1] is Ellipsis:
        return tuple(
            _normalize_tuple_value(item, item_annotations[0]) for item in value
        )
    return tuple(
        _normalize_tuple_value(
            item,
            item_annotations[index] if index < len(item_annotations) else object,
        )
        for index, item in enumerate(value)
    )


class _ImmutableSequences:
    def __post_init__(self) -> None:
        for model_field in fields(self):  # type: ignore[arg-type]
            value = getattr(self, model_field.name)
            normalized = _normalize_tuple_value(value, model_field.type)
            if normalized is not value:
                object.__setattr__(self, model_field.name, normalized)


@dataclass(frozen=True)
class ReasonedResult(_ImmutableSequences):
    status: ComputationStatus
    conclusion: str
    confidence: Confidence
    supporting_signals: tuple[str, ...] = field(default_factory=tuple)
    opposing_signals: tuple[str, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    missing_inputs: tuple[str, ...] = field(default_factory=tuple)
    rule_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.status not in _STATUSES:
            raise ValueError(f"unsupported computation status: {self.status}")
        if self.confidence not in _CONFIDENCES:
            raise ValueError(f"unsupported confidence: {self.confidence}")


@dataclass(frozen=True)
class StemFact(_ImmutableSequences):
    pillar_name: str
    stem: str
    element: str
    polarity: str
    ten_god: str


@dataclass(frozen=True)
class HiddenStemFact(_ImmutableSequences):
    pillar_name: str
    branch: str
    stem: str
    role: str
    element: str
    polarity: str
    ten_god: str


@dataclass(frozen=True)
class RootFact(_ImmutableSequences):
    stem: str
    stem_pillar: str
    branch: str
    branch_pillar: str
    role: str
    exact_stem_root: bool


@dataclass(frozen=True)
class ChartFacts(_ImmutableSequences):
    day_master: str
    month_branch: str
    exposed_stems: tuple[StemFact, ...]
    hidden_stems: tuple[HiddenStemFact, ...]
    roots: tuple[RootFact, ...]
    twelve_growth_by_pillar: tuple[tuple[str, str], ...]
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class BranchRelationResult(_ImmutableSequences):
    relation_type: str
    branches: tuple[str, ...]
    pillar_names: tuple[str, ...]
    state: str
    transformed_element: str
    conditions: tuple[str, ...]
    blockers: tuple[str, ...]
    rule_id: str


@dataclass(frozen=True)
class StrengthContribution(_ImmutableSequences):
    category: str
    signal: str
    value: float
    rule_id: str


@dataclass(frozen=True)
class StrengthResult(_ImmutableSequences):
    reasoning: ReasonedResult
    score: float
    lower_bound: float
    upper_bound: float
    label: str
    contributions: tuple[StrengthContribution, ...]


@dataclass(frozen=True)
class PatternCandidateResult(_ImmutableSequences):
    pattern_id: str
    name: str
    rank: int
    reasoning: ReasonedResult
    formation_conditions: tuple[str, ...]
    damage_conditions: tuple[str, ...]
    rescue_conditions: tuple[str, ...]


@dataclass(frozen=True)
class UsefulGodCandidateResult(_ImmutableSequences):
    method: str
    element: str
    rank: int
    reasoning: ReasonedResult


def _require_string(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a nonempty string")


def _require_string_tuple(value: object, field_name: str) -> None:
    if not isinstance(value, tuple) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise TypeError(f"{field_name} must be a tuple of nonempty strings")


def _require_reasoning(value: object, field_name: str) -> None:
    if not isinstance(value, ReasonedResult):
        raise TypeError(f"{field_name} must be a ReasonedResult")


@dataclass(frozen=True)
class TabooGodCandidate(_ImmutableSequences):
    element: str
    rank: int
    pressure_score: float
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        _require_string(self.element, "element")
        if isinstance(self.rank, bool) or not isinstance(self.rank, int) or self.rank < 1:
            raise TypeError("rank must be a positive integer")
        if (
            isinstance(self.pressure_score, bool)
            or not isinstance(self.pressure_score, (int, float))
            or not math.isfinite(self.pressure_score)
        ):
            raise TypeError("pressure_score must be a finite number")
        _require_string_tuple(self.reasons, "reasons")


@dataclass(frozen=True)
class TabooGodResult(_ImmutableSequences):
    reasoning: ReasonedResult
    candidates: tuple[TabooGodCandidate, ...]
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        _require_reasoning(self.reasoning, "reasoning")
        if not isinstance(self.candidates, tuple) or not all(
            isinstance(item, TabooGodCandidate) for item in self.candidates
        ):
            raise TypeError("candidates must be a tuple of TabooGodCandidate")
        _require_string_tuple(self.evidence_ids, "evidence_ids")


@dataclass(frozen=True)
class BlindImageSignal(_ImmutableSequences):
    image_id: str
    category: str
    value: str
    structural_signals: tuple[str, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        _require_string(self.image_id, "image_id")
        _require_string(self.category, "category")
        _require_string(self.value, "value")
        _require_string_tuple(self.structural_signals, "structural_signals")


@dataclass(frozen=True)
class BlindImageResult(_ImmutableSequences):
    reasoning: ReasonedResult
    images: tuple[BlindImageSignal, ...]
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        _require_reasoning(self.reasoning, "reasoning")
        if not isinstance(self.images, tuple) or not all(
            isinstance(item, BlindImageSignal) for item in self.images
        ):
            raise TypeError("images must be a tuple of BlindImageSignal")
        _require_string_tuple(self.evidence_ids, "evidence_ids")


@dataclass(frozen=True)
class RemedyBoundaryResult(_ImmutableSequences):
    reasoning: ReasonedResult
    conditions: tuple[str, ...]
    applicable_boundaries: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        _require_reasoning(self.reasoning, "reasoning")
        _require_string_tuple(self.conditions, "conditions")
        _require_string_tuple(self.applicable_boundaries, "applicable_boundaries")
        _require_string_tuple(self.stop_conditions, "stop_conditions")
        _require_string_tuple(self.evidence_ids, "evidence_ids")


def _missing_family_reasoning(rule_family: str) -> ReasonedResult:
    reason = f"no_v1_calculation_for:{rule_family}"
    return ReasonedResult(
        status="not_computed",
        conclusion=f"No V1 calculation is available for {rule_family}.",
        confidence="low",
        missing_inputs=(reason,),
        rule_ids=(reason,),
    )


def _missing_taboo_gods() -> TabooGodResult:
    return TabooGodResult(
        reasoning=_missing_family_reasoning("taboo_god_candidate"),
        candidates=(),
        evidence_ids=(),
    )


def _missing_blind_images() -> BlindImageResult:
    return BlindImageResult(
        reasoning=_missing_family_reasoning("blind_image_method"),
        images=(),
        evidence_ids=(),
    )


def _missing_remedy_boundary() -> RemedyBoundaryResult:
    return RemedyBoundaryResult(
        reasoning=_missing_family_reasoning("remedy_boundary"),
        conditions=(),
        applicable_boundaries=(),
        stop_conditions=(),
        evidence_ids=(),
    )


@dataclass(frozen=True)
class LuckPillar(_ImmutableSequences):
    index: int
    gan_zhi: str
    start_year: int
    end_year: int
    start_age: int
    end_age: int


@dataclass(frozen=True)
class LuckCycleResult(_ImmutableSequences):
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
class SchoolInterpretation(_ImmutableSequences):
    school_id: str
    profile_version: str
    reasoning: ReasonedResult
    preferred_pattern_ids: tuple[str, ...]
    preferred_useful_god_elements: tuple[str, ...]


@dataclass(frozen=True)
class CalculationBundle(_ImmutableSequences):
    engine_version: str
    ruleset_version: str
    facts: ChartFacts
    branch_relations: tuple[BranchRelationResult, ...]
    strength: StrengthResult
    patterns: tuple[PatternCandidateResult, ...]
    useful_gods: tuple[UsefulGodCandidateResult, ...]
    luck_cycles: LuckCycleResult
    schools: tuple[SchoolInterpretation, ...]
    taboo_gods: TabooGodResult = field(default_factory=_missing_taboo_gods)
    blind_images: BlindImageResult = field(default_factory=_missing_blind_images)
    remedy_boundary: RemedyBoundaryResult = field(
        default_factory=_missing_remedy_boundary
    )
