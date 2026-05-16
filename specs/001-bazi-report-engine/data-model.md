# Data Model: 八字知识与报告引擎 MVP

## BirthProfile

Represents user-provided birth context.

**Fields**:

- `calendar_type`: `gregorian` or `lunar`
- `birth_date`: date string supplied by user
- `birth_time`: exact time, traditional时辰, or approximate text
- `birthplace`: user-provided place text
- `gender`: user-provided gender value used for domain rules
- `focus_topic`: overall, career, wealth, relationship pattern, current phase, or custom safe topic

**Validation rules**:

- Full reports require all fields.
- If `calendar_type` is unknown, ask for clarification.
- If `birth_time` is unknown or approximate, allow a brief safe response but not a full report.
- If `birthplace` is too vague for stated assumptions, ask for a more specific place.

## ChartSource

Represents provenance and assumptions for chart data.

**Fields**:

- `source_type`: `manual`, `external_verified`, or `future_calculated`
- `source_note`: human-readable provenance
- `calendar_assumption`: how the date was interpreted
- `timezone_assumption`: timezone used or stated as unknown
- `solar_terms_assumption`: whether month/year boundaries follow solar terms
- `true_solar_time_applied`: boolean or unknown
- `confidence`: high, medium, or low

**Validation rules**:

- Full reports must include `source_type` and `source_note`.
- Reports must show assumptions to the reader.
- Low-confidence sources must mark downstream findings as uncertain.

## Pillar

Represents one八字 pillar.

**Fields**:

- `name`: year, month, day, or hour
- `heavenly_stem`: one天干
- `earthly_branch`: one地支
- `hidden_stems`: list of藏干
- `ten_god`:十神 relation relative to日主 when known
- `element`: five-element classification when known

**Validation rules**:

- A complete `BaziChart` requires four pillars.
- The day pillar identifies the日主.

## BaziChart

Represents structured chart facts.

**Fields**:

- `birth_profile`: `BirthProfile`
- `chart_source`: `ChartSource`
- `pillars`: four `Pillar` values
- `day_master`:日主
- `five_elements_summary`: counts or qualitative distribution
- `ten_gods_summary`:十神 distribution and notable relations
- `strength_assessment`:日主旺衰 candidate with support notes
- `pattern_candidates`: candidate格局 values with uncertainty
- `useful_god_candidates`:用神/喜忌 candidates with rationale
- `luck_cycle_summary`:大运/流年 phase summary

**Validation rules**:

- Full report generation requires complete pillars and chart source.
- If strength, pattern, or useful-god values conflict, mark findings uncertain.
- The chart object stores facts and candidates, not final fatalistic prose.

## InterpretationFinding

Represents one traceable interpretive conclusion.

**Fields**:

- `title`: short conclusion title
- `category`: structure, personality, strength, issue, phase, action, or glossary
- `claim`: safe-language conclusion
- `supporting_refs`: references to birth profile, chart source, pillar, summary, or assumption
- `uncertainty`: high, medium, or low
- `safe_action`: suggested next action or reflection

**Validation rules**:

- Every major report conclusion must have at least one supporting reference.
- Claims must avoid prohibited absolute phrases.
- High uncertainty must be visible in the report.

## SafetyReviewResult

Represents ethical and language review.

**Fields**:

- `allowed`: boolean
- `red_line_categories`: list of triggered red lines
- `prohibited_phrases`: list of detected absolute-language phrases
- `disclaimer_present`: boolean
- `redirect_message`: safe alternative when blocked

**Validation rules**:

- Formal reports require `allowed = true`.
- Formal reports require `disclaimer_present = true`.
- Any triggered red-line category blocks or redirects output.
- Any prohibited phrase blocks or rewrites output before delivery.

## Report

Represents the final Markdown artifact.

**Fields**:

- `title`
- `disclaimer`
- `chart_card`
- `assumptions`
- `four_pillars_summary`
- `five_elements_summary`
- `ten_gods_summary`
- `structure_analysis`
- `personality_tendencies`
- `strengths_and_issues`
- `phase_overview`
- `action_suggestions`
- `glossary`
- `ethics_reminder`
- `safety_review`

**Validation rules**:

- All sections are required for a full report.
- Brief safe responses may omit full sections but must not present themselves as a full report.
- The rendered Markdown must keep assumptions and disclaimer visible.
