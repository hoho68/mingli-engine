# Quickstart: Existing Materials Audit and Preparation

## Goal

Use 015 to make the current local source corpus auditable before the next candidate-extraction cycle. The workflow inventories existing materials, aligns them with the 014 source library, assesses preparation and risk readiness, and produces a small next-action queue.

## Current Boundary

- Root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` are external preparation materials.
- Do not move, delete, rename, convert, commit, or mutate those materials unless the user explicitly asks.
- Prepared Markdown, cleaned Markdown, learning notes, and knowledge-skeleton artifacts are preparation aids, not evidence.
- Audit records and queue items are planning metadata, not candidate extracts.
- Reports may use only approved and promoted formal evidence units from the reviewed corpus.

## Maintainer Workflow

1. Discover current material groups across root PDFs, Markdown batches, cleaned Markdown folders, learning notes, source processing notes, and knowledge-skeleton artifacts.
2. Group representations that refer to the same source, preserving uncertain, duplicate, and edition-variant relationships instead of silently merging them.
3. Compare each material group with 014 source-library entries and record exact matches, likely matches, missing registrations, duplicates, blocked entries, and out-of-scope materials.
4. Assess preparation readiness separately from extraction readiness. Cleaned text is useful preparation, but it is not formal evidence.
5. Label sensitive and high-risk materials before extraction planning, especially life-death, illness, disaster, coercive, remedy, paid-pressure, and absolute-verdict themes.
6. Put ready materials in a limited extraction-ready queue only when source identity, locator confidence, rights notes, source-library relationship, rule-family target, and risk boundary are sufficient.
7. Put useful but incomplete materials in preparation, registration, locator-review, or risk-review backlogs with clear missing prerequisites.
8. Preserve duplicate, deferred, blocked, uncertain, and out-of-scope findings with durable reasons.
9. Use the progress summary to choose the next five recommended extraction or preparation actions.

## Expected Validation Commands

Run the materials-audit quality check from the local package after implementation:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.materials_audit import build_materials_audit_progress_summary, validate_materials_audit_quality; print(build_materials_audit_progress_summary()); print(validate_materials_audit_quality())"
```

Expected result after implementation:

- The progress summary prints 16 audited material groups, 26 material
  representations, source-alignment counts, readiness counts, queue counts,
  risk counts, source-boundary counts, material-scope counts, text-preparation
  counts, locator-confidence counts, source-quality counts,
  missing-prerequisite counts, and next recommended queue item ids.
- The queue summary includes 5 `extraction_ready` items, 3
  `registration_backlog` items, 4 `risk_review_backlog` items, 1
  `preparation_backlog` item, 2 `blocked_backlog` items, 1 deferred queue item,
  and 1 blocked queue item.
- The next recommended queue item ids are:
  `queue_northeast_blind_peak_extract`,
  `queue_mingli_true_formula_teacher_extract`,
  `queue_markdown_source_batch_001_register`,
  `queue_blind_life_manual_risk_review`, and
  `queue_blind_school_secret_blocked`.
- The quality check prints `[]`.

Run focused materials-audit tests:

```powershell
uv run --with pytest python -m pytest tests/unit/test_materials_audit.py
```

Run boundary regression tests after changing audit links:

```powershell
uv run --with pytest python -m pytest tests/unit/test_materials_audit.py tests/unit/test_source_library.py tests/unit/test_source_intake.py tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py
```

Run all tests:

```powershell
uv run --with pytest python -m pytest
```

## Manual Review Checklist

- Every discovered material group has a stable audit id, title or label, preparation state, source boundary, and recommended next action.
- Raw files and external preparation folders remain untouched.
- Prepared and cleaned Markdown files are represented as preparation aids only.
- Source-library matches, missing registrations, duplicates, edition variants, and uncertain relationships are visible.
- Extraction-ready queue items include source-library relationship, readiness rationale, target rule family or gap, source quality note, risk boundary, and pre-extraction checks.
- Useful but not-ready materials appear in a preparation or registration backlog with missing prerequisites.
- Sensitive and high-risk materials are labeled before extraction.
- Deferred and blocked queue items remain visible with durable reasons.
- Out-of-scope materials are deferred from the current Bazi evidence workflow.
- Audit metadata avoids long copied passages.
- Audit records and queue items do not count as formal report-usable evidence.

## Done Criteria

- Existing materials can be audited deterministically without network access.
- Audit progress can identify matched sources, missing registrations, ready materials, backlog items, high-risk items, deferred items, and blocked items.
- Maintainers can identify the next five recommended extraction or preparation actions within 5 minutes.
- No raw source files or external preparation folders are mutated.
- No audited material, prepared text, cleaned text, or queue item is counted as report evidence.
- Full test suite passes.
