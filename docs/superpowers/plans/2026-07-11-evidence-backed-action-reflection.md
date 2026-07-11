# Evidence-Backed Action Reflection Implementation Plan

> **For agentic workers:** Use test-driven development and verify each red-green cycle before moving to the next task.

**Goal:** Add structured, evidence-backed, personalized action reflection and a feedback loop to the production report without expanding the evidence corpus or interpretation claims.

**Architecture:** `models.py` exposes `ActionReflectionItem`. `report_schema.py` derives four items exclusively from existing formal conclusions and renders `action_suggestions` from those items. Existing renderers and CLI carry the reader text; report acceptance certifies provenance, degradation, safety, and personalization.

**Tech Stack:** Python 3.12+, frozen dataclasses, pytest, existing formal interpretation, report schema, renderers, CLI, and report acceptance baseline.

---

### Task 1: Lock The Structured Contract

**Files:**
- Modify: `tests/unit/test_report_schema.py`

- [ ] Add failing tests for four stable action ids, exact family groups, evidence ids, conditions, prompts, feedback metrics, and stop boundaries.
- [ ] Add failing tests for disputed and unavailable status degradation.
- [ ] Update the public `Report` field-order contract.
- [ ] Run the focused tests and confirm failure because the model and builder do not exist.

### Task 2: Implement Action Reflection

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/report_schema.py`

- [ ] Add the frozen `ActionReflectionItem` dataclass and `Report.action_reflection_items`.
- [ ] Implement a pure four-track builder using sanitized chart signals and deduplicated evidence ids.
- [ ] Implement guarded and unavailable degradation.
- [ ] Render `action_suggestions` from the structured items and include it in existing safety scans.
- [ ] Run schema and safety tests until green.

### Task 3: Prove Reader And Multi-Chart Behavior

**Files:**
- Modify: `tests/unit/test_report_schema.py`
- Modify: `tests/unit/test_markdown_renderer.py`
- Modify: `tests/unit/test_html_renderer.py`
- Modify: `tests/integration/test_calculate_report_cli.py`
- Modify: `tests/integration/test_generate_markdown_report.py`

- [ ] Verify all four track titles appear once in `行动建议` in Markdown, HTML, and CLI output.
- [ ] Verify two charts produce different conditions and reader text while retaining the same action ids and family groups.
- [ ] Verify internal signal markers and placeholder values never reach reader output.

### Task 4: Extend Release Acceptance

**Files:**
- Modify: `src/mingli_engine/report_acceptance.py`
- Modify: `tests/unit/test_report_acceptance.py`
- Modify: `tests/contract/test_report_acceptance_cli_contract.py`
- Modify: `docs/classical_sources/report_acceptance.md`
- Modify: `docs/classical_sources/coverage.md`

- [ ] Add the failing `evidence_backed_action_reflection` acceptance expectation.
- [ ] Certify four tracks, all ten families, evidence provenance, safe stop boundaries, sanitized text, and one-time renderer output.
- [ ] Document the new gate and unchanged 111-unit, ten-family evidence baseline.

### Task 5: Verify, Review, And Commit

- [ ] Run focused report, renderer, CLI, acceptance, contract, and safety tests.
- [ ] Run curation, materials-audit, and learning-reference quality scans.
- [ ] Run the full repository regression with sufficient timeout.
- [ ] Run `git diff --check`, inspect all changed paths, perform an independent review, and commit the completed goal.
