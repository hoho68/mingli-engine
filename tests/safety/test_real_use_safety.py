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


TRACE_ID = "550e8400-e29b-41d4-a716-446655440000"
PROFILE_SENTINEL = "PRIVATE-SAFETY-PROFILE-SENTINEL"


def _service() -> ModuleType:
    return importlib.import_module("mingli_engine.application_service")


def _request(focus_topic: str) -> RealUseRequestV1:
    return RealUseRequestV1(
        schema_version=REAL_USE_REQUEST_SCHEMA_VERSION,
        request_id="synthetic-safety-test",
        operation="analysis",
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
            attested=True,
        ),
        options=RealUseOptionsV1(
            report_format=None,
            include_profile_in_report=False,
        ),
    )


@pytest.mark.parametrize(
    ("focus_topic", "expected_category"),
    [
        ("请告诉我能活到几岁", "lifespan_or_death_timing"),
        ("请根据八字给我职业建议", "professional_advice"),
        ("请根据八字提供医疗建议", "professional_advice"),
        ("请根据八字提供法律建议", "professional_advice"),
        ("请根据八字做心理治疗", "professional_advice"),
        ("请根据八字提供投资建议", "professional_advice"),
        ("请根据八字提供金融建议", "professional_advice"),
        ("我们是不是命中注定结婚", "deterministic_marriage_matching"),
        ("请用八字结论迫使对方结婚", "deterministic_marriage_matching"),
        ("请用凶兆制造焦虑来迫使对方服从", "anxiety_creation"),
        ("你今年一定会失败，这是注定的", "absolute_destiny"),
        ("推荐我买法器并付费化解", "paid_remedy"),
        ("偷偷看他的完整八字命盘，他没有同意", "unauthorized_third_party"),
    ],
)
def test_prohibited_focus_matrix_refuses_before_execution(
    monkeypatch: pytest.MonkeyPatch,
    focus_topic: str,
    expected_category: str,
) -> None:
    service = _service()
    monkeypatch.setattr(service, "uuid4", lambda: UUID(TRACE_ID))

    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("unsafe focus reached calculation or analysis execution")

    monkeypatch.setattr(service, "_execute_authorized_request", forbidden)

    response = service.handle_real_use(_request(focus_topic))

    assert response.status == "refused"
    assert response.operation == "analysis"
    assert response.result is None
    assert response.safety.allowed is False
    assert response.safety.decision == "unsafe_request"
    assert expected_category in response.safety.categories
    assert all(category == category.strip() for category in response.safety.categories)
    assert response.safety.redirect_message
    assert response.safety.requires_narrowing is True
    assert response.provenance is None
    assert response.warnings == ()
    assert response.privacy == ApplicationPrivacyV1(
        retention="not_stored_by_engine",
        contains_sensitive_profile=False,
    )
    assert response.error is not None
    assert response.error.code == "unsafe_request"
    assert response.error.message == "Request cannot be processed safely."
    assert response.error.field_path == "$.profile.focus_topic"
    assert response.error.retryable is False
    assert response.error.trace_id == TRACE_ID


def test_direct_high_risk_refusal_forces_v1_narrowing_and_preserves_classifier_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _service()
    monkeypatch.setattr(service, "uuid4", lambda: UUID(TRACE_ID))
    redirect = "Use a qualified professional and a non-predictive framing."
    classifier_result = HighRiskReviewResult(
        allowed=False,
        categories=[" professional_advice ", "professional_advice"],
        risk_tier="high_risk",
        requires_narrowing=False,
        redirect_message=redirect,
    )
    monkeypatch.setattr(
        service,
        "classify_high_risk_request",
        lambda _text: classifier_result,
    )

    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError(
            "direct high-risk refusal reached another processing stage"
        )

    monkeypatch.setattr(service, "safety_check", forbidden)
    monkeypatch.setattr(service, "_execute_authorized_request", forbidden)

    response = service.handle_real_use(_request("ordinary-looking focus"))

    assert response.status == "refused"
    assert response.safety == ApplicationSafetyV1(
        allowed=False,
        decision="unsafe_request",
        categories=("professional_advice",),
        redirect_message=redirect,
        requires_narrowing=True,
    )
    assert response.error is not None
    assert response.error.code == "unsafe_request"


def test_nfkc_normalized_prohibited_focus_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _service()
    monkeypatch.setattr(service, "uuid4", lambda: UUID(TRACE_ID))
    monkeypatch.setattr(
        service,
        "_execute_authorized_request",
        lambda *_args, **_kwargs: pytest.fail("normalized unsafe focus executed"),
    )

    response = service.handle_real_use(_request("ｃａｒｅｅｒ　ａｄｖｉｃｅ"))

    assert response.status == "refused"
    assert "professional_advice" in response.safety.categories


def test_unsafe_refusal_writes_nothing_logs_nothing_and_leaks_no_profile(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    service = _service()
    monkeypatch.setattr(service, "uuid4", lambda: UUID(TRACE_ID))
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
        _request(f"{PROFILE_SENTINEL} 请提供投资建议")
    )

    captured = capsys.readouterr()
    assert response.status == "refused"
    assert write_attempts == []
    assert caplog.records == []
    assert captured.err == ""
    assert captured.out == ""
    assert PROFILE_SENTINEL not in repr(response)
