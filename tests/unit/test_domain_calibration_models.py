from __future__ import annotations

from dataclasses import FrozenInstanceError, asdict, fields, replace
from hashlib import sha256
import json
import math
from pathlib import Path

import pytest

from mingli_engine.domain_calibration import (
    CalibrationProtocolError,
    canonical_json_bytes,
    get_authoritative_rule_family_ids,
    load_authoritative_school_profile_identity,
    load_calibration_file,
    records_payload_sha256,
    validate_calibration_references,
    validate_version_set_equality,
)
from mingli_engine.domain_calibration_models import (
    AdjudicationDecision,
    BlindedAssertionProjection,
    CalibrationAssertion,
    CalibrationAssertionResult,
    CalibrationCase,
    CalibrationCitation,
    CalibrationFileEnvelopeV1,
    CalibrationInputFixture,
    CalibrationReleaseDecision,
    CalibrationReview,
    CalibrationRun,
    ExactVersionSet,
    MetricSnapshotV1,
    ReviewAssignment,
    ReviewerPacket,
)
from mingli_engine.formal_interpretation import (
    get_formal_interpretation_rule_families,
)


HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
EVIDENCE_ID = "batch001_blind_image_method_001"
ACCESS_MANIFEST = (
    "provided_packet_bytes_only",
    "tools_disabled",
    "filesystem_disabled",
    "peer_labels_absent",
    "engine_output_absent",
)


def _version_set(**changes: object) -> ExactVersionSet:
    values: dict[str, object] = {
        "application_version": "0.2.0",
        "engine_version": "bazi-core-v1",
        "ruleset_version": "ziping-v1",
        "provider_version": "lunar-python-1.4.8",
        "school_profile_version": "school-profiles-v1",
        "fixture_version": "calibration-fixtures-v1",
        "evidence_baseline_id": "report_acceptance_v1",
        "corpus_sha256": HASH_A,
    }
    values.update(changes)
    return ExactVersionSet(**values)  # type: ignore[arg-type]


def _fixture(**changes: object) -> CalibrationInputFixture:
    values: dict[str, object] = {
        "fixture_id": "fixture-001",
        "schema_version": "domain-calibration-input-v1",
        "request_payload": {"operation": "analysis", "synthetic": True},
        "expected_boundary": "accepted",
        "source_fixture_file": "verified_charts.json",
        "source_fixture_id": "synthetic_01_19961215_0930",
        "source_fixture_sha256": HASH_B,
    }
    values.update(changes)
    return CalibrationInputFixture(**values)  # type: ignore[arg-type]


def _case(**changes: object) -> CalibrationCase:
    values: dict[str, object] = {
        "case_id": "case-001",
        "case_version": "case-v1",
        "input_fixture_file": "input_fixtures.json",
        "input_fixture_id": "fixture-001",
        "input_sha256": HASH_C,
        "source_fixture_file": "verified_charts.json",
        "source_fixture_id": "synthetic_01_19961215_0930",
        "source_fixture_sha256": HASH_B,
        "stratum": "structural",
        "coverage_tags": ["pattern", "synthetic"],
        "claim_scope": "traditional structural conformance",
        "contains_real_personal_data": False,
    }
    values.update(changes)
    return CalibrationCase(**values)  # type: ignore[arg-type]


def _assertion(**changes: object) -> CalibrationAssertion:
    values: dict[str, object] = {
        "assertion_id": "assertion-001",
        "case_id": "case-001",
        "rule_family": "pattern_strength",
        "school_id": "ziping",
        "assertion_kind": "positive",
        "field_path": "$.result.calculation.pattern_candidates.status",
        "acceptable_statuses": ["computed"],
        "acceptable_values": ["follow_strength"],
        "required_rule_ids": ["patterns.follow_strength"],
        "required_evidence_ids": [EVIDENCE_ID],
        "limitations": ["synthetic fixture"],
    }
    values.update(changes)
    return CalibrationAssertion(**values)  # type: ignore[arg-type]


def _citation(**changes: object) -> CalibrationCitation:
    values: dict[str, object] = {
        "citation_id": "citation-001",
        "assertion_id": "assertion-001",
        "evidence_ids": [EVIDENCE_ID],
        "source_locators": ["synthetic:pattern-strength:001"],
        "rule_ids": ["patterns.follow_strength"],
        "applicability": "synthetic structural case",
        "limitations": ["traditional-method scope"],
    }
    values.update(changes)
    return CalibrationCitation(**values)  # type: ignore[arg-type]


def _projection(**changes: object) -> BlindedAssertionProjection:
    values: dict[str, object] = {
        "assertion_id": "assertion-001",
        "synthetic_case_facts": {"month_branch": "zi"},
        "rule_family": "pattern_strength",
        "school_id": "ziping",
        "assertion_kind": "positive",
        "field_path": "$.result.calculation.pattern_candidates.status",
        "candidate_statuses": ["computed"],
        "candidate_values": ["follow_strength"],
        "candidate_rule_ids": ["patterns.follow_strength"],
        "candidate_evidence_ids": [EVIDENCE_ID],
        "limitations": ["synthetic fixture"],
    }
    values.update(changes)
    return BlindedAssertionProjection(**values)  # type: ignore[arg-type]


def _packet(**changes: object) -> ReviewerPacket:
    values: dict[str, object] = {
        "packet_id": "packet-001",
        "assertion": _projection(),
        "citation_ids": ["citation-001"],
        "evidence_excerpts": {
            EVIDENCE_ID: "Concise synthetic excerpt."
        },
        "source_locators": ["synthetic:pattern-strength:001"],
        "rule_scope": ["patterns.follow_strength"],
        "limitations": ["agent-independent review"],
        "access_manifest": list(ACCESS_MANIFEST),
    }
    values.update(changes)
    return ReviewerPacket(**values)  # type: ignore[arg-type]


def _assignment(**changes: object) -> ReviewAssignment:
    values: dict[str, object] = {
        "assignment_id": "assignment-a-001",
        "reviewer_id": "reviewer-a",
        "reviewer_kind": "agent_independent",
        "packet_id": "packet-001",
        "packet_sha256": HASH_C,
        "access_manifest": list(ACCESS_MANIFEST),
        "peer_labels_hidden": True,
        "engine_output_hidden": True,
        "independence_attested": True,
    }
    values.update(changes)
    return ReviewAssignment(**values)  # type: ignore[arg-type]


def _review(**changes: object) -> CalibrationReview:
    values: dict[str, object] = {
        "review_id": "review-a-001",
        "assignment_id": "assignment-a-001",
        "assertion_id": "assertion-001",
        "label": "accept",
        "expected_statuses": ["computed"],
        "acceptable_values": ["follow_strength"],
        "confidence": 0.9,
        "rationale": "The candidate follows the cited tracked rule.",
        "evidence_ids": [EVIDENCE_ID],
        "source_locators": ["synthetic:pattern-strength:001"],
        "packet_sha256": HASH_C,
    }
    values.update(changes)
    return CalibrationReview(**values)  # type: ignore[arg-type]


def _adjudication(**changes: object) -> AdjudicationDecision:
    values: dict[str, object] = {
        "adjudication_id": "adjudication-001",
        "assertion_id": "assertion-001",
        "reviewer_a_review_id": "review-a-001",
        "reviewer_b_review_id": "review-b-001",
        "agreement_state": "agreement",
        "decision": "agreement",
        "final_statuses": ["computed"],
        "final_acceptable_values": ["follow_strength"],
        "retained_alternatives": [],
        "rationale": "Independent labels agree.",
        "evidence_ids": [EVIDENCE_ID],
        "safety_critical": False,
    }
    values.update(changes)
    return AdjudicationDecision(**values)  # type: ignore[arg-type]


def _assertion_result(**changes: object) -> CalibrationAssertionResult:
    values: dict[str, object] = {
        "assertion_id": "assertion-001",
        "actual_status": "computed",
        "actual_values": ["follow_strength"],
        "actual_rule_ids": ["patterns.follow_strength"],
        "actual_evidence_ids": ["ev-pattern-strength-001"],
        "matched": True,
        "failure_codes": [],
    }
    values.update(changes)
    return CalibrationAssertionResult(**values)  # type: ignore[arg-type]


def _run(**changes: object) -> CalibrationRun:
    values: dict[str, object] = {
        "run_id": "run-001",
        "version_set": _version_set(),
        "assertion_results": [_assertion_result()],
    }
    values.update(changes)
    return CalibrationRun(**values)  # type: ignore[arg-type]


def _snapshot(**changes: object) -> MetricSnapshotV1:
    values: dict[str, object] = {
        "snapshot_id": "snapshot-001",
        "schema_version": "domain-calibration-metrics-v1",
        "corpus_sha256": HASH_A,
        "version_set": _version_set(),
        "assertion_count": 1,
        "determinism_rate": 1.0,
        "pillar_agreement_rate": 1.0,
        "evidence_trace_completeness_rate": 1.0,
        "rule_trace_completeness_rate": 1.0,
        "adjudication_coverage_rate": 1.0,
        "unsupported_computed_count": 0,
        "dependency_bypass_count": 0,
        "school_disagreement_recall": 1.0,
        "silent_school_collapse_count": 0,
        "mandatory_abstention_rate": 1.0,
        "reviewer_raw_agreement": 1.0,
        "reviewer_stratum_agreement": {
            "calendrical": 1.0,
            "structural": 1.0,
            "school": 1.0,
        },
        "weighted_kappa": None,
        "jaccard_agreement": 1.0,
        "adjudicated_engine_match": 1.0,
        "safety_critical_exact_match": 1.0,
        "coverage": {"rule_family": {"pattern_strength": 1}},
        "baseline_deltas": {"assertion_count": 0},
    }
    values.update(changes)
    return MetricSnapshotV1(**values)  # type: ignore[arg-type]


def _release(**changes: object) -> CalibrationReleaseDecision:
    values: dict[str, object] = {
        "schema_version": "domain-calibration-release-v1",
        "release_status": "blocked",
        "checks": {"application_contract": "passed", "version": "failed"},
        "metrics": _snapshot(),
        "blockers": ["installed_version_mismatch"],
        "claim_boundary": "independent agent-based domain conformance only",
        "version_set": _version_set(),
        "next_action": "install_target_version",
    }
    values.update(changes)
    return CalibrationReleaseDecision(**values)  # type: ignore[arg-type]


def _envelope(**changes: object) -> CalibrationFileEnvelopeV1:
    values: dict[str, object] = {
        "schema_version": "domain-calibration-file-v1",
        "suite_version": "domain-calibration-suite-v1",
        "generated_from": [HASH_A, HASH_B],
        "contains_real_personal_data": False,
        "payload_sha256": HASH_C,
        "records": [_case()],
    }
    values.update(changes)
    return CalibrationFileEnvelopeV1(**values)  # type: ignore[arg-type]


MODEL_FIELDS = {
    CalibrationFileEnvelopeV1: (
        "schema_version",
        "suite_version",
        "generated_from",
        "contains_real_personal_data",
        "payload_sha256",
        "records",
    ),
    CalibrationInputFixture: (
        "fixture_id",
        "schema_version",
        "request_payload",
        "expected_boundary",
        "source_fixture_file",
        "source_fixture_id",
        "source_fixture_sha256",
    ),
    CalibrationCase: (
        "case_id",
        "case_version",
        "input_fixture_file",
        "input_fixture_id",
        "input_sha256",
        "source_fixture_file",
        "source_fixture_id",
        "source_fixture_sha256",
        "stratum",
        "coverage_tags",
        "claim_scope",
        "contains_real_personal_data",
    ),
    CalibrationAssertion: (
        "assertion_id",
        "case_id",
        "rule_family",
        "school_id",
        "assertion_kind",
        "field_path",
        "acceptable_statuses",
        "acceptable_values",
        "required_rule_ids",
        "required_evidence_ids",
        "limitations",
    ),
    CalibrationCitation: (
        "citation_id",
        "assertion_id",
        "evidence_ids",
        "source_locators",
        "rule_ids",
        "applicability",
        "limitations",
    ),
    BlindedAssertionProjection: (
        "assertion_id",
        "synthetic_case_facts",
        "rule_family",
        "school_id",
        "assertion_kind",
        "field_path",
        "candidate_statuses",
        "candidate_values",
        "candidate_rule_ids",
        "candidate_evidence_ids",
        "limitations",
    ),
    ReviewerPacket: (
        "packet_id",
        "assertion",
        "citation_ids",
        "evidence_excerpts",
        "source_locators",
        "rule_scope",
        "limitations",
        "access_manifest",
    ),
    ReviewAssignment: (
        "assignment_id",
        "reviewer_id",
        "reviewer_kind",
        "packet_id",
        "packet_sha256",
        "access_manifest",
        "peer_labels_hidden",
        "engine_output_hidden",
        "independence_attested",
    ),
    CalibrationReview: (
        "review_id",
        "assignment_id",
        "assertion_id",
        "label",
        "expected_statuses",
        "acceptable_values",
        "confidence",
        "rationale",
        "evidence_ids",
        "source_locators",
        "packet_sha256",
    ),
    AdjudicationDecision: (
        "adjudication_id",
        "assertion_id",
        "reviewer_a_review_id",
        "reviewer_b_review_id",
        "agreement_state",
        "decision",
        "final_statuses",
        "final_acceptable_values",
        "retained_alternatives",
        "rationale",
        "evidence_ids",
        "safety_critical",
    ),
    ExactVersionSet: (
        "application_version",
        "engine_version",
        "ruleset_version",
        "provider_version",
        "school_profile_version",
        "fixture_version",
        "evidence_baseline_id",
        "corpus_sha256",
    ),
    CalibrationAssertionResult: (
        "assertion_id",
        "actual_status",
        "actual_values",
        "actual_rule_ids",
        "actual_evidence_ids",
        "matched",
        "failure_codes",
    ),
    CalibrationRun: ("run_id", "version_set", "assertion_results"),
    MetricSnapshotV1: (
        "snapshot_id",
        "schema_version",
        "corpus_sha256",
        "version_set",
        "assertion_count",
        "determinism_rate",
        "pillar_agreement_rate",
        "evidence_trace_completeness_rate",
        "rule_trace_completeness_rate",
        "adjudication_coverage_rate",
        "unsupported_computed_count",
        "dependency_bypass_count",
        "school_disagreement_recall",
        "silent_school_collapse_count",
        "mandatory_abstention_rate",
        "reviewer_raw_agreement",
        "reviewer_stratum_agreement",
        "weighted_kappa",
        "jaccard_agreement",
        "adjudicated_engine_match",
        "safety_critical_exact_match",
        "coverage",
        "baseline_deltas",
    ),
    CalibrationReleaseDecision: (
        "schema_version",
        "release_status",
        "checks",
        "metrics",
        "blockers",
        "claim_boundary",
        "version_set",
        "next_action",
    ),
}


MODEL_SAMPLES = (
    _envelope(),
    _fixture(),
    _case(),
    _assertion(),
    _citation(),
    _projection(),
    _packet(),
    _assignment(),
    _review(),
    _adjudication(),
    _version_set(),
    _assertion_result(),
    _run(),
    _snapshot(),
    _release(),
)


@pytest.mark.parametrize("record", MODEL_SAMPLES)
def test_every_model_has_exact_fields_and_is_frozen(record: object) -> None:
    assert tuple(field.name for field in fields(record)) == MODEL_FIELDS[type(record)]
    with pytest.raises(FrozenInstanceError):
        setattr(record, fields(record)[0].name, "changed")


@pytest.mark.parametrize(
    ("record", "field_name"),
    [
        (_envelope(), "schema_version"),
        (_fixture(), "fixture_id"),
        (_case(), "case_id"),
        (_assertion(), "assertion_id"),
        (_citation(), "citation_id"),
        (_projection(), "assertion_id"),
        (_packet(), "packet_id"),
        (_assignment(), "assignment_id"),
        (_review(), "review_id"),
        (_adjudication(), "adjudication_id"),
        (_version_set(), "application_version"),
        (_assertion_result(), "assertion_id"),
        (_run(), "run_id"),
        (_snapshot(), "snapshot_id"),
        (_release(), "schema_version"),
    ],
)
def test_every_model_rejects_wrong_runtime_scalar_type(
    record: object,
    field_name: str,
) -> None:
    with pytest.raises(TypeError):
        replace(record, **{field_name: 7})


def test_sequence_fields_normalize_to_tuples_and_reject_invalid_items() -> None:
    assert isinstance(_case().coverage_tags, tuple)
    assert isinstance(_packet().access_manifest, tuple)
    assert isinstance(_run().assertion_results, tuple)
    assert isinstance(_release().blockers, tuple)
    assert isinstance(_envelope().records, tuple)

    with pytest.raises(TypeError):
        _case(coverage_tags=["valid", 7])
    with pytest.raises(TypeError):
        _run(assertion_results=["not-a-result"])


def test_exact_version_set_has_exactly_eight_required_fields() -> None:
    assert MODEL_FIELDS[ExactVersionSet] == tuple(
        field.name for field in fields(ExactVersionSet)
    )
    assert all(field.default is field.default_factory for field in fields(ExactVersionSet))
    with pytest.raises(TypeError):
        ExactVersionSet(application_version="0.2.0")  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        ExactVersionSet(**{**asdict(_version_set()), "extra": "forbidden"})


def test_run_snapshot_release_require_equal_exact_version_sets() -> None:
    run = _run()
    snapshot = _snapshot()
    release = _release()

    validate_version_set_equality(run, snapshot, release)

    with pytest.raises(CalibrationProtocolError, match="version_set"):
        validate_version_set_equality(
            _run(version_set=_version_set(provider_version="other-provider")),
            snapshot,
            release,
        )
    with pytest.raises(ValueError, match="corpus_sha256"):
        _snapshot(corpus_sha256=HASH_B)


def test_canonical_json_is_utf8_sorted_compact_and_rejects_nan() -> None:
    value = {"z": "Chinese text: \u547d\u7406", "a": [2, 1]}

    payload = canonical_json_bytes(value)

    assert payload == b'{"a":[2,1],"z":"Chinese text: \xe5\x91\xbd\xe7\x90\x86"}'
    with pytest.raises(CalibrationProtocolError, match="canonical JSON"):
        canonical_json_bytes({"value": math.nan})


def test_payload_hash_covers_records_only() -> None:
    records = [asdict(_case())]
    expected = sha256(canonical_json_bytes(records)).hexdigest()

    assert records_payload_sha256(records) == expected
    assert records_payload_sha256(tuple(records)) == expected


def test_generated_from_is_sorted_unique_sha256_tuple() -> None:
    assert _envelope().generated_from == (HASH_A, HASH_B)
    with pytest.raises(ValueError, match="generated_from"):
        _envelope(generated_from=[HASH_B, HASH_A])
    with pytest.raises(ValueError, match="generated_from"):
        _envelope(generated_from=[HASH_A, HASH_A])
    with pytest.raises(ValueError, match="generated_from"):
        _envelope(generated_from=["not-a-sha256"])


def _file_payload(
    records: list[object],
    *,
    schema_version: str = "domain-calibration-file-v1",
    generated_from: list[str] | None = None,
    contains_real_personal_data: bool = False,
) -> dict[str, object]:
    record_values = [asdict(record) for record in records]
    return {
        "schema_version": schema_version,
        "suite_version": "domain-calibration-suite-v1",
        "generated_from": generated_from or [],
        "contains_real_personal_data": contains_real_personal_data,
        "payload_sha256": records_payload_sha256(record_values),
        "records": record_values,
    }


def _write_payload(path: Path, payload: object, *, canonical: bool = True) -> None:
    if canonical:
        path.write_bytes(canonical_json_bytes(payload))
    else:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@pytest.mark.parametrize(
    ("record", "record_type", "primary_id"),
    [
        (_fixture(), CalibrationInputFixture, "fixture-001"),
        (_case(), CalibrationCase, "case-001"),
        (_assertion(), CalibrationAssertion, "assertion-001"),
        (_citation(), CalibrationCitation, "citation-001"),
        (_packet(), ReviewerPacket, "packet-001"),
        (_assignment(), ReviewAssignment, "assignment-a-001"),
        (_review(), CalibrationReview, "review-a-001"),
        (_adjudication(), AdjudicationDecision, "adjudication-001"),
        (_run(), CalibrationRun, "run-001"),
        (_snapshot(), MetricSnapshotV1, "snapshot-001"),
    ],
)
def test_loader_constructs_every_standalone_record_type(
    tmp_path: Path,
    record: object,
    record_type: type,
    primary_id: str,
) -> None:
    path = tmp_path / "records.json"
    _write_payload(path, _file_payload([record]))

    envelope = load_calibration_file(path, record_type)

    assert type(envelope.records[0]) is record_type
    assert getattr(envelope.records[0], MODEL_FIELDS[record_type][0]) == primary_id


def test_release_loader_requires_single_release_schema_record(tmp_path: Path) -> None:
    path = tmp_path / "release.json"
    _write_payload(
        path,
        _file_payload(
            [_release()],
            schema_version="domain-calibration-release-v1",
        ),
    )

    envelope = load_calibration_file(path, CalibrationReleaseDecision)

    assert envelope.schema_version == "domain-calibration-release-v1"
    assert envelope.records == (_release(),)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_root_key",
        "extra_root_key",
        "malformed_records",
        "hash_mismatch",
        "privacy_true",
        "noncanonical",
        "unsorted_records",
        "duplicate_primary_id",
    ],
)
def test_loader_rejects_invalid_envelopes(
    tmp_path: Path,
    mutation: str,
) -> None:
    path = tmp_path / "cases.json"
    payload = _file_payload([_case(case_id="case-001")])
    canonical = True
    if mutation == "missing_root_key":
        payload.pop("suite_version")
    elif mutation == "extra_root_key":
        payload["extra"] = "forbidden"
    elif mutation == "malformed_records":
        payload["records"] = {}
    elif mutation == "hash_mismatch":
        payload["payload_sha256"] = HASH_B
    elif mutation == "privacy_true":
        payload["contains_real_personal_data"] = True
    elif mutation == "noncanonical":
        canonical = False
    elif mutation == "unsorted_records":
        payload = _file_payload(
            [_case(case_id="case-002"), _case(case_id="case-001")]
        )
    elif mutation == "duplicate_primary_id":
        payload = _file_payload([_case(), _case()])
    _write_payload(path, payload, canonical=canonical)

    with pytest.raises(CalibrationProtocolError):
        load_calibration_file(path, CalibrationCase)


def test_loader_rejects_duplicate_json_keys_and_malformed_values(
    tmp_path: Path,
) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_bytes(
        b'{"schema_version":"domain-calibration-file-v1",'
        b'"schema_version":"domain-calibration-file-v1"}'
    )
    malformed = tmp_path / "malformed.json"
    payload = _file_payload([_case()])
    payload["records"][0]["case_id"] = 7  # type: ignore[index]
    payload["payload_sha256"] = records_payload_sha256(payload["records"])
    _write_payload(malformed, payload)

    with pytest.raises(CalibrationProtocolError):
        load_calibration_file(duplicate, CalibrationCase)
    with pytest.raises(CalibrationProtocolError):
        load_calibration_file(malformed, CalibrationCase)


def test_loader_rejects_record_missing_or_extra_fields(tmp_path: Path) -> None:
    for filename, mutate in (
        ("missing.json", lambda record: record.pop("claim_scope")),
        ("extra.json", lambda record: record.update({"extra": "forbidden"})),
    ):
        path = tmp_path / filename
        payload = _file_payload([_case()])
        mutate(payload["records"][0])  # type: ignore[index]
        payload["payload_sha256"] = records_payload_sha256(payload["records"])
        _write_payload(path, payload)
        with pytest.raises(CalibrationProtocolError):
            load_calibration_file(path, CalibrationCase)


def test_privacy_is_false_at_envelope_and_case_levels() -> None:
    with pytest.raises(ValueError, match="personal data"):
        _envelope(contains_real_personal_data=True)
    with pytest.raises(ValueError, match="personal data"):
        _case(contains_real_personal_data=True)


def test_authoritative_rule_families_and_school_ids_have_no_second_allowlist() -> None:
    rule_families = get_authoritative_rule_family_ids()
    school_version, school_ids = load_authoritative_school_profile_identity()

    assert rule_families == get_formal_interpretation_rule_families()
    assert rule_families == (
        "pattern_strength",
        "five_element_balance",
        "useful_god_candidate",
        "taboo_god_candidate",
        "ten_god_relation",
        "branch_interaction",
        "blind_image_method",
        "luck_cycle",
        "remedy_boundary",
        "high_risk_signal",
    )
    assert school_version == "school-profiles-v1"
    assert school_ids == ("ziping", "liang_xiangrun", "duan")
    with pytest.raises(ValueError, match="rule_family"):
        _assertion(rule_family="invented-family")
    with pytest.raises(ValueError, match="school_id"):
        _assertion(school_id="invented-school")


@pytest.mark.parametrize("label", ["accept", "revise", "reject"])
def test_non_abstain_review_requires_expected_status(label: str) -> None:
    assert _review(label=label).label == label
    with pytest.raises(ValueError, match="expected status"):
        _review(label=label, expected_statuses=[])


def test_abstain_is_only_empty_expectation_review_label() -> None:
    review = _review(
        label="abstain",
        expected_statuses=[],
        acceptable_values=[],
    )

    assert review.expected_statuses == ()
    assert review.acceptable_values == ()
    with pytest.raises(ValueError, match="abstain"):
        _review(label="abstain", expected_statuses=["computed"])
    with pytest.raises(ValueError, match="label"):
        _review(label="maybe")


def _reference_graph() -> dict[str, tuple[object, ...]]:
    packet = _packet()
    packet_hash = sha256(canonical_json_bytes(packet)).hexdigest()
    return {
        "fixtures": (_fixture(),),
        "cases": (_case(),),
        "assertions": (_assertion(required_evidence_ids=[]),),
        "citations": (_citation(evidence_ids=[]),),
        "packets": (packet,),
        "assignments": (
            _assignment(packet_sha256=packet_hash),
            _assignment(
                assignment_id="assignment-b-001",
                reviewer_id="reviewer-b",
                packet_sha256=packet_hash,
            ),
        ),
        "reviews": (
            _review(evidence_ids=[], packet_sha256=packet_hash),
            _review(
                review_id="review-b-001",
                assignment_id="assignment-b-001",
                evidence_ids=[],
                packet_sha256=packet_hash,
            ),
        ),
        "adjudications": (_adjudication(evidence_ids=[]),),
        "runs": (_run(),),
    }


def test_cross_reference_graph_accepts_only_resolved_distinct_records() -> None:
    validate_calibration_references(**_reference_graph())


@pytest.mark.parametrize(
    ("collection", "replacement"),
    [
        ("cases", (_case(input_fixture_id="missing-fixture"),)),
        ("assertions", (_assertion(case_id="missing-case", required_evidence_ids=[]),)),
        ("citations", (_citation(assertion_id="missing-assertion", evidence_ids=[]),)),
        ("packets", (_packet(citation_ids=["missing-citation"]),)),
        ("assignments", (_assignment(packet_id="missing-packet"),)),
        ("reviews", (_review(assignment_id="missing-assignment", evidence_ids=[]),)),
        (
            "adjudications",
            (_adjudication(reviewer_b_review_id="missing-review", evidence_ids=[]),),
        ),
        (
            "runs",
            (_run(assertion_results=[_assertion_result(assertion_id="missing")]),),
        ),
    ],
)
def test_cross_reference_errors_are_rejected(
    collection: str,
    replacement: tuple[object, ...],
) -> None:
    graph = _reference_graph()
    graph[collection] = replacement

    with pytest.raises(CalibrationProtocolError, match="reference"):
        validate_calibration_references(**graph)


def test_duplicate_primary_ids_and_reviewer_identity_collisions_are_rejected() -> None:
    duplicate_cases = _reference_graph()
    duplicate_cases["cases"] = (_case(), _case())
    with pytest.raises(CalibrationProtocolError, match="duplicate"):
        validate_calibration_references(**duplicate_cases)

    same_reviewer = _reference_graph()
    packet_hash = sha256(
        canonical_json_bytes(same_reviewer["packets"][0])
    ).hexdigest()
    same_reviewer["assignments"] = (
        _assignment(packet_sha256=packet_hash),
        _assignment(
            assignment_id="assignment-b-001",
            reviewer_id="reviewer-a",
            packet_sha256=packet_hash,
        ),
    )
    with pytest.raises(CalibrationProtocolError, match="reviewer"):
        validate_calibration_references(**same_reviewer)


def test_loader_is_read_only_and_never_repairs_input(tmp_path: Path) -> None:
    valid_path = tmp_path / "valid.json"
    invalid_path = tmp_path / "invalid.json"
    _write_payload(valid_path, _file_payload([_case()]))
    _write_payload(invalid_path, _file_payload([_case()]), canonical=False)
    valid_before = valid_path.read_bytes()
    invalid_before = invalid_path.read_bytes()
    valid_mtime = valid_path.stat().st_mtime_ns
    invalid_mtime = invalid_path.stat().st_mtime_ns

    load_calibration_file(valid_path, CalibrationCase)
    with pytest.raises(CalibrationProtocolError):
        load_calibration_file(invalid_path, CalibrationCase)

    assert valid_path.read_bytes() == valid_before
    assert invalid_path.read_bytes() == invalid_before
    assert valid_path.stat().st_mtime_ns == valid_mtime
    assert invalid_path.stat().st_mtime_ns == invalid_mtime
