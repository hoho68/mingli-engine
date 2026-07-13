import json
import re
import unicodedata
from datetime import date
from typing import Literal, cast

from mingli_engine.application_models import (
    REAL_USE_REQUEST_SCHEMA_VERSION,
    ApplicationErrorCode,
    AuthorizationAttestationV1,
    CalendarType,
    RealUseOperation,
    RealUseOptionsV1,
    RealUseProfileV1,
    RealUseRequestV1,
    ReportFormat,
    SubjectRelation,
)


MAX_REQUEST_BYTES = 32 * 1024
MAX_JSON_DEPTH = 8

_ROOT_FIELDS = (
    "schema_version",
    "request_id",
    "operation",
    "profile",
    "authorization",
    "options",
)
_PROFILE_FIELDS = (
    "calendar_type",
    "birth_date",
    "birth_time",
    "birthplace",
    "gender",
    "focus_topic",
)
_AUTHORIZATION_FIELDS = ("subject_relation", "attested")
_OPTIONS_FIELDS = ("report_format", "include_profile_in_report")
_UNSUPPORTED_FIELDS = frozenset(
    {
        "birth_datetime",
        "calculation",
        "calculation_bundle",
        "chart",
        "external_chart",
        "longitude",
        "pillars",
        "precomputed_calculation",
        "timezone",
        "true_solar_time",
    }
)
_REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}\Z", flags=re.ASCII)
_TIME_PATTERN = re.compile(r"(\d{2}):(\d{2})\Z", flags=re.ASCII)
_MIN_BIRTH_DATE = date(1901, 1, 1)
_MAX_BIRTH_DATE = date(2099, 12, 31)

_ERROR_MESSAGES: dict[ApplicationErrorCode, str] = {
    "invalid_json": "Request payload is not valid JSON.",
    "invalid_request": "Request fields are invalid.",
    "authorization_required": "Authorization is required.",
    "unsafe_request": "Request cannot be processed safely.",
    "unsupported_input": "Request contains unsupported input.",
    "payload_too_large": "Request payload exceeds 32 KiB.",
    "response_too_large": "Response payload exceeds the size limit.",
    "calculation_failed": "Calculation could not be completed.",
    "knowledge_unavailable": "Required knowledge is unavailable.",
    "internal_error": "Request processing failed.",
}


class ApplicationInputError(ValueError):
    def __init__(
        self,
        code: ApplicationErrorCode,
        field_path: str | None,
    ) -> None:
        self.code = code
        self.field_path = field_path
        self.message = _ERROR_MESSAGES[code]
        super().__init__(self.message)


class _StrictJsonError(ValueError):
    pass


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _StrictJsonError from None
        result[key] = value
    return result


def _reject_non_finite(_value: str) -> object:
    raise _StrictJsonError from None


def _parse_json(payload: bytes) -> object:
    if len(payload) > MAX_REQUEST_BYTES:
        raise ApplicationInputError("payload_too_large", None)
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise ApplicationInputError("invalid_json", None) from None
    try:
        value: object = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_finite,
        )
    except (json.JSONDecodeError, _StrictJsonError, RecursionError):
        raise ApplicationInputError("invalid_json", None) from None
    if _json_depth(value) > MAX_JSON_DEPTH:
        raise ApplicationInputError("invalid_json", "$")
    return value


def _json_depth(value: object) -> int:
    if isinstance(value, dict):
        if not value:
            return 1
        return 1 + max(_json_depth(item) for item in value.values())
    if isinstance(value, list):
        if not value:
            return 1
        return 1 + max(_json_depth(item) for item in value)
    return 0


def _require_object(value: object, field_path: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ApplicationInputError("invalid_request", field_path)
    return value


def _validate_exact_keys(
    value: dict[str, object],
    expected: tuple[str, ...],
    field_path: str,
) -> None:
    for key in value:
        if key in _UNSUPPORTED_FIELDS:
            raise ApplicationInputError(
                "unsupported_input",
                f"{field_path}.{key}",
            )
    expected_set = frozenset(expected)
    if any(key not in expected_set for key in value):
        raise ApplicationInputError("invalid_request", field_path)
    for key in expected:
        if key not in value:
            raise ApplicationInputError(
                "invalid_request",
                f"{field_path}.{key}",
            )


def _require_string(value: object, field_path: str) -> str:
    if not isinstance(value, str):
        raise ApplicationInputError("invalid_request", field_path)
    return value


def _require_bool(value: object, field_path: str) -> bool:
    if type(value) is not bool:
        raise ApplicationInputError("invalid_request", field_path)
    return cast(bool, value)


def _require_literal(
    value: object,
    allowed: frozenset[str],
    field_path: str,
    *,
    code: Literal["invalid_request", "unsupported_input"] = "invalid_request",
) -> str:
    text = _require_string(value, field_path)
    if text not in allowed:
        raise ApplicationInputError(code, field_path)
    return text


def _require_request_id(value: object) -> str | None:
    if value is None:
        return None
    request_id = _require_string(value, "$.request_id")
    if _REQUEST_ID_PATTERN.fullmatch(request_id) is None:
        raise ApplicationInputError("invalid_request", "$.request_id")
    return request_id


def _require_birth_date(value: object) -> str:
    field_path = "$.profile.birth_date"
    text = _require_string(value, field_path)
    if _DATE_PATTERN.fullmatch(text) is None:
        raise ApplicationInputError("invalid_request", field_path)
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        raise ApplicationInputError("invalid_request", field_path) from None
    if not _MIN_BIRTH_DATE <= parsed <= _MAX_BIRTH_DATE:
        raise ApplicationInputError("invalid_request", field_path)
    return text


def _require_birth_time(value: object) -> str:
    field_path = "$.profile.birth_time"
    text = _require_string(value, field_path)
    match = _TIME_PATTERN.fullmatch(text)
    if match is None:
        raise ApplicationInputError("invalid_request", field_path)
    hour, minute = (int(part) for part in match.groups())
    if hour > 23 or minute > 59:
        raise ApplicationInputError("invalid_request", field_path)
    return text


def _require_free_text(value: object, field_path: str, limit: int) -> str:
    text = _require_string(value, field_path)
    validation_copy = unicodedata.normalize("NFKC", text)
    if len(text) > limit or len(validation_copy) > limit:
        raise ApplicationInputError("invalid_request", field_path)
    return text


def _validated_objects(
    raw: object,
) -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    root = _require_object(raw, "$")
    _validate_exact_keys(root, _ROOT_FIELDS, "$")
    profile = _require_object(root["profile"], "$.profile")
    authorization = _require_object(root["authorization"], "$.authorization")
    options = _require_object(root["options"], "$.options")
    _validate_exact_keys(profile, _PROFILE_FIELDS, "$.profile")
    _validate_exact_keys(
        authorization,
        _AUTHORIZATION_FIELDS,
        "$.authorization",
    )
    _validate_exact_keys(options, _OPTIONS_FIELDS, "$.options")
    return root, profile, authorization, options


def _construct_request(raw: object) -> RealUseRequestV1:
    root, profile, authorization, options = _validated_objects(raw)
    schema_version = _require_literal(
        root["schema_version"],
        frozenset({REAL_USE_REQUEST_SCHEMA_VERSION}),
        "$.schema_version",
    )
    request_id = _require_request_id(root["request_id"])
    operation = _require_literal(
        root["operation"],
        frozenset({"analysis", "report"}),
        "$.operation",
    )
    calendar_type = _require_literal(
        profile["calendar_type"],
        frozenset({"gregorian"}),
        "$.profile.calendar_type",
        code="unsupported_input",
    )
    birth_date = _require_birth_date(profile["birth_date"])
    birth_time = _require_birth_time(profile["birth_time"])
    birthplace = _require_free_text(
        profile["birthplace"],
        "$.profile.birthplace",
        160,
    )
    gender = _require_free_text(profile["gender"], "$.profile.gender", 500)
    focus_topic = _require_free_text(
        profile["focus_topic"],
        "$.profile.focus_topic",
        500,
    )
    subject_relation = _require_literal(
        authorization["subject_relation"],
        frozenset({"self", "authorized_other"}),
        "$.authorization.subject_relation",
    )
    attested = _require_bool(
        authorization["attested"],
        "$.authorization.attested",
    )
    report_format_value = options["report_format"]
    if report_format_value is None:
        report_format = None
    else:
        report_format = _require_literal(
            report_format_value,
            frozenset({"json", "markdown", "html"}),
            "$.options.report_format",
        )
    include_profile = _require_bool(
        options["include_profile_in_report"],
        "$.options.include_profile_in_report",
    )
    if (operation == "analysis") != (report_format is None):
        raise ApplicationInputError("invalid_request", "$.options.report_format")

    return RealUseRequestV1(
        schema_version=cast(Literal["real-use-request-v1"], schema_version),
        request_id=request_id,
        operation=cast(RealUseOperation, operation),
        profile=RealUseProfileV1(
            calendar_type=cast(CalendarType, calendar_type),
            birth_date=birth_date,
            birth_time=birth_time,
            birthplace=birthplace,
            gender=gender,
            focus_topic=focus_topic,
        ),
        authorization=AuthorizationAttestationV1(
            subject_relation=cast(SubjectRelation, subject_relation),
            attested=attested,
        ),
        options=RealUseOptionsV1(
            report_format=cast(ReportFormat | None, report_format),
            include_profile_in_report=include_profile,
        ),
    )


def parse_real_use_request(payload: bytes) -> RealUseRequestV1:
    raw = _parse_json(payload)
    try:
        return _construct_request(raw)
    except ApplicationInputError:
        raise
    except (TypeError, ValueError):
        raise ApplicationInputError("invalid_request", "$") from None
