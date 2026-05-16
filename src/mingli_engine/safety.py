from dataclasses import dataclass

from mingli_engine.models import SafetyReviewResult


PROHIBITED_PHRASES = ("必定", "注定", "一定会", "死定")
SAFE_CONTEXT_MARKERS = (
    "不保证",
    "不一定",
    "不是",
    "并非",
    "避免",
    "不应",
    "不能",
    "禁止",
    "不预测",
)


@dataclass(frozen=True)
class RedLineRule:
    patterns: tuple[str, ...]
    redirect_message: str


RED_LINE_RULES: dict[str, RedLineRule] = {
    "lifespan_or_death_timing": RedLineRule(
        patterns=(
            "哪年会死",
            "几岁去世",
            "几岁会死",
            "死亡时间",
            "什么时候会死",
            "能活到几岁",
            "看寿命",
            "算寿命",
            "预测寿命",
            "寿命多长",
            "死期",
        ),
        redirect_message=(
            "不预测寿命或死亡时间。可以改为讨论风险意识、身心节律与生活安排，"
            "帮助你用更稳妥的方式照顾当下。"
        ),
    ),
    "major_disaster_prediction": RedLineRule(
        patterns=(
            "会不会出车祸",
            "会出车祸吗",
            "会不会有大灾",
            "会不会有灾祸",
            "重大灾祸",
            "血光之灾",
            "牢狱之灾",
        ),
        redirect_message=(
            "不预测重大灾祸。可以改为讨论安全意识、风险排查和现实中的预防行动。"
        ),
    ),
    "deterministic_marriage_matching": RedLineRule(
        patterns=(
            "命中注定结婚",
            "注定结婚",
            "必定结婚",
            "一定会结婚",
            "一定离婚",
            "必定离婚",
            "婚配定论",
        ),
        redirect_message=(
            "不做婚配定论。可以改为讨论相处模式、沟通议题和需要双方共同确认的现实条件。"
        ),
    ),
    "professional_advice": RedLineRule(
        patterns=(
            "投资建议",
            "买哪只股票",
            "诊断",
            "治疗方案",
            "官司会赢",
            "官司能赢",
            "心理治疗",
            "法律建议",
            "医疗建议",
        ),
        redirect_message=(
            "不提供医疗、法律、心理或投资等专业建议。相关决定请咨询合格专业人士。"
        ),
    ),
    "unauthorized_third_party": RedLineRule(
        patterns=(
            "看他的完整八字命盘",
            "看她的完整八字命盘",
            "看对方的完整八字命盘",
            "他的完整八字命盘",
            "她的完整八字命盘",
            "他没有同意",
            "她没有同意",
            "对方没有同意",
            "没有本人同意",
            "未经同意",
            "偷偷看",
        ),
        redirect_message=(
            "不解读未授权第三方的完整命盘。可以改为分析你自己的感受、边界和沟通选择。"
        ),
    ),
    "paid_remedy": RedLineRule(
        patterns=(
            "买法器",
            "买法物",
            "做法事",
            "付费化解",
            "花钱化解",
            "卖法器",
            "改运物品",
        ),
        redirect_message=(
            "不引导付费化解、法事或物品销售。可以改为讨论现实可执行的行动计划。"
        ),
    ),
}


def _is_safe_context(text: str, start_index: int) -> bool:
    context_start = max(0, start_index - 8)
    context_end = min(len(text), start_index + 8)
    nearby_context = text[context_start:context_end]
    for marker in SAFE_CONTEXT_MARKERS:
        marker_start = nearby_context.find(marker)
        while marker_start != -1:
            absolute_marker_start = context_start + marker_start
            is_polar_question = (
                marker == "不是"
                and absolute_marker_start > 0
                and text[absolute_marker_start - 1] == "是"
            )
            if not is_polar_question:
                return True
            marker_start = nearby_context.find(marker, marker_start + len(marker))

    return False


def _iter_match_starts(text: str, pattern: str):
    start_index = text.find(pattern)
    while start_index != -1:
        yield start_index
        start_index = text.find(pattern, start_index + len(pattern))


def _find_unsafe_phrases(text: str, phrases: tuple[str, ...]) -> list[str]:
    unsafe_phrases: list[str] = []

    for phrase in phrases:
        if any(
            not _is_safe_context(text, start_index)
            for start_index in _iter_match_starts(text, phrase)
        ):
            unsafe_phrases.append(phrase)

    return unsafe_phrases


def _matches_rule(text: str, rule: RedLineRule) -> bool:
    for pattern in rule.patterns:
        if any(
            not _is_safe_context(text, start_index)
            for start_index in _iter_match_starts(text, pattern)
        ):
            return True

    return False


def _has_lifespan_or_death_timing_request(text: str) -> bool:
    stripped_text = text.strip(" \t\r\n。！？?")
    if stripped_text == "寿命":
        return True

    return _matches_rule(text, RED_LINE_RULES["lifespan_or_death_timing"])


def safety_check(text: str, *, disclaimer_present: bool = False) -> SafetyReviewResult:
    prohibited_phrases = _find_unsafe_phrases(text, PROHIBITED_PHRASES)
    red_line_categories: list[str] = []
    redirect_messages: list[str] = []

    for category, rule in RED_LINE_RULES.items():
        matches = (
            _has_lifespan_or_death_timing_request(text)
            if category == "lifespan_or_death_timing"
            else _matches_rule(text, rule)
        )
        if matches:
            red_line_categories.append(category)
            redirect_messages.append(rule.redirect_message)

    return SafetyReviewResult(
        allowed=not red_line_categories and not prohibited_phrases,
        red_line_categories=red_line_categories,
        prohibited_phrases=prohibited_phrases,
        disclaimer_present=disclaimer_present,
        redirect_message="\n".join(redirect_messages),
    )
