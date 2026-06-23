import json

# Check candidate_extracts.json
with open("src/mingli_engine/data/source_intake/candidate_extracts.json", "r", encoding="utf-8") as f:
    data = json.load(f)
items = data if isinstance(data, list) else data.get("candidate_extracts", data.get("items", []))

ks_candidates = [c for c in items if "kskeleton" in c.get("candidate_id", "").lower() or "kskeleton" in c.get("material_id", "").lower()]
batch005_promoted = [c for c in items if "batch_005" in c.get("candidate_id", "") or "batch005" in c.get("candidate_id", "")]
print("=== KSkeleton Candidates ===")
for c in ks_candidates:
    print("  " + c.get("candidate_id") + ": status=" + c.get("status"))

print("\n=== Batch 005 Candidates ===")
for c in batch005_promoted:
    print("  " + c.get("candidate_id") + ": status=" + c.get("status"))

# Count by status
from collections import Counter
status_counts = Counter(c.get("status") for c in items)
print("\n=== All Candidates by Status ===")
for k, v in sorted(status_counts.items()):
    print("  " + k + ": " + str(v))
print("  Total: " + str(len(items)))
