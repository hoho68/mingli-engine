# Data Model: Source Extraction Workflow

## SourceMaterial

Represents an external source input that may produce candidate extracts.

**Fields**:

- `material_id`: stable id for the material.
- `title`: human-readable title.
- `material_type`: `pdf`, `markdown`, `review_note`, or `other`.
- `file_label`: filename, folder label, or external source label used for identification.
- `tracking_status`: `external_untracked`, `project_tracked`, or `derived_note`.
- `preparation_status`: `not_started`, `indexed`, `partially_reviewed`, `reviewed`, `blocked`.
- `related_source_id`: optional 012 `ClassicalSource.source_id` when the material maps to a registered source.
- `scope_notes`: what the material may support if reviewed.
- `rights_notes`: notes about copying, quoting, or review limits.
- `gap_reason`: optional reason when the material cannot yet produce candidates.

**Validation Rules**:

- `material_id` values must be unique.
- Root PDF and root `Markdown/` inputs default to `external_untracked`.
- A material with `preparation_status=blocked` must include `gap_reason`.
- `related_source_id`, when present, must refer to a known classical source.

## CandidateExtract

Represents a proposed evidence item that is not yet report-usable.

**Fields**:

- `candidate_id`: stable id.
- `material_id`: source material that produced the candidate.
- `source_locator`: page, chapter, heading, paragraph label, review-note anchor, or other reviewer-verifiable locator.
- `extracted_meaning`: concise summary or paraphrase of the candidate evidence.
- `short_quote`: optional short quote kept within project quote limits.
- `proposed_rule_family`: candidate rule family, aligned with 012 families when possible.
- `risk_tier`: `ordinary`, `sensitive`, or `high_risk`.
- `status`: `draft`, `pending_review`, `returned`, `approved`, `rejected`, `blocked`, or `promoted`.
- `proposed_limitations`: limitations or uncertainty notes.
- `related_evidence_ids`: formal evidence ids that overlap or conflict.
- `related_conflict_ids`: conflict ids that affect this candidate.
- `related_gap_ids`: gap ids this candidate may fill or explain.
- `duplicate_of`: optional candidate or evidence id for duplicate handling.
- `created_by`: maintainer who registered the candidate.
- `created_at`: date of candidate registration.

**Validation Rules**:

- A candidate cannot enter `pending_review` without `material_id`, `source_locator`, `extracted_meaning`, `proposed_rule_family`, and `risk_tier`.
- `high_risk` candidates require `proposed_limitations` before approval.
- Candidates with long copied passages fail validation.
- `approved` candidates must have an approved review decision.
- `promoted` candidates must be included in a promotion batch.

## ReviewDecision

Represents the human review result for one candidate.

**Fields**:

- `decision_id`: stable id.
- `candidate_id`: candidate being reviewed.
- `decision`: `approved`, `returned`, `rejected`, or `blocked`.
- `reviewer`: reviewer name or stable maintainer label.
- `reviewed_at`: review date.
- `rationale`: why this decision was made.
- `required_changes`: changes needed when returned.
- `rejection_reason`: reason when rejected or blocked.
- `approval_limitations`: required report-facing or evidence-facing limitations.
- `source_quality`: `direct_extract`, `review_note`, `secondary_index`, or `needs_recheck`.
- `confidence`: `strong`, `moderate`, or `weak`.

**Validation Rules**:

- Every decision must reference an existing candidate.
- `approved` decisions require `approval_limitations`, `source_quality`, and `confidence`.
- `returned` decisions require `required_changes`.
- `rejected` and `blocked` decisions require `rejection_reason`.
- `needs_recheck` cannot approve a candidate for promotion.

## PromotionBatch

Groups approved candidates prepared for formal evidence corpus updates.

**Fields**:

- `promotion_batch_id`: stable id.
- `candidate_ids`: approved candidates included in the batch.
- `target_evidence_ids`: formal evidence ids created or updated by the batch.
- `review_status`: `draft`, `reviewed`, `approved`, or `blocked`.
- `review_notes`: batch-level summary.
- `unresolved_issues`: remaining source, conflict, duplicate, or safety concerns.

**Validation Rules**:

- A promotion batch cannot include candidates without approved review decisions.
- A blocked batch cannot produce formal evidence.
- A candidate can be `promoted` only when included in an approved or reviewed promotion batch.
- Target evidence ids must not duplicate existing ids unless the batch is explicitly revising them.

## IntakeProgressReport

Computed maintainer-facing summary of the intake queue.

**Fields**:

- `material_counts`: count by material preparation status.
- `candidate_counts`: count by candidate status.
- `risk_tier_counts`: count by risk tier.
- `rule_family_counts`: count by proposed rule family.
- `pending_review_count`: candidates waiting for review.
- `approved_not_promoted_count`: approved candidates not yet in a promotion batch.
- `blocked_or_rejected_count`: candidates excluded from promotion.
- `duplicate_candidates`: candidates marked as duplicates.
- `conflict_link_count`: candidates linked to conflicts.
- `gap_link_count`: candidates linked to gaps.

**Validation Rules**:

- Progress reports are computed from current intake data.
- Pending, approved, rejected, blocked, duplicate, conflict, and gap counts must be separated.
- Formal evidence coverage reports must not count unapproved candidates.

## State Transitions

Candidate review:

```text
draft -> pending_review -> approved -> promoted
   |          |              |
   v          v              v
returned   rejected       blocked
   |
   v
pending_review
```

Source material preparation:

```text
not_started -> indexed -> partially_reviewed -> reviewed
       |          |              |
       v          v              v
     blocked    blocked        blocked
```

Promotion batch:

```text
draft -> reviewed -> approved
   |        |
   v        v
 blocked  blocked
```
