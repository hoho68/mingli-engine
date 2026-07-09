# Final Learning Handoff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a maintained handoff overview for the completed new-material learning pass, linking the finished source-window closure, 017 sync, and candidate/formal evidence boundary audit into one continuation entrypoint.

**Architecture:** Keep runtime data unchanged. Add a single maintainer-facing handoff document under `docs/classical_sources/`, link it from the classical source README, and protect the handoff with a regression test that recomputes the live counts from loaders and extract documents.

**Tech Stack:** Markdown documentation, Python 3.12, pytest, `uv`.

---

### Task 1: Protect The Handoff With A Failing Test

**Files:**
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Add a handoff regression test**

The test should require:

```python
handoff_path = Path("docs/classical_sources/new_material_learning_handoff.md")
assert handoff_path.exists()
```

It should also require live-count markers:

```python
assert "`selected-ready-learning-notes=14`" in handoff
assert "`retained-chapter-learning-closed=11`" in handoff
assert "`017-applied-decisions=28`" in handoff
assert "`013-candidate-extracts=36`" in handoff
assert "`013-review-decisions=36`" in handoff
assert "`013-promotion-batches=25`" in handoff
assert "`012-formal-evidence-units=92`" in handoff
assert "`formal_evidence_delta=0`" in handoff
```

- [x] **Step 2: Run the focused test and confirm it fails before the handoff exists**

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py::test_new_material_learning_handoff_tracks_final_state -q
```

Expected: FAIL because `docs/classical_sources/new_material_learning_handoff.md` does not exist yet.

### Task 2: Create And Link The Handoff

**Files:**
- Create: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `docs/classical_sources/README.md`

- [x] **Step 1: Create the handoff document**

The document must include:
- Completed checkpoints.
- Current frozen counts.
- Where to continue next.
- Remaining optional precision work.
- Guardrails: no remote work, no raw material mutation, no candidate or formal-evidence promotion unless explicitly requested.

- [x] **Step 2: Link the handoff from the README**

Add a short `Current Handoff` section pointing maintainers to `new_material_learning_handoff.md`.

### Task 3: Verify And Commit Locally

**Files:**
- Verify: modified docs, tests, and JSON data

- [x] **Step 1: Run focused tests**

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py::test_new_material_learning_handoff_tracks_final_state -q
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q
```

- [x] **Step 2: Validate key computed counts**

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine import learning_reference_curation as l, source_intake as s, classical_sources as c; summary=l.build_learning_reference_progress_summary(); print(summary.decision_counts); print(len(s.load_candidate_extracts())); print(len(s.load_review_decisions())); print(len(s.load_promotion_batches())); print(len(c.load_evidence_units())); print(summary.formal_evidence_delta)"
```

- [x] **Step 3: Run whitespace check and full test suite**

```powershell
git diff --check
uv run --with pytest python -m pytest -q
```

- [x] **Step 4: Commit locally without remote work**

```powershell
git add docs/classical_sources/README.md docs/classical_sources/new_material_learning_handoff.md docs/superpowers/plans/2026-06-27-final-learning-handoff.md tests/unit/test_learning_reference_curation.py
git commit -m "docs: add new material learning handoff"
```
