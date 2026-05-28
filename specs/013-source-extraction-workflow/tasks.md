# Tasks: Source Extraction Workflow

**Input**: Design documents from `specs/013-source-extraction-workflow/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/source-extraction-workflow-contract.md`, `quickstart.md`

**Tests**: Required. This feature changes evidence intake and report evidence boundaries, so tests must be written before implementation for loaders, validation, high-risk handling, promotion readiness, progress summaries, and report-boundary regression.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently. Root PDF files and root `Markdown/` remain external user materials throughout this task list.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other tasks in the same phase when files do not overlap
- **[Story]**: User story label for story phases only
- Every task includes exact project-relative file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the 013 workspace paths without implementing behavior.

- [X] T001 Create `src/mingli_engine/data/source_intake/.gitkeep` so the intake data directory exists without adding raw PDF or Markdown materials
- [X] T002 [P] Create `docs/classical_sources/intake.md` with an initial "source intake progress" heading and a note that root source materials remain external
- [X] T003 [P] Create `src/mingli_engine/source_intake.py` with module docstring only for the future deterministic intake loader
- [X] T004 Verify `git status --short --branch` still shows root PDF files and root `Markdown/` as untracked inputs, not staged project data

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared intake model types, constants, base JSON loading, and empty intake data files. This phase blocks all user stories.

**CRITICAL**: No user story work begins until this phase is complete.

- [X] T005 [P] Add failing tests for source-intake constants and dataclass construction in `tests/unit/test_source_intake.py`
- [X] T006 Add source-intake constants plus `SourceMaterial`, `CandidateExtract`, `ReviewDecision`, `PromotionBatch`, and `IntakeProgressReport` dataclasses in `src/mingli_engine/models.py`
- [X] T007 [P] Add failing tests for missing intake JSON files, invalid JSON, non-array payloads, and duplicate id detection in `tests/unit/test_source_intake.py`
- [X] T008 Implement `SourceIntakeError`, `_read_json_list()`, `_read_optional_json_list()`, `_require_text()`, `_require_string_list()`, `_ensure_unique()`, and `_data_dir()` in `src/mingli_engine/source_intake.py`
- [X] T009 Create empty JSON arrays in `src/mingli_engine/data/source_intake/source_materials.json`, `src/mingli_engine/data/source_intake/candidate_extracts.json`, `src/mingli_engine/data/source_intake/review_decisions.json`, and `src/mingli_engine/data/source_intake/promotion_batches.json`
- [X] T010 Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py` and confirm the foundational tests pass

**Checkpoint**: Foundation ready. Story work can begin.

---

## Phase 3: User Story 1 - Register Candidate Extracts (Priority: P1) MVP

**Goal**: Maintainers can register external source materials and candidate extracts without making candidates report-usable.

**Independent Test**: Register source materials and pending candidates in intake JSON, load them successfully, reject incomplete candidates, and verify formal evidence loading does not include candidate extracts.

### Tests for User Story 1

- [X] T011 [P] [US1] Add failing tests for valid and invalid `SourceMaterial` records in `tests/unit/test_source_intake.py`
- [X] T012 [US1] Implement `load_source_materials()` and source material validation in `src/mingli_engine/source_intake.py`
- [X] T013 [US1] Add nine current source-material registry records with `tracking_status=external_untracked` in `src/mingli_engine/data/source_intake/source_materials.json`
- [X] T014 [P] [US1] Add failing tests for candidate required fields, pending-review eligibility, and invalid statuses in `tests/unit/test_source_intake.py`
- [X] T015 [US1] Implement `load_candidate_extracts()` and candidate field/status validation in `src/mingli_engine/source_intake.py`
- [X] T016 [US1] Add seed pending candidate records in `src/mingli_engine/data/source_intake/candidate_extracts.json` without copying long source passages
- [X] T017 [P] [US1] Add failing tests that candidate `extracted_meaning` and `short_quote` reject long copied passages and absolute outcome language in `tests/unit/test_source_intake.py`
- [X] T018 [US1] Implement concise-text and prohibited-phrase validation for candidate records in `src/mingli_engine/source_intake.py`
- [X] T019 [P] [US1] Add a report-boundary regression test proving pending candidates are excluded from formal evidence loading in `tests/integration/test_report_regression_cases.py`
- [X] T020 [US1] Preserve the report evidence boundary by keeping `src/mingli_engine/classical_sources.py` independent from `src/mingli_engine/data/source_intake/candidate_extracts.json`
- [X] T021 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py tests/integration/test_report_regression_cases.py`

**Checkpoint**: US1 is independently usable as the MVP intake queue.

---

## Phase 4: User Story 2 - Review Candidate Evidence (Priority: P2)

**Goal**: Reviewers can approve, return, reject, or block candidates with explicit review metadata, and only approved candidates can enter promotion readiness.

**Independent Test**: Add review decisions for candidates, verify required metadata per decision type, enforce high-risk limitations, and validate promotion batches only include approved candidates.

### Tests for User Story 2

- [X] T022 [P] [US2] Add failing tests for approved, returned, rejected, and blocked review decision requirements in `tests/unit/test_source_intake.py`
- [X] T023 [US2] Implement `load_review_decisions()` and review decision validation in `src/mingli_engine/source_intake.py`
- [X] T024 [US2] Add seed review decision records covering approved, returned, rejected, and blocked outcomes in `src/mingli_engine/data/source_intake/review_decisions.json`
- [X] T025 [P] [US2] Add failing tests that approved high-risk candidates require approval limitations and cannot use `source_quality=needs_recheck` in `tests/unit/test_source_intake.py`
- [X] T026 [US2] Implement high-risk approval, source quality, confidence, and approved-decision cross-reference checks in `src/mingli_engine/source_intake.py`
- [X] T027 [P] [US2] Add failing tests for promotion batch validation and approved-candidate membership in `tests/unit/test_source_intake.py`
- [X] T028 [US2] Implement `load_promotion_batches()` and promotion batch validation in `src/mingli_engine/source_intake.py`
- [X] T029 [US2] Add seed promotion batch records in `src/mingli_engine/data/source_intake/promotion_batches.json`
- [X] T030 [US2] Implement `list_approved_candidates_for_promotion()` in `src/mingli_engine/source_intake.py`
- [X] T031 [US2] Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`

**Checkpoint**: US2 can review candidates and identify promotion-ready approved candidates without changing formal evidence.

---

## Phase 5: User Story 3 - Record Conflicts, Gaps, and Rejections (Priority: P3)

**Goal**: Reviewers can preserve duplicate, conflict, gap, rejection, and blocked reasons as audit metadata.

**Independent Test**: Load candidates linked to existing evidence, source conflicts, and gaps; reject invalid links; preserve rejection/blocking reasons; and flag likely duplicates.

### Tests for User Story 3

- [X] T032 [P] [US3] Add failing tests for duplicate candidate detection using `material_id`, `source_locator`, `proposed_rule_family`, and `extracted_meaning` in `tests/unit/test_source_intake.py`
- [X] T033 [US3] Implement `find_duplicate_candidates()` in `src/mingli_engine/source_intake.py`
- [X] T034 [P] [US3] Add failing tests for candidate links to existing evidence ids, source conflict ids, and curation gap ids in `tests/unit/test_source_intake.py`
- [X] T035 [US3] Implement `validate_candidate_links()` using existing 012 evidence units, source conflicts, and derived curation gaps in `src/mingli_engine/source_intake.py`
- [X] T036 [P] [US3] Add failing tests that rejected and blocked review decisions require durable reasons in `tests/unit/test_source_intake.py`
- [X] T037 [US3] Strengthen rejected and blocked reason validation in `src/mingli_engine/source_intake.py`
- [X] T038 [US3] Add representative duplicate, conflict-linked, gap-linked, rejected, and blocked examples to `src/mingli_engine/data/source_intake/candidate_extracts.json` and `src/mingli_engine/data/source_intake/review_decisions.json`
- [X] T039 [US3] Add conflict/gap intake notes to `docs/classical_sources/intake.md`
- [X] T040 [US3] Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`

**Checkpoint**: US3 makes non-promoted material auditable without allowing unsafe or disputed material into reports.

---

## Phase 6: User Story 4 - View Intake Progress (Priority: P4)

**Goal**: Maintainers can see intake progress by source material, candidate status, rule family, risk tier, approval readiness, duplicates, conflicts, and gaps.

**Independent Test**: Build a progress report from intake data and verify it separates pending, approved, promoted, rejected, blocked, duplicate, conflict-linked, and gap-linked counts.

### Tests for User Story 4

- [X] T041 [P] [US4] Add failing tests for `build_intake_progress_report()` status, risk, rule-family, and material counts in `tests/unit/test_source_intake.py`
- [X] T042 [US4] Implement `build_intake_progress_report()` in `src/mingli_engine/source_intake.py`
- [X] T043 [P] [US4] Add failing tests for approved-not-promoted, duplicate, conflict-link, and gap-link progress counts in `tests/unit/test_source_intake.py`
- [X] T044 [US4] Extend `build_intake_progress_report()` with approval readiness, duplicate, conflict-link, and gap-link counts in `src/mingli_engine/source_intake.py`
- [X] T045 [P] [US4] Add failing tests for `validate_intake_quality()` blocking failures in `tests/unit/test_source_intake.py`
- [X] T046 [US4] Implement `validate_intake_quality()` in `src/mingli_engine/source_intake.py`
- [X] T047 [US4] Update `docs/classical_sources/intake.md` with the current computed intake snapshot and next-review queues
- [X] T048 [US4] Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`

**Checkpoint**: US4 gives maintainers a review dashboard without exposing unapproved candidates to report generation.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, safety, and regression verification across all stories.

- [X] T049 [P] Update `docs/classical_sources/README.md` to document the 013 source-intake boundary and external-material guardrails
- [X] T050 [P] Update `specs/013-source-extraction-workflow/quickstart.md` with actual validation commands and expected intake snapshot after implementation
- [X] T051 [P] Add safety regression tests for candidate absolute-language filtering in `tests/safety/test_expanded_high_risk_language.py`
- [X] T052 Run `uv run --with pytest python -m pytest tests/safety/test_expanded_high_risk_language.py tests/integration/test_report_regression_cases.py`
- [X] T053 Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py tests/unit/test_classical_sources.py tests/unit/test_evidence_curation.py`
- [X] T054 Run full suite with `uv run --with pytest python -m pytest`
- [X] T055 Run `git diff --check` and confirm only acceptable line-ending warnings, if any
- [X] T056 Verify `git status --short --branch` shows no staged root PDF files and no staged root `Markdown/` material
- [X] T057 Mark completed tasks in `specs/013-source-extraction-workflow/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies
- **Phase 2 Foundational**: Depends on Phase 1; blocks every user story
- **Phase 3 US1**: Depends on Phase 2; MVP scope
- **Phase 4 US2**: Depends on Phase 2 and may reuse US1 candidate loading
- **Phase 5 US3**: Depends on Phase 2 and benefits from US1/US2 data, but its validation can be tested independently with fixtures
- **Phase 6 US4**: Depends on Phase 2 and can summarize any implemented subset, but full value comes after US1-US3
- **Phase 7 Polish**: Depends on selected stories being complete

### User Story Dependencies

- **US1 Register Candidate Extracts**: Required MVP; no dependency on other stories after Foundation
- **US2 Review Candidate Evidence**: Uses candidates from US1 but can be tested with isolated fixtures
- **US3 Record Conflicts, Gaps, and Rejections**: Uses candidate and review concepts; can be tested with isolated fixtures
- **US4 View Intake Progress**: Uses all intake entities; can be tested with isolated fixtures and then project data

### Within Each Story

- Write failing tests first
- Implement minimal model or loader behavior
- Add or update seed JSON data
- Run focused tests for the story
- Stop at checkpoint and report status before moving to the next phase

---

## Parallel Opportunities

- T002 and T003 can run in parallel after T001
- T005 and T007 can run in parallel because they are separate test groups in the same file but should be merged carefully
- Within each story, tasks marked [P] are tests or docs that can be prepared before implementation
- US2, US3, and US4 can be planned in parallel after Foundation, but this project should execute them sequentially to satisfy staged reporting

---

## Parallel Example: User Story 1

```text
Task: "Add failing tests for valid and invalid SourceMaterial records in tests/unit/test_source_intake.py"
Task: "Add failing tests for candidate required fields, pending-review eligibility, and invalid statuses in tests/unit/test_source_intake.py"
Task: "Add failing tests that candidate extracted_meaning and short_quote reject long copied passages and absolute outcome language in tests/unit/test_source_intake.py"
Task: "Add a report-boundary regression test proving pending candidates are excluded from formal evidence loading in tests/integration/test_report_regression_cases.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 Setup
2. Complete Phase 2 Foundation
3. Complete Phase 3 US1
4. Run focused US1 tests
5. Stop and report before US2

### Incremental Delivery

1. US1 creates a safe candidate queue
2. US2 adds review decisions and promotion readiness
3. US3 adds auditability for conflicts, gaps, duplicates, and rejection reasons
4. US4 adds progress reporting
5. Polish runs safety and full-suite validation

### Staged Reporting Rule

After each phase, report:

- tasks completed in that phase
- focused tests run and result
- whether root PDF files and root `Markdown/` stayed untouched
- the next phase the user should approve or expect
