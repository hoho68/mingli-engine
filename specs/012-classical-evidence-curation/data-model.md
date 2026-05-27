# Data Model: 经典证据库精修

## ClassicalSource

Represents one registered source from the initial corpus.

**Existing Fields**:

- `source_id`: stable id
- `title`: reader-facing title
- `file_name`: original local file identity
- `source_type`: `pdf`
- `extraction_status`: `not_started`, `converted`, `partial`, `failed`
- `review_status`: `unreviewed`, `reviewed`, `approved`, `blocked`
- `scope_notes`: what the source can support
- `risk_notes`: high-risk themes present in the source

**012 Additions**:

- `curation_gap_reason`: optional maintainer-facing reason when a source has fewer than the target evidence units
- `review_reference`: optional link to review notes or extract location

**Validation Rules**:

- All nine initial sources remain present.
- `approved` sources may support report conclusions.
- `blocked`, `unreviewed`, and `failed` sources must not support report conclusions.
- A source with no approved evidence units must have a curation gap reason.

## EvidenceUnit

Represents a concise, reviewed rule or principle from a source.

**Existing Fields**:

- `evidence_id`
- `source_id`
- `source_ref`
- `theme`
- `rule_family`
- `risk_tier`
- `summary`
- `applicability`
- `limitations`
- `school`

**012 Additions**:

- `curation_batch_id`: batch that introduced or last reviewed the unit
- `confidence`: `strong`, `moderate`, `weak`
- `source_quality`: `direct_extract`, `review_note`, `secondary_index`, `needs_recheck`
- `conflict_ids`: conflicts that affect this unit

**Validation Rules**:

- Evidence units must link to known approved sources before report use.
- `source_ref` must include a page, chapter, heading, or review-note reference.
- `summary` must be concise and must not be a long copied passage.
- `high_risk` evidence requires non-empty limitations and non-exact-output wording.
- `confidence=strong` requires a direct source reference and no unresolved severe conflict.

## CurationBatch

Groups a set of evidence additions or revisions.

**Fields**:

- `batch_id`: stable id
- `source_ids`: sources reviewed in the batch
- `evidence_ids`: evidence units added or revised
- `review_status`: `draft`, `reviewed`, `approved`, `blocked`
- `review_notes`: maintainer-facing summary of what changed
- `unresolved_issues`: remaining extraction, conflict, or safety questions

**Validation Rules**:

- Approved evidence units must belong to an approved or reviewed batch.
- A blocked batch cannot introduce report-usable evidence.
- Batch ids must be unique.

## SourceConflict

Represents disagreement or school dependency between evidence units.

**Fields**:

- `conflict_id`: stable id
- `rule_family`: affected rule family
- `evidence_ids`: evidence units involved
- `conflict_type`: `school_difference`, `textual_disagreement`, `scope_mismatch`, `insufficient_context`
- `reader_note`: concise explanation suitable for report downgrade notes
- `severity`: `minor`, `moderate`, `severe`
- `resolution_status`: `open`, `documented`, `resolved`

**Validation Rules**:

- Conflict evidence ids must exist.
- Severe open conflicts prevent `decided` conclusion strength.
- Documented conflicts may still allow `candidate` or `weakly_supported` conclusions.

## CurationGap

Represents missing or insufficient evidence coverage.

**Fields**:

- `gap_id`: stable id
- `source_id`: affected source
- `rule_family`: optional affected family
- `reason`: extraction failure, missing reference, insufficient review, conflict, or safety rewrite needed
- `blocks_report_use`: whether the gap prevents report conclusions

**Validation Rules**:

- Any source below the minimum coverage target must have at least one gap.
- Gaps that block report use must be visible in coverage reports.

## CoverageReport

Maintainer-facing computed summary.

**Fields**:

- `source_counts`: evidence count by source
- `rule_family_counts`: evidence count by rule family
- `risk_tier_counts`: evidence count by risk tier
- `approved_evidence_count`
- `sources_with_gaps`
- `open_conflicts`
- `high_risk_without_limitations`
- `long_summary_violations`

**Validation Rules**:

- Coverage reports are computed from current data.
- Coverage must expose all remaining sources or families below target.
- High-risk and long-summary violations fail the validation run.

## State Transitions

Source curation:

```text
not_started -> partial -> reviewed -> approved
          |       |          |
          v       v          v
        failed  blocked    blocked
```

Batch review:

```text
draft -> reviewed -> approved
   |        |
   v        v
 blocked  blocked
```

Conflict resolution:

```text
open -> documented -> resolved
```
