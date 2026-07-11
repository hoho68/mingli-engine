# Report Acceptance Baseline Design

## Goal

Create a deterministic, read-only acceptance baseline that answers whether the currently activated knowledge can produce release-ready reports with the required evidence, rendering, degradation, and safety behavior.

## Approaches Considered

1. Commit full Markdown and HTML golden files. This makes visual comparison easy but turns ordinary wording improvements into large, brittle snapshot updates.
2. Add only pytest scenario coverage. This is stable, but maintainers and automation cannot query one machine-readable readiness result.
3. Build a read-only acceptance summary backed by focused scenario tests and a JSON CLI. This gives one operational result while keeping detailed assertions in tests. This is the chosen approach.

## Architecture

Add `report_acceptance.py` as an independent read-only service. It builds reports from synthetic profiles, renders them through the production Markdown and HTML paths, evaluates four scenario contracts, and returns dataclasses from `models.py`. It must not write files, retain profiles, alter source metadata, or mutate 013/012 evidence.

`report-acceptance-summary` exposes the resulting dataclass as JSON through the existing CLI serializer. The active corpus remains the source of activation, evidence, and conflict counts.

## Scenario Matrix

### Ordinary Production Report

The report must be safety-allowed, activated with guardrails, audit-complete with guardrails, trace 111 approved evidence units, cover exactly ten rule families, and contain each formal-synthesis marker once.

Markdown and HTML must each contain the formal synthesis once, preserve the order from observation evidence to formal synthesis to structure analysis, and contain no external HTML resources.

### Conflict Guardrail

The report must expose the current open conflict, preserve at least one `disputed` conclusion, include its disagreement note, and retain non-deterministic high-risk boundary language.

### High-Risk Rejection

A synthetic exact-lifespan focus must fail the report safety review with `lifespan_or_death_timing`. No rendered report is accepted for this case.

### Unavailable Degradation

A controlled formal-evidence fixture with an unavailable high-risk conclusion must produce an incomplete synthesis, mark the family unavailable, retain the source body, and keep the non-deterministic professional-boundary notice. This validates the degradation contract without changing the active corpus.

## Summary Contract

`ReportAcceptanceSummary` contains:

- `baseline_id` with stable value `report_acceptance_v1`;
- `acceptance_status`: `ready`, `ready_with_guardrails`, or `blocked`;
- counts for total and passed scenarios;
- activation, audit, evidence, and rule-family totals;
- missing rule families and open conflicts;
- ordered `ReportAcceptanceCaseResult` entries;
- release guardrails and `next_action`.

Each case result contains `case_id`, `scenario_type`, `status`, named checks, and guardrails. A failed check blocks the summary. A fully passing baseline with open conflicts is `ready_with_guardrails`.

## Boundaries

- No raw material parsing, OCR, or new source intake.
- No source-library, 013 candidate, review-decision, promotion, or 012 evidence writes.
- Synthetic birth profiles exist only in memory and are not returned by the summary.
- No exact outcome, lifespan, medical, legal, psychological, or financial advice.
- The acceptance layer evaluates production behavior; it does not create new interpretation rules.

## Verification

Unit tests cover each scenario and blocked aggregation. Contract tests cover the CLI JSON. Existing report, safety, activation, learning-reference, materials-audit, and full repository tests remain required.
