# Raw Text Next Cycle Sensitive Risk Review Prep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-raw-text-next-cycle-sensitive-risk-review-prep` by routing the sensitive-topic representative paths into source-level risk review, block, or defer decisions without creating source-library, 013, or 012 downstream records.

**Architecture:** Follow the existing materials-audit metadata pattern: add sensitive-prep dataclasses, JSON loader, summary builder, markdown renderer, quality validation coverage, and synchronized docs. The step uses only registered path labels and project metadata; external raw materials are not read, moved, converted, or rewritten.

**Tech Stack:** Python 3.12 dataclasses, project-local JSON metadata, pytest, Markdown docs.

---

### Task 1: RED Tests For Sensitive Risk Review Prep

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Add public API expectations**

Add `load_raw_text_next_cycle_sensitive_risk_review_prep_items`, `build_raw_text_next_cycle_sensitive_risk_review_prep_summary`, and `render_raw_text_next_cycle_sensitive_risk_review_prep_markdown` to the materials-audit public callable test.

- [x] **Step 2: Add item loader tests**

Add tests that expect three sensitive prep records:
- `sensitive_risk_prep_bazi_psychology_pdf`,
- `sensitive_risk_prep_erotic_fate_collection_pdf`,
- `sensitive_risk_prep_bazi_comic_ppt`.

Assert all records reference `gated_prep_sensitive_topic_boundary_001`, stay in `bazi_general_sensitive_topic_cluster`, have `risk_boundary == "sensitive"`, use relative paths only, and keep both mutation flags false.

- [x] **Step 3: Add summary closure tests**

Assert the summary has:
- `selection_id == "015-raw-text-next-cycle-sensitive-risk-review-prep"`,
- `selection_status == "sensitive_risk_review_prep_completed"`,
- status counts for prepared, blocked, and deferred equal one each,
- no source-library, candidate, or evidence counts,
- `next_material_entry == "015-raw-text-next-cycle-sensitive-source-level-risk-review"`,
- all boundary checks pass.

- [x] **Step 4: Add markdown/docs sync tests**

Assert the rendered section appears in:
- `docs/classical_sources/materials_audit.md`,
- `docs/classical_sources/new_material_learning_handoff.md`.

- [x] **Step 5: Run RED focused tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -k sensitive_risk_review_prep -q`

Expected: fail because the loader, summary, renderer, and JSON data do not exist yet.

### Task 2: Implement Sensitive Prep Metadata

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_sensitive_risk_review_prep_items.json`

- [x] **Step 1: Add dataclasses**

Add `RawTextNextCycleSensitiveRiskReviewPrepItem` and `RawTextNextCycleSensitiveRiskReviewPrepSummary`.

- [x] **Step 2: Add constants and imports**

Add:
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_RISK_REVIEW_PREP_ID`,
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_RISK_REVIEW_PREP_NEXT_MATERIAL_ENTRY`,
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_RISK_REVIEW_PREP_STATUSES`.

- [x] **Step 3: Add parser and loader**

Validate each prep item:
- references `gated_prep_sensitive_topic_boundary_001`,
- references `next_cycle_bazi_sensitive_topic_risk_review`,
- stays in `bazi_general_sensitive_topic_cluster`,
- has one bounded relative path,
- uses only supported target rule families,
- keeps source-library and downstream mutation unauthorized,
- matches status/action pairs: prepared/risk_review, blocked/block, deferred/defer.

- [x] **Step 4: Add summary and renderer**

The summary must verify:
- final ordinary selection is already complete,
- all sensitive representative paths are covered by the three prep records,
- only one record is prepared for later source-level risk review,
- no downstream metadata was created in this step,
- external raw materials were not mutated.

- [x] **Step 5: Include sensitive prep items in text-quality validation**

Load the new items in `validate_materials_audit_quality()` and include title, paths, boundary decision, rationale, review topics, and guardrails in `_iter_quality_text_fields()`.

- [x] **Step 6: Add JSON records**

Create three records:
- psychology PDF: prepared for source-level risk review,
- erotic fate collection PDF: blocked after sensitive prep,
- comic PPT: deferred after sensitive prep.

- [x] **Step 7: Run focused tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -k sensitive_risk_review_prep -q`

Expected: pass.

### Task 3: Update Docs And Handoff

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Insert rendered sensitive-prep markdown**

Generate `render_raw_text_next_cycle_sensitive_risk_review_prep_markdown(summary)` and insert it after the final ordinary selection section.

- [x] **Step 2: Update handoff next target**

Change the next target from `015-raw-text-next-cycle-sensitive-risk-review-prep` to `015-raw-text-next-cycle-sensitive-source-level-risk-review`.

- [x] **Step 3: Update quickstart marker**

Change `next-new-material-start` to `015-raw-text-next-cycle-sensitive-source-level-risk-review`.

- [x] **Step 4: Run docs tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py::test_new_material_learning_handoff_tracks_final_state -q`

Expected: pass.

### Task 4: Verify And Commit

**Files:**
- All changed files.

- [x] **Step 1: Run focused materials-audit tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q`

- [x] **Step 2: Run quality gates**

Run the project quality-gate command for source-library, materials-audit, extraction-queue-intake, learning-reference-curation, and source-intake validators.

- [x] **Step 3: Run full tests**

Run: `uv run --with pytest python -m pytest -q`

- [x] **Step 4: Inspect diff**

Run: `git diff --check` and `git diff --stat`.

- [x] **Step 5: Commit**

Stage and commit with:

```bash
git add .
git commit -m "feat: prep sensitive raw text risk review"
```

After the commit, mark the goal complete and tell the user the next target is `015-raw-text-next-cycle-sensitive-source-level-risk-review`.
