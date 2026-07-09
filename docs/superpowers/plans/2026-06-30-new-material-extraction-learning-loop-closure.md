# 017 New Material Extraction Learning Loop Closure

## Goal

Complete a long-goal closure checkpoint for the current new-material extraction
and learning loop. The checkpoint starts from the current
`015-raw-text-next-cycle-source-selection` handoff marker, confirms that the
already selected raw-text next-cycle surfaces have progressed through identity
review, registration, preparation reading, 017 authorization audit, explicit
013/012 gate routing, and external inventory refresh confirmation, and then
hands the next session to an explicit authorization or new-material intake
decision.

## Constraints

- Do not move, rewrite, convert, OCR, or parse external raw materials.
- Do not create new 013 candidate extracts, review decisions, promotion batches,
  or 012 formal evidence.
- Treat existing 013/012 records as historical counts only.
- Keep the checkpoint deterministic over tracked JSON metadata.
- Keep the next user-facing target explicit.

## Work Plan

- [x] Add failing tests for the loop-closure item, summary, Markdown rendering,
  docs sync, quickstart marker, and public function exports.
- [x] Add a tracked closure item that links source-selection, sensitive reading,
  017 authorization audit, explicit routing, and inventory confirmation.
- [x] Implement model, loader validation, summary construction, renderer, and
  quality-gate scanning for the closure item.
- [x] Update maintainer docs and the 017 quickstart continuation marker.
- [x] Run quality gates, focused tests, full tests, whitespace check, and commit.

## Expected Next Goal

After this closure lands, the next goal should be
`013-explicit-candidate-review-or-new-material-intake`: either explicitly
authorize downstream 013/012 work, or add/choose a genuinely new material intake
surface before restarting 015 source selection.
