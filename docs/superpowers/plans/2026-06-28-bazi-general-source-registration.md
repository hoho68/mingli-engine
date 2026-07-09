# Bazi General Source Registration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-bazi-general-source-registration` by registering the three prepared Bazi general source-library metadata packets after explicit user authorization.

**Architecture:** Use the three `raw_text_source_registration_prep_items.json` records as the sole source of truth for new source-library entries. Registration mutates only project-tracked source-library metadata, not raw source files, and does not authorize reading, extraction, 013 candidate intake, or 012 evidence changes.

**Tech Stack:** Python dataclasses, JSON metadata, pytest, existing `source_library.py` and `materials_audit.py` validation patterns.

---

## Authorization Gate

This plan must not be executed past Task 1 until the user explicitly authorizes
source-library metadata registration. Required authorization phrase:

`授权注册这 3 条 source-library 元数据`

Authorization received in-thread on 2026-06-28. Registration is now allowed
only for the three prepared Bazi general source-library metadata packets.

Without that authorization, keep the goal active and do not modify
`src/mingli_engine/data/source_library/source_library_entries.json`.

## Files

- Modify: `src/mingli_engine/data/source_library/source_library_entries.json`
- Modify: `src/mingli_engine/data/source_library/source_priority_assessments.json`
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_source_library.py`
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Create: `docs/superpowers/plans/2026-06-28-bazi-general-source-registration.md`

## Tasks

### Task 1: Authorization And RED Tests

- [x] Confirm the exact authorization phrase is present before source-library mutation.
- [x] Add tests proving the three prepared `proposed_entry_id` values exist in `source_library_entries.json`.
- [x] Add tests proving Batch 001 overlap ids were not duplicated.
- [x] Add tests proving variant-choice and deferred ids remain outside source-library registration.
- [x] Add materials-audit summary/docs sync tests for `015 Bazi General Source Registration`.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py tests/unit/test_source_library.py -q` and confirm failures before implementation.

### Task 2: Source-Library Registration

- [x] Append three source-library entries from registration-prep metadata:
  - `entry_bazi_general_lecture_textbook_pdf`
  - `entry_bazi_general_beichen_intro_pdf`
  - `entry_bazi_general_ziping_orthodox_pair_pdf`
- [x] Use the prepared `material_id`, `title`, `material_type`, `local_reference`, `tracking_status`, `readiness_status`, `topic_tags`, `rule_families`, `source_quality_notes`, `rights_notes`, `risk_tier`, `risk_notes`, `priority_level`, and `next_action` fields.
- [x] Keep `readiness_status=needs_preparation` and `next_action=prepare_material`.
- [x] Do not add source-library entries for Youran, Tianma, Ditiansui, Qiongtong, or Huntian Baolan.
- [x] Add high-priority source assessments required by the existing source-library loader.

### Task 3: Registration Audit Layer

- [x] Add source-registration audit dataclasses and JSON metadata, if needed, to record completed registration without blurring into 013/012.
- [x] Implement loader/summary/render functions with checks for:
  - three registered entry ids present
  - skipped Batch 001 overlap ids unchanged
  - variant-choice ids blocked
  - deferred large-source id blocked
  - raw files not mutated
  - 013/012 not mutated
- [x] Include new audit text fields in `validate_materials_audit_quality()` if needed; no new persisted text-field JSON was required.

### Task 4: Docs

- [x] Update `docs/classical_sources/materials_audit.md` with source-registration markers.
- [x] Update `docs/classical_sources/new_material_learning_handoff.md` to mark this goal complete and set the next long goal to the preparation/reading step that follows source registration.
- [x] Preserve existing registration-prep, identity-review, cluster-source-selection, and cluster-selection markers used by tests.

### Task 5: Verification And Commit

- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q` (`59 passed`).
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_source_library.py -q` (`29 passed`).
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q` (`80 passed`).
- [x] Run `uv run --with pytest python -m pytest -q` with UTF-8 output on Windows (`743 passed`).
- [x] Run source-library, materials-audit, and learning-reference quality validators and confirm all return `[]`.
- [x] Run `git diff --check`.
- [x] Commit locally with `feat: register bazi general sources`.
