# Raw Text Next Cycle Sensitive Source-Level Risk Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-raw-text-next-cycle-sensitive-source-level-risk-review` by reviewing the single prepared psychology-labeled sensitive path and deciding whether it can enter later registration preparation without creating source-library, 013, or 012 records.

**Architecture:** Add one source-level risk-review metadata layer after sensitive prep: dataclasses, JSON loader, summary builder, markdown renderer, quality validation, and synchronized docs. The review consumes only existing path-label metadata, keeps blocked/deferred sensitive prep paths unavailable, and separates "cleared for registration prep" from any actual downstream mutation.

**Tech Stack:** Python 3.12 dataclasses, project-local JSON metadata, pytest, Markdown docs.

---

### Task 1: RED Tests For Sensitive Source-Level Risk Review

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Add public API expectations**

Add `load_raw_text_next_cycle_sensitive_source_level_risk_review_items`, `build_raw_text_next_cycle_sensitive_source_level_risk_review_summary`, and `render_raw_text_next_cycle_sensitive_source_level_risk_review_markdown` to the materials-audit public callable test.

- [x] **Step 2: Add item loader tests**

Add tests that expect one review record:
- `sensitive_source_review_bazi_psychology_pdf`,
- it references `sensitive_risk_prep_bazi_psychology_pdf`,
- it has status `cleared_for_sensitive_registration_prep`,
- it keeps `source_library_mutation_authorized == False`,
- it keeps `downstream_mutation_authorized == False`,
- it references only `陆致极王明谦-《八字心理学》东方心理哲学智慧214页.pdf`.

- [x] **Step 3: Add summary closure tests**

Assert:
- `selection_id == "015-raw-text-next-cycle-sensitive-source-level-risk-review"`,
- `selection_status == "sensitive_source_level_risk_review_completed"`,
- `review_item_count == 1`,
- `cleared_for_registration_prep_count == 1`,
- blocked/deferred prep ids remain unavailable,
- source-library/candidate/evidence counts remain zero,
- `next_material_entry == "015-raw-text-next-cycle-sensitive-registration-prep"`,
- all boundary checks pass.

- [x] **Step 4: Add markdown/docs sync tests**

Assert rendered markers appear in:
- `docs/classical_sources/materials_audit.md`,
- `docs/classical_sources/new_material_learning_handoff.md`.

- [x] **Step 5: Run RED focused tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -k sensitive_source_level_risk_review -q`

Expected: fail because the loader, summary, renderer, and JSON data do not exist yet.

### Task 2: Implement Sensitive Source-Level Review Metadata

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_sensitive_source_level_risk_review_items.json`

- [x] **Step 1: Add dataclasses**

Add `RawTextNextCycleSensitiveSourceLevelRiskReviewItem` and `RawTextNextCycleSensitiveSourceLevelRiskReviewSummary`.

- [x] **Step 2: Add constants and imports**

Add:
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_LEVEL_RISK_REVIEW_ID`,
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_LEVEL_RISK_REVIEW_NEXT_MATERIAL_ENTRY`,
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_LEVEL_RISK_REVIEW_STATUSES`.

- [x] **Step 3: Add parser and loader**

Validate:
- only the prepared prep item can be reviewed,
- blocked and deferred prep items are not reviewed,
- exactly one relative path is referenced,
- risk boundary remains `sensitive`,
- recommended action is `register_source`,
- source-library and downstream mutation remain unauthorized,
- no candidate/evidence/source-library ids are present.

- [x] **Step 4: Add summary and renderer**

The summary must verify:
- sensitive risk-review prep is complete,
- the reviewed item matches the prepared prep id,
- blocked/deferred prep ids remain unavailable,
- no downstream metadata is created,
- external raw materials were not read, moved, converted, or rewritten.

- [x] **Step 5: Include review items in text-quality validation**

Load new items in `validate_materials_audit_quality()` and include title, path, risk findings, boundary decision, rationale, and guardrails in `_iter_quality_text_fields()`.

- [x] **Step 6: Add JSON record**

Create one record:
- `sensitive_source_review_bazi_psychology_pdf`.

- [x] **Step 7: Run focused tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -k sensitive_source_level_risk_review -q`

Expected: pass after docs sync is complete.

### Task 3: Update Docs And Handoff

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Insert rendered source-level review markdown**

Generate `render_raw_text_next_cycle_sensitive_source_level_risk_review_markdown(summary)` and insert it after the sensitive prep section.

- [x] **Step 2: Update handoff next target**

Change the next target from `015-raw-text-next-cycle-sensitive-source-level-risk-review` to `015-raw-text-next-cycle-sensitive-registration-prep`.

- [x] **Step 3: Update quickstart marker**

Change `next-new-material-start` to `015-raw-text-next-cycle-sensitive-registration-prep`.

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
git commit -m "feat: review sensitive raw text source risk"
```

After the commit, mark the goal complete and tell the user the next target is `015-raw-text-next-cycle-sensitive-registration-prep`.
