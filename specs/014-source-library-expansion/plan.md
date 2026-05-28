# Implementation Plan: Source Library Expansion and Evidence Factory

**Branch**: `014-source-library-expansion` | **Date**: 2026-05-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/014-source-library-expansion/spec.md`

## Summary

Create a source-library planning layer around the existing 013 source-intake workflow so future classical materials can be registered, prioritized, grouped into extraction batches, and measured for evidence value. The implementation will keep root PDF files and root `Markdown/` as external preparation materials, store only review metadata in project data, and compute source/batch value from downstream candidate-review and formal-evidence outcomes.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules, Python standard-library `json`, `pathlib`, `dataclasses`, `datetime`, and `collections`; no new runtime dependency is planned.

**Storage**: Project-local JSON files for source-library entries, priority assessments, and curation batch plans. Source value summaries are computed from source-library data, 013 source-intake data, and formal evidence metadata. Root PDF files and root `Markdown/` remain external preparation materials unless the user explicitly asks to track, move, convert, or delete them.

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI/library package on Windows first, portable to macOS/Linux

**Project Type**: Python CLI/library

**Performance Goals**: Loading source-library metadata and computing a progress/value summary for the initial corpus should add no more than 300 ms to a validation run and should be deterministic without network access.

**Constraints**: No runtime PDF parsing, no automatic extraction, no automatic evidence approval, no mutation of user-provided root PDF files or root `Markdown/`, no wholesale source copying, no registered source or planned batch counted as report-usable evidence, no personal birth-data retention, no exact death/lifespan output, and no medical/legal/psychological/investment instruction.

**Scale/Scope**: Source-library planning for the current nine classical source materials plus future local materials, with dozens of registered sources and dozens to low hundreds of candidate extracts per review cycle.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Evidence-based traditional analysis: PASS. 014 does not create report judgments directly; it tracks source planning and value before material can support formal traditional conclusions.
- Transparent calculation and evidence boundary: PASS. Registered sources, planned batches, candidate extracts, promoted evidence, and report-usable evidence remain separate trust levels.
- Expanded high-risk boundaries: PASS. High-risk materials and planned batches must be labeled before extraction and still require 013 review limitations before evidence use.
- Reviewable classical evidence: PASS. Source-library entries record identity, readiness, priority, risk, and next actions, then link to candidate-review and promotion outcomes when they exist.
- Test-first quality gates: PASS. Tasks must add tests for source metadata validation, priority/batch validation, value-summary computation, high-risk labeling, and report boundary preservation.
- Privacy: PASS. The feature stores source-review metadata only and does not store personal birth data or generated user reports.

## Project Structure

### Documentation (this feature)

```text
specs/014-source-library-expansion/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- source-library-expansion-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- models.py                       # add source library, priority, batch plan, and value summary models
|-- source_intake.py                # keep candidate review and promotion boundary stable
|-- source_library.py               # new deterministic loader/validator/progress/value reporter for 014
|-- classical_sources.py            # read formal evidence and coverage outcomes for value summaries
`-- data/
    |-- classical_sources/
    |   |-- sources.json
    |   |-- evidence_units.json
    |   |-- curation_batches.json
    |   `-- source_conflicts.json
    |-- source_intake/
    |   |-- source_materials.json
    |   |-- candidate_extracts.json
    |   |-- review_decisions.json
    |   `-- promotion_batches.json
    `-- source_library/
        |-- source_library_entries.json
        |-- source_priority_assessments.json
        `-- curation_batch_plans.json

docs/classical_sources/
|-- README.md
|-- coverage.md
|-- intake.md
`-- source_library.md              # maintainer-facing source library and next-batch notes

tests/
|-- unit/
|   |-- test_source_library.py
|   |-- test_source_intake.py
|   `-- test_classical_sources.py
|-- integration/
|   `-- test_report_regression_cases.py
`-- safety/
    `-- test_expanded_high_risk_language.py
```

**Structure Decision**: Keep 014 in the existing Python package and JSON data style established by 011-013. A new `source_library.py` owns source registration, priority/batch validation, next-source selection, and value-summary computation so planning metadata cannot blur into the 013 candidate-review queue or the 012 formal evidence corpus.

## Complexity Tracking

No constitution violations. The plan intentionally avoids a database, runtime document conversion, automatic extraction, and automatic approval so the workflow stays local, auditable, and small enough for staged review.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Store source-library metadata in project-local JSON rather than tracking or rewriting user-provided source files.
- Keep source-library planning separate from 013 candidate extracts and 012 formal evidence.
- Use explicit maintainer priority assessments instead of opaque automatic scoring.
- Model curation batch plans separately from promotion batches.
- Compute source and batch value summaries from downstream review and promotion outcomes.
- Preserve duplicate, deferred, exhausted, and blocked source outcomes as auditable records.
- Require high-risk labels before extraction planning.

## Phase 1: Design Summary

The feature defines a source-library data model, maintainer contract, and quickstart workflow:

- [data-model.md](data-model.md)
- [contracts/source-library-expansion-contract.md](contracts/source-library-expansion-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Evidence-based traditional analysis: PASS. Source-library records and batch plans are not evidence; they only guide what may later enter the reviewed evidence path.
- Transparent calculation and evidence boundary: PASS. The data model separates source entries, priority assessments, batch plans, candidate extracts, review decisions, promotion outcomes, and formal evidence.
- Expanded high-risk boundaries: PASS. High-risk source entries and batches require risk notes and stricter review boundaries before extraction.
- Reviewable classical evidence: PASS. Every source can be traced from registration to priority decision, batch plan, candidate outcomes, and promoted evidence when those downstream records exist.
- Test-first quality gates: PASS. Planned tests cover validation failures, next-source selection, source value summaries, high-risk labels, non-useful source preservation, and report boundary preservation.
- Privacy: PASS. No personal birth data or generated reports are retained by the source-library workflow.
