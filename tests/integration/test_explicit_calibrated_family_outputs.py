from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

import mingli_engine.application_service as application_service
from mingli_engine.application_service import handle_real_use_json
from mingli_engine.cli import main
from mingli_engine.domain_calibration import canonical_json_bytes
from mingli_engine.domain_calibration_v2 import (
    collect_calibration_observation_v2,
    extract_calibration_family_v2,
)


FIXTURES = Path(__file__).parents[1] / "fixtures" / "application"
EXPLICIT_FAMILIES = (
    "taboo_god_candidate",
    "blind_image_method",
    "remedy_boundary",
)
PUBLIC_CALCULATION_KEYS = {
    "engine_version",
    "ruleset_version",
    "facts",
    "branch_relations",
    "strength",
    "patterns",
    "useful_gods",
    "luck_cycles",
    "schools",
}
LEGACY_ANALYSIS_CLI_SHA256 = (
    "f6965ac6212fee4daace96ffc2675b590bb494bd64bb3f3e16c12958867d2030"
)


def _requests() -> tuple[bytes, bytes]:
    analysis = json.loads(
        (FIXTURES / "valid_analysis_request.json").read_text(encoding="utf-8")
    )
    report = json.loads(json.dumps(analysis))
    report["operation"] = "report"
    report["options"] = {
        "report_format": "json",
        "include_profile_in_report": False,
    }
    return canonical_json_bytes(analysis), canonical_json_bytes(report)


def _mapping(payload: bytes) -> dict[str, Any]:
    value = json.loads(payload)
    assert isinstance(value, dict)
    return value


def test_formal_report_exposes_three_dedicated_family_traces() -> None:
    analysis_request, report_request = _requests()
    observation = collect_calibration_observation_v2(
        "explicit-family-observation-v2",
        analysis_request,
        report_request,
    )
    report = _mapping(observation.report_response_json)["result"]["report"]
    conclusions = {
        item["rule_family"]: item
        for item in report["expanded_evidence"]["formal_conclusions"]
    }

    expected_prefixes = {
        "taboo_god_candidate": "taboo_candidate:",
        "blind_image_method": "blind_image:",
        "remedy_boundary": "remedy_boundary:",
    }
    for family, prefix in expected_prefixes.items():
        trace = conclusions[family]["trace"]
        assert trace["calculation_status"] in {
            "computed",
            "indeterminate",
            "disputed",
        }
        assert trace["rule_ids"]
        assert trace["evidence_ids"]
        assert any(value.startswith(prefix) for value in trace["supporting_signals"])


def test_v2_extractors_match_real_formal_trace_values_and_ids() -> None:
    analysis_request, report_request = _requests()
    observation = collect_calibration_observation_v2(
        "explicit-family-extraction-v2",
        analysis_request,
        report_request,
    )
    report = _mapping(observation.report_response_json)["result"]["report"]
    conclusions = {
        item["rule_family"]: item
        for item in report["expanded_evidence"]["formal_conclusions"]
    }

    for family in EXPLICIT_FAMILIES:
        extraction = extract_calibration_family_v2(observation, family)
        trace = conclusions[family]["trace"]
        assert extraction.availability == "available"
        assert extraction.actual_status == trace["calculation_status"]
        assert extraction.actual_rule_ids == tuple(trace["rule_ids"])
        assert extraction.actual_evidence_ids == tuple(trace["evidence_ids"])
        assert extraction.actual_values
        assert set(extraction.actual_values) <= set(trace["supporting_signals"])
        assert extraction.failure_codes == ()


def test_expectation_shaped_objects_cannot_influence_real_extraction() -> None:
    analysis_request, report_request = _requests()
    observation = collect_calibration_observation_v2(
        "explicit-family-independence-v2",
        analysis_request,
        report_request,
    )
    before = tuple(
        extract_calibration_family_v2(observation, family)
        for family in EXPLICIT_FAMILIES
    )
    unrelated_expectations = {
        "acceptable_values": ["forged-value"],
        "adjudication": {"final_statuses": ["computed"]},
        "required_rule_ids": ["required-sentinel"],
    }
    assert unrelated_expectations
    after = tuple(
        extract_calibration_family_v2(observation, family)
        for family in EXPLICIT_FAMILIES
    )
    assert after == before
    assert all(
        "required-sentinel" not in extraction.actual_rule_ids
        for extraction in after
    )


def test_v1_analysis_response_keeps_exact_calculation_keys() -> None:
    analysis_request, _report_request = _requests()
    response = _mapping(handle_real_use_json(analysis_request))
    assert set(response["result"]["calculation"]) == PUBLIC_CALCULATION_KEYS


def test_existing_analysis_cli_output_remains_byte_compatible(
    monkeypatch: pytest.MonkeyPatch,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    monkeypatch.setattr(
        application_service,
        "uuid4",
        lambda: UUID("00000000-0000-4000-8000-000000000001"),
    )
    exit_code = main(
        [
            "real-use",
            "--input",
            str(FIXTURES / "valid_analysis_request.json"),
        ]
    )
    captured = capsysbinary.readouterr()
    assert exit_code == 0
    assert captured.err == b""
    assert sha256(captured.out).hexdigest() == LEGACY_ANALYSIS_CLI_SHA256
