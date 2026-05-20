# Feature Specification: 报告回归样例清单

**Feature Branch**: `008-report-regression-cases`

**Created**: 2026-05-20

**Status**: Draft

**Input**: User description: "008 做样例清单版回归样例库。用现有自动排盘、外部核对盘和红线拒绝样例建立一个稳定回归清单，并用测试批量验证安全 Markdown 报告继续保留 004 分层结构、005 白话标签、006 结构观察文案、007 层间衔接语，以及红线主题继续返回安全 JSON。不做完整 Markdown 快照、不改 CLI、不改算法、不新增命理判断。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 用清单守住安全报告结构 (Priority: P1)

作为维护报告生成器的人，我希望有一个明确的回归样例清单，能批量验证安全报告是否仍然保留关键标题、来源说明、白话标签、结构观察文案和层间衔接语，这样以后修改报告时不会不小心破坏成品报告体验。

**Why this priority**: 008 的核心价值是防止 004-007 的报告体验被未来改动破坏。安全报告是最常见、最需要稳定的输出。

**Independent Test**: 按样例清单运行安全自动排盘样例和安全外部核对样例，确认两类样例都能生成 Markdown，并且每份报告都包含指定的报告结构与关键文案。

**Acceptance Scenarios**:

1. **Given** 样例清单中包含安全自动排盘样例，**When** 回归验证运行该样例，**Then** 输出是正式 Markdown 报告，并保留自动排盘来源、基础假设、四层阅读结构、结构观察文案和层间衔接语。
2. **Given** 样例清单中包含安全外部核对盘样例，**When** 回归验证运行该样例，**Then** 输出是正式 Markdown 报告，并保留外部核对来源说明，且不会被误标成系统自动排盘。
3. **Given** 安全样例报告已经生成，**When** 回归验证检查报告正文，**Then** 报告不得暴露选定的机器标签或绝对化命运话术。

---

### User Story 2 - 用清单守住安全拒绝行为 (Priority: P2)

作为谨慎使用命理工具的人，我希望红线关注主题也被纳入回归样例清单，这样未来改动报告时，不会让寿命、死亡时间等红线请求误生成正式 Markdown 报告。

**Why this priority**: 命理报告属于敏感文化解释场景。安全拒绝行为必须和正常报告一样被稳定验证。

**Independent Test**: 按样例清单运行红线样例，确认请求 Markdown 输出时仍然返回安全 JSON，且包含明确的拒绝分类。

**Acceptance Scenarios**:

1. **Given** 样例清单中包含寿命或死亡时间相关红线样例，**When** 回归验证运行该样例并请求 Markdown，**Then** 系统返回安全 JSON，而不是正式 Markdown 报告。
2. **Given** 红线样例返回安全 JSON，**When** 回归验证检查返回内容，**Then** `allowed` 为 false，并包含对应红线分类。

---

### User Story 3 - 让样例清单成为后续扩展入口 (Priority: P3)

作为后续继续扩展报告能力的人，我希望样例清单清楚记录每个样例的用途和预期行为，这样新增样例时不用复制散落在多个测试里的隐含规则。

**Why this priority**: 008 不是只写几条测试，而是给后续报告回归测试建立一个入口。清单越清楚，后续新增样例越不容易混乱。

**Independent Test**: 查看样例清单，确认每个样例都有可识别的编号、输入、预期输出类别和用途说明，并且清单中的每个样例都会被自动验证。

**Acceptance Scenarios**:

1. **Given** 维护者打开样例清单，**When** 查看任意一个样例条目，**Then** 能知道该样例用于验证安全 Markdown 还是安全 JSON 拒绝。
2. **Given** 样例清单新增一个条目，**When** 回归验证运行，**Then** 新条目会被纳入验证，而不是需要额外手写一条独立测试才能被发现。

---

### Edge Cases

- 样例清单引用了不存在的输入文件。
- 样例清单中的样例类型不是已支持的安全 Markdown 或安全 JSON。
- 安全样例错误返回了安全 JSON 或非零退出状态。
- 红线样例错误返回了正式 Markdown。
- 外部核对盘样例被误标成系统自动排盘。
- 安全报告缺少 004-007 任一关键合同文字。
- 安全报告出现选定的机器标签或绝对化命运话术。
- 样例清单为空或没有覆盖至少一个安全样例和一个红线样例。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a report regression case list that records representative report examples and their expected output type.
- **FR-002**: The regression case list MUST include at least one safe automatic-chart report case.
- **FR-003**: The regression case list MUST include at least one safe external-verified chart report case.
- **FR-004**: The regression case list MUST include at least one unsafe red-line focus-topic case.
- **FR-005**: Each regression case MUST have a stable identifier, input reference, expected output category, and human-readable purpose.
- **FR-006**: Every case in the regression list MUST be exercised by automated regression validation.
- **FR-007**: Safe Markdown report cases MUST verify the feature 004 layered heading order remains visible.
- **FR-008**: Safe Markdown report cases MUST verify feature 005 reader-facing labels remain visible and selected machine-facing labels remain absent.
- **FR-009**: Safe Markdown report cases MUST verify feature 006 structure observation wording remains visible.
- **FR-010**: Safe Markdown report cases MUST verify feature 007 transition wording remains visible.
- **FR-011**: Safe Markdown report cases MUST verify selected absolute destiny phrases remain absent.
- **FR-012**: External-verified safe report cases MUST verify external source wording remains visible and is not mislabeled as automatic chart output.
- **FR-013**: Unsafe red-line cases MUST verify the system returns safety JSON instead of a Markdown report.
- **FR-014**: Unsafe red-line cases MUST verify the safety JSON includes `allowed` as false and includes the expected red-line category.
- **FR-015**: 008 MUST NOT add or require new user-facing CLI commands, command flags, input data shapes, chart calculations, interpretation conclusions, or full Markdown snapshots.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MUST present outputs as cultural interpretation and self-reflection, not scientific prediction or fate verdict.
- **SE-002**: System MUST refuse or safely redirect requests involving lifespan, death timing, major disaster prediction, deterministic marriage matching, medical advice, legal advice, psychological treatment, investment instruction, unauthorized third-party full-chart analysis, anxiety creation, or paid remedy upsells.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source and key calculation assumptions where reports depend on calendrical or school-specific rules.
- **SE-006**: Regression examples MUST NOT be used to introduce new fate judgments, auspiciousness claims, useful-god verdicts, strength verdicts, luck-cycle judgments, or real-world event predictions.

### Key Entities *(include if feature involves data)*

- **回归样例清单**: 一组代表性报告样例的登记入口，记录每个样例的编号、输入引用、预期输出类别和验证用途。
- **安全 Markdown 样例**: 预期生成正式 Markdown 报告的样例，用来验证报告结构、来源说明、白话标签、结构观察和层间衔接语。
- **安全 JSON 样例**: 预期触发安全拒绝并返回 JSON 的样例，用来验证红线主题不会生成正式 Markdown。
- **报告合同检查点**: 回归验证必须检查的稳定报告要点，例如标题顺序、来源标签、结构观察文案、衔接语、安全边界和禁用话术。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Regression validation covers 100% of cases listed in the report regression case list.
- **SC-002**: The regression case list contains at least 3 cases: one safe automatic-chart case, one safe external-verified case, and one unsafe red-line case.
- **SC-003**: 100% of safe Markdown cases verify the key 004-007 report contracts.
- **SC-004**: 100% of unsafe red-line cases verify safety JSON instead of Markdown.
- **SC-005**: 100% of safe Markdown cases verify selected raw machine labels and selected absolute destiny phrases are absent.
- **SC-006**: Existing report-generation commands continue to work without requiring users to learn a new command or flag.

## Assumptions

- Existing `examples/` files are sufficient for the first regression case list.
- The first version should favor durable phrase and behavior checks over full-output snapshots.
- The regression case list is for maintainers and automated verification, not for end-user report display.
- Future features can add more cases to the same list without changing the user-facing CLI.
