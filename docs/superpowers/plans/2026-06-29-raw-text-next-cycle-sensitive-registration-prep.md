# Raw Text Next Cycle Sensitive Registration Prep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-raw-text-next-cycle-sensitive-registration-prep` by preparing source-library registration metadata for `sensitive_source_review_bazi_psychology_pdf` without actually creating source-library, 013, or 012 records.

**Architecture:** Add a sensitive-specific registration-prep metadata layer after source-level risk review. The layer records proposed source-library ids, title, local reference, risk notes, and guardrails, while preserving the existing separation between registration preparation and actual source registration/downstream candidate evidence workflows.

**Tech Stack:** Python 3.12 dataclasses, project-local JSON metadata, pytest, Markdown docs.

---

### Task 1: RED Tests For Sensitive Registration Prep

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Add public API expectations**

Add `load_raw_text_next_cycle_sensitive_registration_prep_items`, `build_raw_text_next_cycle_sensitive_registration_prep_summary`, and `render_raw_text_next_cycle_sensitive_registration_prep_markdown` to the materials-audit public callable test.

- [x] **Step 2: Add item loader tests**

Expect one prep record:
- `sensitive_registration_prep_bazi_psychology_pdf`,
- references `sensitive_source_review_bazi_psychology_pdf`,
- has status `ready_for_sensitive_source_registration`,
- proposes `entry_bazi_general_bazi_psychology_pdf`,
- proposes `material_bazi_general_bazi_psychology_pdf`,
- uses `陆致极王明谦-《八字心理学》东方心理哲学智慧214页.pdf`,
- keeps source-library and downstream mutation flags false.

- [x] **Step 3: Add summary closure tests**

Assert:
- `prep_id == "015-raw-text-next-cycle-sensitive-registration-prep"`,
- `prep_status == "sensitive_registration_prep_completed"`,
- one prep item and one proposed file,
- source-library/candidate/evidence counts stay zero,
- proposed entry/material ids are available and not yet registered,
- `next_material_entry == "015-raw-text-next-cycle-sensitive-source-registration"`,
- all boundary checks pass.

- [x] **Step 4: Add markdown/docs sync tests**

Assert rendered markers appear in:
- `docs/classical_sources/materials_audit.md`,
- `docs/classical_sources/new_material_learning_handoff.md`.

- [x] **Step 5: Run RED focused tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -k sensitive_registration_prep -q`

Expected: fail because the loader, summary, renderer, and JSON data do not exist yet.

### Task 2: Implement Sensitive Registration Prep Metadata

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_sensitive_registration_prep_items.json`

- [x] **Step 1: Add dataclasses**

Add `RawTextNextCycleSensitiveRegistrationPrepItem` and `RawTextNextCycleSensitiveRegistrationPrepSummary`.

- [x] **Step 2: Add constants and imports**

Add:
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_REGISTRATION_PREP_ID`,
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_REGISTRATION_PREP_NEXT_MATERIAL_ENTRY`,
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_REGISTRATION_PREP_STATUSES`.

- [x] **Step 3: Add parser and loader**

Validate:
- the item references the cleared source-level review,
- the review is cleared for sensitive registration prep,
- proposed local references match the reviewed path,
- proposed source-library ids are available or match an existing compatible entry,
- risk tier remains `sensitive`,
- `proposed_readiness_status == "needs_preparation"`,
- `proposed_next_action == "prepare_material"`,
- source-library and downstream mutation remain unauthorized.

- [x] **Step 4: Add summary and renderer**

The summary must verify:
- source-level risk review is complete,
- proposed entry/material ids are available and not registered yet,
- blocked/deferred sensitive prep items remain unavailable,
- no source-library, 013, or 012 records were created,
- external raw materials were not read, moved, converted, or rewritten.

- [x] **Step 5: Include prep items in text-quality validation**

Load new items in `validate_materials_audit_quality()` and include proposed title, references, source quality notes, rights notes, risk notes, rationale, and guardrails in `_iter_quality_text_fields()`.

- [x] **Step 6: Add JSON record**

Create one record:
- `sensitive_registration_prep_bazi_psychology_pdf`.

- [x] **Step 7: Run focused tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -k sensitive_registration_prep -q`

Expected: pass after docs sync is complete.

### Task 3: Update Docs And Handoff

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Insert rendered sensitive registration-prep markdown**

Generate `render_raw_text_next_cycle_sensitive_registration_prep_markdown(summary)` and insert it after the sensitive source-level risk review section.

- [x] **Step 2: Update handoff next target**

Change the next target from `015-raw-text-next-cycle-sensitive-registration-prep` to `015-raw-text-next-cycle-sensitive-source-registration`.

- [x] **Step 3: Update quickstart marker**

Change `next-new-material-start` to `015-raw-text-next-cycle-sensitive-source-registration`.

- [x] **Step 4: Run docs tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py::test_new_material_learning_handoff_tracks_final_state -q`

Expected: pass.

### Task 4: Verify And Commit

**Files:**
- All changed files.

- [x] **Step 1: Run focused materials-audit tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q`

- [x] **Step 2: Run quality gates**

Run the project quality-gate command for source-library, materials-audit, extraction-queue-intake, learning-reference-curation, and source-intake validators.

- [x] **Step 3: Run full tests**

Run: `uv run --with pytest python -m pytest -q`

- [x] **Step 4: Inspect diff**

Run: `git diff --check` and `git diff --stat`.

- [x] **Step 5: Commit**

Stage and commit with:

```bash
git add .
git commit -m "feat: prep sensitive raw text source registration"
```

After the commit, mark the goal complete and tell the user the next target is `015-raw-text-next-cycle-sensitive-source-registration`.
