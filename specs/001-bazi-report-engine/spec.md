# Feature Specification: 八字知识与报告引擎 MVP

**Feature Branch**: `001-bazi-report-engine`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "建立命理知识与报告引擎，先聚焦八字，生成结构化 Markdown 报告，并内置伦理红线、非绝对化语言、排盘规则透明和缺失输入处理。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validate Birth Inputs (Priority: P1)

As a user seeking a八字 report, I provide birth information and a focus topic so the system can determine whether a full report can be generated.

**Why this priority**: Without complete and trustworthy input, any report would be misleading.

**Independent Test**: Can be fully tested by submitting complete and incomplete birth profiles and verifying that complete profiles proceed while incomplete profiles receive a precise missing-field response.

**Acceptance Scenarios**:

1. **Given** a user provides calendar type, birth date, birth time, birthplace, gender, and focus topic, **When** the intake is checked, **Then** the system accepts the profile as report-ready.
2. **Given** a user omits birth time or birthplace, **When** the intake is checked, **Then** the system refuses full report generation and lists the missing fields.
3. **Given** a user is uncertain whether the date is公历 or农历, **When** the intake is checked, **Then** the system asks for clarification before producing a full report.

---

### User Story 2 - Produce a Structured 八字 Report (Priority: P2)

As a user with validated birth data or a verified八字 chart, I want a structured Markdown report that explains my八字 pattern in clear, non-deterministic language.

**Why this priority**: The report is the core user-visible value of the MVP.

**Independent Test**: Can be fully tested by providing a validated chart and verifying that the output contains every required section, disclaimer, visible assumptions, and traceable conclusions.

**Acceptance Scenarios**:

1. **Given** validated chart data is available, **When** the user requests a full report, **Then** the system generates a Markdown report with disclaimer,命造卡片,四柱摘要,五行摘要,十神摘要,旺衰/格局/用神候选,大运流年概览,行动建议,术语简注, and伦理边界提醒.
2. **Given** a report includes a major conclusion, **When** the report is reviewed, **Then** the conclusion is tied to an input, intermediate result, or explicit assumption.
3. **Given** a calculation rule or school interpretation is uncertain, **When** the report discusses that area, **Then** the uncertainty is stated instead of presented as a final fate verdict.

---

### User Story 3 - Enforce Ethical Boundaries (Priority: P3)

As a user who asks a sensitive or unsafe question, I want the system to protect me from fatalistic, coercive, or professional-advice claims while still offering a safe alternative frame.

**Why this priority**: Ethical handling is required by the project constitution and protects the user experience.

**Independent Test**: Can be fully tested by submitting red-line prompts and verifying that the system refuses or redirects without generating prohibited claims.

**Acceptance Scenarios**:

1. **Given** a user asks about lifespan, death timing, or major disaster prediction, **When** the request is processed, **Then** the system refuses that prediction and offers a safer reflection-oriented alternative.
2. **Given** a user asks whether two people are destined to marry, **When** the request is processed, **Then** the system refuses deterministic matching and offers to discuss the user's own relationship patterns.
3. **Given** a generated report contains absolute language such as 必定, 注定, 一定会, or 死定, **When** the safety review runs, **Then** the report is blocked or rewritten before delivery.

---

### Edge Cases

- Birth time is unknown, approximate, or given only as a time range.
- Birthplace is missing, ambiguous, or not specific enough for location-sensitive assumptions.
- User mixes公历 and农历 dates in one request.
- User asks for a full chart of an unauthorized third party.
- User requests medical, legal, psychological, investment, or paid remedy advice.
- Chart data and birth data conflict.
- Report generation has enough data for a brief intake summary but not enough for a full report.
- Multiple八字 schools would reasonably interpret a structure differently.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST collect or receive calendar type, birth date, birth time, birthplace, gender, and focus topic before full report generation.
- **FR-002**: System MUST identify missing or ambiguous required fields and return a clear completion request instead of generating a full report.
- **FR-003**: System MUST support a validated八字 chart object containing four pillars, five-element summary, ten-god summary, hidden stems, strength assessment, pattern candidates, useful-god candidates, and luck-cycle summary.
- **FR-004**: System MUST expose chart data source and assumptions in every full report.
- **FR-005**: System MUST generate a structured Markdown report with all required report sections.
- **FR-006**: System MUST keep calculation facts, interpretive conclusions, and report prose distinguishable in the output or its underlying report structure.
- **FR-007**: System MUST mark uncertain or school-dependent conclusions as uncertain.
- **FR-008**: System MUST provide action-oriented suggestions for each major interpretive section.
- **FR-009**: System MUST include a plain-language glossary for specialized terms used in the report.
- **FR-010**: System MUST support brief safe responses when the input is insufficient for a full report.
- **FR-011**: System MUST avoid retaining identifiable birth data unless the user explicitly requests storage in a later feature.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MUST present outputs as cultural interpretation and self-reflection, not scientific prediction or fate verdict.
- **SE-002**: System MUST refuse or safely redirect requests involving lifespan, death timing, major disaster prediction, deterministic marriage matching, medical advice, legal advice, psychological treatment, investment instruction, unauthorized third-party full-chart analysis, anxiety creation, or paid remedy upsells.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source and key calculation assumptions where reports depend on calendrical or school-specific rules.

### Key Entities *(include if feature involves data)*

- **Birth Profile**: User-provided birth context, including calendar type, birth date, birth time, birthplace, gender, and focus topic.
- **Chart Source**: Provenance and assumptions for chart data, including whether values were supplied, externally verified, or produced by a future calculation layer.
- **Bazi Chart**: Structured八字 data, including four pillars, hidden stems, five-element summary, ten-god summary, strength assessment, pattern candidates, useful-god candidates, and luck-cycle summary.
- **Interpretation Finding**: A traceable conclusion with supporting inputs, uncertainty level, and safe-language rendering.
- **Report**: The generated Markdown artifact containing required sections, disclaimer, assumptions, findings, suggestions, glossary, and ethics reminder.
- **Safety Review Result**: Outcome of checking red-line requests, disclaimer presence, absolute language, and professional-advice boundaries.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of complete birth profiles are accepted for full-report preparation, and 100% of incomplete profiles receive a missing-field response naming the missing information.
- **SC-002**: 100% of full reports contain all required sections: disclaimer,命造卡片,四柱摘要,五行摘要,十神摘要,结构分析,阶段概览,行动建议,术语简注, and伦理边界提醒.
- **SC-003**: 100% of full reports state chart source and calculation assumptions visible to the reader.
- **SC-004**: 100% of red-line requests in the safety test set are refused or redirected without prohibited claims.
- **SC-005**: 0 generated formal reports contain the prohibited absolute phrases 必定, 注定, 一定会, or 死定.
- **SC-006**: At least 90% of major report conclusions in review samples can be traced to input data, intermediate chart data, or an explicit assumption.
- **SC-007**: A reader can identify the next suggested action in every major interpretive section without needing external explanation.

## Assumptions

- The MVP focuses only on八字 and does not include紫微斗数, 六爻, Web UI, account management, payment, HTML export, PNG export, or PDF export.
- The MVP may use manually supplied or externally verified chart data while preserving a clear boundary for a future automatic calculation layer.
- Birth data is treated as sensitive and is not stored by default.
- Markdown is the first report format because it is readable, reviewable, and easy to transform later.
- The system speaks in Chinese-first report language, with technical terms explained in plain Chinese.
