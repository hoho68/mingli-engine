# Quickstart: Bazi Domain Validation And Application V1

## Scope And Claim

This in-progress feature adds a local Python and CLI application boundary and an agent-independent traditional-method conformance calibration workflow. It does not add HTTP, UI, persistence, external chart input, geographic timezone lookup, true solar time, predictive validation, scientific validation, or human expert review.

Birth-profile and report data are not stored by the engine. A terminal, caller, shell redirection, or host operating system may retain output.

## Activate The Explicit Draft

```powershell
$env:SPECIFY_FEATURE_DIRECTORY='specs/_drafts/019-bazi-domain-validation-and-application-v1'
Get-Content .specify/feature.json
```

Expected feature directory:

```text
specs/_drafts/019-bazi-domain-validation-and-application-v1
```

The non-numbered `_drafts` parent intentionally keeps open 019 tasks outside the completed feature scan. Do not move this package to `specs/019-bazi-domain-validation-and-application-v1/` before final Task 17 closure.

## Governance Baseline

Run before application implementation and after every governance-only change:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_project_completion.py tests/contract/test_project_completion_cli_contract.py -q -p no:cacheprovider
```

The historical feature IDs, counts, and 018 completion result must remain unchanged while 019 lives under `_drafts`.

## Development Verification

Use pinned tools for every implementation task:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_project_completion.py tests/contract/test_project_completion_cli_contract.py -q -p no:cacheprovider
uv run --with mypy==1.17.1 python -m mypy src/mingli_engine --follow-imports=skip
uv run --with ruff==0.12.11 ruff check src tests
```

Each implementation task begins with a focused failing test, reaches green with the minimum implementation, and reruns compatibility tests before commit.

Strict request objects contain every documented key exactly once. `request_id` is required even when its value is null, and `include_profile_in_report` is required with a boolean value. Missing keys, unknown keys, and duplicate keys are invalid.

## Synthetic Analysis Request

Use only synthetic data in examples and tests:

```json
{
  "schema_version": "real-use-request-v1",
  "request_id": "synthetic-analysis-001",
  "operation": "analysis",
  "profile": {
    "calendar_type": "gregorian",
    "birth_date": "1996-12-15",
    "birth_time": "09:30",
    "birthplace": "Synthetic UTC+08 Place",
    "gender": "unknown",
    "focus_topic": "traditional structural overview"
  },
  "authorization": {
    "subject_relation": "self",
    "attested": true
  },
  "options": {
    "report_format": null,
    "include_profile_in_report": false
  }
}
```

After the application boundary is implemented, invoke the typed operation:

```python
from mingli_engine import handle_real_use_json

response_bytes = handle_real_use_json(request_bytes)
```

Expected response properties are schema `real-use-response-v1`, operation `analysis`, status `ok`, one UUID4 trace ID, analysis result, safety decision, actual provenance, no raw profile metadata, and privacy retention `not_stored_by_engine`.

Also run the same synthetic request with `"request_id": null` to prove the required nullable field is accepted; deleting the key must produce `invalid_request`. Deleting `include_profile_in_report` or replacing its boolean with null must also produce `invalid_request`.

## Synthetic Report Request

For a report, set operation to `report` and format to `json`, `markdown`, or `html`:

```json
{
  "schema_version": "real-use-request-v1",
  "request_id": "synthetic-report-001",
  "operation": "report",
  "profile": {
    "calendar_type": "gregorian",
    "birth_date": "1996-12-15",
    "birth_time": "09:30",
    "birthplace": "Synthetic UTC+08 Place",
    "gender": "unknown",
    "focus_topic": "traditional structural overview"
  },
  "authorization": {
    "subject_relation": "authorized_other",
    "attested": true
  },
  "options": {
    "report_format": "markdown",
    "include_profile_in_report": false
  }
}
```

With inclusion false, scan the complete report object and rendered output to confirm all six raw and NFKC-normalized profile values are absent. With inclusion true, expect `contains_sensitive_profile=true` and escaped Markdown or HTML values.

For JSON, Markdown, and HTML separately, assert that source locators, source IDs, evidence IDs, and rule IDs remain traceable; the traditional-analysis and qualified-professional disclaimers are present; conclusions use conditional and uncertainty language; and `必定`, `注定`, `一定会`, `死定`, plus equivalent prohibited absolute wording, are rejected before output.

## Controlled Refusal Check

Set `attested` to false and invoke the same handler. Expected properties:

- status `refused`;
- error code `authorization_required`;
- request operation preserved;
- no chart, analysis, report, or renderer call;
- no engine-managed write or profile leak.

Use the packaged high-risk synthetic fixture `safety_high_risk_lifespan_refusal_001` to verify `unsafe_request` occurs before calculation.

## CLI Operation

After Task 8 implements the command:

```powershell
mingli-engine real-use --input tests/fixtures/application/valid_analysis_request.json
Get-Content tests/fixtures/application/valid_report_request.json -Raw | mingli-engine real-use --input -
```

The command emits exactly one JSON envelope to stdout. Exit status is 0 for `ok`, 3 for `refused`, and 1 for invalid input or controlled application error. Controlled outcomes keep stderr empty.

## Application Verification

The read-only application verifier executes fixed synthetic success, refusal, validation-failure, and internal-error scenarios through audited dependencies. Verify the exact deterministic map reports:

- every scenario present;
- contract status passed;
- privacy status passed;
- write count zero;
- leak count zero;
- overall status passed.

The verifier never writes a result artifact and never includes request or report bodies.

## Calibration Corpus Validation

After calibration models and corpus exist, run:

```powershell
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_models.py tests/unit/test_domain_calibration_corpus.py -q -p no:cacheprovider
```

Confirm at least 42 assertions; exact rule families `pattern_strength`, `five_element_balance`, `useful_god_candidate`, `taboo_god_candidate`, `ten_god_relation`, `branch_interaction`, `blind_image_method`, `luck_cycle`, `remedy_boundary`, and `high_risk_signal`; exact schools `ziping`, `liang_xiangrun`, and `duan`; required boundary cases; packaged synthetic input closure; exact canonical hashes; no real personal data; and no runtime dependency on `tests/`. Confirm the IDs equal `get_formal_interpretation_rule_families()` and `school_profiles.json` `enabled` rather than a calibration-local allowlist.

## Reviewer Procedure

For each frozen packet:

1. The controller computes canonical packet bytes and SHA-256.
2. Reviewer A runs in a fresh `fork_context=false` context with only packet bytes, tools disabled, filesystem disabled, peer labels absent, and engine output absent.
3. The controller validates and writes Reviewer A assignment and review records.
4. Reviewer B repeats the procedure in a different fresh context without Reviewer A identity or output.
5. A separate adjudicator receives frozen reviews, citations, and the claim boundary but no engine output.
6. Adjudication retains legitimate school alternatives and freezes expectations before engine execution.

This is procedural blindness. Documentation must not describe it as OS-level isolation or human expert review.

## Calibration And Release Summary

After Tasks 14 and 15 implement the runner and gates:

```powershell
python -m mingli_engine.cli domain-calibration-summary
```

The summary must expose the exact version set, conformance metrics, gate checks, blockers, claim boundary, and next action. Passing requires:

- 100% determinism, pillar agreement, school-disagreement recall, and mandatory abstention or refusal;
- `evidence_trace_completeness_rate=1.0`, `rule_trace_completeness_rate=1.0`, and `adjudication_coverage_rate=1.0`, each with a non-empty denominator;
- zero unsupported computation, dependency bypass, and silent school collapse;
- overall raw reviewer agreement at least 0.70;
- sufficiently sampled stratum agreement at least 0.60;
- adjudicated engine match at least 0.90;
- exact safety-critical match;
- passing application, privacy, packaging, no-retention, compatibility, and documentation checks.

The final installed run, final `calibration_baseline.json` metric snapshot, and recomputed release decision must carry the same exact `ExactVersionSet`: `application_version`, `engine_version`, `ruleset_version`, `provider_version`, `school_profile_version`, `fixture_version`, `evidence_baseline_id`, and `corpus_sha256`. Any missing, additional, or unequal field blocks release.

Task 14 produces only candidate objects for target `application_version=0.2.0`. Its optional serialized candidate exists only at the integration test's `tmp_path/calibration_baseline_candidate.json`; it must not update `src/mingli_engine/data/domain_calibration/calibration_baseline.json` and cannot produce a ready release while the installed package remains 0.1.0.

## Installed Wheel Verification

The release workflow builds a wheel without network access, inspects required JSON resources, installs into a temporary target, removes checkout `PYTHONPATH`, and runs chart analysis, evidence-backed report generation, calibration summary, and real-use CLI.

The installed calibration child receives its local `PackagingVerification`; it does not recursively build another wheel. Version advances to 0.2.0 only after every non-version gate passes. Then rebuild and install the wheel, execute a fresh final calibration run, generate a fresh final snapshot, update and freeze `src/mingli_engine/data/domain_calibration/calibration_baseline.json` through the controlled release writer, and recompute release from installed resources. Do not reuse the Task 14 candidate or cached Task 15 status.

Before accepting `ready_with_guardrails`, compare the final installed run, final baseline snapshot, and recomputed release `ExactVersionSet` values for exact equality and confirm all three report `application_version=0.2.0`.

## Final Verification

Use a 900000 ms controller timeout:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest -q -p no:cacheprovider
uv run --with mypy==1.17.1 python -m mypy src/mingli_engine --follow-imports=skip
uv run --with ruff==0.12.11 ruff check src tests
python -m mingli_engine.cli knowledge-activation-summary
python -m mingli_engine.cli report-acceptance-summary
python -m mingli_engine.cli report-release-summary
python -m mingli_engine.cli domain-calibration-summary
python -m mingli_engine.cli project-completion-summary
git diff --check
git status --short
```

Final closure moves the fully completed package to `specs/019-bazi-domain-validation-and-application-v1/`, checks every task and requirement item, updates project-completion baselines atomically, and documents the exact released version set.

## Manual Audit Checklist

- Request, response, nested DTO, error, and exit-code contracts match the V1 contract.
- Authorization and safety run before all calculation.
- No raw profile values appear in metadata, errors, logs, diagnostics, stderr, or redacted reports.
- The engine writes no request, response, report, hash, cache, database, or session artifact.
- Reviewer records identify `agent_independent` and disclose procedural blindness.
- Legitimate school differences remain explicit.
- Metrics are described as conformance rather than predictive accuracy.
- Installed execution uses package resources and no source-checkout path.
- Historical 018 completion remains unchanged until atomic 019 closure.
