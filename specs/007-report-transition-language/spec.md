# Feature Specification: 报告层间衔接语优化

**Feature Branch**: `007-report-transition-language`

**Created**: 2026-05-18

**Status**: Draft

**Input**: User description: "007 优化整份 Markdown 八字报告的层间衔接语，让快速导读、基础资料、结构观察、解读边界和行动反思读起来像一份连贯报告；保留 004 分层结构、005 白话标签、006 结构观察文案，不改算法、不改 CLI、不新增命理判断或安全风险。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 按顺序读完整份报告 (Priority: P1)

作为第一次阅读八字报告的小白用户，我希望报告能告诉我“为什么先看这一层、下一层要看什么”，这样我不会觉得内容只是几块模块拼在一起。

**Why this priority**: 007 的核心价值是整体阅读体验。当前每一层已经能读，但层与层之间的关系还不够清楚，读者可能不知道如何从基础资料走到结构观察，再走到边界和行动反思。

**Independent Test**: 生成一份完整、安全的 Markdown 报告，确认快速导读或各层正文中出现简短衔接语，能说明阅读顺序和层间关系，同时标题顺序保持不变。

**Acceptance Scenarios**:

1. **Given** 一份完整、安全的自动排盘报告，**When** 用户阅读快速导读，**Then** 用户能看到如何从基础资料、结构观察、解读边界一路读到行动反思的提示。
2. **Given** 一份完整、安全的报告，**When** 用户从第一层读到第二层，**Then** 报告能说明基础资料是来源和假设，不是命理结论。
3. **Given** 一份完整、安全的报告，**When** 用户从第二层读到第三层，**Then** 报告能说明结构观察只是线索，需要解读边界来避免过度判断。

---

### User Story 2 - 把边界自然接到行动反思 (Priority: P2)

作为想拿报告做复盘的用户，我希望“解读边界”不是突然中断阅读，而是自然引导我把观察转成小问题或行动反思。

**Why this priority**: 命理报告必须保持安全边界，但边界不应该让用户误以为报告没有价值。它应该帮助用户理解：报告只能提供观察语言，下一步是现实复盘。

**Independent Test**: 生成一份完整、安全的 Markdown 报告，确认第三层之后有清楚的边界转行动说明，第四层行动反思也明确表达“复盘提示”而非结果承诺。

**Acceptance Scenarios**:

1. **Given** 一份完整、安全的报告，**When** 用户阅读第三层解读边界，**Then** 报告能说明这些边界是为了防止过度断言，而不是否定结构观察本身。
2. **Given** 一份完整、安全的报告，**When** 用户阅读第四层行动反思，**Then** 报告能说明行动建议是复盘问题或整理方向，不是现实结果承诺。

---

### User Story 3 - 保留既有结构和安全边界 (Priority: P3)

作为谨慎使用命理工具的用户，我希望报告变得更连贯以后，仍然保留原有分层、来源透明、免责声明和红线拒绝，不因为文字更自然就更像预测。

**Why this priority**: 这是敏感文化解释场景。衔接语只能提升阅读路径，不能增加确定性、宿命感或专业建议风险。

**Independent Test**: 运行安全和完整报告生成流程，确认 004 标题顺序、005 标签、006 结构观察文案、安全 JSON、免责声明、伦理提醒和禁止绝对化语言都保持有效。

**Acceptance Scenarios**:

1. **Given** 一份完整、安全的报告，**When** 用户阅读报告，**Then** 004 的主要标题顺序保持不变。
2. **Given** 一份完整、安全的报告，**When** 用户阅读基础资料和结构观察，**Then** 005 的读者友好标签和 006 的结构观察文案仍然存在。
3. **Given** 一个触发安全红线的关注主题，**When** 用户生成报告，**Then** 系统仍然返回安全 JSON，而不是 Markdown 报告。

### Edge Cases

- 报告由自动排盘生成。
- 报告由外部已核对盘面生成。
- 关注主题为空、通用或使用系统默认占位主题。
- 报告里没有大运流年数据，阶段概览仍不能变成预测。
- 五行结构没有明显集中信号，衔接语仍应成立。
- 读者只读快速导读，也能知道后续层级的阅读顺序。
- 读者跳到第三层或第四层，也不能把边界或行动反思误解成结果承诺。
- 关注主题触发安全红线，系统必须继续拒绝生成正式 Markdown。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 每份完整、安全的 Markdown 报告 MUST 保留 004 建立的主要标题顺序。
- **FR-002**: 每份完整、安全的 Markdown 报告 MUST 包含简短衔接语，帮助读者理解快速导读、基础资料、结构观察、解读边界和行动反思之间的阅读关系。
- **FR-003**: 快速导读 MUST 继续保持简洁，并说明读者可以按“先核对资料与假设，再看结构观察，再看边界，最后做行动反思”的路径阅读。
- **FR-004**: 第一层相关文字 MUST 明确表达基础资料、来源和假设是报告依据，不是命理结论。
- **FR-005**: 第二层相关文字 MUST 明确表达结构观察是线索或材料，不是最终判断。
- **FR-006**: 第三层相关文字 MUST 明确表达解读边界用于防止过度断言，并自然引向第四层行动反思。
- **FR-007**: 第四层相关文字 MUST 明确表达行动建议是复盘提示、整理方向或小问题，不是结果承诺。
- **FR-008**: 007 的改动 MUST NOT 改变现有 CLI 命令、命令参数、输入 JSON 形状、安全拒绝退出行为或安全 JSON 形状。
- **FR-009**: 007 的改动 MUST 保留 005 已完成的读者友好标签，不得重新暴露已禁止的机器字段。
- **FR-010**: 007 的改动 MUST 保留 006 已完成的结构观察核心文案。
- **FR-011**: 007 MUST NOT 新增格局、用神、旺衰、大运流年、吉凶、现实事件预测或结果承诺类判断。
- **FR-012**: 衔接语 SHOULD 保持简短，不得把报告改写成长篇叙述或明显增加阅读负担。

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MUST present outputs as cultural interpretation and self-reflection, not scientific prediction or fate verdict.
- **SE-002**: System MUST refuse or safely redirect requests involving lifespan, death timing, major disaster prediction, deterministic marriage matching, medical advice, legal advice, psychological treatment, investment instruction, unauthorized third-party full-chart analysis, anxiety creation, or paid remedy upsells.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source and key calculation assumptions where reports depend on calendrical or school-specific rules.
- **SE-006**: Transition wording MUST NOT increase certainty, imply fixed fate, or weaken existing interpretation boundaries.

### Key Entities *(include if feature involves data)*

- **报告衔接语**: 出现在现有报告字段中的简短说明，用来解释当前层和下一层的阅读关系。
- **阅读路径**: 用户从快速导读到基础资料、结构观察、解读边界、行动反思的安全阅读顺序。
- **基础资料桥接说明**: 说明来源、历法、时区、节气、真太阳时等属于依据和假设，不是结论。
- **边界到行动桥接说明**: 说明边界用于防止过度断言，并将观察转化为复盘问题。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 测试套件中的完整安全 Markdown 报告 100% 保留 004 主要标题顺序。
- **SC-002**: 测试套件中的完整安全 Markdown 报告 100% 包含快速导读到后续层级的阅读路径提示。
- **SC-003**: 测试套件中的完整安全 Markdown 报告 100% 包含基础资料“依据而非结论”的表达。
- **SC-004**: 测试套件中的完整安全 Markdown 报告 100% 包含结构观察“线索而非最终判断”的表达。
- **SC-005**: 测试套件中的完整安全 Markdown 报告 100% 包含边界到行动反思的桥接表达。
- **SC-006**: 测试套件中的完整安全 Markdown 报告 100% 保留 005 读者友好标签和 006 结构观察文案。
- **SC-007**: 红线关注主题测试 100% 继续返回安全 JSON，而不是 Markdown。
- **SC-008**: 生成的正式报告中 0 处新增吉凶、用神、格局、旺衰、大运流年或现实事件预测类判断。

## Assumptions

- 当前报告的标题顺序和主要字段已经足够稳定，007 只补充或轻微调整字段内文案。
- 目标读者是命理小白，需要知道阅读顺序，但不需要长篇解释。
- 自动排盘和外部核对盘面都使用同一套衔接语规则。
- 007 不需要新增配置项；用户不需要通过参数选择是否开启衔接语。
- 现有安全检查和免责声明继续作为正式报告输出前的必要保护。
