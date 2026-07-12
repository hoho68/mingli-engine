import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import MappingProxyType
from typing import Callable

import pytest

from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    ChartFacts,
    HiddenStemFact,
    RootFact,
    StemFact,
)
from mingli_engine.bazi.facts import build_chart_facts
from mingli_engine.bazi.strength import (
    StrengthConfig,
    calculate_strength,
    load_strength_config,
)
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile


EXPECTED_PROFILE = {
    "version": "ziping-strength-v1",
    "month_command": {
        "same_element": 30,
        "resource": 24,
        "output": -18,
        "wealth": -20,
        "officer": -24,
    },
    "root": {"main": 18, "middle": 12, "residual": 6},
    "exposed": {
        "companion": 8,
        "resource": 7,
        "output": -7,
        "wealth": -8,
        "officer": -9,
    },
    "hidden_factor": 0.5,
    "thresholds": {
        "weak": -25,
        "balanced_low": -10,
        "balanced_high": 10,
        "strong": 25,
    },
    "sensitivity_fraction": 0.1,
}


def write_profile(tmp_path: Path, profile: dict[str, object]) -> Path:
    path = tmp_path / "strength.json"
    path.write_text(json.dumps(profile), encoding="utf-8")
    return path


def test_default_strength_profile_matches_the_declared_weights() -> None:
    config = load_strength_config()

    assert isinstance(config, StrengthConfig)
    assert config.version == EXPECTED_PROFILE["version"]
    assert dict(config.month_command) == EXPECTED_PROFILE["month_command"]
    assert dict(config.root) == EXPECTED_PROFILE["root"]
    assert dict(config.exposed) == EXPECTED_PROFILE["exposed"]
    assert config.hidden_factor == EXPECTED_PROFILE["hidden_factor"]
    assert dict(config.thresholds) == EXPECTED_PROFILE["thresholds"]
    assert config.sensitivity_fraction == EXPECTED_PROFILE["sensitivity_fraction"]


def test_strength_config_is_frozen_and_nested_weights_are_read_only() -> None:
    config = load_strength_config()

    with pytest.raises(FrozenInstanceError):
        config.version = "changed"
    with pytest.raises(TypeError):
        config.root["main"] = 99


@pytest.mark.parametrize("version", [None, "", "   "])
def test_rejects_missing_or_empty_version(tmp_path: Path, version: object) -> None:
    profile = dict(EXPECTED_PROFILE)
    if version is None:
        profile.pop("version")
    else:
        profile["version"] = version

    with pytest.raises(ValueError, match="version"):
        load_strength_config(write_profile(tmp_path, profile))


def test_rejects_unsupported_profile_version(tmp_path: Path) -> None:
    profile = json.loads(json.dumps(EXPECTED_PROFILE))
    profile["version"] = "ziping-strength-v2"

    with pytest.raises(
        ValueError,
        match="unsupported strength config version: 'ziping-strength-v2'",
    ):
        load_strength_config(write_profile(tmp_path, profile))


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda profile: profile.pop("root"), "missing top-level"),
        (lambda profile: profile.update({"surprise": {}}), "unknown top-level"),
        (
            lambda profile: profile["exposed"].pop("resource"),
            "missing exposed categories",
        ),
        (
            lambda profile: profile["month_command"].update({"surprise": 1}),
            "unknown month_command categories",
        ),
        (
            lambda profile: profile["root"].update({"secondary": 1}),
            "unknown root categories",
        ),
        (
            lambda profile: profile["thresholds"].pop("strong"),
            "missing thresholds categories",
        ),
    ],
)
def test_rejects_missing_or_unknown_categories(
    tmp_path: Path,
    mutation: Callable[[dict[str, object]], object],
    message: str,
) -> None:
    profile = json.loads(json.dumps(EXPECTED_PROFILE))
    mutation(profile)

    with pytest.raises(ValueError, match=message):
        load_strength_config(write_profile(tmp_path, profile))


@pytest.mark.parametrize(
    ("section", "key", "value"),
    [
        ("month_command", "resource", "24"),
        ("root", "main", True),
        ("exposed", "officer", None),
        ("thresholds", "weak", False),
    ],
)
def test_rejects_nonnumeric_and_boolean_weights(
    tmp_path: Path, section: str, key: str, value: object
) -> None:
    profile = json.loads(json.dumps(EXPECTED_PROFILE))
    profile[section][key] = value

    with pytest.raises(ValueError, match=f"{section}.{key} must be numeric"):
        load_strength_config(write_profile(tmp_path, profile))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("hidden_factor", -0.1, "hidden_factor must be between 0 and 1"),
        ("hidden_factor", 1.1, "hidden_factor must be between 0 and 1"),
        ("hidden_factor", True, "hidden_factor must be numeric"),
        ("sensitivity_fraction", -0.01, "sensitivity_fraction must be nonnegative"),
        ("sensitivity_fraction", 1.01, "sensitivity_fraction must be between 0 and 1"),
        ("sensitivity_fraction", False, "sensitivity_fraction must be numeric"),
    ],
)
def test_rejects_invalid_factors(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    profile = json.loads(json.dumps(EXPECTED_PROFILE))
    profile[field] = value

    with pytest.raises(ValueError, match=message):
        load_strength_config(write_profile(tmp_path, profile))


@pytest.mark.parametrize(
    "thresholds",
    [
        {"weak": -10, "balanced_low": -10, "balanced_high": 10, "strong": 25},
        {"weak": -25, "balanced_low": 11, "balanced_high": 10, "strong": 25},
        {"weak": -25, "balanced_low": -10, "balanced_high": 25, "strong": 25},
    ],
)
def test_rejects_thresholds_that_are_not_strictly_ordered(
    tmp_path: Path, thresholds: dict[str, int]
) -> None:
    profile = json.loads(json.dumps(EXPECTED_PROFILE))
    profile["thresholds"] = thresholds

    with pytest.raises(ValueError, match="thresholds must satisfy"):
        load_strength_config(write_profile(tmp_path, profile))


def test_config_file_read_errors_are_clear(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"

    with pytest.raises(ValueError, match="unable to read strength config"):
        load_strength_config(missing)


def test_invalid_json_is_clear(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSON in strength config"):
        load_strength_config(path)


def facts(
    *,
    day_master: str = "甲",
    month_branch: str = "子",
    exposed: tuple[StemFact, ...] = (),
    hidden: tuple[HiddenStemFact, ...] = (),
    roots: tuple[RootFact, ...] = (),
) -> ChartFacts:
    return ChartFacts(
        day_master=day_master,
        month_branch=month_branch,
        exposed_stems=exposed,
        hidden_stems=hidden,
        roots=roots,
        twelve_growth_by_pillar=(),
        assumptions=("source:frozen",),
    )


def stem(pillar: str, value: str, element: str) -> StemFact:
    return StemFact(pillar, value, element, "yang", "synthetic")


def hidden_stem(
    pillar: str, branch: str, value: str, role: str, element: str
) -> HiddenStemFact:
    return HiddenStemFact(
        pillar, branch, value, role, element, "yang", "synthetic"
    )


def root(
    value: str,
    role: str,
    branch_pillar: str = "month",
    branch: str = "synthetic",
    exact_stem_root: bool = True,
) -> RootFact:
    return RootFact(
        value,
        "day",
        branch,
        branch_pillar,
        role,
        exact_stem_root,
    )


def configured(
    *,
    month_command: dict[str, float] | None = None,
    exposed: dict[str, float] | None = None,
    thresholds: dict[str, float] | None = None,
    sensitivity_fraction: float | None = None,
) -> StrengthConfig:
    base = load_strength_config()
    changes: dict[str, object] = {}
    if month_command is not None:
        changes["month_command"] = MappingProxyType(month_command)
    if exposed is not None:
        changes["exposed"] = MappingProxyType(exposed)
    if thresholds is not None:
        changes["thresholds"] = MappingProxyType(thresholds)
    if sensitivity_fraction is not None:
        changes["sensitivity_fraction"] = sensitivity_fraction
    return replace(base, **changes)


def test_season_and_exact_roots_are_separate_traceable_contributions() -> None:
    result = calculate_strength(
        facts(
            roots=(
                root("甲", "main", "year"),
                root("甲", "middle", "month"),
                root("甲", "residual", "hour"),
            )
        )
    )

    assert [item.category for item in result.contributions] == [
        "month_command",
        "root",
        "root",
        "root",
    ]
    assert [item.value for item in result.contributions] == [24, 18, 12, 6]
    assert [item.signal for item in result.contributions[1:]] == [
        "year:synthetic:main",
        "month:synthetic:middle",
        "hour:synthetic:residual",
    ]
    assert all(item.rule_id for item in result.contributions)
    assert result.reasoning.rule_ids == tuple(
        item.rule_id for item in result.contributions
    )
    assert "profile_version=ziping-strength-v1" in result.reasoning.assumptions


def test_canonical_repeated_day_master_stem_counts_each_physical_root_once() -> None:
    chart = calculate_bazi_chart(
        BirthProfile(
            calendar_type="gregorian",
            birth_date="1992-08-18",
            birth_time="09:30",
            birthplace="上海市",
            gender="未指定",
            focus_topic="整体结构观察",
        )
    )
    repeated_day_master = [
        replace(chart.pillars[0], heavenly_stem=chart.day_master),
        *chart.pillars[1:],
    ]
    chart_facts = build_chart_facts(
        replace(chart, pillars=repeated_day_master)
    )

    assert len(
        [item for item in chart_facts.roots if item.stem == chart.day_master]
    ) == 4

    result = calculate_strength(chart_facts)
    root_contributions = [
        item for item in result.contributions if item.category == "root"
    ]

    assert [(item.signal, item.value, item.rule_id) for item in root_contributions] == [
        ("day:寅:middle", 12, "strength.root.middle"),
        ("hour:巳:main", 18, "strength.root.main"),
    ]


def test_same_branch_in_different_pillar_positions_remains_distinct_roots() -> None:
    config = configured(sensitivity_fraction=0)

    result = calculate_strength(
        facts(
            roots=(
                root("甲", "main", "year", "寅"),
                root("甲", "main", "month", "寅"),
            )
        ),
        config=config,
    )

    assert [
        item.signal for item in result.contributions if item.category == "root"
    ] == ["year:寅:main", "month:寅:main"]


@pytest.mark.parametrize(
    ("chart_facts", "config", "score", "label"),
    [
        (
            facts(month_branch="寅"),
            configured(
                month_command={
                    "same_element": 20,
                    "resource": 24,
                    "output": -18,
                    "wealth": -20,
                    "officer": -24,
                }
            ),
            20,
            "偏强",
        ),
        (facts(month_branch="巳"), None, -18, "偏弱"),
        (
            facts(month_branch="寅"),
            configured(
                month_command={
                    "same_element": 0,
                    "resource": 24,
                    "output": -18,
                    "wealth": -20,
                    "officer": -24,
                }
            ),
            0,
            "较平衡",
        ),
        (facts(month_branch="寅"), None, 30, "强"),
        (
            facts(month_branch="寅"),
            configured(
                month_command={
                    "same_element": -30,
                    "resource": 24,
                    "output": -18,
                    "wealth": -20,
                    "officer": -24,
                }
            ),
            -30,
            "弱",
        ),
    ],
)
def test_clear_synthetic_scores_use_all_strength_bands(
    chart_facts: ChartFacts,
    config: StrengthConfig | None,
    score: float,
    label: str,
) -> None:
    result = calculate_strength(chart_facts, config=config)

    assert result.score == score
    assert result.label == label
    assert result.reasoning.status == "computed"
    assert result.reasoning.confidence in {"high", "medium"}


@pytest.mark.parametrize("score", [-10, 10])
def test_balanced_thresholds_are_inclusive(score: float) -> None:
    config = configured(
        month_command={
            "same_element": score,
            "resource": 0,
            "output": 0,
            "wealth": 0,
            "officer": 0,
        },
        sensitivity_fraction=0,
    )

    result = calculate_strength(facts(month_branch="寅"), config=config)

    assert result.score == score
    assert result.label == "较平衡"


def test_sensitivity_crossing_returns_ordered_indeterminate_bounds() -> None:
    result = calculate_strength(facts())

    assert result.score == 24
    assert result.lower_bound == pytest.approx(21.6)
    assert result.upper_bound == pytest.approx(26.4)
    assert result.label == "临界"
    assert result.reasoning.status == "indeterminate"
    assert result.reasoning.confidence == "low"
    assert "偏强" in result.reasoning.conclusion
    assert "强" in result.reasoning.conclusion


def test_sensitivity_recomputes_the_whole_profile_uniformly() -> None:
    result = calculate_strength(
        facts(
            month_branch="巳",
            exposed=(stem("year", "乙", "木"),),
            roots=(root("甲", "main"),),
        )
    )

    assert result.score == 8
    assert result.lower_bound == pytest.approx(7.2)
    assert result.upper_bound == pytest.approx(8.8)
    assert result.label == "较平衡"
    assert result.reasoning.status == "computed"


@pytest.mark.parametrize("weight", [1e308, -1e308])
def test_nonfinite_central_aggregate_is_rejected(weight: float) -> None:
    config = configured(
        month_command={
            "same_element": weight,
            "resource": 0,
            "output": 0,
            "wealth": 0,
            "officer": 0,
        },
        exposed={
            "companion": weight,
            "resource": 0,
            "output": 0,
            "wealth": 0,
            "officer": 0,
        },
        sensitivity_fraction=0,
    )

    with pytest.raises(
        ValueError,
        match="^strength calculation produced a non-finite value$",
    ):
        calculate_strength(
            facts(
                month_branch="寅",
                exposed=(stem("year", "乙", "木"),),
            ),
            config=config,
        )


def test_nonfinite_sensitivity_product_is_rejected() -> None:
    config = configured(
        month_command={
            "same_element": 1e308,
            "resource": 0,
            "output": 0,
            "wealth": 0,
            "officer": 0,
        },
        sensitivity_fraction=1,
    )

    with pytest.raises(
        ValueError,
        match="^strength calculation produced a non-finite value$",
    ):
        calculate_strength(facts(month_branch="寅"), config=config)


def test_floating_point_threshold_noise_preserves_inclusive_boundary() -> None:
    config = configured(
        month_command={
            "same_element": 0.1,
            "resource": 0,
            "output": 0,
            "wealth": 0,
            "officer": 0,
        },
        exposed={
            "companion": 0.2,
            "resource": 0,
            "output": 0,
            "wealth": 0,
            "officer": 0,
        },
        thresholds={
            "weak": -1,
            "balanced_low": -0.3,
            "balanced_high": 0.3,
            "strong": 1,
        },
        sensitivity_fraction=0,
    )

    result = calculate_strength(
        facts(
            month_branch="寅",
            exposed=(stem("year", "乙", "木"),),
        ),
        config=config,
    )

    assert result.score == 0.1 + 0.2
    assert result.score > 0.3
    assert result.label == "较平衡"


def test_nonexact_day_master_root_contributes_nothing() -> None:
    config = configured(
        month_command={
            "same_element": 0,
            "resource": 0,
            "output": 0,
            "wealth": 0,
            "officer": 0,
        },
        sensitivity_fraction=0,
    )

    result = calculate_strength(
        facts(
            month_branch="寅",
            roots=(root("甲", "main", exact_stem_root=False),),
        ),
        config=config,
    )

    assert result.score == 0
    assert all(item.category != "root" for item in result.contributions)


def test_exposed_self_is_excluded_hidden_factor_applies_and_only_dm_roots_count() -> None:
    config = configured(
        month_command={
            "same_element": 0,
            "resource": 0,
            "output": 0,
            "wealth": 0,
            "officer": 0,
        },
        sensitivity_fraction=0,
    )
    result = calculate_strength(
        facts(
            month_branch="寅",
            exposed=(
                stem("day", "甲", "木"),
                stem("year", "乙", "木"),
            ),
            hidden=(hidden_stem("month", "申", "庚", "main", "金"),),
            roots=(root("甲", "main"), root("乙", "middle")),
        ),
        config=config,
    )

    assert [(item.category, item.signal, item.value) for item in result.contributions] == [
        ("month_command", "companion", 0),
        ("root", "month:synthetic:main", 18),
        ("exposed", "year:companion", 8),
        ("hidden", "month:main:officer", -4.5),
    ]
    assert result.score == 21.5
    assert all("day:companion" != item.signal for item in result.contributions)


def test_positive_and_negative_contributions_are_separate_reasoning_signals() -> None:
    result = calculate_strength(
        facts(
            exposed=(stem("year", "乙", "木"),),
            hidden=(hidden_stem("month", "申", "庚", "main", "金"),),
        )
    )

    assert "year:companion" in result.reasoning.supporting_signals
    assert "month:main:officer" in result.reasoning.opposing_signals


def test_untransformed_relations_add_trace_without_a_numeric_modifier() -> None:
    relation = BranchRelationResult(
        "three_combination",
        ("申", "子", "辰"),
        ("year", "month", "day"),
        "active",
        "",
        ("complete",),
        (),
        "branch.three_combination.申子辰.水",
    )

    config = configured(sensitivity_fraction=0)
    baseline = calculate_strength(facts(), config=config)
    result = calculate_strength(facts(), (relation,), config=config)

    assert result.score == baseline.score
    assert result.contributions == baseline.contributions
    assert any(relation.rule_id in item for item in result.reasoning.assumptions)
    assert any("relation" in rule_id for rule_id in result.reasoning.rule_ids)
    assert result.reasoning.status == "computed"
    assert result.reasoning.missing_inputs == ()


def test_repeated_relation_rule_ids_keep_distinct_occurrence_traces() -> None:
    first = BranchRelationResult(
        "six_combination",
        ("子", "丑"),
        ("year", "month"),
        "present",
        "",
        ("synthetic",),
        (),
        "branch.six_combination.子丑",
    )
    second = replace(
        first,
        branches=("丑", "子"),
        pillar_names=("day", "hour"),
    )
    config = configured(sensitivity_fraction=0)

    result = calculate_strength(facts(), (first, second), config=config)

    relation_assumptions = tuple(
        item
        for item in result.reasoning.assumptions
        if first.rule_id in item
    )
    relation_rule_ids = tuple(
        item
        for item in result.reasoning.rule_ids
        if first.rule_id in item
    )
    assert relation_assumptions == (
        "branch.six_combination.子丑|pillars=year,month|branches=子,丑: "
        "transformed_element is empty; no numeric strength modifier applied",
        "branch.six_combination.子丑|pillars=day,hour|branches=丑,子: "
        "transformed_element is empty; no numeric strength modifier applied",
    )
    assert relation_rule_ids == (
        "strength.relation.no_numeric_modifier:"
        "branch.six_combination.子丑|pillars=year,month|branches=子,丑",
        "strength.relation.no_numeric_modifier:"
        "branch.six_combination.子丑|pillars=day,hour|branches=丑,子",
    )


def transformed_relation() -> BranchRelationResult:
    return BranchRelationResult(
        "three_combination",
        ("申", "子", "辰"),
        ("year", "month", "day"),
        "active",
        "水",
        ("synthetic transformation",),
        (),
        "branch.three_combination.申子辰.水",
    )


def test_transformed_relation_forces_unimplemented_modifier_state() -> None:
    config = configured(sensitivity_fraction=0)
    baseline = calculate_strength(facts(), config=config)

    result = calculate_strength(
        facts(), (transformed_relation(),), config=config
    )

    assert result.score == baseline.score
    assert result.contributions == baseline.contributions
    assert result.reasoning.status == "indeterminate"
    assert result.reasoning.confidence == "low"
    assert result.reasoning.missing_inputs == (
        "transformed_relation_strength_modifier",
    )
    assert "modifier not implemented" in result.reasoning.conclusion
    assert result.label == "待定"


def test_transformed_relation_and_sensitivity_crossing_report_both_causes() -> None:
    result = calculate_strength(facts(), (transformed_relation(),))

    assert result.lower_bound == pytest.approx(21.6)
    assert result.upper_bound == pytest.approx(26.4)
    assert result.reasoning.status == "indeterminate"
    assert "modifier not implemented" in result.reasoning.conclusion
    assert "偏强" in result.reasoning.conclusion
    assert "强" in result.reasoning.conclusion
    assert result.label == "待定"


@pytest.mark.parametrize(
    ("config", "message"),
    [
        (
            replace(load_strength_config(), version="ziping-strength-v2"),
            "unsupported strength config version: 'ziping-strength-v2'",
        ),
        (
            replace(load_strength_config(), sensitivity_fraction=1.01),
            "sensitivity_fraction must be between 0 and 1",
        ),
    ],
)
def test_injected_config_cannot_bypass_guardrails(
    config: StrengthConfig, message: str
) -> None:
    with pytest.raises(ValueError, match=f"^{message}$"):
        calculate_strength(facts(), config=config)


def test_strength_config_defensively_copies_ordinary_mapping_inputs() -> None:
    month_command = dict(EXPECTED_PROFILE["month_command"])
    roots = dict(EXPECTED_PROFILE["root"])
    exposed = dict(EXPECTED_PROFILE["exposed"])
    thresholds = dict(EXPECTED_PROFILE["thresholds"])
    config = StrengthConfig(
        version="ziping-strength-v1",
        month_command=month_command,
        root=roots,
        exposed=exposed,
        hidden_factor=0.5,
        thresholds=thresholds,
        sensitivity_fraction=0.1,
    )
    replacement_roots = {"main": 80, "middle": 40, "residual": 20}
    replaced = replace(config, root=replacement_roots)

    month_command["same_element"] = 999
    roots["main"] = 999
    exposed["companion"] = 999
    thresholds["strong"] = 999
    replacement_roots["main"] = 999

    assert config.month_command["same_element"] == 30
    assert config.root["main"] == 18
    assert config.exposed["companion"] == 8
    assert config.thresholds["strong"] == 25
    assert replaced.root["main"] == 80
    with pytest.raises(TypeError):
        config.root["main"] = 999


@pytest.mark.parametrize(
    ("chart_facts", "message"),
    [
        (facts(day_master="invalid"), "Invalid stem: 'invalid'"),
        (facts(month_branch="invalid"), "Invalid branch: 'invalid'"),
        (
            facts(exposed=(stem("year", "invalid", "木"),)),
            "Invalid stem: 'invalid'",
        ),
        (facts(roots=(root("甲", "unknown"),)), "unknown root role: 'unknown'"),
        (
            facts(
                hidden=(
                    hidden_stem("month", "申", "庚", "unknown", "金"),
                )
            ),
            "unknown hidden stem role: 'unknown'",
        ),
    ],
)
def test_invalid_fact_values_fail_explicitly(
    chart_facts: ChartFacts, message: str
) -> None:
    with pytest.raises(ValueError, match=f"^{message}$"):
        calculate_strength(chart_facts)


def test_inputs_remain_immutable_after_calculation() -> None:
    chart_facts = facts(
        exposed=(stem("year", "乙", "木"),),
        hidden=(hidden_stem("month", "申", "庚", "main", "金"),),
        roots=(root("甲", "main"),),
    )
    relation = BranchRelationResult(
        "six_clash",
        ("子", "午"),
        ("month", "day"),
        "present",
        "",
        ("both present",),
        (),
        "branch.six_clash.子午",
    )
    before = (hash(chart_facts), hash(relation), chart_facts, relation)

    calculate_strength(chart_facts, (relation,))

    assert (hash(chart_facts), hash(relation), chart_facts, relation) == before
