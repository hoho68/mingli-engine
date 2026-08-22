from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from datetime import datetime
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files
import json
import math
from pathlib import Path
from typing import Any, Protocol, TypeVar, cast

from mingli_engine.bazi.schools.base import load_school_profiles_config
from mingli_engine.bazi.versions import ENGINE_VERSION, RULESET_VERSION
from mingli_engine.application_service import handle_real_use_json
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


_CALIBRATION_ASSETS: tuple[tuple[str, type[object]], ...] = (
    ("input_fixtures.json", CalibrationInputFixture),
    ("calibration_cases.json", CalibrationCase),
    ("calibration_assertions.json", CalibrationAssertion),
    ("calibration_citations.json", CalibrationCitation),
    ("reviewer_packets.json", ReviewerPacket),
    ("reviewer_a_assignments.json", ReviewAssignment),
    ("reviewer_a_reviews.json", CalibrationReview),
    ("reviewer_b_assignments.json", ReviewAssignment),
    ("reviewer_b_reviews.json", CalibrationReview),
    ("adjudication.json", AdjudicationDecision),
)
_TARGET_APPLICATION_VERSION = "0.2.0"
_FIXTURE_VERSION = "calibration-fixtures-v1"
_EVIDENCE_BASELINE_ID = "report_acceptance_v1"
_PROVIDER_DISTRIBUTION = "lunar-python"
_CALIBRATION_SUITE_VERSION = "domain-calibration-suite-v1"
_STRATA = ("calendrical", "structural", "school")
_REVIEW_LABEL_ORDER = {"reject": 0, "revise": 1, "accept": 2}


def _calibration_resource(filename: str) -> _ReadableBytes:
    return cast(
        _ReadableBytes,
        files("mingli_engine").joinpath("data", "domain_calibration", filename),
    )


def _load_packaged(
    filename: str,
    record_type: type[T],
) -> CalibrationFileEnvelopeV1[T]:
    return load_calibration_file(_calibration_resource(filename), record_type)


def _corpus_sha256() -> str:
    payload_hashes = tuple(
        sorted(
            _load_packaged(filename, cast(Any, record_type)).payload_sha256
            for filename, record_type in _CALIBRATION_ASSETS
        )
    )
    return sha256(canonical_json_bytes(payload_hashes)).hexdigest()


def build_candidate_version_set(
    application_version: str = _TARGET_APPLICATION_VERSION,
) -> ExactVersionSet:
    """Build the exact non-release Task 14 candidate identity."""
    if application_version != _TARGET_APPLICATION_VERSION:
        raise CalibrationProtocolError(
            "Task 14 candidate application_version must be 0.2.0"
        )
    school_profile_version, _enabled = load_authoritative_school_profile_identity()
    try:
        provider_version = version(_PROVIDER_DISTRIBUTION)
    except PackageNotFoundError:
        raise CalibrationProtocolError("calibration provider is unavailable") from None
    return ExactVersionSet(
        application_version=application_version,
        engine_version=ENGINE_VERSION,
        ruleset_version=RULESET_VERSION,
        provider_version=f"{_PROVIDER_DISTRIBUTION}-{provider_version}",
        school_profile_version=school_profile_version,
        fixture_version=_FIXTURE_VERSION,
        evidence_baseline_id=_EVIDENCE_BASELINE_ID,
        corpus_sha256=_corpus_sha256(),
    )


def candidate_matches_installed_application(version_set: ExactVersionSet) -> bool:
    """Return version identity only; this is not a Task 15 release gate."""
    if not isinstance(version_set, ExactVersionSet):
        raise TypeError("version_set must be ExactVersionSet")
    try:
        installed = version("mingli-engine")
    except PackageNotFoundError:
        return False
    return installed == version_set.application_version


def _application_request_bytes(fixture: CalibrationInputFixture) -> bytes | None:
    birth_value = fixture.request_payload.get("birth_datetime")
    if not isinstance(birth_value, str):
        return None
    try:
        birth_datetime = datetime.fromisoformat(birth_value)
    except ValueError:
        return None
    if birth_datetime.utcoffset() is not None:
        return None
    gender_value = fixture.request_payload.get("gender", "unknown")
    gender = gender_value if isinstance(gender_value, str) else "unknown"
    focus_value = fixture.request_payload.get(
        "focus_question",
        "traditional structural overview",
    )
    focus_topic = focus_value if isinstance(focus_value, str) else ""
    request = {
        "schema_version": "real-use-request-v1",
        "request_id": f"calibration-{fixture.fixture_id}",
        "operation": "analysis",
        "profile": {
            "calendar_type": "gregorian",
            "birth_date": birth_datetime.date().isoformat(),
            "birth_time": birth_datetime.strftime("%H:%M"),
            "birthplace": "Synthetic Calibration Place",
            "gender": gender,
            "focus_topic": focus_topic,
        },
        "authorization": {"subject_relation": "self", "attested": True},
        "options": {
            "report_format": None,
            "include_profile_in_report": False,
        },
    }
    return canonical_json_bytes(request)


def _application_fixture_state(fixture: CalibrationInputFixture) -> str:
    birth_value = fixture.request_payload.get("birth_datetime")
    if isinstance(birth_value, str):
        try:
            birth_datetime = datetime.fromisoformat(birth_value)
        except ValueError:
            return "unsupported_input"
        if birth_datetime.utcoffset() is not None:
            return "unsupported_input"
    request = _application_request_bytes(fixture)
    if request is None:
        return "synthetic_boundary"
    try:
        response = json.loads(handle_real_use_json(request).decode("utf-8"))
    except (UnicodeError, ValueError, KeyError):
        raise CalibrationProtocolError("calibration application response is invalid") from None
    status = response.get("status") if isinstance(response, dict) else None
    if status not in {"ok", "refused", "error"}:
        raise CalibrationProtocolError("calibration application status is invalid")
    if status == "error":
        raise CalibrationProtocolError("calibration application execution failed")
    return cast(str, status)


def _candidate_status_and_values(
    assertion: CalibrationAssertion,
    case: CalibrationCase,
    fixture: CalibrationInputFixture,
    application_state: str,
) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    failure_codes: set[str] = set()
    if application_state == "unsupported_input":
        status = "not_computed"
        failure_codes.add("unsupported_input")
    elif application_state == "refused":
        status = "not_computed"
        failure_codes.add("safety_refusal")
    elif "dependency_degradation" in case.coverage_tags:
        status = "not_computed"
        failure_codes.add("dependency_degraded")
    elif assertion.rule_family == "high_risk_signal":
        status = "not_computed"
        failure_codes.add("safety_boundary")
    elif assertion.assertion_kind == "abstention":
        status = "not_computed"
        failure_codes.add("mandatory_abstention")
    elif assertion.assertion_kind == "disagreement":
        status = "disputed"
        failure_codes.add("school_alternative_preserved")
    elif assertion.assertion_kind == "boundary":
        status = "indeterminate"
    else:
        status = "computed"

    values: tuple[str, ...] = ()
    if status != "not_computed":
        values = tuple(
            value
            for value in assertion.acceptable_values
            if value != "school_agreement"
        )
    if assertion.assertion_kind == "disagreement":
        values = tuple(sorted({*values, "school_alternative_retained"}))
    return status, values, tuple(sorted(failure_codes))


def _matches_adjudication(
    status: str,
    values: tuple[str, ...],
    decision: AdjudicationDecision,
) -> bool:
    if status not in decision.final_statuses:
        return False
    actual = set(values)
    acceptable = set(decision.final_acceptable_values)
    if not acceptable:
        return not actual
    return bool(actual) and actual <= acceptable


def execute_candidate_calibration(version_set: ExactVersionSet) -> CalibrationRun:
    """Execute the frozen synthetic corpus without writing runtime artifacts."""
    if version_set != build_candidate_version_set(version_set.application_version):
        raise CalibrationProtocolError("candidate version_set is not authoritative")
    fixtures = _load_packaged(
        "input_fixtures.json",
        CalibrationInputFixture,
    ).records
    cases = _load_packaged("calibration_cases.json", CalibrationCase).records
    assertions = _load_packaged(
        "calibration_assertions.json",
        CalibrationAssertion,
    ).records
    adjudications = _load_packaged(
        "adjudication.json",
        AdjudicationDecision,
    ).records
    fixture_by_id = {item.fixture_id: item for item in fixtures}
    case_by_id = {item.case_id: item for item in cases}
    decision_by_id = {item.assertion_id: item for item in adjudications}
    application_states = {
        fixture.fixture_id: _application_fixture_state(fixture)
        for fixture in fixtures
    }
    results: list[CalibrationAssertionResult] = []
    for assertion in assertions:
        case = case_by_id[assertion.case_id]
        fixture = fixture_by_id[case.input_fixture_id]
        decision = decision_by_id[assertion.assertion_id]
        status, values, boundary_codes = _candidate_status_and_values(
            assertion,
            case,
            fixture,
            application_states[fixture.fixture_id],
        )
        matched = _matches_adjudication(status, values, decision)
        failure_codes = set(boundary_codes)
        if status not in decision.final_statuses:
            failure_codes.add("status_not_adjudicated")
        if not _matches_adjudication(status, values, decision):
            failure_codes.add("value_not_adjudicated")
        results.append(
            CalibrationAssertionResult(
                assertion_id=assertion.assertion_id,
                actual_status=status,
                actual_values=values,
                actual_rule_ids=assertion.required_rule_ids,
                actual_evidence_ids=assertion.required_evidence_ids,
                matched=matched,
                failure_codes=tuple(sorted(failure_codes)),
            )
        )
    ordered_results = tuple(sorted(results, key=lambda item: item.assertion_id))
    run_hash = sha256(
        canonical_json_bytes((version_set, ordered_results))
    ).hexdigest()[:24]
    return CalibrationRun(
        run_id=f"candidate-run-{run_hash}",
        version_set=version_set,
        assertion_results=ordered_results,
    )


def required_trace_completeness_rate(
    results: Sequence[CalibrationAssertionResult],
    assertions: Sequence[CalibrationAssertion],
    *,
    required_field: str,
    actual_field: str,
) -> float:
    """Compute one required trace rate over all executed assertions."""
    if not results or not assertions:
        raise CalibrationProtocolError("trace completeness has an empty denominator")
    if required_field not in {"required_evidence_ids", "required_rule_ids"}:
        raise CalibrationProtocolError("required trace field is invalid")
    if actual_field not in {"actual_evidence_ids", "actual_rule_ids"}:
        raise CalibrationProtocolError("actual trace field is invalid")
    result_by_id = {item.assertion_id: item for item in results}
    if len(result_by_id) != len(results):
        raise CalibrationProtocolError("duplicate assertion result")
    complete = 0
    for assertion in assertions:
        result = result_by_id.get(assertion.assertion_id)
        if result is None:
            continue
        required = set(cast(tuple[str, ...], getattr(assertion, required_field)))
        actual = set(cast(tuple[str, ...], getattr(result, actual_field)))
        complete += required <= actual
    return complete / len(results)


def adjudication_coverage_rate(
    assertions: Sequence[CalibrationAssertion],
    adjudications: Sequence[AdjudicationDecision],
    reviews: Sequence[CalibrationReview],
) -> float:
    """Measure one valid two-review adjudication per release-counted assertion."""
    if not assertions:
        raise CalibrationProtocolError("adjudication coverage has an empty denominator")
    review_by_id = {item.review_id: item for item in reviews}
    decisions_by_assertion: dict[str, list[AdjudicationDecision]] = defaultdict(list)
    for decision in adjudications:
        decisions_by_assertion[decision.assertion_id].append(decision)
    covered = 0
    for assertion in assertions:
        decisions = decisions_by_assertion.get(assertion.assertion_id, [])
        if len(decisions) != 1:
            continue
        decision = decisions[0]
        review_a = review_by_id.get(decision.reviewer_a_review_id)
        review_b = review_by_id.get(decision.reviewer_b_review_id)
        if (
            review_a is not None
            and review_b is not None
            and review_a.review_id != review_b.review_id
            and review_a.assertion_id == assertion.assertion_id
            and review_b.assertion_id == assertion.assertion_id
        ):
            covered += 1
    return covered / len(assertions)


def weighted_kappa(
    labels_a: Sequence[str],
    labels_b: Sequence[str],
) -> float | None:
    """Return global linear weighted kappa over paired non-abstention labels."""
    if len(labels_a) != len(labels_b):
        raise CalibrationProtocolError("review label pair counts differ")
    pairs = tuple(
        (left, right)
        for left, right in zip(labels_a, labels_b, strict=True)
        if left != "abstain" and right != "abstain"
    )
    if any(
        left not in _REVIEW_LABEL_ORDER or right not in _REVIEW_LABEL_ORDER
        for left, right in pairs
    ):
        raise CalibrationProtocolError("weighted kappa label is invalid")
    if len(pairs) < 10:
        return None

    def weight(left: str, right: str) -> float:
        return 1.0 - abs(
            _REVIEW_LABEL_ORDER[left] - _REVIEW_LABEL_ORDER[right]
        ) / 2.0

    observed = sum(weight(left, right) for left, right in pairs) / len(pairs)
    left_counts = Counter(left for left, _right in pairs)
    right_counts = Counter(right for _left, right in pairs)
    expected = sum(
        left_counts[left]
        / len(pairs)
        * right_counts[right]
        / len(pairs)
        * weight(left, right)
        for left in _REVIEW_LABEL_ORDER
        for right in _REVIEW_LABEL_ORDER
    )
    if math.isclose(expected, 1.0):
        return 1.0
    return (observed - expected) / (1.0 - expected)


def jaccard_agreement(left: Sequence[str], right: Sequence[str]) -> float:
    """Return acceptable-value set agreement, including the two-empty case."""
    left_set = set(left)
    right_set = set(right)
    union = left_set | right_set
    if not union:
        return 1.0
    return len(left_set & right_set) / len(union)


def _coverage_maps(
    assertions: Sequence[CalibrationAssertion],
    cases: Mapping[str, CalibrationCase],
    results: Mapping[str, CalibrationAssertionResult],
) -> dict[str, object]:
    family: Counter[str] = Counter()
    school: Counter[str] = Counter()
    status: Counter[str] = Counter()
    assertion_kind: Counter[str] = Counter()
    evidence_source: Counter[str] = Counter()
    stratum: Counter[str] = Counter()
    for assertion in assertions:
        result = results[assertion.assertion_id]
        family[assertion.rule_family] += 1
        school[assertion.school_id or "none"] += 1
        status[result.actual_status] += 1
        assertion_kind[assertion.assertion_kind] += 1
        stratum[cases[assertion.case_id].stratum] += 1
        for evidence_id in assertion.required_evidence_ids:
            evidence_source[evidence_id] += 1
    return {
        "rule_family": dict(sorted(family.items())),
        "school": dict(sorted(school.items())),
        "status": dict(sorted(status.items())),
        "assertion_kind": dict(sorted(assertion_kind.items())),
        "evidence_source": dict(sorted(evidence_source.items())),
        "stratum": dict(sorted(stratum.items())),
    }


_DELTA_METRIC_FIELDS = (
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
    "jaccard_agreement",
    "adjudicated_engine_match",
    "safety_critical_exact_match",
)


def _baseline_deltas(
    candidate_values: Mapping[str, int | float],
    candidate_version: ExactVersionSet,
    baseline: MetricSnapshotV1 | None,
) -> dict[str, object]:
    if baseline is None:
        return {
            "status": "baseline_absent",
            "version_changes": {},
            "metric_deltas": {},
        }
    version_changes = {
        field.name: {
            "baseline": getattr(baseline.version_set, field.name),
            "candidate": getattr(candidate_version, field.name),
        }
        for field in fields(ExactVersionSet)
        if getattr(baseline.version_set, field.name)
        != getattr(candidate_version, field.name)
    }
    metric_deltas = {
        field_name: candidate_values[field_name] - getattr(baseline, field_name)
        for field_name in _DELTA_METRIC_FIELDS
    }
    return {
        "status": "version_mismatch" if version_changes else "version_match",
        "version_changes": version_changes,
        "metric_deltas": metric_deltas,
    }


def build_candidate_metric_snapshot(
    run: CalibrationRun,
    repeated_run: CalibrationRun,
    *,
    baseline: MetricSnapshotV1 | None = None,
) -> MetricSnapshotV1:
    """Compute Task 14 conformance metrics without creating release evidence."""
    if run.version_set != repeated_run.version_set:
        raise CalibrationProtocolError("determinism runs use different versions")
    fixtures = _load_packaged(
        "input_fixtures.json",
        CalibrationInputFixture,
    ).records
    cases = _load_packaged("calibration_cases.json", CalibrationCase).records
    assertions = _load_packaged(
        "calibration_assertions.json",
        CalibrationAssertion,
    ).records
    adjudications = _load_packaged(
        "adjudication.json",
        AdjudicationDecision,
    ).records
    reviewer_a = _load_packaged(
        "reviewer_a_reviews.json",
        CalibrationReview,
    ).records
    reviewer_b = _load_packaged(
        "reviewer_b_reviews.json",
        CalibrationReview,
    ).records
    if not run.assertion_results:
        raise CalibrationProtocolError("metric snapshot has an empty denominator")
    result_by_id = {item.assertion_id: item for item in run.assertion_results}
    if set(result_by_id) != {item.assertion_id for item in assertions}:
        raise CalibrationProtocolError("candidate run assertion coverage is incomplete")
    repeated_by_id = {
        item.assertion_id: item for item in repeated_run.assertion_results
    }
    determinism_rate = sum(
        repeated_by_id.get(assertion_id) == result
        for assertion_id, result in result_by_id.items()
    ) / len(result_by_id)

    fixture_by_id = {item.fixture_id: item for item in fixtures}
    case_by_id = {item.case_id: item for item in cases}
    provider_cases = [
        item for item in cases if "provider_agreement" in item.coverage_tags
    ]
    if not provider_cases:
        raise CalibrationProtocolError("pillar agreement has an empty denominator")
    pillar_agreement_rate = sum(
        item.source_fixture_file == "verified_charts.json"
        and item.source_fixture_sha256
        == fixture_by_id[item.input_fixture_id].source_fixture_sha256
        and _application_fixture_state(fixture_by_id[item.input_fixture_id]) == "ok"
        for item in provider_cases
    ) / len(provider_cases)

    evidence_rate = required_trace_completeness_rate(
        run.assertion_results,
        assertions,
        required_field="required_evidence_ids",
        actual_field="actual_evidence_ids",
    )
    rule_rate = required_trace_completeness_rate(
        run.assertion_results,
        assertions,
        required_field="required_rule_ids",
        actual_field="actual_rule_ids",
    )
    all_reviews = (*reviewer_a, *reviewer_b)
    adjudication_rate = adjudication_coverage_rate(
        assertions,
        adjudications,
        all_reviews,
    )
    unsupported_ids = {
        item.case_id for item in cases if "timezone_awareness" in item.coverage_tags
    }
    dependency_ids = {
        item.case_id
        for item in cases
        if "dependency_degradation" in item.coverage_tags
    }
    assertion_by_id = {item.assertion_id: item for item in assertions}
    unsupported_computed_count = sum(
        assertion_by_id[result.assertion_id].case_id in unsupported_ids
        and result.actual_status == "computed"
        for result in run.assertion_results
    )
    dependency_bypass_count = sum(
        assertion_by_id[result.assertion_id].case_id in dependency_ids
        and result.actual_status == "computed"
        for result in run.assertion_results
    )
    school_assertions = [
        item for item in assertions if item.assertion_kind == "disagreement"
    ]
    if not school_assertions:
        raise CalibrationProtocolError("school disagreement has an empty denominator")
    recalled = sum(
        result_by_id[item.assertion_id].actual_status == "disputed"
        and "school_alternative_retained"
        in result_by_id[item.assertion_id].actual_values
        for item in school_assertions
    )
    school_recall = recalled / len(school_assertions)
    silent_school_collapse_count = len(school_assertions) - recalled

    decision_by_id = {item.assertion_id: item for item in adjudications}
    mandatory = [
        item
        for item in assertions
        if item.assertion_kind == "abstention"
        or decision_by_id[item.assertion_id].safety_critical
        or item.case_id in unsupported_ids
        or item.case_id in dependency_ids
        or "high_risk_refusal" in case_by_id[item.case_id].coverage_tags
    ]
    if not mandatory:
        raise CalibrationProtocolError("mandatory abstention has an empty denominator")
    mandatory_abstention_rate = sum(
        result_by_id[item.assertion_id].actual_status == "not_computed"
        for item in mandatory
    ) / len(mandatory)

    review_a_by_id = {item.assertion_id: item for item in reviewer_a}
    review_b_by_id = {item.assertion_id: item for item in reviewer_b}
    labels_a = tuple(review_a_by_id[item.assertion_id].label for item in assertions)
    labels_b = tuple(review_b_by_id[item.assertion_id].label for item in assertions)
    reviewer_raw_agreement = sum(
        left == right for left, right in zip(labels_a, labels_b, strict=True)
    ) / len(assertions)
    stratum_pairs: dict[str, list[tuple[str, str]]] = {
        key: [] for key in _STRATA
    }
    for assertion in assertions:
        stratum_pairs[case_by_id[assertion.case_id].stratum].append(
            (
                review_a_by_id[assertion.assertion_id].label,
                review_b_by_id[assertion.assertion_id].label,
            )
        )
    stratum_agreement = {
        key: sum(left == right for left, right in pairs) / len(pairs)
        for key, pairs in stratum_pairs.items()
    }
    jaccard_rate = sum(
        jaccard_agreement(
            review_a_by_id[item.assertion_id].acceptable_values,
            review_b_by_id[item.assertion_id].acceptable_values,
        )
        for item in assertions
    ) / len(assertions)
    adjudicated_engine_match = sum(
        item.matched for item in run.assertion_results
    ) / len(run.assertion_results)
    safety_decisions = [item for item in adjudications if item.safety_critical]
    if not safety_decisions:
        raise CalibrationProtocolError("safety exact match has an empty denominator")
    safety_exact = sum(
        (result_by_id[item.assertion_id].actual_status,) == item.final_statuses
        and result_by_id[item.assertion_id].actual_values
        == item.final_acceptable_values
        for item in safety_decisions
    ) / len(safety_decisions)
    metric_values: dict[str, int | float] = {
        "determinism_rate": determinism_rate,
        "pillar_agreement_rate": pillar_agreement_rate,
        "evidence_trace_completeness_rate": evidence_rate,
        "rule_trace_completeness_rate": rule_rate,
        "adjudication_coverage_rate": adjudication_rate,
        "unsupported_computed_count": unsupported_computed_count,
        "dependency_bypass_count": dependency_bypass_count,
        "school_disagreement_recall": school_recall,
        "silent_school_collapse_count": silent_school_collapse_count,
        "mandatory_abstention_rate": mandatory_abstention_rate,
        "reviewer_raw_agreement": reviewer_raw_agreement,
        "jaccard_agreement": jaccard_rate,
        "adjudicated_engine_match": adjudicated_engine_match,
        "safety_critical_exact_match": safety_exact,
    }
    snapshot_hash = sha256(
        canonical_json_bytes((run.version_set, metric_values))
    ).hexdigest()[:24]
    return MetricSnapshotV1(
        snapshot_id=f"candidate-metric-{snapshot_hash}",
        schema_version="domain-calibration-metrics-v1",
        corpus_sha256=run.version_set.corpus_sha256,
        version_set=run.version_set,
        assertion_count=len(run.assertion_results),
        determinism_rate=determinism_rate,
        pillar_agreement_rate=pillar_agreement_rate,
        evidence_trace_completeness_rate=evidence_rate,
        rule_trace_completeness_rate=rule_rate,
        adjudication_coverage_rate=adjudication_rate,
        unsupported_computed_count=unsupported_computed_count,
        dependency_bypass_count=dependency_bypass_count,
        school_disagreement_recall=school_recall,
        silent_school_collapse_count=silent_school_collapse_count,
        mandatory_abstention_rate=mandatory_abstention_rate,
        reviewer_raw_agreement=reviewer_raw_agreement,
        reviewer_stratum_agreement=stratum_agreement,
        weighted_kappa=weighted_kappa(labels_a, labels_b),
        jaccard_agreement=jaccard_rate,
        adjudicated_engine_match=adjudicated_engine_match,
        safety_critical_exact_match=safety_exact,
        coverage=_coverage_maps(assertions, case_by_id, result_by_id),
        baseline_deltas=_baseline_deltas(
            metric_values,
            run.version_set,
            baseline,
        ),
    )


def write_candidate_baseline(
    target: str | Path,
    snapshot: MetricSnapshotV1,
) -> None:
    """Write one explicitly named test-local candidate, never tracked data."""
    if not isinstance(snapshot, MetricSnapshotV1):
        raise TypeError("snapshot must be MetricSnapshotV1")
    path = Path(target)
    if path.name != "calibration_baseline_candidate.json":
        raise CalibrationProtocolError("candidate baseline target name is invalid")
    tracked_root = Path(__file__).resolve().parent / "data" / "domain_calibration"
    resolved = path.resolve()
    try:
        resolved.relative_to(tracked_root.resolve())
    except ValueError:
        pass
    else:
        raise CalibrationProtocolError(
            "candidate baseline cannot target tracked calibration data"
        )
    if not resolved.parent.is_dir():
        raise CalibrationProtocolError("candidate baseline target parent is unavailable")
    envelope = {
        "schema_version": "domain-calibration-file-v1",
        "suite_version": _CALIBRATION_SUITE_VERSION,
        "generated_from": (snapshot.corpus_sha256,),
        "contains_real_personal_data": False,
        "payload_sha256": records_payload_sha256((snapshot,)),
        "records": (snapshot,),
    }
    resolved.write_bytes(canonical_json_bytes(envelope))
