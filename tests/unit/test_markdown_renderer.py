from dataclasses import replace
from datetime import datetime

from mingli_engine.bazi import analyze_bazi_chart
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.markdown import render_markdown_report
from mingli_engine.report_schema import build_report


def _assert_in_order(text: str, headings: tuple[str, ...]) -> None:
    lines = text.splitlines()
    positions = [lines.index(heading) for heading in headings]
    assert positions == sorted(positions)


def _build_reasoned_report(sample_bazi_chart):
    chart = calculate_bazi_chart(sample_bazi_chart.birth_profile)
    calculation = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1990, 1, 1, 8, 30),
    )
    return build_report(chart, calculation), calculation


def test_render_markdown_report_contains_required_headings(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)
    lines = markdown.splitlines()

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
        assert heading in lines


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
            "### 观察依据",
            "### 正式知识综合",
            "### 综合脉络",
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
    assert "先核对资料与假设" in markdown
    assert "再看结构观察" in markdown
    assert "这些基础资料只说明排盘依据与采用假设，不直接构成命理结论" in markdown
    assert "结构观察提供的是线索，不是最终判断" in markdown
    assert "这些边界是为了防止过度断言" in markdown
    assert "行动反思只作为复盘提示" in markdown


def test_render_markdown_report_includes_observation_basis(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    assert "### 观察依据" in markdown.splitlines()
    assert report.evidence_notes in markdown
    assert markdown.count("### 观察依据") == 1
    assert markdown.count(report.evidence_notes) == 1


def test_render_markdown_report_includes_formal_synthesis_once(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    assert markdown.count("### 正式知识综合") == 1
    assert markdown.count(report.formal_synthesis) == 1
    _assert_in_order(
        markdown,
        (
            "### 观察依据",
            "### 正式知识综合",
            "### 综合脉络",
            "### 结构分析",
        ),
    )


def test_render_markdown_report_includes_integrated_synthesis_once(
    sample_bazi_chart,
):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    assert markdown.count("### 综合脉络") == 1
    assert markdown.count(report.integrated_synthesis) == 1


def test_render_markdown_report_includes_evidence_backed_action_tracks_once(
    sample_bazi_chart,
):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    assert markdown.count(report.action_suggestions) == 1
    for item in report.action_reflection_items:
        assert markdown.count(f"{item.title}｜状态：") == 1
    assert markdown.count("观察问题：") == 4
    assert markdown.count("反馈记录：") == 4
    assert markdown.count("停止边界：") == 4


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
    assert markdown.count(report.interpretation_boundaries) == 1
    assert "不做格局定论" in markdown
    assert "不做用神定论" in markdown
    assert "不做大运流年判断" in markdown


def test_render_markdown_report_exposes_five_reasoned_dimensions(sample_bazi_chart):
    report, calculation = _build_reasoned_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    for heading in (
        "## 推理分析",
        "### 盘面事实",
        "### 计算结果",
        "### 流派视角",
        "### 证据依据",
        "### 解读与安全边界",
    ):
        assert heading in markdown.splitlines()
    assert "- 计算状态：" in markdown
    assert "- 可信度：" in markdown
    for label in (
        "支持信号",
        "反对信号",
        "规则 ID",
        "证据 ID",
        "假设",
        "缺失输入",
    ):
        assert f"- {label}：" in markdown
    for school in calculation.schools:
        assert f"school_view:{school.school_id}:" in markdown
    assert report.chart_card in markdown
    assert report.interpretation_boundaries in markdown
    assert report.ethics_reminder in markdown


def test_render_markdown_report_escapes_reasoned_dynamic_text(sample_bazi_chart):
    report, _ = _build_reasoned_report(sample_bazi_chart)
    first = report.expanded_evidence.formal_conclusions[0]
    hostile = replace(
        first,
        title="# injected <script>alert(1)</script>",
        body="<b>unsafe conclusion</b>",
        rule_family="rule<unsafe>&value",
        trace=replace(
            first.trace,
            chart_signals=["school_view:<school>:value=<img src=x>"],
        ),
    )
    report = replace(
        report,
        formal_synthesis="<iframe>formal injection</iframe>\n# formal heading",
        expanded_evidence=replace(
            report.expanded_evidence,
            formal_conclusions=[
                hostile,
                *report.expanded_evidence.formal_conclusions[1:],
            ],
        ),
    )

    markdown = render_markdown_report(report)

    assert "<script>" not in markdown
    assert "<b>unsafe conclusion</b>" not in markdown
    assert "<img src=x>" not in markdown
    assert "<iframe>formal injection</iframe>" not in markdown
    assert "\n# formal heading" not in markdown
    assert "#### # injected" not in markdown
    assert r"\# injected &lt;script&gt;alert\(1\)&lt;/script&gt;" in markdown
    assert "rule&lt;unsafe&gt;&amp;value" in markdown
