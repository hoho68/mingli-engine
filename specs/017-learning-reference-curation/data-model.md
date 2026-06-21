# Data Model: Learning Reference Curation

## LearningReferenceNote

Represents one maintainer-readable study note created from a ready 016 extraction task.

**Fields**:

- `note_id`: stable id for the note.
- `task_id`: originating 016 extraction task.
- `package_id`: owning 016 package.
- `queue_item_id`: originating 015 queue item.
- `audit_id`: originating 015 audit record.
- `source_library_entry_id`: linked 014 source-library entry.
- `source_material_id`: linked 013 source material.
- `source_title`: maintainer-facing title.
- `target_rule_families`: intended rule families.
- `locator_requirement`: required source locator precision.
- `risk_boundary`: `ordinary`, `sensitive`, or `high_risk`.
- `rights_note`: quotation and source-handling boundary.
- `source_quality_note`: concise source-quality note.
- `learning_points`: ordered learning point ids.
- `overlap_candidate_ids`: existing 013 candidate ids related to the note.
- `status`: `draft`, `ready_for_candidate_intake`, `candidate_intake_started`, `deferred`, or `blocked`.
- `created_at`: note creation date.
- `updated_at`: latest note update date.

**Validation Rules**:

- Every note must reference an existing 016 task and package.
- Every note must preserve 015/014/013 trace ids from the task.
- Notes must have at least one learning point before becoming candidate-intake ready.
- Notes must not include copied source passages or formal evidence wording.

## LearningPoint

Represents one concise study item within a learning reference note.

**Fields**:

- `learning_point_id`: stable id.
- `note_id`: owning learning reference note.
- `point_label`: maintainer-facing label.
- `source_locator`: locator or locator requirement.
- `summary`: concise source-backed learning summary.
- `proposed_rule_family`: intended rule family.
- `risk_tier`: `ordinary`, `sensitive`, or `high_risk`.
- `limitations`: uncertainty and scope limitations.
- `candidate_readiness`: `ready`, `needs_locator`, `needs_risk_review`, `duplicate_review`, `deferred`, or `blocked`.
- `candidate_decision_id`: linked decision when available.

**Validation Rules**:

- Every learning point must reference an existing note.
- Every point must have source locator or a locator requirement.
- Every point must have a supported rule family and risk tier.
- Sensitive and high-risk points require uncertainty and limitation wording.
- Learning point summaries must be concise and must not copy long source passages.

## CandidateIntakeDecision

Represents the maintainer decision for whether a learning point should create or reuse a 013 candidate.

**Fields**:

- `decision_id`: stable id.
- `learning_point_id`: originating learning point.
- `decision`: `create_candidate`, `reuse_existing`, `avoid_duplicate`, `defer`, `manual_review`.
- `source_material_id`: target 013 source material.
- `candidate_id`: candidate id to create or existing candidate id to reuse/avoid.
- `overlap_candidate_ids`: existing candidates considered.
- `rationale`: concise decision reason.
- `status`: `planned`, `applied`, `deferred`, or `blocked`.
- `created_at`: decision creation date.
- `updated_at`: latest decision update date.

**Validation Rules**:

- Every decision must reference an existing learning point.
- `create_candidate` decisions require candidate-ready locator, rule family, risk tier, summary, and limitations.
- Reuse and duplicate-avoidance decisions require overlap candidate ids.
- Applied decisions must not create formal report evidence.

## PrerequisiteActionNote

Represents non-ready 016 backlog work as prerequisite action, not learning reference data.

**Fields**:

- `action_note_id`: stable id.
- `backlog_id`: originating 016 prerequisite backlog record.
- `package_id`: owning 016 package.
- `queue_item_id`: originating 015 queue item.
- `audit_id`: originating 015 audit record.
- `action_type`: `registration`, `preparation`, `locator_review`, `risk_review`, `deferred`, or `blocked`.
- `missing_prerequisites`: missing requirements before extraction.
- `durable_reason`: reason the item is not candidate-ready.
- `recommended_action`: next maintainer action.
- `risk_boundary`: `ordinary`, `sensitive`, or `high_risk`.
- `status`: `planned`, `active`, `completed`, `deferred`, or `blocked`.
- `created_at`: action-note creation date.
- `updated_at`: latest action-note update date.

**Validation Rules**:

- Every action note must reference an existing 016 backlog record.
- Action notes are not learning points, candidates, review decisions, promotion batches, or formal evidence.
- Risk-review, blocked, and deferred action notes cannot create candidate-intake decisions.

## LearningReferenceProgressSummary

Computed maintainer-facing summary of learning-reference readiness.

**Fields**:

- `note_counts`: count by note status.
- `learning_point_counts`: count by candidate readiness.
- `decision_counts`: count by decision and status.
- `prerequisite_action_counts`: count by action type and status.
- `risk_tier_counts`: count by risk tier.
- `overlap_warning_count`: count of existing 013 overlaps.
- `candidate_ready_count`: learning points ready for candidate creation.
- `candidate_decision_count`: total candidate-intake decisions.
- `formal_evidence_delta`: expected to remain zero.
- `next_action_ids`: ordered note, decision, or prerequisite action ids.

**Validation Rules**:

- Summaries are computed from 017 records and upstream 016/013 metadata.
- Counts must separate learning references from 013 candidate extracts and 012 formal evidence.
- `formal_evidence_delta` must be zero.

## State Transitions

Learning reference note:

```text
draft -> ready_for_candidate_intake -> candidate_intake_started
   |                |
   v                v
deferred         blocked
```

Learning point:

```text
needs_locator -> ready -> duplicate_review
      |           |           |
      v           v           v
   deferred    blocked    manual_review
```

Candidate intake decision:

```text
planned -> applied
   |         |
   v         v
deferred  blocked
```

Prerequisite action note:

```text
planned -> active -> completed
   |         |
   v         v
deferred  blocked
```
