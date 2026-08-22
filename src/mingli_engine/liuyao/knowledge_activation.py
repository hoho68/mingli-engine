"""Deterministic evidence activation layer for liuyao analysis (021).

Activates the 67 governed liuyao evidence units promoted by the
batch_20260714 review pipeline. This module only reads through
``mingli_engine.liuyao.knowledge`` loaders; it never re-implements ledger
parsing and never mutates any knowledge ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mingli_engine.liuyao.constants import LIUYAO_RULE_FAMILIES
from mingli_engine.liuyao.knowledge import (
    LiuyaoEvidenceUnit,
    LiuyaoKnowledgeError,
    load_liuyao_evidence_units,
    validate_liuyao_knowledge_chain,
)

EVIDENCE_ACTIVATED_NOTE = (
    "本族观察已连接六爻正式证据；每条引用均可追溯到治理链晋升的"
    "证据单元、来源与页级定位，仅作传统文献学习参考，不构成任何现实预测。"
)

_EXPECTED_TOTAL = 67


@dataclass(frozen=True)
class LiuyaoEvidenceCitation:
    """A full reference carried by an activated analysis conclusion."""

    evidence_id: str
    rule_family: str
    source_id: str
    source_ref: str
    theme: str
    summary: str
    limitations: tuple[str, ...]
    confidence: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "limitations", tuple(self.limitations))
        for value, field_name in (
            (self.evidence_id, "evidence_id"),
            (self.rule_family, "rule_family"),
            (self.source_id, "source_id"),
            (self.source_ref, "source_ref"),
            (self.theme, "theme"),
            (self.summary, "summary"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"liuyao citation {field_name} is required")
        if not self.source_ref.startswith("page:"):
            raise ValueError("liuyao citation source_ref must be a page locator")
        if self.rule_family not in LIUYAO_RULE_FAMILIES:
            raise ValueError("liuyao citation family is outside the namespace")
        if not self.limitations:
            raise ValueError("liuyao citation requires limitation language")
        if self.confidence not in {"strong", "moderate", "weak"}:
            raise ValueError("liuyao citation confidence is invalid")


def citation_from_unit(unit: LiuyaoEvidenceUnit) -> LiuyaoEvidenceCitation:
    """Convert a governed evidence unit into an analysis citation."""
    if not isinstance(unit, LiuyaoEvidenceUnit):
        raise TypeError("citation requires a LiuyaoEvidenceUnit")
    return LiuyaoEvidenceCitation(
        evidence_id=unit.evidence_id,
        rule_family=unit.rule_family,
        source_id=unit.source_id,
        source_ref=unit.source_ref,
        theme=unit.theme,
        summary=unit.summary,
        limitations=unit.limitations,
        confidence=unit.confidence,
    )


@dataclass(frozen=True)
class LiuyaoEvidenceIndex:
    """Family-indexed deterministic view over the governed evidence units."""

    family_evidence: tuple[tuple[str, tuple[LiuyaoEvidenceUnit, ...]], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "family_evidence",
            tuple((family, tuple(units)) for family, units in self.family_evidence),
        )
        families = tuple(family for family, _ in self.family_evidence)
        if families != LIUYAO_RULE_FAMILIES:
            raise ValueError("evidence index must cover the governed families in order")

    def family(self, rule_family: str) -> tuple[LiuyaoEvidenceUnit, ...]:
        """Return the family's evidence units in ledger order."""
        return {family: units for family, units in self.family_evidence}[
            rule_family
        ]


def build_liuyao_evidence_index(
    data_dir: Path | None = None,
) -> LiuyaoEvidenceIndex:
    """Build the family index after full knowledge-chain validation.

    Fails closed: any ledger or cross-link corruption raises
    ``LiuyaoKnowledgeError`` instead of producing a partial index.
    """
    validate_liuyao_knowledge_chain(data_dir)
    units = load_liuyao_evidence_units(data_dir)
    if len(units) != _EXPECTED_TOTAL:
        raise LiuyaoKnowledgeError(
            "the liuyao evidence ledger does not hold the frozen unit count"
        )
    return LiuyaoEvidenceIndex(
        family_evidence=tuple(
            (
                family,
                tuple(item for item in units if item.rule_family == family),
            )
            for family in LIUYAO_RULE_FAMILIES
        )
    )


@dataclass(frozen=True)
class LiuyaoActivationSummary:
    """Validated activation facts over the frozen evidence namespace."""

    total_count: int
    family_counts: tuple[tuple[str, int], ...]
    all_ordinary_risk: bool
    all_moderate_confidence: bool
    all_page_locators: bool

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "family_counts", tuple(self.family_counts)
        )
        if self.total_count <= 0:
            raise ValueError("activation summary requires activated evidence")
        if not self.all_page_locators:
            raise ValueError("activated evidence requires page-level locators")


def validate_liuyao_evidence_activation(
    data_dir: Path | None = None,
) -> LiuyaoActivationSummary:
    """Validate the activation layer and return its governed facts."""
    index = build_liuyao_evidence_index(data_dir)
    units = tuple(
        unit for _, family_units in index.family_evidence for unit in family_units
    )
    return LiuyaoActivationSummary(
        total_count=len(units),
        family_counts=tuple(
            (family, len(family_units))
            for family, family_units in index.family_evidence
        ),
        all_ordinary_risk=all(unit.risk_tier == "ordinary" for unit in units),
        all_moderate_confidence=all(
            unit.confidence == "moderate" for unit in units
        ),
        all_page_locators=all(
            unit.source_ref.startswith("page:") for unit in units
        ),
    )
