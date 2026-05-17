# Feature Specification: 八字基础结构解读规则层

**Feature Branch**: `003-bazi-interpretation-rules`

**Created**: 2026-05-17

**Status**: Draft

**Input**: User description: "在现有自动排盘和 Markdown 报告基础上，新增基础结构解读规则层。第一版只做五行分布、日主基础说明、十神位置摘要和保守结构观察，让报告更像可读的命理结构分析；不做格局定论、用神定论、大运流年、吉凶断语或专业建议。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read Basic Structure In The Report (Priority: P1)

As a user who has generated a八字 report, I want the report to explain the chart's basic structure in plain language so I can understand more than just the raw four pillars.

**Why this priority**: The current report can display chart facts, but its deeper sections are still broad and template-like. Basic structure interpretation is the main value of this feature.

**Independent Test**: Can be fully tested by generating a safe report from a known chart and verifying that the report includes five-elements distribution, day-master explanation, ten-gods placement summary, and conservative structure observations.

**Acceptance Scenarios**:

1. **Given** a complete safe chart, **When** the user generates a report, **Then** the report explains the observed five-elements distribution instead of showing only generic placeholder text.
2. **Given** a complete safe chart, **When** the user reads the day-master section, **Then** the report identifies the day master as the observation center without claiming it determines fate.
3. **Given** a complete safe chart, **When** the user reads the ten-gods section, **Then** the report summarizes which ten-gods appear in which pillars.

---

### User Story 2 - See Clear Interpretation Boundaries (Priority: P2)

As a cautious user, I want the report to clearly say what the basic rule layer does and does not conclude so I do not mistake structure observations for destiny verdicts.

**Why this priority**: Interpretation rules can easily create false confidence. The report must remain conservative, transparent, and ethically bounded.

**Independent Test**: Can be fully tested by generating a report and verifying that it includes limitation language and does not contain prohibited deterministic phrases or unsupported conclusions.

**Acceptance Scenarios**:

1. **Given** a report with basic structure interpretation, **When** the user reads the structure analysis, **Then** the report states that the current layer only performs basic structure observation.
2. **Given** a report with basic structure interpretation, **When** the user reads pattern, useful-god, or luck-cycle related areas, **Then** the report does not present them as decided conclusions.
3. **Given** a report is generated for a safe topic, **When** safety review runs, **Then** the report remains allowed and contains no absolute destiny language.

---

### User Story 3 - Receive Practical Reflection Suggestions (Priority: P3)

As a user with a focus topic, I want the report to turn structure observations into practical reflection prompts so the output feels useful without pretending to predict events.

**Why this priority**: The report should help the user reflect and act, but this is secondary to producing accurate and bounded structure summaries.

**Independent Test**: Can be fully tested by generating a report with a safe focus topic and verifying that action suggestions are connected to observed structure while remaining non-deterministic.

**Acceptance Scenarios**:

1. **Given** a safe focus topic, **When** a report is generated, **Then** the action suggestions reference observable chart tendencies without promising outcomes.
2. **Given** a chart has concentrated or sparse element signals, **When** suggestions are generated, **Then** the report frames them as reflection prompts rather than fixed personality labels.

### Edge Cases

- A chart contains exactly four pillars but some pillar fields are blank or unknown.
- A chart has no hidden stems for one or more pillars.
- One element appears much more often than the others.
- One element does not appear in the available chart signals.
- A ten-god repeats across multiple pillars.
- A focus topic triggers a safety red line; the system must still refuse the formal report.
- The chart source is external verified rather than automatically calculated; basic interpretation should still respect the source disclosure.
- The report must avoid turning missing or sparse signals into deterministic deficiency claims.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a basic structure interpretation for every complete, safe chart used to produce a formal report.
- **FR-002**: System MUST summarize five-elements distribution from available pillar signals.
- **FR-003**: System MUST distinguish direct visible signals from supporting hidden-stem signals in user-facing wording or limitations.
- **FR-004**: System MUST identify the chart day master and explain that it is the observation center.
- **FR-005**: System MUST summarize ten-gods placement across the four pillars when ten-gods data is available.
- **FR-006**: System MUST identify repeated or sparse structure signals using neutral language.
- **FR-007**: System MUST include limitation language stating that this feature performs only basic structure observation.
- **FR-008**: System MUST NOT decide pattern, useful god, day-master strength verdict, luck cycles, annual cycles, auspiciousness, or fate outcomes in this feature.
- **FR-009**: System MUST keep existing report sections and source-disclosure behavior stable.
- **FR-010**: System MUST integrate basic interpretation into both reports generated from automatically calculated charts and reports generated from existing complete chart data.
- **FR-011**: System MUST provide practical reflection suggestions connected to the user's safe focus topic and observed chart structure.
- **FR-012**: System MUST handle incomplete or unknown interpretation signals with explicit limitation text instead of guessing.
- **FR-013**: System MUST refuse formal report output when existing intake or safety review fails.
- **FR-014**: System MUST keep user-facing errors stable and avoid internal tracebacks when interpretation cannot be produced from malformed chart data.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MUST present outputs as cultural interpretation and self-reflection, not scientific prediction or fate verdict.
- **SE-002**: System MUST refuse or safely redirect requests involving lifespan, death timing, major disaster prediction, deterministic marriage matching, medical advice, legal advice, psychological treatment, investment instruction, unauthorized third-party full-chart analysis, anxiety creation, or paid remedy upsells.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source and key calculation assumptions where reports depend on calendrical or school-specific rules.
- **SE-006**: System MUST avoid presenting element absence, repeated ten-gods, or structural concentration as fixed personality labels or inevitable events.

### Key Entities *(include if feature involves data)*

- **Basic Interpretation Summary**: A structured summary of five-elements distribution, day-master explanation, ten-gods placement, structure observations, limitations, and reflection suggestions.
- **Five-Elements Distribution**: A count or qualitative summary of element signals observed from chart pillars and hidden stems.
- **Day-Master Explanation**: A short explanation of the day master as the chart's observation center.
- **Ten-Gods Placement Summary**: A readable summary of which ten-gods appear in which pillars.
- **Structure Observation**: A conservative statement about repeated, concentrated, sparse, or missing chart signals.
- **Interpretation Limitation**: Text that states what the basic rule layer does not determine.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of safe reports generated from complete test charts include a non-empty five-elements distribution summary.
- **SC-002**: 100% of safe reports generated from complete test charts include a day-master explanation.
- **SC-003**: 100% of safe reports generated from complete test charts include a ten-gods placement summary when ten-gods data is present.
- **SC-004**: 100% of safe reports include limitation language that excludes pattern, useful-god, and luck-cycle determination for this feature.
- **SC-005**: 100% of red-line focus-topic cases continue to return a safety response instead of a formal interpreted report.
- **SC-006**: 0 generated formal reports in the test suite contain prohibited absolute destiny phrases.
- **SC-007**: At least two fixed chart examples produce stable interpretation summaries across regression runs unless an intentional rule change is documented.
- **SC-008**: A user can generate a report from the existing supported paths without supplying any new options or extra input fields.

## Assumptions

- Existing chart calculation and chart-source disclosure remain authoritative.
- Existing report sections remain the public report shape.
- The first version uses only data already present in the chart; it does not request new user input.
- The first version treats hidden stems as supporting observation signals, not as a complete strength model.
- The first version does not attempt to rank schools, settle pattern disputes, or decide useful god.
- Existing safety review and disclaimer rules remain mandatory for every formal report.
