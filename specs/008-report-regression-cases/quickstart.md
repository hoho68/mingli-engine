# Quickstart: 报告回归样例清单

## Prerequisites

Run commands from the repository root:

```powershell
cd E:\命理演绎
```

## Inspect Regression Case Manifest

```powershell
Get-Content examples\report-regression-cases.json
```

Expected:

- Contains at least three cases.
- Includes a safe automatic chart case.
- Includes a safe external verified chart case.
- Includes a safety JSON red-line case.

## Run Focused Regression Cases

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v
```

Expected:

- Manifest validation passes.
- Safe Markdown cases produce formal Markdown reports.
- Safety JSON cases return refusal JSON.

## Run Existing Report Integration Tests

```powershell
uv run --with pytest python -m pytest tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py tests/integration/test_report_regression_cases.py -v
```

Expected:

- Existing report paths still pass.
- Manifest-driven regression cases pass.

## Run Full Test Suite

```powershell
uv run --with pytest python -m pytest
```

Expected: all tests pass.

## Manual Spot Check

Generate the automatic chart report:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Confirm the output still includes:

- `# 八字结构化报告`
- `系统自动排盘`
- `五行数量可以先作为结构观察材料来看`
- `先核对资料与假设`
- `行动反思只作为复盘提示`

Generate the unsafe focus case:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.unsafe-focus.json --format markdown
```

Expected:

- Exit code `3`
- JSON output with `allowed: false`
- red-line category `lifespan_or_death_timing`
