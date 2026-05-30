# Feature Specification: Existing Materials Audit and Preparation

**Feature Branch**: `015-existing-materials-audit`

**Created**: 2026-05-30

**Status**: Ready for Review

**Input**: User description: "先不推送主流到远程，继续创建015规格，我们先把已有的资料做好。确认按方案 A 创建 015 规格。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inventory Existing Materials (Priority: P1)

A project maintainer needs a complete inventory of existing source materials before any new evidence extraction work begins. The inventory should cover root PDF materials, prepared Markdown batches, cleaned Markdown variants, existing learning notes, processing-status notes, and knowledge-skeleton artifacts, while preserving the current boundary that raw materials remain external preparation assets.

**Why this priority**: The project already has many materials in different preparation states. Without a reliable inventory, maintainers cannot tell which materials are duplicated, cleaned, partially summarized, already linked to 014 source-library entries, or still waiting for preparation.

**Independent Test**: This can be tested by reviewing the existing material collection and confirming that every discovered material group appears in an audit summary with a stable label, material kind, preparation state, and source-handling boundary.

**Acceptance Scenarios**:

1. **Given** root PDF files, prepared Markdown folders, cleaned Markdown folders, and maintainer notes already exist, **When** a maintainer runs the audit workflow, **Then** the audit identifies each material group and records its current preparation state without moving, deleting, converting, or tracking raw files.
2. **Given** the same source appears as both a raw file and a prepared or cleaned Markdown file, **When** the audit records the material, **Then** the audit links those representations as one material group instead of treating them as unrelated sources.
3. **Given** a material has unclear title, edition, source origin, or preparation history, **When** the audit records it, **Then** the audit marks those fields as uncertain and recommends the next clarification action.

---

### User Story 2 - Align Materials with the Source Library (Priority: P2)

An evidence reviewer needs to know which existing materials are already represented in the 014 source library and which materials still need registration or correction. The audit should compare existing materials against source-library entries and make gaps, duplicates, and uncertain matches visible.

**Why this priority**: 014 created a source-library planning layer. 015 should make the current local material corpus usable by aligning real files, prepared text, and notes with that planning layer before extraction begins.

**Independent Test**: This can be tested by comparing the audit summary against the current source-library entries and confirming that each relevant material is classified as matched, missing from the source library, duplicate, blocked, or needing clarification.

**Acceptance Scenarios**:

1. **Given** a root PDF or Markdown batch clearly matches an existing source-library entry, **When** the audit aligns materials, **Then** the audit records the matching source-library entry and preserves the existing trust boundary.
2. **Given** a useful prepared Markdown material is not yet registered in the source library, **When** the audit aligns materials, **Then** the audit flags it as a registration candidate with the minimum metadata needed for future registration.
3. **Given** two entries appear to describe the same source with different names or editions, **When** the audit aligns materials, **Then** the audit marks the relationship as a possible duplicate or edition variant rather than silently merging it.

---

### User Story 3 - Assess Extraction Readiness and Risk Boundaries (Priority: P3)

A maintainer needs to know which materials are ready for candidate extraction and which ones need cleaning, locator review, source-quality review, or high-risk boundary review first. The assessment should separate text preparation readiness from evidence readiness.

**Why this priority**: Some existing materials are already cleaned and summarized, while others are raw, incomplete, OCR-poor, high-risk, or missing locators. Treating them all as ready would create unsafe or low-quality candidate extraction work.

**Independent Test**: This can be tested by selecting several materials in different states and confirming that the audit assigns readiness findings, missing prerequisites, risk labels, and recommended next actions before extraction.

**Acceptance Scenarios**:

1. **Given** a material has a cleaned Markdown version and usable source notes, **When** readiness is assessed, **Then** the audit can mark it as ready for candidate-extraction review if source identity, locator confidence, rights notes, and risk boundaries are sufficient.
2. **Given** a material has only raw or noisy text, **When** readiness is assessed, **Then** the audit marks it as needing preparation and names what is missing, such as cleaning, locator review, title confirmation, or source-quality notes.
3. **Given** a material contains life-death, illness, disaster, coercive, remedy, or absolute verdict language, **When** readiness is assessed, **Then** the audit labels the high-risk boundary and prevents it from being treated as routine extraction work.

---

### User Story 4 - Produce the Next Candidate Extraction Queue (Priority: P4)

An evidence reviewer needs a practical next-work queue that turns the audit into an ordered set of safe, reviewable extraction candidates. The queue should identify which existing materials should be handled first, why they matter, what rule families or gaps they target, and what must be checked before extraction.

**Why this priority**: The purpose of organizing existing materials is to make the next extraction cycle focused and safe, not to create another static list.

**Independent Test**: This can be tested by generating a next-batch recommendation and confirming that each queue item has a source-library relationship, readiness state, target rule family or gap, risk boundary, and explicit pre-extraction checks.

**Acceptance Scenarios**:

1. **Given** multiple materials are ready or nearly ready, **When** the next queue is prepared, **Then** the queue ranks a small set of recommended materials by readiness, expected value, coverage gap, source quality, and risk.
2. **Given** a material is high-value but high-risk, **When** it appears in the queue, **Then** the queue includes stricter review prerequisites and does not place it ahead of safer equivalent work unless there is a clear rationale.
3. **Given** a material lacks required preparation details, **When** the queue is prepared, **Then** the material appears in a preparation backlog rather than the extraction-ready queue.

### Edge Cases

- A source appears as a root PDF, a prepared Markdown file, a cleaned Markdown file, and a note under different names.
- A cleaned Markdown file is shorter than its source and may have lost important context.
- A Markdown file contains embedded images or image references that may carry evidence not present in text.
- A source has useful learning notes but no reliable source locator.
- A material is high-value for theory but unsafe for direct report use.
- A material belongs to a future domain such as Zi Wei Dou Shu, charms, ritual, or remedy material and should be excluded or deferred from the current Bazi evidence workflow.
- A material is duplicated, partial, corrupted, placeholder-only, or too small to support extraction.
- A source already has candidate extraction notes in the knowledge skeleton, but the source-library entry is missing or incomplete.
- A raw file has been renamed by the user after earlier notes were written.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow maintainers to audit existing material groups across raw source files, prepared text, cleaned text, processing notes, and knowledge-skeleton artifacts.
- **FR-002**: System MUST record each audited material group with a stable label, known title, material representations, preparation state, source identity confidence, and recommended next action.
- **FR-003**: System MUST preserve raw source boundaries and MUST NOT require raw files to be moved, deleted, renamed, converted, committed, or otherwise mutated during the audit.
- **FR-004**: System MUST identify likely relationships between raw materials, prepared Markdown files, cleaned Markdown files, learning notes, processing-status notes, and knowledge-skeleton artifacts.
- **FR-005**: System MUST distinguish exact matches, likely matches, possible duplicates, edition variants, missing registrations, and uncertain relationships.
- **FR-006**: System MUST compare audited material groups against the existing source-library entries and show whether each group is matched, missing, blocked, deferred, duplicated, or needing clarification.
- **FR-007**: System MUST identify materials that should be registered in the source library before extraction can begin.
- **FR-008**: System MUST assess whether each material is ready for candidate extraction, needs preparation, needs source or locator clarification, needs rights review, needs risk review, should be deferred, or should be blocked.
- **FR-009**: System MUST separate text-preparation readiness from formal evidence readiness so cleaned text is never treated as approved report evidence.
- **FR-010**: System MUST flag materials that include high-risk, absolute-outcome, life-death, illness, disaster, coercive, remedy, or paid-pressure themes before they enter extraction work.
- **FR-011**: System MUST identify materials outside the current Bazi evidence scope and recommend deferral rather than mixing them into the active extraction queue.
- **FR-012**: System MUST preserve duplicate, deferred, blocked, uncertain, and out-of-scope findings with reasons so future maintainers do not repeat the same review.
- **FR-013**: System MUST produce a next candidate-extraction queue that ranks a limited set of materials by readiness, expected value, source quality, coverage gap, and risk boundary.
- **FR-014**: System MUST produce a preparation backlog for materials that are useful but not ready for extraction.
- **FR-015**: System MUST make missing prerequisites visible for each queue or backlog item, including missing locator, unclear edition, insufficient cleaning, missing source-library entry, missing risk notes, or missing rights notes.
- **FR-016**: System MUST avoid wholesale copying of source passages into audit records and use concise descriptions, labels, and review metadata instead.
- **FR-017**: System MUST make audit progress measurable by reporting counts for discovered material groups, matched source-library entries, missing registrations, extraction-ready materials, preparation backlog items, high-risk items, deferred items, and blocked items.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MAY use audited materials only as preparation records until they pass the existing candidate-review and formal evidence path.
- **SE-002**: System MUST keep raw source files, prepared text, cleaned text, learning notes, source-library records, candidate extracts, review decisions, promoted evidence, and report evidence as separate trust levels.
- **SE-003**: System MUST NOT present material availability, cleaned text, or audit readiness as scientific proof, destiny certainty, or guaranteed prediction accuracy.
- **SE-004**: System MUST identify and label high-risk material before extraction, including life-death, illness, disaster, coercive matching, paid-remedy, or absolute verdict content.
- **SE-005**: System MUST avoid absolute destiny language, guaranteed outcomes, exact death or lifespan claims, medical diagnosis or treatment, legal instruction, psychological treatment, investment instruction, coercive matching, anxiety creation, and paid-remedy upsells.
- **SE-006**: System MUST avoid storing personal birth data or generated user reports in the materials audit.
- **SE-007**: System MUST preserve source-handling boundaries by storing only concise audit metadata and not long copied passages.

### Key Entities *(include if feature involves data)*

- **Material Audit Record**: A review record for one material group. Key attributes include stable label, known titles, raw/prepared/cleaned representations, source identity confidence, preparation state, source-library relationship, and next action.
- **Material Representation**: One visible form of a material, such as a root PDF, prepared Markdown, cleaned Markdown, learning note, processing-status note, or knowledge-skeleton artifact.
- **Source Alignment Finding**: A finding that connects a material group to the source library. Key attributes include match type, matched source entry, uncertainty reason, duplicate or edition-variant notes, and registration recommendation.
- **Preparation Readiness Finding**: A judgment about whether a material is ready for candidate extraction. Key attributes include cleaning status, locator confidence, source quality, rights notes, risk boundary, missing prerequisites, and readiness state.
- **Extraction Queue Item**: A recommended next work item for candidate extraction or preparation. Key attributes include material group, priority rationale, target rule family or gap, risk boundary, prerequisite checks, and recommended action.
- **Audit Progress Summary**: A summary of audit coverage, including discovered materials, matched entries, missing registrations, ready materials, preparation backlog, high-risk materials, deferred materials, and blocked materials.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of discovered existing material groups are represented in the audit summary with a stable label, material kind, preparation state, source-boundary status, and next action.
- **SC-002**: 0 raw source files are moved, deleted, renamed, converted, committed, or mutated as part of completing the audit.
- **SC-003**: 100% of audited materials are classified as source-library matched, missing registration, possible duplicate or edition variant, blocked, deferred, out of current scope, or needing clarification.
- **SC-004**: 100% of extraction-ready queue items include a source-library relationship, readiness rationale, target rule family or gap, source quality note, risk boundary, and pre-extraction checks.
- **SC-005**: 100% of high-risk or sensitive materials discovered by the audit are labeled before they can appear in the extraction-ready queue.
- **SC-006**: Maintainers can identify the next five recommended extraction or preparation actions from the audit summary within 5 minutes without manually opening every source file.
- **SC-007**: At least one preparation backlog can be produced for useful but not-ready materials, with a clear reason and recommended next action for each item.
- **SC-008**: 0 audited materials, prepared texts, cleaned texts, or queue items are counted as formal report-usable evidence.

## Assumptions

- The primary users are project maintainers and evidence reviewers preparing the local source corpus for later candidate extraction.
- The current source-library workflow remains responsible for source registration and priority metadata.
- The existing source-intake workflow remains responsible for candidate extracts, review decisions, and promotion readiness.
- This feature focuses on auditing and preparing existing materials; it does not perform automatic extraction, full-text conversion, automatic evidence approval, or report generation.
- Root source files and existing preparation folders remain external local materials unless the user explicitly asks to track, move, convert, or delete them.
- "已有资料做好" means making the current material corpus auditable, aligned, prioritized, and ready for a safe next extraction cycle.
- Materials outside the current Bazi evidence scope may be inventoried for visibility but should be deferred from active Bazi extraction work unless a later feature explicitly scopes them in.
