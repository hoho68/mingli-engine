from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime

import pytest

from mingli_engine.bazi.analysis import analyze_bazi_chart
from mingli_engine.bazi.calibrated_families import (
    calculate_blind_image_method,
    calculate_remedy_boundary,
    calculate_taboo_god_candidates,
)
from mingli_engine.bazi.result_models import (
    BlindImageResult,
    BlindImageSignal,
    ReasonedResult,
    RemedyBoundaryResult,
    TabooGodCandidate,
    TabooGodResult,
)
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile


def _bundle():
    profile = BirthProfile(
        calendar_type="gregorian",
        birth_date="1996-12-15",
        birth_time="09:30",
        birthplace="Synthetic UTC+08 Place",
        gender="unknown",
        focus_topic="traditional structural overview",
    )
    chart = calculate_bazi_chart(profile)
    bundle = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1996, 12, 15, 9, 30),
    )
    return chart, bundle


def _reasoning(status: str = "computed") -> ReasonedResult:
    return ReasonedResult(
        status=status,  # type: ignore[arg-type]
        conclusion="family result",
        confidence="medium",
        rule_ids=("family.rule",),
    )


def test_calibrated_family_dtos_are_frozen_and_have_exact_fields() -> None:
    assert tuple(item.name for item in fields(TabooGodCandidate)) == (
        "element",
        "rank",
        "pressure_score",
        "reasons",
    )
    assert tuple(item.name for item in fields(TabooGodResult)) == (
        "reasoning",
        "candidates",
        "evidence_ids",
    )
    assert tuple(item.name for item in fields(BlindImageSignal)) == (
        "image_id",
        "category",
        "value",
        "structural_signals",
    )
    assert tuple(item.name for item in fields(BlindImageResult)) == (
        "reasoning",
        "images",
        "evidence_ids",
    )
    assert tuple(item.name for item in fields(RemedyBoundaryResult)) == (
        "reasoning",
        "conditions",
        "applicable_boundaries",
        "stop_conditions",
        "evidence_ids",
    )

    candidate = TabooGodCandidate("fire", 1, 3.0, ("pressure",))
    with pytest.raises(FrozenInstanceError):
        candidate.rank = 2  # type: ignore[misc]


def test_calibrated_family_dtos_normalize_tuples_and_reject_invalid_types() -> None:
    candidate = TabooGodCandidate("fire", 1, 3.0, ["pressure"])  # type: ignore[arg-type]
    assert candidate.reasons == ("pressure",)
    assert isinstance(candidate.reasons, tuple)

    with pytest.raises(TypeError):
        TabooGodCandidate(1, 1, 3.0, ("pressure",))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        BlindImageResult(_reasoning(), ("not-a-signal",), ())  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        RemedyBoundaryResult(_reasoning(), (1,), (), (), ())  # type: ignore[arg-type]


def test_analysis_bundle_contains_three_independent_family_results() -> None:
    _chart, bundle = _bundle()

    assert isinstance(bundle.taboo_gods, TabooGodResult)
    assert isinstance(bundle.blind_images, BlindImageResult)
    assert isinstance(bundle.remedy_boundary, RemedyBoundaryResult)
    assert bundle.taboo_gods.candidates
    assert bundle.blind_images.images
    assert bundle.remedy_boundary.applicable_boundaries
    assert bundle.taboo_gods.evidence_ids
    assert bundle.blind_images.evidence_ids
    assert bundle.remedy_boundary.evidence_ids


def test_taboo_god_uses_structural_pressure_not_useful_god_inverse() -> None:
    _chart, bundle = _bundle()
    result = calculate_taboo_god_candidates(
        bundle.facts,
        bundle.strength,
        bundle.patterns,
        bundle.schools,
    )
    useful_elements = tuple(dict.fromkeys(item.element for item in bundle.useful_gods))
    candidate_elements = tuple(item.element for item in result.candidates)

    assert result.reasoning.status in {"computed", "indeterminate", "disputed"}
    assert candidate_elements != tuple(reversed(useful_elements))
    assert all(item.reasons for item in result.candidates)
    assert all(item.rank == index for index, item in enumerate(result.candidates, 1))
    assert result.reasoning.rule_ids
    assert all(rule_id.startswith("taboo.") for rule_id in result.reasoning.rule_ids)


def test_taboo_god_reports_missing_prerequisite_and_boundary_conflict() -> None:
    _chart, bundle = _bundle()
    missing_strength = replace(
        bundle.strength,
        reasoning=replace(bundle.strength.reasoning, status="not_computed"),
    )
    missing = calculate_taboo_god_candidates(
        bundle.facts,
        missing_strength,
        bundle.patterns,
        bundle.schools,
    )
    assert missing.reasoning.status == "not_computed"
    assert missing.candidates == ()

    uncertain_strength = replace(
        bundle.strength,
        reasoning=replace(bundle.strength.reasoning, status="indeterminate"),
    )
    uncertain = calculate_taboo_god_candidates(
        bundle.facts,
        uncertain_strength,
        bundle.patterns,
        bundle.schools,
    )
    assert uncertain.reasoning.status == "indeterminate"


def test_blind_image_uses_structural_facts_not_school_aggregate() -> None:
    _chart, bundle = _bundle()
    result = calculate_blind_image_method(
        bundle.facts,
        bundle.branch_relations,
        bundle.strength,
        bundle.schools,
    )
    school_text = "|".join(
        item.school_id + ":" + ",".join(item.preferred_pattern_ids)
        for item in bundle.schools
    )

    assert result.reasoning.status in {"computed", "disputed"}
    assert result.images
    assert all(item.structural_signals for item in result.images)
    assert all(item.value not in school_text for item in result.images)
    assert all(rule_id.startswith("blind.image.") for rule_id in result.reasoning.rule_ids)


def test_blind_image_is_indeterminate_without_structural_signal() -> None:
    _chart, bundle = _bundle()
    facts = replace(bundle.facts, roots=())
    result = calculate_blind_image_method(
        facts,
        (),
        bundle.strength,
        bundle.schools,
    )
    assert result.reasoning.status == "indeterminate"
    assert result.images == ()


def test_remedy_boundary_is_dedicated_output_not_useful_god_copy() -> None:
    _chart, bundle = _bundle()
    result = calculate_remedy_boundary(
        bundle.strength,
        bundle.useful_gods,
        bundle.schools,
    )
    useful_elements = {item.element for item in bundle.useful_gods}

    assert result.reasoning.status in {"computed", "indeterminate", "disputed"}
    assert result.conditions
    assert result.applicable_boundaries
    assert result.stop_conditions
    assert not useful_elements.intersection(result.applicable_boundaries)
    assert all(rule_id.startswith("remedy.boundary.") for rule_id in result.reasoning.rule_ids)


def test_remedy_boundary_reports_missing_and_conflicting_prerequisites() -> None:
    _chart, bundle = _bundle()
    unavailable = tuple(
        replace(
            item,
            reasoning=replace(item.reasoning, status="not_computed"),
        )
        for item in bundle.useful_gods
    )
    missing = calculate_remedy_boundary(
        bundle.strength,
        unavailable,
        bundle.schools,
    )
    assert missing.reasoning.status == "not_computed"
    assert missing.applicable_boundaries == ()

    disputed = calculate_remedy_boundary(
        bundle.strength,
        bundle.useful_gods,
        bundle.schools,
    )
    assert disputed.reasoning.status == "disputed"
    assert "remedy.boundary.school_disagreement" in disputed.reasoning.rule_ids
