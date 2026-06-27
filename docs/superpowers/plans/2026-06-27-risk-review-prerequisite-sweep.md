# Risk Review Prerequisite Sweep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the current 017 planned risk-review prerequisite group without turning high-risk materials into candidates or formal evidence.

**Architecture:** Treat this as a bounded tracking update across 015, 016, and 017. The four risk-review queue items remain high-risk source material, but their prerequisite review actions are closed as completed so they leave the active 017 next-action list. Existing JSON loaders and summaries provide the enforcement surface.

**Tech Stack:** Python 3.12, project-local JSON seed data, pytest, existing `mingli_engine` loaders.

---

### Task 1: Red Tests For Closed Risk-Review Actions

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_extraction_queue_intake.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Add failing tests**

Add tests that require the four risk-review ids to be marked completed in
015 queue items, 016 backlog records, and 017 prerequisite action notes. The
tests also assert that no 016 extraction task, 017 learning point, 013
candidate, promotion batch, or 012 formal evidence is created.

- [x] **Step 2: Run the focused tests to verify RED**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_materials_audit.py::test_seeded_risk_review_sweep_marks_high_risk_queue_items_completed tests/unit/test_extraction_queue_intake.py::test_seeded_risk_review_sweep_closes_backlog_records_without_tasks tests/unit/test_learning_reference_curation.py::test_learning_reference_risk_review_sweep_closes_actions_without_evidence_changes -q
```

Expected: fail because the four risk-review items are still planned.

### Task 2: Seed Data Update

**Files:**
- Modify: `src/mingli_engine/data/materials_audit/extraction_queue_items.json`
- Modify: `src/mingli_engine/data/extraction_queue_intake/extraction_work_packages.json`
- Modify: `src/mingli_engine/data/extraction_queue_intake/prerequisite_backlog_records.json`
- Modify: `src/mingli_engine/data/learning_reference_curation/prerequisite_action_notes.json`

- [x] **Step 1: Mark the four 015 risk-review queue items completed**

Set `status` to `completed` for:

- `queue_blind_life_manual_risk_review`
- `queue_immortal_fortune_jianghu_secret_risk_review`
- `queue_life_death_book_100_pages_risk_review`
- `queue_markdown_source_batch_005_risk_review`

- [x] **Step 2: Mark the related 016 package/backlog records completed**

Set `package_next_candidates_004.status` to `completed`; set all four related
risk-review backlog records to `completed` and refresh their durable reasons
as boundary conclusions.

- [x] **Step 3: Mark the related 017 prerequisite action notes completed**

Mirror the 016 status and durable reasons exactly so the existing link
validator continues to pass.

### Task 3: Snapshot And Documentation Update

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_extraction_queue_intake.py`
- Modify: `tests/unit/test_learning_reference_curation.py`
- Modify: `tests/integration/test_report_regression_cases.py`
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/extraction_queue_intake.md`
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`

- [x] **Step 1: Update expected summary counts**

Expected after the sweep:

- `planned-risk-review-actions=0`
- `completed-risk-review-actions=4`
- 017 `next_action_ids=7`
- 017 prerequisite action counts include `status:completed=4`
- 016 backlog counts include `status:completed=4`
- 015 next-action queue excludes the four completed risk-review items

- [x] **Step 2: Update maintainer docs and handoff**

Record that the next long goal should start from the remaining seven draft
learning notes, not from planned risk-review prerequisite actions.

### Task 4: Verification And Commit

**Files:**
- All files above

- [x] **Step 1: Validate JSON and focused tests**

Run JSON validation and focused tests for 015, 016, 017, and integration
boundary snapshots.

- [x] **Step 2: Run full test suite**

Run:

```powershell
uv run --with pytest python -m pytest -q
```

Expected: all tests pass.

- [x] **Step 3: Commit locally**

Commit the verified local change. Do not push remote work.
