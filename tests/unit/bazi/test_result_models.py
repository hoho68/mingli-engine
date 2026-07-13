from dataclasses import FrozenInstanceError, fields, is_dataclass
from typing import get_origin

import pytest

from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    CalculationBundle,
    ChartFacts,
    HiddenStemFact,
    LuckCycleResult,
    LuckPillar,
    PatternCandidateResult,
    ReasonedResult,
    RootFact,
    SchoolInterpretation,
    StemFact,
    StrengthContribution,
    StrengthResult,
    UsefulGodCandidateResult,
)


def test_reasoned_result_exposes_separate_status_and_trace_fields():
    result = ReasonedResult(
        status="indeterminate",
        conclusion="day-master strength is near a classification boundary",
        confidence="low",
        supporting_signals=("month_command:resource",),
        opposing_signals=("root:none",),
        assumptions=("ruleset:ziping-v1",),
        missing_inputs=(),
        rule_ids=("strength.month_command.resource",),
    )

    assert result.status == "indeterminate"
    assert result.supporting_signals == ("month_command:resource",)
    assert result.opposing_signals == ("root:none",)
    assert result.assumptions == ("ruleset:ziping-v1",)
    assert result.missing_inputs == ()
    assert result.rule_ids == ("strength.month_command.resource",)
    with pytest.raises(FrozenInstanceError):
        result.status = "computed"


def test_reasoned_result_rejects_unknown_status():
    with pytest.raises(ValueError, match="unsupported computation status"):
        ReasonedResult(
            status="candidate",
            conclusion="",
            confidence="low",
        )


def test_reasoned_result_rejects_unknown_confidence():
    with pytest.raises(ValueError, match="unsupported confidence"):
        ReasonedResult(
            status="computed",
            conclusion="",
            confidence="certain",
        )


def test_result_model_fields_match_the_calculation_protocol():
    expected_fields = {
        StemFact: ("pillar_name", "stem", "element", "polarity", "ten_god"),
        HiddenStemFact: (
            "pillar_name",
            "branch",
            "stem",
            "role",
            "element",
            "polarity",
            "ten_god",
        ),
        RootFact: (
            "stem",
            "stem_pillar",
            "branch",
            "branch_pillar",
            "role",
            "exact_stem_root",
        ),
        ChartFacts: (
            "day_master",
            "month_branch",
            "exposed_stems",
            "hidden_stems",
            "roots",
            "twelve_growth_by_pillar",
            "assumptions",
        ),
        BranchRelationResult: (
            "relation_type",
            "branches",
            "pillar_names",
            "state",
            "transformed_element",
            "conditions",
            "blockers",
            "rule_id",
        ),
        StrengthContribution: ("category", "signal", "value", "rule_id"),
        StrengthResult: (
            "reasoning",
            "score",
            "lower_bound",
            "upper_bound",
            "label",
            "contributions",
        ),
        PatternCandidateResult: (
            "pattern_id",
            "name",
            "rank",
            "reasoning",
            "formation_conditions",
            "damage_conditions",
            "rescue_conditions",
        ),
        UsefulGodCandidateResult: ("method", "element", "rank", "reasoning"),
        LuckPillar: (
            "index",
            "gan_zhi",
            "start_year",
            "end_year",
            "start_age",
            "end_age",
        ),
        LuckCycleResult: (
            "reasoning",
            "forward",
            "start_years",
            "start_months",
            "start_days",
            "start_solar",
            "pillars",
            "selected_year_relations",
        ),
        SchoolInterpretation: (
            "school_id",
            "profile_version",
            "reasoning",
            "preferred_pattern_ids",
            "preferred_useful_god_elements",
        ),
        CalculationBundle: (
            "engine_version",
            "ruleset_version",
            "facts",
            "branch_relations",
            "strength",
            "patterns",
            "useful_gods",
            "luck_cycles",
            "schools",
            "taboo_gods",
            "blind_images",
            "remedy_boundary",
        ),
    }

    for model, names in expected_fields.items():
        assert tuple(field.name for field in fields(model)) == names


def test_luck_cycle_selected_year_relations_has_immutable_empty_default():
    reasoning = ReasonedResult(
        status="not_computed",
        conclusion="",
        confidence="low",
    )

    first = LuckCycleResult(reasoning, False, 0, 0, 0, "", ())
    second = LuckCycleResult(reasoning, False, 0, 0, 0, "", ())

    assert first.selected_year_relations == ()
    assert second.selected_year_relations == ()
    with pytest.raises(FrozenInstanceError):
        first.pillars = ()


def test_result_models_recursively_normalize_sequence_inputs():
    supporting_signals = ["month_command:resource"]
    growth_pair = ["year", "growth"]
    growth_rows = [growth_pair]
    reasoning = ReasonedResult(
        status="computed",
        conclusion="string conclusions stay strings",
        confidence="high",
        supporting_signals=supporting_signals,
        opposing_signals=[],
        assumptions=[],
        missing_inputs=[],
        rule_ids=["strength.month_command.resource"],
    )
    stem = StemFact("year", "stem", "wood", "yang", "companion")
    hidden_stem = HiddenStemFact(
        "year", "branch", "stem", "main", "wood", "yang", "companion"
    )
    root = RootFact("stem", "year", "branch", "year", "main", True)
    facts = ChartFacts(
        "stem",
        "branch",
        [stem],
        [hidden_stem],
        [root],
        growth_rows,
        ["timezone:local"],
    )
    relation = BranchRelationResult(
        "combination",
        ["branch", "other"],
        ["year", "month"],
        "present",
        "",
        ["both-present"],
        [],
        "branch.combination",
    )
    contribution = StrengthContribution(
        "month_command", "resource", 24.0, "strength.month_command.resource"
    )
    strength = StrengthResult(reasoning, 24.0, 21.6, 26.4, "strong", [contribution])
    pattern = PatternCandidateResult(
        "pattern",
        "Pattern",
        1,
        reasoning,
        ["formed"],
        [],
        [],
    )
    useful_god = UsefulGodCandidateResult("balancing", "water", 1, reasoning)
    pillar = LuckPillar(1, "stem-branch", 2030, 2039, 10, 19)
    luck_cycles = LuckCycleResult(
        reasoning,
        True,
        1,
        2,
        3,
        "2030-01-01",
        [pillar],
        [relation],
    )
    school = SchoolInterpretation(
        "ziping", "v1", reasoning, ["pattern"], ["water"]
    )
    bundle = CalculationBundle(
        "1.0",
        "rules-v1",
        facts,
        [relation],
        strength,
        [pattern],
        [useful_god],
        luck_cycles,
        [school],
    )

    def assert_tuple_annotations_are_normalized(value):
        if not is_dataclass(value):
            return
        for model_field in fields(value):
            field_value = getattr(value, model_field.name)
            if get_origin(model_field.type) is tuple:
                assert isinstance(field_value, tuple)
                for item in field_value:
                    assert_tuple_annotations_are_normalized(item)
            else:
                assert_tuple_annotations_are_normalized(field_value)

    assert_tuple_annotations_are_normalized(bundle)
    supporting_signals.append("root:main")
    growth_pair.append("mutated")
    growth_rows.append(["month", "growth"])

    assert reasoning.supporting_signals == ("month_command:resource",)
    assert facts.twelve_growth_by_pillar == (("year", "growth"),)
    assert reasoning.conclusion == "string conclusions stay strings"
    assert isinstance(hash(bundle), int)
