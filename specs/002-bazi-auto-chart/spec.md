# Feature Specification: 八字自动排盘层 MVP

**Feature Branch**: `002-bazi-auto-chart`

**Created**: 2026-05-17

**Status**: Draft

**Input**: User description: "在现有八字报告引擎基础上新增自动排盘层。第一版只支持公历生日、出生时间和中国标准时间，不做真太阳时、农历输入或海外时区。系统需要同时提供单独排盘 JSON 和一键排盘生成 Markdown 报告。自动排盘结果采用保守可信度，报告中必须标明由本引擎自动计算且未人工复核。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Calculate Chart From Birth Profile (Priority: P1)

As a user with complete公历 birth information, I want the system to calculate a structured八字 chart so I no longer need to manually supply the four pillars before using the report engine.

**Why this priority**: This is the core new value. Without automatic chart calculation, the previous MVP still depends on externally verified chart data.

**Independent Test**: Can be fully tested by submitting a complete公历 birth profile and verifying that the system returns a complete chart object with four pillars, visible source assumptions, and medium confidence.

**Acceptance Scenarios**:

1. **Given** a complete公历 birth profile with date, time, birthplace, gender, and focus topic, **When** the user requests chart calculation, **Then** the system returns a structured chart with year, month, day, and hour pillars.
2. **Given** a calculated chart is returned, **When** the user inspects its source details, **Then** the system states that the chart was automatically calculated, not manually verified.
3. **Given** a calculated chart is returned, **When** the user inspects assumptions, **Then** the system shows公历 input, China standard time, solar-term boundary assumptions, no true-solar-time adjustment, and medium confidence.

---

### User Story 2 - Generate Report Directly From Birth Profile (Priority: P2)

As a user, I want to submit birth information and receive a full Markdown report in one step so I can use the existing report experience without first handling chart JSON myself.

**Why this priority**: This completes the user-facing path from birth profile to report, while reusing the existing report safety and structure.

**Independent Test**: Can be fully tested by submitting a complete safe birth profile and verifying that the output is a complete Markdown report containing required sections and automatic-calculation source disclosure.

**Acceptance Scenarios**:

1. **Given** a complete safe公历 birth profile, **When** the user requests an automatic report, **Then** the system calculates a chart and returns a Markdown report.
2. **Given** an automatic report is generated, **When** the user reads the report, **Then** the report includes the same required sections as existing full reports.
3. **Given** an automatic report is generated, **When** the user reads the source and assumptions section, **Then** the report clearly states the chart was automatically calculated and not manually reviewed.

---

### User Story 3 - Refuse Unsupported Or Unsafe Inputs (Priority: P3)

As a user, I want clear feedback when my input is incomplete, unsupported, invalid, or unsafe so the system does not silently produce a misleading chart or report.

**Why this priority**: Automatic calculation increases the risk of false confidence. The system must keep the calculation boundary transparent and refuse unsafe or unsupported cases.

**Independent Test**: Can be fully tested by submitting incomplete birth profiles, non公历 calendar types, invalid dates or times, and red-line focus topics, then verifying that no full chart/report is emitted.

**Acceptance Scenarios**:

1. **Given** a birth profile is missing required fields, **When** the user requests chart calculation or an automatic report, **Then** the system refuses the full result and lists missing fields.
2. **Given** the calendar type is农历 or otherwise unsupported, **When** the user requests chart calculation, **Then** the system returns a clear unsupported-calendar response.
3. **Given** the date or time format is invalid, **When** the user requests chart calculation, **Then** the system returns a clear input error instead of a traceback or partial chart.
4. **Given** the focus topic triggers a safety red line, **When** the user requests an automatic report, **Then** the system returns a safety review response instead of a formal report.

### Edge Cases

- Birth date is invalid, such as a nonexistent calendar date.
- Birth time is invalid, out of range, missing minutes, or not in `HH:MM` form.
- Calendar type is农历, mixed, unknown, or omitted.
- Birthplace is present but vague; first version keeps it for display and assumptions, not location calculation.
- Birth time is near a solar-term boundary; the output must still disclose that first version does not apply true solar time.
- User asks a red-line focus topic such as寿命, death timing, major disaster, deterministic matching, professional advice, or paid remedy.
- The calculation source cannot produce a complete four-pillar chart.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept complete公历 birth profiles for automatic chart calculation.
- **FR-002**: System MUST reject full chart calculation when required birth-profile fields are missing or blank.
- **FR-003**: System MUST reject unsupported calendar types in this version, including农历 input.
- **FR-004**: System MUST validate birth date and birth time formats before producing a chart.
- **FR-005**: System MUST produce a chart containing exactly four pillars: year, month, day, and hour.
- **FR-006**: System MUST preserve the submitted birth profile in the calculated chart result.
- **FR-007**: System MUST expose automatic chart source details, including that the result is automatically calculated and not manually verified.
- **FR-008**: System MUST expose calculation assumptions for公历 input, China standard time, solar-term boundaries, and no true-solar-time adjustment.
- **FR-009**: System MUST mark automatically calculated chart confidence as medium, not high.
- **FR-010**: Users MUST be able to request chart-only output from a complete supported birth profile.
- **FR-011**: Users MUST be able to request a full Markdown report directly from a complete supported birth profile.
- **FR-012**: Automatic reports MUST reuse the existing report structure, source disclosure, disclaimer, glossary, action suggestions, and ethics reminder.
- **FR-013**: Automatic reports MUST refuse output when intake validation or safety review fails.
- **FR-014**: System MUST return stable user-facing errors for invalid input or calculation failure, without exposing internal tracebacks.
- **FR-015**: System MUST include at least two fixed reference cases for regression checking of automatic chart calculation behavior.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MUST present outputs as cultural interpretation and self-reflection, not scientific prediction or fate verdict.
- **SE-002**: System MUST refuse or safely redirect requests involving lifespan, death timing, major disaster prediction, deterministic marriage matching, medical advice, legal advice, psychological treatment, investment instruction, unauthorized third-party full-chart analysis, anxiety creation, or paid remedy upsells.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source and key calculation assumptions where reports depend on calendrical or school-specific rules.
- **SE-006**: System MUST state that automatic charts are not manually reviewed, so users can distinguish calculated output from externally verified chart data.

### Key Entities *(include if feature involves data)*

- **Automatic Chart Request**: A complete birth-profile request using公历 date, birth time, birthplace, gender, and focus topic.
- **Calculated Chart**: A structured八字 chart produced from a supported birth profile, containing four pillars and existing chart summary fields.
- **Automatic Chart Source**: Provenance and assumptions for an automatically calculated chart, including automatic origin, no manual review, China standard time, no true solar time, and medium confidence.
- **Calculation Error**: A stable user-facing response for unsupported calendars, invalid date/time formats, incomplete input, or inability to produce a complete chart.
- **Automatic Report**: A Markdown report generated by calculating a chart first and then using the existing report engine.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid complete公历 sample profiles in the test set produce a chart with exactly four pillars.
- **SC-002**: 100% of automatic chart outputs include visible source details and medium confidence.
- **SC-003**: 100% of automatic reports include automatic-calculation disclosure in the source and assumptions section.
- **SC-004**: 100% of unsupported calendar, invalid date, invalid time, and incomplete input cases return a stable error without a traceback.
- **SC-005**: 100% of red-line focus-topic cases return a safety review response instead of a formal automatic report.
- **SC-006**: At least two fixed reference birth-profile cases remain stable across regression runs unless an intentional chart-calculation change is documented.
- **SC-007**: A user can complete the path from complete birth profile to Markdown report in one command without manually editing chart JSON.

## Assumptions

- First version supports only公历 input.
- First version treats all supported birth times as China standard time `UTC+08:00`.
- First version does not apply true solar time.
- First version does not parse longitude or latitude from birthplace.
- Birthplace remains required because it is part of the report card and calculation assumptions, even though it does not affect first-version time correction.
- Automatically calculated charts are medium confidence until manually reviewed or verified by a later workflow.
- Existing report safety checks, disclaimer rules, and Markdown report structure remain authoritative for automatic reports.
- Automatic calculation may provide conservative summaries for deeper strength, pattern, useful-god, and luck-cycle fields; those summaries must avoid deterministic claims.
