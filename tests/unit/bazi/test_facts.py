from dataclasses import replace

import pytest

from mingli_engine.bazi.facts import build_chart_facts, ten_god
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile, Pillar


def raw_verified_chart():
    return calculate_bazi_chart(
        BirthProfile(
            calendar_type="gregorian",
            birth_date="1992-08-18",
            birth_time="09:30",
            birthplace="上海市",
            gender="未指定",
            focus_topic="整体结构观察",
        )
    )


@pytest.mark.parametrize(
    ("target_stem", "expected"),
    [
        ("丙", "比肩"),
        ("丁", "劫财"),
        ("甲", "偏印"),
        ("乙", "正印"),
        ("戊", "食神"),
        ("己", "伤官"),
        ("庚", "偏财"),
        ("辛", "正财"),
        ("壬", "七杀"),
        ("癸", "正官"),
    ],
)
def test_ten_god_covers_every_relationship_and_polarity(
    target_stem: str, expected: str
) -> None:
    assert ten_god("丙", target_stem) == expected


@pytest.mark.parametrize(
    ("day_master", "target_stem"),
    [("invalid", "甲"), ("甲", "invalid")],
)
def test_ten_god_rejects_invalid_stems(
    day_master: str, target_stem: str
) -> None:
    with pytest.raises(ValueError, match="Invalid stem"):
        ten_god(day_master, target_stem)


def test_build_chart_facts_reconstructs_verified_chart() -> None:
    chart = raw_verified_chart()

    assert chart.pillars[3].hidden_stems == ["丙", "庚", "戊"]

    facts = build_chart_facts(chart)

    assert facts.day_master == "丙"
    assert facts.month_branch == "申"
    assert [fact.pillar_name for fact in facts.exposed_stems] == [
        "year",
        "month",
        "day",
        "hour",
    ]
    assert [fact.ten_god for fact in facts.exposed_stems] == [
        "七杀",
        "食神",
        "比肩",
        "正官",
    ]

    for pillar_name in ("year", "month"):
        hidden = [
            fact for fact in facts.hidden_stems if fact.pillar_name == pillar_name
        ]
        assert [fact.stem for fact in hidden] == ["庚", "壬", "戊"]
        assert [fact.role for fact in hidden] == ["main", "middle", "residual"]
        assert [fact.ten_god for fact in hidden] == ["偏财", "七杀", "食神"]
        assert [fact.element for fact in hidden] == ["金", "水", "土"]
        assert [fact.polarity for fact in hidden] == ["yang", "yang", "yang"]

    hour_hidden = [
        fact for fact in facts.hidden_stems if fact.pillar_name == "hour"
    ]
    assert [fact.stem for fact in hour_hidden] == ["丙", "戊", "庚"]
    assert [fact.role for fact in hour_hidden] == [
        "main",
        "middle",
        "residual",
    ]

    day_master_roots = [root for root in facts.roots if root.stem == "丙"]
    assert [
        (
            root.stem_pillar,
            root.branch,
            root.branch_pillar,
            root.role,
            root.exact_stem_root,
        )
        for root in day_master_roots
    ] == [
        ("day", "寅", "day", "middle", True),
        ("day", "巳", "hour", "main", True),
    ]

    assert facts.twelve_growth_by_pillar == (
        ("year", "病"),
        ("month", "病"),
        ("day", "长生"),
        ("hour", "临官"),
    )
    assert facts.assumptions == (
        chart.chart_source.calendar_assumption,
        chart.chart_source.timezone_assumption,
        chart.chart_source.solar_terms_assumption,
        "true_solar_time_applied=False",
        "No longitude or true-solar-time conversion was inferred from birthplace.",
    )
    assert all("上海" not in assumption for assumption in facts.assumptions)
    assert all("longitude=" not in assumption for assumption in facts.assumptions)


@pytest.mark.parametrize(
    "provider_hidden_stems",
    [
        ["庚", "壬"],
        ["庚", "壬", "戊", "甲"],
        ["庚", "壬", "壬"],
        ["庚", "壬", "己"],
    ],
    ids=["missing", "extra", "duplicate", "different"],
)
def test_build_chart_facts_rejects_provider_hidden_stem_mismatch(
    provider_hidden_stems: list[str],
) -> None:
    chart = raw_verified_chart()
    mismatched_year = replace(
        chart.pillars[0], hidden_stems=provider_hidden_stems
    )

    with pytest.raises(
        ValueError,
        match="^provider hidden stems do not match canonical table$",
    ):
        build_chart_facts(
            replace(chart, pillars=[mismatched_year, *chart.pillars[1:]])
        )


def test_build_chart_facts_requires_exactly_four_pillars() -> None:
    chart = raw_verified_chart()

    with pytest.raises(ValueError, match="exactly four pillars"):
        build_chart_facts(replace(chart, pillars=chart.pillars[:3]))


@pytest.mark.parametrize(
    ("source_name", "replacement_name"),
    [
        ("hour", "year"),
        ("year", "hour"),
        ("year", "unknown"),
    ],
    ids=["duplicate-year", "duplicate-hour", "unknown-role"],
)
def test_build_chart_facts_requires_every_pillar_role_once(
    source_name: str, replacement_name: str
) -> None:
    chart = raw_verified_chart()
    pillars = [
        replace(pillar, name=replacement_name)
        if pillar.name == source_name
        else pillar
        for pillar in chart.pillars
    ]

    with pytest.raises(
        ValueError,
        match="^expected exactly one year, month, day, and hour pillar$",
    ):
        build_chart_facts(replace(chart, pillars=pillars))


def test_build_chart_facts_preserves_given_pillar_order() -> None:
    chart = raw_verified_chart()
    reordered_pillars = [
        chart.pillars[2],
        chart.pillars[0],
        chart.pillars[3],
        chart.pillars[1],
    ]

    facts = build_chart_facts(replace(chart, pillars=reordered_pillars))

    assert [fact.pillar_name for fact in facts.exposed_stems] == [
        "day",
        "year",
        "hour",
        "month",
    ]
    assert facts.twelve_growth_by_pillar == (
        ("day", "长生"),
        ("year", "病"),
        ("hour", "临官"),
        ("month", "病"),
    )


def test_build_chart_facts_rejects_day_master_mismatch() -> None:
    chart = raw_verified_chart()

    with pytest.raises(ValueError, match="day master does not match day pillar"):
        build_chart_facts(replace(chart, day_master="丁"))


def test_build_chart_facts_preserves_repeated_exposed_stem_occurrences() -> None:
    chart = raw_verified_chart()
    repeated_stem_pillars = [
        replace(chart.pillars[0], heavenly_stem="丙"),
        *chart.pillars[1:],
    ]

    facts = build_chart_facts(replace(chart, pillars=repeated_stem_pillars))

    roots = [root for root in facts.roots if root.stem == "丙"]
    assert len(roots) == 4
    assert [root.stem_pillar for root in roots] == ["year", "year", "day", "day"]


def test_build_chart_facts_validates_exposed_stems() -> None:
    chart = raw_verified_chart()
    invalid_pillar = Pillar(
        name="year",
        heavenly_stem="invalid",
        earthly_branch="申",
        hidden_stems=["庚", "壬", "戊"],
        ten_god="",
        element="",
    )

    with pytest.raises(ValueError, match="Invalid stem"):
        build_chart_facts(replace(chart, pillars=[invalid_pillar, *chart.pillars[1:]]))
