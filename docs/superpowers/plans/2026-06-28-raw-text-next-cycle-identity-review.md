# Raw Text Next Cycle Identity Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-raw-text-next-cycle-identity-review` for the two selected ordinary next-cycle Bazi general clusters while keeping source-library, 013, 012, and external raw files unchanged.

**Architecture:** Add a cluster-level identity-review metadata layer parallel to the existing 015 raw-text source-selection flow. The new layer validates references back to `raw_text_next_cycle_source_selection_items.json`, summarizes identity/readiness decisions, renders docs/handoff markers, and advances the next long goal to cluster-source selection.

**Tech Stack:** Python dataclasses, JSON metadata under `src/mingli_engine/data/materials_audit/`, pytest, existing `materials_audit.py` validation helpers.

---

### Task 1: RED Tests

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] Add public-function expectations for:
  - `load_raw_text_next_cycle_identity_review_items`
  - `build_raw_text_next_cycle_identity_review_summary`
  - `render_raw_text_next_cycle_identity_review_markdown`
- [x] Add item-loading test expecting 2 records:
  - `next_cycle_identity_bazi_modern_method_series`
  - `next_cycle_identity_bazi_misc_review`
- [x] Add summary test expecting:
  - `review_status=next_cycle_identity_review_completed`
  - `identity-review-items=2`
  - `cluster-source-selection-required=2`
  - `registration-prep-ready=0`
  - `source-library-overlap-found=0`
  - `next-material-entry=015-raw-text-next-cycle-cluster-source-selection`
- [x] Add docs-sync test expecting the generated markers in `materials_audit.md` and `new_material_learning_handoff.md`.
- [x] Update handoff final-state marker to `next-new-material-start=015-raw-text-next-cycle-cluster-source-selection`.
- [x] Run focused tests and verify they fail because the new API/docs do not exist yet.

### Task 2: Implementation

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_identity_review_items.json`

- [x] Add `RawTextNextCycleIdentityReviewItem` and `RawTextNextCycleIdentityReviewSummary`.
- [x] Add constants for:
  - `RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_ID`
  - `RAW_TEXT_NEXT_CYCLE_IDENTITY_REVIEW_NEXT_MATERIAL_ENTRY`
  - allowed identity/review/readiness statuses.
- [x] Implement loader validation:
  - item references an existing selected next-cycle source-selection item.
  - selected cluster id is one of the two authorized next-cycle clusters.
  - file counts, risk boundary, and rule families match the source-selection record.
  - both items remain `cluster_source_selection_required`, not registration-ready.
- [x] Implement summary and renderer with boundary checks:
  - identity items loaded.
  - source-selection references valid.
  - selected clusters only.
  - deferred/risk-gated clusters remain absent.
  - source-library, raw-file, 013, and 012 mutation checks passed.
- [x] Include new items in `validate_materials_audit_quality`.

### Task 3: Docs And Handoff

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: this plan file.

- [x] Add a `015 Raw Text Next Cycle Identity Review` section to materials audit docs.
- [x] Add the same markers to the handoff current snapshot and completed checkpoints.
- [x] Advance `next-new-material-start` and `Next Long Goal` to `015-raw-text-next-cycle-cluster-source-selection`.
- [x] Mark this plan complete after verification passes.

### Task 4: Verification And Commit

**Files:**
- All changed files.

- [x] Run `validate_materials_audit_quality` and expect `[]`.
- [x] Run focused tests for new identity-review cases and handoff final-state.
- [x] Run `tests/unit/test_materials_audit.py`.
- [x] Run `tests/unit/test_learning_reference_curation.py`.
- [x] Run full test suite: `uv run --with pytest python -m pytest -q`.
- [x] Run `git diff --check`.
- [x] Commit locally with message `feat: add raw text next-cycle identity review`.
