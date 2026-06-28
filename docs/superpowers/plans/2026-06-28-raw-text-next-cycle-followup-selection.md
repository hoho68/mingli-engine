# Raw Text Next Cycle Followup Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the next authorized ordinary-risk followup source slice for the raw-text next-cycle modern-method and miscellaneous clusters.

**Architecture:** Reuse the existing 015 materials-audit JSON validation style by adding a followup-selection layer that references the already completed cluster-source selection. Register two more weak-locator source-level records through source-library, 016/017, 013, and 012 while keeping raw external files untouched and keeping case/formula/sensitive clusters gated.

**Tech Stack:** Python dataclasses, existing JSON metadata stores, pytest, existing source-library/source-intake/classical-source validators.

---

### Task 1: RED Tests

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_source_library.py`
- Modify: `tests/unit/test_extraction_queue_intake.py`
- Modify: `tests/unit/test_learning_reference_curation.py`
- Modify: `tests/unit/test_source_intake.py`
- Modify: `tests/unit/test_classical_sources.py`
- Modify: `tests/unit/test_evidence_curation.py`
- Modify: `tests/integration/test_report_regression_cases.py`

- [x] Add tests expecting `015-raw-text-next-cycle-followup-selection` to load two selected source-level records:
  - `next_cycle_followup_source_xinpai_essence_part2`
  - `next_cycle_followup_source_xingming_shuozheng_vol1`
- [x] Add tests expecting two source-library entries and priority assessments.
- [x] Add tests expecting 016 package/tasks/candidate slots for the two weak locator anchors.
- [x] Add tests expecting 017 learning notes/points/decisions for the two anchors.
- [x] Add tests expecting two 013 candidates, review decisions, one promotion batch, two 012 sources/evidence units, and one curation batch.
- [x] Update snapshot counts for source-library, 016, 017, 013, 012, and coverage.
- [x] Run focused tests and verify they fail before implementation.

### Task 2: Implementation

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_followup_selection_items.json`
- Modify existing JSON stores under `source_library`, `materials_audit`, `extraction_queue_intake`, `learning_reference_curation`, `source_intake`, and `classical_sources`.

- [x] Add `RawTextNextCycleFollowupSelectionItem` and summary dataclasses.
- [x] Add loader, summary, renderer, and quality-gate text coverage.
- [x] Add source-library entries, priority assessments, material audit records, representations, readiness, alignments, and queue items.
- [x] Add 016 package/tasks/slots.
- [x] Add 017 notes/points/decisions.
- [x] Add 013 source materials/candidates/reviews/promotion batch.
- [x] Add 012 sources/evidence/curation batch.

### Task 3: Docs And Handoff

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/source_library.md`
- Modify: `docs/classical_sources/extraction_queue_intake.md`
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `docs/classical_sources/intake.md`
- Modify: `docs/classical_sources/coverage.md`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`

- [x] Add the new 015 followup-selection status and selected IDs.
- [x] Document the two weak-locator source-library entries and downstream 013/012 linkage.
- [x] Advance next long goal to `015-raw-text-next-cycle-gated-cluster-review-prep`.

### Task 4: Verification And Commit

- [x] Run material/source-library/source-intake/classical-source/learning quality gates.
- [x] Run focused tests.
- [x] Run full test suite.
- [x] Run `git diff --check`.
- [x] Commit locally with message `feat: add next-cycle followup sources`.
