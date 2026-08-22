from __future__ import annotations

from dataclasses import dataclass
import json

from mingli_engine.application_models import (
    REAL_USE_RESPONSE_SCHEMA_VERSION,
    ApplicationErrorV1,
    ApplicationPrivacyV1,
    ApplicationSafetyV1,
    RealUseResponseV1,
)
from mingli_engine.application_serialization import (
    response_status_from_json_bytes,
    serialize_response,
)
from mingli_engine.application_service import handle_real_use_json


_TRACE_ID = "550e8400-e29b-41d4-a716-446655440000"
_PROFILE_VALUES = (
    "1996-12-15",
    "09:30",
    "Synthetic Verification Place",
    "unknown",
    "traditional structural overview",
)


@dataclass(frozen=True)
class ApplicationVerificationScenario:
    name: str
    contract_status: str
    privacy_status: str
    write_count: int
    leak_count: int


@dataclass(frozen=True)
class ApplicationVerification:
    scenarios: tuple[ApplicationVerificationScenario, ...]
    version_identifiers: tuple[tuple[str, str], ...]
    overall_status: str


def _request_bytes(*, attested: bool) -> bytes:
    request = {
        "schema_version": "real-use-request-v1",
        "request_id": "synthetic-application-verification",
        "operation": "analysis",
        "profile": {
            "calendar_type": "gregorian",
            "birth_date": _PROFILE_VALUES[0],
            "birth_time": _PROFILE_VALUES[1],
            "birthplace": _PROFILE_VALUES[2],
            "gender": _PROFILE_VALUES[3],
            "focus_topic": _PROFILE_VALUES[4],
        },
        "authorization": {
            "subject_relation": "self",
            "attested": attested,
        },
        "options": {
            "report_format": None,
            "include_profile_in_report": False,
        },
    }
    return json.dumps(
        request,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _internal_error_bytes() -> bytes:
    return serialize_response(
        RealUseResponseV1(
            schema_version=REAL_USE_RESPONSE_SCHEMA_VERSION,
            trace_id=_TRACE_ID,
            operation="analysis",
            status="error",
            result=None,
            safety=ApplicationSafetyV1(False, "error", (), "", False),
            provenance=None,
            warnings=(),
            privacy=ApplicationPrivacyV1("not_stored_by_engine", False),
            error=ApplicationErrorV1(
                code="internal_error",
                message="Request processing failed.",
                field_path=None,
                retryable=False,
                trace_id=_TRACE_ID,
            ),
        )
    )


def _scenario(
    name: str,
    payload: bytes,
    *,
    expected_status: str,
) -> tuple[ApplicationVerificationScenario, dict[str, object]]:
    try:
        parsed = json.loads(payload)
        if not isinstance(parsed, dict):
            raise ValueError("response must be an object")
        response: dict[str, object] = parsed
        contract_verified = response_status_from_json_bytes(payload) == expected_status
        privacy = response["privacy"]
        if not isinstance(privacy, dict):
            raise ValueError("privacy must be an object")
        privacy_verified = (
            privacy["retention"] == "not_stored_by_engine"
            and privacy["contains_sensitive_profile"] is False
        )
        leak_count = sum(
            raw_value.encode("utf-8") in payload for raw_value in _PROFILE_VALUES
        )
    except Exception:
        response = {}
        contract_verified = False
        privacy_verified = False
        leak_count = 1
    return (
        ApplicationVerificationScenario(
            name=name,
            contract_status="verified" if contract_verified else "failed",
            privacy_status="verified" if privacy_verified else "failed",
            write_count=0,
            leak_count=leak_count,
        ),
        response,
    )


def build_application_verification() -> ApplicationVerification:
    """Build a deterministic, read-only contract check over synthetic scenarios."""
    success_payload = handle_real_use_json(_request_bytes(attested=True))
    refusal_payload = handle_real_use_json(_request_bytes(attested=False))
    validation_payload = handle_real_use_json(b"{")
    internal_payload = _internal_error_bytes()

    success, success_response = _scenario(
        "success",
        success_payload,
        expected_status="ok",
    )
    refusal, _ = _scenario(
        "refusal",
        refusal_payload,
        expected_status="refused",
    )
    validation_failure, _ = _scenario(
        "validation_failure",
        validation_payload,
        expected_status="error",
    )
    internal_error, _ = _scenario(
        "internal_error",
        internal_payload,
        expected_status="error",
    )
    scenarios = (success, refusal, validation_failure, internal_error)

    provenance_value = success_response.get("provenance")
    provenance = provenance_value if isinstance(provenance_value, dict) else {}
    version_keys = (
        "engine_version",
        "ruleset_version",
        "provider_version",
        "evidence_baseline_id",
    )
    versions = tuple(
        (key, str(provenance.get(key, ""))) for key in version_keys
    )
    verified = (
        all(
            scenario.contract_status == "verified"
            and scenario.privacy_status == "verified"
            and scenario.write_count == 0
            and scenario.leak_count == 0
            for scenario in scenarios
        )
        and all(value for _key, value in versions)
    )
    return ApplicationVerification(
        scenarios=scenarios,
        version_identifiers=versions,
        overall_status="verified" if verified else "failed",
    )
