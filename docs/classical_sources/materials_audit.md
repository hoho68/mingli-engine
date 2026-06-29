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

- 24 audited material groups and 35 material representations.
- Queue counts: `extraction_ready=14`, `risk_review_backlog=5`, and
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
- `015-queue-items=30`
- `016-covered-queue-items=29`
- `015-local-completed-queue-items=1`
- `uncovered-queue-items=0`
- `refreshed-next-action-ids=0`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-external-material-inventory-refresh`
- `post_selected_variant_queue_surface_confirmed`: `passed`

This refresh is read-only planning metadata. It does not mark queue items
completed, mutate 016 packages, create 013 candidate/review/promotion records,
or alter 012 formal evidence. The raw text corpus triage item is locally
completed, the bounded Liang Xiangrun Bazi core path is completed, and the Bazi
general selected-variant path is completed. The local queue is exhausted, so the
next new-material path starts with a fresh external inventory refresh rather
than returning to an already completed stage.

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
- `next-material-entry=015-raw-text-next-cycle-source-selection`
- `post_queue_refresh_surface_confirmed`: `passed`

The post-selected-variant queue refresh confirms that the existing local 015
queue surface is covered or locally completed. The next material entry is
therefore a next-cycle raw-text source selection pass, not a return to the
already completed raw-text folder triage.

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

## 015 Liang Bazi Core Source Selection

The 2026-06-28 Liang Bazi core source selection uses only inventory labels,
existing source batch status summaries, source-library metadata, learning
reference ids, and candidate ids. It does not open source PDFs, create new
source-library records, create 013 candidate/review/promotion records, or alter
012 formal evidence.

- `source-selection-status=source_selection_completed`
- `source-selection-items=12`
- `existing-batch-covered=8`
- `selected-for-individual-review=2`
- `variant-review-required=1`
- `sensitive-boundary-deferred=1`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-liang-bazi-core-individual-review`

Selected individual review items:

- `liang_tianyuan_wuxian_commentary`
- `liang_yushi_yongshen_ciyuan`

Deferred or review-gated items:

- `liang_four_corner_digest`: possible digest or edition variant requiring
  identity review before reuse.
- `liang_female_destiny_detail`: sensitive gendered relationship material
  requiring boundary review before learning use.

The 8 existing-batch-covered items remain represented by Markdown source
batches 001, 002, and 004. The next bounded work surface is individual
cleaned-text review for the two selected items, still outside 013/012 unless a
separate candidate-intake step is explicitly authorized.

## 015 Bazi General Source Cluster Selection

The 2026-06-28 Bazi general source cluster selection uses only inventory CSV
counts, filename labels, representative paths, and the existing
`raw_text_triage_bazi_general` group. It does not open raw source files, create
source-library records, create 013 candidate/review/promotion records, or alter
012 formal evidence.

- `cluster-selection-status=cluster_selection_completed`
- `cluster-selection-items=7`
- `clustered-files=184`
- `clustered-priority-candidates=183`
- `selected-clusters=2`
- `deferred-clusters=3`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-bazi-general-cluster-source-selection`

Selected clusters:

- `bazi_general_foundation_textbook_cluster`
- `bazi_general_classical_reference_cluster`

Deferred or review-gated clusters:

- `bazi_general_modern_method_series_cluster`: fragmented modern method series
  needing identity review.
- `bazi_general_sensitive_topic_cluster`: sensitive relationship, psychology,
  advice, or mixed-topic labels requiring boundary review.
- `bazi_general_misc_identity_review_cluster`: miscellaneous weak-title labels
  requiring manual title review.

The source-level selection inside the two selected clusters is now recorded in
the next section. Registration, extraction, 013 candidate intake, and 012
evidence remain blocked unless explicitly authorized.

## 015 Bazi General Cluster Source Selection

The 2026-06-28 Bazi general cluster source selection uses only inventory CSV
metadata, source-root-relative path labels, and the previously selected
foundation/textbook and classical-reference clusters. It does not open raw
source files, create source-library records, create 013 candidate/review/
promotion records, or alter 012 formal evidence.

- `cluster-source-selection-status=cluster_source_selection_completed`
- `cluster-source-selection-items=8`
- `cluster-source-files=13`
- `cluster-source-priority-candidates=13`
- `selected-for-identity-review=5`
- `variant-identity-review=2`
- `deferred-after-cluster-selection=1`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-bazi-general-source-identity-review`

Selected clusters:

- `bazi_general_foundation_textbook_cluster`
- `bazi_general_classical_reference_cluster`

Selected source records:

- `bazi_general_foundation_youran_notes`
- `bazi_general_foundation_tianma_notes`
- `bazi_general_foundation_lecture_textbook`
- `bazi_general_foundation_beichen_intro`
- `bazi_general_classical_ziping_orthodox_pair`

Variant identity review records:

- `bazi_general_classical_ditiansui_variant_set`
- `bazi_general_classical_qiongtong_variant_set`

Deferred records:

- `bazi_general_classical_huntian_baolan_ziping`

The source identity review for these records is now recorded in the next
section. Registration, reading, extraction, 013 candidate intake, and 012
evidence remain blocked unless explicitly authorized.

## 015 Bazi General Source Identity Review

The 2026-06-28 Bazi general source identity review uses only path labels,
existing source-level selection metadata, and source-library overlap metadata.
It does not open raw source files, create source-library records, create 013
candidate/review/promotion records, or alter 012 formal evidence.

- `source-identity-review-status=source_identity_review_completed`
- `source-identity-review-items=8`
- `existing-batch-overlap=2`
- `registration-prep-ready=3`
- `variant-choice-required=2`
- `deferred-large-source=1`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-bazi-general-registration-prep`

Existing-batch overlap records:

- `bazi_general_identity_youran_notes`: reuse `entry_markdown_source_batch_001`.
- `bazi_general_identity_tianma_notes`: reuse `entry_markdown_source_batch_001`.

Registration-prep-ready records:

- `bazi_general_identity_lecture_textbook`
- `bazi_general_identity_beichen_intro`
- `bazi_general_identity_ziping_orthodox_pair`

Variant-choice records:

- `bazi_general_identity_ditiansui_variant_set`
- `bazi_general_identity_qiongtong_variant_set`

Deferred records:

- `bazi_general_identity_huntian_baolan_ziping`

The registration-prep metadata for the three registration-prep-ready records is
now recorded in the next section. Existing Batch 001 overlaps should not be
registered again, variant sets need a later choice step, and the large deferred
source remains out of the immediate reading path.

## 015 Bazi General Registration Prep

The 2026-06-28 Bazi general registration prep records proposed source-library
metadata for three source identities. It does not mutate
`source_library_entries.json`, open raw source files, create 013
candidate/review/promotion records, or alter 012 formal evidence.

- `registration-prep-status=registration_prep_completed`
- `registration-prep-items=3`
- `proposed-source-files=4`
- `skipped-existing-batch-overlap=2`
- `blocked-variant-choice=2`
- `deferred-large-source=1`
- `source-library-mutation-authorized=false`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-bazi-general-source-registration`

Proposed source-library entry ids:

- `entry_bazi_general_lecture_textbook_pdf`
- `entry_bazi_general_beichen_intro_pdf`
- `entry_bazi_general_ziping_orthodox_pair_pdf`

Registration-prep records:

- `bazi_general_registration_prep_lecture_textbook`
- `bazi_general_registration_prep_beichen_intro`
- `bazi_general_registration_prep_ziping_orthodox_pair`

Skipped existing-batch overlap ids:

- `bazi_general_identity_youran_notes`
- `bazi_general_identity_tianma_notes`

Blocked variant-choice ids:

- `bazi_general_identity_ditiansui_variant_set`
- `bazi_general_identity_qiongtong_variant_set`

Deferred ids:

- `bazi_general_identity_huntian_baolan_ziping`

## 015 Bazi General Source Registration

The 2026-06-28 Bazi general source-registration checkpoint registered the
three prepared source-library metadata packets. It did not register Batch 001
overlaps, variant-choice records, or the deferred large source, and it did not
open raw source files or create downstream 013/012 evidence changes.

- Registration id: `015-bazi-general-source-registration`
- `source-registration-status=source_registration_completed`
- `registered-source-entries=3`
- `registered-source-files=4`
- `skipped-existing-batch-overlap=2`
- `blocked-variant-choice=2`
- `deferred-large-source=1`
- `source-library-mutation-authorized=true`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-bazi-general-source-preparation-reading`

Registered source-library entry ids:

- `entry_bazi_general_lecture_textbook_pdf`
- `entry_bazi_general_beichen_intro_pdf`
- `entry_bazi_general_ziping_orthodox_pair_pdf`

Registered material ids:

- `material_bazi_general_lecture_textbook_pdf`
- `material_bazi_general_beichen_intro_pdf`
- `material_bazi_general_ziping_orthodox_pair_pdf`

Skipped existing-batch overlap ids:

- `bazi_general_identity_youran_notes`
- `bazi_general_identity_tianma_notes`

Blocked variant-choice ids:

- `bazi_general_identity_ditiansui_variant_set`
- `bazi_general_identity_qiongtong_variant_set`

Deferred ids:

- `bazi_general_identity_huntian_baolan_ziping`

Boundary checks:

- `registration_prep_items_loaded`: `passed`
- `source_library_entries_loaded`: `passed`
- `prepared_entries_registered`: `passed`
- `registered_entries_match_prep_metadata`: `passed`
- `skipped_existing_batch_overlap_not_duplicated`: `passed`
- `variant_choice_boundary_respected`: `passed`
- `deferred_large_source_not_registered`: `passed`
- `raw_materials_not_mutated`: `passed`
- `013_012_not_mutated`: `passed`

Guardrails:

- Only source-library metadata registration is authorized in this stage.
- Existing Markdown Batch 001 overlaps stay represented by their existing source-library entry.
- Variant sets require separate selected-variant authorization before registration.
- The deferred large source remains outside registration.
- Reading, extraction, 013 candidate intake, and 012 evidence changes remain blocked.

## 015 Bazi General Source Preparation Reading

The 2026-06-28 preparation-reading checkpoint completed the authorized reading
stage for the three newly registered Bazi general PDF sources. Temporary
conversion/render artifacts stayed outside Git; only concise derived metadata,
013 intake records, and 012 evidence links are tracked.

- Reading id: `015-bazi-general-source-preparation-reading`
- `source-preparation-reading-status=preparation_reading_completed`
- `source-preparation-reading-entries=3`
- `source-preparation-reading-files=4`
- `material-audit-records=3`
- `extraction-tasks=3`
- `learning-notes=3`
- `candidate-extracts=3`
- `formal-evidence-units=3`
- `source-library-mutation-authorized=true`
- `downstream-mutation-authorized=true`
- `next-material-entry=015-bazi-general-variant-choice-and-deferred-review`

Source-library entry ids:

- `entry_bazi_general_lecture_textbook_pdf`
- `entry_bazi_general_beichen_intro_pdf`
- `entry_bazi_general_ziping_orthodox_pair_pdf`

Source material ids:

- `material_bazi_general_lecture_textbook_pdf`
- `material_bazi_general_beichen_intro_pdf`
- `material_bazi_general_ziping_orthodox_pair_pdf`

Promoted candidate ids:

- `candidate_bazi_general_lecture_pattern_strength_001`
- `candidate_bazi_general_beichen_branch_interaction_001`
- `candidate_bazi_general_ziping_useful_god_001`

Formal evidence ids:

- `bazi_general_lecture_pattern_strength_001`
- `bazi_general_beichen_branch_interaction_001`
- `bazi_general_ziping_useful_god_001`

Boundary checks:

- `registered_entries_loaded`: `passed`
- `material_preparation_records_loaded`: `passed`
- `extraction_tasks_completed`: `passed`
- `learning_notes_applied`: `passed`
- `013_candidates_reviewed_promoted`: `passed`
- `012_formal_evidence_linked`: `passed`
- `skipped_existing_batch_overlap_not_duplicated`: `passed`
- `variant_choice_boundary_respected`: `passed`
- `deferred_large_source_not_mutated`: `passed`
- `raw_materials_not_mutated`: `passed`

Guardrails:

- Only concise derived learning and evidence metadata is stored.
- Full PDF conversions and rendered page images remain temporary artifacts.
- Existing Batch 001 overlaps are not duplicated.
- Ditiansui and Qiongtong are handled by the selected-variant registration-prep
  stage; Huntian Baolan remains deferred.

The next bounded work surface is
`015-bazi-general-variant-choice-and-deferred-review`.

## 015 Bazi General Variant Choice And Deferred Review

The 2026-06-28 variant/deferred review closed the remaining three Bazi general
identity-review records from this source batch. It selects canonical local
references for Ditiansui and Qiongtong, keeps Huntian Baolan deferred as a
large source, and does not authorize source-library, 013, or 012 mutation.

- Review id: `015-bazi-general-variant-choice-and-deferred-review`
- `variant-deferred-review-status=variant_deferred_review_completed`
- `variant-deferred-review-items=3`
- `variant-review-items=2`
- `deferred-review-items=1`
- `selected-canonical-variants=2`
- `source-library-registration-authorized=0`
- `source-library-mutation-authorized=false`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-bazi-general-selected-variant-registration-prep`

Variant-choice review ids:

- `bazi_general_variant_review_ditiansui_variant_set`
- `bazi_general_variant_review_qiongtong_variant_set`

Deferred review ids:

- `bazi_general_deferred_review_huntian_baolan_ziping`

Selected canonical variant ids:

- `bazi_general_variant_review_ditiansui_variant_set`: `滴天髓.pdf`
- `bazi_general_variant_review_qiongtong_variant_set`: `穷通宝鉴/窮通寶鑒.pdf`

Boundary checks:

- `variant_deferred_items_loaded`: `passed`
- `identity_review_references_valid`: `passed`
- `source_selection_references_valid`: `passed`
- `variant_records_match_identity_status`: `passed`
- `deferred_records_match_identity_status`: `passed`
- `source_paths_are_relative`: `passed`
- `canonical_variant_choices_recorded`: `passed`
- `source_library_not_mutated`: `passed`
- `013_012_not_mutated`: `passed`
- `raw_materials_not_mutated`: `passed`

Guardrails:

- Variant-choice records have selected local references only; registration
  still requires the next explicit prep step.
- The Huntian Baolan large source remains deferred and is not opened,
  converted, or registered.
- No source-library, 013 candidate, review, promotion, or 012 evidence mutation
  is authorized by this review.
- The next stage should prepare only the selected Ditiansui and Qiongtong
  variants for possible source registration.

The next bounded work surface is
`015-bazi-general-selected-variant-registration-prep`.

## 015 Bazi General Selected Variant Registration Prep

The 2026-06-28 selected-variant registration-prep checkpoint registered the
canonical Ditiansui and Qiongtong local references and advanced their weak
locator-backed metadata through 016, 017, 013, and 012 under explicit user
authorization. It does not open, move, convert, or rewrite the external PDF
files.

- `selected-variant-registration-status=completed`
- `selected-variant-source-entries=2`
- `selected-variant-material-audit-records=2`
- `selected-variant-extraction-tasks=2`
- `selected-variant-learning-notes=2`
- `selected-variant-candidate-extracts=2`
- `selected-variant-formal-evidence-units=2`
- `source-library-mutation-authorized=true`
- `downstream-mutation-authorized=true`
- `next-material-entry=015-materials-audit-next-action-queue`

Selected source-library entry ids:

- `entry_bazi_general_ditiansui_selected_pdf`: `滴天髓.pdf`
- `entry_bazi_general_qiongtong_selected_pdf`: `穷通宝鉴/窮通寶鑒.pdf`

Promoted candidate ids:

- `candidate_bazi_general_ditiansui_pattern_strength_001`
- `candidate_bazi_general_qiongtong_useful_god_001`

Formal evidence ids:

- `bazi_general_ditiansui_pattern_strength_001`
- `bazi_general_qiongtong_useful_god_001`

Guardrails:

- These are weak selected-variant source-preparation anchors, not direct
  transcriptions.
- No long source passages are tracked.
- Later page-level transcription is required before exact classical wording or
  quotation.

## 015 Raw Text Next Cycle Source Selection

The 2026-06-28 raw text next-cycle source selection uses only the existing
Bazi general source-cluster inventory metadata. It does not open raw source
files, create source-library records, create 013 candidate/review/promotion
records, or alter 012 formal evidence.

- Selection id: `015-raw-text-next-cycle-source-selection`
- `next-cycle-source-selection-status=next_cycle_source_selection_completed`
- `next-cycle-source-selection-items=5`
- `selected-for-identity-review=2`
- `deferred-clusters=2`
- `risk-review-clusters=1`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-raw-text-next-cycle-identity-review`

Selected clusters:

- `bazi_general_modern_method_series_cluster`
- `bazi_general_misc_identity_review_cluster`

Deferred clusters:

- `bazi_general_case_collection_cluster`
- `bazi_general_practical_formula_cluster`

Risk-review clusters:

- `bazi_general_sensitive_topic_cluster`

Boundary checks:

- `next_cycle_items_loaded`: `passed`
- `source_cluster_items_loaded`: `passed`
- `external_inventory_entrypoint_confirmed`: `passed`
- `selected_clusters_need_identity_review`: `passed`
- `deferred_clusters_stay_deferred`: `passed`
- `sensitive_clusters_stay_risk_review`: `passed`
- `huntian_baolan_deferred`: `passed`
- `raw_materials_not_mutated`: `passed`
- `source_library_not_mutated`: `passed`
- `013_012_not_mutated`: `passed`

Guardrails:

- Next-cycle selection uses source-cluster inventory metadata only.
- Selected clusters require identity review before registration, reading, or
  extraction.
- Case and formula clusters stay deferred until the selected ordinary identity
  review is closed.
- Sensitive clusters require separate risk review before any learning use.
- Raw files, source-library records, candidates, reviews, promotions, and formal
  evidence are not mutated.

## 015 Raw Text Next Cycle Identity Review

The 2026-06-28 raw text next-cycle identity review uses only the selected
next-cycle source-selection records and source-cluster metadata. It does not
open raw source files, create source-library records, create 013 candidate/
review/promotion records, or alter 012 formal evidence.

- Review id: `015-raw-text-next-cycle-identity-review`
- `next-cycle-identity-review-status=next_cycle_identity_review_completed`
- `next-cycle-identity-review-items=2`
- `cluster-source-selection-required=2`
- `registration-prep-ready=0`
- `source-library-overlap-found=0`
- `source-library-mutation-authorized=false`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-raw-text-next-cycle-cluster-source-selection`

Cluster-source selection required:

- `next_cycle_identity_bazi_modern_method_series`
- `next_cycle_identity_bazi_misc_review`

Registration-prep-ready records:

Source-library overlap records:

Boundary checks:

- `identity_review_items_loaded`: `passed`
- `next_cycle_source_selection_items_loaded`: `passed`
- `selected_source_selection_references_valid`: `passed`
- `selected_clusters_only`: `passed`
- `cluster_counts_match_source_selection`: `passed`
- `deferred_clusters_remain_out_of_scope`: `passed`
- `risk_review_clusters_remain_out_of_scope`: `passed`
- `raw_materials_not_mutated`: `passed`
- `source_library_not_mutated`: `passed`
- `013_012_not_mutated`: `passed`

Guardrails:

- Next-cycle identity review uses source-selection metadata only.
- Selected clusters still require source-level selection before registration
  prep.
- Case, formula, and sensitive clusters remain outside this identity review.
- Raw files, source-library records, candidates, reviews, promotions, and formal
  evidence are not mutated.

## 015 Raw Text Next Cycle Cluster Source Selection

The 2026-06-28 next-cycle cluster-source selection chooses two bounded
source-level records from the ordinary modern-method and miscellaneous
clusters, then records the authorized source-library, 013, and 012 weak-locator
metadata chain. It does not move, convert, or rewrite external raw materials.

- Selection id: `015-raw-text-next-cycle-cluster-source-selection`
- `next-cycle-cluster-source-selection-status=next_cycle_cluster_source_selection_completed`
- `next-cycle-cluster-source-selection-items=2`
- `selected-for-registration=2`
- `registered-source-entries=2`
- `candidate-extracts=2`
- `formal-evidence-units=2`
- `source-library-mutation-authorized=true`
- `downstream-mutation-authorized=true`
- `next-material-entry=015-raw-text-next-cycle-followup-selection`

Selected source records:

- `next_cycle_cluster_source_true_spirit_positioning`
- `next_cycle_cluster_source_mingli_wangdoujing`

Source-library entry ids:

- `entry_bazi_general_true_spirit_positioning_pdf`
- `entry_bazi_general_mingli_wangdoujing_pdf`

Promoted candidate ids:

- `candidate_bazi_general_true_spirit_useful_god_001`
- `candidate_bazi_general_wangdoujing_branch_interaction_001`

Formal evidence ids:

- `bazi_general_true_spirit_useful_god_001`
- `bazi_general_wangdoujing_branch_interaction_001`

Boundary checks:

- `cluster_source_selection_items_loaded`: `passed`
- `identity_review_references_valid`: `passed`
- `source_paths_are_relative`: `passed`
- `selected_clusters_only`: `passed`
- `source_library_entries_registered`: `passed`
- `013_candidates_promoted`: `passed`
- `012_evidence_promoted`: `passed`
- `deferred_clusters_remain_out_of_scope`: `passed`
- `risk_review_clusters_remain_out_of_scope`: `passed`
- `raw_materials_not_mutated`: `passed`

Guardrails:

- Only two authorized source-level records are registered in this next-cycle
  slice.
- All locators remain weak page-level placeholders until later transcription.
- Case, formula, and sensitive clusters remain outside this selection.
- Raw external materials are not moved, converted, or rewritten.

## 015 Raw Text Next Cycle Followup Selection

This followup slice selects two additional bounded ordinary-risk source-level
records from the already selected modern-method and miscellaneous clusters, then
records the authorized source-library, 013, and 012 weak-locator metadata chain.
It does not move, convert, or rewrite external raw materials.

- Selection id: `015-raw-text-next-cycle-followup-selection`
- `next-cycle-followup-selection-status=next_cycle_followup_selection_completed`
- `next-cycle-followup-selection-items=2`
- `selected-for-registration=2`
- `registered-source-entries=2`
- `candidate-extracts=2`
- `formal-evidence-units=2`
- `source-library-mutation-authorized=true`
- `downstream-mutation-authorized=true`
- `next-material-entry=015-raw-text-next-cycle-gated-cluster-review-prep`

Selected source records:

- `next_cycle_followup_source_xinpai_essence_part2`
- `next_cycle_followup_source_xingming_shuozheng_vol1`

Source-library entry ids:

- `entry_bazi_general_xinpai_essence_part2_pdf`
- `entry_bazi_general_xingming_shuozheng_vol1_pdf`

Promoted candidate ids:

- `candidate_bazi_general_xinpai_essence_pattern_strength_001`
- `candidate_bazi_general_xingming_shuozheng_branch_interaction_001`

Formal evidence ids:

- `bazi_general_xinpai_essence_pattern_strength_001`
- `bazi_general_xingming_shuozheng_branch_interaction_001`

Boundary checks:

- `followup_selection_items_loaded`: `passed`
- `cluster_source_selection_references_valid`: `passed`
- `source_paths_are_relative`: `passed`
- `selected_clusters_only`: `passed`
- `source_library_entries_registered`: `passed`
- `013_candidates_promoted`: `passed`
- `012_evidence_promoted`: `passed`
- `case_formula_clusters_remain_deferred`: `passed`
- `sensitive_clusters_remain_risk_gated`: `passed`
- `raw_materials_not_mutated`: `passed`

Guardrails:

- Followup selection adds only ordinary-risk bounded sources.
- All locators remain weak page-level placeholders until later transcription.
- Case, formula, and sensitive clusters remain deferred or risk-gated.
- Raw external materials are not moved, converted, or rewritten.

## 015 Raw Text Next Cycle Gated Cluster Review Prep

This prep layer reviews the next-cycle gated clusters at cluster level only. It
opens the ordinary case and formula clusters for later bounded source selection,
keeps the sensitive-topic cluster behind risk review, and performs no
source-library, 013, or 012 mutation.

- Prep id: `015-raw-text-next-cycle-gated-cluster-review-prep`
- `gated-cluster-review-prep-status=gated_cluster_review_prep_completed`
- `gated-cluster-review-prep-items=3`
- `selected-for-source-selection=2`
- `risk-review-required=1`
- `deferred-after-prep=0`
- `source-library-mutation-authorized=false`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-raw-text-next-cycle-gated-ordinary-source-selection`

Prepared ordinary gated items:

- `gated_prep_case_collection_boundary_001`
- `gated_prep_practical_formula_boundary_001`

Risk-review items:

- `gated_prep_sensitive_topic_boundary_001`

Boundary checks:

- `gated_prep_items_loaded`: `passed`
- `source_selection_references_valid`: `passed`
- `case_formula_clusters_prepared_only`: `passed`
- `sensitive_cluster_stays_risk_review`: `passed`
- `no_source_library_mutation`: `passed`
- `no_013_012_mutation`: `passed`
- `raw_materials_not_mutated`: `passed`

Guardrails:

- Gated prep is cluster-level planning metadata only.
- Case and formula clusters may proceed only to bounded source selection.
- Sensitive-topic material remains behind risk review.
- No source-library, 013, or 012 mutation is performed in this prep step.
- Raw external materials are not moved, converted, or rewritten.

## 015 Raw Text Next Cycle Gated Ordinary Source Selection

This selection layer advances the two prepared ordinary gated clusters from cluster-level prep into bounded source-level registration. It selects one case-collection PDF and one practical-formula PDF, keeps the sensitive-topic cluster behind risk review, and records weak-locator source-library, 016/017, 013, and 012 metadata without mutating external raw materials.

- Selection id: `015-raw-text-next-cycle-gated-ordinary-source-selection`
- `gated-ordinary-source-selection-status=gated_ordinary_source_selection_completed`
- `gated-ordinary-source-selection-items=2`
- `selected-for-registration=2`
- `registered-source-entries=2`
- `candidate-extracts=2`
- `formal-evidence=2`
- `source-library-mutation-authorized=true`
- `downstream-mutation-authorized=true`
- `next-material-entry=015-raw-text-next-cycle-gated-ordinary-followup-selection`

Selected ordinary gated items:
- `gated_ordinary_source_mingzao_chunqiu_case_collection`
- `gated_ordinary_source_sizhu_yuce_yaojue_formula`

Registered source-library entries:
- `entry_bazi_general_mingzao_chunqiu_case_pdf`
- `entry_bazi_general_sizhu_yuce_yaojue_pdf`

Promoted 013 candidates:
- `candidate_bazi_general_mingzao_chunqiu_luck_cycle_001`
- `candidate_bazi_general_sizhu_yuce_yaojue_pattern_strength_001`

Formal 012 evidence units:
- `bazi_general_mingzao_chunqiu_luck_cycle_001`
- `bazi_general_sizhu_yuce_yaojue_pattern_strength_001`

Sensitive items retained for risk review:
- `gated_prep_sensitive_topic_boundary_001`

Boundary checks:
- `gated_ordinary_selection_items_loaded`: `passed`
- `gated_prep_references_valid`: `passed`
- `source_paths_are_relative`: `passed`
- `ordinary_gated_clusters_only`: `passed`
- `source_library_entries_registered`: `passed`
- `013_candidates_promoted`: `passed`
- `012_evidence_promoted`: `passed`
- `sensitive_cluster_remains_risk_review`: `passed`
- `raw_materials_not_mutated`: `passed`

Guardrails:
- Only two ordinary gated source-level records are selected in this pass.
- Sensitive-topic material stays behind risk review.
- Weak locators are accepted only as preparation metadata.
- External raw materials are not moved, converted, or rewritten.

## 015 Raw Text Next Cycle Gated Ordinary Followup Selection

This followup layer selects the next ordinary source-level records from the already prepared case/formula gated clusters. It references the first ordinary selection to avoid duplicated paths, keeps the sensitive-topic cluster behind risk review, and records weak-locator source-library, 016/017, 013, and 012 metadata without mutating external raw materials.

- Selection id: `015-raw-text-next-cycle-gated-ordinary-followup-selection`
- `gated-ordinary-followup-selection-status=gated_ordinary_followup_selection_completed`
- `gated-ordinary-followup-selection-items=2`
- `selected-for-registration=2`
- `registered-source-entries=2`
- `candidate-extracts=2`
- `formal-evidence=2`
- `source-library-mutation-authorized=true`
- `downstream-mutation-authorized=true`
- `next-material-entry=015-raw-text-next-cycle-gated-ordinary-final-selection`

Selected ordinary gated followup items:
- `gated_ordinary_followup_source_bazi_baijue_case_collection`
- `gated_ordinary_followup_source_mingli_mijue_formula`

Prior ordinary gated selection items:
- `gated_ordinary_source_mingzao_chunqiu_case_collection`
- `gated_ordinary_source_sizhu_yuce_yaojue_formula`

Registered source-library entries:
- `entry_bazi_general_bazi_baijue_case_pdf`
- `entry_bazi_general_mingli_mijue_pdf`

Promoted 013 candidates:
- `candidate_bazi_general_bazi_baijue_ten_god_001`
- `candidate_bazi_general_mingli_mijue_branch_interaction_001`

Formal 012 evidence units:
- `bazi_general_bazi_baijue_ten_god_001`
- `bazi_general_mingli_mijue_branch_interaction_001`

Sensitive items retained for risk review:
- `gated_prep_sensitive_topic_boundary_001`

Boundary checks:
- `gated_ordinary_followup_items_loaded`: `passed`
- `gated_prep_references_valid`: `passed`
- `prior_selection_references_valid`: `passed`
- `source_paths_are_relative`: `passed`
- `prior_selected_paths_not_duplicated`: `passed`
- `ordinary_gated_clusters_only`: `passed`
- `source_library_entries_registered`: `passed`
- `013_candidates_promoted`: `passed`
- `012_evidence_promoted`: `passed`
- `sensitive_cluster_remains_risk_review`: `passed`
- `raw_materials_not_mutated`: `passed`

Guardrails:
- Only two ordinary gated followup source-level records are selected.
- Previously selected ordinary gated paths are not duplicated.
- Sensitive-topic material stays behind risk review.
- Weak locators are accepted only as preparation metadata.
- External raw materials are not moved, converted, or rewritten.

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
