from dataclasses import replace
from datetime import datetime
from typing import NoReturn

import pytest

from mingli_engine.application_models import (
    REAL_USE_REQUEST_SCHEMA_VERSION,
    ApplicationReportResultV1,
    AuthorizationAttestationV1,
    RealUseOptionsV1,
    RealUseProfileV1,
    RealUseRequestV1,
)
from mingli_engine.bazi import analyze_bazi_chart
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile, Report
from mingli_engine.report_schema import build_report


ACTIVE_FOCUS = (
    "# hostile heading\n"
    "[focus](https://example.invalid) <script>alert(1)</script> | `code`"
)


def _request(
    report_format: str,
    *,
    focus_topic: str = "traditional structural overview",
    include_profile: bool = False,
) -> RealUseRequestV1:
    return RealUseRequestV1(
        schema_version=REAL_USE_REQUEST_SCHEMA_VERSION,
        request_id="synthetic-rendering-test",
        operation="report",
        profile=RealUseProfileV1(
            calendar_type="gregorian",
            birth_date="1996-12-15",
            birth_time="09:30",
            birthplace="Synthetic UTC+08 Place",
            gender="unknown",
            focus_topic=focus_topic,
        ),
        authorization=AuthorizationAttestationV1("self", True),
        options=RealUseOptionsV1(
            report_format=report_format,  # type: ignore[arg-type]
            include_profile_in_report=include_profile,
        ),
    )


def _safe_report() -> Report:
    profile = BirthProfile(
        calendar_type="gregorian",
        birth_date="1996-12-15",
        birth_time="09:30",
        birthplace="Synthetic UTC+08 Place",
        gender="unknown",
        focus_topic="traditional structural overview",
    )
    chart = calculate_bazi_chart(profile)
    calculation = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1996, 12, 15, 9, 30),
    )
    return build_report(chart, calculation)


@pytest.mark.parametrize("report_format", ["markdown", "html"])
def test_included_profile_active_markup_is_escaped(report_format: str) -> None:
    from mingli_engine.application_service import handle_real_use

    response = handle_real_use(
        _request(
            report_format,
            focus_topic=ACTIVE_FOCUS,
            include_profile=True,
        )
    )

    assert response.status == "ok"
    assert isinstance(response.result, ApplicationReportResultV1)
    assert response.result.content is not None
    rendered = response.result.content.content
    assert response.result.content.contains_sensitive_profile is True
    assert "<script>" not in rendered.lower()
    if report_format == "markdown":
        assert "[focus](https://example.invalid)" not in rendered
        assert "\n# hostile heading" not in rendered
        assert r"\# hostile heading" in rendered
        assert r"\[focus\]\(https://example\.invalid\)" in rendered
        assert r"&lt;script&gt;alert\(1\)&lt;/script&gt;" in rendered
    else:
        assert "href=" not in rendered.lower()
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered


@pytest.mark.parametrize("report_format", ["json", "markdown", "html"])
@pytest.mark.parametrize(
    "prohibited",
    ["必定", "注定", "一定会", "死定", "guaranteed", "will definitely"],
)
def test_post_build_absolute_language_is_refused_before_output(
    monkeypatch: pytest.MonkeyPatch,
    report_format: str,
    prohibited: str,
) -> None:
    import mingli_engine.application_service as service

    unsafe_report = replace(
        _safe_report(),
        integrated_synthesis=f"This conclusion is {prohibited}: {prohibited}",
    )
    calls: list[str] = []

    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        calls.append("output")
        raise AssertionError("unsafe report reached output boundary")

    monkeypatch.setattr(service, "build_application_report", lambda *_args: unsafe_report)
    monkeypatch.setattr(service, "redact_report", forbidden)
    monkeypatch.setattr(service, "serialize_report", forbidden)
    monkeypatch.setattr(service, "render_markdown_report", forbidden)
    monkeypatch.setattr(service, "render_html_report", forbidden)

    response = service.handle_real_use(_request(report_format))

    assert response.status == "refused"
    assert response.result is None
    assert response.provenance is None
    assert response.error is not None
    assert response.error.code == "unsafe_request"
    assert prohibited not in repr(response)
    assert calls == []
