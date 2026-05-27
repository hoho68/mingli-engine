# Implementation Plan: 典籍证据核心与放大报告口径

**Branch**: `011-classical-evidence-core` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/011-classical-evidence-core/spec.md`

## Summary

Build a first-class classical evidence layer from the nine user-provided 命理 PDFs and use it as the core basis for formal reports. The implementation will add reviewable source and evidence data, a deterministic evidence loader, source-backed formal judgment objects, expanded high-risk handling, and report rendering that shows evidence traces without presenting traditional claims as guaranteed outcomes.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules, `lunar-python==1.4.8`, Python standard-library `json`, `pathlib`, `dataclasses`; document conversion remains a development/preparation step using the existing Bruce converter skill rather than a runtime dependency.

**Storage**: Project-local source and evidence files under `src/mingli_engine/data/classical_sources/` plus optional review notes under `docs/classical_sources/`; no persistent user birth-data storage.

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI/library package on Windows first, portable to macOS/Linux

**Project Type**: Python CLI/library

**Performance Goals**: Loading the curated evidence corpus and generating a single report should add no more than 300 ms on a local machine after PDF extraction has already been performed.

**Constraints**: No network dependency, no LLM dependency at report runtime, no wholesale source copying into user reports, no silent use of unreadable PDF extraction, no guaranteed real-world outcomes, and no professional medical/legal/psychological/investment advice.

**Scale/Scope**: Initial corpus of nine books; first implementation should support tens to low hundreds of curated evidence units and one report at a time.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Evidence-based traditional analysis: PASS. The feature explicitly permits formal judgments only when backed by chart facts and curated evidence units, and the report contract requires conclusion strength and source trace.
- Transparent calculation and evidence boundary: PASS. Existing chart source and calendar assumptions stay visible, and new evidence traces identify source entries, rule families, and risk tiers.
- Expanded high-risk boundaries: PASS. High-risk source material is allowed as traditional risk-signal evidence, while exact death timing, exact lifespan, diagnosis/treatment, legal/psychological/investment instruction, coercive matching, anxiety creation, and paid-remedy upsells remain narrowed or refused.
- Reviewable classical evidence: PASS. The design introduces source entries, evidence units, evidence traces, and disputed/unavailable conclusion states.
- Test-first quality gates: PASS. The plan requires failing tests for source loading, evidence mapping, report schema changes, high-risk handling, disclaimer presence, and absolute-language filtering before implementation.
- Privacy: PASS. The feature stores only project knowledge artifacts and generated examples; user birth data remains in existing request/report flows and is not retained.

## Project Structure

### Documentation (this feature)

```text
specs/011-classical-evidence-core/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- classical-evidence-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- classical_sources.py          # load source registry and curated evidence units
|-- formal_interpretation.py      # build source-backed formal judgments from chart + evidence
|-- high_risk.py                  # classify/narrow high-risk traditional signals
|-- models.py                     # add source, evidence, trace, conclusion, and report fields
|-- report_schema.py              # assemble expanded source-backed report sections
|-- markdown.py                   # render evidence traces and formal judgment sections
|-- html.py                       # render the same expanded report contract as static HTML
|-- safety.py                     # align language review with Constitution v2.0
`-- data/
    `-- classical_sources/
        |-- sources.json          # nine-source registry with extraction/review status
        `-- evidence_units.json   # curated initial evidence cards

docs/classical_sources/
|-- README.md                     # review workflow for source extraction and evidence curation
`-- extracts/                     # optional readable Markdown extracts, not consumed blindly

tests/
|-- unit/
|   |-- test_classical_sources.py
|   |-- test_formal_interpretation.py
|   |-- test_high_risk.py
|   `-- test_report_schema.py
|-- integration/
|   |-- test_generate_markdown_report.py
|   `-- test_report_regression_cases.py
`-- safety/
    `-- test_expanded_high_risk_language.py
```

**Structure Decision**: Keep the feature inside the existing Python package. Source/evidence loading is separated from chart calculation, formal interpretation is separated from report rendering, and high-risk classification is separated from general safety text checks so each unit can be tested independently.

## Complexity Tracking

No constitution violations. The plan relies on Constitution v2.0.0, which was amended for this feature before planning.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Use curated project-local source/evidence files instead of reading PDFs at report runtime.
- Represent each book as a source entry with extraction and review status.
- Represent report-supporting knowledge as evidence units, not long source excerpts.
- Extend the existing report schema rather than replacing CLI commands or adding an LLM pipeline.
- Use conclusion strength and risk tier to make expanded judgment language auditable.
- Treat high-risk material as traditional risk-signal evidence with narrowing/refusal gates.
- Keep Markdown and HTML renderers aligned through the same `Report` object.

## Phase 1: Design Summary

The feature defines one core evidence contract and one internal data model:

- [data-model.md](data-model.md)
- [contracts/classical-evidence-contract.md](contracts/classical-evidence-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Evidence-based traditional analysis: PASS. Formal judgments require chart facts, evidence units, and visible evidence traces.
- Transparent calculation and evidence boundary: PASS. Data model and report contract include source ids, rule families, risk tiers, chart assumptions, and conclusion strength.
- Expanded high-risk boundaries: PASS. Contract requires high-risk narrowing/refusal behavior for exact outcomes and professional-advice requests.
- Reviewable classical evidence: PASS. Source entries and evidence units are independently reviewable and report traces identify the basis for each major conclusion.
- Test-first quality gates: PASS. Quickstart and future tasks require focused tests before implementation.
- Privacy: PASS. No new user data retention is introduced.
