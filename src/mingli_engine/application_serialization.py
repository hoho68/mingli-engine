import json
from collections.abc import Callable
from typing import Any, NoReturn, TypeVar, cast
from uuid import UUID

from mingli_engine.application_models import (
    ApplicationAnalysisResultV1,
    ApplicationContentV1,
    ApplicationErrorV1,
    ApplicationPrivacyV1,
    ApplicationProvenanceV1,
    ApplicationReportResultV1,
    ApplicationResultV1,
    ApplicationSafetyV1,
    ApplicationWarningV1,
    RealUseResponseV1,
    ResponseStatus,
)
from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    CalculationBundle,
    ReasonedResult,
    StrengthContribution,
)
from mingli_engine.models import (
    CALCULATION_CONFIDENCES,
    CALCULATION_STATUSES,
    ActionReflectionItem,
    BaziChart,
    EvidenceTrace,
    ExpandedReportEvidence,
    FormalConclusion,
    KnowledgeActivationSummary,
    Report,
    ReportEvidenceAudit,
    SafetyReviewResult,
)
from mingli_engine.public_assumptions import project_public_assumptions


MAX_RESPONSE_BYTES = 1024 * 1024

JsonObject = dict[str, Any]
T = TypeVar("T")


class ResponseSizeError(ValueError):
    pass


def serialize_chart(chart: BaziChart) -> JsonObject:
    payload = {
        "chart_source": {
            "source_type": chart.chart_source.source_type,
            "source_note": chart.chart_source.source_note,
            "calendar_assumption": chart.chart_source.calendar_assumption,
            "timezone_assumption": chart.chart_source.timezone_assumption,
            "solar_terms_assumption": chart.chart_source.solar_terms_assumption,
            "true_solar_time_applied": chart.chart_source.true_solar_time_applied,
            "confidence": chart.chart_source.confidence,
        },
        "pillars": [
            {
                "name": pillar.name,
                "heavenly_stem": pillar.heavenly_stem,
                "earthly_branch": pillar.earthly_branch,
                "gan_zhi": pillar.heavenly_stem + pillar.earthly_branch,
                "hidden_stems": list(pillar.hidden_stems),
                "ten_god": pillar.ten_god,
                "element": pillar.element,
            }
            for pillar in chart.pillars
        ],
        "day_master": chart.day_master,
        "five_elements_summary": dict(chart.five_elements_summary),
        "ten_gods_summary": chart.ten_gods_summary,
        "strength_assessment": chart.strength_assessment,
        "pattern_candidates": list(chart.pattern_candidates),
        "useful_god_candidates": list(chart.useful_god_candidates),
        "luck_cycle_summary": chart.luck_cycle_summary,
    }
    return _validate_chart_mapping(payload)


def serialize_reasoned_result(reasoning: ReasonedResult) -> JsonObject:
    return {
        "status": reasoning.status,
        "conclusion": reasoning.conclusion,
        "confidence": reasoning.confidence,
        "supporting_signals": list(reasoning.supporting_signals),
        "opposing_signals": list(reasoning.opposing_signals),
        "assumptions": project_public_assumptions(reasoning.assumptions),
        "missing_inputs": list(reasoning.missing_inputs),
        "rule_ids": list(reasoning.rule_ids),
    }


def serialize_branch_relation(relation: BranchRelationResult) -> JsonObject:
    return {
        "relation_type": relation.relation_type,
        "branches": list(relation.branches),
        "pillar_names": list(relation.pillar_names),
        "state": relation.state,
        "transformed_element": relation.transformed_element,
        "conditions": list(relation.conditions),
        "blockers": list(relation.blockers),
        "rule_id": relation.rule_id,
    }


def serialize_strength_contribution(
    contribution: StrengthContribution,
) -> JsonObject:
    return {
        "category": contribution.category,
        "signal": contribution.signal,
        "value": contribution.value,
        "rule_id": contribution.rule_id,
    }


def serialize_calculation_bundle(calculation: CalculationBundle) -> JsonObject:
    facts = calculation.facts
    payload = {
        "engine_version": calculation.engine_version,
        "ruleset_version": calculation.ruleset_version,
        "facts": {
            "day_master": facts.day_master,
            "month_branch": facts.month_branch,
            "exposed_stems": [
                {
                    "pillar_name": item.pillar_name,
                    "stem": item.stem,
                    "element": item.element,
                    "polarity": item.polarity,
                    "ten_god": item.ten_god,
                }
                for item in facts.exposed_stems
            ],
            "hidden_stems": [
                {
                    "pillar_name": item.pillar_name,
                    "branch": item.branch,
                    "stem": item.stem,
                    "role": item.role,
                    "element": item.element,
                    "polarity": item.polarity,
                    "ten_god": item.ten_god,
                }
                for item in facts.hidden_stems
            ],
            "roots": [
                {
                    "stem": item.stem,
                    "stem_pillar": item.stem_pillar,
                    "branch": item.branch,
                    "branch_pillar": item.branch_pillar,
                    "role": item.role,
                    "exact_stem_root": item.exact_stem_root,
                }
                for item in facts.roots
            ],
            "twelve_growth_by_pillar": [
                list(item) for item in facts.twelve_growth_by_pillar
            ],
            "assumptions": project_public_assumptions(facts.assumptions),
        },
        "branch_relations": [
            serialize_branch_relation(item) for item in calculation.branch_relations
        ],
        "strength": {
            "reasoning": serialize_reasoned_result(calculation.strength.reasoning),
            "score": calculation.strength.score,
            "lower_bound": calculation.strength.lower_bound,
            "upper_bound": calculation.strength.upper_bound,
            "label": calculation.strength.label,
            "contributions": [
                serialize_strength_contribution(item)
                for item in calculation.strength.contributions
            ],
        },
        "patterns": [
            {
                "pattern_id": item.pattern_id,
                "name": item.name,
                "rank": item.rank,
                "reasoning": serialize_reasoned_result(item.reasoning),
                "formation_conditions": list(item.formation_conditions),
                "damage_conditions": list(item.damage_conditions),
                "rescue_conditions": list(item.rescue_conditions),
            }
            for item in calculation.patterns
        ],
        "useful_gods": [
            {
                "method": item.method,
                "element": item.element,
                "rank": item.rank,
                "reasoning": serialize_reasoned_result(item.reasoning),
            }
            for item in calculation.useful_gods
        ],
        "luck_cycles": {
            "reasoning": serialize_reasoned_result(calculation.luck_cycles.reasoning),
            "forward": calculation.luck_cycles.forward,
            "start_years": calculation.luck_cycles.start_years,
            "start_months": calculation.luck_cycles.start_months,
            "start_days": calculation.luck_cycles.start_days,
            "start_solar": calculation.luck_cycles.start_solar,
            "pillars": [
                {
                    "index": item.index,
                    "gan_zhi": item.gan_zhi,
                    "start_year": item.start_year,
                    "end_year": item.end_year,
                    "start_age": item.start_age,
                    "end_age": item.end_age,
                }
                for item in calculation.luck_cycles.pillars
            ],
            "selected_year_relations": [
                serialize_branch_relation(item)
                for item in calculation.luck_cycles.selected_year_relations
            ],
        },
        "schools": [
            {
                "school_id": item.school_id,
                "profile_version": item.profile_version,
                "reasoning": serialize_reasoned_result(item.reasoning),
                "preferred_pattern_ids": list(item.preferred_pattern_ids),
                "preferred_useful_god_elements": list(
                    item.preferred_useful_god_elements
                ),
            }
            for item in calculation.schools
        ],
    }
    return _validate_calculation_mapping(payload)


def _serialize_evidence_trace(trace: EvidenceTrace) -> JsonObject:
    return {
        "trace_id": trace.trace_id,
        "conclusion_id": trace.conclusion_id,
        "chart_signals": list(trace.chart_signals),
        "evidence_ids": list(trace.evidence_ids),
        "assumptions": list(trace.assumptions),
        "disagreement_note": trace.disagreement_note,
        "calculation_status": trace.calculation_status,
        "calculation_confidence": trace.calculation_confidence,
        "supporting_signals": list(trace.supporting_signals),
        "opposing_signals": list(trace.opposing_signals),
        "rule_ids": list(trace.rule_ids),
        "missing_inputs": list(trace.missing_inputs),
        "school_views": list(trace.school_views),
    }


def _serialize_formal_conclusion(conclusion: FormalConclusion) -> JsonObject:
    return {
        "conclusion_id": conclusion.conclusion_id,
        "title": conclusion.title,
        "body": conclusion.body,
        "rule_family": conclusion.rule_family,
        "strength": conclusion.strength,
        "risk_tier": conclusion.risk_tier,
        "trace": _serialize_evidence_trace(conclusion.trace),
    }


def _serialize_action_reflection(item: ActionReflectionItem) -> JsonObject:
    return {
        "action_id": item.action_id,
        "title": item.title,
        "status": item.status,
        "rule_families": list(item.rule_families),
        "evidence_ids": list(item.evidence_ids),
        "conditions": list(item.conditions),
        "observation_prompt": item.observation_prompt,
        "feedback_metric": item.feedback_metric,
        "stop_boundary": item.stop_boundary,
    }


def _serialize_report_evidence_audit(audit: ReportEvidenceAudit) -> JsonObject:
    return {
        "audit_status": audit.audit_status,
        "rule_family_count": audit.rule_family_count,
        "formal_conclusion_count": audit.formal_conclusion_count,
        "traced_evidence_unit_count": audit.traced_evidence_unit_count,
        "enabled_rule_families": list(audit.enabled_rule_families),
        "conclusion_rule_families": list(audit.conclusion_rule_families),
        "missing_rule_families": list(audit.missing_rule_families),
        "open_conflicts": list(audit.open_conflicts),
        "guardrail_count": audit.guardrail_count,
        "unavailable_conclusion_count": audit.unavailable_conclusion_count,
        "computed_rule_family_count": audit.computed_rule_family_count,
        "indeterminate_rule_family_count": audit.indeterminate_rule_family_count,
        "disputed_rule_family_count": audit.disputed_rule_family_count,
        "not_computed_rule_family_count": audit.not_computed_rule_family_count,
    }


def _serialize_knowledge_activation(
    summary: KnowledgeActivationSummary,
) -> JsonObject:
    return {
        "activation_status": summary.activation_status,
        "source_count": summary.source_count,
        "report_usable_source_count": summary.report_usable_source_count,
        "approved_evidence_count": summary.approved_evidence_count,
        "required_rule_families": list(summary.required_rule_families),
        "enabled_rule_families": list(summary.enabled_rule_families),
        "missing_rule_families": list(summary.missing_rule_families),
        "rule_family_counts": dict(summary.rule_family_counts),
        "risk_tier_counts": dict(summary.risk_tier_counts),
        "sources_with_gaps": list(summary.sources_with_gaps),
        "open_conflicts": list(summary.open_conflicts),
        "quality_failures": list(summary.quality_failures),
        "formal_conclusion_count": summary.formal_conclusion_count,
        "unavailable_conclusion_count": summary.unavailable_conclusion_count,
        "next_action": summary.next_action,
        "guardrails": list(summary.guardrails),
    }


def _serialize_expanded_evidence(evidence: ExpandedReportEvidence) -> JsonObject:
    return {
        "source_summary": list(evidence.source_summary),
        "formal_conclusions": [
            _serialize_formal_conclusion(item)
            for item in evidence.formal_conclusions
        ],
        "high_risk_notes": list(evidence.high_risk_notes),
        "unavailable_conclusions": list(evidence.unavailable_conclusions),
    }


def _serialize_safety_review(review: SafetyReviewResult) -> JsonObject:
    return {
        "allowed": review.allowed,
        "red_line_categories": list(review.red_line_categories),
        "prohibited_phrases": list(review.prohibited_phrases),
        "disclaimer_present": review.disclaimer_present,
        "redirect_message": review.redirect_message,
    }


def serialize_report(report: Report) -> JsonObject:
    payload = {
        "title": report.title,
        "disclaimer": report.disclaimer,
        "quick_guide": report.quick_guide,
        "chart_card": report.chart_card,
        "assumptions": report.assumptions,
        "four_pillars_summary": report.four_pillars_summary,
        "five_elements_summary": report.five_elements_summary,
        "ten_gods_summary": report.ten_gods_summary,
        "evidence_notes": report.evidence_notes,
        "formal_synthesis": report.formal_synthesis,
        "integrated_synthesis": report.integrated_synthesis,
        "structure_analysis": report.structure_analysis,
        "personality_tendencies": report.personality_tendencies,
        "strengths_and_issues": report.strengths_and_issues,
        "phase_overview": report.phase_overview,
        "action_reflection_items": [
            _serialize_action_reflection(item)
            for item in report.action_reflection_items
        ],
        "action_suggestions": report.action_suggestions,
        "interpretation_boundaries": report.interpretation_boundaries,
        "glossary": report.glossary,
        "ethics_reminder": report.ethics_reminder,
        "report_evidence_audit": _serialize_report_evidence_audit(
            report.report_evidence_audit
        ),
        "knowledge_activation": _serialize_knowledge_activation(
            report.knowledge_activation
        ),
        "expanded_evidence": _serialize_expanded_evidence(report.expanded_evidence),
        "safety_review": _serialize_safety_review(report.safety_review),
    }
    return _validate_report_mapping(payload)


def serialize_application_error(error: ApplicationErrorV1) -> JsonObject:
    return {
        "code": error.code,
        "message": error.message,
        "field_path": error.field_path,
        "retryable": error.retryable,
        "trace_id": error.trace_id,
    }


def serialize_application_safety(safety: ApplicationSafetyV1) -> JsonObject:
    return {
        "allowed": safety.allowed,
        "decision": safety.decision,
        "categories": list(safety.categories),
        "redirect_message": safety.redirect_message,
        "requires_narrowing": safety.requires_narrowing,
    }


def serialize_application_provenance(
    provenance: ApplicationProvenanceV1,
) -> JsonObject:
    return {
        "engine_version": provenance.engine_version,
        "ruleset_version": provenance.ruleset_version,
        "provider_version": provenance.provider_version,
        "chart_source_type": provenance.chart_source_type,
        "chart_source_confidence": provenance.chart_source_confidence,
        "evidence_baseline_id": provenance.evidence_baseline_id,
        "evidence_ids": list(provenance.evidence_ids),
    }


def serialize_application_warning(warning: ApplicationWarningV1) -> JsonObject:
    return {"code": warning.code, "message": warning.message}


def serialize_application_privacy(privacy: ApplicationPrivacyV1) -> JsonObject:
    return {
        "retention": privacy.retention,
        "contains_sensitive_profile": privacy.contains_sensitive_profile,
    }


def serialize_application_content(content: ApplicationContentV1) -> JsonObject:
    return {
        "media_type": content.media_type,
        "content": content.content,
        "contains_sensitive_profile": content.contains_sensitive_profile,
    }


def serialize_application_analysis_result(
    result: ApplicationAnalysisResultV1,
) -> JsonObject:
    return {"chart": result.chart, "calculation": result.calculation}


def serialize_application_report_result(
    result: ApplicationReportResultV1,
) -> JsonObject:
    return {
        "report": result.report,
        "content": (
            serialize_application_content(result.content)
            if result.content is not None
            else None
        ),
    }


def _serialize_application_result(result: ApplicationResultV1) -> JsonObject:
    if isinstance(result, ApplicationAnalysisResultV1):
        return serialize_application_analysis_result(result)
    return serialize_application_report_result(result)


def serialize_response_mapping(response: RealUseResponseV1) -> JsonObject:
    return {
        "schema_version": response.schema_version,
        "trace_id": response.trace_id,
        "operation": response.operation,
        "status": response.status,
        "result": (
            _serialize_application_result(response.result)
            if response.result is not None
            else None
        ),
        "safety": serialize_application_safety(response.safety),
        "provenance": (
            serialize_application_provenance(response.provenance)
            if response.provenance is not None
            else None
        ),
        "warnings": [
            serialize_application_warning(warning) for warning in response.warnings
        ],
        "privacy": serialize_application_privacy(response.privacy),
        "error": (
            serialize_application_error(response.error)
            if response.error is not None
            else None
        ),
    }


def serialize_response(response: RealUseResponseV1) -> bytes:
    mapping = serialize_response_mapping(response)
    _validate_response_mapping(mapping)
    _response_from_mapping(mapping)
    payload = json.dumps(
        mapping,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    if len(payload) > MAX_RESPONSE_BYTES:
        raise ResponseSizeError(
            f"response exceeds {MAX_RESPONSE_BYTES} bytes"
        )
    return payload


def _invalid_envelope() -> NoReturn:
    raise ValueError("invalid internal response envelope")


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> JsonObject:
    result: JsonObject = {}
    for key, value in pairs:
        if key in result:
            _invalid_envelope()
        result[key] = value
    return result


def _reject_constant(_value: str) -> NoReturn:
    _invalid_envelope()


def _exact_mapping(value: object, keys: frozenset[str]) -> JsonObject:
    if not isinstance(value, dict) or set(value) != keys:
        _invalid_envelope()
    return cast(JsonObject, value)


def _optional_mapping(
    value: object,
    keys: frozenset[str],
    factory: Callable[..., T],
) -> T | None:
    if value is None:
        return None
    return factory(**_exact_mapping(value, keys))


_ERROR_KEYS = frozenset({"code", "message", "field_path", "retryable", "trace_id"})
_SAFETY_KEYS = frozenset(
    {"allowed", "decision", "categories", "redirect_message", "requires_narrowing"}
)
_PROVENANCE_KEYS = frozenset(
    {
        "engine_version",
        "ruleset_version",
        "provider_version",
        "chart_source_type",
        "chart_source_confidence",
        "evidence_baseline_id",
        "evidence_ids",
    }
)
_WARNING_KEYS = frozenset({"code", "message"})
_PRIVACY_KEYS = frozenset({"retention", "contains_sensitive_profile"})
_CONTENT_KEYS = frozenset({"media_type", "content", "contains_sensitive_profile"})
_ANALYSIS_RESULT_KEYS = frozenset({"chart", "calculation"})
_REPORT_RESULT_KEYS = frozenset({"report", "content"})
_RESPONSE_KEYS = frozenset(
    {
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
)

_CHART_KEYS = frozenset(
    {
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
)
_CHART_SOURCE_KEYS = frozenset(
    {
        "source_type",
        "source_note",
        "calendar_assumption",
        "timezone_assumption",
        "solar_terms_assumption",
        "true_solar_time_applied",
        "confidence",
    }
)
_PILLAR_KEYS = frozenset(
    {
        "name",
        "heavenly_stem",
        "earthly_branch",
        "gan_zhi",
        "hidden_stems",
        "ten_god",
        "element",
    }
)
_CALCULATION_KEYS = frozenset(
    {
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
)
_FACTS_KEYS = frozenset(
    {
        "day_master",
        "month_branch",
        "exposed_stems",
        "hidden_stems",
        "roots",
        "twelve_growth_by_pillar",
        "assumptions",
    }
)
_EXPOSED_STEM_KEYS = frozenset(
    {"pillar_name", "stem", "element", "polarity", "ten_god"}
)
_HIDDEN_STEM_KEYS = frozenset(
    {"pillar_name", "branch", "stem", "role", "element", "polarity", "ten_god"}
)
_ROOT_KEYS = frozenset(
    {"stem", "stem_pillar", "branch", "branch_pillar", "role", "exact_stem_root"}
)
_RELATION_KEYS = frozenset(
    {
        "relation_type",
        "branches",
        "pillar_names",
        "state",
        "transformed_element",
        "conditions",
        "blockers",
        "rule_id",
    }
)
_REASONING_KEYS = frozenset(
    {
        "status",
        "conclusion",
        "confidence",
        "supporting_signals",
        "opposing_signals",
        "assumptions",
        "missing_inputs",
        "rule_ids",
    }
)
_STRENGTH_KEYS = frozenset(
    {"reasoning", "score", "lower_bound", "upper_bound", "label", "contributions"}
)
_CONTRIBUTION_KEYS = frozenset({"category", "signal", "value", "rule_id"})
_PATTERN_KEYS = frozenset(
    {
        "pattern_id",
        "name",
        "rank",
        "reasoning",
        "formation_conditions",
        "damage_conditions",
        "rescue_conditions",
    }
)
_USEFUL_GOD_KEYS = frozenset({"method", "element", "rank", "reasoning"})
_LUCK_CYCLE_KEYS = frozenset(
    {
        "reasoning",
        "forward",
        "start_years",
        "start_months",
        "start_days",
        "start_solar",
        "pillars",
        "selected_year_relations",
    }
)
_LUCK_PILLAR_KEYS = frozenset(
    {"index", "gan_zhi", "start_year", "end_year", "start_age", "end_age"}
)
_SCHOOL_KEYS = frozenset(
    {
        "school_id",
        "profile_version",
        "reasoning",
        "preferred_pattern_ids",
        "preferred_useful_god_elements",
    }
)
_REPORT_KEYS = frozenset(
    {
        "title",
        "disclaimer",
        "quick_guide",
        "chart_card",
        "assumptions",
        "four_pillars_summary",
        "five_elements_summary",
        "ten_gods_summary",
        "evidence_notes",
        "formal_synthesis",
        "integrated_synthesis",
        "structure_analysis",
        "personality_tendencies",
        "strengths_and_issues",
        "phase_overview",
        "action_reflection_items",
        "action_suggestions",
        "interpretation_boundaries",
        "glossary",
        "ethics_reminder",
        "report_evidence_audit",
        "knowledge_activation",
        "expanded_evidence",
        "safety_review",
    }
)
_ACTION_REFLECTION_KEYS = frozenset(
    {
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
)
_REPORT_AUDIT_KEYS = frozenset(
    {
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
)
_KNOWLEDGE_ACTIVATION_KEYS = frozenset(
    {
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
)
_EXPANDED_EVIDENCE_KEYS = frozenset(
    {"source_summary", "formal_conclusions", "high_risk_notes", "unavailable_conclusions"}
)
_FORMAL_CONCLUSION_KEYS = frozenset(
    {"conclusion_id", "title", "body", "rule_family", "strength", "risk_tier", "trace"}
)
_EVIDENCE_TRACE_KEYS = frozenset(
    {
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
)
_REPORT_SAFETY_KEYS = frozenset(
    {
        "allowed",
        "red_line_categories",
        "prohibited_phrases",
        "disclaimer_present",
        "redirect_message",
    }
)


def _require_string(value: object) -> None:
    if not isinstance(value, str):
        _invalid_envelope()


def _require_bool(value: object) -> None:
    if type(value) is not bool:
        _invalid_envelope()


def _require_int(value: object) -> None:
    if type(value) is not int:
        _invalid_envelope()


def _require_float(value: object) -> None:
    if type(value) is not float:
        _invalid_envelope()


def _require_optional_string(value: object) -> None:
    if value is not None:
        _require_string(value)


def _require_optional_bool(value: object) -> None:
    if value is not None:
        _require_bool(value)


def _require_uuid4(value: object) -> None:
    _require_string(value)
    try:
        parsed = UUID(cast(str, value))
    except (ValueError, AttributeError):
        _invalid_envelope()
    if parsed.version != 4 or str(parsed) != value:
        _invalid_envelope()


def _require_list(
    value: object,
    item_validator: Callable[[object], None],
) -> list[Any]:
    if not isinstance(value, list):
        _invalid_envelope()
    items = cast(list[Any], value)
    for item in items:
        item_validator(item)
    return items


def _require_string_list(value: object) -> None:
    _require_list(value, _require_string)


def _require_string_mapping(value: object) -> None:
    if not isinstance(value, dict):
        _invalid_envelope()
    for key, item in value.items():
        _require_string(key)
        _require_string(item)


def _require_integer_mapping(value: object) -> None:
    if not isinstance(value, dict):
        _invalid_envelope()
    for key, item in value.items():
        _require_string(key)
        _require_int(item)


def _validate_chart_source(value: object) -> None:
    source = _exact_mapping(value, _CHART_SOURCE_KEYS)
    for key in (
        "source_type",
        "source_note",
        "calendar_assumption",
        "timezone_assumption",
        "solar_terms_assumption",
        "confidence",
    ):
        _require_string(source[key])
    _require_optional_bool(source["true_solar_time_applied"])


def _validate_pillar(value: object) -> None:
    pillar = _exact_mapping(value, _PILLAR_KEYS)
    for key in (
        "name",
        "heavenly_stem",
        "earthly_branch",
        "gan_zhi",
        "ten_god",
        "element",
    ):
        _require_string(pillar[key])
    _require_string_list(pillar["hidden_stems"])
    if pillar["gan_zhi"] != pillar["heavenly_stem"] + pillar["earthly_branch"]:
        _invalid_envelope()


def _validate_chart_mapping(value: object) -> JsonObject:
    chart = _exact_mapping(value, _CHART_KEYS)
    _validate_chart_source(chart["chart_source"])
    pillars = _require_list(chart["pillars"], _validate_pillar)
    if len(pillars) != 4:
        _invalid_envelope()
    for key in (
        "day_master",
        "ten_gods_summary",
        "strength_assessment",
        "luck_cycle_summary",
    ):
        _require_string(chart[key])
    _require_string_mapping(chart["five_elements_summary"])
    _require_string_list(chart["pattern_candidates"])
    _require_string_list(chart["useful_god_candidates"])
    return chart


def _validate_reasoning(value: object) -> None:
    reasoning = _exact_mapping(value, _REASONING_KEYS)
    for key in ("status", "conclusion", "confidence"):
        _require_string(reasoning[key])
    if reasoning["status"] not in {
        "not_computed",
        "computed",
        "indeterminate",
        "disputed",
    }:
        _invalid_envelope()
    if reasoning["confidence"] not in {"high", "medium", "low"}:
        _invalid_envelope()
    for key in (
        "supporting_signals",
        "opposing_signals",
        "assumptions",
        "missing_inputs",
        "rule_ids",
    ):
        _require_string_list(reasoning[key])


def _validate_relation(value: object) -> None:
    relation = _exact_mapping(value, _RELATION_KEYS)
    for key in (
        "relation_type",
        "state",
        "transformed_element",
        "rule_id",
    ):
        _require_string(relation[key])
    for key in ("branches", "pillar_names", "conditions", "blockers"):
        _require_string_list(relation[key])


def _validate_exposed_stem(value: object) -> None:
    stem = _exact_mapping(value, _EXPOSED_STEM_KEYS)
    for item in stem.values():
        _require_string(item)


def _validate_hidden_stem(value: object) -> None:
    stem = _exact_mapping(value, _HIDDEN_STEM_KEYS)
    for item in stem.values():
        _require_string(item)


def _validate_root(value: object) -> None:
    root = _exact_mapping(value, _ROOT_KEYS)
    for key in ("stem", "stem_pillar", "branch", "branch_pillar", "role"):
        _require_string(root[key])
    _require_bool(root["exact_stem_root"])


def _validate_growth_pair(value: object) -> None:
    items = _require_list(value, _require_string)
    if len(items) != 2:
        _invalid_envelope()


def _validate_facts(value: object) -> None:
    facts = _exact_mapping(value, _FACTS_KEYS)
    _require_string(facts["day_master"])
    _require_string(facts["month_branch"])
    _require_list(facts["exposed_stems"], _validate_exposed_stem)
    _require_list(facts["hidden_stems"], _validate_hidden_stem)
    _require_list(facts["roots"], _validate_root)
    _require_list(facts["twelve_growth_by_pillar"], _validate_growth_pair)
    _require_string_list(facts["assumptions"])


def _validate_contribution(value: object) -> None:
    contribution = _exact_mapping(value, _CONTRIBUTION_KEYS)
    for key in ("category", "signal", "rule_id"):
        _require_string(contribution[key])
    _require_float(contribution["value"])


def _validate_strength(value: object) -> None:
    strength = _exact_mapping(value, _STRENGTH_KEYS)
    _validate_reasoning(strength["reasoning"])
    for key in ("score", "lower_bound", "upper_bound"):
        _require_float(strength[key])
    _require_string(strength["label"])
    _require_list(strength["contributions"], _validate_contribution)


def _validate_pattern(value: object) -> None:
    pattern = _exact_mapping(value, _PATTERN_KEYS)
    _require_string(pattern["pattern_id"])
    _require_string(pattern["name"])
    _require_int(pattern["rank"])
    _validate_reasoning(pattern["reasoning"])
    for key in ("formation_conditions", "damage_conditions", "rescue_conditions"):
        _require_string_list(pattern[key])


def _validate_useful_god(value: object) -> None:
    candidate = _exact_mapping(value, _USEFUL_GOD_KEYS)
    _require_string(candidate["method"])
    _require_string(candidate["element"])
    _require_int(candidate["rank"])
    _validate_reasoning(candidate["reasoning"])


def _validate_luck_pillar(value: object) -> None:
    pillar = _exact_mapping(value, _LUCK_PILLAR_KEYS)
    _require_string(pillar["gan_zhi"])
    for key in ("index", "start_year", "end_year", "start_age", "end_age"):
        _require_int(pillar[key])


def _validate_luck_cycles(value: object) -> None:
    cycles = _exact_mapping(value, _LUCK_CYCLE_KEYS)
    _validate_reasoning(cycles["reasoning"])
    _require_bool(cycles["forward"])
    for key in ("start_years", "start_months", "start_days"):
        _require_int(cycles[key])
    _require_string(cycles["start_solar"])
    _require_list(cycles["pillars"], _validate_luck_pillar)
    _require_list(cycles["selected_year_relations"], _validate_relation)


def _validate_school(value: object) -> None:
    school = _exact_mapping(value, _SCHOOL_KEYS)
    _require_string(school["school_id"])
    _require_string(school["profile_version"])
    _validate_reasoning(school["reasoning"])
    _require_string_list(school["preferred_pattern_ids"])
    _require_string_list(school["preferred_useful_god_elements"])


def _validate_calculation_mapping(value: object) -> JsonObject:
    calculation = _exact_mapping(value, _CALCULATION_KEYS)
    _require_string(calculation["engine_version"])
    _require_string(calculation["ruleset_version"])
    _validate_facts(calculation["facts"])
    _require_list(calculation["branch_relations"], _validate_relation)
    _validate_strength(calculation["strength"])
    _require_list(calculation["patterns"], _validate_pattern)
    _require_list(calculation["useful_gods"], _validate_useful_god)
    _validate_luck_cycles(calculation["luck_cycles"])
    _require_list(calculation["schools"], _validate_school)
    return calculation


def _validate_action_reflection(value: object) -> None:
    item = _exact_mapping(value, _ACTION_REFLECTION_KEYS)
    for key in (
        "action_id",
        "title",
        "status",
        "observation_prompt",
        "feedback_metric",
        "stop_boundary",
    ):
        _require_string(item[key])
    for key in ("rule_families", "evidence_ids", "conditions"):
        _require_string_list(item[key])


def _validate_report_audit(value: object) -> None:
    audit = _exact_mapping(value, _REPORT_AUDIT_KEYS)
    _require_string(audit["audit_status"])
    for key in (
        "rule_family_count",
        "formal_conclusion_count",
        "traced_evidence_unit_count",
        "guardrail_count",
        "unavailable_conclusion_count",
        "computed_rule_family_count",
        "indeterminate_rule_family_count",
        "disputed_rule_family_count",
        "not_computed_rule_family_count",
    ):
        _require_int(audit[key])
    for key in (
        "enabled_rule_families",
        "conclusion_rule_families",
        "missing_rule_families",
        "open_conflicts",
    ):
        _require_string_list(audit[key])


def _validate_knowledge_activation(value: object) -> None:
    summary = _exact_mapping(value, _KNOWLEDGE_ACTIVATION_KEYS)
    _require_string(summary["activation_status"])
    _require_string(summary["next_action"])
    for key in (
        "source_count",
        "report_usable_source_count",
        "approved_evidence_count",
        "formal_conclusion_count",
        "unavailable_conclusion_count",
    ):
        _require_int(summary[key])
    for key in (
        "required_rule_families",
        "enabled_rule_families",
        "missing_rule_families",
        "sources_with_gaps",
        "open_conflicts",
        "quality_failures",
        "guardrails",
    ):
        _require_string_list(summary[key])
    _require_integer_mapping(summary["rule_family_counts"])
    _require_integer_mapping(summary["risk_tier_counts"])


def _validate_evidence_trace(value: object) -> None:
    trace = _exact_mapping(value, _EVIDENCE_TRACE_KEYS)
    for key in (
        "trace_id",
        "conclusion_id",
        "disagreement_note",
        "calculation_status",
        "calculation_confidence",
    ):
        _require_string(trace[key])
    if trace["calculation_status"] not in CALCULATION_STATUSES:
        _invalid_envelope()
    if trace["calculation_confidence"] not in CALCULATION_CONFIDENCES:
        _invalid_envelope()
    for key in (
        "chart_signals",
        "evidence_ids",
        "assumptions",
        "supporting_signals",
        "opposing_signals",
        "rule_ids",
        "missing_inputs",
        "school_views",
    ):
        _require_string_list(trace[key])


def _validate_formal_conclusion(value: object) -> None:
    conclusion = _exact_mapping(value, _FORMAL_CONCLUSION_KEYS)
    for key in (
        "conclusion_id",
        "title",
        "body",
        "rule_family",
        "strength",
        "risk_tier",
    ):
        _require_string(conclusion[key])
    _validate_evidence_trace(conclusion["trace"])


def _validate_expanded_evidence(value: object) -> None:
    evidence = _exact_mapping(value, _EXPANDED_EVIDENCE_KEYS)
    _require_string_list(evidence["source_summary"])
    _require_list(evidence["formal_conclusions"], _validate_formal_conclusion)
    _require_string_list(evidence["high_risk_notes"])
    _require_string_list(evidence["unavailable_conclusions"])


def _validate_report_safety(value: object) -> None:
    safety = _exact_mapping(value, _REPORT_SAFETY_KEYS)
    _require_bool(safety["allowed"])
    _require_string_list(safety["red_line_categories"])
    _require_string_list(safety["prohibited_phrases"])
    _require_bool(safety["disclaimer_present"])
    _require_string(safety["redirect_message"])


def _validate_report_mapping(value: object) -> JsonObject:
    report = _exact_mapping(value, _REPORT_KEYS)
    for key in (
        "title",
        "disclaimer",
        "quick_guide",
        "chart_card",
        "assumptions",
        "four_pillars_summary",
        "five_elements_summary",
        "ten_gods_summary",
        "evidence_notes",
        "formal_synthesis",
        "integrated_synthesis",
        "structure_analysis",
        "personality_tendencies",
        "strengths_and_issues",
        "phase_overview",
        "action_suggestions",
        "interpretation_boundaries",
        "glossary",
        "ethics_reminder",
    ):
        _require_string(report[key])
    _require_list(report["action_reflection_items"], _validate_action_reflection)
    _validate_report_audit(report["report_evidence_audit"])
    _validate_knowledge_activation(report["knowledge_activation"])
    _validate_expanded_evidence(report["expanded_evidence"])
    _validate_report_safety(report["safety_review"])
    return report


def _validate_application_safety(value: object) -> None:
    safety = _exact_mapping(value, _SAFETY_KEYS)
    _require_bool(safety["allowed"])
    _require_string(safety["decision"])
    _require_string_list(safety["categories"])
    _require_string(safety["redirect_message"])
    _require_bool(safety["requires_narrowing"])


def _validate_application_provenance(value: object) -> None:
    provenance = _exact_mapping(value, _PROVENANCE_KEYS)
    for key in (
        "engine_version",
        "ruleset_version",
        "provider_version",
        "chart_source_type",
        "chart_source_confidence",
        "evidence_baseline_id",
    ):
        _require_string(provenance[key])
    _require_string_list(provenance["evidence_ids"])


def _validate_application_privacy(value: object) -> None:
    privacy = _exact_mapping(value, _PRIVACY_KEYS)
    _require_string(privacy["retention"])
    _require_bool(privacy["contains_sensitive_profile"])


def _validate_application_error(value: object) -> None:
    error = _exact_mapping(value, _ERROR_KEYS)
    _require_string(error["code"])
    _require_string(error["message"])
    _require_optional_string(error["field_path"])
    _require_bool(error["retryable"])
    _require_uuid4(error["trace_id"])


def _validate_application_warning(value: object) -> None:
    warning = _exact_mapping(value, _WARNING_KEYS)
    _require_string(warning["code"])
    _require_string(warning["message"])


def _validate_application_content(value: object) -> None:
    content = _exact_mapping(value, _CONTENT_KEYS)
    _require_string(content["media_type"])
    _require_string(content["content"])
    _require_bool(content["contains_sensitive_profile"])


def _validate_analysis_result(value: object) -> None:
    result = _exact_mapping(value, _ANALYSIS_RESULT_KEYS)
    _validate_chart_mapping(result["chart"])
    _validate_calculation_mapping(result["calculation"])


def _validate_report_result(value: object) -> None:
    result = _exact_mapping(value, _REPORT_RESULT_KEYS)
    has_report = result["report"] is not None
    has_content = result["content"] is not None
    if has_report == has_content:
        _invalid_envelope()
    if has_report:
        _validate_report_mapping(result["report"])
    else:
        _validate_application_content(result["content"])


def _validate_success_cross_invariants(response: JsonObject) -> None:
    if response["status"] != "ok":
        return
    result = response["result"]
    provenance = response["provenance"]
    if result is None or provenance is None or response["error"] is not None:
        _invalid_envelope()
    privacy = _exact_mapping(response["privacy"], _PRIVACY_KEYS)
    if response["operation"] == "analysis":
        analysis = _exact_mapping(result, _ANALYSIS_RESULT_KEYS)
        calculation = _exact_mapping(analysis["calculation"], _CALCULATION_KEYS)
        provenance_mapping = _exact_mapping(provenance, _PROVENANCE_KEYS)
        if privacy["contains_sensitive_profile"]:
            _invalid_envelope()
        for key in ("engine_version", "ruleset_version"):
            if provenance_mapping[key] != calculation[key]:
                _invalid_envelope()
        return
    if response["operation"] == "report":
        report_result = _exact_mapping(result, _REPORT_RESULT_KEYS)
        if report_result["report"] is not None:
            report = _exact_mapping(report_result["report"], _REPORT_KEYS)
            safety = _exact_mapping(report["safety_review"], _REPORT_SAFETY_KEYS)
            if not safety["allowed"]:
                _invalid_envelope()
            return
        content = _exact_mapping(report_result["content"], _CONTENT_KEYS)
        if (
            content["contains_sensitive_profile"]
            != privacy["contains_sensitive_profile"]
        ):
            _invalid_envelope()
        return
    _invalid_envelope()


def _validate_response_mapping(value: object) -> JsonObject:
    response = _exact_mapping(value, _RESPONSE_KEYS)
    _require_string(response["schema_version"])
    _require_uuid4(response["trace_id"])
    _require_optional_string(response["operation"])
    _require_string(response["status"])
    _validate_application_safety(response["safety"])
    if response["provenance"] is not None:
        _validate_application_provenance(response["provenance"])
    _require_list(response["warnings"], _validate_application_warning)
    _validate_application_privacy(response["privacy"])
    if response["error"] is not None:
        _validate_application_error(response["error"])
    if response["result"] is not None:
        if response["operation"] == "analysis":
            _validate_analysis_result(response["result"])
        elif response["operation"] == "report":
            _validate_report_result(response["result"])
        else:
            _invalid_envelope()
    _validate_success_cross_invariants(response)
    return response


def _parse_result(value: object, operation: object) -> ApplicationResultV1 | None:
    if value is None:
        return None
    if operation == "analysis":
        mapping = _exact_mapping(value, _ANALYSIS_RESULT_KEYS)
        return ApplicationAnalysisResultV1(
            chart=mapping["chart"],
            calculation=mapping["calculation"],
        )
    if operation == "report":
        mapping = _exact_mapping(value, _REPORT_RESULT_KEYS)
        content = _optional_mapping(
            mapping["content"],
            _CONTENT_KEYS,
            ApplicationContentV1,
        )
        return ApplicationReportResultV1(mapping["report"], content)
    _invalid_envelope()


def _response_from_mapping(root: JsonObject) -> RealUseResponseV1:
    safety = ApplicationSafetyV1(**_exact_mapping(root["safety"], _SAFETY_KEYS))
    provenance = _optional_mapping(
        root["provenance"],
        _PROVENANCE_KEYS,
        ApplicationProvenanceV1,
    )
    privacy = ApplicationPrivacyV1(
        **_exact_mapping(root["privacy"], _PRIVACY_KEYS)
    )
    error = _optional_mapping(root["error"], _ERROR_KEYS, ApplicationErrorV1)
    warnings_value = root["warnings"]
    if not isinstance(warnings_value, list):
        _invalid_envelope()
    warnings = tuple(
        ApplicationWarningV1(**_exact_mapping(item, _WARNING_KEYS))
        for item in warnings_value
    )
    return RealUseResponseV1(
        schema_version=root["schema_version"],
        trace_id=root["trace_id"],
        operation=root["operation"],
        status=root["status"],
        result=_parse_result(root["result"], root["operation"]),
        safety=safety,
        provenance=provenance,
        warnings=warnings,
        privacy=privacy,
        error=error,
    )


def response_status_from_json_bytes(payload: bytes) -> ResponseStatus:
    try:
        if not isinstance(payload, bytes) or len(payload) > MAX_RESPONSE_BYTES:
            _invalid_envelope()
        parsed = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
        root = _validate_response_mapping(parsed)
        response = _response_from_mapping(root)
        if serialize_response(response) != payload:
            _invalid_envelope()
        return response.status
    except Exception:
        _invalid_envelope()
