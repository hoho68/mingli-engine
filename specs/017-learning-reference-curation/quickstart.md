# Quickstart: Learning Reference Curation

## Goal

Use 017 to turn the current 016 extraction queue intake package into learning reference notes, candidate-intake decisions, and prerequisite action notes. The workflow helps maintainers move quickly from newly organized source materials to reviewable project knowledge without crossing candidate or formal-evidence boundaries.

## Current Boundary

- Root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials.
- Do not move, delete, rename, convert, commit, or mutate those materials unless the user explicitly asks.
- 016 extraction tasks and backlog records are planning metadata.
- 017 learning reference notes and candidate-intake decisions are study/reference metadata until an explicit candidate-application step is selected.
- 013 candidate extracts still require review decisions and promotion batches.
- Reports may use only approved and promoted formal evidence units from the reviewed corpus.

## Maintainer Workflow

1. Load the current 016 package summary.
2. Create learning reference notes for the selected ready extraction tasks.
3. Add concise learning points with source trace, locator requirement, rule family, risk tier, and limitations.
4. Check each learning point against existing 013 candidates before creating new candidates.
5. Record candidate-intake decisions: create, reuse, avoid duplicate, defer, or manual review.
6. Preserve registration, preparation, locator-review, risk-review, deferred, and blocked backlog records as prerequisite action notes.
7. Validate high-risk language, copied-passage boundaries, duplicate warnings, and report-evidence boundaries.
8. Use the progress summary to decide the next candidate-intake or prerequisite action.

## Expected Validation Commands

Run the learning reference quality check after implementation:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.learning_reference_curation import build_learning_reference_progress_summary, validate_learning_reference_quality; print(build_learning_reference_progress_summary()); print(validate_learning_reference_quality())"
```

Expected result after implementation:

- The progress summary prints:
  `note_counts={'draft': 7, 'candidate_intake_started': 7}`,
  `learning_point_counts={'duplicate_review': 1, 'ready': 27, 'deferred': 6}`,
  `decision_counts={'reuse_existing': 1, 'create_candidate': 27, 'status:applied': 28}`,
  `prerequisite_action_counts={'risk_review': 3, 'blocked': 1, 'deferred': 2, 'status:planned': 3, 'status:blocked': 1, 'status:deferred': 2}`,
  `risk_tier_counts={'sensitive': 40, 'ordinary': 11, 'high_risk': 3}`,
  `overlap_warning_count=7`,
  `candidate_ready_count=27`,
  `candidate_decision_count=28`,
  `formal_evidence_delta=0`, and next action ids for seven draft notes plus
  three planned risk-review prerequisite actions.
- The quality check prints `[]`.
- Blocked and deferred prerequisite actions remain outside `next_action_ids`
  until their status changes.
- Candidate-intake decisions are applied: one decision reuses an existing
  candidate, and 27 create-candidate decisions have been applied through 013
  intake. The 017 metadata itself still has `formal_evidence_delta=0`; formal
  report evidence comes only from reviewed evidence units.

Run focused learning reference curation tests:

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py
```

Run boundary regression tests after changing learning references or candidate decisions:

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py tests/unit/test_extraction_queue_intake.py tests/unit/test_source_intake.py tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py
```

Run all tests:

```powershell
uv run --with pytest python -m pytest
```

## Manual Review Checklist

- Every learning reference note traces to a valid 016 extraction task.
- Every learning point has source trace, locator requirement or locator, rule family, risk tier, and limitations.
- Candidate-intake decisions check existing 013 overlaps before creating candidates.
- Prerequisite action notes preserve registration, preparation, locator-review, risk-review, deferred, and blocked backlog records without creating candidates.
- Sensitive/high-risk wording includes uncertainty and limitation boundaries.
- No learning reference metadata counts as formal report evidence.

## Done Criteria

- Maintainers can identify first-batch learning notes and candidate decisions within 5 minutes.
- Learning reference metadata validates deterministically without network access.
- No external raw source files or preparation folders are mutated.
- No learning reference note, learning point, candidate decision, or prerequisite action note is counted as formal evidence.
- Full test suite passes.
