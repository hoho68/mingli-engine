# Cross-Family Synthesis Design

## Goal

Add an evidence-constrained integrated narrative above the ten personalized formal conclusions so readers can understand how structure, selection, timing, and guardrails relate without treating the rule families as isolated verdicts.

## Approaches Considered

1. Prepend paragraphs inside `formal_synthesis`. This avoids a public field change but makes detailed conclusions and cross-family coordination inseparable in rendering and acceptance tests.
2. Add a graph dataclass with typed edges. This is machine-friendly but expands the public model substantially and risks implying causal relationships that the evidence does not establish.
3. Add one derived `integrated_synthesis: str` field to `Report`. A pure builder composes existing conclusions, chart signals, strengths, disagreements, and unavailable states into a separate reader layer. This is the chosen approach.

## Narrative Structure

The integrated synthesis contains five stable parts:

### Structure Thread

Coordinates `pattern_strength`, `five_element_balance`, `ten_god_relation`, `branch_interaction`, and `blind_image_method`. It states that these families form the current structural reading context and includes one sanitized chart signal from each available family.

### Selection Bridge

Coordinates `five_element_balance`, `useful_god_candidate`, `taboo_god_candidate`, and `remedy_boundary`. It frames useful/taboo/remedy output as conditional candidates read against the structural context, never as one final element or promised remedy.

### Timing Bridge

Coordinates `pattern_strength`, `branch_interaction`, `luck_cycle`, and `high_risk_signal`. It frames timing as a stage-level observation that must be checked against the natal structure and branch conditions. High-risk output remains non-exact and non-professional.

### Disagreement Coordination

Lists every disputed conclusion and its disagreement note. Disputed families stay visible and are never silently resolved, averaged, or promoted to a stronger conclusion.

### Unavailable Boundary

Names missing or unavailable rule families. When any required family is unavailable, synthesis status is `incomplete` and the narrative does not claim a complete chain.

## Status And Relationship Language

The builder maps report audit status to `完整`, `完整（含护栏）`, or `不完整`. Relationship phrases describe reading order, support context, and required conditions. They do not assert new metaphysical causation.

The current complete baseline must expose:

- a structural context relationship;
- a selection-context relationship;
- a timing-condition relationship;
- a high-risk/remedy guardrail relationship;
- visible disputed families and notes;
- no unavailable families.

## Report Integration

`Report.integrated_synthesis` follows `formal_synthesis`. Markdown and HTML render `综合脉络` after `正式知识综合` and before `结构分析`. Both report-wide safety scans include the field.

The report acceptance baseline adds an `integrated_cross_family_synthesis` check. It verifies the section is present once, contains all five parts, reflects current conflicts, contains no machine signal markers, and remains different across charts with different pattern, selection, branch, and timing signals.

## Boundaries

- No new formal conclusions, rule families, evidence units, or conflict resolutions.
- No source-library, 013, 012, or raw-material mutation.
- No exact event, lifespan, medical, legal, psychological, or financial conclusion.
- No automatic choice between disputed schools.
- No persistence of chart profiles or generated reports.

## Verification

Tests cover complete, guarded, disputed, and unavailable synthesis; public Report ordering; Markdown/HTML/CLI ordering; multi-chart differences; acceptance integration; safety language; quality scans; and the full repository regression.
