# Data Model: HTML 可视化报告

## HTMLReportDocument

Represents the complete static HTML document returned by safe report commands when `--format html` is selected.

Fields:

- `doctype`: Fixed document type declaration, expected to be `<!doctype html>`.
- `language`: Document language, expected to identify Chinese report content.
- `head`: Metadata and inline CSS needed for self-contained reading.
- `main`: The semantic report body rendered from the existing `Report` object.

Validation rules:

- Must be complete enough to open directly in a browser.
- Must include a charset declaration.
- Must include exactly one main report body.
- Must not include JavaScript.
- Must not reference external CSS, fonts, images, scripts, or network resources.
- Must preserve the formal report disclaimer.
- Must preserve the same major report order as Markdown.

## HTMLReportSection

Represents one semantic section in the HTML report body.

Fields:

- `heading`: Reader-facing heading text.
- `level`: Heading depth mirroring the Markdown report hierarchy.
- `body`: Escaped HTML content derived from one or more report fields.
- `section_kind`: Stable logical grouping, such as disclaimer, quick guide, basic data, structure observation, interpretation boundaries, action reflection, glossary, or ethics reminder.

Validation rules:

- Headings must appear in the same logical order as the Markdown report.
- `观察依据` must appear inside the structure-observation layer after ten-god summary and before structure analysis.
- Body text must be escaped before insertion into HTML.
- Section grouping must not add new interpretation conclusions.

## ReportFormatOption

Represents the user-facing output format accepted by report commands.

Allowed values:

- `markdown`: Existing behavior.
- `html`: New static HTML behavior.

Validation rules:

- Both `calculate-report` and `generate-report` must accept the same format choices.
- Unsupported format values continue to be rejected by the CLI argument parser.
- `markdown` behavior remains unchanged.

## HTMLReportSafetyContract

Represents automated checks that protect browser-facing report output.

Safe HTML checks:

- HTML output starts with `<!doctype html>`.
- HTML output contains required report sections in order.
- HTML output contains `观察依据`.
- HTML output includes chart source and assumptions.
- HTML output includes the disclaimer and ethics reminder.
- HTML output escapes special characters such as `<`, `>`, `&`, and quotes.
- HTML output contains no `<script>` tags or external resource references.

Unsafe and invalid-input checks:

- Red-line report requests return safety JSON instead of HTML.
- Missing required birth data returns the existing clarification JSON instead of HTML.
- Invalid input errors do not produce partial HTML documents.

State transitions:

1. User selects `--format html` on an existing report command.
2. Existing input parsing, safety review, chart calculation, and report building run unchanged.
3. If the request is unsafe or invalid, existing JSON/error behavior returns.
4. If a safe `Report` is available, the HTML renderer escapes and renders the report.
5. CLI writes the complete HTML document to stdout.
