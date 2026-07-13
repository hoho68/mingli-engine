from datetime import datetime
from importlib.metadata import version
import unicodedata
from uuid import uuid4

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
    RealUseRequestV1,
    RealUseResponseV1,
)
from mingli_engine.application_serialization import (
    serialize_calculation_bundle,
    serialize_chart,
    serialize_report,
)
from mingli_engine.application_reports import (
    build_application_report,
    redact_report,
    review_built_report,
)
from mingli_engine.bazi import analyze_bazi_chart, validate_calculation_binding
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.classical_sources import load_approved_evidence_units
from mingli_engine.high_risk import classify_high_risk_request
from mingli_engine.html import render_html_report
from mingli_engine.markdown import render_markdown_report
from mingli_engine.models import BirthProfile
from mingli_engine.safety import safety_check


_AUTHORIZATION_REDIRECT = (
    "Provide a true self-use or authorized-other attestation."
)
_PROFESSIONAL_ADVICE_REDIRECT = (
    "不提供替代个人判断的职业、医疗、法律、心理或投资专业建议；"
    "相关决定请咨询合格专业人士。"
)
_ANXIETY_CREATION_REDIRECT = (
    "不使用命理内容制造焦虑、恐吓或迫使他人服从；"
    "可以改为保留自主选择与不确定性的条件化讨论。"
)
_COERCIVE_MATCHING_REDIRECT = (
    "不使用命理结论强制婚配或迫使他人作出关系决定；"
    "可以改为讨论双方自愿确认的沟通与现实条件。"
)
_ABSOLUTE_LANGUAGE_REDIRECT = (
    "Use conditional, non-absolute language that preserves uncertainty and user agency."
)
_UNSAFE_FOCUS_REDIRECT = (
    "Narrow the request to non-predictive traditional analysis that preserves user agency."
)
_EVIDENCE_BASELINE_ID = "report_acceptance_v1"
_PROVIDER_DISTRIBUTION = "lunar-python"
_SAFE_CONTEXT_MARKERS = (
    "不预测",
    "不看",
    "不算",
    "不做",
    "不提供",
    "不输出",
    "不保证",
    "不承诺",
    "不要",
    "避免",
    "禁止",
    "并非",
    "不是",
)
_ADDITIONAL_FOCUS_RULES = (
    (
        "professional_advice",
        (
            "职业建议",
            "职业决策",
            "替我选职业",
            "替我决定职业",
            "替我决定工作",
            "金融建议",
            "财务建议",
            "理财建议",
            "career advice",
        ),
        _PROFESSIONAL_ADVICE_REDIRECT,
    ),
    (
        "deterministic_marriage_matching",
        (
            "强制匹配",
            "强迫结婚",
            "迫使对方结婚",
            "逼对方结婚",
        ),
        _COERCIVE_MATCHING_REDIRECT,
    ),
    (
        "anxiety_creation",
        (
            "制造焦虑",
            "引发焦虑",
            "散播焦虑",
            "恐吓",
            "吓唬",
            "迫使对方服从",
        ),
        _ANXIETY_CREATION_REDIRECT,
    ),
)


def _privacy(*, contains_sensitive_profile: bool = False) -> ApplicationPrivacyV1:
    return ApplicationPrivacyV1(
        retention="not_stored_by_engine",
        contains_sensitive_profile=contains_sensitive_profile,
    )


def _error(
    *,
    code: ApplicationErrorCode,
    message: str,
    field_path: str | None,
    trace_id: str,
) -> ApplicationErrorV1:
    return ApplicationErrorV1(
        code=code,
        message=message,
        field_path=field_path,
        retryable=False,
        trace_id=trace_id,
    )


def _authorization_refusal(
    request: RealUseRequestV1,
    trace_id: str,
) -> RealUseResponseV1:
    return RealUseResponseV1(
        schema_version=REAL_USE_RESPONSE_SCHEMA_VERSION,
        trace_id=trace_id,
        operation=request.operation,
        status="refused",
        result=None,
        safety=ApplicationSafetyV1(
            allowed=False,
            decision="authorization_required",
            categories=("authorization",),
            redirect_message=_AUTHORIZATION_REDIRECT,
            requires_narrowing=False,
        ),
        provenance=None,
        warnings=(),
        privacy=_privacy(),
        error=_error(
            code="authorization_required",
            message="Authorization is required.",
            field_path="$.authorization.attested",
            trace_id=trace_id,
        ),
    )


def _normalized_categories(categories: list[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for category in categories:
        value = unicodedata.normalize("NFKC", category).strip()
        if value and value not in normalized:
            normalized.append(value)
    return tuple(normalized)


def _unsafe_refusal(
    request: RealUseRequestV1,
    trace_id: str,
    *,
    categories: list[str],
    redirect_message: str,
) -> RealUseResponseV1:
    normalized_categories = _normalized_categories(categories)
    if not normalized_categories:
        normalized_categories = ("high_risk_request",)
    safe_redirect = redirect_message.strip() or _UNSAFE_FOCUS_REDIRECT
    return RealUseResponseV1(
        schema_version=REAL_USE_RESPONSE_SCHEMA_VERSION,
        trace_id=trace_id,
        operation=request.operation,
        status="refused",
        result=None,
        safety=ApplicationSafetyV1(
            allowed=False,
            decision="unsafe_request",
            categories=normalized_categories,
            redirect_message=safe_redirect,
            # The V1 refusal matrix requires narrowing even when the classifier's
            # direct-refusal result uses False for its own internal semantics.
            requires_narrowing=True,
        ),
        provenance=None,
        warnings=(),
        privacy=_privacy(),
        error=_error(
            code="unsafe_request",
            message="Request cannot be processed safely.",
            field_path="$.profile.focus_topic",
            trace_id=trace_id,
        ),
    )


def _internal_error(
    request: RealUseRequestV1,
    trace_id: str,
) -> RealUseResponseV1:
    return RealUseResponseV1(
        schema_version=REAL_USE_RESPONSE_SCHEMA_VERSION,
        trace_id=trace_id,
        operation=request.operation,
        status="error",
        result=None,
        safety=ApplicationSafetyV1(False, "error", (), "", False),
        provenance=None,
        warnings=(),
        privacy=_privacy(),
        error=_error(
            code="internal_error",
            message="Request processing failed.",
            field_path=None,
            trace_id=trace_id,
        ),
    )


def _has_unsafe_pattern(text: str, patterns: tuple[str, ...]) -> bool:
    folded_text = text.casefold()
    for pattern in patterns:
        folded_pattern = pattern.casefold()
        start = folded_text.find(folded_pattern)
        while start != -1:
            context_start = max(0, start - 10)
            context_end = min(len(text), start + len(pattern) + 12)
            context = text[context_start:context_end]
            if not any(marker in context for marker in _SAFE_CONTEXT_MARKERS):
                return True
            start = folded_text.find(folded_pattern, start + len(folded_pattern))
    return False


def _additional_focus_refusal(text: str) -> tuple[str, str] | None:
    for category, patterns, redirect_message in _ADDITIONAL_FOCUS_RULES:
        if _has_unsafe_pattern(text, patterns):
            return category, redirect_message
    return None


def _execute_authorized_request(
    request: RealUseRequestV1,
    trace_id: str,
) -> RealUseResponseV1:
    profile = BirthProfile(
        calendar_type=request.profile.calendar_type,
        birth_date=request.profile.birth_date,
        birth_time=request.profile.birth_time,
        birthplace=request.profile.birthplace,
        gender=request.profile.gender,
        focus_topic=request.profile.focus_topic,
    )
    birth_datetime = datetime.fromisoformat(
        f"{profile.birth_date}T{profile.birth_time}"
    )
    chart = calculate_bazi_chart(profile)
    calculation = analyze_bazi_chart(
        chart,
        birth_datetime=birth_datetime,
    )
    validate_calculation_binding(chart, calculation)
    evidence_ids = tuple(
        sorted(unit.evidence_id for unit in load_approved_evidence_units())
    )
    provenance = ApplicationProvenanceV1(
        engine_version=calculation.engine_version,
        ruleset_version=calculation.ruleset_version,
        provider_version=(
            f"{_PROVIDER_DISTRIBUTION}-{version(_PROVIDER_DISTRIBUTION)}"
        ),
        chart_source_type="calculated",
        chart_source_confidence="deterministic_supported_range",
        evidence_baseline_id=_EVIDENCE_BASELINE_ID,
        evidence_ids=evidence_ids,
    )

    if request.operation == "analysis":
        result = ApplicationAnalysisResultV1(
            chart=serialize_chart(chart),
            calculation=serialize_calculation_bundle(calculation),
        )
        privacy = _privacy()
    else:
        full_report = build_application_report(chart, calculation)
        post_build_review = review_built_report(full_report)
        if not post_build_review.allowed:
            categories = list(post_build_review.red_line_categories)
            if post_build_review.prohibited_phrases:
                categories.append("absolute_destiny")
            return _unsafe_refusal(
                request,
                trace_id,
                categories=categories,
                redirect_message=post_build_review.redirect_message,
            )

        include_profile = request.options.include_profile_in_report
        public_report = (
            full_report if include_profile else redact_report(full_report, profile)
        )
        report_format = request.options.report_format
        if report_format == "json":
            result = ApplicationReportResultV1(
                report=serialize_report(public_report),
                content=None,
            )
        elif report_format == "markdown":
            result = ApplicationReportResultV1(
                report=None,
                content=ApplicationContentV1(
                    media_type="text/markdown",
                    content=render_markdown_report(public_report),
                    contains_sensitive_profile=include_profile,
                ),
            )
        elif report_format == "html":
            result = ApplicationReportResultV1(
                report=None,
                content=ApplicationContentV1(
                    media_type="text/html",
                    content=render_html_report(public_report),
                    contains_sensitive_profile=include_profile,
                ),
            )
        else:
            raise ValueError("report operation requires an output format")
        privacy = _privacy(contains_sensitive_profile=include_profile)

    return RealUseResponseV1(
        schema_version=REAL_USE_RESPONSE_SCHEMA_VERSION,
        trace_id=trace_id,
        operation=request.operation,
        status="ok",
        result=result,
        safety=ApplicationSafetyV1(True, "allowed", (), "", False),
        provenance=provenance,
        warnings=(),
        privacy=privacy,
        error=None,
    )


def handle_real_use(request: RealUseRequestV1) -> RealUseResponseV1:
    """Apply authorization and pre-calculation safety to one typed V1 request."""
    trace_id = str(uuid4())
    if not request.authorization.attested:
        return _authorization_refusal(request, trace_id)

    try:
        focus_topic = unicodedata.normalize("NFKC", request.profile.focus_topic)
        high_risk_review = classify_high_risk_request(focus_topic)
        if not high_risk_review.allowed:
            return _unsafe_refusal(
                request,
                trace_id,
                categories=high_risk_review.categories,
                redirect_message=high_risk_review.redirect_message,
            )

        focus_review = safety_check(focus_topic, disclaimer_present=False)
        if not focus_review.allowed:
            categories = [
                *high_risk_review.categories,
                *focus_review.red_line_categories,
            ]
            if focus_review.prohibited_phrases:
                categories.append("absolute_destiny")
            return _unsafe_refusal(
                request,
                trace_id,
                categories=categories,
                redirect_message=(
                    focus_review.redirect_message or _ABSOLUTE_LANGUAGE_REDIRECT
                ),
            )

        additional_refusal = _additional_focus_refusal(focus_topic)
        if additional_refusal is not None:
            category, redirect_message = additional_refusal
            return _unsafe_refusal(
                request,
                trace_id,
                categories=[*high_risk_review.categories, category],
                redirect_message=redirect_message,
            )

        return _execute_authorized_request(request, trace_id)
    except Exception:
        return _internal_error(request, trace_id)
