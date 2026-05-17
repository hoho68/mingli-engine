# Quickstart: 八字报告白话表达优化

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

Expected reader-facing wording:

- includes `系统自动排盘`
- includes `中等可信度`
- includes `公历`
- includes `年柱`, `月柱`, `日柱`, and `时柱`
- does not include `auto_calculated`, `medium`, `gregorian`, `year：`, `month：`, `day：`, or `hour：`

## Generate External-Chart Markdown

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

Expected reader-facing wording:

- includes `外部排盘已核对`
- preserves the external source note
- includes the same 004 layered heading order
- does not include `external_verified`

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

## Run Tests

```powershell
uv run --with pytest python -m pytest
```

Expected: all tests pass.
