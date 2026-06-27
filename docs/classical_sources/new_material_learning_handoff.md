# New Material Learning Handoff

Updated: 2026-06-27

This handoff summarizes the completed local-only new-material reading and
learning pass. It is a maintainer entrypoint for continuing work after the
source-window locator review, learning-closure pass, 017 sync, draft
learning-note closure, candidate/formal evidence boundary audit, and
authorization audit packet, plus the Markdown Batch 005 risk-review routing
pass, risk-review prerequisite sweep, 015 queue refresh, and external material
inventory refresh, and raw text materials folder risk triage.

## Completed Checkpoints

- Source-window locator review closed the current review-note evidence surface:
  `source-window-review-note-items=57`, `page-locators=44`,
  `chapter-locators=11`.
- Manual review closure retained the 11 chapter locators only where rendered
  review could not find a reliable topic page or safety boundary page.
- Learning closure added explicit closure notes to every retained chapter
  source window: `retained-chapter-learning-closed=11`.
- 017 learning-reference sync recorded that selected ready learning inputs
  remain stable: `selected-ready-learning-notes=14`.
- Draft learning-note closure closed the remaining seven 017 learning-note
  handles: `closed-draft-learning-notes=7`, `next_action_ids=0`.
- The risk-review prerequisite sweep is closed:
  `planned-risk-review-actions=0`, `completed-risk-review-actions=4`.
- Candidate/formal evidence boundary audit confirmed the learning closure did
  not create downstream evidence changes: `formal_evidence_delta=0`.
- Authorization audit packet confirms downstream work is selectable only after
  explicit user authorization:
  `authorization-status=ready_for_explicit_downstream_authorization`,
  `downstream-mutation-authorized=false`.
- 015 coverage-aware queue refresh excludes the 16 queue ids already covered by
  016/017 and exposes the newly registered raw text corpus triage item:
  `queue-refresh-status=uncovered_queue_items_available`,
  `refreshed-next-action-ids=1`.
- 015 external material inventory refresh registered the Life Death Book
  Markdown extract and the raw text corpus triage backlog:
  `external-inventory-status=scoped_metadata_registered`,
  `new-015-representations=2`, `new-015-queue-items=1`.
- 015 raw text materials folder risk triage split `资料原文/文本类/` into 11
  exclusive inventory-level groups: `raw-text-total-files=1139`,
  `raw-text-priority-candidates=832`, `risk-review-groups=3`,
  `deferred-groups=6`.

Primary detailed references:

- [source_ref_quality_audit.md](source_ref_quality_audit.md)
- [learning_reference_curation.md](learning_reference_curation.md)
- [2026-06-27-learning-closure-notes.md](../superpowers/plans/2026-06-27-learning-closure-notes.md)
- [2026-06-27-017-learning-closure-sync.md](../superpowers/plans/2026-06-27-017-learning-closure-sync.md)
- [2026-06-27-candidate-formal-boundary-audit.md](../superpowers/plans/2026-06-27-candidate-formal-boundary-audit.md)
- [2026-06-27-markdown-batch-005-risk-review-routing.md](../superpowers/plans/2026-06-27-markdown-batch-005-risk-review-routing.md)
- [2026-06-27-risk-review-prerequisite-sweep.md](../superpowers/plans/2026-06-27-risk-review-prerequisite-sweep.md)
- [2026-06-27-draft-learning-note-closure.md](../superpowers/plans/2026-06-27-draft-learning-note-closure.md)
- [2026-06-27-learning-reference-authorization-audit.md](../superpowers/plans/2026-06-27-learning-reference-authorization-audit.md)
- [2026-06-27-015-queue-refresh.md](../superpowers/plans/2026-06-27-015-queue-refresh.md)
- [2026-06-27-external-material-inventory-refresh.md](../superpowers/plans/2026-06-27-external-material-inventory-refresh.md)
- [2026-06-28-raw-text-materials-folder-risk-triage.md](../superpowers/plans/2026-06-28-raw-text-materials-folder-risk-triage.md)

## Current Frozen Snapshot

Source-window and locator state:

- `source-window-review-note-items=57`
- `page-locators=44`
- `chapter-locators=11`
- `retained-chapter-learning-closed=11`
- `learning-paraphrase-ready=4`
- `policy-boundary-retained=5`
- `safety-boundary-retained=2`

017 learning-reference state:

- `selected-ready-learning-notes=14`
- `closed-draft-learning-notes=7`
- `next_action_ids=0`
- `planned-risk-review-actions=0`
- `completed-risk-review-actions=4`
- `017-applied-decisions=28`
- `017-create-candidate-decisions=27`

Authorization Audit Packet:

- `authorization-status=ready_for_explicit_downstream_authorization`
- `downstream-mutation-authorized=false`
- `017-notes-closed=14`
- `017-next-action-ids=0`
- `012-boundary-leakage=0`
- `next-downstream-entry=013-explicit-candidate-review-or-015-queue-refresh`

015 Queue Refresh:

- `queue-refresh-status=covered_or_completed_queue_exhausted`
- `015-queue-items=17`
- `016-covered-queue-items=16`
- `015-local-completed-queue-items=1`
- `uncovered-queue-items=0`
- `refreshed-next-action-ids=0`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-liang-bazi-core-source-selection`

015 External Material Inventory Refresh:

- `external-inventory-status=scoped_metadata_registered`
- `external-entries=31`
- `new-015-representations=2`
- `new-015-queue-items=1`
- `untracked-material-entries=0`
- `excluded-work-artifacts=3`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-raw-text-materials-folder-risk-triage`

015 Raw Text Materials Folder Risk Triage:

- `raw-text-triage-status=triage_completed`
- `raw-text-total-files=1139`
- `raw-text-priority-candidates=832`
- `raw-text-triage-groups=11`
- `risk-review-groups=3`
- `deferred-groups=6`
- `downstream-mutation-authorized=false`
- `next-material-entry=015-liang-bazi-core-source-selection`

013 and 012 boundary state:

- `013-candidate-extracts=36`
- `013-review-decisions=36`
- `013-promotion-batches=25`
- `012-formal-evidence-units=92`
- `formal_evidence_delta=0`

## Continuation Entry Points

- Start from this file for orientation.
- Use [learning_reference_curation.md](learning_reference_curation.md) for the
  017 note, decision, prerequisite, and boundary audit details.
- Use [source_ref_quality_audit.md](source_ref_quality_audit.md) when deciding
  whether a retained chapter locator needs future transcription.
- Use [extraction_queue_intake.md](extraction_queue_intake.md) and
  [materials_audit.md](materials_audit.md) when choosing the next ready source
  or prerequisite queue item.
- `next-new-material-start=015-materials-audit-next-action-queue`.
- Current 015 queue coverage has no uncovered action after excluding 16
  016-covered ids and the locally completed
  `queue_raw_text_materials_folder_triage`. The 4 formerly planned risk-review
  prerequisite actions are completed, and 017 now has no active
  `next_action_ids`.
- `next-material-entry=015-liang-bazi-core-individual-review`.
- 015 Liang Bazi Core Source Selection is completed:
  `source-selection-status=source_selection_completed`,
  `source-selection-items=12`, `existing-batch-covered=8`,
  `selected-for-individual-review=2`, `variant-review-required=1`,
  `sensitive-boundary-deferred=1`,
  `downstream-mutation-authorized=false`, and
  `next-material-entry=015-liang-bazi-core-individual-review`.
- Selected individual review ids:
  `liang_tianyuan_wuxian_commentary` and
  `liang_yushi_yongshen_ciyuan`.

## Remaining Optional Precision Work

- The 9 CID-backed retained chapter source windows are learning-closed. Do
  targeted OCR or human transcription only if exact quotation, page-level proof,
  or future promotion is explicitly needed.
- The 2 Northeast retained risk-boundary source windows are safety-paraphrase
  learning notes. Keep them paraphrase-only unless a source-specific boundary
  page is identified.
- Audit automation is optional; the current test suite already locks the
  source-window closure counts, 017 sync counts, and candidate/formal evidence
  boundary counts.

## Next Long Goal

When continuing new-material work, use a long goal that starts from
`next-material-entry=015-liang-bazi-core-individual-review`. It should review
the two selected Liang cleaned-text surfaces as bounded learning/reference
planning inputs, create or adjust only 015/017 planning metadata, and keep
013/012 mutations blocked unless separately authorized.

## Guardrails

- Do not mutate root PDFs, root `Markdown/`, `资料原文/`, or `资料整理/`.
- Do not create candidates, review decisions, promotion batches, or formal evidence unless explicitly requested.
- Do not promote retained chapter learning closures without source-specific
  transcription or page-level proof.
- Do not push remote work from this handoff.
