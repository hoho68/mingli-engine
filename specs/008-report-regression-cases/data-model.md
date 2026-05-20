# Data Model: 报告回归样例清单

## ReportRegressionCase

Represents one manifest entry for a report regression example.

Fields:

- `id`: Stable unique identifier for the case.
- `kind`: Expected output category. Supported values are `safe_markdown` and `safety_json`.
- `command`: Existing report command used for the case. Supported values are `calculate-report` and `generate-report`.
- `input`: Project-relative path to the example input file.
- `purpose`: Human-readable reason this case exists.
- `source_type`: Optional source category for safe Markdown cases. Supported values are `auto_calculated` and `external_verified`.
- `expected_category`: Optional red-line category for safety JSON cases.

Validation rules:

- `id`, `kind`, `command`, `input`, and `purpose` are required for every case.
- `id` values must be unique.
- `input` must point to an existing file.
- `kind` must be either `safe_markdown` or `safety_json`.
- `command` must be either `calculate-report` or `generate-report`.
- `source_type` is required when `kind` is `safe_markdown`.
- `expected_category` is required when `kind` is `safety_json`.

## ReportRegressionManifest

Represents the complete regression sample list.

Fields:

- A list of `ReportRegressionCase` objects.

Validation rules:

- Must not be empty.
- Must include at least one `safe_markdown` case using automatic chart calculation.
- Must include at least one `safe_markdown` case using an external verified chart.
- Must include at least one `safety_json` case for a red-line focus topic.
- Every listed case must be exercised by automated validation.

## ReportContractCheck

Represents durable assertions applied to generated outputs.

Safe Markdown checks:

- Formal Markdown report heading is present.
- Quick guide and four layered headings are present in order.
- Source disclosure and assumptions remain visible.
- Feature 005 reader-facing labels remain visible.
- Feature 006 structure observation wording remains visible.
- Feature 007 transition wording remains visible.
- Selected raw machine labels are absent.
- Selected absolute destiny phrases are absent.
- Source-specific expectations are honored.

Safety JSON checks:

- Exit code indicates safety refusal.
- Output parses as JSON.
- `allowed` is `false`.
- Expected red-line category is present.
- Output does not start with a Markdown report heading.

State transitions:

1. Manifest case is loaded.
2. Input path is resolved and validated.
3. Existing CLI command is run with `--format markdown`.
4. Output is classified according to `kind`.
5. Durable contract checks are applied.
