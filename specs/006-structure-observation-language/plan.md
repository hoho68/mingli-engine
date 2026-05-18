# Implementation Plan: 第二层结构观察表达优化

**Branch**: `006-structure-observation-language` | **Date**: 2026-05-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-structure-observation-language/spec.md`

## Summary

Optimize only the Markdown report's `第二层：结构观察` wording so five-element counts, ten-god relationships, and basic structure notes read as clear professional Chinese report prose instead of system-like output. Keep existing calculation, CLI commands, input JSON shapes, safety refusal behavior, 004 heading order, and 005 reader-facing labels unchanged. The implementation should make small wording changes at the interpretation text boundary and prove them with unit, integration, and safety tests.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules plus `lunar-python==1.4.8`; no new runtime dependency

**Storage**: N/A

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI package generating Markdown reports

**Project Type**: Python CLI/library

**Performance Goals**: Report wording generation remains immediate for one in-memory chart/report

**Constraints**: Preserve CLI commands, input JSON shapes, safety refusal exit code and JSON shape, disclaimer, source disclosure, 004 layered heading order, 005 plain-language labels, and non-deterministic language

**Scale/Scope**: One Markdown report at a time; no web UI, PDF export, stored report archive, new Bazi algorithm, or new interpretation conclusion

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Cultural tool, not fate verdict: PASS. This feature changes explanatory wording only and explicitly forbids fate verdicts, auspiciousness claims, useful-god conclusions, strength conclusions, luck-cycle readings, and event predictions.
- Transparent calculation boundary: PASS. Existing chart source, calendar assumptions, timezone/place handling, solar-term handling, and true-solar-time disclosure remain in the first layer. Structure wording continues to show counts as observation material.
- Ethical red lines: PASS. Existing red-line refusal behavior remains unchanged, including lifespan, death, disaster, deterministic marriage matching, medical/legal/psychological/investment, third-party, anxiety, and paid-remedy protections.
- Reviewable reports: PASS. The plan preserves the current intermediate `ElementDistribution` and `BasicInterpretationSummary` flow so text can still be traced to counted signals and chart fields.
- Test-first quality gates: PASS. Implementation tasks must update failing unit and integration assertions before changing wording, then run safety and full test checks.
- Privacy: PASS. No storage, retention, or new personal-data capture is introduced.

## Project Structure

### Documentation (this feature)

```text
specs/006-structure-observation-language/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- structure-observation-markdown-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- interpretation.py   # primary wording boundary for five-element, ten-god, and structure observation text
|-- report_schema.py    # unchanged report assembly boundary; should keep 005 reader-facing labels
|-- markdown.py         # unchanged renderer/layout boundary
`-- cli.py              # unchanged command entry points

tests/
|-- unit/
|   |-- test_interpretation.py      # primary tests for structure wording
|   |-- test_report_schema.py       # verify assembled report fields keep smoother structure text and 005 labels
|   `-- test_markdown_renderer.py   # unchanged layered heading contract if needed
|-- integration/
|   |-- test_calculate_report_cli.py # automatic chart Markdown output
|   `-- test_generate_markdown_report.py # external chart Markdown output
`-- safety/
    `-- test_red_lines_and_language.py # prohibited phrase and safety JSON behavior
```

**Structure Decision**: Keep all new wording in `src/mingli_engine/interpretation.py`, because the current system already builds five-element, ten-god, day-master, structure, suggestion, and limitation text there. Do not add renderer-level replacement in `markdown.py`; the renderer should remain responsible for layout only. Do not move 005 label formatting out of `report_schema.py`.

## Complexity Tracking

No constitution violations.

## Phase 0: Research Summary

The planning decision is to make small, explicit wording changes in the interpretation layer rather than introduce a new localization system or post-render string replacement. This keeps the feature narrow, testable, and auditable.

Research decisions are documented in [research.md](research.md):

- Structure-layer prose belongs in `interpretation.py`.
- Five-element counts must remain visible and accurate.
- Ten-god relationships must remain visible but framed as structural clues.
- Unknown or missing signals stay transparent and conservative.
- Tests must cover unit wording, full Markdown output, and safety boundaries.

## Phase 1: Design Summary

The feature defines a report-output contract for the existing Markdown report rather than a new API. The contract requires smoother `第二层：结构观察` prose while preserving counted values, ten-god placement information, heading order, safety disclaimers, and red-line refusal behavior.

Design artifacts:

- [data-model.md](data-model.md)
- [contracts/structure-observation-markdown-contract.md](contracts/structure-observation-markdown-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Cultural tool, not fate verdict: PASS. The contract and data model require observation wording only.
- Transparent calculation boundary: PASS. Counts and source-derived relationships remain visible; first-layer source disclosure remains unchanged.
- Ethical red lines: PASS. Safety JSON and prohibited-language checks remain mandatory.
- Reviewable reports: PASS. Text remains generated from explicit intermediate objects and existing chart fields.
- Test-first quality gates: PASS. The plan calls for failing tests before implementation and full verification afterward.
- Privacy: PASS. No new data collection, storage, or export path.
