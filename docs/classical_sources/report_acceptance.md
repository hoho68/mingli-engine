# Report Acceptance Baseline

The report acceptance baseline is the final read-only gate between knowledge
activation and release use. It evaluates production report construction,
formal synthesis, evidence tracing, Markdown and HTML rendering, conflict
guardrails, high-risk rejection, and unavailable-evidence degradation.

It does not parse source material, create interpretation rules, mutate the
source library, write 013 candidate or review records, promote evidence, or
change the 012 formal corpus.

## Machine-Readable Check

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -m mingli_engine.cli report-acceptance-summary
```

Current expected baseline:

- `baseline_id=report_acceptance_v1`
- `acceptance_status=ready_with_guardrails`
- `case_count=4`
- `passed_case_count=4`
- `activation_status=enabled_with_guardrails`
- `report_audit_status=complete_with_guardrails`
- `approved_evidence_count=111`
- `rule_family_count=10`
- `traced_evidence_unit_count=111`
- `missing_rule_families=0`
- `open_conflicts=conflict_high_risk_scope_001`
- `next_action=release_reports_with_guardrails`

Any failed case changes the aggregate acceptance status to `blocked`.

## Scenario Matrix

### Ordinary Production Report

Builds a report from an in-memory synthetic profile. The case verifies report
safety, knowledge activation, evidence audit, the 111-unit trace count, all ten
formal-synthesis markers, and consistent Markdown and HTML reading order.

### Conflict Guardrail

Confirms that the current open high-risk scope conflict remains visible, at
least one conclusion remains disputed, disagreement notes reach the formal
synthesis, and the non-deterministic professional boundary remains present.

### High-Risk Rejection

Uses an in-memory exact-lifespan focus. The case passes only when report safety
rejects the request with `lifespan_or_death_timing` and rendering is withheld.

### Unavailable Degradation

Uses a controlled in-memory formal-evidence fixture. The case verifies that an
unavailable high-risk conclusion produces an incomplete synthesis, remains
marked unavailable, preserves its boundary body, and does not lose the
professional-advice limitation.

## Privacy And Mutation Boundary

Synthetic profiles are never returned by the summary and are not persisted.
The acceptance command performs no writes. Its result is an operational health
packet, not new evidence and not an authorization to alter source or intake
records.
