from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any, Protocol, TypeVar, cast

from mingli_engine.bazi.schools.base import load_school_profiles_config
from mingli_engine.classical_sources import load_approved_evidence_units
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


T = TypeVar("T")

_ENVELOPE_FIELDS = frozenset(
    {
        "schema_version",
        "suite_version",
        "generated_from",
        "contains_real_personal_data",
        "payload_sha256",
        "records",
    }
)
_PRIMARY_ID_FIELDS: dict[type[object], str] = {
    CalibrationInputFixture: "fixture_id",
    CalibrationCase: "case_id",
    CalibrationAssertion: "assertion_id",
    CalibrationCitation: "citation_id",
    ReviewerPacket: "packet_id",
    ReviewAssignment: "assignment_id",
    CalibrationReview: "review_id",
    AdjudicationDecision: "adjudication_id",
    CalibrationRun: "run_id",
    MetricSnapshotV1: "snapshot_id",
}


class _ReadableBytes(Protocol):
    def read_bytes(self) -> bytes: ...


class CalibrationProtocolError(ValueError):
    pass


class _DuplicateKeyError(ValueError):
    pass


def get_authoritative_rule_family_ids() -> tuple[str, ...]:
    """Return the formal interpretation API's current rule-family IDs."""
    rule_families = get_formal_interpretation_rule_families()
    if not rule_families or len(set(rule_families)) != len(rule_families):
        raise CalibrationProtocolError("authoritative rule families are invalid")
    return rule_families


def load_authoritative_school_profile_identity() -> tuple[str, tuple[str, ...]]:
    """Return the version and enabled IDs from school_profiles.json."""
    try:
        config = load_school_profiles_config()
    except Exception:
        raise CalibrationProtocolError(
            "authoritative school profiles are unavailable"
        ) from None
    if not config.enabled or len(set(config.enabled)) != len(config.enabled):
        raise CalibrationProtocolError("authoritative enabled schools are invalid")
    return config.version, config.enabled


def _json_value(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _json_value(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("JSON object keys must be strings")
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        return [_json_value(item) for item in value]
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite number")
        return value
    raise TypeError("value is not JSON-compatible")


def canonical_json_bytes(value: object) -> bytes:
    """Return the protocol's canonical UTF-8 JSON representation."""
    try:
        return json.dumps(
            _json_value(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        raise CalibrationProtocolError("value is not canonical JSON") from None


def records_payload_sha256(records: object) -> str:
    """Hash only the canonical records value, excluding envelope metadata."""
    return sha256(canonical_json_bytes(records)).hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError
        result[key] = value
    return result


def _reject_nonfinite(_value: str) -> object:
    raise ValueError("non-finite number")


def _strict_json(payload: bytes) -> object:
    try:
        decoded = payload.decode("utf-8", errors="strict")
        value = json.loads(
            decoded,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeError, ValueError, RecursionError):
        raise CalibrationProtocolError("calibration file is not strict JSON") from None
    if canonical_json_bytes(value) != payload:
        raise CalibrationProtocolError("calibration file is not canonical JSON")
    return value


def _exact_mapping(
    value: object,
    expected_fields: frozenset[str],
    context: str,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != expected_fields:
        raise CalibrationProtocolError(f"{context} fields are not exact")
    return value


def _nested_record(
    value: object,
    record_type: type[T],
    context: str,
) -> T:
    mapping = _exact_mapping(
        value,
        frozenset(field.name for field in fields(cast(Any, record_type))),
        context,
    )
    kwargs = dict(mapping)
    if record_type is ReviewerPacket:
        kwargs["assertion"] = _nested_record(
            kwargs["assertion"],
            BlindedAssertionProjection,
            "blinded assertion projection",
        )
    elif record_type is CalibrationRun:
        kwargs["version_set"] = _nested_record(
            kwargs["version_set"],
            ExactVersionSet,
            "run version_set",
        )
        results = kwargs["assertion_results"]
        if not isinstance(results, list):
            raise CalibrationProtocolError("assertion_results must be a list")
        kwargs["assertion_results"] = tuple(
            _nested_record(
                item,
                CalibrationAssertionResult,
                "assertion result",
            )
            for item in results
        )
    elif record_type is MetricSnapshotV1:
        kwargs["version_set"] = _nested_record(
            kwargs["version_set"],
            ExactVersionSet,
            "metric version_set",
        )
    elif record_type is CalibrationReleaseDecision:
        kwargs["metrics"] = _nested_record(
            kwargs["metrics"],
            MetricSnapshotV1,
            "release metrics",
        )
        kwargs["version_set"] = _nested_record(
            kwargs["version_set"],
            ExactVersionSet,
            "release version_set",
        )
    try:
        constructor = cast(Any, record_type)
        return cast(T, constructor(**kwargs))
    except (TypeError, ValueError):
        raise CalibrationProtocolError("calibration record is malformed") from None


def load_calibration_file(
    path: str | Path | _ReadableBytes,
    record_type: type[T],
) -> CalibrationFileEnvelopeV1[T]:
    """Strictly load one canonical calibration file without modifying it."""
    source: _ReadableBytes
    source = Path(path) if isinstance(path, (str, Path)) else path
    try:
        payload = source.read_bytes()
    except (OSError, UnicodeError):
        raise CalibrationProtocolError("calibration file is unavailable") from None

    root = _exact_mapping(_strict_json(payload), _ENVELOPE_FIELDS, "envelope")
    raw_records = root["records"]
    if not isinstance(raw_records, list):
        raise CalibrationProtocolError("records must be a list")
    if root["payload_sha256"] != records_payload_sha256(raw_records):
        raise CalibrationProtocolError("records payload hash mismatch")

    is_release = record_type is CalibrationReleaseDecision
    expected_schema = (
        "domain-calibration-release-v1"
        if is_release
        else "domain-calibration-file-v1"
    )
    if root["schema_version"] != expected_schema:
        raise CalibrationProtocolError("calibration file schema is not supported")
    if is_release and len(raw_records) != 1:
        raise CalibrationProtocolError("release envelope requires one record")
    if not is_release and record_type not in _PRIMARY_ID_FIELDS:
        raise CalibrationProtocolError("record type is not a standalone protocol record")

    records = tuple(
        _nested_record(item, record_type, record_type.__name__)
        for item in raw_records
    )
    if not is_release:
        primary_field = _PRIMARY_ID_FIELDS[cast(type[object], record_type)]
        primary_ids = tuple(getattr(record, primary_field) for record in records)
        if len(set(primary_ids)) != len(primary_ids):
            raise CalibrationProtocolError("duplicate primary ID")
        if primary_ids != tuple(sorted(primary_ids)):
            raise CalibrationProtocolError("records are not in canonical primary-ID order")

    try:
        return CalibrationFileEnvelopeV1(
            schema_version=cast(str, root["schema_version"]),
            suite_version=cast(str, root["suite_version"]),
            generated_from=cast(tuple[str, ...], root["generated_from"]),
            contains_real_personal_data=cast(
                bool,
                root["contains_real_personal_data"],
            ),
            payload_sha256=cast(str, root["payload_sha256"]),
            records=records,
        )
    except (TypeError, ValueError):
        raise CalibrationProtocolError("calibration envelope is malformed") from None


def _index(
    records: tuple[T, ...],
    expected_type: type[T],
    primary_field: str,
) -> dict[str, T]:
    result: dict[str, T] = {}
    for record in records:
        if not isinstance(record, expected_type):
            raise CalibrationProtocolError("reference collection has invalid records")
        primary_id = getattr(record, primary_field)
        if primary_id in result:
            raise CalibrationProtocolError("duplicate primary ID in reference graph")
        result[primary_id] = record
    return result


def _require_reference(
    reference_id: str,
    index: Mapping[str, object],
    context: str,
) -> None:
    if reference_id not in index:
        raise CalibrationProtocolError(f"unresolved {context} reference")


def _packet_sha256(packet: ReviewerPacket) -> str:
    return sha256(canonical_json_bytes(packet)).hexdigest()


def validate_calibration_references(
    *,
    fixtures: tuple[CalibrationInputFixture, ...] = (),
    cases: tuple[CalibrationCase, ...] = (),
    assertions: tuple[CalibrationAssertion, ...] = (),
    citations: tuple[CalibrationCitation, ...] = (),
    packets: tuple[ReviewerPacket, ...] = (),
    assignments: tuple[ReviewAssignment, ...] = (),
    reviews: tuple[CalibrationReview, ...] = (),
    adjudications: tuple[AdjudicationDecision, ...] = (),
    runs: tuple[CalibrationRun, ...] = (),
) -> None:
    """Validate cross-file IDs, independence, packet hashes, and evidence IDs."""
    fixture_by_id = _index(fixtures, CalibrationInputFixture, "fixture_id")
    case_by_id = _index(cases, CalibrationCase, "case_id")
    assertion_by_id = _index(assertions, CalibrationAssertion, "assertion_id")
    citation_by_id = _index(citations, CalibrationCitation, "citation_id")
    packet_by_id = _index(packets, ReviewerPacket, "packet_id")
    assignment_by_id = _index(assignments, ReviewAssignment, "assignment_id")
    review_by_id = _index(reviews, CalibrationReview, "review_id")
    _index(adjudications, AdjudicationDecision, "adjudication_id")
    _index(runs, CalibrationRun, "run_id")

    for case in cases:
        _require_reference(case.input_fixture_id, fixture_by_id, "fixture")
    for assertion in assertions:
        _require_reference(assertion.case_id, case_by_id, "case")
    for citation in citations:
        _require_reference(citation.assertion_id, assertion_by_id, "assertion")

    for packet in packets:
        source_assertion = assertion_by_id.get(packet.assertion.assertion_id)
        if source_assertion is None:
            raise CalibrationProtocolError("unresolved packet assertion reference")
        if (
            packet.assertion.rule_family != source_assertion.rule_family
            or packet.assertion.school_id != source_assertion.school_id
            or packet.assertion.assertion_kind != source_assertion.assertion_kind
            or packet.assertion.field_path != source_assertion.field_path
        ):
            raise CalibrationProtocolError("packet assertion reference is inconsistent")
        for citation_id in packet.citation_ids:
            source_citation = citation_by_id.get(citation_id)
            if (
                source_citation is None
                or source_citation.assertion_id != source_assertion.assertion_id
            ):
                raise CalibrationProtocolError("unresolved packet citation reference")

    reviewers_by_packet: dict[str, set[str]] = {}
    for assignment in assignments:
        source_packet = packet_by_id.get(assignment.packet_id)
        if source_packet is None:
            raise CalibrationProtocolError("unresolved assignment packet reference")
        if assignment.packet_sha256 != _packet_sha256(source_packet):
            raise CalibrationProtocolError("assignment packet hash reference mismatch")
        packet_reviewers = reviewers_by_packet.setdefault(assignment.packet_id, set())
        if assignment.reviewer_id in packet_reviewers:
            raise CalibrationProtocolError("reviewer identities must be distinct")
        packet_reviewers.add(assignment.reviewer_id)

    for review in reviews:
        source_assignment = assignment_by_id.get(review.assignment_id)
        if source_assignment is None:
            raise CalibrationProtocolError("unresolved review assignment reference")
        source_packet = packet_by_id[source_assignment.packet_id]
        if review.assertion_id != source_packet.assertion.assertion_id:
            raise CalibrationProtocolError("review assertion reference mismatch")
        if review.packet_sha256 != source_assignment.packet_sha256:
            raise CalibrationProtocolError("review packet hash reference mismatch")

    for decision in adjudications:
        _require_reference(decision.assertion_id, assertion_by_id, "assertion")
        review_a = review_by_id.get(decision.reviewer_a_review_id)
        review_b = review_by_id.get(decision.reviewer_b_review_id)
        if review_a is None or review_b is None:
            raise CalibrationProtocolError("unresolved adjudication review reference")
        if (
            review_a.assertion_id != decision.assertion_id
            or review_b.assertion_id != decision.assertion_id
            or review_a.assignment_id == review_b.assignment_id
        ):
            raise CalibrationProtocolError("adjudication review reference mismatch")

    for run in runs:
        seen_assertion_ids: set[str] = set()
        for result in run.assertion_results:
            _require_reference(result.assertion_id, assertion_by_id, "assertion")
            if result.assertion_id in seen_assertion_ids:
                raise CalibrationProtocolError("duplicate run assertion reference")
            seen_assertion_ids.add(result.assertion_id)

    referenced_evidence_ids = {
        evidence_id
        for assertion in assertions
        for evidence_id in assertion.required_evidence_ids
    }
    referenced_evidence_ids.update(
        evidence_id for citation in citations for evidence_id in citation.evidence_ids
    )
    referenced_evidence_ids.update(
        evidence_id
        for packet in packets
        for evidence_id in packet.assertion.candidate_evidence_ids
    )
    referenced_evidence_ids.update(
        evidence_id for review in reviews for evidence_id in review.evidence_ids
    )
    referenced_evidence_ids.update(
        evidence_id
        for decision in adjudications
        for evidence_id in decision.evidence_ids
    )
    if referenced_evidence_ids:
        try:
            authoritative_evidence_ids = {
                unit.evidence_id for unit in load_approved_evidence_units()
            }
        except Exception:
            raise CalibrationProtocolError(
                "authoritative evidence references are unavailable"
            ) from None
        if not referenced_evidence_ids <= authoritative_evidence_ids:
            raise CalibrationProtocolError("unresolved formal evidence reference")


def validate_version_set_equality(
    run: CalibrationRun,
    snapshot: MetricSnapshotV1,
    release: CalibrationReleaseDecision,
) -> None:
    """Require exact run, baseline snapshot, and release version identity."""
    if not isinstance(run, CalibrationRun):
        raise TypeError("run must be CalibrationRun")
    if not isinstance(snapshot, MetricSnapshotV1):
        raise TypeError("snapshot must be MetricSnapshotV1")
    if not isinstance(release, CalibrationReleaseDecision):
        raise TypeError("release must be CalibrationReleaseDecision")
    if not (
        run.version_set == snapshot.version_set == release.version_set
    ):
        raise CalibrationProtocolError(
            "run, snapshot, and release version_set values must match"
        )
