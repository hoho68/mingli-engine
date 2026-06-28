# Raw Text Next Cycle Cluster Source Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Select two bounded source-level records from the next-cycle modern-method and miscellaneous Bazi general clusters, then complete the authorized weak-locator source-library, 016/017, 013, and 012 metadata chain.

**Architecture:** Reuse the existing 015 materials-audit JSON validation pattern for a new next-cycle cluster-source selection layer, then append ordinary-risk weak-locator records to the existing source-library, extraction queue, learning-reference, source-intake, and classical-source JSON files. All records remain path-label/locator metadata and do not read, move, convert, or rewrite raw external files.

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

- [x] Add tests expecting `015-raw-text-next-cycle-cluster-source-selection` to load two selected source-level records:
  - `next_cycle_cluster_source_true_spirit_positioning`
  - `next_cycle_cluster_source_mingli_wangdoujing`
- [x] Add tests expecting two source-library entries and priority assessments:
  - `entry_bazi_general_true_spirit_positioning_pdf`
  - `entry_bazi_general_mingli_wangdoujing_pdf`
- [x] Add tests expecting 016 package/tasks/candidate slots for the two weak locator anchors.
- [x] Add tests expecting 017 learning notes/points/decisions for the two anchors.
- [x] Add tests expecting two 013 candidates, review decisions, one promotion batch, two 012 sources/evidence units, and one curation batch.
- [x] Update handoff final-state marker to `next-new-material-start=015-raw-text-next-cycle-followup-selection`.
- [x] Run focused tests and verify they fail because the records/functions do not exist yet.

### Task 2: Implementation

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_cluster_source_selection_items.json`
- Modify existing JSON stores under `source_library`, `materials_audit`, `extraction_queue_intake`, `learning_reference_curation`, `source_intake`, and `classical_sources`.

- [x] Add `RawTextNextCycleClusterSourceSelectionItem` and summary dataclasses.
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

- [x] Add the new 015 cluster-source selection status and selected IDs.
- [x] Document the two weak-locator source-library entries and downstream 013/012 linkage.
- [x] Advance next long goal to `015-raw-text-next-cycle-followup-selection`.

### Task 4: Verification And Commit

- [x] Run material/source-library/source-intake/classical-source/learning quality gates.
- [x] Run focused tests.
- [x] Run full test suite.
- [x] Run `git diff --check`.
- [x] Commit locally with message `feat: select next-cycle raw text sources`.
