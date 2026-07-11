# Classical Evidence Coverage

This file records maintainer-facing coverage notes for the curated classical
evidence corpus.

The authoritative runtime data lives in
`src/mingli_engine/data/classical_sources/`. Coverage numbers should be derived
from the current JSON corpus instead of maintained by hand.

## Current Status

Snapshot date: 2026-07-11

- Approved evidence units: 111
- Registered sources: 29
- Sources with approved evidence: 28
- Formal interpretation rule families enabled: 10 / 10
- Sources with explicit gaps:
  - `blind_life_manual`: high-risk boundary evidence is promoted; page-level single-claim support still requires later review.
  - `immortal_fortune_jianghu_secret`: extraction and safety rewrite have not started, so it does not support formal conclusions.
- Open conflicts:
  - `conflict_high_risk_scope_001`: severe/open scope mismatch between blind-school risk imagery and life-death material.
- Documented conflicts:
  - `conflict_useful_god_school_001`: moderate/documented school difference for useful-god candidate priority.

## Knowledge Activation Packet

- `knowledge-activation-status=enabled_with_guardrails`
- `classical-sources=29`
- `report-usable-sources=28`
- `approved-evidence-units=111`
- `formal-interpretation-rule-families=10`
- `missing-rule-families=0`
- `formal-unavailable-conclusions=0`
- `open-conflicts=1`
- `quality-failures=0`
- `next-action=enable_for_reports_with_high_risk_guardrails`

Enabled rule families:

- `pattern_strength`
- `five_element_balance`
- `useful_god_candidate`
- `taboo_god_candidate`
- `ten_god_relation`
- `branch_interaction`
- `blind_image_method`
- `luck_cycle`
- `remedy_boundary`
- `high_risk_signal`

Activation rule: the current extracted and promoted corpus is usable by
`formal_interpretation` for all supported rule families. It is enabled with
guardrails because high-risk evidence remains conditional and one severe
high-risk scope conflict is intentionally visible to report traces.

Machine-readable check: run `mingli-engine knowledge-activation-summary` to
return the same activation packet as JSON before enabling report workflows.

## Report Acceptance Packet

- `baseline-id=report_acceptance_v1`
- `acceptance-status=ready_with_guardrails`
- `acceptance-cases=4`
- `passed-acceptance-cases=4`
- `approved-evidence-units=111`
- `traced-evidence-units=111`
- `formal-rule-families=10`
- `personalized-chart-signal-segments=10`
- `missing-rule-families=0`
- `open-conflicts=1`
- `next-action=release_reports_with_guardrails`

The four cases cover an ordinary production report, the current conflict
guardrail, exact-lifespan rejection, and unavailable-evidence degradation.
The ordinary case additionally verifies one sanitized chart-signal segment per
rule family. All cases use in-memory fixtures and do not write source-library,
013, or 012 data.

Machine-readable check: run `mingli-engine report-acceptance-summary`. See
[report_acceptance.md](report_acceptance.md) for scenario and boundary details.

## Evidence Counts By Source

- `blind_life_manual`: 1
- `blind_school_secret`: 8
- `duan_plain_mingxue_outline`: 9
- `fortune_reading_hongfu_qitian`: 9
- `knowledge_skeleton`: 11
- `life_death_book_100_pages`: 11
- `markdown_source_batch_001`: 4
- `markdown_source_batch_002_core`: 7
- `markdown_source_batch_004`: 4
- `markdown_source_batch_005`: 3
- `mingli_true_formula_teacher`: 11
- `mingxue_golden_voice`: 9
- `northeast_blind_peak`: 9
- `source_bazi_general_bazi_baijue_case_pdf`: 1
- `source_bazi_general_beichen_intro_pdf`: 1
- `source_bazi_general_ditiansui_selected_pdf`: 1
- `source_bazi_general_lecture_textbook_pdf`: 1
- `source_bazi_general_mingli_mijue_pdf`: 1
- `source_bazi_general_mingli_wangdoujing_pdf`: 1
- `source_bazi_general_mingzao_chunqiu_case_pdf`: 1
- `source_bazi_general_qiongtong_selected_pdf`: 1
- `source_bazi_general_sizhu_yuce_yaojue_pdf`: 1
- `source_bazi_general_true_spirit_positioning_pdf`: 1
- `source_bazi_general_xingming_shuozheng_vol1_pdf`: 1
- `source_bazi_general_xinpai_essence_part2_pdf`: 1
- `source_bazi_general_ziping_orthodox_pair_pdf`: 1

## Evidence Counts By Rule Family

- `blind_image_method`: 11
- `branch_interaction`: 16
- `five_element_balance`: 4
- `high_risk_signal`: 8
- `luck_cycle`: 12
- `pattern_strength`: 18
- `remedy_boundary`: 8
- `taboo_god_candidate`: 6
- `ten_god_relation`: 13
- `useful_god_candidate`: 15

## Evidence Counts By Risk Tier

- `high_risk`: 12
- `ordinary`: 60
- `sensitive`: 39

## Quality Check Result

- High-risk evidence missing limitations: none.
- Long summary violations: none.
- Unknown or non-report-usable evidence sources: none in approved evidence.

## Guardrails

- Keep root PDF files and root `Markdown/` as preparation material only.
- Do not copy long source passages into evidence summaries.
- Do not use blocked, unreviewed, failed, or unknown sources for report conclusions.
- Keep high-risk evidence conditional and non-exact.
