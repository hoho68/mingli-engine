# 八字算命藏诀（bazi_suanming_cangjue）新材料推进交接

更新：2026-07-09
分支：`codex/complete-new-material-learning`

本文档记录为新材料 `八字算命藏诀-黑白.pdf`（id 词干 `bazi_suanming_cangjue`）推进
提取/学习链路的进度、遇到的问题、以及未完成的工作。供新线程的智能体续作。

---

## 一、目标

从 `bazi_general_misc_identity_review_cluster` 中选一个**真正未处理**的普通风险
PDF，复用 `xiahai_suanmingji`（下海算命记）的 015-new-material 链路，推进到 017
学习笔记 + 013 候选。最终选定的资料是 `八字算命藏诀-黑白.pdf`（21MB，50 页，纯
图像扫描，无文本层）。

---

## 二、已完成（已提交，可靠）

以下 5 个 commit 已提交到分支，测试已验证通过：

```
741f220 feat: close expanded corrected learning loop   ← 上一个任务（扩展校正闭环）
0caf435 feat: select bazi suanming cangjue new material intake
6cc3662 feat: review bazi suanming cangjue source identity
2a49284 feat: register bazi suanming cangjue new material source
```

### Stage 0：集群代表路径
- 将 `八字算命藏诀-黑白.pdf` 加为 `bazi_general_misc_identity_review_cluster`
  的第 4 个 representative_path（文件 `raw_text_source_cluster_selection_items.json`）
- 匹配 `算命` filename_marker，风险 ordinary

### Stage 1：015-new-material-intake（已提交，测试通过）
- 新增第 2 条 intake item：`new_material_intake_bazi_suanming_cangjue_pdf`
- 文件：`src/mingli_engine/data/materials_audit/new_material_intake_items.json`
- 测试：`test_new_material_intake_*`（3 个，len 1→2，全通过）

### Stage 2：015-new-material-source-identity-review（已提交，测试通过）
- 新增第 2 条 identity-review item：`new_material_identity_bazi_suanming_cangjue_pdf`
- canonical_title_label: `Bazi Suanming Cangjue (Bazi Fortune-Telling Hidden Formulas)`
- 确认八字直接适配 branch_interaction，无星命/非八字边界问题
- 文件：`new_material_source_identity_review_items.json`
- 测试：`test_new_material_source_identity_review_*`（3 个，全通过）

### Stage 3：015-new-material-registration-prep（已提交，测试通过）
- 新增第 2 条 prep item：`new_material_registration_prep_bazi_suanming_cangjue_pdf`
- source_library_entry_id: `entry_new_material_bazi_suanming_cangjue_pdf`
- 文件：`new_material_registration_prep_items.json`
- 测试：`test_new_material_registration_prep_*`（通过）

### Stage 4：015-new-material-source-registration（已提交，测试通过）
- 新增第 2 条 registration item
- **真正写入 source_library**：`entry_new_material_bazi_suanming_cangjue_pdf`
  （文件 `source_library/source_library_entries.json`，现 32 条）
- 新增 priority assessment：`priority_new_material_bazi_suanming_cangjue_001`
  （文件 `source_library/source_priority_assessments.json`，现 30 条）
- 文件：`new_material_source_registration_items.json`
- 测试：`test_source_library.py` 计数测试（31→32, 29→30）已更新通过

### Stage 5：015-new-material-preparation-boundary（已提交，测试通过）
- 新增第 2 条 boundary item，reading_status 阻塞
- 文件：`new_material_preparation_boundary_items.json`
- 测试：`test_new_material_source_registration_and_boundary_*` + `long_goal`（通过）

### 架构改进（已提交）
- **泛化 entry/material id 校验**：`registration-prep` validator 原硬编码
  `NEW_MATERIAL_SOURCE_LIBRARY_ENTRY_ID`（仅 xiahai），改为 `startswith("entry_new_material_")`
  前缀校验（`materials_audit.py` ~L10026）
- **泛化 overlap 排除**：identity-review 的 source-library overlap 检查原排除单一
  xiahai 常量，改为排除所有 `entry_new_material_*`（2 处：~L9742 per-item validator、
  ~L9795 summary builder）

---

## 三、未提交的工作区改动（Stage 6-8，数据正确但测试超时）

以下 6 个文件有未提交改动，**数据逻辑已验证正确**，但因 loader 性能问题无法在
限时内跑通测试：

```
M src/mingli_engine/data/materials_audit/new_material_controlled_text_preparation_items.json  (1→2)
M src/mingli_engine/data/materials_audit/new_material_ocr_or_manual_transcription_items.json  (1→2)
M src/mingli_engine/data/materials_audit/new_material_ocr_runtime_setup_items.json            (1→2)
M tests/unit/test_materials_audit.py  (Stage 6-8 测试已更新 len 1→2 + 聚合计数)
M docs/classical_sources/materials_audit.md  (OCR 两节 docs 已更新)
M docs/classical_sources/new_material_learning_handoff.md  (OCR 两节 checkpoint 已更新)
```

### Stage 6：controlled-text-preparation（数据已填，测试通过）
- 真实探测：pdfplumber 探测 `八字算命藏诀-黑白.pdf` → **50 页，0 文本层页面，0 字符**
  （纯图像扫描，与 xiahai 的 84 页/13 非空不同）
- preparation_status: `blocked_requires_ocr_or_manual_transcription`
- **此阶段测试已验证通过**（`test_new_material_controlled_text_preparation_blocks` PASSED）

### Stage 7：OCR-or-manual-transcription（数据已填，loader 超时）
- tesseract_available: false（此阶段要求 runtime 尚未配置）
- pdftoppm_available: false（实际用 pdfplumber 渲染）
- blocker: 默认 tessdata 缺 chi_sim

### Stage 8：OCR-runtime-setup（数据已填，loader 超时）
- **真实 OCR 探测数据**（用 TESSDATA_PREFIX 指向备用 chi_sim 路径）：
  - tesseract 5.5.0.20241111，chi_sim 可用（via 备用路径）
  - 探测 pages 1/11/25/41，300 DPI，PSM 3/4/6
  - **PSM 6 最佳**：page 11 得 222 汉字，page 25 得 221，page 41 得 185
  - 但识别错误仍太多（输出含大量错字/拉丁字母混杂），quality 不足
  - setup_status: `blocked_ocr_quality_insufficient`

### 数据交叉校验已验证
两条 cangjue OCR 记录与上游 controlled-text-prep 的 source_library_entry_id /
source_material_id / local_reference / page_count 字段**全部一致**（用直接 JSON
读取验证，绕过慢 loader）。

---

## 四、核心问题：loader 嵌套加载性能 bug（阻塞 Stage 7-8 测试）

### 现象
`load_new_material_ocr_or_manual_transcription_items()` 单次调用即超过 5 分钟
超时，无法跑通测试。controlled-text-prep（Stage 6）能通过但也很慢。

### 根因
每个 `_xxx_item_from_dict` validator 内部都调用 `load_<上游>_items(source_dir)`
重新加载**全部**上游 items，而上游的每个 item 又触发它的上游加载，形成**嵌套
重复加载**：

```
OCR-or-manual validator (每个 item)
  → load_new_material_controlled_text_preparation_items (全部)
      → 每个 prep item 的 validator
          → load_new_material_preparation_boundary_items (全部)
              → 每个 boundary item 的 validator
                  → load_new_material_source_registration_items (全部)
                      → load_new_material_registration_prep_items (全部)
                          → load_new_material_source_identity_review_items (全部)
                              → load_new_material_intake_items (全部)
                                  → load cluster / source_library ...
```

### 实测耗时（单次调用）
- `load_new_material_registration_prep_items`: ~6 秒（2 items）
- `load_new_material_source_registration_items`: ~12 秒（2 items）
- `load_new_material_preparation_boundary_items`: ~25 秒（2 items）
- `load_new_material_controlled_text_preparation_items`: 更久
- `load_new_material_ocr_or_manual_transcription_items`: >5 分钟（超时）

### 为何 xiahai 单条时没暴露
xiahai 时代每个文件只有 1 条 item，嵌套深度虽深但每层只校验 1 条，勉强可跑
（单次 ~6-25 秒）。加了 cangjue 第 2 条后，每层 ×2，嵌套指数爆炸。

### 可能的修法（未实施）
1. **加缓存/memoization**：在每次 `load_*_items` 调用中缓存结果，避免同一次
   测试运行内重复加载上游。风险低。
2. **把交叉校验移出 `_from_dict`**：`_from_dict` 只做字段/枚举校验，交叉引用
   校验移到 `build_*_summary` 或单独的 `validate_*` 函数。改动面大但最干净。
3. **loader 接受预加载的上游数据**：`load_xxx(source_dir, upstream_cache=...)`。
   介于 1 和 2 之间。

---

## 五、Stage 9+ 的环境阻塞（无法继续）

即使修好 loader 性能，后续阶段也有真实的环境限制：

### Stage 9：OCR-quality-remediation（被环境卡住）
- validator **强制要求 `chi_tra_vert`（繁体竖排）tessdata 可用**
  （`materials_audit.py` ~L11062: `if not item.vertical_tessdata_available: raise`，
  且 tessdata_language_codes 必须含 `chi_tra_vert`）
- 当前系统**只有 `chi_sim`（简体）**，无 `chi_tra_vert`
  - 默认 tessdata（`C:\Program Files\Tesseract-OCR\tessdata`）：只有 eng, osd
  - 备用路径（`C:\Users\lei\AppData\Roaming\TRAE SOLO CN\...\tessdata`）：只有 chi_sim
- 不能谎称有 chi_tra_vert → cangjue 诚实阻塞在 Stage 8

### 后续阶段（均需 Stage 9 先通过）
- Stage 10: human-corrected-transcription-prep
- Stage 11: human-corrected-transcription-execution（产出 prepared-text artifact）
- Stage 12: 017 learning-entry-evaluation → learning note + candidate

### xiahai 的参考值
xiahai 当时能通过 Stage 9（有 chi_tra_vert），走的是：
400dpi + split_pages + chi_tra_vert + PSM5 → page_70 得 539 汉字 → 仍需人工校正 →
产出 4 段 35 字 pilot artifact → 进入 017 学习链。

---

## 六、OCR 工具链现状（实测）

| 工具 | 可用 | 备注 |
|---|---|---|
| pdfplumber | ✅ | 0.11.9，可渲染页面 (`page.to_image()`) |
| tesseract | ✅ | 5.5.0.20241111，在 `C:\Program Files\Tesseract-OCR\tesseract.exe` |
| chi_sim | ⚠️ 备用路径 | `TESSDATA_PREFIX=C:/Users/lei/AppData/Roaming/TRAE SOLO CN/ModularData/ai-agent/vm/tools/app/tesseract/tessdata` |
| chi_tra_vert | ❌ | 系统上不存在，Stage 9 validator 硬性要求 |
| pdftoppm | ❌ | 不在 PATH（实际用 pdfplumber 替代渲染） |
| pymupdf (fitz) | ❌ | 未安装 |
| pdf2image | ❌ | 未安装 |
| ocrmypdf | ❌ | 未安装 |

渲染示例（可用）：
```python
import pdfplumber
pdf = pdfplumber.open('资料原文/文本类/八字算命藏诀-黑白.pdf')
im = pdf.pages[10].to_image(resolution=300)
im.save('page.png')
```

OCR 探测示例（可用，但质量不足）：
```bash
TESSDATA_PREFIX="C:/Users/lei/AppData/Roaming/TRAE SOLO CN/ModularData/ai-agent/vm/tools/app/tesseract/tessdata" \
  "/c/Program Files/Tesseract-OCR/tesseract.exe" page.png - -l chi_sim --psm 6
```

---

## 七、misc 集群剩余未处理 PDF

`bazi_general_misc_identity_review_cluster`（source_root `资料原文/文本类/`）中，
匹配 filename_markers（杂项/手抄/星命/算命）且**未注册**到 source_library 的 PDF：

| 文件 | 大小 | 备注 |
|---|---|---|
| `[鬼谷子算命秘术]扫描版.pdf` | 3.7MB | 体积最小，传统命理经典 |
| `八字算命藏诀-黑白.pdf` | 21MB | **← 本次推进中，已到 Stage 8** |
| `命理手抄《五星正命二十八宿命理》106筒子页.pdf` | 51MB | 五星/星命，域适配弱 |
| `师传命理手抄秘本.pdf` | 54MB | 手抄秘本，扫描质量待查 |
| `捷格推理算命.pdf` | 224MB | 体积过大 |

注意：要把这些 PDF 加入 new-material 链路，需先将它们加为集群的
`representative_paths`（validator 要求 path 在 cluster.representative_paths 中）。
当前 representative_paths 有 4 个：望斗经、下海算命记、星命说证、八字算命藏诀。

---

## 八、续作建议

### 选项 A：修 loader 性能 bug 后继续 cangjue
1. 修 `materials_audit.py` 的嵌套加载（建议方案：给 `load_*_items` 加
   `functools.lru_cache` 或在 module 级维护 per-source_dir 缓存）
2. 跑通 Stage 6-8 测试，提交
3. 安装 `chi_tra_vert.traineddata`（下载到 tessdata 目录），推进 Stage 9
4. 完成 Stage 10-12 → 017 学习笔记 + 013 候选

### 选项 B：回退 Stage 6-8，换更小的 PDF
1. `git checkout --` 6 个未提交文件（回退到 Stage 5 干净状态）
2. 选 `[鬼谷子算命秘术]扫描版.pdf`（3.7MB，最小）作为下一个候选
3. 同样会遇到 loader 性能 bug（2 条 item），所以仍需先修性能

### 选项 C：接受 cangjue 当前状态
- cangjue 已注册到 source_library，诚实阻塞在 preparation-boundary
- Stage 6-8 数据正确但未提交（loader 性能问题）
- 把 Stage 6-8 改动保留为 WIP，记录在本文档

**无论哪个选项，loader 性能 bug 都是必须先解决的阻塞项**（只要 new-material
链路有 ≥2 条 item，Stage 6+ 的 loader 就会超时）。

---

## 九、关键文件索引

### 本次改动涉及
- `src/mingli_engine/materials_audit.py` — loader/validator（已改：泛化 entry id）
- `src/mingli_engine/data/materials_audit/new_material_*.json` — 各阶段数据
- `src/mingli_engine/data/source_library/source_library_entries.json` — +1 entry
- `src/mingli_engine/data/source_library/source_priority_assessments.json` — +1 assessment
- `src/mingli_engine/data/materials_audit/raw_text_source_cluster_selection_items.json` — +1 representative_path
- `tests/unit/test_materials_audit.py` — Stage 0-8 测试（0-5 已验证，6-8 已更新未验证）
- `tests/unit/test_source_library.py` — 计数测试（已验证）
- `docs/classical_sources/materials_audit.md` — 各阶段 section
- `docs/classical_sources/new_material_learning_handoff.md` — 各阶段 checkpoint

### 参考文档
- `docs/classical_sources/new_material_learning_handoff.md` — 主交接文档（xiahai 全链路）
- `docs/classical_sources/learning_reference_curation.md` — 017 学习参考总览

### id 映射表（cangjue 全链路）
| 阶段 | item_id |
|---|---|
| cluster | `bazi_general_misc_identity_review_cluster` |
| intake | `new_material_intake_bazi_suanming_cangjue_pdf` |
| identity-review | `new_material_identity_bazi_suanming_cangjue_pdf` |
| registration-prep | `new_material_registration_prep_bazi_suanming_cangjue_pdf` |
| source-registration | `new_material_source_registration_bazi_suanming_cangjue_pdf` |
| preparation-boundary | `new_material_preparation_boundary_bazi_suanming_cangjue_pdf` |
| controlled-text-prep | `new_material_controlled_text_prep_bazi_suanming_cangjue_pdf` |
| ocr-or-manual | `new_material_ocr_or_manual_bazi_suanming_cangjue_pdf` |
| ocr-runtime-setup | `new_material_ocr_runtime_setup_bazi_suanming_cangjue_pdf` |
| source_library entry | `entry_new_material_bazi_suanming_cangjue_pdf` |
| source_material | `material_new_material_bazi_suanming_cangjue_pdf` |
| priority assessment | `priority_new_material_bazi_suanming_cangjue_001` |
| local_reference | `八字算命藏诀-黑白.pdf` |

---

## 十、Guardrails（恪守）

- 不改根 PDF / `Markdown/` / `资料原文/` / `资料整理/` 原文
- `formal_evidence_delta=0`，不新增 013/012 记录（cangjue 尚未到候选阶段）
- 不提交未验证的测试改动（Stage 6-8 数据正确但测试因性能超时未验证）
- 不谎称有不可用的 OCR tessdata（chi_tra_vert）
- OCR 探测产物（临时 png）不提交到仓库
