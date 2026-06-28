# Bazi General Source Identity Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-bazi-general-source-identity-review` by resolving source identity, existing-batch overlap, variant status, and registration-prep routing for the 8 Bazi general source-level selection records.

**Architecture:** Add a bounded identity-review layer after cluster-source selection. The new layer links every review record back to an existing source-level selection id, may reference existing source-library entries for overlap, and records only planning metadata; it does not mutate source-library entries, read raw source bodies, create 013 candidate data, or alter 012 formal evidence.

**Tech Stack:** Python dataclasses, JSON metadata, pytest, existing `materials_audit.py` validation and rendering patterns.

---

## Files

- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_source_identity_review_items.json`
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Create: `docs/superpowers/plans/2026-06-28-bazi-general-source-identity-review.md`

## Tasks

### Task 1: RED Tests

- [x] Add dataclass smoke tests for `RawTextSourceIdentityReviewItem` and `RawTextSourceIdentityReviewSummary`.
- [x] Add loader tests proving 8 review records load, each references a known `raw_text_cluster_source_selection_items.json` selection id, and existing-batch overlap records reference `entry_markdown_source_batch_001`.
- [x] Add summary tests for deterministic status counts: 2 existing-batch overlaps, 3 registration-prep-ready records, 2 variant-choice records, and 1 deferred large-source record.
- [x] Add markdown/docs sync tests for `015 Bazi General Source Identity Review`.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q` and confirm failures before implementation.

### Task 2: Models And Loader

- [x] Add `RawTextSourceIdentityReviewItem` to `src/mingli_engine/models.py` with review id, source selection id, cluster id, canonical title label, identity status, source-library overlap status, registration readiness, matched source-library entries, recommended action, next review target, rationale, guardrails, and timestamps.
- [x] Add `RawTextSourceIdentityReviewSummary` with review counts, status counts, overlap counts, registration-readiness counts, selected ids, boundary checks, next material entry, and guardrails.
- [x] Add constants for `015-bazi-general-source-identity-review`, status enums, readiness enums, and `015-bazi-general-registration-prep`.
- [x] Implement `load_raw_text_source_identity_review_items()` with uniqueness, enum, source-selection link, selected-cluster link, existing source-library entry validation, and required guardrails.

### Task 3: Identity Review Data And Summary

- [x] Create `raw_text_source_identity_review_items.json` with 8 records:
  - `bazi_general_identity_youran_notes`
  - `bazi_general_identity_tianma_notes`
  - `bazi_general_identity_lecture_textbook`
  - `bazi_general_identity_beichen_intro`
  - `bazi_general_identity_ziping_orthodox_pair`
  - `bazi_general_identity_ditiansui_variant_set`
  - `bazi_general_identity_qiongtong_variant_set`
  - `bazi_general_identity_huntian_baolan_ziping`
- [x] Mark Youran and Tianma as `existing_batch_overlap` with `entry_markdown_source_batch_001`, `registration_readiness=no_registration_needed_existing_batch`, and `recommended_next_action=no_action`.
- [x] Mark lecture textbook, Beichen intro, and Ziping pair as `registration_prep_ready` with `source_library_overlap_status=no_registered_overlap_found` and `recommended_next_action=register_source`.
- [x] Mark Ditiansui and Qiongtong sets as `variant_choice_required` with `recommended_next_action=clarify_identity`.
- [x] Mark Huntian Baolan Ziping as `deferred_large_source` with `recommended_next_action=defer`.
- [x] Implement `build_raw_text_source_identity_review_summary()` and `render_raw_text_source_identity_review_markdown()`.
- [x] Include identity-review text fields in `validate_materials_audit_quality()`.

### Task 4: Docs

- [x] Update `docs/classical_sources/materials_audit.md` with rendered identity-review markers, existing-batch overlaps, registration-prep ids, variant-choice ids, and deferred ids.
- [x] Update `docs/classical_sources/new_material_learning_handoff.md` to mark this goal complete and set the next long goal to `015-bazi-general-registration-prep`.
- [x] Preserve existing Liang, bazi-general cluster-selection, and cluster-source-selection markers used by tests.

### Task 5: Verification And Commit

- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q`.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q`.
- [x] Run `uv run --with pytest python -m pytest -q` with UTF-8 output on Windows.
- [x] Run `validate_materials_audit_quality()` and `validate_learning_reference_quality()` and confirm both return `[]`.
- [x] Run `git diff --check`.
- [x] Commit locally with `feat: review bazi general source identities`.
