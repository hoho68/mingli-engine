# Final Goal Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the current data-consistency gaps, restore the full validation suite to green, refresh maintainer snapshots, and leave the Mingli engine ready for the next evidence/report feature.

**Architecture:** Treat the project as a linked data graph: 013 source intake candidates/reviews/promotions, 014 source library, 015 materials audit, 016 extraction queue intake, 017 learning reference curation, and formal classical evidence must all load without broken references. Prefer data-preserving fixes when downstream review, promotion, and evidence records already exist; do not mutate external raw PDFs, root `Markdown/`, `资料原文/`, or `资料整理/`.

**Tech Stack:** Python 3.12+, existing `mingli_engine` package, JSON data files under `src/mingli_engine/data/`, pytest, PowerShell commands on Windows, Spec Kit artifacts under `specs/017-learning-reference-curation/`.

---

## Goal Mode Starter

Use this objective when starting goal mode:

```text
Complete the Mingli engine final-goal closure plan in docs/superpowers/plans/2026-06-26-final-goal-completion.md: fix 013/source-intake and classical evidence broken references, update stale regression expectations and documentation snapshots, run all focused and full validations, and report the remaining product work without mutating external raw materials.
```

Definition of complete:

- `uv run --with pytest python -m pytest -q` passes.
- `source_intake.build_intake_progress_report()` runs without exception.
- `source_library.build_source_library_progress_report()` runs without exception.
- `classical_sources.load_curation_batches()` runs without exception.
- 016 and 017 quality checks still return `[]`.
- Maintainer docs state the current data counts instead of older snapshots.
- `git status --short` is clean after final commits.

## Current Known State

- Full suite result before this plan: 694 passed, 2 failed.
- Failing tests:
  - `tests/integration/test_report_regression_cases.py::test_learning_reference_intake_decisions_do_not_change_candidate_or_formal_evidence_counts`
  - `tests/integration/test_report_regression_cases.py::test_learning_reference_prerequisite_actions_do_not_change_formal_evidence_counts`
- Current 017 counts:
  - learning notes: 14
  - learning points: 34
  - candidate-intake decisions: 28
  - prerequisite action notes: 6
  - formal evidence delta: 0
- Current 013 source-intake gap:
  - `review_batch_005_ten_god_relation_001` references missing `candidate_markdown_batch_005_ten_god_relation_001`
  - `review_batch_005_blind_image_method_001` references missing `candidate_markdown_batch_005_blind_image_method_001`
  - `review_batch_005_branch_interaction_001` references missing `candidate_markdown_batch_005_branch_interaction_001`
  - matching promotion batches reference the same missing candidates
- Current classical curation gap:
  - `batch_kskeleton_taxonomy_001` references 11 old evidence ids, while the actual evidence ids are the shorter `kskeleton_q...` ids already present in `evidence_units.json`.

## File Map

- `src/mingli_engine/data/source_intake/candidate_extracts.json`: add three promoted batch005 candidate records to match existing review decisions, promotion batches, and formal evidence.
- `src/mingli_engine/data/classical_sources/curation_batches.json`: replace stale KSkeleton evidence ids with the actual evidence ids present in `evidence_units.json`.
- `tests/unit/test_source_intake.py`: add source-intake referential integrity coverage so review and promotion records cannot point at missing candidates again.
- `tests/unit/test_classical_sources.py`: add curation-batch referential integrity coverage.
- `tests/integration/test_report_regression_cases.py`: update stale 017 count/action expectations to match the current curated dataset.
- `docs/classical_sources/coverage.md`: refresh approved evidence/source/rule/risk counts from current JSON.
- `docs/classical_sources/intake.md`: refresh 013 candidate status counts and remove stale statements that imply only five pending candidates remain.
- `docs/classical_sources/learning_reference_curation.md`: refresh 017 progress snapshot to 14 notes, 34 points, 28 decisions, and 6 prerequisite actions.
- `docs/classical_sources/source_library.md`: refresh source-library progress only after `build_source_library_progress_report()` loads successfully.
- `specs/017-learning-reference-curation/quickstart.md`: update expected validation output if it still describes the older five-note 017 slice.

---

### Task 1: Establish A Clean Execution Baseline

**Files:**
- Inspect: `AGENTS.md`
- Inspect: `specs/017-learning-reference-curation/plan.md`
- Inspect: `docs/superpowers/plans/2026-06-26-final-goal-completion.md`

- [ ] **Step 1: Confirm worktree state**

Run:

```powershell
git status --short --branch
```

Expected: current branch is visible and the worktree has no uncommitted changes before edits. If the worktree is dirty, inspect each path with `git diff --stat` and do not overwrite unrelated user changes.

- [ ] **Step 2: Confirm the project instruction pointer**

Run:

```powershell
Get-Content -Raw AGENTS.md
Get-Content -Raw specs/017-learning-reference-curation/plan.md
```

Expected: `AGENTS.md` points to the 017 plan, and the plan confirms no external raw materials should be moved, deleted, converted, or rewritten.

- [ ] **Step 3: Reproduce the currently known failures**

Run:

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py::test_learning_reference_intake_decisions_do_not_change_candidate_or_formal_evidence_counts tests/integration/test_report_regression_cases.py::test_learning_reference_prerequisite_actions_do_not_change_formal_evidence_counts -q
```

Expected before fixes: both tests fail with stale 017 count/action expectations.

- [ ] **Step 4: Reproduce the data-loader failures**

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine import source_intake; print(source_intake.validate_intake_quality()); print(source_intake.build_intake_progress_report())"
```

Expected before fixes: `validate_intake_quality()` reports the first missing batch005 candidate and `build_intake_progress_report()` raises `SourceIntakeError`.

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.classical_sources import load_curation_batches; print(len(load_curation_batches()))"
```

Expected before fixes: raises `ClassicalEvidenceError` for `batch_kskeleton_taxonomy_001`.

- [ ] **Step 5: Commit nothing**

Run:

```powershell
git status --short
```

Expected: no files changed by this baseline task.

---

### Task 2: Add Source-Intake Broken-Reference Regression Tests

**Files:**
- Modify: `tests/unit/test_source_intake.py`
- Inspect: `src/mingli_engine/data/source_intake/candidate_extracts.json`
- Inspect: `src/mingli_engine/data/source_intake/review_decisions.json`
- Inspect: `src/mingli_engine/data/source_intake/promotion_batches.json`

- [ ] **Step 1: Add a test for review decisions and promotion batches**

Append this test near the existing source-intake quality tests in `tests/unit/test_source_intake.py`:

```python
def test_seeded_review_and_promotion_records_reference_existing_candidates():
    candidates = source_intake.load_candidate_extracts()
    candidate_ids = {candidate.candidate_id for candidate in candidates}

    reviews = source_intake.load_review_decisions()
    batches = source_intake.load_promotion_batches()

    assert reviews
    assert batches
    assert all(review.candidate_id in candidate_ids for review in reviews)
    assert all(
        candidate_id in candidate_ids
        for batch in batches
        for candidate_id in batch.candidate_ids
    )
```

- [ ] **Step 2: Add an intake-progress smoke test**

Append this test in the same file:

```python
def test_seeded_intake_progress_report_loads_after_batch_registration():
    report = source_intake.build_intake_progress_report()

    assert report.candidate_counts
    assert report.risk_tier_counts
    assert report.rule_family_counts
```

- [ ] **Step 3: Run the new tests and verify RED**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_source_intake.py::test_seeded_review_and_promotion_records_reference_existing_candidates tests/unit/test_source_intake.py::test_seeded_intake_progress_report_loads_after_batch_registration -q
```

Expected before data repair: failure or error mentioning `candidate_markdown_batch_005_ten_god_relation_001`.

- [ ] **Step 4: Commit only tests after they fail**

Do not commit yet if the tests have not been observed failing. After observing RED:

```powershell
git add tests/unit/test_source_intake.py
git commit -m "test: cover source intake reference integrity"
```

---

### Task 3: Repair Missing Batch005 Candidate Records

**Files:**
- Modify: `src/mingli_engine/data/source_intake/candidate_extracts.json`
- Test: `tests/unit/test_source_intake.py`

- [ ] **Step 1: Add the missing ten-god relation candidate**

Insert this object into `src/mingli_engine/data/source_intake/candidate_extracts.json` before the final closing array bracket, preserving valid JSON commas:

```json
{
  "candidate_id": "candidate_markdown_batch_005_ten_god_relation_001",
  "material_id": "material_markdown_source_batch_005",
  "source_locator": "review-note:note_markdown_batch_005_001#lp_markdown_batch_005_ten_god_relation_001",
  "extracted_meaning": "Training review notes present ten-god relationship imaging: when the useful god is restrained by a ten god, traditional interpretation suggests relationship dynamics with that ten god's represented domain.",
  "short_quote": "",
  "proposed_rule_family": "ten_god_relation",
  "risk_tier": "sensitive",
  "status": "promoted",
  "proposed_limitations": [
    "Relationship interpretations are tendencies, not certainties.",
    "Uncertainty: multiple ten-god interactions may produce countervailing effects.",
    "Cross-source confirmation needed before formal evidence promotion.",
    "Educational context only; not for individual consultation."
  ],
  "related_evidence_ids": [
    "batch005_ten_god_relation_001"
  ],
  "related_conflict_ids": [],
  "related_gap_ids": [],
  "duplicate_of": "",
  "created_by": "learning_reference_curation",
  "created_at": "2026-06-23"
}
```

- [ ] **Step 2: Add the missing blind-image candidate**

Insert this object after the ten-god relation candidate:

```json
{
  "candidate_id": "candidate_markdown_batch_005_blind_image_method_001",
  "material_id": "material_markdown_source_batch_005",
  "source_locator": "review-note:note_markdown_batch_005_001#lp_markdown_batch_005_blind_image_method_001",
  "extracted_meaning": "Training notes present blind-style pattern recognition where specific Ba Zi configurations are traditionally associated with characteristic personality and tendency patterns within educational context.",
  "short_quote": "",
  "proposed_rule_family": "blind_image_method",
  "risk_tier": "sensitive",
  "status": "promoted",
  "proposed_limitations": [
    "Blind-style interpretations are pattern-based tendencies, not deterministic readings.",
    "Uncertainty: different schools may interpret configurations differently.",
    "Cross-confirm with foundation sources before formal evidence promotion.",
    "Educational reference only; not a standalone diagnostic tool."
  ],
  "related_evidence_ids": [
    "batch005_blind_image_method_001"
  ],
  "related_conflict_ids": [],
  "related_gap_ids": [],
  "duplicate_of": "",
  "created_by": "learning_reference_curation",
  "created_at": "2026-06-23"
}
```

- [ ] **Step 3: Add the missing branch-interaction candidate**

Insert this object after the blind-image candidate:

```json
{
  "candidate_id": "candidate_markdown_batch_005_branch_interaction_001",
  "material_id": "material_markdown_source_batch_005",
  "source_locator": "review-note:note_markdown_batch_005_001#lp_markdown_batch_005_branch_interaction_001",
  "extracted_meaning": "Training notes present branch punishment, conflict, and combination principles where interaction effect depends on whether it restrains favorable or unfavorable chart elements.",
  "short_quote": "",
  "proposed_rule_family": "branch_interaction",
  "risk_tier": "sensitive",
  "status": "promoted",
  "proposed_limitations": [
    "Branch interaction effects are context-dependent across different chart configurations.",
    "Uncertainty: same interaction may produce different effects in different charts.",
    "Cross-confirm with established branch interaction sources before promotion.",
    "Educational reference; branch interactions are one factor among many."
  ],
  "related_evidence_ids": [
    "batch005_branch_interaction_001"
  ],
  "related_conflict_ids": [],
  "related_gap_ids": [],
  "duplicate_of": "",
  "created_by": "learning_reference_curation",
  "created_at": "2026-06-23"
}
```

- [ ] **Step 4: Validate JSON syntax**

Run:

```powershell
python -m json.tool src/mingli_engine/data/source_intake/candidate_extracts.json > $null
```

Expected: exit code 0.

- [ ] **Step 5: Run source-intake focused tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_source_intake.py::test_seeded_review_and_promotion_records_reference_existing_candidates tests/unit/test_source_intake.py::test_seeded_intake_progress_report_loads_after_batch_registration -q
```

Expected after repair: PASS.

- [ ] **Step 6: Run intake quality and progress commands**

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine import source_intake; print(source_intake.validate_intake_quality()); print(source_intake.build_intake_progress_report())"
```

Expected after repair: `validate_intake_quality()` prints `[]`, and `build_intake_progress_report()` prints an `IntakeProgressReport`.

- [ ] **Step 7: Commit the source-intake data repair**

Run:

```powershell
git add src/mingli_engine/data/source_intake/candidate_extracts.json tests/unit/test_source_intake.py
git commit -m "fix: restore batch005 source intake candidates"
```

---

### Task 4: Add Classical Curation-Batch Integrity Tests

**Files:**
- Modify: `tests/unit/test_classical_sources.py`
- Inspect: `src/mingli_engine/data/classical_sources/curation_batches.json`
- Inspect: `src/mingli_engine/data/classical_sources/evidence_units.json`

- [ ] **Step 1: Import `load_curation_batches`**

Update the import block in `tests/unit/test_classical_sources.py`:

```python
from mingli_engine.classical_sources import (
    ClassicalEvidenceError,
    load_approved_evidence_units,
    load_classical_sources,
    load_curation_batches,
    load_evidence_units,
)
```

- [ ] **Step 2: Add a curation-batch load test**

Add this test after `test_approved_evidence_units_link_only_to_approved_sources`:

```python
def test_seeded_curation_batches_reference_existing_sources_and_evidence():
    batches = load_curation_batches()
    evidence_ids = {unit.evidence_id for unit in load_evidence_units()}
    source_ids = {source.source_id for source in load_classical_sources()}

    assert batches
    assert all(source_id in source_ids for batch in batches for source_id in batch.source_ids)
    assert all(evidence_id in evidence_ids for batch in batches for evidence_id in batch.evidence_ids)
```

- [ ] **Step 3: Run the new test and verify RED**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_seeded_curation_batches_reference_existing_sources_and_evidence -q
```

Expected before curation-batch repair: failure mentioning `batch_kskeleton_taxonomy_001 references unknown evidence`.

- [ ] **Step 4: Commit only the failing test**

Run after observing RED:

```powershell
git add tests/unit/test_classical_sources.py
git commit -m "test: cover classical curation batch references"
```

---

### Task 5: Repair KSkeleton Curation-Batch Evidence IDs

**Files:**
- Modify: `src/mingli_engine/data/classical_sources/curation_batches.json`
- Test: `tests/unit/test_classical_sources.py`

- [ ] **Step 1: Replace stale KSkeleton ids**

In `src/mingli_engine/data/classical_sources/curation_batches.json`, inside `batch_kskeleton_taxonomy_001`, replace this id list:

```json
[
  "kskeleton_q001_foundation_tables",
  "kskeleton_q002_yushi_tiaohou",
  "kskeleton_q002_shen_pattern",
  "kskeleton_q002_yuanhai_bilateral",
  "kskeleton_q003_geju_selection",
  "kskeleton_q003_day_master",
  "kskeleton_q003_congwang_congshi",
  "kskeleton_q006_interaction_structure",
  "kskeleton_q004_mechanism_layer",
  "kskeleton_q004_cross_dependency",
  "kskeleton_q004_q006_dependency"
]
```

with this actual evidence id list:

```json
[
  "kskeleton_q001_foundation",
  "kskeleton_q002_yushi",
  "kskeleton_q002_shen",
  "kskeleton_q002_yuanhai",
  "kskeleton_q003_geju",
  "kskeleton_q003_day",
  "kskeleton_q003_congwang",
  "kskeleton_q006_interaction",
  "kskeleton_q004_mechanism",
  "kskeleton_q004_cross",
  "kskeleton_q004_q006"
]
```

- [ ] **Step 2: Validate JSON syntax**

Run:

```powershell
python -m json.tool src/mingli_engine/data/classical_sources/curation_batches.json > $null
```

Expected: exit code 0.

- [ ] **Step 3: Run classical source focused tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py::test_seeded_curation_batches_reference_existing_sources_and_evidence tests/unit/test_classical_sources.py::test_approved_evidence_units_link_only_to_approved_sources -q
```

Expected after repair: PASS.

- [ ] **Step 4: Run curation-batch loader smoke command**

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.classical_sources import load_curation_batches; print(len(load_curation_batches()))"
```

Expected after repair: prints `4`.

- [ ] **Step 5: Commit the classical evidence data repair**

Run:

```powershell
git add src/mingli_engine/data/classical_sources/curation_batches.json tests/unit/test_classical_sources.py
git commit -m "fix: repair kskeleton curation batch references"
```

---

### Task 6: Update 017 Regression Expectations To Current Data

**Files:**
- Modify: `tests/integration/test_report_regression_cases.py`
- Inspect: `src/mingli_engine/data/learning_reference_curation/learning_points.json`
- Inspect: `src/mingli_engine/data/learning_reference_curation/candidate_intake_decisions.json`
- Inspect: `src/mingli_engine/data/learning_reference_curation/prerequisite_action_notes.json`

- [ ] **Step 1: Update learning point and decision counts**

In `test_learning_reference_intake_decisions_do_not_change_candidate_or_formal_evidence_counts`, replace:

```python
    assert len(points) == 37
    assert len(decisions) == 31
```

with:

```python
    assert len(points) == 34
    assert len(decisions) == 28
```

- [ ] **Step 2: Update prerequisite action ids**

In `test_learning_reference_prerequisite_actions_do_not_change_formal_evidence_counts`, replace the expected action id set with:

```python
    assert {action.action_note_id for action in action_notes} == {
        "action_blind_life_manual_risk_review_001",
        "action_blind_school_secret_blocked_001",
        "action_markdown_batch_003_registration_001",
        "action_immortal_fortune_jianghu_secret_risk_review_001",
        "action_life_death_book_100_pages_risk_review_001",
        "action_source_processing_status_deferred_001",
    }
```

- [ ] **Step 3: Add summary assertions that lock the current 017 snapshot**

After `assert summary.formal_evidence_delta == 0`, add:

```python
    assert summary.note_counts == {"draft": 7, "candidate_intake_started": 7}
    assert summary.learning_point_counts == {
        "duplicate_review": 1,
        "ready": 27,
        "deferred": 6,
    }
    assert summary.candidate_decision_count == 28
    assert summary.candidate_ready_count == 27
    assert summary.prerequisite_action_counts == {
        "risk_review": 3,
        "blocked": 1,
        "deferred": 2,
        "status:planned": 3,
        "status:blocked": 1,
        "status:deferred": 2,
    }
```

- [ ] **Step 4: Run the two previously failing tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py::test_learning_reference_intake_decisions_do_not_change_candidate_or_formal_evidence_counts tests/integration/test_report_regression_cases.py::test_learning_reference_prerequisite_actions_do_not_change_formal_evidence_counts -q
```

Expected after update: PASS.

- [ ] **Step 5: Run the whole regression file**

Run:

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit the regression expectation update**

Run:

```powershell
git add tests/integration/test_report_regression_cases.py
git commit -m "test: refresh learning reference regression snapshot"
```

---

### Task 7: Run Cross-Layer Loader And Quality Gates

**Files:**
- Inspect: `src/mingli_engine/source_intake.py`
- Inspect: `src/mingli_engine/source_library.py`
- Inspect: `src/mingli_engine/materials_audit.py`
- Inspect: `src/mingli_engine/extraction_queue_intake.py`
- Inspect: `src/mingli_engine/learning_reference_curation.py`
- Inspect: `src/mingli_engine/classical_sources.py`

- [ ] **Step 1: Run 013 intake gate**

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import validate_intake_quality, build_intake_progress_report; print(validate_intake_quality()); print(build_intake_progress_report())"
```

Expected: first line is `[]`; second line is an `IntakeProgressReport`.

- [ ] **Step 2: Run 014 source-library gate**

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_library import validate_source_library_quality, build_source_library_progress_report; print(validate_source_library_quality()); print(build_source_library_progress_report())"
```

Expected: first line is `[]`; second line is a `SourceLibraryProgressReport`.

- [ ] **Step 3: Run 015 materials-audit gate**

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.materials_audit import validate_materials_audit_quality, build_materials_audit_progress_summary; print(validate_materials_audit_quality()); print(build_materials_audit_progress_summary())"
```

Expected: first line is `[]`; second line is an `AuditProgressSummary`.

- [ ] **Step 4: Run 016 extraction-queue gate**

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.extraction_queue_intake import validate_extraction_package_quality, build_package_progress_summary; print(validate_extraction_package_quality()); print(build_package_progress_summary())"
```

Expected: first line is `[]`; second line is a `PackageProgressSummary`.

- [ ] **Step 5: Run 017 learning-reference gate**

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.learning_reference_curation import validate_learning_reference_quality, build_learning_reference_progress_summary; print(validate_learning_reference_quality()); print(build_learning_reference_progress_summary())"
```

Expected: first line is `[]`; second line is a `LearningReferenceProgressSummary`.

- [ ] **Step 6: Run formal evidence loader gates**

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.classical_sources import load_classical_sources, load_approved_evidence_units, load_curation_batches, load_source_conflicts; print(len(load_classical_sources())); print(len(load_approved_evidence_units())); print(len(load_curation_batches())); print(len(load_source_conflicts()))"
```

Expected after repairs:

```text
14
92
4
2
```

- [ ] **Step 7: Commit nothing**

Run:

```powershell
git status --short
```

Expected: no new changes from loader checks.

---

### Task 8: Refresh Maintainer Documentation Snapshots

**Files:**
- Modify: `docs/classical_sources/coverage.md`
- Modify: `docs/classical_sources/intake.md`
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `docs/classical_sources/source_library.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`

- [ ] **Step 1: Capture current computed summaries**

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.classical_sources import load_classical_sources, load_approved_evidence_units, load_curation_batches, load_source_conflicts; from collections import Counter; sources=load_classical_sources(); evidence=load_approved_evidence_units(); print('sources', len(sources), Counter(s.review_status for s in sources)); print('evidence', len(evidence), Counter(e.source_id for e in evidence), Counter(e.rule_family for e in evidence), Counter(e.risk_tier for e in evidence)); print('batches', len(load_curation_batches())); print('conflicts', len(load_source_conflicts()))"
```

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import build_intake_progress_report; print(build_intake_progress_report())"
```

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.learning_reference_curation import build_learning_reference_progress_summary; print(build_learning_reference_progress_summary())"
```

Expected: all commands print summaries without exceptions.

- [ ] **Step 2: Update `coverage.md`**

In `docs/classical_sources/coverage.md`, update these values from the computed output:

```markdown
Snapshot date: 2026-06-26

- Approved evidence units: 92
- Registered sources: 14
```

Replace the source, rule-family, and risk-tier count sections with the exact counters printed in Step 1. Keep the guardrails unchanged unless a validation command reports a new guardrail issue.

- [ ] **Step 3: Update `intake.md`**

In `docs/classical_sources/intake.md`, update the "Computed with `build_intake_progress_report()`" section to match the repaired report. Confirm the status count includes 32 promoted-or-otherwise historical candidates after adding the three batch005 candidates: the exact count should come from the printed `IntakeProgressReport`, not from hand memory.

- [ ] **Step 4: Update `learning_reference_curation.md`**

In `docs/classical_sources/learning_reference_curation.md`, update the progress snapshot to:

```markdown
- Notes: `draft=7`, `candidate_intake_started=7`.
- Learning points: `duplicate_review=1`, `ready=27`, `deferred=6`.
- Candidate decisions: `reuse_existing=1`, `create_candidate=27`, `status:applied=28`.
- Prerequisite actions: `risk_review=3`, `blocked=1`, `deferred=2`, `status:planned=3`, `status:blocked=1`, `status:deferred=2`.
- Candidate-ready count: `27`.
- Candidate decision count: `28`.
- Formal evidence delta: `0`.
```

- [ ] **Step 5: Update `source_library.md`**

In `docs/classical_sources/source_library.md`, update any progress snapshot that failed to load before the batch005 candidate repair. Use the exact `SourceLibraryProgressReport` printed in Task 7 Step 2.

- [ ] **Step 6: Update 017 quickstart**

In `specs/017-learning-reference-curation/quickstart.md`, replace the older expected five-note output with the current 14-note/34-point/28-decision/6-action snapshot from Task 7 Step 5.

- [ ] **Step 7: Run documentation-adjacent focused tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_classical_sources.py tests/unit/test_source_intake.py tests/unit/test_source_library.py tests/unit/test_materials_audit.py tests/unit/test_extraction_queue_intake.py tests/unit/test_learning_reference_curation.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit documentation refresh**

Run:

```powershell
git add docs/classical_sources/coverage.md docs/classical_sources/intake.md docs/classical_sources/learning_reference_curation.md docs/classical_sources/source_library.md specs/017-learning-reference-curation/quickstart.md
git commit -m "docs: refresh classical source progress snapshots"
```

---

### Task 9: Run Boundary And Full Test Verification

**Files:**
- Inspect: `tests/unit/test_learning_reference_curation.py`
- Inspect: `tests/unit/test_extraction_queue_intake.py`
- Inspect: `tests/unit/test_source_intake.py`
- Inspect: `tests/unit/test_source_library.py`
- Inspect: `tests/unit/test_classical_sources.py`
- Inspect: `tests/integration/test_report_regression_cases.py`
- Inspect: `tests/safety/test_expanded_high_risk_language.py`

- [ ] **Step 1: Run 016/017 boundary tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py tests/unit/test_extraction_queue_intake.py tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py -q
```

Expected: PASS.

- [ ] **Step 2: Run 013/014/formal evidence tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_source_intake.py tests/unit/test_source_library.py tests/unit/test_classical_sources.py -q
```

Expected: PASS.

- [ ] **Step 3: Run the full suite**

Run:

```powershell
uv run --with pytest python -m pytest -q
```

Expected: all tests pass. The previous baseline was 694 passed and 2 failed; after this plan, the suite should report zero failures.

- [ ] **Step 4: Run whitespace and JSON checks**

Run:

```powershell
git diff --check
python -m json.tool src/mingli_engine/data/source_intake/candidate_extracts.json > $null
python -m json.tool src/mingli_engine/data/classical_sources/curation_batches.json > $null
```

Expected: all commands exit with code 0.

- [ ] **Step 5: Commit final verification-only adjustments if any**

If Task 9 required small test/doc corrections, commit them:

```powershell
git add tests docs specs src/mingli_engine/data
git commit -m "chore: finalize data consistency verification"
```

If Task 9 made no file changes, skip this commit.

---

### Task 10: Final State Report And Next-Goal Handoff

**Files:**
- Inspect: `git status`
- Inspect: `git log --oneline -8`

- [ ] **Step 1: Confirm clean status**

Run:

```powershell
git status --short --branch
```

Expected: clean worktree.

- [ ] **Step 2: Capture recent commits**

Run:

```powershell
git log --oneline -8
```

Expected: includes commits for source-intake integrity tests, batch005 candidate repair, curation-batch reference repair, regression snapshot refresh, and documentation snapshot refresh.

- [ ] **Step 3: Write the final report**

Report these items to the user:

```text
Completed:
- Repaired 013 source-intake broken references.
- Repaired formal curation-batch broken references.
- Updated 017 regression expectations to current data.
- Refreshed maintainer snapshots.
- Full test suite passes.

Verified:
- 013 intake quality: []
- 014 source-library quality: []
- 015 materials-audit quality: []
- 016 extraction-package quality: []
- 017 learning-reference quality: []
- Formal evidence loaders: sources=14, approved_evidence=92, curation_batches=4, conflicts=2

Remaining product work:
- Review whether batch005 evidence should stay as formal evidence or be demoted for stricter cross-source confirmation.
- Decide the next extraction wave after current 016/017 coverage.
- Consider adding a single repository-wide data graph integrity command if repeated JSON reference drift continues.
```

- [ ] **Step 4: Do not mark final product complete if full tests fail**

If any verification command fails, report the exact failing command and the first failure. Do not claim completion.

---

## Execution Notes

- Use `apply_patch` for manual file edits.
- Do not run destructive git commands.
- Do not mutate root PDFs, root `Markdown/`, `资料原文/`, or `资料整理/`.
- The default data-preserving path is to add the three missing batch005 candidates because review decisions, promotion batches, and formal evidence already exist.
- If a maintainer explicitly rejects batch005 promotion during execution, stop and write a separate demotion plan instead of silently deleting review, promotion, or evidence records.
- Keep commits small and stage only files touched by the current task.
