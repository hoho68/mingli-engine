from dataclasses import replace

import pytest

from mingli_engine.report_schema import build_report


RAW_READER_LABELS = (
    "auto_calculated",
    "external_verified",
    "medium",
    "gregorian",
    "year：",
    "month：",
    "day：",
    "hour：",
)


def _report_body(report) -> str:
    return "\n".join(
        [
            report.quick_guide,
            report.chart_card,
            report.assumptions,
            report.four_pillars_summary,
            report.five_elements_summary,
            report.ten_gods_summary,
            report.structure_analysis,
            report.personality_tendencies,
            report.strengths_and_issues,
            report.phase_overview,
            report.action_suggestions,
            report.interpretation_boundaries,
        ]
    )


def _chart_with_contract_labels(sample_bazi_chart):
    birth_profile = replace(
        sample_bazi_chart.birth_profile,
        calendar_type="gregorian",
        gender="未指定",
    )
    chart_source = replace(
        sample_bazi_chart.chart_source,
        source_type="auto_calculated",
        confidence="medium",
    )
    pillars = [
        replace(pillar, name=name)
        for pillar, name in zip(
            sample_bazi_chart.pillars,
            ("year", "month", "day", "hour"),
            strict=True,
        )
    ]
    return replace(
        sample_bazi_chart,
        birth_profile=birth_profile,
        chart_source=chart_source,
        pillars=pillars,
    )


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
        "interpretation_boundaries",
        "quick_guide",
    ):
        assert getattr(report, field_name)

    assert report.safety_review.allowed is True
    assert report.safety_review.disclaimer_present is True


def test_build_report_includes_basic_interpretation_sections(sample_bazi_chart):
    report = build_report(sample_bazi_chart)
    combined = "\n".join(
        [
            report.five_elements_summary,
            report.ten_gods_summary,
            report.structure_analysis,
            report.personality_tendencies,
            report.strengths_and_issues,
            report.phase_overview,
            report.action_suggestions,
            report.interpretation_boundaries,
        ]
    )

    assert "五行信号观察" in report.five_elements_summary
    assert "明面信号" in report.five_elements_summary
    assert "藏干" in report.five_elements_summary
    assert "观察中心" in report.personality_tendencies
    assert "十神结构观察" in report.ten_gods_summary
    assert "基础结构观察" in report.structure_analysis
    assert "基础结构解读层" in report.phase_overview
    assert "不做大运流年判断" in report.phase_overview
    assert "不做格局定论" in combined
    assert "不做用神定论" in combined
    assert "不做大运流年判断" in combined
    assert combined.count("不做格局定论") == 1
    assert combined.count("不做用神定论") == 1
    assert sample_bazi_chart.birth_profile.focus_topic in report.action_suggestions
    assert "结构" in report.action_suggestions
    assert report.strengths_and_issues not in report.action_suggestions


def test_build_report_prepares_quick_guide_and_boundary_layer(sample_bazi_chart):
    chart = _chart_with_contract_labels(sample_bazi_chart)
    report = build_report(chart)
    guide_lines = [
        line for line in report.quick_guide.splitlines() if line.startswith("- ")
    ]

    assert 3 <= len(guide_lines) <= 5
    assert "系统自动排盘" in report.quick_guide
    assert "中等可信度" in report.quick_guide
    assert chart.birth_profile.focus_topic in report.quick_guide
    assert "结构" in report.quick_guide
    assert "不做格局定论" in report.interpretation_boundaries
    assert "不做用神定论" in report.interpretation_boundaries
    assert "不做大运流年判断" in report.interpretation_boundaries
    assert report.interpretation_boundaries not in report.structure_analysis


def test_build_report_uses_reader_facing_labels(sample_bazi_chart):
    chart = _chart_with_contract_labels(sample_bazi_chart)
    report = build_report(chart)
    body = _report_body(report)

    assert "公历" in report.chart_card
    assert "系统自动排盘" in report.quick_guide
    assert "系统自动排盘" in report.assumptions
    assert "中等可信度" in report.quick_guide
    assert "中等可信度" in report.assumptions
    for pillar_name in ("年柱", "月柱", "日柱", "时柱"):
        assert f"- {pillar_name}：" in report.four_pillars_summary
    for raw_label in RAW_READER_LABELS:
        assert raw_label not in body


def test_build_report_uses_conservative_placeholder_for_unspecified_gender(
    sample_bazi_chart,
):
    birth_profile = replace(sample_bazi_chart.birth_profile, gender="未指定")
    chart = replace(sample_bazi_chart, birth_profile=birth_profile)
    report = build_report(chart)

    assert "性别标记：未说明" in report.chart_card


def test_build_report_preserves_unknown_non_empty_labels(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    assert "历法类型：solar" in report.chart_card
    assert "性别标记：female" in report.chart_card
    assert "externally_verified" in report.quick_guide
    assert "externally_verified" in report.assumptions
    assert "sample-high" in report.quick_guide
    assert "sample-high" in report.assumptions


def test_build_report_normalizes_placeholder_focus_topic(sample_bazi_chart):
    birth_profile = replace(sample_bazi_chart.birth_profile, focus_topic="unknown")
    chart = replace(sample_bazi_chart, birth_profile=birth_profile)

    report = build_report(chart)

    assert "unknown" not in report.quick_guide
    assert "unknown" not in report.action_suggestions
    assert "当前关注主题" in report.quick_guide
    assert "当前关注主题" in report.action_suggestions


def test_build_report_quick_guide_reads_like_plain_guidance(sample_bazi_chart):
    chart = _chart_with_contract_labels(sample_bazi_chart)
    report = build_report(chart)

    assert "这份盘的资料来自系统自动排盘" in report.quick_guide
    assert "这份盘里" in report.quick_guide
    assert "适合先从" in report.quick_guide
    assert "不是命运结论" in report.quick_guide
    assert "可复盘的小问题" in report.quick_guide


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
