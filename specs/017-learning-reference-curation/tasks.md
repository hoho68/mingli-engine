# Tasks: Learning Reference Curation

**Input**: Design documents from `/specs/017-learning-reference-curation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/learning-reference-curation-contract.md, quickstart.md

**Tests**: Required. 017 turns source-preparation metadata into learning reference data and candidate-intake decisions, so tasks include test-first validation for learning notes, learning points, candidate decisions, prerequisite action notes, duplicate/overlap handling, high-risk wording, raw-file non-mutation, and report-boundary preservation.

**Organization**: Tasks are grouped by user story to enable independent implementation and staged validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches separate files or independent fixtures.
- **[Story]**: User story label for story phases only.
- Every task includes exact repository file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create learning-reference curation scaffolding, data placeholders, and documentation placeholders.

- [X] T001 Create learning-reference data directory and placeholder in `src/mingli_engine/data/learning_reference_curation/.gitkeep`
- [X] T002 [P] Create empty JSON array data files in `src/mingli_engine/data/learning_reference_curation/learning_reference_notes.json`, `src/mingli_engine/data/learning_reference_curation/learning_points.json`, `src/mingli_engine/data/learning_reference_curation/candidate_intake_decisions.json`, and `src/mingli_engine/data/learning_reference_curation/prerequisite_action_notes.json`
- [X] T003 [P] Create maintainer documentation skeleton in `docs/classical_sources/learning_reference_curation.md`
- [X] T004 [P] Create learning reference curation module skeleton in `src/mingli_engine/learning_reference_curation.py`
- [X] T005 [P] Create focused test file skeleton in `tests/unit/test_learning_reference_curation.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared constants, models, loaders, validators, and helper contracts that all user stories depend on.

**Critical**: No user story work should begin until this phase is complete.

- [X] T006 [P] Add learning-reference constant validation tests in `tests/unit/test_learning_reference_curation.py`
- [X] T007 Add learning reference note status, learning point readiness, candidate decision type, candidate decision status, prerequisite action type, prerequisite action status, and manual next-action constants in `src/mingli_engine/models.py`
- [X] T008 Add `LearningReferenceNote`, `LearningPoint`, `CandidateIntakeDecision`, `PrerequisiteActionNote`, and `LearningReferenceProgressSummary` dataclasses in `src/mingli_engine/models.py`
- [X] T009 [P] Add JSON loader error-handling tests for missing, malformed, non-array, and non-object learning-reference files in `tests/unit/test_learning_reference_curation.py`
- [X] T010 Implement `LearningReferenceCurationError`, data-directory resolution, JSON list readers, unique-id checks, enum validators, and shared string/list validators in `src/mingli_engine/learning_reference_curation.py`
- [X] T011 [P] Add fixture builders for temporary learning-reference data plus sibling 016/015/014/013/classical-source data in `tests/unit/test_learning_reference_curation.py`
- [X] T012 Add public loader stubs for learning reference notes, learning points, candidate decisions, prerequisite action notes, progress summaries, and quality validation in `src/mingli_engine/learning_reference_curation.py`
- [X] T013 [P] Add performance smoke test for learning reference summary loading under 300 ms in `tests/unit/test_learning_reference_curation.py`
- [X] T014 Run the focused test target and confirm foundational tests fail before story implementation with `tests/unit/test_learning_reference_curation.py`

**Checkpoint**: Foundation ready. Learning reference models and loader helpers exist, and user stories can be implemented incrementally.

---

## Phase 3: User Story 1 - Create Learning Reference Notes From Ready Tasks (Priority: P1) MVP

**Goal**: Convert the initial two ready 016 extraction tasks into readable learning reference notes with source trace, rule-family targets, limitations, overlap visibility, and no formal-evidence promotion.

**Independent Test**: Load the initial 017 learning notes and verify the first two ready 016 tasks have notes with trace links, learning point ids, source boundaries, risk boundaries, and no long copied passages.

### Tests for User Story 1

- [X] T015 [P] [US1] Add tests that valid learning reference notes load from `src/mingli_engine/data/learning_reference_curation/learning_reference_notes.json` in `tests/unit/test_learning_reference_curation.py`
- [X] T016 [P] [US1] Add tests that duplicate `note_id`, invalid note status, invalid risk boundary, invalid locator requirement, unsupported rule family, and missing learning point ids fail validation in `tests/unit/test_learning_reference_curation.py`
- [X] T017 [P] [US1] Add tests that every learning reference note references an existing 016 extraction task, package, 015 queue item, 015 audit record, 014 source-library entry, and 013 source material in `tests/unit/test_learning_reference_curation.py`
- [X] T018 [P] [US1] Add tests that only 016 extraction tasks, not prerequisite backlog records, can become learning reference notes in `tests/unit/test_learning_reference_curation.py`
- [X] T019 [P] [US1] Add tests that learning notes preserve 016 overlap candidate ids and reject unknown overlap candidate ids in `tests/unit/test_learning_reference_curation.py`
- [X] T020 [P] [US1] Add tests that learning-note loading does not mutate 016 extraction package data, 015 materials-audit data, 014 source-library data, or 013 source-intake data in `tests/unit/test_learning_reference_curation.py`
- [X] T021 [P] [US1] Add tests that learning notes reject long copied passages, extracted-meaning leakage, review-state leakage, promotion-state leakage, and formal-evidence wording in `tests/unit/test_learning_reference_curation.py`

### Implementation for User Story 1

- [X] T022 [US1] Implement `load_learning_reference_notes()` validation in `src/mingli_engine/learning_reference_curation.py`
- [X] T023 [US1] Implement cross-checks from learning notes to 016 tasks/packages, 015 queue/audit records, 014 source-library entries, and 013 source materials in `src/mingli_engine/learning_reference_curation.py`
- [X] T024 [US1] Implement overlap candidate id validation against existing 013 candidate records in `src/mingli_engine/learning_reference_curation.py`
- [X] T025 [US1] Seed learning reference notes for `task_northeast_blind_peak_extract_001` and `task_mingli_true_formula_teacher_extract_001` in `src/mingli_engine/data/learning_reference_curation/learning_reference_notes.json`
- [X] T026 [US1] Update `docs/classical_sources/extracts/northeast_blind_peak.md` with a 017 learning-reference section for source trace, learning scope, limitations, and overlap warnings
- [X] T027 [US1] Update `docs/classical_sources/extracts/mingli_true_formula_teacher.md` with a 017 learning-reference section for source trace, learning scope, limitations, and candidate-intake readiness
- [X] T028 [US1] Implement learning-reference quality validation for copied-passage limits, extracted-meaning leakage, review-state leakage, promotion-state leakage, report-evidence wording, absolute language, and high-risk wording in `src/mingli_engine/learning_reference_curation.py`
- [X] T029 [US1] Implement learning note progress counts by note status, risk tier, target rule family, and selected 016 task ids in `src/mingli_engine/learning_reference_curation.py`
- [X] T030 [US1] Document learning-note boundaries in `docs/classical_sources/learning_reference_curation.md`
- [X] T031 [US1] Update maintainer workflow links for 017 in `docs/classical_sources/README.md`, `docs/classical_sources/extraction_queue_intake.md`, and `docs/classical_sources/intake.md`
- [X] T032 [US1] Run US1 focused validation with `tests/unit/test_learning_reference_curation.py`

**Checkpoint**: US1 complete. The initial two ready 016 tasks are visible as learning reference notes, but no 013 candidate extracts or formal evidence are created.

---

## Phase 4: User Story 2 - Convert Approved Learning Points Into Candidate Extracts (Priority: P2)

**Goal**: Add learning points and candidate-intake decisions that describe which points should create, reuse, avoid, defer, or require manual review before touching 013 candidate records.

**Independent Test**: Inspect learning points and candidate-intake decisions to confirm candidate-ready points have source material, locator, rule family, risk tier, limitations, duplicate decisions, and no formal evidence effects.

### Tests for User Story 2

- [X] T033 [P] [US2] Add tests that learning points load and reference existing learning reference notes in `tests/unit/test_learning_reference_curation.py`
- [X] T034 [P] [US2] Add tests that learning points require source locator or locator requirement, summary, proposed rule family, risk tier, limitations, and candidate readiness in `tests/unit/test_learning_reference_curation.py`
- [X] T035 [P] [US2] Add tests that sensitive and high-risk learning points require uncertainty and limitation language in `tests/unit/test_learning_reference_curation.py`
- [X] T036 [P] [US2] Add tests that candidate-intake decisions load and reference existing learning points in `tests/unit/test_learning_reference_curation.py`
- [X] T037 [P] [US2] Add tests that `create_candidate` decisions require candidate-ready learning point metadata and do not allow duplicate-review points to create candidates without manual review in `tests/unit/test_learning_reference_curation.py`
- [X] T038 [P] [US2] Add tests that `reuse_existing` and `avoid_duplicate` decisions require existing overlap candidate ids in `tests/unit/test_learning_reference_curation.py`
- [X] T039 [P] [US2] Add tests that candidate-intake decisions reject review decisions, approval status, promotion status, and formal-evidence wording in `tests/unit/test_learning_reference_curation.py`
- [X] T040 [P] [US2] Add boundary regression tests that learning points and candidate-intake decisions do not change 013 candidate counts or formal evidence counts in `tests/integration/test_report_regression_cases.py`
- [X] T041 [P] [US2] Add safety tests that learning point summaries and candidate-decision rationales reject absolute destiny language, exact death/lifespan claims, medical/legal/psychological/investment instruction, coercive matching, anxiety creation, and paid-remedy upsells in `tests/safety/test_expanded_high_risk_language.py`

### Implementation for User Story 2

- [X] T042 [US2] Implement `load_learning_points()` and learning-point validation for `src/mingli_engine/data/learning_reference_curation/learning_points.json` in `src/mingli_engine/learning_reference_curation.py`
- [X] T043 [US2] Cross-check `learning_reference_notes.json` learning point ids against `learning_points.json` in `src/mingli_engine/learning_reference_curation.py`
- [X] T044 [US2] Implement `load_candidate_intake_decisions()` and candidate-decision validation in `src/mingli_engine/learning_reference_curation.py`
- [X] T045 [US2] Implement decision cross-checks to existing 013 candidate records and source materials in `src/mingli_engine/learning_reference_curation.py`
- [X] T046 [US2] Seed learning points for the two current learning reference notes in `src/mingli_engine/data/learning_reference_curation/learning_points.json`
- [X] T047 [US2] Seed candidate-intake decisions in `src/mingli_engine/data/learning_reference_curation/candidate_intake_decisions.json`
- [X] T048 [US2] Update readable learning reference sections in `docs/classical_sources/extracts/northeast_blind_peak.md` and `docs/classical_sources/extracts/mingli_true_formula_teacher.md` with learning point ids and candidate-intake decisions
- [X] T049 [US2] Implement progress counts by learning point readiness, candidate decision type, candidate decision status, candidate-ready count, and overlap warning count in `src/mingli_engine/learning_reference_curation.py`
- [X] T050 [US2] Finalize quality validation for learning-point and candidate-decision boundary text in `src/mingli_engine/learning_reference_curation.py`
- [X] T051 [US2] Document candidate-intake decision boundaries in `docs/classical_sources/learning_reference_curation.md`
- [X] T052 [US2] Run US2 validation with `tests/unit/test_learning_reference_curation.py`, `tests/integration/test_report_regression_cases.py`, and `tests/safety/test_expanded_high_risk_language.py`

**Checkpoint**: US2 complete. Learning points and decisions are visible and validated, but candidate creation remains explicit and formal evidence counts are unchanged.

---

## Phase 5: User Story 3 - Preserve Backlog As Prerequisite Work (Priority: P3)

**Goal**: Convert non-ready 016 backlog records into prerequisite action notes so registration, risk-review, and blocked-source work remains visible without becoming learning points or candidates.

**Independent Test**: Load prerequisite action notes and verify current 016 backlog records are represented as actions with missing prerequisites, durable reasons, recommended action, risk boundary, and no candidate or formal evidence effects.

### Tests for User Story 3

- [X] T053 [P] [US3] Add tests that prerequisite action notes load and reference existing 016 backlog records, packages, 015 queue items, and 015 audit records in `tests/unit/test_learning_reference_curation.py`
- [X] T054 [P] [US3] Add tests that registration, preparation, locator-review, risk-review, deferred, and blocked action notes require missing prerequisites or durable reasons in `tests/unit/test_learning_reference_curation.py`
- [X] T055 [P] [US3] Add tests that risk-review, deferred, and blocked action notes cannot create candidate-intake decisions or learning points in `tests/unit/test_learning_reference_curation.py`
- [X] T056 [P] [US3] Add tests that prerequisite action notes preserve recommended actions and risk boundaries from 016 backlog records in `tests/unit/test_learning_reference_curation.py`
- [X] T057 [P] [US3] Add tests that learning reference progress summaries include note counts, learning point counts, decision counts, prerequisite action counts, risk-tier counts, overlap warning counts, candidate-ready counts, formal evidence delta, and next action ids in `tests/unit/test_learning_reference_curation.py`
- [X] T058 [P] [US3] Add boundary regression tests that learning notes, learning points, candidate decisions, and prerequisite action notes do not change formal evidence counts in `tests/integration/test_report_regression_cases.py`

### Implementation for User Story 3

- [X] T059 [US3] Implement `load_prerequisite_action_notes()` and action-note validation in `src/mingli_engine/learning_reference_curation.py`
- [X] T060 [US3] Implement prerequisite action routing checks from 017 action notes to 016 backlog records in `src/mingli_engine/learning_reference_curation.py`
- [X] T061 [US3] Seed prerequisite action notes for current registration, risk-review, and blocked 016 backlog records in `src/mingli_engine/data/learning_reference_curation/prerequisite_action_notes.json`
- [X] T062 [US3] Implement `build_learning_reference_progress_summary()` and finalize `validate_learning_reference_quality()` in `src/mingli_engine/learning_reference_curation.py`
- [X] T063 [US3] Document prerequisite action routing, blocked work, and report-evidence boundaries in `docs/classical_sources/learning_reference_curation.md`
- [X] T064 [US3] Run US3 validation with `tests/unit/test_learning_reference_curation.py` and `tests/integration/test_report_regression_cases.py`

**Checkpoint**: US3 complete. Backlog work remains visible without entering learning points, candidate records, or formal evidence.

---

## Phase 6: Optional Candidate Data Application (Requires Explicit Confirmation)

**Purpose**: Apply selected `create_candidate` decisions to 013 candidate data only after the user confirms which decisions should be applied.

- [X] T065 [P] [US2] Add tests for applying approved `create_candidate` decisions into `src/mingli_engine/data/source_intake/candidate_extracts.json` in `tests/unit/test_learning_reference_curation.py`
- [X] T066 [US2] Implement candidate application helper or manual data update path in `src/mingli_engine/learning_reference_curation.py` only for explicitly selected decisions
- [X] T067 [US2] Update `src/mingli_engine/data/source_intake/candidate_extracts.json` only for confirmed `create_candidate` decisions
- [X] T068 [US2] Add matching review-decision placeholders only if explicitly requested in `src/mingli_engine/data/source_intake/review_decisions.json`
- [X] T069 [US2] Run candidate-application validation with `tests/unit/test_learning_reference_curation.py` and `tests/unit/test_source_intake.py`

**Checkpoint**: Candidate application is intentionally separate from learning-reference creation so 017 can produce useful study data before mutating 013 candidate records.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, docs cleanup, and implementation hygiene across all 017 stories.

- [X] T070 [P] Update 017 quickstart validation notes after implementation in `specs/017-learning-reference-curation/quickstart.md`
- [X] T071 [P] Add module export or package reference only if needed in `src/mingli_engine/__init__.py`
- [X] T072 [P] Review and tighten documentation links in `docs/classical_sources/README.md`, `docs/classical_sources/source_library.md`, `docs/classical_sources/intake.md`, `docs/classical_sources/materials_audit.md`, `docs/classical_sources/extraction_queue_intake.md`, and `docs/classical_sources/learning_reference_curation.md`
- [X] T073 Run the quickstart learning reference command from `specs/017-learning-reference-curation/quickstart.md`
- [X] T074 Run focused learning reference tests with `tests/unit/test_learning_reference_curation.py`
- [X] T075 Run boundary regression tests with `tests/unit/test_learning_reference_curation.py`, `tests/unit/test_extraction_queue_intake.py`, `tests/unit/test_source_intake.py`, `tests/integration/test_report_regression_cases.py`, and `tests/safety/test_expanded_high_risk_language.py`
- [X] T076 Run full test suite declared in `pyproject.toml` with `uv run --with pytest python -m pytest`
- [X] T077 Update task completion statuses in `specs/017-learning-reference-curation/tasks.md`

---

## Phase 8: Incremental Ready Queue Extension

**Goal**: Extend the 016/017 learning-reference chain to the next ordinary ready 015 queue item without creating candidates or formal evidence.

- [X] T078 [P] Add red tests that require `queue_duan_plain_mingxue_outline_extract` to appear as a 016 package, extraction task, and candidate draft slot in `tests/unit/test_extraction_queue_intake.py`
- [X] T079 [P] Add red tests that require a Duan learning note, learning point, and candidate-intake decision in `tests/unit/test_learning_reference_curation.py`
- [X] T080 Add `package_next_candidates_002`, `task_duan_plain_mingxue_outline_extract_001`, and `slot_duan_ten_god_relation_001` in `src/mingli_engine/data/extraction_queue_intake/`
- [X] T081 Add `note_duan_plain_mingxue_outline_001`, `lp_duan_ten_god_relation_001`, and `decision_duan_ten_god_relation_001` in `src/mingli_engine/data/learning_reference_curation/`
- [X] T082 Update 017 quickstart, maintainer docs, and Duan extract notes for the incremental ready task
- [X] T083 Run focused 016/017 validation for the incremental ready task
- [X] T084 Run boundary and full test validation after the incremental ready task update

---

## Phase 9: Remaining Queue Coverage

**Goal**: Ensure every remaining 015 queue item has a 016/017 disposition: ready items become learning-reference inputs and non-ready items remain prerequisite work.

- [X] T085 [P] Add red tests requiring `Mingxue Golden Voice` and `Fortune Reading Hongfu Qitian` to appear as 016 tasks, draft slots, learning notes, learning points, and candidate-intake decisions
- [X] T086 [P] Add red tests requiring the remaining registration, locator-review, risk-review, deferred, and preparation queue items to appear as 016 backlog records and 017 prerequisite action notes
- [X] T087 Add `package_next_candidates_003`, remaining ready extraction tasks, draft slots, and prerequisite backlog records in `src/mingli_engine/data/extraction_queue_intake/`
- [X] T088 Add remaining learning notes, learning points, candidate-intake decisions, and prerequisite action notes in `src/mingli_engine/data/learning_reference_curation/`
- [X] T089 Update 017 quickstart, maintainer docs, and extract notes for the remaining queue coverage
- [X] T090 Run focused 016/017 validation for remaining queue coverage
- [X] T091 Run boundary and full test validation after remaining queue coverage
- [X] T092 Update task completion statuses in `specs/017-learning-reference-curation/tasks.md`

---

## Phase 10: Authorized Candidate-Application Closure

**Goal**: Apply the user-authorized candidate-intake decisions, preserve reuse/duplicate boundaries, and refresh computed documentation without changing formal evidence.

- [X] T093 [P] Add red tests for mixed `reuse_existing` and `create_candidate` application behavior in `tests/unit/test_learning_reference_curation.py`
- [X] T094 [P] Add red seeded-data tests for applied decision statuses, overlap warnings, candidate ids, and summary counts in `tests/unit/test_learning_reference_curation.py` and `tests/unit/test_extraction_queue_intake.py`
- [X] T095 Implement actionable decision application support for `reuse_existing`, `avoid_duplicate`, and `create_candidate` in `src/mingli_engine/learning_reference_curation.py`
- [X] T096 Update applied 017 decisions, learning-point readiness, learning-note overlaps, 016 overlap warnings, and confirmed 013 candidate extracts in `src/mingli_engine/data/`
- [X] T097 Update 017 quickstart, 016/017 maintainer docs, 013 intake snapshot, and per-source extract notes for the authorized applied decisions
- [X] T098 Run focused validation for learning reference, extraction queue, source intake, and report regression tests
- [X] T099 Run boundary and full test validation after authorized candidate application
- [X] T100 Update task completion statuses in `specs/017-learning-reference-curation/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; MVP scope.
- **Phase 4 US2**: Depends on Phase 2 and benefits from US1 learning notes.
- **Phase 5 US3**: Depends on Phase 2 and benefits from US1/US2 summary integration.
- **Phase 6 Candidate Data Application**: Depends on US2 and explicit user confirmation.
- **Phase 7 Polish**: Depends on selected user stories being complete.
- **Phase 8 Incremental Ready Queue Extension**: Depends on 015 ready queue data and the established 016/017 validation chain.
- **Phase 9 Remaining Queue Coverage**: Depends on Phase 8 and closes the audited 015 queue disposition.
- **Phase 10 Authorized Candidate-Application Closure**: Depends on explicit user authorization and updates selected 013 pending-review candidates while preserving formal-evidence boundaries.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational and is the recommended MVP.
- **US2 (P2)**: Can start after Foundational, but seeded decisions depend on learning notes from US1.
- **US3 (P3)**: Can start after Foundational, but useful summaries depend on US1/US2 data.

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
- US1 tests T015-T021 can run in parallel.
- US2 tests T033-T041 can run in parallel.
- US3 tests T053-T058 can run in parallel.
- Documentation-only polish tasks T070 and T072 can run in parallel after implementation.

## Parallel Example: User Story 1

```text
Task: "T015 Add tests that valid learning reference notes load from src/mingli_engine/data/learning_reference_curation/learning_reference_notes.json in tests/unit/test_learning_reference_curation.py"
Task: "T017 Add tests that every learning reference note references an existing 016 extraction task, package, 015 queue item, 015 audit record, 014 source-library entry, and 013 source material in tests/unit/test_learning_reference_curation.py"
Task: "T020 Add tests that learning-note loading does not mutate 016 extraction package data, 015 materials-audit data, 014 source-library data, or 013 source-intake data in tests/unit/test_learning_reference_curation.py"
```

## Parallel Example: User Story 2

```text
Task: "T033 Add tests that learning points load and reference existing learning reference notes in tests/unit/test_learning_reference_curation.py"
Task: "T036 Add tests that candidate-intake decisions load and reference existing learning points in tests/unit/test_learning_reference_curation.py"
Task: "T040 Add boundary regression tests that learning points and candidate-intake decisions do not change 013 candidate counts or formal evidence counts in tests/integration/test_report_regression_cases.py"
```

## Parallel Example: User Story 3

```text
Task: "T053 Add tests that prerequisite action notes load and reference existing 016 backlog records, packages, 015 queue items, and 015 audit records in tests/unit/test_learning_reference_curation.py"
Task: "T055 Add tests that risk-review, deferred, and blocked action notes cannot create candidate-intake decisions or learning points in tests/unit/test_learning_reference_curation.py"
Task: "T058 Add boundary regression tests that learning notes, learning points, candidate decisions, and prerequisite action notes do not change formal evidence counts in tests/integration/test_report_regression_cases.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1.
4. Stop and validate learning-note creation independently.
5. Report next step before continuing to US2.

### Incremental Delivery

1. US1 creates readable learning notes from the initial two ready 016 tasks.
2. US2 adds learning points and candidate-intake decisions without applying candidate data unless explicitly confirmed.
3. US3 preserves non-ready backlog work as prerequisite action notes.
4. Optional Phase 6 applies confirmed candidate creation decisions to 013 data.
5. Polish verifies quickstart, focused tests, boundary tests, and full suite.
6. Phase 8 extends the same chain to the next ordinary ready queue item.
7. Phase 9 closes remaining ready and non-ready queue coverage without creating new candidates.
8. Phase 10 applies explicitly authorized candidate-intake decisions and refreshes validation/documentation snapshots.

### Stage Reporting

- Report after Phase 2 before starting US1 implementation.
- Report after each user story checkpoint.
- Do not apply candidate data in Phase 6 without explicit user confirmation.

## Notes

- Root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials.
- 017 does not perform automatic extraction, OCR, runtime PDF parsing, automatic evidence approval, or report generation.
- Learning reference notes, learning points, candidate-intake decisions, and prerequisite action notes are learning/reference metadata, not formal report evidence.
- Use `apply_patch` for manual file edits during implementation.
