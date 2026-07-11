# Personalized Formal Synthesis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add sanitized chart-specific signals to all ten formal rule-family explanations and prove that formal synthesis varies across charts without weakening evidence or safety contracts.

**Architecture:** `report_schema.py` owns one pure reader-signal formatter over existing `EvidenceTrace.chart_signals`. Formal synthesis and expanded observation evidence reuse it, while formal interpretation and 012 evidence remain unchanged.

**Tech Stack:** Python 3.12+, dataclasses, pytest, existing report schema, Markdown/HTML renderers, CLI, and report acceptance baseline.

---

### Task 1: Define Signal Translation And Safety Behavior

**Files:**
- Modify: `tests/unit/test_report_schema.py`

- [ ] Add failing tests for pillar-prefix translation, duplicate removal, placeholder filtering, five-signal limit, empty fallback, and high-risk focus-topic suppression.
- [ ] Add a failing complete-report assertion that all ten rule-family entries contain `盘面信号` and no raw machine marker remains in formal synthesis or evidence notes.
- [ ] Run `uv run --with pytest python -m pytest tests/unit/test_report_schema.py -q` and confirm the new assertions fail because no reader signal formatter exists.

### Task 2: Implement Shared Reader Signal Formatting

**Files:**
- Modify: `src/mingli_engine/report_schema.py`

- [ ] Implement `format_reader_chart_signals(rule_family, signals)` with stable deduplication, pillar translation, placeholder removal, high-risk allowlisting, marker translation, and five-item limit.
- [ ] Add the formatted segment to every available formal synthesis conclusion.
- [ ] Replace raw chart-signal joining in expanded evidence notes with the same formatter.
- [ ] Run schema and safety tests and confirm they pass.

### Task 3: Prove Multi-Chart Personalization

**Files:**
- Modify: `tests/unit/test_report_schema.py`
- Modify: `tests/integration/test_calculate_report_cli.py`
- Modify: `tests/integration/test_generate_markdown_report.py`

- [ ] Add two-chart regression coverage with different strength, pattern, useful-god, element, pillar, and luck inputs.
- [ ] Assert chart-specific signals appear in the matching synthesis and differ for pattern, useful-god, and luck-cycle families.
- [ ] Assert Markdown, HTML, and both CLI report paths contain reader-facing signal text and exclude `traditional_high_risk_signal_boundary`.
- [ ] Run focused report, renderer, and CLI tests.

### Task 4: Extend Acceptance And Documentation

**Files:**
- Modify: `src/mingli_engine/report_acceptance.py`
- Modify: `tests/unit/test_report_acceptance.py`
- Modify: `tests/contract/test_report_acceptance_cli_contract.py`
- Modify: `docs/classical_sources/report_acceptance.md`
- Modify: `docs/classical_sources/coverage.md`

- [ ] Add a failing acceptance expectation for `personalized_chart_signals`.
- [ ] Make the ordinary production acceptance case verify ten signal segments and no raw machine marker.
- [ ] Document the personalization gate and unchanged 111-unit/ten-family baseline.
- [ ] Run acceptance unit and CLI contract tests.

### Task 5: Verify And Commit

**Files:**
- Modify only if an in-scope verification failure requires a tested correction.

- [ ] Run focused report, formal interpretation, renderer, CLI, acceptance, and safety tests.
- [ ] Run curation, materials-audit, and learning-reference quality scans.
- [ ] Run `uv run --with pytest python -m pytest -q` with sufficient timeout.
- [ ] Run `git diff --check`, review changed paths for 013/012 and raw-material boundaries, and commit the result.
