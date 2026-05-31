# Implementation Plan: Existing Materials Audit and Preparation

**Branch**: `015-existing-materials-audit` | **Date**: 2026-05-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/015-existing-materials-audit/spec.md`

## Summary

Create an existing-materials audit layer that inventories current root PDFs, prepared Markdown batches, cleaned Markdown variants, maintainer notes, processing-status notes, and knowledge-skeleton artifacts before the next extraction cycle. The implementation will store only audit metadata in project data, align material groups with 014 source-library entries, classify preparation and extraction readiness, label high-risk boundaries, and produce a small next-action queue. It will not mutate raw files, perform automatic extraction, approve evidence, or count prepared text as report-usable evidence.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules plus Python standard-library `json`, `pathlib`, `dataclasses`, `datetime`, `collections`, and `csv`; no new runtime dependency is planned.

**Storage**: Project-local JSON files for material audit records, source alignment findings, preparation readiness findings, extraction queue items, and audit progress snapshots. Existing root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials unless the user explicitly asks to track, move, convert, or delete them.

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI/library package on Windows first, portable to macOS/Linux for project-tracked data validation

**Project Type**: Python CLI/library

**Performance Goals**: Loading tracked audit metadata and computing an audit progress summary should complete in under 300 ms for the current tracked data set. Optional filesystem discovery helpers should scan the current local material roots deterministically without network access and without opening large binary contents.

**Constraints**: No runtime PDF parsing, no OCR, no automatic extraction, no automatic evidence approval, no mutation of root source files or external preparation folders, no wholesale copied passages, no prepared text counted as formal evidence, no personal birth-data retention, no exact death/lifespan output, and no medical/legal/psychological/investment instruction.

**Scale/Scope**: Audit metadata for the existing nine root PDFs, Markdown batches 001-005, current `资料整理/` notes, and future local material groups; expected scale is dozens to low hundreds of audited material groups and queue items.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Evidence-based traditional analysis: PASS. 015 creates audit and preparation metadata only; it does not create formal traditional judgments or report conclusions.
- Transparent calculation and evidence boundary: PASS. The feature separates raw files, prepared text, cleaned text, notes, source-library entries, candidate extracts, promoted evidence, and report-usable evidence.
- Expanded high-risk boundaries: PASS. High-risk material is labeled before extraction and remains preparation-only until later candidate review and formal evidence promotion.
- Reviewable classical evidence: PASS. Material groups can be traced to source-library entries, readiness findings, and future candidate queue items without treating audit records as evidence cards.
- Test-first quality gates: PASS. Tasks must cover audit validation, source-library alignment, readiness classification, high-risk labeling, file-mutation boundary preservation, and report-boundary exclusion.
- Privacy: PASS. The feature stores source-preparation metadata only and does not store personal birth data or generated reports.

## Project Structure

### Documentation (this feature)

```text
specs/015-existing-materials-audit/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- existing-materials-audit-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- models.py                       # add material audit, alignment, readiness, queue, and progress models
|-- materials_audit.py              # new deterministic loader/validator/progress reporter for 015
|-- source_library.py               # existing 014 source-library alignment inputs
|-- source_intake.py                # existing 013 candidate extraction boundary
`-- data/
    |-- materials_audit/
    |   |-- material_audit_records.json
    |   |-- source_alignment_findings.json
    |   |-- preparation_readiness_findings.json
    |   `-- extraction_queue_items.json
    |-- source_library/
    |   |-- source_library_entries.json
    |   |-- source_priority_assessments.json
    |   `-- curation_batch_plans.json
    `-- source_intake/
        |-- source_materials.json
        |-- candidate_extracts.json
        |-- review_decisions.json
        `-- promotion_batches.json

docs/classical_sources/
|-- README.md
|-- source_library.md
|-- intake.md
`-- materials_audit.md             # maintainer-facing existing-materials audit and next-action queue notes

tests/
|-- unit/
|   |-- test_materials_audit.py
|   |-- test_source_library.py
|   `-- test_source_intake.py
|-- integration/
|   `-- test_report_regression_cases.py
`-- safety/
    `-- test_expanded_high_risk_language.py
```

**Structure Decision**: Keep 015 in the same Python package and JSON-data style as 011-014. A new `materials_audit.py` module owns material grouping, source-library alignment, readiness validation, and next-action queue computation so local preparation records cannot blur into 013 candidate extracts or 012 formal evidence.

## Complexity Tracking

No constitution violations. The plan intentionally avoids a database, file conversion, OCR, runtime PDF parsing, and automatic evidence extraction. The simplest compliant approach is deterministic metadata validation over project-tracked JSON plus optional read-only discovery helpers for local material roots.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Store audit metadata in project-local JSON rather than tracking external raw material files.
- Model material groups separately from 013 source materials and 014 source-library entries.
- Use explicit source-alignment findings instead of automatic fuzzy merges.
- Separate text preparation readiness from extraction readiness and formal evidence readiness.
- Treat high-risk discovery as a pre-extraction safety gate.
- Produce two next-work lists: extraction-ready queue and preparation backlog.
- Keep filesystem discovery read-only and metadata-only.

## Phase 1: Design Summary

The feature defines an audit data model, maintainer-facing contract, and quickstart workflow:

- [data-model.md](data-model.md)
- [contracts/existing-materials-audit-contract.md](contracts/existing-materials-audit-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Evidence-based traditional analysis: PASS. Audit records, readiness findings, and queue items are not evidence and cannot support report conclusions directly.
- Transparent calculation and evidence boundary: PASS. The data model explicitly separates material representations, audit records, source-library alignment, readiness findings, queue items, candidate extracts, promotion batches, and formal evidence.
- Expanded high-risk boundaries: PASS. Sensitive and high-risk materials require boundary notes before entering the extraction-ready queue.
- Reviewable classical evidence: PASS. Every queue item traces back to a material audit record and, when possible, a source-library entry; missing links are visible as registration or clarification tasks.
- Test-first quality gates: PASS. Planned tests cover validation failures, duplicate/variant handling, source-library alignment, high-risk labels, next-action queues, and report-boundary preservation.
- Privacy: PASS. No personal birth data or generated reports are retained by the materials audit workflow.
