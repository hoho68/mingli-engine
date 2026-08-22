# Liuyao Classics Targeted Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不新增来源、不修改六爻推理接口和状态的前提下，把《增删卜易》《卜筮正宗》7 条精确页级规则追加到六爻治理链，使正式证据由 70 条增加到 77 条。

**Architecture:** 以现有 `liuyao_source_batch_20260714_001` 为唯一来源身份，新增一个经过清洗的定向复核台账；晋升器只读取台账中 `promote` 的 7 条记录，复用现有安全、查重、链校验和五台账回滚机制，连续追加候选 0071-0077、评审、晋升批次和证据。知识激活层仍按既有规则族读取证据，只更新冻结总量与引用计数；分析函数、CLI 请求/响应、装卦算法、观察文本和 `yingqi_timing == degraded` 均保持不变。

**Tech Stack:** Python 3.12、dataclasses/JSON、现有 `mingli_engine.liuyao` 知识治理模块、pytest 8.4.1、mypy 1.17.1、Ruff 0.12.11、PowerShell、Git。

---

## 执行上下文与不可变边界

- 工作树：`C:\Users\mail\AppData\Local\Temp\opencode\mingli-022-liuyao-classics-evidence`
- 分支：`codex/022-liuyao-classics-targeted-evidence`
- 主分支基线：`c391ad88d91cbd634e8392026fa705c3cfd6586a`
- 已批准设计：`docs/superpowers/specs/2026-08-22-liuyao-classics-targeted-evidence-design.md`
- 提交身份不写入 Git 配置；每个任务末尾都给出包含固定身份和精确提交信息的命令。

每个任务开始前：

```powershell
Set-Location 'C:\Users\mail\AppData\Local\Temp\opencode\mingli-022-liuyao-classics-evidence'
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
git status --short --branch
```

硬性不变量：

1. 不新增或修改 `liuyao_sources.json` 中的来源记录；source 仍为 2 条。
2. 不改 batch_20260714 manifest、file results、validated outputs、原始 learning records 或 family map。
3. 现有前 70 条 candidate/review/evidence 的字段、顺序、ID 保持不变；新记录只加在尾部。
4. 不改任何公开函数签名、CLI JSON 契约、八个族的状态逻辑或装卦算法。
5. `yingqi_timing.status` 必须继续为 `degraded`，不计算日期，不给确定性应期。
6. 不晋升医疗、法律、投资、寿命生死、仪式化解等高风险或现实行动规则。
7. 用户提供文件的绝对路径和二进制哈希不得进入运行时源码、知识台账或报告。
8. 新增证据总数固定为 7；若任一条无法通过原页复核、安全门禁或签名查重，停止任务并报告，不以其他内容凑数。

## 计划前置审计结论

本计划已经先完成设计 D5 所要求的“复用既有记录”检查：source 001 目标页附近的
`旬空判定`、`生旺墓绝`、`进退神判定`、`月破判断`、`伏神取舍`、`两现取舍`
等粗粒度 learning records 已在现有 70 条正式证据中，不能再次晋升。PDF p477-526
在旧 learning ledger 中没有页段记录，因此只对批准页段做了本地文本提取与原页视觉
复核，没有调用新的外部提取模型。下列 7 条是“现有摘要未覆盖、原页能直接支持、
可安全收窄”的精确页级增量；其他页段全部进入 duplicate/support/conflict 状态，不为
增加数量而重述旧证据。

## 已裁定的 7 条新增证据

| review record | 典籍与 PDF 页 | rule_family | 安全化摘要 |
|---|---|---|---|
| `liuyao_classics_review_20260822_0001` | 《增删卜易》p28 | `yong_shen_selection` | 确定事项用神后，生用神者为原神，克用神者为忌神，克制原神并生助忌神者为仇神；仍须结合各爻旺衰与动静。 |
| `liuyao_classics_review_20260822_0002` | 《增删卜易》p71 | `yingqi_timing` | 应期观察综合静动、旺衰、墓绝、冲合、月破、旬空及其解除条件；只保留候选信号，不直接给出日期。 |
| `liuyao_classics_review_20260822_0003` | 《卜筮正宗》p332 | `shi_ying_relation` | 涉及自身与他人时，世爻表自身、应爻表对方；具体关系人仍按题意选相应六亲为用神，不能把所有他人一概只看应爻。 |
| `liuyao_classics_review_20260822_0004` | 《卜筮正宗》p333 | `yong_shen_selection` | 原神、忌神是否实际起作用必须结合用神显伏旺衰、空破、日冲、墓绝、化退及仇神克制等条件。 |
| `liuyao_classics_review_20260822_0005` | 《卜筮正宗》p493 | `yingqi_timing` | 旬空区分受支持而暂待条件的空与无生受克的真空；仅前者可作为后续可能起作用的候选信号。 |
| `liuyao_classics_review_20260822_0006` | 《卜筮正宗》p498 | `yingqi_timing` | 月破爻若发动且获生扶，可把出破、填实、合破作为后续候选条件；安静且受克无生者不据此生成时点。 |
| `liuyao_classics_review_20260822_0007` | 《卜筮正宗》p501 | `yong_shen_selection` | 用神不现时，伏神须获日月生扶、飞神衰弱或受制，且自身不陷休囚空破墓绝，方可取用。 |

完成后的冻结分布必须是：

```python
EXPECTED_FAMILY_COUNTS = {
    "yong_shen_selection": 9,
    "shi_ying_relation": 3,
    "moving_line_dynamics": 5,
    "six_spirits_attachment": 3,
    "month_day_strength": 4,
    "void_break_state": 2,
    "yingqi_timing": 4,
    "category_judgment": 47,
}
```

无事项类别的默认报告引用总数为 `9 + 3 + 5 + 3 + 4 + 2 + 4 = 30`。

## Task 1：更正来源目录与历史规格

**Files:**

- Create: `docs/classical_sources/liuyao_source_catalog.md`
- Modify: `specs/_drafts/020-liuyao-najia-engine/spec.md`
- Modify: `specs/_drafts/020-liuyao-najia-engine/plan.md`
- Modify: `docs/superpowers/specs/2026-08-22-liuyao-knowledge-activation-design.md`
- Modify: `docs/superpowers/plans/2026-08-22-liuyao-knowledge-activation.md`

- [ ] **Step 1.1：建立 source 001 目录事实**

新目录必须列出以下七部书与 PDF 起始页，不写用户绝对路径：

```text
《增删卜易》 1
《卜筮正宗》 292
《卜筮大全》 529
《易林补遗》 977
《易冒》 1119
《易隐》 1240
《火珠林》 1412
```

同时记录：1517 页一致、提取文本长度 1,682,123、文本 SHA-256
`701FE962C9CC87F7F3E246C299F1FACC0506FBBFFDD35F9353C583ADC00E2DB2`，以及“同内容不同封装，不新增第三来源”的裁决。

- [ ] **Step 1.2：追加历史更正，不抹除既有执行记录**

在四个 020/021 文档的陈旧表述附近追加统一更正：

```markdown
> 2026-08-22 更正：`liuyao_source_batch_20260714_001` 已包含《增删卜易》
> 与《卜筮正宗》。此前“后续新增来源”的表述源于目录识别不足；022 只做既有
> 来源内的定向证据补强，不登记重复来源。
```

- [ ] **Step 1.3：文档核验**

```powershell
rg -n "增删卜易|卜筮正宗|source_batch_20260714_001|不新增第三来源" `
  docs/classical_sources/liuyao_source_catalog.md `
  specs/_drafts/020-liuyao-najia-engine/spec.md `
  specs/_drafts/020-liuyao-najia-engine/plan.md `
  docs/superpowers/specs/2026-08-22-liuyao-knowledge-activation-design.md `
  docs/superpowers/plans/2026-08-22-liuyao-knowledge-activation.md
rg -n "E:\\命理演绎|A9497ADC18B28749436053EF8092940F4D168800B91DB59770EF24ECCEF303A0" `
  docs/classical_sources/liuyao_source_catalog.md
git diff --check
```

预期：第一条能定位全部更正；第二条零命中；`git diff --check` 退出码 0。

- [ ] **Step 1.4：提交**

```powershell
git add docs/classical_sources/liuyao_source_catalog.md `
  specs/_drafts/020-liuyao-najia-engine/spec.md `
  specs/_drafts/020-liuyao-najia-engine/plan.md `
  docs/superpowers/specs/2026-08-22-liuyao-knowledge-activation-design.md `
  docs/superpowers/plans/2026-08-22-liuyao-knowledge-activation.md
git diff --cached --check
git -c user.name="iiilxs" -c user.email="iiilxs@qq.com" commit `
  -m "docs(liuyao): correct classical source coverage"
```

## Task 2：冻结定向复核台账与完整覆盖状态

**Files:**

- Create: `src/mingli_engine/data/liuyao/liuyao_targeted_classics_reviews.json`
- Create: `tests/unit/test_liuyao_classics_review.py`
- Modify: `src/mingli_engine/liuyao/knowledge.py`

- [ ] **Step 2.1：先写失败测试**

测试导入尚不存在的 `load_liuyao_targeted_classics_reviews`，并断言：

```python
def test_targeted_classics_review_is_complete_and_sanitized() -> None:
    ledger = load_liuyao_targeted_classics_reviews()
    assert ledger.review_id == "liuyao_targeted_classics_review_20260822_001"
    assert ledger.source_id == "liuyao_source_batch_20260714_001"
    assert len(ledger.promotion_records) == 7
    assert tuple(item.record_id for item in ledger.promotion_records) == tuple(
        f"liuyao_classics_review_20260822_{index:04d}"
        for index in range(1, 8)
    )
    assert tuple(item.source_ref for item in ledger.promotion_records) == (
        "page:28", "page:71", "page:332", "page:333",
        "page:493", "page:498", "page:501",
    )
    assert all(item.risk_tier == "ordinary" for item in ledger.promotion_records)
    assert all(item.confidence == "moderate" for item in ledger.promotion_records)
```

再断言台账的 coverage 覆盖以下互不留空的页段与裁决：

```python
EXPECTED_COVERAGE = (
    ("page:27-29", "promote_and_duplicate"),
    ("page:61", "support_only"),
    ("page:65", "duplicate"),
    ("page:69-71", "promote_and_duplicate"),
    ("page:72-81", "duplicate_and_conflict"),
    ("page:133-291", "support_only"),
    ("page:300-310", "duplicate"),
    ("page:332-339", "promote_and_duplicate"),
    ("page:340-344", "conflict_logged"),
    ("page:477-482", "support_only"),
    ("page:483", "duplicate"),
    ("page:484-492", "support_only"),
    ("page:493", "promote"),
    ("page:494-497", "support_only"),
    ("page:498", "promote"),
    ("page:499-500", "support_only"),
    ("page:501", "promote"),
    ("page:502-523", "support_only"),
    ("page:524", "duplicate"),
    ("page:525-526", "support_only"),
)
```

安全和隐私测试还必须确认序列化内容不含 `E:\命理演绎`、用户文件二进制哈希、`必定`、`注定`、`一定会`、`死定`，并确认所有 `promote` 记录的页码均为单页。

运行并看到预期失败：

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_liuyao_classics_review.py -q -p no:cacheprovider
```

预期：因 loader/JSON 尚不存在而失败。

- [ ] **Step 2.2：实现严格的内部复核模型与 loader**

在 `knowledge.py` 增加冻结 dataclass：

```python
@dataclass(frozen=True)
class LiuyaoClassicsReviewRecord:
    record_id: str
    work_title: str
    source_ref: str
    theme: str
    rule_family: str
    risk_tier: str
    confidence: str
    summary: str
    applicability: tuple[str, ...]
    limitations: tuple[str, ...]
    conflict_status: str


@dataclass(frozen=True)
class LiuyaoClassicsCoverageDecision:
    source_ref: str
    disposition: str
    rationale: str
    linked_record_ids: tuple[str, ...]


@dataclass(frozen=True)
class LiuyaoTargetedClassicsReviewLedger:
    schema_version: str
    review_id: str
    source_id: str
    promotion_records: tuple[LiuyaoClassicsReviewRecord, ...]
    coverage: tuple[LiuyaoClassicsCoverageDecision, ...]
```

`load_liuyao_targeted_classics_reviews(path=None)` 必须严格检查根字段、schema version、固定 source 001、记录 ID 唯一、7 条 family 合法、普通风险、moderate confidence、单页定位、非空 applicability/limitations，以及 coverage 链接只指向本台账记录。未知字段和错误类型均抛 `LiuyaoKnowledgeError`。

- [ ] **Step 2.3：建立台账**

台账根结构固定为：

```json
{
  "schema_version": "liuyao-targeted-classics-review-v1",
  "review_id": "liuyao_targeted_classics_review_20260822_001",
  "source_id": "liuyao_source_batch_20260714_001",
  "promotion_records": [],
  "coverage": []
}
```

把本计划“已裁定的 7 条新增证据”逐条写入 `promotion_records`。每条 limitations 至少包含：传统文献边界、不可作现实保证，以及 family 特有边界。三个 `yingqi_timing` 记录必须额外写明“不提供具体日期、不把候选条件当作必然应验”。coverage 使用 Step 2.1 的 20 段；p340-344 的争议只记录观点并存，不晋升为唯一规则。

- [ ] **Step 2.4：通过测试并提交**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_liuyao_classics_review.py -q -p no:cacheprovider
uv run --frozen --with ruff==0.12.11 ruff check `
  src/mingli_engine/liuyao/knowledge.py tests/unit/test_liuyao_classics_review.py
git diff --check
git add src/mingli_engine/data/liuyao/liuyao_targeted_classics_reviews.json `
  src/mingli_engine/liuyao/knowledge.py tests/unit/test_liuyao_classics_review.py
git diff --cached --check
git -c user.name="iiilxs" -c user.email="iiilxs@qq.com" commit `
  -m "data(liuyao): freeze targeted classics review"
```

## Task 3：用 TDD 实现第三批追加晋升

**Files:**

- Modify: `tests/unit/test_liuyao_knowledge.py`
- Modify: `src/mingli_engine/liuyao/knowledge.py`

- [ ] **Step 3.1：扩展测试 staging**

在测试 helper 中把 `liuyao_targeted_classics_reviews.json` 复制到临时 `data_dir`；该文件是只读输入，不纳入五台账回滚写集。

- [ ] **Step 3.2：先写成功路径失败测试**

新增 `TestTargetedClassicsPromotion`：先执行 base promotion 与 gap promotion，保存五台账的前 70 个对象，然后调用尚不存在的：

```python
summary = promote_liuyao_targeted_classics_candidates(
    generated_at="2026-08-22T08:00:00Z",
    data_dir=data_dir,
)
```

断言：

```python
assert summary == {
    "family_counts": {
        "shi_ying_relation": 1,
        "yingqi_timing": 3,
        "yong_shen_selection": 3,
    },
    "generated_at": "2026-08-22T08:00:00Z",
    "promoted_count": 7,
    "promotion_batch_id": "liuyao_promotion_batch_20260822_001",
    "total_evidence_count": 77,
}
assert len(load_liuyao_sources(data_dir)) == 2
assert tuple(load_liuyao_candidates(data_dir)[:70]) == base_candidates
assert tuple(load_liuyao_review_decisions(data_dir)[:70]) == base_reviews
assert tuple(load_liuyao_evidence_units(data_dir)[:70]) == base_units
```

新 ID 必须严格为：

```python
assert tuple(item.candidate_id for item in candidates[70:]) == tuple(
    f"liuyao_candidate_batch_20260714_{index:04d}"
    for index in range(71, 78)
)
assert tuple(item.evidence_id for item in units[70:]) == tuple(
    f"liuyao_evidence_batch_20260714_{index:04d}"
    for index in range(71, 78)
)
```

并逐条断言 source 001、精确单页 `source_ref`、record ID、family、ordinary、moderate、curation batch `liuyao_curation_batch_20260822_002` 与复核台账一致。

- [ ] **Step 3.3：先写防错路径失败测试**

覆盖：

1. 没有 base batch 时拒绝；
2. 有 base 但没有 gap batch 时拒绝，保证执行顺序固定；
3. 第三批重复运行时报 `already applied`；
4. review record 指向未知 source、非法 family、非单页、high risk 时拒绝；
5. review record 与前 70 条内容签名等价时拒绝；
6. 链校验失败时 candidates/reviews/batches/evidence 四个发生写入的台账及 sources 台账全部恢复到调用前字节；
7. 不泄漏 source-only intake path、relative path 或完整文件哈希。

运行并看到导入/函数缺失失败：

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_liuyao_knowledge.py -q -p no:cacheprovider
```

- [ ] **Step 3.4：实现晋升函数**

增加常量：

```python
LIUYAO_CLASSICS_PROMOTION_BATCH_ID = "liuyao_promotion_batch_20260822_001"
LIUYAO_CLASSICS_CURATION_BATCH_ID = "liuyao_curation_batch_20260822_002"
_LIUYAO_CLASSICS_REVIEW_DATE = "2026-08-22"
```

实现 `promote_liuyao_targeted_classics_candidates(*, generated_at, data_dir=None)`，步骤固定：

1. 加载现有 2 sources、70 candidates/reviews/units、2 promotion batches；
2. 要求 base 与 gap batch 存在，第三批不存在；
3. 加载复核台账，要求 source 001 已登记；
4. 对 7 条记录依次执行 family 校验、`_liuyao_gate_candidate`、`rule_candidate_signature` 与已有台账去重；
5. 从当前长度 70 连续生成 0071-0077；
6. 追加 approved review，rationale 明确写“022 定向古籍复核、精确页级定位、条件化收窄、无冲突统一”；
7. 追加 promotion batch，review notes 明确“只补证据，不改变推理接口/状态”；
8. 写入后运行 `validate_liuyao_knowledge_chain`，任意异常恢复五台账原字节。

同时扩展 `validate_liuyao_knowledge_chain`：当 candidate/evidence 的 `batch_record_id` 以 `liuyao_classics_review_` 开头时，必须能在复核台账找到同 ID，且 source、page、family、summary、limitations 与复核记录一致。

- [ ] **Step 3.5：聚焦验证并提交**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_liuyao_classics_review.py `
  tests/unit/test_liuyao_knowledge.py -q -p no:cacheprovider
uv run --frozen --with mypy==1.17.1 python -m mypy `
  src/mingli_engine/liuyao/knowledge.py --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check `
  src/mingli_engine/liuyao/knowledge.py `
  tests/unit/test_liuyao_classics_review.py `
  tests/unit/test_liuyao_knowledge.py
git diff --check
git add src/mingli_engine/liuyao/knowledge.py `
  tests/unit/test_liuyao_classics_review.py tests/unit/test_liuyao_knowledge.py
git diff --cached --check
git -c user.name="iiilxs" -c user.email="iiilxs@qq.com" commit `
  -m "feat(liuyao): add targeted classics promotion"
```

## Task 4：把 7 条证据追加到正式台账

**Files:**

- Modify: `src/mingli_engine/data/liuyao/liuyao_candidates.json`
- Modify: `src/mingli_engine/data/liuyao/liuyao_review_decisions.json`
- Modify: `src/mingli_engine/data/liuyao/liuyao_promotion_batches.json`
- Modify: `src/mingli_engine/data/liuyao/liuyao_evidence_units.json`
- Verify unchanged: `src/mingli_engine/data/liuyao/liuyao_sources.json`
- Verify unchanged: `src/mingli_engine/data/liuyao/batch_20260714_liuyao_family_map.json`

- [ ] **Step 4.1：执行一次正式晋升**

```powershell
@'
from mingli_engine.liuyao.knowledge import (
    promote_liuyao_targeted_classics_candidates,
)

print(
    promote_liuyao_targeted_classics_candidates(
        generated_at="2026-08-22T08:00:00Z",
    )
)
'@ | uv run --frozen python -
```

预期打印固定摘要：7 条、总量 77、family counts 为 yong 3 / shi-ying 1 / yingqi 3。

- [ ] **Step 4.2：验证知识链和追加边界**

```powershell
@'
from collections import Counter
from mingli_engine.liuyao.knowledge import (
    load_liuyao_candidates,
    load_liuyao_evidence_units,
    load_liuyao_promotion_batches,
    load_liuyao_review_decisions,
    load_liuyao_sources,
    validate_liuyao_knowledge_chain,
)

validate_liuyao_knowledge_chain()
assert len(load_liuyao_sources()) == 2
assert len(load_liuyao_candidates()) == 77
assert len(load_liuyao_review_decisions()) == 77
assert len(load_liuyao_promotion_batches()) == 3
units = load_liuyao_evidence_units()
assert len(units) == 77
assert Counter(item.rule_family for item in units) == {
    "yong_shen_selection": 9,
    "shi_ying_relation": 3,
    "moving_line_dynamics": 5,
    "six_spirits_attachment": 3,
    "month_day_strength": 4,
    "void_break_state": 2,
    "yingqi_timing": 4,
    "category_judgment": 47,
}
print("liuyao targeted classics chain: PASS")
'@ | uv run --frozen python -
```

核对纯追加 diff：

```powershell
git diff -- src/mingli_engine/data/liuyao/liuyao_sources.json
git diff -- src/mingli_engine/data/liuyao/batch_20260714_liuyao_family_map.json
git diff -- src/mingli_engine/data/liuyao/liuyao_candidates.json `
  src/mingli_engine/data/liuyao/liuyao_review_decisions.json `
  src/mingli_engine/data/liuyao/liuyao_promotion_batches.json `
  src/mingli_engine/data/liuyao/liuyao_evidence_units.json
```

前两条必须零输出；后四条只能在 JSON 数组尾部新增 7/7/1/7 条，不能出现旧字段变更。

- [ ] **Step 4.3：聚焦测试并提交数据**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_liuyao_classics_review.py `
  tests/unit/test_liuyao_knowledge.py -q -p no:cacheprovider
git diff --check
git add src/mingli_engine/data/liuyao/liuyao_candidates.json `
  src/mingli_engine/data/liuyao/liuyao_review_decisions.json `
  src/mingli_engine/data/liuyao/liuyao_promotion_batches.json `
  src/mingli_engine/data/liuyao/liuyao_evidence_units.json
git diff --cached --check
git -c user.name="iiilxs" -c user.email="iiilxs@qq.com" commit `
  -m "data(liuyao): append targeted classics evidence"
```

## Task 5：激活新增引用，但不改变推理状态与接口

**Files:**

- Modify: `src/mingli_engine/liuyao/knowledge_activation.py`
- Modify: `tests/unit/test_liuyao_knowledge_activation.py`
- Modify: `tests/unit/test_liuyao_analysis_activation.py`
- Modify: `tests/integration/test_liuyao_knowledge_activation_cli.py`

- [ ] **Step 5.1：先更新期望并看到失败**

把两个 unit test 里的 family counts 更新为 77 条冻结分布；把 integration test 的默认报告引用总数从 23 改为 30。加强应期测试：

```python
assert yingqi.status == "degraded"
assert len(yingqi.evidence_citations) == 4
assert {item.source_ref for item in yingqi.evidence_citations} >= {
    "page:71", "page:493", "page:498",
}
assert "用神" in "".join(yingqi.observations)
assert "降级" in "".join(yingqi.observations)
```

加强世应测试：3 条引用中新增 source 001 `page:332`；原有卦盘计算文本与 status 不变。加强用神测试：引用中出现 p28、p333、p501。

先运行：

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_liuyao_knowledge_activation.py `
  tests/unit/test_liuyao_analysis_activation.py `
  tests/integration/test_liuyao_knowledge_activation_cli.py `
  -q -p no:cacheprovider
```

预期：`knowledge_activation._EXPECTED_TOTAL` 仍为 70，测试失败。

- [ ] **Step 5.2：只更新冻结总量和说明**

将 `_EXPECTED_TOTAL = 70` 改为 `_EXPECTED_TOTAL = 77`，模块说明改为“67 base + 3 gap + 7 targeted classics”。不改 `analysis.py` 的任何分支，不改报告渲染和 CLI。

- [ ] **Step 5.3：验证行为兼容与确定性**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_liuyao_knowledge_activation.py `
  tests/unit/test_liuyao_analysis_activation.py `
  tests/unit/test_liuyao_analysis.py `
  tests/unit/test_liuyao_report_activation.py `
  tests/integration/test_liuyao_knowledge_activation_cli.py `
  -q -p no:cacheprovider
```

预期全部通过，并继续满足：同一输入两次报告逐字节一致、八个 status 不变、默认报告只有引用数量/内容变化、无禁用绝对化措辞。

- [ ] **Step 5.4：提交**

```powershell
uv run --frozen --with mypy==1.17.1 python -m mypy `
  src/mingli_engine/liuyao --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check `
  src/mingli_engine/liuyao `
  tests/unit/test_liuyao_classics_review.py `
  tests/unit/test_liuyao_knowledge.py `
  tests/unit/test_liuyao_knowledge_activation.py `
  tests/unit/test_liuyao_analysis_activation.py `
  tests/integration/test_liuyao_knowledge_activation_cli.py
git diff --check
git add src/mingli_engine/liuyao/knowledge_activation.py `
  tests/unit/test_liuyao_knowledge_activation.py `
  tests/unit/test_liuyao_analysis_activation.py `
  tests/integration/test_liuyao_knowledge_activation_cli.py
git diff --cached --check
git -c user.name="iiilxs" -c user.email="iiilxs@qq.com" commit `
  -m "test(liuyao): activate targeted classics citations"
```

## Task 6：完整验证、独立审查与阶段性交付

**Files:**

- Modify: `docs/superpowers/plans/2026-08-22-liuyao-classics-targeted-evidence.md`（仅追加执行记录）

- [ ] **Step 6.1：运行专项、类型和风格门禁**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_liuyao_classics_review.py `
  tests/unit/test_liuyao_knowledge.py `
  tests/unit/test_liuyao_knowledge_activation.py `
  tests/unit/test_liuyao_analysis_activation.py `
  tests/unit/test_liuyao_analysis.py `
  tests/unit/test_liuyao_report_activation.py `
  tests/integration/test_liuyao_knowledge_activation_cli.py `
  -q -p no:cacheprovider
uv run --frozen --with mypy==1.17.1 python -m mypy `
  src/mingli_engine/liuyao --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check `
  src/mingli_engine/liuyao `
  tests/unit/test_liuyao_classics_review.py `
  tests/unit/test_liuyao_knowledge.py `
  tests/unit/test_liuyao_knowledge_activation.py `
  tests/unit/test_liuyao_analysis_activation.py `
  tests/integration/test_liuyao_knowledge_activation_cli.py
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/contract/test_wheel_runtime_assets.py -q -p no:cacheprovider
```

- [ ] **Step 6.2：运行全项目非 post-audit 回归**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  -m "not task8_post_audit" -q -p no:cacheprovider
git diff --check
git status --short --branch
```

预期：0 failed；工作区只允许计划执行记录的未提交变化。

- [ ] **Step 6.3：运行隐私、边界与追加式审计**

```powershell
rg -n "E:\\命理演绎|A9497ADC18B28749436053EF8092940F4D168800B91DB59770EF24ECCEF303A0" `
  src/mingli_engine/data/liuyao src/mingli_engine/liuyao tests
rg -n "必定|注定|一定会|死定" `
  src/mingli_engine/data/liuyao/liuyao_targeted_classics_reviews.json `
  src/mingli_engine/data/liuyao/liuyao_evidence_units.json
git diff c391ad88d91cbd634e8392026fa705c3cfd6586a -- `
  src/mingli_engine/data/liuyao/liuyao_sources.json `
  src/mingli_engine/data/liuyao/batch_20260714_liuyao_family_map.json
```

预期三条均零命中/零 diff。若既有 70 条中存在与本轮无关的历史词语，必须用“只扫描新增 0071-0077”的结构化脚本替代第二条，不修改历史记录来消除基线内容。

- [ ] **Step 6.4：按 `superpowers:requesting-code-review` 发起独立审查**

审查范围：设计符合性、7 条原页与安全化摘要一致性、去重、五台账回滚、前 70 条不可变、状态/API 不变、隐私与高风险边界。任何 Critical/Major 必须修复并重跑相应测试；Minor 必须记录裁决。

- [ ] **Step 6.5：追加执行记录并提交**

执行记录必须写明：7 条证据 ID、最终 family 分布、专项/全量测试数字、mypy/Ruff/diff 结果、审查结论，以及“未合并、未推送、未运行 main Task 8”。

```powershell
git add docs/superpowers/plans/2026-08-22-liuyao-classics-targeted-evidence.md
git diff --cached --check
git -c user.name="iiilxs" -c user.email="iiilxs@qq.com" commit `
  -m "docs(liuyao): record targeted evidence verification"
git status --short --branch
```

此处停止并向所有者汇报提交链。未经明确批准，不合并、不推送、不重写 main 的 Task 8 审计文件。

## Task 7：所有者批准后的 main 集成与发布审计

> 本任务是硬授权门。只有所有者明确说“同意合并/推送 022”后才能执行。

- [x] **Step 7.1：将已审查分支合并到 main**

在主工作树确认 main 干净、远端状态明确后，以非破坏方式合并；不得使用 `reset --hard` 或覆盖用户改动。

- [x] **Step 7.2：在 main 运行受控 Task 8**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen python -m mingli_engine.new_material_learning `
  run-task8-regression --batch batch_20260714
uv run --frozen python -m mingli_engine.new_material_learning `
  finalize-task8-audit --batch batch_20260714
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_new_material_learning.py -m task8_post_audit `
  -q -p no:cacheprovider
uv run --frozen --with pytest==8.4.1 python -m pytest `
  -q -p no:cacheprovider
git diff --check
```

Task 8 生成物必须按既有治理流程提交；post-audit 与全量回归均通过后，方可推送 main。

- [ ] **Step 7.3：最终声明条件**

只有以下条件全部成立，才可声明 022 完成：source 仍为 2；正式证据 77；前 70 条不变；应期 4 条引用但状态仍 degraded；API/schema 不变；全部专项、全量、Task 8、mypy、Ruff、diff 和独立审查通过；main 已按批准推送。

## 执行记录（2026-08-22，Task 1-6 完成）

- 新增证据 ID：`liuyao_evidence_batch_20260714_0071` 至 `0077`，对应复核记录
  `liuyao_classics_review_20260822_0001`-`0007`（《增删卜易》p28、p71；
  《卜筮正宗》p332、p333、p493、p498、p501），晋升批次
  `liuyao_promotion_batch_20260822_001`，curated batch
  `liuyao_curation_batch_20260822_002`。
- 最终 family 分布：yong_shen_selection 9、shi_ying_relation 3、
  moving_line_dynamics 5、six_spirits_attachment 3、month_day_strength 4、
  void_break_state 2、yingqi_timing 4、category_judgment 47，合计 77；
  默认报告引用总数 30；`yingqi_timing.status` 仍为 `degraded`。
- 测试结果：六爻专项 7 个测试文件 78 passed；
  `tests/contract/test_wheel_runtime_assets.py` 48 passed；全项目回归
  （排除 task8_post_audit）2599 passed, 1 skipped, 0 failed。
  （覆盖台账修正轮前：专项 75 passed、全量 2596 passed；更早记录中的
  2595 为参数化测试加入前的过时数字，已被取代。）
- 静态门禁：mypy 1.17.1（src/mingli_engine/liuyao，12 文件）零问题；
  Ruff 0.12.11 全部目标文件零告警；`git diff --check` 干净。
- 审计：用户绝对路径与用户文件二进制哈希在 src/台账/tests 零命中；
  复核台账与证据台账无绝对化措辞；`liuyao_sources.json` 与族映射文件相对
  基线 `c391ad8` 零 diff；四个知识台账为纯尾部追加（7/7/1/7）。
- 独立审查结论：首轮 REQUEST CHANGES（4 个 Major：loader 类型/页码/ID 序列
  严格性、对既有 70 条的语义签名查重、冻结前置批次顺序与计数校验、
  theme/applicability 安全门禁），已在 `772d154` 全部修复并重跑测试；
  复审 APPROVE WITH MINOR（1 个 Minor：门禁测试需同时覆盖 theme 与
  applicability），已在 `c433058` 参数化修复。
- 提交链：
  - `89b1f25` docs(liuyao): correct classical source coverage
  - `c35919e` data(liuyao): freeze targeted classics review
  - `29a370c` feat(liuyao): add targeted classics promotion
  - `3caa2f9` data(liuyao): append targeted classics evidence
  - `73e242e` test(liuyao): activate targeted classics citations
  - `a48ec39` test(liuyao): align wheel assets and privacy markers
  - `772d154` fix(liuyao): harden classics promotion gates
  - `c433058` test(liuyao): parameterize classics context gate
- 状态：所有者已批准，本地 `main` 已完成非破坏式快进合并并运行 Task 8；
  尚未推送，Step 7.3 最终发布条件待完成。

## 覆盖台账修正记录（2026-08-22，第二轮）

- `page:61`：duplicate → support_only；该页为反伏章（反吟、伏吟），已完成
  复核，不属于本轮三个弱族定向范围，留待后续 `moving_line_dynamics` 专项；
  设计文档中"第 61 页飞伏"的错误表述同步更正。
- `page:477-492` 拆分为三段：`page:477-482` support_only；`page:483`
  duplicate（有明确的原神生用、用神旺衰及待时条件，与复核记录
  `liuyao_classics_review_20260822_0004` 重复并建立关联）；
  `page:484-492` support_only。覆盖段数 18 → 20。
- `page:524`：保持 duplicate；理由更正为用神多现（两现）取舍与证据
  `liuyao_evidence_batch_20260714_0011` 重复，删除"进退神判定"错误表述。
- 新增语义防回归测试 3 项（p61 反吟伏吟、p483 关联 0004、p524 两现取舍），
  同时验证页码、disposition 与关键理由文本。
- 未新增或删除证据：正式证据仍为 77 条，前 70 条不变，推理接口与 schema
  不变；当前已合并并运行 Task 8，尚未推送。

## main 集成与 Task 8 审计记录（2026-08-23）

- `main` 由 `c391ad8` 非破坏式快进至 `727211b`，合并后预审计全量回归
  2599 passed、1 skipped、7 deselected。
- `run-task8-regression` 执行 7 条受控命令，退出码均为 0，回归前后治理
  快照一致。
- `finalize-task8-audit` 状态为 passed：29 个文件完成审计，0 个文件待处理；
  动态审计哈希只记录在 Task 8 生成物中，避免受治理计划形成自引用更新。
- post-audit 专项 7 passed；包含 post-audit 的全项目回归 2606 passed、
  1 skipped、0 failed；mypy、Ruff、`git diff --check` 均通过。
- 本轮仅更新既有 Task 8 治理生成物和本执行记录；未推送远端，Step 7.3
  仍保持未完成。
