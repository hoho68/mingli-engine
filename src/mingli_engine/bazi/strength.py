from dataclasses import dataclass
import json
import math
from pathlib import Path
from types import MappingProxyType
from typing import Iterable, Literal, Mapping, TypeAlias, cast

from mingli_engine.bazi.constants import (
    BRANCHES,
    BRANCH_ELEMENT,
    CONTROLS,
    GENERATES,
    STEMS,
    STEM_ELEMENT,
)
from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    ChartFacts,
    ReasonedResult,
    StrengthContribution,
    StrengthResult,
)


_DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "calculation"
    / "strength_weights.json"
)
_TOP_LEVEL_KEYS = frozenset(
    {
        "version",
        "month_command",
        "root",
        "exposed",
        "hidden_factor",
        "thresholds",
        "sensitivity_fraction",
    }
)
_SECTION_KEYS = {
    "month_command": frozenset(
        {"same_element", "resource", "output", "wealth", "officer"}
    ),
    "root": frozenset({"main", "middle", "residual"}),
    "exposed": frozenset(
        {"companion", "resource", "output", "wealth", "officer"}
    ),
    "thresholds": frozenset(
        {"weak", "balanced_low", "balanced_high", "strong"}
    ),
}
_ROOT_ROLES = frozenset({"main", "middle", "residual"})
_SUPPORTED_VERSION = "ziping-strength-v1"
_NONFINITE_ERROR = "strength calculation produced a non-finite value"
_THRESHOLD_REL_TOLERANCE = 1e-12
_THRESHOLD_ABS_TOLERANCE = 1e-12

Stem: TypeAlias = Literal[
    "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"
]
Branch: TypeAlias = Literal[
    "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"
]
Element: TypeAlias = Literal["木", "火", "土", "金", "水"]
RootRole: TypeAlias = Literal["main", "middle", "residual"]
SectionName: TypeAlias = Literal[
    "month_command", "root", "exposed", "thresholds"
]
MonthCommandKey: TypeAlias = Literal[
    "same_element", "resource", "output", "wealth", "officer"
]
ThresholdKey: TypeAlias = Literal[
    "weak", "balanced_low", "balanced_high", "strong"
]

ElementCategory: TypeAlias = Literal[
    "companion", "resource", "output", "wealth", "officer"
]


@dataclass(frozen=True)
class StrengthConfig:
    version: str
    month_command: Mapping[MonthCommandKey, float]
    root: Mapping[RootRole, float]
    exposed: Mapping[ElementCategory, float]
    hidden_factor: float
    thresholds: Mapping[ThresholdKey, float]
    sensitivity_fraction: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "month_command",
            MappingProxyType(dict(self.month_command)),
        )
        object.__setattr__(self, "root", MappingProxyType(dict(self.root)))
        object.__setattr__(
            self,
            "exposed",
            MappingProxyType(dict(self.exposed)),
        )
        object.__setattr__(
            self,
            "thresholds",
            MappingProxyType(dict(self.thresholds)),
        )


def _numeric(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric")
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric and finite") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be numeric and finite")
    return number


def _validated_section(
    payload: Mapping[str, object], section_name: SectionName
) -> Mapping[str, float]:
    value = payload[section_name]
    if not isinstance(value, Mapping):
        raise ValueError(f"{section_name} must be an object")

    expected = _SECTION_KEYS[section_name]
    present = set(value)
    missing = sorted(expected - present)
    unknown = sorted(present - expected)
    if missing:
        raise ValueError(
            f"missing {section_name} categories: {', '.join(missing)}"
        )
    if unknown:
        raise ValueError(
            f"unknown {section_name} categories: {', '.join(unknown)}"
        )

    return MappingProxyType(
        {
            key: _numeric(value[key], f"{section_name}.{key}")
            for key in expected
        }
    )


def _validate_strength_config(config: StrengthConfig) -> StrengthConfig:
    if config.version != _SUPPORTED_VERSION:
        raise ValueError(
            f"unsupported strength config version: {config.version!r}"
        )

    payload: Mapping[str, object] = {
        "month_command": config.month_command,
        "root": config.root,
        "exposed": config.exposed,
        "thresholds": config.thresholds,
    }
    month_command = _validated_section(payload, "month_command")
    root = _validated_section(payload, "root")
    exposed = _validated_section(payload, "exposed")
    thresholds = _validated_section(payload, "thresholds")
    hidden_factor = _numeric(config.hidden_factor, "hidden_factor")
    sensitivity_fraction = _numeric(
        config.sensitivity_fraction, "sensitivity_fraction"
    )

    if not 0 <= hidden_factor <= 1:
        raise ValueError("hidden_factor must be between 0 and 1")
    if sensitivity_fraction < 0:
        raise ValueError("sensitivity_fraction must be nonnegative")
    if sensitivity_fraction > 1:
        raise ValueError("sensitivity_fraction must be between 0 and 1")
    if not (
        thresholds["weak"]
        < thresholds["balanced_low"]
        < thresholds["balanced_high"]
        < thresholds["strong"]
    ):
        raise ValueError(
            "thresholds must satisfy weak < balanced_low < "
            "balanced_high < strong"
        )

    return StrengthConfig(
        version=config.version,
        month_command=cast(
            Mapping[MonthCommandKey, float], month_command
        ),
        root=cast(Mapping[RootRole, float], root),
        exposed=cast(Mapping[ElementCategory, float], exposed),
        hidden_factor=hidden_factor,
        thresholds=cast(Mapping[ThresholdKey, float], thresholds),
        sensitivity_fraction=sensitivity_fraction,
    )


def load_strength_config(path: str | Path | None = None) -> StrengthConfig:
    config_path = Path(path) if path is not None else _DEFAULT_CONFIG_PATH
    try:
        raw = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(
            f"unable to read strength config {config_path}: {exc}"
        ) from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid JSON in strength config {config_path}: {exc.msg}"
        ) from exc
    if not isinstance(payload, dict):
        raise ValueError("strength config must be a JSON object")

    present = set(payload)
    missing = sorted(_TOP_LEVEL_KEYS - present)
    unknown = sorted(present - _TOP_LEVEL_KEYS)
    if missing:
        raise ValueError(f"missing top-level fields: {', '.join(missing)}")
    if unknown:
        raise ValueError(f"unknown top-level fields: {', '.join(unknown)}")

    version = payload["version"]
    if not isinstance(version, str) or not version.strip():
        raise ValueError("version must be a non-empty string")

    month_command = _validated_section(payload, "month_command")
    root = _validated_section(payload, "root")
    exposed = _validated_section(payload, "exposed")
    thresholds = _validated_section(payload, "thresholds")
    hidden_factor = _numeric(payload["hidden_factor"], "hidden_factor")
    sensitivity_fraction = _numeric(
        payload["sensitivity_fraction"], "sensitivity_fraction"
    )

    config = StrengthConfig(
        version=version,
        month_command=cast(Mapping[MonthCommandKey, float], month_command),
        root=cast(Mapping[RootRole, float], root),
        exposed=cast(Mapping[ElementCategory, float], exposed),
        hidden_factor=hidden_factor,
        thresholds=cast(Mapping[ThresholdKey, float], thresholds),
        sensitivity_fraction=sensitivity_fraction,
    )
    return _validate_strength_config(config)


def _validated_stem(stem: str) -> Stem:
    if stem not in STEMS:
        raise ValueError(f"Invalid stem: {stem!r}")
    return cast(Stem, stem)


def _validated_branch(branch: str) -> Branch:
    if branch not in BRANCHES:
        raise ValueError(f"Invalid branch: {branch!r}")
    return cast(Branch, branch)


def _validated_root_role(role: str) -> RootRole:
    if role not in _ROOT_ROLES:
        raise ValueError(f"unknown root role: {role!r}")
    return cast(RootRole, role)


def _stem_element(stem: str) -> Element:
    return STEM_ELEMENT[_validated_stem(stem)]


def _element_category(
    day_element: Element, target_element: Element
) -> ElementCategory:
    if target_element == day_element:
        return "companion"
    if GENERATES[target_element] == day_element:
        return "resource"
    if GENERATES[day_element] == target_element:
        return "output"
    if CONTROLS[day_element] == target_element:
        return "wealth"
    if CONTROLS[target_element] == day_element:
        return "officer"
    raise ValueError(f"Invalid element: {target_element!r}")


def _finite_value(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError(_NONFINITE_ERROR)
    return value


def _safe_product(left: float, right: float) -> float:
    return _finite_value(left * right)


def _safe_total(values: Iterable[float]) -> float:
    try:
        total = math.fsum(values)
    except (OverflowError, ValueError) as exc:
        raise ValueError(_NONFINITE_ERROR) from exc
    return _finite_value(total)


def _threshold_snapped_score(
    score: float, thresholds: Mapping[ThresholdKey, float]
) -> float:
    # Snap only comparison operands to absorb binary float noise at boundaries.
    for threshold_name in (
        "weak",
        "balanced_low",
        "balanced_high",
        "strong",
    ):
        threshold = thresholds[threshold_name]
        if math.isclose(
            score,
            threshold,
            rel_tol=_THRESHOLD_REL_TOLERANCE,
            abs_tol=_THRESHOLD_ABS_TOLERANCE,
        ):
            return threshold
    return score


def _label(score: float, thresholds: Mapping[ThresholdKey, float]) -> str:
    comparison_score = _threshold_snapped_score(score, thresholds)
    if comparison_score <= thresholds["weak"]:
        return "弱"
    if comparison_score < thresholds["balanced_low"]:
        return "偏弱"
    if comparison_score <= thresholds["balanced_high"]:
        return "较平衡"
    if comparison_score < thresholds["strong"]:
        return "偏强"
    return "强"


def _relation_occurrence_token(relation: BranchRelationResult) -> str:
    return (
        f"{relation.rule_id}|pillars={','.join(relation.pillar_names)}"
        f"|branches={','.join(relation.branches)}"
    )


def calculate_strength(
    facts: ChartFacts,
    relations: tuple[BranchRelationResult, ...] = (),
    *,
    config: StrengthConfig | None = None,
) -> StrengthResult:
    active_config = (
        load_strength_config()
        if config is None
        else _validate_strength_config(config)
    )
    day_element = _stem_element(facts.day_master)
    month_branch = _validated_branch(facts.month_branch)

    contributions: list[StrengthContribution] = []
    month_element = BRANCH_ELEMENT[month_branch]
    month_category = _element_category(day_element, month_element)
    month_key = "same_element" if month_category == "companion" else month_category
    contributions.append(
        StrengthContribution(
            category="month_command",
            signal=month_category,
            value=active_config.month_command[month_key],
            rule_id=f"strength.month_command.{month_key}",
        )
    )

    seen_physical_roots: set[tuple[str, str, str, RootRole]] = set()
    for root in facts.roots:
        _stem_element(root.stem)
        role = _validated_root_role(root.role)
        if root.stem != facts.day_master or not root.exact_stem_root:
            continue
        physical_identity = (
            root.stem,
            root.branch_pillar,
            root.branch,
            role,
        )
        if physical_identity in seen_physical_roots:
            continue
        seen_physical_roots.add(physical_identity)
        contributions.append(
            StrengthContribution(
                category="root",
                signal=(
                    f"{root.branch_pillar}:{root.branch}:{role}"
                ),
                value=active_config.root[role],
                rule_id=f"strength.root.{role}",
            )
        )

    for exposed in facts.exposed_stems:
        target_element = _stem_element(exposed.stem)
        if exposed.pillar_name == "day" and exposed.stem == facts.day_master:
            continue
        category = _element_category(day_element, target_element)
        contributions.append(
            StrengthContribution(
                category="exposed",
                signal=f"{exposed.pillar_name}:{category}",
                value=active_config.exposed[category],
                rule_id=f"strength.exposed.{category}",
            )
        )

    for hidden in facts.hidden_stems:
        target_element = _stem_element(hidden.stem)
        if hidden.role not in _ROOT_ROLES:
            raise ValueError(f"unknown hidden stem role: {hidden.role!r}")
        category = _element_category(day_element, target_element)
        contributions.append(
            StrengthContribution(
                category="hidden",
                signal=f"{hidden.pillar_name}:{hidden.role}:{category}",
                value=(
                    active_config.exposed[category]
                    * active_config.hidden_factor
                ),
                rule_id=f"strength.hidden.{category}",
            )
        )

    contribution_values = tuple(
        _finite_value(item.value) for item in contributions
    )
    score = _safe_total(contribution_values)
    sensitivity = active_config.sensitivity_fraction
    sensitivity_scores = tuple(
        _safe_total(
            _safe_product(value, factor)
            for value in contribution_values
        )
        for factor in (1 - sensitivity, 1 + sensitivity)
    )
    lower_bound = _finite_value(min(sensitivity_scores))
    upper_bound = _finite_value(max(sensitivity_scores))
    central_label = _label(score, active_config.thresholds)
    lower_label = _label(lower_bound, active_config.thresholds)
    upper_label = _label(upper_bound, active_config.thresholds)

    transformed_relations = tuple(
        relation for relation in relations if relation.transformed_element
    )
    relation_assumptions: list[str] = []
    relation_rule_ids: list[str] = []
    for relation in relations:
        occurrence_token = _relation_occurrence_token(relation)
        if relation.transformed_element:
            relation_assumptions.append(
                f"{occurrence_token}: transformed_element="
                f"{relation.transformed_element}; V1 transformed relation "
                "strength modifier not implemented"
            )
            relation_rule_ids.append(
                "strength.relation.transformed_modifier_unimplemented:"
                f"{occurrence_token}"
            )
        else:
            relation_assumptions.append(
                f"{occurrence_token}: transformed_element is empty; no "
                "numeric strength modifier applied"
            )
            relation_rule_ids.append(
                "strength.relation.no_numeric_modifier:"
                f"{occurrence_token}"
            )
    contribution_rule_ids = tuple(item.rule_id for item in contributions)
    labels = (lower_label, central_label, upper_label)
    sensitivity_crosses = len(set(labels)) > 1
    status: Literal["computed", "indeterminate"]
    confidence: Literal["high", "medium", "low"]
    if transformed_relations:
        status = "indeterminate"
        confidence = "low"
        causes = ["transformed relation strength modifier not implemented"]
        if sensitivity_crosses:
            causes.append(
                f"lower={lower_label}; central={central_label}; "
                f"upper={upper_label}"
            )
        conclusion = "; ".join(causes)
        result_label = "待定"
    elif sensitivity_crosses:
        status = "indeterminate"
        confidence = "low"
        conclusion = (
            f"lower={lower_label}; central={central_label}; upper={upper_label}"
        )
        result_label = "临界"
    else:
        status = "computed"
        confidence = "high" if sensitivity == 0 else "medium"
        conclusion = central_label
        result_label = central_label

    reasoning = ReasonedResult(
        status=status,
        conclusion=conclusion,
        confidence=confidence,
        supporting_signals=tuple(
            item.signal for item in contributions if item.value > 0
        ),
        opposing_signals=tuple(
            item.signal for item in contributions if item.value < 0
        ),
        assumptions=(
            *facts.assumptions,
            f"profile_version={active_config.version}",
            f"sensitivity_fraction={sensitivity}",
            *relation_assumptions,
        ),
        missing_inputs=(
            ("transformed_relation_strength_modifier",)
            if transformed_relations
            else ()
        ),
        rule_ids=contribution_rule_ids + tuple(relation_rule_ids),
    )
    return StrengthResult(
        reasoning=reasoning,
        score=score,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        label=result_label,
        contributions=tuple(contributions),
    )
