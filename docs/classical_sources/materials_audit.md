# Existing Materials Audit

This document tracks the 015 existing-materials audit, source-library alignment,
readiness assessment, and next-action queue.

The materials-audit layer stores only maintainer-facing metadata under
`src/mingli_engine/data/materials_audit/`. It does not parse PDFs, convert raw
files, approve candidate extracts, or promote anything into formal report
evidence.

Related maintainer references:

- [README.md](README.md): overall classical source review workflow.
- [source_library.md](source_library.md): 014 source-library entries used by
  alignment findings and registration backlog items.
- [intake.md](intake.md): 013 candidate-intake workflow that extraction-ready
  queue items must enter before review or promotion.
- [extraction_queue_intake.md](extraction_queue_intake.md): 016 package handoff
  that turns eligible 015 next-action queue items into extraction tasks without
  creating candidate extracts.
- [learning_reference_curation.md](learning_reference_curation.md): 017
  learning/reference layer that turns ready 016 tasks into study metadata and
  keeps non-ready 016 backlog records as prerequisite action notes.
- [coverage.md](coverage.md): formal 012 evidence coverage snapshot used by
  reports.

## Inventory Snapshot

Current audited material groups:

- 9 root PDF groups already registered in the 014 source library.
- 5 prepared Markdown source batches, each represented by a raw folder, a
  cleaned folder, and a learning note.
- 1 processing-status note at `资料整理/source_processing_status.md`.
- 1 knowledge-skeleton group at `资料整理/knowledge_skeleton/`.

Current representation coverage:

- Root PDFs remain `external_untracked` root-file references.
- Markdown batch folders remain `external_untracked` preparation references.
- Learning notes, processing-status notes, and knowledge-skeleton files are
  tracked as audit representations only, not as report evidence.

## Source-Library Alignment

US2 adds explicit alignment findings between 015 audit records and 014
source-library entries. Alignment findings are review metadata only; they do not
merge records automatically.

Current alignment snapshot:

- 7 root PDF groups are exact matches to 014 source-library entries.
- 1 root PDF group is a likely match that still needs title confirmation.
- 1 root PDF group is aligned to a blocked 014 source-library entry.
- 3 Markdown batches need source-library registration or linking.
- 1 Markdown batch is treated as a possible edition variant pending locator
  review.
- 1 Markdown batch has uncertain identity and needs clarification before
  registration.
- The processing-status note is out of scope for source-library registration.
- The knowledge-skeleton group is a possible duplicate/aggregate of several
  source-library planning records and must not be silently merged.

Alignment rules:

- `exact` and `likely` findings must reference an existing 014
  `source_library_entry_id`.
- `missing_source_library_entry` findings must include a registration
  recommendation.
- `possible_duplicate` and `edition_variant` findings must include explanatory
  notes before any merge decision.
- `blocked_source_library_entry`, `uncertain`, and `out_of_scope` findings must
  include durable evidence explaining why the material cannot move forward as a
  routine source match.
- Loading alignment findings reads 014 source-library JSON for validation only;
  it must not mutate 014 source-library records.

## Readiness And Risk Boundaries

US3 adds preparation-readiness findings. These findings classify whether a
material can enter candidate-extraction review or must stay in a preparation,
registration, locator-review, risk-review, deferred, or blocked state.

Current readiness snapshot:

- Extraction-ready examples require a ready audit record, source-library
  relationship, target rule family, rights notes, ready reasons, locator
  confidence, source quality, and no blockers.
- Cleaned Markdown batches 001-003 are `needs_source_registration`; cleaned text
  alone is preparation quality, not extraction readiness.
- Markdown batch 004 is `needs_locator_review` because its possible
  edition-variant relationship must not be silently merged.
- High-risk sources such as blind-life, life-death, Jianghu-style, and batch 005
  are `needs_risk_review`; they cannot be routine extraction work.
- The blocked Blind School Secret source remains `blocked` until source access
  and quotation boundaries are clarified.
- The processing-status note is `deferred` because it is workflow metadata, not
  a source text.
- The knowledge skeleton is `preparation_backlog`; it is a derived aggregate and
  must not become report-usable evidence without component source review.

Readiness rules:

- `ready_for_extraction_review` requires ready reasons, no blockers, no missing
  prerequisites, locator confidence of `moderate` or `strong`, source quality
  other than `needs_recheck`, and a ready audit record.
- `needs_*`, `preparation_backlog`, `deferred`, and `blocked` require missing
  prerequisites or blockers.
- `high_risk` readiness requires explicit risk-review or boundary notes and may
  not use `extract_candidates` as a routine next action.
- Materials-audit quality validation rejects long copied passages, absolute
  outcome language, exact death/lifespan wording, medical/legal/psychological or
  investment instruction, coercive matching, anxiety creation, paid-remedy
  upsells, and report-evidence boundary leakage.
- Cleaned Markdown and knowledge-skeleton artifacts remain preparation aids.
  They are not candidate extracts, approved evidence units, or report-usable
  evidence.

## Next-Action Queue

US4 adds extraction queue items under
`src/mingli_engine/data/materials_audit/extraction_queue_items.json`. Queue items
turn the audit into a small maintainer-facing action list without reading or
mutating raw source files.

Current queue snapshot:

- 5 `extraction_ready` items: ready ordinary or sensitive sources with
  source-library alignment, target rule families, readiness rationale, and
  pre-extraction checks.
- 3 `registration_backlog` items: cleaned Markdown batches that need
  source-library registration before extraction review.
- 4 `risk_review_backlog` items: high-risk material that must complete
  boundary review before any candidate extraction.
- 2 `preparation_backlog` items: a possible edition variant needing locator and
  identity clarification, plus the knowledge skeleton aggregate that needs
  component source links and candidate review before extraction planning.
- 2 `blocked_backlog` items: one blocked source and one deferred workflow note.

The next five recommended actions are selected as a deliberately limited work
surface:

1. two highest-priority extraction-ready items;
2. one registration backlog item;
3. one risk-review backlog item;
4. one blocked/deferred backlog item.

Queue rules:

- `extraction_ready` items require exact or likely source-library alignment,
  extraction-ready readiness, target rule family or gap, and pre-extraction
  checks.
- High-risk queue items must stay in `risk_review_backlog` or blocked/deferred
  backlogs until boundary review is complete.
- Registration, preparation, risk-review, deferred, and blocked backlogs must
  have durable rationales plus linked readiness prerequisites or blockers.
- Queue items are planning metadata only. They are not candidate extracts,
  review decisions, promotion batches, approved evidence units, or formal report
  evidence.
- 017 learning reference notes, learning points, candidate-intake decisions, and
  prerequisite action notes consume the 016 package as metadata only; they do
  not mutate the 015 queue or mark any material as formal evidence.

Quick validation command:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.materials_audit import build_materials_audit_progress_summary, validate_materials_audit_quality; print(build_materials_audit_progress_summary()); print(validate_materials_audit_quality())"
```

Expected computed summary:

- 16 audited material groups and 26 material representations.
- Queue counts: `extraction_ready=5`, `registration_backlog=3`,
  `risk_review_backlog=4`, `preparation_backlog=1`, and
  `blocked_backlog=2`.
- Backlog counters: `registration_backlog_count=3`,
  `risk_review_backlog_count=4`, `preparation_backlog_count=2`,
  `blocked_backlog_count=2`, `deferred_queue_count=1`, and
  `blocked_queue_count=1`.
- Next recommended queue item ids:
  `queue_northeast_blind_peak_extract`,
  `queue_mingli_true_formula_teacher_extract`,
  `queue_markdown_source_batch_001_register`,
  `queue_blind_life_manual_risk_review`, and
  `queue_blind_school_secret_blocked`.
- `validate_materials_audit_quality()` returns `[]`.

## Raw-File Boundary

Root-level PDFs, the root `Markdown/` directory, `资料原文/`, and `资料整理/`
are user-provided preparation materials. The 015 workflow may reference their
labels or relative paths for audit purposes, but it must not move, delete,
rewrite, convert, or commit those raw materials unless the user explicitly asks
for that operation.

Runtime report generation still loads only curated JSON from
`src/mingli_engine/data/classical_sources/`. Materials-audit records,
representations, source-alignment findings, readiness findings, and queue items
are planning metadata. They do not count as candidate extracts, reviewed
evidence, promoted evidence, or report-usable evidence.

## Initial US1 Status

The first implementation slice validates material audit records and
representations, including duplicate ids, enum values, ready-for-review metadata,
high-risk notes, blocked/deferred reasons, and external raw-file boundaries.

The inventory summary can be computed with:

```powershell
uv run --with pytest python -m pytest tests/unit/test_materials_audit.py
```
