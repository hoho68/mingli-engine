from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from typing import Literal


DOMAIN_CALIBRATION_SUITE_V2: Literal["domain-calibration-suite-v2"] = (
    "domain-calibration-suite-v2"
)
CALIBRATION_OBSERVATION_SCHEMA_V2: Literal[
    "domain-calibration-observation-v2"
] = "domain-calibration-observation-v2"
CALIBRATION_EXTRACTION_SCHEMA_V2: Literal[
    "domain-calibration-extraction-v2"
] = "domain-calibration-extraction-v2"

CalibrationAvailabilityV2 = Literal["available", "not_available"]
CalibrationActualStatusV2 = Literal[
    "not_computed", "computed", "indeterminate", "disputed"
]

_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_AVAILABILITIES = frozenset({"available", "not_available"})
_ACTUAL_STATUSES = frozenset(
    {"not_computed", "computed", "indeterminate", "disputed"}
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
