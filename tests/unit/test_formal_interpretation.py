from mingli_engine.classical_sources import load_approved_evidence_units
from mingli_engine.formal_interpretation import build_formal_interpretation
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


def test_formal_interpretation_marks_open_severe_conflict_disputed(
    sample_bazi_chart,
):
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

    expanded = build_formal_interpretation(sample_bazi_chart, evidence_units, [conflict])
    pattern = next(
        item
        for item in expanded.formal_conclusions
        if item.rule_family == "pattern_strength"
    )

    assert pattern.strength == "disputed"
    assert conflict.reader_note in pattern.trace.disagreement_note
