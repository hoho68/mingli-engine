from collections import Counter
from dataclasses import replace
from types import MappingProxyType
from typing import Final, Literal, Mapping, TypeGuard, cast

from mingli_engine.bazi.constants import (
    BRANCHES,
    CONTROLS,
    ELEMENTS,
    GENERATES,
    HIDDEN_STEMS,
    STEM_ELEMENT,
    STEM_POLARITY,
    STEMS,
)
from mingli_engine.bazi.facts import Branch, ten_god
from mingli_engine.bazi.result_models import (
    ChartFacts,
    ComputationStatus,
    Confidence,
    PatternCandidateResult,
    ReasonedResult,
    StrengthResult,
    UsefulGodCandidateResult,
)


Element = Literal["木", "火", "土", "金", "水"]
Stem = Literal["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

WINTER_BRANCHES: Final = frozenset({"亥", "子", "丑"})
SUMMER_BRANCHES: Final = frozenset({"巳", "午", "未"})

_STATUSES: Final = frozenset({"computed", "indeterminate", "disputed", "not_computed"})
_CONFIDENCES: Final = frozenset({"high", "medium", "low"})
_COMPUTED_STRENGTH_LABELS: Final = frozenset({"强", "偏强", "较平衡", "偏弱", "弱"})
_PILLARS: Final = frozenset({"year", "month", "day", "hour"})
_HIDDEN_ROLES: Final = frozenset({"main", "middle", "residual"})
_TEN_GOD_GROUPS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "比肩": "companion",
        "劫财": "companion",
        "正印": "resource",
        "偏印": "resource",
        "食神": "output",
        "伤官": "output",
        "正财": "wealth",
        "偏财": "wealth",
        "正官": "officer",
        "七杀": "officer",
    }
)
_STATUS_ORDER: Final[Mapping[str, int]] = MappingProxyType(
    {
        "computed": 0,
        "indeterminate": 1,
        "disputed": 2,
        "not_computed": 3,
    }
)
_CONFIDENCE_ORDER: Final[Mapping[str, int]] = MappingProxyType(
    {
        "high": 0,
        "medium": 1,
        "low": 2,
    }
)
_METHOD_ORDER: Final[Mapping[str, int]] = MappingProxyType(
    {
        "support_control": 0,
        "seasonal_adjustment": 1,
        "mediation": 2,
        "illness_remedy": 3,
    }
)
_ELEMENT_ORDER: Final[Mapping[str, int]] = MappingProxyType(
    {element: index for index, element in enumerate(ELEMENTS)}
)


def _is_stem(value: str) -> TypeGuard[Stem]:
    return value in STEMS


def _is_element(value: str) -> TypeGuard[Element]:
    return value in ELEMENTS


def _is_branch(value: str) -> TypeGuard[Branch]:
    return value in BRANCHES


def _distinct(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _inverse_generating(element: Element) -> Element:
    return cast(
        Element,
        next(
            source for source in ELEMENTS if GENERATES[cast(Element, source)] == element
        ),
    )


def _inverse_controlling(element: Element) -> Element:
    return cast(
        Element,
        next(
            controller
            for controller in ELEMENTS
            if CONTROLS[cast(Element, controller)] == element
        ),
    )


def _validate_status_and_confidence(
    status: str, confidence: str, *, context: str
) -> None:
    if status not in _STATUSES:
        raise ValueError(f"invalid {context} status: {status!r}")
    if confidence not in _CONFIDENCES:
        raise ValueError(f"invalid {context} confidence: {confidence!r}")


def _validate_chart_facts(facts: ChartFacts) -> Element:
    if not _is_stem(facts.day_master):
        raise ValueError(f"invalid day master: {facts.day_master!r}")
    if facts.month_branch not in BRANCHES:
        raise ValueError(f"invalid month branch: {facts.month_branch!r}")

    exposed_pillars = Counter(item.pillar_name for item in facts.exposed_stems)
    if exposed_pillars != Counter({pillar: 1 for pillar in _PILLARS}):
        raise ValueError("expected exactly one exposed stem for each canonical pillar")
    day_fact = next(item for item in facts.exposed_stems if item.pillar_name == "day")
    if day_fact.stem != facts.day_master:
        raise ValueError("day exposed stem must match day_master")
    for exposed_item in facts.exposed_stems:
        if not _is_stem(exposed_item.stem):
            raise ValueError(f"invalid exposed stem: {exposed_item.stem!r}")
        expected_element = STEM_ELEMENT[exposed_item.stem]
        if exposed_item.element != expected_element:
            raise ValueError(
                f"exposed element mismatch for {exposed_item.stem}: "
                f"{exposed_item.element!r} != {expected_element!r}"
            )
        if exposed_item.polarity != STEM_POLARITY[exposed_item.stem]:
            raise ValueError(f"exposed polarity mismatch for {exposed_item.stem}")
        if exposed_item.ten_god != ten_god(facts.day_master, exposed_item.stem):
            raise ValueError(f"exposed ten_god mismatch for {exposed_item.stem}")

    for hidden_item in facts.hidden_stems:
        if hidden_item.pillar_name not in _PILLARS:
            raise ValueError(f"invalid hidden pillar: {hidden_item.pillar_name!r}")
        if not _is_branch(hidden_item.branch):
            raise ValueError(f"invalid hidden branch: {hidden_item.branch!r}")
        if not _is_stem(hidden_item.stem):
            raise ValueError(f"invalid hidden stem: {hidden_item.stem!r}")
        if hidden_item.role not in _HIDDEN_ROLES:
            raise ValueError(f"invalid hidden role: {hidden_item.role!r}")
        if (
            hidden_item.stem,
            hidden_item.role,
        ) not in HIDDEN_STEMS[hidden_item.branch]:
            raise ValueError(
                f"hidden stem/role is not canonical for {hidden_item.branch}"
            )
        if hidden_item.element != STEM_ELEMENT[hidden_item.stem]:
            raise ValueError(f"hidden element mismatch for {hidden_item.stem}")
        if hidden_item.polarity != STEM_POLARITY[hidden_item.stem]:
            raise ValueError(f"hidden polarity mismatch for {hidden_item.stem}")
        if hidden_item.ten_god != ten_god(facts.day_master, hidden_item.stem):
            raise ValueError(f"hidden ten_god mismatch for {hidden_item.stem}")
        if (
            hidden_item.pillar_name == "month"
            and hidden_item.branch != facts.month_branch
        ):
            raise ValueError("month hidden branch must match month_branch")

    day_element = STEM_ELEMENT[facts.day_master]
    return cast(Element, day_element)


def _validate_computed_strength(strength: StrengthResult) -> None:
    if strength.label not in _COMPUTED_STRENGTH_LABELS:
        raise ValueError(f"invalid computed strength label: {strength.label!r}")
    if strength.reasoning.conclusion != strength.label:
        raise ValueError(
            "strength label consistency requires computed conclusion to match label"
        )


def _candidate(
    method: str,
    element: str,
    *,
    status: ComputationStatus,
    conclusion: str,
    confidence: Confidence,
    supporting_signals: tuple[str, ...] = (),
    opposing_signals: tuple[str, ...] = (),
    assumptions: tuple[str, ...] = (),
    missing_inputs: tuple[str, ...] = (),
    rule_ids: tuple[str, ...],
) -> UsefulGodCandidateResult:
    return UsefulGodCandidateResult(
        method=method,
        element=element,
        rank=0,
        reasoning=ReasonedResult(
            status=status,
            conclusion=conclusion,
            confidence=confidence,
            supporting_signals=_distinct(supporting_signals),
            opposing_signals=_distinct(opposing_signals),
            assumptions=_distinct(assumptions),
            missing_inputs=_distinct(missing_inputs),
            rule_ids=_distinct(rule_ids),
        ),
    )


def _blocked_candidate() -> UsefulGodCandidateResult:
    return replace(
        _candidate(
            "support_control",
            "",
            status="not_computed",
            conclusion="support/control blocked until strength is computed",
            confidence="low",
            missing_inputs=("strength_computed",),
            rule_ids=("useful_god.prerequisite.strength_computed",),
        ),
        rank=1,
    )


def _support_control_candidates(
    day_element: Element, strength: StrengthResult
) -> tuple[UsefulGodCandidateResult, ...]:
    label = strength.label
    if label == "较平衡":
        return (
            _candidate(
                "support_control",
                "",
                status="indeterminate",
                conclusion="balanced strength has no directional preference",
                confidence="medium",
                supporting_signals=(f"strength_label:{label}",),
                rule_ids=("useful_god.support_control.balanced_no_preference",),
            ),
        )

    if label in {"强", "偏强"}:
        elements: tuple[Element, ...] = (
            cast(Element, GENERATES[day_element]),
            cast(Element, CONTROLS[day_element]),
            _inverse_controlling(day_element),
        )
        relations: tuple[str, ...] = ("output", "wealth", "officer")
        confidences: tuple[Confidence, ...] = ("high", "medium", "low")
        direction = "strong"
    else:
        elements = (_inverse_generating(day_element), day_element)
        relations = ("resource", "companion")
        confidences = ("high", "medium")
        direction = "weak"

    return tuple(
        _candidate(
            "support_control",
            element,
            status="computed",
            conclusion=(
                f"{relation} element is a conditional {direction}-chart "
                "support/control candidate"
            ),
            confidence=confidence,
            supporting_signals=(
                f"strength_label:{label}",
                f"day_element:{day_element}",
                f"relation:{relation}",
            ),
            assumptions=("candidate_only:no_unique_final_god",),
            rule_ids=(f"useful_god.support_control.{direction}.{relation}",),
        )
        for element, relation, confidence in zip(
            elements, relations, confidences, strict=True
        )
    )


def _seasonal_adjustment_candidates(
    facts: ChartFacts,
) -> tuple[UsefulGodCandidateResult, ...]:
    if facts.month_branch in WINTER_BRANCHES:
        element = "火"
        season = "winter"
    elif facts.month_branch in SUMMER_BRANCHES:
        element = "水"
        season = "summer"
    else:
        return (
            _candidate(
                "seasonal_adjustment",
                "",
                status="not_computed",
                conclusion="no V1 seasonal rule for spring/autumn month branch",
                confidence="low",
                supporting_signals=(f"month_branch:{facts.month_branch}",),
                rule_ids=("useful_god.seasonal.no_v1_rule_for_spring_autumn",),
            ),
        )
    return (
        _candidate(
            "seasonal_adjustment",
            element,
            status="computed",
            conclusion=f"{season} month conditional adjustment candidate",
            confidence="medium",
            supporting_signals=(f"month_branch:{facts.month_branch}",),
            assumptions=("candidate_only:no_unique_final_god",),
            rule_ids=(f"useful_god.seasonal.{season}",),
        ),
    )


def _element_occurrences(
    facts: ChartFacts,
) -> Mapping[Element, tuple[str, ...]]:
    occurrences: dict[Element, dict[str, None]] = {
        cast(Element, element): {} for element in ELEMENTS
    }
    for exposed_item in facts.exposed_stems:
        element = cast(Element, exposed_item.element)
        occurrences[element][
            f"exposed:{exposed_item.pillar_name}:{exposed_item.stem}:"
            f"{exposed_item.element}"
        ] = None
    for hidden_item in facts.hidden_stems:
        element = cast(Element, hidden_item.element)
        occurrences[element][
            f"hidden:{hidden_item.pillar_name}:{hidden_item.branch}:"
            f"{hidden_item.role}:{hidden_item.stem}:{hidden_item.element}"
        ] = None
    return MappingProxyType(
        {element: tuple(provenance) for element, provenance in occurrences.items()}
    )


def _mediation_candidates(
    facts: ChartFacts,
) -> tuple[UsefulGodCandidateResult, ...]:
    occurrences = _element_occurrences(facts)
    results: list[UsefulGodCandidateResult] = []
    for raw_controller in ELEMENTS:
        controller = cast(Element, raw_controller)
        controlled = cast(Element, CONTROLS[controller])
        bridge = cast(Element, GENERATES[controller])
        controller_provenance = occurrences[controller]
        controlled_provenance = occurrences[controlled]
        if (
            len(controller_provenance) < 2
            or not controlled_provenance
            or occurrences[bridge]
            or GENERATES[bridge] != controlled
        ):
            continue
        summary = (
            f"controller={controller};controller_count="
            f"{len(controller_provenance)};controlled={controlled};"
            f"controlled_count={len(controlled_provenance)};bridge={bridge}"
        )
        results.append(
            _candidate(
                "mediation",
                bridge,
                status="computed",
                conclusion=(
                    f"{bridge} bridges the explicit {controller}->{controlled} "
                    "controlling bottleneck"
                ),
                confidence="medium",
                supporting_signals=(
                    summary,
                    *controller_provenance,
                    *controlled_provenance,
                ),
                assumptions=("candidate_only:no_unique_final_god",),
                rule_ids=(f"useful_god.mediation.{controller}.{controlled}.{bridge}",),
            )
        )
    if results:
        return tuple(results)
    return (
        _candidate(
            "mediation",
            "",
            status="not_computed",
            conclusion="no explicit controlling bottleneck detected",
            confidence="low",
            rule_ids=("useful_god.mediation.no_explicit_bottleneck",),
        ),
    )


def _ten_god_from_provenance(value: str, day_master: str) -> str | None:
    parts = value.split(":")
    if len(parts) == 4 and parts[0] == "exposed":
        _, pillar, stem, ten_god_name = parts
        if pillar not in _PILLARS or not _is_stem(stem):
            return None
    elif len(parts) == 6 and parts[0] == "hidden":
        _, pillar, branch, role, stem, ten_god_name = parts
        if (
            pillar not in _PILLARS
            or not _is_branch(branch)
            or role not in _HIDDEN_ROLES
            or not _is_stem(stem)
            or (stem, role) not in HIDDEN_STEMS[branch]
        ):
            return None
    else:
        return None
    if ten_god_name not in _TEN_GOD_GROUPS:
        return None
    if ten_god(day_master, stem) != ten_god_name:
        return None
    return ten_god_name


def _element_for_ten_god(day_element: Element, ten_god_name: str) -> Element:
    category = _TEN_GOD_GROUPS[ten_god_name]
    if category == "companion":
        return day_element
    if category == "resource":
        return _inverse_generating(day_element)
    if category == "output":
        return cast(Element, GENERATES[day_element])
    if category == "wealth":
        return cast(Element, CONTROLS[day_element])
    return _inverse_controlling(day_element)


def _illness_remedy_candidates(
    day_master: Stem,
    day_element: Element,
    strength: StrengthResult,
    patterns: tuple[PatternCandidateResult, ...],
) -> tuple[UsefulGodCandidateResult, ...]:
    results: list[UsefulGodCandidateResult] = []
    has_trigger = False
    if strength.label in {"强", "弱"}:
        has_trigger = True
        element = (
            cast(Element, GENERATES[day_element])
            if strength.label == "强"
            else _inverse_generating(day_element)
        )
        direction = "strong" if strength.label == "强" else "weak"
        results.append(
            _candidate(
                "illness_remedy",
                element,
                status="computed",
                conclusion=f"first {direction}-chart remedy candidate",
                confidence="low",
                supporting_signals=(f"extreme_strength:{strength.label}",),
                assumptions=("low_confidence_remedy_candidate_only",),
                rule_ids=(f"useful_god.illness_remedy.extreme_{direction}.first",),
            )
        )

    damaged_patterns = tuple(
        item
        for item in patterns
        if item.reasoning.status == "disputed" and item.damage_conditions
    )
    if damaged_patterns:
        has_trigger = True
    for damaged in damaged_patterns:
        derived_from_pattern = False
        for provenance in damaged.rescue_conditions:
            ten_god_name = _ten_god_from_provenance(provenance, day_master)
            if ten_god_name is None:
                continue
            derived_from_pattern = True
            element = _element_for_ten_god(day_element, ten_god_name)
            results.append(
                _candidate(
                    "illness_remedy",
                    element,
                    status="disputed",
                    conclusion=(
                        f"structured rescue for damaged pattern {damaged.pattern_id}"
                    ),
                    confidence="low",
                    supporting_signals=(
                        f"damaged_pattern:{damaged.pattern_id}",
                        provenance,
                    ),
                    opposing_signals=damaged.damage_conditions,
                    assumptions=("low_confidence_remedy_candidate_only",),
                    rule_ids=(
                        "useful_god.illness_remedy.damaged_pattern."
                        f"{damaged.pattern_id}.{ten_god_name}",
                    ),
                )
            )
        if not derived_from_pattern:
            results.append(
                _candidate(
                    "illness_remedy",
                    "",
                    status="indeterminate",
                    conclusion=(
                        "damaged pattern has no derivable rescue element: "
                        f"{damaged.pattern_id}"
                    ),
                    confidence="low",
                    opposing_signals=(
                        f"damaged_pattern:{damaged.pattern_id}",
                        *damaged.damage_conditions,
                    ),
                    missing_inputs=("structured_rescue_ten_god_provenance",),
                    rule_ids=(
                        "useful_god.illness_remedy.rescue_not_derivable."
                        f"{damaged.pattern_id}",
                    ),
                )
            )
    if results:
        return tuple(results)
    if not has_trigger:
        return (
            _candidate(
                "illness_remedy",
                "",
                status="not_computed",
                conclusion="no extreme strength or damaged-pattern trigger",
                confidence="low",
                rule_ids=("useful_god.illness_remedy.no_trigger",),
            ),
        )
    return tuple(results)


def _merge_candidates(
    candidates: tuple[UsefulGodCandidateResult, ...],
) -> UsefulGodCandidateResult:
    first = candidates[0]
    reasonings = tuple(item.reasoning for item in candidates)
    status = cast(
        ComputationStatus,
        max(reasonings, key=lambda item: _STATUS_ORDER[item.status]).status,
    )
    confidence = cast(
        Confidence,
        max(
            reasonings,
            key=lambda item: _CONFIDENCE_ORDER[item.confidence],
        ).confidence,
    )
    merged_sources = (
        tuple(
            f"merged_trace:status={item.status};confidence={item.confidence};"
            f"conclusion={item.conclusion}"
            for item in reasonings
        )
        if len(reasonings) > 1
        else ()
    )
    return UsefulGodCandidateResult(
        method=first.method,
        element=first.element,
        rank=0,
        reasoning=ReasonedResult(
            status=status,
            conclusion=" | ".join(
                _distinct(tuple(item.conclusion for item in reasonings))
            ),
            confidence=confidence,
            supporting_signals=_distinct(
                tuple(
                    signal for item in reasonings for signal in item.supporting_signals
                )
            ),
            opposing_signals=_distinct(
                tuple(signal for item in reasonings for signal in item.opposing_signals)
            ),
            assumptions=_distinct(
                (
                    *(
                        assumption
                        for item in reasonings
                        for assumption in item.assumptions
                    ),
                    *merged_sources,
                )
            ),
            missing_inputs=_distinct(
                tuple(missing for item in reasonings for missing in item.missing_inputs)
            ),
            rule_ids=_distinct(
                tuple(rule_id for item in reasonings for rule_id in item.rule_ids)
            ),
        ),
    )


def _deduplicate_and_rank(
    candidates: tuple[UsefulGodCandidateResult, ...],
) -> tuple[UsefulGodCandidateResult, ...]:
    grouped: dict[tuple[str, str], list[UsefulGodCandidateResult]] = {}
    for candidate in candidates:
        grouped.setdefault((candidate.method, candidate.element), []).append(candidate)
    merged = tuple(_merge_candidates(tuple(group)) for group in grouped.values())
    ordered = sorted(
        merged,
        key=lambda item: (
            _STATUS_ORDER[item.reasoning.status],
            _CONFIDENCE_ORDER[item.reasoning.confidence],
            _METHOD_ORDER[item.method],
            _ELEMENT_ORDER.get(item.element, len(ELEMENTS)),
        ),
    )
    ranked = tuple(
        replace(item, rank=index) for index, item in enumerate(ordered, start=1)
    )
    _validate_outputs(ranked)
    return ranked


def _validate_outputs(
    results: tuple[UsefulGodCandidateResult, ...],
) -> None:
    seen: set[tuple[str, str]] = set()
    for expected_rank, result in enumerate(results, start=1):
        if result.method not in _METHOD_ORDER:
            raise ValueError(f"invalid useful-god method: {result.method!r}")
        if result.element and not _is_element(result.element):
            raise ValueError(f"invalid useful-god element: {result.element!r}")
        _validate_status_and_confidence(
            result.reasoning.status,
            result.reasoning.confidence,
            context="useful-god result",
        )
        key = (result.method, result.element)
        if key in seen:
            raise ValueError(f"duplicate useful-god result key: {key!r}")
        seen.add(key)
        if result.rank != expected_rank:
            raise ValueError("useful-god ranks must be contiguous")


def calculate_useful_god_candidates(
    facts: ChartFacts,
    strength: StrengthResult,
    patterns: tuple[PatternCandidateResult, ...],
) -> tuple[UsefulGodCandidateResult, ...]:
    _validate_status_and_confidence(
        strength.reasoning.status,
        strength.reasoning.confidence,
        context="strength",
    )
    if strength.reasoning.status != "computed":
        return (_blocked_candidate(),)

    day_element = _validate_chart_facts(facts)
    _validate_computed_strength(strength)
    candidates = (
        *_support_control_candidates(day_element, strength),
        *_seasonal_adjustment_candidates(facts),
        *_mediation_candidates(facts),
        *_illness_remedy_candidates(
            cast(Stem, facts.day_master), day_element, strength, patterns
        ),
    )
    return _deduplicate_and_rank(candidates)
