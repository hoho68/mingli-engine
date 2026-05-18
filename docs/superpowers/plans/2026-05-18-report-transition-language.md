# Report Transition Language Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add concise transition wording across the existing layered Markdown report so readers can follow the safe path from source assumptions to structure observation, interpretation boundaries, and action reflection.

**Architecture:** Keep transition wording in `src/mingli_engine/report_schema.py`, where report fields are assembled and safety-reviewed. Keep `src/mingli_engine/markdown.py` as a layout-only renderer. Preserve `src/mingli_engine/interpretation.py` wording from feature 006 unless a test proves a tiny bridge must live beside existing interpretation text.

**Tech Stack:** Python 3.12+, existing `mingli_engine` package, pytest, PowerShell commands on Windows.

---

### Task 1: Lock Report Schema Transition Wording With Failing Tests

**Files:**
- Modify: `tests/unit/test_report_schema.py`

- [ ] **Step 1: Add transition assertions to quick guide test**

Update `test_build_report_prepares_quick_guide_and_boundary_layer` with:

```python
assert "先核对资料与假设" in report.quick_guide
assert "再看结构观察" in report.quick_guide
assert "最后转成行动反思" in report.quick_guide
```

- [ ] **Step 2: Add a dedicated transition test**

Add this test near the other report schema wording tests:

```python
def test_build_report_connects_layers_with_transition_language(sample_bazi_chart):
    report = build_report(_chart_with_contract_labels(sample_bazi_chart))

    assert "这些基础资料只说明排盘依据与采用假设，不直接构成命理结论" in report.assumptions
    assert "结构观察提供的是线索，不是最终判断" in report.structure_analysis
    assert "这些边界是为了防止过度断言" in report.interpretation_boundaries
    assert "再把可观察的线索转成复盘问题" in report.interpretation_boundaries
    assert "行动反思只作为复盘提示" in report.strengths_and_issues
    assert "不是对结果的承诺" in report.action_suggestions
```

- [ ] **Step 3: Run report schema tests and verify failure**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_report_schema.py -v
```

Expected: FAIL because transition wording is not implemented yet.

- [ ] **Step 4: Commit failing schema tests**

```powershell
git add tests/unit/test_report_schema.py
git commit -m "test: lock report transition wording"
```

### Task 2: Lock Final Markdown Transition Behavior With Failing Tests

**Files:**
- Modify: `tests/unit/test_markdown_renderer.py`
- Modify: `tests/integration/test_calculate_report_cli.py`
- Modify: `tests/integration/test_generate_markdown_report.py`

- [ ] **Step 1: Update Markdown renderer test**

Add to `test_render_markdown_report_uses_layered_reading_order`:

```python
assert "先核对资料与假设" in markdown
assert "结构观察提供的是线索，不是最终判断" in markdown
assert "这些边界是为了防止过度断言" in markdown
assert "行动反思只作为复盘提示" in markdown
```

- [ ] **Step 2: Update both CLI integration tests**

In both successful Markdown integration tests, add:

```python
assert "先核对资料与假设" in markdown
assert "这些基础资料只说明排盘依据与采用假设，不直接构成命理结论" in markdown
assert "结构观察提供的是线索，不是最终判断" in markdown
assert "这些边界是为了防止过度断言" in markdown
assert "行动反思只作为复盘提示" in markdown
assert "五行数量可以先作为结构观察材料来看" in markdown
assert "十神关系可以先按四个柱位理解为结构线索" in markdown
assert "基础结构可以先看分布是否集中" in markdown
```

- [ ] **Step 3: Run focused Markdown tests and verify failure**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_markdown_renderer.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v
```

Expected: FAIL because transition wording is not implemented yet.

- [ ] **Step 4: Commit failing Markdown tests**

```powershell
git add tests/unit/test_markdown_renderer.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py
git commit -m "test: cover report transition markdown"
```

### Task 3: Implement Minimal Transition Wording

**Files:**
- Modify: `src/mingli_engine/report_schema.py`

- [ ] **Step 1: Add transition constants near label constants**

Add:

```python
READING_PATH_TRANSITION = "阅读时可以先核对资料与假设，再看结构观察，再看解读边界，最后转成行动反思。"
SOURCE_BASIS_TRANSITION = "这些基础资料只说明排盘依据与采用假设，不直接构成命理结论。"
STRUCTURE_BOUNDARY_TRANSITION = "结构观察提供的是线索，不是最终判断；下一层会说明哪些地方不能过度解读。"
BOUNDARY_ACTION_TRANSITION = "这些边界是为了防止过度断言；在边界内，再把可观察的线索转成复盘问题。"
ACTION_REFLECTION_TRANSITION = "行动反思只作为复盘提示，用来整理可观察的线索，不替代现实判断。"
```

- [ ] **Step 2: Include reading path in quick guide**

In `_build_quick_guide`, replace the boundary bullet with:

```python
f"- 路径：{READING_PATH_TRANSITION}",
```

Keep the quick guide at five bullets.

- [ ] **Step 3: Append source basis transition to assumptions**

In `build_report`, after `assumptions = _build_assumptions(chart)`, add:

```python
assumptions = f"{assumptions}\n{SOURCE_BASIS_TRANSITION}"
```

- [ ] **Step 4: Append structure transition to structure analysis**

Replace:

```python
structure_analysis = interpretation.structure_observations
```

with:

```python
structure_analysis = (
    f"{interpretation.structure_observations}\n{STRUCTURE_BOUNDARY_TRANSITION}"
)
```

- [ ] **Step 5: Append boundary transition to interpretation boundaries**

Replace:

```python
interpretation_boundaries = interpretation.limitations
```

with:

```python
interpretation_boundaries = (
    f"{interpretation.limitations}\n{BOUNDARY_ACTION_TRANSITION}"
)
```

- [ ] **Step 6: Add reflection transition to strengths and issues**

After `strengths_and_issues` is normalized, prefix it with:

```python
strengths_and_issues = f"{ACTION_REFLECTION_TRANSITION}\n{strengths_and_issues}"
```

- [ ] **Step 7: Run focused tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v
```

Expected: PASS.

- [ ] **Step 8: Commit implementation**

```powershell
git add src/mingli_engine/report_schema.py
git commit -m "feat: connect report layers with transitions"
```

### Task 4: Safety And Full Verification

**Files:**
- Inspect: `tests/safety/test_red_lines_and_language.py`
- Inspect: generated CLI output when useful

- [ ] **Step 1: Run safety tests**

```powershell
uv run --with pytest python -m pytest tests/safety/test_red_lines_and_language.py -v
```

Expected: PASS.

- [ ] **Step 2: Run full test suite**

```powershell
uv run --with pytest python -m pytest
```

Expected: PASS.

- [ ] **Step 3: Generate one sample report for manual transition check**

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Expected: output includes reading path, source-basis, structure-boundary, boundary-action, and action-reflection wording while preserving 005 labels and 006 structure wording.

- [ ] **Step 4: Commit any verification-only test adjustment if needed**

Only run this if Task 4 required a small test-only fix:

```powershell
git add tests
git commit -m "test: verify report transition safety"
```

If no files changed, do not create an empty commit.
