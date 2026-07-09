# Liang Bazi Core Source Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-liang-bazi-core-source-selection` by turning the 12-file `raw_text_triage_liang_bazi_core` group into a bounded source-selection packet for the next learning/reference review step.

**Architecture:** Add a small source-selection layer to the existing `materials_audit` module and JSON data directory. The layer uses only tracked metadata and existing inventory CSV/file labels, preserves existing source-library batch coverage, and keeps all 013 candidate, review, promotion, and 012 formal-evidence data unchanged.

**Tech Stack:** Python dataclasses, JSON metadata, CSV count checks, pytest.

---

## Files

- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_source_selection_items.json`
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Create: `docs/superpowers/plans/2026-06-28-liang-bazi-core-source-selection.md`

## Tasks

### Task 1: RED Tests

- [ ] Add tests in `tests/unit/test_materials_audit.py` for `RawTextSourceSelectionItem`, `RawTextSourceSelectionSummary`, loader availability, summary counts, docs sync, queue next entry, and quality validation.
- [ ] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q` and confirm the new tests fail because the source-selection API does not exist yet.

### Task 2: Data Model

- [ ] Add `RawTextSourceSelectionItem` and `RawTextSourceSelectionSummary` dataclasses to `src/mingli_engine/models.py`.
- [ ] Keep defaults consistent with the current audit models: optional lists default to `[]`, optional text defaults to `""`.

### Task 3: Source-Selection Data

- [ ] Create `src/mingli_engine/data/materials_audit/raw_text_source_selection_items.json` with 12 items from `raw_text_triage_liang_bazi_core`.
- [ ] Use four statuses only: `existing_batch_covered`, `ready_for_individual_review`, `variant_review_required`, and `sensitive_boundary_deferred`.
- [ ] Preserve all external raw paths as labels only; do not open, move, convert, rewrite, or delete raw materials.

### Task 4: Loader, Summary, Renderer

- [ ] Implement `load_raw_text_source_selection_items()`.
- [ ] Implement `build_raw_text_source_selection_summary()` with boundary checks:
  - `selection_items_loaded`
  - `triage_group_loaded`
  - `triage_group_file_count_matched`
  - `existing_source_batches_preserved`
  - `raw_materials_not_mutated`
  - `013_012_not_mutated`
- [ ] Implement `render_raw_text_source_selection_markdown()`.
- [ ] Include source-selection items in `validate_materials_audit_quality()`.
- [ ] Make the queue refresh next entry advance to `015-liang-bazi-core-individual-review` after the source-selection packet exists.

### Task 5: Docs

- [ ] Add a `015 Liang Bazi Core Source Selection` section to `docs/classical_sources/materials_audit.md`.
- [ ] Update `docs/classical_sources/new_material_learning_handoff.md` so the next long goal starts at `015-liang-bazi-core-individual-review`.
- [ ] Keep raw-file and evidence-boundary guardrails explicit.

### Task 6: Verification And Commit

- [ ] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q`.
- [ ] Run `uv run --with pytest python -m pytest -q`.
- [ ] Run `uv run python -c "from mingli_engine.materials_audit import validate_materials_audit_quality; print(validate_materials_audit_quality())"` and confirm `[]`.
- [ ] Review `git diff`.
- [ ] Commit locally with `feat: select liang bazi core sources`.
