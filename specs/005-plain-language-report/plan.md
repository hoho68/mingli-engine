# Implementation Plan: 八字报告白话表达优化

**Branch**: `005-plain-language-report` | **Date**: 2026-05-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-plain-language-report/spec.md`

## Summary

Improve the current layered Markdown Bazi report by translating machine-facing values into reader-facing Chinese wording and lightly polishing stiff guidance sentences. The implementation keeps the existing report data flow, CLI commands, interpretation rules, safety checks, and layered Markdown structure unchanged; wording preparation stays in the report assembly boundary.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing standard-library dataclasses and project modules; no new runtime dependency

**Storage**: N/A

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI package generating Markdown reports

**Project Type**: Python CLI/library

**Performance Goals**: Report text preparation remains immediate for one in-memory `Report`

**Constraints**: Preserve existing CLI commands, input JSON shapes, safety refusal exit codes, disclaimer, source disclosure, feature 004 heading order, and non-deterministic language

**Scale/Scope**: One Markdown report at a time; no web UI, PDF export, account system, stored archive, new Bazi algorithm, or new interpretation conclusion

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Cultural tool, not fate verdict: PASS. The feature only changes wording and explicitly avoids new prediction, fate, auspiciousness, pattern, useful-god, strength, or luck-cycle conclusions.
- Transparent calculation boundary: PASS. Source type, source note, confidence, calendar assumptions, timezone, solar-term assumptions, and true-solar-time disclosure remain visible, but known raw values become reader-facing Chinese labels.
- Ethical red lines: PASS. Existing refusal and safety JSON behavior remain unchanged. Formal reports still include disclaimer and ethics reminder.
- Reviewable reports: PASS. The report keeps the 004 layers so factual basis, structure observation, boundary, and reflection stay traceable.
- Test-first quality gates: PASS. Plan requires failing unit and integration tests before wording changes, plus safety tests for prohibited absolute language and red-line refusals.
- Privacy: PASS. No storage, retention, or new personal-data capture is introduced.

## Project Structure

### Documentation (this feature)

```text
specs/005-plain-language-report/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── plain-language-markdown-contract.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/mingli_engine/
├── report_schema.py   # formats reader-facing labels and prepares polished report text
├── markdown.py        # unchanged layout boundary; existing layered headings remain
├── cli.py             # unchanged command entry points
└── models.py          # unchanged report data shape unless tests prove a small field is necessary

tests/
├── unit/
│   ├── test_report_schema.py      # reader-facing labels and polished quick guide
│   └── test_markdown_renderer.py  # unchanged layered heading contract
├── integration/
│   ├── test_generate_markdown_report.py  # external chart plain-language output
│   └── test_calculate_report_cli.py      # auto chart plain-language output
└── safety/
    └── test_red_lines_and_language.py    # prohibited phrase and safety JSON behavior
```

**Structure Decision**: Keep wording and label formatting in `report_schema.py`, where report text is assembled from chart and interpretation objects. Do not move value translation into `markdown.py`; the renderer should keep only layout responsibility.

## Complexity Tracking

No constitution violations.

## Phase 0: Research Summary

The planning decision is to add small reader-facing label helpers in `report_schema.py` rather than introduce a new localization framework or renderer-level replacement pass. This keeps the output deterministic, avoids global string replacement risks, and preserves chart-source transparency.

## Phase 1: Design Summary

The feature defines reader-facing labels for known machine values, a conservative fallback rule for unmapped values, and a Markdown contract that prohibits selected raw machine labels from successful formal reports. Tests should verify schema-level text, both CLI generation paths, unchanged heading order, red-line safety JSON, and absence of prohibited absolute phrases.

## Post-Design Constitution Check

- Cultural tool, not fate verdict: PASS. Polished wording remains observational and reflective.
- Transparent calculation boundary: PASS. Source disclosure remains visible in `第一层：基础资料`.
- Ethical red lines: PASS. Refusal paths, disclaimer, ethics reminder, and prohibited phrase checks remain mandatory.
- Reviewable reports: PASS. Label mapping is explicit and testable; report layers remain unchanged.
- Test-first quality gates: PASS. The implementation plan covers unit, integration, renderer, and safety tests before completion.
- Privacy: PASS. No new storage or data retention.
