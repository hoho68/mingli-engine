# Tasks: Existing Materials Audit and Preparation

**Input**: Design documents from `/specs/015-existing-materials-audit/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/existing-materials-audit-contract.md, quickstart.md

**Tests**: Required. 015 is a domain evidence-preparation feature, so tasks include test-first validation for material audit records, source-library alignment, readiness classification, high-risk handling, queue boundaries, raw-file non-mutation, and report-boundary preservation.

**Organization**: Tasks are grouped by user story to enable independent implementation and staged validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches separate files or independent fixtures.
- **[Story]**: User story label for story phases only.
- Every task includes exact repository file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create materials-audit scaffolding, data placeholders, and documentation placeholders.

- [X] T001 Create materials-audit data directory and placeholder in `src/mingli_engine/data/materials_audit/.gitkeep`
- [X] T002 [P] Create empty JSON array data files in `src/mingli_engine/data/materials_audit/material_audit_records.json`, `src/mingli_engine/data/materials_audit/material_representations.json`, `src/mingli_engine/data/materials_audit/source_alignment_findings.json`, `src/mingli_engine/data/materials_audit/preparation_readiness_findings.json`, and `src/mingli_engine/data/materials_audit/extraction_queue_items.json`
- [X] T003 [P] Create maintainer documentation skeleton in `docs/classical_sources/materials_audit.md`
- [X] T004 [P] Create materials-audit module skeleton in `src/mingli_engine/materials_audit.py`
- [X] T005 [P] Create focused test file skeleton in `tests/unit/test_materials_audit.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared constants, models, loaders, validators, and helper contracts that all user stories depend on.

**Critical**: No user story work should begin until this phase is complete.

- [X] T006 [P] Add materials-audit constant validation tests in `tests/unit/test_materials_audit.py`
- [X] T007 Add materials-audit enum constants for material scope, representation type, source boundary, identity confidence, preparation state, match type, readiness state, queue type, and audit actions in `src/mingli_engine/models.py`
- [X] T008 Add `MaterialAuditRecord`, `MaterialRepresentation`, `SourceAlignmentFinding`, `PreparationReadinessFinding`, `ExtractionQueueItem`, and `AuditProgressSummary` dataclasses in `src/mingli_engine/models.py`
- [X] T009 [P] Add JSON loader error-handling tests for missing, malformed, non-array, and non-object materials-audit files in `tests/unit/test_materials_audit.py`
- [X] T010 Implement `MaterialsAuditError`, data-directory resolution, JSON list readers, unique-id checks, enum validators, and shared string/list validators in `src/mingli_engine/materials_audit.py`
- [X] T011 [P] Add fixture builders for temporary materials-audit data in `tests/unit/test_materials_audit.py`
- [X] T012 Add public loader stubs for audit records, representations, alignment findings, readiness findings, queue items, progress summaries, and quality validation in `src/mingli_engine/materials_audit.py`
- [X] T013 Run the focused test target and confirm foundational tests fail before story implementation with `tests/unit/test_materials_audit.py`

**Checkpoint**: Foundation ready. Materials-audit models and loader helpers exist, and user stories can be implemented incrementally.

---

## Phase 3: User Story 1 - Inventory Existing Materials (Priority: P1) MVP

**Goal**: Inventory existing root PDFs, Markdown batches, cleaned Markdown variants, maintainer notes, processing-status notes, and knowledge-skeleton artifacts as auditable material groups without mutating raw files.

**Independent Test**: Load a materials-audit data set with material groups and representations, then verify each discovered group has stable identity, representation links, preparation state, source boundary, and next action while raw-file references remain external.

### Tests for User Story 1

- [X] T014 [P] [US1] Add tests that valid material audit records and representations load from `src/mingli_engine/data/materials_audit/material_audit_records.json` and `src/mingli_engine/data/materials_audit/material_representations.json` in `tests/unit/test_materials_audit.py`
- [X] T015 [P] [US1] Add tests that duplicate `audit_id`, duplicate `representation_id`, invalid material scope, invalid representation type, invalid source boundary, invalid preparation state, and invalid next action fail validation in `tests/unit/test_materials_audit.py`
- [X] T016 [P] [US1] Add tests that each audit record requires at least one representation or a documented `derived_note_only` boundary in `tests/unit/test_materials_audit.py`
- [X] T017 [P] [US1] Add tests that `external_untracked` root PDF, raw folder, and root Markdown references do not require move/delete/convert/commit operations in `tests/unit/test_materials_audit.py`
- [X] T018 [P] [US1] Add tests that ready-for-extraction-review audit records require topic or rule-family coverage, rights notes, source identity confidence, and source-library relationship or registration recommendation in `tests/unit/test_materials_audit.py`
- [X] T019 [P] [US1] Add tests that deferred, blocked, conflicting-identity, and high-risk audit records require durable reasons or risk notes in `tests/unit/test_materials_audit.py`

### Implementation for User Story 1

- [X] T020 [US1] Implement `load_material_audit_records()` and `load_material_representations()` validation in `src/mingli_engine/materials_audit.py`
- [X] T021 [US1] Seed initial audit records for the current nine root PDFs, Markdown batches 001-005, `资料整理/source_processing_status.md`, and `资料整理/knowledge_skeleton/` groups in `src/mingli_engine/data/materials_audit/material_audit_records.json`
- [X] T022 [US1] Seed material representations for root PDFs, prepared Markdown folders, cleaned Markdown folders, learning notes, processing-status notes, and knowledge-skeleton artifacts in `src/mingli_engine/data/materials_audit/material_representations.json`
- [X] T023 [US1] Implement material inventory progress counts by preparation state, representation type, source boundary, material scope, and risk tier in `src/mingli_engine/materials_audit.py`
- [X] T024 [US1] Document the existing-material inventory snapshot and raw-file non-mutation boundary in `docs/classical_sources/materials_audit.md`
- [X] T025 [US1] Update the maintainer workflow reference for materials audit in `docs/classical_sources/README.md`
- [X] T026 [US1] Run US1 focused validation with `tests/unit/test_materials_audit.py`

**Checkpoint**: US1 complete. Existing materials are visible as auditable preparation records, but none are candidate extracts or formal evidence.

---

## Phase 4: User Story 2 - Align Materials with the Source Library (Priority: P2)

**Goal**: Compare audited material groups with 014 source-library entries and make exact matches, likely matches, missing registrations, duplicates, edition variants, blocked entries, and out-of-scope materials visible.

**Independent Test**: Load alignment findings against current source-library data and verify every aligned record references an existing audit record, exact/likely matches reference source-library entries, and missing registrations include a registration recommendation.

### Tests for User Story 2

- [X] T027 [P] [US2] Add tests that source alignment findings load and reference existing audit records in `tests/unit/test_materials_audit.py`
- [X] T028 [P] [US2] Add tests that `exact` and `likely` alignment findings require existing 014 source-library entry ids from `src/mingli_engine/data/source_library/source_library_entries.json` in `tests/unit/test_materials_audit.py`
- [X] T029 [P] [US2] Add tests that `missing_source_library_entry` findings require registration recommendations in `tests/unit/test_materials_audit.py`
- [X] T030 [P] [US2] Add tests that duplicate, edition-variant, uncertain, blocked, and out-of-scope findings require explanatory notes in `tests/unit/test_materials_audit.py`
- [X] T031 [P] [US2] Add tests that source-library alignment does not mutate 014 source-library records in `src/mingli_engine/data/source_library/source_library_entries.json` in `tests/unit/test_materials_audit.py`

### Implementation for User Story 2

- [X] T032 [US2] Implement `load_source_alignment_findings()` and alignment validation in `src/mingli_engine/materials_audit.py`
- [X] T033 [US2] Implement audit-to-source-library alignment summary counts in `src/mingli_engine/materials_audit.py`
- [X] T034 [US2] Seed source alignment findings for the nine 014 registered source entries and selected Markdown/knowledge-skeleton groups in `src/mingli_engine/data/materials_audit/source_alignment_findings.json`
- [X] T035 [US2] Document exact matches, missing registrations, duplicate/variant handling, and out-of-scope deferral rules in `docs/classical_sources/materials_audit.md`
- [X] T036 [US2] Run US2 focused validation with `tests/unit/test_materials_audit.py`

**Checkpoint**: US2 complete. Existing material groups can be compared to 014 source-library records without silently merging uncertain sources.

---

## Phase 5: User Story 3 - Assess Extraction Readiness and Risk Boundaries (Priority: P3)

**Goal**: Classify each audited material as extraction-ready, needs cleaning, needs locator review, needs source registration, needs identity clarification, needs rights review, needs risk review, preparation backlog, deferred, or blocked.

**Independent Test**: Load readiness findings for materials in different states and verify each state has required reasons, high-risk labels, missing prerequisites, and next actions before extraction.

### Tests for User Story 3

- [X] T037 [P] [US3] Add tests that preparation readiness findings load and reference existing audit records in `tests/unit/test_materials_audit.py`
- [X] T038 [P] [US3] Add tests that extraction-ready findings require ready reasons, no blockers, locator confidence, source quality, risk boundary, and preconditions from audit records in `tests/unit/test_materials_audit.py`
- [X] T039 [P] [US3] Add tests that `needs_*`, `preparation_backlog`, `deferred`, and `blocked` readiness states require missing prerequisites or blockers in `tests/unit/test_materials_audit.py`
- [X] T040 [P] [US3] Add tests that high-risk readiness findings require risk-review notes and cannot be routine extraction work in `tests/unit/test_materials_audit.py`
- [X] T041 [P] [US3] Add safety tests that materials-audit readiness notes reject absolute destiny language, exact death/lifespan claims, medical/legal/psychological/investment instruction, coercive matching, anxiety creation, and paid-remedy upsells in `tests/safety/test_expanded_high_risk_language.py`
- [X] T042 [P] [US3] Add tests that cleaned Markdown and knowledge-skeleton artifacts remain preparation aids and never become formal report evidence in `tests/integration/test_report_regression_cases.py`

### Implementation for User Story 3

- [X] T043 [US3] Implement `load_preparation_readiness_findings()` and readiness validation in `src/mingli_engine/materials_audit.py`
- [X] T044 [US3] Implement readiness summary counts by state, text preparation status, locator confidence, source quality, risk boundary, and missing prerequisite in `src/mingli_engine/materials_audit.py`
- [X] T045 [US3] Implement materials-audit quality validation for long copied passages, absolute language, high-risk wording, and report-boundary exclusion in `src/mingli_engine/materials_audit.py`
- [X] T046 [US3] Seed readiness findings for extraction-ready, preparation-backlog, risk-review, deferred, blocked, and out-of-scope examples in `src/mingli_engine/data/materials_audit/preparation_readiness_findings.json`
- [X] T047 [US3] Document readiness states, risk-review boundaries, and out-of-scope deferral rules in `docs/classical_sources/materials_audit.md`
- [X] T048 [US3] Run US3 validation with `tests/unit/test_materials_audit.py`, `tests/integration/test_report_regression_cases.py`, and `tests/safety/test_expanded_high_risk_language.py`

**Checkpoint**: US3 complete. Materials are classified by preparation and risk readiness before any candidate extraction begins.

---

## Phase 6: User Story 4 - Produce the Next Candidate Extraction Queue (Priority: P4)

**Goal**: Produce a limited next-action queue that separates extraction-ready work from preparation, registration, risk-review, deferred, and blocked backlogs.

**Independent Test**: Load queue items and compute an audit progress summary, then verify the next recommended items have source-library relationship, readiness rationale, target rule family or gap, source quality note, risk boundary, and pre-extraction checks.

### Tests for User Story 4

- [X] T049 [P] [US4] Add tests that extraction queue items load and reference existing audit records in `tests/unit/test_materials_audit.py`
- [X] T050 [P] [US4] Add tests that extraction-ready queue items require source-library alignment, readiness rationale, target rule family or gap, risk boundary, and pre-extraction checks in `tests/unit/test_materials_audit.py`
- [X] T051 [P] [US4] Add tests that high-risk queue items require stricter risk-review prerequisites and clear priority rationale in `tests/unit/test_materials_audit.py`
- [X] T052 [P] [US4] Add tests that preparation, registration, risk-review, deferred, and blocked backlog items require missing prerequisites or reasons in `tests/unit/test_materials_audit.py`
- [X] T053 [P] [US4] Add tests that audit progress summaries include next five recommended queue item ids and separate ready/backlog/deferred/blocked counts in `tests/unit/test_materials_audit.py`
- [X] T054 [P] [US4] Add boundary regression tests that audit records and queue items are excluded from formal evidence counts in `tests/integration/test_report_regression_cases.py`

### Implementation for User Story 4

- [X] T055 [US4] Implement `load_extraction_queue_items()` and queue validation in `src/mingli_engine/materials_audit.py`
- [X] T056 [US4] Implement next-action selection by queue type, priority, readiness state, source-library alignment, target rule family, risk boundary, and missing prerequisite in `src/mingli_engine/materials_audit.py`
- [X] T057 [US4] Implement `build_materials_audit_progress_summary()` and `validate_materials_audit_quality()` in `src/mingli_engine/materials_audit.py`
- [X] T058 [US4] Seed extraction-ready, preparation-backlog, registration-backlog, risk-review-backlog, deferred, and blocked queue items in `src/mingli_engine/data/materials_audit/extraction_queue_items.json`
- [X] T059 [US4] Document the next-action queue, extraction-ready limits, and preparation backlog in `docs/classical_sources/materials_audit.md`
- [X] T060 [US4] Run US4 focused validation with `tests/unit/test_materials_audit.py` and `tests/integration/test_report_regression_cases.py`

**Checkpoint**: US4 complete. Maintainers can identify the next five safe extraction or preparation actions without opening every source file.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, docs cleanup, and implementation hygiene across all stories.

- [X] T061 [P] Update 015 quickstart validation notes after implementation in `specs/015-existing-materials-audit/quickstart.md`
- [X] T062 [P] Add materials-audit module export or package reference only if needed in `src/mingli_engine/__init__.py`
- [X] T063 [P] Review and tighten documentation links in `docs/classical_sources/README.md`, `docs/classical_sources/source_library.md`, `docs/classical_sources/intake.md`, and `docs/classical_sources/materials_audit.md`
- [X] T064 Run the quickstart materials-audit command from `specs/015-existing-materials-audit/quickstart.md`
- [X] T065 Run focused materials-audit tests with `tests/unit/test_materials_audit.py`
- [X] T066 Run boundary regression tests with `tests/unit/test_materials_audit.py`, `tests/unit/test_source_library.py`, `tests/unit/test_source_intake.py`, `tests/integration/test_report_regression_cases.py`, and `tests/safety/test_expanded_high_risk_language.py`
- [X] T067 Run full test suite declared in `pyproject.toml` with `uv run --with pytest python -m pytest`
- [X] T068 Update task completion statuses in `specs/015-existing-materials-audit/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; MVP scope.
- **Phase 4 US2**: Depends on Phase 2 and benefits from US1 audit records.
- **Phase 5 US3**: Depends on Phase 2 and benefits from US1/US2 alignment data.
- **Phase 6 US4**: Depends on Phase 2 and needs US1-US3 data for useful queue recommendations.
- **Phase 7 Polish**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational and is the recommended MVP.
- **US2 (P2)**: Can start after Foundational, but seeded alignment findings depend on audit records from US1.
- **US3 (P3)**: Can start after Foundational, but meaningful readiness findings depend on audit records and alignment findings.
- **US4 (P4)**: Can start after Foundational, but next-action queue quality depends on audit, alignment, and readiness data.

### Within Each User Story

- Tests must be written first and observed failing before implementation.
- Shared constants and models precede loaders.
- Loaders precede progress summaries and queue computation.
- Data seeds follow validation rules.
- Documentation updates follow working validation logic.

---

## Parallel Opportunities

- Setup tasks T002-T005 can run in parallel.
- Foundational tests T006, T009, and T011 can run in parallel before implementation.
- US1 tests T014-T019 can run in parallel.
- US2 tests T027-T031 can run in parallel.
- US3 tests T037-T042 can run in parallel.
- US4 tests T049-T054 can run in parallel.
- Documentation-only polish tasks T061 and T063 can run in parallel after implementation.

## Parallel Example: User Story 1

```text
Task: "T014 Add tests that valid material audit records and representations load from src/mingli_engine/data/materials_audit/material_audit_records.json and src/mingli_engine/data/materials_audit/material_representations.json in tests/unit/test_materials_audit.py"
Task: "T015 Add tests that duplicate audit_id, duplicate representation_id, invalid material scope, invalid representation type, invalid source boundary, invalid preparation state, and invalid next action fail validation in tests/unit/test_materials_audit.py"
Task: "T017 Add tests that external_untracked root PDF, raw folder, and root Markdown references do not require move/delete/convert/commit operations in tests/unit/test_materials_audit.py"
```

## Parallel Example: User Story 2

```text
Task: "T027 Add tests that source alignment findings load and reference existing audit records in tests/unit/test_materials_audit.py"
Task: "T028 Add tests that exact and likely alignment findings require existing 014 source-library entry ids from src/mingli_engine/data/source_library/source_library_entries.json in tests/unit/test_materials_audit.py"
Task: "T030 Add tests that duplicate, edition-variant, uncertain, blocked, and out-of-scope findings require explanatory notes in tests/unit/test_materials_audit.py"
```

## Parallel Example: User Story 3

```text
Task: "T037 Add tests that preparation readiness findings load and reference existing audit records in tests/unit/test_materials_audit.py"
Task: "T041 Add safety tests that materials-audit readiness notes reject absolute destiny language, exact death/lifespan claims, medical/legal/psychological/investment instruction, coercive matching, anxiety creation, and paid-remedy upsells in tests/safety/test_expanded_high_risk_language.py"
Task: "T042 Add tests that cleaned Markdown and knowledge-skeleton artifacts remain preparation aids and never become formal report evidence in tests/integration/test_report_regression_cases.py"
```

## Parallel Example: User Story 4

```text
Task: "T049 Add tests that extraction queue items load and reference existing audit records in tests/unit/test_materials_audit.py"
Task: "T050 Add tests that extraction-ready queue items require source-library alignment, readiness rationale, target rule family or gap, risk boundary, and pre-extraction checks in tests/unit/test_materials_audit.py"
Task: "T054 Add boundary regression tests that audit records and queue items are excluded from formal evidence counts in tests/integration/test_report_regression_cases.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1.
4. Stop and validate material inventory independently.
5. Report next step before continuing to US2.

### Incremental Delivery

1. US1 creates an auditable existing-material inventory.
2. US2 aligns the inventory with 014 source-library entries and registration gaps.
3. US3 classifies extraction readiness and high-risk boundaries.
4. US4 produces the next extraction/preparation queue.
5. Polish verifies quickstart, focused tests, boundary tests, and full suite.

### Stage Reporting

- Report after Phase 2 before starting US1 implementation.
- Report after each user story checkpoint.
- Do not proceed from one user story to the next without a short status summary and next-step prompt.

## Notes

- Root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials.
- 015 does not perform automatic extraction, OCR, runtime PDF parsing, automatic evidence approval, or report generation.
- Audit records, readiness findings, alignment findings, and queue items are planning metadata, not candidate extracts or formal report evidence.
- Use `apply_patch` for manual file edits during implementation.
