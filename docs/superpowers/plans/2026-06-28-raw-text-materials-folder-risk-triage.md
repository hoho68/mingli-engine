# Raw Text Materials Folder Risk Triage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `资料原文/文本类/` from one broad high-risk backlog item into 015 inventory-level triage groups and a next safe source-selection entry.

**Architecture:** Add a small raw-text triage layer inside `materials_audit.py` and `models.py`, backed by one JSON data file under `src/mingli_engine/data/materials_audit/`. The layer reads existing inventory CSV metadata for count verification only, never opens source files, and keeps 013/012 downstream evidence unchanged.

**Tech Stack:** Python dataclasses, JSON, CSV metadata via Python standard library, pytest.

---

## Files

- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_material_triage_groups.json`
- Modify: `src/mingli_engine/data/materials_audit/extraction_queue_items.json`
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Create: `docs/superpowers/plans/2026-06-28-raw-text-materials-folder-risk-triage.md`

## Tasks

- [x] Add failing tests for raw text triage dataclasses, loader, summary, renderer, docs sync, and completed queue refresh.
- [x] Add `RawTextMaterialTriageGroup` and `RawTextMaterialTriageSummary` dataclasses.
- [x] Seed 11 exclusive triage groups covering 1139 inventory rows and 832 priority text candidates.
- [x] Implement `load_raw_text_material_triage_groups()`, `build_raw_text_material_triage_summary()`, and `render_raw_text_material_triage_markdown()`.
- [x] Update queue refresh to exclude locally completed queue items and point next material work to `015-liang-bazi-core-source-selection`.
- [x] Sync maintainer docs and handoff with the completed triage snapshot.
- [x] Run targeted red/green tests and full verification.
- [x] Commit locally and report the next long goal.
