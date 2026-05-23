# Tasks: HTML 可视化报告

**Input**: Design documents from `/specs/010-html-visual-report/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/html-report-contract.md`, `quickstart.md`

**Tests**: Required. This feature changes CLI report output and browser-facing rendering, so renderer, CLI, regression, and safety tests must be written before implementation.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified as an independent increment.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel because it touches different files or only reads context.
- **[Story]**: User story label for implementation phases only.
- Every task includes the relevant command or file path.

---

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm branch state and load the 010 design artifacts before writing tests or code.

- [ ] T001 Run `git status --short --branch` from `E:/命理演绎` and confirm the branch is `010-html-visual-report`.
- [ ] T002 Review `specs/010-html-visual-report/plan.md` for technology, constraints, and target file structure.
- [ ] T003 [P] Review user stories and acceptance criteria in `specs/010-html-visual-report/spec.md`.
- [ ] T004 [P] Review design decisions in `specs/010-html-visual-report/research.md`.
- [ ] T005 [P] Review renderer entities and validation rules in `specs/010-html-visual-report/data-model.md`.
- [ ] T006 [P] Review CLI and HTML output contract in `specs/010-html-visual-report/contracts/html-report-contract.md`.
- [ ] T007 [P] Review verification commands in `specs/010-html-visual-report/quickstart.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Understand current report rendering, CLI dispatch, and test patterns before any user-story work starts.

**Checkpoint**: No user-story test or implementation task should begin until this phase is complete.

- [ ] T008 Inspect current report format parsing and output dispatch in `src/mingli_engine/cli.py`.
- [ ] T009 Inspect current Markdown report ordering in `src/mingli_engine/markdown.py`.
- [ ] T010 Inspect the existing `Report` data contract in `src/mingli_engine/models.py`.
- [ ] T011 [P] Inspect CLI integration test patterns in `tests/integration/test_calculate_report_cli.py`.
- [ ] T012 [P] Inspect external verified chart report test patterns in `tests/integration/test_generate_markdown_report.py`.
- [ ] T013 [P] Inspect regression manifest checks in `tests/integration/test_report_regression_cases.py`.
- [ ] T014 [P] Inspect red-line and report-language safety checks in `tests/safety/test_red_lines_and_language.py`.

---

## Phase 3: User Story 1 - 用户能直接生成 HTML 报告 (Priority: P1) MVP

**Goal**: `calculate-report --format html` and `generate-report --format html` return complete standalone HTML for safe inputs while existing Markdown output remains unchanged.

**Independent Test**: Run safe automatic-chart and external-verified commands with `--format html`; both should exit successfully and write a complete document starting with `<!doctype html>`.

### Tests for User Story 1

> Write these tests first and confirm they fail before implementation.

- [ ] T015 [US1] Create failing complete-document and required-section renderer tests in `tests/unit/test_html_renderer.py`.
- [ ] T016 [US1] Add failing `calculate-report --format html` integration assertions in `tests/integration/test_calculate_report_cli.py`.
- [ ] T017 [US1] Add failing `generate-report --format html` integration assertions in `tests/integration/test_generate_markdown_report.py`.
- [ ] T018 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_html_renderer.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v` and confirm the expected missing renderer or invalid format failures.

### Implementation for User Story 1

- [ ] T019 [US1] Add `render_html_report(report)` with complete static document rendering in `src/mingli_engine/html.py`.
- [ ] T020 [US1] Extend report `--format` choices to include `html` in `src/mingli_engine/cli.py`.
- [ ] T021 [US1] Dispatch safe report output to Markdown or HTML renderers in `src/mingli_engine/cli.py`.
- [ ] T022 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_html_renderer.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v` and confirm US1 passes with Markdown behavior preserved.

**Checkpoint**: User Story 1 is usable as the MVP.

---

## Phase 4: User Story 2 - 读者能按原报告顺序阅读 HTML (Priority: P2)

**Goal**: HTML preserves the current formal report reading order and keeps `观察依据` in the structure-observation layer after ten-god summary and before structure analysis.

**Independent Test**: Generate one safe HTML report and verify the major groups appear in the required order, including source wording and `观察依据` placement.

### Tests for User Story 2

> Write these tests first and confirm they fail before implementation.

- [ ] T023 [US2] Add failing HTML section-order assertions in `tests/unit/test_html_renderer.py`.
- [ ] T024 [US2] Add failing source-wording and `观察依据` placement checks in `tests/integration/test_report_regression_cases.py`.
- [ ] T025 [US2] Run `uv run --with pytest python -m pytest tests/unit/test_html_renderer.py tests/integration/test_report_regression_cases.py -v` and confirm the expected ordering or contract failures.

### Implementation for User Story 2

- [ ] T026 [US2] Refine semantic sections and headings to mirror Markdown hierarchy in `src/mingli_engine/html.py`.
- [ ] T027 [US2] Extend regression helper checks so safe automatic and external verified cases verify HTML contract in `tests/integration/test_report_regression_cases.py`.
- [ ] T028 [US2] Run `uv run --with pytest python -m pytest tests/unit/test_html_renderer.py tests/integration/test_report_regression_cases.py -v` and confirm order, source, and evidence checks pass.

**Checkpoint**: User Story 2 preserves report meaning across formats.

---

## Phase 5: User Story 3 - 维护者能守住 HTML 安全边界 (Priority: P3)

**Goal**: HTML rendering escapes report text, contains no scripts or external resources, and keeps existing unsafe or invalid-input behavior unchanged.

**Independent Test**: Render report text containing HTML special characters and run unsafe `--format html` cases; safe output must escape text, while unsafe output must remain JSON instead of HTML.

### Tests for User Story 3

> Write these tests first and confirm they fail before implementation.

- [ ] T029 [US3] Add failing HTML escaping, no-script, and no-external-resource tests in `tests/unit/test_html_renderer.py`.
- [ ] T030 [US3] Add failing unsafe `--format html` safety JSON assertions in `tests/safety/test_red_lines_and_language.py`.
- [ ] T031 [US3] Add failing invalid-input and no-partial-HTML assertions for `--format html` in `tests/integration/test_generate_markdown_report.py`.
- [ ] T032 [US3] Run `uv run --with pytest python -m pytest tests/unit/test_html_renderer.py tests/safety/test_red_lines_and_language.py tests/integration/test_generate_markdown_report.py -v` and confirm expected failures where implementation is incomplete.

### Implementation for User Story 3

- [ ] T033 [US3] Escape all report text and preserve readable paragraph or list line breaks in `src/mingli_engine/html.py`.
- [ ] T034 [US3] Ensure generated HTML contains no `<script>`, inline event handlers, external URLs, external stylesheets, fonts, images, or CDN references in `src/mingli_engine/html.py`.
- [ ] T035 [US3] Confirm `src/mingli_engine/cli.py` returns existing safety JSON and invalid-input behavior before renderer dispatch.
- [ ] T036 [US3] Run `uv run --with pytest python -m pytest tests/unit/test_html_renderer.py tests/safety/test_red_lines_and_language.py tests/integration/test_generate_markdown_report.py -v` and confirm escaping, safety, and invalid-input checks pass.

**Checkpoint**: User Story 3 protects the browser-facing report boundary.

---

## Phase 6: Polish & Cross-Cutting Verification

**Purpose**: Confirm focused scenarios, regression coverage, and the full project suite after all desired stories are complete.

- [ ] T037 Run renderer quickstart tests with `uv run --with pytest python -m pytest tests/unit/test_html_renderer.py -v`.
- [ ] T038 Run CLI HTML tests with `uv run --with pytest python -m pytest tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v`.
- [ ] T039 Run regression and safety tests with `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_red_lines_and_language.py -v`.
- [ ] T040 Run the full suite with `uv run --with pytest python -m pytest`.
- [ ] T041 [P] Run whitespace validation with `git diff --check` from `E:/命理演绎`.
- [ ] T042 Inspect final changed files with `git status --short --branch` from `E:/命理演绎`.
- [ ] T043 Update completed checkboxes in `specs/010-html-visual-report/tasks.md` for every finished implementation checkpoint.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependency.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user-story work.
- **User Story 1 (Phase 3)**: Depends on Foundational and forms the MVP.
- **User Story 2 (Phase 4)**: Depends on User Story 1 renderer and CLI support.
- **User Story 3 (Phase 5)**: Depends on User Story 1 renderer and CLI support.
- **Polish (Phase 6)**: Depends on all selected user stories.

### User Story Dependencies

- **US1**: No dependency after Foundational.
- **US2**: Requires HTML output path from US1.
- **US3**: Requires HTML output path from US1.
- **US2 and US3**: Can be planned in parallel after US1, but edits to `tests/unit/test_html_renderer.py` and `src/mingli_engine/html.py` should be coordinated to avoid conflicts.

### Within Each User Story

- Tests must be written and run first.
- Renderer or CLI implementation follows failing tests.
- Focused test command must pass before moving to the next story.
- Markdown behavior and safety behavior must be checked whenever CLI dispatch changes.

---

## Parallel Opportunities

- Setup reading tasks T003-T007 can run in parallel.
- Foundational inspection tasks T011-T014 can run in parallel.
- US1 tests T015-T017 touch different test files and can be drafted in parallel.
- US2 tasks touching regression checks can be prepared after US1 while renderer order work is done separately.
- US3 safety and invalid-input tests T030-T031 can be drafted in parallel with renderer escaping tests T029.
- Polish checks T041-T042 can run after test commands finish.

---

## Parallel Example: User Story 1

```powershell
# Draft the independent failing tests first:
Task T015: "Create renderer contract tests in tests/unit/test_html_renderer.py"
Task T016: "Add calculate-report HTML assertions in tests/integration/test_calculate_report_cli.py"
Task T017: "Add generate-report HTML assertions in tests/integration/test_generate_markdown_report.py"

# Then implement the output path:
Task T019: "Add renderer in src/mingli_engine/html.py"
Task T020: "Add html format choice in src/mingli_engine/cli.py"
Task T021: "Dispatch renderer in src/mingli_engine/cli.py"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Stop and validate the focused renderer and CLI tests.
4. Keep Markdown output unchanged while adding HTML.

### Incremental Delivery

1. Deliver US1 so both report commands can output complete static HTML.
2. Deliver US2 so HTML preserves reading order and source/evidence placement.
3. Deliver US3 so escaping, no-script, and red-line behavior are protected.
4. Run Phase 6 verification before merge.

### Safety Notes

- Do not add new Mingli conclusions, chart calculations, input fields, Web forms, JavaScript, external assets, PDF export, or PNG export.
- Keep unsafe red-line requests returning safety JSON even when `--format html` is requested.
- Escape every report text field before inserting it into HTML.
