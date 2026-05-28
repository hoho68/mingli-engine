# Tasks: Source Library Expansion and Evidence Factory

**Input**: Design documents from `/specs/014-source-library-expansion/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/source-library-expansion-contract.md, quickstart.md

**Tests**: Required. 014 is a domain evidence feature, so tasks include test-first validation for source metadata, evidence mapping, high-risk handling, report-boundary preservation, and non-absolute source-library language.

**Organization**: Tasks are grouped by user story to enable independent implementation and staged validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches separate files or independent fixtures.
- **[Story]**: User story label for story phases only.
- Every task includes exact repository file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create source-library scaffolding and documentation placeholders.

- [x] T001 Create source-library data directory and placeholder in `src/mingli_engine/data/source_library/.gitkeep`
- [x] T002 [P] Create empty JSON array data files in `src/mingli_engine/data/source_library/source_library_entries.json`, `src/mingli_engine/data/source_library/source_priority_assessments.json`, and `src/mingli_engine/data/source_library/curation_batch_plans.json`
- [x] T003 [P] Create maintainer documentation skeleton in `docs/classical_sources/source_library.md`
- [x] T004 [P] Create source-library module skeleton in `src/mingli_engine/source_library.py`
- [x] T005 [P] Create focused test file skeleton in `tests/unit/test_source_library.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared constants, models, loaders, and helper contracts that all user stories depend on.

**Critical**: No user story work should begin until this phase is complete.

- [x] T006 [P] Add source-library constant validation tests in `tests/unit/test_source_library.py`
- [x] T007 Add source-library enum constants for readiness, priority, expected value, effort, next action, batch status, and value status in `src/mingli_engine/models.py`
- [x] T008 Add `SourceLibraryEntry`, `SourcePriorityAssessment`, `CurationBatchPlan`, `EvidenceGapTarget`, `SourceValueSummary`, and `SourceLibraryProgressReport` dataclasses in `src/mingli_engine/models.py`
- [x] T009 [P] Add JSON loader error-handling tests for missing, malformed, non-array, and non-object source-library files in `tests/unit/test_source_library.py`
- [x] T010 Implement `SourceLibraryError`, data-directory resolution, JSON list readers, unique-id checks, and shared string/list validators in `src/mingli_engine/source_library.py`
- [x] T011 [P] Add fixture builders for temporary source-library data in `tests/unit/test_source_library.py`
- [x] T012 Add public loader stubs for entries, priority assessments, batch plans, progress reports, value summaries, and quality validation in `src/mingli_engine/source_library.py`
- [x] T013 Run the focused test target and confirm foundational tests fail before story implementation with `tests/unit/test_source_library.py`

**Checkpoint**: Foundation ready. Source-library models and loader helpers exist, and user stories can be implemented incrementally.

---

## Phase 3: User Story 1 - Register Source Materials for Future Use (Priority: P1) MVP

**Goal**: Register source materials with enough metadata for future extraction planning without tracking or mutating raw local files.

**Independent Test**: Load a source-library data set with registered materials and verify identity, readiness, topic coverage, quality notes, risk notes, rights notes, priority, and next action.

### Tests for User Story 1

- [x] T014 [P] [US1] Add tests that valid source-library entries load from `src/mingli_engine/data/source_library/source_library_entries.json` in `tests/unit/test_source_library.py`
- [x] T015 [P] [US1] Add tests that duplicate `entry_id`, invalid readiness, invalid tracking status, invalid priority, invalid next action, and invalid risk tier fail validation in `tests/unit/test_source_library.py`
- [x] T016 [P] [US1] Add tests that `ready_for_extraction` entries require topic tags, rule families, source quality notes, and rights notes in `tests/unit/test_source_library.py`
- [x] T017 [P] [US1] Add tests that `external_untracked` source entries are registered without requiring root PDF or `Markdown/` file operations in `tests/unit/test_source_library.py`
- [x] T018 [P] [US1] Add tests that high-risk entries require risk notes and blocked/deferred/duplicate/exhausted entries require durable outcome reasons in `tests/unit/test_source_library.py`

### Implementation for User Story 1

- [x] T019 [US1] Implement `load_source_library_entries()` and `SourceLibraryEntry` validation in `src/mingli_engine/source_library.py`
- [x] T020 [US1] Seed the current nine source-library entries from existing 013 materials in `src/mingli_engine/data/source_library/source_library_entries.json`
- [x] T021 [US1] Add source-entry progress counts by readiness, priority, rule family, and risk tier in `src/mingli_engine/source_library.py`
- [x] T022 [US1] Document the registered source-library snapshot and external raw-file boundary in `docs/classical_sources/source_library.md`
- [x] T023 [US1] Update the maintainer workflow reference for source-library registration in `docs/classical_sources/README.md`
- [x] T024 [US1] Run US1 focused validation with `tests/unit/test_source_library.py`

**Checkpoint**: US1 complete. Registered sources are visible and validated, but none are report-usable evidence.

---

## Phase 4: User Story 2 - Prioritize Extraction Batches (Priority: P2)

**Goal**: Rank sources and group ready materials into curation batch plans that target gaps, conflicts, rule families, source quality, and risk boundaries.

**Independent Test**: Create priority assessments and a planned batch from registered sources, then verify each high-priority source has a rationale and each batch has a target reason before extraction begins.

### Tests for User Story 2

- [x] T025 [P] [US2] Add tests that priority assessments load and reference existing source entries in `tests/unit/test_source_library.py`
- [x] T026 [P] [US2] Add tests that critical/high priorities require assessments and that target gaps or target rule families are not both empty in `tests/unit/test_source_library.py`
- [x] T027 [P] [US2] Add tests that `source_quality=needs_recheck` cannot be critical and high-risk assessments name the review boundary in `tests/unit/test_source_library.py`
- [x] T028 [P] [US2] Add tests that curation batch plans require entries, targets, expected outputs, and valid status in `tests/unit/test_source_library.py`
- [x] T029 [P] [US2] Add tests that high-risk batch plans require risk notes on all included high-risk entries in `tests/unit/test_source_library.py`

### Implementation for User Story 2

- [x] T030 [US2] Implement `load_source_priority_assessments()` and priority validation in `src/mingli_engine/source_library.py`
- [x] T031 [US2] Implement `load_curation_batch_plans()` and batch-plan validation in `src/mingli_engine/source_library.py`
- [x] T032 [US2] Seed priority assessments for current source-library entries in `src/mingli_engine/data/source_library/source_priority_assessments.json`
- [x] T033 [US2] Seed initial curation batch plans for high-risk boundaries and blind image-method review in `src/mingli_engine/data/source_library/curation_batch_plans.json`
- [x] T034 [US2] Implement next-source selection by priority, readiness, rule family, risk tier, source quality, and unresolved gaps in `src/mingli_engine/source_library.py`
- [x] T035 [US2] Document planned batches and next-source selection rules in `docs/classical_sources/source_library.md`
- [x] T036 [US2] Run US2 focused validation with `tests/unit/test_source_library.py`

**Checkpoint**: US2 complete. Maintainers can see which materials should be processed next and why.

---

## Phase 5: User Story 3 - Measure Source-to-Evidence Value (Priority: P3)

**Goal**: Compute value summaries showing whether a source or batch produced candidates, approvals, rejections, blocked outcomes, conflicts, gaps, and promoted evidence.

**Independent Test**: Link source-library entries to existing 013 source-intake data and verify value summaries separate review value from formal evidence contribution.

### Tests for User Story 3

- [x] T037 [P] [US3] Add tests that source value summaries count linked candidates, approved candidates, rejected or blocked candidates, conflicts, gaps, and promoted evidence in `tests/unit/test_source_library.py`
- [x] T038 [P] [US3] Add tests that registered sources with no downstream records are `not_started` or `in_progress`, not `value_produced`, in `tests/unit/test_source_library.py`
- [x] T039 [P] [US3] Add tests that approved but unpromoted candidates do not count as formal evidence contribution in `tests/unit/test_source_library.py`
- [x] T040 [P] [US3] Add tests that duplicate, deferred, exhausted, and blocked outcomes remain visible with durable reasons in `tests/unit/test_source_library.py`
- [x] T041 [P] [US3] Add tests that completed batch value summaries include improved rule families, remaining gaps, and recommended next action in `tests/unit/test_source_library.py`

### Implementation for User Story 3

- [x] T042 [US3] Implement source-to-candidate linkage through `material_id` in `src/mingli_engine/source_library.py`
- [x] T043 [US3] Implement source value summary computation from source-library, 013 intake, and 012 formal evidence data in `src/mingli_engine/source_library.py`
- [x] T044 [US3] Implement batch value summary computation from included entries and downstream outcomes in `src/mingli_engine/source_library.py`
- [x] T045 [US3] Add value-summary fields to the source-library progress report in `src/mingli_engine/source_library.py`
- [x] T046 [US3] Update computed value snapshot examples in `docs/classical_sources/source_library.md`
- [x] T047 [US3] Run US3 focused validation with `tests/unit/test_source_library.py`

**Checkpoint**: US3 complete. Sources and batches show evidence value, non-usefulness, and remaining gaps without inflating formal evidence coverage.

---

## Phase 6: User Story 4 - Protect Raw-Source and Report Boundaries (Priority: P4)

**Goal**: Ensure registered sources, planned batches, and unapproved candidates never become report-usable evidence or unsafe report language.

**Independent Test**: Register and prioritize a source with no approved evidence, then verify formal evidence and report-boundary tests do not count it as report-usable.

### Tests for User Story 4

- [x] T048 [P] [US4] Add tests that source-library entries and curation batch plans are excluded from formal evidence counts in `tests/unit/test_source_library.py`
- [x] T049 [P] [US4] Add regression tests that report evidence loading ignores source-library data in `tests/integration/test_report_regression_cases.py`
- [x] T050 [P] [US4] Add safety tests that source-library summaries reject absolute destiny language and prohibited high-risk wording in `tests/safety/test_expanded_high_risk_language.py`
- [x] T051 [P] [US4] Add tests that long copied source passages in source-library fields fail validation in `tests/unit/test_source_library.py`

### Implementation for User Story 4

- [x] T052 [US4] Implement source-library quality validation for report-boundary exclusion, high-risk notes, long copied passages, and absolute language in `src/mingli_engine/source_library.py`
- [x] T053 [US4] Ensure `classical_sources.py` report-usable loaders remain independent of `src/mingli_engine/data/source_library/` in `src/mingli_engine/classical_sources.py`
- [x] T054 [US4] Document raw-source, source-library, candidate, promoted-evidence, and report-evidence trust boundaries in `docs/classical_sources/source_library.md`
- [x] T055 [US4] Run US4 boundary validation with `tests/unit/test_source_library.py`, `tests/integration/test_report_regression_cases.py`, and `tests/safety/test_expanded_high_risk_language.py`

**Checkpoint**: US4 complete. 014 planning records are audit metadata only and cannot leak into formal reports.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, docs cleanup, and implementation hygiene across all stories.

- [x] T056 [P] Update 014 quickstart validation notes after implementation in `specs/014-source-library-expansion/quickstart.md`
- [x] T057 [P] Add source-library module export or package reference only if needed in `src/mingli_engine/__init__.py`
- [x] T058 [P] Review and tighten source-library documentation links in `docs/classical_sources/README.md` and `docs/classical_sources/source_library.md`
- [x] T059 Run the quickstart source-library command from `specs/014-source-library-expansion/quickstart.md`
- [x] T060 Run focused source-library tests with `tests/unit/test_source_library.py`
- [x] T061 Run boundary regression tests with `tests/unit/test_source_intake.py`, `tests/integration/test_report_regression_cases.py`, and `tests/safety/test_expanded_high_risk_language.py`
- [x] T062 Run full test suite with `uv run --with pytest python -m pytest`
- [x] T063 Update task completion statuses in `specs/014-source-library-expansion/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; MVP scope.
- **Phase 4 US2**: Depends on Phase 2 and benefits from US1 seeded entries.
- **Phase 5 US3**: Depends on Phase 2 and needs US1/US2 data links for useful summaries.
- **Phase 6 US4**: Depends on Phase 2 and can run after any story, but final boundary validation should run after US1-US3.
- **Phase 7 Polish**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational and is the recommended MVP.
- **US2 (P2)**: Can start after Foundational, but seeded batch plans depend on source entries from US1.
- **US3 (P3)**: Can start after Foundational, but meaningful value summaries depend on source entries and batch plans.
- **US4 (P4)**: Boundary tests can start after Foundational; final validation depends on all implemented stories.

### Within Each User Story

- Tests must be written first and observed failing before implementation.
- Shared models and constants precede loaders.
- Loaders precede progress and value summaries.
- Data seeds follow validation rules.
- Documentation updates follow working validation logic.

---

## Parallel Opportunities

- Setup tasks T002-T005 can run in parallel.
- Foundational tests T006, T009, and T011 can run in parallel before implementation.
- US1 tests T014-T018 can run in parallel.
- US2 tests T025-T029 can run in parallel.
- US3 tests T037-T041 can run in parallel.
- US4 tests T048-T051 can run in parallel.
- Documentation-only polish tasks T056 and T058 can run in parallel after implementation.

## Parallel Example: User Story 1

```text
Task: "T014 Add tests that valid source-library entries load from src/mingli_engine/data/source_library/source_library_entries.json in tests/unit/test_source_library.py"
Task: "T015 Add tests that duplicate entry_id, invalid readiness, invalid tracking status, invalid priority, invalid next action, and invalid risk tier fail validation in tests/unit/test_source_library.py"
Task: "T016 Add tests that ready_for_extraction entries require topic tags, rule families, source quality notes, and rights notes in tests/unit/test_source_library.py"
Task: "T017 Add tests that external_untracked source entries are registered without requiring root PDF or Markdown/ file operations in tests/unit/test_source_library.py"
Task: "T018 Add tests that high-risk entries require risk notes and blocked/deferred/duplicate/exhausted entries require durable outcome reasons in tests/unit/test_source_library.py"
```

## Parallel Example: User Story 2

```text
Task: "T025 Add tests that priority assessments load and reference existing source entries in tests/unit/test_source_library.py"
Task: "T028 Add tests that curation batch plans require entries, targets, expected outputs, and valid status in tests/unit/test_source_library.py"
Task: "T029 Add tests that high-risk batch plans require risk notes on all included high-risk entries in tests/unit/test_source_library.py"
```

## Parallel Example: User Story 3

```text
Task: "T037 Add tests that source value summaries count linked candidates, approved candidates, rejected or blocked candidates, conflicts, gaps, and promoted evidence in tests/unit/test_source_library.py"
Task: "T039 Add tests that approved but unpromoted candidates do not count as formal evidence contribution in tests/unit/test_source_library.py"
Task: "T041 Add tests that completed batch value summaries include improved rule families, remaining gaps, and recommended next action in tests/unit/test_source_library.py"
```

## Parallel Example: User Story 4

```text
Task: "T048 Add tests that source-library entries and curation batch plans are excluded from formal evidence counts in tests/unit/test_source_library.py"
Task: "T049 Add regression tests that report evidence loading ignores source-library data in tests/integration/test_report_regression_cases.py"
Task: "T050 Add safety tests that source-library summaries reject absolute destiny language and prohibited high-risk wording in tests/safety/test_expanded_high_risk_language.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1.
4. Stop and validate source registration independently.
5. Report next step before continuing to US2.

### Incremental Delivery

1. US1 creates a validated source library.
2. US2 adds priority and batch planning.
3. US3 adds source and batch value summaries.
4. US4 hardens raw-source and report boundaries.
5. Polish verifies quickstart, focused tests, boundary tests, and full suite.

### Stage Reporting

- Report after Phase 2 before starting US1 implementation.
- Report after each user story checkpoint.
- Do not proceed from one user story to the next without a short status summary and next-step prompt.

## Notes

- Root PDF files and root `Markdown/` remain external preparation materials.
- 014 does not perform automatic extraction, full-text conversion, or automatic evidence approval.
- Source-library entries, priority assessments, and batch plans are planning metadata, not formal report evidence.
- Use `apply_patch` for manual file edits during implementation.
