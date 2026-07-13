# Data Model: Bazi Domain Validation And Application V1

## Application Request Models

### RealUseProfileV1

Exact fields: `calendar_type`, `birth_date`, `birth_time`, `birthplace`, `gender`, `focus_topic`.

Rules: Gregorian input only; dates from 1901-01-01 through 2099-12-31; UTC+08 wall time; no aware datetime or true solar time; birthplace at most 160 Unicode code points; focus topic at most 500 Unicode code points.

### AuthorizationAttestationV1

Exact fields: `subject_relation`, `attested`.

Rules: relation is `self` or `authorized_other`; false attestation is schema-valid but refuses before calculation.

### RealUseOptionsV1

Exact required fields: `report_format`, `include_profile_in_report`.

Rules: analysis requires null format; report requires `json`, `markdown`, or `html`; `include_profile_in_report` is always present and is a boolean. Omission and defaulting are invalid.

### RealUseRequestV1

Exact required fields: `schema_version`, `request_id`, `operation`, `profile`, `authorization`, `options`.

Rules: schema is `real-use-request-v1`; operation is `analysis` or `report`; the `request_id` key is always present and its value is null or matches `[A-Za-z0-9_-]{1,64}`. Every root and nested request field is required exactly once; missing and unknown fields are invalid.

## Application Response Models

### RealUseResponseV1

Exact fields: `schema_version`, `trace_id`, `operation`, `status`, `result`, `safety`, `provenance`, `warnings`, `privacy`, `error`.

Rules: schema is `real-use-response-v1`; trace ID is random UUID4; status is `ok`, `refused`, or `error`; operation is null only for strict parsing failure; result type matches operation and status; warnings are immutable.

### Nested Response Models

- `ApplicationErrorV1`: `code`, `message`, `field_path`, `retryable`, `trace_id`.
- `ApplicationSafetyV1`: `allowed`, `decision`, `categories`, `redirect_message`, `requires_narrowing`.
- `ApplicationProvenanceV1`: `engine_version`, `ruleset_version`, `provider_version`, `chart_source_type`, `chart_source_confidence`, `evidence_baseline_id`, `evidence_ids`.
- `ApplicationWarningV1`: `code`, `message`.
- `ApplicationPrivacyV1`: `retention`, `contains_sensitive_profile`.
- `ApplicationContentV1`: `media_type`, `content`, `contains_sensitive_profile`.
- `ApplicationAnalysisResultV1`: `chart`, `calculation`.
- `ApplicationReportResultV1`: `report`, `content`.

All DTOs are frozen. Sequences normalize to tuples. Public maps are created explicitly rather than through generic dataclass conversion.

## Application State Flow

```text
raw bytes
  -> strict parse failure: error, operation null
  -> parsed request
       -> attestation failure: refused
       -> safety failure: refused
       -> analysis success: ok with analysis result
       -> report post-build refusal: refused
       -> report success: ok with report result
       -> controlled or unexpected failure: error
```

Stable error codes are `invalid_json`, `invalid_request`, `authorization_required`, `unsafe_request`, `unsupported_input`, `payload_too_large`, `response_too_large`, `calculation_failed`, `knowledge_unavailable`, and `internal_error`.

### Required Non-OK Response Matrix

| Outcome | status | operation | result | safety | provenance | privacy | error |
|---|---|---|---|---|---|---|---|
| Parse error | `error` | null | null | `allowed=false`, `decision=not_evaluated`, empty categories and redirect, `requires_narrowing=false` | null | `retention=not_stored_by_engine`, `contains_sensitive_profile=false` | non-null parse code with matching trace ID |
| Authorization refusal | `refused` | parsed operation | null | `allowed=false`, `decision=authorization_required`, categories `authorization`, fixed attestation redirect, `requires_narrowing=false` | null | `retention=not_stored_by_engine`, `contains_sensitive_profile=false` | non-null `authorization_required` |
| Unsafe refusal | `refused` | parsed operation | null | `allowed=false`, `decision=unsafe_request`, non-empty normalized categories, non-empty safe redirect, `requires_narrowing=true` | null | `retention=not_stored_by_engine`, `contains_sensitive_profile=false` | non-null `unsafe_request` |
| Internal error after parse | `error` | parsed operation | null | `allowed=false`, `decision=error`, empty categories and redirect, `requires_narrowing=false` | null | `retention=not_stored_by_engine`, `contains_sensitive_profile=false` | non-null `internal_error` |

## Verification Models

### ApplicationVerification

A deterministic read-only map covering fixed synthetic success, refusal, validation failure, and internal error scenarios. It records scenario name, contract status, privacy status, write count, leak count, version identifiers, and overall status. It stores no request or report body.

### PackagingVerification

A deterministic map of required installed asset path to SHA-256 plus distribution version, source-isolation status, and overall status. It is constructed from installed resources and never writes a report.

## Calibration Envelope

### CalibrationFileEnvelopeV1

Exact fields: `schema_version`, `suite_version`, `generated_from`, `contains_real_personal_data`, `payload_sha256`, `records`.

Rules: records use exact keys and canonical primary-ID order; `contains_real_personal_data` is false; `generated_from` is a sorted tuple of upstream SHA-256 values; `payload_sha256` hashes UTF-8 canonical JSON of `records` alone with sorted keys, compact separators, and no NaN.

Primary IDs by record are `fixture_id`, `case_id`, `assertion_id`, `citation_id`, `packet_id`, `assignment_id`, `review_id`, `adjudication_id`, `run_id`, and `snapshot_id`. The release decision is a single-record envelope using schema `domain-calibration-release-v1`.

## Calibration Input And Assertion Models

### CalibrationInputFixture

Exact fields: `fixture_id`, `schema_version`, `request_payload`, `expected_boundary`, `source_fixture_file`, `source_fixture_id`, `source_fixture_sha256`.

Rules: contains minimal packaged synthetic input; preserves original test or safety fixture lineage; runtime uses only packaged resources.

### CalibrationCase

Exact fields: `case_id`, `case_version`, `input_fixture_file`, `input_fixture_id`, `input_sha256`, `source_fixture_file`, `source_fixture_id`, `source_fixture_sha256`, `stratum`, `coverage_tags`, `claim_scope`, `contains_real_personal_data`.

Rules: stratum is `calendrical`, `structural`, or `school`; fixture hashes resolve; personal-data flag is false.

### CalibrationAssertion

Exact fields: `assertion_id`, `case_id`, `rule_family`, `school_id`, `assertion_kind`, `field_path`, `acceptable_statuses`, `acceptable_values`, `required_rule_ids`, `required_evidence_ids`, `limitations`.

Rules: assertion kind is `positive`, `counterexample`, `boundary`, `abstention`, or `disagreement`; school ID is nullable; references resolve to case, rules, and formal evidence.

### CalibrationCitation

Exact fields: `citation_id`, `assertion_id`, `evidence_ids`, `source_locators`, `rule_ids`, `applicability`, `limitations`.

Rules: all references resolve and only concise allowlisted evidence excerpts are packetized.

## Blind Review Models

### BlindedAssertionProjection

Exact fields: `assertion_id`, `synthetic_case_facts`, `rule_family`, `school_id`, `assertion_kind`, `field_path`, `candidate_statuses`, `candidate_values`, `candidate_rule_ids`, `candidate_evidence_ids`, `limitations`.

Rules: embedded in a packet; contains only non-personal synthetic facts and candidate claim data; contains no engine output.

### ReviewerPacket

Exact fields: `packet_id`, `assertion`, `citation_ids`, `evidence_excerpts`, `source_locators`, `rule_scope`, `limitations`, `access_manifest`.

Rules: canonical packet hash covers the packet value alone. Access manifest is exactly `provided_packet_bytes_only`, `tools_disabled`, `filesystem_disabled`, `peer_labels_absent`, `engine_output_absent`.

### ReviewAssignment

Exact fields: `assignment_id`, `reviewer_id`, `reviewer_kind`, `packet_id`, `packet_sha256`, `access_manifest`, `peer_labels_hidden`, `engine_output_hidden`, `independence_attested`.

Rules: reviewer kind is `agent_independent`; reviewer A and B identifiers are distinct; all independence booleans are true.

### CalibrationReview

Exact fields: `review_id`, `assignment_id`, `assertion_id`, `label`, `expected_statuses`, `acceptable_values`, `confidence`, `rationale`, `evidence_ids`, `source_locators`, `packet_sha256`.

Rules: label is `accept`, `revise`, `reject`, or `abstain`. Abstain is the sole abstention source and requires empty expectation tuples; other labels require at least one expected status.

### AdjudicationDecision

Exact fields: `adjudication_id`, `assertion_id`, `reviewer_a_review_id`, `reviewer_b_review_id`, `agreement_state`, `decision`, `final_statuses`, `final_acceptable_values`, `retained_alternatives`, `rationale`, `evidence_ids`, `safety_critical`.

Rules: decisions are agreement, clerical correction, retained alternative, or unresolved disagreement; legitimate school differences remain explicit; safety-critical expectations are exact.

## Execution And Metric Models

### ExactVersionSet

Exact fields: `application_version`, `engine_version`, `ruleset_version`, `provider_version`, `school_profile_version`, `fixture_version`, `evidence_baseline_id`, `corpus_sha256`.

Rules: the DTO is frozen with no optional or additional fields. A Task 14 candidate uses target `application_version=0.2.0` and is not release evidence. After Task 16 installs version 0.2.0, the fresh final `CalibrationRun.version_set`, final baseline `MetricSnapshotV1.version_set`, and `CalibrationReleaseDecision.version_set` are structurally and value-wise equal. Any target/installed mismatch or final-artifact mismatch blocks release. `MetricSnapshotV1.corpus_sha256` equals `version_set.corpus_sha256`.

### CalibrationAssertionResult

Exact fields: `assertion_id`, `actual_status`, `actual_values`, `actual_rule_ids`, `actual_evidence_ids`, `matched`, `failure_codes`.

### CalibrationRun

Exact fields: `run_id`, `version_set`, `assertion_results`.

Rules: read-only execution uses frozen adjudication and exact packaged inputs; repeated runs are deterministic. Task 14 output is a candidate run against the declared 0.2.0 target and cannot be promoted directly. Task 16 executes a new final run from the installed 0.2.0 distribution.

### MetricSnapshotV1

Exact fields: `snapshot_id`, `schema_version`, `corpus_sha256`, `version_set`, `assertion_count`, `determinism_rate`, `pillar_agreement_rate`, `evidence_trace_completeness_rate`, `rule_trace_completeness_rate`, `adjudication_coverage_rate`, `unsupported_computed_count`, `dependency_bypass_count`, `school_disagreement_recall`, `silent_school_collapse_count`, `mandatory_abstention_rate`, `reviewer_raw_agreement`, `reviewer_stratum_agreement`, `weighted_kappa`, `jaccard_agreement`, `adjudicated_engine_match`, `safety_critical_exact_match`, `coverage`, `baseline_deltas`.

Rules: `evidence_trace_completeness_rate` is executed assertions whose actual evidence IDs include every required evidence ID divided by all executed assertions. `rule_trace_completeness_rate` is executed assertions whose actual rule IDs include every required rule ID divided by all executed assertions. `adjudication_coverage_rate` is release-counted assertions with one valid frozen adjudication referencing both valid independent reviews divided by all release-counted assertions. Empty denominators are invalid. Raw agreement uses exact four-label equality; global weighted kappa excludes abstentions, orders reject 0, revise 1, accept 2, uses linear weights, is null below 10 eligible pairs, and is 1.0 when expected disagreement is zero; Jaccard returns 1.0 for two empty sets; stratum agreement has exactly calendrical, structural, and school keys.

### CalibrationReleaseDecision

Exact fields: `schema_version`, `release_status`, `checks`, `metrics`, `blockers`, `claim_boundary`, `version_set`, `next_action`.

Rules: release status cannot pass with a failed mandatory gate; blockers are deterministic; claim boundary and version set are always present.

## Candidate And Final Baseline Lifecycle

Task 14 computes candidate run and snapshot objects with target `application_version=0.2.0`. Candidate baseline serialization is test-local at `tmp_path/calibration_baseline_candidate.json`; it is not packaged, is not a release baseline, and never replaces `src/mingli_engine/data/domain_calibration/calibration_baseline.json`.

Task 15 may prove every non-version gate but keeps release blocked for installed-version mismatch and missing final 0.2.0 calibration artifacts. Task 16 first advances and installs 0.2.0, then reruns the full calibration, creates the final snapshot, and invokes the sole controlled release writer to update and freeze `src/mingli_engine/data/domain_calibration/calibration_baseline.json`. Release is recomputed only after the final run, final baseline snapshot, and release decision carry equal `ExactVersionSet` values.

## Calibration State Flow

```text
curated case and assertion
  -> frozen canonical packet
  -> reviewer A assignment and review
  -> reviewer B assignment and review
  -> frozen adjudication
  -> exact-version engine execution
  -> metric snapshot
  -> release decision
```

Review, adjudication, run, metric, and release loaders are read-only and reject missing, extra, duplicate, malformed, noncanonical, hash-mismatched, privacy-invalid, or cross-reference-invalid data.
