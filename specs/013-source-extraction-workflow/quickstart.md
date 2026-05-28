# Quickstart: Source Extraction Workflow

## Goal

Use 013 to manage source material intake safely before anything becomes formal report evidence.

## Current Boundary

- Root PDF files and root `Markdown/` are external preparation material.
- Do not move, delete, convert, or commit those materials unless the user explicitly asks.
- Candidate extracts are not formal evidence.
- Reports may use only approved and promoted evidence units from the 012 corpus.

## Reviewer Workflow

1. Register source materials with stable `material_id` values and `tracking_status=external_untracked` when the source file remains outside tracked project data.
2. Add candidate extracts with source locator, extracted meaning, proposed rule family, risk tier, limitations, and pending review status.
3. Review candidates one by one.
4. Approve only candidates with reviewable locator, concise meaning, source quality, confidence, limitations, and no unresolved blocking issue.
5. Return candidates that need better locator, safer language, clearer rule family, or duplicate/conflict handling.
6. Reject or block candidates that are unsafe, source-poor, rights-sensitive, too copied, or not convertible into evidence.
7. Place approved candidates into a promotion batch before updating the formal evidence corpus.
8. Re-run intake validation and report regression tests before implementation completion.

## Expected Validation Commands

Run all tests:

```powershell
uv run --with pytest python -m pytest
```

Run focused intake tests after implementation:

```powershell
uv run --with pytest python -m pytest tests/unit/test_source_intake.py
```

Run report boundary regression tests:

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py
```

Run the source-intake quality check from the local package:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import build_intake_progress_report, validate_intake_quality; r=build_intake_progress_report(); print(r); print(validate_intake_quality())"
```

## Expected Intake Snapshot

After the 013 implementation, the current source-intake data computes to:

- Source material preparation: `partially_reviewed=7`, `indexed=1`, `not_started=1`.
- Candidate status: `pending_review=1`, `returned=1`, `approved=1`, `rejected=2`, `blocked=1`.
- Risk tiers: `sensitive=3`, `high_risk=2`, `ordinary=1`.
- Rule families: `blind_image_method=4`, `high_risk_signal=1`, `pattern_strength=1`.
- Approval readiness: `approved_not_promoted=0`.
- Audit links: `duplicate_candidates=1`, `conflict_link_count=1`, `gap_link_count=1`.
- `validate_intake_quality()` returns an empty list for the checked-in intake data.

## Manual Review Checklist

- Source materials are registered without tracking raw root files.
- Pending candidates include source material, locator, extracted meaning, proposed rule family, risk tier, and status.
- High-risk candidates include uncertainty and limitation notes.
- Rejected and blocked candidates preserve reasons.
- Approved candidates have reviewer, review date, rationale, source quality, confidence, and approval limitations.
- Promotion batches include only approved candidates.
- Formal report generation ignores unapproved candidates.

## Done Criteria

- Intake data validates deterministically without network access.
- Progress summary separates material coverage, candidate status, approval readiness, risk distribution, rule families, conflicts, and gaps.
- No unapproved candidate can be loaded as report-usable evidence.
- Full test suite passes.
