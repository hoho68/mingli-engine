"""Tests for matter category input and category evidence activation (021 follow-up).

The supported matter categories are derived strictly from the 47 governed
``category_judgment`` evidence units of batch_20260714; no category may be
invented beyond what the frozen evidence ledger covers.
"""

from __future__ import annotations

import pytest

from mingli_engine.high_risk import REFUSAL_MESSAGE
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
