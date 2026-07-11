# Report Acceptance Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only four-scenario report acceptance matrix and JSON CLI that certifies the current 111-unit, ten-family knowledge baseline for release use with guardrails.

**Architecture:** A new `report_acceptance.py` module evaluates production report construction and rendering with in-memory synthetic profiles plus one controlled degradation fixture. Dataclasses in `models.py` expose deterministic results, and `cli.py` serializes the summary without mutating corpus or intake data.

**Tech Stack:** Python 3.12+, dataclasses, pytest, existing report builder, safety review, Markdown/HTML renderers, argparse CLI.

---

### Task 1: Define Acceptance Models And Scenarios

**Files:**
- Modify: `src/mingli_engine/models.py`
- Create: `src/mingli_engine/report_acceptance.py`
- Create: `tests/unit/test_report_acceptance.py`

- [ ] Write failing tests for the ordinary, conflict, high-risk rejection, and unavailable-degradation case results, plus blocked summary aggregation.
- [ ] Run `uv run --with pytest python -m pytest tests/unit/test_report_acceptance.py -q` and confirm collection fails because the module and dataclasses do not exist.
- [ ] Add frozen `ReportAcceptanceCaseResult` and `ReportAcceptanceSummary` dataclasses.
- [ ] Implement the four read-only evaluators and `build_report_acceptance_summary()` with stable ordering and `report_acceptance_v1` baseline id.
- [ ] Run the unit tests and confirm all acceptance cases pass.

### Task 2: Expose The Acceptance CLI

**Files:**
- Modify: `src/mingli_engine/cli.py`
- Create: `tests/contract/test_report_acceptance_cli_contract.py`

- [ ] Write a failing subprocess contract test for `report-acceptance-summary` and assert the command is initially unknown.
- [ ] Add the CLI handler and parser entry using the existing dataclass JSON serializer.
- [ ] Assert `ready_with_guardrails`, four passed cases, 111 evidence units, ten families, no missing families, the current conflict id, and no profile fields in output.
- [ ] Run the unit and contract tests and confirm they pass.

### Task 3: Document And Verify The Release Baseline

**Files:**
- Create: `docs/classical_sources/report_acceptance.md`
- Modify: `docs/classical_sources/README.md`
- Modify: `docs/classical_sources/coverage.md`

- [ ] Document the four scenarios, JSON command, current expected counts, guardrails, and no-mutation boundary.
- [ ] Link the acceptance baseline from the classical-source index and coverage packet.
- [ ] Run focused report, renderer, CLI, safety, and acceptance tests.
- [ ] Run the materials, learning-reference, and evidence quality scans and confirm no failures.
- [ ] Run `uv run --with pytest python -m pytest -q` with a sufficient timeout.
- [ ] Run `git diff --check`, review changed paths for boundary compliance, and commit the result.
