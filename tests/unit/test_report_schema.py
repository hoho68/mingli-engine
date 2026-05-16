from dataclasses import replace

import pytest

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


def test_build_report_blocks_lifespan_focus_topic(sample_bazi_chart):
    birth_profile = replace(sample_bazi_chart.birth_profile, focus_topic="寿命")
    chart = replace(sample_bazi_chart, birth_profile=birth_profile)

    report = build_report(chart)

    assert report.safety_review.allowed is False
    assert "lifespan_or_death_timing" in report.safety_review.red_line_categories


def test_build_report_rejects_chart_without_four_pillars(sample_bazi_chart):
    chart = replace(sample_bazi_chart, pillars=[])

    with pytest.raises(ValueError, match="four pillars"):
        build_report(chart)
