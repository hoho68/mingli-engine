# Implementation Plan: Extraction Queue Intake Package

**Branch**: `016-extraction-queue-intake` | **Date**: 2026-05-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/016-extraction-queue-intake/spec.md`

## Summary

Create a planning handoff layer that converts the 015 materials-audit next-action queue into a bounded extraction work package for the next 013 candidate-intake cycle. The implementation will store only package metadata, extraction task records, candidate draft slots, prerequisite backlog records, and progress summaries. It will preserve traceability to 015 audit records, 015 queue items, 014 source-library entries, and intended 013 source-intake destinations without reading raw files, creating candidate extracts, approving evidence, or changing formal report evidence counts.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules plus Python standard-library `json`, `pathlib`, `dataclasses`, `datetime`, and `collections`; no new runtime dependency is planned.

**Storage**: Project-local JSON files for extraction work packages, extraction tasks, candidate draft slots, prerequisite backlog records, and package progress metadata. Existing root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials unless the user explicitly asks to track, move, convert, or delete them.

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI/library package on Windows first, portable to macOS/Linux for project-tracked data validation

**Project Type**: Python CLI/library

**Performance Goals**: Loading tracked package metadata and computing an extraction package summary should complete in under 300 ms for the initial package. Validation must be deterministic without network access and without opening large binary contents.

**Constraints**: No runtime PDF parsing, no OCR, no automatic extraction, no automatic candidate creation, no automatic evidence approval, no mutation of root source files or external preparation folders, no wholesale copied passages, no draft slots counted as candidate extracts or formal evidence, no personal birth-data retention, no exact death/lifespan output, and no medical/legal/psychological/investment instruction.

**Scale/Scope**: Initial package generation for the current 015 next five recommended queue items plus prerequisite backlog visibility for useful non-ready items; expected scale is dozens of extraction tasks and draft slots per cycle.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Evidence-based traditional analysis: PASS. 016 creates extraction planning metadata only; it does not create formal traditional judgments or report conclusions.
- Transparent calculation and evidence boundary: PASS. The feature separates 015 queue items, extraction tasks, candidate draft slots, 013 candidate extracts, review decisions, promotion batches, and formal report evidence.
- Expanded high-risk boundaries: PASS. High-risk and sensitive package items require risk-boundary labels and prerequisite routing before manual extraction can begin.
- Reviewable classical evidence: PASS. Every extraction task traces to a 015 queue item and audit record, and when available to 014 source-library and intended 013 source-intake records.
- Test-first quality gates: PASS. Tasks must cover package validation, queue eligibility, draft-slot boundaries, high-risk routing, duplicate/overlap detection, and report-boundary exclusion.
- Privacy: PASS. The feature stores source-preparation metadata only and does not store personal birth data or generated reports.

## Project Structure

### Documentation (this feature)

```text
specs/016-extraction-queue-intake/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- extraction-queue-intake-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- models.py                         # add extraction work package, task, draft slot, backlog, and summary models
|-- extraction_queue_intake.py         # new deterministic loader/validator/progress reporter for 016
|-- materials_audit.py                 # existing 015 queue and readiness source
|-- source_library.py                  # existing 014 source-library alignment inputs
|-- source_intake.py                   # existing 013 candidate extraction boundary
`-- data/
    |-- extraction_queue_intake/
    |   |-- extraction_work_packages.json
    |   |-- extraction_tasks.json
    |   |-- candidate_draft_slots.json
    |   `-- prerequisite_backlog_records.json
    |-- materials_audit/
    |   |-- material_audit_records.json
    |   |-- source_alignment_findings.json
    |   |-- preparation_readiness_findings.json
    |   `-- extraction_queue_items.json
    |-- source_library/
    |   `-- source_library_entries.json
    `-- source_intake/
        |-- source_materials.json
        |-- candidate_extracts.json
        |-- review_decisions.json
        `-- promotion_batches.json

docs/classical_sources/
|-- README.md
|-- source_library.md
|-- intake.md
|-- materials_audit.md
`-- extraction_queue_intake.md       # maintainer-facing 016 package notes

tests/
|-- unit/
|   |-- test_extraction_queue_intake.py
|   |-- test_materials_audit.py
|   |-- test_source_library.py
|   `-- test_source_intake.py
|-- integration/
|   `-- test_report_regression_cases.py
`-- safety/
    `-- test_expanded_high_risk_language.py
```

**Structure Decision**: Keep 016 in the existing Python package and JSON-data style established by 011-015. A new `extraction_queue_intake.py` module owns work-package loading, queue eligibility validation, draft-slot boundary checks, prerequisite backlog routing, duplicate/overlap detection, and package progress summaries so extraction planning metadata cannot blur into 013 candidate extracts or 012 formal evidence.

## Complexity Tracking

No constitution violations. The plan intentionally avoids a database, file conversion, OCR, runtime PDF parsing, automatic extraction, automatic candidate creation, and automatic approval. The simplest compliant approach is deterministic validation over project-tracked JSON linked back to 015/014/013 metadata.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Store 016 package metadata separately from 013 candidate extracts and 015 audit records.
- Treat candidate draft slots as placeholders, not candidate extracts.
- Use 015 queue eligibility plus readiness/alignment cross-checks before creating extraction tasks.
- Preserve prerequisite backlog items instead of silently dropping non-ready queue work.
- Detect duplicate/overlap risks against existing 013 candidate metadata without creating or mutating candidates.
- Keep high-risk material in prerequisite routing until risk review is complete.
- Keep raw-file and report-evidence boundaries unchanged.

## Phase 1: Design Summary

The feature defines an extraction queue intake data model, maintainer-facing contract, and quickstart workflow:

- [data-model.md](data-model.md)
- [contracts/extraction-queue-intake-contract.md](contracts/extraction-queue-intake-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Evidence-based traditional analysis: PASS. Work packages, extraction tasks, and draft slots are not evidence and cannot support report conclusions directly.
- Transparent calculation and evidence boundary: PASS. The data model explicitly separates queue items, extraction tasks, draft slots, prerequisite backlog, 013 candidate extracts, review decisions, promotion batches, and formal evidence.
- Expanded high-risk boundaries: PASS. Sensitive and high-risk queue items require risk routing and cannot become routine extraction tasks without prerequisites.
- Reviewable classical evidence: PASS. Every task and backlog item traces back to an originating queue item and audit record; missing links are visible as validation failures.
- Test-first quality gates: PASS. Planned tests cover validation failures, queue eligibility, draft-slot non-evidence boundaries, high-risk language, duplicate/overlap warnings, and report-boundary preservation.
- Privacy: PASS. No personal birth data or generated reports are retained by the extraction queue intake workflow.
