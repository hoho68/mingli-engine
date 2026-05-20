# Report Regression Cases Design

## Context

The project now generates layered, safer, and more readable Bazi Markdown reports. Features 004 through 007 improved the report in sequence: layered reading order, reader-facing labels, smoother structure observation language, and transition wording between report layers.

Feature 008 will add a small regression sample library so future report changes can be checked against representative inputs. The goal is stability, not visual presentation. This feature should make it harder to accidentally break headings, source labels, transition wording, structure observation wording, safety refusal behavior, or other report contracts.

## Selected Direction

Use a manifest-based regression sample library.

The manifest will list existing representative example inputs and the expected behavior for each case. Tests will read the manifest and run the existing CLI paths against those inputs. This gives the project one place to describe which examples matter and why, while avoiding brittle full Markdown snapshots.

## Scope

In scope:

- Add a regression case manifest, likely `examples/report-regression-cases.json`.
- Include existing safe automatic-chart report input.
- Include existing safe external-verified chart report input.
- Include existing unsafe focus-topic input.
- Add integration tests that read the manifest and check expected behavior.
- Verify safe cases still produce Markdown reports with the key 004-007 report contracts.
- Verify unsafe cases still return safety JSON instead of Markdown.

Out of scope:

- No new Bazi algorithm work.
- No new interpretation conclusions.
- No CLI command or flag changes.
- No full Markdown snapshot files.
- No HTML, PDF, PNG, or visual report export.
- No stored report archive.

## Regression Case Types

### Safe Automatic Chart Case

Uses the existing automatic birth-profile example. It should run through the automatic chart calculation path and produce Markdown.

The test should confirm the report includes:

- `# 八字结构化报告`
- `## 快速导读`
- The four layered headings from feature 004.
- Reader-facing labels from feature 005, such as `系统自动排盘`, `中等可信度`, `公历`, and pillar labels.
- Structure observation wording from feature 006.
- Transition wording from feature 007.
- No selected raw machine labels in reader-facing output.
- No selected absolute destiny phrases.

### Safe External Verified Case

Uses the existing external verified chart example. It should run through the external chart report path and produce Markdown.

The test should confirm:

- External source wording such as `外部排盘已核对` remains visible.
- The external source note remains visible.
- The same report structure, labels, structure observation wording, and transition wording remain visible.
- The report is not mislabeled as an automatic chart case.

### Unsafe Focus Case

Uses an existing unsafe focus-topic example. It should run through the report command with Markdown requested, but return safety JSON instead of Markdown.

The test should confirm:

- Exit code is `3`.
- Output parses as JSON.
- `allowed` is `false`.
- The expected red-line category is present.
- Output does not start with a Markdown report heading.

## Manifest Shape

The manifest should stay simple and readable. A likely shape:

```json
[
  {
    "id": "safe-auto-gregorian",
    "kind": "safe_markdown",
    "command": "calculate-report",
    "input": "examples/birth-profile.auto-gregorian.json",
    "source_type": "auto_calculated"
  },
  {
    "id": "safe-external-verified",
    "kind": "safe_markdown",
    "command": "generate-report",
    "input": "examples/bazi-chart.external-verified.json",
    "source_type": "external_verified"
  },
  {
    "id": "unsafe-lifespan-focus",
    "kind": "safety_json",
    "command": "calculate-report",
    "input": "examples/birth-profile.unsafe-focus.json",
    "expected_category": "lifespan_or_death_timing"
  }
]
```

The implementation can adjust exact field names if the tests remain clear, but the manifest should avoid embedding long report text or snapshots.

## Testing Strategy

Add one integration test module, likely `tests/integration/test_report_regression_cases.py`.

The tests should:

1. Load the manifest.
2. Validate that each listed input path exists.
3. Run each case through the CLI with `--format markdown`.
4. For safe Markdown cases, assert shared report contracts and case-specific source expectations.
5. For unsafe cases, assert safety JSON behavior.

This keeps regression checks focused on durable contracts rather than exact full-report wording.

## Safety Boundaries

The regression sample library must preserve the existing safety posture:

- Safe examples remain cultural interpretation and reflection material.
- Unsafe focus topics continue to be refused.
- Tests should guard against selected absolute language such as `必定`, `注定`, `一定会`, and `死定`.
- The feature must not add new prediction, auspiciousness, useful-god, strength, luck-cycle, or real-world event conclusions.

## Success Criteria

- The manifest contains at least three cases: safe automatic chart, safe external verified chart, and unsafe focus-topic refusal.
- Every manifest case is exercised by automated tests.
- Safe cases verify the key report contracts from features 004-007.
- Unsafe cases verify safety JSON instead of Markdown.
- Full test suite passes.

## Implementation Notes

Keep this feature small. Prefer a manifest and tests over new application logic. If a helper is needed, keep it local to the test module unless production code genuinely needs to understand regression cases.
