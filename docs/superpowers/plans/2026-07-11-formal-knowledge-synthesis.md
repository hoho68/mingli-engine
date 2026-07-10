# Formal Knowledge Synthesis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reader-facing formal knowledge synthesis that activates all ten evidence-backed rule families in generated reports while preserving audit and safety boundaries.

**Architecture:** `report_schema.py` owns a pure formatter over existing formal conclusions and audit metadata. `Report` stores the resulting text, while Markdown and HTML render it in the observation layer; no source-library, 013, 012, or extraction data changes are required.

**Tech Stack:** Python 3.12+, dataclasses, pytest, existing Markdown/HTML renderers and safety checks.

---

### Task 1: Define synthesis behavior with failing schema tests

**Files:**
- Modify: `tests/unit/test_report_schema.py`

- [ ] Add a test that builds a report and asserts `formal_synthesis` is non-empty, contains the three group titles, contains every enabled rule-family marker exactly once, states `完整（含护栏）`, and retains 111 traced evidence units.
- [ ] Add a focused formatter test with one `disputed` conclusion and one `unavailable` conclusion, asserting that disagreement text, incomplete status, and unavailable boundaries are visible.
- [ ] Run `uv run --with pytest python -m pytest tests/unit/test_report_schema.py -q` and confirm failure because `Report.formal_synthesis` and `_build_formal_synthesis` do not exist.

### Task 2: Implement the synthesis model and builder

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/report_schema.py`

- [ ] Add `formal_synthesis: str` to `Report` immediately after `evidence_notes`.
- [ ] Add stable group definitions for the ten rule families and strength labels for `decided`, `candidate`, `weakly_supported`, `disputed`, and `unavailable`.
- [ ] Implement `_build_formal_synthesis(expanded_evidence, report_evidence_audit)` so each enabled conclusion appears once, missing/unavailable families are named, disagreement notes are preserved, and sensitive/high-risk material receives a non-deterministic boundary.
- [ ] Build the synthesis in `build_report`, include it in `Report`, `_major_body_sections`, and both safety scan inputs.
- [ ] Run `uv run --with pytest python -m pytest tests/unit/test_report_schema.py -q` and confirm it passes.

### Task 3: Render the synthesis and update public contracts

**Files:**
- Modify: `src/mingli_engine/markdown.py`
- Modify: `src/mingli_engine/html.py`
- Modify: `tests/unit/test_markdown_renderer.py`
- Modify: `tests/unit/test_html_renderer.py`
- Modify: `tests/integration/test_calculate_report_cli.py`
- Modify: `tests/integration/test_generate_markdown_report.py`

- [ ] Add failing renderer tests asserting the `正式知识综合` subsection occurs exactly once after `观察依据` and before `结构分析`, and includes `report.formal_synthesis`.
- [ ] Run the renderer and integration test set and confirm the new heading is absent.
- [ ] Add the subsection to Markdown and HTML using the existing renderer helpers; update CLI integration assertions to prove generated output includes it.
- [ ] Update Report field-order assertions to include `formal_synthesis` after `evidence_notes`.
- [ ] Run `uv run --with pytest python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py tests/unit/test_html_renderer.py tests/integration/test_calculate_report_cli.py tests/integration/test_generate_markdown_report.py -q` and confirm it passes.

### Task 4: Verify safety, quality, and repository regression

**Files:**
- Modify only if a failing verification exposes an in-scope defect.

- [ ] Run `uv run --with pytest python -m pytest tests/unit/test_evidence_curation.py tests/unit/test_formal_interpretation.py tests/contract/test_knowledge_activation_cli_contract.py tests/safety/test_expanded_high_risk_language.py tests/safety/test_red_lines_and_language.py -q`.
- [ ] Run the project quality scan and confirm activation is `enabled_with_guardrails`, approved evidence is 111, audit is `complete_with_guardrails`, all ten families are covered, and safety is allowed for an ordinary sample.
- [ ] Run `uv run --with pytest python -m pytest -q` with a timeout sufficient for the full suite.
- [ ] Run `git diff --check`, review the complete diff, and commit the implementation with a focused message.
