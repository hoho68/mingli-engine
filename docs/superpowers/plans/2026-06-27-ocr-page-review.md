# OCR Page Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Review the 36 remaining chapter-level source-window locators with local PDF text extraction, page rendering, and visual inspection, then upgrade any verifiable item to `page:` while keeping explicit blocker notes for unresolved items.

**Architecture:** Work only in project-tracked review notes, tests, audit docs, and this plan. Root PDFs are read-only preparation materials. Exact page upgrades require a visible page or reliable text-extraction signal; unresolved items keep `chapter:` plus `Locator note`.

**Tech Stack:** Python 3.12, pytest, pathlib/json/re, pdfplumber/pypdf, Poppler `pdftoppm`, existing `tests/unit/test_classical_sources.py`, Markdown review-note docs.

---

### Task 1: Add Audit Evidence For This Pass

**Files:**
- Modify: `tests/unit/test_classical_sources.py`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`

- [x] **Step 1: Write the failing test**

Require the audit report to contain an explicit section for this pass:

```python
assert "## OCR/Page Review Pass" in report
assert "| blind_school_secret_pdf | page-reviewed | 1 |" in report
assert "| blocked:pdf-text-cid-or-empty | 27 |" in report
assert "| blocked:pdf-directory-text-only | 9 |" in report
```

- [x] **Step 2: Run test to verify it fails**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_source_ref_quality_audit_tracks_source_window_references -q
```

Expected: FAIL because the audit report does not yet have this pass-specific section.

- [x] **Step 3: Add the audit section**

Add an `## OCR/Page Review Pass` section to `docs/classical_sources/source_ref_quality_audit.md` with one table row per reviewed source family.

- [x] **Step 4: Run test to verify it passes**

Run the same focused pytest command. Expected: PASS.

### Task 2: Review Remaining Chapter Locators

**Files:**
- Modify: `docs/classical_sources/extracts/*.md`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`

- [x] **Step 1: Inventory current chapter locators**

Run:

```powershell
@'
from pathlib import Path
for path in sorted(Path("docs/classical_sources/extracts").glob("*.md")):
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### source-window-"):
            current = line.removeprefix("### ")
        if "- Source locator: `chapter:" in line:
            print(path, current, line)
'@ | python -
```

- [x] **Step 2: Inspect local PDF capabilities**

Use `pdfplumber`/`pypdf` first. If text is CID/empty, render relevant pages with `pdftoppm` into `tmp/pdfs/` and visually inspect candidate pages. Do not write to or mutate root PDFs.

- [x] **Step 3: Upgrade only verified locators**

Change a locator to `page:<number>; source=<source_id>; heading:<slug>` only when the page has a visible heading or topic text that supports the source-window. Keep `chapter:` when the rendered pages or extracted text do not provide a reliable match.

- [x] **Step 4: Keep blockers for unresolved items**

Retain `Locator note` on every `chapter:` item. Use existing blocker codes unless the review discovers a clearer reason.

### Task 3: Verify And Commit

**Files:**
- Modify: `tests/unit/test_classical_sources.py`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`
- Modify: `docs/classical_sources/extracts/*.md`
- Modify: `docs/superpowers/plans/2026-06-27-ocr-page-review.md`

- [x] **Step 1: Run focused tests**

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py tests/unit/test_source_intake.py -q
```

- [x] **Step 2: Run full tests**

```powershell
uv run --with pytest python -m pytest -q
```

- [x] **Step 3: Run static checks**

```powershell
python -m json.tool src\mingli_engine\data\classical_sources\evidence_units.json > $null
git diff --check
git status --short
```

- [x] **Step 4: Commit locally**

```powershell
git add docs/classical_sources/extracts docs/classical_sources/source_ref_quality_audit.md tests/unit/test_classical_sources.py docs/superpowers/plans/2026-06-27-ocr-page-review.md
git commit -m "docs: record OCR page review findings"
```

Do not push.

## Execution Notes

- Rendered source pages with Poppler `pdftoppm.exe` through ASCII temporary copies because the bundled `.cmd` wrapper and Chinese workspace paths were not reliable.
- Upgraded 20 source-window locators from `chapter:` to `page:`:
  - Duan Plain Mingxue Outline: 4
  - Mingxue Golden Voice: 7
  - Fortune Reading Hongfu Qitian: 3
  - Northeast Blind Peak: 6
- Remaining chapter locators: 16
  - `blocked:pdf-text-cid-or-empty`: 13
  - `blocked:pdf-directory-text-only`: 3
