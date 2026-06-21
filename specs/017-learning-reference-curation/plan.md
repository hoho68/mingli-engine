# Implementation Plan: Learning Reference Curation

**Branch**: `017-learning-reference-curation` | **Date**: 2026-05-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/017-learning-reference-curation/spec.md`

## Summary

Create a bounded learning-reference curation layer that turns the current 016 extraction queue intake package into maintainer-readable study notes, candidate-intake decisions, and prerequisite action notes. The implementation will use project-tracked metadata only, will not mutate external raw materials, and will keep learning references outside formal evidence until existing 013 review and promotion workflows approve and promote candidate extracts.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules plus Python standard-library `json`, `pathlib`, `dataclasses`, and `collections`; no new runtime dependency is planned.

**Storage**: Project-local JSON files for learning reference notes, learning points, candidate-intake decisions, prerequisite action notes, and progress summaries. Existing documentation files under `docs/classical_sources/` will hold maintainer-facing readable notes. External root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials.

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI/library package on Windows first, portable to macOS/Linux for tracked JSON validation

**Project Type**: Python CLI/library

**Performance Goals**: Loading tracked learning-reference metadata and computing a summary should complete in under 300 ms for the first package. Validation must be deterministic without network access and without opening large binary files.

**Constraints**: No runtime PDF parsing, no OCR, no automatic raw-file conversion, no movement/deletion/rewrite of external preparation materials, no long copied passages, no automatic formal evidence promotion, no personal birth-data retention, no exact death/lifespan claims, and no medical/legal/psychological/investment instruction.

**Scale/Scope**: Initial 017 scope was the current 016 package: two ready extraction tasks, two learning reference notes, several learning points, candidate-intake decisions for those learning points, and prerequisite action notes for current registration, risk-review, and blocked backlog records. The current incremental scope adds the next ordinary ready task, Duan Plain Mingxue Outline, as a third 016/017 learning-reference item without changing formal evidence counts.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Evidence-based traditional analysis: PASS. 017 creates source-backed study metadata and candidate-intake planning only; it does not produce final report judgments.
- Transparent calculation and evidence boundary: PASS. 017 separates learning notes, candidate-intake decisions, 013 candidate extracts, review decisions, promotion batches, and 012 formal evidence.
- Expanded high-risk boundaries: PASS. Sensitive and high-risk learning points require uncertainty, limitations, and refusal-boundary language before candidate intake.
- Reviewable classical evidence: PASS. Every learning reference note traces to 016 task/backlog records plus 015/014/013 ids where available.
- Test-first quality gates: PASS. Tasks will include tests for learning note validation, candidate-intake boundaries, overlap decisions, prerequisite action routing, high-risk wording, and formal-evidence exclusion.
- Privacy: PASS. The feature stores source-preparation metadata only and does not store personal birth data or generated reports.

## Project Structure

### Documentation (this feature)

```text
specs/017-learning-reference-curation/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- learning-reference-curation-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- models.py
|-- learning_reference_curation.py
|-- extraction_queue_intake.py
|-- source_intake.py
|-- source_library.py
|-- materials_audit.py
`-- data/
    |-- learning_reference_curation/
    |   |-- learning_reference_notes.json
    |   |-- learning_points.json
    |   |-- candidate_intake_decisions.json
    |   |-- prerequisite_action_notes.json
    |   `-- .gitkeep
    |-- extraction_queue_intake/
    |-- source_intake/
    |-- source_library/
    |-- materials_audit/
    `-- classical_sources/

docs/classical_sources/
|-- README.md
|-- extraction_queue_intake.md
|-- learning_reference_curation.md
`-- extracts/
    |-- northeast_blind_peak.md
    `-- mingli_true_formula_teacher.md

tests/
|-- unit/
|   `-- test_learning_reference_curation.py
|-- integration/
|   `-- test_report_regression_cases.py
`-- safety/
    `-- test_expanded_high_risk_language.py
```

**Structure Decision**: Keep 017 in the existing Python package and JSON-data style established by 011-016. A new `learning_reference_curation.py` module owns learning-note loading, candidate-intake decision validation, prerequisite-action routing, duplicate/overlap boundaries, and progress summaries so learning references cannot blur into 013 candidate extracts or 012 formal evidence.

## Complexity Tracking

No constitution violations. The plan intentionally avoids automatic PDF parsing, OCR, source conversion, automatic candidate approval, and direct formal evidence promotion. The simplest compliant approach is deterministic validation over project-tracked JSON linked back to 016/015/014/013 metadata.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Store learning references separately from 013 candidates and 012 formal evidence.
- Treat readable learning notes as study metadata, not evidence.
- Create candidate-intake decisions before mutating 013 candidate data.
- Use 016 tasks and backlog records as the first bounded work surface.
- Preserve duplicate/overlap warnings before creating candidates.
- Keep high-risk and blocked materials behind prerequisite action notes.
- Keep raw-file and report-evidence boundaries unchanged.

## Phase 1: Design Summary

The feature defines learning-reference curation entities, contracts, and quickstart workflow:

- [data-model.md](data-model.md)
- [contracts/learning-reference-curation-contract.md](contracts/learning-reference-curation-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Evidence-based traditional analysis: PASS. Learning references remain source-backed study notes and candidate-intake planning metadata.
- Transparent calculation and evidence boundary: PASS. The data model explicitly separates learning notes, learning points, candidate-intake decisions, 013 candidates, review decisions, promotion batches, and formal evidence.
- Expanded high-risk boundaries: PASS. Sensitive/high-risk learning points and backlog action notes require boundaries before candidate intake.
- Reviewable classical evidence: PASS. Every note and decision traces to upstream package/task/backlog/source ids.
- Test-first quality gates: PASS. Planned tests cover validation failures, duplicate/overlap handling, high-risk wording, raw-file non-mutation, and formal-evidence exclusion.
- Privacy: PASS. No personal birth data or generated reports are retained by this workflow.
