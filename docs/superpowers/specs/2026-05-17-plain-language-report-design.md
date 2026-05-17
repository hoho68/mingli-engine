# Plain-Language Report Design

## Goal

Improve the existing Bazi Markdown report so it reads like a polished report for ordinary readers rather than a program dump. The feature focuses on plain-language expression: translate machine-facing values into Chinese report wording and lightly polish key explanatory sentences.

This feature does not change chart calculation, interpretation rules, CLI commands, input JSON shapes, safety refusal behavior, or the layered report structure from feature 004.

## User Experience

A beginner reader should be able to scan the report without seeing raw internal labels such as `auto_calculated`, `medium`, `year`, `month`, `day`, `hour`, or `gregorian`.

The report should still keep the necessary Bazi terms, but the surrounding wording should make them easier to understand. For example, pillar names should appear as `年柱`, `月柱`, `日柱`, and `时柱`; source and confidence values should appear as readable Chinese phrases such as `系统自动排盘` and `中等可信度`.

The tone should stay careful and non-deterministic. The report may say a signal is "比较集中" or "适合先观察", but must not imply fixed outcomes, fate verdicts, auspiciousness, useful-god conclusions, pattern verdicts, luck-cycle predictions, or event predictions.

## Scope

In scope:

- Translate machine-facing report values into Chinese reader-facing labels.
- Polish the quick guide so its bullets sound like report guidance, not raw data output.
- Polish source and assumption wording while preserving transparent disclosure.
- Polish four-pillar row labels from internal names to Chinese pillar names.
- Polish structure, boundary, and action-reflection sentences only where wording is currently stiff.
- Add tests that verify the report no longer exposes selected raw machine labels in successful Markdown output.
- Preserve all existing safety checks, disclaimer, source disclosure, red-line refusal JSON, and prohibited phrase checks.

Out of scope:

- No new Bazi algorithm or interpretation depth.
- No new格局, 用神, 旺衰, 大运流年, 吉凶, or outcome judgment.
- No web UI, PDF export, account system, storage, or report archive.
- No CLI command, flag, or input schema changes.
- No broad rewrite of the whole report style into a long narrative.

## Proposed Changes

### Reader-Facing Value Labels

Add a small formatting boundary in the report assembly layer for values that currently leak as machine strings:

- calendar type: `gregorian` -> `公历`
- source type: `auto_calculated` -> `系统自动排盘`; `external_verified` -> `外部排盘已核对`
- confidence: `low` -> `低可信度`; `medium` -> `中等可信度`; `high` -> `高可信度`
- pillar name: `year` -> `年柱`; `month` -> `月柱`; `day` -> `日柱`; `hour` -> `时柱`
- gender placeholder: empty or unspecified machine wording should read as `未说明`

Unknown values should not be guessed. If a value is not recognized, the report should display a conservative Chinese fallback such as `未说明` or keep the original value only when disclosure is better than hiding it.

### Plain-Language Quick Guide

Keep the quick guide at three to five bullets. Rewrite bullets so they sound like direct reading guidance:

- source and confidence status in Chinese
- the main structure signal in a gentle sentence
- day-master wording as an observation coordinate, not an identity or destiny label
- boundary reminder
- focus-topic reflection cue when available

Example direction:

`这份盘里，土和金的信号比较集中，适合先从这两个方向看整体结构。`

### Plain-Language Body Wording

Keep the 004 layered structure exactly as it is. Only smooth the wording inside existing fields:

- source assumptions should read as transparent notes rather than raw metadata
- structure observation should explain that counts are observation material, not a final strength model
- action suggestions should remain practical reflection prompts tied to the safe focus topic
- boundary text should remain visible and concise

## Safety

All existing safety behavior remains mandatory:

- Unsafe focus topics still return exit code `3` with safety JSON instead of Markdown.
- Formal reports still include the disclaimer and ethics reminder.
- Formal reports must not include prohibited absolute phrases: `必定`, `注定`, `一定会`, `死定`.
- The feature must not introduce deterministic marriage, lifespan/death timing, disaster prediction, professional advice, unauthorized third-party analysis, anxiety creation, or paid remedy language.

The language polish should make the report warmer without making it more certain.

## Testing Strategy

Add and update tests at the report schema, renderer, integration, and safety levels:

- Schema tests verify reader-facing labels are used for calendar type, source type, confidence, and pillar names.
- Markdown renderer tests verify layered headings remain unchanged after wording changes.
- Integration tests verify both `calculate-report` and `generate-report` successful Markdown outputs include plain-language labels and do not include selected raw machine labels.
- Safety tests continue to verify prohibited phrases are absent and red-line focus topics return JSON.

The project test command remains:

```powershell
uv run --with pytest python -m pytest
```

## Acceptance Criteria

- A successful auto-calculated report shows `系统自动排盘`, `中等可信度`, `公历`, and Chinese pillar names.
- A successful externally verified report shows `外部排盘已核对` or equivalent reader-facing source wording.
- Successful Markdown reports do not expose `auto_calculated`, `external_verified`, `medium`, `gregorian`, `year：`, `month：`, `day：`, or `hour：` in reader-facing body text.
- The quick guide reads as plain guidance and still has three to five bullets.
- Existing layered headings from 004 remain in the same order.
- Existing source disclosure remains visible.
- Existing safety refusal behavior and prohibited phrase protections remain unchanged.

## Implementation Boundaries

Prefer small helper functions in `report_schema.py` because that layer already prepares report text. Do not move domain logic into `markdown.py`; the renderer should remain a simple layout boundary.

If tests reveal repeated label mapping needs, use small dictionaries or helper functions rather than scattering string replacements throughout the code.

## Open Decisions

No open product decisions remain. The selected direction is: completely beginner-friendly wording, implemented as machine-field translation plus key sentence polish.
