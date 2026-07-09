# 013 Explicit Candidate Review Or 015 Queue Refresh Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the `013-explicit-candidate-review-or-015-queue-refresh` routing stage without creating 013 candidates or 012 formal evidence.

**Architecture:** Add a read-only routing record that links the completed sensitive preparation-reading stage, the 017 authorization audit, and the 015 queue refresh summary. Because downstream mutation remains unauthorized in the audit packet, the routing summary selects the queue-refresh path and advances the handoff to `015-external-material-inventory-refresh`.

**Tech Stack:** Python dataclasses, project-local JSON, existing `materials_audit` and `learning_reference_curation` validators, pytest via `uv run --with pytest python -m pytest`.

---

### Task 1: Add RED Tests

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] Add public callable tests for the routing loader, summary, and renderer.
- [x] Add item and summary tests asserting the routing selects `015-external-material-inventory-refresh`.
- [x] Add docs sync tests and advance the handoff final marker.

### Task 2: Add Data And Models

**Files:**
- Create: `src/mingli_engine/data/materials_audit/explicit_candidate_review_or_queue_refresh_items.json`
- Modify: `src/mingli_engine/models.py`

- [x] Add one routing JSON item.
- [x] Add routing item and summary dataclasses.

### Task 3: Implement Routing Logic

**Files:**
- Modify: `src/mingli_engine/materials_audit.py`

- [x] Add loader validation against sensitive preparation-reading, authorization audit, and queue refresh.
- [x] Add summary builder with read-only 013/012 delta counts.
- [x] Add markdown renderer.
- [x] Add quality scanning for rationale and guardrails.

### Task 4: Sync Documentation

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`

- [x] Insert the rendered routing section after sensitive preparation-reading.
- [x] Advance next markers to `015-external-material-inventory-refresh`.

### Task 5: Verify And Commit

- [x] Run focused routing tests.
- [x] Run `tests/unit/test_materials_audit.py`.
- [x] Run `tests/unit/test_learning_reference_curation.py`.
- [x] Run quality validators.
- [x] Run full `uv run --with pytest python -m pytest -q`.
- [x] Run `git diff --check`.
- [x] Commit with message `feat: route explicit candidate review gate`.
