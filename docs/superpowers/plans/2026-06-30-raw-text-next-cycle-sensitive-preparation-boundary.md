# Raw Text Next Cycle Sensitive Preparation Boundary Implementation Plan

## Goal

Complete `015-raw-text-next-cycle-sensitive-preparation-boundary` for the registered sensitive source `entry_bazi_general_bazi_psychology_pdf`.

The stage must use only registered metadata and path labels. It must not read, convert, move, or rewrite the raw PDF, and it must keep 013 candidate intake and 012 formal evidence gated.

## Steps

- [x] Locate the existing sensitive source registration pipeline and docs markers.
- [x] Add focused tests for boundary item loading, summary closure, and docs sync.
- [x] Add boundary metadata JSON for the registered sensitive source.
- [x] Add models, loader validation, summary builder, renderer, and quality scanning hooks.
- [x] Run focused RED/GREEN tests for the new sensitive preparation boundary.
- [x] Render and insert the new docs section, then advance handoff/quickstart next markers.
- [x] Run related quality gates and full tests.
- [x] Commit the completed stage and mark the goal complete.
