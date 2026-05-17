# Implementation Plan: 报告分层阅读体验优化

**Branch**: `004-report-readability` | **Date**: 2026-05-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-report-readability/spec.md`

## Summary

Improve the existing Markdown Bazi report by adding a near-top quick guide and reorganizing detailed content into four reading layers: factual source data, structure observations, interpretation boundaries, and action reflection. The implementation keeps the current CLI commands and interpretation rules unchanged, adds only report-shaping text needed for readability, and preserves all safety gates.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing standard-library dataclasses and project modules; no new runtime dependency

**Storage**: N/A

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI package generating Markdown reports

**Project Type**: Python CLI/library

**Performance Goals**: Report rendering remains immediate for one in-memory `Report`

**Constraints**: Preserve existing CLI commands, input JSON shapes, safety refusal exit codes, disclaimer, source disclosure, and non-deterministic language

**Scale/Scope**: One Markdown report at a time; no web UI, PDF export, account system, or stored report archive

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Cultural tool, not fate verdict: PASS. This feature reorganizes existing conservative content and does not add new predictions or fate claims.
- Transparent calculation boundary: PASS. `第一层：基础资料` keeps chart card and source assumptions visible.
- Ethical red lines: PASS. Existing safety refusal behavior and disclaimer remain mandatory.
- Reviewable reports: PASS. The layered structure makes source, observation, boundary, and reflection easier to trace.
- Test-first quality gates: PASS. Plan includes unit, integration, and safety tests before implementation changes.
- Privacy: PASS. No new storage or retention behavior is introduced.

## Project Structure

### Documentation (this feature)

```text
specs/004-report-readability/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── layered-markdown-contract.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/mingli_engine/
├── models.py          # Report data shape gains quick guide and boundary fields if needed
├── report_schema.py   # prepares quick guide and explicit boundary text
├── markdown.py        # renders layered Markdown structure
└── cli.py             # unchanged command entry points

tests/
├── unit/
│   ├── test_report_schema.py
│   └── test_markdown_renderer.py
├── integration/
│   ├── test_generate_markdown_report.py
│   └── test_calculate_report_cli.py
└── safety/
    └── test_red_lines_and_language.py
```

**Structure Decision**: Keep readability changes inside the existing report assembly and Markdown rendering boundary. Do not create a new report format or new CLI layer.

## Complexity Tracking

No constitution violations.

## Phase 0: Research Summary

The main planning decision is to keep Markdown rendering deterministic and project-local. The quick guide should be prepared in `report_schema.py`, because that layer already has access to chart source, interpretation distribution, limitations, and focus topic. The renderer should remain a simple layout function.

## Phase 1: Design Summary

The feature adds a `Quick Guide` and explicit `Interpretation Boundary` concept to the report data model, then renders the report into recognizable layers. Existing report content is reused rather than replaced. Tests should verify heading order, source visibility, boundary visibility, focus-topic action reflection, unchanged red-line refusal behavior, and absence of prohibited deterministic phrases.

## Post-Design Constitution Check

- Cultural tool, not fate verdict: PASS. Quick guide and action reflection must remain conservative.
- Transparent calculation boundary: PASS. Source disclosure is required under `第一层：基础资料`.
- Ethical red lines: PASS. Refusal paths and disclaimer remain unchanged.
- Reviewable reports: PASS. Layer headings make evidence and boundaries more visible.
- Test-first quality gates: PASS. TDD tasks cover schema, renderer, CLI, and safety paths.
- Privacy: PASS. No new storage or data retention.
