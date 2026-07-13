import json
from collections.abc import Callable
from typing import Any, NoReturn, TypeVar, cast

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
    return {
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
    return {
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
    return {
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
    payload = json.dumps(
        serialize_response_mapping(response),
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
        response = _response_from_mapping(_exact_mapping(parsed, _RESPONSE_KEYS))
        if serialize_response(response) != payload:
            _invalid_envelope()
        return response.status
    except Exception:
        _invalid_envelope()
