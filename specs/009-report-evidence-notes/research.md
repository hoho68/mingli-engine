# Research: 报告证据说明层

## Decision: Add A Dedicated Report Field

**Decision**: Add a dedicated evidence-note field to the formal report object.

**Rationale**: The evidence text is part of the formal report contract and should be included in safety review and Markdown rendering. A dedicated field keeps the boundary clear: report assembly owns content, while the renderer owns section placement.

**Alternatives considered**:

- Append the text to `structure_analysis`: rejected because the evidence note has a distinct purpose and placement.
- Put the text only in the Markdown renderer: rejected because safety review and future renderers would not see the same formal report content.
- Add a production registry of evidence checks: rejected as too much structure for one concise report section.

## Decision: Place The Section After Ten-God Summary

**Decision**: Render `### 观察依据` inside `第二层：结构观察`, after `### 十神摘要` and before `### 结构分析`.

**Rationale**: The reader first sees raw structure summaries, then receives a short guide explaining how those summaries become observation basis, then continues to broader structure analysis. This preserves the existing four-layer reading order.

**Alternatives considered**:

- Place it before `四柱与五行摘要`: rejected because the reader would not yet have seen the referenced summaries.
- Place it in `第三层：解读边界`: rejected because the section explains evidence basis, not only interpretive limits.
- Place it in `快速导读`: rejected because the quick guide should remain concise.

## Decision: Use Durable Plain-Language Bullets

**Decision**: Use a compact bullet list covering source assumptions, four pillars, five-element signals, ten-god signals, and action-reflection boundaries.

**Rationale**: The section should answer "where did this observation come from?" without becoming a new interpretation engine. Stable bullet labels make the contract easy to test without freezing the whole report.

**Alternatives considered**:

- Generate long prose dynamically for each chart: rejected because it would add length and make tests brittle.
- Include exact numeric evidence tables: rejected because existing summaries already expose the structure signals and this feature is about explanation, not new data presentation.
- Add per-sentence citations throughout the report: rejected as too broad for the current report format.

## Decision: Extend Existing Regression Tests

**Decision**: Add evidence-note assertions to existing report schema, Markdown renderer, and manifest-driven regression tests.

**Rationale**: The 008 regression manifest already verifies safe automatic and external verified report paths. Adding evidence-note checks there protects the new section across final CLI output without full Markdown snapshots.

**Alternatives considered**:

- Add full Markdown snapshots: rejected because report prose is expected to evolve.
- Add a separate example manifest: rejected because the existing manifest is already the stable report-regression entry point.
- Test only the renderer: rejected because report assembly and safety review also need coverage.

## Decision: Keep Safety JSON Behavior Unchanged

**Decision**: Unsafe red-line inputs should continue returning safety JSON and should not receive a formal report or `观察依据` section.

**Rationale**: The evidence section is only for safe formal reports. Creating partial formal reports for red-line inputs would weaken the existing safety boundary.

**Alternatives considered**:

- Include a safety explanation section in refused Markdown: rejected because red-line report requests currently return JSON and 009 must not change CLI output semantics.
- Add new refusal categories for evidence notes: rejected because the existing safety checks already cover the relevant red lines.
