"""Liuyao V1 calibration corpus and conformance runner (synthetic cases only)."""

from __future__ import annotations

from dataclasses import dataclass
import json
from importlib import resources
from pathlib import Path
from typing import Any

from mingli_engine.liuyao.analysis import analyze_liuyao_chart
from mingli_engine.liuyao.casting import assemble_liuyao_chart
from mingli_engine.liuyao.constants import LIUYAO_RULE_FAMILIES
from mingli_engine.liuyao.result_models import LiuyaoCastRequest, LiuyaoLineInput

CALIBRATION_SCHEMA = "liuyao-calibration-v1"


class LiuyaoCalibrationError(ValueError):
    """Raised when a calibration artifact is invalid."""


@dataclass(frozen=True)
class CalibrationCase:
    case_id: str
    request: dict[str, Any]
    note: str

    def __post_init__(self) -> None:
        if not self.case_id.strip() or not isinstance(self.request, dict):
            raise ValueError("calibration case is invalid")


@dataclass(frozen=True)
class CalibrationAssertion:
    assertion_id: str
    case_id: str
    rule_family: str
    check_type: str
    expected: str
    safety_critical: bool = False

    def __post_init__(self) -> None:
        if not self.assertion_id.strip() or not self.case_id.strip():
            raise ValueError("calibration assertion ids are required")
        if self.rule_family not in LIUYAO_RULE_FAMILIES:
            raise ValueError("calibration assertion family is outside the namespace")
        if self.check_type not in {"contains", "not_contains", "status_equals"}:
            raise ValueError("calibration assertion check type is invalid")
        if not self.expected.strip():
            raise ValueError("calibration assertion expected value is required")
        if not isinstance(self.safety_critical, bool):
            raise ValueError("calibration assertion safety flag must be boolean")


@dataclass(frozen=True)
class ReviewerReview:
    review_id: str
    reviewer: str
    assertion_id: str
    label: str
    rationale: str

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.review_id, "review_id"),
            (self.reviewer, "reviewer"),
            (self.assertion_id, "assertion_id"),
            (self.rationale, "rationale"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"calibration review {field_name} is required")
        if self.label not in {"accept", "reject"}:
            raise ValueError("calibration review label must be accept or reject")


@dataclass(frozen=True)
class AdjudicationRecord:
    assertion_id: str
    reviewer_a_review_id: str
    reviewer_b_review_id: str
    agreement_state: str
    decision: str
    rationale: str

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.assertion_id, "assertion_id"),
            (self.reviewer_a_review_id, "reviewer_a_review_id"),
            (self.reviewer_b_review_id, "reviewer_b_review_id"),
            (self.rationale, "rationale"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"calibration adjudication {field_name} is required")
        if self.agreement_state not in {"agreement", "disagreement"}:
            raise ValueError("calibration adjudication agreement state is invalid")
        if self.decision not in {"counted", "excluded"}:
            raise ValueError("calibration adjudication decision is invalid")


def _calibration_dir(data_dir: Path | None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    return Path(
        str(resources.files("mingli_engine").joinpath("data/liuyao/calibration"))
    )


def _load_json(name: str, data_dir: Path | None) -> Any:
    path = _calibration_dir(data_dir) / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LiuyaoCalibrationError(f"the liuyao {name} artifact is unavailable") from error


def load_calibration_cases(data_dir: Path | None = None) -> tuple[CalibrationCase, ...]:
    raw = _load_json("calibration_cases.json", data_dir)
    if not isinstance(raw, list):
        raise LiuyaoCalibrationError("calibration cases must be a JSON array")
    try:
        cases = tuple(CalibrationCase(**item) for item in raw)
    except (TypeError, ValueError) as error:
        raise LiuyaoCalibrationError("calibration cases are invalid") from error
    if len({item.case_id for item in cases}) != len(cases):
        raise LiuyaoCalibrationError("calibration case ids must be unique")
    for case in cases:
        try:
            _request_from_dict(case.request)
        except (TypeError, ValueError) as error:
            raise LiuyaoCalibrationError(
                f"calibration case {case.case_id} request is invalid"
            ) from error
    return cases


def load_calibration_assertions(
    data_dir: Path | None = None,
) -> tuple[CalibrationAssertion, ...]:
    raw = _load_json("calibration_assertions.json", data_dir)
    if not isinstance(raw, list):
        raise LiuyaoCalibrationError("calibration assertions must be a JSON array")
    try:
        assertions = tuple(CalibrationAssertion(**item) for item in raw)
    except (TypeError, ValueError) as error:
        raise LiuyaoCalibrationError("calibration assertions are invalid") from error
    if len({item.assertion_id for item in assertions}) != len(assertions):
        raise LiuyaoCalibrationError("calibration assertion ids must be unique")
    return assertions


def load_reviewer_reviews(
    reviewer: str,
    data_dir: Path | None = None,
) -> tuple[ReviewerReview, ...]:
    raw = _load_json(f"reviewer_{reviewer}_reviews.json", data_dir)
    if not isinstance(raw, list):
        raise LiuyaoCalibrationError("reviewer reviews must be a JSON array")
    try:
        reviews = tuple(ReviewerReview(**item) for item in raw)
    except (TypeError, ValueError) as error:
        raise LiuyaoCalibrationError("reviewer reviews are invalid") from error
    if any(item.reviewer != f"reviewer_{reviewer}" for item in reviews):
        raise LiuyaoCalibrationError("reviewer review identity mismatch")
    if len({item.assertion_id for item in reviews}) != len(reviews):
        raise LiuyaoCalibrationError("reviewer reviews must cover assertions once")
    return reviews


def load_adjudication(data_dir: Path | None = None) -> tuple[AdjudicationRecord, ...]:
    raw = _load_json("adjudication.json", data_dir)
    if not isinstance(raw, list):
        raise LiuyaoCalibrationError("calibration adjudication must be a JSON array")
    try:
        records = tuple(AdjudicationRecord(**item) for item in raw)
    except (TypeError, ValueError) as error:
        raise LiuyaoCalibrationError("calibration adjudication is invalid") from error
    if len({item.assertion_id for item in records}) != len(records):
        raise LiuyaoCalibrationError("adjudication must cover assertions once")
    return records


def _request_from_dict(payload: dict[str, Any]) -> LiuyaoCastRequest:
    return LiuyaoCastRequest(
        cast_mode=payload["cast_mode"],
        cast_datetime=payload["cast_datetime"],
        lines=tuple(
            LiuyaoLineInput(
                position=item["position"],
                yin_yang=item["yin_yang"],
                moving=item["moving"],
            )
            for item in payload.get("lines", [])
        ),
        numbers=tuple(payload.get("numbers", [])),
        request_id=payload.get("request_id"),
    )


def _family_text(case_id: str, rule_family: str, cases: dict[str, CalibrationCase]) -> tuple[str, str]:
    request = _request_from_dict(cases[case_id].request)
    analysis = analyze_liuyao_chart(assemble_liuyao_chart(request))
    observation = {
        item.rule_family: item for item in analysis.family_observations
    }[rule_family]
    return " ".join(observation.observations), observation.status


def evaluate_assertion(
    assertion: CalibrationAssertion,
    cases: dict[str, CalibrationCase],
) -> bool:
    """Evaluate one assertion against the live engine output."""
    text, status = _family_text(assertion.case_id, assertion.rule_family, cases)
    if assertion.check_type == "contains":
        return assertion.expected in text
    if assertion.check_type == "not_contains":
        return assertion.expected not in text
    return status == assertion.expected


def run_calibration(
    *,
    data_dir: Path | None = None,
) -> dict[str, object]:
    """Compute conformance metrics over adjudicated assertions."""
    cases_list = load_calibration_cases(data_dir)
    assertions = load_calibration_assertions(data_dir)
    reviews_a = load_reviewer_reviews("a", data_dir)
    reviews_b = load_reviewer_reviews("b", data_dir)
    adjudication = load_adjudication(data_dir)
    cases = {item.case_id: item for item in cases_list}
    assertion_ids = {item.assertion_id for item in assertions}
    if not (
        {item.assertion_id for item in reviews_a}
        == {item.assertion_id for item in reviews_b}
        == {item.assertion_id for item in adjudication}
        == assertion_ids
    ):
        raise LiuyaoCalibrationError(
            "reviews and adjudication must cover every assertion exactly once"
        )
    review_a_by_id = {item.assertion_id: item for item in reviews_a}
    review_b_by_id = {item.assertion_id: item for item in reviews_b}
    agreement = 0
    for record in adjudication:
        a = review_a_by_id[record.assertion_id]
        b = review_b_by_id[record.assertion_id]
        expected_state = "agreement" if a.label == b.label else "disagreement"
        if record.agreement_state != expected_state:
            raise LiuyaoCalibrationError("adjudication agreement state is inconsistent")
        if a.label == b.label == "accept" and record.decision != "counted":
            raise LiuyaoCalibrationError("accepted assertions must be counted")
        if expected_state == "agreement":
            agreement += 1
    counted = [item for item in adjudication if item.decision == "counted"]
    if not counted:
        raise LiuyaoCalibrationError("no adjudicated assertions are counted")
    assertion_by_id = {item.assertion_id: item for item in assertions}
    engine_matches = 0
    safety_critical_total = 0
    safety_critical_matches = 0
    for record in counted:
        assertion = assertion_by_id[record.assertion_id]
        matched = evaluate_assertion(assertion, cases)
        engine_matches += int(matched)
        if assertion.safety_critical:
            safety_critical_total += 1
            safety_critical_matches += int(matched)
    total = len(counted)
    return {
        "adjudicated_count": len(adjudication),
        "counted_assertion_count": total,
        "engine_match_rate": engine_matches / total,
        "reviewer_agreement_rate": agreement / len(adjudication),
        "safety_critical_match_rate": (
            safety_critical_matches / safety_critical_total
            if safety_critical_total
            else 1.0
        ),
        "schema_version": CALIBRATION_SCHEMA,
    }