# Feature Specification: 八字报告白话表达优化

**Feature Branch**: `005-plain-language-report`

**Created**: 2026-05-18

**Status**: Draft

**Input**: User description: "把 004 分层后的 Markdown 报告做成小白友好的白话表达：翻译机器字段，润色关键句，让报告不像程序输出，但不改变算法、CLI 或安全边界。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read Without Machine Labels (Priority: P1)

As a beginner reading a generated Bazi Markdown report, I want source, confidence, calendar, and pillar labels to appear in plain Chinese instead of internal machine strings, so I can understand the report without knowing the system's data model.

**Why this priority**: The report is already layered, but raw values such as `auto_calculated`, `medium`, `gregorian`, `year`, `month`, `day`, and `hour` still make it feel like program output. Removing that friction is the core value of this feature.

**Independent Test**: Generate a complete safe Markdown report and verify that reader-facing text uses Chinese labels for source type, confidence level, calendar type, and four-pillar names while selected raw machine labels are absent from the report body.

**Acceptance Scenarios**:

1. **Given** a safe report generated from automatic chart calculation, **When** the user reads the source and quick guide sections, **Then** they see reader-facing wording such as "系统自动排盘" and "中等可信度" instead of raw source and confidence values.
2. **Given** a safe report generated from external verified chart data, **When** the user reads the source section, **Then** they see reader-facing wording that clearly indicates the chart came from externally verified data.
3. **Given** any complete safe report, **When** the user reads the four-pillar summary, **Then** the pillar rows use `年柱`, `月柱`, `日柱`, and `时柱` rather than `year`, `month`, `day`, and `hour`.

---

### User Story 2 - Read Smoother Guidance (Priority: P2)

As a beginner reader, I want the quick guide and action-reflection text to sound like a human-readable report rather than raw metadata or rigid system notes, so I can follow the report path more naturally.

**Why this priority**: Plain labels solve the most visible problem, but the report still needs a more polished reading experience in the sections users are most likely to skim first.

**Independent Test**: Generate a complete safe Markdown report and verify that the quick guide remains concise, uses plain guidance language, and still avoids deterministic or outcome-promising wording.

**Acceptance Scenarios**:

1. **Given** a complete safe report, **When** the user reads `## 快速导读`, **Then** the bullets explain source status, structure signal, interpretation boundary, and safe focus-topic reflection in plain Chinese.
2. **Given** a complete safe report with concentrated element signals, **When** the user reads the structure-related wording, **Then** the wording says the signals are observation material and does not present them as a final strength model or fate conclusion.
3. **Given** a complete safe report with a safe focus topic, **When** the user reads action reflection, **Then** the suggestions are framed as reflection prompts or review cues rather than promised outcomes.

---

### User Story 3 - Preserve Trust And Safety (Priority: P3)

As a cautious user, I want the friendlier wording to preserve the existing safety boundaries and source transparency, so the report does not become more certain just because it reads more smoothly.

**Why this priority**: This is a wording feature in a sensitive domain. Better language must not create new claims, stronger certainty, or hidden assumptions.

**Independent Test**: Run existing safe and unsafe report-generation flows and verify that source disclosure, disclaimer, ethics reminder, safety refusal JSON, and prohibited-phrase protections remain intact.

**Acceptance Scenarios**:

1. **Given** a focus topic that triggers a safety red line, **When** the user generates a report, **Then** the system still returns safety JSON instead of a Markdown report.
2. **Given** a complete safe report, **When** the user reads the formal report, **Then** the disclaimer, source assumptions, and ethics reminder remain visible.
3. **Given** a complete safe report, **When** safety language is checked, **Then** the report contains no absolute destiny phrases such as `必定`, `注定`, `一定会`, or `死定`.

### Edge Cases

- A report is generated from automatically calculated chart data with medium confidence.
- A report is generated from externally verified chart data.
- A chart source or confidence value is unfamiliar or not yet mapped to a reader-facing phrase.
- A birth profile has an empty, unspecified, or non-informative gender value.
- A focus topic is empty, generic, or safely worded.
- A focus topic triggers a safety red line; the system must still return safety JSON instead of Markdown.
- Interpretation signals are unknown, sparse, or missing; the report must stay transparent instead of inventing meaning.
- A reader only skims the quick guide; that section must remain conservative and not overstate certainty.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every complete, safe Markdown report MUST use reader-facing Chinese wording for known chart source types.
- **FR-002**: Every complete, safe Markdown report MUST use reader-facing Chinese wording for known confidence levels.
- **FR-003**: Every complete, safe Markdown report MUST use reader-facing Chinese wording for known calendar types.
- **FR-004**: Every complete, safe Markdown report MUST label the four pillars as `年柱`, `月柱`, `日柱`, and `时柱`.
- **FR-005**: Every complete, safe Markdown report MUST avoid exposing selected raw machine labels in reader-facing body text, including `auto_calculated`, `external_verified`, `medium`, `gregorian`, `year：`, `month：`, `day：`, and `hour：`.
- **FR-006**: Unknown or unmapped source, confidence, calendar, gender, or pillar values MUST be handled conservatively without guessing hidden meaning.
- **FR-007**: The quick guide MUST remain three to five concise bullets and MUST use plain Chinese guidance language.
- **FR-008**: The quick guide MUST continue to cover source or confidence status, a primary structure observation, an interpretation boundary reminder, and a safe focus-topic reflection cue when available.
- **FR-009**: Structure wording MUST continue to frame element and ten-god signals as observation material, not as complete strength analysis or fate verdict.
- **FR-010**: Action-reflection wording MUST remain tied to the user's safe focus topic and MUST be framed as reflection or review prompts rather than promised outcomes.
- **FR-011**: The layered Markdown heading order introduced in feature 004 MUST remain unchanged.
- **FR-012**: Existing CLI commands, flags, input JSON shapes, refusal exit behavior, and safety JSON shape MUST remain unchanged.
- **FR-013**: Existing chart source disclosure and key calculation assumptions MUST remain visible in every complete, safe report.
- **FR-014**: The feature MUST NOT introduce new pattern verdicts, useful-god verdicts, strength verdicts, luck-cycle or annual-cycle judgments, auspiciousness claims, or real-world outcome predictions.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MUST present outputs as cultural interpretation and self-reflection, not scientific prediction or fate verdict.
- **SE-002**: System MUST refuse or safely redirect requests involving lifespan, death timing, major disaster prediction, deterministic marriage matching, medical advice, legal advice, psychological treatment, investment instruction, unauthorized third-party full-chart analysis, anxiety creation, or paid remedy upsells.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source and key calculation assumptions where reports depend on calendrical or school-specific rules.
- **SE-006**: Friendlier wording MUST NOT increase certainty, imply fate outcomes, or weaken existing interpretation boundaries.

### Key Entities *(include if feature involves data)*

- **Reader-Facing Label**: A human-readable phrase shown in the report instead of an internal source, confidence, calendar, pillar, or placeholder value.
- **Plain-Language Report Wording**: Existing report content rewritten lightly so ordinary readers can understand it without losing source transparency or safety boundaries.
- **Machine-Facing Value**: A raw internal value that may be valid for data exchange but should not appear as-is in final reader-facing Markdown.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of complete safe Markdown reports in the test suite show reader-facing Chinese labels for known source type, confidence level, calendar type, and pillar names.
- **SC-002**: 100% of complete safe Markdown reports in the test suite do not expose the selected raw machine labels listed in FR-005 in reader-facing body text.
- **SC-003**: 100% of complete safe Markdown reports in the test suite keep the feature 004 layered heading order.
- **SC-004**: 100% of complete safe Markdown reports in the test suite keep chart source disclosure and key calculation assumptions visible.
- **SC-005**: 100% of red-line focus-topic cases in the test suite continue to return safety JSON instead of Markdown.
- **SC-006**: 0 generated formal reports in the test suite contain prohibited absolute destiny phrases.
- **SC-007**: At least two report-generation paths, automatic chart calculation and external chart input, produce plain-language Markdown output without requiring new user options.

## Assumptions

- The feature is Markdown-only and does not introduce a web UI or export format.
- Existing report content and interpretation rules remain the source of truth; this feature changes wording, not meaning.
- Existing safety review remains mandatory before formal report output.
- Known reader-facing label mappings are enough for the current supported examples; unfamiliar future values should be disclosed conservatively rather than interpreted.
- The target reader is a beginner who benefits from plain Chinese labels while still seeing core Bazi terms.
