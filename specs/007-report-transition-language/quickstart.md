# Quickstart: 报告层间衔接语优化

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

Expected transition behavior:

- includes `## 快速导读`
- includes a concise reading path cue from source assumptions to structure observation, boundaries, and action reflection
- includes source-as-basis wording in `第一层：基础资料`
- includes clue-not-conclusion wording around `第二层：结构观察`
- includes boundary-to-reflection wording around `第三层：解读边界` or `第四层：行动反思`
- keeps feature 006 phrases such as `五行数量可以先作为结构观察材料来看`

## Generate External-Chart Markdown

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

Expected compatibility behavior:

- includes `外部排盘已核对`
- preserves the external source note
- keeps 004 heading order
- uses the same transition wording as automatic-chart reports

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
uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py tests/safety/test_red_lines_and_language.py
```

Expected: all focused tests pass.

## Run Full Test Suite

```powershell
uv run --with pytest python -m pytest
```

Expected: all tests pass.
