from dataclasses import dataclass
from datetime import datetime

from lunar_python import Solar  # type: ignore[import-untyped]

from mingli_engine.bazi.constants import BRANCHES, STEMS


_MAX_LUCK_CYCLE_COUNT = 100
_GENDER_VALUES = {"male": 1, "男": 1, "female": 0, "女": 0}


@dataclass(frozen=True)
class ProviderPillar:
    name: str
    heavenly_stem: str
    earthly_branch: str
    hidden_stems: list[str]
    ten_god: str
    element: str

    @property
    def gan_zhi(self) -> str:
        return f"{self.heavenly_stem}{self.earthly_branch}"


@dataclass(frozen=True)
class ProviderLuckCycle:
    forward: bool
    start_years: int
    start_months: int
    start_days: int
    start_hours: int
    start_solar: str
    pillars: tuple[tuple[int, str, int, int, int, int], ...]


def _validate_provider_luck_cycle(result: ProviderLuckCycle, count: int) -> None:
    if not isinstance(result.forward, bool):
        raise RuntimeError("luck-cycle provider returned invalid direction")
    component_ranges = (
        ("start_years", result.start_years, 0, 200),
        ("start_months", result.start_months, 0, 11),
        ("start_days", result.start_days, 0, 30),
        ("start_hours", result.start_hours, 0, 23),
    )
    for name, value, minimum, maximum in component_ranges:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not minimum <= value <= maximum
        ):
            raise RuntimeError(f"luck-cycle provider returned invalid {name}")
    if not result.start_solar:
        raise RuntimeError("luck-cycle provider returned invalid start_solar")
    if len(result.pillars) != count:
        raise RuntimeError(
            f"luck-cycle provider returned {len(result.pillars)} valid pillars; expected {count}"
        )

    previous_end_year: int | None = None
    previous_end_age: int | None = None
    for expected_index, pillar in enumerate(result.pillars, start=1):
        index, gan_zhi, start_year, end_year, start_age, end_age = pillar
        numeric_values = (index, start_year, end_year, start_age, end_age)
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in numeric_values
        ):
            raise RuntimeError("luck-cycle provider returned non-integer pillar data")
        if index != expected_index:
            raise RuntimeError(
                "luck-cycle provider returned non-sequential pillar indexes"
            )
        if (
            not isinstance(gan_zhi, str)
            or len(gan_zhi) != 2
            or gan_zhi[0] not in STEMS
            or gan_zhi[1] not in BRANCHES
        ):
            raise RuntimeError("luck-cycle provider returned invalid gan_zhi")
        if (
            start_year < 1
            or end_year < start_year
            or start_age < 1
            or end_age < start_age
        ):
            raise RuntimeError("luck-cycle provider returned invalid year or age range")
        if previous_end_year is not None and start_year <= previous_end_year:
            raise RuntimeError("luck-cycle provider returned non-chronological years")
        if previous_end_age is not None and start_age <= previous_end_age:
            raise RuntimeError("luck-cycle provider returned non-chronological ages")
        previous_end_year = end_year
        previous_end_age = end_age


def calculate_provider_luck_cycles(
    birth_datetime: datetime,
    gender: str,
    *,
    sect: int = 1,
    count: int = 8,
) -> ProviderLuckCycle:
    if not isinstance(birth_datetime, datetime):
        raise ValueError("birth_datetime must be a datetime")
    if birth_datetime.utcoffset() is not None:
        raise ValueError(
            "birth_datetime must be naive local wall time under chart timezone assumption"
        )
    normalized_gender = gender.strip().casefold() if isinstance(gender, str) else ""
    gender_value = _GENDER_VALUES.get(normalized_gender)
    if gender_value is None:
        raise ValueError(
            "gender must be male/female or 男/女 for luck-cycle calculation"
        )
    if isinstance(sect, bool) or not isinstance(sect, int) or sect not in {1, 2}:
        raise ValueError("sect must be 1 or 2")
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or not 1 <= count <= _MAX_LUCK_CYCLE_COUNT
    ):
        raise ValueError("count must be an integer between 1 and 100")

    try:
        eight_char = (
            Solar.fromYmdHms(
                birth_datetime.year,
                birth_datetime.month,
                birth_datetime.day,
                birth_datetime.hour,
                birth_datetime.minute,
                birth_datetime.second,
            )
            .getLunar()
            .getEightChar()
        )
        yun = eight_char.getYun(gender_value, sect)
        result = ProviderLuckCycle(
            forward=yun.isForward(),
            start_years=yun.getStartYear(),
            start_months=yun.getStartMonth(),
            start_days=yun.getStartDay(),
            start_hours=yun.getStartHour(),
            start_solar=yun.getStartSolar().toYmdHms(),
            pillars=tuple(
                (
                    item.getIndex(),
                    item.getGanZhi(),
                    item.getStartYear(),
                    item.getEndYear(),
                    item.getStartAge(),
                    item.getEndAge(),
                )
                for item in yun.getDaYun(count + 1)
                if item.getIndex() > 0
            ),
        )
    except Exception as exc:
        raise RuntimeError("luck-cycle provider calculation failed") from exc

    _validate_provider_luck_cycle(result, count)
    return result


def calculate_provider_pillars(birth_datetime: datetime) -> list[ProviderPillar]:
    eight_char = (
        Solar.fromYmdHms(
            birth_datetime.year,
            birth_datetime.month,
            birth_datetime.day,
            birth_datetime.hour,
            birth_datetime.minute,
            birth_datetime.second,
        )
        .getLunar()
        .getEightChar()
    )

    return [
        ProviderPillar(
            name="year",
            heavenly_stem=eight_char.getYearGan(),
            earthly_branch=eight_char.getYearZhi(),
            hidden_stems=eight_char.getYearHideGan(),
            ten_god=eight_char.getYearShiShenGan(),
            element=eight_char.getYearWuXing(),
        ),
        ProviderPillar(
            name="month",
            heavenly_stem=eight_char.getMonthGan(),
            earthly_branch=eight_char.getMonthZhi(),
            hidden_stems=eight_char.getMonthHideGan(),
            ten_god=eight_char.getMonthShiShenGan(),
            element=eight_char.getMonthWuXing(),
        ),
        ProviderPillar(
            name="day",
            heavenly_stem=eight_char.getDayGan(),
            earthly_branch=eight_char.getDayZhi(),
            hidden_stems=eight_char.getDayHideGan(),
            ten_god=eight_char.getDayShiShenGan(),
            element=eight_char.getDayWuXing(),
        ),
        ProviderPillar(
            name="hour",
            heavenly_stem=eight_char.getTimeGan(),
            earthly_branch=eight_char.getTimeZhi(),
            hidden_stems=eight_char.getTimeHideGan(),
            ten_god=eight_char.getTimeShiShenGan(),
            element=eight_char.getTimeWuXing(),
        ),
    ]
