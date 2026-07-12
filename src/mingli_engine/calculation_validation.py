from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, replace
from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Callable, Final

from mingli_engine.bazi.analysis import analyze_bazi_chart
from mingli_engine.bazi.branch_relations import (
    detect_branch_relations,
    detect_branch_relations_for_positions,
)
from mingli_engine.bazi.constants import (
    BRANCHES,
    HIDDEN_STEMS,
    STEM_ELEMENT,
    STEM_POLARITY,
    STEMS,
)
from mingli_engine.bazi.facts import build_chart_facts, ten_god
from mingli_engine.bazi.legacy_adapter import build_legacy_not_computed_bundle
from mingli_engine.bazi.luck_cycles import calculate_luck_cycles
from mingli_engine.bazi.patterns import (
    PATTERN_DAMAGE,
    PATTERN_RESCUE,
    TEN_GOD_PATTERN_NAMES,
    calculate_pattern_candidates,
)
from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    ChartFacts,
    HiddenStemFact,
    ReasonedResult,
    RootFact,
    StemFact,
    StrengthResult,
)
from mingli_engine.bazi.schools import (
    interpret_with_enabled_schools,
    load_school_profiles_config,
)
from mingli_engine.bazi.strength import calculate_strength, load_strength_config
from mingli_engine.bazi.useful_gods import calculate_useful_god_candidates
from mingli_engine.bazi.versions import ENGINE_VERSION, RULESET_VERSION
from mingli_engine.calendar_provider import calculate_provider_luck_cycles
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
    REPO_ROOT / "src" / "mingli_engine",
    DEFAULT_FIXTURE_DIR,
    REPO_ROOT / "docs" / "classical_sources",
)
_WORKSPACE_EXCLUDED_DIRS = frozenset({".git", ".venv", ".uv_cache_tmp"})
_CACHE_DIR_NAMES = frozenset(
    {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
)
_PERSONAL_ARTIFACT_MARKERS = (
    "birth-profile",
    "birth_profile",
    "personal-profile",
    "personal_profile",
    "personal-report",
    "personal_report",
    "report-output",
    "report_output",
)
_PROJECT_OUTPUT_MARKERS = frozenset(
    {
        "project-output",
        "project_output",
        "generated-reports",
        "generated_reports",
        "report-output",
        "report_output",
    }
)
_GIT_RECURSIVE_SURFACES = (
    "refs",
    "logs",
    "worktrees",
    "modules",
    "rebase-apply",
    "rebase-merge",
    "sequencer",
    "objects/info",
    "objects/pack",
)
PASS = "passed"
FAIL = "failed"
CHECK_NAMES: Final[tuple[str, ...]] = (
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
_PATTERN_DAY_MASTER = STEMS[0]
_TEN_GOD_STEM = {ten_god(_PATTERN_DAY_MASTER, stem): stem for stem in STEMS}
_MONTH_BRANCH_BY_MAIN = {
    ten_god(_PATTERN_DAY_MASTER, hidden[0][0]): branch
    for branch, hidden in HIDDEN_STEMS.items()
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


def _json_value(value: object) -> object:
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _execute_verified_record(record: dict[str, Any]) -> None:
    input_data = record["input"]
    expected = record["expected"]
    profile = BirthProfile(**input_data)
    birth_datetime = datetime.fromisoformat(
        f"{profile.birth_date}T{profile.birth_time}:00"
    )
    first_chart = calculate_bazi_chart(profile)
    first_bundle = analyze_bazi_chart(
        first_chart,
        birth_datetime=birth_datetime,
        selected_year=2030,
    )
    second_chart = calculate_bazi_chart(profile)
    second_bundle = analyze_bazi_chart(
        second_chart,
        birth_datetime=birth_datetime,
        selected_year=2030,
    )
    _require(first_chart == second_chart, "verified chart is not deterministic")
    _require(first_bundle == second_bundle, "verified analysis is not deterministic")
    _require(
        first_bundle.engine_version == ENGINE_VERSION
        and first_bundle.ruleset_version == RULESET_VERSION,
        "verified analysis version mismatch",
    )
    _require(
        [
            {
                "name": pillar.name,
                "gan_zhi": f"{pillar.heavenly_stem}{pillar.earthly_branch}",
            }
            for pillar in first_chart.pillars
        ]
        == expected["chart_pillars"],
        "verified chart pillar mismatch",
    )
    _require(
        _json_value(asdict(first_bundle.facts)) == expected["facts"],
        "verified facts mismatch",
    )
    _require(
        _json_value([asdict(item) for item in first_bundle.branch_relations])
        == expected["relations"],
        "verified relations mismatch",
    )
    strength = expected["strength"]
    _require(
        {
            "status": first_bundle.strength.reasoning.status,
            "label": first_bundle.strength.label,
            "score": first_bundle.strength.score,
            "lower_bound": first_bundle.strength.lower_bound,
            "upper_bound": first_bundle.strength.upper_bound,
        }
        == strength,
        "verified strength mismatch",
    )
    _require(
        [
            {
                "pattern_id": item.pattern_id,
                "status": item.reasoning.status,
                "rank": item.rank,
            }
            for item in first_bundle.patterns
        ]
        == expected["patterns"],
        "verified pattern mismatch",
    )
    luck = first_bundle.luck_cycles
    _require(
        {
            "status": luck.reasoning.status,
            "forward": luck.forward,
            "start_years": luck.start_years,
            "start_months": luck.start_months,
            "start_days": luck.start_days,
            "start_solar": luck.start_solar,
            "pillars": [asdict(item) for item in luck.pillars],
        }
        == expected["luck"],
        "verified luck mismatch",
    )


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
            or any(
                not isinstance(item, dict)
                or set(item) != {"name", "gan_zhi"}
                or not isinstance(item.get("gan_zhi"), str)
                or len(item["gan_zhi"]) != 2
                or item["gan_zhi"][0] not in STEMS
                or item["gan_zhi"][1] not in BRANCHES
                for item in pillars
            )
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
        _execute_verified_record(record)
    return len(ids) == len(set(ids))


def _chart_facts_from_json(payload: dict[str, Any]) -> ChartFacts:
    return ChartFacts(
        day_master=payload["day_master"],
        month_branch=payload["month_branch"],
        exposed_stems=tuple(StemFact(**item) for item in payload["exposed_stems"]),
        hidden_stems=tuple(
            HiddenStemFact(**item) for item in payload["hidden_stems"]
        ),
        roots=tuple(RootFact(**item) for item in payload["roots"]),
        twelve_growth_by_pillar=tuple(
            tuple(item) for item in payload["twelve_growth_by_pillar"]
        ),
        assumptions=tuple(payload["assumptions"]),
    )


def _relations_from_json(
    payload: list[dict[str, Any]],
) -> tuple[BranchRelationResult, ...]:
    return tuple(BranchRelationResult(**item) for item in payload)


def _pattern_stem_fact(pillar_name: str, stem: str) -> StemFact:
    return StemFact(
        pillar_name=pillar_name,
        stem=stem,
        element=STEM_ELEMENT[stem],
        polarity=STEM_POLARITY[stem],
        ten_god=ten_god(_PATTERN_DAY_MASTER, stem),
    )


def _pattern_hidden_facts(
    pillar_name: str,
    branch: str,
) -> tuple[HiddenStemFact, ...]:
    return tuple(
        HiddenStemFact(
            pillar_name=pillar_name,
            branch=branch,
            stem=stem,
            role=role,
            element=STEM_ELEMENT[stem],
            polarity=STEM_POLARITY[stem],
            ten_god=ten_god(_PATTERN_DAY_MASTER, stem),
        )
        for stem, role in HIDDEN_STEMS[branch]
    )


def _execute_pattern_boundary(case: dict[str, Any]) -> set[str]:
    signals = tuple(case["signals"])
    pattern_name = TEN_GOD_PATTERN_NAMES[case["pattern_ten_god"]]
    forbidden = {*PATTERN_DAMAGE[pattern_name], *PATTERN_RESCUE[pattern_name]}
    neutral_god = next(
        god
        for god in _TEN_GOD_STEM
        if god not in forbidden and god not in signals
    )
    assigned = tuple(_TEN_GOD_STEM[god] for god in signals)
    neutral_stem = _TEN_GOD_STEM[neutral_god]
    non_day_stems = (*assigned, *((neutral_stem,) * (3 - len(assigned))))
    month_branch = _MONTH_BRANCH_BY_MAIN[case["pattern_ten_god"]]
    latent = tuple(
        fact
        for index, branch in enumerate(case.get("latent_branches", ()))
        for fact in _pattern_hidden_facts(("year", "hour")[index % 2], branch)
    )
    facts = ChartFacts(
        day_master=_PATTERN_DAY_MASTER,
        month_branch=month_branch,
        exposed_stems=(
            _pattern_stem_fact("year", non_day_stems[0]),
            _pattern_stem_fact("month", non_day_stems[1]),
            _pattern_stem_fact("day", _PATTERN_DAY_MASTER),
            _pattern_stem_fact("hour", non_day_stems[2]),
        ),
        hidden_stems=(*_pattern_hidden_facts("month", month_branch), *latent),
        roots=(),
        twelve_growth_by_pillar=(),
        assumptions=("fixture:canonical-pattern-facts",),
    )
    strength_status = case.get("strength_status", "computed")
    strength = StrengthResult(
        reasoning=ReasonedResult(
            status=strength_status,
            conclusion="fixture strength prerequisite",
            confidence="high" if strength_status == "computed" else "low",
            rule_ids=("strength.fixture_boundary",),
        ),
        score=0.0,
        lower_bound=0.0,
        upper_bound=0.0,
        label="boundary fixture",
        contributions=(),
    )
    candidate = calculate_pattern_candidates(facts, strength)[0]
    damage = tuple(item.rsplit(":", 1)[-1] for item in candidate.damage_conditions)
    rescue = tuple(item.rsplit(":", 1)[-1] for item in candidate.rescue_conditions)
    _require(damage == tuple(case["expected_damage"]), "pattern damage mismatch")
    _require(rescue == tuple(case["expected_rescue"]), "pattern rescue mismatch")
    categories: set[str] = set()
    if damage:
        _require(candidate.reasoning.status == "disputed", "damage status mismatch")
        categories.add("damaged_pattern")
    if rescue:
        categories.add("rescued_pattern")
    latent_context = case.get("expected_latent_context")
    if latent_context:
        _require(not damage, "latent signal counted as exposed damage")
        _require(
            all(
                any(
                    assumption.startswith("latent_damage_context:hidden:")
                    and assumption.endswith(f":{god}")
                    for assumption in candidate.reasoning.assumptions
                )
                for god in latent_context
            ),
            "latent context mismatch",
        )
        categories.add("latent_vs_exposed")
    if strength_status == "indeterminate":
        _require(
            candidate.reasoning.status == "indeterminate",
            "pattern prerequisite status mismatch",
        )
        categories.add("pattern_strength_prerequisite_indeterminate")
    _require(bool(categories), "pattern boundary has no executed behavior")
    return categories


def _validate_strength_result(result: StrengthResult, expected: dict[str, Any]) -> None:
    _require(result.reasoning.status == expected["status"], "strength status mismatch")
    _require(result.label == expected["label"], "strength label mismatch")
    if expected.get("sensitivity_boundary"):
        for field_name in ("score", "lower_bound", "upper_bound"):
            lower, upper = expected[f"{field_name}_range"]
            _require(
                lower <= getattr(result, field_name) <= upper,
                f"strength {field_name} range mismatch",
            )
    else:
        _require(result.score == expected["score"], "strength score mismatch")
        _require(
            result.lower_bound == expected["lower_bound"],
            "strength lower-bound mismatch",
        )
        _require(
            result.upper_bound == expected["upper_bound"],
            "strength upper-bound mismatch",
        )


def _execute_strength_boundary(case: dict[str, Any]) -> set[str]:
    execution = case["execution"]
    chart = None
    birth_datetime = None
    if execution["kind"] == "chart_facts":
        facts = _chart_facts_from_json(execution["facts"])
        relations = _relations_from_json(execution["relations"])
    else:
        _require(execution["kind"] == "full_chart", "unsupported strength input")
        chart = calculate_bazi_chart(BirthProfile(**execution["input"]))
        if execution.get("chart_source_overrides"):
            chart = replace(
                chart,
                chart_source=replace(
                    chart.chart_source,
                    **execution["chart_source_overrides"],
                ),
            )
        facts = build_chart_facts(chart)
        relations = detect_branch_relations(chart)
        birth_datetime = datetime.fromisoformat(execution["birth_datetime"])
    result = calculate_strength(facts, relations)
    _validate_strength_result(result, case["expected"]["strength"])
    semantic = case["expected"]["semantic"]
    kind = semantic["kind"]
    categories = set(_STRENGTH_SEMANTIC_CATEGORIES.get(kind, set()))
    _require(bool(categories), "unsupported strength semantic")
    if kind == "near_threshold":
        crossed = tuple(
            threshold
            for threshold in load_strength_config().thresholds.values()
            if result.lower_bound <= threshold < result.upper_bound
        )
        _require(crossed == (semantic["threshold"],), "threshold semantic mismatch")
        _require(result.reasoning.status == "indeterminate", "threshold status mismatch")
    elif kind == "incomplete_relation":
        _require(len(relations) == 1, "incomplete relation count mismatch")
        relation = relations[0]
        positions_by_pillar = {
            item.pillar_name: item.branch
            for item in facts.hidden_stems
            if item.role == "main"
        }
        detected = detect_branch_relations_for_positions(
            tuple(positions_by_pillar.items())
        )
        _require(
            not any(
                item.relation_type == relation.relation_type
                and set(item.branches) >= set(relation.branches)
                for item in detected
            ),
            "incomplete relation was complete",
        )
        _require(relation.state == "incomplete", "relation state mismatch")
        _require(not relation.transformed_element, "incomplete relation transformed")
        _require(bool(relation.conditions), "incomplete relation lacks conditions")
        _require(
            relation.blockers == (f"missing {semantic['missing_branch']}",),
            "incomplete relation blocker mismatch",
        )
        _require(
            any(
                relation.rule_id in rule_id and "no_numeric_modifier" in rule_id
                for rule_id in result.reasoning.rule_ids
            ),
            "incomplete relation affected numeric strength",
        )
    elif kind == "school_disagreement":
        patterns = calculate_pattern_candidates(facts, result, relations)
        useful_gods = calculate_useful_god_candidates(facts, result, patterns)
        schools = interpret_with_enabled_schools(
            facts=facts,
            strength=result,
            patterns=patterns,
            useful_gods=useful_gods,
        )
        actual_views = [
            {
                "school_id": item.school_id,
                "status": item.reasoning.status,
                "preferred_pattern_ids": list(item.preferred_pattern_ids),
                "preferred_useful_god_elements": list(
                    item.preferred_useful_god_elements
                ),
            }
            for item in schools
        ]
        _require(actual_views == semantic["school_results"], "school view mismatch")
        _require(
            all(
                semantic["cross_school_rule_id"] in item.reasoning.rule_ids
                for item in schools
            ),
            "school disagreement rule mismatch",
        )
        _require(
            len({item.preferred_pattern_ids for item in schools}) > 1,
            "school preferences do not disagree",
        )
    elif kind == "unknown_gender":
        _require(chart is not None and birth_datetime is not None, "missing chart")
        luck = calculate_luck_cycles(chart, birth_datetime=birth_datetime)
        _require(
            luck.reasoning.status == semantic["luck_status"]
            and list(luck.reasoning.missing_inputs) == semantic["missing_inputs"],
            "unknown-gender degradation mismatch",
        )
    elif kind == "aware_datetime":
        _require(chart is not None and birth_datetime is not None, "missing chart")
        try:
            calculate_luck_cycles(chart, birth_datetime=birth_datetime)
        except ValueError as error:
            _require(str(error) == semantic["error"], "aware-time error mismatch")
        else:
            raise ValueError("aware datetime was accepted")
    else:
        _require(kind == "true_solar_assumption_recorded", "unknown semantic")
        if chart is None:
            raise ValueError("missing true-solar chart")
        _require(chart.chart_source.true_solar_time_applied is True, "solar flag mismatch")
        _require(
            semantic["assumption"] in result.reasoning.assumptions,
            "true-solar assumption mismatch",
        )
    return categories


def _execute_luck_boundary(case: dict[str, Any]) -> tuple[set[str], Any | None]:
    birth_datetime = datetime.fromisoformat(case["birth_datetime"])
    if "expected_error" in case:
        _require(birth_datetime.utcoffset() is not None, "expected aware datetime")
        try:
            calculate_provider_luck_cycles(
                birth_datetime,
                case["gender"],
                sect=case["sect"],
                count=case["count"],
            )
        except ValueError as error:
            _require(
                str(error) == case["expected_error"]["message"],
                "provider rejection mismatch",
            )
        else:
            raise ValueError("aware provider datetime was accepted")
        return {"time_assumption_unsupported"}, None
    result = calculate_provider_luck_cycles(
        birth_datetime,
        case["gender"],
        sect=case["sect"],
        count=case.get("count", 2),
    )
    expected = case["expected"]
    _require(result.forward is expected["forward"], "luck direction mismatch")
    _require(result.start_years == expected["start_years"], "luck years mismatch")
    _require(result.start_months == expected["start_months"], "luck months mismatch")
    _require(result.start_days == expected["start_days"], "luck days mismatch")
    _require(result.start_hours == expected["start_hours"], "luck hours mismatch")
    _require(result.start_solar == expected["start_solar"], "luck start mismatch")
    _require(
        result.pillars == tuple(tuple(item) for item in expected["pillars"]),
        "luck pillars mismatch",
    )
    category = "solar_term_boundary" if "boundary_case" in case else "luck_direction_boundary"
    return {category}, result


def _validate_solar_boundary_group(
    cases: list[dict[str, Any]],
    results: dict[str, Any],
) -> None:
    boundary_cases = [case for case in cases if "boundary_case" in case]
    _require(len(boundary_cases) == 3, "solar boundary case count mismatch")
    transition = datetime.fromisoformat(
        boundary_cases[0]["boundary_case"]["transition"]
    )
    by_delta: dict[int, Any] = {}
    for case in boundary_cases:
        _require(
            datetime.fromisoformat(case["boundary_case"]["transition"])
            == transition,
            "solar transition mismatch",
        )
        delta = int(
            (
                datetime.fromisoformat(case["birth_datetime"]) - transition
            ).total_seconds()
        )
        _require(
            case["boundary_case"]["phase"]
            == {-1: "before", 0: "exact", 1: "after"}.get(delta),
            "solar phase mismatch",
        )
        by_delta[delta] = results[case["id"]]
    _require(set(by_delta) == {-1, 0, 1}, "solar offsets mismatch")
    _require(by_delta[-1].forward is not by_delta[0].forward, "solar direction unchanged")
    _require(by_delta[-1].pillars != by_delta[0].pillars, "solar pillars unchanged")
    _require(by_delta[0].forward is by_delta[1].forward, "solar exact/after drift")
    _require(
        tuple(item[1] for item in by_delta[0].pillars)
        == tuple(item[1] for item in by_delta[1].pillars),
        "solar exact/after pillars drift",
    )


def _execute_boundary_case(
    case: dict[str, Any],
    fixture_name: str,
) -> tuple[set[str], Any | None]:
    if fixture_name == "strength_boundary_cases.json":
        return _execute_strength_boundary(case), None
    if fixture_name == "pattern_counterexamples.json":
        return _execute_pattern_boundary(case), None
    _require(
        fixture_name == "luck_cycle_boundary_cases.json",
        "unsupported boundary fixture",
    )
    return _execute_luck_boundary(case)


def _boundary_fixture_ready(fixture_dir: Path) -> bool:
    tracked_ids: list[str] = []
    counted_ids: list[str] = []
    categories: set[str] = set()
    luck_cases: list[dict[str, Any]] = []
    luck_results: dict[str, Any] = {}
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
            counts_toward_gate = metadata.get("counts_toward_boundary_gate")
            if not isinstance(counts_toward_gate, bool):
                return False
            derived, execution_result = _execute_boundary_case(case, fixture_name)
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
            tracked_ids.append(case_id)
            if fixture_name == "luck_cycle_boundary_cases.json":
                luck_cases.append(case)
                if execution_result is not None:
                    luck_results[case_id] = execution_result
            if counts_toward_gate:
                counted_ids.append(case_id)
                categories.update(derived)
    _validate_solar_boundary_group(luck_cases, luck_results)
    return (
        len(counted_ids) >= 20
        and len(counted_ids) == len(set(counted_ids))
        and len(tracked_ids) == len(set(tracked_ids))
        and _REQUIRED_BOUNDARY_CATEGORIES <= categories
    )


def _content_snapshot(roots: tuple[Path, ...]) -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []
    for root in roots:
        resolved = root.resolve()
        if not resolved.is_dir():
            entries.append((str(resolved), "missing"))
            continue
        for path in sorted(item for item in resolved.rglob("*") if item.is_file()):
            entries.append((str(path), sha256(path.read_bytes()).hexdigest()))
    return tuple(entries)


def _workspace_snapshot(
    workspace_root: Path,
) -> tuple[tuple[str, int, int], ...]:
    root = workspace_root.resolve()
    if not root.is_dir():
        raise ValueError("workspace root is unavailable")
    entries: list[tuple[str, int, int]] = []
    for current, dir_names, file_names in os.walk(root, followlinks=False):
        dir_names[:] = sorted(
            name for name in dir_names if name not in _WORKSPACE_EXCLUDED_DIRS
        )
        current_path = Path(current)
        for file_name in sorted(file_names):
            path = current_path / file_name
            if not path.is_file() or path.is_symlink():
                continue
            stat = path.stat()
            entries.append(
                (
                    path.relative_to(root).as_posix(),
                    stat.st_size,
                    stat.st_mtime_ns,
                )
            )
    return tuple(entries)


def _metadata_entry(
    path: Path,
    root: Path,
    kind: str,
) -> tuple[str, str, int, int]:
    stat = path.stat()
    return (
        path.relative_to(root).as_posix(),
        kind,
        stat.st_size,
        stat.st_mtime_ns,
    )


def _artifact_snapshot(
    workspace_root: Path,
) -> tuple[tuple[str, str, int, int], ...]:
    root = workspace_root.resolve()
    artifacts: list[tuple[str, str, int, int]] = []
    for current, dir_names, file_names in os.walk(root, followlinks=False):
        dir_names[:] = sorted(dir_names)
        current_path = Path(current)
        current_parts = tuple(
            part.casefold() for part in current_path.relative_to(root).parts
        )
        in_virtualenv = bool(current_parts) and current_parts[0] == ".venv"
        in_project_output = any(
            part in _PROJECT_OUTPUT_MARKERS for part in current_parts
        )
        for dir_name in dir_names:
            normalized = dir_name.casefold()
            personal = any(
                marker in normalized for marker in _PERSONAL_ARTIFACT_MARKERS
            )
            project_output = normalized in _PROJECT_OUTPUT_MARKERS
            cache = normalized in _CACHE_DIR_NAMES and (
                not in_virtualenv or in_project_output or project_output
            )
            if personal or project_output or cache:
                artifacts.append(
                    _metadata_entry(current_path / dir_name, root, "directory")
                )
        for file_name in sorted(file_names):
            normalized = file_name.casefold()
            personal = any(
                marker in normalized for marker in _PERSONAL_ARTIFACT_MARKERS
            )
            cache = normalized.endswith(".pyc") and (
                not in_virtualenv or in_project_output
            )
            if personal or cache:
                artifacts.append(
                    _metadata_entry(current_path / file_name, root, "file")
                )
    return tuple(sorted(artifacts))


def _subtree_metadata_snapshot(
    workspace_root: Path,
    subtree_name: str,
) -> tuple[tuple[str, str, int, int], ...]:
    root = workspace_root.resolve()
    subtree = root / subtree_name
    if not subtree.exists():
        return ()
    entries = [_metadata_entry(subtree, root, "directory")]
    for current, dir_names, file_names in os.walk(subtree, followlinks=False):
        dir_names[:] = sorted(dir_names)
        current_path = Path(current)
        entries.extend(
            _metadata_entry(current_path / name, root, "directory")
            for name in dir_names
        )
        entries.extend(
            _metadata_entry(current_path / name, root, "file")
            for name in sorted(file_names)
            if (current_path / name).is_file()
            and not (current_path / name).is_symlink()
        )
    return tuple(sorted(entries))


def _git_metadata_snapshot(
    workspace_root: Path,
) -> tuple[tuple[str, str, int, int], ...]:
    root = workspace_root.resolve()
    git_root = root / ".git"
    if not git_root.is_dir():
        return ()
    entries = [_metadata_entry(git_root, root, "directory")]
    entries.extend(
        _metadata_entry(path, root, "file")
        for path in sorted(git_root.iterdir())
        if path.is_file() and not path.is_symlink()
    )
    entries.extend(
        _metadata_entry(path, root, "directory")
        for path in sorted(git_root.iterdir())
        if path.is_dir() and not path.is_symlink()
    )
    for relative in _GIT_RECURSIVE_SURFACES:
        entries.extend(
            _subtree_metadata_snapshot(root, f".git/{relative}")
        )
    objects_root = git_root / "objects"
    if objects_root.is_dir():
        entries.extend(
            _metadata_entry(path, root, "directory")
            for path in sorted(objects_root.iterdir())
            if path.is_dir() and not path.is_symlink()
        )
    return tuple(sorted(set(entries)))


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


def calculation_checks_pass(checks: Mapping[str, str] | None) -> bool:
    if checks is None:
        return False
    snapshot = dict(checks)
    return set(snapshot) == set(CHECK_NAMES) and all(
        snapshot[name] == PASS for name in CHECK_NAMES
    )


def build_calculation_checks(
    *,
    fixture_dir: Path | None = None,
    snapshot_roots: tuple[Path, ...] | None = None,
    workspace_root: Path | None = None,
) -> dict[str, str]:
    resolved_fixture_dir = fixture_dir or DEFAULT_FIXTURE_DIR
    resolved_workspace_root = workspace_root or REPO_ROOT
    if snapshot_roots is not None:
        roots = snapshot_roots
    elif fixture_dir is not None:
        roots = tuple(
            resolved_fixture_dir if root == DEFAULT_FIXTURE_DIR else root
            for root in DEFAULT_SNAPSHOT_ROOTS
        )
    else:
        roots = DEFAULT_SNAPSHOT_ROOTS
    before_content: tuple[tuple[str, str], ...] | None
    before_workspace: tuple[tuple[str, int, int], ...] | None
    before_artifacts: tuple[tuple[str, str, int, int], ...] | None
    before_git: tuple[tuple[str, str, int, int], ...] | None
    before_uv_cache: tuple[tuple[str, str, int, int], ...] | None
    try:
        before_content = _content_snapshot(roots)
        before_workspace = _workspace_snapshot(resolved_workspace_root)
        before_artifacts = _artifact_snapshot(resolved_workspace_root)
        before_git = _git_metadata_snapshot(resolved_workspace_root)
        before_uv_cache = _subtree_metadata_snapshot(
            resolved_workspace_root,
            ".uv_cache_tmp",
        )
    except Exception:
        before_content = None
        before_workspace = None
        before_artifacts = None
        before_git = None
        before_uv_cache = None

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
        after_content = _content_snapshot(roots)
        after_workspace = _workspace_snapshot(resolved_workspace_root)
        after_artifacts = _artifact_snapshot(resolved_workspace_root)
        after_git = _git_metadata_snapshot(resolved_workspace_root)
        after_uv_cache = _subtree_metadata_snapshot(
            resolved_workspace_root,
            ".uv_cache_tmp",
        )
        checks["no_persistence"] = (
            before_content is not None
            and before_workspace is not None
            and before_artifacts is not None
            and before_git is not None
            and before_uv_cache is not None
            and before_content == after_content
            and before_workspace == after_workspace
            and before_artifacts == after_artifacts
            and before_git == after_git
            and before_uv_cache == after_uv_cache
        )
    except Exception:
        checks["no_persistence"] = False
    return {
        name: PASS if checks[name] else FAIL
        for name in CHECK_NAMES
    }
