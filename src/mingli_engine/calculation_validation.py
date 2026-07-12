from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable

from mingli_engine.bazi.analysis import analyze_bazi_chart
from mingli_engine.bazi.legacy_adapter import build_legacy_not_computed_bundle
from mingli_engine.bazi.schools import load_school_profiles_config
from mingli_engine.bazi.versions import ENGINE_VERSION, RULESET_VERSION
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.classical_sources import (
    load_approved_evidence_units,
    load_source_conflicts,
)
from mingli_engine.formal_interpretation import (
    classify_chart_calculation_states,
)
from mingli_engine.models import BirthProfile
from mingli_engine.report_schema import build_report


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "bazi_calculation"
DEFAULT_SNAPSHOT_ROOTS = (
    REPO_ROOT / "src" / "mingli_engine" / "data" / "calculation",
    REPO_ROOT / "src" / "mingli_engine" / "data" / "classical_sources",
    DEFAULT_FIXTURE_DIR,
    REPO_ROOT / "docs" / "classical_sources",
)
PASS = "passed"
FAIL = "failed"
CHECK_NAMES = (
    "stages_present",
    "placeholder_integrity",
    "verified_fixture_count",
    "boundary_fixture_count",
    "three_school_profiles",
    "evidence_calculation_separation",
    "high_risk_guardrails",
    "no_persistence",
)
_PILLAR_ROLES = ("year", "month", "day", "hour")
_REQUIRED_BOUNDARY_CATEGORIES = frozenset(
    {
        "near_threshold_strength",
        "latent_vs_exposed",
        "pattern_strength_prerequisite_indeterminate",
        "damaged_pattern",
        "rescued_pattern",
        "incomplete_three_group",
        "school_disagreement",
        "solar_term_boundary",
        "luck_direction_boundary",
        "unknown_gender",
        "time_assumption_aware",
        "time_assumption_unsupported",
        "true_solar_assumption_recorded",
    }
)
_BOUNDARY_BEHAVIOR_CONTRACTS = {
    "near_threshold_strength": (
        "test_strength_boundary_fixture_executes_real_calculation",
        "near_threshold_range_asserted",
    ),
    "latent_vs_exposed": (
        "test_fixture_counterexamples_use_canonical_fact_builders",
        "latent_signal_does_not_count_as_exposed",
    ),
    "pattern_strength_prerequisite_indeterminate": (
        "test_fixture_counterexamples_use_canonical_fact_builders",
        "indeterminate_strength_blocks_pattern",
    ),
    "damaged_pattern": (
        "test_fixture_counterexamples_use_canonical_fact_builders",
        "pattern_damage_asserted",
    ),
    "rescued_pattern": (
        "test_fixture_counterexamples_use_canonical_fact_builders",
        "pattern_rescue_asserted",
    ),
    "incomplete_three_group": (
        "test_strength_boundary_fixture_executes_real_calculation",
        "incomplete_relation_asserted",
    ),
    "school_disagreement": (
        "test_strength_boundary_fixture_executes_real_calculation",
        "school_preferences_compared",
    ),
    "solar_term_boundary": (
        "test_provider_luck_cycles_match_frozen_regression_cases",
        "solar_term_boundary_output_asserted",
    ),
    "luck_direction_boundary": (
        "test_provider_luck_cycles_match_frozen_regression_cases",
        "luck_direction_and_start_asserted",
    ),
    "unknown_gender": (
        "test_strength_boundary_fixture_executes_real_calculation",
        "unknown_gender_luck_degradation_asserted",
    ),
    "time_assumption_aware": (
        "test_strength_boundary_fixture_executes_real_calculation",
        "aware_datetime_rejection_asserted",
    ),
    "time_assumption_unsupported": (
        "test_provider_rejects_aware_fixture_before_lunar_call",
        "aware_datetime_rejected_before_provider",
    ),
    "true_solar_assumption_recorded": (
        "test_strength_boundary_fixture_executes_real_calculation",
        "true_solar_assumption_recorded",
    ),
}
_STRENGTH_SEMANTIC_CATEGORIES = {
    "near_threshold": {"near_threshold_strength"},
    "incomplete_relation": {"incomplete_three_group"},
    "school_disagreement": {"school_disagreement"},
    "unknown_gender": {"unknown_gender"},
    "aware_datetime": {"time_assumption_aware"},
    "true_solar_assumption_recorded": {"true_solar_assumption_recorded"},
}


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("calculation fixture root must be an object")
    return payload


def _canonical_hash(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _contains_placeholder(value: object) -> bool:
    if isinstance(value, str):
        normalized = value.strip().casefold()
        return "?" in normalized or normalized in {"tbd", "todo", "placeholder"}
    if isinstance(value, dict):
        return any(_contains_placeholder(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_placeholder(item) for item in value)
    return False


def _verified_fixture_ready(fixture_dir: Path) -> bool:
    payload = _load_json_object(fixture_dir / "verified_charts.json")
    records = payload.get("records")
    if (
        payload.get("schema_version") != "bazi-verified-charts-v1"
        or payload.get("engine_version") != ENGINE_VERSION
        or payload.get("ruleset_version") != RULESET_VERSION
        or not isinstance(records, list)
        or len(records) < 30
        or _contains_placeholder(payload)
    ):
        return False
    independent = payload.get("independent_verification")
    if not isinstance(independent, dict) or independent.get("runtime_dependency") is not False:
        return False
    claim_boundary = independent.get("claim_boundary")
    if not isinstance(claim_boundary, str) or "chart_pillars only" not in claim_boundary:
        return False

    ids: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            return False
        record_id = record.get("id")
        input_data = record.get("input")
        versions = record.get("versions")
        expected = record.get("expected")
        verification = record.get("verification")
        if (
            not isinstance(record_id, str)
            or not record_id
            or not isinstance(input_data, dict)
            or input_data.get("birthplace") != "UTC+08 synthetic fixture"
            or versions
            != {
                "engine": ENGINE_VERSION,
                "ruleset": RULESET_VERSION,
                "primary_provider": "lunar-python==1.4.8",
                "independent_provider": "cnlunar==0.2.4",
            }
            or not isinstance(expected, dict)
            or not isinstance(verification, dict)
        ):
            return False
        ids.append(record_id)
        artifact = verification.get("cross_provider_artifact")
        pillars = artifact.get("pillars") if isinstance(artifact, dict) else None
        expected_pillars = expected.get("chart_pillars")
        downstream = verification.get("downstream_snapshot")
        if (
            verification.get("baseline_kind")
            != "chart_pillars_cross_provider_agreement"
            or verification.get("review_status") != "cross_provider_reviewed"
            or verification.get("review_scope") != ["chart_pillars"]
            or verification.get("synthetic_input") is not True
            or verification.get("contains_real_personal_data") is not False
            or not isinstance(artifact, dict)
            or artifact.get("provider") != "cnlunar"
            or artifact.get("version") != "0.2.4"
            or not isinstance(pillars, list)
            or len(pillars) != 4
            or [item.get("name") for item in pillars if isinstance(item, dict)]
            != list(_PILLAR_ROLES)
            or pillars != expected_pillars
            or verification.get("cross_provider_artifact_sha256")
            != _canonical_hash(artifact)
            or not isinstance(downstream, dict)
            or downstream.get("review_status")
            != "project_engine_frozen_snapshot"
            or downstream.get("scope")
            != ["facts", "relations", "strength", "patterns", "luck"]
            or downstream.get("engine_version") != ENGINE_VERSION
            or downstream.get("ruleset_version") != RULESET_VERSION
        ):
            return False
    return len(ids) == len(set(ids))


def _derived_boundary_categories(case: dict[str, Any], fixture_name: str) -> set[str]:
    if fixture_name == "strength_boundary_cases.json":
        expected = case.get("expected")
        semantic = expected.get("semantic") if isinstance(expected, dict) else None
        if not isinstance(semantic, dict):
            return set()
        kind = semantic.get("kind")
        if not isinstance(kind, str):
            return set()
        return set(_STRENGTH_SEMANTIC_CATEGORIES.get(kind, set()))
    if fixture_name == "pattern_counterexamples.json":
        derived: set[str] = set()
        if case.get("expected_damage"):
            derived.add("damaged_pattern")
        if case.get("expected_rescue"):
            derived.add("rescued_pattern")
        if case.get("expected_latent_context"):
            derived.add("latent_vs_exposed")
        if case.get("strength_status") == "indeterminate":
            derived.add("pattern_strength_prerequisite_indeterminate")
        return derived
    if "expected_error" in case:
        return {"time_assumption_unsupported"}
    if "boundary_case" in case:
        return {"solar_term_boundary"}
    return {"luck_direction_boundary"}


def _boundary_fixture_ready(fixture_dir: Path) -> bool:
    counted_ids: list[str] = []
    categories: set[str] = set()
    for fixture_name in (
        "strength_boundary_cases.json",
        "pattern_counterexamples.json",
        "luck_cycle_boundary_cases.json",
    ):
        payload = _load_json_object(fixture_dir / fixture_name)
        cases = payload.get("cases", payload.get("counterexamples"))
        if (
            payload.get("schema_version") != "bazi-boundary-fixtures-v1"
            or payload.get("synthetic_input") is not True
            or payload.get("contains_real_personal_data") is not False
            or not isinstance(cases, list)
            or _contains_placeholder(payload)
        ):
            return False
        for case in cases:
            if not isinstance(case, dict):
                return False
            metadata = case.get("fixture_metadata")
            if not isinstance(metadata, dict):
                return False
            if metadata.get("counts_toward_boundary_gate") is not True:
                continue
            derived = _derived_boundary_categories(case, fixture_name)
            expected_tests = {
                _BOUNDARY_BEHAVIOR_CONTRACTS[item][0] for item in derived
            }
            expected_behaviors = {
                _BOUNDARY_BEHAVIOR_CONTRACTS[item][1] for item in derived
            }
            case_id = case.get("id")
            if (
                not isinstance(case_id, str)
                or not case_id
                or not derived
                or metadata.get("synthetic_input") is not True
                or metadata.get("contains_real_personal_data") is not False
                or set(metadata.get("categories", [])) != derived
                or {metadata.get("execution_test")} != expected_tests
                or set(metadata.get("demonstrated_behaviors", []))
                != expected_behaviors
            ):
                return False
            counted_ids.append(case_id)
            categories.update(derived)
    return (
        len(counted_ids) >= 20
        and len(counted_ids) == len(set(counted_ids))
        and _REQUIRED_BOUNDARY_CATEGORIES <= categories
    )


def _snapshot(roots: tuple[Path, ...]) -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []
    for root in roots:
        resolved = root.resolve()
        if not resolved.is_dir():
            entries.append((str(resolved), "missing"))
            continue
        for path in sorted(item for item in resolved.rglob("*") if item.is_file()):
            entries.append((str(path), sha256(path.read_bytes()).hexdigest()))
    return tuple(entries)


def _reasonings(bundle: Any) -> tuple[Any, ...]:
    return (
        bundle.strength.reasoning,
        *(item.reasoning for item in bundle.patterns),
        *(item.reasoning for item in bundle.useful_gods),
        bundle.luck_cycles.reasoning,
        *(item.reasoning for item in bundle.schools),
    )


def _run_runtime_probes() -> dict[str, bool]:
    fixture = _load_json_object(DEFAULT_FIXTURE_DIR / "verified_charts.json")
    input_data = fixture["records"][0]["input"]
    profile = BirthProfile(**input_data)
    chart = calculate_bazi_chart(profile)
    birth_datetime = datetime.fromisoformat(
        f"{profile.birth_date}T{profile.birth_time}:00"
    )
    calculation = analyze_bazi_chart(chart, birth_datetime=birth_datetime)
    legacy = build_legacy_not_computed_bundle(chart)
    evidence_before = load_approved_evidence_units()
    conflicts = load_source_conflicts()
    legacy_report = build_report(chart, legacy)
    report = build_report(chart, calculation)
    legacy_interpretation = legacy_report.expanded_evidence
    calculated_interpretation = report.expanded_evidence
    evidence_after = load_approved_evidence_units()

    config = load_school_profiles_config()
    reasonings = _reasonings(calculation)
    stages_present = (
        calculation.engine_version == ENGINE_VERSION
        and calculation.ruleset_version == RULESET_VERSION
        and calculation.facts is not None
        and isinstance(calculation.branch_relations, tuple)
        and calculation.strength is not None
        and bool(calculation.patterns)
        and bool(calculation.useful_gods)
        and calculation.luck_cycles is not None
        and len(calculation.schools) == 3
        and all(item.profile_version == config.version for item in calculation.schools)
        and all(item.status in {"computed", "indeterminate", "disputed", "not_computed"} for item in reasonings)
        and all(item.rule_ids for item in reasonings)
    )

    severe_open_families = {
        conflict.rule_family
        for conflict in conflicts
        if conflict.severity == "severe" and conflict.resolution_status == "open"
    }
    legacy_states = classify_chart_calculation_states(legacy)
    placeholder_integrity = all(
        state == "not_computed" for state in legacy_states.values()
    ) and all(
        conclusion.strength != "candidate"
        and (
            conclusion.strength == "disputed"
            if conclusion.rule_family in severe_open_families
            else conclusion.strength in {"weakly_supported", "unavailable"}
        )
        for conclusion in legacy_interpretation.formal_conclusions
    )

    expected_ids = sorted(item.evidence_id for item in evidence_before)
    legacy_ids = sorted(
        evidence_id
        for conclusion in legacy_interpretation.formal_conclusions
        for evidence_id in conclusion.trace.evidence_ids
    )
    calculated_ids = sorted(
        evidence_id
        for conclusion in calculated_interpretation.formal_conclusions
        for evidence_id in conclusion.trace.evidence_ids
    )
    evidence_calculation_separation = (
        expected_ids == legacy_ids == calculated_ids
        and expected_ids == sorted(item.evidence_id for item in evidence_after)
        and any(
            conclusion.strength == "candidate"
            for conclusion in calculated_interpretation.formal_conclusions
        )
        and all(
            conclusion.strength != "candidate"
            for conclusion in legacy_interpretation.formal_conclusions
            if conclusion.trace.calculation_status == "not_computed"
        )
    )

    high_risk = next(
        (
            conclusion
            for conclusion in report.expanded_evidence.formal_conclusions
            if conclusion.rule_family == "high_risk_signal"
        ),
        None,
    )
    high_risk_actions = [
        item
        for item in report.action_reflection_items
        if "high_risk_signal" in item.rule_families
    ]
    high_risk_guardrails = (
        bool(severe_open_families)
        and high_risk is not None
        and high_risk.strength == "disputed"
        and bool(high_risk.trace.disagreement_note)
        and bool(report.report_evidence_audit.open_conflicts)
        and bool(high_risk_actions)
        and all(item.stop_boundary for item in high_risk_actions)
    )
    three_school_profiles = (
        config.version == "school-profiles-v1"
        and config.enabled == ("ziping", "liang_xiangrun", "duan")
        and set(config.profiles) == set(config.enabled)
    )
    return {
        "stages_present": stages_present,
        "placeholder_integrity": placeholder_integrity,
        "three_school_profiles": three_school_profiles,
        "evidence_calculation_separation": evidence_calculation_separation,
        "high_risk_guardrails": high_risk_guardrails,
    }


def _safe_check(check: Callable[[], bool]) -> bool:
    try:
        return bool(check())
    except Exception:
        return False


def build_calculation_checks(
    *,
    fixture_dir: Path | None = None,
    snapshot_roots: tuple[Path, ...] | None = None,
) -> dict[str, str]:
    resolved_fixture_dir = fixture_dir or DEFAULT_FIXTURE_DIR
    roots = snapshot_roots or DEFAULT_SNAPSHOT_ROOTS
    before: tuple[tuple[str, str], ...] | None
    try:
        before = _snapshot(roots)
    except Exception:
        before = None

    runtime = {
        "stages_present": False,
        "placeholder_integrity": False,
        "three_school_profiles": False,
        "evidence_calculation_separation": False,
        "high_risk_guardrails": False,
    }
    try:
        runtime.update(_run_runtime_probes())
    except Exception:
        pass

    checks = {
        "stages_present": runtime["stages_present"],
        "placeholder_integrity": runtime["placeholder_integrity"],
        "verified_fixture_count": _safe_check(
            lambda: _verified_fixture_ready(resolved_fixture_dir)
        ),
        "boundary_fixture_count": _safe_check(
            lambda: _boundary_fixture_ready(resolved_fixture_dir)
        ),
        "three_school_profiles": runtime["three_school_profiles"],
        "evidence_calculation_separation": runtime[
            "evidence_calculation_separation"
        ],
        "high_risk_guardrails": runtime["high_risk_guardrails"],
        "no_persistence": False,
    }
    try:
        after = _snapshot(roots)
        checks["no_persistence"] = before is not None and before == after
    except Exception:
        checks["no_persistence"] = False
    return {
        name: PASS if checks[name] else FAIL
        for name in CHECK_NAMES
    }
