# 015 External Material Inventory Refresh Confirmation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Confirm the current `015-external-material-inventory-refresh` entrypoint after the explicit candidate-review gate routes back to 015, without mutating raw materials or downstream 013/012 data.

**Architecture:** Add a read-only confirmation record that links the completed `013-explicit-candidate-review-or-015-queue-refresh` routing item to the existing external inventory refresh summary. The confirmation reuses the existing path-label inventory scanner and advances the handoff to `015-raw-text-next-cycle-source-selection` when there are no untracked immediate entries.

**Tech Stack:** Python dataclasses, project-local JSON, existing `materials_audit` validators, pytest via `uv run --with pytest python -m pytest`.

---

### Task 1: Add RED Tests

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] Add public callable checks for the confirmation loader, summary, and renderer.
- [x] Add item and summary tests that assert the confirmation routes to `015-raw-text-next-cycle-source-selection`.
- [x] Add docs sync tests and advance the handoff final marker.

### Task 2: Add Data And Models

**Files:**
- Create: `src/mingli_engine/data/materials_audit/external_material_inventory_refresh_confirmation_items.json`
- Modify: `src/mingli_engine/models.py`

- [x] Add one confirmation JSON item.
- [x] Add `ExternalMaterialInventoryRefreshConfirmationItem`.
- [x] Add `ExternalMaterialInventoryRefreshConfirmationSummary`.

### Task 3: Implement Confirmation Logic

**Files:**
- Modify: `src/mingli_engine/materials_audit.py`

- [x] Add loader validation against the explicit routing summary and existing external inventory summary.
- [x] Add summary builder with read-only 013/012 delta counts.
- [x] Add markdown renderer.
- [x] Add quality scanning for rationale and guardrails.

### Task 4: Sync Documentation

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`

- [x] Insert the rendered confirmation section after the routing section.
- [x] Advance next markers to `015-raw-text-next-cycle-source-selection`.

### Task 5: Verify And Commit

- [x] Run focused confirmation tests.
- [x] Run `tests/unit/test_materials_audit.py`.
- [x] Run `tests/unit/test_learning_reference_curation.py`.
- [x] Run quality validators.
- [x] Run full `uv run --with pytest python -m pytest -q`.
- [x] Run `git diff --check`.
- [x] Commit with message `feat: confirm external inventory refresh route`.
