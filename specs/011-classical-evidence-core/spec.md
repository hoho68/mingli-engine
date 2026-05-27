# Feature Specification: 典籍证据核心与放大报告口径

**Feature Branch**: `011-classical-evidence-core`

**Created**: 2026-05-27

**Status**: Draft

**Input**: User description: "将九本命理 PDF 认真学习并作为命理演绎正式报告的核心证据；不是作为反例，而是作为报告论证主干。将现有安全宪法尺度尽量放大，采用允许正式传统命理判断、但保留来源、分歧、置信度和非绝对化边界的新口径。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use Classical Books As Core Evidence (Priority: P1)

作为正式命理报告的使用者，我希望报告解释不是来自空泛模板，而是能回到指定命理书籍、规则类别和证据链，这样报告更像真正的命理演绎。

**Why this priority**: 这是本特性的核心价值。没有典籍证据层，后续格局、用神、岁运、盲派象法等判断仍然只是无来源文案。

**Independent Test**: 可以用任一安全完整八字生成报告，验证报告包含可见的命理依据，且依据指向指定来源集合中的书籍或规则类别。

**Acceptance Scenarios**:

1. **Given** 九本指定命理 PDF 已作为来源资料进入项目，**When** 用户生成正式报告，**Then** 报告包含与结论相关的命理依据，而不是只输出泛化观察。
2. **Given** 某条结论引用了盲派、段氏、五行十神或岁运规则，**When** 维护者审查报告，**Then** 可以追溯该结论使用的来源书目、规则类别和解释链。
3. **Given** 来源资料之间存在不同口径，**When** 报告使用其中一种口径，**Then** 报告说明这是特定来源或流派下的判断，而不是唯一真理。

---

### User Story 2 - Produce Formal Traditional Judgments (Priority: P2)

作为想要正式命理分析的用户，我希望报告能够给出格局、旺衰、用神候选、十神组合、刑冲合害、盲派象法、大运流年等实质判断，而不只是温和的自我反思提示。

**Why this priority**: 用户已明确要求扩大安全宪法尺度，让系统进入正式命理报告口径。报告必须能承载传统命理判断，否则典籍证据库无法发挥作用。

**Independent Test**: 可以用包含完整四柱、大运信息和安全关注主题的样例生成报告，验证报告出现来源支持的正式判断，并同时保留置信度和边界。

**Acceptance Scenarios**:

1. **Given** 一份完整安全命盘，**When** 生成正式报告，**Then** 报告可以给出格局候选、旺衰倾向、用神候选或忌神候选等判断。
2. **Given** 报告进入大运流年分析，**When** 输出阶段主题，**Then** 报告可以说明传统命理上的触发条件、应期线索和风险点。
3. **Given** 判断依据不足，**When** 报告生成，**Then** 系统降级为候选、待核或分歧说明，而不是硬下定论。

---

### User Story 3 - Expand High-Risk Material With Boundaries (Priority: P3)

作为需要严肃命理分析的用户，我希望生死、疾病、灾厄、重大关系和财务风险类材料不被简单删除，而是以传统高风险信号的形式进入报告证据，同时不变成恐吓或专业建议。

**Why this priority**: 指定书目中包含大量高风险内容。如果完全排除，违背用户对核心证据的要求；如果无边界输出，又会形成恐吓和误导。

**Independent Test**: 可以用高风险关注主题和普通关注主题分别生成报告，验证普通报告能引用高风险规则作为传统信号，禁止输出精确寿命、诊断、治疗、投资或保证式化解。

**Acceptance Scenarios**:

1. **Given** 传统来源中存在生死、疾病或灾厄规则，**When** 报告需要引用，**Then** 系统将其标记为高风险传统信号并解释条件和不确定性。
2. **Given** 用户要求精确死亡年份、寿命终点或疾病诊断，**When** 系统响应，**Then** 系统拒绝或缩窄为传统风险信号说明。
3. **Given** 用户询问化解或改运，**When** 报告输出，**Then** 可以说明传统说法和低风险行动建议，但不得保证效果、制造恐惧或诱导付费。

---

### User Story 4 - Keep Reports Auditable Under The New Constitution (Priority: P4)

作为维护者，我希望新口径下的报告仍可测试、可审查、可回归，避免“尺度放大”变成任意断语。

**Why this priority**: 放大报告口径会提高产品价值，也提高语言、来源和风险控制复杂度。自动化检查必须跟上。

**Independent Test**: 运行回归样例，验证每份正式报告包含证据来源、关键判断、边界说明、免责声明，并且不出现绝对命运语言。

**Acceptance Scenarios**:

1. **Given** 报告包含多个传统判断，**When** 运行回归测试，**Then** 每个主要判断都能关联到证据或明确的降级原因。
2. **Given** 报告涉及高风险信号，**When** 运行安全语言检查，**Then** 报告不包含绝对化、恐吓式、保证式或专业建议式表达。
3. **Given** 后续新增来源书目，**When** 扩展证据库，**Then** 既有报告契约和新来源索引规则仍然适用。

### Edge Cases

- PDF 文字抽取出现乱码、缺页、表格错位或页码混乱时，来源不得进入可引用核心证据，直到人工标记为可审查。
- 同一规则在不同书中表述冲突时，报告必须显示流派或来源分歧，不能合并成单一断语。
- 来源材料含有明显恐吓、绝对化、疾病诊断、死亡断语或付费化解话术时，报告必须改写为传统高风险信号说明。
- 命盘缺少出生时间、地点、性别、大运或流年所需信息时，相关判断必须降级或跳过。
- 用户请求第三方完整命盘且无授权时，系统不得输出完整个人分析。
- 用户只要求文化解释或轻量报告时，系统不得强行输出高风险内容。
- 新口径不得删除免责声明、来源假设、计算假设或证据说明。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST treat the nine user-provided 命理 PDFs as the initial classical evidence corpus for formal reports.
- **FR-002**: System MUST preserve each source title, file identity, extraction status, and review status before it can support report conclusions.
- **FR-003**: System MUST organize extracted knowledge into evidence units that can be traced by source, theme, rule family, and risk tier.
- **FR-004**: System MUST support report evidence for blind-school methods, 段氏口径, 五行十神, 格局旺衰, 用神忌神候选, 刑冲合害, 神煞, 大运流年, and high-risk signal materials when available.
- **FR-005**: System MUST allow formal reports to make substantive traditional judgments when they are backed by chart data and evidence units.
- **FR-006**: System MUST label conclusions as decided, candidate, weakly supported, disputed, or unavailable based on evidence sufficiency.
- **FR-007**: System MUST show a reader-facing evidence explanation for major conclusions in formal reports.
- **FR-008**: System MUST distinguish source-backed traditional claims from project-generated synthesis.
- **FR-009**: System MUST identify when a conclusion depends on a specific school, book, or rule family.
- **FR-010**: System MUST allow expanded judgment language including 格局候选, 旺衰倾向, 用神候选, 忌神候选, 应期线索, 风险信号, 成象, 破局, 得助, 受制, and 触发条件.
- **FR-011**: System MUST avoid unsupported conclusions when evidence is missing, unreadable, or disputed.
- **FR-012**: System MUST handle high-risk traditional content as evidence-backed risk signal analysis rather than guaranteed real-world outcome.
- **FR-013**: System MUST refuse or narrow requests for exact death timing, exact lifespan, medical diagnosis or treatment, legal instruction, psychological treatment, investment instruction, coercive matching, anxiety creation, or paid-remedy upsells.
- **FR-014**: System MUST include the expanded constitution stance in formal report safety and language review.
- **FR-015**: System MUST keep existing chart source disclosure and calculation assumption disclosure visible.
- **FR-016**: System MUST support regression validation for safe ordinary reports and high-risk narrowed reports.
- **FR-017**: System MUST preserve user-provided source files and generated source extracts without silently rewriting or deleting them.
- **FR-018**: System MUST provide a maintainable way to add new evidence sources later without changing report semantics.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MAY make substantive traditional 命理 judgments when they are backed by chart data and classical evidence.
- **SE-002**: System MUST present those judgments as traditional evidence analysis, not scientific proof, destiny enforcement, or guaranteed real-world outcomes.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source, key calculation assumptions, and evidence sources where reports depend on calendrical or school-specific rules.
- **SE-006**: System MAY discuss traditionally high-risk signals when source-backed, but MUST label uncertainty and MUST refuse guaranteed death timing, exact lifespan, medical diagnosis or treatment, legal instruction, psychological treatment, investment instruction, coercive matching, anxiety creation, and paid-remedy upsells.

### Key Entities *(include if feature involves data)*

- **Classical Source**: A source book or PDF in the evidence corpus, including title, file identity, extraction status, review status, and scope notes.
- **Evidence Unit**: A reviewable rule, passage summary, or principle distilled from a source, tagged by theme, rule family, risk tier, and source reference.
- **Rule Family**: A category of traditional analysis such as 五行十神, 格局旺衰, 用神忌神, 刑冲合害, 盲派象法, 神煞, 大运流年, or 高风险信号.
- **Evidence Trace**: The link between a report conclusion and the evidence units, chart facts, and assumptions that support it.
- **Risk Tier**: A classification that separates ordinary analysis, sensitive life-domain analysis, and high-risk signal analysis.
- **Conclusion Strength**: A report-facing status such as decided, candidate, weakly supported, disputed, or unavailable.
- **Expanded Constitution Profile**: The governance stance that permits source-backed formal traditional judgments while blocking absolute, coercive, or professional-advice outputs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the nine initial PDFs are represented as source entries with title, file identity, extraction status, and review status.
- **SC-002**: At least 80% of report major conclusions in safe formal examples include a visible evidence trace or an explicit unavailable/disputed explanation.
- **SC-003**: Safe formal reports can include at least six expanded judgment families: 格局候选, 旺衰倾向, 用神候选, 十神组合, 刑冲合害, and 大运流年主题.
- **SC-004**: 100% of high-risk examples are either narrowed into traditional risk signal analysis or refused when they request exact outcomes or professional advice.
- **SC-005**: 0 generated formal reports in the test suite contain prohibited absolute destiny phrases.
- **SC-006**: 100% of formal reports retain disclaimer, chart source disclosure, calculation assumptions, and evidence explanation.
- **SC-007**: A maintainer can inspect a generated report and identify the source family behind each major conclusion without reading implementation code.
- **SC-008**: Adding a future source book can be validated without changing the public report contract.

## Assumptions

- The initial source corpus consists of the nine PDF files provided in the project root on 2026-05-27.
- The corpus is allowed to become formal report evidence, including books that discuss high-risk traditional topics.
- Source passages should be summarized into evidence units rather than copied wholesale into reports.
- Existing birth-data validation and chart calculation disclosure remain required.
- Existing report formats may evolve, but formal reports must remain reviewable and source-aware.
- The expanded constitution profile supersedes prior specs where they conflict, but existing tests should be intentionally updated rather than silently removed.
