# Data Model: 报告分层阅读体验优化

## Layered Report

Represents the final Markdown report organized for staged reading.

**Fields and relationships**:

- `title`: Existing report title.
- `disclaimer`: Existing safety disclaimer.
- `quick_guide`: Short three-to-five bullet reading guide.
- `chart_card`: Existing birth/profile summary.
- `assumptions`: Existing source and calculation assumptions.
- `four_pillars_summary`: Existing four-pillar facts.
- `five_elements_summary`: Existing element observation text.
- `ten_gods_summary`: Existing ten-god placement text.
- `structure_analysis`: Existing structure observation text, without excessive duplicated boundary prose.
- `personality_tendencies`: Existing day-master observation wording.
- `interpretation_boundaries`: Explicit boundary layer text.
- `strengths_and_issues`: Existing reflection prompt text.
- `phase_overview`: Existing phase overview wording.
- `action_suggestions`: Existing action reflection wording.
- `glossary`: Existing terminology notes.
- `ethics_reminder`: Existing ethics reminder.
- `safety_review`: Existing safety review result.

**Validation rules**:

- Formal reports must include `disclaimer`, `quick_guide`, source assumptions, boundary text, and ethics reminder.
- `quick_guide` must contain three to five Markdown bullet lines.
- `interpretation_boundaries` must include boundary language for pattern, useful god, and luck-cycle or annual-cycle conclusions.
- No formal report text may include prohibited absolute destiny phrases in unsafe contexts.

## Quick Guide

A short near-top reading guide.

**Content rules**:

- Includes source or confidence status.
- Includes one primary structure observation.
- Includes one conservative boundary reminder.
- Includes a focus-topic cue when a safe focus topic is available.
- Uses bullet formatting rather than long paragraphs.

## Reading Layer

A named group of related report content.

**Required layers**:

- `第一层：基础资料`
- `第二层：结构观察`
- `第三层：解读边界`
- `第四层：行动反思`

**Ordering rule**:

The required layers must appear after `快速导读` and in the listed order.

## Section Label

A plain label that tells the reader the role of a paragraph.

**Allowed labels**:

- `观察`
- `依据`
- `边界`
- `提示`

**Usage rule**:

Labels are required only where they clarify interpretation sections. Factual source sections do not need all labels.
