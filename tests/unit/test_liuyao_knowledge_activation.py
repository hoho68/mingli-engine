"""Tests for the liuyao knowledge activation layer (021)."""

from __future__ import annotations

import pytest

from mingli_engine.liuyao.constants import LIUYAO_RULE_FAMILIES
from mingli_engine.liuyao.knowledge import (
    LiuyaoEvidenceUnit,
    LiuyaoKnowledgeError,
    load_liuyao_evidence_units,
)
from mingli_engine.liuyao.knowledge_activation import (
    LiuyaoActivationSummary,
    LiuyaoEvidenceCitation,
    LiuyaoEvidenceIndex,
    build_liuyao_evidence_index,
    citation_from_unit,
    validate_liuyao_evidence_activation,
)

EXPECTED_FAMILY_COUNTS = {
    "yong_shen_selection": 9,
    "shi_ying_relation": 3,
    "moving_line_dynamics": 5,
    "six_spirits_attachment": 3,
    "month_day_strength": 4,
    "void_break_state": 2,
    "yingqi_timing": 4,
    "category_judgment": 47,
}


def _unit(**overrides) -> LiuyaoEvidenceUnit:
    payload = {
        "evidence_id": "liuyao_evidence_batch_20260714_0001",
        "source_id": "liuyao_source_batch_20260714_001",
        "source_ref": "page:1-32",
        "theme": "起卦与变卦操作规则",
        "rule_family": "moving_line_dynamics",
        "risk_tier": "ordinary",
        "summary": "传统起卦与变卦规则描述。",
        "applicability": ("采用三枚铜钱抛掷六次",),
        "limitations": ("此规则仅存在于术数文献中",),
        "batch_record_id": "batch_20260714-test",
        "curation_batch_id": "liuyao_curation_batch_20260714_001",
    }
    payload.update(overrides)
    return LiuyaoEvidenceUnit(**payload)


class TestCitationFromUnit:
    def test_carries_full_reference_fields(self) -> None:
        citation = citation_from_unit(_unit())
        assert citation.evidence_id == "liuyao_evidence_batch_20260714_0001"
        assert citation.rule_family == "moving_line_dynamics"
        assert citation.source_id == "liuyao_source_batch_20260714_001"
        assert citation.source_ref == "page:1-32"
        assert citation.theme == "起卦与变卦操作规则"
        assert citation.summary == "传统起卦与变卦规则描述。"
        assert citation.limitations == ("此规则仅存在于术数文献中",)
        assert citation.confidence == "moderate"

    def test_rejects_non_string_fields(self) -> None:
        with pytest.raises((TypeError, ValueError)):
            LiuyaoEvidenceCitation(
                evidence_id="",
                rule_family="moving_line_dynamics",
                source_id="liuyao_source_batch_20260714_001",
                source_ref="page:1-32",
                theme="t",
                summary="s",
                limitations=("l",),
                confidence="moderate",
            )

    def test_rejects_non_page_source_ref(self) -> None:
        with pytest.raises(ValueError, match="page"):
            citation_from_unit(_unit(source_ref="chapter:3"))

    def test_rejects_family_outside_namespace(self) -> None:
        with pytest.raises(ValueError, match="family"):
            LiuyaoEvidenceCitation(
                evidence_id="e1",
                rule_family="bazi_strength",
                source_id="s1",
                source_ref="page:1",
                theme="t",
                summary="s",
                limitations=("l",),
                confidence="moderate",
            )

    def test_rejects_empty_limitations(self) -> None:
        with pytest.raises(ValueError, match="limitation"):
            LiuyaoEvidenceCitation(
                evidence_id="e1",
                rule_family="moving_line_dynamics",
                source_id="s1",
                source_ref="page:1",
                theme="t",
                summary="s",
                limitations=(),
                confidence="moderate",
            )


class TestBuildEvidenceIndex:
    def test_covers_all_eight_families_in_governed_order(self) -> None:
        index = build_liuyao_evidence_index()
        assert isinstance(index, LiuyaoEvidenceIndex)
        assert tuple(family for family, _ in index.family_evidence) == (
            LIUYAO_RULE_FAMILIES
        )

    def test_total_and_family_distribution_match_frozen_ledger(self) -> None:
        index = build_liuyao_evidence_index()
        counts = {family: len(units) for family, units in index.family_evidence}
        assert counts == EXPECTED_FAMILY_COUNTS
        assert sum(counts.values()) == 77

    def test_family_lookup_returns_ledger_order(self) -> None:
        index = build_liuyao_evidence_index()
        ledger = load_liuyao_evidence_units()
        for family in LIUYAO_RULE_FAMILIES:
            expected = tuple(item for item in ledger if item.rule_family == family)
            assert index.family(family) == expected

    def test_build_is_deterministic(self) -> None:
        first = build_liuyao_evidence_index()
        second = build_liuyao_evidence_index()
        assert first == second

    def test_corrupted_ledger_fails_closed(self, tmp_path) -> None:
        import json
        from dataclasses import asdict
        from importlib import resources

        source_dir = resources.files("mingli_engine").joinpath("data/liuyao")
        for name in (
            "liuyao_sources.json",
            "liuyao_candidates.json",
            "liuyao_review_decisions.json",
            "liuyao_promotion_batches.json",
            "liuyao_evidence_units.json",
        ):
            (tmp_path / name).write_bytes(source_dir.joinpath(name).read_bytes())
        units = load_liuyao_evidence_units()
        (tmp_path / "liuyao_evidence_units.json").write_text(
            json.dumps(
                [asdict(item) for item in units[1:]],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        with pytest.raises(LiuyaoKnowledgeError):
            build_liuyao_evidence_index(tmp_path)


class TestValidateEvidenceActivation:
    def test_summary_matches_frozen_facts(self) -> None:
        summary = validate_liuyao_evidence_activation()
        assert isinstance(summary, LiuyaoActivationSummary)
        assert summary.total_count == 77
        assert dict(summary.family_counts) == EXPECTED_FAMILY_COUNTS
        assert tuple(family for family, _ in summary.family_counts) == (
            LIUYAO_RULE_FAMILIES
        )

    def test_summary_confirms_governance_invariants(self) -> None:
        summary = validate_liuyao_evidence_activation()
        assert summary.all_ordinary_risk is True
        assert summary.all_moderate_confidence is True
        assert summary.all_page_locators is True

    def test_non_page_locator_fails_closed(self, tmp_path) -> None:
        import json
        from dataclasses import asdict
        from importlib import resources

        source_dir = resources.files("mingli_engine").joinpath("data/liuyao")
        for name in (
            "liuyao_sources.json",
            "liuyao_candidates.json",
            "liuyao_review_decisions.json",
            "liuyao_promotion_batches.json",
        ):
            (tmp_path / name).write_bytes(source_dir.joinpath(name).read_bytes())
        units = list(load_liuyao_evidence_units())
        payload = asdict(units[0])
        payload["source_ref"] = "chapter:3"
        (tmp_path / "liuyao_evidence_units.json").write_text(
            json.dumps([payload] + [asdict(item) for item in units[1:]], ensure_ascii=False),
            encoding="utf-8",
        )
        with pytest.raises(LiuyaoKnowledgeError):
            validate_liuyao_evidence_activation(tmp_path)
