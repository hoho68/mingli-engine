from datetime import datetime

from mingli_engine.bazi import analyze_bazi_chart
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.report_schema import build_report


def _calculation_chart(chart):
    return calculate_bazi_chart(chart.birth_profile)


def test_reasoned_calculation_reaches_formal_evidence_and_audit(sample_bazi_chart):
    chart = _calculation_chart(sample_bazi_chart)
    calculation = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1990, 1, 1, 8, 30),
        selected_year=2030,
    )

    report = build_report(chart, calculation)

    conclusions = {
        item.rule_family: item for item in report.expanded_evidence.formal_conclusions
    }
    audit = report.report_evidence_audit
    assert len(conclusions) == 10
    assert audit.traced_evidence_unit_count == 111
    assert (
        audit.computed_rule_family_count
        + audit.indeterminate_rule_family_count
        + audit.disputed_rule_family_count
        + audit.not_computed_rule_family_count
        == 10
    )
    assert conclusions["luck_cycle"].strength in {"candidate", "disputed"}
    assert "calculation_status:computed" in conclusions["luck_cycle"].trace.assumptions
    assert conclusions["taboo_god_candidate"].strength == "weakly_supported"
    assert "calculation_status:not_computed" in conclusions[
        "taboo_god_candidate"
    ].trace.assumptions
    school_signals = conclusions["blind_image_method"].trace.chart_signals
    assert {signal.split(":", 2)[1] for signal in school_signals if signal.startswith("school_view:")} == {
        item.school_id for item in calculation.schools
    }
    assert report.knowledge_activation.open_conflicts


def test_reasoned_report_keeps_approved_evidence_and_guardrails(sample_bazi_chart):
    chart = _calculation_chart(sample_bazi_chart)
    calculation = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1990, 1, 1, 8, 30),
        selected_year=2030,
    )

    report = build_report(chart, calculation)

    evidence_ids = {
        evidence_id
        for conclusion in report.expanded_evidence.formal_conclusions
        for evidence_id in conclusion.trace.evidence_ids
    }
    assert len(evidence_ids) == 111
    assert report.expanded_evidence.high_risk_notes
    assert report.report_evidence_audit.guardrail_count > 0
    assert report.safety_review.disclaimer_present is True
