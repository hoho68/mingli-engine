# Bazi General Registration Prep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-bazi-general-registration-prep` by preparing source-library registration metadata for the three Bazi general identity-review records that are ready for registration prep.

**Architecture:** Add a registration-prep layer after source identity review. The layer records proposed source-library entry payload fields for review, verifies they do not duplicate existing source-library entries, and keeps actual source-library mutation blocked for a later explicit source-registration step.

**Tech Stack:** Python dataclasses, JSON metadata, pytest, existing `materials_audit.py` validation and rendering patterns.

---

## Files

- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_source_registration_prep_items.json`
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Create: `docs/superpowers/plans/2026-06-28-bazi-general-registration-prep.md`

## Tasks

### Task 1: RED Tests

- [x] Add dataclass smoke tests for `RawTextSourceRegistrationPrepItem` and `RawTextSourceRegistrationPrepSummary`.
- [x] Add loader tests proving exactly 3 registration-prep records load and each references a `registration_prep_ready` identity review record.
- [x] Add summary tests proving 3 proposed entries, 4 proposed source files, 2 skipped existing Batch 001 overlaps, 2 blocked variant-choice records, and 1 deferred large-source record.
- [x] Add markdown/docs sync tests for `015 Bazi General Registration Prep`.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q` and confirm failures before implementation.

### Task 2: Models And Loader

- [x] Add `RawTextSourceRegistrationPrepItem` to `src/mingli_engine/models.py` with prep id, identity review id, proposed source-library entry fields, local references, topic tags, rule families, risk/rights/readiness metadata, overlap policy, rationale, guardrails, and timestamps.
- [x] Add `RawTextSourceRegistrationPrepSummary` with prep counts, skipped/blocked/deferred counts, proposed ids, boundary checks, next material entry, and guardrails.
- [x] Add constants for `015-bazi-general-registration-prep`, registration-prep statuses, overlap policies, and `015-bazi-general-source-registration`.
- [x] Implement `load_raw_text_source_registration_prep_items()` with uniqueness, enum validation, identity-review link validation, non-duplicate proposed source ids, source-root-relative paths, and required guardrails.

### Task 3: Registration Prep Data And Summary

- [x] Create `raw_text_source_registration_prep_items.json` with 3 records:
  - `bazi_general_registration_prep_lecture_textbook`
  - `bazi_general_registration_prep_beichen_intro`
  - `bazi_general_registration_prep_ziping_orthodox_pair`
- [x] Mark all proposed entries as `registration_status=ready_for_source_registration`, `proposed_tracking_status=external_untracked`, `proposed_readiness_status=needs_preparation`, and `proposed_next_action=prepare_material`.
- [x] Preserve source-root-relative local references: one file for lecture textbook, one file for Beichen intro, and two files for the Ziping pair.
- [x] Implement `build_raw_text_source_registration_prep_summary()` and `render_raw_text_source_registration_prep_markdown()`.
- [x] Include registration-prep text fields in `validate_materials_audit_quality()`.

### Task 4: Docs

- [x] Update `docs/classical_sources/materials_audit.md` with rendered registration-prep markers, proposed entry ids, skipped overlap ids, variant-choice ids, and deferred ids.
- [x] Update `docs/classical_sources/new_material_learning_handoff.md` to mark this goal complete and set the next long goal to `015-bazi-general-source-registration`.
- [x] Preserve existing Liang, bazi-general cluster-selection, cluster-source-selection, and identity-review markers used by tests.

### Task 5: Verification And Commit

- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q`.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q`.
- [x] Run `uv run --with pytest python -m pytest -q` with UTF-8 output on Windows.
- [x] Run `validate_materials_audit_quality()` and `validate_learning_reference_quality()` and confirm both return `[]`.
- [x] Run `git diff --check`.
- [x] Commit locally with `feat: prepare bazi general source registration`.
