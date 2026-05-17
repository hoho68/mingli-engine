import pytest

from mingli_engine.chart_calculator import (
    ChartCalculationError,
    calculate_bazi_chart,
)
from mingli_engine.models import BirthProfile


def complete_profile(**overrides):
    values = {
        "calendar_type": "gregorian",
        "birth_date": "1992-08-18",
        "birth_time": "09:30",
        "birthplace": "上海市",
        "gender": "未指定",
        "focus_topic": "职业规划与长期学习节奏",
    }
    values.update(overrides)
    return BirthProfile(**values)


def test_calculate_bazi_chart_from_complete_gregorian_profile():
    chart = calculate_bazi_chart(complete_profile())

    assert chart.chart_source.source_type == "auto_calculated"
    assert chart.chart_source.confidence == "medium"
    assert chart.chart_source.true_solar_time_applied is False
    assert "未人工复核" in chart.chart_source.source_note
    assert len(chart.pillars) == 4
    assert [
        f"{pillar.heavenly_stem}{pillar.earthly_branch}"
        for pillar in chart.pillars
    ] == ["壬申", "戊申", "丙寅", "癸巳"]
    assert chart.day_master == "丙"


def test_rejects_lunar_calendar_type():
    with pytest.raises(ChartCalculationError, match="calendar_type"):
        calculate_bazi_chart(complete_profile(calendar_type="lunar"))


def test_rejects_invalid_birth_date():
    with pytest.raises(ChartCalculationError, match="birth_date"):
        calculate_bazi_chart(complete_profile(birth_date="1992-02-31"))


def test_rejects_invalid_birth_time():
    with pytest.raises(ChartCalculationError, match="birth_time"):
        calculate_bazi_chart(complete_profile(birth_time="25:99"))


def test_rejects_non_strict_birth_date_format():
    with pytest.raises(ChartCalculationError, match="birth_date"):
        calculate_bazi_chart(complete_profile(birth_date="1992-8-18"))


def test_rejects_non_strict_birth_time_format():
    with pytest.raises(ChartCalculationError, match="birth_time"):
        calculate_bazi_chart(complete_profile(birth_time="9:30"))
