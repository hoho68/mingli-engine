import pytest

from mingli_engine.chart_calculator import (
    ChartCalculationError,
    _to_pillar,
    calculate_bazi_chart,
)
from mingli_engine.calendar_provider import ProviderPillar
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


def test_calculate_bazi_chart_discloses_no_true_solar_time_for_boundary_case():
    chart = calculate_bazi_chart(
        complete_profile(
            birth_date="1992-02-04",
            birth_time="04:50",
            birthplace="北京市",
            focus_topic="整体结构观察",
        )
    )

    assert len(chart.pillars) == 4
    assert chart.chart_source.true_solar_time_applied is False
    assert "节气" in chart.chart_source.calendar_assumption
    assert "UTC+08:00" in chart.chart_source.timezone_assumption


def test_normalizes_provider_exceptions(monkeypatch):
    def raise_provider_error(_birth_datetime):
        raise RuntimeError("provider down")

    monkeypatch.setattr(
        "mingli_engine.chart_calculator.calculate_provider_pillars",
        raise_provider_error,
    )

    with pytest.raises(ChartCalculationError, match="chart calculation failed"):
        calculate_bazi_chart(complete_profile())


@pytest.mark.parametrize("calendar_type", [" Solar ", " 公历 "])
def test_accepts_normalized_supported_calendar_type(calendar_type):
    chart = calculate_bazi_chart(complete_profile(calendar_type=calendar_type))

    assert chart.chart_source.source_type == "auto_calculated"


def make_provider_pillar(name, stem):
    return ProviderPillar(
        name=name,
        heavenly_stem=stem,
        earthly_branch=f"{stem}-branch",
        hidden_stems=[f"{stem}-hidden"],
        ten_god=f"{stem}-ten-god",
        element=f"{stem}-element",
    )


def test_uses_day_named_pillar_for_day_master(monkeypatch):
    provider_pillars = [
        make_provider_pillar("day", "D"),
        make_provider_pillar("hour", "H"),
        make_provider_pillar("year", "Y"),
        make_provider_pillar("month", "M"),
    ]
    monkeypatch.setattr(
        "mingli_engine.chart_calculator.calculate_provider_pillars",
        lambda _birth_datetime: provider_pillars,
    )

    chart = calculate_bazi_chart(complete_profile())

    assert chart.day_master == "D"


@pytest.mark.parametrize(
    "provider_pillars",
    [
        [
            make_provider_pillar("year", "Y"),
            make_provider_pillar("month", "M"),
            make_provider_pillar("hour", "H"),
            make_provider_pillar("minute", "I"),
        ],
        [
            make_provider_pillar("year", "Y"),
            make_provider_pillar("month", "M"),
            make_provider_pillar("day", "D"),
            make_provider_pillar("day", "X"),
        ],
    ],
)
def test_rejects_missing_or_duplicate_day_pillars(monkeypatch, provider_pillars):
    monkeypatch.setattr(
        "mingli_engine.chart_calculator.calculate_provider_pillars",
        lambda _birth_datetime: provider_pillars,
    )

    with pytest.raises(ChartCalculationError):
        calculate_bazi_chart(complete_profile())


def test_to_pillar_copies_hidden_stems():
    provider_pillar = make_provider_pillar("day", "D")

    pillar = _to_pillar(provider_pillar)
    provider_pillar.hidden_stems.append("mutated")

    assert pillar.hidden_stems == ["D-hidden"]
