from collections.abc import Callable
from dataclasses import dataclass

from mingli_engine.bazi import (
    build_legacy_not_computed_bundle,
    validate_calculation_binding,
)
from mingli_engine.bazi.result_models import CalculationBundle, ReasonedResult
from mingli_engine.models import (
    BaziChart,
    CalculationStatus,
    EvidenceTrace,
    EvidenceUnit,
    ExpandedReportEvidence,
    FormalConclusion,
    SourceConflict,
)


_STATUS_PRIORITY = {
    "not_computed": 0,
    "computed": 1,
    "indeterminate": 2,
    "disputed": 3,
}
_CONFIDENCE_PRIORITY = {"low": 0, "medium": 1, "high": 2}
_SCHOOL_DISAGREEMENT_RULE_IDS = {
    "pattern_strength": "school.cross_school_disagreement.pattern_preferences",
    "useful_god_candidate": (
        "school.cross_school_disagreement.useful_god_preferences"
    ),
    "remedy_boundary": "school.cross_school_disagreement.useful_god_preferences",
}


def _not_computed_reasoning(rule_family: str) -> ReasonedResult:
    reason = f"no_v1_calculation_for:{rule_family}"
    return ReasonedResult(
        status="not_computed",
        conclusion=f"No V1 calculation is available for {rule_family}.",
        confidence="low",
        missing_inputs=(reason,),
        rule_ids=(reason,),
    )


def _aggregate_reasoning(
    rule_family: str,
    reasonings: tuple[ReasonedResult, ...],
) -> ReasonedResult:
    if not reasonings:
        return _not_computed_reasoning(rule_family)
    status = max(reasonings, key=lambda item: _STATUS_PRIORITY[item.status]).status
    driving = tuple(item for item in reasonings if item.status == status)
    confidence = min(
        driving,
        key=lambda item: _CONFIDENCE_PRIORITY[item.confidence],
    ).confidence

    def distinct(values: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(value for value in values if value))

    return ReasonedResult(
        status=status,
        conclusion=" | ".join(
            f"{index + 1}:{item.conclusion}" for index, item in enumerate(reasonings)
        ),
        confidence=confidence,
        supporting_signals=distinct(
            tuple(signal for item in reasonings for signal in item.supporting_signals)
        ),
        opposing_signals=distinct(
            tuple(signal for item in reasonings for signal in item.opposing_signals)
        ),
        assumptions=distinct(
            tuple(value for item in reasonings for value in item.assumptions)
        ),
        missing_inputs=distinct(
            tuple(value for item in reasonings for value in item.missing_inputs)
        ),
        rule_ids=distinct(tuple(value for item in reasonings for value in item.rule_ids)),
    )


def _school_reasonings(
    calculation: CalculationBundle,
    disagreement_label: str | None = None,
) -> tuple[ReasonedResult, ...]:
    if disagreement_label is None:
        return tuple(item.reasoning for item in calculation.schools)
    rule_id = f"school.cross_school_disagreement.{disagreement_label}"
    return tuple(
        item.reasoning
        for item in calculation.schools
        if item.reasoning.status != "disputed" or rule_id in item.reasoning.rule_ids
    )


def _family_reasoning(
    calculation: CalculationBundle,
    rule_family: str,
) -> ReasonedResult:
    if rule_family in {"pattern_strength", "five_element_balance"}:
        reasonings: tuple[ReasonedResult, ...] = (calculation.strength.reasoning,)
        if rule_family == "pattern_strength":
            reasonings += tuple(item.reasoning for item in calculation.patterns)
            reasonings += _school_reasonings(calculation, "pattern_preferences")
        return _aggregate_reasoning(rule_family, reasonings)
    if rule_family in {"useful_god_candidate", "remedy_boundary"}:
        reasonings = tuple(item.reasoning for item in calculation.useful_gods)
        reasonings += _school_reasonings(calculation, "useful_god_preferences")
        return _aggregate_reasoning(rule_family, reasonings)
    if rule_family == "blind_image_method":
        return _aggregate_reasoning(
            rule_family,
            _school_reasonings(calculation),
        )
    if rule_family == "luck_cycle":
        return calculation.luck_cycles.reasoning
    return _not_computed_reasoning(rule_family)


def classify_chart_calculation_states(
    calculation: CalculationBundle,
) -> dict[str, str]:
    return {
        spec.rule_family: _family_reasoning(calculation, spec.rule_family).status
        for spec in _FAMILY_SPECS
    }


@dataclass(frozen=True)
class _FamilySpec:
    rule_family: str
    title: str
    risk_tier: str
    signal_builder: Callable[[BaziChart], list[str]]


def _compact(values: list[str]) -> list[str]:
    compacted: list[str] = []
    for value in values:
        text = value.strip()
        if text and text not in compacted:
            compacted.append(text)
    return compacted


def _pillar_gan_zhi(chart: BaziChart) -> list[str]:
    return _compact(
        [
            f"{pillar.name}:{pillar.heavenly_stem}{pillar.earthly_branch}"
            for pillar in chart.pillars
        ]
    )


def _pillar_branches(chart: BaziChart) -> list[str]:
    return _compact([f"{pillar.name}:{pillar.earthly_branch}" for pillar in chart.pillars])


def _pillar_ten_gods(chart: BaziChart) -> list[str]:
    return _compact([f"{pillar.name}:{pillar.ten_god}" for pillar in chart.pillars])


def _pattern_signals(chart: BaziChart) -> list[str]:
    return _compact([chart.strength_assessment, *chart.pattern_candidates])


def _element_signals(chart: BaziChart) -> list[str]:
    return _compact(
        [f"{element}:{status}" for element, status in chart.five_elements_summary.items()]
    )


def _luck_signals(chart: BaziChart) -> list[str]:
    return _compact([chart.luck_cycle_summary])


def _useful_god_signals(chart: BaziChart) -> list[str]:
    return _compact(chart.useful_god_candidates)


def _taboo_god_signals(chart: BaziChart) -> list[str]:
    return _compact(
        [
            f"{element}:{status}"
            for element, status in chart.five_elements_summary.items()
            if "旺" in status or "偏" in status
        ]
    )


def _high_risk_signals(chart: BaziChart) -> list[str]:
    focus_topic = chart.birth_profile.focus_topic.strip()
    if focus_topic.lower() in {"", "unknown", "unspecified", "none", "null"}:
        focus_topic = ""
    return _compact(
        [
            f"focus_topic:{focus_topic}" if focus_topic else "",
            (
                f"stage_signal:{chart.luck_cycle_summary}"
                if chart.luck_cycle_summary.strip()
                else ""
            ),
            "traditional_high_risk_signal_boundary",
        ]
    )


_FAMILY_SPECS = (
    _FamilySpec(
        rule_family="pattern_strength",
        title="格局与旺衰候选",
        risk_tier="ordinary",
        signal_builder=_pattern_signals,
    ),
    _FamilySpec(
        rule_family="five_element_balance",
        title="五行强弱倾向",
        risk_tier="ordinary",
        signal_builder=_element_signals,
    ),
    _FamilySpec(
        rule_family="useful_god_candidate",
        title="用神候选边界",
        risk_tier="ordinary",
        signal_builder=_useful_god_signals,
    ),
    _FamilySpec(
        rule_family="taboo_god_candidate",
        title="忌神候选边界",
        risk_tier="ordinary",
        signal_builder=_taboo_god_signals,
    ),
    _FamilySpec(
        rule_family="ten_god_relation",
        title="十神组合关系",
        risk_tier="ordinary",
        signal_builder=_pillar_ten_gods,
    ),
    _FamilySpec(
        rule_family="branch_interaction",
        title="刑冲合害线索",
        risk_tier="ordinary",
        signal_builder=_pillar_branches,
    ),
    _FamilySpec(
        rule_family="blind_image_method",
        title="盲派象法取象",
        risk_tier="ordinary",
        signal_builder=_pillar_gan_zhi,
    ),
    _FamilySpec(
        rule_family="luck_cycle",
        title="大运流年主题",
        risk_tier="sensitive",
        signal_builder=_luck_signals,
    ),
    _FamilySpec(
        rule_family="remedy_boundary",
        title="趋避调整边界",
        risk_tier="sensitive",
        signal_builder=_useful_god_signals,
    ),
    _FamilySpec(
        rule_family="high_risk_signal",
        title="高风险信号边界",
        risk_tier="high_risk",
        signal_builder=_high_risk_signals,
    ),
)


def get_formal_interpretation_rule_families() -> tuple[str, ...]:
    return tuple(spec.rule_family for spec in _FAMILY_SPECS)


def _group_evidence_by_family(
    evidence_units: list[EvidenceUnit],
) -> dict[str, list[EvidenceUnit]]:
    grouped: dict[str, list[EvidenceUnit]] = {}
    for unit in evidence_units:
        grouped.setdefault(unit.rule_family, []).append(unit)
    return grouped


def _source_summary(evidence_units: list[EvidenceUnit]) -> list[str]:
    summaries: list[str] = []
    for unit in evidence_units:
        label = f"{unit.source_id} / {unit.rule_family} / {unit.risk_tier}"
        if unit.school:
            label += f" / {unit.school}"
        if label not in summaries:
            summaries.append(label)
    return summaries


def _body_for_supported(spec: _FamilySpec, units: list[EvidenceUnit]) -> str:
    summaries = "；".join(unit.summary for unit in units[:2])
    return (
        f"{spec.title}采用已审核证据单元作候选判断。"
        f"当前依据提示：{summaries}"
    )


def _body_for_unavailable(spec: _FamilySpec) -> str:
    return (
        f"{spec.title}目前没有可用的已审核证据单元支撑，"
        "只能保留为不可用结论。"
    )


def _school_view_signals(
    calculation: CalculationBundle | None,
    rule_family: str,
) -> list[str]:
    if calculation is None or rule_family not in {
        "pattern_strength",
        "useful_god_candidate",
        "blind_image_method",
        "remedy_boundary",
    }:
        return []
    views: list[str] = []
    for item in calculation.schools:
        view = (
            f"school_view:{item.school_id}:{item.reasoning.status}:"
            f"{item.reasoning.conclusion}"
        )
        if rule_family == "pattern_strength":
            view += f":patterns={','.join(item.preferred_pattern_ids)}"
        elif rule_family in {"useful_god_candidate", "remedy_boundary"}:
            view += (
                ":useful_gods="
                f"{','.join(item.preferred_useful_god_elements)}"
            )
        views.append(view)
    return views


def _school_disagreement_note(
    calculation: CalculationBundle | None,
    rule_family: str,
    calculation_status: CalculationStatus,
) -> str:
    if calculation is None or calculation_status != "disputed":
        return ""
    disagreement_rule_id = _SCHOOL_DISAGREEMENT_RULE_IDS.get(rule_family)
    if disagreement_rule_id is None or not any(
        disagreement_rule_id in item.reasoning.rule_ids
        for item in calculation.schools
    ):
        return ""
    views = _school_view_signals(calculation, rule_family)
    if not views:
        return ""
    return "School calculation disagreement preserved: " + "；".join(views)


def _relevant_conflicts(
    spec: _FamilySpec,
    units: list[EvidenceUnit],
    source_conflicts: list[SourceConflict],
) -> list[SourceConflict]:
    evidence_ids = {unit.evidence_id for unit in units}
    return [
        conflict
        for conflict in source_conflicts
        if conflict.rule_family == spec.rule_family
        and bool(evidence_ids.intersection(conflict.evidence_ids))
    ]


def _build_conclusion(
    chart: BaziChart,
    calculation: CalculationBundle | None,
    spec: _FamilySpec,
    units: list[EvidenceUnit],
    source_conflicts: list[SourceConflict],
) -> FormalConclusion:
    conclusion_id = f"formal_{spec.rule_family}"
    reasoning = (
        _family_reasoning(calculation, spec.rule_family)
        if calculation is not None
        else _not_computed_reasoning(spec.rule_family)
    )
    chart_signals = _compact(spec.signal_builder(chart))
    evidence_ids = [unit.evidence_id for unit in units]
    assumptions = [
        "four_pillars_complete",
        "classical_evidence_units_approved",
        f"rule_family:{spec.rule_family}",
        *reasoning.assumptions,
    ]
    relevant_conflicts = _relevant_conflicts(spec, units, source_conflicts)
    disagreement_note = "；".join(
        note
        for note in [
            *(conflict.reader_note for conflict in relevant_conflicts),
            _school_disagreement_note(
                calculation,
                spec.rule_family,
                reasoning.status,
            ),
            (
                "No approved evidence unit is available for this rule family."
                if not units
                else ""
            ),
        ]
        if note
    )
    trace = EvidenceTrace(
        trace_id=f"trace_{spec.rule_family}",
        conclusion_id=conclusion_id,
        chart_signals=chart_signals,
        evidence_ids=evidence_ids,
        assumptions=assumptions,
        disagreement_note=disagreement_note,
        calculation_status=reasoning.status,
        calculation_confidence=reasoning.confidence,
        supporting_signals=_compact(list(reasoning.supporting_signals)),
        opposing_signals=_compact(list(reasoning.opposing_signals)),
        rule_ids=_compact(list(reasoning.rule_ids)),
        missing_inputs=_compact(list(reasoning.missing_inputs)),
        school_views=_school_view_signals(calculation, spec.rule_family),
    )
    has_open_severe_conflict = any(
        conflict.severity == "severe" and conflict.resolution_status == "open"
        for conflict in relevant_conflicts
    )
    if reasoning.status == "disputed" or has_open_severe_conflict:
        strength = "disputed"
    elif reasoning.status == "not_computed":
        strength = "weakly_supported" if evidence_ids else "unavailable"
    elif reasoning.status == "indeterminate":
        strength = "weakly_supported"
    else:
        strength = "candidate" if evidence_ids else "unavailable"
    return FormalConclusion(
        conclusion_id=conclusion_id,
        title=spec.title,
        body=_body_for_supported(spec, units) if units else _body_for_unavailable(spec),
        rule_family=spec.rule_family,
        strength=strength,
        risk_tier=spec.risk_tier,
        trace=trace,
    )


def build_formal_interpretation(
    chart: BaziChart,
    evidence_units: list[EvidenceUnit],
    source_conflicts: list[SourceConflict] | None = None,
    calculation: CalculationBundle | None = None,
) -> ExpandedReportEvidence:
    calculation = calculation or build_legacy_not_computed_bundle(chart)
    validate_calculation_binding(chart, calculation)
    grouped = _group_evidence_by_family(evidence_units)
    conflicts = source_conflicts or []
    conclusions = [
        _build_conclusion(
            chart,
            calculation,
            spec,
            grouped.get(spec.rule_family, []),
            conflicts,
        )
        for spec in _FAMILY_SPECS
    ]
    unavailable = [
        conclusion.title
        for conclusion in conclusions
        if conclusion.strength == "unavailable"
    ]
    high_risk_notes = [
        unit.summary
        for unit in evidence_units
        if unit.risk_tier == "high_risk"
    ]
    return ExpandedReportEvidence(
        source_summary=_source_summary(evidence_units),
        formal_conclusions=conclusions,
        high_risk_notes=high_risk_notes,
        unavailable_conclusions=unavailable,
    )
