# Data Model: Existing Materials Audit and Preparation

## MaterialAuditRecord

Represents one audited material group across raw files, prepared text, cleaned text, maintainer notes, and knowledge-skeleton artifacts.

**Fields**:

- `audit_id`: stable id for the audited material group.
- `canonical_title`: best-known maintainer-facing title.
- `alternate_titles`: other known labels, file names, translated names, or edition names.
- `material_scope`: `bazi`, `ziwei`, `qimen`, `ritual_remedy`, `mixed`, or `out_of_scope`.
- `primary_material_type`: `pdf`, `markdown`, `note`, `image_folder`, `mixed`, or `other`.
- `representations`: list of `MaterialRepresentation` ids.
- `source_library_entry_id`: optional 014 source-library entry id when already aligned.
- `source_identity_confidence`: `confirmed`, `likely`, `uncertain`, or `conflicting`.
- `preparation_state`: `not_started`, `raw_available`, `prepared_text_available`, `cleaned_text_available`, `notes_available`, `candidate_skeleton_available`, `ready_for_extraction_review`, `deferred`, or `blocked`.
- `source_boundary`: `external_untracked`, `project_tracked_metadata`, or `derived_note_only`.
- `topic_tags`: maintainer-facing topic labels.
- `rule_families`: proposed Bazi rule families the material may support.
- `risk_tier`: `ordinary`, `sensitive`, or `high_risk`.
- `risk_notes`: reasons for sensitive or high-risk handling.
- `rights_notes`: source-handling and quoting limits.
- `missing_prerequisites`: missing items such as locator review, title confirmation, cleaned text, source-library registration, risk notes, or rights notes.
- `recommended_next_action`: `register_source`, `clarify_identity`, `prepare_text`, `review_cleaned_text`, `risk_review`, `extract_candidates`, `defer`, `block`, or `no_action`.
- `outcome_reason`: durable reason when deferred or blocked.
- `created_at`: audit record creation date.
- `updated_at`: latest audit update date.

**Validation Rules**:

- `audit_id` values must be unique.
- Each record must have at least one representation or a documented `derived_note_only` boundary.
- `external_untracked` records must not require raw file movement, deletion, conversion, or commit.
- `source_identity_confidence=conflicting` requires a missing prerequisite or outcome reason explaining the conflict.
- `risk_tier=high_risk` requires non-empty `risk_notes`.
- `preparation_state=ready_for_extraction_review` requires source identity confidence, rights notes, risk notes when needed, at least one target topic or rule family, and a source-library entry or explicit registration recommendation.
- `deferred` and `blocked` records require `outcome_reason`.

## MaterialRepresentation

Represents one visible form of a material discovered or maintained locally.

**Fields**:

- `representation_id`: stable id for the representation.
- `audit_id`: material audit record this representation belongs to.
- `representation_type`: `root_pdf`, `raw_markdown`, `cleaned_markdown`, `learning_note`, `processing_status_note`, `knowledge_skeleton`, `image_asset`, `raw_folder`, or `other`.
- `local_reference`: filename, folder label, or project-relative path label.
- `tracking_status`: `external_untracked`, `project_tracked`, or `derived_note`.
- `text_quality`: `unknown`, `raw_ocr`, `noisy`, `usable`, `cleaned`, `summary_only`, or `not_text`.
- `locator_quality`: `none`, `folder_only`, `file_only`, `heading`, `line_window`, `page_or_section`, or `review_anchor`.
- `size_hint`: optional human-readable or metadata-only size note.
- `modified_hint`: optional metadata-only modified-date note when useful.
- `contains_images`: whether images or image references may contain review-relevant material.
- `notes`: concise representation note.

**Validation Rules**:

- `representation_id` values must be unique.
- Every representation must reference an existing `audit_id`.
- `local_reference` must be a label or path reference, not copied source text.
- `root_pdf`, `raw_folder`, and external preparation materials default to `external_untracked`.
- `cleaned_markdown` cannot by itself imply formal evidence readiness.

## SourceAlignmentFinding

Represents how an audited material group relates to 014 source-library entries and existing source-intake records.

**Fields**:

- `alignment_id`: stable id.
- `audit_id`: audited material group.
- `match_type`: `exact`, `likely`, `possible_duplicate`, `edition_variant`, `missing_source_library_entry`, `blocked_source_library_entry`, `out_of_scope`, or `uncertain`.
- `source_library_entry_id`: optional matched 014 entry id.
- `source_material_id`: optional matched 013 source material id.
- `confidence`: `strong`, `moderate`, or `weak`.
- `evidence`: concise reason for the alignment decision.
- `registration_recommendation`: whether a source-library entry should be created or updated.
- `duplicate_or_variant_notes`: notes for possible duplicate or edition-variant handling.
- `reviewer`: maintainer label.
- `reviewed_at`: review date.

**Validation Rules**:

- Every finding must reference an existing audit record.
- `exact` and `likely` matches require `source_library_entry_id`.
- `missing_source_library_entry` requires a registration recommendation.
- Duplicate and edition-variant findings require explanatory notes.
- `out_of_scope` findings require the scope reason.

## PreparationReadinessFinding

Represents whether an audited material is ready for candidate-extraction review or needs more preparation.

**Fields**:

- `readiness_id`: stable id.
- `audit_id`: audited material group.
- `readiness_state`: `ready_for_extraction_review`, `needs_cleaning`, `needs_locator_review`, `needs_source_registration`, `needs_identity_clarification`, `needs_rights_review`, `needs_risk_review`, `preparation_backlog`, `deferred`, or `blocked`.
- `text_preparation_status`: `not_started`, `raw_only`, `prepared`, `cleaned`, `summary_only`, or `not_applicable`.
- `locator_confidence`: `none`, `weak`, `moderate`, or `strong`.
- `source_quality`: `strong`, `moderate`, `weak`, or `needs_recheck`.
- `risk_boundary`: `ordinary`, `sensitive`, or `high_risk`.
- `missing_prerequisites`: list of missing prerequisites.
- `ready_reasons`: reasons supporting readiness.
- `blockers`: reasons preventing extraction.
- `recommended_next_action`: next maintainer action.
- `assessed_by`: maintainer label.
- `assessed_at`: assessment date.

**Validation Rules**:

- Every readiness finding must reference an existing audit record.
- `ready_for_extraction_review` requires at least one ready reason and no blockers.
- `needs_*`, `preparation_backlog`, `deferred`, and `blocked` states require missing prerequisites or blockers.
- `risk_boundary=high_risk` requires a `needs_risk_review`, `preparation_backlog`, or explicit high-risk ready reason.
- `source_quality=needs_recheck` cannot be extraction-ready without a recheck action.

## ExtractionQueueItem

Represents a recommended next action for candidate extraction or material preparation.

**Fields**:

- `queue_item_id`: stable id.
- `audit_id`: material audit record.
- `queue_type`: `extraction_ready`, `preparation_backlog`, `registration_backlog`, `risk_review_backlog`, or `blocked_backlog`.
- `priority_level`: `critical`, `high`, `medium`, `low`, or `deferred`.
- `priority_rationale`: why this item is placed in the queue.
- `target_rule_families`: rule families expected to benefit.
- `target_gap_ids`: evidence gaps or audit gaps the item may address.
- `risk_boundary`: `ordinary`, `sensitive`, or `high_risk`.
- `pre_extraction_checks`: checks required before extraction begins.
- `recommended_action`: `register_source`, `clarify_identity`, `prepare_text`, `review_cleaned_text`, `risk_review`, `extract_candidates`, `defer`, or `block`.
- `depends_on`: other queue item ids or prerequisite labels.
- `status`: `planned`, `active`, `completed`, `deferred`, or `blocked`.
- `created_at`: queue creation date.
- `updated_at`: latest queue update date.

**Validation Rules**:

- Every queue item must reference an existing audit record.
- Extraction-ready items require source-library alignment, readiness rationale, target rule family or gap, source quality, risk boundary, and pre-extraction checks.
- High-risk extraction-ready items require risk-review checks and cannot be ranked ahead of safer equivalent work without rationale.
- Preparation and registration backlog items require a missing prerequisite.
- Blocked and deferred queue items require a reason.

## AuditProgressSummary

Computed maintainer-facing summary of existing-material audit coverage.

**Fields**:

- `material_group_counts`: count by `preparation_state`.
- `representation_counts`: count by `representation_type`.
- `source_alignment_counts`: count by `match_type`.
- `readiness_counts`: count by `readiness_state`.
- `queue_counts`: count by `queue_type` and `status`.
- `risk_tier_counts`: count by risk tier.
- `out_of_scope_count`: count of materials deferred from the current Bazi evidence workflow.
- `missing_registration_count`: count of useful materials missing source-library registration.
- `extraction_ready_count`: count of extraction-ready queue items.
- `preparation_backlog_count`: count of useful but not-ready materials.
- `next_action_ids`: ordered next recommended queue item ids.

**Validation Rules**:

- Summaries are computed from current audit records, representations, alignment findings, readiness findings, and queue items.
- Counts must separate extraction-ready items from preparation, registration, risk-review, deferred, and blocked backlogs.
- Audit progress summaries must never include audited materials in formal evidence counts.

## State Transitions

Material preparation:

```text
not_started -> raw_available -> prepared_text_available -> cleaned_text_available
       |              |                    |
       v              v                    v
    deferred    notes_available     ready_for_extraction_review
       |              |                    |
       v              v                    v
    blocked    candidate_skeleton_available -> ready_for_extraction_review
```

Readiness:

```text
needs_identity_clarification -> needs_source_registration -> needs_locator_review
              |                           |                         |
              v                           v                         v
        preparation_backlog ------> needs_cleaning ----------> ready_for_extraction_review
              |                           |                         |
              v                           v                         v
          deferred                   blocked               needs_risk_review
```

Queue:

```text
registration_backlog -> preparation_backlog -> risk_review_backlog -> extraction_ready
          |                    |                    |                 |
          v                    v                    v                 v
       deferred             blocked              blocked          completed
```
