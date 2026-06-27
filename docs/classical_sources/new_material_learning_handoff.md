# New Material Learning Handoff

Updated: 2026-06-27

This handoff summarizes the completed local-only new-material reading and
learning pass. It is a maintainer entrypoint for continuing work after the
source-window locator review, learning-closure pass, 017 sync, and
candidate/formal evidence boundary audit, plus the Markdown Batch 005
risk-review routing pass and risk-review prerequisite sweep.

## Completed Checkpoints

- Source-window locator review closed the current review-note evidence surface:
  `source-window-review-note-items=57`, `page-locators=44`,
  `chapter-locators=11`.
- Manual review closure retained the 11 chapter locators only where rendered
  review could not find a reliable topic page or safety boundary page.
- Learning closure added explicit closure notes to every retained chapter
  source window: `retained-chapter-learning-closed=11`.
- 017 learning-reference sync recorded that selected ready learning inputs
  remain stable: `selected-ready-learning-notes=14`, `next_action_ids=7`.
- The risk-review prerequisite sweep is closed:
  `planned-risk-review-actions=0`, `completed-risk-review-actions=4`.
- Candidate/formal evidence boundary audit confirmed the learning closure did
  not create downstream evidence changes: `formal_evidence_delta=0`.

Primary detailed references:

- [source_ref_quality_audit.md](source_ref_quality_audit.md)
- [learning_reference_curation.md](learning_reference_curation.md)
- [2026-06-27-learning-closure-notes.md](../superpowers/plans/2026-06-27-learning-closure-notes.md)
- [2026-06-27-017-learning-closure-sync.md](../superpowers/plans/2026-06-27-017-learning-closure-sync.md)
- [2026-06-27-candidate-formal-boundary-audit.md](../superpowers/plans/2026-06-27-candidate-formal-boundary-audit.md)
- [2026-06-27-markdown-batch-005-risk-review-routing.md](../superpowers/plans/2026-06-27-markdown-batch-005-risk-review-routing.md)
- [2026-06-27-risk-review-prerequisite-sweep.md](../superpowers/plans/2026-06-27-risk-review-prerequisite-sweep.md)

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
- `next_action_ids=7`
- `planned-risk-review-actions=0`
- `completed-risk-review-actions=4`
- `017-applied-decisions=28`
- `017-create-candidate-decisions=27`

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
- Current 015 queue coverage is complete: all 16 queue ids are present in 016
  package snapshots, and the 4 formerly planned risk-review prerequisite
  actions are completed. The next local work should start from
  `next-learning-note-start=017-draft-learning-reference-notes`.

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
`next-learning-note-start=017-draft-learning-reference-notes`, processes the
seven remaining draft learning notes, and carries any candidate-facing change
through the same bounded path:

1. 017 draft learning-note review and closure.
2. Candidate-intake decision audit without creating new formal evidence.
3. 013 candidate/review/promotion work only if explicitly requested.
4. Candidate/formal evidence boundary audit before any promotion work.

## Guardrails

- Do not mutate root PDFs, root `Markdown/`, `资料原文/`, or `资料整理/`.
- Do not create candidates, review decisions, promotion batches, or formal evidence unless explicitly requested.
- Do not promote retained chapter learning closures without source-specific
  transcription or page-level proof.
- Do not push remote work from this handoff.
