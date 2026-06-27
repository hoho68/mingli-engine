# 015 Queue Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh the 015 materials-audit next-action queue after 016/017 coverage, so the next local learning path does not point back to already-covered queue items.

**Architecture:** Keep the original `build_materials_audit_progress_summary()` stable for raw 015 inventory reporting. Add a coverage-aware refresh packet that reads 015 queue items and sibling 016 work-package snapshots, excludes covered queue ids, and renders a maintainer-facing Markdown packet. The packet is read-only and does not mutate raw materials, 013 candidates, or 012 formal evidence.

**Tech Stack:** Python 3.12, project-local JSON loaders, pytest, Markdown documentation.

---

### Task 1: Lock Coverage-Aware Queue Refresh

**Files:**
- Modify: `tests/unit/test_materials_audit.py`

- [x] **Step 1: Write the failing refresh summary test**

Add:

```python
def test_materials_audit_queue_refresh_excludes_covered_016_queue_items():
    summary = materials_audit.build_materials_audit_progress_summary()
    refresh = materials_audit.build_materials_audit_queue_refresh_summary()

    assert refresh.refresh_id == "015-materials-audit-next-action-queue-refresh"
    assert refresh.refresh_status == "covered_queue_exhausted"
    assert refresh.queue_item_count == 16
    assert refresh.covered_queue_item_count == 16
    assert refresh.uncovered_queue_item_ids == []
    assert refresh.legacy_next_action_ids == summary.next_action_ids
    assert refresh.refreshed_next_action_ids == []
    assert refresh.downstream_mutation_authorized is False
    assert refresh.next_material_entry == "015-external-material-inventory-refresh"
    assert refresh.boundary_checks == {
        "015_queue_loaded": "passed",
        "016_coverage_loaded": "passed",
        "covered_items_excluded": "passed",
        "013_012_not_mutated": "passed",
    }
```

- [x] **Step 2: Write the failing renderer/docs sync test**

Add:

```python
def test_materials_audit_queue_refresh_markdown_and_docs_are_in_sync():
    refresh = materials_audit.build_materials_audit_queue_refresh_summary()
    markdown = materials_audit.render_materials_audit_queue_refresh_markdown(refresh)
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(encoding="utf-8")
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(encoding="utf-8")

    for marker in (
        "015 Queue Refresh",
        "`queue-refresh-status=covered_queue_exhausted`",
        "`015-queue-items=16`",
        "`016-covered-queue-items=16`",
        "`uncovered-queue-items=0`",
        "`refreshed-next-action-ids=0`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-external-material-inventory-refresh`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff
```

- [x] **Step 3: Run both tests and confirm RED**

```powershell
$env:PYTHONPATH='src'; uv run --with pytest python -m pytest tests/unit/test_materials_audit.py::test_materials_audit_queue_refresh_excludes_covered_016_queue_items tests/unit/test_materials_audit.py::test_materials_audit_queue_refresh_markdown_and_docs_are_in_sync -q
```

Expected: FAIL because the refresh builder and renderer do not exist yet.

### Task 2: Implement the Read-Only Queue Refresh Packet

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`

- [x] **Step 1: Add `MaterialQueueRefreshSummary`**

Add a frozen dataclass near `AuditProgressSummary` with fields:

```python
@dataclass(frozen=True)
class MaterialQueueRefreshSummary:
    refresh_id: str
    refresh_status: str
    queue_item_count: int
    covered_queue_item_count: int
    uncovered_queue_item_ids: list[str]
    legacy_next_action_ids: list[str]
    refreshed_next_action_ids: list[str]
    downstream_mutation_authorized: bool
    next_material_entry: str
    boundary_checks: dict[str, str]
    covered_queue_item_ids: list[str] = field(default_factory=list)
    guardrails: list[str] = field(default_factory=list)
```

- [x] **Step 2: Build coverage from sibling 016 package snapshots**

Implement `build_materials_audit_queue_refresh_summary()` in `materials_audit.py`. Read `extraction_queue_intake/extraction_work_packages.json` directly as JSON when present; collect `source_queue_snapshot_ids`; filter the current 015 queue to uncovered items; select refreshed next ids with the existing `_select_next_queue_item_ids()`.

- [x] **Step 3: Render stable Markdown**

Implement `render_materials_audit_queue_refresh_markdown()` with the markers required by the tests and guardrails that no downstream mutation is authorized.

### Task 3: Sync Maintainer Docs

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`

- [x] **Step 1: Add 015 Queue Refresh markers**

Both docs must include:

```text
015 Queue Refresh
queue-refresh-status=covered_queue_exhausted
015-queue-items=16
016-covered-queue-items=16
uncovered-queue-items=0
refreshed-next-action-ids=0
downstream-mutation-authorized=false
next-material-entry=015-external-material-inventory-refresh
```

- [x] **Step 2: Update next long goal**

After this queue refresh, the next long goal is `next-material-entry=015-external-material-inventory-refresh`: perform an external-preparation inventory refresh and create/adjust 015 metadata only if new user-provided materials are actually present and explicitly in scope.

### Task 4: Verify and Commit

**Files:**
- Verify all modified files.

- [x] **Step 1: Run focused tests**

```powershell
$env:PYTHONPATH='src'; uv run --with pytest python -m pytest tests/unit/test_materials_audit.py tests/unit/test_extraction_queue_intake.py tests/unit/test_learning_reference_curation.py -q
```

- [x] **Step 2: Run queue refresh smoke command**

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.materials_audit import build_materials_audit_queue_refresh_summary, render_materials_audit_queue_refresh_markdown; refresh=build_materials_audit_queue_refresh_summary(); print(refresh); print(render_materials_audit_queue_refresh_markdown(refresh))"
```

- [x] **Step 3: Run full verification**

```powershell
git diff --check
$env:PYTHONPATH='src'; uv run --with pytest python -m pytest -q
```

- [x] **Step 4: Commit locally**

```powershell
git add docs/superpowers/plans/2026-06-27-015-queue-refresh.md src/mingli_engine/models.py src/mingli_engine/materials_audit.py tests/unit/test_materials_audit.py docs/classical_sources/materials_audit.md docs/classical_sources/new_material_learning_handoff.md
git commit -m "feat: add materials audit queue refresh"
```
