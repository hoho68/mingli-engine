# Classical Evidence Contract

## Source Registry Contract

Every initial PDF must have one source registry entry.

```json
{
  "source_id": "northeast_blind_peak",
  "title": "东北盲派巅峰",
  "file_name": "东北盲派巅峰.pdf",
  "source_type": "pdf",
  "extraction_status": "converted",
  "review_status": "approved",
  "scope_notes": "盲派象法、结构判断、应事口径",
  "risk_notes": ["high_risk_signal"]
}
```

Contract rules:

- `source_id` is stable and unique.
- A source with `review_status` other than `approved` may appear in source inventory but must not support report conclusions.
- The source registry must include all nine initial PDFs.

## Evidence Unit Contract

Each curated evidence unit must be source-backed and tagged.

```json
{
  "evidence_id": "duan_ten_god_relation_001",
  "source_id": "duan_plain_mingxue_outline",
  "source_ref": "review-note:ten-god-relationships",
  "theme": "十神关系",
  "rule_family": "ten_god_relation",
  "risk_tier": "ordinary",
  "school": "段氏",
  "summary": "十神关系应结合柱位与组合看关系功能，不宜脱离结构单断。",
  "applicability": ["ten_god_available", "four_pillars_complete"],
  "limitations": ["缺少十神标注时降级为不可用"]
}
```

Contract rules:

- `summary` must be concise and reviewed.
- `risk_tier=high_risk` requires non-empty `limitations`.
- Evidence units must not contain guaranteed real-world outcomes.

## Report Evidence Contract

Formal reports must expose source-backed conclusions in both Markdown and HTML.

Required reader-facing content:

- Source summary: which source families or books support the report.
- Formal judgment section: traditional judgments such as 格局候选, 旺衰倾向, 用神候选, 十神组合, 刑冲合害, or 大运流年主题.
- Evidence trace: chart signal plus source/rule-family basis for major conclusions.
- Conclusion strength: decided, candidate, weakly supported, disputed, or unavailable.
- High-risk label where applicable.

Required behavior:

- Markdown and HTML renderers must show the same report contract.
- Existing chart source and calculation assumptions remain visible.
- Unsafe exact-outcome requests return JSON safety/narrowing output instead of a formal report.

## High-Risk Narrowing Contract

Requests for high-risk themes follow this behavior:

| Request Type | Expected Behavior |
| --- | --- |
| General health tendency in formal report | Allowed as traditional high-risk or sensitive signal, with uncertainty and professional-care disclaimer |
| Exact disease diagnosis or treatment | Refused or narrowed to non-diagnostic traditional signal explanation |
| Exact death timing or exact lifespan | Refused or narrowed to non-exact traditional risk-signal explanation |
| Disaster, severe loss, or accident signal | Allowed only as conditional risk-signal language; no guaranteed event |
| Remedy or adjustment | Allowed as traditional claim description and low-risk reflection; no guaranteed effect or paid pressure |
| Investment, legal, psychological instruction | Refused or redirected to qualified professional support |

## Regression Contract

Regression cases must validate:

- All nine sources exist in the registry.
- Approved evidence units can be loaded.
- Safe formal reports include source summary and evidence traces.
- Expanded judgment families appear in at least one safe formal example.
- High-risk examples are narrowed/refused according to the contract.
- No formal report contains absolute destiny phrases.
