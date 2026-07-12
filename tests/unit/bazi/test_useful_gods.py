from dataclasses import FrozenInstanceError, replace
from typing import Final, Mapping, TypeGuard

import pytest

from mingli_engine.bazi.constants import (
    ELEMENTS,
    HIDDEN_STEMS,
    STEM_ELEMENT,
    STEM_POLARITY,
    STEMS,
)
from mingli_engine.bazi.facts import Branch, Stem, build_chart_facts, ten_god
from mingli_engine.bazi.patterns import calculate_pattern_candidates
from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    ChartFacts,
    HiddenStemFact,
    PatternCandidateResult,
    RootFact,
    StemFact,
    StrengthResult,
    UsefulGodCandidateResult,
)
from mingli_engine.bazi.strength import (
    Element,
    ElementCategory,
    calculate_strength,
    load_strength_config,
)
from mingli_engine.bazi.useful_gods import (
    SUMMER_BRANCHES,
    WINTER_BRANCHES,
    _blocked_candidate,
    calculate_useful_god_candidates,
)
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile


PILLARS: Final = ("year", "month", "day", "hour")
DEFAULT_BRANCHES: Final[tuple[Branch, Branch, Branch, Branch]] = (
    "子",
    "酉",
    "卯",
    "亥",
)
STRENGTH_CASES: Final[
    Mapping[Stem, Mapping[str, tuple[Branch, tuple[Stem, Stem, Stem]]]]
] = {
    "甲": {
        "强": ("子", ("甲", "甲", "甲")),
        "偏强": ("巳", ("甲", "甲", "甲")),
        "较平衡": ("丑", ("甲", "甲", "庚")),
        "偏弱": ("丑", ("丙", "丙", "丙")),
        "弱": ("巳", ("庚", "庚", "庚")),
    },
    "丙": {
        "强": ("寅", ("甲", "甲", "甲")),
        "弱": ("子", ("戊", "戊", "戊")),
    },
    "戊": {
        "强": ("丑", ("丙", "丙", "丙")),
        "弱": ("子", ("甲", "甲", "甲")),
    },
    "庚": {
        "强": ("丑", ("戊", "戊", "戊")),
        "弱": ("子", ("甲", "甲", "甲")),
    },
    "壬": {
        "强": ("子", ("甲", "甲", "甲")),
        "弱": ("丑", ("戊", "戊", "戊")),
    },
}


def is_stem(value: str) -> TypeGuard[Stem]:
    return value in STEMS


def chart_facts(
    day_master: Stem = "甲",
    *,
    month_branch: Branch = "酉",
    exposed: tuple[Stem, Stem, Stem, Stem] | None = None,
    branches: tuple[Branch, Branch, Branch, Branch] | None = None,
) -> ChartFacts:
    stems = exposed or ("壬", "辛", day_master, "癸")
    active_branches = branches or (
        DEFAULT_BRANCHES[0],
        month_branch,
        DEFAULT_BRANCHES[2],
        DEFAULT_BRANCHES[3],
    )
    exposed_facts = tuple(
        StemFact(
            pillar_name=pillar,
            stem=stem,
            element=STEM_ELEMENT[stem],
            polarity=STEM_POLARITY[stem],
            ten_god=ten_god(day_master, stem),
        )
        for pillar, stem in zip(PILLARS, stems, strict=True)
    )
    hidden_facts = tuple(
        HiddenStemFact(
            pillar_name=pillar,
            branch=branch,
            stem=stem,
            role=role,
            element=STEM_ELEMENT[stem],
            polarity=STEM_POLARITY[stem],
            ten_god=ten_god(day_master, stem),
        )
        for pillar, branch in zip(PILLARS, active_branches, strict=True)
        for stem, role in HIDDEN_STEMS[branch]
    )
    roots = tuple(
        RootFact(
            stem=exposed_item.stem,
            stem_pillar=exposed_item.pillar_name,
            branch=hidden_item.branch,
            branch_pillar=hidden_item.pillar_name,
            role=hidden_item.role,
            exact_stem_root=True,
        )
        for exposed_item in exposed_facts
        for hidden_item in hidden_facts
        if exposed_item.stem == hidden_item.stem
    )
    return ChartFacts(
        day_master=day_master,
        month_branch=month_branch,
        exposed_stems=exposed_facts,
        hidden_stems=hidden_facts,
        roots=roots,
        twelve_growth_by_pillar=(),
        assumptions=("facts:useful-god-test",),
    )


def strength_case(
    day_master: Stem = "甲", label: str = "较平衡"
) -> tuple[ChartFacts, StrengthResult]:
    month_branch, non_day_stems = STRENGTH_CASES[day_master][label]
    facts = chart_facts(
        day_master,
        month_branch=month_branch,
        exposed=(
            non_day_stems[0],
            non_day_stems[1],
            day_master,
            non_day_stems[2],
        ),
    )
    result = calculate_strength(facts)
    assert result.reasoning.status == "computed"
    assert result.label == label
    return facts, result


def computed_month_case(month_branch: Branch) -> tuple[ChartFacts, StrengthResult]:
    for target_stem in STEMS:
        if not is_stem(target_stem):
            raise AssertionError(f"invalid canonical stem {target_stem!r}")
        facts = chart_facts(
            month_branch=month_branch,
            exposed=(target_stem, target_stem, "甲", target_stem),
        )
        result = calculate_strength(facts)
        if result.reasoning.status == "computed":
            return facts, result
    raise AssertionError(f"no computed canonical case for {month_branch}")


def method_results(
    results: tuple[UsefulGodCandidateResult, ...], method: str
) -> tuple[UsefulGodCandidateResult, ...]:
    return tuple(item for item in results if item.method == method)


def damaged_pattern_case(
    *, rescue: bool = True
) -> tuple[ChartFacts, StrengthResult, PatternCandidateResult]:
    exposed: tuple[Stem, Stem, Stem, Stem] = (
        ("甲", "丁", "甲", "壬") if rescue else ("甲", "甲", "甲", "丁")
    )
    facts = chart_facts(exposed=exposed)
    actual_strength = calculate_strength(facts)
    assert actual_strength.reasoning.status == "computed"
    damaged = calculate_pattern_candidates(facts, actual_strength)[0]
    assert damaged.reasoning.status == "disputed"
    assert damaged.damage_conditions
    assert bool(damaged.rescue_conditions) is rescue
    return facts, actual_strength, damaged


def blocked_relation() -> BranchRelationResult:
    return BranchRelationResult(
        relation_type="clash",
        branches=("子", "酉"),
        pillar_names=("year", "month"),
        state="blocked",
        transformed_element="",
        conditions=("both branches present",),
        blockers=("relation effect guarded in V1",),
        rule_id="branch.clash.ziyou.test",
    )


def baseline_patterns(
    facts: ChartFacts, strength: StrengthResult
) -> tuple[PatternCandidateResult, ...]:
    return calculate_pattern_candidates(facts, strength)


def calculate_with_baseline(
    facts: ChartFacts, strength: StrengthResult
) -> tuple[UsefulGodCandidateResult, ...]:
    return calculate_useful_god_candidates(
        facts,
        strength,
        baseline_patterns(facts, strength),
    )


def replace_baseline_pattern(
    baseline: tuple[PatternCandidateResult, ...],
    replacement: PatternCandidateResult,
) -> tuple[PatternCandidateResult, ...]:
    return tuple(
        replacement if item.pattern_id == replacement.pattern_id else item
        for item in baseline
    )


def test_strength_prerequisite_returns_exactly_one_blocked_result() -> None:
    facts = chart_facts(
        month_branch="子",
        exposed=("庚", "庚", "甲", "庚"),
    )
    upstream = calculate_strength(facts)
    assert upstream.reasoning.status == "indeterminate"

    result = calculate_useful_god_candidates(facts, upstream, ())

    assert len(result) == 1
    assert (result[0].method, result[0].element, result[0].rank) == (
        "support_control",
        "",
        1,
    )
    assert result[0].reasoning.status == "not_computed"
    assert result[0].reasoning.missing_inputs == ("strength_not_computed",)
    assert result[0].reasoning.rule_ids == (
        "useful_god.prerequisite.support_control.strength_not_computed",
    )


def test_blocked_candidate_validates_method_and_records_reason() -> None:
    blocked = _blocked_candidate("mediation", "explicit_bottleneck_missing")

    assert (blocked.method, blocked.element, blocked.rank) == ("mediation", "", 0)
    assert blocked.reasoning.status == "not_computed"
    assert blocked.reasoning.missing_inputs == ("explicit_bottleneck_missing",)
    assert blocked.reasoning.rule_ids == (
        "useful_god.prerequisite.mediation.explicit_bottleneck_missing",
    )
    with pytest.raises(ValueError, match="blocked candidate method"):
        _blocked_candidate("invented", "missing")


@pytest.mark.parametrize(
    ("day_master", "strong_expected", "weak_expected"),
    [
        ("甲", ("火", "土", "金"), ("水", "木")),
        ("丙", ("土", "金", "水"), ("木", "火")),
        ("戊", ("金", "水", "木"), ("火", "土")),
        ("庚", ("水", "木", "火"), ("土", "金")),
        ("壬", ("木", "火", "土"), ("金", "水")),
    ],
)
def test_support_control_maps_all_five_day_elements(
    day_master: Stem,
    strong_expected: tuple[Element, ...],
    weak_expected: tuple[Element, ...],
) -> None:
    for label in ("强", "弱"):
        facts, actual_strength = strength_case(day_master, label)
        results = calculate_with_baseline(facts, actual_strength)
        expected = strong_expected if label == "强" else weak_expected
        assert (
            tuple(item.element for item in method_results(results, "support_control"))
            == expected
        )


@pytest.mark.parametrize(
    ("label", "expected"),
    [("偏强", ("火", "土", "金")), ("偏弱", ("水", "木"))],
)
def test_partial_strength_labels_keep_directional_order(
    label: str, expected: tuple[Element, ...]
) -> None:
    facts, actual_strength = strength_case("甲", label)
    results = calculate_with_baseline(facts, actual_strength)
    assert (
        tuple(item.element for item in method_results(results, "support_control"))
        == expected
    )


def test_balanced_strength_has_no_directional_preference() -> None:
    facts, actual_strength = strength_case()
    support = method_results(
        calculate_with_baseline(facts, actual_strength),
        "support_control",
    )
    assert len(support) == 1
    assert support[0].element == ""
    assert support[0].reasoning.status == "indeterminate"
    assert "no directional preference" in support[0].reasoning.conclusion


@pytest.mark.parametrize("label", ("待定", "临界"))
def test_computed_strength_rejects_noncomputed_labels(label: str) -> None:
    facts, actual = strength_case()
    forged = replace(
        actual,
        label=label,
        reasoning=replace(actual.reasoning, conclusion=label),
    )
    with pytest.raises(ValueError, match="computed strength label"):
        calculate_useful_god_candidates(facts, forged, ())


def test_rejects_forged_day_master_element_status_and_label() -> None:
    facts, actual = strength_case()
    forged_day = replace(facts, day_master="丁")
    forged_element = replace(
        facts,
        exposed_stems=(
            replace(facts.exposed_stems[0], element="火"),
            *facts.exposed_stems[1:],
        ),
    )
    forged_label = replace(actual, reasoning=replace(actual.reasoning, conclusion="弱"))
    forged_status = replace(actual, reasoning=replace(actual.reasoning))
    object.__setattr__(forged_status.reasoning, "status", "forged")

    with pytest.raises(ValueError, match="day exposed stem"):
        calculate_useful_god_candidates(forged_day, actual, ())
    with pytest.raises(ValueError, match="element mismatch"):
        calculate_useful_god_candidates(forged_element, actual, ())
    with pytest.raises(ValueError, match="strength status"):
        calculate_useful_god_candidates(facts, forged_status, ())
    with pytest.raises(ValueError, match="strength label consistency"):
        calculate_useful_god_candidates(facts, forged_label, ())


def test_rejects_score_zero_labeled_strong() -> None:
    facts, actual = strength_case("甲", "强")
    forged = replace(actual, score=0.0, lower_bound=0.0, upper_bound=0.0)
    with pytest.raises(ValueError, match="strength contribution sum|classification"):
        calculate_useful_god_candidates(facts, forged, ())


def test_rejects_incomplete_or_nonfinite_computed_strength() -> None:
    facts, actual = strength_case()
    mutations = (
        replace(actual, contributions=()),
        replace(
            actual,
            contributions=(
                replace(actual.contributions[0], value=float("nan")),
                *actual.contributions[1:],
            ),
        ),
        replace(actual, score=float("nan")),
        replace(actual, lower_bound=actual.score + 1.0),
        replace(
            actual,
            reasoning=replace(
                actual.reasoning,
                assumptions=tuple(
                    item
                    for item in actual.reasoning.assumptions
                    if item != "profile_version=ziping-strength-v1"
                ),
            ),
        ),
        replace(
            actual,
            reasoning=replace(
                actual.reasoning,
                rule_ids=actual.reasoning.rule_ids[1:],
            ),
        ),
    )
    for forged in mutations:
        with pytest.raises(ValueError, match="computed strength"):
            calculate_useful_god_candidates(facts, forged, ())


def test_rejects_forged_strength_contribution_despite_consistent_totals() -> None:
    facts, actual = strength_case()
    forged_contribution = replace(
        actual.contributions[0],
        category="forged",
        rule_id="strength.forged.category",
    )
    forged = replace(
        actual,
        contributions=(forged_contribution, *actual.contributions[1:]),
        reasoning=replace(
            actual.reasoning,
            rule_ids=(
                "strength.forged.category",
                *actual.reasoning.rule_ids[1:],
            ),
        ),
    )

    with pytest.raises(ValueError, match="canonical strength mismatch"):
        calculate_useful_god_candidates(facts, forged, ())


def test_rejects_same_version_custom_strength_profile() -> None:
    facts, _actual = strength_case("甲", "强")
    config = load_strength_config()
    custom_exposed: dict[ElementCategory, float] = dict(config.exposed)
    custom_exposed["companion"] += 1.0
    custom = replace(config, exposed=custom_exposed)
    custom_strength = calculate_strength(facts, config=custom)
    assert custom_strength.reasoning.status == "computed"

    with pytest.raises(ValueError, match="canonical strength mismatch"):
        calculate_useful_god_candidates(facts, custom_strength, ())


def test_season_constants_are_immutable_and_exact() -> None:
    assert WINTER_BRANCHES == frozenset({"亥", "子", "丑"})
    assert SUMMER_BRANCHES == frozenset({"巳", "午", "未"})
    assert isinstance(WINTER_BRANCHES, frozenset)
    assert isinstance(SUMMER_BRANCHES, frozenset)


@pytest.mark.parametrize("branch", tuple(WINTER_BRANCHES))
def test_winter_month_nominates_fire(branch: Branch) -> None:
    facts, actual_strength = computed_month_case(branch)
    seasonal = method_results(
        calculate_with_baseline(facts, actual_strength),
        "seasonal_adjustment",
    )
    assert [
        (item.element, item.reasoning.status, item.reasoning.confidence)
        for item in seasonal
    ] == [("火", "computed", "medium")]


@pytest.mark.parametrize("branch", tuple(SUMMER_BRANCHES))
def test_summer_month_nominates_water(branch: Branch) -> None:
    facts, actual_strength = computed_month_case(branch)
    seasonal = method_results(
        calculate_with_baseline(facts, actual_strength),
        "seasonal_adjustment",
    )
    assert [
        (item.element, item.reasoning.status, item.reasoning.confidence)
        for item in seasonal
    ] == [("水", "computed", "medium")]


@pytest.mark.parametrize("branch", ("寅", "卯", "辰", "申", "酉", "戌"))
def test_spring_and_autumn_have_no_v1_seasonal_rule(branch: Branch) -> None:
    facts, actual_strength = computed_month_case(branch)
    seasonal = method_results(
        calculate_with_baseline(facts, actual_strength),
        "seasonal_adjustment",
    )
    assert len(seasonal) == 1
    assert seasonal[0].element == ""
    assert seasonal[0].reasoning.status == "not_computed"
    assert seasonal[0].reasoning.rule_ids == (
        "useful_god.seasonal.no_v1_rule_for_spring_autumn",
    )


def mediation_facts(*, bridge_present: bool = False) -> ChartFacts:
    return chart_facts(
        "壬",
        month_branch="辰",
        exposed=("甲", "乙", "壬", "丙" if bridge_present else "辛"),
        branches=("卯", "辰", "子", "酉"),
    )


def test_mediation_detects_explicit_controlling_bottleneck_with_provenance() -> None:
    facts = mediation_facts()
    actual_strength = calculate_strength(facts)
    assert actual_strength.reasoning.status == "computed"
    mediation = method_results(
        calculate_with_baseline(facts, actual_strength),
        "mediation",
    )
    fire = next(item for item in mediation if item.element == "火")
    trace = " ".join(fire.reasoning.supporting_signals)
    assert "controller=木" in trace
    assert "controlled=土" in trace
    assert "controller_count=" in trace
    assert "controlled_count=" in trace
    assert "exposed:year:甲:木" in trace
    assert "hidden:month:辰:main:戊:土" in trace


def test_mediation_requires_two_controllers_and_absent_bridge() -> None:
    single_controller = chart_facts(
        "壬",
        month_branch="酉",
        exposed=("丙", "辛", "壬", "甲"),
        branches=("子", "酉", "亥", "卯"),
    )
    for facts in (single_controller, mediation_facts(bridge_present=True)):
        actual_strength = calculate_strength(facts)
        assert actual_strength.reasoning.status == "computed"
        mediation = method_results(
            calculate_with_baseline(facts, actual_strength),
            "mediation",
        )
        assert len(mediation) == 1
        assert mediation[0].element == ""
        assert mediation[0].reasoning.status == "not_computed"


def test_rejects_duplicate_hidden_provenance() -> None:
    baseline = chart_facts()
    actual_strength = calculate_strength(baseline)
    duplicated = replace(
        baseline,
        hidden_stems=(*baseline.hidden_stems, baseline.hidden_stems[0]),
    )
    with pytest.raises(ValueError, match="complete canonical hidden stems"):
        calculate_useful_god_candidates(duplicated, actual_strength, ())


def test_rejects_whole_pillar_hidden_omission() -> None:
    baseline = chart_facts()
    actual_strength = calculate_strength(baseline)
    omitted = replace(
        baseline,
        hidden_stems=tuple(
            item for item in baseline.hidden_stems if item.pillar_name != "year"
        ),
    )
    with pytest.raises(ValueError, match="complete canonical hidden stems"):
        calculate_useful_god_candidates(omitted, actual_strength, ())


def test_rejects_reordered_hidden_stems() -> None:
    baseline = chart_facts()
    actual_strength = calculate_strength(baseline)
    reordered = replace(
        baseline,
        hidden_stems=(
            *baseline.hidden_stems[:-2],
            *reversed(baseline.hidden_stems[-2:]),
        ),
    )
    with pytest.raises(ValueError, match="complete canonical hidden stems"):
        calculate_useful_god_candidates(reordered, actual_strength, ())


def test_rejects_omitted_hidden_bridge_occurrence() -> None:
    baseline = chart_facts(
        "壬",
        month_branch="辰",
        exposed=("甲", "乙", "壬", "辛"),
        branches=("卯", "辰", "子", "巳"),
    )
    actual_strength = calculate_strength(baseline)
    assert actual_strength.reasoning.status == "computed"
    omitted_bridge = replace(
        baseline,
        hidden_stems=tuple(
            item
            for item in baseline.hidden_stems
            if not (item.pillar_name == "hour" and item.element == "火")
        ),
    )
    with pytest.raises(ValueError, match="complete canonical hidden stems"):
        calculate_useful_god_candidates(omitted_bridge, actual_strength, ())


def test_rejects_extra_root() -> None:
    facts = chart_facts()
    actual_strength = calculate_strength(facts)
    forged = replace(
        facts,
        roots=(
            *facts.roots,
            replace(facts.roots[0], branch_pillar="forged"),
        ),
    )
    with pytest.raises(ValueError, match="canonical roots"):
        calculate_useful_god_candidates(
            forged,
            actual_strength,
            baseline_patterns(facts, actual_strength),
        )


def test_rejects_missing_root() -> None:
    facts = chart_facts()
    actual_strength = calculate_strength(facts)
    forged = replace(facts, roots=facts.roots[1:])
    with pytest.raises(ValueError, match="canonical roots"):
        calculate_useful_god_candidates(
            forged,
            actual_strength,
            baseline_patterns(facts, actual_strength),
        )


def test_rejects_duplicate_root() -> None:
    facts = chart_facts()
    actual_strength = calculate_strength(facts)
    forged = replace(facts, roots=(*facts.roots, facts.roots[0]))
    with pytest.raises(ValueError, match="canonical roots"):
        calculate_useful_god_candidates(
            forged,
            actual_strength,
            baseline_patterns(facts, actual_strength),
        )


def test_rejects_reordered_roots() -> None:
    facts = chart_facts()
    actual_strength = calculate_strength(facts)
    forged = replace(facts, roots=tuple(reversed(facts.roots)))
    with pytest.raises(ValueError, match="canonical roots"):
        calculate_useful_god_candidates(
            forged,
            actual_strength,
            baseline_patterns(facts, actual_strength),
        )


def test_repeated_exposed_stem_preserves_root_multiplicity() -> None:
    facts = chart_facts(exposed=("甲", "甲", "甲", "甲"))
    actual_strength = calculate_strength(facts)
    assert tuple(root.stem_pillar for root in facts.roots) == PILLARS

    results = calculate_useful_god_candidates(
        facts,
        actual_strength,
        baseline_patterns(facts, actual_strength),
    )

    assert results


@pytest.mark.parametrize(("label", "expected"), (("强", "火"), ("弱", "水")))
def test_illness_remedy_extremes_use_first_directional_candidate(
    label: str, expected: Element
) -> None:
    facts, actual_strength = strength_case("甲", label)
    illness = method_results(
        calculate_with_baseline(facts, actual_strength),
        "illness_remedy",
    )
    assert len(illness) == 1
    assert illness[0].element == expected
    assert illness[0].reasoning.confidence == "low"
    assert f"extreme_strength:{label}" in illness[0].reasoning.supporting_signals


def test_illness_remedy_uses_structured_rescue_ten_god_provenance() -> None:
    facts, actual_strength, damaged = damaged_pattern_case()
    illness = method_results(
        calculate_useful_god_candidates(facts, actual_strength, (damaged,)),
        "illness_remedy",
    )
    assert len(illness) == 1
    assert illness[0].element == "水"
    assert illness[0].reasoning.status == "disputed"
    assert illness[0].reasoning.confidence == "low"
    assert damaged.rescue_conditions[0] in illness[0].reasoning.supporting_signals


def test_damaged_pattern_without_rescue_is_indeterminate() -> None:
    facts, actual_strength, damaged = damaged_pattern_case(rescue=False)
    illness = method_results(
        calculate_useful_god_candidates(facts, actual_strength, (damaged,)),
        "illness_remedy",
    )
    assert len(illness) == 1
    assert illness[0].element == ""
    assert illness[0].reasoning.status == "indeterminate"
    assert illness[0].reasoning.confidence == "low"


def test_rejects_prose_and_forged_rescue_provenance() -> None:
    facts, actual_strength, damaged = damaged_pattern_case()
    for rescue in (
        ("choose water because prose says so",),
        ("exposed:year:丙:食神",),
    ):
        forged = replace(
            damaged,
            rescue_conditions=rescue,
            reasoning=replace(
                damaged.reasoning,
                supporting_signals=rescue,
            ),
        )
        with pytest.raises(ValueError, match="rescue condition provenance"):
            calculate_useful_god_candidates(facts, actual_strength, (forged,))


@pytest.mark.parametrize("remove_supporting", (True, False))
def test_rejects_pattern_conditions_missing_reasoning_trace(
    remove_supporting: bool,
) -> None:
    facts, actual_strength, damaged = damaged_pattern_case()
    if remove_supporting:
        reasoning = replace(damaged.reasoning, supporting_signals=())
    else:
        reasoning = replace(damaged.reasoning, opposing_signals=())
    missing_trace = replace(damaged, reasoning=reasoning)
    with pytest.raises(ValueError, match="reasoning supporting|reasoning opposing"):
        calculate_useful_god_candidates(facts, actual_strength, (missing_trace,))


def test_rejects_fabricated_pattern_using_present_unrelated_tokens() -> None:
    facts, actual_strength, expected = damaged_pattern_case()
    unrelated_damage = "exposed:year:甲:比肩"
    assert unrelated_damage in {
        f"exposed:{item.pillar_name}:{item.stem}:{item.ten_god}"
        for item in facts.exposed_stems
    }
    fabricated = replace(
        expected,
        damage_conditions=(unrelated_damage,),
        reasoning=replace(
            expected.reasoning,
            opposing_signals=(unrelated_damage,),
        ),
    )

    with pytest.raises(ValueError, match="canonical pattern mismatch"):
        calculate_useful_god_candidates(facts, actual_strength, (fabricated,))


def test_rejects_forged_nonprovenance_damage_with_present_rescue() -> None:
    facts, actual_strength, expected = damaged_pattern_case()
    fabricated = replace(
        expected,
        damage_conditions=("countercondition:forged",),
        reasoning=replace(
            expected.reasoning,
            opposing_signals=("countercondition:forged",),
        ),
    )
    assert expected.rescue_conditions

    with pytest.raises(ValueError, match="canonical pattern mismatch"):
        calculate_useful_god_candidates(facts, actual_strength, (fabricated,))


def test_rejects_illness_pattern_absent_from_recomputed_baseline() -> None:
    facts, actual_strength, expected = damaged_pattern_case()
    fabricated = replace(
        expected,
        pattern_id="fabricated.present_tokens",
        name="伪造格",
    )

    with pytest.raises(ValueError, match="canonical pattern sequence"):
        calculate_useful_god_candidates(facts, actual_strength, (fabricated,))


def test_rejects_omitted_canonical_damaged_pattern() -> None:
    facts, actual_strength, damaged = damaged_pattern_case()
    baseline = baseline_patterns(facts, actual_strength)
    supplied = tuple(item for item in baseline if item.pattern_id != damaged.pattern_id)
    assert len(supplied) + 1 == len(baseline)

    with pytest.raises(ValueError, match="canonical pattern sequence"):
        calculate_useful_god_candidates(facts, actual_strength, supplied)


def test_rejects_invalid_pattern_identity() -> None:
    facts, actual_strength, damaged = damaged_pattern_case()
    invalid_identity = replace(damaged, pattern_id="", rank=0)

    with pytest.raises(ValueError, match="canonical pattern sequence"):
        calculate_useful_god_candidates(facts, actual_strength, (invalid_identity,))


def test_nondisputed_structural_countercondition_is_not_a_damage_trigger() -> None:
    facts, actual_strength = strength_case("甲", "弱")
    guarded = next(
        item
        for item in calculate_pattern_candidates(facts, actual_strength)
        if item.pattern_id == "follow.congruo"
    )
    supplied = replace_baseline_pattern(
        baseline_patterns(facts, actual_strength), guarded
    )

    illness = method_results(
        calculate_useful_god_candidates(facts, actual_strength, supplied),
        "illness_remedy",
    )

    assert len(illness) == 1
    assert illness[0].element == "水"
    assert illness[0].reasoning.status == "computed"
    assert illness[0].reasoning.supporting_signals == ("extreme_strength:弱",)


def test_guarded_follow_cannot_create_remedy_trigger() -> None:
    facts, actual_strength = strength_case("甲", "弱")
    canonical_patterns = baseline_patterns(facts, actual_strength)
    canonical_results = calculate_useful_god_candidates(
        facts, actual_strength, canonical_patterns
    )
    relation = replace(
        blocked_relation(),
        branches=("子", "巳"),
        rule_id="branch.clash.zisi.test",
    )
    guarded_patterns = calculate_pattern_candidates(facts, actual_strength, (relation,))
    guarded_follow = next(
        item for item in guarded_patterns if item.pattern_id == "follow.congruo"
    )
    assert guarded_follow.reasoning.status == "indeterminate"
    disputed_follow = replace(
        guarded_follow,
        reasoning=replace(guarded_follow.reasoning, status="disputed"),
    )
    supplied = replace_baseline_pattern(guarded_patterns, disputed_follow)

    guarded_results = calculate_useful_god_candidates(facts, actual_strength, supplied)

    assert guarded_results == canonical_results
    assert len(method_results(guarded_results, "illness_remedy")) == len(
        method_results(canonical_results, "illness_remedy")
    )


def test_rejects_nondisputed_provenance_shaped_damage() -> None:
    facts, actual_strength, damaged = damaged_pattern_case()
    forged = replace(
        damaged,
        reasoning=replace(damaged.reasoning, status="computed"),
    )

    with pytest.raises(ValueError, match="canonical pattern mismatch"):
        calculate_useful_god_candidates(facts, actual_strength, (forged,))


def test_each_damaged_pattern_keeps_its_unresolved_rescue_trace() -> None:
    facts = chart_facts(
        month_branch="丑",
        exposed=("甲", "丁", "甲", "辛"),
    )
    actual_strength = calculate_strength(facts)
    patterns = baseline_patterns(facts, actual_strength)
    damaged_patterns = tuple(
        item
        for item in patterns
        if item.reasoning.status == "disputed" and item.damage_conditions
    )
    assert len(damaged_patterns) == 2

    illness = method_results(
        calculate_useful_god_candidates(facts, actual_strength, patterns),
        "illness_remedy",
    )

    assert any(item.element for item in illness)
    empty = next(item for item in illness if item.element == "")
    assert empty.reasoning.status == "indeterminate"
    assert "damaged_pattern:standard.zhengguan" in empty.reasoning.opposing_signals


def test_illness_remedy_without_trigger_is_not_computed() -> None:
    facts, actual_strength = strength_case("甲", "偏强")
    illness = method_results(
        calculate_with_baseline(facts, actual_strength),
        "illness_remedy",
    )
    assert len(illness) == 1
    assert illness[0].element == ""
    assert illness[0].reasoning.status == "not_computed"
    assert illness[0].reasoning.confidence == "low"


def test_duplicate_illness_candidates_merge_traces_conservatively() -> None:
    facts = chart_facts(
        month_branch="寅",
        exposed=("甲", "丙", "甲", "戊"),
    )
    actual_strength = calculate_strength(facts)
    assert (actual_strength.reasoning.status, actual_strength.label) == (
        "computed",
        "强",
    )
    patterns = baseline_patterns(facts, actual_strength)
    damaged = next(item for item in patterns if item.pattern_id == "standard.piancai")
    illness = method_results(
        calculate_useful_god_candidates(facts, actual_strength, patterns),
        "illness_remedy",
    )
    fire = tuple(item for item in illness if item.element == "火")
    assert len(fire) == 1
    assert fire[0].reasoning.status == "disputed"
    assert fire[0].reasoning.confidence == "low"
    assert "extreme_strength:强" in fire[0].reasoning.supporting_signals
    assert damaged.rescue_conditions[0] in fire[0].reasoning.supporting_signals


def test_results_are_unique_ranked_deterministically_and_do_not_mutate_inputs() -> None:
    facts = mediation_facts()
    upstream_strength = calculate_strength(facts)
    assert upstream_strength.reasoning.status == "computed"
    patterns = calculate_pattern_candidates(facts, upstream_strength)
    before = (facts, upstream_strength, patterns)

    first = calculate_useful_god_candidates(facts, upstream_strength, patterns)
    second = calculate_useful_god_candidates(facts, upstream_strength, patterns)

    assert first == second
    assert before == (facts, upstream_strength, patterns)
    assert tuple(item.rank for item in first) == tuple(range(1, len(first) + 1))
    assert len({(item.method, item.element) for item in first}) == len(first)
    with pytest.raises(FrozenInstanceError):
        setattr(first[0], "rank", 99)

    status_order = {"computed": 0, "indeterminate": 1, "disputed": 2, "not_computed": 3}
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    method_order = {
        "support_control": 0,
        "seasonal_adjustment": 1,
        "mediation": 2,
        "illness_remedy": 3,
    }
    element_order = {element: index for index, element in enumerate(ELEMENTS)}
    expected = sorted(
        first,
        key=lambda item: (
            status_order[item.reasoning.status],
            confidence_order[item.reasoning.confidence],
            method_order[item.method],
            element_order.get(item.element, len(ELEMENTS)),
        ),
    )
    assert list(first) == expected


def test_actual_blocked_relation_strength_and_patterns_are_supported() -> None:
    facts, _baseline_strength, _damaged = damaged_pattern_case()
    relation = blocked_relation()
    related_strength = calculate_strength(facts, (relation,))
    related_patterns = calculate_pattern_candidates(
        facts, related_strength, (relation,)
    )
    assert related_strength.reasoning.status == "computed"
    assert any(
        rule_id.startswith("strength.relation.")
        for rule_id in related_strength.reasoning.rule_ids
    )
    assert any(
        rule_id.startswith("pattern.relation.")
        for item in related_patterns
        for rule_id in item.reasoning.rule_ids
    )

    results = calculate_useful_god_candidates(facts, related_strength, related_patterns)

    assert results


def test_documented_relation_guard_may_make_pattern_more_conservative() -> None:
    facts, _baseline_strength, _damaged = damaged_pattern_case()
    relation = blocked_relation()
    related_strength = calculate_strength(facts, (relation,))
    related_patterns = calculate_pattern_candidates(
        facts, related_strength, (relation,)
    )
    related_damaged = next(
        item
        for item in related_patterns
        if item.reasoning.status == "disputed" and item.damage_conditions
    )
    guarded = replace(
        related_damaged,
        reasoning=replace(
            related_damaged.reasoning,
            status="not_computed",
            confidence="low",
        ),
    )
    supplied = replace_baseline_pattern(related_patterns, guarded)

    results = calculate_useful_god_candidates(facts, related_strength, supplied)

    illness = method_results(results, "illness_remedy")
    assert len(illness) == 1
    assert illness[0].reasoning.status == "disputed"


def test_actual_facts_strength_pattern_pipeline_is_supported() -> None:
    chart = calculate_bazi_chart(
        BirthProfile(
            calendar_type="gregorian",
            birth_date="1992-08-18",
            birth_time="09:30",
            birthplace="上海市",
            gender="未指定",
            focus_topic="整体结构观察",
        )
    )
    facts = build_chart_facts(chart)
    actual_strength = calculate_strength(facts)
    patterns = calculate_pattern_candidates(facts, actual_strength)

    results = calculate_useful_god_candidates(facts, actual_strength, patterns)

    assert results
    assert all(
        item.reasoning.status
        in {"computed", "indeterminate", "disputed", "not_computed"}
        for item in results
    )
    assert all(item.element in {*ELEMENTS, ""} for item in results)
