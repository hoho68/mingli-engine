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
|-- application.py
|-- application_models.py
|-- application_inputs.py
|-- application_serialization.py
|-- domain_calibration.py
|-- domain_calibration_models.py
|-- domain_calibration_release.py
`-- data/domain_calibration/
    |-- calibration_cases.json
    |-- calibration_assertions.json
    |-- review_assignments.json
    |-- reviewer_a_reviews.json
    |-- reviewer_b_reviews.json
    |-- adjudications.json
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
attested: true
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
- Unknown fields are rejected at every object level.
- External charts and precomputed bundles are rejected.

### 6.2 Response V1

`RealUseResponseV1` contains:

```text
schema_version: "real-use-response-v1"
trace_id: random UUID4 string
operation: "analysis" | "report"
status: "ok" | "refused" | "error"
result: explicit result DTO or null
safety: ApplicationSafetyV1
provenance: ApplicationProvenanceV1 or null
warnings: tuple[ApplicationWarningV1, ...]
privacy: ApplicationPrivacyV1
error: ApplicationErrorV1 or null
```

The response does not echo birth date, birth time, birthplace, gender, or
focus topic in metadata. A rendered report may contain those values only when
`include_profile_in_report=true`; the response then marks the content
`contains_sensitive_profile=true`.

### 6.3 Public Operations

```python
def handle_real_use(request: RealUseRequestV1) -> RealUseResponseV1:
    ...

def handle_real_use_json(payload: bytes) -> bytes:
    ...
```

The root package exports these two operations and the request/response DTOs.
Existing low-level functions remain available.

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
input_fixture_id
input_sha256
stratum: calendrical | structural | school
coverage_tags
claim_scope
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

`ReviewAssignment` records reviewer role, `reviewer_kind=agent_independent`,
independence declaration, peer-label blindness, and engine-output blindness.

`CalibrationReview` records assertion label, rationale, confidence,
abstention, evidence IDs, and source locators.

`AdjudicationDecision` records agreement, clerical correction, retained
alternative, or unresolved disagreement. Legitimate school differences remain
acceptable alternatives or `disputed`; adjudication cannot silently select a
universal winner.

All files have a suite version, canonical ordering, exact-key validation,
privacy declaration, and SHA-256 integrity fields.

## 14. Calibration Workflow

1. Curator selects and freezes cases before reviewers see engine output.
2. Existing tracked evidence and source locators are bundled by assertion.
3. Reviewer A and reviewer B independently label assertions without seeing
   each other or current engine output.
4. Review files are frozen and hashed.
5. Adjudicator compares labels and evidence. It resolves clerical/evidence
   errors and retains legitimate school disagreements.
6. Adjudicated expectations are frozen before the engine run.
7. Calibration runner executes the exact engine, ruleset, school profiles,
   evidence baseline, and fixture versions.
8. Metric snapshot and release decision are generated read-only.

If only one valid review exists, the assertion is `self_reviewed` and cannot
count toward the independent-calibration release label.

## 15. Minimum Calibration Coverage

The V1 release corpus requires:

- at least 40 adjudicated assertions;
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

Feature 019 gets a complete Spec Kit directory so project-completion counts no
longer stop at 017:

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

