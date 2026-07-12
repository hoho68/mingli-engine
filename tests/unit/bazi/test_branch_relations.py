from dataclasses import replace
from typing import Any

import pytest

from mingli_engine.bazi.branch_relations import (
    PAIR_PUNISHMENTS,
    SELF_PUNISHMENTS,
    SIX_BREAKS,
    SIX_CLASHES,
    SIX_COMBINATIONS,
    SIX_HARMS,
    THREE_COMBINATIONS,
    THREE_MEETINGS,
    TRIPLE_PUNISHMENTS,
    detect_branch_relations,
    detect_branch_relations_for_positions,
)
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile, Pillar


PAIR_CASES = (
    (
        "six_combination",
        (
            ("子", "丑"),
            ("寅", "亥"),
            ("卯", "戌"),
            ("辰", "酉"),
            ("巳", "申"),
            ("午", "未"),
        ),
    ),
    (
        "six_clash",
        (
            ("子", "午"),
            ("丑", "未"),
            ("寅", "申"),
            ("卯", "酉"),
            ("辰", "戌"),
            ("巳", "亥"),
        ),
    ),
    (
        "six_harm",
        (
            ("子", "未"),
            ("丑", "午"),
            ("寅", "巳"),
            ("卯", "辰"),
            ("申", "亥"),
            ("酉", "戌"),
        ),
    ),
    (
        "six_break",
        (
            ("子", "酉"),
            ("卯", "午"),
            ("辰", "丑"),
            ("未", "戌"),
            ("寅", "亥"),
            ("巳", "申"),
        ),
    ),
)


def chart_with_branches(*branches: str):
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
    pillars = [
        replace(pillar, earthly_branch=branch)
        for pillar, branch in zip(chart.pillars, branches, strict=True)
    ]
    return replace(chart, pillars=pillars)


@pytest.mark.parametrize(
    ("relation_type", "pair"),
    [
        (relation_type, pair)
        for relation_type, table in PAIR_CASES
        for pair in table
    ],
)
def test_detects_every_pair_relation(
    relation_type: str, pair: tuple[str, str]
) -> None:
    results = detect_branch_relations(chart_with_branches(*pair, "辰", "辰"))
    matches = [result for result in results if result.relation_type == relation_type]

    assert any(
        result.branches == pair
        and result.pillar_names == ("year", "month")
        and result.state == "present"
        and result.transformed_element == ""
        and result.conditions
        and result.blockers == ()
        and result.rule_id == f"branch.{relation_type}.{''.join(pair)}"
        for result in matches
    )


def test_canonical_relation_tables_match_the_declared_rules() -> None:
    tables = {
        "six_combination": SIX_COMBINATIONS,
        "six_clash": SIX_CLASHES,
        "six_harm": SIX_HARMS,
        "six_break": SIX_BREAKS,
    }

    for relation_type, expected_pairs in PAIR_CASES:
        assert tuple(tables[relation_type]) == expected_pairs
    assert dict(THREE_COMBINATIONS) == {
        ("申", "子", "辰"): "水",
        ("亥", "卯", "未"): "木",
        ("寅", "午", "戌"): "火",
        ("巳", "酉", "丑"): "金",
    }
    assert dict(THREE_MEETINGS) == {
        ("亥", "子", "丑"): "水",
        ("寅", "卯", "辰"): "木",
        ("巳", "午", "未"): "火",
        ("申", "酉", "戌"): "金",
    }
    assert tuple(PAIR_PUNISHMENTS) == (("子", "卯"),)
    assert tuple(TRIPLE_PUNISHMENTS) == (("寅", "巳", "申"), ("丑", "未", "戌"))
    assert SELF_PUNISHMENTS == ("辰", "午", "酉", "亥")


def test_detects_pair_punishment() -> None:
    results = detect_branch_relations(chart_with_branches("子", "卯", "申", "辰"))

    punishment = next(
        result
        for result in results
        if result.rule_id == "branch.punishment.子卯"
    )
    assert punishment.relation_type == "punishment"
    assert punishment.branches == ("子", "卯")
    assert punishment.pillar_names == ("year", "month")
    assert punishment.state == "present"


@pytest.mark.parametrize("group", TRIPLE_PUNISHMENTS)
def test_detects_only_complete_triple_punishments(group: tuple[str, str, str]) -> None:
    complete = detect_branch_relations(chart_with_branches(*group, "子"))
    incomplete = detect_branch_relations(
        chart_with_branches(group[0], group[1], "子", "亥")
    )

    rule_id = f"branch.punishment.{''.join(group)}"
    result = next(item for item in complete if item.rule_id == rule_id)
    assert result.branches == group
    assert result.pillar_names == ("year", "month", "day")
    assert result.state == "present"
    assert all(item.rule_id != rule_id for item in incomplete)


@pytest.mark.parametrize("branch", SELF_PUNISHMENTS)
def test_detects_each_self_punishment_only_for_duplicates(branch: str) -> None:
    duplicate = detect_branch_relations(
        chart_with_branches(branch, branch, "子", "丑")
    )
    single = detect_branch_relations(chart_with_branches(branch, "子", "丑", "寅"))

    rule_id = f"branch.self_punishment.{branch}"
    result = next(item for item in duplicate if item.rule_id == rule_id)
    assert result.relation_type == "punishment"
    assert result.branches == (branch, branch)
    assert result.pillar_names == ("year", "month")
    assert result.state == "present"
    assert all(item.rule_id != rule_id for item in single)


@pytest.mark.parametrize(
    ("relation_type", "table"),
    (("three_combination", THREE_COMBINATIONS), ("three_meeting", THREE_MEETINGS)),
)
@pytest.mark.parametrize("group_index", range(4))
def test_detects_complete_active_triples_without_claiming_transformation(
    relation_type: str,
    table: Any,
    group_index: int,
) -> None:
    group, element = tuple(table.items())[group_index]
    results = detect_branch_relations(chart_with_branches(*group, "辰"))

    rule_id = f"branch.{relation_type}.{''.join(group)}.{element}"
    result = next(item for item in results if item.rule_id == rule_id)
    assert result.relation_type == relation_type
    assert result.branches == group
    assert result.pillar_names == ("year", "month", "day")
    assert result.state == "active"
    assert result.transformed_element == ""
    assert element in " ".join(result.conditions)
    assert result.blockers == ()


@pytest.mark.parametrize(
    ("relation_type", "table"),
    (("three_combination", THREE_COMBINATIONS), ("three_meeting", THREE_MEETINGS)),
)
def test_incomplete_triples_emit_no_half_relation(
    relation_type: str, table: Any
) -> None:
    group = next(iter(table))

    results = detect_branch_relations(
        chart_with_branches(group[0], group[1], "巳", "午")
    )

    assert all(result.relation_type != relation_type for result in results)


def test_duplicate_positions_emit_distinct_pair_and_triple_combinations() -> None:
    pair_results = detect_branch_relations(
        chart_with_branches("子", "丑", "子", "丑")
    )
    triples = detect_branch_relations(chart_with_branches("申", "子", "辰", "申"))

    combinations = [
        result
        for result in pair_results
        if result.rule_id == "branch.six_combination.子丑"
    ]
    assert [result.pillar_names for result in combinations] == [
        ("year", "month"),
        ("year", "hour"),
        ("month", "day"),
        ("day", "hour"),
    ]
    assert [result.branches for result in combinations] == [
        ("子", "丑"),
        ("子", "丑"),
        ("丑", "子"),
        ("子", "丑"),
    ]

    water_triples = [
        result
        for result in triples
        if result.rule_id == "branch.three_combination.申子辰.水"
    ]
    assert [result.pillar_names for result in water_triples] == [
        ("year", "month", "day"),
        ("month", "day", "hour"),
    ]
    assert [result.branches for result in water_triples] == [
        ("申", "子", "辰"),
        ("子", "辰", "申"),
    ]


def test_results_are_ordered_by_family_then_canonical_pillar_positions() -> None:
    chart = chart_with_branches("卯", "子", "午", "酉")
    reordered = replace(
        chart,
        pillars=[
            chart.pillars[2],
            chart.pillars[0],
            chart.pillars[3],
            chart.pillars[1],
        ],
    )

    results = detect_branch_relations(chart)

    assert results == detect_branch_relations(reordered)
    assert [(result.relation_type, result.pillar_names) for result in results] == [
        ("six_clash", ("year", "hour")),
        ("six_clash", ("month", "day")),
        ("six_break", ("year", "day")),
        ("six_break", ("month", "hour")),
        ("punishment", ("year", "month")),
    ]


@pytest.mark.parametrize(
    "table",
    [
        SIX_COMBINATIONS,
        SIX_CLASHES,
        SIX_HARMS,
        SIX_BREAKS,
        THREE_COMBINATIONS,
        THREE_MEETINGS,
        PAIR_PUNISHMENTS,
        TRIPLE_PUNISHMENTS,
    ],
)
def test_relation_tables_are_read_only(table: Any) -> None:
    with pytest.raises(TypeError):
        table[next(iter(table))] = object()


def test_self_punishment_table_is_immutable() -> None:
    table: Any = SELF_PUNISHMENTS
    with pytest.raises(TypeError):
        table[0] = "子"


@pytest.mark.parametrize(
    "branches",
    [("子", "丑", "寅"), ("子", "丑", "寅", "卯", "辰")],
)
def test_requires_exactly_four_pillars(branches: tuple[str, ...]) -> None:
    chart = chart_with_branches("子", "丑", "寅", "卯")
    pillars = [
        replace(chart.pillars[index % 4], earthly_branch=branch)
        for index, branch in enumerate(branches)
    ]

    with pytest.raises(ValueError, match="^expected exactly four pillars$"):
        detect_branch_relations(replace(chart, pillars=pillars))


@pytest.mark.parametrize(
    "names",
    [
        ("year", "month", "day", "day"),
        ("year", "month", "day", "unknown"),
    ],
)
def test_requires_each_canonical_pillar_role_once(names: tuple[str, ...]) -> None:
    chart = chart_with_branches("子", "丑", "寅", "卯")
    pillars = [
        replace(pillar, name=name)
        for pillar, name in zip(chart.pillars, names, strict=True)
    ]

    with pytest.raises(
        ValueError,
        match="^expected exactly one year, month, day, and hour pillar$",
    ):
        detect_branch_relations(replace(chart, pillars=pillars))


def test_rejects_invalid_branches() -> None:
    chart = chart_with_branches("子", "丑", "寅", "卯")
    invalid = Pillar(
        name="hour",
        heavenly_stem="甲",
        earthly_branch="invalid",
        hidden_stems=[],
        ten_god="",
        element="",
    )

    with pytest.raises(ValueError, match="^Invalid branch: 'invalid'$"):
        detect_branch_relations(replace(chart, pillars=[*chart.pillars[:3], invalid]))


def test_generic_position_detection_matches_canonical_chart_detection() -> None:
    chart = chart_with_branches("午", "子", "午", "酉")
    positions = tuple(
        (pillar.name, pillar.earthly_branch)
        for pillar in (
            chart.pillars[2],
            chart.pillars[0],
            chart.pillars[3],
            chart.pillars[1],
        )
    )

    assert detect_branch_relations_for_positions(positions) != detect_branch_relations(
        chart
    )
    assert detect_branch_relations_for_positions(
        tuple(
            (name, next(p for p in chart.pillars if p.name == name).earthly_branch)
            for name in ("year", "month", "day", "hour")
        )
    ) == detect_branch_relations(chart)


def test_generic_position_detection_preserves_extra_positions_and_duplicates() -> None:
    positions = (
        ("year", "子"),
        ("month", "寅"),
        ("day", "午"),
        ("hour", "酉"),
        ("active_luck_2", "午"),
        ("selected_year_2031", "卯"),
    )

    first = detect_branch_relations_for_positions(positions)
    second = detect_branch_relations_for_positions(positions)

    assert first == second
    assert any(
        result.branches == ("午", "午")
        and result.pillar_names == ("day", "active_luck_2")
        for result in first
    )
    assert any(
        "selected_year_2031" in result.pillar_names
        and "active_luck_2" in result.pillar_names
        for result in first
    )


@pytest.mark.parametrize(
    ("positions", "message"),
    [
        ([("year", "子"), ("month", "丑")], "positions must be a tuple"),
        ((("year", "子"),), "at least two positions are required"),
        ((("year", "子"), ("year", "丑")), "position names must be unique"),
        ((("", "子"), ("month", "丑")), "position names must be nonempty"),
        ((("year", "invalid"), ("month", "丑")), "Invalid branch: 'invalid'"),
    ],
)
def test_generic_position_detection_validates_inputs(
    positions: Any, message: str
) -> None:
    with pytest.raises(ValueError, match=f"^{message}$"):
        detect_branch_relations_for_positions(positions)
