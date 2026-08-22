"""Deterministic evidence activation layer for liuyao analysis (021).

Activates the 67 governed liuyao evidence units promoted by the
batch_20260714 review pipeline. This module only reads through
``mingli_engine.liuyao.knowledge`` loaders; it never re-implements ledger
parsing and never mutates any knowledge ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mingli_engine.high_risk import REFUSAL_MESSAGE
from mingli_engine.liuyao.constants import (
    LIUYAO_HIGH_RISK_MATTER_CATEGORY_LABELS,
    LIUYAO_MATTER_CATEGORIES,
    LIUYAO_MATTER_CATEGORY_LABELS,
    LIUYAO_RULE_FAMILIES,
)
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


# Matter category → governed evidence mapping (021 follow-up). Each id is a
# promoted ``category_judgment`` unit whose theme/summary explicitly addresses
# the matter; ids stay in ledger order. No category is asserted beyond what
# the frozen evidence ledger covers, and no ledger content is duplicated here.
CATEGORY_EVIDENCE_IDS: dict[str, tuple[str, ...]] = {
    "weather": (
        "liuyao_evidence_batch_20260714_0012",
        "liuyao_evidence_batch_20260714_0027",
        "liuyao_evidence_batch_20260714_0049",
        "liuyao_evidence_batch_20260714_0050",
    ),
    "annual_fortune": (
        "liuyao_evidence_batch_20260714_0013",
        "liuyao_evidence_batch_20260714_0028",
        "liuyao_evidence_batch_20260714_0029",
    ),
    "wealth": (
        "liuyao_evidence_batch_20260714_0033",
        "liuyao_evidence_batch_20260714_0034",
        "liuyao_evidence_batch_20260714_0055",
    ),
    "career": (
        "liuyao_evidence_batch_20260714_0014",
        "liuyao_evidence_batch_20260714_0055",
    ),
    "marriage": ("liuyao_evidence_batch_20260714_0014",),
    "travel": ("liuyao_evidence_batch_20260714_0055",),
    "lost_items": (
        "liuyao_evidence_batch_20260714_0036",
        "liuyao_evidence_batch_20260714_0037",
        "liuyao_evidence_batch_20260714_0038",
    ),
    "house": ("liuyao_evidence_batch_20260714_0039",),
    "agriculture": (
        "liuyao_evidence_batch_20260714_0031",
        "liuyao_evidence_batch_20260714_0032",
    ),
}


class LiuyaoMatterCategoryError(ValueError):
    """Base error for matter category input failures."""


class UnknownLiuyaoMatterCategoryError(LiuyaoMatterCategoryError):
    """Raised when the matter category is outside the governed vocabulary."""


class RefusedLiuyaoMatterCategoryError(LiuyaoMatterCategoryError):
    """Raised when a high-risk matter category is refused before analysis."""


@dataclass(frozen=True)
class LiuyaoMatterCategoryGate:
    """Classification result for the optional matter category input."""

    category: str | None
    label: str
    status: str

    def __post_init__(self) -> None:
        if self.status == "not_provided":
            if self.category is not None or self.label != "":
                raise ValueError("an absent matter category carries no label")
        elif self.status == "accepted":
            if self.category not in LIUYAO_MATTER_CATEGORY_LABELS:
                raise ValueError("accepted matter category must be supported")
            if LIUYAO_MATTER_CATEGORY_LABELS[self.category] != self.label:
                raise ValueError("matter category label mismatch")
        else:
            raise ValueError("unsupported matter category gate status")


def resolve_matter_category(category: str | None) -> LiuyaoMatterCategoryGate:
    """Validate and classify the optional matter category input.

    High-risk categories (medical, legal, investment, lifespan) reuse the
    existing safety refusal message and are refused before any analysis;
    unknown categories raise an input validation error.
    """
    if category is None:
        return LiuyaoMatterCategoryGate(
            category=None, label="", status="not_provided"
        )
    if not isinstance(category, str) or category not in LIUYAO_MATTER_CATEGORIES:
        raise UnknownLiuyaoMatterCategoryError(
            "unknown liuyao matter category"
        )
    if category in LIUYAO_HIGH_RISK_MATTER_CATEGORY_LABELS:
        raise RefusedLiuyaoMatterCategoryError(REFUSAL_MESSAGE)
    return LiuyaoMatterCategoryGate(
        category=category,
        label=LIUYAO_MATTER_CATEGORY_LABELS[category],
        status="accepted",
    )


@dataclass(frozen=True)
class LiuyaoMatterCategoryIndex:
    """Category-indexed deterministic view over category_judgment evidence."""

    category_units: tuple[tuple[str, tuple[LiuyaoEvidenceUnit, ...]], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "category_units",
            tuple(
                (category, tuple(units))
                for category, units in self.category_units
            ),
        )
        categories = tuple(category for category, _ in self.category_units)
        if categories != tuple(LIUYAO_MATTER_CATEGORY_LABELS):
            raise ValueError(
                "matter category index must cover the supported categories in order"
            )
        for category, units in self.category_units:
            if not units:
                raise ValueError("a supported matter category requires evidence")
            evidence_ids = [unit.evidence_id for unit in units]
            if len(set(evidence_ids)) != len(evidence_ids):
                raise ValueError("matter category evidence ids must be unique")
            for unit in units:
                if not isinstance(unit, LiuyaoEvidenceUnit):
                    raise TypeError("matter category units must be evidence units")
                if unit.rule_family != "category_judgment":
                    raise ValueError(
                        "matter category evidence must come from category_judgment"
                    )

    def units_for(self, category: str) -> tuple[LiuyaoEvidenceUnit, ...]:
        """Return the category's evidence units in ledger order."""
        return {name: units for name, units in self.category_units}[category]


def build_liuyao_matter_category_index(
    evidence_index: LiuyaoEvidenceIndex,
) -> LiuyaoMatterCategoryIndex:
    """Build the matter category index over a validated evidence index.

    Fails closed: any mapped evidence id missing from the governed ledger
    raises ``LiuyaoKnowledgeError`` instead of producing a partial mapping.
    """
    if not isinstance(evidence_index, LiuyaoEvidenceIndex):
        raise TypeError("matter category index requires a LiuyaoEvidenceIndex")
    if tuple(CATEGORY_EVIDENCE_IDS) != tuple(LIUYAO_MATTER_CATEGORY_LABELS):
        raise LiuyaoKnowledgeError(
            "the matter category mapping does not cover the supported vocabulary"
        )
    family_units = evidence_index.family("category_judgment")
    ledger_ids = {unit.evidence_id for unit in family_units}
    missing = sorted(
        {
            evidence_id
            for evidence_ids in CATEGORY_EVIDENCE_IDS.values()
            for evidence_id in evidence_ids
        }
        - ledger_ids
    )
    if missing:
        raise LiuyaoKnowledgeError(
            "the matter category mapping references evidence outside the ledger"
        )
    return LiuyaoMatterCategoryIndex(
        category_units=tuple(
            (
                category,
                tuple(
                    unit
                    for unit in family_units
                    if unit.evidence_id in frozenset(evidence_ids)
                ),
            )
            for category, evidence_ids in CATEGORY_EVIDENCE_IDS.items()
        )
    )
