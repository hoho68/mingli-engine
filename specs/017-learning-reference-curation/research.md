# Research: Learning Reference Curation

## Decision: Store learning references separately from 013 candidates and 012 formal evidence

**Rationale**: Learning references are study notes that help maintainers understand source material and prepare candidate extraction. They are useful before candidate review, but they are not candidate extracts, review decisions, promotion batches, or formal report evidence.

**Alternatives considered**:

- Write learning notes directly into 013 `candidate_extracts.json`: rejected because many learning notes are not ready for candidate semantics and may need duplicate or safety review first.
- Write learning notes directly into 012 evidence units: rejected because formal report evidence requires reviewed and promoted material.
- Keep notes only in free-form docs: rejected because maintainers need validation and progress summaries.

## Decision: Treat readable learning notes as study metadata, not evidence

**Rationale**: The fastest useful output is maintainer-readable knowledge, but the project must preserve evidence boundaries. Notes may summarize source-backed ideas, but reports must not consume them until candidate review and promotion happen.

**Alternatives considered**:

- Make every learning point report-usable immediately: rejected because it bypasses 013 review and 012 promotion.
- Avoid learning notes and create only structured candidates: rejected because maintainers need readable intermediate context and duplicate decisions.

## Decision: Create candidate-intake decisions before mutating 013 candidate data

**Rationale**: The current 016 package already warns about overlap. A decision layer lets maintainers identify which learning points should create candidates, reuse existing candidates, avoid duplicates, defer, or require manual review.

**Alternatives considered**:

- Always create new candidates: rejected because it can duplicate pending, rejected, approved, or blocked candidates.
- Never create candidates automatically from learning notes: rejected because structured candidate records are needed for review progress.

## Decision: Use 016 tasks and backlog records as the first bounded work surface

**Rationale**: 016 initially selected the next useful work: two extraction-ready tasks plus three prerequisite backlog records. The incremental ready-queue extension adds Duan Plain Mingxue Outline as the next ordinary ready task while still avoiding a broad sweep across every external material at once.

**Alternatives considered**:

- Process all root PDFs and Markdown batches: rejected because it is too broad for one safe implementation slice.
- Process only one source: rejected because the first package already contains two high-value ready sources and useful overlap contrast.

## Decision: Preserve duplicate and overlap warnings before creating candidates

**Rationale**: Existing 013 data already contains candidates for Northeast Blind Peak and other sources. The learning workflow should surface reuse or duplicate-avoidance decisions before adding records.

**Alternatives considered**:

- Trust source/title uniqueness only: rejected because candidates may overlap at material and rule-family level.
- Delete or rewrite existing candidates: rejected because 017 must not mutate historical review records silently.

## Decision: Keep high-risk and blocked materials behind prerequisite action notes

**Rationale**: High-risk and blocked materials can be valuable, but risk-review and access/quotation clearance are prerequisites. Backlog action notes preserve work without treating those items as routine learning references.

**Alternatives considered**:

- Extract high-risk backlog items immediately: rejected because it violates readiness and safety boundaries.
- Ignore backlog items: rejected because maintainers would lose the next actions needed to unlock future curation.

## Decision: Preserve raw-file and report-evidence boundaries

**Rationale**: 017 should not open PDFs, run OCR, convert Markdown, copy long passages, create formal evidence, or store personal birth data. It arranges study and review metadata only.

**Alternatives considered**:

- Include source excerpts for convenience: rejected because long copied passages and source text belong outside planning metadata.
- Link learning references into report evidence counts: rejected because only reviewed and promoted formal evidence may affect reports.
