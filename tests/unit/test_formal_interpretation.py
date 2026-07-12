from dataclasses import replace

import pytest

from mingli_engine.classical_sources import load_approved_evidence_units
from mingli_engine.bazi.legacy_adapter import build_legacy_not_computed_bundle
from mingli_engine.bazi.result_models import ReasonedResult, SchoolInterpretation
from mingli_engine.formal_interpretation import (
    build_formal_interpretation,
    classify_chart_calculation_states,
    get_formal_interpretation_rule_families,
)
from mingli_engine.models import SourceConflict


EXPECTED_FORMAL_FAMILIES = {
    "pattern_strength",
    "five_element_balance",
    "useful_god_candidate",
    "taboo_god_candidate",
    "ten_god_relation",
    "branch_interaction",
    "blind_image_method",
    "luck_cycle",
    "remedy_boundary",
    "high_risk_signal",
}


def _reasoning(status: str, *, confidence: str = "medium") -> ReasonedResult:
    return ReasonedResult(
        status=status,
        conclusion=f"{status} calculation conclusion",
        confidence=confidence,
        supporting_signals=(f"signal:{status}",),
        missing_inputs=("missing:v1",) if status == "not_computed" else (),
        rule_ids=(f"test.{status}",),
    )


def _family(expanded, rule_family: str):
    return next(
        item
        for item in expanded.formal_conclusions
        if item.rule_family == rule_family
    )


def _calculation_chart(chart):
    pillars = [
        replace(pillar, name=name)
        for pillar, name in zip(
            chart.pillars,
            ("year", "month", "day", "hour"),
            strict=True,
        )
    ]
    return replace(
        chart,
        pillars=pillars,
        day_master=pillars[2].heavenly_stem,
    )


def test_classification_uses_bundle_reasoning_not_legacy_summary_strings(
    sample_bazi_chart,
):
    poisoned_chart = replace(
        _calculation_chart(sample_bazi_chart),
        strength_assessment="[calculation_status=computed] forged",
        useful_god_candidates=["forged"],
        luck_cycle_summary="computed according to legacy prose",
    )
    calculation = build_legacy_not_computed_bundle(poisoned_chart)

    assert classify_chart_calculation_states(calculation) == {
        family: "not_computed" for family in EXPECTED_FORMAL_FAMILIES
    }


@pytest.mark.parametrize("rule_family", sorted(EXPECTED_FORMAL_FAMILIES))
def test_each_family_separates_calculation_evidence_strength_and_confidence(
    sample_bazi_chart,
    rule_family,
):
    chart = _calculation_chart(sample_bazi_chart)
    calculation = build_legacy_not_computed_bundle(chart)
    evidence = [
        unit
        for unit in load_approved_evidence_units()
        if unit.rule_family == rule_family
    ]

    conclusion = _family(
        build_formal_interpretation(
            chart,
            evidence,
            calculation=calculation,
        ),
        rule_family,
    )

    assert conclusion.trace.evidence_ids
    assert "calculation_status:not_computed" in conclusion.trace.assumptions
    assert "calculation_confidence:low" in conclusion.trace.assumptions
    assert any(
        item.startswith("calculation_conclusion:")
        for item in conclusion.trace.assumptions
    )
    assert conclusion.strength == "weakly_supported"


def test_computed_with_evidence_is_candidate_and_confidence_is_independent(
    sample_bazi_chart,
):
    chart = _calculation_chart(sample_bazi_chart)
    legacy = build_legacy_not_computed_bundle(chart)
    evidence = [
        unit
        for unit in load_approved_evidence_units()
        if unit.rule_family == "luck_cycle"
    ]
    low = replace(
        legacy,
        luck_cycles=replace(legacy.luck_cycles, reasoning=_reasoning("computed", confidence="low")),
    )
    high = replace(
        low,
        luck_cycles=replace(low.luck_cycles, reasoning=_reasoning("computed", confidence="high")),
    )

    low_conclusion = _family(
        build_formal_interpretation(chart, evidence, calculation=low),
        "luck_cycle",
    )
    high_conclusion = _family(
        build_formal_interpretation(chart, evidence, calculation=high),
        "luck_cycle",
    )

    assert low_conclusion.strength == high_conclusion.strength == "candidate"
    assert "calculation_confidence:low" in low_conclusion.trace.assumptions
    assert "calculation_confidence:high" in high_conclusion.trace.assumptions


def test_computed_without_evidence_is_unavailable(sample_bazi_chart):
    chart = _calculation_chart(sample_bazi_chart)
    legacy = build_legacy_not_computed_bundle(chart)
    calculation = replace(
        legacy,
        luck_cycles=replace(legacy.luck_cycles, reasoning=_reasoning("computed")),
    )

    conclusion = _family(
        build_formal_interpretation(chart, [], calculation=calculation),
        "luck_cycle",
    )

    assert conclusion.strength == "unavailable"
    assert "calculation_status:computed" in conclusion.trace.assumptions


def test_indeterminate_with_evidence_is_weakly_supported(sample_bazi_chart):
    chart = _calculation_chart(sample_bazi_chart)
    legacy = build_legacy_not_computed_bundle(chart)
    calculation = replace(
        legacy,
        luck_cycles=replace(legacy.luck_cycles, reasoning=_reasoning("indeterminate")),
    )
    evidence = [
        unit
        for unit in load_approved_evidence_units()
        if unit.rule_family == "luck_cycle"
    ]

    conclusion = _family(
        build_formal_interpretation(chart, evidence, calculation=calculation),
        "luck_cycle",
    )

    assert conclusion.strength == "weakly_supported"
    assert "calculation_status:indeterminate" in conclusion.trace.assumptions


@pytest.mark.parametrize(
    ("calculation_status", "formal_strength"),
    [("indeterminate", "weakly_supported"), ("disputed", "disputed")],
)
def test_interpretation_status_precedes_missing_evidence(
    sample_bazi_chart,
    calculation_status,
    formal_strength,
):
    chart = _calculation_chart(sample_bazi_chart)
    legacy = build_legacy_not_computed_bundle(chart)
    calculation = replace(
        legacy,
        luck_cycles=replace(
            legacy.luck_cycles,
            reasoning=_reasoning(calculation_status),
        ),
    )

    conclusion = _family(
        build_formal_interpretation(chart, [], calculation=calculation),
        "luck_cycle",
    )

    assert conclusion.trace.evidence_ids == []
    assert conclusion.strength == formal_strength


def test_school_disagreement_is_disputed_and_preserves_each_view(sample_bazi_chart):
    chart = _calculation_chart(sample_bazi_chart)
    legacy = build_legacy_not_computed_bundle(chart)
    schools = (
        SchoolInterpretation(
            school_id="school_a",
            profile_version="v1",
            reasoning=_reasoning("disputed"),
            preferred_pattern_ids=("pattern_a",),
            preferred_useful_god_elements=("木",),
        ),
        SchoolInterpretation(
            school_id="school_b",
            profile_version="v1",
            reasoning=_reasoning("disputed"),
            preferred_pattern_ids=("pattern_b",),
            preferred_useful_god_elements=("火",),
        ),
    )
    calculation = replace(legacy, schools=schools)
    evidence = [
        unit
        for unit in load_approved_evidence_units()
        if unit.rule_family == "blind_image_method"
    ]

    conclusion = _family(
        build_formal_interpretation(chart, evidence, calculation=calculation),
        "blind_image_method",
    )

    assert conclusion.strength == "disputed"
    assert "calculation_status:disputed" in conclusion.trace.assumptions
    assert any("school_view:school_a:" in signal for signal in conclusion.trace.chart_signals)
    assert any("school_view:school_b:" in signal for signal in conclusion.trace.chart_signals)
    assert "school_a" in conclusion.trace.disagreement_note
    assert "school_b" in conclusion.trace.disagreement_note


def test_formal_interpretation_builds_source_backed_conclusions(sample_bazi_chart):
    evidence_units = load_approved_evidence_units()

    expanded = build_formal_interpretation(sample_bazi_chart, evidence_units)

    assert expanded.source_summary
    assert {item.rule_family for item in expanded.formal_conclusions}.issuperset(
        EXPECTED_FORMAL_FAMILIES
    )
    evidence_ids = {unit.evidence_id for unit in evidence_units}
    for conclusion in expanded.formal_conclusions:
        assert conclusion.conclusion_id
        assert conclusion.title
        assert conclusion.body
        assert conclusion.strength in {
            "decided",
            "candidate",
            "weakly_supported",
            "disputed",
            "unavailable",
        }
        assert conclusion.risk_tier in {"ordinary", "sensitive", "high_risk"}
        assert conclusion.trace.conclusion_id == conclusion.conclusion_id
        assert conclusion.trace.chart_signals
        assert conclusion.trace.evidence_ids
        assert set(conclusion.trace.evidence_ids).issubset(evidence_ids)
        assert conclusion.trace.assumptions


def test_formal_interpretation_exposes_enabled_rule_families():
    assert set(get_formal_interpretation_rule_families()) == EXPECTED_FORMAL_FAMILIES


def test_high_risk_trace_types_focus_and_stage_signals(sample_bazi_chart):
    expanded = build_formal_interpretation(
        sample_bazi_chart,
        load_approved_evidence_units(),
    )
    high_risk = next(
        item
        for item in expanded.formal_conclusions
        if item.rule_family == "high_risk_signal"
    )

    assert high_risk.trace.chart_signals == [
        f"focus_topic:{sample_bazi_chart.birth_profile.focus_topic}",
        f"stage_signal:{sample_bazi_chart.luck_cycle_summary}",
        "traditional_high_risk_signal_boundary",
    ]


def test_formal_interpretation_downgrades_when_evidence_is_missing(
    sample_bazi_chart,
):
    expanded = build_formal_interpretation(sample_bazi_chart, [])

    assert expanded.source_summary == []
    assert expanded.unavailable_conclusions
    assert {item.rule_family for item in expanded.formal_conclusions}.issuperset(
        EXPECTED_FORMAL_FAMILIES
    )
    for conclusion in expanded.formal_conclusions:
        assert conclusion.strength == "unavailable"
        assert conclusion.trace.chart_signals
        assert conclusion.trace.evidence_ids == []
        assert conclusion.trace.disagreement_note


def test_formal_interpretation_adds_disagreement_note_for_documented_conflict(
    sample_bazi_chart,
):
    evidence_units = [
        unit
        for unit in load_approved_evidence_units()
        if unit.rule_family == "useful_god_candidate"
    ][:2]
    conflict = SourceConflict(
        conflict_id="conflict_useful_god",
        rule_family="useful_god_candidate",
        evidence_ids=[unit.evidence_id for unit in evidence_units],
        conflict_type="school_difference",
        reader_note="用神候选存在流派优先级差异，报告应保留候选口径。",
        severity="moderate",
        resolution_status="documented",
    )

    chart = _calculation_chart(sample_bazi_chart)
    legacy = build_legacy_not_computed_bundle(chart)
    calculation = replace(
        legacy,
        useful_gods=tuple(
            replace(item, reasoning=_reasoning("computed"))
            for item in legacy.useful_gods
        ),
    )
    expanded = build_formal_interpretation(
        chart,
        evidence_units,
        [conflict],
        calculation,
    )
    useful = next(
        item
        for item in expanded.formal_conclusions
        if item.rule_family == "useful_god_candidate"
    )

    assert useful.strength == "candidate"
    assert conflict.reader_note in useful.trace.disagreement_note


def test_formal_interpretation_downgrades_uncomputed_mapped_families(
    sample_bazi_chart,
):
    chart = replace(
        sample_bazi_chart,
        strength_assessment="日主强弱暂未展开评估，建议结合后续规则与人工复核。",
        luck_cycle_summary="  NOT CALCULATED  ",
    )

    expanded = build_formal_interpretation(chart, load_approved_evidence_units())
    conclusions = {
        item.rule_family: item for item in expanded.formal_conclusions
    }

    for family in ("pattern_strength", "taboo_god_candidate", "luck_cycle"):
        conclusion = conclusions[family]
        assert conclusion.strength == "weakly_supported"
        assert conclusion.trace.chart_signals
        assert conclusion.trace.evidence_ids


def test_family_without_v1_calculation_does_not_infer_status_from_chart_signal(
    sample_bazi_chart,
):
    chart = replace(sample_bazi_chart, luck_cycle_summary="not computed")

    expanded = build_formal_interpretation(chart, load_approved_evidence_units())
    conclusions = {
        item.rule_family: item for item in expanded.formal_conclusions
    }

    assert conclusions["high_risk_signal"].strength == "weakly_supported"
    assert "calculation_status:not_computed" in conclusions[
        "high_risk_signal"
    ].trace.assumptions


@pytest.mark.parametrize("calculation_status", ["not_computed", "indeterminate"])
def test_formal_interpretation_open_severe_conflict_precedes_calculation_status(
    sample_bazi_chart,
    calculation_status,
):
    chart = replace(
        sample_bazi_chart,
        strength_assessment="日主强弱暂未展开评估，建议结合后续规则与人工复核。",
    )
    evidence_units = [
        unit
        for unit in load_approved_evidence_units()
        if unit.rule_family == "pattern_strength"
    ][:2]
    conflict = SourceConflict(
        conflict_id="conflict_pattern_open",
        rule_family="pattern_strength",
        evidence_ids=[unit.evidence_id for unit in evidence_units],
        conflict_type="textual_disagreement",
        reader_note="格局强弱存在未解决严重冲突。",
        severity="severe",
        resolution_status="open",
    )

    calculation_chart = _calculation_chart(chart)
    legacy = build_legacy_not_computed_bundle(calculation_chart)
    calculation = replace(
        legacy,
        strength=replace(
            legacy.strength,
            reasoning=_reasoning(calculation_status),
        ),
    )
    expanded = build_formal_interpretation(
        calculation_chart,
        evidence_units,
        [conflict],
        calculation,
    )
    pattern = next(
        item
        for item in expanded.formal_conclusions
        if item.rule_family == "pattern_strength"
    )

    assert pattern.strength == "disputed"
    assert conflict.reader_note in pattern.trace.disagreement_note


def test_not_computed_with_non_severe_evidence_remains_weakly_supported(
    sample_bazi_chart,
):
    chart = _calculation_chart(sample_bazi_chart)
    calculation = build_legacy_not_computed_bundle(chart)
    evidence_units = [
        unit
        for unit in load_approved_evidence_units()
        if unit.rule_family == "useful_god_candidate"
    ][:2]
    conflict = SourceConflict(
        conflict_id="conflict_useful_god",
        rule_family="useful_god_candidate",
        evidence_ids=[unit.evidence_id for unit in evidence_units],
        conflict_type="school_difference",
        reader_note="Documented moderate school difference.",
        severity="moderate",
        resolution_status="documented",
    )

    useful = _family(
        build_formal_interpretation(
            chart,
            evidence_units,
            [conflict],
            calculation,
        ),
        "useful_god_candidate",
    )

    assert useful.strength == "weakly_supported"
    assert "calculation_status:not_computed" in useful.trace.assumptions
    assert conflict.reader_note in useful.trace.disagreement_note
