# Feature Specification: 报告证据说明层

**Feature Branch**: `009-report-evidence-notes`

**Created**: 2026-05-20

**Status**: Draft

**Input**: User description: "009 报告证据说明层：在安全 Markdown 报告中新增观察依据小节，用白话说明结构观察来自排盘来源、四柱、五行、十神和行动反思边界；不新增命理判断、不改 CLI、不改算法。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 读者能看懂观察从哪里来 (Priority: P1)

作为阅读正式报告的人，我希望在结构观察层看到一段清楚的“观察依据”说明，知道报告里的结构观察来自排盘来源、四柱、五行和十神等已有资料，而不是凭空断事。

**Why this priority**: 009 的核心价值是让报告更可审查、更透明。读者先能看懂“依据是什么”，后续才适合继续阅读结构分析和行动反思。

**Independent Test**: 生成一份安全正式报告，检查报告在结构观察层包含 `观察依据` 小节，并且该小节能说明来源假设、四柱、五行、十神和行动反思的依据。

**Acceptance Scenarios**:

1. **Given** 一个安全的自动排盘输入，**When** 用户生成正式 Markdown 报告，**Then** 报告在结构观察层展示 `观察依据` 小节，并说明结构观察依赖已有排盘来源与结构信号。
2. **Given** 一个安全的外部核对盘输入，**When** 用户生成正式 Markdown 报告，**Then** 报告同样展示 `观察依据` 小节，并且不会把外部核对盘误说成系统自动排盘。
3. **Given** 报告已经展示四柱、五行和十神摘要，**When** 读者继续阅读结构观察层，**Then** 能在进入更宽泛分析前看到这些摘要如何被当作观察依据。

---

### User Story 2 - 维护者能用回归样例守住证据说明 (Priority: P2)

作为维护报告生成器的人，我希望现有安全报告回归样例也能检查 `观察依据`，这样未来改报告文案时，不会不小心删掉或移动这层证据说明。

**Why this priority**: 008 已经建立了报告回归样例库。009 应该把新小节纳入同一套守护机制，避免新增内容只在单元测试里被覆盖。

**Independent Test**: 运行报告回归样例验证，确认所有安全 Markdown 样例都包含 `观察依据`，且顺序、核心含义和安全语言边界仍然满足要求。

**Acceptance Scenarios**:

1. **Given** 回归样例清单包含安全自动排盘样例，**When** 回归验证运行该样例，**Then** 验证会检查 `观察依据` 小节存在并位于结构观察层。
2. **Given** 回归样例清单包含安全外部核对盘样例，**When** 回归验证运行该样例，**Then** 验证会检查 `观察依据` 小节，同时保留外部来源说明。
3. **Given** 后续维护者改动报告结构，**When** `观察依据` 被删除、移动到错误层级或失去核心说明，**Then** 自动化验证会失败。

---

### User Story 3 - 证据说明不变成新的命理断语 (Priority: P3)

作为谨慎使用命理报告的人，我希望新增的证据说明只解释观察依据和阅读边界，而不是新增格局、用神、大运流年、吉凶或事件预测等判断。

**Why this priority**: 证据说明的目标是提高透明度，不是让报告显得更权威或更断言。安全边界必须和可读性一起前进。

**Independent Test**: 检查新增的证据说明内容，确认它没有新增命运判断、绝对化语言、红线主题或专业建议，并且红线输入仍然返回安全 JSON。

**Acceptance Scenarios**:

1. **Given** 一份安全正式报告，**When** 检查 `观察依据` 小节，**Then** 小节只说明资料来源和结构信号，不给出新的格局、用神、强弱、大运流年或现实事件判断。
2. **Given** 用户请求寿命、死亡时间等红线主题，**When** 请求正式 Markdown 报告，**Then** 系统仍返回安全 JSON，而不是包含 `观察依据` 的正式报告。
3. **Given** 报告内容经过安全语言检查，**When** 检查新增证据说明，**Then** 不出现 `必定`、`注定`、`一定会`、`死定` 等绝对化话术。

---

### Edge Cases

- 安全自动排盘报告和安全外部核对盘报告都必须包含 `观察依据`，但来源说明不得互相误标。
- 缺少必要出生资料时，不应为了展示 `观察依据` 而生成完整正式报告。
- 红线关注主题仍应返回安全 JSON，不应出现正式 Markdown 报告或 `观察依据` 小节。
- 报告已有的四层阅读顺序不得被新增小节打乱。
- `观察依据` 不应暴露原始机器标签，例如 `auto_calculated`、`external_verified`、`medium` 或 `gregorian`。
- `观察依据` 不应复制整篇报告或形成完整 Markdown 快照依赖。
- 当后续新增安全报告样例时，样例应能被同一套回归验证检查是否包含证据说明。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every formal safe Markdown report MUST include a reader-facing `观察依据` section.
- **FR-002**: The `观察依据` section MUST appear inside the structure-observation layer after the report has shown four-pillar, five-element, and ten-god summaries, and before broader structure analysis.
- **FR-003**: The `观察依据` section MUST explain that observations start from chart source and assumptions rather than unsupported certainty.
- **FR-004**: The `观察依据` section MUST explain that four-pillar observations come from year, month, day, and hour pillar structure positions and combinations.
- **FR-005**: The `观察依据` section MUST explain that five-element observations come from visible signals, hidden-stem signals, and total counted signals.
- **FR-006**: The `观察依据` section MUST explain that ten-god observations are relationship signals across pillar positions.
- **FR-007**: The `观察依据` section MUST explain that action reflection turns observable structure signals into review prompts rather than outcome predictions.
- **FR-008**: Safe automatic-chart reports MUST keep automatic chart source wording visible while showing the evidence section.
- **FR-009**: Safe external-verified chart reports MUST keep external source wording visible and MUST NOT be mislabeled as automatic chart output while showing the evidence section.
- **FR-010**: Unsafe red-line cases MUST continue returning safety JSON instead of a formal Markdown report with an evidence section.
- **FR-011**: The feature MUST NOT add or require new user-facing CLI commands, command flags, input data shapes, chart calculations, interpretation conclusions, full Markdown snapshots, or export formats.
- **FR-012**: Automated validation MUST exercise the evidence section for every safe Markdown case listed in the report regression case list.
- **FR-013**: The evidence section MUST use reader-facing wording and MUST NOT expose selected raw machine labels.
- **FR-014**: The evidence section MUST NOT introduce absolute destiny language or new fate verdicts.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MUST present outputs as cultural interpretation and self-reflection, not scientific prediction or fate verdict.
- **SE-002**: System MUST refuse or safely redirect requests involving lifespan, death timing, major disaster prediction, deterministic marriage matching, medical advice, legal advice, psychological treatment, investment instruction, unauthorized third-party full-chart analysis, anxiety creation, or paid remedy upsells.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source and key calculation assumptions where reports depend on calendrical or school-specific rules.
- **SE-006**: The evidence section MUST reinforce reviewability and boundaries without adding auspiciousness claims, useful-god verdicts, strength verdicts, luck-cycle judgments, or real-world event predictions.

### Key Entities *(include if feature involves data)*

- **观察依据小节**: 正式报告中的一段读者可见说明，用来解释结构观察基于哪些已有资料和信号。
- **依据检查点**: `观察依据` 必须覆盖的稳定说明点，包括来源假设、四柱、五行、十神和行动反思边界。
- **安全正式报告**: 已通过安全检查并可输出为 Markdown 的报告；该报告必须包含免责声明、来源假设、四层结构和证据说明。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of formal safe Markdown reports include a visible `观察依据` section.
- **SC-002**: 100% of safe report regression cases verify that `观察依据` appears in the structure-observation layer in the required order.
- **SC-003**: 100% of safe report regression cases verify evidence wording for source assumptions, four pillars, five-element signals, ten-god signals, and action-reflection boundaries.
- **SC-004**: 100% of unsafe red-line report requests continue returning safety JSON instead of a formal Markdown report.
- **SC-005**: 0 new user-facing commands, flags, input shapes, chart calculations, interpretation conclusions, full Markdown snapshots, or export formats are required for 009.
- **SC-006**: 100% of existing report and safety regression checks continue passing after the evidence section is added.

## Assumptions

- The first version should use concise, durable wording rather than long explanatory prose.
- The evidence section is for formal safe reports only; unsafe red-line inputs do not receive a formal report.
- Existing chart source, four-pillar, five-element, ten-god, and action-reflection content is sufficient for the first evidence explanation.
- The feature is about transparency and reviewability, not deeper interpretation.
- Existing regression case coverage from 008 is the right place to protect this new report contract.
