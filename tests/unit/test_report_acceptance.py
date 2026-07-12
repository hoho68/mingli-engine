from mingli_engine.models import KnowledgeActivationSummary, ReportAcceptanceCaseResult
from mingli_engine.report_schema import KnowledgeActivationError
from mingli_engine import report_acceptance
from mingli_engine.report_acceptance import (
    build_report_acceptance_summary,
    determine_report_acceptance_status,
)


def _case_by_id(summary, case_id: str):
    return next(case for case in summary.cases if case.case_id == case_id)


def test_report_acceptance_summary_certifies_current_release_baseline():
    summary = build_report_acceptance_summary()

    assert summary.baseline_id == "report_acceptance_v1"
    assert summary.acceptance_status == "ready_with_guardrails"
    assert summary.case_count == 4
    assert summary.passed_case_count == 4
    assert summary.activation_status == "enabled_with_guardrails"
    assert summary.report_audit_status == "complete_with_guardrails"
    assert summary.approved_evidence_count == 111
    assert summary.rule_family_count == 10
    assert summary.traced_evidence_unit_count == 111
    assert summary.missing_rule_families == []
    assert summary.open_conflicts == ["conflict_high_risk_scope_001"]
    assert [case.case_id for case in summary.cases] == [
        "ordinary_production_report",
        "conflict_guardrail",
        "high_risk_rejection",
        "unavailable_degradation",
    ]
    assert summary.next_action == "release_reports_with_guardrails"
    assert "synthetic_profiles_not_persisted" in summary.guardrails


def test_ordinary_report_case_covers_content_renderers_and_safety():
    case = _case_by_id(
        build_report_acceptance_summary(),
        "ordinary_production_report",
    )

    assert case.scenario_type == "production_report"
    assert case.status == "passed"
    assert case.checks == {
        "report_safety": "passed",
        "knowledge_activation": "passed",
        "evidence_audit": "passed",
        "evidence_trace_count": "passed",
        "rule_family_coverage": "passed",
        "formal_synthesis_coverage": "passed",
        "personalized_chart_signals": "passed",
        "integrated_cross_family_synthesis": "passed",
        "evidence_backed_action_reflection": "passed",
        "markdown_rendering": "passed",
        "html_rendering": "passed",
    }


def test_conflict_case_preserves_disagreement_and_high_risk_guardrails():
    case = _case_by_id(
        build_report_acceptance_summary(),
        "conflict_guardrail",
    )

    assert case.status == "passed"
    assert case.checks == {
        "open_conflict_exposed": "passed",
        "disputed_conclusion_exposed": "passed",
        "disagreement_note_exposed": "passed",
        "high_risk_boundary_exposed": "passed",
    }
    assert "non_deterministic_high_risk_language" in case.guardrails


def test_high_risk_case_is_rejected_before_render_acceptance():
    case = _case_by_id(
        build_report_acceptance_summary(),
        "high_risk_rejection",
    )

    assert case.status == "passed"
    assert case.checks == {
        "safety_rejected": "passed",
        "lifespan_category_exposed": "passed",
        "rendering_withheld": "passed",
    }
    assert "exact_lifespan_output_prohibited" in case.guardrails


def test_unavailable_case_keeps_incomplete_and_professional_boundaries():
    case = _case_by_id(
        build_report_acceptance_summary(),
        "unavailable_degradation",
    )

    assert case.status == "passed"
    assert case.checks == {
        "incomplete_status_exposed": "passed",
        "unavailable_family_exposed": "passed",
        "source_body_preserved": "passed",
        "professional_boundary_preserved": "passed",
        "action_reflection_degraded": "passed",
    }


def test_acceptance_status_blocks_any_failed_case():
    passed = ReportAcceptanceCaseResult(
        case_id="passed",
        scenario_type="fixture",
        status="passed",
        checks={"contract": "passed"},
    )
    failed = ReportAcceptanceCaseResult(
        case_id="failed",
        scenario_type="fixture",
        status="failed",
        checks={"contract": "failed"},
    )

    assert determine_report_acceptance_status([passed], []) == "ready"
    assert determine_report_acceptance_status([passed], ["conflict"]) == (
        "ready_with_guardrails"
    )
    assert determine_report_acceptance_status([passed, failed], []) == "blocked"


def test_acceptance_blocks_failed_calculation_validation(monkeypatch):
    monkeypatch.setattr(
        report_acceptance,
        "build_calculation_checks",
        lambda: {"stages_present": "failed"},
    )

    summary = build_report_acceptance_summary()

    assert summary.acceptance_status == "blocked"
    calculation_case = _case_by_id(summary, "calculation_validation")
    assert calculation_case.status == "failed"
    assert calculation_case.checks == {"stages_present": "failed"}
    assert summary.next_action == "resolve_failed_acceptance_cases"


def test_acceptance_uses_copy_of_precomputed_calculation_checks():
    provided = {"stages_present": "failed"}

    summary = build_report_acceptance_summary(calculation_checks=provided)
    calculation_case = _case_by_id(summary, "calculation_validation")
    provided["stages_present"] = "passed"

    assert calculation_case.checks == {"stages_present": "failed"}
    assert calculation_case.checks is not provided


def test_acceptance_summary_returns_blocked_packet_when_report_gate_fails(
    monkeypatch,
):
    blocked_activation = KnowledgeActivationSummary(
        activation_status="blocked_missing_rule_family",
        source_count=1,
        report_usable_source_count=1,
        approved_evidence_count=1,
        required_rule_families=["pattern_strength", "high_risk_signal"],
        enabled_rule_families=["pattern_strength"],
        missing_rule_families=["high_risk_signal"],
        rule_family_counts={"pattern_strength": 1},
        risk_tier_counts={"ordinary": 1},
        sources_with_gaps=[],
        open_conflicts=[],
        quality_failures=[],
        formal_conclusion_count=2,
        unavailable_conclusion_count=1,
        next_action="curate_missing_rule_family_evidence",
        guardrails=[],
    )
    monkeypatch.setattr(
        report_acceptance,
        "_build_safe_report",
        lambda: (_ for _ in ()).throw(
            KnowledgeActivationError("blocked_missing_rule_family")
        ),
    )
    monkeypatch.setattr(
        report_acceptance,
        "_load_activation_summary",
        lambda: blocked_activation,
    )

    summary = build_report_acceptance_summary()

    assert summary.acceptance_status == "blocked"
    assert summary.case_count == 1
    assert summary.passed_case_count == 0
    assert summary.activation_status == "blocked_missing_rule_family"
    assert summary.report_audit_status == "unavailable"
    assert summary.approved_evidence_count == 1
    assert summary.rule_family_count == 1
    assert summary.traced_evidence_unit_count == 0
    assert summary.missing_rule_families == ["high_risk_signal"]
    assert summary.cases[0].case_id == "ordinary_production_report"
    assert summary.cases[0].checks == {"report_construction": "failed"}
    assert summary.next_action == "curate_missing_rule_family_evidence"
