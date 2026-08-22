from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Generic, Literal, TypeVar, cast

from mingli_engine.bazi.schools.base import load_school_profiles_config
from mingli_engine.formal_interpretation import (
    get_formal_interpretation_rule_families,
)


JsonObject = dict[str, object]
T = TypeVar("T")

CalibrationStratum = Literal["calendrical", "structural", "school"]
AssertionKind = Literal[
    "positive",
    "counterexample",
    "boundary",
    "abstention",
    "disagreement",
]
ReviewLabel = Literal["accept", "revise", "reject", "abstain"]
AdjudicationDecisionKind = Literal[
    "agreement",
    "clerical_correction",
    "retained_alternative",
    "unresolved_disagreement",
]

_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
_STRATA = frozenset({"calendrical", "structural", "school"})
_ASSERTION_KINDS = frozenset(
    {"positive", "counterexample", "boundary", "abstention", "disagreement"}
)
_REVIEW_LABELS = frozenset({"accept", "revise", "reject", "abstain"})
_AGREEMENT_STATES = frozenset({"agreement", "disagreement"})
_ADJUDICATION_DECISIONS = frozenset(
    {
        "agreement",
        "clerical_correction",
        "retained_alternative",
        "unresolved_disagreement",
    }
)
_RELEASE_STATUSES = frozenset({"blocked", "ready", "ready_with_guardrails"})
_ACCESS_MANIFEST = (
    "provided_packet_bytes_only",
    "tools_disabled",
    "filesystem_disabled",
    "peer_labels_absent",
    "engine_output_absent",
)


def _require_str(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value or value != value.strip():
        raise ValueError(f"{field_name} must be a nonempty trimmed string")


def _require_literal(
    value: object,
    allowed: frozenset[str],
    field_name: str,
) -> None:
    _require_str(value, field_name)
    if value not in allowed:
        raise ValueError(f"{field_name} is not supported")


def _require_bool(value: object, field_name: str) -> None:
    if type(value) is not bool:
        raise TypeError(f"{field_name} must be bool")


def _require_sha256(value: object, field_name: str) -> None:
    _require_str(value, field_name)
    assert isinstance(value, str)
    if _SHA256_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be lowercase SHA-256")


def _string_tuple(
    value: object,
    field_name: str,
    *,
    unique: bool = True,
) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{field_name} must be a list or tuple")
    result = tuple(value)
    if not all(isinstance(item, str) for item in result):
        raise TypeError(f"{field_name} must contain only str values")
    if any(not item or item != item.strip() for item in result):
        raise ValueError(f"{field_name} must contain nonempty trimmed strings")
    if unique and len(set(result)) != len(result):
        raise ValueError(f"{field_name} values must be unique")
    return result


def _model_tuple(
    value: object,
    expected_type: type[T],
    field_name: str,
) -> tuple[T, ...]:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{field_name} must be a list or tuple")
    result = tuple(value)
    if not all(isinstance(item, expected_type) for item in result):
        raise TypeError(
            f"{field_name} must contain only {expected_type.__name__} values"
        )
    return result


def _mapping(value: object, field_name: str) -> JsonObject:
    if not isinstance(value, dict) or not all(
        isinstance(key, str) for key in value
    ):
        raise TypeError(f"{field_name} must be a string-keyed dict")
    return dict(value)


def _string_mapping(value: object, field_name: str) -> dict[str, str]:
    result = _mapping(value, field_name)
    if not all(isinstance(item, str) for item in result.values()):
        raise TypeError(f"{field_name} values must be str")
    return {key: item for key, item in result.items() if isinstance(item, str)}


def _require_count(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be int")
    if value < 0:
        raise ValueError(f"{field_name} must be nonnegative")


def _require_rate(
    value: object,
    field_name: str,
    *,
    nullable: bool = False,
    minimum: float = 0.0,
) -> None:
    if value is None and nullable:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric) or not minimum <= numeric <= 1.0:
        raise ValueError(f"{field_name} is outside its valid range")


def _require_rule_family(value: object) -> None:
    _require_str(value, "rule_family")
    if value not in get_formal_interpretation_rule_families():
        raise ValueError("rule_family is not authoritative")


def _require_school_id(value: object) -> None:
    if value is None:
        return
    _require_str(value, "school_id")
    if value not in load_school_profiles_config().enabled:
        raise ValueError("school_id is not enabled by school_profiles.json")


@dataclass(frozen=True)
class CalibrationFileEnvelopeV1(Generic[T]):
    schema_version: str
    suite_version: str
    generated_from: tuple[str, ...]
    contains_real_personal_data: bool
    payload_sha256: str
    records: tuple[T, ...]

    def __post_init__(self) -> None:
        _require_literal(
            self.schema_version,
            frozenset(
                {"domain-calibration-file-v1", "domain-calibration-release-v1"}
            ),
            "schema_version",
        )
        if self.suite_version != "domain-calibration-suite-v1":
            raise ValueError("suite_version is not supported")
        generated_from = _string_tuple(self.generated_from, "generated_from")
        if generated_from != tuple(sorted(generated_from)):
            raise ValueError("generated_from must be canonically sorted")
        for item in generated_from:
            _require_sha256(item, "generated_from")
        _require_bool(
            self.contains_real_personal_data,
            "contains_real_personal_data",
        )
        if self.contains_real_personal_data:
            raise ValueError("calibration files cannot contain real personal data")
        _require_sha256(self.payload_sha256, "payload_sha256")
        if not isinstance(self.records, (list, tuple)):
            raise TypeError("records must be a list or tuple")
        object.__setattr__(self, "generated_from", generated_from)
        object.__setattr__(self, "records", tuple(self.records))


@dataclass(frozen=True)
class CalibrationInputFixture:
    fixture_id: str
    schema_version: str
    request_payload: JsonObject
    expected_boundary: str
    source_fixture_file: str
    source_fixture_id: str
    source_fixture_sha256: str

    def __post_init__(self) -> None:
        for field_name in (
            "fixture_id",
            "expected_boundary",
            "source_fixture_file",
            "source_fixture_id",
        ):
            _require_str(getattr(self, field_name), field_name)
        if self.schema_version != "domain-calibration-input-v1":
            raise ValueError("schema_version is not supported")
        object.__setattr__(
            self,
            "request_payload",
            _mapping(self.request_payload, "request_payload"),
        )
        _require_sha256(self.source_fixture_sha256, "source_fixture_sha256")


@dataclass(frozen=True)
class CalibrationCase:
    case_id: str
    case_version: str
    input_fixture_file: str
    input_fixture_id: str
    input_sha256: str
    source_fixture_file: str
    source_fixture_id: str
    source_fixture_sha256: str
    stratum: CalibrationStratum
    coverage_tags: tuple[str, ...]
    claim_scope: str
    contains_real_personal_data: bool

    def __post_init__(self) -> None:
        for field_name in (
            "case_id",
            "case_version",
            "input_fixture_file",
            "input_fixture_id",
            "source_fixture_file",
            "source_fixture_id",
            "claim_scope",
        ):
            _require_str(getattr(self, field_name), field_name)
        _require_sha256(self.input_sha256, "input_sha256")
        _require_sha256(self.source_fixture_sha256, "source_fixture_sha256")
        _require_literal(self.stratum, _STRATA, "stratum")
        object.__setattr__(
            self,
            "coverage_tags",
            _string_tuple(self.coverage_tags, "coverage_tags"),
        )
        _require_bool(
            self.contains_real_personal_data,
            "contains_real_personal_data",
        )
        if self.contains_real_personal_data:
            raise ValueError("calibration cases cannot contain real personal data")


@dataclass(frozen=True)
class CalibrationAssertion:
    assertion_id: str
    case_id: str
    rule_family: str
    school_id: str | None
    assertion_kind: AssertionKind
    field_path: str
    acceptable_statuses: tuple[str, ...]
    acceptable_values: tuple[str, ...]
    required_rule_ids: tuple[str, ...]
    required_evidence_ids: tuple[str, ...]
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_str(self.assertion_id, "assertion_id")
        _require_str(self.case_id, "case_id")
        _require_rule_family(self.rule_family)
        _require_school_id(self.school_id)
        _require_literal(self.assertion_kind, _ASSERTION_KINDS, "assertion_kind")
        _require_str(self.field_path, "field_path")
        for field_name in (
            "acceptable_statuses",
            "acceptable_values",
            "required_rule_ids",
            "required_evidence_ids",
            "limitations",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )


@dataclass(frozen=True)
class CalibrationCitation:
    citation_id: str
    assertion_id: str
    evidence_ids: tuple[str, ...]
    source_locators: tuple[str, ...]
    rule_ids: tuple[str, ...]
    applicability: str
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_str(self.citation_id, "citation_id")
        _require_str(self.assertion_id, "assertion_id")
        _require_str(self.applicability, "applicability")
        for field_name in (
            "evidence_ids",
            "source_locators",
            "rule_ids",
            "limitations",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )


@dataclass(frozen=True)
class BlindedAssertionProjection:
    assertion_id: str
    synthetic_case_facts: JsonObject
    rule_family: str
    school_id: str | None
    assertion_kind: AssertionKind
    field_path: str
    candidate_statuses: tuple[str, ...]
    candidate_values: tuple[str, ...]
    candidate_rule_ids: tuple[str, ...]
    candidate_evidence_ids: tuple[str, ...]
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_str(self.assertion_id, "assertion_id")
        object.__setattr__(
            self,
            "synthetic_case_facts",
            _mapping(self.synthetic_case_facts, "synthetic_case_facts"),
        )
        _require_rule_family(self.rule_family)
        _require_school_id(self.school_id)
        _require_literal(self.assertion_kind, _ASSERTION_KINDS, "assertion_kind")
        _require_str(self.field_path, "field_path")
        for field_name in (
            "candidate_statuses",
            "candidate_values",
            "candidate_rule_ids",
            "candidate_evidence_ids",
            "limitations",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )


@dataclass(frozen=True)
class ReviewerPacket:
    packet_id: str
    assertion: BlindedAssertionProjection
    citation_ids: tuple[str, ...]
    evidence_excerpts: dict[str, str]
    source_locators: tuple[str, ...]
    rule_scope: tuple[str, ...]
    limitations: tuple[str, ...]
    access_manifest: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_str(self.packet_id, "packet_id")
        if not isinstance(self.assertion, BlindedAssertionProjection):
            raise TypeError("assertion must be BlindedAssertionProjection")
        object.__setattr__(
            self,
            "evidence_excerpts",
            _string_mapping(self.evidence_excerpts, "evidence_excerpts"),
        )
        for field_name in (
            "citation_ids",
            "source_locators",
            "rule_scope",
            "limitations",
            "access_manifest",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )
        if self.access_manifest != _ACCESS_MANIFEST:
            raise ValueError("access_manifest is not the exact blinded manifest")


@dataclass(frozen=True)
class ReviewAssignment:
    assignment_id: str
    reviewer_id: str
    reviewer_kind: str
    packet_id: str
    packet_sha256: str
    access_manifest: tuple[str, ...]
    peer_labels_hidden: bool
    engine_output_hidden: bool
    independence_attested: bool

    def __post_init__(self) -> None:
        for field_name in ("assignment_id", "reviewer_id", "packet_id"):
            _require_str(getattr(self, field_name), field_name)
        if self.reviewer_kind != "agent_independent":
            raise ValueError("reviewer_kind must be agent_independent")
        _require_sha256(self.packet_sha256, "packet_sha256")
        manifest = _string_tuple(self.access_manifest, "access_manifest")
        if manifest != _ACCESS_MANIFEST:
            raise ValueError("access_manifest is not the exact blinded manifest")
        object.__setattr__(self, "access_manifest", manifest)
        for field_name in (
            "peer_labels_hidden",
            "engine_output_hidden",
            "independence_attested",
        ):
            value = getattr(self, field_name)
            _require_bool(value, field_name)
            if not value:
                raise ValueError(f"{field_name} must be true")


@dataclass(frozen=True)
class CalibrationReview:
    review_id: str
    assignment_id: str
    assertion_id: str
    label: ReviewLabel
    expected_statuses: tuple[str, ...]
    acceptable_values: tuple[str, ...]
    confidence: float
    rationale: str
    evidence_ids: tuple[str, ...]
    source_locators: tuple[str, ...]
    packet_sha256: str

    def __post_init__(self) -> None:
        for field_name in (
            "review_id",
            "assignment_id",
            "assertion_id",
            "rationale",
        ):
            _require_str(getattr(self, field_name), field_name)
        _require_literal(self.label, _REVIEW_LABELS, "label")
        for field_name in (
            "expected_statuses",
            "acceptable_values",
            "evidence_ids",
            "source_locators",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )
        if self.label == "abstain":
            if self.expected_statuses or self.acceptable_values:
                raise ValueError("abstain requires empty expectation tuples")
        elif not self.expected_statuses:
            raise ValueError("non-abstain review requires an expected status")
        _require_rate(self.confidence, "confidence")
        _require_sha256(self.packet_sha256, "packet_sha256")


@dataclass(frozen=True)
class AdjudicationDecision:
    adjudication_id: str
    assertion_id: str
    reviewer_a_review_id: str
    reviewer_b_review_id: str
    agreement_state: str
    decision: AdjudicationDecisionKind
    final_statuses: tuple[str, ...]
    final_acceptable_values: tuple[str, ...]
    retained_alternatives: tuple[str, ...]
    rationale: str
    evidence_ids: tuple[str, ...]
    safety_critical: bool

    def __post_init__(self) -> None:
        for field_name in (
            "adjudication_id",
            "assertion_id",
            "reviewer_a_review_id",
            "reviewer_b_review_id",
            "rationale",
        ):
            _require_str(getattr(self, field_name), field_name)
        if self.reviewer_a_review_id == self.reviewer_b_review_id:
            raise ValueError("adjudication requires two distinct review IDs")
        _require_literal(
            self.agreement_state,
            _AGREEMENT_STATES,
            "agreement_state",
        )
        _require_literal(
            self.decision,
            _ADJUDICATION_DECISIONS,
            "decision",
        )
        for field_name in (
            "final_statuses",
            "final_acceptable_values",
            "retained_alternatives",
            "evidence_ids",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )
        _require_bool(self.safety_critical, "safety_critical")


@dataclass(frozen=True)
class ExactVersionSet:
    application_version: str
    engine_version: str
    ruleset_version: str
    provider_version: str
    school_profile_version: str
    fixture_version: str
    evidence_baseline_id: str
    corpus_sha256: str

    def __post_init__(self) -> None:
        for field_name in (
            "application_version",
            "engine_version",
            "ruleset_version",
            "provider_version",
            "school_profile_version",
            "fixture_version",
            "evidence_baseline_id",
        ):
            _require_str(getattr(self, field_name), field_name)
        _require_sha256(self.corpus_sha256, "corpus_sha256")


@dataclass(frozen=True)
class CalibrationAssertionResult:
    assertion_id: str
    actual_status: str
    actual_values: tuple[str, ...]
    actual_rule_ids: tuple[str, ...]
    actual_evidence_ids: tuple[str, ...]
    matched: bool
    failure_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_str(self.assertion_id, "assertion_id")
        _require_str(self.actual_status, "actual_status")
        for field_name in (
            "actual_values",
            "actual_rule_ids",
            "actual_evidence_ids",
            "failure_codes",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )
        _require_bool(self.matched, "matched")


@dataclass(frozen=True)
class CalibrationRun:
    run_id: str
    version_set: ExactVersionSet
    assertion_results: tuple[CalibrationAssertionResult, ...]

    def __post_init__(self) -> None:
        _require_str(self.run_id, "run_id")
        if not isinstance(self.version_set, ExactVersionSet):
            raise TypeError("version_set must be ExactVersionSet")
        object.__setattr__(
            self,
            "assertion_results",
            _model_tuple(
                self.assertion_results,
                CalibrationAssertionResult,
                "assertion_results",
            ),
        )


@dataclass(frozen=True)
class MetricSnapshotV1:
    snapshot_id: str
    schema_version: str
    corpus_sha256: str
    version_set: ExactVersionSet
    assertion_count: int
    determinism_rate: float
    pillar_agreement_rate: float
    evidence_trace_completeness_rate: float
    rule_trace_completeness_rate: float
    adjudication_coverage_rate: float
    unsupported_computed_count: int
    dependency_bypass_count: int
    school_disagreement_recall: float
    silent_school_collapse_count: int
    mandatory_abstention_rate: float
    reviewer_raw_agreement: float
    reviewer_stratum_agreement: dict[str, float]
    weighted_kappa: float | None
    jaccard_agreement: float
    adjudicated_engine_match: float
    safety_critical_exact_match: float
    coverage: JsonObject
    baseline_deltas: JsonObject

    def __post_init__(self) -> None:
        _require_str(self.snapshot_id, "snapshot_id")
        if self.schema_version != "domain-calibration-metrics-v1":
            raise ValueError("schema_version is not supported")
        _require_sha256(self.corpus_sha256, "corpus_sha256")
        if not isinstance(self.version_set, ExactVersionSet):
            raise TypeError("version_set must be ExactVersionSet")
        if self.corpus_sha256 != self.version_set.corpus_sha256:
            raise ValueError("corpus_sha256 must equal version_set.corpus_sha256")
        for field_name in (
            "assertion_count",
            "unsupported_computed_count",
            "dependency_bypass_count",
            "silent_school_collapse_count",
        ):
            _require_count(getattr(self, field_name), field_name)
        for field_name in (
            "determinism_rate",
            "pillar_agreement_rate",
            "evidence_trace_completeness_rate",
            "rule_trace_completeness_rate",
            "adjudication_coverage_rate",
            "school_disagreement_recall",
            "mandatory_abstention_rate",
            "reviewer_raw_agreement",
            "jaccard_agreement",
            "adjudicated_engine_match",
            "safety_critical_exact_match",
        ):
            _require_rate(getattr(self, field_name), field_name)
        _require_rate(
            self.weighted_kappa,
            "weighted_kappa",
            nullable=True,
            minimum=-1.0,
        )
        stratum_rates = _mapping(
            self.reviewer_stratum_agreement,
            "reviewer_stratum_agreement",
        )
        if set(stratum_rates) != _STRATA:
            raise ValueError(
                "reviewer_stratum_agreement requires exact stratum keys"
            )
        for key, value in stratum_rates.items():
            _require_rate(value, f"reviewer_stratum_agreement.{key}")
        object.__setattr__(
            self,
            "reviewer_stratum_agreement",
            {
                key: float(cast(int | float, value))
                for key, value in stratum_rates.items()
            },
        )
        object.__setattr__(self, "coverage", _mapping(self.coverage, "coverage"))
        object.__setattr__(
            self,
            "baseline_deltas",
            _mapping(self.baseline_deltas, "baseline_deltas"),
        )


@dataclass(frozen=True)
class CalibrationReleaseDecision:
    schema_version: str
    release_status: str
    checks: dict[str, str]
    metrics: MetricSnapshotV1
    blockers: tuple[str, ...]
    claim_boundary: str
    version_set: ExactVersionSet
    next_action: str

    def __post_init__(self) -> None:
        _require_str(self.schema_version, "schema_version")
        if self.schema_version != "domain-calibration-release-v1":
            raise ValueError("schema_version is not supported")
        _require_literal(self.release_status, _RELEASE_STATUSES, "release_status")
        object.__setattr__(self, "checks", _string_mapping(self.checks, "checks"))
        if not isinstance(self.metrics, MetricSnapshotV1):
            raise TypeError("metrics must be MetricSnapshotV1")
        object.__setattr__(
            self,
            "blockers",
            _string_tuple(self.blockers, "blockers"),
        )
        _require_str(self.claim_boundary, "claim_boundary")
        if not isinstance(self.version_set, ExactVersionSet):
            raise TypeError("version_set must be ExactVersionSet")
        if self.version_set != self.metrics.version_set:
            raise ValueError("release and metric version_set values must match")
        _require_str(self.next_action, "next_action")
        if self.release_status != "blocked" and (
            self.blockers or any(value != "passed" for value in self.checks.values())
        ):
            raise ValueError("ready release cannot contain failed gates")
