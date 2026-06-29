# Raw Text Next Cycle Gated Ordinary Source Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Select bounded ordinary source-level records from the prepared case-collection and practical-formula gated clusters, then register their weak-location 015/016/017/013/012 metadata without touching external raw materials.

**Architecture:** Add a 015 gated ordinary source-selection layer that references the completed gated-cluster-review-prep records. The selected records become source-library entries, materials-audit records, extraction queue tasks, learning reference notes, promoted 013 candidates, and formal 012 evidence with weak source-file/page locators.

**Tech Stack:** Python 3.12, dataclasses, project-local JSON, pytest.

---

### Task 1: RED Coverage

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_source_library.py`
- Modify: `tests/unit/test_extraction_queue_intake.py`
- Modify: `tests/unit/test_learning_reference_curation.py`
- Modify: `tests/unit/test_source_intake.py`
- Modify: `tests/unit/test_classical_sources.py`
- Modify: `tests/unit/test_evidence_curation.py`
- Modify: `tests/integration/test_report_regression_cases.py`

- [x] Add tests for `load_raw_text_next_cycle_gated_ordinary_source_selection_items`, summary counts, markdown/docs sync, selected source ids, sensitive-cluster exclusion, source-library mutation authorization, 013 candidate promotion, and 012 evidence promotion.
- [x] Run the focused tests and confirm they fail before implementation.

### Task 2: 015 Data Model And Loader

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_gated_ordinary_source_selection_items.json`

- [x] Add gated ordinary source selection dataclasses.
- [x] Add constants, loader validation, summary builder, markdown renderer, and quality-gate integration.
- [x] Store exactly two selected ordinary records: `八字18本/命造春秋  188P.pdf` and `四柱预测要诀.pdf`.
- [x] Verify the sensitive topic prep item remains risk-review only.

### Task 3: Downstream Metadata Registration

**Files:**
- Modify: `src/mingli_engine/data/source_library/source_library_entries.json`
- Modify: `src/mingli_engine/data/source_library/source_priority_assessments.json`
- Modify: `src/mingli_engine/data/materials_audit/material_audit_records.json`
- Modify: `src/mingli_engine/data/materials_audit/material_representations.json`
- Modify: `src/mingli_engine/data/materials_audit/preparation_readiness_findings.json`
- Modify: `src/mingli_engine/data/materials_audit/source_alignment_findings.json`
- Modify: `src/mingli_engine/data/materials_audit/extraction_queue_items.json`
- Modify: `src/mingli_engine/data/extraction_queue_intake/extraction_work_packages.json`
- Modify: `src/mingli_engine/data/extraction_queue_intake/extraction_tasks.json`
- Modify: `src/mingli_engine/data/extraction_queue_intake/candidate_draft_slots.json`
- Modify: `src/mingli_engine/data/learning_reference_curation/learning_reference_notes.json`
- Modify: `src/mingli_engine/data/learning_reference_curation/learning_points.json`
- Modify: `src/mingli_engine/data/learning_reference_curation/candidate_intake_decisions.json`
- Modify: `src/mingli_engine/data/source_intake/source_materials.json`
- Modify: `src/mingli_engine/data/source_intake/candidate_extracts.json`
- Modify: `src/mingli_engine/data/source_intake/review_decisions.json`
- Modify: `src/mingli_engine/data/source_intake/promotion_batches.json`
- Modify: `src/mingli_engine/data/classical_sources/sources.json`
- Modify: `src/mingli_engine/data/classical_sources/evidence_units.json`
- Modify: `src/mingli_engine/data/classical_sources/curation_batches.json`

- [x] Register two source-library entries and priority assessments.
- [x] Register audit/readiness/alignment/queue records.
- [x] Register 016 tasks and 017 notes/learning points/decisions.
- [x] Promote two 013 candidates and two 012 evidence units.

### Task 4: Maintainer Documentation

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `docs/classical_sources/source_library.md`
- Modify: `docs/classical_sources/extraction_queue_intake.md`
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `docs/classical_sources/intake.md`
- Modify: `docs/classical_sources/README.md`
- Modify: `docs/classical_sources/coverage.md`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`

- [x] Add the rendered 015 gated ordinary source-selection section.
- [x] Update counts and handoff markers for the two new ordinary weak-location records.
- [x] State the next target after this goal.

### Task 5: Verification And Commit

- [x] Run focused tests for materials audit/source library/extraction intake/learning curation/source intake/classical sources/evidence/report regression.
- [x] Run material quality gates.
- [x] Run the full test suite.
- [x] Run `git diff --check`.
- [x] Commit locally with `feat: select gated ordinary raw text sources`.
