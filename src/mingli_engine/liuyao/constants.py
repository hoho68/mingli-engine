"""Frozen najia (六爻纳甲) primitives and derivation rules.

All tables follow the standard classical conventions documented in
specs/020-liuyao-najia-engine/research.md (R1-R4). Lines are always stored
bottom-up (position 1 = 初爻).
"""

from __future__ import annotations

# Eight trigrams: name -> (lines bottom-up, element, xiantian index)
TRIGRAM_LINES: dict[str, tuple[int, int, int]] = {
    "乾": (1, 1, 1),
    "兑": (1, 1, 0),
    "离": (1, 0, 1),
    "震": (1, 0, 0),
    "巽": (0, 1, 1),
    "坎": (0, 1, 0),
    "艮": (0, 0, 1),
    "坤": (0, 0, 0),
}
TRIGRAM_ELEMENTS: dict[str, str] = {
    "乾": "金",
    "兑": "金",
    "离": "火",
    "震": "木",
    "巽": "木",
    "坎": "水",
    "艮": "土",
    "坤": "土",
}
XIANTIAN_INDEX: dict[str, int] = {
    "乾": 1,
    "兑": 2,
    "离": 3,
    "震": 4,
    "巽": 5,
    "坎": 6,
    "艮": 7,
    "坤": 8,
}
XIANTIAN_TRIGRAMS: tuple[str, ...] = tuple(
    sorted(XIANTIAN_INDEX, key=lambda name: XIANTIAN_INDEX[name])
)

# Eight palaces in canonical order; palace element equals its trigram element.
EIGHT_PALACES: tuple[str, ...] = ("乾", "坎", "艮", "震", "巽", "离", "坤", "兑")

# 京房八宫卦序: palace -> eight gua names in sequence (本宫,一世,二世,三世,四世,五世,游魂,归魂).
PALACE_SEQUENCE_NAMES: dict[str, tuple[str, ...]] = {
    "乾": ("乾为天", "天风姤", "天山遁", "天地否", "风地观", "山地剥", "火地晋", "火天大有"),
    "坎": ("坎为水", "水泽节", "水雷屯", "水火既济", "泽火革", "雷火丰", "地火明夷", "地水师"),
    "艮": ("艮为山", "山火贲", "山天大畜", "山泽损", "火泽睽", "天泽履", "风泽中孚", "风山渐"),
    "震": ("震为雷", "雷地豫", "雷水解", "雷风恒", "地风升", "水风井", "泽风大过", "泽雷随"),
    "巽": ("巽为风", "风天小畜", "风火家人", "风雷益", "天雷无妄", "火雷噬嗑", "山雷颐", "山风蛊"),
    "离": ("离为火", "火山旅", "火风鼎", "火水未济", "山水蒙", "风水涣", "天水讼", "天火同人"),
    "坤": ("坤为地", "地雷复", "地泽临", "地天泰", "雷天大壮", "泽天夬", "水天需", "水地比"),
    "兑": ("兑为泽", "泽水困", "泽地萃", "泽山咸", "水山蹇", "地山谦", "雷山小过", "雷泽归妹"),
}

# 世爻 position per palace sequence index; 应爻 is three positions away.
SHI_POSITION_BY_SEQUENCE: dict[int, int] = {
    0: 6,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 4,
    7: 3,
}

# Najia stem-branch assignment per trigram, inner (lines 1-3) and outer
# (lines 4-6), bottom-up.
NAJIA_GANZHI: dict[str, dict[str, tuple[str, str, str]]] = {
    "乾": {"inner": ("甲子", "甲寅", "甲辰"), "outer": ("壬午", "壬申", "壬戌")},
    "坎": {"inner": ("戊寅", "戊辰", "戊午"), "outer": ("戊申", "戊戌", "戊子")},
    "艮": {"inner": ("丙辰", "丙午", "丙申"), "outer": ("丙戌", "丙子", "丙寅")},
    "震": {"inner": ("庚子", "庚寅", "庚辰"), "outer": ("庚午", "庚申", "庚戌")},
    "巽": {"inner": ("辛丑", "辛亥", "辛酉"), "outer": ("辛未", "辛巳", "辛卯")},
    "离": {"inner": ("己卯", "己丑", "己亥"), "outer": ("己酉", "己未", "己巳")},
    "坤": {"inner": ("乙未", "乙巳", "乙卯"), "outer": ("癸丑", "癸亥", "癸酉")},
    "兑": {"inner": ("丁巳", "丁卯", "丁丑"), "outer": ("丁亥", "丁酉", "丁未")},
}

BRANCH_ELEMENTS: dict[str, str] = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}

SHENG_CYCLE: dict[str, str] = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE_CYCLE: dict[str, str] = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

SIX_RELATIONS: tuple[str, ...] = ("父母", "兄弟", "官鬼", "妻财", "子孙")

SIX_SPIRITS: tuple[str, ...] = ("青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武")
DAY_STEM_SPIRIT_START: dict[str, str] = {
    "甲": "青龙",
    "乙": "青龙",
    "丙": "朱雀",
    "丁": "朱雀",
    "戊": "勾陈",
    "己": "螣蛇",
    "庚": "白虎",
    "辛": "白虎",
    "壬": "玄武",
    "癸": "玄武",
}

HEAVENLY_STEMS: tuple[str, ...] = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
EARTHLY_BRANCHES: tuple[str, ...] = (
    "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥",
)

# Independent liuyao rule-family namespace (spec FR-4; fixed order).
LIUYAO_RULE_FAMILIES: tuple[str, ...] = (
    "yong_shen_selection",
    "shi_ying_relation",
    "moving_line_dynamics",
    "six_spirits_attachment",
    "month_day_strength",
    "void_break_state",
    "yingqi_timing",
    "category_judgment",
)

# Palace-sequence flip sets (lines differing from the palace head gua).
_SEQUENCE_FLIPS: dict[int, tuple[int, ...]] = {
    0: (),
    1: (1,),
    2: (1, 2),
    3: (1, 2, 3),
    4: (1, 2, 3, 4),
    5: (1, 2, 3, 4, 5),
    6: (1, 2, 3, 5),
    7: (5,),
}


def palace_gua_lines(palace: str, sequence: int) -> tuple[int, ...]:
    """Return the six bottom-up line values of a palace-sequence gua."""
    if palace not in TRIGRAM_LINES:
        raise ValueError(f"unknown palace: {palace}")
    flips = _SEQUENCE_FLIPS.get(sequence)
    if flips is None:
        raise ValueError(f"unknown palace sequence: {sequence}")
    head = TRIGRAM_LINES[palace]
    lines = list(head) + list(head)
    for position in flips:
        lines[position - 1] = 1 - lines[position - 1]
    return tuple(lines)


def six_relation(palace_element: str, branch: str) -> str:
    """Six-relation of a line branch relative to the palace element."""
    line_element = BRANCH_ELEMENTS[branch]
    if line_element == palace_element:
        return "兄弟"
    if SHENG_CYCLE[line_element] == palace_element:
        return "父母"
    if SHENG_CYCLE[palace_element] == line_element:
        return "子孙"
    if KE_CYCLE[line_element] == palace_element:
        return "官鬼"
    if KE_CYCLE[palace_element] == line_element:
        return "妻财"
    raise ValueError(f"unreachable relation: {palace_element} vs {branch}")


def load_gua_reference() -> tuple[dict[str, object], ...]:
    """Load the frozen 64-gua structural reference from package data."""
    import json
    from importlib import resources

    path = resources.files("mingli_engine").joinpath(
        "data/liuyao/gua_reference.json"
    )
    raw = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(raw, dict)
        or raw.get("schema_version") != "liuyao-gua-reference-v1"
        or not isinstance(raw.get("records"), list)
        or len(raw["records"]) != 64
    ):
        raise ValueError("the liuyao gua reference is invalid")
    records: list[dict[str, object]] = []
    for item in raw["records"]:
        if not isinstance(item, dict) or set(item) != {
            "gua_name",
            "lines",
            "lower_trigram",
            "upper_trigram",
            "palace",
            "palace_sequence",
            "shi_position",
            "ying_position",
        }:
            raise ValueError("a liuyao gua reference record is invalid")
        records.append(item)
    names = [str(item["gua_name"]) for item in records]
    if len(set(names)) != 64:
        raise ValueError("liuyao gua reference names must be unique")
    return tuple(records)
