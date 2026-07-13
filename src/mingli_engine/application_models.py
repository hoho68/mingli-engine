from dataclasses import dataclass
from typing import Literal


REAL_USE_REQUEST_SCHEMA_VERSION: Literal["real-use-request-v1"] = (
    "real-use-request-v1"
)
REAL_USE_RESPONSE_SCHEMA_VERSION: Literal["real-use-response-v1"] = (
    "real-use-response-v1"
)

CalendarType = Literal["gregorian"]
RealUseOperation = Literal["analysis", "report"]
SubjectRelation = Literal["self", "authorized_other"]
ReportFormat = Literal["json", "markdown", "html"]
ResponseStatus = Literal["ok", "refused", "error"]
SafetyDecision = Literal[
    "allowed",
    "not_evaluated",
    "authorization_required",
    "unsafe_request",
    "error",
]
ApplicationErrorCode = Literal[
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
]
ContentMediaType = Literal["text/markdown", "text/html"]
ChartSourceType = Literal["calculated"]
ChartSourceConfidence = Literal["deterministic_supported_range"]
RetentionPolicy = Literal["not_stored_by_engine"]

APPLICATION_ERROR_CODES = frozenset(
    {
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
    }
)
CONTENT_MEDIA_TYPES = frozenset({"text/markdown", "text/html"})

_OPERATIONS = frozenset({"analysis", "report"})
_RELATIONS = frozenset({"self", "authorized_other"})
_REPORT_FORMATS = frozenset({"json", "markdown", "html"})
_RESPONSE_STATUSES = frozenset({"ok", "refused", "error"})
_SAFETY_DECISIONS = frozenset(
    {
        "allowed",
        "not_evaluated",
        "authorization_required",
        "unsafe_request",
        "error",
    }
)
_PARSE_ERROR_CODES = frozenset(
    {"payload_too_large", "invalid_json", "invalid_request", "unsupported_input"}
)
_REFUSAL_ERROR_CODES = frozenset({"authorization_required", "unsafe_request"})
_AUTHORIZATION_REDIRECT = (
    "Provide a true self-use or authorized-other attestation."
)


def _require_bool(value: object, field_name: str) -> None:
    if type(value) is not bool:
        raise TypeError(f"{field_name} must be bool")


def _require_literal(value: object, allowed: frozenset[str], field_name: str) -> None:
    if value not in allowed:
        raise ValueError(f"unsupported {field_name}")


@dataclass(frozen=True)
class RealUseProfileV1:
    calendar_type: CalendarType
    birth_date: str
    birth_time: str
    birthplace: str
    gender: str
    focus_topic: str

    def __post_init__(self) -> None:
        if self.calendar_type != "gregorian":
            raise ValueError("unsupported calendar_type")


@dataclass(frozen=True)
class AuthorizationAttestationV1:
    subject_relation: SubjectRelation
    attested: bool

    def __post_init__(self) -> None:
        _require_literal(self.subject_relation, _RELATIONS, "subject_relation")
        _require_bool(self.attested, "attested")


@dataclass(frozen=True)
class RealUseOptionsV1:
    report_format: ReportFormat | None
    include_profile_in_report: bool

    def __post_init__(self) -> None:
        if self.report_format is not None:
            _require_literal(self.report_format, _REPORT_FORMATS, "report_format")
        _require_bool(
            self.include_profile_in_report,
            "include_profile_in_report",
        )


@dataclass(frozen=True)
class RealUseRequestV1:
    schema_version: Literal["real-use-request-v1"]
    request_id: str | None
    operation: RealUseOperation
    profile: RealUseProfileV1
    authorization: AuthorizationAttestationV1
    options: RealUseOptionsV1

    def __post_init__(self) -> None:
        if self.schema_version != REAL_USE_REQUEST_SCHEMA_VERSION:
            raise ValueError("unsupported schema_version")
        if self.request_id is not None and not isinstance(self.request_id, str):
            raise TypeError("request_id must be str or None")
        _require_literal(self.operation, _OPERATIONS, "operation")
        if not isinstance(self.profile, RealUseProfileV1):
            raise TypeError("profile must be RealUseProfileV1")
        if not isinstance(self.authorization, AuthorizationAttestationV1):
            raise TypeError("authorization must be AuthorizationAttestationV1")
        if not isinstance(self.options, RealUseOptionsV1):
            raise TypeError("options must be RealUseOptionsV1")
        format_matches = (
            self.operation == "analysis" and self.options.report_format is None
        ) or (
            self.operation == "report" and self.options.report_format is not None
        )
        if not format_matches:
            raise ValueError("operation and report_format are incompatible")


@dataclass(frozen=True)
class ApplicationErrorV1:
    code: ApplicationErrorCode
    message: str
    field_path: str | None
    retryable: bool
    trace_id: str

    def __post_init__(self) -> None:
        _require_literal(self.code, APPLICATION_ERROR_CODES, "code")
        _require_bool(self.retryable, "retryable")


@dataclass(frozen=True)
class ApplicationSafetyV1:
    allowed: bool
    decision: SafetyDecision
    categories: tuple[str, ...]
    redirect_message: str
    requires_narrowing: bool

    def __post_init__(self) -> None:
        _require_bool(self.allowed, "allowed")
        _require_literal(self.decision, _SAFETY_DECISIONS, "decision")
        object.__setattr__(self, "categories", tuple(self.categories))
        _require_bool(self.requires_narrowing, "requires_narrowing")


@dataclass(frozen=True)
class ApplicationProvenanceV1:
    engine_version: str
    ruleset_version: str
    provider_version: str
    chart_source_type: ChartSourceType
    chart_source_confidence: ChartSourceConfidence
    evidence_baseline_id: str
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.chart_source_type != "calculated":
            raise ValueError("unsupported chart_source_type")
        if self.chart_source_confidence != "deterministic_supported_range":
            raise ValueError("unsupported chart_source_confidence")
        object.__setattr__(self, "evidence_ids", tuple(self.evidence_ids))


@dataclass(frozen=True)
class ApplicationWarningV1:
    code: str
    message: str


@dataclass(frozen=True)
class ApplicationPrivacyV1:
    retention: RetentionPolicy
    contains_sensitive_profile: bool

    def __post_init__(self) -> None:
        if self.retention != "not_stored_by_engine":
            raise ValueError("unsupported retention")
        _require_bool(
            self.contains_sensitive_profile,
            "contains_sensitive_profile",
        )


@dataclass(frozen=True)
class ApplicationContentV1:
    media_type: ContentMediaType
    content: str
    contains_sensitive_profile: bool

    def __post_init__(self) -> None:
        _require_literal(self.media_type, CONTENT_MEDIA_TYPES, "media_type")
        _require_bool(
            self.contains_sensitive_profile,
            "contains_sensitive_profile",
        )


@dataclass(frozen=True)
class ApplicationAnalysisResultV1:
    chart: dict[str, object]
    calculation: dict[str, object]


@dataclass(frozen=True)
class ApplicationReportResultV1:
    report: dict[str, object] | None
    content: ApplicationContentV1 | None

    def __post_init__(self) -> None:
        if (self.report is None) == (self.content is None):
            raise ValueError("report result requires exactly one representation")


ApplicationResultV1 = ApplicationAnalysisResultV1 | ApplicationReportResultV1


@dataclass(frozen=True)
class RealUseResponseV1:
    schema_version: Literal["real-use-response-v1"]
    trace_id: str
    operation: RealUseOperation | None
    status: ResponseStatus
    result: ApplicationResultV1 | None
    safety: ApplicationSafetyV1
    provenance: ApplicationProvenanceV1 | None
    warnings: tuple[ApplicationWarningV1, ...]
    privacy: ApplicationPrivacyV1
    error: ApplicationErrorV1 | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "warnings", tuple(self.warnings))
        self._validate_envelope_types_and_literals()
        if self.status == "ok":
            self._validate_ok()
        else:
            self._validate_non_ok()

    def _validate_envelope_types_and_literals(self) -> None:
        if self.schema_version != REAL_USE_RESPONSE_SCHEMA_VERSION:
            raise ValueError("unsupported schema_version")
        if self.operation is not None:
            _require_literal(self.operation, _OPERATIONS, "operation")
        _require_literal(self.status, _RESPONSE_STATUSES, "status")
        if not isinstance(self.safety, ApplicationSafetyV1):
            raise TypeError("safety must be ApplicationSafetyV1")
        if not isinstance(self.privacy, ApplicationPrivacyV1):
            raise TypeError("privacy must be ApplicationPrivacyV1")
        if not all(isinstance(item, ApplicationWarningV1) for item in self.warnings):
            raise TypeError("warnings must contain ApplicationWarningV1 values")

    def _validate_ok(self) -> None:
        expected_result_type = (
            ApplicationAnalysisResultV1
            if self.operation == "analysis"
            else ApplicationReportResultV1
        )
        if self.operation is None or not isinstance(self.result, expected_result_type):
            raise ValueError("ok response operation and result are incompatible")
        if self.provenance is None or self.error is not None:
            raise ValueError("ok response requires provenance and no error")
        if self.safety != ApplicationSafetyV1(True, "allowed", (), "", False):
            raise ValueError("ok response requires allowed safety")

    def _validate_non_ok(self) -> None:
        if self.result is not None or self.provenance is not None:
            raise ValueError("non-ok response requires null result and provenance")
        if self.error is None:
            raise ValueError("non-ok response requires an error")
        if self.error.trace_id != self.trace_id:
            raise ValueError("error trace_id must match response trace_id")
        if self.privacy != ApplicationPrivacyV1("not_stored_by_engine", False):
            raise ValueError("non-ok response requires non-sensitive privacy")
        if self.status == "refused":
            self._validate_refusal()
        else:
            self._validate_error()

    def _validate_refusal(self) -> None:
        if self.operation is None or self.error is None:
            raise ValueError("refused response requires parsed operation and error")
        if self.error.code not in _REFUSAL_ERROR_CODES:
            raise ValueError("refused response requires a refusal error code")
        if self.error.code == "authorization_required":
            expected = ApplicationSafetyV1(
                False,
                "authorization_required",
                ("authorization",),
                _AUTHORIZATION_REDIRECT,
                False,
            )
            if self.safety != expected:
                raise ValueError("authorization refusal safety is invalid")
            return
        if (
            self.safety.allowed
            or self.safety.decision != "unsafe_request"
            or not self.safety.categories
            or not self.safety.redirect_message
            or not self.safety.requires_narrowing
        ):
            raise ValueError("unsafe refusal safety is invalid")

    def _validate_error(self) -> None:
        if self.error is None:
            raise ValueError("error response requires an error")
        if self.error.code in _REFUSAL_ERROR_CODES:
            raise ValueError("refusal error codes require refused status")
        is_parse_error = self.error.code in _PARSE_ERROR_CODES
        if is_parse_error != (self.operation is None):
            raise ValueError("operation is null only for parse errors")
        expected_decision: SafetyDecision = (
            "not_evaluated" if is_parse_error else "error"
        )
        if self.safety != ApplicationSafetyV1(
            False,
            expected_decision,
            (),
            "",
            False,
        ):
            raise ValueError("error response safety is invalid")
