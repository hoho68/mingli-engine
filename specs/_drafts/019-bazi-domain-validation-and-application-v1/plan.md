# Implementation Plan: Bazi Domain Validation And Application V1

**Branch**: `codex/019-bazi-domain-validation-application` | **Date**: 2026-07-13 | **Spec**: [spec.md](spec.md)

**Input**: Approved design in `docs/superpowers/specs/2026-07-13-bazi-domain-validation-and-application-v1-design.md` and execution plan in `docs/superpowers/plans/2026-07-13-bazi-domain-validation-and-application-v1.md`.

## Summary

Publish a strict V1 Python and JSON CLI application boundary over the existing deterministic Bazi engine, enforcing authorization, safety, whole-report privacy, same-process provenance, explicit serialization, and no engine retention. Add a separately governed calibration corpus with two procedurally blinded independent agent reviews, adjudication, exact conformance metrics, installed-wheel verification, and version-bound release gates. Keep the open Spec Kit under `specs/_drafts/` so the 001-017 completion baseline and historical 018 result remain unchanged until final closure.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Python standard library, existing `mingli_engine` modules, `lunar-python==1.4.8`; no HTTP, UI, database, or new runtime service dependency.

**Storage**: Tracked canonical JSON under `src/mingli_engine/data/domain_calibration/`; application requests and responses have no engine-managed persistence.

**Testing**: pytest 8.4.1, mypy 1.17.1, Ruff 0.12.11, wheel build and installed-target subprocess tests.

**Target Platform**: Local Python library and CLI, Windows first and portable to supported Python environments.

**Project Type**: Python library and CLI package.

**Performance Goals**: Strictly bound request parsing to 32 KiB and depth 8; bound serialized responses to 1 MiB; keep calibration deterministic and read-only.

**Constraints**: Gregorian dates 1901-01-01 through 2099-12-31; documented UTC+08 wall-time assumption; no true solar time; no external chart or serialized calculation input; no raw profile leakage; no engine-managed retention; no real personal calibration data; no scientific or predictive claims.

**Scale/Scope**: At least 42 adjudicated assertions covering rule families `pattern_strength`, `five_element_balance`, `useful_god_candidate`, `taboo_god_candidate`, `ten_god_relation`, `branch_interaction`, `blind_image_method`, `luck_cycle`, `remedy_boundary`, and `high_risk_signal`, plus schools `ziping`, `liang_xiangrun`, and `duan`, mandatory boundary and refusal cases, two valid independent reviews per counted assertion, and one exact installed distribution version set. The sole authorities are `get_formal_interpretation_rule_families()` and `src/mingli_engine/data/calculation/school_profiles.json` `enabled`.

## Constitution Check

*GATE: Must pass before Phase 0 research and be re-checked after Phase 1 design.*

- Evidence-based traditional analysis: PASS. The application exposes source-backed traditional analysis and the calibration claim is limited to traditional-method conformance.
- Transparent calculation and evidence boundary: PASS. Strict input, calculation, analysis, reporting, serialization, evidence traces, and calibration records remain separate and versioned.
- Expanded high-risk boundaries: PASS. Authorization and safety checks run before calculation; prohibited professional-advice, coercive, lifespan, and remedy requests are refused.
- Reviewable classical evidence and reports: PASS. Major outputs carry rule, evidence, version, school, confidence, disagreement, and limitation information.
- Test-first quality gates: PASS. Every implementation phase begins with focused failing tests and closes with pytest, type, lint, compatibility, or installed-wheel verification as applicable.
- Privacy: PASS. The engine stores no birth profile or generated report and calibration contains only synthetic non-personal inputs.

## Project Structure

### Documentation (this feature)

```text
specs/_drafts/019-bazi-domain-validation-and-application-v1/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- tasks.md
|-- contracts/
|   |-- real-use-v1-contract.md
|   `-- domain-calibration-v1-contract.md
`-- checklists/
    `-- requirements.md
```

### Source Code (repository root)

```text
src/mingli_engine/
|-- application_models.py
|-- application_inputs.py
|-- application_serialization.py
|-- application_service.py
|-- application_reports.py
|-- application_validation.py
|-- packaging_validation.py
|-- domain_calibration.py
|-- domain_calibration_models.py
|-- domain_calibration_release.py
|-- cli.py
|-- project_completion.py
`-- data/domain_calibration/
    |-- calibration_cases.json
    |-- input_fixtures.json
    |-- calibration_assertions.json
    |-- calibration_citations.json
    |-- reviewer_packets.json
    |-- reviewer_a_assignments.json
    |-- reviewer_a_reviews.json
    |-- reviewer_b_assignments.json
    |-- reviewer_b_reviews.json
    |-- adjudication.json
    `-- calibration_baseline.json

tests/
|-- unit/
|-- contract/
|-- integration/
|-- safety/
`-- fixtures/application/
```

**Structure Decision**: Extend the existing package with narrow modules for request models, parsing, serialization, service orchestration, report privacy, application verification, packaging verification, calibration models, calibration execution, and release gating. Keep immutable calibration data inside package resources so installed execution never depends on repository fixtures.

## Complexity Tracking

No constitution violations. Two application entry points are required because typed Python callers and untrusted JSON callers have different trust boundaries. Separate reviewer and adjudicator artifacts are required to support the approved independent-conformance claim. HTTP, UI, persistence, network services, and broad source ingestion are deliberately excluded.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Use a strict frozen V1 envelope independent of engine and ruleset versions.
- Require every root and nested request field; `request_id` is required and nullable, while `include_profile_in_report` is required and boolean.
- Perform authorization and safety before any calculation.
- Keep chart, analysis, report, and provenance in one process and request.
- Redact the complete report object before rendering.
- Verify all package resources from an installed wheel outside the checkout.
- Use canonical JSON envelopes and immutable review records.
- Use two procedurally blinded independent agents followed by separate adjudication.
- Measure traditional-method conformance rather than predictive accuracy.
- Bind release status to exact versions and preserve the historical 018 result.
- Share one exact eight-field `ExactVersionSet` unchanged across run, baseline snapshot, and release decision.

## Phase 1: Design Summary

Detailed models, contracts, and operator workflow are defined in:

- [data-model.md](data-model.md)
- [contracts/real-use-v1-contract.md](contracts/real-use-v1-contract.md)
- [contracts/domain-calibration-v1-contract.md](contracts/domain-calibration-v1-contract.md)
- [quickstart.md](quickstart.md)

## Approved Task Mapping

The headings in [tasks.md](tasks.md) map one-to-one to approved implementation-plan Tasks 0 through 17. `T001-T005` belong to Task 0, `T006-T011` to Task 1, and each subsequent heading states its exact approved Task number through Task 17. The word "phase" is reserved here for Spec Kit research/design stages and is not used as a second implementation numbering system.

Every implementation task follows red-green-refactor. The detailed dependency-ordered checklist is [tasks.md](tasks.md).

## Calibration Release Sequence

Task 14 computes a candidate run, candidate metric snapshot, and test-local candidate baseline for target `application_version=0.2.0`; it does not mutate `src/mingli_engine/data/domain_calibration/calibration_baseline.json` and cannot create a final release decision. Task 15 proves all non-version gates while version/final-baseline checks remain blocked. Task 16 advances `pyproject.toml` to 0.2.0 and builds a pre-baseline wheel used only to execute the fresh final calibration run and snapshot. The controlled release writer then updates and freezes the tracked final baseline. That pre-baseline wheel is discarded as release evidence. The workflow builds a second, final wheel after the baseline freeze, installs it into a new empty temporary target, and recomputes all release evidence from that final installation without cached Task 14 or Task 15 results.

The final installation must verify its wheel manifest, calibration summary, release decision, resource SHA-256 map, source isolation, and exact equality of the final `CalibrationRun.version_set`, final baseline `MetricSnapshotV1.version_set`, and `CalibrationReleaseDecision.version_set`. Runtime and Task 14 remain read-only with respect to the tracked final baseline; the pre-baseline wheel never counts as publication or release evidence.

## Release Gates

- Application contract, privacy, safety, no-retention, packaging, and compatibility checks pass.
- Determinism, pillar agreement, `evidence_trace_completeness_rate`, `rule_trace_completeness_rate`, `adjudication_coverage_rate`, school-disagreement recall, and mandatory abstention or refusal equal 1.0.
- Unsupported-computed, dependency-bypass, and silent school-collapse counts equal zero.
- Overall reviewer raw agreement is at least 0.70; each stratum with at least 10 paired observations is at least 0.60.
- Adjudicated acceptable-set engine match is at least 0.90 and every safety-critical assertion matches exactly.
- Every counted assertion has two valid independent reviews.
- Documentation repeats the claim boundary, procedural blindness limitation, no-engine-retention wording, exclusions, and exact version set.
- `CalibrationRun.version_set`, baseline `MetricSnapshotV1.version_set`, and `CalibrationReleaseDecision.version_set` are exactly equal and contain only `application_version`, `engine_version`, `ruleset_version`, `provider_version`, `school_profile_version`, `fixture_version`, `evidence_baseline_id`, and `corpus_sha256`.
- Final equality and packaging gates are evaluated only from the post-baseline final wheel installed into a fresh target after the Task 16 run, snapshot, and controlled baseline freeze; neither Task 14 candidates nor the Task 16 pre-baseline wheel satisfy this gate.
- JSON, Markdown, and HTML report tests each prove source and evidence traceability, disclaimer presence, non-absolute uncertainty language, and rejection of prohibited absolute destiny wording.

## Verification Commands

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_project_completion.py tests/contract/test_project_completion_cli_contract.py -q -p no:cacheprovider
uv run --with mypy==1.17.1 python -m mypy src/mingli_engine --follow-imports=skip
uv run --with ruff==0.12.11 ruff check src tests
git diff --check
```

Final full-suite shell calls use a 900000 ms controller timeout.

## Post-Design Constitution Check

- Evidence-based traditional analysis: PASS. Claims remain bounded to auditable traditional-method conformance.
- Transparent calculation and evidence boundary: PASS. Data models and contracts expose exact inputs, outputs, traces, versions, and disagreement states.
- Expanded high-risk boundaries: PASS. Structural authorization, lexical safety, post-build safety, and exact refusal cases are contract requirements.
- Reviewable classical evidence and reports: PASS. Canonical citations, packet hashes, reviews, adjudication, rule IDs, and evidence IDs form a complete audit chain.
- Test-first quality gates: PASS. Tasks specify failing tests before implementation and fresh verification before each commit.
- Privacy: PASS. Whole-object redaction, bounded diagnostics, no-write tests, installed isolation, and synthetic calibration data are explicit gates.
