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
    AdjudicationDecision,
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
ADJUDICATION_FILENAME = "adjudication.json"
ADJUDICATOR_ID = "adjudicator-independent-v1"
ALLOWED_DECISIONS = {
    "agreement",
    "clerical_correction",
    "retained_alternative",
    "unresolved_disagreement",
}


@dataclass(frozen=True)
class _AdjudicationData:
    root: Traversable
    fixtures: CalibrationFileEnvelopeV1[CalibrationInputFixture]
    cases: CalibrationFileEnvelopeV1[CalibrationCase]
    assertions: CalibrationFileEnvelopeV1[CalibrationAssertion]
    citations: CalibrationFileEnvelopeV1[CalibrationCitation]
    packets: CalibrationFileEnvelopeV1[ReviewerPacket]
    reviewer_a_assignments: CalibrationFileEnvelopeV1[ReviewAssignment]
    reviewer_a_reviews: CalibrationFileEnvelopeV1[CalibrationReview]
    reviewer_b_assignments: CalibrationFileEnvelopeV1[ReviewAssignment]
    reviewer_b_reviews: CalibrationFileEnvelopeV1[CalibrationReview]
    adjudications: CalibrationFileEnvelopeV1[AdjudicationDecision]


def _resource_root() -> Traversable:
    return resources.files("mingli_engine").joinpath("data/domain_calibration")


def _load_data() -> _AdjudicationData:
    root = _resource_root()
    assert root.joinpath(ADJUDICATION_FILENAME).is_file(), (
        "missing adjudication resource: adjudication.json"
    )
    return _AdjudicationData(
        root=root,
        fixtures=load_calibration_file(
            root.joinpath("input_fixtures.json"), CalibrationInputFixture
        ),
        cases=load_calibration_file(
            root.joinpath("calibration_cases.json"), CalibrationCase
        ),
        assertions=load_calibration_file(
            root.joinpath("calibration_assertions.json"), CalibrationAssertion
        ),
        citations=load_calibration_file(
            root.joinpath("calibration_citations.json"), CalibrationCitation
        ),
        packets=load_calibration_file(
            root.joinpath("reviewer_packets.json"), ReviewerPacket
        ),
        reviewer_a_assignments=load_calibration_file(
            root.joinpath("reviewer_a_assignments.json"), ReviewAssignment
        ),
        reviewer_a_reviews=load_calibration_file(
            root.joinpath("reviewer_a_reviews.json"), CalibrationReview
        ),
        reviewer_b_assignments=load_calibration_file(
            root.joinpath("reviewer_b_assignments.json"), ReviewAssignment
        ),
        reviewer_b_reviews=load_calibration_file(
            root.joinpath("reviewer_b_reviews.json"), CalibrationReview
        ),
        adjudications=load_calibration_file(
            root.joinpath(ADJUDICATION_FILENAME), AdjudicationDecision
        ),
    )


@pytest.fixture(scope="module")
def data() -> _AdjudicationData:
    return _load_data()


def _review_signature(review: CalibrationReview) -> tuple[object, ...]:
    return (review.label, review.expected_statuses, review.acceptable_values)


def _reviews_by_assertion(
    reviews: tuple[CalibrationReview, ...],
) -> dict[str, CalibrationReview]:
    return {review.assertion_id: review for review in reviews}


def test_every_assertion_has_exactly_one_adjudication(
    data: _AdjudicationData,
) -> None:
    assertion_ids = {assertion.assertion_id for assertion in data.assertions.records}
    adjudicated_ids = [
        decision.assertion_id for decision in data.adjudications.records
    ]
    assert len(assertion_ids) == 43
    assert len(adjudicated_ids) == 43
    assert set(adjudicated_ids) == assertion_ids
    assert len(adjudicated_ids) == len(set(adjudicated_ids))


def test_adjudications_reference_the_correct_two_frozen_reviews(
    data: _AdjudicationData,
) -> None:
    reviewer_a = _reviews_by_assertion(data.reviewer_a_reviews.records)
    reviewer_b = _reviews_by_assertion(data.reviewer_b_reviews.records)
    for decision in data.adjudications.records:
        assert decision.reviewer_a_review_id == reviewer_a[
            decision.assertion_id
        ].review_id
        assert decision.reviewer_b_review_id == reviewer_b[
            decision.assertion_id
        ].review_id
        assert decision.reviewer_a_review_id != decision.reviewer_b_review_id


def test_adjudicator_and_adjudication_ids_are_unique_and_independent(
    data: _AdjudicationData,
) -> None:
    adjudication_ids = [
        decision.adjudication_id for decision in data.adjudications.records
    ]
    reviewer_ids = {
        assignment.reviewer_id
        for assignment in (
            *data.reviewer_a_assignments.records,
            *data.reviewer_b_assignments.records,
        )
    }
    assert len(adjudication_ids) == len(set(adjudication_ids)) == 43
    assert all(
        value.startswith(f"adjudication-{ADJUDICATOR_ID}-")
        for value in adjudication_ids
    )
    assert ADJUDICATOR_ID not in reviewer_ids


def test_agreement_state_and_decision_literals_are_exact(
    data: _AdjudicationData,
) -> None:
    reviewer_a = _reviews_by_assertion(data.reviewer_a_reviews.records)
    reviewer_b = _reviews_by_assertion(data.reviewer_b_reviews.records)
    for decision in data.adjudications.records:
        reviews_agree = _review_signature(reviewer_a[decision.assertion_id]) == (
            _review_signature(reviewer_b[decision.assertion_id])
        )
        assert decision.agreement_state == (
            "agreement" if reviews_agree else "disagreement"
        )
        assert decision.decision in ALLOWED_DECISIONS


def test_agreement_decisions_match_both_reviews_exactly(
    data: _AdjudicationData,
) -> None:
    reviewer_a = _reviews_by_assertion(data.reviewer_a_reviews.records)
    reviewer_b = _reviews_by_assertion(data.reviewer_b_reviews.records)
    for decision in data.adjudications.records:
        if decision.decision != "agreement":
            continue
        review_a = reviewer_a[decision.assertion_id]
        review_b = reviewer_b[decision.assertion_id]
        assert _review_signature(review_a) == _review_signature(review_b)
        assert decision.final_statuses == review_a.expected_statuses
        assert decision.final_acceptable_values == review_a.acceptable_values
        assert decision.retained_alternatives == ()


def test_clerical_corrections_have_explicit_evidence_basis(
    data: _AdjudicationData,
) -> None:
    citations = {
        citation.assertion_id: citation for citation in data.citations.records
    }
    for decision in data.adjudications.records:
        if decision.decision != "clerical_correction":
            continue
        citation = citations[decision.assertion_id]
        assert decision.final_statuses
        assert decision.evidence_ids
        assert set(decision.evidence_ids) <= set(citation.evidence_ids)
        rationale = decision.rationale.casefold()
        assert any(token in rationale for token in ("evidence", "citation", "证据", "引文"))


def test_different_values_and_school_views_are_never_silently_collapsed(
    data: _AdjudicationData,
) -> None:
    assertions = {
        assertion.assertion_id: assertion for assertion in data.assertions.records
    }
    reviewer_a = _reviews_by_assertion(data.reviewer_a_reviews.records)
    reviewer_b = _reviews_by_assertion(data.reviewer_b_reviews.records)
    for decision in data.adjudications.records:
        assertion = assertions[decision.assertion_id]
        review_a = reviewer_a[decision.assertion_id]
        review_b = reviewer_b[decision.assertion_id]
        value_union = set(review_a.acceptable_values) | set(
            review_b.acceptable_values
        )
        values_differ = review_a.acceptable_values != review_b.acceptable_values
        school_view = assertion.assertion_kind == "disagreement"
        # Exact safety expectations override reviewer-proposed computed values.
        # Those corrections remain evidence-bounded and are checked separately.
        if assertion.rule_family == "high_risk_signal":
            continue
        if not (values_differ or school_view):
            continue
        assert decision.decision in {
            "retained_alternative",
            "unresolved_disagreement",
        }
        if value_union:
            assert value_union <= set(decision.retained_alternatives)
            assert value_union <= set(decision.final_acceptable_values)
        elif decision.decision == "retained_alternative":
            pytest.fail("retained alternative requires an explicit retained value")


def test_safety_critical_expectations_are_exact_and_non_ambiguous(
    data: _AdjudicationData,
) -> None:
    assertions = {
        assertion.assertion_id: assertion for assertion in data.assertions.records
    }
    safety_decisions = []
    for decision in data.adjudications.records:
        expected_safety = (
            assertions[decision.assertion_id].rule_family == "high_risk_signal"
        )
        assert decision.safety_critical is expected_safety
        if not expected_safety:
            continue
        safety_decisions.append(decision)
        assert decision.final_statuses == ("not_computed",)
        assert decision.final_acceptable_values == ()
        assert decision.decision != "unresolved_disagreement"
    assert len(safety_decisions) == 4


def test_rationale_and_evidence_are_bounded_and_contain_no_runtime_results(
    data: _AdjudicationData,
) -> None:
    citations = {
        citation.assertion_id: citation for citation in data.citations.records
    }
    forbidden = (
        "engine output",
        "calculation result",
        "calibration run",
        "metric",
        "release threshold",
        "release result",
        "tests/",
        "src/",
        str(REPO_ROOT).casefold(),
    )
    for decision in data.adjudications.records:
        citation = citations[decision.assertion_id]
        assert decision.rationale.strip() == decision.rationale
        assert len(decision.rationale) >= 20
        assert decision.evidence_ids
        assert set(decision.evidence_ids) <= set(citation.evidence_ids)
        rationale = decision.rationale.casefold()
        assert all(fragment.casefold() not in rationale for fragment in forbidden)


def test_adjudication_envelope_is_private_canonical_sorted_and_hashed(
    data: _AdjudicationData,
) -> None:
    envelope = data.adjudications
    assert envelope.contains_real_personal_data is False
    assert envelope.generated_from == tuple(sorted(envelope.generated_from))
    assert envelope.generated_from == tuple(
        sorted(
            (
                data.assertions.payload_sha256,
                data.citations.payload_sha256,
                data.reviewer_a_reviews.payload_sha256,
                data.reviewer_b_reviews.payload_sha256,
            )
        )
    )
    assert envelope.payload_sha256 == records_payload_sha256(envelope.records)
    adjudication_ids = tuple(
        decision.adjudication_id for decision in envelope.records
    )
    assert adjudication_ids == tuple(sorted(adjudication_ids))
    payload = data.root.joinpath(ADJUDICATION_FILENAME).read_bytes()
    assert payload == canonical_json_bytes(json.loads(payload.decode("utf-8")))
    assert payload[-1:] == b"}"


def test_complete_reference_graph_accepts_both_reviews_and_adjudication(
    data: _AdjudicationData,
) -> None:
    validate_calibration_references(
        fixtures=data.fixtures.records,
        cases=data.cases.records,
        assertions=data.assertions.records,
        citations=data.citations.records,
        packets=data.packets.records,
        assignments=(
            *data.reviewer_a_assignments.records,
            *data.reviewer_b_assignments.records,
        ),
        reviews=(
            *data.reviewer_a_reviews.records,
            *data.reviewer_b_reviews.records,
        ),
        adjudications=data.adjudications.records,
    )


def test_adjudication_loader_is_read_only() -> None:
    path = _resource_root().joinpath(ADJUDICATION_FILENAME)
    before = sha256(path.read_bytes()).hexdigest()
    load_calibration_file(path, AdjudicationDecision)
    after = sha256(path.read_bytes()).hexdigest()
    assert after == before


def test_adjudication_records_have_only_protocol_fields(
    data: _AdjudicationData,
) -> None:
    assert set(asdict(data.adjudications.records[0])) == {
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
    }
