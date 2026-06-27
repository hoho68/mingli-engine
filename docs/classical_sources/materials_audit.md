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
- 1 Life Death Book Markdown extract at
  `Markdown/2800.《命理生死之书》100页.md`, linked as a representation of the
  existing Life Death Book audit record.
- 5 prepared Markdown source batches, each represented by a raw folder, a
  cleaned folder, and a learning note.
- 1 raw external text corpus folder at `资料原文/文本类/`, registered as a
  risk-review triage backlog before source-library registration or extraction.
- 1 processing-status note at `资料整理/source_processing_status.md`.
- 1 knowledge-skeleton group at `资料整理/knowledge_skeleton/`.

Current representation coverage:

- Root PDFs remain `external_untracked` root-file references.
- The Life Death Book Markdown extract remains `external_untracked`
  preparation material and is not runtime evidence.
- Markdown batch folders remain `external_untracked` preparation references.
- The raw text corpus folder remains `external_untracked` and must be triaged
  before any source registration, extraction, or evidence work.
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
- The raw text corpus folder is an uncertain broad mixed corpus and must be
  triaged into bounded source groups before source-library registration.

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
- The raw text corpus folder is `needs_risk_review`; it is a large mixed
  external corpus that requires coarse inventory triage and source scope
  selection before any extraction.

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

- 9 `extraction_ready` items: ready ordinary or sensitive sources with
  source-library alignment, target rule families, readiness rationale, and
  pre-extraction checks.
- 5 `risk_review_backlog` items: four high-risk materials whose prerequisite
  boundary-screening actions are completed, plus the raw text corpus triage
  item now completed by the 2026-06-28 folder-level triage.
- 3 `blocked_backlog` items: one OCR-deferred Markdown batch, one blocked
  source, and one deferred workflow note.

The next five recommended actions are selected as a deliberately limited work
surface:

1. two highest-priority extraction-ready items;
2. one blocked/deferred backlog item;
3. the next ready extraction items by queue priority.

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

- 19 audited material groups and 30 material representations.
- Queue counts: `extraction_ready=9`, `risk_review_backlog=5`, and
  `blocked_backlog=3`.
- Backlog counters: `registration_backlog_count=0`,
  `risk_review_backlog_count=5`, `preparation_backlog_count=0`,
  `blocked_backlog_count=3`, `deferred_queue_count=2`, and
  `blocked_queue_count=1`.
- Next recommended queue item ids:
  `queue_northeast_blind_peak_extract`,
  `queue_mingli_true_formula_teacher_extract`,
  `queue_markdown_source_batch_003_register`,
  `queue_markdown_source_batch_004_prepare`,
  and `queue_duan_plain_mingxue_outline_extract`.
- `validate_materials_audit_quality()` returns `[]`.

## 015 Queue Refresh

The 2026-06-27 coverage-aware queue refresh compares the 015 next-action queue
with completed 016 work-package snapshots. The current 015 summary now includes
the newly registered raw text corpus triage backlog, and the refreshed queue
excludes queue ids already covered by 016/017.

- `queue-refresh-status=covered_or_completed_queue_exhausted`
- `015-queue-items=17`
- `016-covered-queue-items=16`
- `015-local-completed-queue-items=1`
- `uncovered-queue-items=0`
- `refreshed-next-action-ids=0`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-liang-bazi-core-source-selection`

This refresh is read-only planning metadata. It does not mark queue items
completed, mutate 016 packages, create 013 candidate/review/promotion records,
or alter 012 formal evidence. The raw text corpus triage item is locally
completed, so the next local new-material path is source selection for the
bounded Liang Xiangrun Bazi core group.

## 015 External Material Inventory Refresh

The 2026-06-27 external inventory refresh scanned root PDFs, `Markdown/`,
`资料原文/`, and `资料整理/` as path labels and immediate entries only. It did not
open, parse, move, convert, or rewrite external material files.

- `external-inventory-status=scoped_metadata_registered`
- `external-entries=31`
- `new-015-representations=2`
- `new-015-queue-items=1`
- `untracked-material-entries=0`
- `excluded-work-artifacts=3`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-raw-text-materials-folder-risk-triage`

Registered 015 metadata:

- `repr_life_death_book_100_pages_markdown_extract` links the existing Life
  Death Book Markdown extract to `audit_life_death_book_100_pages`.
- `audit_raw_text_materials_folder`, `repr_raw_text_materials_folder`,
  `ready_raw_text_materials_folder_triage`, and
  `queue_raw_text_materials_folder_triage` capture `资料原文/文本类/` as a
  high-risk triage backlog.

Excluded workflow artifacts:

- `资料整理/_inventory/`
- `资料整理/new_thread_prompt_2026-05-29.md`
- `资料整理/thread_handoff_2026-05-29.md`

## 015 Raw Text Materials Folder Risk Triage

The 2026-06-28 raw text triage uses only path labels and the existing CSV
inventory under `资料整理/_inventory/`. It does not open source files, read PDF or
document contents, transcribe media, OCR images, mutate external materials,
create 013 candidate/review/promotion records, or alter 012 formal evidence.

- `raw-text-triage-status=triage_completed`
- `raw-text-total-files=1139`
- `raw-text-priority-candidates=832`
- `raw-text-triage-groups=11`
- `risk-review-groups=3`
- `deferred-groups=6`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-liang-bazi-core-source-selection`

Exclusive triage groups:

- `raw_text_triage_ritual_remedy_high_risk`: 428 files, risk review required.
- `raw_text_triage_media_course_deferred`: 246 files, non-text media deferred.
- `raw_text_triage_bazi_general`: 184 files, source-selection backlog.
- `raw_text_triage_unclassified_deferred`: 150 files, manual title review
  required.
- `raw_text_triage_image_assets_deferred`: 52 files, image review deferred.
- `raw_text_triage_fengshui_geo`: 34 files, separate domain review.
- `raw_text_triage_qimen_dunjia`: 13 files, separate domain review.
- `raw_text_triage_liang_bazi_core`: 12 files, source selection ready.
- `raw_text_triage_ziwei_astrology`: 9 files, separate domain review.
- `raw_text_triage_blind_school_sensitive`: 8 files, risk review required.
- `raw_text_triage_life_death_high_risk`: 3 files, high-risk review required.

The immediate next bounded source-selection surface is
`raw_text_triage_liang_bazi_core`; high-risk ritual-remedy, blind-school, and
life-death groups stay behind risk review.

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
