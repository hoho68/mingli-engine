# Structure Observation Language Design

## Goal

Feature 006 will make the report's `第二层：结构观察` read more naturally for beginners while keeping the same careful, professional boundary. The current output already has a useful layered structure, but this layer still has several system-like sentences such as raw element counts, direct ten-god lists, and internal explanation phrases.

This feature changes wording only. It must not change chart calculation, interpretation rules, CLI commands, input JSON shapes, safety refusal behavior, Markdown heading order, or the plain-language labels added in feature 005.

## User Experience

A beginner reader should feel that the structure layer is explaining what can be observed, not dumping intermediate data. The report may still show useful counts and Bazi terms, but it should introduce them in ordinary Chinese and explain how to read them.

The selected tone is clear and professional, but smoother. It should avoid being overly emotional, mystical, or chatty. The output should sound like a careful report:

- It can say which signals are relatively concentrated or less visible.
- It can explain that counts are observation material.
- It can name ten-god relationships as structural clues.
- It must not turn those clues into fate verdicts, auspiciousness judgments, useful-god conclusions, strength conclusions, or event predictions.

## Scope

In scope:

- Polish the wording inside `第二层：结构观察`.
- Make five-element count text easier to read while preserving the actual counted values.
- Make ten-god text less like a raw list by adding a short reader-facing introduction.
- Make the basic structure observation sentence sound like report prose rather than an internal note.
- Keep the current layered Markdown sections and field ordering.
- Add tests that lock in the smoother wording and protect existing safety boundaries.

Out of scope:

- No new Bazi algorithm.
- No new `格局`, `用神`, `旺衰`, `大运流年`, `吉凶`, or outcome judgment.
- No broad rewrite of the full report.
- No changes to report input format, CLI flags, JSON safety response, or Markdown heading order.
- No UI, PDF export, account system, storage, or report archive.

## Proposed Changes

### Five-Element Observation

Keep the element counts visible, but introduce them as observation material. Instead of a terse system-like sentence, the report should say in plain language that these counts help the reader see where signals are more concentrated or less visible.

The wording should preserve transparency. If the current counted values are `木1、火2、土5、金5、水2`, the output should still expose those values, but with a smoother sentence around them.

### Ten-God Observation

Keep the per-pillar ten-god relationships, because they are useful context. Add a short introductory phrase so readers understand these are relationship clues by pillar position, not final conclusions.

The output should remain concise. This feature should not expand ten-god interpretation into long personality or destiny descriptions.

### Basic Structure Observation

Replace internal-sounding phrasing such as `基础结构观察：五行分布先看有无、多少与集中度。` with report prose that explains the same idea more naturally.

The sentence should keep the key meaning: the current layer is observing distribution, concentration, and absence/presence before making any deeper reading.

## Safety

All existing safety behavior remains mandatory:

- Unsafe focus topics still return safety JSON instead of Markdown.
- Formal reports still include the disclaimer and ethics reminder.
- Formal reports must not include prohibited absolute phrases such as `必定`, `注定`, `一定会`, or `死定`.
- The feature must not add deterministic marriage, lifespan/death timing, disaster prediction, medical/legal/financial advice, unauthorized third-party analysis, anxiety creation, or paid remedy language.

The wording polish should make the report easier to read without making it more certain.

## Testing Strategy

Add focused tests before implementation:

- Unit tests for interpretation text should expect smoother five-element, ten-god, and basic structure wording.
- Integration tests should verify generated Markdown still contains `第二层：结构观察` and no longer contains the selected internal-sounding phrases.
- Existing safety tests should continue to pass unchanged.
- Full project tests should pass with:

```powershell
uv run --with pytest python -m pytest
```

## Acceptance Criteria

- The `第二层：结构观察` section reads as clear report prose rather than raw program output.
- Five-element counts remain visible and accurate.
- Ten-god pillar information remains visible and is framed as structural observation.
- Existing 004 layered headings remain in the same order.
- Existing 005 reader-facing labels remain unchanged.
- Existing safety refusal behavior, disclaimer, ethics reminder, and prohibited phrase protections remain unchanged.
- No new predictive, fate-verdict, auspiciousness, useful-god, or luck-cycle conclusions are introduced.

## Implementation Boundaries

Prefer changing wording at the interpretation text boundary where the structure observation sentences are generated. Do not add renderer-level string replacement in `markdown.py`; the renderer should remain responsible for layout rather than domain prose.

If repeated wording helpers are needed, keep them small and local to the interpretation/report assembly area. Avoid introducing a broad localization framework for this small feature.

## Open Decisions

No product decisions remain open. The selected direction is: optimize only `第二层：结构观察`, using a clear professional tone that is smoother for beginner readers.
