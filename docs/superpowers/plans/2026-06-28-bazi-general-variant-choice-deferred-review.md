# Bazi General Variant Choice Deferred Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the residual Bazi general variant-choice/deferred-review surface by selecting canonical local references for Ditiansui and Qiongtong while keeping source-library and 013/012 mutation blocked.

**Architecture:** Extend the existing 015 materials-audit metadata model with a `selected_local_reference` field for variant-choice items. The summary remains a read-only 015 decision artifact: it records two canonical local-reference choices, keeps Huntian Baolan durably deferred, and points the next stage to selected-variant registration prep without registering sources or formal evidence.

**Tech Stack:** Python 3.12 dataclasses, project JSON metadata, pytest via `uv run --with pytest python -m pytest`.

---

### Task 1: RED Tests For Canonical Variant Choices

**Files:**
- Modify: `tests/unit/test_materials_audit.py`

- [x] **Step 1: Update item-level expectations**

Change `test_bazi_general_variant_deferred_review_items_load_residual_surface()` so it expects:

```python
diti = items_by_id["bazi_general_variant_review_ditiansui_variant_set"]
assert diti.review_status == "canonical_variant_selected"
assert diti.decision == "select_canonical_variant"
assert diti.canonical_choice_status == "selected_for_registration_prep"
assert diti.selected_local_reference == "滴天髓.pdf"

qiong = items_by_id["bazi_general_variant_review_qiongtong_variant_set"]
assert qiong.review_status == "canonical_variant_selected"
assert qiong.decision == "select_canonical_variant"
assert qiong.canonical_choice_status == "selected_for_registration_prep"
assert qiong.selected_local_reference == "穷通宝鉴/窮通寶鑒.pdf"
```

The large source remains:

```python
huntian = items_by_id["bazi_general_deferred_review_huntian_baolan_ziping"]
assert huntian.review_status == "deferred_large_source_reviewed"
assert huntian.decision == "keep_large_source_deferred"
assert huntian.canonical_choice_status == "not_applicable"
assert huntian.selected_local_reference == ""
```

- [x] **Step 2: Update summary expectations**

Change `test_bazi_general_variant_deferred_review_summary_closes_residual_surface()` so it expects:

```python
assert summary.selected_canonical_variant_count == 2
assert summary.selected_canonical_variant_ids == [
    "bazi_general_variant_review_ditiansui_variant_set",
    "bazi_general_variant_review_qiongtong_variant_set",
]
assert summary.next_material_entry == "015-bazi-general-selected-variant-registration-prep"
assert summary.boundary_checks["canonical_variant_choices_recorded"] == "passed"
assert summary.boundary_checks["source_library_not_mutated"] == "passed"
assert summary.boundary_checks["013_012_not_mutated"] == "passed"
```

- [x] **Step 3: Update docs-sync markers**

Change the docs-sync test so it expects:

```python
"`selected-canonical-variants=2`",
"`next-material-entry=015-bazi-general-selected-variant-registration-prep`",
```

- [x] **Step 4: Verify RED**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_materials_audit.py::test_bazi_general_variant_deferred_review_items_load_residual_surface tests/unit/test_materials_audit.py::test_bazi_general_variant_deferred_review_summary_closes_residual_surface tests/unit/test_materials_audit.py::test_bazi_general_variant_deferred_review_markdown_and_docs_are_in_sync -q
```

Expected: FAIL because the model/data still uses blocked variant choices and lacks `selected_local_reference`.

### Task 2: GREEN Model And Metadata

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Modify: `src/mingli_engine/data/materials_audit/bazi_general_variant_deferred_review_items.json`

- [x] **Step 1: Add `selected_local_reference` to the dataclass**

Add this optional field to `BaziGeneralVariantDeferredReviewItem`:

```python
selected_local_reference: str = ""
```

- [x] **Step 2: Extend allowed variant decisions**

Allow these additional values:

```python
BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_STATUSES = frozenset(
    {
        "blocked_pending_variant_choice",
        "canonical_variant_selected",
        "deferred_large_source_reviewed",
    }
)
BAZI_GENERAL_VARIANT_DEFERRED_REVIEW_DECISIONS = frozenset(
    {
        "keep_variant_choice_blocked",
        "select_canonical_variant",
        "keep_large_source_deferred",
    }
)
BAZI_GENERAL_VARIANT_DEFERRED_CANONICAL_CHOICE_STATUSES = frozenset(
    {"not_selected", "selected_for_registration_prep", "not_applicable"}
)
```

- [x] **Step 3: Validate selected local references**

For `review_kind == "variant_choice"`, accept either the old blocked shape or the new selected shape. The new selected shape must require:

```python
item.review_status == "canonical_variant_selected"
item.decision == "select_canonical_variant"
item.canonical_choice_status == "selected_for_registration_prep"
item.selected_local_reference in item.local_references
item.selected_source_library_entry_id == ""
item.source_library_mutation_authorized is False
item.downstream_mutation_authorized is False
```

For `review_kind == "deferred_large_source"`, require `selected_local_reference == ""`.

- [x] **Step 4: Update summary boundary logic**

Use selected-local-reference status to compute canonical selections:

```python
selected_canonical_variant_ids = [
    item.item_id
    for item in items
    if item.review_kind == "variant_choice"
    and item.canonical_choice_status == "selected_for_registration_prep"
    and item.selected_local_reference
]
```

Replace the old `no_canonical_variants_selected` check with `canonical_variant_choices_recorded`, which passes when every variant-choice item is selected.

- [x] **Step 5: Update JSON metadata**

Set Ditiansui to:

```json
"review_status": "canonical_variant_selected",
"decision": "select_canonical_variant",
"canonical_choice_status": "selected_for_registration_prep",
"selected_local_reference": "滴天髓.pdf"
```

Set Qiongtong to:

```json
"review_status": "canonical_variant_selected",
"decision": "select_canonical_variant",
"canonical_choice_status": "selected_for_registration_prep",
"selected_local_reference": "穷通宝鉴/窮通寶鑒.pdf"
```

Set Huntian Baolan to:

```json
"selected_local_reference": ""
```

### Task 3: Docs And Verification

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `docs/superpowers/plans/2026-06-28-bazi-general-variant-choice-deferred-review.md`

- [x] **Step 1: Refresh docs**

Update the Bazi General Variant Choice And Deferred Review section so it says two canonical variants were selected for the next registration-prep stage, no source-library or 013/012 mutation was authorized, and Huntian Baolan remains deferred.

- [x] **Step 2: Run quality gates**

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.materials_audit import validate_materials_audit_quality, build_bazi_general_variant_deferred_review_summary; print(validate_materials_audit_quality()); s=build_bazi_general_variant_deferred_review_summary(); print(s.review_status, s.selected_canonical_variant_count, s.next_material_entry, s.boundary_checks)"
```

Expected: empty quality-failure list; summary reports 2 selected canonical variants.

- [x] **Step 3: Run focused and full tests**

```powershell
uv run --with pytest python -m pytest tests/unit/test_materials_audit.py::test_bazi_general_variant_deferred_review_items_load_residual_surface tests/unit/test_materials_audit.py::test_bazi_general_variant_deferred_review_summary_closes_residual_surface tests/unit/test_materials_audit.py::test_bazi_general_variant_deferred_review_markdown_and_docs_are_in_sync -q
$env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest -q
git diff --check
```

Expected: all tests pass and diff check has no whitespace errors.

- [x] **Step 4: Commit**

```powershell
git add docs/classical_sources/materials_audit.md docs/classical_sources/new_material_learning_handoff.md docs/superpowers/plans/2026-06-28-bazi-general-variant-choice-deferred-review.md src/mingli_engine/models.py src/mingli_engine/materials_audit.py src/mingli_engine/data/materials_audit/bazi_general_variant_deferred_review_items.json tests/unit/test_materials_audit.py
git commit -m "feat: resolve bazi general variant choices"
```
