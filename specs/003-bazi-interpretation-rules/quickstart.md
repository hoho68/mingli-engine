# Quickstart: 八字基础结构解读规则层

## Prerequisites

- Work from the repository root.
- Keep `PYTHONPATH` pointed at `src` when running the package directly.

```powershell
cd E:\命理演绎
$env:PYTHONPATH='src'
```

## Run The Full Test Suite

```powershell
uv run --with pytest python -m pytest
```

Expected result after implementation: all tests pass.

## Generate A Report From Automatic Chart Calculation

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Expected result after implementation:

- Output starts with `# 八字结构化报告`.
- `排盘来源与假设` still shows `auto_calculated`, `未人工复核`, and confidence.
- The report includes richer `五行信号观察`, `日主`, `十神`, and `基础结构观察` wording.
- The report states that this layer does not decide `格局`, `用神`, or `大运流年`.

## Generate A Report From An External Verified Chart

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

Expected result after implementation:

- Existing source disclosure remains visible.
- The report includes the same basic interpretation layer without requiring new input fields.
- Ten-god placement is summarized by pillar when available.

## Verify Safety Refusal Is Unchanged

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.unsafe-focus.json --format markdown
```

Expected result after implementation:

- Command exits with code `3`.
- Output is safety JSON, not Markdown.
- The JSON includes `allowed: false` and `lifespan_or_death_timing`.

## Focused Verification Commands

```powershell
uv run --with pytest python -m pytest tests\unit\test_interpretation.py -v
uv run --with pytest python -m pytest tests\unit\test_report_schema.py -v
uv run --with pytest python -m pytest tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py -v
uv run --with pytest python -m pytest tests\safety\test_red_lines_and_language.py -v
```

Expected result after implementation: each command passes, and generated formal reports contain no absolute destiny language.
