from mingli_engine.report_schema import build_report


def test_build_report_returns_complete_safe_report(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    for field_name in (
        "disclaimer",
        "chart_card",
        "assumptions",
        "four_pillars_summary",
        "five_elements_summary",
        "ten_gods_summary",
        "structure_analysis",
        "phase_overview",
        "action_suggestions",
        "glossary",
        "ethics_reminder",
    ):
        assert getattr(report, field_name)

    assert report.safety_review.allowed is True
    assert report.safety_review.disclaimer_present is True
