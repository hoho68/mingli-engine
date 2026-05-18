# Research: 第二层结构观察表达优化

## Decision: Keep Structure Prose In The Interpretation Layer

**Decision**: Update wording generation in `src/mingli_engine/interpretation.py`, especially the functions that build five-element, ten-god, and structure observation text.

**Rationale**: The existing code already creates interpretation text from chart and distribution objects in this file. Keeping the change there preserves the current responsibility split: interpretation creates domain prose, report schema assembles report fields, and Markdown rendering lays out the report.

**Alternatives considered**:

- Renderer-level replacement in `markdown.py`: rejected because it would mix layout with domain prose and could accidentally replace user-provided or unrelated text.
- Report assembly rewrite in `report_schema.py`: rejected because 005 label formatting belongs there, but 006 wording comes from interpretation summaries.
- New localization framework: rejected because the feature is narrow and Chinese-only for now.

## Decision: Preserve Counts While Smoothing The Sentence

**Decision**: Keep direct, hidden, and total five-element counts visible, but introduce them as observation material in more natural Chinese.

**Rationale**: The spec requires readability without losing transparency. Counts let users and maintainers trace the wording back to input chart signals.

**Alternatives considered**:

- Hide numeric counts and only describe concentration: rejected because it weakens auditability.
- Keep current terse wording unchanged: rejected because it is the core readability issue for 006.

## Decision: Frame Ten-God Values As Relationship Clues

**Decision**: Keep each pillar's ten-god value visible and add a short reader-facing introduction that says these are structural relationship clues.

**Rationale**: This preserves the data while preventing readers from treating the list as a final fate conclusion.

**Alternatives considered**:

- Expand ten-god interpretation into detailed personality prose: rejected because it would add new interpretation depth outside 006.
- Remove ten-god labels from the layer: rejected because they are a useful part of the existing structure observation.

## Decision: Keep Unknown And Missing Signals Conservative

**Decision**: Unknown signals and missing ten-god positions should continue to be disclosed without guessing. Missing elements should still be described as less visible in countable signals, not as real-world deficiency.

**Rationale**: The constitution requires transparent calculation boundaries and avoids overclaiming from incomplete or school-dependent material.

**Alternatives considered**:

- Guess a friendly explanation for unknown values: rejected because it reduces transparency.
- Treat missing elements as weakness: rejected because it creates unsafe and deterministic interpretation.

## Decision: Verify Through Unit, Integration, And Safety Tests

**Decision**: Add or update tests at three levels: interpretation unit tests for exact wording boundaries, integration tests for final Markdown, and safety tests to ensure prohibited language and red-line refusal remain intact.

**Rationale**: The feature changes report language in a sensitive domain. The tests must prove both readability and safety preservation.

**Alternatives considered**:

- Unit-only testing: rejected because final Markdown can still regress through report assembly or rendering.
- Snapshot-only testing: rejected because focused assertions are clearer and less brittle for prose polish.
