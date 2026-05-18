# Tasks: 第二层结构观察表达优化

**Input**: Design documents from `specs/006-structure-observation-language/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/structure-observation-markdown-contract.md](contracts/structure-observation-markdown-contract.md), [quickstart.md](quickstart.md)

**Tests**: Required. This feature changes report language in a sensitive domain, so tests must be written before implementation and must cover unit wording, final Markdown output, red-line refusal behavior, and prohibited absolute language.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested as an independent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file and has no dependency on an incomplete task.
- **[Story]**: Maps the task to a user story from `spec.md`.
- Every task includes exact file paths.

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm the active feature context and the existing code boundary before changing tests or implementation.

- [x] T001 Confirm the active feature pointer in `.specify/feature.json` and the 006 plan reference in `AGENTS.md`
- [x] T002 [P] Review the implementation boundary in `specs/006-structure-observation-language/plan.md` and `specs/006-structure-observation-language/research.md`
- [x] T003 [P] Review the Markdown behavior contract in `specs/006-structure-observation-language/contracts/structure-observation-markdown-contract.md`
- [x] T004 [P] Review the current structure text generators in `src/mingli_engine/interpretation.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Identify the exact existing assertions and output phrases that 006 will replace.

**Critical**: No wording implementation should begin until these checks identify the current old phrases and affected test files.

- [x] T005 Locate existing old-phrase assertions in `tests/unit/test_interpretation.py`, `tests/unit/test_report_schema.py`, `tests/integration/test_calculate_report_cli.py`, and `tests/integration/test_generate_markdown_report.py`
- [x] T006 Generate current sample Markdown through `src/mingli_engine/cli.py` with `examples/birth-profile.auto-gregorian.json` and confirm it still contains the old structure phrases before implementation

**Checkpoint**: Foundation ready. User story work can begin.

---

## Phase 3: User Story 1 - 读懂结构观察层 (Priority: P1) MVP

**Goal**: Make the `第二层：结构观察` wording read as natural, professional Chinese instead of system-like output.

**Independent Test**: Run `tests/unit/test_interpretation.py` and verify the interpretation summary contains the smoother five-element and basic structure wording while rejecting the three old system-like phrases.

### Tests for User Story 1

- [x] T007 [US1] Update `test_build_basic_interpretation_explains_day_master_and_ten_gods` in `tests/unit/test_interpretation.py` to expect smoother five-element and basic structure wording
- [x] T008 [US1] Add `test_build_basic_interpretation_avoids_system_like_structure_phrases` in `tests/unit/test_interpretation.py`
- [x] T009 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_interpretation.py -v` and confirm the new assertions fail before implementation in `tests/unit/test_interpretation.py`

### Implementation for User Story 1

- [x] T010 [US1] Replace the five-element opening prose in `_build_five_elements_text` in `src/mingli_engine/interpretation.py`
- [x] T011 [US1] Replace the basic structure opening prose in `_build_structure_text` in `src/mingli_engine/interpretation.py`
- [x] T012 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_interpretation.py -v` and confirm User Story 1 passes for `tests/unit/test_interpretation.py`
- [x] T013 [US1] Commit User Story 1 changes from `tests/unit/test_interpretation.py` and `src/mingli_engine/interpretation.py`

**Checkpoint**: User Story 1 should now be independently functional and testable.

---

## Phase 4: User Story 2 - 保留关键结构信息 (Priority: P2)

**Goal**: Ensure the smoother wording still preserves five-element counts, pillar ten-god relationships, and feature 005 reader-facing labels in final report output.

**Independent Test**: Run report schema and CLI integration tests and verify final Markdown keeps counts, ten-god pillar information, 004 heading order, and 005 labels while rejecting old structure phrases.

### Tests for User Story 2

- [x] T014 [P] [US2] Update assembled report wording assertions in `tests/unit/test_report_schema.py`
- [x] T015 [P] [US2] Update automatic chart CLI Markdown assertions in `tests/integration/test_calculate_report_cli.py`
- [x] T016 [P] [US2] Update external chart CLI Markdown assertions in `tests/integration/test_generate_markdown_report.py`
- [x] T017 [US2] Run `uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v` and confirm the new assertions fail before implementation for `tests/unit/test_report_schema.py`

### Implementation for User Story 2

- [x] T018 [US2] Replace the readable ten-god prefix and no-readable-signal wording in `_build_ten_gods_text` in `src/mingli_engine/interpretation.py`
- [x] T019 [US2] Run `uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v` and confirm User Story 2 passes for `tests/integration/test_calculate_report_cli.py`
- [x] T020 [US2] Commit User Story 2 changes from `tests/unit/test_report_schema.py`, `tests/integration/test_calculate_report_cli.py`, `tests/integration/test_generate_markdown_report.py`, and `src/mingli_engine/interpretation.py`

**Checkpoint**: User Stories 1 and 2 should both work independently.

---

## Phase 5: User Story 3 - 保持克制和安全边界 (Priority: P3)

**Goal**: Verify that smoother wording does not weaken ethical red lines, disclaimer behavior, or prohibited-language checks.

**Independent Test**: Run safety tests and full test suite, then generate one sample Markdown report for manual language review.

### Tests for User Story 3

- [x] T021 [P] [US3] Review prohibited phrase coverage in `tests/safety/test_red_lines_and_language.py`
- [x] T022 [US3] Run `uv run --with pytest python -m pytest tests/safety/test_red_lines_and_language.py -v` and confirm safety behavior passes for `tests/safety/test_red_lines_and_language.py`
- [x] T023 [US3] Run `uv run --with pytest python -m pytest` and confirm the full suite passes for `tests/`
- [x] T024 [US3] Generate sample Markdown through `src/mingli_engine/cli.py` with `examples/birth-profile.auto-gregorian.json` and confirm the output keeps safe observation language

### Implementation for User Story 3

- [x] T025 [US3] Add a targeted safety assertion in `tests/safety/test_red_lines_and_language.py` only if T021 shows the current safety test does not cover the new structure wording
- [x] T026 [US3] Commit any User Story 3 test adjustment from `tests/safety/test_red_lines_and_language.py`

**Checkpoint**: All user stories should now be independently functional and safety-verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final checks and handoff.

- [x] T027 Run `git diff --check` for formatting validation across `src/mingli_engine/interpretation.py` and `tests/`
- [x] T028 Run the quickstart verification commands in `specs/006-structure-observation-language/quickstart.md`
- [x] T029 Inspect `git status --short --branch` and recent commits for `006-structure-observation-language`
- [x] T030 Prepare final completion summary referencing `specs/006-structure-observation-language/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks user story work.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP.
- **User Story 2 (Phase 4)**: Can start after Foundational, but should usually follow US1 because both edit `src/mingli_engine/interpretation.py`.
- **User Story 3 (Phase 5)**: Can start after implementation wording exists; verifies safety and full behavior.
- **Polish (Phase 6)**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1**: No dependency on US2 or US3.
- **US2**: Depends on the same wording boundary as US1; sequential execution reduces conflict in `src/mingli_engine/interpretation.py`.
- **US3**: Depends on final wording being present, then validates safety and language boundaries.

### Within Each User Story

- Write or update tests first.
- Run the focused tests and confirm failure.
- Implement the smallest wording change.
- Run focused tests and confirm pass.
- Commit after the story is stable.

## Parallel Opportunities

- T002, T003, and T004 can run in parallel.
- T014, T015, and T016 can run in parallel because they edit different test files.
- T021 can run in parallel with manual review of sample output after wording implementation exists.
- Full implementation should keep edits to `src/mingli_engine/interpretation.py` sequential because US1 and US2 touch the same file.

## Parallel Example: User Story 2

```text
Task: "Update assembled report wording assertions in tests/unit/test_report_schema.py"
Task: "Update automatic chart CLI Markdown assertions in tests/integration/test_calculate_report_cli.py"
Task: "Update external chart CLI Markdown assertions in tests/integration/test_generate_markdown_report.py"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1.
3. Validate `tests/unit/test_interpretation.py`.
4. Stop and review the structure-layer wording before expanding to final Markdown tests.

### Incremental Delivery

1. US1 improves the core interpretation prose.
2. US2 proves the improved prose survives report assembly and CLI rendering.
3. US3 proves safety behavior and prohibited-language checks still hold.
4. Polish verifies quickstart and final git state.

### Notes

- `[P]` tasks touch different files and can be assigned to different workers.
- Tasks without `[P]` should run sequentially to avoid conflicts.
- Every story should be testable before moving to the next story.
- No task should add new algorithms, new report layers, new CLI flags, or new predictive conclusions.
