# Bazi Domain Validation And Application V1 Design

**Feature:** 019-bazi-domain-validation-and-application-v1  
**Date:** 2026-07-13  
**Branch:** `codex/019-bazi-domain-validation-application`  
**Status:** Approved design

## 1. Purpose

Feature 018 made the deterministic Bazi inference engine operational inside the
repository. Feature 019 makes that engine usable through a supported,
versioned application boundary and adds an independently reviewed traditional
method conformance calibration layer.

The feature does not add raw source material. It uses only the tracked formal
evidence corpus, existing synthetic charts, existing boundary fixtures, and
the three implemented school adapters.

## 2. Claim Boundary

The strongest permitted claim is:

> Independent agent-based domain-conformance calibration of deterministic
> structural outputs against tracked traditional-method evidence and blinded
> reviewer labels.

The feature does not establish:

- scientific validity;
- causal or predictive accuracy;
- real-world outcome accuracy;
- human expert review;
- universal agreement between traditional schools;
- geographic timezone or true-solar-time support.

Reviewer records use `reviewer_kind=agent_independent`. Documentation and
runtime responses must not call these reviewers human experts.

## 3. Goals

1. Add a versioned, public Python application facade.
2. Add a versioned, strict JSON CLI command for controlled real use.
3. Require explicit self-use or authorized-other attestation before any
   calculation.
4. Keep chart calculation, analysis, and report generation in one process and
   one request so the existing provenance binding remains effective.
5. Build a blinded two-reviewer calibration workflow with separate
   adjudication.
6. Produce traceable conformance metrics and release gates by rule family and
   school.
7. Package every required JSON data asset into the built wheel and verify the
   installed distribution.
8. Preserve the existing low-level engine and CLI commands except for explicit
   security hardening.

## 4. Non-Goals

- No HTTP server or network listener.
- No browser or desktop UI.
- No database, vector store, account system, or session persistence.
- No external chart input in the new real-use contract.
- No serialized `CalculationBundle` input.
- No longitude, timezone lookup, or true-solar-time calculation.
- No automatic evidence promotion or new source extraction.
- No personal birth-profile or generated-report retention by the engine.

HTTP and UI adapters belong to a later feature after the application contract
has demonstrated stability.

## 5. Selected Architecture

The design uses four layers:

```text
strict request parser
  -> application facade
       -> authorization and safety boundary
       -> chart + analysis + report in one process
       -> explicit public serializers
  -> versioned response envelope

tracked calibration corpus
  -> blinded reviewer A and reviewer B labels
  -> adjudication
  -> calibration runner and metric snapshot
  -> application/calibration release gates
```

### 5.1 New Modules

```text
src/mingli_engine/
|-- application_models.py
|-- application_inputs.py
|-- application_serialization.py
|-- application_service.py
|-- application_reports.py
|-- application_validation.py
|-- packaging_validation.py
|-- domain_calibration.py
|-- domain_calibration_models.py
|-- domain_calibration_release.py
`-- data/domain_calibration/
    |-- calibration_cases.json
    |-- input_fixtures.json
    |-- calibration_assertions.json
    |-- calibration_citations.json
    |-- reviewer_packets.json
    |-- reviewer_a_assignments.json
    |-- reviewer_a_reviews.json
    |-- reviewer_b_assignments.json
    |-- reviewer_b_reviews.json
    |-- adjudication.json
    `-- calibration_baseline.json
```

Each module has one responsibility. The facade does not parse unbounded JSON,
the parser does not calculate charts, and the calibration runner does not
modify review records.

## 6. Application Contract

### 6.1 Request V1

`RealUseRequestV1` is a frozen dataclass with the following fields:

```text
schema_version: "real-use-request-v1"
request_id: optional opaque ASCII identifier
operation: "analysis" | "report"
profile: RealUseProfileV1
authorization: AuthorizationAttestationV1
options: RealUseOptionsV1
```

`RealUseProfileV1` contains exactly:

```text
calendar_type
birth_date
birth_time
birthplace
gender
focus_topic
```

`AuthorizationAttestationV1` contains:

```text
subject_relation: "self" | "authorized_other"
attested: bool
```

`RealUseOptionsV1` contains:

```text
report_format: "json" | "markdown" | "html" | null
include_profile_in_report: bool
```

Rules:

- `report_format` is null for `analysis`.
- `report_format` is required for `report`.
- `include_profile_in_report` defaults to false.
- `attested=false` is schema-valid and produces `authorization_required`
  before calculation.
- Any `subject_relation` value outside the two allowed literals is an
  `invalid_request` schema error and never reaches the authorization service.
- Unknown fields are rejected at every object level.
- External charts and precomputed bundles are rejected.

### 6.2 Response V1

`RealUseResponseV1` contains:

```text
schema_version: "real-use-response-v1"
trace_id: random UUID4 string
operation: "analysis" | "report" | null
status: "ok" | "refused" | "error"
result: explicit result DTO or null
safety: ApplicationSafetyV1
provenance: ApplicationProvenanceV1 or null
warnings: immutable sequence of ApplicationWarningV1
privacy: ApplicationPrivacyV1
error: ApplicationErrorV1 or null
```

The response does not echo birth date, birth time, birthplace, gender, or
focus topic in metadata. A rendered report may contain those values only when
`include_profile_in_report=true`; the response then marks the content
`contains_sensitive_profile=true`.

`operation` is null for every strict parsing failure. The parser never peeks at
or partially trusts an otherwise invalid object. Every typed
`handle_real_use()` response and every successfully parsed JSON response
carries the request operation.

The nested DTOs have exact V1 fields:

```text
ApplicationErrorV1: code, message, field_path, retryable, trace_id
ApplicationSafetyV1: allowed, decision, categories, redirect_message, requires_narrowing
ApplicationProvenanceV1: engine_version, ruleset_version, provider_version,
  chart_source_type, chart_source_confidence, evidence_baseline_id, evidence_ids
ApplicationWarningV1: code, message
ApplicationPrivacyV1: retention, contains_sensitive_profile
ApplicationContentV1: media_type, content, contains_sensitive_profile
ApplicationAnalysisResultV1: chart, calculation
ApplicationReportResultV1: report, content
```

All sequences are tuples, all maps are explicit public dictionaries, and all
DTOs are frozen. `result` is exactly one of `ApplicationAnalysisResultV1`,
`ApplicationReportResultV1`, or null according to operation and status.

### 6.3 Public Operations

```python
def handle_real_use(request: RealUseRequestV1) -> RealUseResponseV1:
    """Execute one validated request in one process and return a typed envelope."""

def handle_real_use_json(payload: bytes) -> bytes:
    """Parse, execute, serialize, and size-check one strict JSON request."""

def response_status_from_json_bytes(payload: bytes) -> ResponseStatus:
    """Read only the status from an internally generated response envelope."""
```

`handle_real_use_json` creates the trace ID before parsing, converts parser,
authorization, safety, calculation, knowledge, and unexpected failures into the
stable response envelope, and never leaks exception text. It enforces the
response limit after serialization; if normal serialization is too large, it
returns a small `response_too_large` envelope. The root package exports all
three operations and the request/response DTOs. Existing low-level functions
remain available.

## 7. Input And Output Limits

The strict JSON boundary enforces:

- maximum request size: 32 KiB;
- maximum JSON nesting depth: 8;
- maximum response size: 1 MiB;
- duplicate JSON keys rejected;
- non-finite numbers rejected;
- unknown fields rejected;
- `request_id`: 1 to 64 ASCII letters, digits, `_`, or `-`;
- `focus_topic`: at most 500 Unicode code points;
- `birthplace`: at most 160 Unicode code points;
- all other free text: at most 500 Unicode code points;
- provider-supported dates: 1901-01-01 through 2099-12-31;
- exactly Gregorian input under the documented UTC+08 wall-time assumption;
- true solar time is not applied.

File and stdin adapters read at most 32 KiB plus one sentinel byte. If the
sentinel byte exists they stop reading and return `payload_too_large`; they do
not buffer the remainder before rejection.

Unicode is normalized with NFKC for validation and safety classification. The
engine must not include raw invalid values in errors.

## 8. Authorization And Safety Flow

The order is mandatory:

1. Enforce byte, JSON, schema, and field limits.
2. Require `attested=true` and an allowed subject relationship.
3. Run focus-topic and high-risk safety checks.
4. Refuse without invoking chart calculation when authorization or safety
   fails.
5. Calculate chart and analysis in the same process.
6. Build the report with the original bound bundle when requested.
7. Run post-build safety review.
8. Serialize an explicit response DTO and enforce the output-size limit.

Lexical third-party detection remains defense in depth. It is not a substitute
for structural authorization.

## 9. Error Contract

`ApplicationErrorV1` uses these stable codes:

```text
invalid_json
invalid_request
authorization_required
unsafe_request
unsupported_input
payload_too_large
response_too_large
calculation_failed
knowledge_unavailable
internal_error
```

Each error contains only:

```text
code
message
field_path
retryable
trace_id
```

Errors never include request values, exception text, file paths, report bodies,
or Python representations.

## 10. Privacy And Retention

The accurate privacy statement is:

> Birth-profile and report data are not stored by the engine.

The engine cannot promise that a terminal, caller, shell redirection, or host
operating system will not retain output.

Rules:

- no request or response logging;
- no stable hash of birth data;
- no application-managed files, database rows, caches, or sessions;
- random per-request trace IDs;
- diagnostics, when explicitly enabled for tests, may contain only operation,
  status, duration bucket, payload-size bucket, safety categories, and version
  identifiers;
- weak process-local calculation provenance remains unchanged;
- application responses cannot be passed back as trusted calculation input.

## 11. Public Serialization

Application serializers are explicit and versioned. They do not use generic
`dataclasses.asdict()` over public response objects.

Analysis output includes:

- chart source and pillars without the raw birth profile;
- the complete public `CalculationBundle` result fields;
- filtered public assumptions;
- computation states, confidence, signals, rule IDs, and school views.

Report JSON includes the stable report fields, evidence audit, formal traces,
safety result, and knowledge activation summary. Markdown and HTML are returned
as typed content objects with a media type and sensitive-content flag.

Existing CLI serializers remain compatibility surfaces. The new facade has an
independent `schema_version` so engine or ruleset versions are not misused as
wire-schema versions.

When `include_profile_in_report=false`, redaction applies to the complete report
object before any JSON, Markdown, or HTML renderer runs. Every raw and NFKC
normalized occurrence of all six profile fields (`calendar_type`, `birth_date`,
`birth_time`, `birthplace`, `gender`, and `focus_topic`) is removed from every
report field, nested value, metadata value, and rendered output. Redaction is
not limited to the chart card. Tests use unique sentinels for each field and
scan the complete serialized result.

## 12. Markdown And HTML Safety

The real-use facade must escape untrusted profile values in both Markdown and
HTML paths, including legacy/non-analysis report content.

Trusted report headings and static explanatory text remain formatted. User
values are escaped before insertion, covering ATX and Setext headings, raw
HTML, links, images, tables, blockquotes, emphasis, code spans, and fences.

Security hardening may change output only for values containing active markup.
Ordinary legacy output remains byte compatible.

## 13. Calibration Data Model

### 13.1 CalibrationCase

```text
case_id
case_version
input_fixture_file
input_fixture_id
input_sha256
source_fixture_file
source_fixture_id
source_fixture_sha256
stratum: calendrical | structural | school
coverage_tags
claim_scope
contains_real_personal_data
```

### 13.2 CalibrationAssertion

```text
assertion_id
case_id
rule_family
school_id or null
assertion_kind: positive | counterexample | boundary | abstention | disagreement
field_path
acceptable_statuses
acceptable_values
required_rule_ids
required_evidence_ids
limitations
```

### 13.3 Review Records

The exact review and execution records are:

```text
CalibrationFileEnvelopeV1: schema_version, suite_version, generated_from,
  contains_real_personal_data, payload_sha256, records
CalibrationInputFixture: fixture_id, schema_version, request_payload,
  expected_boundary, source_fixture_file, source_fixture_id,
  source_fixture_sha256
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
  expected_statuses, acceptable_values, confidence, rationale,
  evidence_ids, source_locators, packet_sha256
AdjudicationDecision: adjudication_id, assertion_id, reviewer_a_review_id,
  reviewer_b_review_id, agreement_state, decision, final_statuses,
  final_acceptable_values, retained_alternatives, rationale, evidence_ids,
  safety_critical
CalibrationAssertionResult: assertion_id, actual_status, actual_values,
  actual_rule_ids, actual_evidence_ids, matched, failure_codes
CalibrationRun: run_id, engine_version, ruleset_version,
  school_profile_version, evidence_baseline_id, fixture_version,
  corpus_sha256, assertion_results
MetricSnapshotV1: snapshot_id, schema_version, corpus_sha256, version_set, assertion_count,
  determinism_rate, pillar_agreement_rate, trace_completeness_rate,
  unsupported_computed_count, dependency_bypass_count,
  school_disagreement_recall, silent_school_collapse_count,
  mandatory_abstention_rate, reviewer_raw_agreement,
  reviewer_stratum_agreement, weighted_kappa, jaccard_agreement,
  adjudicated_engine_match, safety_critical_exact_match,
  coverage, baseline_deltas
CalibrationReleaseDecision: schema_version, release_status, checks, metrics,
  blockers, claim_boundary, version_set, next_action
```

Every calibration JSON file uses `CalibrationFileEnvelopeV1`.
`payload_sha256` is SHA-256 over UTF-8 canonical JSON of `records` alone
(`sort_keys=true`, separators `,` and `:`, no NaN); `generated_from` is a
canonically sorted tuple of upstream SHA-256 values. `records` is sorted by its
primary ID. Reviewer labels are exactly `accept`, `revise`, `reject`, or
`abstain`.

Primary IDs are `fixture_id`, `case_id`, `assertion_id`, `citation_id`,
`packet_id`, `assignment_id`, `review_id`, `adjudication_id`, `run_id`, and
`snapshot_id` for their corresponding record types. A release decision is a
single-record envelope keyed by the constant schema version
`domain-calibration-release-v1`. `label=abstain` is the only abstention source
of truth and requires empty `expected_statuses` and `acceptable_values`; every
other label requires at least one expected status.

The blinded projection is a value embedded inside each packet, not a lookup.
Its synthetic facts contain only the packaged, non-personal case facts needed
to assess the candidate claim and never engine output. One packet's canonical
bytes are canonical JSON of the `ReviewerPacket` value alone. Its exact access
manifest is the tuple `provided_packet_bytes_only`, `tools_disabled`,
`filesystem_disabled`, `peer_labels_absent`, `engine_output_absent`.

`reviewer_kind` is exactly `agent_independent`. Legitimate school differences
remain acceptable alternatives or `disputed`; adjudication cannot silently
select a universal winner.

All files have a suite version, canonical ordering, exact-key validation,
privacy declaration, and SHA-256 integrity fields.

The installed calibration input closure is
`data/domain_calibration/input_fixtures.json`. It contains only the minimal
synthetic input records needed by the frozen cases, including the explicit
`safety_high_risk_lifespan_refusal_001` record. Each case executes this packaged
file and separately records the original `tests/fixtures/` or safety-test
source locator and hash as lineage. Runtime never reads `tests/` or the source
checkout.

## 14. Calibration Workflow

1. Curator selects and freezes cases before reviewers see engine output.
2. Existing tracked evidence and source locators are bundled by assertion.
3. The controller creates a canonical allowlisted packet containing only the
   assertion, exact evidence excerpts, locators, rule scope, limitations, and
   packet manifest. The packet excludes engine output, expected fixtures,
   peer labels, source-checkout paths, and unrelated corpus records.
4. Reviewer A and reviewer B run in fresh `fork_context=false` agent contexts.
   Each receives only the packet bytes and an instruction forbidding tools and
   filesystem reads. The controller records packet SHA-256 and the declared
   access manifest, then writes the returned structured review.
5. Review files are frozen and hashed.
6. Adjudicator compares labels and evidence. It resolves clerical/evidence
   errors and retains legitimate school disagreements.
7. Adjudicated expectations are frozen before the engine run.
8. Calibration runner executes the exact engine, ruleset, school profiles,
   evidence baseline, and fixture versions.
9. Metric snapshot and release decision are generated read-only.

If only one valid review exists, the assertion is `self_reviewed` and cannot
count toward the independent-calibration release label.

## 15. Minimum Calibration Coverage

The V1 release corpus requires:

- at least 42 adjudicated assertions;
- every one of the 10 active rule families covered by positive,
  counterexample, and boundary/abstention behavior where applicable;
- each enabled school covered by agreement, disagreement, counterexample, and
  `not_computed`/abstention behavior;
- calendrical cases linked to existing cross-provider pillar artifacts;
- explicit cases for dependency degradation, empty branch relations, severe
  conflict, unknown gender, aware datetime rejection, and high-risk refusal;
- no real personal data.

## 16. Metrics

`MetricSnapshotV1` reports:

- determinism rate;
- chart-pillar cross-provider agreement;
- exact status agreement;
- exact/acceptable-set conclusion agreement;
- evidence-ID trace completeness;
- rule-ID trace completeness;
- unsupported-computed count;
- dependency-bypass count;
- appropriate-abstention rate;
- school-disagreement recall;
- silent-disagreement-collapse count;
- reviewer raw agreement;
- weighted kappa for categorical strata with at least 10 observations;
- Jaccard agreement for multi-label candidates;
- coverage by family, school, status, assertion kind, and evidence source;
- baseline deltas by engine, ruleset, school-profile, fixture, and evidence
  versions.

These are conformance metrics, not predictive-accuracy metrics.

Raw agreement counts exact equality across all four reviewer labels. Weighted
kappa uses only paired non-abstention labels ordered `reject=0`, `revise=1`,
`accept=2`, with linear weight `1 - abs(i-j)/2`; it is null below 10 eligible
pairs. The singular `weighted_kappa` field is the global value; when expected
disagreement is zero it is 1.0. Jaccard compares acceptable-value sets and
defines two empty sets as 1.0.

`reviewer_stratum_agreement` is an exact map with only `calendrical`,
`structural`, and `school` keys. Each denominator contains assertions in that
case stratum with exactly two valid independent reviews and includes
abstentions. The 0.60 release threshold applies only when that denominator is
at least 10. Family, school ID, status, assertion-kind, and evidence-source
coverage maps are informational coverage outputs and do not create additional
per-stratum agreement gates.

## 17. Release Gates

All of the following are mandatory:

- determinism: 100%;
- existing cross-provider pillar agreement: 100%;
- evidence and rule trace completeness: 100%;
- unsupported-computed and dependency-bypass counts: 0;
- silent school-disagreement collapse: 0;
- school-disagreement recall: 100%;
- mandatory abstention/refusal cases: 100%;
- adjudication coverage: 100%;
- valid independent reviews per counted assertion: 2;
- reviewer raw agreement: at least 0.70 overall;
- no sufficiently sampled stratum below 0.60 raw agreement;
- adjudicated engine acceptable-set match: at least 0.90 overall;
- every safety-critical assertion matches exactly;
- application contract, privacy, packaging, and no-retention tests pass;
- documentation repeats the claim boundary and exact version set.

Failure blocks the 019 application/calibration release label. It does not
rewrite the historical 018 operational result.

## 18. Packaging

The current wheel omits required JSON assets. Feature 019 adds explicit
setuptools package-data configuration for every runtime JSON file.

The release test must:

1. build a wheel without network access;
2. inspect the wheel manifest for required data assets;
3. install the wheel into a temporary target;
4. run chart analysis, evidence-backed report generation, calibration summary,
   and the real-use CLI from the installed distribution;
5. verify no dependency on the source checkout.

The installed calibration-summary child receives an explicit local
`PackagingVerification` built from its installed resources. This dependency
injection prevents the child's release summary from recursively building and
launching another wheel. The outer release gate alone owns wheel construction;
the child verifies only its own distribution assets and source isolation.

The package version advances from `0.1.0` to `0.2.0` when the V1 application
contract is released.

## 19. CLI

Add one command:

```text
mingli-engine real-use --input <path-or->
```

It accepts one strict request and emits exactly one JSON response envelope to
stdout. Controlled refusals and application errors are represented in that
envelope. Exit codes are:

```text
0 ok
3 refused
1 invalid request or controlled application error
```

Existing commands retain their current interfaces.

## 20. Testing Strategy

All implementation work follows red-green-refactor TDD.

Required suites include:

- exact request and response DTO field contracts;
- duplicate keys, unknown fields, depth, byte, Unicode, date, and output limits;
- authorization before safety and calculation;
- refusal paths proving calculator, analyzer, report builder, and renderer were
  not called;
- no raw input in errors, trace metadata, diagnostics, or stderr;
- hostile Markdown and HTML in analysis and non-analysis paths;
- same-process provenance and cross-request/copy rejection;
- weak provenance lifecycle cleanup;
- no engine-managed writes on success, refusal, validation failure, and
  internal exception;
- deterministic public serialization excluding private configuration;
- calibration schema, blindness, independence, integrity, coverage, metrics,
  baseline deltas, and failure gates;
- three-school agreement/disagreement/abstention behavior;
- wheel manifest and installed-distribution smoke tests;
- all existing 018 calculation, report, acceptance, release, and completion
  tests.

## 21. Feature Governance

Feature 019 gets a complete Spec Kit package before implementation. While tasks
remain open it lives below `specs/_drafts/` so the frozen completed baseline is
not misreported. Final closure moves it atomically to:

```text
specs/019-bazi-domain-validation-and-application-v1/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- tasks.md
|-- contracts/
`-- checklists/
```

The documentation distinguishes:

- operational release readiness;
- agent-independent traditional-method conformance calibration;
- scientific or predictive validation, which remains out of scope.

## 22. Success Criteria

Feature 019 is complete only when:

1. The public application facade and `real-use` CLI satisfy their frozen V1
   contracts.
2. All authorization, input-bound, safety, privacy, and no-retention gates pass.
3. The independent agent calibration corpus meets minimum coverage and release
   metrics.
4. Every disagreement is adjudicated or intentionally retained.
5. The built and installed wheel runs without source-checkout data.
6. Existing engine/report interfaces remain compatible except documented
   security hardening.
7. Application and calibration release summaries are enabled with guardrails
   or stricter.
8. The complete repository test suite and final read-only release commands
   pass from a clean worktree.
