# Quickstart: Learning Reference Curation

## Goal

Use 017 to turn the current 016 extraction queue intake package into learning reference notes, candidate-intake decisions, and prerequisite action notes. The workflow helps maintainers move quickly from newly organized source materials to reviewable project knowledge without crossing candidate or formal-evidence boundaries.

## Current Boundary

- Root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials.
- Do not move, delete, rename, convert, commit, or mutate those materials unless the user explicitly asks.
- 016 extraction tasks and backlog records are planning metadata.
- 017 learning reference notes and candidate-intake decisions are study/reference metadata until an explicit candidate-application step is selected.
- 013 candidate extracts still require review decisions and promotion batches.
- Reports may use only approved and promoted formal evidence units from the reviewed corpus.

## Maintainer Workflow

1. Load the current 016 package summary.
2. Create learning reference notes for the selected ready extraction tasks.
3. Add concise learning points with source trace, locator requirement, rule family, risk tier, and limitations.
4. Check each learning point against existing 013 candidates before creating new candidates.
5. Record candidate-intake decisions: create, reuse, avoid duplicate, defer, or manual review.
6. Preserve registration, preparation, locator-review, risk-review, deferred, and blocked backlog records as prerequisite action notes.
7. Validate high-risk language, copied-passage boundaries, duplicate warnings, and report-evidence boundaries.
8. Use the progress summary to decide the next candidate-intake or prerequisite action.

## Expected Validation Commands

Run the learning reference quality check after implementation:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.learning_reference_curation import build_learning_reference_progress_summary, validate_learning_reference_quality; print(build_learning_reference_progress_summary()); print(validate_learning_reference_quality())"
```

Expected result after implementation:

- The progress summary prints:
  `note_counts={'candidate_intake_started': 29}`,
  `learning_point_counts={'duplicate_review': 3, 'ready': 40, 'deferred': 6}`,
  `decision_counts={'reuse_existing': 3, 'create_candidate': 40, 'status:applied': 43}`,
  `prerequisite_action_counts={'risk_review': 4, 'blocked': 1, 'deferred': 2, 'status:completed': 4, 'status:blocked': 1, 'status:deferred': 2}`,
  `risk_tier_counts={'sensitive': 44, 'ordinary': 37, 'high_risk': 4}`,
  `overlap_warning_count=9`,
  `candidate_ready_count=40`,
  `candidate_decision_count=43`,
  `formal_evidence_delta=0`, and `next_action_ids=[]`.
- The quality check prints `[]`.
- Completed, blocked, and deferred prerequisite actions remain outside
  `next_action_ids`.
- Candidate-intake decisions are applied: three decisions reuse existing
  candidates, and 40 create-candidate decisions have been applied through 013
  intake. The 017 metadata itself still has `formal_evidence_delta=0`; formal
  report evidence comes only from reviewed evidence units.

## Source-Window Learning Closure Sync

The source-window learning-closure pass is an operational sync for maintainer
review, not a candidate or evidence promotion step.

- `selected-ready-learning-notes=31`: the 31 ready items remain selected 016
  extraction tasks and 017 learning reference notes. This means
  learning-reference input readiness, not automatic formal-evidence readiness.
- `retained-chapter-learning-closed=11`: retained chapter-level source windows
  now have explicit learning-closure notes in the extract Markdown.
- `learning-paraphrase-ready=4`: Duan retained chapter windows can be used as
  short paraphrase learning notes. Future transcription is optional unless
  exact quotation, page-level proof, or promotion is needed.
- `policy-boundary-retained=5`: Hongfu remedy-boundary windows stay as policy
  paraphrase material and must not be promoted without human transcription.
- `safety-boundary-retained=2`: Northeast risk-boundary windows stay as safety
  paraphrase material unless a source-specific boundary page is identified.
- `closed-draft-learning-notes=7`: the remaining draft-note maintainer handles
  are closed as `candidate_intake_started` after their learning points and
  candidate-intake decisions were already applied.
- `next_action_ids=0`: no learning note, candidate-intake decision, or
  prerequisite action currently needs active local handling.
- `planned-risk-review-actions=0`: no risk-review prerequisite action remains
  planned after the sweep.
- `completed-risk-review-actions=4`: Blind Life Manual, Immortal Fortune
  Jianghu Secret, Life Death Book, and Markdown Batch 005 have completed
  prerequisite boundary screening.
- `formal_evidence_delta=0`: No new candidate-intake decisions, no 013 candidate extracts, no review decisions, no promotion batches, and no formal evidence are created by this source-window sync; later authorized downstream records are counted in 013/012 snapshots.

Blocked and deferred prerequisite records remain outside `next_action_ids`.

## Authorization Audit Packet

Run the local authorization audit before entering optional downstream 013 or
012 work:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.learning_reference_curation import build_learning_reference_authorization_audit, render_learning_reference_authorization_audit_markdown; print(render_learning_reference_authorization_audit_markdown(build_learning_reference_authorization_audit()))"
```

Expected markers:

- `authorization-status=ready_for_explicit_downstream_authorization`
- `downstream-mutation-authorized=false`
- `017-notes-closed=31`
- `017-next-action-ids=0`
- `012-boundary-leakage=0`
- `next-downstream-entry=013-explicit-candidate-review-or-015-queue-refresh`

This packet is read-only. It confirms that downstream work may be selected only
after an explicit user request; it does not create candidates, review decisions,
promotion batches, or formal evidence.

## Current New-Material Continuation

The 015 raw text next-cycle sensitive preparation reading is complete:

- `sensitive-preparation-reading-status=sensitive_preparation_reading_completed`
- `sensitive-preparation-reading-items=1`
- `safe-reading-notes=3`
- `candidate-intake-ready=0`
- `formal-evidence-ready=0`
- `candidate-extracts=0`
- `formal-evidence=0`
- `downstream-mutation-authorized=false`
- `explicit-routing-status=routed_to_015_queue_refresh`
- `candidate-extract-delta=0`
- `formal-evidence-delta=0`
- `external-inventory-confirmation-status=external_inventory_refresh_confirmed`
- `untracked-material-entries=0`
- `new-material-learning-loop-status=new_material_learning_loop_closed`
- `completed-loop-stages=16`
- `registered-source-entries=11`

Explicit Downstream Authorization Receipt:

- `downstream-authorization-status=downstream_authorization_consumed`
- `authorization-scope=013_012_downstream`
- `pending-017-decisions=0`
- `017-applied-decisions=45`
- `013-candidate-extracts=54`
- `013-review-decisions=54`
- `013-promotion-batches=34`
- `012-formal-evidence-units=111`
- `candidate-extract-delta=0`
- `formal-evidence-delta=0`
- `downstream-mutation-authorized=true`
- `next-downstream-entry=015-new-material-intake`
- `new-material-intake-status=new_material_intake_selected`
- `selected-source-files=1`
- `selected-for-identity-review=1`
- `source-library-mutation-authorized=false`
- `new-material-source-identity-review-status=identity_review_completed`
- `identity-review-items=1`
- `registration-prep-ready=1`
- `source-library-overlap-found=0`
- `candidate-extract-delta=0`
- `formal-evidence-delta=0`
- `new-material-registration-prep-status=registration_prep_completed`
- `new-material-source-registration-status=source_registration_completed`
- `new-material-preparation-boundary-status=preparation_boundary_completed`
- `registered-source-entries=1`
- `text-preparation-required=1`
- `reading-blocked=1`
- `new-material-controlled-text-preparation-status=blocked_requires_ocr_or_manual_transcription`
- `pdf-pages=84`
- `text-layer-nonempty-pages=13`
- `text-layer-chars=592`
- `usable-text-layer=0`
- `new-material-ocr-or-manual-transcription-status=blocked_ocr_runtime_unavailable`
- `pdftoppm-available=1`
- `ocr-runtime-available=0`
- `prepared-text-artifacts=0`
- `new-material-ocr-runtime-setup-status=blocked_ocr_quality_insufficient`
- `probe-pages=4`
- `probe-dpi-values=300`
- `tesseract-available=1`
- `chi-sim-available=1`
- `prepared-text-artifacts=0`
- `new-material-ocr-quality-remediation-status=blocked_requires_human_correction`
- `probe-dpi-values=400`
- `vertical-tessdata-available=1`
- `assistive-ocr-route=1`
- `human-correction-required=1`
- `prepared-text-artifacts=0`
- `new-material-human-corrected-transcription-prep-status=blocked_ready_for_human_correction`
- `correction-packet-ready=1`
- `selected-page-ranges=2`
- `uncorrected-ocr-committed=0`
- `human-corrected-text-available=0`
- `prepared-text-artifacts=0`
- `new-material-human-corrected-transcription-execution-status=pilot_prepared_text_created`
- `prepared-text-artifacts=1`
- `corrected-excerpts=4`
- `corrected-characters=35`
- `page-locators=4`
- `learning-entry-ready=1`
- `uncorrected-ocr-committed=0`
- `long-form-transcription-committed=0`
- `next-material-entry=017-new-material-corrected-pilot-learning-entry-evaluation`

017 New Material Corrected Pilot Learning Entry Evaluation:

- `new-material-corrected-pilot-learning-entry-evaluation-status=ready_for_learning_note_prep`
- `learning-entry-evaluation-items=1`
- `learning-note-allowed=1`
- `candidate-intake-allowed=0`
- `duplicate-overlap-review-required=1`
- `risk-boundary-review-required=1`
- `candidate-extract-delta=0`
- `formal-evidence-delta=0`
- `downstream-mutation-authorized=false`
- `next-material-entry=017-new-material-corrected-pilot-learning-note-prep`
- `new_material_corrected_pilot_learning_entry_xiahai_suanmingji_pdf`
- Previous completed marker:
  `next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`
- Previous completed marker:
  `next-new-material-start=017-new-material-corrected-pilot-learning-note-prep`

017 New Material Corrected Pilot Learning Note Prep:

- `new-material-corrected-pilot-learning-note-prep-status=ready_for_learning_note_draft`
- `learning-note-prep-items=1`
- `proposed-learning-notes=1`
- `proposed-learning-points=1`
- `learning-note-draft-allowed=1`
- `candidate-intake-allowed=0`
- `overlap-review-required=1`
- `risk-boundary-review-required=1`
- `candidate-extract-delta=0`
- `formal-evidence-delta=0`
- `downstream-mutation-authorized=false`
- `next-material-entry=017-new-material-corrected-pilot-learning-note-draft`
- `new_material_corrected_pilot_learning_note_prep_xiahai_suanmingji_pdf`
- `note_xiahai_suanmingji_corrected_pilot_001`
- `next-new-material-start=017-new-material-corrected-pilot-learning-note-draft`

The next long goal should create the bounded 017 learning-note draft from the
prep packet, keep it concise, and still block candidate intake until the draft
is reviewed.

Run focused learning reference curation tests:

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py
```

Run boundary regression tests after changing learning references or candidate decisions:

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py tests/unit/test_extraction_queue_intake.py tests/unit/test_source_intake.py tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py
```

Run all tests:

```powershell
uv run --with pytest python -m pytest
```

## Manual Review Checklist

- Every learning reference note traces to a valid 016 extraction task.
- Every learning point has source trace, locator requirement or locator, rule family, risk tier, and limitations.
- Candidate-intake decisions check existing 013 overlaps before creating candidates.
- Prerequisite action notes preserve registration, preparation, locator-review, risk-review, deferred, and blocked backlog records without creating candidates.
- Sensitive/high-risk wording includes uncertainty and limitation boundaries.
- No learning reference metadata counts as formal report evidence.

## Done Criteria

- Maintainers can identify first-batch learning notes and candidate decisions within 5 minutes.
- Learning reference metadata validates deterministically without network access.
- No external raw source files or preparation folders are mutated.
- No learning reference note, learning point, candidate decision, or prerequisite action note is counted as formal evidence.
- Full test suite passes.
