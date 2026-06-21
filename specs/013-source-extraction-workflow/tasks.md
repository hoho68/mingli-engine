# Tasks: Source Extraction Workflow

**Input**: Design documents from `specs/013-source-extraction-workflow/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/source-extraction-workflow-contract.md`, `quickstart.md`

**Tests**: Required. This feature changes evidence intake and report evidence boundaries, so tests must be written before implementation for loaders, validation, high-risk handling, promotion readiness, progress summaries, and report-boundary regression.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently. Root PDF files and root `Markdown/` remain external user materials throughout this task list.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other tasks in the same phase when files do not overlap
- **[Story]**: User story label for story phases only
- Every task includes exact project-relative file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the 013 workspace paths without implementing behavior.

- [X] T001 Create `src/mingli_engine/data/source_intake/.gitkeep` so the intake data directory exists without adding raw PDF or Markdown materials
- [X] T002 [P] Create `docs/classical_sources/intake.md` with an initial "source intake progress" heading and a note that root source materials remain external
- [X] T003 [P] Create `src/mingli_engine/source_intake.py` with module docstring only for the future deterministic intake loader
- [X] T004 Verify `git status --short --branch` still shows root PDF files and root `Markdown/` as untracked inputs, not staged project data

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared intake model types, constants, base JSON loading, and empty intake data files. This phase blocks all user stories.

**CRITICAL**: No user story work begins until this phase is complete.

- [X] T005 [P] Add failing tests for source-intake constants and dataclass construction in `tests/unit/test_source_intake.py`
- [X] T006 Add source-intake constants plus `SourceMaterial`, `CandidateExtract`, `ReviewDecision`, `PromotionBatch`, and `IntakeProgressReport` dataclasses in `src/mingli_engine/models.py`
- [X] T007 [P] Add failing tests for missing intake JSON files, invalid JSON, non-array payloads, and duplicate id detection in `tests/unit/test_source_intake.py`
- [X] T008 Implement `SourceIntakeError`, `_read_json_list()`, `_read_optional_json_list()`, `_require_text()`, `_require_string_list()`, `_ensure_unique()`, and `_data_dir()` in `src/mingli_engine/source_intake.py`
- [X] T009 Create empty JSON arrays in `src/mingli_engine/data/source_intake/source_materials.json`, `src/mingli_engine/data/source_intake/candidate_extracts.json`, `src/mingli_engine/data/source_intake/review_decisions.json`, and `src/mingli_engine/data/source_intake/promotion_batches.json`
- [X] T010 Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py` and confirm the foundational tests pass

**Checkpoint**: Foundation ready. Story work can begin.

---

## Phase 3: User Story 1 - Register Candidate Extracts (Priority: P1) MVP

**Goal**: Maintainers can register external source materials and candidate extracts without making candidates report-usable.

**Independent Test**: Register source materials and pending candidates in intake JSON, load them successfully, reject incomplete candidates, and verify formal evidence loading does not include candidate extracts.

### Tests for User Story 1

- [X] T011 [P] [US1] Add failing tests for valid and invalid `SourceMaterial` records in `tests/unit/test_source_intake.py`
- [X] T012 [US1] Implement `load_source_materials()` and source material validation in `src/mingli_engine/source_intake.py`
- [X] T013 [US1] Add nine current source-material registry records with `tracking_status=external_untracked` in `src/mingli_engine/data/source_intake/source_materials.json`
- [X] T014 [P] [US1] Add failing tests for candidate required fields, pending-review eligibility, and invalid statuses in `tests/unit/test_source_intake.py`
- [X] T015 [US1] Implement `load_candidate_extracts()` and candidate field/status validation in `src/mingli_engine/source_intake.py`
- [X] T016 [US1] Add seed pending candidate records in `src/mingli_engine/data/source_intake/candidate_extracts.json` without copying long source passages
- [X] T017 [P] [US1] Add failing tests that candidate `extracted_meaning` and `short_quote` reject long copied passages and absolute outcome language in `tests/unit/test_source_intake.py`
- [X] T018 [US1] Implement concise-text and prohibited-phrase validation for candidate records in `src/mingli_engine/source_intake.py`
- [X] T019 [P] [US1] Add a report-boundary regression test proving pending candidates are excluded from formal evidence loading in `tests/integration/test_report_regression_cases.py`
- [X] T020 [US1] Preserve the report evidence boundary by keeping `src/mingli_engine/classical_sources.py` independent from `src/mingli_engine/data/source_intake/candidate_extracts.json`
- [X] T021 [US1] Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py tests/integration/test_report_regression_cases.py`

**Checkpoint**: US1 is independently usable as the MVP intake queue.

---

## Phase 4: User Story 2 - Review Candidate Evidence (Priority: P2)

**Goal**: Reviewers can approve, return, reject, or block candidates with explicit review metadata, and only approved candidates can enter promotion readiness.

**Independent Test**: Add review decisions for candidates, verify required metadata per decision type, enforce high-risk limitations, and validate promotion batches only include approved candidates.

### Tests for User Story 2

- [X] T022 [P] [US2] Add failing tests for approved, returned, rejected, and blocked review decision requirements in `tests/unit/test_source_intake.py`
- [X] T023 [US2] Implement `load_review_decisions()` and review decision validation in `src/mingli_engine/source_intake.py`
- [X] T024 [US2] Add seed review decision records covering approved, returned, rejected, and blocked outcomes in `src/mingli_engine/data/source_intake/review_decisions.json`
- [X] T025 [P] [US2] Add failing tests that approved high-risk candidates require approval limitations and cannot use `source_quality=needs_recheck` in `tests/unit/test_source_intake.py`
- [X] T026 [US2] Implement high-risk approval, source quality, confidence, and approved-decision cross-reference checks in `src/mingli_engine/source_intake.py`
- [X] T027 [P] [US2] Add failing tests for promotion batch validation and approved-candidate membership in `tests/unit/test_source_intake.py`
- [X] T028 [US2] Implement `load_promotion_batches()` and promotion batch validation in `src/mingli_engine/source_intake.py`
- [X] T029 [US2] Add seed promotion batch records in `src/mingli_engine/data/source_intake/promotion_batches.json`
- [X] T030 [US2] Implement `list_approved_candidates_for_promotion()` in `src/mingli_engine/source_intake.py`
- [X] T031 [US2] Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`

**Checkpoint**: US2 can review candidates and identify promotion-ready approved candidates without changing formal evidence.

---

## Phase 5: User Story 3 - Record Conflicts, Gaps, and Rejections (Priority: P3)

**Goal**: Reviewers can preserve duplicate, conflict, gap, rejection, and blocked reasons as audit metadata.

**Independent Test**: Load candidates linked to existing evidence, source conflicts, and gaps; reject invalid links; preserve rejection/blocking reasons; and flag likely duplicates.

### Tests for User Story 3

- [X] T032 [P] [US3] Add failing tests for duplicate candidate detection using `material_id`, `source_locator`, `proposed_rule_family`, and `extracted_meaning` in `tests/unit/test_source_intake.py`
- [X] T033 [US3] Implement `find_duplicate_candidates()` in `src/mingli_engine/source_intake.py`
- [X] T034 [P] [US3] Add failing tests for candidate links to existing evidence ids, source conflict ids, and curation gap ids in `tests/unit/test_source_intake.py`
- [X] T035 [US3] Implement `validate_candidate_links()` using existing 012 evidence units, source conflicts, and derived curation gaps in `src/mingli_engine/source_intake.py`
- [X] T036 [P] [US3] Add failing tests that rejected and blocked review decisions require durable reasons in `tests/unit/test_source_intake.py`
- [X] T037 [US3] Strengthen rejected and blocked reason validation in `src/mingli_engine/source_intake.py`
- [X] T038 [US3] Add representative duplicate, conflict-linked, gap-linked, rejected, and blocked examples to `src/mingli_engine/data/source_intake/candidate_extracts.json` and `src/mingli_engine/data/source_intake/review_decisions.json`
- [X] T039 [US3] Add conflict/gap intake notes to `docs/classical_sources/intake.md`
- [X] T040 [US3] Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`

**Checkpoint**: US3 makes non-promoted material auditable without allowing unsafe or disputed material into reports.

---

## Phase 6: User Story 4 - View Intake Progress (Priority: P4)

**Goal**: Maintainers can see intake progress by source material, candidate status, rule family, risk tier, approval readiness, duplicates, conflicts, and gaps.

**Independent Test**: Build a progress report from intake data and verify it separates pending, approved, promoted, rejected, blocked, duplicate, conflict-linked, and gap-linked counts.

### Tests for User Story 4

- [X] T041 [P] [US4] Add failing tests for `build_intake_progress_report()` status, risk, rule-family, and material counts in `tests/unit/test_source_intake.py`
- [X] T042 [US4] Implement `build_intake_progress_report()` in `src/mingli_engine/source_intake.py`
- [X] T043 [P] [US4] Add failing tests for approved-not-promoted, duplicate, conflict-link, and gap-link progress counts in `tests/unit/test_source_intake.py`
- [X] T044 [US4] Extend `build_intake_progress_report()` with approval readiness, duplicate, conflict-link, and gap-link counts in `src/mingli_engine/source_intake.py`
- [X] T045 [P] [US4] Add failing tests for `validate_intake_quality()` blocking failures in `tests/unit/test_source_intake.py`
- [X] T046 [US4] Implement `validate_intake_quality()` in `src/mingli_engine/source_intake.py`
- [X] T047 [US4] Update `docs/classical_sources/intake.md` with the current computed intake snapshot and next-review queues
- [X] T048 [US4] Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`

**Checkpoint**: US4 gives maintainers a review dashboard without exposing unapproved candidates to report generation.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, safety, and regression verification across all stories.

- [X] T049 [P] Update `docs/classical_sources/README.md` to document the 013 source-intake boundary and external-material guardrails
- [X] T050 [P] Update `specs/013-source-extraction-workflow/quickstart.md` with actual validation commands and expected intake snapshot after implementation
- [X] T051 [P] Add safety regression tests for candidate absolute-language filtering in `tests/safety/test_expanded_high_risk_language.py`
- [X] T052 Run `uv run --with pytest python -m pytest tests/safety/test_expanded_high_risk_language.py tests/integration/test_report_regression_cases.py`
- [X] T053 Run `uv run --with pytest python -m pytest tests/unit/test_source_intake.py tests/unit/test_classical_sources.py tests/unit/test_evidence_curation.py`
- [X] T054 Run full suite with `uv run --with pytest python -m pytest`
- [X] T055 Run `git diff --check` and confirm only acceptable line-ending warnings, if any
- [X] T056 Verify `git status --short --branch` shows no staged root PDF files and no staged root `Markdown/` material
- [X] T057 Mark completed tasks in `specs/013-source-extraction-workflow/tasks.md`

---

## Phase 8: Pending Candidate Review Worklist

**Goal**: Surface the 017-created pending candidates as a bounded review worklist without writing human review decisions or changing formal evidence.

- [X] T058 [P] Add red tests for pending candidate review worklist ordering, required review actions, learning-reference locator replacement, sensitive-language checks, and non-pending exclusion in `tests/unit/test_source_intake.py`
- [X] T059 [P] Add a report-boundary regression test proving the review worklist does not change candidate ids or formal evidence ids in `tests/integration/test_report_regression_cases.py`
- [X] T060 Add `CandidateReviewWorkItem` in `src/mingli_engine/models.py`
- [X] T061 Implement `list_pending_candidate_review_worklist()` in `src/mingli_engine/source_intake.py`
- [X] T062 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the current pending-review worklist
- [X] T063 Run focused, boundary, and full-suite validation after adding the worklist

---

## Phase 9: Pending Candidate Review Decision Packets

**Goal**: Convert the current pending review worklist into review-decision packet metadata that names required manual inputs and approval blockers without writing review decisions or changing formal evidence.

- [X] T064 [P] Add red tests for pending candidate review decision packets, required review inputs, decision options, approval blockers, and non-pending exclusion in `tests/unit/test_source_intake.py`
- [X] T065 [P] Add a report-boundary regression test proving decision packets do not write review decisions or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T066 Add `CandidateReviewDecisionPacket` in `src/mingli_engine/models.py`
- [X] T067 Implement `list_pending_candidate_review_decision_packets()` in `src/mingli_engine/source_intake.py`
- [X] T068 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with review packet boundaries and blockers
- [X] T069 Run focused, boundary, and full-suite validation after adding decision packets

---

## Phase 10: Pending Review Packet Dashboard

**Goal**: Summarize current pending review decision packets into blocker and missing-input dashboard counts without writing review decisions, promotion batches, or formal evidence.

- [X] T070 [P] Add red tests for packet summary counts, candidate ids, decision option counts, required review input counts, approval blocker counts, packet action counts, and zero review/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T071 [P] Add a report-boundary regression test proving packet summary generation does not write review decisions or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T072 Add `CandidateReviewPacketSummary` in `src/mingli_engine/models.py`
- [X] T073 Implement `build_pending_candidate_review_packet_summary()` in `src/mingli_engine/source_intake.py`
- [X] T074 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with packet summary dashboard counts
- [X] T075 Run focused, boundary, and full-suite validation after adding the packet dashboard

---

## Phase 11: Pending Review Action Queue

**Goal**: Convert the packet dashboard into one prioritized next manual action per pending candidate without writing review decisions, promotion batches, or formal evidence.

- [X] T076 [P] Add red tests for pending review action queue ordering, priorities, primary actions, blocking inputs, and no-pending behavior in `tests/unit/test_source_intake.py`
- [X] T077 [P] Add a report-boundary regression test proving action queue generation does not write review decisions or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T078 Add `CandidateReviewActionQueueItem` in `src/mingli_engine/models.py`
- [X] T079 Implement `build_pending_candidate_review_action_queue()` in `src/mingli_engine/source_intake.py`
- [X] T080 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the high-priority action queue
- [X] T081 Run focused, boundary, and full-suite validation after adding the action queue

---

## Phase 12: Pending Review Markdown Checklist

**Goal**: Render the current pending review action queue as a stable Markdown checklist for manual review sessions without writing files, review decisions, promotion batches, or formal evidence.

- [X] T082 [P] Add red tests for Markdown checklist summary, candidate action items, blocking inputs, boundary notes, and empty-queue behavior in `tests/unit/test_source_intake.py`
- [X] T083 [P] Add a report-boundary regression test proving Markdown rendering does not write review decisions or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T084 Implement `render_pending_candidate_review_action_queue_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T085 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the Markdown checklist command and summary
- [X] T086 Run focused, boundary, and full-suite validation after adding Markdown checklist rendering

---

## Phase 13: Pending Review Input Templates

**Goal**: Render the current pending review candidates as fillable human review input templates without writing review decisions, promotion batches, or formal evidence.

- [X] T087 [P] Add red unit tests for pending review input templates, fillable fields, conditional blocker fields, Markdown rendering, and empty-queue behavior in `tests/unit/test_source_intake.py`
- [X] T088 [P] Add a report-boundary regression test proving input-template generation does not write review decisions or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T089 Add `CandidateReviewInputTemplate` in `src/mingli_engine/models.py`
- [X] T090 Implement `list_pending_candidate_review_input_templates()` and `render_pending_candidate_review_input_templates_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T091 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the input-template command and current summary
- [X] T092 Run focused, boundary, and full-suite validation after adding input templates

---

## Phase 14: Pending Review Draft Validation

**Goal**: Validate filled pending-candidate review decision drafts before any manual write to `review_decisions.json`, without writing review decisions, promotion batches, or formal evidence.

- [X] T093 [P] Add red unit tests for complete approved drafts, unresolved approved blockers, Markdown validation summary, and zero deltas in `tests/unit/test_source_intake.py`
- [X] T094 [P] Add a report-boundary regression test proving draft validation does not write review decisions or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T095 Add `CandidateReviewDraftValidationResult` in `src/mingli_engine/models.py`
- [X] T096 Implement `validate_pending_candidate_review_decision_draft()` and `render_pending_candidate_review_draft_validation_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T097 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the draft-validation command and boundary notes
- [X] T098 Run focused, boundary, and full-suite validation after adding draft validation

---

## Phase 15: Pending Review Application Guard

**Goal**: Preview the manual application of validated review decision drafts, including review-decision additions and candidate-status updates, without writing JSON, promoting candidates, or changing formal evidence.

- [X] T099 [P] Add red unit tests for ready application previews, blocked draft previews, Markdown guard summaries, preview deltas, and zero applied deltas in `tests/unit/test_source_intake.py`
- [X] T100 [P] Add a report-boundary regression test proving application guard previews do not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T101 Add `CandidateReviewApplicationGuardResult` in `src/mingli_engine/models.py`
- [X] T102 Implement `build_pending_candidate_review_application_guard()` and `render_pending_candidate_review_application_guard_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T103 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the application-guard command and boundary notes
- [X] T104 Run focused, boundary, and full-suite validation after adding application guard previews

---

## Phase 16: Pending Review Application Packets

**Goal**: Export application-guard previews as manual application packets with copyable JSON snippets, checklist items, and rollback notes, without writing JSON, promoting candidates, or changing formal evidence.

- [X] T105 [P] Add red unit tests for exportable packets, blocked packets, Markdown JSON snippets, manual checklist items, rollback notes, preview deltas, and zero applied deltas in `tests/unit/test_source_intake.py`
- [X] T106 [P] Add a report-boundary regression test proving application packet export does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T107 Add `CandidateReviewApplicationPacket` in `src/mingli_engine/models.py`
- [X] T108 Implement `build_pending_candidate_review_application_packets()` and `render_pending_candidate_review_application_packets_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T109 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the application-packet command and boundary notes
- [X] T110 Run focused, boundary, and full-suite validation after adding application packet export

---

## Phase 17: Pending Review Application Audit Summary

**Goal**: Summarize the pending-review manual application pipeline across templates, draft validation, application guard, and application packets, without writing JSON, promoting candidates, or changing formal evidence.

- [X] T111 [P] Add red unit tests for audit summary counts, exportable candidates, blocked candidates, missing-draft candidates, next manual actions, preview deltas, and zero applied deltas in `tests/unit/test_source_intake.py`
- [X] T112 [P] Add a report-boundary regression test proving audit summary generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T113 Add `CandidateReviewApplicationAuditSummary` in `src/mingli_engine/models.py`
- [X] T114 Implement `build_pending_candidate_review_application_audit_summary()` and `render_pending_candidate_review_application_audit_summary_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T115 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the audit-summary command and boundary notes
- [X] T116 Run focused, boundary, and full-suite validation after adding application audit summary

---

## Phase 18: Pending Review Manual Action Dashboard

**Goal**: Group the current pending candidates by shortest next manual action and output a recommended processing order, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T117 [P] Add red unit tests for manual action dashboard grouping, action counts, candidates by action, recommended processing order, preview deltas, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T118 [P] Add a report-boundary regression test proving manual action dashboard generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T119 Add `CandidateReviewManualActionDashboard` in `src/mingli_engine/models.py`
- [X] T120 Implement `build_pending_candidate_review_manual_action_dashboard()` and `render_pending_candidate_review_manual_action_dashboard_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T121 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual action dashboard command, grouped action lanes, recommended processing order, and boundary notes
- [X] T122 Run focused, boundary, and full-suite validation after adding the manual action dashboard

---

## Phase 19: Pending Review Manual Application Dry-Run Guide

**Goal**: Expand the manual action dashboard into per-candidate dry-run steps, ready criteria, post-apply checks, and rollback notes, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T123 [P] Add red unit tests for dry-run guide steps, required inputs, ready criteria, post-apply checks, rollback notes, recommended order, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T124 [P] Add a report-boundary regression test proving dry-run guide generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T125 Add `CandidateReviewManualApplicationDryRunStep` and `CandidateReviewManualApplicationDryRunGuide` in `src/mingli_engine/models.py`
- [X] T126 Implement `build_pending_candidate_review_manual_application_dry_run_guide()` and `render_pending_candidate_review_manual_application_dry_run_guide_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T127 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the dry-run guide command, per-candidate steps, ready criteria, post-apply checks, rollback notes, and boundary notes
- [X] T128 Run focused, boundary, and full-suite validation after adding the manual application dry-run guide

---

## Phase 20: Pending Review Manual Application Preflight Report

**Goal**: Verify manual application readiness before a human applies packets by checking review-decision id uniqueness, pending-status patch alignment, and packet preview delta consistency, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T129 [P] Add red unit tests for preflight report ready/blocked candidates, decision id uniqueness, candidate-status patch alignment, packet delta consistency, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T130 [P] Add a report-boundary regression test proving preflight report generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T131 Add `CandidateReviewManualApplicationPreflightCheck` and `CandidateReviewManualApplicationPreflightReport` in `src/mingli_engine/models.py`
- [X] T132 Implement `build_pending_candidate_review_manual_application_preflight_report()` and `render_pending_candidate_review_manual_application_preflight_report_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T133 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the preflight report command, ready/blocked counts, uniqueness/status/delta checks, and boundary notes
- [X] T134 Run focused, boundary, and full-suite validation after adding the manual application preflight report

---

## Phase 21: Pending Review Manual Application Handoff Summary

**Goal**: Combine the manual action dashboard, dry-run guide, and preflight report into one human execution handoff with ready, blocked, and missing-draft lanes, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T135 [P] Add red unit tests for handoff summary ready/blocked/missing lanes, recommended processing order, manual steps, preflight checks, blockers, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T136 [P] Add a report-boundary regression test proving handoff summary generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T137 Add `CandidateReviewManualApplicationHandoffItem` and `CandidateReviewManualApplicationHandoffSummary` in `src/mingli_engine/models.py`
- [X] T138 Implement `build_pending_candidate_review_manual_application_handoff_summary()` and `render_pending_candidate_review_manual_application_handoff_summary_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T139 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the handoff summary command, execution lanes, preflight checks, recommended order, and boundary notes
- [X] T140 Run focused, boundary, and full-suite validation after adding the manual application handoff summary

---

## Phase 22: Pending Review Manual Application Readiness Ledger

**Goal**: Render the manual application handoff as an unchecked, maintainer-facing readiness ledger with per-candidate checkboxes, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T141 [P] Add red unit tests for readiness ledger rows, statuses, checkboxes, blockers, recommended processing order, unchecked checkbox counts, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T142 [P] Add a report-boundary regression test proving readiness ledger generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T143 Add `CandidateReviewManualApplicationReadinessLedgerRow` and `CandidateReviewManualApplicationReadinessLedger` in `src/mingli_engine/models.py`
- [X] T144 Implement `build_pending_candidate_review_manual_application_readiness_ledger()` and `render_pending_candidate_review_manual_application_readiness_ledger_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T145 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the readiness ledger command, checkbox rows, recommended order, and boundary notes
- [X] T146 Run focused, boundary, and full-suite validation after adding the manual application readiness ledger

---

## Phase 23: Pending Review Manual Application Session Packet

**Goal**: Compress the readiness ledger into a ready-first manual session packet with ready actions, blocked follow-ups, missing-draft follow-ups, and post-session verification, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T147 [P] Add red unit tests for session packet header, ready-first action queue, blocked follow-ups, missing-draft follow-ups, post-session verification, recommended order, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T148 [P] Add a report-boundary regression test proving session packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T149 Add `CandidateReviewManualApplicationSessionAction` and `CandidateReviewManualApplicationSessionPacket` in `src/mingli_engine/models.py`
- [X] T150 Implement `build_pending_candidate_review_manual_application_session_packet()` and `render_pending_candidate_review_manual_application_session_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T151 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the session packet command, ready-first queue, follow-ups, post-session verification, and boundary notes
- [X] T152 Run focused, boundary, and full-suite validation after adding the manual application session packet

---

## Phase 24: Pending Review Manual Application Session Outcome Preview

**Goal**: Preview the post-session outcome of applying only ready session actions, including projected status changes, remaining pending follow-ups, and post-session next actions, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T153 [P] Add red unit tests for session outcome preview scope, ready-only projected status changes, remaining pending follow-ups, post-session next actions, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T154 [P] Add a report-boundary regression test proving session outcome preview generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T155 Add `CandidateReviewManualApplicationSessionOutcomeItem` and `CandidateReviewManualApplicationSessionOutcomePreview` in `src/mingli_engine/models.py`
- [X] T156 Implement `build_pending_candidate_review_manual_application_session_outcome_preview()` and `render_pending_candidate_review_manual_application_session_outcome_preview_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T157 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the session outcome preview command, ready-only projection, remaining pending follow-ups, post-session next actions, and boundary notes
- [X] T158 Run focused, boundary, and full-suite validation after adding the manual application session outcome preview

---

## Phase 25: Pending Review Manual Application Post-Session Verification Report

**Goal**: Verify the actual source-intake data after a maintainer manually applies ready session actions, including ready review decision/status matches and follow-up candidates that must remain pending, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T159 [P] Add red unit tests for post-session verification success, missing manual application blockers, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T160 [P] Add a report-boundary regression test proving post-session verification report generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T161 Add `CandidateReviewManualApplicationPostSessionVerificationItem` and `CandidateReviewManualApplicationPostSessionVerificationReport` in `src/mingli_engine/models.py`
- [X] T162 Implement `build_pending_candidate_review_manual_application_post_session_verification_report()` and `render_pending_candidate_review_manual_application_post_session_verification_report_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T163 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the post-session verification command, pre/post data comparison note, ready-action checks, follow-up pending checks, and boundary notes
- [X] T164 Run focused, boundary, and full-suite validation after adding the manual application post-session verification report

---

## Phase 26: Pending Review Manual Application Reconciliation Dashboard

**Goal**: Group post-session verification results into the shortest next manual actions for each candidate, including verified completions, missing review-decision writes, candidate-status corrections, follow-up mismatches, and continued follow-up processing, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T165 [P] Add red unit tests for reconciliation action counts, candidates by action, recommended processing order, blocker prioritization, candidate-status correction, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T166 [P] Add a report-boundary regression test proving reconciliation dashboard generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T167 Add `CandidateReviewManualApplicationReconciliationItem` and `CandidateReviewManualApplicationReconciliationDashboard` in `src/mingli_engine/models.py`
- [X] T168 Implement `build_pending_candidate_review_manual_application_reconciliation_dashboard()` and `render_pending_candidate_review_manual_application_reconciliation_dashboard_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T169 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the reconciliation command, action groups, recommended order, and boundary notes
- [X] T170 Run focused, boundary, and full-suite validation after adding the manual application reconciliation dashboard

---

## Phase 27: Pending Review Manual Application Closure Packet

**Goal**: Convert reconciliation results into a read-only manual session closure packet that separates verified candidates ready to close from carry-forward candidates for the next manual session, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T171 [P] Add red unit tests for closure/carry-forward lanes, closure action counts, closure status, recommended next-session setup, blocker carry-forward mapping, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T172 [P] Add a report-boundary regression test proving closure packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T173 Add `CandidateReviewManualApplicationClosureItem` and `CandidateReviewManualApplicationClosurePacket` in `src/mingli_engine/models.py`
- [X] T174 Implement `build_pending_candidate_review_manual_application_closure_packet()` and `render_pending_candidate_review_manual_application_closure_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T175 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the closure packet command, closure/carry-forward lanes, recommended next-session setup, and boundary notes
- [X] T176 Run focused, boundary, and full-suite validation after adding the manual application closure packet

---

## Phase 28: Pending Review Manual Application Next-Session Starter

**Goal**: Convert closure-packet carry-forward items into a read-only next-session starter with lane-specific checklists and recommended start order for missing review decisions, candidate-status corrections, follow-up mismatch investigations, and follow-up processing, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T177 [P] Add red unit tests for starter lane counts, candidates by lane, recommended start order, lane checklists, closed-candidate omission, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T178 [P] Add a report-boundary regression test proving next-session starter generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T179 Add `CandidateReviewManualApplicationNextSessionStarterItem` and `CandidateReviewManualApplicationNextSessionStarter` in `src/mingli_engine/models.py`
- [X] T180 Implement `build_pending_candidate_review_manual_application_next_session_starter()` and `render_pending_candidate_review_manual_application_next_session_starter_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T181 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session starter command, starter lanes, kickoff checklist, and boundary notes
- [X] T182 Run focused, boundary, and full-suite validation after adding the manual application next-session starter

---

## Phase 29: Pending Review Manual Application Next-Session Packet

**Goal**: Compress the next-session starter into a read-only ready-first manual session packet with correction and follow-up queues, kickoff checklist, post-session verification checklist, and recommended processing order, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T183 [P] Add red unit tests for correction queue grouping, follow-up queue grouping, closed-candidate omission, correction-first processing order, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T184 [P] Add a report-boundary regression test proving next-session packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T185 Add `CandidateReviewManualApplicationNextSessionPacketItem` and `CandidateReviewManualApplicationNextSessionPacket` in `src/mingli_engine/models.py`
- [X] T186 Implement `build_pending_candidate_review_manual_application_next_session_packet()` and `render_pending_candidate_review_manual_application_next_session_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T187 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session packet command, correction/follow-up queues, kickoff checklist, post-session verification checklist, recommended processing order, and boundary notes
- [X] T188 Run focused, boundary, and full-suite validation after adding the manual application next-session packet

---

## Phase 30: Pending Review Manual Application Next-Session Audit Summary

**Goal**: Summarize the closure packet, next-session starter, and next-session packet into a read-only audit summary that verifies carry-forward, queue, kickoff, post-session verification, and recommended-order coverage, while listing the shortest next manual actions without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T189 [P] Add red unit tests for closure/starter/packet status rollup, correction/follow-up queue counts, coverage checks, closed-candidate omission, correction-first shortest actions, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T190 [P] Add a report-boundary regression test proving next-session audit summary generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T191 Add `CandidateReviewManualApplicationNextSessionAuditSummary` in `src/mingli_engine/models.py`
- [X] T192 Implement `build_pending_candidate_review_manual_application_next_session_audit_summary()` and `render_pending_candidate_review_manual_application_next_session_audit_summary_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T193 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session audit summary command, coverage checks, shortest next actions, and boundary notes
- [X] T194 Run focused, boundary, and full-suite validation after adding the manual application next-session audit summary

---

## Phase 31: Pending Review Manual Application Next-Session Operator Checklist

**Goal**: Expand the next-session audit summary's shortest next actions into a read-only operator checklist with target candidates, ready criteria, operator checklist items, verification checklist items, and recommended processing order, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T195 [P] Add red unit tests for action sequence expansion, target candidates by action, ready criteria, operator checklist items, closed-candidate targeting, correction-first prioritization, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T196 [P] Add a report-boundary regression test proving next-session operator checklist generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T197 Add `CandidateReviewManualApplicationNextSessionOperatorChecklistItem` and `CandidateReviewManualApplicationNextSessionOperatorChecklist` in `src/mingli_engine/models.py`
- [X] T198 Implement `build_pending_candidate_review_manual_application_next_session_operator_checklist()` and `render_pending_candidate_review_manual_application_next_session_operator_checklist_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T199 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session operator checklist command, target candidates, ready criteria, operator checklist, verification checklist, recommended processing order, and boundary notes
- [X] T200 Run focused, boundary, and full-suite validation after adding the manual application next-session operator checklist

---

## Phase 32: Pending Review Manual Application Next-Session Execution Handoff

**Goal**: Condense the next-session operator checklist into a one-page read-only execution handoff with first action, first-action targets, ready conditions, blocked conditions, action sequence, target candidates, verification chain, and recommended processing order, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T201 [P] Add red unit tests for first-action selection, first-action targets, ready and blocked conditions, action sequence, target candidates, verification chain, close-first handoff behavior, correction-first prioritization, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T202 [P] Add a report-boundary regression test proving next-session execution handoff generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T203 Add `CandidateReviewManualApplicationNextSessionExecutionHandoff` in `src/mingli_engine/models.py`
- [X] T204 Implement `build_pending_candidate_review_manual_application_next_session_execution_handoff()` and `render_pending_candidate_review_manual_application_next_session_execution_handoff_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T205 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session execution handoff command, first action, ready/blocked conditions, target candidates, verification chain, recommended processing order, and boundary notes
- [X] T206 Run focused, boundary, and full-suite validation after adding the manual application next-session execution handoff

---

## Phase 33: Pending Review Manual Application Next-Session Completion Criteria

**Goal**: Convert the next-session execution handoff into a read-only completion criteria sheet with done conditions, blocked conditions, retry conditions, verification entrypoints, first action, target candidates, and recommended processing order, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T207 [P] Add red unit tests for criteria status, first action, first-action targets, target candidates, done conditions, blocked conditions, retry conditions, verification entrypoints, close-first behavior, correction-first prioritization, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T208 [P] Add a report-boundary regression test proving next-session completion criteria generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T209 Add `CandidateReviewManualApplicationNextSessionCompletionCriteria` in `src/mingli_engine/models.py`
- [X] T210 Implement `build_pending_candidate_review_manual_application_next_session_completion_criteria()` and `render_pending_candidate_review_manual_application_next_session_completion_criteria_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T211 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session completion criteria command, done/blocked/retry conditions, verification entrypoints, target candidates, recommended processing order, and boundary notes
- [X] T212 Run focused, boundary, and full-suite validation after adding the manual application next-session completion criteria

---

## Phase 34: Pending Review Manual Application Next-Session Retry Planner

**Goal**: Expand next-session completion criteria retry conditions into a read-only retry planner with failure entrypoints, retry sequence, target candidates, first action, verification entrypoints, return-to-handoff path, and recommended processing order, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T213 [P] Add red unit tests for retry status, failure entrypoints, retry conditions, retry sequence, first-action targets, target candidates, verification entrypoints, return-to-handoff path, close-first behavior, correction-first prioritization, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T214 [P] Add a report-boundary regression test proving next-session retry planner generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T215 Add `CandidateReviewManualApplicationNextSessionRetryPlanner` in `src/mingli_engine/models.py`
- [X] T216 Implement `build_pending_candidate_review_manual_application_next_session_retry_planner()` and `render_pending_candidate_review_manual_application_next_session_retry_planner_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T217 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session retry planner command, failure entrypoints, retry sequence, return-to-handoff path, verification entrypoints, target candidates, recommended processing order, and boundary notes
- [X] T218 Run focused, boundary, and full-suite validation after adding the manual application next-session retry planner

---

## Phase 35: Pending Review Manual Application Next-Session Final Readiness Summary

**Goal**: Combine next-session completion criteria and retry planner into a read-only final readiness summary with start gate, first action, ready/blocked/retry conditions, failure entrypoints, verification entrypoints, return-to-handoff path, target candidates, and recommended processing order, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T219 [P] Add red unit tests for readiness status, start gate, first action, first-action targets, ready conditions, blocked conditions, retry conditions, failure entrypoints, verification entrypoints, return-to-handoff path, target candidates, recommended processing order, close-first behavior, correction-first prioritization, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T220 [P] Add a report-boundary regression test proving next-session final readiness summary generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T221 Add `CandidateReviewManualApplicationNextSessionFinalReadinessSummary` in `src/mingli_engine/models.py`
- [X] T222 Implement `build_pending_candidate_review_manual_application_next_session_final_readiness_summary()` and `render_pending_candidate_review_manual_application_next_session_final_readiness_summary_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T223 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session final readiness summary command, start gate, first action, ready/blocked/retry conditions, failure entrypoints, verification entrypoints, return-to-handoff path, target candidates, recommended processing order, and boundary notes
- [X] T224 Run focused, boundary, and full-suite validation after adding the manual application next-session final readiness summary

---

## Phase 36: Pending Review Manual Application Next-Session Manual Execution Launch Note

**Goal**: Condense the next-session final readiness summary into a read-only manual execution launch note with launch status, start gate, first command, candidate order, abort conditions, return paths, verification commands, target candidates, and boundary checks, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T225 [P] Add red unit tests for launch status, start gate, first command, first-command targets, candidate order, abort conditions, return paths, verification commands, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T226 [P] Add a report-boundary regression test proving next-session manual execution launch note generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T227 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchNote` in `src/mingli_engine/models.py`
- [X] T228 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_note()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T229 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session manual execution launch note command, launch status, start gate, first command, candidate order, abort conditions, return paths, verification commands, target candidates, and boundary notes
- [X] T230 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution launch note

---

## Phase 37: Pending Review Manual Application Next-Session Manual Execution Launch Audit

**Goal**: Audit the next-session final readiness summary against the manual execution launch note with coverage checks for start gate, first command, candidate order, abort conditions, return paths, verification commands, target candidates, and read-only boundary, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T231 [P] Add red unit tests for audit status, readiness status, launch status, start gate, first command, coverage checks, missing coverage, boundary checks, candidate order, return paths, verification commands, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T232 [P] Add a report-boundary regression test proving next-session manual execution launch audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T233 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchAudit` in `src/mingli_engine/models.py`
- [X] T234 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T235 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session manual execution launch audit command, coverage checks, missing coverage, boundary checks, candidate order, return paths, verification commands, target candidates, and boundary notes
- [X] T236 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution launch audit

---

## Phase 38: Pending Review Manual Application Next-Session Manual Execution Launch Seal

**Goal**: Freeze a ready next-session manual execution launch audit into a read-only launch seal with seal status, audit status, launch status, start gate, sealed first command, sealed candidate order, blocked reasons, seal checks, verification commands, rollback entrypoints, target candidates, and boundary notes, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T237 [P] Add red unit tests for seal status, audit status, launch status, start gate, sealed first command, sealed candidate order, blocked reasons, seal checks, verification commands, rollback entrypoints, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T238 [P] Add a report-boundary regression test proving next-session manual execution launch seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T239 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchSeal` in `src/mingli_engine/models.py`
- [X] T240 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T241 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session manual execution launch seal command, seal status, blocked reasons, seal checks, verification commands, rollback entrypoints, target candidates, and boundary notes
- [X] T242 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution launch seal

---

## Phase 39: Pending Review Manual Application Next-Session Manual Execution Launch Runbook

**Goal**: Expand the next-session manual execution launch seal into a read-only launch runbook with runbook status, seal status, start gate, first step, execution order, step verification, failure rollback, post-completion review, target candidates, and boundary notes, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T243 [P] Add red unit tests for runbook status, seal status, start gate, first step, execution order, step verification, failure rollback, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T244 [P] Add a report-boundary regression test proving next-session manual execution launch runbook generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T245 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbook` in `src/mingli_engine/models.py`
- [X] T246 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T247 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session manual execution launch runbook command, runbook status, first step, execution order, step verification, failure rollback, post-completion review, target candidates, and boundary notes
- [X] T248 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution launch runbook

---

## Phase 40: Pending Review Manual Application Next-Session Manual Execution Launch Runbook Audit

**Goal**: Audit the next-session manual execution launch runbook against the launch seal with coverage checks for first step, candidate order, verification commands, failure rollback, post-completion review, target candidates, and read-only boundary, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T249 [P] Add red unit tests for runbook audit status, runbook status, seal status, first step, coverage checks, missing coverage, candidate order, verification commands, failure rollback, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T250 [P] Add a report-boundary regression test proving next-session manual execution launch runbook audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T251 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAudit` in `src/mingli_engine/models.py`
- [X] T252 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T253 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session manual execution launch runbook audit command, coverage checks, missing coverage, audit status, verification commands, failure rollback, post-completion review, target candidates, and boundary notes
- [X] T254 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution launch runbook audit

---

## Phase 41: Pending Review Manual Application Next-Session Manual Execution Launch Runbook Audit Seal

**Goal**: Freeze a ready next-session manual execution launch runbook audit into a read-only audit seal with seal status, audit status, runbook status, blocked reasons, seal checks, verification commands, rollback entrypoints, post-completion review, target candidates, and boundary notes, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T255 [P] Add red unit tests for runbook audit seal status, audit status, runbook status, launch seal status, sealed first step, blocked reasons, seal checks, verification commands, rollback entrypoints, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T256 [P] Add a report-boundary regression test proving next-session manual execution launch runbook audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T257 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAuditSeal` in `src/mingli_engine/models.py`
- [X] T258 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T259 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the next-session manual execution launch runbook audit seal command, seal status, audit status, runbook status, blocked reasons, seal checks, verification commands, rollback entrypoints, post-completion review, target candidates, and boundary notes
- [X] T260 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution launch runbook audit seal

---

## Phase 42: Pending Review Manual Application Next-Session Manual Execution Final Launch Packet

**Goal**: Compress the next-session manual execution launch runbook audit seal into a final read-only launch packet with launch packet status, sealed first step, candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T261 [P] Add red unit tests for final launch packet status, audit seal status, sealed first step, candidate order, operator start checklist, verification checklist, rollback path, post-completion review, boundary confirmation, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T262 [P] Add a report-boundary regression test proving final launch packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T263 Add `CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacket` in `src/mingli_engine/models.py`
- [X] T264 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T265 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the final launch packet command, launch packet status, audit seal status, sealed first step, candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, and boundary confirmation
- [X] T266 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution final launch packet

---

## Phase 43: Pending Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit

**Goal**: Audit the next-session manual execution final launch packet against the launch runbook audit seal with handoff readiness, coverage checks, missing coverage, operator-safe start boundary, candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T267 [P] Add red unit tests for final launch packet handoff readiness, launch packet status, audit seal status, sealed first step, coverage checks, missing coverage, operator-safe start boundary, candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T268 [P] Add a report-boundary regression test proving final launch packet handoff audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T269 Add `CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAudit` in `src/mingli_engine/models.py`
- [X] T270 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T271 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the final launch packet handoff audit command, handoff readiness, coverage checks, missing coverage, operator-safe start boundary, verification checklist, rollback path, post-completion review, target candidates, and boundary confirmation
- [X] T272 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution final launch packet handoff audit

---

## Phase 44: Pending Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit Seal

**Goal**: Freeze the next-session manual execution final launch packet handoff audit into a final read-only operator go/no-go seal with seal status, handoff readiness, go/no-go decision, sealed first step, sealed candidate order, operator-safe start boundary, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T273 [P] Add red unit tests for handoff audit seal status, handoff readiness, go/no-go decision, launch packet status, audit seal status, sealed first step, sealed candidate order, blocked reasons, seal checks, operator-safe start boundary, verification checklist, rollback path, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T274 [P] Add a report-boundary regression test proving final launch packet handoff audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T275 Add `CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAuditSeal` in `src/mingli_engine/models.py`
- [X] T276 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T277 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the final launch packet handoff audit seal command, seal status, handoff readiness, go/no-go decision, operator-safe start boundary, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T278 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution final launch packet handoff audit seal

---

## Phase 45: Pending Review Manual Application Next-Session Manual Execution Operator Go/No-Go Seal Launch Receipt

**Goal**: Compress the next-session manual execution operator go/no-go seal into a final read-only launch receipt with receipt status, seal status, go/no-go decision, receipt decision, signed first step, signed candidate order, operator receipt checklist, pre-execution confirmation, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T279 [P] Add red unit tests for launch receipt status, seal status, handoff readiness, go/no-go decision, receipt decision, signed first step, signed candidate order, operator receipt checklist, pre-execution confirmation, verification checklist, rollback path, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T280 [P] Add a report-boundary regression test proving operator go/no-go seal launch receipt generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T281 Add `CandidateReviewManualApplicationNextSessionManualExecutionOperatorGoNoGoSealLaunchReceipt` in `src/mingli_engine/models.py`
- [X] T282 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T283 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the operator go/no-go seal launch receipt command, receipt status, seal status, go/no-go decision, receipt decision, signed first step, signed candidate order, operator receipt checklist, pre-execution confirmation, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T284 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution operator go/no-go seal launch receipt

---

## Phase 46: Pending Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit

**Goal**: Audit the next-session manual execution launch receipt against the operator go/no-go seal with final boundary readiness, receipt coverage checks, missing coverage, final boundary confirmation, signed first step, signed candidate order, operator receipt checklist, pre-execution confirmation, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T285 [P] Add red unit tests for final boundary readiness, receipt status, seal status, go/no-go decision, receipt decision, signed first step, receipt coverage checks, missing coverage, final boundary confirmation, signed candidate order, operator receipt checklist, pre-execution confirmation, verification checklist, rollback path, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T286 [P] Add a report-boundary regression test proving launch receipt final boundary audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T287 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAudit` in `src/mingli_engine/models.py`
- [X] T288 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T289 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the launch receipt final boundary audit command, final boundary readiness, receipt coverage checks, missing coverage, final boundary confirmation, pre-execution confirmation, signed candidate order, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T290 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution launch receipt final boundary audit

---

## Phase 47: Pending Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal

**Goal**: Freeze the next-session manual execution launch receipt final boundary audit into a final read-only boundary seal with seal status, final boundary readiness, receipt status, go/no-go decision, receipt decision, sealed first step, sealed candidate order, receipt coverage checks, missing coverage, final boundary confirmation, pre-execution confirmation, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T291 [P] Add red unit tests for launch receipt final boundary audit seal status, final boundary readiness, receipt status, go/no-go decision, receipt decision, sealed first step, sealed candidate order, receipt coverage checks, missing coverage, seal checks, final boundary confirmation, pre-execution confirmation, verification checklist, rollback path, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T292 [P] Add a report-boundary regression test proving launch receipt final boundary audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T293 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSeal` in `src/mingli_engine/models.py`
- [X] T294 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T295 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the launch receipt final boundary audit seal command, seal status, final boundary readiness, receipt coverage checks, missing coverage, final boundary confirmation, pre-execution confirmation, sealed candidate order, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T296 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution launch receipt final boundary audit seal

---

## Phase 48: Pending Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal Operator Start Packet

**Goal**: Convert the next-session manual execution launch receipt final boundary audit seal into a final read-only operator start packet with packet status, seal status, final boundary readiness, receipt status, go/no-go decision, receipt decision, start authorization, sealed first step, sealed candidate order, operator start checklist, pre-execution confirmation, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T297 [P] Add red unit tests for operator start packet status, seal status, final boundary readiness, receipt status, go/no-go decision, receipt decision, start authorization, sealed first step, sealed candidate order, operator start checklist, pre-execution confirmation, verification checklist, rollback path, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T298 [P] Add a report-boundary regression test proving operator start packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T299 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacket` in `src/mingli_engine/models.py`
- [X] T300 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T301 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the operator start packet command, packet status, start authorization, sealed first step, sealed candidate order, operator start checklist, pre-execution confirmation, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T302 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution launch receipt final boundary audit seal operator start packet

---

## Phase 49: Pending Review Manual Application Next-Session Manual Execution Operator Start Packet Audit

**Goal**: Audit the next-session manual execution operator start packet against the launch receipt final boundary audit seal with audit status, packet status, seal status, start authorization, coverage checks, missing coverage, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, boundary checks, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T303 [P] Add red unit tests for operator start packet audit status, packet status, seal status, start authorization, coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T304 [P] Add a report-boundary regression test proving operator start packet audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T305 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAudit` in `src/mingli_engine/models.py`
- [X] T306 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T307 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the operator start packet audit command, audit status, coverage checks, missing coverage, boundary checks, sealed first step, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T308 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution operator start packet audit

---

## Phase 50: Pending Review Manual Application Next-Session Manual Execution Operator Start Packet Audit Seal

**Goal**: Freeze the next-session manual execution operator start packet audit into a final read-only audit seal with seal status, audit status, packet status, start authorization, blocked reasons, seal checks, coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T309 [P] Add red unit tests for operator start packet audit seal status, audit status, packet status, start authorization, blocked reasons, seal checks, coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T310 [P] Add a report-boundary regression test proving operator start packet audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T311 Add `CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAuditSeal` in `src/mingli_engine/models.py`
- [X] T312 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T313 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the operator start packet audit seal command, seal status, audit status, packet status, start authorization, blocked reasons, seal checks, coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, and boundary confirmation
- [X] T314 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution operator start packet audit seal

---

## Phase 51: Pending Review Manual Application Next-Session Manual Execution Start Authorization Receipt

**Goal**: Compress the next-session manual execution operator start packet audit seal into a final read-only start authorization receipt with receipt status, seal status, audit status, packet status, start authorization, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, receipt checks, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T315 [P] Add red unit tests for start authorization receipt status, seal status, audit status, packet status, start authorization, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, receipt checks, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T316 [P] Add a report-boundary regression test proving start authorization receipt generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T317 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceipt` in `src/mingli_engine/models.py`
- [X] T318 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T319 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the start authorization receipt command, receipt status, seal status, audit status, packet status, start authorization, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, receipt checks, and boundary confirmation
- [X] T320 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start authorization receipt

---

## Phase 52: Pending Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit

**Goal**: Audit the next-session manual execution start authorization receipt against the operator start packet audit seal with coverage audit status, receipt status, seal status, operator start packet audit status, packet status, start authorization, coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T321 [P] Add red unit tests for start authorization receipt coverage audit status, receipt status, seal status, operator start packet audit status, packet status, start authorization, coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T322 [P] Add a report-boundary regression test proving start authorization receipt coverage audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T323 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAudit` in `src/mingli_engine/models.py`
- [X] T324 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T325 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the start authorization receipt coverage audit command, coverage audit status, receipt status, seal status, operator start packet audit status, packet status, start authorization, coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T326 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start authorization receipt coverage audit

---

## Phase 53: Pending Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit Seal

**Goal**: Freeze the next-session manual execution start authorization receipt coverage audit into a final read-only coverage audit seal with seal status, coverage audit status, receipt status, operator start packet audit seal status, operator start packet audit status, packet status, start authorization, blocked reasons, seal checks, coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T327 [P] Add red unit tests for start authorization receipt coverage audit seal status, coverage audit status, receipt status, operator start packet audit seal status, operator start packet audit status, packet status, start authorization, blocked reasons, seal checks, coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T328 [P] Add a report-boundary regression test proving start authorization receipt coverage audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T329 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAuditSeal` in `src/mingli_engine/models.py`
- [X] T330 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T331 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the start authorization receipt coverage audit seal command, seal status, coverage audit status, receipt status, operator start packet audit seal status, operator start packet audit status, packet status, start authorization, blocked reasons, seal checks, coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, and boundary confirmation
- [X] T332 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start authorization receipt coverage audit seal

---

## Phase 54: Pending Review Manual Application Next-Session Manual Execution Authorization Packet

**Goal**: Compress the next-session manual execution start authorization receipt coverage audit seal into a final read-only manual execution authorization packet with packet status, seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, authorization checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T333 [P] Add red unit tests for manual execution authorization packet status, seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, authorization checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T334 [P] Add a report-boundary regression test proving manual execution authorization packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T335 Add `CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacket` in `src/mingli_engine/models.py`
- [X] T336 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T337 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution authorization packet command, packet status, seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, authorization checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T338 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution authorization packet

---

## Phase 55: Pending Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit

**Goal**: Audit the next-session manual execution authorization packet against the start authorization receipt coverage audit seal with audit status, packet status, seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, packet coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T339 [P] Add red unit tests for manual execution authorization packet coverage audit status, packet status, seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, packet coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T340 [P] Add a report-boundary regression test proving manual execution authorization packet coverage audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T341 Add `CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAudit` in `src/mingli_engine/models.py`
- [X] T342 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T343 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution authorization packet coverage audit command, audit status, packet status, seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, packet coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T344 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution authorization packet coverage audit

---

## Phase 56: Pending Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit Seal

**Goal**: Freeze the next-session manual execution authorization packet coverage audit into a final read-only audit seal with seal status, audit status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, seal checks, packet coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T345 [P] Add red unit tests for manual execution authorization packet coverage audit seal status, audit status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, seal checks, packet coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T346 [P] Add a report-boundary regression test proving manual execution authorization packet coverage audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T347 Add `CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSeal` in `src/mingli_engine/models.py`
- [X] T348 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T349 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution authorization packet coverage audit seal command, seal status, audit status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, seal checks, packet coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T350 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution authorization packet coverage audit seal

---

## Phase 57: Pending Review Manual Application Next-Session Manual Execution Start Docket

**Goal**: Compress the next-session manual execution authorization packet coverage audit seal into a final read-only start docket with docket status, seal status, audit status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, docket checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T351 [P] Add red unit tests for manual execution start docket status, seal status, audit status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, docket checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T352 [P] Add a report-boundary regression test proving manual execution start docket generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T353 Add `CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSealStartDocket` in `src/mingli_engine/models.py`
- [X] T354 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T355 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start docket command, docket status, seal status, audit status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, docket checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T356 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start docket

---

## Phase 58: Pending Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit

**Goal**: Audit the next-session manual execution start docket against the authorization packet coverage audit seal with audit status, docket status, seal status, audit source status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, docket coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T357 [P] Add red unit tests for manual execution start docket coverage audit status, docket status, seal status, audit source status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, docket coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T358 [P] Add a report-boundary regression test proving manual execution start docket coverage audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T359 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAudit` in `src/mingli_engine/models.py`
- [X] T360 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T361 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start docket coverage audit command, audit status, docket status, seal status, audit source status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, docket coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T362 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start docket coverage audit

---

## Phase 59: Pending Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit Seal

**Goal**: Freeze the next-session manual execution start docket coverage audit into a final read-only coverage audit seal with seal status, audit status, docket status, source seal status, audit source status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, seal checks, docket coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T363 [P] Add red unit tests for manual execution start docket coverage audit seal status, audit status, docket status, source seal status, audit source status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, seal checks, docket coverage checks, missing coverage, boundary checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T364 [P] Add a report-boundary regression test proving manual execution start docket coverage audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T365 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSeal` in `src/mingli_engine/models.py`
- [X] T366 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T367 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start docket coverage audit seal command, seal status, audit status, docket status, source seal status, audit source status, packet status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, seal checks, docket coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T368 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start docket coverage audit seal

---

## Phase 60: Pending Review Manual Application Next-Session Manual Execution Final Start Packet

**Goal**: Compress the manual execution start docket coverage audit seal into a final read-only start packet with packet status, seal status, audit status, docket status, source seal status, audit source status, packet source status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, packet checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T369 [P] Add red unit tests for manual execution final start packet status, seal status, audit status, docket status, source seal status, audit source status, packet source status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, packet checks, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T370 [P] Add a report-boundary regression test proving manual execution final start packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T371 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSealFinalStartPacket` in `src/mingli_engine/models.py`
- [X] T372 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T373 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution final start packet command, packet status, seal status, audit status, docket status, source seal status, audit source status, packet source status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, packet checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T374 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution final start packet

---

## Phase 61: Pending Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit

**Goal**: Audit the manual execution final start packet against the sealed start docket coverage audit before operator handoff with handoff readiness, packet status, seal status, audit status, docket status, source seal status, audit source status, packet source status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, coverage checks, missing coverage, boundary checks, operator-safe start boundary, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T375 [P] Add red unit tests for manual execution final start packet handoff audit readiness, packet status, seal status, audit status, docket status, source seal status, audit source status, packet source status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, coverage checks, missing coverage, boundary checks, operator-safe start boundary, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T376 [P] Add a report-boundary regression test proving manual execution final start packet handoff audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T377 Add `CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAudit` in `src/mingli_engine/models.py`
- [X] T378 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T379 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution final start packet handoff audit command, handoff readiness, packet status, seal status, audit status, docket status, source seal status, audit source status, packet source status, authorization packet seal status, coverage audit status, receipt status, operator start packet audit status, start authorization, coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T380 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution final start packet handoff audit

---

## Phase 62: Pending Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit Seal

**Goal**: Freeze the manual execution final start packet handoff audit into a final read-only start seal with seal status, handoff readiness, go/no-go start decision, packet status, seal source status, audit status, docket status, start authorization, seal checks, coverage checks, missing coverage, boundary checks, operator-safe start boundary, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T381 [P] Add red unit tests for manual execution final start packet handoff audit seal status, handoff readiness, go/no-go start decision, packet status, seal source status, audit status, docket status, start authorization, seal checks, coverage checks, missing coverage, boundary checks, operator-safe start boundary, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T382 [P] Add a report-boundary regression test proving manual execution final start packet handoff audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T383 Add `CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSeal` in `src/mingli_engine/models.py`
- [X] T384 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T385 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution final start packet handoff audit seal command, seal status, handoff readiness, go/no-go start decision, packet status, seal source status, audit status, docket status, start authorization, seal checks, coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T386 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution final start packet handoff audit seal

---

## Phase 63: Pending Review Manual Application Next-Session Manual Execution Start Authorization Packet

**Goal**: Compress the manual execution final start packet handoff audit seal into a final read-only start authorization packet with packet status, seal status, handoff readiness, go/no-go start decision, start authorization, audit status, docket status, authorization checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T387 [P] Add red unit tests for manual execution start authorization packet status, seal status, handoff readiness, go/no-go start decision, start authorization, audit status, docket status, authorization checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T388 [P] Add a report-boundary regression test proving manual execution start authorization packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T389 Add `CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSealStartAuthorizationPacket` in `src/mingli_engine/models.py`
- [X] T390 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T391 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start authorization packet command, packet status, seal status, handoff readiness, go/no-go start decision, start authorization, authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T392 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start authorization packet

---

## Phase 64: Pending Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit

**Goal**: Audit the manual execution start authorization packet against the final start packet handoff audit seal with audit status, packet status, seal status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, packet coverage checks, missing coverage, boundary checks, authorization checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T393 [P] Add red unit tests for manual execution start authorization packet coverage audit status, packet status, seal status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, packet coverage checks, missing coverage, boundary checks, authorization checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T394 [P] Add a report-boundary regression test proving manual execution start authorization packet coverage audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T395 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAudit` in `src/mingli_engine/models.py`
- [X] T396 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T397 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start authorization packet coverage audit command, audit status, packet status, seal status, handoff readiness, go/no-go start decision, start authorization, coverage checks, missing coverage, boundary checks, authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T398 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start authorization packet coverage audit

---

## Phase 65: Pending Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit Seal

**Goal**: Freeze the manual execution start authorization packet coverage audit into a final read-only coverage audit seal with seal status, audit status, packet status, seal source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, seal checks, packet coverage checks, missing coverage, boundary checks, authorization checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T399 [P] Add red unit tests for manual execution start authorization packet coverage audit seal status, audit status, packet status, seal source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, seal checks, packet coverage checks, missing coverage, boundary checks, authorization checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T400 [P] Add a report-boundary regression test proving manual execution start authorization packet coverage audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T401 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSeal` in `src/mingli_engine/models.py`
- [X] T402 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T403 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start authorization packet coverage audit seal command, seal status, audit status, packet status, seal source status, handoff readiness, go/no-go start decision, start authorization, seal checks, coverage checks, missing coverage, boundary checks, authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T404 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start authorization packet coverage audit seal

---

## Phase 66: Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet

**Goal**: Compress the manual execution start authorization packet coverage audit seal into a final read-only manual execution start clearance packet with packet status, seal status, audit status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T405 [P] Add red unit tests for manual execution start clearance packet status, seal status, audit status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T406 [P] Add a report-boundary regression test proving manual execution start clearance packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T407 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacket` in `src/mingli_engine/models.py`
- [X] T408 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T409 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start clearance packet command, packet status, seal status, audit status, packet source status, handoff readiness, go/no-go start decision, start authorization, clearance checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T410 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start clearance packet

---

## Phase 67: Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit

**Goal**: Audit the manual execution start clearance packet against the start authorization packet coverage audit seal with audit status, packet status, seal status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T411 [P] Add red unit tests for manual execution start clearance packet coverage audit status, packet status, seal status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T412 [P] Add a report-boundary regression test proving manual execution start clearance packet coverage audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T413 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAudit` in `src/mingli_engine/models.py`
- [X] T414 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T415 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start clearance packet coverage audit command, audit status, packet status, seal status, packet source status, handoff readiness, go/no-go start decision, start authorization, coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T416 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start clearance packet coverage audit

---

## Phase 68: Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit Seal

**Goal**: Freeze the manual execution start clearance packet coverage audit into a read-only coverage audit seal with seal status, audit status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, seal checks, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T417 [P] Add red unit tests for manual execution start clearance packet coverage audit seal status, audit status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, seal checks, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T418 [P] Add a report-boundary regression test proving manual execution start clearance packet coverage audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T419 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSeal` in `src/mingli_engine/models.py`
- [X] T420 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T421 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start clearance packet coverage audit seal command, seal status, audit status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, seal checks, coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T422 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start clearance packet coverage audit seal

---

## Phase 69: Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization

**Goal**: Compress the manual execution start clearance packet coverage audit seal into a read-only final start authorization with authorization status, seal status, audit status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, authorization checks, seal checks, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T423 [P] Add red unit tests for manual execution start clearance packet final start authorization status, seal status, audit status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, authorization checks, seal checks, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T424 [P] Add a report-boundary regression test proving manual execution start clearance packet final start authorization generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T425 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorization` in `src/mingli_engine/models.py`
- [X] T426 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T427 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start clearance packet final start authorization command, authorization status, seal status, audit status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, authorization checks, seal checks, coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T428 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start clearance packet final start authorization

---

## Phase 70: Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit

**Goal**: Audit the manual execution start clearance packet final start authorization against the coverage audit seal with audit status, authorization status, seal status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, authorization coverage checks, authorization checks, seal checks, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T429 [P] Add red unit tests for manual execution start clearance packet final start authorization coverage audit status, authorization status, seal status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, authorization coverage checks, authorization checks, seal checks, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T430 [P] Add a report-boundary regression test proving manual execution start clearance packet final start authorization coverage audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T431 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAudit` in `src/mingli_engine/models.py`
- [X] T432 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T433 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start clearance packet final start authorization coverage audit command, audit status, authorization status, seal status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, authorization coverage checks, authorization checks, seal checks, coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T434 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start clearance packet final start authorization coverage audit

---

## Phase 71: Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit Seal

**Goal**: Freeze the manual execution start clearance packet final start authorization coverage audit into a read-only audit seal with seal status, audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T435 [P] Add red unit tests for manual execution start clearance packet final start authorization coverage audit seal status, audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T436 [P] Add a report-boundary regression test proving manual execution start clearance packet final start authorization coverage audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T437 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSeal` in `src/mingli_engine/models.py`
- [X] T438 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T439 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start clearance packet final start authorization coverage audit seal command, seal status, audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T440 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start clearance packet final start authorization coverage audit seal

---

## Phase 72: Pending Review Manual Application Next-Session Manual Execution Start Handoff Packet

**Goal**: Compress the manual execution start clearance packet final start authorization coverage audit seal into a read-only operator-facing start handoff packet with handoff packet status, handoff status, seal status, audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, handoff checks, seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T441 [P] Add red unit tests for manual execution start handoff packet status, handoff status, seal status, audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, handoff checks, seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, missing coverage, boundary checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T442 [P] Add a report-boundary regression test proving manual execution start handoff packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T443 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacket` in `src/mingli_engine/models.py`
- [X] T444 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T445 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start handoff packet command, handoff packet status, handoff status, seal status, audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, handoff checks, operator start checklist, coverage checks, missing coverage, boundary checks, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T446 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start handoff packet

---

## Phase 73: Pending Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit

**Goal**: Audit the manual execution start handoff packet against the final start authorization coverage audit seal with audit status, handoff packet status, handoff status, seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, coverage checks, missing coverage, boundary checks, handoff checks, seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T447 [P] Add red unit tests for manual execution start handoff packet coverage audit status, handoff packet status, handoff status, seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, coverage checks, missing coverage, boundary checks, handoff checks, seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T448 [P] Add a report-boundary regression test proving manual execution start handoff packet coverage audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T449 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAudit` in `src/mingli_engine/models.py`
- [X] T450 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T451 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start handoff packet coverage audit command, audit status, handoff packet status, handoff status, seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, coverage checks, missing coverage, boundary checks, handoff checks, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T452 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start handoff packet coverage audit

---

## Phase 74: Pending Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit Seal

**Goal**: Freeze the manual execution start handoff packet coverage audit into a read-only audit seal with seal status, audit status, handoff packet status, handoff status, final start authorization coverage audit seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, seal checks, coverage checks, missing coverage, boundary checks, handoff checks, source seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T453 [P] Add red unit tests for manual execution start handoff packet coverage audit seal status, audit status, handoff packet status, handoff status, final start authorization coverage audit seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, seal checks, coverage checks, missing coverage, boundary checks, handoff checks, source seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T454 [P] Add a report-boundary regression test proving manual execution start handoff packet coverage audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T455 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSeal` in `src/mingli_engine/models.py`
- [X] T456 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T457 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start handoff packet coverage audit seal command, seal status, audit status, handoff packet status, handoff status, final start authorization coverage audit seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, seal checks, coverage checks, missing coverage, boundary checks, handoff checks, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T458 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start handoff packet coverage audit seal

---

## Phase 75: Pending Review Manual Application Next-Session Manual Execution Start Packet

**Goal**: Compress the manual execution start handoff packet coverage audit seal into a read-only operator-facing start packet with start packet status, seal status, audit status, handoff packet status, handoff status, final start authorization coverage audit seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, start checks, seal checks, coverage checks, missing coverage, boundary checks, handoff checks, source seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T459 [P] Add red unit tests for manual execution start packet status, seal status, audit status, handoff packet status, handoff status, final start authorization coverage audit seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, start checks, seal checks, coverage checks, missing coverage, boundary checks, handoff checks, source seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T460 [P] Add a report-boundary regression test proving manual execution start packet generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T461 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacket` in `src/mingli_engine/models.py`
- [X] T462 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T463 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start packet command, start packet status, seal status, audit status, handoff packet status, handoff status, final start authorization coverage audit seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, start checks, seal checks, coverage checks, missing coverage, boundary checks, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T464 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start packet

---

## Phase 76: Pending Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit

**Goal**: Audit the manual execution start packet against the start handoff packet coverage audit seal with audit status, start packet status, seal status, start packet source audit status, handoff packet status, handoff status, final start authorization coverage audit seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, coverage checks, source coverage checks, missing coverage, boundary checks, start checks, seal checks, handoff checks, source seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T465 [P] Add red unit tests for manual execution start packet coverage audit status, start packet status, seal status, start packet source audit status, handoff packet status, handoff status, final start authorization coverage audit seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, source audit status, docket status, coverage checks, source coverage checks, missing coverage, boundary checks, start checks, seal checks, handoff checks, source seal checks, authorization coverage checks, authorization checks, coverage seal checks, packet coverage checks, clearance checklist, sealed first step, sealed candidate order, operator authorization checklist, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T466 [P] Add a report-boundary regression test proving manual execution start packet coverage audit generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T467 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAudit` in `src/mingli_engine/models.py`
- [X] T468 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T469 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start packet coverage audit command, audit status, start packet status, seal status, start packet source audit status, handoff packet status, handoff status, final start authorization coverage audit seal status, coverage audit status, authorization status, packet status, seal source status, packet source status, handoff readiness, go/no-go start decision, start authorization, coverage checks, source coverage checks, missing coverage, boundary checks, operator start checklist, verification checklist, rollback path, post-completion review, target candidates, blocked reasons, and boundary confirmation
- [X] T470 Run focused, boundary, and full-suite validation after adding the manual application next-session manual execution start packet coverage audit

---

## Phase 77: Pending Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit Seal

**Goal**: Freeze the manual execution start packet coverage audit into a read-only audit seal with seal status, audit status, start packet status, start packet source audit status, seal checks, coverage checks, source coverage checks, missing coverage, boundary checks, blocked reasons, target candidates, boundary confirmation, and zero applied/formal-evidence deltas, without writing review decisions, updating candidate status, promoting candidates, or changing formal evidence.

- [X] T471 [P] Add red unit tests for manual execution start packet coverage audit seal status, audit status, start packet status, start packet source audit status, seal checks, coverage checks, source coverage checks, missing coverage, boundary checks, start checks, operator start checklist, sealed first step, sealed candidate order, target candidates, blocked reasons, close-first behavior, Markdown rendering, and zero applied/formal-evidence deltas in `tests/unit/test_source_intake.py`
- [X] T472 [P] Add a report-boundary regression test proving manual execution start packet coverage audit seal generation does not write review decisions, candidate statuses, or formal evidence in `tests/integration/test_report_regression_cases.py`
- [X] T473 Add `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAuditSeal` in `src/mingli_engine/models.py`
- [X] T474 Implement `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal()` and `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal_markdown()` in `src/mingli_engine/source_intake.py`
- [X] T475 Update `specs/013-source-extraction-workflow/quickstart.md` and `docs/classical_sources/intake.md` with the manual execution start packet coverage audit seal command, seal status, audit status, start packet status, start packet source audit status, seal checks, coverage checks, source coverage checks, missing coverage, boundary checks, target candidates, blocked reasons, and boundary confirmation
- [X] T476 Run targeted, focused, boundary, and full-suite validation after adding the manual application next-session manual execution start packet coverage audit seal

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies
- **Phase 2 Foundational**: Depends on Phase 1; blocks every user story
- **Phase 3 US1**: Depends on Phase 2; MVP scope
- **Phase 4 US2**: Depends on Phase 2 and may reuse US1 candidate loading
- **Phase 5 US3**: Depends on Phase 2 and benefits from US1/US2 data, but its validation can be tested independently with fixtures
- **Phase 6 US4**: Depends on Phase 2 and can summarize any implemented subset, but full value comes after US1-US3
- **Phase 7 Polish**: Depends on selected stories being complete
- **Phase 8 Pending Candidate Review Worklist**: Depends on 017 candidate application and preserves the boundary before human review decisions
- **Phase 9 Pending Candidate Review Decision Packets**: Depends on Phase 8 and prepares human review decisions without writing them automatically
- **Phase 10 Pending Review Packet Dashboard**: Depends on Phase 9 and summarizes manual-review blockers without writing decisions or evidence
- **Phase 11 Pending Review Action Queue**: Depends on Phase 10 and selects the next manual action per pending candidate without writing decisions or evidence
- **Phase 12 Pending Review Markdown Checklist**: Depends on Phase 11 and renders the action queue for manual sessions without writing files or evidence
- **Phase 13 Pending Review Input Templates**: Depends on Phase 12 and provides fillable review input templates without writing review decisions or formal evidence
- **Phase 14 Pending Review Draft Validation**: Depends on Phase 13 and validates filled templates before manual review-decision writes without mutating data
- **Phase 15 Pending Review Application Guard**: Depends on Phase 14 and previews manual data changes without writing JSON or changing formal evidence
- **Phase 16 Pending Review Application Packets**: Depends on Phase 15 and exports copyable manual-application packets without mutating data
- **Phase 17 Pending Review Application Audit Summary**: Depends on Phase 16 and summarizes manual application readiness without mutating data
- **Phase 18 Pending Review Manual Action Dashboard**: Depends on Phase 17 and groups the shortest next manual actions into execution lanes without mutating data
- **Phase 19 Pending Review Manual Application Dry-Run Guide**: Depends on Phase 18 and expands the recommended action order into candidate-level dry-run steps without mutating data
- **Phase 20 Pending Review Manual Application Preflight Report**: Depends on Phase 19 and verifies ready packets before manual application without mutating data
- **Phase 21 Pending Review Manual Application Handoff Summary**: Depends on Phase 20 and combines dashboard, dry-run, and preflight outputs into a human execution sheet without mutating data
- **Phase 22 Pending Review Manual Application Readiness Ledger**: Depends on Phase 21 and renders the handoff as unchecked maintainer ledger rows without mutating data
- **Phase 23 Pending Review Manual Application Session Packet**: Depends on Phase 22 and compresses ledger rows into a ready-first manual session packet without mutating data
- **Phase 24 Pending Review Manual Application Session Outcome Preview**: Depends on Phase 23 and previews ready-only session outcomes plus remaining follow-ups without mutating data
- **Phase 25 Pending Review Manual Application Post-Session Verification Report**: Depends on Phase 24 and verifies manual ready-action outcomes against current data without mutating data
- **Phase 26 Pending Review Manual Application Reconciliation Dashboard**: Depends on Phase 25 and groups verification outcomes into next manual actions without mutating data
- **Phase 27 Pending Review Manual Application Closure Packet**: Depends on Phase 26 and separates verified session closure items from next-session carry-forward items without mutating data
- **Phase 28 Pending Review Manual Application Next-Session Starter**: Depends on Phase 27 and turns carry-forward items into lane-specific next-session starter checklists without mutating data
- **Phase 29 Pending Review Manual Application Next-Session Packet**: Depends on Phase 28 and compresses starter lanes into correction and follow-up queues without mutating data
- **Phase 30 Pending Review Manual Application Next-Session Audit Summary**: Depends on Phase 29 and verifies closure/starter/packet coverage without mutating data
- **Phase 31 Pending Review Manual Application Next-Session Operator Checklist**: Depends on Phase 30 and expands audited next actions into human operator checklist rows without mutating data
- **Phase 32 Pending Review Manual Application Next-Session Execution Handoff**: Depends on Phase 31 and condenses operator checklist rows into a one-page human execution handoff without mutating data
- **Phase 33 Pending Review Manual Application Next-Session Completion Criteria**: Depends on Phase 32 and converts execution handoff rows into done/blocked/retry criteria without mutating data
- **Phase 34 Pending Review Manual Application Next-Session Retry Planner**: Depends on Phase 33 and expands retry conditions into failure entrypoints and retry sequence without mutating data
- **Phase 35 Pending Review Manual Application Next-Session Final Readiness Summary**: Depends on Phase 34 and combines completion criteria plus retry planner into a final start-gate summary without mutating data
- **Phase 36 Pending Review Manual Application Next-Session Manual Execution Launch Note**: Depends on Phase 35 and condenses final readiness into a one-page launch note without mutating data
- **Phase 37 Pending Review Manual Application Next-Session Manual Execution Launch Audit**: Depends on Phase 36 and audits launch-note coverage of final readiness without mutating data
- **Phase 38 Pending Review Manual Application Next-Session Manual Execution Launch Seal**: Depends on Phase 37 and freezes a ready launch audit into a final read-only launch seal without mutating data
- **Phase 39 Pending Review Manual Application Next-Session Manual Execution Launch Runbook**: Depends on Phase 38 and expands the launch seal into a final read-only execution runbook without mutating data
- **Phase 40 Pending Review Manual Application Next-Session Manual Execution Launch Runbook Audit**: Depends on Phase 39 and audits launch-runbook coverage of the launch seal without mutating data
- **Phase 41 Pending Review Manual Application Next-Session Manual Execution Launch Runbook Audit Seal**: Depends on Phase 40 and freezes a ready launch-runbook audit into a final read-only audit seal without mutating data
- **Phase 42 Pending Review Manual Application Next-Session Manual Execution Final Launch Packet**: Depends on Phase 41 and compresses the audit seal into a final read-only launch packet without mutating data
- **Phase 43 Pending Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit**: Depends on Phase 42 and audits final launch packet handoff coverage before operator start without mutating data
- **Phase 44 Pending Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit Seal**: Depends on Phase 43 and freezes final launch packet handoff readiness into a read-only operator go/no-go seal without mutating data
- **Phase 45 Pending Review Manual Application Next-Session Manual Execution Operator Go/No-Go Seal Launch Receipt**: Depends on Phase 44 and compresses the operator go/no-go seal into a read-only pre-execution receipt without mutating data
- **Phase 46 Pending Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit**: Depends on Phase 45 and audits launch receipt boundary coverage against the operator go/no-go seal without mutating data
- **Phase 47 Pending Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal**: Depends on Phase 46 and freezes launch receipt final boundary audit readiness into a read-only boundary seal without mutating data
- **Phase 48 Pending Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal Operator Start Packet**: Depends on Phase 47 and converts the boundary seal into a read-only operator start packet without mutating data
- **Phase 49 Pending Review Manual Application Next-Session Manual Execution Operator Start Packet Audit**: Depends on Phase 48 and audits operator start packet coverage of the boundary seal without mutating data
- **Phase 50 Pending Review Manual Application Next-Session Manual Execution Operator Start Packet Audit Seal**: Depends on Phase 49 and freezes a ready operator start packet audit into a read-only audit seal without mutating data
- **Phase 51 Pending Review Manual Application Next-Session Manual Execution Start Authorization Receipt**: Depends on Phase 50 and compresses the audit seal into a read-only start authorization receipt without mutating data
- **Phase 52 Pending Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit**: Depends on Phase 51 and audits start authorization receipt coverage of the operator start packet audit seal without mutating data
- **Phase 53 Pending Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit Seal**: Depends on Phase 52 and freezes a ready start authorization receipt coverage audit into a read-only coverage audit seal without mutating data
- **Phase 54 Pending Review Manual Application Next-Session Manual Execution Authorization Packet**: Depends on Phase 53 and compresses the coverage audit seal into a read-only manual execution authorization packet without mutating data
- **Phase 55 Pending Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit**: Depends on Phase 54 and audits manual execution authorization packet coverage of the coverage audit seal without mutating data
- **Phase 56 Pending Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit Seal**: Depends on Phase 55 and freezes a ready manual execution authorization packet coverage audit into a read-only audit seal without mutating data
- **Phase 57 Pending Review Manual Application Next-Session Manual Execution Start Docket**: Depends on Phase 56 and compresses the authorization packet coverage audit seal into a read-only start docket without mutating data
- **Phase 58 Pending Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit**: Depends on Phase 57 and audits start docket coverage of the authorization packet coverage audit seal without mutating data
- **Phase 59 Pending Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit Seal**: Depends on Phase 58 and freezes a ready start docket coverage audit into a read-only coverage audit seal without mutating data
- **Phase 60 Pending Review Manual Application Next-Session Manual Execution Final Start Packet**: Depends on Phase 59 and compresses the coverage audit seal into a final read-only start packet without mutating data
- **Phase 61 Pending Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit**: Depends on Phase 60 and audits final start packet handoff coverage before operator start without mutating data
- **Phase 62 Pending Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit Seal**: Depends on Phase 61 and freezes final start packet handoff readiness into a read-only start seal without mutating data
- **Phase 63 Pending Review Manual Application Next-Session Manual Execution Start Authorization Packet**: Depends on Phase 62 and compresses the start seal into a read-only start authorization packet without mutating data
- **Phase 64 Pending Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit**: Depends on Phase 63 and audits start authorization packet coverage of the start seal without mutating data
- **Phase 65 Pending Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit Seal**: Depends on Phase 64 and freezes start authorization packet coverage audit readiness into a read-only coverage audit seal without mutating data
- **Phase 66 Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet**: Depends on Phase 65 and compresses start authorization packet coverage audit seal readiness into a read-only start clearance packet without mutating data
- **Phase 67 Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit**: Depends on Phase 66 and audits start clearance packet coverage of the coverage audit seal without mutating data
- **Phase 68 Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit Seal**: Depends on Phase 67 and freezes start clearance packet coverage audit readiness into a read-only coverage audit seal without mutating data
- **Phase 69 Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization**: Depends on Phase 68 and compresses the coverage audit seal into a read-only final start authorization without mutating data
- **Phase 70 Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit**: Depends on Phase 69 and audits final start authorization coverage of the coverage audit seal without mutating data
- **Phase 71 Pending Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit Seal**: Depends on Phase 70 and freezes final start authorization coverage audit readiness into a read-only audit seal without mutating data
- **Phase 72 Pending Review Manual Application Next-Session Manual Execution Start Handoff Packet**: Depends on Phase 71 and compresses the final start authorization coverage audit seal into a read-only operator-facing start handoff packet without mutating data
- **Phase 73 Pending Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit**: Depends on Phase 72 and audits start handoff packet coverage of the final start authorization coverage audit seal without mutating data
- **Phase 74 Pending Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit Seal**: Depends on Phase 73 and freezes start handoff packet coverage audit readiness into a read-only audit seal without mutating data
- **Phase 75 Pending Review Manual Application Next-Session Manual Execution Start Packet**: Depends on Phase 74 and compresses start handoff packet coverage audit seal readiness into a read-only operator-facing start packet without mutating data
- **Phase 76 Pending Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit**: Depends on Phase 75 and audits start packet coverage of the start handoff packet coverage audit seal without mutating data
- **Phase 77 Pending Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit Seal**: Depends on Phase 76 and freezes start packet coverage audit readiness into a read-only audit seal without mutating data

### User Story Dependencies

- **US1 Register Candidate Extracts**: Required MVP; no dependency on other stories after Foundation
- **US2 Review Candidate Evidence**: Uses candidates from US1 but can be tested with isolated fixtures
- **US3 Record Conflicts, Gaps, and Rejections**: Uses candidate and review concepts; can be tested with isolated fixtures
- **US4 View Intake Progress**: Uses all intake entities; can be tested with isolated fixtures and then project data

### Within Each Story

- Write failing tests first
- Implement minimal model or loader behavior
- Add or update seed JSON data
- Run focused tests for the story
- Stop at checkpoint and report status before moving to the next phase

---

## Parallel Opportunities

- T002 and T003 can run in parallel after T001
- T005 and T007 can run in parallel because they are separate test groups in the same file but should be merged carefully
- Within each story, tasks marked [P] are tests or docs that can be prepared before implementation
- US2, US3, and US4 can be planned in parallel after Foundation, but this project should execute them sequentially to satisfy staged reporting

---

## Parallel Example: User Story 1

```text
Task: "Add failing tests for valid and invalid SourceMaterial records in tests/unit/test_source_intake.py"
Task: "Add failing tests for candidate required fields, pending-review eligibility, and invalid statuses in tests/unit/test_source_intake.py"
Task: "Add failing tests that candidate extracted_meaning and short_quote reject long copied passages and absolute outcome language in tests/unit/test_source_intake.py"
Task: "Add a report-boundary regression test proving pending candidates are excluded from formal evidence loading in tests/integration/test_report_regression_cases.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 Setup
2. Complete Phase 2 Foundation
3. Complete Phase 3 US1
4. Run focused US1 tests
5. Stop and report before US2

### Incremental Delivery

1. US1 creates a safe candidate queue
2. US2 adds review decisions and promotion readiness
3. US3 adds auditability for conflicts, gaps, duplicates, and rejection reasons
4. US4 adds progress reporting
5. Polish runs safety and full-suite validation
6. Phase 8 surfaces current pending candidates for review planning without approving, rejecting, or promoting them
7. Phase 9 prepares review-decision packets with required manual inputs and approval blockers, still without mutating review decisions or formal evidence
8. Phase 10 summarizes those packets into dashboard counts so the next human-review pass can start with the largest blockers
9. Phase 11 turns the dashboard into a per-candidate action queue for the next manual review pass
10. Phase 12 renders that action queue as a stable Markdown checklist for manual review sessions
11. Phase 13 renders fillable input templates for the next human review session
12. Phase 14 validates filled review-decision drafts before any manual data write
13. Phase 15 previews review-decision and candidate-status changes before manual application
14. Phase 16 exports ready previews as copyable manual application packets
15. Phase 17 summarizes manual-application readiness and next actions across all pending candidates
16. Phase 18 groups those next actions into a manual execution dashboard and recommended processing order
17. Phase 19 expands the dashboard into per-candidate dry-run steps, ready criteria, post-apply checks, and rollback notes
18. Phase 20 verifies manual application readiness with decision-id uniqueness, pending-status patch, and packet-delta checks
19. Phase 21 combines the dashboard, dry-run guide, and preflight report into one human execution handoff
20. Phase 22 renders the handoff into unchecked readiness ledger rows for manual execution
21. Phase 23 compresses readiness ledger rows into a ready-first session packet with follow-ups and verification
22. Phase 24 previews ready-only session outcomes and remaining pending follow-ups before any manual data write
23. Phase 25 verifies actual post-session data against the ready-only outcome preview without performing repairs
24. Phase 26 reconciles verification outcomes into the next manual action dashboard without performing repairs
25. Phase 27 packages reconciliation outcomes into session closure and carry-forward lanes without performing repairs
26. Phase 28 starts the next manual session from carry-forward lanes and checklists without performing repairs
27. Phase 29 compresses the next-session starter into correction and follow-up queues without performing repairs
28. Phase 30 audits closure, starter, and packet coverage for the next manual session without performing repairs
29. Phase 31 expands audited next actions into operator checklist rows without performing repairs
30. Phase 32 condenses operator checklist rows into a one-page execution handoff without performing repairs
31. Phase 33 converts the execution handoff into done, blocked, and retry criteria without performing repairs
32. Phase 34 expands retry criteria into failure entrypoints and retry sequence without performing repairs
33. Phase 35 combines completion criteria and retry planner into final readiness summary without performing repairs
34. Phase 36 condenses final readiness into a manual execution launch note without performing repairs
35. Phase 37 audits launch-note coverage of final readiness without performing repairs
36. Phase 38 freezes a ready launch audit into a manual execution launch seal without performing repairs
37. Phase 39 expands the launch seal into a manual execution launch runbook without performing repairs
38. Phase 40 audits launch-runbook coverage of the launch seal without performing repairs
39. Phase 41 freezes a ready launch-runbook audit into a final audit seal without performing repairs
40. Phase 42 compresses the audit seal into a final launch packet without performing repairs
41. Phase 43 audits final launch packet handoff coverage before operator start without performing repairs
42. Phase 44 freezes final launch packet handoff readiness into an operator go/no-go seal without performing repairs
43. Phase 45 compresses the operator go/no-go seal into a pre-execution launch receipt without performing repairs
44. Phase 46 audits launch receipt final boundary coverage without performing repairs
45. Phase 47 freezes launch receipt final boundary audit readiness into a boundary seal without performing repairs
46. Phase 48 converts the boundary seal into an operator start packet without performing repairs
47. Phase 49 audits operator start packet coverage of the boundary seal without performing repairs
48. Phase 50 freezes a ready operator start packet audit into an audit seal without performing repairs
49. Phase 51 compresses the audit seal into a start authorization receipt without performing repairs
50. Phase 52 audits start authorization receipt coverage of the audit seal without performing repairs
51. Phase 53 freezes a ready start authorization receipt coverage audit into a coverage audit seal without performing repairs
52. Phase 54 compresses the coverage audit seal into a manual execution authorization packet without performing repairs
53. Phase 55 audits manual execution authorization packet coverage of the coverage audit seal without performing repairs
54. Phase 56 freezes a ready manual execution authorization packet coverage audit into an audit seal without performing repairs
55. Phase 57 compresses the authorization packet coverage audit seal into a manual execution start docket without performing repairs
56. Phase 58 audits manual execution start docket coverage of the authorization packet coverage audit seal without performing repairs
57. Phase 59 freezes a ready manual execution start docket coverage audit into a coverage audit seal without performing repairs
58. Phase 60 compresses the start docket coverage audit seal into a final start packet without performing repairs
59. Phase 61 audits final start packet handoff coverage before operator start without performing repairs
60. Phase 62 freezes final start packet handoff readiness into a start seal without performing repairs
61. Phase 63 compresses the start seal into a start authorization packet without performing repairs
62. Phase 64 audits start authorization packet coverage of the start seal without performing repairs
63. Phase 65 freezes start authorization packet coverage audit readiness into a coverage audit seal without performing repairs
64. Phase 66 compresses the coverage audit seal into a manual execution start clearance packet without performing repairs
65. Phase 67 audits manual execution start clearance packet coverage of the coverage audit seal without performing repairs
66. Phase 68 freezes manual execution start clearance packet coverage audit readiness into a coverage audit seal without performing repairs
67. Phase 69 compresses manual execution start clearance packet coverage audit seal readiness into a final start authorization without performing repairs
68. Phase 70 audits final start authorization coverage of the coverage audit seal without performing repairs
69. Phase 71 freezes final start authorization coverage audit readiness into an audit seal without performing repairs
70. Phase 72 compresses final start authorization coverage audit seal readiness into an operator-facing start handoff packet without performing repairs
71. Phase 73 audits start handoff packet coverage of the final start authorization coverage audit seal without performing repairs
72. Phase 74 freezes start handoff packet coverage audit readiness into an audit seal without performing repairs
73. Phase 75 compresses start handoff packet coverage audit seal readiness into an operator-facing start packet without performing repairs
74. Phase 76 audits start packet coverage of the start handoff packet coverage audit seal without performing repairs
75. Phase 77 freezes start packet coverage audit readiness into an audit seal without performing repairs

### Staged Reporting Rule

After each phase, report:

- tasks completed in that phase
- focused tests run and result
- whether root PDF files and root `Markdown/` stayed untouched
- the next phase the user should approve or expect
