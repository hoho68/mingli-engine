# Manual Review Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the next local-only manual review pass for remaining chapter locators by upgrading the one newly confirmed Northeast page locator and logging manual-review notes for retained blockers.

**Architecture:** The pass keeps external PDFs untouched, renders pages only to the OS temp directory, and updates tracked review notes, audit documentation, and unit-test expectations. It does not create candidates, promote evidence, or alter formal evidence.

**Tech Stack:** Markdown review notes, Python 3.12, pytest, Poppler `pdftoppm`, `uv`.

---

### Task 1: Extend Visual Review

**Files:**
- Read: `docs/classical_sources/extracts/duan_plain_mingxue_outline.md`
- Read: `docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md`
- Read: `docs/classical_sources/extracts/northeast_blind_peak.md`

- [x] **Step 1: Render follow-up candidate pages**

Rendered to `%TEMP%\mingli_manual_closure_review\rendered`:
- Duan: pages 104-115
- Hongfu: pages 15-24 and 69-90
- Northeast: pages 1-159 as contact sheets

- [x] **Step 2: Record conservative review decisions**

Decision results:
- `northeast_branch_interaction_001`: upgrade to `page:123; source=northeast_blind_peak_pdf; heading:three-harmony-branch-interaction`
- Duan remaining 4 windows: retain chapter locator with `manual-review:no-single-topic-page`
- Hongfu remaining 5 remedy-boundary windows: retain chapter locator with `manual-review:no-remedy-boundary-page`
- Northeast remaining 2 risk-boundary windows: retain chapter locator with `manual-review:no-risk-boundary-page`

### Task 2: Protect Closure With A Failing Test

**Files:**
- Modify: `tests/unit/test_classical_sources.py`

- [x] **Step 1: Update expected locator counts**

Expected after implementation:

```python
assert "| PAGE_LOCATOR | 44 |" in report
assert "| CHAPTER_LOCATOR | 11 |" in report
assert "| northeast_blind_peak_pdf | page-reviewed | 7 |" in report
assert "| northeast_blind_peak_pdf | rendered-review-blocked | 2 |" in report
```

- [x] **Step 2: Require manual-review notes for retained chapter locators**

The chapter-locator helper now extracts `Manual review note` and requires it to start with `manual-review:`.

- [x] **Step 3: Add manual review closure report expectations**

Expected rows:

```python
assert "## Manual Review Closure Pass" in report
assert "| duan_plain_mingxue_outline_pdf | no-single-topic-page | 4 |" in report
assert "| fortune_reading_hongfu_qitian_pdf | no-remedy-boundary-page | 5 |" in report
assert "| northeast_blind_peak_pdf | page-reviewed | 1 |" in report
assert "| northeast_blind_peak_pdf | no-risk-boundary-page | 2 |" in report
```

- [x] **Step 4: Run the focused test and confirm it fails**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_source_ref_quality_audit_tracks_source_window_references -q
```

Expected: FAIL on the pre-implementation audit counts.

### Task 3: Update Review Notes And Audit

**Files:**
- Modify: `docs/classical_sources/extracts/duan_plain_mingxue_outline.md`
- Modify: `docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md`
- Modify: `docs/classical_sources/extracts/northeast_blind_peak.md`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`

- [x] **Step 1: Upgrade the Northeast branch interaction source window**

Set:

```text
page:123; source=northeast_blind_peak_pdf; heading:three-harmony-branch-interaction
```

- [x] **Step 2: Add manual-review notes to the retained chapter locators**

Use these buckets:

```text
manual-review:no-single-topic-page
manual-review:no-remedy-boundary-page
manual-review:no-risk-boundary-page
```

- [x] **Step 3: Update audit counts, closure table, recommendations, and detailed inventory**

Expected totals:
- `PAGE_LOCATOR`: 44
- `CHAPTER_LOCATOR`: 11
- Remaining CID-backed chapter windows: 9
- Remaining Northeast risk-boundary chapter windows: 2

### Task 4: Verify And Commit Locally

**Files:**
- Verify: all modified Markdown and tests

- [x] **Step 1: Run focused source-ref audit test**

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_source_ref_quality_audit_tracks_source_window_references -q
```

- [x] **Step 2: Run JSON validation**

```powershell
python -m json.tool src\mingli_engine\data\classical_sources\evidence_units.json > $null
```

- [x] **Step 3: Run full test suite**

```powershell
uv run --with pytest python -m pytest -q
```

- [x] **Step 4: Check whitespace and commit**

```powershell
git diff --check
git add docs/classical_sources/extracts/duan_plain_mingxue_outline.md docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md docs/classical_sources/extracts/northeast_blind_peak.md docs/classical_sources/source_ref_quality_audit.md docs/superpowers/plans/2026-06-27-manual-review-closure.md tests/unit/test_classical_sources.py
git commit -m "docs: close manual locator review pass"
```
