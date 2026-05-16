from dataclasses import replace

from mingli_engine.models import BaziChart, Report, SafetyReviewResult
from mingli_engine.safety import safety_check


LIFESPAN_FOCUS_TOPICS = frozenset({"寿命"})


def _format_true_solar_time(value: bool | None) -> str:
    if value is True:
        return "已应用"
    if value is False:
        return "未应用"
    return "未说明"


def _format_list(values: list[str]) -> str:
    if not values:
        return "暂无明确候选"
    return "、".join(values)


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
    return "\n".join(
        [
            f"- 历法类型：{profile.calendar_type}",
            f"- 出生日期：{profile.birth_date}",
            f"- 出生时间：{profile.birth_time}",
            f"- 出生地点：{profile.birthplace}",
            f"- 性别标记：{profile.gender}",
            f"- 关注主题：{profile.focus_topic}",
            f"- 日主：{chart.day_master}",
        ]
    )


def _build_assumptions(chart: BaziChart) -> str:
    source = chart.chart_source
    return "\n".join(
        [
            f"- 来源类型：{source.source_type}",
            f"- 来源说明：{source.source_note}",
            f"- 历法假设：{source.calendar_assumption}",
            f"- 时区假设：{source.timezone_assumption}",
            f"- 节气假设：{source.solar_terms_assumption}",
            f"- 真太阳时：{_format_true_solar_time(source.true_solar_time_applied)}",
            f"- 可信度：{source.confidence}",
        ]
    )


def _build_four_pillars_summary(chart: BaziChart) -> str:
    rows = []
    for pillar in chart.pillars:
        hidden_stems = "、".join(pillar.hidden_stems) if pillar.hidden_stems else "无"
        rows.append(
            f"- {pillar.name}：{pillar.heavenly_stem}{pillar.earthly_branch}，"
            f"藏干：{hidden_stems}，十神：{pillar.ten_god}，五行：{pillar.element}"
        )
    return "\n".join(rows)


def _build_five_elements_summary(chart: BaziChart) -> str:
    return "\n".join(
        f"- {element}：{description}"
        for element, description in chart.five_elements_summary.items()
    )


def _build_structure_analysis(chart: BaziChart) -> str:
    pattern_candidates = _format_list(chart.pattern_candidates)
    useful_god_candidates = _format_list(chart.useful_god_candidates)
    return (
        f"以{chart.day_master}为观察中心，强弱评估为：{chart.strength_assessment}。"
        f"结构上可记录的格局候选包括：{pattern_candidates}；"
        f"用神候选包括：{useful_god_candidates}。这些判断属于传统命理框架下的倾向性整理，"
        "需要结合排盘来源、历法假设与个人现实处境理解。"
    )


def _major_body_sections(report: Report) -> str:
    return "\n\n".join(
        [
            report.disclaimer,
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
            report.glossary,
            report.ethics_reminder,
        ]
    )


def build_report(chart: BaziChart) -> Report:
    disclaimer = (
        "本报告定位为传统命理知识的文化解读与自我反思材料，不是科学预测，"
        "也不替代医疗、法律、心理、投资等专业建议。请把内容作为观察语言与提问线索，"
        "而非对人生结果的断言。"
    )
    chart_card = _build_chart_card(chart)
    assumptions = _build_assumptions(chart)
    four_pillars_summary = _build_four_pillars_summary(chart)
    five_elements_summary = _build_five_elements_summary(chart)
    ten_gods_summary = (
        f"{chart.ten_gods_summary} 十神信息宜用于观察关系、资源与行动风格的倾向，"
        "不作为固定标签。"
    )
    structure_analysis = _build_structure_analysis(chart)
    personality_tendencies = (
        "性格倾向可从日主、十神与五行分布交叉观察：此盘更适合以弹性、学习力、"
        "边界感和执行节奏作为自我反思关键词。"
    )
    strengths_and_issues = (
        "优势可关注资源整合、理解复杂信息与持续学习；议题可关注计划落地、压力管理、"
        "表达边界与长期节奏。"
    )
    phase_overview = (
        f"{chart.luck_cycle_summary} 阶段概览只描述可反思的主题变化，"
        "不推断具体事件结果。"
    )
    action_suggestions = (
        "建议把关注主题拆成可执行的小步骤：记录现实证据、区分情绪与事实、"
        "为重要决定咨询相应专业人士，并定期复盘行动反馈。"
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
        glossary=glossary,
        ethics_reminder=ethics_reminder,
        safety_review=safety_check(
            "\n\n".join(
                [
                    disclaimer,
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
