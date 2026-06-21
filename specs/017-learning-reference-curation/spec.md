# Feature Specification: Learning Reference Curation

**Feature Branch**: `017-learning-reference-curation`

**Created**: 2026-05-31

**Status**: Draft

**Input**: User description: "尽快把新增的资料整理好，变成本项目的学习参考数据；第一批基于 016 的 extraction-ready tasks，backlog 只做前置处理，不直接抽取；不要移动、删除、转换或改写外部原始/准备资料。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Learning Reference Notes From Ready Tasks (Priority: P1)

A maintainer wants to turn selected ready 016 extraction tasks into concise learning reference notes, so the project has readable source-backed guidance before any formal evidence promotion.

**Why this priority**: This is the fastest path from the newly organized materials into reusable project knowledge without waiting for every backlog item to be resolved.

**Independent Test**: Can be tested by opening the current learning reference notes for the selected ready tasks and confirming each note names its source, queue trace, locator boundary, target rule families, summary points, limitations, and candidate-intake readiness.

**Acceptance Scenarios**:

1. **Given** a ready 016 extraction task for Northeast Blind Peak, **When** the maintainer reviews the generated learning reference note, **Then** the note identifies the source trace, target rule families, overlap warnings, safety boundary, and candidate-ready learning points without copying long source passages.
2. **Given** a ready 016 extraction task for Mingli True Formula Teacher, **When** the maintainer reviews the generated learning reference note, **Then** the note identifies source trace, target rule families, locator requirements, uncertainty notes, and candidate-ready learning points without creating formal evidence.

---

### User Story 2 - Convert Approved Learning Points Into Candidate Extracts (Priority: P2)

A maintainer wants to convert selected learning points into 013 candidate extracts, so the project can review them before they ever become formal report evidence.

**Why this priority**: Learning notes are useful, but the project needs structured candidate records to support review, duplicate handling, and later promotion.

**Independent Test**: Can be tested by loading 013 source-intake data and confirming new candidates trace to existing source materials, use concise extracted meanings, carry limitations, avoid duplicate candidates, and remain outside formal evidence counts.

**Acceptance Scenarios**:

1. **Given** a learning point from a ready task with a source material link, **When** it is accepted for candidate intake, **Then** a pending candidate record exists with locator, proposed rule family, risk tier, limitations, and source trace.
2. **Given** a learning point that overlaps an existing pending, rejected, approved, or blocked 013 candidate, **When** candidate intake is prepared, **Then** the feature records reuse or duplicate-avoidance guidance instead of silently creating a redundant candidate.

---

### User Story 3 - Preserve Backlog As Prerequisite Work (Priority: P3)

A maintainer wants non-ready 016 backlog records to become actionable prerequisite work, so registration, risk review, and blocked-source issues are visible without being treated as learning reference data.

**Why this priority**: Backlog work matters, but forcing it into candidate extraction would blur readiness, safety, and evidence boundaries.

**Independent Test**: Can be tested by inspecting backlog action notes and confirming registration, risk-review, and blocked items have next actions, durable reasons, and no candidate extracts or formal evidence records.

**Acceptance Scenarios**:

1. **Given** the Markdown batch registration backlog, **When** prerequisite work is summarized, **Then** the action is source registration or alignment review, not candidate extraction.
2. **Given** the high-risk Blind Life Manual backlog, **When** prerequisite work is summarized, **Then** the action is risk-boundary review, not routine extraction.
3. **Given** the blocked Blind School Secret backlog, **When** prerequisite work is summarized, **Then** the action preserves access and quotation blockers, not source-derived learning content.

---

### Edge Cases

- Existing 013 candidates may already cover the same source material and rule family; the feature must surface reuse or duplicate warnings before adding candidates.
- Some notes may have only file-level or section-level locator information; candidate intake must keep locator requirements visible instead of inventing precise anchors.
- High-risk or sensitive material may be useful for learning but unsafe for direct report claims; the feature must require uncertainty, limitation, and refusal-boundary language.
- Backlog records may look valuable but lack registration, locator review, risk review, or access clearance; they must stay in prerequisite notes until resolved.
- External root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` must remain untouched unless the user explicitly asks otherwise.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST define learning reference notes for the selected ready 016 extraction tasks. The initial selected tasks were Northeast Blind Peak and Mingli True Formula Teacher; the current incremental selection also includes Duan Plain Mingxue Outline.
- **FR-002**: Each learning reference note MUST include source title, 016 task id, 015 queue id, 015 audit id, 014 source-library entry id, 013 source material id, target rule families, locator requirement, risk boundary, source-quality note, rights note, learning points, limitations, and candidate-intake readiness.
- **FR-003**: Learning reference notes MUST be concise summaries and MUST NOT copy long source passages or extracted source text from external raw materials.
- **FR-004**: The feature MUST allow selected learning points to become 013 candidate extract records only when they have a source material id, locator, proposed rule family, risk tier, concise extracted meaning, and limitations.
- **FR-005**: The feature MUST keep candidate extract records outside formal report evidence until existing 013 review and promotion workflows approve and promote them.
- **FR-006**: The feature MUST detect and document overlap with existing 013 pending, approved, rejected, or blocked candidates before creating new candidate records.
- **FR-007**: The feature MUST record whether an overlapping candidate should be reused, superseded, avoided as duplicate, or left for manual review.
- **FR-008**: The feature MUST preserve 016 prerequisite backlog records as prerequisite action notes, not as learning reference notes or candidate extracts.
- **FR-009**: The feature MUST include prerequisite action notes for source registration, risk review, and blocked-source clearance represented in the current 016 package.
- **FR-010**: The feature MUST validate that learning notes, candidates, and backlog action notes do not alter formal evidence counts.
- **FR-011**: The feature MUST update maintainer documentation so a future maintainer can see how 016 package records move into learning notes, 013 candidates, review decisions, promotion batches, and formal 012 evidence.
- **FR-012**: The feature MUST provide a quick validation path that confirms learning notes, candidate records, backlog action notes, duplicate warnings, and evidence boundaries are valid.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: Learning reference notes MAY summarize traditional 命理 source material only as source-backed study data, not as scientific proof or guaranteed real-world outcomes.
- **SE-002**: Learning points and candidate extracts MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-003**: High-risk or sensitive learning points MUST include uncertainty and limitation notes before they can become candidate extracts.
- **SE-004**: The feature MUST refuse or block candidate-ready wording that requests guaranteed death timing, exact lifespan, medical diagnosis or treatment, legal instruction, psychological treatment, investment instruction, coercive matching, anxiety creation, or paid-remedy upsells.
- **SE-005**: Candidate records created from learning points MUST remain pending review until manually reviewed under the 013 workflow.
- **SE-006**: Backlog records with high-risk, blocked, or deferred states MUST NOT become routine candidate extracts until prerequisites are resolved.

### Key Entities *(include if feature involves data)*

- **LearningReferenceNote**: A maintainer-facing note summarizing source-backed learning points from a ready 016 extraction task.
- **LearningPoint**: A concise, candidate-ready study item inside a learning note, with rule family, locator, risk tier, limitations, and duplicate/overlap status.
- **CandidateIntakeDecision**: The decision to create, reuse, avoid, defer, or manually review a 013 candidate for a learning point.
- **PrerequisiteActionNote**: A maintainer-facing note preserving non-ready backlog work such as source registration, risk review, and blocked-source clearance.
- **LearningReferenceProgressSummary**: A computed view of note counts, learning point counts, candidate-intake decisions, backlog actions, risk tiers, duplicate warnings, and evidence-boundary status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A maintainer can identify the first two source-backed learning reference notes and their candidate-ready learning points within 5 minutes.
- **SC-002**: The first implementation slice produces learning notes for exactly the two current ready 016 extraction tasks and prerequisite action notes for the current non-ready 016 backlog records.
- **SC-003**: All learning points include source trace, target rule family or gap, risk boundary, locator requirement, and limitations.
- **SC-004**: All candidate-intake decisions clearly state create, reuse, avoid duplicate, defer, or manual review before any candidate data is added.
- **SC-005**: Validation confirms that learning notes, candidate-intake decisions, and prerequisite action notes do not change formal report evidence counts.
- **SC-006**: Focused, boundary, and full validation pass before the feature is marked complete.

## Assumptions

- The first 017 scope is limited to the current 016 package rather than all external materials at once.
- The selected ready 016 extraction tasks are the fastest useful source of learning reference data, starting with the first two high-priority tasks and then extending to the next ordinary ready task.
- Backlog items remain prerequisite work until registration, locator, risk, or access blockers are resolved.
- Existing 013, 014, 015, and 016 project data remains the source of truth for traceability and readiness.
- External root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials and are not moved, deleted, converted, rewritten, or committed by this feature.
