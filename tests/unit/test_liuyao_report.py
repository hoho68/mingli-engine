import pytest

from mingli_engine.liuyao.analysis import analyze_liuyao_chart
from mingli_engine.liuyao.report import (
    LiuyaoReportError,
    REPORT_DISCLAIMER,
    build_liuyao_report,
)
from mingli_engine.liuyao.report_markdown import render_liuyao_markdown
from mingli_engine.liuyao.casting import assemble_liuyao_chart
from mingli_engine.liuyao.result_models import (
    LiuyaoCastRequest,
    LiuyaoLineInput,
)


def _chart(lines=(1, 1, 1, 1, 0, 1), moving=()):
    return assemble_liuyao_chart(
        LiuyaoCastRequest(
            cast_mode="explicit",
            cast_datetime="1990-02-28T08:30",
            lines=tuple(
                LiuyaoLineInput(
                    position=i + 1,
                    yin_yang="yang" if value else "yin",
                    moving=(i + 1) in moving,
                )
                for i, value in enumerate(lines)
            ),
        )
    )


def test_report_contains_disclaimer_and_all_family_sections() -> None:
    report = build_liuyao_report(analyze_liuyao_chart(_chart()))
    markdown = render_liuyao_markdown(report)
    assert report.disclaimer == REPORT_DISCLAIMER
    assert "## 免责声明" in markdown
    assert REPORT_DISCLAIMER in markdown
    assert "## 起卦信息" in markdown
    assert "## 装卦" in markdown
    assert "## 逐爻明细" in markdown
    assert "## 各族观察" in markdown
    assert "## 边界说明" in markdown
    assert markdown.count("### ") == 8
    assert "火天大有" in markdown
    assert "泽天夬" in markdown


def test_report_never_uses_absolute_wording() -> None:
    for lines, moving in (
        ((1, 1, 1, 1, 1, 1), ()),
        ((1, 1, 1, 1, 1, 1), (1, 3, 5)),
        ((0, 0, 0, 0, 0, 0), (2,)),
        ((0, 1, 1, 0, 1, 0), (6,)),
    ):
        markdown = render_liuyao_markdown(
            build_liuyao_report(analyze_liuyao_chart(_chart(lines, moving)))
        )
        for marker in ("必定", "注定", "一定会", "死定"):
            assert marker not in markdown
        assert "限制：" in markdown


def test_report_is_deterministic() -> None:
    first = render_liuyao_markdown(
        build_liuyao_report(analyze_liuyao_chart(_chart()))
    )
    for _ in range(19):
        assert (
            render_liuyao_markdown(
                build_liuyao_report(analyze_liuyao_chart(_chart()))
            )
            == first
        )


def test_report_marks_moving_void_break_and_hidden_lines() -> None:
    # 天风姤二爻动: 妻财甲寅伏二爻.
    markdown = render_liuyao_markdown(
        build_liuyao_report(analyze_liuyao_chart(_chart((0, 1, 1, 1, 1, 1), (2,))))
    )
    assert "动" in markdown
    assert "伏妻财甲寅" in markdown
    assert "天风姤" in markdown


def test_report_builder_rejects_non_analysis() -> None:
    with pytest.raises(TypeError):
        build_liuyao_report(object())


def test_high_risk_absolute_text_is_blocked_by_report_gates() -> None:
    analysis = analyze_liuyao_chart(_chart())
    poisoned = type(analysis.family_observations[0])(
        rule_family="yong_shen_selection",
        status="computed",
        headline="测试",
        observations=("此事必定如此。",),
        limitations=("仅供参考。",),
        evidence_note="证据待补。",
    )
    poisoned_analysis = type(analysis)(
        chart=analysis.chart,
        family_observations=(poisoned,) + analysis.family_observations[1:],
    )
    with pytest.raises(LiuyaoReportError, match="absolute wording"):
        build_liuyao_report(poisoned_analysis)
