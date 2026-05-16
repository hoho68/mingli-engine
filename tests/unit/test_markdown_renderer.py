from mingli_engine.markdown import render_markdown_report
from mingli_engine.report_schema import build_report


def test_render_markdown_report_contains_required_headings(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    for heading in (
        "# 八字结构化报告",
        "## 免责声明",
        "## 命造卡片",
        "## 排盘来源与假设",
        "## 四柱与五行摘要",
        "## 十神摘要",
        "## 结构分析",
        "## 性格倾向",
        "## 优势与议题",
        "## 阶段概览",
        "## 行动建议",
        "## 术语简释",
        "## 伦理边界提醒",
    ):
        assert heading in markdown


def test_render_markdown_report_keeps_chart_source_transparent(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    assert sample_bazi_chart.chart_source.source_note in markdown
    assert sample_bazi_chart.chart_source.calendar_assumption in markdown
    assert markdown.endswith("\n")
