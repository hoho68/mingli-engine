# Feature Specification: 第二层结构观察表达优化

**Feature Branch**: `006-structure-observation-language`

**Created**: 2026-05-18

**Status**: Draft

**Input**: User description: "006 只优化报告的 `第二层：结构观察`，让五行数量、十神关系和基础结构说明读起来更像清晰专业的中文报告，而不是系统输出；不改算法、不改安全边界、不改 CLI、不改 004 分层结构，也不改变 005 已完成的白话标签。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 读懂结构观察层 (Priority: P1)

作为第一次阅读八字报告的小白用户，我希望 `第二层：结构观察` 不像程序直接吐出的数据，而是用清晰、专业、顺口的中文解释这些结构信号，让我知道应该怎样看这些信息。

**Why this priority**: 006 的核心价值就是降低结构观察层的阅读门槛。当前报告的层次已经建立，但这一层仍有一些偏系统腔的句子，会让普通读者觉得生硬。

**Independent Test**: 生成一份完整、安全的 Markdown 报告，阅读 `第二层：结构观察`，确认五行、十神和基础结构说明都以自然报告语言呈现，并且没有被改成命运断语。

**Acceptance Scenarios**:

1. **Given** 一份完整、安全的自动排盘报告，**When** 用户阅读 `第二层：结构观察`，**Then** 五行数量说明用自然中文解释这些数字是观察材料，而不是只显示生硬的系统式句子。
2. **Given** 一份完整、安全的报告，**When** 用户阅读基础结构说明，**Then** 文案说明当前层次是在看分布、集中度和有无情况，而不是直接下结论。

---

### User Story 2 - 保留关键结构信息 (Priority: P2)

作为需要核对报告信息的用户，我希望优化文字以后，五行计数和四柱十神关系仍然完整可见，这样我既能看懂，也能知道报告依据来自哪里。

**Why this priority**: 语言变顺不能牺牲透明度。五行数量和十神关系是结构观察层的核心材料，必须保留。

**Independent Test**: 生成一份完整、安全的 Markdown 报告，确认 `第二层：结构观察` 仍然展示五行计数，并且仍然展示年柱、月柱、日柱、时柱对应的十神关系。

**Acceptance Scenarios**:

1. **Given** 一份包含五行计数的报告，**When** 用户阅读五行观察文字，**Then** 用户仍然能看到各五行的计数值。
2. **Given** 一份包含十神关系的报告，**When** 用户阅读十神观察文字，**Then** 用户仍然能看到各柱位对应的十神关系，并且这些关系被表述为结构线索而不是最终结论。

---

### User Story 3 - 保持克制和安全边界 (Priority: P3)

作为谨慎使用命理工具的用户，我希望文字更顺以后，报告仍然保持观察和反思定位，不因为表达更自然就变得更绝对、更吓人或更像预测。

**Why this priority**: 命理报告属于敏感文化解释场景。可读性提升必须服从安全边界，不能引入新的吉凶判断、宿命结论或现实结果承诺。

**Independent Test**: 运行安全与非安全报告生成流程，确认免责声明、伦理边界、红线拒绝、禁止绝对化语言等保护仍然有效。

**Acceptance Scenarios**:

1. **Given** 一份完整、安全的报告，**When** 用户阅读结构观察层，**Then** 报告只表达观察线索，不出现吉凶、用神、格局定论、旺衰定论、大运流年或现实事件预测。
2. **Given** 一个触发安全红线的关注主题，**When** 用户生成报告，**Then** 系统仍然返回安全 JSON，而不是 Markdown 报告。

### Edge Cases

- 五行计数中有多个元素同时相对集中。
- 五行计数中某个元素很少或完全不可见。
- 五行分布没有明显集中信号。
- 十神信息存在缺失、未知或无法判断的情况。
- 关注主题为空、通用或使用系统默认占位主题。
- 关注主题触发安全红线，系统必须继续拒绝生成正式 Markdown。
- 报告由自动排盘生成，或由外部已核对盘面生成。
- 用户只阅读 `第二层：结构观察`，也不能被误导为已经得到完整命运结论。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 每份完整、安全的 Markdown 报告 MUST 保留 `第二层：结构观察` 这一层级和它在报告中的现有位置。
- **FR-002**: 五行观察文字 MUST 用自然中文说明五行数量是结构观察材料，而不是完整旺衰模型或最终结论。
- **FR-003**: 五行观察文字 MUST 保留当前报告中已经计算出的各五行计数值。
- **FR-004**: 当五行信号有相对集中或相对少见的情况时，报告 MUST 以观察语气说明这些情况，不得表达成吉凶或命运判断。
- **FR-005**: 十神观察文字 MUST 保留各柱位对应的十神关系，并用读者能理解的引导语说明它们是结构线索。
- **FR-006**: 基础结构观察文字 MUST 使用自然报告表达，避免直接呈现内部说明式句子。
- **FR-007**: 完整、安全的报告 MUST NOT 出现选定的系统腔句式，例如 `五行信号观察：明面信号为`、`这些数量用于观察结构分布`、`基础结构观察：五行分布先看有无、多少与集中度。`。
- **FR-008**: 006 的改动 MUST 聚焦在 `第二层：结构观察`，不得主动重写免责声明、快速导读、基础资料、解读边界、行动反思、术语简注或伦理边界提醒。
- **FR-009**: 006 的改动 MUST 保持 005 已完成的读者友好标签，不得重新暴露 `auto_calculated`、`medium`、`gregorian`、`year`、`month`、`day`、`hour` 等机器字段。
- **FR-010**: 现有 CLI 命令、输入 JSON 形状、安全拒绝退出行为和安全 JSON 形状 MUST 保持不变。
- **FR-011**: 006 MUST NOT 新增格局、用神、旺衰、大运流年、吉凶、现实事件或结果承诺类判断。

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MUST present outputs as cultural interpretation and self-reflection, not scientific prediction or fate verdict.
- **SE-002**: System MUST refuse or safely redirect requests involving lifespan, death timing, major disaster prediction, deterministic marriage matching, medical advice, legal advice, psychological treatment, investment instruction, unauthorized third-party full-chart analysis, anxiety creation, or paid remedy upsells.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source and key calculation assumptions where reports depend on calendrical or school-specific rules.
- **SE-006**: Smoother structure wording MUST NOT increase certainty, imply fixed fate, or weaken existing interpretation boundaries.

### Key Entities *(include if feature involves data)*

- **结构观察层**: Markdown 报告中用于说明五行分布、十神关系和基础结构线索的第二层内容。
- **五行观察文字**: 对木、火、土、金、水计数和相对分布的读者-facing 说明。
- **十神观察文字**: 对各柱位十神关系的读者-facing 说明。
- **基础结构说明**: 对“先看分布、集中度、有无情况”的简短解释性文字。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 测试套件中的完整安全 Markdown 报告 100% 保留 `第二层：结构观察`，且该层文字不包含 FR-007 列出的系统腔句式。
- **SC-002**: 测试套件中的完整安全 Markdown 报告 100% 保留五行计数值。
- **SC-003**: 测试套件中的完整安全 Markdown 报告 100% 保留各柱位十神关系。
- **SC-004**: 测试套件中的完整安全 Markdown 报告 100% 保持 004 分层标题顺序不变。
- **SC-005**: 测试套件中的完整安全 Markdown 报告 100% 保持 005 已完成的读者友好标签。
- **SC-006**: 红线关注主题测试 100% 继续返回安全 JSON，而不是 Markdown。
- **SC-007**: 生成的正式报告中 0 处新增吉凶、用神、格局、旺衰、大运流年或现实事件预测类判断。

## Assumptions

- 当前排盘和解释规则已经是 006 的输入基础；本阶段只改表达，不改含义。
- 目标读者是命理小白，需要清晰专业但不啰嗦的中文说明。
- 结构观察层可以保留必要命理术语，但必须用周边文字解释它们只是观察线索。
- 自动排盘和外部核对盘面都应使用同一套结构观察表达。
- 006 不需要新增配置项；用户不需要通过参数选择新旧文案。
