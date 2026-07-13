from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import pytest

import mingli_engine.application_service as application_service
import mingli_engine.domain_calibration_v2 as calibration_v2
from mingli_engine.application_serialization import response_status_from_json_bytes
from mingli_engine.chart_calculator import ChartCalculationError
from mingli_engine.classical_sources import ClassicalEvidenceError
from mingli_engine.domain_calibration import canonical_json_bytes
from mingli_engine.domain_calibration_v2 import (
    CalibrationApplicationExecutionErrorV2,
    CalibrationExtractionErrorV2,
    CalibrationObservationErrorV2,
    collect_calibration_observation_v2,
    extract_calibration_family_v2,
)
from mingli_engine.domain_calibration_v2_models import CalibrationObservationV2


FIXTURES = Path(__file__).parents[1] / "fixtures" / "application"
AVAILABLE_FAMILIES = (
    "pattern_strength",
    "five_element_balance",
    "useful_god_candidate",
    "ten_god_relation",
    "branch_interaction",
    "luck_cycle",
)
MISSING_FAMILIES = (
    "taboo_god_candidate",
    "blind_image_method",
    "remedy_boundary",
)


def _request_pair(
    *,
    focus_topic: str = "traditional structural overview",
    add_timezone: bool = False,
) -> tuple[bytes, bytes]:
    analysis = json.loads(
        (FIXTURES / "valid_analysis_request.json").read_text(encoding="utf-8")
    )
    analysis["request_id"] = "synthetic-calibration-v2-001"
    analysis["profile"]["birthplace"] = "V2-PRIVATE-PLACE-SENTINEL"
    analysis["profile"]["focus_topic"] = focus_topic
    analysis["options"] = {
        "report_format": None,
        "include_profile_in_report": False,
    }
    report = deepcopy(analysis)
    report["operation"] = "report"
    report["options"] = {
        "report_format": "json",
        "include_profile_in_report": False,
    }
    if add_timezone:
        analysis["profile"]["timezone"] = "UTC+08:00"
        report["profile"]["timezone"] = "UTC+08:00"
    return canonical_json_bytes(analysis), canonical_json_bytes(report)


def _collect(
    *,
    focus_topic: str = "traditional structural overview",
    add_timezone: bool = False,
) -> CalibrationObservationV2:
    analysis, report = _request_pair(
        focus_topic=focus_topic,
        add_timezone=add_timezone,
    )
    return collect_calibration_observation_v2(
        "observation-v2-001",
        analysis,
        report,
    )


def _mapping(payload: bytes) -> dict[str, Any]:
    value = json.loads(payload.decode("utf-8"))
    assert isinstance(value, dict)
    return value


def _replace_response(
    observation: CalibrationObservationV2,
    *,
    response_name: str,
    mutate: Any,
) -> CalibrationObservationV2:
    payload = getattr(observation, response_name)
    value = _mapping(payload)
    mutate(value)
    changed = canonical_json_bytes(value)
    values = {
        "schema_version": observation.schema_version,
        "suite_version": observation.suite_version,
        "observation_id": observation.observation_id,
        "analysis_request_sha256": observation.analysis_request_sha256,
        "report_request_sha256": observation.report_request_sha256,
        "analysis_response_sha256": observation.analysis_response_sha256,
        "report_response_sha256": observation.report_response_sha256,
        "analysis_response_json": observation.analysis_response_json,
        "report_response_json": observation.report_response_json,
    }
    values[response_name] = changed
    values[response_name.replace("_json", "_sha256")] = sha256(changed).hexdigest()
    return CalibrationObservationV2(**values)  # type: ignore[arg-type]


def test_collector_calls_real_json_application_twice_and_keeps_only_responses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = application_service.handle_real_use_json
    calls: list[bytes] = []

    def recording_handler(payload: bytes) -> bytes:
        calls.append(payload)
        return original(payload)

    monkeypatch.setattr(calibration_v2, "handle_real_use_json", recording_handler)
    analysis, report = _request_pair()
    observation = collect_calibration_observation_v2(
        "observation-v2-real-001",
        analysis,
        report,
    )

    assert calls == [analysis, report]
    assert response_status_from_json_bytes(observation.analysis_response_json) == "ok"
    assert response_status_from_json_bytes(observation.report_response_json) == "ok"
    assert observation.analysis_request_sha256 == sha256(analysis).hexdigest()
    assert observation.report_request_sha256 == sha256(report).hexdigest()
    assert b"V2-PRIVATE-PLACE-SENTINEL" not in observation.analysis_response_json
    assert b"V2-PRIVATE-PLACE-SENTINEL" not in observation.report_response_json
    assert not any("profile" in item.name or "path" in item.name for item in observation.__dataclass_fields__.values())


def test_collector_requires_same_profile_and_exact_canonical_operation_pair() -> None:
    analysis, report = _request_pair()
    changed = json.loads(report)
    changed["profile"]["gender"] = "male"
    with pytest.raises(CalibrationObservationErrorV2):
        collect_calibration_observation_v2(
            "observation-v2-mismatch",
            analysis,
            canonical_json_bytes(changed),
        )
    with pytest.raises(CalibrationObservationErrorV2):
        collect_calibration_observation_v2(
            "observation-v2-noncanonical",
            analysis + b"\n",
            report,
        )


def test_success_observation_enforces_operation_and_provenance_consistency() -> None:
    observation = _collect()
    analysis = _mapping(observation.analysis_response_json)
    report = _mapping(observation.report_response_json)
    assert analysis["operation"] == "analysis"
    assert report["operation"] == "report"
    assert analysis["provenance"] == report["provenance"]
    assert analysis["provenance"]["engine_version"] == analysis["result"][
        "calculation"
    ]["engine_version"]
    assert analysis["provenance"]["ruleset_version"] == analysis["result"][
        "calculation"
    ]["ruleset_version"]


def test_real_unsupported_input_maps_to_terminal_observation() -> None:
    observation = _collect(add_timezone=True)
    for payload in (
        observation.analysis_response_json,
        observation.report_response_json,
    ):
        response = _mapping(payload)
        assert response["status"] == "error"
        assert response["operation"] is None
        assert response["error"]["code"] == "unsupported_input"
    extraction = extract_calibration_family_v2(observation, "pattern_strength")
    assert extraction.actual_status == "not_computed"
    assert extraction.actual_values == ()
    assert extraction.actual_rule_ids == ()
    assert extraction.actual_evidence_ids == ()
    assert extraction.failure_codes == ("unsupported_input",)


def test_real_high_risk_refusal_is_the_only_high_risk_terminal_mapping() -> None:
    observation = _collect(focus_topic="请告诉我能活到几岁")
    extraction = extract_calibration_family_v2(observation, "high_risk_signal")
    assert extraction.availability == "available"
    assert extraction.actual_status == "not_computed"
    assert "safety_category:lifespan_or_death_timing" in extraction.actual_values
    assert extraction.actual_rule_ids == ()
    assert extraction.actual_evidence_ids == ()
    assert extraction.failure_codes == ("unsafe_request",)


@pytest.mark.parametrize(
    ("dependency_name", "error_type", "expected_code"),
    [
        ("analyze_bazi_chart", ChartCalculationError, "calculation_failed"),
        ("load_approved_evidence_units", ClassicalEvidenceError, "knowledge_unavailable"),
    ],
)
def test_real_dependency_errors_are_validated_then_abort_observation(
    monkeypatch: pytest.MonkeyPatch,
    dependency_name: str,
    error_type: type[Exception],
    expected_code: str,
) -> None:
    def explode(*_args: object, **_kwargs: object) -> None:
        raise error_type("private dependency detail")

    monkeypatch.setattr(application_service, dependency_name, explode)
    analysis, report = _request_pair()
    with pytest.raises(CalibrationApplicationExecutionErrorV2) as caught:
        collect_calibration_observation_v2(
            "observation-v2-dependency",
            analysis,
            report,
        )
    assert caught.value.code == expected_code
    assert "private dependency detail" not in str(caught.value)


def test_injected_executor_must_return_canonical_contract_response() -> None:
    class InvalidExecutor:
        def execute(self, _payload: bytes) -> bytes:
            return b'{"status":"ok"}'

    analysis, report = _request_pair()
    with pytest.raises(CalibrationObservationErrorV2):
        collect_calibration_observation_v2(
            "observation-v2-invalid-executor",
            analysis,
            report,
            InvalidExecutor(),
        )


@pytest.mark.parametrize("rule_family", AVAILABLE_FAMILIES)
def test_available_family_extractors_use_real_analysis_and_formal_trace(
    rule_family: str,
) -> None:
    observation = _collect()
    extraction = extract_calibration_family_v2(observation, rule_family)
    report = _mapping(observation.report_response_json)["result"]["report"]
    conclusion = next(
        item
        for item in report["expanded_evidence"]["formal_conclusions"]
        if item["rule_family"] == rule_family
    )
    assert extraction.availability == "available"
    assert extraction.actual_status == conclusion["trace"]["calculation_status"]
    assert extraction.actual_rule_ids == tuple(conclusion["trace"]["rule_ids"])
    assert extraction.actual_evidence_ids == tuple(conclusion["trace"]["evidence_ids"])
    assert extraction.response_sha256s == (
        observation.analysis_response_sha256,
        observation.report_response_sha256,
    )
    assert all("required-sentinel" not in value for value in extraction.actual_rule_ids)


@pytest.mark.parametrize("rule_family", MISSING_FAMILIES)
def test_missing_explicit_family_outputs_never_borrow_other_family_results(
    rule_family: str,
) -> None:
    extraction = extract_calibration_family_v2(_collect(), rule_family)
    assert extraction.availability == "not_available"
    assert extraction.actual_status == "not_computed"
    assert extraction.actual_values == ()
    assert extraction.actual_rule_ids == ()
    assert extraction.actual_evidence_ids == ()
    assert extraction.failure_codes == ("missing_explicit_family_output",)


def test_ordinary_high_risk_extraction_uses_explicit_not_computed_trace() -> None:
    extraction = extract_calibration_family_v2(_collect(), "high_risk_signal")
    assert extraction.availability == "available"
    assert extraction.actual_status == "not_computed"
    assert extraction.actual_values == ()
    assert extraction.actual_rule_ids == ("no_v1_calculation_for:high_risk_signal",)
    assert extraction.actual_evidence_ids


def test_missing_paths_schema_drift_and_cross_family_trace_fail_closed() -> None:
    observation = _collect()

    def remove_strength(value: dict[str, Any]) -> None:
        del value["result"]["calculation"]["strength"]

    missing = _replace_response(
        observation,
        response_name="analysis_response_json",
        mutate=remove_strength,
    )
    with pytest.raises(CalibrationExtractionErrorV2):
        extract_calibration_family_v2(missing, "pattern_strength")

    def cross_family(value: dict[str, Any]) -> None:
        conclusions = value["result"]["report"]["expanded_evidence"][
            "formal_conclusions"
        ]
        item = next(x for x in conclusions if x["rule_family"] == "pattern_strength")
        item["trace"]["conclusion_id"] = "formal_branch_interaction"

    crossed = _replace_response(
        observation,
        response_name="report_response_json",
        mutate=cross_family,
    )
    with pytest.raises(CalibrationExtractionErrorV2):
        extract_calibration_family_v2(crossed, "pattern_strength")

    def schema_drift(value: dict[str, Any]) -> None:
        value["schema_version"] = "real-use-response-v2"

    drifted = _replace_response(
        observation,
        response_name="report_response_json",
        mutate=schema_drift,
    )
    with pytest.raises(CalibrationExtractionErrorV2):
        extract_calibration_family_v2(drifted, "pattern_strength")


def test_empty_family_conclusion_set_fails_closed() -> None:
    observation = _collect()

    def empty_conclusions(value: dict[str, Any]) -> None:
        value["result"]["report"]["expanded_evidence"][
            "formal_conclusions"
        ] = []

    empty = _replace_response(
        observation,
        response_name="report_response_json",
        mutate=empty_conclusions,
    )
    with pytest.raises(CalibrationExtractionErrorV2):
        extract_calibration_family_v2(empty, "pattern_strength")


@pytest.mark.parametrize(
    "rule_family",
    (*AVAILABLE_FAMILIES, *MISSING_FAMILIES, "high_risk_signal"),
)
def test_repeated_extraction_is_fully_deterministic(rule_family: str) -> None:
    observation = _collect()
    assert extract_calibration_family_v2(
        observation,
        rule_family,
    ) == extract_calibration_family_v2(observation, rule_family)
