# Structure Observation Language Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Polish only the report's `第二层：结构观察` wording so it reads as clear professional Chinese prose while preserving all calculations, report structure, CLI behavior, and safety boundaries.

**Architecture:** Keep domain prose generation in `src/mingli_engine/interpretation.py`. Keep 005 reader-facing label formatting in `src/mingli_engine/report_schema.py` and keep Markdown layout in `src/mingli_engine/markdown.py`. Tests should prove both direct interpretation strings and final CLI Markdown output.

**Tech Stack:** Python 3.12+, existing `mingli_engine` package, pytest, PowerShell commands on Windows.

---

### Task 1: Lock Interpretation Wording With Failing Unit Tests

**Files:**
- Modify: `tests/unit/test_interpretation.py`

- [ ] **Step 1: Update the main interpretation wording test**

Replace the structure wording assertions in `test_build_basic_interpretation_explains_day_master_and_ten_gods` with expectations for the new natural report wording:

```python
def test_build_basic_interpretation_explains_day_master_and_ten_gods():
    summary = build_basic_interpretation(balanced_chart())

    assert "五行数量可以先作为结构观察材料来看" in summary.five_elements_summary
    assert "明面信号：" in summary.five_elements_summary
    assert "藏干信号：" in summary.five_elements_summary
    assert "合计信号：" in summary.five_elements_summary
    assert "不等同于完整旺衰模型" in summary.five_elements_summary
    assert "日主戊" in summary.day_master_summary
    assert "观察中心" in summary.day_master_summary
    assert "十神关系可以先按四个柱位理解为结构线索" in summary.ten_gods_summary
    assert "年柱：七杀" in summary.ten_gods_summary
    assert "月柱：食神" in summary.ten_gods_summary
    assert "日柱：日主" in summary.ten_gods_summary
    assert "时柱：伤官" in summary.ten_gods_summary
    assert "基础结构可以先看分布是否集中、哪些信号可见、哪些信号暂时不明显" in summary.structure_observations
    assert "不做格局定论" in summary.limitations
    assert "不做用神定论" in summary.limitations
    assert "不做大运流年判断" in summary.limitations
```

- [ ] **Step 2: Add a regression test for removed system-like phrases**

Add this test near the other interpretation wording tests:

```python
def test_build_basic_interpretation_avoids_system_like_structure_phrases():
    summary = build_basic_interpretation(balanced_chart())
    joined = "\n".join(
        [
            summary.five_elements_summary,
            summary.ten_gods_summary,
            summary.structure_observations,
        ]
    )

    for old_phrase in (
        "五行信号观察：明面信号为",
        "这些数量用于观察结构分布",
        "基础结构观察：五行分布先看有无、多少与集中度。",
    ):
        assert old_phrase not in joined
```

- [ ] **Step 3: Run the focused unit tests and confirm failure**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_interpretation.py -v
```

Expected: FAIL because the implementation still emits the old wording.

- [ ] **Step 4: Commit the failing tests**

```powershell
git add tests/unit/test_interpretation.py
git commit -m "test: lock structure observation wording"
```

### Task 2: Lock Final Markdown Behavior With Failing Integration Tests

**Files:**
- Modify: `tests/integration/test_calculate_report_cli.py`
- Modify: `tests/integration/test_generate_markdown_report.py`
- Modify: `tests/unit/test_report_schema.py`

- [ ] **Step 1: Update `test_report_schema.py` assertions**

Change existing structure text assertions so the assembled report expects the new wording:

```python
assert "五行数量可以先作为结构观察材料来看" in report.five_elements_summary
assert "十神关系可以先按四个柱位理解为结构线索" in report.ten_gods_summary
assert "基础结构可以先看分布是否集中" in report.structure_analysis
```

Also assert the old phrases do not leak:

```python
for old_phrase in (
    "五行信号观察：明面信号为",
    "这些数量用于观察结构分布",
    "基础结构观察：五行分布先看有无、多少与集中度。",
):
    assert old_phrase not in "\n".join(
        [
            report.five_elements_summary,
            report.ten_gods_summary,
            report.structure_analysis,
        ]
    )
```

- [ ] **Step 2: Update CLI integration assertions**

In both CLI integration files, replace old positive checks for system-like headings with new positive checks:

```python
assert "五行数量可以先作为结构观察材料来看" in markdown
assert "明面信号：" in markdown
assert "藏干信号：" in markdown
assert "合计信号：" in markdown
assert "十神关系可以先按四个柱位理解为结构线索" in markdown
assert "基础结构可以先看分布是否集中" in markdown
```

Add old-phrase rejection:

```python
for old_phrase in (
    "五行信号观察：明面信号为",
    "这些数量用于观察结构分布",
    "基础结构观察：五行分布先看有无、多少与集中度。",
):
    assert old_phrase not in markdown
```

- [ ] **Step 3: Run focused report tests and confirm failure**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v
```

Expected: FAIL because implementation still emits old structure wording.

- [ ] **Step 4: Commit the failing report-output tests**

```powershell
git add tests/unit/test_report_schema.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py
git commit -m "test: cover structure observation markdown wording"
```

### Task 3: Implement The Minimal Wording Change

**Files:**
- Modify: `src/mingli_engine/interpretation.py`

- [ ] **Step 1: Update five-element text generation**

In `_build_five_elements_text`, keep the same count variables and replace the first two `parts` strings with:

```python
parts = [
    (
        "五行数量可以先作为结构观察材料来看："
        f"明面信号：{direct_text}；"
        f"藏干信号：{hidden_text}；"
        f"合计信号：{total_text}。"
    ),
    "这些数字只用来帮助观察分布和集中度，不等同于完整旺衰模型，也不是最终结论。",
]
```

Keep the dominant, missing, and unknown-signal branches, but adjust the dominant sentence to:

```python
parts.append(f"当前可计数信号中，{dominant}相对更集中，适合作为后续观察重点。")
```

- [ ] **Step 2: Update ten-god text generation**

In `_build_ten_gods_text`, keep the same `pillar_lines`, missing handling, repeated handling, and summarization. Replace the no-readable-signal sentence with:

```python
text = "十神关系可以先按四个柱位理解为结构线索；当前没有可读的十神信号，本层保留为空白观察。"
```

Replace the readable-signal prefix with:

```python
text = "十神关系可以先按四个柱位理解为结构线索：\n" + "\n".join(pillar_lines)
```

- [ ] **Step 3: Update basic structure observation text**

In `_build_structure_text`, replace the first observation with:

```python
observations = ["基础结构可以先看分布是否集中、哪些信号可见、哪些信号暂时不明显。"]
```

Keep the dominant/missing/balanced branches. If wording is touched, preserve the observation tone and do not add new conclusions.

- [ ] **Step 4: Run focused tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_interpretation.py tests/unit/test_report_schema.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit implementation**

```powershell
git add src/mingli_engine/interpretation.py
git commit -m "feat: polish structure observation wording"
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

- [ ] **Step 3: Generate one sample report for manual language check**

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Expected: output includes the smoother structure wording and does not include the three old system-like phrases.

- [ ] **Step 4: Commit any verification-only test adjustment if needed**

Only run this if Task 4 required a small test-only fix:

```powershell
git add tests
git commit -m "test: verify structure observation safety"
```

If no files changed, do not create an empty commit.
