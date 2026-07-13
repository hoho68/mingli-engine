from __future__ import annotations

from collections import Counter
from types import MappingProxyType
from typing import Final, Mapping

from mingli_engine.bazi.constants import ELEMENTS
from mingli_engine.bazi.result_models import (
    BlindImageResult,
    BlindImageSignal,
    BranchRelationResult,
    ChartFacts,
    ComputationStatus,
    PatternCandidateResult,
    ReasonedResult,
    RemedyBoundaryResult,
    SchoolInterpretation,
    StrengthResult,
    TabooGodCandidate,
    TabooGodResult,
    UsefulGodCandidateResult,
)


TABOO_EVIDENCE_IDS: Final = (
    "duan_taboo_god_candidate_001",
    "duan_taboo_god_candidate_002",
)
BLIND_IMAGE_EVIDENCE_IDS: Final = (
    "northeast_blind_image_001",
    "northeast_blind_image_002",
    "northeast_blind_image_003",
    "northeast_blind_image_004",
)
REMEDY_BOUNDARY_EVIDENCE_IDS: Final = (
    "fortune_remedy_boundary_001",
    "fortune_remedy_boundary_002",
    "fortune_remedy_boundary_003",
    "fortune_remedy_boundary_004",
)

_ELEMENT_ORDER: Final[Mapping[str, int]] = MappingProxyType(
    {element: index for index, element in enumerate(ELEMENTS)}
)
_HIDDEN_WEIGHTS: Final[Mapping[str, float]] = MappingProxyType(
    {"main": 1.5, "middle": 1.0, "residual": 0.5}
)


def _not_computed(
    family: str,
    missing_inputs: tuple[str, ...],
) -> ReasonedResult:
    return ReasonedResult(
        status="not_computed",
        conclusion=f"{family} prerequisites are unavailable",
        confidence="low",
        missing_inputs=missing_inputs,
        rule_ids=(f"{family}.prerequisite.complete",),
    )


def _school_preference_disagreement(
    schools: tuple[SchoolInterpretation, ...],
) -> bool:
    active = tuple(
        item.preferred_useful_god_elements
        for item in schools
        if item.reasoning.status != "not_computed"
    )
    return len(set(active)) > 1


def calculate_taboo_god_candidates(
    facts: ChartFacts,
    strength: StrengthResult,
    patterns: tuple[PatternCandidateResult, ...],
    schools: tuple[SchoolInterpretation, ...],
) -> TabooGodResult:
    """Identify structural pressure candidates without inverting useful gods."""
    if strength.reasoning.status == "not_computed" or not facts.exposed_stems:
        return TabooGodResult(
            reasoning=_not_computed(
                "taboo",
                ("computed_strength", "canonical_element_facts"),
            ),
            candidates=(),
            evidence_ids=TABOO_EVIDENCE_IDS,
        )

    pressure = {element: 0.0 for element in ELEMENTS}
    for exposed in facts.exposed_stems:
        pressure[exposed.element] += 2.0
    for hidden in facts.hidden_stems:
        pressure[hidden.element] += _HIDDEN_WEIGHTS.get(hidden.role, 0.0)

    pattern_damage = Counter(
        condition
        for pattern in patterns
        for condition in pattern.damage_conditions
        if condition
    )
    ranked = sorted(
        pressure.items(),
        key=lambda item: (-item[1], _ELEMENT_ORDER.get(item[0], len(ELEMENTS))),
    )[:2]
    candidates = tuple(
        TabooGodCandidate(
            element=element,
            rank=index,
            pressure_score=score,
            reasons=(
                f"weighted_presence:{score:g}",
                f"strength_context:{strength.label or 'unclassified'}",
                f"pattern_damage_signals:{sum(pattern_damage.values())}",
            ),
        )
        for index, (element, score) in enumerate(ranked, 1)
    )
    candidate_signals = tuple(
        f"taboo_candidate:{item.element}:rank={item.rank}:pressure={item.pressure_score:g}"
        for item in candidates
    )
    rules = [
        "taboo.structure.element_presence",
        "taboo.context.strength_pressure",
        "taboo.context.pattern_damage",
    ]
    status: ComputationStatus = strength.reasoning.status
    opposing: tuple[str, ...] = ()
    if status == "computed" and _school_preference_disagreement(schools):
        candidate_elements = {item.element for item in candidates}
        preferred = {
            element
            for school in schools
            for element in school.preferred_useful_god_elements
        }
        if candidate_elements.intersection(preferred):
            status = "disputed"
            rules.append("taboo.school.preference_conflict")
            opposing = ("taboo_candidate_overlaps_school_support_preference",)
    return TabooGodResult(
        reasoning=ReasonedResult(
            status=status,
            conclusion="weighted structural pressure candidates were calculated",
            confidence="low" if status != "computed" else "medium",
            supporting_signals=candidate_signals,
            opposing_signals=opposing,
            assumptions=facts.assumptions,
            rule_ids=tuple(rules),
        ),
        candidates=candidates,
        evidence_ids=TABOO_EVIDENCE_IDS,
    )


def calculate_blind_image_method(
    facts: ChartFacts,
    relations: tuple[BranchRelationResult, ...],
    strength: StrengthResult,
    schools: tuple[SchoolInterpretation, ...],
) -> BlindImageResult:
    """Build structural image signals from canonical chart facts and relations."""
    complete_pillars = {item.pillar_name for item in facts.exposed_stems}
    if (
        strength.reasoning.status == "not_computed"
        or complete_pillars != {"year", "month", "day", "hour"}
        or not facts.hidden_stems
    ):
        return BlindImageResult(
            reasoning=_not_computed(
                "blind.image",
                ("canonical_four_pillar_facts", "computed_strength"),
            ),
            images=(),
            evidence_ids=BLIND_IMAGE_EVIDENCE_IDS,
        )

    images: list[BlindImageSignal] = []
    if facts.roots:
        root_links = tuple(
            f"{item.stem_pillar}->{item.branch_pillar}:{item.stem}:{item.role}"
            for item in facts.roots
        )
        images.append(
            BlindImageSignal(
                image_id="root_resonance",
                category="root_structure",
                value=f"root_links={len(root_links)}",
                structural_signals=root_links,
            )
        )
    for index, relation in enumerate(relations, 1):
        images.append(
            BlindImageSignal(
                image_id=f"branch_relation_{index}",
                category="branch_interaction",
                value=(
                    f"{relation.relation_type}:{relation.state}:"
                    f"{','.join(relation.pillar_names)}"
                ),
                structural_signals=(
                    f"branches:{','.join(relation.branches)}",
                    f"rule:{relation.rule_id}",
                ),
            )
        )

    if not images:
        return BlindImageResult(
            reasoning=ReasonedResult(
                status="indeterminate",
                conclusion="no cross-confirmed structural image signal was found",
                confidence="low",
                missing_inputs=("root_or_branch_interaction_signal",),
                assumptions=facts.assumptions,
                rule_ids=("blind.image.structural_cross_check",),
            ),
            images=(),
            evidence_ids=BLIND_IMAGE_EVIDENCE_IDS,
        )

    image_signals = tuple(
        f"blind_image:{item.image_id}:{item.category}:{item.value}"
        for item in images
    )
    rules = ["blind.image.structural_cross_check"]
    if facts.roots:
        rules.append("blind.image.root_resonance")
    if relations:
        rules.append("blind.image.branch_interaction")
    status: ComputationStatus = (
        "indeterminate"
        if strength.reasoning.status == "indeterminate"
        else "computed"
    )
    return BlindImageResult(
        reasoning=ReasonedResult(
            status=status,
            conclusion="structural image signals were cross-confirmed",
            confidence="medium" if status == "computed" else "low",
            supporting_signals=image_signals,
            assumptions=(
                *facts.assumptions,
                "school_context_ids:"
                + ",".join(item.school_id for item in schools),
            ),
            rule_ids=tuple(rules),
        ),
        images=tuple(images),
        evidence_ids=BLIND_IMAGE_EVIDENCE_IDS,
    )


def calculate_remedy_boundary(
    strength: StrengthResult,
    useful_gods: tuple[UsefulGodCandidateResult, ...],
    schools: tuple[SchoolInterpretation, ...],
) -> RemedyBoundaryResult:
    """Translate available structure into bounded, non-promissory use rules."""
    active = tuple(
        item for item in useful_gods if item.reasoning.status != "not_computed"
    )
    if strength.reasoning.status == "not_computed" or not active:
        return RemedyBoundaryResult(
            reasoning=_not_computed(
                "remedy.boundary",
                ("computed_strength", "available_useful_god_context"),
            ),
            conditions=(),
            applicable_boundaries=(),
            stop_conditions=(),
            evidence_ids=REMEDY_BOUNDARY_EVIDENCE_IDS,
        )

    conditions = (
        f"strength_status:{strength.reasoning.status}",
        "candidate_context_available",
        "traditional_reflection_only",
    )
    boundaries = (
        "reversible_observation_only",
        "no_outcome_promise",
        "no_professional_advice_substitution",
    )
    stop_conditions = (
        "paid_remedy_or_ritual",
        "fear_or_dependency_language",
        "medical_legal_financial_or_mental_health_request",
    )
    status: ComputationStatus = (
        "indeterminate"
        if strength.reasoning.status == "indeterminate"
        or any(item.reasoning.status == "indeterminate" for item in active)
        else "computed"
    )
    rules = [
        "remedy.boundary.low_risk_reflection",
        "remedy.boundary.no_outcome_promise",
        "remedy.boundary.stop_conditions",
    ]
    opposing: tuple[str, ...] = ()
    if _school_preference_disagreement(schools):
        status = "disputed"
        rules.append("remedy.boundary.school_disagreement")
        opposing = ("school_method_preferences_require_separate_review",)
    signals = (
        *(f"remedy_condition:{item}" for item in conditions),
        *(f"remedy_boundary:{item}" for item in boundaries),
        *(f"remedy_stop:{item}" for item in stop_conditions),
    )
    return RemedyBoundaryResult(
        reasoning=ReasonedResult(
            status=status,
            conclusion="bounded low-risk reflection conditions were calculated",
            confidence="low" if status != "computed" else "medium",
            supporting_signals=signals,
            opposing_signals=opposing,
            assumptions=("useful_god_context_is_not_a_remedy_result",),
            rule_ids=tuple(rules),
        ),
        conditions=conditions,
        applicable_boundaries=boundaries,
        stop_conditions=stop_conditions,
        evidence_ids=REMEDY_BOUNDARY_EVIDENCE_IDS,
    )
