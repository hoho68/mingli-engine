# Tasks: 报告层间衔接语优化

**Input**: Design documents from `specs/007-report-transition-language/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/report-transition-markdown-contract.md`, `quickstart.md`

**Tests**: Required. This feature changes reader-facing report language in a sensitive cultural interpretation domain, so tests must cover report schema wording, final Markdown output, safety refusal behavior, disclaimer/safety boundaries, and preservation of earlier 004/005/006 behavior.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested as an independent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when it touches different files and does not depend on incomplete tasks
- **[Story]**: User story label such as `[US1]`, `[US2]`, `[US3]`
- Every task includes exact repository file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the current feature context and keep implementation scoped to the existing report assembly boundary.

- [X] T001 Confirm the branch is `007-report-transition-language` and the worktree is clean before implementation in `.git`
- [X] T002 Review implementation scope in `specs/007-report-transition-language/plan.md`
- [X] T003 [P] Review the Markdown output contract in `specs/007-report-transition-language/contracts/report-transition-markdown-contract.md`
- [X] T004 [P] Review existing report assembly boundaries in `src/mingli_engine/report_schema.py`
- [X] T005 [P] Review existing Markdown heading rendering in `src/mingli_engine/markdown.py`
- [X] T006 [P] Review existing safety language tests in `tests/safety/test_red_lines_and_language.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Lock the old behavior that must not move while adding transitions.

**Critical**: No user story implementation should begin until these baseline checks are understood.

- [X] T007 Identify existing 004 heading-order assertions in `tests/unit/test_markdown_renderer.py`
- [X] T008 Identify existing 005 reader-friendly label assertions in `tests/unit/test_report_schema.py`
- [X] T009 Identify existing 006 structure-observation wording assertions in `tests/unit/test_report_schema.py`
- [X] T010 [P] Identify automatic-chart Markdown integration coverage in `tests/integration/test_calculate_report_cli.py`
- [X] T011 [P] Identify external-chart Markdown integration coverage in `tests/integration/test_generate_markdown_report.py`
- [X] T012 [P] Identify unsafe-focus JSON refusal coverage in `tests/safety/test_red_lines_and_language.py`

**Checkpoint**: Existing output contracts are located before adding any new transition tests or prose.

---

## Phase 3: User Story 1 - 按顺序读完整份报告 (Priority: P1) MVP

**Goal**: A first-time reader can see the intended reading path from quick guide to source assumptions, structure observation, boundaries, and action reflection.

**Independent Test**: Generate a complete safe Markdown report and confirm it contains a concise reading-path cue, source-as-basis wording, structure-as-clue wording, and unchanged 004 heading order.

### Tests for User Story 1

> Write these tests first and confirm they fail before implementation.

- [X] T013 [US1] Add quick-guide reading-path assertions in `tests/unit/test_report_schema.py`
- [X] T014 [US1] Add source-as-basis and structure-as-clue report field assertions in `tests/unit/test_report_schema.py`
- [X] T015 [P] [US1] Add final Markdown transition assertions while preserving heading order in `tests/unit/test_markdown_renderer.py`
- [X] T016 [P] [US1] Add automatic-chart Markdown transition assertions in `tests/integration/test_calculate_report_cli.py`
- [X] T017 [P] [US1] Add external-chart Markdown transition assertions in `tests/integration/test_generate_markdown_report.py`
- [X] T018 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v` and confirm the new assertions fail before implementation in `tests/`

### Implementation for User Story 1

- [X] T019 [US1] Add concise transition constants for reading path, source basis, and structure boundary in `src/mingli_engine/report_schema.py`
- [X] T020 [US1] Update quick guide assembly to include the reading-path cue while keeping the concise bullet pattern in `src/mingli_engine/report_schema.py`
- [X] T021 [US1] Append source-as-basis wording to the assumptions field in `src/mingli_engine/report_schema.py`
- [X] T022 [US1] Append structure-as-clue wording after existing 006 structure observations in `src/mingli_engine/report_schema.py`
- [X] T023 [US1] Run focused US1 tests and confirm they pass in `tests/unit/test_report_schema.py`, `tests/unit/test_markdown_renderer.py`, `tests/integration/test_calculate_report_cli.py`, and `tests/integration/test_generate_markdown_report.py`

**Checkpoint**: User Story 1 is complete when safe reports explain the reading order and first two layer transitions without changing headings or existing labels.

---

## Phase 4: User Story 2 - 把边界自然接到行动反思 (Priority: P2)

**Goal**: The boundary layer should guide the reader toward reflection instead of feeling like an abrupt stop, while action wording remains a prompt rather than a result promise.

**Independent Test**: Generate a complete safe Markdown report and confirm the third layer explains boundaries as overclaiming protection, then naturally leads into reflection prompts in the fourth layer.

### Tests for User Story 2

- [X] T024 [US2] Add boundary-to-action report field assertions in `tests/unit/test_report_schema.py`
- [X] T025 [US2] Add action-reflection-not-promise report field assertions in `tests/unit/test_report_schema.py`
- [X] T026 [P] [US2] Add final Markdown boundary-to-reflection assertions in `tests/unit/test_markdown_renderer.py`
- [X] T027 [P] [US2] Add automatic-chart boundary-to-reflection assertions in `tests/integration/test_calculate_report_cli.py`
- [X] T028 [P] [US2] Add external-chart boundary-to-reflection assertions in `tests/integration/test_generate_markdown_report.py`
- [X] T029 [US2] Run `uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v` and confirm the new US2 assertions fail before implementation in `tests/`

### Implementation for User Story 2

- [X] T030 [US2] Add concise boundary-action and action-reflection transition constants in `src/mingli_engine/report_schema.py`
- [X] T031 [US2] Append boundary-action wording to interpretation boundaries in `src/mingli_engine/report_schema.py`
- [X] T032 [US2] Add action-reflection wording to the fourth-layer action content in `src/mingli_engine/report_schema.py`
- [X] T033 [US2] Run focused US2 tests and confirm they pass in `tests/unit/test_report_schema.py`, `tests/unit/test_markdown_renderer.py`, `tests/integration/test_calculate_report_cli.py`, and `tests/integration/test_generate_markdown_report.py`

**Checkpoint**: User Story 2 is complete when the report naturally moves from “不能过度断言” to “把线索转成复盘问题”.

---

## Phase 5: User Story 3 - 保留既有结构和安全边界 (Priority: P3)

**Goal**: The report becomes more connected without weakening safety behavior or regressing 004 heading order, 005 labels, or 006 structure-observation wording.

**Independent Test**: Run focused and full verification to confirm safe Markdown still contains the required compatibility wording, while unsafe focus topics still return safety JSON.

### Tests for User Story 3

- [X] T034 [P] [US3] Add or strengthen 004 heading-order compatibility assertions in `tests/unit/test_markdown_renderer.py`
- [X] T035 [P] [US3] Add or strengthen 005 reader-facing label compatibility assertions in `tests/unit/test_report_schema.py`
- [X] T036 [US3] Add or strengthen 006 structure-observation compatibility assertions in `tests/unit/test_report_schema.py`
- [X] T037 [P] [US3] Add or strengthen 006 structure-observation final Markdown assertions in `tests/integration/test_calculate_report_cli.py`
- [X] T038 [P] [US3] Add or strengthen external-report compatibility assertions in `tests/integration/test_generate_markdown_report.py`
- [X] T039 [P] [US3] Confirm unsafe-focus Markdown requests still return safety JSON in `tests/safety/test_red_lines_and_language.py`

### Implementation for User Story 3

- [X] T040 [US3] Keep `src/mingli_engine/markdown.py` layout-only unless tests show an unavoidable placement issue
- [X] T041 [US3] Keep `src/mingli_engine/interpretation.py` 006 structure wording unchanged unless tests show an unavoidable adjacency issue
- [X] T042 [US3] Run safety tests with `uv run --with pytest python -m pytest tests/safety/test_red_lines_and_language.py -v` for `tests/safety/test_red_lines_and_language.py`
- [X] T043 [US3] Run focused report tests with `uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py tests/safety/test_red_lines_and_language.py -v` for `tests/`

**Checkpoint**: User Story 3 is complete when compatibility and safety tests pass without changing CLI behavior or safety JSON shape.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, sample output review, and cleanup.

- [X] T044 Generate one automatic-chart Markdown sample with `uv run python -m mingli_engine.cli calculate-report --input examples/birth-profile.auto-gregorian.json --format markdown` and inspect transition wording against `specs/007-report-transition-language/quickstart.md`
- [X] T045 Generate one external-chart Markdown sample with `uv run python -m mingli_engine.cli generate-report --input examples/bazi-chart.external-verified.json --format markdown` and inspect source-label compatibility against `specs/007-report-transition-language/quickstart.md`
- [X] T046 Run the full test suite with `uv run --with pytest python -m pytest` for `tests/`
- [X] T047 [P] Run a prohibited absolute-language check for new transition wording in `src/mingli_engine/report_schema.py`
- [X] T048 [P] Run `git diff --check` before final commit in `.git`
- [X] T049 Update task completion checkboxes as implementation proceeds in `specs/007-report-transition-language/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Phase 1; blocks story implementation.
- **Phase 3 US1**: Depends on Phase 2; delivers MVP reading flow.
- **Phase 4 US2**: Can start after Phase 2, but should normally follow US1 because it uses the same report assembly constants.
- **Phase 5 US3**: Can start after Phase 2, but final safety/compatibility verification should run after US1 and US2 implementation.
- **Phase 6 Polish**: Depends on selected story phases being complete.

### User Story Dependencies

- **US1 (P1)**: Independent MVP after foundation.
- **US2 (P2)**: Independent final behavior can be tested on its own, but implementation is simplest after US1 transition constants exist.
- **US3 (P3)**: Safety and compatibility guardrail; should be verified before completion.

### Within Each User Story

- Tests must be written first and should fail before implementation.
- Report field assertions should come before final Markdown assertions.
- `src/mingli_engine/report_schema.py` changes should come before any renderer change.
- Safety and full-suite verification should run after all intended wording changes.

---

## Parallel Opportunities

- T003-T006 can be reviewed in parallel because they read different files.
- T010-T012 can be reviewed in parallel because they inspect different test paths.
- T015-T017 can be written in parallel because they target different Markdown or integration test files.
- T026-T028 can be written in parallel because they target different Markdown or integration test files.
- T034, T035, and T037-T039 can be strengthened in parallel when they target different compatibility or safety assertions.
- T047-T048 can run in parallel near completion because they are independent checks.

---

## Parallel Example: User Story 1

```text
Task: "T015 [P] [US1] Add final Markdown transition assertions while preserving heading order in tests/unit/test_markdown_renderer.py"
Task: "T016 [P] [US1] Add automatic-chart Markdown transition assertions in tests/integration/test_calculate_report_cli.py"
Task: "T017 [P] [US1] Add external-chart Markdown transition assertions in tests/integration/test_generate_markdown_report.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Add failing US1 tests for reading path, source basis, structure clue, and heading order.
3. Implement only the US1 transitions in `src/mingli_engine/report_schema.py`.
4. Run focused US1 tests.
5. Stop and validate the MVP output before adding boundary-to-action wording.

### Incremental Delivery

1. Finish US1 so the report has a clear reading path.
2. Finish US2 so the boundary layer leads naturally into reflection.
3. Finish US3 so previous structure, labels, and safety behavior are protected.
4. Run sample Markdown generation and the full test suite.

### Implementation Notes

- Keep transition wording concise and deterministic.
- Do not add headings, CLI flags, input JSON fields, storage, chart calculations, or new命理 judgments.
- Prefer `src/mingli_engine/report_schema.py` for prose assembly.
- Keep `src/mingli_engine/markdown.py` as a renderer unless a test proves a placement-only adjustment is required.
- Keep 006 structure wording in `src/mingli_engine/interpretation.py` unchanged unless a test proves otherwise.
