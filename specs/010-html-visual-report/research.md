# Research: HTML 可视化报告

## Decision: Add A Dedicated HTML Renderer

**Decision**: Add `src/mingli_engine/html.py` with a public `render_html_report(report)` function.

**Rationale**: HTML is a presentation format with escaping and document-structure concerns that do not belong in the Markdown renderer or report schema. A dedicated renderer keeps `Report` as the shared source of truth while allowing Markdown and HTML output to evolve independently.

**Alternatives considered**:

- Convert rendered Markdown to HTML: rejected because it would add parser behavior or brittle string transforms, and it would make semantic section markup harder to control.
- Put HTML directly in `report_schema.py`: rejected because report assembly should remain format-agnostic.
- Add HTML as methods on `Report`: rejected because the model should remain a data contract, not a renderer.

## Decision: Use Standard Library Escaping

**Decision**: Escape report text with Python standard library HTML escaping before inserting it into the HTML document.

**Rationale**: 010 does not need a template engine or new dependency. The output is a small static document assembled from known `Report` fields, and the critical safety requirement is correct escaping of user/source text.

**Alternatives considered**:

- Add a template engine: rejected as unnecessary dependency and scope for a single static report document.
- Trust report text because it comes from internal dataclasses: rejected because report fields can include user-provided topics, birthplace, source notes, or externally verified chart text.
- Escape only known user fields: rejected because future report fields could accidentally carry untrusted text; renderer-level escaping is safer.

## Decision: Extend Existing Format Choices

**Decision**: Extend `calculate-report` and `generate-report` so `--format` accepts both `markdown` and `html`.

**Rationale**: The existing commands already represent formal report generation. Adding another format choice is more discoverable and avoids duplicate command semantics.

**Alternatives considered**:

- Add `calculate-report-html` and `generate-report-html`: rejected because it duplicates command behavior and violates the scope guard against new user-facing commands.
- Add a global export command: rejected because 010 is not a storage or file-conversion feature.
- Add file output flags: rejected because current CLI writes reports to stdout and 010 should preserve that model.

## Decision: Keep HTML Pure Static

**Decision**: Generate a complete static HTML document with inline CSS, no JavaScript, and no external assets.

**Rationale**: Static HTML is easy to save, inspect, print, and later convert to PDF. It also avoids introducing browser-execution risk or external network dependencies.

**Alternatives considered**:

- Add collapsible sections: rejected for 010 because it requires JavaScript or CSS state controls and complicates testing.
- Add charts or visual widgets: rejected because they introduce a new visualization contract beyond the confirmed single-page reading layout.
- Use external CSS or fonts: rejected because the report should be self-contained and work offline.

## Decision: Test Structure, Not Full HTML Snapshots

**Decision**: Use focused unit and integration tests that verify document completeness, section order, escaping, no-script/no-external-resource constraints, CLI dispatch, and safety behavior.

**Rationale**: Full HTML snapshots would make style changes expensive. Structural assertions protect the contract while leaving room to refine visual spacing and copy.

**Alternatives considered**:

- Full HTML snapshots: rejected as brittle and too strict for a presentation layer.
- Browser screenshot tests: rejected for 010 because the initial requirement is static structure, not pixel-perfect layout.
- Only CLI smoke tests: rejected because escaping and no-script constraints need direct renderer coverage.

## Decision: Keep Safety And Invalid-Input Behavior Unchanged

**Decision**: HTML format is only available after the same existing report safety and input-validity checks pass.

**Rationale**: HTML is a formal report format. Unsafe red-line requests and invalid inputs must not receive partial formal report documents.

**Alternatives considered**:

- Return a styled HTML refusal page: rejected because current report commands return safety JSON for red-line cases and 010 must preserve output semantics.
- Render partial HTML for missing input: rejected because the constitution requires missing required birth data to stop full report generation.
