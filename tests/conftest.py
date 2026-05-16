import pytest

from mingli_engine.models import BaziChart, BirthProfile, ChartSource, Pillar


@pytest.fixture
def sample_bazi_chart() -> BaziChart:
    birth_profile = BirthProfile(
        calendar_type="solar",
        birth_date="1990-01-01",
        birth_time="08:30",
        birthplace="北京",
        gender="female",
        focus_topic="事业发展",
    )
    chart_source = ChartSource(
        source_type="externally_verified",
        source_note="样例盘由外部排盘工具核对，仅用于测试报告结构。",
        calendar_assumption="公历日期输入，未做农历换算。",
        timezone_assumption="使用出生地北京时间 UTC+8。",
        solar_terms_assumption="节气边界按外部排盘工具结果采用。",
        true_solar_time_applied=False,
        confidence="sample-high",
    )
    pillars = [
        Pillar(
            name="年柱",
            heavenly_stem="己",
            earthly_branch="巳",
            hidden_stems=["丙", "戊", "庚"],
            ten_god="正官",
            element="土火",
        ),
        Pillar(
            name="月柱",
            heavenly_stem="丙",
            earthly_branch="子",
            hidden_stems=["癸"],
            ten_god="偏印",
            element="火水",
        ),
        Pillar(
            name="日柱",
            heavenly_stem="壬",
            earthly_branch="申",
            hidden_stems=["庚", "壬", "戊"],
            ten_god="日主",
            element="水金",
        ),
        Pillar(
            name="时柱",
            heavenly_stem="甲",
            earthly_branch="辰",
            hidden_stems=["戊", "乙", "癸"],
            ten_god="食神",
            element="木土",
        ),
    ]

    return BaziChart(
        birth_profile=birth_profile,
        chart_source=chart_source,
        pillars=pillars,
        day_master="壬水",
        five_elements_summary={
            "木": "有",
            "火": "有",
            "土": "偏多",
            "金": "有",
            "水": "偏旺",
        },
        ten_gods_summary="官印食神皆有呈现，需结合日主强弱候选判断。",
        strength_assessment="日主壬水有根，整体偏旺的候选判断。",
        pattern_candidates=["官印相生候选", "食神生财线索"],
        useful_god_candidates=["火", "土"],
        luck_cycle_summary="阶段变化宜以趋势观察，不作确定性预测。",
    )
