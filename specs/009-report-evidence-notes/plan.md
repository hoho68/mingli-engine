# Implementation Plan: 报告证据说明层

**Branch**: `009-report-evidence-notes` | **Date**: 2026-05-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-report-evidence-notes/spec.md`

## Summary

Add a reader-facing `观察依据` section to every safe formal Markdown report. The section will explain, in plain language, how existing report observations relate to chart source assumptions, four pillars, five-element signals, ten-god relationship signals, and action-reflection boundaries. The implementation will extend the existing report schema and Markdown renderer, then update report and regression tests. It will not add new CLI behavior, input shapes, calculations, interpretation conclusions, snapshots, or export formats.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules plus `lunar-python==1.4.8`; no new runtime dependency

**Storage**: No persistent storage; generated reports remain stdout/file content from existing CLI paths

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI/library package generating JSON and Markdown reports

**Project Type**: Python CLI/library

**Performance Goals**: Evidence-note generation is static string assembly and should not add noticeable runtime to report generation

**Constraints**: Preserve existing CLI commands and flags, input JSON shapes, chart calculations, safety JSON behavior, four-layer report order, regression manifest semantics, and prohibition against full Markdown snapshots

**Scale/Scope**: One new report field, one Markdown subsection, focused test updates, and regression coverage for the existing safe automatic and external verified report examples

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Cultural tool, not fate verdict: PASS. The feature explains observation basis and must not add fate verdicts, auspiciousness claims, or deterministic language.
- Transparent calculation boundary: PASS. The new section explicitly points readers back to source assumptions, four pillars, element signals, and ten-god signals.
- Ethical red lines: PASS. Red-line requests continue to return safety JSON and do not receive a formal report or evidence section.
- Reviewable reports: PASS. The feature exists to improve traceability from report prose back to existing chart and interpretation inputs.
- Test-first quality gates: PASS. Tasks must add failing tests before extending the report model and renderer.
- Privacy: PASS. The feature derives text from existing in-memory report objects and stores no personal birth data.

## Project Structure

### Documentation (this feature)

```text
specs/009-report-evidence-notes/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- report-evidence-notes-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- models.py          # add evidence_notes to Report
|-- report_schema.py   # build evidence-note text from existing report/chart signals
`-- markdown.py        # render ### 观察依据 inside 第二层：结构观察

tests/
|-- unit/
|   |-- test_report_schema.py      # report field and content coverage
|   `-- test_markdown_renderer.py  # placement/order coverage
|-- integration/
|   `-- test_report_regression_cases.py # safe manifest cases guard the new section
`-- safety/
    `-- test_red_lines_and_language.py  # existing red-line and absolute-language coverage

examples/
`-- report-regression-cases.json   # unchanged manifest, reused for evidence coverage
```

**Structure Decision**: Keep 009 as a report-schema and renderer feature. The evidence section belongs in the `Report` object because safety review and renderers should see the same formal report content. The Markdown renderer owns only placement and headings. Regression tests should protect durable phrases and section order, not a full Markdown snapshot.

## Complexity Tracking

No constitution violations.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Add a dedicated `Report.evidence_notes` field instead of folding the text into an existing section.
- Place `### 观察依据` after `### 十神摘要` and before `### 结构分析`.
- Use concise static reader-facing bullets derived from existing concepts.
- Extend existing unit and regression tests instead of adding snapshot fixtures.
- Keep red-line behavior unchanged.

## Phase 1: Design Summary

The feature defines a small report entity extension and one Markdown contract:

- [data-model.md](data-model.md)
- [contracts/report-evidence-notes-contract.md](contracts/report-evidence-notes-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Cultural tool, not fate verdict: PASS. The contract forbids new fate verdicts and absolute destiny language.
- Transparent calculation boundary: PASS. Evidence notes explicitly describe source assumptions and structure signals.
- Ethical red lines: PASS. Safety JSON behavior remains first-class and is verified through existing safety and regression tests.
- Reviewable reports: PASS. The report gains a dedicated reader-facing traceability section.
- Test-first quality gates: PASS. The design requires failing tests before model and renderer changes.
- Privacy: PASS. No new data storage or user-identifying sample data is introduced.
