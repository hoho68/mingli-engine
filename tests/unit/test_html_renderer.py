from dataclasses import replace
import re

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
