# Implementation Plan: 报告层间衔接语优化

**Branch**: `007-report-transition-language` | **Date**: 2026-05-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-report-transition-language/spec.md`

## Summary

Add concise transition wording to the existing layered Markdown Bazi report so readers can follow the path from quick guide, to source assumptions, to structure observation, to interpretation boundaries, and finally to action reflection. The implementation keeps chart calculation, CLI commands, input JSON shapes, safety refusal behavior, 004 heading order, 005 reader-facing labels, and 006 structure observation wording unchanged. Transition prose should be prepared in the report assembly layer and verified through unit, integration, renderer, and safety tests.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules plus `lunar-python==1.4.8`; no new runtime dependency

**Storage**: N/A

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI package generating Markdown reports

**Project Type**: Python CLI/library

**Performance Goals**: Report text assembly remains immediate for one in-memory chart/report

**Constraints**: Preserve CLI commands, input JSON shapes, safety refusal exit code and JSON shape, disclaimer, source disclosure, 004 layered heading order, 005 plain-language labels, 006 structure wording, and non-deterministic language

**Scale/Scope**: One Markdown report at a time; no web UI, PDF export, stored report archive, new Bazi algorithm, or new interpretation conclusion

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Cultural tool, not fate verdict: PASS. Transition wording explains reading order and boundaries only; it does not add prediction, fate verdicts, auspiciousness claims, useful-god conclusions, strength conclusions, luck-cycle readings, or event predictions.
- Transparent calculation boundary: PASS. Source, calendar assumptions, timezone/place handling, solar-term handling, and true-solar-time disclosure remain visible. New source-layer transition explicitly frames those values as basis and assumptions, not conclusions.
- Ethical red lines: PASS. Existing red-line refusal behavior remains unchanged for lifespan, death, disaster, deterministic marriage matching, medical/legal/psychological/investment, third-party, anxiety, and paid-remedy requests.
- Reviewable reports: PASS. Transitions are deterministic report text assembled from existing report fields; they do not hide or reinterpret intermediate chart data.
- Test-first quality gates: PASS. Implementation tasks must add failing report schema and integration assertions before wording changes, then run safety and full suite verification.
- Privacy: PASS. No storage, retention, or new personal-data capture is introduced.

## Project Structure

### Documentation (this feature)

```text
specs/007-report-transition-language/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- report-transition-markdown-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- report_schema.py    # primary boundary for quick guide, source, boundary, and action transition wording
|-- markdown.py         # renderer/layout boundary; heading order should remain unchanged
|-- interpretation.py   # existing 006 structure wording boundary; should remain unchanged unless tests prove a tiny bridge belongs there
`-- cli.py              # unchanged command entry points

tests/
|-- unit/
|   |-- test_report_schema.py       # primary tests for assembled transition wording
|   `-- test_markdown_renderer.py   # heading order and final field placement
|-- integration/
|   |-- test_calculate_report_cli.py # automatic chart Markdown output
|   `-- test_generate_markdown_report.py # external chart Markdown output
`-- safety/
    `-- test_red_lines_and_language.py # prohibited phrase and safety JSON behavior
```

**Structure Decision**: Add transition wording in `src/mingli_engine/report_schema.py` because this layer already prepares report fields and safety-reviewed prose. Keep `src/mingli_engine/markdown.py` as a simple layout renderer and avoid adding domain-specific transition logic there. Preserve `src/mingli_engine/interpretation.py` unless implementation discovers a transition must remain adjacent to existing interpretation text.

## Complexity Tracking

No constitution violations.

## Phase 0: Research Summary

The planning decision is to add concise connective prose to existing report fields rather than introduce new sections, new headings, or a narrative renderer. This keeps the 004 report structure stable while improving reading flow.

Research decisions are documented in [research.md](research.md):

- Put transition wording in report assembly.
- Keep Markdown headings and renderer behavior unchanged.
- Keep quick guide concise and avoid increasing bullet count beyond the existing pattern unless tests prove it remains readable.
- Preserve 005 labels and 006 structure observation wording.
- Verify through report schema, Markdown integration, and safety tests.

## Phase 1: Design Summary

The feature defines a Markdown output contract for transition wording in the existing report. The contract requires a reading-path cue in the quick guide, source-as-basis wording in the first layer, clue-not-conclusion wording around structure observation, boundary-to-action wording in the third layer, and reflection-not-promise wording in the action layer.

Design artifacts:

- [data-model.md](data-model.md)
- [contracts/report-transition-markdown-contract.md](contracts/report-transition-markdown-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Cultural tool, not fate verdict: PASS. Transition wording is explicitly limited to reading path, observation, boundary, and reflection.
- Transparent calculation boundary: PASS. First-layer transition reinforces source and assumption transparency.
- Ethical red lines: PASS. Safety JSON, disclaimer, ethics reminder, and prohibited-language checks remain mandatory.
- Reviewable reports: PASS. Transitions are added to existing report fields and remain testable in final Markdown.
- Test-first quality gates: PASS. Plan requires red-green tests before implementation and full verification afterward.
- Privacy: PASS. No new data capture, persistence, or export path.
