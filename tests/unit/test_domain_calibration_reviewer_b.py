from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib import resources
from importlib.resources.abc import Traversable
import json
from pathlib import Path

import pytest

from mingli_engine.domain_calibration import (
    canonical_json_bytes,
    load_calibration_file,
    records_payload_sha256,
    validate_calibration_references,
)
from mingli_engine.domain_calibration_models import (
    CalibrationAssertion,
    CalibrationCase,
    CalibrationCitation,
    CalibrationFileEnvelopeV1,
    CalibrationInputFixture,
    CalibrationReview,
    ReviewerPacket,
    ReviewAssignment,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
ASSIGNMENTS_FILENAME = "reviewer_b_assignments.json"
REVIEWS_FILENAME = "reviewer_b_reviews.json"
REVIEWER_B_ID = "reviewer-b-independent-v1"
ACCESS_MANIFEST = (
    "provided_packet_bytes_only",
    "tools_disabled",
    "filesystem_disabled",
    "peer_labels_absent",
    "engine_output_absent",
)
ALLOWED_LABELS = {"accept", "revise", "reject", "abstain"}


@dataclass(frozen=True)
class _ReviewerBData:
    root: Traversable
    fixtures: CalibrationFileEnvelopeV1[CalibrationInputFixture]
    cases: CalibrationFileEnvelopeV1[CalibrationCase]
    assertions: CalibrationFileEnvelopeV1[CalibrationAssertion]
    citations: CalibrationFileEnvelopeV1[CalibrationCitation]
    packets: CalibrationFileEnvelopeV1[ReviewerPacket]
    assignments: CalibrationFileEnvelopeV1[ReviewAssignment]
    reviews: CalibrationFileEnvelopeV1[CalibrationReview]


def _resource_root() -> Traversable:
    return resources.files("mingli_engine").joinpath("data/domain_calibration")


def _load_reviewer_b_data() -> _ReviewerBData:
    root = _resource_root()
    missing = [
        filename
        for filename in (ASSIGNMENTS_FILENAME, REVIEWS_FILENAME)
        if not root.joinpath(filename).is_file()
    ]
    assert missing == [], f"missing Reviewer B resources: {missing}"
    return _ReviewerBData(
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
        assignments=load_calibration_file(
            root.joinpath(ASSIGNMENTS_FILENAME),
            ReviewAssignment,
        ),
        reviews=load_calibration_file(
            root.joinpath(REVIEWS_FILENAME),
            CalibrationReview,
        ),
    )


@pytest.fixture(scope="module")
def reviewer_b_data() -> _ReviewerBData:
    return _load_reviewer_b_data()


def _packet_hash(packet: ReviewerPacket) -> str:
    return sha256(canonical_json_bytes(packet)).hexdigest()


def test_reviewer_b_covers_every_packet_exactly_once(
    reviewer_b_data: _ReviewerBData,
) -> None:
    packet_ids = {packet.packet_id for packet in reviewer_b_data.packets.records}
    assignments_by_packet: dict[str, list[ReviewAssignment]] = {}
    for assignment in reviewer_b_data.assignments.records:
        assignments_by_packet.setdefault(assignment.packet_id, []).append(assignment)
    reviews_by_assignment: dict[str, list[CalibrationReview]] = {}
    for review in reviewer_b_data.reviews.records:
        reviews_by_assignment.setdefault(review.assignment_id, []).append(review)

    assert len(packet_ids) == 43
    assert len(reviewer_b_data.assignments.records) == 43
    assert len(reviewer_b_data.reviews.records) == 43
    assert set(assignments_by_packet) == packet_ids
    assert all(len(records) == 1 for records in assignments_by_packet.values())
    assert set(reviews_by_assignment) == {
        assignment.assignment_id
        for assignment in reviewer_b_data.assignments.records
    }
    assert all(len(records) == 1 for records in reviews_by_assignment.values())


def test_reviewer_b_uses_unique_record_ids_and_one_stable_identity(
    reviewer_b_data: _ReviewerBData,
) -> None:
    assignment_ids = tuple(
        assignment.assignment_id
        for assignment in reviewer_b_data.assignments.records
    )
    review_ids = tuple(review.review_id for review in reviewer_b_data.reviews.records)
    reviewer_ids = {
        assignment.reviewer_id
        for assignment in reviewer_b_data.assignments.records
    }

    assert len(assignment_ids) == len(set(assignment_ids)) == 43
    assert len(review_ids) == len(set(review_ids)) == 43
    assert reviewer_ids == {REVIEWER_B_ID}
    assert all("reviewer-a" not in value for value in (*assignment_ids, *review_ids))


def test_reviewer_b_identity_ids_and_packet_hashes_are_distinct_from_reviewer_a(
    reviewer_b_data: _ReviewerBData,
) -> None:
    reviewer_a_assignments = load_calibration_file(
        reviewer_b_data.root.joinpath("reviewer_a_assignments.json"),
        ReviewAssignment,
    )
    reviewer_a_reviews = load_calibration_file(
        reviewer_b_data.root.joinpath("reviewer_a_reviews.json"),
        CalibrationReview,
    )
    reviewer_a_ids = {
        assignment.reviewer_id
        for assignment in reviewer_a_assignments.records
    }
    reviewer_b_ids = {
        assignment.reviewer_id
        for assignment in reviewer_b_data.assignments.records
    }

    assert reviewer_a_ids.isdisjoint(reviewer_b_ids)
    assert {
        assignment.assignment_id
        for assignment in reviewer_a_assignments.records
    }.isdisjoint(
        assignment.assignment_id
        for assignment in reviewer_b_data.assignments.records
    )
    assert {review.review_id for review in reviewer_a_reviews.records}.isdisjoint(
        review.review_id for review in reviewer_b_data.reviews.records
    )
    assert {
        assignment.packet_id: assignment.packet_sha256
        for assignment in reviewer_a_assignments.records
    } == {
        assignment.packet_id: assignment.packet_sha256
        for assignment in reviewer_b_data.assignments.records
    }


def test_assignments_declare_exact_independent_access_contract(
    reviewer_b_data: _ReviewerBData,
) -> None:
    for assignment in reviewer_b_data.assignments.records:
        assert assignment.reviewer_kind == "agent_independent"
        assert assignment.access_manifest == ACCESS_MANIFEST
        assert assignment.peer_labels_hidden is True
        assert assignment.engine_output_hidden is True
        assert assignment.independence_attested is True


def test_assignment_and_review_hashes_match_frozen_packet_bytes(
    reviewer_b_data: _ReviewerBData,
) -> None:
    packets_by_id = {
        packet.packet_id: packet for packet in reviewer_b_data.packets.records
    }
    assignments_by_id = {
        assignment.assignment_id: assignment
        for assignment in reviewer_b_data.assignments.records
    }

    assert {
        assignment.packet_sha256
        for assignment in reviewer_b_data.assignments.records
    } == {_packet_hash(packet) for packet in reviewer_b_data.packets.records}
    for assignment in reviewer_b_data.assignments.records:
        assert assignment.packet_sha256 == _packet_hash(
            packets_by_id[assignment.packet_id]
        )
    for review in reviewer_b_data.reviews.records:
        assert review.packet_sha256 == assignments_by_id[
            review.assignment_id
        ].packet_sha256


def test_review_labels_and_abstentions_follow_protocol(
    reviewer_b_data: _ReviewerBData,
) -> None:
    for review in reviewer_b_data.reviews.records:
        assert review.label in ALLOWED_LABELS
        if review.label == "abstain":
            assert review.expected_statuses == ()
            assert review.acceptable_values == ()
        else:
            assert review.expected_statuses


def test_reviews_have_bounded_confidence_rationale_and_evidence(
    reviewer_b_data: _ReviewerBData,
) -> None:
    assignments_by_id = {
        assignment.assignment_id: assignment
        for assignment in reviewer_b_data.assignments.records
    }
    packets_by_id = {
        packet.packet_id: packet for packet in reviewer_b_data.packets.records
    }

    for review in reviewer_b_data.reviews.records:
        assignment = assignments_by_id[review.assignment_id]
        packet = packets_by_id[assignment.packet_id]
        assert 0.0 < review.confidence <= 1.0
        assert review.rationale.strip() == review.rationale
        assert len(review.rationale) >= 20
        assert review.evidence_ids
        assert review.source_locators
        assert set(review.evidence_ids) <= set(
            packet.assertion.candidate_evidence_ids
        )
        assert set(review.source_locators) <= set(packet.source_locators)
        if review.label != "abstain":
            assert set(review.expected_statuses) <= set(
                packet.assertion.candidate_statuses
            )
            assert set(review.acceptable_values) <= set(
                packet.assertion.candidate_values
            )
        assert review.assertion_id == packet.assertion.assertion_id


def test_reviews_contain_no_forbidden_context_references(
    reviewer_b_data: _ReviewerBData,
) -> None:
    forbidden_fragments = (
        "filesystem",
        "tool call",
        "engine output",
        "peer review",
        "reviewer a",
        "reviewer b",
        "adjudication",
        "tests/",
        "src/",
        str(REPO_ROOT).casefold(),
    )

    for review in reviewer_b_data.reviews.records:
        rationale = review.rationale.casefold()
        assert all(fragment.casefold() not in rationale for fragment in forbidden_fragments)
    serialized = canonical_json_bytes(
        {
            "assignments": reviewer_b_data.assignments.records,
            "reviews": reviewer_b_data.reviews.records,
        }
    ).decode("utf-8")
    assert "reviewer-a" not in serialized.casefold()


def test_reviewer_b_envelopes_are_canonical_private_sorted_and_hashed(
    reviewer_b_data: _ReviewerBData,
) -> None:
    envelopes = (
        (reviewer_b_data.assignments, "assignment_id"),
        (reviewer_b_data.reviews, "review_id"),
    )
    for envelope, primary_id in envelopes:
        assert envelope.contains_real_personal_data is False
        assert envelope.generated_from == tuple(sorted(envelope.generated_from))
        assert envelope.payload_sha256 == records_payload_sha256(envelope.records)
        primary_ids = tuple(
            getattr(record, primary_id) for record in envelope.records
        )
        assert primary_ids == tuple(sorted(primary_ids))
        assert len(primary_ids) == len(set(primary_ids))

    assert reviewer_b_data.assignments.generated_from == (
        reviewer_b_data.packets.payload_sha256,
    )
    assert reviewer_b_data.reviews.generated_from == tuple(
        sorted(
            (
                reviewer_b_data.assignments.payload_sha256,
                reviewer_b_data.packets.payload_sha256,
            )
        )
    )


def test_reviewer_b_cross_references_are_complete(
    reviewer_b_data: _ReviewerBData,
) -> None:
    validate_calibration_references(
        fixtures=reviewer_b_data.fixtures.records,
        cases=reviewer_b_data.cases.records,
        assertions=reviewer_b_data.assertions.records,
        citations=reviewer_b_data.citations.records,
        packets=reviewer_b_data.packets.records,
        assignments=reviewer_b_data.assignments.records,
        reviews=reviewer_b_data.reviews.records,
    )


def test_reviewer_b_resources_are_strict_canonical_json(
    reviewer_b_data: _ReviewerBData,
) -> None:
    for filename in (ASSIGNMENTS_FILENAME, REVIEWS_FILENAME):
        payload = reviewer_b_data.root.joinpath(filename).read_bytes()
        assert payload == canonical_json_bytes(json.loads(payload.decode("utf-8")))
        assert payload[-1:] == b"}"


def test_reviewer_b_loader_is_read_only() -> None:
    root = _resource_root()
    paths_and_types = (
        (root.joinpath(ASSIGNMENTS_FILENAME), ReviewAssignment),
        (root.joinpath(REVIEWS_FILENAME), CalibrationReview),
    )
    before = {
        str(path): sha256(path.read_bytes()).hexdigest()
        for path, _record_type in paths_and_types
    }

    for path, record_type in paths_and_types:
        load_calibration_file(path, record_type)

    after = {
        str(path): sha256(path.read_bytes()).hexdigest()
        for path, _record_type in paths_and_types
    }
    assert after == before


def test_reviewer_b_records_have_only_protocol_fields(
    reviewer_b_data: _ReviewerBData,
) -> None:
    assignment_fields = set(asdict(reviewer_b_data.assignments.records[0]))
    review_fields = set(asdict(reviewer_b_data.reviews.records[0]))
    assert assignment_fields == {
        "assignment_id",
        "reviewer_id",
        "reviewer_kind",
        "packet_id",
        "packet_sha256",
        "access_manifest",
        "peer_labels_hidden",
        "engine_output_hidden",
        "independence_attested",
    }
    assert review_fields == {
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
    }
