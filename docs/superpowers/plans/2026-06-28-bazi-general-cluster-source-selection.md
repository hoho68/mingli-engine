# Bazi General Cluster Source Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-bazi-general-cluster-source-selection` by turning the already selected foundation/textbook and classical-reference clusters into concrete source-level selection records for the next identity-review or registration-prep stage.

**Architecture:** Add a source-level selection layer that points to bounded source records inside the two selected clusters. This layer uses only inventory CSV metadata, path labels, existing 015 cluster metadata, and source-library boundary awareness. It does not open large source bodies, parse PDFs, register sources, create 013 candidate data, or alter 012 formal evidence.

**Tech Stack:** Python dataclasses, JSON metadata, PowerShell/CSV inventory inspection, pytest, existing `materials_audit.py` validation and rendering patterns.

---

## Files

- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_cluster_source_selection_items.json`
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Create: `docs/superpowers/plans/2026-06-28-bazi-general-cluster-source-selection.md`

## Tasks

### Task 1: RED Tests

- [x] Add dataclass smoke tests for `RawTextClusterSourceSelectionItem` and `RawTextClusterSourceSelectionSummary`.
- [x] Add loader tests proving selected records are limited to the two selected cluster ids and use only source-root-relative paths.
- [x] Add summary tests proving status counts, source-file counts, extension counts, target rule families, boundary checks, and next material entry are deterministic.
- [x] Add markdown/docs sync tests for `015 Bazi General Cluster Source Selection`.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q` and confirm failures before implementation.

### Task 2: Models And Loader

- [x] Add `RawTextClusterSourceSelectionItem` to `src/mingli_engine/models.py` with selection id, cluster id, triage group, paths, counts, status, identity-review note, rationale, guardrails, and timestamps.
- [x] Add `RawTextClusterSourceSelectionSummary` to `src/mingli_engine/models.py` with source-level counts, selected cluster ids, status counts, boundary checks, next material entry, and guardrails.
- [x] Add constants for `015-bazi-general-cluster-source-selection`, selected cluster ids, status values, and `015-bazi-general-source-identity-review`.
- [x] Implement `load_raw_text_cluster_source_selection_items()` with uniqueness, enum, path, count, and selected-cluster validation.

### Task 3: Source-Level Data And Summary

- [x] Create `raw_text_cluster_source_selection_items.json` with 8 source-level records across the foundation/textbook and classical-reference clusters.
- [x] Mark compact foundation/textbook sources and the paired Ziping source as selected for identity review.
- [x] Mark Ditiansui and Qiongtong variant sets for variant identity review before reuse.
- [x] Defer the oversized Huntian Baolan/Ziping file until after the compact source records are resolved.
- [x] Implement `build_raw_text_cluster_source_selection_summary()` with checks that selected clusters are valid and no downstream mutation is authorized.
- [x] Implement `render_raw_text_cluster_source_selection_markdown()`.
- [x] Include cluster-source selection text fields in `validate_materials_audit_quality()`.

### Task 4: Docs

- [x] Update `docs/classical_sources/materials_audit.md` with rendered cluster-source selection markers, selected source ids, and variant/deferred ids.
- [x] Update `docs/classical_sources/new_material_learning_handoff.md` to mark this goal complete and set the next long goal to `015-bazi-general-source-identity-review`.
- [x] Preserve existing Liang and bazi-general cluster-selection markers already used by tests.

### Task 5: Verification And Commit

- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q`.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q`.
- [x] Run `uv run --with pytest python -m pytest -q` with UTF-8 output on Windows.
- [x] Run `validate_materials_audit_quality()` and `validate_learning_reference_quality()` and confirm both return `[]`.
- [x] Run `git diff --check`.
- [x] Commit locally with `feat: select bazi general source records`.
