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
- [extraction_queue_intake.md](extraction_queue_intake.md): 016 package handoff
  that prepares eligible 015 queue work for later manual 013 candidate records.
- [learning_reference_curation.md](learning_reference_curation.md): 017
  learning notes and candidate-intake planning metadata derived from ready 016
  tasks.

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
- 016 extraction tasks are still planning records. They may guide manual 013
  candidate creation later, but they are not candidate extracts, review
  decisions, promotion batches, or formal evidence.
- 017 learning reference notes start as planning records. A maintainer may
  explicitly apply a selected `create_candidate` decision into 013; that creates
  a normal pending-review candidate, not a review decision, promotion batch, or
  formal evidence unit.

## Current Computed Snapshot

Computed with `build_intake_progress_report()` after the selected Bazi general
variant registration-prep promotion:

- Source material preparation: `partially_reviewed=11`, `not_started=1`,
  `reviewed=7`.
- Candidate status: `promoted=49`, `rejected=2`, `blocked=1`.
- Risk tiers: `sensitive=27`, `ordinary=23`, `high_risk=2`.
- Rule families: `pattern_strength=12`, `useful_god_candidate=8`,
  `blind_image_method=5`, `branch_interaction=6`, `luck_cycle=5`,
  `ten_god_relation=4`, `high_risk_signal=2`,
  `five_element_balance=1`, and `remedy_boundary=1`.
- Promotion readiness: `approved_not_promoted=0`.
- Audit links: `duplicate_candidates=1`, `conflict_link_count=2`,
  `gap_link_count=1`.
- Intake quality failures: none.

## Next Review Queues

- Pending review: none.
- Returned for revision: none.
- Approved-not-promoted: none.
- Promoted: 49 candidates, including the original 017 applied candidates,
  markdown source batches 001/002/004/005, knowledge skeleton candidates,
  Bazi general source-preparation candidates, the Markdown Batch 002 extension
  candidates, selected Bazi general variant candidates for `滴天髓.pdf` and
  `穷通宝鉴/窮通寶鑒.pdf`, and
  `candidate_blind_life_manual_gap_001` as boundary-only high-risk evidence.
- Rejected or blocked audit records:
  `candidate_mingxue_golden_voice_scope_001`,
  `candidate_blind_school_secret_blocked_001`, and
  `candidate_northeast_blind_image_duplicate_001`.

The pending-review workflow sections below remain as maintainer scaffolding for
future candidate sessions. The current seeded data has no active
`pending_review` candidates.

## Pending Candidate Review Worklist

`list_pending_candidate_review_worklist()` turns the current pending queue into
review-planning items. It does not create review decisions, promotion batches,
or formal evidence.

Current worklist:

- `candidate_northeast_blind_image_001`: verify locator, review meaning,
  decide outcome, confirm uncertainty/limitation language, and review
  duplicate/reuse context.
- `candidate_mingli_pattern_strength_017_001`: verify locator, review meaning,
  replace the learning-reference locator with a source page/section/review-note
  anchor, confirm uncertainty/limitation language, and decide outcome.
- `candidate_duan_ten_god_relation_017_001`: verify locator, review meaning,
  replace the learning-reference locator with a source page/section/review-note
  anchor, and decide outcome.
- `candidate_mingxue_five_element_balance_017_001`: verify locator, review
  meaning, replace the learning-reference locator with a source
  page/section/review-note anchor, and decide outcome.
- `candidate_hongfu_remedy_boundary_017_001`: verify locator, review meaning,
  replace the learning-reference locator with a source page/section/review-note
  anchor, confirm uncertainty/limitation language, and decide outcome.

## Review Decision Packet Boundary

`list_pending_candidate_review_decision_packets()` expands the worklist into
review-decision packet metadata. The packets show which review inputs are still
needed before a maintainer writes `review_decisions.json`; they do not approve,
return, reject, block, promote, or create formal evidence.

Current packet blockers:

- `candidate_northeast_blind_image_001`: source locator verification,
  candidate-meaning verification, selected review outcome,
  uncertainty/limitation confirmation, and duplicate/reuse resolution.
- `candidate_mingli_pattern_strength_017_001`: source locator verification,
  candidate-meaning verification, selected review outcome, replacement of the
  learning-reference locator with a source page/section/review-note anchor, and
  uncertainty/limitation confirmation.
- `candidate_duan_ten_god_relation_017_001`: source locator verification,
  candidate-meaning verification, selected review outcome, and replacement of
  the learning-reference locator with a source page/section/review-note anchor.
- `candidate_mingxue_five_element_balance_017_001`: source locator
  verification, candidate-meaning verification, selected review outcome, and
  replacement of the learning-reference locator with a source
  page/section/review-note anchor.
- `candidate_hongfu_remedy_boundary_017_001`: source locator verification,
  candidate-meaning verification, selected review outcome, replacement of the
  learning-reference locator with a source page/section/review-note anchor, and
  uncertainty/limitation confirmation.

## Review Packet Summary

`build_pending_candidate_review_packet_summary()` rolls up the packet dashboard
without writing review decisions or formal evidence.

Current summary:

- Packet count: `5`.
- Candidate ids:
  `candidate_northeast_blind_image_001`,
  `candidate_mingli_pattern_strength_017_001`,
  `candidate_duan_ten_god_relation_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, and
  `candidate_hongfu_remedy_boundary_017_001`.
- Decision options: `approved=5`, `returned=5`, `rejected=5`, `blocked=5`.
- Required manual inputs: base review fields are needed for all five packets;
  `source_page_or_section_locator=4`,
  `uncertainty_and_limitation_language=3`, and
  `duplicate_or_reuse_resolution=1`.
- Approval blockers: `source_locator_not_verified=5`,
  `candidate_meaning_not_verified=5`, `review_outcome_not_selected=5`,
  `learning_reference_locator_not_replaced=4`,
  `uncertainty_limitations_not_confirmed=3`, and
  `duplicate_or_reuse_resolution_before_approval=1`.
- Boundary deltas: `review_decision_delta=0`, `formal_evidence_delta=0`.

## Pending Review Action Queue

`build_pending_candidate_review_action_queue()` converts the packet dashboard
into the next manual action per pending candidate. These queue items are
planning metadata only; they do not write review decisions, promotion batches,
or formal evidence.

Current high-priority queue:

- `candidate_northeast_blind_image_001`: `resolve_duplicate_or_reuse_context`.
  Blocking input: `duplicate_or_reuse_resolution`.
- `candidate_mingli_pattern_strength_017_001`:
  `replace_learning_reference_locator`. Blocking input:
  `source_page_or_section_locator`.
- `candidate_duan_ten_god_relation_017_001`:
  `replace_learning_reference_locator`. Blocking input:
  `source_page_or_section_locator`.
- `candidate_mingxue_five_element_balance_017_001`:
  `replace_learning_reference_locator`. Blocking input:
  `source_page_or_section_locator`.
- `candidate_hongfu_remedy_boundary_017_001`:
  `replace_learning_reference_locator`. Blocking input:
  `source_page_or_section_locator`.

## Markdown Review Checklist

`render_pending_candidate_review_action_queue_markdown()` renders the current
action queue as a stable Markdown checklist for manual review sessions. It
does not write files, review decisions, promotion batches, or formal evidence.

Current checklist summary:

- Queue items: `5`.
- Review packet count: `5`.
- Review decision delta: `0`.
- Formal evidence delta: `0`.
- First checklist item: `candidate_northeast_blind_image_001` with
  `resolve_duplicate_or_reuse_context`.
- Remaining four checklist items use `replace_learning_reference_locator`.

## Review Input Templates

`render_pending_candidate_review_input_templates_markdown()` renders fillable
review-input scaffolds for the same five pending candidates. These templates are
not review decisions; they do not write `review_decisions.json`, promotion
batches, or formal evidence.

Current template summary:

- Template count: `5`.
- Review packet count: `5`.
- Review decision delta: `0`.
- Formal evidence delta: `0`.
- Base fields for every template: `reviewer`, `reviewed_at`,
  `source_locator`, `source_quality`, `confidence`, `review_outcome`, and
  `rationale`.
- Outcome fields: `approval_limitations` for approved, `required_changes` for
  returned, and `rejection_reason` for rejected or blocked.
- Conditional fields: `duplicate_or_reuse_resolution=1`,
  `source_page_or_section_locator=4`, and
  `uncertainty_and_limitation_language=3`.
- First template:
  `review_candidate_northeast_blind_image_001` for
  `candidate_northeast_blind_image_001`.
- Remaining four templates use decision id hints matching their candidate ids:
  `review_candidate_mingli_pattern_strength_017_001`,
  `review_candidate_duan_ten_god_relation_017_001`,
  `review_candidate_mingxue_five_element_balance_017_001`, and
  `review_candidate_hongfu_remedy_boundary_017_001`.

## Review Draft Validation

`validate_pending_candidate_review_decision_draft()` and
`render_pending_candidate_review_draft_validation_markdown()` validate filled
review-input templates before a maintainer manually updates candidates and
`review_decisions.json`. The validation layer does not write review decisions,
promotion batches, candidate status changes, or formal evidence.

Current validation behavior:

- Returned drafts require `required_changes`.
- Rejected and blocked drafts require a durable `rejection_reason`.
- Approved drafts require `approval_limitations`, cannot use
  `source_quality=needs_recheck`, and must satisfy any template-specific
  conditional fields before they are ready for manual application.
- For the current pending set, approved drafts may require
  `source_page_or_section_locator`, `uncertainty_and_limitation_language`, and
  `duplicate_or_reuse_resolution` depending on the candidate.
- Validation output always reports `review_decision_delta=0` and
  `formal_evidence_delta=0`.

Example safe returned-draft validation:

- Candidate: `candidate_duan_ten_god_relation_017_001`.
- Review outcome: `returned`.
- Required manual field: `required_changes`.
- Expected validation status after that field is filled:
  `ready_for_manual_application`.

Example blocked approved-draft validation:

- Candidate: `candidate_northeast_blind_image_001`.
- Review outcome: `approved`.
- Missing fields remain blocking until `approval_limitations`,
  `uncertainty_and_limitation_language`, and
  `duplicate_or_reuse_resolution` are filled, and source quality is no longer
  `needs_recheck`.

## Review Application Guard

`build_pending_candidate_review_application_guard()` and
`render_pending_candidate_review_application_guard_markdown()` preview the
manual data changes for review-decision drafts that passed validation. The
guard does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

Current guard behavior:

- Ready drafts include a `review_decision_preview` copied from the normalized
  validated draft.
- Ready drafts include a candidate status preview from `pending_review` to the
  selected review outcome.
- Blocked drafts include missing fields and blocking issues, but no review
  decision or candidate-status preview.
- Preview deltas describe what a maintainer would manually apply; applied
  deltas remain zero.

Example ready returned-draft guard:

- Candidate: `candidate_duan_ten_god_relation_017_001`.
- Review outcome: `returned`.
- Preview review decision additions: `1`.
- Preview candidate status updates: `1`.
- Candidate status preview: `pending_review -> returned`.
- Applied review decision delta: `0`.
- Applied candidate status delta: `0`.
- Formal evidence delta: `0`.

## Review Application Packets

`build_pending_candidate_review_application_packets()` and
`render_pending_candidate_review_application_packets_markdown()` export ready
application-guard previews as copyable manual instruction packets. These
packets do not write `review_decisions.json`, do not update
`candidate_extracts.json`, do not promote candidates, and do not alter formal
evidence.

Current packet behavior:

- Exportable packets include a review-decision JSON snippet for manual append.
- Exportable packets include a candidate-status update snippet for manual
  editing.
- Exportable packets include checklist items:
  `append_review_decision_entry`, `update_candidate_status`,
  `run_source_intake_tests`, and `verify_formal_evidence_delta_zero`.
- Exportable packets include rollback notes to remove the appended review
  decision and restore the previous candidate status if manual application is
  abandoned.
- Blocked packets preserve blocking issues and do not include copyable update
  snippets.
- Applied deltas remain zero; preview deltas only describe what a maintainer
  would manually apply.

Example ready returned-draft packet:

- Candidate: `candidate_duan_ten_god_relation_017_001`.
- Review decision JSON: `decision=returned` with `required_changes`.
- Candidate status update: `pending_review -> returned`.
- Preview review decision additions: `1`.
- Preview candidate status updates: `1`.
- Applied review decision delta: `0`.
- Applied candidate status delta: `0`.
- Formal evidence delta: `0`.

## Review Application Audit Summary

`build_pending_candidate_review_application_audit_summary()` and
`render_pending_candidate_review_application_audit_summary_markdown()` summarize
the full manual-application readiness chain across templates, draft validation,
application guard previews, and application packets. The summary is read-only
planning metadata; it does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

Current summary behavior:

- Counts pending review templates, supplied drafts, validation-ready drafts,
  validation-blocked drafts, guard-ready previews, exportable packets, blocked
  packets, and candidates still missing drafts.
- Lists exportable candidates with next action
  `apply_manual_application_packet`.
- Lists blocked candidates with next action `resolve_draft_blocking_issues`.
- Lists candidates without supplied drafts with next action
  `fill_review_input_template`.
- Reports preview deltas separately from applied deltas.
- Applied review-decision, candidate-status, and formal-evidence deltas remain
  zero.

Example one-draft audit summary:

- Supplied draft: `candidate_duan_ten_god_relation_017_001` as `returned`.
- Exportable candidates: `candidate_duan_ten_god_relation_017_001`.
- Missing draft candidates:
  `candidate_northeast_blind_image_001`,
  `candidate_mingli_pattern_strength_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, and
  `candidate_hongfu_remedy_boundary_017_001`.
- Shortest next action for the exportable candidate:
  `apply_manual_application_packet`.
- Shortest next action for missing draft candidates:
  `fill_review_input_template`.

## Review Manual Action Dashboard

`build_pending_candidate_review_manual_action_dashboard()` and
`render_pending_candidate_review_manual_action_dashboard_markdown()` group the
current pending candidates by shortest next manual action and produce a
recommended processing order. The dashboard is read-only planning metadata; it
does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

Example dashboard with one exportable returned draft and one blocked approved
draft:

- `apply_manual_application_packet=1`:
  `candidate_duan_ten_god_relation_017_001`.
- `resolve_draft_blocking_issues=1`:
  `candidate_northeast_blind_image_001`.
- `fill_review_input_template=3`:
  `candidate_mingli_pattern_strength_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, and
  `candidate_hongfu_remedy_boundary_017_001`.
- Recommended processing order:
  `candidate_duan_ten_god_relation_017_001`,
  `candidate_northeast_blind_image_001`,
  `candidate_mingli_pattern_strength_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, then
  `candidate_hongfu_remedy_boundary_017_001`.
- Applied review-decision, candidate-status, and formal-evidence deltas remain
  zero.

## Review Manual Application Dry-Run Guide

`build_pending_candidate_review_manual_application_dry_run_guide()` and
`render_pending_candidate_review_manual_application_dry_run_guide_markdown()`
expand the manual action dashboard into a per-candidate execution guide. The
guide is read-only planning metadata; it does not write `review_decisions.json`,
does not update `candidate_extracts.json`, does not promote candidates, and
does not alter formal evidence.

Example dry-run guide with one exportable returned draft and one blocked
approved draft:

- `candidate_duan_ten_god_relation_017_001` is
  `ready_for_manual_application`: manual steps are
  `append_review_decision_entry` and `update_candidate_status`; post-apply
  checks are `run_source_intake_tests` and
  `verify_formal_evidence_delta_zero`; rollback notes remove the appended
  review decision and restore `returned` back to `pending_review`.
- `candidate_northeast_blind_image_001` is
  `blocked_until_draft_issues_resolved`: required inputs are
  `approval_limitations`, `uncertainty_and_limitation_language`, and
  `duplicate_or_reuse_resolution`; blocking issues include missing approval
  limitations, missing uncertainty language, missing duplicate/reuse
  resolution, and `source_quality=needs_recheck` on an approved draft.
- `candidate_mingli_pattern_strength_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, and
  `candidate_hongfu_remedy_boundary_017_001` are
  `needs_review_input_template`: each lists base review fields and the
  candidate-specific conditional locator or uncertainty inputs before draft
  validation and application guard previews can run.
- The recommended processing order remains:
  `candidate_duan_ten_god_relation_017_001`,
  `candidate_northeast_blind_image_001`,
  `candidate_mingli_pattern_strength_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, then
  `candidate_hongfu_remedy_boundary_017_001`.
- Applied review-decision, candidate-status, and formal-evidence deltas remain
  zero.

## Review Manual Application Preflight Report

`build_pending_candidate_review_manual_application_preflight_report()` and
`render_pending_candidate_review_manual_application_preflight_report_markdown()`
check manual application readiness before a human copies packet output into
tracked JSON. The report is read-only planning metadata; it does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

Example preflight report with one exportable returned draft and one blocked
approved draft:

- `candidate_duan_ten_god_relation_017_001` is ready because its
  review-decision id is unique, its candidate-status update starts from
  `pending_review`, and its expected review-decision/status deltas match the
  application packet preview.
- `candidate_northeast_blind_image_001` is blocked because the manual
  application packet is not exportable and still carries the unresolved draft
  blocking issues.
- `candidate_mingli_pattern_strength_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, and
  `candidate_hongfu_remedy_boundary_017_001` are blocked because no manual
  application packet exists until review input templates are filled and pass
  validation.
- Ready candidate count is `1`, blocked candidate count is `4`, and preview
  review-decision/status deltas are `1/1`.
- Applied review-decision, candidate-status, and formal-evidence deltas remain
  zero.

## Review Manual Application Handoff Summary

`build_pending_candidate_review_manual_application_handoff_summary()` and
`render_pending_candidate_review_manual_application_handoff_summary_markdown()`
combine the manual action dashboard, dry-run guide, and preflight report into
one human execution handoff. The summary is read-only planning metadata; it
does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

Example handoff summary with one exportable returned draft and one blocked
approved draft:

- Ready candidates: `candidate_duan_ten_god_relation_017_001`.
- Blocked candidates: `candidate_northeast_blind_image_001`.
- Missing-draft candidates:
  `candidate_mingli_pattern_strength_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, and
  `candidate_hongfu_remedy_boundary_017_001`.
- The ready Duan handoff item lists manual steps
  `append_review_decision_entry` and `update_candidate_status`, preflight
  checks `decision_id_unique`, `candidate_status_patch_matches_pending`, and
  `packet_delta_matches_preview`, post-apply checks
  `run_source_intake_tests` and `verify_formal_evidence_delta_zero`, rollback
  notes, and the expected `pending_review -> returned` status update.
- The blocked Northeast item carries the non-exportable packet blocker and
  unresolved draft issues. Missing-draft items carry template inputs as their
  next manual work.
- Applied review-decision, candidate-status, and formal-evidence deltas remain
  zero.

## Review Manual Application Readiness Ledger

`build_pending_candidate_review_manual_application_readiness_ledger()` and
`render_pending_candidate_review_manual_application_readiness_ledger_markdown()`
turn the handoff summary into an unchecked manual ledger. The ledger is
read-only planning metadata; it does not write `review_decisions.json`, does
not update `candidate_extracts.json`, does not promote candidates, and does
not alter formal evidence.

Example readiness ledger with one exportable returned draft and one blocked
approved draft:

- Ledger rows: `5`.
- Ready rows: `1`, blocked rows: `1`, missing-draft rows: `3`.
- The ready Duan row has status `ready_to_apply_manual_packet` and checkboxes
  for `confirm_decision_id_unique`,
  `confirm_candidate_status_patch_matches_pending`,
  `confirm_packet_delta_matches_preview`, `append_review_decision_entry`,
  `update_candidate_status`, `run_source_intake_tests`, and
  `verify_formal_evidence_delta_zero`.
- The blocked Northeast row has status `blocked_resolve_draft_issues` and
  checkboxes to resolve draft blocking issues, rerun validation, rerun the
  application guard, rerun the preflight report, and rerun the handoff summary.
- Missing-draft rows have status `needs_review_input_template` and checkboxes
  to fill templates, run draft validation, run the application guard, rerun the
  preflight report, and rerun the handoff summary.
- Applied review-decision, candidate-status, and formal-evidence deltas remain
  zero.

## Review Manual Application Session Packet

`build_pending_candidate_review_manual_application_session_packet()` and
`render_pending_candidate_review_manual_application_session_packet_markdown()`
compress the readiness ledger into a ready-first manual session packet. The
packet is read-only planning metadata; it does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

Example session packet with one exportable returned draft and one blocked
approved draft:

- Session id: `pending_review_manual_application_session`.
- Session scope: `ready_first_manual_application`.
- Ready action queue: one Duan action to apply the manual packet.
- Blocked follow-ups: one Northeast action to resolve draft blocking issues.
- Missing-draft follow-ups: three rows to fill review input templates.
- Post-session verification checkboxes: `run_source_intake_tests`,
  `verify_formal_evidence_delta_zero`, `rerun_readiness_ledger`, and
  `confirm_manual_changes_only`.
- Applied review-decision, candidate-status, and formal-evidence deltas remain
  zero.

## Review Manual Application Session Outcome Preview

`build_pending_candidate_review_manual_application_session_outcome_preview()`
and
`render_pending_candidate_review_manual_application_session_outcome_preview_markdown()`
preview the post-session outcome if the maintainer applies only the ready
actions from the session packet. The preview is read-only planning metadata; it
does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

Example session outcome preview with one exportable returned draft and one
blocked approved draft:

- Preview scope: `ready_actions_only`.
- Projected ready application: `candidate_duan_ten_god_relation_017_001`
  leaves `pending_review` and becomes `returned`.
- Remaining pending follow-ups:
  `candidate_northeast_blind_image_001`,
  `candidate_mingli_pattern_strength_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, and
  `candidate_hongfu_remedy_boundary_017_001`.
- Projected review-decision additions: `1`; projected candidate-status
  updates: `1`.
- Post-session next actions: rerun source-intake tests, rerun the readiness
  ledger, resolve blocked follow-ups, and fill missing draft templates.
- Applied review-decision, candidate-status, and formal-evidence deltas remain
  zero.

## Review Manual Application Post-Session Verification Report

`build_pending_candidate_review_manual_application_post_session_verification_report()`
and
`render_pending_candidate_review_manual_application_post_session_verification_report_markdown()`
compare the ready-only outcome preview with the current source-intake data after
a maintainer manually applies the ready packet. The report is read-only
planning metadata; it does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

When the current data is still the pre-application state, the report blocks the
ready Duan action with `review_decision_missing` and
`candidate_status_not_updated`. When verifying a separate post-session data
directory, pass `preview_data_dir` for the pre-session source of truth and use
`data_dir` for the post-session data being checked.

Example post-session verification after the Duan ready packet has been applied:

- Verification scope: `ready_actions_only_post_session`.
- Post-session status: `verified`.
- Ready action verification:
  `candidate_duan_ten_god_relation_017_001` has the expected returned review
  decision and actual candidate status `returned`.
- Follow-up pending verification: the Northeast, Mingli pattern strength,
  Mingxue balance, and Hongfu remedy candidates remain `pending_review`.
- Expected review-decision additions: `1`; expected candidate-status updates:
  `1`.
- Applied review-decision, candidate-status, and formal-evidence deltas remain
  zero because the verifier only reads data.

## Review Manual Application Reconciliation Dashboard

`build_pending_candidate_review_manual_application_reconciliation_dashboard()`
and
`render_pending_candidate_review_manual_application_reconciliation_dashboard_markdown()`
turn the post-session verification report into a next-action dashboard. The
dashboard is read-only planning metadata; it does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The dashboard uses this action order:

1. `append_missing_review_decision`
2. `correct_candidate_status`
3. `investigate_follow_up_mismatch`
4. `continue_follow_up_processing`
5. `verified_complete`

Current pre-application data produces one `append_missing_review_decision`
action for `candidate_duan_ten_god_relation_017_001` and four
`continue_follow_up_processing` actions for the candidates that remain
`pending_review`. If a manual application has already appended the review
decision but left the candidate status unchanged, the Duan candidate moves to
`correct_candidate_status`. If a follow-up candidate leaves `pending_review`
unexpectedly, it moves to `investigate_follow_up_mismatch`. Fully verified
ready actions move to `verified_complete`.

Applied review-decision, candidate-status, and formal-evidence deltas remain
zero because reconciliation only classifies the next human action.

## Review Manual Application Closure Packet

`build_pending_candidate_review_manual_application_closure_packet()` and
`render_pending_candidate_review_manual_application_closure_packet_markdown()`
turn the reconciliation dashboard into a final read-only closure packet for the
manual application session. The packet does not write `review_decisions.json`,
does not update `candidate_extracts.json`, does not promote candidates, and
does not alter formal evidence.

The packet separates candidates into two lanes:

- `session_closure`: verified complete candidates that can be closed for this
  manual application session.
- `carry_forward`: candidates that must move into the next manual session for a
  missing review decision, candidate-status correction, follow-up mismatch
  investigation, or normal follow-up processing.

Current pre-application data produces `carry_forward_required`: the Duan
candidate carries forward for `carry_forward_missing_review_decision`, and the
four still-pending follow-up candidates carry forward for
`carry_forward_follow_up_processing`. After the Duan ready packet is manually
applied and verified, the packet becomes `partial_closure_ready`: the Duan
candidate can close, while the four follow-up candidates carry forward.

The recommended next-session setup lists close steps first when any verified
items exist, then missing review-decision work, candidate-status corrections,
follow-up investigations, and ordinary follow-up processing. Applied
review-decision, candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Starter

`build_pending_candidate_review_manual_application_next_session_starter()` and
`render_pending_candidate_review_manual_application_next_session_starter_markdown()`
convert closure-packet carry-forward items into a read-only starter for the
next manual application session. Closed candidates are omitted from starter
items; if any verified items were present, the kickoff checklist still reminds
the maintainer to close them before continuing. The starter does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

Starter lanes:

- `missing_review_decision`: recover the ready manual application packet,
  append the missing review decision, and rerun post-session verification,
  reconciliation, and closure.
- `candidate_status_correction`: verify the review decision is present, apply
  the candidate-status patch manually, then rerun the verification chain.
- `follow_up_mismatch_investigation`: inspect unexpected follow-up status or
  review-decision changes before rerunning the verification chain.
- `follow_up_processing`: resume normal pending-review work by filling or
  revising templates, running draft validation, running the application guard,
  rerunning the manual action dashboard, and preparing the next session packet.

Current pre-application data produces one `missing_review_decision` starter
item for `candidate_duan_ten_god_relation_017_001` and four
`follow_up_processing` starter items. After the Duan item is verified and
closed, the starter omits it and only carries the four follow-up candidates
into the next session. Applied review-decision, candidate-status, and
formal-evidence deltas remain zero.

## Bazi General Next-Cycle Cluster-Source Intake


The 2026-06-28 `015-raw-text-next-cycle-followup-selection` stage added
two more ordinary-risk weak-locator candidates under explicit user authorization:

- `candidate_bazi_general_xinpai_essence_pattern_strength_001` from
  `material_bazi_general_xinpai_essence_part2_pdf`, approved by
  `review_bazi_general_xinpai_essence_pattern_strength_001` and promoted to
  `bazi_general_xinpai_essence_pattern_strength_001`.
- `candidate_bazi_general_xingming_shuozheng_branch_interaction_001` from
  `material_bazi_general_xingming_shuozheng_vol1_pdf`, approved by
  `review_bazi_general_xingming_shuozheng_branch_interaction_001` and promoted
  to `bazi_general_xingming_shuozheng_branch_interaction_001`.

These records keep weak page anchors and concise paraphrases only; raw PDFs
remain external and unchanged.

The 2026-06-28 `015-raw-text-next-cycle-cluster-source-selection` stage added
two authorized weak-locator 013 candidates:

- `candidate_bazi_general_true_spirit_useful_god_001` from
  `material_bazi_general_true_spirit_positioning_pdf`, approved by
  `review_bazi_general_true_spirit_useful_god_001` and promoted to
  `bazi_general_true_spirit_useful_god_001`.
- `candidate_bazi_general_wangdoujing_branch_interaction_001` from
  `material_bazi_general_mingli_wangdoujing_pdf`, approved by
  `review_bazi_general_wangdoujing_branch_interaction_001` and promoted to
  `bazi_general_wangdoujing_branch_interaction_001`.

Both records use `source_quality=review_note`, `confidence=weak`, and empty
short quotes. They are metadata links only; raw PDFs remain external and
unchanged.

## Review Manual Application Next-Session Packet

`build_pending_candidate_review_manual_application_next_session_packet()` and
`render_pending_candidate_review_manual_application_next_session_packet_markdown()`
compress the next-session starter into a ready-first manual session packet. The
packet is read-only planning metadata: it does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The packet groups starter items into two execution queues:

- `correction_queue`: missing review decisions, candidate-status corrections,
  and follow-up mismatch investigations that should be resolved before ordinary
  follow-up work.
- `follow_up_queue`: normal pending-review follow-up processing, including
  template fill/revision, draft validation, application guard, dashboard rerun,
  and next-session packet preparation.

The recommended processing order lists correction candidates first, preserving
the starter lane priority, then follow-up candidates. Current pre-application
data produces one correction item for
`candidate_duan_ten_god_relation_017_001` and four follow-up items. If the
Duan item is already verified and closed, it is omitted from both queues and
the packet starts with the four follow-up candidates.

The packet carries forward the starter kickoff checklist and adds a
post-session verification checklist: rerun post-session verification,
reconciliation, closure, next-session starter, and next-session packet after
manual changes. Applied review-decision, candidate-status, and formal-evidence
deltas remain zero.

## Review Manual Application Next-Session Audit Summary

`build_pending_candidate_review_manual_application_next_session_audit_summary()`
and
`render_pending_candidate_review_manual_application_next_session_audit_summary_markdown()`
summarize the closure packet, next-session starter, and next-session packet in
one read-only audit view. The summary does not write `review_decisions.json`,
does not update `candidate_extracts.json`, does not promote candidates, and
does not alter formal evidence.

Coverage checks confirm that:

- closure carry-forward candidates are represented in the starter;
- starter ordering is preserved in the packet processing order;
- correction and follow-up queues are present and counted;
- kickoff checklist coverage is available for the next manual session;
- post-session verification coverage is available after manual actions.

The shortest next actions are derived from the closure and packet state. If
verified session items exist, the first action is
`close_verified_candidate_session_items`. If correction candidates exist, the
summary starts with `apply_correction_queue_first`, then
`continue_follow_up_queue` when follow-up work remains, and finally
`rerun_post_session_verification_chain`.

Current pre-application data produces a ready audit with one correction item,
four follow-up items, complete coverage checks, and zero applied
review-decision, candidate-status, and formal-evidence deltas.

## Review Manual Application Next-Session Operator Checklist

`build_pending_candidate_review_manual_application_next_session_operator_checklist()`
and
`render_pending_candidate_review_manual_application_next_session_operator_checklist_markdown()`
turn the next-session audit summary's shortest next actions into a copyable
human operator checklist. The checklist is read-only planning metadata: it does
not write `review_decisions.json`, does not update `candidate_extracts.json`,
does not promote candidates, and does not alter formal evidence.

Each operator action includes:

- target candidates for the action;
- ready criteria that must be true before the action starts;
- an unchecked operator checklist for the manual step;
- an unchecked verification checklist for the follow-up validation;
- boundary notes preserving the planning-only role.

Current pre-application data produces three operator actions:
`apply_correction_queue_first`, `continue_follow_up_queue`, and
`rerun_post_session_verification_chain`. If verified session items exist, the
checklist starts with `close_verified_candidate_session_items` before ordinary
follow-up work. Correction targets are always listed before follow-up targets
so the maintainer does not start ordinary follow-up processing before missing
review decisions, candidate-status corrections, or mismatch investigations are
resolved.

Applied review-decision, candidate-status, and formal-evidence deltas remain
zero.

## Review Manual Application Next-Session Execution Handoff

`build_pending_candidate_review_manual_application_next_session_execution_handoff()`
and
`render_pending_candidate_review_manual_application_next_session_execution_handoff_markdown()`
condense the operator checklist into a one-page execution handoff for the next
manual session. The handoff is read-only planning metadata: it does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The handoff surfaces:

- the first manual action to run;
- target candidates for that first action;
- ready conditions copied from the operator checklist;
- blocked conditions when the operator checklist is not ready;
- the full action sequence;
- the complete target-candidate set;
- the verification chain and recommended processing order.

Current pre-application data produces a `ready_for_execution` handoff whose
first action is `apply_correction_queue_first` for
`candidate_duan_ten_god_relation_017_001`, followed by ordinary follow-up
processing and the post-session verification chain. If verified session items
already exist, the first action becomes
`close_verified_candidate_session_items` and its target candidates are listed
before the follow-up queue. Applied review-decision, candidate-status, and
formal-evidence deltas remain zero.

## Review Manual Application Next-Session Completion Criteria

`build_pending_candidate_review_manual_application_next_session_completion_criteria()`
and
`render_pending_candidate_review_manual_application_next_session_completion_criteria_markdown()`
turn the execution handoff into a read-only completion criteria sheet for the
next manual session. The criteria sheet does not write `review_decisions.json`,
does not update `candidate_extracts.json`, does not promote candidates, and
does not alter formal evidence.

The criteria sheet includes:

- done conditions for the first action, remaining action sequence,
  verification entrypoints, and zero review-decision, candidate-status, and
  formal-evidence deltas;
- blocked conditions copied from the execution handoff when the handoff is not
  ready;
- retry conditions for a failed first-action verification or a changed handoff;
- verification entrypoints copied from the execution handoff's verification
  chain;
- first action, first-action targets, target candidates, and recommended
  processing order.

Current pre-application data produces a `ready_for_completion_check` criteria
sheet whose first action is `apply_correction_queue_first`; if verified session
items are waiting, the criteria sheet instead starts with
`close_verified_candidate_session_items`. Applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Retry Planner

`build_pending_candidate_review_manual_application_next_session_retry_planner()`
and
`render_pending_candidate_review_manual_application_next_session_retry_planner_markdown()`
expand the completion criteria retry conditions into a read-only retry plan.
The planner does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The retry planner includes:

- failure entrypoints derived from each retry condition;
- retry sequence steps, ending with `rerun_completion_criteria`;
- target candidates and first-action targets;
- verification entrypoints copied from the completion criteria;
- a return-to-handoff path through the execution handoff and completion
  criteria renderers;
- recommended processing order.

Current pre-application data produces `ready_for_retry_planning` with
`first_action_verification_failed` and
`execution_handoff_stale_after_manual_changes` as failure entrypoints. The
retry plan remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Final Readiness Summary

`build_pending_candidate_review_manual_application_next_session_final_readiness_summary()`
and
`render_pending_candidate_review_manual_application_next_session_final_readiness_summary_markdown()`
combine the next-session completion criteria and retry planner into a final
read-only confirmation sheet before a maintainer starts the next manual
session. The summary does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The final readiness summary includes:

- the start gate and first action for the next manual session;
- first-action targets, target candidates, and recommended processing order;
- ready, blocked, and retry conditions from the completion criteria;
- failure entrypoints, verification entrypoints, and return-to-handoff path
  from the retry planner;
- final readiness checks that confirm criteria, retry plan, targets,
  verification entrypoints, and read-only boundaries.

Current pre-application data produces
`ready_to_start_next_manual_session` with `start_with_first_action` and
`apply_correction_queue_first`. If verified session items are waiting, the
summary instead starts with `close_verified_candidate_session_items`. The
summary remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Launch Note

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_note()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_markdown()`
condense the final readiness summary into a one-page read-only launch sheet
for the next manual execution session. The launch note does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The launch note includes:

- launch status, start gate, first command, and first-command targets;
- candidate order and target candidates for the manual session;
- abort conditions for blocked, targetless, or boundary-unsafe starts;
- return paths back through the next-session handoff, completion criteria, and
  final readiness summary;
- verification commands for focused, boundary, and full-suite checks.

Current pre-application data produces `ready_to_launch_manual_execution` with
`execute_apply_correction_queue_first` as the first command. If verified
session items are waiting, the launch note instead starts with
`execute_close_verified_candidate_session_items`. The launch note remains a
planning artifact only; applied review-decision, candidate-status, and
formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Launch Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_markdown()`
compare the final readiness summary with the manual execution launch note. The
audit verifies that the launch note covers the start gate, first command,
candidate order, abort conditions, return paths, verification commands, target
candidates, and read-only boundary. The launch audit does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The launch audit includes:

- audit status, readiness status, launch status, start gate, and first command;
- coverage checks and missing coverage for the launch note;
- boundary checks for review-decision, candidate-status, and formal-evidence
  deltas;
- candidate order, return paths, verification commands, and target candidates.

Current pre-application data produces `launch_audit_ready` with all coverage
checks marked `covered`. If verified session items are waiting, the audit still
preserves the close-first launch command and verifies that the launch note
covers it. The launch audit remains a planning artifact only; applied
review-decision, candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Launch Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_markdown()`
freeze a ready launch audit into the final read-only seal for starting the
next manual execution session. The seal does not write `review_decisions.json`,
does not update `candidate_extracts.json`, does not promote candidates, and
does not alter formal evidence.

The launch seal includes:

- seal status, audit status, launch status, start gate, and sealed first
  command;
- sealed candidate order, target candidates, and blocked reasons;
- seal checks for audit readiness, coverage, first command, verification
  commands, and zero boundary deltas;
- verification commands and rollback entrypoints.

Current pre-application data produces `sealed_for_manual_execution` with
`execute_apply_correction_queue_first` as the sealed first command. If verified
session items are waiting, the seal instead preserves
`execute_close_verified_candidate_session_items`. The launch seal remains a
planning artifact only; applied review-decision, candidate-status, and
formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Launch Runbook

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_markdown()`
expand the launch seal into a read-only manual execution runbook. The runbook
does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The launch runbook includes:

- runbook status, seal status, start gate, and first step;
- execution order containing the sealed first command, candidate order,
  focused/boundary/full validation steps, and launch-seal rerender;
- step verification commands and candidate-order checks;
- failure rollback entrypoints and post-completion review checks;
- target candidates and read-only boundary notes.

Current pre-application data produces `ready_for_manual_execution_runbook`
with `execute_apply_correction_queue_first` as the first step. If verified
session items are waiting, the runbook instead starts with
`execute_close_verified_candidate_session_items`. The launch runbook remains a
planning artifact only; applied review-decision, candidate-status, and
formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Launch Runbook Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_markdown()`
compare the launch seal with the manual execution runbook. The audit does not
write `review_decisions.json`, does not update `candidate_extracts.json`, does
not promote candidates, and does not alter formal evidence.

The launch runbook audit includes:

- audit status, runbook status, seal status, start gate, and first step;
- coverage checks and missing coverage for seal-to-runbook handoff;
- candidate order, execution order, step verification, verification commands,
  failure rollback, and post-completion review coverage;
- target candidates and read-only boundary checks.

Current pre-application data produces `runbook_audit_ready` with all coverage
checks marked `covered`. If verified session items are waiting, the audit still
preserves the close-first runbook first step and verifies that the runbook
covers it. The launch runbook audit remains a planning artifact only; applied
review-decision, candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Launch Runbook Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_markdown()`
freeze a ready launch runbook audit into a final read-only seal. The seal does
not write `review_decisions.json`, does not update `candidate_extracts.json`,
does not promote candidates, and does not alter formal evidence.

The launch runbook audit seal includes:

- seal status, audit status, runbook status, launch seal status, start gate,
  and sealed first step;
- sealed candidate order, target candidates, and blocked reasons;
- seal checks for audit readiness, runbook coverage, first step, verification
  commands, rollback entrypoints, post-completion review, and zero boundary
  deltas;
- verification commands, rollback entrypoints, and post-completion review
  checks.

Current pre-application data produces
`sealed_for_manual_execution_runbook_audit` with
`execute_apply_correction_queue_first` as the sealed first step. If verified
session items are waiting, the seal instead preserves
`execute_close_verified_candidate_session_items`. The launch runbook audit
seal remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Final Launch Packet

`build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_markdown()`
compress the launch runbook audit seal into a final read-only launch packet.
The packet does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The final launch packet includes:

- launch packet status, audit seal status, and sealed first step;
- candidate order, target candidates, and blocked reasons;
- operator start checklist, verification checklist, rollback path, and
  post-completion review;
- boundary confirmation for zero review-decision, candidate-status, and
  formal-evidence deltas.

Current pre-application data produces
`ready_for_final_manual_launch_packet` with
`execute_apply_correction_queue_first` as the sealed first step. If verified
session items are waiting, the packet instead preserves
`execute_close_verified_candidate_session_items`. The final launch packet
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_markdown()`
audit the final launch packet against the launch runbook audit seal before
operator handoff. The audit does not write `review_decisions.json`, does not
update `candidate_extracts.json`, does not promote candidates, and does not
alter formal evidence.

The final launch packet handoff audit includes:

- handoff readiness, launch packet status, audit seal status, and sealed first
  step;
- coverage checks and missing coverage for status preservation, first step,
  candidate order, operator checklist, verification commands, rollback path,
  post-completion review, target candidates, and boundary confirmation;
- operator-safe start boundary checks before execution begins;
- candidate order, operator start checklist, verification checklist, rollback
  path, post-completion review, boundary confirmation, blocked reasons, and
  target candidates.

Current pre-application data produces `ready_for_operator_handoff` with all
coverage checks marked `covered`. If verified session items are waiting, the
audit preserves `execute_close_verified_candidate_session_items` as the first
operator step. The handoff audit remains a planning artifact only; applied
review-decision, candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_markdown()`
freeze the final launch packet handoff audit into a read-only operator
go/no-go seal. The seal does not write `review_decisions.json`, does not
update `candidate_extracts.json`, does not promote candidates, and does not
alter formal evidence.

The final launch packet handoff audit seal includes:

- seal status, handoff readiness, go/no-go decision, launch packet status,
  audit seal status, and sealed first step;
- sealed candidate order, blocked reasons, and seal checks;
- operator-safe start boundary, verification checklist, rollback path, and
  post-completion review;
- boundary confirmation and target candidates.

Current pre-application data produces
`sealed_for_operator_manual_execution_go` with
`go_for_operator_manual_execution` as the go/no-go decision and
`execute_apply_correction_queue_first` as the sealed first step. If verified
session items are waiting, the seal preserves
`execute_close_verified_candidate_session_items`. The handoff audit seal
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Operator Go/No-Go Seal Launch Receipt

`build_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_markdown()`
compress the operator go/no-go seal into a read-only pre-execution receipt.
The receipt does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The operator go/no-go seal launch receipt includes:

- receipt status, seal status, handoff readiness, go/no-go decision, receipt
  decision, and signed first step;
- signed candidate order, blocked reasons, operator receipt checklist, and
  pre-execution confirmation;
- verification checklist, rollback path, post-completion review, boundary
  confirmation, and target candidates.

Current pre-application data produces `ready_for_operator_launch_receipt`
with `receipt_ready_to_start_manual_execution` as the receipt decision and
`execute_apply_correction_queue_first` as the signed first step. If verified
session items are waiting, the receipt preserves
`execute_close_verified_candidate_session_items`. The launch receipt remains
a planning artifact only; applied review-decision, candidate-status, and
formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_markdown()`
audit the launch receipt against the operator go/no-go seal before any manual
execution begins. The audit does not write `review_decisions.json`, does not
update `candidate_extracts.json`, does not promote candidates, and does not
alter formal evidence.

The launch receipt final boundary audit includes:

- final boundary readiness, receipt status, seal status, go/no-go decision,
  receipt decision, and signed first step;
- receipt coverage checks and missing coverage for seal status, go/no-go
  decision, receipt decision, signed first step, signed candidate order,
  receipt checklist, pre-execution confirmation, verification checklist,
  rollback path, post-completion review, target candidates, and boundary
  deltas;
- final boundary confirmation, pre-execution confirmation, signed candidate
  order, blocked reasons, and target candidates.

Current pre-application data produces `ready_for_final_boundary_audit` with all
receipt coverage checks marked `covered`. If verified session items are
waiting, the audit preserves `execute_close_verified_candidate_session_items`
as the signed first step. The final boundary audit remains a planning artifact
only; applied review-decision, candidate-status, and formal-evidence deltas
remain zero.

## Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_markdown()`
freeze the launch receipt final boundary audit into a final read-only boundary
seal before any manual execution begins. The seal does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The launch receipt final boundary audit seal includes:

- seal status, final boundary readiness, receipt status, go/no-go decision,
  receipt decision, and sealed first step;
- sealed candidate order, receipt coverage checks, missing coverage, blocked
  reasons, and target candidates;
- final boundary confirmation, pre-execution confirmation, verification
  checklist, rollback path, post-completion review, and boundary confirmation.

Current pre-application data produces
`sealed_for_launch_receipt_final_boundary` with
`ready_for_final_boundary_audit` and
`execute_apply_correction_queue_first`. If verified session items are waiting,
the seal preserves `execute_close_verified_candidate_session_items`. The final
boundary audit seal remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal Operator Start Packet

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_markdown()`
convert the launch receipt final boundary audit seal into a final read-only
operator start packet. The packet does not write `review_decisions.json`, does
not update `candidate_extracts.json`, does not promote candidates, and does
not alter formal evidence.

The operator start packet includes:

- packet status, seal status, final boundary readiness, receipt status,
  go/no-go decision, receipt decision, start authorization, and sealed first
  step;
- sealed candidate order, operator start checklist, blocked reasons, and
  target candidates;
- pre-execution confirmation, verification checklist, rollback path,
  post-completion review, and boundary confirmation.

Current pre-application data produces `ready_for_operator_start_packet` with
`authorized_to_start_manual_execution` and
`execute_apply_correction_queue_first`. If verified session items are waiting,
the packet preserves `execute_close_verified_candidate_session_items`. The
operator start packet remains a planning artifact only; applied
review-decision, candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Operator Start Packet Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_markdown()`
audit the operator start packet against the launch receipt final boundary audit
seal before any manual execution begins. The audit does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The operator start packet audit includes:

- audit status, packet status, seal status, start authorization, coverage
  checks, missing coverage, and boundary checks;
- sealed first step, sealed candidate order, operator start checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, and blocked reasons;
- boundary confirmation and zero applied review-decision, candidate-status,
  and formal-evidence deltas.

Current pre-application data produces `operator_start_packet_audit_ready` with
all coverage checks marked `covered` and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the audit preserves `execute_close_verified_candidate_session_items`. The
operator start packet audit remains a planning artifact only; applied
review-decision, candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Operator Start Packet Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal_markdown()`
freeze the operator start packet audit into a final read-only audit seal. The
seal does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The operator start packet audit seal includes:

- seal status, audit status, packet status, start authorization, blocked
  reasons, seal checks, coverage checks, missing coverage, and boundary checks;
- sealed first step, sealed candidate order, operator start checklist,
  verification checklist, rollback path, post-completion review, and target
  candidates;
- boundary confirmation and zero applied review-decision, candidate-status,
  and formal-evidence deltas.

Current pre-application data produces `sealed_for_operator_start_packet_audit`
with `operator_start_packet_audit_ready` and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the seal preserves `execute_close_verified_candidate_session_items`. The
operator start packet audit seal remains a planning artifact only; applied
review-decision, candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Authorization Receipt

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_markdown()`
compress the operator start packet audit seal into a final read-only start
authorization receipt. The receipt does not write `review_decisions.json`,
does not update `candidate_extracts.json`, does not promote candidates, and
does not alter formal evidence.

The start authorization receipt includes:

- receipt status, seal status, audit status, packet status, start
  authorization, and sealed first step;
- sealed candidate order, operator start checklist, verification checklist,
  rollback path, post-completion review, target candidates, and blocked
  reasons;
- receipt checks, boundary confirmation, and zero applied review-decision,
  candidate-status, and formal-evidence deltas.

Current pre-application data produces
`ready_for_manual_execution_start_authorization_receipt` with
`sealed_for_operator_start_packet_audit` and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the receipt preserves `execute_close_verified_candidate_session_items`. The
start authorization receipt remains a planning artifact only; applied
review-decision, candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_markdown()`
audit the start authorization receipt against the operator start packet audit
seal before manual execution begins. The audit does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The start authorization receipt coverage audit includes:

- coverage audit status, receipt status, seal status, operator start packet
  audit status, packet status, start authorization, coverage checks, missing
  coverage, and boundary checks;
- sealed first step, sealed candidate order, operator start checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, and blocked reasons;
- boundary confirmation and zero applied review-decision, candidate-status,
  and formal-evidence deltas.

Current pre-application data produces
`start_authorization_receipt_coverage_audit_ready` with all coverage checks
marked `covered`, `ready_for_manual_execution_start_authorization_receipt`,
`sealed_for_operator_start_packet_audit`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the coverage audit preserves
`execute_close_verified_candidate_session_items`. The coverage audit remains a
planning artifact only; applied review-decision, candidate-status, and
formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_markdown()`
freeze the start authorization receipt coverage audit into a final read-only
coverage audit seal. The seal does not write `review_decisions.json`, does not
update `candidate_extracts.json`, does not promote candidates, and does not
alter formal evidence.

The start authorization receipt coverage audit seal includes:

- seal status, coverage audit status, receipt status, operator start packet
  audit seal status, operator start packet audit status, packet status, start
  authorization, blocked reasons, and seal checks;
- coverage checks, missing coverage, boundary checks, sealed first step,
  sealed candidate order, operator start checklist, verification checklist,
  rollback path, post-completion review, and target candidates;
- boundary confirmation and zero applied review-decision, candidate-status,
  and formal-evidence deltas.

Current pre-application data produces
`sealed_for_start_authorization_receipt_coverage_audit` with
`start_authorization_receipt_coverage_audit_ready`,
`ready_for_manual_execution_start_authorization_receipt`,
`sealed_for_operator_start_packet_audit`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the seal preserves `execute_close_verified_candidate_session_items`. The seal
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Authorization Packet

`build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_markdown()`
compress the start authorization receipt coverage audit seal into a final
read-only manual execution authorization packet. The packet does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The manual execution authorization packet includes:

- packet status, seal status, coverage audit status, receipt status, operator
  start packet audit status, start authorization, and sealed first step;
- authorization checks, sealed candidate order, operator authorization
  checklist, verification checklist, rollback path, post-completion review,
  target candidates, and blocked reasons;
- boundary confirmation and zero applied review-decision, candidate-status,
  and formal-evidence deltas.

Current pre-application data produces
`ready_for_manual_execution_authorization_packet` with
`sealed_for_start_authorization_receipt_coverage_audit` and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the packet preserves `execute_close_verified_candidate_session_items`. The
authorization packet remains a planning artifact only; applied
review-decision, candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_markdown()`
audit the manual execution authorization packet against the start authorization
receipt coverage audit seal before manual execution begins. The audit does not
write `review_decisions.json`, does not update `candidate_extracts.json`, does
not promote candidates, and does not alter formal evidence.

The manual execution authorization packet coverage audit includes:

- audit status, packet status, seal status, coverage audit status, receipt
  status, operator start packet audit status, start authorization, packet
  coverage checks, missing coverage, and boundary checks;
- sealed first step, sealed candidate order, operator authorization checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, and blocked reasons;
- boundary confirmation and zero applied review-decision, candidate-status,
  and formal-evidence deltas.

Current pre-application data produces
`manual_execution_authorization_packet_coverage_audit_ready` with all packet
coverage checks marked `covered`,
`ready_for_manual_execution_authorization_packet`,
`sealed_for_start_authorization_receipt_coverage_audit`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the audit preserves `execute_close_verified_candidate_session_items`. The audit
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_markdown()`
freeze the manual execution authorization packet coverage audit into a final
read-only audit seal. The seal does not write `review_decisions.json`, does not
update `candidate_extracts.json`, does not promote candidates, and does not
alter formal evidence.

The manual execution authorization packet coverage audit seal includes:

- seal status, audit status, packet status, authorization packet seal status,
  coverage audit status, receipt status, operator start packet audit status,
  start authorization, seal checks, packet coverage checks, missing coverage,
  and boundary checks;
- sealed first step, sealed candidate order, operator authorization checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`sealed_for_manual_execution_authorization_packet_coverage_audit` with
`manual_execution_authorization_packet_coverage_audit_ready`,
`ready_for_manual_execution_authorization_packet`,
`sealed_for_start_authorization_receipt_coverage_audit`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the seal preserves `execute_close_verified_candidate_session_items`. The seal
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Docket

`build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_markdown()`
compress the manual execution authorization packet coverage audit seal into a
final read-only start docket. The docket does not write `review_decisions.json`,
does not update `candidate_extracts.json`, does not promote candidates, and
does not alter formal evidence.

The manual execution start docket includes:

- docket status, seal status, audit status, packet status, authorization packet
  seal status, coverage audit status, receipt status, operator start packet
  audit status, start authorization, and docket checks;
- sealed first step, sealed candidate order, operator authorization checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`ready_for_manual_execution_start_docket` with
`sealed_for_manual_execution_authorization_packet_coverage_audit`,
`manual_execution_authorization_packet_coverage_audit_ready`,
`ready_for_manual_execution_authorization_packet`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the docket preserves `execute_close_verified_candidate_session_items`. The
docket remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_markdown()`
audit the manual execution start docket against the authorization packet
coverage audit seal before manual execution begins. The audit does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The manual execution start docket coverage audit includes:

- audit status, docket status, seal status, audit source status, packet status,
  authorization packet seal status, coverage audit status, receipt status,
  operator start packet audit status, start authorization, docket coverage
  checks, missing coverage, and boundary checks;
- sealed first step, sealed candidate order, operator authorization checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`manual_execution_start_docket_coverage_audit_ready` with all docket coverage
checks marked `covered`, `ready_for_manual_execution_start_docket`,
`sealed_for_manual_execution_authorization_packet_coverage_audit`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the audit preserves `execute_close_verified_candidate_session_items`. The audit
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_markdown()`
freeze the manual execution start docket coverage audit into a final read-only
coverage audit seal. The seal does not write `review_decisions.json`, does not
update `candidate_extracts.json`, does not promote candidates, and does not
alter formal evidence.

The manual execution start docket coverage audit seal includes:

- seal status, audit status, docket status, source seal status, audit source
  status, packet status, authorization packet seal status, coverage audit
  status, receipt status, operator start packet audit status, start
  authorization, seal checks, docket coverage checks, missing coverage, and
  boundary checks;
- sealed first step, sealed candidate order, operator authorization checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`sealed_for_manual_execution_start_docket_coverage_audit` with
`manual_execution_start_docket_coverage_audit_ready`,
`ready_for_manual_execution_start_docket`,
`sealed_for_manual_execution_authorization_packet_coverage_audit`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the seal preserves `execute_close_verified_candidate_session_items`. The seal
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Final Start Packet

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_markdown()`
compress the manual execution start docket coverage audit seal into a final
read-only start packet for the next manual operator session. The packet does
not write `review_decisions.json`, does not update `candidate_extracts.json`,
does not promote candidates, and does not alter formal evidence.

The manual execution final start packet includes:

- packet status, seal status, audit status, docket status, source seal status,
  audit source status, packet source status, authorization packet seal status,
  coverage audit status, receipt status, operator start packet audit status,
  start authorization, and packet checks;
- sealed first step, sealed candidate order, operator authorization checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`ready_for_manual_execution_final_start_packet` with
`sealed_for_manual_execution_start_docket_coverage_audit`,
`manual_execution_start_docket_coverage_audit_ready`,
`ready_for_manual_execution_start_docket`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the packet preserves `execute_close_verified_candidate_session_items`. The
packet remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_markdown()`
audit the manual execution final start packet against the sealed start docket
coverage audit before operator handoff. The audit does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The manual execution final start packet handoff audit includes:

- handoff readiness, packet status, seal status, audit status, docket status,
  source seal status, audit source status, packet source status, authorization
  packet seal status, coverage audit status, receipt status, operator start
  packet audit status, start authorization, coverage checks, missing coverage,
  and boundary checks;
- operator-safe start boundary, sealed first step, sealed candidate order,
  operator authorization checklist, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`ready_for_manual_execution_final_start_packet_handoff` with
`ready_for_manual_execution_final_start_packet`,
`sealed_for_manual_execution_start_docket_coverage_audit`,
`manual_execution_start_docket_coverage_audit_ready`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the audit preserves `execute_close_verified_candidate_session_items`. The audit
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_markdown()`
freeze the manual execution final start packet handoff audit into a read-only
operator start seal. The seal does not write `review_decisions.json`, does not
update `candidate_extracts.json`, does not promote candidates, and does not
alter formal evidence.

The manual execution final start packet handoff audit seal includes:

- seal status, handoff readiness, go/no-go start decision, packet status, seal
  source status, audit status, docket status, start authorization, seal checks,
  coverage checks, missing coverage, and boundary checks;
- operator-safe start boundary, sealed first step, sealed candidate order,
  operator authorization checklist, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`sealed_for_manual_execution_final_start_packet_handoff` with
`ready_for_manual_execution_final_start_packet_handoff`,
`go_for_operator_manual_execution`,
`ready_for_manual_execution_final_start_packet`,
`sealed_for_manual_execution_start_docket_coverage_audit`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the seal preserves `execute_close_verified_candidate_session_items`. The seal
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Authorization Packet

`build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet_markdown()`
compress the final start packet handoff audit seal into a read-only start
authorization packet. The packet does not write `review_decisions.json`, does
not update `candidate_extracts.json`, does not promote candidates, and does
not alter formal evidence.

The manual execution start authorization packet includes:

- packet status, seal status, handoff readiness, go/no-go start decision,
  start authorization, audit status, docket status, and authorization
  checklist;
- sealed first step, sealed candidate order, operator authorization checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`ready_for_manual_execution_start_authorization_packet` with
`sealed_for_manual_execution_final_start_packet_handoff`,
`ready_for_manual_execution_final_start_packet_handoff`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the packet preserves `execute_close_verified_candidate_session_items`. The
packet remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_markdown()`
audit the start authorization packet against the final start packet handoff
audit seal. The audit does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The manual execution start authorization packet coverage audit includes:

- audit status, packet status, seal status, handoff readiness, go/no-go start
  decision, start authorization, source audit status, docket status, packet
  coverage checks, missing coverage, and boundary checks;
- authorization checklist, sealed first step, sealed candidate order, operator
  authorization checklist, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`manual_execution_start_authorization_packet_coverage_audit_ready` with
`ready_for_manual_execution_start_authorization_packet`,
`sealed_for_manual_execution_final_start_packet_handoff`,
`ready_for_manual_execution_final_start_packet_handoff`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the audit preserves `execute_close_verified_candidate_session_items`. The
audit remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_markdown()`
freeze the start authorization packet coverage audit into a read-only coverage
audit seal. The seal does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The manual execution start authorization packet coverage audit seal includes:

- seal status, audit status, packet status, seal source status, handoff
  readiness, go/no-go start decision, start authorization, source audit
  status, docket status, seal checks, packet coverage checks, missing
  coverage, and boundary checks;
- authorization checklist, sealed first step, sealed candidate order, operator
  authorization checklist, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`sealed_for_manual_execution_start_authorization_packet_coverage_audit` with
`manual_execution_start_authorization_packet_coverage_audit_ready`,
`ready_for_manual_execution_start_authorization_packet`,
`sealed_for_manual_execution_final_start_packet_handoff`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the seal preserves `execute_close_verified_candidate_session_items`. The seal
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Clearance Packet

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_markdown()`
compress the start authorization packet coverage audit seal into a read-only
manual execution start clearance packet. The packet does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The manual execution start clearance packet includes:

- packet status, seal status, audit status, packet source status, handoff
  readiness, go/no-go start decision, start authorization, source audit
  status, docket status, and clearance checklist;
- sealed first step, sealed candidate order, operator authorization
  checklist, verification checklist, rollback path, post-completion review,
  target candidates, blocked reasons, and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`ready_for_manual_execution_start_clearance_packet` with
`sealed_for_manual_execution_start_authorization_packet_coverage_audit`,
`manual_execution_start_authorization_packet_coverage_audit_ready`,
`ready_for_manual_execution_start_authorization_packet`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the packet preserves `execute_close_verified_candidate_session_items`. The
packet remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_markdown()`
audit the start clearance packet against the coverage audit seal inputs. The
audit does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The manual execution start clearance packet coverage audit includes:

- audit status, packet status, seal status, packet source status, handoff
  readiness, go/no-go start decision, start authorization, source audit
  status, docket status, packet coverage checks, missing coverage, and
  boundary checks;
- clearance checklist, sealed first step, sealed candidate order, operator
  authorization checklist, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`manual_execution_start_clearance_packet_coverage_audit_ready` with
`ready_for_manual_execution_start_clearance_packet`,
`sealed_for_manual_execution_start_authorization_packet_coverage_audit`,
`ready_for_manual_execution_start_authorization_packet`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the audit preserves `execute_close_verified_candidate_session_items`. The audit
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_markdown()`
freeze the start clearance packet coverage audit into a read-only coverage
audit seal. The seal does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The manual execution start clearance packet coverage audit seal includes:

- seal status, audit status, packet status, seal source status, packet source
  status, handoff readiness, go/no-go start decision, start authorization,
  source audit status, docket status, seal checks, packet coverage checks,
  missing coverage, and boundary checks;
- clearance checklist, sealed first step, sealed candidate order, operator
  authorization checklist, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`sealed_for_manual_execution_start_clearance_packet_coverage_audit` with
`manual_execution_start_clearance_packet_coverage_audit_ready`,
`ready_for_manual_execution_start_clearance_packet`,
`sealed_for_manual_execution_start_authorization_packet_coverage_audit`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the seal preserves `execute_close_verified_candidate_session_items`. The seal
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_markdown()`
compress the start clearance packet coverage audit seal into a read-only final
start authorization. The authorization does not write `review_decisions.json`,
does not update `candidate_extracts.json`, does not promote candidates, and
does not alter formal evidence.

The manual execution start clearance packet final start authorization includes:

- authorization status, seal status, audit status, packet status, seal source
  status, packet source status, handoff readiness, go/no-go start decision,
  start authorization, source audit status, docket status, authorization
  checks, seal checks, packet coverage checks, missing coverage, and boundary
  checks;
- clearance checklist, sealed first step, sealed candidate order, operator
  authorization checklist, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`authorized_for_manual_execution_start_from_clearance_packet` with
`sealed_for_manual_execution_start_clearance_packet_coverage_audit`,
`manual_execution_start_clearance_packet_coverage_audit_ready`,
`ready_for_manual_execution_start_clearance_packet`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the authorization preserves `execute_close_verified_candidate_session_items`.
The authorization remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_markdown()`
audit the final start authorization against the start clearance packet coverage
audit seal inputs. The audit does not write `review_decisions.json`, does not
update `candidate_extracts.json`, does not promote candidates, and does not
alter formal evidence.

The manual execution start clearance packet final start authorization coverage
audit includes:

- audit status, authorization status, seal status, packet status, seal source
  status, packet source status, handoff readiness, go/no-go start decision,
  start authorization, source audit status, docket status, authorization
  coverage checks, authorization checks, seal checks, packet coverage checks,
  missing coverage, and boundary checks;
- clearance checklist, sealed first step, sealed candidate order, operator
  authorization checklist, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`
with `authorized_for_manual_execution_start_from_clearance_packet`,
`sealed_for_manual_execution_start_clearance_packet_coverage_audit`,
`ready_for_manual_execution_start_clearance_packet`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the audit preserves `execute_close_verified_candidate_session_items`. The
audit remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_markdown()`
freeze the ready final start authorization coverage audit into a read-only
audit seal. The seal does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The manual execution start clearance packet final start authorization coverage
audit seal includes:

- seal status, audit status, authorization status, packet status, seal source
  status, packet source status, handoff readiness, go/no-go start decision,
  start authorization, source audit status, docket status, seal checks,
  authorization coverage checks, authorization checks, coverage seal checks,
  packet coverage checks, missing coverage, and boundary checks;
- clearance checklist, sealed first step, sealed candidate order, operator
  authorization checklist, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`
with
`manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`,
`authorized_for_manual_execution_start_from_clearance_packet`,
`ready_for_manual_execution_start_clearance_packet`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the seal preserves `execute_close_verified_candidate_session_items`. The seal
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Handoff Packet

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_markdown()`
compress the final start authorization coverage audit seal into a read-only
operator-facing start handoff packet. The packet does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The manual execution start handoff packet includes:

- handoff packet status, handoff status, seal status, audit status,
  authorization status, packet status, seal source status, packet source
  status, handoff readiness, go/no-go start decision, start authorization,
  source audit status, docket status, handoff checks, seal checks,
  authorization coverage checks, authorization checks, coverage seal checks,
  packet coverage checks, missing coverage, and boundary checks;
- clearance checklist, sealed first step, sealed candidate order, operator
  authorization checklist, operator start checklist, verification checklist,
  rollback path, post-completion review, target candidates, blocked reasons,
  and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`ready_for_manual_execution_start_handoff_packet` and
`ready_for_operator_manual_execution_start_handoff` with
`sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`,
`manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`,
`authorized_for_manual_execution_start_from_clearance_packet`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the packet preserves `execute_close_verified_candidate_session_items`. The
packet remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_markdown()`
audit the start handoff packet against the final start authorization coverage
audit seal. The audit does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The manual execution start handoff packet coverage audit includes:

- audit status, handoff packet status, handoff status, seal status, coverage
  audit status, authorization status, packet status, seal source status,
  packet source status, handoff readiness, go/no-go start decision, start
  authorization, source audit status, docket status, coverage checks, missing
  coverage, and boundary checks;
- handoff checks, seal checks, authorization coverage checks, authorization
  checks, coverage seal checks, packet coverage checks, clearance checklist,
  sealed first step, sealed candidate order, operator authorization checklist,
  operator start checklist, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`manual_execution_start_handoff_packet_coverage_audit_ready` with
`ready_for_manual_execution_start_handoff_packet`,
`ready_for_operator_manual_execution_start_handoff`,
`sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`,
`manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`,
`authorized_for_manual_execution_start_from_clearance_packet`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the audit preserves `execute_close_verified_candidate_session_items`; otherwise
the sealed first step remains `execute_apply_correction_queue_first`. The audit
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_markdown()`
freeze the start handoff packet coverage audit into a read-only audit seal.
The seal does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The manual execution start handoff packet coverage audit seal includes:

- seal status, audit status, handoff packet status, handoff status, final start
  authorization coverage audit seal status, coverage audit status,
  authorization status, packet status, seal source status, packet source
  status, handoff readiness, go/no-go start decision, start authorization,
  source audit status, docket status, seal checks, coverage checks, missing
  coverage, and boundary checks;
- handoff checks, source seal checks, authorization coverage checks,
  authorization checks, coverage seal checks, packet coverage checks,
  clearance checklist, sealed first step, sealed candidate order, operator
  authorization checklist, operator start checklist, verification checklist,
  rollback path, post-completion review, target candidates, blocked reasons,
  and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`sealed_for_manual_execution_start_handoff_packet_coverage_audit` with
`manual_execution_start_handoff_packet_coverage_audit_ready`,
`ready_for_manual_execution_start_handoff_packet`,
`ready_for_operator_manual_execution_start_handoff`,
`sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`,
`manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`,
`authorized_for_manual_execution_start_from_clearance_packet`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the seal preserves `execute_close_verified_candidate_session_items`; otherwise
the sealed first step remains `execute_apply_correction_queue_first`. The seal
remains a planning artifact only; applied review-decision, candidate-status,
and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Packet

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_markdown()`
compress the start handoff packet coverage audit seal into a read-only
operator-facing start packet. The packet does not write
`review_decisions.json`, does not update `candidate_extracts.json`, does not
promote candidates, and does not alter formal evidence.

The manual execution start packet includes:

- start packet status, seal status, audit status, handoff packet status,
  handoff status, final start authorization coverage audit seal status,
  coverage audit status, authorization status, packet status, seal source
  status, packet source status, handoff readiness, go/no-go start decision,
  start authorization, source audit status, docket status, start checks, seal
  checks, coverage checks, missing coverage, and boundary checks;
- handoff checks, source seal checks, authorization coverage checks,
  authorization checks, coverage seal checks, packet coverage checks,
  clearance checklist, sealed first step, sealed candidate order, operator
  authorization checklist, operator start checklist, verification checklist,
  rollback path, post-completion review, target candidates, blocked reasons,
  and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`ready_for_operator_manual_execution_start_packet` with
`sealed_for_manual_execution_start_handoff_packet_coverage_audit`,
`manual_execution_start_handoff_packet_coverage_audit_ready`,
`ready_for_manual_execution_start_handoff_packet`,
`ready_for_operator_manual_execution_start_handoff`,
`sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`,
`manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`,
`authorized_for_manual_execution_start_from_clearance_packet`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the packet preserves `execute_close_verified_candidate_session_items`;
otherwise the sealed first step remains `execute_apply_correction_queue_first`.
The packet remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_markdown()`
audit the operator-facing start packet against the start handoff packet
coverage audit seal. The audit does not write `review_decisions.json`, does
not update `candidate_extracts.json`, does not promote candidates, and does
not alter formal evidence.

The manual execution start packet coverage audit includes:

- audit status, start packet status, seal status, start packet source audit
  status, handoff packet status, handoff status, final start authorization
  coverage audit seal status, coverage audit status, authorization status,
  packet status, seal source status, packet source status, handoff readiness,
  go/no-go start decision, start authorization, source audit status, docket
  status, coverage checks, source coverage checks, missing coverage, and
  boundary checks;
- start checks, seal checks, handoff checks, source seal checks,
  authorization coverage checks, authorization checks, coverage seal checks,
  packet coverage checks, clearance checklist, sealed first step, sealed
  candidate order, operator authorization checklist, operator start checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`manual_execution_start_packet_coverage_audit_ready` with
`ready_for_operator_manual_execution_start_packet`,
`sealed_for_manual_execution_start_handoff_packet_coverage_audit`,
`manual_execution_start_handoff_packet_coverage_audit_ready`,
`ready_for_manual_execution_start_handoff_packet`,
`ready_for_operator_manual_execution_start_handoff`,
`sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`,
`manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`,
`authorized_for_manual_execution_start_from_clearance_packet`,
`go_for_operator_manual_execution`, and
`authorized_to_start_manual_execution`. If verified session items are waiting,
the audit preserves `execute_close_verified_candidate_session_items`;
otherwise the sealed first step remains `execute_apply_correction_queue_first`.
The audit remains a planning artifact only; applied review-decision,
candidate-status, and formal-evidence deltas remain zero.

## Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit Seal

`build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal()`
and
`render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal_markdown()`
freeze the ready operator-facing start packet coverage audit into a read-only
seal. The seal does not write `review_decisions.json`, does not update
`candidate_extracts.json`, does not promote candidates, and does not alter
formal evidence.

The manual execution start packet coverage audit seal includes:

- seal status, audit status, start packet status, start packet source audit
  status, start handoff packet coverage audit seal status, handoff packet
  status, handoff status, final start authorization coverage audit seal status,
  coverage audit status, authorization status, packet status, seal source
  status, packet source status, handoff readiness, go/no-go start decision,
  start authorization, source audit status, and docket status;
- seal checks, coverage checks, source coverage checks, missing coverage,
  boundary checks, start checks, source seal checks, handoff checks,
  authorization coverage checks, authorization checks, coverage seal checks,
  packet coverage checks, clearance checklist, sealed first step, sealed
  candidate order, operator authorization checklist, operator start checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, and boundary confirmation;
- zero applied review-decision, candidate-status, and formal-evidence deltas.

Current pre-application data produces
`sealed_for_manual_execution_start_packet_coverage_audit` with
`manual_execution_start_packet_coverage_audit_ready`,
`ready_for_operator_manual_execution_start_packet`, and
`manual_execution_start_handoff_packet_coverage_audit_ready`. If verified
session items are waiting, the seal preserves
`execute_close_verified_candidate_session_items`; otherwise the sealed first
step remains `execute_apply_correction_queue_first`. The seal remains a
planning artifact only; applied review-decision, candidate-status, and
formal-evidence deltas remain zero.

## Gated Ordinary Source Selection Promotions

- `candidate_bazi_general_mingzao_chunqiu_luck_cycle_001` and `candidate_bazi_general_sizhu_yuce_yaojue_pattern_strength_001` are promoted weak-locator 013 candidates from the 015 gated ordinary source-selection pass.
- `promotion_bazi_general_gated_ordinary_source_selection_001` links them to `bazi_general_mingzao_chunqiu_luck_cycle_001` and `bazi_general_sizhu_yuce_yaojue_pattern_strength_001` formal evidence units.

## Gated Ordinary Followup Selection Promotions

- `candidate_bazi_general_bazi_baijue_ten_god_001` and `candidate_bazi_general_mingli_mijue_branch_interaction_001` are promoted weak-locator 013 candidates from the 015 gated ordinary followup selection pass.
- `promotion_bazi_general_gated_ordinary_followup_selection_001` links them to `bazi_general_bazi_baijue_ten_god_001` and `bazi_general_mingli_mijue_branch_interaction_001` formal evidence units.

## Gated Ordinary Final Selection Promotions

- `candidate_bazi_general_choujin_bosi_branch_interaction_001` and `candidate_bazi_general_bazi_shizhan_mifa_luck_cycle_001` are promoted weak-locator 013 candidates from the 015 gated ordinary final selection pass.
- `promotion_bazi_general_gated_ordinary_final_selection_001` links them to `bazi_general_choujin_bosi_branch_interaction_001` and `bazi_general_bazi_shizhan_mifa_luck_cycle_001` formal evidence units.
