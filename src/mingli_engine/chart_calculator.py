import re
from datetime import datetime

from mingli_engine.calendar_provider import ProviderPillar, calculate_provider_pillars
from mingli_engine.models import BaziChart, BirthProfile, ChartSource, Pillar
from mingli_engine.validation import validate_birth_profile


class ChartCalculationError(ValueError):
    pass


SUPPORTED_GREGORIAN_VALUES = {"gregorian", "solar", "公历"}
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
TIME_PATTERN = re.compile(r"\d{2}:\d{2}")


def _parse_birth_datetime(profile: BirthProfile) -> datetime:
    if not DATE_PATTERN.fullmatch(profile.birth_date):
        raise ChartCalculationError("birth_date must use YYYY-MM-DD")

    if not TIME_PATTERN.fullmatch(profile.birth_time):
        raise ChartCalculationError("birth_time must use HH:MM")

    try:
        parsed_date = datetime.strptime(profile.birth_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ChartCalculationError("birth_date must use YYYY-MM-DD") from exc

    try:
        parsed_time = datetime.strptime(profile.birth_time, "%H:%M").time()
    except ValueError as exc:
        raise ChartCalculationError("birth_time must use HH:MM") from exc

    return datetime.combine(parsed_date, parsed_time)


def _validate_supported_profile(profile: BirthProfile) -> None:
    validation_result = validate_birth_profile(profile)
    if not validation_result.report_ready:
        missing = ", ".join(validation_result.missing_fields)
        raise ChartCalculationError(f"missing required field(s): {missing}")

    normalized_calendar_type = profile.calendar_type.strip().lower()
    if normalized_calendar_type not in SUPPORTED_GREGORIAN_VALUES:
        raise ChartCalculationError(
            "calendar_type must be one of: gregorian, solar, 公历"
        )


def _to_pillar(provider_pillar: ProviderPillar) -> Pillar:
    return Pillar(
        name=provider_pillar.name,
        heavenly_stem=provider_pillar.heavenly_stem,
        earthly_branch=provider_pillar.earthly_branch,
        hidden_stems=list(provider_pillar.hidden_stems),
        ten_god=provider_pillar.ten_god,
        element=provider_pillar.element,
    )


def _five_elements_summary(provider_pillars: list[ProviderPillar]) -> dict[str, str]:
    return {pillar.name: pillar.element for pillar in provider_pillars}


def _get_day_pillar(provider_pillars: list[ProviderPillar]) -> ProviderPillar:
    day_pillars = [pillar for pillar in provider_pillars if pillar.name == "day"]
    if len(day_pillars) != 1:
        raise ChartCalculationError("expected exactly one day pillar")

    return day_pillars[0]


def calculate_bazi_chart(profile: BirthProfile) -> BaziChart:
    _validate_supported_profile(profile)
    birth_datetime = _parse_birth_datetime(profile)
    try:
        provider_pillars = calculate_provider_pillars(birth_datetime)
    except ChartCalculationError:
        raise
    except Exception as exc:
        raise ChartCalculationError("chart calculation failed") from exc

    if len(provider_pillars) != 4:
        raise ChartCalculationError("expected four provider pillars")

    pillars = [_to_pillar(pillar) for pillar in provider_pillars]
    day_pillar = _get_day_pillar(provider_pillars)

    return BaziChart(
        birth_profile=profile,
        chart_source=ChartSource(
            source_type="auto_calculated",
            source_note="由 lunar_python 自动排盘生成，未人工复核。",
            calendar_assumption="按公历生日输入，并按节气划分年月柱。",
            timezone_assumption="按 UTC+08:00 语境解释出生日期与时间。",
            solar_terms_assumption="节气数据由 lunar_python 提供。",
            true_solar_time_applied=False,
            confidence="medium",
        ),
        pillars=pillars,
        day_master=day_pillar.heavenly_stem,
        five_elements_summary=_five_elements_summary(provider_pillars),
        ten_gods_summary="十神信息来自自动排盘结果，可作为后续解读参考。",
        strength_assessment="日主强弱暂未展开评估，建议结合后续规则与人工复核。",
        pattern_candidates=[],
        useful_god_candidates=[],
        luck_cycle_summary="大运流年暂未计算，当前结果仅覆盖本命四柱。",
    )
