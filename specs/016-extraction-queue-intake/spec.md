# Feature Specification: Extraction Queue Intake Package

**Feature Branch**: `016-extraction-queue-intake`

**Created**: 2026-05-31

**Status**: Draft

**Input**: User description: "保持不推送远程，开始规划 016；016 围绕把 015 的 next-action queue 转成下一批候选抽取任务。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build the Next Extraction Work Package (Priority: P1)

An evidence reviewer needs the 015 materials-audit next-action queue turned into a small, reviewable extraction work package before opening source files. The package should identify which queue items are ready for candidate extraction, what each task targets, what source and audit records it traces to, and which checks must happen before any candidate text is written.

**Why this priority**: 015 produced the next recommended actions, but maintainers still need a focused handoff into the 013 candidate-intake workflow. Without a work package, ready queue items can be mixed with registration, risk-review, or blocked backlog items.

**Independent Test**: This can be tested by loading the current 015 queue and confirming that only eligible extraction-ready items become extraction task records with stable task ids, source-library links, audit links, target rule families or gaps, risk boundary, and pre-extraction checks.

**Acceptance Scenarios**:

1. **Given** the 015 next-action queue includes extraction-ready, registration-backlog, risk-review, preparation-backlog, and blocked items, **When** a maintainer builds the next extraction work package, **Then** only eligible extraction-ready queue items become extraction tasks and every skipped item is listed with a reason.
2. **Given** an extraction-ready queue item has source-library alignment, readiness rationale, target rule family, and pre-extraction checks, **When** it is converted into a work package task, **Then** the task preserves links to the 015 audit record, 015 queue item, 014 source-library entry, and the intended 013 source-intake destination.
3. **Given** a queue item is high-risk, blocked, deferred, or missing locator/source registration prerequisites, **When** the work package is built, **Then** it remains outside extraction tasks and is routed to the correct prerequisite backlog.

---

### User Story 2 - Prepare Candidate Draft Slots Without Evidence Promotion (Priority: P2)

An extraction reviewer needs task slots that show what candidate extracts may be created later, without treating the slots as reviewed candidates or formal evidence. The package should define the expected candidate intent, locator requirements, source-quality checks, and safety wording requirements for each task.

**Why this priority**: Reviewers need enough structure to work consistently, but the system must not fabricate extracted text, approval decisions, or report evidence before a human review step.

**Independent Test**: This can be tested by inspecting the generated package and confirming that candidate slots contain no source passages, no approved meanings, no review decisions, and no promotion status, while still naming the intended rule family or coverage gap.

**Acceptance Scenarios**:

1. **Given** an extraction task targets a rule family or evidence gap, **When** draft slots are prepared, **Then** each slot names the intended extraction purpose, required locator precision, and required review notes without copying source text.
2. **Given** a task touches sensitive or high-risk material, **When** draft slots are prepared, **Then** the slots require bounded traditional-analysis language, uncertainty notes, and high-risk review before any candidate can be marked review-ready.
3. **Given** a maintainer reviews the package, **When** they inspect candidate slots, **Then** they can tell which future 013 candidate records are allowed to be created and which prerequisites are still missing.

---

### User Story 3 - Preserve Backlog and Boundary Visibility (Priority: P3)

A maintainer needs the work package to preserve the non-ready parts of the 015 queue so registration, risk review, locator review, and blocked work are not lost. The package should separate extraction tasks from prerequisite tasks and keep formal evidence counts unchanged.

**Why this priority**: The queue is useful only if it keeps unsafe and incomplete work visible without letting it enter extraction prematurely.

**Independent Test**: This can be tested by generating a package that includes skipped queue items and confirming that non-ready items are represented as prerequisite backlog records, not extraction tasks or formal evidence.

**Acceptance Scenarios**:

1. **Given** a queue item requires source-library registration, **When** the package is built, **Then** the item appears in a registration prerequisite backlog with its missing metadata and recommended next action.
2. **Given** a queue item requires risk review, **When** the package is built, **Then** the item appears in a risk-review prerequisite backlog and cannot be scheduled as routine extraction.
3. **Given** blocked or deferred items exist, **When** the package is built, **Then** their durable reasons remain visible and they do not affect candidate, promotion, or report-evidence counts.

### Edge Cases

- The 015 next-action ids change order after material readiness is updated.
- A queue item is marked extraction-ready but its linked audit record no longer has matching readiness or alignment data.
- Multiple queue items point to the same audit record or source-library entry.
- A queue item targets a rule family that already has pending 013 candidates.
- A source has approved-but-unpromoted 013 candidates and should not be duplicated blindly.
- A high-risk queue item has useful coverage value but lacks risk-review prerequisites.
- A registration-backlog item becomes ready after source-library registration but before extraction work begins.
- A blocked item lacks a durable reason or depends on external material access that is not available.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST build a next extraction work package from the current 015 materials-audit queue without reading or mutating raw source files.
- **FR-002**: System MUST include only eligible extraction-ready 015 queue items as extraction tasks.
- **FR-003**: System MUST preserve skipped registration, preparation, risk-review, deferred, and blocked queue items as prerequisite backlog records with reasons.
- **FR-004**: System MUST give every extraction task a stable task id, source audit link, queue item link, source-library link when available, priority rationale, target rule family or gap, and recommended action.
- **FR-005**: System MUST verify that every extraction task still has matching 015 audit, alignment, readiness, and queue data before it enters the package.
- **FR-006**: System MUST identify duplicate or overlapping extraction tasks that point to the same source, rule family, or unresolved 013 candidate.
- **FR-007**: System MUST define draft candidate slots for extraction tasks without copying source passages, extracted meanings, review decisions, approval status, or promotion status.
- **FR-008**: System MUST require locator precision, source-quality notes, rights notes, risk boundary, and pre-extraction checks before a draft slot can be considered ready for manual extraction.
- **FR-009**: System MUST route high-risk, sensitive, blocked, deferred, or prerequisite-missing queue items away from routine extraction tasks.
- **FR-010**: System MUST preserve links from package records back to 015 materials-audit records, 014 source-library entries, and intended 013 source-intake records.
- **FR-011**: System MUST report package progress with counts for extraction tasks, candidate draft slots, registration backlog, risk-review backlog, preparation backlog, deferred items, blocked items, and duplicate/overlap warnings.
- **FR-012**: System MUST keep extraction work packages, draft slots, backlog records, and skipped items outside formal report evidence counts.
- **FR-013**: System MUST avoid automatic extraction, automatic candidate approval, automatic promotion, OCR, PDF parsing, or source-file conversion.
- **FR-014**: System MUST make the next manual action clear for every package item, including extract, register source, review risk, review locator, defer, or block.
- **FR-015**: System MUST validate package metadata for long copied passages, absolute destiny language, exact death or lifespan claims, medical/legal/psychological/investment instruction, coercive matching, anxiety creation, and paid-remedy upsells.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MAY use 015 queue items only as preparation and scheduling metadata until a future 013 candidate is manually extracted and reviewed.
- **SE-002**: System MUST keep raw files, prepared text, audit records, extraction tasks, draft candidate slots, 013 candidate extracts, review decisions, promotion batches, and formal report evidence as separate trust levels.
- **SE-003**: System MUST NOT present task readiness, draft slots, or queue priority as scientific proof, destiny certainty, or guaranteed prediction accuracy.
- **SE-004**: System MUST label sensitive and high-risk extraction tasks before manual extraction begins.
- **SE-005**: System MUST avoid absolute destiny language, guaranteed outcomes, exact death or lifespan claims, medical diagnosis or treatment, legal instruction, psychological treatment, investment instruction, coercive matching, anxiety creation, and paid-remedy upsells.
- **SE-006**: System MUST avoid storing personal birth data or generated user reports in extraction work packages.
- **SE-007**: System MUST store concise task metadata only and must not copy long source passages into package records.

### Key Entities *(include if feature involves data)*

- **Extraction Work Package**: A maintainer-facing batch created from the 015 next-action queue. Key attributes include package id, source queue snapshot, creation date, selected extraction tasks, prerequisite backlog records, and package status.
- **Extraction Task**: A planned manual extraction work item linked to a 015 queue item and audit record. Key attributes include task id, target rule family or gap, source-library link, priority rationale, risk boundary, and pre-extraction checks.
- **Candidate Draft Slot**: A placeholder describing a future 013 candidate extract that may be created manually. Key attributes include intended source locator requirement, target meaning category, safety requirements, and review readiness status.
- **Prerequisite Backlog Record**: A non-extraction package item for registration, preparation, locator review, risk review, deferred, or blocked work. Key attributes include missing prerequisites, durable reason, recommended action, and originating queue item.
- **Package Progress Summary**: A summary of extraction tasks, draft slots, prerequisite backlogs, duplicate warnings, blocked/deferred items, and evidence-boundary status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of package extraction tasks trace to a valid 015 queue item, 015 audit record, readiness finding, and source-alignment finding.
- **SC-002**: 0 registration-backlog, preparation-backlog, risk-review-backlog, deferred, or blocked queue items are scheduled as routine extraction tasks.
- **SC-003**: 100% of candidate draft slots contain no copied source passage, no extracted meaning, no review decision, and no promotion status.
- **SC-004**: 100% of extraction tasks include target rule family or gap, locator requirement, source-quality note, rights note, risk boundary, and pre-extraction checks.
- **SC-005**: 100% of skipped queue items appear in a prerequisite backlog with a missing prerequisite or durable reason.
- **SC-006**: Maintainers can identify the next extraction tasks and prerequisite backlogs from the package summary within 5 minutes.
- **SC-007**: 0 extraction work packages, extraction tasks, draft slots, or prerequisite backlog records are counted as formal report-usable evidence.
- **SC-008**: The package quality check reports no boundary, copied-passage, or high-risk language failures for the seeded package data.

## Assumptions

- The primary users are project maintainers and evidence reviewers moving from 015 materials audit into the next 013 candidate-extraction cycle.
- 016 creates extraction task planning metadata, not actual extracted source candidates.
- The existing 015 materials-audit queue remains the source of truth for readiness and prerequisite routing.
- The existing 014 source-library workflow remains responsible for source registration and source priority metadata.
- The existing 013 source-intake workflow remains responsible for actual candidate extracts, review decisions, and promotion readiness.
- Root PDFs, root `Markdown/`, `资料原文/`, and `资料整理/` remain external preparation materials unless the user explicitly asks to track, move, convert, or delete them.
- The initial 016 package should focus on the current 015 next five recommended queue item ids and preserve the rest as backlog context when useful.
