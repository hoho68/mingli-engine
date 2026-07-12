import json
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType

import pytest

from mingli_engine.bazi.patterns import (
    PATTERN_DAMAGE,
    PATTERN_RESCUE,
    TEN_GOD_PATTERN_NAMES,
    calculate_pattern_candidates,
)
from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    ChartFacts,
    HiddenStemFact,
    ReasonedResult,
    StemFact,
    StrengthResult,
)


FIXTURE_PATH = (
    Path(__file__).parents[2]
    / "fixtures"
    / "bazi_calculation"
    / "pattern_counterexamples.json"
)
ALLOWED_STATUSES = {"not_computed", "computed", "indeterminate", "disputed"}


def exposed(pillar: str, ten_god: str, stem: str = "甲") -> StemFact:
    return StemFact(pillar, stem, "木", "yang", ten_god)


def hidden(
    pillar: str,
    role: str,
    ten_god: str,
    stem: str = "癸",
    branch: str = "子",
) -> HiddenStemFact:
    return HiddenStemFact(pillar, branch, stem, role, "水", "yin", ten_god)


def facts(
    month_main: str = "正官",
    *,
    exposed_stems: tuple[StemFact, ...] = (),
    month_secondary: tuple[HiddenStemFact, ...] = (),
    other_hidden: tuple[HiddenStemFact, ...] = (),
) -> ChartFacts:
    return ChartFacts(
        day_master="甲",
        month_branch="子",
        exposed_stems=exposed_stems,
        hidden_stems=(
            hidden("month", "main", month_main),
            *month_secondary,
            *other_hidden,
        ),
        roots=(),
        twelve_growth_by_pillar=(),
        assumptions=("facts:synthetic",),
    )


def strength(
    *, status: str = "computed", label: str = "较平衡"
) -> StrengthResult:
    return StrengthResult(
        reasoning=ReasonedResult(
            status=status,
            conclusion=label,
            confidence="high" if status == "computed" else "low",
            rule_ids=("strength.synthetic",),
        ),
        score=0.0,
        lower_bound=0.0,
        upper_bound=0.0,
        label=label,
        contributions=(),
    )


def by_name(results, name: str):
    return next(candidate for candidate in results if candidate.name == name)


def signal_ten_gods(conditions: tuple[str, ...]) -> list[str]:
    return [condition.rsplit(":", 1)[-1] for condition in conditions]


def load_counterexamples() -> list[dict[str, object]]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert payload["version"] == "ziping-pattern-counterexamples-v1"
    return payload["counterexamples"]


def test_rule_tables_are_exact_read_only_mappings_with_tuple_values() -> None:
    assert isinstance(TEN_GOD_PATTERN_NAMES, MappingProxyType)
    assert dict(TEN_GOD_PATTERN_NAMES) == {
        "正官": "正官格",
        "七杀": "七杀格",
        "正财": "正财格",
        "偏财": "偏财格",
        "正印": "正印格",
        "偏印": "偏印格",
        "食神": "食神格",
        "伤官": "伤官格",
    }
    assert dict(PATTERN_DAMAGE) == {
        "正官格": ("伤官",),
        "七杀格": (),
        "正财格": ("比肩", "劫财"),
        "偏财格": ("比肩", "劫财"),
        "正印格": ("正财", "偏财"),
        "偏印格": ("正财", "偏财"),
        "食神格": ("偏印",),
        "伤官格": ("正官",),
    }
    assert dict(PATTERN_RESCUE) == {
        "正官格": ("正印", "偏印"),
        "七杀格": ("食神", "正印", "偏印"),
        "正财格": ("正官", "七杀", "食神", "伤官"),
        "偏财格": ("正官", "七杀", "食神", "伤官"),
        "正印格": ("比肩", "劫财", "正官", "七杀"),
        "偏印格": ("比肩", "劫财", "正官", "七杀"),
        "食神格": ("正财", "偏财"),
        "伤官格": ("正财", "偏财", "正印", "偏印"),
    }
    assert all(isinstance(value, tuple) for value in PATTERN_DAMAGE.values())
    with pytest.raises(TypeError):
        PATTERN_DAMAGE["正官格"] = ()


def test_main_month_candidate_records_exposed_formation_with_high_confidence() -> None:
    chart = facts(exposed_stems=(exposed("year", "正官", "辛"),))

    candidate = calculate_pattern_candidates(chart, strength())[0]

    assert candidate.pattern_id == "standard.zhengguan"
    assert candidate.name == "正官格"
    assert candidate.rank == 1
    assert candidate.reasoning.status == "computed"
    assert candidate.reasoning.confidence == "high"
    assert candidate.formation_conditions == (
        "hidden:month:子:main:癸:正官",
        "exposed:year:辛:正官",
    )
    assert "exposed:year:辛:正官" in candidate.reasoning.supporting_signals


def test_unexposed_main_candidate_remains_latent_and_visible() -> None:
    candidate = calculate_pattern_candidates(facts(), strength())[0]

    assert candidate.name == "正官格"
    assert candidate.reasoning.status == "computed"
    assert candidate.reasoning.confidence == "medium"
    assert candidate.formation_conditions == (
        "hidden:month:子:main:癸:正官",
        "exposure:none:正官",
    )
    assert "formation:latent:正官" in candidate.reasoning.assumptions


@pytest.mark.parametrize(
    ("ten_god", "pattern_id", "name"),
    [
        ("比肩", "special.jianlu", "建禄格候选"),
        ("劫财", "special.yuejie", "月劫格候选"),
    ],
)
def test_companion_month_command_stays_an_explicit_candidate(
    ten_god: str, pattern_id: str, name: str
) -> None:
    candidate = calculate_pattern_candidates(facts(ten_god), strength())[0]

    assert (candidate.pattern_id, candidate.name, candidate.rank) == (
        pattern_id,
        name,
        1,
    )
    assert "candidate_only:not_final_pattern" in candidate.reasoning.assumptions


def test_secondary_roles_require_exposure_and_preserve_canonical_order() -> None:
    chart = facts(
        month_secondary=(
            hidden("month", "residual", "偏财", "戊", "辰"),
            hidden("month", "middle", "食神", "丙", "辰"),
            hidden("month", "middle", "食神", "丙", "辰"),
        ),
        exposed_stems=(
            exposed("hour", "偏财", "戊"),
            exposed("day", "食神", "丙"),
            exposed("year", "食神", "丙"),
        ),
    )

    results = calculate_pattern_candidates(chart, strength())

    assert [(item.name, item.rank) for item in results] == [
        ("正官格", 1),
        ("食神格", 2),
        ("偏财格", 3),
    ]
    assert len({item.pattern_id for item in results}) == len(results)


def test_fixture_drives_damage_rescue_and_strength_prerequisite() -> None:
    for case in load_counterexamples():
        signals = tuple(
            exposed("year" if index % 2 == 0 else "hour", ten_god, f"S{index}")
            for index, ten_god in enumerate(case["signals"])
        )
        upstream_status = case.get("strength_status", "computed")
        candidate = calculate_pattern_candidates(
            facts(case["pattern_ten_god"], exposed_stems=signals),
            strength(status=upstream_status),
        )[0]

        assert signal_ten_gods(candidate.damage_conditions) == case["expected_damage"]
        assert signal_ten_gods(candidate.rescue_conditions) == case["expected_rescue"]
        if upstream_status == "indeterminate":
            assert candidate.reasoning.status == "indeterminate"
            assert candidate.reasoning.confidence == "low"
            assert (
                "prerequisite:strength:indeterminate"
                in candidate.reasoning.assumptions
            )


@pytest.mark.parametrize("pattern_ten_god", tuple(TEN_GOD_PATTERN_NAMES))
def test_all_damage_and_rescue_tables_are_applied(pattern_ten_god: str) -> None:
    pattern_name = TEN_GOD_PATTERN_NAMES[pattern_ten_god]
    damage = PATTERN_DAMAGE[pattern_name]
    rescue = PATTERN_RESCUE[pattern_name]
    signals = tuple(
        exposed("year", ten_god, f"D{index}")
        for index, ten_god in enumerate((*damage, *rescue))
    )

    candidate = calculate_pattern_candidates(
        facts(pattern_ten_god, exposed_stems=signals), strength()
    )[0]

    assert signal_ten_gods(candidate.damage_conditions) == list(damage)
    assert signal_ten_gods(candidate.rescue_conditions) == list(rescue)


def test_damage_keeps_candidate_and_rescue_never_erases_opposition() -> None:
    damaged = calculate_pattern_candidates(
        facts("正官", exposed_stems=(exposed("year", "伤官"),)), strength()
    )[0]
    rescued = calculate_pattern_candidates(
        facts(
            "正官",
            exposed_stems=(exposed("year", "伤官"), exposed("hour", "正印")),
        ),
        strength(),
    )[0]

    assert damaged.reasoning.status == "disputed"
    assert damaged.reasoning.confidence == "low"
    assert rescued.reasoning.status == "disputed"
    assert rescued.reasoning.confidence == "medium"
    assert rescued.damage_conditions
    assert rescued.damage_conditions[0] in rescued.reasoning.opposing_signals
    assert rescued.rescue_conditions[0] in rescued.reasoning.supporting_signals


def test_exposed_signals_precede_hidden_without_dropping_hidden_provenance() -> None:
    chart = facts(
        "正官",
        exposed_stems=(exposed("hour", "伤官", "丁"),),
        other_hidden=(hidden("year", "main", "伤官", "丁", "午"),),
    )

    candidate = calculate_pattern_candidates(chart, strength())[0]

    assert candidate.damage_conditions == (
        "exposed:hour:丁:伤官",
        "hidden:year:午:main:丁:伤官",
    )


@pytest.mark.parametrize(
    ("upstream", "expected"),
    [("disputed", "disputed"), ("not_computed", "not_computed")],
)
def test_noncomputed_strength_status_is_propagated(
    upstream: str, expected: str
) -> None:
    candidate = calculate_pattern_candidates(
        facts(), strength(status=upstream)
    )[0]

    assert candidate.reasoning.status == expected
    assert candidate.reasoning.confidence == "low"
    assert f"prerequisite:strength:{upstream}" in candidate.reasoning.assumptions


@pytest.mark.parametrize(
    ("label", "pattern_id", "name"),
    [("强", "follow.congqiang", "从强候选"), ("弱", "follow.congruo", "从弱候选")],
)
def test_extreme_strength_adds_only_guarded_follow_candidate(
    label: str, pattern_id: str, name: str
) -> None:
    results = calculate_pattern_candidates(facts(), strength(label=label))
    follow = results[-1]

    assert (follow.pattern_id, follow.name, follow.rank) == (
        pattern_id,
        name,
        len(results),
    )
    assert follow.reasoning.status == "indeterminate"
    assert follow.reasoning.confidence == "low"
    assert follow.reasoning.missing_inputs
    assert follow.formation_conditions
    assert follow.damage_conditions
    assert "follow:v1_never_auto_confirm" in follow.reasoning.assumptions


def test_nonextreme_strength_does_not_add_follow_candidate() -> None:
    results = calculate_pattern_candidates(facts(), strength(label="偏强"))

    assert all(not item.pattern_id.startswith("follow.") for item in results)


@pytest.mark.parametrize(
    ("hidden_stems", "message"),
    [
        ((), "exactly one month main hidden stem"),
        (
            (
                hidden("month", "main", "正官"),
                hidden("month", "main", "七杀"),
            ),
            "exactly one month main hidden stem",
        ),
        ((hidden("month", "main", "未知"),), "unknown month main ten god"),
    ],
)
def test_malformed_month_facts_raise_explicit_value_error(
    hidden_stems: tuple[HiddenStemFact, ...], message: str
) -> None:
    malformed = ChartFacts("甲", "子", (), hidden_stems, (), (), ())

    with pytest.raises(ValueError, match=message):
        calculate_pattern_candidates(malformed, strength())


def test_results_are_immutable_deterministic_and_use_protocol_statuses() -> None:
    chart = facts(
        exposed_stems=(exposed("year", "正官", "辛"), exposed("hour", "伤官", "丁")),
        month_secondary=(hidden("month", "middle", "伤官", "丁", "午"),),
    )

    first = calculate_pattern_candidates(chart, strength(label="强"))
    second = calculate_pattern_candidates(chart, strength(label="强"))

    assert first == second
    assert all(item.reasoning.status in ALLOWED_STATUSES for item in first)
    assert all(item.reasoning.rule_ids for item in first)
    with pytest.raises(FrozenInstanceError):
        first[0].rank = 99


def test_relation_blockers_and_transformed_state_are_traced_without_effects() -> None:
    relation = BranchRelationResult(
        relation_type="three_combination",
        branches=("申", "子", "辰"),
        pillar_names=("year", "month", "hour"),
        state="blocked",
        transformed_element="水",
        conditions=("three branches present",),
        blockers=("month command blocks transformation",),
        rule_id="branch.three_combination.shenzichen",
    )

    candidate = calculate_pattern_candidates(facts(), strength(), (relation,))[0]

    assert any("state=blocked" in item for item in candidate.reasoning.assumptions)
    assert any(
        "transformed_element=水" in item
        for item in candidate.reasoning.assumptions
    )
    assert any(
        "blocker=month command blocks transformation" in item
        for item in candidate.reasoning.opposing_signals
    )
    assert any(
        "V1 pattern effect not implemented" in item
        for item in candidate.reasoning.assumptions
    )
    assert candidate.reasoning.status == "computed"
