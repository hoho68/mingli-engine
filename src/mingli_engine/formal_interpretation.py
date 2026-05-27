from collections.abc import Callable
from dataclasses import dataclass

from mingli_engine.models import (
    BaziChart,
    EvidenceTrace,
    EvidenceUnit,
    ExpandedReportEvidence,
    FormalConclusion,
)


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
)


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


def _build_conclusion(
    chart: BaziChart,
    spec: _FamilySpec,
    units: list[EvidenceUnit],
) -> FormalConclusion:
    conclusion_id = f"formal_{spec.rule_family}"
    chart_signals = spec.signal_builder(chart)
    evidence_ids = [unit.evidence_id for unit in units]
    assumptions = [
        "four_pillars_complete",
        "classical_evidence_units_approved",
        f"rule_family:{spec.rule_family}",
    ]
    if not units:
        trace = EvidenceTrace(
            trace_id=f"trace_{spec.rule_family}",
            conclusion_id=conclusion_id,
            chart_signals=chart_signals,
            evidence_ids=[],
            assumptions=assumptions,
            disagreement_note="No approved evidence unit is available for this rule family.",
        )
        return FormalConclusion(
            conclusion_id=conclusion_id,
            title=spec.title,
            body=_body_for_unavailable(spec),
            rule_family=spec.rule_family,
            strength="unavailable",
            risk_tier=spec.risk_tier,
            trace=trace,
        )

    trace = EvidenceTrace(
        trace_id=f"trace_{spec.rule_family}",
        conclusion_id=conclusion_id,
        chart_signals=chart_signals,
        evidence_ids=evidence_ids,
        assumptions=assumptions,
        disagreement_note="",
    )
    strength = "candidate" if chart_signals else "weakly_supported"
    return FormalConclusion(
        conclusion_id=conclusion_id,
        title=spec.title,
        body=_body_for_supported(spec, units),
        rule_family=spec.rule_family,
        strength=strength,
        risk_tier=spec.risk_tier,
        trace=trace,
    )


def build_formal_interpretation(
    chart: BaziChart,
    evidence_units: list[EvidenceUnit],
) -> ExpandedReportEvidence:
    grouped = _group_evidence_by_family(evidence_units)
    conclusions = [
        _build_conclusion(chart, spec, grouped.get(spec.rule_family, []))
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
