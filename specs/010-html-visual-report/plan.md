# Implementation Plan: HTML 可视化报告

**Branch**: `010-html-visual-report` | **Date**: 2026-05-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/010-html-visual-report/spec.md`

## Summary

Add a pure static HTML output format to the existing safe formal report flow. The implementation will add a dedicated HTML renderer for the current `Report` object, then extend `calculate-report` and `generate-report` so `--format html` returns a complete standalone HTML document for safe inputs. The feature will preserve Markdown output, existing input shapes, chart calculation, safety JSON behavior, and interpretation content.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules plus Python standard library HTML escaping; no new runtime dependency

**Storage**: No persistent storage; HTML is generated to stdout through existing CLI flows

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI/library package generating JSON, Markdown, and static HTML reports

**Project Type**: Python CLI/library

**Performance Goals**: HTML rendering is string assembly over an existing in-memory `Report` and should add no noticeable runtime to report generation

**Constraints**: Preserve existing CLI command names, input JSON shapes, chart calculations, safety JSON exit behavior, Markdown output behavior, report safety boundaries, and no external assets or JavaScript in HTML

**Scale/Scope**: One new renderer module, CLI format choice extension, focused unit/integration/safety tests, and regression coverage for safe automatic and external verified report examples

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Cultural tool, not fate verdict: PASS. HTML is presentation-only and must not add new Bazi judgments, auspiciousness claims, deterministic phrasing, or professional advice.
- Transparent calculation boundary: PASS. HTML renders the same report fields that already expose chart source, calendar assumptions, timezone, solar-term handling, and true solar time status.
- Ethical red lines: PASS. Red-line requests continue returning safety JSON and do not receive a formal HTML report.
- Reviewable reports: PASS. HTML preserves the same report order and keeps `观察依据` visible inside the structure-observation layer.
- Test-first quality gates: PASS. Tasks must add failing renderer, CLI, escaping, and safety tests before implementation.
- Privacy: PASS. HTML is generated from in-memory report objects and introduces no storage or user-identifying sample data.

## Project Structure

### Documentation (this feature)

```text
specs/010-html-visual-report/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- html-report-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- html.py       # new static HTML renderer for Report
|-- cli.py        # accept --format html and dispatch to HTML renderer
|-- markdown.py   # unchanged Markdown renderer remains canonical for Markdown
`-- models.py     # existing Report model, no new fields expected

tests/
|-- unit/
|   `-- test_html_renderer.py             # HTML document, order, escaping, no script
|-- integration/
|   |-- test_calculate_report_cli.py       # calculate-report --format html path
|   |-- test_generate_markdown_report.py   # generate-report --format html path
|   `-- test_report_regression_cases.py   # manifest-level HTML contract checks
`-- safety/
    `-- test_red_lines_and_language.py     # unsafe --format html still returns JSON
```

**Structure Decision**: Keep 010 as a renderer and CLI output-format feature. The `Report` object already contains the complete formal report contract, so HTML should be derived from it without changing report schema. `src/mingli_engine/html.py` owns only HTML presentation, escaping, and section structure; `src/mingli_engine/cli.py` owns format dispatch after safety checks pass.

## Complexity Tracking

No constitution violations.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Add a dedicated `render_html_report(report)` renderer instead of deriving HTML from Markdown text.
- Use Python standard library HTML escaping for all report text.
- Extend existing `--format` choices rather than adding new commands.
- Keep HTML pure static with inline CSS and no external resources.
- Verify output through structural tests instead of full snapshots.
- Keep red-line and invalid-input behavior unchanged.

## Phase 1: Design Summary

The feature defines a display-layer document contract and one CLI contract:

- [data-model.md](data-model.md)
- [contracts/html-report-contract.md](contracts/html-report-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Cultural tool, not fate verdict: PASS. The HTML contract forbids new interpretive conclusions and deterministic visual framing.
- Transparent calculation boundary: PASS. HTML must include existing source and assumptions sections.
- Ethical red lines: PASS. Contract requires safety JSON instead of formal HTML for unsafe requests.
- Reviewable reports: PASS. HTML must preserve section order and observation-basis placement.
- Test-first quality gates: PASS. Quickstart and future tasks include focused red/green tests before implementation.
- Privacy: PASS. No persistent storage, external resources, or new personal-data samples are introduced.
