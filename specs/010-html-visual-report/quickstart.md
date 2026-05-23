# Quickstart: HTML 可视化报告

## Prerequisites

Run commands from the repository root:

```powershell
cd E:\命理演绎
```

## Run Focused HTML Renderer Tests

After implementation, run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_html_renderer.py -v
```

Expected:

- HTML renderer returns a complete document starting with `<!doctype html>`.
- HTML includes title, disclaimer, quick guide, all four report layers, glossary, and ethics reminder.
- HTML keeps `观察依据` after ten-god summary and before structure analysis.
- HTML escapes special characters in report text.
- HTML contains no `<script>` tags or external resources.

## Run CLI HTML Tests

```powershell
uv run --with pytest python -m pytest tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -v
```

Expected:

- `calculate-report --format html` returns a complete HTML report for `examples\birth-profile.auto-gregorian.json`.
- `generate-report --format html` returns a complete HTML report for `examples\bazi-chart.external-verified.json`.
- Existing `--format markdown` tests continue passing.
- Invalid input and missing required birth data do not produce partial HTML.

## Run Regression And Safety Tests

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_red_lines_and_language.py -v
```

Expected:

- Safe report regression cases protect HTML output or HTML-specific contract checks.
- Unsafe red-line report requests with `--format html` return safety JSON.
- Safety JSON output does not contain `<!doctype html>`.
- Existing absolute-language and red-line tests continue passing.

## Run Full Test Suite

```powershell
uv run --with pytest python -m pytest
```

Expected: all tests pass.

## Manual HTML Spot Check

Generate the automatic chart HTML report:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format html
```

Confirm the output includes:

- `<!doctype html>`
- `<html lang="zh-CN">`
- `免责声明`
- `快速导读`
- `第一层：基础资料`
- `第二层：结构观察`
- `观察依据`
- `第三层：解读边界`
- `第四层：行动反思`
- `伦理边界提醒`

Generate the external verified HTML report:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format html
```

Confirm the output:

- starts with `<!doctype html>`
- includes external verified source wording
- does not mislabel the source as automatic chart output

Generate the unsafe focus case:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.unsafe-focus.json --format html
```

Expected:

- Exit code `3`
- JSON output with `allowed: false`
- no `<!doctype html>`
- no formal HTML report
