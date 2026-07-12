from dataclasses import replace
from datetime import datetime
import re

from mingli_engine.bazi import analyze_bazi_chart
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.html import render_html_report
from mingli_engine.report_schema import build_report


def _assert_in_order(text: str, chunks: tuple[str, ...]) -> None:
    positions = []
    cursor = 0
    for chunk in chunks:
        position = text.find(chunk, cursor)
        assert position != -1, f"missing chunk after offset {cursor}: {chunk!r}"
        positions.append(position)
        cursor = position + len(chunk)

    assert positions == sorted(positions)


def _build_reasoned_report(sample_bazi_chart):
    chart = calculate_bazi_chart(sample_bazi_chart.birth_profile)
    calculation = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1990, 1, 1, 8, 30),
    )
    return build_report(chart, calculation), calculation


def test_render_html_report_returns_complete_static_document(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    html = render_html_report(report)

    assert html.startswith("<!doctype html>")
    assert '<html lang="zh-CN">' in html
    assert '<meta charset="utf-8">' in html
    assert f"<title>{report.title}</title>" in html
    assert "<style>" in html
    assert "</style>" in html
    assert len(re.findall(r"<main(?:\s|>)", html)) == 1
    assert html.count("</main>") == 1


def test_render_html_report_preserves_markdown_reading_order(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    html = render_html_report(report)

    _assert_in_order(
        html,
        (
            report.title,
            report.disclaimer,
            report.quick_guide,
            report.chart_card,
            report.assumptions,
            report.four_pillars_summary,
            report.five_elements_summary,
            report.ten_gods_summary,
            report.evidence_notes,
            report.formal_synthesis,
            report.integrated_synthesis,
            report.structure_analysis,
            report.personality_tendencies,
            report.interpretation_boundaries,
            report.strengths_and_issues,
            report.phase_overview,
            report.action_suggestions,
            report.glossary,
            report.ethics_reminder,
        ),
    )
    assert html.count(report.evidence_notes) == 1
    assert html.count("<h3>正式知识综合</h3>") == 1
    assert html.count(report.formal_synthesis) == 1
    assert html.count("<h3>综合脉络</h3>") == 1
    assert html.count(report.integrated_synthesis) == 1
    _assert_in_order(
        html,
        (
            "<h3>观察依据</h3>",
            "<h3>正式知识综合</h3>",
            "<h3>综合脉络</h3>",
            "<h3>结构分析</h3>",
        ),
    )


def test_render_html_report_includes_evidence_backed_action_tracks_once(
    sample_bazi_chart,
):
    report = build_report(sample_bazi_chart)

    html = render_html_report(report)

    assert html.count(report.action_suggestions) == 1
    for item in report.action_reflection_items:
        assert html.count(f"{item.title}｜状态：") == 1
    assert html.count("观察问题：") == 4
    assert html.count("反馈记录：") == 4
    assert html.count("停止边界：") == 4


def test_render_html_report_escapes_text_and_uses_no_external_resources(
    sample_bazi_chart,
):
    report = replace(
        build_report(sample_bazi_chart),
        title='HTML <title> & "quoted" \'single\'',
        disclaimer='<script>alert("x" & \'y\')</script>',
    )

    html = render_html_report(report)
    normalized = html.lower()

    assert "HTML &lt;title&gt; &amp; &quot;quoted&quot; &#x27;single&#x27;" in html
    assert "&lt;script&gt;alert(&quot;x&quot; &amp; &#x27;y&#x27;)&lt;/script&gt;" in html
    assert "<script" not in normalized
    assert " onclick" not in normalized
    assert "http://" not in normalized
    assert "https://" not in normalized
    assert "<link" not in normalized
    assert 'rel="stylesheet"' not in normalized
    assert "@font-face" not in normalized
    assert "<img" not in normalized


def test_render_html_report_exposes_five_reasoned_dimensions(sample_bazi_chart):
    report, calculation = _build_reasoned_report(sample_bazi_chart)

    html = render_html_report(report)

    for heading in (
        "推理分析",
        "盘面事实",
        "计算结果",
        "流派视角",
        "证据依据",
        "解读与安全边界",
    ):
        assert f">{heading}<" in html
    assert "计算状态：" in html
    assert "可信度：" in html
    for label in (
        "支持信号",
        "反对信号",
        "规则 ID",
        "证据 ID",
        "假设",
        "缺失输入",
    ):
        assert f"{label}：" in html
    for school in calculation.schools:
        assert f"school_view:{school.school_id}:" in html
    assert report.interpretation_boundaries in html
    assert report.ethics_reminder in html


def test_render_html_report_uses_faithful_reasoning_channels(sample_bazi_chart):
    report, _ = _build_reasoned_report(sample_bazi_chart)
    first = report.expanded_evidence.formal_conclusions[0]
    trace = replace(
        first.trace,
        chart_signals=["chart:exact"],
        supporting_signals=["support:exact"],
        opposing_signals=["oppose:exact"],
        rule_ids=["rule.exact"],
        missing_inputs=["missing:exact"],
        school_views=["school_view:exact"],
        disagreement_note="disagreement:exact",
    )
    report = replace(
        report,
        expanded_evidence=replace(
            report.expanded_evidence,
            formal_conclusions=[
                replace(first, trace=trace),
                *report.expanded_evidence.formal_conclusions[1:],
            ],
        ),
    )

    html = render_html_report(report)

    assert "<strong>支持信号：</strong>support:exact" in html
    assert "<strong>反对信号：</strong>oppose:exact" in html
    assert "<strong>规则 ID：</strong>rule.exact" in html
    assert "<strong>缺失输入：</strong>missing:exact" in html
    assert "<strong>分歧说明：</strong>disagreement:exact" in html
    assert "<strong>反对信号：</strong>disagreement:exact" not in html
    assert "<strong>流派视角：</strong>school_view:exact" in html


def test_render_html_report_escapes_reasoned_dynamic_text(sample_bazi_chart):
    report, _ = _build_reasoned_report(sample_bazi_chart)
    first = report.expanded_evidence.formal_conclusions[0]
    hostile = replace(
        first,
        title='<title onclick="bad">unsafe</title>',
        body='<script>alert("bad")</script>',
        rule_family="rule<&'\"unsafe",
        trace=replace(
            first.trace,
            chart_signals=['school_view:<school>:value=<img onerror="bad">'],
            school_views=['school_view:<school>:value=<img onerror="bad">'],
        ),
    )
    report = replace(
        report,
        expanded_evidence=replace(
            report.expanded_evidence,
            formal_conclusions=[
                hostile,
                *report.expanded_evidence.formal_conclusions[1:],
            ],
        ),
    )

    html = render_html_report(report)
    normalized = html.lower()

    assert '<title onclick="bad">unsafe</title>' not in html
    assert '<script>alert("bad")</script>' not in html
    assert '<img onerror="bad">' not in html
    assert "&lt;title onclick=&quot;bad&quot;&gt;unsafe&lt;/title&gt;" in html
    assert "rule&lt;&amp;&#x27;&quot;unsafe" in html
    assert "<script" not in normalized
    assert re.search(r"<[^>]*\sonclick=", normalized) is None
    assert re.search(r"<[^>]*\sonerror=", normalized) is None
    assert "<img" not in normalized
