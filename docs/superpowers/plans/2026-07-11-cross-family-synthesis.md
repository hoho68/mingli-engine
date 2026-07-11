# Cross-Family Synthesis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a separate integrated report layer that coordinates all ten evidence-backed rule families into structural, selection, timing, disagreement, and unavailable threads.

**Architecture:** `report_schema.py` builds `integrated_synthesis` only from existing formal conclusions and report audit metadata. `Report`, Markdown, HTML, safety scans, CLI tests, and the report acceptance baseline consume the derived string; no evidence or interpretation data is mutated.

**Tech Stack:** Python 3.12+, dataclasses, pytest, existing formal interpretation, report schema, renderers, CLI, and report acceptance baseline.

---

### Task 1: Define Integrated Synthesis Behavior

**Files:**
- Modify: `tests/unit/test_report_schema.py`

- [ ] Add failing tests for the five narrative parts, current guarded status, all expected relationship families, disagreement notes, and no unavailable families in the active report.
- [ ] Add a focused incomplete fixture that requires unavailable families to be named and prevents a complete-chain claim.
- [ ] Update the expected Report public field order with `integrated_synthesis` after `formal_synthesis`.
- [ ] Run schema tests and confirm failure because the field and builder do not exist.

### Task 2: Implement Cross-Family Composition

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/report_schema.py`

- [ ] Add `integrated_synthesis: str` to `Report`.
- [ ] Implement `build_integrated_synthesis(expanded_evidence, report_evidence_audit)` with stable family groups, reader signal excerpts, strength labels, disagreement preservation, and incomplete degradation.
- [ ] Build and attach the field in `build_report`.
- [ ] Include the field in `_major_body_sections` and the initial report safety scan.
- [ ] Run schema and safety tests until green.

### Task 3: Render And Prove Multi-Chart Behavior

**Files:**
- Modify: `src/mingli_engine/markdown.py`
- Modify: `src/mingli_engine/html.py`
- Modify: `tests/unit/test_markdown_renderer.py`
- Modify: `tests/unit/test_html_renderer.py`
- Modify: `tests/integration/test_calculate_report_cli.py`
- Modify: `tests/integration/test_generate_markdown_report.py`
- Modify: `tests/unit/test_report_schema.py`

- [ ] Add failing renderer tests for one `综合脉络` section after `正式知识综合` and before `结构分析`.
- [ ] Add CLI assertions for the section, guarded status, and high-risk relationship boundary.
- [ ] Extend the existing two-chart regression so integrated structural, selection, and timing text differs while evidence counts and conflicts remain stable.
- [ ] Implement Markdown and HTML rendering and run focused tests.

### Task 4: Extend Acceptance And Documentation

**Files:**
- Modify: `src/mingli_engine/report_acceptance.py`
- Modify: `tests/unit/test_report_acceptance.py`
- Modify: `tests/contract/test_report_acceptance_cli_contract.py`
- Modify: `docs/classical_sources/report_acceptance.md`
- Modify: `docs/classical_sources/coverage.md`

- [ ] Add a failing `integrated_cross_family_synthesis` acceptance expectation.
- [ ] Verify the integrated section contains all five narrative parts, exposes disagreement, contains no internal signal markers, and renders once in both formats.
- [ ] Document the cross-family gate and unchanged 111-unit, ten-family baseline.
- [ ] Run acceptance unit and contract tests.

### Task 5: Verify And Commit

**Files:**
- Modify only when an in-scope verification failure has a failing regression test.

- [ ] Run focused report, formal interpretation, renderer, CLI, acceptance, and safety tests.
- [ ] Run curation, materials-audit, and learning-reference quality scans.
- [ ] Run `uv run --with pytest python -m pytest -q` with sufficient timeout.
- [ ] Run `git diff --check`, review changed paths for evidence and raw-material boundaries, and commit the result.
