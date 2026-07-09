# Markdown Batch 005 Risk Review Routing Plan

Date: 2026-06-27

Goal: Continue the local-only new-material learning chain from
`next-new-material-start=015-materials-audit-next-action-queue` by routing
Markdown Batch 005 as prerequisite-only risk-review work through 016 and 017,
without creating extraction tasks, candidates, review decisions, promotion
batches, or formal evidence.

## Scope

- Select `queue_markdown_source_batch_005_risk_review` from the 015 queue.
- Add `package_next_candidates_004` as a planned 016 package with no selected
  extraction tasks.
- Add `backlog_markdown_batch_005_risk_review_001` as the 016 prerequisite
  backlog record.
- Add `action_markdown_batch_005_risk_review_001` as the 017 prerequisite
  action note.
- Update 016/017 documentation, quickstart snapshot, and the new-material
  handoff.
- Preserve candidate/formal evidence boundary counts.

## Verification

- Add failing tests first for the 015 -> 016 -> 017 trace and boundary counts.
- Run focused 016 and 017 tests after data/document updates.
- Validate changed JSON files.
- Run package and learning-reference quality summaries.
- Run `git diff --check`.
- Run the full pytest suite before commit.

## Completion Checklist

- [x] Confirmed target queue item and current absence from 016/017 seed data.
- [x] Added red tests for 016 backlog routing and 017 prerequisite action.
- [x] Added 016 package/backlog and 017 action note seed data.
- [x] Updated tests and docs to the new snapshot counts.
- [x] Ran focused and full verification.
- [x] Created a local commit and documented the next long goal.
