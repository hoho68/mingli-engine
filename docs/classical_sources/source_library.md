# Source Library Progress

This document tracks source-library planning for the 014 workflow.

Root PDF files and the root `Markdown/` directory are external preparation
materials. Do not move, delete, convert, or commit those materials unless the
user explicitly asks for that action.

Related maintainer references:

- [README.md](README.md): overall classical source review workflow.
- [intake.md](intake.md): 013 candidate intake and promotion boundary.
- [materials_audit.md](materials_audit.md): 015 existing-material inventory,
  registration gaps, readiness findings, and next-action queue.
- [extraction_queue_intake.md](extraction_queue_intake.md): 016 handoff package
  that turns eligible 015 queue items into extraction tasks while preserving
  prerequisite backlog records.
- [learning_reference_curation.md](learning_reference_curation.md): 017 study
  notes, learning points, candidate-intake decisions, and prerequisite action
  notes derived from the current 016 package.
- [coverage.md](coverage.md): formal 012 evidence coverage snapshot.

## Current Boundary

- Source-library entries are planning metadata, not report evidence.
- Priority assessments explain why a source should be processed now, later, or
  not at all.
- Curation batch plans describe extraction/review work before candidate
  outcomes exist.
- Formal reports may use only reviewed and promoted formal evidence.

## Trust Boundaries

- Raw source files: root PDFs and root `Markdown/` stay external preparation
  materials. The source-library workflow may reference labels, but it must not
  move, delete, convert, rewrite, or commit those files unless explicitly
  requested.
- Source-library records: entries, priority assessments, and curation batch
  plans are planning metadata. They may identify materials, readiness,
  priority, risk, expected outputs, and next actions, but they are never
  report-usable evidence.
- Materials-audit records: 015 uses the current local materials to identify
  exact matches, missing registrations, preparation backlog, and risk-review
  backlog. Those findings may update future planning, but they do not mutate
  source-library records automatically.
- Extraction queue intake records: 016 packages may reference source-library
  entries and 013 source material ids for traceability, but they remain
  planning metadata outside candidate extracts and formal report evidence.
- Learning reference records: 017 notes, points, decisions, and prerequisite
  actions may reference source-library entries through 016/015 trace links. A
  maintainer-selected 017 create-candidate decision can create a normal 013
  pending-review candidate, but it still remains outside formal report evidence
  until ordinary 013 review and promotion rules pass.
- Candidate extracts: 013 candidates are review queue items. Pending,
  returned, rejected, blocked, and duplicate candidates stay outside formal
  evidence and reports.
- Approved candidates and promotion batches: approval creates review value, but
  it is still not formal report evidence until a reviewed or approved promotion
  target also exists in the 012 formal evidence corpus.
- Formal report evidence: reports may consume only approved formal evidence
  units and source conflicts from `data/classical_sources/`, through the
  existing report evidence loaders.

`validate_source_library_quality()` now checks source-library metadata for
report-evidence boundary leaks, absolute outcome language, prohibited
high-risk wording, and long copied passages. These checks protect the planning
layer; they do not make source-library records part of report evidence.

Quick validation command:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_library import build_source_library_progress_report, validate_source_library_quality; print(build_source_library_progress_report()); print(validate_source_library_quality())"
```

## Current Registered Snapshot

Computed with `build_source_library_progress_report()` after selected Bazi
general variant registration prep:

- Registered source entries: 27.
- Readiness: `ready_for_extraction=11`, `blocked=1`,
  `needs_preparation=2`, `review_completed=13`.
- Priority: `high=19`, `medium=6`, `deferred=1`, `low=1`.
- Risk tiers: `sensitive=8`, `ordinary=16`, `high_risk=3`.
- High-risk entries:
  `entry_blind_life_manual_pdf`,
  `entry_immortal_fortune_jianghu_secret_pdf`, and
  `entry_life_death_book_100_pages_pdf`.
- Rule-family coverage:
  `pattern_strength=14`, `blind_image_method=6`,
  `high_risk_signal=7`, `branch_interaction=10`,
  `ten_god_relation=9`, `remedy_boundary=2`,
  `useful_god_candidate=9`, `luck_cycle=6`, and
  `five_element_balance=1`.
- Next source candidates:
  `entry_northeast_blind_peak_pdf`,
  `entry_mingli_true_formula_teacher_pdf`,
  `entry_life_death_book_100_pages_pdf`, and
  `entry_markdown_source_batch_002_core`,
  `entry_markdown_source_batch_001`.

## Priority Assessments

US2 adds one priority assessment per registered source. High-priority entries
must have explicit rationale, target gaps or rule families, source quality,
effort, and risk tier before they can guide extraction planning.

- High priority: `entry_northeast_blind_peak_pdf`,
  `entry_blind_life_manual_pdf`, `entry_mingli_true_formula_teacher_pdf`, and
  `entry_life_death_book_100_pages_pdf`.
- Medium priority: `entry_duan_plain_mingxue_outline_pdf`,
  `entry_mingxue_golden_voice_pdf`, and
  `entry_fortune_reading_hongfu_qitian_pdf`.
- Low/deferred: `entry_immortal_fortune_jianghu_secret_pdf` and
  `entry_blind_school_secret_pdf`.

## Planned Curation Batches

- `batch_plan_high_risk_boundaries_001`: planned high-risk review for
  life-death, aphoristic, and remedy-boundary materials. This batch is planning
  metadata only and does not create formal evidence.
- `batch_plan_blind_image_method_001`: planned sensitive review for blind
  image-method and branch-interaction candidate extraction. This batch is also
  planning metadata only.

## Source Value Snapshot

Computed with `build_source_library_progress_report()`,
`build_source_value_summary()`, and `build_batch_value_summary()` after selected
variant registration prep:

- Value status counts:
  `value_produced=17`, `blocked=1`, and `not_started=1`.
- `entry_life_death_book_100_pages_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `conflict_count=1`, `gap_count=0`,
  `promoted_evidence_count=1`, `value_status=value_produced`.
- `entry_blind_life_manual_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `conflict_count=1`, `gap_count=1`,
  `promoted_evidence_count=1`, `value_status=value_produced`.
- `entry_northeast_blind_peak_pdf`: `candidate_count=2`,
  `approved_candidate_count=1`, `rejected_or_blocked_count=1`,
  `promoted_evidence_count=1`, `value_status=value_produced`.
- `entry_mingli_true_formula_teacher_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `promoted_evidence_count=1`,
  `value_status=value_produced`.
- `entry_duan_plain_mingxue_outline_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `promoted_evidence_count=1`,
  `value_status=value_produced`.
- `entry_mingxue_golden_voice_pdf`: `candidate_count=2`,
  `approved_candidate_count=1`, `rejected_or_blocked_count=1`,
  `promoted_evidence_count=1`, `value_status=value_produced`.
- `entry_fortune_reading_hongfu_qitian_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `promoted_evidence_count=1`,
  `value_status=value_produced`.
- `entry_blind_school_secret_pdf`: `candidate_count=1`,
  `rejected_or_blocked_count=1`, `value_status=blocked`.
- `entry_immortal_fortune_jianghu_secret_pdf`: `candidate_count=0`,
  `value_status=not_started`.
- `entry_markdown_source_batch_001`: `candidate_count=4`,
  `approved_candidate_count=4`, `promoted_evidence_count=4`,
  `value_status=value_produced`.
- `entry_markdown_source_batch_002_core`: `candidate_count=4`,
  `approved_candidate_count=4`, `promoted_evidence_count=4`,
  `value_status=value_produced`.
- `entry_markdown_source_batch_004`: `candidate_count=4`,
  `approved_candidate_count=4`, `promoted_evidence_count=4`,
  `value_status=value_produced`.
- `entry_markdown_source_batch_005`: `candidate_count=3`,
  `approved_candidate_count=3`, `promoted_evidence_count=3`,
  `value_status=value_produced`.
- `entry_knowledge_skeleton`: `candidate_count=11`,
  `approved_candidate_count=11`, `promoted_evidence_count=0`,
  `value_status=value_produced`.
- `entry_bazi_general_ditiansui_selected_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `promoted_evidence_count=2`,
  `value_status=value_produced`.
- `entry_bazi_general_qiongtong_selected_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `promoted_evidence_count=2`,
  `value_status=value_produced`.
- `entry_bazi_general_true_spirit_positioning_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `promoted_evidence_count=1`,
  `value_status=value_produced`.
- `entry_bazi_general_mingli_wangdoujing_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `promoted_evidence_count=1`,
  `value_status=value_produced`.
- `entry_bazi_general_xinpai_essence_part2_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `promoted_evidence_count=1`,
  `value_status=value_produced`.
- `entry_bazi_general_xingming_shuozheng_vol1_pdf`: `candidate_count=1`,
  `approved_candidate_count=1`, `promoted_evidence_count=1`,
  `value_status=value_produced`.
- `batch_plan_high_risk_boundaries_001`: `candidate_count=2`,
  `approved_candidate_count=1`, `conflict_count=1`, `gap_count=1`,
  `promoted_evidence_count=1`, `value_status=value_produced`.
- `batch_plan_blind_image_method_001`: `candidate_count=3`,
  `approved_candidate_count=1`, `rejected_or_blocked_count=1`,
  `gap_count=1`, `promoted_evidence_count=1`,
  `value_status=value_produced`.

`promoted_evidence_count` only counts reviewed/approved 013 promotion targets
that also exist as formal 012 evidence units. Approved but unpromoted
candidates, registered source entries, priority assessments, and planned
curation batches remain outside formal report evidence.

## Next-Source Selection Rules

`list_next_source_candidates()` selects only entries with
`readiness_status=ready_for_extraction` and `next_action=extract_candidates`.
It ranks by priority while preserving registered order within the same priority
level, so the next queue remains reviewable and stable.

## Registered Entries

- `entry_northeast_blind_peak_pdf`: ready for extraction; blind-school image
  and branch interaction material.
- `entry_duan_plain_mingxue_outline_pdf`: ready for extraction; ten-god and
  pattern-strength material.
- `entry_blind_school_secret_pdf`: blocked until source access and quotation
  boundaries are clarified.
- `entry_blind_life_manual_pdf`: ready for extraction; high-risk blind-school
  aphoristic material requiring conditional rewrite.
- `entry_mingli_true_formula_teacher_pdf`: ready for extraction; pattern,
  useful-god, and luck-cycle material.
- `entry_mingxue_golden_voice_pdf`: ready for extraction; five-element,
  ten-god, and terminology material.
- `entry_fortune_reading_hongfu_qitian_pdf`: ready for extraction; practice
  and remedy-boundary material.
- `entry_immortal_fortune_jianghu_secret_pdf`: needs preparation; high-risk
  Jianghu-style material requiring safety review.
- `entry_life_death_book_100_pages_pdf`: ready for extraction; high-risk
  life-death material usable only as bounded traditional signal input.
- `entry_bazi_general_ditiansui_selected_pdf`: review completed; selected
  Ditiansui canonical variant stored as weak locator-backed source metadata.
- `entry_bazi_general_qiongtong_selected_pdf`: review completed; selected
  Qiongtong Baojian canonical variant stored as weak locator-backed source
  metadata.
- `entry_bazi_general_true_spirit_positioning_pdf`: review completed; bounded
  next-cycle modern-method source stored as weak locator-backed source
  metadata.
- `entry_bazi_general_mingli_wangdoujing_pdf`: review completed; bounded
  next-cycle miscellaneous source stored as weak locator-backed source
  metadata.
- `entry_bazi_general_xinpai_essence_part2_pdf`: review completed; bounded
  next-cycle followup modern-method source stored as weak locator-backed
  source metadata.
- `entry_bazi_general_xingming_shuozheng_vol1_pdf`: review completed;
  bounded next-cycle followup miscellaneous source stored as weak
  locator-backed source metadata.

## US1 Review Notes

- All entries use `tracking_status=external_untracked`, so the workflow stores
  labels and review metadata rather than the raw source files.
- Ready entries include topic tags, rule families, source quality notes, rights
  notes, priority, risk tier, and next action.
- Blocked or deferred source outcomes must keep durable reasons so maintainers
  do not repeat unsafe or unclear work.
