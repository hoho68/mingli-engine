# Existing Materials Audit Contract

## Material Audit Record Contract

Material audit records group existing local materials without requiring raw files to become tracked project assets.

```json
{
  "audit_id": "audit_northeast_blind_peak",
  "canonical_title": "Northeast Blind Peak",
  "alternate_titles": ["东北盲派巅峰.pdf"],
  "material_scope": "bazi",
  "primary_material_type": "pdf",
  "representations": ["repr_northeast_blind_peak_root_pdf"],
  "source_library_entry_id": "entry_northeast_blind_peak_pdf",
  "source_identity_confidence": "confirmed",
  "preparation_state": "raw_available",
  "source_boundary": "external_untracked",
  "topic_tags": ["blind-school", "image-method", "structure"],
  "rule_families": ["blind_image_method", "branch_interaction"],
  "risk_tier": "sensitive",
  "risk_notes": ["Image-method material may require conditional rewrite."],
  "rights_notes": "Do not copy long passages; store concise audit metadata only.",
  "missing_prerequisites": ["cleaned_text_or_locator_review"],
  "recommended_next_action": "prepare_text",
  "outcome_reason": "",
  "created_at": "2026-05-30",
  "updated_at": "2026-05-30"
}
```

Contract rules:

- `audit_id` must be stable and unique.
- Raw local files referenced by `source_boundary=external_untracked` must not be moved, deleted, renamed, converted, committed, or mutated by the audit.
- High-risk records require risk notes.
- Records marked ready for extraction review require source identity, source-library relationship or registration recommendation, rights notes, risk notes when needed, and at least one topic or rule family.
- Deferred and blocked records require an outcome reason.

## Material Representation Contract

Material representations record visible forms of the same material.

```json
{
  "representation_id": "repr_northeast_blind_peak_root_pdf",
  "audit_id": "audit_northeast_blind_peak",
  "representation_type": "root_pdf",
  "local_reference": "东北盲派巅峰.pdf",
  "tracking_status": "external_untracked",
  "text_quality": "not_text",
  "locator_quality": "file_only",
  "size_hint": "root PDF present",
  "modified_hint": "",
  "contains_images": true,
  "notes": "Raw PDF is external preparation material; do not ingest as evidence."
}
```

Contract rules:

- Each representation must reference an existing audit record.
- `local_reference` is a label or path reference, not copied source text.
- External raw files default to `external_untracked`.
- Cleaned Markdown represents preparation quality only and must not imply formal evidence readiness.

## Source Alignment Finding Contract

Source alignment findings connect audited material groups to 014 source-library entries or 013 source-intake materials.

```json
{
  "alignment_id": "align_northeast_blind_peak_001",
  "audit_id": "audit_northeast_blind_peak",
  "match_type": "exact",
  "source_library_entry_id": "entry_northeast_blind_peak_pdf",
  "source_material_id": "material_northeast_blind_peak_pdf",
  "confidence": "strong",
  "evidence": "Root PDF label and 014 local reference describe the same source.",
  "registration_recommendation": "none",
  "duplicate_or_variant_notes": "",
  "reviewer": "maintainer",
  "reviewed_at": "2026-05-30"
}
```

Contract rules:

- Exact and likely matches require a source-library entry id.
- Missing source-library entries require a registration recommendation.
- Duplicate and edition-variant findings require explanatory notes.
- Out-of-scope findings require the reason the material is deferred from the current Bazi workflow.

## Preparation Readiness Finding Contract

Preparation readiness findings decide whether a material can enter candidate-extraction review.

```json
{
  "readiness_id": "ready_northeast_blind_peak_001",
  "audit_id": "audit_northeast_blind_peak",
  "readiness_state": "needs_locator_review",
  "text_preparation_status": "raw_only",
  "locator_confidence": "weak",
  "source_quality": "moderate",
  "risk_boundary": "sensitive",
  "missing_prerequisites": ["cleaned_text_or_locator_review"],
  "ready_reasons": ["Registered in source library and has target rule families."],
  "blockers": [],
  "recommended_next_action": "prepare_text",
  "assessed_by": "maintainer",
  "assessed_at": "2026-05-30"
}
```

Contract rules:

- Ready findings require ready reasons and no blockers.
- Not-ready findings require missing prerequisites or blockers.
- High-risk findings require risk-review notes before extraction readiness.
- `source_quality=needs_recheck` cannot be extraction-ready without a recheck action.

## Extraction Queue Item Contract

Extraction queue items turn the audit into concrete next work.

```json
{
  "queue_item_id": "queue_northeast_blind_peak_prepare_001",
  "audit_id": "audit_northeast_blind_peak",
  "queue_type": "preparation_backlog",
  "priority_level": "high",
  "priority_rationale": "High-priority 014 source with useful blind-school image-method coverage, but locator preparation is still needed.",
  "target_rule_families": ["blind_image_method", "branch_interaction"],
  "target_gap_ids": [],
  "risk_boundary": "sensitive",
  "pre_extraction_checks": ["confirm locator", "avoid absolute verdict language", "store concise paraphrases only"],
  "recommended_action": "prepare_text",
  "depends_on": [],
  "status": "planned",
  "created_at": "2026-05-30",
  "updated_at": "2026-05-30"
}
```

Contract rules:

- Queue items must reference existing audit records.
- Extraction-ready queue items require source-library alignment, readiness rationale, target rule family or gap, source quality, risk boundary, and pre-extraction checks.
- Preparation backlog items require missing prerequisites.
- High-risk queue items require stricter risk-review prerequisites.
- Queue items are not candidate extracts and are never formal report evidence.

## Progress Summary Contract

The audit progress summary must expose:

- Material group counts by preparation state.
- Representation counts by representation type.
- Source-alignment counts by match type.
- Readiness counts by readiness state.
- Queue counts by queue type and status.
- Risk tier counts.
- Missing source-library registration count.
- Extraction-ready count.
- Preparation backlog count.
- Ordered next recommended queue item ids.

Expected behavior:

- Progress checks fail when extraction-ready items are missing source-library alignment or pre-extraction checks.
- Progress checks fail when high-risk or sensitive materials are missing risk notes.
- Progress checks pass with visible backlog counts when useful materials need preparation.
- Audit summaries must not count audited materials, prepared text, or queue items as formal evidence.

## Boundary Contract

015 must preserve the existing evidence boundary:

- Raw source files are never report evidence.
- Prepared Markdown and cleaned Markdown are never report evidence.
- Learning notes and knowledge-skeleton artifacts are never report evidence.
- Audit records, readiness findings, source-alignment findings, and queue items are never report evidence.
- Candidate extracts remain governed by 013.
- Formal reports may consume only reviewed 012 evidence units and source conflicts through the existing report object.
