# Feature Specification: Source Library Expansion and Evidence Factory

**Feature Branch**: `014-source-library-expansion`

**Created**: 2026-05-28

**Status**: Draft

**Input**: User description: "Create the next feature for turning many future Mingli articles and source materials into durable project value: register source materials, prioritize extraction batches, measure evidence contribution, and keep raw local PDFs/Markdown external unless explicitly requested."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register Source Materials for Future Use (Priority: P1)

A project maintainer needs to register each newly provided article, book excerpt, PDF, or prepared Markdown source as a source-library entry before any extraction work begins. The entry must describe what the material is, what it may help with, how ready it is for review, and whether it is suitable for future candidate extraction.

**Why this priority**: The project will receive many more sources. Without a clear source library, the team cannot know which materials exist, which ones matter most, which ones have already been handled, or which ones should not be used.

**Independent Test**: This can be tested by registering a new source material and confirming that it has enough metadata for a maintainer to decide whether it is ready for extraction without opening every raw file.

**Acceptance Scenarios**:

1. **Given** a newly provided source material, **When** a maintainer registers it, **Then** the source library records its label, material type, preparation status, topic or rule-family coverage, source quality notes, risk concerns, and next action.
2. **Given** a source material is only stored locally as a raw PDF or local Markdown file, **When** it is registered, **Then** the source library records the material without requiring the raw file to be tracked, moved, deleted, or changed.
3. **Given** a registered source has insufficient title, locator, or preparation information, **When** a maintainer reviews the library, **Then** the source is clearly marked as not ready for extraction and shows the missing information.

---

### User Story 2 - Prioritize Extraction Batches (Priority: P2)

An evidence reviewer needs to decide which materials should be processed next. The system should help organize materials into curation batches based on expected value, coverage gaps, source quality, extraction effort, and risk level.

**Why this priority**: More sources do not automatically improve accuracy. The next batch should target areas that improve evidence coverage, reduce blind spots, or clarify conflicts rather than simply processing files in arrival order.

**Independent Test**: This can be tested by creating a planned curation batch from several registered sources and confirming that each included source has a priority rationale and expected contribution.

**Acceptance Scenarios**:

1. **Given** multiple registered sources with different topics and readiness states, **When** a reviewer prepares a curation batch, **Then** the batch identifies its target evidence gaps, included materials, expected value, risk concerns, and next action.
2. **Given** a source is high quality but covers an already saturated rule area, **When** it is prioritized, **Then** its priority rationale explains whether it is still useful for conflict checking, duplicate confirmation, or later deferral.
3. **Given** a source contains sensitive or high-risk claims, **When** it is assigned to a batch, **Then** the batch marks the special review boundary before extraction begins.

---

### User Story 3 - Measure Source-to-Evidence Value (Priority: P3)

A maintainer needs to see whether a source or batch actually produced value after extraction and review. Value should be measured by reviewable outcomes such as candidate extracts, approvals, rejections, conflicts, gaps, promoted evidence, and areas where the material proved unusable.

**Why this priority**: The project goal is better evidence-backed Mingli interpretation, not merely a larger pile of materials. Measuring contribution helps decide which future sources are worth processing and which topics still need stronger material.

**Independent Test**: This can be tested by linking a registered source to existing candidate extracts and review outcomes, then confirming that the source summary reports its contribution without treating unapproved material as formal evidence.

**Acceptance Scenarios**:

1. **Given** a registered source has produced candidate extracts, **When** a maintainer views its value summary, **Then** the summary shows candidate counts, approval status, rejection or blocked counts, related conflicts, and promoted evidence counts.
2. **Given** a source produced no usable evidence, **When** its value is summarized, **Then** the summary preserves the reason and marks the source as exhausted, blocked, duplicate, or deferred rather than silently hiding it.
3. **Given** a batch has completed review, **When** the maintainer reviews the batch outcome, **Then** the batch shows which rule families improved, which gaps remain, and what the recommended next batch should focus on.

---

### User Story 4 - Protect Raw-Source and Report Boundaries (Priority: P4)

A project maintainer needs confidence that registering many raw materials will not accidentally make those materials report-usable, violate source-handling boundaries, or create unsafe claims. Raw source entries and planned batches must remain distinct from candidate extracts, approved evidence, and formal report evidence.

**Why this priority**: The project already separates user-provided source material, candidate extracts, review decisions, and formal evidence. 014 must preserve that boundary while making large-scale source management easier.

**Independent Test**: This can be tested by registering and prioritizing a source that has no approved evidence, then confirming that generated reports and formal evidence coverage do not treat it as usable evidence.

**Acceptance Scenarios**:

1. **Given** a source is registered but has not produced approved evidence, **When** formal evidence or report-ready evidence is inspected, **Then** the source does not count as report-usable evidence.
2. **Given** a batch is planned but extraction has not started, **When** the project reports progress, **Then** the batch is shown as planned work rather than completed evidence coverage.
3. **Given** a source contains long copyrighted passages, **When** it is registered or summarized, **Then** the source library stores concise descriptions and review metadata instead of wholesale copied text.

### Edge Cases

- A source material is registered twice under different file labels or editions.
- A source title is known, but author, edition, or origin details are uncertain.
- A material is locally available but not yet readable, converted, or prepared for review.
- A material covers many rule families and needs to be split across several future batches.
- A material is mostly anecdotal, contradictory, or unsafe and should be preserved as reviewed but not useful.
- A batch has many high-priority sources but reviewer capacity is limited.
- A source initially appears valuable but later proves duplicate or low quality.
- A source can support conflict analysis even when it should not add new formal evidence.
- Raw source files are renamed or moved by the user outside the project after registration.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow maintainers to register source materials as source-library entries without requiring raw local files to become tracked project assets.
- **FR-002**: System MUST record enough source-library metadata for maintainers to identify the material, preparation status, topic coverage, source quality, risk concerns, and next action.
- **FR-003**: System MUST distinguish registered source materials, planned extraction batches, candidate extracts, review decisions, promotion outcomes, and formal report-usable evidence.
- **FR-004**: System MUST support source readiness states such as not started, needs preparation, ready for extraction, in extraction, review completed, exhausted, deferred, duplicate, and blocked.
- **FR-005**: System MUST allow maintainers to assign each source a priority level with a rationale based on expected evidence value, coverage gap, source quality, extraction effort, and risk level.
- **FR-006**: System MUST allow reviewers to group registered sources into curation batches with a goal, target rule families or gaps, included sources, expected output, review boundary, and batch status.
- **FR-007**: System MUST require each planned curation batch to identify at least one evidence gap, conflict area, rule family, or source-quality reason that justifies processing the batch.
- **FR-008**: System MUST link source-library entries to candidate extracts, review decisions, conflicts, gaps, and promotion batches when those downstream records exist.
- **FR-009**: System MUST provide value summaries per source and per batch that show candidate counts, approval counts, rejection or blocked counts, conflict or gap counts, and formal evidence contribution.
- **FR-010**: System MUST make it possible to identify the highest-value next sources by priority, readiness, topic coverage, rule family, source quality, risk level, and unresolved gaps.
- **FR-011**: System MUST preserve duplicate, deferred, exhausted, rejected, and blocked source outcomes with reasons instead of silently removing them from project history.
- **FR-012**: System MUST prevent registered sources, planned batches, and unapproved candidate material from being counted as formal report-usable evidence.
- **FR-013**: System MUST support concise source descriptions and paraphrased review notes, and MUST avoid wholesale copying of source materials into source-library records.
- **FR-014**: System MUST make source-library progress auditable by showing how many materials are registered, ready, in progress, completed, deferred, blocked, and value-producing.
- **FR-015**: System MUST support next-action recommendations for each source or batch, such as prepare material, extract candidates, review candidates, promote approved items, revisit conflict, defer, or block.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MAY use curated classical material to support traditional Mingli judgments only after the material has passed the approved evidence path.
- **SE-002**: System MUST present source value as evidence contribution and review coverage, not as scientific proof or guaranteed prediction accuracy.
- **SE-003**: System MUST preserve formal report disclaimers wherever curated evidence later influences generated reports.
- **SE-004**: System MUST avoid absolute destiny language, guaranteed outcomes, exact death or lifespan claims, medical diagnosis or treatment, legal instruction, psychological treatment, investment instruction, coercive matching, anxiety creation, and paid-remedy upsells.
- **SE-005**: System MUST label high-risk source materials and planned batches before extraction so reviewers can apply stricter uncertainty and limitation requirements.
- **SE-006**: System MUST keep raw source materials, source-library records, candidate extracts, and formal evidence as separate trust levels.
- **SE-007**: System MUST avoid storing personal birth data or generated user reports in source-library expansion records.

### Key Entities *(include if feature involves data)*

- **Source Library Entry**: A registered material that may support future evidence work. Key attributes include source identifier, title or file label, material type, preparation status, topic coverage, source quality notes, priority, risk concerns, and next action.
- **Source Priority Assessment**: A maintainer judgment about why a source should be processed now, later, or not at all. Key attributes include expected evidence value, targeted gap, effort estimate, risk level, and rationale.
- **Curation Batch Plan**: A planned or completed group of sources selected for extraction and review. Key attributes include batch goal, included sources, target rule families, expected output, status, and completion outcome.
- **Evidence Gap Target**: A missing, weak, conflicted, or under-reviewed area of the formal evidence corpus that a source or batch is expected to address.
- **Source Value Summary**: A post-review outcome summary for one source or batch. Key attributes include candidate counts, approval outcomes, rejected or blocked outcomes, conflicts, gaps, promoted evidence, and recommended next step.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of registered source materials include material identity, preparation status, topic or rule-family coverage, source quality notes, priority rationale, risk notes, and next action.
- **SC-002**: 0 raw local PDF or Markdown materials are required to be tracked, moved, deleted, converted, or mutated in order to register them in the source library.
- **SC-003**: 100% of planned curation batches identify at least one target gap, rule family, conflict area, or source-quality rationale before extraction begins.
- **SC-004**: Maintainers can identify the next five highest-priority extraction candidates from a progress summary within 2 minutes without manually inspecting every registered source.
- **SC-005**: 100% of completed source value summaries show candidate, approval, rejection or blocked, conflict or gap, and formal evidence contribution counts when downstream records exist.
- **SC-006**: 0 registered sources, planned batches, or unapproved candidate records are counted as formal report-usable evidence.
- **SC-007**: At least one duplicate, deferred, exhausted, or blocked source can be preserved with a reason and excluded from active extraction planning.

## Assumptions

- The primary users are project maintainers and evidence reviewers, not end users reading reports.
- The existing source-intake workflow remains responsible for candidate extracts, review decisions, and promotion readiness.
- This feature focuses on source-library expansion, prioritization, batch planning, and value measurement; it does not perform automatic extraction, full-text conversion, report-generation retrieval, or automated approval.
- User-provided root PDF files and the root `Markdown/` directory remain external preparation materials unless the user explicitly asks to track, move, convert, or delete them.
- "Value" means traceable evidence contribution, coverage improvement, conflict clarification, or documented non-usefulness; it does not mean guaranteed real-world prediction accuracy.
- Manual human review remains required before any source-derived material becomes formal evidence.
