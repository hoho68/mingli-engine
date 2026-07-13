from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from hashlib import sha256
import inspect

import pytest

from mingli_engine.domain_calibration_v2 import (
    ApplicationJsonExecutorV2,
    collect_calibration_observation_v2,
    extract_calibration_family_v2,
    get_calibration_extractor_registry_v2,
)
from mingli_engine.domain_calibration_v2_models import (
    CALIBRATION_EXTRACTION_SCHEMA_V2,
    CALIBRATION_OBSERVATION_SCHEMA_V2,
    DOMAIN_CALIBRATION_SUITE_V2,
    CalibrationExtractionV2,
    CalibrationObservationV2,
)
from mingli_engine.formal_interpretation import (
    get_formal_interpretation_rule_families,
)


HASH_A = "a" * 64
HASH_B = "b" * 64
RESPONSE = b'{"status":"ok"}'


def _observation(**changes: object) -> CalibrationObservationV2:
    values: dict[str, object] = {
        "schema_version": CALIBRATION_OBSERVATION_SCHEMA_V2,
        "suite_version": DOMAIN_CALIBRATION_SUITE_V2,
        "observation_id": "observation-v2-001",
        "analysis_request_sha256": HASH_A,
        "report_request_sha256": HASH_B,
        "analysis_response_sha256": sha256(RESPONSE).hexdigest(),
        "report_response_sha256": sha256(RESPONSE).hexdigest(),
        "analysis_response_json": RESPONSE,
        "report_response_json": RESPONSE,
    }
    values.update(changes)
    return CalibrationObservationV2(**values)  # type: ignore[arg-type]


def _extraction(**changes: object) -> CalibrationExtractionV2:
    values: dict[str, object] = {
        "schema_version": CALIBRATION_EXTRACTION_SCHEMA_V2,
        "suite_version": DOMAIN_CALIBRATION_SUITE_V2,
        "observation_id": "observation-v2-001",
        "rule_family": "pattern_strength",
        "availability": "available",
        "actual_status": "computed",
        "actual_values": ["strength_label:balanced"],
        "actual_rule_ids": ["strength.month_command.officer"],
        "actual_evidence_ids": ["mingxue_pattern_strength_001"],
        "failure_codes": [],
        "response_sha256s": [HASH_A, HASH_B],
    }
    values.update(changes)
    return CalibrationExtractionV2(**values)  # type: ignore[arg-type]


def test_v2_models_have_exact_fields_and_explicit_v2_identity() -> None:
    assert [item.name for item in fields(CalibrationObservationV2)] == [
        "schema_version",
        "suite_version",
        "observation_id",
        "analysis_request_sha256",
        "report_request_sha256",
        "analysis_response_sha256",
        "report_response_sha256",
        "analysis_response_json",
        "report_response_json",
    ]
    assert [item.name for item in fields(CalibrationExtractionV2)] == [
        "schema_version",
        "suite_version",
        "observation_id",
        "rule_family",
        "availability",
        "actual_status",
        "actual_values",
        "actual_rule_ids",
        "actual_evidence_ids",
        "failure_codes",
        "response_sha256s",
    ]
    assert DOMAIN_CALIBRATION_SUITE_V2 == "domain-calibration-suite-v2"
    assert CALIBRATION_OBSERVATION_SCHEMA_V2 == "domain-calibration-observation-v2"
    assert CALIBRATION_EXTRACTION_SCHEMA_V2 == "domain-calibration-extraction-v2"


def test_v2_models_are_frozen_and_normalize_sequence_fields_to_tuples() -> None:
    observation = _observation()
    extraction = _extraction()
    assert extraction.actual_values == ("strength_label:balanced",)
    assert extraction.actual_rule_ids == ("strength.month_command.officer",)
    assert extraction.actual_evidence_ids == ("mingxue_pattern_strength_001",)
    assert extraction.failure_codes == ()
    assert extraction.response_sha256s == (HASH_A, HASH_B)
    with pytest.raises(FrozenInstanceError):
        observation.observation_id = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        extraction.actual_status = "disputed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("factory", "changes", "error_type"),
    [
        (_observation, {"schema_version": "domain-calibration-observation-v1"}, ValueError),
        (_observation, {"suite_version": "domain-calibration-suite-v1"}, ValueError),
        (_observation, {"analysis_response_json": bytearray(RESPONSE)}, TypeError),
        (_observation, {"analysis_request_sha256": "not-a-hash"}, ValueError),
        (_observation, {"analysis_response_sha256": HASH_A}, ValueError),
        (_extraction, {"schema_version": "domain-calibration-extraction-v1"}, ValueError),
        (_extraction, {"availability": "supported"}, ValueError),
        (_extraction, {"actual_status": "unsupported"}, ValueError),
        (_extraction, {"actual_values": [1]}, TypeError),
        (_extraction, {"response_sha256s": [HASH_A]}, ValueError),
    ],
)
def test_v2_models_fail_closed_on_wrong_runtime_values(
    factory: object,
    changes: dict[str, object],
    error_type: type[Exception],
) -> None:
    with pytest.raises(error_type):
        factory(**changes)  # type: ignore[operator]


def test_extractor_registry_exactly_matches_authoritative_families() -> None:
    registry = get_calibration_extractor_registry_v2()
    assert tuple(registry) == get_formal_interpretation_rule_families()
    assert len(registry) == len(set(registry)) == 10
    with pytest.raises(TypeError):
        registry["extra"] = lambda value: value  # type: ignore[index]


def test_collector_executor_and_extractors_expose_no_expectation_inputs() -> None:
    collector_names = tuple(inspect.signature(collect_calibration_observation_v2).parameters)
    assert collector_names == (
        "observation_id",
        "analysis_request_json",
        "report_request_json",
        "executor",
    )
    assert inspect.isclass(ApplicationJsonExecutorV2)
    for extractor in get_calibration_extractor_registry_v2().values():
        assert tuple(inspect.signature(extractor).parameters) == ("observation",)
    assert tuple(inspect.signature(extract_calibration_family_v2).parameters) == (
        "observation",
        "rule_family",
    )


def test_v2_extraction_source_has_no_v1_expectation_or_review_dependencies() -> None:
    module = inspect.getmodule(extract_calibration_family_v2)
    assert module is not None
    source = inspect.getsource(module)
    for forbidden in (
        "acceptable_values",
        "required_rule_ids",
        "required_evidence_ids",
        "coverage_tags",
        "case_signal",
        "CalibrationAssertion",
        "AdjudicationDecision",
        "CalibrationReview",
        "ReviewerPacket",
    ):
        assert forbidden not in source


def test_unrelated_expectation_objects_cannot_change_frozen_extraction() -> None:
    extraction = _extraction()
    fake_assertion = {"acceptable_values": ["first"]}
    fake_adjudication = {"final_acceptable_values": ["second"]}
    before = replace(extraction)
    fake_assertion["acceptable_values"] = ["changed"]
    fake_adjudication["final_acceptable_values"] = ["changed"]
    assert extraction == before
