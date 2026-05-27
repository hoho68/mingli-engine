from dataclasses import dataclass, field


@dataclass(frozen=True)
class HighRiskReviewResult:
    allowed: bool
    categories: list[str] = field(default_factory=list)
    risk_tier: str = "ordinary"
    requires_narrowing: bool = False
    report_note: str = ""
    redirect_message: str = ""


SAFE_CONTEXT_MARKERS = (
    "不预测",
    "不看",
    "不算",
    "不做",
    "不提供",
    "不输出",
    "不保证",
    "不承诺",
    "不要",
    "避免",
    "禁止",
    "并非",
    "不是",
)

REFUSAL_PATTERNS: dict[str, tuple[str, ...]] = {
    "lifespan_or_death_timing": (
        "哪年会死",
        "几岁去世",
        "几岁会死",
        "死亡时间",
        "什么时候会死",
        "能活到几岁",
        "算寿命",
        "预测寿命",
        "寿命多长",
        "死期",
    ),
    "major_disaster_prediction": (
        "会不会出车祸",
        "会出车祸吗",
        "会不会有大灾",
        "会不会有灾祸",
        "牢狱之灾会不会发生",
    ),
    "professional_advice": (
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
    "paid_remedy": (
        "买法器",
        "买法物",
        "做法事",
        "付费化解",
        "花钱化解",
        "卖法器",
        "改运物品",
    ),
}

GENERAL_HIGH_RISK_PATTERNS = (
    "寿命",
    "寿夭",
    "生死",
    "健康风险",
    "疾病风险",
    "灾厄",
    "灾祸",
    "事故信号",
    "车祸信号",
    "破财风险",
    "重大关系风险",
)

REFUSAL_MESSAGE = (
    "不提供精确寿命、死亡时间、诊断治疗、法律心理投资指令、"
    "强制匹配或付费化解承诺；可以改为传统高风险信号的条件化说明。"
)

NARROWING_NOTE = (
    "高风险材料边界：仅作为传统高风险信号分析，说明条件、证据与不确定性；"
    "不输出精确寿命、死亡时间、诊断治疗或保证结果。"
)


def _is_safe_context(text: str, start_index: int) -> bool:
    context_start = max(0, start_index - 10)
    context_end = min(len(text), start_index + 12)
    nearby_context = text[context_start:context_end]
    return any(marker in nearby_context for marker in SAFE_CONTEXT_MARKERS)


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    for pattern in patterns:
        start_index = text.find(pattern)
        while start_index != -1:
            if not _is_safe_context(text, start_index):
                return True
            start_index = text.find(pattern, start_index + len(pattern))
    return False


def _matched_refusal_categories(text: str) -> list[str]:
    categories: list[str] = []
    for category, patterns in REFUSAL_PATTERNS.items():
        if _matches_any(text, patterns):
            categories.append(category)
    return categories


def _has_general_high_risk_signal(text: str) -> bool:
    return _matches_any(text, GENERAL_HIGH_RISK_PATTERNS)


def classify_high_risk_request(text: str) -> HighRiskReviewResult:
    categories = _matched_refusal_categories(text)
    if categories:
        return HighRiskReviewResult(
            allowed=False,
            categories=categories,
            risk_tier="high_risk",
            requires_narrowing=False,
            report_note="",
            redirect_message=REFUSAL_MESSAGE,
        )

    if _has_general_high_risk_signal(text):
        return HighRiskReviewResult(
            allowed=True,
            categories=["traditional_high_risk_signal"],
            risk_tier="high_risk",
            requires_narrowing=True,
            report_note=NARROWING_NOTE,
            redirect_message="",
        )

    return HighRiskReviewResult(allowed=True)
