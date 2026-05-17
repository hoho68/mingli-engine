# Data Model: 八字报告白话表达优化

## Reader-Facing Label

Represents a human-readable phrase shown in the report instead of a raw internal value.

| Field | Meaning | Validation |
|-------|---------|------------|
| raw_value | Internal value from chart or metadata | May be empty or unknown |
| label | Reader-facing Chinese phrase | Must not create new interpretation meaning |
| category | The type of value being labeled | One of source type, confidence, calendar type, pillar name, placeholder |

Known label expectations:

- `auto_calculated` -> `系统自动排盘`
- `external_verified` -> `外部排盘已核对`
- `low` -> `低可信度`
- `medium` -> `中等可信度`
- `high` -> `高可信度`
- `gregorian` -> `公历`
- `year` -> `年柱`
- `month` -> `月柱`
- `day` -> `日柱`
- `hour` -> `时柱`

Fallback rule:

- Empty or placeholder-like values display as `未说明`.
- Unknown non-empty values are disclosed conservatively when hiding them would reduce source transparency.

## Plain-Language Report Wording

Represents report text prepared for final Markdown output.

| Field | Meaning | Validation |
|-------|---------|------------|
| quick guide wording | First reading guidance after disclaimer | Three to five bullet lines; no deterministic claims |
| chart card wording | Birth profile and day-master facts | Uses reader-facing calendar and placeholder labels |
| source wording | Chart source and assumptions | Keeps source note, calendar, timezone, solar terms, true-solar-time, and confidence visible |
| pillar summary wording | Four-pillar rows | Uses Chinese pillar names and keeps stems, branches, hidden stems, ten gods, and elements visible |
| action-reflection wording | Safe focus-topic prompt | Frames suggestions as reflection or review cues, not promised outcomes |

## Machine-Facing Value

Represents a valid internal value that may be appropriate in JSON data but not in final reader-facing Markdown.

Selected raw labels that must not appear in successful formal report body text:

- `auto_calculated`
- `external_verified`
- `medium`
- `gregorian`
- `year：`
- `month：`
- `day：`
- `hour：`

The selected list is intentionally scoped to current supported examples and may be expanded in later features.
