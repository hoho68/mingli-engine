from dataclasses import FrozenInstanceError, MISSING, fields, is_dataclass
from typing import Any, get_args

import pytest

from mingli_engine.application_models import (
    APPLICATION_ERROR_CODES,
    CONTENT_MEDIA_TYPES,
    REAL_USE_REQUEST_SCHEMA_VERSION,
    REAL_USE_RESPONSE_SCHEMA_VERSION,
    ApplicationAnalysisResultV1,
    ApplicationContentV1,
    ApplicationErrorCode,
    ApplicationErrorV1,
    ApplicationPrivacyV1,
    ApplicationProvenanceV1,
    ApplicationReportResultV1,
    ApplicationSafetyV1,
    ApplicationWarningV1,
    AuthorizationAttestationV1,
    CalendarType,
    ChartSourceConfidence,
    ChartSourceType,
    ContentMediaType,
    RealUseOperation,
    RealUseOptionsV1,
    RealUseProfileV1,
    RealUseRequestV1,
    RealUseResponseV1,
    ReportFormat,
    ResponseStatus,
    RetentionPolicy,
    SafetyDecision,
    SubjectRelation,
)


TRACE_ID = "550e8400-e29b-41d4-a716-446655440000"


def _wrong_type(value: object) -> Any:
    return value


def _profile() -> RealUseProfileV1:
    return RealUseProfileV1(
        calendar_type="gregorian",
        birth_date="1996-12-15",
        birth_time="09:30",
        birthplace="Synthetic UTC+08 Place",
        gender="unknown",
        focus_topic="traditional structural overview",
    )


def _request(
    *,
    operation: RealUseOperation = "analysis",
    report_format: ReportFormat | None = None,
    request_id: str | None = "synthetic-analysis-001",
    attested: bool = True,
) -> RealUseRequestV1:
    return RealUseRequestV1(
        schema_version=REAL_USE_REQUEST_SCHEMA_VERSION,
        request_id=request_id,
        operation=operation,
        profile=_profile(),
        authorization=AuthorizationAttestationV1(
            subject_relation="self",
            attested=attested,
        ),
        options=RealUseOptionsV1(
            report_format=report_format,
            include_profile_in_report=False,
        ),
    )


def _privacy(*, sensitive: bool = False) -> ApplicationPrivacyV1:
    return ApplicationPrivacyV1(
        retention="not_stored_by_engine",
        contains_sensitive_profile=sensitive,
    )


def _provenance() -> ApplicationProvenanceV1:
    return ApplicationProvenanceV1(
        engine_version="0.2.0",
        ruleset_version="bazi-rules-v1",
        provider_version="lunar-python-1.4.8",
        chart_source_type="calculated",
        chart_source_confidence="deterministic_supported_range",
        evidence_baseline_id="tracked-evidence-baseline",
        evidence_ids=["evidence.synthetic"],  # type: ignore[arg-type]
    )


def _error(code: ApplicationErrorCode) -> ApplicationErrorV1:
    return ApplicationErrorV1(
        code=code,
        message="Controlled application outcome.",
        field_path=None,
        retryable=False,
        trace_id=TRACE_ID,
    )


def _safety(
    decision: SafetyDecision,
    *,
    allowed: bool = False,
    categories: tuple[str, ...] | list[str] = (),
    redirect_message: str = "",
    requires_narrowing: bool = False,
) -> ApplicationSafetyV1:
    return ApplicationSafetyV1(
        allowed=allowed,
        decision=decision,
        categories=categories,  # type: ignore[arg-type]
        redirect_message=redirect_message,
        requires_narrowing=requires_narrowing,
    )


def _response(**changes: Any) -> RealUseResponseV1:
    values: dict[str, Any] = {
        "schema_version": REAL_USE_RESPONSE_SCHEMA_VERSION,
        "trace_id": TRACE_ID,
        "operation": "analysis",
        "status": "ok",
        "result": ApplicationAnalysisResultV1(chart={}, calculation={}),
        "safety": _safety("allowed", allowed=True),
        "provenance": _provenance(),
        "warnings": [],
        "privacy": _privacy(),
        "error": None,
    }
    values.update(changes)
    return RealUseResponseV1(**values)


def test_application_dto_fields_are_exact_and_required() -> None:
    expected_fields = {
        RealUseProfileV1: (
            "calendar_type",
            "birth_date",
            "birth_time",
            "birthplace",
            "gender",
            "focus_topic",
        ),
        AuthorizationAttestationV1: ("subject_relation", "attested"),
        RealUseOptionsV1: ("report_format", "include_profile_in_report"),
        RealUseRequestV1: (
            "schema_version",
            "request_id",
            "operation",
            "profile",
            "authorization",
            "options",
        ),
        ApplicationErrorV1: (
            "code",
            "message",
            "field_path",
            "retryable",
            "trace_id",
        ),
        ApplicationSafetyV1: (
            "allowed",
            "decision",
            "categories",
            "redirect_message",
            "requires_narrowing",
        ),
        ApplicationProvenanceV1: (
            "engine_version",
            "ruleset_version",
            "provider_version",
            "chart_source_type",
            "chart_source_confidence",
            "evidence_baseline_id",
            "evidence_ids",
        ),
        ApplicationWarningV1: ("code", "message"),
        ApplicationPrivacyV1: ("retention", "contains_sensitive_profile"),
        ApplicationContentV1: (
            "media_type",
            "content",
            "contains_sensitive_profile",
        ),
        ApplicationAnalysisResultV1: ("chart", "calculation"),
        ApplicationReportResultV1: ("report", "content"),
        RealUseResponseV1: (
            "schema_version",
            "trace_id",
            "operation",
            "status",
            "result",
            "safety",
            "provenance",
            "warnings",
            "privacy",
            "error",
        ),
    }

    for model, expected in expected_fields.items():
        model_fields = fields(model)
        assert tuple(field.name for field in model_fields) == expected
        assert all(
            field.default is MISSING and field.default_factory is MISSING
            for field in model_fields
        )


def test_protocol_literals_and_schema_constants_are_exact() -> None:
    assert REAL_USE_REQUEST_SCHEMA_VERSION == "real-use-request-v1"
    assert REAL_USE_RESPONSE_SCHEMA_VERSION == "real-use-response-v1"
    assert get_args(CalendarType) == ("gregorian",)
    assert get_args(RealUseOperation) == ("analysis", "report")
    assert get_args(SubjectRelation) == ("self", "authorized_other")
    assert get_args(ReportFormat) == ("json", "markdown", "html")
    assert get_args(ResponseStatus) == ("ok", "refused", "error")
    assert get_args(SafetyDecision) == (
        "allowed",
        "not_evaluated",
        "authorization_required",
        "unsafe_request",
        "error",
    )
    assert get_args(ApplicationErrorCode) == (
        "invalid_json",
        "invalid_request",
        "authorization_required",
        "unsafe_request",
        "unsupported_input",
        "payload_too_large",
        "response_too_large",
        "calculation_failed",
        "knowledge_unavailable",
        "internal_error",
    )
    assert get_args(ContentMediaType) == ("text/markdown", "text/html")
    assert get_args(ChartSourceType) == ("calculated",)
    assert get_args(ChartSourceConfidence) == ("deterministic_supported_range",)
    assert get_args(RetentionPolicy) == ("not_stored_by_engine",)
    assert APPLICATION_ERROR_CODES == frozenset(get_args(ApplicationErrorCode))
    assert CONTENT_MEDIA_TYPES == frozenset(get_args(ContentMediaType))


def test_all_dtos_are_frozen_dataclasses() -> None:
    values = (
        _profile(),
        AuthorizationAttestationV1("self", False),
        RealUseOptionsV1(None, False),
        _request(attested=False, request_id=None),
        _error("invalid_json"),
        _safety("not_evaluated"),
        _provenance(),
        ApplicationWarningV1("limited_scope", "Scope is limited."),
        _privacy(),
        ApplicationContentV1("text/markdown", "# Report", False),
        ApplicationAnalysisResultV1({}, {}),
        ApplicationReportResultV1({}, None),
        _response(),
    )

    for value in values:
        assert is_dataclass(value)
        first_field = fields(value)[0].name
        with pytest.raises(FrozenInstanceError):
            setattr(value, first_field, None)


def test_sequence_inputs_normalize_to_tuples_without_aliasing() -> None:
    categories = ["professional_advice"]
    evidence_ids = ["evidence.synthetic"]
    warnings = [ApplicationWarningV1("limited_scope", "Scope is limited.")]

    safety = _safety(
        "unsafe_request",
        categories=categories,
        redirect_message="Use a qualified professional.",
        requires_narrowing=True,
    )
    provenance = ApplicationProvenanceV1(
        "0.2.0",
        "bazi-rules-v1",
        "lunar-python-1.4.8",
        "calculated",
        "deterministic_supported_range",
        "tracked-evidence-baseline",
        evidence_ids,  # type: ignore[arg-type]
    )
    response = _response(warnings=warnings)
    categories.append("later")
    evidence_ids.append("later")
    warnings.append(ApplicationWarningV1("later", "Later."))

    assert safety.categories == ("professional_advice",)
    assert provenance.evidence_ids == ("evidence.synthetic",)
    assert response.warnings == (
        ApplicationWarningV1("limited_scope", "Scope is limited."),
    )


def test_request_requires_all_fields_and_accepts_nullable_id_and_false_attestation() -> (
    None
):
    request = _request(request_id=None, attested=False)

    assert request.request_id is None
    assert request.authorization.attested is False
    with pytest.raises(TypeError):
        RealUseOptionsV1(report_format=None)  # type: ignore[call-arg]


@pytest.mark.parametrize("bad_value", [None, 0, 1, "false"])
def test_request_boolean_fields_require_actual_bool(bad_value: object) -> None:
    with pytest.raises(TypeError, match="attested must be bool"):
        AuthorizationAttestationV1("self", bad_value)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="include_profile_in_report must be bool"):
        RealUseOptionsV1(None, bad_value)  # type: ignore[arg-type]


def test_request_rejects_invalid_literals_but_does_not_parse_text_or_dates() -> None:
    profile = RealUseProfileV1(
        "gregorian",
        "not-parsed-here",
        "also-not-parsed-here",
        "",
        "domain-parser-decides",
        "",
    )
    assert profile.birth_date == "not-parsed-here"

    with pytest.raises(ValueError, match="calendar_type"):
        RealUseProfileV1("lunar", "", "", "", "", "")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="subject_relation"):
        AuthorizationAttestationV1("friend", True)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="report_format"):
        RealUseOptionsV1("pdf", False)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="schema_version"):
        RealUseRequestV1(
            _wrong_type("v2"),
            None,
            "analysis",
            profile,
            AuthorizationAttestationV1("self", True),
            RealUseOptionsV1(None, False),
        )


@pytest.mark.parametrize(
    ("operation", "report_format"),
    [("analysis", "json"), ("report", None)],
)
def test_request_rejects_operation_report_format_mismatch(
    operation: RealUseOperation,
    report_format: ReportFormat | None,
) -> None:
    with pytest.raises(ValueError, match="operation and report_format"):
        _request(operation=operation, report_format=report_format)


def test_ok_analysis_and_report_responses_are_constructible() -> None:
    analysis = _response()
    report = _response(
        operation="report",
        result=ApplicationReportResultV1(
            None,
            ApplicationContentV1("text/html", "<p>Report</p>", False),
        ),
    )

    assert analysis.status == "ok"
    assert isinstance(analysis.result, ApplicationAnalysisResultV1)
    assert report.status == "ok"
    assert isinstance(report.result, ApplicationReportResultV1)


@pytest.mark.parametrize(
    ("operation", "result"),
    [
        ("analysis", ApplicationReportResultV1({}, None)),
        ("report", ApplicationAnalysisResultV1({}, {})),
        (None, ApplicationAnalysisResultV1({}, {})),
    ],
)
def test_ok_response_rejects_operation_result_mismatch(
    operation: RealUseOperation | None,
    result: ApplicationAnalysisResultV1 | ApplicationReportResultV1,
) -> None:
    with pytest.raises(ValueError, match="ok response"):
        _response(operation=operation, result=result)


@pytest.mark.parametrize(
    ("report", "content"),
    [
        (None, None),
        ({}, ApplicationContentV1("text/markdown", "Report", False)),
    ],
)
def test_report_result_requires_exactly_one_representation(
    report: dict[str, object] | None,
    content: ApplicationContentV1 | None,
) -> None:
    with pytest.raises(ValueError, match="exactly one"):
        ApplicationReportResultV1(report, content)


@pytest.mark.parametrize(
    "code",
    ["payload_too_large", "invalid_json", "invalid_request", "unsupported_input"],
)
def test_parse_error_matrix_is_constructible(code: ApplicationErrorCode) -> None:
    response = _response(
        operation=None,
        status="error",
        result=None,
        safety=_safety("not_evaluated"),
        provenance=None,
        privacy=_privacy(),
        error=_error(code),
    )

    assert response.operation is None
    assert response.result is None
    assert response.safety == _safety("not_evaluated")
    assert response.provenance is None
    assert response.privacy == _privacy()
    assert response.error == _error(code)


def test_parse_time_unsupported_input_uses_null_operation_contract() -> None:
    response = _response(
        operation=None,
        status="error",
        result=None,
        safety=_safety("not_evaluated"),
        provenance=None,
        error=_error("unsupported_input"),
    )

    assert response.operation is None
    assert response.safety.decision == "not_evaluated"


def test_post_parse_unsupported_input_preserves_operation_contract() -> None:
    response = _response(
        operation="analysis",
        status="error",
        result=None,
        safety=_safety("error"),
        provenance=None,
        error=_error("unsupported_input"),
    )

    assert response.operation == "analysis"
    assert response.safety.decision == "error"


@pytest.mark.parametrize("operation", ["analysis", "report"])
def test_authorization_refusal_matrix_is_constructible(
    operation: RealUseOperation,
) -> None:
    safety = _safety(
        "authorization_required",
        categories=["authorization"],
        redirect_message=("Provide a true self-use or authorized-other attestation."),
    )
    response = _response(
        operation=operation,
        status="refused",
        result=None,
        safety=safety,
        provenance=None,
        privacy=_privacy(),
        error=_error("authorization_required"),
    )

    assert response.operation == operation
    assert response.result is None
    assert response.safety == safety
    assert response.provenance is None
    assert response.privacy == _privacy()
    assert response.error == _error("authorization_required")


@pytest.mark.parametrize("operation", ["analysis", "report"])
def test_unsafe_refusal_matrix_is_constructible(
    operation: RealUseOperation,
) -> None:
    safety = _safety(
        "unsafe_request",
        categories=["professional_advice"],
        redirect_message="Use a qualified professional for this decision.",
        requires_narrowing=True,
    )
    response = _response(
        operation=operation,
        status="refused",
        result=None,
        safety=safety,
        provenance=None,
        privacy=_privacy(),
        error=_error("unsafe_request"),
    )

    assert response.operation == operation
    assert response.result is None
    assert response.safety == safety
    assert response.provenance is None
    assert response.privacy == _privacy()
    assert response.error == _error("unsafe_request")


@pytest.mark.parametrize("operation", ["analysis", "report"])
def test_internal_error_matrix_is_constructible(
    operation: RealUseOperation,
) -> None:
    response = _response(
        operation=operation,
        status="error",
        result=None,
        safety=_safety("error"),
        provenance=None,
        privacy=_privacy(),
        error=_error("internal_error"),
    )

    assert response.operation == operation
    assert response.result is None
    assert response.safety == _safety("error")
    assert response.provenance is None
    assert response.privacy == _privacy()
    assert response.error == _error("internal_error")


@pytest.mark.parametrize(
    "changes",
    [
        {"status": "ok", "result": None},
        {"status": "ok", "provenance": None},
        {"status": "ok", "error": _error("internal_error")},
        {"status": "ok", "safety": _safety("not_evaluated")},
        {
            "status": "refused",
            "result": ApplicationAnalysisResultV1({}, {}),
            "safety": _safety(
                "authorization_required",
                categories=["authorization"],
                redirect_message=(
                    "Provide a true self-use or authorized-other attestation."
                ),
            ),
            "provenance": None,
            "error": _error("authorization_required"),
        },
        {
            "status": "refused",
            "result": None,
            "safety": _safety("unsafe_request"),
            "provenance": None,
            "error": _error("unsafe_request"),
        },
        {
            "status": "error",
            "operation": None,
            "result": None,
            "safety": _safety("error"),
            "provenance": None,
            "error": _error("internal_error"),
        },
        {
            "status": "error",
            "operation": "analysis",
            "result": None,
            "safety": _safety("not_evaluated"),
            "provenance": None,
            "error": _error("invalid_json"),
        },
        {
            "status": "error",
            "operation": "analysis",
            "result": None,
            "safety": _safety("error"),
            "provenance": _provenance(),
            "error": _error("internal_error"),
        },
        {
            "status": "error",
            "operation": "analysis",
            "result": None,
            "safety": _safety("error"),
            "provenance": None,
            "privacy": _privacy(sensitive=True),
            "error": _error("internal_error"),
        },
        {
            "status": "error",
            "operation": "analysis",
            "result": None,
            "safety": _safety("error"),
            "provenance": None,
            "error": ApplicationErrorV1(
                "internal_error", "Controlled.", None, False, "other-trace"
            ),
        },
    ],
)
def test_response_rejects_illegal_status_matrix_combinations(
    changes: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        _response(**changes)


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (
            lambda: ApplicationContentV1(
                "application/pdf",  # type: ignore[arg-type]
                "",
                False,
            ),
            "media_type",
        ),
        (
            lambda: ApplicationProvenanceV1(
                "0.2.0",
                "rules",
                "provider",
                "external",  # type: ignore[arg-type]
                "deterministic_supported_range",
                "baseline",
                (),
            ),
            "chart_source_type",
        ),
        (
            lambda: ApplicationPrivacyV1(
                "stored",  # type: ignore[arg-type]
                False,
            ),
            "retention",
        ),
        (
            lambda: ApplicationErrorV1(
                "exception",  # type: ignore[arg-type]
                "message",
                None,
                False,
                TRACE_ID,
            ),
            "code",
        ),
    ],
)
def test_response_nested_dtos_reject_values_outside_literals(
    factory: Any,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        factory()


@pytest.mark.parametrize(
    ("field_name", "factory"),
    [
        (
            "birth_date",
            lambda: RealUseProfileV1(
                "gregorian", _wrong_type(1), "09:30", "place", "unknown", "focus"
            ),
        ),
        (
            "birth_time",
            lambda: RealUseProfileV1(
                "gregorian", "1996-12-15", _wrong_type(1), "place", "unknown", "focus"
            ),
        ),
        (
            "birthplace",
            lambda: RealUseProfileV1(
                "gregorian", "1996-12-15", "09:30", _wrong_type(1), "unknown", "focus"
            ),
        ),
        (
            "gender",
            lambda: RealUseProfileV1(
                "gregorian", "1996-12-15", "09:30", "place", _wrong_type(1), "focus"
            ),
        ),
        (
            "focus_topic",
            lambda: RealUseProfileV1(
                "gregorian", "1996-12-15", "09:30", "place", "unknown", _wrong_type(1)
            ),
        ),
        (
            "message",
            lambda: ApplicationErrorV1(
                "invalid_json", _wrong_type(1), None, False, TRACE_ID
            ),
        ),
        (
            "field_path",
            lambda: ApplicationErrorV1(
                "invalid_json", "error", _wrong_type(False), False, TRACE_ID
            ),
        ),
        (
            "retryable",
            lambda: ApplicationErrorV1(
                "invalid_json", "error", None, _wrong_type(1), TRACE_ID
            ),
        ),
        (
            "trace_id",
            lambda: ApplicationErrorV1(
                "invalid_json", "error", None, False, _wrong_type(1)
            ),
        ),
        (
            "categories",
            lambda: ApplicationSafetyV1(
                False, "unsafe_request", _wrong_type("unsafe"), "redirect", True
            ),
        ),
        (
            "categories",
            lambda: ApplicationSafetyV1(
                False, "unsafe_request", _wrong_type([1]), "redirect", True
            ),
        ),
        (
            "redirect_message",
            lambda: ApplicationSafetyV1(False, "error", (), _wrong_type(1), False),
        ),
        (
            "requires_narrowing",
            lambda: ApplicationSafetyV1(False, "error", (), "", _wrong_type(1)),
        ),
        (
            "engine_version",
            lambda: ApplicationProvenanceV1(
                _wrong_type(1),
                "rules",
                "provider",
                "calculated",
                "deterministic_supported_range",
                "baseline",
                (),
            ),
        ),
        (
            "evidence_ids",
            lambda: ApplicationProvenanceV1(
                "engine",
                "rules",
                "provider",
                "calculated",
                "deterministic_supported_range",
                "baseline",
                _wrong_type("evidence"),
            ),
        ),
        (
            "evidence_ids",
            lambda: ApplicationProvenanceV1(
                "engine",
                "rules",
                "provider",
                "calculated",
                "deterministic_supported_range",
                "baseline",
                _wrong_type([1]),
            ),
        ),
        ("code", lambda: ApplicationWarningV1(_wrong_type(1), "warning")),
        ("message", lambda: ApplicationWarningV1("warning", _wrong_type(1))),
        (
            "contains_sensitive_profile",
            lambda: ApplicationPrivacyV1("not_stored_by_engine", _wrong_type(1)),
        ),
        (
            "content",
            lambda: ApplicationContentV1("text/markdown", _wrong_type(1), False),
        ),
        (
            "contains_sensitive_profile",
            lambda: ApplicationContentV1("text/markdown", "content", _wrong_type(1)),
        ),
        ("chart", lambda: ApplicationAnalysisResultV1(_wrong_type([]), {})),
        ("calculation", lambda: ApplicationAnalysisResultV1({}, _wrong_type([]))),
        ("report", lambda: ApplicationReportResultV1(_wrong_type([]), None)),
        ("content", lambda: ApplicationReportResultV1(None, _wrong_type(object()))),
    ],
)
def test_nested_dto_fields_reject_wrong_runtime_types(
    field_name: str,
    factory: Any,
) -> None:
    with pytest.raises(TypeError, match=field_name):
        factory()


@pytest.mark.parametrize(
    ("field_name", "changes"),
    [
        ("result", {"result": object()}),
        ("safety", {"safety": object()}),
        ("provenance", {"provenance": object()}),
        ("warnings", {"warnings": [object()]}),
        ("privacy", {"privacy": object()}),
        ("error", {"error": object()}),
    ],
)
def test_response_rejects_wrong_nested_runtime_types(
    field_name: str,
    changes: dict[str, object],
) -> None:
    with pytest.raises(TypeError, match=field_name):
        _response(**changes)


@pytest.mark.parametrize(
    ("field_name", "changes"),
    [
        ("profile", {"profile": object()}),
        ("authorization", {"authorization": object()}),
        ("options", {"options": object()}),
    ],
)
def test_request_rejects_wrong_nested_runtime_types(
    field_name: str,
    changes: dict[str, object],
) -> None:
    values: dict[str, object] = {
        "schema_version": REAL_USE_REQUEST_SCHEMA_VERSION,
        "request_id": None,
        "operation": "analysis",
        "profile": _profile(),
        "authorization": AuthorizationAttestationV1("self", True),
        "options": RealUseOptionsV1(None, False),
    }
    values.update(changes)
    with pytest.raises(TypeError, match=field_name):
        RealUseRequestV1(**values)  # type: ignore[arg-type]
