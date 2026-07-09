# Candidate Formal Boundary Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify and document that the source-window learning-closure pass did not alter 017 decision counts, 013 candidate/review/promotion state, or 012 formal evidence coverage.

**Architecture:** Keep runtime data unchanged. Add one boundary-audit regression test that derives counts from the existing loaders, then update the 017 maintainer overview with the same immutable snapshot and boundary markers.

**Tech Stack:** Markdown documentation, Python 3.12, pytest, `uv`.

---

### Task 1: Protect The Boundary With A Failing Test

**Files:**
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Count 017 applied decisions and 013/012 downstream records**

Expected seeded counts:

```python
assert summary.decision_counts == {
    "reuse_existing": 1,
    "create_candidate": 27,
    "status:applied": 28,
}
assert len(candidates) == 36
assert len(reviews) == 36
assert len(promotion_batches) == 25
assert len(evidence_units) == 92
```

- [x] **Step 2: Assert learning-reference and learning-closure locators do not leak into 012 evidence**

Expected guard:

```python
assert not any(
    unit.source_ref.startswith("learning-reference:")
    or "candidate_" in unit.source_ref
    or "learning-closure:" in unit.source_ref
    for unit in evidence_units
)
```

- [x] **Step 3: Run the focused test and confirm it fails before docs are updated**

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py::test_learning_reference_candidate_formal_evidence_boundary_audit_snapshot -q
```

Observed: FAIL on missing `Candidate/Formal Evidence Boundary Audit` documentation markers.

### Task 2: Update The 017 Boundary Audit Snapshot

**Files:**
- Modify: `docs/classical_sources/learning_reference_curation.md`

- [x] **Step 1: Add the boundary audit section**

The section must include these markers:

```text
`017-applied-decisions=28`
`017-create-candidate-decisions=27`
`013-candidate-extracts=36`
`013-review-decisions=36`
`013-promotion-batches=25`
`012-formal-evidence-units=92`
`formal_evidence_delta=0`
`learning-reference-source-refs-in-012=0`
`candidate-id-source-refs-in-012=0`
`learning-closure-source-refs-in-012=0`
```

- [x] **Step 2: State the maintained boundary**

The section must state that 017 decisions are planning/provenance metadata, 013 candidates/reviews/promotions are the review pipeline, and 012 evidence units are the only formal report evidence surface.

### Task 3: Verify And Commit Locally

**Files:**
- Verify: modified docs, tests, and JSON data

- [x] **Step 1: Run focused tests**

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py::test_learning_reference_candidate_formal_evidence_boundary_audit_snapshot -q
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q
```

- [x] **Step 2: Validate JSON files and computed counts**

```powershell
python -m json.tool src\mingli_engine\data\learning_reference_curation\candidate_intake_decisions.json > $null
python -m json.tool src\mingli_engine\data\source_intake\candidate_extracts.json > $null
python -m json.tool src\mingli_engine\data\source_intake\review_decisions.json > $null
python -m json.tool src\mingli_engine\data\source_intake\promotion_batches.json > $null
python -m json.tool src\mingli_engine\data\classical_sources\evidence_units.json > $null
```

- [x] **Step 3: Run whitespace check and full test suite**

```powershell
git diff --check
uv run --with pytest python -m pytest -q
```

- [x] **Step 4: Commit locally without remote work**

```powershell
git add docs/classical_sources/learning_reference_curation.md docs/superpowers/plans/2026-06-27-candidate-formal-boundary-audit.md tests/unit/test_learning_reference_curation.py
git commit -m "docs: audit candidate formal evidence boundary"
```
