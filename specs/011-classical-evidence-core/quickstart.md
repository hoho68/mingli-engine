# Quickstart: 典籍证据核心与放大报告口径

## 1. Verify The Source Registry

After implementation, run the focused source tests:

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py -v
```

Expected result:

- The nine initial sources are present.
- Every report-usable source has approved review status.
- Evidence units do not point to blocked or unreviewed sources.

## 2. Verify Formal Interpretation

Run the formal interpretation tests:

```powershell
uv run --with pytest python -m pytest tests/unit/test_formal_interpretation.py -v
```

Expected result:

- Formal conclusions include conclusion strength.
- Major conclusions have chart signals and evidence traces.
- Missing evidence downgrades conclusions instead of forcing a judgment.

## 3. Verify High-Risk Handling

Run high-risk safety tests:

```powershell
uv run --with pytest python -m pytest tests/safety/test_expanded_high_risk_language.py -v
```

Expected result:

- Source-backed high-risk signals can be discussed as traditional risk signals.
- Exact death timing, exact lifespan, diagnosis/treatment, legal, psychological, investment, coercive matching, and paid-remedy upsell requests are narrowed or refused.
- Absolute destiny phrases do not appear in formal reports.

## 4. Generate A Formal Markdown Report

Run an existing safe report path:

```powershell
uv run python -m mingli_engine.cli generate-report --input examples/bazi-chart.external-verified.json --format markdown
```

Expected report content:

- Disclaimer remains visible.
- Chart source and calculation assumptions remain visible.
- A source-backed 命理依据 section appears.
- Expanded formal judgment language appears where evidence supports it.
- Evidence traces identify source family, chart signal, and conclusion strength.

## 5. Verify Full Regression

Run the full suite:

```powershell
uv run --with pytest python -m pytest
```

Expected result:

- Existing calculation and rendering contracts still pass.
- Safe Markdown and HTML reports satisfy the same expanded report contract.
- Safety JSON/narrowing behavior remains stable for prohibited exact-outcome requests.
