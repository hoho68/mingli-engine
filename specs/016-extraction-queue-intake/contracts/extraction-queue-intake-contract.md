# Extraction Queue Intake Contract

## Extraction Work Package Contract

Extraction work packages group selected 015 queue work into a reviewable handoff for manual candidate extraction.

```json
{
  "package_id": "package_next_candidates_001",
  "package_label": "Next candidate extraction package 001",
  "source_queue_snapshot_ids": [
    "queue_northeast_blind_peak_extract",
    "queue_mingli_true_formula_teacher_extract",
    "queue_markdown_source_batch_001_register",
    "queue_blind_life_manual_risk_review",
    "queue_blind_school_secret_blocked"
  ],
  "selected_task_ids": [
    "task_northeast_blind_peak_extract_001",
    "task_mingli_true_formula_teacher_extract_001"
  ],
  "backlog_record_ids": [
    "backlog_markdown_batch_001_registration_001",
    "backlog_blind_life_manual_risk_review_001",
    "backlog_blind_school_secret_blocked_001"
  ],
  "status": "planned",
  "created_at": "2026-05-31",
  "updated_at": "2026-05-31",
  "notes": "Initial package from the 015 next-action queue."
}
```

Contract rules:

- Every package source queue id must reference a current 015 queue item.
- Every selected task and backlog record must reference the package.
- Work packages are planning metadata only and are never 013 candidate extracts or formal evidence.

## Extraction Task Contract

Extraction tasks represent manual extraction work that may later produce 013 candidate extracts.

```json
{
  "task_id": "task_northeast_blind_peak_extract_001",
  "package_id": "package_next_candidates_001",
  "queue_item_id": "queue_northeast_blind_peak_extract",
  "audit_id": "audit_northeast_blind_peak",
  "source_library_entry_id": "entry_northeast_blind_peak_pdf",
  "intended_source_material_id": "material_northeast_blind_peak_pdf",
  "priority_level": "high",
  "priority_rationale": "Ready source with blind image-method coverage and clear pre-extraction checks.",
  "target_rule_families": ["blind_image_method", "branch_interaction"],
  "target_gap_ids": [],
  "risk_boundary": "sensitive",
  "locator_requirement": "page_or_section",
  "source_quality_note": "Registered source with moderate source quality and locator review required before quotation.",
  "rights_note": "Do not copy long passages; extract concise paraphrased candidate meaning only after review.",
  "pre_extraction_checks": [
    "confirm source locator",
    "avoid absolute verdict language",
    "store concise candidate metadata only"
  ],
  "overlap_warnings": [],
  "status": "planned",
  "created_at": "2026-05-31",
  "updated_at": "2026-05-31"
}
```

Contract rules:

- Extraction tasks require an `extraction_ready` originating queue item.
- Tasks require current audit, alignment, readiness, source-quality, locator, rights, and risk-boundary support.
- Tasks must not include copied source passages, extracted meanings, review decisions, approval status, or promotion status.
- Sensitive and high-risk tasks require explicit safety checks before manual extraction.

## Candidate Draft Slot Contract

Candidate draft slots describe possible future 013 candidate records without creating candidate extracts.

```json
{
  "draft_slot_id": "slot_northeast_blind_image_001",
  "task_id": "task_northeast_blind_peak_extract_001",
  "intended_candidate_label": "Northeast Blind Peak blind image-method candidate",
  "target_rule_family": "blind_image_method",
  "target_gap_id": "",
  "locator_requirement": "page_or_section",
  "expected_review_notes": [
    "Record exact source locator during manual extraction.",
    "Explain uncertainty and school dependency before review."
  ],
  "risk_boundary": "sensitive",
  "safety_requirements": [
    "No absolute destiny language.",
    "No exact death or lifespan claim.",
    "No professional advice."
  ],
  "status": "planned"
}
```

Contract rules:

- Draft slots must reference extraction tasks.
- Draft slots must not include source passages, extracted meanings, approval state, review state, or promotion state.
- Draft slots are not formal evidence and cannot affect report evidence counts.

## Prerequisite Backlog Contract

Prerequisite backlog records preserve queue work that cannot become routine extraction yet.

```json
{
  "backlog_id": "backlog_blind_life_manual_risk_review_001",
  "package_id": "package_next_candidates_001",
  "queue_item_id": "queue_blind_life_manual_risk_review",
  "audit_id": "audit_blind_life_manual",
  "backlog_type": "risk_review",
  "missing_prerequisites": ["risk_review"],
  "durable_reason": "High-risk aphoristic material requires boundary review before extraction.",
  "recommended_action": "risk_review",
  "risk_boundary": "high_risk",
  "status": "planned",
  "created_at": "2026-05-31",
  "updated_at": "2026-05-31"
}
```

Contract rules:

- Every non-ready queue item must have a backlog record or explicit skip reason.
- Backlog records require missing prerequisites or durable reasons.
- Risk-review, blocked, and deferred records cannot be routine extraction tasks.

## Progress Summary Contract

The package progress summary must expose:

- Package counts by status.
- Extraction task counts by status.
- Candidate draft slot counts by status.
- Backlog counts by type and status.
- Risk-boundary counts.
- Duplicate or overlap warning counts.
- Ordered next manual action ids.

Expected behavior:

- Package validation fails when an extraction task lacks a valid 015 queue item, audit record, readiness finding, or alignment finding.
- Package validation fails when draft slots contain copied passages, extracted meanings, review decisions, approval status, or promotion status.
- Package validation fails when high-risk work is scheduled as routine extraction without risk-review prerequisites.
- Package summaries must not count packages, tasks, draft slots, or backlog records as formal evidence.

## Boundary Contract

016 must preserve the existing evidence boundary:

- Raw source files are never report evidence.
- 015 audit records and queue items are never report evidence.
- 016 work packages, extraction tasks, draft slots, and backlog records are never report evidence.
- Candidate extracts remain governed by 013 and require human review.
- Formal reports may consume only reviewed 012 evidence units and source conflicts through the existing report object.
