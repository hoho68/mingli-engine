# Knowledge Skeleton 引用准确性验证报告

验证范围: 资料整理/knowledge_skeleton/ 中所有 CSV 文件
Markdown 源文件数: 44
CSV 引用总数: 187

## 验证结果

- **文件存在性**: 187/187 成功 (100%)
- **行号范围**: 全部在文件范围内
- **多文件引用**: 5 条，文件全部存在

## 按 CSV 文件分布

| CSV 文件 | 引用数 |
|----------|--------|
| q003_geju_strength/geju_success_failure_candidates.csv | 37 |
| q004_luck_cycle_boundary/q004_luck_trigger_candidates.csv | 24 |
| q003_geju_strength/congwang_congshi_candidates.csv | 19 |
| q002_yongshen_tiaohou/q002_extraction_manifest.csv | 15 |
| q002_yongshen_tiaohou/yuanhai_dual_yongshen_notes.csv | 12 |
| q003_geju_strength/wuxing_missing_candidates.csv | 11 |
| q002_yongshen_tiaohou/yuanhai_high_risk_boundary.csv | 10 |
| q002_yongshen_tiaohou/shen_pattern_categories.csv | 8 |
| q002_yongshen_tiaohou/shen_pattern_success_failure.csv | 8 |
| q002_yongshen_tiaohou/shen_yangren_jianlu_mapping_review.csv | 8 |
| q002_yongshen_tiaohou/yuanhai_ming_pattern_xiji.csv | 8 |
| q006_branch_interaction/q006_interaction_candidates.csv | 8 |
| q003_geju_strength/day_master_strength_rules.csv | 7 |
| q001_foundation_tables/q001_extraction_manifest.csv | 6 |
| q003_geju_strength/geju_selection_rules.csv | 6 |

## 按风险级别分布

- medium: 59
- low: 24
- 破格候选 非报告断语: 16
- high_risk: 14
- 救应条件 非报告断语: 7
- 结构条件 非报告断语: 6
- medium_to_high: 5
- sensitive: 4
- 需回查 PDF 或更好 OCR 不可补造: 2
- high_risk_boundary: 1
- 只作分类边界 非正式证据: 1
- 不得把特别格直接等同吉凶: 1
- 旧式人生断语已剥离: 1
- 富贵评价不纳入规则: 1
- 残疾等高风险断语剥离: 1
- 只保留结构与限制条件: 1
- 贵贱评价不纳入规则: 1
- 人格贫富类断语剥离: 1
- 疾病贫困类断语剥离: 1
- 旧式评价语剥离: 1
- 不直接断事: 1
- 分型需结合全局复核: 1
- 见根时不得轻率归从势: 1
- 避免过度归类: 1
- 作为复核问题而非结论: 1
- 羡慕 富贵 婚姻类评价剥离: 1
- 转 G005 继续处理: 1
- 单条注释需后续交叉复核: 1
- 不得机械以全局定从旺: 1
- 不得把强弱直接转成吉凶断语: 1
- 不得绕过调候层直接输出报告规则: 1
- 不得写成一定好坏: 1
- 当前只到分类入口: 1
- 不得构造虚假精确分数: 1
- 高风险和确定性断语剥离: 1
- 不得提前归入从格: 1
- 结构规则不得直接断事: 1
- 特殊格不得与常规格混并: 1
- 优先序是取格程序不是吉凶等级: 1
- 归并后仍需全局复核: 1
- 不得只凭单一透干定格: 1
- 合会取格仍需排除高风险断语: 1
- 只限定抽取范围 非正式证据: 1
- 取格程序不得直接断事: 1
- 示例只作取格优先说明: 1
- 透干变化只作候选分支: 1
- 不得以日主强弱单独定成败: 1
- 善不善不得写成好坏吉凶: 1
- 术语与羊刃需沿用 Q002 映射复核: 1
- 建禄与月劫需保留术语差异: 1
- 只作概念边界 非正式证据: 1
- 转 Q005 或高风险语言复核: 1
- 健康体弱类不得转报告规则: 1
- 不作优劣判断: 1
- 不得单一路径定格: 1
- 需要组合枚举后再复核: 1
- 标为待研究 不生成规则: 1
- 禁止机械吉凶二分: 1
- 作为体系边界 非报告规则: 1
- 未标注: 0

## 结论

知识骨架中所有 CSV 文件的 source_file + source_lines 引用全部有效。
说明候选规则的来源追溯是完整的，可以在后续自动化流程中信赖这些引用。