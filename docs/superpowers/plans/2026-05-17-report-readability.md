# Report Readability Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render Bazi Markdown reports as a layered reading experience with a quick guide, factual layer, structure layer, boundary layer, and action-reflection layer.

**Architecture:** `report_schema.py` prepares readability-specific report text such as the quick guide and explicit boundary layer. `markdown.py` remains the layout boundary and renders the new layer headings. CLI commands stay unchanged and continue to call the same report builder and Markdown renderer.

**Tech Stack:** Python 3.12+, dataclasses, existing CLI/report modules, pytest, no new runtime dependencies.

---

## File Structure

- Modify: `src/mingli_engine/models.py`
  - Add `quick_guide` and `interpretation_boundaries` fields to `Report`.
- Modify: `src/mingli_engine/report_schema.py`
  - Build quick-guide bullets and explicit boundary text from existing chart, source, and interpretation data.
- Modify: `src/mingli_engine/markdown.py`
  - Render the report using `快速导读` and the four reading layers.
- Modify: `tests/unit/test_report_schema.py`
  - Verify quick-guide content and boundary text at the schema level.
- Modify: `tests/unit/test_markdown_renderer.py`
  - Verify heading order and layered Markdown structure.
- Modify: `tests/integration/test_generate_markdown_report.py`
  - Verify layered output for external chart reports.
- Modify: `tests/integration/test_calculate_report_cli.py`
  - Verify layered output for automatic chart reports.
- Modify: `tests/safety/test_red_lines_and_language.py`
  - Keep generated-report prohibited-language coverage aligned with layered output.

## Task 1: Prepare Quick Guide And Boundary Text

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/report_schema.py`
- Modify: `tests/unit/test_report_schema.py`

- [ ] **Step 1: Write failing report schema tests**

Append to `tests/unit/test_report_schema.py`:

```python
def test_build_report_prepares_quick_guide_and_boundary_layer(sample_bazi_chart):
    report = build_report(sample_bazi_chart)
    guide_lines = [
        line for line in report.quick_guide.splitlines() if line.startswith("- ")
    ]

    assert 3 <= len(guide_lines) <= 5
    assert sample_bazi_chart.chart_source.source_type in report.quick_guide
    assert sample_bazi_chart.chart_source.confidence in report.quick_guide
    assert sample_bazi_chart.birth_profile.focus_topic in report.quick_guide
    assert "结构" in report.quick_guide
    assert "不做格局定论" in report.interpretation_boundaries
    assert "不做用神定论" in report.interpretation_boundaries
    assert "不做大运流年判断" in report.interpretation_boundaries
    assert report.interpretation_boundaries not in report.structure_analysis
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_report_schema.py::test_build_report_prepares_quick_guide_and_boundary_layer -v
```

Expected: failure because `Report` has no `quick_guide` or `interpretation_boundaries` fields.

- [ ] **Step 3: Add fields to the report model**

In `src/mingli_engine/models.py`, update `Report` so these fields appear after `disclaimer` and before `glossary` respectively:

```python
    quick_guide: str
```

and:

```python
    interpretation_boundaries: str
```

- [ ] **Step 4: Build quick-guide text in report schema**

In `src/mingli_engine/report_schema.py`, add:

```python
def _format_elements_for_report(elements: list[str]) -> str:
    return "、".join(elements) if elements else "暂无突出信号"


def _build_quick_guide(chart: BaziChart, interpretation) -> str:
    source = chart.chart_source
    focus_topic = chart.birth_profile.focus_topic.strip() or "当前关注主题"
    dominant = _format_elements_for_report(
        interpretation.element_distribution.dominant_elements
    )
    return "\n".join(
        [
            f"- 来源：{source.source_type}，可信度：{source.confidence}。",
            f"- 结构：当前可先观察{dominant}相关信号的分布。",
            f"- 日主：{chart.day_master}作为观察中心，不作为命运结论。",
            "- 边界：本报告不做格局定论、用神定论或大运流年判断。",
            f"- 提示：围绕{focus_topic}，把结构观察转成可复盘的小问题。",
        ]
    )
```

Inside `build_report`, after `interpretation = build_basic_interpretation(chart)`, add:

```python
    quick_guide = _build_quick_guide(chart, interpretation)
```

Set:

```python
    interpretation_boundaries = interpretation.limitations
```

Set `structure_analysis` to only the observation text:

```python
    structure_analysis = interpretation.structure_observations
```

Pass the new fields to `Report(...)`:

```python
        quick_guide=quick_guide,
        interpretation_boundaries=interpretation_boundaries,
```

Add `quick_guide` and `interpretation_boundaries` to the safety-check body and `_major_body_sections(report)`.

- [ ] **Step 5: Run report schema tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_report_schema.py -v
```

Expected: all report schema tests pass.

- [ ] **Step 6: Commit Task 1**

Run:

```powershell
git add src\mingli_engine\models.py src\mingli_engine\report_schema.py tests\unit\test_report_schema.py
git commit -m "feat: prepare layered report text"
```

## Task 2: Render Layered Markdown

**Files:**
- Modify: `src/mingli_engine/markdown.py`
- Modify: `tests/unit/test_markdown_renderer.py`

- [ ] **Step 1: Add failing renderer structure tests**

Add this helper and test to `tests/unit/test_markdown_renderer.py`:

```python
def _assert_in_order(text: str, headings: tuple[str, ...]) -> None:
    positions = [text.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_render_markdown_report_uses_layered_reading_order(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    markdown = render_markdown_report(report)

    _assert_in_order(
        markdown,
        (
            "# 八字结构化报告",
            "## 免责声明",
            "## 快速导读",
            "## 第一层：基础资料",
            "### 命造卡片",
            "### 排盘来源与假设",
            "## 第二层：结构观察",
            "### 四柱与五行摘要",
            "### 十神摘要",
            "### 结构分析",
            "### 性格倾向",
            "## 第三层：解读边界",
            "## 第四层：行动反思",
            "### 优势与议题",
            "### 阶段概览",
            "### 行动建议",
            "## 术语简注",
            "## 伦理边界提醒",
        ),
    )
```

Update `test_render_markdown_report_contains_required_headings` so it expects `## 快速导读` and the four layer headings instead of only same-level legacy headings.

- [ ] **Step 2: Run renderer tests and verify failure**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_markdown_renderer.py -v
```

Expected: failure because the renderer still uses the old flat heading structure.

- [ ] **Step 3: Render the layered structure**

Replace the `sections` list in `src/mingli_engine/markdown.py` with:

```python
    sections = [
        f"# {report.title}",
        "## 免责声明",
        report.disclaimer,
        "## 快速导读",
        report.quick_guide,
        "## 第一层：基础资料",
        "### 命造卡片",
        report.chart_card,
        "### 排盘来源与假设",
        report.assumptions,
        "## 第二层：结构观察",
        "### 四柱与五行摘要",
        report.four_pillars_summary,
        report.five_elements_summary,
        "### 十神摘要",
        report.ten_gods_summary,
        "### 结构分析",
        report.structure_analysis,
        "### 性格倾向",
        report.personality_tendencies,
        "## 第三层：解读边界",
        report.interpretation_boundaries,
        "## 第四层：行动反思",
        "### 优势与议题",
        report.strengths_and_issues,
        "### 阶段概览",
        report.phase_overview,
        "### 行动建议",
        report.action_suggestions,
        "## 术语简注",
        report.glossary,
        "## 伦理边界提醒",
        report.ethics_reminder,
    ]
```

- [ ] **Step 4: Run renderer tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_markdown_renderer.py -v
```

Expected: all renderer tests pass.

- [ ] **Step 5: Commit Task 2**

Run:

```powershell
git add src\mingli_engine\markdown.py tests\unit\test_markdown_renderer.py
git commit -m "feat: render layered markdown report"
```

## Task 3: Update CLI And Safety Coverage

**Files:**
- Modify: `tests/integration/test_generate_markdown_report.py`
- Modify: `tests/integration/test_calculate_report_cli.py`
- Modify: `tests/safety/test_red_lines_and_language.py`

- [ ] **Step 1: Add layered CLI assertions**

In both integration test files, add this helper:

```python
def _assert_in_order(text: str, headings: tuple[str, ...]) -> None:
    positions = [text.index(heading) for heading in headings]
    assert positions == sorted(positions)
```

In the successful Markdown report tests, assert:

```python
    _assert_in_order(
        markdown,
        (
            "## 快速导读",
            "## 第一层：基础资料",
            "## 第二层：结构观察",
            "## 第三层：解读边界",
            "## 第四层：行动反思",
        ),
    )
    assert "### 排盘来源与假设" in markdown
    assert "### 四柱与五行摘要" in markdown
    assert "### 行动建议" in markdown
```

Keep existing source-disclosure, interpretation, unsafe-topic, and prohibited-phrase assertions.

- [ ] **Step 2: Add or update safety generated-report assertion**

In `tests/safety/test_red_lines_and_language.py`, ensure the generated Markdown safety test asserts:

```python
    assert "## 快速导读" in markdown
    assert "## 第三层：解读边界" in markdown
```

Keep the prohibited phrase checks.

- [ ] **Step 3: Run integration and safety tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py tests\safety\test_red_lines_and_language.py -v
```

Expected: all selected tests pass, including existing exit code `3` safety cases.

- [ ] **Step 4: Commit Task 3**

Run:

```powershell
git add tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py tests\safety\test_red_lines_and_language.py
git commit -m "test: cover layered report output"
```

## Task 4: Full Verification

**Files:**
- Read: `specs/004-report-readability/spec.md`
- Read: `specs/004-report-readability/contracts/layered-markdown-contract.md`

- [ ] **Step 1: Run focused verification**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_report_schema.py tests\unit\test_markdown_renderer.py tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py tests\safety\test_red_lines_and_language.py -v
```

Expected: all selected tests pass.

- [ ] **Step 2: Run the full suite**

Run:

```powershell
uv run --with pytest python -m pytest
```

Expected: all tests pass.

- [ ] **Step 3: Inspect generated Markdown manually**

Run:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Expected output includes `快速导读`, all four layer headings, visible source disclosure, visible interpretation boundary language, focus-topic action reflection, and no prohibited absolute destiny language.

- [ ] **Step 4: Confirm worktree status**

Run:

```powershell
git status --short --branch
```

Expected: branch is `004-report-readability` with no uncommitted implementation changes.
