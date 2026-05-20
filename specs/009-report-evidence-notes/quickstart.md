# Quickstart: 报告证据说明层

## Prerequisites

Run commands from the repository root:

```powershell
cd E:\命理演绎
```

## Run Focused Unit Tests

After implementation, run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py -v
```

Expected:

- Report schema tests confirm the evidence-note field exists and includes source, four-pillar, five-element, ten-god, and action basis wording.
- Markdown renderer tests confirm `### 观察依据` appears inside `第二层：结构观察` in the required order.

## Run Focused Regression Cases

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v
```

Expected:

- Safe automatic-chart report includes `### 观察依据`.
- Safe external-verified report includes `### 观察依据` and preserves external source wording.
- Safety JSON cases still return refusal JSON.

## Run Safety Tests

```powershell
uv run --with pytest python -m pytest tests/safety/test_red_lines_and_language.py -v
```

Expected:

- Existing red-line and absolute-language checks continue passing.

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

Confirm the output includes:

- `### 观察依据`
- `来源依据`
- `四柱依据`
- `五行依据`
- `十神依据`
- `行动依据`

Generate the unsafe focus case:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.unsafe-focus.json --format markdown
```

Expected:

- Exit code `3`
- JSON output with `allowed: false`
- no formal Markdown heading
- no `### 观察依据`
