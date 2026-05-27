# Implementation Plan: 经典证据库精修

**Branch**: `012-classical-evidence-curation` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/012-classical-evidence-curation/spec.md`

## Summary

Deepen the 011 classical evidence layer by curating the nine initial sources into a richer, auditable evidence corpus. The implementation will expand project-local curated evidence data, add curation batches, source conflicts, curation gaps, and coverage reporting, then use those structures to keep formal reports source-rich without changing the public report contract introduced by 011.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing project modules, `lunar-python==1.4.8`, Python standard-library `json`, `pathlib`, `dataclasses`, and `collections`; document conversion remains a preparation step outside runtime.

**Storage**: Project-local JSON files under `src/mingli_engine/data/classical_sources/` plus review notes under `docs/classical_sources/`; no database and no persistent user birth-data storage.

**Testing**: pytest via `uv run --with pytest python -m pytest`

**Target Platform**: Local CLI/library package on Windows first, portable to macOS/Linux

**Project Type**: Python CLI/library

**Performance Goals**: Loading the expanded curated corpus, conflicts, and coverage summary should add no more than 500 ms for a single report and should remain deterministic without network access.

**Constraints**: No runtime PDF parsing, no LLM dependency at report runtime, no wholesale source copying into reports, no unreviewed or blocked source evidence in formal conclusions, no exact death/lifespan output, no diagnosis/treatment/legal/psychological/investment instruction, no paid-remedy upsell.

**Scale/Scope**: Nine initial books, at least 60 curated evidence units, at least eight rule families, one corpus loaded per report or validation run.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Evidence-based traditional analysis: PASS. The feature expands only source-backed evidence units and keeps report judgments tied to chart facts, evidence ids, and conclusion strength.
- Transparent calculation and evidence boundary: PASS. The plan keeps chart calculation separate from evidence curation and adds source references, conflicts, gaps, and coverage summaries.
- Expanded high-risk boundaries: PASS. High-risk evidence remains allowed only as traditional risk-signal material with limitations; exact outcomes and professional advice stay refused or narrowed.
- Reviewable classical evidence: PASS. Evidence units, curation batches, source conflicts, and curation gaps are structured for review and regression checks.
- Test-first quality gates: PASS. Tasks must add failing tests for coverage counts, source refs, conflict handling, high-risk limitations, long-summary rejection, and report regression before implementation.
- Privacy: PASS. The feature stores only source knowledge and review metadata; user birth data and generated reports are not retained.

## Project Structure

### Documentation (this feature)

```text
specs/012-classical-evidence-curation/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- evidence-curation-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- classical_sources.py          # extend source/evidence/conflict/gap loading and validation
|-- evidence_curation.py          # build coverage reports and curation quality checks
|-- formal_interpretation.py      # consume expanded evidence and conflict/gap metadata
|-- models.py                     # add curation batch, conflict, gap, and coverage models
|-- report_schema.py              # preserve 011 report contract while exposing richer evidence notes
|-- markdown.py                   # no new public format; render through Report object if needed
|-- html.py                       # same report contract as Markdown
|-- safety.py                     # keep high-risk and absolute-language gates stable
`-- data/
    `-- classical_sources/
        |-- sources.json
        |-- evidence_units.json
        |-- curation_batches.json
        `-- source_conflicts.json

docs/classical_sources/
|-- README.md
|-- coverage.md                   # generated or maintained coverage notes for reviewers
`-- extracts/

tests/
|-- unit/
|   |-- test_classical_sources.py
|   |-- test_evidence_curation.py
|   |-- test_formal_interpretation.py
|   `-- test_report_schema.py
|-- integration/
|   `-- test_report_regression_cases.py
`-- safety/
    `-- test_expanded_high_risk_language.py
```

**Structure Decision**: Keep 012 inside the existing Python package. The existing `classical_sources.py` remains the deterministic loader; a new `evidence_curation.py` owns coverage and quality reporting so curation checks do not blur into report rendering. Reports continue using the 011 `Report` object and renderer contract.

## Complexity Tracking

No constitution violations. The plan intentionally avoids runtime PDF parsing and avoids a database so the corpus remains deterministic and reviewable.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Expand curated JSON rather than parse PDFs or Markdown at report runtime.
- Treat evidence curation as batches so additions can be audited together.
- Use source references and review-note references when pagination is unreliable.
- Represent source conflicts separately from evidence units.
- Compute coverage reports from loaded data instead of maintaining duplicated counts by hand.
- Keep the 011 report public contract stable while improving source richness.

## Phase 1: Design Summary

The feature defines curation data, validation, and maintainer-facing quality contracts:

- [data-model.md](data-model.md)
- [contracts/evidence-curation-contract.md](contracts/evidence-curation-contract.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Evidence-based traditional analysis: PASS. Expanded evidence and conflicts continue to support only traceable traditional judgments.
- Transparent calculation and evidence boundary: PASS. Data model keeps source curation, chart signals, report traces, and coverage reporting separate.
- Expanded high-risk boundaries: PASS. High-risk evidence requires limitations and report output remains narrowed/refused for exact or professional-advice requests.
- Reviewable classical evidence: PASS. Batches, conflicts, gaps, and coverage reports make every addition auditable.
- Test-first quality gates: PASS. Quickstart requires focused curation, report, high-risk, and regression tests before implementation is complete.
- Privacy: PASS. No personal case archive or generated-report retention is introduced.
