# Tasks: 经典证据库精修

**Input**: Design documents from `specs/012-classical-evidence-curation/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/evidence-curation-contract.md`, `quickstart.md`

**Tests**: Required. The feature plan and constitution require failing tests before implementation for coverage counts, source references, conflict handling, high-risk limitations, copied-summary rejection, report compatibility, and safety regressions.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently. Do not move, delete, rewrite, or commit the root PDF files or the root `Markdown/` preparation directory while executing these tasks.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on incomplete tasks.
- **[Story]**: Required only for user story phases.
- Every task names the exact repository path to change or validate.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare curation-specific data and reviewer documentation without changing report behavior.

- [X] T001 [P] Update curation workflow guardrails in `docs/classical_sources/README.md` to state that root PDFs and root `Markdown/` are preparation material and must not be moved, deleted, or committed.
- [X] T002 [P] Create maintainer coverage report placeholder in `docs/classical_sources/coverage.md`.
- [X] T003 [P] Create review-note naming conventions for the nine source ids in `docs/classical_sources/extracts/README.md`.
- [X] T004 Create empty UTF-8 JSON array for curation batches in `src/mingli_engine/data/classical_sources/curation_batches.json`.
- [X] T005 Create empty UTF-8 JSON array for source conflicts in `src/mingli_engine/data/classical_sources/source_conflicts.json`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared contracts, loaders, and quality-report infrastructure required by all user stories.

**CRITICAL**: No user story implementation starts until this phase is complete.

### Tests First

- [X] T006 Add expanded source/evidence contract tests for `curation_gap_reason`, `review_reference`, `curation_batch_id`, `confidence`, `source_quality`, and `conflict_ids` in `tests/unit/test_classical_sources.py`.
- [X] T007 Add curation batch and source conflict loader validation tests in `tests/unit/test_classical_sources.py`.
- [X] T008 [P] Add initial coverage report and quality-check tests in `tests/unit/test_evidence_curation.py`.
- [X] T009 [P] Add report contract compatibility tests proving 012 keeps the 011 `Report` object shape in `tests/unit/test_report_schema.py`.

### Implementation

- [X] T010 Add `CurationBatch`, `SourceConflict`, `CurationGap`, and `CoverageReport` dataclasses plus curation constants in `src/mingli_engine/models.py`.
- [X] T011 Extend source and evidence validation for expanded curation metadata and source reference prefixes in `src/mingli_engine/classical_sources.py`.
- [X] T012 Add `load_curation_batches()` and `load_source_conflicts()` with uniqueness and cross-reference validation in `src/mingli_engine/classical_sources.py`.
- [X] T013 Create `build_coverage_report()` and `validate_curation_quality()` in `src/mingli_engine/evidence_curation.py`.

**Checkpoint**: Foundation ready. Loader and coverage tests should fail before T010-T013 and pass after T010-T013.

---

## Phase 3: User Story 1 - Curate Evidence Units By Source (Priority: P1) MVP

**Goal**: Every initial source has approved evidence units or an explicit curation gap, and each evidence unit has auditable source references and curation metadata.

**Independent Test**: `uv run --with pytest python -m pytest tests/unit/test_classical_sources.py tests/unit/test_evidence_curation.py -v`

### Tests First

- [X] T014 [US1] Add tests that all nine initial source ids have approved evidence coverage or an explicit curation gap reason in `tests/unit/test_classical_sources.py`.
- [X] T015 [P] [US1] Add per-source coverage and gap visibility tests in `tests/unit/test_evidence_curation.py`.

### Review Notes

- [X] T016 [P] [US1] Draft reviewed evidence map for `northeast_blind_peak` in `docs/classical_sources/extracts/northeast_blind_peak.md`.
- [X] T017 [P] [US1] Draft reviewed evidence map for `duan_plain_mingxue_outline` in `docs/classical_sources/extracts/duan_plain_mingxue_outline.md`.
- [X] T018 [P] [US1] Draft reviewed evidence map for `blind_school_secret` in `docs/classical_sources/extracts/blind_school_secret.md`.
- [X] T019 [P] [US1] Draft reviewed evidence map for `blind_life_manual` in `docs/classical_sources/extracts/blind_life_manual.md`.
- [X] T020 [P] [US1] Draft reviewed evidence map for `mingli_true_formula_teacher` in `docs/classical_sources/extracts/mingli_true_formula_teacher.md`.
- [X] T021 [P] [US1] Draft reviewed evidence map for `mingxue_golden_voice` in `docs/classical_sources/extracts/mingxue_golden_voice.md`.
- [X] T022 [P] [US1] Draft reviewed evidence map for `fortune_reading_hongfu_qitian` in `docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md`.
- [X] T023 [P] [US1] Draft reviewed evidence map for `immortal_fortune_jianghu_secret` in `docs/classical_sources/extracts/immortal_fortune_jianghu_secret.md`.
- [X] T024 [P] [US1] Draft reviewed evidence map for `life_death_book_100_pages` in `docs/classical_sources/extracts/life_death_book_100_pages.md`.

### Implementation

- [X] T025 [US1] Update all nine source records with `curation_gap_reason` and `review_reference` in `src/mingli_engine/data/classical_sources/sources.json`.
- [X] T026 [US1] Add approved or reviewed batch records for the first nine-source curation pass in `src/mingli_engine/data/classical_sources/curation_batches.json`.
- [X] T027 [US1] Add curated evidence units for `northeast_blind_peak` in `src/mingli_engine/data/classical_sources/evidence_units.json`.
- [X] T028 [US1] Add curated evidence units for `duan_plain_mingxue_outline` in `src/mingli_engine/data/classical_sources/evidence_units.json`.
- [X] T029 [US1] Add curated evidence units for `blind_school_secret` in `src/mingli_engine/data/classical_sources/evidence_units.json`.
- [X] T030 [US1] Add curated evidence units or an explicit blocking gap for `blind_life_manual` in `src/mingli_engine/data/classical_sources/evidence_units.json`.
- [X] T031 [US1] Add curated evidence units for `mingli_true_formula_teacher` in `src/mingli_engine/data/classical_sources/evidence_units.json`.
- [X] T032 [US1] Add curated evidence units for `mingxue_golden_voice` in `src/mingli_engine/data/classical_sources/evidence_units.json`.
- [X] T033 [US1] Add curated evidence units for `fortune_reading_hongfu_qitian` in `src/mingli_engine/data/classical_sources/evidence_units.json`.
- [X] T034 [US1] Add curated evidence units or an explicit blocking gap for `immortal_fortune_jianghu_secret` in `src/mingli_engine/data/classical_sources/evidence_units.json`.
- [X] T035 [US1] Add high-risk bounded evidence units for `life_death_book_100_pages` in `src/mingli_engine/data/classical_sources/evidence_units.json`.

**Checkpoint**: User Story 1 is complete when every initial source has approved evidence or a visible gap and all evidence units link to a curation batch and review reference.

---

## Phase 4: User Story 2 - Classify Rule Families And Risk Tiers (Priority: P2)

**Goal**: Evidence and reports distinguish rule families, risk tiers, school dependency, and high-risk boundaries.

**Independent Test**: `uv run --with pytest python -m pytest tests/unit/test_evidence_curation.py tests/safety/test_expanded_high_risk_language.py tests/integration/test_report_regression_cases.py -v`

### Tests First

- [X] T036 [US2] Add taxonomy coverage tests for at least eight approved rule families and all risk tiers in `tests/unit/test_evidence_curation.py`.
- [X] T037 [P] [US2] Add high-risk evidence limitation and non-exact-output tests in `tests/safety/test_expanded_high_risk_language.py`.
- [X] T038 [P] [US2] Add report regression expectations for expanded rule family names while preserving existing Markdown and HTML report contracts in `tests/integration/test_report_regression_cases.py`.

### Implementation

- [X] T039 [US2] Extend rule family constants for useful-god and taboo-god classifications in `src/mingli_engine/models.py`.
- [X] T040 [US2] Extend evidence validation for legal rule family names, legal risk tiers, high-risk limitations, and concise summaries in `src/mingli_engine/classical_sources.py`.
- [X] T041 [US2] Reclassify or expand curated evidence to at least 60 approved units across at least eight rule families in `src/mingli_engine/data/classical_sources/evidence_units.json`.
- [X] T042 [US2] Extend formal interpretation family specs for useful-god, taboo-god, remedy-boundary, and high-risk signal coverage in `src/mingli_engine/formal_interpretation.py`.

**Checkpoint**: User Story 2 is complete when coverage proves at least 60 approved units, at least eight rule families, complete risk-tier tagging, and safe high-risk limitations.

---

## Phase 5: User Story 3 - Represent Source Conflict And Evidence Gaps (Priority: P3)

**Goal**: Conflicts, school differences, and insufficient evidence are preserved and downgrade conclusions instead of being forced into a single answer.

**Independent Test**: `uv run --with pytest python -m pytest tests/unit/test_classical_sources.py tests/unit/test_formal_interpretation.py tests/unit/test_report_schema.py -v`

### Tests First

- [X] T043 [US3] Add source conflict validation tests for missing evidence ids, severe open conflicts, and documented conflicts in `tests/unit/test_classical_sources.py`.
- [X] T044 [P] [US3] Add formal interpretation tests proving severe open conflicts prevent `decided` strength and documented conflicts add disagreement notes in `tests/unit/test_formal_interpretation.py`.
- [X] T045 [P] [US3] Add report schema tests proving conflict and gap notes appear without adding new public `Report` fields in `tests/unit/test_report_schema.py`.

### Implementation

- [X] T046 [US3] Add conflict validation and gap derivation helpers in `src/mingli_engine/classical_sources.py`.
- [X] T047 [US3] Populate documented school and source conflict records in `src/mingli_engine/data/classical_sources/source_conflicts.json`.
- [X] T048 [US3] Apply conflicts and gaps to conclusion strength and `EvidenceTrace.disagreement_note` in `src/mingli_engine/formal_interpretation.py`.
- [X] T049 [US3] Surface disagreement and unavailable-evidence notes through existing evidence notes rendering in `src/mingli_engine/report_schema.py`.

**Checkpoint**: User Story 3 is complete when conflicting evidence is retained, unsupported conclusions downgrade, and report output explains disagreement without changing the report contract.

---

## Phase 6: User Story 4 - Audit Curation Quality (Priority: P4)

**Goal**: Maintainers can run quality checks that summarize coverage, traceability, risk boundaries, long-summary violations, and remaining gaps.

**Independent Test**: `uv run --with pytest python -m pytest tests/unit/test_evidence_curation.py tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py -v`

### Tests First

- [X] T050 [US4] Add tests for source counts, rule family counts, risk tier counts, approved evidence count, sources with gaps, open conflicts, and validation failures in `tests/unit/test_evidence_curation.py`.
- [X] T051 [P] [US4] Add regression assertions that safe reports keep source summaries, evidence traces, conclusion strength, disclaimer, and chart assumptions after the expanded corpus in `tests/integration/test_report_regression_cases.py`.
- [X] T052 [P] [US4] Add safety assertions that generated formal reports contain no absolute destiny phrases after expanded high-risk evidence is loaded in `tests/safety/test_expanded_high_risk_language.py`.

### Implementation

- [X] T053 [US4] Complete coverage metrics and validation failure reporting in `src/mingli_engine/evidence_curation.py`.
- [X] T054 [US4] Update maintainer-facing coverage output with current source counts, rule family counts, risk tier counts, gaps, and conflicts in `docs/classical_sources/coverage.md`.
- [X] T055 [US4] Ensure `build_report()` loads the expanded corpus and preserves existing Markdown and HTML output fields in `src/mingli_engine/report_schema.py`.
- [X] T056 [US4] Update quickstart validation notes for the final 012 commands and expected coverage results in `specs/012-classical-evidence-curation/quickstart.md`.

**Checkpoint**: User Story 4 is complete when quality checks explain what passed, what failed, and what still needs curation without reading implementation code.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verify the whole feature, clean up generated curation artifacts, and protect user-provided materials.

- [X] T057 Run source and curation unit tests with `uv run --with pytest python -m pytest tests/unit/test_classical_sources.py tests/unit/test_evidence_curation.py -v` and record any remaining gap in `docs/classical_sources/coverage.md`.
- [X] T058 Run report and safety regression tests with `uv run --with pytest python -m pytest tests/unit/test_formal_interpretation.py tests/unit/test_report_schema.py tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py -v`.
- [X] T059 Run full validation with `uv run --with pytest python -m pytest` and `git diff --check` from the repository root `E:\命理演绎`.
- [X] T060 Verify `git status --short` still leaves root `*.pdf` files and root `Markdown/` untracked unless the user explicitly asks otherwise.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks every user story.
- **Phase 3 US1**: Depends on Phase 2. This is the MVP.
- **Phase 4 US2**: Depends on Phase 2 and benefits from US1 evidence expansion.
- **Phase 5 US3**: Depends on Phase 2 and can proceed once enough evidence ids exist to form conflicts.
- **Phase 6 US4**: Depends on Phases 3-5 for meaningful final coverage.
- **Phase 7 Polish**: Depends on whichever user stories are intended for the current delivery pass.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational. No dependency on US2-US4.
- **US2 (P2)**: Starts after Foundational. Uses US1 curation data for the final count target.
- **US3 (P3)**: Starts after Foundational. Needs evidence ids from US1 or fixtures in tests.
- **US4 (P4)**: Starts after US1-US3 to audit the completed corpus and report behavior.

### Within Each User Story

- Tests must be written first and observed failing before implementation.
- Review notes before JSON curation data.
- Models before loaders.
- Loaders before coverage reports.
- Coverage and conflict logic before report rendering updates.
- Story checkpoint validation before moving to the next priority.

---

## Parallel Opportunities

- Setup documentation tasks T001-T003 can run in parallel.
- Initial foundational tests T008-T009 can run in parallel with T006-T007 because they touch different test files.
- US1 review note tasks T016-T024 can run in parallel because each source has a separate note file.
- US2 test tasks T036-T038 can run in parallel because they touch unit, safety, and integration test files.
- US3 test tasks T043-T045 can run in parallel because they touch separate test files.
- US4 regression and safety test tasks T051-T052 can run in parallel.

## Parallel Example: User Story 1

```text
Task: "Draft reviewed evidence map for northeast_blind_peak in docs/classical_sources/extracts/northeast_blind_peak.md"
Task: "Draft reviewed evidence map for duan_plain_mingxue_outline in docs/classical_sources/extracts/duan_plain_mingxue_outline.md"
Task: "Draft reviewed evidence map for blind_school_secret in docs/classical_sources/extracts/blind_school_secret.md"
Task: "Draft reviewed evidence map for blind_life_manual in docs/classical_sources/extracts/blind_life_manual.md"
Task: "Draft reviewed evidence map for mingli_true_formula_teacher in docs/classical_sources/extracts/mingli_true_formula_teacher.md"
Task: "Draft reviewed evidence map for mingxue_golden_voice in docs/classical_sources/extracts/mingxue_golden_voice.md"
Task: "Draft reviewed evidence map for fortune_reading_hongfu_qitian in docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md"
Task: "Draft reviewed evidence map for immortal_fortune_jianghu_secret in docs/classical_sources/extracts/immortal_fortune_jianghu_secret.md"
Task: "Draft reviewed evidence map for life_death_book_100_pages in docs/classical_sources/extracts/life_death_book_100_pages.md"
```

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational contracts and loaders.
3. Complete Phase 3 US1.
4. Stop and validate per-source evidence or gap coverage with `tests/unit/test_classical_sources.py` and `tests/unit/test_evidence_curation.py`.

### Incremental Delivery

1. Add US1 source curation for auditability.
2. Add US2 taxonomy and risk-tier coverage.
3. Add US3 conflicts and evidence gaps.
4. Add US4 quality reporting and regression protection.
5. Run Phase 7 validation before marking 012 complete.

### Safety And Data Notes

- Do not use runtime PDF parsing.
- Do not copy long source passages into report-facing evidence summaries.
- Do not allow blocked, unreviewed, failed, or unknown sources to support formal conclusions.
- Do not change the public report contract introduced in 011.
- Do not commit root PDFs or root `Markdown/` unless the user explicitly changes the instruction.
