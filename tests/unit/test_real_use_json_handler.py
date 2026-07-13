import json
from pathlib import Path
from types import ModuleType
from typing import Any, NoReturn
from uuid import UUID

import pytest

import mingli_engine
from mingli_engine.application_models import (
    REAL_USE_RESPONSE_SCHEMA_VERSION,
    ApplicationContentV1,
    ApplicationPrivacyV1,
    ApplicationProvenanceV1,
    ApplicationReportResultV1,
    ApplicationSafetyV1,
    RealUseRequestV1,
    RealUseResponseV1,
)
from mingli_engine.chart_calculator import ChartCalculationError
from mingli_engine.classical_sources import ClassicalEvidenceError
from mingli_engine.high_risk import HighRiskReviewResult


FIXTURES = Path(__file__).parents[1] / "fixtures" / "application"
TRACE_ID = "550e8400-e29b-41d4-a716-446655440000"
SECRET = "PRIVATE-JSON-HANDLER-SENTINEL"


def _service() -> ModuleType:
    import mingli_engine.application_service as service

    return service


def _analysis_mapping() -> dict[str, Any]:
    return json.loads(
        (FIXTURES / "valid_analysis_request.json").read_text(encoding="utf-8")
    )


def _report_mapping() -> dict[str, Any]:
    return json.loads(
        (FIXTURES / "valid_report_request.json").read_text(encoding="utf-8")
    )


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _handle(payload: bytes) -> bytes:
    handler = getattr(_service(), "handle_real_use_json")
    return handler(payload)


def _decoded(payload: bytes) -> dict[str, Any]:
    decoded = json.loads(payload)
    assert isinstance(decoded, dict)
    return decoded


def _assert_controlled_error(
    response: dict[str, Any],
    *,
    code: str,
    operation: str | None,
) -> None:
    assert response["schema_version"] == "real-use-response-v1"
    assert response["operation"] == operation
    assert response["status"] == "error"
    assert response["result"] is None
    assert response["provenance"] is None
    assert response["warnings"] == []
    assert response["privacy"] == {
        "contains_sensitive_profile": False,
        "retention": "not_stored_by_engine",
    }
    assert response["safety"] == {
        "allowed": False,
        "categories": [],
        "decision": "not_evaluated" if operation is None else "error",
        "redirect_message": "",
        "requires_narrowing": False,
    }
    assert response["error"]["code"] == code
    assert response["error"]["retryable"] is False
    assert response["error"]["trace_id"] == response["trace_id"]
    UUID(response["trace_id"], version=4)


@pytest.mark.parametrize(
    ("fixture_name", "expected_operation"),
    [
        ("valid_analysis_request.json", "analysis"),
        ("valid_report_request.json", "report"),
    ],
)
def test_handle_real_use_json_returns_canonical_utf8_success_envelope(
    fixture_name: str,
    expected_operation: str,
) -> None:
    response_bytes = _handle((FIXTURES / fixture_name).read_bytes())
    response = _decoded(response_bytes)

    assert response_bytes == _canonical_bytes(response)
    assert response["operation"] == expected_operation
    assert response["status"] == "ok"
    assert response["error"] is None
    assert response["provenance"] is not None
    assert response["privacy"]["retention"] == "not_stored_by_engine"


@pytest.mark.parametrize(
    ("payload_factory", "expected_code"),
    [
        (lambda: b"{", "invalid_json"),
        (
            lambda: _canonical_bytes(
                {key: value for key, value in _analysis_mapping().items() if key != "request_id"}
            ),
            "invalid_request",
        ),
        (
            lambda: _canonical_bytes({**_analysis_mapping(), "chart": {}}),
            "unsupported_input",
        ),
        (lambda: b" " * (32 * 1024 + 1), "payload_too_large"),
    ],
)
def test_parse_failures_use_complete_non_ok_matrix(
    payload_factory: Any,
    expected_code: str,
) -> None:
    response = _decoded(_handle(payload_factory()))

    _assert_controlled_error(response, code=expected_code, operation=None)
    assert response["error"]["message"]


def test_authorization_refusal_serializes_complete_matrix() -> None:
    request = _analysis_mapping()
    request["authorization"]["attested"] = False

    response = _decoded(_handle(_canonical_bytes(request)))

    assert response["operation"] == "analysis"
    assert response["status"] == "refused"
    assert response["result"] is None
    assert response["provenance"] is None
    assert response["safety"] == {
        "allowed": False,
        "categories": ["authorization"],
        "decision": "authorization_required",
        "redirect_message": (
            "Provide a true self-use or authorized-other attestation."
        ),
        "requires_narrowing": False,
    }
    assert response["privacy"] == {
        "contains_sensitive_profile": False,
        "retention": "not_stored_by_engine",
    }
    assert response["error"]["code"] == "authorization_required"
    assert response["error"]["trace_id"] == response["trace_id"]


def test_safety_refusal_serializes_complete_matrix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _service()
    monkeypatch.setattr(
        service,
        "classify_high_risk_request",
        lambda _text: HighRiskReviewResult(
            allowed=False,
            categories=["professional_advice"],
            redirect_message="Use a qualified professional.",
        ),
    )

    response = _decoded(_handle(_canonical_bytes(_analysis_mapping())))

    assert response["operation"] == "analysis"
    assert response["status"] == "refused"
    assert response["result"] is None
    assert response["provenance"] is None
    assert response["safety"] == {
        "allowed": False,
        "categories": ["professional_advice"],
        "decision": "unsafe_request",
        "redirect_message": "Use a qualified professional.",
        "requires_narrowing": True,
    }
    assert response["error"]["code"] == "unsafe_request"


@pytest.mark.parametrize(
    ("dependency", "exception", "expected_code"),
    [
        (
            "calculate_bazi_chart",
            ChartCalculationError(f"calculation failed for {SECRET}"),
            "calculation_failed",
        ),
        (
            "load_approved_evidence_units",
            ClassicalEvidenceError(f"missing C:/private/{SECRET}.json"),
            "knowledge_unavailable",
        ),
        (
            "analyze_bazi_chart",
            RuntimeError(f"unexpected internal failure: {SECRET}"),
            "internal_error",
        ),
    ],
)
def test_typed_execution_failures_map_to_stable_non_leaking_errors(
    monkeypatch: pytest.MonkeyPatch,
    dependency: str,
    exception: Exception,
    expected_code: str,
) -> None:
    service = _service()

    def explode(*_args: object, **_kwargs: object) -> NoReturn:
        raise exception

    monkeypatch.setattr(service, dependency, explode)

    response_bytes = _handle(_canonical_bytes(_analysis_mapping()))
    response = _decoded(response_bytes)

    _assert_controlled_error(
        response,
        code=expected_code,
        operation="analysis",
    )
    assert SECRET.encode() not in response_bytes
    assert b"C:/private" not in response_bytes
    assert str(exception).encode() not in response_bytes


def test_oversized_normal_response_becomes_small_controlled_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _service()

    def oversized(
        request: RealUseRequestV1,
        trace_id: str,
    ) -> RealUseResponseV1:
        return RealUseResponseV1(
            schema_version=REAL_USE_RESPONSE_SCHEMA_VERSION,
            trace_id=trace_id,
            operation=request.operation,
            status="ok",
            result=ApplicationReportResultV1(
                report=None,
                content=ApplicationContentV1(
                    media_type="text/markdown",
                    content="x" * (1024 * 1024),
                    contains_sensitive_profile=False,
                ),
            ),
            safety=ApplicationSafetyV1(True, "allowed", (), "", False),
            provenance=ApplicationProvenanceV1(
                engine_version="bazi-core-v1",
                ruleset_version="bazi-rules-v1",
                provider_version="provider-v1",
                chart_source_type="calculated",
                chart_source_confidence="deterministic_supported_range",
                evidence_baseline_id="evidence-v1",
                evidence_ids=(),
            ),
            warnings=(),
            privacy=ApplicationPrivacyV1("not_stored_by_engine", False),
            error=None,
        )

    request = _report_mapping()
    request["options"] = {
        "report_format": "markdown",
        "include_profile_in_report": False,
    }
    monkeypatch.setattr(service, "_execute_authorized_request", oversized)

    response_bytes = _handle(_canonical_bytes(request))
    response = _decoded(response_bytes)

    assert len(response_bytes) < 2048
    _assert_controlled_error(
        response,
        code="response_too_large",
        operation="report",
    )


def test_public_root_exports_json_handler_and_status_reader() -> None:
    handler = getattr(mingli_engine, "handle_real_use_json")
    status_reader = getattr(mingli_engine, "response_status_from_json_bytes")

    response = handler((FIXTURES / "valid_analysis_request.json").read_bytes())

    assert status_reader(response) == "ok"
