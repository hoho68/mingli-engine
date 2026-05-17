# Data Model: 八字基础结构解读规则层

## ElementDistribution

Represents observed five-elements signals from a chart.

**Fields**:

- `direct_counts`: counts from visible heavenly stems and earthly branches
- `hidden_counts`: counts from hidden stems
- `total_counts`: direct plus hidden counts
- `dominant_elements`: elements with the highest observed total count
- `missing_elements`: elements with zero observed total count
- `unknown_signals`: chart values the rule layer could not map to an element

**Validation rules**:

- Counts must include all five elements: 木, 火, 土, 金, 水.
- Unknown signals must be reported as limitations, not guessed.
- Hidden-stem counts must not be presented as a full strength model.

## TenGodPlacement

Represents where a ten-god appears in the four pillars.

**Fields**:

- `ten_god`: ten-god label from the chart
- `pillars`: pillar display names where the ten-god appears

**Validation rules**:

- Blank or unknown ten-gods are omitted from placement summaries and recorded as limitations.
- Repeated ten-gods may be described as repeated signals, not fate outcomes.

## BasicInterpretationSummary

Structured output from the basic interpretation layer.

**Fields**:

- `element_distribution`: `ElementDistribution`
- `five_elements_summary`: user-facing text about direct and hidden element signals
- `day_master_summary`: user-facing text explaining the day master as observation center
- `ten_gods_summary`: user-facing text about ten-gods placement
- `structure_observations`: list of neutral observations about concentration, absence, or repetition
- `focus_suggestions`: list of practical, non-deterministic reflection prompts
- `limitations`: list of explicit boundaries for this rule layer

**Validation rules**:

- Must not contain prohibited absolute destiny phrases.
- Must not determine pattern, useful god, day-master strength verdict, luck cycles, annual cycles, auspiciousness, or fate outcomes.
- Must be deterministic for the same chart input.

## InterpretedReport

Existing `Report` output enriched by `BasicInterpretationSummary`.

**Relationships**:

- Consumes existing `BaziChart`.
- Uses `BasicInterpretationSummary` to fill existing report fields.
- Keeps existing source disclosure, disclaimer, safety review, and Markdown sections.

**Validation rules**:

- Must remain blocked by existing safety review when focus topic is unsafe.
- Must include limitation language for the basic interpretation layer.
- Must support both automatically calculated charts and externally verified charts.
