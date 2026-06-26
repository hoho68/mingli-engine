# Evidence Source Reference Quality Audit Report

Generated: automatic analysis
Audit scope: 92 evidence units

## Precision Summary

| Precision Level | Count | Share |
|-----------------|-------|-------|
| REVIEW_NOTE_SOURCE_WINDOW | 57 | 62.0% |
| MARKDOWN_SOURCE_LINE | 15 | 16.3% |
| REVIEW_NOTE_KS_PATH | 11 | 12.0% |
| PAGE_EXACT | 9 | 9.8% |

## Source-Window Locator Detail

| Locator Type | Count |
|--------------|-------|
| PAGE_LOCATOR | 39 |
| CHAPTER_LOCATOR | 16 |
| MARKDOWN_LINE_LOCATOR | 2 |

## Chapter Locator Blocker Detail

| Blocker | Count |
|---------|-------|
| blocked:pdf-directory-text-only | 3 |
| blocked:pdf-text-cid-or-empty | 13 |

## OCR/Page Review Pass

| Source | Outcome | Count |
|--------|---------|-------|
| blind_school_secret_pdf | prior-page-reviewed | 1 |
| duan_plain_mingxue_outline_pdf | page-reviewed | 4 |
| duan_plain_mingxue_outline_pdf | rendered-review-blocked | 5 |
| mingxue_golden_voice_pdf | page-reviewed | 7 |
| mingxue_golden_voice_pdf | rendered-review-blocked | 2 |
| fortune_reading_hongfu_qitian_pdf | page-reviewed | 3 |
| fortune_reading_hongfu_qitian_pdf | rendered-review-blocked | 6 |
| northeast_blind_peak_pdf | page-reviewed | 6 |
| northeast_blind_peak_pdf | rendered-review-blocked | 3 |

## Improvement Notes

Converted 51 legacy topic-only review-note references in the prior pass and preserved them as source-window locators.
Converted 6 legacy file-section review-note references into verifiable source-window locators in the prior pass.
Upgraded 20 additional source-window locators from chapter-level to page-level after local PDF rendering and visual review.
- All 57 review-note-backed evidence units now point to `review-note:<extract>.md#source-window-<slug>`.
- Each source-window section has a `Source locator` field using `page:`, `chapter:`, or `Markdown/...#L...`.
- Remaining chapter-level locators carry a `Locator note` explaining why page or Markdown-line precision is currently blocked.
- Page-level locator coverage is used where PDF text extraction, table-of-contents mapping, or rendered page review is reliable.
- Chapter-level locators are retained only where visual review did not produce a reliable topic-page match.
- Markdown line locators are used for the Life Death Book material that already has a tracked Markdown extract.

Prior improvements are preserved:
- 15 promoted Markdown learning material locators point to cleaned Markdown files and line numbers.
- 11 knowledge-skeleton locators remain explicit curated review-note paths.

## Priority Groups

### Current Goal Progress (92 items)
- REVIEW_NOTE_SOURCE_WINDOW: 57 items now point to source-window sections with source locators.
- PAGE_LOCATOR: 39 source-window items now have page-level locators.
- CHAPTER_LOCATOR: 16 source-window items remain chapter-level with explicit blocker notes.
- MARKDOWN_SOURCE_LINE: 15 items point to cleaned Markdown files and line numbers.
- REVIEW_NOTE_KS_PATH: 11 items point to knowledge-skeleton files.
- PAGE_EXACT: 9 items already have exact page references.

### Optional Future Precision Work
- For the remaining CID-backed source windows, do a targeted OCR/manual transcription pass rather than relying on CID text extraction.
- For the remaining Northeast source windows, use manual topic review to avoid over-mapping case-heavy pages to broad rule families.
- Promote this audit builder into a checked utility command if future curation passes need repeatable report generation.

## Detailed Inventory

| Evidence ID | Theme | Rule Family | School | Batch | Current source_ref | Source locator | Precision | Status |
|-------------|-------|-------------|--------|-------|--------------------|----------------|-----------|--------|
| duan_ten_god_relation_001 | 十神关系 | ten_god_relation | 段氏 | batch_012_seed_001 | `review-note:duan_plain_mingxue_outline.md#source-window-ten-god-relationships` | `page:66; source=duan_plain_mingxue_outline_pdf; heading:ten-god-section-start` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| mingxue_five_element_balance_001 | 五行强弱 | five_element_balance | 通论 | batch_012_seed_001 | `review-note:mingxue_golden_voice.md#source-window-five-element-balance` | `page:104; source=mingxue_golden_voice_pdf; heading:five-element-command` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_pattern_strength_001 | 格局旺衰 | pattern_strength | 师传口径 | batch_012_seed_001 | `review-note:mingli_true_formula_teacher.md#source-window-pattern-strength` | `page:121; source=mingli_true_formula_teacher_pdf; heading:wangshuai-pattern-context` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| blind_branch_interaction_001 | 刑冲合害 | branch_interaction | 盲派 | batch_012_seed_001 | `review-note:blind_school_secret.md#source-window-branch-interactions` | `page:98; source=blind_school_secret_pdf; heading:branch-punishment-overview` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| northeast_blind_image_001 | 盲派象法 | blind_image_method | 东北盲派 | batch_012_seed_001 | `review-note:northeast_blind_peak.md#source-window-image-method` | `page:2; source=northeast_blind_peak_pdf; heading:eight-method-rules` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_luck_cycle_trigger_001 | 大运流年 | luck_cycle | 师传口径 | batch_012_seed_001 | `review-note:mingli_true_formula_teacher.md#source-window-luck-cycle-trigger` | `page:141; source=mingli_true_formula_teacher_pdf; heading:xiaoxian-luck-cycle` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| fortune_remedy_boundary_001 | 趋避与调整 | remedy_boundary | 通俗命理 | batch_012_seed_001 | `review-note:fortune_reading_hongfu_qitian.md#source-window-remedy-boundary` | `chapter:source=fortune_reading_hongfu_qitian_pdf; section=remedy-boundary` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| life_death_high_risk_signal_001 | 生死寿夭材料 | high_risk_signal | 传统高风险材料 | batch_012_seed_001 | `review-note:life_death_book_100_pages.md#source-window-life-death-risk-signal` | `Markdown/2800.《命理生死之书》100页.md#L15` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| northeast_blind_image_002 | 盲派象法 | blind_image_method | 东北盲派 | batch_012_taxonomy_001 | `review-note:northeast_blind_peak.md#source-window-image-method-position` | `page:16; source=northeast_blind_peak_pdf; heading:position-child-star` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| northeast_blind_image_003 | 干支组合取象 | blind_image_method | 东北盲派 | batch_012_taxonomy_001 | `review-note:northeast_blind_peak.md#source-window-image-method-combination` | `page:34; source=northeast_blind_peak_pdf; heading:marriage-five-rules-combination` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| northeast_blind_image_004 | 象法回归结构 | blind_image_method | 东北盲派 | batch_012_taxonomy_001 | `review-note:northeast_blind_peak.md#source-window-image-method-structure` | `page:34; source=northeast_blind_peak_pdf; heading:marriage-five-rules-structure` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| northeast_blind_image_005 | 象法触发条件 | blind_image_method | 东北盲派 | batch_012_taxonomy_001 | `review-note:northeast_blind_peak.md#source-window-image-method-trigger` | `page:13; source=northeast_blind_peak_pdf; heading:timing-match-condition` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| northeast_blind_image_006 | 象法边界 | blind_image_method | 东北盲派 | batch_012_taxonomy_001 | `review-note:northeast_blind_peak.md#source-window-image-method-risk-boundary` | `chapter:source=northeast_blind_peak_pdf; section=image-method-risk-boundary` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| northeast_branch_interaction_001 | 支象互动 | branch_interaction | 东北盲派 | batch_012_taxonomy_001 | `review-note:northeast_blind_peak.md#source-window-branch-image-interaction` | `chapter:source=northeast_blind_peak_pdf; section=branch-image-interaction` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| northeast_high_risk_signal_001 | 高风险取象边界 | high_risk_signal | 东北盲派 | batch_012_taxonomy_001 | `review-note:northeast_blind_peak.md#source-window-high-risk-image-boundary` | `chapter:source=northeast_blind_peak_pdf; section=high-risk-image-boundary` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| duan_ten_god_relation_002 | 十神柱位 | ten_god_relation | 段氏 | batch_012_taxonomy_001 | `review-note:duan_plain_mingxue_outline.md#source-window-ten-god-position` | `chapter:source=duan_plain_mingxue_outline_pdf; section=ten-god-position` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| duan_ten_god_relation_003 | 十神结构 | ten_god_relation | 段氏 | batch_012_taxonomy_001 | `review-note:duan_plain_mingxue_outline.md#source-window-ten-god-structure` | `page:84; source=duan_plain_mingxue_outline_pdf; heading:guan-sha-mixed-structure` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| duan_pattern_strength_001 | 格局语境 | pattern_strength | 段氏 | batch_012_taxonomy_001 | `review-note:duan_plain_mingxue_outline.md#source-window-pattern-context` | `page:92; source=duan_plain_mingxue_outline_pdf; heading:pattern-context` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| duan_useful_god_candidate_001 | 用神候选 | useful_god_candidate | 段氏 | batch_012_taxonomy_001 | `review-note:duan_plain_mingxue_outline.md#source-window-useful-god-balance` | `chapter:source=duan_plain_mingxue_outline_pdf; section=useful-god-balance` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| duan_useful_god_candidate_002 | 用神条件 | useful_god_candidate | 段氏 | batch_012_taxonomy_001 | `review-note:duan_plain_mingxue_outline.md#source-window-useful-god-condition` | `chapter:source=duan_plain_mingxue_outline_pdf; section=useful-god-condition` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| duan_taboo_god_candidate_001 | 忌神候选 | taboo_god_candidate | 段氏 | batch_012_taxonomy_001 | `review-note:duan_plain_mingxue_outline.md#source-window-taboo-god-excess` | `chapter:source=duan_plain_mingxue_outline_pdf; section=taboo-god-excess` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| duan_taboo_god_candidate_002 | 忌神语境 | taboo_god_candidate | 段氏 | batch_012_taxonomy_001 | `review-note:duan_plain_mingxue_outline.md#source-window-taboo-god-context` | `chapter:source=duan_plain_mingxue_outline_pdf; section=taboo-god-context` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| blind_branch_interaction_002 | 刑冲合害位置 | branch_interaction | 盲派 | batch_012_taxonomy_001 | `review-note:blind_school_secret.md#source-window-branch-interaction-position` | `page:98; source=blind_school_secret_pdf; heading:branch-interaction-position` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| blind_branch_interaction_003 | 刑冲合害引动 | branch_interaction | 盲派 | batch_012_taxonomy_001 | `review-note:blind_school_secret.md#source-window-branch-interaction-trigger` | `page:50; source=blind_school_secret_pdf; heading:branch-interaction-trigger` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| blind_branch_interaction_004 | 刑冲合害强弱 | branch_interaction | 盲派 | batch_012_taxonomy_001 | `review-note:blind_school_secret.md#source-window-branch-interaction-strength` | `page:112; source=blind_school_secret_pdf; heading:branch-interaction-strength` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| blind_school_image_001 | 盲派象法 | blind_image_method | 盲派 | batch_012_taxonomy_001 | `review-note:blind_school_secret.md#source-window-blind-school-image` | `page:226; source=blind_school_secret_pdf; heading:blind-school-image` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| blind_school_image_002 | 象法边界 | blind_image_method | 盲派 | batch_012_taxonomy_001 | `review-note:blind_school_secret.md#source-window-blind-school-image-boundary` | `page:431; source=blind_school_secret_pdf; heading:blind-school-image-boundary` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| blind_high_risk_signal_001 | 高风险边界 | high_risk_signal | 盲派 | batch_012_taxonomy_001 | `review-note:blind_school_secret.md#source-window-blind-high-risk-boundary` | `page:70; source=blind_school_secret_pdf; heading:blind-high-risk-boundary` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| blind_remedy_boundary_001 | 趋避边界 | remedy_boundary | 盲派 | batch_012_taxonomy_001 | `review-note:blind_school_secret.md#source-window-blind-remedy-boundary` | `page:446; source=blind_school_secret_pdf; heading:professional-consultation-remedy-boundary` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_pattern_strength_002 | 根气旺衰 | pattern_strength | 师传口径 | batch_012_taxonomy_001 | `review-note:mingli_true_formula_teacher.md#source-window-pattern-root-qi` | `page:56; source=mingli_true_formula_teacher_pdf; heading:wangshuai-root-qi` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_pattern_strength_003 | 格局降级 | pattern_strength | 师传口径 | batch_012_taxonomy_001 | `review-note:mingli_true_formula_teacher.md#source-window-pattern-candidate-downgrade` | `page:125; source=mingli_true_formula_teacher_pdf; heading:geju-candidate` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_luck_cycle_trigger_002 | 岁运条件 | luck_cycle | 师传口径 | batch_012_taxonomy_001 | `review-note:mingli_true_formula_teacher.md#source-window-luck-cycle-condition` | `page:141; source=mingli_true_formula_teacher_pdf; heading:luck-cycle-condition` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_useful_god_candidate_001 | 用神候选 | useful_god_candidate | 师传口径 | batch_012_taxonomy_001 | `review-note:mingli_true_formula_teacher.md#source-window-useful-god-root` | `page:143; source=mingli_true_formula_teacher_pdf; heading:yongshen-definition` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_useful_god_candidate_002 | 调候候选 | useful_god_candidate | 师传口径 | batch_012_taxonomy_001 | `review-note:mingli_true_formula_teacher.md#source-window-useful-god-season` | `page:154; source=mingli_true_formula_teacher_pdf; heading:tiaohou-principle` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_taboo_god_candidate_001 | 忌神候选 | taboo_god_candidate | 师传口径 | batch_012_taxonomy_001 | `review-note:mingli_true_formula_teacher.md#source-window-taboo-god-damage` | `page:250; source=mingli_true_formula_teacher_pdf; heading:jishen-boundary` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_taboo_god_candidate_002 | 忌神引动 | taboo_god_candidate | 师传口径 | batch_012_taxonomy_001 | `review-note:mingli_true_formula_teacher.md#source-window-taboo-god-trigger` | `page:250; source=mingli_true_formula_teacher_pdf; heading:jishen-trigger-boundary` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_ten_god_relation_001 | 十神功能 | ten_god_relation | 师传口径 | batch_012_taxonomy_001 | `review-note:mingli_true_formula_teacher.md#source-window-ten-god-function` | `page:155; source=mingli_true_formula_teacher_pdf; heading:ten-god-classification` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| mingxue_five_element_balance_002 | 五行季令 | five_element_balance | 通论 | batch_012_taxonomy_001 | `review-note:mingxue_golden_voice.md#source-window-five-element-season` | `page:104; source=mingxue_golden_voice_pdf; heading:five-element-season-command` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| mingxue_five_element_balance_003 | 五行流通 | five_element_balance | 通论 | batch_012_taxonomy_001 | `review-note:mingxue_golden_voice.md#source-window-five-element-flow` | `page:114; source=mingxue_golden_voice_pdf; heading:yin-yang-forward-reverse-five-elements` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| mingxue_ten_god_relation_001 | 十神术语 | ten_god_relation | 通论 | batch_012_taxonomy_001 | `review-note:mingxue_golden_voice.md#source-window-ten-god-terms` | `chapter:source=mingxue_golden_voice_pdf; section=ten-god-terms` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| mingxue_ten_god_relation_002 | 十神平衡 | ten_god_relation | 通论 | batch_012_taxonomy_001 | `review-note:mingxue_golden_voice.md#source-window-ten-god-balance` | `chapter:source=mingxue_golden_voice_pdf; section=ten-god-balance` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| mingxue_useful_god_candidate_001 | 用神候选 | useful_god_candidate | 通论 | batch_012_taxonomy_001 | `review-note:mingxue_golden_voice.md#source-window-useful-god-flow` | `page:93; source=mingxue_golden_voice_pdf; heading:favorable-taboo-notes` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| mingxue_taboo_god_candidate_001 | 忌神候选 | taboo_god_candidate | 通论 | batch_012_taxonomy_001 | `review-note:mingxue_golden_voice.md#source-window-taboo-god-imbalance` | `page:93; source=mingxue_golden_voice_pdf; heading:favorable-taboo-notes` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| mingxue_pattern_strength_001 | 格局术语 | pattern_strength | 通论 | batch_012_taxonomy_001 | `review-note:mingxue_golden_voice.md#source-window-pattern-terminology` | `page:72; source=mingxue_golden_voice_pdf; heading:core-terminology` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| fortune_remedy_boundary_002 | 低风险调整 | remedy_boundary | 通俗命理 | batch_012_taxonomy_001 | `review-note:fortune_reading_hongfu_qitian.md#source-window-remedy-low-risk-action` | `chapter:source=fortune_reading_hongfu_qitian_pdf; section=remedy-low-risk-action` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| fortune_remedy_boundary_003 | 调整语言 | remedy_boundary | 通俗命理 | batch_012_taxonomy_001 | `review-note:fortune_reading_hongfu_qitian.md#source-window-remedy-language` | `chapter:source=fortune_reading_hongfu_qitian_pdf; section=remedy-language` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| fortune_remedy_boundary_004 | 付费边界 | remedy_boundary | 通俗命理 | batch_012_taxonomy_001 | `review-note:fortune_reading_hongfu_qitian.md#source-window-remedy-paid-boundary` | `chapter:source=fortune_reading_hongfu_qitian_pdf; section=remedy-paid-boundary` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| fortune_luck_cycle_001 | 阶段提示 | luck_cycle | 通俗命理 | batch_012_taxonomy_001 | `review-note:fortune_reading_hongfu_qitian.md#source-window-popular-luck-cycle` | `page:54; source=fortune_reading_hongfu_qitian_pdf; heading:minggong-xiaoxian-liunian` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| fortune_ten_god_relation_001 | 十神通俗解释 | ten_god_relation | 通俗命理 | batch_012_taxonomy_001 | `review-note:fortune_reading_hongfu_qitian.md#source-window-popular-ten-god` | `page:41; source=fortune_reading_hongfu_qitian_pdf; heading:six-relations-ten-god` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| fortune_useful_god_candidate_001 | 用神通俗化 | useful_god_candidate | 通俗命理 | batch_012_taxonomy_001 | `review-note:fortune_reading_hongfu_qitian.md#source-window-popular-useful-god` | `page:69; source=fortune_reading_hongfu_qitian_pdf; heading:yongshen-section-start` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| fortune_taboo_god_candidate_001 | 忌神通俗化 | taboo_god_candidate | 通俗命理 | batch_012_taxonomy_001 | `review-note:fortune_reading_hongfu_qitian.md#source-window-popular-taboo-god` | `chapter:source=fortune_reading_hongfu_qitian_pdf; section=popular-taboo-god` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| life_death_high_risk_signal_002 | 高风险不确定性 | high_risk_signal | 传统高风险材料 | batch_012_taxonomy_001 | `page:4; heading:序言` |  | PAGE_EXACT | no change needed |
| life_death_high_risk_signal_003 | 高风险公式边界 | high_risk_signal | 传统高风险材料 | batch_012_taxonomy_001 | `page:6; heading:古今生死秘诀` |  | PAGE_EXACT | no change needed |
| life_death_high_risk_signal_004 | 高风险实践边界 | high_risk_signal | 传统高风险材料 | batch_012_taxonomy_001 | `page:10; heading:命法天关` |  | PAGE_EXACT | no change needed |
| life_death_luck_cycle_001 | 限运阶段 | luck_cycle | 传统高风险材料 | batch_012_taxonomy_001 | `page:13; heading:限运法` |  | PAGE_EXACT | no change needed |
| life_death_luck_cycle_002 | 岁运动态 | luck_cycle | 传统高风险材料 | batch_012_taxonomy_001 | `page:12; heading:流生流组` |  | PAGE_EXACT | no change needed |
| life_death_pattern_strength_001 | 高风险格局转写 | pattern_strength | 传统高风险材料 | batch_012_taxonomy_001 | `page:6; heading:格局生死引用` |  | PAGE_EXACT | no change needed |
| life_death_branch_interaction_001 | 高风险地支互动 | branch_interaction | 传统高风险材料 | batch_012_taxonomy_001 | `page:3; heading:地支合会灾咎` |  | PAGE_EXACT | no change needed |
| life_death_remedy_boundary_001 | 解灾边界 | remedy_boundary | 传统高风险材料 | batch_012_taxonomy_001 | `page:2; heading:解关口秘法` |  | PAGE_EXACT | no change needed |
| life_death_remedy_boundary_002 | 高风险行动边界 | remedy_boundary | 传统高风险材料 | batch_012_taxonomy_001 | `page:11; heading:实践应用` |  | PAGE_EXACT | no change needed |
| life_death_book_boundary_signal_001 | 生死高风险边界 | high_risk_signal | 传统高风险材料 | batch_012_taxonomy_001 | `review-note:life_death_book_100_pages.md#source-window-risk-boundary` | `Markdown/2800.《命理生死之书》100页.md#L157` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| northeast_blind_image_007 | 象法条件信号 | blind_image_method | 东北盲派 | batch_012_taxonomy_001 | `review-note:northeast_blind_peak.md#source-window-blind-image-method` | `page:2; source=northeast_blind_peak_pdf; heading:eight-method-rules` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| duan_ten_god_relation_004 | 十神关系分类 | ten_god_relation | 段氏 | batch_012_taxonomy_001 | `review-note:duan_plain_mingxue_outline.md#source-window-ten-god-relation` | `page:66; source=duan_plain_mingxue_outline_pdf; heading:ten-god-relation-start` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| mingxue_five_element_balance_004 | 五行平衡术语 | five_element_balance | 命学 | batch_012_taxonomy_001 | `review-note:mingxue_golden_voice.md#source-window-five-element-balance-terms` | `page:104; source=mingxue_golden_voice_pdf; heading:five-element-balance-terms` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| teacher_pattern_strength_004 | 格局强度条件信号 | pattern_strength | 命理真诀 | batch_012_taxonomy_001 | `review-note:mingli_true_formula_teacher.md#source-window-pattern-strength-conditions` | `page:121; source=mingli_true_formula_teacher_pdf; heading:pattern-strength-conditions` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| fortune_remedy_boundary_005 | 补救边界条件信号 | remedy_boundary | 鸿福 | batch_012_taxonomy_001 | `review-note:fortune_reading_hongfu_qitian.md#source-window-remedy-boundary-conditions` | `chapter:source=fortune_reading_hongfu_qitian_pdf; section=remedy-boundary-conditions` | REVIEW_NOTE_SOURCE_WINDOW | improved |
| batch002_useful_god_comparison_001 | 用神比较 | useful_god_candidate | 梁湘润教材 | batch_markdown_registration_001 | `review-note:Markdown/source_batch_002_cleaned/简体《子平教材讲义第二级次》梁湘润(1).md#L515` |  | MARKDOWN_SOURCE_LINE | improved |
| batch001_pattern_strength_001 | 取格局与日主强弱 | pattern_strength | 梁湘润体系 | batch_markdown_registration_001 | `review-note:Markdown/source_batch_001_cleaned/简体《子平基础概要》梁湘润_ce.md#L1004` |  | MARKDOWN_SOURCE_LINE | improved |
| batch001_ten_god_relation_001 | Ten-god relation positioning system | ten_god_relation | Liang Xiangrun lineage | batch_markdown_registration_001 | `review-note:Markdown/source_batch_001_cleaned/简体《子平基础概要》梁湘润_ce.md#L3331` |  | MARKDOWN_SOURCE_LINE | improved |
| batch001_branch_interaction_001 | Branch interaction patterns (刑冲合会) | branch_interaction | Mainstream Ziping | batch_markdown_registration_001 | `review-note:Markdown/source_batch_001_cleaned/简体《子平基础概要》梁湘润_ce.md#L221` |  | MARKDOWN_SOURCE_LINE | improved |
| batch001_blind_image_method_001 | Blind-school image method conditional signals | blind_image_method | Blind school (Central Plains) | batch_markdown_registration_001 | `review-note:Markdown/source_batch_001_cleaned/中原盲派命理秘典.md#L9` |  | MARKDOWN_SOURCE_LINE | improved |
| batch002_pattern_strength_001 | Pattern strength taxonomy from Liang Xiangrun textbook series | pattern_strength | Liang Xiangrun lineage | batch_markdown_registration_001 | `review-note:Markdown/source_batch_002_cleaned/简体《子平教材讲义第二级次》梁湘润(1).md#L657` |  | MARKDOWN_SOURCE_LINE | improved |
| batch002_luck_cycle_001 | Luck cycle trigger identification from Liang Xiangrun case material | luck_cycle | Liang Xiangrun lineage | batch_markdown_registration_001 | `review-note:Markdown/source_batch_002_cleaned/简体《子平母法—大流年判例》梁湘润(1).md#L137` |  | MARKDOWN_SOURCE_LINE | improved |
| batch002_ten_god_relation_001 | Ten-god relation taxonomy from Liang Xiangrun textbook series | ten_god_relation | Liang Xiangrun lineage | batch_markdown_registration_001 | `review-note:Markdown/source_batch_002_cleaned/简体 梁湘润《子平教材讲义第一级次》ce.md#L4797` |  | MARKDOWN_SOURCE_LINE | improved |
| batch004_useful_god_001 | Advanced use-god comparison across Shen/Yu/Yuanhai systems | useful_god_candidate | Liang Xiangrun lineage | batch_markdown_registration_001 | `review-note:Markdown/source_batch_004_cleaned/简体《渊海喜忌随笔》梁湘润(1).md#L20` |  | MARKDOWN_SOURCE_LINE | improved |
| batch004_pattern_strength_001 | Advanced pattern strength and preference/avoidance rules | pattern_strength | Liang Xiangrun lineage | batch_markdown_registration_001 | `review-note:Markdown/source_batch_004_cleaned/简体《沈氏用神例解》梁湘润(精校)(1).md#L1522` |  | MARKDOWN_SOURCE_LINE | improved |
| batch004_branch_interaction_001 | Four-corner formation branch interaction framework | branch_interaction | Liang Xiangrun lineage (four-corner formation) | batch_markdown_registration_001 | `review-note:Markdown/source_batch_004_cleaned/简体《四角方阵刑冲合会透解》梁湘润2024(1).md#L263` |  | MARKDOWN_SOURCE_LINE | improved |
| batch004_luck_cycle_001 | Advanced luck-cycle trigger identification | luck_cycle | Liang Xiangrun lineage | batch_markdown_registration_001 | `review-note:Markdown/source_batch_004_cleaned/简体《流年法典》梁湘润_(1).md#L28` |  | MARKDOWN_SOURCE_LINE | improved |
| kskeleton_q001_foundation | q001: foundation | ten_god_relation | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q001_foundation_tables/q001_foundation_tables.md` |  | REVIEW_NOTE_KS_PATH | improved |
| kskeleton_q002_yushi | q002: yushi | useful_god_candidate | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q002_yongshen_tiaohou/q002_yongshen_tiaohou.md` |  | REVIEW_NOTE_KS_PATH | improved |
| kskeleton_q002_shen | q002: shen | useful_god_candidate | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q002_yongshen_tiaohou/shen_pattern_yongshen_framework.md` |  | REVIEW_NOTE_KS_PATH | improved |
| kskeleton_q002_yuanhai | q002: yuanhai | useful_god_candidate | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q002_yongshen_tiaohou/shen_yuanhai_comparison_notes.md` |  | REVIEW_NOTE_KS_PATH | improved |
| kskeleton_q003_geju | q003: geju | pattern_strength | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q003_geju_strength/geju_selection_rules.csv` |  | REVIEW_NOTE_KS_PATH | improved |
| kskeleton_q003_day | q003: day | pattern_strength | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q003_geju_strength/day_master_strength_rules.csv` |  | REVIEW_NOTE_KS_PATH | improved |
| kskeleton_q003_congwang | q003: congwang | pattern_strength | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q003_geju_strength/congwang_congshi_candidates.csv` |  | REVIEW_NOTE_KS_PATH | improved |
| kskeleton_q006_interaction | q006: interaction | branch_interaction | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q006_branch_interaction/q006_interaction_schema.md` |  | REVIEW_NOTE_KS_PATH | improved |
| kskeleton_q004_mechanism | q004: mechanism | luck_cycle | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q004_luck_cycle_boundary/q004_mechanism_schema.md` |  | REVIEW_NOTE_KS_PATH | improved |
| kskeleton_q004_cross | q004: cross | luck_cycle | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q004_luck_cycle_boundary/q004_cross_review_backlog.md` |  | REVIEW_NOTE_KS_PATH | improved |
| kskeleton_q004_q006 | q004: q006 | luck_cycle | Multiple lineages | batch_kskeleton_taxonomy_001 | `review-note:knowledge_skeleton/q004_luck_cycle_boundary/q004_q006_dependency_patch.md` |  | REVIEW_NOTE_KS_PATH | improved |
| batch005_ten_god_relation_001 | ten god relation: batch 005 training notes | ten_god_relation | Wuyang course notes | batch_markdown_registration_001 | `review-note:Markdown/source_batch_005_cleaned/高阶资料1-6节.md#L58` |  | MARKDOWN_SOURCE_LINE | improved |
| batch005_blind_image_method_001 | blind image method: batch 005 training notes | blind_image_method | Wuyang course notes | batch_markdown_registration_001 | `review-note:Markdown/source_batch_005_cleaned/高阶资料1-6节.md#L5` |  | MARKDOWN_SOURCE_LINE | improved |
| batch005_branch_interaction_001 | branch interaction: batch 005 training notes | branch_interaction | Wuyang course notes | batch_markdown_registration_001 | `review-note:Markdown/source_batch_005_cleaned/11节 刑冲取象复习笔记.md#L5` |  | MARKDOWN_SOURCE_LINE | improved |

## Recommendations

1. OCR pass: prioritize the 13 CID-backed chapter windows that still lack exact page matches.
2. Northeast manual review pass: only upgrade the 3 remaining Northeast chapter windows after a topic-page match is visually confirmed.
3. Audit automation: promote this classification logic into a dedicated command if future curation passes need repeatable report generation.
