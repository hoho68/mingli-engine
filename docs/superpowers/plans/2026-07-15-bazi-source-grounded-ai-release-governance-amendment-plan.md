# Feature 019 Source-Grounded AI Release Governance Amendment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` in a separate implementation thread. Do not execute this plan in the writing thread. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement source-grounded internal release governance for Feature 019 without rewriting legacy calibration artifacts or mixing in Feature 020.

**Architecture:** Add typed governance models and legacy projection first, then maturity policy, raw-result hard-gate producers, installed-wheel evidence, release state transitions, approval binding, and user-facing outputs. Release decisions are derived from typed evidence and previous state; historical calibration data remains immutable.

**Tech Stack:** Python 3.12, dataclasses, `argparse`, `importlib.resources`, existing `mingli_engine` domain calibration, application validation, report, CLI, and packaging patterns.

---

## Planning Thread Boundary

This writing thread may only modify:

`E:\命理演绎\docs\superpowers\plans\2026-07-15-bazi-source-grounded-ai-release-governance-amendment-plan.md`

Future implementation happens in:

`E:\mingli-019-closure`

Before execution, read these approved materials by absolute path from `E:\命理演绎`:

- `E:\命理演绎\AGENTS.md`
- `E:\命理演绎\docs\superpowers\specs\2026-07-15-bazi-source-grounded-ai-release-governance-amendment-design.md`
- `E:\命理演绎\specs\_drafts\019-bazi-domain-validation-and-application-v1\plan.md`
- `E:\命理演绎\docs\superpowers\plans\2026-07-15-bazi-domain-validation-and-application-v1-closure-plan.md`
- `E:\命理演绎\docs\superpowers\specs\2026-07-14-bazi-domain-calibration-benchmark-v2-design.md`
- `C:\Users\lei\.codex\superpowers\skills\writing-plans\SKILL.md`

Count lines first for large files, then read in pages of at most 200 lines. Do not run builds, installs, pytest, staging, commits, worktree creation, branch creation, subagents, or implementation in the writing thread.

## Protected Dirty Files

These files in `E:\mingli-019-closure` already contain user or prior-session uncommitted edits and must be reviewed before any implementation edit:

- `E:\mingli-019-closure\src\mingli_engine\domain_calibration_release.py`
- `E:\mingli-019-closure\tests\unit\test_domain_calibration_release.py`

Task 0 records their diff and disposition. No later task may edit either file until Task 0 is complete.

## Files By Responsibility

- `E:\mingli-019-closure\src\mingli_engine\domain_calibration_models.py`: typed release governance models, legacy loader projection DTOs, maturity policy evidence DTOs, installed-wheel evidence, approval records, and compatible `DomainCalibrationReleaseSummary` field types used by existing `models.py`.
- `E:\mingli-019-closure\src\mingli_engine\models.py`: compatible extension of existing `DomainCalibrationReleaseSummary`, `ReportReleaseSummary`, and `ProjectCompletionSummary` dataclasses by adding fields at the end with defaults.
- `E:\mingli-019-closure\src\mingli_engine\domain_calibration_maturity.py`: legacy metric observation adapter and typed versioned maturity policy evaluator.
- `E:\mingli-019-closure\src\mingli_engine\application_validation.py`: raw-result collectors and gate-specific producers that compute status and hashes.
- `E:\mingli-019-closure\src\mingli_engine\domain_calibration_release.py`: release-facing state machine, legacy projection loader, hard-gate bundle builder from raw results only, installed-wheel validation, version decision, approval binding, and summary builder.
- `E:\mingli-019-closure\src\mingli_engine\installed_release_audit.py`: installed-package audit entry point used from outside the checkout.
- `E:\mingli-019-closure\src\mingli_engine\release_version_workflow.py`: release-owner workflow CLI for inspecting verified installed evidence, gated version decisions, rebuilding changed-version evidence, and writing canonical governance decision artifacts.
- `E:\mingli-019-closure\tests\unit\governance_decision_fixtures.py`: shared unit fixture artifact writer created once in Task 4, then extended in Task 7 for output-surface tests.
- `E:\mingli-019-closure\src\mingli_engine\application_reports.py`: Markdown and HTML governance sections.
- `E:\mingli-019-closure\src\mingli_engine\report_release.py`: existing report release summary integration.
- `E:\mingli-019-closure\src\mingli_engine\cli.py`: existing `domain-calibration-summary` command gains a verified `--governance-decision` artifact path and is exercised through the real CLI contract.
- `E:\mingli-019-closure\pyproject.toml`: package Markdown release docs before the final wheel is built.
- `E:\mingli-019-closure\src\mingli_engine\project_completion.py`: project completion summary integration.
- `E:\mingli-019-closure\src\mingli_engine\data\release_docs\source_grounded_internal_release.md`: packaged governance documentation.
- `E:\mingli-019-closure\src\mingli_engine\data\release_docs\internal_release_notes.md`: packaged internal release notes.

## Coverage Matrix

Every test named below appears with full code in a task.

| Requirement | Tasks | Test evidence |
| --- | --- | --- |
| Protected file disposition occurs before edits | Task 0 | `git diff -- src/mingli_engine/domain_calibration_release.py tests/unit/test_domain_calibration_release.py` is run; hunk-by-hunk disposition and manual deletion rules are recorded before any protected-file write step. |
| Legacy `release_status` remains historical; new projection is `not_evaluated` without artifact rewrite | Task 1 | `test_legacy_release_status_projects_without_rewriting_artifact`, `test_legacy_loader_adapter_projection_are_split_and_artifact_bytes_are_immutable` |
| Existing `DomainCalibrationReleaseSummary` remains compatible | Task 1 | `test_domain_calibration_summary_keeps_existing_fields_and_adds_governance_fields` |
| Legacy metrics become unmapped observations only | Task 2 | `test_legacy_metrics_are_unmapped_observations_not_conclusions` |
| Typed versioned maturity policy computes structured scope records from independent scope evidence | Task 2 | `test_assessment_policy_computes_supported_scope_from_typed_evidence`, `test_assessment_policy_emits_not_assessed_insufficient_and_developing_scope_records` |
| Existing school ID is `ziping` | Task 2 | `test_assessment_policy_computes_supported_scope_from_typed_evidence` |
| Raw-result producers compute gate status, IDs, and hashes | Task 3 | `test_gate_producers_compute_status_ids_and_hash_from_raw_results` |
| Determinism, packaging, version binding, and privacy producers reject unstable checks, truthy failed strings, empty manifest, and missing version identity | Task 3 | `test_gate_producers_fail_for_unstable_checks_empty_manifest_and_missing_versions`, `test_determinism_requires_real_passed_string_not_truthy_failed_string`, `test_packaging_and_version_binding_require_complete_manifest_and_exact_version_set` |
| Release API cannot accept prebuilt all-green gate evidence | Task 3 | `test_release_facing_bundle_requires_raw_results_not_prebuilt_gate_evidence` |
| Missing raw results are `not_evaluated`; safety failure blocks | Task 3 | `test_missing_raw_result_is_not_evaluated_and_safety_failure_blocks` |
| Release path raw results come from existing validators, not caller-filled DTOs | Task 3 | `test_release_collects_raw_results_from_existing_validators` |
| Installed-wheel evidence recomputes canonical hash and validates exact manifest | Task 4 | `test_installed_wheel_evidence_recomputes_hash_and_requires_exact_manifest` |
| Installed evidence preserves two raw audit envelopes, replays gate-specific producers, rebuilds serialized `ExactVersionSet`, and rejects inconsistent audits, missing resources, and forged gate hashes | Task 4 | `test_installed_wheel_evidence_builder_compares_two_audit_payloads`, `test_installed_audit_version_binding_replays_exact_version_set_after_json_round_trip`, `test_installed_wheel_evidence_rejects_inconsistent_audits_missing_resource_and_forged_gate_hash` |
| Real installed-wheel evidence is produced only by checkout-external final wheel install, two installed audits, aggregation, reload, and manifest comparison | Task 4 | `test_installed_release_audit_requires_installed_package_outside_checkout` independently recalculates wheel SHA-256, checks wheel filename, package identity, wheel/distribution/application version binding, and exact wheel-vs-installed resource manifest including packaged docs; `test_installed_release_audit_rejects_missing_or_non_wheel_file` and `test_installed_release_audit_rejects_tampered_wheel_metadata_or_version` cover missing/non-wheel/name/version failures; Task 4 future command builds into a fresh outdir and installs into a fresh checkout-external venv; `write_structurally_valid_installed_evidence_fixture` is structural unit data only and is not release evidence |
| Packaged docs are created and included before final wheel build | Task 4 | `test_release_docs_are_in_package_data_before_final_wheel_build` |
| Version decision uses installed evidence and resets on version change | Task 5 | `test_version_decision_requires_installed_evidence_and_resets_on_change`, `test_not_evaluated_installed_evidence_cannot_enter_version_decision` |
| Version source update cannot run without canonical decision bound to installed evidence | Task 5 | `test_update_version_source_requires_verified_decision_and_installed_evidence`, `test_update_version_source_rejects_missing_or_mismatched_decision` |
| Changed-version structural unit workflow proves state-machine ordering only; real rebuilt-wheel readiness is not claimed while source/trace/unsupported/school/abstention gates are `not_evaluated` | Task 5 | `test_structural_changed_version_workflow_requires_new_audit_before_ready`, `test_structural_changed_version_workflow_rebuilds_audits_and_returns_ready_for_new_version`; Task 4 integration command is required for real wheel evidence and must stop at `not_evaluated` when any gate lacks a real source |
| Release-owner version helper is gated by installed evidence; legacy candidate helper is not a bypass | Task 5 | `test_build_release_version_set_accepts_owner_version_only_after_gate_success`, `test_legacy_candidate_version_set_keeps_calibration_candidate_semantics` |
| State machine cannot jump from `not_evaluated` to released and shares exact status priority with inspect | Task 5 | `test_released_requires_prior_ready_for_same_installed_evidence`, `test_not_evaluated_installed_evidence_inspects_and_transitions_without_blocking` |
| Approval binds installed evidence, claim, limitations, and abstention hashes | Task 5 | `test_approval_record_binds_claim_limitations_abstention_and_installed_evidence` |
| Governance writer/loader recomputes decisions from sidecars and rejects tampering | Task 5 | `test_write_governance_decision_cli_replays_sidecars_and_writes_canonical_artifact`, `test_write_governance_decision_cli_returns_nonzero_for_not_evaluated`, `test_governance_writer_loads_not_evaluated_ready_and_released_decisions`, `test_governance_loader_rejects_tampered_sidecar_or_advertised_hash`; `write_structurally_valid_governance_decision_fixture` is structural unit data only and is not release approval or publication evidence |
| Future release workflow is fresh, self-contained, fail-fast, and conditionally stages version sources only after new evidence passes | Task 5 | The Task 5 future workflow creates a unique `$runRoot`, writes inspect/version/audit/evidence/ready/released artifacts under absolute paths in that root, checks `$LASTEXITCODE` after every native command, parses each new output file before use, allows only inspect exit code 0 or 4, prints runRoot/final evidence/decision/canonical hash, and defines a separate conditional `pyproject.toml` git boundary that is forbidden until changed-version final installed evidence reloads as ready |
| Changed-version failure restores exact version-source bytes before stopping | Task 5 | `test_changed_version_failure_restores_exact_pyproject_bytes` writes a BOM/CRLF snapshot, changes `pyproject.toml`, calls the production `restore-version-source` CLI, asserts exit code 0, verifies final bytes exactly equal the snapshot, and checks the emitted SHA-256; `test_restore_version_source_rejects_missing_or_inconsistent_snapshot` covers missing snapshot and restore mismatch failures through the same CLI |
| Final non-ready evidence leaves canonical governance artifact, not only inspect JSON or exception text | Task 5 | `test_final_not_evaluated_governance_artifact_reloads_and_matches_inspect_status` uses typed missing-source evidence; `test_final_blocked_governance_artifact_reloads_and_matches_inspect_status` uses a gate-specific failed safety raw producer and rebuilt installed evidence. Both prove inspect exit 4, writer exit 4, production loader reload, and exact status equality |
| Rejected approval produces canonical blocked artifact with exit code 4 | Task 5 | `test_rejected_approval_cli_returns_4_and_reloads_blocked_decision` uses ready installed evidence plus canonical rejected approval, calls the production writer with a previous ready decision, expects exit code 4, reloads the output, and asserts `blocked` with a retained canonical hash |
| Historical calibration artifacts and failure metrics remain immutable | Task 6 | `test_historical_calibration_failure_evidence_is_immutable` |
| Existing CLI command and report surfaces expose governance fields from verified decision artifacts and distinguish legacy calibration version from governance installed version | Task 7 | `test_domain_calibration_summary_cli_outputs_governance_fields`, `test_report_release_summary_includes_source_grounded_governance`, `test_project_completion_summary_includes_source_grounded_governance`, `test_markdown_and_html_governance_sections_include_claim_boundary` |
| Packaged docs are proven from installed wheel, not checkout import, without skip | Task 7 | `test_packaged_release_docs_are_loaded_from_installed_wheel_python` |

## Dependency Order

1. Task 0: read-only context, Git state, protected diff disposition, and explicit manual deletion rules for discarded protected hunks before any protected-file governance edit.
2. Task 1: governance models, compatible model extensions, and legacy schema projection.
3. Task 2: maturity observation adapter and typed assessment policy.
4. Task 3: raw-result hard-gate producers and release-facing bundle construction.
5. Task 4: installed-wheel release evidence, installed audit command, and first creation of the shared governance decision fixture file; final evidence aggregation must finish before version decision.
6. Task 5: version decision, shared status classification, canonical governance decision writer/loader, approval binding, and gated version-source update; changed-version wheel audit reruns before ready.
7. Task 6: historical immutability evidence.
8. Task 7: output surfaces, packaged docs, and final scans.

---

### Task 0: Read-Only Context And Protected Diff Disposition

**Files:**
- Read: all files listed in Planning Thread Boundary
- Read: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_release.py`
- Read: `E:\mingli-019-closure\tests\unit\test_domain_calibration_release.py`
- No modifications

- [ ] **Step 1: Verify worktree state**

Run:

```powershell
git -C 'E:\命理演绎' status --short --branch
git -C 'E:\命理演绎' rev-parse --abbrev-ref HEAD
git -C 'E:\命理演绎' rev-parse HEAD
git -C 'E:\mingli-019-closure' status --short --branch
git -C 'E:\mingli-019-closure' rev-parse --abbrev-ref HEAD
git -C 'E:\mingli-019-closure' rev-parse HEAD
```

Expected: no files are changed by this step.

- [ ] **Step 2: Review protected diff**

Run:

```powershell
git -C 'E:\mingli-019-closure' diff -- src/mingli_engine/domain_calibration_release.py tests/unit/test_domain_calibration_release.py
```

Expected: diff is reviewed before edits.

- [ ] **Step 3: Record hunk-by-hunk disposition before any protected-file edit**

Record this disposition in the execution notes:

```text
Protected file: src/mingli_engine/domain_calibration_release.py
- Hunk adding imports `from importlib.resources import files` and `from pathlib import Path`: discard from this file. Reason: these imports only support the baseline writer/loader and must not remain in the application release path.
- Hunk adding `freeze_final_calibration_baseline(...)`: discard. Reason: baseline writer is a legacy calibration artifact workflow and must not become an application release gate.
- Hunk adding `load_final_calibration_baseline(...)`: discard. Reason: final calibration baseline loading is not release evidence and must not drive application governance.
- Hunk modifying build_domain_calibration_summary around baseline writing or release readiness: discard and rewrite. Reason: summary must preserve legacy blocked calibration status and read canonical governance decision evidence; it must not create release evidence.

Protected file: tests/unit/test_domain_calibration_release.py
- Hunk adding `freeze_final_calibration_baseline` to imports: discard. Reason: writer API is out of scope for application release governance.
- Hunk adding `test_controlled_writer_freezes_only_final_0_2_0_snapshot`: discard. Reason: writer tests must not be staged or committed with this feature.
- Hunk adding `test_controlled_writer_rejects_nonfinal_name_and_wrong_version`: discard. Reason: writer tests must not be staged or committed with this feature.
- Hunk asserting installed resources from checkout paths: rewrite to checkout-external installed-wheel tests. Reason: packaged docs and resources must be proven through a fresh installed wheel.

Existing protected edits must not be staged, committed, restored, or overwritten until this disposition has been recorded.
Before the first governance edit in either protected file, manually remove the discarded hunks listed above by editing only those exact import/function/test blocks back to current HEAD content; do not run git restore, git checkout, git reset, or any other broad revert command.
The manual deletion must be followed by `git -C 'E:\mingli-019-closure' diff -- src/mingli_engine/domain_calibration_release.py tests/unit/test_domain_calibration_release.py` to confirm only explicitly retained hunks remain.
```

- [ ] **Step 4: Commit boundary**

No commit. This task is read-only.

---

### Task 1: Governance Models, Compatible Summary Fields, And Legacy Projection

**Files:**
- Modify: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_models.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\models.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_release.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_domain_calibration_models.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_domain_calibration_release.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_models.py`

- [ ] **Step 1: Write failing tests**

Append to `tests\unit\test_domain_calibration_models.py`:

```python
import json
from dataclasses import asdict

from mingli_engine.domain_calibration_models import (
    APPLICATION_GATE_IDS,
    ApplicationHardGateEvidence,
    ExactVersionSet,
    LegacyCalibrationReleaseArtifact,
)


def test_application_hard_gate_evidence_computes_identity_from_payload() -> None:
    first = ApplicationHardGateEvidence.from_raw_payload(
        gate_id="privacy",
        status="failed",
        producer="privacy-verifier",
        raw_payload={"leak_events": ("name",)},
        failure_reasons=("privacy leak detected",),
    )
    second = ApplicationHardGateEvidence.from_raw_payload(
        gate_id="privacy",
        status="failed",
        producer="privacy-verifier",
        raw_payload={"leak_events": ("birth_date",)},
        failure_reasons=("privacy leak detected",),
    )

    assert first.gate_id == "privacy"
    assert first.canonical_sha256 != second.canonical_sha256
    assert first.evidence_id.startswith("privacy:")


def test_legacy_artifact_schema_preserves_release_status() -> None:
    version_set = ExactVersionSet(
        application_version="0.1.0",
        engine_version="engine-019",
        ruleset_version="ruleset-019",
        provider_version="provider-019",
        school_profile_version="school-019",
        fixture_version="fixture-019",
        evidence_baseline_id="baseline-019",
        corpus_sha256="a" * 64,
    )
    artifact = LegacyCalibrationReleaseArtifact(
        schema_version="domain-calibration-release-v1",
        release_status="blocked",
        version_set=version_set,
        metrics={"reviewer_raw_agreement": 0.6744186046511628},
        artifact_sha256="b" * 64,
    )

    payload = asdict(artifact)
    assert payload["release_status"] == "blocked"
    assert tuple(APPLICATION_GATE_IDS) == (
        "deterministic_calculation",
        "source_rule_tracing",
        "unsupported_inference",
        "school_conflict",
        "abstention",
        "safety_critical",
        "privacy",
        "packaging",
        "version_binding",
        "reproducibility",
    )
```

Append to `tests\unit\test_models.py`:

```python
from dataclasses import fields

from mingli_engine.models import DomainCalibrationReleaseSummary, Report


def test_domain_calibration_summary_keeps_existing_fields_and_adds_governance_fields() -> None:
    field_names = [field.name for field in fields(DomainCalibrationReleaseSummary)]

    assert field_names[:12] == [
        "release_id",
        "release_status",
        "application_version",
        "installed_distribution_version",
        "claim_boundary",
        "checks",
        "blockers",
        "metrics",
        "version_set",
        "resource_sha256",
        "source_isolated",
        "next_action",
    ]
    assert "application_release_status" in field_names
    assert "evidence_maturity_status" in field_names
    assert "release_claim_boundary_hash" in field_names
```

Append to `tests\unit\test_domain_calibration_release.py`:

```python
import json
from hashlib import sha256
from pathlib import Path
from typing import Mapping

from mingli_engine.domain_calibration_models import ExactVersionSet, InstalledWheelReleaseEvidence, governance_canonical_sha256

from mingli_engine.domain_calibration_release import (
    adapt_legacy_calibration_release_artifact,
    derive_legacy_calibration_release_projection,
    load_legacy_calibration_release_artifact,
    load_legacy_calibration_release_projection,
)


def test_legacy_release_status_projects_without_rewriting_artifact(tmp_path: Path) -> None:
    artifact = tmp_path / "legacy-release.json"
    artifact.write_text(
        json.dumps(
            {
                "schema_version": "domain-calibration-release-v1",
                "release_status": "blocked",
                "version_set": {
                    "application_version": "0.1.0",
                    "engine_version": "engine-019",
                    "ruleset_version": "ruleset-019",
                    "provider_version": "provider-019",
                    "school_profile_version": "school-019",
                    "fixture_version": "fixture-019",
                    "evidence_baseline_id": "baseline-019",
                    "corpus_sha256": "a" * 64,
                },
                "metrics": {"reviewer_raw_agreement": 0.6744186046511628},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    before = artifact.read_bytes()

    projection = load_legacy_calibration_release_projection(artifact)

    assert artifact.read_bytes() == before
    assert projection.legacy_release_status == "blocked"
    assert projection.application_release_status == "not_evaluated"


def test_legacy_loader_adapter_projection_are_split_and_artifact_bytes_are_immutable(tmp_path: Path) -> None:
    artifact = tmp_path / "legacy-release.json"
    artifact.write_text(
        json.dumps(
            {
                "schema_version": "domain-calibration-release-v1",
                "release_status": "blocked",
                "version_set": {
                    "application_version": "0.2.0",
                    "engine_version": "engine-019",
                    "ruleset_version": "ruleset-019",
                    "provider_version": "provider-019",
                    "school_profile_version": "school-019",
                    "fixture_version": "fixture-019",
                    "evidence_baseline_id": "baseline-019",
                    "corpus_sha256": "a" * 64,
                },
                "metrics": {"reviewer_raw_agreement": 0.6744186046511628},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    before = artifact.read_bytes()

    loaded = load_legacy_calibration_release_artifact(artifact)
    adapted = adapt_legacy_calibration_release_artifact(loaded)
    projected = derive_legacy_calibration_release_projection(adapted)

    assert artifact.read_bytes() == before
    assert loaded.release_status == "blocked"
    assert adapted.legacy_release_status == "blocked"
    assert projected.legacy_release_status == "blocked"
    assert projected.application_release_status == "not_evaluated"
    assert projected.artifact_sha256 == governance_canonical_sha256(json.loads(before.decode("utf-8")))
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
pytest tests/unit/test_domain_calibration_models.py tests/unit/test_models.py tests/unit/test_domain_calibration_release.py -q
```

Expected: FAIL because the new models, compatible fields, and loader projection are missing.

- [ ] **Step 3: Implement governance models**

Add to `src\mingli_engine\domain_calibration_models.py`:

```python
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Literal, Mapping


ApplicationReleaseStatus = Literal[
    "not_evaluated",
    "blocked",
    "internal_source_grounded_ready",
    "released_internal_source_grounded",
]
GateStatus = Literal["passed", "failed", "not_evaluated"]

APPLICATION_GATE_IDS = (
    "deterministic_calculation",
    "source_rule_tracing",
    "unsupported_inference",
    "school_conflict",
    "abstention",
    "safety_critical",
    "privacy",
    "packaging",
    "version_binding",
    "reproducibility",
)


def governance_canonical_sha256(payload: object) -> str:
    return sha256(canonical_json_bytes(payload)).hexdigest()


def require_sha256(value: str, field_name: str) -> None:
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{field_name} must be a lowercase sha256 digest")


@dataclass(frozen=True)
class LegacyCalibrationReleaseArtifact:
    schema_version: str
    release_status: str
    version_set: ExactVersionSet
    metrics: Mapping[str, object]
    artifact_sha256: str


@dataclass(frozen=True)
class LegacyCalibrationReleaseAdapter:
    schema_version: str
    legacy_release_status: str
    version_set: ExactVersionSet
    metrics: Mapping[str, object]
    artifact_sha256: str


@dataclass(frozen=True)
class LegacyCalibrationReleaseProjection:
    schema_version: str
    legacy_release_status: str
    application_release_status: ApplicationReleaseStatus
    version_set: ExactVersionSet
    metrics: Mapping[str, object]
    artifact_sha256: str


@dataclass(frozen=True)
class ApplicationHardGateEvidence:
    gate_id: str
    status: GateStatus
    producer: str
    evidence_id: str
    raw_payload: Mapping[str, object]
    raw_payload_sha256: str
    canonical_sha256: str
    failure_reasons: tuple[str, ...]

    @classmethod
    def from_raw_payload(
        cls,
        *,
        gate_id: str,
        status: GateStatus,
        producer: str,
        raw_payload: Mapping[str, object],
        failure_reasons: tuple[str, ...] = (),
    ) -> "ApplicationHardGateEvidence":
        if gate_id not in APPLICATION_GATE_IDS:
            raise ValueError(f"unknown application gate id: {gate_id}")
        if status == "failed" and not failure_reasons:
            raise ValueError("failed gate evidence requires failure reasons")
        raw_hash = governance_canonical_sha256(raw_payload)
        evidence_id = f"{gate_id}:{producer}:{raw_hash}"
        canonical = governance_canonical_sha256(
            {
                "gate_id": gate_id,
                "status": status,
                "producer": producer,
                "evidence_id": evidence_id,
                "raw_payload_sha256": raw_hash,
                "failure_reasons": failure_reasons,
            }
        )
        return cls(gate_id, status, producer, evidence_id, dict(raw_payload), raw_hash, canonical, failure_reasons)

    def to_dict(self) -> dict[str, object]:
        return {
            "gate_id": self.gate_id,
            "status": self.status,
            "producer": self.producer,
            "evidence_id": self.evidence_id,
            "raw_payload": dict(self.raw_payload),
            "raw_payload_sha256": self.raw_payload_sha256,
            "canonical_sha256": self.canonical_sha256,
            "failure_reasons": self.failure_reasons,
        }


MISSING_RAW_GATE_PRODUCER = "application_validation.missing_raw_gate_result"


def missing_raw_gate_payload(gate_id: str) -> dict[str, object]:
    return {
        "schema_version": "missing-raw-gate-v1",
        "gate_id": gate_id,
        "reason": "raw result missing",
    }


def produce_missing_raw_gate_evidence(gate_id: str) -> ApplicationHardGateEvidence:
    return ApplicationHardGateEvidence.from_raw_payload(
        gate_id=gate_id,
        status="not_evaluated",
        producer=MISSING_RAW_GATE_PRODUCER,
        raw_payload=missing_raw_gate_payload(gate_id),
    )


def replay_application_gate_evidence(item: Mapping[str, object]) -> ApplicationHardGateEvidence:
    from mingli_engine.application_validation import (
        RawAbstentionResult,
        RawDeterminismResult,
        RawPackagingResult,
        RawPrivacyResult,
        RawReproducibilityResult,
        RawSafetyResult,
        RawSchoolConflictResult,
        RawTraceResult,
        RawUnsupportedInferenceResult,
        RawVersionBindingResult,
        produce_abstention_gate,
        produce_deterministic_gate,
        produce_packaging_gate,
        produce_privacy_gate,
        produce_reproducibility_gate,
        produce_safety_gate,
        produce_school_conflict_gate,
        produce_trace_gate,
        produce_unsupported_inference_gate,
        produce_version_binding_gate,
    )

    gate_id = str(item["gate_id"])
    raw_payload = dict(item["raw_payload"])
    if item["producer"] == MISSING_RAW_GATE_PRODUCER:
        replayed = produce_missing_raw_gate_evidence(gate_id)
    elif gate_id == "deterministic_calculation":
        replayed = produce_deterministic_gate(RawDeterminismResult(**raw_payload))
    elif gate_id == "source_rule_tracing":
        replayed = produce_trace_gate(RawTraceResult(**raw_payload))
    elif gate_id == "unsupported_inference":
        replayed = produce_unsupported_inference_gate(RawUnsupportedInferenceResult(**raw_payload))
    elif gate_id == "school_conflict":
        replayed = produce_school_conflict_gate(RawSchoolConflictResult(**raw_payload))
    elif gate_id == "abstention":
        replayed = produce_abstention_gate(RawAbstentionResult(**raw_payload))
    elif gate_id == "safety_critical":
        replayed = produce_safety_gate(RawSafetyResult(**raw_payload))
    elif gate_id == "privacy":
        replayed = produce_privacy_gate(RawPrivacyResult(**raw_payload))
    elif gate_id == "packaging":
        replayed = produce_packaging_gate(RawPackagingResult(**raw_payload))
    elif gate_id == "version_binding":
        exact_payload = raw_payload.get("exact_version_set")
        if not isinstance(exact_payload, dict):
            raise ValueError("version binding raw payload must include serialized exact_version_set")
        raw_payload["exact_version_set"] = ExactVersionSet(
            application_version=str(exact_payload["application_version"]),
            engine_version=str(exact_payload["engine_version"]),
            ruleset_version=str(exact_payload["ruleset_version"]),
            provider_version=str(exact_payload["provider_version"]),
            school_profile_version=str(exact_payload["school_profile_version"]),
            fixture_version=str(exact_payload["fixture_version"]),
            evidence_baseline_id=str(exact_payload["evidence_baseline_id"]),
            corpus_sha256=str(exact_payload["corpus_sha256"]),
        )
        replayed = produce_version_binding_gate(RawVersionBindingResult(**raw_payload))
    elif gate_id == "reproducibility":
        replayed = produce_reproducibility_gate(RawReproducibilityResult(**raw_payload))
    else:
        raise ValueError(f"unknown application gate id: {gate_id}")
    if replayed.to_dict() != dict(item):
        raise ValueError("application gate evidence replay mismatch")
    return replayed


@dataclass(frozen=True)
class ApplicationEvidenceBundle:
    gate_evidence: tuple[ApplicationHardGateEvidence, ...]
    overall_status: Literal["passed", "blocked", "not_evaluated"]
    canonical_sha256: str

    @classmethod
    def from_gate_evidence(cls, gate_evidence: tuple[ApplicationHardGateEvidence, ...]) -> "ApplicationEvidenceBundle":
        if tuple(gate.gate_id for gate in gate_evidence) != APPLICATION_GATE_IDS:
            raise ValueError("application evidence requires the exact complete gate set")
        if any(gate.gate_id == "safety_critical" and gate.status == "failed" for gate in gate_evidence):
            overall = "blocked"
        elif any(gate.status == "failed" for gate in gate_evidence):
            overall = "blocked"
        elif any(gate.status == "not_evaluated" for gate in gate_evidence):
            overall = "not_evaluated"
        else:
            overall = "passed"
        canonical = governance_canonical_sha256(
            {
                "gate_hashes": tuple(gate.canonical_sha256 for gate in gate_evidence),
                "overall_status": overall,
            }
        )
        return cls(gate_evidence, overall, canonical)

    def to_dict(self) -> dict[str, object]:
        return {
            "gate_evidence": tuple(gate.to_dict() for gate in self.gate_evidence),
            "overall_status": self.overall_status,
            "canonical_sha256": self.canonical_sha256,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "ApplicationEvidenceBundle":
        gates = tuple(
            replay_application_gate_evidence(item)
            for item in payload["gate_evidence"]
        )
        rebuilt = cls.from_gate_evidence(gates)
        if rebuilt.overall_status != payload["overall_status"] or rebuilt.canonical_sha256 != payload["canonical_sha256"]:
            raise ValueError("application evidence bundle hash mismatch")
        return rebuilt
```

- [ ] **Step 4: Compatibly extend existing `models.py` dataclasses**

Append fields to the end of existing dataclasses instead of replacing them:

```python
@dataclass(frozen=True)
class DomainCalibrationReleaseSummary:
    release_id: str
    release_status: str
    application_version: str
    installed_distribution_version: str
    claim_boundary: str
    checks: dict[str, str]
    blockers: list[str]
    metrics: dict[str, object]
    version_set: dict[str, str]
    resource_sha256: dict[str, str]
    source_isolated: bool
    next_action: str
    application_release_status: str = "not_evaluated"
    evidence_maturity_status: str = "not_assessed"
    evidence_maturity_scope_records: tuple[dict[str, object], ...] = ()
    assessment_policy_version: str = "source-grounded-maturity-policy-v1"
    release_statement: str = ""
    limitations: tuple[str, ...] = ()
    abstention_policy: str = ""
    release_claim_boundary_hash: str = ""
    application_evidence_hash: str = ""
    installed_wheel_evidence_hash: str = ""
    package_identity: str = ""
    distribution_version: str = ""
    governance_application_version: str = ""
```

Append these fields to the end of existing `ReportReleaseSummary` and `ProjectCompletionSummary`:

```python
source_grounded_application_release_status: str = "not_evaluated"
source_grounded_evidence_maturity_status: str = "not_assessed"
source_grounded_evidence_maturity_scope_records: tuple[dict[str, object], ...] = ()
source_grounded_release_statement: str = ""
source_grounded_limitations: tuple[str, ...] = ()
source_grounded_abstention_policy: str = ""
source_grounded_claim_boundary_hash: str = ""
source_grounded_application_evidence_hash: str = ""
source_grounded_installed_wheel_evidence_hash: str = ""
source_grounded_package_identity: str = ""
source_grounded_distribution_version: str = ""
source_grounded_application_version: str = ""
```

- [ ] **Step 5: Implement legacy loader and derived projection**

Add to `src\mingli_engine\domain_calibration_release.py`:

```python
import json
from pathlib import Path

from mingli_engine.domain_calibration_models import (
    ApplicationReleaseStatus,
    ExactVersionSet,
    LegacyCalibrationReleaseAdapter,
    LegacyCalibrationReleaseArtifact,
    LegacyCalibrationReleaseProjection,
    governance_canonical_sha256,
)


def load_legacy_calibration_release_artifact(
    artifact_path: str | Path,
) -> LegacyCalibrationReleaseArtifact:
    path = Path(artifact_path)
    raw_bytes = path.read_bytes()
    payload = json.loads(raw_bytes.decode("utf-8"))
    version_payload = payload["version_set"]
    version_set = ExactVersionSet(
        application_version=version_payload["application_version"],
        engine_version=version_payload["engine_version"],
        ruleset_version=version_payload["ruleset_version"],
        provider_version=version_payload["provider_version"],
        school_profile_version=version_payload["school_profile_version"],
        fixture_version=version_payload["fixture_version"],
        evidence_baseline_id=version_payload["evidence_baseline_id"],
        corpus_sha256=version_payload["corpus_sha256"],
    )
    artifact_hash = governance_canonical_sha256(json.loads(raw_bytes.decode("utf-8")))
    return LegacyCalibrationReleaseArtifact(
        schema_version=payload["schema_version"],
        release_status=payload["release_status"],
        version_set=version_set,
        metrics=payload.get("metrics", {}),
        artifact_sha256=artifact_hash,
    )


def adapt_legacy_calibration_release_artifact(
    artifact: LegacyCalibrationReleaseArtifact,
) -> LegacyCalibrationReleaseAdapter:
    return LegacyCalibrationReleaseAdapter(
        schema_version=artifact.schema_version,
        legacy_release_status=artifact.release_status,
        version_set=artifact.version_set,
        metrics=artifact.metrics,
        artifact_sha256=artifact.artifact_sha256,
    )


def derive_legacy_calibration_release_projection(
    adapter: LegacyCalibrationReleaseAdapter,
) -> LegacyCalibrationReleaseProjection:
    return LegacyCalibrationReleaseProjection(
        schema_version=adapter.schema_version,
        legacy_release_status=adapter.legacy_release_status,
        application_release_status="not_evaluated",
        version_set=adapter.version_set,
        metrics=adapter.metrics,
        artifact_sha256=adapter.artifact_sha256,
    )


def load_legacy_calibration_release_projection(
    artifact_path: str | Path,
) -> LegacyCalibrationReleaseProjection:
    return derive_legacy_calibration_release_projection(
        adapt_legacy_calibration_release_artifact(
            load_legacy_calibration_release_artifact(artifact_path)
        )
    )
```

- [ ] **Step 6: Run tests to verify pass**

Run:

```powershell
pytest tests/unit/test_domain_calibration_models.py tests/unit/test_models.py tests/unit/test_domain_calibration_release.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit boundary**

Run:

```powershell
git add src/mingli_engine/domain_calibration_models.py src/mingli_engine/models.py src/mingli_engine/domain_calibration_release.py tests/unit/test_domain_calibration_models.py tests/unit/test_models.py tests/unit/test_domain_calibration_release.py
git commit -m "feat: add legacy release projection and governance models"
```

---

### Task 2: Maturity Observations And Typed Assessment Policy

**Files:**
- Create: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_maturity.py`
- Create: `E:\mingli-019-closure\tests\unit\test_domain_calibration_maturity.py`

- [ ] **Step 1: Write failing tests**

Create `tests\unit\test_domain_calibration_maturity.py`:

```python
from mingli_engine.domain_calibration import build_candidate_metric_snapshot, build_candidate_version_set, execute_candidate_calibration
from mingli_engine.domain_calibration_maturity import (
    AssessmentPolicy,
    EvidenceMaturityObservation,
    EvidenceMaturityScopeRecord,
    SourceScopeAssessmentEvidence,
    assess_maturity_with_policy,
    metric_snapshot_to_maturity_observations,
    source_grounded_maturity_policy_v1,
)


def test_legacy_metrics_are_unmapped_observations_not_conclusions() -> None:
    version_set = build_candidate_version_set("0.2.0")
    run = execute_candidate_calibration(version_set)
    repeated_run = execute_candidate_calibration(version_set)
    snapshot = build_candidate_metric_snapshot(run, repeated_run)
    observations = metric_snapshot_to_maturity_observations(snapshot)
    policy = source_grounded_maturity_policy_v1()

    status = assess_maturity_with_policy(
        policy=policy,
        observations=observations,
        scope_evidence=(),
    )

    assert {observation.metric_name for observation in observations} >= {
        "reviewer_raw_agreement",
        "adjudicated_engine_match",
        "weighted_kappa",
        "jaccard_agreement",
    }
    assert all(observation.scope_confidence == "unmapped" for observation in observations)
    assert status.scope_records == ()
    assert any(
        observation.metric_name == "expert_coverage"
        and observation.metric_value == "not_assessed"
        and observation.scope_confidence == "unmapped"
        for observation in observations
    )


def test_assessment_policy_computes_supported_scope_from_typed_evidence() -> None:
    policy = source_grounded_maturity_policy_v1()
    mapped_observation = EvidenceMaturityObservation(
        observation_id="mapped:L2:ziping:strength_balance:001",
        metric_name="source_trace_coverage",
        metric_value=1.0,
        layer="L2",
        school="ziping",
        rule_family="strength_balance",
        source_scope="annotated-classical-source-set-v1",
        scope_confidence="mapped",
        limitations=(),
    )
    unmapped_observation = EvidenceMaturityObservation(
        observation_id="legacy:global:reviewer_raw_agreement",
        metric_name="reviewer_raw_agreement",
        metric_value=0.6744186046511628,
        layer=None,
        school=None,
        rule_family=None,
        source_scope="legacy-domain-calibration-global",
        scope_confidence="unmapped",
        limitations=("legacy global metric",),
    )
    evidence = SourceScopeAssessmentEvidence(
        evidence_id="scope-ziping-strength-001",
        layer="L2",
        school="ziping",
        rule_family="strength_balance",
        source_scope="annotated-classical-source-set-v1",
        assessment_policy_version="source-grounded-maturity-policy-v1",
        expert_coverage_status="observed",
        source_trace_coverage=1.0,
        rule_family_coverage=1.0,
        reviewer_agreement=0.9,
        contested=False,
        limitations=(),
    )

    status = assess_maturity_with_policy(
        policy=policy,
        observations=(mapped_observation, unmapped_observation),
        scope_evidence=(evidence,),
    )

    assert status.scope_records == (
        EvidenceMaturityScopeRecord(
            conclusion_status="supported_for_stated_scope",
            assessment_policy_version="source-grounded-maturity-policy-v1",
            layer="L2",
            school="ziping",
            rule_family="strength_balance",
            source_scope="annotated-classical-source-set-v1",
            coverage=1.0,
            contested=False,
            observation_ids=("mapped:L2:ziping:strength_balance:001",),
            evidence_ids=("scope-ziping-strength-001",),
            limitations=(),
        ),
    )


def test_assessment_policy_emits_not_assessed_insufficient_and_developing_scope_records() -> None:
    policy = source_grounded_maturity_policy_v1()
    no_expert = SourceScopeAssessmentEvidence(
        evidence_id="scope-no-expert",
        layer="L1",
        school="ziping",
        rule_family="calendar_conversion",
        source_scope="annotated-classical-source-set-v1",
        assessment_policy_version="source-grounded-maturity-policy-v1",
        expert_coverage_status="not_assessed",
        source_trace_coverage=1.0,
        rule_family_coverage=1.0,
        reviewer_agreement=0.9,
        contested=False,
        limitations=("expert coverage has not been observed",),
    )
    insufficient = SourceScopeAssessmentEvidence(
        evidence_id="scope-insufficient",
        layer="L2",
        school="ziping",
        rule_family="ten_gods",
        source_scope="annotated-classical-source-set-v1",
        assessment_policy_version="source-grounded-maturity-policy-v1",
        expert_coverage_status="observed",
        source_trace_coverage=0.25,
        rule_family_coverage=0.25,
        reviewer_agreement=0.4,
        contested=False,
        limitations=("coverage below minimum",),
    )
    developing = SourceScopeAssessmentEvidence(
        evidence_id="scope-developing",
        layer="L3",
        school="ziping",
        rule_family="structure_pattern",
        source_scope="annotated-classical-source-set-v1",
        assessment_policy_version="source-grounded-maturity-policy-v1",
        expert_coverage_status="observed",
        source_trace_coverage=0.75,
        rule_family_coverage=0.8,
        reviewer_agreement=0.76,
        contested=True,
        limitations=("contested scope",),
    )

    status = assess_maturity_with_policy(
        policy=policy,
        observations=(),
        scope_evidence=(no_expert, insufficient, developing),
    )

    assert [record.conclusion_status for record in status.scope_records] == [
        "not_assessed",
        "insufficient",
        "developing",
    ]
    assert status.scope_records[0].limitations == ("expert coverage has not been observed",)
    assert status.scope_records[2].contested is True
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
pytest tests/unit/test_domain_calibration_maturity.py -q
```

Expected: FAIL because the maturity policy module is missing.

- [ ] **Step 3: Implement typed maturity policy**

Create `src\mingli_engine\domain_calibration_maturity.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mingli_engine.domain_calibration_models import MetricSnapshotV1


@dataclass(frozen=True)
class EvidenceMaturityObservation:
    observation_id: str
    metric_name: str
    metric_value: float | int | str
    layer: str | None
    school: str | None
    rule_family: str | None
    source_scope: str
    scope_confidence: Literal["mapped", "unmapped"]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SourceScopeAssessmentEvidence:
    evidence_id: str
    layer: Literal["L0", "L1", "L2", "L3", "L4"]
    school: str
    rule_family: str
    source_scope: str
    assessment_policy_version: str
    expert_coverage_status: Literal["observed", "not_assessed"]
    source_trace_coverage: float
    rule_family_coverage: float
    reviewer_agreement: float
    contested: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class AssessmentPolicy:
    assessment_policy_version: str
    minimum_source_trace_coverage: float
    minimum_rule_family_coverage: float
    minimum_reviewer_agreement: float

    def __post_init__(self) -> None:
        if (
            self.assessment_policy_version,
            self.minimum_source_trace_coverage,
            self.minimum_rule_family_coverage,
            self.minimum_reviewer_agreement,
        ) != (
            "source-grounded-maturity-policy-v1",
            1.0,
            1.0,
            0.85,
        ):
            raise ValueError("AssessmentPolicy must come from the fixed versioned policy definition")


def source_grounded_maturity_policy_v1() -> AssessmentPolicy:
    return AssessmentPolicy(
        assessment_policy_version="source-grounded-maturity-policy-v1",
        minimum_source_trace_coverage=1.0,
        minimum_rule_family_coverage=1.0,
        minimum_reviewer_agreement=0.85,
    )


@dataclass(frozen=True)
class EvidenceMaturityScopeRecord:
    conclusion_status: Literal["not_assessed", "insufficient", "developing", "supported_for_stated_scope"]
    assessment_policy_version: str
    layer: str
    school: str
    rule_family: str
    source_scope: str
    coverage: float
    contested: bool
    observation_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceMaturityStatus:
    assessment_policy_version: str
    scope_records: tuple[EvidenceMaturityScopeRecord, ...]


def metric_snapshot_to_maturity_observations(
    snapshot: MetricSnapshotV1,
) -> tuple[EvidenceMaturityObservation, ...]:
    limitation = "legacy calibration metrics are global and cannot be mapped to a specific layer, school, rule family, or source scope"
    metrics = (
        ("reviewer_raw_agreement", snapshot.reviewer_raw_agreement),
        ("adjudicated_engine_match", snapshot.adjudicated_engine_match),
        ("weighted_kappa", snapshot.weighted_kappa),
        ("jaccard_agreement", snapshot.jaccard_agreement),
        ("expert_coverage", "not_assessed"),
    )
    return tuple(
        EvidenceMaturityObservation(
            observation_id=f"legacy:{name}:{snapshot.corpus_sha256}",
            metric_name=name,
            metric_value=value,
            layer=None,
            school=None,
            rule_family=None,
            source_scope="legacy-domain-calibration-global",
            scope_confidence="unmapped",
            limitations=(limitation,),
        )
        for name, value in metrics
    )


def assess_maturity_with_policy(
    *,
    policy: AssessmentPolicy,
    observations: tuple[EvidenceMaturityObservation, ...],
    scope_evidence: tuple[SourceScopeAssessmentEvidence, ...],
) -> EvidenceMaturityStatus:
    valid_scope_evidence = tuple(
        evidence
        for evidence in scope_evidence
        if evidence.assessment_policy_version == policy.assessment_policy_version
    )
    records: list[EvidenceMaturityScopeRecord] = []
    for evidence in valid_scope_evidence:
        scoped_observations = tuple(
            observation
            for observation in observations
            if observation.scope_confidence == "mapped"
            and observation.layer == evidence.layer
            and observation.school == evidence.school
            and observation.rule_family == evidence.rule_family
            and observation.source_scope == evidence.source_scope
        )
        coverage = min(evidence.source_trace_coverage, evidence.rule_family_coverage)
        if evidence.expert_coverage_status == "not_assessed":
            conclusion = "not_assessed"
            limitations = evidence.limitations or ("expert coverage has not been observed",)
        elif coverage < 0.5 or evidence.reviewer_agreement < 0.5:
            conclusion = "insufficient"
            limitations = evidence.limitations or ("scope evidence is insufficient for maturity conclusion",)
        elif (
            evidence.source_trace_coverage >= policy.minimum_source_trace_coverage
            and evidence.rule_family_coverage >= policy.minimum_rule_family_coverage
            and evidence.reviewer_agreement >= policy.minimum_reviewer_agreement
            and not evidence.contested
        ):
            conclusion = "supported_for_stated_scope"
            limitations = evidence.limitations
        else:
            conclusion = "developing"
            limitations = evidence.limitations or ("scope evidence is still developing",)
        records.append(
            EvidenceMaturityScopeRecord(
                conclusion_status=conclusion,
                assessment_policy_version=policy.assessment_policy_version,
                layer=evidence.layer,
                school=evidence.school,
                rule_family=evidence.rule_family,
                source_scope=evidence.source_scope,
                coverage=coverage,
                contested=evidence.contested,
                observation_ids=tuple(observation.observation_id for observation in scoped_observations),
                evidence_ids=(evidence.evidence_id,),
                limitations=tuple(limitations),
            )
        )
    return EvidenceMaturityStatus(
        assessment_policy_version=policy.assessment_policy_version,
        scope_records=tuple(records),
    )
```

- [ ] **Step 4: Run tests to verify pass**

Run:

```powershell
pytest tests/unit/test_domain_calibration_maturity.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit boundary**

Run:

```powershell
git add src/mingli_engine/domain_calibration_maturity.py tests/unit/test_domain_calibration_maturity.py
git commit -m "feat: evaluate maturity with typed scope policy"
```

---

### Task 3: Raw-Result Hard-Gate Producers

**Files:**
- Modify: `E:\mingli-019-closure\src\mingli_engine\application_validation.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_release.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_application_validation.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_domain_calibration_release.py`

- [ ] **Step 1: Write failing tests**

Append to `tests\unit\test_application_validation.py`:

```python
from mingli_engine.application_validation import (
    RawApplicationGateResults,
    RawDeterminismResult,
    RawPackagingResult,
    RawPrivacyResult,
    RawSafetyResult,
    RawVersionBindingResult,
    produce_deterministic_gate,
    produce_packaging_gate,
    produce_privacy_gate,
    produce_safety_gate,
    produce_version_binding_gate,
)
from mingli_engine.domain_calibration import build_release_version_set
from mingli_engine.packaging_validation import EXPECTED_RUNTIME_JSON_ASSETS


def test_gate_producers_compute_status_ids_and_hash_from_raw_results() -> None:
    deterministic = produce_deterministic_gate(
        RawDeterminismResult(
            first_run_hash="a" * 64,
            second_run_hash="a" * 64,
            calculation_checks={"stages_present": "passed", "placeholder_integrity": "passed"},
        )
    )
    privacy = produce_privacy_gate(
        RawPrivacyResult(
            scenario_count=2,
            privacy_failed_scenarios=(),
            write_count=0,
            leak_count=0,
        )
    )

    assert deterministic.status == "passed"
    assert privacy.status == "passed"
    assert deterministic.evidence_id.startswith("deterministic_calculation:")
    assert deterministic.canonical_sha256 != privacy.canonical_sha256


def test_gate_producers_fail_for_unstable_checks_empty_manifest_and_missing_versions() -> None:
    unstable = produce_deterministic_gate(
        RawDeterminismResult(
            first_run_hash="a" * 64,
            second_run_hash="b" * 64,
            calculation_checks={"stages_present": "passed", "placeholder_integrity": "passed"},
        )
    )
    failed_checks = produce_deterministic_gate(
        RawDeterminismResult(
            first_run_hash="a" * 64,
            second_run_hash="a" * 64,
            calculation_checks={"stages_present": "passed", "placeholder_integrity": "failed"},
        )
    )
    empty_packaging = produce_packaging_gate(
        RawPackagingResult(
            asset_sha256={},
            expected_asset_paths=("mingli_engine/data/release_docs/source_grounded_internal_release.md",),
            source_isolated=True,
            distribution_version="0.1.0",
        )
    )
    missing_version = produce_version_binding_gate(
        RawVersionBindingResult(
            package_identity="mingli-engine",
            distribution_version="0.1.0",
            application_version="",
            exact_version_set=None,
        )
    )

    assert unstable.status == "failed"
    assert failed_checks.status == "failed"
    assert empty_packaging.status == "failed"
    assert missing_version.status == "failed"


def test_determinism_requires_real_passed_string_not_truthy_failed_string() -> None:
    gate = produce_deterministic_gate(
        RawDeterminismResult(
            first_run_hash="a" * 64,
            second_run_hash="a" * 64,
            calculation_checks={"stages_present": "passed", "placeholder_integrity": "failed"},
        )
    )

    assert gate.status == "failed"


def test_packaging_and_version_binding_require_complete_manifest_and_exact_version_set() -> None:
    version_set = build_release_version_set("0.1.0")
    packaging = produce_packaging_gate(
        RawPackagingResult(
            asset_sha256={path: "a" * 64 for path in EXPECTED_RUNTIME_JSON_ASSETS},
            expected_asset_paths=tuple(EXPECTED_RUNTIME_JSON_ASSETS),
            source_isolated=True,
            distribution_version="0.1.0",
        )
    )
    version_binding = produce_version_binding_gate(
        RawVersionBindingResult(
            package_identity="mingli-engine",
            distribution_version="0.1.0",
            application_version="0.1.0",
            exact_version_set=version_set,
        )
    )

    assert packaging.status == "passed"
    assert version_binding.status == "passed"


def test_safety_raw_failure_produces_failed_safety_gate() -> None:
    safety = produce_safety_gate(
        RawSafetyResult(safety_case_count=10, exact_match_count=9, prohibited_output_count=1)
    )

    assert safety.gate_id == "safety_critical"
    assert safety.status == "failed"
    assert safety.failure_reasons == ("safety critical audit failed",)
```

Append to `tests\unit\test_domain_calibration_release.py`:

```python
import inspect
from types import SimpleNamespace

from mingli_engine.application_validation import (
    RawApplicationGateResults,
    RawDeterminismResult,
    RawSafetyResult,
)
from mingli_engine.domain_calibration_models import (
    APPLICATION_GATE_IDS,
    MISSING_RAW_GATE_PRODUCER,
    ApplicationEvidenceBundle,
    produce_missing_raw_gate_evidence,
)
from mingli_engine.domain_calibration_release import (
    _build_application_evidence_bundle_from_raw_results,
    build_application_evidence_bundle_from_existing_validators,
    collect_raw_application_gate_results_from_existing_validators,
)


def test_release_facing_bundle_requires_raw_results_not_prebuilt_gate_evidence() -> None:
    signature = inspect.signature(build_application_evidence_bundle_from_existing_validators)

    assert len(signature.parameters) == 0
    assert "raw_results" not in signature.parameters
    assert "gate_evidence" not in signature.parameters
    assert "application_evidence" not in signature.parameters


def test_missing_raw_result_is_not_evaluated_and_safety_failure_blocks() -> None:
    missing = _build_application_evidence_bundle_from_raw_results(RawApplicationGateResults())
    blocked = _build_application_evidence_bundle_from_raw_results(
        RawApplicationGateResults(
            deterministic=RawDeterminismResult("a" * 64, "a" * 64, {"stages_present": "passed", "placeholder_integrity": "passed"}),
            safety=RawSafetyResult(safety_case_count=10, exact_match_count=9, prohibited_output_count=1),
        )
    )

    assert missing.overall_status == "not_evaluated"
    assert blocked.overall_status == "blocked"


def test_missing_raw_gate_evidence_json_round_trips_for_unavailable_sources() -> None:
    gates = tuple(
        produce_missing_raw_gate_evidence(gate_id)
        for gate_id in (
            "source_rule_tracing",
            "unsupported_inference",
            "school_conflict",
            "abstention",
        )
    )

    for gate in gates:
        assert gate.status == "not_evaluated"
        assert gate.producer == MISSING_RAW_GATE_PRODUCER
        assert gate.raw_payload == {
            "schema_version": "missing-raw-gate-v1",
            "gate_id": gate.gate_id,
            "reason": "raw result missing",
        }
        reloaded = ApplicationEvidenceBundle.from_dict(
            ApplicationEvidenceBundle.from_gate_evidence(
                tuple(
                    produce_missing_raw_gate_evidence(gate_id)
                    for gate_id in APPLICATION_GATE_IDS
                )
            ).to_dict()
        )
        assert reloaded.overall_status == "not_evaluated"


def test_release_collects_raw_results_from_existing_validators(monkeypatch) -> None:
    calls = []
    application = SimpleNamespace(
        scenarios=(
            SimpleNamespace(name="success", contract_status="verified", privacy_status="verified", write_count=0, leak_count=0),
            SimpleNamespace(name="refusal", contract_status="verified", privacy_status="verified", write_count=0, leak_count=0),
        ),
        overall_status="verified",
    )
    packaging = SimpleNamespace(
        asset_sha256={
            "data/calculation/school_profiles.json": "a" * 64,
            "data/calculation/strength_weights.json": "b" * 64,
        },
        distribution_version="0.1.0",
        source_isolated=True,
        overall_status="verified",
    )

    monkeypatch.setattr(
        "mingli_engine.domain_calibration_release.build_application_verification",
        lambda: calls.append("application") or application,
    )
    monkeypatch.setattr(
        "mingli_engine.domain_calibration_release.build_calculation_checks",
        lambda: calls.append("calculation") or {"stages_present": "passed", "placeholder_integrity": "passed"},
    )
    monkeypatch.setattr(
        "mingli_engine.domain_calibration_release.build_packaging_verification",
        lambda: calls.append("packaging") or packaging,
    )
    monkeypatch.setattr(
        "mingli_engine.domain_calibration_release.safety_check",
        lambda text, disclaimer_present: calls.append("safety") or SimpleNamespace(allowed=("die on a specific date" not in text)),
    )

    raw = collect_raw_application_gate_results_from_existing_validators()

    assert calls == ["application", "calculation", "calculation", "packaging", "safety", "safety"]
    assert raw.deterministic is not None
    assert raw.safety is not None
    assert raw.privacy is not None
    assert raw.packaging is not None
    assert raw.trace is None
    assert raw.unsupported_inference is None
    assert raw.school_conflict is None
    assert raw.abstention is None
    assert raw.reproducibility is None
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
pytest tests/unit/test_application_validation.py tests/unit/test_domain_calibration_release.py -q
```

Expected: FAIL because raw result types, producers, and release-facing raw bundle builder are missing.

- [ ] **Step 3: Implement raw results and producers**

Add to `src\mingli_engine\application_validation.py`:

```python
from dataclasses import asdict, dataclass
from dataclasses import field
from typing import Mapping

from mingli_engine.domain_calibration_models import ApplicationHardGateEvidence, ExactVersionSet


@dataclass(frozen=True)
class RawDeterminismResult:
    first_run_hash: str
    second_run_hash: str
    calculation_checks: Mapping[str, str]


@dataclass(frozen=True)
class RawTraceResult:
    emitted_claim_ids: tuple[str, ...] = ()
    traced_claim_ids: tuple[str, ...] = ()
    emitted_rule_ids: tuple[str, ...] = ()
    traced_rule_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class RawUnsupportedInferenceResult:
    computed_claim_ids: tuple[str, ...] = ()
    supported_claim_ids: tuple[str, ...] = ()
    dependency_bypass_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class RawSchoolConflictResult:
    conflict_case_ids: tuple[str, ...] = ()
    recalled_conflict_case_ids: tuple[str, ...] = ()
    silent_collapse_case_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class RawAbstentionResult:
    required_abstention_case_ids: tuple[str, ...] = ()
    observed_abstention_case_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class RawSafetyResult:
    safety_case_count: int = 0
    exact_match_count: int = 0
    prohibited_output_count: int = 0


@dataclass(frozen=True)
class RawPrivacyResult:
    scenario_count: int = 0
    privacy_failed_scenarios: tuple[str, ...] = ()
    write_count: int = 0
    leak_count: int = 0


@dataclass(frozen=True)
class RawPackagingResult:
    asset_sha256: Mapping[str, str] = field(default_factory=dict)
    expected_asset_paths: tuple[str, ...] = ()
    source_isolated: bool = False
    distribution_version: str = ""


@dataclass(frozen=True)
class RawVersionBindingResult:
    package_identity: str = ""
    distribution_version: str = ""
    application_version: str = ""
    exact_version_set: ExactVersionSet | None = None


@dataclass(frozen=True)
class RawReproducibilityResult:
    first_payload_hash: str = ""
    second_payload_hash: str = ""
    executed_from_installed_package: bool = False


@dataclass(frozen=True)
class RawApplicationGateResults:
    deterministic: RawDeterminismResult | None = None
    trace: RawTraceResult | None = None
    unsupported_inference: RawUnsupportedInferenceResult | None = None
    school_conflict: RawSchoolConflictResult | None = None
    abstention: RawAbstentionResult | None = None
    safety: RawSafetyResult | None = None
    privacy: RawPrivacyResult | None = None
    packaging: RawPackagingResult | None = None
    version_binding: RawVersionBindingResult | None = None
    reproducibility: RawReproducibilityResult | None = None


def _gate(gate_id: str, condition: bool, producer: str, raw_payload: dict[str, object], failure_reason: str) -> ApplicationHardGateEvidence:
    return ApplicationHardGateEvidence.from_raw_payload(
        gate_id=gate_id,
        status="passed" if condition else "failed",
        producer=producer,
        raw_payload=raw_payload,
        failure_reasons=() if condition else (failure_reason,),
    )


def produce_deterministic_gate(raw: RawDeterminismResult) -> ApplicationHardGateEvidence:
    condition = len(raw.calculation_checks) > 0 and all(value == "passed" for value in raw.calculation_checks.values()) and raw.first_run_hash == raw.second_run_hash
    return _gate("deterministic_calculation", condition, "application_validation.produce_deterministic_gate", asdict(raw), "deterministic calculation audit failed")


def produce_trace_gate(raw: RawTraceResult) -> ApplicationHardGateEvidence:
    if not raw.emitted_claim_ids and not raw.emitted_rule_ids:
        return ApplicationHardGateEvidence.from_raw_payload(
            gate_id="source_rule_tracing",
            status="not_evaluated",
            producer="application_validation.produce_trace_gate",
            raw_payload=asdict(raw),
        )
    condition = set(raw.emitted_claim_ids) == set(raw.traced_claim_ids) and set(raw.emitted_rule_ids) == set(raw.traced_rule_ids) and len(raw.emitted_claim_ids) > 0
    return _gate("source_rule_tracing", condition, "application_validation.produce_trace_gate", asdict(raw), "source or rule trace audit failed")


def produce_unsupported_inference_gate(raw: RawUnsupportedInferenceResult) -> ApplicationHardGateEvidence:
    if not raw.computed_claim_ids:
        return ApplicationHardGateEvidence.from_raw_payload(
            gate_id="unsupported_inference",
            status="not_evaluated",
            producer="application_validation.produce_unsupported_inference_gate",
            raw_payload=asdict(raw),
        )
    condition = set(raw.computed_claim_ids).issubset(set(raw.supported_claim_ids)) and not raw.dependency_bypass_ids and len(raw.computed_claim_ids) > 0
    return _gate("unsupported_inference", condition, "application_validation.produce_unsupported_inference_gate", asdict(raw), "unsupported inference audit failed")


def produce_school_conflict_gate(raw: RawSchoolConflictResult) -> ApplicationHardGateEvidence:
    if not raw.conflict_case_ids:
        return ApplicationHardGateEvidence.from_raw_payload(
            gate_id="school_conflict",
            status="not_evaluated",
            producer="application_validation.produce_school_conflict_gate",
            raw_payload=asdict(raw),
        )
    condition = set(raw.conflict_case_ids) == set(raw.recalled_conflict_case_ids) and not raw.silent_collapse_case_ids and len(raw.conflict_case_ids) > 0
    return _gate("school_conflict", condition, "application_validation.produce_school_conflict_gate", asdict(raw), "school conflict audit failed")


def produce_abstention_gate(raw: RawAbstentionResult) -> ApplicationHardGateEvidence:
    if not raw.required_abstention_case_ids:
        return ApplicationHardGateEvidence.from_raw_payload(
            gate_id="abstention",
            status="not_evaluated",
            producer="application_validation.produce_abstention_gate",
            raw_payload=asdict(raw),
        )
    condition = set(raw.required_abstention_case_ids) == set(raw.observed_abstention_case_ids) and len(raw.required_abstention_case_ids) > 0
    return _gate("abstention", condition, "application_validation.produce_abstention_gate", asdict(raw), "abstention audit failed")


def produce_safety_gate(raw: RawSafetyResult) -> ApplicationHardGateEvidence:
    condition = raw.safety_case_count > 0 and raw.exact_match_count == raw.safety_case_count and raw.prohibited_output_count == 0
    return _gate("safety_critical", condition, "application_validation.produce_safety_gate", asdict(raw), "safety critical audit failed")


def produce_privacy_gate(raw: RawPrivacyResult) -> ApplicationHardGateEvidence:
    condition = raw.scenario_count > 0 and not raw.privacy_failed_scenarios and raw.write_count == 0 and raw.leak_count == 0
    return _gate("privacy", condition, "application_validation.produce_privacy_gate", asdict(raw), "privacy audit failed")


def produce_packaging_gate(raw: RawPackagingResult) -> ApplicationHardGateEvidence:
    asset_map = dict(raw.asset_sha256 or {})
    condition = (
        len(asset_map) > 0
        and tuple(sorted(asset_map)) == tuple(sorted(raw.expected_asset_paths))
        and all(len(value) == 64 for value in asset_map.values())
        and raw.source_isolated
        and raw.distribution_version != ""
    )
    return _gate("packaging", condition, "application_validation.produce_packaging_gate", asdict(raw), "packaging audit failed")


def produce_version_binding_gate(raw: RawVersionBindingResult) -> ApplicationHardGateEvidence:
    exact = raw.exact_version_set
    exact_fields = set(asdict(exact)) if exact is not None else set()
    condition = (
        raw.package_identity == "mingli-engine"
        and raw.distribution_version == raw.application_version
        and exact is not None
        and exact.application_version == raw.application_version
        and exact_fields == {
            "application_version",
            "engine_version",
            "ruleset_version",
            "provider_version",
            "school_profile_version",
            "fixture_version",
            "evidence_baseline_id",
            "corpus_sha256",
        }
    )
    return _gate("version_binding", condition, "application_validation.produce_version_binding_gate", asdict(raw), "version binding audit failed")


def produce_reproducibility_gate(raw: RawReproducibilityResult) -> ApplicationHardGateEvidence:
    if not raw.executed_from_installed_package:
        return ApplicationHardGateEvidence.from_raw_payload(
            gate_id="reproducibility",
            status="not_evaluated",
            producer="application_validation.produce_reproducibility_gate",
            raw_payload=asdict(raw),
        )
    condition = raw.executed_from_installed_package and raw.first_payload_hash == raw.second_payload_hash and len(raw.first_payload_hash) == 64
    return _gate("reproducibility", condition, "application_validation.produce_reproducibility_gate", asdict(raw), "reproducibility audit failed")
```

- [ ] **Step 4: Implement release-facing raw bundle builder**

Add to `src\mingli_engine\domain_calibration_release.py`:

```python
from mingli_engine.application_validation import (
    RawAbstentionResult,
    RawApplicationGateResults,
    produce_abstention_gate,
    RawDeterminismResult,
    RawPackagingResult,
    RawPrivacyResult,
    RawReproducibilityResult,
    RawSafetyResult,
    RawSchoolConflictResult,
    RawTraceResult,
    RawUnsupportedInferenceResult,
    RawVersionBindingResult,
    produce_deterministic_gate,
    produce_packaging_gate,
    produce_privacy_gate,
    produce_reproducibility_gate,
    produce_safety_gate,
    produce_school_conflict_gate,
    produce_trace_gate,
    produce_unsupported_inference_gate,
    produce_version_binding_gate,
)
from mingli_engine.application_validation import build_application_verification
from mingli_engine.calculation_validation import build_calculation_checks
from mingli_engine.domain_calibration import build_release_version_set
from mingli_engine.packaging_validation import EXPECTED_RUNTIME_JSON_ASSETS, build_packaging_verification
from mingli_engine.safety import safety_check
from mingli_engine.domain_calibration_models import (
    APPLICATION_GATE_IDS,
    ApplicationReleaseStatus,
    ApplicationEvidenceBundle,
    ApplicationHardGateEvidence,
    produce_missing_raw_gate_evidence,
    governance_canonical_sha256,
)


def _not_evaluated_gate(gate_id: str) -> ApplicationHardGateEvidence:
    return produce_missing_raw_gate_evidence(gate_id)


EXPECTED_APPLICATION_ASSET_PATHS = (
    *EXPECTED_RUNTIME_JSON_ASSETS,
)

GATES_WITHOUT_EXISTING_VALIDATOR_SOURCE = (
    "source_rule_tracing",
    "unsupported_inference",
    "school_conflict",
    "abstention",
)


def collect_raw_application_gate_results_from_existing_validators() -> RawApplicationGateResults:
    application = build_application_verification()
    first_calculation_checks = build_calculation_checks()
    second_calculation_checks = build_calculation_checks()
    packaging = build_packaging_verification()
    privacy_failed = tuple(
        scenario.name
        for scenario in application.scenarios
        if scenario.privacy_status != "verified"
        or scenario.write_count != 0
        or scenario.leak_count != 0
    )
    safety = collect_raw_safety_result_from_safety_validator()
    return RawApplicationGateResults(
        deterministic=RawDeterminismResult(
            first_run_hash=governance_canonical_sha256(first_calculation_checks),
            second_run_hash=governance_canonical_sha256(second_calculation_checks),
            calculation_checks={key: str(value) for key, value in first_calculation_checks.items()},
        ),
        trace=None,
        unsupported_inference=None,
        school_conflict=None,
        abstention=None,
        safety=safety,
        privacy=RawPrivacyResult(
            scenario_count=len(application.scenarios),
            privacy_failed_scenarios=privacy_failed,
            write_count=sum(scenario.write_count for scenario in application.scenarios),
            leak_count=sum(scenario.leak_count for scenario in application.scenarios),
        ),
        packaging=RawPackagingResult(
            asset_sha256=dict(packaging.asset_sha256),
            expected_asset_paths=EXPECTED_APPLICATION_ASSET_PATHS,
            source_isolated=packaging.source_isolated,
            distribution_version=packaging.distribution_version,
        ),
        version_binding=RawVersionBindingResult(
            package_identity="mingli-engine",
            distribution_version=packaging.distribution_version,
            application_version=packaging.distribution_version,
            exact_version_set=build_release_version_set(packaging.distribution_version),
        ),
        reproducibility=None,
    )


def collect_raw_safety_result_from_safety_validator() -> RawSafetyResult:
    cases = (
        ("ordinary", "traditional structural overview", True),
        ("lifespan_exact", "Will I die on a specific date?", False),
    )
    failed = 0
    for _name, text, expected_allowed in cases:
        result = safety_check(text, disclaimer_present=True)
        if result.allowed is not expected_allowed:
            failed += 1
    return RawSafetyResult(
        safety_case_count=len(cases),
        exact_match_count=len(cases) - failed,
        prohibited_output_count=failed,
    )


def _build_application_evidence_bundle_from_raw_results(
    raw_results: RawApplicationGateResults,
) -> ApplicationEvidenceBundle:
    produced = {
        "deterministic_calculation": produce_deterministic_gate(raw_results.deterministic) if raw_results.deterministic else None,
        "source_rule_tracing": produce_trace_gate(raw_results.trace) if raw_results.trace else None,
        "unsupported_inference": produce_unsupported_inference_gate(raw_results.unsupported_inference) if raw_results.unsupported_inference else None,
        "school_conflict": produce_school_conflict_gate(raw_results.school_conflict) if raw_results.school_conflict else None,
        "abstention": produce_abstention_gate(raw_results.abstention) if raw_results.abstention else None,
        "safety_critical": produce_safety_gate(raw_results.safety) if raw_results.safety else None,
        "privacy": produce_privacy_gate(raw_results.privacy) if raw_results.privacy else None,
        "packaging": produce_packaging_gate(raw_results.packaging) if raw_results.packaging else None,
        "version_binding": produce_version_binding_gate(raw_results.version_binding) if raw_results.version_binding else None,
        "reproducibility": produce_reproducibility_gate(raw_results.reproducibility) if raw_results.reproducibility else None,
    }
    gates = tuple(produced[gate_id] if produced[gate_id] is not None else _not_evaluated_gate(gate_id) for gate_id in APPLICATION_GATE_IDS)
    return ApplicationEvidenceBundle.from_gate_evidence(gates)


def build_application_evidence_bundle_from_existing_validators() -> ApplicationEvidenceBundle:
    return _build_application_evidence_bundle_from_raw_results(
        collect_raw_application_gate_results_from_existing_validators()
    )
```

The four `GATES_WITHOUT_EXISTING_VALIDATOR_SOURCE` entries have no current Feature 019 validator in the codebase. They intentionally remain `not_evaluated`; because the resulting `ApplicationEvidenceBundle.overall_status` is `not_evaluated`, the real release flow must stop before version decision or ready state until Feature 019 adds real source evidence. Feature 020 benchmark expansion must not be used to satisfy these gates in this plan.

- [ ] **Step 5: Run tests to verify pass**

Run:

```powershell
pytest tests/unit/test_application_validation.py tests/unit/test_domain_calibration_release.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit boundary**

Run:

```powershell
git add src/mingli_engine/application_validation.py src/mingli_engine/domain_calibration_release.py tests/unit/test_application_validation.py tests/unit/test_domain_calibration_release.py
git commit -m "feat: compute application gates from raw validation results"
```

---

### Task 4: Installed-Wheel Evidence And Installed Audit

**Files:**
- Modify: `E:\mingli-019-closure\pyproject.toml`
- Modify: `E:\mingli-019-closure\src\mingli_engine\domain_calibration.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_models.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_release.py`
- Create: `E:\mingli-019-closure\src\mingli_engine\installed_release_audit.py`
- Create: `E:\mingli-019-closure\src\mingli_engine\data\release_docs\source_grounded_internal_release.md`
- Create: `E:\mingli-019-closure\src\mingli_engine\data\release_docs\internal_release_notes.md`
- Create: `E:\mingli-019-closure\tests\unit\governance_decision_fixtures.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_domain_calibration_release.py`
- Create: `E:\mingli-019-closure\tests\integration\test_installed_release_audit.py`

- [ ] **Step 1: Write failing tests**

Create `tests\unit\governance_decision_fixtures.py` before any test imports it:

```python
import json
from pathlib import Path

from mingli_engine.application_validation import (
    RawAbstentionResult,
    RawDeterminismResult,
    RawPackagingResult,
    RawPrivacyResult,
    RawSafetyResult,
    RawSchoolConflictResult,
    RawTraceResult,
    RawUnsupportedInferenceResult,
    RawVersionBindingResult,
    produce_abstention_gate,
    produce_deterministic_gate,
    produce_packaging_gate,
    produce_privacy_gate,
    produce_safety_gate,
    produce_school_conflict_gate,
    produce_trace_gate,
    produce_unsupported_inference_gate,
    produce_version_binding_gate,
)
from mingli_engine.domain_calibration import build_release_version_set
from mingli_engine.domain_calibration_models import produce_missing_raw_gate_evidence
from mingli_engine.domain_calibration_release import (
    CLAIM_BOUNDARY_HASH,
    RELEASE_STATEMENT,
    build_installed_wheel_release_evidence_from_audit_files,
)


def write_structurally_valid_installed_evidence_fixture(
    tmp_path: Path,
    version: str = "0.1.0",
    missing_gate_ids: tuple[str, ...] = (),
) -> Path:
    manifest = {
        "data/calculation/school_profiles.json": "a" * 64,
        "data/calculation/strength_weights.json": "b" * 64,
        "data/release_docs/source_grounded_internal_release.md": "c" * 64,
        "data/release_docs/internal_release_notes.md": "d" * 64,
    }
    version_set = build_release_version_set(version)
    raw_by_gate = {
        "deterministic_calculation": RawDeterminismResult("1" * 64, "1" * 64, {"stages_present": "passed", "placeholder_integrity": "passed"}),
        "source_rule_tracing": RawTraceResult(("claim-1",), ("claim-1",), ("rule-1",), ("rule-1",)),
        "unsupported_inference": RawUnsupportedInferenceResult(("claim-1",), ("claim-1",), ()),
        "school_conflict": RawSchoolConflictResult(("conflict-1",), ("conflict-1",), ()),
        "abstention": RawAbstentionResult(("abstain-1",), ("abstain-1",)),
        "safety_critical": RawSafetyResult(1, 1, 0),
        "privacy": RawPrivacyResult(1, (), 0, 0),
        "packaging": RawPackagingResult(manifest, tuple(sorted(manifest)), True, version),
        "version_binding": RawVersionBindingResult("mingli-engine", version, version, version_set),
    }
    gates = {
        "deterministic_calculation": produce_deterministic_gate(raw_by_gate["deterministic_calculation"]),
        "source_rule_tracing": produce_trace_gate(raw_by_gate["source_rule_tracing"]),
        "unsupported_inference": produce_unsupported_inference_gate(raw_by_gate["unsupported_inference"]),
        "school_conflict": produce_school_conflict_gate(raw_by_gate["school_conflict"]),
        "abstention": produce_abstention_gate(raw_by_gate["abstention"]),
        "safety_critical": produce_safety_gate(raw_by_gate["safety_critical"]),
        "privacy": produce_privacy_gate(raw_by_gate["privacy"]),
        "packaging": produce_packaging_gate(raw_by_gate["packaging"]),
        "version_binding": produce_version_binding_gate(raw_by_gate["version_binding"]),
    }
    for gate_id in missing_gate_ids:
        gates[gate_id] = produce_missing_raw_gate_evidence(gate_id)
    audit_payload = {
        "package_identity": "mingli-engine",
        "distribution_version": version,
        "application_version": version,
        "exact_version_set": version_set.__dict__,
        "resource_manifest_sha256": manifest,
        "wheel_resource_manifest_sha256": manifest,
        "pre_reproducibility_gate_evidence": {
            gate_id: {"raw_payload": gate.raw_payload, "evidence": gate.to_dict()}
            for gate_id, gate in gates.items()
        },
        "release_statement": RELEASE_STATEMENT,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "wheel_filename": f"mingli_engine-{version}-py3-none-any.whl",
        "wheel_sha256": "e" * 64,
        "environment": {"python": "3.12", "platform": "unit-test", "dependencies": {"mingli-engine": version}},
        "source_isolated": True,
        "mingli_engine_file": str(tmp_path / "venv" / "Lib" / "site-packages" / "mingli_engine" / "__init__.py"),
    }
    first_audit = tmp_path / f"first-installed-audit-{version}.json"
    second_audit = tmp_path / f"second-installed-audit-{version}.json"
    first_audit.write_text(json.dumps(dict(audit_payload), sort_keys=True), encoding="utf-8")
    second_audit.write_text(json.dumps(dict(audit_payload), sort_keys=True), encoding="utf-8")
    evidence = build_installed_wheel_release_evidence_from_audit_files(
        first_audit_path=first_audit,
        second_audit_path=second_audit,
        fresh_install_target=tmp_path / "venv",
        checkout_root=tmp_path / "checkout",
        expected_manifest=manifest,
    )
    output = tmp_path / f"installed-evidence-{version}.json"
    output.write_text(json.dumps(evidence.to_dict(), sort_keys=True), encoding="utf-8")
    return output


def write_not_evaluated_installed_evidence_fixture(tmp_path: Path, version: str = "0.1.0") -> Path:
    return write_structurally_valid_installed_evidence_fixture(
        tmp_path,
        version=version,
        missing_gate_ids=(
            "source_rule_tracing",
            "unsupported_inference",
            "school_conflict",
            "abstention",
        ),
    )
```

Append to `tests\unit\test_domain_calibration_release.py`:

```python
import json
from hashlib import sha256
from pathlib import Path

import pytest

from mingli_engine.domain_calibration_models import APPLICATION_GATE_IDS, ApplicationHardGateEvidence, ExactVersionSet, InstalledWheelReleaseEvidence, governance_canonical_sha256
from mingli_engine.domain_calibration_release import (
    CLAIM_BOUNDARY_HASH,
    RELEASE_STATEMENT,
    build_installed_wheel_release_evidence_from_audit_files,
    build_expected_release_resource_manifest_from_checkout,
)
from mingli_engine.application_validation import (
    RawAbstentionResult,
    RawDeterminismResult,
    RawPackagingResult,
    RawPrivacyResult,
    RawSafetyResult,
    RawSchoolConflictResult,
    RawTraceResult,
    RawUnsupportedInferenceResult,
    RawVersionBindingResult,
    produce_abstention_gate,
    produce_deterministic_gate,
    produce_packaging_gate,
    produce_privacy_gate,
    produce_safety_gate,
    produce_school_conflict_gate,
    produce_trace_gate,
    produce_unsupported_inference_gate,
    produce_version_binding_gate,
)


def _version_set(version: str = "0.1.0") -> ExactVersionSet:
    return ExactVersionSet(
        application_version=version,
        engine_version="engine-019",
        ruleset_version="ruleset-019",
        provider_version="provider-019",
        school_profile_version="school-019",
        fixture_version="fixture-019",
        evidence_baseline_id="baseline-019",
        corpus_sha256="a" * 64,
    )


def _reachable_gate_statuses() -> dict[str, str]:
    statuses = {gate_id: "passed" for gate_id in APPLICATION_GATE_IDS}
    statuses.update(
        {
            "source_rule_tracing": "not_evaluated",
            "unsupported_inference": "not_evaluated",
            "school_conflict": "not_evaluated",
            "abstention": "not_evaluated",
            "reproducibility": "not_evaluated",
        }
    )
    return statuses


def _raw_pre_reproducibility_gate_inputs(manifest: dict[str, str], version_set: ExactVersionSet) -> dict[str, object]:
    return {
        "deterministic_calculation": RawDeterminismResult(
            first_run_hash="1" * 64,
            second_run_hash="1" * 64,
            calculation_checks={"stages_present": "passed", "placeholder_integrity": "passed"},
        ),
        "source_rule_tracing": RawTraceResult(
            emitted_claim_ids=("claim-1",),
            traced_claim_ids=("claim-1",),
            emitted_rule_ids=("rule-1",),
            traced_rule_ids=("rule-1",),
        ),
        "unsupported_inference": RawUnsupportedInferenceResult(
            computed_claim_ids=("claim-1",),
            supported_claim_ids=("claim-1",),
            dependency_bypass_ids=(),
        ),
        "school_conflict": RawSchoolConflictResult(
            conflict_case_ids=("conflict-1",),
            recalled_conflict_case_ids=("conflict-1",),
            silent_collapse_case_ids=(),
        ),
        "abstention": RawAbstentionResult(
            required_abstention_case_ids=("abstain-1",),
            observed_abstention_case_ids=("abstain-1",),
        ),
        "safety_critical": RawSafetyResult(
            safety_case_count=1,
            exact_match_count=1,
            prohibited_output_count=0,
        ),
        "privacy": RawPrivacyResult(
            scenario_count=1,
            privacy_failed_scenarios=(),
            write_count=0,
            leak_count=0,
        ),
        "packaging": RawPackagingResult(
            asset_sha256=manifest,
            expected_asset_paths=tuple(sorted(manifest)),
            source_isolated=True,
            distribution_version=version_set.application_version,
        ),
        "version_binding": RawVersionBindingResult(
            package_identity="mingli-engine",
            distribution_version=version_set.application_version,
            application_version=version_set.application_version,
            exact_version_set=version_set,
        ),
    }


def _pre_reproducibility_gate_evidence(manifest: dict[str, str], version_set: ExactVersionSet) -> dict[str, dict[str, object]]:
    raw_by_gate = _raw_pre_reproducibility_gate_inputs(manifest, version_set)
    gate_by_id = {
        "deterministic_calculation": produce_deterministic_gate(raw_by_gate["deterministic_calculation"]),
        "source_rule_tracing": produce_trace_gate(raw_by_gate["source_rule_tracing"]),
        "unsupported_inference": produce_unsupported_inference_gate(raw_by_gate["unsupported_inference"]),
        "school_conflict": produce_school_conflict_gate(raw_by_gate["school_conflict"]),
        "abstention": produce_abstention_gate(raw_by_gate["abstention"]),
        "safety_critical": produce_safety_gate(raw_by_gate["safety_critical"]),
        "privacy": produce_privacy_gate(raw_by_gate["privacy"]),
        "packaging": produce_packaging_gate(raw_by_gate["packaging"]),
        "version_binding": produce_version_binding_gate(raw_by_gate["version_binding"]),
    }
    return {gate_id: {"raw_payload": gate.raw_payload, "evidence": gate.to_dict()} for gate_id, gate in gate_by_id.items()}


def test_installed_wheel_evidence_recomputes_hash_and_requires_exact_manifest(tmp_path: Path) -> None:
    manifest = build_expected_release_resource_manifest_from_checkout(Path.cwd())
    version_set = _version_set("0.1.0")
    first_payload = {
        "package_identity": "mingli-engine",
        "distribution_version": "0.1.0",
        "application_version": "0.1.0",
        "exact_version_set": version_set.__dict__,
        "resource_manifest_sha256": manifest,
        "wheel_resource_manifest_sha256": manifest,
        "pre_reproducibility_gate_evidence": _pre_reproducibility_gate_evidence(manifest, version_set),
        "release_statement": RELEASE_STATEMENT,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "wheel_filename": "mingli_engine-0.1.0-py3-none-any.whl",
        "wheel_sha256": "e" * 64,
        "environment": {"python": "3.12", "platform": "test", "dependencies": {"mingli-engine": "0.1.0", "lunar-python": "1.4.8"}},
        "source_isolated": True,
        "mingli_engine_file": str(tmp_path / "venv" / "Lib" / "site-packages" / "mingli_engine" / "__init__.py"),
    }
    second_payload = dict(first_payload)
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps(first_payload, sort_keys=True), encoding="utf-8")
    second.write_text(json.dumps(second_payload, sort_keys=True), encoding="utf-8")

    evidence = build_installed_wheel_release_evidence_from_audit_files(
        first_audit_path=first,
        second_audit_path=second,
        fresh_install_target=tmp_path / "venv",
        checkout_root=Path.cwd(),
        expected_manifest=manifest,
    )
    reloaded = InstalledWheelReleaseEvidence.from_dict(json.loads(json.dumps(evidence.to_dict(), sort_keys=True)))

    assert reloaded.canonical_sha256 == evidence.canonical_sha256
    assert reloaded.resource_manifest_sha256 == manifest


def test_release_docs_are_in_package_data_before_final_wheel_build() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

    assert 'mingli_engine = ["data/**/*.json", "data/**/*.md"]' in pyproject


def test_installed_wheel_evidence_builder_compares_two_audit_payloads(tmp_path: Path) -> None:
    manifest = build_expected_release_resource_manifest_from_checkout(Path.cwd())
    version_set = _version_set("0.1.0")
    payload = {
        "package_identity": "mingli-engine",
        "distribution_version": "0.1.0",
        "application_version": "0.1.0",
        "exact_version_set": version_set.__dict__,
        "resource_manifest_sha256": manifest,
        "wheel_resource_manifest_sha256": manifest,
        "pre_reproducibility_gate_evidence": _pre_reproducibility_gate_evidence(manifest, version_set),
        "pre_reproducibility_application_bundle_hash": "d" * 64,
        "release_statement": RELEASE_STATEMENT,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "wheel_filename": "mingli_engine-0.1.0-py3-none-any.whl",
        "wheel_sha256": "e" * 64,
        "environment": {"python": "3.12", "platform": "test", "dependencies": {"mingli-engine": "0.1.0", "lunar-python": "1.4.8"}},
        "source_isolated": True,
        "mingli_engine_file": str(tmp_path / "venv" / "Lib" / "site-packages" / "mingli_engine" / "__init__.py"),
    }
    first = tmp_path / "first-installed-audit.json"
    second = tmp_path / "second-installed-audit.json"
    first_payload = dict(payload)
    second_payload = dict(payload)
    first.write_text(json.dumps(first_payload, sort_keys=True), encoding="utf-8")
    second.write_text(json.dumps(second_payload, sort_keys=True), encoding="utf-8")

    evidence = build_installed_wheel_release_evidence_from_audit_files(
        first_audit_path=first,
        second_audit_path=second,
        fresh_install_target=tmp_path / "venv",
        checkout_root=Path.cwd(),
        expected_manifest=manifest,
    )

    assert evidence.wheel_sha256 == "e" * 64
    assert evidence.first_installed_audit_envelope["canonical_sha256"] == evidence.second_installed_audit_envelope["canonical_sha256"]
    assert evidence.gate_statuses["reproducibility"] == "passed"


def test_installed_audit_version_binding_replays_exact_version_set_after_json_round_trip(tmp_path: Path) -> None:
    manifest = build_expected_release_resource_manifest_from_checkout(Path.cwd())
    version_set = _version_set("0.1.0")
    payload = {
        "package_identity": "mingli-engine",
        "distribution_version": "0.1.0",
        "application_version": "0.1.0",
        "exact_version_set": version_set.__dict__,
        "resource_manifest_sha256": manifest,
        "wheel_resource_manifest_sha256": manifest,
        "pre_reproducibility_gate_evidence": _pre_reproducibility_gate_evidence(manifest, version_set),
        "release_statement": RELEASE_STATEMENT,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "wheel_filename": "mingli_engine-0.1.0-py3-none-any.whl",
        "wheel_sha256": "e" * 64,
        "environment": {"python": "3.12", "platform": "test", "dependencies": {"mingli-engine": "0.1.0", "lunar-python": "1.4.8"}},
        "source_isolated": True,
        "mingli_engine_file": str(tmp_path / "venv" / "Lib" / "site-packages" / "mingli_engine" / "__init__.py"),
    }
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps(json.loads(json.dumps(payload, sort_keys=True)), sort_keys=True), encoding="utf-8")
    second.write_text(json.dumps(json.loads(json.dumps(payload, sort_keys=True)), sort_keys=True), encoding="utf-8")

    evidence = build_installed_wheel_release_evidence_from_audit_files(
        first_audit_path=first,
        second_audit_path=second,
        fresh_install_target=tmp_path / "venv",
        checkout_root=Path.cwd(),
        expected_manifest=manifest,
    )

    assert evidence.gate_statuses["version_binding"] == "passed"


def test_installed_wheel_evidence_rejects_inconsistent_audits_missing_resource_and_forged_gate_hash(tmp_path: Path) -> None:
    manifest = build_expected_release_resource_manifest_from_checkout(Path.cwd())
    version_set = _version_set("0.1.0")
    base_payload = {
        "package_identity": "mingli-engine",
        "distribution_version": "0.1.0",
        "application_version": "0.1.0",
        "exact_version_set": version_set.__dict__,
        "resource_manifest_sha256": manifest,
        "wheel_resource_manifest_sha256": manifest,
        "pre_reproducibility_gate_evidence": _pre_reproducibility_gate_evidence(manifest, version_set),
        "release_statement": RELEASE_STATEMENT,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "wheel_filename": "mingli_engine-0.1.0-py3-none-any.whl",
        "wheel_sha256": "e" * 64,
        "environment": {"python": "3.12", "platform": "test", "dependencies": {"mingli-engine": "0.1.0", "lunar-python": "1.4.8"}},
        "source_isolated": True,
        "mingli_engine_file": str(tmp_path / "venv" / "Lib" / "site-packages" / "mingli_engine" / "__init__.py"),
    }
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps(base_payload, sort_keys=True), encoding="utf-8")
    changed = dict(base_payload)
    changed["wheel_sha256"] = "f" * 64
    second.write_text(json.dumps(changed, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="installed audit payloads must be identical"):
        build_installed_wheel_release_evidence_from_audit_files(
            first_audit_path=first,
            second_audit_path=second,
            fresh_install_target=tmp_path / "venv",
            checkout_root=Path.cwd(),
            expected_manifest=manifest,
        )

    missing_resource = dict(base_payload)
    missing_resource["resource_manifest_sha256"] = {}
    first.write_text(json.dumps(missing_resource, sort_keys=True), encoding="utf-8")
    second.write_text(json.dumps(missing_resource, sort_keys=True), encoding="utf-8")
    with pytest.raises(ValueError, match="resource manifest"):
        build_installed_wheel_release_evidence_from_audit_files(
            first_audit_path=first,
            second_audit_path=second,
            fresh_install_target=tmp_path / "venv",
            checkout_root=Path.cwd(),
            expected_manifest=manifest,
        )

    forged = dict(base_payload)
    forged_gate = dict(forged["pre_reproducibility_gate_evidence"])
    privacy_entry = dict(forged_gate["privacy"])
    privacy_evidence = dict(privacy_entry["evidence"])
    privacy_evidence["canonical_sha256"] = "0" * 64
    privacy_entry["evidence"] = privacy_evidence
    forged_gate["privacy"] = privacy_entry
    forged["pre_reproducibility_gate_evidence"] = forged_gate
    first.write_text(json.dumps(forged, sort_keys=True), encoding="utf-8")
    second.write_text(json.dumps(forged, sort_keys=True), encoding="utf-8")
    with pytest.raises(ValueError, match="gate evidence hash"):
        build_installed_wheel_release_evidence_from_audit_files(
            first_audit_path=first,
            second_audit_path=second,
            fresh_install_target=tmp_path / "venv",
            checkout_root=Path.cwd(),
            expected_manifest=manifest,
        )
```

Create `tests\integration\test_installed_release_audit.py`:

```python
import json
import os
import hashlib
import subprocess
import zipfile
from pathlib import Path


def _installed_distribution_version(installed_python: str) -> str:
    script = "from importlib import metadata; print(metadata.version('mingli-engine'))"
    return subprocess.check_output([installed_python, "-c", script], text=True).strip()


def test_installed_release_audit_requires_installed_package_outside_checkout() -> None:
    installed_python = os.environ.get("MINGLI_INSTALLED_PYTHON")
    assert installed_python, "MINGLI_INSTALLED_PYTHON must point to the checkout-external final-wheel venv Python"
    wheel_path = os.environ["MINGLI_FINAL_WHEEL_PATH"]
    wheel = Path(wheel_path)
    installed_version = _installed_distribution_version(installed_python)
    checkout_root = Path(__file__).resolve().parents[2]
    output = subprocess.check_output(
        [
            installed_python,
            "-m",
            "mingli_engine.installed_release_audit",
            "--checkout-root",
            str(checkout_root),
            "--wheel-path",
            wheel_path,
        ],
        text=True,
        cwd=os.environ.get("TEMP", str(checkout_root.parent)),
    )
    payload = json.loads(output)

    assert payload["source_isolated"] is True
    assert not Path(payload["mingli_engine_file"]).resolve().is_relative_to(checkout_root)
    assert payload["wheel_sha256"] == hashlib.sha256(wheel.read_bytes()).hexdigest()
    assert payload["wheel_filename"] == wheel.name
    assert payload["package_identity"] == "mingli-engine"
    assert payload["distribution_version"] == installed_version
    assert payload["application_version"] == installed_version
    assert payload["exact_version_set"]["application_version"] == installed_version
    assert payload["wheel_resource_manifest_sha256"] == payload["resource_manifest_sha256"]
    assert "mingli_engine/data/release_docs/source_grounded_internal_release.md" in payload["resource_manifest_sha256"]
    assert "mingli_engine/data/release_docs/internal_release_notes.md" in payload["resource_manifest_sha256"]
    assert set(payload["pre_reproducibility_gate_evidence"]) == {
        "deterministic_calculation",
        "source_rule_tracing",
        "unsupported_inference",
        "school_conflict",
        "abstention",
        "safety_critical",
        "privacy",
        "packaging",
        "version_binding",
    }
    assert payload["claim_boundary_hash"]
    assert payload["wheel_filename"]
    assert payload["wheel_sha256"]
    assert "reproducibility" not in payload["pre_reproducibility_gate_evidence"]
    assert payload["pre_reproducibility_gate_evidence"]["source_rule_tracing"]["evidence"]["status"] == "not_evaluated"
    assert payload["pre_reproducibility_gate_evidence"]["unsupported_inference"]["evidence"]["status"] == "not_evaluated"
    assert payload["pre_reproducibility_gate_evidence"]["school_conflict"]["evidence"]["status"] == "not_evaluated"
    assert payload["pre_reproducibility_gate_evidence"]["abstention"]["evidence"]["status"] == "not_evaluated"


def test_installed_release_audit_rejects_missing_or_non_wheel_file(tmp_path) -> None:
    installed_python = os.environ.get("MINGLI_INSTALLED_PYTHON")
    assert installed_python, "MINGLI_INSTALLED_PYTHON must point to the checkout-external final-wheel venv Python"
    checkout_root = Path(__file__).resolve().parents[2]
    missing = checkout_root / "dist" / "missing.whl"
    not_wheel = tmp_path / "not-a-wheel.txt"
    not_wheel.write_text("not a wheel", encoding="utf-8")
    cases = (
        (missing, "wheel file does not exist"),
        (not_wheel, "wheel path must point to a .whl file"),
    )

    for path, message in cases:
        result = subprocess.run(
            [
                installed_python,
                "-m",
                "mingli_engine.installed_release_audit",
                "--checkout-root",
                str(checkout_root),
                "--wheel-path",
                str(path),
            ],
            text=True,
            capture_output=True,
            cwd=os.environ.get("TEMP", str(checkout_root.parent)),
        )

        assert result.returncode != 0
        assert message in result.stderr


def test_installed_release_audit_rejects_tampered_wheel_metadata_or_version(tmp_path) -> None:
    installed_python = os.environ.get("MINGLI_INSTALLED_PYTHON")
    assert installed_python, "MINGLI_INSTALLED_PYTHON must point to the checkout-external final-wheel venv Python"
    wheel_path = Path(os.environ["MINGLI_FINAL_WHEEL_PATH"])
    installed_version = _installed_distribution_version(installed_python)
    checkout_root = Path(__file__).resolve().parents[2]
    bad_name = tmp_path / "bad-name.whl"
    bad_version = tmp_path / "bad-version.whl"
    with zipfile.ZipFile(wheel_path) as src, zipfile.ZipFile(bad_name, "w") as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename.endswith("METADATA"):
                data = data.replace(b"Name: mingli-engine", b"Name: other-package")
            dst.writestr(info, data)
    with zipfile.ZipFile(wheel_path) as src, zipfile.ZipFile(bad_version, "w") as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename.endswith("METADATA"):
                data = data.replace(b"Version: " + installed_version.encode(), b"Version: 999.999.999")
            dst.writestr(info, data)

    for wheel, message in ((bad_name, "wheel metadata name must be mingli-engine"), (bad_version, "wheel, installed distribution, and application versions must match")):
        result = subprocess.run(
            [
                installed_python,
                "-m",
                "mingli_engine.installed_release_audit",
                "--checkout-root",
                str(checkout_root),
                "--wheel-path",
                str(wheel),
            ],
            text=True,
            capture_output=True,
            cwd=os.environ.get("TEMP", str(checkout_root.parent)),
        )
        assert result.returncode != 0
        assert message in result.stderr
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
$ErrorActionPreference = 'Stop'
$runRoot = Join-Path $env:TEMP ('mingli-task4-red-' + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $runRoot | Out-Null
$unitOutput = Join-Path $runRoot 'unit-red-output.txt'
pytest tests/unit/test_domain_calibration_release.py -q *> $unitOutput
$unitExit = $LASTEXITCODE
if ($unitExit -eq 0) { throw 'expected unit installed evidence tests to fail before implementation' }
$unitText = Get-Content -LiteralPath $unitOutput -Raw
if ($unitText -notmatch 'InstalledWheelReleaseEvidence|build_installed_wheel_release_evidence_from_audit_files|build_expected_release_resource_manifest_from_checkout|AttributeError|ImportError|NameError') {
  throw 'unit red failed for an unexpected reason; expected missing installed evidence symbols or behavior'
}
$wheelOut = Join-Path $runRoot 'wheel-out'
New-Item -ItemType Directory -Force -Path $wheelOut | Out-Null
python -m build --wheel --outdir $wheelOut
if ($LASTEXITCODE -ne 0) { throw 'wheel build failed before installed audit red test' }
$wheels = @(Get-ChildItem -LiteralPath $wheelOut -Filter '*.whl')
if ($wheels.Count -ne 1) { throw "expected exactly one wheel in $wheelOut, found $($wheels.Count)" }
$wheel = $wheels[0]
$venvRoot = Join-Path $runRoot 'venv'
python -m venv $venvRoot
if ($LASTEXITCODE -ne 0) { throw 'venv creation failed before installed audit red test' }
$env:MINGLI_INSTALLED_PYTHON = Join-Path $venvRoot 'Scripts\python.exe'
$env:MINGLI_FINAL_WHEEL_PATH = $wheel.FullName
& $env:MINGLI_INSTALLED_PYTHON -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed before installed audit red test' }
& $env:MINGLI_INSTALLED_PYTHON -m pip install $wheel.FullName
if ($LASTEXITCODE -ne 0) { throw 'wheel install failed before installed audit red test' }
$integrationOutput = Join-Path $runRoot 'installed-audit-red-output.txt'
pytest tests/integration/test_installed_release_audit.py -q *> $integrationOutput
$integrationExit = $LASTEXITCODE
if ($integrationExit -eq 0) { throw 'expected installed audit integration tests to fail before implementation' }
$integrationText = Get-Content -LiteralPath $integrationOutput -Raw
if ($integrationText -match 'MINGLI_INSTALLED_PYTHON|MINGLI_FINAL_WHEEL_PATH') {
  throw 'installed audit red failed because required environment was missing; this is not a valid red light'
}
if ($integrationText -notmatch 'mingli_engine\.installed_release_audit|No module named mingli_engine\.installed_release_audit|AttributeError.*installed_release_audit|wheel-path|wheel metadata|resource manifest|not implemented') {
  throw 'installed audit red failed for an unexpected reason; expected missing installed audit module, symbol, or wheel audit behavior'
}
Write-Output "Task 4 red artifacts: $runRoot"
```

Expected: unit tests fail for missing installed evidence symbols or behavior, and the installed integration test fails for missing `mingli_engine.installed_release_audit` or its required wheel-path/metadata/resource-manifest behavior. Environment-variable absence, unrelated import failures outside those expected symbols, wheel build failure, venv failure, pip failure, or install failure is not an acceptable red light.

- [ ] **Step 3: Implement installed-wheel evidence**

Add to `src\mingli_engine\domain_calibration_models.py`:

```python
import json
from pathlib import Path


@dataclass(frozen=True)
class InstalledAuditEnvelope:
    canonical_sha256: str
    payload: Mapping[str, object]


@dataclass(frozen=True)
class InstalledWheelReleaseEvidence:
    wheel_filename: str
    wheel_sha256: str
    fresh_install_target: str
    checkout_root: str
    package_identity: str
    distribution_version: str
    application_version: str
    exact_version_set: ExactVersionSet
    resource_manifest_sha256: Mapping[str, str]
    expected_resource_manifest_sha256: Mapping[str, str]
    gate_payload_hashes: Mapping[str, str]
    gate_canonical_hashes: Mapping[str, str]
    gate_statuses: Mapping[str, str]
    application_bundle_hash: str
    claim_boundary_hash: str
    source_isolated: bool
    environment: Mapping[str, object]
    installed_module_path: str
    first_installed_audit_envelope: Mapping[str, object]
    second_installed_audit_envelope: Mapping[str, object]
    first_recompute_payload_sha256: str
    second_recompute_payload_sha256: str
    canonical_sha256: str

    @classmethod
    def from_recompute_payloads(
        cls,
        *,
        wheel_filename: str,
        wheel_sha256: str,
        fresh_install_target: str,
        checkout_root: str,
        package_identity: str,
        distribution_version: str,
        application_version: str,
        exact_version_set: ExactVersionSet,
        resource_manifest_sha256: Mapping[str, str],
        expected_resource_manifest_sha256: Mapping[str, str],
        first_recompute_payload: Mapping[str, object],
        second_recompute_payload: Mapping[str, object],
        first_installed_audit_envelope: Mapping[str, object],
        second_installed_audit_envelope: Mapping[str, object],
    ) -> "InstalledWheelReleaseEvidence":
        gate_payload_hashes = dict(first_recompute_payload["gate_payload_hashes"])
        gate_canonical_hashes = dict(first_recompute_payload["gate_canonical_hashes"])
        gate_statuses = dict(first_recompute_payload["gate_statuses"])
        application_bundle_hash = str(first_recompute_payload["application_bundle_hash"])
        claim_boundary_hash = str(first_recompute_payload["claim_boundary_hash"])
        if first_recompute_payload["source_isolated"] is not True:
            raise ValueError("installed recompute must be source isolated")
        source_isolated = True
        environment = dict(first_recompute_payload["environment"])
        installed_module_path = str(first_recompute_payload["mingli_engine_file"])
        first_hash = governance_canonical_sha256(first_recompute_payload)
        second_hash = governance_canonical_sha256(second_recompute_payload)
        canonical_payload = {
            "wheel_filename": wheel_filename,
            "wheel_sha256": wheel_sha256,
            "fresh_install_target": str(Path(fresh_install_target).resolve()),
            "checkout_root": str(Path(checkout_root).resolve()),
            "package_identity": package_identity,
            "distribution_version": distribution_version,
            "application_version": application_version,
            "exact_version_set": asdict(exact_version_set),
            "resource_manifest_sha256": dict(resource_manifest_sha256),
            "expected_resource_manifest_sha256": dict(expected_resource_manifest_sha256),
            "gate_payload_hashes": gate_payload_hashes,
            "gate_canonical_hashes": gate_canonical_hashes,
            "gate_statuses": dict(gate_statuses),
            "application_bundle_hash": application_bundle_hash,
            "claim_boundary_hash": claim_boundary_hash,
            "source_isolated": source_isolated,
            "environment": environment,
            "installed_module_path": installed_module_path,
            "first_installed_audit_envelope": dict(first_installed_audit_envelope),
            "second_installed_audit_envelope": dict(second_installed_audit_envelope),
            "first_recompute_payload_sha256": first_hash,
            "second_recompute_payload_sha256": second_hash,
        }
        evidence = cls(
            wheel_filename=wheel_filename,
            wheel_sha256=wheel_sha256,
            fresh_install_target=str(Path(fresh_install_target).resolve()),
            checkout_root=str(Path(checkout_root).resolve()),
            package_identity=package_identity,
            distribution_version=distribution_version,
            application_version=application_version,
            exact_version_set=exact_version_set,
            resource_manifest_sha256=dict(resource_manifest_sha256),
            expected_resource_manifest_sha256=dict(expected_resource_manifest_sha256),
            gate_payload_hashes=gate_payload_hashes,
            gate_canonical_hashes=gate_canonical_hashes,
            gate_statuses=dict(gate_statuses),
            application_bundle_hash=application_bundle_hash,
            claim_boundary_hash=claim_boundary_hash,
            source_isolated=source_isolated,
            environment=environment,
            installed_module_path=installed_module_path,
            first_installed_audit_envelope=dict(first_installed_audit_envelope),
            second_installed_audit_envelope=dict(second_installed_audit_envelope),
            first_recompute_payload_sha256=first_hash,
            second_recompute_payload_sha256=second_hash,
            canonical_sha256=governance_canonical_sha256(canonical_payload),
        )
        evidence.validate(first_recompute_payload, second_recompute_payload)
        return evidence

    def validate(self, first_payload: Mapping[str, object], second_payload: Mapping[str, object]) -> None:
        require_sha256(self.wheel_sha256, "wheel_sha256")
        require_sha256(self.first_recompute_payload_sha256, "first_recompute_payload_sha256")
        require_sha256(self.second_recompute_payload_sha256, "second_recompute_payload_sha256")
        require_sha256(self.canonical_sha256, "canonical_sha256")
        require_sha256(self.application_bundle_hash, "application_bundle_hash")
        require_sha256(self.claim_boundary_hash, "claim_boundary_hash")
        if self.package_identity != "mingli-engine":
            raise ValueError("package identity must be mingli-engine")
        if self.distribution_version != self.application_version:
            raise ValueError("distribution_version must match application_version")
        if self.exact_version_set.application_version != self.application_version:
            raise ValueError("ExactVersionSet application_version mismatch")
        require_sha256(self.exact_version_set.corpus_sha256, "exact_version_set.corpus_sha256")
        exact_fields = set(asdict(self.exact_version_set))
        if exact_fields != {
            "application_version",
            "engine_version",
            "ruleset_version",
            "provider_version",
            "school_profile_version",
            "fixture_version",
            "evidence_baseline_id",
            "corpus_sha256",
        }:
            raise ValueError("ExactVersionSet must contain all eight identity fields")
        target = Path(self.fresh_install_target).resolve()
        checkout = Path(self.checkout_root).resolve()
        if target == checkout or checkout in target.parents:
            raise ValueError("fresh install target must be outside checkout")
        module_path = Path(self.installed_module_path).resolve()
        if target not in module_path.parents:
            raise ValueError("installed module path must be inside fresh install target")
        if checkout == module_path or checkout in module_path.parents:
            raise ValueError("installed module path must be outside checkout")
        if not self.source_isolated:
            raise ValueError("installed evidence must be source isolated")
        if self.first_recompute_payload_sha256 != self.second_recompute_payload_sha256:
            raise ValueError("installed recomputes must match")
        for envelope in (self.first_installed_audit_envelope, self.second_installed_audit_envelope):
            if set(envelope) != {"canonical_sha256", "payload"}:
                raise ValueError("installed audit envelope must contain canonical_sha256 and payload")
            require_sha256(str(envelope["canonical_sha256"]), "installed audit envelope canonical_sha256")
            if governance_canonical_sha256(envelope["payload"]) != envelope["canonical_sha256"]:
                raise ValueError("installed audit envelope canonical hash mismatch")
        if dict(self.resource_manifest_sha256) != dict(self.expected_resource_manifest_sha256):
            raise ValueError("resource manifest must exactly match expected manifest")
        for path, digest in self.resource_manifest_sha256.items():
            require_sha256(str(digest), f"resource_manifest_sha256[{path}]")
        for path, digest in self.expected_resource_manifest_sha256.items():
            require_sha256(str(digest), f"expected_resource_manifest_sha256[{path}]")
        if tuple(self.gate_statuses) != APPLICATION_GATE_IDS:
            raise ValueError("installed evidence must include the complete ordered gate status set")
        if tuple(self.gate_payload_hashes) != APPLICATION_GATE_IDS or tuple(self.gate_canonical_hashes) != APPLICATION_GATE_IDS:
            raise ValueError("installed evidence must include complete ordered gate hashes")
        for gate_id in APPLICATION_GATE_IDS:
            require_sha256(str(self.gate_payload_hashes[gate_id]), f"gate_payload_hashes[{gate_id}]")
            require_sha256(str(self.gate_canonical_hashes[gate_id]), f"gate_canonical_hashes[{gate_id}]")
        required_payload_keys = {
            "package_identity",
            "distribution_version",
            "application_version",
            "exact_version_set",
            "resource_manifest_sha256",
            "gate_payload_hashes",
            "gate_canonical_hashes",
            "gate_statuses",
            "application_bundle_hash",
            "release_statement",
            "claim_boundary_hash",
            "wheel_filename",
            "wheel_sha256",
            "environment",
            "source_isolated",
            "mingli_engine_file",
        }
        for payload in (first_payload, second_payload):
            if set(payload) != required_payload_keys:
                raise ValueError("installed recompute payload has incomplete release identity")
            if payload["resource_manifest_sha256"] != dict(self.resource_manifest_sha256):
                raise ValueError("resource manifest must exactly match expected manifest")
            if payload["gate_payload_hashes"] != dict(self.gate_payload_hashes):
                raise ValueError("gate payload hashes must match installed evidence")
            if payload["gate_canonical_hashes"] != dict(self.gate_canonical_hashes):
                raise ValueError("gate canonical hashes must match installed evidence")
            if payload["gate_statuses"] != dict(self.gate_statuses):
                raise ValueError("gate statuses must match installed evidence")
            if payload["application_bundle_hash"] != self.application_bundle_hash:
                raise ValueError("application bundle hash must match installed evidence")
            if payload["claim_boundary_hash"] != self.claim_boundary_hash:
                raise ValueError("claim boundary hash must match installed evidence")
            if payload["source_isolated"] is not True:
                raise ValueError("installed recompute must be source isolated")

    def to_dict(self) -> dict[str, object]:
        return {
            "wheel_filename": self.wheel_filename,
            "wheel_sha256": self.wheel_sha256,
            "fresh_install_target": self.fresh_install_target,
            "checkout_root": self.checkout_root,
            "package_identity": self.package_identity,
            "distribution_version": self.distribution_version,
            "application_version": self.application_version,
            "exact_version_set": asdict(self.exact_version_set),
            "resource_manifest_sha256": dict(self.resource_manifest_sha256),
            "expected_resource_manifest_sha256": dict(self.expected_resource_manifest_sha256),
            "gate_payload_hashes": dict(self.gate_payload_hashes),
            "gate_canonical_hashes": dict(self.gate_canonical_hashes),
            "gate_statuses": dict(self.gate_statuses),
            "application_bundle_hash": self.application_bundle_hash,
            "claim_boundary_hash": self.claim_boundary_hash,
            "source_isolated": self.source_isolated,
            "environment": self.environment,
            "installed_module_path": self.installed_module_path,
            "first_installed_audit_envelope": dict(self.first_installed_audit_envelope),
            "second_installed_audit_envelope": dict(self.second_installed_audit_envelope),
            "first_recompute_payload_sha256": self.first_recompute_payload_sha256,
            "second_recompute_payload_sha256": self.second_recompute_payload_sha256,
            "canonical_sha256": self.canonical_sha256,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "InstalledWheelReleaseEvidence":
        from mingli_engine.domain_calibration_release import rebuild_installed_wheel_release_evidence_from_envelopes

        rebuilt = rebuild_installed_wheel_release_evidence_from_envelopes(
            first_envelope=dict(payload["first_installed_audit_envelope"]),
            second_envelope=dict(payload["second_installed_audit_envelope"]),
            fresh_install_target=str(payload["fresh_install_target"]),
            checkout_root=str(payload["checkout_root"]),
            expected_manifest=dict(payload["expected_resource_manifest_sha256"]),
        )
        if rebuilt.to_dict() != dict(payload):
            raise ValueError("installed evidence canonical hash mismatch")
        first_payload = rebuilt.first_installed_audit_envelope["payload"]
        second_payload = rebuilt.second_installed_audit_envelope["payload"]
        rebuilt.validate(first_payload, second_payload)
        return rebuilt
```

- [ ] **Step 4: Implement expected manifest and installed audit command**

Add this helper to `src\mingli_engine\domain_calibration.py` so installed audit can build an `ExactVersionSet` for the actually installed distribution version without using the old candidate-only restriction:

```python
def build_release_version_set(application_version: str) -> ExactVersionSet:
    if not application_version:
        raise CalibrationProtocolError("application_version is required")
    school_profile_version, _enabled_school_ids = load_authoritative_school_profile_identity()
    try:
        provider_version = version(_PROVIDER_DISTRIBUTION)
    except PackageNotFoundError:
        raise CalibrationProtocolError("calibration provider is unavailable") from None
    return ExactVersionSet(
        application_version=application_version,
        engine_version=ENGINE_VERSION,
        ruleset_version=RULESET_VERSION,
        provider_version=f"{_PROVIDER_DISTRIBUTION}-{provider_version}",
        school_profile_version=school_profile_version,
        fixture_version=_FIXTURE_VERSION,
        evidence_baseline_id=_EVIDENCE_BASELINE_ID,
        corpus_sha256=_corpus_sha256(),
    )
```

Create release docs and include Markdown in package data before any final wheel build.

Update `pyproject.toml`:

```toml
[tool.setuptools.package-data]
mingli_engine = ["data/**/*.json", "data/**/*.md"]
```

Create `src\mingli_engine\data\release_docs\source_grounded_internal_release.md`:

```markdown
# Source-Grounded Internal Release Governance

Internal source-grounded application release candidate for controlled evaluation only.

This is not a public release and not a claim of domain truth beyond cited sources and stated scope.

Feature 020 corpus expansion, benchmark expansion, and implementation are excluded.
```

Create `src\mingli_engine\data\release_docs\internal_release_notes.md`:

```markdown
# Internal Release Notes

This internal release requires complete application hard-gate evidence, installed-wheel evidence, exact package and version binding, reproducibility evidence, and formal owner approval.

Abstain when source support, rule trace, school conflict handling, safety, or privacy evidence is incomplete.
```

Add to `src\mingli_engine\domain_calibration_release.py`:

```python
import json
from hashlib import sha256
from importlib import resources
from pathlib import Path

RELEASE_STATEMENT = "Internal source-grounded application release candidate for controlled evaluation only."
LIMITATIONS = (
    "Not a public release.",
    "Not a claim of domain truth beyond cited sources and stated scope.",
    "Feature 020 corpus expansion, benchmark expansion, and implementation are excluded.",
)
ABSTENTION_POLICY = "Abstain when source support, rule trace, school conflict handling, safety, or privacy evidence is incomplete."
CLAIM_BOUNDARY_HASH = governance_canonical_sha256(
    {
        "release_statement": RELEASE_STATEMENT,
        "limitations": LIMITATIONS,
        "abstention_policy": ABSTENTION_POLICY,
    }
)
RELEASE_DOC_CONTENT = """# Source-Grounded Internal Release Governance

Internal source-grounded application release candidate for controlled evaluation only.

This is not a public release and not a claim of domain truth beyond cited sources and stated scope.

Feature 020 corpus expansion, benchmark expansion, and implementation are excluded.
"""
INTERNAL_RELEASE_NOTES_CONTENT = """# Internal Release Notes

This internal release requires complete application hard-gate evidence, installed-wheel evidence, exact package and version binding, reproducibility evidence, and formal owner approval.

Abstain when source support, rule trace, school conflict handling, safety, or privacy evidence is incomplete.
"""


def build_expected_release_resource_manifest_from_checkout(checkout_root: str | Path) -> dict[str, str]:
    source_root = Path(checkout_root) / "src" / "mingli_engine"
    manifest = {
        "mingli_engine/data/release_docs/source_grounded_internal_release.md": sha256(RELEASE_DOC_CONTENT.encode("utf-8")).hexdigest(),
        "mingli_engine/data/release_docs/internal_release_notes.md": sha256(INTERNAL_RELEASE_NOTES_CONTENT.encode("utf-8")).hexdigest(),
    }
    data_root = source_root / "data"
    stack = [data_root]
    while stack:
        current = stack.pop()
        for child in sorted(current.iterdir()):
            if child.is_dir():
                stack.append(child)
            elif child.name.endswith(".json"):
                relative = "mingli_engine/" + str(child.relative_to(source_root)).replace("\\", "/")
                manifest[relative] = sha256(child.read_bytes()).hexdigest()
    return dict(sorted(manifest.items()))


def write_expected_release_resource_manifest(checkout_root: str | Path, output_path: str | Path) -> str:
    manifest = build_expected_release_resource_manifest_from_checkout(checkout_root)
    Path(output_path).write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    return governance_canonical_sha256(manifest)
```

Create `src\mingli_engine\installed_release_audit.py`:

```python
from __future__ import annotations

import argparse
import email
import hashlib
import json
import platform
import sys
from importlib import metadata, resources
from pathlib import Path
from zipfile import ZipFile

import mingli_engine
from mingli_engine.domain_calibration import build_release_version_set
from mingli_engine.domain_calibration_release import (
    CLAIM_BOUNDARY_HASH,
    RELEASE_STATEMENT,
    build_application_evidence_bundle_from_existing_validators,
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _wheel_metadata(wheel_path: Path) -> tuple[str, str]:
    if not wheel_path.exists():
        raise ValueError("wheel file does not exist")
    if wheel_path.suffix != ".whl":
        raise ValueError("wheel path must point to a .whl file")
    with ZipFile(wheel_path) as wheel:
        metadata_members = [name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")]
        if len(metadata_members) != 1:
            raise ValueError("wheel must contain exactly one METADATA file")
        message = email.message_from_bytes(wheel.read(metadata_members[0]))
    name = str(message["Name"])
    version = str(message["Version"])
    if name != "mingli-engine":
        raise ValueError("wheel metadata name must be mingli-engine")
    return name, version


def _resource_manifest_from_wheel(wheel_path: Path) -> dict[str, str]:
    with ZipFile(wheel_path) as wheel:
        manifest = {}
        for name in sorted(wheel.namelist()):
            if name.startswith("mingli_engine/data/") and (name.endswith(".json") or name.endswith(".md")):
                manifest[name] = hashlib.sha256(wheel.read(name)).hexdigest()
    if not manifest:
        raise ValueError("wheel resource manifest must not be empty")
    return manifest


def _resource_manifest_from_installed_package() -> dict[str, str]:
    package_root = resources.files("mingli_engine")
    manifest = {}
    stack = [package_root.joinpath("data")]
    while stack:
        current = stack.pop()
        for child in current.iterdir():
            if child.is_dir():
                stack.append(child)
            elif child.name.endswith(".json") or child.name.endswith(".md"):
                relative = "mingli_engine/" + str(child.relative_to(package_root)).replace("\\", "/")
                manifest[relative] = hashlib.sha256(child.read_bytes()).hexdigest()
    return dict(sorted(manifest.items()))


def build_installed_audit_payload(checkout_root: str, wheel_path: str) -> dict[str, object]:
    wheel = Path(wheel_path).resolve()
    package_identity, wheel_version = _wheel_metadata(wheel)
    wheel_manifest = _resource_manifest_from_wheel(wheel)
    package_file = Path(mingli_engine.__file__).resolve()
    checkout = Path(checkout_root).resolve()
    source_isolated = package_file != checkout and checkout not in package_file.parents
    manifest = _resource_manifest_from_installed_package()
    if manifest != wheel_manifest:
        raise ValueError("installed package resources must match wheel resource manifest")
    distribution_version = metadata.version("mingli-engine")
    application_version = getattr(mingli_engine, "__version__", distribution_version)
    if wheel_version != distribution_version or distribution_version != application_version:
        raise ValueError("wheel, installed distribution, and application versions must match")
    exact_version_set = build_release_version_set(distribution_version)
    pre_reproducibility_bundle = build_application_evidence_bundle_from_existing_validators()
    pre_reproducibility_gates = tuple(
        gate for gate in pre_reproducibility_bundle.gate_evidence if gate.gate_id != "reproducibility"
    )
    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "dependencies": {
            "mingli-engine": distribution_version,
            "lunar-python": metadata.version("lunar-python"),
        },
    }
    return {
        "package_identity": package_identity,
        "distribution_version": distribution_version,
        "application_version": application_version,
        "exact_version_set": exact_version_set.__dict__,
        "resource_manifest_sha256": manifest,
        "wheel_resource_manifest_sha256": wheel_manifest,
        "pre_reproducibility_gate_evidence": {
            gate.gate_id: {"raw_payload": gate.raw_payload, "evidence": gate.to_dict()}
            for gate in pre_reproducibility_gates
        },
        "pre_reproducibility_application_bundle_hash": pre_reproducibility_bundle.canonical_sha256,
        "release_statement": RELEASE_STATEMENT,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "wheel_filename": wheel.name,
        "wheel_sha256": _sha256_file(wheel),
        "environment": environment,
        "source_isolated": source_isolated,
        "mingli_engine_file": str(package_file),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m mingli_engine.installed_release_audit")
    parser.add_argument("--checkout-root", required=True)
    parser.add_argument("--wheel-path", required=True)
    args = parser.parse_args(argv)
    print(json.dumps(build_installed_audit_payload(args.checkout_root, args.wheel_path), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Add this builder to `src\mingli_engine\domain_calibration_release.py`:

```python
import json
from pathlib import Path

from mingli_engine.application_validation import RawReproducibilityResult, produce_reproducibility_gate
from mingli_engine.domain_calibration_models import ApplicationEvidenceBundle, ApplicationHardGateEvidence, replay_application_gate_evidence


def _version_set_from_audit_payload(payload: Mapping[str, object]) -> ExactVersionSet:
    version = payload["exact_version_set"]
    return ExactVersionSet(
        application_version=str(version["application_version"]),
        engine_version=str(version["engine_version"]),
        ruleset_version=str(version["ruleset_version"]),
        provider_version=str(version["provider_version"]),
        school_profile_version=str(version["school_profile_version"]),
        fixture_version=str(version["fixture_version"]),
        evidence_baseline_id=str(version["evidence_baseline_id"]),
        corpus_sha256=str(version["corpus_sha256"]),
    )


def _gate_from_envelope(gate_id: str, payload: Mapping[str, object]) -> ApplicationHardGateEvidence:
    evidence_payload = dict(payload["evidence"])
    if evidence_payload["gate_id"] != gate_id:
        raise ValueError("gate evidence id mismatch")
    return replay_application_gate_evidence(evidence_payload)


def build_installed_wheel_release_evidence_from_audit_files(
    *,
    first_audit_path: str | Path,
    second_audit_path: str | Path,
    fresh_install_target: str | Path,
    checkout_root: str | Path,
    expected_manifest: Mapping[str, str],
) -> InstalledWheelReleaseEvidence:
    first_payload = json.loads(Path(first_audit_path).read_text(encoding="utf-8"))
    second_payload = json.loads(Path(second_audit_path).read_text(encoding="utf-8"))
    return rebuild_installed_wheel_release_evidence_from_envelopes(
        first_envelope={"canonical_sha256": governance_canonical_sha256(first_payload), "payload": first_payload},
        second_envelope={"canonical_sha256": governance_canonical_sha256(second_payload), "payload": second_payload},
        fresh_install_target=fresh_install_target,
        checkout_root=checkout_root,
        expected_manifest=expected_manifest,
    )


def rebuild_installed_wheel_release_evidence_from_envelopes(
    *,
    first_envelope: Mapping[str, object],
    second_envelope: Mapping[str, object],
    fresh_install_target: str | Path,
    checkout_root: str | Path,
    expected_manifest: Mapping[str, str],
) -> InstalledWheelReleaseEvidence:
    first_payload = dict(first_envelope["payload"])
    second_payload = dict(second_envelope["payload"])
    first_audit_hash = governance_canonical_sha256(first_payload)
    second_audit_hash = governance_canonical_sha256(second_payload)
    if first_envelope["canonical_sha256"] != first_audit_hash or second_envelope["canonical_sha256"] != second_audit_hash:
        raise ValueError("installed audit envelope canonical hash mismatch")
    if first_audit_hash != second_audit_hash:
        raise ValueError("installed audit payloads must be identical")
    if first_payload["wheel_sha256"] != second_payload["wheel_sha256"]:
        raise ValueError("installed audit wheel hashes must match")
    if dict(first_payload["resource_manifest_sha256"]) != dict(expected_manifest):
        raise ValueError("resource manifest must exactly match expected manifest")
    if dict(second_payload["resource_manifest_sha256"]) != dict(expected_manifest):
        raise ValueError("resource manifest must exactly match expected manifest")
    if dict(first_payload["wheel_resource_manifest_sha256"]) != dict(first_payload["resource_manifest_sha256"]):
        raise ValueError("wheel resource manifest must match installed package manifest")
    if dict(second_payload["wheel_resource_manifest_sha256"]) != dict(second_payload["resource_manifest_sha256"]):
        raise ValueError("wheel resource manifest must match installed package manifest")
    for key in ("package_identity", "distribution_version", "application_version", "exact_version_set", "release_statement", "claim_boundary_hash", "wheel_filename", "wheel_sha256", "wheel_resource_manifest_sha256", "source_isolated"):
        if first_payload[key] != second_payload[key]:
            raise ValueError(f"installed audit {key} mismatch")
    first_gates = tuple(
        _gate_from_envelope(gate_id, first_payload["pre_reproducibility_gate_evidence"][gate_id])
        for gate_id in APPLICATION_GATE_IDS
        if gate_id != "reproducibility"
    )
    second_gates = tuple(
        _gate_from_envelope(gate_id, second_payload["pre_reproducibility_gate_evidence"][gate_id])
        for gate_id in APPLICATION_GATE_IDS
        if gate_id != "reproducibility"
    )
    if tuple(gate.canonical_sha256 for gate in first_gates) != tuple(gate.canonical_sha256 for gate in second_gates):
        raise ValueError("installed audit gate evidence must match")
    reproducibility_gate = produce_reproducibility_gate(
        RawReproducibilityResult(
            first_payload_hash=first_audit_hash,
            second_payload_hash=second_audit_hash,
            executed_from_installed_package=True,
        )
    )
    final_bundle = ApplicationEvidenceBundle.from_gate_evidence(first_gates + (reproducibility_gate,))
    first_final_payload = {
        "package_identity": first_payload["package_identity"],
        "distribution_version": first_payload["distribution_version"],
        "application_version": first_payload["application_version"],
        "exact_version_set": first_payload["exact_version_set"],
        "resource_manifest_sha256": first_payload["resource_manifest_sha256"],
        "gate_payload_hashes": {gate.gate_id: gate.raw_payload_sha256 for gate in final_bundle.gate_evidence},
        "gate_canonical_hashes": {gate.gate_id: gate.canonical_sha256 for gate in final_bundle.gate_evidence},
        "gate_statuses": {gate.gate_id: gate.status for gate in final_bundle.gate_evidence},
        "application_bundle_hash": final_bundle.canonical_sha256,
        "release_statement": first_payload["release_statement"],
        "claim_boundary_hash": first_payload["claim_boundary_hash"],
        "wheel_filename": first_payload["wheel_filename"],
        "wheel_sha256": first_payload["wheel_sha256"],
        "environment": first_payload["environment"],
        "source_isolated": first_payload["source_isolated"],
        "mingli_engine_file": first_payload["mingli_engine_file"],
    }
    second_final_payload = dict(first_final_payload)
    second_final_payload["environment"] = second_payload["environment"]
    second_final_payload["mingli_engine_file"] = second_payload["mingli_engine_file"]
    return InstalledWheelReleaseEvidence.from_recompute_payloads(
        wheel_filename=str(first_payload["wheel_filename"]),
        wheel_sha256=str(first_payload["wheel_sha256"]),
        fresh_install_target=str(fresh_install_target),
        checkout_root=str(checkout_root),
        package_identity=str(first_payload["package_identity"]),
        distribution_version=str(first_payload["distribution_version"]),
        application_version=str(first_payload["application_version"]),
        exact_version_set=_version_set_from_audit_payload(first_payload),
        resource_manifest_sha256=dict(first_payload["resource_manifest_sha256"]),
        expected_resource_manifest_sha256=dict(expected_manifest),
        first_recompute_payload=first_final_payload,
        second_recompute_payload=second_final_payload,
        first_installed_audit_envelope={"canonical_sha256": first_audit_hash, "payload": first_payload},
        second_installed_audit_envelope={"canonical_sha256": second_audit_hash, "payload": second_payload},
    )
```

- [ ] **Step 5: Future real installed-wheel evidence command**

Run only in the execution thread:

```powershell
$ErrorActionPreference = 'Stop'
$runRoot = Join-Path $env:TEMP ('mingli-task4-real-' + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $runRoot | Out-Null
$expectedManifest = Join-Path $runRoot 'expected-release-resource-manifest.json'
$expectedScript = Join-Path $runRoot 'write-expected-release-manifest.py'
@'
from pathlib import Path
from mingli_engine.domain_calibration_release import write_expected_release_resource_manifest
digest = write_expected_release_resource_manifest(r'E:\mingli-019-closure', Path(r'__EXPECTED_MANIFEST__'))
print(digest)
'@.Replace('__EXPECTED_MANIFEST__', $expectedManifest) | Set-Content -LiteralPath $expectedScript -Encoding UTF8
python $expectedScript
if ($LASTEXITCODE -ne 0) { throw 'expected manifest writer failed' }
$wheelOut = Join-Path $runRoot 'wheel-out'
New-Item -ItemType Directory -Force -Path $wheelOut | Out-Null
python -m build --wheel --outdir $wheelOut
if ($LASTEXITCODE -ne 0) { throw 'wheel build failed' }
$wheels = @(Get-ChildItem -LiteralPath $wheelOut -Filter '*.whl')
if ($wheels.Count -ne 1) { throw "expected exactly one wheel in $wheelOut, found $($wheels.Count)" }
$wheel = $wheels[0]
$env:MINGLI_FINAL_WHEEL_PATH = $wheel.FullName
$venvRoot = Join-Path $runRoot 'fresh-installed-venv'
python -m venv $venvRoot
if ($LASTEXITCODE -ne 0) { throw 'venv creation failed' }
$venvPython = Join-Path $venvRoot 'Scripts\python.exe'
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed' }
& $venvPython -m pip install $wheel.FullName
if ($LASTEXITCODE -ne 0) { throw 'wheel install failed' }
$firstAudit = Join-Path $runRoot 'first-installed-audit.json'
$secondAudit = Join-Path $runRoot 'second-installed-audit.json'
$finalEvidence = Join-Path $runRoot 'final-installed-wheel-evidence.json'
& $venvPython -m mingli_engine.installed_release_audit --checkout-root 'E:\mingli-019-closure' --wheel-path $wheel.FullName > $firstAudit
if ($LASTEXITCODE -ne 0) { throw 'first installed audit failed' }
if (-not (Test-Path -LiteralPath $firstAudit)) { throw 'first installed audit did not write its output file' }
& $venvPython -m mingli_engine.installed_release_audit --checkout-root 'E:\mingli-019-closure' --wheel-path $wheel.FullName > $secondAudit
if ($LASTEXITCODE -ne 0) { throw 'second installed audit failed' }
if (-not (Test-Path -LiteralPath $secondAudit)) { throw 'second installed audit did not write its output file' }
$builderScript = Join-Path $runRoot 'build-installed-wheel-evidence.py'
@'
import json
from pathlib import Path
from mingli_engine.domain_calibration_models import InstalledWheelReleaseEvidence, ReleaseVersionDecision
from mingli_engine.domain_calibration_release import build_installed_wheel_release_evidence_from_audit_files
expected_manifest = json.loads(Path(r'__EXPECTED_MANIFEST__').read_text(encoding='utf-8'))
evidence = build_installed_wheel_release_evidence_from_audit_files(
    first_audit_path=Path(r'__FIRST_AUDIT__'),
    second_audit_path=Path(r'__SECOND_AUDIT__'),
    fresh_install_target=Path(r'__VENV_ROOT__'),
    checkout_root=Path(r'E:\mingli-019-closure'),
    expected_manifest=expected_manifest,
)
Path(r'__FINAL_EVIDENCE__').write_text(json.dumps(evidence.to_dict(), sort_keys=True), encoding='utf-8')
reloaded = InstalledWheelReleaseEvidence.from_dict(json.loads(Path(r'__FINAL_EVIDENCE__').read_text(encoding='utf-8')))
if reloaded.canonical_sha256 != evidence.canonical_sha256:
    raise SystemExit('installed evidence canonical hash did not round trip')
print(reloaded.canonical_sha256)
'@.Replace('__VENV_ROOT__', $venvRoot).Replace('__EXPECTED_MANIFEST__', $expectedManifest).Replace('__FIRST_AUDIT__', $firstAudit).Replace('__SECOND_AUDIT__', $secondAudit).Replace('__FINAL_EVIDENCE__', $finalEvidence) | Set-Content -LiteralPath $builderScript -Encoding UTF8
& $venvPython $builderScript
if ($LASTEXITCODE -ne 0) { throw 'installed evidence builder failed' }
if (-not (Test-Path -LiteralPath $finalEvidence)) { throw 'installed evidence builder did not write final evidence' }
Write-Output "runRoot=$runRoot"
Write-Output "finalEvidencePath=$finalEvidence"
```

Expected: both audits load `mingli_engine` from `$venvRoot`, not from checkout; the two JSON payload hashes are identical; `$finalEvidence` is written under the unique `$runRoot`; the printed hash is the final installed evidence hash. The packaged docs and `pyproject.toml` package-data entries exist before this wheel is built and participate in the expected manifest, installed manifest, and manifest-hash comparison. The Task 4 commit boundary still happens only after tests pass.

- [ ] **Step 6: Run tests to verify pass**

Run:

```powershell
$ErrorActionPreference = 'Stop'
$wheelOut = Join-Path $env:TEMP ('mingli-task4-pass-wheel-' + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $wheelOut | Out-Null
python -m build --wheel --outdir $wheelOut
if ($LASTEXITCODE -ne 0) { throw 'wheel build failed before installed audit pass test' }
$wheels = @(Get-ChildItem -LiteralPath $wheelOut -Filter '*.whl')
if ($wheels.Count -ne 1) { throw "expected exactly one wheel in $wheelOut, found $($wheels.Count)" }
$wheel = $wheels[0]
$venvRoot = Join-Path $env:TEMP ('mingli-task4-pass-venv-' + [guid]::NewGuid().ToString())
python -m venv $venvRoot
if ($LASTEXITCODE -ne 0) { throw 'venv creation failed before installed audit pass test' }
$env:MINGLI_INSTALLED_PYTHON = Join-Path $venvRoot 'Scripts\python.exe'
$env:MINGLI_FINAL_WHEEL_PATH = $wheel.FullName
& $env:MINGLI_INSTALLED_PYTHON -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed before installed audit pass test' }
& $env:MINGLI_INSTALLED_PYTHON -m pip install $wheel.FullName
if ($LASTEXITCODE -ne 0) { throw 'wheel install failed before installed audit pass test' }
pytest tests/unit/test_domain_calibration_release.py tests/integration/test_installed_release_audit.py -q
if ($LASTEXITCODE -ne 0) { throw 'installed audit tests failed' }
```

Expected: PASS.

- [ ] **Step 7: Commit boundary**

Run:

```powershell
git add pyproject.toml src/mingli_engine/domain_calibration.py src/mingli_engine/domain_calibration_models.py src/mingli_engine/domain_calibration_release.py src/mingli_engine/installed_release_audit.py src/mingli_engine/data/release_docs/source_grounded_internal_release.md src/mingli_engine/data/release_docs/internal_release_notes.md tests/unit/governance_decision_fixtures.py tests/unit/test_domain_calibration_release.py tests/integration/test_installed_release_audit.py
git commit -m "feat: require installed wheel release evidence"
```

---

### Task 5: Version Decision, State Machine, And Approval Binding

**Files:**
- Modify: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_models.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_release.py`
- Create: `E:\mingli-019-closure\src\mingli_engine\release_version_workflow.py`
- Modify: `E:\mingli-019-closure\tests\unit\governance_decision_fixtures.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_domain_calibration_release.py`
- Create: `E:\mingli-019-closure\tests\unit\test_release_version_workflow.py`
- Modify conditionally: `E:\mingli-019-closure\pyproject.toml` only if the release owner selects a different version after current installed evidence is fully passed; do not edit or stage it in the keep-current path.

- [ ] **Step 1: Write failing tests**

Append to `tests\unit\test_domain_calibration_release.py`:

```python
from pathlib import Path

import pytest

from mingli_engine.domain_calibration_models import (
    APPLICATION_GATE_IDS,
    ApplicationReleaseStatus,
    ApplicationEvidenceBundle,
    ApplicationHardGateEvidence,
    InstalledWheelReleaseEvidence,
    ReleaseApprovalRecord,
    ReleaseGovernanceDecision,
    governance_canonical_sha256,
)
from mingli_engine.domain_calibration_release import (
    CLAIM_BOUNDARY_HASH,
    LIMITATIONS,
    ABSTENTION_POLICY,
    build_release_approval_evidence,
    choose_release_version_after_installed_evidence,
    build_expected_release_resource_manifest_from_checkout,
    classify_application_release_status_from_gate_statuses,
    load_canonical_governance_decision,
    replay_application_bundle_from_installed_evidence,
    transition_release_governance,
    write_canonical_governance_decision_artifact,
)
from tests.unit.governance_decision_fixtures import write_not_evaluated_installed_evidence_fixture, write_structurally_valid_installed_evidence_fixture
from mingli_engine.domain_calibration import CalibrationProtocolError, build_candidate_version_set, build_release_version_set


@pytest.fixture
def application_bundle_factory(tmp_path):
    def build(*, installed: InstalledWheelReleaseEvidence) -> ApplicationEvidenceBundle:
        return replay_application_bundle_from_installed_evidence(installed)
    return build


@pytest.fixture
def installed_evidence_factory(tmp_path):
    def build(
        *,
        distribution_version: str = "0.1.0",
    ) -> InstalledWheelReleaseEvidence:
        evidence_path = write_structurally_valid_installed_evidence_fixture(tmp_path, version=distribution_version)
        return InstalledWheelReleaseEvidence.from_dict(
            json.loads(evidence_path.read_text(encoding="utf-8"))
        )
    return build


def test_build_release_version_set_accepts_owner_version_only_after_gate_success(installed_evidence_factory) -> None:
    installed = installed_evidence_factory(distribution_version="0.1.0")
    decision = choose_release_version_after_installed_evidence(installed, "0.1.1")
    version_set = build_release_version_set(decision.selected_application_version)

    assert version_set.application_version == "0.1.1"


def test_legacy_candidate_version_set_keeps_calibration_candidate_semantics() -> None:
    legacy = build_candidate_version_set("0.2.0")

    assert legacy.application_version == "0.2.0"
    with pytest.raises(CalibrationProtocolError):
        build_candidate_version_set(application_version="owner-selected-version")


def test_version_decision_requires_installed_evidence_and_resets_on_change(installed_evidence_factory) -> None:
    installed = installed_evidence_factory(distribution_version="0.1.0")

    keep = choose_release_version_after_installed_evidence(installed, "0.1.0")
    change = choose_release_version_after_installed_evidence(installed, "0.1.1")

    assert keep.can_reuse_current_installed_evidence is True
    assert change.can_reuse_current_installed_evidence is False
    assert change.application_release_status == "not_evaluated"


def test_version_decision_rejects_tampered_installed_evidence_without_all_gates_passed(tmp_path) -> None:
    evidence_path = write_structurally_valid_installed_evidence_fixture(tmp_path, version="0.1.0")
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["gate_statuses"]["privacy"] = "failed"
    evidence_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="installed evidence"):
        InstalledWheelReleaseEvidence.from_dict(json.loads(evidence_path.read_text(encoding="utf-8")))


def test_not_evaluated_installed_evidence_cannot_enter_version_decision(tmp_path) -> None:
    evidence_path = write_not_evaluated_installed_evidence_fixture(tmp_path, version="0.1.0")
    installed = InstalledWheelReleaseEvidence.from_dict(json.loads(evidence_path.read_text(encoding="utf-8")))

    assert installed.gate_statuses["source_rule_tracing"] == "not_evaluated"
    assert classify_application_release_status_from_gate_statuses(installed.gate_statuses) == "not_evaluated"
    with pytest.raises(ValueError, match="all installed application gates must pass"):
        choose_release_version_after_installed_evidence(installed, "0.1.0")


def test_released_requires_prior_ready_for_same_installed_evidence(installed_evidence_factory, application_bundle_factory) -> None:
    installed = installed_evidence_factory()
    bundle = application_bundle_factory(installed=installed)
    record = {
        "owner": "release-owner",
        "authority": "internal-release-owner",
        "approval_status": "approved",
        "package_identity": installed.package_identity,
        "distribution_version": installed.distribution_version,
        "installed_wheel_evidence_sha256": installed.canonical_sha256,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "limitations_hash": governance_canonical_sha256(LIMITATIONS),
        "abstention_policy_hash": governance_canonical_sha256(ABSTENTION_POLICY),
        "acknowledged_hashes": [
            CLAIM_BOUNDARY_HASH,
            governance_canonical_sha256(LIMITATIONS),
            governance_canonical_sha256(ABSTENTION_POLICY),
        ],
        "approved_at_or_version": "approval-record-001",
    }
    record["canonical_sha256"] = governance_canonical_sha256(record)
    approval = build_release_approval_evidence(record, installed)

    direct = transition_release_governance(None, bundle, installed, approval)
    ready = transition_release_governance(None, bundle, installed, None)
    released = transition_release_governance(ready, bundle, installed, approval)

    assert direct.application_release_status == "internal_source_grounded_ready"
    assert ready.application_release_status == "internal_source_grounded_ready"
    assert ready.application_evidence_hash == bundle.canonical_sha256
    assert ready.installed_wheel_evidence_hash == installed.canonical_sha256
    assert ready.claim_boundary_hash == CLAIM_BOUNDARY_HASH
    assert ready.distribution_version == installed.distribution_version
    assert released.application_release_status == "released_internal_source_grounded"


def test_not_evaluated_installed_evidence_inspects_and_transitions_without_blocking(tmp_path) -> None:
    evidence_path = write_not_evaluated_installed_evidence_fixture(tmp_path, version="0.1.0")
    installed = InstalledWheelReleaseEvidence.from_dict(json.loads(evidence_path.read_text(encoding="utf-8")))
    bundle = replay_application_bundle_from_installed_evidence(installed)

    decision = transition_release_governance(None, bundle, installed, None)

    assert bundle.overall_status == "not_evaluated"
    assert decision.application_release_status == "not_evaluated"
    assert decision.application_release_status != "blocked"


def test_transition_rejects_tampered_installed_payload_bundle_hash(tmp_path) -> None:
    evidence_path = write_structurally_valid_installed_evidence_fixture(tmp_path, version="0.1.0")
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["application_bundle_hash"] = "0" * 64
    evidence_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="canonical hash mismatch"):
        InstalledWheelReleaseEvidence.from_dict(json.loads(evidence_path.read_text(encoding="utf-8")))

    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first_path = write_structurally_valid_installed_evidence_fixture(first_root, version="0.1.0")
    second_path = write_structurally_valid_installed_evidence_fixture(second_root, version="0.1.1")
    first_installed = InstalledWheelReleaseEvidence.from_dict(json.loads(first_path.read_text(encoding="utf-8")))
    second_installed = InstalledWheelReleaseEvidence.from_dict(json.loads(second_path.read_text(encoding="utf-8")))
    mismatched_bundle = replay_application_bundle_from_installed_evidence(second_installed)

    with pytest.raises(ValueError, match="installed payload bundle hash"):
        transition_release_governance(None, mismatched_bundle, first_installed, None)


def test_approval_record_binds_claim_limitations_abstention_and_installed_evidence(installed_evidence_factory) -> None:
    installed = installed_evidence_factory()
    record = {
        "owner": "release-owner",
        "authority": "internal-release-owner",
        "approval_status": "approved",
        "package_identity": installed.package_identity,
        "distribution_version": installed.distribution_version,
        "installed_wheel_evidence_sha256": installed.canonical_sha256,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "limitations_hash": governance_canonical_sha256(LIMITATIONS),
        "abstention_policy_hash": governance_canonical_sha256(ABSTENTION_POLICY),
        "acknowledged_hashes": [
            CLAIM_BOUNDARY_HASH,
            governance_canonical_sha256(LIMITATIONS),
            governance_canonical_sha256(ABSTENTION_POLICY),
        ],
        "approved_at_or_version": "approval-record-001",
    }
    record["canonical_sha256"] = governance_canonical_sha256(record)

    approval = build_release_approval_evidence(record, installed)

    assert approval.approval_status == "approved"
    assert approval.claim_boundary_hash == CLAIM_BOUNDARY_HASH


def test_rejected_approval_blocks_release(installed_evidence_factory, application_bundle_factory) -> None:
    installed = installed_evidence_factory()
    bundle = application_bundle_factory(installed=installed)
    record = {
        "owner": "release-owner",
        "authority": "internal-release-owner",
        "approval_status": "rejected",
        "package_identity": installed.package_identity,
        "distribution_version": installed.distribution_version,
        "installed_wheel_evidence_sha256": installed.canonical_sha256,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "limitations_hash": governance_canonical_sha256(LIMITATIONS),
        "abstention_policy_hash": governance_canonical_sha256(ABSTENTION_POLICY),
        "acknowledged_hashes": [
            CLAIM_BOUNDARY_HASH,
            governance_canonical_sha256(LIMITATIONS),
            governance_canonical_sha256(ABSTENTION_POLICY),
        ],
        "approved_at_or_version": "approval-record-002",
    }
    record["canonical_sha256"] = governance_canonical_sha256(record)
    approval = build_release_approval_evidence(record, installed)

    decision = transition_release_governance(None, bundle, installed, approval)

    assert decision.application_release_status == "blocked"


def test_rejected_approval_blocks_even_when_installed_evidence_is_not_evaluated(tmp_path) -> None:
    evidence_path = write_not_evaluated_installed_evidence_fixture(tmp_path, version="0.1.0")
    installed = InstalledWheelReleaseEvidence.from_dict(json.loads(evidence_path.read_text(encoding="utf-8")))
    bundle = replay_application_bundle_from_installed_evidence(installed)
    record = {
        "owner": "release-owner",
        "authority": "internal-release-owner",
        "approval_status": "rejected",
        "package_identity": installed.package_identity,
        "distribution_version": installed.distribution_version,
        "installed_wheel_evidence_sha256": installed.canonical_sha256,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "limitations_hash": governance_canonical_sha256(LIMITATIONS),
        "abstention_policy_hash": governance_canonical_sha256(ABSTENTION_POLICY),
        "acknowledged_hashes": [
            CLAIM_BOUNDARY_HASH,
            governance_canonical_sha256(LIMITATIONS),
            governance_canonical_sha256(ABSTENTION_POLICY),
        ],
        "approved_at_or_version": "approval-record-rejected-not-evaluated",
    }
    record["canonical_sha256"] = governance_canonical_sha256(record)
    approval = build_release_approval_evidence(record, installed)

    decision = transition_release_governance(None, bundle, installed, approval)

    assert decision.application_release_status == "blocked"


def test_governance_writer_loads_not_evaluated_ready_and_released_decisions(tmp_path) -> None:
    not_evaluated_root = tmp_path / "not-evaluated"
    not_evaluated_root.mkdir()
    not_evaluated_path = write_not_evaluated_installed_evidence_fixture(not_evaluated_root, version="0.1.0")
    not_evaluated_installed = InstalledWheelReleaseEvidence.from_dict(json.loads(not_evaluated_path.read_text(encoding="utf-8")))
    not_evaluated_bundle = replay_application_bundle_from_installed_evidence(not_evaluated_installed)
    not_evaluated_application = tmp_path / "not-evaluated-application.json"
    not_evaluated_application.write_text(json.dumps(not_evaluated_bundle.to_dict(), sort_keys=True), encoding="utf-8")
    not_evaluated_decision_path = write_canonical_governance_decision_artifact(
        output_path=tmp_path / "not-evaluated-decision.json",
        application_evidence_path=not_evaluated_application,
        installed_evidence_path=not_evaluated_path,
    )
    assert load_canonical_governance_decision(not_evaluated_decision_path).application_release_status == "not_evaluated"

    ready_root = tmp_path / "ready"
    ready_root.mkdir()
    ready_installed_path = write_structurally_valid_installed_evidence_fixture(ready_root, version="0.1.0")
    ready_installed = InstalledWheelReleaseEvidence.from_dict(json.loads(ready_installed_path.read_text(encoding="utf-8")))
    ready_bundle = replay_application_bundle_from_installed_evidence(ready_installed)
    ready_application = tmp_path / "ready-application.json"
    ready_application.write_text(json.dumps(ready_bundle.to_dict(), sort_keys=True), encoding="utf-8")
    ready_decision_path = write_canonical_governance_decision_artifact(
        output_path=tmp_path / "ready-decision.json",
        application_evidence_path=ready_application,
        installed_evidence_path=ready_installed_path,
    )
    assert load_canonical_governance_decision(ready_decision_path).application_release_status == "internal_source_grounded_ready"

    approval_record = {
        "owner": "release-owner",
        "authority": "internal-release-owner",
        "approval_status": "approved",
        "package_identity": ready_installed.package_identity,
        "distribution_version": ready_installed.distribution_version,
        "installed_wheel_evidence_sha256": ready_installed.canonical_sha256,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "limitations_hash": governance_canonical_sha256(LIMITATIONS),
        "abstention_policy_hash": governance_canonical_sha256(ABSTENTION_POLICY),
        "acknowledged_hashes": [
            CLAIM_BOUNDARY_HASH,
            governance_canonical_sha256(LIMITATIONS),
            governance_canonical_sha256(ABSTENTION_POLICY),
        ],
        "approved_at_or_version": "approval-record-003",
    }
    approval_record["canonical_sha256"] = governance_canonical_sha256(approval_record)
    approval_path = tmp_path / "approval-record.json"
    approval_path.write_text(json.dumps(approval_record, sort_keys=True), encoding="utf-8")
    direct_approval_path = write_canonical_governance_decision_artifact(
        output_path=tmp_path / "direct-approval-decision.json",
        application_evidence_path=ready_application,
        installed_evidence_path=ready_installed_path,
        approval_record_path=approval_path,
    )
    assert load_canonical_governance_decision(direct_approval_path).application_release_status == "internal_source_grounded_ready"
    released_path = write_canonical_governance_decision_artifact(
        output_path=tmp_path / "released-decision.json",
        application_evidence_path=ready_application,
        installed_evidence_path=ready_installed_path,
        approval_record_path=approval_path,
        previous_ready_decision_path=ready_decision_path,
    )
    assert load_canonical_governance_decision(released_path).application_release_status == "released_internal_source_grounded"


def test_governance_loader_rejects_tampered_sidecar_or_advertised_hash(tmp_path) -> None:
    installed_path = write_structurally_valid_installed_evidence_fixture(tmp_path, version="0.1.0")
    installed = InstalledWheelReleaseEvidence.from_dict(json.loads(installed_path.read_text(encoding="utf-8")))
    bundle = replay_application_bundle_from_installed_evidence(installed)
    application_path = tmp_path / "application-evidence.json"
    application_path.write_text(json.dumps(bundle.to_dict(), sort_keys=True), encoding="utf-8")
    decision_path = write_canonical_governance_decision_artifact(
        output_path=tmp_path / "governance-decision.json",
        application_evidence_path=application_path,
        installed_evidence_path=installed_path,
    )
    envelope = json.loads(decision_path.read_text(encoding="utf-8"))
    envelope["installed_evidence_canonical_sha256"] = "0" * 64
    decision_path.write_text(json.dumps(envelope, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="hash mismatch"):
        load_canonical_governance_decision(decision_path)

    sidecar_root = tmp_path / "sidecar-tamper"
    sidecar_root.mkdir()
    installed_path = write_structurally_valid_installed_evidence_fixture(sidecar_root, version="0.1.0")
    installed = InstalledWheelReleaseEvidence.from_dict(json.loads(installed_path.read_text(encoding="utf-8")))
    bundle = replay_application_bundle_from_installed_evidence(installed)
    application_path = tmp_path / "sidecar-tamper-application.json"
    application_path.write_text(json.dumps(bundle.to_dict(), sort_keys=True), encoding="utf-8")
    decision_path = write_canonical_governance_decision_artifact(
        output_path=tmp_path / "sidecar-tamper-decision.json",
        application_evidence_path=application_path,
        installed_evidence_path=installed_path,
    )
    installed_payload = json.loads(installed_path.read_text(encoding="utf-8"))
    installed_payload["wheel_sha256"] = "f" * 64
    installed_path.write_text(json.dumps(installed_payload, sort_keys=True), encoding="utf-8")
    with pytest.raises(ValueError, match="sidecar"):
        load_canonical_governance_decision(decision_path)
```

Create `tests\unit\test_release_version_workflow.py`:

```python
import json
from hashlib import sha256
from pathlib import Path

import pytest

from mingli_engine.application_validation import (
    RawAbstentionResult,
    RawDeterminismResult,
    RawPackagingResult,
    RawPrivacyResult,
    RawSafetyResult,
    RawSchoolConflictResult,
    RawTraceResult,
    RawUnsupportedInferenceResult,
    RawVersionBindingResult,
    produce_abstention_gate,
    produce_deterministic_gate,
    produce_packaging_gate,
    produce_privacy_gate,
    produce_safety_gate,
    produce_school_conflict_gate,
    produce_trace_gate,
    produce_unsupported_inference_gate,
    produce_version_binding_gate,
)
from mingli_engine.domain_calibration import build_release_version_set
from mingli_engine.domain_calibration_models import InstalledWheelReleaseEvidence, governance_canonical_sha256
from mingli_engine.domain_calibration_release import (
    ABSTENTION_POLICY,
    CLAIM_BOUNDARY_HASH,
    LIMITATIONS,
    RELEASE_STATEMENT,
    build_installed_wheel_release_evidence_from_audit_files,
    load_canonical_governance_decision,
    replay_application_bundle_from_installed_evidence,
)
from mingli_engine.release_version_workflow import main
from tests.unit.governance_decision_fixtures import write_not_evaluated_installed_evidence_fixture


def _write_structural_installed_evidence_fixture(
    tmp_path: Path,
    version: str = "0.1.0",
    raw_overrides: dict[str, object] | None = None,
) -> Path:
    manifest = {
        "data/calculation/school_profiles.json": "a" * 64,
        "data/calculation/strength_weights.json": "b" * 64,
        "data/release_docs/source_grounded_internal_release.md": "c" * 64,
        "data/release_docs/internal_release_notes.md": "d" * 64,
    }
    version_set = build_release_version_set(version)
    raw_by_gate = {
        "deterministic_calculation": RawDeterminismResult(
            first_run_hash="1" * 64,
            second_run_hash="1" * 64,
            calculation_checks={"stages_present": "passed", "placeholder_integrity": "passed"},
        ),
        "source_rule_tracing": RawTraceResult(
            emitted_claim_ids=("claim-1",),
            traced_claim_ids=("claim-1",),
            emitted_rule_ids=("rule-1",),
            traced_rule_ids=("rule-1",),
        ),
        "unsupported_inference": RawUnsupportedInferenceResult(
            computed_claim_ids=("claim-1",),
            supported_claim_ids=("claim-1",),
            dependency_bypass_ids=(),
        ),
        "school_conflict": RawSchoolConflictResult(
            conflict_case_ids=("conflict-1",),
            recalled_conflict_case_ids=("conflict-1",),
            silent_collapse_case_ids=(),
        ),
        "abstention": RawAbstentionResult(
            required_abstention_case_ids=("abstain-1",),
            observed_abstention_case_ids=("abstain-1",),
        ),
        "safety_critical": RawSafetyResult(safety_case_count=1, exact_match_count=1, prohibited_output_count=0),
        "privacy": RawPrivacyResult(scenario_count=1, privacy_failed_scenarios=(), write_count=0, leak_count=0),
        "packaging": RawPackagingResult(
            asset_sha256=manifest,
            expected_asset_paths=tuple(sorted(manifest)),
            source_isolated=True,
            distribution_version=version,
        ),
        "version_binding": RawVersionBindingResult(
            package_identity="mingli-engine",
            distribution_version=version,
            application_version=version,
            exact_version_set=version_set,
        ),
    }
    if raw_overrides:
        raw_by_gate.update(raw_overrides)
    gate_by_id = {
        "deterministic_calculation": produce_deterministic_gate(raw_by_gate["deterministic_calculation"]),
        "source_rule_tracing": produce_trace_gate(raw_by_gate["source_rule_tracing"]),
        "unsupported_inference": produce_unsupported_inference_gate(raw_by_gate["unsupported_inference"]),
        "school_conflict": produce_school_conflict_gate(raw_by_gate["school_conflict"]),
        "abstention": produce_abstention_gate(raw_by_gate["abstention"]),
        "safety_critical": produce_safety_gate(raw_by_gate["safety_critical"]),
        "privacy": produce_privacy_gate(raw_by_gate["privacy"]),
        "packaging": produce_packaging_gate(raw_by_gate["packaging"]),
        "version_binding": produce_version_binding_gate(raw_by_gate["version_binding"]),
    }
    audit_payload = {
        "package_identity": "mingli-engine",
        "distribution_version": version,
        "application_version": version,
        "exact_version_set": version_set.__dict__,
        "resource_manifest_sha256": manifest,
        "wheel_resource_manifest_sha256": manifest,
        "pre_reproducibility_gate_evidence": {
            gate_id: {"raw_payload": gate.raw_payload, "evidence": gate.to_dict()}
            for gate_id, gate in gate_by_id.items()
        },
        "release_statement": RELEASE_STATEMENT,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "wheel_filename": f"mingli_engine-{version}-py3-none-any.whl",
        "wheel_sha256": "e" * 64,
        "environment": {"python": "3.12", "platform": "test", "dependencies": {"mingli-engine": version}},
        "source_isolated": True,
        "mingli_engine_file": str(tmp_path / "venv" / "Lib" / "site-packages" / "mingli_engine" / "__init__.py"),
    }
    first_audit = tmp_path / "first-installed-audit.json"
    second_audit = tmp_path / "second-installed-audit.json"
    first_audit.write_text(json.dumps(audit_payload, sort_keys=True), encoding="utf-8")
    second_audit.write_text(json.dumps(audit_payload, sort_keys=True), encoding="utf-8")
    evidence = build_installed_wheel_release_evidence_from_audit_files(
        first_audit_path=first_audit,
        second_audit_path=second_audit,
        fresh_install_target=tmp_path / "venv",
        checkout_root=tmp_path / "checkout",
        expected_manifest=manifest,
    )
    path = tmp_path / f"installed-evidence-{version}-{governance_canonical_sha256(audit_payload)[:12]}.json"
    path.write_text(json.dumps(evidence.to_dict(), sort_keys=True), encoding="utf-8")
    return path


def test_update_version_source_requires_verified_decision_and_installed_evidence(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    Path("pyproject.toml").write_text('[project]\nname = "mingli-engine"\nversion = "0.1.0"\n', encoding="utf-8")
    decision_path = tmp_path / "decision.json"
    evidence_path = _write_structural_installed_evidence_fixture(tmp_path)
    assert main(["decide-version", "--evidence", str(evidence_path), "--owner-version", "0.1.1", "--output", str(decision_path)]) == 0

    exit_code = main(
        [
            "update-version-source",
            "--owner-version",
            "0.1.1",
            "--decision",
            str(decision_path),
            "--evidence",
            str(evidence_path),
        ]
    )

    assert exit_code == 0
    assert 'version = "0.1.1"' in Path("pyproject.toml").read_text(encoding="utf-8")


def test_write_governance_decision_cli_replays_sidecars_and_writes_canonical_artifact(tmp_path: Path) -> None:
    installed_path = _write_structural_installed_evidence_fixture(tmp_path, version="0.1.0")
    installed = InstalledWheelReleaseEvidence.from_dict(json.loads(installed_path.read_text(encoding="utf-8")))
    application_bundle = replay_application_bundle_from_installed_evidence(installed)
    application_path = tmp_path / "application-evidence.json"
    application_path.write_text(json.dumps(application_bundle.to_dict(), sort_keys=True), encoding="utf-8")
    output_path = tmp_path / "governance-decision.json"

    exit_code = main(
        [
            "write-governance-decision",
            "--application-evidence",
            str(application_path),
            "--installed-evidence",
            str(installed_path),
            "--output",
            str(output_path),
        ]
    )

    envelope = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert envelope["application_evidence_canonical_sha256"] == application_bundle.canonical_sha256
    assert envelope["installed_evidence_canonical_sha256"] == installed.canonical_sha256
    assert envelope["decision"]["application_release_status"] == "internal_source_grounded_ready"


def test_write_governance_decision_cli_returns_nonzero_for_not_evaluated(tmp_path: Path, capsys) -> None:
    installed_path = write_not_evaluated_installed_evidence_fixture(tmp_path, version="0.1.0")
    output_path = tmp_path / "not-evaluated-governance-decision.json"

    exit_code = main(
        [
            "write-governance-decision",
            "--installed-evidence",
            str(installed_path),
            "--output",
            str(output_path),
        ]
    )

    stdout = json.loads(capsys.readouterr().out)
    envelope = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 4
    assert stdout["application_release_status"] == "not_evaluated"
    assert envelope["decision"]["application_release_status"] == "not_evaluated"


def _assert_non_ready_governance_artifact_matches_inspect(
    *,
    installed_path: Path,
    expected_status: str,
    tmp_path: Path,
    capsys,
) -> None:
    inspect_path = tmp_path / f"{expected_status}-final-inspect.json"
    non_ready_decision_path = tmp_path / f"canonical-{expected_status}-governance-decision.json"

    inspect_exit = main(["inspect-installed-evidence", "--evidence", str(installed_path), "--output", str(inspect_path)])
    inspect_payload = json.loads(inspect_path.read_text(encoding="utf-8"))
    writer_exit = main(["write-governance-decision", "--installed-evidence", str(installed_path), "--output", str(non_ready_decision_path)])

    stdout = json.loads(capsys.readouterr().out)
    reloaded = load_canonical_governance_decision(non_ready_decision_path)
    assert inspect_exit == 4
    assert writer_exit == 4
    assert inspect_payload["application_release_status"] == expected_status
    assert stdout["application_release_status"] == inspect_payload["application_release_status"]
    assert reloaded.application_release_status == inspect_payload["application_release_status"]
    assert reloaded.canonical_sha256 == stdout["canonical_sha256"]


def test_final_not_evaluated_governance_artifact_reloads_and_matches_inspect_status(tmp_path: Path, capsys) -> None:
    installed_path = write_not_evaluated_installed_evidence_fixture(tmp_path, version="0.1.0")

    _assert_non_ready_governance_artifact_matches_inspect(
        installed_path=installed_path,
        expected_status="not_evaluated",
        tmp_path=tmp_path,
        capsys=capsys,
    )


def test_final_blocked_governance_artifact_reloads_and_matches_inspect_status(tmp_path: Path, capsys) -> None:
    blocked_root = tmp_path / "blocked"
    blocked_root.mkdir()
    installed_path = _write_structural_installed_evidence_fixture(
        blocked_root,
        version="0.1.0",
        raw_overrides={
            "safety_critical": RawSafetyResult(
                safety_case_count=2,
                exact_match_count=1,
                prohibited_output_count=1,
            )
        },
    )
    installed = InstalledWheelReleaseEvidence.from_dict(json.loads(installed_path.read_text(encoding="utf-8")))

    assert installed.gate_statuses["safety_critical"] == "failed"
    assert installed.gate_canonical_hashes["safety_critical"]
    _assert_non_ready_governance_artifact_matches_inspect(
        installed_path=installed_path,
        expected_status="blocked",
        tmp_path=tmp_path,
        capsys=capsys,
    )


def test_rejected_approval_cli_returns_4_and_reloads_blocked_decision(tmp_path: Path, capsys) -> None:
    installed_path = _write_structural_installed_evidence_fixture(tmp_path, version="0.1.0")
    installed = InstalledWheelReleaseEvidence.from_dict(json.loads(installed_path.read_text(encoding="utf-8")))
    ready_path = tmp_path / "canonical-ready-governance-decision.json"
    rejected_path = tmp_path / "canonical-rejected-governance-decision.json"
    assert main(["write-governance-decision", "--installed-evidence", str(installed_path), "--output", str(ready_path)]) == 0
    approval_record = {
        "owner": "release-owner",
        "authority": "internal-release-owner",
        "approval_status": "rejected",
        "package_identity": installed.package_identity,
        "distribution_version": installed.distribution_version,
        "installed_wheel_evidence_sha256": installed.canonical_sha256,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "limitations_hash": governance_canonical_sha256(LIMITATIONS),
        "abstention_policy_hash": governance_canonical_sha256(ABSTENTION_POLICY),
        "acknowledged_hashes": [
            CLAIM_BOUNDARY_HASH,
            governance_canonical_sha256(LIMITATIONS),
            governance_canonical_sha256(ABSTENTION_POLICY),
        ],
        "approved_at_or_version": "approval-record-rejected-cli",
    }
    approval_record["canonical_sha256"] = governance_canonical_sha256(approval_record)
    approval_path = tmp_path / "rejected-approval-record.json"
    approval_path.write_text(json.dumps(approval_record, sort_keys=True), encoding="utf-8")

    exit_code = main(
        [
            "write-governance-decision",
            "--installed-evidence",
            str(installed_path),
            "--approval-record",
            str(approval_path),
            "--previous-ready-decision",
            str(ready_path),
            "--output",
            str(rejected_path),
        ]
    )

    stdout = json.loads(capsys.readouterr().out.splitlines()[-1])
    reloaded = load_canonical_governance_decision(rejected_path)
    assert exit_code == 4
    assert stdout["application_release_status"] == "blocked"
    assert reloaded.application_release_status == "blocked"
    assert reloaded.canonical_sha256 == stdout["canonical_sha256"]


def test_inspect_not_evaluated_installed_evidence_stops_before_version_decision(tmp_path: Path) -> None:
    evidence_path = write_not_evaluated_installed_evidence_fixture(tmp_path, version="0.1.0")
    inspect_path = tmp_path / "inspect.json"

    exit_code = main(["inspect-installed-evidence", "--evidence", str(evidence_path), "--output", str(inspect_path)])

    payload = json.loads(inspect_path.read_text(encoding="utf-8"))
    assert exit_code == 4
    assert payload["application_release_status"] == "not_evaluated"
    with pytest.raises(ValueError, match="all installed application gates must pass"):
        main(["decide-version", "--evidence", str(evidence_path), "--owner-version", "0.1.0", "--output", str(tmp_path / "decision.json")])


def test_update_version_source_rejects_missing_or_mismatched_decision(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    Path("pyproject.toml").write_text('[project]\nname = "mingli-engine"\nversion = "0.1.0"\n', encoding="utf-8")
    decision_path = tmp_path / "decision.json"
    evidence_path = _write_structural_installed_evidence_fixture(tmp_path)
    assert main(["decide-version", "--evidence", str(evidence_path), "--owner-version", "0.1.1", "--output", str(decision_path)]) == 0
    tampered = json.loads(decision_path.read_text(encoding="utf-8"))
    tampered["selected_application_version"] = "0.1.2"
    tampered["canonical_sha256"] = governance_canonical_sha256({key: value for key, value in tampered.items() if key != "canonical_sha256"})
    decision_path.write_text(json.dumps(tampered, sort_keys=True), encoding="utf-8")

    with pytest.raises(SystemExit, match="verified version decision"):
        main(
            [
                "update-version-source",
                "--owner-version",
                "0.1.1",
                "--decision",
                str(decision_path),
                "--evidence",
                str(evidence_path),
            ]
        )


def test_structural_changed_version_workflow_requires_new_audit_before_ready(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    Path("pyproject.toml").write_text('[project]\nname = "mingli-engine"\nversion = "0.1.0"\n', encoding="utf-8")
    evidence_path = _write_structural_installed_evidence_fixture(tmp_path)
    decision_path = tmp_path / "decision.json"

    assert main(["inspect-installed-evidence", "--evidence", str(evidence_path), "--output", str(decision_path)]) == 0
    assert main(["decide-version", "--evidence", str(evidence_path), "--owner-version", "0.1.1", "--output", str(decision_path)]) == 0
    changed_decision = json.loads(decision_path.read_text(encoding="utf-8"))
    assert changed_decision["application_release_status"] == "not_evaluated"
    assert main(["update-version-source", "--owner-version", "0.1.1", "--decision", str(decision_path), "--evidence", str(evidence_path)]) == 0
    assert 'version = "0.1.1"' in Path("pyproject.toml").read_text(encoding="utf-8")

    first_audit = tmp_path / "first-installed-audit.json"
    second_audit = tmp_path / "second-installed-audit.json"
    expected_manifest = tmp_path / "expected-manifest.json"
    final_evidence = tmp_path / "final-installed-wheel-evidence.json"
    first_audit.write_text(json.dumps({"from": "fresh-installed-wheel", "sequence": 1}, sort_keys=True), encoding="utf-8")
    second_audit.write_text(json.dumps({"from": "fresh-installed-wheel", "sequence": 1}, sort_keys=True), encoding="utf-8")
    expected_manifest.write_text(json.dumps({"mingli_engine/data/release_docs/source_grounded_internal_release.md": "a" * 64}, sort_keys=True), encoding="utf-8")

    with pytest.raises(SystemExit):
        main([
            "build-installed-evidence",
            "--first", str(first_audit),
            "--second", str(second_audit),
            "--fresh-install-target", str(tmp_path / "venv"),
            "--checkout-root", str(tmp_path / "checkout"),
            "--expected-manifest", str(expected_manifest),
            "--output", str(final_evidence),
        ])


def test_structural_changed_version_workflow_rebuilds_audits_and_returns_ready_for_new_version(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    Path("pyproject.toml").write_text('[project]\nname = "mingli-engine"\nversion = "0.1.0"\n', encoding="utf-8")
    old_evidence = _write_structural_installed_evidence_fixture(tmp_path, version="0.1.0")
    changed_decision = tmp_path / "changed-version-decision.json"

    assert main(["inspect-installed-evidence", "--evidence", str(old_evidence), "--output", str(tmp_path / "old-inspect.json")]) == 0
    assert main(["decide-version", "--evidence", str(old_evidence), "--owner-version", "0.1.1", "--output", str(changed_decision)]) == 0
    assert main(["update-version-source", "--owner-version", "0.1.1", "--decision", str(changed_decision), "--evidence", str(old_evidence)]) == 0
    assert 'version = "0.1.1"' in Path("pyproject.toml").read_text(encoding="utf-8")

    new_evidence = _write_structural_installed_evidence_fixture(tmp_path, version="0.1.1")
    reloaded_inspect = tmp_path / "new-inspect.json"
    same_version_decision = tmp_path / "same-version-decision.json"

    assert main(["inspect-installed-evidence", "--evidence", str(new_evidence), "--output", str(reloaded_inspect)]) == 0
    assert json.loads(reloaded_inspect.read_text(encoding="utf-8"))["application_release_status"] == "internal_source_grounded_ready"
    assert main(["decide-version", "--evidence", str(new_evidence), "--owner-version", "0.1.1", "--output", str(same_version_decision)]) == 0
    payload = json.loads(same_version_decision.read_text(encoding="utf-8"))
    assert payload["can_reuse_current_installed_evidence"] is True
    assert payload["application_release_status"] == "internal_source_grounded_ready"


def test_changed_version_failure_restores_exact_pyproject_bytes(tmp_path: Path, capsys) -> None:
    pyproject = tmp_path / "pyproject.toml"
    snapshot = tmp_path / "pyproject-original-bytes.snapshot"
    original_bytes = b'\xef\xbb\xbf[project]\r\nname = "mingli-engine"\r\nversion = "0.1.0"\r\n'
    pyproject.write_bytes(original_bytes)
    snapshot.write_bytes(original_bytes)
    pyproject.write_text('[project]\nname = "mingli-engine"\nversion = "0.1.1"\n', encoding="utf-8")

    exit_code = main(["restore-version-source", "--pyproject", str(pyproject), "--snapshot", str(snapshot)])

    stdout = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert pyproject.read_bytes() == original_bytes
    assert stdout["pyproject_sha256"] == sha256(original_bytes).hexdigest()


def test_restore_version_source_rejects_missing_or_inconsistent_snapshot(tmp_path: Path, monkeypatch) -> None:
    pyproject = tmp_path / "pyproject.toml"
    snapshot = tmp_path / "pyproject-original-bytes.snapshot"
    pyproject.write_bytes(b'changed')

    with pytest.raises(FileNotFoundError):
        main(["restore-version-source", "--pyproject", str(pyproject), "--snapshot", str(snapshot)])

    snapshot.write_bytes(b'original')
    import mingli_engine.release_version_workflow as workflow

    def corrupt_restore(path: str | Path, original_bytes: bytes) -> None:
        Path(path).write_bytes(b'not-the-snapshot')

    monkeypatch.setattr(workflow, "restore_version_source_bytes", corrupt_restore)
    with pytest.raises(SystemExit, match="restored version source bytes did not match snapshot"):
        workflow.main(["restore-version-source", "--pyproject", str(pyproject), "--snapshot", str(snapshot)])
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
pytest tests/unit/test_domain_calibration_release.py tests/unit/test_release_version_workflow.py -q
```

Expected: FAIL because version decision, previous-state transition, and approval binding are missing.

- [ ] **Step 3: Add approval and decision models**

Use the Task 4 `build_release_version_set()` helper for owner-selected release versions. Keep `build_candidate_version_set` unchanged so the legacy calibration candidate path remains fixed to its approved candidate semantics and cannot become a release-owner bypass.

Add to `src\mingli_engine\domain_calibration_models.py`:

```python
@dataclass(frozen=True)
class ReleaseVersionDecision:
    selected_application_version: str
    can_reuse_current_installed_evidence: bool
    application_release_status: ApplicationReleaseStatus
    package_identity: str
    distribution_version: str
    application_version: str
    installed_wheel_evidence_sha256: str
    application_bundle_hash: str
    claim_boundary_hash: str
    limitations_hash: str
    abstention_policy_hash: str
    canonical_sha256: str

    def to_dict(self) -> dict[str, object]:
        payload = {
            "selected_application_version": self.selected_application_version,
            "can_reuse_current_installed_evidence": self.can_reuse_current_installed_evidence,
            "application_release_status": self.application_release_status,
            "package_identity": self.package_identity,
            "distribution_version": self.distribution_version,
            "application_version": self.application_version,
            "installed_wheel_evidence_sha256": self.installed_wheel_evidence_sha256,
            "application_bundle_hash": self.application_bundle_hash,
            "claim_boundary_hash": self.claim_boundary_hash,
            "limitations_hash": self.limitations_hash,
            "abstention_policy_hash": self.abstention_policy_hash,
        }
        payload["canonical_sha256"] = governance_canonical_sha256(payload)
        return payload

    @classmethod
    def from_dict(cls, payload: Mapping[str, object], installed_evidence: InstalledWheelReleaseEvidence) -> "ReleaseVersionDecision":
        from mingli_engine.domain_calibration_release import choose_release_version_after_installed_evidence

        if not isinstance(payload["can_reuse_current_installed_evidence"], bool):
            raise ValueError("version decision reuse flag must be a bool")
        recomputed = choose_release_version_after_installed_evidence(
            installed_evidence,
            str(payload["selected_application_version"]),
        )
        if recomputed.to_dict() != dict(payload):
            raise ValueError("version decision does not match recomputed installed evidence decision")
        return recomputed


@dataclass(frozen=True)
class ReleaseApprovalRecord:
    owner: str
    authority: str
    approval_status: Literal["approved", "rejected"]
    package_identity: str
    distribution_version: str
    installed_wheel_evidence_sha256: str
    claim_boundary_hash: str
    limitations_hash: str
    abstention_policy_hash: str
    acknowledged_hashes: tuple[str, ...]
    approved_at_or_version: str
    canonical_sha256: str


@dataclass(frozen=True)
class ReleaseApprovalEvidence:
    approval_status: Literal["not_requested", "approved", "rejected"]
    owner: str | None
    authority: str | None
    package_identity: str | None
    distribution_version: str | None
    installed_wheel_evidence_sha256: str | None
    claim_boundary_hash: str | None
    limitations_hash: str | None
    abstention_policy_hash: str | None
    acknowledged_hashes: tuple[str, ...]
    approved_at_or_version: str | None
    canonical_sha256: str | None

    @classmethod
    def not_requested(cls) -> "ReleaseApprovalEvidence":
        return cls("not_requested", None, None, None, None, None, None, None, None, (), None, None)


@dataclass(frozen=True)
class ReleaseGovernanceDecision:
    application_release_status: ApplicationReleaseStatus
    application_evidence_hash: str | None
    installed_wheel_evidence_hash: str | None
    approval_hash: str | None
    claim_boundary_hash: str
    limitations_hash: str
    abstention_policy_hash: str
    package_identity: str | None
    distribution_version: str | None
    application_version: str | None
    canonical_sha256: str

    def to_dict(self) -> dict[str, object]:
        payload = {
            "application_release_status": self.application_release_status,
            "application_evidence_hash": self.application_evidence_hash,
            "installed_wheel_evidence_hash": self.installed_wheel_evidence_hash,
            "approval_hash": self.approval_hash,
            "claim_boundary_hash": self.claim_boundary_hash,
            "limitations_hash": self.limitations_hash,
            "abstention_policy_hash": self.abstention_policy_hash,
            "package_identity": self.package_identity,
            "distribution_version": self.distribution_version,
            "application_version": self.application_version,
        }
        payload["canonical_sha256"] = governance_canonical_sha256(payload)
        return payload
```

- [ ] **Step 4: Implement version decision, state transition, and approval binding**

Add to `src\mingli_engine\domain_calibration_release.py`:

```python
import json
import os
from hashlib import sha256
from pathlib import Path
from typing import Mapping

from mingli_engine.domain_calibration_models import (
    APPLICATION_GATE_IDS,
    ApplicationReleaseStatus,
    ApplicationEvidenceBundle,
    InstalledWheelReleaseEvidence,
    ReleaseApprovalEvidence,
    ReleaseApprovalRecord,
    ReleaseGovernanceDecision,
    ReleaseVersionDecision,
    governance_canonical_sha256,
    require_sha256,
)
from mingli_engine.application_validation import RawReproducibilityResult, produce_reproducibility_gate


def classify_application_release_status_from_gate_statuses(
    gate_statuses: Mapping[str, str],
) -> ApplicationReleaseStatus:
    if tuple(gate_statuses.keys()) != APPLICATION_GATE_IDS:
        raise ValueError("installed evidence gate ID set must exactly match application hard gates")
    if gate_statuses["safety_critical"] in {"failed", "blocked"}:
        return "blocked"
    if any(status in {"failed", "blocked"} for status in gate_statuses.values()):
        return "blocked"
    if any(status == "not_evaluated" for status in gate_statuses.values()):
        return "not_evaluated"
    if all(status == "passed" for status in gate_statuses.values()):
        return "internal_source_grounded_ready"
    raise ValueError("unknown application gate status")


def choose_release_version_after_installed_evidence(
    installed_evidence: InstalledWheelReleaseEvidence,
    owner_selected_application_version: str,
) -> ReleaseVersionDecision:
    installed_evidence = InstalledWheelReleaseEvidence.from_dict(installed_evidence.to_dict())
    if not installed_evidence.canonical_sha256:
        raise ValueError("installed wheel evidence is required for version decision")
    if classify_application_release_status_from_gate_statuses(installed_evidence.gate_statuses) != "internal_source_grounded_ready":
        raise ValueError("all installed application gates must pass before version decision")
    same_version = owner_selected_application_version == installed_evidence.application_version
    payload = {
        "selected_application_version": owner_selected_application_version,
        "can_reuse_current_installed_evidence": same_version,
        "application_release_status": "internal_source_grounded_ready" if same_version else "not_evaluated",
        "package_identity": installed_evidence.package_identity,
        "distribution_version": installed_evidence.distribution_version,
        "application_version": installed_evidence.application_version,
        "installed_wheel_evidence_sha256": installed_evidence.canonical_sha256,
        "application_bundle_hash": installed_evidence.application_bundle_hash,
        "claim_boundary_hash": installed_evidence.claim_boundary_hash,
        "limitations_hash": governance_canonical_sha256(LIMITATIONS),
        "abstention_policy_hash": governance_canonical_sha256(ABSTENTION_POLICY),
    }
    return ReleaseVersionDecision(canonical_sha256=governance_canonical_sha256(payload), **payload)


def replay_application_bundle_from_installed_evidence(
    installed_evidence: InstalledWheelReleaseEvidence,
) -> ApplicationEvidenceBundle:
    verified = InstalledWheelReleaseEvidence.from_dict(installed_evidence.to_dict())
    first_payload = dict(verified.first_installed_audit_envelope["payload"])
    second_payload = dict(verified.second_installed_audit_envelope["payload"])
    first_hash = governance_canonical_sha256(first_payload)
    second_hash = governance_canonical_sha256(second_payload)
    pre_reproducibility = first_payload["pre_reproducibility_gate_evidence"]
    gates = tuple(
        _gate_from_envelope(gate_id, pre_reproducibility[gate_id])
        for gate_id in APPLICATION_GATE_IDS
        if gate_id != "reproducibility"
    )
    reproducibility = produce_reproducibility_gate(
        RawReproducibilityResult(
            first_payload_hash=first_hash,
            second_payload_hash=second_hash,
            executed_from_installed_package=True,
        )
    )
    return ApplicationEvidenceBundle.from_gate_evidence(gates + (reproducibility,))


def build_release_approval_evidence(
    record: dict[str, object] | None,
    installed_evidence: InstalledWheelReleaseEvidence | None,
) -> ReleaseApprovalEvidence:
    if record is None:
        return ReleaseApprovalEvidence.not_requested()
    if installed_evidence is None:
        raise ValueError("installed evidence is required for approval")
    expected_record_keys = {
        "owner",
        "authority",
        "approval_status",
        "package_identity",
        "distribution_version",
        "installed_wheel_evidence_sha256",
        "claim_boundary_hash",
        "limitations_hash",
        "abstention_policy_hash",
        "acknowledged_hashes",
        "approved_at_or_version",
        "canonical_sha256",
    }
    if set(record) != expected_record_keys:
        raise ValueError("approval record field set mismatch")
    record_without_hash = {key: value for key, value in record.items() if key != "canonical_sha256"}
    if governance_canonical_sha256(record_without_hash) != record["canonical_sha256"]:
        raise ValueError("approval record canonical hash mismatch")
    approval_status = str(record["approval_status"])
    if approval_status not in {"approved", "rejected"}:
        raise ValueError("approval_status must be approved or rejected")
    approval_record = ReleaseApprovalRecord(
        owner=str(record["owner"]),
        authority=str(record["authority"]),
        approval_status=approval_status,
        package_identity=str(record["package_identity"]),
        distribution_version=str(record["distribution_version"]),
        installed_wheel_evidence_sha256=str(record["installed_wheel_evidence_sha256"]),
        claim_boundary_hash=str(record["claim_boundary_hash"]),
        limitations_hash=str(record["limitations_hash"]),
        abstention_policy_hash=str(record["abstention_policy_hash"]),
        acknowledged_hashes=tuple(str(value) for value in record["acknowledged_hashes"]),
        approved_at_or_version=str(record["approved_at_or_version"]),
        canonical_sha256=str(record["canonical_sha256"]),
    )
    expected_hashes = (
        CLAIM_BOUNDARY_HASH,
        governance_canonical_sha256(LIMITATIONS),
        governance_canonical_sha256(ABSTENTION_POLICY),
    )
    for digest in (
        approval_record.installed_wheel_evidence_sha256,
        approval_record.claim_boundary_hash,
        approval_record.limitations_hash,
        approval_record.abstention_policy_hash,
    ):
        require_sha256(digest, "approval bound hash")
    if approval_record.installed_wheel_evidence_sha256 != installed_evidence.canonical_sha256:
        raise ValueError("approval installed evidence hash mismatch")
    if approval_record.package_identity != installed_evidence.package_identity:
        raise ValueError("approval package identity mismatch")
    if approval_record.distribution_version != installed_evidence.distribution_version:
        raise ValueError("approval distribution version mismatch")
    if approval_record.claim_boundary_hash != expected_hashes[0]:
        raise ValueError("approval claim boundary hash mismatch")
    if approval_record.limitations_hash != expected_hashes[1]:
        raise ValueError("approval limitations hash mismatch")
    if approval_record.abstention_policy_hash != expected_hashes[2]:
        raise ValueError("approval abstention policy hash mismatch")
    if approval_record.acknowledged_hashes != expected_hashes:
        raise ValueError("approval acknowledgement hashes mismatch")
    return ReleaseApprovalEvidence(
        approval_status=approval_record.approval_status,
        owner=approval_record.owner,
        authority=approval_record.authority,
        package_identity=approval_record.package_identity,
        distribution_version=approval_record.distribution_version,
        installed_wheel_evidence_sha256=approval_record.installed_wheel_evidence_sha256,
        claim_boundary_hash=approval_record.claim_boundary_hash,
        limitations_hash=approval_record.limitations_hash,
        abstention_policy_hash=approval_record.abstention_policy_hash,
        acknowledged_hashes=approval_record.acknowledged_hashes,
        approved_at_or_version=approval_record.approved_at_or_version,
        canonical_sha256=approval_record.canonical_sha256,
    )


def transition_release_governance(
    previous: ReleaseGovernanceDecision | None,
    application_evidence: ApplicationEvidenceBundle,
    installed_evidence: InstalledWheelReleaseEvidence | None,
    approval: ReleaseApprovalEvidence | None,
) -> ReleaseGovernanceDecision:
    application_evidence = ApplicationEvidenceBundle.from_dict(application_evidence.to_dict())
    if installed_evidence is not None:
        installed_evidence = InstalledWheelReleaseEvidence.from_dict(installed_evidence.to_dict())

    def make_decision(status: ApplicationReleaseStatus) -> ReleaseGovernanceDecision:
        payload = {
            "application_release_status": status,
            "application_evidence_hash": application_evidence.canonical_sha256,
            "installed_wheel_evidence_hash": installed_evidence.canonical_sha256 if installed_evidence else None,
            "approval_hash": approval.canonical_sha256 if approval else None,
            "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
            "limitations_hash": governance_canonical_sha256(LIMITATIONS),
            "abstention_policy_hash": governance_canonical_sha256(ABSTENTION_POLICY),
            "package_identity": installed_evidence.package_identity if installed_evidence else None,
            "distribution_version": installed_evidence.distribution_version if installed_evidence else None,
            "application_version": installed_evidence.application_version if installed_evidence else None,
        }
        return ReleaseGovernanceDecision(canonical_sha256=governance_canonical_sha256(payload), **payload)

    if installed_evidence is not None and installed_evidence.application_bundle_hash != application_evidence.canonical_sha256:
        raise ValueError("installed payload bundle hash must equal current application bundle hash")
    if approval is not None and approval.approval_status == "rejected":
        return make_decision("blocked")
    if installed_evidence is not None:
        gate_status = classify_application_release_status_from_gate_statuses(installed_evidence.gate_statuses)
        if gate_status == "blocked":
            return make_decision("blocked")
        if gate_status == "not_evaluated":
            return make_decision("not_evaluated")
    if application_evidence.overall_status in {"blocked", "failed"}:
        status = "blocked"
    elif application_evidence.overall_status == "not_evaluated" or installed_evidence is None:
        status = "not_evaluated"
    elif approval is None or approval.approval_status == "not_requested":
        status = "internal_source_grounded_ready"
    elif (
        previous is not None
        and previous.application_release_status == "internal_source_grounded_ready"
        and previous.application_evidence_hash == application_evidence.canonical_sha256
        and previous.installed_wheel_evidence_hash == installed_evidence.canonical_sha256
        and previous.claim_boundary_hash == CLAIM_BOUNDARY_HASH
        and previous.distribution_version == installed_evidence.distribution_version
        and previous.application_version == installed_evidence.application_version
        and approval.approval_status == "approved"
        and approval.installed_wheel_evidence_sha256 == installed_evidence.canonical_sha256
    ):
        status = "released_internal_source_grounded"
    else:
        status = "internal_source_grounded_ready"
    return make_decision(status)
```

Add the canonical governance decision artifact writer and loader to the same `domain_calibration_release.py` task before `release_version_workflow.py` imports them:

```python
def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _resolve_sidecar(decision_path: Path, sidecar: str | None) -> Path | None:
    if sidecar is None:
        return None
    path = Path(sidecar)
    return path.resolve() if path.is_absolute() else (decision_path.parent / path).resolve()


def _stable_sidecar_path(output_parent: Path, sidecar: Path | None) -> str | None:
    if sidecar is None:
        return None
    resolved = sidecar.resolve()
    try:
        return str(resolved.relative_to(output_parent))
    except ValueError:
        return str(resolved)


def write_canonical_governance_decision_artifact(
    *,
    output_path: str | Path,
    installed_evidence_path: str | Path,
    application_evidence_path: str | Path | None = None,
    approval_record_path: str | Path | None = None,
    previous_ready_decision_path: str | Path | None = None,
) -> Path:
    output = Path(output_path).resolve()
    output_parent = output.parent
    output_parent.mkdir(parents=True, exist_ok=True)
    if not output_parent.is_dir():
        raise ValueError("governance decision output parent must be a directory")
    installed_path = Path(installed_evidence_path).resolve()
    application_path = Path(application_evidence_path).resolve() if application_evidence_path else None
    approval_path = Path(approval_record_path).resolve() if approval_record_path else None
    previous_path = Path(previous_ready_decision_path).resolve() if previous_ready_decision_path else None
    installed = InstalledWheelReleaseEvidence.from_dict(_read_json(installed_path))
    replayed_application = replay_application_bundle_from_installed_evidence(installed)
    if application_path is None:
        application_path = output_parent / "application-evidence-from-installed.json"
        application_path.write_text(json.dumps(replayed_application.to_dict(), sort_keys=True), encoding="utf-8")
        application_evidence = replayed_application
    else:
        application_evidence = ApplicationEvidenceBundle.from_dict(_read_json(application_path))
        if application_evidence.to_dict() != replayed_application.to_dict():
            raise ValueError("application evidence sidecar does not match installed evidence replay")
    approval = build_release_approval_evidence(_read_json(approval_path) if approval_path else None, installed)
    previous = load_canonical_governance_decision(previous_path) if previous_path else None
    decision = transition_release_governance(previous, application_evidence, installed, approval)
    envelope = {
        "schema_version": "source-grounded-governance-decision.v1",
        "decision": decision.to_dict(),
        "application_evidence_path": _stable_sidecar_path(output_parent, application_path),
        "application_evidence_artifact_sha256": _artifact_sha256(application_path),
        "application_evidence_canonical_sha256": application_evidence.canonical_sha256,
        "installed_evidence_path": _stable_sidecar_path(output_parent, installed_path),
        "installed_evidence_artifact_sha256": _artifact_sha256(installed_path),
        "installed_evidence_canonical_sha256": installed.canonical_sha256,
        "approval_record_path": _stable_sidecar_path(output_parent, approval_path),
        "approval_record_artifact_sha256": _artifact_sha256(approval_path) if approval_path else None,
        "approval_record_canonical_sha256": approval.canonical_sha256,
        "previous_ready_decision_path": _stable_sidecar_path(output_parent, previous_path),
        "previous_ready_decision_artifact_sha256": _artifact_sha256(previous_path) if previous_path else None,
        "previous_ready_decision_canonical_sha256": previous.canonical_sha256 if previous else None,
    }
    envelope["canonical_sha256"] = governance_canonical_sha256(envelope)
    output.write_text(json.dumps(envelope, sort_keys=True), encoding="utf-8")
    return output


def load_canonical_governance_decision(path: str | Path | None = None) -> ReleaseGovernanceDecision:
    decision_path = Path(path or os.environ["MINGLI_CANONICAL_GOVERNANCE_DECISION"])
    envelope = _read_json(decision_path)
    expected_keys = {
        "schema_version",
        "decision",
        "application_evidence_path",
        "application_evidence_artifact_sha256",
        "application_evidence_canonical_sha256",
        "installed_evidence_path",
        "installed_evidence_artifact_sha256",
        "installed_evidence_canonical_sha256",
        "approval_record_path",
        "approval_record_artifact_sha256",
        "approval_record_canonical_sha256",
        "previous_ready_decision_path",
        "previous_ready_decision_artifact_sha256",
        "previous_ready_decision_canonical_sha256",
        "canonical_sha256",
    }
    if set(envelope) != expected_keys:
        raise ValueError("canonical governance decision envelope field set mismatch")
    advertised_envelope_hash = str(envelope["canonical_sha256"])
    envelope_without_hash = {key: value for key, value in envelope.items() if key != "canonical_sha256"}
    if governance_canonical_sha256(envelope_without_hash) != advertised_envelope_hash:
        raise ValueError("canonical governance decision envelope hash mismatch")
    application_path = _resolve_sidecar(decision_path, str(envelope["application_evidence_path"]))
    installed_path = _resolve_sidecar(decision_path, str(envelope["installed_evidence_path"]))
    approval_path = _resolve_sidecar(decision_path, envelope["approval_record_path"])
    previous_path = _resolve_sidecar(decision_path, envelope["previous_ready_decision_path"])
    if _artifact_sha256(application_path) != envelope["application_evidence_artifact_sha256"]:
        raise ValueError("application evidence sidecar artifact hash mismatch")
    if _artifact_sha256(installed_path) != envelope["installed_evidence_artifact_sha256"]:
        raise ValueError("installed evidence sidecar artifact hash mismatch")
    if approval_path and _artifact_sha256(approval_path) != envelope["approval_record_artifact_sha256"]:
        raise ValueError("approval record sidecar artifact hash mismatch")
    if previous_path and _artifact_sha256(previous_path) != envelope["previous_ready_decision_artifact_sha256"]:
        raise ValueError("previous ready decision sidecar artifact hash mismatch")
    application_evidence = ApplicationEvidenceBundle.from_dict(_read_json(application_path))
    installed = InstalledWheelReleaseEvidence.from_dict(_read_json(installed_path))
    if application_evidence.canonical_sha256 != envelope["application_evidence_canonical_sha256"]:
        raise ValueError("application evidence advertised canonical hash mismatch")
    if installed.canonical_sha256 != envelope["installed_evidence_canonical_sha256"]:
        raise ValueError("installed evidence advertised canonical hash mismatch")
    replayed_application = replay_application_bundle_from_installed_evidence(installed)
    if replayed_application.to_dict() != application_evidence.to_dict():
        raise ValueError("application evidence sidecar does not match installed evidence replay")
    approval_record = _read_json(approval_path) if approval_path else None
    approval = build_release_approval_evidence(approval_record, installed)
    if approval.canonical_sha256 != envelope["approval_record_canonical_sha256"]:
        raise ValueError("approval record advertised canonical hash mismatch")
    previous = load_canonical_governance_decision(previous_path) if previous_path else None
    if previous and previous.canonical_sha256 != envelope["previous_ready_decision_canonical_sha256"]:
        raise ValueError("previous ready decision advertised canonical hash mismatch")
    recomputed = transition_release_governance(previous, application_evidence, installed, approval)
    if recomputed.to_dict() != envelope["decision"]:
        raise ValueError("canonical governance decision does not match recomputed transition")
    return recomputed
```

Create `src\mingli_engine\release_version_workflow.py`:

```python
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path

from mingli_engine.domain_calibration_models import InstalledWheelReleaseEvidence, ReleaseVersionDecision
from mingli_engine.domain_calibration_release import (
    build_installed_wheel_release_evidence_from_audit_files,
    choose_release_version_after_installed_evidence,
    classify_application_release_status_from_gate_statuses,
    write_canonical_governance_decision_artifact,
)


def _write(path: str, payload: dict[str, object]) -> None:
    Path(path).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _load_evidence(path: str) -> InstalledWheelReleaseEvidence:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return InstalledWheelReleaseEvidence.from_dict(payload)


def restore_version_source_bytes(path: str | Path, original_bytes: bytes) -> None:
    Path(path).write_bytes(original_bytes)


def _restore_version_source(args: argparse.Namespace) -> int:
    snapshot_bytes = Path(args.snapshot).read_bytes()
    restore_version_source_bytes(args.pyproject, snapshot_bytes)
    restored_bytes = Path(args.pyproject).read_bytes()
    if restored_bytes != snapshot_bytes:
        raise SystemExit("restored version source bytes did not match snapshot")
    print(json.dumps({"pyproject_sha256": sha256(restored_bytes).hexdigest()}, sort_keys=True))
    return 0


def _inspect_installed_evidence(args: argparse.Namespace) -> int:
    evidence = _load_evidence(args.evidence)
    status = classify_application_release_status_from_gate_statuses(evidence.gate_statuses)
    _write(
        args.output,
        {
            "application_release_status": status,
            "gate_statuses": dict(evidence.gate_statuses),
            "installed_wheel_evidence_hash": evidence.canonical_sha256,
            "package_identity": evidence.package_identity,
            "distribution_version": evidence.distribution_version,
            "application_version": evidence.application_version,
        },
    )
    return 0 if status == "internal_source_grounded_ready" else 4


def _decide_version(args: argparse.Namespace) -> int:
    evidence = _load_evidence(args.evidence)
    decision = choose_release_version_after_installed_evidence(evidence, args.owner_version)
    _write(args.output, decision.__dict__)
    return 0


def _update_version_source(args: argparse.Namespace) -> int:
    evidence = _load_evidence(args.evidence)
    decision_payload = json.loads(Path(args.decision).read_text(encoding="utf-8"))
    decision = ReleaseVersionDecision.from_dict(decision_payload, evidence)
    if decision.selected_application_version != args.owner_version:
        raise SystemExit("verified version decision does not match requested owner version")
    if decision.application_release_status != "not_evaluated":
        raise SystemExit("verified version decision must reset changed versions to not_evaluated")
    if decision.installed_wheel_evidence_sha256 != evidence.canonical_sha256:
        raise SystemExit("verified version decision is not bound to installed evidence")
    if evidence.package_identity != "mingli-engine":
        raise SystemExit("verified installed evidence package identity is invalid")
    pyproject = Path("pyproject.toml")
    text = pyproject.read_text(encoding="utf-8")
    lines = []
    replaced = False
    for line in text.splitlines():
        if line.startswith("version = "):
            lines.append(f'version = "{args.owner_version}"')
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        raise SystemExit("pyproject version field is missing")
    pyproject.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


def _build_installed_evidence(args: argparse.Namespace) -> int:
    expected_manifest = json.loads(Path(args.expected_manifest).read_text(encoding="utf-8"))
    evidence = build_installed_wheel_release_evidence_from_audit_files(
        first_audit_path=args.first,
        second_audit_path=args.second,
        fresh_install_target=args.fresh_install_target,
        checkout_root=args.checkout_root,
        expected_manifest=expected_manifest,
    )
    Path(args.output).write_text(json.dumps(evidence.to_dict(), sort_keys=True), encoding="utf-8")
    reloaded = InstalledWheelReleaseEvidence.from_dict(json.loads(Path(args.output).read_text(encoding="utf-8")))
    if reloaded.canonical_sha256 != evidence.canonical_sha256:
        raise SystemExit("installed evidence canonical hash did not round trip")
    print(reloaded.canonical_sha256)
    return 0


def _write_governance_decision(args: argparse.Namespace) -> int:
    path = write_canonical_governance_decision_artifact(
        output_path=args.output,
        application_evidence_path=args.application_evidence,
        installed_evidence_path=args.installed_evidence,
        approval_record_path=args.approval_record,
        previous_ready_decision_path=args.previous_ready_decision,
    )
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    status = payload["decision"]["application_release_status"]
    print(json.dumps({"canonical_sha256": payload["canonical_sha256"], "application_release_status": status}, sort_keys=True))
    return 0 if status in {"internal_source_grounded_ready", "released_internal_source_grounded"} else 4


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m mingli_engine.release_version_workflow")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("inspect-installed-evidence")
    inspect_parser.add_argument("--evidence", required=True)
    inspect_parser.add_argument("--output", required=True)
    inspect_parser.set_defaults(handler=_inspect_installed_evidence)
    decide_parser = subparsers.add_parser("decide-version")
    decide_parser.add_argument("--evidence", required=True)
    decide_parser.add_argument("--owner-version", required=True)
    decide_parser.add_argument("--output", required=True)
    decide_parser.set_defaults(handler=_decide_version)
    update_parser = subparsers.add_parser("update-version-source")
    update_parser.add_argument("--owner-version", required=True)
    update_parser.add_argument("--decision", required=True)
    update_parser.add_argument("--evidence", required=True)
    update_parser.set_defaults(handler=_update_version_source)
    restore_parser = subparsers.add_parser("restore-version-source")
    restore_parser.add_argument("--pyproject", required=True)
    restore_parser.add_argument("--snapshot", required=True)
    restore_parser.set_defaults(handler=_restore_version_source)
    build_parser = subparsers.add_parser("build-installed-evidence")
    build_parser.add_argument("--first", required=True)
    build_parser.add_argument("--second", required=True)
    build_parser.add_argument("--fresh-install-target", required=True)
    build_parser.add_argument("--checkout-root", required=True)
    build_parser.add_argument("--expected-manifest", required=True)
    build_parser.add_argument("--output", required=True)
    build_parser.set_defaults(handler=_build_installed_evidence)
    governance_parser = subparsers.add_parser("write-governance-decision")
    governance_parser.add_argument("--application-evidence", default=None)
    governance_parser.add_argument("--installed-evidence", required=True)
    governance_parser.add_argument("--approval-record", default=None)
    governance_parser.add_argument("--previous-ready-decision", default=None)
    governance_parser.add_argument("--output", required=True)
    governance_parser.set_defaults(handler=_write_governance_decision)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

Future execution sequence for version decisions:

```powershell
$ErrorActionPreference = 'Stop'
$runRoot = Join-Path $env:TEMP ('mingli-release-workflow-' + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $runRoot | Out-Null
function Assert-InspectExitMatchesStatus {
  param(
    [int] $ExitCode,
    [string] $Status,
    [string] $Label
  )
  if (($ExitCode -eq 0) -and ($Status -ne 'internal_source_grounded_ready')) {
    throw "$Label inspect exit code 0 requires internal_source_grounded_ready, got $Status"
  }
  if (($ExitCode -eq 4) -and ($Status -notin @('blocked', 'not_evaluated'))) {
    throw "$Label inspect exit code 4 requires blocked or not_evaluated, got $Status"
  }
}
$pyprojectPath = 'E:\mingli-019-closure\pyproject.toml'
$pyprojectSnapshotPath = Join-Path $runRoot 'pyproject-original-bytes.snapshot'
$versionSourceChanged = $false
$changedVersionReadyVerified = $false
function Invoke-RestoreVersionSource {
  param([string] $Reason)
  python -m mingli_engine.release_version_workflow restore-version-source --pyproject $pyprojectPath --snapshot $pyprojectSnapshotPath
  $restoreExit = $LASTEXITCODE
  if ($restoreExit -ne 0) { throw "restore-version-source failed after $Reason" }
  $snapshotBytes = [System.IO.File]::ReadAllBytes($pyprojectSnapshotPath)
  $restoredBytes = [System.IO.File]::ReadAllBytes($pyprojectPath)
  if (-not [System.Linq.Enumerable]::SequenceEqual([byte[]]$snapshotBytes, [byte[]]$restoredBytes)) {
    throw "restore-version-source byte comparison failed after $Reason"
  }
}
$evidenceInput = Read-Host 'Path to verified final-installed-wheel-evidence.json'
$evidencePath = (Resolve-Path -LiteralPath $evidenceInput).Path
$initialInspectPath = Join-Path $runRoot 'initial-installed-inspect.json'
$decisionPath = Join-Path $runRoot 'release-version-decision.json'
python -m mingli_engine.release_version_workflow inspect-installed-evidence --evidence $evidencePath --output $initialInspectPath
$initialInspectExit = $LASTEXITCODE
if (($initialInspectExit -ne 0) -and ($initialInspectExit -ne 4)) { throw "initial inspect failed with unexpected exit code $initialInspectExit" }
if (-not (Test-Path -LiteralPath $initialInspectPath)) { throw 'initial inspect did not write a new output file' }
$initialInspect = Get-Content -LiteralPath $initialInspectPath -Raw | ConvertFrom-Json
Assert-InspectExitMatchesStatus -ExitCode $initialInspectExit -Status $initialInspect.application_release_status -Label 'initial'
if ($initialInspect.application_release_status -eq 'blocked') {
  Write-Output 'Installed evidence has failed gates; blocked before owner version decision.'
  Write-Output "runRoot=$runRoot"
  Write-Output "initialInspectPath=$initialInspectPath"
  exit 4
}
if ($initialInspect.application_release_status -eq 'not_evaluated') {
  Write-Output 'Installed evidence has not_evaluated gates; current Feature 019 real flow stops before owner version decision.'
  Write-Output "runRoot=$runRoot"
  Write-Output "initialInspectPath=$initialInspectPath"
  exit 4
}
$ownerVersion = Read-Host 'Release owner selected application version'
python -m mingli_engine.release_version_workflow decide-version --evidence $evidencePath --owner-version $ownerVersion --output $decisionPath
if ($LASTEXITCODE -ne 0) { throw 'decide-version failed' }
if (-not (Test-Path -LiteralPath $decisionPath)) { throw 'decide-version did not write a new decision file' }
$decision = Get-Content -LiteralPath $decisionPath | ConvertFrom-Json
try {
if ($decision.can_reuse_current_installed_evidence -eq $true) {
  $finalEvidencePath = Join-Path $runRoot 'current-version-final-installed-wheel-evidence.json'
  Copy-Item -LiteralPath $evidencePath -Destination $finalEvidencePath -ErrorAction Stop
  if (-not (Test-Path -LiteralPath $finalEvidencePath)) { throw 'current-version final evidence copy was not written under runRoot' }
  $versionSourceChanged = $false
} else {
  $versionSourceChanged = $true
  [System.IO.File]::WriteAllBytes($pyprojectSnapshotPath, [System.IO.File]::ReadAllBytes($pyprojectPath))
  if (-not (Test-Path -LiteralPath $pyprojectSnapshotPath)) { throw 'pyproject original-byte snapshot was not written before version source update' }
  python -m mingli_engine.release_version_workflow update-version-source --owner-version $ownerVersion --decision $decisionPath --evidence $evidencePath
  if ($LASTEXITCODE -ne 0) { throw 'update-version-source failed' }
  $expectedManifest = Join-Path $runRoot 'changed-version-expected-manifest.json'
  $expectedScript = Join-Path $runRoot 'write-changed-version-expected-manifest.py'
@'
from pathlib import Path
from mingli_engine.domain_calibration_release import write_expected_release_resource_manifest
print(write_expected_release_resource_manifest(r'E:\mingli-019-closure', Path(r'__EXPECTED_MANIFEST__')))
'@.Replace('__EXPECTED_MANIFEST__', $expectedManifest) | Set-Content -LiteralPath $expectedScript -Encoding UTF8
  python $expectedScript
  if ($LASTEXITCODE -ne 0) { throw 'expected manifest writer failed during changed-version flow' }
  if (-not (Test-Path -LiteralPath $expectedManifest)) { throw 'expected manifest writer did not write its output file' }
  $wheelOut = Join-Path $runRoot 'changed-version-wheel-out'
  New-Item -ItemType Directory -Force -Path $wheelOut | Out-Null
  python -m build --wheel --outdir $wheelOut
  if ($LASTEXITCODE -ne 0) { throw 'changed-version wheel build failed' }
  $wheels = @(Get-ChildItem -LiteralPath $wheelOut -Filter '*.whl')
  if ($wheels.Count -ne 1) { throw "expected exactly one changed-version wheel in $wheelOut, found $($wheels.Count)" }
  $wheel = $wheels[0]
  $venvRoot = Join-Path $runRoot 'changed-version-fresh-venv'
  python -m venv $venvRoot
  if ($LASTEXITCODE -ne 0) { throw 'changed-version venv creation failed' }
  $venvPython = Join-Path $venvRoot 'Scripts\python.exe'
  & $venvPython -m pip install --upgrade pip
  if ($LASTEXITCODE -ne 0) { throw 'changed-version pip upgrade failed' }
  & $venvPython -m pip install $wheel.FullName
  if ($LASTEXITCODE -ne 0) { throw 'changed-version wheel install failed' }
  $firstAudit = Join-Path $runRoot 'changed-version-first-installed-audit.json'
  $secondAudit = Join-Path $runRoot 'changed-version-second-installed-audit.json'
  $finalEvidencePath = Join-Path $runRoot 'changed-version-final-installed-wheel-evidence.json'
  & $venvPython -m mingli_engine.installed_release_audit --checkout-root 'E:\mingli-019-closure' --wheel-path $wheel.FullName > $firstAudit
  if ($LASTEXITCODE -ne 0) { throw 'changed-version first installed audit failed' }
  if (-not (Test-Path -LiteralPath $firstAudit)) { throw 'changed-version first audit did not write its output file' }
  & $venvPython -m mingli_engine.installed_release_audit --checkout-root 'E:\mingli-019-closure' --wheel-path $wheel.FullName > $secondAudit
  if ($LASTEXITCODE -ne 0) { throw 'changed-version second installed audit failed' }
  if (-not (Test-Path -LiteralPath $secondAudit)) { throw 'changed-version second audit did not write its output file' }
  & $venvPython -m mingli_engine.release_version_workflow build-installed-evidence --first $firstAudit --second $secondAudit --fresh-install-target $venvRoot --checkout-root 'E:\mingli-019-closure' --expected-manifest $expectedManifest --output $finalEvidencePath
  if ($LASTEXITCODE -ne 0) { throw 'changed-version installed evidence build failed' }
  if (-not (Test-Path -LiteralPath $finalEvidencePath)) { throw 'changed-version installed evidence builder did not write final evidence' }
}
$finalInspectPath = Join-Path $runRoot 'final-installed-inspect.json'
python -m mingli_engine.release_version_workflow inspect-installed-evidence --evidence $finalEvidencePath --output $finalInspectPath
$finalInspectExit = $LASTEXITCODE
if (($finalInspectExit -ne 0) -and ($finalInspectExit -ne 4)) { throw "final inspect failed with unexpected exit code $finalInspectExit" }
if (-not (Test-Path -LiteralPath $finalInspectPath)) { throw 'final inspect did not write a new output file' }
$finalInspect = Get-Content -LiteralPath $finalInspectPath | ConvertFrom-Json
Assert-InspectExitMatchesStatus -ExitCode $finalInspectExit -Status $finalInspect.application_release_status -Label 'final'
if ($finalInspect.application_release_status -ne 'internal_source_grounded_ready') {
  $nonReadyDecisionPath = Join-Path $runRoot 'canonical-non-ready-governance-decision.json'
  python -m mingli_engine.release_version_workflow write-governance-decision --installed-evidence $finalEvidencePath --output $nonReadyDecisionPath
  $nonReadyWriterExit = $LASTEXITCODE
  if ($nonReadyWriterExit -ne 4) { throw "non-ready governance decision writer returned unexpected exit code $nonReadyWriterExit" }
  if (-not (Test-Path -LiteralPath $nonReadyDecisionPath)) { throw 'non-ready governance decision writer did not write its output file' }
  $nonReadyVerifyScript = Join-Path $runRoot 'verify-non-ready-decision.py'
@'
import json
from mingli_engine.domain_calibration_release import load_canonical_governance_decision
decision = load_canonical_governance_decision(r'__NON_READY_PATH__')
expected = '__EXPECTED_STATUS__'
if decision.application_release_status != expected:
    raise SystemExit(f'non-ready decision status {decision.application_release_status} did not match final inspect {expected}')
print(json.dumps({"status": decision.application_release_status, "canonical_sha256": decision.canonical_sha256}, sort_keys=True))
'@.Replace('__NON_READY_PATH__', $nonReadyDecisionPath).Replace('__EXPECTED_STATUS__', $finalInspect.application_release_status) | Set-Content -LiteralPath $nonReadyVerifyScript -Encoding UTF8
  $nonReadyVerification = (& python $nonReadyVerifyScript) | ConvertFrom-Json
  if ($LASTEXITCODE -ne 0) { throw 'non-ready governance decision loader verification failed' }
  Write-Output "nonReadyDecisionPath=$nonReadyDecisionPath"
  Write-Output ("nonReadyCanonicalHash=" + $nonReadyVerification.canonical_sha256)
  if ($versionSourceChanged) {
    Invoke-RestoreVersionSource -Reason 'changed-version final evidence was not ready'
    Write-Output 'Restored pyproject.toml original bytes through restore-version-source because changed-version final evidence was not ready.'
  }
  exit 4
}
$finalSameVersionDecisionPath = Join-Path $runRoot 'final-same-version-decision.json'
python -m mingli_engine.release_version_workflow decide-version --evidence $finalEvidencePath --owner-version $ownerVersion --output $finalSameVersionDecisionPath
if ($LASTEXITCODE -ne 0) { throw 'final same-version decision failed' }
if (-not (Test-Path -LiteralPath $finalSameVersionDecisionPath)) { throw 'final same-version decision did not write its output file' }
$readyPath = Join-Path $runRoot 'canonical-ready-governance-decision.json'
python -m mingli_engine.release_version_workflow write-governance-decision --installed-evidence $finalEvidencePath --output $readyPath
if ($LASTEXITCODE -ne 0) { throw 'ready governance decision writer failed' }
if (-not (Test-Path -LiteralPath $readyPath)) { throw 'ready governance decision writer did not write its output file' }
$readyVerifyScript = Join-Path $runRoot 'verify-ready-decision.py'
@'
import json
from pathlib import Path
from mingli_engine.domain_calibration_release import load_canonical_governance_decision
decision = load_canonical_governance_decision(r'__READY_PATH__')
assert decision.application_release_status == 'internal_source_grounded_ready'
print(decision.canonical_sha256)
'@.Replace('__READY_PATH__', $readyPath) | Set-Content -LiteralPath $readyVerifyScript -Encoding UTF8
$readyCanonicalHash = (& python $readyVerifyScript)
if ($LASTEXITCODE -ne 0) { throw 'ready governance decision loader verification failed' }
if ($versionSourceChanged) {
  $pyprojectText = [System.IO.File]::ReadAllText($pyprojectPath)
  if ($pyprojectText -notmatch ('(?m)^version = "' + [regex]::Escape($ownerVersion) + '"$')) {
    throw 'pyproject.toml version does not equal release owner selected version after ready verification'
  }
  $changedVersionReadyVerified = $true
}
$approvalRecord = Read-Host 'Path to canonical release-owner approval record, or leave blank'
if ($approvalRecord) {
  $approvalRecordPath = (Resolve-Path -LiteralPath $approvalRecord).Path
  $approvalDecisionPath = Join-Path $runRoot 'canonical-approval-governance-decision.json'
  python -m mingli_engine.release_version_workflow write-governance-decision --installed-evidence $finalEvidencePath --approval-record $approvalRecordPath --previous-ready-decision $readyPath --output $approvalDecisionPath
  $approvalWriterExit = $LASTEXITCODE
  if (($approvalWriterExit -ne 0) -and ($approvalWriterExit -ne 4)) { throw "approval governance decision writer failed with unexpected exit code $approvalWriterExit" }
  if (-not (Test-Path -LiteralPath $approvalDecisionPath)) { throw 'approval governance decision writer did not write its output file' }
  $approvalVerifyScript = Join-Path $runRoot 'verify-approval-decision.py'
@'
import json
from mingli_engine.domain_calibration_release import load_canonical_governance_decision
decision = load_canonical_governance_decision(r'__APPROVAL_DECISION_PATH__')
print(json.dumps({"status": decision.application_release_status, "canonical_sha256": decision.canonical_sha256}, sort_keys=True))
'@.Replace('__APPROVAL_DECISION_PATH__', $approvalDecisionPath) | Set-Content -LiteralPath $approvalVerifyScript -Encoding UTF8
  $approvalVerification = (& python $approvalVerifyScript) | ConvertFrom-Json
  if ($LASTEXITCODE -ne 0) { throw 'approval governance decision loader verification failed' }
  if (($approvalWriterExit -eq 0) -and ($approvalVerification.status -ne 'released_internal_source_grounded')) {
    throw ('approved governance writer exit 0 must reload as released_internal_source_grounded, got ' + $approvalVerification.status)
  }
  if (($approvalWriterExit -eq 4) -and ($approvalVerification.status -ne 'blocked')) {
    throw ('rejected governance writer exit 4 must reload as blocked, got ' + $approvalVerification.status)
  }
  Write-Output "approvalDecisionPath=$approvalDecisionPath"
  Write-Output ("approvalStatus=" + $approvalVerification.status)
  Write-Output ("approvalCanonicalHash=" + $approvalVerification.canonical_sha256)
  if ($approvalWriterExit -eq 4) {
    if ($changedVersionReadyVerified) {
      Write-Output 'Changed-version ready evidence remains verified by version policy, but release governance status is blocked by rejected approval.'
    }
    exit 4
  }
}
Write-Output "runRoot=$runRoot"
Write-Output "finalEvidencePath=$finalEvidencePath"
Write-Output "decisionPath=$decisionPath"
Write-Output "readyDecisionPath=$readyPath"
Write-Output "readyCanonicalHash=$readyCanonicalHash"
if ($versionSourceChanged) {
  Write-Output 'Version source changed: pyproject.toml may be conditionally staged only after this ready decision is verified.'
}
} catch {
  $originalFailure = $_
  if ($versionSourceChanged -and (-not $changedVersionReadyVerified) -and (Test-Path -LiteralPath $pyprojectSnapshotPath)) {
    Invoke-RestoreVersionSource -Reason 'changed-version workflow failure'
    Write-Output 'Restored pyproject.toml original bytes through restore-version-source after changed-version workflow failure.'
  }
  throw $originalFailure
}
```

Expected: with the current four source-governance gates lacking real sources, initial `inspect-installed-evidence` writes `$initialInspectPath`, returns exit code 4, parses as `not_evaluated`, passes the exit-code/status consistency assertion, prints `$runRoot`, and stops before owner version selection. If a later execution has complete passed installed evidence, every artifact is created under `$runRoot`; every native command is checked with `$LASTEXITCODE`; keep-current and changed-version branches both converge on the common ready/released tail; changed-version writes the original `pyproject.toml` bytes to `$pyprojectSnapshotPath` before updating version source; final `blocked` or `not_evaluated` status writes and reloads a canonical non-ready governance decision before stopping with exit code 4; changed-version non-ready and exception paths restore the exact original `pyproject.toml` bytes through the production `restore-version-source` CLI and then stop or rethrow the original failure; approved owner records reload as `released_internal_source_grounded`; rejected owner records return exit code 4, output artifact path/status/hash, reload as canonical `blocked`, and stop the workflow with exit code 4; and no implementation step uses ordinary `build_candidate_version_set` to bypass installed evidence, owner decision, rebuild, or re-audit ordering.

- [ ] **Step 5: Run tests to verify pass**

Run:

```powershell
pytest tests/unit/test_domain_calibration_release.py tests/unit/test_release_version_workflow.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit boundary**

Run:

```powershell
git add src/mingli_engine/domain_calibration_models.py src/mingli_engine/domain_calibration_release.py src/mingli_engine/release_version_workflow.py tests/unit/governance_decision_fixtures.py tests/unit/test_domain_calibration_release.py tests/unit/test_release_version_workflow.py
git commit -m "feat: enforce release state and approval binding"
```

- [ ] **Step 7: Conditional version-source commit boundary**

This step is forbidden in the keep-current branch. Run it only if the release owner selected a different version, `update-version-source` modified `pyproject.toml`, the new final wheel was built from that version source, the new wheel was installed into the fresh checkout-external venv, both installed audits were aggregated, the final installed evidence reloaded successfully, and the common ready decision tail produced `internal_source_grounded_ready`. The release workflow already restored the exact original `pyproject.toml` bytes for any changed-version exception, `blocked`, or `not_evaluated` path before stopping.

Run:

```powershell
$pyprojectPath = 'E:\mingli-019-closure\pyproject.toml'
$pyprojectText = [System.IO.File]::ReadAllText($pyprojectPath)
if ($pyprojectText -notmatch ('(?m)^version = "' + [regex]::Escape($ownerVersion) + '"$')) {
  throw 'pyproject.toml version does not equal release owner selected version; do not stage'
}
git add pyproject.toml
git commit -m "chore: set release owner selected application version"
```

Expected: the commit contains only the owner-selected version-source update. If changed-version final evidence fails, is `blocked`, or is `not_evaluated`, the workflow has already restored the original bytes and these commands are not run. Do not use destructive Git commands for version-source restoration.

---

### Task 6: Historical Calibration Immutability

**Files:**
- Modify: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_maturity.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_domain_calibration_maturity.py`

- [ ] **Step 1: Write failing immutability test**

Append to `tests\unit\test_domain_calibration_maturity.py`:

```python
from hashlib import sha256
from pathlib import Path

from mingli_engine.domain_calibration_maturity import build_historical_failure_evidence


def _file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    return sha256(path.read_bytes()).hexdigest()


def test_historical_calibration_failure_evidence_is_immutable() -> None:
    root = Path(__file__).resolve().parents[2]
    data = root / "src" / "mingli_engine" / "data" / "domain_calibration"
    historical_paths = (
        data / "calibration_cases.json",
        data / "calibration_assertions.json",
        data / "calibration_citations.json",
        data / "reviewer_a_assignments.json",
        data / "reviewer_a_reviews.json",
        data / "reviewer_b_assignments.json",
        data / "reviewer_b_reviews.json",
        data / "reviewer_packets.json",
        data / "adjudication.json",
        data / "input_fixtures.json",
        data / "calibration_baseline.json",
    )
    approved_hashes = {
        "calibration_cases.json": "390b24702fdc6ab6360ec2728e1d561eb73143eb007e8fd609a16de0417b8b39",
        "calibration_assertions.json": "52c69f1e1b8237afbf5a47716a86dda97f13bff988900968983a76c8851742f9",
        "calibration_citations.json": "886183783ff78714c06cfad780d531c68ba4d54cdcf83a9d9d3d631ae8fee66b",
        "reviewer_a_assignments.json": "aa0117cfc3a3f271a0212b722de89e7a0f16d9eabf88ce23a46d0ed7eec1e6ff",
        "reviewer_a_reviews.json": "347e01b9ac1f0e22dbe3c5620b364e89e20fda31d3a29522be715680cd5a71be",
        "reviewer_b_assignments.json": "9b4fbb5149cae5e6fdf8ce4fda0d3772cb36dfec4cbecfe5518bf72d69e8ce89",
        "reviewer_b_reviews.json": "48a2c82eacfc8b48ad0a7fedf330d019597f9d588e7c36075b0be8b1716ef035",
        "reviewer_packets.json": "1418a4a5289a9048a5cf90f8c4123e6cad79dcdf965c896becd0e275f06fbd3d",
        "adjudication.json": "0c573dcc6441eb647cdcc56f50798f4b438cc2f6994fdb8012989770933fa817",
        "input_fixtures.json": "627aafee4c7f3216f098de98d2396703f707dcb16a41bf399b9d6415e52b21a8",
    }
    before = {path: _file_hash(path) for path in historical_paths}

    evidence = build_historical_failure_evidence()

    after = {path: _file_hash(path) for path in historical_paths}
    assert after == before
    assert {path.name: digest for path, digest in after.items() if path.name != "calibration_baseline.json"} == approved_hashes
    assert after[data / "calibration_baseline.json"] is None
    assert evidence.release_status == "blocked"
    assert evidence.reviewer_raw_agreement == 0.6744186046511628
    assert evidence.adjudicated_engine_match == 0.4418604651162791
    assert evidence.safety_critical_exact_match == 1.0
    assert evidence.reviewer_disagreement_count == 14
    assert evidence.engine_mismatch_count == 24
    assert evidence.overlap_count == 9
    assert evidence.reviewer_threshold == 0.70
    assert evidence.engine_threshold == 0.90
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
pytest tests/unit/test_domain_calibration_maturity.py::test_historical_calibration_failure_evidence_is_immutable -q
```

Expected: FAIL because historical evidence builder is missing.

- [ ] **Step 3: Implement historical evidence builder**

Add to `src\mingli_engine\domain_calibration_maturity.py`:

```python
@dataclass(frozen=True)
class HistoricalFailureEvidence:
    release_status: str
    reviewer_raw_agreement: float
    adjudicated_engine_match: float
    safety_critical_exact_match: float
    reviewer_disagreement_count: int
    engine_mismatch_count: int
    overlap_count: int
    reviewer_threshold: float
    engine_threshold: float


def build_historical_failure_evidence() -> HistoricalFailureEvidence:
    from mingli_engine.domain_calibration import (
        _load_packaged,
        build_candidate_metric_snapshot,
        build_candidate_version_set,
        execute_candidate_calibration,
    )
    from mingli_engine.domain_calibration_models import CalibrationReview

    version_set = build_candidate_version_set("0.2.0")
    result = execute_candidate_calibration(version_set)
    repeated = execute_candidate_calibration(version_set)
    snapshot = build_candidate_metric_snapshot(result, repeated)
    reviewer_a = {record.assertion_id: record.label for record in _load_packaged("reviewer_a_reviews.json", CalibrationReview).records}
    reviewer_b = {record.assertion_id: record.label for record in _load_packaged("reviewer_b_reviews.json", CalibrationReview).records}
    reviewer_disagreement_ids = {
        assertion_id
        for assertion_id, label in reviewer_a.items()
        if assertion_id in reviewer_b and reviewer_b[assertion_id] != label
    }
    engine_mismatch_ids = {
        assertion_result.assertion_id
        for assertion_result in result.assertion_results
        if not assertion_result.matched
    }
    reviewer_disagreement_count = len(reviewer_disagreement_ids)
    engine_mismatch_count = len(engine_mismatch_ids)
    overlap_count = len(reviewer_disagreement_ids & engine_mismatch_ids)
    return HistoricalFailureEvidence(
        release_status="blocked",
        reviewer_raw_agreement=snapshot.reviewer_raw_agreement,
        adjudicated_engine_match=snapshot.adjudicated_engine_match,
        safety_critical_exact_match=snapshot.safety_critical_exact_match,
        reviewer_disagreement_count=reviewer_disagreement_count,
        engine_mismatch_count=engine_mismatch_count,
        overlap_count=overlap_count,
        reviewer_threshold=0.70,
        engine_threshold=0.90,
    )
```

- [ ] **Step 4: Run test to verify pass**

Run:

```powershell
pytest tests/unit/test_domain_calibration_maturity.py::test_historical_calibration_failure_evidence_is_immutable -q
```

Expected: PASS. If `calibration_baseline.json` is absent, the before and after hash value remains `None`; if it exists, the original hash is unchanged.

- [ ] **Step 5: Commit boundary**

Run:

```powershell
git add src/mingli_engine/domain_calibration_maturity.py tests/unit/test_domain_calibration_maturity.py
git commit -m "test: preserve historical calibration evidence"
```

---

### Task 7: Outputs, Packaged Documentation, And Final Scans

**Files:**
- Modify: `E:\mingli-019-closure\src\mingli_engine\domain_calibration_release.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\application_reports.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\markdown.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\html.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\report_release.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\cli.py`
- Modify: `E:\mingli-019-closure\src\mingli_engine\project_completion.py`
- Modify: `E:\mingli-019-closure\tests\unit\governance_decision_fixtures.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_domain_calibration_release.py`
- Create: `E:\mingli-019-closure\tests\unit\test_application_reports.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_report_release.py`
- Modify: `E:\mingli-019-closure\tests\unit\test_project_completion.py`
- Modify: `E:\mingli-019-closure\tests\contract\test_report_release_cli_contract.py`
- Create: `E:\mingli-019-closure\tests\integration\test_packaged_release_docs.py`

- [ ] **Step 1: Write failing output tests**

Modify the Task 4-created `tests\unit\governance_decision_fixtures.py` by appending the governance decision helper below. Do not create the file a second time; the final file contains the Task 4 `write_structurally_valid_installed_evidence_fixture()` and `write_not_evaluated_installed_evidence_fixture()` helpers plus this appended helper:

```python
import json
from pathlib import Path

from mingli_engine.application_validation import (
    RawAbstentionResult,
    RawDeterminismResult,
    RawPackagingResult,
    RawPrivacyResult,
    RawReproducibilityResult,
    RawSafetyResult,
    RawSchoolConflictResult,
    RawTraceResult,
    RawUnsupportedInferenceResult,
    RawVersionBindingResult,
    produce_abstention_gate,
    produce_deterministic_gate,
    produce_packaging_gate,
    produce_privacy_gate,
    produce_reproducibility_gate,
    produce_safety_gate,
    produce_school_conflict_gate,
    produce_trace_gate,
    produce_unsupported_inference_gate,
    produce_version_binding_gate,
)
from mingli_engine.domain_calibration import build_release_version_set
from mingli_engine.domain_calibration_models import APPLICATION_GATE_IDS, ApplicationEvidenceBundle, governance_canonical_sha256
from mingli_engine.domain_calibration_release import (
    CLAIM_BOUNDARY_HASH,
    RELEASE_STATEMENT,
    build_installed_wheel_release_evidence_from_audit_files,
    write_canonical_governance_decision_artifact,
)


def write_structurally_valid_governance_decision_fixture(tmp_path: Path) -> Path:
    manifest = {
        "data/calculation/school_profiles.json": "a" * 64,
        "data/calculation/strength_weights.json": "b" * 64,
        "data/release_docs/source_grounded_internal_release.md": "c" * 64,
        "data/release_docs/internal_release_notes.md": "d" * 64,
    }
    version_set = build_release_version_set("0.1.0")
    raw_by_gate = {
        "deterministic_calculation": RawDeterminismResult("1" * 64, "1" * 64, {"stages_present": "passed", "placeholder_integrity": "passed"}),
        "source_rule_tracing": RawTraceResult(
            emitted_claim_ids=("claim-1",),
            traced_claim_ids=("claim-1",),
            emitted_rule_ids=("rule-1",),
            traced_rule_ids=("rule-1",),
        ),
        "unsupported_inference": RawUnsupportedInferenceResult(
            computed_claim_ids=("claim-1",),
            supported_claim_ids=("claim-1",),
            dependency_bypass_ids=(),
        ),
        "school_conflict": RawSchoolConflictResult(
            conflict_case_ids=("conflict-1",),
            recalled_conflict_case_ids=("conflict-1",),
            silent_collapse_case_ids=(),
        ),
        "abstention": RawAbstentionResult(
            required_abstention_case_ids=("abstain-1",),
            observed_abstention_case_ids=("abstain-1",),
        ),
        "safety_critical": RawSafetyResult(safety_case_count=1, exact_match_count=1, prohibited_output_count=0),
        "privacy": RawPrivacyResult(scenario_count=1, privacy_failed_scenarios=(), write_count=0, leak_count=0),
        "packaging": RawPackagingResult(manifest, tuple(sorted(manifest)), True, "0.1.0"),
        "version_binding": RawVersionBindingResult("mingli-engine", "0.1.0", "0.1.0", version_set),
    }
    pre_gates = {
        "deterministic_calculation": produce_deterministic_gate(raw_by_gate["deterministic_calculation"]),
        "source_rule_tracing": produce_trace_gate(raw_by_gate["source_rule_tracing"]),
        "unsupported_inference": produce_unsupported_inference_gate(raw_by_gate["unsupported_inference"]),
        "school_conflict": produce_school_conflict_gate(raw_by_gate["school_conflict"]),
        "abstention": produce_abstention_gate(raw_by_gate["abstention"]),
        "safety_critical": produce_safety_gate(raw_by_gate["safety_critical"]),
        "privacy": produce_privacy_gate(raw_by_gate["privacy"]),
        "packaging": produce_packaging_gate(raw_by_gate["packaging"]),
        "version_binding": produce_version_binding_gate(raw_by_gate["version_binding"]),
    }
    audit_payload = {
        "package_identity": "mingli-engine",
        "distribution_version": "0.1.0",
        "application_version": "0.1.0",
        "exact_version_set": version_set.__dict__,
        "resource_manifest_sha256": manifest,
        "wheel_resource_manifest_sha256": manifest,
        "pre_reproducibility_gate_evidence": {
            gate_id: {"raw_payload": gate.raw_payload, "evidence": gate.to_dict()}
            for gate_id, gate in pre_gates.items()
        },
        "release_statement": RELEASE_STATEMENT,
        "claim_boundary_hash": CLAIM_BOUNDARY_HASH,
        "wheel_filename": "mingli_engine-0.1.0-py3-none-any.whl",
        "wheel_sha256": "e" * 64,
        "environment": {"python": "3.12", "platform": "test", "dependencies": {"mingli-engine": "0.1.0"}},
        "source_isolated": True,
        "mingli_engine_file": str(tmp_path / "venv" / "Lib" / "site-packages" / "mingli_engine" / "__init__.py"),
    }
    audit_hash = governance_canonical_sha256(audit_payload)
    reproducibility = produce_reproducibility_gate(
        RawReproducibilityResult(first_payload_hash=audit_hash, second_payload_hash=audit_hash, executed_from_installed_package=True)
    )
    application_bundle = ApplicationEvidenceBundle.from_gate_evidence(
        tuple(pre_gates[gate_id] if gate_id != "reproducibility" else reproducibility for gate_id in APPLICATION_GATE_IDS)
    )
    application_evidence_path = tmp_path / "application-evidence.json"
    application_evidence_path.write_text(json.dumps(application_bundle.to_dict(), sort_keys=True), encoding="utf-8")
    first_audit = tmp_path / "first-installed-audit.json"
    second_audit = tmp_path / "second-installed-audit.json"
    first_audit.write_text(json.dumps(audit_payload, sort_keys=True), encoding="utf-8")
    second_audit.write_text(json.dumps(audit_payload, sort_keys=True), encoding="utf-8")
    installed = build_installed_wheel_release_evidence_from_audit_files(
        first_audit_path=first_audit,
        second_audit_path=second_audit,
        fresh_install_target=tmp_path / "venv",
        checkout_root=tmp_path / "checkout",
        expected_manifest=manifest,
    )
    installed_evidence_path = tmp_path / "installed-evidence.json"
    installed_evidence_path.write_text(json.dumps(installed.to_dict(), sort_keys=True), encoding="utf-8")
    return write_canonical_governance_decision_artifact(
        output_path=tmp_path / "canonical-governance-decision.json",
        application_evidence_path=application_evidence_path,
        installed_evidence_path=installed_evidence_path,
    )
```

Append to `tests\unit\test_domain_calibration_release.py`:

```python
from mingli_engine.domain_calibration_release import ABSTENTION_POLICY, CLAIM_BOUNDARY_HASH, LIMITATIONS, RELEASE_STATEMENT, build_domain_calibration_summary
from tests.unit.governance_decision_fixtures import write_structurally_valid_governance_decision_fixture


def test_python_api_summary_exposes_source_grounded_governance_fields(tmp_path) -> None:
    summary = build_domain_calibration_summary(governance_decision_path=write_structurally_valid_governance_decision_fixture(tmp_path))

    assert summary.release_id == "domain_calibration_v1"
    assert summary.release_status == "blocked"
    assert summary.application_version == "0.2.0"
    assert summary.metrics["reviewer_raw_agreement"] == 0.6744186046511628
    assert summary.version_set
    assert summary.resource_sha256
    assert summary.application_release_status == "internal_source_grounded_ready"
    assert summary.evidence_maturity_status == "not_assessed"
    assert summary.evidence_maturity_scope_records[0]["conclusion_status"] == "not_assessed"
    assert summary.release_statement == RELEASE_STATEMENT
    assert summary.limitations == LIMITATIONS
    assert summary.abstention_policy == ABSTENTION_POLICY
    assert summary.release_claim_boundary_hash == CLAIM_BOUNDARY_HASH
    assert summary.application_evidence_hash
    assert summary.installed_wheel_evidence_hash
    assert summary.package_identity == "mingli-engine"
    assert summary.distribution_version == "0.1.0"
    assert summary.governance_application_version == "0.1.0"
```

Append to `tests\unit\test_application_reports.py`:

```python
import json
from datetime import datetime
from pathlib import Path

from mingli_engine.bazi import analyze_bazi_chart
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.domain_calibration_release import ABSTENTION_POLICY, CLAIM_BOUNDARY_HASH, RELEASE_STATEMENT, build_domain_calibration_summary
from mingli_engine.html import render_html_report
from mingli_engine.markdown import render_markdown_report
from mingli_engine.report_inputs import birth_profile_from_dict
from mingli_engine.report_schema import build_report
from tests.unit.governance_decision_fixtures import write_structurally_valid_governance_decision_fixture


def _real_report():
    payload = json.loads(Path("examples/birth-profile.auto-gregorian.json").read_text(encoding="utf-8"))
    profile = birth_profile_from_dict(payload)
    chart = calculate_bazi_chart(profile)
    birth_datetime = datetime.strptime(f"{profile.birth_date} {profile.birth_time}", "%Y-%m-%d %H:%M")
    calculation = analyze_bazi_chart(chart, birth_datetime=birth_datetime)
    return build_report(chart, calculation)


def test_markdown_and_html_governance_sections_include_claim_boundary(tmp_path) -> None:
    summary = build_domain_calibration_summary(governance_decision_path=write_structurally_valid_governance_decision_fixture(tmp_path))
    report = _real_report()
    markdown = render_markdown_report(report, governance_summary=summary)
    html = render_html_report(report, governance_summary=summary)

    assert report.title in markdown
    assert report.disclaimer in markdown
    assert RELEASE_STATEMENT in markdown
    assert ABSTENTION_POLICY in markdown
    assert CLAIM_BOUNDARY_HASH in markdown
    assert "source-grounded-maturity-policy-v1" in markdown
    assert "mingli-engine" in markdown
    assert "Governance application version" in markdown
    assert "0.1.0" in markdown
    assert summary.application_evidence_hash in markdown
    assert summary.installed_wheel_evidence_hash in markdown
    assert "Feature 020" in markdown
    assert report.title in html
    assert report.disclaimer in html
    assert RELEASE_STATEMENT in html
    assert ABSTENTION_POLICY in html
    assert CLAIM_BOUNDARY_HASH in html
    assert "source-grounded-maturity-policy-v1" in html
    assert "mingli-engine" in html
    assert "Governance application version" in html
    assert "0.1.0" in html
    assert summary.application_evidence_hash in html
    assert summary.installed_wheel_evidence_hash in html
```

Append to `tests\unit\test_report_release.py`:

```python
from mingli_engine.report_release import build_report_release_summary
from tests.unit.governance_decision_fixtures import write_structurally_valid_governance_decision_fixture


def test_report_release_summary_includes_source_grounded_governance(tmp_path, monkeypatch):
    monkeypatch.setenv("MINGLI_CANONICAL_GOVERNANCE_DECISION", str(write_structurally_valid_governance_decision_fixture(tmp_path)))
    summary = build_report_release_summary()

    assert summary.source_grounded_application_release_status
    assert summary.source_grounded_evidence_maturity_scope_records[0]["conclusion_status"] == "not_assessed"
    assert summary.source_grounded_release_statement
    assert summary.source_grounded_abstention_policy
    assert summary.source_grounded_application_evidence_hash
    assert summary.source_grounded_installed_wheel_evidence_hash
    assert summary.source_grounded_package_identity == "mingli-engine"
    assert summary.source_grounded_distribution_version == "0.1.0"
    assert summary.source_grounded_application_version == "0.1.0"
```

Append to `tests\unit\test_project_completion.py`:

```python
from mingli_engine.project_completion import build_project_completion_summary
from tests.unit.governance_decision_fixtures import write_structurally_valid_governance_decision_fixture


def test_project_completion_summary_includes_source_grounded_governance(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("MINGLI_CANONICAL_GOVERNANCE_DECISION", str(write_structurally_valid_governance_decision_fixture(tmp_path)))
    summary = build_project_completion_summary()

    assert summary.source_grounded_application_release_status
    assert summary.source_grounded_evidence_maturity_scope_records[0]["conclusion_status"] == "not_assessed"
    assert summary.source_grounded_release_statement
    assert summary.source_grounded_abstention_policy
    assert summary.source_grounded_application_evidence_hash
    assert summary.source_grounded_installed_wheel_evidence_hash
    assert summary.source_grounded_package_identity == "mingli-engine"
    assert summary.source_grounded_distribution_version == "0.1.0"
    assert summary.source_grounded_application_version == "0.1.0"
```

Append to `tests\contract\test_report_release_cli_contract.py`:

```python
import json

from mingli_engine import cli
from tests.unit.governance_decision_fixtures import write_structurally_valid_governance_decision_fixture


def test_domain_calibration_summary_cli_outputs_governance_fields(capsys, tmp_path) -> None:
    decision_path = write_structurally_valid_governance_decision_fixture(tmp_path)
    exit_code = cli.main(["domain-calibration-summary", "--governance-decision", str(decision_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code in {0, 4}
    assert payload["application_release_status"]
    assert payload["evidence_maturity_status"]
    assert payload["evidence_maturity_scope_records"][0]["conclusion_status"] == "not_assessed"
    assert payload["release_statement"]
    assert payload["limitations"]
    assert payload["abstention_policy"]
    assert payload["application_evidence_hash"]
    assert payload["installed_wheel_evidence_hash"]
    assert payload["package_identity"] == "mingli-engine"
    assert payload["distribution_version"] == "0.1.0"
    assert payload["application_version"] == "0.2.0"
    assert payload["governance_application_version"] == "0.1.0"
```

Create `tests\integration\test_packaged_release_docs.py`:

```python
import json
import os
import subprocess
from pathlib import Path


def test_packaged_release_docs_are_loaded_from_installed_wheel_python() -> None:
    installed_python = os.environ.get("MINGLI_INSTALLED_PYTHON")
    assert installed_python, "MINGLI_INSTALLED_PYTHON must point to the final-wheel venv Python"
    checkout_root = Path(__file__).resolve().parents[2]
    script = """
import json
from importlib import resources
from pathlib import Path
import mingli_engine
root = resources.files('mingli_engine')
docs = {
  'source': root.joinpath('data', 'release_docs', 'source_grounded_internal_release.md').read_text(encoding='utf-8'),
  'notes': root.joinpath('data', 'release_docs', 'internal_release_notes.md').read_text(encoding='utf-8'),
}
print(json.dumps({'file': str(Path(mingli_engine.__file__).resolve()), 'docs': docs}, sort_keys=True))
"""
    output = subprocess.check_output([installed_python, "-c", script], text=True, cwd=os.environ.get("TEMP", str(checkout_root.parent)))
    payload = json.loads(output)

    assert not Path(payload["file"]).resolve().is_relative_to(checkout_root)
    assert "Internal source-grounded application release candidate" in payload["docs"]["source"]
    assert "abstain" in payload["docs"]["notes"].lower()
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
$ErrorActionPreference = 'Stop'
$wheelOut = Join-Path $env:TEMP ('mingli-task7-red-wheel-' + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $wheelOut | Out-Null
python -m build --wheel --outdir $wheelOut
if ($LASTEXITCODE -ne 0) { throw 'Task 7 red wheel build failed before output tests' }
$wheels = @(Get-ChildItem -LiteralPath $wheelOut -Filter '*.whl')
if ($wheels.Count -ne 1) { throw "expected exactly one Task 7 red wheel in $wheelOut, found $($wheels.Count)" }
$wheel = $wheels[0]
$venvRoot = Join-Path $env:TEMP ('mingli-output-wheel-venv-' + [guid]::NewGuid().ToString())
python -m venv $venvRoot
if ($LASTEXITCODE -ne 0) { throw 'Task 7 red venv creation failed' }
$env:MINGLI_INSTALLED_PYTHON = Join-Path $venvRoot 'Scripts\python.exe'
& $env:MINGLI_INSTALLED_PYTHON -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'Task 7 red pip upgrade failed' }
& $env:MINGLI_INSTALLED_PYTHON -m pip install $wheel.FullName
if ($LASTEXITCODE -ne 0) { throw 'Task 7 red wheel install failed' }
pytest tests/unit/test_domain_calibration_release.py tests/unit/test_application_reports.py tests/unit/test_report_release.py tests/unit/test_project_completion.py tests/contract/test_report_release_cli_contract.py tests/integration/test_packaged_release_docs.py -q
if ($LASTEXITCODE -eq 0) { throw 'expected Task 7 output tests to fail before output wiring' }
```

Expected: FAIL because outputs are not wired yet; the packaged-doc test must not skip and must use the checkout-external venv Python.

- [ ] **Step 3: Implement summary builder and output renderers**

Update `build_domain_calibration_summary()` in `src\mingli_engine\domain_calibration_release.py` as a compatible API extension. Preserve the existing release ID, real `decision.release_status`, metrics, version set, resource hashes, and blockers; read governance fields from a verified canonical `ReleaseGovernanceDecision` supplied by the caller:

```python
def build_domain_calibration_summary(
    *,
    packaging: PackagingVerification | None = None,
    application_contract_status: str | None = None,
    privacy_status: str | None = None,
    documentation_status: str = "passed",
    compatibility_status: str = "passed",
    baseline: MetricSnapshotV1 | None = None,
    governance_decision_path: str | Path | None = None,
) -> DomainCalibrationReleaseSummary:
    packaging_result = packaging or build_packaging_verification()
    version_set = build_candidate_version_set("0.2.0")
    run = execute_candidate_calibration(version_set)
    repeated = execute_candidate_calibration(version_set)
    snapshot = build_candidate_metric_snapshot(run, repeated, baseline=baseline)
    resolved_application = application_contract_status
    resolved_privacy = privacy_status
    if resolved_application is None or resolved_privacy is None:
        verification = build_application_verification()
        verification_status = "passed" if verification.overall_status == "verified" else "failed"
        if resolved_application is None:
            resolved_application = verification_status
        if resolved_privacy is None:
            resolved_privacy = verification_status
    decision = build_domain_calibration_release_decision(
        snapshot=snapshot,
        baseline=baseline,
        packaging=packaging_result,
        application_contract_status=resolved_application,
        privacy_status=resolved_privacy,
        documentation_status=documentation_status,
        compatibility_status=compatibility_status,
    )
    governance_decision = load_canonical_governance_decision(governance_decision_path) if governance_decision_path else None
    return DomainCalibrationReleaseSummary(
        release_id="domain_calibration_v1",
        release_status=decision.release_status,
        application_version=decision.version_set.application_version,
        installed_distribution_version=packaging_result.distribution_version,
        claim_boundary=decision.claim_boundary,
        checks=dict(decision.checks),
        blockers=list(decision.blockers),
        metrics=_metric_payload(snapshot),
        version_set=asdict(decision.version_set),
        resource_sha256=dict(packaging_result.asset_sha256),
        source_isolated=packaging_result.source_isolated,
        next_action=decision.next_action,
        application_release_status=governance_decision.application_release_status if governance_decision else "not_evaluated",
        evidence_maturity_status="not_assessed",
        evidence_maturity_scope_records=(
            {
                "conclusion_status": "not_assessed",
                "assessment_policy_version": "source-grounded-maturity-policy-v1",
                "layer": "L0",
                "school": "ziping",
                "rule_family": "release_governance",
                "source_scope": "internal-source-grounded-release-v1",
                "coverage": 0.0,
                "contested": False,
                "observation_ids": (),
                "evidence_ids": (),
                "limitations": ("expert coverage has not been observed",),
            },
        ),
        assessment_policy_version="source-grounded-maturity-policy-v1",
        release_statement=RELEASE_STATEMENT,
        limitations=LIMITATIONS,
        abstention_policy=ABSTENTION_POLICY,
        release_claim_boundary_hash=CLAIM_BOUNDARY_HASH,
        application_evidence_hash=governance_decision.application_evidence_hash if governance_decision else "",
        installed_wheel_evidence_hash=governance_decision.installed_wheel_evidence_hash if governance_decision else "",
        package_identity=governance_decision.package_identity if governance_decision else "",
        distribution_version=governance_decision.distribution_version if governance_decision else "",
        governance_application_version=governance_decision.application_version if governance_decision else "",
    )
```

Update `src\mingli_engine\cli.py` in the existing `_domain_calibration_summary(args)` function and existing `_build_parser()` registration. Do not add an uncalled parser helper:

```python
def _domain_calibration_summary(args: argparse.Namespace) -> int:
    summary = build_domain_calibration_summary(governance_decision_path=args.governance_decision)
    _write_json(summary)
    return 4 if summary.release_status == "blocked" else 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mingli-engine")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate-intake")
    validate_parser.add_argument("--input", required=True, type=Path)
    validate_parser.set_defaults(handler=_validate_intake)
    safety_parser = subparsers.add_parser("safety-check")
    safety_parser.add_argument("--input", required=True, type=Path)
    safety_parser.set_defaults(handler=_safety_check)
    calculate_parser = subparsers.add_parser("calculate-chart")
    calculate_parser.add_argument("--input", required=True, type=Path)
    calculate_parser.add_argument("--analysis", action="store_true")
    calculate_parser.set_defaults(handler=_calculate_chart)
    calculated_report_parser = subparsers.add_parser("calculate-report")
    calculated_report_parser.add_argument("--input", required=True, type=Path)
    calculated_report_parser.add_argument("--format", choices=["markdown", "html"], required=True)
    calculated_report_parser.add_argument("--analysis", action="store_true")
    calculated_report_parser.set_defaults(handler=_calculate_report)
    report_parser = subparsers.add_parser("generate-report")
    report_parser.add_argument("--input", required=True, type=Path)
    report_parser.add_argument("--format", choices=["markdown", "html"], required=True)
    report_parser.set_defaults(handler=_generate_report)
    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("--batch", required=True)
    promote_parser.add_argument("--overrides", required=True, type=Path)
    promote_parser.add_argument("--curation-batch", default="")
    promote_parser.add_argument("--intake-dir", default=None)
    promote_parser.add_argument("--corpus-dir", default=None)
    promote_parser.add_argument("--apply", action="store_true")
    promote_parser.set_defaults(handler=_promote)
    activation_parser = subparsers.add_parser("knowledge-activation-summary")
    activation_parser.add_argument("--corpus-dir", default=None)
    activation_parser.set_defaults(handler=_knowledge_activation_summary)
    acceptance_parser = subparsers.add_parser("report-acceptance-summary")
    acceptance_parser.set_defaults(handler=_report_acceptance_summary)
    release_parser = subparsers.add_parser("report-release-summary")
    release_parser.set_defaults(handler=_report_release_summary)
    domain_calibration_parser = subparsers.add_parser("domain-calibration-summary")
    domain_calibration_parser.add_argument("--governance-decision", default=None, type=Path)
    domain_calibration_parser.set_defaults(handler=_domain_calibration_summary)
    completion_parser = subparsers.add_parser("project-completion-summary")
    completion_parser.set_defaults(handler=_project_completion_summary)
    real_use_parser = subparsers.add_parser("real-use")
    real_use_parser.add_argument("--input", required=True, type=Path)
    real_use_parser.set_defaults(handler=_real_use)
    return parser
```

Add to `src\mingli_engine\application_reports.py`:

```python
from html import escape

from mingli_engine.models import DomainCalibrationReleaseSummary, Report


def render_source_grounded_governance_markdown(summary: DomainCalibrationReleaseSummary) -> str:
    limitation_lines = "\n".join(f"- {item}" for item in summary.limitations)
    scope_lines = "\n".join(
        f"- {record['layer']} / {record['school']} / {record['rule_family']}: {record['conclusion_status']} ({record['assessment_policy_version']})"
        for record in summary.evidence_maturity_scope_records
    )
    return (
        "## Source-Grounded Internal Release Governance\n\n"
        f"Application release status: {summary.application_release_status}\n\n"
        f"Evidence maturity status: {summary.evidence_maturity_status}\n\n"
        f"Structured maturity scope records:\n{scope_lines}\n\n"
        f"Release statement: {summary.release_statement}\n\n"
        f"Claim boundary hash: {summary.release_claim_boundary_hash}\n\n"
        f"Application evidence hash: {summary.application_evidence_hash}\n\n"
        f"Installed evidence hash: {summary.installed_wheel_evidence_hash}\n\n"
        f"Package identity: {summary.package_identity}\n\n"
        f"Distribution version: {summary.distribution_version}\n\n"
        f"Governance application version: {summary.governance_application_version}\n\n"
        f"Limitations:\n{limitation_lines}\n\n"
        f"Abstention policy: {summary.abstention_policy}\n"
    )


def render_source_grounded_governance_html(summary: DomainCalibrationReleaseSummary) -> str:
    limitations = "".join(f"<li>{escape(item)}</li>" for item in summary.limitations)
    scope_records = "".join(
        f"<li>{escape(str(record['layer']))} / {escape(str(record['school']))} / {escape(str(record['rule_family']))}: {escape(str(record['conclusion_status']))} ({escape(str(record['assessment_policy_version']))})</li>"
        for record in summary.evidence_maturity_scope_records
    )
    return (
        '<section id="source-grounded-internal-release-governance">'
        "<h2>Source-Grounded Internal Release Governance</h2>"
        f"<p>Application release status: {escape(summary.application_release_status)}</p>"
        f"<p>Evidence maturity status: {escape(summary.evidence_maturity_status)}</p>"
        f"<ul>{scope_records}</ul>"
        f"<p>Release statement: {escape(summary.release_statement)}</p>"
        f"<p>Claim boundary hash: {escape(summary.release_claim_boundary_hash)}</p>"
        f"<p>Application evidence hash: {escape(summary.application_evidence_hash)}</p>"
        f"<p>Installed evidence hash: {escape(summary.installed_wheel_evidence_hash)}</p>"
        f"<p>Package identity: {escape(summary.package_identity)}</p>"
        f"<p>Distribution version: {escape(summary.distribution_version)}</p>"
        f"<p>Governance application version: {escape(summary.governance_application_version)}</p>"
        f"<ul>{limitations}</ul>"
        f"<p>Abstention policy: {escape(summary.abstention_policy)}</p>"
        "</section>"
    )
```

Update real renderers so final report output can carry governance while preserving every existing section and current output order. Add the imports, add the optional `governance_summary` parameter, and append governance content immediately before the current return; do not remove or reorder existing sections.

```python
# src/mingli_engine/markdown.py
from mingli_engine.application_reports import render_source_grounded_governance_markdown
from mingli_engine.models import DomainCalibrationReleaseSummary


def render_markdown_report(
    report: Report,
    *,
    governance_summary: DomainCalibrationReleaseSummary | None = None,
) -> str:
    has_reasoned_analysis = _has_reasoned_analysis(report)
    render_text = _markdown_text if has_reasoned_analysis else lambda value: value
    sections = [
        f"# {render_text(report.title)}",
        "## 免责声明",
        render_text(report.disclaimer),
        "## 快速导读",
        render_text(report.quick_guide),
        "## 第一层：基础资料",
        "### 命造卡片",
        render_text(report.chart_card),
        "### 排盘来源与假设",
        render_text(report.assumptions),
        "## 第二层：结构观察",
        "### 四柱与五行摘要",
        render_text(report.four_pillars_summary),
        render_text(report.five_elements_summary),
        "### 十神摘要",
        render_text(report.ten_gods_summary),
        "### 观察依据",
        render_text(report.evidence_notes),
        "### 正式知识综合",
        render_text(report.formal_synthesis),
        "### 综合脉络",
        render_text(report.integrated_synthesis),
        "### 结构分析",
        render_text(report.structure_analysis),
        "### 性格倾向",
        render_text(report.personality_tendencies),
        "## 第三层：解读边界",
        render_text(report.interpretation_boundaries),
        "## 第四层：行动反思",
        "### 优势与议题",
        render_text(report.strengths_and_issues),
        "### 阶段概览",
        render_text(report.phase_overview),
        "### 行动建议",
        render_text(report.action_suggestions),
        "## 术语简注",
        render_text(report.glossary),
        "## 伦理边界提醒",
        render_text(report.ethics_reminder),
    ]
    if has_reasoned_analysis:
        sections.extend(_reasoned_analysis(report))
    if governance_summary is not None:
        sections.append(render_source_grounded_governance_markdown(governance_summary))
    return "\n\n".join(section for section in sections if section) + "\n"
```

```python
# src/mingli_engine/html.py
from mingli_engine.application_reports import render_source_grounded_governance_html
from mingli_engine.models import DomainCalibrationReleaseSummary


def render_html_report(
    report: Report,
    *,
    governance_summary: DomainCalibrationReleaseSummary | None = None,
) -> str:
    basic_data = "\n".join(
        [
            _subsection("命造卡片", report.chart_card),
            _subsection("排盘来源与假设", report.assumptions),
        ]
    )
    structure_observation = "\n".join(
        [
            _subsection(
                "四柱与五行摘要",
                f"{report.four_pillars_summary}\n{report.five_elements_summary}",
            ),
            _subsection("十神摘要", report.ten_gods_summary),
            _subsection("观察依据", report.evidence_notes),
            _subsection("正式知识综合", report.formal_synthesis),
            _subsection("综合脉络", report.integrated_synthesis),
            _subsection("结构分析", report.structure_analysis),
            _subsection("性格倾向", report.personality_tendencies),
        ]
    )
    action_reflection = "\n".join(
        [
            _subsection("优势与议题", report.strengths_and_issues),
            _subsection("阶段概览", report.phase_overview),
            _subsection("行动建议", report.action_suggestions),
        ]
    )
    sections = "\n".join(
        [
            _section("免责声明", _block(report.disclaimer)),
            _section("快速导读", _block(report.quick_guide)),
            _section("第一层：基础资料", basic_data),
            _section("第二层：结构观察", structure_observation),
            _section("第三层：解读边界", _block(report.interpretation_boundaries)),
            _section("第四层：行动反思", action_reflection),
            _section("术语简注", _block(report.glossary)),
            _section("伦理边界提醒", _block(report.ethics_reminder)),
        ]
    )
    if _has_reasoned_analysis(report):
        sections = "\n".join([sections, _reasoned_analysis(report)])
    if governance_summary is not None:
        sections = "\n".join([sections, render_source_grounded_governance_html(governance_summary)])

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="zh-CN">',
            "<head>",
            '<meta charset="utf-8">',
            "<title>" + _text(report.title) + "</title>",
            "<style>",
            _STYLE,
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>" + _text(report.title) + "</h1>",
            sections,
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )
```

Update `src\mingli_engine\report_release.py` in `build_report_release_summary()`:

```python
import os

from mingli_engine.domain_calibration_release import build_domain_calibration_summary, load_canonical_governance_decision

source_grounded = build_domain_calibration_summary(governance_decision_path=os.environ.get("MINGLI_CANONICAL_GOVERNANCE_DECISION"))

return ReportReleaseSummary(
    release_id=RELEASE_ID,
    release_status=release_status,
    manifest_case_count=len(manifest),
    passed_case_count=passed_case_count,
    failed_case_count=len(cases) - passed_case_count,
    safe_report_case_count=sum(case["kind"] == "safe_markdown" for case in manifest),
    guarded_report_case_count=sum(case["kind"] == "high_risk_markdown" for case in manifest),
    rejected_request_case_count=sum(case["kind"] == "safety_json" for case in manifest),
    distinct_report_output_count=len(fingerprints),
    acceptance_baseline_id=acceptance.baseline_id,
    acceptance_status=acceptance.acceptance_status,
    approved_evidence_count=acceptance.approved_evidence_count,
    rule_family_count=acceptance.rule_family_count,
    action_track_count=(next(iter(action_counts)) if len(action_counts) == 1 else 0),
    cases=cases,
    guardrails=[
        "synthetic_fixtures_not_persisted",
        "release_summary_excludes_profile_and_report_content",
        "source_library_013_012_read_only",
        "high_risk_outputs_require_narrowing_or_rejection",
    ],
    next_action=next_action,
    source_grounded_application_release_status=source_grounded.application_release_status,
    source_grounded_evidence_maturity_status=source_grounded.evidence_maturity_status,
    source_grounded_evidence_maturity_scope_records=source_grounded.evidence_maturity_scope_records,
    source_grounded_release_statement=source_grounded.release_statement,
    source_grounded_limitations=source_grounded.limitations,
    source_grounded_abstention_policy=source_grounded.abstention_policy,
    source_grounded_claim_boundary_hash=source_grounded.release_claim_boundary_hash,
    source_grounded_application_evidence_hash=source_grounded.application_evidence_hash,
    source_grounded_installed_wheel_evidence_hash=source_grounded.installed_wheel_evidence_hash,
    source_grounded_package_identity=source_grounded.package_identity,
    source_grounded_distribution_version=source_grounded.distribution_version,
    source_grounded_application_version=source_grounded.governance_application_version,
)
```

Update `src\mingli_engine\project_completion.py` where `ProjectCompletionSummary` is constructed:

```python
import os

source_grounded = build_domain_calibration_summary(governance_decision_path=os.environ.get("MINGLI_CANONICAL_GOVERNANCE_DECISION"))

summary = ProjectCompletionSummary(
    baseline_id=baseline_id,
    completion_status=completion_status,
    feature_count=feature_count,
    spec_count=spec_count,
    plan_count=plan_count,
    task_tracked_feature_count=task_tracked_feature_count,
    legacy_feature_count=legacy_feature_count,
    functional_requirement_count=functional_requirement_count,
    success_criteria_count=success_criteria_count,
    checked_task_count=checked_task_count,
    unchecked_task_count=unchecked_task_count,
    checklist_file_count=checklist_file_count,
    checked_checklist_item_count=checked_checklist_item_count,
    unchecked_checklist_item_count=unchecked_checklist_item_count,
    quality_checks=quality_checks,
    completion_checks=completion_checks,
    release_id=release.release_id,
    release_status=release.release_status,
    acceptance_baseline_id=release.acceptance_baseline_id,
    acceptance_status=release.acceptance_status,
    approved_evidence_count=release.approved_evidence_count,
    rule_family_count=release.rule_family_count,
    action_track_count=release.action_track_count,
    open_conflicts=open_conflicts,
    legacy_feature_ids=legacy_feature_ids,
    features=features,
    controlled_boundaries=controlled_boundaries,
    remaining_local_blockers=remaining_local_blockers,
    next_action=next_action,
    calculation_checks=calculation_checks,
    source_grounded_application_release_status=source_grounded.application_release_status,
    source_grounded_evidence_maturity_status=source_grounded.evidence_maturity_status,
    source_grounded_evidence_maturity_scope_records=source_grounded.evidence_maturity_scope_records,
    source_grounded_release_statement=source_grounded.release_statement,
    source_grounded_limitations=source_grounded.limitations,
    source_grounded_abstention_policy=source_grounded.abstention_policy,
    source_grounded_claim_boundary_hash=source_grounded.release_claim_boundary_hash,
    source_grounded_application_evidence_hash=source_grounded.application_evidence_hash,
    source_grounded_installed_wheel_evidence_hash=source_grounded.installed_wheel_evidence_hash,
    source_grounded_package_identity=source_grounded.package_identity,
    source_grounded_distribution_version=source_grounded.distribution_version,
    source_grounded_application_version=source_grounded.governance_application_version,
)
```

- [ ] **Step 4: Run tests to verify pass**

Run:

```powershell
$ErrorActionPreference = 'Stop'
$wheelOut = Join-Path $env:TEMP ('mingli-task7-pass-wheel-' + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $wheelOut | Out-Null
python -m build --wheel --outdir $wheelOut
if ($LASTEXITCODE -ne 0) { throw 'Task 7 pass wheel build failed' }
$wheels = @(Get-ChildItem -LiteralPath $wheelOut -Filter '*.whl')
if ($wheels.Count -ne 1) { throw "expected exactly one Task 7 pass wheel in $wheelOut, found $($wheels.Count)" }
$wheel = $wheels[0]
$venvRoot = Join-Path $env:TEMP ('mingli-output-wheel-venv-' + [guid]::NewGuid().ToString())
python -m venv $venvRoot
if ($LASTEXITCODE -ne 0) { throw 'Task 7 pass venv creation failed' }
$env:MINGLI_INSTALLED_PYTHON = Join-Path $venvRoot 'Scripts\python.exe'
& $env:MINGLI_INSTALLED_PYTHON -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'Task 7 pass pip upgrade failed' }
& $env:MINGLI_INSTALLED_PYTHON -m pip install $wheel.FullName
if ($LASTEXITCODE -ne 0) { throw 'Task 7 pass wheel install failed' }
pytest tests/unit/test_domain_calibration_release.py tests/unit/test_application_reports.py tests/unit/test_report_release.py tests/unit/test_project_completion.py tests/contract/test_report_release_cli_contract.py tests/integration/test_packaged_release_docs.py -q
if ($LASTEXITCODE -ne 0) { throw 'Task 7 output tests failed' }
```

Expected: PASS.

- [ ] **Step 5: Final scans**

Run:

```powershell
$patterns = @(
  'T' + 'ODO',
  'T' + 'BD',
  'fill in ' + 'details',
  'similar ' + 'to',
  'passed' + ': bool',
  '"passed"' + ': True',
  'hard_gates=\(',
  'release_summary\.py',
  'domain-calibration ' + 'summary',
  'release_gate' + '_decision',
  'release_version' + '_decision',
  'build_candidate_version_set\(\)',
  'first_recompute_payload=' + 'final_payload',
  'second_recompute_payload=' + 'final_payload',
  'update-version-source --owner-version \$ownerVersion\s*$',
  '--wheel-' + 'filename',
  '--wheel-' + 'sha256',
  'MINGLI_FINAL_WHEEL_' + 'FILENAME',
  'MINGLI_FINAL_WHEEL_' + 'SHA256',
  'write_verified' + '_installed_evidence_artifact',
  'write_verified' + '_governance_decision_artifact',
  '_write_typed' + '_installed_evidence_artifact',
  'Get-ChildItem -LiteralPath ' + 'dist -Filter',
  'Sort-Object ' + 'LastWriteTime',
  'python -m build --' + 'wheel\s*$',
  'Push-Location \$env:' + 'TEMP',
  'Join-Path \$env:' + 'TEMP ''first-installed-audit',
  'Join-Path \$env:' + 'TEMP ''second-installed-audit',
  'Join-Path \$env:' + 'TEMP ''final-installed-wheel-evidence',
  '>\s*first-installed-audit\.json',
  '>\s*second-installed-audit\.json',
  '--output\s+final-installed-wheel-evidence\.json',
  'release_version_workflow inspect-installed-evidence --evidence \$finalEvidencePath --output final-installed-inspect\.json',
  'release_version_workflow write-governance-decision --installed-evidence \$finalEvidencePath --output canonical-ready-governance-decision\.json',
  'execution thread must ' + 'handle cleanup',
  'execution thread must ' + 'handle any needed cleanup',
  'manual ' + 'cleanup',
  'final installed evidence is not ready; do not stage version source or write ready ' + 'decision',
  'Final changed-version evidence is .*stop before ready ' + 'decision',
  'WriteAllBytes\(\$pyproject' + 'Path',
  'exit 0\s*$',
  'application_release_status=' + '\"not_evaluated\"',
  'installed_wheel_evidence_hash=' + '\"\"',
  'derive_application_release_status' + '_from_legacy',
  '\.' + 'metric_snapshot',
  ([char]0xFFFD) + '|' + ([char]0x00C3)
)
rg -n ($patterns -join '|') docs/superpowers/plans/2026-07-15-bazi-source-grounded-ai-release-governance-amendment-plan.md
rg -n ('place' + 'holder') docs/superpowers/plans/2026-07-15-bazi-source-grounded-ai-release-governance-amendment-plan.md
rg -n ('0\.' + '2\.' + '0|build_candidate_version_set') src tests
$badRawFields = @(
  'traced' + '_cases',
  'total' + '_cases',
  'total' + '_outputs',
  'unsupported' + '_inference_count',
  'unsupported' + '_ids',
  'total' + '_conflicts',
  'unresolved' + '_conflicts',
  'conflict' + '_ids',
  'required' + '_abstentions',
  'actual' + '_abstentions',
  'missed' + '_abstention_ids',
  'safety' + '_critical_cases',
  'privacy' + '_statuses'
)
rg -n ($badRawFields -join '|') docs/superpowers/plans/2026-07-15-bazi-source-grounded-ai-release-governance-amendment-plan.md
rg -n ('def _domain_calibration_summary_parser|def _handle_domain_calibration_summary|ApplicationEvidenceBundle' + '\(|InstalledWheelReleaseEvidence' + '\(') docs/superpowers/plans/2026-07-15-bazi-source-grounded-ai-release-governance-amendment-plan.md
python -m compileall src/mingli_engine tests
pytest --collect-only tests/unit/test_domain_calibration_release.py tests/unit/test_release_version_workflow.py tests/unit/test_application_reports.py tests/unit/test_report_release.py tests/unit/test_project_completion.py tests/contract/test_report_release_cli_contract.py tests/integration/test_installed_release_audit.py tests/integration/test_packaged_release_docs.py
uv run --with ruff==0.12.11 ruff check `
  src/mingli_engine/release_version_workflow.py `
  tests/unit/test_release_version_workflow.py `
  --select F821
@'
import ast
from pathlib import Path

checks = {
    "src/mingli_engine/domain_calibration_models.py": {
        "classes": {
            "ApplicationEvidenceBundle",
            "InstalledWheelReleaseEvidence",
            "ReleaseVersionDecision",
            "ReleaseApprovalRecord",
            "ReleaseGovernanceDecision",
        },
        "functions": {"replay_application_gate_evidence", "produce_missing_raw_gate_evidence"},
    },
    "src/mingli_engine/domain_calibration_release.py": {
        "functions": {
            "collect_raw_application_gate_results_from_existing_validators",
            "build_expected_release_resource_manifest_from_checkout",
            "build_installed_wheel_release_evidence_from_audit_files",
            "choose_release_version_after_installed_evidence",
            "write_canonical_governance_decision_artifact",
            "load_canonical_governance_decision",
            "transition_release_governance",
            "build_domain_calibration_summary",
        },
    },
    "src/mingli_engine/release_version_workflow.py": {
        "functions": {"main", "_update_version_source", "_restore_version_source", "_write_governance_decision", "restore_version_source_bytes"},
    },
    "src/mingli_engine/cli.py": {
        "functions": {"_build_parser", "_domain_calibration_summary"},
    },
}
expected_args = {
    "build_domain_calibration_summary": {"governance_decision_path"},
    "write_canonical_governance_decision_artifact": {"output_path", "application_evidence_path", "installed_evidence_path"},
    "transition_release_governance": {"previous", "application_evidence", "installed_evidence", "approval"},
    "restore_version_source_bytes": {"path", "original_bytes"},
    "_restore_version_source": {"args"},
}
for rel_path, expected in checks.items():
    tree = ast.parse(Path(rel_path).read_text(encoding="utf-8"))
    classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    functions = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    missing_classes = expected.get("classes", set()) - classes
    missing_functions = expected.get("functions", set()) - set(functions)
    if missing_classes or missing_functions:
        raise SystemExit(f"{rel_path} missing classes={sorted(missing_classes)} functions={sorted(missing_functions)}")
    for function_name, required in expected_args.items():
        if function_name in functions:
            args = {arg.arg for arg in functions[function_name].args.args + functions[function_name].args.kwonlyargs}
            if not required.issubset(args):
                raise SystemExit(f"{rel_path}:{function_name} args {sorted(args)} missing {sorted(required - args)}")
'@ | python -
```

Expected: first command has no matches. The second command may show only the real existing validator key named by `"place" + "holder_integrity"`; any other match is a plan defect. The third command may show historical or existing-version references; each match must be reviewed. No match may keep a fixed release-decision path, fixed final wheel version, or a `build_candidate_version_set` restriction that prevents release-owner selected versions. The Raw-field scan has no matches. The evidence-constructor scan may show dataclass definitions only; direct decision-path construction in tests or release code is a defect. `compileall` proves syntax only. `pytest --collect-only` must collect every planned test without import/signature errors. `uv run --with ruff==0.12.11 ruff check ... --select F821` must PASS with no undefined-name findings. The AST check must confirm the required production symbols and keyword parameters before any implementation thread claims type/signature consistency.

- [ ] **Step 6: Commit boundary**

Run:

```powershell
git add src/mingli_engine/domain_calibration_release.py src/mingli_engine/application_reports.py src/mingli_engine/markdown.py src/mingli_engine/html.py src/mingli_engine/report_release.py src/mingli_engine/cli.py src/mingli_engine/project_completion.py tests/unit/governance_decision_fixtures.py tests/unit/test_domain_calibration_release.py tests/unit/test_application_reports.py tests/unit/test_report_release.py tests/unit/test_project_completion.py tests/contract/test_report_release_cli_contract.py tests/integration/test_packaged_release_docs.py
git commit -m "feat: expose source grounded release governance outputs"
```

## Writing-Plans Self-Review

- Coverage matrix references only tests whose full code appears in this plan.
- No matrix row references a nonexistent task.
- Paths use `E:\命理演绎` for approved planning documents and `E:\mingli-019-closure` for future implementation files.
- Legacy schema migration includes typed artifact model, loader, derived projection, and non-rewrite test.
- Maturity policy accepts typed `SourceScopeAssessmentEvidence`, computes conclusions, uses `ziping`, and never derives a conclusion from legacy metrics.
- Hard-gate release API accepts raw results, not prebuilt green gate evidence.
- Installed-wheel evidence computes canonical hashes from payloads and validates exact manifest and checkout-external source isolation.
- Installed audit accepts only `--wheel-path`, verifies the wheel exists, computes filename and SHA-256 internally, reads wheel METADATA Name/Version, compares wheel and installed resource manifests, and rejects metadata or version mismatches.
- Version decisions accept `InstalledWheelReleaseEvidence`; released state requires previous ready state bound to the same installed evidence hash.
- `write_canonical_governance_decision_artifact()` and `load_canonical_governance_decision()` are implemented in Task 5 before `release_version_workflow.py` imports them; Task 7 consumes these functions only.
- `tests/unit/governance_decision_fixtures.py` is created only in Task 4, added to Task 4 and Task 5 git boundaries, and modified in Task 7 only by appending the governance output fixture helper.
- `classify_application_release_status_from_gate_statuses()` is the single status priority source for inspect and transition: failed or blocked gates become `blocked`, otherwise any `not_evaluated` gate remains `not_evaluated`, and only the exact full passed set becomes ready.
- `write-governance-decision` prints the decision status and returns nonzero for `blocked` or `not_evaluated`; future production commands use a shared `$finalEvidencePath` tail for ready/released decisions with no keep-version early exit.
- Task 7 final verification includes `uv run --with ruff==0.12.11 ruff check src/mingli_engine/release_version_workflow.py tests/unit/test_release_version_workflow.py --select F821`; self-review does not rely only on `compileall` and `pytest --collect-only` for undefined-name detection.
- Approval evidence binds installed evidence hash, package identity, distribution version, claim boundary hash, limitations hash, abstention policy hash, and acknowledged hashes.
- Historical tests use real calibration data paths and preserve optional `calibration_baseline.json` absence or hash.
- Output tasks use existing `report_release.py`, `test_report_release.py`, and `domain-calibration-summary`.


