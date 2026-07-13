from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib import resources
from importlib.resources.abc import Traversable
import json
from pathlib import Path

import pytest

from mingli_engine.classical_sources import load_approved_evidence_units
from mingli_engine.domain_calibration import (
    canonical_json_bytes,
    get_authoritative_rule_family_ids,
    load_authoritative_school_profile_identity,
    load_calibration_file,
    records_payload_sha256,
    validate_calibration_references,
)
from mingli_engine.domain_calibration_models import (
    BlindedAssertionProjection,
    CalibrationAssertion,
    CalibrationCase,
    CalibrationCitation,
    CalibrationFileEnvelopeV1,
    CalibrationInputFixture,
    ReviewerPacket,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_FILENAMES = (
    "input_fixtures.json",
    "calibration_cases.json",
    "calibration_assertions.json",
    "calibration_citations.json",
    "reviewer_packets.json",
)
SOURCE_LINEAGE_PATHS = {
    "verified_charts.json": (
        REPO_ROOT / "tests/fixtures/bazi_calculation/verified_charts.json"
    ),
    "pattern_counterexamples.json": (
        REPO_ROOT / "tests/fixtures/bazi_calculation/pattern_counterexamples.json"
    ),
    "strength_boundary_cases.json": (
        REPO_ROOT / "tests/fixtures/bazi_calculation/strength_boundary_cases.json"
    ),
    "luck_cycle_boundary_cases.json": (
        REPO_ROOT / "tests/fixtures/bazi_calculation/luck_cycle_boundary_cases.json"
    ),
    "source_conflicts.json": (
        REPO_ROOT
        / "src/mingli_engine/data/classical_sources/source_conflicts.json"
    ),
    "test_real_use_safety.py": REPO_ROOT / "tests/safety/test_real_use_safety.py",
}
ACCESS_MANIFEST = (
    "provided_packet_bytes_only",
    "tools_disabled",
    "filesystem_disabled",
    "peer_labels_absent",
    "engine_output_absent",
)


@dataclass(frozen=True)
class _Corpus:
    root: Traversable
    fixtures: CalibrationFileEnvelopeV1[CalibrationInputFixture]
    cases: CalibrationFileEnvelopeV1[CalibrationCase]
    assertions: CalibrationFileEnvelopeV1[CalibrationAssertion]
    citations: CalibrationFileEnvelopeV1[CalibrationCitation]
    packets: CalibrationFileEnvelopeV1[ReviewerPacket]


def _resource_root() -> Traversable:
    return resources.files("mingli_engine").joinpath("data/domain_calibration")


def _load_corpus() -> _Corpus:
    root = _resource_root()
    missing = [name for name in RESOURCE_FILENAMES if not root.joinpath(name).is_file()]
    assert missing == [], f"missing packaged calibration resources: {missing}"
    return _Corpus(
        root=root,
        fixtures=load_calibration_file(
            root.joinpath("input_fixtures.json"),
            CalibrationInputFixture,
        ),
        cases=load_calibration_file(
            root.joinpath("calibration_cases.json"),
            CalibrationCase,
        ),
        assertions=load_calibration_file(
            root.joinpath("calibration_assertions.json"),
            CalibrationAssertion,
        ),
        citations=load_calibration_file(
            root.joinpath("calibration_citations.json"),
            CalibrationCitation,
        ),
        packets=load_calibration_file(
            root.joinpath("reviewer_packets.json"),
            ReviewerPacket,
        ),
    )


@pytest.fixture(scope="module")
def corpus() -> _Corpus:
    return _load_corpus()


def _ids(records: tuple[object, ...], field_name: str) -> tuple[str, ...]:
    return tuple(getattr(record, field_name) for record in records)


def test_corpus_has_exact_packaged_files_and_minimum_record_counts(
    corpus: _Corpus,
) -> None:
    assert tuple(sorted(item.name for item in corpus.root.iterdir())) == tuple(
        sorted(RESOURCE_FILENAMES)
    )
    assert len(corpus.fixtures.records) == 11
    assert len(corpus.cases.records) == 11
    assert len(corpus.assertions.records) == 43
    assert len(corpus.citations.records) == 43
    assert len(corpus.packets.records) == 43


def test_every_authoritative_rule_family_has_required_assertion_kinds(
    corpus: _Corpus,
) -> None:
    expected_families = get_authoritative_rule_family_ids()
    observed_families = tuple(
        sorted({record.rule_family for record in corpus.assertions.records})
    )

    assert observed_families == tuple(sorted(expected_families))
    for family in expected_families:
        kinds = {
            record.assertion_kind
            for record in corpus.assertions.records
            if record.rule_family == family
        }
        assert {"positive", "counterexample"} <= kinds
        assert kinds.intersection({"boundary", "abstention"})


def test_every_enabled_school_has_agreement_disagreement_counterexample_and_abstention(
    corpus: _Corpus,
) -> None:
    _version, enabled_schools = load_authoritative_school_profile_identity()

    for school_id in enabled_schools:
        school_assertions = tuple(
            record
            for record in corpus.assertions.records
            if record.school_id == school_id
        )
        assert any(
            record.assertion_kind == "positive"
            and "school_agreement" in record.acceptable_values
            for record in school_assertions
        )
        assert any(
            record.assertion_kind == "disagreement"
            for record in school_assertions
        )
        assert any(
            record.assertion_kind == "counterexample"
            for record in school_assertions
        )
        assert any(
            record.assertion_kind == "abstention"
            and record.acceptable_statuses == ("not_computed",)
            for record in school_assertions
        )


def test_required_boundary_cases_and_source_fixture_ids_are_frozen(
    corpus: _Corpus,
) -> None:
    required_tags = {
        "calendrical_cross_provider",
        "dependency_degradation",
        "empty_branch_relations",
        "severe_conflict",
        "unknown_gender",
        "aware_datetime_utc_plus_08_rejection",
        "aware_datetime_utc_rejection",
        "aware_datetime_utc_minus_05_rejection",
        "high_risk_refusal",
    }
    observed_tags = {
        tag for case in corpus.cases.records for tag in case.coverage_tags
    }
    required_source_fixture_ids = {
        "strength_indeterminate_prerequisite",
        "synthetic_01_19961215_0930",
        "conflict_high_risk_scope_001",
        "unknown_gender_luck_prerequisite",
        "aware_datetime_utc_plus_08_rejected_before_provider",
        "aware_datetime_utc_rejected_before_provider",
        "aware_datetime_utc_minus_05_rejected_before_provider",
        "safety_high_risk_lifespan_refusal_001",
    }

    assert required_tags <= observed_tags
    assert required_source_fixture_ids <= {
        case.source_fixture_id for case in corpus.cases.records
    }
    assert "calendrical" in {case.stratum for case in corpus.cases.records}
    assert "school" in {case.stratum for case in corpus.cases.records}


def test_fixture_and_case_lineage_hashes_resolve_without_runtime_test_reads(
    corpus: _Corpus,
) -> None:
    fixtures_by_id = {
        fixture.fixture_id: fixture for fixture in corpus.fixtures.records
    }
    expected_hashes = {
        filename: sha256(path.read_bytes()).hexdigest()
        for filename, path in SOURCE_LINEAGE_PATHS.items()
    }

    for fixture in corpus.fixtures.records:
        assert fixture.source_fixture_file in expected_hashes
        assert fixture.source_fixture_sha256 == expected_hashes[
            fixture.source_fixture_file
        ]
        assert "/" not in fixture.source_fixture_file
        assert "\\" not in fixture.source_fixture_file
        assert fixture.request_payload["synthetic"] is True
    for case in corpus.cases.records:
        fixture = fixtures_by_id[case.input_fixture_id]
        assert case.input_fixture_file == "input_fixtures.json"
        assert case.input_sha256 == sha256(
            canonical_json_bytes(fixture.request_payload)
        ).hexdigest()
        assert case.source_fixture_file == fixture.source_fixture_file
        assert case.source_fixture_id == fixture.source_fixture_id
        assert case.source_fixture_sha256 == fixture.source_fixture_sha256


def test_all_envelopes_are_private_canonical_sorted_and_records_hashed(
    corpus: _Corpus,
) -> None:
    envelopes = (
        (corpus.fixtures, "fixture_id"),
        (corpus.cases, "case_id"),
        (corpus.assertions, "assertion_id"),
        (corpus.citations, "citation_id"),
        (corpus.packets, "packet_id"),
    )

    for envelope, primary_id in envelopes:
        assert envelope.contains_real_personal_data is False
        assert envelope.generated_from == tuple(sorted(envelope.generated_from))
        assert envelope.payload_sha256 == records_payload_sha256(envelope.records)
        record_ids = _ids(envelope.records, primary_id)
        assert record_ids == tuple(sorted(record_ids))
        assert len(record_ids) == len(set(record_ids))
    assert all(case.contains_real_personal_data is False for case in corpus.cases.records)


def test_corpus_has_complete_cross_references_and_one_to_one_records(
    corpus: _Corpus,
) -> None:
    validate_calibration_references(
        fixtures=corpus.fixtures.records,
        cases=corpus.cases.records,
        assertions=corpus.assertions.records,
        citations=corpus.citations.records,
        packets=corpus.packets.records,
    )
    assertion_ids = _ids(corpus.assertions.records, "assertion_id")
    assert _ids(corpus.citations.records, "assertion_id") == assertion_ids
    assert tuple(packet.assertion.assertion_id for packet in corpus.packets.records) == (
        assertion_ids
    )


def test_citations_use_only_approved_evidence_and_tracked_locators(
    corpus: _Corpus,
) -> None:
    evidence_by_id = {
        unit.evidence_id: unit for unit in load_approved_evidence_units()
    }

    for citation in corpus.citations.records:
        assert citation.evidence_ids
        assert citation.rule_ids
        assert citation.source_locators
        for evidence_id in citation.evidence_ids:
            assert evidence_id in evidence_by_id
            assert evidence_by_id[evidence_id].source_ref in citation.source_locators


def test_packets_embed_only_blinded_projection_and_exact_access_manifest(
    corpus: _Corpus,
) -> None:
    for packet in corpus.packets.records:
        assert type(packet.assertion) is BlindedAssertionProjection
        assert packet.access_manifest == ACCESS_MANIFEST
        assert len(packet.citation_ids) == 1
        assert set(packet.evidence_excerpts) == set(
            packet.assertion.candidate_evidence_ids
        )
        assert packet.rule_scope == packet.assertion.candidate_rule_ids


def test_packet_hash_is_canonical_hash_of_packet_value_alone(
    corpus: _Corpus,
) -> None:
    packet_hashes = tuple(
        sha256(canonical_json_bytes(packet)).hexdigest()
        for packet in corpus.packets.records
    )

    assert len(packet_hashes) == len(set(packet_hashes))
    for packet, packet_hash in zip(corpus.packets.records, packet_hashes, strict=True):
        assert packet_hash == sha256(
            canonical_json_bytes(asdict(packet))
        ).hexdigest()
        assert packet_hash != sha256(
            canonical_json_bytes({"packet": asdict(packet)})
        ).hexdigest()


def _walk_mappings(value: object) -> tuple[dict[str, object], ...]:
    mappings: list[dict[str, object]] = []
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            mappings.append(current)
            pending.extend(current.values())
        elif isinstance(current, (list, tuple)):
            pending.extend(current)
    return tuple(mappings)


def test_packets_exclude_engine_results_final_expectations_peer_labels_and_paths(
    corpus: _Corpus,
) -> None:
    forbidden_keys = {
        "engine_output",
        "result",
        "actual_status",
        "actual_values",
        "expected_statuses",
        "final_statuses",
        "final_acceptable_values",
        "peer_labels",
        "review_label",
        "adjudication",
        "hidden_fields",
    }

    for packet in corpus.packets.records:
        value = asdict(packet)
        assert all(
            forbidden_keys.isdisjoint(mapping)
            for mapping in _walk_mappings(value)
        )
        serialized = canonical_json_bytes(value).decode("utf-8")
        assert "tests/" not in serialized
        assert "src/" not in serialized
        assert str(REPO_ROOT) not in serialized
        assert "\\\u547d\u7406\u6f14\u7ece\\" not in serialized


def test_packet_content_is_allowlisted_to_its_assertion_and_citation(
    corpus: _Corpus,
) -> None:
    citations_by_id = {
        citation.citation_id: citation for citation in corpus.citations.records
    }
    evidence_by_id = {
        unit.evidence_id: unit for unit in load_approved_evidence_units()
    }

    for packet in corpus.packets.records:
        citation = citations_by_id[packet.citation_ids[0]]
        assert citation.assertion_id == packet.assertion.assertion_id
        assert packet.source_locators == citation.source_locators
        assert packet.rule_scope == citation.rule_ids
        assert packet.evidence_excerpts == {
            evidence_id: evidence_by_id[evidence_id].summary
            for evidence_id in citation.evidence_ids
        }


def test_resource_bytes_are_canonical_and_load_without_checkout_fallback(
    corpus: _Corpus,
) -> None:
    root_text = str(corpus.root).replace("\\", "/")
    assert "/tests/" not in root_text

    for filename in RESOURCE_FILENAMES:
        resource = corpus.root.joinpath(filename)
        payload = resource.read_bytes()
        assert payload == canonical_json_bytes(
            json.loads(payload.decode("utf-8"))
        )
