from dataclasses import replace

from mingli_engine.interpretation import build_basic_interpretation
from mingli_engine.models import BaziChart, Report, SafetyReviewResult
from mingli_engine.safety import safety_check


LIFESPAN_FOCUS_TOPICS = frozenset({"寿命"})
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
    if focus_topic.strip() not in LIFESPAN_FOCUS_TOPICS:
        return review

    lifespan_review = SafetyReviewResult(
        allowed=False,
        red_line_categories=["lifespan_or_death_timing"],
        disclaimer_present=True,
        redirect_message="不预测寿命或死亡时间。可改为讨论风险意识、身心节律与生活安排。",
    )
    return _merge_safety_reviews(review, lifespan_review, disclaimer_present=True)


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


def build_report(chart: BaziChart) -> Report:
    if len(chart.pillars) != 4:
        raise ValueError("BaziChart must contain exactly four pillars")

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
    dominant_elements = interpretation.element_distribution.dominant_elements
    missing_elements = interpretation.element_distribution.missing_elements
    if dominant_elements:
        action_focus = f"{'、'.join(dominant_elements)}等较集中的结构信号"
    elif missing_elements:
        action_focus = "暂未形成可计数信号的结构边界"
    else:
        action_focus = "当前结构观察"
    phase_overview = (
        f"{chart.luck_cycle_summary} 阶段概览只描述可反思的主题变化，"
        f"不推断具体事件结果。{phase_boundary}"
    )
    action_suggestions = (
        f"围绕{focus_topic}，可以先承接{action_focus}，整理成一两个可记录的小步骤，"
        "再用现实反馈慢慢复盘。这里给的是观察和整理方向，不是对结果的承诺。"
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
        structure_analysis=structure_analysis,
        personality_tendencies=personality_tendencies,
        strengths_and_issues=strengths_and_issues,
        phase_overview=phase_overview,
        action_suggestions=action_suggestions,
        interpretation_boundaries=interpretation_boundaries,
        glossary=glossary,
        ethics_reminder=ethics_reminder,
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
