# Materials Audit Next Action Queue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the post-selected-variant 015 next-action queue refresh so local new-material planning no longer points back to completed stages.

**Architecture:** Reuse the existing `MaterialQueueRefreshSummary` contract and keep this as read-only 015 planning metadata. The refresh will continue to exclude 016-covered and locally completed queue items, add an explicit post-selected-variant boundary check, keep 013/012 mutation disabled, and route the next long goal to a fresh external inventory/material-selection cycle rather than an already completed Liang/Bazi stage.

**Tech Stack:** Python 3.12 dataclass loaders, project JSON metadata, Markdown documentation snapshots, pytest via `uv run --with pytest python -m pytest`.

---

### Task 1: RED Tests For Post-Selected-Variant Queue Closure

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Update queue refresh expectations**

Change `test_materials_audit_queue_refresh_excludes_covered_016_queue_items` so it expects:

```python
assert refresh.refresh_id == "015-materials-audit-next-action-queue-refresh"
assert refresh.refresh_status == "covered_or_completed_queue_exhausted"
assert refresh.queue_item_count == 22
assert refresh.covered_queue_item_count == 21
assert refresh.locally_completed_queue_item_ids == [
    "queue_raw_text_materials_folder_triage",
]
assert refresh.uncovered_queue_item_ids == []
assert refresh.refreshed_next_action_ids == []
assert refresh.downstream_mutation_authorized is False
assert refresh.next_material_entry == "015-external-material-inventory-refresh"
assert refresh.boundary_checks == {
    "015_queue_loaded": "passed",
    "016_coverage_loaded": "passed",
    "covered_items_excluded": "passed",
    "completed_items_excluded": "passed",
    "post_selected_variant_queue_surface_confirmed": "passed",
    "013_012_not_mutated": "passed",
}
```

- [x] **Step 2: Update docs-sync expectations**

Change queue refresh markdown sync to require:

```text
`next-material-entry=015-external-material-inventory-refresh`
`post_selected_variant_queue_surface_confirmed`: `passed`
```

Change the handoff final-state test to require:

```text
`next-new-material-start=015-external-material-inventory-refresh`
```

- [x] **Step 3: Run RED**

```powershell
$env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest tests/unit/test_materials_audit.py::test_materials_audit_queue_refresh_excludes_covered_016_queue_items tests/unit/test_materials_audit.py::test_materials_audit_queue_refresh_markdown_and_docs_are_in_sync tests/unit/test_learning_reference_curation.py::test_new_material_learning_handoff_tracks_final_state -q
```

Expected: FAIL because the code and docs still point to `015-liang-bazi-core-individual-review`.

### Task 2: GREEN Queue Refresh Logic

**Files:**
- Modify: `src/mingli_engine/materials_audit.py`

- [x] **Step 1: Add a post-selected-variant completion detector**

Add a helper near `_selected_variant_entries_registered`:

```python
def _selected_variant_queue_surface_completed(
    source_entries_by_id: dict[str, source_library.SourceLibraryEntry],
) -> bool:
    return _selected_variant_entries_registered(source_entries_by_id)
```

- [x] **Step 2: Use the detector in `build_materials_audit_queue_refresh_summary`**

Load source-library entries in the function and add:

```python
post_selected_variant_surface_confirmed = (
    all_queue_items_covered
    and bool(locally_completed_queue_item_ids)
    and _selected_variant_queue_surface_completed(source_entries_by_id)
)
```

Set:

```python
next_material_entry=(
    "015-external-material-inventory-refresh"
    if post_selected_variant_surface_confirmed
    else ...
)
```

Add boundary check:

```python
"post_selected_variant_queue_surface_confirmed": (
    "passed" if post_selected_variant_surface_confirmed else "failed"
),
```

Keep `downstream_mutation_authorized=False`.

### Task 3: Docs, Verification, And Commit

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `docs/superpowers/plans/2026-06-28-materials-audit-next-action-queue.md`

- [x] **Step 1: Refresh docs**

Update the 015 Queue Refresh section to say the post-selected-variant queue is exhausted:

```text
`next-material-entry=015-external-material-inventory-refresh`
`post_selected_variant_queue_surface_confirmed`: `passed`
```

Update handoff:

```text
`next-new-material-start=015-external-material-inventory-refresh`
```

The next long goal should be an external inventory refresh / new material selection cycle, with Huntian Baolan still separate.

- [x] **Step 2: Run quality gates and tests**

```powershell
$env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8'; uv run python -c "from mingli_engine import source_library, materials_audit, source_intake, learning_reference_curation, extraction_queue_intake; from mingli_engine.classical_sources import load_classical_sources, load_evidence_units; from mingli_engine.evidence_curation import validate_curation_quality; checks=[source_library.validate_source_library_quality(), materials_audit.validate_materials_audit_quality(), extraction_queue_intake.validate_extraction_package_quality(), source_intake.validate_intake_quality(), learning_reference_curation.validate_learning_reference_quality(), validate_curation_quality(load_classical_sources(), load_evidence_units())]; print(checks); raise SystemExit(1 if any(checks) else 0)"
$env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest tests/unit/test_materials_audit.py::test_materials_audit_queue_refresh_excludes_covered_016_queue_items tests/unit/test_materials_audit.py::test_materials_audit_queue_refresh_markdown_and_docs_are_in_sync tests/unit/test_learning_reference_curation.py::test_new_material_learning_handoff_tracks_final_state -q
$env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest -q
git diff --check
```

Expected: all gates/tests pass; `git diff --check` reports no whitespace errors.

- [x] **Step 3: Commit**

```powershell
git add docs src tests
git commit -m "chore: close materials audit next queue"
```
