# Bazi General Variant Choice Deferred Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the 015 Bazi general variant/deferred review surface for Ditiansui, Qiongtong, and Huntian Baolan without mutating raw materials or promoting unclear variants into 013/012.

**Architecture:** Add one read-only materials-audit layer that records variant-choice and deferred-source review conclusions as project metadata. The layer loads a dedicated JSON file, validates it against the existing source-selection and identity-review records, renders a maintainer-facing summary, and syncs the summary into the materials audit and handoff docs.

**Tech Stack:** Python 3.12 dataclasses, JSON metadata, pytest, existing `mingli_engine.materials_audit` validation style.

---

### Task 1: Red Tests For Variant/Deferred Review

**Files:**
- Modify: `tests/unit/test_materials_audit.py`

- [ ] **Step 1: Add failing dataclass and public API tests**

Add assertions for:
- `models.BaziGeneralVariantDeferredReviewItem`
- `models.BaziGeneralVariantDeferredReviewSummary`
- `materials_audit.load_bazi_general_variant_deferred_review_items`
- `materials_audit.build_bazi_general_variant_deferred_review_summary`
- `materials_audit.render_bazi_general_variant_deferred_review_markdown`

- [ ] **Step 2: Add failing current-data tests**

Expected review surface:
- review id: `015-bazi-general-variant-choice-and-deferred-review`
- review status: `variant_deferred_review_completed`
- item count: `3`
- variant items: `2`
- deferred items: `1`
- selected canonical variants: `0`
- source-library registrations authorized: `0`
- downstream mutation authorized: `false`
- next material entry: `015-bazi-general-next-source-batch-preparation`

- [ ] **Step 3: Add failing docs sync test**

Require these markers in both `docs/classical_sources/materials_audit.md` and `docs/classical_sources/new_material_learning_handoff.md`:
- `015 Bazi General Variant Choice And Deferred Review`
- `` `variant-deferred-review-status=variant_deferred_review_completed` ``
- `` `variant-review-items=2` ``
- `` `deferred-review-items=1` ``
- `` `selected-canonical-variants=0` ``
- `` `source-library-mutation-authorized=false` ``
- `` `downstream-mutation-authorized=false` ``
- `` `next-material-entry=015-bazi-general-next-source-batch-preparation` ``

- [ ] **Step 4: Run RED test**

Run:

```powershell
$env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q
```

Expected: FAIL because the new dataclasses/functions/data/docs do not exist yet.

### Task 2: Add Metadata Model And Loader

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/bazi_general_variant_deferred_review_items.json`

- [ ] **Step 1: Add dataclasses**

Add frozen dataclasses with fields for review id, upstream identity id, upstream source-selection id, review kind, review status, variant/deferred decision, file references, candidate rule families, mutation flags, guardrails, and timestamps.

- [ ] **Step 2: Add constants and enum sets**

Add constants for the review id, next material entry, allowed review kinds, statuses, and decisions.

- [ ] **Step 3: Add JSON records**

Create exactly three records:
- Ditiansui variant set: keep blocked for variant selection; no canonical source chosen.
- Qiongtong variant set: keep blocked for variant selection; no canonical source chosen.
- Huntian Baolan Ziping: keep deferred as large source; no registration or reading.

- [ ] **Step 4: Add loader validation**

Validate:
- record ids are unique
- upstream identity-review ids exist
- upstream source-selection ids exist
- Ditiansui/Qiongtong records point to `variant_choice_required`
- Huntian record points to `deferred_large_source`
- all local references are relative
- all mutation flags are false
- no selected source-library entry ids are present

### Task 3: Summary, Markdown, And Quality Gate

**Files:**
- Modify: `src/mingli_engine/materials_audit.py`
- Modify: `tests/unit/test_materials_audit.py`

- [ ] **Step 1: Build summary**

Compute counts, ids, mutation flags, and boundary checks from the three review records.

- [ ] **Step 2: Render markdown**

Render a concise section with counts, ids, boundary checks, and guardrails.

- [ ] **Step 3: Include quality validation**

Wire the loader into `validate_materials_audit_quality` so invalid metadata fails the normal audit quality gate.

- [ ] **Step 4: Run GREEN focused tests**

Run:

```powershell
$env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q
```

Expected: PASS.

### Task 4: Documentation And Handoff

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`

- [ ] **Step 1: Append materials-audit section**

Add the rendered 015 variant/deferred review section after the preparation-reading section.

- [ ] **Step 2: Update handoff**

Record that the stage is complete, that no source-library/013/012 mutation was authorized for the three unresolved records, and that the next goal is `015-bazi-general-next-source-batch-preparation`.

- [ ] **Step 3: Re-run docs sync test**

Run the focused materials-audit test file again and confirm the docs markers pass.

### Task 5: Verification And Commit

**Files:**
- Verify all modified files

- [ ] **Step 1: Run audit and count validators**

Run a Python validation snippet covering:
- `materials_audit.validate_materials_audit_quality() == []`
- `build_bazi_general_variant_deferred_review_summary().review_status`
- source-library/013/012 counts remain unchanged except for no intended changes in this stage

- [ ] **Step 2: Run full tests**

Run:

```powershell
$env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 3: Inspect diff and commit**

Run:

```powershell
git diff --check
git status --short
git add docs/superpowers/plans/2026-06-28-bazi-general-variant-choice-deferred-review.md src/mingli_engine/models.py src/mingli_engine/materials_audit.py src/mingli_engine/data/materials_audit/bazi_general_variant_deferred_review_items.json tests/unit/test_materials_audit.py docs/classical_sources/materials_audit.md docs/classical_sources/new_material_learning_handoff.md
git commit -m "feat: review bazi general variant sources"
```

Expected: commit succeeds locally; no remote action.
