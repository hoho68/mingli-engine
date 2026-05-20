# Tasks: 报告回归样例清单

**Input**: Design documents from `/specs/008-report-regression-cases/`

**Prerequisites**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/report-regression-cases-contract.md](contracts/report-regression-cases-contract.md), [quickstart.md](quickstart.md)

**Tests**: Required. 008 is a regression-safety feature, so the implementation must write failing pytest coverage before adding the manifest that makes it pass.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified in priority order.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or is read-only
- **[Story]**: Maps the task to a specific user story
- Every task includes an exact repository path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the current workspace and implementation references before changing files.

- [ ] T001 Confirm the current branch is `008-report-regression-cases` and inspect outstanding changes with `git status --short --branch` in `.git`
- [ ] T002 Review the implementation scope and no-production-code default in `specs/008-report-regression-cases/plan.md`
- [ ] T003 [P] Review manifest fields and supported values in `specs/008-report-regression-cases/data-model.md`
- [ ] T004 [P] Review the contract assertions required for safe Markdown and safety JSON in `specs/008-report-regression-cases/contracts/report-regression-cases-contract.md`
- [ ] T005 [P] Review the detailed Superpowers implementation guide in `docs/superpowers/plans/2026-05-20-report-regression-cases.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Identify the existing CLI test patterns and reusable sample inputs that all user stories depend on.

**Critical**: No user story implementation should begin until this phase is complete.

- [ ] T006 Inspect existing automatic report CLI test patterns in `tests/integration/test_calculate_report_cli.py`
- [ ] T007 Inspect existing external verified report test patterns in `tests/integration/test_generate_markdown_report.py`
- [ ] T008 [P] Confirm the safe automatic input exists and remains anonymized in `examples/birth-profile.auto-gregorian.json`
- [ ] T009 [P] Confirm the safe external verified input exists and remains anonymized in `examples/bazi-chart.external-verified.json`
- [ ] T010 [P] Confirm the unsafe focus input exists and targets a red-line topic in `examples/birth-profile.unsafe-focus.json`
- [ ] T011 Identify existing safety refusal expectations and exit-code behavior in `tests/safety/test_red_lines_and_language.py`

**Checkpoint**: Existing examples, CLI patterns, and safety behavior are understood; user story work can start.

---

## Phase 3: User Story 1 - 用清单守住安全报告结构 (Priority: P1) MVP

**Goal**: Add manifest-driven regression coverage for safe Markdown report cases so 004-007 report contracts stay visible.

**Independent Test**: Run only `tests/integration/test_report_regression_cases.py` with the safe automatic and safe external cases in the manifest; both must generate Markdown and pass durable structure and wording checks.

### Tests for User Story 1

> Write these tests first and verify they fail before adding the manifest.

- [ ] T012 [US1] Create a failing manifest loader and safe Markdown CLI contract test in `tests/integration/test_report_regression_cases.py`
- [ ] T013 [US1] Add assertions in `tests/integration/test_report_regression_cases.py` for formal report heading, quick guide, four layer headings, source disclosure, assumptions, reader-facing labels, structure observation wording, transition wording, raw-label absence, and absolute-language absence
- [ ] T014 [US1] Run `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v` and confirm the expected missing-manifest failure for `tests/integration/test_report_regression_cases.py`

### Implementation for User Story 1

- [ ] T015 [US1] Create `examples/report-regression-cases.json` with a `safe-auto-gregorian` case using `examples/birth-profile.auto-gregorian.json`
- [ ] T016 [US1] Add a `safe-external-verified` case to `examples/report-regression-cases.json` using `examples/bazi-chart.external-verified.json`
- [ ] T017 [US1] Verify source-specific expectations in `tests/integration/test_report_regression_cases.py` distinguish `auto_calculated` from `external_verified`
- [ ] T018 [US1] Run `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v` and confirm safe Markdown cases pass for `tests/integration/test_report_regression_cases.py`

**Checkpoint**: Safe automatic and safe external Markdown cases are listed, exercised, and protected against 004-007 report regressions.

---

## Phase 4: User Story 2 - 用清单守住安全拒绝行为 (Priority: P2)

**Goal**: Add manifest-driven regression coverage for unsafe red-line focus topics so they continue returning safety JSON instead of Markdown.

**Independent Test**: Run only `tests/integration/test_report_regression_cases.py` with the unsafe case in the manifest; it must return parseable safety JSON with `allowed` set to `false` and the expected red-line category.

### Tests for User Story 2

- [ ] T019 [US2] Extend `tests/integration/test_report_regression_cases.py` with safety JSON assertions for refusal exit code, parseable JSON, `allowed == false`, expected category, and no Markdown report heading
- [ ] T020 [US2] Run `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v` and confirm the expected safety-case coverage failure for `tests/integration/test_report_regression_cases.py`

### Implementation for User Story 2

- [ ] T021 [US2] Add an `unsafe-lifespan-focus` case to `examples/report-regression-cases.json` using `examples/birth-profile.unsafe-focus.json`
- [ ] T022 [US2] Set `expected_category` for the unsafe case in `examples/report-regression-cases.json` to the existing red-line category expected by safety tests
- [ ] T023 [US2] Run `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v` and confirm safety JSON cases pass for `tests/integration/test_report_regression_cases.py`

**Checkpoint**: Unsafe red-line examples are listed, exercised, and prevented from generating formal Markdown reports.

---

## Phase 5: User Story 3 - 让样例清单成为后续扩展入口 (Priority: P3)

**Goal**: Make the manifest self-checking enough that future cases can be added without creating separate one-off tests.

**Independent Test**: Add or inspect any manifest entry in `examples/report-regression-cases.json`; the test suite should automatically validate shape, supported values, unique IDs, existing input paths, and story-specific required fields.

### Tests for User Story 3

- [ ] T024 [US3] Add manifest shape assertions in `tests/integration/test_report_regression_cases.py` for required fields, unique IDs, supported `kind`, supported `command`, existing `input`, and non-empty `purpose`
- [ ] T025 [US3] Add kind-specific assertions in `tests/integration/test_report_regression_cases.py` requiring `source_type` for `safe_markdown` and `expected_category` for `safety_json`
- [ ] T026 [US3] Add coverage assertions in `tests/integration/test_report_regression_cases.py` requiring at least one automatic safe case, one external safe case, and one safety JSON case

### Implementation for User Story 3

- [ ] T027 [US3] Adjust `examples/report-regression-cases.json` so every case satisfies the manifest shape and kind-specific requirements
- [ ] T028 [US3] Run `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v` and confirm all manifest validation passes for `tests/integration/test_report_regression_cases.py`

**Checkpoint**: The manifest is a durable extension point, and every listed case is automatically exercised.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the new regression library works with existing report and safety tests without changing CLI behavior.

- [ ] T029 Run report integration tests from `specs/008-report-regression-cases/quickstart.md` with `uv run --with pytest python -m pytest tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py tests/integration/test_report_regression_cases.py -v`
- [ ] T030 Run safety tests with `uv run --with pytest python -m pytest tests/safety/test_red_lines_and_language.py -v`
- [ ] T031 Run the full suite with `uv run --with pytest python -m pytest` for repository root `tests`
- [ ] T032 [P] Run whitespace validation with `git diff --check` for changed files under `examples/` and `tests/`
- [ ] T033 Inspect final changes with `git status --short --branch` and ensure only intentional files changed in `.git`
- [ ] T034 Update task checkboxes in `specs/008-report-regression-cases/tasks.md` as implementation checkpoints are completed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion; may run after US1 because it extends the same test and manifest files
- **User Story 3 (Phase 5)**: Depends on US1 and US2 because it validates the completed initial manifest
- **Polish (Phase 6)**: Depends on all intended user stories being complete

### User Story Dependencies

- **US1**: Can deliver the MVP guardrail for safe Markdown reports.
- **US2**: Adds the required unsafe red-line regression case.
- **US3**: Makes the manifest extensible and self-validating after the first safe and unsafe cases exist.

### Within Each User Story

- Write or extend failing tests first.
- Run the focused test and confirm the expected failure.
- Add or adjust manifest entries.
- Re-run the focused test and confirm it passes.
- Move to the next story only after the current story is green.

---

## Parallel Opportunities

- T003, T004, and T005 are independent read-only setup tasks.
- T008, T009, and T010 are independent example-file checks.
- During implementation, only one worker should edit `tests/integration/test_report_regression_cases.py` and `examples/report-regression-cases.json` at a time because the user stories build on the same files.
- T032 can run in parallel with manual final review after all implementation edits are complete.

---

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete US1 to protect safe Markdown report structure and wording.
3. Stop and validate `tests/integration/test_report_regression_cases.py` before expanding to safety cases.

### Incremental Delivery

1. US1 protects existing safe report quality.
2. US2 adds red-line refusal coverage.
3. US3 turns the case list into a durable extension point.
4. Polish verifies integration, safety, and full-suite compatibility.

### Scope Guard

- Do not add new CLI commands, flags, input shapes, chart calculations, interpretation conclusions, or full Markdown snapshots.
- Keep helper logic local to `tests/integration/test_report_regression_cases.py` unless a real production need appears.
- Treat `examples/report-regression-cases.json` as a maintainer-facing regression manifest, not an end-user feature.
