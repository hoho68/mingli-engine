import json
from pathlib import Path

import pytest

from mingli_engine.liuyao import knowledge
from mingli_engine.liuyao.knowledge import (
    LiuyaoKnowledgeError,
    load_liuyao_candidates,
    load_liuyao_evidence_units,
    load_liuyao_family_map,
    load_liuyao_promotion_batches,
    load_liuyao_review_decisions,
    promote_liuyao_batch_candidates,
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


def _stage(tmp_path: Path) -> Path:
    data_dir = tmp_path / "liuyao"
    data_dir.mkdir()
    for name in LEDGER_NAMES:
        (data_dir / name).write_text("[]\n", encoding="utf-8")
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
