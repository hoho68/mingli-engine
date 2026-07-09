# Raw Text Next Cycle Gated Ordinary Final Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Complete `015-raw-text-next-cycle-gated-ordinary-final-selection` by selecting the remaining bounded ordinary gated source-level records and registering their 014/015/016/017/013/012 weak-locator metadata.

**Architecture:** Follow the existing source-selection and followup-selection pattern in `materials_audit.py`: add final-selection dataclasses, JSON loader, summary builder, renderer, quality-gate coverage, and synchronized docs. Downstream records are deterministic metadata entries only; external raw PDF files are not opened, moved, converted, or rewritten.

**Tech Stack:** Python 3.12 dataclasses, project-local JSON metadata, pytest, Markdown docs.

---

### Task 1: RED Tests For Final Ordinary Gated Selection

**Files:**
- Modify: `tests/unit/test_materials_audit.py`

- [x] **Step 1: Add tests for final selection items**

Add tests that expect:
- two final selected records,
- selected ids `gated_ordinary_final_source_choujin_bosi_case_collection` and `gated_ordinary_final_source_bazi_shizhan_mifa_formula`,
- paths `鍏瓧18鏈?鎶界瓔鍓ヤ笣璁插叓瀛? 274P.pdf` and `鍏瓧瀹炴垬绉樻硶鍏紑.pdf`,
- no duplication with source-selection or followup-selection paths.

- [x] **Step 2: Add tests for final summary closure**

Add tests that expect:
- `selection_id == "015-raw-text-next-cycle-gated-ordinary-final-selection"`,
- `selection_status == "gated_ordinary_final_selection_completed"`,
- all registration/candidate/evidence counts equal 2,
- `next_material_entry == "015-raw-text-next-cycle-sensitive-risk-review-prep"`,
- `ordinary_representative_paths_exhausted` and `sensitive_cluster_remains_risk_review` boundary checks pass.

- [x] **Step 3: Add markdown/docs sync tests**

Assert the rendered final-selection section appears in:
- `docs/classical_sources/materials_audit.md`,
- `docs/classical_sources/new_material_learning_handoff.md`.

- [x] **Step 4: Run the new tests and confirm RED**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -k gated_ordinary_final -q`

Expected: fail because the loader, summary, renderer, and JSON data do not exist yet.

### Task 2: Implement Final Selection Loader And Summary

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_gated_ordinary_final_selection_items.json`

- [x] **Step 1: Add dataclasses**

Add `RawTextNextCycleGatedOrdinaryFinalSelectionItem` and `RawTextNextCycleGatedOrdinaryFinalSelectionSummary`, mirroring the followup dataclasses and preserving `prior_selection_id`.

- [x] **Step 2: Add constants and imports**

Add:
- `RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FINAL_SELECTION_ID`,
- `RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FINAL_SELECTION_NEXT_MATERIAL_ENTRY`,
- `RAW_TEXT_NEXT_CYCLE_GATED_ORDINARY_FINAL_SELECTION_STATUSES`.

Import the new dataclasses into `materials_audit.py`.

- [x] **Step 3: Add item parser and loader**

Add `_raw_text_next_cycle_gated_ordinary_final_selection_item_from_dict()` and `load_raw_text_next_cycle_gated_ordinary_final_selection_items()`, validating:
- final items reference followup selection ids,
- selected paths do not duplicate any earlier ordinary gated selected path,
- cluster ids are the ordinary deferred case/formula clusters,
- source-library and downstream mutation are explicitly authorized.

- [x] **Step 4: Add summary and renderer**

Add `build_raw_text_next_cycle_gated_ordinary_final_selection_summary()` and `render_raw_text_next_cycle_gated_ordinary_final_selection_markdown()`.

The summary must verify:
- source-library entries exist,
- source materials exist,
- 013 candidates are promoted,
- 012 evidence references matching source ids,
- all ordinary representative paths from the case/formula clusters are now covered,
- the sensitive cluster remains in risk review.

- [x] **Step 5: Include final items in text-quality validation**

Load final items in `validate_materials_audit_quality()` and pass them through `_iter_quality_text_fields()`.

- [x] **Step 6: Add final-selection JSON records**

Create two records:
- `gated_ordinary_final_source_choujin_bosi_case_collection`,
- `gated_ordinary_final_source_bazi_shizhan_mifa_formula`.

- [x] **Step 7: Run focused materials-audit tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -k gated_ordinary_final -q`

Expected: pass once downstream metadata exists; if downstream references are not written yet, fail only on expected missing registration/candidate/evidence checks.

### Task 3: Register Downstream Metadata

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

- [x] **Step 1: Upsert 014 source-library records**

Register entries for:
- `entry_bazi_general_choujin_bosi_case_pdf`,
- `entry_bazi_general_bazi_shizhan_mifa_pdf`.

- [x] **Step 2: Upsert 015 audit/representation/readiness/alignment/queue records**

Add matching records for both final selected source files, with weak locator readiness and no raw-file mutation.

- [x] **Step 3: Upsert 016 work package, tasks, and slots**

Add `package_bazi_general_gated_ordinary_final_selection_001` and two extraction tasks/slots.

- [x] **Step 4: Upsert 017 notes, learning points, and decisions**

Add one note and one learning point per final selected source, with `candidate_ready` decisions.

- [x] **Step 5: Upsert 013 source materials, candidates, reviews, and promotion batch**

Add promoted candidates:
- `candidate_bazi_general_choujin_bosi_branch_interaction_001`,
- `candidate_bazi_general_bazi_shizhan_mifa_luck_cycle_001`.

- [x] **Step 6: Upsert 012 sources, evidence, and curation batch**

Add source ids and evidence ids matching the candidates.

### Task 4: Update Docs And Counts

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `docs/classical_sources/source_library.md`
- Modify: `docs/classical_sources/extraction_queue_intake.md`
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `docs/classical_sources/source_intake.md`
- Modify: `docs/classical_sources/source_ref_audit.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`
- Modify tests that assert deterministic counts.

- [x] **Step 1: Insert rendered final-selection markdown**

Generate final-selection markdown from `materials_audit.py` and insert it after the followup-selection section.

- [x] **Step 2: Update handoff**

Add the final-selection checkpoint, plan link, updated counts, and next target:
`015-raw-text-next-cycle-sensitive-risk-review-prep`.

- [x] **Step 3: Update domain docs and quickstart counts**

Refresh count tables and add the two final source ids where existing docs enumerate current state.

- [x] **Step 4: Update count-sensitive tests**

Update source-library, extraction-queue, learning-reference, source-intake, classical-source, integration, and safety tests where they assert current totals or selected ids.

### Task 5: Verify And Commit

**Files:**
- All changed files.

- [x] **Step 1: Run focused tests**

Run:
- `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q`
- `uv run --with pytest python -m pytest tests/unit/test_source_library.py tests/unit/test_extraction_queue_intake.py tests/unit/test_learning_reference_curation.py tests/unit/test_source_intake.py tests/unit/test_classical_sources.py -q`

- [x] **Step 2: Run quality gates**

Run the project quality-gate command used by the existing tests and fix any failures.

- [x] **Step 3: Run full tests**

Run: `uv run --with pytest python -m pytest -q`

- [x] **Step 4: Inspect diff**

Run: `git diff --check` and `git diff --stat`.

- [x] **Step 5: Commit**

Stage and commit with:

```bash
git add .
git commit -m "feat: select gated ordinary final raw text sources"
```

After the commit, mark the goal complete and tell the user the next target is `015-raw-text-next-cycle-sensitive-risk-review-prep`.

