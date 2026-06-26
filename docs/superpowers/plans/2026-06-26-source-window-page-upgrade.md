# Source Window Page Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade source-window locators from broad chapter references to exact `page:` or `Markdown/...#L...` references where the source material is locally verifiable, and document why remaining chapter references cannot yet be upgraded.

**Architecture:** Keep formal evidence ids stable and work only in project-tracked review notes, audit docs, and tests. Source-window sections remain the contract surface: each section keeps `Source ref`, `Source locator`, and, when still chapter-level, a `Locator note` explaining the blocking reason.

**Tech Stack:** Python 3.12, pytest, pathlib/json/re, existing `tests/unit/test_classical_sources.py`, project Markdown review notes, local PDF/Markdown inspection tools.

---

### Task 1: Add A Chapter-Locator Reason Gate

**Files:**
- Modify: `tests/unit/test_classical_sources.py`

- [x] **Step 1: Write the failing test**

Add this assertion path to the existing source-window helper so every `chapter:` locator must have a same-section `Locator note`:

```python
def _assert_chapter_locator_has_note(section, source_locator):
    if not source_locator.startswith("chapter:"):
        return

    locator_note = _extract_bulleted_field(section, "Locator note")
    assert locator_note.startswith("blocked:"), locator_note
```

Call it from `_review_note_source_window_source_locator()` after `source_locator` is extracted.

- [x] **Step 2: Run test to verify it fails**

Run:

```bash
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_review_note_evidence_uses_precise_source_window_locators -q
```

Expected: FAIL because existing `chapter:` source-window sections do not yet have `Locator note`.

- [x] **Step 3: Implement minimal documentation changes**

For every remaining `chapter:` source-window section in `docs/classical_sources/extracts/*.md`, add:

```markdown
- Locator note: `blocked:<short-reason>`
```

Use reason values such as `blocked:pdf-text-cid-or-empty`, `blocked:pdf-directory-text-only`, or `blocked:no-tracked-markdown-source`.

- [x] **Step 4: Run test to verify it passes**

Run:

```bash
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_review_note_evidence_uses_precise_source_window_locators -q
```

Expected: PASS.

### Task 2: Upgrade Verifiable Chapter Locators

**Files:**
- Modify: `docs/classical_sources/extracts/*.md`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`

- [x] **Step 1: Inventory current chapter locators**

Run:

```bash
@'
from pathlib import Path
for path in Path("docs/classical_sources/extracts").glob("*.md"):
    for line in path.read_text(encoding="utf-8").splitlines():
        if "- Source locator: `chapter:" in line:
            print(path, line)
'@ | python -
```

Expected: list every remaining chapter-level locator.

- [x] **Step 2: Find verifiable local source paths**

Run:

```bash
rg -n "duan_plain_mingxue_outline|mingxue_golden_voice|northeast_blind_peak|fortune_reading_hongfu_qitian|blind_school_secret" src docs Markdown
```

Expected: identify whether a matching tracked Markdown source exists. If none exists for a source, keep the chapter locator and note the reason.

- [x] **Step 3: Upgrade only verified locators**

Replace a `chapter:` locator with one of these forms only when local evidence supports it:

```markdown
- Source locator: `page:<number>; source=<source_id>; heading:<heading-slug>`
- Source locator: `Markdown/<path>.md#L<number>`
```

Do not invent page numbers. If a PDF has CID/empty text or only directory text, keep `chapter:`.

- [x] **Step 4: Refresh audit report**

Regenerate `docs/classical_sources/source_ref_quality_audit.md` so the precision summary and `Source-Window Locator Detail` counts match the edited review notes.

### Task 3: Verify And Commit

**Files:**
- Modify: `tests/unit/test_classical_sources.py`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`
- Modify: `docs/classical_sources/extracts/*.md`

- [x] **Step 1: Run focused tests**

Run:

```bash
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py tests/unit/test_source_intake.py -q
```

Expected: PASS.

- [x] **Step 2: Run full test suite**

Run:

```bash
uv run --with pytest python -m pytest -q
```

Expected: PASS.

- [x] **Step 3: Run static file checks**

Run:

```bash
python -m json.tool src/mingli_engine/data/classical_sources/evidence_units.json > $null
git diff --check
git status --short
```

Expected: JSON parses, diff check has no errors, and changed files are limited to this goal.

- [x] **Step 4: Commit locally**

Run:

```bash
git add docs/classical_sources/extracts docs/classical_sources/source_ref_quality_audit.md tests/unit/test_classical_sources.py docs/superpowers/plans/2026-06-26-source-window-page-upgrade.md
git commit -m "docs: record source-window locator upgrade blockers"
```

Expected: local commit on `codex/complete-new-material-learning`. Do not push.
