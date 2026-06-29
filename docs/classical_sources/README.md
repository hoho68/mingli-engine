# Classical Source Review Workflow

This directory tracks the human review workflow for the classical evidence
corpus used by formal reports.

Runtime report generation does not parse PDFs or Markdown extracts directly.
Only curated JSON files under `src/mingli_engine/data/classical_sources/` are
loaded by the engine.

## Current Handoff

For the current new-material reading and learning closure state, start with
[new_material_learning_handoff.md](new_material_learning_handoff.md). It links
the completed source-window learning closure, 017 learning-reference sync, and
candidate/formal evidence boundary audit, and gated ordinary source-selection and followup checkpoints into one continuation entrypoint.

## Preparation Materials

Root-level PDF files and the root `Markdown/` directory are user-provided
preparation material. Do not move, delete, rewrite, or commit those files unless
the user explicitly asks for that operation. Review notes in this directory may
refer to those materials, but runtime code must continue to load only curated
JSON from `src/mingli_engine/data/classical_sources/`.

## Source Intake Boundary

The 013 source-intake workflow adds a separate preparation queue under
`src/mingli_engine/data/source_intake/`. Those records can register external
materials, candidate extracts, review decisions, and promotion batches, but they
are not formal report evidence.

Formal reports continue to load only reviewed evidence units from
`src/mingli_engine/data/classical_sources/`. Pending, returned, rejected,
blocked, and approved-but-unpromoted candidates must stay out of report evidence
until a reviewer promotes them into the formal corpus.

The intake queue may reference root PDF labels or root `Markdown/` labels for
audit purposes. It must not copy long passages, track raw source files, or
change the user's external preparation materials.

## Source Library Boundary

The 014 source-library workflow adds a planning layer under
`src/mingli_engine/data/source_library/`. Source-library records describe which
materials exist, how ready they are, what rule families they may support, and
what the next action should be. They are not candidate extracts, promotion
batches, formal evidence, or report-ready evidence.

See [source_library.md](source_library.md) for the current source-library
snapshot, value summaries, and trust-boundary notes. Registered entries may
reference root PDF labels or root `Markdown/` labels, but they must not move,
delete, convert, commit, or read those raw source files as part of report
generation. `validate_source_library_quality()` rejects source-library metadata
that leaks into report-evidence language, copies long passages, or uses
absolute/high-risk wording. The 015 [materials audit](materials_audit.md)
checks which current local material groups match those source-library entries
and which ones still need registration, locator review, or risk review.

## Materials Audit Boundary

The 015 materials-audit workflow adds an inventory layer under
`src/mingli_engine/data/materials_audit/`. It records current root PDFs,
prepared Markdown batches, cleaned Markdown folders, learning notes,
processing-status notes, and knowledge-skeleton artifacts as auditable
preparation metadata.

See [materials_audit.md](materials_audit.md) for the current inventory snapshot
and raw-file non-mutation boundary. The audit may reference external material
labels such as root PDF names or `Markdown/` folders, but it must not move,
delete, convert, rewrite, or commit those raw files unless the user explicitly
asks for that operation. Audit records are not candidate extracts and are not
formal report evidence. Extraction-ready audit queue items still have to enter
the 013 [source-intake workflow](intake.md) before they can become reviewed
candidate extracts.

## Extraction Queue Intake Boundary

The 016 [extraction queue intake](extraction_queue_intake.md) workflow converts
the 015 next-action queue into a bounded handoff package for future manual 013
candidate extraction. It stores package metadata and extraction task records
under `src/mingli_engine/data/extraction_queue_intake/`, validates links back
to 015 audit/readiness/alignment records plus 014/013 source ids, and keeps all
package records outside candidate extracts, promotion batches, and formal
report evidence.

## Learning Reference Curation Boundary

The 017 [learning reference curation](learning_reference_curation.md) workflow
turns ready 016 extraction tasks into maintainer-readable learning notes,
learning points, and candidate-intake decisions, while preserving non-ready 016
backlog work as prerequisite action notes. These records trace back to
016/015/014/013 ids, preserve overlap warnings, and help plan later candidate
intake. A maintainer-selected `create_candidate` decision may be applied into
013 as a normal pending-review candidate. It still does not create review
decisions, promotion batches, or formal report evidence.

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
6. Promote source-intake candidates only after approval, link validation, and a
   reviewed promotion batch.

Long passages should not be copied into report-facing evidence units.
