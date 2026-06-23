with open("tests/unit/test_materials_audit.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i in range(1319, 1342):
    if i < len(lines):
        print(str(i+1) + ":" + repr(lines[i]))
