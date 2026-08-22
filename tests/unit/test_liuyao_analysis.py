import pytest

from mingli_engine.liuyao.analysis import (
    AnalysisConfigError,
    LIUYAO_RULE_FAMILIES,
    LiuyaoAnalysis,
    analyze_liuyao_chart,
    load_analysis_config,
)
from mingli_engine.liuyao.casting import assemble_liuyao_chart
from mingli_engine.liuyao.result_models import (
    LiuyaoCastRequest,
    LiuyaoChart,
    LiuyaoLineInput,
)


def _chart(lines: tuple[int, ...], moving: tuple[int, ...] = ()) -> LiuyaoChart:
    return assemble_liuyao_chart(
        LiuyaoCastRequest(
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
    )


def test_analysis_config_loads_with_governed_family_order() -> None:
    config = load_analysis_config()
    assert tuple(item.rule_family for item in config.families) == LIUYAO_RULE_FAMILIES
    assert config.evidence_pending_note
    assert config.shared_limitations
    assert all(item.label and item.headline for item in config.families)


def test_analysis_covers_eight_families_in_order() -> None:
    analysis = analyze_liuyao_chart(_chart((1, 1, 1, 1, 0, 1)))
    assert isinstance(analysis, LiuyaoAnalysis)
    assert tuple(
        item.rule_family for item in analysis.family_observations
    ) == LIUYAO_RULE_FAMILIES
    for item in analysis.family_observations:
        assert item.limitations
        assert item.evidence_note
        assert item.headline
    by_family = {item.rule_family: item for item in analysis.family_observations}
    assert by_family["category_judgment"].status == "not_computed"
    assert by_family["yingqi_timing"].status == "degraded"
    assert by_family["yong_shen_selection"].status == "computed"
    assert by_family["shi_ying_relation"].status == "computed"
    assert by_family["moving_line_dynamics"].status == "computed"
    assert by_family["six_spirits_attachment"].status == "computed"
    assert by_family["month_day_strength"].status == "computed"
    assert by_family["void_break_state"].status == "computed"


def test_yong_shen_observation_reports_relations_and_hidden_spirits() -> None:
    # 天风姤: 妻财伏于二爻.
    analysis = analyze_liuyao_chart(_chart((0, 1, 1, 1, 1, 1)))
    yong = {
        item.rule_family: item for item in analysis.family_observations
    }["yong_shen_selection"]
    text = "".join(yong.observations)
    assert "六亲分布" in text
    assert "妻财伏于2爻" in text


def test_moving_line_dynamics_reports_returning_relation() -> None:
    quiet = analyze_liuyao_chart(_chart((1, 1, 1, 1, 1, 1)))
    moving = {
        item.rule_family: item for item in quiet.family_observations
    }["moving_line_dynamics"]
    assert "安静无动爻" in moving.observations[0]

    active = analyze_liuyao_chart(_chart((1, 1, 1, 1, 1, 1), (1,)))
    dynamics = {
        item.rule_family: item for item in active.family_observations
    }["moving_line_dynamics"]
    text = dynamics.observations[0]
    assert "1爻" in text and "动" in text and "变出" in text
    # 乾为天初爻甲子动，变出辛丑: 丑土生/克 子水 -> 回头关系提示
    assert "辛丑" in text


def test_void_break_and_month_day_observations_use_chart_flags() -> None:
    # 乾为天(甲子日寅月): 六爻戌空、五爻申月破、四爻午日破.
    analysis = analyze_liuyao_chart(_chart((1, 1, 1, 1, 1, 1)))
    by_family = {item.rule_family: item for item in analysis.family_observations}
    void_text = "".join(by_family["void_break_state"].observations)
    assert "戌亥" in void_text
    assert "6爻" in void_text
    assert "5爻" in void_text
    assert "4爻" in void_text
    strength_text = "".join(by_family["month_day_strength"].observations)
    assert "月建寅" in strength_text
    assert "日辰子" in strength_text


def test_analysis_is_deterministic() -> None:
    first = analyze_liuyao_chart(_chart((0, 1, 1, 0, 1, 0)))
    for _ in range(19):
        assert analyze_liuyao_chart(_chart((0, 1, 1, 0, 1, 0))) == first


def test_analysis_config_rejects_wrong_family_order() -> None:
    config = load_analysis_config()
    reordered = tuple(reversed(config.families))
    with pytest.raises(ValueError, match="governed order"):
        type(config)(
            families=reordered,
            evidence_pending_note=config.evidence_pending_note,
            shared_limitations=config.shared_limitations,
        )


def test_analysis_config_missing_file_raises(tmp_path, monkeypatch) -> None:
    from mingli_engine.liuyao import analysis as analysis_module

    original = analysis_module.load_analysis_config

    class _Missing:
        def read_text(self, encoding: str) -> str:
            raise OSError("missing")

    monkeypatch.setattr(
        analysis_module.resources,
        "files",
        lambda package: type("R", (), {"joinpath": lambda self, p: _Missing()})(),
    )
    with pytest.raises(AnalysisConfigError, match="unavailable"):
        original()
