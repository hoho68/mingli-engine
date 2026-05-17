# Implementation Plan: 八字基础结构解读规则层

**Branch**: `003-bazi-interpretation-rules` | **Date**: 2026-05-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-bazi-interpretation-rules/spec.md`

## Summary

Add a deterministic, conservative interpretation layer that consumes existing `BaziChart` data and produces richer five-elements, day-master, ten-gods, structure-observation, limitation, and reflection text for existing Markdown reports. The feature keeps report sections and CLI commands stable while improving report content.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project dependencies only; no new runtime dependency

**Storage**: No persistent storage. Interpretation is computed in memory from `BaziChart`.

**Testing**: pytest unit, report schema, integration, and safety tests

**Target Platform**: Local command-line execution on Windows first, portable to macOS/Linux

**Project Type**: Single Python package with reusable library modules and CLI wrapper

**Performance Goals**: Add interpretation to one report in under 2 seconds on a local machine

**Constraints**: Basic structure observation only; no pattern determination, useful-god determination, day-master strength verdict, luck-cycle reading, auspiciousness, or fate outcome

**Scale/Scope**: One chart/report at a time; at least two fixed chart examples should produce stable interpretation summaries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Cultural tool, not fate verdict: PASS. This feature explicitly excludes deterministic fate language and presents observations as self-reflection.
- Transparent calculation boundary: PASS. Interpretation consumes existing chart data and does not change calendrical assumptions or source disclosure.
- Ethical red lines: PASS. Existing safety review remains mandatory before formal report output.
- Reviewable reports: PASS. Interpretation text is derived from structured chart fields and explicit rules.
- Test-first quality gates: PASS. Plan includes unit tests for rule outputs, report-schema tests, integration tests, red-line refusals, and absolute-language checks.
- Privacy: PASS. No storage is introduced; birth/chart data remains in memory and in user-requested output only.

## Phase 0 Research Summary

See [research.md](./research.md).

Key decisions:

- Use deterministic in-project rules, not an LLM or external knowledge service.
- Create a focused `interpretation.py` module that depends only on project models.
- Count five-elements signals from visible stems, visible branches, and hidden stems, with wording that distinguishes hidden-stem support from direct visible signals.
- Integrate interpretation into existing report fields rather than adding new public CLI commands or new Markdown sections.
- Keep excluded topics explicit in limitation language.

## Phase 1 Design Summary

See [data-model.md](./data-model.md), [contracts/report-interpretation-contract.md](./contracts/report-interpretation-contract.md), and [quickstart.md](./quickstart.md).

The design adds:

- `ElementDistribution`
- `TenGodPlacement`
- `BasicInterpretationSummary`
- basic interpretation rules for five-elements, day master, ten-gods, observations, limitations, and suggestions
- report integration for existing Markdown output paths

Existing public commands remain unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/003-bazi-interpretation-rules/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- report-interpretation-contract.md
`-- checklists/
    `-- requirements.md
```

### Source Code (repository root)

```text
src/
`-- mingli_engine/
    |-- __init__.py
    |-- chart_calculator.py
    |-- cli.py
    |-- interpretation.py
    |-- markdown.py
    |-- models.py
    |-- report_schema.py
    |-- safety.py
    `-- validation.py

tests/
|-- contract/
|   |-- test_auto_chart_cli_contract.py
|   `-- test_cli_json_contract.py
|-- integration/
|   |-- test_calculate_report_cli.py
|   `-- test_generate_markdown_report.py
|-- safety/
|   `-- test_red_lines_and_language.py
`-- unit/
    |-- test_interpretation.py
    |-- test_report_schema.py
    `-- existing unit tests
```

**Structure Decision**: Add one focused `interpretation.py` module. Keep calendrical calculation in `chart_calculator.py`/`calendar_provider.py`, report assembly in `report_schema.py`, Markdown rendering in `markdown.py`, and CLI dispatch in `cli.py`.

## Complexity Tracking

No constitution violations. No added complexity exceptions.

## Post-Design Constitution Check

- Cultural tool, not fate verdict: PASS. Report wording must remain reflective and non-deterministic.
- Transparent calculation boundary: PASS. Interpretation does not alter chart source or assumptions.
- Ethical red lines: PASS. Report safety review remains the output gate.
- Reviewable reports: PASS. Each summary traces to chart pillars, stems, branches, hidden stems, or ten-gods.
- Test-first quality gates: PASS. Plan requires failing tests before production code.
- Privacy: PASS. No new storage path is added.
