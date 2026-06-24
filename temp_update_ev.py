# -*- coding: utf-8 -*-
import json, os

# 读取当前数据
with open("src/mingli_engine/data/classical_sources/evidence_units.json", encoding="utf-8") as f:
    ev = json.load(f)

# 定义 REVIEW_NOTE_ID 组的 source_ref 更新映射
# evidence_id -> (new_source_ref, 文件的原始路径引用)
updates = {
    # === KSkeleton Q001 ===
    "kskeleton_q001_foundation": (
        "knowledge_skeleton/q001_foundation_tables/q001_foundation_tables.md",
        "资料整理/knowledge_skeleton/q001_foundation_tables/q001_foundation_tables.md#L1-L104",
    ),
    
    # === KSkeleton Q002 ===
    "kskeleton_q002_yushi": (
        "knowledge_skeleton/q002_yongshen_tiaohou/q002_yongshen_tiaohou.md",
        "资料整理/knowledge_skeleton/q002_yongshen_tiaohou/q002_yongshen_tiaohou.md",
    ),
    "kskeleton_q002_shen": (
        "knowledge_skeleton/q002_yongshen_tiaohou/shen_pattern_yongshen_framework.md",
        "资料整理/knowledge_skeleton/q002_yongshen_tiaohou/shen_pattern_yongshen_framework.md",
    ),
    "kskeleton_q002_yuanhai": (
        "knowledge_skeleton/q002_yongshen_tiaohou/shen_yuanhai_comparison_notes.md",
        "资料整理/knowledge_skeleton/q002_yongshen_tiaohou/shen_yuanhai_comparison_notes.md",
    ),
    
    # === KSkeleton Q003 ===
    "kskeleton_q003_geju": (
        "knowledge_skeleton/q003_geju_strength/geju_selection_rules.csv",
        "资料整理/knowledge_skeleton/q003_geju_strength/geju_selection_rules.csv",
    ),
    "kskeleton_q003_day": (
        "knowledge_skeleton/q003_geju_strength/day_master_strength_rules.csv",
        "资料整理/knowledge_skeleton/q003_geju_strength/day_master_strength_rules.csv",
    ),
    "kskeleton_q003_congwang": (
        "knowledge_skeleton/q003_geju_strength/congwang_congshi_candidates.csv",
        "资料整理/knowledge_skeleton/q003_geju_strength/congwang_congshi_candidates.csv",
    ),
    
    # === KSkeleton Q004 ===
    "kskeleton_q004_mechanism": (
        "knowledge_skeleton/q004_luck_cycle_boundary/q004_mechanism_schema.md",
        "资料整理/knowledge_skeleton/q004_luck_cycle_boundary/q004_mechanism_schema.md",
    ),
    "kskeleton_q004_cross": (
        "knowledge_skeleton/q004_luck_cycle_boundary/q004_cross_review_backlog.md",
        "资料整理/knowledge_skeleton/q004_luck_cycle_boundary/q004_cross_review_backlog.md",
    ),
    "kskeleton_q004_q006": (
        "knowledge_skeleton/q004_luck_cycle_boundary/q004_q006_dependency_patch.md",
        "资料整理/knowledge_skeleton/q004_luck_cycle_boundary/q004_q006_dependency_patch.md",
    ),
    
    # === KSkeleton Q006 ===
    "kskeleton_q006_interaction": (
        "knowledge_skeleton/q006_branch_interaction/q006_interaction_schema.md",
        "资料整理/knowledge_skeleton/q006_branch_interaction/q006_interaction_schema.md",
    ),
}

# 对 LEARNING_REF_NOTE 组也需要改进
# 这些 evidence 的 source_ref 已经是 learning-reference:note_id#lp_id 格式
# 但可以补充源文件的路径引用

learning_note_updates = {
    "batch001_pattern_strength_001": (
        "review-note:markdown_source_batch_001.md#pattern-strength (source: Markdown/source_batch_001_cleaned/*.md)",
        "Markdown/source_batch_001_cleaned",
    ),
    "batch001_ten_god_relation_001": (
        "learning-reference:note_markdown_batch_001_pattern_strength_001#lp_markdown_batch_001_ten_god_relation_001",
        "参见 learning_reference_curation.md 中 batch001 pattern strength 笔记",
    ),
    "batch001_branch_interaction_001": (
        "learning-reference:note_markdown_batch_001_pattern_strength_001#lp_markdown_batch_001_branch_interaction_001",
        "同上",
    ),
    "batch001_blind_image_method_001": (
        "learning-reference:note_markdown_batch_001_pattern_strength_001#lp_markdown_batch_001_blind_image_method_001",
        "同上",
    ),
    "batch002_useful_god_comparison_001": (
        "review-note:markdown_source_batch_002_core.md#useful-god-comparison",
        "Markdown/source_batch_002_cleaned",
    ),
    "batch002_pattern_strength_001": (
        "learning-reference:note_markdown_batch_002_useful_god_001#lp_markdown_batch_002_pattern_strength_001",
        "参见 learning_reference_curation.md 中 batch002 笔记",
    ),
    "batch002_luck_cycle_001": (
        "learning-reference:note_markdown_batch_002_useful_god_001#lp_markdown_batch_002_luck_cycle_001",
        "同上",
    ),
    "batch002_ten_god_relation_001": (
        "learning-reference:note_markdown_batch_002_useful_god_001#lp_markdown_batch_002_ten_god_relation_001",
        "同上",
    ),
    "batch004_useful_god_001": (
        "learning-reference:note_markdown_batch_004_001#lp_markdown_batch_004_useful_god_001",
        "参见 learning_reference_curation.md 中 batch004 笔记",
    ),
    "batch004_pattern_strength_001": (
        "learning-reference:note_markdown_batch_004_001#lp_markdown_batch_004_pattern_strength_001",
        "同上",
    ),
    "batch004_branch_interaction_001": (
        "learning-reference:note_markdown_batch_004_001#lp_markdown_batch_004_branch_interaction_001",
        "同上",
    ),
    "batch004_luck_cycle_001": (
        "learning-reference:note_markdown_batch_004_001#lp_markdown_batch_004_luck_cycle_001",
        "同上",
    ),
}

# 执行更新
update_count = 0
kskeleton_count = 0
for e in ev:
    eid = e.get("evidence_id", "")
    
    if eid in updates:
        new_ref, source_path = updates[eid]
        old_ref = e.get("source_ref", "")
        e["source_ref"] = new_ref
        print(f"  [KS] {eid}: {old_ref} -> {new_ref}")
        update_count += 1
        kskeleton_count += 1
    
    # LEARNING_REF_NOTE 组的 source_ref 已经有定位信息，不需要改写
    # 但 REVIEW_NOTE_TOPIC 组中部分 batch005 的已经包含 #lp 锚点，属于 REVIEW_NOTE_ID 级别

# 检查 batch005 的三条——它们的 source_ref 是 review-note:note_markdown_batch_005_001#lp_xxx
# 这个已经包含了 note_id 和 lp_id，精确度足够
for e in ev:
    eid = e.get("evidence_id", "")
    sref = e.get("source_ref", "")
    if "batch005" in eid and sref.startswith("review-note:note_markdown_batch_005_001"):
        print(f"  [batch005] {eid} source_ref 已包含 note+lp 锚点，保留: {sref}")

# 写入更新
with open("src/mingli_engine/data/classical_sources/evidence_units.json", "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=2)

print(f"\n更新完成: {update_count} 条 evidence 的 source_ref 已改进")
