# Classical Source Review Workflow

This directory tracks the human review workflow for the classical evidence
corpus used by formal reports.

Runtime report generation does not parse PDFs or Markdown extracts directly.
Only curated JSON files under `src/mingli_engine/data/classical_sources/` are
loaded by the engine.

## Preparation Materials

Root-level PDF files and the root `Markdown/` directory are user-provided
preparation material. Do not move, delete, rewrite, or commit those files unless
the user explicitly asks for that operation. Review notes in this directory may
refer to those materials, but runtime code must continue to load only curated
JSON from `src/mingli_engine/data/classical_sources/`.

## Review States

- `not_started`: the source is registered but no readable extract has been
  reviewed.
- `converted`: the source has a readable extract or review notes.
- `partial`: only part of the source has been reviewed.
- `failed`: extraction failed or produced unreadable text.

## Evidence Curation

1. Keep raw PDFs and generated extracts as preparation material only.
2. Summarize useful rules into concise evidence units.
3. Link every evidence unit to a registered source id and review reference.
4. Mark a source `approved` only when its curated evidence can support report
   conclusions.
5. Keep high-risk material tagged with limitations and uncertainty language.

Long passages should not be copied into report-facing evidence units.
