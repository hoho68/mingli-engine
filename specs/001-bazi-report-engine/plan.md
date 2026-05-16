# Implementation Plan: 八字知识与报告引擎 MVP

**Branch**: `001-bazi-report-engine` | **Date**: 2026-05-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-bazi-report-engine/spec.md`

## Summary

Build a local-first 八字 knowledge and report engine that validates birth-profile completeness, accepts verified chart data, generates a structured Markdown report, and blocks unsafe or deterministic outputs. The MVP will be a small Python library with a JSON-based CLI contract so the engine can be tested without a Web UI and later reused by a frontend or automated chart-calculation layer.

## Technical Context

**Language/Version**: Python 3.12+; local verification uses Python 3.13.13

**Primary Dependencies**: Python standard library for MVP; pytest for tests

**Storage**: No persistent storage in MVP. Inputs and outputs are file/stdin based; identifiable birth data is not retained by default.

**Testing**: pytest with unit, contract, integration, and safety tests

**Target Platform**: Local developer environment and command-line execution on Windows first, portable to macOS/Linux

**Project Type**: Single Python package with library modules and a small CLI wrapper

**Performance Goals**: Generate a complete Markdown report from validated chart data in under 2 seconds on a local machine; validate missing input and red-line requests instantly from a user's perspective.

**Constraints**: No Web UI, accounts, payments, HTML export, PNG export, PDF export, 紫微斗数, or 六爻 in MVP. Calculation facts, interpretation findings, and report prose remain separate. Full reports require complete birth profile or verified chart data.

**Scale/Scope**: One report at a time for MVP. Designed for later sample-library regression testing and frontend reuse.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Cultural tool, not fate verdict: PASS. Report contract requires cultural/self-reflection framing and blocks absolute destiny language.
- Transparent calculation boundary: PASS. `ChartSource` records whether chart data is supplied, externally verified, or future-calculated, plus calendar and true-solar-time assumptions.
- Ethical red lines: PASS. Safety review has explicit red-line categories and redirect behavior.
- Reviewable reports: PASS. `InterpretationFinding` requires supporting refs, uncertainty level, and safe-language rendering.
- Test-first quality gates: PASS. The plan requires tests for validation, schema transformations, red-line refusals, disclaimer presence, and absolute-language filtering.
- Privacy: PASS. No persistent storage in MVP; sample cases must be anonymized.

## Phase 0 Research Summary

See [research.md](./research.md) for decisions and alternatives.

Key decisions:

- Use a Python library plus JSON CLI contract for the MVP.
- Keep automatic calendrical calculation out of scope; accept verified chart data through a transparent `ChartSource`.
- Use Markdown as the first report format.
- Model ethical screening as a first-class safety review rather than report afterthought.

## Phase 1 Design Summary

See [data-model.md](./data-model.md), [contracts/cli-json-contract.md](./contracts/cli-json-contract.md), and [quickstart.md](./quickstart.md).

The design separates:

- intake validation: `BirthProfile`
- chart provenance: `ChartSource`
- structured chart facts: `BaziChart`
- traceable conclusions: `InterpretationFinding`
- safety review: `SafetyReviewResult`
- final artifact: `Report`

## Project Structure

### Documentation (this feature)

```text
specs/001-bazi-report-engine/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- cli-json-contract.md
`-- checklists/
    `-- requirements.md
```

### Source Code (repository root)

```text
pyproject.toml
src/
`-- mingli_engine/
    |-- __init__.py
    |-- cli.py
    |-- models.py
    |-- validation.py
    |-- safety.py
    |-- report_schema.py
    `-- markdown.py

tests/
|-- contract/
|   `-- test_cli_json_contract.py
|-- integration/
|   `-- test_generate_markdown_report.py
|-- safety/
|   `-- test_red_lines_and_language.py
`-- unit/
    |-- test_birth_profile_validation.py
    |-- test_report_schema.py
    `-- test_markdown_renderer.py
```

**Structure Decision**: Use one small Python package. `models.py` owns data shapes, `validation.py` owns intake completeness, `safety.py` owns ethical screening and language checks, `report_schema.py` assembles report sections, `markdown.py` renders Markdown, and `cli.py` exposes the JSON contract for manual use and contract tests.

## Complexity Tracking

No constitution violations. No additional complexity exceptions.

## Post-Design Constitution Check

- Cultural tool, not fate verdict: PASS. Contracts and data model include disclaimer and prohibited-language review.
- Transparent calculation boundary: PASS. The data model records chart source and assumptions before report generation.
- Ethical red lines: PASS. Safety review blocks or redirects prohibited request categories before final report delivery.
- Reviewable reports: PASS. Findings require supporting refs and uncertainty level.
- Test-first quality gates: PASS. Quickstart and implementation plan require tests before code.
- Privacy: PASS. No storage path exists in MVP; future retention requires a new spec.
