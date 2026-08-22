# batch_20260714 死亡/寿命内容风险处置表（八字推理知识闭环整改）

日期：2026-08-20 ｜ 范围：仅 batch_20260714 派生记录 ｜ 旧知识与六爻文件保持不变

## 1. 方法与筛查分层

处置对象由**确定性证据内容风险分类器**在全部 944 条已推广候选上产生，不硬编码任何数量。筛查经历三层口径，逐层扩大并全部留痕：

| 层 | 口径 | 条数 | 说明 |
|---|---|---:|---|
| L1 | 严格词（死亡/寿命/壽命/夭亡/自杀/自殺/生死关口/死期） | 47 | 任务书"原 50 条"的最接近可复现代理（原始 50 条 ID 清单未提供；47 ⊆ 68 ⊆ 88，为确定超集链） |
| L2 | 复合词筛查（60+ 复合标记） | 68 | 排除 空亡/亡神/死绝 等单字误报 |
| L3 | 确定性分类器（本表口径） | **88** | 在 L2 之外新捕获 20 条真实死亡/寿命内容（含「此运必死人」「父母早亡」「夭壽」「凶亡」等），另复核否定语境与结构术语 |

L1 47 条全部 ⊂ L2 68 条全部 ⊂ L3 88 条。最终处置集合为 L3 的 88 条，分类计数精确相加：A=59 + B=26 + C=3 = **88**。

## 2. 分类定义与处置动作

| 类 | 名称 | 定义 | promotion_action | 最终 risk_tier | 最终 rule_family | 进入报告 |
|---|---|---|---|---|---|---|
| A | exact_death_lifespan_rule | 精确寿命、死亡时间、死亡关口、寿数换算、条件→死亡断语（含引用的古籍死亡断语） | reject_not_promoted（学习记录保留，候选 rejected，证据移除，文件终态必要时重算为 learned_not_promoted） | high_risk（不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 |
| B | descriptive_death_content | 文献性/案例性转录、死亡相邻但无精确生死判定、否定或避免语境、吉向寿元断语、语义不明但无法可靠排除的记录 | promote_as_high_risk_signal（保留证据链但改标） | high_risk | high_risk_signal | 仅作高风险信号，带强制限制，不作普通推理结论 |
| C | ordinary_no_death_content | 结构术语误报、纯否定语境、伤害类型描述且无死亡含义 | keep_ordinary（保持不变，记录排除理由） | ordinary（不变） | 原 family（不变） | 是（维持） |

B 类强制限制语（含 不得/不输出/精确 门禁标记）：「仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。」

## 3. 分类计数

- A（reject_not_promoted）：**59**
- B（promote_as_high_risk_signal）：**26**
- C（keep_ordinary）：**3**
- 合计：**88**（59 + 26 + 3，精确相加，无遗漏项）

## 4. 分层与专项名单

### 4.1 原 50 条与 88 条的交集

任务书原始 50 条的 ID 清单未随任务提供，无法逐条比对。以最接近的可复现口径（L1 严格词，47 条）作交集代理：L1 全部 47 条均在 88 条集合内，无一条被放行 ordinary（47 条中 A=37、B=9、C=1，唯一 C 为 0446 否定语境）。

### 4.2 L1(47) → L2(68) 新增 21 条

`0068 0139 0146 0180 0181 0299 0320 0425 0453 0483 0505 0557 0607 0609 0621 0643 0656 0658 0715 0844 0923`

### 4.3 L2(68) → L3(88) 新增 20 条

`0115 0202 0205 0229 0240 0304 0471 0475 0484 0504 0531 0539 0571 0586 0600 0620 0635 0758 0790 0930`

新增原因：旧复合词口径未覆盖「早亡/凶亡/必死/先亡/送终/丧偶/死别/夭壽/寿短/母死/夫亡」等断语模式；确定性分类器补齐后捕获。其中 0484（此运必死人）、0504（丈夫必死）、0531（父母早亡）、0205（夭壽）、0930（凶亡）为明确普通级死亡断语，必须治理。

### 4.4 仅限制语命中的 38 条（L2 口径）及其最终类别

- A（23）：`0086 0101 0124 0197 0199 0201 0203 0261 0303 0307 0314 0315 0316 0320 0329 0342 0512 0557 0584 0606 0751 0817 0907`
- B（15）：`0068 0139 0146 0299 0331 0332 0426 0428 0439 0453 0613 0643 0658 0715 0844`

说明：按分类器复核，38 条中多数在含义字段即可被更宽断语模式命中（如 0086「父死」、0329「早亡」）；纯限制语命中（含义无死亡内容）者为 0428、0439、0453、0715、0844 等，均因限制语自承来源含死亡断语而保守处置 B。

### 4.5 真正死亡/寿命内容

85 条（A 59 + B 26）。剩余 3 条（0425、0446、0539）经显式语义裁定无死亡含义，维持 ordinary 并记录排除理由。

### 4.6 术语误报

- 集合内：0425（「衰病死」为十二长生阶段名→C）；0607（「死神」为神煞名、「衰病死」为长生阶段名，但因同句含血光、自作凶等伤害意象，仍按 B 保守处置，不按误报放行）。
- 集合外（从未进入 88）：空亡 18 条、亡神 2 条、死绝/死絕 10 条——均为结构术语，分类器不以单字匹配，故未命中。

### 4.7 否定语境

- 0446「冲去主该神离开命主而不主死亡」→ C（死亡仅以否定形式出现，规则为冲的语义，维持 ordinary）。
- 0331「嫁夫不死也敗身家」→ B（死亡以否定条件出现但仍为断语组成部分）。
- 0643「不至于早夭」→ B（否定语境但「合破应凶」隐含生死凶险）。
- 0240「免血光、產厄」→ B（避免语境的禁忌术语）。

### 4.8 仅来源页面含死亡案例、规则本身无死亡含义的记录

0439、0453、0758、0790 四条：规则本身分别为库门开合、七杀/偏官归类、婚变标志、从格判断，均无死亡含义；但限制语自承来源页/原书含死亡断语，候选与来源死亡内容无法可靠切割，按「无法可靠判定不自行放行」原则保守处置 B（high_risk_signal，非 ordinary，非拒绝）。

## 5. 显式语义裁定（0425 / 0446 / 0607 / 0332）

- **0425 → C（keep_ordinary）**：含义为十二长生各阶段的修持提示（临官/帝旺/衰病死/墓库/绝/胎养），「衰病死」是长生十二宫阶段名连读，属结构术语；无任何死亡、寿命、夭亡断语；限制语亦未自承死亡内容。排除理由：结构术语误报。
- **0446 → C（keep_ordinary）**：含义论述「冲」的语义规则，唯一死亡词出现于「冲去主该神离开命主而**不主**死亡」——明确否定语境；规则本身无死亡、寿命内容。排除理由：否定语境，死亡被显式排除在规则结论之外。
- **0607 → B（promote_as_high_risk_signal）**：含义中「带死神绝衰病死」确为神煞名（死神）与长生阶段名（衰病死）连读，单看此句属术语；但同条口诀另含「逢刑冲破害见血光」「若非犯法自作凶」等伤害/自伤意象，限制语亦自承「含自寻短见与血光之类字眼」。整体无法可靠排除死亡/自伤相邻内容，保守处置 B，不放行 ordinary。
- **0332 → B（promote_as_high_risk_signal）**：含义为民俗禁忌转录（犯此关者子难求、勿入斋坛、休入丧孝家），「喪孝」指向他人丧事场合而非对自身生死的判定，无寿命/死期/死亡关口内容；但死亡域语义（丧孝、源文「不幸者死亡」）在场，按描述性转录处置 B，带强制限制。

## 6. 旧知识与六爻保护

- 旧候选 54 条、旧证据 111 条：分类器复核仅在 high_risk/sensitive 级记录上命中（含两处书名《寿终取象》的良性字符串命中），ordinary 旧记录零命中；旧记录全部保持字节不变，新校验仅约束 ordinary 级，不触及 sensitive/high_risk 旧记录。
- 六爻文件（`src/mingli_engine/liuyao/**`、`data/liuyao/**`、`specs/_drafts/020-liuyao-najia-engine/**`）不参与本整改。

## 7. 后续步骤

1. 按本表实现独立证据内容风险分类器与确定性推广门禁（TDD，先失败测试）。
2. 受治理重建：A 类 59 条转为 rejected/learned_not_promoted 并移除对应证据；B 类 26 条改标 high_risk + high_risk_signal + 强制限制语；C 类 3 条保持不变；同步重建 promotion batch、curation batch、学习记录、文件终态。
3. 重建前后比对旧记录 ID/内容/哈希集合；全量验证后重跑 Task 8 regression 与 final audit。

## 8. 逐条处置表（88 条，A=59 / B=26 / C=3）
| candidate_id | 命中字段 | 命中关键词 | 语境 | evidence_risk_class | promotion_action | 最终 risk_tier | 最终 rule_family | 是否允许进入报告 | 强制限制语 | 判定理由 |
|---|---|---|---|---|---|---|---|---|---|---|
| `candidate_batch_20260714_0001` | 含义 | 死亡关口 | 通过排命宫、大限、小限、月限，结合十二流年神煞，可预测死亡关口等信息。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 方法主张「可预测死亡关口」，属可操作的生死关口推算方法 |
| `candidate_batch_20260714_0002` | 含义 | 死亡关口 | 空亡组合是判断死亡关口的重要条件之一。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「空亡组合是判断死亡关口的重要条件」，死亡关口判定条件 |
| `candidate_batch_20260714_0006` | 含义 | 死亡 | 作者据此推断，命主在该柱对应限运内可能遭遇重大灾咎，包括疾病、死亡或破财等。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 限运内推断结局显含死亡，属生死应期推断 |
| `candidate_batch_20260714_0007` | 含义 | 死亡（描述框架） | 文本认为，在此情形下命主在该限运内可能应凶，案例包括意外死亡、自杀等。 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 预测落点为一般「应凶」，死亡/自杀仅作案例列举 |
| `candidate_batch_20260714_0058` | 含义 | 十有七亡 | 書稱「十有七亡」。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「十有七亡」死亡率断语 |
| `candidate_batch_20260714_0062` | 含义 | 早死 | 書稱「早死無生」。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「早死无生」死亡断语 |
| `candidate_batch_20260714_0068` | 含义 | 早傷 | 書稱「骨肉早傷」。 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「骨肉早傷」为伤亡相邻表述，无死亡判定 |
| `candidate_batch_20260714_0086` | 含义 | 父死 | 書稱「父死他鄉」。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「父死他鄉」条件→死亡断语 |
| `candidate_batch_20260714_0101` | 含义 | 壽短 | 父壽短；若在地支逢刑尅則母壽短（頁面並列『干父壽短／支刑尅母壽短』） | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「父壽短／母壽短」寿命长短断语 |
| `candidate_batch_20260714_0115` | 含义 | 母死 | 生母無緣，刑冲母死 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「刑冲母死」死亡断语 |
| `candidate_batch_20260714_0124` | 含义 | 凶亡 | 夫妻一方凶亡 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「夫妻一方凶亡」死亡断语 |
| `candidate_batch_20260714_0126` | 含义 | 夭亡 | 子緣薄；若干支皆傷則兒女夭亡 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「干支皆傷則兒女夭亡」条件→夭亡断语 |
| `candidate_batch_20260714_0131` | 含义 | 夭亡 | （夭亡）見印解亦貧苦 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 以「夭亡」格局为前提的断语 |
| `candidate_batch_20260714_0139` | 限制语 | 死亡域词+描述框架 | 原文斷語「末歲損成家之子」，並附「多修多改運，不修照原來」之化解式表述。 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「末歲損成家之子」为伤亡相邻表述，语义不确指死亡 |
| `candidate_batch_20260714_0146` | 限制语 | 死亡域词+描述框架 | 原文分別斷「父母不完全」「兄弟不全」「妻妾不全」「子息愚頑」，為傷官居四柱之六親類比。 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「父母不完全」等六亲不全表述，死亡语义不明 |
| `candidate_batch_20260714_0180` | 含义 | 夭折 | Traditional verse pairs these respectively with… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「早年夭折」配置断语 |
| `candidate_batch_20260714_0181` | 含义 | 亡身 | Traditional verse pairs these respectively with… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「因色亡身」死亡断语 |
| `candidate_batch_20260714_0197` | 含义 | 父死 | 斷語稱公亡外鄉、父死外；所列日時生者主因孝病中成親 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「公亡外鄉、父死外」死亡断语 |
| `candidate_batch_20260714_0199` | 含义 | 壽不長 | 依次斷為富貴雙全、兄弟壽不長、老敗淒涼 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「兄弟壽不長」寿命断语 |
| `candidate_batch_20260714_0200` | 含义 | 夭亡 | 依口訣對應斷語：四甲少妻子、四乙命早亡、四丙子息空、四丁壽命長、四戊人孤刑、四己人忠良、四庚他… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「命早亡／壽命長／夭亡」寿命生死断语 |
| `candidate_batch_20260714_0201` | 含义 | 早亡 | 口訣稱父母早亡、雙亡、不全（母損或父損）或無靠 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「父母早亡、雙亡」死亡断语 |
| `candidate_batch_20260714_0202` | 含义 | 長壽 | 口訣稱父母長壽賢貴、椿萱並茂；偏財遇劫財則稱父必風流 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「父母長壽賢貴」吉向寿元断语，寿命类内容保守标高风险 |
| `candidate_batch_20260714_0203` | 含义 | 早亡 | 口訣稱父早亡、死不歸或喪他鄉；相對地偏財歸祿則稱父必崢嶸 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「父早亡、死不歸」死亡断语 |
| `candidate_batch_20260714_0205` | 含义 | 夭壽 | 口訣分別稱孤寡、內亂外重、醜惡貪悖、滾浪桃花（尅子）、妨夫破家、寡賤、血厄、淫濫、貪妒兇頑、產… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「產厄或夭壽」寿夭断语 |
| `candidate_batch_20260714_0229` | 含义 | 死別 | 傳統斷語稱「月干比劫同胞多；坐空亡則死別或不得力」，屬未驗證之條件式主張。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「坐空亡則死別」死別断语 |
| `candidate_batch_20260714_0240` | 含义+限制语 | 死亡域词+描述框架 | 傳統口訣斷貞潔，原文並括註免血光、產厄。 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「免血光、產厄」以避免语境出现的禁忌术语 |
| `candidate_batch_20260714_0260` | 含义 | 死亡 | 第147页歌诀直书“做盜賊死亡” | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「做盜賊死亡」死亡断语 |
| `candidate_batch_20260714_0261` | 含义 | 而死 | 第147页歌诀称“投江而死” | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「投江而死」死亡断语 |
| `candidate_batch_20260714_0268` | 含义 | 夭亡 | 歌诀称“無兄弟或過養他家”，甚者“兄弟夭亡或生離” | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「兄弟夭亡」夭亡断语 |
| `candidate_batch_20260714_0299` | 含义 | 長壽 | 原文列出月份與日干之天德貴人對應，並以長壽、世世長年為斷語。 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「長壽、世世長年」吉向寿元断语，寿命类内容保守标高风险 |
| `candidate_batch_20260714_0303` | 含义 | 必死 | 源文稱男命結妻必死、女命結夫必亡；另稱女命無官無食無印一生無夫（p.209）、男命無財無官無印… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「結妻必死、結夫必亡」绝对化死亡断语 |
| `candidate_batch_20260714_0304` | 含义 | 送終 | 源文稱此類配置與膝下無子、生子不賢榮、有子分西東、有子難送終相關；又稱四柱無比手足虛微、月逢傷… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「有子難送終」死亡境遇断语 |
| `candidate_batch_20260714_0307` | 含义 | 壽有損 | 源文稱日運年成三合局必有紅鸞之喜；命無財祿而財祿逢旺相定當衆聚發；身主冲破則不離祖而漂流他鄉；… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「父壽有損、母年早喪」寿夭断语 |
| `candidate_batch_20260714_0314` | 含义 | 非夭 | 源文斷語：非夭則貧。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「非夭則貧」夭亡断语 |
| `candidate_batch_20260714_0315` | 含义 | 非夭 | 源文斷語：非夭則貧。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「非夭則貧」夭亡断语 |
| `candidate_batch_20260714_0316` | 含义 | 早亡 | 源文斷語：論命早亡。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「論命早亡」死亡断语 |
| `candidate_batch_20260714_0320` | 含义 | 尅雙親 | 源文斷語：早尅雙親。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「早尅雙親」亲属伤亡断语（保守） |
| `candidate_batch_20260714_0329` | 含义 | 早亡 | 源文同繫於母年早喪或母早亡。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「母年早喪或母早亡」死亡断语 |
| `candidate_batch_20260714_0331` | 限制语 | 死亡域词+描述框架 | 原文稱為女破骨，謂主破男家、嫁夫不死也敗身家 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「嫁夫不死也敗身家」死亡以否定条件出现 |
| `candidate_batch_20260714_0332` | 含义 | 喪孝 | 原文稱犯此關者子難求，囑勿入齋壇、休入喪孝家，謂如不注意則災疾難免 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 民俗禁忌转录（勿入喪孝家），无对自身生死的判定 |
| `candidate_batch_20260714_0333` | 含义 | 死亡 | 原文稱若逢此殺必主死亡，並引書云辰戌為羅網，人命逢之主尅陷淹滯之疾、或受牢獄之災 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「若逢此殺必主死亡」死亡断语 |
| `candidate_batch_20260714_0341` | 含义 | 死別 | 歌訣稱『非生離終須死別』，屬分離與死亡的描述性斷語 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「非生離終須死別」死別断语 |
| `candidate_batch_20260714_0342` | 含义 | 喪偶 | 歌訣稱『使夫星久入黃泉』，即夫星入墓主喪偶之象的描述 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「夫星久入黃泉」主丧偶死亡断语 |
| `candidate_batch_20260714_0425` | — | — | 该书为各阶段配修持提示：临官防得意忘形、帝旺防盛极而衰、衰病死当乐天知命、墓库冲开则发、绝处可… | C | keep_ordinary | ordinary（不变） | 原 rule_family（不变） | 是（维持） | —（维持原限制语，记录排除理由） | 「衰病死」为十二长生阶段名，结构术语误报 |
| `candidate_batch_20260714_0426` | 含义 | 生命垂危 | 源文断语为：大运流年与禄神冲克“有凶讯，小则破财，大则严重病灾不免”；禄神冲破轻者耗财消灾、重… | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「生命垂危」死亡相邻结局，无精确生死判定 |
| `candidate_batch_20260714_0428` | 限制语 | 死亡域词+描述框架 | 源页以歌谣体逐干逐运给出吉凶断语，如甲木日元“甲运比肩百事强”“乙运劫财运逢衰”，并依次覆盖乙… | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 行运歌谣汇编，限制语自承含死亡相邻意象，保守高风险 |
| `candidate_batch_20260714_0439` | 限制语 | 死亡域词+描述框架 | 按作者体系，刑冲即开库门之意；库空则开门收外物，库满则开门放出库中物，是收是放须先判库中有无东… | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 规则本身为库门开合机制；限制语自承源页命例含死亡断语，保守高风险 |
| `candidate_batch_20260714_0446` | — | — | 作为候选规则：书称冲破主大凶、冲凶岁运生相应凶事、冲旺喜神吉而冲旺忌神凶、冲去主该神离开命主而… | C | keep_ordinary | ordinary（不变） | 原 rule_family（不变） | 是（维持） | —（维持原限制语，记录排除理由） | 「不主死亡」为否定语境，规则本身无死亡含义 |
| `candidate_batch_20260714_0453` | 限制语 | 死亡域词+描述框架 | 按该书作者立场归为七杀而非偏官，并主张论命优先安顿七杀；有制化则改按偏官。 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 规则为七杀/偏官归类；限制语自承源页含凶死描述，保守高风险 |
| `candidate_batch_20260714_0465` | 含义 | 凶死 | 文本谓七杀专主攻身，无制而身旺硬扛者一般不得善终、凶死于突发之灾，身弱气虚者一般主慢性恶疾或很… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 按干支阴阳分层的凶死规则体系 |
| `candidate_batch_20260714_0471` | 含义 | 早夭 | 依次判为：祖上社会地位比较高甚至有当官之人、经济条件也蛮好；祖上长辈中会有伤残之人甚至有早夭之… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「祖上长辈中有早夭之人」条件→夭亡判定 |
| `candidate_batch_20260714_0475` | 含义 | 死别 | 依次判为：配偶能力强、有社会地位、财运也好；能力差、地位不高；配偶不顺之象；能力还是不错、有一… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「婚姻不顺」定义枚举含生离死别 |
| `candidate_batch_20260714_0483` | 含义 | 大关口 | 文中称相应阶段'十有九凶'：早年运刑冲年月柱则自己不降灾便长辈遭难，中年运冲日柱主该运不好，晚… | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「大关口／遭难」灾厄应期，生死语义不明，保守高风险 |
| `candidate_batch_20260714_0484` | 含义 | 必死 | 文中分别断为：与年柱同主父母凶、此运必死人；与月柱同主婚姻不顺、兄弟不和或姐妹有灾；与日柱同主… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「此运必死人」死亡断语 |
| `candidate_batch_20260714_0496` | 含义 | 死亡（描述框架） | 文本主张此为配偶易见疾病、离异或死亡的风险标记。 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「风险标记」框架下的一般死亡风险，无应期 |
| `candidate_batch_20260714_0501` | 含义 | 克死 | 文本称可直断为二次婚姻之兆，年日伏吟夫宫再逢冲者并称克死丈夫后再嫁。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「克死丈夫后再嫁」死亡断语 |
| `candidate_batch_20260714_0504` | 含义 | 必死 | 书中称克夫、夫亡或离婚；对只有官或杀且带官墓者称又到大运流年官星入墓则丈夫必死，并自注准确率9… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「官星入墓則丈夫必死」死亡断语 |
| `candidate_batch_20260714_0505` | 含义 | 横死 | 书中称克夫再嫁；坐支伤官带羊刃者称夫遭横死，特别是命中无财的人，并称财星上来可以化解、无财无法化解。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「夫遭横死」死亡断语 |
| `candidate_batch_20260714_0508` | 含义 | 死亡 | 书中称必离婚或配偶死亡。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「必离婚或配偶死亡」绝对化死亡断语 |
| `candidate_batch_20260714_0512` | 含义 | 则死 | 书中称婚姻不顺、有婚灾、男受女人的气、女受男人的气、争吵不休，不分则离、不离则死，并配一八水土… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「不离则死」死亡断语 |
| `candidate_batch_20260714_0531` | 含义 | 早亡 | 对应断语为父母早亡、离异、过继、随母改嫁、娶妻之年父亡等，作者对部分条文附现代软化解释。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「父母早亡／娶妻之年父亡」死亡断语 |
| `candidate_batch_20260714_0539` | — | — | 页面称金木相战多筋骨之伤, 木土相战多皮肉之伤, 水火相战多烧烫血光, 金火相战多血疾苍毒 | C | keep_ordinary | ordinary（不变） | 原 rule_family（不变） | 是（维持） | —（维持原限制语，记录排除理由） | 「血光」为烧烫伤害类型描述，限制语明确不构成事故预言，无死亡含义 |
| `candidate_batch_20260714_0557` | 含义 | 先亡 | 页面将前列条件断为『母先亡』类信号，将后列条件断为『父先亡』类信号 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「母先亡／父先亡」死亡信号断语 |
| `candidate_batch_20260714_0571` | 限制语 | 死亡域词+描述框架 | 文本称二牛卧槽主婚姻曲折、二虎相争必有一伤；子午冲主身不安并取象心脑血管之类、卯酉冲主伤四肢车… | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 车惊车祸、伤病类断语，无死亡判定，保守高风险 |
| `candidate_batch_20260714_0584` | 含义 | 夭贫 | 断语称主夭贫、难以发越之兆, 可在艺术、九流发展。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「主夭贫」夭亡断语 |
| `candidate_batch_20260714_0586` | 含义 | 丧偶 | 断语称离婚或多婚或丧偶或无配偶。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「丧偶」死亡断语 |
| `candidate_batch_20260714_0600` | 含义 | 死别 | 文本称主该六亲病伤手术、生离死别，亦有结婚、搬迁、离婚、合并等象 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「主该六亲病伤手术、生离死别」死别断语 |
| `candidate_batch_20260714_0606` | 含义 | 早亡 | 口诀断言分别对应先克父、母早亡、妻身逝、夫必伤、兄弟殃、子女伤、祖辈灾患、身有殃、凶祸至等六亲… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「母早亡、妻身逝」六亲死亡断语 |
| `candidate_batch_20260714_0607` | 含义+限制语 | 死亡域词+描述框架 | 口诀逐项断言：藏禄不堪强、只恐六亲靠不住；藏刃喜有偏官做武郎、逢刑冲破害见血光；带冲神离乡背井… | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「死神／衰病死」为神煞与长生术语，但含血光、自作凶等伤害意象，保守高风险 |
| `candidate_batch_20260714_0609` | 含义 | 夭寿 | 口诀断言相应组合主聋哑、失明、四肢眼目破伤、中年后犯刑、伤父母、富贵少寿或夭寿、刑戳之灾等；仅… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「富贵少寿或夭寿」寿夭断语 |
| `candidate_batch_20260714_0613` | 含义+限制语 | 死亡域词+描述框架 | 原文称「偷生命所招，儿女定虚耗」，并注此为看女命克子情况的查法 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「儿女定虚耗」子女损耗断语，死亡语义不明，保守高风险 |
| `candidate_batch_20260714_0620` | 含义 | 送终 | 原文称男子带流路上死、女子带流产后亡，为男女皆忌之一大恶煞，并称与老人去速、子女送终、四柱无财… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「路上死／产后亡／送终」死亡断语 |
| `candidate_batch_20260714_0621` | 含义 | 短命 | 原文称单有此关不为大恶，与将军箭、阎罗关、流霞煞一种或多种配见则立大凶、不论男女皆忌；组合情形… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「组合情形主短命」寿命断语 |
| `candidate_batch_20260714_0635` | 含义+限制语 | 死亡域词+描述框架 | 按该书说法为白虎煞，一般主凶，涉血光、事故、健康等描述性断语，并提示遵纪守法、注意安全。 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 白虎煞涉血光、事故的神煞描述，无死亡判定 |
| `candidate_batch_20260714_0643` | 限制语 | 死亡域词+描述框架 | 书中断为凶命，所幸戊癸合绊不至于早夭，戊癸合被打破时应凶 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「不至于早夭」为否定语境，但「合破应凶」隐含生死凶险，保守高风险 |
| `candidate_batch_20260714_0656` | 含义 | 凶死 | 惟有用印化杀，终身有印绶之运则可以发达；其他的运不但不发达而且多灾，若走食伤运则克泄交加，书中… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「走食伤运則凶死之象」运→凶死应期 |
| `candidate_batch_20260714_0658` | 含义 | 短促 | 阳干食伤太旺者即使走好运也不是富贵命；阴干印旺者行运只有比劫之乡顺母之性为美、其余皆不可行、最… | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 所引断语含「短命／凶死」字样但仅照录，规则本身为行运喜忌 |
| `candidate_batch_20260714_0680` | 含义 | 短命 | 原文称'数量上三个为凶，三个就为多了，超过三个就会出问题'，并涉'食伤被制短命、三枭无比夺财、… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「食伤被制短命、制财短命」寿命断语 |
| `candidate_batch_20260714_0715` | 限制语 | 死亡域词+描述框架 | 書中判為破印之忌，並錄有財以傷之則危之語 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 「財以傷之則危」及寿夭语句仅照录，死亡语义间接 |
| `candidate_batch_20260714_0751` | 含义 | 必克兄弟 | 书中断前十种为无兄弟、有亦离散；戊寅己卯日生人为必克兄弟姐妹；偏官偏印偏才重叠为一定是遮子；正… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「必克兄弟姐妹」亲属伤亡断语（保守） |
| `candidate_batch_20260714_0758` | 限制语 | 死亡域词+描述框架 | 条件性候选：页面主张平衡或用神到位偏结婚标志，失衡加月日支受伤偏婚变标志；财官受伤过重被描述为… | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 规则为婚变标志；限制语自承源文含丧偶字眼，保守高风险 |
| `candidate_batch_20260714_0790` | 限制语 | 死亡域词+描述框架 | 日干无气则从，阴日干易从、阳日干难从；有制神无破为假从，行制神生旺运亦可发；制神被合克或日干生… | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 规则为从格判断；限制语自承原书含凶亡断语，保守高风险 |
| `candidate_batch_20260714_0817` | 含义 | 夫亡 | 据以推算结婚年龄与姻缘长短，如例98推20岁结婚、总计12年姻缘，例89推38年姻缘而'夫亡' | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 推算姻缘长短并以「夫亡」为端点，属生死应期推算 |
| `candidate_batch_20260714_0844` | 限制语 | 死亡域词+描述框架 | 作者称天人地三才到位方可应验，并自注这种暗拱会与格用无关、只能拿来解释发生何事 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 规则为暗拱解释方法；例解含搏虎被噬伤亡叙事，仅作描述 |
| `candidate_batch_20260714_0899` | 含义 | 死亡（描述框架） | 原书以此三层「克夫基因」加大运流年「引爆点」解释案例78丈夫死亡一事，仅作来源描述性记录 | B | promote_as_high_risk_signal | high_risk | high_risk_signal | 仅作高风险信号（带限制，不作普通推理结论） | 仅作传统高风险信号与文化资料描述，不得用于真实个人寿命、死亡时间或医疗判断，不输出精确生死结论。 | 明确案例归因描述（案例78丈夫死亡），带「仅作来源描述性记录」框架 |
| `candidate_batch_20260714_0907` | 含义 | 寿终 | 书中以加总得数断寿终或成婚之岁。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「加总得数断寿终或成婚之岁」寿命/死期换算方法 |
| `candidate_batch_20260714_0923` | 含义 | 寿数 | 书内据此推得具体寿数断语（134例'55+1=55岁亡'；143例'54+8=62岁亡'），均… | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「55+1=55岁亡」寿数→死亡年龄换算 |
| `candidate_batch_20260714_0930` | 含义 | 凶亡 | 喜神转生忌神判不吉，六亲之喜神转生忌神判凶亡；忌神转生喜神判吉。 | A | reject_not_promoted | high_risk（学习记录保留，不推广） | 无报告证据（学习记录 mapping_outcome=high_risk_signal，gate=rejected_safety） | 否 | —（不入库；候选 rejected，附拒绝原因） | 「喜神转生忌神判凶亡」凶亡断语 |
