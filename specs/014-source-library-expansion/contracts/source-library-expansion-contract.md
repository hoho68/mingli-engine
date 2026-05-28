# Source Library Expansion Contract

## Source Library Entry Contract

Source-library entries register materials for planning without requiring raw user-provided files to become tracked project assets.

```json
{
  "entry_id": "entry_blind_life_manual_pdf",
  "material_id": "material_blind_life_manual_pdf",
  "title": "Blind Life Manual",
  "material_type": "pdf",
  "local_reference": "blind_life_manual.pdf",
  "tracking_status": "external_untracked",
  "readiness_status": "ready_for_extraction",
  "topic_tags": ["blind-school", "image-method", "aphoristic-material"],
  "rule_families": ["blind_image_method", "high_risk_signal"],
  "source_quality_notes": "Usable only after conditional rewrite and locator review.",
  "rights_notes": "Do not copy long passages into project files.",
  "risk_tier": "high_risk",
  "risk_notes": ["May contain standalone verdict or life-risk language."],
  "priority_level": "high",
  "next_action": "extract_candidates",
  "outcome_reason": "",
  "created_at": "2026-05-28",
  "updated_at": "2026-05-28"
}
```

Contract rules:

- `entry_id` must be stable and unique.
- `tracking_status=external_untracked` means the workflow may reference the material label but must not move, delete, convert, or commit the source file.
- `ready_for_extraction` requires topic tags, rule families, source quality notes, and rights notes.
- `high_risk` requires risk notes before the source can enter an extraction batch.
- `deferred`, `duplicate`, `exhausted`, and `blocked` entries require `outcome_reason`.

## Priority Assessment Contract

Priority assessments document why a source should be processed now, later, or not at all.

```json
{
  "assessment_id": "priority_blind_life_manual_001",
  "entry_id": "entry_blind_life_manual_pdf",
  "priority_level": "high",
  "expected_value": "improves_high_risk_boundary",
  "target_gap_ids": ["gap_blind_life_manual"],
  "target_rule_families": ["blind_image_method", "high_risk_signal"],
  "source_quality": "moderate",
  "effort_level": "medium",
  "risk_tier": "high_risk",
  "rationale": "The source can improve high-risk boundary handling if rewritten as conditional, source-located signals.",
  "assessed_by": "maintainer",
  "assessed_at": "2026-05-28"
}
```

Contract rules:

- Assessments must reference existing source-library entries.
- `target_gap_ids` and `target_rule_families` cannot both be empty.
- `source_quality=needs_recheck` cannot be `critical`.
- `high_risk` assessments must describe the safety review boundary.
- `deferred` assessments must explain what would make the source worth revisiting.

## Curation Batch Plan Contract

Batch plans choose registered sources for upcoming extraction and review. They are not promotion batches and do not create formal evidence.

```json
{
  "batch_plan_id": "batch_plan_high_risk_boundaries_001",
  "title": "High-risk boundary source review",
  "goal": "Prepare sources that can clarify life-risk and image-method boundaries without exact-outcome claims.",
  "entry_ids": ["entry_blind_life_manual_pdf", "entry_life_death_book_100_pages_pdf"],
  "target_gap_ids": ["gap_blind_life_manual"],
  "target_rule_families": ["high_risk_signal", "blind_image_method"],
  "risk_boundary": "high_risk",
  "expected_output": ["candidate_extracts", "gap_notes", "conflict_notes"],
  "status": "planned",
  "review_capacity": "Small batch; high-risk review required before approval.",
  "completion_summary": "",
  "recommended_next_batch": ""
}
```

Contract rules:

- Batch plans must include at least one source entry.
- Batch plans must identify a target gap, target rule family, conflict area, or source-quality rationale.
- High-risk batch plans require all included high-risk entries to have risk notes.
- `completed`, `deferred`, and `blocked` batch plans require a completion summary.
- Planned batch entries must not be counted as formal evidence coverage.

## Source Value Summary Contract

Source value summaries are computed from source-library records plus downstream 013/012 outcomes.

Expected summary fields:

```json
{
  "subject_id": "entry_blind_life_manual_pdf",
  "subject_type": "source",
  "candidate_count": 1,
  "approved_candidate_count": 0,
  "rejected_or_blocked_count": 0,
  "conflict_count": 0,
  "gap_count": 1,
  "promoted_evidence_count": 0,
  "value_status": "in_progress",
  "recommended_next_action": "review_candidates"
}
```

Expected behavior:

- Registered sources with no downstream candidates are not value-producing.
- Approved candidates count as review value but not formal evidence until promotion creates or updates formal evidence.
- Rejected, blocked, duplicate, exhausted, and deferred outcomes remain visible with reasons.
- Completed batch summaries identify improved rule families, remaining gaps, and the recommended next batch focus.

## Report Boundary Contract

014 must preserve the existing report boundary:

- Raw source files are never report evidence.
- Source-library entries are never report evidence.
- Priority assessments and batch plans are never report evidence.
- Pending, returned, rejected, and blocked candidates remain outside formal report evidence.
- Approved candidates are still not formal report evidence until promoted into the reviewed evidence corpus.
- Formal reports may consume only reviewed evidence units and source conflicts through the existing report object.
