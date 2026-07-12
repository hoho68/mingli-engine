from dataclasses import dataclass
import json
import math
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Mapping, cast

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

ElementCategory = Literal[
    "companion", "resource", "output", "wealth", "officer"
]


@dataclass(frozen=True)
class StrengthConfig:
    version: str
    month_command: Mapping[str, float]
    root: Mapping[str, float]
    exposed: Mapping[str, float]
    hidden_factor: float
    thresholds: Mapping[str, float]
    sensitivity_fraction: float


def _numeric(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be numeric and finite")
    return number


def _validated_section(
    payload: Mapping[str, object], section_name: str
) -> Mapping[str, float]:
    value = payload[section_name]
    if not isinstance(value, dict):
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

    if not 0 <= hidden_factor <= 1:
        raise ValueError("hidden_factor must be between 0 and 1")
    if sensitivity_fraction < 0:
        raise ValueError("sensitivity_fraction must be nonnegative")
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
        version=version,
        month_command=month_command,
        root=root,
        exposed=exposed,
        hidden_factor=hidden_factor,
        thresholds=thresholds,
        sensitivity_fraction=sensitivity_fraction,
    )


def _stem_element(stem: str) -> str:
    if stem not in STEMS:
        raise ValueError(f"Invalid stem: {stem!r}")
    return STEM_ELEMENT[stem]  # type: ignore[index]


def _element_category(day_element: str, target_element: str) -> ElementCategory:
    if target_element == day_element:
        return "companion"
    if GENERATES[target_element] == day_element:  # type: ignore[index]
        return "resource"
    if GENERATES[day_element] == target_element:  # type: ignore[index]
        return "output"
    if CONTROLS[day_element] == target_element:  # type: ignore[index]
        return "wealth"
    if CONTROLS[target_element] == day_element:  # type: ignore[index]
        return "officer"
    raise ValueError(f"Invalid element: {target_element!r}")


def _label(score: float, thresholds: Mapping[str, float]) -> str:
    if score <= thresholds["weak"]:
        return "弱"
    if score < thresholds["balanced_low"]:
        return "偏弱"
    if score <= thresholds["balanced_high"]:
        return "较平衡"
    if score < thresholds["strong"]:
        return "偏强"
    return "强"


def calculate_strength(
    facts: ChartFacts,
    relations: tuple[BranchRelationResult, ...] = (),
    *,
    config: StrengthConfig | None = None,
) -> StrengthResult:
    active_config = config if config is not None else load_strength_config()
    day_element = _stem_element(facts.day_master)
    if facts.month_branch not in BRANCHES:
        raise ValueError(f"Invalid branch: {facts.month_branch!r}")

    contributions: list[StrengthContribution] = []
    month_element = BRANCH_ELEMENT[facts.month_branch]  # type: ignore[index]
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

    for root in facts.roots:
        _stem_element(root.stem)
        if root.role not in _ROOT_ROLES:
            raise ValueError(f"unknown root role: {root.role!r}")
        if root.stem != facts.day_master:
            continue
        contributions.append(
            StrengthContribution(
                category="root",
                signal=root.role,
                value=active_config.root[root.role],
                rule_id=f"strength.root.{root.role}",
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

    score = sum(item.value for item in contributions)
    sensitivity = active_config.sensitivity_fraction
    sensitivity_ranges = tuple(
        tuple(
            item.value * factor
            for factor in (1 - sensitivity, 1 + sensitivity)
        )
        for item in contributions
    )
    lower_bound = sum(min(values) for values in sensitivity_ranges)
    upper_bound = sum(max(values) for values in sensitivity_ranges)
    central_label = _label(score, active_config.thresholds)
    lower_label = _label(lower_bound, active_config.thresholds)
    upper_label = _label(upper_bound, active_config.thresholds)

    relation_assumptions = tuple(
        f"{relation.rule_id}: no numeric strength modifier without a proven "
        "transformed_element"
        for relation in relations
    )
    relation_rule_ids = tuple(
        f"strength.relation.no_numeric_modifier:{relation.rule_id}"
        for relation in relations
    )
    contribution_rule_ids = tuple(item.rule_id for item in contributions)
    labels = (lower_label, central_label, upper_label)
    indeterminate = len(set(labels)) > 1
    if indeterminate:
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
        status=cast(Literal["computed", "indeterminate"], status),
        conclusion=conclusion,
        confidence=cast(Literal["high", "medium", "low"], confidence),
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
        missing_inputs=(),
        rule_ids=contribution_rule_ids + relation_rule_ids,
    )
    return StrengthResult(
        reasoning=reasoning,
        score=score,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        label=result_label,
        contributions=tuple(contributions),
    )
