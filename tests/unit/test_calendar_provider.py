from datetime import datetime

from mingli_engine.calendar_provider import calculate_provider_pillars


def test_calculate_provider_pillars_returns_bazi_provider_data():
    pillars = calculate_provider_pillars(datetime(1992, 8, 18, 9, 30))

    assert [pillar.gan_zhi for pillar in pillars] == ["壬申", "戊申", "丙寅", "癸巳"]
    assert [pillar.name for pillar in pillars] == ["year", "month", "day", "hour"]
    assert pillars[0].hidden_stems == ["庚", "壬", "戊"]
    assert pillars[2].ten_god == "日主"
    assert pillars[3].element == "水火"
