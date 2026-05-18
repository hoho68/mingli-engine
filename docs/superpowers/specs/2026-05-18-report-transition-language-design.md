# Report Transition Language Design

## Goal

Feature 007 will make the whole Markdown report read more like one coherent report instead of several adjacent modules. Features 004, 005, and 006 already made the report layered, reader-friendly, and smoother inside `第二层：结构观察`. The next improvement is to add light transition wording so each layer explains why it exists and how the reader should move to the next layer.

This feature changes wording only. It must not change chart calculation, interpretation rules, CLI commands, input JSON shapes, safety refusal behavior, Markdown heading order, or the reader-facing labels and structure wording already completed in features 005 and 006.

## User Experience

A beginner reader should understand the reading path:

1. `快速导读` gives the shortest route through the report.
2. `第一层：基础资料` shows source and assumptions, not conclusions.
3. `第二层：结构观察` shows observable structure signals.
4. `第三层：解读边界` explains what the report must not overclaim.
5. `第四层：行动反思` turns safe observations into review prompts.

The tone should remain clear, professional, and concise. The transitions should make the report feel connected, but they should not turn it into a long essay or a persuasive narrative.

## Scope

In scope:

- Add or polish short transition sentences around existing report layers.
- Make the quick guide lead more naturally into the layered reading path.
- Make the first layer explicitly say that source data and assumptions are the basis, not the conclusion.
- Make the second layer lead into interpretation boundaries.
- Make the third layer explain that boundaries protect against overreading, not that the report has no value.
- Make the fourth layer open with a clearer reflection-oriented bridge.
- Preserve all existing headings, section order, CLI behavior, safety behavior, and calculation output.
- Add tests that verify the new transitions appear and safety boundaries remain unchanged.

Out of scope:

- No new Bazi algorithm.
- No new `格局`, `用神`, `旺衰`, `大运流年`, `吉凶`, or outcome judgment.
- No broad rewrite into a long narrative report.
- No UI, PDF export, account system, storage, or report archive.
- No changes to command names, flags, JSON input shape, or safety JSON shape.

## Proposed Changes

### Quick Guide Bridge

Keep the quick guide short. Add a final or near-final sentence that tells the reader how to use the following layers. The wording should be practical, such as telling the reader to first check source assumptions, then read structure observations, then use the boundary and reflection sections.

The quick guide must remain concise and should still fit the current three-to-five bullet expectation unless implementation shows a better existing pattern.

### First Layer Bridge

After source and assumption material, add a short sentence that explains this layer is the evidence base. It should say, in plain language, that birth data, source type, calendar assumptions, timezone, solar terms, and true-solar-time status are inputs and assumptions, not interpretation conclusions.

### Second Layer Bridge

After structure observation, add a short transition that says these signals are observation clues and need boundaries before deeper interpretation. This should point naturally to `第三层：解读边界`.

### Third Layer Bridge

After interpretation boundaries, add wording that frames boundaries positively: they prevent overclaiming and keep the report useful for self-reflection. The transition should lead into `第四层：行动反思`.

### Fourth Layer Bridge

Add or polish the opening of action reflection so it tells the reader how to convert observations into small review questions or practical notes. It must avoid promising outcomes or giving professional advice.

## Safety

All existing safety behavior remains mandatory:

- Unsafe focus topics still return safety JSON instead of Markdown.
- Formal reports still include the disclaimer and ethics reminder.
- Formal reports must not include prohibited absolute phrases such as `必定`, `注定`, `一定会`, or `死定`.
- The feature must not add deterministic marriage, lifespan/death timing, disaster prediction, medical/legal/financial advice, unauthorized third-party analysis, anxiety creation, or paid remedy language.

Transition wording must make the report easier to follow without making it more certain.

## Testing Strategy

Add focused tests before implementation:

- Unit tests for report assembly should verify transition wording appears in the expected report fields.
- Markdown renderer or integration tests should verify final Markdown includes the transitions while preserving 004 heading order.
- Integration tests should verify both automatic chart and external chart flows keep the transition wording.
- Safety tests should continue to verify prohibited absolute phrases and red-line refusal behavior.
- Full project tests should pass with:

```powershell
uv run --with pytest python -m pytest
```

## Acceptance Criteria

- A successful Markdown report reads as a connected sequence from quick guide to action reflection.
- Existing 004 heading order remains unchanged.
- Existing 005 reader-facing labels remain unchanged.
- Existing 006 structure observation wording remains unchanged.
- The first layer clearly frames source data and assumptions as basis, not conclusion.
- The second layer clearly frames structure observations as clues, not final judgments.
- The third layer clearly frames boundaries as protection against overreading.
- The fourth layer clearly frames action suggestions as reflection prompts, not promised outcomes.
- Existing safety refusal behavior, disclaimer, ethics reminder, and prohibited phrase protections remain unchanged.
- No new predictive, fate-verdict, auspiciousness, useful-god, strength, or luck-cycle conclusions are introduced.

## Implementation Boundaries

Prefer adding transition wording in the report assembly layer where existing report fields are composed. If a transition belongs inside an existing interpretation field, keep it close to that field's current generator and avoid renderer-level replacement. `markdown.py` should remain a layout boundary and should not contain domain-specific transition logic unless the existing design already expects purely structural section text there.

Avoid a broad rewrite of all prose. This feature should add connective tissue, not change the report's meaning or turn concise sections into long paragraphs.

## Open Decisions

No product decisions remain open. The selected direction is: preserve the existing layered Markdown report and add concise transition wording that helps a beginner move through the report in a safe reading order.
