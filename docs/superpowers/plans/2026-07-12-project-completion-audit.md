# Project Completion Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single machine-readable local completion gate across specs, tasks, checklists, learning closure, quality validation, and report release.

**Architecture:** `project_completion.py` parses tracked project artifacts and composes existing quality validators plus `report_release_v1`. New frozen dataclasses expose only aggregate and stable feature status. `cli.py` serializes the packet without running Git, network, tests, raw-material readers, or mutations.

**Tech Stack:** Python 3.12+, pathlib, re, frozen dataclasses, existing quality/release services, argparse CLI, and pytest.

---

### Task 1: Lock Artifact And Closure Facts

**Files:**
- Create: `tests/unit/test_project_completion.py`
- Modify: `src/mingli_engine/models.py`

- [ ] Add failing expectations for 17 specs/plans, 12 task-tracked features, five legacy features, 240 functional requirements, 122 success criteria, 1,081 checked tasks, zero unchecked tasks, 17 complete checklists, and 272 checked checklist items.
- [ ] Add fixtures that remove a plan, uncheck a task, and uncheck a checklist item; each must produce a blocked packet with stable blocker codes.
- [ ] Define feature-result and completion-summary dataclasses.

### Task 2: Compose Runtime Completion Gates

**Files:**
- Create: `src/mingli_engine/project_completion.py`
- Modify: `tests/unit/test_project_completion.py`

- [ ] Parse only stable feature ids 001-017 and classify 001-005 as legacy baselines.
- [ ] Check learning handoff markers for zero pending sources, local archive creation, and wait-for-new-material/remote-request status.
- [ ] Run curation, materials, and learning-reference quality validators.
- [ ] Consume `build_report_release_summary()` and fail closed on a blocked release or acceptance state.
- [ ] Return `complete_with_guardrails` only when all checks pass and no local blocker remains.

### Task 3: Add CLI And Privacy Contract

**Files:**
- Modify: `src/mingli_engine/cli.py`
- Create: `tests/contract/test_project_completion_cli_contract.py`

- [ ] Add `project-completion-summary` for the fixed repository root.
- [ ] Return exit `4` for a blocked packet and `1` for invalid completion artifacts.
- [ ] Verify the JSON contains no birth data, report body, raw material path, source text, or remote information.

### Task 4: Publish Final Maintainer Handoff

**Files:**
- Create: `docs/classical_sources/project_completion.md`
- Modify: `docs/classical_sources/README.md`
- Modify: `docs/classical_sources/coverage.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`

- [ ] Document the final command, counts, guarded state, historical archive interpretation, controlled boundaries, and future restart conditions.
- [ ] Add a current completion note without rewriting historical checkpoint records.

### Task 5: Verify And Commit

- [ ] Run completion, release, acceptance, report, CLI, renderer, and safety tests.
- [ ] Run all three quality scans.
- [ ] Run the full repository regression.
- [ ] Independently review completion logic and privacy boundaries.
- [ ] Run `git diff --check`, verify no source-library/013/012/raw mutation, and commit.
