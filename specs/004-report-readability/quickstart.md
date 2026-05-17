# Quickstart: 报告分层阅读体验优化

## Run Full Verification

```powershell
cd E:\命理演绎
uv run --with pytest python -m pytest
```

Expected result after implementation: all tests pass.

## Generate Automatic Chart Report

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Expected Markdown includes:

- `## 快速导读`
- `## 第一层：基础资料`
- `## 第二层：结构观察`
- `## 第三层：解读边界`
- `## 第四层：行动反思`
- source disclosure and confidence
- focus-topic action reflection

## Generate External Verified Chart Report

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

Expected Markdown includes the same layered structure and preserves the external source note.

## Verify Safety Refusal Is Unchanged

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.unsafe-focus.json --format markdown
```

Expected result:

- exit code `3`
- safety JSON, not Markdown
- includes `allowed: false`
- includes `lifespan_or_death_timing`

## Focused Test Commands

```powershell
uv run --with pytest python -m pytest tests\unit\test_report_schema.py tests\unit\test_markdown_renderer.py -v
uv run --with pytest python -m pytest tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py -v
uv run --with pytest python -m pytest tests\safety\test_red_lines_and_language.py -v
```

Expected result: all selected tests pass.
