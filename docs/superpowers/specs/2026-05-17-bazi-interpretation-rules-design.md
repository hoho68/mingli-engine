# 八字基础结构解读规则层 Design

## Goal

Add a conservative interpretation layer that turns an existing `BaziChart` into clearer baseline structure observations for the Markdown report.

The first version should help users understand what the chart contains without making fate claims. It should explain five-elements distribution, day-master context, ten-gods placement, and basic structural observations. It must not determine pattern, useful god, luck cycles, auspiciousness, lifespan, disaster timing, marriage certainty, professional advice, or paid remedy suggestions.

## Chosen Scope

We choose **Approach A: basic structure interpretation**.

Included:

- Five-elements distribution from visible stems, visible branches, and hidden stems
- Day-master explanation as the observation center
- Ten-gods placement summary from the four pillars
- Neutral structure observations such as concentrated, balanced, sparse, missing, or repeated signals
- Practical reflection prompts tied to the user's focus topic

Excluded:

- Pattern determination
- Useful-god determination
- Strength verdicts such as definitive strong/weak day master
- Luck-cycle and annual-cycle interpretation
- Good/bad fate verdicts
- Any absolute wording such as "必定", "注定", "一定会", or "死定"

## Reference Framing

The external `ming-li` reference repository organizes命理 work as staged, bounded reasoning: ethics, structured八字 steps, ten-gods combinations, patterns, and reporting boundaries. We follow that spirit but keep this feature narrower than a full命理推演 engine.

Reference materials:

- `ming-li` skill directory: https://github.com/Larkin0302/vantasma-toolkit/tree/main/skills/ming-li
- 十神组合 reference: https://github.com/Larkin0302/vantasma-toolkit/blob/main/skills/ming-li/references/12-%E5%85%AB%E5%AD%97-%E5%8D%81%E7%A5%9E%E7%BB%84%E5%90%88.md
- 八步范式 reference: https://github.com/Larkin0302/vantasma-toolkit/blob/main/skills/ming-li/references/09-%E9%9F%A6%E5%8D%83%E9%87%8C8%E6%AD%A5%E8%8C%83%E5%BC%8F.md

## Architecture

Add a focused interpretation unit between chart calculation and report rendering:

```text
BirthProfile -> calculate_bazi_chart -> BaziChart
BaziChart -> basic interpretation rules -> InterpretationSummary
BaziChart + InterpretationSummary -> Report -> Markdown
```

`calculate_bazi_chart` remains responsible for calendrical facts and conservative chart placeholders. The new interpretation layer consumes a complete `BaziChart`; it does not call `lunar_python`, parse dates, or modify the chart. The report schema uses the interpretation output to fill the existing summary sections with more specific, testable content.

## Proposed Components

### Interpretation Summary

Create a domain object that can carry:

- `five_elements_counts`
- `five_elements_summary`
- `day_master_summary`
- `ten_gods_summary`
- `structure_observations`
- `focus_suggestions`
- `limitations`

The object should be deterministic from `BaziChart`, so tests can assert exact phrases or exact structured counts.

### Five-Elements Rule

Count signals from:

- Heavenly stems
- Earthly branches
- Hidden stems

Visible stems and visible branches are treated as direct signals. Hidden stems are treated as supporting signals. The first version may use simple integer counts, but the report text should explain that the counts are observation aids rather than strength verdicts.

### Day-Master Rule

Use `chart.day_master` to produce a short explanation:

- Identify the day master
- Explain that it is the observation center
- Avoid saying the day master is inherently good or bad
- Avoid definitive strong/weak claims

### Ten-Gods Rule

Summarize ten-gods already present in the four pillars:

- Which pillar each ten-god appears in
- Repeated ten-gods, if any
- Missing ten-gods, if the rule has enough information

The first version does not interpret combinations as fate outcomes.

### Structure Observations

Generate conservative statements:

- "某元素信号较集中"
- "某元素信号较少"
- "四柱中可观察到某十神重复"
- "当前规则层只做基础结构观察"

No fixed destiny, no event prediction, no professional advice.

## Report Integration

Use the interpretation layer to improve these existing report fields:

- `five_elements_summary`
- `ten_gods_summary`
- `structure_analysis`
- `personality_tendencies`
- `strengths_and_issues`
- `action_suggestions`

The Markdown section structure should remain stable. Existing CLI users should not need new flags.

## Error Handling

If the chart is incomplete or not exactly four pillars, the report builder already rejects it. The interpretation layer should also raise a stable error when it receives malformed chart data, so failures do not produce misleading partial analysis.

If a chart has unknown stems, branches, elements, or ten-gods, the first version should use an explicit limitation note rather than guessing.

## Testing Strategy

Use TDD and focused tests:

- Unit tests for five-elements counting
- Unit tests for day-master summary
- Unit tests for ten-gods placement summary
- Unit tests for conservative language and limitations
- Report-schema tests proving the report uses interpretation output
- Integration tests proving `calculate-report` includes the new sections and still blocks unsafe topics
- Safety tests proving no prohibited absolute phrases appear

At least the existing fixed charts should produce stable interpretation text.

## Acceptance Criteria

- A safe automatic report includes richer five-elements and ten-gods summaries than the current placeholder-like output.
- The report states that the interpretation is basic structure observation, not pattern/useful-god/luck-cycle determination.
- The report keeps existing source disclosure, disclaimer, safety review, and Markdown section structure.
- Unsafe focus topics still return a safety response instead of a formal report.
- All generated formal report text avoids prohibited deterministic phrases.

## Open Decisions Resolved

- Depth: choose basic structure only.
- Delivery surface: integrate into existing `calculate-report` and `generate-report` report output, no new user-facing command.
- Domain boundary: no pattern, useful-god, or luck-cycle judgment in this feature.
- Tone: practical, reflective, and conservative.
