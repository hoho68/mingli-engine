# Raw Text Next Cycle Gated Cluster Review Prep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bounded 015 preparation layer for the raw-text next-cycle gated clusters.

**Architecture:** Reuse the existing materials-audit JSON validation style by adding a gated-cluster review prep layer after followup selection. This layer references the already deferred case/formula clusters and sensitive risk-review cluster, records why no source-library/013/012 mutation is performed in this prep step, and advances the next entry to bounded ordinary gated source selection.

**Tech Stack:** Python dataclasses, existing materials-audit JSON metadata, pytest, existing documentation snapshots.

---

### Task 1: RED Tests

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] Add public-function expectations for `load_raw_text_next_cycle_gated_cluster_review_prep_items`, `build_raw_text_next_cycle_gated_cluster_review_prep_summary`, and `render_raw_text_next_cycle_gated_cluster_review_prep_markdown`.
- [x] Add tests expecting three gated prep items:
  - `gated_prep_case_collection_boundary_001`
  - `gated_prep_practical_formula_boundary_001`
  - `gated_prep_sensitive_topic_boundary_001`
- [x] Assert case/formula items are ordinary-risk and prepared only for later bounded source selection.
- [x] Assert the sensitive item remains risk-review required and has no source-library/013/012 mutation.
- [x] Assert summary markers document `selected-for-source-selection=2`, `risk-review-required=1`, `source-library-mutation-authorized=false`, `downstream-mutation-authorized=false`, and `next-material-entry=015-raw-text-next-cycle-gated-ordinary-source-selection`.
- [x] Update handoff next start marker to `015-raw-text-next-cycle-gated-ordinary-source-selection`.
- [x] Run focused tests and verify they fail before implementation.

### Task 2: Implementation

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_gated_cluster_review_prep_items.json`

- [x] Add `RawTextNextCycleGatedClusterReviewPrepItem` and `RawTextNextCycleGatedClusterReviewPrepSummary` dataclasses.
- [x] Add constants for the prep id, allowed prep statuses, and next material entry.
- [x] Add loader validation that references existing next-cycle source-selection items.
- [x] Add summary checks that case/formula remain ordinary, sensitive remains gated, no source-library/013/012 mutation occurs, and raw materials stay untouched.
- [x] Add markdown renderer for docs and handoff markers.
- [x] Add the new prep data file with three cluster-level prep records.

### Task 3: Docs And Handoff

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`

- [x] Add a `015 Raw Text Next Cycle Gated Cluster Review Prep` section to materials audit docs.
- [x] Update handoff completed checkpoints, frozen snapshot, continuation entry point, and next long goal.
- [x] Keep authorization docs explicit that this prep step does not create source-library entries, candidates, reviews, promotions, or formal evidence.

### Task 4: Verification And Commit

- [x] Run focused materials-audit and handoff tests.
- [x] Run quality gates.
- [x] Run full test suite.
- [x] Run `git diff --check`.
- [x] Commit locally with message `feat: prepare gated raw text clusters`.
