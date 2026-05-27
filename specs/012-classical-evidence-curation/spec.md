# Feature Specification: 经典证据库精修

**Feature Branch**: `012-classical-evidence-curation`

**Created**: 2026-05-27

**Status**: Draft

**Input**: User description: "在 011 已搭建经典证据核心之后，继续深化经典证据库精修：逐本拆解九本命理 PDF/Markdown，扩充证据单元，补充页码/章节/主题/风险等级，建立来源冲突、证据不足和流派差异的报告呈现规则。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Curate Evidence Units By Source (Priority: P1)

作为维护者，我希望九本经典来源都能被逐本拆解成可审查的证据单元，而不是只停留在来源清单或少量初始卡片，这样正式报告能引用更丰富、更具体的规则依据。

**Why this priority**: 011 已经建立证据层骨架；012 的核心价值是把骨架变成可持续增长的证据库。没有逐本精修，正式报告仍会受限于少量泛化证据。

**Independent Test**: 可以检查每本初始来源是否至少有一批可审查证据单元，且每条证据包含来源引用、主题、规则家族、适用条件、限制条件和风险等级。

**Acceptance Scenarios**:

1. **Given** 九本初始来源已注册，**When** 维护者查看证据库，**Then** 每本来源都有对应的证据单元或明确的不可用/待审原因。
2. **Given** 某本来源已有可读 Markdown 或人工摘录，**When** 证据被纳入核心库，**Then** 证据单元包含页码、章节、标题或审阅引用，方便回查。
3. **Given** 某条规则适用于特定盘面条件，**When** 证据单元被读取，**Then** 其适用条件和限制条件足以判断是否可用于报告。

---

### User Story 2 - Classify Rule Families And Risk Tiers (Priority: P2)

作为报告使用者，我希望报告中的格局、旺衰、用神、十神、刑冲合害、盲派象法、大运流年和高风险信号都能来自清晰分类的证据单元，而不是混成同一种笼统依据。

**Why this priority**: 正式命理报告的可信度来自“结论属于什么规则家族、依据来自哪个流派、风险等级是什么”。分类越清楚，报告越可审计。

**Independent Test**: 可以按规则家族统计证据覆盖度，验证重点家族都有足够证据，并检查高风险材料全部带有限制和不确定性说明。

**Acceptance Scenarios**:

1. **Given** 一批新增证据单元，**When** 系统校验证据库，**Then** 每条证据都有合法的规则家族和风险等级。
2. **Given** 高风险材料涉及寿夭、疾病、灾厄、重大关系或财务压力，**When** 证据被保存，**Then** 该证据必须标为高风险或敏感，并带有不可输出精确结果的限制。
3. **Given** 某条证据只适用于特定流派或口径，**When** 它进入报告证据池，**Then** 报告可以显示该结论具有流派依赖。

---

### User Story 3 - Represent Source Conflict And Evidence Gaps (Priority: P3)

作为维护者，我希望同一主题下不同来源出现冲突、口径差异或证据不足时，系统能保留差异并在报告中降级说明，而不是强行合并成唯一结论。

**Why this priority**: 经典命理材料本身存在流派差异。精修证据库必须能保留争议，否则“核心证据”会变成新的不透明断语。

**Independent Test**: 可以构造同一规则家族下的支持证据和冲突证据，验证报告会输出候选、分歧或不可用状态，而不是硬下决定性结论。

**Acceptance Scenarios**:

1. **Given** 两本来源对同一判断条件有不同说法，**When** 证据库被校验，**Then** 系统保留两条证据并标记冲突或流派差异。
2. **Given** 某项报告结论缺少足够证据，**When** 报告生成，**Then** 该结论降级为候选、弱支持或不可用。
3. **Given** 证据来自未审、阻断或抽取失败的来源，**When** 报告选择依据，**Then** 该来源不得支撑正式结论。

---

### User Story 4 - Audit Curation Quality (Priority: P4)

作为项目负责人，我希望每次扩充证据库后都能通过自动检查确认覆盖度、追溯性、风险边界和报告语言没有退化。

**Why this priority**: 证据库会持续增长，必须有回归检查防止无来源、长摘抄、恐吓式高风险话术或绝对化语言进入报告。

**Independent Test**: 可以运行证据库质量检查和报告回归样例，验证新增证据不会破坏来源追溯、安全边界和非绝对化口径。

**Acceptance Scenarios**:

1. **Given** 新增一批证据单元，**When** 质量检查运行，**Then** 系统报告每本来源的证据数量、风险分布和未解决问题。
2. **Given** 证据单元包含过长原文摘录，**When** 校验运行，**Then** 系统阻止其作为报告证据。
3. **Given** 报告引用新增证据，**When** 回归测试运行，**Then** 报告仍保留免责声明、来源摘要、证据 trace、结论强度和高风险边界。

### Edge Cases

- PDF 或 Markdown 抽取乱码、缺页、页码错乱时，相关材料必须停留在待审或失败状态，不得进入可引用证据。
- 同一来源内部存在断语式、恐吓式或绝对化表达时，证据单元必须改写为条件化摘要并保留限制说明。
- 同一规则家族下证据数量不足时，报告必须降级，不得用少量证据冒充完整流派判断。
- 新增证据覆盖高风险主题时，必须拒绝精确寿命、死亡时间、疾病诊断、治疗方案、法律心理投资指令和付费化解承诺。
- 来源文件、抽取文件和人工审阅记录之间不一致时，证据单元不得标为 approved。
- 证据库扩充不能要求保存用户个人命盘或历史报告。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST keep all nine initial books as first-class source entries with curation status and review notes.
- **FR-002**: System MUST allow each source to have multiple curated evidence units with source reference, theme, rule family, risk tier, summary, applicability, and limitations.
- **FR-003**: System MUST include page, chapter, heading, or review-note references for evidence units whenever a readable extract exists.
- **FR-004**: System MUST distinguish approved, reviewed, unreviewed, blocked, failed, and partially curated source material before report use.
- **FR-005**: System MUST validate evidence ids and source ids for uniqueness.
- **FR-006**: System MUST reject evidence units that point to blocked, unreviewed, failed, or unknown sources when used for report conclusions.
- **FR-007**: System MUST classify evidence across rule families including pattern strength, useful-god candidates, taboo-god candidates, ten-god relations, branch interactions, blind-school image methods, luck cycles, remedy boundaries, and high-risk signals.
- **FR-008**: System MUST support evidence coverage reporting by source, rule family, risk tier, and review status.
- **FR-009**: System MUST represent source disagreement, school dependency, or evidence insufficiency without forcing a single conclusion.
- **FR-010**: System MUST keep high-risk evidence tagged with explicit limitations and uncertainty language.
- **FR-011**: System MUST prevent long copied passages from becoming report-facing evidence summaries.
- **FR-012**: System MUST let formal reports use newly curated evidence without changing the public report contract introduced in 011.
- **FR-013**: System MUST keep safe formal reports traceable to chart signals and evidence ids.
- **FR-014**: System MUST keep high-risk narrowed reports and exact-outcome refusals covered by regression cases.
- **FR-015**: System MUST preserve raw PDFs and generated extracts without silently rewriting or deleting them.
- **FR-016**: System MUST provide maintainers a clear list of curation gaps that remain after each validation run.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MAY make substantive traditional 命理 judgments when they are backed by chart data and classical evidence.
- **SE-002**: System MUST present those judgments as traditional evidence analysis, not scientific proof, destiny enforcement, or guaranteed real-world outcomes.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source, key calculation assumptions, and evidence sources where reports depend on calendrical or school-specific rules.
- **SE-006**: System MAY discuss traditionally high-risk signals when source-backed, but MUST label uncertainty and MUST refuse guaranteed death timing, exact lifespan, medical diagnosis or treatment, legal instruction, psychological treatment, investment instruction, coercive matching, anxiety creation, and paid-remedy upsells.

### Key Entities *(include if feature involves data)*

- **Classical Source**: A registered book, PDF, converted extract, or reviewed source identity with curation status, review status, scope, and risk notes.
- **Evidence Unit**: A concise, reviewed rule summary linked to one source reference and tagged by theme, rule family, risk tier, applicability, limitations, and school.
- **Curation Batch**: A group of evidence units added or revised together, with coverage counts and unresolved review notes.
- **Source Conflict**: A recorded disagreement between evidence units, schools, or source passages that affects conclusion strength.
- **Coverage Report**: A maintainer-facing summary of evidence counts, gaps, risk distribution, and validation failures.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the nine initial sources have either approved evidence units or explicit curation gap reasons.
- **SC-002**: At least 60 curated evidence units are available across the initial corpus before the feature is considered complete.
- **SC-003**: At least eight rule families have approved evidence coverage.
- **SC-004**: 100% of high-risk evidence units include limitations and non-exact-output boundaries.
- **SC-005**: 0 approved evidence units contain long unreviewed copied passages or guaranteed real-world outcome phrasing.
- **SC-006**: Safe formal report regression cases show source summaries, evidence traces, and conclusion strength after evidence expansion.
- **SC-007**: High-risk regression cases remain narrowed or refused according to the expanded constitution.
- **SC-008**: A maintainer can identify which sources and rule families still need curation without reading implementation code.

## Assumptions

- 011 already provides the source registry, initial evidence units, expanded report evidence model, and high-risk boundary behavior.
- Raw PDFs and generated Markdown extracts are preparation materials, not runtime report inputs.
- Evidence summaries should be concise syntheses rather than copied source passages.
- Page or chapter references may use review-note references when PDF pagination is unreliable.
- User birth data and generated reports remain outside evidence curation storage.
- The first 012 pass focuses on the nine existing sources, not adding new books.
