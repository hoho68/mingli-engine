# Report Release Readiness

The report release readiness packet is the final read-only operational gate for
enabling the report CLI. It runs the fixed anonymous scenario matrix in
`examples/report-regression-cases.json` through production input parsing, chart
calculation or external-chart loading, report construction, safety review, and
both renderers.

It depends on `report_acceptance_v1`. Acceptance certifies the formal evidence,
conflict, unavailable, and action-reflection baseline; release readiness proves
that representative tracked inputs preserve those contracts end to end.

## Enablement Command

Run:

```powershell
$env:PYTHONPATH='src'; uv run python -m mingli_engine.cli report-release-summary
```

Current expected packet:

- `release_id=report_release_v1`
- `release_status=ready_with_guardrails`
- `manifest_case_count=5`
- `passed_case_count=5`
- `failed_case_count=0`
- `safe_report_case_count=2`
- `guarded_report_case_count=1`
- `rejected_request_case_count=2`
- `distinct_report_output_count=3`
- `acceptance_baseline_id=report_acceptance_v1`
- `acceptance_status=ready_with_guardrails`
- `approved_evidence_count=111`
- `rule_family_count=10`
- `action_track_count=4`
- `next_action=enable_report_cli_with_guardrails`

The command exits `0` for `ready` or `ready_with_guardrails`. A blocked packet
is still written as JSON but exits `4`. Manifest read or validation errors exit
`1` without a partial report.

## Fixed Scenario Matrix

### Ordinary Safe Reports

Two cases cover automatic calculation and an externally verified chart. Both
must produce complete Markdown and HTML, expose the correct chart-source label,
trace the enabled evidence corpus, retain all four action-reflection tracks,
and remove internal signal markers.

### Guarded High-Risk Report

One general lifespan case must be narrowed rather than rejected. Both formats
must retain the traditional-risk boundary, non-exact language, professional
support boundary, and the stage-reflection stop condition.

### Rejected Requests

Two exact-lifespan cases must stop before chart/report construction and
rendering. The result must expose `lifespan_or_death_timing` through the safety
path and must not contain report content.

## Failure Interpretation

- `repair_report_acceptance`: the formal evidence or universal report baseline
  is blocked; repair that layer before inspecting release cases.
- `repair_report_release_matrix`: acceptance is usable but one or more tracked
  end-to-end cases failed.
- `enable_report_cli_with_guardrails`: all cases passed and the known high-risk
  conflict remains visible, so reports may be enabled only with current safety
  narrowing and rejection behavior.

The v1 loader requires all five stable case ids in order. Removing, renaming,
or replacing a case, changing its source-type contract, escaping the repository
path, or adding an unsupported command fails closed. Production CLI does not
accept an alternate manifest path.

All three report-producing cases must also retain distinct full-report
fingerprints. A collapsed output, missing or reordered reader section,
duplicated section, unexpected pre-report rejection, or renderer exception
blocks release with a privacy-safe case failure rather than exposing fixture or
exception details.

## Privacy And Mutation Boundary

The release packet returns only stable case ids, scenario types, statuses,
format labels, check results, aggregate counts, and guardrails. It does not
return fixture paths, birth dates, birth times, places, gender, focus text,
charts, reports, or output fingerprints.

Profiles, charts, reports, and fingerprints exist only in memory for the
duration of the command. The gate does not parse raw materials and does not
write source-library, 013, 012, fixture, or report files.
