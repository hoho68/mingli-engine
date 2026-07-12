from dataclasses import replace

from mingli_engine.bazi import CalculationBundle, build_legacy_not_computed_bundle
from mingli_engine.bazi.analysis import _require_calculation_bundle_binding
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.classical_sources import (
    load_approved_evidence_units,
    load_classical_sources,
    load_source_conflicts,
)
from mingli_engine.evidence_curation import build_knowledge_activation_summary
from mingli_engine.formal_interpretation import build_formal_interpretation
from mingli_engine.high_risk import classify_high_risk_request
from mingli_engine.interpretation import build_basic_interpretation
from mingli_engine.models import (
    ActionReflectionItem,
    BaziChart,
    ExpandedReportEvidence,
    FormalConclusion,
    KnowledgeActivationSummary,
    Report,
    ReportEvidenceAudit,
    SafetyReviewResult,
)
from mingli_engine.safety import safety_check


PLACEHOLDER_VALUES = frozenset({"", "未指定", "unspecified", "unknown", "none", "null"})

SOURCE_TYPE_LABELS = {
    "auto_calculated": "系统自动排盘",
    "external_verified": "外部排盘已核对",
}
CONFIDENCE_LABELS = {
    "low": "低可信度",
    "medium": "中等可信度",
    "high": "高可信度",
}
CALENDAR_TYPE_LABELS = {
    "gregorian": "公历",
}
PILLAR_NAME_LABELS = {
    "year": "年柱",
    "month": "月柱",
    "day": "日柱",
    "hour": "时柱",
    "年柱": "年柱",
    "月柱": "月柱",
    "日柱": "日柱",
    "时柱": "时柱",
}
READING_PATH_TRANSITION = (
    "阅读时可以先核对资料与假设，再看结构观察，再看解读边界，"
    "最后转成行动反思。"
)
SOURCE_BASIS_TRANSITION = (
    "这些基础资料只说明排盘依据与采用假设，不直接构成命理结论。"
)
STRUCTURE_BOUNDARY_TRANSITION = (
    "结构观察提供的是线索，不是最终判断；下一层会说明哪些地方不能过度解读。"
)
BOUNDARY_ACTION_TRANSITION = (
    "这些边界是为了防止过度断言；在边界内，再把可观察的线索转成复盘问题。"
)
ACTION_REFLECTION_TRANSITION = (
    "行动反思只作为复盘提示，用来整理可观察的线索，不替代现实判断。"
)
REPORT_ENABLED_ACTIVATION_STATUSES = frozenset({"enabled", "enabled_with_guardrails"})


class KnowledgeActivationError(ValueError):
    pass


def _reader_label(value: str | None, labels: dict[str, str]) -> str:
    normalized = (value or "").strip()
    if normalized.lower() in PLACEHOLDER_VALUES or normalized in PLACEHOLDER_VALUES:
        return "未说明"
    return labels.get(normalized, normalized)


def _focus_topic_label(value: str) -> str:
    label = _reader_label(value, {})
    if label == "未说明":
        return "当前关注主题"
    return label


def _normalize_focus_topic_text(text: str, raw_focus_topic: str) -> str:
    raw = raw_focus_topic.strip()
    label = _focus_topic_label(raw_focus_topic)
    if raw and label != raw:
        return text.replace(raw, label)
    return text


def _format_true_solar_time(value: bool | None) -> str:
    if value is True:
        return "已应用"
    if value is False:
        return "未应用"
    return "未说明"


def _merge_safety_reviews(
    *reviews: SafetyReviewResult, disclaimer_present: bool
) -> SafetyReviewResult:
    red_line_categories: list[str] = []
    prohibited_phrases: list[str] = []
    redirect_messages: list[str] = []

    for review in reviews:
        for category in review.red_line_categories:
            if category not in red_line_categories:
                red_line_categories.append(category)
        for phrase in review.prohibited_phrases:
            if phrase not in prohibited_phrases:
                prohibited_phrases.append(phrase)
        if review.redirect_message and review.redirect_message not in redirect_messages:
            redirect_messages.append(review.redirect_message)

    return SafetyReviewResult(
        allowed=not red_line_categories and not prohibited_phrases,
        red_line_categories=red_line_categories,
        prohibited_phrases=prohibited_phrases,
        disclaimer_present=disclaimer_present,
        redirect_message="\n".join(redirect_messages),
    )


def _review_focus_topic(focus_topic: str) -> SafetyReviewResult:
    review = safety_check(focus_topic, disclaimer_present=True)
    high_risk_review = classify_high_risk_request(focus_topic)
    if high_risk_review.allowed:
        return review

    narrowed_review = SafetyReviewResult(
        allowed=False,
        red_line_categories=high_risk_review.categories,
        disclaimer_present=True,
        redirect_message=high_risk_review.redirect_message,
    )
    return _merge_safety_reviews(review, narrowed_review, disclaimer_present=True)


def _build_chart_card(chart: BaziChart) -> str:
    profile = chart.birth_profile
    calendar_type = _reader_label(profile.calendar_type, CALENDAR_TYPE_LABELS)
    gender = _reader_label(profile.gender, {})
    focus_topic = _reader_label(profile.focus_topic, {})
    return "\n".join(
        [
            f"- 历法类型：{calendar_type}",
            f"- 出生日期：{profile.birth_date}",
            f"- 出生时间：{profile.birth_time}",
            f"- 出生地点：{profile.birthplace}",
            f"- 性别标记：{gender}",
            f"- 关注主题：{focus_topic}",
            f"- 日主：{chart.day_master}",
        ]
    )


def _build_assumptions(chart: BaziChart) -> str:
    source = chart.chart_source
    source_type = _reader_label(source.source_type, SOURCE_TYPE_LABELS)
    confidence = _reader_label(source.confidence, CONFIDENCE_LABELS)
    return "\n".join(
        [
            f"- 来源类型：{source_type}",
            f"- 来源说明：{source.source_note}",
            f"- 历法假设：{source.calendar_assumption}",
            f"- 时区假设：{source.timezone_assumption}",
            f"- 节气假设：{source.solar_terms_assumption}",
            f"- 真太阳时：{_format_true_solar_time(source.true_solar_time_applied)}",
            f"- 可信度：{confidence}",
        ]
    )


def _build_four_pillars_summary(chart: BaziChart) -> str:
    rows = []
    for pillar in chart.pillars:
        pillar_name = _reader_label(pillar.name, PILLAR_NAME_LABELS)
        hidden_stems = "、".join(pillar.hidden_stems) if pillar.hidden_stems else "无"
        rows.append(
            f"- {pillar_name}：{pillar.heavenly_stem}{pillar.earthly_branch}，"
            f"藏干：{hidden_stems}，十神：{pillar.ten_god}，五行：{pillar.element}"
        )
    return "\n".join(rows)


def _format_elements_for_report(elements: list[str]) -> str:
    return "、".join(elements) if elements else "暂无突出信号"


def _build_quick_guide(chart: BaziChart, interpretation) -> str:
    source = chart.chart_source
    focus_topic = _focus_topic_label(chart.birth_profile.focus_topic)
    source_label = _reader_label(source.source_type, SOURCE_TYPE_LABELS)
    confidence_label = _reader_label(source.confidence, CONFIDENCE_LABELS)
    dominant = _format_elements_for_report(
        interpretation.element_distribution.dominant_elements
    )
    return "\n".join(
        [
            f"- 来源：这份盘的资料来自{source_label}，当前标记为{confidence_label}。",
            f"- 结构：这份盘里，{dominant}的信号比较集中，适合先从这些方向看整体结构。",
            f"- 日主：{chart.day_master}是本报告的观察中心，不是命运结论。",
            f"- 路径：{READING_PATH_TRANSITION}",
            f"- 提示：围绕{focus_topic}，把结构观察转成可复盘的小问题。",
        ]
    )


def _format_knowledge_activation_notes(
    knowledge_activation: KnowledgeActivationSummary,
) -> str:
    lines = [
        f"- Knowledge activation: status={knowledge_activation.activation_status}",
        (
            "- Knowledge activation coverage: "
            f"sources={knowledge_activation.source_count}, "
            f"report_usable_sources={knowledge_activation.report_usable_source_count}, "
            f"approved_evidence_units={knowledge_activation.approved_evidence_count}, "
            f"enabled_rule_families={len(knowledge_activation.enabled_rule_families)}, "
            f"missing_rule_families={len(knowledge_activation.missing_rule_families)}, "
            f"unavailable_conclusions={knowledge_activation.unavailable_conclusion_count}"
        ),
    ]
    if knowledge_activation.open_conflicts:
        lines.append(
            "- Knowledge activation open conflicts: "
            + "銆?".join(knowledge_activation.open_conflicts)
        )
    if knowledge_activation.guardrails:
        lines.append(
            "- Knowledge activation guardrails: "
            + " / ".join(knowledge_activation.guardrails)
        )
    return "\n".join(lines)


def _unique_preserving_order(values: list[str]) -> list[str]:
    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique


def _build_report_evidence_audit(
    expanded_evidence: ExpandedReportEvidence,
    knowledge_activation: KnowledgeActivationSummary,
) -> ReportEvidenceAudit:
    calculation_statuses = [
        assumption.removeprefix("calculation_status:")
        for conclusion in expanded_evidence.formal_conclusions
        for assumption in conclusion.trace.assumptions
        if assumption.startswith("calculation_status:")
    ]
    conclusion_rule_families = [
        conclusion.rule_family
        for conclusion in expanded_evidence.formal_conclusions
        if conclusion.strength != "unavailable"
    ]
    traced_evidence_ids = _unique_preserving_order(
        [
            evidence_id
            for conclusion in expanded_evidence.formal_conclusions
            for evidence_id in conclusion.trace.evidence_ids
        ]
    )
    missing_rule_families = [
        rule_family
        for rule_family in knowledge_activation.enabled_rule_families
        if rule_family not in conclusion_rule_families
    ]
    missing_rule_families.extend(
        rule_family
        for rule_family in knowledge_activation.missing_rule_families
        if rule_family not in missing_rule_families
    )
    if missing_rule_families or expanded_evidence.unavailable_conclusions:
        audit_status = "incomplete"
    elif knowledge_activation.activation_status == "enabled_with_guardrails":
        audit_status = "complete_with_guardrails"
    else:
        audit_status = "complete"

    return ReportEvidenceAudit(
        audit_status=audit_status,
        rule_family_count=len(knowledge_activation.enabled_rule_families),
        formal_conclusion_count=len(expanded_evidence.formal_conclusions),
        traced_evidence_unit_count=len(traced_evidence_ids),
        enabled_rule_families=knowledge_activation.enabled_rule_families,
        conclusion_rule_families=conclusion_rule_families,
        missing_rule_families=missing_rule_families,
        open_conflicts=knowledge_activation.open_conflicts,
        guardrail_count=len(knowledge_activation.guardrails)
        + len(knowledge_activation.open_conflicts),
        unavailable_conclusion_count=len(expanded_evidence.unavailable_conclusions),
        computed_rule_family_count=calculation_statuses.count("computed"),
        indeterminate_rule_family_count=calculation_statuses.count("indeterminate"),
        disputed_rule_family_count=calculation_statuses.count("disputed"),
        not_computed_rule_family_count=calculation_statuses.count("not_computed"),
    )


def _format_report_evidence_audit_notes(
    report_evidence_audit: ReportEvidenceAudit,
    expanded_evidence: ExpandedReportEvidence,
) -> str:
    lines = [
        (
            "- Report evidence audit: "
            f"status={report_evidence_audit.audit_status}, "
            f"rule_families={report_evidence_audit.rule_family_count}, "
            f"formal_conclusions={report_evidence_audit.formal_conclusion_count}, "
            f"traced_evidence_units={report_evidence_audit.traced_evidence_unit_count}, "
            f"unavailable_conclusions={report_evidence_audit.unavailable_conclusion_count}"
        )
    ]
    for conclusion in expanded_evidence.formal_conclusions:
        sample_ids = conclusion.trace.evidence_ids[:3]
        sample_text = ",".join(sample_ids) if sample_ids else "none"
        lines.append(
            "- Report rule-family trace: "
            f"rule_family={conclusion.rule_family}, "
            f"strength={conclusion.strength}, "
            f"risk_tier={conclusion.risk_tier}, "
            f"evidence_count={len(conclusion.trace.evidence_ids)}, "
            f"sample_evidence_ids={sample_text}"
        )
    return "\n".join(lines)


def _format_expanded_evidence_notes(
    expanded_evidence: ExpandedReportEvidence,
    knowledge_activation: KnowledgeActivationSummary | None = None,
    report_evidence_audit: ReportEvidenceAudit | None = None,
) -> str:
    lines = [
        "- 命理依据：正式判断来自已审核的经典证据单元，并保留规则家族、结论强度和盘面信号。",
    ]
    if knowledge_activation is not None:
        lines.append(_format_knowledge_activation_notes(knowledge_activation))
    if report_evidence_audit is not None:
        lines.append(
            _format_report_evidence_audit_notes(
                report_evidence_audit,
                expanded_evidence,
            )
        )
    if expanded_evidence.source_summary:
        lines.append("- 来源摘要：" + "；".join(expanded_evidence.source_summary))

    for conclusion in expanded_evidence.formal_conclusions:
        evidence_ids = "、".join(conclusion.trace.evidence_ids) or "暂无可用证据"
        chart_signals = format_reader_chart_signals(
            conclusion.rule_family,
            conclusion.trace.chart_signals,
        )
        lines.append(
            "- 正式判断："
            f"{conclusion.title}｜{conclusion.rule_family}｜{conclusion.strength}｜"
            f"证据：{evidence_ids}｜盘面：{chart_signals}"
        )
        if conclusion.trace.disagreement_note:
            lines.append(f"- 分歧说明：{conclusion.trace.disagreement_note}")

    if expanded_evidence.high_risk_notes:
        lines.append("- 高风险材料边界：相关材料只作为传统风险信号，不输出精确结果或专业建议。")
    if expanded_evidence.unavailable_conclusions:
        lines.append(
            "- 不足项："
            + "；".join(expanded_evidence.unavailable_conclusions)
            + " 当前证据不足，保留为不可用或待核。"
        )
    return "\n".join(lines)


def _build_evidence_notes(
    expanded_evidence: ExpandedReportEvidence,
    knowledge_activation: KnowledgeActivationSummary,
    report_evidence_audit: ReportEvidenceAudit,
) -> str:
    return "\n".join(
        [
            "- 来源依据：先看排盘来源与历法、时区、节气等假设，避免把前提当成结论。",
            "- 四柱依据：年柱、月柱、日柱、时柱只提供结构位置和组合线索，不单独断事。",
            "- 五行依据：明面信号、藏干信号和合计信号用于观察分布，不用于给人生下定论。",
            "- 十神依据：十神关系按柱位理解为关系线索，需要结合解读边界一起阅读。",
            "- 行动依据：行动反思只把可观察线索转成复盘问题，不预测具体结果。",
            _format_expanded_evidence_notes(
                expanded_evidence,
                knowledge_activation,
                report_evidence_audit,
            ),
        ]
    )


FORMAL_SYNTHESIS_RULE_GROUPS = (
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
    ("时机与风险", ("luck_cycle", "high_risk_signal")),
)

FORMAL_SYNTHESIS_RULE_TITLES = {
    "pattern_strength": "格局与旺衰候选",
    "five_element_balance": "五行强弱倾向",
    "ten_god_relation": "十神组合关系",
    "branch_interaction": "刑冲合害线索",
    "blind_image_method": "盲派象法取象",
    "useful_god_candidate": "用神候选边界",
    "taboo_god_candidate": "忌神候选边界",
    "remedy_boundary": "趋避调整边界",
    "luck_cycle": "大运流年主题",
    "high_risk_signal": "高风险信号边界",
}

FORMAL_SYNTHESIS_STRENGTH_LABELS = {
    "decided": "已定",
    "candidate": "候选",
    "weakly_supported": "弱支持",
    "disputed": "有分歧",
    "unavailable": "不可用",
}

FORMAL_SYNTHESIS_AUDIT_STATUS_LABELS = {
    "complete": "完整",
    "complete_with_guardrails": "完整（含护栏）",
    "incomplete": "不完整",
}

READER_SIGNAL_PLACEHOLDERS = frozenset(
    {"", "unknown", "unspecified", "none", "null"}
)
READER_SIGNAL_PILLAR_LABELS = {
    "year": "年柱",
    "month": "月柱",
    "day": "日柱",
    "hour": "时柱",
    "年柱": "年柱",
    "月柱": "月柱",
    "日柱": "日柱",
    "时柱": "时柱",
}
READER_SIGNAL_SPECIAL_LABELS = {
    "traditional_high_risk_signal_boundary": (
        "传统高风险信号边界（仅作条件观察）"
    ),
}
def _reader_signal_text(signal: str) -> str:
    text = signal.strip()
    if text.lower() in READER_SIGNAL_PLACEHOLDERS:
        return ""
    if text in READER_SIGNAL_SPECIAL_LABELS:
        return READER_SIGNAL_SPECIAL_LABELS[text]

    separator = ":" if ":" in text else "：" if "：" in text else ""
    if separator:
        prefix, value = text.split(separator, 1)
        normalized_prefix = prefix.strip()
        normalized_value = value.strip()
        if normalized_value.lower() in READER_SIGNAL_PLACEHOLDERS:
            return ""
        if normalized_prefix == "focus_topic":
            return ""
        if normalized_prefix == "stage_signal":
            return normalized_value
        pillar_label = READER_SIGNAL_PILLAR_LABELS.get(normalized_prefix)
        if pillar_label and normalized_value:
            return f"{pillar_label}：{normalized_value}"
    return text


def format_reader_chart_signals(
    rule_family: str,
    signals: list[str],
) -> str:
    candidates = signals
    if rule_family == "high_risk_signal":
        candidates = [
            signal
            for signal in signals
            if signal == "traditional_high_risk_signal_boundary"
            or signal.startswith("stage_signal:")
        ]

    formatted: list[str] = []
    for signal in candidates:
        text = _reader_signal_text(signal)
        if text and text not in formatted:
            formatted.append(text)
        if len(formatted) == 5:
            break

    if not formatted:
        return "当前未形成可用盘面信号"
    return "、".join(formatted)


def build_formal_synthesis(
    expanded_evidence: ExpandedReportEvidence,
    report_evidence_audit: ReportEvidenceAudit,
) -> str:
    conclusions_by_family = {
        conclusion.rule_family: conclusion
        for conclusion in expanded_evidence.formal_conclusions
    }
    unavailable = set(expanded_evidence.unavailable_conclusions)
    audit_label = FORMAL_SYNTHESIS_AUDIT_STATUS_LABELS.get(
        report_evidence_audit.audit_status,
        report_evidence_audit.audit_status,
    )
    lines = [
        "正式综合",
        (
            f"证据审计：{audit_label}；规则家族数："
            f"{report_evidence_audit.rule_family_count}；正式结论数："
            f"{report_evidence_audit.formal_conclusion_count}；追溯证据数："
            f"{report_evidence_audit.traced_evidence_unit_count}。"
        ),
    ]

    for group_title, rule_families in FORMAL_SYNTHESIS_RULE_GROUPS:
        lines.extend(["", group_title])
        for rule_family in rule_families:
            conclusion = conclusions_by_family.get(rule_family)
            if conclusion is None:
                unavailable_tokens = {
                    rule_family,
                    FORMAL_SYNTHESIS_RULE_TITLES[rule_family],
                }
                state = (
                    "不可用"
                    if unavailable_tokens & unavailable
                    else "缺失"
                )
                lines.append(
                    f"- rule_family={rule_family}｜"
                    f"{FORMAL_SYNTHESIS_RULE_TITLES[rule_family]}｜强度：不可用｜"
                    f"证据数：0｜{state}：当前没有可用的正式结论。"
                )
                continue

            strength_label = FORMAL_SYNTHESIS_STRENGTH_LABELS.get(
                conclusion.strength,
                conclusion.strength,
            )
            chart_signals = format_reader_chart_signals(
                conclusion.rule_family,
                conclusion.trace.chart_signals,
            )
            lines.append(
                f"- rule_family={rule_family}｜{conclusion.title}｜"
                f"强度：{strength_label}｜"
                f"证据数：{len(conclusion.trace.evidence_ids)}｜"
                f"盘面信号：{chart_signals}｜{conclusion.body}"
            )
            if conclusion.trace.disagreement_note:
                lines.append(f"  分歧说明：{conclusion.trace.disagreement_note}")

        if group_title == "时机与风险":
            lines.append(
                "边界：本组内容只表示非确定性的传统观察，不预测精确事件或寿命，"
                "也不替代医疗、法律、心理、投资等专业建议。"
            )

    return "\n".join(lines)


_build_formal_synthesis = build_formal_synthesis


INTEGRATED_SYNTHESIS_FAMILY_ORDER = (
    "pattern_strength",
    "five_element_balance",
    "ten_god_relation",
    "branch_interaction",
    "blind_image_method",
    "useful_god_candidate",
    "taboo_god_candidate",
    "remedy_boundary",
    "luck_cycle",
    "high_risk_signal",
)


def _integrated_conclusion_text(
    conclusion: FormalConclusion | None,
    rule_family: str,
) -> str:
    title = FORMAL_SYNTHESIS_RULE_TITLES[rule_family]
    if conclusion is None:
        return f"{title}（不可用）"
    strength = FORMAL_SYNTHESIS_STRENGTH_LABELS.get(
        conclusion.strength,
        conclusion.strength,
    )
    signals = format_reader_chart_signals(
        conclusion.rule_family,
        conclusion.trace.chart_signals,
    )
    signal_excerpt = signals.split("、", 1)[0]
    return f"{conclusion.title}（{strength}；{signal_excerpt}）"


def build_integrated_synthesis(
    expanded_evidence: ExpandedReportEvidence,
    report_evidence_audit: ReportEvidenceAudit,
) -> str:
    conclusions = {
        conclusion.rule_family: conclusion
        for conclusion in expanded_evidence.formal_conclusions
    }

    def item(rule_family: str) -> str:
        return _integrated_conclusion_text(
            conclusions.get(rule_family),
            rule_family,
        )

    status_label = FORMAL_SYNTHESIS_AUDIT_STATUS_LABELS.get(
        report_evidence_audit.audit_status,
        report_evidence_audit.audit_status,
    )
    structure_items = "、".join(
        item(rule_family)
        for rule_family in (
            "pattern_strength",
            "five_element_balance",
            "ten_god_relation",
            "branch_interaction",
            "blind_image_method",
        )
    )
    selection_items = "、".join(
        item(rule_family)
        for rule_family in (
            "five_element_balance",
            "useful_god_candidate",
            "taboo_god_candidate",
            "remedy_boundary",
        )
    )
    timing_items = "、".join(
        item(rule_family)
        for rule_family in (
            "pattern_strength",
            "branch_interaction",
            "luck_cycle",
            "high_risk_signal",
        )
    )
    disputed = [
        conclusion
        for conclusion in expanded_evidence.formal_conclusions
        if conclusion.strength == "disputed"
    ]
    if disputed:
        disagreement_text = "；".join(
            (
                f"{conclusion.title}："
                f"{conclusion.trace.disagreement_note or '保留分歧候选，不作唯一裁决。'}"
            )
            for conclusion in disputed
        )
    else:
        disagreement_text = "当前没有标记为有分歧的正式结论。"

    missing_families = set(report_evidence_audit.missing_rule_families)
    missing_families.update(
        rule_family
        for rule_family in INTEGRATED_SYNTHESIS_FAMILY_ORDER
        if rule_family not in conclusions
    )
    missing_families.update(
        conclusion.rule_family
        for conclusion in expanded_evidence.formal_conclusions
        if conclusion.strength == "unavailable"
    )
    unavailable_titles = set(expanded_evidence.unavailable_conclusions)
    unavailable_labels = [
        FORMAL_SYNTHESIS_RULE_TITLES[rule_family]
        for rule_family in INTEGRATED_SYNTHESIS_FAMILY_ORDER
        if rule_family in missing_families
        or FORMAL_SYNTHESIS_RULE_TITLES[rule_family] in unavailable_titles
    ]
    if unavailable_labels:
        unavailable_text = (
            "不可用边界："
            + "、".join(unavailable_labels)
            + "。完整综合链暂不成立，相关部分保持不可用或待核。"
        )
    else:
        unavailable_text = "不可用边界：无。当前十类正式结论均可进入综合阅读。"

    lines = [
        (
            f"综合状态：{status_label}。本层只协调已审核结论的阅读关系，"
            "不新增命理判断。"
        ),
        (
            f"结构主线（支持关系）：{structure_items}。"
            "这些结论共同提供当前结构阅读上下文，不单独决定现实结果。"
        ),
        (
            f"取用衔接（条件制约）：{selection_items}。"
            "取用与调整必须回到结构和平衡条件，保留候选，不指定唯一五行或承诺效果。"
        ),
        (
            f"阶段衔接（条件制约）：{timing_items}。"
            "阶段主题必须结合原局结构与地支条件复核；高风险与趋避只构成护栏关系，"
            "不预测精确事件或寿命，也不替代专业建议。"
        ),
        f"分歧协调：{disagreement_text}",
        unavailable_text,
    ]
    return "\n".join(lines)


ACTION_REFLECTION_TRACKS = (
    (
        "structure_calibration",
        "结构校准",
        ("pattern_strength", "five_element_balance"),
        "把当前结构信号放回一个可观察场景，记录哪些表现吻合、哪些不吻合。",
        "记录场景、原先预期、实际结果和一条反例，下一次复盘时比较变化。",
        "若盘面前提或现实场景无法核对，就停止据此延伸判断。",
        False,
    ),
    (
        "relationship_process_review",
        "关系过程复盘",
        ("ten_god_relation", "branch_interaction", "blind_image_method"),
        "选择一次真实互动，只记录沟通顺序、角色分工和可见反应，不评价他人本质。",
        "记录一次具体互动、自己的做法、对方可见回应和可调整的一步。",
        "若只能依靠猜测他人动机或给关系定性，就停止使用本项。",
        False,
    ),
    (
        "selection_experiment",
        "取用小实验",
        ("useful_god_candidate", "taboo_god_candidate", "remedy_boundary"),
        "只选择一个低成本、可逆的小调整，先写清观察期限，不把候选五行当成唯一答案。",
        "记录调整前基线、执行频率、现实反馈和无效或相反反馈。",
        "不购买或依赖所谓改运方案；出现成本、压力或效果承诺时立即停止。",
        True,
    ),
    (
        "stage_review",
        "阶段复盘",
        ("luck_cycle", "high_risk_signal"),
        "把阶段主题写成待核问题，只核对已经发生的趋势，不预测精确事件或寿命。",
        "按固定周期记录现实事件、影响程度、其他可能原因和仍不确定之处。",
        "涉及医疗、法律、心理、财务或寿命问题时停止命理解读并寻求专业支持。",
        True,
    ),
)


def build_action_reflection_items(
    expanded_evidence: ExpandedReportEvidence,
) -> list[ActionReflectionItem]:
    conclusions = {
        conclusion.rule_family: conclusion
        for conclusion in expanded_evidence.formal_conclusions
    }
    explicitly_unavailable = set(expanded_evidence.unavailable_conclusions)

    def is_unavailable(conclusion: FormalConclusion | None) -> bool:
        return conclusion is None or bool(
            {conclusion.rule_family, conclusion.title} & explicitly_unavailable
        )

    items: list[ActionReflectionItem] = []

    for (
        action_id,
        title,
        rule_families,
        observation_prompt,
        feedback_metric,
        stop_boundary,
        guarded,
    ) in ACTION_REFLECTION_TRACKS:
        track_conclusions = [conclusions.get(family) for family in rule_families]
        available = all(
            not is_unavailable(conclusion)
            and conclusion is not None
            and conclusion.strength != "unavailable"
            and bool(conclusion.trace.evidence_ids)
            for conclusion in track_conclusions
        )
        if not available:
            missing = [
                FORMAL_SYNTHESIS_RULE_TITLES[family]
                for family, conclusion in zip(
                    rule_families,
                    track_conclusions,
                    strict=True,
                )
                if is_unavailable(conclusion)
                or conclusion is None
                or conclusion.strength == "unavailable"
                or not conclusion.trace.evidence_ids
            ]
            items.append(
                ActionReflectionItem(
                    action_id=action_id,
                    title=title,
                    status="unavailable",
                    rule_families=list(rule_families),
                    evidence_ids=[],
                    conditions=["缺少可用结论或证据：" + "、".join(missing)],
                    observation_prompt="当前证据不足，暂不执行本项行动反思。",
                    feedback_metric="等待证据恢复后重新生成，再开始记录反馈。",
                    stop_boundary="证据不足时不开始行动实验，也不根据缺口补作推断。",
                )
            )
            continue

        typed_conclusions = [
            conclusion
            for conclusion in track_conclusions
            if conclusion is not None
        ]
        evidence_ids: list[str] = []
        conditions: list[str] = []
        for conclusion in typed_conclusions:
            for evidence_id in conclusion.trace.evidence_ids:
                if evidence_id not in evidence_ids:
                    evidence_ids.append(evidence_id)
            conditions.append(
                f"{FORMAL_SYNTHESIS_RULE_TITLES[conclusion.rule_family]}："
                f"{format_reader_chart_signals(conclusion.rule_family, conclusion.trace.chart_signals)}"
            )
            if conclusion.trace.disagreement_note:
                conditions.append(
                    f"分歧说明：{conclusion.trace.disagreement_note}"
                )

        has_guarded_strength = any(
            conclusion.strength in {"weakly_supported", "disputed"}
            for conclusion in typed_conclusions
        )
        items.append(
            ActionReflectionItem(
                action_id=action_id,
                title=title,
                status=(
                    "ready_with_guardrails"
                    if guarded or has_guarded_strength
                    else "ready"
                ),
                rule_families=list(rule_families),
                evidence_ids=evidence_ids,
                conditions=conditions,
                observation_prompt=observation_prompt,
                feedback_metric=feedback_metric,
                stop_boundary=stop_boundary,
            )
        )

    return items


ACTION_REFLECTION_STATUS_LABELS = {
    "ready": "可复盘",
    "ready_with_guardrails": "可复盘（含护栏）",
    "unavailable": "不可用",
}


def render_action_reflection_items(
    items: list[ActionReflectionItem],
    focus_topic: str,
) -> str:
    lines = [
        f"围绕{focus_topic}，以下行动反思仅用于整理可观察线索和现实反馈。"
    ]
    for item in items:
        status = ACTION_REFLECTION_STATUS_LABELS.get(item.status, item.status)
        lines.extend(
            [
                "",
                (
                    f"{item.title}｜状态：{status}｜"
                    "规则族："
                    + "、".join(
                        FORMAL_SYNTHESIS_RULE_TITLES[family]
                        for family in item.rule_families
                    )
                    + "｜"
                    f"证据数：{len(item.evidence_ids)}"
                ),
                "适用条件：" + "；".join(item.conditions),
                f"观察问题：{item.observation_prompt}",
                f"反馈记录：{item.feedback_metric}",
                f"停止边界：{item.stop_boundary}",
            ]
        )
    lines.extend(
        [
            "",
            "这些内容是观察和整理方向，不替代现实判断，也不是对结果的承诺。",
        ]
    )
    return "\n".join(lines)


def _ensure_knowledge_activation_ready(
    knowledge_activation: KnowledgeActivationSummary,
) -> None:
    if knowledge_activation.activation_status in REPORT_ENABLED_ACTIVATION_STATUSES:
        return
    raise KnowledgeActivationError(
        "knowledge activation is not enabled: "
        f"{knowledge_activation.activation_status}; "
        f"next_action={knowledge_activation.next_action}"
    )


def _major_body_sections(report: Report) -> str:
    return "\n\n".join(
        [
            report.disclaimer,
            report.quick_guide,
            report.chart_card,
            report.assumptions,
            report.four_pillars_summary,
            report.five_elements_summary,
            report.ten_gods_summary,
            report.evidence_notes,
            report.formal_synthesis,
            report.integrated_synthesis,
            report.structure_analysis,
            report.personality_tendencies,
            report.strengths_and_issues,
            report.phase_overview,
            report.action_suggestions,
            report.interpretation_boundaries,
            report.glossary,
            report.ethics_reminder,
        ]
    )


def _default_not_computed_calculation(chart: BaziChart) -> CalculationBundle:
    try:
        return build_legacy_not_computed_bundle(chart)
    except ValueError:
        compatible_chart = calculate_bazi_chart(chart.birth_profile)
        return build_legacy_not_computed_bundle(compatible_chart)


def build_report(
    chart: BaziChart,
    calculation: CalculationBundle | None = None,
) -> Report:
    if len(chart.pillars) != 4:
        raise ValueError("BaziChart must contain exactly four pillars")
    supplied_calculation = calculation
    calculation = calculation or _default_not_computed_calculation(chart)
    if supplied_calculation is not None:
        _require_calculation_bundle_binding(chart, calculation)

    disclaimer = (
        "本报告定位为传统命理知识的文化解读与自我反思材料，不是科学预测，"
        "也不替代医疗、法律、心理、投资等专业建议。请把内容作为观察语言与提问线索，"
        "而非对人生结果的断言。"
    )
    chart_card = _build_chart_card(chart)
    assumptions = f"{_build_assumptions(chart)}\n{SOURCE_BASIS_TRANSITION}"
    four_pillars_summary = _build_four_pillars_summary(chart)
    interpretation = build_basic_interpretation(chart)
    quick_guide = _build_quick_guide(chart, interpretation)
    five_elements_summary = interpretation.five_elements_summary
    ten_gods_summary = interpretation.ten_gods_summary
    sources = load_classical_sources()
    evidence_units = load_approved_evidence_units()
    source_conflicts = load_source_conflicts()
    knowledge_activation = build_knowledge_activation_summary(
        sources,
        evidence_units,
        source_conflicts,
    )
    _ensure_knowledge_activation_ready(knowledge_activation)
    expanded_evidence = build_formal_interpretation(
        chart,
        evidence_units,
        source_conflicts,
        calculation,
    )
    report_evidence_audit = _build_report_evidence_audit(
        expanded_evidence,
        knowledge_activation,
    )
    evidence_notes = _build_evidence_notes(
        expanded_evidence,
        knowledge_activation,
        report_evidence_audit,
    )
    formal_synthesis = build_formal_synthesis(
        expanded_evidence,
        report_evidence_audit,
    )
    integrated_synthesis = build_integrated_synthesis(
        expanded_evidence,
        report_evidence_audit,
    )
    structure_analysis = (
        f"{interpretation.structure_observations}\n{STRUCTURE_BOUNDARY_TRANSITION}"
    )
    personality_tendencies = interpretation.day_master_summary
    strengths_and_issues = _normalize_focus_topic_text(
        interpretation.focus_suggestions,
        chart.birth_profile.focus_topic,
    )
    strengths_and_issues = f"{ACTION_REFLECTION_TRANSITION}\n{strengths_and_issues}"
    interpretation_boundaries = (
        f"{interpretation.limitations}\n{BOUNDARY_ACTION_TRANSITION}"
    )
    phase_boundary = (
        "当前基础结构解读层不做大运流年判断。"
        if "不做大运流年判断" in interpretation.limitations
        else "当前基础结构解读层保留阶段判断边界。"
    )
    focus_topic = _focus_topic_label(chart.birth_profile.focus_topic)
    phase_overview = (
        f"{chart.luck_cycle_summary} 阶段概览只描述可反思的主题变化，"
        f"不推断具体事件结果。{phase_boundary}"
    )
    action_reflection_items = build_action_reflection_items(expanded_evidence)
    action_suggestions = render_action_reflection_items(
        action_reflection_items,
        focus_topic,
    )
    glossary = (
        "日主：以出生日天干作为观察中心。十神：传统命理中描述关系与功能的术语。"
        "用神候选：在特定结构理解下可作为平衡线索的五行候选。"
    )
    ethics_reminder = (
        "命理报告不应制造恐惧、歧视或依赖，也不应替代专业判断。"
        "当内容涉及健康、法律、心理或财务风险时，请优先寻求合格专业支持。"
    )

    draft_report = Report(
        title="八字结构化报告",
        disclaimer=disclaimer,
        quick_guide=quick_guide,
        chart_card=chart_card,
        assumptions=assumptions,
        four_pillars_summary=four_pillars_summary,
        five_elements_summary=five_elements_summary,
        ten_gods_summary=ten_gods_summary,
        evidence_notes=evidence_notes,
        formal_synthesis=formal_synthesis,
        integrated_synthesis=integrated_synthesis,
        structure_analysis=structure_analysis,
        personality_tendencies=personality_tendencies,
        strengths_and_issues=strengths_and_issues,
        phase_overview=phase_overview,
        action_reflection_items=action_reflection_items,
        action_suggestions=action_suggestions,
        interpretation_boundaries=interpretation_boundaries,
        glossary=glossary,
        ethics_reminder=ethics_reminder,
        report_evidence_audit=report_evidence_audit,
        knowledge_activation=knowledge_activation,
        expanded_evidence=expanded_evidence,
        safety_review=safety_check(
            "\n\n".join(
                [
                    disclaimer,
                    quick_guide,
                    chart_card,
                    assumptions,
                    four_pillars_summary,
                    five_elements_summary,
                    ten_gods_summary,
                    evidence_notes,
                    formal_synthesis,
                    integrated_synthesis,
                    structure_analysis,
                    personality_tendencies,
                    strengths_and_issues,
                    phase_overview,
                    action_suggestions,
                    interpretation_boundaries,
                    glossary,
                    ethics_reminder,
                ]
            ),
            disclaimer_present=True,
        ),
    )
    body_review = safety_check(_major_body_sections(draft_report), disclaimer_present=True)
    focus_topic_review = _review_focus_topic(chart.birth_profile.focus_topic)
    final_review = _merge_safety_reviews(
        body_review,
        focus_topic_review,
        disclaimer_present=True,
    )
    return replace(draft_report, safety_review=final_review)
