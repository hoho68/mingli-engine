import json
from pathlib import Path

import pytest

from mingli_engine.liuyao.calendar_bridge import (
    CalendarBridgeError,
    month_command_and_day_ganzhi,
    parse_cast_datetime,
    xun_void_branches,
)
from mingli_engine.liuyao.casting import assemble_liuyao_chart
from mingli_engine.liuyao.najia import (
    NajiaError,
    derive_bian_gua,
    derive_hu_gua,
    gua_info_from_lines,
)
from mingli_engine.liuyao.result_models import (
    LiuyaoCastRequest,
    LiuyaoLineInput,
)

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "liuyao"
    / "golden_vectors.json"
)


def _load_vectors() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _request(vector: dict) -> LiuyaoCastRequest:
    context = _load_vectors()["day_context"]
    return LiuyaoCastRequest(
        cast_mode="explicit",
        cast_datetime=context["cast_datetime"],
        lines=tuple(
            LiuyaoLineInput(
                position=index + 1,
                yin_yang="yang" if value else "yin",
                moving=(index + 1) in vector["moving"],
            )
            for index, value in enumerate(vector["lines"])
        ),
    )


def test_result_models_enforce_strict_validation() -> None:
    with pytest.raises(ValueError, match="six lines"):
        LiuyaoCastRequest(
            cast_mode="explicit",
            cast_datetime="1990-02-28T08:30",
            lines=(
                LiuyaoLineInput(position=1, yin_yang="yang", moving=False),
            ),
        )
    with pytest.raises(ValueError, match="between 1 and 6"):
        LiuyaoLineInput(position=7, yin_yang="yang", moving=False)
    with pytest.raises(ValueError, match="YYYY-MM-DDTHH:MM"):
        LiuyaoCastRequest(cast_mode="time", cast_datetime="1990-02-28 08:30")
    with pytest.raises(ValueError, match="no lines or numbers"):
        LiuyaoCastRequest(cast_mode="time", cast_datetime="1990-02-28T08:30", numbers=(1, 2))
    with pytest.raises(ValueError, match="two positive integers"):
        LiuyaoCastRequest(cast_mode="number", cast_datetime="1990-02-28T08:30", numbers=(0, 2))
    with pytest.raises(ValueError, match="does not take lines"):
        LiuyaoCastRequest(
            cast_mode="number",
            cast_datetime="1990-02-28T08:30",
            lines=tuple(
                LiuyaoLineInput(position=i + 1, yin_yang="yang", moving=False)
                for i in range(6)
            ),
            numbers=(1, 2),
        )
    with pytest.raises(ValueError, match="positions 1-6 exactly once"):
        LiuyaoCastRequest(
            cast_mode="explicit",
            cast_datetime="1990-02-28T08:30",
            lines=tuple(
                LiuyaoLineInput(position=1, yin_yang="yang", moving=False)
                for _ in range(6)
            ),
        )


def test_calendar_bridge_ranges_and_xun_void() -> None:
    with pytest.raises(CalendarBridgeError, match="out of range"):
        parse_cast_datetime("2100-01-01T00:00")
    with pytest.raises(CalendarBridgeError, match="YYYY-MM-DDTHH:MM"):
        parse_cast_datetime("1990/02/28 08:30")
    assert xun_void_branches("甲子") == ("戌", "亥")
    assert xun_void_branches("甲戌") == ("申", "酉")
    assert xun_void_branches("甲申") == ("午", "未")
    assert xun_void_branches("甲午") == ("辰", "巳")
    assert xun_void_branches("甲辰") == ("寅", "卯")
    assert xun_void_branches("甲寅") == ("子", "丑")
    month, day, stem = month_command_and_day_ganzhi(parse_cast_datetime("1990-02-28T08:30"))
    assert (month, day, stem) == ("寅", "甲子", "甲")
    month_2, day_2, stem_2 = month_command_and_day_ganzhi(parse_cast_datetime("1990-01-01T08:30"))
    assert (month_2, day_2, stem_2) == ("子", "丙寅", "丙")


def test_gua_lookup_rejects_non_gua_lines() -> None:
    with pytest.raises(NajiaError):
        gua_info_from_lines((1, 1, 1, 1, 1))
    with pytest.raises(NajiaError):
        gua_info_from_lines((1, 1, 1, 1, 1, 2))


def test_derive_bian_and_hu_gua() -> None:
    assert derive_bian_gua((1, 1, 1, 1, 1, 1), frozenset()) is None
    assert derive_bian_gua((1, 1, 1, 1, 1, 1), frozenset({1})).gua_name == "天风姤"
    assert derive_hu_gua((1, 1, 1, 1, 1, 1)).gua_name == "乾为天"
    assert derive_hu_gua((1, 1, 1, 1, 0, 1)).gua_name == "泽天夬"


@pytest.mark.parametrize(
    "vector",
    _load_vectors()["vectors"],
    ids=[vector["name"] for vector in _load_vectors()["vectors"]],
)
def test_golden_vectors_assemble_field_exact(vector: dict) -> None:
    chart = assemble_liuyao_chart(_request(vector))
    expected = vector["expected"]
    context = _load_vectors()["day_context"]

    assert chart.ben_gua.gua_name == expected["ben_gua"]
    assert chart.ben_gua.palace == expected["palace"]
    assert chart.ben_gua.palace_sequence == expected["palace_sequence"]
    assert chart.ben_gua.shi_position == expected["shi_position"]
    assert chart.ben_gua.ying_position == expected["ying_position"]
    if expected["bian_gua"] is None:
        assert chart.bian_gua is None
    else:
        assert chart.bian_gua is not None
        assert chart.bian_gua.gua_name == expected["bian_gua"]
    assert chart.hu_gua.gua_name == expected["hu_gua"]
    assert chart.month_command == context["month_command"]
    assert chart.day_ganzhi == context["day_ganzhi"]
    assert tuple(chart.xun_void_branches) == tuple(context["xun_void"])

    assert [line.ganzhi for line in chart.lines] == expected["ganzhi"]
    assert [line.six_relation for line in chart.lines] == expected["relations"]
    assert [line.six_spirit for line in chart.lines] == context["spirits_bottom_up"]
    shi_positions = [line.position for line in chart.lines if line.shi_ying == "shi"]
    ying_positions = [line.position for line in chart.lines if line.shi_ying == "ying"]
    assert shi_positions == [expected["shi_position"]]
    assert ying_positions == [expected["ying_position"]]
    for position, line in enumerate(chart.lines, start=1):
        expected_hidden = expected["hidden"].get(str(position))
        if expected_hidden is None:
            assert line.hidden_spirit is None
        else:
            assert line.hidden_spirit is not None
            assert line.hidden_spirit.ganzhi == expected_hidden[0]
            assert line.hidden_spirit.six_relation == expected_hidden[1]
            assert line.hidden_spirit.attached_position == position
        assert line.void == (position in expected["void_positions"])
        assert line.month_break == (position in expected["month_break_positions"])
        expected_day_break = (
            position in expected["day_break_positions"] and not line.moving
        )
        assert line.day_break == expected_day_break
    assert [line.moving for line in chart.lines] == [
        (index + 1) in vector["moving"] for index in range(6)
    ]
    assert chart.assumptions


def test_golden_vector_count_meets_release_gate() -> None:
    assert len(_load_vectors()["vectors"]) >= 20


def test_explicit_casting_is_deterministic() -> None:
    vector = _load_vectors()["vectors"][0]
    first = assemble_liuyao_chart(_request(vector))
    for _ in range(19):
        assert assemble_liuyao_chart(_request(vector)) == first
