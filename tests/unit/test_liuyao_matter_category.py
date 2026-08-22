"""Tests for matter category input and category evidence activation (021 follow-up).

The supported matter categories are derived strictly from the 47 governed
``category_judgment`` evidence units of batch_20260714; no category may be
invented beyond what the frozen evidence ledger covers.
"""

from __future__ import annotations

import pytest

from mingli_engine.high_risk import REFUSAL_MESSAGE
from mingli_engine.liuyao.analysis import (
    LiuyaoAnalysis,
    LiuyaoFamilyObservation,
    analyze_liuyao_chart,
    load_analysis_config,
)
from mingli_engine.liuyao.casting import assemble_liuyao_chart
from mingli_engine.liuyao.constants import (
    LIUYAO_HIGH_RISK_MATTER_CATEGORY_LABELS,
    LIUYAO_MATTER_CATEGORIES,
    LIUYAO_MATTER_CATEGORY_LABELS,
)
from mingli_engine.liuyao.knowledge import (
    LiuyaoKnowledgeError,
    load_liuyao_evidence_units,
)
from mingli_engine.liuyao.knowledge_activation import (
    CATEGORY_EVIDENCE_IDS,
    LiuyaoEvidenceIndex,
    LiuyaoMatterCategoryGate,
    RefusedLiuyaoMatterCategoryError,
    UnknownLiuyaoMatterCategoryError,
    build_liuyao_evidence_index,
    build_liuyao_matter_category_index,
    resolve_matter_category,
)
from mingli_engine.liuyao.report import build_liuyao_report
from mingli_engine.liuyao.report_markdown import render_liuyao_markdown
from mingli_engine.liuyao.result_models import (
    LiuyaoCastRequest,
    LiuyaoChart,
    LiuyaoLineInput,
)

EXPECTED_CATEGORY_LABELS = {
    "weather": "天气晴雨",
    "annual_fortune": "年运与自身气运",
    "wealth": "求财营生",
    "career": "功名科考",
    "marriage": "婚姻",
    "travel": "出行",
    "lost_items": "失物寻人",
    "house": "家宅",
    "agriculture": "农事蚕桑",
}

EXPECTED_HIGH_RISK_CATEGORY_LABELS = {
    "medical": "疾病医疗",
    "legal": "官司诉讼",
    "investment": "投资理财",
    "lifespan": "寿命生死",
}

# Frozen snapshot: every id below is a promoted category_judgment unit whose
# theme/summary explicitly addresses the matter; ledger order is preserved.
EXPECTED_CATEGORY_EVIDENCE = {
    "weather": (
        "liuyao_evidence_batch_20260714_0012",
        "liuyao_evidence_batch_20260714_0027",
        "liuyao_evidence_batch_20260714_0049",
        "liuyao_evidence_batch_20260714_0050",
    ),
    "annual_fortune": (
        "liuyao_evidence_batch_20260714_0013",
        "liuyao_evidence_batch_20260714_0028",
        "liuyao_evidence_batch_20260714_0029",
    ),
    "wealth": (
        "liuyao_evidence_batch_20260714_0033",
        "liuyao_evidence_batch_20260714_0034",
        "liuyao_evidence_batch_20260714_0055",
    ),
    "career": (
        "liuyao_evidence_batch_20260714_0014",
        "liuyao_evidence_batch_20260714_0055",
    ),
    "marriage": ("liuyao_evidence_batch_20260714_0014",),
    "travel": ("liuyao_evidence_batch_20260714_0055",),
    "lost_items": (
        "liuyao_evidence_batch_20260714_0036",
        "liuyao_evidence_batch_20260714_0037",
        "liuyao_evidence_batch_20260714_0038",
    ),
    "house": ("liuyao_evidence_batch_20260714_0039",),
    "agriculture": (
        "liuyao_evidence_batch_20260714_0031",
        "liuyao_evidence_batch_20260714_0032",
    ),
}

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


def test_category_vocabulary_covers_supported_and_high_risk_sets() -> None:
    assert LIUYAO_MATTER_CATEGORY_LABELS == EXPECTED_CATEGORY_LABELS
    assert (
        LIUYAO_HIGH_RISK_MATTER_CATEGORY_LABELS
        == EXPECTED_HIGH_RISK_CATEGORY_LABELS
    )
    assert LIUYAO_MATTER_CATEGORIES == tuple(
        EXPECTED_CATEGORY_LABELS
    ) + tuple(EXPECTED_HIGH_RISK_CATEGORY_LABELS)
    assert not set(EXPECTED_CATEGORY_LABELS) & set(
        EXPECTED_HIGH_RISK_CATEGORY_LABELS
    )


def test_category_evidence_mapping_matches_frozen_snapshot() -> None:
    assert CATEGORY_EVIDENCE_IDS == EXPECTED_CATEGORY_EVIDENCE
    assert tuple(CATEGORY_EVIDENCE_IDS) == tuple(LIUYAO_MATTER_CATEGORY_LABELS)


def test_category_mapping_units_exist_in_governed_ledger() -> None:
    ledger = load_liuyao_evidence_units()
    category_units = {
        unit.evidence_id: unit
        for unit in ledger
        if unit.rule_family == "category_judgment"
    }
    assert len(category_units) == 47
    mapped_ids = {
        evidence_id
        for evidence_ids in CATEGORY_EVIDENCE_IDS.values()
        for evidence_id in evidence_ids
    }
    assert mapped_ids <= set(category_units)
    for evidence_id in mapped_ids:
        unit = category_units[evidence_id]
        assert unit.risk_tier == "ordinary"
        assert unit.confidence == "moderate"
        assert unit.source_ref.startswith("page:")
        assert unit.limitations


def test_build_matter_category_index_groups_units_in_ledger_order() -> None:
    index = build_liuyao_matter_category_index(build_liuyao_evidence_index())
    assert tuple(category for category, _ in index.category_units) == tuple(
        LIUYAO_MATTER_CATEGORY_LABELS
    )
    for category, units in index.category_units:
        expected_ids = EXPECTED_CATEGORY_EVIDENCE[category]
        assert tuple(unit.evidence_id for unit in units) == expected_ids
        for unit in units:
            assert unit.rule_family == "category_judgment"
        assert index.units_for(category) == units


def test_matter_category_index_fails_closed_on_incomplete_ledger() -> None:
    with pytest.raises(LiuyaoKnowledgeError):
        build_liuyao_matter_category_index(_EMPTY_INDEX)


def test_matter_category_index_rejects_foreign_input() -> None:
    with pytest.raises(TypeError):
        build_liuyao_matter_category_index(object())


def test_resolve_matter_category_not_provided() -> None:
    gate = resolve_matter_category(None)
    assert isinstance(gate, LiuyaoMatterCategoryGate)
    assert gate.status == "not_provided"
    assert gate.category is None
    assert gate.label == ""


def test_resolve_matter_category_accepts_supported_categories() -> None:
    for category, label in EXPECTED_CATEGORY_LABELS.items():
        gate = resolve_matter_category(category)
        assert gate.status == "accepted"
        assert gate.category == category
        assert gate.label == label


def test_resolve_matter_category_refuses_high_risk_categories() -> None:
    for category in EXPECTED_HIGH_RISK_CATEGORY_LABELS:
        with pytest.raises(RefusedLiuyaoMatterCategoryError) as excinfo:
            resolve_matter_category(category)
        assert str(excinfo.value) == REFUSAL_MESSAGE


def test_resolve_matter_category_rejects_unknown_categories() -> None:
    for bad in ("astrology", "", "天气晴雨", "WEATHER", " weather", 123, True):
        with pytest.raises(UnknownLiuyaoMatterCategoryError):
            resolve_matter_category(bad)


def _chart(lines: tuple[int, ...], moving: tuple[int, ...] = ()) -> LiuyaoChart:
    return assemble_liuyao_chart(
        LiuyaoCastRequest(
            cast_mode="explicit",
            cast_datetime="1990-02-28T08:30",
            lines=tuple(
                LiuyaoLineInput(
                    position=index + 1,
                    yin_yang="yang" if value else "yin",
                    moving=(index + 1) in moving,
                )
                for index, value in enumerate(lines)
            ),
        )
    )


def _by_family(analysis: LiuyaoAnalysis) -> dict[str, LiuyaoFamilyObservation]:
    return {item.rule_family: item for item in analysis.family_observations}


def test_cast_request_accepts_optional_matter_category() -> None:
    base = dict(
        cast_mode="time",
        cast_datetime="1990-02-28T08:30",
    )
    assert LiuyaoCastRequest(**base).matter_category is None
    assert (
        LiuyaoCastRequest(**base, matter_category="weather").matter_category
        == "weather"
    )
    assert (
        LiuyaoCastRequest(**base, matter_category=None).matter_category is None
    )


def test_cast_request_rejects_unknown_matter_category() -> None:
    base = dict(
        cast_mode="time",
        cast_datetime="1990-02-28T08:30",
    )
    with pytest.raises(ValueError, match="matter category"):
        LiuyaoCastRequest(**base, matter_category="astrology")
    with pytest.raises(TypeError):
        LiuyaoCastRequest(**base, matter_category=7)


def test_analysis_without_category_keeps_v1_not_computed() -> None:
    config = load_analysis_config()
    chart = _chart((1, 1, 1, 1, 0, 1), moving=(4,))
    default_run = _by_family(analyze_liuyao_chart(chart))["category_judgment"]
    explicit_none = _by_family(
        analyze_liuyao_chart(chart, matter_category=None)
    )["category_judgment"]
    for observation in (default_run, explicit_none):
        assert observation.status == "not_computed"
        assert observation.observations == (
            "V1 未提供事项类别输入，分类占断不启用。",
        )
        assert observation.evidence_citations == ()
        assert observation.evidence_note == config.evidence_pending_note
    assert default_run == explicit_none


def test_analysis_with_supported_category_computes_citations() -> None:
    config = load_analysis_config()
    chart = _chart((1, 1, 1, 1, 0, 1), moving=(4,))
    analysis = analyze_liuyao_chart(chart, matter_category="weather")
    families = _by_family(analysis)
    observation = families["category_judgment"]
    assert observation.status == "computed"
    assert observation.observations == (
        "所问事项类别：天气晴雨。",
        "本族按事项类别激活4条已晋升的分类占断证据，"
        "仅呈现传统文献信号，不作现实预测。",
    )
    assert observation.evidence_note == config.evidence_activated_note
    citation_ids = tuple(
        citation.evidence_id for citation in observation.evidence_citations
    )
    assert citation_ids == EXPECTED_CATEGORY_EVIDENCE["weather"]
    for citation in observation.evidence_citations:
        assert citation.rule_family == "category_judgment"
        assert citation.source_id.startswith("liuyao_source_batch_20260714_")
        assert citation.source_ref.startswith("page:")
        assert citation.limitations
    legacy = _by_family(analyze_liuyao_chart(chart))
    for family, item in legacy.items():
        if family == "category_judgment":
            continue
        current = families[family]
        assert current.status == item.status, family
        assert current.observations == item.observations, family
        assert current.evidence_citations == item.evidence_citations, family


def test_analysis_every_supported_category_has_ledger_citations() -> None:
    chart = _chart((0, 1, 1, 1, 1, 1))
    for category, expected_ids in EXPECTED_CATEGORY_EVIDENCE.items():
        observation = _by_family(
            analyze_liuyao_chart(chart, matter_category=category)
        )["category_judgment"]
        assert observation.status == "computed", category
        citation_ids = tuple(
            citation.evidence_id for citation in observation.evidence_citations
        )
        assert citation_ids == expected_ids, category
        assert category and observation.observations[0].endswith("。")


def test_analysis_refuses_high_risk_category_before_analysis() -> None:
    chart = _chart((1, 1, 1, 1, 0, 1), moving=(4,))
    for category in EXPECTED_HIGH_RISK_CATEGORY_LABELS:
        with pytest.raises(RefusedLiuyaoMatterCategoryError) as excinfo:
            analyze_liuyao_chart(chart, matter_category=category)
        assert str(excinfo.value) == REFUSAL_MESSAGE


def test_analysis_rejects_unknown_category() -> None:
    chart = _chart((1, 1, 1, 1, 0, 1), moving=(4,))
    with pytest.raises(UnknownLiuyaoMatterCategoryError):
        analyze_liuyao_chart(chart, matter_category="astrology")


def test_category_analysis_is_deterministic() -> None:
    chart = _chart((1, 1, 1, 1, 0, 1), moving=(4,))
    first = analyze_liuyao_chart(chart, matter_category="agriculture")
    second = analyze_liuyao_chart(chart, matter_category="agriculture")
    assert first == second


def test_category_analysis_with_empty_index_fails_closed() -> None:
    chart = _chart((1, 1, 1, 1, 0, 1), moving=(4,))
    with pytest.raises(LiuyaoKnowledgeError):
        analyze_liuyao_chart(
            chart,
            matter_category="weather",
            evidence_index=_EMPTY_INDEX,
        )


def test_report_renders_category_section_with_citations() -> None:
    chart = _chart((1, 1, 1, 1, 0, 1), moving=(4,))
    report = build_liuyao_report(
        analyze_liuyao_chart(chart, matter_category="weather")
    )
    markdown = render_liuyao_markdown(report)
    assert "所问事项类别：天气晴雨。" in markdown
    assert "（已观察）" in markdown
    for evidence_id in EXPECTED_CATEGORY_EVIDENCE["weather"]:
        assert f"证据引用：{evidence_id}" in markdown
    assert "liuyao_source_batch_20260714_001" in markdown
    assert "page:129-160" in markdown


def test_report_boundary_holds_for_every_supported_category() -> None:
    chart = _chart((1, 1, 1, 1, 0, 1), moving=(4,))
    for category in EXPECTED_CATEGORY_EVIDENCE:
        report = build_liuyao_report(
            analyze_liuyao_chart(chart, matter_category=category)
        )
        markdown = render_liuyao_markdown(report)
        for marker in ("必定", "注定", "一定会", "死定"):
            assert marker not in markdown


def test_report_without_category_is_unchanged() -> None:
    chart = _chart((1, 1, 1, 1, 0, 1), moving=(4,))
    legacy = render_liuyao_markdown(build_liuyao_report(analyze_liuyao_chart(chart)))
    explicit_none = render_liuyao_markdown(
        build_liuyao_report(analyze_liuyao_chart(chart, matter_category=None))
    )
    assert legacy == explicit_none
    assert "未提供事项类别输入" in legacy
