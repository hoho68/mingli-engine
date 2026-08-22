from mingli_engine.liuyao.constants import (
    BRANCH_ELEMENTS,
    DAY_STEM_SPIRIT_START,
    EIGHT_PALACES,
    LIUYAO_RULE_FAMILIES,
    NAJIA_GANZHI,
    PALACE_SEQUENCE_NAMES,
    SHENG_CYCLE,
    SHI_POSITION_BY_SEQUENCE,
    SIX_RELATIONS,
    SIX_SPIRITS,
    TRIGRAM_ELEMENTS,
    TRIGRAM_LINES,
    XIANTIAN_INDEX,
    palace_gua_lines,
    six_relation,
)


def test_trigram_tables_are_complete_and_consistent() -> None:
    assert len(TRIGRAM_LINES) == 8
    assert set(TRIGRAM_LINES) == set(TRIGRAM_ELEMENTS) == set(XIANTIAN_INDEX)
    assert set(TRIGRAM_LINES) == set(EIGHT_PALACES)
    assert sorted(XIANTIAN_INDEX.values()) == [1, 2, 3, 4, 5, 6, 7, 8]
    assert all(len(lines) == 3 and set(lines) <= {0, 1} for lines in TRIGRAM_LINES.values())
    assert TRIGRAM_LINES["乾"] == (1, 1, 1)
    assert TRIGRAM_ELEMENTS["震"] == TRIGRAM_ELEMENTS["巽"] == "木"


def test_palace_sequences_cover_all_64_gua_with_known_members() -> None:
    assert set(PALACE_SEQUENCE_NAMES) == set(EIGHT_PALACES)
    all_names = [name for names in PALACE_SEQUENCE_NAMES.values() for name in names]
    assert len(all_names) == 64
    assert len(set(all_names)) == 64
    assert PALACE_SEQUENCE_NAMES["乾"] == (
        "乾为天", "天风姤", "天山遁", "天地否", "风地观", "山地剥", "火地晋", "火天大有",
    )
    assert PALACE_SEQUENCE_NAMES["坤"][-1] == "水地比"
    assert PALACE_SEQUENCE_NAMES["离"][7] == "天火同人"


def test_palace_gua_lines_match_classical_examples() -> None:
    # 乾为天 pure yang.
    assert palace_gua_lines("乾", 0) == (1, 1, 1, 1, 1, 1)
    # 天风姤: upper 乾 lower 巽.
    assert palace_gua_lines("乾", 1) == (0, 1, 1, 1, 1, 1)
    # 天地否: upper 乾 lower 坤.
    assert palace_gua_lines("乾", 3) == (0, 0, 0, 1, 1, 1)
    # 山地剥: upper 艮 lower 坤.
    assert palace_gua_lines("乾", 5) == (0, 0, 0, 0, 0, 1)
    # 火地晋 (游魂): upper 离 lower 坤.
    assert palace_gua_lines("乾", 6) == (0, 0, 0, 1, 0, 1)
    # 火天大有 (归魂): upper 离 lower 乾.
    assert palace_gua_lines("乾", 7) == (1, 1, 1, 1, 0, 1)
    # 水地比 (坤宫归魂): upper 坎 lower 坤.
    assert palace_gua_lines("坤", 7) == (0, 0, 0, 0, 1, 0)
    # 雷泽归妹 (兑宫归魂): upper 震 lower 兑.
    assert palace_gua_lines("兑", 7) == (1, 1, 0, 1, 0, 0)


def test_shi_ying_positions_follow_jingfang_sequence() -> None:
    assert SHI_POSITION_BY_SEQUENCE == {
        0: 6, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 4, 7: 3,
    }
    for sequence, shi in SHI_POSITION_BY_SEQUENCE.items():
        ying = shi + 3 if shi <= 3 else shi - 3
        assert 1 <= shi <= 6
        assert 1 <= ying <= 6


def test_najia_tables_are_complete() -> None:
    assert set(NAJIA_GANZHI) == set(EIGHT_PALACES)
    for entry in NAJIA_GANZHI.values():
        assert len(entry["inner"]) == 3
        assert len(entry["outer"]) == 3
    assert NAJIA_GANZHI["乾"]["inner"][0] == "甲子"
    assert NAJIA_GANZHI["坤"]["outer"][-1] == "癸酉"


def test_six_relation_cycles() -> None:
    assert six_relation("金", "申") == "兄弟"  # 金同金
    assert six_relation("金", "辰") == "父母"  # 土生金
    assert six_relation("金", "子") == "子孙"  # 金生水
    assert six_relation("金", "午") == "官鬼"  # 火克金
    assert six_relation("金", "寅") == "妻财"  # 金克木
    assert set(SIX_RELATIONS) == {"父母", "兄弟", "官鬼", "妻财", "子孙"}
    assert set(SHENG_CYCLE) == set(BRANCH_ELEMENTS.values()) == {"金", "木", "水", "火", "土"}


def test_six_spirits_and_day_stem_start() -> None:
    assert SIX_SPIRITS == ("青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武")
    assert DAY_STEM_SPIRIT_START["甲"] == "青龙"
    assert DAY_STEM_SPIRIT_START["壬"] == "玄武"
    assert set(DAY_STEM_SPIRIT_START) == {
        "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸",
    }


def test_liuyao_rule_families_are_eight_and_isolated() -> None:
    assert len(LIUYAO_RULE_FAMILIES) == 8
    assert len(set(LIUYAO_RULE_FAMILIES)) == 8
    from mingli_engine.models import RULE_FAMILIES

    assert not set(LIUYAO_RULE_FAMILIES) & set(RULE_FAMILIES)


def test_gua_reference_matches_programmatic_derivation() -> None:
    from mingli_engine.liuyao.constants import (
        EIGHT_PALACES,
        PALACE_SEQUENCE_NAMES,
        palace_gua_lines,
        load_gua_reference,
    )

    records = load_gua_reference()
    assert len(records) == 64
    expected_names = {
        name for names in PALACE_SEQUENCE_NAMES.values() for name in names
    }
    assert {str(item["gua_name"]) for item in records} == expected_names
    for item in records:
        palace = str(item["palace"])
        sequence = int(str(item["palace_sequence"]))
        assert palace in EIGHT_PALACES
        assert item["gua_name"] == PALACE_SEQUENCE_NAMES[palace][sequence]
        assert list(item["lines"]) == list(palace_gua_lines(palace, sequence))
        assert int(str(item["shi_position"])) > 0
        assert int(str(item["ying_position"])) > 0
