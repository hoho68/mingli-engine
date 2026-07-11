# Report Release Readiness Design

## Goal

Create a maintainer-facing, machine-readable release gate that proves the enabled knowledge system produces stable, private, evidence-backed reports across the repository's representative anonymous scenarios.

## Approaches Considered

1. Add more assertions only to the existing integration test. This improves CI but gives maintainers no runtime release packet.
2. Fold the manifest matrix into `report_acceptance.py`. This reuses one command but mixes focused evidence acceptance with end-to-end example execution and makes failure diagnosis less clear.
3. Add a separate read-only `report_release.py` service above the existing acceptance gate. It validates and executes the tracked regression manifest, builds reports through production code, compares Markdown and HTML contracts, and returns a privacy-safe summary. This is the chosen approach.

## Input Matrix

The service consumes `examples/report-regression-cases.json` and its existing five tracked scenarios:

- two ordinary safe reports, covering automatic and externally verified chart sources;
- one general high-risk report that must remain narrowed and guarded;
- two exact-lifespan requests that must be rejected before report release.

Inputs remain synthetic repository fixtures. The summary never returns fixture paths, birth dates, birth times, places, gender, focus text, chart data, or rendered report bodies.

## Case Contracts

### Safe Report

Build the report in process, require safety approval, complete guarded evidence audit, 111 traced evidence units, ten rule families, four evidence-backed action tracks, sanitized reader text, and one complete Markdown and HTML rendering. Formal synthesis, integrated synthesis, and action reflection must be identical across both formats.

### Guarded High-Risk Report

Apply every safe-report check and additionally require the high-risk classifier to narrow rather than reject, preserve the traditional-risk boundary, prohibit exact event or lifespan output, and retain professional-support language.

### Rejected Request

Require classifier rejection with the manifest's expected category and withhold report construction and rendering.

## Aggregate Contract

`ReportReleaseSummary` exposes:

- stable `release_id=report_release_v1`;
- aggregate status and passed/total counts;
- safe, guarded, and rejected scenario counts;
- distinct report-output count for released report cases;
- nested `report_acceptance_v1` status and evidence counts;
- action-track count, privacy guardrails, and next action;
- one result per manifest case containing only case id, scenario type, status, output formats, checks, and guardrails.

Any invalid manifest, failed case, duplicate id, path escape, blocked report acceptance, missing evidence/action contract, unsafe output, or format mismatch must fail closed. A fully passing matrix inherits `ready_with_guardrails` while the known high-risk scope conflict remains open.

## Boundaries

- Read only tracked JSON fixtures and formal evidence through existing loaders.
- Do not parse raw materials or mutate source-library, 013, 012, or report inputs.
- Do not persist profiles, charts, reports, fingerprints, or feedback records.
- Do not expose fixture input paths or personal-profile fields in the summary.
- Do not resolve the known high-risk evidence conflict.

## Verification

Tests cover manifest validation, five-case execution, safe and guarded reports, exact-risk rejection, four action tracks, cross-format consistency, distinct outputs, acceptance dependency, fail-closed behavior, CLI serialization, privacy, quality scans, and the full repository regression.
