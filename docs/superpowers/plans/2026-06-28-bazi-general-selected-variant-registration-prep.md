# Bazi General Selected Variant Registration Prep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Register the selected Ditiansui and Qiongtong local references as source-library metadata and advance them through 013 candidate intake and 012 formal evidence under the user's explicit authorization.

**Architecture:** Reuse the existing Bazi general preparation-reading chain: source-library entries, materials-audit records, 016 extraction tasks, 017 learning notes/points/decisions, 013 candidate/review/promotion, and 012 source/evidence/curation batch. The PDF files stay external and unchanged; evidence uses concise review-note/page anchors with `source_quality=review_note`, not direct quotation.

**Tech Stack:** Python 3.12 dataclass loaders, project JSON metadata, pypdf/Poppler read-only page checks, pytest via `uv run --with pytest python -m pytest`.

---

### Task 1: RED Tests For Selected Variant Registration And Promotion

**Files:**
- Modify: `tests/unit/test_source_library.py`
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_source_intake.py`
- Modify: `tests/unit/test_classical_sources.py`
- Modify: `tests/unit/test_evidence_curation.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Add source-library expectations**

Add two source-library entries to the expected set:

```python
"entry_bazi_general_ditiansui_selected_pdf",
"entry_bazi_general_qiongtong_selected_pdf",
```

Assert:

```python
ditiansui = by_id["entry_bazi_general_ditiansui_selected_pdf"]
assert ditiansui.material_id == "material_bazi_general_ditiansui_selected_pdf"
assert ditiansui.local_reference == "滴天髓.pdf"
assert ditiansui.readiness_status == "review_completed"
assert ditiansui.next_action == "no_action"

qiongtong = by_id["entry_bazi_general_qiongtong_selected_pdf"]
assert qiongtong.material_id == "material_bazi_general_qiongtong_selected_pdf"
assert qiongtong.local_reference == "穷通宝鉴/窮通寶鑒.pdf"
assert qiongtong.readiness_status == "review_completed"
assert qiongtong.next_action == "no_action"
```

Update the gated-identity test so only `huntian` stays unregistered; `ditiansui` and `qiongtong` are now allowed because this goal explicitly selected canonical local references.

- [x] **Step 2: Add 015/016/017 chain expectations**

Add a materials-audit test requiring:

```python
audit_bazi_general_ditiansui_selected_pdf
audit_bazi_general_qiongtong_selected_pdf
queue_bazi_general_ditiansui_pattern_strength_extract
queue_bazi_general_qiongtong_useful_god_extract
```

Add or extend extraction/learning-reference tests requiring:

```python
package_bazi_general_selected_variant_preparation_reading_001
task_bazi_general_ditiansui_pattern_strength_001
task_bazi_general_qiongtong_useful_god_001
note_bazi_general_ditiansui_pattern_strength_001
note_bazi_general_qiongtong_useful_god_001
lp_bazi_general_ditiansui_pattern_strength_001
lp_bazi_general_qiongtong_useful_god_001
decision_bazi_general_ditiansui_pattern_strength_001
decision_bazi_general_qiongtong_useful_god_001
```

- [x] **Step 3: Add 013 source-intake expectations**

Add a focused test for:

```python
expected_materials = {
    "material_bazi_general_ditiansui_selected_pdf": (
        "source_bazi_general_ditiansui_selected_pdf",
        "reviewed",
    ),
    "material_bazi_general_qiongtong_selected_pdf": (
        "source_bazi_general_qiongtong_selected_pdf",
        "reviewed",
    ),
}
expected_candidates = {
    "candidate_bazi_general_ditiansui_pattern_strength_001": (
        "material_bazi_general_ditiansui_selected_pdf",
        "pattern_strength",
        "bazi_general_ditiansui_pattern_strength_001",
    ),
    "candidate_bazi_general_qiongtong_useful_god_001": (
        "material_bazi_general_qiongtong_selected_pdf",
        "useful_god_candidate",
        "bazi_general_qiongtong_useful_god_001",
    ),
}
```

The promotion batch must be:

```python
promotion_bazi_general_selected_variant_preparation_001
```

- [x] **Step 4: Add 012 formal evidence expectations**

Add evidence checks for:

```python
expected_evidence = {
    "bazi_general_ditiansui_pattern_strength_001": (
        "source_bazi_general_ditiansui_selected_pdf",
        "pattern_strength",
    ),
    "bazi_general_qiongtong_useful_god_001": (
        "source_bazi_general_qiongtong_selected_pdf",
        "useful_god_candidate",
    ),
}
```

Each unit must use:

```python
unit.curation_batch_id == "batch_bazi_general_selected_variant_001"
unit.risk_tier == "ordinary"
unit.source_quality == "review_note"
unit.confidence == "weak"
unit.source_ref.startswith("page:")
```

- [x] **Step 5: Update snapshot expectations**

Expected totals after GREEN:

```text
source-library entries: 19
source materials: 19
017 notes: 21
017 learning points: 41
017 candidate-intake decisions: 35
013 candidate extracts: 44
013 review decisions: 44
013 promotion batches: 29
012 formal evidence units: 101
classical sources: 19
curation batches: 8
```

Run focused RED:

```powershell
uv run --with pytest python -m pytest tests/unit/test_source_library.py::test_load_source_library_entries_loads_current_registered_sources tests/unit/test_source_library.py::test_bazi_general_registration_does_not_duplicate_gated_identity_records tests/unit/test_source_intake.py::test_bazi_general_selected_variant_intake_records_are_promoted tests/unit/test_classical_sources.py::test_bazi_general_selected_variant_evidence_is_formalized tests/unit/test_evidence_curation.py::test_project_curation_quality_report_includes_conflicts_and_has_no_failures tests/unit/test_learning_reference_curation.py::test_learning_reference_candidate_formal_evidence_boundary_audit_snapshot -q
```

Expected: FAIL because the selected-variant chain has not been added yet.

### Task 2: GREEN JSON Metadata

**Files:**
- Modify: `src/mingli_engine/data/source_library/source_library_entries.json`
- Modify: `src/mingli_engine/data/source_library/source_priority_assessments.json`
- Modify: `src/mingli_engine/data/materials_audit/material_audit_records.json`
- Modify: `src/mingli_engine/data/materials_audit/material_representations.json`
- Modify: `src/mingli_engine/data/materials_audit/source_alignment_findings.json`
- Modify: `src/mingli_engine/data/materials_audit/preparation_readiness_findings.json`
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

- [x] **Step 1: Add selected-variant source-library entries and priority assessments**

Create:

```text
entry_bazi_general_ditiansui_selected_pdf
entry_bazi_general_qiongtong_selected_pdf
priority_bazi_general_ditiansui_selected_001
priority_bazi_general_qiongtong_selected_001
```

Use `readiness_status=review_completed`, `next_action=no_action`, `risk_tier=ordinary`, and `rights_notes` that prohibit long copied passages.

- [x] **Step 2: Add 015 materials-audit chain**

Add two audit records, representations, alignments, readiness findings, and completed extraction queue items. Use `source_boundary=external_untracked`, `preparation_state=ready_for_extraction_review`, and `status=completed`.

- [x] **Step 3: Add 016 and 017 provenance**

Create one completed package:

```text
package_bazi_general_selected_variant_preparation_reading_001
```

Add two tasks, two draft slots, two learning notes, two learning points, and two applied create-candidate decisions.

- [x] **Step 4: Add 013 candidates, reviews, and promotion batch**

Create:

```text
candidate_bazi_general_ditiansui_pattern_strength_001
candidate_bazi_general_qiongtong_useful_god_001
review_bazi_general_ditiansui_pattern_strength_001
review_bazi_general_qiongtong_useful_god_001
promotion_bazi_general_selected_variant_preparation_001
```

Keep both candidates `status=promoted`, `risk_tier=ordinary`, `source_quality=review_note`, and `confidence=weak`.

- [x] **Step 5: Add 012 sources, evidence, and curation batch**

Create:

```text
source_bazi_general_ditiansui_selected_pdf
source_bazi_general_qiongtong_selected_pdf
bazi_general_ditiansui_pattern_strength_001
bazi_general_qiongtong_useful_god_001
batch_bazi_general_selected_variant_001
```

Use weak/review-note evidence because this pass validates selected-variant reading anchors, not full transcription.

### Task 3: Docs And Verification

**Files:**
- Modify: `docs/classical_sources/source_library.md`
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/extraction_queue_intake.md`
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `docs/classical_sources/intake.md`
- Modify: `docs/classical_sources/coverage.md`
- Modify: `docs/classical_sources/source_ref_quality_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `docs/superpowers/plans/2026-06-28-bazi-general-selected-variant-registration-prep.md`

- [x] **Step 1: Refresh docs to new totals**

Update docs to show 19 source-library entries, 44 013 candidates/reviews, 29 promotion batches, and 101 formal evidence units. Add a selected-variant section naming the two canonical local references and the weak source-quality limitation.

- [x] **Step 2: Run quality gates**

```powershell
$env:PYTHONPATH='src'; $env:PYTHONIOENCODING='utf-8'; uv run python -c "from mingli_engine import source_library, materials_audit, source_intake, learning_reference_curation; from mingli_engine.classical_sources import load_classical_sources, load_evidence_units; from mingli_engine.evidence_curation import validate_curation_quality; print(source_library.validate_source_library_quality()); print(materials_audit.validate_materials_audit_quality()); print(source_intake.validate_intake_quality()); print(learning_reference_curation.validate_learning_reference_quality()); print(validate_curation_quality(load_classical_sources(), load_evidence_units()))"
```

Expected: five empty lists.

- [x] **Step 3: Run focused and full tests**

```powershell
uv run --with pytest python -m pytest tests/unit/test_source_library.py tests/unit/test_materials_audit.py tests/unit/test_source_intake.py::test_bazi_general_selected_variant_intake_records_are_promoted tests/unit/test_classical_sources.py::test_bazi_general_selected_variant_evidence_is_formalized tests/unit/test_evidence_curation.py::test_project_curation_quality_report_includes_conflicts_and_has_no_failures tests/unit/test_learning_reference_curation.py::test_learning_reference_candidate_formal_evidence_boundary_audit_snapshot -q
$env:PYTHONIOENCODING='utf-8'; uv run --with pytest python -m pytest -q
git diff --check
```

Expected: all tests pass and diff check has no whitespace errors.

- [x] **Step 4: Commit**

```powershell
git add docs src tests
git commit -m "feat: promote selected bazi variants"
```
