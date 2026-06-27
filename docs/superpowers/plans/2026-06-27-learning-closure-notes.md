# Retained Chapter Learning Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the local-only learning loop for the remaining 11 chapter-level source-window locators by recording learning-closure notes, updating the source-reference audit, and verifying the result with tests before a local commit.

**Architecture:** This pass keeps source precision unchanged. It adds a curation-state layer on retained chapter locators so later work can distinguish learning-ready paraphrases, policy-boundary retained material, and safety-boundary retained material without promoting candidates or formal evidence.

**Tech Stack:** Markdown review notes, Python 3.12, pytest, `uv`.

---

### Task 1: Protect Learning Closure With A Failing Test

**Files:**
- Modify: `tests/unit/test_classical_sources.py`

- [x] **Step 1: Require learning-closure notes for retained chapter locators**

The chapter-locator helper now extracts `Learning closure note` and requires it to start with `learning-closure:`.

- [x] **Step 2: Add learning closure audit expectations**

Expected rows:

```python
assert "## Learning Closure Pass" in report
assert "| duan_plain_mingxue_outline_pdf | learning-paraphrase-ready | 4 |" in report
assert "| fortune_reading_hongfu_qitian_pdf | policy-boundary-retained | 5 |" in report
assert "| northeast_blind_peak_pdf | safety-boundary-retained | 2 |" in report
assert "| Total | retained-chapter-learning-closed | 11 |" in report
```

- [x] **Step 3: Run the focused test and confirm it fails before implementation**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_source_ref_quality_audit_tracks_source_window_references -q
```

Observed: FAIL on the missing `## Learning Closure Pass` report section.

### Task 2: Add Learning Closure Notes

**Files:**
- Modify: `docs/classical_sources/extracts/duan_plain_mingxue_outline.md`
- Modify: `docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md`
- Modify: `docs/classical_sources/extracts/northeast_blind_peak.md`

- [x] **Step 1: Mark Duan chapter windows as learning paraphrase ready**

Updated 4 retained chapter windows with:

```text
learning-closure:learning-paraphrase-ready
```

- [x] **Step 2: Mark Hongfu remedy windows as policy-boundary retained**

Updated 5 retained chapter windows with:

```text
learning-closure:policy-boundary-retained
```

- [x] **Step 3: Mark Northeast risk windows as safety-boundary retained**

Updated 2 retained chapter windows with:

```text
learning-closure:safety-boundary-retained
```

### Task 3: Update Audit Report

**Files:**
- Modify: `docs/classical_sources/source_ref_quality_audit.md`

- [x] **Step 1: Add the learning closure table**

Expected totals:
- Duan learning-paraphrase-ready: 4
- Hongfu policy-boundary-retained: 5
- Northeast safety-boundary-retained: 2
- Total retained-chapter-learning-closed: 11

- [x] **Step 2: Update improvement notes, priority groups, future precision notes, and recommendations**

The report should state that learning closure is complete for retained chapter locators and that future transcription is optional unless exact quotation, page-level proof, or promotion is needed.

### Task 4: Verify And Commit Locally

**Files:**
- Verify: all modified Markdown and tests

- [x] **Step 1: Count chapter locators and learning-closure notes**

```powershell
(rg 'Source locator: `chapter:' docs/classical_sources/extracts | Measure-Object).Count
(rg 'Learning closure note: `learning-closure:' docs/classical_sources/extracts | Measure-Object).Count
```

- [x] **Step 2: Run focused source-ref audit test**

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_source_ref_quality_audit_tracks_source_window_references -q
```

- [x] **Step 3: Run JSON validation, whitespace check, and full test suite**

```powershell
python -m json.tool src\mingli_engine\data\classical_sources\evidence_units.json > $null
git diff --check
uv run --with pytest python -m pytest -q
```

- [x] **Step 4: Commit locally without remote work**

```powershell
git add docs/classical_sources/extracts/duan_plain_mingxue_outline.md docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md docs/classical_sources/extracts/northeast_blind_peak.md docs/classical_sources/source_ref_quality_audit.md docs/superpowers/plans/2026-06-27-learning-closure-notes.md tests/unit/test_classical_sources.py
git commit -m "docs: close retained chapter learning notes"
```
