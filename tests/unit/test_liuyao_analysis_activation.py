"""Tests for evidence-activated liuyao analysis (021, Task 3)."""

from __future__ import annotations

from mingli_engine.liuyao.analysis import (
    analyze_liuyao_chart,
    load_analysis_config,
)
from mingli_engine.liuyao.casting import assemble_liuyao_chart
from mingli_engine.liuyao.knowledge_activation import (
    LiuyaoEvidenceCitation,
    LiuyaoEvidenceIndex,
)
from mingli_engine.liuyao.result_models import (
    LiuyaoCastRequest,
    LiuyaoChart,
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

EXPECTED_CITATION_COUNTS = {
    "yong_shen_selection": 6,
    "shi_ying_relation": 0,
    "moving_line_dynamics": 5,
    "six_spirits_attachment": 3,
    "month_day_strength": 4,
    "void_break_state": 2,
    "yingqi_timing": 0,
    "category_judgment": 0,
}


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


def _by_family(analysis):
    return {item.rule_family: item for item in analysis.family_observations}


def test_evidence_bearing_families_carry_full_citations() -> None:
    analysis = analyze_liuyao_chart(_chart((1, 1, 1, 1, 0, 1), moving=(4,)))
    families = _by_family(analysis)
    for family, expected_count in EXPECTED_CITATION_COUNTS.items():
        citations = families[family].evidence_citations
        assert len(citations) == expected_count, family
        for citation in citations:
            assert isinstance(citation, LiuyaoEvidenceCitation)
            assert citation.evidence_id.startswith("liuyao_evidence_batch_20260714_")
            assert citation.rule_family == family
            assert citation.source_id.startswith("liuyao_source_batch_20260714_")
            assert citation.source_ref.startswith("page:")
            assert citation.limitations


def test_citations_carry_all_governed_evidence_of_the_family() -> None:
    from mingli_engine.liuyao.knowledge import load_liuyao_evidence_units

    analysis = analyze_liuyao_chart(_chart((0, 1, 1, 1, 1, 1)))
    families = _by_family(analysis)
    ledger = load_liuyao_evidence_units()
    expected_ids = {
        item.evidence_id for item in ledger if item.rule_family == "month_day_strength"
    }
    assert len(expected_ids) == 4
    ids = {
        citation.evidence_id
        for citation in families["month_day_strength"].evidence_citations
    }
    assert ids == expected_ids


def test_observations_and_statuses_match_v1_exactly() -> None:
    chart = _chart((1, 1, 1, 1, 0, 1), moving=(4,))
    activated = _by_family(analyze_liuyao_chart(chart))
    legacy = _by_family(analyze_liuyao_chart(chart, evidence_index=_EMPTY_INDEX))
    for family, observation in legacy.items():
        current = activated[family]
        assert current.observations == observation.observations, family
        assert current.status == observation.status, family
        assert observation.evidence_citations == (), family


def test_empty_families_keep_pending_note() -> None:
    config = load_analysis_config()
    analysis = analyze_liuyao_chart(_chart((1, 1, 1, 1, 0, 1)))
    families = _by_family(analysis)
    for family in ("shi_ying_relation", "yingqi_timing", "category_judgment"):
        assert families[family].evidence_citations == ()
        assert families[family].evidence_note == config.evidence_pending_note


def test_activated_families_use_activated_note() -> None:
    config = load_analysis_config()
    analysis = analyze_liuyao_chart(_chart((1, 1, 1, 1, 0, 1)))
    families = _by_family(analysis)
    for family, count in EXPECTED_CITATION_COUNTS.items():
        if count:
            assert families[family].evidence_note == config.evidence_activated_note
            assert families[family].evidence_note != config.evidence_pending_note


def test_explicit_empty_index_disables_activation() -> None:
    config = load_analysis_config()
    analysis = analyze_liuyao_chart(
        _chart((1, 1, 1, 1, 0, 1)), evidence_index=_EMPTY_INDEX
    )
    for item in analysis.family_observations:
        assert item.evidence_citations == ()
        assert item.evidence_note == config.evidence_pending_note
