# Quickstart: 经典证据库精修

## 1. Verify Source And Evidence Loading

Run the existing source registry tests after expanding the corpus:

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py -v
```

Expected result:

- All nine sources remain present.
- Approved evidence links only to approved sources.
- Unreviewed, blocked, and failed sources cannot support conclusions.

## 2. Verify Curation Quality

Run the curation quality tests:

```powershell
uv run --with pytest python -m pytest tests/unit/test_evidence_curation.py -v
```

Expected result:

- The corpus has at least 60 approved evidence units.
- At least eight rule families have approved evidence coverage.
- Every source has evidence coverage or an explicit curation gap.
- High-risk evidence has limitations.
- Long copied passages and guaranteed-outcome summaries are rejected.
- Current 012 snapshot: 60 approved evidence units, 10 rule families, 10 high-risk units with non-exact limitations, and two explicit source gaps.

## 3. Verify Formal Interpretation With Expanded Evidence

Run the formal interpretation tests:

```powershell
uv run --with pytest python -m pytest tests/unit/test_formal_interpretation.py -v
```

Expected result:

- Formal conclusions use expanded evidence ids.
- Conflicted or insufficient evidence downgrades conclusion strength.
- Disagreement notes appear when source conflicts apply.
- Current 012 snapshot includes documented useful-god school difference notes and an open severe high-risk scope conflict.

## 4. Verify Report Regression

Run the report regression cases:

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -v
```

Expected result:

- Safe Markdown and HTML reports keep source summary, evidence trace, conclusion strength, disclaimer, and chart assumptions.
- High-risk narrowed reports remain conditional and non-exact.
- Exact-outcome requests still return safety JSON.

## 5. Verify High-Risk Language

Run the high-risk safety tests:

```powershell
uv run --with pytest python -m pytest tests/safety/test_expanded_high_risk_language.py -v
```

Expected result:

- General high-risk traditional signals can be discussed with uncertainty.
- Exact death timing, exact lifespan, diagnosis/treatment, legal, psychological, investment, coercive matching, anxiety creation, and paid-remedy upsells remain refused or narrowed.
- No generated formal report contains absolute destiny phrases.

## 6. Full Validation

Run the full suite before marking implementation complete:

```powershell
uv run --with pytest python -m pytest
git diff --check
```

Expected result:

- All tests pass.
- Whitespace validation has exit code 0.
- Any remaining source curation gaps are explicit in the coverage report.
- Before completion, confirm `docs/classical_sources/coverage.md` reflects the current derived counts and remaining gaps.
