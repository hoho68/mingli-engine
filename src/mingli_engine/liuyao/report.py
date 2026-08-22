"""Liuyao report model and boundary enforcement (V1)."""

from __future__ import annotations

from dataclasses import dataclass
import unicodedata

from mingli_engine.high_risk import classify_high_risk_request
from mingli_engine.liuyao.analysis import LiuyaoAnalysis
from mingli_engine.safety import safety_check

_PROHIBITED_ABSOLUTE_WORDING: tuple[str, ...] = (
    "必定",
    "注定",
    "一定会",
    "死定",
    "guaranteed to",
    "will certainly",
)

REPORT_DISCLAIMER = (
    "本报告定位为传统占卜文化的学习与自我反思材料，不是科学预测，"
    "也不替代医疗、法律、心理、投资等专业建议；任何现实决策仍以您本人"
    "与合格专业人士的判断为准。"
)


class LiuyaoReportError(ValueError):
    """Raised when a report cannot be produced within the boundary."""


@dataclass(frozen=True)
class LiuyaoReport:
    title: str
    disclaimer: str
    analysis: LiuyaoAnalysis

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("report title is required")
        if not self.disclaimer.strip():
            raise ValueError("report disclaimer is required")
        if not isinstance(self.analysis, LiuyaoAnalysis):
            raise TypeError("report requires a LiuyaoAnalysis")


def build_liuyao_report(analysis: LiuyaoAnalysis) -> LiuyaoReport:
    """Build a report after boundary checks over all composed text."""
    if not isinstance(analysis, LiuyaoAnalysis):
        raise TypeError("report requires a LiuyaoAnalysis")
    composed = " ".join(
        f"{item.headline} {' '.join(item.observations)} {' '.join(item.limitations)}"
        for item in analysis.family_observations
    )
    normalized = unicodedata.normalize("NFKC", composed).casefold()
    if any(
        marker.casefold() in normalized for marker in _PROHIBITED_ABSOLUTE_WORDING
    ):
        raise LiuyaoReportError("the report contains prohibited absolute wording")
    safety = safety_check(REPORT_DISCLAIMER + composed, disclaimer_present=True)
    high_risk = classify_high_risk_request(composed)
    if not safety.allowed or not high_risk.allowed:
        raise LiuyaoReportError(
            "the report cannot be produced within the safety boundary"
        )
    return LiuyaoReport(
        title="六爻排盘学习报告",
        disclaimer=REPORT_DISCLAIMER,
        analysis=analysis,
    )
