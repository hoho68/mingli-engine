"""Najia assembly: from six lines to a complete liuyao chart."""

from __future__ import annotations

from mingli_engine.liuyao.constants import (
    BRANCH_ELEMENTS,
    DAY_STEM_SPIRIT_START,
    EARTHLY_BRANCHES,
    EIGHT_PALACES,
    NAJIA_GANZHI,
    PALACE_SEQUENCE_NAMES,
    SHI_POSITION_BY_SEQUENCE,
    SIX_SPIRITS,
    TRIGRAM_ELEMENTS,
    TRIGRAM_LINES,
    palace_gua_lines,
    six_relation,
)
from mingli_engine.liuyao.result_models import (
    GuaInfo,
    HiddenSpirit,
    LiuyaoLine,
)


class NajiaError(ValueError):
    """Raised when a liuyao assembly input is invalid."""


def _trigram_of(lines: tuple[int, ...]) -> str:
    for name, trigram_lines in TRIGRAM_LINES.items():
        if tuple(lines) == trigram_lines:
            return name
    raise NajiaError("the line triplet does not form a trigram")


def gua_info_from_lines(lines: tuple[int, ...]) -> GuaInfo:
    """Look up the gua for six bottom-up line values."""
    if len(lines) != 6 or set(lines) - {0, 1}:
        raise NajiaError("a gua requires exactly six binary lines")
    lower = _trigram_of(lines[:3])
    upper = _trigram_of(lines[3:])
    for palace in EIGHT_PALACES:
        for sequence, gua_name in enumerate(PALACE_SEQUENCE_NAMES[palace]):
            if palace_gua_lines(palace, sequence) == tuple(lines):
                shi = SHI_POSITION_BY_SEQUENCE[sequence]
                ying = shi + 3 if shi <= 3 else shi - 3
                return GuaInfo(
                    gua_name=gua_name,
                    upper_trigram=upper,
                    lower_trigram=lower,
                    palace=palace,
                    palace_sequence=sequence,
                    shi_position=shi,
                    ying_position=ying,
                )
    raise NajiaError("the six lines do not match any palace gua")


def _line_ganzhi(gua: GuaInfo, position: int) -> str:
    if position <= 3:
        return NAJIA_GANZHI[gua.lower_trigram]["inner"][position - 1]
    return NAJIA_GANZHI[gua.upper_trigram]["outer"][position - 4]


def _hidden_spirits(
    gua: GuaInfo,
    line_relations: tuple[str, ...],
) -> dict[int, HiddenSpirit]:
    palace_head = gua_info_from_lines(palace_gua_lines(gua.palace, 0))
    present = set(line_relations)
    hidden: dict[int, HiddenSpirit] = {}
    for position in range(1, 7):
        head_ganzhi = _line_ganzhi(palace_head, position)
        head_relation = six_relation(
            _palace_element(gua.palace),
            head_ganzhi[1],
        )
        if head_relation not in present:
            hidden[position] = HiddenSpirit(
                ganzhi=head_ganzhi,
                six_relation=head_relation,
                attached_position=position,
            )
    return hidden


def _palace_element(palace: str) -> str:
    return TRIGRAM_ELEMENTS[palace]


def assemble_chart_lines(
    gua: GuaInfo,
    line_values: tuple[int, ...],
    moving_positions: frozenset[int],
    *,
    day_stem: str,
    xun_void_branches: frozenset[str],
    month_command: str,
    day_branch: str,
) -> tuple[LiuyaoLine, ...]:
    """Assemble the six fully annotated lines of a gua."""
    if len(line_values) != 6:
        raise NajiaError("assembly requires exactly six line values")
    spirit_start = DAY_STEM_SPIRIT_START.get(day_stem)
    if spirit_start is None:
        raise NajiaError("the day stem is invalid")
    spirit_offset = SIX_SPIRITS.index(spirit_start)
    month_index = _branch_index(month_command)
    day_index = _branch_index(day_branch)
    relations = tuple(
        six_relation(_palace_element(gua.palace), _line_ganzhi(gua, position)[1])
        for position in range(1, 7)
    )
    hidden = _hidden_spirits(gua, relations)
    lines: list[LiuyaoLine] = []
    for position in range(1, 7):
        ganzhi = _line_ganzhi(gua, position)
        branch = ganzhi[1]
        branch_index = _branch_index(branch)
        moving = position in moving_positions
        lines.append(
            LiuyaoLine(
                position=position,
                yin_yang="yang" if line_values[position - 1] else "yin",
                moving=moving,
                ganzhi=ganzhi,
                element=BRANCH_ELEMENTS[branch],
                six_relation=relations[position - 1],
                six_spirit=SIX_SPIRITS[(spirit_offset + position - 1) % 6],
                shi_ying=(
                    "shi"
                    if position == gua.shi_position
                    else "ying"
                    if position == gua.ying_position
                    else ""
                ),
                hidden_spirit=hidden.get(position),
                void=branch in xun_void_branches,
                month_break=(branch_index - month_index) % 12 == 6,
                day_break=(branch_index - day_index) % 12 == 6 and not moving,
            )
        )
    return tuple(lines)


def _branch_index(branch: str) -> int:
    try:
        return EARTHLY_BRANCHES.index(branch)
    except ValueError as error:
        raise NajiaError(f"unknown earthly branch: {branch}") from error


def derive_bian_gua(
    line_values: tuple[int, ...],
    moving_positions: frozenset[int],
) -> GuaInfo | None:
    """Derive the changed gua from moving lines, or None when static."""
    if not moving_positions:
        return None
    changed = list(line_values)
    for position in moving_positions:
        changed[position - 1] = 1 - changed[position - 1]
    return gua_info_from_lines(tuple(changed))


def derive_hu_gua(line_values: tuple[int, ...]) -> GuaInfo:
    """Derive the nuclear gua (lines 2-3-4 lower, 3-4-5 upper)."""
    nuclear = (
        line_values[1],
        line_values[2],
        line_values[3],
        line_values[2],
        line_values[3],
        line_values[4],
    )
    return gua_info_from_lines(nuclear)
