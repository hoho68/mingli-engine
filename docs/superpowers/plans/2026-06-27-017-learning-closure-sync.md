# 017 Learning Closure Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the 017 learning-reference overview and quickstart snapshots with the retained source-window learning-closure pass while preserving candidate, prerequisite, and formal-evidence boundaries.

**Architecture:** Keep 017 JSON schemas and candidate counts unchanged. Use tests to count the source-window learning-closure notes from tracked extract Markdown, then require the 017 maintainer docs to state how those closures affect selected ready notes, `next_action_ids`, and remaining prerequisite actions.

**Tech Stack:** Markdown documentation, Python 3.12, pytest, `uv`.

---

### Task 1: Protect The Cross-Document Sync With A Failing Test

**Files:**
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Count source-window learning-closure notes from extract Markdown**

Expected source-window closure counts:

```python
assert closure_counts == {
    "learning-paraphrase-ready": 4,
    "policy-boundary-retained": 5,
    "safety-boundary-retained": 2,
}
```

- [x] **Step 2: Require 017 docs to mirror the closure counts and boundary meaning**

Expected documentation markers:

```python
assert "Source-Window Learning Closure Sync" in docs
assert "`retained-chapter-learning-closed=11`" in docs
assert "`learning-paraphrase-ready=4`" in docs
assert "`policy-boundary-retained=5`" in docs
assert "`safety-boundary-retained=2`" in docs
assert "`formal_evidence_delta=0`" in docs
```

- [x] **Step 3: Run the focused test and confirm it fails before docs are updated**

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py::test_learning_reference_docs_track_source_window_learning_closure_sync -q
```

Expected: FAIL on missing source-window learning closure sync markers in the 017 docs.

### Task 2: Update 017 Maintainer Snapshots

**Files:**
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`

- [x] **Step 1: Add a source-window learning-closure sync section to the 017 overview**

The section must state:
- 14 selected ready 016 extraction tasks / 017 learning reference notes remain selected.
- 11 retained chapter source windows are learning-closed.
- No new candidate-intake decision, 013 candidate, review decision, promotion batch, or formal evidence is created by this sync.
- The seven draft note ids remain in `next_action_ids` as maintainer review handles.
- The three planned risk-review prerequisite actions remain the only active prerequisite actions in `next_action_ids`.

- [x] **Step 2: Add the same operational snapshot to quickstart**

The quickstart must explain that retained chapter closures do not remove draft-note handles from `next_action_ids`; future transcription is optional unless exact quotation, page-level proof, or promotion is needed.

### Task 3: Verify And Commit Locally

**Files:**
- Verify: modified docs, tests, and the existing 017 JSON data

- [x] **Step 1: Run focused learning-reference tests**

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q
```

- [x] **Step 2: Validate 017 JSON and summary command**

```powershell
python -m json.tool src\mingli_engine\data\learning_reference_curation\learning_reference_notes.json > $null
python -m json.tool src\mingli_engine\data\learning_reference_curation\learning_points.json > $null
python -m json.tool src\mingli_engine\data\learning_reference_curation\candidate_intake_decisions.json > $null
python -m json.tool src\mingli_engine\data\learning_reference_curation\prerequisite_action_notes.json > $null
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.learning_reference_curation import build_learning_reference_progress_summary, validate_learning_reference_quality; print(build_learning_reference_progress_summary()); print(validate_learning_reference_quality())"
```

- [x] **Step 3: Run whitespace check and full test suite**

```powershell
git diff --check
uv run --with pytest python -m pytest -q
```

- [x] **Step 4: Commit locally without remote work**

```powershell
git add docs/classical_sources/learning_reference_curation.md docs/superpowers/plans/2026-06-27-017-learning-closure-sync.md specs/017-learning-reference-curation/quickstart.md tests/unit/test_learning_reference_curation.py
git commit -m "docs: sync 017 learning closure snapshot"
```
