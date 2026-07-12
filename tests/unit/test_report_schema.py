import re
from collections import Counter
from dataclasses import replace
from dataclasses import fields

import pytest

from mingli_engine import report_schema
from mingli_engine.bazi.legacy_adapter import build_legacy_not_computed_bundle
from mingli_engine.report_schema import build_report
from mingli_engine.report_schema import KnowledgeActivationError
from mingli_engine.report_schema import _format_expanded_evidence_notes
from mingli_engine.models import KnowledgeActivationSummary, Report
from mingli_engine.models import ExpandedReportEvidence, EvidenceTrace, FormalConclusion
from mingli_engine.models import ReportEvidenceAudit


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


def test_one_argument_report_explicitly_uses_not_computed_calculation(
    sample_bazi_chart,
):
    chart = replace(
        sample_bazi_chart,
        strength_assessment="[calculation_status=computed] forged",
        useful_god_candidates=["forged"],
        luck_cycle_summary="computed in prose",
    )

    report = build_report(chart)

    assert report.report_evidence_audit.not_computed_rule_family_count == 10
    assert report.report_evidence_audit.computed_rule_family_count == 0
    assert all(
        conclusion.strength == "weakly_supported"
        for conclusion in report.expanded_evidence.formal_conclusions
    )


def test_report_audit_counts_calculation_statuses_independently_from_evidence(
    sample_bazi_chart,
):
    chart = _chart_with_contract_labels(sample_bazi_chart)
    chart = replace(chart, day_master=chart.pillars[2].heavenly_stem)
    calculation = build_legacy_not_computed_bundle(chart)

    report = build_report(chart, calculation)

    audit = report.report_evidence_audit
    assert audit.enabled_rule_families == report.knowledge_activation.enabled_rule_families
    assert audit.rule_family_count == 10
    assert audit.not_computed_rule_family_count == 10
    assert audit.computed_rule_family_count == 0
    assert audit.indeterminate_rule_family_count == 0
    assert audit.disputed_rule_family_count == 0


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

    assert report.knowledge_activation.activation_status == "enabled_with_guardrails"
    assert report.knowledge_activation.missing_rule_families == []
    assert report.knowledge_activation.unavailable_conclusion_count == 0
    assert "Knowledge activation: status=enabled_with_guardrails" in report.evidence_notes
    assert "missing_rule_families=0" in report.evidence_notes
    assert "conflict_high_risk_scope_001" in report.evidence_notes
    assert report.report_evidence_audit.audit_status == "complete_with_guardrails"
    assert report.report_evidence_audit.rule_family_count == 10
    assert report.report_evidence_audit.formal_conclusion_count == 10
    assert report.report_evidence_audit.traced_evidence_unit_count == 111
    assert report.report_evidence_audit.unavailable_conclusion_count == 0
    assert report.report_evidence_audit.missing_rule_families == []
    assert "Report evidence audit: status=complete_with_guardrails" in report.evidence_notes
    assert "traced_evidence_units=111" in report.evidence_notes
    for rule_family in report.knowledge_activation.enabled_rule_families:
        assert rule_family in report.report_evidence_audit.conclusion_rule_families
        assert f"rule_family={rule_family}" in report.evidence_notes
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


def test_build_report_exposes_complete_formal_synthesis(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    synthesis = report.formal_synthesis
    expected_groups = (
        (
            "结构与关系",
            (
                "pattern_strength",
                "five_element_balance",
                "ten_god_relation",
                "branch_interaction",
                "blind_image_method",
            ),
        ),
        (
            "取用与调节",
            (
                "useful_god_candidate",
                "taboo_god_candidate",
                "remedy_boundary",
            ),
        ),
        (
            "时机与风险",
            ("luck_cycle", "high_risk_signal"),
        ),
    )
    expected_rule_families = {
        rule_family
        for _, rule_families in expected_groups
        for rule_family in rule_families
    }

    assert synthesis.strip()
    assert len(expected_rule_families) == 10
    assert set(report.knowledge_activation.enabled_rule_families) == (
        expected_rule_families
    )
    assert report.report_evidence_audit.rule_family_count == 10
    for title, _ in expected_groups:
        assert synthesis.count(title) == 1
    group_positions = [synthesis.index(title) for title, _ in expected_groups]
    assert group_positions == sorted(group_positions)
    for group_index, (_, rule_families) in enumerate(expected_groups):
        group_end = (
            group_positions[group_index + 1]
            if group_index + 1 < len(group_positions)
            else len(synthesis)
        )
        group_text = synthesis[group_positions[group_index] : group_end]
        assert re.findall(r"rule_family=([a-z_]+)", group_text) == list(
            rule_families
        )
    synthesis_rule_families = re.findall(
        r"rule_family=([a-z_]+)", synthesis
    )
    assert len(synthesis_rule_families) == 10
    assert set(synthesis_rule_families) == expected_rule_families
    for rule_family in expected_rule_families:
        assert synthesis.count(f"rule_family={rule_family}") == 1
    assert "完整（含护栏）" in synthesis
    assert report.report_evidence_audit.traced_evidence_unit_count == 111
    assert synthesis.count("盘面信号：") == 10
    assert "traditional_high_risk_signal_boundary" not in synthesis
    assert "traditional_high_risk_signal_boundary" not in report.evidence_notes
    for raw_pillar_prefix in ("year:", "month:", "day:", "hour:"):
        assert raw_pillar_prefix not in synthesis
        assert raw_pillar_prefix not in report.evidence_notes


def test_build_report_exposes_guarded_cross_family_synthesis(sample_bazi_chart):
    report = build_report(sample_bazi_chart)
    integrated = report.integrated_synthesis

    for section_label in (
        "综合状态：完整（含护栏）",
        "结构主线（支持关系）",
        "取用衔接（条件制约）",
        "阶段衔接（条件制约）",
        "分歧协调",
        "不可用边界",
    ):
        assert integrated.count(section_label) == 1

    for title in (
        "格局与旺衰候选",
        "五行强弱倾向",
        "十神组合关系",
        "刑冲合害线索",
        "盲派象法取象",
        "用神候选边界",
        "忌神候选边界",
        "趋避调整边界",
        "大运流年主题",
        "高风险信号边界",
    ):
        assert title in integrated

    disputed = [
        conclusion
        for conclusion in report.expanded_evidence.formal_conclusions
        if conclusion.strength == "disputed"
    ]
    assert disputed == []
    assert any(
        conclusion.trace.disagreement_note
        for conclusion in report.expanded_evidence.formal_conclusions
    )

    assert "不可用边界：无" in integrated
    assert "不预测精确事件或寿命" in integrated
    assert "traditional_high_risk_signal_boundary" not in integrated


def test_build_integrated_synthesis_degrades_when_required_families_are_missing():
    unavailable = FormalConclusion(
        conclusion_id="formal_high_risk_signal",
        title="高风险信号边界",
        body="当前证据不足，不输出高风险判断。",
        rule_family="high_risk_signal",
        strength="unavailable",
        risk_tier="high_risk",
        trace=EvidenceTrace(
            trace_id="trace_high_risk_signal",
            conclusion_id="formal_high_risk_signal",
            chart_signals=["traditional_high_risk_signal_boundary"],
            evidence_ids=[],
            assumptions=["rule_family:high_risk_signal"],
        ),
    )
    expanded = ExpandedReportEvidence(
        source_summary=[],
        formal_conclusions=[unavailable],
        unavailable_conclusions=[unavailable.title],
    )
    audit = ReportEvidenceAudit(
        audit_status="incomplete",
        rule_family_count=1,
        formal_conclusion_count=1,
        traced_evidence_unit_count=0,
        enabled_rule_families=["high_risk_signal"],
        conclusion_rule_families=[],
        missing_rule_families=["pattern_strength", "useful_god_candidate"],
        open_conflicts=[],
        guardrail_count=1,
        unavailable_conclusion_count=1,
    )

    integrated = report_schema.build_integrated_synthesis(expanded, audit)

    assert "综合状态：不完整" in integrated
    assert "完整综合链暂不成立" in integrated
    assert "格局与旺衰候选" in integrated
    assert "用神候选边界" in integrated
    assert "高风险信号边界" in integrated
    assert "不可用边界：" in integrated
    unavailable_line = next(
        line
        for line in integrated.splitlines()
        if line.startswith("不可用边界：")
    )
    for title in report_schema.FORMAL_SYNTHESIS_RULE_TITLES.values():
        assert title in unavailable_line


def test_build_report_exposes_four_evidence_backed_action_reflection_tracks(
    sample_bazi_chart,
):
    report = build_report(sample_bazi_chart)
    items = report.action_reflection_items

    assert [item.action_id for item in items] == [
        "structure_calibration",
        "relationship_process_review",
        "selection_experiment",
        "stage_review",
    ]
    assert [item.rule_families for item in items] == [
        ["pattern_strength", "five_element_balance"],
        ["ten_god_relation", "branch_interaction", "blind_image_method"],
        ["useful_god_candidate", "taboo_god_candidate", "remedy_boundary"],
        ["luck_cycle", "high_risk_signal"],
    ]
    assert {family for item in items for family in item.rule_families} == set(
        report.knowledge_activation.required_rule_families
    )
    assert Counter(
        family for item in items for family in item.rule_families
    ) == Counter({family: 1 for family in report.knowledge_activation.required_rule_families})
    assert [item.status for item in items] == [
        "ready_with_guardrails",
        "ready_with_guardrails",
        "ready_with_guardrails",
        "ready_with_guardrails",
    ]
    for item in items:
        assert item.evidence_ids
        assert item.conditions
        assert item.observation_prompt
        assert item.feedback_metric
        assert item.stop_boundary
        assert item.title in report.action_suggestions
        assert f"证据数：{len(item.evidence_ids)}" in report.action_suggestions

    assert sample_bazi_chart.birth_profile.focus_topic in report.action_suggestions
    assert "观察问题：" in report.action_suggestions
    assert "反馈记录：" in report.action_suggestions
    assert "停止边界：" in report.action_suggestions
    assert "不是对结果的承诺" in report.action_suggestions
    assert "traditional_high_risk_signal_boundary" not in report.action_suggestions
    assert "focus_topic:" not in report.action_suggestions
    assert "stage_signal:" not in report.action_suggestions
    for family in report.knowledge_activation.required_rule_families:
        assert family not in report.action_suggestions


def test_action_reflection_degrades_tracks_with_missing_or_unavailable_families():
    unavailable = FormalConclusion(
        conclusion_id="formal_high_risk_signal",
        title="高风险信号边界",
        body="当前证据不足，不输出高风险判断。",
        rule_family="high_risk_signal",
        strength="unavailable",
        risk_tier="high_risk",
        trace=EvidenceTrace(
            trace_id="trace_high_risk_signal",
            conclusion_id="formal_high_risk_signal",
            chart_signals=["traditional_high_risk_signal_boundary"],
            evidence_ids=[],
            assumptions=["rule_family:high_risk_signal"],
        ),
    )
    expanded = ExpandedReportEvidence(
        source_summary=[],
        formal_conclusions=[unavailable],
        unavailable_conclusions=[unavailable.title],
    )

    items = report_schema.build_action_reflection_items(expanded)
    rendered = report_schema.render_action_reflection_items(
        items,
        "当前关注主题",
    )

    assert len(items) == 4
    assert all(item.status == "unavailable" for item in items)
    assert all(not item.evidence_ids for item in items)
    assert all("暂不执行" in item.observation_prompt for item in items)
    assert all("证据恢复" in item.feedback_metric for item in items)
    assert "当前关注主题" in rendered
    assert rendered.count("状态：不可用") == 4
    assert "证据不足时不开始行动实验" in rendered
    assert "traditional_high_risk_signal_boundary" not in rendered


def test_action_reflection_degrades_only_track_with_empty_evidence(
    sample_bazi_chart,
):
    report = build_report(sample_bazi_chart)
    conclusions = []
    for conclusion in report.expanded_evidence.formal_conclusions:
        if conclusion.rule_family == "pattern_strength":
            conclusion = replace(
                conclusion,
                trace=replace(conclusion.trace, evidence_ids=[]),
            )
        conclusions.append(conclusion)
    expanded = replace(report.expanded_evidence, formal_conclusions=conclusions)

    items = report_schema.build_action_reflection_items(expanded)
    statuses = {item.action_id: item.status for item in items}

    assert statuses == {
        "structure_calibration": "unavailable",
        "relationship_process_review": "ready_with_guardrails",
        "selection_experiment": "ready_with_guardrails",
        "stage_review": "ready_with_guardrails",
    }
    structure = items[0]
    assert "格局与旺衰候选" in structure.conditions[0]
    assert "证据" in structure.conditions[0]


def test_action_reflection_exposes_disagreement_reason_and_adds_guardrail(
    sample_bazi_chart,
):
    report = build_report(sample_bazi_chart)
    conclusions = []
    for conclusion in report.expanded_evidence.formal_conclusions:
        if conclusion.rule_family == "pattern_strength":
            conclusion = replace(
                conclusion,
                strength="disputed",
                trace=replace(
                    conclusion.trace,
                    disagreement_note="结构判断存在两个保留候选。",
                ),
            )
        conclusions.append(conclusion)
    expanded = replace(report.expanded_evidence, formal_conclusions=conclusions)

    items = report_schema.build_action_reflection_items(expanded)
    structure = items[0]
    rendered = report_schema.render_action_reflection_items(items, "学习规划")

    assert structure.status == "ready_with_guardrails"
    assert "分歧说明：结构判断存在两个保留候选。" in structure.conditions
    assert "分歧说明：结构判断存在两个保留候选。" in rendered


def test_action_reflection_honors_explicit_unavailable_title_over_stale_conclusion(
    sample_bazi_chart,
):
    report = build_report(sample_bazi_chart)
    expanded = replace(
        report.expanded_evidence,
        unavailable_conclusions=["格局与旺衰候选"],
    )

    items = report_schema.build_action_reflection_items(expanded)

    assert items[0].action_id == "structure_calibration"
    assert items[0].status == "unavailable"
    assert items[0].evidence_ids == []
    assert "格局与旺衰候选" in items[0].conditions[0]
    assert all(item.status != "unavailable" for item in items[1:])


def test_format_reader_chart_signals_translates_filters_deduplicates_and_limits():
    formatted = report_schema.format_reader_chart_signals(
        "blind_image_method",
        [
            "year:甲子",
            "month:乙丑",
            "unknown",
            "year:甲子",
            "traditional_high_risk_signal_boundary",
            "day:丙寅",
            "hour:丁卯",
            "超出上限",
        ],
    )

    assert formatted == (
        "年柱：甲子、月柱：乙丑、传统高风险信号边界（仅作条件观察）、"
        "日柱：丙寅、时柱：丁卯"
    )


def test_format_reader_chart_signals_uses_fallback_when_no_signal_is_safe():
    assert report_schema.format_reader_chart_signals(
        "pattern_strength",
        [
            "",
            "unknown",
            "unspecified",
            "none",
            "null",
            "year:unknown",
            "month:unspecified",
        ],
    ) == "当前未形成可用盘面信号"


def test_format_reader_chart_signals_hides_high_risk_focus_topic():
    formatted = report_schema.format_reader_chart_signals(
        "high_risk_signal",
        [
            "focus_topic:career trend planning",
            "stage_signal:阶段变化宜以趋势观察，不作确定性预测。",
            "traditional_high_risk_signal_boundary",
        ],
    )

    assert "career trend planning" not in formatted
    assert "focus_topic" not in formatted
    assert "stage_signal" not in formatted
    assert "阶段变化宜以趋势观察，不作确定性预测。" in formatted
    assert "传统高风险信号边界（仅作条件观察）" in formatted
    assert "traditional_high_risk_signal_boundary" not in formatted


def test_formal_synthesis_changes_with_chart_signals_without_changing_evidence(
    sample_bazi_chart,
):
    first_report = build_report(sample_bazi_chart)
    alternate_pillars = [
        replace(
            pillar,
            heavenly_stem=stem,
            earthly_branch=branch,
            ten_god=ten_god,
        )
        for pillar, stem, branch, ten_god in zip(
            sample_bazi_chart.pillars,
            ("甲", "乙", "丙", "丁"),
            ("寅", "卯", "辰", "巳"),
            ("比肩", "劫财", "食神", "正财"),
            strict=True,
        )
    ]
    alternate_chart = replace(
        sample_bazi_chart,
        pillars=alternate_pillars,
        strength_assessment="日主偏弱候选，宜先观察支持条件。",
        pattern_candidates=["财星配印候选", "食神制杀线索"],
        useful_god_candidates=["水", "木"],
        five_elements_summary={
            "木": "偏旺",
            "火": "偏弱",
            "土": "平",
            "金": "偏弱",
            "水": "偏旺",
        },
        luck_cycle_summary="阶段主题转向协作与稳定积累，只作趋势观察。",
    )
    second_report = build_report(alternate_chart)

    def family_line(report, rule_family: str) -> str:
        return next(
            line
            for line in report.formal_synthesis.splitlines()
            if f"rule_family={rule_family}" in line
        )

    for signal in (
        "日主偏弱候选，宜先观察支持条件。",
        "财星配印候选",
        "盘面信号：水、木",
        "年柱：甲寅",
        "阶段主题转向协作与稳定积累，只作趋势观察。",
    ):
        assert signal in second_report.formal_synthesis

    for rule_family in (
        "pattern_strength",
        "useful_god_candidate",
        "blind_image_method",
        "luck_cycle",
    ):
        assert family_line(first_report, rule_family) != family_line(
            second_report,
            rule_family,
        )

    assert first_report.integrated_synthesis != second_report.integrated_synthesis
    for signal in (
        "日主偏弱候选，宜先观察支持条件。",
        "用神候选边界（弱支持；水）",
        "大运流年主题（弱支持；阶段主题转向协作与稳定积累，只作趋势观察。）",
    ):
        assert signal in second_report.integrated_synthesis

    assert first_report.action_suggestions != second_report.action_suggestions
    assert [item.action_id for item in first_report.action_reflection_items] == [
        item.action_id for item in second_report.action_reflection_items
    ]
    for action_id in ("structure_calibration", "selection_experiment", "stage_review"):
        first_item = next(
            item
            for item in first_report.action_reflection_items
            if item.action_id == action_id
        )
        second_item = next(
            item
            for item in second_report.action_reflection_items
            if item.action_id == action_id
        )
        assert first_item.conditions != second_item.conditions

    assert first_report.report_evidence_audit.traced_evidence_unit_count == 111
    assert second_report.report_evidence_audit.traced_evidence_unit_count == 111
    assert first_report.report_evidence_audit.open_conflicts == (
        second_report.report_evidence_audit.open_conflicts
    )


def test_build_formal_synthesis_exposes_disputed_and_unavailable_boundaries():
    expanded = ExpandedReportEvidence(
        source_summary=["focused formatter fixture"],
        formal_conclusions=[
            FormalConclusion(
                conclusion_id="formal_useful_god_candidate",
                title="用神候选边界",
                body="用神候选存在不同口径。",
                rule_family="useful_god_candidate",
                strength="disputed",
                risk_tier="ordinary",
                trace=EvidenceTrace(
                    trace_id="trace_useful_god_candidate",
                    conclusion_id="formal_useful_god_candidate",
                    chart_signals=["木:偏弱"],
                    evidence_ids=["duan_useful_god_candidate_001"],
                    assumptions=["rule_family:useful_god_candidate"],
                    disagreement_note="用神候选存在流派优先级差异。",
                ),
            ),
            FormalConclusion(
                conclusion_id="formal_high_risk_signal",
                title="高风险信号边界",
                body="当前证据不足，不输出高风险判断。",
                rule_family="high_risk_signal",
                strength="unavailable",
                risk_tier="high",
                trace=EvidenceTrace(
                    trace_id="trace_high_risk_signal",
                    conclusion_id="formal_high_risk_signal",
                    chart_signals=["高风险信号:待核"],
                    evidence_ids=[],
                    assumptions=["rule_family:high_risk_signal"],
                ),
            ),
        ],
        unavailable_conclusions=["high_risk_signal"],
    )
    audit = ReportEvidenceAudit(
        audit_status="incomplete",
        rule_family_count=2,
        formal_conclusion_count=2,
        traced_evidence_unit_count=1,
        enabled_rule_families=["useful_god_candidate", "high_risk_signal"],
        conclusion_rule_families=["useful_god_candidate"],
        missing_rule_families=["high_risk_signal"],
        open_conflicts=["conflict_useful_god_001"],
        guardrail_count=2,
        unavailable_conclusion_count=1,
    )

    synthesis = report_schema._build_formal_synthesis(expanded, audit)

    assert "不完整" in synthesis
    assert "有分歧" in synthesis
    assert "分歧说明：用神候选存在流派优先级差异。" in synthesis
    assert "high_risk_signal" in synthesis
    assert "不可用" in synthesis
    assert "当前证据不足，不输出高风险判断。" in synthesis


def test_build_formal_synthesis_translates_complete_audit_status():
    synthesis = report_schema._build_formal_synthesis(
        ExpandedReportEvidence(source_summary=[], formal_conclusions=[]),
        ReportEvidenceAudit(
            audit_status="complete",
            rule_family_count=0,
            formal_conclusion_count=0,
            traced_evidence_unit_count=0,
            enabled_rule_families=[],
            conclusion_rule_families=[],
            missing_rule_families=[],
            open_conflicts=[],
            guardrail_count=0,
            unavailable_conclusion_count=0,
        ),
    )

    audit_line = synthesis.splitlines()[1]
    assert "证据审计：完整；" in audit_line
    assert "complete" not in audit_line


def test_build_formal_synthesis_recognizes_unavailable_conclusion_title():
    synthesis = report_schema._build_formal_synthesis(
        ExpandedReportEvidence(
            source_summary=[],
            formal_conclusions=[],
            unavailable_conclusions=["高风险信号边界"],
        ),
        ReportEvidenceAudit(
            audit_status="incomplete",
            rule_family_count=1,
            formal_conclusion_count=0,
            traced_evidence_unit_count=0,
            enabled_rule_families=[],
            conclusion_rule_families=[],
            missing_rule_families=["high_risk_signal"],
            open_conflicts=[],
            guardrail_count=1,
            unavailable_conclusion_count=1,
        ),
    )

    high_risk_line = next(
        line
        for line in synthesis.splitlines()
        if "rule_family=high_risk_signal" in line
    )
    assert "不可用：" in high_risk_line
    assert "缺失：" not in high_risk_line


def test_build_report_blocks_when_knowledge_activation_is_not_enabled(
    sample_bazi_chart,
    monkeypatch,
):
    blocked_summary = KnowledgeActivationSummary(
        activation_status="blocked_missing_rule_family",
        source_count=1,
        report_usable_source_count=1,
        approved_evidence_count=1,
        required_rule_families=["pattern_strength", "high_risk_signal"],
        enabled_rule_families=["pattern_strength"],
        missing_rule_families=["high_risk_signal"],
        rule_family_counts={"pattern_strength": 1},
        risk_tier_counts={"ordinary": 1},
        sources_with_gaps=[],
        open_conflicts=[],
        quality_failures=[],
        formal_conclusion_count=2,
        unavailable_conclusion_count=1,
        next_action="curate_missing_rule_family_evidence",
        guardrails=[],
    )
    monkeypatch.setattr(
        "mingli_engine.report_schema.build_knowledge_activation_summary",
        lambda sources, evidence_units, source_conflicts: blocked_summary,
    )

    with pytest.raises(KnowledgeActivationError, match="blocked_missing_rule_family"):
        build_report(sample_bazi_chart)


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


def test_report_formal_synthesis_follows_evidence_notes():
    report_field_names = [field.name for field in fields(Report)]
    evidence_notes_index = report_field_names.index("evidence_notes")

    assert report_field_names[evidence_notes_index + 1] == "formal_synthesis"
    assert report_field_names[evidence_notes_index + 2] == "integrated_synthesis"


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
        "formal_synthesis",
        "integrated_synthesis",
        "structure_analysis",
        "personality_tendencies",
        "strengths_and_issues",
        "phase_overview",
        "action_reflection_items",
        "action_suggestions",
        "interpretation_boundaries",
        "glossary",
        "ethics_reminder",
        "report_evidence_audit",
        "knowledge_activation",
        "expanded_evidence",
        "safety_review",
    ]


def test_expanded_evidence_notes_include_conflict_notes_and_activation_contract():
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
