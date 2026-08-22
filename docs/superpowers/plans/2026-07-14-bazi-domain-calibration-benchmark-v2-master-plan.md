# Bazi Domain Calibration And Benchmark V2 Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement approved child plans task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Do not use sealed holdout data during routine implementation, do not create Feature 020 code before Feature 019 is closed, and do not use subagents unless the project owner explicitly authorizes them in the execution thread.

**Goal:** Deliver Feature 020 as a versioned internal domain calibration and benchmark program that measures expert stability, evaluates the unchanged engine, produces an Error Matrix, gates evidence-backed rule correction, and releases only from a final installed wheel and sealed evaluation.

**Architecture:** Feature 020 is split into a master roadmap plus child implementation plans because several phases depend on real outputs that do not exist at planning time: expert reliability, the initial Error Matrix, validation metrics, and sealed release evidence. The first executable child plan freezes the V2 protocol, loaders, hashes, split governance, privacy checks, and V1-to-V2 migration contract without changing domain rules. Later child plans are generated only after their gate artifacts exist.

**Tech Stack:** Python 3.12+, standard library dataclasses and `typing.Literal`, existing `mingli_engine` modules, package resources under `src/mingli_engine/data/domain_calibration/v2/`, pytest 8.4.1, mypy 1.17.1, Ruff 0.12.11, setuptools wheel verification.

---

## Scope Check

Feature 020 contains multiple empirically gated subsystems. A single detailed no-placeholder plan for the whole feature would either invent an Error Matrix that has not been measured or prescribe rule corrections before expert labels, adjudication, and baseline evaluation exist. This master plan therefore controls sequence, gates, and child-plan creation. The immediately executable child plan is:

- `docs/superpowers/plans/2026-07-14-bazi-domain-calibration-benchmark-v2-protocol-plan.md`

The following child plans are created only after their listed gate artifacts exist:

- Existing baseline relabeling plan: created after the protocol plan passes and Feature 019 artifacts are frozen.
- Expert workflow pilot plan: created after the 43 migrated assertions and protocol examples are available.
- Benchmark V1 governance plan: created after the pilot reliability report and schema freeze decision exist.
- Metrics and Error Matrix plan: created after Benchmark V1 split manifests and adjudicated labels exist.
- Evidence-guided rule correction plan: created only after a real Error Matrix ranks approved error clusters.
- Sealed release evaluation plan: created only after validation gates pass and a controlled sealed evaluator is designated.
- Governance closure plan: created after sealed release evidence exists.

## Fixed Feature Boundary

Feature 020 includes domain calibration, internal benchmark governance, expert workflow, metrics, Error Matrix, and gated rule-correction process. It does not add timezone lookup, true solar time, lunar input, deep annual interpretation, broad new spirit-star rules, Zi Wei Dou Shu, Liu Yao, model training, public benchmark claims, or Lao Yi narrative expression.

Feature 019 closure is a hard prerequisite. Execution stops if the package is not released through the approved 0.2.0 installed-wheel and baseline process, or if Feature 020 schema or rule changes have been folded into Feature 019.

## Master File Structure

- Create: `docs/superpowers/plans/2026-07-14-bazi-domain-calibration-benchmark-v2-protocol-plan.md`  
  First executable child plan. Freezes DTOs, canonical JSON, loaders, hashes, split governance, privacy checks, and migration protocol.
- Later create: `docs/superpowers/plans/2026-07-14-bazi-domain-calibration-benchmark-v2-existing-baseline-relabeling-plan.md`  
  Maps the existing 43 assertions into L0-L4 with acceptable alternatives, conditions, contradictions, school scope, label status, and the unchanged-engine initial Error Matrix.
- Later create: `docs/superpowers/plans/2026-07-14-bazi-domain-calibration-benchmark-v2-expert-pilot-plan.md`  
  Runs the 30-50 assertion pilot, Round A, Round B, adjudication, and expert reliability analysis.
- Later create: `docs/superpowers/plans/2026-07-14-bazi-domain-calibration-benchmark-v2-benchmark-v1-governance-plan.md`  
  Builds development, validation, sealed holdout, and challenge splits with access manifests and leakage invalidation rules.
- Later create: `docs/superpowers/plans/2026-07-14-bazi-domain-calibration-benchmark-v2-metrics-error-matrix-plan.md`  
  Computes per-layer metrics, expert target stability, high-confidence error audit, abstention audit, and grouped Error Matrix.
- Later create: `docs/superpowers/plans/2026-07-14-bazi-domain-calibration-benchmark-v2-rule-correction-plan.md`  
  Plans only the approved corrections backed by the real Error Matrix. It cannot be drafted from assumptions.
- Later create: `docs/superpowers/plans/2026-07-14-bazi-domain-calibration-benchmark-v2-sealed-release-plan.md`  
  Runs final installed-wheel sealed evaluation, exact version-set checks, benchmark card, and release decision.
- Later create: `docs/superpowers/plans/2026-07-14-bazi-domain-calibration-benchmark-v2-governance-closure-plan.md`  
  Performs full suite, static checks, privacy audit, package audit, Spec Kit closure, and final review.

## Standard Commands For Child Plans

Every pytest command in child plans uses this PowerShell prologue:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
```

Use these pinned tools unless a child plan narrows the target:

```powershell
uv run --with pytest==8.4.1 python -m pytest <targets> -q -p no:cacheprovider
uv run --with mypy==1.17.1 python -m mypy <targets> --follow-imports=skip
uv run --with ruff==0.12.11 ruff check <targets>
git diff --check
```

## Phase 0: Feature 019 Closure Gate

**Purpose:** Prevent Feature 020 from changing the 019 baseline or using draft 019 evidence as a release foundation.

**Gate checks:**

- `pyproject.toml` package version is `0.2.0`.
- Feature 019 is no longer only in `specs/_drafts/019-bazi-domain-validation-and-application-v1/`.
- Feature 019 final baseline and release decision are reproducible from a clean installed distribution.
- Existing candidate metrics are preserved as historical evidence, not rewritten for Feature 020.
- No Feature 020 schema, benchmark split, or rule correction is included in the 019 release.

**Exit result:** `Feature 020 may start` or `Feature 020 blocked by Feature 019`.

## Phase 1: Protocol And Migration

**Executable plan:** `docs/superpowers/plans/2026-07-14-bazi-domain-calibration-benchmark-v2-protocol-plan.md`

**Deliverables:**

- V2 benchmark, assertion, review, adjudication, metric, error, release, split, access, and migration DTOs.
- Strict canonical JSON loader with duplicate-key, non-finite, exact-field, hash, and privacy rejection.
- Split manifest and leakage invalidation governance.
- V1-to-V2 migration protocol that maps existing assertions without modifying rules.

**Exit gate:** exact-field, immutability, canonical hash, privacy, migration, invalid-input, type, lint, and package-resource tests pass.

## Phase 2: Existing Baseline Relabeling

**Child-plan creation gate:** Phase 1 is green and Feature 019 release artifacts are frozen.

**Deliverables:**

- Existing 43 assertions mapped to L0-L4.
- `acceptable_alternatives`, `conditions`, `explicit_contradictions`, `school_scope`, `label_status`, and `confidence_band` present for every migrated assertion.
- Unchanged-engine baseline run against the migrated assertions.
- Initial Error Matrix generated from actual results, with no rule modifications.

**Exit gate:** every migrated assertion has traceable evidence and a stable label status, or is explicitly marked as challenge/excluded according to the approved label model.

## Phase 3: Expert Workflow Pilot

**Child-plan creation gate:** Phase 2 produces migrated examples and an initial Error Matrix.

**Deliverables:**

- Expert eligibility, method scope, conflict disclosure, consent, and access declarations.
- 30-50 assertion pilot packets.
- Round A independent labels with no engine output.
- Round B randomized anonymous output acceptability reviews after Round A freeze.
- Independent adjudication that preserves alternatives and school conflict.
- Expert reliability report.

**Exit gate:** the label model is usable by the panel with acceptable reliability, or unstable targets are routed to challenge status and excluded from single-answer supervision.

## Phase 4: Benchmark V1 Governance

**Child-plan creation gate:** Phase 3 reliability report and schema freeze decision exist.

**Deliverables:**

- Development, validation, sealed holdout, and challenge split manifests.
- Approximately 300 assertions across required rule families where feasible.
- Coverage for positive, negative, counterexample, boundary, disagreement, and mandatory-abstention cases.
- Access manifests and split exposure status.
- Leakage invalidation rules and privacy declarations.

**Exit gate:** all counted assertions have valid expert review, adjudication, provenance, split role, and privacy status.

## Phase 5: Metrics And Error Matrix

**Child-plan creation gate:** Phase 4 split manifests and labels are frozen.

**Deliverables:**

- Expert metrics: raw agreement, weighted kappa where ordinal, Jaccard for multi-label sets, per-family and per-school agreement, pairwise distribution, high-disagreement count, abstention agreement, condition-set agreement, and Krippendorff alpha when supported.
- Engine metrics by L0-L4 and cross-layer gates.
- Error Matrix grouped by layer, family, school, complexity, scenario, confidence, evidence source, and split.
- Expert target stability report.
- High-confidence error audit and abstention audit.

**Exit gate:** every mismatch has one primary error code or is classified as an evaluation-target defect.

## Phase 6: Evidence-Guided Rule Correction

**Child-plan creation gate:** Phase 5 produces a real ranked Error Matrix.

**Allowed inputs:** development and validation splits, approved error clusters, governing evidence, school scope, counterexamples, and regression targets.

**Forbidden inputs:** sealed holdout contents, sealed holdout metric details that expose identities, and speculative corrections not backed by the Error Matrix.

**Exit gate:** validation thresholds pass without safety, traceability, deterministic, or school-attribution regression.

## Phase 7: Sealed Release Evaluation

**Child-plan creation gate:** Phase 6 validation gates pass and a controlled evaluator has sealed access.

**Deliverables:**

- Fresh final wheel built after all tracked benchmark assets are frozen.
- Installed-target sealed holdout execution outside the checkout.
- Exact equality for version set, benchmark manifest identity, resource hashes, metrics, and release decision.
- Benchmark card naming the benchmark as internal and documenting scope, limitations, expert composition, access controls, and prohibited interpretations.

**Exit gate:** all mandatory layer and cross-layer gates pass from the final installed distribution.

## Phase 8: Governance Closure

**Child-plan creation gate:** Phase 7 release decision exists.

**Deliverables:**

- Full test suite, mypy, Ruff, and `git diff --check`.
- Privacy audit and package audit.
- Spec Kit closure for Feature 020.
- Historical V1 metrics retained unchanged.
- Public-facing docs continue to identify the benchmark as internal unless external governance and reproducibility requirements have been met.

**Exit gate:** final review passes and Feature 020 can be closed without changing the Feature 019 historical baseline.

## Design Coverage Map

- Design sections 1-4 map to Scope Check, Fixed Feature Boundary, and Phase 0.
- Section 5 maps to Phase 1 protocol DTOs and Phase 5 metrics.
- Sections 6-8 map to Phase 1, Phase 2, and Phase 4.
- Sections 9-11 map to Phase 3 and Phase 5.
- Sections 12-13 map to Phase 5, Phase 7, and Phase 8.
- Sections 14-15 map to Phase 2, Phase 4, Phase 5, and Phase 6.
- Section 16 maps to Fixed Feature Boundary and Phase 5 L3/L4 unsupported-new-judgment checks.
- Section 17 maps to Phase 1 loaders, Phase 4 access manifests, Phase 7 benchmark card, and Phase 8 audit.
- Sections 18-21 map one-to-one to Phases 0-8 and the approved decisions above.

## Gated Items Not Planned As Implementation Yet

- Specific rule corrections: gated by the real Error Matrix from Phase 5.
- Sealed holdout execution details: gated by split governance and controlled evaluator designation.
- Expert target thresholds beyond the approved design: gated by pilot reliability results and versioned governance.
- Public benchmark language: gated by external governance, licensing, and independent reproducibility.

