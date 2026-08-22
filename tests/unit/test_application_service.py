import builtins
import importlib
import logging
from pathlib import Path
from types import ModuleType
from typing import NoReturn
from uuid import UUID

import pytest

from mingli_engine.application_models import (
    REAL_USE_REQUEST_SCHEMA_VERSION,
    ApplicationPrivacyV1,
    ApplicationSafetyV1,
    AuthorizationAttestationV1,
    RealUseOptionsV1,
    RealUseProfileV1,
    RealUseRequestV1,
)
from mingli_engine.high_risk import HighRiskReviewResult
from mingli_engine.models import SafetyReviewResult


TRACE_ID = "550e8400-e29b-41d4-a716-446655440000"
PROFILE_SENTINEL = "PRIVATE-PROFILE-SENTINEL"


def _service() -> ModuleType:
    return importlib.import_module("mingli_engine.application_service")


def _request(
    *,
    operation: str = "analysis",
    attested: bool = True,
    focus_topic: str = "traditional structural overview",
) -> RealUseRequestV1:
    return RealUseRequestV1(
        schema_version=REAL_USE_REQUEST_SCHEMA_VERSION,
        request_id="synthetic-service-test",
        operation=operation,  # type: ignore[arg-type]
        profile=RealUseProfileV1(
            calendar_type="gregorian",
            birth_date="1996-12-15",
            birth_time="09:30",
            birthplace="Synthetic UTC+08 Place",
            gender="unknown",
            focus_topic=focus_topic,
        ),
        authorization=AuthorizationAttestationV1(
            subject_relation="self",
            attested=attested,
        ),
        options=RealUseOptionsV1(
            report_format=None if operation == "analysis" else "json",
            include_profile_in_report=False,
        ),
    )


def _fix_trace_id(monkeypatch: pytest.MonkeyPatch, service: ModuleType) -> None:
    monkeypatch.setattr(service, "uuid4", lambda: UUID(TRACE_ID))


@pytest.mark.parametrize("operation", ["analysis", "report"])
def test_attestation_false_returns_complete_authorization_refusal_before_safety(
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    service = _service()
    _fix_trace_id(monkeypatch, service)

    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("authorization refusal reached safety or execution")

    monkeypatch.setattr(service, "classify_high_risk_request", forbidden)
    monkeypatch.setattr(service, "safety_check", forbidden)
    monkeypatch.setattr(service, "_execute_authorized_request", forbidden)

    response = service.handle_real_use(
        _request(
            operation=operation,
            attested=False,
            focus_topic=f"{PROFILE_SENTINEL} 投资建议",
        )
    )

    assert response.schema_version == "real-use-response-v1"
    assert response.trace_id == TRACE_ID
    assert response.operation == operation
    assert response.status == "refused"
    assert response.result is None
    assert response.safety == ApplicationSafetyV1(
        allowed=False,
        decision="authorization_required",
        categories=("authorization",),
        redirect_message=(
            "Provide a true self-use or authorized-other attestation."
        ),
        requires_narrowing=False,
    )
    assert response.provenance is None
    assert response.warnings == ()
    assert response.privacy == ApplicationPrivacyV1(
        retention="not_stored_by_engine",
        contains_sensitive_profile=False,
    )
    assert response.error is not None
    assert response.error.code == "authorization_required"
    assert response.error.message == "Authorization is required."
    assert response.error.field_path == "$.authorization.attested"
    assert response.error.retryable is False
    assert response.error.trace_id == TRACE_ID
    assert PROFILE_SENTINEL not in repr(response)


def test_authorized_request_runs_both_safety_checks_before_execution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _service()
    _fix_trace_id(monkeypatch, service)
    events: list[str] = []

    def classify(_text: str) -> HighRiskReviewResult:
        events.append("high_risk")
        return HighRiskReviewResult(allowed=True)

    def review(_text: str, *, disclaimer_present: bool) -> SafetyReviewResult:
        assert disclaimer_present is False
        events.append("focus_safety")
        return SafetyReviewResult(allowed=True)

    original_execute = service._execute_authorized_request

    def execute(request: RealUseRequestV1, trace_id: str):
        events.append("execution")
        return original_execute(request, trace_id)

    monkeypatch.setattr(service, "classify_high_risk_request", classify)
    monkeypatch.setattr(service, "safety_check", review)
    monkeypatch.setattr(service, "_execute_authorized_request", execute)

    response = service.handle_real_use(_request())

    assert events == ["high_risk", "focus_safety", "execution"]
    assert response.status == "ok"
    assert response.error is None


def test_authorization_refusal_writes_nothing_logs_nothing_and_uses_no_stderr(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    service = _service()
    _fix_trace_id(monkeypatch, service)
    write_attempts: list[str] = []

    def forbidden_write(*_args: object, **_kwargs: object) -> None:
        write_attempts.append("write")
        raise AssertionError("engine-managed write attempted")

    monkeypatch.setattr(builtins, "open", forbidden_write)
    monkeypatch.setattr(Path, "write_text", forbidden_write)
    monkeypatch.setattr(Path, "write_bytes", forbidden_write)
    monkeypatch.setattr(Path, "touch", forbidden_write)
    monkeypatch.setattr(Path, "mkdir", forbidden_write)
    caplog.set_level(logging.DEBUG)

    response = service.handle_real_use(
        _request(attested=False, focus_topic=PROFILE_SENTINEL)
    )

    captured = capsys.readouterr()
    assert response.status == "refused"
    assert write_attempts == []
    assert caplog.records == []
    assert captured.err == ""
    assert captured.out == ""
    assert PROFILE_SENTINEL not in repr(response)


def test_safety_exception_becomes_non_leaking_controlled_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    service = _service()
    _fix_trace_id(monkeypatch, service)

    def explode(_text: str) -> HighRiskReviewResult:
        raise RuntimeError(f"classifier failed for {PROFILE_SENTINEL}")

    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("classifier exception reached downstream execution")

    monkeypatch.setattr(service, "classify_high_risk_request", explode)
    monkeypatch.setattr(service, "_execute_authorized_request", forbidden)
    caplog.set_level(logging.DEBUG)

    response = service.handle_real_use(
        _request(focus_topic=f"{PROFILE_SENTINEL} 投资建议")
    )

    captured = capsys.readouterr()
    assert response.status == "error"
    assert response.operation == "analysis"
    assert response.result is None
    assert response.safety == ApplicationSafetyV1(False, "error", (), "", False)
    assert response.provenance is None
    assert response.privacy == ApplicationPrivacyV1(
        "not_stored_by_engine",
        False,
    )
    assert response.error is not None
    assert response.error.code == "internal_error"
    assert response.error.message == "Request processing failed."
    assert response.error.field_path is None
    assert response.error.retryable is False
    assert response.error.trace_id == TRACE_ID
    assert caplog.records == []
    assert captured.err == ""
    assert captured.out == ""
    assert PROFILE_SENTINEL not in repr(response)
