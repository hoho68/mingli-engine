import json
from pathlib import Path

import pytest

from mingli_engine.liuyao import knowledge
from mingli_engine.liuyao.knowledge import (
    LiuyaoKnowledgeError,
    LiuyaoTargetedClassicsReviewLedger,
    load_liuyao_candidates,
    load_liuyao_evidence_units,
    load_liuyao_family_map,
    load_liuyao_promotion_batches,
    load_liuyao_review_decisions,
    load_liuyao_sources,
    load_liuyao_targeted_classics_reviews,
    promote_liuyao_batch_candidates,
    promote_liuyao_family_gap_candidates,
    promote_liuyao_targeted_classics_candidates,
    validate_liuyao_knowledge_chain,
)

BATCH_DATA_ROOT = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "mingli_engine"
    / "data"
    / "new_material_learning"
)
LIUYAO_DATA_DIR = (
    Path(__file__).resolve().parents[2] / "src" / "mingli_engine" / "data" / "liuyao"
)
LEDGER_NAMES = (
    "liuyao_sources.json",
    "liuyao_candidates.json",
    "liuyao_review_decisions.json",
    "liuyao_promotion_batches.json",
    "liuyao_evidence_units.json",
)
REVIEW_LEDGER_NAME = "liuyao_targeted_classics_reviews.json"


def _stage(tmp_path: Path) -> Path:
    data_dir = tmp_path / "liuyao"
    data_dir.mkdir()
    for name in LEDGER_NAMES:
        (data_dir / name).write_text("[]\n", encoding="utf-8")
    # the targeted classics review ledger is a read-only promotion input and
    # stays outside the five-ledger rollback write set
    (data_dir / REVIEW_LEDGER_NAME).write_bytes(
        (LIUYAO_DATA_DIR / REVIEW_LEDGER_NAME).read_bytes()
    )
    return data_dir


def test_liuyao_family_map_is_frozen_and_maps_namespaces(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    family_map = load_liuyao_family_map()
    assert family_map.map_family("六爻占筮用神判断规则") == "yong_shen_selection"
    assert family_map.map_family("旬空判定") == "void_break_state"
    assert family_map.map_family("六神与神煞辅助断法") == "six_spirits_attachment"
    assert family_map.map_family("进退神判定") == "moving_line_dynamics"
    assert family_map.map_family("xyzzy-unknown") == "unmapped_family"
    monkeypatch.setattr(
        knowledge, "_EXPECTED_FAMILY_MAP_SHA256", "0" * 64
    )
    with pytest.raises(LiuyaoKnowledgeError, match="not frozen"):
        load_liuyao_family_map()


def test_empty_liuyao_namespace_is_valid(tmp_path: Path) -> None:
    data_dir = _stage(tmp_path)
    validate_liuyao_knowledge_chain(data_dir)
    assert load_liuyao_evidence_units(data_dir) == ()


def test_liuyao_namespace_is_isolated_from_bazi() -> None:
    from mingli_engine.liuyao.constants import LIUYAO_RULE_FAMILIES
    from mingli_engine.models import RULE_FAMILIES

    assert not set(LIUYAO_RULE_FAMILIES) & set(RULE_FAMILIES)


def test_promote_liuyao_batch_candidates_full_pipeline(tmp_path: Path) -> None:
    data_dir = _stage(tmp_path)
    summary = promote_liuyao_batch_candidates(
        BATCH_DATA_ROOT,
        generated_at="2026-08-19T03:00:00Z",
        data_dir=data_dir,
    )
    assert summary["reviewed_candidate_count"] == 101
    promoted = summary["promoted_count"]
    assert promoted > 0
    assert summary["registered_source_count"] == 2
    candidates = load_liuyao_candidates(data_dir)
    reviews = load_liuyao_review_decisions(data_dir)
    batches = load_liuyao_promotion_batches(data_dir)
    units = load_liuyao_evidence_units(data_dir)
    assert len(candidates) == promoted
    assert len(reviews) == promoted
    assert len(units) == promoted
    assert len(batches) == 1
    assert all(item.status == "promoted" for item in candidates)
    assert all(
        item.proposed_rule_family
        in knowledge.LIUYAO_RULE_FAMILIES
        for item in candidates
    )
    assert all(item.risk_tier != "high_risk" for item in candidates)
    validate_liuyao_knowledge_chain(data_dir)
    # evidence text never leaks intake paths or full source hashes
    manifest = json.loads(
        (BATCH_DATA_ROOT / "batch_20260714_manifest.json").read_text(encoding="utf-8")
    )
    forbidden = [manifest["intake_root"]] + [
        item["relative_path"] for item in manifest["files"]
    ] + [item["sha256"] for item in manifest["files"]] + [
        item["sha256"].lower() for item in manifest["files"]
    ]
    payload = json.dumps(
        [json.loads((data_dir / name).read_text(encoding="utf-8")) for name in LEDGER_NAMES],
        ensure_ascii=False,
    )
    assert not any(value and value in payload for value in forbidden)
    with pytest.raises(LiuyaoKnowledgeError, match="already applied"):
        promote_liuyao_batch_candidates(
            BATCH_DATA_ROOT,
            generated_at="2026-08-19T04:00:00Z",
            data_dir=data_dir,
        )


def test_promote_rolls_back_on_validation_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data_dir = _stage(tmp_path)
    before = {
        name: (data_dir / name).read_bytes() for name in LEDGER_NAMES
    }

    def _boom(data_dir=None):
        raise LiuyaoKnowledgeError("forced chain failure")

    monkeypatch.setattr(knowledge, "validate_liuyao_knowledge_chain", _boom)
    with pytest.raises(LiuyaoKnowledgeError, match="forced chain failure"):
        promote_liuyao_batch_candidates(
            BATCH_DATA_ROOT,
            generated_at="2026-08-19T03:00:00Z",
            data_dir=data_dir,
        )
    assert {
        name: (data_dir / name).read_bytes() for name in LEDGER_NAMES
    } == before


def _stage_promoted(tmp_path: Path) -> Path:
    data_dir = _stage(tmp_path)
    promote_liuyao_batch_candidates(
        BATCH_DATA_ROOT,
        generated_at="2026-08-19T03:00:00Z",
        data_dir=data_dir,
    )
    return data_dir


class TestGapPromotion:
    """Append-only governed promotion closing the two zero-evidence families."""

    def test_gap_promotion_appends_three_units(self, tmp_path: Path) -> None:
        data_dir = _stage_promoted(tmp_path)
        base_candidates = load_liuyao_candidates(data_dir)
        summary = promote_liuyao_family_gap_candidates(
            BATCH_DATA_ROOT,
            generated_at="2026-08-22T02:00:00Z",
            data_dir=data_dir,
        )
        assert summary["promoted_count"] == 3
        assert summary["family_counts"] == {
            "shi_ying_relation": 2,
            "yingqi_timing": 1,
        }
        candidates = load_liuyao_candidates(data_dir)
        reviews = load_liuyao_review_decisions(data_dir)
        batches = load_liuyao_promotion_batches(data_dir)
        units = load_liuyao_evidence_units(data_dir)
        assert len(candidates) == len(base_candidates) + 3 == 70
        assert len(reviews) == 70
        assert len(units) == 70
        assert len(batches) == 2
        # append-only: the frozen base segment is byte-order identical
        assert tuple(item.candidate_id for item in candidates[:67]) == tuple(
            item.candidate_id for item in base_candidates
        )
        new_candidates = candidates[67:]
        assert tuple(item.candidate_id for item in new_candidates) == (
            "liuyao_candidate_batch_20260714_0068",
            "liuyao_candidate_batch_20260714_0069",
            "liuyao_candidate_batch_20260714_0070",
        )
        assert tuple(item.proposed_rule_family for item in new_candidates) == (
            "shi_ying_relation",
            "shi_ying_relation",
            "yingqi_timing",
        )
        new_units = units[67:]
        assert tuple(item.evidence_id for item in new_units) == (
            "liuyao_evidence_batch_20260714_0068",
            "liuyao_evidence_batch_20260714_0069",
            "liuyao_evidence_batch_20260714_0070",
        )
        assert tuple(item.rule_family for item in new_units) == (
            "shi_ying_relation",
            "shi_ying_relation",
            "yingqi_timing",
        )
        for unit in new_units:
            assert unit.risk_tier == "ordinary"
            assert unit.confidence == "moderate"
            assert unit.source_ref.startswith("page:")
            assert unit.source_id.startswith("liuyao_source_batch_20260714_")
        validate_liuyao_knowledge_chain(data_dir)

    def test_gap_promotion_is_append_only_and_idempotent(
        self, tmp_path: Path
    ) -> None:
        data_dir = _stage_promoted(tmp_path)
        promote_liuyao_family_gap_candidates(
            BATCH_DATA_ROOT,
            generated_at="2026-08-22T02:00:00Z",
            data_dir=data_dir,
        )
        with pytest.raises(LiuyaoKnowledgeError, match="already applied"):
            promote_liuyao_family_gap_candidates(
                BATCH_DATA_ROOT,
                generated_at="2026-08-22T03:00:00Z",
                data_dir=data_dir,
            )

    def test_gap_promotion_requires_the_base_batch(self, tmp_path: Path) -> None:
        data_dir = _stage(tmp_path)
        with pytest.raises(LiuyaoKnowledgeError, match="base promotion"):
            promote_liuyao_family_gap_candidates(
                BATCH_DATA_ROOT,
                generated_at="2026-08-22T02:00:00Z",
                data_dir=data_dir,
            )

    def test_gap_promotion_rejects_unknown_records(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        data_dir = _stage_promoted(tmp_path)
        monkeypatch.setattr(
            knowledge,
            "LIUYAO_GAP_PROMOTION_ADJUDICATIONS",
            (("batch_20260714-bogus-record", "shi_ying_relation"),),
        )
        with pytest.raises(LiuyaoKnowledgeError, match="unknown"):
            promote_liuyao_family_gap_candidates(
                BATCH_DATA_ROOT,
                generated_at="2026-08-22T02:00:00Z",
                data_dir=data_dir,
            )

    def test_gap_promotion_rejects_already_promoted_records(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        data_dir = _stage_promoted(tmp_path)
        monkeypatch.setattr(
            knowledge,
            "LIUYAO_GAP_PROMOTION_ADJUDICATIONS",
            (
                (
                    "batch_20260714-02ae584ac6d1-006-o001-candidate-002",
                    "shi_ying_relation",
                ),
            ),
        )
        with pytest.raises(LiuyaoKnowledgeError, match="already promoted"):
            promote_liuyao_family_gap_candidates(
                BATCH_DATA_ROOT,
                generated_at="2026-08-22T02:00:00Z",
                data_dir=data_dir,
            )

    def test_gap_promotion_rolls_back_on_validation_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        data_dir = _stage_promoted(tmp_path)
        before = {name: (data_dir / name).read_bytes() for name in LEDGER_NAMES}

        def _boom(data_dir=None):
            raise LiuyaoKnowledgeError("forced chain failure")

        monkeypatch.setattr(knowledge, "validate_liuyao_knowledge_chain", _boom)
        with pytest.raises(LiuyaoKnowledgeError, match="forced chain failure"):
            promote_liuyao_family_gap_candidates(
                BATCH_DATA_ROOT,
                generated_at="2026-08-22T02:00:00Z",
                data_dir=data_dir,
            )
        assert {
            name: (data_dir / name).read_bytes() for name in LEDGER_NAMES
        } == before

    def test_gap_promotion_never_leaks_intake_paths_or_hashes(
        self, tmp_path: Path
    ) -> None:
        data_dir = _stage_promoted(tmp_path)
        promote_liuyao_family_gap_candidates(
            BATCH_DATA_ROOT,
            generated_at="2026-08-22T02:00:00Z",
            data_dir=data_dir,
        )
        manifest = json.loads(
            (BATCH_DATA_ROOT / "batch_20260714_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        forbidden = [manifest["intake_root"]] + [
            item["relative_path"] for item in manifest["files"]
        ] + [item["sha256"] for item in manifest["files"]] + [
            item["sha256"].lower() for item in manifest["files"]
        ]
        payload = json.dumps(
            [
                json.loads((data_dir / name).read_text(encoding="utf-8"))
                for name in LEDGER_NAMES
            ],
            ensure_ascii=False,
        )
        assert not any(value and value in payload for value in forbidden)


def _stage_gap_promoted(tmp_path: Path) -> Path:
    data_dir = _stage_promoted(tmp_path)
    promote_liuyao_family_gap_candidates(
        BATCH_DATA_ROOT,
        generated_at="2026-08-22T02:00:00Z",
        data_dir=data_dir,
    )
    return data_dir


def _tamper_review_ledger(
    monkeypatch: pytest.MonkeyPatch,
    data_dir: Path,
    mutate,
) -> None:
    ledger = load_liuyao_targeted_classics_reviews(
        data_dir / REVIEW_LEDGER_NAME
    )
    records = list(ledger.promotion_records)
    mutate(ledger, records)
    tampered = LiuyaoTargetedClassicsReviewLedger(
        schema_version=ledger.schema_version,
        review_id=ledger.review_id,
        source_id=ledger.source_id,
        promotion_records=tuple(records),
        coverage=ledger.coverage,
    )
    monkeypatch.setattr(
        knowledge,
        "load_liuyao_targeted_classics_reviews",
        lambda path=None: tampered,
    )


class TestTargetedClassicsPromotion:
    """Append-only governed promotion of the 7 adjudicated classics records."""

    def test_targeted_classics_promotion_appends_seven_units(
        self, tmp_path: Path
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)
        base_candidates = load_liuyao_candidates(data_dir)
        base_reviews = load_liuyao_review_decisions(data_dir)
        base_units = load_liuyao_evidence_units(data_dir)
        summary = promote_liuyao_targeted_classics_candidates(
            generated_at="2026-08-22T08:00:00Z",
            data_dir=data_dir,
        )
        assert summary == {
            "family_counts": {
                "shi_ying_relation": 1,
                "yingqi_timing": 3,
                "yong_shen_selection": 3,
            },
            "generated_at": "2026-08-22T08:00:00Z",
            "promoted_count": 7,
            "promotion_batch_id": "liuyao_promotion_batch_20260822_001",
            "total_evidence_count": 77,
        }
        assert len(load_liuyao_sources(data_dir)) == 2
        candidates = load_liuyao_candidates(data_dir)
        reviews = load_liuyao_review_decisions(data_dir)
        batches = load_liuyao_promotion_batches(data_dir)
        units = load_liuyao_evidence_units(data_dir)
        assert len(candidates) == len(reviews) == len(units) == 77
        assert len(batches) == 3
        # append-only: the frozen 70-record prefix is byte-order identical
        assert tuple(candidates[:70]) == base_candidates
        assert tuple(reviews[:70]) == base_reviews
        assert tuple(units[:70]) == base_units
        assert tuple(item.candidate_id for item in candidates[70:]) == tuple(
            f"liuyao_candidate_batch_20260714_{index:04d}"
            for index in range(71, 78)
        )
        assert tuple(item.evidence_id for item in units[70:]) == tuple(
            f"liuyao_evidence_batch_20260714_{index:04d}"
            for index in range(71, 78)
        )
        ledger = load_liuyao_targeted_classics_reviews(
            data_dir / REVIEW_LEDGER_NAME
        )
        record_by_id = {item.record_id: item for item in ledger.promotion_records}
        for candidate, unit in zip(candidates[70:], units[70:], strict=True):
            record = record_by_id[candidate.batch_record_id]
            assert candidate.source_id == "liuyao_source_batch_20260714_001"
            assert candidate.source_locator == record.source_ref
            assert "-" not in candidate.source_locator
            assert candidate.extracted_meaning == record.summary
            assert candidate.proposed_rule_family == record.rule_family
            assert candidate.risk_tier == "ordinary"
            assert candidate.status == "promoted"
            assert candidate.proposed_limitations == record.limitations
            assert unit.batch_record_id == record.record_id
            assert unit.source_id == "liuyao_source_batch_20260714_001"
            assert unit.source_ref == record.source_ref
            assert unit.theme == record.theme
            assert unit.rule_family == record.rule_family
            assert unit.risk_tier == "ordinary"
            assert unit.confidence == "moderate"
            assert unit.summary == record.summary
            assert unit.applicability == record.applicability
            assert unit.limitations == record.limitations
            assert unit.curation_batch_id == "liuyao_curation_batch_20260822_002"
        validate_liuyao_knowledge_chain(data_dir)

    def test_targeted_classics_promotion_requires_the_base_batch(
        self, tmp_path: Path
    ) -> None:
        data_dir = _stage(tmp_path)
        with pytest.raises(LiuyaoKnowledgeError, match="base promotion"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )

    def test_targeted_classics_promotion_requires_the_gap_batch(
        self, tmp_path: Path
    ) -> None:
        data_dir = _stage_promoted(tmp_path)
        with pytest.raises(LiuyaoKnowledgeError, match="gap promotion"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )

    def test_targeted_classics_promotion_is_idempotent(
        self, tmp_path: Path
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)
        promote_liuyao_targeted_classics_candidates(
            generated_at="2026-08-22T08:00:00Z",
            data_dir=data_dir,
        )
        with pytest.raises(LiuyaoKnowledgeError, match="already applied"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T09:00:00Z",
                data_dir=data_dir,
            )

    def test_targeted_classics_rejects_unknown_source(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)

        def _mutate(ledger, records) -> None:
            object.__setattr__(
                ledger, "source_id", "liuyao_source_batch_20260714_099"
            )

        _tamper_review_ledger(monkeypatch, data_dir, _mutate)
        with pytest.raises(LiuyaoKnowledgeError, match="unknown"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )

    def test_targeted_classics_rejects_family_outside_namespace(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)

        def _mutate(ledger, records) -> None:
            object.__setattr__(records[0], "rule_family", "not_a_family")

        _tamper_review_ledger(monkeypatch, data_dir, _mutate)
        with pytest.raises(LiuyaoKnowledgeError, match="outside the namespace"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )

    def test_targeted_classics_rejects_non_single_page_locator(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)

        def _mutate(ledger, records) -> None:
            object.__setattr__(records[0], "source_ref", "page:28-29")

        _tamper_review_ledger(monkeypatch, data_dir, _mutate)
        with pytest.raises(LiuyaoKnowledgeError, match="single page"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )

    def test_targeted_classics_rejects_high_risk_records(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)

        def _mutate(ledger, records) -> None:
            object.__setattr__(records[0], "risk_tier", "high_risk")

        _tamper_review_ledger(monkeypatch, data_dir, _mutate)
        with pytest.raises(LiuyaoKnowledgeError, match="ordinary"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )

    def test_targeted_classics_rejects_signature_duplicates(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)
        # semantically equivalent to an existing evidence unit after
        # normalization, but not byte-identical (trailing punctuation)
        existing = load_liuyao_evidence_units(data_dir)[0]

        def _mutate(ledger, records) -> None:
            object.__setattr__(
                records[0], "rule_family", existing.rule_family
            )
            object.__setattr__(
                records[0], "summary", existing.summary + "，"
            )
            object.__setattr__(
                records[0], "applicability", existing.applicability
            )
            object.__setattr__(
                records[0], "limitations", existing.limitations
            )

        _tamper_review_ledger(monkeypatch, data_dir, _mutate)
        with pytest.raises(LiuyaoKnowledgeError, match="duplicate"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )

    def test_targeted_classics_rejects_reversed_batch_sequence(
        self, tmp_path: Path
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)
        batches_path = data_dir / "liuyao_promotion_batches.json"
        payload = json.loads(batches_path.read_text(encoding="utf-8"))
        payload.reverse()
        batches_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        with pytest.raises(LiuyaoKnowledgeError, match="batch sequence"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )

    def test_targeted_classics_rejects_altered_predecessor_state(
        self, tmp_path: Path
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)
        candidates_path = data_dir / "liuyao_candidates.json"
        payload = json.loads(candidates_path.read_text(encoding="utf-8"))
        candidates_path.write_text(
            json.dumps(payload[:-1], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        with pytest.raises(LiuyaoKnowledgeError, match="70-record"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )

    @pytest.mark.parametrize("field", ("theme", "applicability"))
    def test_targeted_classics_gates_theme_and_applicability(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)

        def _mutate(ledger, records) -> None:
            if field == "theme":
                object.__setattr__(records[0], "theme", "占断结果必定如期")
            else:
                object.__setattr__(
                    records[0],
                    "applicability",
                    (*records[0].applicability, "结果必定如期"),
                )

        _tamper_review_ledger(monkeypatch, data_dir, _mutate)
        with pytest.raises(LiuyaoKnowledgeError, match="rejected_boundary"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )

    def test_targeted_classics_rolls_back_on_validation_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)
        before = {name: (data_dir / name).read_bytes() for name in LEDGER_NAMES}

        def _boom(data_dir=None):
            raise LiuyaoKnowledgeError("forced chain failure")

        monkeypatch.setattr(knowledge, "validate_liuyao_knowledge_chain", _boom)
        with pytest.raises(LiuyaoKnowledgeError, match="forced chain failure"):
            promote_liuyao_targeted_classics_candidates(
                generated_at="2026-08-22T08:00:00Z",
                data_dir=data_dir,
            )
        assert {
            name: (data_dir / name).read_bytes() for name in LEDGER_NAMES
        } == before

    def test_targeted_classics_never_leaks_intake_paths_or_hashes(
        self, tmp_path: Path
    ) -> None:
        data_dir = _stage_gap_promoted(tmp_path)
        promote_liuyao_targeted_classics_candidates(
            generated_at="2026-08-22T08:00:00Z",
            data_dir=data_dir,
        )
        manifest = json.loads(
            (BATCH_DATA_ROOT / "batch_20260714_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        forbidden = [manifest["intake_root"]] + [
            item["relative_path"] for item in manifest["files"]
        ] + [item["sha256"] for item in manifest["files"]] + [
            item["sha256"].lower() for item in manifest["files"]
        ]
        payload = json.dumps(
            [
                json.loads((data_dir / name).read_text(encoding="utf-8"))
                for name in LEDGER_NAMES
            ],
            ensure_ascii=False,
        )
        assert not any(value and value in payload for value in forbidden)
