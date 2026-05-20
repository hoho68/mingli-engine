# Research: 报告回归样例清单

## Decision: Use A Manifest-Based Regression Case List

**Decision**: Add a small manifest under `examples/` that lists representative report cases and their expected output category.

**Rationale**: The project already has multiple example inputs. A manifest gives maintainers one clear place to see which examples are part of the report regression set and why they matter. It also lets tests exercise every listed case without duplicating separate test functions for each new sample.

**Alternatives considered**:

- Hard-code all regression cases directly in the test file: rejected because the case list would be less visible to maintainers and harder to extend.
- Add a production registry for regression cases: rejected because the feature is a testing and example-documentation concern.
- Store generated Markdown outputs as fixtures: rejected because full snapshots would make safe wording improvements unnecessarily noisy.

## Decision: Avoid Full Markdown Snapshots

**Decision**: Validate durable report contracts and key phrases instead of comparing entire Markdown documents.

**Rationale**: The report language is intentionally evolving across features. Full snapshots would fail on harmless prose edits and make future readability work harder. Contract checks protect the important behavior without freezing every sentence.

**Alternatives considered**:

- Full Markdown snapshot files: rejected because they are brittle for reader-facing prose.
- Minimal smoke tests only checking exit codes: rejected because they would not protect 004-007 report contracts.

## Decision: Exercise The Existing CLI Paths

**Decision**: Regression tests should run manifest cases through the existing CLI commands with `--format markdown`.

**Rationale**: The risks being guarded are final user-visible report behavior and safety JSON output. CLI-level integration tests prove the complete chain still works: input example, parsing, calculation or chart loading, report assembly, safety review, and rendering.

**Alternatives considered**:

- Test only lower-level report builder functions: rejected because final Markdown and CLI safety behavior could still regress.
- Add a new command just for regression cases: rejected because 008 must not change user-facing CLI behavior.

## Decision: Reuse Existing Anonymized Examples First

**Decision**: Initial manifest entries should point to existing examples: automatic chart, external verified chart, and unsafe focus.

**Rationale**: These examples already cover the core happy paths and a red-line path. Reusing them keeps scope small and avoids inventing new birth data.

**Alternatives considered**:

- Add new sample birth data: rejected for the first version because existing examples are enough for the selected regression goals.
- Include every file under `examples/`: rejected because unsupported or validation-error examples have different purposes and should not be swept into report-regression semantics automatically.

## Decision: Keep Test Helpers Local

**Decision**: Manifest loading and report assertions should initially live in `tests/integration/test_report_regression_cases.py`.

**Rationale**: No production feature needs to read the manifest. Keeping helpers local avoids creating public APIs before there is a real consumer.

**Alternatives considered**:

- Add a reusable source module for manifest parsing: rejected as unnecessary until production code or multiple test modules need it.
- Move shared report assertions out of existing tests now: rejected because 008 can be implemented with minimal new structure.
