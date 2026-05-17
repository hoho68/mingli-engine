from mingli_engine.interpretation import (
    build_basic_interpretation,
    count_element_distribution,
)
from mingli_engine.models import BaziChart, BirthProfile, ChartSource, Pillar


def make_chart(pillars: list[Pillar], day_master: str = "戊") -> BaziChart:
    return BaziChart(
        birth_profile=BirthProfile(
            calendar_type="solar",
            birth_date="1992-08-18",
            birth_time="14:30",
            birthplace="上海",
            gender="unspecified",
            focus_topic="事业发展",
        ),
        chart_source=ChartSource(
            source_type="test",
            source_note="固定测试盘",
            calendar_assumption="固定测试",
            timezone_assumption="UTC+08:00",
            solar_terms_assumption="固定测试",
            true_solar_time_applied=False,
            confidence="test",
        ),
        pillars=pillars,
        day_master=day_master,
        five_elements_summary={},
        ten_gods_summary="",
        strength_assessment="",
        pattern_candidates=[],
        useful_god_candidates=[],
        luck_cycle_summary="",
    )


def balanced_chart() -> BaziChart:
    return make_chart(
        [
            Pillar("year", "甲", "子", ["癸"], "七杀", "木水"),
            Pillar("month", "丙", "寅", ["甲", "丙", "戊"], "食神", "火木"),
            Pillar("day", "戊", "申", ["庚", "壬", "戊"], "日主", "土金"),
            Pillar("hour", "辛", "酉", ["辛"], "伤官", "金金"),
        ],
        day_master="戊",
    )


def concentrated_chart() -> BaziChart:
    return make_chart(
        [
            Pillar("year", "甲", "寅", ["甲", "丙", "戊"], "比肩", "木木"),
            Pillar("month", "乙", "卯", ["乙"], "劫财", "木木"),
            Pillar("day", "甲", "寅", ["甲", "丙", "戊"], "日主", "木木"),
            Pillar("hour", "乙", "卯", ["乙"], "劫财", "木木"),
        ],
        day_master="甲",
    )


def test_count_element_distribution_distinguishes_direct_and_hidden_signals():
    distribution = count_element_distribution(balanced_chart())

    assert distribution.direct_counts == {
        "木": 2,
        "火": 1,
        "土": 1,
        "金": 3,
        "水": 1,
    }
    assert distribution.hidden_counts == {
        "木": 1,
        "火": 1,
        "土": 2,
        "金": 2,
        "水": 2,
    }
    assert distribution.total_counts == {
        "木": 3,
        "火": 2,
        "土": 3,
        "金": 5,
        "水": 3,
    }
    assert distribution.dominant_elements == ["金"]
    assert distribution.missing_elements == []
    assert distribution.unknown_signals == []


def test_count_element_distribution_records_missing_and_concentrated_signals():
    distribution = count_element_distribution(concentrated_chart())

    assert distribution.dominant_elements == ["木"]
    assert distribution.missing_elements == ["金", "水"]
    assert distribution.total_counts["木"] == 12
    assert distribution.total_counts["金"] == 0
    assert distribution.total_counts["水"] == 0
