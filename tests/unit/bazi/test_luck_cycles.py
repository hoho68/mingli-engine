import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from mingli_engine.calendar_provider import (
    ProviderLuckCycle,
    calculate_provider_luck_cycles,
)
from mingli_engine.bazi.luck_cycles import calculate_luck_cycles
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile


FIXTURE_PATH = (
    Path(__file__).parents[2]
    / "fixtures"
    / "bazi_calculation"
    / "luck_cycle_boundary_cases.json"
)


def _fixture_cases() -> list[dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", _fixture_cases(), ids=lambda case: case["id"])
def test_provider_luck_cycles_match_frozen_regression_cases(
    case: dict[str, Any],
) -> None:
    expected = case["expected"]

    result = calculate_provider_luck_cycles(
        datetime.fromisoformat(case["birth_datetime"]),
        case["gender"],
        sect=case["sect"],
        count=2,
    )

    assert result.forward is expected["forward"]
    assert result.start_years == expected["start_years"]
    assert result.start_months == expected["start_months"]
    assert result.start_days == expected["start_days"]
    assert result.start_hours == expected["start_hours"]
    assert result.start_solar == expected["start_solar"]
    assert result.pillars == tuple(tuple(item) for item in expected["pillars"])


def test_provider_luck_cycle_dto_is_immutable() -> None:
    result = calculate_provider_luck_cycles(
        datetime(1992, 8, 18, 9, 30), "male", count=2
    )

    assert isinstance(result, ProviderLuckCycle)
    with pytest.raises(FrozenInstanceError):
        result.forward = False  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.pillars[0][0] = 9  # type: ignore[index]


def test_provider_supports_declared_max_count_with_forward_modulo_sequence() -> None:
    result = calculate_provider_luck_cycles(
        datetime(1992, 8, 18, 9, 30), "male", count=100
    )

    assert len(result.pillars) == 100
    assert result.pillars[:2] == (
        (1, "己酉", 1999, 2008, 8, 17),
        (2, "庚戌", 2009, 2018, 18, 27),
    )
    assert result.pillars[60][1] == result.pillars[0][1]
    assert result.pillars[99][1] == result.pillars[39][1]


def test_provider_max_count_preserves_reverse_modulo_sequence() -> None:
    result = calculate_provider_luck_cycles(
        datetime(1991, 6, 15, 12), "male", sect=2, count=100
    )

    assert len(result.pillars) == 100
    assert result.pillars[:2] == (
        (1, "癸巳", 1994, 2003, 4, 13),
        (2, "壬辰", 2004, 2013, 14, 23),
    )
    assert result.pillars[60][1] == result.pillars[0][1]
    assert result.pillars[99][1] == result.pillars[39][1]


@pytest.mark.parametrize(
    ("alias", "canonical"),
    [(" MALE ", "male"), ("男", "male"), (" Female ", "female"), ("女", "female")],
)
def test_provider_normalizes_supported_gender_aliases(
    alias: str, canonical: str
) -> None:
    birth_datetime = datetime(1992, 8, 18, 9, 30)

    assert calculate_provider_luck_cycles(
        birth_datetime, alias, count=2
    ) == calculate_provider_luck_cycles(birth_datetime, canonical, count=2)


@pytest.mark.parametrize("gender", ["", "unspecified", "unknown", 1, None])
def test_provider_rejects_unsupported_gender(gender: Any) -> None:
    with pytest.raises(
        ValueError,
        match="^gender must be male/female or 男/女 for luck-cycle calculation$",
    ):
        calculate_provider_luck_cycles(datetime(1992, 8, 18, 9, 30), gender)


@pytest.mark.parametrize(
    ("keyword", "value", "message"),
    [
        ("sect", 0, "sect must be 1 or 2"),
        ("sect", 3, "sect must be 1 or 2"),
        ("sect", True, "sect must be 1 or 2"),
        ("count", 0, "count must be an integer between 1 and 100"),
        ("count", 101, "count must be an integer between 1 and 100"),
        ("count", True, "count must be an integer between 1 and 100"),
    ],
)
def test_provider_validates_sect_and_count(
    keyword: str, value: Any, message: str
) -> None:
    kwargs = {keyword: value}
    with pytest.raises(ValueError, match=f"^{message}$"):
        calculate_provider_luck_cycles(datetime(1992, 8, 18, 9, 30), "male", **kwargs)


def test_provider_requires_datetime() -> None:
    with pytest.raises(ValueError, match="^birth_datetime must be a datetime$"):
        calculate_provider_luck_cycles("1992-08-18T09:30:00", "male")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "tzinfo",
    [timezone(timedelta(hours=8)), timezone.utc, timezone(timedelta(hours=-5))],
    ids=["utc_plus_8", "utc", "utc_minus_5"],
)
def test_provider_rejects_aware_datetime_before_lunar_call(
    tzinfo: timezone, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*args: Any) -> None:
        raise AssertionError("Solar must not be called for aware datetime")

    monkeypatch.setattr("mingli_engine.calendar_provider.Solar.fromYmdHms", fail)

    with pytest.raises(
        ValueError,
        match=(
            "^birth_datetime must be naive local wall time under chart timezone "
            "assumption$"
        ),
    ):
        calculate_provider_luck_cycles(
            datetime(1992, 8, 18, 9, 30, tzinfo=tzinfo), "male"
        )


def test_provider_wraps_lunar_exceptions_with_stable_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: Any) -> None:
        raise LookupError("provider detail")

    monkeypatch.setattr("mingli_engine.calendar_provider.Solar.fromYmdHms", fail)

    with pytest.raises(
        RuntimeError, match="^luck-cycle provider calculation failed$"
    ) as exc_info:
        calculate_provider_luck_cycles(datetime(1992, 8, 18, 9, 30), "male")

    assert isinstance(exc_info.value.__cause__, LookupError)


def _chart_for(
    birth_date: str,
    birth_time: str,
    gender: str,
):
    chart = calculate_bazi_chart(
        BirthProfile(
            calendar_type="gregorian",
            birth_date=birth_date,
            birth_time=birth_time,
            birthplace="Shanghai",
            gender=gender or "male",
            focus_topic="structure",
        )
    )
    if chart.birth_profile.gender != gender:
        chart = replace(
            chart, birth_profile=replace(chart.birth_profile, gender=gender)
        )
    return chart


def _chart(gender: str = "male"):
    return _chart_for("1992-08-18", "09:30", gender)


def test_luck_cycles_degrade_when_birth_datetime_is_missing() -> None:
    result = calculate_luck_cycles(_chart())

    assert result.reasoning.status == "not_computed"
    assert result.reasoning.confidence == "low"
    assert result.reasoning.missing_inputs == ("birth_datetime",)
    assert result.pillars == ()
    assert result.selected_year_relations == ()


@pytest.mark.parametrize("gender", ["", "unspecified", "unknown"])
def test_luck_cycles_degrade_for_unsupported_chart_gender(gender: str) -> None:
    result = calculate_luck_cycles(
        _chart(gender), birth_datetime=datetime(1992, 8, 18, 9, 30)
    )

    assert result.reasoning.status == "not_computed"
    assert result.reasoning.confidence == "low"
    assert result.reasoning.missing_inputs == ("supported_gender",)
    assert result.pillars == ()


def test_unsupported_gender_degrades_before_chart_datetime_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chart = _chart("unsupported")
    mismatched = replace(chart.pillars[0], heavenly_stem="甲")

    def fail(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("provider must not be called for unsupported gender")

    monkeypatch.setattr(
        "mingli_engine.bazi.luck_cycles.calculate_provider_pillars", fail
    )
    monkeypatch.setattr(
        "mingli_engine.bazi.luck_cycles.calculate_provider_luck_cycles", fail
    )

    result = calculate_luck_cycles(
        replace(chart, pillars=[mismatched, *chart.pillars[1:]]),
        birth_datetime=datetime(1992, 8, 18, 9, 30),
    )

    assert result.reasoning.status == "not_computed"
    assert result.reasoning.confidence == "low"
    assert result.reasoning.missing_inputs == ("supported_gender",)
    assert result.pillars == ()
    assert result.selected_year_relations == ()


def test_unsupported_gender_degrades_before_failing_natal_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise LookupError("provider detail")

    monkeypatch.setattr(
        "mingli_engine.bazi.luck_cycles.calculate_provider_pillars", fail
    )

    result = calculate_luck_cycles(
        _chart("unsupported"), birth_datetime=datetime(1992, 8, 18, 9, 30)
    )

    assert result.reasoning.status == "not_computed"
    assert result.reasoning.confidence == "low"
    assert result.reasoning.missing_inputs == ("supported_gender",)
    assert result.pillars == ()
    assert result.selected_year_relations == ()


def test_unsupported_gender_degrades_before_profile_datetime_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("provider must not be called for unsupported gender")

    monkeypatch.setattr(
        "mingli_engine.bazi.luck_cycles.calculate_provider_pillars", fail
    )
    monkeypatch.setattr(
        "mingli_engine.bazi.luck_cycles.calculate_provider_luck_cycles", fail
    )

    result = calculate_luck_cycles(
        _chart("unsupported"), birth_datetime=datetime(1992, 8, 18, 9, 31)
    )

    assert result.reasoning.status == "not_computed"
    assert result.reasoning.missing_inputs == ("supported_gender",)


@pytest.mark.parametrize(
    "birth_datetime",
    [datetime(1992, 8, 18, 9, 31), datetime(1992, 8, 18, 10, 30)],
    ids=["minute_mismatch", "hour_mismatch"],
)
def test_supported_gender_requires_exact_profile_datetime_before_provider(
    birth_datetime: datetime, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("provider must not be called for profile mismatch")

    monkeypatch.setattr(
        "mingli_engine.bazi.luck_cycles.calculate_provider_pillars", fail
    )
    monkeypatch.setattr(
        "mingli_engine.bazi.luck_cycles.calculate_provider_luck_cycles", fail
    )

    with pytest.raises(
        ValueError,
        match=(
            "^birth_datetime must exactly match chart birth_profile birth_date and "
            "birth_time$"
        ),
    ):
        calculate_luck_cycles(_chart(), birth_datetime=birth_datetime)


def test_supported_gender_accepts_exact_profile_datetime() -> None:
    result = calculate_luck_cycles(
        _chart(), birth_datetime=datetime(1992, 8, 18, 9, 30), count=2
    )

    assert result.reasoning.status == "computed"


@pytest.mark.parametrize(
    "tzinfo",
    [timezone(timedelta(hours=8)), timezone.utc, timezone(timedelta(hours=-5))],
    ids=["utc_plus_8", "utc", "utc_minus_5"],
)
def test_high_level_rejects_aware_datetime_before_natal_provider(
    tzinfo: timezone, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("natal provider must not be called for aware datetime")

    monkeypatch.setattr(
        "mingli_engine.bazi.luck_cycles.calculate_provider_pillars", fail
    )

    with pytest.raises(
        ValueError,
        match=(
            "^birth_datetime must be naive local wall time under chart timezone "
            "assumption$"
        ),
    ):
        calculate_luck_cycles(
            _chart(),
            birth_datetime=datetime(1992, 8, 18, 9, 30, tzinfo=tzinfo),
        )


def test_natal_provider_exceptions_are_wrapped_with_stable_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise LookupError("provider detail")

    monkeypatch.setattr(
        "mingli_engine.bazi.luck_cycles.calculate_provider_pillars", fail
    )

    with pytest.raises(
        RuntimeError, match="^natal-pillar provider calculation failed$"
    ) as exc_info:
        calculate_luck_cycles(
            _chart(), birth_datetime=datetime(1992, 8, 18, 9, 30)
        )

    assert isinstance(exc_info.value.__cause__, LookupError)


def test_luck_cycles_reject_chart_and_datetime_mismatch() -> None:
    chart = _chart()
    mismatched = replace(chart.pillars[0], heavenly_stem="甲")

    with pytest.raises(ValueError, match="^chart pillars do not match birth_datetime$"):
        calculate_luck_cycles(
            replace(chart, pillars=[mismatched, *chart.pillars[1:]]),
            birth_datetime=datetime(1992, 8, 18, 9, 30),
        )


def test_luck_cycles_map_real_provider_pipeline_and_trace_start_hours() -> None:
    result = calculate_luck_cycles(
        _chart(), birth_datetime=datetime(1992, 8, 18, 9, 30), count=2
    )

    assert result.reasoning.status == "computed"
    assert result.forward is True
    assert (result.start_years, result.start_months, result.start_days) == (6, 9, 10)
    assert result.start_solar == "1999-05-28 09:30:00"
    assert tuple(
        (p.index, p.gan_zhi, p.start_year, p.end_year, p.start_age, p.end_age)
        for p in result.pillars
    ) == (
        (1, "己酉", 1999, 2008, 8, 17),
        (2, "庚戌", 2009, 2018, 18, 27),
    )
    trace = result.reasoning.supporting_signals + result.reasoning.assumptions
    assert "start_hours=0" in trace
    assert "sect=1" in trace
    assert "count=2" in trace
    assert _chart().chart_source.timezone_assumption in result.reasoning.assumptions
    assert "naive_wall_time=true" in result.reasoning.assumptions
    assert "true_solar_time_applied=False" in result.reasoning.assumptions
    assert result.reasoning.rule_ids


@pytest.mark.parametrize("selected_year", [2009, 2018])
def test_selected_year_active_cycle_boundaries_are_inclusive(
    selected_year: int,
) -> None:
    result = calculate_luck_cycles(
        _chart(),
        birth_datetime=datetime(1992, 8, 18, 9, 30),
        selected_year=selected_year,
        count=2,
    )

    assert "active_luck_pillar=2" in result.reasoning.supporting_signals


@pytest.mark.parametrize(
    ("start_solar", "expected_signal"),
    [
        ("1998-07-01 00:00:01", "no_active_luck_pillar"),
        ("1998-07-01 00:00:00", "active_luck_pillar=1"),
        ("1998-06-30 23:59:59", "active_luck_pillar=1"),
    ],
    ids=["before_start", "on_start", "after_start"],
)
def test_july_first_reference_uses_exact_inclusive_cycle_start(
    start_solar: str,
    expected_signal: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mingli_engine.bazi.luck_cycles.calculate_provider_luck_cycles",
        lambda *args, **kwargs: ProviderLuckCycle(
            forward=True,
            start_years=6,
            start_months=0,
            start_days=0,
            start_hours=0,
            start_solar=start_solar,
            pillars=(
                (1, "己酉", 1998, 2007, 7, 16),
                (2, "庚戌", 2008, 2017, 17, 26),
            ),
        ),
    )

    result = calculate_luck_cycles(
        _chart(),
        birth_datetime=datetime(1992, 8, 18, 9, 30),
        selected_year=1998,
        count=2,
    )

    assert expected_signal in result.reasoning.supporting_signals


@pytest.mark.parametrize(
    ("selected_year", "expected_signal"),
    [
        (1998, "no_active_luck_pillar"),
        (1999, "active_luck_pillar=1"),
        (2008, "active_luck_pillar=1"),
        (2009, "active_luck_pillar=2"),
    ],
)
def test_late_year_start_uses_inclusive_start_exclusive_next_cycle(
    selected_year: int,
    expected_signal: str,
) -> None:
    chart = _chart_for("1991-06-15", "12:00", "female")
    kwargs = {
        "birth_datetime": datetime(1991, 6, 15, 12),
        "selected_year": selected_year,
        "count": 2,
    }

    first = calculate_luck_cycles(chart, **kwargs)
    second = calculate_luck_cycles(chart, **kwargs)

    assert first == second
    assert expected_signal in first.reasoning.supporting_signals


def test_selected_year_relations_include_dynamic_positions_and_exclude_natal_only() -> (
    None
):
    first = calculate_luck_cycles(
        _chart(),
        birth_datetime=datetime(1992, 8, 18, 9, 30),
        selected_year=2014,
        count=2,
    )
    second = calculate_luck_cycles(
        _chart(),
        birth_datetime=datetime(1992, 8, 18, 9, 30),
        selected_year=2014,
        count=2,
    )

    assert first == second
    assert "selected_year_reference=2014-07-01" in first.reasoning.assumptions
    assert first.selected_year_relations
    assert any(
        "day" in relation.pillar_names
        and "active_luck_2" in relation.pillar_names
        and "selected_year_2014" in relation.pillar_names
        for relation in first.selected_year_relations
    )
    assert all(
        any(
            name.startswith("active_luck_") or name.startswith("selected_year_")
            for name in relation.pillar_names
        )
        for relation in first.selected_year_relations
    )
    event_terms = ("death", "disaster", "marriage", "wealth", "illness", "career")
    rendered = repr(first).casefold()
    assert not any(term in rendered for term in event_terms)


def test_reordered_chart_pillars_produce_identical_luck_cycle_output() -> None:
    chart = _chart()
    reordered = replace(
        chart,
        pillars=[
            chart.pillars[2],
            chart.pillars[0],
            chart.pillars[3],
            chart.pillars[1],
        ],
    )
    kwargs = {
        "birth_datetime": datetime(1992, 8, 18, 9, 30),
        "selected_year": 2001,
        "count": 2,
    }

    assert calculate_luck_cycles(reordered, **kwargs) == calculate_luck_cycles(
        chart, **kwargs
    )


def test_year_outside_returned_cycles_still_compares_selected_year_to_natal() -> None:
    result = calculate_luck_cycles(
        _chart(),
        birth_datetime=datetime(1992, 8, 18, 9, 30),
        selected_year=2025,
        count=2,
    )

    assert "no_active_luck_pillar" in result.reasoning.supporting_signals
    assert result.selected_year_relations
    assert all(
        not any(name.startswith("active_luck_") for name in relation.pillar_names)
        for relation in result.selected_year_relations
    )
    assert any(
        "selected_year_2025" in relation.pillar_names
        and any(
            name in {"year", "month", "day", "hour"} for name in relation.pillar_names
        )
        for relation in result.selected_year_relations
    )


@pytest.mark.parametrize("selected_year", [True, 0, 10000, 2030.0])
def test_luck_cycles_validate_selected_year(selected_year: Any) -> None:
    with pytest.raises(
        ValueError, match="^selected_year must be an integer between 1 and 9999$"
    ):
        calculate_luck_cycles(_chart(), selected_year=selected_year)


def test_luck_cycle_calculation_does_not_persist_birth_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    calculate_luck_cycles(
        _chart(), birth_datetime=datetime(1992, 8, 18, 9, 30), count=2
    )

    assert list(tmp_path.iterdir()) == []
