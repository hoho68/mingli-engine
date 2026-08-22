from datetime import datetime
from hashlib import blake2b
from hmac import compare_digest
import json
from secrets import token_bytes
from threading import Lock
from weakref import ReferenceType, ref

from mingli_engine.bazi.branch_relations import detect_branch_relations
from mingli_engine.bazi.calibrated_families import (
    calculate_blind_image_method,
    calculate_remedy_boundary,
    calculate_taboo_god_candidates,
)
from mingli_engine.bazi.facts import build_chart_facts
from mingli_engine.bazi.luck_cycles import calculate_luck_cycles
from mingli_engine.bazi.patterns import calculate_pattern_candidates
from mingli_engine.bazi.result_models import CalculationBundle
from mingli_engine.bazi.schools import interpret_with_enabled_schools
from mingli_engine.bazi.strength import calculate_strength
from mingli_engine.bazi.useful_gods import calculate_useful_god_candidates
from mingli_engine.bazi.versions import ENGINE_VERSION, RULESET_VERSION
from mingli_engine.models import BaziChart


PROVENANCE_ERROR = "calculation bundle is unbound or does not match chart input"

_PROVENANCE_KEY = token_bytes(32)
_PROVENANCE_LOCK = Lock()
_PROVENANCE: dict[
    int, tuple[ReferenceType[CalculationBundle], bytes]
] = {}


def _chart_context_digest(chart: BaziChart) -> bytes:
    profile = chart.birth_profile
    source = chart.chart_source
    context = (
        (
            profile.calendar_type,
            profile.birth_date,
            profile.birth_time,
            profile.birthplace,
            profile.gender,
            profile.focus_topic,
        ),
        (
            source.source_type,
            source.source_note,
            source.calendar_assumption,
            source.timezone_assumption,
            source.solar_terms_assumption,
            source.true_solar_time_applied,
            source.confidence,
        ),
        tuple(
            (
                pillar.name,
                pillar.heavenly_stem,
                pillar.earthly_branch,
                tuple(pillar.hidden_stems),
                pillar.ten_god,
                pillar.element,
            )
            for pillar in chart.pillars
        ),
        chart.day_master,
        tuple(sorted(chart.five_elements_summary.items())),
    )
    encoded = json.dumps(
        context,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return blake2b(encoded, key=_PROVENANCE_KEY, digest_size=32).digest()


def _bind_calculation_bundle(
    bundle: CalculationBundle, chart: BaziChart
) -> CalculationBundle:
    """Keep only a keyed digest in a process-local, weak-lifetime binding."""
    bundle_id = id(bundle)

    def discard(dead_reference: ReferenceType[CalculationBundle]) -> None:
        with _PROVENANCE_LOCK:
            current = _PROVENANCE.get(bundle_id)
            if current is not None and current[0] is dead_reference:
                _PROVENANCE.pop(bundle_id, None)

    bundle_reference = ref(bundle, discard)
    digest = _chart_context_digest(chart)
    with _PROVENANCE_LOCK:
        current = _PROVENANCE.get(bundle_id)
        if current is not None and current[0]() is not bundle:
            raise RuntimeError("calculation bundle identity collision")
        _PROVENANCE[bundle_id] = (bundle_reference, digest)
    return bundle


def validate_calculation_binding(
    chart: BaziChart, bundle: CalculationBundle
) -> None:
    with _PROVENANCE_LOCK:
        current = _PROVENANCE.get(id(bundle))
        if current is None or current[0]() is not bundle:
            raise ValueError(PROVENANCE_ERROR)
        expected_digest = current[1]
    if not compare_digest(expected_digest, _chart_context_digest(chart)):
        raise ValueError(PROVENANCE_ERROR)


_require_calculation_bundle_binding = validate_calculation_binding


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
    taboo_gods = calculate_taboo_god_candidates(
        facts,
        strength,
        patterns,
        schools,
    )
    blind_images = calculate_blind_image_method(
        facts,
        relations,
        strength,
        schools,
    )
    remedy_boundary = calculate_remedy_boundary(
        strength,
        useful_gods,
        schools,
    )
    bundle = CalculationBundle(
        engine_version=ENGINE_VERSION,
        ruleset_version=RULESET_VERSION,
        facts=facts,
        branch_relations=relations,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        luck_cycles=luck_cycles,
        schools=schools,
        taboo_gods=taboo_gods,
        blind_images=blind_images,
        remedy_boundary=remedy_boundary,
    )
    return _bind_calculation_bundle(bundle, chart)
