from datetime import datetime

from mingli_engine.bazi.branch_relations import detect_branch_relations
from mingli_engine.bazi.facts import build_chart_facts
from mingli_engine.bazi.luck_cycles import calculate_luck_cycles
from mingli_engine.bazi.patterns import calculate_pattern_candidates
from mingli_engine.bazi.result_models import CalculationBundle
from mingli_engine.bazi.schools import interpret_with_enabled_schools
from mingli_engine.bazi.strength import calculate_strength
from mingli_engine.bazi.useful_gods import calculate_useful_god_candidates
from mingli_engine.models import BaziChart


ENGINE_VERSION = "bazi-core-v1"
RULESET_VERSION = "ziping-v1"


def analyze_bazi_chart(
    chart: BaziChart,
    *,
    birth_datetime: datetime | None = None,
    selected_year: int | None = None,
) -> CalculationBundle:
    facts = build_chart_facts(chart)
    relations = detect_branch_relations(chart)
    strength = calculate_strength(facts, relations)
    patterns = calculate_pattern_candidates(facts, strength, relations)
    useful_gods = calculate_useful_god_candidates(facts, strength, patterns)
    luck_cycles = calculate_luck_cycles(
        chart,
        birth_datetime=birth_datetime,
        selected_year=selected_year,
    )
    schools = interpret_with_enabled_schools(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    return CalculationBundle(
        engine_version=ENGINE_VERSION,
        ruleset_version=RULESET_VERSION,
        facts=facts,
        branch_relations=relations,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        luck_cycles=luck_cycles,
        schools=schools,
    )
