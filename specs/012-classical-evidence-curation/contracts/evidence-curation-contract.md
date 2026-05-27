# Evidence Curation Contract

## Expanded Source Contract

Each source entry remains compatible with the 011 source registry and may add curation metadata.

```json
{
  "source_id": "blind_life_manual",
  "title": "盲人断命秘典",
  "file_name": "盲人断命秘典.pdf",
  "source_type": "pdf",
  "extraction_status": "partial",
  "review_status": "reviewed",
  "scope_notes": "断语体材料，待拆解为条件化证据。",
  "risk_notes": ["high_risk_signal"],
  "curation_gap_reason": "Needs safety rewrite before report use.",
  "review_reference": "docs/classical_sources/extracts/blind_life_manual.md"
}
```

Contract rules:

- All nine initial source ids must remain present.
- A source with no approved evidence units must expose a curation gap reason.
- `blocked`, `unreviewed`, and `failed` sources may appear in inventory but must not support conclusions.

## Expanded Evidence Unit Contract

Evidence units remain concise summaries and may carry curation metadata.

```json
{
  "evidence_id": "duan_ten_god_relation_002",
  "source_id": "duan_plain_mingxue_outline",
  "source_ref": "page:42; heading:十神关系",
  "theme": "十神组合",
  "rule_family": "ten_god_relation",
  "risk_tier": "ordinary",
  "school": "段氏",
  "summary": "十神组合须结合柱位、日主关系与整体结构，不宜离开原局单断。",
  "applicability": ["ten_god_available", "four_pillars_complete"],
  "limitations": ["缺少柱位或日主关系时降级。"],
  "curation_batch_id": "batch_duan_001",
  "confidence": "moderate",
  "source_quality": "direct_extract",
  "conflict_ids": []
}
```

Contract rules:

- `source_ref` must include `page:`, `chapter:`, `heading:`, or `review-note:`.
- `summary` must be concise and reviewed.
- `risk_tier=high_risk` requires limitations that forbid exact outcome or professional-advice use.
- Evidence units must not contain guaranteed real-world outcomes.
- Evidence units introduced by blocked batches are not report-usable.

## Curation Batch Contract

```json
{
  "batch_id": "batch_duan_001",
  "source_ids": ["duan_plain_mingxue_outline"],
  "evidence_ids": ["duan_ten_god_relation_002"],
  "review_status": "approved",
  "review_notes": "Initial reviewed expansion for ten-god relation rules.",
  "unresolved_issues": []
}
```

Contract rules:

- Batch ids must be unique.
- Approved evidence must belong to an approved or reviewed batch.
- Blocked batches cannot introduce report-usable evidence.

## Source Conflict Contract

```json
{
  "conflict_id": "conflict_pattern_strength_001",
  "rule_family": "pattern_strength",
  "evidence_ids": [
    "teacher_pattern_strength_001",
    "duan_pattern_candidate_003"
  ],
  "conflict_type": "school_difference",
  "reader_note": "师传口径与段氏口径对格局优先级不同，报告应降级为候选。",
  "severity": "moderate",
  "resolution_status": "documented"
}
```

Contract rules:

- Conflict records must reference existing evidence ids.
- Open severe conflicts prevent decided conclusions.
- Documented conflicts must appear as disagreement notes when the affected conclusion is used.

## Coverage Report Contract

The maintainer-facing coverage report must include:

- Evidence count by source.
- Evidence count by rule family.
- Evidence count by risk tier.
- Sources with gaps and reasons.
- Open conflicts and severity.
- High-risk evidence missing limitations.
- Evidence summaries that exceed the configured concise-summary limit.

Expected behavior:

- Coverage checks fail when high-risk evidence lacks limitations.
- Coverage checks fail when approved evidence references blocked or unreviewed sources.
- Coverage checks fail when approved evidence contains guaranteed outcome language.
- Coverage checks pass with warnings when a source has documented gaps but does not support report conclusions.

## Report Compatibility Contract

012 must preserve the 011 report contract:

- Markdown and HTML reports still expose source summary, formal conclusions, evidence traces, conclusion strength, high-risk notes, and unavailable conclusions through the same report object.
- Safe reports may cite expanded evidence units without changing CLI commands or output formats.
- Exact death timing, exact lifespan, diagnosis/treatment, legal, psychological, investment, coercive matching, anxiety creation, and paid-remedy upsell requests remain refused or narrowed.
