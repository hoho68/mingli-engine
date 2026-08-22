"""Casting: explicit lines, time casting, and number casting → one chart."""

from __future__ import annotations

from mingli_engine.liuyao.calendar_bridge import (
    DOCUMENTED_ASSUMPTIONS,
    month_command_and_day_ganzhi,
    parse_cast_datetime,
    xun_void_branches,
)
from mingli_engine.liuyao.constants import XIANTIAN_TRIGRAMS, TRIGRAM_LINES
from mingli_engine.liuyao.najia import (
    assemble_chart_lines,
    derive_bian_gua,
    derive_hu_gua,
    gua_info_from_lines,
)
from mingli_engine.liuyao.result_models import (
    LiuyaoCastRequest,
    LiuyaoChart,
    LiuyaoLineInput,
)


class CastingError(ValueError):
    """Raised when a cast request cannot be fulfilled."""


def _lines_to_values(
    lines: tuple[LiuyaoLineInput, ...],
) -> tuple[tuple[int, ...], frozenset[int]]:
    ordered = tuple(sorted(lines, key=lambda line: line.position))
    values = tuple(1 if line.yin_yang == "yang" else 0 for line in ordered)
    moving = frozenset(line.position for line in ordered if line.moving)
    return values, moving


def _trigram_by_xiantian(number: int) -> tuple[int, int, int]:
    index = number % 8 or 8
    return TRIGRAM_LINES[XIANTIAN_TRIGRAMS[index - 1]]


def _cast_time(moment) -> tuple[tuple[int, ...], frozenset[int]]:
    from lunar_python import Solar  # type: ignore[import-untyped]

    lunar = Solar.fromYmdHms(
        moment.year, moment.month, moment.day, moment.hour, moment.minute, 0
    ).getLunar()
    year_branch = lunar.getYearInGanZhi()[1]
    year_number = _branch_number(year_branch)
    month_number = abs(lunar.getMonth())
    day_number = lunar.getDay()
    hour_branch_number = (moment.hour + 1) // 2 % 12 + 1
    upper = (year_number + month_number + day_number) % 8 or 8
    lower = (year_number + month_number + day_number + hour_branch_number) % 8 or 8
    moving = (year_number + month_number + day_number + hour_branch_number) % 6 or 6
    lower_lines = _trigram_by_xiantian(lower)
    upper_lines = _trigram_by_xiantian(upper)
    values = lower_lines + upper_lines
    return values, frozenset({moving})


def _cast_number(numbers: tuple[int, ...]) -> tuple[tuple[int, ...], frozenset[int]]:
    first, second = numbers
    upper = first % 8 or 8
    lower = second % 8 or 8
    moving = (first + second) % 6 or 6
    values = _trigram_by_xiantian(lower) + _trigram_by_xiantian(upper)
    return values, frozenset({moving})


def _branch_number(branch: str) -> int:
    from mingli_engine.liuyao.constants import EARTHLY_BRANCHES

    try:
        return EARTHLY_BRANCHES.index(branch) + 1
    except ValueError as error:
        raise CastingError(f"unknown earthly branch: {branch}") from error


def assemble_liuyao_chart(request: LiuyaoCastRequest) -> LiuyaoChart:
    """Assemble a complete liuyao chart from a validated cast request."""
    if not isinstance(request, LiuyaoCastRequest):
        raise TypeError("request must be a LiuyaoCastRequest")
    moment = parse_cast_datetime(request.cast_datetime)
    if request.cast_mode == "explicit":
        values, moving = _lines_to_values(request.lines)
    elif request.cast_mode == "time":
        values, moving = _cast_time(moment)
    else:
        values, moving = _cast_number(request.numbers)
    ben_gua = gua_info_from_lines(values)
    month_command, day_ganzhi, day_stem = month_command_and_day_ganzhi(moment)
    void_pair = xun_void_branches(day_ganzhi)
    void = frozenset(void_pair)
    lines = assemble_chart_lines(
        ben_gua,
        values,
        moving,
        day_stem=day_stem,
        xun_void_branches=void,
        month_command=month_command,
        day_branch=day_ganzhi[1],
    )
    return LiuyaoChart(
        cast_mode=request.cast_mode,
        cast_datetime=request.cast_datetime,
        ben_gua=ben_gua,
        bian_gua=derive_bian_gua(values, moving),
        hu_gua=derive_hu_gua(values),
        lines=lines,
        month_command=month_command,
        day_ganzhi=day_ganzhi,
        xun_void_branches=void_pair,
        assumptions=DOCUMENTED_ASSUMPTIONS,
        request_id=request.request_id,
    )
