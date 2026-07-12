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


def _profile(*, gender: str = "female") -> BirthProfile:
    return BirthProfile(
        calendar_type="gregorian",
        birth_date="1992-08-18",
        birth_time="09:30",
        birthplace="Shanghai",
        gender=gender,
        focus_topic="career",
    )


def _chart(*, gender: str = "female"):
    return calculate_bazi_chart(_profile(gender=gender))


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
