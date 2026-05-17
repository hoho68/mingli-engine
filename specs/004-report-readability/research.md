# Research: 报告分层阅读体验优化

## Decision: Keep The Feature Markdown-Only

**Rationale**: The user asked for more hierarchy in the current report, not a new UI or export format. Markdown already carries headings, bullets, and labels well enough for this feature.

**Alternatives considered**:

- HTML layout: rejected because it would introduce a new output format and visual surface.
- PDF/PNG export: rejected because it is outside the current CLI report contract.

## Decision: Prepare Quick Guide Text In Report Schema

**Rationale**: `report_schema.py` already has access to chart source, confidence, focus topic, interpretation boundaries, and element distribution. Building quick-guide bullets there keeps `markdown.py` focused on layout.

**Alternatives considered**:

- Build quick guide in `markdown.py`: rejected because it would make the renderer parse report prose.
- Build quick guide in `interpretation.py`: rejected because source confidence and focus topic live outside pure interpretation rules.

## Decision: Add Explicit Report Fields For Readability Text

**Rationale**: A `quick_guide` field and an `interpretation_boundaries` field keep layered rendering simple and avoid copying the same limitation text through multiple report sections.

**Alternatives considered**:

- Derive all content from existing strings during rendering: rejected because it encourages brittle string parsing.
- Keep limitations embedded only in `structure_analysis`: rejected because the new layered report needs a visible boundary layer.

## Decision: Use Layer Headings And Light Subheadings

**Rationale**: Four `##` layer headings create the requested hierarchy, while existing sections can become `###` subsections or bold labels. This keeps the report recognizable while making the reading path clearer.

**Alternatives considered**:

- Keep all current headings at the same level: rejected because it would not create clear reading layers.
- Collapse sections into a short summary: rejected because it would remove useful report detail.

## Decision: Preserve Existing Safety And CLI Contracts

**Rationale**: Readability must not change red-line handling, input shapes, or command names. Safety behavior is a domain-level invariant.

**Alternatives considered**:

- Add a new `--style layered` flag: rejected because the user asked to improve the report, not add a mode.
- Return layered output only for automatic charts: rejected because external verified chart reports should receive the same readability improvement.
