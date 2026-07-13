import copy
import json
import unicodedata
from pathlib import Path
from typing import Any

import pytest

import mingli_engine.application_inputs as application_inputs
from mingli_engine.application_inputs import (
    MAX_REQUEST_BYTES,
    ApplicationInputError,
    parse_real_use_request,
)
from mingli_engine.application_models import (
    AuthorizationAttestationV1,
    RealUseOptionsV1,
    RealUseProfileV1,
    RealUseRequestV1,
)


FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "application"


def _mapping(name: str = "valid_analysis_request.json") -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _encode(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def _payload_with_attested_number(number: bytes) -> bytes:
    payload = _encode(_mapping())
    marker = b'"attested":true'
    assert marker in payload
    return payload.replace(marker, b'"attested":' + number)


def _error(
    payload: bytes,
    code: str,
    field_path: str | None,
) -> ApplicationInputError:
    with pytest.raises(ApplicationInputError) as caught:
        parse_real_use_request(payload)
    assert caught.value.code == code
    assert caught.value.field_path == field_path
    return caught.value


@pytest.mark.parametrize(
    ("fixture_name", "expected"),
    [
        (
            "valid_analysis_request.json",
            RealUseRequestV1(
                schema_version="real-use-request-v1",
                request_id="synthetic-analysis-001",
                operation="analysis",
                profile=RealUseProfileV1(
                    calendar_type="gregorian",
                    birth_date="1996-12-15",
                    birth_time="09:30",
                    birthplace="Synthetic UTC+08 Place",
                    gender="unknown",
                    focus_topic="traditional structural overview",
                ),
                authorization=AuthorizationAttestationV1(
                    subject_relation="self",
                    attested=True,
                ),
                options=RealUseOptionsV1(
                    report_format=None,
                    include_profile_in_report=False,
                ),
            ),
        ),
        (
            "valid_report_request.json",
            RealUseRequestV1(
                schema_version="real-use-request-v1",
                request_id="synthetic-report-001",
                operation="report",
                profile=RealUseProfileV1(
                    calendar_type="gregorian",
                    birth_date="2001-02-03",
                    birth_time="23:05",
                    birthplace="Synthetic UTC+08 Report Place",
                    gender="unknown",
                    focus_topic="traditional report with school-aware uncertainty",
                ),
                authorization=AuthorizationAttestationV1(
                    subject_relation="authorized_other",
                    attested=True,
                ),
                options=RealUseOptionsV1(
                    report_format="markdown",
                    include_profile_in_report=True,
                ),
            ),
        ),
    ],
)
def test_valid_fixtures_construct_explicit_request_dtos(
    fixture_name: str,
    expected: RealUseRequestV1,
) -> None:
    assert parse_real_use_request((FIXTURE_DIR / fixture_name).read_bytes()) == expected


def test_accepts_valid_utf8_and_preserves_original_display_text() -> None:
    payload = _mapping()
    payload["profile"]["birthplace"] = "Ａ区合成地点"
    payload["profile"]["focus_topic"] = "传统结构概览"

    request = parse_real_use_request(_encode(payload))

    assert request.profile.birthplace == "Ａ区合成地点"
    assert request.profile.focus_topic == "传统结构概览"


def test_accepts_exactly_32_kib_including_json_whitespace() -> None:
    payload = _encode(_mapping())
    padded = payload + (b" " * (MAX_REQUEST_BYTES - len(payload)))

    assert len(padded) == 32 * 1024
    assert parse_real_use_request(padded).operation == "analysis"


def test_payload_size_precedes_utf8_decoding() -> None:
    error = _error(
        b"\xff" + (b" " * MAX_REQUEST_BYTES),
        "payload_too_large",
        None,
    )

    assert str(error) == "Request payload exceeds 32 KiB."


@pytest.mark.parametrize(
    "payload",
    [
        b"\xff",
        b'{"schema_version":',
        b'{"request_id":"first","request_id":"second"}',
        b'{"value":NaN}',
        b'{"value":Infinity}',
        b'{"value":-Infinity}',
    ],
)
def test_rejects_invalid_utf8_json_duplicates_and_non_finite_values(
    payload: bytes,
) -> None:
    _error(payload, "invalid_json", None)


@pytest.mark.parametrize("number", [b"1e400", b"-1e400", b"1e+400", b"-1e+400"])
def test_rejects_float_exponents_that_overflow_to_infinity(number: bytes) -> None:
    error = _error(
        _payload_with_attested_number(number),
        "invalid_json",
        None,
    )
    raw_value = number.decode("ascii")
    assert raw_value not in str(error)
    assert raw_value not in repr(error)


@pytest.mark.parametrize(
    "number",
    [b"1.5", b"-1.5", b"1e2", b"1e-2", b"-1e-2", b"1e-400"],
)
def test_finite_floats_pass_json_validation_before_strict_field_types(
    number: bytes,
) -> None:
    error = _error(
        _payload_with_attested_number(number),
        "invalid_request",
        "$.authorization.attested",
    )
    raw_value = number.decode("ascii")
    assert raw_value not in str(error)
    assert raw_value not in repr(error)


def test_rejects_json_nesting_depth_above_eight() -> None:
    nested: object = 0
    for _ in range(9):
        nested = [nested]

    _error(_encode(nested), "invalid_json", "$")


def test_deep_small_json_never_leaks_recursion_error_or_inner_value() -> None:
    raw_value = "private-depth-sentinel"
    payload = (b"[" * 600) + _encode(raw_value) + (b"]" * 600)
    assert len(payload) < 2 * 1024

    error = _error(payload, "invalid_json", "$")

    assert raw_value not in str(error)
    assert raw_value not in repr(error)


def test_json_decoder_recursion_error_is_also_stable_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_recursion_error(*_args: object, **_kwargs: object) -> object:
        raise RecursionError("private decoder detail")

    monkeypatch.setattr(application_inputs.json, "loads", raise_recursion_error)

    error = _error(b"{}", "invalid_json", None)
    assert "private decoder detail" not in str(error)
    assert "private decoder detail" not in repr(error)


@pytest.mark.parametrize(
    ("object_path", "field_name"),
    [
        ((), "schema_version"),
        ((), "request_id"),
        ((), "operation"),
        ((), "profile"),
        ((), "authorization"),
        ((), "options"),
        (("profile",), "calendar_type"),
        (("profile",), "birth_date"),
        (("profile",), "birth_time"),
        (("profile",), "birthplace"),
        (("profile",), "gender"),
        (("profile",), "focus_topic"),
        (("authorization",), "subject_relation"),
        (("authorization",), "attested"),
        (("options",), "report_format"),
        (("options",), "include_profile_in_report"),
    ],
)
def test_every_field_is_required(
    object_path: tuple[str, ...],
    field_name: str,
) -> None:
    payload = _mapping()
    target = payload
    for part in object_path:
        target = target[part]
    del target[field_name]
    field_path = ".".join(("$", *object_path, field_name))

    _error(_encode(payload), "invalid_request", field_path)


@pytest.mark.parametrize(
    ("object_path", "expected_path"),
    [
        ((), "$"),
        (("profile",), "$.profile"),
        (("authorization",), "$.authorization"),
        (("options",), "$.options"),
    ],
)
def test_unknown_fields_are_rejected_at_every_object_level(
    object_path: tuple[str, ...],
    expected_path: str,
) -> None:
    payload = _mapping()
    target = payload
    for part in object_path:
        target = target[part]
    target["private_secret_unknown"] = "must-not-echo"

    error = _error(_encode(payload), "invalid_request", expected_path)
    assert "private_secret_unknown" not in str(error)
    assert "must-not-echo" not in str(error)


@pytest.mark.parametrize(
    ("path", "bad_value"),
    [
        (("schema_version",), None),
        (("request_id",), 1),
        (("operation",), None),
        (("profile",), []),
        (("authorization",), []),
        (("options",), []),
        (("profile", "calendar_type"), None),
        (("profile", "birth_date"), 19961215),
        (("profile", "birth_time"), 930),
        (("profile", "birthplace"), None),
        (("profile", "gender"), None),
        (("profile", "focus_topic"), None),
        (("authorization", "subject_relation"), None),
        (("authorization", "attested"), 1),
        (("options", "report_format"), False),
        (("options", "include_profile_in_report"), 0),
    ],
)
def test_every_field_has_a_strict_json_type(
    path: tuple[str, ...],
    bad_value: object,
) -> None:
    payload = _mapping()
    target = payload
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = bad_value

    _error(_encode(payload), "invalid_request", ".".join(("$", *path)))


@pytest.mark.parametrize("request_id", [None, "a", "A_0-9", "x" * 64])
def test_request_id_accepts_nullable_and_ascii_pattern(request_id: str | None) -> None:
    payload = _mapping()
    payload["request_id"] = request_id

    assert parse_real_use_request(_encode(payload)).request_id == request_id


@pytest.mark.parametrize(
    "request_id",
    ["", "x" * 65, "contains space", "contains.dot", "全角Ａ"],
)
def test_request_id_rejects_values_outside_ascii_pattern(request_id: str) -> None:
    payload = _mapping()
    payload["request_id"] = request_id

    _error(_encode(payload), "invalid_request", "$.request_id")


def test_wrong_schema_is_rejected() -> None:
    payload = _mapping()
    payload["schema_version"] = "real-use-request-v2-private"

    _error(_encode(payload), "invalid_request", "$.schema_version")


def test_illegal_subject_relation_does_not_echo_value() -> None:
    payload = _mapping()
    raw_value = "secret-illegal-relation"
    payload["authorization"]["subject_relation"] = raw_value

    error = _error(
        _encode(payload),
        "invalid_request",
        "$.authorization.subject_relation",
    )
    assert raw_value not in str(error)
    assert raw_value not in repr(error)


def test_false_attestation_is_schema_valid() -> None:
    payload = _mapping()
    payload["authorization"]["attested"] = False

    assert parse_real_use_request(_encode(payload)).authorization.attested is False


@pytest.mark.parametrize(
    ("operation", "report_format"),
    [
        ("analysis", "json"),
        ("analysis", "markdown"),
        ("analysis", "html"),
        ("report", None),
    ],
)
def test_operation_and_report_format_must_match(
    operation: str,
    report_format: str | None,
) -> None:
    payload = _mapping()
    payload["operation"] = operation
    payload["options"]["report_format"] = report_format

    _error(_encode(payload), "invalid_request", "$.options.report_format")


@pytest.mark.parametrize(
    ("path", "bad_value"),
    [
        (("operation",), "calculate"),
        (("options", "report_format"), "pdf"),
    ],
)
def test_operation_and_report_format_literals_are_closed(
    path: tuple[str, ...],
    bad_value: str,
) -> None:
    payload = _mapping()
    target = payload
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = bad_value

    _error(_encode(payload), "invalid_request", ".".join(("$", *path)))


@pytest.mark.parametrize("calendar_type", ["lunar", "julian", "solar"])
def test_only_gregorian_calendar_is_supported(calendar_type: str) -> None:
    payload = _mapping()
    payload["profile"]["calendar_type"] = calendar_type

    _error(_encode(payload), "unsupported_input", "$.profile.calendar_type")


@pytest.mark.parametrize(
    "birth_date",
    [
        "1900-12-31",
        "2100-01-01",
        "2000-02-30",
        "2000-2-03",
        "2000/02/03",
        "2000-02-03T09:30",
    ],
)
def test_birth_date_requires_canonical_supported_gregorian_date(
    birth_date: str,
) -> None:
    payload = _mapping()
    payload["profile"]["birth_date"] = birth_date

    _error(_encode(payload), "invalid_request", "$.profile.birth_date")


@pytest.mark.parametrize("birth_date", ["1901-01-01", "2000-02-29", "2099-12-31"])
def test_birth_date_accepts_supported_boundaries(birth_date: str) -> None:
    payload = _mapping()
    payload["profile"]["birth_date"] = birth_date

    assert parse_real_use_request(_encode(payload)).profile.birth_date == birth_date


@pytest.mark.parametrize(
    "birth_time",
    ["9:30", "09:3", "24:00", "23:60", "09:30:00", "09:30+08:00", "09:30Z"],
)
def test_birth_time_requires_canonical_unaware_wall_time(birth_time: str) -> None:
    payload = _mapping()
    payload["profile"]["birth_time"] = birth_time

    _error(_encode(payload), "invalid_request", "$.profile.birth_time")


@pytest.mark.parametrize("birth_time", ["00:00", "09:30", "23:59"])
def test_birth_time_accepts_supported_boundaries(birth_time: str) -> None:
    payload = _mapping()
    payload["profile"]["birth_time"] = birth_time

    assert parse_real_use_request(_encode(payload)).profile.birth_time == birth_time


@pytest.mark.parametrize(
    ("field_name", "limit"),
    [("birthplace", 160), ("focus_topic", 500), ("gender", 500)],
)
def test_free_text_limits_are_inclusive(field_name: str, limit: int) -> None:
    payload = _mapping()
    payload["profile"][field_name] = "x" * limit

    assert getattr(parse_real_use_request(_encode(payload)).profile, field_name) == (
        "x" * limit
    )


@pytest.mark.parametrize(
    ("field_name", "limit"),
    [("birthplace", 160), ("focus_topic", 500), ("gender", 500)],
)
def test_free_text_rejects_normalized_values_above_limits(
    field_name: str,
    limit: int,
) -> None:
    payload = _mapping()
    ligature = "\ufb03"
    raw_value = ligature * ((limit // 3) + 1)
    normalized = unicodedata.normalize("NFKC", raw_value)
    assert len(raw_value) <= limit < len(normalized)
    payload["profile"][field_name] = raw_value

    error = _error(
        _encode(payload),
        "invalid_request",
        f"$.profile.{field_name}",
    )
    assert raw_value not in str(error)
    assert normalized not in str(error)


@pytest.mark.parametrize(
    ("object_path", "field_name"),
    [
        ((), "chart"),
        ((), "precomputed_calculation"),
        (("profile",), "external_chart"),
        (("profile",), "calculation_bundle"),
    ],
)
def test_external_charts_and_precomputed_fields_are_unsupported(
    object_path: tuple[str, ...],
    field_name: str,
) -> None:
    payload = copy.deepcopy(_mapping())
    target = payload
    for part in object_path:
        target = target[part]
    target[field_name] = {"private": "must-not-echo"}
    object_field_path = ".".join(("$", *object_path, field_name))

    error = _error(_encode(payload), "unsupported_input", object_field_path)
    assert "must-not-echo" not in str(error)


def test_error_messages_are_stable_and_never_use_parser_exception_text() -> None:
    first = _error(b'{"secret-one":', "invalid_json", None)
    second = _error(b'{"secret-two":', "invalid_json", None)

    assert first.message == second.message == "Request payload is not valid JSON."
    assert str(first) == str(second) == first.message
    assert "secret-one" not in repr(first)
    assert "secret-two" not in repr(second)
