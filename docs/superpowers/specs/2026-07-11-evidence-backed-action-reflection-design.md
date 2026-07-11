# Evidence-Backed Action Reflection Design

## Goal

Convert the existing personalized formal conclusions into low-risk action reflection items that are observable, recordable, reviewable, and stoppable while preserving the evidence and safety boundaries of every source rule family.

## Chosen Approach

Add an `ActionReflectionItem` dataclass and derive four stable items from the existing `ExpandedReportEvidence`. The report keeps a reader-facing `action_suggestions` string, but that string is rendered from the structured items instead of being assembled from a generic element-count sentence.

This keeps machine-auditable provenance without adding new metaphysical conclusions. It also lets unavailable or disputed evidence degrade an individual item instead of silently producing advice.

## Four Reflection Tracks

### Structure Calibration

Uses `pattern_strength` and `five_element_balance`. It asks the reader to compare sanitized structural signals with an observable situation and record where the signals fit or do not fit.

### Relationship Process Review

Uses `ten_god_relation`, `branch_interaction`, and `blind_image_method`. It focuses on interaction patterns and concrete process observations, never labels another person's character or predicts a relationship outcome.

### Selection Experiment

Uses `useful_god_candidate`, `taboo_god_candidate`, and `remedy_boundary`. It permits only a small, reversible observation experiment. It never selects one final element, sells a remedy, or promises an effect.

### Stage Review

Uses `luck_cycle` and `high_risk_signal`. It records stage themes and actual feedback without exact event or lifespan prediction. Medical, legal, psychological, and financial questions remain outside the report and require qualified professional support.

## Item Contract

Each `ActionReflectionItem` contains:

- stable `action_id` and reader title;
- `status`: `ready`, `ready_with_guardrails`, or `unavailable`;
- contributing `rule_families` and deduplicated `evidence_ids`;
- reader-facing `conditions` derived from sanitized chart signals;
- an `observation_prompt` and `feedback_metric`;
- an explicit `stop_boundary`.

An item is unavailable when any required family is missing, explicitly listed as unavailable, or has an unavailable conclusion. It is guarded when a contributing conclusion is disputed or the track is intrinsically sensitive. Unavailable items expose the gap and do not issue an action imperative.
An available conclusion without evidence ids is treated as unavailable for action purposes. Disputed conclusions append their disagreement note to the reader-facing conditions so the guardrail reason remains auditable.

## Report And Acceptance Integration

`Report.action_reflection_items` appears immediately before `action_suggestions`. Markdown, HTML, and CLI continue to render the existing `行动建议` section, now backed by the structured items. Report-wide safety checks include the rendered text.

The report acceptance baseline adds an `evidence_backed_action_reflection` check. It verifies four stable tracks, all ten rule families, non-empty evidence provenance for available items, safe stop boundaries, sanitized signals, reader rendering, and chart-specific output.

## Boundaries

- No new formal conclusions, evidence units, rule families, or conflict resolutions.
- No raw-material, source-library, 013, or 012 mutation.
- No exact event, lifespan, medical, legal, psychological, or financial instruction.
- No persistence of profiles, reflection responses, or generated reports.
- No claim that an observation prompt predicts or controls a result.

## Verification

Tests cover the four-track contract, evidence provenance, guarded and unavailable degradation, placeholder and internal-marker filtering, multi-chart differences, renderers, CLI, acceptance, safety suites, quality scans, and the full repository regression.
