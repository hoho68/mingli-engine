from dataclasses import replace

from mingli_engine.bazi.analysis import (
    _bind_calculation_bundle,
    validate_calculation_binding,
)
from mingli_engine.bazi.constants import STEM_ELEMENT
from mingli_engine.bazi.facts import build_chart_facts
from mingli_engine.bazi.result_models import (
    CalculationBundle,
    LuckCycleResult,
    PatternCandidateResult,
    ReasonedResult,
    SchoolInterpretation,
    StrengthResult,
    UsefulGodCandidateResult,
)
from mingli_engine.bazi.versions import ENGINE_VERSION, RULESET_VERSION
from mingli_engine.models import BaziChart


LEGACY_REASON_CODE = "legacy_report_without_calculation_bundle"
_LEGACY_PILLAR_NAMES = {
    "year": "year",
    "month": "month",
    "day": "day",
    "hour": "hour",
    "time": "hour",
    "年柱": "year",
    "月柱": "month",
    "日柱": "day",
    "时柱": "hour",
}


def _status_token(status: str) -> str:
    return f"[calculation_status={status}]"


def _summary(status: str, text: str) -> str:
    return f"{_status_token(status)} {text}".rstrip()


def _not_computed_reasoning(stage: str) -> ReasonedResult:
    return ReasonedResult(
        status="not_computed",
        conclusion=f"{stage} was not computed in the legacy report.",
        confidence="low",
        missing_inputs=(LEGACY_REASON_CODE,),
        rule_ids=(LEGACY_REASON_CODE,),
    )


def apply_calculation_bundle(
    chart: BaziChart, bundle: CalculationBundle
) -> BaziChart:
    validate_calculation_binding(chart, bundle)
    ten_gods = ", ".join(
        f"{fact.pillar_name}:{fact.ten_god}" for fact in bundle.facts.exposed_stems
    )
    strength = bundle.strength
    patterns = [
        _summary(
            candidate.reasoning.status,
            f"{candidate.name}: {candidate.reasoning.conclusion}",
        )
        for candidate in bundle.patterns
    ]
    useful_gods = [
        _summary(
            candidate.reasoning.status,
            (
                f"{candidate.method}:{candidate.element}: "
                f"{candidate.reasoning.conclusion}"
            ),
        )
        for candidate in bundle.useful_gods
    ]
    luck_cycles = bundle.luck_cycles
    return replace(
        chart,
        pillars=[
            replace(pillar, hidden_stems=list(pillar.hidden_stems))
            for pillar in chart.pillars
        ],
        five_elements_summary=dict(chart.five_elements_summary),
        ten_gods_summary=_summary("computed", ten_gods),
        strength_assessment=_summary(
            strength.reasoning.status,
            (
                f"{strength.reasoning.conclusion} "
                f"label={strength.label}; score={strength.score:g}"
            ),
        ),
        pattern_candidates=patterns,
        useful_god_candidates=useful_gods,
        luck_cycle_summary=_summary(
            luck_cycles.reasoning.status,
            luck_cycles.reasoning.conclusion,
        ),
    )


def _normalize_legacy_fact_chart(chart: BaziChart) -> BaziChart:
    pillars = [
        replace(
            pillar,
            name=_LEGACY_PILLAR_NAMES.get(pillar.name, pillar.name),
        )
        for pillar in chart.pillars
    ]
    day_pillars = [pillar for pillar in pillars if pillar.name == "day"]
    day_master = chart.day_master
    if len(day_pillars) == 1:
        stem = day_pillars[0].heavenly_stem
        if chart.day_master == f"{stem}{STEM_ELEMENT.get(stem, '')}":
            day_master = stem
    return replace(chart, pillars=pillars, day_master=day_master)


def build_legacy_not_computed_bundle(chart: BaziChart) -> CalculationBundle:
    facts = build_chart_facts(_normalize_legacy_fact_chart(chart))
    strength = StrengthResult(
        reasoning=_not_computed_reasoning("strength"),
        score=0.0,
        lower_bound=0.0,
        upper_bound=0.0,
        label="",
        contributions=(),
    )
    patterns = (
        PatternCandidateResult(
            pattern_id="legacy.not_computed",
            name="Not computed",
            rank=1,
            reasoning=_not_computed_reasoning("patterns"),
            formation_conditions=(),
            damage_conditions=(),
            rescue_conditions=(),
        ),
    )
    useful_gods = (
        UsefulGodCandidateResult(
            method="legacy",
            element="",
            rank=1,
            reasoning=_not_computed_reasoning("useful_gods"),
        ),
    )
    luck_cycles = LuckCycleResult(
        reasoning=_not_computed_reasoning("luck_cycles"),
        forward=False,
        start_years=0,
        start_months=0,
        start_days=0,
        start_solar="",
        pillars=(),
        selected_year_relations=(),
    )
    schools = (
        SchoolInterpretation(
            school_id="legacy",
            profile_version="unversioned",
            reasoning=_not_computed_reasoning("school_interpretations"),
            preferred_pattern_ids=(),
            preferred_useful_god_elements=(),
        ),
    )
    bundle = CalculationBundle(
        engine_version=ENGINE_VERSION,
        ruleset_version=RULESET_VERSION,
        facts=facts,
        branch_relations=(),
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        luck_cycles=luck_cycles,
        schools=schools,
    )
    return _bind_calculation_bundle(bundle, chart)
