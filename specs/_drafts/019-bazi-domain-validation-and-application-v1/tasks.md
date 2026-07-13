# Tasks: Bazi Domain Validation And Application V1

**Input**: Design documents from `/specs/_drafts/019-bazi-domain-validation-and-application-v1/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/real-use-v1-contract.md, contracts/domain-calibration-v1-contract.md, quickstart.md

**Tests**: Required. Every implementation phase follows red-green-refactor and verifies privacy, safety, compatibility, packaging, and calibration boundaries before commit.

**Organization**: Tasks follow the approved Task 0 through Task 17 execution order. Every item remains unchecked while the feature is in progress.

## Task 0: Establish Active Feature Governance Before Implementation

- [ ] T001 Pin `SPECIFY_FEATURE_DIRECTORY` and `.specify/feature.json` to `specs/_drafts/019-bazi-domain-validation-and-application-v1`
- [ ] T002 Create the complete draft Spec Kit under `specs/_drafts/019-bazi-domain-validation-and-application-v1/` and keep `specs/_drafts/019-bazi-domain-validation-and-application-v1/spec.md` status `In Progress`
- [ ] T003 Run draft consistency analysis across `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `tasks.md`, `contracts/`, and `checklists/` under `specs/_drafts/019-bazi-domain-validation-and-application-v1/`
- [ ] T004 Prove `tests/unit/test_project_completion.py` and `tests/contract/test_project_completion_cli_contract.py` remain green before application code
- [ ] T005 Commit Task 0 as `docs: establish 019 draft feature governance`

## Task 1: Package And Verify Runtime Assets

- [ ] T006 [P] Write failing wheel-manifest tests in `tests/contract/test_wheel_runtime_assets.py` for every JSON under `src/mingli_engine/data/`
- [ ] T007 [P] Write failing source-isolated installed-package tests in `tests/integration/test_installed_package_baseline.py`
- [ ] T008 Run `tests/contract/test_wheel_runtime_assets.py` and `tests/integration/test_installed_package_baseline.py` and confirm failures are limited to required wheel data and verifier behavior
- [ ] T009 Configure setuptools package discovery and `mingli_engine = ["data/**/*.json"]` in `pyproject.toml`
- [ ] T010 Implement read-only `PackagingVerification` in `src/mingli_engine/packaging_validation.py`
- [ ] T011 Run focused pytest, mypy, Ruff, and commit `fix: package and verify mingli runtime assets`

## Task 2: Freeze The Exact Application DTO Protocol

- [ ] T012 Write failing exact-field, literal, tuple, immutability, and complete response-matrix tests in `tests/unit/test_application_models.py`
- [ ] T013 Implement all frozen request, response, result, safety, privacy, warning, provenance, content, and error DTOs in `src/mingli_engine/application_models.py`
- [ ] T014 Verify focused pytest, mypy, Ruff, and commit `feat: define real-use application protocol`

## Task 3: Build The Strict JSON Request Boundary

- [ ] T015 Write failing parser tests in `tests/unit/test_application_inputs.py` using `tests/fixtures/application/valid_analysis_request.json` and `tests/fixtures/application/valid_report_request.json` for byte, UTF-8, duplicate-key, non-finite, depth, every required exact root/nested key, required nullable `request_id`, required boolean `include_profile_in_report`, unknown key, ID, literal, date, text, operation-format, and unsupported-input rules
- [ ] T016 Add synthetic valid request fixtures in `tests/fixtures/application/valid_analysis_request.json` and `tests/fixtures/application/valid_report_request.json`
- [ ] T017 Implement bounded strict parsing and explicit DTO construction in `src/mingli_engine/application_inputs.py`
- [ ] T018 Verify focused pytest, mypy, Ruff, and commit `feat: enforce strict real-use input boundary`

## Task 4: Publish Explicit Versioned Serializers

- [ ] T019 Write failing exact-key, deterministic JSON, private-field exclusion, status-reader, and 1 MiB response tests in `tests/unit/test_application_serialization.py`
- [ ] T020 Implement explicit chart, calculation, report, nested DTO, and response serializers in `src/mingli_engine/application_serialization.py`
- [ ] T021 Route compatible existing CLI serialization in `src/mingli_engine/cli.py` through helpers from `src/mingli_engine/application_serialization.py` and verify ordinary output in existing `tests/contract/` CLI tests
- [ ] T022 Verify application and legacy CLI tests, mypy, Ruff, and commit `refactor: publish versioned application serializers`

## Task 5: Enforce Authorization And Pre-Calculation Safety

- [ ] T023 [P] Write failing call-order and authorization tests in `tests/unit/test_application_service.py`
- [ ] T024 [P] Write failing prohibited-focus and high-risk refusal tests in `tests/safety/test_real_use_safety.py`
- [ ] T025 Implement authorization and safety decisions before calculation in `src/mingli_engine/application_service.py`
- [ ] T026 Add failure-path no-write, no-log, no-stderr, and no-profile-leak tests in `tests/unit/test_application_service.py` and `tests/safety/test_real_use_safety.py`
- [ ] T027 Verify focused pytest, mypy, Ruff, and commit `feat: guard real-use authorization and safety`

## Task 6: Execute Analysis With Same-Process Provenance

- [ ] T028 Write failing success, exact provenance, cross-request rejection, copy rejection, reconstruction rejection, and weak-registry cleanup tests in `tests/integration/test_real_use_analysis.py`
- [ ] T029 Implement one-process profile, provider, analyzer, public result, and provenance orchestration in `src/mingli_engine/application_service.py`
- [ ] T030 Export the typed application surface from `src/mingli_engine/__init__.py`
- [ ] T031 Add success and injected-exception no-write and no-leak tests in `tests/integration/test_real_use_analysis.py`
- [ ] T032 Verify analysis, provenance, calculation validation, mypy, Ruff, and commit `feat: expose same-process real-use analysis`

## Task 7: Build Safe Reports, Whole-Object Redaction, And Post-Build Gate

- [ ] T033 [P] Write failing JSON, Markdown, and HTML tests in `tests/integration/test_real_use_reports.py` for full-object redaction, profile inclusion, source locator/ID traceability, evidence/rule ID traceability, traditional-analysis disclaimer, and qualified-professional disclaimer
- [ ] T034 [P] Write failing JSON, Markdown, and HTML tests in `tests/safety/test_real_use_rendering.py` for active-markup escaping, report size, conditional and uncertainty language, and rejection before output of `必定`, `注定`, `一定会`, `死定`, and equivalent prohibited absolute wording
- [ ] T035 Write failing post-build safety test in `tests/integration/test_real_use_reports.py` proving no JSON, Markdown, or HTML renderer call after report refusal
- [ ] T036 Implement explicit report traversal, redaction, and content construction in `src/mingli_engine/application_reports.py`
- [ ] T037 Harden `src/mingli_engine/report_renderer.py` at Markdown and HTML insertion boundaries
- [ ] T038 Enforce post-build safety before redaction and rendering in `src/mingli_engine/application_service.py`
- [ ] T039 Verify report integration, safety, legacy renderer, mypy, Ruff, and commit `feat: render privacy-bounded real-use reports`

## Task 8: Complete The JSON Handler And Controlled CLI

- [ ] T040 [P] Write failing stable-envelope and exception-mapping tests in `tests/unit/test_real_use_json_handler.py`
- [ ] T041 [P] Write failing application verification tests in `tests/unit/test_application_validation.py`
- [ ] T042 [P] Write failing bounded stdin/file, one-envelope, stderr, operation, and exit-code tests in `tests/contract/test_real_use_cli_contract.py`
- [ ] T043 Implement `handle_real_use` and `handle_real_use_json` in `src/mingli_engine/application_service.py`, explicit non-OK response-matrix serialization and bounded oversized-response fallback in `src/mingli_engine/application_serialization.py`, and verify them in `tests/unit/test_real_use_json_handler.py`
- [ ] T044 Implement read-only deterministic `build_application_verification()` in `src/mingli_engine/application_validation.py`
- [ ] T045 Implement `real-use --input REQUEST_PATH_OR_STDIN` and root exports in `src/mingli_engine/cli.py` and `src/mingli_engine/__init__.py`
- [ ] T046 Verify all application and legacy CLI suites, mypy, Ruff, and commit `feat: deliver controlled real-use application v1`

## Task 9: Define Exact Calibration Models And Loaders

- [ ] T047 Write failing exact-field, frozen-record, `ExactVersionSet`, run/baseline/release equality, tuple, primary-ID, authoritative rule-family/school IDs, label, canonical-order, hash, privacy, and abstention tests in `tests/unit/test_domain_calibration_models.py`
- [ ] T048 Implement calibration dataclasses in `src/mingli_engine/domain_calibration_models.py`
- [ ] T049 Implement strict read-only canonical loaders and cross-reference validation in `src/mingli_engine/domain_calibration.py`
- [ ] T050 Verify focused pytest, mypy, Ruff, and commit `feat: define domain calibration protocol`

## Task 10: Freeze Cases, Assertions, Citations, And Allowlisted Packets

- [ ] T051 [P] Write failing minimum coverage, required-case, packaged-fixture, lineage, privacy, and installed-path tests in `tests/unit/test_domain_calibration_corpus.py`
- [ ] T052 [P] Write failing packet allowlist, embedded projection, exact manifest, exclusion, and canonical packet-hash tests in `tests/unit/test_domain_calibration_corpus.py` against `src/mingli_engine/data/domain_calibration/reviewer_packets.json`
- [ ] T053 Freeze `calibration_cases.json`, `input_fixtures.json`, `calibration_assertions.json`, and `calibration_citations.json` under `src/mingli_engine/data/domain_calibration/`
- [ ] T054 Freeze canonical allowlisted packets in `src/mingli_engine/data/domain_calibration/reviewer_packets.json` before any reviewer sees engine output
- [ ] T055 Verify corpus and model tests, Ruff, and commit `test: freeze bazi domain calibration corpus`

## Task 11: Produce Reviewer A Records In Isolated Context

- [ ] T056 Write failing reviewer-A coverage, packet-hash, evidence, confidence, rationale, abstention, and access-declaration tests in `tests/unit/test_domain_calibration_reviewer_a.py`
- [ ] T057 Execute Reviewer A in a fresh `fork_context=false` context using only canonical bytes from `src/mingli_engine/data/domain_calibration/reviewer_packets.json`, with no tools or filesystem
- [ ] T058 Controller-validate and write `src/mingli_engine/data/domain_calibration/reviewer_a_assignments.json` and `src/mingli_engine/data/domain_calibration/reviewer_a_reviews.json`, then verify both with `tests/unit/test_domain_calibration_reviewer_a.py`
- [ ] T059 Verify reviewer-A tests and commit `data: add independent calibration reviewer a`

## Task 12: Produce Reviewer B Records Independently

- [ ] T060 Write failing reviewer-B distinct-identity, same-packet, no-peer-reference, full-coverage, and access-declaration tests in `tests/unit/test_domain_calibration_reviewer_b.py`
- [ ] T061 Execute a different Reviewer B in a fresh `fork_context=false` context using `src/mingli_engine/data/domain_calibration/reviewer_packets.json` without Reviewer A identity or output
- [ ] T062 Controller-validate and write `src/mingli_engine/data/domain_calibration/reviewer_b_assignments.json` and `src/mingli_engine/data/domain_calibration/reviewer_b_reviews.json`, then verify both with `tests/unit/test_domain_calibration_reviewer_b.py`
- [ ] T063 Verify reviewer-B tests and commit `data: add independent calibration reviewer b`

## Task 13: Adjudicate Without Collapsing Legitimate Schools

- [ ] T064 Write failing complete-coverage, two-review, decision-literal, safety-critical, and school-alternative tests in `tests/unit/test_domain_calibration_adjudication.py`
- [ ] T065 Execute a separate adjudicator using frozen review files and `src/mingli_engine/data/domain_calibration/calibration_citations.json`, the claim boundary, and no current engine output
- [ ] T066 Controller-validate and freeze `src/mingli_engine/data/domain_calibration/adjudication.json` without collapsing legitimate school differences, then verify it with `tests/unit/test_domain_calibration_adjudication.py`
- [ ] T067 Verify adjudication tests and commit `data: adjudicate bazi domain calibration`

## Task 14: Execute Calibration And Compute Metrics

- [ ] T068 Write failing target-version, deterministic-run, trace, unsupported, dependency, school-alternative, metric-formula, candidate-baseline, and delta tests in `tests/integration/test_domain_calibration_pipeline.py`
- [ ] T069 Implement read-only calibration execution and assertion results in `src/mingli_engine/domain_calibration.py`
- [ ] T070 Implement determinism, pillar, `evidence_trace_completeness_rate`, `rule_trace_completeness_rate`, `adjudication_coverage_rate`, unsupported, dependency, abstention, school, reviewer, kappa, Jaccard, coverage, engine-match, safety, and delta metrics in `src/mingli_engine/domain_calibration.py`, with formula and empty-denominator tests in `tests/integration/test_domain_calibration_pipeline.py`
- [ ] T071 Generate a non-release candidate run, candidate snapshot, and candidate baseline for target `application_version=0.2.0` in `tests/integration/test_domain_calibration_pipeline.py`; the test may write only its temporary `tmp_path/calibration_baseline_candidate.json`, MUST NOT update `src/mingli_engine/data/domain_calibration/calibration_baseline.json`, and MUST prove the candidate cannot satisfy final release while the installed version differs
- [ ] T072 Verify calibration and existing Bazi pipeline tests, mypy, Ruff, and commit `feat: measure bazi domain conformance`

## Task 15: Add Application, Privacy, Packaging, And Calibration Release Gates

- [ ] T073 [P] Write failing exact-threshold, blocker, claim-boundary, version-set, and historical-018-isolation tests in `tests/unit/test_domain_calibration_release.py`
- [ ] T074 [P] Write failing installed real-use and calibration tests in `tests/integration/test_installed_real_use.py`
- [ ] T075 Implement deterministic application, privacy, packaging, calibration, documentation, and compatibility gates in `src/mingli_engine/domain_calibration_release.py`
- [ ] T076 Add exact release summary models and `domain-calibration-summary` CLI output in `src/mingli_engine/models.py` and `src/mingli_engine/cli.py`
- [ ] T077 Integrate 019 release evidence without changing completed-feature counts in `src/mingli_engine/project_completion.py`
- [ ] T078 Verify `tests/unit/test_domain_calibration_release.py` and `tests/integration/test_installed_real_use.py`, confirm the pre-0.2.0 release remains blocked only by version/final-baseline gates after all other checks pass, run mypy and Ruff, and commit `feat: gate calibrated application release`

## Task 16: Prove Installed Application V1 And Advance Version

- [ ] T079 Write failing final-release tests in `tests/contract/test_wheel_runtime_assets.py` and `tests/integration/test_installed_real_use.py` requiring `pyproject.toml` version 0.2.0, a wheel rebuilt after the frozen final baseline, every calibration asset, installed manifest and resource hashes, installed calibration summary and release decision, source isolation, equal final run/baseline/release `ExactVersionSet`, and `ready_with_guardrails`
- [ ] T080 Run `tests/contract/test_wheel_runtime_assets.py`, `tests/integration/test_installed_package_baseline.py`, and `tests/integration/test_installed_real_use.py`; confirm all non-version gates pass and that the pre-baseline wheel fails as release evidence because it lacks the frozen final baseline and post-baseline build identity
- [ ] T081 Update `pyproject.toml` to 0.2.0; build a pre-baseline wheel and install it only to execute a fresh final calibration run and metric snapshot through `src/mingli_engine/domain_calibration.py`; use the controlled release writer in `src/mingli_engine/domain_calibration_release.py` to replace and freeze `src/mingli_engine/data/domain_calibration/calibration_baseline.json`; discard the pre-baseline wheel as release evidence; build a new final wheel containing that frozen baseline; install the final wheel into a new empty temporary target; and from only that final installation verify manifest, calibration summary, release decision, resource SHA-256 map, source isolation, and exact run/baseline/release `ExactVersionSet` equality in `tests/contract/test_wheel_runtime_assets.py` and `tests/integration/test_installed_real_use.py`
- [ ] T082 Verify `tests/contract/test_wheel_runtime_assets.py`, `tests/integration/test_installed_package_baseline.py`, `tests/integration/test_installed_real_use.py`, and `tests/unit/test_domain_calibration_release.py` against the post-baseline final wheel and fresh installation, run mypy and Ruff, and commit `release: package calibrated application v1`

## Task 17: Close Governance, Documentation, And Final Audit

- [ ] T083 Write failing closure tests in `tests/unit/test_project_completion.py` and `tests/contract/test_project_completion_cli_contract.py` for formal 019 artifacts, no draft directory, no open items, exact counts, navigation, versions, claim boundary, procedural blindness, privacy wording, and exclusions
- [ ] T084 Move the completed Spec Kit atomically to `specs/019-bazi-domain-validation-and-application-v1/` and update `.specify/feature.json`
- [ ] T085 Publish maintainer and user documentation in `docs/classical_sources/domain_calibration.md`, `docs/classical_sources/real_use_application.md`, and navigation
- [ ] T086 Update feature IDs, exact requirement/success-criteria/task/checklist aggregates, and completion baseline in `src/mingli_engine/project_completion.py`, `tests/unit/test_project_completion.py`, and `tests/contract/test_project_completion_cli_contract.py`
- [ ] T087 Run the complete `tests/` pytest suite with 900000 ms controller timeout
- [ ] T088 Run full mypy over `src/mingli_engine/`, Ruff over `src/` and `tests/`, five release commands, repository privacy audit, built-wheel manifest audit, and `git diff --check`
- [ ] T089 Commit `docs: complete calibrated application v1 governance`
- [ ] T090 Run a fresh whole-feature review over the Task 1 through Task 17 commit range and all files named in `specs/019-bazi-domain-validation-and-application-v1/tasks.md`, fix every Critical or Important finding, and rerun T087-T088 verification

## Dependencies And Execution Order

- Task 0 governance blocks every implementation task.
- Tasks 1 through 4 establish package resources and the frozen protocol.
- Tasks 5 through 8 deliver the controlled application and checkpoint 019-B.
- Tasks 9 and 10 freeze calibration semantics and packets before review.
- Reviewer A and Reviewer B use independent contexts and must not share outputs.
- Adjudication starts only after both review files are frozen and must finish before engine execution.
- Task 14 generates candidate calibration objects for target application version 0.2.0 and never mutates the tracked final baseline.
- Task 15 evaluates non-version gates but cannot release a candidate or a version-mismatched baseline.
- Task 16 advances to 0.2.0, uses a pre-baseline installation only to compute final calibration, freezes the final baseline through the sole controlled release writer, rebuilds the final wheel after that freeze, installs it to a new target, and derives all release evidence from the final installation with equal run/baseline/release version sets.
- Version 0.2.0 is the final non-governance implementation change in Task 16 and follows all non-version gates.
- Formal 019 governance and completed-feature counts change atomically only in Task 17.

## Parallel Opportunities

- Independent test files marked `[P]` may be authored in parallel before their shared implementation begins.
- Wheel manifest and installed smoke tests may be authored in parallel.
- Application DTO, parser, serializer, safety, analysis, and report phases execute sequentially because each consumes the prior public contract.
- Reviewer A and Reviewer B are procedurally independent but controller integration remains sequential to prevent context leakage.

## Completion Rule

Feature 019 is complete only after the installed Python and CLI application satisfy V1, all privacy and safety paths pass, both independent reviews and adjudication are frozen, calibration and release gates pass, the wheel is source-isolated, governance is moved to the formal path, the full suite and audit pass, and a fresh reviewer reports no Critical or Important finding.
