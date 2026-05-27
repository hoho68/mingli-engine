from dataclasses import replace
from dataclasses import fields

import pytest

from mingli_engine.report_schema import build_report
from mingli_engine.report_schema import _format_expanded_evidence_notes
from mingli_engine.models import Report
from mingli_engine.models import ExpandedReportEvidence, EvidenceTrace, FormalConclusion


RAW_READER_LABELS = (
    "auto_calculated",
    "external_verified",
    "medium",
    "gregorian",
    "year：",
    "month：",
    "day：",
    "hour：",
)


def _report_body(report) -> str:
    return "\n".join(
        [
            report.quick_guide,
            report.chart_card,
            report.assumptions,
            report.four_pillars_summary,
            report.five_elements_summary,
            report.ten_gods_summary,
            report.evidence_notes,
            report.structure_analysis,
            report.personality_tendencies,
            report.strengths_and_issues,
            report.phase_overview,
            report.action_suggestions,
            report.interpretation_boundaries,
        ]
    )


def _chart_with_contract_labels(sample_bazi_chart):
    birth_profile = replace(
        sample_bazi_chart.birth_profile,
        calendar_type="gregorian",
        gender="未指定",
    )
    chart_source = replace(
        sample_bazi_chart.chart_source,
        source_type="auto_calculated",
        confidence="medium",
    )
    pillars = [
        replace(pillar, name=name)
        for pillar, name in zip(
            sample_bazi_chart.pillars,
            ("year", "month", "day", "hour"),
            strict=True,
        )
    ]
    return replace(
        sample_bazi_chart,
        birth_profile=birth_profile,
        chart_source=chart_source,
        pillars=pillars,
    )


def test_build_report_returns_complete_safe_report(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    for field_name in (
        "disclaimer",
        "chart_card",
        "assumptions",
        "four_pillars_summary",
        "five_elements_summary",
        "ten_gods_summary",
        "evidence_notes",
        "structure_analysis",
        "phase_overview",
        "action_suggestions",
        "glossary",
        "ethics_reminder",
        "interpretation_boundaries",
        "quick_guide",
    ):
        assert getattr(report, field_name)

    assert report.safety_review.allowed is True
    assert report.safety_review.disclaimer_present is True


def test_build_report_includes_basic_interpretation_sections(sample_bazi_chart):
    report = build_report(sample_bazi_chart)
    combined = "\n".join(
        [
            report.five_elements_summary,
            report.ten_gods_summary,
            report.structure_analysis,
            report.personality_tendencies,
            report.strengths_and_issues,
            report.phase_overview,
            report.action_suggestions,
            report.interpretation_boundaries,
        ]
    )

    assert "五行数量可以先作为结构观察材料来看" in report.five_elements_summary
    assert "明面信号：" in report.five_elements_summary
    assert "藏干信号：" in report.five_elements_summary
    assert "合计信号：" in report.five_elements_summary
    assert "观察中心" in report.personality_tendencies
    assert "十神关系可以先按四个柱位理解为结构线索" in report.ten_gods_summary
    assert "基础结构可以先看分布是否集中" in report.structure_analysis
    assert "基础结构解读层" in report.phase_overview
    assert "不做大运流年判断" in report.phase_overview
    assert "不做格局定论" in combined
    assert "不做用神定论" in combined
    assert "不做大运流年判断" in combined
    assert combined.count("不做格局定论") == 1
    assert combined.count("不做用神定论") == 1
    assert sample_bazi_chart.birth_profile.focus_topic in report.action_suggestions
    assert "结构" in report.action_suggestions
    assert report.strengths_and_issues not in report.action_suggestions
    for old_phrase in (
        "五行信号观察：明面信号为",
        "这些数量用于观察结构分布",
        "基础结构观察：五行分布先看有无、多少与集中度。",
    ):
        assert old_phrase not in "\n".join(
            [
                report.five_elements_summary,
                report.ten_gods_summary,
                report.structure_analysis,
            ]
        )


def test_build_report_explains_observation_basis(sample_bazi_chart):
    report = build_report(_chart_with_contract_labels(sample_bazi_chart))

    assert "来源依据：" in report.evidence_notes
    assert "排盘来源" in report.evidence_notes
    assert "历法" in report.evidence_notes
    assert "四柱依据：" in report.evidence_notes
    for pillar_name in ("年柱", "月柱", "日柱", "时柱"):
        assert pillar_name in report.evidence_notes
    assert "五行依据：" in report.evidence_notes
    assert "明面信号" in report.evidence_notes
    assert "藏干信号" in report.evidence_notes
    assert "合计信号" in report.evidence_notes
    assert "十神依据：" in report.evidence_notes
    assert "关系线索" in report.evidence_notes
    assert "行动依据：" in report.evidence_notes
    assert "复盘问题" in report.evidence_notes
    assert "不预测具体结果" in report.evidence_notes


def test_build_report_attaches_expanded_source_backed_evidence(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    expanded = report.expanded_evidence

    assert expanded.source_summary
    assert expanded.formal_conclusions
    assert {item.rule_family for item in expanded.formal_conclusions}.issuperset(
        {
            "pattern_strength",
            "five_element_balance",
            "ten_god_relation",
            "branch_interaction",
            "blind_image_method",
            "luck_cycle",
        }
    )
    for conclusion in expanded.formal_conclusions:
        assert conclusion.strength in {
            "decided",
            "candidate",
            "weakly_supported",
            "disputed",
            "unavailable",
        }
        assert conclusion.trace.conclusion_id == conclusion.conclusion_id
        assert conclusion.trace.chart_signals
        assert conclusion.trace.evidence_ids
        assert conclusion.trace.assumptions


def test_build_report_prepares_quick_guide_and_boundary_layer(sample_bazi_chart):
    chart = _chart_with_contract_labels(sample_bazi_chart)
    report = build_report(chart)
    guide_lines = [
        line for line in report.quick_guide.splitlines() if line.startswith("- ")
    ]

    assert 3 <= len(guide_lines) <= 5
    assert "系统自动排盘" in report.quick_guide
    assert "中等可信度" in report.quick_guide
    assert "先核对资料与假设" in report.quick_guide
    assert "再看结构观察" in report.quick_guide
    assert "最后转成行动反思" in report.quick_guide
    assert chart.birth_profile.focus_topic in report.quick_guide
    assert "结构" in report.quick_guide
    assert "不做格局定论" in report.interpretation_boundaries
    assert "不做用神定论" in report.interpretation_boundaries
    assert "不做大运流年判断" in report.interpretation_boundaries
    assert report.interpretation_boundaries not in report.structure_analysis


def test_build_report_connects_source_and_structure_layers(sample_bazi_chart):
    report = build_report(_chart_with_contract_labels(sample_bazi_chart))

    assert (
        "这些基础资料只说明排盘依据与采用假设，不直接构成命理结论"
        in report.assumptions
    )
    assert "结构观察提供的是线索，不是最终判断" in report.structure_analysis
    assert "五行数量可以先作为结构观察材料来看" in report.five_elements_summary
    assert "十神关系可以先按四个柱位理解为结构线索" in report.ten_gods_summary
    assert "基础结构可以先看分布是否集中" in report.structure_analysis


def test_build_report_connects_boundaries_to_action_reflection(sample_bazi_chart):
    report = build_report(_chart_with_contract_labels(sample_bazi_chart))

    assert "这些边界是为了防止过度断言" in report.interpretation_boundaries
    assert "把可观察的线索转成复盘问题" in report.interpretation_boundaries
    assert "行动反思只作为复盘提示" in report.strengths_and_issues
    assert "不替代现实判断" in report.strengths_and_issues
    assert "不是对结果的承诺" in report.action_suggestions


def test_build_report_uses_reader_facing_labels(sample_bazi_chart):
    chart = _chart_with_contract_labels(sample_bazi_chart)
    report = build_report(chart)
    body = _report_body(report)

    assert "公历" in report.chart_card
    assert "系统自动排盘" in report.quick_guide
    assert "系统自动排盘" in report.assumptions
    assert "中等可信度" in report.quick_guide
    assert "中等可信度" in report.assumptions
    for pillar_name in ("年柱", "月柱", "日柱", "时柱"):
        assert f"- {pillar_name}：" in report.four_pillars_summary
    for raw_label in RAW_READER_LABELS:
        assert raw_label not in body


def test_build_report_uses_conservative_placeholder_for_unspecified_gender(
    sample_bazi_chart,
):
    birth_profile = replace(sample_bazi_chart.birth_profile, gender="未指定")
    chart = replace(sample_bazi_chart, birth_profile=birth_profile)
    report = build_report(chart)

    assert "性别标记：未说明" in report.chart_card


def test_build_report_preserves_unknown_non_empty_labels(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    assert "历法类型：solar" in report.chart_card
    assert "性别标记：female" in report.chart_card
    assert "externally_verified" in report.quick_guide
    assert "externally_verified" in report.assumptions
    assert "sample-high" in report.quick_guide
    assert "sample-high" in report.assumptions


def test_build_report_normalizes_placeholder_focus_topic(sample_bazi_chart):
    birth_profile = replace(sample_bazi_chart.birth_profile, focus_topic="unknown")
    chart = replace(sample_bazi_chart, birth_profile=birth_profile)

    report = build_report(chart)
    body = _report_body(report)

    assert "unknown" not in report.quick_guide
    assert "unknown" not in report.action_suggestions
    assert "unknown" not in body
    assert "当前关注主题" in report.quick_guide
    assert "当前关注主题" in report.action_suggestions
    assert "当前关注主题" in report.strengths_and_issues


def test_build_report_quick_guide_reads_like_plain_guidance(sample_bazi_chart):
    chart = _chart_with_contract_labels(sample_bazi_chart)
    report = build_report(chart)

    assert "这份盘的资料来自系统自动排盘" in report.quick_guide
    assert "这份盘里" in report.quick_guide
    assert "适合先从" in report.quick_guide
    assert "不是命运结论" in report.quick_guide
    assert "可复盘的小问题" in report.quick_guide


def test_build_report_blocks_exact_lifespan_focus_topic(sample_bazi_chart):
    birth_profile = replace(sample_bazi_chart.birth_profile, focus_topic="寿命多长")
    chart = replace(sample_bazi_chart, birth_profile=birth_profile)

    report = build_report(chart)

    assert report.safety_review.allowed is False
    assert "lifespan_or_death_timing" in report.safety_review.red_line_categories


def test_build_report_rejects_chart_without_four_pillars(sample_bazi_chart):
    chart = replace(sample_bazi_chart, pillars=[])

    with pytest.raises(ValueError, match="four pillars"):
        build_report(chart)


def test_report_public_contract_fields_remain_stable_for_012():
    assert [field.name for field in fields(Report)] == [
        "title",
        "disclaimer",
        "quick_guide",
        "chart_card",
        "assumptions",
        "four_pillars_summary",
        "five_elements_summary",
        "ten_gods_summary",
        "evidence_notes",
        "structure_analysis",
        "personality_tendencies",
        "strengths_and_issues",
        "phase_overview",
        "action_suggestions",
        "interpretation_boundaries",
        "glossary",
        "ethics_reminder",
        "expanded_evidence",
        "safety_review",
    ]


def test_expanded_evidence_notes_include_conflict_notes_without_new_report_fields():
    expanded = ExpandedReportEvidence(
        source_summary=["source / useful_god_candidate / ordinary"],
        formal_conclusions=[
            FormalConclusion(
                conclusion_id="formal_useful_god_candidate",
                title="用神候选边界",
                body="用神候选存在不同口径。",
                rule_family="useful_god_candidate",
                strength="candidate",
                risk_tier="ordinary",
                trace=EvidenceTrace(
                    trace_id="trace_useful_god_candidate",
                    conclusion_id="formal_useful_god_candidate",
                    chart_signals=["木:偏弱"],
                    evidence_ids=["duan_useful_god_candidate_001"],
                    assumptions=["rule_family:useful_god_candidate"],
                    disagreement_note="用神候选存在流派优先级差异。",
                ),
            )
        ],
    )

    notes = _format_expanded_evidence_notes(expanded)

    assert "分歧说明：用神候选存在流派优先级差异。" in notes
    assert [field.name for field in fields(Report)] == [
        "title",
        "disclaimer",
        "quick_guide",
        "chart_card",
        "assumptions",
        "four_pillars_summary",
        "five_elements_summary",
        "ten_gods_summary",
        "evidence_notes",
        "structure_analysis",
        "personality_tendencies",
        "strengths_and_issues",
        "phase_overview",
        "action_suggestions",
        "interpretation_boundaries",
        "glossary",
        "ethics_reminder",
        "expanded_evidence",
        "safety_review",
    ]
