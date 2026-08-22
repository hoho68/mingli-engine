from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Any, Literal


DOMAIN_CALIBRATION_SUITE_V2: Literal["domain-calibration-suite-v2"] = (
    "domain-calibration-suite-v2"
)
CALIBRATION_OBSERVATION_SCHEMA_V2: Literal[
    "domain-calibration-observation-v2"
] = "domain-calibration-observation-v2"
CALIBRATION_EXTRACTION_SCHEMA_V2: Literal[
    "domain-calibration-extraction-v2"
] = "domain-calibration-extraction-v2"
CALIBRATION_EXECUTABLE_FIXTURE_SCHEMA_V2: Literal[
    "domain-calibration-executable-fixture-v2"
] = "domain-calibration-executable-fixture-v2"
CALIBRATION_FIXTURE_FILE_SCHEMA_V2: Literal[
    "domain-calibration-fixture-file-v2"
] = "domain-calibration-fixture-file-v2"

CalibrationAvailabilityV2 = Literal["available", "not_available"]
CalibrationActualStatusV2 = Literal[
    "not_computed", "computed", "indeterminate", "disputed"
]

_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_AVAILABILITIES = frozenset({"available", "not_available"})
_ACTUAL_STATUSES = frozenset(
    {"not_computed", "computed", "indeterminate", "disputed"}
)
_SCENARIO_KINDS = frozenset(
    {
        "normal_analysis_report",
        "aware_datetime_rejection",
        "dependency_degradation",
        "empty_branch_relations",
        "severe_conflict",
        "unknown_gender",
        "high_risk_refusal",
        "school_disagreement_ziping",
        "school_disagreement_liang_xiangrun",
        "school_disagreement_duan",
    }
)
_EXECUTION_POLICIES = frozenset(
    {"direct_application", "inject_calculation_failure"}
)
_INTERFACE_OUTCOMES = frozenset(
    {"ok", "unsupported_input", "unsafe_request", "calculation_failed"}
)


def _require_string(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise TypeError(f"{field_name} must be a nonempty trimmed string")


def _require_sha256(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    if _SHA256_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be a lowercase SHA-256")


def _string_tuple(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{field_name} must be a list or tuple")
    normalized = tuple(value)
    if not all(
        isinstance(item, str) and item and item == item.strip()
        for item in normalized
    ):
        raise TypeError(f"{field_name} must contain nonempty trimmed strings")
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{field_name} must not contain duplicates")
    return normalized


def _canonical_json_text(value: object, field_name: str) -> dict[str, Any]:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    try:
        parsed = json.loads(value)
    except (ValueError, RecursionError):
        raise ValueError(f"{field_name} must contain JSON") from None
    if not isinstance(parsed, dict):
        raise ValueError(f"{field_name} must contain a JSON object")
    canonical = json.dumps(
        parsed,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    if canonical != value:
        raise ValueError(f"{field_name} must be canonical JSON")
    return parsed


@dataclass(frozen=True)
class CalibrationObservationV2:
    schema_version: Literal["domain-calibration-observation-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    observation_id: str
    analysis_request_sha256: str
    report_request_sha256: str
    analysis_response_sha256: str
    report_response_sha256: str
    analysis_response_json: bytes
    report_response_json: bytes

    def __post_init__(self) -> None:
        if self.schema_version != CALIBRATION_OBSERVATION_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 observation schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        _require_string(self.observation_id, "observation_id")
        for field_name in (
            "analysis_request_sha256",
            "report_request_sha256",
            "analysis_response_sha256",
            "report_response_sha256",
        ):
            _require_sha256(getattr(self, field_name), field_name)
        for field_name in ("analysis_response_json", "report_response_json"):
            value = getattr(self, field_name)
            if type(value) is not bytes:
                raise TypeError(f"{field_name} must be bytes")
            expected_hash = getattr(self, field_name.replace("_json", "_sha256"))
            if sha256(value).hexdigest() != expected_hash:
                raise ValueError(f"{field_name} does not match its SHA-256")


@dataclass(frozen=True)
class CalibrationExtractionV2:
    schema_version: Literal["domain-calibration-extraction-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    observation_id: str
    rule_family: str
    availability: CalibrationAvailabilityV2
    actual_status: CalibrationActualStatusV2
    actual_values: tuple[str, ...]
    actual_rule_ids: tuple[str, ...]
    actual_evidence_ids: tuple[str, ...]
    failure_codes: tuple[str, ...]
    response_sha256s: tuple[str, str]

    def __post_init__(self) -> None:
        if self.schema_version != CALIBRATION_EXTRACTION_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 extraction schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        _require_string(self.observation_id, "observation_id")
        _require_string(self.rule_family, "rule_family")
        if self.availability not in _AVAILABILITIES:
            raise ValueError("availability is not supported")
        if self.actual_status not in _ACTUAL_STATUSES:
            raise ValueError("actual_status is not supported")
        for field_name in (
            "actual_values",
            "actual_rule_ids",
            "actual_evidence_ids",
            "failure_codes",
            "response_sha256s",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )
        if len(self.response_sha256s) != 2:
            raise ValueError("response_sha256s must contain exactly two values")
        for index, value in enumerate(self.response_sha256s):
            _require_sha256(value, f"response_sha256s[{index}]")
        if self.availability == "not_available" and (
            self.actual_status != "not_computed"
            or self.actual_values
            or self.actual_rule_ids
            or self.actual_evidence_ids
            or self.failure_codes != ("missing_explicit_family_output",)
        ):
            raise ValueError("not_available extraction must use the exact boundary")


@dataclass(frozen=True)
class CalibrationFixtureV2:
    schema_version: Literal["domain-calibration-executable-fixture-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    fixture_id: str
    scenario_kind: str
    execution_policy: str
    expected_interface_outcome: str
    analysis_request_json: str
    report_request_json: str
    analysis_request_sha256: str
    report_request_sha256: str
    contains_real_personal_data: bool

    def __post_init__(self) -> None:
        if self.schema_version != CALIBRATION_EXECUTABLE_FIXTURE_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 executable fixture schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        _require_string(self.fixture_id, "fixture_id")
        if self.scenario_kind not in _SCENARIO_KINDS:
            raise ValueError("scenario_kind is not registered")
        if self.execution_policy not in _EXECUTION_POLICIES:
            raise ValueError("execution_policy is not supported")
        if self.expected_interface_outcome not in _INTERFACE_OUTCOMES:
            raise ValueError("expected_interface_outcome is not supported")
        if (
            self.execution_policy == "inject_calculation_failure"
            and self.expected_interface_outcome != "calculation_failed"
        ) or (
            self.execution_policy == "direct_application"
            and self.expected_interface_outcome == "calculation_failed"
        ):
            raise ValueError("execution policy and interface outcome do not match")
        _canonical_json_text(self.analysis_request_json, "analysis_request_json")
        _canonical_json_text(self.report_request_json, "report_request_json")
        for field_name in ("analysis_request_sha256", "report_request_sha256"):
            _require_sha256(getattr(self, field_name), field_name)
        if sha256(self.analysis_request_json.encode("utf-8")).hexdigest() != (
            self.analysis_request_sha256
        ):
            raise ValueError("analysis_request_json does not match its SHA-256")
        if sha256(self.report_request_json.encode("utf-8")).hexdigest() != (
            self.report_request_sha256
        ):
            raise ValueError("report_request_json does not match its SHA-256")
        if type(self.contains_real_personal_data) is not bool:
            raise TypeError("contains_real_personal_data must be bool")
        if self.contains_real_personal_data:
            raise ValueError("executable fixtures must not contain real personal data")


@dataclass(frozen=True)
class CalibrationFixtureEnvelopeV2:
    schema_version: Literal["domain-calibration-fixture-file-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    generated_from: tuple[str, ...]
    contains_real_personal_data: bool
    payload_sha256: str
    records: tuple[CalibrationFixtureV2, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CALIBRATION_FIXTURE_FILE_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 fixture file schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        object.__setattr__(
            self,
            "generated_from",
            _string_tuple(self.generated_from, "generated_from"),
        )
        for index, value in enumerate(self.generated_from):
            _require_sha256(value, f"generated_from[{index}]")
        if type(self.contains_real_personal_data) is not bool:
            raise TypeError("contains_real_personal_data must be bool")
        if self.contains_real_personal_data:
            raise ValueError("fixture envelope must not contain real personal data")
        _require_sha256(self.payload_sha256, "payload_sha256")
        if not isinstance(self.records, (list, tuple)):
            raise TypeError("records must be a list or tuple")
        records = tuple(self.records)
        if not records or not all(
            isinstance(item, CalibrationFixtureV2) for item in records
        ):
            raise TypeError("records must contain CalibrationFixtureV2 values")
        object.__setattr__(self, "records", records)


@dataclass(frozen=True)
class CalibrationFixtureExecutionV2:
    fixture_id: str
    scenario_kind: str
    actual_interface_outcome: str
    observation: CalibrationObservationV2 | None
    extractions: tuple[CalibrationExtractionV2, ...]

    def __post_init__(self) -> None:
        _require_string(self.fixture_id, "fixture_id")
        if self.scenario_kind not in _SCENARIO_KINDS:
            raise ValueError("scenario_kind is not registered")
        if self.actual_interface_outcome not in _INTERFACE_OUTCOMES:
            raise ValueError("actual_interface_outcome is not supported")
        if self.observation is not None and not isinstance(
            self.observation, CalibrationObservationV2
        ):
            raise TypeError("observation must be CalibrationObservationV2 or None")
        if not isinstance(self.extractions, (list, tuple)):
            raise TypeError("extractions must be a list or tuple")
        extractions = tuple(self.extractions)
        if not all(
            isinstance(item, CalibrationExtractionV2) for item in extractions
        ):
            raise TypeError("extractions must contain CalibrationExtractionV2 values")
        object.__setattr__(self, "extractions", extractions)
        if self.observation is None:
            if self.actual_interface_outcome != "calculation_failed" or extractions:
                raise ValueError("missing observation is only valid for dependency failure")
        elif not extractions:
            raise ValueError("observable fixture execution must include extractions")
