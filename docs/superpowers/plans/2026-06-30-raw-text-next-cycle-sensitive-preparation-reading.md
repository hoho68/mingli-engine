# 015 Raw Text Next Cycle Sensitive Preparation Reading Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the bounded sensitive preparation-reading stage for `entry_bazi_general_bazi_psychology_pdf` without creating 013 candidates or 012 formal evidence.

**Architecture:** Reuse the existing materials-audit pipeline style: add a small JSON record, typed dataclasses, loader validation, summary builder, markdown renderer, quality scanning hooks, docs sync, and tests. The stage depends on the completed sensitive preparation boundary and validates only registered metadata/path labels plus safe boundary notes; it does not mutate source-library readiness, raw materials, 013, or 012.

**Tech Stack:** Python dataclasses, project-local JSON, existing `materials_audit` validators, pytest via `uv run --with pytest python -m pytest`.

---

### Task 1: Add RED Tests

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] Add the new public callable names:
  - `load_raw_text_next_cycle_sensitive_preparation_reading_items`
  - `build_raw_text_next_cycle_sensitive_preparation_reading_summary`
  - `render_raw_text_next_cycle_sensitive_preparation_reading_markdown`
- [x] Add tests for one preparation-reading item tied to `sensitive_preparation_boundary_bazi_psychology_pdf`.
- [x] Add summary tests that assert source file count 1, safe note count 3, candidate/evidence counts 0, downstream mutation false, and next entry `013-explicit-candidate-review-or-015-queue-refresh`.
- [x] Add markdown/docs sync markers for materials audit and handoff docs.

### Task 2: Add Data And Models

**Files:**
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_sensitive_preparation_reading_items.json`
- Modify: `src/mingli_engine/models.py`

- [x] Add one JSON item for `sensitive_preparation_reading_bazi_psychology_pdf`.
- [x] Add `RawTextNextCycleSensitivePreparationReadingItem`.
- [x] Add `RawTextNextCycleSensitivePreparationReadingSummary`.

### Task 3: Implement Loader, Summary, Renderer, Quality Hooks

**Files:**
- Modify: `src/mingli_engine/materials_audit.py`

- [x] Add constants for `015-raw-text-next-cycle-sensitive-preparation-reading` and next entry `013-explicit-candidate-review-or-015-queue-refresh`.
- [x] Add loader validation tied to the completed preparation-boundary item and source-library entry.
- [x] Add summary checks for metadata-only reading, source path relativity, safe-note coverage, and blocked 013/012 mutation.
- [x] Add markdown renderer.
- [x] Add quality text scanning for rationale, safe reading notes, sensitive controls, local references, and guardrails.

### Task 4: Sync Documentation

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`

- [x] Insert the rendered sensitive preparation-reading section after the preparation-boundary section.
- [x] Advance current handoff and quickstart markers to `013-explicit-candidate-review-or-015-queue-refresh`.
- [x] Update Next Long Goal and Next Target to the explicit candidate-review-or-queue-refresh gate.

### Task 5: Verify And Commit

**Files:**
- Modify: this plan file

- [x] Run focused tests for `sensitive_preparation_reading`.
- [x] Run `tests/unit/test_materials_audit.py`.
- [x] Run `tests/unit/test_learning_reference_curation.py`.
- [x] Run local quality validators.
- [x] Run full `uv run --with pytest python -m pytest -q`.
- [x] Run `git diff --check`.
- [x] Commit with message `feat: add sensitive raw text preparation reading`.
