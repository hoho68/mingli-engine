from mingli_engine.classical_sources import load_approved_evidence_units
from mingli_engine.formal_interpretation import build_formal_interpretation


EXPECTED_FORMAL_FAMILIES = {
    "pattern_strength",
    "five_element_balance",
    "ten_god_relation",
    "branch_interaction",
    "blind_image_method",
    "luck_cycle",
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
