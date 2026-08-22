import json
from pathlib import Path

import pytest

from mingli_engine.liuyao.knowledge import (
    LiuyaoKnowledgeError,
    load_liuyao_targeted_classics_reviews,
)

LIUYAO_DATA_DIR = (
    Path(__file__).resolve().parents[2] / "src" / "mingli_engine" / "data" / "liuyao"
)

EXPECTED_COVERAGE = (
    ("page:27-29", "promote_and_duplicate"),
    ("page:61", "duplicate"),
    ("page:65", "duplicate"),
    ("page:69-71", "promote_and_duplicate"),
    ("page:72-81", "duplicate_and_conflict"),
    ("page:133-291", "support_only"),
    ("page:300-310", "duplicate"),
    ("page:332-339", "promote_and_duplicate"),
    ("page:340-344", "conflict_logged"),
    ("page:477-492", "support_only"),
    ("page:493", "promote"),
    ("page:494-497", "support_only"),
    ("page:498", "promote"),
    ("page:499-500", "support_only"),
    ("page:501", "promote"),
    ("page:502-523", "support_only"),
    ("page:524", "duplicate"),
    ("page:525-526", "support_only"),
)


def test_targeted_classics_review_is_complete_and_sanitized() -> None:
    ledger = load_liuyao_targeted_classics_reviews()
    assert ledger.review_id == "liuyao_targeted_classics_review_20260822_001"
    assert ledger.source_id == "liuyao_source_batch_20260714_001"
    assert len(ledger.promotion_records) == 7
    assert tuple(item.record_id for item in ledger.promotion_records) == tuple(
        f"liuyao_classics_review_20260822_{index:04d}"
        for index in range(1, 8)
    )
    assert tuple(item.source_ref for item in ledger.promotion_records) == (
        "page:28", "page:71", "page:332", "page:333",
        "page:493", "page:498", "page:501",
    )
    assert all(item.risk_tier == "ordinary" for item in ledger.promotion_records)
    assert all(item.confidence == "moderate" for item in ledger.promotion_records)
    assert tuple(
        (item.source_ref, item.disposition) for item in ledger.coverage
    ) == EXPECTED_COVERAGE


def test_targeted_classics_review_carries_no_forbidden_content() -> None:
    ledger = load_liuyao_targeted_classics_reviews()
    payload = json.dumps(
        json.loads(
            (LIUYAO_DATA_DIR / "liuyao_targeted_classics_reviews.json").read_text(
                encoding="utf-8"
            )
        ),
        ensure_ascii=False,
    )
    # forbidden markers are assembled at runtime so the raw user-file hash
    # and absolute path never persist as literals in the repository
    user_file_hash = (
        "A9497ADC18B28749436053EF8092940F"
        "4D168800B91DB59770EF24ECCEF303A0"
    )
    forbidden = (
        "E:" + "\\" + "命理演绎",
        user_file_hash,
        user_file_hash.lower(),
        "必定",
        "注定",
        "一定会",
        "死定",
    )
    assert not any(marker in payload for marker in forbidden)
    for record in ledger.promotion_records:
        # every promoted record is a single-page locator
        assert record.source_ref.startswith("page:")
        assert "-" not in record.source_ref


def _write_variant(tmp_path: Path, mutate) -> Path:
    payload = json.loads(
        (LIUYAO_DATA_DIR / "liuyao_targeted_classics_reviews.json").read_text(
            encoding="utf-8"
        )
    )
    mutate(payload)
    variant = tmp_path / "variant.json"
    variant.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return variant


class TestTargetedClassicsReviewLoaderStrictness:
    def test_rejects_non_list_sequence_fields(self, tmp_path: Path) -> None:
        variant = _write_variant(
            tmp_path,
            lambda payload: payload["promotion_records"][0].update(
                applicability="not-a-list"
            ),
        )
        with pytest.raises(LiuyaoKnowledgeError):
            load_liuyao_targeted_classics_reviews(variant)

    def test_rejects_unknown_record_fields(self, tmp_path: Path) -> None:
        variant = _write_variant(
            tmp_path,
            lambda payload: payload["promotion_records"][0].update(extra="x"),
        )
        with pytest.raises(LiuyaoKnowledgeError):
            load_liuyao_targeted_classics_reviews(variant)

    @pytest.mark.parametrize("locator", ("page:abc", "page:", "page:0"))
    def test_rejects_non_canonical_single_page_locators(
        self, tmp_path: Path, locator: str
    ) -> None:
        variant = _write_variant(
            tmp_path,
            lambda payload: payload["promotion_records"][0].update(
                source_ref=locator
            ),
        )
        with pytest.raises(LiuyaoKnowledgeError):
            load_liuyao_targeted_classics_reviews(variant)

    def test_rejects_non_frozen_record_id_sequence(self, tmp_path: Path) -> None:
        def _swap(payload) -> None:
            records = payload["promotion_records"]
            records[0]["record_id"], records[1]["record_id"] = (
                records[1]["record_id"],
                records[0]["record_id"],
            )

        variant = _write_variant(tmp_path, _swap)
        with pytest.raises(LiuyaoKnowledgeError):
            load_liuyao_targeted_classics_reviews(variant)

    def test_rejects_reversed_coverage_page_range(self, tmp_path: Path) -> None:
        variant = _write_variant(
            tmp_path,
            lambda payload: payload["coverage"][0].update(
                source_ref="page:29-27"
            ),
        )
        with pytest.raises(LiuyaoKnowledgeError):
            load_liuyao_targeted_classics_reviews(variant)

    def test_rejects_unknown_coverage_links(self, tmp_path: Path) -> None:
        variant = _write_variant(
            tmp_path,
            lambda payload: payload["coverage"][0].update(
                linked_record_ids=["liuyao_classics_review_20260822_0099"]
            ),
        )
        with pytest.raises(LiuyaoKnowledgeError):
            load_liuyao_targeted_classics_reviews(variant)
