# HTML Visual Report Design

## Context

The project can now generate safe, layered Bazi reports as Markdown from both
automatically calculated charts and externally verified charts. Features 004
through 009 improved readability, plain-language structure, transition wording,
regression coverage, and observation-basis notes.

The next natural extension from the original roadmap is an HTML visual report.
For the first version, the goal is not to build a full Web app. The goal is to
give the existing report engine one more output format that is easier to read,
save, print, and later convert into PDF.

## Goal

Add a pure static HTML output format for formal safe reports.

Users should be able to run the existing report commands with `--format html`
and receive a complete, self-contained HTML document that preserves the same
report content, safety boundaries, and reading order as the current Markdown
report.

## Decisions Confirmed

- Output path: extend existing CLI report commands with `--format html`.
- Commands covered: `calculate-report` and `generate-report`.
- Layout: single-page reading layout.
- Interactivity: none for the first version.
- Assets: no JavaScript and no external CSS, fonts, images, or network
  dependencies.
- Domain scope: no new Bazi calculations, no new interpretation conclusions,
  no new input shape, and no Web form.

## User Value

Readers get a report that feels more polished than raw Markdown while keeping
the same cautious language and transparent structure.

Maintainers get a small, testable display layer that can later support PDF
export, richer visual components, or a Web preview without changing the report
model again.

## Scope

### In Scope

- Add `html` as an accepted format for `calculate-report`.
- Add `html` as an accepted format for `generate-report`.
- Render the existing `Report` object to a complete HTML document.
- Preserve the current report order:
  - title
  - disclaimer
  - quick guide
  - first layer: source and basic data
  - second layer: structure observation
  - observation basis
  - third layer: interpretation boundaries
  - fourth layer: action reflection
  - glossary
  - ethics reminder
- Use semantic HTML headings and sections.
- Include inline CSS for a calm report-reading layout.
- Escape user/chart/report text so arbitrary content cannot break HTML markup.
- Keep safety JSON behavior unchanged for red-line requests.
- Keep invalid-input behavior unchanged.
- Add tests for renderer output, CLI behavior, safety behavior, and HTML
  escaping.

### Out of Scope

- No JavaScript.
- No collapsible sections, tabs, filters, or client-side interactions.
- No Web page input form or preview page.
- No browser server or app runtime.
- No charts, SVG visualizations, element wheels, or dashboard widgets.
- No PNG/PDF export in this feature.
- No new report fields.
- No new Bazi calculations, auspiciousness claims, useful-god verdicts,
  strength verdicts, luck-cycle judgments, or event predictions.
- No external assets or CDN dependencies.

## Proposed UX

The HTML document should read like a polished long-form report, not a dashboard.

The first viewport should show:

- the report title
- a compact subtitle or label indicating it is a structured Bazi report
- the disclaimer near the top
- the quick guide immediately after the disclaimer

Each major report layer should be visually separated with simple spacing,
subtle borders, or neutral background bands. The design should prioritize
readability and printability over decoration.

The first version should avoid heavy visual metaphors. It should not use
fortune-telling imagery, decorative mysticism, or dramatic colors. The tone
should stay calm, reviewable, and practical.

## HTML Contract

The renderer should produce a complete HTML document:

```html
<!doctype html>
<html lang="zh-CN">
...
</html>
```

The document should include:

- `<meta charset="utf-8">`
- a meaningful `<title>`
- a `<style>` block with inline CSS
- one `<main>` element
- semantic `<section>` elements for report groups
- heading levels that mirror the current Markdown hierarchy

The output should not include:

- `<script>`
- remote URLs
- inline event handlers
- raw unescaped user-provided text

## CLI Behavior

The existing Markdown behavior should remain valid:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

The feature adds equivalent HTML output:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format html
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format html
```

For unsafe red-line inputs, both report commands should continue returning
safety JSON with the existing non-zero exit code. They should not return a
formal HTML report.

## Suggested Code Shape

Add one focused renderer module:

```text
src/mingli_engine/html.py
```

The module should expose one function:

```python
def render_html_report(report: Report) -> str:
    ...
```

The CLI should choose the renderer based on `args.format` after `build_report`
has produced a safe report.

The HTML renderer should stay presentation-only. It should not call the chart
calculator, safety checker, or interpretation builder.

## Testing Strategy

Use test-first implementation.

Recommended tests:

- Unit test that `render_html_report()` returns a complete HTML document.
- Unit test that the HTML contains the same major report sections in the same
  order as Markdown.
- Unit test that report text is HTML-escaped.
- Unit test that no `<script>` tag appears in generated HTML.
- Integration test that `calculate-report --format html` returns HTML for a
  safe automatic-chart input.
- Integration test that `generate-report --format html` returns HTML for a safe
  external verified chart input.
- Regression test extension so existing safe report cases also exercise HTML
  output or a dedicated HTML report contract.
- Safety test that unsafe red-line report requests still return safety JSON and
  never output `<!doctype html>`.
- Full suite verification after implementation.

## Success Criteria

- Safe `calculate-report --format html` outputs a complete static HTML report.
- Safe `generate-report --format html` outputs a complete static HTML report.
- Markdown output remains unchanged.
- Red-line and invalid-input behavior remains unchanged.
- HTML output preserves report section order and includes `观察依据`.
- HTML output escapes report text safely.
- HTML output contains no JavaScript and no external resources.
- All existing tests and the new HTML tests pass.

## Risks And Mitigations

- Risk: HTML output drifts from Markdown content.
  - Mitigation: Render from the same `Report` object and test section order.
- Risk: HTML introduces injection or broken markup.
  - Mitigation: Escape all report text and add explicit escaping tests.
- Risk: Scope expands into a Web app.
  - Mitigation: Keep 010 to CLI HTML output only; defer Web input and preview.
- Risk: Visual styling makes the report feel too decorative or deterministic.
  - Mitigation: Use restrained report styling and preserve existing safety text.

## Self-Check

- No TBD, TODO, or unresolved placeholders.
- The feature is focused on one output format and one layout.
- The design does not add new domain judgments or calculations.
- The design keeps safety JSON behavior unchanged.
- The design can be converted into Spec Kit requirements and tests.
