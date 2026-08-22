# 六爻知识激活设计（021）

**Status**: Approved design baseline
**Date**: 2026-08-22
**Branch**: `021-liuyao-knowledge-activation`
**Base**: 六爻V1冻结提交 `da96f7451d07aa4edeaac0c9c4a68e7e910735cd`
**Depends on**: 六爻V1纳甲引擎（020，已冻结）；八字019能力链（已发布 main，不在本范围改动）

## 目标

将 batch_20260714 治理链晋升的 **67 条六爻正式证据**接入六爻分析与报告链路，
使每条被激活的分析结论携带完整引用：`evidence_id`、`rule_family`、`source_id`、
页级 `source_ref`、`limitations`。替换 V1 的"证据链尚未晋升"占位说明。

## 范围与边界

- 只激活既有 67 条正式证据；**不扩展到新材料学习**，不新增、不修改任何知识台账
  （`liuyao_evidence_units.json` 等五个台账与族映射文件保持字节不变）。
- 不改动八字 013/019 链路、不改动 `data/classical_sources/`、不改动 `data/new_material_learning/`。
- 不改动六爻装卦、起卦、校准口径；校准语料与全部既有断言保持通过。
- 本阶段不推送、不合并到 `main`。

> 2026-08-22 更正：`liuyao_source_batch_20260714_001` 已包含《增删卜易》
> 与《卜筮正宗》。此前“后续新增来源”的表述源于目录识别不足；022 只做既有
> 来源内的定向证据补强，不登记重复来源。

## 既有证据分布（冻结事实）

| rule_family | 条数 | 激活方式 |
|---|---:|---|
| category_judgment | 47 | 仅入索引与校验；V1 无事项类别输入，族保持 `not_computed`，不挂载引用 |
| yong_shen_selection | 6 | 挂载到对应 computed 族 |
| moving_line_dynamics | 5 | 挂载到对应 computed 族 |
| month_day_strength | 4 | 挂载到对应 computed 族 |
| six_spirits_attachment | 3 | 挂载到对应 computed 族 |
| void_break_state | 2 | 挂载到对应 computed 族 |
| shi_ying_relation | 0 | 无证据，族保持 computed 结构观察＋证据待定说明 |
| yingqi_timing | 0 | 无证据，族保持 degraded＋证据待定说明 |

全部 67 条：`risk_tier=ordinary`、`confidence=moderate`、`source_ref` 均为 `page:N` 或
`page:N-M` 页级定位。

## 设计决策

### D1 复用现有加载器，不建第二套台账读取

激活层只调用 `mingli_engine.liuyao.knowledge` 的
`load_liuyao_evidence_units` / `validate_liuyao_knowledge_chain`。
加载失败或链校验失败即抛出 `LiuyaoKnowledgeError`（失败关闭，不静默降级）。

### D2 族索引确定性证据选择层

新模块 `mingli_engine/liuyao/knowledge_activation.py`：

- `build_liuyao_evidence_index(data_dir=None) -> LiuyaoEvidenceIndex`
  - 先运行 `validate_liuyao_knowledge_chain` 做链校验；
  - 按 `LIUYAO_RULE_FAMILIES` 固定顺序建立 族 → 证据元组 的映射；
  - 族内顺序保持台账顺序（晋升顺序，确定性）；
  - 索引构建时断言总量、分布、风险等级与页级定位不变量（见 D5）。
- `LiuyaoEvidenceIndex.family(rule_family) -> tuple[LiuyaoEvidenceUnit, ...]`
  为选择入口；V1 选择口径为"族级全量挂载"（每族最多 6 条），
  触发条件级窄化留作后续工作，不在本阶段引入模糊匹配。

### D3 引用模型与结论携带

- 新值对象 `LiuyaoEvidenceCitation`（frozen dataclass）：
  `evidence_id`、`rule_family`、`source_id`、`source_ref`、`theme`、`summary`、
  `limitations`、`confidence`。由证据单元确定性转换，逐字段校验。
- `LiuyaoFamilyObservation` 增加字段
  `evidence_citations: tuple[LiuyaoEvidenceCitation, ...] = ()`（带默认值，
  既有构造调用与测试不受影响）。

### D4 分析与报告集成（最小侵入）

- `analyze_liuyao_chart(chart, *, config=None, evidence_index=None)`：
  `evidence_index is None` 时经 D2 构建（strict）。五个有证据的 computed 族
  （yong_shen_selection、moving_line_dynamics、six_spirits_attachment、
  month_day_strength、void_break_state）挂载对应族全部引用，`evidence_note` 改用激活说明；
  `observations` 文本与八族 `status` **完全不变**（校准断言只读这两处）。
- 无证据族（shi_ying_relation、yingqi_timing）与 `not_computed` 的
  category_judgment 保持现有 `evidence_pending_note`。
- `analysis_config.json` 增加可选键 `evidence_activated_note`
  （schema 版本不变，缺省回退到模块常量）。
- `build_liuyao_report` 的边界检查组合文本纳入引用的 summary 与 limitations
  （纵深防御；证据本身已在晋升时过门禁）。
- `render_liuyao_markdown` 在每条族观察的证据说明后渲染确定性引用行：
  `证据引用：{evidence_id}（{rule_family}，{source_id}，{source_ref}）：{summary}；限制：…`。

### D5 激活不变量（测试断言）

- 索引总量 67；族分布精确等于上表；全部 ordinary/moderate；全部页级 source_ref。
- 每个 computed 且有证据的族：引用数等于该族证据数；每条引用字段完整。
- 重复调用结果逐字节一致（确定性）。
- 证据台账字节不变（激活前后 SHA-256 一致）。

## 错误与恢复

- 台账缺失/损坏/链校验失败 → `LiuyaoKnowledgeError`，CLI 现有
  `_liuyao_error` 路径报错退出，不产出半激活报告。
- 配置缺少 `evidence_activated_note` → 回退模块常量，不报错。

## 验收标准

- 67 条证据全部进入索引并通过链校验；族分布与冻结事实一致。
- 五个有证据的 computed 族的报告输出携带完整五要素引用。
- 既有六爻测试、校准一致性、全量测试套件全部通过。
- 五个知识台账与族映射文件 SHA-256 与 `da96f745` 一致。
