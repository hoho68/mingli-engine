# Tasks: Liuyao Najia Calculation Engine V1

**Input**: Design documents from `/specs/020-liuyao-najia-engine/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/liuyao-v1-contract.md

**Tests**: REQUIRED (domain feature). Every phase follows red-green-refactor: failing focused tests first, implementation, then focused pytest + mypy + Ruff per plan.md Verification Commands.

**Organization**: Tasks are grouped by user story so each story is independently implementable and testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: US1 显式爻录入 / US2 时间与数字起卦 / US3 解读报告 / US4 知识与校准

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Package skeleton and reference-data scaffolding that everything else builds on.

- [x] T001 Create the `liuyao` package skeleton (`src/mingli_engine/liuyao/__init__.py`, `constants.py`, `result_models.py`) and empty test module files `tests/unit/test_liuyao_constants.py`, `test_liuyao_casting.py`, `test_liuyao_najia.py`, `test_liuyao_analysis.py`, `test_liuyao_report.py`, plus `tests/integration/test_liuyao_cli.py`
- [x] T002 [P] Add failing test for frozen reference-data loading in `tests/unit/test_liuyao_constants.py`, then create the `gua_reference.json` generator that derives all 64 gua (names, trigrams, palace, sequence) programmatically and writes `src/mingli_engine/data/liuyao/gua_reference.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Deterministic primitives every user story depends on. CRITICAL: no story work before this phase completes.

- [x] T003 Write failing tests for trigram/palace constants and the 京房八宫 sequence in `tests/unit/test_liuyao_constants.py`
- [x] T004 Implement eight-trigram primitives (lines, element, xiantian index), the 64-gua palace table, and shi/ying derivation (本宫世六、一至五世、游魂世四、归魂世三、应隔三位) in `src/mingli_engine/liuyao/constants.py`
- [x] T005 Write failing tests for immutable chart/line/result model validation (line counts, position uniqueness, mode-field consistency) in `tests/unit/test_liuyao_najia.py`
- [x] T006 Implement the frozen dataclasses from data-model.md (`LiuyaoLineInput`, `LiuyaoCastRequest`, `TrigramInfo`, `GuaInfo`, `LiuyaoLine`, `HiddenSpirit`, `LiuyaoChart`) in `src/mingli_engine/liuyao/result_models.py`
- [x] T007 Write failing tests for month-command/day-ganzhi/xun-void/month-break derivation against known calendar dates in `tests/unit/test_liuyao_najia.py`
- [x] T008 Implement `calendar_bridge.py`: month command from solar terms, day ganzhi, xun void branches, month break, day-break clash flags via `calendar_provider`

---

## Phase 3: User Story 1 - 显式录入六爻获得装卦与分析 (Priority: P1) 🎯 MVP

**Goal**: Explicit six-line input produces a complete, field-exact najia assembly.

**Independent Test**: Assemble ≥20 classical golden vectors (covering all eight palaces, moving lines, hidden spirits, void, breaks) with 100% field-exact match.

- [x] T009 [US1] Write failing golden-vector tests for najia line assembly （纳甲干支、五行、六亲、六神、世应) for at least 20 reference charts in `tests/unit/test_liuyao_najia.py` (fixtures under `tests/fixtures/liuyao/golden_vectors.json`)
- [x] T010 [US1] Implement najia assembly in `src/mingli_engine/liuyao/najia.py`: per-line ganzhi from trigram najia rules, element, six-relation from palace element, shi/ying markers, hidden-spirit borrowing from palace head gua, six-spirit assignment by day stem
- [x] T011 [US1] Write failing tests for bian-gua （变卦） and hu-gua （互卦） derivation including no-moving-line behavior in `tests/unit/test_liuyao_najia.py`
- [x] T012 [US1] Implement changed/nuclear gua resolution and full `LiuyaoChart` assembly (void/month-break/day-break flags from T008) in `src/mingli_engine/liuyao/najia.py`
- [x] T013 [US1] Write failing tests for explicit-mode request validation and determinism (20 identical invocations byte-exact) in `tests/unit/test_liuyao_casting.py`
- [x] T014 [US1] Implement explicit casting and the public `assemble_liuyao_chart(request)` entry in `src/mingli_engine/liuyao/casting.py` and `liuyao/__init__.py`

**Checkpoint**: US1 independently testable — every golden vector passes; determinism proven.

---

## Phase 4: User Story 2 - 时间起卦与数字起卦 (Priority: P2)

**Goal**: Time-based and number-based casting convert deterministically into the same six-line model and assemble identically.

**Independent Test**: Documented conversion samples for both modes produce the expected six lines and assemble the same chart as equivalent explicit input.

- [x] T015 [P] [US2] Write failing tests for time casting (year-branch+month+day / +hour conversion, mod-8/mod-6 zero mapping) in `tests/unit/test_liuyao_casting.py`
- [x] T016 [P] [US2] Write failing tests for number casting (two-number conversion, validation of exactly two positive integers) in `tests/unit/test_liuyao_casting.py`
- [x] T017 [US2] Implement time and number casting conversions plus lunar-date fields via lunar-python in `src/mingli_engine/liuyao/casting.py`

**Checkpoint**: US2 independently testable; all three modes share one chart pipeline.

---

## Phase 5: User Story 3 - 传统方法解读报告 (Priority: P2)

**Goal**: A boundary-guarded deterministic Markdown report over the eight independent liuyao rule families, with graceful evidence-pending degradation.

**Independent Test**: Fixed charts produce byte-identical reports with disclaimer, fixed family order, limitation language, zero absolute wording, and 100% high-risk refusal/narrowing.

- [x] T018 [P] [US3] Write failing tests for the eight-family structural analysis (yong-shen candidates, shi/ying relation, moving-line dynamics, six-spirits attachment, month/day strength, void/break state, yingqi candidates, category scaffold) in `tests/unit/test_liuyao_analysis.py`
- [x] T019 [US3] Write failing loader tests for the governed analysis configuration in `tests/unit/test_liuyao_analysis.py`, then create `src/mingli_engine/data/liuyao/analysis_config.json` (eight families in fixed order, headline templates, evidence-pending wording, prohibited-wording reuse)
- [x] T020 [US3] Implement `analysis.py`: governed per-family observations with status computed/degraded/not_computed, limitation wording, and evidence-pending notes from `data/liuyao/analysis_config.json`
- [x] T021 [P] [US3] Write failing tests for the report boundary (disclaimer presence, absolute-wording absence, high-risk refusal/narrowing, determinism) in `tests/unit/test_liuyao_report.py`
- [x] T022 [US3] Implement `report.py` + `report_markdown.py`: report model, safety/high-risk gating through the reused classifiers, deterministic Markdown sections per contract
- [x] T023 [P] [US3] Write failing CLI contract tests (bounded input, mode/field mismatch errors, exit codes, no persistence) in `tests/integration/test_liuyao_cli.py`
- [x] T024 [US3] Add `liuyao-calculate` and `liuyao-report` subcommands to `src/mingli_engine/cli.py` and the example file `examples/liuyao-cast.explicit.json`

**Checkpoint**: US3 independently testable; release-gate boundary checks provable from CLI output.

---

## Phase 6: User Story 4 - 六爻知识学习与传统校准 (Priority: P3)

**Goal**: Liuyao knowledge namespace scaffolding and a synthetic calibration corpus with dual-review conformance metrics, without touching bazi chains.

**Independent Test**: Promoted liuyao records carry file-hash+page locators; calibration metrics compute from synthetic cases only; every bazi artifact hash is unchanged.

- [x] T025 [P] [US4] Write failing tests for the independent liuyao evidence namespace (family enum isolation, empty-namespace degradation) in `tests/unit/test_liuyao_analysis.py`
- [x] T026 [US4] Implement the `LIUYAO_RULE_FAMILIES` namespace and liuyao evidence/config loaders in `src/mingli_engine/liuyao/constants.py` and `analysis.py`
- [x] T027 [US4] Add the liuyao family-map overlay for the 101 extracted batch candidates (digest-frozen `data/liuyao/batch_20260714_liuyao_family_map.json`) with failing loader tests first
- [x] T028 [US4] Promote the mapped batch candidates into the independent liuyao evidence namespace: append-only linked candidate, review, batch, and evidence records under `src/mingli_engine/data/liuyao/` reusing the batch_20260714 pipeline contracts, with failing promotion-gate tests first
- [x] T029 [US4] Build the synthetic calibration corpus (≥40 assertions covering all eight families, mandatory boundary/refusal cases) under `src/mingli_engine/data/liuyao/calibration/` with failing validation tests first
- [x] T030 [US4] Implement calibration execution (dual independent review, adjudication, conformance metrics) mirroring the 019 patterns in `src/mingli_engine/liuyao/` modules
- [x] T031 [US4] Verify zero disturbance: byte-compare all bazi data artifacts and rerun the full suite plus 019 calibration summaries

**Checkpoint**: US4 independently testable; conformance metrics and non-disturbance provable.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T032 Run the full release-gate sequence from plan.md (golden vectors, determinism ×3 modes ×20, boundary, privacy no-write, full pytest, focused mypy/Ruff, `git diff --check`)
- [x] T033 Update `docs/classical_sources/` orientation notes and the batch learning handoff to reference the liuyao V1 boundary and evidence-pending state
- [x] T034 Final consistency pass across spec.md, plan.md, data-model.md, contracts, quickstart.md, and tasks.md

---

## Dependencies

- Phase 1 → Phase 2 → all stories
- US1 (Phase 3) blocks US2/US3 (shared chart pipeline)
- US2 (Phase 4) depends only on Phase 2; can run parallel to US1 after Phase 2
- US3 (Phase 5) depends on US1 (needs charts) and T019 (analysis config); T018/T021/T023 test-authoring can parallelize
- US4 (Phase 6) depends on US3 (analysis layer); promotion (T028) follows the family map (T027); knowledge/calibration stages follow it
- Phase 7 requires all prior phases

## Parallel Execution Examples

- After Phase 2: T009 (golden vectors) ∥ T015+T016 (casting tests) — different files
- Within US3: T018 (analysis tests) ∥ T021 (report tests) ∥ T023 (CLI tests) — different files
- Within US4: T025 (namespace tests) ∥ T027 (family map) — different files

## Implementation Strategy

1. **MVP first**: Phases 1-3 deliver a field-exact najia assembly with golden vectors — independently demonstrable.
2. **Incremental**: US2 adds casting modes without touching US1 code paths; US3 adds analysis/report/CLI; US4 adds knowledge/calibration governance.
3. **Red-green discipline**: every task writes or updates failing tests before implementation; each phase closes with the plan's verification commands.
4. **Zero disturbance gate**: after every phase, rerun the full suite; any bazi regression stops the phase.
