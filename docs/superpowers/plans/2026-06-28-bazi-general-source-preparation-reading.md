# 015 Bazi General Source Preparation Reading

## Goal

Complete the authorized long-stage goal for the three newly registered Bazi
general source-library entries:

- `entry_bazi_general_lecture_textbook_pdf`
- `entry_bazi_general_beichen_intro_pdf`
- `entry_bazi_general_ziping_orthodox_pair_pdf`

The stage is complete when the sources have durable preparation-reading
records, downstream 013 candidate intake/review/promotion records, 012 formal
evidence records, synced documentation, passing tests, and a local commit.

## Boundaries

- Do not move, delete, rename, or rewrite files under `资料原文/`.
- Do not commit full PDF-to-text conversions or long source passages.
- Use temporary conversion/read artifacts only as working material.
- Avoid duplicating Batch 001 overlap already covered by existing evidence.
- Keep Ditiansui/Qiongtong variant-choice work and deferred Huntian Baolan
  material outside this goal.
- Keep user authorization explicit in docs and audit records for 013/012
  advancement.

## Plan

1. Reconfirm the repository state and current 015/016/017/013/012 counts.
2. Write RED tests that expect the new preparation-reading summary and the
   required three-source downstream chain.
3. Read the three PDF sources through the hardened document converter or a
   deterministic local PDF text fallback, writing outputs only to temporary
   scratch space.
4. Add or update data in this order:
   - `source_library`: lifecycle status for the three entries after reading.
   - `materials_audit`: audit records, representations, alignment findings,
     readiness findings, and extraction queue items.
   - `extraction_queue_intake`: one completed work package, three completed
     tasks, and draft slots tied to the candidate intake.
   - `learning_reference_curation`: three notes, learning points, and applied
     candidate-intake decisions.
   - `source_intake`: three source materials, three promoted candidates, three
     approved review decisions, and one reviewed promotion batch.
   - `classical_sources`: three approved source records, three evidence units,
     and one reviewed curation batch.
5. Add a focused source-preparation-reading progress summary and render it into
   handoff/audit documentation.
6. Run targeted tests first, then full `uv run pytest`.
7. Inspect `git diff`, stage the intended files, and create a local commit.

## Expected Next Goal

After this goal, the next large goal should be
`015-bazi-general-variant-choice-and-deferred-review`: resolve the Ditiansui and
Qiongtong variant sets, keep Huntian Baolan deferred unless the needed source
clarity is obtained, and then prepare the next Bazi general source batch.
