# Markdown Batch 002 Extension 013/012 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote three ordinary-risk Markdown Batch 002 structural learning items into reviewed 013 candidates and formal 012 evidence.

**Architecture:** Use the existing source-intake and classical-source JSON pipeline without adding new runtime code. Each new candidate uses an exact `review-note:Markdown/source_batch_002_cleaned/...#L...` locator, is approved, included in one reviewed promotion batch, and mirrored by one 012 evidence unit in a reviewed curation batch. Documentation and audit snapshots are refreshed to 42 candidates, 28 promotion batches, and 99 formal evidence units.

**Tech Stack:** Python 3.12 dataclass loaders, project JSON metadata, pytest via `uv run --with pytest python -m pytest`.

---

### Task 1: RED Tests For Batch 002 Extension

**Files:**
- Modify: `tests/unit/test_source_intake.py`
- Modify: `tests/unit/test_classical_sources.py`
- Modify: `tests/unit/test_evidence_curation.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Add failing source-intake assertions**

Add a test that expects:

```python
expected_candidates = {
    "candidate_markdown_batch_002_branch_route_001": (
        "branch_interaction",
        "batch002_branch_interaction_route_001",
    ),
    "candidate_markdown_batch_002_useful_god_types_001": (
        "useful_god_candidate",
        "batch002_useful_god_types_001",
    ),
    "candidate_markdown_batch_002_day_master_strength_basis_001": (
        "pattern_strength",
        "batch002_day_master_strength_basis_001",
    ),
}
```

Each candidate must use `material_markdown_source_batch_002_core`, status `promoted`, risk tier `ordinary`, a Markdown line locator, an approved review decision, and promotion batch `promotion_markdown_batch_002_extension_001`.

- [x] **Step 2: Add failing 012 evidence assertions**

Add tests expecting the three evidence ids above under source `markdown_source_batch_002_core`, curation batch `batch_markdown_batch_002_extension_001`, exact Markdown line locators, non-empty applicability, and limitations.

- [x] **Step 3: Update count snapshots in tests**

Expected new totals:

```text
013 candidates: 42
013 approved reviews: 39
013 promotion batches: 28
012 evidence units: 99
```

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_source_intake.py::test_markdown_batch_002_extension_candidates_are_promoted tests/unit/test_classical_sources.py::test_markdown_batch_002_extension_evidence_is_formalized tests/unit/test_evidence_curation.py::test_project_curation_quality_report_includes_conflicts_and_has_no_failures tests/unit/test_learning_reference_curation.py::test_learning_reference_candidate_formal_evidence_boundary_audit_snapshot -q
```

Expected: FAIL because the new candidate/evidence ids do not exist yet.

### Task 2: GREEN JSON Metadata

**Files:**
- Modify: `src/mingli_engine/data/source_intake/candidate_extracts.json`
- Modify: `src/mingli_engine/data/source_intake/review_decisions.json`
- Modify: `src/mingli_engine/data/source_intake/promotion_batches.json`
- Modify: `src/mingli_engine/data/classical_sources/evidence_units.json`
- Modify: `src/mingli_engine/data/classical_sources/curation_batches.json`

- [x] **Step 1: Add three promoted candidates**

Use these locators:

```text
review-note:Markdown/source_batch_002_cleaned/八字命理讲义教材（299页）.md#L760
review-note:Markdown/source_batch_002_cleaned/八字命理讲义教材（299页）.md#L1156
review-note:Markdown/source_batch_002_cleaned/简体《子平教材讲义第二级次》梁湘润(1).md#L714
```

- [x] **Step 2: Add approved reviews and one promotion batch**

All three reviews use `source_quality=direct_extract`, `confidence=moderate`, and non-empty approval limitations.

- [x] **Step 3: Add three formal evidence units and one curation batch**

Use `source_id=markdown_source_batch_002_core`, `risk_tier=ordinary`, and `source_quality=direct_extract`.

- [x] **Step 4: Run focused tests**

Run the command from Task 1 again. Expected: PASS.

### Task 3: Docs And Verification

**Files:**
- Modify: `docs/classical_sources/coverage.md`
- Modify: `docs/classical_sources/intake.md`
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`

- [x] **Step 1: Refresh docs to 42/28/99**

Update candidate/review/promotion/evidence counts and Markdown Batch 002 source coverage.

- [x] **Step 2: Run quality gates**

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import validate_intake_quality; from mingli_engine.learning_reference_curation import validate_learning_reference_quality; from mingli_engine.materials_audit import validate_materials_audit_quality; from mingli_engine.classical_sources import load_approved_evidence_units, load_classical_sources; from mingli_engine.evidence_curation import validate_curation_quality; print(validate_intake_quality()); print(validate_learning_reference_quality()); print(validate_materials_audit_quality()); print(validate_curation_quality(load_classical_sources(), load_approved_evidence_units()))"
```

Expected: four empty lists.

- [x] **Step 3: Run full tests and commit**

```powershell
uv run --with pytest python -m pytest -q
git diff --check
git add <changed-files>
git commit -m "feat: extend markdown batch 002 evidence"
```

Expected: all tests pass and the worktree is clean after commit.
