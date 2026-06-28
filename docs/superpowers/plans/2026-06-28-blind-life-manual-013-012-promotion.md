# Blind Life Manual 013 012 Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote the returned `candidate_blind_life_manual_gap_001` into a bounded 013 approved/promoted candidate and one 012 high-risk boundary evidence unit.

**Architecture:** Keep the source claim narrow: revise the candidate into a conditional high-risk boundary note anchored to `blind_life_manual.md#source-window-high-risk-boundary`. Update existing JSON metadata rather than adding raw extraction artifacts, then refresh computed-count documentation and tests.

**Tech Stack:** Python 3.12 JSON metadata, existing `source_intake`, `classical_sources`, `learning_reference_curation`, and pytest validation.

---

### Task 1: Red Tests

**Files:**
- Modify: `tests/unit/test_source_intake.py`
- Modify: `tests/unit/test_evidence_curation.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [ ] **Step 1: Add focused 013/012 promotion test**

Assert:
- `candidate_blind_life_manual_gap_001.status == "promoted"`
- candidate locator is `review-note:blind_life_manual.md#source-window-high-risk-boundary`
- candidate links `blind_life_manual_high_risk_boundary_001`
- review decision is `approved`
- promotion batch `promotion_blind_life_manual_high_risk_boundary_001` exists
- target evidence id is `blind_life_manual_high_risk_boundary_001`

- [ ] **Step 2: Add focused 012 evidence test**

Assert:
- `load_approved_evidence_units()` includes `blind_life_manual_high_risk_boundary_001`
- source id is `blind_life_manual`
- rule family is `high_risk_signal`
- risk tier is `high_risk`
- limitations include refusal of exact lifespan/death timing and diagnostic claims
- approved evidence count increases from 95 to 96

- [ ] **Step 3: Update 017 boundary snapshot expectations**

Assert current 013/012 counts become:
- candidates: 39
- review decisions: 39
- promoted candidates: 36
- approved reviews: 36
- formal evidence units: 96
- `formal_evidence_delta` remains `0` for the 017 boundary audit itself

- [ ] **Step 4: Run RED focused tests**

Run:

```powershell
$env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest tests/unit/test_source_intake.py tests/unit/test_evidence_curation.py tests/unit/test_learning_reference_curation.py -q
```

Expected: FAIL because the candidate is still returned, the evidence unit does not exist, and counts still reflect 35/95.

### Task 2: Data Promotion

**Files:**
- Modify: `src/mingli_engine/data/source_intake/source_materials.json`
- Modify: `src/mingli_engine/data/source_intake/candidate_extracts.json`
- Modify: `src/mingli_engine/data/source_intake/review_decisions.json`
- Modify: `src/mingli_engine/data/source_intake/promotion_batches.json`
- Modify: `src/mingli_engine/data/classical_sources/sources.json`
- Modify: `src/mingli_engine/data/classical_sources/evidence_units.json`
- Modify: `src/mingli_engine/data/classical_sources/curation_batches.json`

- [ ] **Step 1: Update source material**

Set `material_blind_life_manual_pdf.preparation_status` to `partially_reviewed` and preserve rights notes.

- [ ] **Step 2: Revise candidate**

Set `candidate_blind_life_manual_gap_001`:
- locator to `review-note:blind_life_manual.md#source-window-high-risk-boundary`
- extracted meaning to a conditional high-risk boundary summary
- rule family to `high_risk_signal`
- status to `promoted`
- related evidence to `blind_life_manual_high_risk_boundary_001`
- related conflict to `conflict_high_risk_scope_001`

- [ ] **Step 3: Revise review decision**

Change the existing review decision to `approved`, with approval limitations and no required changes.

- [ ] **Step 4: Add promotion batch**

Append `promotion_blind_life_manual_high_risk_boundary_001`.

- [ ] **Step 5: Approve source and add evidence**

Set `blind_life_manual.review_status` to `approved`, keep extraction partial, and keep a narrowed curation gap reason noting only boundary evidence is available. Append `blind_life_manual_high_risk_boundary_001` to `evidence_units.json`.

- [ ] **Step 6: Add 012 curation batch**

Append `batch_blind_life_manual_high_risk_boundary_001` with the new source/evidence ids.

### Task 3: Docs And Validation

**Files:**
- Modify: `docs/classical_sources/intake.md`
- Modify: `docs/classical_sources/coverage.md`
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `docs/classical_sources/extracts/blind_life_manual.md`

- [ ] **Step 1: Refresh docs**

Update computed counts and note the safe promotion:
- promoted candidates `36`
- returned candidates `0`
- formal evidence units `96`
- `blind_life_manual` evidence count `1`

- [ ] **Step 2: Run quality gates**

Run:

```powershell
$env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8'; uv run python -c "from mingli_engine import source_intake, learning_reference_curation, materials_audit, classical_sources; print(source_intake.validate_intake_quality()); print(learning_reference_curation.validate_learning_reference_quality()); print(materials_audit.validate_materials_audit_quality()); print(len(classical_sources.load_approved_evidence_units()))"
```

Expected: empty quality failures and evidence count 96.

- [ ] **Step 3: Run focused and full tests**

Run:

```powershell
$env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest tests/unit/test_source_intake.py tests/unit/test_evidence_curation.py tests/unit/test_learning_reference_curation.py -q
$env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest -q
```

Expected: all tests pass.

### Task 4: Commit

**Files:**
- All changed files from Tasks 1-3

- [ ] **Step 1: Inspect and commit**

Run:

```powershell
git diff --check
git status --short
git add docs/superpowers/plans/2026-06-28-blind-life-manual-013-012-promotion.md tests/unit/test_source_intake.py tests/unit/test_evidence_curation.py tests/unit/test_learning_reference_curation.py src/mingli_engine/data/source_intake/source_materials.json src/mingli_engine/data/source_intake/candidate_extracts.json src/mingli_engine/data/source_intake/review_decisions.json src/mingli_engine/data/source_intake/promotion_batches.json src/mingli_engine/data/classical_sources/sources.json src/mingli_engine/data/classical_sources/evidence_units.json src/mingli_engine/data/classical_sources/curation_batches.json docs/classical_sources/intake.md docs/classical_sources/coverage.md docs/classical_sources/learning_reference_curation.md docs/classical_sources/new_material_learning_handoff.md docs/classical_sources/extracts/blind_life_manual.md
git commit -m "feat: promote blind life manual boundary evidence"
```

Expected: local commit succeeds; no remote action.
