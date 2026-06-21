# Quickstart: Extraction Queue Intake Package

## Goal

Use 016 to turn the 015 materials-audit next-action queue into a bounded extraction work package for the next manual 013 candidate-extraction cycle. The package identifies extraction tasks, candidate draft slots, and prerequisite backlog items while preserving audit, source-library, source-intake, and formal-evidence boundaries.

## Current Boundary

- Root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials.
- Do not move, delete, rename, convert, commit, or mutate those materials unless the user explicitly asks.
- 015 audit records and queue items are planning metadata, not candidate extracts.
- 016 extraction work packages, extraction tasks, candidate draft slots, and prerequisite backlog records are planning metadata, not candidate extracts.
- Reports may use only approved and promoted formal evidence units from the reviewed corpus.

## Maintainer Workflow

1. Load the current 015 materials-audit next-action queue.
2. Cross-check each queue item against current 015 audit records, alignment findings, and readiness findings.
3. Convert eligible `extraction_ready` queue items into extraction tasks.
4. Create candidate draft slots that describe future manual candidate intent without copying source text or extracted meanings.
5. Route registration, preparation, locator-review, risk-review, deferred, and blocked items into prerequisite backlog records.
6. Detect duplicate or overlap risks against existing 013 candidate-intake records.
7. Validate high-risk language, rights notes, locator requirements, and report-evidence boundaries.
8. Use the package summary to decide the next manual extraction and prerequisite actions.

## Expected Validation Commands

Run the extraction queue intake quality check from the local package after implementation:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.extraction_queue_intake import build_package_progress_summary, validate_extraction_package_quality; print(build_package_progress_summary()); print(validate_extraction_package_quality())"
```

Expected result after implementation:

- The progress summary prints package counts, extraction task counts, candidate draft slot counts, backlog counts, risk-boundary counts, overlap warning counts, and next manual action ids.
- With the current 016 package data, the summary includes `extraction_task_count=2`, `candidate_draft_slot_count=2`, three prerequisite backlog records, `overlap_warning_count=2`, and next manual action ids for the two planned tasks plus the two planned prerequisite backlog records.
- The quality check prints `[]`.

Run focused extraction queue intake tests:

```powershell
uv run --with pytest python -m pytest tests/unit/test_extraction_queue_intake.py
```

Run boundary regression tests after changing package links:

```powershell
uv run --with pytest python -m pytest tests/unit/test_extraction_queue_intake.py tests/unit/test_materials_audit.py tests/unit/test_source_library.py tests/unit/test_source_intake.py tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py
```

Run all tests:

```powershell
uv run --with pytest python -m pytest
```

## Manual Review Checklist

- Every extraction task traces to a valid 015 queue item and audit record.
- Extraction tasks include source-library relationship when available, target rule family or gap, locator requirement, source-quality note, rights note, risk boundary, and pre-extraction checks.
- Candidate draft slots contain no copied source passage, no extracted meaning, no review decision, no approval status, and no promotion status.
- Registration, preparation, locator-review, risk-review, deferred, and blocked items are preserved as prerequisite backlog records when present in a package snapshot.
- Sensitive and high-risk work is labeled before manual extraction.
- Duplicate or overlap warnings are visible before reviewers create new 013 candidates.
- Raw files and external preparation folders remain untouched.
- Package records, extraction tasks, draft slots, and backlog records do not count as formal report-usable evidence.

## Done Criteria

- Maintainers can identify the next extraction tasks and prerequisite backlogs within 5 minutes.
- Package metadata can be validated deterministically without network access.
- No raw source files or external preparation folders are mutated.
- No extraction package, task, draft slot, or backlog item is counted as formal evidence.
- Full test suite passes.
