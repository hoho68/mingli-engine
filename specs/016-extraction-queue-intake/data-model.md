# Data Model: Extraction Queue Intake Package

## ExtractionWorkPackage

Represents one maintainer-facing package generated from a 015 materials-audit queue snapshot.

**Fields**:

- `package_id`: stable id for the work package.
- `package_label`: maintainer-facing label.
- `source_queue_snapshot_ids`: ordered 015 queue item ids considered by the package.
- `selected_task_ids`: extraction task ids included in the package.
- `backlog_record_ids`: prerequisite backlog record ids preserved by the package.
- `status`: `planned`, `active`, `completed`, `deferred`, or `blocked`.
- `created_at`: package creation date.
- `updated_at`: latest package update date.
- `notes`: concise package note.

**Validation Rules**:

- `package_id` values must be unique.
- Every selected task and backlog record must reference the package.
- Every source queue id must reference a current 015 queue item.
- Completed packages require at least one selected task or a durable no-work reason.

## ExtractionTask

Represents a planned manual extraction task created from an eligible 015 queue item.

**Fields**:

- `task_id`: stable id.
- `package_id`: owning work package.
- `queue_item_id`: originating 015 queue item.
- `audit_id`: originating 015 audit record.
- `source_library_entry_id`: matched 014 source-library entry when available.
- `intended_source_material_id`: intended 013 source material id when available.
- `priority_level`: `critical`, `high`, `medium`, or `low`.
- `priority_rationale`: why the task is in the package.
- `target_rule_families`: rule families expected to benefit.
- `target_gap_ids`: evidence or coverage gaps the task may address.
- `risk_boundary`: `ordinary`, `sensitive`, or `high_risk`.
- `locator_requirement`: required locator precision before manual extraction.
- `source_quality_note`: concise quality note.
- `rights_note`: source handling and quotation limits.
- `pre_extraction_checks`: checks required before extraction begins.
- `overlap_warnings`: duplicate or overlap warnings against 013 candidates.
- `status`: `planned`, `active`, `completed`, `deferred`, or `blocked`.
- `created_at`: task creation date.
- `updated_at`: latest task update date.

**Validation Rules**:

- Every extraction task must reference an existing package and 015 queue item.
- Originating queue items must be `extraction_ready`.
- The audit record, readiness finding, and alignment finding must still support extraction readiness.
- Tasks require target rule family or gap, locator requirement, source-quality note, rights note, risk boundary, and pre-extraction checks.
- High-risk tasks require explicit risk-review completion or must be blocked/deferred.
- Tasks are planning metadata and must not include copied source passages or extracted meanings.

## CandidateDraftSlot

Represents a placeholder for a future manually created 013 candidate extract.

**Fields**:

- `draft_slot_id`: stable id.
- `task_id`: owning extraction task.
- `intended_candidate_label`: maintainer-facing label for the future candidate.
- `target_rule_family`: intended rule family.
- `target_gap_id`: optional target gap id.
- `locator_requirement`: locator precision required before extraction.
- `expected_review_notes`: review notes that must be captured later.
- `risk_boundary`: `ordinary`, `sensitive`, or `high_risk`.
- `safety_requirements`: required uncertainty, limitation, or refusal notes.
- `status`: `planned`, `ready_for_manual_extraction`, `deferred`, or `blocked`.

**Validation Rules**:

- Every draft slot must reference an existing extraction task.
- Draft slots must not include source passages, extracted meanings, review decisions, approval status, or promotion status.
- High-risk draft slots require safety requirements.
- Ready slots require locator requirement and pre-extraction checks from the parent task.

## PrerequisiteBacklogRecord

Represents a package item that cannot become a routine extraction task yet.

**Fields**:

- `backlog_id`: stable id.
- `package_id`: owning work package.
- `queue_item_id`: originating 015 queue item.
- `audit_id`: originating 015 audit record.
- `backlog_type`: `registration`, `preparation`, `locator_review`, `risk_review`, `deferred`, or `blocked`.
- `missing_prerequisites`: missing requirements before extraction.
- `durable_reason`: reason the item is not extraction-ready.
- `recommended_action`: next maintainer action.
- `risk_boundary`: `ordinary`, `sensitive`, or `high_risk`.
- `status`: `planned`, `active`, `completed`, `deferred`, or `blocked`.
- `created_at`: backlog creation date.
- `updated_at`: latest backlog update date.

**Validation Rules**:

- Every backlog record must reference an existing package and 015 queue item.
- Non-extraction queue items must have missing prerequisites or durable reasons.
- Risk-review backlog records cannot be scheduled as routine extraction tasks.
- Blocked and deferred records require durable reasons.

## PackageProgressSummary

Computed maintainer-facing summary of package readiness.

**Fields**:

- `package_counts`: count by package status.
- `task_counts`: count by extraction task status.
- `draft_slot_counts`: count by draft slot status.
- `backlog_counts`: count by backlog type and status.
- `risk_boundary_counts`: count by risk boundary.
- `overlap_warning_count`: count of duplicate or overlap warnings.
- `extraction_task_count`: total extraction tasks.
- `candidate_draft_slot_count`: total draft slots.
- `blocked_or_deferred_count`: total blocked or deferred package items.
- `next_manual_action_ids`: ordered next extraction or prerequisite action ids.

**Validation Rules**:

- Summaries are computed from package records, tasks, draft slots, and backlog records.
- Counts must separate extraction tasks from candidate draft slots, prerequisite backlogs, 013 candidate extracts, and formal evidence.
- Package progress summaries must never include package records in formal evidence counts.

## State Transitions

Package:

```text
planned -> active -> completed
   |         |
   v         v
deferred  blocked
```

Extraction task:

```text
planned -> active -> completed
   |         |
   v         v
deferred  blocked
```

Draft slot:

```text
planned -> ready_for_manual_extraction
   |                 |
   v                 v
deferred          blocked
```

Backlog:

```text
planned -> active -> completed
   |         |
   v         v
deferred  blocked
```
