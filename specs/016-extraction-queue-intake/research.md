# Research: Extraction Queue Intake Package

## Decision: Store 016 package metadata separately from 013 candidate extracts

**Rationale**: 016 is a planning handoff from 015 materials-audit queue items into future 013 candidate extraction work. Storing work-package metadata separately keeps task readiness, draft candidate intent, and prerequisite routing visible without implying that candidate extracts already exist.

**Alternatives considered**:

- Write directly into 013 `candidate_extracts.json`: rejected because draft slots do not yet contain extracted text, review decisions, or candidate-ready source locators.
- Extend 015 queue items in place: rejected because 015 owns audit readiness, while 016 owns extraction work-package handoff.

## Decision: Treat candidate draft slots as placeholders, not candidate extracts

**Rationale**: Draft slots describe what a reviewer may manually extract later. They must not include source passages, extracted meanings, review decisions, approval status, or promotion status.

**Alternatives considered**:

- Create blank 013 candidate records: rejected because 013 candidate validation expects candidate extract semantics.
- Skip draft slots entirely: rejected because reviewers need consistent task intent, locator requirements, and risk requirements before opening sources.

## Decision: Cross-check 015 queue eligibility before task creation

**Rationale**: A queue item can become stale if audit records, readiness findings, or source alignments change. Extraction tasks should require current queue, audit, readiness, and alignment consistency.

**Alternatives considered**:

- Trust only `queue_type=extraction_ready`: rejected because it can miss changed readiness, blocked state, or missing source-library alignment.
- Recompute source readiness from raw files: rejected because 016 must not read or mutate raw source files.

## Decision: Preserve prerequisite backlog records

**Rationale**: Non-ready items remain important work. Registration, locator review, preparation, risk review, deferred, and blocked items should stay visible with durable reasons instead of disappearing from the package.

**Alternatives considered**:

- Omit non-ready queue items: rejected because maintainers would lose the reason items were skipped.
- Convert all non-ready items into extraction tasks: rejected because it violates safety and evidence-readiness boundaries.

## Decision: Detect duplicate and overlap risks against existing 013 metadata

**Rationale**: Some sources already have pending, rejected, approved, or blocked 013 candidates. 016 should surface overlap warnings so reviewers do not duplicate work blindly.

**Alternatives considered**:

- Ignore existing 013 candidates: rejected because it can create redundant extraction work.
- Mutate existing candidate records: rejected because 016 is planning metadata only.

## Decision: Keep high-risk items out of routine extraction until prerequisites pass

**Rationale**: High-risk material can be reviewed, but it needs explicit risk review, uncertainty wording, and source boundaries before candidate extraction.

**Alternatives considered**:

- Rank high-risk items by source priority alone: rejected because safety prerequisites outrank extraction convenience.
- Block high-risk items forever: rejected because the project constitution allows bounded, source-backed high-risk signal analysis after review.

## Decision: Preserve raw-file and report-evidence boundaries

**Rationale**: 016 should not open PDFs, run OCR, convert Markdown, copy source passages, create report evidence, or store personal birth data. It only arranges review work.

**Alternatives considered**:

- Include source excerpts for convenience: rejected because source passages belong in later candidate extraction and review.
- Link draft slots into report evidence counts: rejected because only reviewed and promoted formal evidence may affect reports.
