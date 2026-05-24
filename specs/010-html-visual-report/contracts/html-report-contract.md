# HTML Report Contract: HTML 可视化报告

## Scope

This contract defines static HTML output for existing formal safe report commands. It does not add new commands, input schemas, chart calculations, report fields, Web forms, JavaScript interactions, PNG export, or PDF export.

## CLI Contract

Existing Markdown commands remain valid:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

New HTML format commands:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format html
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format html
```

Expected safe HTML behavior:

- Exit code is `0`.
- Standard output starts with `<!doctype html>`.
- Standard output contains one complete HTML document.
- Standard error is empty.

Expected unsafe red-line behavior:

- Existing safety JSON behavior remains unchanged.
- Exit code remains the existing safety refusal code.
- Standard output is JSON, not HTML.
- Standard output must not start with `<!doctype html>`.

Expected invalid-input behavior:

- Existing invalid input and clarification behavior remains unchanged.
- Invalid input must not produce partial HTML.

## HTML Document Contract

Every safe HTML report MUST include:

```html
<!doctype html>
<html lang="zh-CN">
```

The document head MUST include:

- `<meta charset="utf-8">`
- a meaningful `<title>`
- inline CSS inside `<style>`

The document body MUST include:

- one `<main>` element
- semantic sections for the formal report
- headings that preserve the report hierarchy

The document MUST NOT include:

- `<script>`
- inline event handlers such as `onclick`
- external stylesheets
- external fonts
- external images
- CDN or remote URLs

## Report Content Contract

HTML output MUST preserve these report groups in order:

```text
title
disclaimer
quick guide
basic data
structure observation
interpretation boundaries
action reflection
glossary
ethics reminder
```

Inside the structure-observation group, HTML output MUST preserve this order:

```text
four-pillar and five-element summary
ten-god summary
observation basis
structure analysis
personality tendencies
```

The HTML report MUST contain all formal report fields that Markdown currently renders:

- disclaimer
- quick guide
- chart card
- assumptions
- four pillars summary
- five elements summary
- ten gods summary
- evidence notes
- structure analysis
- personality tendencies
- interpretation boundaries
- strengths and issues
- phase overview
- action suggestions
- glossary
- ethics reminder

## Escaping And Resource Contract

All report text MUST be escaped before insertion into HTML.

At minimum, tests MUST verify safe rendering of:

- `<`
- `>`
- `&`
- double quote
- single quote

The output MUST not allow source notes, focus topics, birthplace text, or other report fields to create tags, attributes, scripts, or external resource links.

## Safety Contract

HTML presentation MUST keep the same domain boundaries as Markdown:

- It presents cultural interpretation and self-reflection, not scientific prediction.
- It includes the disclaimer.
- It exposes chart source and assumptions.
- It avoids absolute destiny language.
- It does not add useful-god verdicts, strength verdicts, luck-cycle judgments, auspiciousness claims, or real-world event predictions.
- It does not replace medical, legal, psychological, or investment advice.

Unsafe red-line report requests MUST continue to return safety JSON and MUST NOT generate a formal HTML report.

## Regression Contract

Automated validation MUST verify:

- safe automatic-chart HTML output
- safe external-verified HTML output
- required section order
- `观察依据` placement
- HTML escaping
- no scripts or external resources
- unsafe red-line requests still return safety JSON
- existing Markdown report tests continue passing
