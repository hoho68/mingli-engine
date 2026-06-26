# Classical Evidence Coverage

This file records maintainer-facing coverage notes for the curated classical
evidence corpus.

The authoritative runtime data lives in
`src/mingli_engine/data/classical_sources/`. Coverage numbers should be derived
from the current JSON corpus instead of maintained by hand.

## Current Status

Snapshot date: 2026-06-26

- Approved evidence units: 92
- Registered sources: 14
- Sources with explicit gaps:
  - `blind_life_manual`: 断语体和高风险口径尚未完成条件化改写，暂不支撑正式结论。
  - `immortal_fortune_jianghu_secret`: 尚未开始抽取和安全改写，恐吓式或付费化解口径未审，暂不支撑正式结论。
- Open conflicts:
  - `conflict_high_risk_scope_001`: severe/open scope mismatch between blind-school risk imagery and life-death material.
- Documented conflicts:
  - `conflict_useful_god_school_001`: moderate/documented school difference for useful-god candidate priority.

## Evidence Counts By Source

- `blind_life_manual`: 0
- `blind_school_secret`: 8
- `duan_plain_mingxue_outline`: 9
- `fortune_reading_hongfu_qitian`: 9
- `immortal_fortune_jianghu_secret`: 0
- `knowledge_skeleton`: 11
- `life_death_book_100_pages`: 11
- `markdown_source_batch_001`: 4
- `markdown_source_batch_002_core`: 4
- `markdown_source_batch_004`: 4
- `markdown_source_batch_005`: 3
- `mingli_true_formula_teacher`: 11
- `mingxue_golden_voice`: 9
- `northeast_blind_peak`: 9

## Evidence Counts By Rule Family

- `blind_image_method`: 11
- `branch_interaction`: 10
- `five_element_balance`: 4
- `high_risk_signal`: 7
- `luck_cycle`: 10
- `pattern_strength`: 13
- `remedy_boundary`: 8
- `taboo_god_candidate`: 6
- `ten_god_relation`: 12
- `useful_god_candidate`: 11

## Evidence Counts By Risk Tier

- `ordinary`: 42
- `sensitive`: 39
- `high_risk`: 11

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
