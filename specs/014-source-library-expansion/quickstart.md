# Quickstart: Source Library Expansion and Evidence Factory

## Goal

Use 014 to decide which source materials should be processed next and whether those materials actually produce evidence value after review.

## Current Boundary

- Root PDF files and root `Markdown/` are external preparation material.
- Do not move, delete, convert, or commit those materials unless the user explicitly asks.
- Source-library entries are planning records, not evidence.
- Curation batch plans are planned work, not promotion batches.
- Reports may use only approved and promoted evidence units from the formal corpus.

## Maintainer Workflow

1. Register each source material as a source-library entry with stable identity, local reference, readiness status, topic tags, rule families, source quality notes, rights notes, risk notes, priority, and next action.
2. Mark raw local PDFs and root `Markdown/` references as `external_untracked` unless the user explicitly requests tracking or conversion.
3. Add a priority assessment for sources marked `critical` or `high`, including expected value, target gaps or rule families, source quality, effort, risk, and rationale.
4. Build a curation batch plan from ready sources. Each batch must name a goal, included sources, target gaps or rule families, expected output, risk boundary, and status.
5. Use 013 to extract candidate evidence only after the source is ready and assigned to a reviewable batch.
6. Review candidates through the 013 workflow. Do not count source-library registration or planned batches as report evidence.
7. After review, compute source and batch value summaries from candidate counts, approvals, rejections, blocks, conflicts, gaps, and promoted evidence.
8. Preserve duplicate, deferred, exhausted, rejected, and blocked source outcomes with durable reasons.
9. Use the progress summary to choose the next five highest-priority sources or the next recommended batch focus.

## Expected Validation Commands

Run the source-library quality check from the local package:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_library import build_source_library_progress_report, validate_source_library_quality; print(build_source_library_progress_report()); print(validate_source_library_quality())"
```

Expected result after US1-US4:

- The progress report prints registered source counts, next source ids, high-risk entry ids, and value status counts.
- The quality check prints `[]`.

Run all tests:

```powershell
uv run --with pytest python -m pytest
```

Run focused source-library tests after implementation:

```powershell
uv run --with pytest python -m pytest tests/unit/test_source_library.py
```

Run intake and report-boundary tests after changing source-library links:

```powershell
uv run --with pytest python -m pytest tests/unit/test_source_library.py tests/unit/test_source_intake.py tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py
```

## Manual Review Checklist

- Source-library entries identify materials without tracking or mutating raw root files.
- Ready sources include topic tags, rule families, quality notes, rights notes, risk notes when needed, priority, and next action.
- High-priority sources have priority assessments with target gaps or rule families.
- Batch plans include source entries, target gaps or rule families, expected output, risk boundary, and status.
- Planned batches and registered sources do not count as formal evidence coverage.
- Value summaries are computed from downstream candidate-review and promotion outcomes.
- Non-useful or blocked materials remain visible with durable reasons.
- Source-library metadata rejects report-evidence boundary leaks, absolute outcome language, prohibited high-risk wording, and long copied passages.

## Done Criteria

- Source-library data validates deterministically without network access.
- The progress summary can identify the next five highest-priority extraction candidates.
- Source and batch value summaries separate registration, candidate review, promotion, and formal evidence contribution.
- No registered source, planned batch, or unapproved candidate can be loaded as report-usable evidence.
- Full test suite passes.
