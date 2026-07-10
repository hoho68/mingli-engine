# Formal Knowledge Synthesis Design

## Goal

Turn the ten activated formal rule families into a reader-facing report section without weakening the existing evidence, activation, conflict, or safety boundaries.

## Chosen Approach

Add one derived `formal_synthesis: str` field to `Report`. Build it from `ExpandedReportEvidence` and `ReportEvidenceAudit`, then render it once between observation evidence and the existing basic structure analysis.

This is preferred over appending more text to `evidence_notes`, because the audit trail and reader narrative have different jobs. It is also preferred over introducing another nested public dataclass because the report's visible sections are currently plain strings and the underlying machine-readable conclusions already remain available in `expanded_evidence`.

## Content Structure

The synthesis groups all formal conclusions in stable reading order:

1. `structure_and_relations`: `pattern_strength`, `five_element_balance`, `ten_god_relation`, `branch_interaction`, `blind_image_method`.
2. `selection_and_adjustment`: `useful_god_candidate`, `taboo_god_candidate`, `remedy_boundary`.
3. `timing_and_risk`: `luck_cycle`, `high_risk_signal`.

Each conclusion shows its reader-facing title, translated strength, evidence count, supported body, and any disagreement note. Evidence identifiers remain in `evidence_notes` and `report_evidence_audit`; the synthesis does not duplicate them.

## Status And Guardrails

- `complete` becomes a complete synthesis.
- `complete_with_guardrails` becomes a complete synthesis with explicit conflict and high-risk boundaries.
- `incomplete` names missing or unavailable rule families and never presents itself as complete.
- Sensitive and high-risk groups state that timing and risk signals are conditional cultural interpretation, not exact event, lifespan, medical, legal, psychological, or financial conclusions.
- The synthesis is included in the report-wide safety scan.

## Rendering And Contract

Markdown and HTML add one subsection named `正式知识综合` after `观察依据` and before `结构分析`. CLI report generation inherits this behavior through the existing renderers. The public `Report` contract adds `formal_synthesis` immediately after `evidence_notes`.

## Verification

Tests must prove that the synthesis:

- covers every enabled rule family exactly once across the three groups;
- carries disputed and unavailable states into reader-facing boundaries;
- appears once and in the same position in Markdown and HTML;
- participates in safety review;
- preserves the 111-unit audit and the current activation status;
- passes focused, safety, quality, and full regression suites.
