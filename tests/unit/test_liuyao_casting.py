import pytest

from mingli_engine.liuyao.casting import assemble_liuyao_chart
from mingli_engine.liuyao.result_models import (
    LiuyaoCastRequest,
    LiuyaoLineInput,
)


def _explicit(lines: tuple[int, ...], moving: tuple[int, ...] = ()) -> LiuyaoCastRequest:
    return LiuyaoCastRequest(
        cast_mode="explicit",
        cast_datetime="1990-02-28T08:30",
        lines=tuple(
            LiuyaoLineInput(
                position=index + 1,
                yin_yang="yang" if value else "yin",
                moving=(index + 1) in moving,
            )
            for index, value in enumerate(lines)
        ),
    )


def test_time_casting_matches_documented_conversion() -> None:
    # 1990-02-28T08:30 = 庚午年二月初四辰时: upper (7+2+4)%8=5 巽,
    # lower (7+2+4+5)%8=2 兑, moving 18%6=0->6 → 风泽中孚六爻动.
    chart = assemble_liuyao_chart(
        LiuyaoCastRequest(cast_mode="time", cast_datetime="1990-02-28T08:30")
    )
    assert chart.ben_gua.gua_name == "风泽中孚"
    assert [line.position for line in chart.lines if line.moving] == [6]
    assert chart.cast_mode == "time"


def test_number_casting_matches_documented_conversion() -> None:
    # (7, 9): upper 7 艮, lower 9%8=1 乾, moving 16%6=4 → 山天大畜四爻动.
    chart = assemble_liuyao_chart(
        LiuyaoCastRequest(
            cast_mode="number",
            cast_datetime="1990-02-28T08:30",
            numbers=(7, 9),
        )
    )
    assert chart.ben_gua.gua_name == "山天大畜"
    assert [line.position for line in chart.lines if line.moving] == [4]


def test_number_casting_zero_remainder_maps_to_eight_and_six() -> None:
    # (8, 8): upper 8 坤, lower 8 坤, moving 16%6=4 → 坤为地四爻动.
    chart = assemble_liuyao_chart(
        LiuyaoCastRequest(
            cast_mode="number",
            cast_datetime="1990-02-28T08:30",
            numbers=(8, 8),
        )
    )
    assert chart.ben_gua.gua_name == "坤为地"
    assert [line.position for line in chart.lines if line.moving] == [4]


def test_casting_modes_converge_on_the_same_chart_pipeline() -> None:
    explicit_chart = assemble_liuyao_chart(_explicit((1, 1, 1, 0, 0, 1), (4,)))
    number_chart = assemble_liuyao_chart(
        LiuyaoCastRequest(
            cast_mode="number",
            cast_datetime="1990-02-28T08:30",
            numbers=(7, 9),
        )
    )
    assert explicit_chart.ben_gua == number_chart.ben_gua
    assert explicit_chart.lines == number_chart.lines


def test_casting_validation_rejects_mismatched_fields() -> None:
    with pytest.raises(ValueError, match="exactly two positive integers"):
        LiuyaoCastRequest(
            cast_mode="number",
            cast_datetime="1990-02-28T08:30",
            numbers=(7,),
        )
    with pytest.raises(ValueError, match="no lines or numbers"):
        LiuyaoCastRequest(
            cast_mode="time",
            cast_datetime="1990-02-28T08:30",
            numbers=(7, 9),
        )
    with pytest.raises(ValueError, match="does not take numbers"):
        LiuyaoCastRequest(
            cast_mode="explicit",
            cast_datetime="1990-02-28T08:30",
            lines=tuple(
                LiuyaoLineInput(position=i + 1, yin_yang="yang", moving=False)
                for i in range(6)
            ),
            numbers=(7, 9),
        )


def test_all_modes_are_deterministic() -> None:
    requests = (
        _explicit((1, 1, 1, 1, 0, 1)),
        LiuyaoCastRequest(cast_mode="time", cast_datetime="1990-02-28T08:30"),
        LiuyaoCastRequest(
            cast_mode="number", cast_datetime="1990-02-28T08:30", numbers=(3, 5)
        ),
    )
    for request in requests:
        first = assemble_liuyao_chart(request)
        for _ in range(19):
            assert assemble_liuyao_chart(request) == first
