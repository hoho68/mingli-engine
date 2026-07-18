# Feature 019 Evidence-Trust Recovery Design

**Feature:** `019-bazi-domain-validation-and-application-v1`
**Date:** 2026-07-18
**Status:** Awaiting written-spec review
**Selected direction:** Evidence first; scope isolation before implementation

## 1. Purpose

Feature 019 has a usable V1 application boundary and substantial release-governance
infrastructure, but its current calibration runner does not prove what its metrics
claim to measure. It reads only the application response status, derives candidate
values from the assertion's expected values, copies required trace identifiers into
the actual result, and measures pillar agreement from fixture metadata rather than
calculated pillars.

This recovery makes calibration evidence truthful before attempting release closure.
The first deliverable may report worse metrics than the historical run. That is an
acceptable and expected outcome: a truthful failing result is progress, while a
self-confirming passing result is not release evidence.

## 2. Decision

Use an additive, versioned observation layer between the real application response
and calibration evaluation:

```text
synthetic fixture
  -> real V1 request bytes
  -> handle_real_use_json()
  -> validated application snapshot
  -> code-owned observation projectors
  -> actual observations indexed by field_path
  -> assertion/adjudication comparison
  -> metrics and maturity observations
```

Observation projectors receive application output only. They never receive
`acceptable_values`, `acceptable_statuses`, `required_rule_ids`,
`required_evidence_ids`, reviewer labels, or adjudication decisions. Comparison with
those artifacts happens only after the actual observation has been frozen.

Historical V1 corpus, reviewer, adjudication, run, and metric artifacts remain
immutable. Corrected evidence uses a new schema/suite identifier and cannot silently
replace or rewrite a historical result.

## 3. Alternatives Considered

### 3.1 Patch the current helper in place

Rejected. The assertion paths such as
`analysis.rule_families.pattern_strength` do not exist in the public response, and
the current analysis response has no claim-specific evidence trace. A generic JSON
path helper would therefore either fail or keep fabricating data.

### 3.2 Extend the public V1 response with calibration-only fields

Rejected for this recovery. It would change the already-frozen public application
contract and couple user-facing serialization to a test harness. Claim-level runtime
trace improvements can be added later through an explicitly versioned application
contract.

### 3.3 Add an independent observation projection

Selected. It preserves the public V1 contract, makes provenance of each actual value
reviewable, and allows unsupported families or missing traces to remain honestly
`not_computed` or incomplete.

## 4. Scope

### 4.1 Included in the first recovery stage

1. Protect all existing dirty work in both current worktrees.
2. Create a new isolated branch and worktree from closure commit `fb8ea64`.
3. Add a response-only calibration observation model and projector.
4. Replace assertion-derived candidate results with observation-derived results.
5. Replace metadata-only pillar agreement with actual-pillar comparison against a
   packaged, immutable reference.
6. Add adversarial tests proving that output tampering changes calibration results.
7. Recompute candidate metrics without producing release-ready evidence.
8. Mark historical self-confirming metrics as non-conclusive in documentation while
   preserving their bytes and hashes.

### 4.2 Explicitly excluded from the first recovery stage

- No Feature 020 implementation or fixture changes.
- No raw PDF or external-material ingestion.
- No release version bump, tag, push, or public release.
- No rewriting reviewer or adjudication records to improve a metric.
- No final baseline or `internal_source_grounded_ready` decision.
- No broad mypy cleanup unrelated to touched calibration modules.
- No deletion of build products or user files without separate user authorization.

## 5. Isolation and Change Safety

Implementation runs in:

```text
E:\命理演绎\.superpowers\worktrees\019-evidence-trust-closure
```

That path is already covered by the repository's `.superpowers/` ignore rule. The
new branch is created from `fb8ea64`, not from either dirty worktree:

```text
codex/019-evidence-trust-closure
```

The current worktrees remain untouched:

- `E:\命理演绎`: existing V2 prototype and external materials;
- `E:\mingli-019-closure`: existing materials-audit and build changes.

Before implementation, record branch, HEAD, tracked diff names, untracked names,
and a content hash inventory for every dirty tracked file. After worktree creation,
verify those inventories are unchanged.

## 6. Components

### 6.1 `CalibrationObservationV1`

A frozen observation contains only values derived from an actual application run:

```text
field_path
status
values
rule_ids
evidence_ids
failure_codes
source_response_sha256
```

Rules:

- `field_path` comes from a code-owned authoritative projector registry.
- `values` are canonical tokens derived from response fields.
- `rule_ids` come only from serialized calculation or report trace fields.
- `evidence_ids` come only from claim-specific response trace fields.
- Aggregate application provenance is not copied into every observation.
- Missing claim-specific trace produces an empty tuple and an explicit
  `claim_evidence_trace_missing` failure code.
- Values are sorted, deduplicated, bounded strings.

### 6.2 Application snapshot

Each unique fixture is executed once. The snapshot validates:

- root response is an object;
- status is exactly `ok`, `refused`, or `error`;
- an `ok` response contains analysis result, chart, calculation, and provenance;
- a refused response has no result and retains safety categories;
- an error response fails the calibration run rather than becoming a domain result;
- the canonical response SHA-256 is recorded before projection.

Unsupported fixture encodings that cannot form a V1 request produce an explicit
boundary snapshot without calling the application. That state is determined from
the fixture input, never from the assertion kind.

The runner accepts an injected application callable for tests:

```python
execute_candidate_calibration(
    version_set,
    *,
    application_runner=handle_real_use_json,
)
```

This makes tamper testing explicit and avoids hidden monkeypatch dependencies.

### 6.3 Authoritative projectors

The initial registry covers these paths:

| Field path | Actual response source |
| --- | --- |
| `analysis.rule_families.pattern_strength` | calculation strength and pattern results |
| `analysis.rule_families.five_element_balance` | chart five-element summary and strength result |
| `analysis.rule_families.useful_god_candidate` | calculation useful-god results |
| `analysis.rule_families.ten_god_relation` | exposed and hidden ten-god facts |
| `analysis.rule_families.branch_interaction` | calculation branch relations |
| `analysis.rule_families.luck_cycle` | calculation luck-cycle result |
| `analysis.school_views.<school_id>` | matching calculation school result |

The following V1 paths have no truthful output in the frozen public application
response and therefore remain `not_computed` until a later, versioned capability
adds them:

- `analysis.rule_families.taboo_god_candidate`
- `analysis.rule_families.blind_image_method`
- `analysis.rule_families.remedy_boundary`
- `analysis.rule_families.high_risk_signal`, except that an actual safety refusal is
  retained as a refusal observation rather than a computed domain value.

Projectors may report a family as computed only when the corresponding serialized
engine structure exists and passes structural validation. They may not infer
`positive`, `counterexample`, `boundary`, `abstention`, `school agreement`, or
`school disagreement` from assertion metadata.

### 6.4 Canonical actual values

Values encode observed structures, not expected labels. Examples:

```text
strength.status=<value>
strength.label=<value>
pattern.id=<pattern_id>
five_element.<element>=<count>
useful_god=<method>|<element>|<rank>|<status>
ten_god.exposed=<pillar>|<stem>|<ten_god>
branch_relation=<type>|<branches>|<state>|<rule_id>
luck_cycle.start=<years>|<months>|<days>
school=<school_id>|<reasoning_status>|<preferred_patterns>|<preferred_elements>
```

Numbers use a fixed canonical representation. Text is Unicode-preserving and has
no locale-dependent formatting. Order in the serialized engine result cannot alter
the sorted observation tuple.

Legacy abstract acceptable values such as `pattern_strength:supported` are not
manufactured by the projector. Consequently, legacy match rates may fall. Those
rates are retained as evidence-maturity observations, not application-release gates.

### 6.5 Trace extraction

Rule IDs are collected from the exact calculation structures contributing to an
observation. A family does not inherit rule IDs from unrelated calculation sections.

The current V1 analysis response exposes aggregate evidence provenance but not
claim-specific evidence IDs. Aggregate IDs must not be presented as claim-specific
proof. Until claim-level evidence is exposed by a later source-trace stage,
`actual_evidence_ids` remains empty and trace completeness honestly fails.

This recovery therefore separates two facts:

1. the engine produced a structural result under particular rule IDs;
2. the public response currently does or does not prove the source evidence for that
   individual result.

### 6.6 Pillar reference

Create an additive packaged reference under a new corrected calibration suite. It
contains, for each provider-agreement case:

```text
fixture_id
source_fixture_id
source_fixture_sha256
expected_pillars: year, month, day, hour gan-zhi
```

The reference is copied from the existing verified synthetic fixture with its source
hash recorded. Pillar agreement compares actual response
`result.chart.pillars[].gan_zhi` to these four expected values. It never counts a
filename, fixture hash, or successful status as pillar agreement.

The installed-wheel check verifies that the reference is packaged and that its
source hash and payload hash are stable.

## 7. Evaluation Order

For every assertion:

1. Locate the already-built observation by fixture and `field_path`.
2. Copy actual status, values, rule IDs, evidence IDs, and projector failure codes.
3. Only then load the independent adjudication target.
4. Compute match and append mismatch codes.
5. Never mutate the observation during comparison.

The observation index is hashable and its canonical hash is included in the run ID.
Two identical application responses must produce identical observations and run IDs.
Different response payloads that change an observed field must produce different
observations and run IDs even when the top-level status is unchanged.

## 8. Adversarial Invariants

The implementation is not accepted unless all of these tests pass:

1. Replace the whole `result` payload while preserving `status=ok`: observations and
   run ID must change or the run must fail structural validation.
2. Change `acceptable_values`: actual observations must remain byte-for-byte equal.
3. Change required rule/evidence IDs: actual trace IDs must remain unchanged.
4. Remove one actual rule ID from the engine response: rule completeness must fall.
5. Remove claim evidence trace: evidence completeness must fall.
6. Change one actual pillar: pillar agreement must fall.
7. Reorder semantically unordered response lists: canonical observation must remain
   deterministic where the underlying contract treats order as irrelevant.
8. Pass malformed application JSON: the run must fail closed with
   `CalibrationProtocolError`.
9. Pass a refused safety request: no domain value may be reported as computed.
10. Ensure the observation module never imports reviewer or adjudication models and
    never reads calibration acceptable/required fields.

## 9. Error Handling

- Invalid response structure: fail the run closed.
- Application status `error`: fail the run closed.
- Unsupported input fixture: explicit boundary snapshot.
- Safety refusal: explicit refusal observation, no calculated values.
- Missing projector: `not_computed` with `unsupported_observation_path`.
- Missing claim trace: keep the value, return empty trace IDs, and record a trace
  failure; do not discard the structural observation.
- Duplicate field paths or duplicate actual tokens: reject registry construction or
  canonicalize as specified; never silently choose one conflicting value.

## 10. Test Strategy

### Unit tests

- observation model validation and canonicalization;
- one projector test per supported family;
- unsupported-family and refusal behavior;
- response structural validation;
- rule/evidence trace isolation;
- actual-pillar comparator;
- observation independence from expected labels.

### Integration tests

- execute the packaged synthetic corpus through the real V1 JSON application;
- run twice and prove deterministic observations;
- execute all adversarial invariants;
- recompute metrics and record the truthful result without asserting historical pass
  thresholds;
- verify historical artifacts are byte-for-byte unchanged.

### Packaging tests

- corrected-suite resources are present in the wheel;
- resource hashes match the package manifest;
- execution succeeds from an installed target outside the checkout;
- no test fixture or repository-relative path is required at runtime.

## 11. Stage Exit Criteria

The evidence-trust recovery stage is complete only when:

- implementation occurs on the isolated closure branch;
- both original dirty worktree inventories remain unchanged;
- all adversarial invariants pass;
- tampering with the result payload no longer produces an identical run;
- assertion expectations cannot alter actual observations;
- trace IDs are never copied from required IDs;
- pillar agreement compares four actual pillars;
- historical artifacts remain unchanged and are documented as non-conclusive;
- focused unit, integration, packaging, Ruff, mypy-on-touched-files, and
  `git diff --check` gates pass;
- a fresh audit finds no self-confirming path from expected labels into actual output.

Passing this stage does not mean Feature 019 is releasable. It establishes a
trustworthy foundation for the next stage: claim-level source tracing and the four
source-grounded application hard gates.

## 12. Beginner-Facing Checkpoint Protocol

At the end of every stage, report exactly:

1. what was completed in plain language;
2. the commands or artifacts that prove it;
3. remaining risks and whether the project is currently safe to release;
4. the single next action required from the user.

The user is never asked to choose implementation details. Separate approval is
requested only for irreversible actions, deleting user files, publishing, version
selection, or accepting a product/governance trade-off.
