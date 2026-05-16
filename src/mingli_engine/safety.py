from mingli_engine.models import SafetyReviewResult


PROHIBITED_PHRASES = ("必定", "注定", "一定会", "死定")
LIFESPAN_OR_DEATH_TIMING_PATTERNS = (
    "什么时候会死",
    "能活到几岁",
    "寿命",
    "死期",
)

LIFESPAN_OR_DEATH_TIMING_REDIRECT = (
    "不预测寿命或死亡时间。可以改为讨论风险意识、身心节律与生活安排，"
    "帮助你用更稳妥的方式照顾当下。"
)


def safety_check(text: str, *, disclaimer_present: bool = False) -> SafetyReviewResult:
    prohibited_phrases = [
        phrase for phrase in PROHIBITED_PHRASES if phrase in text
    ]
    red_line_categories: list[str] = []
    redirect_message = ""

    if any(pattern in text for pattern in LIFESPAN_OR_DEATH_TIMING_PATTERNS):
        red_line_categories.append("lifespan_or_death_timing")
        redirect_message = LIFESPAN_OR_DEATH_TIMING_REDIRECT

    return SafetyReviewResult(
        allowed=not red_line_categories and not prohibited_phrases,
        red_line_categories=red_line_categories,
        prohibited_phrases=prohibited_phrases,
        disclaimer_present=disclaimer_present,
        redirect_message=redirect_message,
    )
