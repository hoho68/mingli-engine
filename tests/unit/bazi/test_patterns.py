import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import MappingProxyType
from typing import Final, Mapping, NotRequired, TypeGuard, TypedDict

import pytest

from mingli_engine.bazi.constants import (
    HIDDEN_STEMS,
    STEM_ELEMENT,
    STEM_POLARITY,
)
from mingli_engine.bazi.facts import Branch, Stem, ten_god
from mingli_engine.bazi.patterns import (
    PATTERN_DAMAGE,
    PATTERN_RESCUE,
    TEN_GOD_PATTERN_NAMES,
    calculate_pattern_candidates,
)
from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    ChartFacts,
    ComputationStatus,
    Confidence,
    HiddenStemFact,
    PatternCandidateResult,
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
DAY_MASTER: Final = "甲"
PILLAR_ORDER: Final = ("year", "month", "day", "hour")
TEN_GOD_STEM: Final[Mapping[str, Stem]] = MappingProxyType(
    {
        "比肩": "甲",
        "劫财": "乙",
        "食神": "丙",
        "伤官": "丁",
        "偏财": "戊",
        "正财": "己",
        "七杀": "庚",
        "正官": "辛",
        "偏印": "壬",
        "正印": "癸",
    }
)
MONTH_BRANCH_BY_MAIN: Final[Mapping[str, Branch]] = MappingProxyType(
    {
        "比肩": "寅",
        "劫财": "卯",
        "食神": "巳",
        "伤官": "午",
        "偏财": "辰",
        "正财": "丑",
        "七杀": "申",
        "正官": "酉",
        "偏印": "亥",
        "正印": "子",
    }
)
ALLOWED_STATUSES = {"not_computed", "computed", "indeterminate", "disputed"}


class Counterexample(TypedDict):
    id: str
    pattern_ten_god: str
    signals: tuple[str, ...]
    expected_damage: tuple[str, ...]
    expected_rescue: tuple[str, ...]
    strength_status: NotRequired[ComputationStatus]
    latent_branches: NotRequired[tuple[Branch, ...]]
    expected_latent_context: NotRequired[tuple[str, ...]]


def _is_str_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict) and all(
        isinstance(key, str) for key in value
    )


def _is_object_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def _is_status(value: object) -> TypeGuard[ComputationStatus]:
    return isinstance(value, str) and value in ALLOWED_STATUSES


def _is_branch(value: str) -> TypeGuard[Branch]:
    return value in HIDDEN_STEMS


def _string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"fixture {field} must be a nonempty string")
    return value


def _strings(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise ValueError(f"fixture {field} must be a string list")
    return tuple(value)


def _branches(value: object, field: str) -> tuple[Branch, ...]:
    strings = _strings(value, field)
    if not all(_is_branch(branch) for branch in strings):
        raise ValueError(f"fixture {field} contains an invalid branch")
    return tuple(branch for branch in strings if _is_branch(branch))


def load_counterexamples() -> tuple[Counterexample, ...]:
    raw: object = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if not _is_str_object_dict(raw):
        raise ValueError("fixture root must be an object")
    if raw.get("version") != "ziping-pattern-counterexamples-v1":
        raise ValueError("unsupported pattern counterexample fixture version")
    rows = raw.get("counterexamples")
    if not _is_object_list(rows):
        raise ValueError("fixture counterexamples must be a list")

    parsed: list[Counterexample] = []
    for row_index, raw_row in enumerate(rows):
        if not _is_str_object_dict(raw_row):
            raise ValueError(f"counterexample {row_index} must be an object")
        parsed_row: Counterexample = {
            "id": _string(raw_row.get("id"), "id"),
            "pattern_ten_god": _string(
                raw_row.get("pattern_ten_god"), "pattern_ten_god"
            ),
            "signals": _strings(raw_row.get("signals"), "signals"),
            "expected_damage": _strings(
                raw_row.get("expected_damage"), "expected_damage"
            ),
            "expected_rescue": _strings(
                raw_row.get("expected_rescue"), "expected_rescue"
            ),
        }
        raw_status = raw_row.get("strength_status")
        if raw_status is not None:
            if not _is_status(raw_status):
                raise ValueError("fixture strength_status is invalid")
            parsed_row["strength_status"] = raw_status
        if "latent_branches" in raw_row:
            parsed_row["latent_branches"] = _branches(
                raw_row["latent_branches"], "latent_branches"
            )
        if "expected_latent_context" in raw_row:
            parsed_row["expected_latent_context"] = _strings(
                raw_row["expected_latent_context"],
                "expected_latent_context",
            )
        parsed.append(parsed_row)
    return tuple(parsed)


def canonical_stem_fact(pillar: str, stem: Stem) -> StemFact:
    return StemFact(
        pillar_name=pillar,
        stem=stem,
        element=STEM_ELEMENT[stem],
        polarity=STEM_POLARITY[stem],
        ten_god=ten_god(DAY_MASTER, stem),
    )


def canonical_hidden_facts(
    pillar: str, branch: Branch
) -> tuple[HiddenStemFact, ...]:
    return tuple(
        HiddenStemFact(
            pillar_name=pillar,
            branch=branch,
            stem=stem,
            role=role,
            element=STEM_ELEMENT[stem],
            polarity=STEM_POLARITY[stem],
            ten_god=ten_god(DAY_MASTER, stem),
        )
        for stem, role in HIDDEN_STEMS[branch]
    )


def facts(
    month_main: str = "正官",
    *,
    exposed_signals: tuple[str, ...] = (),
    other_hidden_branches: tuple[Branch, ...] = (),
) -> ChartFacts:
    if len(exposed_signals) > 3:
        raise ValueError("tests support at most three non-day exposed signals")
    assigned_stems = tuple(TEN_GOD_STEM[item] for item in exposed_signals)
    pattern_name = TEN_GOD_PATTERN_NAMES.get(month_main)
    forbidden = (
        {*PATTERN_DAMAGE[pattern_name], *PATTERN_RESCUE[pattern_name]}
        if pattern_name is not None
        else set()
    )
    neutral_god = next(
        god_name
        for god_name in TEN_GOD_STEM
        if god_name not in forbidden and god_name not in exposed_signals
    )
    neutral_stem = TEN_GOD_STEM[neutral_god]
    non_day_stems = (
        *assigned_stems,
        *((neutral_stem,) * (3 - len(assigned_stems))),
    )
    exposed_stems = (
        canonical_stem_fact("year", non_day_stems[0]),
        canonical_stem_fact("month", non_day_stems[1]),
        canonical_stem_fact("day", DAY_MASTER),
        canonical_stem_fact("hour", non_day_stems[2]),
    )
    month_branch = MONTH_BRANCH_BY_MAIN[month_main]
    other_hidden = tuple(
        hidden_fact
        for index, branch in enumerate(other_hidden_branches)
        for hidden_fact in canonical_hidden_facts(
            ("year", "hour")[index % 2], branch
        )
    )
    return ChartFacts(
        day_master=DAY_MASTER,
        month_branch=month_branch,
        exposed_stems=exposed_stems,
        hidden_stems=(
            *canonical_hidden_facts("month", month_branch),
            *other_hidden,
        ),
        roots=(),
        twelve_growth_by_pillar=(),
        assumptions=("facts:canonical-test",),
    )


def strength(
    *,
    status: ComputationStatus = "computed",
    label: str = "较平衡",
) -> StrengthResult:
    confidence: Confidence = "high" if status == "computed" else "low"
    return StrengthResult(
        reasoning=ReasonedResult(
            status=status,
            conclusion=label,
            confidence=confidence,
            rule_ids=("strength.canonical_test",),
        ),
        score=0.0,
        lower_bound=0.0,
        upper_bound=0.0,
        label=label,
        contributions=(),
    )


def by_name(
    results: tuple[PatternCandidateResult, ...], name: str
) -> PatternCandidateResult:
    return next(candidate for candidate in results if candidate.name == name)


def signal_ten_gods(conditions: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(condition.rsplit(":", 1)[-1] for condition in conditions)


def transformed_relation() -> BranchRelationResult:
    return BranchRelationResult(
        "three_combination",
        ("申", "子", "辰"),
        ("year", "month", "hour"),
        "transformed",
        "水",
        ("three branches present",),
        (),
        "branch.three_combination.shenzichen",
    )


def test_rule_tables_are_exact_read_only_mappings_with_tuple_values() -> None:
    assert isinstance(TEN_GOD_PATTERN_NAMES, MappingProxyType)
    assert dict(TEN_GOD_PATTERN_NAMES) == {
        "正官": "正官格", "七杀": "七杀格", "正财": "正财格",
        "偏财": "偏财格", "正印": "正印格", "偏印": "偏印格",
        "食神": "食神格", "伤官": "伤官格",
    }
    assert dict(PATTERN_DAMAGE) == {
        "正官格": ("伤官",), "七杀格": (),
        "正财格": ("比肩", "劫财"), "偏财格": ("比肩", "劫财"),
        "正印格": ("正财", "偏财"), "偏印格": ("正财", "偏财"),
        "食神格": ("偏印",), "伤官格": ("正官",),
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


def test_main_candidate_records_real_exposed_formation() -> None:
    candidate = calculate_pattern_candidates(
        facts("正官", exposed_signals=("正官",)), strength()
    )[0]

    assert (candidate.pattern_id, candidate.name, candidate.rank) == (
        "standard.zhengguan", "正官格", 1
    )
    assert candidate.reasoning.confidence == "high"
    assert candidate.formation_conditions == (
        "hidden:month:酉:main:辛:正官",
        "exposed:year:辛:正官",
    )


def test_unexposed_main_candidate_remains_latent() -> None:
    candidate = calculate_pattern_candidates(facts(), strength())[0]
    assert candidate.reasoning.status == "computed"
    assert candidate.reasoning.confidence == "medium"
    assert candidate.formation_conditions[-1] == "exposure:none:正官"
    assert "formation:latent:正官" in candidate.reasoning.assumptions


@pytest.mark.parametrize(
    ("ten_god_name", "pattern_id", "name"),
    [("比肩", "special.jianlu", "建禄格候选"),
     ("劫财", "special.yuejie", "月劫格候选")],
)
def test_companion_month_command_is_explicit_candidate(
    ten_god_name: str, pattern_id: str, name: str
) -> None:
    candidate = calculate_pattern_candidates(facts(ten_god_name), strength())[0]
    assert (candidate.pattern_id, candidate.name) == (pattern_id, name)
    assert "candidate_only:not_final_pattern" in candidate.reasoning.assumptions


def test_secondary_roles_require_exposure_and_keep_canonical_order() -> None:
    results = calculate_pattern_candidates(
        facts("正财", exposed_signals=("正官", "正印")), strength()
    )
    assert [(item.name, item.rank) for item in results] == [
        ("正财格", 1), ("正印格", 2), ("正官格", 3)
    ]


def test_fixture_counterexamples_use_canonical_fact_builders() -> None:
    for case in load_counterexamples():
        candidate = calculate_pattern_candidates(
            facts(
                case["pattern_ten_god"],
                exposed_signals=case["signals"],
                other_hidden_branches=case.get("latent_branches", ()),
            ),
            strength(status=case.get("strength_status", "computed")),
        )[0]
        expected_status = (
            case.get("strength_status")
            or ("disputed" if case["expected_damage"] else "computed")
        )
        assert candidate.reasoning.status == expected_status
        assert signal_ten_gods(candidate.damage_conditions) == case["expected_damage"]
        assert signal_ten_gods(candidate.rescue_conditions) == case["expected_rescue"]
        for latent_god in case.get("expected_latent_context", ()):
            assert any(
                item.startswith("latent_damage_context:hidden:")
                and item.endswith(f":{latent_god}")
                for item in candidate.reasoning.assumptions
            )


@pytest.mark.parametrize("pattern_ten_god", tuple(TEN_GOD_PATTERN_NAMES))
def test_each_damage_and_rescue_rule_is_applied(pattern_ten_god: str) -> None:
    pattern_name = TEN_GOD_PATTERN_NAMES[pattern_ten_god]
    for damage_god in PATTERN_DAMAGE[pattern_name]:
        candidate = calculate_pattern_candidates(
            facts(pattern_ten_god, exposed_signals=(damage_god,)), strength()
        )[0]
        assert signal_ten_gods(candidate.damage_conditions) == (damage_god,)
    for rescue_god in PATTERN_RESCUE[pattern_name]:
        candidate = calculate_pattern_candidates(
            facts(pattern_ten_god, exposed_signals=(rescue_god,)), strength()
        )[0]
        assert signal_ten_gods(candidate.rescue_conditions) == (rescue_god,)


def test_damage_persists_when_rescue_is_present() -> None:
    candidate = calculate_pattern_candidates(
        facts("正官", exposed_signals=("伤官", "正印")), strength()
    )[0]
    assert candidate.reasoning.status == "disputed"
    assert candidate.reasoning.confidence == "medium"
    assert candidate.damage_conditions == ("exposed:year:丁:伤官",)
    assert candidate.rescue_conditions == ("exposed:month:癸:正印",)


def test_canonical_hidden_damage_is_latent_context_only() -> None:
    candidate = calculate_pattern_candidates(
        facts("正官", other_hidden_branches=("午",)), strength()
    )[0]
    assert candidate.reasoning.status == "computed"
    assert candidate.damage_conditions == ()
    assert (
        "latent_damage_context:hidden:year:午:main:丁:伤官"
        in candidate.reasoning.assumptions
    )


@pytest.mark.parametrize(
    ("upstream", "expected"),
    [("indeterminate", "indeterminate"), ("disputed", "disputed"),
     ("not_computed", "not_computed")],
)
def test_strength_status_is_propagated(
    upstream: ComputationStatus, expected: ComputationStatus
) -> None:
    candidate = calculate_pattern_candidates(
        facts(), strength(status=upstream)
    )[0]
    assert candidate.reasoning.status == expected
    assert candidate.reasoning.confidence == "low"
    assert f"prerequisite:strength:{upstream}" in candidate.reasoning.assumptions


@pytest.mark.parametrize(
    ("label", "pattern_id"),
    [("强", "follow.congqiang"), ("弱", "follow.congruo")],
)
def test_extreme_strength_adds_guarded_follow_candidate(
    label: str, pattern_id: str
) -> None:
    follow = calculate_pattern_candidates(facts(), strength(label=label))[-1]
    assert follow.pattern_id == pattern_id
    assert follow.reasoning.status == "indeterminate"
    assert follow.reasoning.confidence == "low"


def test_results_are_immutable_and_deterministic() -> None:
    chart = facts("正官", exposed_signals=("正官", "伤官"))
    first = calculate_pattern_candidates(chart, strength(label="强"))
    assert first == calculate_pattern_candidates(chart, strength(label="强"))
    assert all(item.reasoning.status in ALLOWED_STATUSES for item in first)
    with pytest.raises(FrozenInstanceError):
        setattr(first[0], "rank", 99)


@pytest.mark.parametrize(
    ("field_name", "bad_value", "message"),
    [("stem", "X", "invalid exposed stem"),
     ("element", "火", "exposed element mismatch"),
     ("polarity", "yin", "exposed polarity mismatch"),
     ("ten_god", "伤官", "exposed ten_god mismatch")],
)
def test_rejects_corrupt_exposed_fact_identity(
    field_name: str, bad_value: str, message: str
) -> None:
    chart = facts()
    corrupted = replace(chart.exposed_stems[0], **{field_name: bad_value})
    malformed = replace(
        chart, exposed_stems=(corrupted, *chart.exposed_stems[1:])
    )
    with pytest.raises(ValueError, match=message):
        calculate_pattern_candidates(malformed, strength())


@pytest.mark.parametrize(
    ("field_name", "bad_value", "message"),
    [("stem", "甲", "hidden stem/role is not canonical"),
     ("element", "火", "hidden element mismatch"),
     ("polarity", "yang", "hidden polarity mismatch"),
     ("ten_god", "伤官", "hidden ten_god mismatch")],
)
def test_rejects_corrupt_hidden_fact_identity(
    field_name: str, bad_value: str, message: str
) -> None:
    chart = facts()
    corrupted = replace(chart.hidden_stems[0], **{field_name: bad_value})
    malformed = replace(chart, hidden_stems=(corrupted,))
    with pytest.raises(ValueError, match=message):
        calculate_pattern_candidates(malformed, strength())


@pytest.mark.parametrize("roles", [("year", "month", "day"),
                                    ("year", "year", "day", "hour")])
def test_rejects_missing_or_duplicate_exposed_pillar_roles(
    roles: tuple[str, ...]
) -> None:
    malformed = replace(
        facts(),
        exposed_stems=tuple(canonical_stem_fact(role, "甲") for role in roles),
    )
    with pytest.raises(ValueError, match="exactly one exposed stem"):
        calculate_pattern_candidates(malformed, strength())


def test_rejects_day_exposed_stem_different_from_day_master() -> None:
    chart = facts()
    malformed = replace(
        chart,
        exposed_stems=tuple(
            canonical_stem_fact("day", "乙")
            if item.pillar_name == "day" else item
            for item in chart.exposed_stems
        ),
    )
    with pytest.raises(ValueError, match="day exposed stem must match day_master"):
        calculate_pattern_candidates(malformed, strength())


def test_rejects_noncanonical_hidden_role_and_order() -> None:
    chart = facts("正财")
    wrong_role = replace(chart.hidden_stems[1], role="residual")
    with pytest.raises(ValueError, match="hidden stem/role is not canonical"):
        calculate_pattern_candidates(
            replace(chart, hidden_stems=(chart.hidden_stems[0], wrong_role)),
            strength(),
        )
    with pytest.raises(ValueError, match="canonical order"):
        calculate_pattern_candidates(
            replace(chart, hidden_stems=tuple(reversed(chart.hidden_stems))),
            strength(),
        )


@pytest.mark.parametrize(
    ("day_master", "month_branch", "message"),
    [("X", "酉", "invalid day master"), ("甲", "X", "invalid month branch")],
)
def test_rejects_invalid_day_master_or_month_branch(
    day_master: str, month_branch: str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        calculate_pattern_candidates(
            replace(facts(), day_master=day_master, month_branch=month_branch),
            strength(),
        )


def test_rejects_incomplete_month_hidden_table() -> None:
    chart = facts("正财")
    with pytest.raises(ValueError, match="month hidden facts must exactly match"):
        calculate_pattern_candidates(
            replace(chart, hidden_stems=chart.hidden_stems[:1]), strength()
        )


@pytest.mark.parametrize(
    "relation",
    [
        replace(transformed_relation(), state="present"),
        replace(transformed_relation(), blockers=("blocked",)),
        replace(transformed_relation(), transformed_element=""),
        replace(
            transformed_relation(), state="blocked",
            transformed_element="水", blockers=("blocked",)
        ),
    ],
)
def test_rejects_contradictory_relation_payloads(
    relation: BranchRelationResult,
) -> None:
    with pytest.raises(ValueError, match="relation transformation consistency"):
        calculate_pattern_candidates(facts(), strength(), (relation,))


def test_valid_transformation_guards_standard_and_follow_candidates() -> None:
    results = calculate_pattern_candidates(
        facts(), strength(label="强"), (transformed_relation(),)
    )
    assert {item.name for item in results} == {"正官格", "从强候选"}
    assert all(item.reasoning.status == "indeterminate" for item in results)
    assert all(item.reasoning.confidence == "low" for item in results)
    assert all(
        "transformed_relation_pattern_modifier" in item.reasoning.missing_inputs
        for item in results
    )


def test_blocked_relation_is_trace_only_opposition() -> None:
    blocked = replace(
        transformed_relation(),
        state="blocked",
        transformed_element="",
        blockers=("month command blocks transformation",),
    )
    candidate = calculate_pattern_candidates(
        facts(), strength(), (blocked,)
    )[0]
    assert candidate.reasoning.status == "computed"
    assert any("blocker=" in item for item in candidate.reasoning.opposing_signals)
    assert (
        "transformed_relation_pattern_modifier"
        not in candidate.reasoning.missing_inputs
    )
