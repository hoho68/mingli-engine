# Feature 020: Bazi Domain Calibration And Benchmark V2

**Status**: Approved design baseline  
**Date**: 2026-07-14  
**Depends on**: Feature 019 closure  
**Target release**: 0.3.0  
**Benchmark name**: Bazi Calibration Benchmark V1 (Internal)

## 1. Background

The project has crossed from free-form metaphysical text generation into a deterministic, traceable traditional-knowledge reasoning system. The current engine exposes ten formal rule families, three school adapters, structured evidence, stable application boundaries, privacy controls, safety refusals, and reproducible calibration artifacts.

The first calibration baseline is valuable because it makes uncertainty measurable. It must not be interpreted as a simple percentage of total domain ability. The current candidate metrics show two different realities:

- Engineering integrity is strong: determinism, pillar agreement, evidence trace completeness, rule trace completeness, adjudication coverage, school-disagreement recall, mandatory abstention, and safety-critical exact match are all 1.0.
- Domain alignment remains unresolved: reviewer raw agreement is 0.6744186046511628 and adjudicated acceptable-set engine match is 0.4418604651162791.

The 44.19% result means the current engine and current adjudication target differ substantially. The difference may originate in rule implementation, label design, school attribution, acceptable alternatives, missing conditions, or evaluation granularity. Feature 020 must identify those causes before expanding the engine's domain surface.

## 2. Strategic Sequence

The approved delivery sequence is:

1. Finish and freeze Feature 019 without adding new domain capabilities.
2. Deliver Feature 020 as a dedicated domain calibration and benchmark program.
3. Add temporal and calendrical policy capabilities in a later feature.
4. Deepen annual and period interpretation only after temporal policies are stable.
5. Add the controlled Lao Yi personality and narrative expression layer after the reasoning contract is calibrated.

Feature numbering should remain sequential unless a separate governance decision reserves a range:

- Feature 020: domain calibration and internal benchmark.
- Feature 021: timezone, historical timezone, solar-time, and day-boundary policy.
- Feature 022: annual and period interpretation expansion.
- Feature 023: controlled personality and narrative expression layer.

## 3. Goals

Feature 020 MUST:

1. Replace flat calibration assertions with layer-aware, school-aware, condition-aware, multi-label assertions.
2. Establish a versioned internal benchmark with development, validation, sealed holdout, and challenge splits.
3. Measure expert agreement before using expert labels as supervision.
4. Represent multiple acceptable interpretations without collapsing legitimate school differences.
5. Separate factual correctness, structural interpretation, semantic expression, and time-event language.
6. Produce an Error Matrix by layer, rule family, school, complexity, scenario, confidence, and error type.
7. Re-evaluate the existing engine against the frozen benchmark before changing rules.
8. Permit rule changes only when an error cluster has traceable benchmark and evidence support.
9. Preserve deterministic execution, evidence traceability, privacy, safety, and no-retention guarantees.
10. Produce version-bound release evidence that cannot be satisfied by development or validation data alone.

## 4. Non-Goals

Feature 020 MUST NOT:

- Add true solar time, geographic timezone lookup, daylight-saving handling, historical timezone lookup, or day-boundary policies.
- Add lunar-calendar input.
- Add new metaphysical systems such as Zi Wei Dou Shu or Liu Yao.
- Add new schools merely to increase coverage.
- Add broad new spirit-star or event-prediction rules.
- Build the Lao Yi consumer expression product.
- Train or fine-tune a generative model.
- claim scientific proof, causal validity, or real-world predictive accuracy.
- optimize directly against the sealed holdout split.
- treat expert disagreement as engine error without an adjudicated evaluation policy.
- rewrite Feature 019's historical baseline to make Feature 020 appear successful.

## 5. Reasoning Layers

Every benchmark assertion MUST declare exactly one primary reasoning layer.

### L0: Calendrical Facts

Examples include four pillars, solar-term boundary selection, hidden stems, sexagenary identifiers, and provider-derived start data. L0 is deterministic under an explicitly declared calendar and policy configuration.

L0 outputs MUST NOT contain school-dependent personality or event interpretation.

### L1: Derived Structural Facts

Examples include ten-god relations, five-element relations, root facts, branch combinations, clashes, harms, punishments, and deterministic structural counts.

L1 may depend on declared rule tables but MUST remain independently reproducible from L0 inputs.

### L2: School-Specific Structural Interpretation

Examples include strength tendency, pattern candidates, useful-god candidates, taboo-god candidates, school-specific priorities, blind-image structures, and remedy boundaries.

L2 MUST declare a school or an explicit cross-school scope. Multiple acceptable conclusions and disputed states are first-class outcomes.

### L3: Human-Meaning Expression

Examples include personality tendencies, work-style tendencies, relationship dynamics, resource pressure, and user-facing explanatory language.

L3 MUST be conditional, non-absolute, evidence-backed, and prohibited from introducing a new L0-L2 judgment.

### L4: Time-Event Interpretation

Examples include annual triggers, period-sensitive tendencies, and event-adjacent language.

L4 MUST NOT be evaluated or marketed as scientific prediction accuracy. Evaluation covers structural trigger correctness, condition completeness, uncertainty, abstention, evidence, and safety.

## 6. Benchmark Dataset Architecture

The internal benchmark MUST contain four immutable split roles.

### 6.1 Development Split

- Visible to maintainers and rule developers.
- May be used for debugging and local regression tests.
- Must never be reported as independent release evidence.

### 6.2 Validation Split

- Visible after the associated labels are frozen.
- Used for version comparison, threshold tuning, and error analysis.
- Must not be repeatedly relabeled to accommodate current engine output.

### 6.3 Sealed Holdout Split

- Hidden from rule implementers and routine test execution.
- Decrypted or supplied only to a controlled release evaluator.
- Used for final release metrics.
- Any exposure to engine developers invalidates the split version and requires a new holdout.

### 6.4 Challenge Split

- Contains expert-disputed, school-dependent, boundary, adversarial, and rare-combination cases.
- Used to evaluate disagreement handling, abstention, robustness, and explanation quality.
- Must not be mixed into a single headline accuracy score.

Each split manifest MUST record:

- benchmark version;
- split role;
- case and assertion IDs;
- canonical payload hashes;
- source and lineage hashes;
- creation and freeze timestamps;
- author, reviewer, adjudicator, controller, and engine access declarations;
- whether the split has ever been exposed to an implementation context;
- permitted metric and release uses;
- privacy declaration.

## 7. Assertion Model

The V2 assertion model MUST include:

- `assertion_id`
- `case_id`
- `layer`
- `rule_family`
- `school_scope`
- `claim_concepts`
- `polarity`
- `conditions`
- `required_evidence_ids`
- `acceptable_alternatives`
- `explicit_contradictions`
- `abstention_policy`
- `minimum_input_requirements`
- `confidence_band`
- `safety_critical`
- `complexity_tier`
- `scenario_tags`
- `benchmark_split`
- `label_status`

Free-form prose MAY accompany an assertion but MUST NOT be the only machine-evaluable label.

## 8. Label Status Model

Every adjudicated assertion MUST use one of these states:

- `consensus`: experts agree on a stable core label.
- `acceptable_set`: multiple conclusions are considered compatible.
- `school_dependent`: correctness requires a declared school scope.
- `expert_disputed`: no stable expert target exists.
- `insufficient_input`: a responsible system should abstain or reduce confidence.
- `excluded`: governance, privacy, evidence, or integrity checks prevent scoring.

`expert_disputed` cases MUST remain in the challenge corpus. They MUST NOT be silently deleted and MUST NOT penalize an engine that reports the dispute or abstains according to policy.

## 9. Expert Panel

The pilot panel SHOULD contain at least five qualified participants:

- two reviewers with documented Zi Ping practice;
- one reviewer with documented image-method or blind-school practice;
- one cross-school rule and evidence researcher;
- one safety and product-language reviewer.

Expert eligibility MUST require:

- a declared method or school scope;
- the ability to cite or explain rule grounds;
- acceptance of structured and blinded review;
- conflict-of-interest disclosure;
- consent to reliability measurement;
- no access to engine output before independent labeling.

The benchmark MUST report expert reliability. Expert labels are evidence, not unquestionable ground truth.

## 10. Expert Review Workflow

Review proceeds in two separate rounds.

### Round A: Independent Labeling

Experts receive canonical case facts, allowlisted evidence, declared assumptions, and the requested school scope. They do not receive engine output, peer labels, benchmark aggregate metrics, or implementation details.

They return structured labels, conditions, acceptable alternatives, contradictions, confidence, evidence references, and abstention decisions.

### Round B: Anonymous Output Acceptability

After Round A is frozen, experts receive randomized and anonymized candidate outputs. Candidate origin is hidden. Experts evaluate structural compatibility, missing conditions, overclaiming, school attribution, uncertainty, and safety.

Round B MUST NOT replace Round A. Its purpose is to measure whether different wording expresses an acceptable structure, not to anchor the gold label to engine prose.

### Adjudication

A separate adjudicator or panel receives frozen reviews and evidence. Adjudication MUST:

- preserve legitimate alternatives;
- identify the common core, if one exists;
- mark high disagreement explicitly;
- separate school conflict from factual error;
- prevent current engine output from influencing the target;
- record all changes from reviewer labels to adjudicated labels.

## 11. Expert Agreement Metrics

The benchmark MUST measure experts before measuring the engine.

Required expert metrics include:

- raw agreement;
- weighted kappa where labels are ordinal;
- Jaccard agreement for multi-label sets;
- per-family and per-school agreement;
- pairwise agreement distribution;
- high-disagreement case count;
- abstention agreement;
- condition-set agreement;
- Krippendorff's alpha when the sample and label structure support it.

Cases below the configured expert-consensus threshold MUST NOT become single-answer strong supervision.

## 12. Engine Metrics And Release Thresholds

Metrics MUST be reported separately by layer. A single aggregate score is insufficient.

### L0 Gates

- Release-critical cases: 100% exact match.
- Silent calendrical error count: zero.
- Required provenance and assumptions: 100% complete.

### L1 Gates

- Macro F1: at least 0.98.
- Each critical fact family: at least 0.95.
- Safety-critical and contradiction checks: 100% exact.

### L2 Gates

- Adjudicated acceptable-set match: at least 0.85.
- Each required rule family: at least 0.75.
- School attribution error rate: below the approved maximum.
- Silent school-collapse count: zero.

### L3 Gates

- Expert acceptability: at least 0.75.
- Unsupported new-judgment count: zero.
- Absolute or coercive language count: zero.
- Required uncertainty and condition expression: 100%.

### L4 Gates

- No scientific or real-world prediction-accuracy claim.
- Structural trigger correctness evaluated under L0-L2 rules.
- Condition, evidence, uncertainty, and abstention compliance: 100% for release-critical cases.
- Prohibited professional-advice and guaranteed-event output: zero.

### Cross-Layer Gates

- determinism rate: 1.0;
- evidence trace completeness: 1.0;
- rule trace completeness: 1.0;
- adjudication coverage for counted assertions: 1.0;
- dependency bypass count: zero;
- high-confidence error rate tracked separately and required to improve or remain below the approved threshold;
- benchmark leakage checks pass;
- sealed holdout identity and access manifest pass.

Threshold changes require a versioned governance decision and MUST NOT be made merely because a candidate release failed.

## 13. Error Taxonomy

Every mismatch MUST receive one primary error code and optional contributing codes.

Primary categories:

- `calendar_fact_error`
- `derived_fact_error`
- `rule_condition_missing`
- `rule_condition_invented`
- `school_misattribution`
- `acceptable_alternative_missed`
- `contradicted_consensus`
- `false_positive_conclusion`
- `false_negative_conclusion`
- `incorrect_abstention`
- `missing_abstention`
- `confidence_too_high`
- `confidence_too_low`
- `evidence_trace_error`
- `rule_trace_error`
- `expression_overreach`
- `safety_boundary_error`
- `evaluation_label_defect`
- `expert_target_unstable`

The Error Matrix MUST support grouping by layer, family, school, complexity, scenario, confidence, evidence source, and benchmark split.

## 14. Corpus Scale And Growth

Feature 020 uses staged growth.

### Pilot

- Re-label the existing 43 assertions under the V2 model.
- Add only enough cases to produce a 30-50 assertion expert workflow pilot.
- Validate that experts can apply the labels consistently.
- Revise the schema before any large labeling effort.

### Benchmark V1

- Target approximately 300 assertions.
- Each required rule family SHOULD have at least 30 countable assertions where feasible.
- Include positive, negative, counterexample, boundary, disagreement, and mandatory-abstention cases.
- Include simple, compound, and adversarial complexity tiers.
- Preserve school-specific strata rather than forcing equal answers.

Real personal cases are not required for Benchmark V1. Any future real-case study requires explicit authorization, de-identification, purpose limitation, retention policy, and separate governance. Real cases MUST NOT be described as proof of predictive validity.

## 15. Rule-Change Policy

The engine MUST be measured against the frozen benchmark before rules change.

Rule work is prioritized in this order:

1. L0 errors.
2. L1 errors.
3. High-confidence L2 errors.
4. Missing abstention or unsafe forced output.
5. Silent school collapse or school misattribution.
6. Missing conditions and unsupported semantic expansion.
7. Low-priority coverage improvements.

Every rule change MUST cite:

- the affected error cluster;
- benchmark case IDs from development or validation splits;
- governing evidence and school scope;
- expected metric movement;
- counterexamples and regression tests;
- proof that sealed holdout data was not consulted.

The project MUST NOT tune rules directly to sealed holdout outcomes.

## 16. Controlled Expression Boundary

Feature 020 defines but does not build the future expression contract.

The future product data flow is:

```text
calculation facts
-> school-aware structural conclusions
-> controlled human-meaning interpretation
-> personality and narrative expression
```

Each higher layer may summarize or rephrase lower-layer outputs but MUST NOT introduce a new lower-layer claim.

Example:

- L2: `Seven-killings structure is prominent; transformation conditions are disputed.`
- L3: `Traditional interpretation associates this structure with pressure and rule-bound environments, while outcomes depend on the stated transformation conditions.`
- Expression: `This kind of person is often shaped by demanding environments and may develop responsibility through pressure.`

The expression layer may improve readability and cultural value. It may not turn conditional structure into guaranteed life events.

## 17. Privacy, Safety, And Evidence Governance

Feature 020 inherits all Feature 019 controls and adds benchmark-specific protections:

- synthetic data by default;
- no real personal data in tracked benchmark assets;
- no raw personal values in logs, diagnostics, hashes, or release artifacts;
- no engine-managed case retention;
- canonical JSON and exact field validation;
- duplicate-key, non-finite, unknown-field, and hash-tampering rejection;
- allowlisted evidence packets;
- reviewer and adjudicator access manifests;
- explicit procedural-blindness limitations;
- no claim of human expert review until qualified human reviews actually exist;
- no public benchmark claim until method, licensing, and independent reproducibility are established.

## 18. Implementation Phases

### Phase 0: Close Feature 019

Deliverables:

- Feature 019 implementation and governance complete.
- Version 0.2.0 released through its approved wheel and baseline process.
- Existing candidate metrics preserved as the historical first domain baseline.
- No Feature 020 schema or rule change folded into the 019 baseline.

Exit gate: Feature 019 is formally closed and reproducible from a clean installed distribution.

### Phase 1: Freeze Feature 020 Protocol

Deliverables:

- V2 benchmark, assertion, expert review, adjudication, metric, error, and release DTOs.
- Exact canonical JSON envelopes and hashes.
- Split and leakage governance contract.
- Migration rules from V1 calibration artifacts.

Exit gate: exact-field, immutability, hash, privacy, and invalid-input tests pass.

### Phase 2: Re-label The Existing Baseline

Deliverables:

- Existing 43 assertions mapped to L0-L4.
- Multi-label acceptable sets, conditions, contradictions, and school scopes.
- V1-to-V2 comparison report.
- Initial Error Matrix over the unchanged engine.

Exit gate: every migrated assertion has traceable evidence and an explicit label status.

### Phase 3: Expert Workflow Pilot

Deliverables:

- Expert eligibility and conflict declarations.
- 30-50 assertion pilot packets.
- Round A labels, Round B acceptability reviews, and independent adjudication.
- Expert reliability report.
- Schema revisions frozen after pilot review.

Exit gate: the panel can apply the label model with acceptable reliability, or unstable areas are explicitly routed to challenge status.

### Phase 4: Build Benchmark V1

Deliverables:

- Approximately 300 assertions across required strata.
- Frozen development, validation, sealed holdout, and challenge manifests.
- Coverage and balance report.
- Leakage audit and access manifests.

Exit gate: all counted assertions have valid expert review, adjudication, provenance, and privacy status.

### Phase 5: Baseline And Error Matrix

Deliverables:

- Two deterministic engine runs.
- Per-layer, family, school, complexity, scenario, and confidence metrics.
- Expert agreement and target-stability metrics.
- Ranked Error Matrix.
- High-confidence error and abstention audit.

Exit gate: every mismatch is assigned an actionable error category or an evaluation-target defect.

### Phase 6: Evidence-Guided Rule Correction

Deliverables:

- Focused rule changes tied to approved error clusters.
- Counterexample and regression tests.
- Before/after validation metrics.
- No sealed holdout exposure.

Exit gate: required validation thresholds pass without regression in safety, traceability, or deterministic behavior.

### Phase 7: Sealed Release Evaluation

Deliverables:

- Fresh installed-wheel execution against the sealed holdout.
- Exact version-set and benchmark-manifest equality.
- Release decision with blockers and claim boundary.
- Benchmark card documenting scope, limitations, expert composition, and prohibited interpretations.

Exit gate: all mandatory layer and cross-layer gates pass from the final installed distribution.

### Phase 8: Governance Closure

Deliverables:

- Formal Feature 020 Spec Kit closure.
- Maintainer documentation and benchmark operator guide.
- Historical V1 metrics retained unchanged.
- Public documentation continues to identify the benchmark as internal unless external-governance requirements have been met.

Exit gate: full suite, static checks, privacy audit, package audit, and fresh whole-feature review pass.

## 19. Risks And Controls

### Benchmark Overfitting

Control: sealed holdout, access manifests, split invalidation on exposure, and rule-change evidence limited to development and validation splits.

### Expert Capture By One School

Control: declared school scopes, multiple reviewers, acceptable sets, school-dependent labels, and per-school metrics.

### Unstable Expert Targets

Control: expert agreement measurement, disputed status, challenge routing, and exclusion from single-answer supervision.

### Label Complexity

Control: a 30-50 assertion pilot before scaling, exact schemas, examples, reviewer training, and inter-rater analysis.

### Metric Gaming

Control: per-layer and per-family gates, high-confidence error reporting, no single aggregate release score, and versioned threshold governance.

### Expression Layer Leakage

Control: lower-layer claim IDs, derivation checks, unsupported-new-judgment count, and separate future product feature.

### Privacy Or Personal-Data Leakage

Control: synthetic benchmark by default, strict privacy fields, forbidden-key scans, no stable personal hashes, and independent privacy audit.

## 20. Definition Of Done

Feature 020 is complete only when:

1. Feature 019 is formally closed and remains reproducible.
2. The V2 layered calibration protocol is frozen and strictly validated.
3. Expert reliability is measured and unstable targets are explicitly classified.
4. Benchmark V1 has versioned development, validation, sealed holdout, and challenge splits.
5. The unchanged engine has a complete initial Error Matrix.
6. Rule corrections are tied to evidence-backed error clusters.
7. All required layer and cross-layer thresholds pass on a fresh sealed evaluation.
8. The final wheel reproduces benchmark identity, metrics, and release decision outside the checkout.
9. Safety, privacy, no-retention, evidence, and claim-boundary gates remain intact.
10. No documentation claims scientific prediction accuracy, universal school agreement, or external public-benchmark authority.

## 21. Approved Decisions

The following decisions are approved and are not open implementation placeholders:

- Feature 019 closes before Feature 020 changes begin.
- Feature 020 is calibration and benchmark work, not capability expansion.
- Evaluation uses L0-L4 layers.
- Multiple acceptable interpretations and expert disagreement are first-class states.
- The benchmark uses four split roles including a sealed holdout.
- Experts are evaluated for agreement before their labels supervise the engine.
- True solar time and timezone work are deferred to a later feature.
- The future Lao Yi expression layer cannot introduce new domain judgments.
- Benchmark V1 remains internal until external governance and reproducibility are established.
- Release evidence must come from a final installed distribution and sealed evaluation.
