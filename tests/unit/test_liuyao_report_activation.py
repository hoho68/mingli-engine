"""Tests for evidence citation rendering and report boundary (021, Task 4)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from mingli_engine.liuyao.analysis import (
    LiuyaoAnalysis,
    LiuyaoEvidenceIndex,
    analyze_liuyao_chart,
)
from mingli_engine.liuyao.casting import assemble_liuyao_chart
from mingli_engine.liuyao.knowledge_activation import LiuyaoEvidenceCitation
from mingli_engine.liuyao.report import (
    LiuyaoReportError,
    build_liuyao_report,
)
from mingli_engine.liuyao.report_markdown import render_liuyao_markdown
from mingli_engine.liuyao.result_models import (
    LiuyaoCastRequest,
    LiuyaoLineInput,
)

_EMPTY_INDEX = LiuyaoEvidenceIndex(
    family_evidence=tuple(
        (family, ())
        for family in (
            "yong_shen_selection",
            "shi_ying_relation",
            "moving_line_dynamics",
            "six_spirits_attachment",
            "month_day_strength",
            "void_break_state",
            "yingqi_timing",
            "category_judgment",
        )
    )
)


def _chart():
    return assemble_liuyao_chart(
        LiuyaoCastRequest(
            cast_mode="explicit",
            cast_datetime="1990-02-28T08:30",
            lines=tuple(
                LiuyaoLineInput(position=i + 1, yin_yang="yang", moving=False)
                for i in range(6)
            ),
        )
    )


def _render_default() -> str:
    report = build_liuyao_report(analyze_liuyao_chart(_chart()))
    return render_liuyao_markdown(report)


def test_markdown_renders_full_citation_lines() -> None:
    text = _render_default()
    citation_lines = [
        line for line in text.splitlines() if line.startswith("- 证据引用：")
    ]
    # 9 + 3 + 5 + 3 + 4 + 2 + 4 activated citations across the seven
    # evidence families (category_judgment stays not_computed by default).
    assert len(citation_lines) == 30
    for line in citation_lines:
        assert "liuyao_evidence_batch_20260714_" in line
        assert "liuyao_source_batch_20260714_" in line
        assert "page:" in line
        assert "限制：" in line


def test_markdown_citation_line_format_is_deterministic() -> None:
    first = _render_default()
    second = _render_default()
    assert first == second
    sample = next(
        line for line in first.splitlines() if line.startswith("- 证据引用：")
    )
    # - 证据引用：{id}（{family}，{source}，{ref}）：{summary}；限制：…
    assert "（" in sample and "），" not in sample
    head, _, tail = sample.partition("：")
    assert head == "- 证据引用"
    assert "（" in tail and "）：" in tail


def test_families_without_citations_render_no_citation_lines() -> None:
    report = build_liuyao_report(
        analyze_liuyao_chart(_chart(), evidence_index=_EMPTY_INDEX)
    )
    text = render_liuyao_markdown(report)
    assert "- 证据引用：" not in text


def test_report_boundary_covers_citation_text() -> None:
    analysis = analyze_liuyao_chart(_chart(), evidence_index=_EMPTY_INDEX)
    forged = LiuyaoEvidenceCitation(
        evidence_id="liuyao_evidence_batch_20260714_9001",
        rule_family="yong_shen_selection",
        source_id="liuyao_source_batch_20260714_001",
        source_ref="page:1",
        theme=" forged ",
        summary="此断语必定应验。",
        limitations=("伪造引用，仅用于边界测试",),
        confidence="moderate",
    )
    replaced = tuple(
        replace(item, evidence_citations=(forged,))
        if item.rule_family == "yong_shen_selection"
        else item
        for item in analysis.family_observations
    )
    forged_analysis = LiuyaoAnalysis(chart=analysis.chart, family_observations=replaced)
    with pytest.raises(LiuyaoReportError):
        build_liuyao_report(forged_analysis)
