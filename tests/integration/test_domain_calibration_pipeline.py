from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path

import pytest

import mingli_engine.domain_calibration as calibration
from mingli_engine.domain_calibration import (
    CalibrationProtocolError,
    load_calibration_file,
)
from mingli_engine.domain_calibration_models import (
    AdjudicationDecision,
    CalibrationAssertion,
    CalibrationCase,
    CalibrationFileEnvelopeV1,
    CalibrationInputFixture,
    CalibrationReview,
    MetricSnapshotV1,
)


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "src/mingli_engine/data/domain_calibration"
TRACKED_BASELINE = DATA_ROOT / "calibration_baseline.json"
TARGET_APPLICATION_VERSION = "0.2.0"
_REQUIRED_API = (
    "build_candidate_version_set",
    "execute_candidate_calibration",
    "build_candidate_metric_snapshot",
    "write_candidate_baseline",
    "candidate_matches_installed_application",
    "required_trace_completeness_rate",
    "adjudication_coverage_rate",
    "weighted_kappa",
    "jaccard_agreement",
)
_API_READY = all(hasattr(calibration, name) for name in _REQUIRED_API)


@pytest.fixture(autouse=True)
def _require_task14_api(request: pytest.FixtureRequest) -> None:
    if request.node.name != "test_task14_api_is_explicit" and not _API_READY:
        pytest.skip("Task 14 API is not implemented yet")


@pytest.fixture(scope="module")
def assertions() -> CalibrationFileEnvelopeV1[CalibrationAssertion]:
    return load_calibration_file(
        DATA_ROOT / "calibration_assertions.json",
        CalibrationAssertion,
    )


@pytest.fixture(scope="module")
def cases() -> CalibrationFileEnvelopeV1[CalibrationCase]:
    return load_calibration_file(
        DATA_ROOT / "calibration_cases.json",
        CalibrationCase,
    )


@pytest.fixture(scope="module")
def fixtures() -> CalibrationFileEnvelopeV1[CalibrationInputFixture]:
    return load_calibration_file(
        DATA_ROOT / "input_fixtures.json",
        CalibrationInputFixture,
    )


@pytest.fixture(scope="module")
def adjudications() -> CalibrationFileEnvelopeV1[AdjudicationDecision]:
    return load_calibration_file(
        DATA_ROOT / "adjudication.json",
        AdjudicationDecision,
    )


@pytest.fixture(scope="module")
def reviewer_a() -> CalibrationFileEnvelopeV1[CalibrationReview]:
    return load_calibration_file(
        DATA_ROOT / "reviewer_a_reviews.json",
        CalibrationReview,
    )


@pytest.fixture(scope="module")
def reviewer_b() -> CalibrationFileEnvelopeV1[CalibrationReview]:
    return load_calibration_file(
        DATA_ROOT / "reviewer_b_reviews.json",
        CalibrationReview,
    )


@pytest.fixture(scope="module")
def version_set():
    return calibration.build_candidate_version_set(TARGET_APPLICATION_VERSION)


@pytest.fixture(scope="module")
def run(version_set):
    return calibration.execute_candidate_calibration(version_set)


@pytest.fixture(scope="module")
def repeated_run(version_set):
    return calibration.execute_candidate_calibration(version_set)


@pytest.fixture(scope="module")
def snapshot(run, repeated_run):
    return calibration.build_candidate_metric_snapshot(run, repeated_run)


def _asset_hashes() -> dict[str, str]:
    return {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(DATA_ROOT.glob("*.json"))
    }


def test_task14_api_is_explicit() -> None:
    missing = [name for name in _REQUIRED_API if not hasattr(calibration, name)]
    assert missing == []


def test_candidate_version_set_targets_exact_0_2_0(version_set) -> None:
    assert version_set.application_version == TARGET_APPLICATION_VERSION
    assert version_set.engine_version == "bazi-core-v1"
    assert version_set.ruleset_version == "ziping-v1"
    assert version_set.provider_version == "lunar-python-1.4.8"
    assert version_set.school_profile_version == "school-profiles-v1"
    assert version_set.fixture_version == "calibration-fixtures-v1"
    assert version_set.evidence_baseline_id == "report_acceptance_v1"
    assert len(version_set.corpus_sha256) == 64


def test_repeated_exact_version_runs_are_fully_deterministic(
    run,
    repeated_run,
) -> None:
    assert run == repeated_run
    assert run.run_id == repeated_run.run_id
    assert run.version_set == repeated_run.version_set
    assert run.assertion_results == repeated_run.assertion_results


def test_all_43_assertions_produce_unique_ordered_results(
    assertions,
    run,
) -> None:
    assertion_ids = tuple(item.assertion_id for item in assertions.records)
    result_ids = tuple(item.assertion_id for item in run.assertion_results)
    assert len(assertion_ids) == len(result_ids) == 43
    assert result_ids == assertion_ids == tuple(sorted(assertion_ids))
    assert len(set(result_ids)) == 43


def test_results_have_complete_traces_and_stable_failure_codes(
    assertions,
    run,
) -> None:
    by_id = {item.assertion_id: item for item in assertions.records}
    for result in run.assertion_results:
        assertion = by_id[result.assertion_id]
        assert set(assertion.required_rule_ids) <= set(result.actual_rule_ids)
        assert set(assertion.required_evidence_ids) <= set(
            result.actual_evidence_ids
        )
        assert result.failure_codes == tuple(sorted(set(result.failure_codes)))
        assert result.actual_status in {
            "computed",
            "indeterminate",
            "disputed",
            "not_computed",
        }


def test_unsupported_inputs_are_never_computed(
    assertions,
    cases,
    run,
) -> None:
    unsupported_case_ids = {
        item.case_id
        for item in cases.records
        if "timezone_awareness" in item.coverage_tags
    }
    result_by_id = {
        item.assertion_id: item for item in run.assertion_results
    }
    selected = [
        result_by_id[item.assertion_id]
        for item in assertions.records
        if item.case_id in unsupported_case_ids
    ]
    assert selected
    assert all(item.actual_status == "not_computed" for item in selected)
    assert all("unsupported_input" in item.failure_codes for item in selected)


def test_dependency_degradation_never_bypasses_prerequisites(
    assertions,
    run,
) -> None:
    result_by_id = {
        item.assertion_id: item for item in run.assertion_results
    }
    selected = [
        result_by_id[item.assertion_id]
        for item in assertions.records
        if item.case_id == "case-dependency-degradation-001"
    ]
    assert selected
    assert all(item.actual_status == "not_computed" for item in selected)
    assert all("dependency_degraded" in item.failure_codes for item in selected)


def test_school_alternatives_are_visible_and_never_silently_collapsed(
    assertions,
    run,
) -> None:
    result_by_id = {
        item.assertion_id: item for item in run.assertion_results
    }
    school_assertions = [
        item for item in assertions.records if item.assertion_kind == "disagreement"
    ]
    assert len(school_assertions) == 3
    for assertion in school_assertions:
        result = result_by_id[assertion.assertion_id]
        assert result.actual_status == "disputed"
        assert "school_alternative_retained" in result.actual_values
        assert "school_alternative_preserved" in result.failure_codes


def test_safety_refusal_and_mandatory_abstention_are_exact(
    assertions,
    adjudications,
    run,
    snapshot,
) -> None:
    assertion_by_id = {item.assertion_id: item for item in assertions.records}
    result_by_id = {
        item.assertion_id: item for item in run.assertion_results
    }
    safety = [item for item in adjudications.records if item.safety_critical]
    assert len(safety) == 4
    for decision in safety:
        result = result_by_id[decision.assertion_id]
        assert assertion_by_id[result.assertion_id].rule_family == "high_risk_signal"
        assert result.actual_status == "not_computed"
        assert result.actual_values == ()
    assert snapshot.mandatory_abstention_rate == 1.0
    assert snapshot.safety_critical_exact_match == 1.0


def test_core_execution_and_trace_metrics_use_the_43_result_denominator(
    snapshot,
) -> None:
    assert snapshot.assertion_count == 43
    assert snapshot.determinism_rate == 1.0
    assert snapshot.pillar_agreement_rate == 1.0
    assert snapshot.evidence_trace_completeness_rate == 1.0
    assert snapshot.rule_trace_completeness_rate == 1.0
    assert snapshot.adjudication_coverage_rate == 1.0
    assert snapshot.unsupported_computed_count == 0
    assert snapshot.dependency_bypass_count == 0
    assert snapshot.school_disagreement_recall == 1.0
    assert snapshot.silent_school_collapse_count == 0


def test_reviewer_metrics_follow_the_exact_contract(snapshot) -> None:
    assert snapshot.reviewer_raw_agreement == pytest.approx(29 / 43)
    assert snapshot.reviewer_stratum_agreement == pytest.approx(
        {
            "calendrical": 11 / 16,
            "structural": 11 / 18,
            "school": 7 / 9,
        }
    )
    assert set(snapshot.reviewer_stratum_agreement) == {
        "calendrical",
        "structural",
        "school",
    }
    assert snapshot.weighted_kappa == pytest.approx(0.5701643489254108)
    assert snapshot.jaccard_agreement == pytest.approx(32 / 43)


def test_weighted_kappa_and_jaccard_edge_cases() -> None:
    assert calibration.weighted_kappa(("accept",) * 9, ("accept",) * 9) is None
    assert calibration.weighted_kappa(("accept",) * 10, ("accept",) * 10) == 1.0
    assert calibration.jaccard_agreement((), ()) == 1.0
    assert calibration.jaccard_agreement(("a", "b"), ("b", "c")) == pytest.approx(
        1 / 3
    )


def test_three_core_completeness_rates_reject_empty_denominators() -> None:
    with pytest.raises(CalibrationProtocolError, match="empty denominator"):
        calibration.required_trace_completeness_rate(
            (),
            (),
            required_field="required_evidence_ids",
            actual_field="actual_evidence_ids",
        )
    with pytest.raises(CalibrationProtocolError, match="empty denominator"):
        calibration.required_trace_completeness_rate(
            (),
            (),
            required_field="required_rule_ids",
            actual_field="actual_rule_ids",
        )
    with pytest.raises(CalibrationProtocolError, match="empty denominator"):
        calibration.adjudication_coverage_rate((), (), ())


def test_snapshot_corpus_and_version_set_are_exactly_bound(
    run,
    snapshot,
) -> None:
    assert snapshot.version_set == run.version_set
    assert snapshot.corpus_sha256 == snapshot.version_set.corpus_sha256
    assert snapshot.schema_version == "domain-calibration-metrics-v1"
    assert 0.0 <= snapshot.adjudicated_engine_match <= 1.0
    matched = sum(item.matched for item in run.assertion_results)
    assert snapshot.adjudicated_engine_match == pytest.approx(matched / 43)


def test_coverage_maps_and_version_bound_baseline_deltas(
    run,
    repeated_run,
    snapshot,
) -> None:
    assert set(snapshot.coverage) == {
        "rule_family",
        "school",
        "status",
        "assertion_kind",
        "evidence_source",
        "stratum",
    }
    assert sum(snapshot.coverage["rule_family"].values()) == 43
    assert sum(snapshot.coverage["school"].values()) == 43
    assert sum(snapshot.coverage["status"].values()) == 43
    assert sum(snapshot.coverage["assertion_kind"].values()) == 43
    assert sum(snapshot.coverage["stratum"].values()) == 43
    assert snapshot.baseline_deltas["status"] == "baseline_absent"

    baseline_version = replace(
        snapshot.version_set,
        application_version="0.1.0",
        provider_version="lunar-python-previous",
    )
    baseline = replace(
        snapshot,
        snapshot_id="metric-snapshot-baseline-test",
        version_set=baseline_version,
        determinism_rate=0.5,
    )
    compared = calibration.build_candidate_metric_snapshot(
        run,
        repeated_run,
        baseline=baseline,
    )
    assert compared.baseline_deltas["status"] == "version_mismatch"
    assert compared.baseline_deltas["version_changes"] == {
        "application_version": {"baseline": "0.1.0", "candidate": "0.2.0"},
        "provider_version": {
            "baseline": "lunar-python-previous",
            "candidate": "lunar-python-1.4.8",
        },
    }
    metric_deltas = compared.baseline_deltas["metric_deltas"]
    assert isinstance(metric_deltas, dict)
    assert metric_deltas["determinism_rate"] == 0.5


def test_candidate_baseline_can_only_be_written_to_explicit_tmp_target(
    tmp_path: Path,
    snapshot,
) -> None:
    before = _asset_hashes()
    assert not TRACKED_BASELINE.exists()
    target = tmp_path / "calibration_baseline_candidate.json"
    calibration.write_candidate_baseline(target, snapshot)
    loaded = load_calibration_file(target, MetricSnapshotV1)
    assert loaded.records == (snapshot,)
    assert target.parent == tmp_path
    assert not TRACKED_BASELINE.exists()
    assert _asset_hashes() == before

    with pytest.raises(CalibrationProtocolError, match="candidate baseline target"):
        calibration.write_candidate_baseline(tmp_path / "baseline.json", snapshot)
    with pytest.raises(CalibrationProtocolError, match="tracked calibration data"):
        calibration.write_candidate_baseline(
            DATA_ROOT / "calibration_baseline_candidate.json",
            snapshot,
        )


def test_candidate_target_does_not_match_current_installed_release(version_set) -> None:
    assert version("mingli-engine") == "0.1.0"
    assert version_set.application_version == "0.2.0"
    assert calibration.candidate_matches_installed_application(version_set) is False


def test_application_error_fails_closed_without_candidate_results(
    monkeypatch: pytest.MonkeyPatch,
    version_set,
) -> None:
    monkeypatch.setattr(
        calibration,
        "handle_real_use_json",
        lambda _payload: b'{"status":"error"}',
    )
    with pytest.raises(
        CalibrationProtocolError,
        match="calibration application execution failed",
    ):
        calibration.execute_candidate_calibration(version_set)


def test_candidate_run_is_read_only_and_creates_no_tracked_artifacts(
    version_set,
) -> None:
    before = _asset_hashes()
    calibration.execute_candidate_calibration(version_set)
    assert _asset_hashes() == before
    assert not TRACKED_BASELINE.exists()
    forbidden = {
        "calibration_run.json",
        "metric_snapshot.json",
        "calibration_baseline.json",
        "release_decision.json",
    }
    assert not forbidden.intersection(path.name for path in DATA_ROOT.glob("*.json"))
