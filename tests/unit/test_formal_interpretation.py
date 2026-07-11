from dataclasses import replace

import pytest

from mingli_engine.classical_sources import load_approved_evidence_units
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


def test_classifies_current_sample_chart_calculation_states(sample_bazi_chart):
    assert classify_chart_calculation_states(sample_bazi_chart) == {
        "pattern_strength": "computed",
        "useful_god_candidate": "computed",
        "taboo_god_candidate": "not_computed",
        "luck_cycle": "computed",
    }


def test_classifies_current_calculator_placeholders_as_not_computed(
    sample_bazi_chart,
):
    chart = replace(
        sample_bazi_chart,
        strength_assessment="日主强弱暂未展开评估，建议结合后续规则与人工复核。",
        luck_cycle_summary="大运流年暂未计算，当前结果仅覆盖本命四柱。",
    )

    states = classify_chart_calculation_states(chart)

    assert states["pattern_strength"] == "not_computed"
    assert states["luck_cycle"] == "not_computed"


@pytest.mark.parametrize("marker", ["  NOT CALCULATED  ", "  NoT CoMpUtEd  "])
def test_classifies_english_markers_case_insensitively(
    sample_bazi_chart,
    marker,
):
    chart = replace(
        sample_bazi_chart,
        strength_assessment=marker,
        luck_cycle_summary=marker,
    )

    states = classify_chart_calculation_states(chart)

    assert states["pattern_strength"] == "not_computed"
    assert states["luck_cycle"] == "not_computed"


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

    expanded = build_formal_interpretation(sample_bazi_chart, evidence_units, [conflict])
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


def test_unmapped_family_retains_chart_signal_strength_logic(sample_bazi_chart):
    chart = replace(sample_bazi_chart, luck_cycle_summary="not computed")

    expanded = build_formal_interpretation(chart, load_approved_evidence_units())
    conclusions = {
        item.rule_family: item for item in expanded.formal_conclusions
    }

    assert conclusions["high_risk_signal"].strength == "candidate"


def test_formal_interpretation_marks_open_severe_conflict_disputed(
    sample_bazi_chart,
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

    expanded = build_formal_interpretation(chart, evidence_units, [conflict])
    pattern = next(
        item
        for item in expanded.formal_conclusions
        if item.rule_family == "pattern_strength"
    )

    assert pattern.strength == "disputed"
    assert conflict.reader_note in pattern.trace.disagreement_note
