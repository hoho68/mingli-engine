import builtins
import os
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from datetime import datetime
from pathlib import Path

import pytest

import mingli_engine.bazi.analysis as analysis
from mingli_engine.bazi.analysis import analyze_bazi_chart
from mingli_engine.bazi.facts import build_chart_facts
from mingli_engine.bazi.legacy_adapter import (
    apply_calculation_bundle,
    build_legacy_not_computed_bundle,
)
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.models import BirthProfile


PROVENANCE_ERROR = "calculation bundle is unbound or does not match chart input"


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
        bundle.engine_version = "changed"
    with pytest.raises(FrozenInstanceError):
        bundle.facts.day_master = "changed"


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
