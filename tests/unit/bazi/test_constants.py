import pytest

from mingli_engine.bazi import constants


def test_canonical_sequences_and_element_cycles() -> None:
    assert constants.STEMS == ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
    assert constants.BRANCHES == ("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥")
    assert constants.ELEMENTS == ("木", "火", "土", "金", "水")
    assert constants.GENERATES == {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    assert constants.CONTROLS == {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    assert constants.GROWTH_PHASES == (
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


@pytest.mark.parametrize(
    ("stem", "element", "polarity", "growth_start"),
    [
        ("甲", "木", "阳", "亥"),
        ("乙", "木", "阴", "午"),
        ("丙", "火", "阳", "寅"),
        ("丁", "火", "阴", "酉"),
        ("戊", "土", "阳", "寅"),
        ("己", "土", "阴", "酉"),
        ("庚", "金", "阳", "巳"),
        ("辛", "金", "阴", "子"),
        ("壬", "水", "阳", "申"),
        ("癸", "水", "阴", "卯"),
    ],
)
def test_stem_facts(stem: str, element: str, polarity: str, growth_start: str) -> None:
    assert constants.STEM_ELEMENT[stem] == element
    assert constants.STEM_POLARITY[stem] == polarity
    assert constants.GROWTH_START[stem] == growth_start
    assert constants.growth_phase(stem, growth_start) == "长生"


@pytest.mark.parametrize(
    ("branch", "element", "hidden_stems"),
    [
        ("子", "水", (("癸", "main"),)),
        ("丑", "土", (("己", "main"), ("癸", "middle"), ("辛", "residual"))),
        ("寅", "木", (("甲", "main"), ("丙", "middle"), ("戊", "residual"))),
        ("卯", "木", (("乙", "main"),)),
        ("辰", "土", (("戊", "main"), ("乙", "middle"), ("癸", "residual"))),
        ("巳", "火", (("丙", "main"), ("戊", "middle"), ("庚", "residual"))),
        ("午", "火", (("丁", "main"), ("己", "middle"))),
        ("未", "土", (("己", "main"), ("丁", "middle"), ("乙", "residual"))),
        ("申", "金", (("庚", "main"), ("壬", "middle"), ("戊", "residual"))),
        ("酉", "金", (("辛", "main"),)),
        ("戌", "土", (("戊", "main"), ("辛", "middle"), ("丁", "residual"))),
        ("亥", "水", (("壬", "main"), ("甲", "middle"))),
    ],
)
def test_branch_facts(
    branch: str,
    element: str,
    hidden_stems: tuple[tuple[str, str], ...],
) -> None:
    assert constants.BRANCH_ELEMENT[branch] == element
    assert constants.HIDDEN_STEMS[branch] == hidden_stems


@pytest.mark.parametrize(
    ("branch", "phase"),
    [
        ("亥", "长生"),
        ("子", "沐浴"),
        ("丑", "冠带"),
        ("寅", "临官"),
        ("卯", "帝旺"),
        ("辰", "衰"),
        ("巳", "病"),
        ("午", "死"),
        ("未", "墓"),
        ("申", "绝"),
        ("酉", "胎"),
        ("戌", "养"),
    ],
)
def test_yang_growth_phases_walk_forward(branch: str, phase: str) -> None:
    assert constants.growth_phase("甲", branch) == phase


@pytest.mark.parametrize(
    ("branch", "phase"),
    [
        ("午", "长生"),
        ("巳", "沐浴"),
        ("辰", "冠带"),
        ("卯", "临官"),
        ("寅", "帝旺"),
        ("丑", "衰"),
        ("子", "病"),
        ("亥", "死"),
        ("戌", "墓"),
        ("酉", "绝"),
        ("申", "胎"),
        ("未", "养"),
    ],
)
def test_yin_growth_phases_walk_backward(branch: str, phase: str) -> None:
    assert constants.growth_phase("乙", branch) == phase


@pytest.mark.parametrize("stem", ["", "A", "甲木"])
def test_growth_phase_rejects_invalid_stem(stem: str) -> None:
    with pytest.raises(ValueError, match=f"Invalid stem: {stem!r}"):
        constants.growth_phase(stem, "子")


@pytest.mark.parametrize("branch", ["", "A", "子水"])
def test_growth_phase_rejects_invalid_branch(branch: str) -> None:
    with pytest.raises(ValueError, match=f"Invalid branch: {branch!r}"):
        constants.growth_phase("甲", branch)
