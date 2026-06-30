# 015 New Material Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-new-material-intake` by selecting `下海算命记.pdf` as the next bounded source-level intake surface from existing raw-text inventory metadata.

**Architecture:** Add a metadata-only intake layer in `materials_audit` that validates the selected path against the existing `bazi_general_misc_identity_review_cluster`, requires the consumed downstream authorization summary, and routes to `015-new-material-source-identity-review`. The stage does not read, move, convert, register, or promote the source file.

**Tech Stack:** Python dataclasses, JSON fixtures, existing `materials_audit` and `learning_reference_curation` loaders, pytest.

---

## Tasks

- [x] Add failing tests for new material intake item loading, summary, Markdown/docs sync, public API, and next marker.
- [x] Add intake JSON and dataclasses.
- [x] Implement loader validation, summary, renderer, and quality scanning.
- [x] Update materials audit docs, handoff, and quickstart.
- [x] Run focused tests, quality gates, full test suite, whitespace check, and commit.
