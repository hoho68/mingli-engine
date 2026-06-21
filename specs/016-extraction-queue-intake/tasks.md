# Tasks: Extraction Queue Intake Package

**Input**: Design documents from `/specs/016-extraction-queue-intake/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/extraction-queue-intake-contract.md, quickstart.md

**Tests**: Required. 016 is a domain evidence-preparation feature, so tasks include test-first validation for extraction work packages, task eligibility, candidate draft-slot boundaries, prerequisite backlog routing, high-risk handling, duplicate/overlap warnings, raw-file non-mutation, and report-boundary preservation.

**Organization**: Tasks are grouped by user story to enable independent implementation and staged validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches separate files or independent fixtures.
- **[Story]**: User story label for story phases only.
- Every task includes exact repository file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create extraction-queue-intake scaffolding, data placeholders, and documentation placeholders.

- [X] T001 Create extraction-queue-intake data directory and placeholder in `src/mingli_engine/data/extraction_queue_intake/.gitkeep`
- [X] T002 [P] Create empty JSON array data files in `src/mingli_engine/data/extraction_queue_intake/extraction_work_packages.json`, `src/mingli_engine/data/extraction_queue_intake/extraction_tasks.json`, `src/mingli_engine/data/extraction_queue_intake/candidate_draft_slots.json`, and `src/mingli_engine/data/extraction_queue_intake/prerequisite_backlog_records.json`
- [X] T003 [P] Create maintainer documentation skeleton in `docs/classical_sources/extraction_queue_intake.md`
- [X] T004 [P] Create extraction queue intake module skeleton in `src/mingli_engine/extraction_queue_intake.py`
- [X] T005 [P] Create focused test file skeleton in `tests/unit/test_extraction_queue_intake.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared constants, models, loaders, validators, and helper contracts that all user stories depend on.

**Critical**: No user story work should begin until this phase is complete.

- [X] T006 [P] Add extraction-queue-intake constant validation tests in `tests/unit/test_extraction_queue_intake.py`
- [X] T007 Add extraction package enum constants for package status, task status, draft slot status, backlog type, priority level, risk boundary, locator requirement, and manual action in `src/mingli_engine/models.py`
- [X] T008 Add `ExtractionWorkPackage`, `ExtractionTask`, `CandidateDraftSlot`, `PrerequisiteBacklogRecord`, and `PackageProgressSummary` dataclasses in `src/mingli_engine/models.py`
- [X] T009 [P] Add JSON loader error-handling tests for missing, malformed, non-array, and non-object extraction-queue-intake files in `tests/unit/test_extraction_queue_intake.py`
- [X] T010 Implement `ExtractionQueueIntakeError`, data-directory resolution, JSON list readers, unique-id checks, enum validators, and shared string/list validators in `src/mingli_engine/extraction_queue_intake.py`
- [X] T011 [P] Add fixture builders for temporary extraction-queue-intake data in `tests/unit/test_extraction_queue_intake.py`
- [X] T012 Add public loader stubs for work packages, extraction tasks, draft slots, backlog records, progress summaries, and quality validation in `src/mingli_engine/extraction_queue_intake.py`
- [X] T013 [P] Add performance smoke test for package summary loading under 300 ms in `tests/unit/test_extraction_queue_intake.py`
- [X] T014 Run the focused test target and confirm foundational tests fail before story implementation with `tests/unit/test_extraction_queue_intake.py`

**Checkpoint**: Foundation ready. Extraction queue intake models and loader helpers exist, and user stories can be implemented incrementally.

---

## Phase 3: User Story 1 - Build the Next Extraction Work Package (Priority: P1) MVP

**Goal**: Convert eligible 015 next-action queue items into a small extraction work package while routing non-ready queue items away from routine extraction.

**Independent Test**: Load the current 015 queue and verify only eligible `extraction_ready` items become extraction tasks with stable ids, source-library links, audit links, target rule families or gaps, risk boundary, and pre-extraction checks.

### Tests for User Story 1

- [X] T015 [P] [US1] Add tests that valid work packages and extraction tasks load from `src/mingli_engine/data/extraction_queue_intake/extraction_work_packages.json` and `src/mingli_engine/data/extraction_queue_intake/extraction_tasks.json` in `tests/unit/test_extraction_queue_intake.py`
- [X] T016 [P] [US1] Add tests that duplicate `package_id`, duplicate `task_id`, invalid package status, invalid task status, invalid priority, invalid risk boundary, and invalid manual action fail validation in `tests/unit/test_extraction_queue_intake.py`
- [X] T017 [P] [US1] Add tests that every extraction task references an existing 015 queue item, 015 audit record, readiness finding, and alignment finding in `tests/unit/test_extraction_queue_intake.py`
- [X] T018 [P] [US1] Add tests that only `extraction_ready` 015 queue items can become extraction tasks and that registration, preparation, risk-review, deferred, or blocked items cannot be scheduled as routine extraction in `tests/unit/test_extraction_queue_intake.py`
- [X] T019 [P] [US1] Add tests that extraction tasks require source-library relationship when available, target rule family or gap, locator requirement, source-quality note, rights note, risk boundary, and pre-extraction checks in `tests/unit/test_extraction_queue_intake.py`
- [X] T020 [P] [US1] Add tests that extraction task loading does not mutate 015 materials-audit data, 014 source-library data, or 013 source-intake data in `tests/unit/test_extraction_queue_intake.py`

### Implementation for User Story 1

- [X] T021 [US1] Implement `load_extraction_work_packages()` and `load_extraction_tasks()` validation in `src/mingli_engine/extraction_queue_intake.py`
- [X] T022 [US1] Implement cross-checks from extraction tasks to 015 queue items, audit records, readiness findings, alignment findings, 014 source-library entries, and 013 source materials in `src/mingli_engine/extraction_queue_intake.py`
- [X] T023 [US1] Seed initial work package for the current 015 next five recommended queue item ids in `src/mingli_engine/data/extraction_queue_intake/extraction_work_packages.json`
- [X] T024 [US1] Seed extraction tasks for eligible ready queue items in `src/mingli_engine/data/extraction_queue_intake/extraction_tasks.json`
- [X] T025 [US1] Implement extraction package progress counts by package status, task status, priority level, risk boundary, and selected source queue ids in `src/mingli_engine/extraction_queue_intake.py`
- [X] T026 [US1] Document the package snapshot and task eligibility boundary in `docs/classical_sources/extraction_queue_intake.md`
- [X] T027 [US1] Update maintainer workflow references for 016 in `docs/classical_sources/README.md`, `docs/classical_sources/materials_audit.md`, and `docs/classical_sources/intake.md`
- [X] T028 [US1] Run US1 focused validation with `tests/unit/test_extraction_queue_intake.py`

**Checkpoint**: US1 complete. Eligible 015 queue items are visible as extraction tasks, but no candidate extracts or formal evidence are created.

---

## Phase 4: User Story 2 - Prepare Candidate Draft Slots Without Evidence Promotion (Priority: P2)

**Goal**: Add candidate draft slots that describe future manual 013 candidates without copying source text, extracted meanings, review decisions, approval status, or promotion status.

**Independent Test**: Inspect the generated package and confirm candidate draft slots contain no source passages, no approved meanings, no review decisions, and no promotion status while still naming intended rule families or gaps.

### Tests for User Story 2

- [X] T029 [P] [US2] Add tests that candidate draft slots load and reference existing extraction tasks in `tests/unit/test_extraction_queue_intake.py`
- [X] T030 [P] [US2] Add tests that draft slots reject copied source passages, extracted meanings, review decisions, approval status, promotion status, and formal-evidence wording in `tests/unit/test_extraction_queue_intake.py`
- [X] T031 [P] [US2] Add tests that ready draft slots require locator requirement, expected review notes, safety requirements, and parent task pre-extraction checks in `tests/unit/test_extraction_queue_intake.py`
- [X] T032 [P] [US2] Add tests that sensitive and high-risk draft slots require uncertainty, limitation, and risk-review safety requirements in `tests/unit/test_extraction_queue_intake.py`
- [X] T033 [P] [US2] Add safety tests that extraction package task and draft-slot notes reject absolute destiny language, exact death/lifespan claims, medical/legal/psychological/investment instruction, coercive matching, anxiety creation, and paid-remedy upsells in `tests/safety/test_expanded_high_risk_language.py`
- [X] T034 [P] [US2] Add boundary regression tests that candidate draft slots are excluded from 013 candidate counts and formal evidence counts in `tests/integration/test_report_regression_cases.py`

### Implementation for User Story 2

- [X] T035 [US2] Implement `load_candidate_draft_slots()` and draft-slot validation in `src/mingli_engine/extraction_queue_intake.py`
- [X] T036 [US2] Implement extraction package quality validation for long copied passages, extracted-meaning leakage, review-state leakage, promotion-state leakage, absolute language, high-risk wording, and report-boundary exclusion in `src/mingli_engine/extraction_queue_intake.py`
- [X] T037 [US2] Seed candidate draft slots for the initial extraction tasks in `src/mingli_engine/data/extraction_queue_intake/candidate_draft_slots.json`
- [X] T038 [US2] Implement draft-slot progress counts by status, target rule family, risk boundary, and readiness state in `src/mingli_engine/extraction_queue_intake.py`
- [X] T039 [US2] Document draft-slot boundaries and manual extraction prerequisites in `docs/classical_sources/extraction_queue_intake.md`
- [X] T040 [US2] Run US2 validation with `tests/unit/test_extraction_queue_intake.py`, `tests/integration/test_report_regression_cases.py`, and `tests/safety/test_expanded_high_risk_language.py`

**Checkpoint**: US2 complete. Reviewers can see future candidate intent without creating unreviewed candidates or report evidence.

---

## Phase 5: User Story 3 - Preserve Backlog and Boundary Visibility (Priority: P3)

**Goal**: Preserve non-ready queue work as prerequisite backlog records and keep package records outside candidate, promotion, and report-evidence counts.

**Independent Test**: Generate a package that includes skipped queue items and verify non-ready items are represented as prerequisite backlog records, not extraction tasks or formal evidence.

### Tests for User Story 3

- [X] T041 [P] [US3] Add tests that prerequisite backlog records load and reference existing work packages, 015 queue items, and 015 audit records in `tests/unit/test_extraction_queue_intake.py`
- [X] T042 [P] [US3] Add tests that registration, preparation, locator-review, risk-review, deferred, and blocked backlog records require missing prerequisites or durable reasons in `tests/unit/test_extraction_queue_intake.py`
- [X] T043 [P] [US3] Add tests that risk-review, deferred, and blocked backlog records cannot be scheduled as routine extraction tasks in `tests/unit/test_extraction_queue_intake.py`
- [X] T044 [P] [US3] Add tests that duplicate or overlap warnings are produced for extraction tasks that point to existing 013 pending, approved, rejected, or blocked candidates in `tests/unit/test_extraction_queue_intake.py`
- [X] T045 [P] [US3] Add tests that package progress summaries include extraction task counts, draft slot counts, backlog counts, risk-boundary counts, overlap warning counts, and next manual action ids in `tests/unit/test_extraction_queue_intake.py`
- [X] T046 [P] [US3] Add boundary regression tests that extraction packages, tasks, draft slots, and backlog records do not change formal evidence counts in `tests/integration/test_report_regression_cases.py`

### Implementation for User Story 3

- [X] T047 [US3] Implement `load_prerequisite_backlog_records()` and backlog validation in `src/mingli_engine/extraction_queue_intake.py`
- [X] T048 [US3] Implement prerequisite backlog routing checks for registration, preparation, locator-review, risk-review, deferred, and blocked 015 queue items in `src/mingli_engine/extraction_queue_intake.py`
- [X] T049 [US3] Implement duplicate and overlap warning detection against existing 013 source-intake candidate records in `src/mingli_engine/extraction_queue_intake.py`
- [X] T050 [US3] Seed prerequisite backlog records for current registration, risk-review, and blocked/deferred next-action queue items in `src/mingli_engine/data/extraction_queue_intake/prerequisite_backlog_records.json`
- [X] T051 [US3] Implement `build_package_progress_summary()` and finalize `validate_extraction_package_quality()` in `src/mingli_engine/extraction_queue_intake.py`
- [X] T052 [US3] Document prerequisite backlog routing, duplicate/overlap warnings, and report-evidence boundaries in `docs/classical_sources/extraction_queue_intake.md`
- [X] T053 [US3] Run US3 validation with `tests/unit/test_extraction_queue_intake.py` and `tests/integration/test_report_regression_cases.py`

**Checkpoint**: US3 complete. Non-ready queue work stays visible without entering extraction tasks, candidate records, or formal evidence.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, docs cleanup, and implementation hygiene across all stories.

- [X] T054 [P] Update 016 quickstart validation notes after implementation in `specs/016-extraction-queue-intake/quickstart.md`
- [X] T055 [P] Add extraction queue intake module export or package reference only if needed in `src/mingli_engine/__init__.py`
- [X] T056 [P] Review and tighten documentation links in `docs/classical_sources/README.md`, `docs/classical_sources/source_library.md`, `docs/classical_sources/intake.md`, `docs/classical_sources/materials_audit.md`, and `docs/classical_sources/extraction_queue_intake.md`
- [X] T057 Run the quickstart extraction queue intake command from `specs/016-extraction-queue-intake/quickstart.md`
- [X] T058 Run focused extraction queue intake tests with `tests/unit/test_extraction_queue_intake.py`
- [X] T059 Run boundary regression tests with `tests/unit/test_extraction_queue_intake.py`, `tests/unit/test_materials_audit.py`, `tests/unit/test_source_library.py`, `tests/unit/test_source_intake.py`, `tests/integration/test_report_regression_cases.py`, and `tests/safety/test_expanded_high_risk_language.py`
- [X] T060 Run full test suite declared in `pyproject.toml` with `uv run --with pytest python -m pytest`
- [X] T061 Update task completion statuses in `specs/016-extraction-queue-intake/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; MVP scope.
- **Phase 4 US2**: Depends on Phase 2 and benefits from US1 extraction tasks.
- **Phase 5 US3**: Depends on Phase 2 and benefits from US1/US2 package and draft-slot data.
- **Phase 6 Polish**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational and is the recommended MVP.
- **US2 (P2)**: Can start after Foundational, but seeded draft slots depend on extraction tasks from US1.
- **US3 (P3)**: Can start after Foundational, but useful backlog summaries depend on package/task/draft-slot data from US1/US2.

### Within Each User Story

- Tests must be written first and observed failing before implementation.
- Shared constants and models precede loaders.
- Loaders precede progress summaries and quality validation.
- Data seeds follow validation rules.
- Documentation updates follow working validation logic.

---

## Parallel Opportunities

- Setup tasks T002-T005 can run in parallel.
- Foundational tests T006, T009, T011, and T013 can run in parallel before implementation.
- US1 tests T015-T020 can run in parallel.
- US2 tests T029-T034 can run in parallel.
- US3 tests T041-T046 can run in parallel.
- Documentation-only polish tasks T054 and T056 can run in parallel after implementation.

## Parallel Example: User Story 1

```text
Task: "T015 Add tests that valid work packages and extraction tasks load from src/mingli_engine/data/extraction_queue_intake/extraction_work_packages.json and src/mingli_engine/data/extraction_queue_intake/extraction_tasks.json in tests/unit/test_extraction_queue_intake.py"
Task: "T017 Add tests that every extraction task references an existing 015 queue item, 015 audit record, readiness finding, and alignment finding in tests/unit/test_extraction_queue_intake.py"
Task: "T020 Add tests that extraction task loading does not mutate 015 materials-audit data, 014 source-library data, or 013 source-intake data in tests/unit/test_extraction_queue_intake.py"
```

## Parallel Example: User Story 2

```text
Task: "T029 Add tests that candidate draft slots load and reference existing extraction tasks in tests/unit/test_extraction_queue_intake.py"
Task: "T030 Add tests that draft slots reject copied source passages, extracted meanings, review decisions, approval status, promotion status, and formal-evidence wording in tests/unit/test_extraction_queue_intake.py"
Task: "T034 Add boundary regression tests that candidate draft slots are excluded from 013 candidate counts and formal evidence counts in tests/integration/test_report_regression_cases.py"
```

## Parallel Example: User Story 3

```text
Task: "T041 Add tests that prerequisite backlog records load and reference existing work packages, 015 queue items, and 015 audit records in tests/unit/test_extraction_queue_intake.py"
Task: "T044 Add tests that duplicate or overlap warnings are produced for extraction tasks that point to existing 013 pending, approved, rejected, or blocked candidates in tests/unit/test_extraction_queue_intake.py"
Task: "T046 Add boundary regression tests that extraction packages, tasks, draft slots, and backlog records do not change formal evidence counts in tests/integration/test_report_regression_cases.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1.
4. Stop and validate package/task creation independently.
5. Report next step before continuing to US2.

### Incremental Delivery

1. US1 creates a bounded extraction work package from eligible 015 queue items.
2. US2 adds candidate draft slots without creating 013 candidates or formal evidence.
3. US3 preserves prerequisite backlogs and duplicate/overlap warnings.
4. Polish verifies quickstart, focused tests, boundary tests, and full suite.

### Stage Reporting

- Report after Phase 2 before starting US1 implementation.
- Report after each user story checkpoint.
- Do not proceed from one user story to the next without a short status summary and next-step prompt.

## Notes

- Root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials.
- 016 does not perform automatic extraction, OCR, runtime PDF parsing, automatic candidate creation, automatic evidence approval, or report generation.
- Extraction packages, extraction tasks, candidate draft slots, and prerequisite backlog records are planning metadata, not candidate extracts or formal evidence.
- Use `apply_patch` for manual file edits during implementation.
