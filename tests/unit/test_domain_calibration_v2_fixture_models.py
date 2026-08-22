from __future__ import annotations

from dataclasses import FrozenInstanceError, asdict, fields
from hashlib import sha256
import json
from pathlib import Path

import pytest

from mingli_engine.domain_calibration import (
    canonical_json_bytes,
    records_payload_sha256,
)
from mingli_engine.domain_calibration_v2 import (
    CalibrationFixtureErrorV2,
    load_executable_fixtures_v2,
)
from mingli_engine.domain_calibration_v2_models import (
    CALIBRATION_EXECUTABLE_FIXTURE_SCHEMA_V2,
    CALIBRATION_FIXTURE_FILE_SCHEMA_V2,
    DOMAIN_CALIBRATION_SUITE_V2,
    CalibrationFixtureEnvelopeV2,
    CalibrationFixtureExecutionV2,
    CalibrationFixtureV2,
)


FORBIDDEN_MANIFEST_KEYS = {
    "acceptable_values",
    "expected_domain_status",
    "required_rule_ids",
    "required_evidence_ids",
    "engine_output",
    "review",
    "reviews",
    "reviewer",
    "adjudication",
    "calibration_run",
    "metrics",
    "baseline",
    "case_signal",
    "coverage_tags",
}


def _canonical_request(operation: str) -> str:
    request = {
        "authorization": {"attested": True, "subject_relation": "self"},
        "operation": operation,
        "options": {
            "include_profile_in_report": False,
            "report_format": "json" if operation == "report" else None,
        },
        "profile": {
            "birth_date": "1996-12-15",
            "birth_time": "09:30",
            "birthplace": "Synthetic Calibration V2 Place",
            "calendar_type": "gregorian",
            "focus_topic": "synthetic fixture model",
            "gender": "unknown",
        },
        "request_id": "synthetic-fixture-model-v2",
        "schema_version": "real-use-request-v1",
    }
    return canonical_json_bytes(request).decode("utf-8")


def _fixture(**changes: object) -> CalibrationFixtureV2:
    analysis = _canonical_request("analysis")
    report = _canonical_request("report")
    values: dict[str, object] = {
        "schema_version": CALIBRATION_EXECUTABLE_FIXTURE_SCHEMA_V2,
        "suite_version": DOMAIN_CALIBRATION_SUITE_V2,
        "fixture_id": "fixture-v2-model",
        "scenario_kind": "normal_analysis_report",
        "execution_policy": "direct_application",
        "expected_interface_outcome": "ok",
        "analysis_request_json": analysis,
        "report_request_json": report,
        "analysis_request_sha256": sha256(analysis.encode("utf-8")).hexdigest(),
        "report_request_sha256": sha256(report.encode("utf-8")).hexdigest(),
        "contains_real_personal_data": False,
    }
    values.update(changes)
    return CalibrationFixtureV2(**values)  # type: ignore[arg-type]


def _write_envelope(path: Path, records: list[dict[str, object]]) -> None:
    generated_from = sorted(
        value
        for record in records
        for key, value in record.items()
        if key in {"analysis_request_sha256", "report_request_sha256"}
    )
    envelope = {
        "schema_version": CALIBRATION_FIXTURE_FILE_SCHEMA_V2,
        "suite_version": DOMAIN_CALIBRATION_SUITE_V2,
        "generated_from": generated_from,
        "contains_real_personal_data": False,
        "payload_sha256": records_payload_sha256(records),
        "records": records,
    }
    path.write_bytes(canonical_json_bytes(envelope))


def _walk_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value).union(
            key for item in value.values() for key in _walk_keys(item)
        )
    if isinstance(value, list):
        return {key for item in value for key in _walk_keys(item)}
    return set()


def test_fixture_models_are_frozen_v2_and_have_exact_fields() -> None:
    assert tuple(item.name for item in fields(CalibrationFixtureV2)) == (
        "schema_version",
        "suite_version",
        "fixture_id",
        "scenario_kind",
        "execution_policy",
        "expected_interface_outcome",
        "analysis_request_json",
        "report_request_json",
        "analysis_request_sha256",
        "report_request_sha256",
        "contains_real_personal_data",
    )
    assert tuple(item.name for item in fields(CalibrationFixtureEnvelopeV2)) == (
        "schema_version",
        "suite_version",
        "generated_from",
        "contains_real_personal_data",
        "payload_sha256",
        "records",
    )
    assert tuple(item.name for item in fields(CalibrationFixtureExecutionV2)) == (
        "fixture_id",
        "scenario_kind",
        "actual_interface_outcome",
        "observation",
        "extractions",
    )
    fixture = _fixture()
    with pytest.raises(FrozenInstanceError):
        fixture.fixture_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "changes",
    [
        {"schema_version": "domain-calibration-executable-fixture-v1"},
        {"suite_version": "domain-calibration-suite-v1"},
        {"scenario_kind": "unregistered"},
        {"execution_policy": "simulate_output"},
        {"expected_interface_outcome": "computed"},
        {"contains_real_personal_data": True},
        {"contains_real_personal_data": 0},
        {"analysis_request_json": b"{}"},
        {"analysis_request_sha256": "a" * 64},
    ],
)
def test_fixture_model_rejects_wrong_schema_types_privacy_and_hashes(
    changes: dict[str, object],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _fixture(**changes)


def test_packaged_fixture_envelope_is_canonical_sorted_hashed_and_private() -> None:
    envelope = load_executable_fixtures_v2()
    assert envelope.schema_version == CALIBRATION_FIXTURE_FILE_SCHEMA_V2
    assert envelope.suite_version == DOMAIN_CALIBRATION_SUITE_V2
    assert envelope.contains_real_personal_data is False
    assert len(envelope.records) >= 10
    assert tuple(item.fixture_id for item in envelope.records) == tuple(
        sorted(item.fixture_id for item in envelope.records)
    )
    assert len({item.fixture_id for item in envelope.records}) == len(
        envelope.records
    )
    assert all(item.contains_real_personal_data is False for item in envelope.records)
    assert envelope.payload_sha256 == records_payload_sha256(
        [asdict(item) for item in envelope.records]
    )
    assert envelope.generated_from == tuple(
        sorted(
            request_hash
            for item in envelope.records
            for request_hash in (
                item.analysis_request_sha256,
                item.report_request_sha256,
            )
        )
    )


def test_manifest_contains_only_requests_and_interface_level_expectations() -> None:
    envelope = load_executable_fixtures_v2()
    raw = json.loads(
        canonical_json_bytes(
            {
                "records": [asdict(item) for item in envelope.records],
            }
        )
    )
    assert not (_walk_keys(raw) & FORBIDDEN_MANIFEST_KEYS)
    for item in envelope.records:
        assert "response" not in item.analysis_request_json
        assert "response" not in item.report_request_json
        assert "engine_output" not in item.analysis_request_json
        assert "engine_output" not in item.report_request_json


def test_loader_is_strictly_read_only(tmp_path: Path) -> None:
    source = Path(
        "src/mingli_engine/data/domain_calibration/v2/executable_fixtures.json"
    )
    target = tmp_path / source.name
    target.write_bytes(source.read_bytes())
    before = (target.read_bytes(), target.stat().st_mtime_ns)
    first = load_executable_fixtures_v2(target)
    second = load_executable_fixtures_v2(target)
    after = (target.read_bytes(), target.stat().st_mtime_ns)
    assert first == second
    assert after == before


def test_loader_rejects_noncanonical_hash_duplicate_and_forbidden_records(
    tmp_path: Path,
) -> None:
    source = Path(
        "src/mingli_engine/data/domain_calibration/v2/executable_fixtures.json"
    )
    raw = json.loads(source.read_text(encoding="utf-8"))

    noncanonical = tmp_path / "noncanonical.json"
    noncanonical.write_text(json.dumps(raw, ensure_ascii=False, indent=2), "utf-8")
    with pytest.raises(CalibrationFixtureErrorV2):
        load_executable_fixtures_v2(noncanonical)

    bad_hash = tmp_path / "bad-hash.json"
    bad_hash_raw = dict(raw)
    bad_hash_raw["payload_sha256"] = "0" * 64
    bad_hash.write_bytes(canonical_json_bytes(bad_hash_raw))
    with pytest.raises(CalibrationFixtureErrorV2):
        load_executable_fixtures_v2(bad_hash)

    duplicate = tmp_path / "duplicate.json"
    duplicate_records = [*raw["records"], raw["records"][0]]
    _write_envelope(duplicate, duplicate_records)
    with pytest.raises(CalibrationFixtureErrorV2):
        load_executable_fixtures_v2(duplicate)

    forbidden = tmp_path / "forbidden.json"
    forbidden_records = [dict(item) for item in raw["records"]]
    forbidden_records[0]["acceptable_values"] = ["forged"]
    _write_envelope(forbidden, forbidden_records)
    with pytest.raises(CalibrationFixtureErrorV2):
        load_executable_fixtures_v2(forbidden)


def test_loader_rejects_request_pair_drift_and_oversize(tmp_path: Path) -> None:
    source = Path(
        "src/mingli_engine/data/domain_calibration/v2/executable_fixtures.json"
    )
    raw = json.loads(source.read_text(encoding="utf-8"))
    records = [dict(item) for item in raw["records"]]
    first = records[0]
    report = json.loads(first["report_request_json"])
    report["profile"]["gender"] = "male"
    report_text = canonical_json_bytes(report).decode("utf-8")
    first["report_request_json"] = report_text
    first["report_request_sha256"] = sha256(report_text.encode()).hexdigest()
    drift = tmp_path / "drift.json"
    _write_envelope(drift, records)
    with pytest.raises(CalibrationFixtureErrorV2):
        load_executable_fixtures_v2(drift)

    oversized_records = [dict(item) for item in raw["records"]]
    oversized = oversized_records[0]
    request = json.loads(oversized["analysis_request_json"])
    request["profile"]["focus_topic"] = "x" * (32 * 1024)
    request_text = canonical_json_bytes(request).decode("utf-8")
    oversized["analysis_request_json"] = request_text
    oversized["analysis_request_sha256"] = sha256(request_text.encode()).hexdigest()
    oversize_path = tmp_path / "oversize.json"
    _write_envelope(oversize_path, oversized_records)
    with pytest.raises(CalibrationFixtureErrorV2):
        load_executable_fixtures_v2(oversize_path)
