# -*- coding: utf-8 -*-
import os, csv

# 从 knowledge_skeleton 所有 CSV 中提取 source_file 引用信息
ks_base = "资料整理/knowledge_skeleton"
md_base = "Markdown"

# 扫描所有 CSV 文件
all_entries = []
for root, dirs, files in os.walk(ks_base):
    for f in files:
        if f.endswith(".csv"):
            fpath = os.path.join(root, f)
            rel_dir = os.path.relpath(root, ks_base)
            with open(fpath, encoding="utf-8") as fh:
                try:
                    reader = csv.DictReader(fh)
                    for row in reader:
                        # 检查是否有 source_file 和 source_lines 列
                        src_file = row.get("source_file", row.get("source", "")).strip()
                        src_lines = row.get("source_lines", row.get("lines", "")).strip()
                        if src_file and src_lines:
                            all_entries.append({
                                "csv_file": f"{rel_dir}/{f}",
                                "source_file": src_file,
                                "source_lines": src_lines,
                                "rule_id": row.get("rule_id", row.get("candidate_id", row.get("mapping_id", ""))),
                                "theme": row.get("theme", "")[:40],
                                "risk": row.get("risk_boundary", row.get("risk_level", "")),
                            })
                except Exception as ex:
                    pass

print(f"=== 从知识骨架 CSV 中提取到 {len(all_entries)} 条 source_file 引用 ===")

# 统计引用了哪些 Markdown 文件
from collections import Counter
file_counts = Counter(e["source_file"] for e in all_entries)
print(f"\n引用的 Markdown 文件分布:")
for fname, cnt in file_counts.most_common():
    print(f"  [{cnt}] {fname}")

# 检查这些 Markdown 文件是否存在于 Markdown 目录中
print(f"\n引用准确性验证:")
found = 0
not_found = 0
for fname, cnt in file_counts.most_common():
    # 在 Markdown 目录中搜索
    file_path = None
    for md_root, md_dirs, md_files in os.walk(md_base):
        if fname in md_files:
            file_path = os.path.join(md_root, fname)
            break
    if file_path:
        found += 1
        file_size = os.path.getsize(file_path)
        print(f"  [OK] {fname} -> {file_path} ({file_size} bytes)")
    else:
        not_found += 1
        print(f"  [MISSING] {fname}")

print(f"\n存在: {found}, 不存在: {not_found}, 总计: {found+not_found}")

# 检查行号是否有效
print(f"\n行号范围验证 (抽样):")
line_issues = []
for e in all_entries[:50]:
    src_file = e["source_file"]
    src_lines = e["source_lines"]
    
    # 找到文件
    file_path = None
    for md_root, md_dirs, md_files in os.walk(md_base):
        if src_file in md_files:
            file_path = os.path.join(md_root, src_file)
            break
    
    if not file_path:
        line_issues.append((src_file, src_lines, "FILE_NOT_FOUND"))
        continue
    
    with open(file_path, encoding="utf-8", errors="replace") as fh:
        total_lines = sum(1 for _ in fh)
    
    # 解析行号范围 (支持 "L1-L10" 或 "1000-2000" 或 "1000-2000;3000-4000")
    ranges = src_lines.replace("L", "").split(";")
    for r in ranges:
        r = r.strip()
        if "-" in r:
            parts = r.split("-")
            try:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                if end > total_lines:
                    line_issues.append((src_file, src_lines, f"END_LINE_{end}>TOTAL_{total_lines}"))
            except:
                pass

print(f"\n行号超出文件范围的问题: {len(line_issues)}")
for fname, lines, issue in line_issues[:10]:
    print(f"  [{issue}] {fname} lines={lines}")
