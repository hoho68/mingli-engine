# Report Regression Cases Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a manifest-driven regression sample library that protects key Markdown report contracts and safety JSON behavior.

**Architecture:** Keep this feature in examples and tests. Add `examples/report-regression-cases.json` as the representative case manifest and `tests/integration/test_report_regression_cases.py` as the CLI-level validator. Do not modify production code unless the tests reveal an existing contract gap.

**Tech Stack:** Python 3.12+, existing `mingli_engine` CLI, JSON manifest, pytest, PowerShell commands on Windows.

---

### Task 1: Add Failing Manifest-Driven Regression Tests

**Files:**
- Create: `tests/integration/test_report_regression_cases.py`

- [ ] **Step 1: Create the regression test file**

Create `tests/integration/test_report_regression_cases.py` with this content:

```python
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"
MANIFEST_PATH = EXAMPLES_DIR / "report-regression-cases.json"

REQUIRED_FIELDS = {"id", "kind", "command", "input", "purpose"}
SUPPORTED_KINDS = {"safe_markdown", "safety_json"}
SUPPORTED_COMMANDS = {"calculate-report", "generate-report"}
RAW_READER_LABELS = (
    "auto_calculated",
    "external_verified",
    "medium",
    "gregorian",
    "year：",
    "month：",
    "day：",
    "hour：",
)
ABSOLUTE_DESTINY_PHRASES = ("必定", "注定", "一定会", "死定")
LAYER_HEADINGS = (
    "## 快速导读",
    "## 第一层：基础资料",
    "## 第二层：结构观察",
    "## 第三层：解读边界",
    "## 第四层：行动反思",
)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_path = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else os.pathsep.join([src_path, env["PYTHONPATH"]])
    )
    return subprocess.run(
        [sys.executable, "-m", "mingli_engine.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def _load_cases() -> list[dict[str, str]]:
    assert MANIFEST_PATH.exists(), "Missing report regression manifest"
    cases = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(cases, list)
    assert cases
    return cases


def _assert_in_order(text: str, headings: tuple[str, ...]) -> None:
    lines = text.splitlines()
    positions = [lines.index(heading) for heading in headings]
    assert positions == sorted(positions)


def _assert_manifest_case_shape(case: dict[str, str]) -> None:
    assert REQUIRED_FIELDS.issubset(case), case
    assert case["kind"] in SUPPORTED_KINDS
    assert case["command"] in SUPPORTED_COMMANDS
    input_path = REPO_ROOT / case["input"]
    assert input_path.exists(), case
    if case["kind"] == "safe_markdown":
        assert case.get("source_type") in {"auto_calculated", "external_verified"}
    if case["kind"] == "safety_json":
        assert case.get("expected_category")


def _assert_safe_markdown(case: dict[str, str], result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, result.stderr
    markdown = result.stdout
    assert markdown.startswith("# 八字结构化报告")
    _assert_in_order(markdown, LAYER_HEADINGS)
    assert "### 排盘来源与假设" in markdown.splitlines()
    assert "### 四柱与五行摘要" in markdown.splitlines()
    assert "公历" in markdown
    for pillar_name in ("年柱", "月柱", "日柱", "时柱"):
        assert f"- {pillar_name}：" in markdown
    assert "五行数量可以先作为结构观察材料来看" in markdown
    assert "十神关系可以先按四个柱位理解为结构线索" in markdown
    assert "基础结构可以先看分布是否集中" in markdown
    assert "先核对资料与假设" in markdown
    assert "结构观察提供的是线索，不是最终判断" in markdown
    assert "这些边界是为了防止过度断言" in markdown
    assert "行动反思只作为复盘提示" in markdown
    for raw_label in RAW_READER_LABELS:
        assert raw_label not in markdown
    for phrase in ABSOLUTE_DESTINY_PHRASES:
        assert phrase not in markdown
    if case["source_type"] == "auto_calculated":
        assert "系统自动排盘" in markdown
        assert "中等可信度" in markdown
    if case["source_type"] == "external_verified":
        assert "外部排盘已核对" in markdown
        assert "来源类型：系统自动排盘" not in markdown


def _assert_safety_json(case: dict[str, str], result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 3, result.stderr
    assert not result.stdout.startswith("# 八字结构化报告")
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert case["expected_category"] in payload["red_line_categories"]


def test_report_regression_manifest_is_valid():
    cases = _load_cases()
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids))
    for case in cases:
        _assert_manifest_case_shape(case)
    assert any(
        case["kind"] == "safe_markdown" and case.get("source_type") == "auto_calculated"
        for case in cases
    )
    assert any(
        case["kind"] == "safe_markdown" and case.get("source_type") == "external_verified"
        for case in cases
    )
    assert any(case["kind"] == "safety_json" for case in cases)


def test_report_regression_cases_exercise_cli_contracts():
    for case in _load_cases():
        result = _run_cli(
            case["command"],
            "--input",
            str(REPO_ROOT / case["input"]),
            "--format",
            "markdown",
        )
        if case["kind"] == "safe_markdown":
            _assert_safe_markdown(case, result)
        elif case["kind"] == "safety_json":
            _assert_safety_json(case, result)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v
```

Expected: FAIL with `Missing report regression manifest`.

- [ ] **Step 3: Commit failing test**

```powershell
git add tests/integration/test_report_regression_cases.py
git commit -m "test: add report regression case harness"
```

### Task 2: Add The Regression Case Manifest

**Files:**
- Create: `examples/report-regression-cases.json`

- [ ] **Step 1: Create the manifest**

Create `examples/report-regression-cases.json` with this content:

```json
[
  {
    "id": "safe-auto-gregorian",
    "kind": "safe_markdown",
    "command": "calculate-report",
    "input": "examples/birth-profile.auto-gregorian.json",
    "purpose": "Guards automatic chart Markdown report structure, reader-facing labels, structure observation wording, and transition wording.",
    "source_type": "auto_calculated"
  },
  {
    "id": "safe-external-verified",
    "kind": "safe_markdown",
    "command": "generate-report",
    "input": "examples/bazi-chart.external-verified.json",
    "purpose": "Guards external verified Markdown report structure, external source labeling, structure observation wording, and transition wording.",
    "source_type": "external_verified"
  },
  {
    "id": "unsafe-lifespan-focus",
    "kind": "safety_json",
    "command": "calculate-report",
    "input": "examples/birth-profile.unsafe-focus.json",
    "purpose": "Guards red-line refusal behavior for lifespan or death timing focus topics.",
    "expected_category": "lifespan_or_death_timing"
  }
]
```

- [ ] **Step 2: Run the focused test and verify GREEN**

Run:

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v
```

Expected: PASS.

- [ ] **Step 3: Commit manifest**

```powershell
git add examples/report-regression-cases.json
git commit -m "test: add report regression case manifest"
```

### Task 3: Verify Integration With Existing Report Tests

**Files:**
- Inspect: `tests/integration/test_calculate_report_cli.py`
- Inspect: `tests/integration/test_generate_markdown_report.py`
- Inspect: `tests/integration/test_report_regression_cases.py`

- [ ] **Step 1: Run integration report tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py tests/integration/test_report_regression_cases.py -v
```

Expected: PASS.

- [ ] **Step 2: Run safety tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/safety/test_red_lines_and_language.py -v
```

Expected: PASS.

- [ ] **Step 3: Commit only if verification required a test adjustment**

If no files changed, do not commit. If a focused test adjustment was needed:

```powershell
git add tests/integration/test_report_regression_cases.py
git commit -m "test: refine report regression contracts"
```

### Task 4: Full Verification

**Files:**
- Inspect: `examples/report-regression-cases.json`
- Inspect: `tests/integration/test_report_regression_cases.py`

- [ ] **Step 1: Run full test suite**

Run:

```powershell
uv run --with pytest python -m pytest
```

Expected: PASS.

- [ ] **Step 2: Run diff check**

Run:

```powershell
git diff --check
```

Expected: exit code 0. Windows line-ending warnings are acceptable if there are no whitespace errors.

- [ ] **Step 3: Inspect final status**

Run:

```powershell
git status --short --branch
```

Expected: branch `008-report-regression-cases` with only intentional changes, or clean after commits.
