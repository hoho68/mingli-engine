# Report Evidence Notes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reader-facing `### 观察依据` section to safe Markdown reports and protect it with unit, renderer, safety, and regression tests.

**Architecture:** Extend the existing `Report` dataclass with an `evidence_notes` field. Build the content in `report_schema.py` from existing chart/report concepts, include it in safety review, then render it in `markdown.py` inside `第二层：结构观察` after `十神摘要` and before `结构分析`.

**Tech Stack:** Python 3.12+, existing `mingli_engine` package, pytest, PowerShell commands on Windows.

---

### Task 1: Add Failing Report Schema Tests

**Files:**
- Modify: `tests/unit/test_report_schema.py`

- [ ] **Step 1: Add `evidence_notes` to the complete report field check**

In `test_build_report_returns_complete_safe_report`, add `"evidence_notes"` to the tuple of required non-empty report fields.

- [ ] **Step 2: Add a focused evidence-note content test**

Add this test near the other report schema tests:

```python
def test_build_report_explains_observation_basis(sample_bazi_chart):
    report = build_report(_chart_with_contract_labels(sample_bazi_chart))

    assert "来源依据：" in report.evidence_notes
    assert "排盘来源" in report.evidence_notes
    assert "历法" in report.evidence_notes
    assert "四柱依据：" in report.evidence_notes
    for pillar_name in ("年柱", "月柱", "日柱", "时柱"):
        assert pillar_name in report.evidence_notes
    assert "五行依据：" in report.evidence_notes
    assert "明面信号" in report.evidence_notes
    assert "藏干信号" in report.evidence_notes
    assert "合计信号" in report.evidence_notes
    assert "十神依据：" in report.evidence_notes
    assert "关系线索" in report.evidence_notes
    assert "行动依据：" in report.evidence_notes
    assert "复盘问题" in report.evidence_notes
    assert "不预测具体结果" in report.evidence_notes
```

- [ ] **Step 3: Add evidence notes to the raw-label body check**

In `_report_body`, include `report.evidence_notes` so existing raw-label assertions cover the new field.

- [ ] **Step 4: Run the focused schema test and verify RED**

```powershell
uv run --with pytest python -m pytest tests/unit/test_report_schema.py -v
```

Expected: FAIL with an `AttributeError` for `evidence_notes`.

### Task 2: Implement Evidence Notes In The Report Model

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/report_schema.py`
- Test: `tests/unit/test_report_schema.py`

- [ ] **Step 1: Add the report field**

In `src/mingli_engine/models.py`, add the field after `ten_gods_summary`:

```python
    evidence_notes: str
```

- [ ] **Step 2: Add the evidence-note builder**

In `src/mingli_engine/report_schema.py`, add this helper near the other `_build_*` helpers:

```python
def _build_evidence_notes() -> str:
    return "\n".join(
        [
            "- 来源依据：先看排盘来源与历法、时区、节气等假设，避免把前提当成结论。",
            "- 四柱依据：年柱、月柱、日柱、时柱只提供结构位置和组合线索，不单独断事。",
            "- 五行依据：明面信号、藏干信号和合计信号用于观察分布，不用于给人生下定论。",
            "- 十神依据：十神关系按柱位理解为关系线索，需要结合解读边界一起阅读。",
            "- 行动依据：行动反思只把可观察线索转成复盘问题，不预测具体结果。",
        ]
    )
```

- [ ] **Step 3: Wire the field into `build_report`**

In `build_report`, after `ten_gods_summary = interpretation.ten_gods_summary`, add:

```python
    evidence_notes = _build_evidence_notes()
```

In the `Report(...)` construction, add:

```python
        evidence_notes=evidence_notes,
```

In the safety-review text list, add `evidence_notes` after `ten_gods_summary`.

- [ ] **Step 4: Include evidence notes in major body safety review**

In `_major_body_sections`, add:

```python
            report.evidence_notes,
```

after `report.ten_gods_summary`.

- [ ] **Step 5: Run the schema tests and verify GREEN**

```powershell
uv run --with pytest python -m pytest tests/unit/test_report_schema.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit model and schema work**

```powershell
git add src/mingli_engine/models.py src/mingli_engine/report_schema.py tests/unit/test_report_schema.py
git commit -m "feat: add report evidence notes"
```

### Task 3: Render Evidence Notes In Markdown

**Files:**
- Modify: `tests/unit/test_markdown_renderer.py`
- Modify: `src/mingli_engine/markdown.py`

- [ ] **Step 1: Extend renderer order test**

In `test_render_markdown_report_uses_layered_reading_order`, add `"### 观察依据"` after `"### 十神摘要"` and before `"### 结构分析"` in the expected heading tuple.

- [ ] **Step 2: Add renderer content assertions**

Add this test:

```python
def test_render_markdown_report_includes_observation_basis(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    assert "### 观察依据" in markdown.splitlines()
    assert report.evidence_notes in markdown
    assert markdown.count("### 观察依据") == 1
    assert markdown.count(report.evidence_notes) == 1
```

- [ ] **Step 3: Run the renderer tests and verify RED**

```powershell
uv run --with pytest python -m pytest tests/unit/test_markdown_renderer.py -v
```

Expected: FAIL because `### 观察依据` is not rendered yet.

- [ ] **Step 4: Render the section**

In `src/mingli_engine/markdown.py`, add these two entries after `report.ten_gods_summary`:

```python
        "### 观察依据",
        report.evidence_notes,
```

- [ ] **Step 5: Run renderer tests and verify GREEN**

```powershell
uv run --with pytest python -m pytest tests/unit/test_markdown_renderer.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit renderer work**

```powershell
git add src/mingli_engine/markdown.py tests/unit/test_markdown_renderer.py
git commit -m "feat: render report evidence notes"
```

### Task 4: Extend Regression And Safety Coverage

**Files:**
- Modify: `tests/integration/test_report_regression_cases.py`
- Modify: `tests/safety/test_red_lines_and_language.py`

- [ ] **Step 1: Add evidence-note phrases to regression tests**

In `tests/integration/test_report_regression_cases.py`, add:

```python
EVIDENCE_NOTE_PHRASES = (
    "### 观察依据",
    "来源依据：",
    "四柱依据：",
    "五行依据：",
    "十神依据：",
    "行动依据：",
    "不预测具体结果",
)
```

- [ ] **Step 2: Assert section placement in safe Markdown checks**

In `_assert_safe_markdown`, after `_assert_in_order(markdown, LAYER_HEADINGS)`, add:

```python
    _assert_in_order(
        markdown,
        (
            "### 四柱与五行摘要",
            "### 十神摘要",
            "### 观察依据",
            "### 结构分析",
            "### 性格倾向",
        ),
    )
    for phrase in EVIDENCE_NOTE_PHRASES:
        assert phrase in markdown
```

- [ ] **Step 3: Assert safety JSON cases do not emit evidence Markdown**

In `_assert_safety_json`, add:

```python
    assert "### 观察依据" not in result.stdout
```

- [ ] **Step 4: Extend generated report safety language test**

In `tests/safety/test_red_lines_and_language.py`, inside `test_generated_auto_report_avoids_absolute_or_fatalistic_phrases`, add:

```python
    assert "### 观察依据" in markdown
    assert "不预测具体结果" in markdown
```

- [ ] **Step 5: Run regression and safety tests**

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_red_lines_and_language.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit regression coverage**

```powershell
git add tests/integration/test_report_regression_cases.py tests/safety/test_red_lines_and_language.py
git commit -m "test: cover report evidence notes"
```

### Task 5: Full Verification

**Files:**
- Inspect: `src/mingli_engine/models.py`
- Inspect: `src/mingli_engine/report_schema.py`
- Inspect: `src/mingli_engine/markdown.py`
- Inspect: `tests/unit/test_report_schema.py`
- Inspect: `tests/unit/test_markdown_renderer.py`
- Inspect: `tests/integration/test_report_regression_cases.py`
- Inspect: `tests/safety/test_red_lines_and_language.py`

- [ ] **Step 1: Run report-focused tests**

```powershell
uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py tests/integration/test_report_regression_cases.py -v
```

Expected: PASS.

- [ ] **Step 2: Run full test suite**

```powershell
uv run --with pytest python -m pytest
```

Expected: PASS.

- [ ] **Step 3: Run diff check**

```powershell
git diff --check
```

Expected: exit code 0. Windows line-ending warnings are acceptable if there are no whitespace errors.

- [ ] **Step 4: Inspect final status**

```powershell
git status --short --branch
```

Expected: branch `009-report-evidence-notes` with a clean worktree after commits.
