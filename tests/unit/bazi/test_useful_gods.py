from dataclasses import FrozenInstanceError, replace

import pytest

from mingli_engine.bazi.constants import (
    ELEMENTS,
    HIDDEN_STEMS,
    STEM_ELEMENT,
    STEM_POLARITY,
)
from mingli_engine.bazi.facts import build_chart_facts, ten_god
from mingli_engine.bazi.patterns import calculate_pattern_candidates
from mingli_engine.bazi.result_models import (
    ChartFacts,
    ComputationStatus,
    HiddenStemFact,
    PatternCandidateResult,
    ReasonedResult,
    StemFact,
    StrengthResult,
)
from mingli_engine.bazi.strength import calculate_strength
from mingli_engine.bazi.useful_gods import (
    SUMMER_BRANCHES,
    WINTER_BRANCHES,
    calculate_useful_god_candidates,
)
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile


PILLARS = ("year", "month", "day", "hour")
DEFAULT_BRANCHES = ("子", "酉", "卯", "亥")


def chart_facts(
    day_master: str = "甲",
    *,
    month_branch: str = "酉",
    exposed: tuple[str, str, str, str] | None = None,
    branches: tuple[str, str, str, str] | None = None,
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
    return ChartFacts(
        day_master=day_master,
        month_branch=month_branch,
        exposed_stems=exposed_facts,
        hidden_stems=hidden_facts,
        roots=(),
        twelve_growth_by_pillar=(),
        assumptions=("facts:useful-god-test",),
    )


def strength(
    label: str = "较平衡",
    *,
    status: ComputationStatus = "computed",
) -> StrengthResult:
    return StrengthResult(
        reasoning=ReasonedResult(
            status=status,
            conclusion=label,
            confidence="high" if status == "computed" else "low",
            rule_ids=("strength.useful_god_test",),
        ),
        score=0.0,
        lower_bound=0.0,
        upper_bound=0.0,
        label=label,
        contributions=(),
    )


def pattern(
    *,
    damage: tuple[str, ...] = (),
    rescue: tuple[str, ...] = (),
    status: ComputationStatus = "disputed",
) -> PatternCandidateResult:
    return PatternCandidateResult(
        pattern_id="test.damaged",
        name="测试受损格",
        rank=1,
        reasoning=ReasonedResult(
            status=status,
            conclusion="damaged test pattern",
            confidence="low",
            rule_ids=("pattern.test.damaged",),
        ),
        formation_conditions=("formation:test",),
        damage_conditions=damage,
        rescue_conditions=rescue,
    )


def method_results(results, method: str):
    return tuple(item for item in results if item.method == method)


def test_strength_prerequisite_returns_exactly_one_blocked_result() -> None:
    result = calculate_useful_god_candidates(
        chart_facts(month_branch="子"),
        strength("临界", status="indeterminate"),
        (),
    )

    assert len(result) == 1
    assert (result[0].method, result[0].element, result[0].rank) == (
        "support_control",
        "",
        1,
    )
    assert result[0].reasoning.status == "not_computed"
    assert result[0].reasoning.missing_inputs == ("strength_computed",)
    assert result[0].reasoning.rule_ids == (
        "useful_god.prerequisite.strength_computed",
    )


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
    day_master: str,
    strong_expected: tuple[str, ...],
    weak_expected: tuple[str, ...],
) -> None:
    facts = chart_facts(day_master, exposed=("壬", "辛", day_master, "癸"))

    for label in ("强", "偏强"):
        results = calculate_useful_god_candidates(facts, strength(label), ())
        assert (
            tuple(item.element for item in method_results(results, "support_control"))
            == strong_expected
        )
    for label in ("弱", "偏弱"):
        results = calculate_useful_god_candidates(facts, strength(label), ())
        assert (
            tuple(item.element for item in method_results(results, "support_control"))
            == weak_expected
        )


def test_balanced_strength_has_no_directional_preference() -> None:
    support = method_results(
        calculate_useful_god_candidates(chart_facts(), strength(), ()),
        "support_control",
    )
    assert len(support) == 1
    assert support[0].element == ""
    assert support[0].reasoning.status == "indeterminate"
    assert "no directional preference" in support[0].reasoning.conclusion


@pytest.mark.parametrize("label", ("待定", "临界", "unknown"))
def test_computed_strength_rejects_noncomputed_labels(label: str) -> None:
    with pytest.raises(ValueError, match="computed strength label"):
        calculate_useful_god_candidates(chart_facts(), strength(label), ())


def test_rejects_forged_day_master_element_status_and_label() -> None:
    facts = chart_facts()
    forged_day = replace(facts, day_master="丁")
    forged_element = replace(
        facts,
        exposed_stems=(
            replace(facts.exposed_stems[0], element="火"),
            *facts.exposed_stems[1:],
        ),
    )
    forged_status = strength()
    object.__setattr__(forged_status.reasoning, "status", "forged")
    forged_label = replace(
        strength("强"), reasoning=replace(strength("强").reasoning, conclusion="弱")
    )

    with pytest.raises(ValueError, match="day exposed stem"):
        calculate_useful_god_candidates(forged_day, strength(), ())
    with pytest.raises(ValueError, match="element mismatch"):
        calculate_useful_god_candidates(forged_element, strength(), ())
    with pytest.raises(ValueError, match="strength status"):
        calculate_useful_god_candidates(facts, forged_status, ())
    with pytest.raises(ValueError, match="strength label consistency"):
        calculate_useful_god_candidates(facts, forged_label, ())


def test_season_constants_are_immutable_and_exact() -> None:
    assert WINTER_BRANCHES == frozenset({"亥", "子", "丑"})
    assert SUMMER_BRANCHES == frozenset({"巳", "午", "未"})
    assert isinstance(WINTER_BRANCHES, frozenset)
    assert isinstance(SUMMER_BRANCHES, frozenset)


@pytest.mark.parametrize("branch", tuple(WINTER_BRANCHES))
def test_winter_month_nominates_fire(branch: str) -> None:
    seasonal = method_results(
        calculate_useful_god_candidates(
            chart_facts(month_branch=branch), strength(), ()
        ),
        "seasonal_adjustment",
    )
    assert [
        (item.element, item.reasoning.status, item.reasoning.confidence)
        for item in seasonal
    ] == [("火", "computed", "medium")]


@pytest.mark.parametrize("branch", tuple(SUMMER_BRANCHES))
def test_summer_month_nominates_water(branch: str) -> None:
    seasonal = method_results(
        calculate_useful_god_candidates(
            chart_facts(month_branch=branch), strength(), ()
        ),
        "seasonal_adjustment",
    )
    assert [
        (item.element, item.reasoning.status, item.reasoning.confidence)
        for item in seasonal
    ] == [("水", "computed", "medium")]


@pytest.mark.parametrize("branch", ("寅", "卯", "辰", "申", "酉", "戌"))
def test_spring_and_autumn_have_no_v1_seasonal_rule(branch: str) -> None:
    seasonal = method_results(
        calculate_useful_god_candidates(
            chart_facts(month_branch=branch), strength(), ()
        ),
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
    mediation = method_results(
        calculate_useful_god_candidates(mediation_facts(), strength(), ()),
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
        mediation = method_results(
            calculate_useful_god_candidates(facts, strength(), ()),
            "mediation",
        )
        assert len(mediation) == 1
        assert mediation[0].element == ""
        assert mediation[0].reasoning.status == "not_computed"


def test_mediation_deduplicates_identical_provenance() -> None:
    baseline = mediation_facts()
    duplicated = replace(
        baseline,
        hidden_stems=(*baseline.hidden_stems, baseline.hidden_stems[0]),
    )
    expected = method_results(
        calculate_useful_god_candidates(baseline, strength(), ()), "mediation"
    )
    actual = method_results(
        calculate_useful_god_candidates(duplicated, strength(), ()), "mediation"
    )
    assert actual == expected


@pytest.mark.parametrize(("label", "expected"), (("强", "火"), ("弱", "水")))
def test_illness_remedy_extremes_use_first_directional_candidate(
    label: str, expected: str
) -> None:
    illness = method_results(
        calculate_useful_god_candidates(chart_facts(), strength(label), ()),
        "illness_remedy",
    )
    assert len(illness) == 1
    assert illness[0].element == expected
    assert illness[0].reasoning.confidence == "low"
    assert f"extreme_strength:{label}" in illness[0].reasoning.supporting_signals


def test_illness_remedy_uses_structured_rescue_ten_god_provenance() -> None:
    damaged = pattern(
        damage=("exposed:year:丁:伤官",),
        rescue=("exposed:month:癸:正印",),
    )
    illness = method_results(
        calculate_useful_god_candidates(chart_facts(), strength(), (damaged,)),
        "illness_remedy",
    )
    assert len(illness) == 1
    assert illness[0].element == "水"
    assert illness[0].reasoning.status == "disputed"
    assert illness[0].reasoning.confidence == "low"
    assert damaged.rescue_conditions[0] in illness[0].reasoning.supporting_signals


@pytest.mark.parametrize("rescue", ((), ("choose water because prose says so",)))
def test_damaged_pattern_without_derivable_rescue_is_indeterminate(
    rescue: tuple[str, ...],
) -> None:
    illness = method_results(
        calculate_useful_god_candidates(
            chart_facts(),
            strength(),
            (pattern(damage=("exposed:year:丁:伤官",), rescue=rescue),),
        ),
        "illness_remedy",
    )
    assert len(illness) == 1
    assert illness[0].element == ""
    assert illness[0].reasoning.status == "indeterminate"
    assert illness[0].reasoning.confidence == "low"


def test_each_damaged_pattern_keeps_its_unresolved_rescue_trace() -> None:
    resolved = pattern(
        damage=("exposed:year:丁:伤官",),
        rescue=("exposed:month:癸:正印",),
    )
    unresolved = replace(
        pattern(damage=("exposed:hour:乙:劫财",)),
        pattern_id="test.unresolved",
    )

    illness = method_results(
        calculate_useful_god_candidates(
            chart_facts(), strength(), (resolved, unresolved)
        ),
        "illness_remedy",
    )

    assert any(item.element == "水" for item in illness)
    empty = next(item for item in illness if item.element == "")
    assert empty.reasoning.status == "indeterminate"
    assert "damaged_pattern:test.unresolved" in empty.reasoning.opposing_signals


def test_illness_remedy_without_trigger_is_not_computed() -> None:
    illness = method_results(
        calculate_useful_god_candidates(chart_facts(), strength("偏强"), ()),
        "illness_remedy",
    )
    assert len(illness) == 1
    assert illness[0].element == ""
    assert illness[0].reasoning.status == "not_computed"
    assert illness[0].reasoning.confidence == "low"


def test_duplicate_illness_candidates_merge_traces_conservatively() -> None:
    damaged = pattern(
        damage=("exposed:month:辛:正官",),
        rescue=("exposed:year:丙:食神",),
    )
    illness = method_results(
        calculate_useful_god_candidates(chart_facts(), strength("强"), (damaged,)),
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
    upstream_strength = strength("强")
    patterns = (
        pattern(
            damage=("exposed:month:乙:伤官",),
            rescue=("exposed:hour:辛:正印",),
        ),
    )
    before = (facts, upstream_strength, patterns)

    first = calculate_useful_god_candidates(facts, upstream_strength, patterns)
    second = calculate_useful_god_candidates(facts, upstream_strength, patterns)

    assert first == second
    assert before == (facts, upstream_strength, patterns)
    assert tuple(item.rank for item in first) == tuple(range(1, len(first) + 1))
    assert len({(item.method, item.element) for item in first}) == len(first)
    with pytest.raises(FrozenInstanceError):
        first[0].rank = 99  # type: ignore[misc]

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
