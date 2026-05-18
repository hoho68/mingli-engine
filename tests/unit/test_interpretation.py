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


def unknown_only_chart() -> BaziChart:
    return make_chart(
        [
            Pillar("year", "A", "B", ["C"], "", ""),
            Pillar("month", "D", "E", ["F"], "unknown", ""),
            Pillar("day", "G", "H", ["I"], "Unknown", ""),
            Pillar("hour", "J", "K", ["L"], "UNKNOWN", ""),
        ],
        day_master=" ",
    )


def chinese_unknown_ten_god_chart() -> BaziChart:
    return make_chart(
        [
            Pillar("year", "甲", "子", ["癸"], "未知", "木水"),
            Pillar("month", "丙", "寅", ["甲", "丙", "戊"], "未说明", "火木"),
            Pillar("day", "戊", "申", ["庚", "壬", "戊"], "无", "土金"),
            Pillar("hour", "辛", "酉", ["辛"], "UNKNOWN", "金金"),
        ],
        day_master="戊",
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


def test_count_element_distribution_has_no_dominant_elements_without_countable_signals():
    distribution = count_element_distribution(
        make_chart(
            [
                Pillar("year", "A", "B", ["C"], "unknown", ""),
                Pillar("month", "D", "E", ["F"], "unknown", ""),
                Pillar("day", "G", "H", ["I"], "unknown", ""),
                Pillar("hour", "J", "K", ["L"], "unknown", ""),
            ]
        )
    )

    assert distribution.total_counts == {
        "木": 0,
        "火": 0,
        "土": 0,
        "金": 0,
        "水": 0,
    }
    assert distribution.dominant_elements == []
    assert distribution.missing_elements == ["木", "火", "土", "金", "水"]


def test_count_element_distribution_strips_signals_and_ignores_blanks():
    distribution = count_element_distribution(
        make_chart(
            [
                Pillar("year", " 甲 ", " 子 ", ["", " ", " 癸 "], "unknown", ""),
                Pillar("month", " 未知 ", "", ["  未知藏干  "], "unknown", ""),
            ]
        )
    )

    assert distribution.direct_counts["木"] == 1
    assert distribution.direct_counts["水"] == 1
    assert distribution.hidden_counts["水"] == 1
    assert distribution.unknown_signals == ["未知", "未知藏干"]


def test_build_basic_interpretation_explains_day_master_and_ten_gods():
    summary = build_basic_interpretation(balanced_chart())

    assert "五行数量可以先作为结构观察材料来看" in summary.five_elements_summary
    assert "明面信号：" in summary.five_elements_summary
    assert "藏干信号：" in summary.five_elements_summary
    assert "合计信号：" in summary.five_elements_summary
    assert "不等同于完整旺衰模型" in summary.five_elements_summary
    assert "日主戊" in summary.day_master_summary
    assert "观察中心" in summary.day_master_summary
    assert "十神关系可以先按四个柱位理解为结构线索" in summary.ten_gods_summary
    assert "年柱：七杀" in summary.ten_gods_summary
    assert "月柱：食神" in summary.ten_gods_summary
    assert "日柱：日主" in summary.ten_gods_summary
    assert "时柱：伤官" in summary.ten_gods_summary
    assert "基础结构可以先看分布是否集中、哪些信号可见、哪些信号暂时不明显" in (
        summary.structure_observations
    )
    assert "不做格局定论" in summary.limitations
    assert "不做用神定论" in summary.limitations
    assert "不做大运流年判断" in summary.limitations


def test_build_basic_interpretation_avoids_system_like_structure_phrases():
    summary = build_basic_interpretation(balanced_chart())
    joined = "\n".join(
        [
            summary.five_elements_summary,
            summary.ten_gods_summary,
            summary.structure_observations,
        ]
    )

    for old_phrase in (
        "五行信号观察：明面信号为",
        "这些数量用于观察结构分布",
        "基础结构观察：五行分布先看有无、多少与集中度。",
    ):
        assert old_phrase not in joined


def test_build_basic_interpretation_uses_neutral_language_for_missing_signals():
    summary = build_basic_interpretation(concentrated_chart())
    joined = "\n".join(
        [
            summary.five_elements_summary,
            summary.structure_observations,
            summary.focus_suggestions,
        ]
    )

    assert "金、水暂未形成可计数信号" in joined
    assert "不等于现实能力缺失" in joined
    for prohibited_phrase in ("必定", "注定", "一定会", "死定"):
        assert prohibited_phrase not in joined


def test_build_basic_interpretation_records_missing_ten_gods_when_all_unknown():
    summary = build_basic_interpretation(unknown_only_chart())

    assert "当前没有可读的十神信号" in summary.ten_gods_summary
    assert "未识别十神位置：年柱、月柱、日柱、时柱，本层不作补猜。" in (
        summary.ten_gods_summary
    )


def test_build_basic_interpretation_treats_chinese_unknown_ten_gods_as_missing():
    summary = build_basic_interpretation(chinese_unknown_ten_god_chart())

    assert "当前没有可读的十神信号" in summary.ten_gods_summary
    assert "未识别十神位置：年柱、月柱、日柱、时柱，本层不作补猜。" in (
        summary.ten_gods_summary
    )
    assert "年柱：未知" not in summary.ten_gods_summary
    assert "月柱：未说明" not in summary.ten_gods_summary
    assert "日柱：无" not in summary.ten_gods_summary


def test_build_basic_interpretation_uses_limitation_suggestions_without_counts():
    summary = build_basic_interpretation(unknown_only_chart())

    assert "暂无可计数五行信号" in summary.focus_suggestions
    assert "较集中的信号" not in summary.focus_suggestions
    assert "日主未标明" in summary.day_master_summary
    assert "观察中心" in summary.day_master_summary


def test_build_basic_interpretation_reports_unknown_signals_in_limitations():
    summary = build_basic_interpretation(unknown_only_chart())

    assert "另有未识别信号：A、B、C、D、E、F、G、H、I、J、K、L" in (
        summary.five_elements_summary
    )
    assert "存在未识别信号" in summary.limitations
