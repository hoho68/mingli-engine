from itertools import product
from types import MappingProxyType
from typing import Final, Mapping

from mingli_engine.bazi.constants import BRANCHES
from mingli_engine.bazi.result_models import BranchRelationResult
from mingli_engine.models import BaziChart, Pillar


BranchPair = tuple[str, str]
BranchTriple = tuple[str, str, str]


SIX_COMBINATIONS: Final[Mapping[BranchPair, None]] = MappingProxyType(
    {
        ("子", "丑"): None,
        ("寅", "亥"): None,
        ("卯", "戌"): None,
        ("辰", "酉"): None,
        ("巳", "申"): None,
        ("午", "未"): None,
    }
)
SIX_CLASHES: Final[Mapping[BranchPair, None]] = MappingProxyType(
    {
        ("子", "午"): None,
        ("丑", "未"): None,
        ("寅", "申"): None,
        ("卯", "酉"): None,
        ("辰", "戌"): None,
        ("巳", "亥"): None,
    }
)
SIX_HARMS: Final[Mapping[BranchPair, None]] = MappingProxyType(
    {
        ("子", "未"): None,
        ("丑", "午"): None,
        ("寅", "巳"): None,
        ("卯", "辰"): None,
        ("申", "亥"): None,
        ("酉", "戌"): None,
    }
)
SIX_BREAKS: Final[Mapping[BranchPair, None]] = MappingProxyType(
    {
        ("子", "酉"): None,
        ("卯", "午"): None,
        ("辰", "丑"): None,
        ("未", "戌"): None,
        ("寅", "亥"): None,
        ("巳", "申"): None,
    }
)
THREE_COMBINATIONS: Final[Mapping[BranchTriple, str]] = MappingProxyType(
    {
        ("申", "子", "辰"): "水",
        ("亥", "卯", "未"): "木",
        ("寅", "午", "戌"): "火",
        ("巳", "酉", "丑"): "金",
    }
)
THREE_MEETINGS: Final[Mapping[BranchTriple, str]] = MappingProxyType(
    {
        ("亥", "子", "丑"): "水",
        ("寅", "卯", "辰"): "木",
        ("巳", "午", "未"): "火",
        ("申", "酉", "戌"): "金",
    }
)
PAIR_PUNISHMENTS: Final[Mapping[BranchPair, None]] = MappingProxyType(
    {("子", "卯"): None}
)
TRIPLE_PUNISHMENTS: Final[Mapping[BranchTriple, None]] = MappingProxyType(
    {("寅", "巳", "申"): None, ("丑", "未", "戌"): None}
)
SELF_PUNISHMENTS: Final[tuple[str, ...]] = ("辰", "午", "酉", "亥")


_PILLAR_ORDER: Final[tuple[str, ...]] = ("year", "month", "day", "hour")
_PAIR_FAMILIES: Final[tuple[tuple[str, Mapping[BranchPair, None]], ...]] = (
    ("six_combination", SIX_COMBINATIONS),
    ("six_clash", SIX_CLASHES),
    ("six_harm", SIX_HARMS),
    ("six_break", SIX_BREAKS),
)
_FAMILY_ORDER: Final[Mapping[str, int]] = MappingProxyType(
    {
        "six_combination": 0,
        "six_clash": 1,
        "six_harm": 2,
        "six_break": 3,
        "punishment": 4,
        "three_combination": 5,
        "three_meeting": 6,
    }
)


def _validated_pillars(chart: BaziChart) -> tuple[Pillar, ...]:
    if len(chart.pillars) != 4:
        raise ValueError("expected exactly four pillars")

    pillars_by_name = {pillar.name: pillar for pillar in chart.pillars}
    if set(pillars_by_name) != set(_PILLAR_ORDER) or len(pillars_by_name) != 4:
        raise ValueError(
            "expected exactly one year, month, day, and hour pillar"
        )

    pillars = tuple(pillars_by_name[name] for name in _PILLAR_ORDER)
    for pillar in pillars:
        if pillar.earthly_branch not in BRANCHES:
            raise ValueError(f"Invalid branch: {pillar.earthly_branch!r}")
    return pillars


def _position_combinations(
    branches: tuple[str, ...], required: tuple[str, ...]
) -> tuple[tuple[int, ...], ...]:
    positions_by_branch = {
        branch: tuple(
            index for index, present in enumerate(branches) if present == branch
        )
        for branch in required
    }
    if any(not positions_by_branch[branch] for branch in required):
        return ()

    combinations = {
        tuple(sorted(positions))
        for positions in product(
            *(positions_by_branch[branch] for branch in required)
        )
        if len(set(positions)) == len(required)
    }
    return tuple(sorted(combinations))


def _result(
    relation_type: str,
    indexes: tuple[int, ...],
    positions: tuple[tuple[str, str], ...],
    state: str,
    conditions: tuple[str, ...],
    rule_id: str,
) -> BranchRelationResult:
    return BranchRelationResult(
        relation_type=relation_type,
        branches=tuple(positions[index][1] for index in indexes),
        pillar_names=tuple(positions[index][0] for index in indexes),
        state=state,
        transformed_element="",
        conditions=conditions,
        blockers=(),
        rule_id=rule_id,
    )


def detect_branch_relations(
    chart: BaziChart,
) -> tuple[BranchRelationResult, ...]:
    pillars = _validated_pillars(chart)
    return detect_branch_relations_for_positions(
        tuple((pillar.name, pillar.earthly_branch) for pillar in pillars)
    )


def detect_branch_relations_for_positions(
    positions: tuple[tuple[str, str], ...],
) -> tuple[BranchRelationResult, ...]:
    if not isinstance(positions, tuple):
        raise ValueError("positions must be a tuple")
    if len(positions) < 2:
        raise ValueError("at least two positions are required")
    if any(
        not isinstance(position, tuple) or len(position) != 2 for position in positions
    ):
        raise ValueError("each position must be a name and branch tuple")

    names = tuple(position[0] for position in positions)
    if any(not isinstance(name, str) or not name.strip() for name in names):
        raise ValueError("position names must be nonempty")
    if len(set(names)) != len(names):
        raise ValueError("position names must be unique")

    branches = tuple(position[1] for position in positions)
    for branch in branches:
        if branch not in BRANCHES:
            raise ValueError(f"Invalid branch: {branch!r}")

    results: list[BranchRelationResult] = []

    for relation_type, table in _PAIR_FAMILIES:
        for pair in table:
            for indexes in _position_combinations(branches, pair):
                results.append(
                    _result(
                        relation_type,
                        indexes,
                        positions,
                        "present",
                        (f"branches {pair[0]} and {pair[1]} are both present",),
                        f"branch.{relation_type}.{''.join(pair)}",
                    )
                )

    for pair in PAIR_PUNISHMENTS:
        for indexes in _position_combinations(branches, pair):
            results.append(
                _result(
                    "punishment",
                    indexes,
                    positions,
                    "present",
                    (f"punishment pair {''.join(pair)} is present",),
                    f"branch.punishment.{''.join(pair)}",
                )
            )

    for group in TRIPLE_PUNISHMENTS:
        for indexes in _position_combinations(branches, group):
            results.append(
                _result(
                    "punishment",
                    indexes,
                    positions,
                    "present",
                    (f"complete punishment group {''.join(group)} is present",),
                    f"branch.punishment.{''.join(group)}",
                )
            )

    for branch in SELF_PUNISHMENTS:
        branch_indexes = tuple(
            index for index, present in enumerate(branches) if present == branch
        )
        for first_index, first in enumerate(branch_indexes):
            for second in branch_indexes[first_index + 1 :]:
                results.append(
                    _result(
                        "punishment",
                        (first, second),
                        positions,
                        "present",
                        (f"branch {branch} occurs in multiple pillar positions",),
                        f"branch.self_punishment.{branch}",
                    )
                )

    triple_families = (
        ("three_combination", THREE_COMBINATIONS),
        ("three_meeting", THREE_MEETINGS),
    )
    for triple_relation_type, triple_table in triple_families:
        for group, element in triple_table.items():
            for indexes in _position_combinations(branches, group):
                results.append(
                    _result(
                        triple_relation_type,
                        indexes,
                        positions,
                        "active",
                        (
                            f"complete group {''.join(group)} is present; "
                            f"table element={element}; transformation is not assessed",
                        ),
                        f"branch.{triple_relation_type}.{''.join(group)}.{element}",
                    )
                )

    return tuple(
        sorted(
            results,
            key=lambda result: (
                _FAMILY_ORDER[result.relation_type],
                tuple(names.index(name) for name in result.pillar_names),
                result.rule_id,
            ),
        )
    )
