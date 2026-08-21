from dataclasses import replace
from datetime import datetime

import pytest

from mingli_engine.bazi import analyze_bazi_chart
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.formal_interpretation import (
    _family_reasoning,
    classify_chart_calculation_states,
)
from mingli_engine.models import BirthProfile
from mingli_engine.report_schema import build_report


def _calculation_chart(chart):
    return calculate_bazi_chart(chart.birth_profile)


def _analyzed_bundle(birth_date: str):
    profile = BirthProfile(
        calendar_type="gregorian",
        birth_date=birth_date,
        birth_time="09:30",
        birthplace="Shanghai",
        gender="female",
        focus_topic="career",
    )
    chart = calculate_bazi_chart(profile)
    calculation = analyze_bazi_chart(
        chart,
        birth_datetime=datetime.fromisoformat(f"{birth_date}T09:30"),
        selected_year=2030,
    )
    return chart, calculation


@pytest.mark.parametrize(
    ("birth_date", "expected"),
    [
        (
            "1950-03-22",
            {
                "pattern_strength": "disputed",
                "five_element_balance": "computed",
                "useful_god_candidate": "disputed",
                "taboo_god_candidate": "computed",
                "ten_god_relation": "computed",
                "branch_interaction": "computed",
                "blind_image_method": "computed",
                "luck_cycle": "computed",
                "remedy_boundary": "computed",
                "high_risk_signal": "not_computed",
            },
        ),
        (
            "1950-03-25",
            {
                "pattern_strength": "computed",
                "five_element_balance": "computed",
                "useful_god_candidate": "indeterminate",
                "taboo_god_candidate": "computed",
                "ten_god_relation": "computed",
                "branch_interaction": "computed",
                "blind_image_method": "computed",
                "luck_cycle": "computed",
                "remedy_boundary": "indeterminate",
                "high_risk_signal": "not_computed",
            },
        ),
    ],
)
def test_real_bundles_have_exact_conservative_family_status_maps(
    birth_date,
    expected,
):
    chart, calculation = _analyzed_bundle(birth_date)

    assert classify_chart_calculation_states(calculation) == expected
    report = build_report(chart, calculation)
    assert {
        conclusion.rule_family: conclusion.trace.calculation_status
        for conclusion in report.expanded_evidence.formal_conclusions
    } == expected


def test_real_structural_facts_and_relations_become_computed_candidates():
    chart, calculation = _analyzed_bundle("1950-03-22")
    assert calculation.branch_relations

    ten_gods = _family_reasoning(calculation, "ten_god_relation")
    branches = _family_reasoning(calculation, "branch_interaction")
    report = build_report(chart, calculation)

    assert ten_gods.status == "computed"
    assert ten_gods.confidence == "high"
    assert ten_gods.assumptions == calculation.facts.assumptions
    assert ten_gods.rule_ids == (
        "facts.ten_god.exposed",
        "facts.ten_god.hidden",
    )
    assert {
        f"{fact.pillar_name}:exposed:{fact.stem}:{fact.ten_god}"
        for fact in calculation.facts.exposed_stems
    }.issubset(set(ten_gods.supporting_signals))
    assert branches.status == "computed"
    assert branches.confidence == "high"
    assert branches.rule_ids == tuple(
        dict.fromkeys(relation.rule_id for relation in calculation.branch_relations)
    )
    assert len(branches.supporting_signals) == len(calculation.branch_relations)
    for rule_family in ("ten_god_relation", "branch_interaction"):
        conclusion = _formal_family(report, rule_family)
        assert conclusion.trace.calculation_status == "computed"
        assert conclusion.strength == "candidate"
        assert conclusion.trace.evidence_ids


def test_real_empty_relation_stage_is_computed_with_explicit_none_detected_signal():
    chart, calculation = _analyzed_bundle("1950-01-06")
    assert calculation.branch_relations == ()

    reasoning = _family_reasoning(calculation, "branch_interaction")
    report = build_report(chart, calculation)
    conclusion = _formal_family(report, "branch_interaction")

    assert reasoning.status == "computed"
    assert reasoning.conclusion == "no branch relations detected"
    assert reasoning.supporting_signals == ("no branch relations detected",)
    assert reasoning.rule_ids == ("branch.relation.none_detected",)
    assert conclusion.trace.calculation_status == "computed"
    assert conclusion.strength == "candidate"
    assert conclusion.trace.evidence_ids


@pytest.mark.parametrize("empty_field", ["exposed_stems", "hidden_stems"])
def test_empty_structural_fact_rows_are_indeterminate(empty_field):
    _chart, calculation = _analyzed_bundle("1950-03-22")
    incomplete_facts = replace(calculation.facts, **{empty_field: ()})
    incomplete = replace(calculation, facts=incomplete_facts)

    reasoning = _family_reasoning(incomplete, "ten_god_relation")

    assert reasoning.status == "indeterminate"
    assert reasoning.confidence == "low"
    assert reasoning.missing_inputs == (
        "canonical_exposed_and_hidden_ten_god_facts",
    )
    assert reasoning.rule_ids == ("facts.ten_god.canonical_structure",)


def _formal_family(report, rule_family: str):
    return next(
        conclusion
        for conclusion in report.expanded_evidence.formal_conclusions
        if conclusion.rule_family == rule_family
    )


def _school_view_signals(conclusion):
    return conclusion.trace.school_views


def test_disputed_calculation_without_family_school_rule_has_no_school_note():
    chart, calculation = _analyzed_bundle("1950-03-22")

    report = build_report(chart, calculation)

    for rule_family in (
        "pattern_strength",
        "useful_god_candidate",
    ):
        conclusion = _formal_family(report, rule_family)
        assert conclusion.strength == "disputed"
        assert "School calculation disagreement preserved" not in (
            conclusion.trace.disagreement_note
        )
        views = _school_view_signals(conclusion)
        assert len(views) == len(calculation.schools)
    pattern_views = _school_view_signals(_formal_family(report, "pattern_strength"))
    assert all(":patterns=" in view for view in pattern_views)
    assert all(":useful_gods=" not in view for view in pattern_views)
    useful_views = _school_view_signals(
        _formal_family(report, "useful_god_candidate")
    )
    assert all(":useful_gods=" in view for view in useful_views)
    assert all(":patterns=" not in view for view in useful_views)
    blind = _formal_family(report, "blind_image_method")
    assert blind.strength == "candidate"
    assert blind.trace.calculation_status == "computed"
    assert "School calculation disagreement preserved" not in (
        blind.trace.disagreement_note
    )
    blind_views = _school_view_signals(blind)
    assert all(":patterns=" not in view for view in blind_views)
    assert all(":useful_gods=" not in view for view in blind_views)


def test_useful_god_school_rule_projects_only_useful_god_views():
    chart, calculation = _analyzed_bundle("1950-01-01")

    report = build_report(chart, calculation)

    pattern = _formal_family(report, "pattern_strength")
    useful = _formal_family(report, "useful_god_candidate")
    remedy = _formal_family(report, "remedy_boundary")
    blind = _formal_family(report, "blind_image_method")
    assert "School calculation disagreement preserved" not in (
        pattern.trace.disagreement_note
    )
    assert "School calculation disagreement preserved" not in (
        blind.trace.disagreement_note
    )
    for conclusion in (useful, remedy):
        assert "School calculation disagreement preserved" in (
            conclusion.trace.disagreement_note
        )
        views = _school_view_signals(conclusion)
        assert len(views) == len(calculation.schools)
        assert all(":useful_gods=" in view for view in views)
        assert all(":patterns=" not in view for view in views)
        for school in calculation.schools:
            assert f"school_view:{school.school_id}:" in (
                conclusion.trace.disagreement_note
            )


def test_reasoned_calculation_reaches_formal_evidence_and_audit(sample_bazi_chart):
    chart = _calculation_chart(sample_bazi_chart)
    calculation = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1990, 1, 1, 8, 30),
        selected_year=2030,
    )

    report = build_report(chart, calculation)

    conclusions = {
        item.rule_family: item for item in report.expanded_evidence.formal_conclusions
    }
    audit = report.report_evidence_audit
    assert len(conclusions) == 10
    assert audit.traced_evidence_unit_count == 996
    assert (
        audit.computed_rule_family_count
        + audit.indeterminate_rule_family_count
        + audit.disputed_rule_family_count
        + audit.not_computed_rule_family_count
        == 10
    )
    assert conclusions["luck_cycle"].strength in {"candidate", "disputed"}
    assert conclusions["luck_cycle"].trace.calculation_status == "computed"
    assert conclusions["taboo_god_candidate"].strength == "weakly_supported"
    assert conclusions["taboo_god_candidate"].trace.calculation_status == (
        "indeterminate"
    )
    school_views = conclusions["blind_image_method"].trace.school_views
    assert {view.split(":", 2)[1] for view in school_views} == {
        item.school_id for item in calculation.schools
    }
    assert not any(
        signal.startswith("school_view:")
        for conclusion in conclusions.values()
        for signal in conclusion.trace.chart_signals
    )
    assert report.knowledge_activation.open_conflicts


def test_reasoned_report_keeps_approved_evidence_and_guardrails(sample_bazi_chart):
    chart = _calculation_chart(sample_bazi_chart)
    calculation = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1990, 1, 1, 8, 30),
        selected_year=2030,
    )

    report = build_report(chart, calculation)

    evidence_ids = {
        evidence_id
        for conclusion in report.expanded_evidence.formal_conclusions
        for evidence_id in conclusion.trace.evidence_ids
    }
    assert len(evidence_ids) == 996
    assert report.expanded_evidence.high_risk_notes
    assert report.report_evidence_audit.guardrail_count > 0
    assert report.safety_review.disclaimer_present is True
