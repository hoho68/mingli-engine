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

- [ ] 1.1 写失败测试：
  - `LiuyaoEvidenceCitation` 字段完整性（evidence_id/rule_family/source_id/页级 source_ref/theme/summary/limitations/confidence）与非法值拒绝（空字段、非页级 source_ref、族外 rule_family）。
  - `build_liuyao_evidence_index` 返回 8 族全覆盖；总量 67；族分布 47/6/5/4/3/2/0/0；族内保持台账顺序。
  - 同一输入两次构建结果相等（确定性）。
- [ ] 1.2 实现 `knowledge_activation.py`：引用 dataclass、索引 dataclass、`build_liuyao_evidence_index`（内部先 `validate_liuyao_knowledge_chain`，再 `load_liuyao_evidence_units`，断不变量）。
- [ ] 1.3 跑聚焦测试通过；核对冻结保护基线为空；提交 `feat(liuyao): add evidence citation model and family index`。

## Task 2：激活校验摘要

**Files**:
- Test: `tests/unit/test_liuyao_knowledge_activation.py`（追加）
- Impl: `src/mingli_engine/liuyao/knowledge_activation.py`（追加）

- [ ] 2.1 写失败测试：`validate_liuyao_evidence_activation()` 返回摘要（总量、族分布、全 ordinary、全 moderate、全页级定位）；损坏副本（tmp_path 删一条证据）抛 `LiuyaoKnowledgeError`。
- [ ] 2.2 实现 `validate_liuyao_evidence_activation(data_dir=None)`。
- [ ] 2.3 聚焦测试通过；核对基线；提交 `feat(liuyao): add evidence activation validation summary`。

## Task 3：分析层挂载引用

**Files**:
- Test: `tests/unit/test_liuyao_analysis_activation.py`（新建）
- Impl: `src/mingli_engine/liuyao/analysis.py`、`src/mingli_engine/liuyao/knowledge_activation.py`（`citation_from_unit` 转换）、`src/mingli_engine/data/liuyao/analysis_config.json`（增加 `evidence_activated_note`）

- [ ] 3.1 写失败测试：
  - 五个有证据族（yong_shen_selection/moving_line_dynamics/six_spirits_attachment/month_day_strength/void_break_state）的观察携带该族全部引用，每条引用五要素齐全；
  - `observations` 文本与八族 `status` 与 V1 完全一致（对固定卦逐字断言）；
  - shi_ying_relation、yingqi_timing、category_judgment 无引用且保留 pending note；
  - 显式传入空索引时全部族无引用（显式降级路径可测试）。
- [ ] 3.2 实现：`LiuyaoFamilyObservation.evidence_citations`（默认 `()`）、`analyze_liuyao_chart(..., evidence_index=None)`、配置可选键解析与回退常量。
- [ ] 3.3 聚焦测试＋`tests/unit/test_liuyao_analysis.py`＋`tests/unit/test_liuyao_calibration.py` 通过；核对基线；提交 `feat(liuyao): attach governed evidence citations to family analysis`。

## Task 4：报告边界与 Markdown 渲染

**Files**:
- Test: `tests/unit/test_liuyao_report_activation.py`（新建）
- Impl: `src/mingli_engine/liuyao/report.py`、`src/mingli_engine/liuyao/report_markdown.py`

- [ ] 4.1 写失败测试：
  - Markdown 对每条引用渲染 `证据引用：…（族，source_id，page:…）：…；限制：…`；
  - 无引用族不出现"证据引用"行；
  - 报告边界检查覆盖引用文本（构造含禁用绝对化措辞的引用时被拒——用伪造 citation 单测 report 层）。
- [ ] 4.2 实现渲染与边界组合文本扩展。
- [ ] 4.3 聚焦测试＋`tests/unit/test_liuyao_report.py` 通过；核对基线；提交 `feat(liuyao): render evidence citations and extend report boundary`。

## Task 5：端到端与全量回归

**Files**:
- Test: `tests/integration/test_liuyao_knowledge_activation_cli.py`（新建）

- [ ] 5.1 写失败测试：`liuyao-report` 对 golden vector 请求输出含证据引用行（含 `liuyao_evidence_batch_20260714_` 与 `page:`），退出码 0。
- [ ] 5.2 视需要接线（预期 CLI 无需改动，分析默认激活）。
- [ ] 5.3 全量回归：
  ```powershell
  uv run --frozen --with pytest==8.4.1 python -m pytest -q -p no:cacheprovider
  ```
  既有 4 个 task8 分支绑定失败在本分支同样出现（基线 `da96f745` 上即如此，
  属阶段A已裁决的环境绑定，不是本次回归）。
- [ ] 5.4 核对冻结保护基线为空；`git diff --check` 无新增告警；提交 `test(liuyao): cover end-to-end knowledge activation`。

## 完成判定

- [ ] 全部任务提交完成，工作区干净。
- [ ] 设计 D5 全部不变量有测试断言且通过。
- [ ] 不推送、不合 main；汇报提交清单与测试结果。
