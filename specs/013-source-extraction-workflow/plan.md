# Implementation Plan: Source Extraction Workflow

**Branch**: `013-source-extraction-workflow` | **Date**: 2026-05-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/013-source-extraction-workflow/spec.md`

## Summary

Create an audit-first intake workflow for user-provided classical source materials. The implementation will register source materials as external preparation inputs, capture candidate extracts in a review queue, require explicit human review decisions, and only allow approved candidates to become formal evidence additions compatible with the 012 classical evidence corpus.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules, Python standard-library `json`, `pathlib`, `dataclasses`, `datetime`, and `collections`; no new runtime dependency is planned.

**Storage**: Project-local JSON files for source-material registry, candidate extracts, review decisions, promotion batches, and progress summaries. Root PDF files and root `Markdown/` remain external preparation materials unless the user explicitly asks to track, move, convert, or delete them.

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI/library package on Windows first, portable to macOS/Linux

**Project Type**: Python CLI/library

**Performance Goals**: Loading intake metadata and building a progress summary for the initial corpus should add no more than 300 ms to a validation run and should be deterministic without network access.

**Constraints**: No runtime PDF parsing, no automatic approval, no wholesale source copying, no unapproved candidate evidence in reports, no mutation of user-provided root PDF files or root `Markdown/`, no personal birth-data retention, no exact death/lifespan output, and no medical/legal/psychological/investment instruction.

**Scale/Scope**: Initial workflow for the current nine classical source materials plus future local materials, with dozens to low hundreds of candidate extracts per batch.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Evidence-based traditional analysis: PASS. 013 does not create report judgments directly; it creates a reviewed path before evidence can support traditional conclusions.
- Transparent calculation and evidence boundary: PASS. Candidate extracts remain outside the formal report-usable evidence boundary until approval and promotion.
- Expanded high-risk boundaries: PASS. High-risk candidates require uncertainty and limitation notes before approval; prohibited advice and exact outcome claims remain blocked.
- Reviewable classical evidence: PASS. The workflow requires source material, locator, reviewer decision, rationale, and promotion batch traceability.
- Test-first quality gates: PASS. Tasks must add tests for required fields, state transitions, high-risk limitations, duplicate/conflict links, and exclusion of unapproved candidates.
- Privacy: PASS. The feature stores source-review metadata only and does not store personal birth data or generated user reports.

## Project Structure

### Documentation (this feature)

```text
specs/013-source-extraction-workflow/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- source-extraction-workflow-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- models.py                       # add source intake and candidate review models
|-- classical_sources.py            # keep formal evidence loading boundary stable
|-- evidence_curation.py            # integrate approved-candidate/promotion readiness checks if needed
|-- source_intake.py                # new deterministic loader/validator/progress reporter for 013
`-- data/
    |-- classical_sources/
    |   |-- sources.json
    |   |-- evidence_units.json
    |   |-- curation_batches.json
    |   `-- source_conflicts.json
    `-- source_intake/
        |-- source_materials.json
        |-- candidate_extracts.json
        |-- review_decisions.json
        `-- promotion_batches.json

docs/classical_sources/
|-- README.md
|-- coverage.md
|-- intake.md                       # maintainer-facing source intake progress notes
`-- extracts/

tests/
|-- unit/
|   |-- test_source_intake.py
|   |-- test_classical_sources.py
|   `-- test_evidence_curation.py
|-- integration/
|   `-- test_report_regression_cases.py
`-- safety/
    `-- test_expanded_high_risk_language.py
```

**Structure Decision**: Keep 013 inside the existing Python package and data-file style established by 011 and 012. A new `source_intake.py` owns candidate queue loading, validation, duplicate detection, review-state transitions, and progress reporting so raw intake metadata cannot blur into formal report evidence loading.

## Complexity Tracking

No constitution violations. The plan intentionally avoids a database, runtime document conversion, and automatic approval so the workflow stays auditable and small enough for local review.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Store source intake metadata in project-local JSON rather than tracking or rewriting user-provided source files.
- Model candidate extracts separately from formal evidence units.
- Require explicit review decisions and promotion batches before formal evidence updates.
- Represent rejected and blocked candidates as durable audit records.
- Keep duplicate/conflict/gap links explicit instead of silently merging candidate material.
- Build progress summaries from intake data rather than maintaining manual counts.

## Phase 1: Design Summary

The feature defines an intake data model, review contract, and maintainer workflow:

- [data-model.md](data-model.md)
- [contracts/source-extraction-workflow-contract.md](contracts/source-extraction-workflow-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Evidence-based traditional analysis: PASS. Only approved and promoted candidates can become formal evidence; pending intake records cannot support report conclusions.
- Transparent calculation and evidence boundary: PASS. Source material, candidate extract, review decision, and promoted evidence remain distinct states.
- Expanded high-risk boundaries: PASS. High-risk candidate approval requires limitation notes and exact/professional-advice refusals.
- Reviewable classical evidence: PASS. Every approved addition must trace to source material, locator, review decision, and promotion batch.
- Test-first quality gates: PASS. Planned tests cover validation failures, state transitions, high-risk limitations, duplicate/conflict/gap links, progress summaries, and report boundary preservation.
- Privacy: PASS. No personal birth data or generated reports are retained by the intake workflow.
