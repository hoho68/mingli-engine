# Bazi Domain Validation And Application V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` in this session, or `superpowers:executing-plans` in a separate session. Follow every red-green-refactor checkpoint and do not combine reviewer roles.

**Goal:** Deliver a versioned, privacy-bounded Python/CLI application contract and an independently agent-reviewed traditional-method conformance calibration system over the existing Bazi engine.

**Architecture:** Strict JSON becomes frozen request DTOs. One facade performs authorization, safety classification, chart calculation, analysis, report construction, post-build safety review, redaction, and explicit serialization in one process. A separate immutable calibration corpus is reviewed twice from allowlisted blinded packets, adjudicated before execution, measured against exact engine/evidence versions, and controlled by read-only release gates. HTTP, UI, remote services, and predictive/scientific claims remain out of scope.

**Tech Stack:** Python 3.12+, standard library, `lunar-python==1.4.8`, setuptools, pytest 8.4.1, mypy 1.17.1, Ruff 0.12.11.

**Governance baseline:** Task 0 creates the complete `specs/_drafts/019-bazi-domain-validation-and-application-v1/` Spec Kit directory before application implementation. The non-numbered draft parent keeps the frozen 001-017 completion baseline green while 019 tasks are open. Task 17 moves the closed package to formal `specs/019-bazi-domain-validation-and-application-v1/` and updates the completion baseline atomically.

## Long-Goal Checkpoints

1. `019-A`: packaged runtime assets and frozen application protocol.
2. `019-B`: controlled same-process facade, serializers, renderers, and CLI.
3. `019-C`: frozen cases, allowlisted blinded packets, two reviews, and adjudication.
4. `019-D`: metrics, release gates, installed-wheel proof, governance closure, and audit.

Keep goal `019-bazi-domain-validation-and-application-v1` active through all checkpoints. After each checkpoint, report the next checkpoint explicitly.

## Standard Verification Commands

Use these pinned commands in every task where applicable:

```powershell
uv run --with pytest==8.4.1 python -m pytest <targets> -q -p no:cacheprovider
uv run --with mypy==1.17.1 python -m mypy <targets> --follow-imports=skip
uv run --with ruff==0.12.11 ruff check <targets>
```

All final-suite shell calls use tool timeout `900000 ms`.

### Task 0: Establish Active Feature Governance Before Implementation

**Files:**
- Create: `specs/_drafts/019-bazi-domain-validation-and-application-v1/spec.md`
- Create: `specs/_drafts/019-bazi-domain-validation-and-application-v1/plan.md`
- Create: `specs/_drafts/019-bazi-domain-validation-and-application-v1/research.md`
- Create: `specs/_drafts/019-bazi-domain-validation-and-application-v1/data-model.md`
- Create: `specs/_drafts/019-bazi-domain-validation-and-application-v1/quickstart.md`
- Create: `specs/_drafts/019-bazi-domain-validation-and-application-v1/tasks.md`
- Create: `specs/_drafts/019-bazi-domain-validation-and-application-v1/contracts/real-use-v1-contract.md`
- Create: `specs/_drafts/019-bazi-domain-validation-and-application-v1/contracts/domain-calibration-v1-contract.md`
- Create: `specs/_drafts/019-bazi-domain-validation-and-application-v1/checklists/requirements.md`
- Modify: `.specify/feature.json`

- [ ] **Step 1: Pin the explicit draft feature path**

Set `SPECIFY_FEATURE_DIRECTORY=specs/_drafts/019-bazi-domain-validation-and-application-v1` and persist that exact path in `.specify/feature.json`. Do not allow sequential auto-numbering to choose 018.

- [ ] **Step 2: Create the complete in-progress Spec Kit**

Write all listed artifacts from the confirmed design and this plan. `tasks.md` uses unchecked TDD tasks, the requirement checklist is complete for specification quality, and `spec.md` status is `In Progress`. No `TBD`, `TODO`, ellipsis placeholder, or unresolved clarification is allowed. Run Spec Kit consistency analysis against the draft package.

- [ ] **Step 3: Prove the completed baseline remains unchanged**

Run `tests/unit/test_project_completion.py` and its CLI contract before any application code. Because `_drafts` does not match `^\d{3}-`, the existing feature IDs, counts, and historical 018 result must remain unchanged.

- [ ] **Step 4: Verify and commit**

Run project-completion unit/contract tests. Commit: `docs: establish 019 draft feature governance`.

### Task 1: Package And Verify Runtime Assets

**Files:**
- Modify: `pyproject.toml`
- Create: `src/mingli_engine/packaging_validation.py`
- Create: `tests/contract/test_wheel_runtime_assets.py`
- Create: `tests/integration/test_installed_package_baseline.py`

- [ ] **Step 1: Write all failing packaging tests first**

Require the wheel to contain every JSON below `mingli_engine/data/`, including `data/calculation/strength_weights.json`, `data/calculation/school_profiles.json`, and the actual file `data/classical_sources/evidence_units.json`. Require an installed-target subprocess, running outside the checkout with checkout `PYTHONPATH` removed, to load chart, analysis, and evidence-backed report data. Require `build_packaging_verification()` to return an exact deterministic map of asset path to SHA-256, distribution version, source-isolation status, and overall status.

- [ ] **Step 2: Confirm red**

```powershell
uv run --with pytest==8.4.1 python -m pytest tests/contract/test_wheel_runtime_assets.py tests/integration/test_installed_package_baseline.py -q -p no:cacheprovider
```

Expected: wheel data and verifier tests fail.

- [ ] **Step 3: Implement package data and verifier**

Add setuptools discovery from `src` and `mingli_engine = ["data/**/*.json"]`. Implement a read-only verifier using `importlib.resources`, `importlib.metadata`, and SHA-256. It must not rely on repository paths or write a report.

- [ ] **Step 4: Verify green, type, and lint**

Run the task tests, mypy on `packaging_validation.py`, and Ruff on all changed Python files.

- [ ] **Step 5: Commit**

Commit message: `fix: package and verify mingli runtime assets`.

### Task 2: Freeze The Exact Application DTO Protocol

**Files:**
- Create: `src/mingli_engine/application_models.py`
- Create: `tests/unit/test_application_models.py`

- [ ] **Step 1: Write exact-field, literal, tuple, and immutability tests**

Require frozen DTOs with these exact fields:

```text
RealUseProfileV1: calendar_type, birth_date, birth_time, birthplace, gender, focus_topic
AuthorizationAttestationV1: subject_relation, attested
RealUseOptionsV1: report_format, include_profile_in_report
RealUseRequestV1: schema_version, request_id, operation, profile, authorization, options
ApplicationErrorV1: code, message, field_path, retryable, trace_id
ApplicationSafetyV1: allowed, decision, categories, redirect_message, requires_narrowing
ApplicationProvenanceV1: engine_version, ruleset_version, provider_version, chart_source_type, chart_source_confidence, evidence_baseline_id, evidence_ids
ApplicationWarningV1: code, message
ApplicationPrivacyV1: retention, contains_sensitive_profile
ApplicationContentV1: media_type, content, contains_sensitive_profile
ApplicationAnalysisResultV1: chart, calculation
ApplicationReportResultV1: report, content
RealUseResponseV1: schema_version, trace_id, operation, status, result, safety, provenance, warnings, privacy, error
```

Test response invariants for `ok`, `refused`, and `error`, and operation/result compatibility. `RealUseRequestV1.operation` is always `analysis|report`; `RealUseResponseV1.operation` is null for every strict parsing failure and otherwise carries the parsed request operation.

- [ ] **Step 2: Confirm red, then implement constants and DTOs**

Use schema versions `real-use-request-v1` and `real-use-response-v1`; allowed operations `analysis|report`; statuses `ok|refused|error`; relations `self|authorized_other`; formats `json|markdown|html`. Normalize sequences to tuples in frozen instances.

- [ ] **Step 3: Verify and commit**

Run focused pytest, pinned mypy, and Ruff. Commit: `feat: define real-use application protocol`.

### Task 3: Build The Strict JSON Request Boundary

**Files:**
- Create: `src/mingli_engine/application_inputs.py`
- Create: `tests/unit/test_application_inputs.py`
- Create: `tests/fixtures/application/valid_analysis_request.json`
- Create: `tests/fixtures/application/valid_report_request.json`

- [ ] **Step 1: Write failing parser tests**

Cover valid requests and reject: over 32 KiB, invalid UTF-8, duplicate keys, non-finite values, depth above 8, unknown keys at every object level, invalid request ID, wrong schema, illegal `subject_relation`, operation/format mismatch, non-Gregorian input, external chart/precomputed bundle fields, text limits, and dates outside 1901-01-01 through 2099-12-31. Keep `attested=false` schema-valid. Assert errors contain stable code and field path but no raw invalid value.

- [ ] **Step 2: Implement strict parsing**

Use `object_pairs_hook` for duplicate detection, `parse_constant` for non-finite rejection, exact-key validators, NFKC validation copies, regex `[A-Za-z0-9_-]{1,64}`, and explicit DTO construction. Keep original accepted display values only in the request DTO.

- [ ] **Step 3: Verify and commit**

Run focused pytest, mypy, and Ruff. Commit: `feat: enforce strict real-use input boundary`.

### Task 4: Publish Explicit Versioned Serializers

**Files:**
- Create: `src/mingli_engine/application_serialization.py`
- Modify: `src/mingli_engine/cli.py`
- Create: `tests/unit/test_application_serialization.py`

- [ ] **Step 1: Write failing exact-key and size tests**

Require explicit serializer functions for chart, calculation, report, every nested application DTO, and response. Reject private dataclass/configuration fields. Require deterministic UTF-8 JSON with sorted keys and no NaN. Write the response-over-1-MiB test before implementation. Require `response_status_from_json_bytes()` to accept only internally valid envelopes.

- [ ] **Step 2: Implement serializers without generic public `asdict()`**

Construct every mapping with the exact key lists from Task 2. Set `MAX_RESPONSE_BYTES = 1024 * 1024`; normal serialization raises an internal `ResponseSizeError` before bytes escape.

- [ ] **Step 3: Move compatible CLI serialization through public helpers**

Preserve existing command output byte compatibility except documented security hardening.

- [ ] **Step 4: Verify and commit**

Run application serialization and existing CLI contract tests, mypy, and Ruff. Commit: `refactor: publish versioned application serializers`.

### Task 5: Enforce Authorization And Pre-Calculation Safety

**Files:**
- Create: `src/mingli_engine/application_service.py`
- Create: `tests/unit/test_application_service.py`
- Create: `tests/safety/test_real_use_safety.py`

- [ ] **Step 1: Write failing call-order and refusal tests**

Prove byte/schema validation precedes authorization; structural authorization precedes lexical safety; and failed authorization or unsafe focus prevents chart provider, analyzer, report builder, and renderer calls. Cover schema-valid `attested=false`, lifespan/death focus (`寿命`), medical, legal, psychological, investment, coercive matching, anxiety creation, and remedy upsell categories. Illegal relations remain Task 3 `invalid_request` cases and never reach this service.

- [ ] **Step 2: Implement controlled pre-calculation decisions**

Map failures to `authorization_required` or `unsafe_request`; issue a UUID4 trace ID; never echo input or exception text. Lexical third-party detection remains defense in depth.

- [ ] **Step 3: Add no-write/no-log failure tests**

Monkeypatch file-writing entry points and capture logs/stderr. Authorization, safety, and validation failures must create no engine-managed file/cache/session and reveal no raw or normalized profile value.

- [ ] **Step 4: Verify and commit**

Run focused unit/safety tests, mypy, and Ruff. Commit: `feat: guard real-use authorization and safety`.

### Task 6: Execute Analysis With Same-Process Provenance

**Files:**
- Modify: `src/mingli_engine/application_service.py`
- Modify: `src/mingli_engine/__init__.py`
- Create: `tests/integration/test_real_use_analysis.py`

- [ ] **Step 1: Write failing success and provenance-lifecycle tests**

Require chart and complete calculation output, filtered assumptions, rule/evidence IDs, versions, and no raw profile metadata. Prove report-bound bundle trust rejects cross-request reuse, shallow/deep copy, and serialize/deserialize reconstruction. Prove the weak provenance registry releases entries after garbage collection.

- [ ] **Step 2: Implement one-process analysis**

Construct `BirthProfile`, call the provider and analyzer in one request scope, serialize only public fields, and build `ApplicationProvenanceV1` from actual versions and evidence baseline.

- [ ] **Step 3: Test success and internal-exception privacy**

On success and injected provider/analyzer exception, assert no writes and no raw profile values in logs, errors, trace metadata, or stderr.

- [ ] **Step 4: Verify and commit**

Run analysis, provenance, calculation validation, mypy, and Ruff. Commit: `feat: expose same-process real-use analysis`.

### Task 7: Build Safe Reports, Whole-Object Redaction, And Post-Build Gate

**Files:**
- Create: `src/mingli_engine/application_reports.py`
- Modify: `src/mingli_engine/application_service.py`
- Modify: `src/mingli_engine/report_renderer.py`
- Create: `tests/integration/test_real_use_reports.py`
- Create: `tests/safety/test_real_use_rendering.py`

- [ ] **Step 1: Write all report safety tests before implementation**

For JSON, Markdown, and HTML, inject unique raw and NFKC-normalized sentinels into all six profile fields. With `include_profile_in_report=false`, assert every sentinel is absent from every nested report value, metadata value, and rendered byte. With inclusion true, require escaped output plus `contains_sensitive_profile=true`. Cover headings, Setext, raw HTML, links/images, tables, blockquotes, emphasis, code spans, and fences. Add report-size tests before renderer implementation.

- [ ] **Step 2: Write the post-build safety refusal test**

Monkeypatch `build_report()` to return `safety_review.allowed=false`; assert JSON/Markdown/HTML renderers are never called and the facade returns a controlled refusal.

- [ ] **Step 3: Implement whole-report redaction and escaping**

Traverse only the explicit report DTO schema, remove raw and normalized occurrences before any renderer, and never perform ad-hoc string replacement over serialized JSON. Escape untrusted included values at their Markdown/HTML insertion boundaries.

- [ ] **Step 4: Enforce post-build safety before rendering**

Inspect `report.safety_review.allowed` immediately after `build_report()`. Refuse before redaction/rendering when false. Preserve ordinary legacy output where no active markup is present.

- [ ] **Step 5: Verify and commit**

Run report integration/safety plus legacy renderer tests, mypy, and Ruff. Commit: `feat: render privacy-bounded real-use reports`.

### Task 8: Complete The JSON Handler And Controlled CLI

**Files:**
- Modify: `src/mingli_engine/application_service.py`
- Modify: `src/mingli_engine/application_serialization.py`
- Create: `src/mingli_engine/application_validation.py`
- Modify: `src/mingli_engine/cli.py`
- Modify: `src/mingli_engine/__init__.py`
- Create: `tests/contract/test_real_use_cli_contract.py`
- Create: `tests/unit/test_real_use_json_handler.py`
- Create: `tests/unit/test_application_validation.py`

- [ ] **Step 1: Write failing handler-envelope tests**

Require `handle_real_use_json(payload: bytes) -> bytes` to create trace ID before parsing; map parser, authorization, safety, unsupported input, calculation, knowledge, response-size, and unexpected exceptions to stable envelopes; return a small `response_too_large` envelope when normal output exceeds 1 MiB; and leak no exception text/path/input. Require `build_application_verification()` to execute fixed synthetic success, refusal, validation-failure, and injected-internal-error scenarios through audited dependencies and return an exact deterministic contract/privacy check map without writing a result artifact.

- [ ] **Step 2: Implement the complete boundary**

Implement `handle_real_use()`, `handle_real_use_json()`, `response_status_from_json_bytes()`, and `build_application_verification()`. The verifier uses a service dependency bundle whose write/log sinks are counting test doubles, checks envelopes and raw-value absence, and reports scenario names, contract status, privacy status, write count, leak count, and overall status. Export the three public request operations and all V1 DTOs from the root package; keep the verifier maintainer-facing.

- [ ] **Step 3: Implement `real-use --input <path-or->`**

Read file or stdin through one bounded helper that requests at most `MAX_REQUEST_BYTES + 1` bytes. When the sentinel byte exists, stop without buffering the remainder and emit `payload_too_large`. Write exactly one response JSON to stdout and map status to exit codes: ok 0, refused 3, error 1. Keep diagnostics off and stderr empty for controlled outcomes. Every strict parsing failure carries `operation=null` without peeking at partially valid JSON; every successfully parsed response carries `analysis` or `report`.

- [ ] **Step 4: Verify and checkpoint 019-B**

Run all application unit/integration/safety/contract tests plus legacy CLI tests, mypy, and Ruff. Commit: `feat: deliver controlled real-use application v1`.

### Task 9: Define Exact Calibration Models And Loaders

**Files:**
- Create: `src/mingli_engine/domain_calibration_models.py`
- Create: `src/mingli_engine/domain_calibration.py`
- Create: `tests/unit/test_domain_calibration_models.py`

- [ ] **Step 1: Write exact-field and validation tests**

Require the exact fields from design sections 13.1-13.3 for `CalibrationFileEnvelopeV1`, `CalibrationInputFixture`, `CalibrationCase`, `CalibrationAssertion`, `CalibrationCitation`, `BlindedAssertionProjection`, `ReviewerPacket`, `ReviewAssignment`, `CalibrationReview`, `AdjudicationDecision`, `CalibrationAssertionResult`, `CalibrationRun`, `MetricSnapshotV1`, and `CalibrationReleaseDecision`. Require review labels exactly `accept|revise|reject|abstain`, the exact primary-ID mapping, frozen records, tuples, exact keys, canonical record order, suite version, sorted upstream hashes, canonical-record SHA-256, privacy declaration, and no real personal data. Require `label=abstain` exactly when both expectation tuples are empty; non-abstain labels require at least one status.

- [ ] **Step 2: Implement models and strict read-only loaders**

Reject missing, extra, duplicate, malformed, noncanonical, hash-mismatched, or cross-reference-invalid records. Loaders never repair or rewrite files.

- [ ] **Step 3: Verify and commit**

Run focused pytest, mypy, and Ruff. Commit: `feat: define domain calibration protocol`.

### Task 10: Freeze Cases, Assertions, Citations, And Allowlisted Packets

**Files:**
- Create: `src/mingli_engine/data/domain_calibration/calibration_cases.json`
- Create: `src/mingli_engine/data/domain_calibration/input_fixtures.json`
- Create: `src/mingli_engine/data/domain_calibration/calibration_assertions.json`
- Create: `src/mingli_engine/data/domain_calibration/calibration_citations.json`
- Create: `src/mingli_engine/data/domain_calibration/reviewer_packets.json`
- Create: `tests/unit/test_domain_calibration_corpus.py`

- [ ] **Step 1: Write failing corpus coverage tests**

Require at least 42 assertions: each of 10 active families has positive, counterexample, and boundary/abstention coverage; each of three enabled schools has agreement, disagreement, counterexample, and not-computed/abstention coverage. Require exact inclusion of:

```text
pattern_counterexamples.json: strength_indeterminate_prerequisite
verified_charts.json: synthetic_01_19961215_0930
source_conflicts.json: conflict_high_risk_scope_001
strength_boundary_cases.json: unknown_gender_luck_prerequisite
luck_cycle_boundary_cases.json: aware_datetime_utc_plus_08_rejected_before_provider
luck_cycle_boundary_cases.json: aware_datetime_utc_rejected_before_provider
luck_cycle_boundary_cases.json: aware_datetime_utc_minus_05_rejected_before_provider
high-risk refusal: focus_topic 寿命 from the existing safety corpus
```

Require every case to execute a record from packaged `input_fixtures.json` by ID/hash, retain original source fixture file/ID/hash lineage, and declare `contains_real_personal_data=false`. Require explicit packaged record `safety_high_risk_lifespan_refusal_001`; runtime paths must not reference `tests/`.

- [ ] **Step 2: Write blindness packet tests**

Each canonical packet embeds one `BlindedAssertionProjection` containing synthetic case facts and candidate claim fields, plus citation excerpts, locators, rule scope, limitations, and the exact five-value access manifest from the design. Assert no engine output, adjudicated expectation, peer label, checkout path, unrelated record, or hidden field. Require SHA-256 over canonical bytes of the single `ReviewerPacket` value.

- [ ] **Step 3: Freeze the corpus and packets**

Select synthetic tracked cases only; copy only minimal input DTOs into the packaged fixture closure, preserve source-fixture hashes as lineage, and do not add raw material or copy long passages. Freeze canonical envelopes and hashes before reviewers receive packets.

- [ ] **Step 4: Verify and commit**

Run corpus/model tests and Ruff. Commit: `test: freeze bazi domain calibration corpus`.

### Task 11: Produce Reviewer A Records In Isolated Context

**Files:**
- Create: `src/mingli_engine/data/domain_calibration/reviewer_a_assignments.json`
- Create: `src/mingli_engine/data/domain_calibration/reviewer_a_reviews.json`
- Create: `tests/unit/test_domain_calibration_reviewer_a.py`

- [ ] **Step 1: Write reviewer-A validation tests and confirm red**

Require one review per assertion, exact packet hash, evidence/locator support, confidence, rationale, label-based abstention invariants, and the full blindness/access declaration. Run the test and confirm it fails because Reviewer A records are absent.

- [ ] **Step 2: Execute the controller procedure and turn green**

Spawn a fresh agent with `fork_context=false`; provide only canonical packet bytes; forbid tools and filesystem reads; require structured JSON. Record reviewer kind `agent_independent`, packet hash, access manifest, peer-label hidden, engine-output hidden, and independence attestation. The controller writes records; the reviewer does not write files. This is procedural/process blindness, not an OS-level isolation claim.

- [ ] **Step 3: Verify and commit**

Commit: `data: add independent calibration reviewer a`.

### Task 12: Produce Reviewer B Records Independently

**Files:**
- Create: `src/mingli_engine/data/domain_calibration/reviewer_b_assignments.json`
- Create: `src/mingli_engine/data/domain_calibration/reviewer_b_reviews.json`
- Create: `tests/unit/test_domain_calibration_reviewer_b.py`

- [ ] **Step 1: Write reviewer-B independence tests and confirm red**

Require distinct reviewer/assignment/review IDs, identical packet hashes, exact manifests, no peer references, full coverage, and no Reviewer A identity/output. Run the test and confirm it fails because Reviewer B records are absent.

- [ ] **Step 2: Execute the second isolated procedure and turn green**

Use a different fresh agent. Reviewer B receives the same packet bytes but no Reviewer A identity/output and no engine output. Use `fork_context=false`, no tools/filesystem, and controller-owned writes.

- [ ] **Step 3: Verify and commit**

Commit: `data: add independent calibration reviewer b`.

### Task 13: Adjudicate Without Collapsing Legitimate Schools

**Files:**
- Create: `src/mingli_engine/data/domain_calibration/adjudication.json`
- Create: `tests/unit/test_domain_calibration_adjudication.py`

- [ ] **Step 1: Write failing adjudication tests**

Require coverage of every assertion and both review IDs. Allowed decisions are agreement, clerical correction, retained alternative, and unresolved disagreement. Require exact safety-critical decisions and prohibit selecting a universal winner for legitimate school disagreement.

- [ ] **Step 2: Run a separate adjudicator agent and freeze decisions**

The adjudicator receives both frozen reviews, citations, and claim boundary, but no current engine output. Controller writes canonical decisions and hashes.

- [ ] **Step 3: Verify and checkpoint 019-C**

Commit: `data: adjudicate bazi domain calibration`.

### Task 14: Execute Calibration And Compute Metrics

**Files:**
- Modify: `src/mingli_engine/domain_calibration.py`
- Create: `src/mingli_engine/data/domain_calibration/calibration_baseline.json`
- Create: `tests/integration/test_domain_calibration_pipeline.py`

- [ ] **Step 1: Write failing runner and metric tests**

Require exact engine, ruleset, school-profile, evidence-baseline, fixture, and corpus versions; deterministic repeated runs; exact rule/evidence traces; unsupported and dependency-degraded cases remain non-computed; school alternatives remain visible.

- [ ] **Step 2: Implement runner and all metrics**

Compute determinism, cross-provider pillars, status/acceptable-set match, trace completeness, unsupported-computed count, dependency-bypass count, abstention quality, school recall/collapse, raw reviewer agreement, weighted kappa, Jaccard agreement, stratified coverage, and versioned deltas. Raw agreement is exact four-label equality. The single global kappa excludes abstentions, orders `reject=0`, `revise=1`, `accept=2`, uses linear weight `1-abs(i-j)/2`, is null below 10 eligible pairs, and is 1.0 when expected disagreement is zero. Jaccard uses acceptable-value sets and returns 1.0 for two empty sets. `reviewer_stratum_agreement` has only calendrical/structural/school keys and uses two-valid-review denominators including abstentions.

- [ ] **Step 3: Freeze read-only baseline**

Store exact version set, corpus hashes, metrics, and claim boundary. Runtime computes deltas but never rewrites it.

- [ ] **Step 4: Verify and commit**

Run calibration integration plus existing Bazi analysis pipeline, mypy, and Ruff. Commit: `feat: measure bazi domain conformance`.

### Task 15: Add Application, Privacy, Packaging, And Calibration Release Gates

**Files:**
- Create: `src/mingli_engine/domain_calibration_release.py`
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/project_completion.py`
- Modify: `src/mingli_engine/cli.py`
- Create: `tests/unit/test_domain_calibration_release.py`
- Create: `tests/integration/test_installed_real_use.py`
- Modify: `tests/unit/test_project_completion.py`
- Modify: `tests/contract/test_project_completion_cli_contract.py`

- [ ] **Step 1: Write failing exact-gate tests**

Require this exact check set: `determinism`, `pillar_agreement`, `trace_completeness`, `unsupported_inference`, `school_disagreement`, `abstention`, `adjudication`, `reviewer_independence`, `reviewer_agreement`, `engine_match`, `application_contract`, `privacy`, `packaging`, `claim_boundary`, `version_set`. Inject one failure per gate. Apply the 0.60 per-stratum raw-agreement gate only to the three case-stratum keys with at least 10 assertions having exactly two valid independent reviews; include abstentions in numerator/denominator. Treat all other coverage dimensions as informational. Before release implementation, write an installed-wheel test that builds and installs into a temporary target, runs real-use analysis, all report formats, and calibration summary outside the checkout, and confirms red because release integration/version closure is incomplete.

- [ ] **Step 2: Implement deterministic release logic**

Return `ready_with_guardrails` only when design section 17 thresholds all pass; otherwise return `blocked`, sorted blockers, exact metrics/version set, claim boundary, and next action. `application_contract` and `privacy` consume the corresponding fields from a single `build_application_verification()` result covering success/refusal/validation/internal-exception scenarios. `packaging` consumes a direct installed-distribution verification that builds a wheel in a temporary directory, checks asset hashes, installs outside the checkout, runs real-use analysis/reports and calibration summary, and proves source isolation. The installed child calls the summary builder with an explicit local `PackagingVerification` derived from its installed resources, so only the outer gate builds a wheel and no recursive packaging check occurs. Do not alter historical 018 result.

- [ ] **Step 3: Integrate copy-safe completion and CLI summary**

Compute once per summary call without global cache. Add `domain-calibration-summary`: ready exits 0, blocked exits 4. Add `src/mingli_engine/cli.py` to the task commit inventory.

- [ ] **Step 4: Verify and commit**

Run release, installed-distribution, completion, packaging verifier, and CLI contract tests, mypy, and Ruff. At this task the real release may remain blocked only by the required package version `0.2.0`; injected threshold tests must otherwise pass. Commit: `feat: gate calibrated application release`.

### Task 16: Prove Installed Application V1 And Advance Version

**Files:**
- Modify: `pyproject.toml`
- Modify: `tests/contract/test_wheel_runtime_assets.py`
- Modify: `tests/integration/test_installed_real_use.py`
- Modify: `tests/unit/test_domain_calibration_release.py`

- [ ] **Step 1: Write the exact release-version assertion and confirm red**

Require distribution version exactly `0.2.0`, all calibration JSON in the wheel, installed real-use/calibration commands green, and the recomputed domain release status `ready_with_guardrails`. Before the version edit, confirm this test fails only on version/version-set and dependent release status.

- [ ] **Step 2: Confirm red, then advance version to 0.2.0**

Change version only after every non-version application, privacy, calibration, and installed-packaging gate passes. Rebuild the wheel and recompute the full release decision; no cached Task 15 result may be reused.

- [ ] **Step 3: Verify and commit**

Run both wheel suites, mypy/Ruff for changed Python, and commit: `release: package calibrated application v1`.

### Task 17: Close Governance, Documentation, And Final Audit

**Files:**
- Move and finalize: `specs/_drafts/019-bazi-domain-validation-and-application-v1/` to `specs/019-bazi-domain-validation-and-application-v1/`
- Modify: `.specify/feature.json`
- Modify: `docs/classical_sources/README.md`
- Create: `docs/classical_sources/domain_calibration.md`
- Create: `docs/classical_sources/real_use_application.md`
- Modify: `src/mingli_engine/project_completion.py`
- Modify: `tests/unit/test_project_completion.py`
- Modify: `tests/contract/test_project_completion_cli_contract.py`

- [ ] **Step 1: Write failing governance-closure tests**

Require the complete formal 019 Spec Kit, no remaining draft directory, no placeholders, all task/checklist items closed, navigation links, exact application/calibration versions, claim boundary, `agent_independent` disclosure, procedural blindness limitation, accurate no-engine-retention wording, and explicit HTTP/UI/geographic exclusions. Require 019 to be added to expected feature/count baselines only at this closure task.

- [ ] **Step 2: Finalize governance and user documentation**

Move the pre-created package to its formal path, point `.specify/feature.json` at that path, and update in-progress artifacts to implemented facts. Add 019 to `EXPECTED_FEATURE_IDS`, update exact FR/SC/task/checklist aggregates from the formal artifacts, and advance the completion baseline ID as documented. Include synthetic self/authorized-other requests, commands, status interpretation, privacy limits, calibration meaning, and installation smoke. Never include real personal data.

- [ ] **Step 3: Run full suite with enforced controller timeout**

Tool timeout: `900000 ms`.

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest -q -p no:cacheprovider
```

- [ ] **Step 4: Run type, lint, and five release commands**

```powershell
uv run --with mypy==1.17.1 python -m mypy src/mingli_engine --follow-imports=skip
uv run --with ruff==0.12.11 ruff check src tests
python -m mingli_engine.cli knowledge-activation-summary
python -m mingli_engine.cli report-acceptance-summary
python -m mingli_engine.cli report-release-summary
python -m mingli_engine.cli domain-calibration-summary
python -m mingli_engine.cli project-completion-summary
```

- [ ] **Step 5: Run exact repository/privacy audit**

```powershell
git diff --check
git status --short
git status --short -- "资料原文" "资料整理" "Markdown" "*.pdf"
Get-ChildItem -Recurse -File -Include *.pdf,*.doc,*.docx,*.xls,*.xlsx,*.ppt,*.pptx | Select-Object -ExpandProperty FullName
Get-ChildItem -Recurse -File tmp,.codex-test-logs -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '(birth.?profile|real.?use|generated.?report|calibration.?run)' } | Select-Object -ExpandProperty FullName
git grep -n -I -E '(199[0-9]-[01][0-9]-[0-3][0-9].*(出生|birth)|真实姓名|身份证|手机号)' -- ':!tests/fixtures/**' ':!docs/superpowers/**'
```

Inspect the built wheel manifest and confirm no runtime-generated request, report, review, or run artifact exists outside the intentional tracked synthetic corpus. Raw-material status must be empty.

- [ ] **Step 6: Commit and perform fresh review**

Commit: `docs: complete calibrated application v1 governance`. Dispatch a fresh whole-feature reviewer over the complete 019 commit range, fix every Critical/Important finding, rerun Steps 3-5, then mark the long goal complete.

## Final Acceptance

The goal is complete only when the application facade/CLI is installed-wheel usable, all privacy and safety paths are proven, both blinded reviews and adjudication are frozen, all section-17 gates pass, 019 is formally incorporated into project completion, the full suite/type/lint/audit pass, and a fresh reviewer has no Critical or Important finding.
