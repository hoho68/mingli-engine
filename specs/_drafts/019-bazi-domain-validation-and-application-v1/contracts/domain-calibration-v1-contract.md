# Domain Calibration V1 Contract

## Claim Boundary

The calibration supports only this claim: independent agent-based domain-conformance calibration of deterministic structural outputs against tracked traditional-method evidence and blinded reviewer labels.

It does not establish scientific validity, causal or predictive accuracy, real-world outcome accuracy, human expert review, universal school agreement, geographic timezone support, or true-solar-time support. Reviewer kind is exactly `agent_independent` and isolation is procedural rather than an OS-level sandbox claim.

## Canonical File Envelope

Every domain-calibration JSON file uses:

```json
{
  "schema_version": "domain-calibration-file-v1",
  "suite_version": "domain-calibration-suite-v1",
  "generated_from": [],
  "contains_real_personal_data": false,
  "payload_sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
  "records": []
}
```

Rules:

- Exact keys are required and unknown keys are rejected.
- `records` are sorted by the record type's primary ID.
- `generated_from` is a canonically sorted tuple of upstream SHA-256 values.
- `payload_sha256` is SHA-256 over UTF-8 canonical JSON of `records` alone using sorted keys, separators `,` and `:`, and no NaN.
- Privacy declaration is false for real personal data in every file.
- Loaders reject missing, duplicate, malformed, noncanonical, hash-mismatched, privacy-invalid, and cross-reference-invalid records and never repair files.

Primary IDs are:

```text
CalibrationInputFixture: fixture_id
CalibrationCase: case_id
CalibrationAssertion: assertion_id
CalibrationCitation: citation_id
ReviewerPacket: packet_id
ReviewAssignment: assignment_id
CalibrationReview: review_id
AdjudicationDecision: adjudication_id
CalibrationRun: run_id
MetricSnapshotV1: snapshot_id
```

A release decision is one record using schema `domain-calibration-release-v1`.

## Exact Record Fields

```text
CalibrationInputFixture: fixture_id, schema_version, request_payload,
  expected_boundary, source_fixture_file, source_fixture_id,
  source_fixture_sha256

CalibrationCase: case_id, case_version, input_fixture_file, input_fixture_id,
  input_sha256, source_fixture_file, source_fixture_id,
  source_fixture_sha256, stratum, coverage_tags, claim_scope,
  contains_real_personal_data

CalibrationAssertion: assertion_id, case_id, rule_family, school_id,
  assertion_kind, field_path, acceptable_statuses, acceptable_values,
  required_rule_ids, required_evidence_ids, limitations

CalibrationCitation: citation_id, assertion_id, evidence_ids, source_locators,
  rule_ids, applicability, limitations

BlindedAssertionProjection: assertion_id, synthetic_case_facts, rule_family,
  school_id, assertion_kind, field_path, candidate_statuses, candidate_values,
  candidate_rule_ids, candidate_evidence_ids, limitations

ReviewerPacket: packet_id, assertion, citation_ids, evidence_excerpts,
  source_locators, rule_scope, limitations, access_manifest

ReviewAssignment: assignment_id, reviewer_id, reviewer_kind, packet_id,
  packet_sha256, access_manifest, peer_labels_hidden, engine_output_hidden,
  independence_attested

CalibrationReview: review_id, assignment_id, assertion_id, label,
  expected_statuses, acceptable_values, confidence, rationale, evidence_ids,
  source_locators, packet_sha256

AdjudicationDecision: adjudication_id, assertion_id, reviewer_a_review_id,
  reviewer_b_review_id, agreement_state, decision, final_statuses,
  final_acceptable_values, retained_alternatives, rationale, evidence_ids,
  safety_critical

CalibrationAssertionResult: assertion_id, actual_status, actual_values,
  actual_rule_ids, actual_evidence_ids, matched, failure_codes

ExactVersionSet: application_version, engine_version, ruleset_version,
  provider_version, school_profile_version, fixture_version,
  evidence_baseline_id, corpus_sha256

CalibrationRun: run_id, version_set, assertion_results

MetricSnapshotV1: snapshot_id, schema_version, corpus_sha256, version_set,
  assertion_count, determinism_rate, pillar_agreement_rate,
  evidence_trace_completeness_rate, rule_trace_completeness_rate,
  adjudication_coverage_rate, unsupported_computed_count,
  dependency_bypass_count, school_disagreement_recall,
  silent_school_collapse_count, mandatory_abstention_rate,
  reviewer_raw_agreement, reviewer_stratum_agreement, weighted_kappa,
  jaccard_agreement, adjudicated_engine_match,
  safety_critical_exact_match, coverage, baseline_deltas

CalibrationReleaseDecision: schema_version, release_status, checks, metrics,
  blockers, claim_boundary, version_set, next_action
```

All records are frozen and sequence fields normalize to tuples.

`ExactVersionSet` is a frozen exact-key DTO with no optional or additional fields. `CalibrationRun.version_set`, the `MetricSnapshotV1.version_set` stored in `calibration_baseline.json`, and `CalibrationReleaseDecision.version_set` must be structurally and value-wise identical. `MetricSnapshotV1.corpus_sha256` must equal `version_set.corpus_sha256`; any mismatch blocks release before metric thresholds are evaluated.

## Corpus Contract

- At least 42 assertions are adjudicated.
- The active rule family IDs are exactly `pattern_strength`, `five_element_balance`, `useful_god_candidate`, `taboo_god_candidate`, `ten_god_relation`, `branch_interaction`, `blind_image_method`, `luck_cycle`, `remedy_boundary`, and `high_risk_signal`; each covers positive, counterexample, and boundary or abstention behavior where applicable.
- The enabled school IDs are exactly `ziping`, `liang_xiangrun`, and `duan`; each covers agreement, disagreement, counterexample, and `not_computed` or abstention behavior.
- `mingli_engine.formal_interpretation.get_formal_interpretation_rule_families()` is the sole rule-family authority, and `src/mingli_engine/data/calculation/school_profiles.json` `enabled` is the sole school authority. Calibration validation reads and compares those sources and defines no second independent allowlist.
- Calendrical cases link to tracked cross-provider pillar artifacts.
- Explicit cases cover dependency degradation, empty branch relations, severe conflict, unknown gender, aware datetime rejection, and high-risk refusal.
- `pattern_counterexamples.json` case `strength_indeterminate_prerequisite` is represented.
- `verified_charts.json` case `synthetic_01_19961215_0930` is represented.
- `source_conflicts.json` case `conflict_high_risk_scope_001` is represented.
- `strength_boundary_cases.json` case `unknown_gender_luck_prerequisite` is represented.
- Aware datetime UTC+08, UTC, and UTC-05 rejection cases from `luck_cycle_boundary_cases.json` are represented.
- Packaged fixture `safety_high_risk_lifespan_refusal_001` represents the existing lifespan safety refusal.
- Every case executes a minimal record from packaged `input_fixtures.json` and separately records original source fixture lineage and hash.
- Installed runtime never reads `tests/` or a source-checkout path.
- No record contains real personal data or new raw source material.

## Blinded Packet Contract

Each packet embeds one `BlindedAssertionProjection` and includes only synthetic case facts needed to assess the candidate claim, citation IDs, concise evidence excerpts, source locators, rule scope, and limitations.

The exact access manifest is:

```text
provided_packet_bytes_only
tools_disabled
filesystem_disabled
peer_labels_absent
engine_output_absent
```

Packet canonical bytes are canonical JSON of the `ReviewerPacket` value alone. Packets exclude current engine output, adjudicated expectations, expected fixtures, peer labels, source-checkout paths, unrelated corpus records, and hidden fields.

## Independent Review Contract

Reviewer A and Reviewer B run in separate fresh contexts with `fork_context=false`. Each receives only canonical packet bytes and instructions forbidding tools and filesystem access. The controller owns all file writes.

Assignments require distinct reviewer, assignment, and review IDs; identical packet hashes; `reviewer_kind=agent_independent`; exact access manifests; hidden peer labels and engine output; and independence attestation.

Review labels are exactly `accept`, `revise`, `reject`, or `abstain`. `abstain` is the only abstention source of truth and requires empty `expected_statuses` and `acceptable_values`. Every other label requires at least one expected status. Reviews include confidence, rationale, evidence IDs, source locators, and exact packet hash.

An assertion with fewer than two valid independent reviews is `self_reviewed` and does not count toward the independent-calibration release label.

## Adjudication Contract

A separate adjudicator receives both frozen reviews, citations, and claim boundary but no current engine output. Every assertion references both review IDs.

Allowed decisions are agreement, clerical correction, retained alternative, and unresolved disagreement. Adjudication may correct clerical or evidence errors but must retain legitimate school alternatives or mark them disputed. It cannot silently select a universal school winner. Safety-critical decisions require exact final expectations.

Adjudicated expectations are frozen and hashed before engine execution.

## Execution Contract

The runner executes the exact application, engine, ruleset, provider, school-profile, evidence-baseline, fixture, and corpus versions in `ExactVersionSet`. It uses packaged synthetic inputs, does not mutate reviews or adjudication, and produces deterministic `CalibrationAssertionResult` records with actual statuses, values, rule IDs, evidence IDs, match state, and stable failure codes.

The baseline stores exact version set, corpus hashes, metrics, and claim boundary. Runtime computes deltas but never rewrites the baseline.

## Metric Contract

- Determinism compares repeated exact-version runs.
- Pillar agreement uses existing tracked cross-provider artifacts.
- `evidence_trace_completeness_rate` equals the number of executed assertions whose actual evidence IDs include every required evidence ID divided by all executed assertions.
- `rule_trace_completeness_rate` equals the number of executed assertions whose actual rule IDs include every required rule ID divided by all executed assertions.
- `adjudication_coverage_rate` equals the number of release-counted assertions with one valid frozen adjudication referencing both valid independent reviews divided by all release-counted assertions.
- An empty denominator for any of these three rates is invalid and blocks release.
- Unsupported-computed and dependency-bypass counts identify forbidden computation.
- Mandatory abstention rate covers unsupported and safety-refusal expectations.
- School-disagreement recall and silent-collapse count preserve school alternatives.
- Raw reviewer agreement is exact equality across all four labels.
- `reviewer_stratum_agreement` has exactly `calendrical`, `structural`, and `school` keys. Denominators include assertions with exactly two valid independent reviews, including abstentions.
- Global weighted kappa uses paired non-abstention labels ordered `reject=0`, `revise=1`, `accept=2` with linear weight `1 - abs(i-j)/2`; it is null below 10 eligible pairs and 1.0 when expected disagreement is zero.
- Jaccard agreement compares acceptable-value sets and returns 1.0 for two empty sets.
- Coverage maps report family, school, status, assertion kind, evidence source, and stratum without creating extra release thresholds.
- Baseline deltas are bound to every `ExactVersionSet` field, including application and provider versions.

These are conformance metrics and never predictive-accuracy metrics.

## Release Contract

All conditions are mandatory:

- Determinism equals 1.0.
- Existing cross-provider pillar agreement equals 1.0.
- `evidence_trace_completeness_rate`, `rule_trace_completeness_rate`, and `adjudication_coverage_rate` each equal 1.0.
- Unsupported-computed and dependency-bypass counts equal zero.
- Silent school-disagreement collapse equals zero.
- School-disagreement recall equals 1.0.
- Mandatory abstention and refusal cases equal 1.0.
- Each counted assertion has two valid independent reviews.
- Overall reviewer raw agreement is at least 0.70.
- No stratum with at least 10 paired observations is below 0.60 raw agreement.
- Adjudicated engine acceptable-set match is at least 0.90 overall.
- Every safety-critical assertion matches exactly.
- Application contract, privacy, packaging, no-retention, compatibility, and documentation checks pass.
- Documentation repeats the claim boundary and exact version set.
- Calibration run, baseline snapshot, and release decision carry exactly equal `ExactVersionSet` values.

Any failure blocks the 019 application and calibration release label without rewriting the historical 018 operational result.

## Packaging Contract

The built wheel includes every JSON resource under `mingli_engine/data/`, including all domain calibration files. Release verification builds without network access, inspects the wheel manifest, installs to a temporary target, and runs chart analysis, evidence-backed report generation, calibration summary, and real-use CLI outside the checkout.

The installed calibration child receives an explicit local `PackagingVerification` so it verifies installed resources and source isolation without recursively building another wheel. Package version advances from 0.1.0 to 0.2.0 only after every non-version gate passes and fresh wheel verification is recomputed.
