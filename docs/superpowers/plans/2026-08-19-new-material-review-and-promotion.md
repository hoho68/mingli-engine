# New Material Review And Promotion (Task 4) Implementation Plan

**Date**: 2026-08-19 | **Parent plan**: [2026-08-09-new-material-multi-tranche-extraction.md](2026-08-09-new-material-multi-tranche-extraction.md) Task 4 | **Batch**: `batch_20260714`

## Owner-Authorized Scope

The owner selected **full automatic promotion** and confirmed the **family-mapping + in-scope full promotion** implementation after reviewing these measured facts:

- 294 active validated outputs yield 1,808 learning points and 1,970 rule candidates.
- The candidates use 1,783 distinct free-text rule-family labels (1,733 singletons); none uses the ten governed `RULE_FAMILIES` directly, so promotion requires a governed family-mapping artifact.
- 648 candidates come from non-bazi systems (dream omens, liuyao, meihua, ziwei, xuankong fengshui, date selection, acupuncture/ritual) that can never enter the bazi knowledge chains; they become `learned_not_promoted` batch learning records.
- Prototype with the frozen rule set below: 876 promotable, 648 out-of-scope system, 362 unmapped family, 80 gate-rejected (48 high-risk narrowing, 29 safety classifier, 3 lifespan markers), 3 out-of-scope family, 1 over-length; zero batch-internal or legacy signature duplicates.
- The 29 safety-classifier rejections are health/illness description candidates; the runtime safety classifiers remain in force and are not overridden.

## Architecture

1. **Frozen family-map artifact** `batch_20260714_rule_family_map.json` (digest-frozen SHA-256 constant in `new_material_learning.py`, same pattern as the policy-reclassification ledger):
   - `file_systems`: per-file SHA-256 system classification (`bazi` or a named out-of-scope system) with a statement.
   - `out_of_scope_keywords`: ordered keywords marking non-engine families inside bazi files.
   - `family_rules`: ordered (governed family, keywords) rules; first match wins; no match is `unmapped_family`.
   - `file_schools`: conservative per-file school labels (盲派/子平/empty).
2. **Batch review-records ledger** `batch_20260714_learning_records.json` (schema `new-material-learning-review-records-v1`): one immutable record per learning point and per rule candidate with stable IDs `{file_result_id}-o{output:03d}-learning-{seq:03d}` / `-candidate-{seq:03d}`, full provenance (file hash, validated output id, tranche id, output hash, locators), mapping outcome, deterministic gate decision (`eligible`, `duplicate_legacy`, `duplicate_batch`, `out_of_scope_system`, `out_of_scope_family`, `unmapped_family`, `rejected`), gate reason, signature, and promoted 013/012 IDs (filled at promotion time).
3. **Deterministic gates** (existing `evaluate_promotion_candidate` on the mapped candidate, plus): locators inside the output page range; conclusion and each limitation ≤ 280 chars; non-empty limitations (013 `approval_limitations` contract); safety classifiers pass; batch-internal signature dedup (first wins in manifest/page/sequence order); legacy signature dedup against 013 candidates and 012 evidence; documented-conflict families attach existing `conflict_ids` to new evidence instead of blocking.
4. **Registration**: only files with at least one promoted candidate are registered: 012 `sources.json` (`source_batch_20260714_{sha12}`, `review_status=approved`, `extraction_status=partial`) and 013 `source_materials.json` (`material_batch_20260714_{sha12}`, linked `related_source_id`).
5. **013 writes**: `candidate_extracts` (`status=promoted` after batch application, `source_locator=page:X-Y`, `created_by=batch_20260714_review_pipeline`), `review_decisions` (`approved`, reviewer `batch_20260714_review_pipeline`, `source_quality=direct_extract`, `confidence=moderate`, `approval_limitations` = candidate limitations), one `promotion_batches` record `promotion_batch_20260714_001` (`reviewed`).
6. **012 writes**: `evidence_units` (`b20260714_evidence_{seq:04d}`, `source_ref=page:X-Y`, `summary=conclusion`, `applicability=trigger_conditions`, `source_quality=direct_extract`, `confidence=moderate`, school from `file_schools`, conflict links for documented-conflict families), one `curation_batches` record `batch_new_material_20260714_001` (`reviewed`).
7. **File results v4**: `FileLearningResult` learned-state validation gains a multi-tranche form (multiple `source_locators`; single-shot binding fields empty); the ledger schema becomes `new-material-learning-file-results-v4` while the loader keeps accepting v3 for the archived generation. Rebuilt statuses: `promoted` (≥1 promoted candidate), `duplicate` (all candidates duplicates), `learned_not_promoted` (otherwise, with durable reason and recovery condition).
8. **CLI**: `build-learning-records` derives the review-records ledger from frozen extraction inputs (read-only for upstream chains); `promote-learning-records --confirm-promotion` performs registration, 013/012 writes, and file-results rebuild in one governed step, then revalidates every touched chain.

## Governance Rules

- Legacy 017/013/012 records are never mutated; all writes are pure appends plus the new batch records.
- The 017 learning-reference chain is intentionally untouched (no fabricated 014/015/016 upstream records); batch learning notes live in the batch review-records ledger.
- Runtime safety classifiers, high-risk narrowing, and absolute-wording gates are not relaxed.
- Every rejected or non-promoted candidate keeps a durable machine-readable reason in the review-records ledger.
- Raw intake files are never read; promotion consumes only tracked validated outputs.

## Verification

- Focused red-green tests for mapping, ledger build, gates, registration, 013/012 writes, and file-results v4.
- `validate_intake_quality()`, `validate_candidate_links()`, `validate_curation_quality()`, `validate_learning_reference_quality() == []`.
- Update hard-bound count tests and docs markers to the post-promotion state; full suite with `-m "not task8_post_audit"`, mypy, Ruff, `git diff --check`.
- Regenerate `docs/classical_sources/new_material_20260714_learning.md`; Task 5 batch closure (rehash, Task 8 regression, final audit) remains a separate step.

## Task Checklist

- [x] 1. Frozen family-map artifact + loader tests.
- [x] 2. Review-records ledger models, builder, loader, writer + tests.
- [x] 3. Source/material registration + tests.
- [x] 4. 013 candidate/review/batch writer + tests.
- [x] 5. 012 evidence/curation-batch writer + tests.
- [x] 6. File-results v4 contract + rebuild + tests.
- [x] 7. CLI wiring (`build-learning-records`, `promote-learning-records --confirm-promotion`).
- [x] 8. Execute promotion on tracked data; run all chain validators.
- [x] 9. Update hard-bound tests and docs markers; full suite, mypy, Ruff, diff check.
- [x] 10. Regenerate acceptance report; update checkpoints in both plans. (Completed during Task 5 batch closure on 2026-08-19: controlled regression, final audit `3c4738c7…`, post-audit tests 7/7, full suite 2403 passed / 1 skipped.)
