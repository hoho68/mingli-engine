# Report Release Readiness Implementation Plan

> **For agentic workers:** Use test-driven development and verify every red-green cycle before proceeding.

**Goal:** Turn the tracked anonymous report regression matrix into a machine-readable release gate and documented report-enablement workflow.

**Architecture:** A new `report_release.py` module validates `examples/report-regression-cases.json`, builds or rejects each scenario in process using production code, compares Markdown and HTML contracts, depends on `report_acceptance_v1`, and returns privacy-safe dataclasses. `cli.py` exposes the summary without writing files.

**Tech Stack:** Python 3.12+, dataclasses, pathlib/json/hashlib, existing chart/report/safety/rendering services, pytest, and argparse CLI.

---

### Task 1: Define Release Models And Manifest Contract

**Files:**
- Modify: `src/mingli_engine/models.py`
- Create: `tests/unit/test_report_release.py`

- [ ] Add failing tests for the five stable case ids, scenario counts, result fields, and privacy-safe serialization.
- [ ] Add invalid manifest tests for missing fields, duplicate ids, unsupported kinds/commands, missing inputs, and path escape.
- [ ] Define frozen release case and summary dataclasses plus `ReportReleaseError`.

### Task 2: Implement In-Process Matrix Execution

**Files:**
- Create: `src/mingli_engine/report_release.py`
- Modify: `tests/unit/test_report_release.py`

- [ ] Load and validate the tracked manifest without exposing its input paths.
- [ ] Build safe and guarded reports through production code and render both Markdown and HTML.
- [ ] Verify evidence, four action tracks, sanitization, format consistency, high-risk narrowing, and rejection withholding.
- [ ] Compute only an aggregate distinct-output count; do not return report bodies or fingerprints.
- [ ] Fail closed when any case or the existing report acceptance gate fails.

### Task 3: Add CLI And Regression Contracts

**Files:**
- Modify: `src/mingli_engine/cli.py`
- Create: `tests/contract/test_report_release_cli_contract.py`
- Modify: `tests/integration/test_report_regression_cases.py`

- [ ] Add `report-release-summary` for the fixed tracked manifest; inject alternate manifests only through Python tests.
- [ ] Verify JSON status, counts, checks, guardrails, and absence of private profile fields and values.
- [ ] Extend existing safe/high-risk regression assertions for formal synthesis, integrated synthesis, four action tracks, and cross-format output.

### Task 4: Document Enablement

**Files:**
- Create: `docs/classical_sources/report_release.md`
- Modify: `docs/classical_sources/README.md`
- Modify: `docs/classical_sources/coverage.md`

- [ ] Document the release command, expected baseline, case matrix, failure interpretation, privacy boundary, and enablement sequence.
- [ ] Preserve the existing 111-unit, ten-family, four-action-track guarded baseline.

### Task 5: Verify, Review, And Commit

- [ ] Run focused release, acceptance, report regression, CLI, renderer, and safety tests.
- [ ] Run curation, materials-audit, and learning-reference quality scans.
- [ ] Run the full repository regression.
- [ ] Run `git diff --check`, independently review the changes, verify no raw/source-library/013/012 mutation, and commit.
