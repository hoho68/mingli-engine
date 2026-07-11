# Project Completion Audit Design

## Goal

Add one deterministic, read-only completion packet that answers whether the local project is fully deliverable across specifications, task closure, quality gates, learning closure, formal evidence activation, report acceptance, and report release.

## Audit Findings Driving The Design

- All 17 feature directories contain `spec.md` and `plan.md`.
- Features 006-017 contain 1,081 checked tasks and zero unchecked tasks.
- Features 001-005 are historical implemented baselines created before task artifacts became mandatory; their requirements checklists are complete and their behavior remains covered by later regression and release gates.
- All 17 requirement checklists contain 272 checked items and zero unchecked items.
- The specifications contain 240 functional requirements and 122 measurable success criteria.
- Learning handoff records show zero pending new-material sources, a local archive commit, and a waiting state for new material or an explicit remote request. Earlier `pending_final_archive` text is a historical checkpoint, not a current blocker.
- Evidence quality, materials quality, learning-reference quality, report acceptance, and report release already have separate health checks, but there is no aggregate completion entrypoint.

## Chosen Approach

Create `project_completion.py` above the existing validators and `report_release_v1`. It reads only tracked specification and documentation artifacts, computes task/checklist closure, runs the three quality validators, consumes the current release packet, and returns a privacy-safe `ProjectCompletionSummary`.

The service does not run Git, tests, network calls, raw-material readers, or mutation workflows. Test execution remains an external verification step; the completion packet certifies live tracked state and runtime gates.

## Fixed Local Completion Baseline

The v1 audit requires the exact feature ids `001` through `017` and classifies them as:

- legacy implemented baseline: 001-005, where no `tasks.md` exists by historical design;
- task-tracked completed features: 006-017, where every `T###` task is checked.

Every feature must have `spec.md`, `plan.md`, and a complete requirements checklist. The audit reports requirement, success-criterion, task, and checklist counts without copying artifact content.

## Runtime Completion Gates

The summary fails closed unless all of these pass:

- specification artifact baseline;
- requirement and success-criterion inventory;
- task closure and legacy classification;
- checklist closure;
- learning/archive handoff markers;
- documentation navigation and release guidance;
- evidence-curation, materials-audit, and learning-reference quality;
- `report_release_v1`, including its `report_acceptance_v1` dependency.

A passing project inherits `complete_with_guardrails` while the known high-risk scope conflict remains visible. Controlled blocked/deferred material records, future extensions, absence of new materials, and no remote push are boundaries rather than local delivery blockers.

## Public Packet

The summary exposes aggregate counts, one artifact result per stable feature id, named check statuses, release/acceptance state, evidence/rule/action counts, controlled boundaries, remaining local blockers, and a next action. It does not expose personal birth data, report bodies, raw material paths, fixture paths, Git remote data, or source text.

The CLI command is `project-completion-summary`. It exits `0` for `complete` or `complete_with_guardrails`, `4` for a blocked packet, and `1` for an unreadable or invalid completion baseline.

## Boundaries

- No network or remote Git operation.
- No raw PDF/Markdown/text parsing.
- No source-library, 013, or 012 mutation.
- No automatic promotion, candidate review, or conflict resolution.
- No claim that future extensions such as Web UI, accounts, payments, PDF export, or other divination systems are part of the completed local scope.

## Verification

Tests cover exact feature classification, counts, missing artifacts, unchecked tasks/checklists, historical archive interpretation, quality failure propagation, release failure propagation, privacy-safe serialization, CLI exit behavior, documentation markers, quality scans, and the full repository regression.
