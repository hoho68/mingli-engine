from dataclasses import dataclass
from datetime import datetime

from lunar_python import Solar


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
