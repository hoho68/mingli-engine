from dataclasses import replace
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import NoReturn
import unicodedata

import pytest

from mingli_engine.application_models import (
    REAL_USE_REQUEST_SCHEMA_VERSION,
    ApplicationContentV1,
    ApplicationReportResultV1,
    AuthorizationAttestationV1,
    RealUseOptionsV1,
    RealUseProfileV1,
    RealUseRequestV1,
)
from mingli_engine.bazi import analyze_bazi_chart
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.classical_sources import load_approved_evidence_units
from mingli_engine.models import BirthProfile, Report
from mingli_engine.report_schema import build_report


PROFILE_VALUES = (
    "gregorian",
    "1996-12-15",
    "09:30",
    "ＦＵＬＬＷＩＤＴＨ-PLACE",
    "ＧＥＮＤＥＲ-MARKER",
    "ＦＯＣＵＳ-METADATA-MARKER",
)
REPORT_BODY_SENTINEL = "PRIVATE-BUILT-REPORT-SENTINEL"


def _request(
    report_format: str,
    *,
    include_profile: bool = False,
    focus_topic: str = PROFILE_VALUES[-1],
) -> RealUseRequestV1:
    return RealUseRequestV1(
        schema_version=REAL_USE_REQUEST_SCHEMA_VERSION,
        request_id="synthetic-report-test",
        operation="report",
        profile=RealUseProfileV1(
            calendar_type=PROFILE_VALUES[0],  # type: ignore[arg-type]
            birth_date=PROFILE_VALUES[1],
            birth_time=PROFILE_VALUES[2],
            birthplace=PROFILE_VALUES[3],
            gender=PROFILE_VALUES[4],
            focus_topic=focus_topic,
        ),
        authorization=AuthorizationAttestationV1("self", True),
        options=RealUseOptionsV1(
            report_format=report_format,  # type: ignore[arg-type]
            include_profile_in_report=include_profile,
        ),
    )


def _profile(request: RealUseRequestV1) -> BirthProfile:
    return BirthProfile(
        calendar_type=request.profile.calendar_type,
        birth_date=request.profile.birth_date,
        birth_time=request.profile.birth_time,
        birthplace=request.profile.birthplace,
        gender=request.profile.gender,
        focus_topic=request.profile.focus_topic,
    )


def _real_report(request: RealUseRequestV1) -> Report:
    profile = _profile(request)
    chart = calculate_bazi_chart(profile)
    calculation = analyze_bazi_chart(
        chart,
        birth_datetime=datetime.fromisoformat(
            f"{profile.birth_date}T{profile.birth_time}"
        ),
    )
    return build_report(chart, calculation)


def _response_text(response: object) -> str:
    result = getattr(response, "result")
    assert isinstance(result, ApplicationReportResultV1)
    if result.report is not None:
        return json.dumps(result.report, ensure_ascii=False, sort_keys=True)
    assert isinstance(result.content, ApplicationContentV1)
    return result.content.content


@pytest.mark.parametrize("report_format", ["json", "markdown", "html"])
def test_real_use_report_succeeds_in_all_formats(report_format: str) -> None:
    from mingli_engine.application_service import handle_real_use

    response = handle_real_use(_request(report_format))

    assert response.status == "ok"
    assert response.operation == "report"
    assert isinstance(response.result, ApplicationReportResultV1)
    assert response.provenance is not None
    assert response.error is None
    assert response.safety.allowed is True
    assert response.privacy.contains_sensitive_profile is False
    if report_format == "json":
        assert response.result.report is not None
        assert response.result.content is None
    else:
        assert response.result.report is None
        assert response.result.content is not None
        expected_media = "text/markdown" if report_format == "markdown" else "text/html"
        assert response.result.content.media_type == expected_media
        assert response.result.content.contains_sensitive_profile is False
    assert len(_response_text(response).encode("utf-8")) < 1024 * 1024


def test_profile_exclusion_redacts_raw_and_nfkc_values_from_nested_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import mingli_engine.application_service as service

    original_build = service.build_application_report

    def build_with_nested_markers(chart: object, calculation: object) -> Report:
        report = original_build(chart, calculation)
        conclusion = report.expanded_evidence.formal_conclusions[0]
        trace = replace(
            conclusion.trace,
            assumptions=[
                *conclusion.trace.assumptions,
                PROFILE_VALUES[-1],
                unicodedata.normalize("NFKC", PROFILE_VALUES[-1]),
            ],
        )
        expanded = replace(
            report.expanded_evidence,
            formal_conclusions=[
                replace(conclusion, trace=trace),
                *report.expanded_evidence.formal_conclusions[1:],
            ],
        )
        activation = replace(
            report.knowledge_activation,
            next_action=PROFILE_VALUES[-1],
        )
        return replace(
            report,
            expanded_evidence=expanded,
            knowledge_activation=activation,
        )

    monkeypatch.setattr(service, "build_application_report", build_with_nested_markers)

    response = service.handle_real_use(_request("json", include_profile=False))
    serialized = _response_text(response)

    assert response.status == "ok"
    for value in PROFILE_VALUES:
        assert value not in serialized
        assert unicodedata.normalize("NFKC", value) not in serialized


@pytest.mark.parametrize("report_format", ["json", "markdown", "html"])
def test_profile_inclusion_marks_sensitive_and_contains_only_profile_fields(
    report_format: str,
) -> None:
    from mingli_engine.application_service import handle_real_use

    response = handle_real_use(
        _request(report_format, include_profile=True)
    )
    rendered = _response_text(response)
    comparable = rendered.replace("\\", "") if report_format == "markdown" else rendered

    assert response.status == "ok"
    assert response.privacy.contains_sensitive_profile is True
    assert PROFILE_VALUES[1] in comparable
    assert PROFILE_VALUES[2] in comparable
    assert PROFILE_VALUES[3] in comparable
    assert PROFILE_VALUES[-1] in comparable
    assert "synthetic-report-test" not in comparable
    assert "attested" not in comparable
    assert "authorization" not in comparable
    if response.result is not None and response.result.content is not None:
        assert response.result.content.contains_sensitive_profile is True


@pytest.mark.parametrize("report_format", ["json", "markdown", "html"])
def test_report_preserves_source_evidence_rule_and_school_traceability(
    report_format: str,
) -> None:
    from mingli_engine.application_service import handle_real_use

    response = handle_real_use(_request(report_format))
    rendered = _response_text(response)
    comparable = rendered.replace("\\", "") if report_format == "markdown" else rendered
    evidence = load_approved_evidence_units()[0]

    assert evidence.source_id in comparable
    assert evidence.source_ref in comparable
    assert evidence.evidence_id in comparable
    assert "rule" in comparable.lower()
    assert "传统命理知识" in comparable
    assert "不替代医疗、法律、心理、投资等专业建议" in comparable
    assert any(marker in comparable for marker in ("可能", "候选", "条件", "若"))
    assert any(marker in comparable for marker in ("不确定", "可信度", "保留"))
    assert any(marker in comparable for marker in ("流派", "school_view"))


def test_report_order_is_build_then_review_then_redact_then_serialize(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import mingli_engine.application_service as service

    events: list[str] = []
    original_build = service.build_application_report
    original_review = service.review_built_report
    original_redact = service.redact_report
    original_serialize = service.serialize_report

    def build(chart: object, calculation: object) -> Report:
        events.append("build")
        return original_build(chart, calculation)

    def review(report: Report):
        events.append("post_build_review")
        return original_review(report)

    def redact(report: Report, profile: BirthProfile) -> Report:
        events.append("redact")
        return original_redact(report, profile)

    def serialize(report: Report):
        events.append("serialize")
        return original_serialize(report)

    monkeypatch.setattr(service, "build_application_report", build)
    monkeypatch.setattr(service, "review_built_report", review)
    monkeypatch.setattr(service, "redact_report", redact)
    monkeypatch.setattr(service, "serialize_report", serialize)

    response = service.handle_real_use(_request("json"))

    assert response.status == "ok"
    assert events == ["build", "post_build_review", "redact", "serialize"]


def test_post_build_refusal_precedes_redaction_and_every_renderer(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import mingli_engine.application_service as service

    unsafe = replace(
        _real_report(_request("json")),
        formal_synthesis=f"{REPORT_BODY_SENTINEL} 这个结果必定发生。",
    )

    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("post-build refusal reached redaction or rendering")

    monkeypatch.setattr(service, "build_application_report", lambda *_args: unsafe)
    monkeypatch.setattr(service, "redact_report", forbidden)
    monkeypatch.setattr(service, "serialize_report", forbidden)
    monkeypatch.setattr(service, "render_markdown_report", forbidden)
    monkeypatch.setattr(service, "render_html_report", forbidden)
    for method in ("write_text", "write_bytes", "touch", "mkdir"):
        monkeypatch.setattr(Path, method, forbidden)
    caplog.set_level(logging.DEBUG)

    response = service.handle_real_use(_request("json"))

    captured = capsys.readouterr()
    assert response.status == "refused"
    assert response.error is not None
    assert response.error.code == "unsafe_request"
    assert response.provenance is None
    assert REPORT_BODY_SENTINEL not in repr(response)
    assert caplog.records == []
    assert captured.out == ""
    assert captured.err == ""


def test_renderer_exception_is_controlled_without_report_or_profile_leak(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import mingli_engine.application_service as service

    def explode(_report: Report) -> NoReturn:
        raise RuntimeError(f"renderer failed: {REPORT_BODY_SENTINEL} {PROFILE_VALUES[-1]}")

    monkeypatch.setattr(service, "render_markdown_report", explode)
    caplog.set_level(logging.DEBUG)

    response = service.handle_real_use(_request("markdown"))

    captured = capsys.readouterr()
    assert response.status == "error"
    assert response.result is None
    assert response.provenance is None
    assert response.error is not None
    assert response.error.code == "internal_error"
    assert REPORT_BODY_SENTINEL not in repr(response)
    assert PROFILE_VALUES[-1] not in repr(response)
    assert caplog.records == []
    assert captured.out == ""
    assert captured.err == ""
