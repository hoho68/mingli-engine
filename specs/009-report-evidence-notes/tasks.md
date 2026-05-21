# Tasks: 报告证据说明层

**Input**: Design documents from `/specs/009-report-evidence-notes/`

**Prerequisites**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/report-evidence-notes-contract.md](contracts/report-evidence-notes-contract.md), [quickstart.md](quickstart.md)

**Tests**: Required. 009 changes formal report output, so every user story must follow test-first implementation and verify safety boundaries.

**Organization**: Tasks are grouped by user story to keep each increment independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or is read-only
- **[Story]**: Maps the task to a specific user story
- Every task includes an exact repository path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the 009 workspace and implementation references before changing code.

- [X] T001 Confirm the current branch is `009-report-evidence-notes` and inspect outstanding changes with `git status --short --branch` in `.git`
- [X] T002 Review the implementation scope, constraints, and source layout in `specs/009-report-evidence-notes/plan.md`
- [X] T003 [P] Review evidence-note requirements and acceptance scenarios in `specs/009-report-evidence-notes/spec.md`
- [X] T004 [P] Review evidence-note fields and validation rules in `specs/009-report-evidence-notes/data-model.md`
- [X] T005 [P] Review Markdown order and safety contract in `specs/009-report-evidence-notes/contracts/report-evidence-notes-contract.md`
- [X] T006 [P] Review the detailed Superpowers implementation guide in `docs/superpowers/plans/2026-05-20-report-evidence-notes.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Understand the existing report model, report builder, renderer, and tests before writing failing tests.

**Critical**: No user story work should begin until this phase is complete.

- [X] T007 Inspect the existing `Report` dataclass fields in `src/mingli_engine/models.py`
- [X] T008 Inspect existing report assembly and safety-review flow in `src/mingli_engine/report_schema.py`
- [X] T009 Inspect current Markdown section ordering in `src/mingli_engine/markdown.py`
- [X] T010 [P] Inspect report schema test patterns in `tests/unit/test_report_schema.py`
- [X] T011 [P] Inspect Markdown renderer order tests in `tests/unit/test_markdown_renderer.py`
- [X] T012 [P] Inspect safe Markdown regression checks in `tests/integration/test_report_regression_cases.py`
- [X] T013 [P] Inspect generated report safety-language checks in `tests/safety/test_red_lines_and_language.py`

**Checkpoint**: Existing report object, renderer placement, regression tests, and safety checks are understood.

---

## Phase 3: User Story 1 - 读者能看懂观察从哪里来 (Priority: P1) MVP

**Goal**: Add a reader-facing `观察依据` section to every safe formal Markdown report.

**Independent Test**: Build and render one safe report; confirm the report object has evidence notes and Markdown shows `### 观察依据` inside `第二层：结构观察` after summaries and before broader analysis.

### Tests for User Story 1

> Write these tests first and verify they fail before implementation.

- [X] T014 [US1] Add failing `evidence_notes` field and content assertions to `tests/unit/test_report_schema.py`
- [X] T015 [US1] Add `report.evidence_notes` to the raw-label body helper in `tests/unit/test_report_schema.py`
- [X] T016 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_report_schema.py -v` and confirm the expected missing-field failure for `tests/unit/test_report_schema.py`

### Implementation for User Story 1

- [X] T017 [US1] Add the `evidence_notes` field to the `Report` dataclass in `src/mingli_engine/models.py`
- [X] T018 [US1] Add `_build_evidence_notes()` with source, four-pillar, five-element, ten-god, and action-basis wording in `src/mingli_engine/report_schema.py`
- [X] T019 [US1] Wire `evidence_notes` into `build_report()`, `_major_body_sections()`, and safety-review text in `src/mingli_engine/report_schema.py`
- [X] T020 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_report_schema.py -v` and confirm schema tests pass for `tests/unit/test_report_schema.py`
- [X] T021 [US1] Add failing renderer order and content assertions for `### 观察依据` to `tests/unit/test_markdown_renderer.py`
- [X] T022 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_markdown_renderer.py -v` and confirm the expected missing-renderer-section failure for `tests/unit/test_markdown_renderer.py`
- [X] T023 [US1] Render `### 观察依据` after `report.ten_gods_summary` and before `### 结构分析` in `src/mingli_engine/markdown.py`
- [X] T024 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_markdown_renderer.py -v` and confirm renderer tests pass for `tests/unit/test_markdown_renderer.py`

**Checkpoint**: A safe report object contains evidence notes, and Markdown renders them in the correct structure-observation location.

---

## Phase 4: User Story 2 - 维护者能用回归样例守住证据说明 (Priority: P2)

**Goal**: Extend the 008 regression sample library so every safe Markdown case guards `观察依据`.

**Independent Test**: Run `tests/integration/test_report_regression_cases.py`; safe automatic and external verified examples must both verify the new section, placement, and evidence-basis phrases.

### Tests for User Story 2

- [X] T025 [US2] Add `EVIDENCE_NOTE_PHRASES` for `### 观察依据`, source, four-pillar, five-element, ten-god, action, and non-prediction wording in `tests/integration/test_report_regression_cases.py`
- [X] T026 [US2] Assert evidence-note section placement after `### 十神摘要` and before `### 结构分析` in `tests/integration/test_report_regression_cases.py`
- [X] T027 [US2] Assert every evidence-note phrase appears in safe Markdown output in `tests/integration/test_report_regression_cases.py`
- [X] T028 [US2] Run `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v` and confirm regression cases pass for `tests/integration/test_report_regression_cases.py`

### Implementation for User Story 2

- [X] T029 [US2] Keep `examples/report-regression-cases.json` unchanged and verify the existing safe cases exercise evidence notes through `tests/integration/test_report_regression_cases.py`

**Checkpoint**: Existing safe automatic and external verified regression examples guard the new evidence-note contract without adding a new CLI command or sample manifest.

---

## Phase 5: User Story 3 - 证据说明不变成新的命理断语 (Priority: P3)

**Goal**: Ensure evidence notes reinforce boundaries and do not create new fate verdicts or weaken red-line refusal behavior.

**Independent Test**: Run safety and regression tests; safe reports include conservative evidence wording, while unsafe red-line inputs still return safety JSON and never emit formal Markdown evidence sections.

### Tests for User Story 3

- [X] T030 [US3] Add assertions that safety JSON outputs do not contain `### 观察依据` in `tests/integration/test_report_regression_cases.py`
- [X] T031 [US3] Extend generated-report safety language checks to require `### 观察依据` and `不预测具体结果` in `tests/safety/test_red_lines_and_language.py`
- [X] T032 [US3] Verify selected raw machine labels and absolute destiny phrases still stay absent from report body through `tests/unit/test_report_schema.py`
- [X] T033 [US3] Run `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_red_lines_and_language.py -v` and confirm safety and regression tests pass for `tests/integration/test_report_regression_cases.py`

### Implementation for User Story 3

- [X] T034 [US3] Confirm no production safety behavior changes were needed in `src/mingli_engine/safety.py`

**Checkpoint**: Evidence notes remain explanatory and conservative, and unsafe requests continue returning safety JSON.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the new report section works with existing report, regression, and safety tests.

- [X] T035 Run report-focused tests from `specs/009-report-evidence-notes/quickstart.md` with `uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py tests/integration/test_report_regression_cases.py -v`
- [X] T036 Run safety tests from `specs/009-report-evidence-notes/quickstart.md` with `uv run --with pytest python -m pytest tests/safety/test_red_lines_and_language.py -v`
- [X] T037 Run the full suite with `uv run --with pytest python -m pytest` for repository root `tests`
- [X] T038 [P] Run whitespace validation with `git diff --check` for changed files under `src/` and `tests/`
- [X] T039 Inspect final changes with `git status --short --branch` and ensure only intentional files changed in `.git`
- [X] T040 Update completed task checkboxes in `specs/009-report-evidence-notes/tasks.md` as implementation checkpoints are completed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion and delivers the MVP
- **User Story 2 (Phase 4)**: Depends on US1 because regression tests need the rendered evidence section
- **User Story 3 (Phase 5)**: Depends on US1 and can run after or alongside US2 test updates once the section exists
- **Polish (Phase 6)**: Depends on all intended user stories being complete

### User Story Dependencies

- **US1**: Independent MVP for the report object and Markdown output.
- **US2**: Extends existing regression sample coverage after US1 output exists.
- **US3**: Confirms evidence notes stay within safety and ethics boundaries after US1 output exists.

### Within Each User Story

- Write failing tests first.
- Run the focused test and confirm the expected failure.
- Add the minimal implementation or test extension.
- Re-run the focused test and confirm it passes.
- Move to the next story only after the current story is green.

---

## Parallel Opportunities

- T003, T004, T005, and T006 are independent read-only setup tasks.
- T010, T011, T012, and T013 are independent read-only foundational checks.
- After US1 implementation is green, T025 through T027 can be prepared in the same test file before running T028.
- T038 can run in parallel with manual final review after all implementation edits are complete.

---

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete US1 to add evidence notes to the report object and Markdown output.
3. Stop and validate report schema and renderer tests before adding regression and safety coverage.

### Incremental Delivery

1. US1 gives readers the visible `观察依据` section.
2. US2 protects the section through existing safe report regression samples.
3. US3 verifies the section stays conservative and red-line behavior remains unchanged.
4. Polish verifies focused tests, safety tests, full suite, and diff hygiene.

### Scope Guard

- Do not add new CLI commands, flags, input shapes, chart calculations, interpretation conclusions, full Markdown snapshots, or export formats.
- Do not change `examples/report-regression-cases.json` unless a current safe example cannot exercise the new section.
- Keep evidence-note wording concise and reader-facing; avoid raw labels and absolute destiny language.
