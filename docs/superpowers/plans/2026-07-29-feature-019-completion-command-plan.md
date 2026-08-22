# Feature 019 Completion Command Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to execute this command plan. Each implementation package follows the exact task text in `docs/superpowers/plans/2026-07-19-feature-019-source-grounded-hard-gates.md` and the approved Feature 019 governance/quality amendments. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Feature 019 from the current two-worktree state, produce honest source-grounded installed-wheel evidence, close formal governance only after every hard gate and required owner checkpoint passes, and preserve unrelated Feature 020 work without folding it into the Feature 019 release boundary.

**Architecture:** Use `codex/019-closure-release` in `E:\mingli-019-closure` as the sole integration branch. Finish the independent `codex/019-evidence-trust-closure` task, fast-forward it into the integration branch, then execute the remaining source-grounded hard-gate tasks sequentially. Kimi K3 performs implementation and mechanical verification; the Codex controller performs scope control, specification review, code-quality review, integration, and final completion judgment.

**Tech Stack:** Python 3.12+, pytest 8.4.1, mypy 1.17.1, Ruff 0.12.11, `uv --frozen`, setuptools wheel builds, canonical JSON/SHA-256 governance artifacts, Git worktrees, Kimi CLI model `kimi-code/k3`.

---

## Authority Order

When instructions differ, use this precedence:

1. `specs/_drafts/019-bazi-domain-validation-and-application-v1/quality-gate-amendment.md`
2. `specs/_drafts/019-bazi-domain-validation-and-application-v1/governance-amendment-plan.md`
3. `docs/superpowers/plans/2026-07-19-feature-019-source-grounded-hard-gates.md`
4. `specs/_drafts/019-bazi-domain-validation-and-application-v1/tasks.md`
5. `docs/superpowers/plans/2026-07-15-bazi-domain-validation-and-application-v1-closure-plan.md`, excluding every step marked superseded or `DO NOT EXECUTE`

The old fixed `0.2.0` final-baseline workflow is historical planning text. Do not create `calibration_baseline.json`, do not force a version bump, and do not claim `ready` or `released` without current installed evidence and the required owner-bound approval artifacts.

## Workspace Boundaries

- Integration worktree: `E:\mingli-019-closure`
- Integration branch: `codex/019-closure-release`
- Evidence implementation worktree: `E:\命理演绎\.superpowers\worktrees\019-evidence-trust-closure`
- Evidence implementation branch: `codex/019-evidence-trust-closure`
- Protected owner workspace: `E:\命理演绎`
- Protected owner branch: `codex/019-bazi-domain-validation-application`

The owner workspace contains unfinished Feature 020 files and must not be cleaned, reset, staged, committed, or used as Feature 019 release evidence. Build directories and Python cache directories are disposable outputs, but deletion must target only explicitly verified cache/build paths in the active worktree.

## Kimi Delegation Contract

Every implementation task is assigned to Kimi CLI using model `kimi-code/k3`.

The controller supplies:

- the exact task number and full task text;
- the active worktree and allowed file list;
- current failing/passing test evidence;
- protected files and forbidden actions;
- the expected commit message;
- required final response fields: status, files changed, tests run, commit SHA, remaining issues, and quota state.

Kimi must:

- follow red-green-refactor for new behavior or bug fixes;
- preserve unrelated dirty files;
- never reset, stash, rebase, force-push, or rewrite imported governance artifacts;
- never self-approve an owner checkpoint;
- never weaken tests, mypy/Ruff rules, hashes, privacy checks, or release gates;
- exclude `build/`, `.pytest_cache`, `__pycache__`, and temporary evidence from commits unless the authoritative task explicitly requires a tracked artifact;
- report `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`;
- explicitly report whether quota, rate limit, context limit, or model availability prevented completion.

The controller does not ask the owner for routine Kimi execution permission. It retries transient CLI, encoding, logging, and session failures automatically. It asks the owner only when Kimi reports persistent model/quota unavailability or when an authoritative governance task requires a non-delegable owner approval.

## Review Contract

After every Kimi implementation commit:

1. **Specification review:** compare the diff to the exact task, amendments, immutable boundaries, and expected artifacts.
2. **Quality review:** inspect production/test design, failure behavior, privacy, deterministic serialization, hash binding, type/lint deltas, and unrelated scope.
3. **Fresh verification:** run the focused commands independently from the controller.
4. If either review fails, resume the same Kimi session with exact findings and require a fix plus re-verification.
5. Advance only after both reviews pass with no Critical or Important finding.

## Task 0: Freeze The Current Inventory

**Files:** read-only across both worktrees.

- [x] **Step 1:** Confirm Kimi CLI model mapping.

```powershell
Get-Content C:\Users\lei\.kimi\config.toml |
  Select-String 'default_model|provider|model'
```

Expected: default model includes `kimi-code/k3`.

- [x] **Step 2:** Audit `codex/019-closure-release`.

Expected evidence:

- release-gate and governance-amendment Tasks 1-7 are committed;
- package version remains `0.1.0`;
- historical `calibration_baseline.json` remains absent;
- formal Spec Kit closure is not done;
- `materials_audit` hermeticity work is the only active implementation delta apart from build output.

- [x] **Step 3:** Audit `codex/019-evidence-trust-closure`.

Expected evidence:

- branch is a strict linear descendant of `codex/019-closure-release`;
- committed source-grounded audit model/resource work is integration-ready;
- source-grounded Task 6 implementation and tests are complete but uncommitted;
- focused capture tests, mypy, and Ruff pass;
- no file overlap exists with the integration worktree's `materials_audit` delta.

## Task 1: Finish Materials-Audit Hermeticity

**Worktree:** `E:\mingli-019-closure`

**Files:**

- Modify: `pyproject.toml`
- Modify: `src/mingli_engine/materials_audit.py`
- Modify: `tests/unit/test_materials_audit.py`
- Create: `tests/integration/test_materials_audit_external.py`
- Never stage: `build/`

- [ ] **Step 1:** Review the existing diff and prove it only removes implicit external-root dependence, requires explicit `workspace_root`, synthesizes unit fixtures, and marks real external-material tests with `external_materials`.

- [ ] **Step 2:** Run the already-green unit batch.

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_materials_audit.py -q -p no:cacheprovider
```

Expected: 151 tests pass.

- [ ] **Step 3:** Run focused type and lint verification.

```powershell
uv run --frozen --with mypy==1.17.1 python -m mypy src/mingli_engine/materials_audit.py --follow-imports=skip --show-error-codes --no-color-output --no-pretty
uv run --frozen --with ruff==0.12.11 ruff check src/mingli_engine/materials_audit.py tests/unit/test_materials_audit.py tests/integration/test_materials_audit_external.py pyproject.toml
```

Expected: no new Feature 019 candidate error, no changed-line finding, and no Ruff finding in modified files.

- [ ] **Step 4:** Run the external test in its default skipped mode and, when `MINGLI_EXTERNAL_MATERIAL_ROOT` is absent, prove no accidental host path is read.

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest tests/integration/test_materials_audit_external.py -q -p no:cacheprovider
```

Expected: controlled skip or pass according to the marker contract.

- [ ] **Step 5:** Commit only the four intended files.

```powershell
git add pyproject.toml src/mingli_engine/materials_audit.py tests/unit/test_materials_audit.py tests/integration/test_materials_audit_external.py
git commit -m "test: isolate external materials audit"
```

## Task 2: Finish Source-Grounded Capture Task 6

**Worktree:** `E:\命理演绎\.superpowers\worktrees\019-evidence-trust-closure`

**Files:**

- Create: `src/mingli_engine/application_source_grounded_capture.py`
- Create: `tests/unit/test_application_source_grounded_capture.py`
- Create: `tests/integration/test_application_source_grounded_capture.py`
- Modify: `tests/unit/source_grounded_v2_fixtures.py`
- Modify: `tests/integration/test_real_use_reports.py`

- [ ] **Step 1:** Verify the five-file diff matches Task 6, captures four sibling responses from actual output only, imports no audit authority into runtime capture, and preserves renderer refusal behavior.

- [ ] **Step 2:** Run the unit and integration capture files separately or with importlib mode so duplicate basenames cannot resolve through stale bytecode.

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_application_source_grounded_capture.py -q -p no:cacheprovider
uv run --frozen --with pytest==8.4.1 python -m pytest tests/integration/test_application_source_grounded_capture.py -q -p no:cacheprovider
uv run --frozen --with pytest==8.4.1 python -m pytest tests/integration/test_real_use_reports.py -q -p no:cacheprovider
```

Expected: 14, 3, and 14 tests pass respectively.

- [ ] **Step 3:** Run focused mypy and Ruff.

```powershell
uv run --frozen --with mypy==1.17.1 python -m mypy src/mingli_engine/application_source_grounded_capture.py --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check src/mingli_engine/application_source_grounded_capture.py tests/unit/test_application_source_grounded_capture.py tests/integration/test_application_source_grounded_capture.py tests/unit/source_grounded_v2_fixtures.py tests/integration/test_real_use_reports.py
```

Expected: no findings.

- [ ] **Step 4:** Commit Task 6.

```powershell
git add src/mingli_engine/application_source_grounded_capture.py tests/unit/test_application_source_grounded_capture.py tests/integration/test_application_source_grounded_capture.py tests/unit/source_grounded_v2_fixtures.py tests/integration/test_real_use_reports.py
git commit -m "feat: capture installed audit responses"
```

## Task 3: Integrate The Evidence Branch

**Worktree:** `E:\mingli-019-closure`

- [ ] **Step 1:** Require both worktrees to have no uncommitted source/test delta. Build/cache output may remain untracked but must not be staged. Record the merge base and both branch tips.

```powershell
git status --short --branch
git merge-base codex/019-closure-release codex/019-evidence-trust-closure
git rev-parse codex/019-closure-release
```

Expected: both branch tips descend from the recorded merge base. If the integration
branch advanced through reviewed commits after the inventory audit, preserve both
histories with a merge commit; never cherry-pick or rebase the frozen evidence
history.

- [ ] **Step 2:** Integrate without rewriting either branch.

```powershell
git merge --no-ff codex/019-evidence-trust-closure -m "merge: integrate source-grounded evidence closure"
```

Expected: no content conflict because the reviewed deltas have disjoint paths;
the original evidence commit hashes remain ancestors of the merge result.

- [ ] **Step 3:** Re-run Task 1 and Task 2 focused tests from the integrated worktree.

- [ ] **Step 4:** Run quality capture and comparison.

```powershell
uv run --frozen --with mypy==1.17.1 --with ruff==0.12.11 python scripts/compare_quality_baseline.py capture --output build/feature019-current-quality.json
uv run --frozen python scripts/compare_quality_baseline.py compare --baseline specs/_drafts/019-bazi-domain-validation-and-application-v1/quality-baseline.json --current build/feature019-current-quality.json
```

Expected: the comparison accepts only frozen debt, reports no new/changed-line error, and binds the result to the live HEAD and repository state.

## Task 4: Execute Source-Grounded Tasks 7-10

**Worktree:** `E:\mingli-019-closure`

Kimi receives the complete authoritative text for one task at a time from `docs/superpowers/plans/2026-07-19-feature-019-source-grounded-hard-gates.md`.

- [ ] **Task 7:** Project complete JSON and rendered surfaces.
- [ ] **Task 8:** Freeze and reconstruct pure actual evidence.
- [ ] **Task 9:** Build post-freeze relational authority audit.
- [ ] **Task 10:** Produce the four V2 gates from one audit.

For every task:

```powershell
git status --short --branch
git diff --check
```

Then run every exact RED/GREEN/focused test, mypy, and Ruff command named in that task. Commit with the exact commit message specified by the authoritative task. Do not start the next task until controller specification and quality review both pass.

Acceptance:

- `source_rule_tracing`, `unsupported_inference`, `school_conflict`, and `abstention` are derived from one independently reconstructed audit;
- runtime actual capture has no authority import path;
- gates cannot self-certify, trust embedded expected data, or use Feature 020 benchmark output;
- historical V1 and Stage 1 bytes/hashes remain unchanged.

## Task 5: Execute Source-Grounded Task 11

**Worktree:** `E:\mingli-019-closure`

- [ ] Implement contextual V2 replay without changing historical V1.
- [ ] Complete all Task 11 pre-freeze source, test, script, packaged-document, and authority-bundle tooling.
- [ ] Run the full pre-freeze verification set required by Task 11.
- [ ] Re-run the quality comparator.
- [ ] Commit only the exact Task 11 files and require a clean scoped worktree.

Acceptance:

- trusted bundle and approval anchors are external inputs, never trusted from an embedded copy;
- approval is still absent;
- no release-facing installed audit has run;
- any later source/test/package correction is known to invalidate the future frozen candidate.

## Task 6: Build And Independently Review The Task 12 Candidate

**Worktree:** `E:\mingli-019-closure`

- [ ] Build the exact candidate wheel from the clean Task 11 commit.
- [ ] Freeze `authority_bundle.json` and `authority_freeze_packet.md`.
- [ ] Prove neither bundle nor approval sidecars are wheel resources.
- [ ] Commit the exact Task 12 bundle/packet bytes.
- [ ] Run an independent review of the candidate wheel, request manifest, resource indexes, claim/limitation/abstention policy, and bundle digest.

Hard stop:

- Do not create `authority_approval.json` until the authoritative Task 12/13 checkpoint verifies the committed bytes and the project owner approves that exact bundle and review packet.
- Any byte change returns execution to Task 11 and rebuilds Task 12.

## Task 7: Record The Owner-Bound Task 13 Approval

This task is intentionally non-delegable.

- [ ] Run `scripts/verify_source_grounded_authority_checkpoint.py preapproval` with the exact committed Task 12 wheel, bundle, packet, and owner-confirmation sidecar.
- [ ] Create `authority_approval.json` only through the verified capability returned by the script.
- [ ] Commit only the approval sidecar.
- [ ] Run the postapproval verifier against the approval commit and write the untracked checkpoint under `build/source-grounded-evidence/`.

Acceptance: approval binds the exact wheel, bundle, packet, claim boundary, limitations, abstention policy, owner identity, and independent-review status. No AI worker may fabricate or silently infer these owner fields.

## Task 8: Execute Source-Grounded Tasks 14-16

**Worktree:** `E:\mingli-019-closure`

- [ ] **Task 14:** Build dual fresh-install V2 evidence from the approved candidate bytes.
- [ ] **Task 15:** Delete installs and replay version-exactly from immutable evidence.
- [ ] **Task 16:** Update only the six postapproval-safe documentation files and run final technical verification.

Hard rules:

- any candidate-wheel, packaged-resource, request, policy, inventory, renderer, projection-version, or packaged-Python change invalidates Task 13 approval and restarts Tasks 11-13;
- installed/host/dual-run/deleted-install evidence must agree exactly;
- all four V2 gates must report honest source-grounded results;
- no task may infer an internal release status beyond the governance state machine.

## Task 9: Perform Task 17 Formal Governance Closure

Run only after the authoritative Task 17 authorization gate passes.

- [ ] Write and verify formal closure tests.
- [ ] Move the complete Spec Kit atomically to `specs/019-bazi-domain-validation-and-application-v1/`.
- [ ] Update `.specify/feature.json`.
- [ ] Update project-completion counts, navigation, and formal completion documentation.
- [ ] Preserve all external sidecar bytes and approval anchors exactly.
- [ ] Mark only genuinely completed task/checklist items complete; superseded historical tasks remain explicitly superseded rather than falsely executed.
- [ ] Commit formal closure using the authoritative commit message.

## Task 10: Final Verification And Independent Review

- [ ] Run the full repository pytest suite with a 900000 ms controller timeout.

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests -q -p no:cacheprovider
```

- [ ] Run the frozen quality comparator and confirm no new or changed-line findings.
- [ ] Run the five release-summary commands and persist their canonical outputs under the task-authorized temporary directory.
- [ ] Run privacy/no-retention, wheel manifest, installed-source isolation, hash-integrity, persistence, and `git diff --check` audits.
- [ ] Run a fresh whole-feature specification review.
- [ ] Run a separate code-quality/security/privacy review.
- [ ] Return every Critical or Important finding to Kimi for correction, then repeat all affected verification.
- [ ] Confirm the final worktree is clean apart from explicitly allowed ignored/untracked build evidence.

Completion requires:

- zero failing tests;
- no Feature 019 candidate mypy/Ruff errors and no changed-line finding;
- all hard gates evaluated from real source evidence;
- exact installed evidence and replay equality;
- all mandatory owner approvals bound to exact immutable bytes;
- no Critical or Important review finding;
- formal 019 path present and draft path absent;
- project completion reports the exact authorized state without rewriting historical calibration evidence.

## Task 11: Integrate Without Losing Feature 020 Work

After Feature 019 completion is independently verified:

- [ ] Record the final Feature 019 commit range and hashes.
- [ ] Inspect the protected owner workspace dirty files again.
- [ ] Integrate the completed Feature 019 branch using a non-destructive merge strategy that preserves all owner Feature 020 files.
- [ ] Resolve overlaps only after exact diff review; never discard the owner workspace's uncommitted data.
- [ ] Re-run the full verification from the integrated owner branch.

The command plan is complete only when both the isolated Feature 019 branch and the integrated owner branch satisfy their applicable verification gates.
