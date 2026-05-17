# Feature Specification: 报告分层阅读体验优化

**Feature Branch**: `004-report-readability`

**Created**: 2026-05-17

**Status**: Draft

**Input**: User description: "让当前八字 Markdown 报告更有层次感。采用分层阅读版：先快速导读，再基础资料，再结构观察，再解读边界，再行动反思。不新增命理判断、不改变 CLI 用法、不改变安全边界。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quickly Understand The Report Path (Priority: P1)

As a user reading a generated Bazi report, I want a short quick guide near the top so I can understand what to notice first before reading the full report.

**Why this priority**: The current report includes useful sections, but users must read through the whole Markdown to infer the main path. A quick guide creates the first layer of understanding.

**Independent Test**: Can be fully tested by generating a safe report and verifying that the Markdown includes a `快速导读` section with three to five concise bullets that summarize source confidence, structure observation, interpretation boundary, and the user's focus topic when available.

**Acceptance Scenarios**:

1. **Given** a complete safe chart, **When** the user generates a Markdown report, **Then** the report includes `## 快速导读` before the detailed reading layers.
2. **Given** a complete safe chart, **When** the user reads `快速导读`, **Then** they can see the report source status, one primary structure observation, one boundary reminder, and one focus-topic reflection cue.
3. **Given** a report has a quick guide, **When** safety review scans the generated report, **Then** the guide remains allowed and contains no absolute destiny language.

---

### User Story 2 - Read The Report By Layers (Priority: P2)

As a beginner reader, I want the report to be grouped into clear reading layers so I can move from factual information to interpretation and then reflection without getting lost.

**Why this priority**: Layering is the main user-requested improvement. It makes the report easier to scan without changing the underlying interpretation rules.

**Independent Test**: Can be fully tested by rendering a safe report and verifying that the Markdown contains the four reading layers in order: `第一层：基础资料`, `第二层：结构观察`, `第三层：解读边界`, and `第四层：行动反思`.

**Acceptance Scenarios**:

1. **Given** a generated report, **When** the user scans the headings, **Then** they see the four layers in a logical order.
2. **Given** the user opens the `第一层：基础资料`, **When** they read it, **Then** it contains chart card and source assumptions.
3. **Given** the user opens the `第二层：结构观察`, **When** they read it, **Then** it contains four-pillar, five-elements, ten-god, structure, and day-master observation content.
4. **Given** the user opens the `第三层：解读边界`, **When** they read it, **Then** it clearly states that the feature does not decide pattern, useful god, luck cycles, auspiciousness, or fate outcomes.
5. **Given** the user opens the `第四层：行动反思`, **When** they read it, **Then** it contains reflection wording tied to the user's safe focus topic.

---

### User Story 3 - Distinguish Observation, Basis, Boundary, And Prompt (Priority: P3)

As a cautious reader, I want important sections to label what is an observation, what supports it, what the boundary is, and what I can reflect on next, so I do not mistake a structural note for a fate verdict.

**Why this priority**: This improves comprehension and safety, but it depends on the layered report structure existing first.

**Independent Test**: Can be fully tested by generating a report and verifying that important interpretation sections include plain labels such as `观察`, `依据`, `边界`, or `提示` where appropriate.

**Acceptance Scenarios**:

1. **Given** the report includes structure interpretation, **When** the user reads the section, **Then** the wording separates observation from boundary language.
2. **Given** the report includes action reflection, **When** the user reads the section, **Then** suggestions are framed as prompts or复盘 cues, not outcomes.
3. **Given** the report includes factual source assumptions, **When** the user reads that section, **Then** it stays factual and is not forced into every label.

### Edge Cases

- A report is generated from automatically calculated chart data with medium confidence.
- A report is generated from externally verified chart data.
- A chart contains unknown or sparse interpretation signals.
- A focus topic is safe but empty or generic.
- A focus topic triggers a safety red line; the system must still return safety JSON instead of Markdown.
- A reader only skims the quick guide; the quick guide must not overstate certainty.
- Boundary language must be visible without being repeated so often that the report becomes noisy.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST add a `快速导读` section to every complete, safe Markdown report.
- **FR-002**: The quick guide MUST contain three to five concise bullet points.
- **FR-003**: The quick guide MUST include source or confidence status, one primary structure observation, one interpretation boundary reminder, and a focus-topic reflection cue when a safe focus topic is available.
- **FR-004**: System MUST organize the detailed Markdown report into four reading layers: `第一层：基础资料`, `第二层：结构观察`, `第三层：解读边界`, and `第四层：行动反思`.
- **FR-005**: `第一层：基础资料` MUST include the existing chart card and source assumptions.
- **FR-006**: `第二层：结构观察` MUST include the existing four-pillar, five-elements, ten-god, structure, and day-master observation content.
- **FR-007**: `第三层：解读边界` MUST make the current interpretation boundaries easy to find, including no pattern verdict, no useful-god verdict, and no luck-cycle or annual-cycle conclusion.
- **FR-008**: `第四层：行动反思` MUST include the existing reflection and action guidance tied to the user's safe focus topic.
- **FR-009**: Important interpretation sections SHOULD use clear labels such as `观察`, `依据`, `边界`, and `提示` when those labels make the section easier to understand.
- **FR-010**: System MUST preserve existing CLI commands, flags, input JSON shapes, and refusal exit behavior.
- **FR-011**: System MUST preserve chart source disclosure and key calculation assumptions.
- **FR-012**: System MUST preserve the existing disclaimer and ethics reminder in every formal report.
- **FR-013**: System MUST avoid excessive repeated boundary text; each major boundary idea should appear clearly without being repeated in every section.
- **FR-014**: System MUST keep reports readable when interpretation signals are unknown, sparse, or missing by using limitation wording instead of guessing.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MUST present outputs as cultural interpretation and self-reflection, not scientific prediction or fate verdict.
- **SE-002**: System MUST refuse or safely redirect requests involving lifespan, death timing, major disaster prediction, deterministic marriage matching, medical advice, legal advice, psychological treatment, investment instruction, unauthorized third-party full-chart analysis, anxiety creation, or paid remedy upsells.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source and key calculation assumptions where reports depend on calendrical or school-specific rules.
- **SE-006**: The quick guide MUST be conservative because users may read only that section.
- **SE-007**: System MUST NOT introduce new pattern, useful-god, strength, luck-cycle, auspiciousness, or fate-outcome conclusions as part of readability changes.

### Key Entities *(include if feature involves data)*

- **Layered Report**: A Markdown report organized into quick guide, factual layer, structure observation layer, boundary layer, and reflection layer.
- **Quick Guide**: A short bullet summary near the top of the report that helps the user understand the report path before reading details.
- **Reading Layer**: A named group of related report content that separates factual inputs, structure observations, interpretation boundaries, and reflection prompts.
- **Section Label**: A plain-language marker such as `观察`, `依据`, `边界`, or `提示` that tells the reader what role a paragraph serves.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of complete, safe Markdown reports in the test suite include `## 快速导读`.
- **SC-002**: 100% of complete, safe Markdown reports in the test suite include the four reading layers in the required order.
- **SC-003**: 100% of complete, safe Markdown reports in the test suite keep source disclosure visible under the factual reading layer.
- **SC-004**: 100% of complete, safe Markdown reports in the test suite keep interpretation boundary language visible under the boundary reading layer.
- **SC-005**: 100% of red-line focus-topic cases continue to return safety JSON instead of a formal Markdown report.
- **SC-006**: 0 generated formal reports in the test suite contain prohibited absolute destiny phrases.
- **SC-007**: A user can still generate reports through the existing supported commands without supplying new options or input fields.
- **SC-008**: At least two report-generation paths, automatic chart calculation and external chart input, produce the layered Markdown structure.

## Assumptions

- The feature is Markdown-only and does not introduce a web UI.
- Existing report content remains the source of truth; this feature reorganizes and lightly rewrites for readability.
- Existing safety review remains mandatory before formal report output.
- Existing interpretation rules from feature 003 remain unchanged.
- Layer labels are intended to help beginner readers and may use plain Chinese headings rather than technical terminology.
