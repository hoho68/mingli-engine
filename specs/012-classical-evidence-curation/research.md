# Research: 经典证据库精修

## Decision: Continue With Curated JSON As Runtime Source

Runtime report generation will continue loading curated project-local JSON files rather than raw PDFs or converted Markdown.

**Rationale**: The source files include OCR noise, page ambiguity, and potentially unsafe original wording. Reports need deterministic, reviewed evidence units rather than direct document parsing.

**Alternatives considered**:

- Parse PDFs at report runtime: rejected because extraction quality is unstable and would make evidence unverifiable.
- Read Markdown extracts directly: rejected because extracts are preparation material and may contain unreviewed copied passages.
- Move to a database: rejected for this scope because the corpus is small and JSON is easier to review in diffs.

## Decision: Add Curation Batches

Evidence additions will be grouped into curation batches with reviewer notes, source ids, evidence ids, and unresolved issues.

**Rationale**: The corpus will grow from a small seed to at least 60 evidence units. Batches make it possible to review what changed, why it was accepted, and which gaps remain.

**Alternatives considered**:

- Add evidence directly without batch metadata: rejected because maintainers would lose review context.
- Require one batch per source only: rejected because later corrections and topic-specific passes need smaller review units.

## Decision: Use Source References, Not Long Excerpts

Each evidence unit must carry a page, chapter, heading, or review-note reference. The summary remains a concise synthesis.

**Rationale**: The report can show traceability without copying long copyrighted or unsafe passages. Review-note references handle sources whose page numbers are unreliable.

**Alternatives considered**:

- Store direct excerpts in report-facing units: rejected because it would bloat reports and risk copying unsafe wording.
- Store only source titles: rejected because it is too vague for audit.

## Decision: Represent Conflicts Separately

Disagreements between sources or schools will be represented as explicit source conflict records that link evidence ids and describe the disagreement.

**Rationale**: Multiple evidence units can remain valid while disagreeing. A separate conflict layer lets reports downgrade or label conclusions without mutating the original evidence.

**Alternatives considered**:

- Embed conflict text in every evidence unit: rejected because it duplicates data and becomes hard to maintain.
- Ignore conflicts until report generation: rejected because conflict handling must be testable before rendering.

## Decision: Compute Coverage Reports

Coverage by source, rule family, risk tier, and review status will be computed from source, evidence, batch, and conflict data.

**Rationale**: Derived reports avoid stale hand-maintained counts and give maintainers a direct picture of curation gaps.

**Alternatives considered**:

- Maintain a static coverage file: rejected because it can drift from evidence data.
- Rely only on tests: rejected because tests pass/fail but do not summarize remaining work.

## Decision: Keep The 011 Report Contract Stable

Formal reports will keep the existing source summary, formal conclusions, evidence traces, conclusion strength, high-risk notes, and unavailable conclusion fields.

**Rationale**: 012 should deepen evidence quality without changing user-facing formats or CLI semantics. Expanded evidence should feed the existing report object.

**Alternatives considered**:

- Add a new report format: rejected because it would split rendering behavior.
- Add curation-only details to every report: rejected because reviewer metadata is not always reader-facing.

## Decision: Preserve Existing High-Risk Narrowing

High-risk evidence units can expand coverage, but output rules from Constitution v2.0 remain unchanged.

**Rationale**: The user wants the full corpus used as core evidence, while exact death timing, exact lifespan, diagnosis, treatment, legal, psychological, investment, coercive matching, anxiety creation, and paid-remedy upsells must remain blocked or narrowed.

**Alternatives considered**:

- Exclude all high-risk evidence: rejected because it would discard important source material.
- Allow original high-risk wording unchanged: rejected because it would violate the constitution and user safety boundaries.
