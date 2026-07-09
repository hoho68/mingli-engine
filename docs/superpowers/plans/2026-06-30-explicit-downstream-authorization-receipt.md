# Explicit Downstream Authorization Receipt Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Record the user's explicit 2026-06-30 authorization for 013/012 downstream work, consume it against the current 017 authorization audit, and route onward without duplicating already-applied candidates or formal evidence.

**Architecture:** Add a read-only authorization receipt layer in `learning_reference_curation` backed by tracked JSON. The layer validates that all 017 candidate-intake decisions are already applied, pending downstream deltas are zero, and 013/012 counts remain aligned, then advances the handoff to new material intake.

**Tech Stack:** Python dataclasses, JSON fixtures, existing `learning_reference_curation`, `source_intake`, and `classical_sources` loaders, pytest.

---

## Files

- Modify `src/mingli_engine/models.py`: add receipt item and summary dataclasses.
- Modify `src/mingli_engine/learning_reference_curation.py`: add loader, validation, summary, renderer, and quality-scan coverage.
- Create `src/mingli_engine/data/learning_reference_curation/downstream_authorization_receipts.json`: single user authorization receipt.
- Modify `tests/unit/test_learning_reference_curation.py`: red/green tests for receipt loading, summary, docs sync, and handoff marker.
- Modify `docs/classical_sources/learning_reference_curation.md`: maintainer-facing receipt section.
- Modify `docs/classical_sources/new_material_learning_handoff.md`: mark authorization consumed and update next target.
- Modify `specs/017-learning-reference-curation/quickstart.md`: update current continuation markers.

## Tasks

- [x] Add failing tests for receipt loading, summary counts, Markdown/docs sync, and handoff next target.
- [x] Add receipt JSON and dataclasses.
- [x] Implement receipt loader, summary, renderer, and quality scanning.
- [x] Update maintainer docs, handoff, and quickstart.
- [x] Run focused tests, full test suite, whitespace check, and commit.
