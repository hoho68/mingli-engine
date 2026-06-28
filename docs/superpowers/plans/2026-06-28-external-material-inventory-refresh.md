# External Material Inventory Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh the post-selected-variant external material entrypoint and close stale 016 manual-action residue that is already represented downstream.

**Architecture:** Reuse the existing external inventory scanner and 016 package summary. The scanner stays read-only and continues to report no untracked immediate external entries; after the post-selected-variant queue surface is confirmed, it routes to a new next-cycle raw-text source-selection entry rather than the already completed raw-text triage. The 016 task records that already have authorized 017/013/012 downstream representation are marked completed so `next_manual_action_ids` no longer points to stale work.

**Tech Stack:** Python 3.12 dataclass loaders, project JSON metadata, Markdown documentation snapshots, pytest via `uv run --with pytest python -m pytest`.

---

### Task 1: RED Tests For External Inventory Next Cycle

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_extraction_queue_intake.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Update external inventory expectations**

In `test_external_material_inventory_refresh_summarizes_scoped_metadata`, expect:

```python
assert refresh.next_material_entry == "015-raw-text-next-cycle-source-selection"
assert refresh.boundary_checks == {
    "external_roots_scanned_read_only": "passed",
    "015_metadata_registered": "passed",
    "workflow_artifacts_excluded": "passed",
    "post_queue_refresh_surface_confirmed": "passed",
    "raw_materials_not_mutated": "passed",
    "013_012_not_mutated": "passed",
}
```

In docs sync, expect:

```text
`next-material-entry=015-raw-text-next-cycle-source-selection`
`post_queue_refresh_surface_confirmed`: `passed`
```

- [x] **Step 2: Add 016 closure expectation**

Add a focused test:

```python
def test_post_external_inventory_refresh_closes_applied_manual_actions():
    summary = extraction_queue_intake.build_package_progress_summary()

    assert summary.task_counts == {"completed": 19}
    assert summary.extraction_task_count == 19
    assert summary.next_manual_action_ids == []
```

- [x] **Step 3: Update handoff next marker expectation**

In `test_new_material_learning_handoff_tracks_final_state`, expect:

```text
`next-new-material-start=015-raw-text-next-cycle-source-selection`
```

- [x] **Step 4: Run RED**

```powershell
$env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest tests/unit/test_materials_audit.py::test_external_material_inventory_refresh_summarizes_scoped_metadata tests/unit/test_materials_audit.py::test_external_material_inventory_refresh_markdown_and_docs_are_in_sync tests/unit/test_extraction_queue_intake.py::test_post_external_inventory_refresh_closes_applied_manual_actions tests/unit/test_learning_reference_curation.py::test_new_material_learning_handoff_tracks_final_state -q
```

Expected: FAIL because implementation and JSON still point to the old raw-text triage/manual-action state.

### Task 2: GREEN External Inventory And 016 Closure

**Files:**
- Modify: `src/mingli_engine/materials_audit.py`
- Modify: `src/mingli_engine/data/extraction_queue_intake/extraction_tasks.json`

- [x] **Step 1: Add next-cycle constant**

Add:

```python
EXTERNAL_INVENTORY_POST_QUEUE_NEXT_MATERIAL_ENTRY = (
    "015-raw-text-next-cycle-source-selection"
)
```

- [x] **Step 2: Route external inventory after queue closure**

In `build_external_material_inventory_refresh_summary`, call:

```python
queue_refresh = build_materials_audit_queue_refresh_summary(source_dir)
post_queue_refresh_surface_confirmed = (
    queue_refresh.next_material_entry == "015-external-material-inventory-refresh"
    and queue_refresh.refresh_status == "covered_or_completed_queue_exhausted"
)
```

Set `next_material_entry` to `EXTERNAL_INVENTORY_POST_QUEUE_NEXT_MATERIAL_ENTRY` when the post-queue surface is confirmed and there are no untracked immediate external entries. Add the boundary check:

```python
"post_queue_refresh_surface_confirmed": (
    "passed" if post_queue_refresh_surface_confirmed else "failed"
),
```

- [x] **Step 3: Mark already-applied 016 tasks completed**

In `extraction_tasks.json`, change the first eight extraction tasks from:

```json
"status": "planned"
```

to:

```json
"status": "completed"
```

Do not change draft slots, candidates, review decisions, promotion batches, evidence units, raw PDFs, Markdown roots, or preparation folders.

### Task 3: Docs, Verification, And Commit

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/extraction_queue_intake.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `docs/superpowers/plans/2026-06-28-external-material-inventory-refresh.md`

- [x] **Step 1: Refresh docs**

Update materials audit external inventory section:

```text
`next-material-entry=015-raw-text-next-cycle-source-selection`
`post_queue_refresh_surface_confirmed`: `passed`
```

Update extraction queue intake to state:

```text
All 19 extraction tasks are completed; `next_manual_action_ids=0`.
```

Update handoff:

```text
`next-new-material-start=015-raw-text-next-cycle-source-selection`
```

- [x] **Step 2: Run gates**

```powershell
$env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8'; uv run python -c "from mingli_engine import source_library, materials_audit, source_intake, learning_reference_curation, extraction_queue_intake; from mingli_engine.classical_sources import load_classical_sources, load_evidence_units; from mingli_engine.evidence_curation import validate_curation_quality; checks=[source_library.validate_source_library_quality(), materials_audit.validate_materials_audit_quality(), extraction_queue_intake.validate_extraction_package_quality(), source_intake.validate_intake_quality(), learning_reference_curation.validate_learning_reference_quality(), validate_curation_quality(load_classical_sources(), load_evidence_units())]; print(checks); raise SystemExit(1 if any(checks) else 0)"
$env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest tests/unit/test_materials_audit.py::test_external_material_inventory_refresh_summarizes_scoped_metadata tests/unit/test_materials_audit.py::test_external_material_inventory_refresh_markdown_and_docs_are_in_sync tests/unit/test_extraction_queue_intake.py::test_post_external_inventory_refresh_closes_applied_manual_actions tests/unit/test_learning_reference_curation.py::test_new_material_learning_handoff_tracks_final_state -q
$env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest -q
git diff --check
```

- [x] **Step 3: Commit**

```powershell
git add docs src tests
git commit -m "chore: refresh external inventory entrypoint"
```
