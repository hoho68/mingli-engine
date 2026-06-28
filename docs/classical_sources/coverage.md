# Classical Evidence Coverage

This file records maintainer-facing coverage notes for the curated classical
evidence corpus.

The authoritative runtime data lives in
`src/mingli_engine/data/classical_sources/`. Coverage numbers should be derived
from the current JSON corpus instead of maintained by hand.

## Current Status

Snapshot date: 2026-06-28

- Approved evidence units: 105
- Registered sources: 23
- Sources with explicit gaps:
  - `blind_life_manual`: 仅条件化高风险边界已提升；单条断语仍需页码或标题级定位复核后才能支撑正式结论。
  - `immortal_fortune_jianghu_secret`: 尚未开始抽取和安全改写，恐吓式或付费化解口径未审，暂不支撑正式结论。
- Open conflicts:
  - `conflict_high_risk_scope_001`: severe/open scope mismatch between blind-school risk imagery and life-death material.
- Documented conflicts:
  - `conflict_useful_god_school_001`: moderate/documented school difference for useful-god candidate priority.

## Evidence Counts By Source

- `blind_life_manual`: 1
- `blind_school_secret`: 8
- `duan_plain_mingxue_outline`: 9
- `fortune_reading_hongfu_qitian`: 9
- `immortal_fortune_jianghu_secret`: 0
- `knowledge_skeleton`: 11
- `life_death_book_100_pages`: 11
- `markdown_source_batch_001`: 4
- `markdown_source_batch_002_core`: 7
- `markdown_source_batch_004`: 4
- `markdown_source_batch_005`: 3
- `mingli_true_formula_teacher`: 11
- `mingxue_golden_voice`: 9
- `northeast_blind_peak`: 9
- `source_bazi_general_beichen_intro_pdf`: 1
- `source_bazi_general_ditiansui_selected_pdf`: 1
- `source_bazi_general_lecture_textbook_pdf`: 1
- `source_bazi_general_mingli_wangdoujing_pdf`: 1
- `source_bazi_general_qiongtong_selected_pdf`: 1
- `source_bazi_general_true_spirit_positioning_pdf`: 1
- `source_bazi_general_xinpai_essence_part2_pdf`: 1
- `source_bazi_general_xingming_shuozheng_vol1_pdf`: 1
- `source_bazi_general_ziping_orthodox_pair_pdf`: 1

## Evidence Counts By Rule Family

- `blind_image_method`: 11
- `branch_interaction`: 14
- `five_element_balance`: 4
- `high_risk_signal`: 8
- `luck_cycle`: 10
- `pattern_strength`: 17
- `remedy_boundary`: 8
- `taboo_god_candidate`: 6
- `ten_god_relation`: 12
- `useful_god_candidate`: 15

## Evidence Counts By Risk Tier

- `ordinary`: 54
- `sensitive`: 39
- `high_risk`: 12

## Quality Check Result

- High-risk evidence missing limitations: none.
- Long summary violations: none.
- Unknown or non-report-usable evidence sources: none in approved evidence.

## Guardrails

- Keep root PDF files and root `Markdown/` as preparation material only.
- Do not copy long source passages into evidence summaries.
- Do not use blocked, unreviewed, failed, or unknown sources for report
  conclusions.
- Keep high-risk evidence conditional and non-exact.
