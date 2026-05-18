# Data Model: 第二层结构观察表达优化

## ElementDistribution

Represents countable five-element signals already derived from a chart.

Fields:

- `direct_counts`: Counts from visible stems and branches.
- `hidden_counts`: Counts from hidden stems.
- `total_counts`: Direct plus hidden counts for each five element.
- `dominant_elements`: Elements with the highest total count when countable signals exist.
- `missing_elements`: Elements with zero total count.
- `unknown_signals`: Signals that cannot be mapped to a known five element.

Validation rules:

- Counts must remain numeric and unchanged by wording polish.
- Missing elements must mean “not visible in countable signals,” not “real-world ability is missing.”
- Unknown signals must be disclosed conservatively and not interpreted.

## TenGodPlacement

Represents where a readable ten-god relationship appears.

Fields:

- `ten_god`: The readable ten-god value.
- `pillars`: Pillar display names where that relationship appears.

Validation rules:

- Empty, placeholder, or unknown ten-god values should not be treated as readable signals.
- Repeated ten-god values may be summarized as repeated observation signals, not as destiny conclusions.

## BasicInterpretationSummary

Represents the interpretation text consumed by report assembly.

Fields relevant to this feature:

- `five_elements_summary`: Reader-facing five-element observation prose.
- `ten_gods_summary`: Reader-facing ten-god observation prose.
- `structure_observations`: Reader-facing basic structure observation prose.
- `limitations`: Existing boundary text that must continue to prohibit overinterpretation.

Validation rules:

- `five_elements_summary` must keep direct, hidden, and total counts visible.
- `ten_gods_summary` must keep pillar ten-god relationships visible when readable.
- `structure_observations` must describe distribution and concentration as observation clues.
- None of these fields may introduce fate verdicts, auspiciousness claims, useful-god conclusions, strength conclusions, luck-cycle readings, or event predictions.

## Markdown Structure Observation Layer

Represents the final `第二层：结构观察` block seen by users.

Content requirements:

- Includes the existing day-master observation.
- Includes smoother five-element observation text.
- Includes smoother ten-god observation text.
- Includes smoother basic structure observation text.
- Keeps existing 004 heading order.
- Keeps 005 reader-facing labels elsewhere in the report unchanged.

State transitions:

1. Chart data is counted into `ElementDistribution`.
2. Interpretation functions create `BasicInterpretationSummary`.
3. Report assembly maps summary fields into the report schema.
4. Markdown renderer places the fields under `第二层：结构观察`.
5. Safety checks and language checks must still pass before completion.
