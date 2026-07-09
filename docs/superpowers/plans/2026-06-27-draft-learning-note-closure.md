# Draft Learning Note Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the seven remaining draft 017 learning reference notes after their learning points and candidate-intake decisions have already been applied, without creating new 013 candidates, reviews, promotion batches, or 012 formal evidence.

**Architecture:** Keep the existing 017 loader and summary builder unchanged. Treat this as a data/docs closure: move only the seven draft note statuses to `candidate_intake_started`, then update tests and maintainer-facing docs so `next_action_ids` is empty while the 36/36/25/92 downstream boundary remains frozen.

**Tech Stack:** Python 3.12, pytest, project-local JSON metadata, Markdown documentation.

---

### Task 1: Lock Draft-Note Closure Behavior

**Files:**
- Modify: `tests/unit/test_learning_reference_curation.py`
- Modify: `tests/integration/test_report_regression_cases.py`

- [ ] **Step 1: Write the failing unit test**

Add a unit test that expects the seven former draft note ids to have `candidate_intake_started`, expects `summary.note_counts == {"candidate_intake_started": 14}`, and expects `summary.next_action_ids == []`.

```python
def test_learning_reference_closes_remaining_draft_notes_without_evidence_changes():
    notes = learning_reference_curation.load_learning_reference_notes()
    summary = learning_reference_curation.build_learning_reference_progress_summary()
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    promotion_batches = source_intake.load_promotion_batches()
    evidence_units = classical_sources.load_evidence_units()

    closed_note_ids = {
        "note_northeast_blind_peak_001",
        "note_mingli_true_formula_teacher_001",
        "note_duan_plain_mingxue_outline_001",
        "note_mingxue_golden_voice_001",
        "note_fortune_reading_hongfu_qitian_001",
        "note_markdown_batch_002_useful_god_001",
        "note_markdown_batch_001_pattern_strength_001",
    }
    notes_by_id = {note.note_id: note for note in notes}

    assert {
        note_id
        for note_id in closed_note_ids
        if notes_by_id[note_id].status == "candidate_intake_started"
    } == closed_note_ids
    assert summary.note_counts == {"candidate_intake_started": 14}
    assert summary.next_action_ids == []
    assert summary.formal_evidence_delta == 0
    assert len(candidates) == 36
    assert len(reviews) == 36
    assert len(promotion_batches) == 25
    assert len(evidence_units) == 92
```

- [ ] **Step 2: Run the unit test and verify RED**

Run:

```powershell
$env:PYTHONPATH='src'; uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py::test_learning_reference_closes_remaining_draft_notes_without_evidence_changes -q
```

Expected: FAIL because the seven notes are still `draft` and still populate `next_action_ids`.

- [ ] **Step 3: Update existing summary and integration expectations**

After the data change, update existing assertions that currently expect `{"draft": 7, "candidate_intake_started": 7}` and seven note ids in `next_action_ids` to expect `{"candidate_intake_started": 14}` and `[]`.

### Task 2: Close the Seven Draft Notes

**Files:**
- Modify: `src/mingli_engine/data/learning_reference_curation/learning_reference_notes.json`

- [ ] **Step 1: Change only the seven draft note statuses**

For these note ids, set `status` to `candidate_intake_started` and `updated_at` to `2026-06-27`:

```text
note_northeast_blind_peak_001
note_mingli_true_formula_teacher_001
note_duan_plain_mingxue_outline_001
note_mingxue_golden_voice_001
note_fortune_reading_hongfu_qitian_001
note_markdown_batch_002_useful_god_001
note_markdown_batch_001_pattern_strength_001
```

- [ ] **Step 2: Run focused GREEN verification**

Run:

```powershell
$env:PYTHONPATH='src'; uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py::test_learning_reference_closes_remaining_draft_notes_without_evidence_changes -q
```

Expected: PASS.

### Task 3: Sync Maintainer Docs and Handoff

**Files:**
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`

- [ ] **Step 1: Update counts and markers**

Replace draft-count markers with:

```text
Learning reference notes: candidate_intake_started=14
selected-ready-learning-notes=14
closed-draft-learning-notes=7
next_action_ids=0
planned-risk-review-actions=0
completed-risk-review-actions=4
formal_evidence_delta=0
```

- [ ] **Step 2: Update continuation guidance**

State that 017 has no active `next_action_ids`; the next long goal is a local candidate/formal-evidence authorization audit before any optional 013 promotion work or a 015 queue refresh for brand-new materials.

### Task 4: Verify and Commit

**Files:**
- Verify all modified files.

- [ ] **Step 1: Run focused tests**

```powershell
$env:PYTHONPATH='src'; uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py tests/integration/test_report_regression_cases.py::test_learning_reference_prerequisite_actions_do_not_change_formal_evidence_counts -q
```

- [ ] **Step 2: Run metadata quality check**

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine import learning_reference_curation as l; s=l.build_learning_reference_progress_summary(); print(s.note_counts); print(s.next_action_ids); print(l.validate_learning_reference_quality())"
```

Expected:

```text
{'candidate_intake_started': 14}
[]
[]
```

- [ ] **Step 3: Run full test suite**

```powershell
$env:PYTHONPATH='src'; uv run --with pytest python -m pytest -q
```

- [ ] **Step 4: Commit locally**

```powershell
git add docs/superpowers/plans/2026-06-27-draft-learning-note-closure.md src/mingli_engine/data/learning_reference_curation/learning_reference_notes.json tests/unit/test_learning_reference_curation.py tests/integration/test_report_regression_cases.py docs/classical_sources/learning_reference_curation.md specs/017-learning-reference-curation/quickstart.md docs/classical_sources/new_material_learning_handoff.md
git commit -m "docs: close draft learning notes"
```
