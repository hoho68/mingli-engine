# Data Model: Source Library Expansion and Evidence Factory

## SourceLibraryEntry

Represents one registered source material that may support future evidence work.

**Fields**:

- `entry_id`: stable id for the source-library entry.
- `material_id`: optional 013 source material id when the source already exists in the intake workflow.
- `title`: human-readable title or best-known label.
- `material_type`: `pdf`, `markdown`, `review_note`, `book_excerpt`, or `other`.
- `local_reference`: filename, folder label, external note label, or other user-verifiable local reference.
- `tracking_status`: `external_untracked`, `project_tracked`, or `derived_note`.
- `readiness_status`: `not_started`, `needs_preparation`, `ready_for_extraction`, `in_extraction`, `review_completed`, `exhausted`, `deferred`, `duplicate`, or `blocked`.
- `topic_tags`: maintainer-facing topic labels.
- `rule_families`: proposed rule families the source may support.
- `source_quality_notes`: concise notes about edition, authority, clarity, or review confidence.
- `rights_notes`: source-handling and quoting limits.
- `risk_tier`: `ordinary`, `sensitive`, or `high_risk`.
- `risk_notes`: reasons for sensitivity or high-risk handling.
- `priority_level`: `critical`, `high`, `medium`, `low`, or `deferred`.
- `next_action`: `prepare_material`, `extract_candidates`, `review_candidates`, `promote_approved`, `revisit_conflict`, `defer`, `block`, or `no_action`.
- `outcome_reason`: required reason for exhausted, deferred, duplicate, or blocked entries.
- `created_at`: registration date.
- `updated_at`: latest review or planning update date.

**Validation Rules**:

- `entry_id` values must be unique.
- `tracking_status=external_untracked` means raw local material must not be moved, deleted, converted, or committed by the workflow.
- A source cannot be `ready_for_extraction` without non-empty `topic_tags`, `rule_families`, `source_quality_notes`, and `rights_notes`.
- `high_risk` entries require non-empty `risk_notes`.
- `exhausted`, `deferred`, `duplicate`, and `blocked` entries require `outcome_reason`.
- `priority_level=critical` or `high` requires a priority assessment.

## SourcePriorityAssessment

Represents the maintainer rationale for processing a source now, later, or not at all.

**Fields**:

- `assessment_id`: stable id.
- `entry_id`: source-library entry being assessed.
- `priority_level`: `critical`, `high`, `medium`, `low`, or `deferred`.
- `expected_value`: `fills_gap`, `clarifies_conflict`, `confirms_existing_rule`, `improves_high_risk_boundary`, `broadens_school_coverage`, or `documents_non_usefulness`.
- `target_gap_ids`: evidence gaps the source may address.
- `target_rule_families`: rule families expected to benefit.
- `source_quality`: `strong`, `moderate`, `weak`, or `needs_recheck`.
- `effort_level`: `low`, `medium`, or `high`.
- `risk_tier`: `ordinary`, `sensitive`, or `high_risk`.
- `rationale`: concise explanation of why this priority is assigned.
- `assessed_by`: maintainer label.
- `assessed_at`: assessment date.

**Validation Rules**:

- Every assessment must reference an existing source-library entry.
- `target_gap_ids` and `target_rule_families` cannot both be empty.
- `source_quality=needs_recheck` cannot produce `critical` priority.
- `high_risk` assessments require a rationale that names the review boundary.
- `deferred` priority requires a rationale explaining what would change the decision.

## CurationBatchPlan

Represents a planned or completed extraction/review batch made from registered sources.

**Fields**:

- `batch_plan_id`: stable id.
- `title`: maintainer-facing batch title.
- `goal`: what the batch is intended to improve or clarify.
- `entry_ids`: source-library entries included in the batch.
- `target_gap_ids`: evidence gaps the batch is expected to address.
- `target_rule_families`: rule families covered by the batch.
- `risk_boundary`: ordinary, sensitive, or high-risk review boundary for the batch.
- `expected_output`: expected outcome such as candidate extracts, conflict notes, gap notes, or non-usefulness documentation.
- `status`: `planned`, `active`, `review_ready`, `completed`, `deferred`, or `blocked`.
- `review_capacity`: optional note about reviewer capacity or batch size.
- `completion_summary`: outcome note after the batch is completed.
- `recommended_next_batch`: optional next focus area after completion.

**Validation Rules**:

- A batch plan must include at least one source-library entry.
- A batch plan must include at least one `target_gap_ids`, `target_rule_families`, or source-quality rationale in `goal`.
- `risk_boundary=high_risk` requires all high-risk entries to have risk notes.
- `completed` batches require `completion_summary`.
- `blocked` or `deferred` batches require `completion_summary` explaining why.
- Planned and active batches must not be counted as formal evidence coverage.

## EvidenceGapTarget

Represents a gap, conflict area, or weak coverage area a source or batch is meant to address.

**Fields**:

- `gap_target_id`: stable id.
- `rule_family`: affected rule family.
- `description`: concise description of the weak, missing, disputed, or risky area.
- `source_entry_ids`: source-library entries that may address it.
- `related_gap_ids`: 012 derived curation gap ids when available.
- `related_conflict_ids`: 012 source conflict ids when available.
- `priority_level`: `critical`, `high`, `medium`, `low`, or `deferred`.
- `blocks_report_use`: whether the gap currently prevents report-ready evidence use.

**Validation Rules**:

- Gap targets must have a description and at least one rule family or related formal gap/conflict id.
- Gap targets that block report use must appear in source-library progress summaries.
- A gap target cannot be marked resolved until linked downstream outcomes exist.

## SourceValueSummary

Computed summary of source or batch contribution after downstream review exists.

**Fields**:

- `subject_id`: source entry id or batch plan id being summarized.
- `subject_type`: `source` or `batch`.
- `candidate_count`: linked 013 candidate count.
- `approved_candidate_count`: linked approved candidate count.
- `rejected_or_blocked_count`: linked rejected or blocked candidate count.
- `conflict_count`: linked conflict count.
- `gap_count`: linked gap count.
- `promoted_evidence_count`: formal evidence count that traces to promoted candidates.
- `value_status`: `not_started`, `in_progress`, `value_produced`, `non_useful_documented`, `deferred`, or `blocked`.
- `recommended_next_action`: next maintainer action.

**Validation Rules**:

- Value summaries are computed from current source-library, 013 source-intake, and 012 formal evidence data.
- Registered sources with no downstream records are `not_started` or `in_progress`, not value-producing.
- Unapproved candidates never count as formal evidence contribution.
- Rejected, blocked, duplicate, exhausted, and deferred outcomes remain visible with reasons.

## State Transitions

Source-library readiness:

```text
not_started -> needs_preparation -> ready_for_extraction -> in_extraction -> review_completed
       |              |                    |                    |
       v              v                    v                    v
    deferred       blocked              duplicate            exhausted
```

Batch planning:

```text
planned -> active -> review_ready -> completed
   |         |           |
   v         v           v
deferred  blocked     blocked
```

Value status:

```text
not_started -> in_progress -> value_produced
       |            |
       v            v
    deferred   non_useful_documented
       |
       v
    blocked
```
