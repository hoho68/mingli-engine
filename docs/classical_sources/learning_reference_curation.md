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

Later 017/013 sessions applied the selected create-candidate decisions into
normal 013 candidate records and then reviewed/promoted eligible candidates
through the ordinary intake and promotion path. The 017 learning-reference
metadata itself still reports `formal_evidence_delta=0`; formal report evidence
comes only from reviewed 012 evidence units.

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

Candidate-intake decision records include these first-wave examples:

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

The full seeded 017 decision set now contains `reuse_existing=1`,
`create_candidate=27`, and `status:applied=28`. Applied decisions are no
longer themselves evidence; any report-usable value comes only after the
ordinary 013 review/promotion path creates matching formal evidence units.

## Prerequisite Action Boundary

Prerequisite action notes must reference existing 016 prerequisite backlog
records, the owning 016 package, the originating 015 queue item, and the
originating 015 audit record. Action notes preserve the backlog record's
missing prerequisites, recommended action, risk boundary, and status.

Current prerequisite action notes:

- `action_blind_life_manual_risk_review_001`: completed risk-review action for
  `backlog_blind_life_manual_risk_review_001`.
- `action_blind_school_secret_blocked_001`: blocked action for
  `backlog_blind_school_secret_blocked_001`, requiring source-access and
  quotation-boundary clarification before any extraction work.
- `action_markdown_batch_003_registration_001`: deferred registration action
  for `backlog_markdown_batch_003_registration_001`.
- `action_immortal_fortune_jianghu_secret_risk_review_001`: completed
  risk-review action for
  `backlog_immortal_fortune_jianghu_secret_risk_review_001`.
- `action_life_death_book_100_pages_risk_review_001`: completed risk-review
  action for `backlog_life_death_book_100_pages_risk_review_001`.
- `action_source_processing_status_deferred_001`: deferred action for workflow
  metadata that is not source text.
- `action_markdown_batch_005_risk_review_001`: completed risk-review action for
  `backlog_markdown_batch_005_risk_review_001`.

Risk-review, deferred, and blocked action notes cannot become learning points,
candidate extracts, review decisions, promotion batches, approved evidence
units, or formal report evidence. They remain prerequisite work until a future
workflow resolves the missing prerequisite and creates a new ready queue item.

## Current Incremental Snapshot

- Learning reference notes: `candidate_intake_started=16`.
- Learning points: `duplicate_review=3`, `ready=27`, `deferred=6`.
- Candidate decisions: `reuse_existing=3`, `create_candidate=27`,
  `status:applied=30`.
- Prerequisite actions: `risk_review=4`, `blocked=1`, `deferred=2`,
  `status:completed=4`, `status:deferred=2`, `status:blocked=1`.
- Candidate-ready count: `27`.
- Candidate decision count: `30`.
- Risk tier counts: `ordinary=11`, `sensitive=44`, `high_risk=4` across notes,
  learning points, and prerequisite actions.
- Target rule family counts: `blind_image_method=2`,
  `branch_interaction=4`, `pattern_strength=10`,
  `useful_god_candidate=5`, `luck_cycle=4`, `ten_god_relation=4`,
  `five_element_balance=1`, `remedy_boundary=1`, and
  `high_risk_signal=1`.
- Overlap warnings: `9`.
- Formal evidence delta: `0`.
- Next action ids: none. The seven former draft notes are closed as
  `candidate_intake_started`, and the four risk-review prerequisite actions are
  completed outside the active action list.

## Source-Window Learning Closure Sync

The 2026-06-27 source-window learning-closure pass is now reflected in the
017 maintainer snapshot without changing 017 data schemas or promotion state.

- `selected-ready-learning-notes=19`: the 19 ready items remain selected 016
  extraction tasks and 017 learning reference notes. Here "ready" means ready
  as learning-reference input, not automatically ready for formal evidence.
- `retained-chapter-learning-closed=11`: retained chapter-level source windows
  now have explicit learning-closure notes in the extract Markdown.
- `learning-paraphrase-ready=4`: Duan retained chapter windows can be used as
  short paraphrase learning notes; targeted transcription is only needed before
  exact quotation, page-level proof, or future promotion.
- `policy-boundary-retained=5`: Hongfu remedy-boundary windows stay as policy
  paraphrase material and must not be promoted without human transcription.
- `safety-boundary-retained=2`: Northeast risk-boundary windows stay as safety
  paraphrase material unless a source-specific boundary page is identified.
- `closed-draft-learning-notes=7`: the remaining draft learning-note handles
  are closed as `candidate_intake_started` after their learning points and
  candidate-intake decisions were already applied.
- `next_action_ids=0`: no 017 learning note, candidate-intake decision, or
  prerequisite action currently needs active local handling.
- `planned-risk-review-actions=0`: no risk-review prerequisite action remains
  planned after the sweep.
- `completed-risk-review-actions=4`: Blind Life Manual, Immortal Fortune
  Jianghu Secret, Life Death Book, and Markdown Batch 005 have completed
  prerequisite boundary screening.
- `formal_evidence_delta=0`: No new candidate-intake decisions, no 013 candidate extracts, no review decisions, no promotion batches, and no formal evidence are created by this source-window sync; later authorized Bazi general preparation-reading records are counted separately in 013/012 snapshots.

Completed, blocked, or deferred prerequisite records remain outside
`next_action_ids`.
The retained source-window closures only clarify learning/reference use and
future optional transcription boundaries.

## Liang Bazi Core Individual Review

The 2026-06-28 individual-review pass completed the two selected Liang cleaned
Markdown surfaces from the source-selection packet:

- `liang_tianyuan_wuxian_commentary`: recorded as
  `note_liang_tianyuan_wuxian_individual_review_001`, with a duplicate-review
  learning point for day-master and seasonal use-god separation. It reuses
  `candidate_markdown_batch_004_pattern_strength_001`.
- `liang_yushi_yongshen_ciyuan`: recorded as
  `note_liang_yushi_yongshen_individual_review_001`, with a duplicate-review
  learning point for month-branch use-god taxonomy and interference hierarchy.
  It reuses `candidate_markdown_batch_004_useful_god_001`.

Both records are bounded 017 learning/reference metadata. They do not create
013 candidates, 013 reviews, 013 promotion batches, or 012 formal evidence.

## Candidate/Formal Evidence Boundary Audit

The candidate/formal evidence boundary audit confirms that 017 learning
records remain provenance metadata while explicitly authorized downstream work
is represented in 013 and 012.

- `017-applied-decisions=33`: 017 candidate-intake decisions remain provenance
  and planning metadata after application.
- `017-create-candidate-decisions=30`: applied create-candidate decisions map
  to existing 013 candidate extracts; the reuse decisions continue to point to
  `candidate_northeast_blind_image_001`,
  `candidate_markdown_batch_004_pattern_strength_001`, and
  `candidate_markdown_batch_004_useful_god_001`.
- `013-candidate-extracts=39`: current 013 candidate status counts are
  `promoted=36`, `rejected=2`, and `blocked=1`.
- `013-review-decisions=39`: current review decisions are `approved=36`,
  `rejected=2`, and `blocked=1`.
- `013-promotion-batches=27`: all current promotion batches are `reviewed`.
- `012-formal-evidence-units=96`: formal evidence coverage remains in the
  approved classical evidence corpus only.
- `formal_evidence_delta=0`: the 017 summary itself does not add or remove
  formal evidence.
- `learning-reference-source-refs-in-012=0`: 012 evidence does not cite
  `learning-reference:` locators.
- `candidate-id-source-refs-in-012=0`: 012 evidence source refs do not cite
  candidate ids.
- `learning-closure-source-refs-in-012=0`: 012 evidence source refs do not cite
  `learning-closure:` notes.

Maintained boundary: 017 records describe learning/provenance decisions; 013
records carry candidate, review, and promotion pipeline state; 012 evidence
units are the only formal report evidence surface.

Authorized downstream update on 2026-06-28: the returned
`candidate_blind_life_manual_gap_001` record was promoted through 013 as
`promotion_blind_life_manual_high_risk_boundary_001` and added to 012 as
`blind_life_manual_high_risk_boundary_001`. This is boundary-only high-risk
evidence; individual aphoristic claims from the source still require separate
page or heading locators before use.

## Authorization Audit Packet

The 2026-06-27 authorization audit packet is a read-only local clearance check
for choosing the next explicit downstream action. It does not authorize any
candidate, review, promotion, or formal-evidence mutation by itself.

- `authorization-status=ready_for_explicit_downstream_authorization`
- `downstream-mutation-authorized=false`
- `017-notes-closed=19`
- `017-next-action-ids=0`
- `017-applied-decisions=33`
- `013-candidate-extracts=39`
- `013-review-decisions=39`
- `013-promotion-batches=27`
- `012-formal-evidence-units=96`
- `formal_evidence_delta=0`
- `012-boundary-leakage=0`
- `next-downstream-entry=013-explicit-candidate-review-or-015-queue-refresh`

Clearance checks are all passed: 017 notes are closed, 017 has no active
`next_action_ids`, all 017 decisions are applied, 013 candidate/review/promotion
counts are aligned, 012 formal evidence has no boundary leakage, and any
downstream mutation still requires an explicit user request.

## Phase C Source Disposition Snapshot

The current 016/017 state consumes 14 selected extraction tasks as learning
reference notes and preserves 7 prerequisite backlog records as action notes.

- 14 ready items are 016 extraction tasks and 017 learning reference notes:
  five root-PDF learning notes, three Markdown batch learning notes, and six
  knowledge-skeleton learning notes.
- Those notes contain 34 learning points and 28 candidate-intake decisions.
  One decision reuses an existing candidate, 27 are create-candidate decisions,
  and 28 decisions have `status=applied`.
- 7 non-ready items remain prerequisite action notes: Blind Life Manual,
  Blind School Secret, Markdown Batch 003, Immortal Fortune Jianghu Secret,
  Life Death Book 100 Pages, Source Processing Status, and Markdown Batch 005.

Ready materials are learning-reference inputs, and non-ready materials remain
prerequisite work until a future workflow resolves their blockers.

Quick validation command:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.learning_reference_curation import build_learning_reference_progress_summary, validate_learning_reference_quality; print(build_learning_reference_progress_summary()); print(validate_learning_reference_quality())"
```
