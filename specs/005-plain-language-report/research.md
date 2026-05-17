# Research: 八字报告白话表达优化

## Decision: Keep Label Formatting In Report Assembly

**Decision**: Add reader-facing label helpers in `src/mingli_engine/report_schema.py`.

**Rationale**: `report_schema.py` already converts chart and interpretation objects into report text. This is the right boundary for turning internal values into user-facing wording before Markdown layout happens.

**Alternatives considered**:

- Renderer-level replacement in `markdown.py`: rejected because it would blur layout and content responsibilities and could accidentally replace text inside user-provided notes.
- A new localization module: rejected for now because the project has one language and a small fixed mapping set.

## Decision: Use Explicit Known-Value Mappings

**Decision**: Use small dictionaries or helper functions for known values such as source type, confidence, calendar type, pillar name, and placeholders.

**Rationale**: Explicit mappings are easy to audit and test. They avoid hidden transformations and make it clear which raw values are intentionally translated.

**Alternatives considered**:

- Ad hoc inline conditional strings: rejected because repeated formatting rules would be harder to test and maintain.
- Broad string replacement after report generation: rejected because it can produce accidental changes outside the intended fields.

## Decision: Preserve Transparent Fallbacks For Unknown Values

**Decision**: Unknown values should not be interpreted. The report may use `未说明` for empty or placeholder-like values and should otherwise disclose the original value conservatively when hiding it would reduce transparency.

**Rationale**: The constitution requires transparent calculation boundaries. Unknown data should not be guessed into a friendlier but inaccurate phrase.

**Alternatives considered**:

- Always hide unknown values as `未说明`: rejected because it can lose useful source disclosure.
- Always show raw unknown values: accepted only as fallback when disclosure matters; known machine values should still be translated.

## Decision: Keep The 004 Markdown Structure Unchanged

**Decision**: Do not change heading order or add new report layers.

**Rationale**: Feature 004 already solved report layering. Feature 005 is only a wording polish and should not expand scope.

**Alternatives considered**:

- Add narrative introductions to each layer: rejected for this feature because it overlaps with a future deeper report-quality pass.

## Decision: Verify Through Both CLI Paths

**Decision**: Integration tests must cover both `calculate-report` and `generate-report`.

**Rationale**: The feature applies to automatic chart calculation and externally supplied chart data. Both paths must produce plain-language Markdown without new options.

**Alternatives considered**:

- Unit-only tests: rejected because raw machine labels currently appear in final Markdown, so real CLI output must be checked.
