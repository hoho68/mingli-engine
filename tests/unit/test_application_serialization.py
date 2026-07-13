import json
import math
from copy import deepcopy
from dataclasses import dataclass, fields, replace
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from mingli_engine.application_models import (
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
    RealUseOperation,
    RealUseResponseV1,
    ResponseStatus,
    SafetyDecision,
)
from mingli_engine.application_serialization import (
    MAX_RESPONSE_BYTES,
    ResponseSizeError,
    response_status_from_json_bytes,
    serialize_application_analysis_result,
    serialize_application_content,
    serialize_application_error,
    serialize_application_privacy,
    serialize_application_provenance,
    serialize_application_report_result,
    serialize_application_safety,
    serialize_application_warning,
    serialize_calculation_bundle,
    serialize_chart,
    serialize_report,
    serialize_response,
    serialize_response_mapping,
)
from mingli_engine.bazi import analyze_bazi_chart
from mingli_engine.bazi.result_models import CalculationBundle
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BaziChart, Report
from mingli_engine.models import (
    CALCULATION_CONFIDENCES,
    CALCULATION_STATUSES,
)
from mingli_engine.report_inputs import birth_profile_from_dict
from mingli_engine.report_schema import build_report


TRACE_ID = "550e8400-e29b-41d4-a716-446655440000"
REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def calculated_bazi_chart() -> BaziChart:
    payload = json.loads(
        (REPO_ROOT / "examples" / "birth-profile.auto-gregorian.json").read_text(
            encoding="utf-8"
        )
    )
    return calculate_bazi_chart(birth_profile_from_dict(payload))


def _calculation(chart: BaziChart) -> CalculationBundle:
    return analyze_bazi_chart(
        chart,
        birth_datetime=datetime.fromisoformat(
            f"{chart.birth_profile.birth_date}T{chart.birth_profile.birth_time}"
        ),
    )


def _privacy() -> ApplicationPrivacyV1:
    return ApplicationPrivacyV1("not_stored_by_engine", False)


def _provenance(
    *,
    engine_version: str = "0.2.0",
    ruleset_version: str = "bazi-rules-v1",
) -> ApplicationProvenanceV1:
    return ApplicationProvenanceV1(
        engine_version=engine_version,
        ruleset_version=ruleset_version,
        provider_version="lunar-python-1.4.8",
        chart_source_type="calculated",
        chart_source_confidence="deterministic_supported_range",
        evidence_baseline_id="tracked-evidence-baseline",
        evidence_ids=("evidence.synthetic",),
    )


def _safety(
    decision: SafetyDecision,
    *,
    allowed: bool = False,
    categories: tuple[str, ...] = (),
    redirect_message: str = "",
    requires_narrowing: bool = False,
) -> ApplicationSafetyV1:
    return ApplicationSafetyV1(
        allowed,
        decision,
        categories,
        redirect_message,
        requires_narrowing,
    )


def _error(code: ApplicationErrorCode) -> ApplicationErrorV1:
    return ApplicationErrorV1(
        code=code,
        message="Controlled application outcome.",
        field_path=None,
        retryable=False,
        trace_id=TRACE_ID,
    )


def _ok_response(
    *,
    result: ApplicationAnalysisResultV1 | ApplicationReportResultV1 | None = None,
    operation: RealUseOperation = "analysis",
    provenance: ApplicationProvenanceV1 | None = None,
    privacy: ApplicationPrivacyV1 | None = None,
) -> RealUseResponseV1:
    if result is None:
        result = ApplicationAnalysisResultV1(
            chart={"day_master": "water"},
            calculation={"engine_version": "0.2.0"},
        )
    return RealUseResponseV1(
        schema_version=REAL_USE_RESPONSE_SCHEMA_VERSION,
        trace_id=TRACE_ID,
        operation=operation,
        status="ok",
        result=result,
        safety=_safety("allowed", allowed=True),
        provenance=provenance or _provenance(),
        warnings=(ApplicationWarningV1("limited_scope", "Scope is limited."),),
        privacy=privacy or _privacy(),
        error=None,
    )


def _non_ok_response(
    *,
    operation: RealUseOperation | None,
    status: ResponseStatus,
    safety: ApplicationSafetyV1,
    code: ApplicationErrorCode,
) -> RealUseResponseV1:
    return RealUseResponseV1(
        schema_version=REAL_USE_RESPONSE_SCHEMA_VERSION,
        trace_id=TRACE_ID,
        operation=operation,
        status=status,
        result=None,
        safety=safety,
        provenance=None,
        warnings=(),
        privacy=_privacy(),
        error=_error(code),
    )


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _valid_analysis_mapping(chart: BaziChart) -> dict[str, Any]:
    calculation = _calculation(chart)
    return serialize_response_mapping(
        _ok_response(
            result=ApplicationAnalysisResultV1(
                serialize_chart(chart),
                serialize_calculation_bundle(calculation),
            ),
            provenance=_provenance(
                engine_version=calculation.engine_version,
                ruleset_version=calculation.ruleset_version,
            ),
        )
    )


def _valid_report_mapping(chart: BaziChart) -> dict[str, Any]:
    calculation = _calculation(chart)
    report = build_report(chart, calculation)
    return serialize_response_mapping(
        _ok_response(
            operation="report",
            result=ApplicationReportResultV1(serialize_report(report), None),
        )
    )


def _mapping_at(root: dict[str, Any], path: tuple[object, ...]) -> dict[str, Any]:
    current: Any = root
    for part in path:
        current = current[part]
    assert isinstance(current, dict)
    return current


def test_chart_serializer_has_exact_public_shape_without_birth_profile(
    sample_bazi_chart: BaziChart,
) -> None:
    payload = serialize_chart(sample_bazi_chart)

    assert set(payload) == {
        "chart_source",
        "pillars",
        "day_master",
        "five_elements_summary",
        "ten_gods_summary",
        "strength_assessment",
        "pattern_candidates",
        "useful_god_candidates",
        "luck_cycle_summary",
    }
    assert set(payload["chart_source"]) == {
        "source_type",
        "source_note",
        "calendar_assumption",
        "timezone_assumption",
        "solar_terms_assumption",
        "true_solar_time_applied",
        "confidence",
    }
    assert all(
        set(pillar) == {
            "name",
            "heavenly_stem",
            "earthly_branch",
            "gan_zhi",
            "hidden_stems",
            "ten_god",
            "element",
        }
        for pillar in payload["pillars"]
    )
    assert "birth_profile" not in json.dumps(payload, ensure_ascii=False)


def test_calculation_serializer_covers_complete_public_bundle(
    calculated_bazi_chart: BaziChart,
) -> None:
    calculation = _calculation(calculated_bazi_chart)
    payload = serialize_calculation_bundle(calculation)

    assert set(payload) == {
        "engine_version",
        "ruleset_version",
        "facts",
        "branch_relations",
        "strength",
        "patterns",
        "useful_gods",
        "luck_cycles",
        "schools",
    }
    assert {"taboo_gods", "blind_images", "remedy_boundary"}.isdisjoint(payload)
    assert set(payload["facts"]) == {
        "day_master",
        "month_branch",
        "exposed_stems",
        "hidden_stems",
        "roots",
        "twelve_growth_by_pillar",
        "assumptions",
    }
    assert set(payload["strength"]) == {
        "reasoning",
        "score",
        "lower_bound",
        "upper_bound",
        "label",
        "contributions",
    }
    required_reasoning = {
        "status",
        "conclusion",
        "confidence",
        "supporting_signals",
        "opposing_signals",
        "assumptions",
        "missing_inputs",
        "rule_ids",
    }
    reasonings = [
        payload["strength"]["reasoning"],
        payload["luck_cycles"]["reasoning"],
        *(item["reasoning"] for item in payload["patterns"]),
        *(item["reasoning"] for item in payload["useful_gods"]),
        *(item["reasoning"] for item in payload["schools"]),
    ]
    assert reasonings
    assert all(set(item) == required_reasoning for item in reasonings)
    assert payload["facts"]["exposed_stems"]
    assert payload["facts"]["hidden_stems"]
    assert payload["facts"]["roots"]
    assert payload["branch_relations"]
    assert payload["strength"]["contributions"]
    assert payload["patterns"]
    assert payload["useful_gods"]
    assert set(payload["luck_cycles"]) == {
        "reasoning",
        "forward",
        "start_years",
        "start_months",
        "start_days",
        "start_solar",
        "pillars",
        "selected_year_relations",
    }
    assert isinstance(payload["luck_cycles"]["pillars"], list)
    assert payload["schools"]


def test_calculation_serializer_filters_assumptions_and_private_subclass_fields(
    calculated_bazi_chart: BaziChart,
) -> None:
    calculation = _calculation(calculated_bazi_chart)
    private_marker = "internal_config_path=C:/secret/provider.json"

    @dataclass(frozen=True)
    class PrivateCalculationBundle(CalculationBundle):
        private_config: str = private_marker

    calculation = replace(
        calculation,
        strength=replace(
            calculation.strength,
            reasoning=replace(
                calculation.strength.reasoning,
                assumptions=("calendar:gregorian", private_marker),
            ),
        ),
    )
    private_bundle = PrivateCalculationBundle(
        **{
            field.name: getattr(calculation, field.name)
            for field in fields(CalculationBundle)
        }
    )

    serialized = json.dumps(
        serialize_calculation_bundle(private_bundle),
        ensure_ascii=False,
    )

    assert "calendar:gregorian" in serialized
    assert "private_config" not in serialized
    assert private_marker not in serialized


def test_report_serializer_covers_complete_report_json_and_nested_keys(
    calculated_bazi_chart: BaziChart,
) -> None:
    report = build_report(calculated_bazi_chart, _calculation(calculated_bazi_chart))
    payload = serialize_report(report)

    assert set(payload) == {field.name for field in fields(Report)}
    assert all(
        set(item) == {
            "action_id",
            "title",
            "status",
            "rule_families",
            "evidence_ids",
            "conditions",
            "observation_prompt",
            "feedback_metric",
            "stop_boundary",
        }
        for item in payload["action_reflection_items"]
    )
    assert set(payload["report_evidence_audit"]) == {
        "audit_status",
        "rule_family_count",
        "formal_conclusion_count",
        "traced_evidence_unit_count",
        "enabled_rule_families",
        "conclusion_rule_families",
        "missing_rule_families",
        "open_conflicts",
        "guardrail_count",
        "unavailable_conclusion_count",
        "computed_rule_family_count",
        "indeterminate_rule_family_count",
        "disputed_rule_family_count",
        "not_computed_rule_family_count",
    }
    assert set(payload["knowledge_activation"]) == {
        "activation_status",
        "source_count",
        "report_usable_source_count",
        "approved_evidence_count",
        "required_rule_families",
        "enabled_rule_families",
        "missing_rule_families",
        "rule_family_counts",
        "risk_tier_counts",
        "sources_with_gaps",
        "open_conflicts",
        "quality_failures",
        "formal_conclusion_count",
        "unavailable_conclusion_count",
        "next_action",
        "guardrails",
    }
    assert set(payload["expanded_evidence"]) == {
        "source_summary",
        "formal_conclusions",
        "high_risk_notes",
        "unavailable_conclusions",
    }
    assert set(payload["safety_review"]) == {
        "allowed",
        "red_line_categories",
        "prohibited_phrases",
        "disclaimer_present",
        "redirect_message",
    }
    for conclusion in payload["expanded_evidence"]["formal_conclusions"]:
        assert set(conclusion) == {
            "conclusion_id",
            "title",
            "body",
            "rule_family",
            "strength",
            "risk_tier",
            "trace",
        }
        assert set(conclusion["trace"]) == {
            "trace_id",
            "conclusion_id",
            "chart_signals",
            "evidence_ids",
            "assumptions",
            "disagreement_note",
            "calculation_status",
            "calculation_confidence",
            "supporting_signals",
            "opposing_signals",
            "rule_ids",
            "missing_inputs",
            "school_views",
        }


def test_report_serializer_excludes_private_subclass_fields(
    calculated_bazi_chart: BaziChart,
) -> None:
    report = build_report(calculated_bazi_chart, _calculation(calculated_bazi_chart))

    @dataclass(frozen=True)
    class PrivateReport(Report):
        private_profile_cache: str = "SECRET_PROFILE_CACHE"

    private_report = PrivateReport(
        **{field.name: getattr(report, field.name) for field in fields(Report)}
    )

    serialized = json.dumps(serialize_report(private_report), ensure_ascii=False)

    assert "private_profile_cache" not in serialized
    assert "SECRET_PROFILE_CACHE" not in serialized


def test_each_nested_application_dto_serializer_has_exact_keys() -> None:
    content = ApplicationContentV1("text/markdown", "# Report", False)
    analysis = ApplicationAnalysisResultV1({"chart": True}, {"calculation": True})
    report = ApplicationReportResultV1(None, content)

    cases = (
        (
            serialize_application_error(_error("internal_error")),
            {"code", "message", "field_path", "retryable", "trace_id"},
        ),
        (
            serialize_application_safety(_safety("not_evaluated")),
            {
                "allowed",
                "decision",
                "categories",
                "redirect_message",
                "requires_narrowing",
            },
        ),
        (
            serialize_application_provenance(_provenance()),
            {
                "engine_version",
                "ruleset_version",
                "provider_version",
                "chart_source_type",
                "chart_source_confidence",
                "evidence_baseline_id",
                "evidence_ids",
            },
        ),
        (
            serialize_application_warning(
                ApplicationWarningV1("limited_scope", "Scope is limited.")
            ),
            {"code", "message"},
        ),
        (
            serialize_application_privacy(_privacy()),
            {"retention", "contains_sensitive_profile"},
        ),
        (
            serialize_application_content(content),
            {"media_type", "content", "contains_sensitive_profile"},
        ),
        (
            serialize_application_analysis_result(analysis),
            {"chart", "calculation"},
        ),
        (
            serialize_application_report_result(report),
            {"report", "content"},
        ),
    )

    for payload, expected_keys in cases:
        assert set(payload) == expected_keys
    assert serialize_application_safety(_safety("not_evaluated"))["categories"] == []
    assert serialize_application_provenance(_provenance())["evidence_ids"] == [
        "evidence.synthetic"
    ]
    assert serialize_application_report_result(report)["report"] is None


def test_response_mapping_has_exact_nested_keys_and_values() -> None:
    response = _ok_response()

    payload = serialize_response_mapping(response)

    assert set(payload) == {
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
    }
    assert payload == {
        "schema_version": "real-use-response-v1",
        "trace_id": TRACE_ID,
        "operation": "analysis",
        "status": "ok",
        "result": {
            "chart": {"day_master": "water"},
            "calculation": {"engine_version": "0.2.0"},
        },
        "safety": {
            "allowed": True,
            "decision": "allowed",
            "categories": [],
            "redirect_message": "",
            "requires_narrowing": False,
        },
        "provenance": {
            "engine_version": "0.2.0",
            "ruleset_version": "bazi-rules-v1",
            "provider_version": "lunar-python-1.4.8",
            "chart_source_type": "calculated",
            "chart_source_confidence": "deterministic_supported_range",
            "evidence_baseline_id": "tracked-evidence-baseline",
            "evidence_ids": ["evidence.synthetic"],
        },
        "warnings": [{"code": "limited_scope", "message": "Scope is limited."}],
        "privacy": {
            "retention": "not_stored_by_engine",
            "contains_sensitive_profile": False,
        },
        "error": None,
    }


@pytest.mark.parametrize(
    "response",
    [
        _non_ok_response(
            operation=None,
            status="error",
            safety=_safety("not_evaluated"),
            code="invalid_json",
        ),
        _non_ok_response(
            operation="analysis",
            status="refused",
            safety=_safety(
                "authorization_required",
                categories=("authorization",),
                redirect_message=(
                    "Provide a true self-use or authorized-other attestation."
                ),
            ),
            code="authorization_required",
        ),
        _non_ok_response(
            operation="report",
            status="refused",
            safety=_safety(
                "unsafe_request",
                categories=("professional_advice",),
                redirect_message="Use a qualified professional.",
                requires_narrowing=True,
            ),
            code="unsafe_request",
        ),
        _non_ok_response(
            operation="analysis",
            status="error",
            safety=_safety("error"),
            code="internal_error",
        ),
    ],
    ids=("parse-error", "authorization-refusal", "unsafe-refusal", "internal-error"),
)
def test_non_ok_response_matrix_serializes_every_required_value(
    response: RealUseResponseV1,
) -> None:
    payload = serialize_response_mapping(response)

    assert payload["schema_version"] == "real-use-response-v1"
    assert payload["trace_id"] == TRACE_ID
    assert payload["operation"] == response.operation
    assert payload["status"] == response.status
    assert payload["result"] is None
    assert payload["safety"] == serialize_application_safety(response.safety)
    assert payload["provenance"] is None
    assert payload["warnings"] == []
    assert payload["privacy"] == {
        "retention": "not_stored_by_engine",
        "contains_sensitive_profile": False,
    }
    assert payload["error"] == serialize_application_error(response.error)


def test_response_json_is_deterministic_utf8_sorted_compact_and_rejects_nan(
    calculated_bazi_chart: BaziChart,
) -> None:
    calculation = serialize_calculation_bundle(_calculation(calculated_bazi_chart))
    response = _ok_response(
        result=ApplicationAnalysisResultV1(
            chart=serialize_chart(calculated_bazi_chart),
            calculation=calculation,
        ),
        provenance=_provenance(
            engine_version=calculation["engine_version"],
            ruleset_version=calculation["ruleset_version"],
        ),
    )

    first = serialize_response(response)
    second = serialize_response(response)

    assert first == second
    assert first == json.dumps(
        serialize_response_mapping(response),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    assert calculated_bazi_chart.day_master.encode() in first
    assert b'"chart":{"chart_source":' in first

    non_finite_calculation = deepcopy(calculation)
    non_finite_calculation["strength"]["score"] = math.nan
    non_finite = _ok_response(
        result=ApplicationAnalysisResultV1(
            serialize_chart(calculated_bazi_chart),
            non_finite_calculation,
        ),
        provenance=_provenance(
            engine_version=calculation["engine_version"],
            ruleset_version=calculation["ruleset_version"],
        ),
    )
    with pytest.raises(ValueError, match="JSON compliant"):
        serialize_response(non_finite)


def test_response_serializer_enforces_one_mib_limit_without_fallback() -> None:
    assert MAX_RESPONSE_BYTES == 1024 * 1024
    content = ApplicationContentV1(
        "text/markdown",
        "x" * MAX_RESPONSE_BYTES,
        False,
    )
    response = _ok_response(
        operation="report",
        result=ApplicationReportResultV1(None, content),
    )

    with pytest.raises(ResponseSizeError, match="response exceeds 1048576 bytes"):
        serialize_response(response)


def test_response_status_reader_accepts_only_canonical_valid_internal_envelopes(
    calculated_bazi_chart: BaziChart,
) -> None:
    payload_mapping = _valid_analysis_mapping(calculated_bazi_chart)
    response = _ok_response(
        result=ApplicationAnalysisResultV1(
            payload_mapping["result"]["chart"],
            payload_mapping["result"]["calculation"],
        ),
        provenance=_provenance(
            engine_version=payload_mapping["result"]["calculation"][
                "engine_version"
            ],
            ruleset_version=payload_mapping["result"]["calculation"][
                "ruleset_version"
            ],
        ),
    )
    payload = serialize_response(response)

    assert response_status_from_json_bytes(payload) == "ok"

    parsed = json.loads(payload)
    invalid_payloads = [
        b"not-json",
        b'"not-an-envelope"',
        payload + b" ",
        payload.replace(b'"status":"ok"', b'"status":"invalid"'),
        json.dumps(
            {**parsed, "private": "do-not-accept"},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode(),
        payload.replace(
            b'"schema_version":"real-use-response-v1"',
            b'"schema_version":"real-use-response-v2"',
        ),
        payload.replace(
            b'"trace_id":"550e8400-e29b-41d4-a716-446655440000"',
            b'"trace_id":"550e8400-e29b-41d4-a716-446655440000",'
            b'"trace_id":"duplicate"',
        ),
    ]

    for invalid in invalid_payloads:
        with pytest.raises(ValueError, match="invalid internal response envelope"):
            response_status_from_json_bytes(invalid)


def test_response_status_reader_does_not_leak_invalid_payload_values() -> None:
    secret = "RAW_PROFILE_SECRET_74f580"
    payload = json.dumps(
        {"schema_version": "wrong", "secret": secret},
        separators=(",", ":"),
    ).encode()

    with pytest.raises(ValueError) as captured:
        response_status_from_json_bytes(payload)

    assert secret not in str(captured.value)
    assert str(captured.value) == "invalid internal response envelope"


def test_response_status_reader_rejects_illegal_error_matrix() -> None:
    valid = serialize_response(
        _non_ok_response(
            operation=None,
            status="error",
            safety=_safety("not_evaluated"),
            code="invalid_json",
        )
    )
    parsed: dict[str, Any] = json.loads(valid)
    parsed["operation"] = "analysis"
    invalid = json.dumps(
        parsed,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()

    with pytest.raises(ValueError, match="invalid internal response envelope"):
        response_status_from_json_bytes(invalid)


def test_response_status_reader_accepts_all_complete_internal_envelope_variants(
    calculated_bazi_chart: BaziChart,
) -> None:
    analysis_mapping = _valid_analysis_mapping(calculated_bazi_chart)
    report_mapping = _valid_report_mapping(calculated_bazi_chart)
    responses = (
        _ok_response(
            result=ApplicationAnalysisResultV1(
                analysis_mapping["result"]["chart"],
                analysis_mapping["result"]["calculation"],
            ),
            provenance=_provenance(
                engine_version=analysis_mapping["result"]["calculation"][
                    "engine_version"
                ],
                ruleset_version=analysis_mapping["result"]["calculation"][
                    "ruleset_version"
                ],
            ),
        ),
        _ok_response(
            operation="report",
            result=ApplicationReportResultV1(
                report_mapping["result"]["report"],
                None,
            ),
        ),
        _ok_response(
            operation="report",
            result=ApplicationReportResultV1(
                None,
                ApplicationContentV1("text/html", "<p>Report</p>", False),
            ),
        ),
        _ok_response(
            operation="report",
            result=ApplicationReportResultV1(
                None,
                ApplicationContentV1("text/html", "<p>Report</p>", True),
            ),
            privacy=ApplicationPrivacyV1("not_stored_by_engine", True),
        ),
        _non_ok_response(
            operation=None,
            status="error",
            safety=_safety("not_evaluated"),
            code="invalid_json",
        ),
        _non_ok_response(
            operation="analysis",
            status="refused",
            safety=_safety(
                "authorization_required",
                categories=("authorization",),
                redirect_message=(
                    "Provide a true self-use or authorized-other attestation."
                ),
            ),
            code="authorization_required",
        ),
        _non_ok_response(
            operation="report",
            status="refused",
            safety=_safety(
                "unsafe_request",
                categories=("professional_advice",),
                redirect_message="Use a qualified professional.",
                requires_narrowing=True,
            ),
            code="unsafe_request",
        ),
        _non_ok_response(
            operation="analysis",
            status="error",
            safety=_safety("error"),
            code="internal_error",
        ),
    )

    for response in responses:
        payload = serialize_response(response)
        assert response_status_from_json_bytes(payload) == response.status


@pytest.mark.parametrize(
    "invalid_trace_id",
    [
        "not-a-uuid",
        "00000000-0000-0000-0000-000000000000",
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "550E8400-E29B-41D4-A716-446655440000",
        "{550e8400-e29b-41d4-a716-446655440000}",
    ],
)
def test_response_status_reader_rejects_noncanonical_non_v4_trace_ids(
    calculated_bazi_chart: BaziChart,
    invalid_trace_id: str,
) -> None:
    payload = _valid_analysis_mapping(calculated_bazi_chart)
    payload["trace_id"] = invalid_trace_id

    with pytest.raises(ValueError, match="invalid internal response envelope"):
        response_status_from_json_bytes(_canonical_bytes(payload))


@pytest.mark.parametrize(
    "invalid_trace_id",
    ["not-a-uuid", "6ba7b810-9dad-11d1-80b4-00c04fd430c8"],
)
def test_response_status_reader_rejects_invalid_error_trace_uuid_even_when_matching(
    invalid_trace_id: str,
) -> None:
    payload = serialize_response_mapping(
        _non_ok_response(
            operation=None,
            status="error",
            safety=_safety("not_evaluated"),
            code="invalid_json",
        )
    )
    payload["trace_id"] = invalid_trace_id
    payload["error"]["trace_id"] = invalid_trace_id

    with pytest.raises(ValueError, match="invalid internal response envelope"):
        response_status_from_json_bytes(_canonical_bytes(payload))


def test_response_status_reader_rejects_empty_missing_and_extra_public_structures(
    calculated_bazi_chart: BaziChart,
) -> None:
    analysis = _valid_analysis_mapping(calculated_bazi_chart)
    report = _valid_report_mapping(calculated_bazi_chart)
    cases = (
        ("empty-chart", analysis, ("result", "chart"), "empty", ""),
        ("missing-chart", analysis, ("result", "chart"), "missing", "day_master"),
        ("extra-chart", analysis, ("result", "chart"), "extra", "private"),
        (
            "empty-calculation",
            analysis,
            ("result", "calculation"),
            "empty",
            "",
        ),
        (
            "missing-calculation",
            analysis,
            ("result", "calculation"),
            "missing",
            "facts",
        ),
        (
            "extra-calculation",
            analysis,
            ("result", "calculation"),
            "extra",
            "private",
        ),
        ("empty-report", report, ("result", "report"), "empty", ""),
        ("missing-report", report, ("result", "report"), "missing", "title"),
        ("extra-report", report, ("result", "report"), "extra", "private"),
    )

    for _case_id, source, path, mutation, key in cases:
        payload = deepcopy(source)
        target = _mapping_at(payload, path)
        if mutation == "empty":
            target.clear()
        elif mutation == "missing":
            target.pop(key)
        else:
            target[key] = "INTERNAL_PRIVATE_VALUE"

        with pytest.raises(ValueError, match="invalid internal response envelope"):
            response_status_from_json_bytes(_canonical_bytes(payload))


def test_response_status_reader_recursively_validates_public_result_structures(
    calculated_bazi_chart: BaziChart,
) -> None:
    analysis = _valid_analysis_mapping(calculated_bazi_chart)
    report = _valid_report_mapping(calculated_bazi_chart)
    cases = (
        (analysis, ("result", "chart", "chart_source"), "source_type"),
        (analysis, ("result", "chart", "pillars", 0), "gan_zhi"),
        (analysis, ("result", "calculation", "facts"), "day_master"),
        (
            analysis,
            ("result", "calculation", "facts", "exposed_stems", 0),
            "ten_god",
        ),
        (
            analysis,
            ("result", "calculation", "strength", "reasoning"),
            "status",
        ),
        (report, ("result", "report", "report_evidence_audit"), "audit_status"),
        (report, ("result", "report", "knowledge_activation"), "activation_status"),
        (report, ("result", "report", "safety_review"), "allowed"),
        (
            report,
            (
                "result",
                "report",
                "expanded_evidence",
                "formal_conclusions",
                0,
                "trace",
            ),
            "trace_id",
        ),
    )

    for source, path, key in cases:
        missing = deepcopy(source)
        _mapping_at(missing, path).pop(key)
        extra = deepcopy(source)
        _mapping_at(extra, path)["private"] = "INTERNAL_PRIVATE_VALUE"

        for payload in (missing, extra):
            with pytest.raises(
                ValueError,
                match="invalid internal response envelope",
            ):
                response_status_from_json_bytes(_canonical_bytes(payload))


def test_response_status_reader_rejects_public_result_value_type_mismatches(
    calculated_bazi_chart: BaziChart,
) -> None:
    analysis = _valid_analysis_mapping(calculated_bazi_chart)
    report = _valid_report_mapping(calculated_bazi_chart)
    cases: tuple[
        tuple[dict[str, Any], tuple[object, ...], str, object], ...
    ] = (
        (analysis, ("result", "chart"), "day_master", 1),
        (analysis, ("result", "chart", "chart_source"), "confidence", False),
        (analysis, ("result", "calculation"), "engine_version", []),
        (analysis, ("result", "calculation", "strength"), "score", "high"),
        (report, ("result", "report"), "title", []),
        (report, ("result", "report", "safety_review"), "allowed", 1),
    )

    for source, path, key, invalid_value in cases:
        payload = deepcopy(source)
        _mapping_at(payload, path)[key] = invalid_value

        with pytest.raises(ValueError, match="invalid internal response envelope"):
            response_status_from_json_bytes(_canonical_bytes(payload))


def test_response_status_reader_rejects_operation_result_schema_mismatches(
    calculated_bazi_chart: BaziChart,
) -> None:
    analysis = _valid_analysis_mapping(calculated_bazi_chart)
    report = _valid_report_mapping(calculated_bazi_chart)
    analysis["result"] = report["result"]
    report["result"] = _valid_analysis_mapping(calculated_bazi_chart)["result"]

    for payload in (analysis, report):
        with pytest.raises(ValueError, match="invalid internal response envelope"):
            response_status_from_json_bytes(_canonical_bytes(payload))


def test_response_status_reader_rejects_nested_envelope_key_and_type_anomalies(
    calculated_bazi_chart: BaziChart,
) -> None:
    success = _valid_analysis_mapping(calculated_bazi_chart)
    failure = serialize_response_mapping(
        _non_ok_response(
            operation=None,
            status="error",
            safety=_safety("not_evaluated"),
            code="invalid_json",
        )
    )
    cases = (
        (success, ("provenance",), "engine_version", 1),
        (success, ("provenance",), "private", "extra"),
        (success, ("safety",), "allowed", 1),
        (success, ("safety",), "private", "extra"),
        (success, ("privacy",), "contains_sensitive_profile", 0),
        (success, ("privacy",), "private", "extra"),
        (success, ("warnings", 0), "code", False),
        (success, ("warnings", 0), "private", "extra"),
        (failure, ("error",), "retryable", 0),
        (failure, ("error",), "private", "extra"),
    )

    for source, path, key, invalid_value in cases:
        payload = deepcopy(source)
        _mapping_at(payload, path)[key] = invalid_value

        with pytest.raises(ValueError, match="invalid internal response envelope"):
            response_status_from_json_bytes(_canonical_bytes(payload))


def test_response_serializer_rejects_incomplete_internal_result_mapping() -> None:
    with pytest.raises(ValueError, match="invalid internal response envelope"):
        serialize_response(_ok_response())


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("calculation_status", "partially_computed"),
        ("calculation_confidence", "certain"),
    ],
)
def test_response_status_reader_rejects_invalid_evidence_trace_enums_without_leak(
    calculated_bazi_chart: BaziChart,
    field_name: str,
    invalid_value: str,
) -> None:
    payload = _valid_report_mapping(calculated_bazi_chart)
    trace = _mapping_at(
        payload,
        (
            "result",
            "report",
            "expanded_evidence",
            "formal_conclusions",
            0,
            "trace",
        ),
    )
    trace[field_name] = invalid_value

    with pytest.raises(ValueError) as captured:
        response_status_from_json_bytes(_canonical_bytes(payload))

    assert str(captured.value) == "invalid internal response envelope"
    assert invalid_value not in str(captured.value)


@pytest.mark.parametrize(
    ("field_name", "allowed_values"),
    [
        ("calculation_status", CALCULATION_STATUSES),
        ("calculation_confidence", CALCULATION_CONFIDENCES),
    ],
)
def test_response_status_reader_accepts_every_evidence_trace_enum_value(
    calculated_bazi_chart: BaziChart,
    field_name: str,
    allowed_values: frozenset[str],
) -> None:
    for allowed_value in allowed_values:
        payload = _valid_report_mapping(calculated_bazi_chart)
        trace = _mapping_at(
            payload,
            (
                "result",
                "report",
                "expanded_evidence",
                "formal_conclusions",
                0,
                "trace",
            ),
        )
        trace[field_name] = allowed_value

        assert response_status_from_json_bytes(_canonical_bytes(payload)) == "ok"


def test_response_status_reader_rejects_ok_json_report_with_blocked_safety(
    calculated_bazi_chart: BaziChart,
) -> None:
    payload = _valid_report_mapping(calculated_bazi_chart)
    report_safety = _mapping_at(payload, ("result", "report", "safety_review"))
    report_safety["allowed"] = False

    with pytest.raises(ValueError, match="invalid internal response envelope"):
        response_status_from_json_bytes(_canonical_bytes(payload))


@pytest.mark.parametrize(
    ("content_sensitive", "privacy_sensitive"),
    [(True, False), (False, True)],
)
def test_response_status_reader_requires_content_and_privacy_sensitivity_match(
    content_sensitive: bool,
    privacy_sensitive: bool,
) -> None:
    response = _ok_response(
        operation="report",
        result=ApplicationReportResultV1(
            None,
            ApplicationContentV1(
                "text/html",
                "<p>Report</p>",
                content_sensitive,
            ),
        ),
    )
    payload = serialize_response_mapping(response)
    payload["privacy"]["contains_sensitive_profile"] = privacy_sensitive

    with pytest.raises(ValueError, match="invalid internal response envelope"):
        response_status_from_json_bytes(_canonical_bytes(payload))


def test_response_status_reader_rejects_sensitive_analysis_success(
    calculated_bazi_chart: BaziChart,
) -> None:
    payload = _valid_analysis_mapping(calculated_bazi_chart)
    payload["privacy"]["contains_sensitive_profile"] = True

    with pytest.raises(ValueError, match="invalid internal response envelope"):
        response_status_from_json_bytes(_canonical_bytes(payload))


@pytest.mark.parametrize("version_field", ["engine_version", "ruleset_version"])
def test_response_status_reader_requires_analysis_provenance_version_match(
    calculated_bazi_chart: BaziChart,
    version_field: str,
) -> None:
    payload = _valid_analysis_mapping(calculated_bazi_chart)
    payload["provenance"][version_field] = "mismatched-version"

    with pytest.raises(ValueError, match="invalid internal response envelope"):
        response_status_from_json_bytes(_canonical_bytes(payload))
