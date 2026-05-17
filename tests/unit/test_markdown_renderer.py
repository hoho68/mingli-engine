from mingli_engine.markdown import render_markdown_report
from mingli_engine.report_schema import build_report


def _assert_in_order(text: str, headings: tuple[str, ...]) -> None:
    positions = [text.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_render_markdown_report_contains_required_headings(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    for heading in (
        "# 八字结构化报告",
        "## 免责声明",
        "## 快速导读",
        "## 第一层：基础资料",
        "## 第二层：结构观察",
        "## 第三层：解读边界",
        "## 第四层：行动反思",
        "## 术语简注",
        "## 伦理边界提醒",
    ):
        assert heading in markdown


def test_render_markdown_report_uses_layered_reading_order(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    _assert_in_order(
        markdown,
        (
            "# 八字结构化报告",
            "## 免责声明",
            "## 快速导读",
            "## 第一层：基础资料",
            "### 命造卡片",
            "### 排盘来源与假设",
            "## 第二层：结构观察",
            "### 四柱与五行摘要",
            "### 十神摘要",
            "### 结构分析",
            "### 性格倾向",
            "## 第三层：解读边界",
            "## 第四层：行动反思",
            "### 优势与议题",
            "### 阶段概览",
            "### 行动建议",
            "## 术语简注",
            "## 伦理边界提醒",
        ),
    )


def test_render_markdown_report_keeps_chart_source_transparent(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    assert sample_bazi_chart.chart_source.source_note in markdown
    assert sample_bazi_chart.chart_source.calendar_assumption in markdown
    assert markdown.endswith("\n")


def test_render_markdown_report_includes_interpretation_boundaries(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    assert report.interpretation_boundaries in markdown
    assert "不做格局定论" in markdown
    assert "不做用神定论" in markdown
    assert "不做大运流年判断" in markdown
