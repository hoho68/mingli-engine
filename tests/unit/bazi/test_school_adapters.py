import json
import operator
from collections.abc import Callable, MutableMapping
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import MappingProxyType
from typing import TypedDict, cast

import pytest

from mingli_engine.bazi.facts import build_chart_facts
from mingli_engine.bazi.patterns import calculate_pattern_candidates
from mingli_engine.bazi.result_models import (
    ChartFacts,
    PatternCandidateResult,
    ReasonedResult,
    SchoolInterpretation,
    StrengthResult,
    UsefulGodCandidateResult,
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
from mingli_engine.bazi.schools.base import SchoolAdapterBase
from mingli_engine.bazi.strength import calculate_strength
from mingli_engine.bazi.useful_gods import calculate_useful_god_candidates
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile


class ProfilePayload(TypedDict):
    priority: int
    method_order: list[str]


class SchoolProfilesPayload(TypedDict):
    version: str
    enabled: list[str]
    profiles: dict[str, ProfilePayload]


PipelineCase = tuple[
    ChartFacts,
    StrengthResult,
    tuple[PatternCandidateResult, ...],
    tuple[UsefulGodCandidateResult, ...],
]
SchoolResultForge = Callable[[SchoolInterpretation], SchoolInterpretation]
InputForge = Callable[
    [
        tuple[PatternCandidateResult, ...],
        tuple[UsefulGodCandidateResult, ...],
    ],
    tuple[
        tuple[PatternCandidateResult, ...],
        tuple[UsefulGodCandidateResult, ...],
    ],
]
ConfigMutation = Callable[[dict[str, object]], None]


EXPECTED_CONFIG: SchoolProfilesPayload = {
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


def pipeline_case(birth_date: str = "1992-08-18") -> PipelineCase:
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


class ReturningAdapter:
    profile_version = "school-profiles-v1"

    def __init__(self, school_id: str, result: SchoolInterpretation) -> None:
        self.school_id = school_id
        self.result = result

    def interpret(
        self,
        *,
        facts: ChartFacts,
        strength: StrengthResult,
        patterns: tuple[PatternCandidateResult, ...],
        useful_gods: tuple[UsefulGodCandidateResult, ...],
    ) -> SchoolInterpretation:
        return self.result


def valid_fake_result(
    *,
    school_id: str,
    pattern_id: str,
    element: str = "",
) -> SchoolInterpretation:
    return SchoolInterpretation(
        school_id=school_id,
        profile_version="school-profiles-v1",
        reasoning=ReasonedResult(
            status="computed",
            conclusion="validated fake preference",
            confidence="medium",
            rule_ids=(f"school.{school_id}.fake",),
        ),
        preferred_pattern_ids=(pattern_id,),
        preferred_useful_god_elements=((element,) if element else ()),
    )


def mutate_reasoning(
    result: SchoolInterpretation, field_name: str, value: object
) -> SchoolInterpretation:
    reasoning = replace(result.reasoning)
    object.__setattr__(reasoning, field_name, value)
    return replace(result, reasoning=reasoning)


def mutate_preference(
    result: SchoolInterpretation, field_name: str, value: object
) -> SchoolInterpretation:
    mutated = replace(result)
    object.__setattr__(mutated, field_name, value)
    return mutated


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
        setattr(config, "version", "changed")
    with pytest.raises(TypeError):
        operator.setitem(
            cast(MutableMapping[str, SchoolProfile], config.profiles),
            "ziping",
            config.profiles["duan"],
        )
    with pytest.raises(TypeError):
        operator.setitem(config.profiles["ziping"].method_order, 0, "changed")


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
    tmp_path: Path, mutate: ConfigMutation, message: str
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


def direct_builtin_adapters() -> tuple[SchoolAdapterBase, ...]:
    config = load_school_profiles_config()
    return (
        ZipingSchoolAdapter(config.profiles["ziping"], config.version),
        LiangXiangrunSchoolAdapter(config.profiles["liang_xiangrun"], config.version),
        DuanSchoolAdapter(config.profiles["duan"], config.version),
    )


def test_builtin_adapters_are_immutable_when_loaded_or_constructed_directly() -> None:
    config = load_school_profiles_config()
    loaded = load_enabled_school_adapters()
    assert all(isinstance(adapter, SchoolAdapterBase) for adapter in loaded)
    loaded_builtins = tuple(cast(SchoolAdapterBase, adapter) for adapter in loaded)
    direct = direct_builtin_adapters()

    for adapter in (*loaded_builtins, *direct):
        original_profile = adapter.profile
        with pytest.raises(FrozenInstanceError):
            setattr(adapter, "profile", config.profiles["ziping"])
        with pytest.raises(FrozenInstanceError):
            setattr(adapter, "profile_version", "changed")
        assert adapter.profile is original_profile
        assert adapter.profile_version == "school-profiles-v1"


def test_direct_builtin_school_identity_cannot_be_shadowed() -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    adapters = direct_builtin_adapters()

    for adapter, expected_school_id in zip(
        adapters,
        ("ziping", "liang_xiangrun", "duan"),
        strict=True,
    ):
        assert adapter.school_id == expected_school_id
        assert "school_id" not in adapter.__dict__
        with pytest.raises((AttributeError, FrozenInstanceError)):
            setattr(adapter, "school_id", "forged")
        assert "school_id" not in adapter.__dict__
        assert adapter.school_id == expected_school_id

        result = adapter.interpret(
            facts=facts,
            strength=strength,
            patterns=patterns,
            useful_gods=useful_gods,
        )
        assert result.school_id == expected_school_id


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


def test_ziping_keeps_earlier_disputed_method_before_later_computed_method() -> None:
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
                    profile.method_order.index(item.method),
                    item.reasoning.status != "computed",
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


def test_liang_support_only_profile_emits_only_support_preferences_and_rules() -> None:
    facts, strength, patterns, useful_gods = pipeline_case("1991-01-18")
    profile = SchoolProfile(
        school_id="liang_xiangrun",
        priority=80,
        method_order=("support_control",),
    )
    result = LiangXiangrunSchoolAdapter(profile, "school-profiles-v1").interpret(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    expected_elements = tuple(
        dict.fromkeys(
            item.element
            for item in useful_gods
            if item.method == "support_control"
            and item.reasoning.status == "computed"
            and item.element
        )
    )

    assert result.preferred_pattern_ids == ()
    assert result.preferred_useful_god_elements == expected_elements
    assert result.reasoning.rule_ids == ("school.liang_xiangrun.support_control",)
    claimed = (
        result.reasoning.conclusion,
        *result.reasoning.supporting_signals,
        *result.reasoning.rule_ids,
    )
    assert all("pattern" not in value and "seasonal" not in value for value in claimed)


def test_liang_profile_method_order_controls_preferences_and_pattern_gate() -> None:
    facts, strength, patterns, useful_gods = pipeline_case("1991-01-18")
    seasonal_first = SchoolProfile(
        school_id="liang_xiangrun",
        priority=80,
        method_order=("seasonal_adjustment", "support_control"),
    )
    support_first = SchoolProfile(
        school_id="liang_xiangrun",
        priority=80,
        method_order=("support_control", "seasonal_adjustment"),
    )
    seasonal_result = LiangXiangrunSchoolAdapter(
        seasonal_first, "school-profiles-v1"
    ).interpret(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    support_result = LiangXiangrunSchoolAdapter(
        support_first, "school-profiles-v1"
    ).interpret(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    assert seasonal_result.preferred_pattern_ids == ()
    assert support_result.preferred_pattern_ids == ()
    assert seasonal_result.preferred_useful_god_elements != (
        support_result.preferred_useful_god_elements
    )
    assert seasonal_result.reasoning.rule_ids == (
        "school.liang_xiangrun.seasonal_adjustment",
        "school.liang_xiangrun.support_control",
    )
    assert support_result.reasoning.rule_ids == (
        "school.liang_xiangrun.support_control",
        "school.liang_xiangrun.seasonal_adjustment",
    )

    pattern_profile = SchoolProfile(
        school_id="liang_xiangrun",
        priority=80,
        method_order=("pattern_context",),
    )
    pattern_result = LiangXiangrunSchoolAdapter(
        pattern_profile, "school-profiles-v1"
    ).interpret(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    assert pattern_result.preferred_pattern_ids
    assert pattern_result.preferred_useful_god_elements == ()
    assert pattern_result.reasoning.rule_ids == (
        "school.liang_xiangrun.exposed_pattern_context",
    )


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
    clean = tuple(
        item.pattern_id
        for item in patterns
        if item.formation_conditions and not item.damage_conditions
    )
    assert qualifying
    assert clean
    assert positive.preferred_pattern_ids == qualifying
    assert not set(clean) & set(positive.preferred_pattern_ids)
    assert all(
        item.formation_conditions
        and item.damage_conditions
        and all(
            condition in item.reasoning.opposing_signals
            for condition in item.damage_conditions
        )
        for item in patterns
        if item.pattern_id in positive.preferred_pattern_ids
    )
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
def test_direct_adapter_rejects_duplicate_rank_and_forged_inputs(
    forge: InputForge,
) -> None:
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


@pytest.mark.parametrize(
    "forge",
    [
        lambda result: replace(result, profile_version="wrong-version"),
        lambda result: replace(
            result, reasoning=replace(result.reasoning, rule_ids=())
        ),
        lambda result: replace(
            result,
            reasoning=replace(result.reasoning, rule_ids=("other.rule",)),
        ),
        lambda result: mutate_reasoning(result, "status", "invalid"),
        lambda result: mutate_reasoning(result, "confidence", "invalid"),
        lambda result: replace(result, preferred_pattern_ids=("unknown.pattern",)),
        lambda result: replace(
            result,
            preferred_pattern_ids=(
                result.preferred_pattern_ids[0],
                result.preferred_pattern_ids[0],
            ),
        ),
        lambda result: replace(
            result, preferred_useful_god_elements=("unknown-element",)
        ),
        lambda result: replace(
            result,
            preferred_useful_god_elements=(
                result.preferred_useful_god_elements[0],
                result.preferred_useful_god_elements[0],
            ),
        ),
        lambda result: mutate_preference(
            result, "preferred_pattern_ids", [result.preferred_pattern_ids[0]]
        ),
        lambda result: mutate_preference(
            result, "preferred_pattern_ids", (["unhashable"],)
        ),
        lambda result: replace(
            result,
            preferred_pattern_ids=(),
            preferred_useful_god_elements=(),
        ),
        lambda result: replace(
            result,
            reasoning=replace(result.reasoning, status="not_computed"),
        ),
    ],
)
def test_malformed_adapter_output_is_isolated_before_disagreement(
    forge: SchoolResultForge,
) -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    element = next(item.element for item in useful_gods if item.element)
    base_result = valid_fake_result(
        school_id="ziping",
        pattern_id=patterns[0].pattern_id,
        element=element,
    )
    malformed = ReturningAdapter("ziping", forge(base_result))
    valid_liang = load_enabled_school_adapters()[1]

    first = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=(malformed, valid_liang),
    )
    second = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=(malformed, valid_liang),
    )

    assert first == second
    assert tuple(item.school_id for item in first) == ("ziping", "liang_xiangrun")
    isolated = first[0]
    assert isolated.profile_version == "school-profiles-v1"
    assert isolated.reasoning.status == "not_computed"
    assert isolated.reasoning.rule_ids == ("school.ziping.adapter_error",)
    assert isolated.preferred_pattern_ids == ()
    assert isolated.preferred_useful_god_elements == ()
    assert isolated.reasoning.missing_inputs[0].startswith("adapter_error:")
    assert first[1].reasoning.status != "not_computed"
    with pytest.raises(FrozenInstanceError):
        setattr(isolated, "school_id", "changed")


@pytest.mark.parametrize(
    "forge",
    [
        lambda result: mutate_preference(
            result, "reasoning", {"malformed": "reasoning"}
        ),
        lambda result: mutate_reasoning(
            result, "conclusion", {"malformed": "conclusion"}
        ),
        lambda result: mutate_reasoning(result, "conclusion", ""),
        lambda result: mutate_reasoning(result, "conclusion", " padded "),
        lambda result: mutate_reasoning(
            result, "supporting_signals", ({"malformed": "support"},)
        ),
        lambda result: mutate_reasoning(
            result, "opposing_signals", ({"malformed": "opposition"},)
        ),
        lambda result: mutate_reasoning(
            result, "assumptions", ({"malformed": "assumption"},)
        ),
        lambda result: mutate_reasoning(
            result, "missing_inputs", ({"malformed": "missing"},)
        ),
        lambda result: mutate_reasoning(result, "rule_ids", ({"malformed": "rule"},)),
    ],
)
def test_malformed_reasoning_payload_is_isolated_before_aggregation(
    forge: SchoolResultForge,
) -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    base_result = valid_fake_result(
        school_id="ziping",
        pattern_id=patterns[0].pattern_id,
    )
    malformed = ReturningAdapter("ziping", forge(base_result))
    valid_liang = load_enabled_school_adapters()[1]

    results = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=(malformed, valid_liang),
    )

    assert tuple(item.school_id for item in results) == (
        "ziping",
        "liang_xiangrun",
    )
    isolated = results[0]
    assert isolated.reasoning.status == "not_computed"
    assert isolated.reasoning.rule_ids == ("school.ziping.adapter_error",)
    assert isolated.preferred_pattern_ids == ()
    assert isolated.preferred_useful_god_elements == ()
    assert results[1].reasoning.status != "not_computed"


def test_disagreement_compares_preference_order_not_only_membership() -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    first_id, second_id = (item.pattern_id for item in patterns[:2])
    ziping_result = valid_fake_result(school_id="ziping", pattern_id=first_id)
    ziping_result = replace(ziping_result, preferred_pattern_ids=(first_id, second_id))
    liang_result = valid_fake_result(school_id="liang_xiangrun", pattern_id=second_id)
    liang_result = replace(liang_result, preferred_pattern_ids=(second_id, first_id))

    results = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=(
            ReturningAdapter("ziping", ziping_result),
            ReturningAdapter("liang_xiangrun", liang_result),
        ),
    )

    assert tuple(item.reasoning.status for item in results) == (
        "disputed",
        "disputed",
    )
    assert tuple(item.preferred_pattern_ids for item in results) == (
        (first_id, second_id),
        (second_id, first_id),
    )
    assert all(
        "school.cross_school_disagreement.pattern_preferences"
        in item.reasoning.rule_ids
        for item in results
    )


def fake_adapters_for_inputs(
    pattern_id: str,
) -> tuple[ReturningAdapter, ReturningAdapter, ReturningAdapter]:
    return (
        ReturningAdapter(
            "ziping",
            valid_fake_result(school_id="ziping", pattern_id=pattern_id),
        ),
        ReturningAdapter(
            "liang_xiangrun",
            valid_fake_result(school_id="liang_xiangrun", pattern_id=pattern_id),
        ),
        ReturningAdapter(
            "duan",
            valid_fake_result(school_id="duan", pattern_id=pattern_id),
        ),
    )


def test_injected_adapters_are_sorted_by_config_and_allow_subsets(
    tmp_path: Path,
) -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    ziping, liang, duan = fake_adapters_for_inputs(patterns[0].pattern_id)

    reversed_results = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=(duan, liang, ziping),
    )
    assert tuple(item.school_id for item in reversed_results) == (
        "ziping",
        "liang_xiangrun",
        "duan",
    )

    subset = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=(liang,),
    )
    assert tuple(item.school_id for item in subset) == ("liang_xiangrun",)

    payload = json.loads(json.dumps(EXPECTED_CONFIG))
    payload["profiles"]["ziping"]["priority"] = 70
    payload["profiles"]["duan"]["priority"] = 100
    custom_path = write_config(tmp_path, payload)
    custom_results = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=(ziping, liang, duan),
        path=custom_path,
    )
    assert tuple(item.school_id for item in custom_results) == (
        "duan",
        "liang_xiangrun",
        "ziping",
    )


def test_injected_adapter_contract_rejects_invalid_collections(tmp_path: Path) -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    ziping, liang, _ = fake_adapters_for_inputs(patterns[0].pattern_id)
    unknown = ReturningAdapter(
        "unknown",
        valid_fake_result(school_id="unknown", pattern_id=patterns[0].pattern_id),
    )
    wrong_version = ReturningAdapter("liang_xiangrun", liang.result)
    wrong_version.profile_version = "wrong-version"

    common = {
        "facts": facts,
        "strength": strength,
        "patterns": patterns,
        "useful_gods": useful_gods,
    }
    with pytest.raises(ValueError, match="tuple"):
        invalid_adapters = cast(tuple[SchoolAdapter, ...], [ziping])
        interpret_with_enabled_schools(**common, adapters=invalid_adapters)
    with pytest.raises(ValueError, match="enabled"):
        interpret_with_enabled_schools(**common, adapters=(unknown,))
    with pytest.raises(ValueError, match="unique"):
        interpret_with_enabled_schools(**common, adapters=(ziping, ziping))
    with pytest.raises(ValueError, match="profile version"):
        interpret_with_enabled_schools(**common, adapters=(wrong_version,))

    payload = json.loads(json.dumps(EXPECTED_CONFIG))
    payload["enabled"] = ["ziping"]
    path = write_config(tmp_path, payload)
    with pytest.raises(ValueError, match="enabled"):
        interpret_with_enabled_schools(**common, adapters=(liang,), path=path)


@pytest.mark.parametrize("raises", [False, True])
def test_mutating_adapter_identity_is_snapshotted_before_call(raises: bool) -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    stable_result = valid_fake_result(
        school_id="ziping", pattern_id=patterns[0].pattern_id
    )

    class MutatingAdapter:
        school_id = "ziping"
        profile_version = "school-profiles-v1"

        def interpret(
            self,
            *,
            facts: ChartFacts,
            strength: StrengthResult,
            patterns: tuple[PatternCandidateResult, ...],
            useful_gods: tuple[UsefulGodCandidateResult, ...],
        ) -> SchoolInterpretation:
            self.school_id = "unknown"
            self.profile_version = "wrong-version"
            if raises:
                raise RuntimeError("mutated adapter failure")
            return stable_result

    valid_liang = load_enabled_school_adapters()[1]
    results = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=(valid_liang, MutatingAdapter()),
    )

    assert tuple(item.school_id for item in results) == (
        "ziping",
        "liang_xiangrun",
    )
    if raises:
        assert results[0].reasoning.status == "not_computed"
        assert results[0].reasoning.rule_ids == ("school.ziping.adapter_error",)
    else:
        assert results[0].preferred_pattern_ids == stable_result.preferred_pattern_ids
        assert "school.ziping.fake" in results[0].reasoning.rule_ids
        assert "school.ziping.adapter_error" not in results[0].reasoning.rule_ids


def test_aggregate_uses_public_interpret_override_and_isolates_exception() -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    profile = load_school_profiles_config().profiles["ziping"]
    expected = valid_fake_result(school_id="ziping", pattern_id=patterns[0].pattern_id)
    calls: list[str] = []

    class OverridingZipingAdapter(ZipingSchoolAdapter):
        def interpret(
            self,
            *,
            facts: ChartFacts,
            strength: StrengthResult,
            patterns: tuple[PatternCandidateResult, ...],
            useful_gods: tuple[UsefulGodCandidateResult, ...],
        ) -> SchoolInterpretation:
            calls.append("interpret")
            return expected

    adapter = OverridingZipingAdapter(profile, "school-profiles-v1")
    direct = adapter.interpret(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    aggregate = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=(adapter,),
    )
    assert direct == expected
    assert aggregate == (expected,)
    assert calls == ["interpret", "interpret"]

    class RaisingZipingAdapter(ZipingSchoolAdapter):
        def interpret(
            self,
            *,
            facts: ChartFacts,
            strength: StrengthResult,
            patterns: tuple[PatternCandidateResult, ...],
            useful_gods: tuple[UsefulGodCandidateResult, ...],
        ) -> SchoolInterpretation:
            raise RuntimeError("public override failure")

    failure = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=(RaisingZipingAdapter(profile, "school-profiles-v1"),),
    )
    assert failure[0].school_id == "ziping"
    assert failure[0].reasoning.status == "not_computed"
    assert failure[0].reasoning.rule_ids == ("school.ziping.adapter_error",)


def test_aggregation_does_not_promote_not_computed_or_allow_adapter_suppression() -> (
    None
):
    facts, strength, patterns, useful_gods = pipeline_case()

    class EmptyAdapter:
        school_id = "ziping"
        profile_version = "school-profiles-v1"

        def interpret(
            self,
            *,
            facts: ChartFacts,
            strength: StrengthResult,
            patterns: tuple[PatternCandidateResult, ...],
            useful_gods: tuple[UsefulGodCandidateResult, ...],
        ) -> SchoolInterpretation:
            return SchoolInterpretation(
                school_id=self.school_id,
                profile_version=self.profile_version,
                reasoning=ReasonedResult(
                    status="not_computed",
                    conclusion="no supported preference",
                    confidence="low",
                    missing_inputs=("reviewed_rules",),
                    rule_ids=("school.ziping.no_supported_preference",),
                ),
                preferred_pattern_ids=(),
                preferred_useful_god_elements=(),
            )

    enabled = load_enabled_school_adapters()
    adapters = (enabled[2], EmptyAdapter(), enabled[1])
    results = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        adapters=adapters,
    )
    assert len(results) == 3
    assert results[0].school_id == "ziping"
    assert results[0].reasoning.status == "not_computed"
    assert results[0].preferred_pattern_ids == ()
    assert tuple(item.school_id for item in results[1:]) == (
        "liang_xiangrun",
        "duan",
    )


def test_inputs_are_frozen_and_never_mutated_by_direct_or_aggregate_calls() -> None:
    facts, strength, patterns, useful_gods = pipeline_case()
    snapshot = (facts, strength, patterns, useful_gods)
    with pytest.raises(FrozenInstanceError):
        setattr(facts, "day_master", "forged")
    with pytest.raises(TypeError):
        operator.setitem(patterns[0].formation_conditions, 0, "forged")

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
