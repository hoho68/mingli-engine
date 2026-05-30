# Source Intake Progress

This document tracks reviewed source-intake progress for the 013 workflow.

Root PDF files and the root `Markdown/` directory are external preparation
materials. Do not move, delete, convert, or commit those materials unless the
user explicitly asks for that action.

Related maintainer references:

- [README.md](README.md): overall classical source review workflow.
- [source_library.md](source_library.md): 014 source registration, priority,
  batch planning, and value summaries.
- [materials_audit.md](materials_audit.md): 015 local-material inventory,
  preparation readiness, and next-action queue before candidate extraction.

## Audit Links

- Duplicate candidates stay in the intake queue with `duplicate_of` and a
  rejected review decision instead of being deleted.
- Conflict-linked candidates use `related_conflict_ids` that refer to reviewed
  012 source conflicts.
- Gap-linked candidates use `related_gap_ids` derived from the reviewed source
  corpus, so unresolved coverage is visible before promotion.
- Rejected and blocked candidates must keep durable reasons that explain why
  the material is not promotion-ready.
- 015 materials-audit queue items are pre-intake planning records. They must be
  converted into 013 candidate extracts and review decisions before any later
  promotion can occur.

## Current Computed Snapshot

Computed with `build_intake_progress_report()` after US4 implementation:

- Source material preparation: `partially_reviewed=7`, `indexed=1`,
  `not_started=1`.
- Candidate status: `pending_review=1`, `returned=1`, `approved=1`,
  `rejected=2`, `blocked=1`.
- Risk tiers: `sensitive=3`, `high_risk=2`, `ordinary=1`.
- Rule families: `blind_image_method=4`, `high_risk_signal=1`,
  `pattern_strength=1`.
- Promotion readiness: `approved_not_promoted=0`.
- Audit links: `duplicate_candidates=1`, `conflict_link_count=1`,
  `gap_link_count=1`.
- Intake quality failures: none.

## Next Review Queues

- Pending review: `candidate_northeast_blind_image_001`.
- Returned for revision: `candidate_blind_life_manual_gap_001`.
- Approved and already batched: `candidate_life_death_boundary_001`.
- Rejected or blocked audit records:
  `candidate_mingxue_golden_voice_scope_001`,
  `candidate_blind_school_secret_blocked_001`, and
  `candidate_northeast_blind_image_duplicate_001`.
