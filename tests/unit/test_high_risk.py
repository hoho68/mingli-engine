from dataclasses import replace

from mingli_engine.high_risk import classify_high_risk_request
from mingli_engine.report_schema import build_report


def test_general_high_risk_request_is_narrowed_to_signal_analysis():
    review = classify_high_risk_request("请看寿命与健康风险的传统信号，不要精确年份")

    assert review.allowed is True
    assert review.requires_narrowing is True
    assert review.risk_tier == "high_risk"
    assert "traditional_high_risk_signal" in review.categories
    assert "传统高风险信号" in review.report_note
    assert "精确寿命" in review.report_note


def test_exact_lifespan_and_professional_requests_are_refused():
    cases = {
        "请算我能活到几岁": "lifespan_or_death_timing",
        "用八字诊断疾病并给治疗方案": "professional_advice",
    }

    for text, category in cases.items():
        review = classify_high_risk_request(text)

        assert review.allowed is False
        assert category in review.categories
        assert review.redirect_message


def test_build_report_allows_lifespan_focus_as_narrowed_signal(sample_bazi_chart):
    chart = replace(
        sample_bazi_chart,
        birth_profile=replace(sample_bazi_chart.birth_profile, focus_topic="寿命"),
    )

    report = build_report(chart)

    assert report.safety_review.allowed is True
    assert "高风险材料边界" in report.evidence_notes
    assert "传统风险信号" in report.evidence_notes
