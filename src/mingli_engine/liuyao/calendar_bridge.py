"""Calendar bridge: month command, day ganzhi, and xun-void derivation.

Reuses the existing calendar provider and shares the bazi engine's documented
assumptions (Gregorian input, UTC+08 wall time, no true solar time, range
1901-01-01 through 2099-12-31).
"""

from __future__ import annotations

from datetime import datetime

from mingli_engine.calendar_provider import calculate_provider_pillars
from mingli_engine.liuyao.constants import EARTHLY_BRANCHES, HEAVENLY_STEMS

MIN_CAST_DATE = datetime(1901, 1, 1)
MAX_CAST_DATE = datetime(2099, 12, 31, 23, 59)

DOCUMENTED_ASSUMPTIONS: tuple[str, ...] = (
    "gregorian_utc_plus_8_wall_time",
    "no_true_solar_time",
    "plum_blossom_numeric_casting_documented",
)


class CalendarBridgeError(ValueError):
    """Raised when a casting datetime is out of range or unsupported."""


def parse_cast_datetime(value: str) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except (TypeError, ValueError) as error:
        raise CalendarBridgeError("cast datetime must use YYYY-MM-DDTHH:MM") from error
    if not MIN_CAST_DATE <= parsed <= MAX_CAST_DATE:
        raise CalendarBridgeError("cast datetime is out of range")
    return parsed


def month_command_and_day_ganzhi(moment: datetime) -> tuple[str, str, str]:
    """Return (month_command_branch, day_ganzhi, day_stem) for a cast moment."""
    pillars = calculate_provider_pillars(moment)
    by_name = {pillar.name: pillar for pillar in pillars}
    month_branch = by_name["month"].earthly_branch
    day_ganzhi = by_name["day"].heavenly_stem + by_name["day"].earthly_branch
    return month_branch, day_ganzhi, by_name["day"].heavenly_stem


def xun_void_branches(day_ganzhi: str) -> tuple[str, str]:
    """Return the two void branches for the day's xun (旬)."""
    if len(day_ganzhi) != 2:
        raise CalendarBridgeError("day ganzhi is invalid")
    stem, branch = day_ganzhi[0], day_ganzhi[1]
    if stem not in HEAVENLY_STEMS or branch not in EARTHLY_BRANCHES:
        raise CalendarBridgeError("day ganzhi is invalid")
    cycle_index = None
    for index in range(60):
        if (
            HEAVENLY_STEMS[index % 10] == stem
            and EARTHLY_BRANCHES[index % 12] == branch
        ):
            cycle_index = index
            break
    if cycle_index is None:
        raise CalendarBridgeError("day ganzhi is invalid")
    xun_start = cycle_index - (cycle_index % 10)
    xun_start_branch_index = xun_start % 12
    return (
        EARTHLY_BRANCHES[(xun_start_branch_index - 2) % 12],
        EARTHLY_BRANCHES[(xun_start_branch_index - 1) % 12],
    )
