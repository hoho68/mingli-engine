import unicodedata
from uuid import uuid4

from mingli_engine.application_models import (
    REAL_USE_RESPONSE_SCHEMA_VERSION,
    ApplicationErrorCode,
    ApplicationErrorV1,
    ApplicationPrivacyV1,
    ApplicationSafetyV1,
    RealUseRequestV1,
    RealUseResponseV1,
)
from mingli_engine.high_risk import classify_high_risk_request
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


def _privacy() -> ApplicationPrivacyV1:
    return ApplicationPrivacyV1(
        retention="not_stored_by_engine",
        contains_sensitive_profile=False,
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
    # Task 6 replaces this controlled boundary with same-process calculation.
    return _internal_error(request, trace_id)


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
