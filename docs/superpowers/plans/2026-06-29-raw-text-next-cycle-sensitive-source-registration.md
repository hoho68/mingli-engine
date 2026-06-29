# Raw Text Next Cycle Sensitive Source Registration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete `015-raw-text-next-cycle-sensitive-source-registration` by registering `entry_bazi_general_bazi_psychology_pdf` from prepared sensitive metadata while keeping 013 and 012 downstream mutation gated.

**Architecture:** Use `raw_text_next_cycle_sensitive_registration_prep_items.json` as the source of truth for the new source-library entry and add a small source-registration audit layer to link the registered entry back to prep. The stage mutates only project-tracked source-library metadata and materials-audit registration metadata; it does not read raw files or create learning, candidate, review, promotion, or formal evidence records.

**Tech Stack:** Python 3.12 dataclasses, project-local JSON metadata, pytest, Markdown docs.

---

### Task 1: RED Tests For Sensitive Source Registration

**Files:**
- Modify: `tests/unit/test_materials_audit.py`
- Modify: `tests/unit/test_source_library.py`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Add public API expectations**

Add `load_raw_text_next_cycle_sensitive_source_registration_items`, `build_raw_text_next_cycle_sensitive_source_registration_summary`, and `render_raw_text_next_cycle_sensitive_source_registration_markdown` to the materials-audit public callable test.

- [x] **Step 2: Add materials-audit registration tests**

Expect one registration audit item:
- `sensitive_source_registration_bazi_psychology_pdf`,
- registered entry `entry_bazi_general_bazi_psychology_pdf`,
- registered material `material_bazi_general_bazi_psychology_pdf`,
- prep item `sensitive_registration_prep_bazi_psychology_pdf`,
- source-library mutation authorized true,
- downstream mutation authorized false.

- [x] **Step 3: Add summary closure tests**

Assert:
- `registration_id == "015-raw-text-next-cycle-sensitive-source-registration"`,
- `registration_status == "sensitive_source_registration_completed"`,
- one registered entry and one registered file,
- candidate/evidence counts stay zero,
- blocked/deferred sensitive prep ids remain unavailable,
- `next_material_entry == "015-raw-text-next-cycle-sensitive-preparation-boundary"`,
- all boundary checks pass.

- [x] **Step 4: Add source-library tests**

Assert `source_library.load_source_library_entries()` includes:
- `entry_bazi_general_bazi_psychology_pdf`,
- `material_bazi_general_bazi_psychology_pdf`,
- `risk_tier == "sensitive"`,
- `readiness_status == "needs_preparation"`,
- `next_action == "prepare_material"`,
- rule family `ten_god_relation`.

- [x] **Step 5: Run RED focused tests**

Run: `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -k sensitive_source_registration -q`

Expected: fail because the registration loader, summary, renderer, and registered source-library entry do not exist yet.

### Task 2: Implement Sensitive Source Registration

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/materials_audit.py`
- Create: `src/mingli_engine/data/materials_audit/raw_text_next_cycle_sensitive_source_registration_items.json`
- Modify: `src/mingli_engine/data/source_library/source_library_entries.json`
- Modify: `src/mingli_engine/data/source_library/source_priority_assessments.json`

- [x] **Step 1: Add dataclasses**

Add `RawTextNextCycleSensitiveSourceRegistrationItem` and `RawTextNextCycleSensitiveSourceRegistrationSummary`.

- [x] **Step 2: Add constants and imports**

Add:
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_REGISTRATION_ID`,
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_REGISTRATION_NEXT_MATERIAL_ENTRY`,
- `RAW_TEXT_NEXT_CYCLE_SENSITIVE_SOURCE_REGISTRATION_STATUSES`.

- [x] **Step 3: Add parser and loader**

Validate:
- registration item references the sensitive registration-prep item,
- source-library entry exists,
- entry metadata matches prep metadata,
- source-library mutation is authorized,
- downstream mutation remains unauthorized,
- blocked/deferred sensitive prep ids are not registered.

- [x] **Step 4: Add summary and renderer**

The summary must verify:
- sensitive registration prep is complete,
- registered entry and material ids match prep metadata,
- 013/012 counts remain zero,
- raw materials were not mutated,
- next material entry points to the next gated preparation boundary.

- [x] **Step 5: Add source-library entry and assessment**

Append:
- `entry_bazi_general_bazi_psychology_pdf`,
- `assessment_bazi_general_bazi_psychology_pdf`.

Use `readiness_status=needs_preparation`, `next_action=prepare_material`, and sensitive risk notes from prep.

- [x] **Step 6: Include registration audit text in quality validation**

Include registration item rationale and guardrails in `_iter_quality_text_fields()`.

### Task 3: Update Docs And Handoff

**Files:**
- Modify: `docs/classical_sources/materials_audit.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`
- Modify: `docs/classical_sources/source_library.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Insert rendered source-registration markdown**

Generate `render_raw_text_next_cycle_sensitive_source_registration_markdown(summary)` and insert it after sensitive registration prep.

- [x] **Step 2: Update source-library docs**

Add the registered sensitive entry id and update source-library counts.

- [x] **Step 3: Update handoff and quickstart next target**

Set the next target to `015-raw-text-next-cycle-sensitive-preparation-boundary`.

- [x] **Step 4: Run docs tests**

Run focused materials-audit/source-library/handoff tests.

### Task 4: Verify And Commit

**Files:**
- All changed files.

- [x] **Step 1: Run focused materials-audit and source-library tests**

Run:
- `uv run --with pytest python -m pytest tests/unit/test_materials_audit.py -q`
- `uv run --with pytest python -m pytest tests/unit/test_source_library.py -q`

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
git commit -m "feat: register sensitive raw text source"
```

After the commit, mark the goal complete and tell the user the next target is `015-raw-text-next-cycle-sensitive-preparation-boundary`.
