# Learning Reference Curation Contract

## Learning Reference Note Contract

Learning reference notes turn 016 extraction tasks into readable study metadata.

```json
{
  "note_id": "note_northeast_blind_peak_001",
  "task_id": "task_northeast_blind_peak_extract_001",
  "package_id": "package_next_candidates_001",
  "queue_item_id": "queue_northeast_blind_peak_extract",
  "audit_id": "audit_northeast_blind_peak",
  "source_library_entry_id": "entry_northeast_blind_peak_pdf",
  "source_material_id": "material_northeast_blind_peak_pdf",
  "source_title": "Northeast Blind Peak",
  "target_rule_families": ["blind_image_method", "branch_interaction"],
  "locator_requirement": "page_or_section",
  "risk_boundary": "sensitive",
  "rights_note": "Do not copy long passages; store concise paraphrases only.",
  "source_quality_note": "Confirm page or section locator before manual extraction.",
  "learning_points": ["lp_northeast_blind_image_001"],
  "overlap_candidate_ids": [
    "candidate_northeast_blind_image_001",
    "candidate_northeast_blind_image_duplicate_001"
  ],
  "status": "draft",
  "created_at": "2026-05-31",
  "updated_at": "2026-05-31"
}
```

Contract rules:

- Every note must reference an existing 016 extraction task.
- Notes must preserve traceability to 015 queue/audit data and 014/013 source ids.
- Notes are learning metadata only and never formal report evidence.

## Learning Point Contract

Learning points are concise study units that may later become 013 candidates.

```json
{
  "learning_point_id": "lp_northeast_blind_image_001",
  "note_id": "note_northeast_blind_peak_001",
  "point_label": "Blind image method conditional signal",
  "source_locator": "page_or_section_required",
  "summary": "Blind image statements should be framed as conditional traditional signals tied to chart structure.",
  "proposed_rule_family": "blind_image_method",
  "risk_tier": "sensitive",
  "limitations": [
    "State uncertainty and school dependency.",
    "Do not use as standalone verdict language."
  ],
  "candidate_readiness": "duplicate_review",
  "candidate_decision_id": "decision_northeast_blind_image_001"
}
```

Contract rules:

- Learning points must reference a learning reference note.
- Summaries must be concise and must not copy long source passages.
- Sensitive and high-risk points require uncertainty and limitation notes.
- Candidate readiness must be explicit before any candidate-intake decision is applied.

## Candidate Intake Decision Contract

Candidate-intake decisions describe whether a learning point should create or reuse 013 candidate records.

```json
{
  "decision_id": "decision_northeast_blind_image_001",
  "learning_point_id": "lp_northeast_blind_image_001",
  "decision": "manual_review",
  "source_material_id": "material_northeast_blind_peak_pdf",
  "candidate_id": "",
  "overlap_candidate_ids": [
    "candidate_northeast_blind_image_001",
    "candidate_northeast_blind_image_duplicate_001"
  ],
  "rationale": "Existing pending and rejected candidates overlap this source and rule family; reviewer must decide reuse or replacement.",
  "status": "planned",
  "created_at": "2026-05-31",
  "updated_at": "2026-05-31"
}
```

Contract rules:

- Decisions must reference learning points.
- `create_candidate` decisions require candidate-ready point metadata.
- Reuse and duplicate-avoidance decisions require overlap candidate ids.
- Decisions do not approve, promote, or create formal evidence.

## Prerequisite Action Note Contract

Prerequisite action notes keep non-ready backlog work visible.

```json
{
  "action_note_id": "action_blind_life_manual_risk_review_001",
  "backlog_id": "backlog_blind_life_manual_risk_review_001",
  "package_id": "package_next_candidates_001",
  "queue_item_id": "queue_blind_life_manual_risk_review",
  "audit_id": "audit_blind_life_manual",
  "action_type": "risk_review",
  "missing_prerequisites": ["risk_review"],
  "durable_reason": "High-risk aphoristic material needs boundary review before candidate extraction.",
  "recommended_action": "risk_review",
  "risk_boundary": "high_risk",
  "status": "planned",
  "created_at": "2026-05-31",
  "updated_at": "2026-05-31"
}
```

Contract rules:

- Action notes must reference 016 prerequisite backlog records.
- Action notes cannot become learning points or candidate extracts until prerequisites are resolved.
- Risk-review, deferred, and blocked actions stay outside routine candidate extraction.

## Progress Summary Contract

The learning-reference progress summary must expose:

- Learning reference note counts by status.
- Learning point counts by candidate readiness.
- Candidate-intake decision counts by decision and status.
- Prerequisite action counts by type and status.
- Risk-tier counts.
- Duplicate or overlap warning counts.
- Candidate-ready learning point counts.
- Ordered next action ids.
- Formal evidence delta, which must remain zero.

## Boundary Contract

017 must preserve the evidence boundary:

- External raw files are never read or mutated by 017.
- 016 package records are planning metadata.
- 017 notes, learning points, decisions, and action notes are learning/reference metadata.
- 013 candidate extracts remain governed by 013 and require human review.
- Formal reports may consume only reviewed 012 evidence units and source conflicts through existing report loaders.
