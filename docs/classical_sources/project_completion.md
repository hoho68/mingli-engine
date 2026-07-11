# Project Completion Audit

This document is the final local maintainer handoff for the current project
scope. It composes tracked specification closure, learning/archive closure,
quality validators, formal report acceptance, and report release readiness into
one read-only packet.

## Completion Command

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -m mingli_engine.cli project-completion-summary
```

Current expected packet:

- `baseline_id=project_completion_v1`
- `completion_status=complete_with_guardrails`
- `feature_count=17`
- `spec_count=17`
- `plan_count=17`
- `task_tracked_feature_count=12`
- `legacy_feature_count=5`
- `functional_requirement_count=240`
- `success_criteria_count=122`
- `checked_task_count=1081`
- `unchecked_task_count=0`
- `checklist_file_count=17`
- `checked_checklist_item_count=272`
- `unchecked_checklist_item_count=0`
- `release_id=report_release_v1`
- `release_status=ready_with_guardrails`
- `acceptance_baseline_id=report_acceptance_v1`
- `acceptance_status=ready_with_guardrails`
- `approved_evidence_count=111`
- `rule_family_count=10`
- `action_track_count=4`
- `remaining_local_blockers=0`
- `next_action=local_delivery_complete_wait_for_new_material_or_explicit_remote_request`

The command exits `0` for `complete` or `complete_with_guardrails`. It writes a
blocked JSON packet and exits `4` when a tracked completion check fails. An
unreadable or invalid completion root exits `1` without exposing artifact
content.

## Specification Closure

Features 001-017 all retain specifications, implementation plans, and complete
requirements checklists. Features 006-017 contain task artifacts with every
`T###` task checked.

Features 001-005 predate mandatory task artifacts. They are explicitly
classified as `legacy_implemented_baseline`, not silently counted as missing.
Their specifications, plans, requirement checklists, later regression tests,
and current release gates remain present. Adding or removing task artifacts in
that fixed historical group requires an explicit completion-baseline revision.

## Learning And Archive Closure

The new-material handoff records:

- zero pending new-material sources;
- the local archive commit already created;
- the post-archive state waiting for new material or an explicit push request.

Older `completed_no_new_external_materials_pending_final_archive` lines are
historical checkpoint outputs retained for auditability. They are superseded by
the later local archive receipt and are not current blockers.

## Guarded Completion

`complete_with_guardrails` means the current local product scope is complete,
not that every possible source or future feature is exhausted. The following
remain controlled boundaries:

- the known high-risk scope conflict stays visible and non-deterministic;
- deferred or risk-gated materials remain outside runtime evidence;
- raw materials remain outside report generation;
- remote push and hosting are not performed without an explicit request;
- Web UI, accounts, payments, PDF export, long-term case archives, and other
  divination systems remain future extensions under the constitution.

These boundaries do not block the completed local Bazi knowledge and report
engine.

## Restart Conditions

Resume project work only when one of these occurs:

1. New material is supplied and explicitly enters the controlled intake path.
2. A current completion, quality, acceptance, or release check becomes blocked.
3. The user explicitly requests a remote operation or a future extension.
4. The user requests changes to the current report product itself.

Until then, the local delivery is complete and the repository should remain in
its guarded release state.

## Privacy And Mutation Boundary

The completion command reads tracked specs, checklists, summaries, and current
runtime validators. It does not run Git or network commands, parse raw source
materials, retain personal profile data, generate reports for storage, or
mutate source-library, 013, 012, fixtures, or evidence.
