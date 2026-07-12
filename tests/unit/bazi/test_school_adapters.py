import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import MappingProxyType

import pytest

from mingli_engine.bazi.facts import build_chart_facts
from mingli_engine.bazi.patterns import calculate_pattern_candidates
from mingli_engine.bazi.result_models import (
    ReasonedResult,
    SchoolInterpretation,
)
from mingli_engine.bazi.schools import (
    DuanSchoolAdapter,
    LiangXiangrunSchoolAdapter,
    SchoolAdapter,
    SchoolProfile,
    ZipingSchoolAdapter,
    interpret_with_enabled_schools,
    load_enabled_school_adapters,
    load_school_profiles_config,
)
from mingli_engine.bazi.strength import calculate_strength
from mingli_engine.bazi.useful_gods import calculate_useful_god_candidates
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile


EXPECTED_CONFIG = {
    "version": "school-profiles-v1",
    "enabled": ["ziping", "liang_xiangrun", "duan"],
    "profiles": {
        "ziping": {
            "priority": 100,
            "method_order": [
                "support_control",
                "seasonal_adjustment",
                "mediation",
                "illness_remedy",
            ],
        },
        "liang_xiangrun": {
            "priority": 80,
            "method_order": [
                "pattern_context",
                "seasonal_adjustment",
                "support_control",
            ],
        },
        "duan": {
            "priority": 70,
            "method_order": [
                "structural_flow",
                "support_control",
                "pattern_context",
            ],
        },
    },
}


def pipeline_case(birth_date: str = "1992-08-18"):
    chart = calculate_bazi_chart(
        BirthProfile(
            calendar_type="gregorian",
            birth_date=birth_date,
            birth_time="09:30",
            birthplace="Shanghai",
            gender="unspecified",
            focus_topic="structure",
        )
    )
    facts = build_chart_facts(chart)
    strength = calculate_strength(facts)
    patterns = calculate_pattern_candidates(facts, strength)
    useful_gods = calculate_useful_god_candidates(facts, strength, patterns)
    return facts, strength, patterns, useful_gods


def write_config(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / "school_profiles.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_tracked_school_profile_json_is_exact_and_deeply_immutable() -> None:
    config_path = (
        Path(__file__).parents[3]
        / "src"
        / "mingli_engine"
        / "data"
        / "calculation"
        / "school_profiles.json"
    )
    assert json.loads(config_path.read_text(encoding="utf-8")) == EXPECTED_CONFIG

    config = load_school_profiles_config()
    assert config.version == "school-profiles-v1"
    assert config.enabled == ("ziping", "liang_xiangrun", "duan")
    assert isinstance(config.profiles, MappingProxyType)
    assert config.profiles["ziping"].method_order == (
        "support_control",
        "seasonal_adjustment",
        "mediation",
        "illness_remedy",
    )
    with pytest.raises(FrozenInstanceError):
        config.version = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        config.profiles["ziping"] = config.profiles["duan"]  # type: ignore[index]
    with pytest.raises(TypeError):
        config.profiles["ziping"].method_order[0] = "changed"  # type: ignore[index]


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda value: value.update(extra=True), "top-level keys"),
        (lambda value: value.__setitem__("version", "v2"), "version"),
        (lambda value: value.__setitem__("enabled", []), "enabled"),
        (
            lambda value: value.__setitem__("enabled", ["ziping", "ziping", "duan"]),
            "unique",
        ),
        (
            lambda value: value.__setitem__("enabled", ["ziping", "unknown", "duan"]),
            "known",
        ),
        (lambda value: value["profiles"].pop("duan"), "profile ids"),
        (
            lambda value: value["profiles"].__setitem__(
                "unknown", {"priority": 1, "method_order": ["support_control"]}
            ),
            "profile ids",
        ),
        (
            lambda value: value["profiles"]["ziping"].update(extra=True),
            "profile keys",
        ),
        (
            lambda value: value["profiles"]["ziping"].__setitem__("priority", True),
            "positive integer",
        ),
        (
            lambda value: value["profiles"]["ziping"].__setitem__("priority", 0),
            "positive integer",
        ),
        (
            lambda value: value["profiles"]["duan"].__setitem__("priority", 80),
            "unique",
        ),
        (
            lambda value: value["profiles"]["ziping"].__setitem__("method_order", []),
            "nonempty",
        ),
        (
            lambda value: value["profiles"]["ziping"].__setitem__(
                "method_order", ["support_control", "support_control"]
            ),
            "unique",
        ),
        (
            lambda value: value["profiles"]["ziping"].__setitem__(
                "method_order", ["structural_flow"]
            ),
            "ziping",
        ),
        (
            lambda value: value["profiles"]["duan"].__setitem__(
                "method_order", ["unknown_method"]
            ),
            "method",
        ),
    ],
)
def test_school_profile_validation_boundaries(
    tmp_path: Path, mutate, message: str
) -> None:
    payload = json.loads(json.dumps(EXPECTED_CONFIG))
    mutate(payload)
    with pytest.raises(ValueError, match=message):
        load_school_profiles_config(write_config(tmp_path, payload))


def test_school_profile_loader_reports_read_and_json_errors(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="read school profiles"):
        load_school_profiles_config(tmp_path / "missing.json")
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="parse school profiles JSON"):
        load_school_profiles_config(bad_json)


def test_loader_returns_runtime_protocol_adapters_in_priority_order() -> None:
    adapters = load_enabled_school_adapters()
    assert tuple(type(item) for item in adapters) == (
        ZipingSchoolAdapter,
        LiangXiangrunSchoolAdapter,
        DuanSchoolAdapter,
    )
    assert tuple(item.school_id for item in adapters) == (
        "ziping",
        "liang_xiangrun",
        "duan",
    )
    assert all(isinstance(item, SchoolAdapter) for item in adapters)
    assert all(item.profile_version == "school-profiles-v1" for item in adapters)


def test_ziping_preserves_full_baseline_order_and_method_order() -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    result = load_enabled_school_adapters()[0].interpret(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )

    assert result.preferred_pattern_ids == tuple(item.pattern_id for item in patterns)
    expected_elements = []
    for method in EXPECTED_CONFIG["profiles"]["ziping"]["method_order"]:
        for item in useful_gods:
            if item.method == method and item.element not in expected_elements:
                expected_elements.append(item.element)
    expected_elements = [item for item in expected_elements if item]
    assert result.preferred_useful_god_elements == tuple(expected_elements)
    assert result.reasoning.status == "indeterminate"
    assert "school.ziping.baseline_rank" in result.reasoning.rule_ids
    assert any("follow.congruo" in item for item in result.reasoning.opposing_signals)


def test_ziping_orders_computed_preferences_before_disputed_candidates() -> None:
    facts, strength, patterns, useful_gods = pipeline_case("1980-06-15")
    assert any(
        item.element and item.reasoning.status == "disputed" for item in useful_gods
    )
    profile = SchoolProfile(
        school_id="ziping",
        priority=100,
        method_order=(
            "illness_remedy",
            "support_control",
            "seasonal_adjustment",
            "mediation",
        ),
    )
    result = ZipingSchoolAdapter(profile, "school-profiles-v1").interpret(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )

    expected = tuple(
        dict.fromkeys(
            item.element
            for item in sorted(
                (item for item in useful_gods if item.element),
                key=lambda item: (
                    item.reasoning.status != "computed",
                    profile.method_order.index(item.method),
                    item.rank,
                ),
            )
        )
    )
    assert result.preferred_useful_god_elements == expected


def test_liang_uses_only_exposed_patterns_then_computed_seasonal_and_support() -> None:
    facts, strength, patterns, useful_gods = pipeline_case("1991-01-18")
    result = load_enabled_school_adapters()[1].interpret(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )

    expected_patterns = tuple(
        item.pattern_id
        for item in patterns
        if item.reasoning.status == "computed"
        and any(value.startswith("exposed:") for value in item.formation_conditions)
    )
    assert result.preferred_pattern_ids == expected_patterns
    selected = tuple(
        item
        for method in ("seasonal_adjustment", "support_control")
        for item in useful_gods
        if item.method == method
        and item.reasoning.status == "computed"
        and item.element
    )
    assert result.preferred_useful_god_elements == tuple(
        dict.fromkeys(item.element for item in selected)
    )
    assert all(item.method != "mediation" for item in selected)
    assert "school.liang_xiangrun.exposed_pattern_context" in result.reasoning.rule_ids
    assert any("excluded" in item for item in result.reasoning.assumptions)


def test_duan_requires_explicit_conditions_counterconditions_and_provenance() -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    positive = load_enabled_school_adapters()[2].interpret(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    qualifying = tuple(
        item.pattern_id
        for item in patterns
        if item.formation_conditions and item.damage_conditions
    )
    contextual = tuple(
        item.pattern_id
        for item in patterns
        if item.formation_conditions and item.pattern_id not in qualifying
    )
    assert positive.preferred_pattern_ids == (*qualifying, *contextual)
    assert positive.preferred_useful_god_elements
    assert "school.duan.structural_flow" in positive.reasoning.rule_ids
    assert any(
        "formation_condition" in item for item in positive.reasoning.supporting_signals
    )
    assert any(
        "countercondition" in item for item in positive.reasoning.opposing_signals
    )

    no_counter_facts, no_counter_strength, no_counter_patterns, no_counter_useful = (
        pipeline_case("1988-03-15")
    )
    assert all(not item.damage_conditions for item in no_counter_patterns)
    negative = load_enabled_school_adapters()[2].interpret(
        facts=no_counter_facts,
        strength=no_counter_strength,
        patterns=no_counter_patterns,
        useful_gods=no_counter_useful,
    )
    assert negative.reasoning.status == "not_computed"
    assert negative.preferred_pattern_ids == ()
    assert negative.preferred_useful_god_elements == ()
    assert "structural_counterconditions" in negative.reasoning.missing_inputs


def test_direct_adapter_rejects_forged_empty_useful_preferences() -> None:
    facts, strength, patterns, useful_gods = pipeline_case("1988-03-15")
    no_useful = tuple(
        replace(
            item,
            element="",
            reasoning=replace(
                item.reasoning,
                status="not_computed",
                confidence="low",
            ),
        )
        for item in useful_gods
    )
    with pytest.raises(ValueError, match="duplicate useful-god|canonical useful-god"):
        ZipingSchoolAdapter(
            load_school_profiles_config().profiles["ziping"], "school-profiles-v1"
        ).interpret(
            facts=facts,
            strength=strength,
            patterns=patterns,
            useful_gods=no_useful,
        )


@pytest.mark.parametrize(
    "forge",
    [
        lambda patterns, useful: (patterns + (patterns[0],), useful),
        lambda patterns, useful: (
            (replace(patterns[0], rank=2), *patterns[1:]),
            useful,
        ),
        lambda patterns, useful: (
            patterns,
            useful + (useful[0],),
        ),
        lambda patterns, useful: (
            patterns,
            (replace(useful[0], rank=2), *useful[1:]),
        ),
        lambda patterns, useful: (
            patterns,
            (replace(useful[0], element="invalid"), *useful[1:]),
        ),
    ],
)
def test_direct_adapter_rejects_duplicate_rank_and_forged_inputs(forge) -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    forged_patterns, forged_useful = forge(patterns, useful_gods)
    with pytest.raises(ValueError):
        load_enabled_school_adapters()[0].interpret(
            facts=facts,
            strength=strength,
            patterns=tuple(forged_patterns),
            useful_gods=tuple(forged_useful),
        )


def test_aggregation_preserves_preferences_and_marks_only_real_disagreement() -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    first = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    second = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )

    assert first == second
    assert tuple(item.school_id for item in first) == (
        "ziping",
        "liang_xiangrun",
        "duan",
    )
    assert first[0].preferred_pattern_ids == tuple(item.pattern_id for item in patterns)
    assert all(item.reasoning.status == "disputed" for item in first)
    assert all(
        "school.cross_school_disagreement.pattern_preferences"
        in item.reasoning.rule_ids
        for item in first
    )
    assert all(
        any(
            signal.startswith("cross_school_disagreement:pattern_preferences:")
            for signal in item.reasoning.opposing_signals
        )
        for item in first
    )


def test_aggregation_does_not_promote_not_computed_or_allow_adapter_suppression() -> (
    None
):
    facts, strength, patterns, useful_gods = pipeline_case()

    class EmptyAdapter:
        school_id = "empty"
        profile_version = "school-profiles-v1"

        def interpret(self, *, facts, strength, patterns, useful_gods):
            return SchoolInterpretation(
                school_id=self.school_id,
                profile_version=self.profile_version,
                reasoning=ReasonedResult(
                    status="not_computed",
                    conclusion="no supported preference",
                    confidence="low",
                    missing_inputs=("reviewed_rules",),
                    rule_ids=("school.empty.no_supported_preference",),
                ),
                preferred_pattern_ids=(),
                preferred_useful_god_elements=(),
            )

    adapters = (EmptyAdapter(), *load_enabled_school_adapters())
    results = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=adapters,
    )
    assert len(results) == 4
    assert results[0].school_id == "empty"
    assert results[0].reasoning.status == "not_computed"
    assert results[0].preferred_pattern_ids == ()
    assert tuple(item.school_id for item in results[1:]) == (
        "ziping",
        "liang_xiangrun",
        "duan",
    )


def test_inputs_are_frozen_and_never_mutated_by_direct_or_aggregate_calls() -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    snapshot = (facts, strength, patterns, useful_gods)
    with pytest.raises(FrozenInstanceError):
        facts.day_master = "forged"  # type: ignore[misc]
    with pytest.raises(TypeError):
        patterns[0].formation_conditions[0] = "forged"  # type: ignore[index]

    for adapter in load_enabled_school_adapters():
        adapter.interpret(
            facts=facts,
            strength=strength,
            patterns=patterns,
            useful_gods=useful_gods,
        )
    interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    assert (facts, strength, patterns, useful_gods) == snapshot


def test_real_chart_pipeline_reaches_all_school_adapters() -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    results = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    assert facts.day_master
    assert strength.reasoning.status == "computed"
    assert patterns
    assert useful_gods
    assert len(results) == 3
    assert all(item.profile_version == "school-profiles-v1" for item in results)
