STEMS = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
BRANCHES = ("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥")
ELEMENTS = ("木", "火", "土", "金", "水")

GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

STEM_ELEMENT = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}
STEM_POLARITY = {
    "甲": "yang",
    "乙": "yin",
    "丙": "yang",
    "丁": "yin",
    "戊": "yang",
    "己": "yin",
    "庚": "yang",
    "辛": "yin",
    "壬": "yang",
    "癸": "yin",
}
BRANCH_ELEMENT = {
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
HIDDEN_STEMS = {
    "子": (("癸", "main"),),
    "丑": (("己", "main"), ("癸", "middle"), ("辛", "residual")),
    "寅": (("甲", "main"), ("丙", "middle"), ("戊", "residual")),
    "卯": (("乙", "main"),),
    "辰": (("戊", "main"), ("乙", "middle"), ("癸", "residual")),
    "巳": (("丙", "main"), ("戊", "middle"), ("庚", "residual")),
    "午": (("丁", "main"), ("己", "middle")),
    "未": (("己", "main"), ("丁", "middle"), ("乙", "residual")),
    "申": (("庚", "main"), ("壬", "middle"), ("戊", "residual")),
    "酉": (("辛", "main"),),
    "戌": (("戊", "main"), ("辛", "middle"), ("丁", "residual")),
    "亥": (("壬", "main"), ("甲", "middle")),
}

GROWTH_PHASES = (
    "长生",
    "沐浴",
    "冠带",
    "临官",
    "帝旺",
    "衰",
    "病",
    "死",
    "墓",
    "绝",
    "胎",
    "养",
)
GROWTH_START = {
    "甲": "亥",
    "乙": "午",
    "丙": "寅",
    "丁": "酉",
    "戊": "寅",
    "己": "酉",
    "庚": "巳",
    "辛": "子",
    "壬": "申",
    "癸": "卯",
}


def growth_phase(stem: str, branch: str) -> str:
    if stem not in STEMS:
        raise ValueError(f"Invalid stem: {stem!r}")
    if branch not in BRANCHES:
        raise ValueError(f"Invalid branch: {branch!r}")

    start_index = BRANCHES.index(GROWTH_START[stem])
    branch_index = BRANCHES.index(branch)
    if STEM_POLARITY[stem] == "yang":
        phase_index = (branch_index - start_index) % len(BRANCHES)
    else:
        phase_index = (start_index - branch_index) % len(BRANCHES)
    return GROWTH_PHASES[phase_index]
