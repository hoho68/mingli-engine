# Research: Bazi Domain Validation And Application V1

## Decision: Publish an independent V1 wire schema

**Rationale**: Application callers need a stable request and response contract that does not confuse wire compatibility with engine, ruleset, provider, evidence, or school-profile versions.

**Alternatives considered**:

- Expose existing internal dataclasses directly: rejected because private fields and internal evolution would become public compatibility obligations.
- Reuse the engine version as schema version: rejected because protocol and engine changes have different lifecycles.
- Add an HTTP API first: rejected because network hosting, identity, persistence, and deployment risks are outside V1.

## Decision: Parse bounded bytes before constructing trusted DTOs

**Rationale**: A strict parser can reject oversized, malformed, duplicate-key, deeply nested, non-finite, unknown-field, and unsupported inputs before any partial object is trusted.

**Alternatives considered**:

- Accept ordinary decoded dictionaries: rejected because duplicate keys and exact byte limits are already lost.
- Use permissive forward-compatible unknown fields: rejected because V1 security and privacy behavior depends on an exact object shape.
- Accept external charts or calculation bundles: rejected because this would bypass same-process calculation provenance.

## Decision: Require structural authorization before lexical safety

**Rationale**: Self-use or authorized-other attestation is a clear machine-enforceable boundary. Safety classification then narrows high-risk focus topics before chart calculation.

**Alternatives considered**:

- Infer authorization from free text: rejected because lexical inference cannot establish consent.
- Calculate first and refuse later: rejected because unauthorized or unsafe requests must not invoke calculation.
- Treat illegal relationships as authorization refusals: rejected because values outside the two literals are schema errors.

## Decision: Keep calculation, analysis, and report construction in one request scope

**Rationale**: Existing weak process-local provenance can bind the original chart and calculation bundle when no serialized or cross-request object is accepted.

**Alternatives considered**:

- Accept a serialized `CalculationBundle`: rejected because reconstruction cannot preserve identity-bound trust.
- Split chart calculation and reporting into separate commands: rejected because callers could substitute or replay intermediate values.
- Introduce durable provenance storage: rejected because persistence is unnecessary and conflicts with the no-retention goal.

## Decision: Use explicit serializers and whole-object redaction

**Rationale**: Exact serializers prevent private configuration from leaking. Redacting every explicit report field before rendering covers metadata and legacy sections that chart-card-only redaction would miss.

**Alternatives considered**:

- Use generic `dataclasses.asdict()`: rejected because it silently expands the public surface when private fields are added.
- Redact serialized JSON with text replacement: rejected because it is structure-blind and can corrupt content.
- Redact only the profile card: rejected because profile values can appear in nested report fields and rendered formats.

## Decision: State no engine retention precisely

**Rationale**: The engine can guarantee that it creates no request logs, response logs, stable profile hashes, files, caches, database rows, or sessions. It cannot control terminal scrollback, callers, shell redirection, or host operating systems.

**Alternatives considered**:

- Claim that data is never stored anywhere: rejected because that overstates control beyond the process boundary.
- Add encrypted local history: rejected because session persistence is explicitly out of scope.
- Add stable birth-data hashes for diagnostics: rejected because hashes create linkable sensitive identifiers.

## Decision: Package every runtime JSON resource and test the installed wheel

**Rationale**: Repository tests can pass while built distributions omit JSON data. Manifest inspection and source-isolated installed subprocesses prove the shipped artifact rather than the checkout.

**Alternatives considered**:

- Read resources from repository-relative paths: rejected because installed packages do not contain the checkout layout.
- Test wheel contents only: rejected because presence does not prove runtime loaders use installed resources.
- Let installed calibration recursively build another wheel: rejected because only the outer release gate should own wheel construction.

## Decision: Use canonical immutable calibration envelopes

**Rationale**: Exact keys, canonical record ordering, canonical record SHA-256, sorted upstream hashes, and read-only loaders make corpus, packet, review, adjudication, run, and baseline drift observable.

**Alternatives considered**:

- Allow loaders to repair order or hashes: rejected because validation would mutate evidence of drift.
- Store review output in free-form Markdown: rejected because metrics and independence checks require strict fields.
- Hash entire files including formatting: rejected because the contract needs a stable semantic hash of canonical records.

## Decision: Use two independent agent reviews and separate adjudication

**Rationale**: Reviewers receive identical allowlisted packet bytes in separate fresh contexts without tools, filesystem, peer labels, or engine output. Separate adjudication resolves clerical issues while preserving legitimate school differences.

**Alternatives considered**:

- Reuse the implementation agent as sole reviewer: rejected because it cannot support an independent-calibration claim.
- Show current engine output to reviewers: rejected because labels would be anchored to implementation behavior.
- Collapse disagreement by majority: rejected because two reviewers cannot establish a school-independent universal answer.
- Describe the procedure as OS sandboxing: rejected because the approved process guarantees procedural isolation only.

## Decision: Measure conformance, not prediction

**Rationale**: Synthetic fixtures, tracked evidence, and reviewer labels can test deterministic structural and school-specific method conformance. They cannot establish causal, scientific, or real-world predictive validity.

**Alternatives considered**:

- Label the result predictive accuracy: rejected because no outcome dataset or scientific validation design exists.
- Call reviewers human experts: rejected because reviewer kind is exactly `agent_independent`.
- Suppress disagreement metrics: rejected because school variation is part of the domain boundary.

## Decision: Gate release on exact versions and mandatory thresholds

**Rationale**: Calibration results are meaningful only for the engine, ruleset, provider, school profiles, fixtures, evidence baseline, and corpus that produced them. Mandatory privacy, packaging, safety, and compatibility gates prevent a strong metric from masking an unsafe artifact.

**Alternatives considered**:

- Reuse cached release results after version changes: rejected because the installed artifact must be recomputed.
- Average safety-critical failures into overall match: rejected because every safety-critical assertion must match exactly.
- Update the historical 018 status when 019 fails: rejected because 019 adds a new application and calibration release label rather than rewriting prior operational evidence.
