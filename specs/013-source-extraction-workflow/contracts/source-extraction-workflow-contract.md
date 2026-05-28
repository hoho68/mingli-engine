# Source Extraction Workflow Contract

## Source Material Contract

Source materials identify preparation inputs without requiring user-provided files to become tracked project assets.

```json
{
  "material_id": "material_blind_life_manual_pdf",
  "title": "盲人断命秘典",
  "material_type": "pdf",
  "file_label": "盲人断命秘典.pdf",
  "tracking_status": "external_untracked",
  "preparation_status": "indexed",
  "related_source_id": "blind_life_manual",
  "scope_notes": "Potential blind-school image and high-risk signal material; requires safety rewrite before evidence use.",
  "rights_notes": "Do not copy long passages into project files.",
  "gap_reason": ""
}
```

Contract rules:

- `material_id` must be stable and unique.
- `tracking_status=external_untracked` means the workflow may reference the material label but must not move, delete, convert, or commit the source file.
- `related_source_id` must be empty or refer to a registered 012 source.
- Blocked materials must include a `gap_reason`.

## Candidate Extract Contract

Candidate extracts are proposed evidence and are not report-usable until approved and promoted.

```json
{
  "candidate_id": "candidate_blind_life_manual_001",
  "material_id": "material_blind_life_manual_pdf",
  "source_locator": "review-note:blind_life_manual.md#image-method-1",
  "extracted_meaning": "A blind-school image statement should be rewritten as a conditional signal tied to chart structure, not as a standalone verdict.",
  "short_quote": "",
  "proposed_rule_family": "blind_image_method",
  "risk_tier": "sensitive",
  "status": "pending_review",
  "proposed_limitations": ["Use only as a conditional traditional signal."],
  "related_evidence_ids": [],
  "related_conflict_ids": [],
  "related_gap_ids": ["gap_blind_life_manual_review"],
  "duplicate_of": "",
  "created_by": "maintainer",
  "created_at": "2026-05-28"
}
```

Contract rules:

- `pending_review` candidates require source material, locator, extracted meaning, proposed rule family, and risk tier.
- `high_risk` candidates require non-empty limitation notes before approval.
- Candidate summaries must be concise paraphrases or short quotes within project quote limits.
- Candidates with status other than `approved` or `promoted` must never be exposed as formal report evidence.

## Review Decision Contract

Review decisions record human approval, return, rejection, or blocking.

```json
{
  "decision_id": "review_candidate_blind_life_manual_001",
  "candidate_id": "candidate_blind_life_manual_001",
  "decision": "approved",
  "reviewer": "maintainer",
  "reviewed_at": "2026-05-28",
  "rationale": "Locator is reviewable, summary is conditional, and limitations prevent absolute output.",
  "required_changes": [],
  "rejection_reason": "",
  "approval_limitations": ["Do not use for exact outcome claims."],
  "source_quality": "review_note",
  "confidence": "moderate"
}
```

Contract rules:

- `approved` decisions require approval limitations, source quality, and confidence.
- `returned` decisions require required changes.
- `rejected` and `blocked` decisions require rejection reason.
- `source_quality=needs_recheck` cannot approve promotion.

## Promotion Batch Contract

Promotion batches bridge approved candidates into the formal 012 evidence corpus.

```json
{
  "promotion_batch_id": "promotion_013_seed_001",
  "candidate_ids": ["candidate_blind_life_manual_001"],
  "target_evidence_ids": ["blind_life_manual_blind_image_method_001"],
  "review_status": "reviewed",
  "review_notes": "Initial approved candidates prepared for formal evidence update.",
  "unresolved_issues": []
}
```

Contract rules:

- Promotion batches may include only candidates with approved review decisions.
- Blocked promotion batches cannot create or update formal evidence.
- Formal report generation may use only target evidence ids after they exist in the reviewed evidence corpus.

## Progress Summary Contract

The intake progress summary must expose:

- Source material counts by preparation status.
- Candidate counts by review status.
- Risk tier counts.
- Proposed rule-family counts.
- Approved candidates not yet promoted.
- Rejected and blocked candidate counts with reasons.
- Duplicate, conflict, and gap link counts.

Expected behavior:

- Progress checks fail when pending-review candidates are missing required fields.
- Progress checks fail when approved high-risk candidates lack limitations.
- Progress checks fail when promoted candidates lack promotion batch membership.
- Progress checks pass with warnings when materials have documented gaps but no candidates.

## Report Boundary Contract

013 must preserve the 012 report boundary:

- Raw source materials are never report evidence.
- Pending, returned, rejected, and blocked candidates are never report evidence.
- Approved candidates are still not report evidence until promoted into formal evidence units.
- Formal reports continue to consume reviewed 012 evidence units and source conflicts through the existing report object.
