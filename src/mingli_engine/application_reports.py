from dataclasses import fields, is_dataclass, replace
import unicodedata
from typing import Any, cast

from mingli_engine.bazi.result_models import CalculationBundle
from mingli_engine.classical_sources import load_approved_evidence_units
from mingli_engine.models import BaziChart, BirthProfile, Report, SafetyReviewResult
from mingli_engine.report_schema import build_report


PROHIBITED_ABSOLUTE_PHRASES = (
    "必定",
    "注定",
    "一定会",
    "死定",
    "guaranteed",
    "destined",
    "will definitely",
)
_REDACTION_MARKER = "[profile redacted]"
_TRADITIONAL_DISCLAIMER_MARKER = "传统命理知识"
_PROFESSIONAL_BOUNDARY_MARKER = "不替代医疗、法律、心理、投资等专业建议"
_UNSAFE_REPORT_REDIRECT = (
    "Revise the report to conditional, non-absolute language before rendering."
)


def _traceability_lines() -> list[str]:
    return [
        (
            f"source_id={unit.source_id}; source_locator={unit.source_ref}; "
            f"evidence_id={unit.evidence_id}; rule_family={unit.rule_family}"
        )
        for unit in sorted(
            load_approved_evidence_units(),
            key=lambda item: item.evidence_id,
        )
    ]


def build_application_report(
    chart: BaziChart,
    calculation: CalculationBundle,
) -> Report:
    """Build the full bound report and add stable source traceability."""
    report = build_report(chart, calculation)
    traceability = _traceability_lines()
    expanded = replace(
        report.expanded_evidence,
        source_summary=traceability,
    )
    evidence_notes = "\n".join([report.evidence_notes, *traceability])
    return replace(
        report,
        evidence_notes=evidence_notes,
        expanded_evidence=expanded,
    )


def _walk_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for key, item in value.items():
            strings.extend(_walk_strings(key))
            strings.extend(_walk_strings(item))
        return strings
    if isinstance(value, (list, tuple)):
        strings = []
        for item in value:
            strings.extend(_walk_strings(item))
        return strings
    if is_dataclass(value) and not isinstance(value, type):
        strings = []
        for field in fields(value):
            strings.extend(_walk_strings(getattr(value, field.name)))
        return strings
    return []


def review_built_report(report: Report) -> SafetyReviewResult:
    """Review the complete report before any redaction or renderer call."""
    text = "\n".join(_walk_strings(report))
    folded = text.casefold()
    absolute_phrases = [
        phrase
        for phrase in PROHIBITED_ABSOLUTE_PHRASES
        if phrase.casefold() in folded
    ]
    categories = list(report.safety_review.red_line_categories)
    prohibited = list(report.safety_review.prohibited_phrases)
    redirect_messages = [report.safety_review.redirect_message]

    if absolute_phrases:
        if "absolute_destiny" not in categories:
            categories.append("absolute_destiny")
        for phrase in absolute_phrases:
            if phrase not in prohibited:
                prohibited.append(phrase)
        redirect_messages.append(_UNSAFE_REPORT_REDIRECT)

    if _TRADITIONAL_DISCLAIMER_MARKER not in text:
        categories.append("missing_traditional_analysis_disclaimer")
    if _PROFESSIONAL_BOUNDARY_MARKER not in text:
        categories.append("missing_professional_boundary")

    normalized_categories = list(dict.fromkeys(categories))
    normalized_redirects = list(
        dict.fromkeys(message for message in redirect_messages if message)
    )
    return SafetyReviewResult(
        allowed=(
            report.safety_review.allowed
            and not normalized_categories
            and not prohibited
        ),
        red_line_categories=normalized_categories,
        prohibited_phrases=prohibited,
        disclaimer_present=report.safety_review.disclaimer_present,
        redirect_message="\n".join(normalized_redirects),
    )


def _profile_replacements(profile: BirthProfile) -> tuple[str, ...]:
    values = (
        profile.calendar_type,
        profile.birth_date,
        profile.birth_time,
        profile.birthplace,
        profile.gender,
        profile.focus_topic,
    )
    replacements = {
        candidate
        for value in values
        for candidate in (value, unicodedata.normalize("NFKC", value))
        if candidate
    }
    return tuple(sorted(replacements, key=lambda item: (-len(item), item)))


def _redact_value(value: Any, replacements: tuple[str, ...]) -> Any:
    if isinstance(value, str):
        redacted = value
        for sensitive in replacements:
            redacted = redacted.replace(sensitive, _REDACTION_MARKER)
        return redacted
    if isinstance(value, list):
        return [_redact_value(item, replacements) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_value(item, replacements) for item in value)
    if isinstance(value, dict):
        return {
            key: _redact_value(item, replacements)
            for key, item in value.items()
        }
    if is_dataclass(value) and not isinstance(value, type):
        updates = {
            field.name: _redact_value(getattr(value, field.name), replacements)
            for field in fields(value)
        }
        return replace(value, **updates)
    return value


def redact_report(report: Report, profile: BirthProfile) -> Report:
    """Redact every explicit and nested report value using raw and NFKC forms."""
    return cast(Report, _redact_value(report, _profile_replacements(profile)))
