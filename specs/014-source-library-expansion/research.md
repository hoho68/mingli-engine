# Research: Source Library Expansion and Evidence Factory

## Decision: Store source-library metadata in project-local JSON

**Rationale**: The existing classical evidence and source-intake features use deterministic JSON data loaded by Python modules. Keeping 014 in the same style makes the workflow reviewable in Git, portable across local machines, and simple to validate without a database or network access.

**Alternatives considered**:

- SQLite or another local database: rejected for now because the current scale is modest and the project already reviews JSON data well.
- Tracking raw PDFs or root `Markdown/`: rejected because user-provided source materials must remain external unless the user explicitly requests tracking or conversion.
- Ad hoc Markdown-only lists: rejected because priority, batch, and value summaries need structured validation.

## Decision: Keep source-library planning separate from candidate extraction

**Rationale**: 013 already owns candidate extracts, review decisions, and promotion batches. 014 should describe what source materials exist, why they matter, and what should be processed next. Separating these layers keeps registered sources from becoming unreviewed evidence.

**Alternatives considered**:

- Add all 014 fields directly to 013 `source_materials.json`: rejected because it would make the intake queue carry planning concerns and could increase migration risk.
- Treat every registered source as a candidate extract: rejected because source-level planning is broader than a single evidence candidate.
- Merge 014 with the formal 012 corpus: rejected because formal report evidence must remain approved and curated.

## Decision: Use explicit priority assessments instead of opaque automatic scoring

**Rationale**: Source value is partly judgmental: a source may be valuable because it fills a gap, clarifies a conflict, confirms an existing rule, or documents why material should not be used. Explicit priority fields and rationales are easier to audit than a hidden score.

**Alternatives considered**:

- Fully automatic ranking: rejected because source quality, safety risk, and rule-family coverage need human judgment.
- Arrival-order processing: rejected because it does not target evidence gaps or high-value review work.
- Single numeric priority only: rejected because maintainers need to understand why a source is high or low priority.

## Decision: Model curation batch plans separately from promotion batches

**Rationale**: A curation batch plan selects sources for extraction and review before candidate outcomes exist. A 013 promotion batch groups already approved candidates prepared for formal evidence updates. Keeping them separate prevents planned work from being mistaken for completed evidence.

**Alternatives considered**:

- Reuse 013 promotion batches for planning: rejected because promotion batches require approved candidates, while planning happens before extraction.
- Store batch planning only in freeform notes: rejected because batches need validation for target gaps, included sources, risk boundaries, and status.

## Decision: Compute source and batch value summaries from downstream records

**Rationale**: A source creates value when it produces approved candidates, promoted evidence, conflict clarification, durable rejection, blocked reason, or documented gap resolution. These are outcomes already represented by 013 source-intake and 012 formal evidence data, so summaries should be computed instead of manually duplicated.

**Alternatives considered**:

- Manual value scores: rejected because they drift from actual review outcomes.
- Count registered sources as value: rejected because registration alone does not improve report evidence.
- Count all candidates as value: rejected because unapproved candidates are not report-usable and may be unsafe.

## Decision: Preserve non-useful source outcomes

**Rationale**: Duplicate, deferred, exhausted, blocked, or low-quality materials still teach the project something. Preserving those reasons prevents repeated work and helps explain why some local materials do not become formal evidence.

**Alternatives considered**:

- Delete failed or duplicate sources: rejected because it loses audit history.
- Hide deferred sources from summaries: rejected because maintainers need planning visibility.
- Treat blocked sources as errors only: rejected because blocked status can be a valid reviewed outcome.

## Decision: Require high-risk labels before extraction planning

**Rationale**: Some classical materials discuss life-death, illness, disaster, coercive relationship claims, paid remedies, or other sensitive topics. Labeling this at source and batch level gives reviewers a safety boundary before candidate extraction begins.

**Alternatives considered**:

- Detect risk only after candidate extraction: rejected because reviewers need to know before selecting and processing the source.
- Exclude all high-risk sources entirely: rejected because the project may use traditional high-risk material when it is bounded, source-backed, and safely reviewed.
