import builtins
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
import json
import os
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

import mingli_engine.bazi as bazi_api
import mingli_engine.bazi.analysis as analysis
from mingli_engine.bazi.analysis import analyze_bazi_chart
from mingli_engine.bazi.branch_relations import detect_branch_relations
from mingli_engine.bazi.constants import (
    BRANCHES,
    STEM_ELEMENT,
    STEM_POLARITY,
    STEMS,
)
from mingli_engine.bazi.facts import build_chart_facts
from mingli_engine.bazi.legacy_adapter import (
    apply_calculation_bundle,
    build_legacy_not_computed_bundle,
)
from mingli_engine.bazi.luck_cycles import calculate_luck_cycles
from mingli_engine.bazi.patterns import calculate_pattern_candidates
from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    ChartFacts,
    HiddenStemFact,
    RootFact,
    StemFact,
)
from mingli_engine.bazi.schools import interpret_with_enabled_schools
from mingli_engine.bazi.strength import calculate_strength
from mingli_engine.bazi.useful_gods import calculate_useful_god_candidates
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile


PROVENANCE_ERROR = "calculation bundle is unbound or does not match chart input"
FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "bazi_calculation"
VERIFIED_FIXTURE_PATH = FIXTURE_DIR / "verified_charts.json"
BOUNDARY_FIXTURE_PATHS = (
    FIXTURE_DIR / "strength_boundary_cases.json",
    FIXTURE_DIR / "pattern_counterexamples.json",
    FIXTURE_DIR / "luck_cycle_boundary_cases.json",
)
EXPECTED_BOUNDARY_CATEGORIES = {
    "near_threshold_strength",
    "latent_vs_exposed",
    "damaged_pattern",
    "rescued_pattern",
    "incomplete_three_groups",
    "school_disagreement",
    "solar_term_before",
    "solar_term_exact",
    "solar_term_after",
    "unknown_gender",
    "time_assumption_aware",
    "time_assumption_unsupported",
    "true_solar_assumption_recorded",
}
CANONICAL_PILLAR_ROLES = ("year", "month", "day", "hour")
ELEMENT_NAMES = dict(
    zip(("木", "火", "土", "金", "水"), ("wood", "fire", "earth", "metal", "water"), strict=True)
)
BOUNDARY_BEHAVIOR_CONTRACTS = {
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
    "incomplete_three_groups": (
        "test_strength_boundary_fixture_executes_real_calculation",
        "incomplete_relation_asserted",
    ),
    "school_disagreement": (
        "test_strength_boundary_fixture_executes_real_calculation",
        "school_preferences_compared",
    ),
    "solar_term_before": (
        "test_provider_luck_cycles_match_frozen_regression_cases",
        "solar_term_boundary_output_asserted",
    ),
    "solar_term_exact": (
        "test_provider_luck_cycles_match_frozen_regression_cases",
        "solar_term_boundary_output_asserted",
    ),
    "solar_term_after": (
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


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _json_value(value: object) -> object:
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


def _verified_records() -> list[dict[str, Any]]:
    if not VERIFIED_FIXTURE_PATH.exists():
        return []
    payload = _load_json(VERIFIED_FIXTURE_PATH)
    records = payload.get("records")
    assert isinstance(records, list)
    return records


def _verified_parameters() -> list[Any]:
    records = _verified_records()
    if not records:
        return [pytest.param(None, id="verified_fixture_missing")]
    return [pytest.param(record, id=str(record["id"])) for record in records]


def _strength_boundary_cases() -> list[dict[str, Any]]:
    payload = _load_json(FIXTURE_DIR / "strength_boundary_cases.json")
    return payload["cases"]


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


def _contains_placeholder(value: object) -> bool:
    if isinstance(value, str):
        normalized = value.strip().casefold()
        return "?" in normalized or normalized in {"tbd", "todo", "placeholder"}
    if isinstance(value, dict):
        return any(_contains_placeholder(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_placeholder(item) for item in value)
    return False


def _canonical_artifact_hash(artifact: dict[str, Any]) -> str:
    encoded = json.dumps(
        artifact,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _validate_cross_provider_record(record: dict[str, Any]) -> None:
    verification = record["verification"]
    artifact = verification["cross_provider_artifact"]
    pillars = artifact["pillars"]
    assert verification["baseline_kind"] == (
        "chart_pillars_cross_provider_agreement"
    )
    assert verification["review_status"] == "cross_provider_reviewed"
    assert verification["review_scope"] == ["chart_pillars"]
    assert artifact["provider"] == "cnlunar"
    assert artifact["version"] == "0.2.4"
    assert artifact["api"] == "cnlunar.Lunar(datetime)"
    assert artifact["method"] == (
        "year8Char, month8Char, day8Char, twohour8Char"
    )
    assert set(artifact) == {"provider", "version", "api", "method", "pillars"}
    assert len(pillars) == 4
    assert tuple(item["name"] for item in pillars) == CANONICAL_PILLAR_ROLES
    assert all(
        len(item["gan_zhi"]) == 2
        and item["gan_zhi"][0] in STEMS
        and item["gan_zhi"][1] in BRANCHES
        for item in pillars
    )
    assert pillars == record["expected"]["chart_pillars"]
    assert verification["cross_provider_artifact_sha256"] == (
        _canonical_artifact_hash(artifact)
    )
    assert verification["downstream_snapshot"] == {
        "review_status": "project_engine_frozen_snapshot",
        "scope": ["facts", "relations", "strength", "patterns", "luck"],
        "engine_version": "bazi-core-v1",
        "ruleset_version": "ziping-v1",
    }


def _derived_verified_coverage(record: dict[str, Any]) -> dict[str, Any]:
    pillars = record["expected"]["chart_pillars"]
    by_role = {item["name"]: item["gan_zhi"] for item in pillars}
    assert tuple(item["name"] for item in pillars) == CANONICAL_PILLAR_ROLES
    day_stem = by_role["day"][0]
    month_branch = by_role["month"][1]
    branches = [item["gan_zhi"][1] for item in pillars]
    assert record["expected"]["facts"]["day_master"] == day_stem
    assert record["expected"]["facts"]["month_branch"] == month_branch
    return {
        "day_master": day_stem,
        "day_master_element": ELEMENT_NAMES[STEM_ELEMENT[day_stem]],
        "day_master_polarity": STEM_POLARITY[day_stem],
        "month_branch": month_branch,
        "forward": record["expected"]["luck"]["forward"],
        "repeated_branch": len(set(branches)) < len(branches),
        "no_relation_chart": not record["expected"]["relations"],
    }


def _profile(**overrides: str) -> BirthProfile:
    values = {
        "calendar_type": "gregorian",
        "birth_date": "1992-08-18",
        "birth_time": "09:30",
        "birthplace": "Shanghai",
        "gender": "female",
        "focus_topic": "career",
    }
    values.update(overrides)
    return BirthProfile(**values)


def _chart(**overrides: str):
    return calculate_bazi_chart(_profile(**overrides))


def _record_real_stage_calls(monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
    stage_names = (
        "build_chart_facts",
        "detect_branch_relations",
        "calculate_strength",
        "calculate_pattern_candidates",
        "calculate_useful_god_candidates",
        "calculate_luck_cycles",
        "interpret_with_enabled_schools",
    )
    for name in stage_names:
        real_stage = getattr(analysis, name)

        def record(
            *args: object,
            _name: str = name,
            _stage=real_stage,
            **kwargs: object,
        ):
            calls.append((_name, args, kwargs))
            return _stage(*args, **kwargs)

        monkeypatch.setattr(analysis, name, record)
    return calls


def _forbid_file_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    real_open = builtins.open

    def guarded_open(file, mode="r", *args, **kwargs):
        assert not any(flag in mode for flag in "wax+"), (
            f"analysis attempted a file write: {file!r} mode={mode!r}"
        )
        return real_open(file, mode, *args, **kwargs)

    def reject_path_write(*_args, **_kwargs):
        pytest.fail("analysis attempted a pathlib file write")

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(Path, "write_text", reject_path_write)
    monkeypatch.setattr(Path, "write_bytes", reject_path_write)


def test_public_exports_do_not_create_calendar_provider_import_cycle() -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(Path.cwd() / "src")

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import mingli_engine.calendar_provider; "
                "from mingli_engine.bazi import analyze_bazi_chart; "
                "assert callable(analyze_bazi_chart)"
            ),
        ],
        cwd=Path.cwd(),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr


def test_versions_are_available_from_dependency_neutral_and_public_modules() -> None:
    from mingli_engine.bazi import ENGINE_VERSION, RULESET_VERSION
    from mingli_engine.bazi.versions import (
        ENGINE_VERSION as NEUTRAL_ENGINE_VERSION,
    )
    from mingli_engine.bazi.versions import (
        RULESET_VERSION as NEUTRAL_RULESET_VERSION,
    )

    assert ENGINE_VERSION == NEUTRAL_ENGINE_VERSION == "bazi-core-v1"
    assert RULESET_VERSION == NEUTRAL_RULESET_VERSION == "ziping-v1"


def test_verified_chart_fixture_schema_privacy_review_and_coverage() -> None:
    payload = _load_json(VERIFIED_FIXTURE_PATH)
    records = payload["records"]

    assert payload["schema_version"] == "bazi-verified-charts-v1"
    assert payload["engine_version"] == "bazi-core-v1"
    assert payload["ruleset_version"] == "ziping-v1"
    assert payload["primary_provider"] == {
        "name": "lunar-python",
        "version": "1.4.8",
    }
    assert payload["independent_verification"] == {
        "provider": "cnlunar",
        "version": "0.2.4",
        "api": "cnlunar.Lunar(datetime)",
        "method": "year8Char, month8Char, day8Char, twohour8Char",
        "installation_scope": "temporary_target_only",
        "runtime_dependency": False,
        "command_description": (
            "python -m pip install --target <temporary-directory> "
            "cnlunar==0.2.4; prepend that directory to PYTHONPATH only for "
            "the one-time fixture verification process"
        ),
        "claim_boundary": (
            "Cross-provider review covers chart_pillars only; downstream "
            "expectations are frozen project-engine snapshots."
        ),
    }
    assert payload["selection"]["method"] == "deterministic_exact_set_cover"
    assert isinstance(records, list)
    assert len(records) >= 30
    assert not _contains_placeholder(payload)
    serialized = json.dumps(payload, ensure_ascii=False).casefold()
    assert "human_reviewed" not in serialized
    assert "authoritative" not in serialized

    ids = [record["id"] for record in records]
    assert len(ids) == len(set(ids))
    assert all(record["input"]["birthplace"] == "UTC+08 synthetic fixture" for record in records)
    assert all(record["verification"]["synthetic_input"] is True for record in records)
    assert all(
        record["verification"]["contains_real_personal_data"] is False
        for record in records
    )
    for record in records:
        _validate_cross_provider_record(record)
    assert all(
        record["versions"]
        == {
            "engine": "bazi-core-v1",
            "ruleset": "ziping-v1",
            "primary_provider": "lunar-python==1.4.8",
            "independent_provider": "cnlunar==0.2.4",
        }
        for record in records
    )
    assert all(
        set(record["expected"]["strength"])
        == {"status", "label", "score", "lower_bound", "upper_bound"}
        for record in records
    )

    derived = [_derived_verified_coverage(record) for record in records]
    for record, actual in zip(records, derived, strict=True):
        assert record["coverage"]["day_master_element"] == actual[
            "day_master_element"
        ]
        assert record["coverage"]["day_master_polarity"] == actual[
            "day_master_polarity"
        ]
        assert record["coverage"]["repeated_branch"] is actual[
            "repeated_branch"
        ]
        assert record["coverage"]["no_relation_chart"] is actual[
            "no_relation_chart"
        ]
    day_masters = {item["day_master"] for item in derived}
    month_branches = {item["month_branch"] for item in derived}
    directions = {item["forward"] for item in derived}
    polarities = {item["day_master_polarity"] for item in derived}
    elements = {item["day_master_element"] for item in derived}
    assert day_masters == set("甲乙丙丁戊己庚辛壬癸")
    assert month_branches == set("子丑寅卯辰巳午未申酉戌亥")
    assert directions == {True, False}
    assert polarities == {"yin", "yang"}
    assert elements == {"wood", "fire", "earth", "metal", "water"}
    assert any(item["repeated_branch"] for item in derived)
    assert any(item["no_relation_chart"] for item in derived)


def test_cross_provider_contract_rejects_empty_or_mismatched_artifacts() -> None:
    record = _verified_records()[0]
    empty = deepcopy(record)
    empty["verification"]["cross_provider_artifact"]["pillars"] = []
    with pytest.raises(AssertionError):
        _validate_cross_provider_record(empty)

    mismatched = deepcopy(record)
    mismatched["verification"]["cross_provider_artifact"]["pillars"][0][
        "gan_zhi"
    ] = mismatched["expected"]["chart_pillars"][1]["gan_zhi"]
    with pytest.raises(AssertionError):
        _validate_cross_provider_record(mismatched)


def test_boundary_fixture_schemas_counts_privacy_and_categories() -> None:
    all_cases: list[dict[str, Any]] = []
    for path in BOUNDARY_FIXTURE_PATHS:
        payload = _load_json(path)
        assert payload["schema_version"] == "bazi-boundary-fixtures-v1"
        assert payload["synthetic_input"] is True
        assert payload["contains_real_personal_data"] is False
        cases = payload.get("cases", payload.get("counterexamples"))
        assert isinstance(cases, list)
        for case in cases:
            metadata = case["fixture_metadata"]
            assert metadata["synthetic_input"] is True
            assert metadata["contains_real_personal_data"] is False
            assert isinstance(metadata["categories"], list)
            assert metadata["categories"]
            assert isinstance(metadata["counts_toward_boundary_gate"], bool)
            assert isinstance(metadata["demonstrated_behaviors"], list)
            assert metadata["demonstrated_behaviors"]
            for category in metadata["categories"]:
                execution_test, demonstrated_behavior = (
                    BOUNDARY_BEHAVIOR_CONTRACTS[category]
                )
                assert metadata["execution_test"] == execution_test
                assert demonstrated_behavior in metadata["demonstrated_behaviors"]
            assert not _contains_placeholder(case)
            if path.name == "strength_boundary_cases.json":
                expected_strength = case["expected"]["strength"]
                range_keys = {
                    key for key in expected_strength if key.endswith("_range")
                }
                assert bool(range_keys) is bool(
                    expected_strength.get("sensitivity_boundary")
                )
        all_cases.extend(cases)

    counted = [
        case
        for case in all_cases
        if case["fixture_metadata"]["counts_toward_boundary_gate"]
    ]
    counted_ids = [case["id"] for case in counted]
    categories = {
        category
        for case in counted
        for category in case["fixture_metadata"]["categories"]
    }
    assert len(counted) >= 20
    assert len(counted_ids) == len(set(counted_ids))
    assert EXPECTED_BOUNDARY_CATEGORIES <= categories
    assert sum(
        case["fixture_metadata"]["execution_test"]
        == "test_strength_boundary_fixture_executes_real_calculation"
        for case in counted
    ) == 6


@pytest.mark.parametrize("record", _verified_parameters())
def test_verified_chart_pipeline_matches_frozen_cross_provider_fixture(
    record: dict[str, Any] | None,
) -> None:
    assert record is not None
    input_data = record["input"]
    expected = record["expected"]
    profile = BirthProfile(**input_data)
    birth_datetime = datetime.fromisoformat(
        f"{input_data['birth_date']}T{input_data['birth_time']}:00"
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

    assert first_chart == second_chart
    assert first_bundle == second_bundle
    assert [
        {
            "name": pillar.name,
            "gan_zhi": f"{pillar.heavenly_stem}{pillar.earthly_branch}",
        }
        for pillar in first_chart.pillars
    ] == expected["chart_pillars"]
    assert _json_value(asdict(first_bundle.facts)) == expected["facts"]
    assert _json_value(
        [asdict(relation) for relation in first_bundle.branch_relations]
    ) == expected["relations"]

    strength = expected["strength"]
    assert first_bundle.strength.reasoning.status == strength["status"]
    assert first_bundle.strength.label == strength["label"]
    assert first_bundle.strength.score == strength["score"]
    assert first_bundle.strength.lower_bound == strength["lower_bound"]
    assert first_bundle.strength.upper_bound == strength["upper_bound"]

    assert [
        {
            "pattern_id": pattern.pattern_id,
            "status": pattern.reasoning.status,
            "rank": pattern.rank,
        }
        for pattern in first_bundle.patterns
    ] == expected["patterns"]
    assert {
        "status": first_bundle.luck_cycles.reasoning.status,
        "forward": first_bundle.luck_cycles.forward,
        "start_years": first_bundle.luck_cycles.start_years,
        "start_months": first_bundle.luck_cycles.start_months,
        "start_days": first_bundle.luck_cycles.start_days,
        "start_solar": first_bundle.luck_cycles.start_solar,
        "pillars": [asdict(pillar) for pillar in first_bundle.luck_cycles.pillars],
    } == expected["luck"]


@pytest.mark.parametrize(
    "case",
    _strength_boundary_cases(),
    ids=lambda case: case["id"],
)
def test_strength_boundary_fixture_executes_real_calculation(
    case: dict[str, Any],
) -> None:
    execution = case["execution"]
    chart = None
    birth_datetime = None
    if execution["kind"] == "chart_facts":
        facts = _chart_facts_from_json(execution["facts"])
        relations = _relations_from_json(execution["relations"])
    else:
        assert execution["kind"] == "full_chart"
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
    expected_strength = case["expected"]["strength"]
    assert result.reasoning.status == expected_strength["status"]
    assert result.label == expected_strength["label"]
    if expected_strength.get("sensitivity_boundary"):
        for field_name in ("score", "lower_bound", "upper_bound"):
            lower, upper = expected_strength[f"{field_name}_range"]
            assert lower <= getattr(result, field_name) <= upper
    else:
        assert result.score == expected_strength["score"]
        assert result.lower_bound == expected_strength["lower_bound"]
        assert result.upper_bound == expected_strength["upper_bound"]

    semantic = case["expected"]["semantic"]
    if semantic["kind"] == "near_threshold":
        assert expected_strength["sensitivity_boundary"] is True
        assert result.lower_bound <= semantic["threshold"] < result.upper_bound
    elif semantic["kind"] == "incomplete_relation":
        assert len(relations) == 1
        assert relations[0].relation_type == semantic["relation_type"]
        assert relations[0].state == semantic["state"]
        available_branches = {item.branch for item in facts.hidden_stems}
        assert set(relations[0].branches) <= available_branches
        assert semantic["missing_branch"] not in available_branches
        assert f"missing {semantic['missing_branch']}" in relations[0].blockers
        assert semantic["rule_id"] in result.reasoning.rule_ids[-1]
    elif semantic["kind"] == "school_disagreement":
        patterns = calculate_pattern_candidates(facts, result, relations)
        useful_gods = calculate_useful_god_candidates(facts, result, patterns)
        schools = interpret_with_enabled_schools(
            facts=facts,
            strength=result,
            patterns=patterns,
            useful_gods=useful_gods,
        )
        actual_schools = [
            {
                "school_id": school.school_id,
                "status": school.reasoning.status,
                "preferred_pattern_ids": list(school.preferred_pattern_ids),
                "preferred_useful_god_elements": list(
                    school.preferred_useful_god_elements
                ),
            }
            for school in schools
        ]
        assert actual_schools == semantic["school_results"]
        assert len(
            {
                (
                    tuple(item["preferred_pattern_ids"]),
                    tuple(item["preferred_useful_god_elements"]),
                )
                for item in actual_schools
            }
        ) > 1
    elif semantic["kind"] == "unknown_gender":
        assert chart is not None
        assert birth_datetime is not None
        luck = calculate_luck_cycles(chart, birth_datetime=birth_datetime)
        assert luck.reasoning.status == semantic["luck_status"]
        assert list(luck.reasoning.missing_inputs) == semantic["missing_inputs"]
    elif semantic["kind"] == "aware_datetime":
        assert chart is not None
        assert birth_datetime is not None
        assert birth_datetime.utcoffset() is not None
        with pytest.raises(ValueError, match=semantic["error"]):
            calculate_luck_cycles(chart, birth_datetime=birth_datetime)
    else:
        assert semantic["kind"] == "true_solar_assumption_recorded"
        assert chart is not None
        assert chart.chart_source.true_solar_time_applied is True
        assert semantic["assumption"] in result.reasoning.assumptions


def test_complete_profile_pipeline_has_exact_order_versions_and_immutable_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chart = _chart()
    birth_datetime = datetime(1992, 8, 18, 9, 30)
    calls = _record_real_stage_calls(monkeypatch)
    _forbid_file_writes(monkeypatch)

    bundle = analyze_bazi_chart(
        chart,
        birth_datetime=birth_datetime,
        selected_year=2030,
    )

    assert [name for name, _args, _kwargs in calls] == [
        "build_chart_facts",
        "detect_branch_relations",
        "calculate_strength",
        "calculate_pattern_candidates",
        "calculate_useful_god_candidates",
        "calculate_luck_cycles",
        "interpret_with_enabled_schools",
    ]
    assert calls[0][1:] == ((chart,), {})
    assert calls[1][1:] == ((chart,), {})
    assert calls[2][1] == (bundle.facts, bundle.branch_relations)
    assert calls[2][2] == {}
    assert calls[3][1] == (
        bundle.facts,
        bundle.strength,
        bundle.branch_relations,
    )
    assert calls[3][2] == {}
    assert calls[4][1] == (
        bundle.facts,
        bundle.strength,
        bundle.patterns,
    )
    assert calls[4][2] == {}
    assert calls[5][1:] == (
        (chart,),
        {"birth_datetime": birth_datetime, "selected_year": 2030},
    )
    assert calls[6][1] == ()
    assert calls[6][2] == {
        "facts": bundle.facts,
        "strength": bundle.strength,
        "patterns": bundle.patterns,
        "useful_gods": bundle.useful_gods,
    }
    assert bundle.engine_version == "bazi-core-v1"
    assert bundle.ruleset_version == "ziping-v1"
    assert bundle.strength.reasoning.status == "computed"
    assert bundle.luck_cycles.reasoning.status == "computed"
    assert bundle.patterns
    assert bundle.useful_gods
    assert bundle.schools
    assert isinstance(bundle.branch_relations, tuple)
    assert isinstance(bundle.patterns, tuple)
    assert isinstance(bundle.useful_gods, tuple)
    assert isinstance(bundle.schools, tuple)
    with pytest.raises(FrozenInstanceError):
        bundle.engine_version = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        bundle.facts.day_master = "changed"  # type: ignore[misc]


def test_unsupported_gender_degrades_only_luck_prerequisite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chart = _chart(gender="unspecified")
    calls = _record_real_stage_calls(monkeypatch)
    _forbid_file_writes(monkeypatch)

    bundle = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1992, 8, 18, 9, 30),
        selected_year=2030,
    )

    assert [name for name, _args, _kwargs in calls] == [
        "build_chart_facts",
        "detect_branch_relations",
        "calculate_strength",
        "calculate_pattern_candidates",
        "calculate_useful_god_candidates",
        "calculate_luck_cycles",
        "interpret_with_enabled_schools",
    ]
    assert bundle.strength.reasoning.status == "computed"
    assert any(item.reasoning.status == "computed" for item in bundle.patterns)
    assert any(item.reasoning.status == "computed" for item in bundle.useful_gods)
    assert all(item.reasoning.status != "not_computed" for item in bundle.schools)
    assert bundle.luck_cycles.reasoning.status == "not_computed"
    assert bundle.luck_cycles.reasoning.missing_inputs == ("supported_gender",)


def test_legacy_bundle_preserves_only_lossless_facts_and_marks_semantics_not_computed() -> (
    None
):
    chart = _chart()
    poisoned_summaries = replace(
        chart,
        ten_gods_summary="must not be parsed",
        strength_assessment="[calculation_status=computed] forged",
        pattern_candidates=["forged pattern"],
        useful_god_candidates=["forged useful god"],
        luck_cycle_summary="forged luck",
    )

    bundle = build_legacy_not_computed_bundle(poisoned_summaries)

    reason = "legacy_report_without_calculation_bundle"
    assert bundle.engine_version == "bazi-core-v1"
    assert bundle.ruleset_version == "ziping-v1"
    assert bundle.facts == build_chart_facts(chart)
    assert bundle.branch_relations == ()
    assert bundle.strength.reasoning.status == "not_computed"
    assert bundle.strength.reasoning.missing_inputs == (reason,)
    assert bundle.strength.score == 0.0
    assert bundle.strength.contributions == ()
    assert bundle.patterns[0].reasoning.status == "not_computed"
    assert bundle.patterns[0].reasoning.missing_inputs == (reason,)
    assert bundle.useful_gods[0].reasoning.status == "not_computed"
    assert bundle.useful_gods[0].reasoning.missing_inputs == (reason,)
    assert bundle.luck_cycles.reasoning.status == "not_computed"
    assert bundle.luck_cycles.reasoning.missing_inputs == (reason,)
    assert bundle.luck_cycles.pillars == ()
    assert bundle.schools[0].reasoning.status == "not_computed"
    assert bundle.schools[0].reasoning.missing_inputs == (reason,)


def test_legacy_adapter_is_one_way_and_prefixes_every_summary_with_status() -> None:
    chart = _chart()
    bundle = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1992, 8, 18, 9, 30),
        selected_year=2030,
    )

    adapted = apply_calculation_bundle(chart, bundle)

    assert adapted is not chart
    assert adapted.birth_profile == chart.birth_profile
    assert adapted.pillars == chart.pillars
    assert adapted.ten_gods_summary.startswith("[calculation_status=computed]")
    assert adapted.strength_assessment.startswith(
        f"[calculation_status={bundle.strength.reasoning.status}]"
    )
    assert len(adapted.pattern_candidates) == len(bundle.patterns)
    assert all(
        summary.startswith(
            f"[calculation_status={candidate.reasoning.status}]"
        )
        for summary, candidate in zip(
            adapted.pattern_candidates, bundle.patterns, strict=True
        )
    )
    assert len(adapted.useful_god_candidates) == len(bundle.useful_gods)
    assert all(
        summary.startswith(
            f"[calculation_status={candidate.reasoning.status}]"
        )
        for summary, candidate in zip(
            adapted.useful_god_candidates, bundle.useful_gods, strict=True
        )
    )
    assert adapted.luck_cycle_summary.startswith(
        f"[calculation_status={bundle.luck_cycles.reasoning.status}]"
    )


def test_legacy_adapter_rejects_bundle_from_chart_with_different_pillars() -> None:
    chart = _chart()
    other_chart = _chart(birth_date="1993-08-18")
    bundle = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1992, 8, 18, 9, 30),
    )

    with pytest.raises(ValueError, match=f"^{PROVENANCE_ERROR}$"):
        apply_calculation_bundle(other_chart, bundle)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("birthplace", "Beijing"),
        ("gender", "male"),
        ("birth_time", "09:31"),
    ],
)
def test_legacy_adapter_rejects_same_pillars_with_different_birth_context(
    field_name: str,
    value: str,
) -> None:
    chart = _chart()
    bundle = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1992, 8, 18, 9, 30),
    )
    foreign_profile = replace(chart.birth_profile, **{field_name: value})
    foreign_chart = replace(chart, birth_profile=foreign_profile)

    with pytest.raises(ValueError, match=f"^{PROVENANCE_ERROR}$"):
        apply_calculation_bundle(foreign_chart, bundle)


def test_legacy_adapter_rejects_unbound_equal_bundle_copy() -> None:
    chart = _chart()
    bundle = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1992, 8, 18, 9, 30),
    )
    unbound_copy = replace(bundle)

    assert unbound_copy == bundle
    assert unbound_copy is not bundle
    with pytest.raises(ValueError, match=f"^{PROVENANCE_ERROR}$"):
        apply_calculation_bundle(chart, unbound_copy)


def test_legacy_not_computed_bundle_is_bound_only_to_its_chart() -> None:
    chart = _chart()
    bundle = build_legacy_not_computed_bundle(chart)

    adapted = apply_calculation_bundle(chart, bundle)

    assert adapted.strength_assessment.startswith(
        "[calculation_status=not_computed]"
    )
    with pytest.raises(ValueError, match=f"^{PROVENANCE_ERROR}$"):
        apply_calculation_bundle(
            replace(
                chart,
                birth_profile=replace(chart.birth_profile, gender="male"),
            ),
            bundle,
        )


def test_public_binding_validator_accepts_only_original_legacy_chart() -> None:
    chart = _chart()
    localized_names = ("年柱", "月柱", "日柱", "time")
    localized_chart = replace(
        chart,
        pillars=[
            replace(pillar, name=name)
            for pillar, name in zip(
                chart.pillars,
                localized_names,
                strict=True,
            )
        ],
        day_master=chart.day_master,
    )

    assert callable(getattr(bazi_api, "validate_calculation_binding", None))
    bundle = build_legacy_not_computed_bundle(localized_chart)

    bazi_api.validate_calculation_binding(localized_chart, bundle)
    assert tuple(fact.pillar_name for fact in bundle.facts.exposed_stems) == (
        "year",
        "month",
        "day",
        "hour",
    )
    with pytest.raises(ValueError, match=f"^{PROVENANCE_ERROR}$"):
        bazi_api.validate_calculation_binding(chart, bundle)


def test_legacy_adapter_defensively_copies_mutable_chart_fields() -> None:
    chart = _chart()
    bundle = analyze_bazi_chart(
        chart,
        birth_datetime=datetime(1992, 8, 18, 9, 30),
    )

    adapted = apply_calculation_bundle(chart, bundle)

    assert adapted.pillars == chart.pillars
    assert adapted.pillars is not chart.pillars
    assert all(
        adapted_pillar is not original_pillar
        for adapted_pillar, original_pillar in zip(
            adapted.pillars, chart.pillars, strict=True
        )
    )
    assert all(
        adapted_pillar.hidden_stems is not original_pillar.hidden_stems
        for adapted_pillar, original_pillar in zip(
            adapted.pillars, chart.pillars, strict=True
        )
    )
    assert adapted.five_elements_summary == chart.five_elements_summary
    assert adapted.five_elements_summary is not chart.five_elements_summary

    chart.pillars[0].hidden_stems.append("original-only")
    adapted.pillars[1].hidden_stems.append("adapted-only")
    chart.five_elements_summary["original-only"] = "wood"
    adapted.five_elements_summary["adapted-only"] = "fire"

    assert "original-only" not in adapted.pillars[0].hidden_stems
    assert "adapted-only" not in chart.pillars[1].hidden_stems
    assert "original-only" not in adapted.five_elements_summary
    assert "adapted-only" not in chart.five_elements_summary


def test_legacy_summaries_are_exact_and_deterministic_across_runs() -> None:
    chart = _chart()
    birth_datetime = datetime(1992, 8, 18, 9, 30)

    first = apply_calculation_bundle(
        chart,
        analyze_bazi_chart(chart, birth_datetime=birth_datetime, selected_year=2030),
    )
    second = apply_calculation_bundle(
        chart,
        analyze_bazi_chart(chart, birth_datetime=birth_datetime, selected_year=2030),
    )

    expected = (
        "[calculation_status=computed] year:七杀, month:食神, day:比肩, hour:正官",
        "[calculation_status=computed] 弱 label=弱; score=-38.5",
        (
            "[calculation_status=computed] 偏财格: 偏财格: candidate",
            "[calculation_status=computed] 七杀格: 七杀格: candidate",
            "[calculation_status=computed] 食神格: 食神格: candidate",
            "[calculation_status=indeterminate] 从弱候选: 从弱候选: guarded V1 candidate",
        ),
        (
            "[calculation_status=computed] support_control:木: resource element is a conditional weak-chart support/control candidate",
            "[calculation_status=computed] support_control:火: companion element is a conditional weak-chart support/control candidate",
            "[calculation_status=computed] illness_remedy:木: first weak-chart remedy candidate",
            "[calculation_status=not_computed] seasonal_adjustment:: no V1 seasonal rule for spring/autumn month branch",
            "[calculation_status=not_computed] mediation:: no explicit controlling bottleneck detected",
        ),
        "[calculation_status=computed] Luck-cycle direction, start, pillars, and requested structural branch relations were calculated.",
    )

    def summaries(adapted):
        return (
            adapted.ten_gods_summary,
            adapted.strength_assessment,
            tuple(adapted.pattern_candidates),
            tuple(adapted.useful_god_candidates),
            adapted.luck_cycle_summary,
        )

    assert summaries(first) == expected
    assert summaries(second) == expected
