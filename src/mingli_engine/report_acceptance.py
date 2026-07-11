from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.classical_sources import (
    load_approved_evidence_units,
    load_classical_sources,
    load_source_conflicts,
)
from mingli_engine.evidence_curation import build_knowledge_activation_summary
from mingli_engine.html import render_html_report
from mingli_engine.markdown import render_markdown_report
from mingli_engine.models import (
    BirthProfile,
    EvidenceTrace,
    ExpandedReportEvidence,
    FormalConclusion,
    KnowledgeActivationSummary,
    Report,
    ReportAcceptanceCaseResult,
    ReportAcceptanceSummary,
    ReportEvidenceAudit,
)
from mingli_engine.report_schema import (
    KnowledgeActivationError,
    build_formal_synthesis,
    build_report,
)


_BASELINE_ID = "report_acceptance_v1"
_PASS = "passed"
_FAIL = "failed"


def _check(condition: bool) -> str:
    return _PASS if condition else _FAIL


def _case_status(checks: dict[str, str]) -> str:
    return _PASS if checks and all(value == _PASS for value in checks.values()) else _FAIL


def _synthetic_profile(*, focus_topic: str) -> BirthProfile:
    return BirthProfile(
        calendar_type="gregorian",
        birth_date="1992-08-18",
        birth_time="09:30",
        birthplace="acceptance-fixture",
        gender="unspecified",
        focus_topic=focus_topic,
    )


def _build_safe_report() -> Report:
    chart = calculate_bazi_chart(
        _synthetic_profile(focus_topic="career planning and long-term learning")
    )
    return build_report(chart)


def _load_activation_summary() -> KnowledgeActivationSummary:
    return build_knowledge_activation_summary(
        load_classical_sources(),
        load_approved_evidence_units(),
        load_source_conflicts(),
    )


def _ordinary_production_case(report: Report) -> ReportAcceptanceCaseResult:
    markdown = render_markdown_report(report)
    html = render_html_report(report)
    enabled_families = report.knowledge_activation.enabled_rule_families
    synthesis_complete = (
        report.formal_synthesis.count("rule_family=") == len(enabled_families)
        and all(
            report.formal_synthesis.count(f"rule_family={family}") == 1
            for family in enabled_families
        )
    )
    personalized_signals = (
        report.formal_synthesis.count("盘面信号：") == len(enabled_families)
        and "traditional_high_risk_signal_boundary"
        not in report.formal_synthesis
        and "traditional_high_risk_signal_boundary" not in report.evidence_notes
    )
    markdown_ordered = (
        markdown.count(report.formal_synthesis) == 1
        and markdown.find(report.evidence_notes)
        < markdown.find(report.formal_synthesis)
        < markdown.find(report.structure_analysis)
    )
    html_lower = html.lower()
    html_ordered = (
        html.count(report.formal_synthesis) == 1
        and html.find(report.evidence_notes)
        < html.find(report.formal_synthesis)
        < html.find(report.structure_analysis)
        and "http://" not in html_lower
        and "https://" not in html_lower
        and "<script" not in html_lower
    )
    checks = {
        "report_safety": _check(report.safety_review.allowed),
        "knowledge_activation": _check(
            report.knowledge_activation.activation_status
            in {"enabled", "enabled_with_guardrails"}
        ),
        "evidence_audit": _check(
            report.report_evidence_audit.audit_status
            in {"complete", "complete_with_guardrails"}
        ),
        "evidence_trace_count": _check(
            report.report_evidence_audit.traced_evidence_unit_count == 111
        ),
        "rule_family_coverage": _check(
            report.report_evidence_audit.rule_family_count == 10
            and not report.report_evidence_audit.missing_rule_families
        ),
        "formal_synthesis_coverage": _check(synthesis_complete),
        "personalized_chart_signals": _check(personalized_signals),
        "markdown_rendering": _check(markdown_ordered),
        "html_rendering": _check(html_ordered),
    }
    return ReportAcceptanceCaseResult(
        case_id="ordinary_production_report",
        scenario_type="production_report",
        status=_case_status(checks),
        checks=checks,
        guardrails=["synthetic_profile_not_persisted"],
    )


def _conflict_guardrail_case(report: Report) -> ReportAcceptanceCaseResult:
    disputed = [
        conclusion
        for conclusion in report.expanded_evidence.formal_conclusions
        if conclusion.strength == "disputed"
    ]
    disagreement_notes = [
        conclusion.trace.disagreement_note
        for conclusion in disputed
        if conclusion.trace.disagreement_note
    ]
    checks = {
        "open_conflict_exposed": _check(
            bool(report.report_evidence_audit.open_conflicts)
            and all(
                conflict_id in report.evidence_notes
                for conflict_id in report.report_evidence_audit.open_conflicts
            )
        ),
        "disputed_conclusion_exposed": _check(
            bool(disputed)
            and all(
                f"rule_family={conclusion.rule_family}" in report.formal_synthesis
                for conclusion in disputed
            )
        ),
        "disagreement_note_exposed": _check(
            bool(disagreement_notes)
            and all(note in report.formal_synthesis for note in disagreement_notes)
        ),
        "high_risk_boundary_exposed": _check(
            "不预测精确事件或寿命" in report.formal_synthesis
            and "不替代医疗、法律、心理、投资等专业建议" in report.formal_synthesis
        ),
    }
    return ReportAcceptanceCaseResult(
        case_id="conflict_guardrail",
        scenario_type="conflict_boundary",
        status=_case_status(checks),
        checks=checks,
        guardrails=["non_deterministic_high_risk_language"],
    )


def _high_risk_rejection_case() -> ReportAcceptanceCaseResult:
    chart = calculate_bazi_chart(_synthetic_profile(focus_topic="寿命多长"))
    report = build_report(chart)
    rejected = not report.safety_review.allowed
    rendered_report = None if rejected else render_markdown_report(report)
    checks = {
        "safety_rejected": _check(rejected),
        "lifespan_category_exposed": _check(
            "lifespan_or_death_timing" in report.safety_review.red_line_categories
        ),
        "rendering_withheld": _check(rendered_report is None),
    }
    return ReportAcceptanceCaseResult(
        case_id="high_risk_rejection",
        scenario_type="safety_rejection",
        status=_case_status(checks),
        checks=checks,
        guardrails=["exact_lifespan_output_prohibited"],
    )


def _unavailable_degradation_case() -> ReportAcceptanceCaseResult:
    body = "当前证据不足，不输出高风险判断。"
    conclusion = FormalConclusion(
        conclusion_id="formal_high_risk_signal",
        title="高风险信号边界",
        body=body,
        rule_family="high_risk_signal",
        strength="unavailable",
        risk_tier="high_risk",
        trace=EvidenceTrace(
            trace_id="trace_high_risk_signal",
            conclusion_id="formal_high_risk_signal",
            chart_signals=["traditional_high_risk_signal_boundary"],
            evidence_ids=[],
            assumptions=["rule_family:high_risk_signal"],
            disagreement_note="No approved evidence unit is available.",
        ),
    )
    expanded = ExpandedReportEvidence(
        source_summary=[],
        formal_conclusions=[conclusion],
        unavailable_conclusions=[conclusion.title],
    )
    audit = ReportEvidenceAudit(
        audit_status="incomplete",
        rule_family_count=1,
        formal_conclusion_count=1,
        traced_evidence_unit_count=0,
        enabled_rule_families=["high_risk_signal"],
        conclusion_rule_families=[],
        missing_rule_families=["high_risk_signal"],
        open_conflicts=[],
        guardrail_count=1,
        unavailable_conclusion_count=1,
    )
    synthesis = build_formal_synthesis(expanded, audit)
    checks = {
        "incomplete_status_exposed": _check("不完整" in synthesis),
        "unavailable_family_exposed": _check(
            "rule_family=high_risk_signal" in synthesis and "不可用" in synthesis
        ),
        "source_body_preserved": _check(body in synthesis),
        "professional_boundary_preserved": _check(
            "不预测精确事件或寿命" in synthesis
            and "不替代医疗、法律、心理、投资等专业建议" in synthesis
        ),
    }
    return ReportAcceptanceCaseResult(
        case_id="unavailable_degradation",
        scenario_type="evidence_degradation",
        status=_case_status(checks),
        checks=checks,
        guardrails=["unavailable_conclusions_are_not_promoted"],
    )


def determine_report_acceptance_status(
    cases: list[ReportAcceptanceCaseResult],
    open_conflicts: list[str],
) -> str:
    if not cases or any(case.status != _PASS for case in cases):
        return "blocked"
    if open_conflicts:
        return "ready_with_guardrails"
    return "ready"


def build_report_acceptance_summary() -> ReportAcceptanceSummary:
    try:
        report = _build_safe_report()
    except KnowledgeActivationError:
        activation = _load_activation_summary()
        failed_case = ReportAcceptanceCaseResult(
            case_id="ordinary_production_report",
            scenario_type="production_report",
            status=_FAIL,
            checks={"report_construction": _FAIL},
            guardrails=["knowledge_activation_gate_enforced"],
        )
        return ReportAcceptanceSummary(
            baseline_id=_BASELINE_ID,
            acceptance_status="blocked",
            case_count=1,
            passed_case_count=0,
            activation_status=activation.activation_status,
            report_audit_status="unavailable",
            approved_evidence_count=activation.approved_evidence_count,
            rule_family_count=len(activation.enabled_rule_families),
            traced_evidence_unit_count=0,
            missing_rule_families=list(activation.missing_rule_families),
            open_conflicts=list(activation.open_conflicts),
            cases=[failed_case],
            guardrails=[
                "synthetic_profiles_not_persisted",
                "source_library_013_012_read_only",
                "knowledge_activation_gate_enforced",
            ],
            next_action=activation.next_action,
        )
    cases = [
        _ordinary_production_case(report),
        _conflict_guardrail_case(report),
        _high_risk_rejection_case(),
        _unavailable_degradation_case(),
    ]
    open_conflicts = list(report.report_evidence_audit.open_conflicts)
    status = determine_report_acceptance_status(cases, open_conflicts)
    if status == "ready_with_guardrails":
        next_action = "release_reports_with_guardrails"
    elif status == "ready":
        next_action = "release_reports"
    else:
        next_action = "resolve_failed_acceptance_cases"
    return ReportAcceptanceSummary(
        baseline_id=_BASELINE_ID,
        acceptance_status=status,
        case_count=len(cases),
        passed_case_count=sum(case.status == _PASS for case in cases),
        activation_status=report.knowledge_activation.activation_status,
        report_audit_status=report.report_evidence_audit.audit_status,
        approved_evidence_count=report.knowledge_activation.approved_evidence_count,
        rule_family_count=report.report_evidence_audit.rule_family_count,
        traced_evidence_unit_count=(
            report.report_evidence_audit.traced_evidence_unit_count
        ),
        missing_rule_families=list(report.report_evidence_audit.missing_rule_families),
        open_conflicts=open_conflicts,
        cases=cases,
        guardrails=[
            "synthetic_profiles_not_persisted",
            "source_library_013_012_read_only",
            "high_risk_outputs_require_safety_rejection_or_guardrails",
        ],
        next_action=next_action,
    )
