# Quickstart: 第二层结构观察表达优化

## Prerequisites

Run commands from the repository root:

```powershell
cd E:\命理演绎
```

## Generate Automatic-Chart Markdown

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Expected structure-layer behavior:

- includes `## 第二层：结构观察`
- five-element text explains counts as observation material
- direct, hidden, and total five-element counts remain visible
- ten-god text still shows pillar relationships
- basic structure text reads as report prose
- does not include `五行信号观察：明面信号为`
- does not include `这些数量用于观察结构分布`
- does not include `基础结构观察：五行分布先看有无、多少与集中度。`

## Generate External-Chart Markdown

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

Expected compatibility behavior:

- keeps the same 004 layered heading order
- keeps 005 reader-facing labels
- preserves source disclosure in `第一层：基础资料`
- uses the same smoother structure observation wording

## Verify Safety Refusal Still Returns JSON

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.unsafe-focus.json --format markdown
```

Expected behavior:

- exit code is `3`
- output is safety JSON, not Markdown
- JSON includes `allowed: false`
- JSON includes `lifespan_or_death_timing`

## Run Focused Tests

```powershell
uv run --with pytest python -m pytest tests/unit/test_interpretation.py tests/unit/test_report_schema.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py tests/safety/test_red_lines_and_language.py
```

Expected: all focused tests pass.

## Run Full Test Suite

```powershell
uv run --with pytest python -m pytest
```

Expected: all tests pass.
