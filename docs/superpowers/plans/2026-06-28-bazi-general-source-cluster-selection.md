# Bazi General Source Cluster Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-bazi-general-source-cluster-selection` by turning the 184-file `raw_text_triage_bazi_general` backlog into bounded cluster-selection metadata and choosing the next high-value source-selection surface.

**Architecture:** Add a separate raw-text cluster-selection layer instead of overloading the Liang source-selection model, because the existing source-selection items require already registered source-library entries. The new layer uses only inventory CSV counts, path labels, representative paths, and guardrails; it does not open source files, register sources, or mutate 013/012 data.

**Tech Stack:** Python dataclasses, JSON metadata, PowerShell/CSV inventory inspection, pytest, existing `materials_audit.py` validation and rendering patterns.

---

## Files

- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_source_cluster_selection_items.json`
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Create: `docs/superpowers/plans/2026-06-28-bazi-general-source-cluster-selection.md`

## Tasks

### Task 1: RED Tests

- [x] Add dataclass smoke tests for `RawTextSourceClusterSelectionItem` and `RawTextSourceClusterSelectionSummary`.
- [x] Add loader tests proving the bazi-general cluster packet has 7 clusters, all under `raw_text_triage_bazi_general`, with file counts summing to 184 and priority counts summing to 183.
- [x] Add summary tests proving selected clusters, deferred clusters, boundary checks, and next material entry are deterministic.
- [x] Add markdown/docs sync tests for `015 Bazi General Source Cluster Selection`.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q` and confirm failures before implementation.

### Task 2: Models And Loader

- [x] Add `RawTextSourceClusterSelectionItem` to `src/mingli_engine/models.py` with cluster id, triage group, counts, extension counts, representative paths, target rule families, status, recommended action, rationale, guardrails, and timestamps.
- [x] Add `RawTextSourceClusterSelectionSummary` to `src/mingli_engine/models.py` with summary counts, selected/deferred cluster ids, boundary checks, next material entry, and guardrails.
- [x] Add constants for `015-bazi-general-source-cluster-selection`, `raw_text_triage_bazi_general`, and `015-bazi-general-cluster-source-selection`.
- [x] Implement `load_raw_text_source_cluster_selection_items()` with uniqueness and field validation.

### Task 3: Cluster Data And Summary

- [x] Create `raw_text_source_cluster_selection_items.json` with 7 mutually exclusive clusters:
  - `bazi_general_foundation_textbook_cluster`
  - `bazi_general_classical_reference_cluster`
  - `bazi_general_case_collection_cluster`
  - `bazi_general_modern_method_series_cluster`
  - `bazi_general_practical_formula_cluster`
  - `bazi_general_sensitive_topic_cluster`
  - `bazi_general_misc_identity_review_cluster`
- [x] Mark the foundation and classical reference clusters as selected for next source selection.
- [x] Keep modern method series and misc identity review behind identity review, and keep sensitive topic cluster behind boundary review.
- [x] Implement `build_raw_text_source_cluster_selection_summary()` with checks that clustered counts match the triage group and that no downstream mutation is authorized.
- [x] Implement `render_raw_text_source_cluster_selection_markdown()`.
- [x] Include cluster-selection text fields in `validate_materials_audit_quality()`.

### Task 4: Docs

- [x] Update `docs/classical_sources/materials_audit.md` with the rendered cluster-selection markers and selected cluster ids.
- [x] Update `docs/classical_sources/new_material_learning_handoff.md` to mark this goal complete and set the next long goal to `015-bazi-general-cluster-source-selection`.
- [x] Preserve historical Liang source-selection and individual-review markers already used by tests.

### Task 5: Verification And Commit

- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q`.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q`.
- [x] Run `uv run --with pytest python -m pytest -q` with UTF-8 output on Windows.
- [x] Run `validate_materials_audit_quality()` and `validate_learning_reference_quality()` and confirm both return `[]`.
- [x] Run `git diff --check`.
- [x] Commit locally with `feat: select bazi general source clusters`.
