# Learning Reference Curation

017 learning reference curation stores maintainer metadata for turning the 016
extraction queue intake package into source-backed study notes, candidate
intake decisions, and prerequisite action notes.

Related maintainer references:

- [README.md](README.md): overall classical source review workflow.
- [intake.md](intake.md): 013 candidate-intake workflow that may later receive
  explicitly approved candidate records.
- [source_library.md](source_library.md): 014 source-library entries used by
  upstream task traceability.
- [materials_audit.md](materials_audit.md): 015 audit records, readiness
  findings, alignment findings, and next-action queue.
- [extraction_queue_intake.md](extraction_queue_intake.md): 016 package,
  extraction task, candidate draft slot, and prerequisite backlog source.
- [coverage.md](coverage.md): formal 012 evidence coverage snapshot used by
  reports.

## Current Boundary

Learning reference notes, learning points, candidate-intake decisions, and
prerequisite action notes are learning/reference metadata until a maintainer
explicitly applies a selected `create_candidate` decision. Applying a decision
may create a 013 candidate extract in `pending_review` status, but it still does
not create review decisions, promotion batches, approved evidence units, or
formal report evidence.

Root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external
preparation materials. The 017 workflow may reference tracked metadata derived
from earlier workflows, but it must not move, delete, convert, rewrite, or
commit those external materials unless explicitly requested.

## Initial Setup Status

US1 creates learning reference notes from the current selected 016 ready
extraction tasks:

- `note_northeast_blind_peak_001` traces
  `task_northeast_blind_peak_extract_001` to
  `material_northeast_blind_peak_pdf`, preserves the blind image-method overlap
  warnings, and stays in `draft` status.
- `note_mingli_true_formula_teacher_001` traces
  `task_mingli_true_formula_teacher_extract_001` to
  `material_mingli_true_formula_teacher_pdf` and stays in `draft` status.
- `note_duan_plain_mingxue_outline_001` traces
  `task_duan_plain_mingxue_outline_extract_001` to
  `material_duan_plain_mingxue_outline_pdf` and stays in `draft` status.
- `note_mingxue_golden_voice_001` traces
  `task_mingxue_golden_voice_extract_001` to
  `material_mingxue_golden_voice_pdf`, preserves the rejected broad-scope
  overlap warning, and stays in `draft` status.
- `note_fortune_reading_hongfu_qitian_001` traces
  `task_fortune_reading_hongfu_qitian_extract_001` to
  `material_fortune_reading_hongfu_qitian_pdf` and stays in `draft` status.

US2 adds five learning points and five candidate-intake decisions. These records
plan candidate intake before any 013 mutation happens.

US3 adds prerequisite action notes for the current non-ready 016 backlog records.
These actions keep registration, preparation, locator-review, risk-review,
deferred, and blocked-source work visible
without turning the underlying 015 queue items into learning points or candidate
intake decisions.

Phase 6 applies the selected
`decision_mingli_pattern_strength_001` create-candidate decision into 013 as
`candidate_mingli_pattern_strength_017_001`. The new candidate is
`pending_review`; no review decision, promotion batch, or formal evidence unit
is created.

## Learning Note Boundary

Learning notes must come from 016 extraction tasks, not prerequisite backlog
records. Loading validates links to:

- 016 extraction work packages and extraction tasks.
- 015 queue items and audit records.
- 014 source-library entries.
- 013 source materials and existing overlap candidate ids.

Learning notes must keep at least one learning point id as a planning handle,
preserve 016 overlap candidate ids, and reject unknown overlap candidates.

Quality validation rejects copied-passage markers, extracted-meaning leakage,
review-state leakage, promotion-state leakage, report-evidence wording,
absolute outcome language, exact death or lifespan language, and prohibited
high-risk instruction wording.

## Candidate-Intake Decision Boundary

Learning points must reference existing learning notes, stay within the note's
target rule families and risk boundary, keep a source locator or locator
requirement, and include uncertainty plus limitation language for sensitive and
high-risk material.

Candidate-intake decisions must reference existing learning points and 013
source materials. `create_candidate` is allowed only for `ready` learning
points, and the named candidate id remains planned metadata until an explicit
candidate-application step is requested. `reuse_existing` and
`avoid_duplicate` decisions must name existing overlap candidate ids.

Candidate-intake decision records now:

- `decision_northeast_blind_image_001`: applied as `reuse_existing`, pointing
  to `candidate_northeast_blind_image_001` while preserving
  `candidate_northeast_blind_image_duplicate_001` as a rejected duplicate
  overlap.
- `decision_mingli_pattern_strength_001`: `create_candidate` for
  `lp_mingli_pattern_strength_001`, applied as
  `candidate_mingli_pattern_strength_017_001` in 013 with `pending_review`
  status.
- `decision_duan_ten_god_relation_001`: applied as `create_candidate`,
  creating `candidate_duan_ten_god_relation_017_001`.
- `decision_mingxue_five_element_balance_001`: applied as `create_candidate`,
  creating `candidate_mingxue_five_element_balance_017_001` while preserving
  `candidate_mingxue_golden_voice_scope_001` as an overlap warning.
- `decision_hongfu_remedy_boundary_001`: applied as `create_candidate`,
  creating `candidate_hongfu_remedy_boundary_017_001`.

All created candidates are `pending_review`; none are approved, promoted, or
formal report evidence.

## Prerequisite Action Boundary

Prerequisite action notes must reference existing 016 prerequisite backlog
records, the owning 016 package, the originating 015 queue item, and the
originating 015 audit record. Action notes preserve the backlog record's
missing prerequisites, recommended action, risk boundary, and status.

Current US3 action notes:

- `action_markdown_batch_001_registration_001`: registration action for
  `backlog_markdown_batch_001_registration_001`, requiring
  `source_library_registration` before extraction.
- `action_blind_life_manual_risk_review_001`: risk-review action for
  `backlog_blind_life_manual_risk_review_001`, keeping high-risk aphoristic
  material outside candidate extraction until boundary review is complete.
- `action_blind_school_secret_blocked_001`: blocked action for
  `backlog_blind_school_secret_blocked_001`, requiring source-access and
  quotation-boundary clarification before any extraction work.
- `action_markdown_batch_002_registration_001` and
  `action_markdown_batch_003_registration_001`: registration actions requiring
  source-library registration before extraction.
- `action_immortal_fortune_jianghu_secret_risk_review_001`,
  `action_life_death_book_100_pages_risk_review_001`, and
  `action_markdown_batch_005_risk_review_001`: risk-review actions keeping
  high-risk materials outside extraction until boundary review is complete.
- `action_markdown_batch_004_locator_review_001`: locator-review action for a
  possible edition variant.
- `action_source_processing_status_deferred_001`: deferred action for workflow
  metadata that is not source text.
- `action_knowledge_skeleton_preparation_001`: preparation action for an
  aggregate skeleton that needs component source review.

Risk-review, deferred, and blocked action notes cannot become learning points,
candidate extracts, review decisions, promotion batches, approved evidence
units, or formal report evidence. They remain prerequisite work until a future
workflow resolves the missing prerequisite and creates a new ready queue item.

## Current Incremental Snapshot

- Learning reference notes: `draft=5`.
- Learning points: `duplicate_review=1`, `ready=4`.
- Candidate decisions: `reuse_existing=1`, `create_candidate=4`,
  `status:applied=5`.
- Prerequisite actions: `registration=3`, `risk_review=4`,
  `locator_review=1`, `preparation=1`, `deferred=1`, `blocked=1`,
  `status:planned=9`, `status:deferred=1`, `status:blocked=1`.
- Candidate-ready count: `4`.
- Risk tier counts: `ordinary=8`, `sensitive=9`, `high_risk=4` across notes,
  learning points, and prerequisite actions.
- Target rule family counts: `blind_image_method=1`,
  `branch_interaction=1`, `pattern_strength=4`,
  `useful_god_candidate=1`, `luck_cycle=1`, `ten_god_relation=2`,
  `five_element_balance=1`, and `remedy_boundary=1`.
- Overlap warnings: `7`.
- Formal evidence delta: `0`.
- Applied 013 candidates:
  `candidate_mingli_pattern_strength_017_001`,
  `candidate_duan_ten_god_relation_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, and
  `candidate_hongfu_remedy_boundary_017_001`; all are `pending_review`.

## Phase C Source Disposition Snapshot

The current 015 audit covers 16 material groups. All 16 now have an explicit
015 queue or backlog state:

- 5 `extraction_ready` queue items.
- 3 `registration_backlog` queue items.
- 4 `risk_review_backlog` queue items.
- 2 `preparation_backlog` queue items.
- 2 `blocked_backlog` queue items.

The current 016/017 package intentionally consumes the first bounded work
surface from that queue:

- 5 ready items are 016 extraction tasks and 017 learning reference notes:
  `Northeast Blind Peak`, `Mingli True Formula Teacher`, and
  `Duan Plain Mingxue Outline`, `Mingxue Golden Voice`, and
  `Fortune Reading Hongfu Qitian`.
- Those five notes have 5 learning points and 5 candidate-intake decisions; one
  decision reuses an existing pending candidate and four decisions are applied
  as pending 013 candidates.
- 11 non-ready items are 016 prerequisite backlog records or 017 prerequisite
  action notes: `Markdown Source Batch 001`, `Markdown Source Batch 002`,
  `Markdown Source Batch 003`, `Blind Life Manual`,
  `Immortal Fortune Jianghu Secret`, `Life Death Book 100 Pages`,
  `Markdown Source Batch 005`, `Markdown Source Batch 004`,
  `Blind School Secret`, `Source Processing Status`, and
  `Knowledge Skeleton`.

No audited material is left without a 016/017 disposition: ready materials are
learning-reference inputs, and non-ready materials are prerequisite work.

Quick validation command:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.learning_reference_curation import build_learning_reference_progress_summary, validate_learning_reference_quality; print(build_learning_reference_progress_summary()); print(validate_learning_reference_quality())"
```
