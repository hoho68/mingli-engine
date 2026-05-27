# Tasks: 典籍证据核心与放大报告口径

**Input**: Design documents from `/specs/011-classical-evidence-core/`

**Prerequisites**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/classical-evidence-contract.md](contracts/classical-evidence-contract.md), [quickstart.md](quickstart.md)

**Tests**: Required. This feature changes report evidence, judgment language, high-risk handling, and rendered report contracts, so source loading, evidence mapping, schema, renderer, integration, and safety tests must be written before implementation.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified as an independent increment.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel because it touches a different file or is read-only.
- **[Story]**: Maps the task to a specific user story.
- Every task includes the relevant command or repository path.

---

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm the 011 workspace and load the design artifacts before writing tests or code.

- [X] T001 Run `git status --short --branch` from `E:/命理演绎` and confirm the branch is `011-classical-evidence-core`.
- [X] T002 Review implementation scope, constraints, and source layout in `specs/011-classical-evidence-core/plan.md`.
- [X] T003 [P] Review user stories and acceptance scenarios in `specs/011-classical-evidence-core/spec.md`.
- [X] T004 [P] Review source, evidence, trace, conclusion, and risk entities in `specs/011-classical-evidence-core/data-model.md`.
- [X] T005 [P] Review source registry, evidence unit, report evidence, and high-risk contracts in `specs/011-classical-evidence-core/contracts/classical-evidence-contract.md`.
- [X] T006 [P] Review source loading, formal interpretation, high-risk, and regression verification commands in `specs/011-classical-evidence-core/quickstart.md`.
- [X] T007 [P] Review research decisions about curated evidence files and runtime behavior in `specs/011-classical-evidence-core/research.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Understand existing report flow and create shared directories before user-story implementation begins.

**Critical**: No user story work should begin until this phase is complete.

- [X] T008 Inspect the current report dataclasses in `src/mingli_engine/models.py`.
- [X] T009 Inspect existing report assembly and safety-review flow in `src/mingli_engine/report_schema.py`.
- [X] T010 Inspect current Markdown rendering order in `src/mingli_engine/markdown.py`.
- [X] T011 Inspect current HTML rendering order in `src/mingli_engine/html.py`.
- [X] T012 Inspect current CLI safety and format dispatch in `src/mingli_engine/cli.py`.
- [X] T013 [P] Inspect existing report schema tests in `tests/unit/test_report_schema.py`.
- [X] T014 [P] Inspect current regression report assertions in `tests/integration/test_report_regression_cases.py`.
- [X] T015 [P] Inspect current red-line and language safety assertions in `tests/safety/test_red_lines_and_language.py`.
- [X] T016 Create shared source data directories `src/mingli_engine/data/classical_sources/` and review directories `docs/classical_sources/extracts/`.
- [X] T017 [P] Create source review workflow documentation in `docs/classical_sources/README.md`.

**Checkpoint**: Existing flow is understood and shared source directories exist.

---

## Phase 3: User Story 1 - Use Classical Books As Core Evidence (Priority: P1) MVP

**Goal**: Represent all nine books as reviewable source entries and load approved evidence units deterministically.

**Independent Test**: Run `uv run --with pytest python -m pytest tests/unit/test_classical_sources.py -v`; it verifies all nine sources exist, source ids are unique, approved evidence links to approved sources, and blocked/unreviewed sources cannot support report conclusions.

### Tests for User Story 1

> Write these tests first and verify they fail before implementation.

- [X] T018 [US1] Create failing source registry and evidence validation tests in `tests/unit/test_classical_sources.py`.
- [X] T019 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_classical_sources.py -v` and confirm the expected missing module or missing data failure for `tests/unit/test_classical_sources.py`.

### Implementation for User Story 1

- [X] T020 [US1] Add `ClassicalSource` and `EvidenceUnit` dataclasses and validation constants in `src/mingli_engine/models.py`.
- [X] T021 [US1] Create nine initial source entries in `src/mingli_engine/data/classical_sources/sources.json`.
- [X] T022 [US1] Create initial approved evidence units across ordinary, sensitive, and high-risk families in `src/mingli_engine/data/classical_sources/evidence_units.json`.
- [X] T023 [US1] Implement source and evidence loading plus validation in `src/mingli_engine/classical_sources.py`.
- [X] T024 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_classical_sources.py -v` and confirm US1 passes.

**Checkpoint**: The initial classical evidence corpus is loadable and independently validated.

---

## Phase 4: User Story 2 - Produce Formal Traditional Judgments (Priority: P2)

**Goal**: Build source-backed formal conclusions with conclusion strength, evidence traces, and expanded judgment families.

**Independent Test**: Run `uv run --with pytest python -m pytest tests/unit/test_formal_interpretation.py tests/unit/test_report_schema.py -v`; it verifies formal conclusions contain chart signals, evidence ids, conclusion strength, and report evidence fields.

### Tests for User Story 2

> Write these tests first and verify they fail before implementation.

- [X] T025 [US2] Create failing formal conclusion and evidence trace tests in `tests/unit/test_formal_interpretation.py`.
- [X] T026 [US2] Add failing expanded report evidence field assertions in `tests/unit/test_report_schema.py`.
- [X] T027 [US2] Run `uv run --with pytest python -m pytest tests/unit/test_formal_interpretation.py tests/unit/test_report_schema.py -v` and confirm missing model or report evidence failures.

### Implementation for User Story 2

- [X] T028 [US2] Add `EvidenceTrace`, `FormalConclusion`, and `ExpandedReportEvidence` dataclasses in `src/mingli_engine/models.py`.
- [X] T029 [US2] Implement `build_formal_interpretation(chart, evidence_units)` in `src/mingli_engine/formal_interpretation.py`.
- [X] T030 [US2] Wire expanded evidence and formal conclusions into `build_report()` in `src/mingli_engine/report_schema.py`.
- [X] T031 [US2] Render source-backed `命理依据` and formal conclusions in `src/mingli_engine/markdown.py`.
- [X] T032 [US2] Render the same source-backed evidence contract in `src/mingli_engine/html.py`.
- [X] T033 [US2] Run `uv run --with pytest python -m pytest tests/unit/test_formal_interpretation.py tests/unit/test_report_schema.py -v` and confirm US2 unit tests pass.

**Checkpoint**: Safe formal reports can carry source-backed traditional judgments in the report object and renderers.

---

## Phase 5: User Story 3 - Expand High-Risk Material With Boundaries (Priority: P3)

**Goal**: Allow source-backed high-risk traditional signals while narrowing or refusing exact outcomes and professional-advice requests.

**Independent Test**: Run `uv run --with pytest python -m pytest tests/unit/test_high_risk.py tests/safety/test_expanded_high_risk_language.py -v`; it verifies high-risk signal discussion, exact death/lifespan refusal, professional-advice refusal, and non-absolute language.

### Tests for User Story 3

> Write these tests first and verify they fail before implementation.

- [X] T034 [US3] Create failing high-risk classification and narrowing tests in `tests/unit/test_high_risk.py`.
- [X] T035 [US3] Create failing expanded high-risk language and refusal tests in `tests/safety/test_expanded_high_risk_language.py`.
- [X] T036 [US3] Run `uv run --with pytest python -m pytest tests/unit/test_high_risk.py tests/safety/test_expanded_high_risk_language.py -v` and confirm missing high-risk handling failures.

### Implementation for User Story 3

- [X] T037 [US3] Implement high-risk request classification and narrowing helpers in `src/mingli_engine/high_risk.py`.
- [X] T038 [US3] Align focus-topic and text review behavior with Constitution v2.0 in `src/mingli_engine/safety.py`.
- [X] T039 [US3] Route high-risk formal notes and unavailable/refused conclusions through `src/mingli_engine/report_schema.py`.
- [X] T040 [US3] Ensure CLI report paths use the expanded high-risk review before rendering in `src/mingli_engine/cli.py`.
- [X] T041 [US3] Run `uv run --with pytest python -m pytest tests/unit/test_high_risk.py tests/safety/test_expanded_high_risk_language.py -v` and confirm US3 passes.

**Checkpoint**: High-risk corpus material can support bounded traditional risk-signal analysis without exact-outcome or professional-advice output.

---

## Phase 6: User Story 4 - Keep Reports Auditable Under The New Constitution (Priority: P4)

**Goal**: Protect source-backed reports with integration and regression coverage across Markdown, HTML, safe examples, and high-risk narrowed/refused examples.

**Independent Test**: Run `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v`; it verifies source summaries, evidence traces, expanded judgment families, high-risk narrowing/refusal, and absence of absolute destiny phrases.

### Tests for User Story 4

> Write these tests first and verify they fail before implementation.

- [X] T042 [US4] Add failing safe-report assertions for source summary, evidence traces, and expanded judgment families in `tests/integration/test_report_regression_cases.py`.
- [X] T043 [US4] Add failing high-risk narrowed/refused regression fixtures in `examples/birth-profile.high-risk-general.json` and `examples/birth-profile.exact-lifespan.json`.
- [X] T044 [US4] Add failing manifest entries for expanded safe and high-risk cases in `examples/report-regression-cases.json`.
- [X] T045 [US4] Run `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v` and confirm expected expanded contract failures.

### Implementation for User Story 4

- [X] T046 [US4] Update regression helper checks for Markdown source-backed evidence in `tests/integration/test_report_regression_cases.py`.
- [X] T047 [US4] Update regression helper checks for HTML source-backed evidence in `tests/integration/test_report_regression_cases.py`.
- [X] T048 [US4] Ensure report outputs include the expanded contract fields required by `examples/report-regression-cases.json`.
- [X] T049 [US4] Run `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v` and confirm US4 passes.

**Checkpoint**: Safe and high-risk report behavior is regression-guarded under Constitution v2.0.

---

## Phase 7: Polish & Cross-Cutting Verification

**Purpose**: Verify quickstart commands, full test suite, and diff hygiene after all user stories are complete.

- [X] T050 Run source registry quickstart with `uv run --with pytest python -m pytest tests/unit/test_classical_sources.py -v` from `E:/命理演绎`.
- [X] T051 Run formal interpretation quickstart with `uv run --with pytest python -m pytest tests/unit/test_formal_interpretation.py -v` from `E:/命理演绎`.
- [X] T052 Run high-risk quickstart with `uv run --with pytest python -m pytest tests/safety/test_expanded_high_risk_language.py -v` from `E:/命理演绎`.
- [X] T053 Run full regression with `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v` from `E:/命理演绎`.
- [X] T054 Run full suite with `uv run --with pytest python -m pytest` from `E:/命理演绎`.
- [X] T055 [P] Run whitespace validation with `git diff --check` from `E:/命理演绎`.
- [X] T056 Inspect final changed files with `git status --short --branch` from `E:/命理演绎`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and delivers the MVP evidence corpus.
- **User Story 2 (Phase 4)**: Depends on US1 because formal conclusions need validated evidence units.
- **User Story 3 (Phase 5)**: Depends on US1 because high-risk handling needs risk-tiered evidence units.
- **User Story 4 (Phase 6)**: Depends on US2 and US3 because regression tests need rendered formal conclusions and high-risk behavior.
- **Polish (Phase 7)**: Depends on all selected user stories.

### User Story Dependencies

- **US1**: Independent MVP for the source registry and evidence loader.
- **US2**: Requires US1 evidence units and adds formal report judgments.
- **US3**: Requires US1 risk-tiered evidence units and adds high-risk narrowing/refusal.
- **US4**: Requires US2 report rendering and US3 high-risk behavior before regression can fully pass.

### Within Each User Story

- Write failing tests first.
- Run the focused test command and confirm the expected failure.
- Implement the minimal code/data needed for that story.
- Re-run the focused test command and confirm it passes.
- Move to the next story only after the current story is green.

---

## Parallel Opportunities

- T003 through T007 are independent read-only setup tasks.
- T013 through T015 are independent read-only foundational inspection tasks.
- T017 can run in parallel with T018 after the directory scaffold from T016 exists.
- US2 test tasks T025 and T026 touch different test files and can be drafted in parallel.
- US3 test tasks T034 and T035 touch different test files and can be drafted in parallel.
- US4 implementation tasks T046 and T047 can be split by Markdown and HTML regression helpers.
- Polish tasks T050 through T053 can run independently after implementation is complete; T055 can run while final status is inspected.

---

## Parallel Example: User Story 2

```powershell
# Draft independent failing tests:
Task T025: "Create formal interpretation tests in tests/unit/test_formal_interpretation.py"
Task T026: "Add report evidence assertions in tests/unit/test_report_schema.py"

# Implement in dependency order:
Task T028: "Add evidence trace and conclusion models in src/mingli_engine/models.py"
Task T029: "Build formal conclusions in src/mingli_engine/formal_interpretation.py"
Task T030: "Wire report schema in src/mingli_engine/report_schema.py"
Task T031: "Render Markdown evidence in src/mingli_engine/markdown.py"
Task T032: "Render HTML evidence in src/mingli_engine/html.py"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 so all nine books are represented and evidence units load safely.
3. Stop and validate `tests/unit/test_classical_sources.py`.
4. Use US1 as the minimum useful foundation for future source curation, even before reports are expanded.

### Incremental Delivery

1. US1 creates the reviewable source/evidence corpus.
2. US2 uses that corpus to produce formal source-backed traditional judgments.
3. US3 expands high-risk handling without allowing exact outcomes or professional advice.
4. US4 locks the new report contract into Markdown, HTML, and regression coverage.
5. Phase 7 verifies quickstart commands, full suite, and diff hygiene.

### Safety And Scope Guard

- Do not parse raw PDFs at report runtime.
- Do not copy long source passages into user reports.
- Do not store user birth data or generated reports beyond existing request/output behavior.
- Do not remove disclaimer, chart source, calculation assumptions, or evidence explanations.
- Do not allow exact death timing, exact lifespan, diagnosis/treatment, legal, psychological, investment, coercive matching, anxiety creation, or paid-remedy upsell outputs.
- Keep Markdown and HTML report contracts aligned through the same `Report` object.
