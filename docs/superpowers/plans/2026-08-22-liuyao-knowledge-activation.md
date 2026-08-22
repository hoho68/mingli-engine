# 六爻知识激活实施计划（021）

**Date**: 2026-08-22
**Branch**: `021-liuyao-knowledge-activation`
**Design**: `docs/superpowers/specs/2026-08-22-liuyao-knowledge-activation-design.md`
**Method**: TDD、小步骤、频繁提交。每个任务先写失败测试，再实现，再跑聚焦测试，通过后立即提交。
**Commit identity**: 仓库无 git 身份配置，所有提交使用
`git -c user.name="iiilxs" -c user.email="iiilxs@qq.com" commit`（不修改任何配置）。

## 环境约定

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
# 聚焦测试
uv run --frozen --with pytest==8.4.1 python -m pytest <paths> -q -p no:cacheprovider
```

## 冻结保护基线（每个任务提交前核对）

```powershell
git diff da96f7451d07aa4edeaac0c9c4a68e7e910735cd -- `
  src/mingli_engine/data/liuyao/liuyao_sources.json `
  src/mingli_engine/data/liuyao/liuyao_candidates.json `
  src/mingli_engine/data/liuyao/liuyao_review_decisions.json `
  src/mingli_engine/data/liuyao/liuyao_promotion_batches.json `
  src/mingli_engine/data/liuyao/liuyao_evidence_units.json `
  src/mingli_engine/data/liuyao/batch_20260714_liuyao_family_map.json
# 必须为空
```

---

## Task 1：证据引用模型与族索引

**Files**:
- Test: `tests/unit/test_liuyao_knowledge_activation.py`（新建）
- Impl: `src/mingli_engine/liuyao/knowledge_activation.py`（新建）

- [x] 1.1 写失败测试：
  - `LiuyaoEvidenceCitation` 字段完整性（evidence_id/rule_family/source_id/页级 source_ref/theme/summary/limitations/confidence）与非法值拒绝（空字段、非页级 source_ref、族外 rule_family）。
  - `build_liuyao_evidence_index` 返回 8 族全覆盖；总量 67；族分布 47/6/5/4/3/2/0/0；族内保持台账顺序。
  - 同一输入两次构建结果相等（确定性）。
- [x] 1.2 实现 `knowledge_activation.py`：引用 dataclass、索引 dataclass、`build_liuyao_evidence_index`（内部先 `validate_liuyao_knowledge_chain`，再 `load_liuyao_evidence_units`，断不变量）。
- [x] 1.3 跑聚焦测试通过；核对冻结保护基线为空；提交 `feat(liuyao): add evidence citation model and family index`。

## Task 2：激活校验摘要

**Files**:
- Test: `tests/unit/test_liuyao_knowledge_activation.py`（追加）
- Impl: `src/mingli_engine/liuyao/knowledge_activation.py`（追加）

- [x] 2.1 写失败测试：`validate_liuyao_evidence_activation()` 返回摘要（总量、族分布、全 ordinary、全 moderate、全页级定位）；损坏副本（tmp_path 删一条证据）抛 `LiuyaoKnowledgeError`。
- [x] 2.2 实现 `validate_liuyao_evidence_activation(data_dir=None)`。
- [x] 2.3 聚焦测试通过；核对基线；提交 `feat(liuyao): add evidence activation validation summary`。

## Task 3：分析层挂载引用

**Files**:
- Test: `tests/unit/test_liuyao_analysis_activation.py`（新建）
- Impl: `src/mingli_engine/liuyao/analysis.py`、`src/mingli_engine/liuyao/knowledge_activation.py`（`citation_from_unit` 转换）、`src/mingli_engine/data/liuyao/analysis_config.json`（增加 `evidence_activated_note`）

- [x] 3.1 写失败测试：
  - 五个有证据族（yong_shen_selection/moving_line_dynamics/six_spirits_attachment/month_day_strength/void_break_state）的观察携带该族全部引用，每条引用五要素齐全；
  - `observations` 文本与八族 `status` 与 V1 完全一致（对固定卦逐字断言）；
  - shi_ying_relation、yingqi_timing、category_judgment 无引用且保留 pending note；
  - 显式传入空索引时全部族无引用（显式降级路径可测试）。
- [x] 3.2 实现：`LiuyaoFamilyObservation.evidence_citations`（默认 `()`）、`analyze_liuyao_chart(..., evidence_index=None)`、配置可选键解析与回退常量。
- [x] 3.3 聚焦测试＋`tests/unit/test_liuyao_analysis.py`＋`tests/unit/test_liuyao_calibration.py` 通过；核对基线；提交 `feat(liuyao): attach governed evidence citations to family analysis`。

## Task 4：报告边界与 Markdown 渲染

**Files**:
- Test: `tests/unit/test_liuyao_report_activation.py`（新建）
- Impl: `src/mingli_engine/liuyao/report.py`、`src/mingli_engine/liuyao/report_markdown.py`

- [x] 4.1 写失败测试：
  - Markdown 对每条引用渲染 `证据引用：…（族，source_id，page:…）：…；限制：…`；
  - 无引用族不出现"证据引用"行；
  - 报告边界检查覆盖引用文本（构造含禁用绝对化措辞的引用时被拒——用伪造 citation 单测 report 层）。
- [x] 4.2 实现渲染与边界组合文本扩展。
- [x] 4.3 聚焦测试＋`tests/unit/test_liuyao_report.py` 通过；核对基线；提交 `feat(liuyao): render evidence citations and extend report boundary`。

## Task 5：端到端与全量回归

**Files**:
- Test: `tests/integration/test_liuyao_knowledge_activation_cli.py`（新建）

- [x] 5.1 写失败测试：`liuyao-report` 对 golden vector 请求输出含证据引用行（含 `liuyao_evidence_batch_20260714_` 与 `page:`），退出码 0。
- [x] 5.2 视需要接线（预期 CLI 无需改动，分析默认激活）。
- [x] 5.3 全量回归：
  ```powershell
  uv run --frozen --with pytest==8.4.1 python -m pytest -q -p no:cacheprovider
  ```
  既有 4 个 task8 分支绑定失败在本分支同样出现（基线 `da96f745` 上即如此，
  属阶段A已裁决的环境绑定，不是本次回归）。
- [x] 5.4 核对冻结保护基线为空；`git diff --check` 无新增告警；提交 `test(liuyao): cover end-to-end knowledge activation`。

## 执行记录（2026-08-22）

- 全部 5 个任务按 TDD 完成；提交链：
  `e044f14` 设计+计划 → `70f37a6` 引用模型与族索引 → `732050c` 激活校验摘要 →
  `399130d` 分析层挂载引用 → `95b1640` 报告渲染与边界 → `2e2e8cf` 端到端测试与打包清单修正。
- 计划外修正（已在 Task 5 全量回归中暴露）：新增模块触发打包治理清单
  `_EXPECTED_PACKAGE_MODULES_SHA256`（`packaging_validation.py`）按设计拒绝未登记模块；
  已按既定算法重算并登记新清单哈希（71 个模块，
  `958cdcf4…de27`），算法经旧哈希反向复算验证。
- 全量回归：2531 passed, 1 skipped；5 个失败全部为 Task 8 冻结环境绑定
  （分支绑定 4 个＋仓库哈希绑定 1 个），在基线 `da96f745` 上同样失败
  （基线为 4 failed＋哈希绑定偶然通过），属阶段A已裁决的冻结检查，非本次回归。
- 冻结台账保护基线为空；`git diff --check` 干净；未推送、未合并。

## 完成判定

- [x] 全部任务提交完成，工作区干净。
- [x] 设计 D5 全部不变量有测试断言且通过。
- [x] 不推送、不合 main；汇报提交清单与测试结果。

## 追加执行记录：事项类别输入与类别证据激活（2026-08-22，第二轮）

- 类别映射严格取自 47 条 category_judgment 已晋升证据：9 个普通类别
  （weather 4 条 / annual_fortune 3 条 / wealth 3 条 / career 2 条 / marriage 1 条 /
  travel 1 条 / lost_items 3 条 / house 1 条 / agriculture 2 条），映射快照锁定在
  `tests/unit/test_liuyao_matter_category.py`；17 个被映射证据单元逐条通过
  既有 high_risk/safety/绝对化措辞边界复核。
- 高风险类别（medical/legal/investment/lifespan）复用 `high_risk.REFUSAL_MESSAGE`
  在分析前拒绝；未知类别返回输入校验错误；缺省保持 V1 `not_computed` 逐字兼容。
- 贯通链路：CLI JSON（可选 `matter_category`）→ `LiuyaoCastRequest` →
  `analyze_liuyao_chart(matter_category=...)` → 报告引用渲染；卦盘 JSON 不变。
- 提交链：`0a72f19` 类别词表/门禁/索引 → `195f897` 请求模型与分析激活 →
  `790544f` CLI 贯通与 020 契约 V1.1 注记 → `a483818` lint 预算内修正。
- 验证：专项 82 项通过；全量（排除 task8_post_audit）2560 passed, 1 skipped,
  0 failed；mypy 六爻+CLI 范围零问题；Ruff 维持基线 13 项既有告警（无新增）；
  `git diff --check` 干净；六个冻结台账相对 `da96f745` 字节不变。
- 未闭环：47 条中 30 条本轮不挂载——坟茔（0020）、从师（0030）、诉讼混合条
  （0035）、疾病/医药/神灵病因条（0018/0019/0051/0056/0057/0058）、婚育寿夭
  混合条（0054）、祭祀禳解条（0021）及通用方法论条（0016/0022-0026/0040/
  0042-0045/0048/0060-0063/0065-0067）；对应事项按未知类别或高风险类别拒绝。
