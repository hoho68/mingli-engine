# Feature Specification: Bazi Domain Validation And Application V1

**Feature Branch**: `codex/019-bazi-domain-validation-application`

**Created**: 2026-07-13

**Status**: In Progress

**Input**: Deliver a versioned, privacy-bounded Python and CLI application contract over the deterministic Bazi engine, plus an independently agent-reviewed traditional-method conformance calibration workflow.

## Claim Boundary

The strongest permitted claim is independent agent-based domain-conformance calibration of deterministic structural outputs against tracked traditional-method evidence and blinded reviewer labels. This feature does not establish scientific validity, causal or predictive accuracy, real-world outcome accuracy, human expert review, universal agreement between traditional schools, geographic timezone support, or true-solar-time support. Reviewers are always identified as `agent_independent`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run An Authorized Real-Use Analysis (Priority: P1)

A caller submits a bounded Gregorian birth profile for self-use or an authorized other and receives deterministic chart and analysis data through a stable V1 response envelope.

**Why this priority**: A supported application boundary is the minimum usable surface for the existing engine.

**Independent Test**: Submit a valid analysis request and verify the exact response schema, same-process provenance, filtered assumptions, absence of raw profile metadata, and no engine-managed retention.

**Acceptance Scenarios**:

1. **Given** a valid self-use request with attestation, **When** analysis is requested, **Then** the response is `ok`, contains chart and complete public calculation output, carries actual version provenance, and stores no birth-profile or response data.
2. **Given** a schema-valid request with `attested=false`, **When** it is handled, **Then** the response is `refused` with `authorization_required` before chart calculation or analysis is invoked.
3. **Given** malformed, oversized, duplicate-key, unsupported, or unknown-field input, **When** it is parsed, **Then** a stable error envelope is returned without raw invalid values or exception details.

---

### User Story 2 - Generate A Privacy-Bounded Report (Priority: P1)

An authorized caller requests JSON, Markdown, or HTML report content and chooses explicitly whether the six profile fields may appear in the rendered report.

**Why this priority**: Report generation is the user-facing output of the engine and carries the largest privacy and markup-injection risk.

**Independent Test**: Generate all three report formats with profile inclusion disabled and enabled, scanning every nested field and rendered byte for raw and normalized sentinels and active markup.

**Acceptance Scenarios**:

1. **Given** `include_profile_in_report=false`, **When** any report format is generated, **Then** all raw and NFKC-normalized occurrences of calendar type, birth date, birth time, birthplace, gender, and focus topic are absent from the complete report object and output.
2. **Given** profile inclusion is enabled, **When** untrusted values contain Markdown or HTML syntax, **Then** the values are escaped, the content is marked sensitive, and trusted headings retain formatting.
3. **Given** post-build safety review refuses the report, **When** the facade handles the result, **Then** no renderer is called and a controlled refusal envelope is returned.
4. **Given** an allowed evidence-backed report, **When** JSON, Markdown, or HTML is rendered, **Then** each format preserves source and evidence traceability, includes the required traditional-analysis disclaimer, uses non-absolute uncertainty language, and rejects prohibited absolute destiny wording.

---

### User Story 3 - Use The Installed CLI Contract (Priority: P2)

A controlled local caller provides one request by file or stdin and receives exactly one JSON response from the installed distribution.

**Why this priority**: The CLI proves the application contract is usable without importing repository internals.

**Independent Test**: Build and install the wheel outside the checkout, invoke `mingli-engine real-use --input REQUEST_PATH_OR_STDIN`, and verify output, exit codes, resource loading, and source isolation.

**Acceptance Scenarios**:

1. **Given** a valid installed request, **When** the command runs, **Then** stdout contains exactly one V1 response and exit code is 0.
2. **Given** a controlled refusal, **When** the command runs, **Then** stdout contains the refusal envelope, stderr is empty, and exit code is 3.
3. **Given** invalid input or a controlled application error, **When** the command runs, **Then** stdout contains one error envelope and exit code is 1.

---

### User Story 4 - Review Traditional-Method Conformance Independently (Priority: P2)

Maintainers freeze synthetic calibration cases and allowlisted evidence packets before two independent agents review each assertion, followed by separate adjudication.

**Why this priority**: Domain-conformance claims require evidence-backed labels that are independent of current engine output.

**Independent Test**: Validate canonical packets, two distinct assignments and reviews per counted assertion, exact access manifests, frozen hashes, adjudication coverage, and absence of engine output or peer labels from reviewer packets.

**Acceptance Scenarios**:

1. **Given** a frozen assertion packet, **When** Reviewer A and Reviewer B assess it in separate fresh contexts, **Then** each receives only canonical packet bytes with tools and filesystem disabled and records `reviewer_kind=agent_independent`.
2. **Given** reviewers disagree on a legitimate school interpretation, **When** adjudication occurs, **Then** alternatives remain explicit or disputed rather than selecting a universal school winner.
3. **Given** fewer than two valid independent reviews, **When** metrics are computed, **Then** the assertion is marked `self_reviewed` and excluded from the independent-calibration release label.

---

### User Story 5 - Decide Release Readiness From Reproducible Gates (Priority: P3)

A maintainer runs deterministic application, privacy, packaging, calibration, and compatibility gates and receives a version-bound release decision.

**Why this priority**: The application and calibration label must be reproducible and must not weaken the completed 018 result.

**Independent Test**: Recompute the metric snapshot and release decision from frozen inputs and verify every threshold, version, blocker, and claim-boundary field.

**Acceptance Scenarios**:

1. **Given** all mandatory gates pass, **When** the release summary is computed, **Then** status is `ready_with_guardrails` or stricter and identifies the exact application, engine, ruleset, provider, school-profile, fixture, evidence, and corpus versions.
2. **Given** any safety-critical mismatch, privacy failure, packaging failure, or missing independent review, **When** release status is computed, **Then** 019 is blocked without rewriting the historical 018 operational result.
3. **Given** the built wheel, **When** installed smoke tests run outside the checkout, **Then** all required JSON assets load and no runtime operation reads `tests/` or repository-only paths.

### Edge Cases

- Requests over 32 KiB are rejected after reading at most one sentinel byte beyond the limit.
- JSON deeper than 8 levels, duplicate keys, invalid UTF-8, non-finite numbers, and unknown fields are rejected.
- The `request_id` key is required and its value is either null or 1 to 64 ASCII letters, digits, `_`, or `-`.
- The `include_profile_in_report` key is required and its value is a boolean.
- Every request object and nested object contains exactly its specified required keys; omission and unknown keys are invalid.
- Dates outside 1901-01-01 through 2099-12-31, aware datetimes, non-Gregorian input, external charts, and serialized calculation bundles are rejected.
- Focus topics covering lifespan or death, medical, legal, psychological, investment, coercive matching, anxiety creation, or remedy upsells are refused before calculation.
- Response serialization over 1 MiB becomes a small `response_too_large` envelope.
- Weak process-local provenance rejects cross-request reuse, copies, and serialized reconstruction and releases entries after garbage collection.
- Calibration includes dependency degradation, empty branch relations, severe conflict, unknown gender, aware datetime rejection, high-risk refusal, and three-school disagreement and abstention.
- No calibration case contains real personal data.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST expose frozen `RealUseRequestV1` and `RealUseResponseV1` DTOs with schema versions `real-use-request-v1` and `real-use-response-v1`.
- **FR-002**: The root package MUST expose `handle_real_use`, `handle_real_use_json`, and `response_status_from_json_bytes` while preserving existing low-level interfaces.
- **FR-003**: The strict parser MUST require every exact root and nested object field, reject unknown fields, require `request_id` with a null or valid identifier value, require boolean `include_profile_in_report`, and reject invalid UTF-8, duplicate keys, non-finite values, excessive depth, invalid literals, invalid identifiers, unsupported dates, external charts, and precomputed bundles.
- **FR-004**: The JSON boundary MUST enforce a 32 KiB request limit, nesting depth 8, text limits, Gregorian dates from 1901-01-01 through 2099-12-31, UTC+08 wall-time assumptions, and no true solar time.
- **FR-005**: Authorization MUST require `attested=true` and `subject_relation` of `self` or `authorized_other` before safety classification or calculation.
- **FR-006**: Safety checks MUST run before chart calculation and MUST refuse prohibited high-risk or professional-advice requests without invoking downstream calculation or rendering.
- **FR-007**: Analysis and report generation MUST use the original chart and calculation bundle in one process and one request with actual provenance versions.
- **FR-008**: Public serializers MUST construct explicit versioned mappings, use deterministic UTF-8 JSON, reject non-finite values, and exclude private configuration.
- **FR-009**: The response MUST enforce a 1 MiB maximum and replace oversized normal output with a bounded `response_too_large` envelope.
- **FR-010**: Report redaction MUST cover the complete explicit report object before JSON, Markdown, or HTML rendering when profile inclusion is disabled.
- **FR-011**: Markdown and HTML paths MUST escape active markup in all untrusted profile values while preserving ordinary legacy output.
- **FR-012**: The CLI MUST accept exactly one bounded request from a path or stdin, emit exactly one response envelope, and use exit codes 0 for `ok`, 3 for `refused`, and 1 for `error`.
- **FR-013**: The wheel MUST package every runtime JSON asset and installed tests MUST run chart analysis, evidence-backed reports, calibration summary, and real-use outside the source checkout.
- **FR-014**: Every calibration JSON file MUST use a strict `CalibrationFileEnvelopeV1` with canonical ordering, canonical record SHA-256, sorted upstream hashes, exact keys, suite version, and privacy declaration.
- **FR-015**: The V1 corpus MUST contain at least 42 adjudicated assertions and cover the active rule family IDs `pattern_strength`, `five_element_balance`, `useful_god_candidate`, `taboo_god_candidate`, `ten_god_relation`, `branch_interaction`, `blind_image_method`, `luck_cycle`, `remedy_boundary`, and `high_risk_signal`, plus school IDs `ziping`, `liang_xiangrun`, and `duan`, across required positive, counterexample, boundary, disagreement, and abstention behavior. `get_formal_interpretation_rule_families()` and `src/mingli_engine/data/calculation/school_profiles.json` `enabled` are the respective sole authorities; calibration MUST NOT define a second independent allowlist.
- **FR-016**: Reviewer packets MUST embed a blinded assertion projection, allowlisted evidence and locators, limitations, and the exact access manifest while excluding engine output, peer labels, checkout paths, and unrelated records.
- **FR-017**: Every counted assertion MUST have two valid reviews from distinct `agent_independent` reviewers and a separate adjudication decision frozen before engine execution.
- **FR-018**: Adjudication MUST retain legitimate school alternatives or unresolved disagreement and MUST NOT collapse school-dependent claims into a universal winner.
- **FR-019**: Calibration metrics MUST separately report `evidence_trace_completeness_rate`, `rule_trace_completeness_rate`, and `adjudication_coverage_rate`, plus determinism, pillar agreement, unsupported computation, dependency bypass, abstention, school disagreement, reviewer agreement, weighted kappa, Jaccard agreement, coverage, engine match, safety-critical match, and version deltas.
- **FR-020**: Release decisions MUST bind an `ExactVersionSet` containing exactly `application_version`, `engine_version`, `ruleset_version`, `provider_version`, `school_profile_version`, `fixture_version`, `evidence_baseline_id`, and `corpus_sha256`; the run, baseline snapshot, and release decision version sets MUST be exactly equal, and any mismatch or failed application, privacy, packaging, calibration, review, documentation, or compatibility gate MUST block 019.
- **FR-021**: The application package version MUST advance to `0.2.0` only after all non-version release gates pass and fresh installed-wheel verification is recomputed.
- **FR-022**: Feature governance MUST remain in the explicit draft path while tasks are open and move atomically to the formal 019 path only during final closure.
- **FR-023**: JSON, Markdown, and HTML report acceptance MUST each prove source and evidence traceability, required disclaimer presence, non-absolute uncertainty language, and rejection of prohibited absolute destiny wording before release.

### Safety, Ethics, And Privacy Requirements

- **SE-001**: Runtime and documentation MUST describe outputs as traditional evidence analysis and MUST NOT claim scientific proof, prediction, causation, guaranteed outcomes, or human expert validation.
- **SE-002**: Reviewer records and documentation MUST use `reviewer_kind=agent_independent` and describe blindness as procedural rather than OS-level isolation.
- **SE-003**: The system MUST refuse guaranteed death timing, exact lifespan, medical diagnosis or treatment, legal instruction, psychological treatment, investment instruction, coercive matching, anxiety creation, and paid-remedy upsells.
- **SE-004**: Errors, diagnostics, logs, stderr, trace metadata, and release artifacts MUST NOT contain raw or normalized profile values, exception text, file paths, or report bodies.
- **SE-005**: Birth-profile and report data MUST NOT be stored by the engine; documentation MUST state that callers, terminals, shell redirection, and host systems may retain output.
- **SE-006**: The engine MUST create no request logs, response logs, stable birth-data hashes, application-managed files, database rows, caches, or sessions.
- **SE-007**: Reports MUST preserve user agency, uncertainty, school dependency, evidence limitations, and qualified-professional boundaries.
- **SE-008**: Calibration MUST use tracked synthetic inputs and formal evidence only and MUST contain no real personal data or new raw source extraction.

### Key Entities

- **RealUseRequestV1**: Strict versioned request containing operation, bounded profile, authorization attestation, and output options.
- **RealUseResponseV1**: Stable envelope containing status, result, safety, provenance, warnings, privacy, and error data.
- **ApplicationVerification**: Read-only deterministic application contract and privacy check map over fixed synthetic scenarios.
- **PackagingVerification**: Deterministic installed-resource hash, distribution-version, and source-isolation result.
- **CalibrationCase**: Synthetic execution case bound to packaged input and original source-fixture lineage.
- **CalibrationAssertion**: Rule-family and school-specific expected conformance claim.
- **ReviewerPacket**: Canonical allowlisted blinded packet supplied independently to reviewers.
- **CalibrationReview**: Structured agent-independent label with evidence, rationale, confidence, and packet hash.
- **AdjudicationDecision**: Frozen resolution that retains legitimate alternatives and safety-critical expectations.
- **CalibrationRun**: Exact-version execution result over the frozen corpus.
- **ExactVersionSet**: Frozen eight-field identity shared without difference by the calibration run, baseline metric snapshot, and release decision.
- **MetricSnapshotV1**: Reproducible conformance metrics and version deltas.
- **CalibrationReleaseDecision**: Versioned release status, checks, blockers, claim boundary, and next action.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Valid analysis and report requests produce exact V1 envelopes through both Python and installed CLI surfaces.
- **SC-002**: Authorization and unsafe requests invoke zero chart, analysis, report, and renderer calls.
- **SC-003**: Request limit, nesting, strict-schema, Unicode, date, response-size, and stable-error tests pass at 100%.
- **SC-004**: Whole-object redaction tests find zero raw or NFKC-normalized profile sentinels when inclusion is disabled.
- **SC-005**: No-retention tests observe zero engine-managed writes and zero profile leaks across success, refusal, validation failure, and internal exception scenarios.
- **SC-006**: The installed wheel contains every required JSON asset and all installed smoke operations run with zero dependency on the source checkout.
- **SC-007**: The frozen corpus contains at least 42 adjudicated assertions, covers every active rule family and school behavior required by FR-015, and contains zero real personal records.
- **SC-008**: Counted assertions have exactly two valid independent reviews and 100% adjudication coverage.
- **SC-009**: Determinism, cross-provider pillar agreement, `evidence_trace_completeness_rate`, `rule_trace_completeness_rate`, `adjudication_coverage_rate`, school-disagreement recall, and mandatory abstention or refusal rates are 100%.
- **SC-010**: Unsupported-computed count, dependency-bypass count, and silent school-disagreement collapse count are zero.
- **SC-011**: Overall reviewer raw agreement is at least 0.70 and no stratum with at least 10 paired reviews is below 0.60.
- **SC-012**: Adjudicated engine acceptable-set match is at least 0.90 and every safety-critical assertion matches exactly.
- **SC-013**: Existing 018 calculation, report, release, and project-completion tests remain green throughout draft implementation.
- **SC-014**: Final release summaries are `ready_with_guardrails` or stricter and repeat the exact version set and claim boundary.
- **SC-015**: JSON, Markdown, and HTML report tests each pass source trace, evidence trace, disclaimer, non-absolute language, and prohibited absolute-language rejection checks.

## Assumptions And Dependencies

- Feature 018 provides the deterministic calculation, analysis, report, provenance, evidence, and three-school foundations.
- Runtime dependencies remain Python 3.12+, standard library, and `lunar-python==1.4.8`; development verification pins pytest 8.4.1, mypy 1.17.1, and Ruff 0.12.11.
- Calibration uses only tracked formal evidence, existing synthetic charts, existing boundary fixtures, and packaged minimal synthetic inputs.
- HTTP, browser, desktop UI, remote services, accounts, databases, sessions, geographic timezone lookup, longitude, and true solar time remain outside this feature.
- Final governance closure and version advancement occur only after every earlier implementation and release task is verified.
