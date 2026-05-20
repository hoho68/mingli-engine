# Implementation Plan: 报告回归样例清单

**Branch**: `008-report-regression-cases` | **Date**: 2026-05-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-report-regression-cases/spec.md`

## Summary

Add a manifest-based regression sample library for existing report examples. The implementation will introduce a small case list under `examples/` and an integration test that runs every listed case through the existing CLI report paths. Safe cases must continue to produce Markdown with the 004-007 report contracts, while unsafe red-line cases must continue to return safety JSON. No CLI command, input schema, chart calculation, interpretation conclusion, or full Markdown snapshot will be added.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules plus `lunar-python==1.4.8`; no new runtime dependency

**Storage**: File-based example manifest under `examples/`; no persistent user data storage

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI package generating JSON and Markdown reports

**Project Type**: Python CLI/library

**Performance Goals**: Regression validation over the initial small manifest should complete as part of the existing test suite without noticeable delay

**Constraints**: Preserve existing CLI commands and flags, input JSON shapes, chart calculations, report wording contracts from 004-007, safety JSON behavior, and prohibition against full Markdown snapshots

**Scale/Scope**: Initial manifest contains at least three cases: safe automatic chart, safe external verified chart, and unsafe red-line focus case

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Cultural tool, not fate verdict: PASS. The feature adds regression validation only and does not add interpretive claims.
- Transparent calculation boundary: PASS. Safe cases explicitly guard source labels and calculation assumptions already shown in reports.
- Ethical red lines: PASS. Unsafe focus cases become part of the regression sample library and must continue returning safety JSON.
- Reviewable reports: PASS. The manifest makes representative examples explicit and ties them to stable report contracts.
- Test-first quality gates: PASS. Implementation tasks must write failing manifest-driven tests before adding the manifest.
- Privacy: PASS. The feature uses existing anonymized examples and introduces no retention of personal user data.

## Project Structure

### Documentation (this feature)

```text
specs/008-report-regression-cases/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- report-regression-cases-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
examples/
|-- report-regression-cases.json       # new manifest for representative report cases
|-- birth-profile.auto-gregorian.json  # existing safe automatic chart input
|-- bazi-chart.external-verified.json  # existing safe external verified input
`-- birth-profile.unsafe-focus.json    # existing unsafe focus input

tests/
`-- integration/
    `-- test_report_regression_cases.py # new manifest-driven regression tests

src/mingli_engine/
|-- cli.py             # unchanged; tests call existing commands
|-- report_schema.py   # unchanged unless tests reveal an existing contract gap
`-- markdown.py        # unchanged; no full snapshot renderer changes
```

**Structure Decision**: Keep 008 as a test and example-manifest feature. The manifest belongs under `examples/` because it documents representative sample inputs. The regression runner belongs under `tests/integration/` because it exercises CLI-level behavior and final report output. No production code should be required for the initial implementation.

## Complexity Tracking

No constitution violations.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Use a manifest instead of hard-coded case lists scattered across tests.
- Avoid full Markdown snapshots because report prose is expected to evolve.
- Keep regression checks at CLI/integration level.
- Reuse existing anonymized examples for the first version.
- Keep helpers local to the integration test unless production code needs them later.

## Phase 1: Design Summary

The feature defines a simple regression case manifest and one integration test contract:

- [data-model.md](data-model.md)
- [contracts/report-regression-cases-contract.md](contracts/report-regression-cases-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Cultural tool, not fate verdict: PASS. Case definitions describe validation purpose only.
- Transparent calculation boundary: PASS. Safe Markdown checks include source and assumptions visibility.
- Ethical red lines: PASS. Safety JSON cases are first-class manifest entries.
- Reviewable reports: PASS. Manifest entries document what each representative sample guards.
- Test-first quality gates: PASS. Plan requires a failing integration test before adding the manifest.
- Privacy: PASS. Existing anonymized samples remain local files; no user data is stored.
