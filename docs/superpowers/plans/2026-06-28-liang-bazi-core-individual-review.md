# Liang Bazi Core Individual Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-liang-bazi-core-individual-review` for the two selected Liang Xiangrun cleaned-text surfaces and record the bounded learning outcome in 017 metadata.

**Architecture:** Reuse the existing 017 learning-reference curation model: add two learning reference notes, two learning points, and two applied `reuse_existing` candidate-intake decisions. The work reads cleaned Markdown only for short local review windows, stores concise paraphrases, and does not mutate 013 candidates, 013 reviews, 013 promotion batches, or 012 formal evidence.

**Tech Stack:** Python dataclasses, JSON metadata, pytest, existing `learning_reference_curation.py` validation.

---

## Files

- Modify: `src/mingli_engine/data/learning_reference_curation/learning_reference_notes.json`
- Modify: `src/mingli_engine/data/learning_reference_curation/learning_points.json`
- Modify: `src/mingli_engine/data/learning_reference_curation/candidate_intake_decisions.json`
- Modify: `tests/unit/test_learning_reference_curation.py`
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Create: `docs/superpowers/plans/2026-06-28-liang-bazi-core-individual-review.md`

## Tasks

### Task 1: RED Tests

- [x] Add tests in `tests/unit/test_learning_reference_curation.py` for the two individual review notes, their learning points, and their applied `reuse_existing` decisions.
- [x] Update summary, authorization, and handoff tests to expect 16 closed notes, 30 applied decisions, 3 reuse decisions, and unchanged 013/012 counts.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q` and confirm failures before data changes.

### Task 2: 017 Data

- [x] Add `note_liang_tianyuan_wuxian_individual_review_001`.
- [x] Add `note_liang_yushi_yongshen_individual_review_001`.
- [x] Add one learning point for Tianyuan Wuxian commentary focused on day-master/use-god distinction and ordinary/sensitive boundary handling.
- [x] Add one learning point for Yushi Yongshen Ciyuan focused on month-branch use-god taxonomy and harm/interference hierarchy.
- [x] Add two applied `reuse_existing` decisions that reference existing batch 004 candidate ids.

### Task 3: Docs

- [x] Add a short `Liang Bazi Core Individual Review` section to `docs/classical_sources/learning_reference_curation.md`.
- [x] Update `docs/classical_sources/new_material_learning_handoff.md` with completed individual review snapshot and a new next target.
- [x] Keep explicit guardrails: no 013/012 changes, no long source passages, no exact outcome or high-risk instruction.

### Task 4: Verification And Commit

- [x] Run `uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q`.
- [x] Run `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q`.
- [x] Run `uv run --with pytest python -m pytest -q` with UTF-8 output on Windows.
- [x] Run learning-reference and materials-audit quality validators and confirm both return `[]`.
- [x] Review `git diff`.
- [x] Commit locally with `feat: review liang bazi individual sources`.
