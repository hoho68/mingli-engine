# Data Model: 典籍证据核心与放大报告口径

## ClassicalSource

Represents one book or PDF in the classical evidence corpus.

**Fields**:

- `source_id`: stable id such as `northeast_blind_peak`
- `title`: human-readable title
- `file_name`: original local file name
- `source_type`: `pdf`
- `extraction_status`: `not_started`, `converted`, `partial`, `failed`
- `review_status`: `unreviewed`, `reviewed`, `approved`, `blocked`
- `scope_notes`: short description of what the source can support
- `risk_notes`: high-risk themes present in the source

**Validation Rules**:

- `source_id` must be unique.
- A source may support report conclusions only when `review_status` is `approved`.
- `blocked` sources remain in the registry but cannot support report conclusions.

## EvidenceUnit

Represents a curated rule, principle, or source-backed summary used to support report conclusions.

**Fields**:

- `evidence_id`: stable id
- `source_id`: link to `ClassicalSource`
- `source_ref`: page, chapter, heading, or review note reference
- `theme`: reader-facing topic such as 格局, 十神, 岁运, 盲派象法
- `rule_family`: machine-facing family such as `pattern_strength`, `ten_god_relation`, `branch_interaction`, `luck_cycle`, `high_risk_signal`
- `risk_tier`: `ordinary`, `sensitive`, `high_risk`
- `summary`: concise reviewed statement
- `applicability`: chart conditions that make the unit relevant
- `limitations`: when this unit should be downgraded or not used
- `school`: optional school/source orientation

**Validation Rules**:

- Evidence units must link to an approved source before they can appear in a report trace.
- `high_risk` units require limitations.
- `summary` must be a synthesis, not a long copied passage.

## EvidenceTrace

Links a report conclusion to chart facts and evidence.

**Fields**:

- `trace_id`: stable id inside a report
- `conclusion_id`: conclusion being supported
- `chart_signals`: relevant chart fields or derived observations
- `evidence_ids`: evidence units used
- `assumptions`: relevant calculation or school assumptions
- `disagreement_note`: optional source or school disagreement

**Validation Rules**:

- Major conclusions must have at least one chart signal and either evidence ids or an unavailable/disputed explanation.
- Trace output must be reader-facing in reports and machine-checkable in tests.

## FormalConclusion

Represents one substantive traditional judgment in the expanded report.

**Fields**:

- `conclusion_id`: stable id inside a report
- `title`: reader-facing heading
- `body`: concise explanation
- `rule_family`: primary rule family
- `strength`: `decided`, `candidate`, `weakly_supported`, `disputed`, `unavailable`
- `risk_tier`: `ordinary`, `sensitive`, `high_risk`
- `trace`: `EvidenceTrace`

**Validation Rules**:

- `decided` conclusions require strong chart signals and approved evidence.
- `candidate` is the default for pattern, useful-god, and high-risk conclusions unless evidence is unusually clear.
- `high_risk` conclusions must use uncertainty language and cannot present guaranteed outcomes.

## ExpandedReportEvidence

Groups source-backed material for report rendering.

**Fields**:

- `source_summary`: reader-facing list of source families used
- `formal_conclusions`: list of `FormalConclusion`
- `high_risk_notes`: narrowed high-risk signal notes
- `unavailable_conclusions`: skipped or downgraded conclusions with reasons

**Validation Rules**:

- Formal reports must include `source_summary`.
- The renderer must preserve disclaimer, chart source disclosure, calculation assumptions, and evidence explanation.

## State Transitions

Source review state:

```text
not_started -> converted -> reviewed -> approved
                      |          |
                      v          v
                    failed     blocked
```

Conclusion strength state:

```text
unavailable -> weakly_supported -> candidate -> decided
                    |
                    v
                 disputed
```

High-risk handling:

```text
source high-risk rule -> risk signal note -> narrowed report output
                                      |-> refusal for exact outcome/professional advice
```
