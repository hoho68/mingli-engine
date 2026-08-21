# New Material Learning Restart Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Process all 29 non-video files in the `2026.07.14新增资料` intake, preserve validated legacy knowledge, autonomously promote only verified knowledge, and close the batch with every file in a terminal state.

**Architecture:** Add a small restart-specific manifest and orchestration layer beside the existing materials-audit and learning-reference pipelines. Raw files stay outside Git; tracked JSON stores hashes, per-file remote authorization receipts, routing, source locators, candidate/review states, and final disposition. Remote processing is default-deny, every parser receives only a verified read-only temporary copy, and Codex verifies every promotion against existing reviewed 013/012 data and regression tests.

**Tech Stack:** Python 3.13 standard library, project dataclasses and JSON loaders, `uv`, pytest 8.4.1, Poppler text probing, local DeepSeek command/service, local `kimi-cli`, existing `materials_audit`, `learning_reference_curation`, `source_intake`, and `classical_sources` validators.

**Local constraint:** Git author identity is intentionally not configured. Replace commit steps with `git diff --check` and `git status --short` checkpoints; do not create commits until the user changes this instruction.

**OpenCode execution override:** When this plan is executed from OpenCode, follow
`docs/superpowers/plans/2026-08-08-new-material-learning-opencode-handoff.md` for provider authentication and model selection. Its explicit OpenCode bindings (`deepseek/deepseek-chat`, `deepseek/deepseek-reasoner`, `kimi-for-coding/k3-256k`, and `kimi-for-coding/k3`) supersede the standalone CLI discovery and Kimi CLI wording below; all schemas, gates, tests, and terminal-state requirements in this plan remain authoritative.

---

## File map

- Create `src/mingli_engine/new_material_learning.py`: manifest models, hashing, video exclusion, terminal-state validation, summaries, and local-model routing records.
- Create `src/mingli_engine/data/new_material_learning/batch_20260714_manifest.json`: tracked metadata for the 29 non-video files; no raw content.
- Create `src/mingli_engine/data/new_material_learning/batch_20260714_remote_authorizations.json`: strict manifest-bound per-file remote-processing receipts; absence of explicit scope is denial.
- Create `src/mingli_engine/data/new_material_learning/batch_20260714_model_runs.json`: resumable local-model run receipts.
- Create `src/mingli_engine/data/new_material_learning/batch_20260714_file_results.json`: per-file learning, locator, review, promotion, and final-state records.
- Create `src/mingli_engine/data/new_material_learning/batch_20260714_task8_command_evidence.json`: strict command names, exit codes, normalized results, and repository-status snapshot.
- Create `src/mingli_engine/data/new_material_learning/batch_20260714_final_audit.json`: source-only audit bound to command evidence, checked Task 8 state, reviewed paths, protected legacy knowledge JSON, and all upstream ledgers.
- Create `tests/unit/test_new_material_learning.py`: manifest, exclusion, routing, state, and quality-gate tests.
- Modify `src/mingli_engine/cli.py`: add read-only summary/validation commands and explicit batch execution commands.
- Modify existing JSON under `src/mingli_engine/data/learning_reference_curation/`, `source_intake/`, and `classical_sources/` only when verified candidates pass the autonomous promotion gate.
- Create `docs/classical_sources/new_material_20260714_learning.md`: human-readable progress and final acceptance report.

### Task 1: Establish a clean baseline and model-entry gates

**Files:**
- Read: `pyproject.toml`
- Read: `src/mingli_engine/cli.py`
- Read: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Verify the repository baseline**

Run:

```powershell
uv sync --frozen
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest -m "not task8_post_audit" -q -p no:cacheprovider
```

Expected: dependency sync exits 0 and the full existing suite passes before new work begins.

- [x] **Step 2: Verify local model entry points without sending material**

Run:

```powershell
Get-Command kimi,kimi-cli -ErrorAction SilentlyContinue
Get-Command deepseek,ollama,lmstudio,llama-server -ErrorAction SilentlyContinue
kimi-cli --help
```

Expected: `kimi-cli` resolves locally. DeepSeek must resolve to a local command or an explicitly identified localhost service before any DeepSeek task runs. If no local DeepSeek entry exists, stop text-model dispatch and record the blocker; do not substitute a remote API.

- [x] **Step 3: Record the clean checkpoint**

Run:

```powershell
git diff --check
git status --short --branch
```

Expected: only the approved design and plan documents differ from HEAD.

### Task 2: Build the manifest and hard video exclusion

**Files:**
- Create: `src/mingli_engine/new_material_learning.py`
- Create: `tests/unit/test_new_material_learning.py`
- Create: `src/mingli_engine/data/new_material_learning/batch_20260714_manifest.json`

- [x] **Step 1: Write failing tests for hashing, relative paths, and video exclusion**

Add tests using temporary `.pdf`, `.docx`, and `.mp4` files. Assert that `build_manifest()` returns two records, reports one excluded video, calculates uppercase SHA256 values, and never opens the video payload.

```python
def test_build_manifest_excludes_video_and_hashes_non_video_files(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"pdf")
    (tmp_path / "b.docx").write_bytes(b"docx")
    (tmp_path / "ignored.mp4").write_bytes(b"video")
    manifest = build_manifest(tmp_path)
    assert [item.relative_path for item in manifest.files] == ["a.pdf", "b.docx"]
    assert manifest.excluded_video_count == 1
    assert all(len(item.sha256) == 64 for item in manifest.files)
```

- [x] **Step 2: Run the focused test and confirm RED**

Run:

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_new_material_learning.py::test_build_manifest_excludes_video_and_hashes_non_video_files -q -p no:cacheprovider
```

Expected: FAIL because `new_material_learning` does not exist.

- [x] **Step 3: Implement immutable manifest records**

Implement `ManifestFile`, `LearningBatchManifest`, `build_manifest(root)`, and `write_manifest(path, manifest)`. Use a fixed case-insensitive video extension set and `hashlib.sha256`; sort records by Unicode relative path. The writer must reject paths inside the intake root so raw input is never overwritten.

- [x] **Step 4: Generate the real manifest**

Run:

```powershell
$env:PYTHONPATH='src'
uv run --frozen python -m mingli_engine.new_material_learning manifest `
  --root 'E:\_mingli-new-material-intake\2026.07.14新增资料' `
  --output 'src\mingli_engine\data\new_material_learning\batch_20260714_manifest.json'
```

Expected: `file_count=29`, `pdf_count=28`, `docx_count=1`, `excluded_video_count=0`; every record has a SHA256 and byte size.

- [x] **Step 5: Verify GREEN and checkpoint**

Run:

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_new_material_learning.py -q -p no:cacheprovider
git diff --check
git status --short
```

Expected: focused tests pass and no raw input path is staged or tracked.

### Task 3: Authorize, safely probe text quality, and choose DeepSeek versus Kimi

**Files:**
- Modify: `src/mingli_engine/new_material_learning.py`
- Modify: `tests/unit/test_new_material_learning.py`
- Create: `src/mingli_engine/data/new_material_learning/batch_20260714_model_runs.json`
- Create: `src/mingli_engine/data/new_material_learning/batch_20260714_remote_authorizations.json`

- [x] **Step 1: Write failing routing tests**

Cover these deterministic decisions: usable PDF/DOCX text routes to `deepseek_text`; empty or low-density PDF text routes to `kimi_multimodal`; encrypted/corrupt files route to `blocked`; videos cannot appear in routing input.

```python
def test_route_uses_kimi_only_when_text_is_not_reliable():
    assert choose_route(text_chars=5000, nonempty_pages=10, total_pages=12) == "deepseek_text"
    assert choose_route(text_chars=40, nonempty_pages=1, total_pages=20) == "kimi_multimodal"
```

- [x] **Step 2: Implement authorization receipts, capability probes, and routing receipts**

Require one manifest-bound authorization receipt per file and deny remote processing by default; filename markers can only strengthen denial. Open each authorized source no-follow, stream it to a private read-only temporary copy while verifying expected size and SHA256, run `pdftotext`/`pdfinfo` or DOCX `zipfile`/XML parsing only against that copy, and reverify source identity plus inventory afterward. Store only counts, resolved tool identity, route, timestamps, exit status, output artifact hash, and explicit model-call count in model-run receipts.

- [x] **Step 3: Probe all 29 files**

Run:

```powershell
$env:PYTHONPATH='src'
uv run --frozen python -m mingli_engine.new_material_learning probe `
  --manifest 'src\mingli_engine\data\new_material_learning\batch_20260714_manifest.json' `
  --authorizations 'src\mingli_engine\data\new_material_learning\batch_20260714_remote_authorizations.json' `
  --runs 'src\mingli_engine\data\new_material_learning\batch_20260714_model_runs.json'
```

Expected for the current batch: 29 explicit authorization denials and 29 `blocked` routing receipts with durable reasons; zero model calls.

- [x] **Step 4: Verify routing tests and checkpoint**

Run:

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_new_material_learning.py -q -p no:cacheprovider
git diff --check
```

Expected: all routing tests pass.

### Task 4: Create resumable local-model extraction packets

**Files:**
- Modify: `src/mingli_engine/new_material_learning.py`
- Modify: `tests/unit/test_new_material_learning.py`
- Modify: `src/mingli_engine/data/new_material_learning/batch_20260714_model_runs.json`

- [x] **Step 1: Write failing schema tests for model output**

Require each model result to contain `file_sha256`, `source_locator`, `summary`, `learning_points`, `rule_candidates`, `limitations`, `risk_tier`, `model_id`, and `prompt_version`. Reject missing locators, absolute claims, empty limitations, unknown hashes, and outputs not linked to a manifest record.

- [x] **Step 2: Implement immutable packets, stable prompts, and JSON validation**

Bind every immutable packet to the expected file hash, exact route and model, exact locator, prompt version, authorization receipt, and selected/document page bounds. DeepSeek prompts must request concise source-grounded extraction from bounded text chunks. Kimi prompts must request page-aware observations and explicitly distinguish visible text from inference. Both prompts must forbid unsupported certainty and require exact packet locators. Validation rejects blocked routes, mismatched bindings, out-of-range pages, and outputs rejected by the existing safety/high-risk classifiers.

- [x] **Step 3: Apply the authorization gate to DeepSeek text packets**

Run DeepSeek only for explicitly authorized `deepseek_text` receipts. Process bounded chunks, cache each validated JSON response by immutable packet ID, and resume without repeating successful chunks. The current batch has no authorized receipts, so no DeepSeek call is permitted or recorded.

- [x] **Step 4: Apply the authorization gate to Kimi multimodal packets**

Use Kimi only for explicitly authorized `kimi_multimodal` receipts and only on required pages. Cache validated JSON by immutable packet ID. Do not send files routed to DeepSeek through Kimi merely for convenience. The current batch has no authorized receipts, so no Kimi call is permitted or recorded.

- [x] **Step 5: Verify model receipts**

Run:

```powershell
$env:PYTHONPATH='src'
uv run --frozen python -m mingli_engine.new_material_learning validate-runs `
  --manifest 'src\mingli_engine\data\new_material_learning\batch_20260714_manifest.json' `
  --authorizations 'src\mingli_engine\data\new_material_learning\batch_20260714_remote_authorizations.json' `
  --runs 'src\mingli_engine\data\new_material_learning\batch_20260714_model_runs.json'
```

Expected: every attempted packet is `validated`, `blocked`, or `deferred`; no unvalidated model output advances.

### Task 5: Convert validated outputs into learning records

**Files:**
- Modify: `src/mingli_engine/new_material_learning.py`
- Modify: `tests/unit/test_new_material_learning.py`
- Create: `src/mingli_engine/data/new_material_learning/batch_20260714_file_results.json`
- Modify: `src/mingli_engine/data/learning_reference_curation/learning_reference_notes.json`
- Modify: `src/mingli_engine/data/learning_reference_curation/learning_points.json`

- [x] **Step 1: Write failing tests for traceability and terminal states**

Assert that every learning point references a manifest SHA256 and source locator; every file result uses exactly one of `promoted`, `learned_not_promoted`, `duplicate`, `blocked`, or `deferred`; blocked/deferred results require durable reasons.

- [x] **Step 2: Implement conversion with stable IDs**

Generate IDs from `batch_20260714`, a short file hash, and a sequence number. Preserve model outputs as candidates, normalize terminology, and attach limitations and risk tier. Do not change legacy notes.

- [x] **Step 3: Materialize learning notes for all validated packets**

Run:

```powershell
$env:PYTHONPATH='src'
uv run --frozen python -m mingli_engine.new_material_learning build-learning-records `
  --batch batch_20260714
```

Expected: every validated packet produces traceable notes/points; blocked/deferred files produce only disposition records.

- [x] **Step 4: Run learning-reference validation**

Run:

```powershell
$env:PYTHONPATH='src'
uv run --frozen python -c "from mingli_engine.learning_reference_curation import validate_learning_reference_quality; issues=validate_learning_reference_quality(); print(issues); raise SystemExit(bool(issues))"
```

Expected: `[]` and exit 0.

### Task 6: Deduplicate, resolve conflicts, and autonomously promote

**Files:**
- Modify: `src/mingli_engine/data/learning_reference_curation/candidate_intake_decisions.json`
- Modify: `src/mingli_engine/data/source_intake/candidate_extracts.json`
- Modify: `src/mingli_engine/data/source_intake/review_decisions.json`
- Modify: `src/mingli_engine/data/source_intake/promotion_batches.json`
- Modify: `src/mingli_engine/data/classical_sources/evidence_units.json`
- Modify: `src/mingli_engine/data/classical_sources/source_conflicts.json`
- Modify: `tests/unit/test_new_material_learning.py`

- [x] **Step 1: Write failing gate tests**

Test that exact/semantic duplicates become `duplicate`; unresolved contradictions become `learned_not_promoted`; candidates lacking locators, conditions, limitations, or safe language cannot promote; valid candidates create linked 017, 013, and 012 records without mutating legacy records.

- [x] **Step 2: Apply deterministic review rules**

Compare normalized rule family, trigger conditions, conclusion, limitations, and source trace. Preserve conflicting views with school/condition/evidence-strength metadata. Never overwrite an existing rule; reuse or append linked evidence.

- [x] **Step 3: Promote passing candidates in one batch**

Use the existing `apply_candidate_intake_decisions` and source-intake promotion patterns. Create one named promotion batch for `batch_20260714`; set file status to `promoted` only after matching formal evidence is loadable and validated.

- [x] **Step 4: Run source and evidence validators**

Run:

```powershell
$env:PYTHONPATH='src'
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_learning_reference_curation.py `
  tests/unit/test_source_intake.py `
  tests/unit/test_classical_sources.py `
  tests/unit/test_new_material_learning.py `
  -q -p no:cacheprovider
```

Expected: all selected tests pass; otherwise stop further promotion and retain diagnostics.

### Task 7: Make every file administratively terminal and render accounting evidence

**Files:**
- Modify: `src/mingli_engine/new_material_learning.py`
- Modify: `src/mingli_engine/data/new_material_learning/batch_20260714_file_results.json`
- Create: `docs/classical_sources/new_material_20260714_learning.md`
- Modify: `src/mingli_engine/cli.py`
- Modify: `tests/unit/test_new_material_learning.py`

- [x] **Step 1: Write failing completion tests**

Require 29 manifest files, 29 terminal file results, zero video entries, matching SHA256 links, no pending states, and explicit blocker/recovery reasons. Require the report totals to reconcile exactly with the manifest.

- [x] **Step 2: Implement summary, renderer, and CLI commands**

Add `new-material-learning-summary` and `validate-new-material-learning` commands. The report must show file totals, extension counts, authorization and call counts, route counts, terminal-state counts, learning points, duplicate files separately from duplicate terminal states, conflicts, promotions, blocked/deferred reasons, and bound ledger hashes. Administrative terminal accounting must remain distinct from final Task 8 audit status.

- [x] **Step 3: Render and validate the acceptance report**

Run:

```powershell
$env:PYTHONPATH='src'
uv run --frozen mingli-engine validate-new-material-learning --batch batch_20260714
uv run --frozen mingli-engine new-material-learning-summary --batch batch_20260714 `
  | Set-Content -LiteralPath 'docs\classical_sources\new_material_20260714_learning.md' -Encoding utf8
```

Expected: validation exits 0; `terminal_files=29`, `pending_files=0`, `video_learning_files=0`; status totals sum to 29; final audit status remains pending until Task 8 evidence exists.

### Task 8: Run complete regression and final audit

**Files:**
- Verify all files above.
- Create `src/mingli_engine/data/new_material_learning/batch_20260714_task8_command_evidence.json`.
- Create `src/mingli_engine/data/new_material_learning/batch_20260714_final_audit.json`.
- Regenerate `docs/classical_sources/new_material_20260714_learning.md`.

- [x] **Step 1: Rehash the intake and detect source mutation**

Regenerate an in-memory manifest and compare every relative path, byte size, and SHA256 with `batch_20260714_manifest.json`.

Persist the exact source-rehash command, exit code, and 29-file result in the Task 8 command-evidence artifact. Do not read source bodies for any purpose other than this deterministic rehash.

Expected: 29 exact matches and no unexpected non-video file changes.

- [x] **Step 2: Run all tests and quality gates**

Run:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv sync --frozen
uv run --frozen --with pytest==8.4.1 python -m pytest -m "not task8_post_audit" -q -p no:cacheprovider
git diff --check
git status --short --branch
```

Expected: frozen sync succeeds, full suite passes, diff check is clean, and no raw intake file appears in Git status.

Also run focused pytest with `-m "not task8_post_audit"`, focused mypy, and focused Ruff for the new-material-learning source, CLI, and test paths. Use `$env:PYTHONPATH='src'; uv run --frozen python -m mingli_engine.new_material_learning run-task8-regression --batch batch_20260714` as the controlled runner: it records exact command names, exit codes, normalized results, bounded stdout/stderr transcripts and hashes, execution times, branch, the complete `git status --short --branch` snapshot, and identical hashes for every tracked or nonignored untracked repository input immediately before and after regression. Then run `$env:PYTHONPATH='src'; uv run --frozen python -m mingli_engine.new_material_learning finalize-task8-audit --batch batch_20260714`. The final audit must bind the command-evidence SHA-256; the tested implementation/config/test/plan and upstream-ledger hashes; canonical protected legacy knowledge JSON hashes; and the checked Task 8 plan hash. Summary and validation commands dynamically enumerate and rehash the current Git-visible repository inputs, reject raw-file extensions and intake-path markers, and fail when stale. After final-audit and report generation, run `uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_new_material_learning.py -m task8_post_audit -q -p no:cacheprovider`; this post-audit result is not certified by the artifacts it validates.

- [x] **Step 3: Report final disposition**

Report the 29-file reconciliation, model routing counts, promoted/learned/duplicate/blocked/deferred counts, all unresolved conflicts, full-test result, current intake rehash, protected tracked-knowledge preservation, and confirmation that videos remained ignored. Treat the legacy `资料原文` freeze as separately governed unless a live external rehash was performed.

The report must include the final-audit SHA-256. It may claim Task 8 passed only after the strict command evidence, plan state, protected hashes, reviewed-file hashes, upstream ledgers, and source rehash all validate.
