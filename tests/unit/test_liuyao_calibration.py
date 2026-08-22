import json
from pathlib import Path

import pytest

from mingli_engine.liuyao.calibration import (
    LiuyaoCalibrationError,
    evaluate_assertion,
    load_calibration_assertions,
    load_calibration_cases,
    run_calibration,
)

CAL_DIR = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "mingli_engine"
    / "data"
    / "liuyao"
    / "calibration"
)


def test_calibration_corpus_shape_and_synthetic_boundary() -> None:
    cases = load_calibration_cases(CAL_DIR)
    assertions = load_calibration_assertions(CAL_DIR)
    assert len(cases) >= 6
    assert len(assertions) >= 40
    assert sum(item.safety_critical for item in assertions) >= 8
    assert {item.case_id for item in assertions} == {item.case_id for item in cases}
    families = {item.rule_family for item in assertions}
    from mingli_engine.liuyao.constants import LIUYAO_RULE_FAMILIES

    assert families == set(LIUYAO_RULE_FAMILIES)
    payload = json.dumps(
        [json.loads(path.read_text(encoding="utf-8")) for path in CAL_DIR.glob("*.json")],
        ensure_ascii=False,
    )
    assert "contains_real_personal_data" not in payload
    for case in cases:
        assert case.request["request_id"] is None


def test_calibration_metrics_meet_release_thresholds() -> None:
    metrics = run_calibration()
    assert metrics["adjudicated_count"] == 72
    assert metrics["counted_assertion_count"] == 72
    assert metrics["engine_match_rate"] == 1.0
    assert metrics["reviewer_agreement_rate"] >= 0.7
    assert metrics["safety_critical_match_rate"] == 1.0


def test_calibration_requires_complete_dual_review_coverage(tmp_path: Path) -> None:
    staged = tmp_path / "calibration"
    staged.mkdir()
    for path in CAL_DIR.glob("*.json"):
        staged.joinpath(path.name).write_bytes(path.read_bytes())
    reviews = json.loads((staged / "reviewer_b_reviews.json").read_text(encoding="utf-8"))
    reviews.pop()
    (staged / "reviewer_b_reviews.json").write_text(
        json.dumps(reviews, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with pytest.raises(LiuyaoCalibrationError, match="exactly once"):
        run_calibration(data_dir=staged)


def test_calibration_rejects_inconsistent_adjudication_state(tmp_path: Path) -> None:
    staged = tmp_path / "calibration"
    staged.mkdir()
    for path in CAL_DIR.glob("*.json"):
        staged.joinpath(path.name).write_bytes(path.read_bytes())
    adjudication = json.loads((staged / "adjudication.json").read_text(encoding="utf-8"))
    adjudication[0]["agreement_state"] = "disagreement"
    (staged / "adjudication.json").write_text(
        json.dumps(adjudication, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with pytest.raises(LiuyaoCalibrationError, match="inconsistent"):
        run_calibration(data_dir=staged)


def test_evaluate_assertion_matches_engine_behavior() -> None:
    cases = {item.case_id: item for item in load_calibration_cases(CAL_DIR)}
    assertions = load_calibration_assertions(CAL_DIR)
    first = assertions[0]
    assert evaluate_assertion(first, cases) is True
    tampered = type(first)(
        assertion_id=first.assertion_id,
        case_id=first.case_id,
        rule_family=first.rule_family,
        check_type=first.check_type,
        expected="不存在的文本",
        safety_critical=first.safety_critical,
    )
    assert evaluate_assertion(tampered, cases) is False
