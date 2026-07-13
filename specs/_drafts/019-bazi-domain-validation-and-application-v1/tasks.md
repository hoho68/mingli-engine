# Tasks: Bazi Domain Validation And Application V1

**Input**: Design documents from `/specs/_drafts/019-bazi-domain-validation-and-application-v1/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/real-use-v1-contract.md, contracts/domain-calibration-v1-contract.md, quickstart.md

**Tests**: Required. Every implementation phase follows red-green-refactor and verifies privacy, safety, compatibility, packaging, and calibration boundaries before commit.

**Organization**: Tasks follow the approved Task 0 through Task 17 execution order. Every item remains unchecked while the feature is in progress.

## Phase 1: Active Draft Governance

- [ ] T001 Pin `SPECIFY_FEATURE_DIRECTORY` and `.specify/feature.json` to `specs/_drafts/019-bazi-domain-validation-and-application-v1`
- [ ] T002 Create the complete draft Spec Kit and keep `spec.md` status `In Progress`
- [ ] T003 Run draft consistency analysis and reject placeholder, requirement, contract, and terminology drift
- [ ] T004 Prove `tests/unit/test_project_completion.py` and `tests/contract/test_project_completion_cli_contract.py` remain green before application code
- [ ] T005 Commit Task 0 as `docs: establish 019 draft feature governance`

## Phase 2: Package Runtime Assets

- [ ] T006 [P] Write failing wheel-manifest tests in `tests/contract/test_wheel_runtime_assets.py` for every JSON under `src/mingli_engine/data/`
- [ ] T007 [P] Write failing source-isolated installed-package tests in `tests/integration/test_installed_package_baseline.py`
- [ ] T008 Confirm packaging tests fail only because required wheel data and verifier behavior are absent
- [ ] T009 Configure setuptools package discovery and `mingli_engine = ["data/**/*.json"]` in `pyproject.toml`
- [ ] T010 Implement read-only `PackagingVerification` in `src/mingli_engine/packaging_validation.py`
- [ ] T011 Run focused pytest, mypy, Ruff, and commit `fix: package and verify mingli runtime assets`

## Phase 3: Freeze Application DTO Protocol

- [ ] T012 Write failing exact-field, literal, tuple, immutability, and response-invariant tests in `tests/unit/test_application_models.py`
- [ ] T013 Implement all frozen request, response, result, safety, privacy, warning, provenance, content, and error DTOs in `src/mingli_engine/application_models.py`
- [ ] T014 Verify focused pytest, mypy, Ruff, and commit `feat: define real-use application protocol`

## Phase 4: Strict JSON Request Boundary

- [ ] T015 Write failing parser tests for byte, UTF-8, duplicate-key, non-finite, depth, exact-key, ID, literal, date, text, operation-format, and unsupported-input rules
- [ ] T016 Add synthetic valid request fixtures in `tests/fixtures/application/valid_analysis_request.json` and `tests/fixtures/application/valid_report_request.json`
- [ ] T017 Implement bounded strict parsing and explicit DTO construction in `src/mingli_engine/application_inputs.py`
- [ ] T018 Verify focused pytest, mypy, Ruff, and commit `feat: enforce strict real-use input boundary`

## Phase 5: Explicit Public Serialization

- [ ] T019 Write failing exact-key, deterministic JSON, private-field exclusion, status-reader, and 1 MiB response tests in `tests/unit/test_application_serialization.py`
- [ ] T020 Implement explicit chart, calculation, report, nested DTO, and response serializers in `src/mingli_engine/application_serialization.py`
- [ ] T021 Route compatible existing CLI serialization through public helpers without changing ordinary output
- [ ] T022 Verify application and legacy CLI tests, mypy, Ruff, and commit `refactor: publish versioned application serializers`

## Phase 6: Authorization And Pre-Calculation Safety

- [ ] T023 [P] Write failing call-order and authorization tests in `tests/unit/test_application_service.py`
- [ ] T024 [P] Write failing prohibited-focus and high-risk refusal tests in `tests/safety/test_real_use_safety.py`
- [ ] T025 Implement authorization and safety decisions before calculation in `src/mingli_engine/application_service.py`
- [ ] T026 Add failure-path no-write, no-log, no-stderr, and no-profile-leak tests
- [ ] T027 Verify focused pytest, mypy, Ruff, and commit `feat: guard real-use authorization and safety`

## Phase 7: Same-Process Analysis And Provenance

- [ ] T028 Write failing success, exact provenance, cross-request rejection, copy rejection, reconstruction rejection, and weak-registry cleanup tests in `tests/integration/test_real_use_analysis.py`
- [ ] T029 Implement one-process profile, provider, analyzer, public result, and provenance orchestration in `src/mingli_engine/application_service.py`
- [ ] T030 Export the typed application surface from `src/mingli_engine/__init__.py`
- [ ] T031 Add success and injected-exception no-write and no-leak tests
- [ ] T032 Verify analysis, provenance, calculation validation, mypy, Ruff, and commit `feat: expose same-process real-use analysis`

## Phase 8: Safe Reports And Whole-Object Redaction

- [ ] T033 [P] Write failing JSON, Markdown, and HTML full-object redaction and profile-inclusion tests in `tests/integration/test_real_use_reports.py`
- [ ] T034 [P] Write failing active-markup escaping and report-size tests in `tests/safety/test_real_use_rendering.py`
- [ ] T035 Write failing post-build safety test proving no renderer call after report refusal
- [ ] T036 Implement explicit report traversal, redaction, and content construction in `src/mingli_engine/application_reports.py`
- [ ] T037 Harden `src/mingli_engine/report_renderer.py` at Markdown and HTML insertion boundaries
- [ ] T038 Enforce post-build safety before redaction and rendering in `src/mingli_engine/application_service.py`
- [ ] T039 Verify report integration, safety, legacy renderer, mypy, Ruff, and commit `feat: render privacy-bounded real-use reports`

## Phase 9: JSON Handler, Verification, And CLI

- [ ] T040 [P] Write failing stable-envelope and exception-mapping tests in `tests/unit/test_real_use_json_handler.py`
- [ ] T041 [P] Write failing application verification tests in `tests/unit/test_application_validation.py`
- [ ] T042 [P] Write failing bounded stdin/file, one-envelope, stderr, operation, and exit-code tests in `tests/contract/test_real_use_cli_contract.py`
- [ ] T043 Implement `handle_real_use`, `handle_real_use_json`, and bounded oversized-response fallback
- [ ] T044 Implement read-only deterministic `build_application_verification()` in `src/mingli_engine/application_validation.py`
- [ ] T045 Implement `real-use --input REQUEST_PATH_OR_STDIN` and root exports in `src/mingli_engine/cli.py` and `src/mingli_engine/__init__.py`
- [ ] T046 Verify all application and legacy CLI suites, mypy, Ruff, and commit `feat: deliver controlled real-use application v1`

## Phase 10: Calibration Models And Loaders

- [ ] T047 Write failing exact-field, frozen-record, tuple, primary-ID, label, canonical-order, hash, privacy, and abstention tests in `tests/unit/test_domain_calibration_models.py`
- [ ] T048 Implement calibration dataclasses in `src/mingli_engine/domain_calibration_models.py`
- [ ] T049 Implement strict read-only canonical loaders and cross-reference validation in `src/mingli_engine/domain_calibration.py`
- [ ] T050 Verify focused pytest, mypy, Ruff, and commit `feat: define domain calibration protocol`

## Phase 11: Freeze Calibration Corpus And Packets

- [ ] T051 [P] Write failing minimum coverage, required-case, packaged-fixture, lineage, privacy, and installed-path tests in `tests/unit/test_domain_calibration_corpus.py`
- [ ] T052 [P] Write failing packet allowlist, embedded projection, exact manifest, exclusion, and canonical packet-hash tests
- [ ] T053 Freeze `calibration_cases.json`, `input_fixtures.json`, `calibration_assertions.json`, and `calibration_citations.json` under `src/mingli_engine/data/domain_calibration/`
- [ ] T054 Freeze canonical allowlisted `reviewer_packets.json` before any reviewer sees engine output
- [ ] T055 Verify corpus and model tests, Ruff, and commit `test: freeze bazi domain calibration corpus`

## Phase 12: Independent Reviewer A

- [ ] T056 Write failing reviewer-A coverage, packet-hash, evidence, confidence, rationale, abstention, and access-declaration tests in `tests/unit/test_domain_calibration_reviewer_a.py`
- [ ] T057 Execute Reviewer A in a fresh `fork_context=false` context with only packet bytes and no tools or filesystem
- [ ] T058 Controller-validate and write `reviewer_a_assignments.json` and `reviewer_a_reviews.json`
- [ ] T059 Verify reviewer-A tests and commit `data: add independent calibration reviewer a`

## Phase 13: Independent Reviewer B

- [ ] T060 Write failing reviewer-B distinct-identity, same-packet, no-peer-reference, full-coverage, and access-declaration tests in `tests/unit/test_domain_calibration_reviewer_b.py`
- [ ] T061 Execute a different Reviewer B in a fresh `fork_context=false` context without Reviewer A identity or output
- [ ] T062 Controller-validate and write `reviewer_b_assignments.json` and `reviewer_b_reviews.json`
- [ ] T063 Verify reviewer-B tests and commit `data: add independent calibration reviewer b`

## Phase 14: Separate Adjudication

- [ ] T064 Write failing complete-coverage, two-review, decision-literal, safety-critical, and school-alternative tests in `tests/unit/test_domain_calibration_adjudication.py`
- [ ] T065 Execute a separate adjudicator with frozen reviews, citations, claim boundary, and no current engine output
- [ ] T066 Controller-validate and freeze `adjudication.json` without collapsing legitimate school differences
- [ ] T067 Verify adjudication tests and commit `data: adjudicate bazi domain calibration`

## Phase 15: Calibration Runner And Metrics

- [ ] T068 Write failing exact-version, deterministic-run, trace, unsupported, dependency, school-alternative, metric-formula, and delta tests in `tests/integration/test_domain_calibration_pipeline.py`
- [ ] T069 Implement read-only calibration execution and assertion results in `src/mingli_engine/domain_calibration.py`
- [ ] T070 Implement determinism, pillar, trace, unsupported, dependency, abstention, school, reviewer, kappa, Jaccard, coverage, engine-match, safety, and delta metrics
- [ ] T071 Freeze exact version set, corpus hashes, metrics, and claim boundary in `calibration_baseline.json`
- [ ] T072 Verify calibration and existing Bazi pipeline tests, mypy, Ruff, and commit `feat: measure bazi domain conformance`

## Phase 16: Release Gates And Installed Integration

- [ ] T073 [P] Write failing exact-threshold, blocker, claim-boundary, version-set, and historical-018-isolation tests in `tests/unit/test_domain_calibration_release.py`
- [ ] T074 [P] Write failing installed real-use and calibration tests in `tests/integration/test_installed_real_use.py`
- [ ] T075 Implement deterministic application, privacy, packaging, calibration, documentation, and compatibility gates in `src/mingli_engine/domain_calibration_release.py`
- [ ] T076 Add exact release summary models and `domain-calibration-summary` CLI output in `src/mingli_engine/models.py` and `src/mingli_engine/cli.py`
- [ ] T077 Integrate 019 release evidence without changing completed-feature counts in `src/mingli_engine/project_completion.py`
- [ ] T078 Verify focused and installed tests, mypy, Ruff, and commit `feat: gate calibrated application release`

## Phase 17: Installed V1 And Version Advancement

- [ ] T079 Write failing wheel release tests requiring version 0.2.0, every calibration asset, installed real-use and calibration commands, and `ready_with_guardrails`
- [ ] T080 Confirm all non-version gates pass and the test fails only on version-dependent expectations
- [ ] T081 Advance package version to 0.2.0, rebuild the wheel, and recompute the full release decision without cached results
- [ ] T082 Verify both wheel suites, mypy, Ruff, and commit `release: package calibrated application v1`

## Phase 18: Governance Closure And Final Audit

- [ ] T083 Write failing closure tests for formal 019 artifacts, no draft directory, no open items, exact counts, navigation, versions, claim boundary, procedural blindness, privacy wording, and exclusions
- [ ] T084 Move the completed Spec Kit atomically to `specs/019-bazi-domain-validation-and-application-v1/` and update `.specify/feature.json`
- [ ] T085 Publish maintainer and user documentation in `docs/classical_sources/domain_calibration.md`, `docs/classical_sources/real_use_application.md`, and navigation
- [ ] T086 Update project-completion feature IDs, exact requirement, success-criteria, task, checklist aggregates, and completion baseline
- [ ] T087 Run the complete pytest suite with 900000 ms controller timeout
- [ ] T088 Run full mypy, Ruff, five release commands, repository privacy audit, wheel manifest audit, and `git diff --check`
- [ ] T089 Commit `docs: complete calibrated application v1 governance`
- [ ] T090 Run a fresh whole-feature review, fix every Critical or Important finding, and rerun all final verification

## Dependencies And Execution Order

- Phase 1 governance blocks every implementation phase.
- Phases 2 through 5 establish package resources and the frozen protocol.
- Phases 6 through 9 deliver the controlled application and checkpoint 019-B.
- Phases 10 and 11 freeze calibration semantics and packets before review.
- Reviewer A and Reviewer B use independent contexts and must not share outputs.
- Adjudication starts only after both review files are frozen and must finish before engine execution.
- Metrics and release gates consume immutable upstream records and never rewrite them.
- Version 0.2.0 is the final non-governance implementation change and follows all non-version gates.
- Formal 019 governance and completed-feature counts change atomically only in Phase 18.

## Parallel Opportunities

- Independent test files marked `[P]` may be authored in parallel before their shared implementation begins.
- Wheel manifest and installed smoke tests may be authored in parallel.
- Application DTO, parser, serializer, safety, analysis, and report phases execute sequentially because each consumes the prior public contract.
- Reviewer A and Reviewer B are procedurally independent but controller integration remains sequential to prevent context leakage.

## Completion Rule

Feature 019 is complete only after the installed Python and CLI application satisfy V1, all privacy and safety paths pass, both independent reviews and adjudication are frozen, calibration and release gates pass, the wheel is source-isolated, governance is moved to the formal path, the full suite and audit pass, and a fresh reviewer reports no Critical or Important finding.
