# 015 External Material Inventory Refresh

Goal: scan external preparation entrypoints, compare them with tracked 015
metadata, register only clear in-scope 015 metadata gaps, and keep 013/012
downstream evidence unchanged.

## Scope

- External roots: root PDFs, `Markdown/`, `资料原文/`, and `资料整理/`.
- Register the Life Death Book Markdown extract as a representation of the
  existing Life Death Book audit record.
- Register `资料原文/文本类/` as a bounded raw-folder backlog entry that requires
  risk-aware triage before source-library registration or extraction.
- Treat `_inventory`, old thread prompts, and handoff notes as workflow
  artifacts, not source material.

## Guardrails

- Do not move, delete, rewrite, convert, or commit external raw/preparation
  materials.
- Do not create 013 candidates, review decisions, promotion batches, or 012
  formal evidence.
- Keep all changes in 015 metadata, tests, and maintainer documentation.

## Steps

- [x] Scan external roots and current 015 references.
- [x] Add failing tests for the external inventory refresh summary and docs.
- [x] Add 015 metadata for the Life Death Markdown representation and raw text
  folder triage backlog.
- [x] Implement the refresh summary and Markdown renderer.
- [x] Sync maintainer docs and handoff.
- [x] Run targeted and full verification.
- [x] Commit local changes and announce the next long goal.
