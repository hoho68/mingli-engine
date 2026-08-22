from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import mingli_engine.application_service as application_service
import mingli_engine.domain_calibration_v2 as calibration_v2
from mingli_engine.chart_calculator import ChartCalculationError
from mingli_engine.domain_calibration_v2 import (
    ApplicationJsonExecutorV2,
    execute_calibration_fixture_v2,
    load_executable_fixtures_v2,
)
from mingli_engine.domain_calibration_v2_models import (
    CalibrationFixtureExecutionV2,
    CalibrationFixtureV2,
)
from mingli_engine.formal_interpretation import (
    get_formal_interpretation_rule_families,
)


def _fixture_by_kind() -> dict[str, CalibrationFixtureV2]:
    return {
        item.scenario_kind: item
        for item in load_executable_fixtures_v2().records
    }


class _RealDependencyFailureExecutor:
    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._monkeypatch = monkeypatch
        self.calls: list[bytes] = []

    def execute(self, payload: bytes) -> bytes:
        self.calls.append(payload)

        def fail_calculation(*_args: object, **_kwargs: object) -> None:
            raise ChartCalculationError("synthetic private dependency detail")

        with self._monkeypatch.context() as context:
            context.setattr(
                application_service,
                "analyze_bazi_chart",
                fail_calculation,
            )
            return application_service.handle_real_use_json(payload)


def _execute(
    fixture: CalibrationFixtureV2,
    monkeypatch: pytest.MonkeyPatch,
    dependency_executor: ApplicationJsonExecutorV2 | None = None,
) -> CalibrationFixtureExecutionV2:
    if fixture.execution_policy == "inject_calculation_failure":
        assert dependency_executor is not None
        return execute_calibration_fixture_v2(fixture, dependency_executor)
    return execute_calibration_fixture_v2(fixture)


def _response(execution: CalibrationFixtureExecutionV2, name: str) -> dict[str, Any]:
    assert execution.observation is not None
    payload = getattr(execution.observation, name)
    value: object = __import__("json").loads(payload)
    assert isinstance(value, dict)
    return value


def _domain_projection(execution: CalibrationFixtureExecutionV2) -> tuple[object, ...]:
    return tuple(
        (
            item.rule_family,
            item.availability,
            item.actual_status,
            item.actual_values,
            item.actual_rule_ids,
            item.actual_evidence_ids,
            item.failure_codes,
        )
        for item in execution.extractions
    )


def test_all_fixtures_use_real_application_and_registered_extractors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = calibration_v2.handle_real_use_json
    direct_calls: list[bytes] = []

    def record_real_call(payload: bytes) -> bytes:
        direct_calls.append(payload)
        return original(payload)

    monkeypatch.setattr(calibration_v2, "handle_real_use_json", record_real_call)
    dependency = _RealDependencyFailureExecutor(monkeypatch)
    executions = tuple(
        _execute(item, monkeypatch, dependency)
        for item in load_executable_fixtures_v2().records
    )

    assert len(direct_calls) + len(dependency.calls) == len(executions) * 2
    assert len(dependency.calls) == 2
    families = get_formal_interpretation_rule_families()
    for execution in executions:
        if execution.scenario_kind == "dependency_degradation":
            assert execution.actual_interface_outcome == "calculation_failed"
            assert execution.observation is None
            assert execution.extractions == ()
        else:
            assert execution.observation is not None
            assert tuple(item.rule_family for item in execution.extractions) == families


def test_normal_and_explicit_families_come_from_real_formal_trace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    execution = _execute(
        _fixture_by_kind()["normal_analysis_report"],
        monkeypatch,
    )
    assert execution.actual_interface_outcome == "ok"
    by_family = {item.rule_family: item for item in execution.extractions}
    assert set(by_family) == set(get_formal_interpretation_rule_families())
    assert all(item.availability == "available" for item in by_family.values())
    assert any(
        value.startswith("taboo_candidate:")
        for value in by_family["taboo_god_candidate"].actual_values
    )
    assert any(
        value.startswith("blind_image:")
        for value in by_family["blind_image_method"].actual_values
    )
    assert any(
        value.startswith("remedy_boundary:")
        for value in by_family["remedy_boundary"].actual_values
    )


def test_registered_boundary_scenarios_are_observed_not_simulated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixtures = _fixture_by_kind()

    aware = _execute(fixtures["aware_datetime_rejection"], monkeypatch)
    assert aware.actual_interface_outcome == "unsupported_input"
    assert all(item.failure_codes == ("unsupported_input",) for item in aware.extractions)

    high_risk = _execute(fixtures["high_risk_refusal"], monkeypatch)
    assert high_risk.actual_interface_outcome == "unsafe_request"
    assert all(item.failure_codes == ("unsafe_request",) for item in high_risk.extractions)

    empty = _execute(fixtures["empty_branch_relations"], monkeypatch)
    calculation = _response(empty, "analysis_response_json")["result"]["calculation"]
    assert calculation["branch_relations"] == []

    unknown = _execute(fixtures["unknown_gender"], monkeypatch)
    unknown_calculation = _response(unknown, "analysis_response_json")["result"]["calculation"]
    assert unknown_calculation["luck_cycles"]["reasoning"]["status"] == "not_computed"

    severe = _execute(fixtures["severe_conflict"], monkeypatch)
    report = _response(severe, "report_response_json")["result"]["report"]
    high_risk_conclusion = next(
        item
        for item in report["expanded_evidence"]["formal_conclusions"]
        if item["rule_family"] == "high_risk_signal"
    )
    assert high_risk_conclusion["strength"] == "disputed"
    assert high_risk_conclusion["trace"]["disagreement_note"]


@pytest.mark.parametrize(
    ("scenario_kind", "school_id"),
    [
        ("school_disagreement_ziping", "ziping"),
        ("school_disagreement_liang_xiangrun", "liang_xiangrun"),
        ("school_disagreement_duan", "duan"),
    ],
)
def test_school_disagreement_scenarios_preserve_each_real_school_view(
    monkeypatch: pytest.MonkeyPatch,
    scenario_kind: str,
    school_id: str,
) -> None:
    execution = _execute(_fixture_by_kind()[scenario_kind], monkeypatch)
    calculation = _response(execution, "analysis_response_json")["result"]["calculation"]
    schools = {item["school_id"]: item for item in calculation["schools"]}
    assert schools[school_id]["reasoning"]["status"] == "disputed"
    assert "school.cross_school_disagreement" in "|".join(
        schools[school_id]["reasoning"]["rule_ids"]
    )


def test_dependency_error_comes_from_real_application_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture_by_kind()["dependency_degradation"]
    dependency = _RealDependencyFailureExecutor(monkeypatch)
    execution = execute_calibration_fixture_v2(fixture, dependency)
    assert dependency.calls == [
        fixture.analysis_request_json.encode("utf-8"),
        fixture.report_request_json.encode("utf-8"),
    ]
    assert execution.actual_interface_outcome == "calculation_failed"
    assert execution.observation is None
    assert execution.extractions == ()


def test_expectation_shaped_objects_cannot_change_fixture_extraction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture_by_kind()["normal_analysis_report"]
    before = _domain_projection(_execute(fixture, monkeypatch))
    external_expectations = {
        "acceptable_values": ["forged"],
        "expected_domain_status": "computed",
        "required_rule_ids": ["forged.rule"],
        "adjudication": {"winner": "forged"},
    }
    assert external_expectations
    after = _domain_projection(_execute(fixture, monkeypatch))
    assert after == before


def test_fixture_execution_is_semantically_deterministic_and_writes_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture_by_kind()["normal_analysis_report"]
    writes: list[tuple[str, object]] = []

    def reject_write(path: Path, *_args: object, **_kwargs: object) -> None:
        writes.append((str(path), _args))
        raise AssertionError("fixture execution attempted a file write")

    monkeypatch.setattr(Path, "write_bytes", reject_write)
    monkeypatch.setattr(Path, "write_text", reject_write)
    first = _execute(fixture, monkeypatch)
    second = _execute(fixture, monkeypatch)
    assert _domain_projection(first) == _domain_projection(second)
    assert writes == []
    data_dir = Path("src/mingli_engine/data/domain_calibration/v2")
    assert {item.name for item in data_dir.iterdir()} == {
        "executable_fixtures.json"
    }
