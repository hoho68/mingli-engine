# Remaining Chapter Locator Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the next long local-only pass over the remaining chapter-level source-window locators by upgrading visually confirmed pages and documenting precise blockers for the rest.

**Architecture:** The pass changes only tracked review notes, the source reference audit report, and the unit test expectations that protect those counts. External PDFs stay untouched; rendered PNGs live in the OS temp directory for visual review only.

**Tech Stack:** Markdown review notes, Python 3.12, pytest, Poppler `pdftoppm`, `uv`.

---

### Task 1: Confirm Target Inventory

**Files:**
- Read: `docs/classical_sources/extracts/duan_plain_mingxue_outline.md`
- Read: `docs/classical_sources/extracts/mingxue_golden_voice.md`
- Read: `docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md`
- Read: `docs/classical_sources/extracts/northeast_blind_peak.md`

- [x] **Step 1: List all remaining chapter locators**

Run:

```powershell
rg -n "Locator: chapter:|Locator note:" docs/classical_sources/extracts
```

Expected: 16 remaining chapter-level source-window locators before this pass.

- [x] **Step 2: Render candidate PDF pages into temp PNGs**

Use the bundled Poppler binary directly, copying PDFs to `%TEMP%\mingli_remaining_locator_review\src` first to avoid Unicode-path failures.

Expected visual review candidates:
- Duan: pages 66-85 and 92-103
- Mingxue: pages 72-79, 93-103, and 116-119
- Hongfu: pages 69-75
- Northeast: pages 2, 13, 16, 34, 130, and 147

- [x] **Step 3: Record conservative upgrade decisions**

Confirmed upgrades:
- `duan_ten_god_relation_002`: page 66, `ten-god-pillar-position-context`
- `mingxue_ten_god_relation_001`: page 72, `ten-god-terms`
- `mingxue_ten_god_relation_002`: page 116, `qa-structure-balance`
- `fortune_taboo_god_candidate_001`: page 72, `yongshen-illness-remedy`

Retained as chapter-level:
- Duan useful/taboo balance windows where pages show broad element balance but not a stable single topic page.
- Hongfu remedy-boundary windows where source pages discuss use-god/remedy concepts but not the product/safety boundary itself.
- Northeast branch/risk-boundary windows where rendered pages did not directly support the exact branch-interaction or high-risk boundary theme.

### Task 2: Protect The New Counts With A Failing Test

**Files:**
- Modify: `tests/unit/test_classical_sources.py`

- [x] **Step 1: Update audit count expectations**

Expected values after implementation:

```python
assert "| PAGE_LOCATOR | 43 |" in report
assert "| CHAPTER_LOCATOR | 12 |" in report
assert "| blocked:rendered-review-no-topic-page-match | 4 |" in report
assert "| blocked:rendered-review-no-remedy-boundary-page-match | 5 |" in report
assert "| blocked:rendered-review-no-branch-interaction-topic-match | 1 |" in report
assert "| blocked:rendered-review-no-risk-boundary-page-match | 2 |" in report
```

- [x] **Step 2: Update OCR/Page Review Pass expectations**

Expected rows:

```python
assert "| duan_plain_mingxue_outline_pdf | page-reviewed | 5 |" in report
assert "| duan_plain_mingxue_outline_pdf | rendered-review-blocked | 4 |" in report
assert "| mingxue_golden_voice_pdf | page-reviewed | 9 |" in report
assert "| fortune_reading_hongfu_qitian_pdf | page-reviewed | 4 |" in report
assert "| fortune_reading_hongfu_qitian_pdf | rendered-review-blocked | 5 |" in report
assert "| northeast_blind_peak_pdf | rendered-review-blocked | 3 |" in report
```

- [x] **Step 3: Run the focused test and confirm it fails**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_source_ref_quality_audit_tracks_source_window_references -q
```

Expected: FAIL because the audit report and review notes still contain the pre-pass counts.

### Task 3: Update Review Notes And Audit Report

**Files:**
- Modify: `docs/classical_sources/extracts/duan_plain_mingxue_outline.md`
- Modify: `docs/classical_sources/extracts/mingxue_golden_voice.md`
- Modify: `docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md`
- Modify: `docs/classical_sources/extracts/northeast_blind_peak.md`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`

- [x] **Step 1: Upgrade confirmed source-window locators**

Use these exact locator values:

```text
page:66; source=duan_plain_mingxue_outline_pdf; heading:ten-god-pillar-position-context
page:72; source=mingxue_golden_voice_pdf; heading:ten-god-terms
page:116; source=mingxue_golden_voice_pdf; heading:qa-structure-balance
page:72; source=fortune_reading_hongfu_qitian_pdf; heading:yongshen-illness-remedy
```

- [x] **Step 2: Refine retained blocker notes**

Use these blocker buckets:

```text
blocked:rendered-review-no-topic-page-match
blocked:rendered-review-no-remedy-boundary-page-match
blocked:rendered-review-no-branch-interaction-topic-match
blocked:rendered-review-no-risk-boundary-page-match
```

- [x] **Step 3: Update audit top-level counts and detailed inventory**

Expected totals:
- `PAGE_LOCATOR`: 43
- `CHAPTER_LOCATOR`: 12
- `MARKDOWN_LINE_LOCATOR`: 2

### Task 4: Verify And Commit Locally

**Files:**
- Verify: `src/mingli_engine/data/classical_sources/evidence_units.json`
- Verify: all modified Markdown and tests

- [x] **Step 1: Run focused test**

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_source_ref_quality_audit_tracks_source_window_references -q
```

- [x] **Step 2: Run source JSON validation**

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
git add docs/classical_sources/extracts/duan_plain_mingxue_outline.md docs/classical_sources/extracts/mingxue_golden_voice.md docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md docs/classical_sources/extracts/northeast_blind_peak.md docs/classical_sources/source_ref_quality_audit.md docs/superpowers/plans/2026-06-27-remaining-chapter-locator-review.md tests/unit/test_classical_sources.py
git commit -m "docs: refine remaining chapter locators"
```
