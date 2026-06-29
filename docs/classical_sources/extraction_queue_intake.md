# Extraction Queue Intake

016 extraction queue intake stores maintainer metadata for turning the 015
next-action queue into bounded manual extraction preparation.

Related maintainer references:

- [README.md](README.md): overall classical source review workflow.
- [source_library.md](source_library.md): 014 source-library entries used for
  task traceability.
- [intake.md](intake.md): 013 candidate-intake workflow that may later receive
  manually created candidates.
- [materials_audit.md](materials_audit.md): 015 audit records, readiness
  findings, alignment findings, and next-action queue.
- [learning_reference_curation.md](learning_reference_curation.md): 017
  learning notes, learning points, candidate-intake decisions, and prerequisite
  action notes derived from the current 016 package.
- [coverage.md](coverage.md): formal 012 evidence coverage snapshot used by
  reports.

## Work Package Snapshot

Work packages live in
`src/mingli_engine/data/extraction_queue_intake/extraction_work_packages.json`.
They list the 015 queue item ids considered, the selected extraction task ids,
and prerequisite backlog records kept visible for later review.

Current packages:

- `package_next_candidates_001` snapshots the current 015 next-action queue ids:
  `queue_northeast_blind_peak_extract`,
  `queue_mingli_true_formula_teacher_extract`,
  `queue_markdown_source_batch_001_register`,
  `queue_blind_life_manual_risk_review`, and
  `queue_blind_school_secret_blocked`.
- Only the two `extraction_ready` queue items are selected as extraction tasks
  in US1.
- Registration, risk-review, and blocked queue work from the package snapshot is
  preserved as prerequisite backlog records, not routine extraction tasks.
- `package_next_candidates_002` snapshots
  `queue_duan_plain_mingxue_outline_extract` and selects
  `task_duan_plain_mingxue_outline_extract_001` as the next ordinary-risk
  learning-reference extraction task.
- `package_next_candidates_003` snapshots the next multi-item 015 queue slice.
  It selects `queue_mingxue_golden_voice_extract` and
  `queue_fortune_reading_hongfu_qitian_extract` as extraction tasks while
  keeping registration, risk-review, and deferred work in prerequisite backlog
  records.
- `package_markdown_batch_registration_001` and
  `package_knowledge_skeleton_001` preserve the completed Markdown batch and
  knowledge-skeleton learning passes.
- `package_next_candidates_004` snapshots
  `queue_markdown_source_batch_005_risk_review` as completed
  prerequisite-only risk-review work. It has no selected extraction tasks.
- `package_bazi_general_source_preparation_reading_001` and
  `package_bazi_general_selected_variant_preparation_reading_001` preserve the
  completed Bazi general preparation-reading and selected-variant
  registration-prep passes.
- `package_bazi_general_gated_ordinary_source_selection_001` preserves the
  completed gated ordinary source-selection pass for Mingzao Chunqiu and
  Sizhu Yuce Yaojue.

## Extraction Task Boundary

Extraction tasks are planning metadata for future manual 013 candidate work.
They must not copy raw passages, extracted meanings, review decisions, approval
states, promotion states, or formal evidence wording.

Current US1 extraction tasks:

- `task_northeast_blind_peak_extract_001` links
  `queue_northeast_blind_peak_extract`,
  `audit_northeast_blind_peak`,
  `entry_northeast_blind_peak_pdf`, and
  `material_northeast_blind_peak_pdf`.
- `task_mingli_true_formula_teacher_extract_001` links
  `queue_mingli_true_formula_teacher_extract`,
  `audit_mingli_true_formula_teacher`,
  `entry_mingli_true_formula_teacher_pdf`, and
  `material_mingli_true_formula_teacher_pdf`.
- `task_duan_plain_mingxue_outline_extract_001` links
  `queue_duan_plain_mingxue_outline_extract`,
  `audit_duan_plain_mingxue_outline`,
  `entry_duan_plain_mingxue_outline_pdf`, and
  `material_duan_plain_mingxue_outline_pdf`.
- `task_mingxue_golden_voice_extract_001` links
  `queue_mingxue_golden_voice_extract`,
  `audit_mingxue_golden_voice`,
  `entry_mingxue_golden_voice_pdf`, and
  `material_mingxue_golden_voice_pdf`.
- `task_fortune_reading_hongfu_qitian_extract_001` links
  `queue_fortune_reading_hongfu_qitian_extract`,
  `audit_fortune_reading_hongfu_qitian`,
  `entry_fortune_reading_hongfu_qitian_pdf`, and
  `material_fortune_reading_hongfu_qitian_pdf`.
- `task_bazi_general_ditiansui_pattern_strength_001` links
  `queue_bazi_general_ditiansui_pattern_strength_extract`,
  `audit_bazi_general_ditiansui_selected_pdf`,
  `entry_bazi_general_ditiansui_selected_pdf`, and
  `material_bazi_general_ditiansui_selected_pdf`.
- `task_bazi_general_qiongtong_useful_god_001` links
  `queue_bazi_general_qiongtong_useful_god_extract`,
  `audit_bazi_general_qiongtong_selected_pdf`,
  `entry_bazi_general_qiongtong_selected_pdf`, and
  `material_bazi_general_qiongtong_selected_pdf`.
- `task_bazi_general_mingzao_chunqiu_luck_cycle_001` links
  `queue_bazi_general_mingzao_chunqiu_luck_cycle_extract`,
  `audit_bazi_general_mingzao_chunqiu_case_pdf`,
  `entry_bazi_general_mingzao_chunqiu_case_pdf`, and
  `material_bazi_general_mingzao_chunqiu_case_pdf`.
- `task_bazi_general_sizhu_yuce_yaojue_pattern_strength_001` links
  `queue_bazi_general_sizhu_yuce_yaojue_pattern_strength_extract`,
  `audit_bazi_general_sizhu_yuce_yaojue_pdf`,
  `entry_bazi_general_sizhu_yuce_yaojue_pdf`, and
  `material_bazi_general_sizhu_yuce_yaojue_pdf`.

Task loading validates package membership, 015 queue eligibility, audit-record
identity, readiness findings, source-library alignment, source-material links,
target rule families or gaps, locator requirement, rights notes, risk boundary,
and pre-extraction checks.

## Candidate Draft Slot Boundary

Candidate draft slots describe intended future candidate records without
creating 013 candidates. They must stay outside candidate counts, promotion
counts, and report evidence counts.

Current US2 draft slots:

- `slot_northeast_blind_image_001` belongs to
  `task_northeast_blind_peak_extract_001` and targets
  `blind_image_method`.
- `slot_mingli_pattern_strength_001` belongs to
  `task_mingli_true_formula_teacher_extract_001` and targets
  `pattern_strength`.
- `slot_duan_ten_god_relation_001` belongs to
  `task_duan_plain_mingxue_outline_extract_001` and targets
  `ten_god_relation`.
- `slot_mingxue_five_element_balance_001` belongs to
  `task_mingxue_golden_voice_extract_001` and targets
  `five_element_balance`.
- `slot_hongfu_remedy_boundary_001` belongs to
  `task_fortune_reading_hongfu_qitian_extract_001` and targets
  `remedy_boundary`.
- `slot_bazi_general_ditiansui_pattern_strength_001` belongs to
  `task_bazi_general_ditiansui_pattern_strength_001` and targets
  `pattern_strength`.
- `slot_bazi_general_qiongtong_useful_god_001` belongs to
  `task_bazi_general_qiongtong_useful_god_001` and targets
  `useful_god_candidate`.

Draft slots are only placeholders. They do not store source passages,
extracted meanings, review decisions, approval status, promotion status, or
formal-evidence wording. Manual extraction must still create separate 013
candidate records later, and those candidates still require normal 013 review
and promotion before anything can become formal report evidence.

Sensitive draft slots require uncertainty and limitation safety requirements.
High-risk draft slots also require a risk-review safety requirement before they
can be considered ready for manual extraction.

## Prerequisite Backlog

Queue items that are not routine-extraction ready are preserved as prerequisite
backlog records with missing prerequisites, durable reasons, recommended manual
actions, and risk boundaries.

Current US3 backlog records:

- `backlog_blind_life_manual_risk_review_001` keeps
  `queue_blind_life_manual_risk_review` out of routine extraction after
  completed boundary screening.
- `backlog_blind_school_secret_blocked_001` keeps
  `queue_blind_school_secret_blocked` blocked until source access and quotation
  boundaries are clarified.
- `backlog_markdown_batch_003_registration_001` keeps the failed-conversion
  Markdown batch visible until OCR and source-library registration can happen.
- `backlog_immortal_fortune_jianghu_secret_risk_review_001`,
  `backlog_life_death_book_100_pages_risk_review_001`, and
  `backlog_markdown_batch_005_risk_review_001` keep high-risk materials out of
  routine extraction after completed boundary screening.
- `backlog_source_processing_status_deferred_001` records workflow metadata as
  deferred from source extraction.

Registration, preparation, locator-review, and risk-review backlog records must
name missing prerequisites. Deferred and blocked records must provide durable
reasons. Risk-review, deferred, and blocked records cannot share a queue item
with an extraction task.

## Duplicate And Overlap Warnings

016 detects overlap against existing 013 candidate records without mutating
those candidates. The current package surfaces two overlap warnings for
`task_northeast_blind_peak_extract_001` because
`material_northeast_blind_peak_pdf` already has pending and rejected
blind-image candidate records:

- `candidate_northeast_blind_image_001`
- `candidate_northeast_blind_image_duplicate_001`

It also surfaces applied 017 candidate-application overlaps for the current
ready tasks:

- `candidate_mingli_pattern_strength_017_001` on
  `task_mingli_true_formula_teacher_extract_001`.
- `candidate_duan_ten_god_relation_017_001` on
  `task_duan_plain_mingxue_outline_extract_001`.
- `candidate_mingxue_golden_voice_scope_001` and
  `candidate_mingxue_five_element_balance_017_001` on
  `task_mingxue_golden_voice_extract_001`.
- `candidate_hongfu_remedy_boundary_017_001` on
  `task_fortune_reading_hongfu_qitian_extract_001`.

These warnings are planning signals for the reviewer. They are not review
decisions, approval states, promotion states, or formal report evidence.

## Raw-File And Evidence Boundary

016 does not read, parse, move, convert, or mutate root PDFs, root Markdown, raw
source folders, or preparation folders. It does not create candidate extracts,
approve evidence, promote evidence, or change formal report evidence counts.

## Initial Setup Status

US1 seeded the initial package and two extraction tasks. The completed
incremental packages add Duan Plain Mingxue Outline, Mingxue Golden Voice,
Fortune Reading Hongfu Qitian, three Markdown batch tasks, six knowledge
skeleton tasks, three Bazi general preparation-reading tasks, two selected
Bazi general variant tasks, two next-cycle cluster-source tasks, and two next-cycle followup tasks. All 23 extraction tasks are now completed and
`next_manual_action_ids=0`. US2 keeps seventeen draft slots as historical
planning metadata. US3 and the current queue continuation track seven
prerequisite backlog records, including four completed risk-review records,
overlap warning visibility, and package progress counts while keeping all 016
records outside candidate and formal evidence counts.

017 learning reference curation consumed the selected 016 extraction tasks as
study-note inputs and mirrors the non-ready 016 backlog records as prerequisite
action notes. The 016 package remains planning metadata; 017 notes, learning
points, candidate-intake decisions, and action notes do not mutate raw
materials. The authorized downstream passes that now exist in 013/012 remain
tracked by their normal source-intake and formal-evidence records.

The latest completed package,
`package_bazi_general_next_cycle_followup_001`, covers
`queue_bazi_general_xinpai_essence_pattern_strength_extract` and
`queue_bazi_general_xingming_shuozheng_branch_interaction_extract`. Both tasks are
ordinary-risk, weak-locator metadata tasks; raw PDFs remain external and
unchanged.

Quick validation command:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.extraction_queue_intake import build_package_progress_summary, validate_extraction_package_quality; print(build_package_progress_summary()); print(validate_extraction_package_quality())"
```
