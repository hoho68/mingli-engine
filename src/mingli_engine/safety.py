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
LIFESPAN_OR_DEATH_TIMING_PATTERNS = (
    "什么时候会死",
    "能活到几岁",
    "看寿命",
    "算寿命",
    "预测寿命",
    "寿命多长",
    "死期",
)

LIFESPAN_OR_DEATH_TIMING_REDIRECT = (
    "不预测寿命或死亡时间。可以改为讨论风险意识、身心节律与生活安排，"
    "帮助你用更稳妥的方式照顾当下。"
)


def _is_safe_context(text: str, start_index: int) -> bool:
    context_start = max(0, start_index - 8)
    context_end = min(len(text), start_index + 8)
    nearby_context = text[context_start:context_end]
    return any(marker in nearby_context for marker in SAFE_CONTEXT_MARKERS)


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


def _has_lifespan_or_death_timing_request(text: str) -> bool:
    stripped_text = text.strip(" \t\r\n。！？?！")
    if stripped_text == "寿命":
        return True

    for pattern in LIFESPAN_OR_DEATH_TIMING_PATTERNS:
        if any(
            not _is_safe_context(text, start_index)
            for start_index in _iter_match_starts(text, pattern)
        ):
            return True

    return False


def safety_check(text: str, *, disclaimer_present: bool = False) -> SafetyReviewResult:
    prohibited_phrases = _find_unsafe_phrases(text, PROHIBITED_PHRASES)
    red_line_categories: list[str] = []
    redirect_message = ""

    if _has_lifespan_or_death_timing_request(text):
        red_line_categories.append("lifespan_or_death_timing")
        redirect_message = LIFESPAN_OR_DEATH_TIMING_REDIRECT

    return SafetyReviewResult(
        allowed=not red_line_categories and not prohibited_phrases,
        red_line_categories=red_line_categories,
        prohibited_phrases=prohibited_phrases,
        disclaimer_present=disclaimer_present,
        redirect_message=redirect_message,
    )
