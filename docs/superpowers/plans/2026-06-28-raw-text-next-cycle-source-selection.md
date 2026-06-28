# 015 Raw Text Next Cycle Source Selection

## Goal

Complete `015-raw-text-next-cycle-source-selection`: choose the next bounded raw-text source-selection surface from already-inventoried material metadata, keep raw files and downstream 013/012 data unchanged, render the result into maintainer docs, and leave the next long goal explicit.

## Constraints

- Use tracked inventory metadata only.
- Do not parse, convert, move, or rewrite external raw materials.
- Do not register new source-library entries in this stage.
- Do not create or promote 013 candidates or 012 formal evidence.
- Keep `浑天宝鉴` and other large/deferred surfaces outside the next selected work surface.
- Preserve the current external inventory entrypoint as completed before advancing the handoff marker.

## Work Plan

- [x] Add failing tests for `015-raw-text-next-cycle-source-selection` models, loaders, summary, Markdown rendering, docs sync, and handoff marker.
- [x] Add next-cycle source-selection data selecting ordinary identity-review clusters and deferring case/formula/sensitive clusters behind their proper boundaries.
- [x] Implement models, constants, loader validation, summary construction, renderer, and quality-gate coverage.
- [x] Update `docs/classical_sources/materials_audit.md` and `docs/classical_sources/new_material_learning_handoff.md`.
- [x] Run `validate_materials_audit_quality`, focused tests, full tests, `git diff --check`, and commit locally.

## Expected Next Goal

After this goal completes, the next goal should be `015-raw-text-next-cycle-identity-review`: resolve identity/duplicate/registration-readiness for the selected ordinary next-cycle clusters before any source-library registration or learning-reference work.
