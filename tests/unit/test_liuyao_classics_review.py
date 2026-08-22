import json
from pathlib import Path

from mingli_engine.liuyao.knowledge import load_liuyao_targeted_classics_reviews

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
    forbidden = (
        "E:\\命理演绎",
        "A9497ADC18B28749436053EF8092940F4D168800B91DB59770EF24ECCEF303A0",
        "a9497adc18b28749436053ef8092940f4d168800b91db59770ef24eccef303a0",
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
