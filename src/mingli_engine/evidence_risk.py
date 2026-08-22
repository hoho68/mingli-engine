"""Independent risk classifier for KNOWLEDGE EVIDENCE content.

This module governs the content of candidate extracts, learning records and
evidence units — the material that can enter the report-usable knowledge chain.
It is deliberately separate from ``high_risk.classify_high_risk_request``,
which governs user requests: a classical text teaching how to determine a
death juncture is not a user request, but it must never become ordinary
report-usable knowledge either.

Three deterministic classes:

- ``exact_death_lifespan_rule`` — exact lifespan, death timing, death juncture,
  lifespan conversion, or condition→death verdicts (including quoted classical
  fatality verses). Never promotable; learning records are retained but the
  content must not reach the report-usable chain.
- ``descriptive_death_content`` — death/lifespan-adjacent content framed as
  historical/cultural transcription, case narration, negated or averted
  contexts, auspicious longevity verses, or harm content whose death semantics
  cannot be reliably excluded. Promotable only as ``high_risk`` evidence in the
  governed ``high_risk_signal`` family with the required boundary limitation;
  never an ordinary reasoning conclusion.
- ``ordinary_content`` — everything else, including structural terms that only
  look like death wording (十二长生 stage names, 空亡, 亡神, 死绝) and explicit
  negations (不主死亡).
"""

import unicodedata
from dataclasses import dataclass
from typing import Iterable

ORDINARY_CONTENT = "ordinary_content"
DESCRIPTIVE_DEATH_CONTENT = "descriptive_death_content"
EXACT_DEATH_LIFESPAN_RULE = "exact_death_lifespan_rule"

EVIDENCE_RISK_CLASSES = frozenset(
    {ORDINARY_CONTENT, DESCRIPTIVE_DEATH_CONTENT, EXACT_DEATH_LIFESPAN_RULE}
)

HIGH_RISK_SIGNAL_FAMILY = "high_risk_signal"

REQUIRED_DESCRIPTIVE_DEATH_LIMITATION = (
    "仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，"
    "不输出精确生死结论。"
)

EXACT_DEATH_LIFESPAN_GATE_REASON = (
    "Exact death or lifespan prediction content is not promotable to "
    "report-usable knowledge."
)

# Condition→death verdicts, death timing/juncture, lifespan length or
# conversion. Matching is restricted to the knowledge content itself (the
# extracted meaning / summary), never the limitation boilerplate, and negated
# contexts are excluded per match.
_EXACT_PATTERNS: tuple[str, ...] = (
    "死亡关口",
    "生死关口",
    "死期",
    "寿终",
    "壽終",
    "寿数",
    "壽數",
    "岁亡",
    "歲亡",
    "夭亡",
    "夭折",
    "早夭",
    "夭寿",
    "夭壽",
    "夭贫",
    "夭貧",
    "非夭",
    "主夭",
    "早死",
    "早亡",
    "短命",
    "寿短",
    "壽短",
    "寿不长",
    "壽不長",
    "寿有损",
    "壽有損",
    "少寿",
    "少壽",
    "凶亡",
    "横死",
    "橫死",
    "凶死",
    "必死",
    "克死",
    "早丧",
    "早喪",
    "双亡",
    "雙亡",
    "身亡",
    "亡身",
    "死于",
    "死於",
    "而死",
    "父死",
    "母死",
    "夫亡",
    "妻亡",
    "丧偶",
    "喪偶",
    "黄泉",
    "黃泉",
    "死别",
    "死別",
    "十有七亡",
    "十有九亡",
    "不得善终",
    "不得善終",
    "则死",
    "則死",
    "先亡",
    "送终",
    "送終",
    "后亡",
    "後亡",
    "路上死",
    "尅雙親",
    "剋雙親",
    "克双亲",
    "必克兄弟",
    "体死绝而亡",
    "體死絕而亡",
)

# Bare 死亡 in the knowledge content is exact unless the content itself frames
# it as case narration / descriptive transcription / a general risk marker.
_DEATH_BARE = "死亡"
_DESCRIPTIVE_FRAMING_MARKERS: tuple[str, ...] = (
    "案例",
    "仅作",
    "僅作",
    "描述",
    "转录",
    "轉錄",
    "转写",
    "轉寫",
    "著录",
    "著錄",
    "文献",
    "文獻",
    "照录",
    "照錄",
    "风险标记",
    "風險標記",
    "存档",
    "存檔",
)

# Death-adjacent content without an exact death/lifespan verdict. These never
# stay ordinary; they become descriptive high-risk signals.
_DESCRIPTIVE_DOMAIN_PATTERNS: tuple[str, ...] = (
    "自杀",
    "自殺",
    "自尽",
    "自盡",
    "生命垂危",
    "早伤",
    "早傷",
    "伤亡",
    "傷亡",
    "丧孝",
    "喪孝",
    "大关口",
    "长寿",
    "長壽",
    "寿元",
    "壽元",
    "短促",
)

# Death-domain terms that, combined with descriptive framing anywhere in the
# record (meaning or limitations), indicate self-declared descriptive death
# content that cannot be reliably separated from the knowledge content.
_DEATH_DOMAIN_TERMS: tuple[str, ...] = _EXACT_PATTERNS + (
    "死亡",
    "自杀",
    "自殺",
    "寿夭",
    "壽夭",
    "寿命",
    "壽命",
    "寿元",
    "壽元",
    "伤亡",
    "傷亡",
    "虚耗",
    "虛耗",
    "血光",
)

# Negation contexts: a death term explicitly ruled out is not a death verdict
# (e.g. 不主死亡, 不至于早夭).
_NEGATION_MARKERS: tuple[str, ...] = (
    "不主",
    "不至于",
    "不至於",
    "并非",
    "並非",
    "不是",
    "不作",
    "不构成",
    "不構成",
)


class EvidenceContentRiskError(ValueError):
    """Raised when report-usable knowledge violates the content risk gate."""


@dataclass(frozen=True)
class EvidenceContentRisk:
    risk_class: str
    matched_marker: str = ""
    matched_field: str = ""


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def _has_unnegated_match(text: str, pattern: str) -> bool:
    start = text.find(pattern)
    while start != -1:
        context = text[max(0, start - 6) : start]
        if not any(marker in context for marker in _NEGATION_MARKERS):
            return True
        start = text.find(pattern, start + len(pattern))
    return False


def classify_evidence_content(
    meaning: str, limitations: Iterable[str] = ()
) -> EvidenceContentRisk:
    """Classify knowledge evidence content into the three risk classes.

    ``meaning`` is the knowledge content itself (candidate ``extracted_meaning``
    / evidence ``summary`` / learning-record ``conclusion``); ``limitations``
    are only used to detect self-declared descriptive framing.
    """
    text = _normalize(meaning)
    full_text = text + " " + _normalize(" ".join(limitations))

    for pattern in _EXACT_PATTERNS:
        if _has_unnegated_match(text, pattern):
            return EvidenceContentRisk(
                risk_class=EXACT_DEATH_LIFESPAN_RULE,
                matched_marker=pattern,
                matched_field="meaning",
            )
    if _has_unnegated_match(text, _DEATH_BARE):
        if any(marker in text for marker in _DESCRIPTIVE_FRAMING_MARKERS):
            return EvidenceContentRisk(
                risk_class=DESCRIPTIVE_DEATH_CONTENT,
                matched_marker=_DEATH_BARE,
                matched_field="meaning",
            )
        return EvidenceContentRisk(
            risk_class=EXACT_DEATH_LIFESPAN_RULE,
            matched_marker=_DEATH_BARE,
            matched_field="meaning",
        )
    for pattern in _DESCRIPTIVE_DOMAIN_PATTERNS:
        if _has_unnegated_match(text, pattern):
            return EvidenceContentRisk(
                risk_class=DESCRIPTIVE_DEATH_CONTENT,
                matched_marker=pattern,
                matched_field="meaning",
            )
    if any(
        _has_unnegated_match(full_text, term) for term in _DEATH_DOMAIN_TERMS
    ) and any(marker in full_text for marker in _DESCRIPTIVE_FRAMING_MARKERS):
        field = (
            "meaning+limitations"
            if any(_has_unnegated_match(text, term) for term in _DEATH_DOMAIN_TERMS)
            else "limitations"
        )
        return EvidenceContentRisk(
            risk_class=DESCRIPTIVE_DEATH_CONTENT,
            matched_marker="death-domain+framing",
            matched_field=field,
        )
    return EvidenceContentRisk(risk_class=ORDINARY_CONTENT)


def enforce_promotion_content_gate(
    *,
    meaning: str,
    limitations: Iterable[str],
    risk_tier: str,
    rule_family: str,
    owner_id: str = "",
) -> EvidenceContentRisk:
    """Deterministic promotion gate for report-usable knowledge content.

    - exact death/lifespan rules are never promotable, at any tier;
    - descriptive death content is promotable only as ``high_risk`` evidence in
      the governed ``high_risk_signal`` family carrying the required boundary
      limitation;
    - ordinary content passes unchanged.
    """
    risk = classify_evidence_content(meaning, limitations)
    if risk.risk_class == EXACT_DEATH_LIFESPAN_RULE:
        raise EvidenceContentRiskError(
            f"{owner_id} exact death/lifespan rule content is not promotable"
        )
    if risk.risk_class == DESCRIPTIVE_DEATH_CONTENT:
        limitation_text = " ".join(limitations)
        if risk_tier != "high_risk" or rule_family != HIGH_RISK_SIGNAL_FAMILY:
            raise EvidenceContentRiskError(
                f"{owner_id} descriptive death content requires high_risk tier "
                f"and {HIGH_RISK_SIGNAL_FAMILY} family"
            )
        if not any(
            marker in limitation_text
            for marker in ("精确", "不输出", "拒绝", "不得")
        ):
            raise EvidenceContentRiskError(
                f"{owner_id} descriptive death content requires an explicit "
                "boundary limitation prohibiting real-world lifespan, death "
                "timing or medical judgement"
            )
    return risk
