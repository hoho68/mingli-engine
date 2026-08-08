# Bazi Domain Validation And Application V1 Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Before execution, use superpowers:using-git-worktrees to create an isolated closure worktree from clean HEAD `d7d05b1`; do not bring in the current workspace's Feature 020 files or uncommitted changes. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the unfinished Feature 019 release sequence without repeating completed Tasks 0-14: add deterministic release gates, freeze the final baseline only from a pre-baseline 0.2.0 installation, rebuild a post-baseline final wheel, verify fresh installed evidence, and close formal Spec Kit governance.

**Architecture:** Treat commit `8e7b7ef` Task 14 as complete candidate-calibration work: it creates candidate run/snapshot evidence and a test-local candidate baseline only. The newer Spec Kit release sequence in `specs/_drafts/019-bazi-domain-validation-and-application-v1/plan.md`, `data-model.md`, `quickstart.md`, `contracts/domain-calibration-v1-contract.md`, and `tasks.md` is authoritative: Task 15 proves non-version gates while release remains blocked, and Task 16 alone advances to 0.2.0, builds a pre-baseline wheel, runs final calibration, freezes `calibration_baseline.json` through a controlled writer, discards the pre-baseline wheel, rebuilds the final wheel, and derives release evidence only from a new final installation.

**Tech Stack:** Python 3.12+, standard library dataclasses/pathlib/subprocess/importlib resources, existing `mingli_engine` application and calibration modules, setuptools wheel packaging, pytest 8.4.1, mypy 1.17.1, Ruff 0.12.11, PowerShell commands with `uv run --frozen --with ...` to avoid lockfile mutation.

---

## Scope Check

This plan covers only the true unfinished Feature 019 closure work after committed Task 14. It does not repeat Tasks 0-14, does not restore the old Task 14 baseline-freeze step from the original implementation plan, does not include Feature 020 files, and does not start Feature 020. The plan creates future execution steps only.

## Mandatory Execution Preconditions

- Start from clean commit `d7d05b1`.
- Use `superpowers:using-git-worktrees` before implementation.
- Create a separate worktree and branch such as:

```powershell
git worktree add ..\mingli-019-closure d7d05b1
Set-Location ..\mingli-019-closure
git switch -c codex/019-closure-release
```

- Confirm the closure worktree does not contain current Feature 020 files:

```powershell
git status --short --branch
Test-Path docs/superpowers/specs/2026-07-14-bazi-domain-calibration-benchmark-v2-design.md
Test-Path src/mingli_engine/data/domain_calibration/v2
Test-Path tests/unit/test_domain_calibration_v2_fixture_models.py
```

Expected: clean branch status, and all three `Test-Path` checks return `False`.

## Standard Command Rules

Every pytest command uses:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
```

Every `uv` command uses `--frozen`:

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest <targets> -q -p no:cacheprovider
uv run --frozen --with mypy==1.17.1 python -m mypy <targets> --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check <targets>
```

Use a 30000 ms controller timeout for ordinary commands and focused tests. Use a 900000 ms controller timeout only for the final full suite.

## Completed Work To Preserve

- Task 14 commit `8e7b7ef` exists and is not rewritten.
- `src/mingli_engine/domain_calibration.py` already provides `build_candidate_version_set`, `execute_candidate_calibration`, `build_candidate_metric_snapshot`, `write_candidate_baseline`, `candidate_matches_installed_application`, metric helpers, read-only loaders, and `validate_version_set_equality`.
- `tests/integration/test_domain_calibration_pipeline.py` already proves candidate execution is deterministic, targets `application_version=0.2.0`, writes only `tmp_path/calibration_baseline_candidate.json`, refuses tracked baseline writes, and creates no tracked artifacts.
- `src/mingli_engine/data/domain_calibration/calibration_baseline.json`, `src/mingli_engine/domain_calibration_release.py`, `tests/unit/test_domain_calibration_release.py`, `tests/integration/test_installed_real_use.py`, and final `dist/` release evidence do not exist at the start of this plan.

## File Structure

- Create: `src/mingli_engine/domain_calibration_release.py`  
  Owns release-gate evaluation, non-version blockers, installed-packaging injection, final baseline freeze, and exact version-set release decisions.
- Modify: `src/mingli_engine/models.py`  
  Adds public `DomainCalibrationReleaseSummary` and `DomainCalibrationGateResult` DTOs for CLI/project-completion JSON.
- Modify: `src/mingli_engine/cli.py`  
  Adds `domain-calibration-summary` command and exit code `4` for blocked release.
- Modify: `src/mingli_engine/project_completion.py`  
  Integrates Feature 019 calibration release evidence without changing completed-feature counts before Task 17.
- Create: `tests/unit/test_domain_calibration_release.py`  
  Tests exact gates, blockers, version-set equality, final baseline writer, and historical 018 isolation.
- Create: `tests/integration/test_installed_real_use.py`  
  Tests installed real-use analysis/reports and installed domain calibration summary from isolated targets.
- Modify: `tests/contract/test_wheel_runtime_assets.py`  
  Adds final 0.2.0 wheel, post-baseline identity, and manifest evidence assertions.
- Modify: `tests/integration/test_installed_package_baseline.py`  
  Updates installed verifier expectations from 0.1.0 to 0.2.0 only in Task 16.
- Modify: `tests/unit/test_project_completion.py`  
  Adds formal 019 closure expectations in Task 17.
- Modify: `tests/contract/test_project_completion_cli_contract.py`  
  Adds formal 019 CLI completion expectations in Task 17.
- Modify: `pyproject.toml`  
  Version changes from `0.1.0` to `0.2.0` only after Task 15 non-version gates are green.
- Create: `src/mingli_engine/data/domain_calibration/calibration_baseline.json`  
  Created only by the Task 16 controlled release writer after the pre-baseline 0.2.0 wheel computes the fresh final snapshot.
- Move: `specs/_drafts/019-bazi-domain-validation-and-application-v1/` to `specs/019-bazi-domain-validation-and-application-v1/`  
  Task 17 only.
- Modify: `.specify/feature.json`  
  Task 17 only.
- Create: `docs/classical_sources/domain_calibration.md`
- Create: `docs/classical_sources/real_use_application.md`
- Modify: `docs/classical_sources/README.md`

## Task 0: Confirm Task 14 Evidence And Isolation

**Files:**
- Read: `src/mingli_engine/domain_calibration.py`
- Read: `tests/integration/test_domain_calibration_pipeline.py`
- Read: `specs/_drafts/019-bazi-domain-validation-and-application-v1/plan.md`
- Read: `specs/_drafts/019-bazi-domain-validation-and-application-v1/tasks.md`

- [ ] **Step 1: Confirm worktree and Task 14 baseline state**

```powershell
git rev-parse --short HEAD
git status --short --branch
git show --stat --oneline --no-renames 8e7b7ef
Test-Path src/mingli_engine/data/domain_calibration/calibration_baseline.json
Test-Path src/mingli_engine/domain_calibration_release.py
Test-Path docs/superpowers/specs/2026-07-14-bazi-domain-calibration-benchmark-v2-design.md
```

Expected: HEAD is `d7d05b1`, branch is `codex/019-closure-release`, status is clean, Task 14 commit is `8e7b7ef feat: measure bazi domain conformance`, baseline and release module are `False`, and the Feature 020 design file is `False`.

- [ ] **Step 2: Run focused Task 14 evidence tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/integration/test_domain_calibration_pipeline.py -q -p no:cacheprovider
```

Expected: PASS. This proves Task 14 is candidate-only and never writes `src/mingli_engine/data/domain_calibration/calibration_baseline.json`.

- [ ] **Step 3: Run focused protocol regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_models.py tests/unit/test_domain_calibration_corpus.py tests/unit/test_domain_calibration_adjudication.py tests/integration/test_domain_calibration_pipeline.py -q -p no:cacheprovider
```

Expected: PASS. Existing calibration models, corpus, adjudication, and candidate metrics remain intact.

- [ ] **Step 4: Commit**

No commit for Task 0. It is an evidence confirmation gate.

## Task 1: Add Domain Calibration Release Gates

**Files:**
- Create: `src/mingli_engine/domain_calibration_release.py`
- Create: `tests/unit/test_domain_calibration_release.py`

- [ ] **Step 1: Write failing release-gate tests**

Create `tests/unit/test_domain_calibration_release.py`:

```python
from __future__ import annotations

from dataclasses import replace

import pytest

from mingli_engine.domain_calibration import (
    CalibrationProtocolError,
    build_candidate_metric_snapshot,
    build_candidate_version_set,
    execute_candidate_calibration,
    validate_version_set_equality,
)
from mingli_engine.domain_calibration_models import (
    CalibrationReleaseDecision,
    MetricSnapshotV1,
)
from mingli_engine.domain_calibration_release import (
    RELEASE_CLAIM_BOUNDARY,
    build_domain_calibration_release_decision,
)
from mingli_engine.packaging_validation import PackagingVerification


def _snapshot() -> MetricSnapshotV1:
    version_set = build_candidate_version_set("0.2.0")
    run = execute_candidate_calibration(version_set)
    repeated = execute_candidate_calibration(version_set)
    return build_candidate_metric_snapshot(run, repeated)


def _verified_packaging(version: str = "0.1.0") -> PackagingVerification:
    return PackagingVerification(
        asset_sha256={"data/domain_calibration/calibration_assertions.json": "a" * 64},
        distribution_version=version,
        source_isolated=True,
        overall_status="verified",
    )


def test_release_decision_has_exact_gate_set_and_blocks_before_final_baseline() -> None:
    snapshot = _snapshot()
    decision = build_domain_calibration_release_decision(
        snapshot=snapshot,
        baseline=None,
        packaging=_verified_packaging("0.1.0"),
        application_contract_status="passed",
        privacy_status="passed",
        documentation_status="passed",
        compatibility_status="passed",
    )

    assert isinstance(decision, CalibrationReleaseDecision)
    assert decision.schema_version == "domain-calibration-release-v1"
    assert decision.release_status == "blocked"
    assert tuple(decision.checks) == (
        "determinism",
        "pillar_agreement",
        "trace_completeness",
        "unsupported_inference",
        "school_disagreement",
        "abstention",
        "adjudication",
        "reviewer_independence",
        "reviewer_agreement",
        "engine_match",
        "safety_critical",
        "application_contract",
        "privacy",
        "packaging",
        "documentation",
        "compatibility",
        "claim_boundary",
        "version_set",
        "final_baseline",
    )
    assert decision.checks["determinism"] == "passed"
    assert decision.checks["version_set"] == "failed"
    assert decision.checks["final_baseline"] == "failed"
    assert "installed distribution version is not 0.2.0" in decision.blockers
    assert "final calibration baseline is missing" in decision.blockers
    assert decision.claim_boundary == RELEASE_CLAIM_BOUNDARY
    assert decision.version_set == snapshot.version_set
    assert decision.next_action == "complete_task16_final_baseline_and_final_wheel"


@pytest.mark.parametrize(
    ("field_name", "bad_value", "blocker"),
    [
        ("determinism_rate", 0.999, "determinism gate failed"),
        ("pillar_agreement_rate", 0.999, "pillar agreement gate failed"),
        ("evidence_trace_completeness_rate", 0.999, "trace completeness gate failed"),
        ("rule_trace_completeness_rate", 0.999, "trace completeness gate failed"),
        ("adjudication_coverage_rate", 0.999, "adjudication gate failed"),
        ("unsupported_computed_count", 1, "unsupported inference gate failed"),
        ("dependency_bypass_count", 1, "unsupported inference gate failed"),
        ("school_disagreement_recall", 0.999, "school disagreement gate failed"),
        ("silent_school_collapse_count", 1, "school disagreement gate failed"),
        ("mandatory_abstention_rate", 0.999, "abstention gate failed"),
        ("reviewer_raw_agreement", 0.69, "reviewer agreement gate failed"),
        ("adjudicated_engine_match", 0.89, "engine match gate failed"),
        ("safety_critical_exact_match", 0.999, "safety-critical gate failed"),
    ],
)
def test_each_release_threshold_has_a_deterministic_blocker(
    field_name: str,
    bad_value: int | float,
    blocker: str,
) -> None:
    snapshot = replace(_snapshot(), **{field_name: bad_value})
    decision = build_domain_calibration_release_decision(
        snapshot=snapshot,
        baseline=snapshot,
        packaging=_verified_packaging("0.2.0"),
        application_contract_status="passed",
        privacy_status="passed",
        documentation_status="passed",
        compatibility_status="passed",
    )

    assert decision.release_status == "blocked"
    assert blocker in decision.blockers


def test_ready_release_requires_equal_run_baseline_and_release_version_sets() -> None:
    snapshot = _snapshot()
    decision = build_domain_calibration_release_decision(
        snapshot=snapshot,
        baseline=snapshot,
        packaging=_verified_packaging("0.2.0"),
        application_contract_status="passed",
        privacy_status="passed",
        documentation_status="passed",
        compatibility_status="passed",
    )
    run = execute_candidate_calibration(snapshot.version_set)

    assert decision.release_status == "ready_with_guardrails"
    validate_version_set_equality(run, snapshot, decision)


def test_release_blocks_version_set_drift_before_thresholds_are_considered() -> None:
    snapshot = _snapshot()
    drifted = replace(
        snapshot,
        version_set=replace(snapshot.version_set, application_version="0.1.0"),
    )

    with pytest.raises(ValueError, match="corpus_sha256"):
        replace(drifted, corpus_sha256="b" * 64)
```

- [ ] **Step 2: Run tests and confirm red**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py -q -p no:cacheprovider
```

Expected: FAIL with `ModuleNotFoundError: No module named 'mingli_engine.domain_calibration_release'`.

- [ ] **Step 3: Implement minimal release gate module**

Create `src/mingli_engine/domain_calibration_release.py`:

```python
from __future__ import annotations

from collections import OrderedDict

from mingli_engine.domain_calibration_models import (
    CalibrationReleaseDecision,
    MetricSnapshotV1,
)
from mingli_engine.packaging_validation import PackagingVerification


RELEASE_CLAIM_BOUNDARY = (
    "Independent agent-based domain-conformance calibration of deterministic "
    "structural outputs against tracked traditional-method evidence and blinded "
    "agent-independent reviewer labels; not scientific, causal, predictive, "
    "real-world outcome, human expert, or universal-school validation."
)

_GATE_NAMES = (
    "determinism",
    "pillar_agreement",
    "trace_completeness",
    "unsupported_inference",
    "school_disagreement",
    "abstention",
    "adjudication",
    "reviewer_independence",
    "reviewer_agreement",
    "engine_match",
    "safety_critical",
    "application_contract",
    "privacy",
    "packaging",
    "documentation",
    "compatibility",
    "claim_boundary",
    "version_set",
    "final_baseline",
)


def _pass_fail(condition: bool) -> str:
    return "passed" if condition else "failed"


def _sampled_strata_pass(snapshot: MetricSnapshotV1) -> bool:
    coverage = snapshot.coverage
    stratum_counts = coverage.get("stratum")
    if not isinstance(stratum_counts, dict):
        return False
    for stratum, rate in snapshot.reviewer_stratum_agreement.items():
        denominator = stratum_counts.get(stratum, 0)
        if isinstance(denominator, int) and denominator >= 10 and rate < 0.60:
            return False
    return True


def build_domain_calibration_release_decision(
    *,
    snapshot: MetricSnapshotV1,
    baseline: MetricSnapshotV1 | None,
    packaging: PackagingVerification,
    application_contract_status: str,
    privacy_status: str,
    documentation_status: str,
    compatibility_status: str,
) -> CalibrationReleaseDecision:
    if not isinstance(snapshot, MetricSnapshotV1):
        raise TypeError("snapshot must be MetricSnapshotV1")
    if baseline is not None and not isinstance(baseline, MetricSnapshotV1):
        raise TypeError("baseline must be MetricSnapshotV1")
    if not isinstance(packaging, PackagingVerification):
        raise TypeError("packaging must be PackagingVerification")

    checks = OrderedDict((name, "failed") for name in _GATE_NAMES)
    checks["determinism"] = _pass_fail(snapshot.determinism_rate == 1.0)
    checks["pillar_agreement"] = _pass_fail(snapshot.pillar_agreement_rate == 1.0)
    checks["trace_completeness"] = _pass_fail(
        snapshot.evidence_trace_completeness_rate == 1.0
        and snapshot.rule_trace_completeness_rate == 1.0
    )
    checks["unsupported_inference"] = _pass_fail(
        snapshot.unsupported_computed_count == 0
        and snapshot.dependency_bypass_count == 0
    )
    checks["school_disagreement"] = _pass_fail(
        snapshot.school_disagreement_recall == 1.0
        and snapshot.silent_school_collapse_count == 0
    )
    checks["abstention"] = _pass_fail(snapshot.mandatory_abstention_rate == 1.0)
    checks["adjudication"] = _pass_fail(snapshot.adjudication_coverage_rate == 1.0)
    checks["reviewer_independence"] = _pass_fail(snapshot.assertion_count >= 42)
    checks["reviewer_agreement"] = _pass_fail(
        snapshot.reviewer_raw_agreement >= 0.70 and _sampled_strata_pass(snapshot)
    )
    checks["engine_match"] = _pass_fail(snapshot.adjudicated_engine_match >= 0.90)
    checks["safety_critical"] = _pass_fail(snapshot.safety_critical_exact_match == 1.0)
    checks["application_contract"] = _pass_fail(application_contract_status == "passed")
    checks["privacy"] = _pass_fail(privacy_status == "passed")
    checks["packaging"] = _pass_fail(
        packaging.overall_status == "verified" and packaging.source_isolated
    )
    checks["documentation"] = _pass_fail(documentation_status == "passed")
    checks["compatibility"] = _pass_fail(compatibility_status == "passed")
    checks["claim_boundary"] = _pass_fail("predictive" in RELEASE_CLAIM_BOUNDARY)
    checks["version_set"] = _pass_fail(
        snapshot.version_set.application_version == "0.2.0"
        and packaging.distribution_version == "0.2.0"
    )
    checks["final_baseline"] = _pass_fail(
        baseline is not None and baseline.version_set == snapshot.version_set
    )

    blocker_messages = {
        "determinism": "determinism gate failed",
        "pillar_agreement": "pillar agreement gate failed",
        "trace_completeness": "trace completeness gate failed",
        "unsupported_inference": "unsupported inference gate failed",
        "school_disagreement": "school disagreement gate failed",
        "abstention": "abstention gate failed",
        "adjudication": "adjudication gate failed",
        "reviewer_independence": "reviewer independence gate failed",
        "reviewer_agreement": "reviewer agreement gate failed",
        "engine_match": "engine match gate failed",
        "safety_critical": "safety-critical gate failed",
        "application_contract": "application contract gate failed",
        "privacy": "privacy gate failed",
        "packaging": "packaging gate failed",
        "documentation": "documentation gate failed",
        "compatibility": "compatibility gate failed",
        "claim_boundary": "claim boundary gate failed",
        "version_set": "installed distribution version is not 0.2.0",
        "final_baseline": "final calibration baseline is missing",
    }
    blockers = tuple(
        blocker_messages[name] for name, status in checks.items() if status == "failed"
    )
    status = "ready_with_guardrails" if not blockers else "blocked"
    next_action = (
        "release_complete_with_guardrails"
        if status == "ready_with_guardrails"
        else "complete_task16_final_baseline_and_final_wheel"
    )
    return CalibrationReleaseDecision(
        schema_version="domain-calibration-release-v1",
        release_status=status,
        checks=dict(checks),
        metrics=snapshot,
        blockers=blockers,
        claim_boundary=RELEASE_CLAIM_BOUNDARY,
        version_set=snapshot.version_set,
        next_action=next_action,
    )
```

- [ ] **Step 4: Run focused release tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 5: Run focused regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_models.py tests/integration/test_domain_calibration_pipeline.py tests/unit/test_domain_calibration_release.py -q -p no:cacheprovider
uv run --frozen --with mypy==1.17.1 python -m mypy src/mingli_engine/domain_calibration.py src/mingli_engine/domain_calibration_models.py src/mingli_engine/domain_calibration_release.py --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check src/mingli_engine/domain_calibration.py src/mingli_engine/domain_calibration_models.py src/mingli_engine/domain_calibration_release.py tests/unit/test_domain_calibration_release.py tests/integration/test_domain_calibration_pipeline.py
```

Expected: pytest PASS, mypy reports no issues, Ruff reports no findings.

- [ ] **Step 6: Commit**

```powershell
git add src/mingli_engine/domain_calibration_release.py tests/unit/test_domain_calibration_release.py
git commit -m "feat: gate calibrated application release"
```

Expected: commit created without staging Feature 020 files.

## Task 2: Add Domain Calibration Summary Models, CLI, And Project Completion Integration

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/cli.py`
- Modify: `src/mingli_engine/project_completion.py`
- Modify: `tests/unit/test_domain_calibration_release.py`
- Modify: `tests/unit/test_project_completion.py`
- Modify: `tests/contract/test_project_completion_cli_contract.py`

- [ ] **Step 1: Write failing summary and CLI tests**

Append to `tests/unit/test_domain_calibration_release.py`:

```python
from dataclasses import asdict

from mingli_engine.domain_calibration_release import build_domain_calibration_summary
from mingli_engine.models import DomainCalibrationReleaseSummary


def test_domain_calibration_summary_is_public_serializable_and_blocked_pre_version() -> None:
    summary = build_domain_calibration_summary(
        packaging=_verified_packaging("0.1.0"),
        application_contract_status="passed",
        privacy_status="passed",
        documentation_status="passed",
        compatibility_status="passed",
    )

    assert isinstance(summary, DomainCalibrationReleaseSummary)
    payload = asdict(summary)
    assert payload["release_id"] == "domain_calibration_v1"
    assert payload["release_status"] == "blocked"
    assert payload["application_version"] == "0.2.0"
    assert payload["installed_distribution_version"] == "0.1.0"
    assert payload["claim_boundary"] == RELEASE_CLAIM_BOUNDARY
    assert "final calibration baseline is missing" in payload["blockers"]
    assert payload["metrics"]["assertion_count"] == 43
    assert payload["checks"]["version_set"] == "failed"
```

Append to `tests/contract/test_project_completion_cli_contract.py`:

```python

def test_domain_calibration_summary_cli_outputs_blocked_pre_version_packet():
    result = _run_cli("domain-calibration-summary")

    assert result.returncode == 4
    payload = json.loads(result.stdout)
    assert payload["release_id"] == "domain_calibration_v1"
    assert payload["release_status"] == "blocked"
    assert payload["application_version"] == "0.2.0"
    assert payload["installed_distribution_version"] == "0.1.0"
    assert payload["checks"]["version_set"] == "failed"
    assert payload["next_action"] == "complete_task16_final_baseline_and_final_wheel"
```

- [ ] **Step 2: Run tests and confirm red**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py tests/contract/test_project_completion_cli_contract.py::test_domain_calibration_summary_cli_outputs_blocked_pre_version_packet -q -p no:cacheprovider
```

Expected: FAIL with `ImportError` for `DomainCalibrationReleaseSummary` or CLI parser error for unknown command `domain-calibration-summary`.

- [ ] **Step 3: Add public summary models**

Append to the release-summary section of `src/mingli_engine/models.py`:

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
```

- [ ] **Step 4: Add summary builder**

Add to `src/mingli_engine/domain_calibration_release.py`:

```python
from dataclasses import asdict

from mingli_engine.domain_calibration import (
    build_candidate_metric_snapshot,
    build_candidate_version_set,
    execute_candidate_calibration,
)
from mingli_engine.models import DomainCalibrationReleaseSummary
from mingli_engine.packaging_validation import build_packaging_verification


def _metric_payload(snapshot: MetricSnapshotV1) -> dict[str, object]:
    return {
        "assertion_count": snapshot.assertion_count,
        "determinism_rate": snapshot.determinism_rate,
        "pillar_agreement_rate": snapshot.pillar_agreement_rate,
        "evidence_trace_completeness_rate": snapshot.evidence_trace_completeness_rate,
        "rule_trace_completeness_rate": snapshot.rule_trace_completeness_rate,
        "adjudication_coverage_rate": snapshot.adjudication_coverage_rate,
        "unsupported_computed_count": snapshot.unsupported_computed_count,
        "dependency_bypass_count": snapshot.dependency_bypass_count,
        "school_disagreement_recall": snapshot.school_disagreement_recall,
        "silent_school_collapse_count": snapshot.silent_school_collapse_count,
        "mandatory_abstention_rate": snapshot.mandatory_abstention_rate,
        "reviewer_raw_agreement": snapshot.reviewer_raw_agreement,
        "reviewer_stratum_agreement": snapshot.reviewer_stratum_agreement,
        "weighted_kappa": snapshot.weighted_kappa,
        "jaccard_agreement": snapshot.jaccard_agreement,
        "adjudicated_engine_match": snapshot.adjudicated_engine_match,
        "safety_critical_exact_match": snapshot.safety_critical_exact_match,
    }


def build_domain_calibration_summary(
    *,
    packaging: PackagingVerification | None = None,
    application_contract_status: str = "passed",
    privacy_status: str = "passed",
    documentation_status: str = "failed",
    compatibility_status: str = "passed",
    baseline: MetricSnapshotV1 | None = None,
) -> DomainCalibrationReleaseSummary:
    packaging_result = packaging or build_packaging_verification()
    version_set = build_candidate_version_set("0.2.0")
    run = execute_candidate_calibration(version_set)
    repeated = execute_candidate_calibration(version_set)
    snapshot = build_candidate_metric_snapshot(run, repeated, baseline=baseline)
    decision = build_domain_calibration_release_decision(
        snapshot=snapshot,
        baseline=baseline,
        packaging=packaging_result,
        application_contract_status=application_contract_status,
        privacy_status=privacy_status,
        documentation_status=documentation_status,
        compatibility_status=compatibility_status,
    )
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
    )
```

- [ ] **Step 5: Add CLI command**

Modify `src/mingli_engine/cli.py` imports:

```python
from mingli_engine.domain_calibration_release import (
    build_domain_calibration_summary,
)
```

Add handler near `_report_release_summary`:

```python
def _domain_calibration_summary(args: argparse.Namespace) -> int:
    summary = build_domain_calibration_summary()
    _write_json(summary)
    return 4 if summary.release_status == "blocked" else 0
```

Add parser registration:

```python
    domain_calibration_parser = subparsers.add_parser("domain-calibration-summary")
    domain_calibration_parser.set_defaults(handler=_domain_calibration_summary)
```

- [ ] **Step 6: Integrate project completion without changing formal counts**

Modify `src/mingli_engine/project_completion.py` imports:

```python
from mingli_engine.domain_calibration_release import (
    build_domain_calibration_summary,
)
```

In `build_project_completion_summary`, add the explicit opt-in parameter:

```python
def build_project_completion_summary(
    *,
    specs_dir: Path | None = None,
    docs_dir: Path | None = None,
    calculation_checks: dict[str, str] | None = None,
    acceptance_summary: ReportAcceptanceSummary | None = None,
    include_domain_calibration_release: bool = False,
) -> ProjectCompletionSummary:
```

Compute calibration summary after `release_ready` only when the caller opts in:

```python
    domain_calibration = None
    domain_calibration_ready = False
    if include_domain_calibration_release:
        try:
            domain_calibration = build_domain_calibration_summary()
            domain_calibration_ready = (
                domain_calibration.release_status in {"ready", "ready_with_guardrails"}
            )
        except Exception:
            domain_calibration = None
            domain_calibration_ready = False
```

Add the check without changing `EXPECTED_FEATURE_IDS` yet:

```python
    if include_domain_calibration_release:
        completion_checks["domain_calibration_release"] = (
            PASS if domain_calibration_ready else FAIL
        )
```

The default remains `False` until Task 17 formal closure, so existing project-completion tests preserve the historical 17-feature baseline during Tasks 15 and 16.

- [ ] **Step 7: Run focused tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py tests/contract/test_project_completion_cli_contract.py -q -p no:cacheprovider
```

Expected: PASS. Existing project-completion CLI remains green, and `domain-calibration-summary` returns blocked with exit code 4 before Task 16.

- [ ] **Step 8: Run focused regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py tests/unit/test_project_completion.py tests/contract/test_project_completion_cli_contract.py tests/integration/test_domain_calibration_pipeline.py -q -p no:cacheprovider
uv run --frozen --with mypy==1.17.1 python -m mypy src/mingli_engine/models.py src/mingli_engine/cli.py src/mingli_engine/project_completion.py src/mingli_engine/domain_calibration_release.py --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check src/mingli_engine/models.py src/mingli_engine/cli.py src/mingli_engine/project_completion.py src/mingli_engine/domain_calibration_release.py tests/unit/test_domain_calibration_release.py tests/contract/test_project_completion_cli_contract.py
```

Expected: pytest PASS, mypy reports no issues, Ruff reports no findings.

- [ ] **Step 9: Commit**

```powershell
git add src/mingli_engine/models.py src/mingli_engine/cli.py src/mingli_engine/project_completion.py src/mingli_engine/domain_calibration_release.py tests/unit/test_domain_calibration_release.py tests/unit/test_project_completion.py tests/contract/test_project_completion_cli_contract.py
git commit -m "feat: expose calibrated release summary"
```

Expected: commit created without staging Feature 020 files.

## Task 3: Add Installed Real-Use And Non-Version Release Gates

**Files:**
- Create: `tests/integration/test_installed_real_use.py`
- Modify: `src/mingli_engine/domain_calibration_release.py`
- Modify: `tests/unit/test_domain_calibration_release.py`

- [ ] **Step 1: Write failing installed real-use tests**

Create `tests/integration/test_installed_real_use.py`:

```python
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest


pytest_plugins = ("tests.contract.test_wheel_runtime_assets",)

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def installed_target(
    tmp_path_factory: pytest.TempPathFactory,
    built_wheel: Path,
) -> Path:
    work_dir = tmp_path_factory.mktemp("installed-real-use")
    target = work_dir / "target"
    target.mkdir()
    completed = subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--offline",
            "--target",
            str(target),
            "--no-deps",
            str(built_wheel),
        ],
        cwd=work_dir,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    return target


def _run_installed(target: Path, cwd: Path, script: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(target)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=cwd,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        timeout=30,
    )


def test_installed_real_use_and_calibration_summary_are_source_isolated(
    installed_target: Path,
    tmp_path: Path,
) -> None:
    script = dedent(
        """
        import json
        from pathlib import Path
        import sys

        from mingli_engine.application_service import handle_real_use_json
        from mingli_engine.domain_calibration_release import build_domain_calibration_summary

        request = {
            "authorization": {"attested": True, "subject_relation": "self"},
            "operation": "analysis",
            "options": {"include_profile_in_report": False, "report_format": None},
            "profile": {
                "birth_date": "1996-12-15",
                "birth_time": "09:30",
                "birthplace": "Synthetic Installed Place",
                "calendar_type": "gregorian",
                "focus_topic": "installed real use",
                "gender": "unknown",
            },
            "request_id": "installed-analysis-001",
            "schema_version": "real-use-request-v1",
        }
        response = json.loads(handle_real_use_json(json.dumps(
            request,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")))
        summary = build_domain_calibration_summary()
        module_files = sorted(
            str(Path(module.__file__).resolve())
            for name, module in sys.modules.items()
            if (name == "mingli_engine" or name.startswith("mingli_engine."))
            and getattr(module, "__file__", None)
        )
        print(json.dumps({
            "response_status": response["status"],
            "summary_status": summary.release_status,
            "installed_distribution_version": summary.installed_distribution_version,
            "source_isolated": summary.source_isolated,
            "module_files": module_files,
        }, sort_keys=True))
        """
    )

    completed = _run_installed(installed_target, tmp_path, script)

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    payload = json.loads(completed.stdout)
    assert payload["response_status"] == "ok"
    assert payload["summary_status"] == "blocked"
    assert payload["installed_distribution_version"] == "0.1.0"
    assert payload["source_isolated"] is True
    assert all(Path(path).is_relative_to(installed_target) for path in payload["module_files"])
    assert all(not Path(path).is_relative_to(REPO_ROOT) for path in payload["module_files"])
    assert list(tmp_path.iterdir()) == []
```

- [ ] **Step 2: Run installed test and confirm red**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/integration/test_installed_real_use.py -q -p no:cacheprovider
```

Expected before Task 2 implementation: FAIL because `domain_calibration_summary` is unavailable from installed package. Expected after Task 2: PASS while release remains blocked by version/final-baseline gates.

- [ ] **Step 3: Add documentation/non-version status inputs**

Extend `build_domain_calibration_summary()` call sites to accept real statuses from current verification modules when available:

```python
def build_domain_calibration_summary(
    *,
    packaging: PackagingVerification | None = None,
    application_contract_status: str | None = None,
    privacy_status: str | None = None,
    documentation_status: str = "passed",
    compatibility_status: str = "passed",
    baseline: MetricSnapshotV1 | None = None,
) -> DomainCalibrationReleaseSummary:
    from mingli_engine.application_validation import build_application_verification

    verification = build_application_verification()
    resolved_application = application_contract_status or verification.overall_status
    resolved_privacy = privacy_status or (
        "passed"
        if verification.overall_status == "passed"
        else "failed"
    )
```

Use `resolved_application` and `resolved_privacy` in the decision builder.

- [ ] **Step 4: Run focused installed and release tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py tests/integration/test_installed_real_use.py -q -p no:cacheprovider
```

Expected: PASS. Release summary is blocked only by version/final-baseline gates when non-version checks pass.

- [ ] **Step 5: Run focused regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py tests/integration/test_installed_real_use.py tests/contract/test_wheel_runtime_assets.py tests/integration/test_installed_package_baseline.py tests/contract/test_real_use_cli_contract.py -q -p no:cacheprovider
uv run --frozen --with mypy==1.17.1 python -m mypy src/mingli_engine/domain_calibration_release.py src/mingli_engine/application_validation.py --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check src/mingli_engine/domain_calibration_release.py tests/unit/test_domain_calibration_release.py tests/integration/test_installed_real_use.py
```

Expected: pytest PASS, mypy reports no issues, Ruff reports no findings.

- [ ] **Step 6: Commit**

```powershell
git add src/mingli_engine/domain_calibration_release.py tests/unit/test_domain_calibration_release.py tests/integration/test_installed_real_use.py
git commit -m "test: verify installed calibrated application gates"
```

Expected: commit created with Task 15 installed-gate coverage.

## Task 4: Add Red Final-Release Gate Before Version Advance

**Files:**
- Modify: `tests/contract/test_wheel_runtime_assets.py`
- Modify: `tests/integration/test_installed_real_use.py`
- Modify: `tests/unit/test_domain_calibration_release.py`

- [ ] **Step 1: Write final-release red tests**

Append to `tests/unit/test_domain_calibration_release.py`:

```python
from mingli_engine.domain_calibration_release import load_final_calibration_baseline


def test_final_baseline_is_missing_before_task16() -> None:
    with pytest.raises(CalibrationProtocolError, match="final calibration baseline is missing"):
        load_final_calibration_baseline()
```

Append to `tests/integration/test_installed_real_use.py`:

```python

def test_pre_baseline_installation_cannot_be_final_release_evidence(
    installed_target: Path,
    tmp_path: Path,
) -> None:
    script = dedent(
        """
        import json
        from mingli_engine.domain_calibration_release import build_domain_calibration_summary

        summary = build_domain_calibration_summary()
        print(json.dumps({
            "release_status": summary.release_status,
            "installed_distribution_version": summary.installed_distribution_version,
            "checks": summary.checks,
            "blockers": summary.blockers,
        }, sort_keys=True))
        """
    )
    completed = _run_installed(installed_target, tmp_path, script)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["release_status"] == "blocked"
    assert payload["installed_distribution_version"] == "0.1.0"
    assert payload["checks"]["version_set"] == "failed"
    assert payload["checks"]["final_baseline"] == "failed"
```

Append to `tests/contract/test_wheel_runtime_assets.py`:

```python

def test_final_release_requires_0_2_0_wheel_after_frozen_baseline(built_wheel: Path) -> None:
    assert "0.2.0" in built_wheel.name
    with ZipFile(built_wheel) as wheel:
        names = set(wheel.namelist())
    assert "mingli_engine/data/domain_calibration/calibration_baseline.json" in names
```

- [ ] **Step 2: Run and confirm exact red**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py::test_final_baseline_is_missing_before_task16 tests/integration/test_installed_real_use.py::test_pre_baseline_installation_cannot_be_final_release_evidence tests/contract/test_wheel_runtime_assets.py::test_final_release_requires_0_2_0_wheel_after_frozen_baseline -q -p no:cacheprovider
```

Expected: first two tests PASS as red-gate assertions; wheel test FAIL because current wheel is `0.1.0` and has no `calibration_baseline.json`. This is the approved red gate before version advance.

- [ ] **Step 3: Do not change version yet**

No production code change in this task. The red gate documents the exact release blocker.

- [ ] **Step 4: Commit**

```powershell
git add tests/unit/test_domain_calibration_release.py tests/integration/test_installed_real_use.py tests/contract/test_wheel_runtime_assets.py
git commit -m "test: lock final calibrated release red gate"
```

Expected: commit created while `pyproject.toml` still says `version = "0.1.0"`.

## Task 5: Advance To 0.2.0, Freeze Final Baseline From Pre-Baseline Wheel, Then Rebuild Final Wheel

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/mingli_engine/domain_calibration_release.py`
- Create: `src/mingli_engine/data/domain_calibration/calibration_baseline.json`
- Modify: `tests/contract/test_wheel_runtime_assets.py`
- Modify: `tests/integration/test_installed_package_baseline.py`
- Modify: `tests/integration/test_installed_real_use.py`
- Modify: `tests/unit/test_domain_calibration_release.py`

- [ ] **Step 1: Add controlled final baseline writer tests**

Append to `tests/unit/test_domain_calibration_release.py`:

```python
from pathlib import Path

from mingli_engine.domain_calibration import load_calibration_file
from mingli_engine.domain_calibration_release import freeze_final_calibration_baseline


def test_controlled_writer_freezes_only_final_0_2_0_snapshot(tmp_path: Path) -> None:
    snapshot = _snapshot()
    target = tmp_path / "calibration_baseline.json"

    freeze_final_calibration_baseline(target, snapshot)

    loaded = load_calibration_file(target, MetricSnapshotV1)
    assert loaded.records == (snapshot,)
    assert loaded.schema_version == "domain-calibration-file-v1"
    assert loaded.contains_real_personal_data is False


def test_controlled_writer_rejects_nonfinal_name_and_wrong_version(tmp_path: Path) -> None:
    snapshot = _snapshot()
    with pytest.raises(CalibrationProtocolError, match="final baseline target name"):
        freeze_final_calibration_baseline(tmp_path / "calibration_baseline_candidate.json", snapshot)

    wrong_version = replace(
        snapshot,
        version_set=replace(snapshot.version_set, application_version="0.1.0"),
    )
    with pytest.raises(CalibrationProtocolError, match="final baseline requires 0.2.0"):
        freeze_final_calibration_baseline(tmp_path / "calibration_baseline.json", wrong_version)
```

- [ ] **Step 2: Run writer tests and confirm red**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py::test_controlled_writer_freezes_only_final_0_2_0_snapshot tests/unit/test_domain_calibration_release.py::test_controlled_writer_rejects_nonfinal_name_and_wrong_version -q -p no:cacheprovider
```

Expected: FAIL with `ImportError` or missing `freeze_final_calibration_baseline`.

- [ ] **Step 3: Implement controlled final baseline writer**

Add to `src/mingli_engine/domain_calibration_release.py`:

```python
from pathlib import Path

from mingli_engine.domain_calibration import (
    CalibrationProtocolError,
    canonical_json_bytes,
    load_calibration_file,
    records_payload_sha256,
)


def freeze_final_calibration_baseline(
    target: str | Path,
    snapshot: MetricSnapshotV1,
) -> None:
    if not isinstance(snapshot, MetricSnapshotV1):
        raise TypeError("snapshot must be MetricSnapshotV1")
    if snapshot.version_set.application_version != "0.2.0":
        raise CalibrationProtocolError("final baseline requires 0.2.0")
    path = Path(target)
    if path.name != "calibration_baseline.json":
        raise CalibrationProtocolError("final baseline target name is invalid")
    if not path.parent.is_dir():
        raise CalibrationProtocolError("final baseline target parent is unavailable")
    envelope = {
        "schema_version": "domain-calibration-file-v1",
        "suite_version": "domain-calibration-suite-v1",
        "generated_from": (snapshot.corpus_sha256,),
        "contains_real_personal_data": False,
        "payload_sha256": records_payload_sha256((snapshot,)),
        "records": (snapshot,),
    }
    path.write_bytes(canonical_json_bytes(envelope))


def load_final_calibration_baseline(
    path: str | Path = "src/mingli_engine/data/domain_calibration/calibration_baseline.json",
) -> MetricSnapshotV1:
    baseline_path = Path(path)
    if not baseline_path.exists():
        raise CalibrationProtocolError("final calibration baseline is missing")
    envelope = load_calibration_file(baseline_path, MetricSnapshotV1)
    if len(envelope.records) != 1:
        raise CalibrationProtocolError("final calibration baseline must contain one snapshot")
    return envelope.records[0]
```

- [ ] **Step 4: Verify writer tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py -q -p no:cacheprovider
```

Expected: PASS except tests that intentionally require the final tracked baseline before it is generated. If `test_final_baseline_is_missing_before_task16` still exists, replace it in this task with a final-baseline-present assertion after Step 8.

- [ ] **Step 5: Confirm non-version gates before version edit**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_release.py tests/integration/test_installed_real_use.py tests/contract/test_wheel_runtime_assets.py tests/integration/test_installed_package_baseline.py tests/integration/test_domain_calibration_pipeline.py -q -p no:cacheprovider
```

Expected: only the final-release test requiring a 0.2.0 post-baseline wheel fails. Non-version gates pass.

- [ ] **Step 6: Advance package version to 0.2.0**

Modify `pyproject.toml`:

```toml
[project]
name = "mingli-engine"
version = "0.2.0"
```

Do not modify `uv.lock`.

- [ ] **Step 7: Build and install pre-baseline wheel only for final calibration**

```powershell
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
uv build --frozen --offline --wheel --out-dir dist
$preBaselineWheel = Get-ChildItem dist\*.whl | Select-Object -First 1
$preBaselineTarget = New-Item -ItemType Directory -Path (Join-Path $env:TEMP "mingli-019-prebaseline")
python -m pip install --no-index --no-deps --target $preBaselineTarget.FullName $preBaselineWheel.FullName
```

Expected: exactly one `mingli_engine-0.2.0-*.whl` exists in `dist/`, and it is installed to a temporary pre-baseline target. This wheel is not release evidence.

- [ ] **Step 8: Execute final calibration from pre-baseline installation and freeze baseline**

Run this from the closure worktree root:

```powershell
$script = @'
from pathlib import Path
import sys

from mingli_engine.domain_calibration import (
    build_candidate_metric_snapshot,
    build_candidate_version_set,
    execute_candidate_calibration,
)
from mingli_engine.domain_calibration_release import freeze_final_calibration_baseline

version_set = build_candidate_version_set("0.2.0")
run = execute_candidate_calibration(version_set)
repeated = execute_candidate_calibration(version_set)
snapshot = build_candidate_metric_snapshot(run, repeated)
target = Path(sys.argv[1])
freeze_final_calibration_baseline(target, snapshot)
print(snapshot.snapshot_id)
'@
$env:PYTHONPATH=$preBaselineTarget.FullName
$env:PYTHONDONTWRITEBYTECODE='1'
python -c $script "src/mingli_engine/data/domain_calibration/calibration_baseline.json"
```

Expected: `src/mingli_engine/data/domain_calibration/calibration_baseline.json` is created, contains one `MetricSnapshotV1`, and its `version_set.application_version` is `0.2.0`.

- [ ] **Step 9: Discard pre-baseline wheel evidence**

```powershell
Remove-Item -Recurse -Force dist
```

Expected: `dist/` is removed. The pre-baseline wheel is not used by any final verification step.

- [ ] **Step 10: Build post-baseline final wheel**

```powershell
uv build --frozen --offline --wheel --out-dir dist
$finalWheel = Get-ChildItem dist\*.whl | Select-Object -First 1
```

Expected: exactly one `mingli_engine-0.2.0-*.whl` exists and includes the frozen `mingli_engine/data/domain_calibration/calibration_baseline.json`.

- [ ] **Step 11: Update installed verifier expectations to 0.2.0**

Modify `tests/integration/test_installed_package_baseline.py` expected packaging result:

```python
assert result == {
    "asset_sha256": _source_asset_hashes(),
    "distribution_version": "0.2.0",
    "overall_status": "verified",
    "source_isolated": True,
}
```

Modify `tests/contract/test_wheel_runtime_assets.py` fake distribution defaults only where tests model installed metadata for the current package:

```python
version: str | None = "0.2.0",
dist_info = "mingli_engine-0.2.0.dist-info"
```

- [ ] **Step 12: Update installed release tests to require final evidence**

Replace the pre-baseline installed test expectation in `tests/integration/test_installed_real_use.py` with:

```python
def test_final_installed_wheel_supplies_release_evidence(
    installed_target: Path,
    tmp_path: Path,
) -> None:
    script = dedent(
        """
        import json
        from mingli_engine.domain_calibration import (
            build_candidate_metric_snapshot,
            build_candidate_version_set,
            execute_candidate_calibration,
            validate_version_set_equality,
        )
        from mingli_engine.domain_calibration_release import (
            build_domain_calibration_release_decision,
            build_domain_calibration_summary,
            load_final_calibration_baseline,
        )
        from mingli_engine.packaging_validation import build_packaging_verification

        version_set = build_candidate_version_set("0.2.0")
        run = execute_candidate_calibration(version_set)
        repeated = execute_candidate_calibration(version_set)
        snapshot = build_candidate_metric_snapshot(run, repeated, baseline=load_final_calibration_baseline())
        decision = build_domain_calibration_release_decision(
            snapshot=snapshot,
            baseline=load_final_calibration_baseline(),
            packaging=build_packaging_verification(),
            application_contract_status="passed",
            privacy_status="passed",
            documentation_status="passed",
            compatibility_status="passed",
        )
        validate_version_set_equality(run, load_final_calibration_baseline(), decision)
        summary = build_domain_calibration_summary(baseline=load_final_calibration_baseline())
        print(json.dumps({
            "decision_status": decision.release_status,
            "summary_status": summary.release_status,
            "distribution_version": summary.installed_distribution_version,
            "source_isolated": summary.source_isolated,
            "version_set": summary.version_set,
        }, sort_keys=True))
        """
    )
    completed = _run_installed(installed_target, tmp_path, script)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["decision_status"] == "ready_with_guardrails"
    assert payload["summary_status"] == "ready_with_guardrails"
    assert payload["distribution_version"] == "0.2.0"
    assert payload["source_isolated"] is True
    assert payload["version_set"]["application_version"] == "0.2.0"
```

- [ ] **Step 13: Run final wheel focused verification**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/contract/test_wheel_runtime_assets.py tests/integration/test_installed_package_baseline.py tests/integration/test_installed_real_use.py tests/unit/test_domain_calibration_release.py -q -p no:cacheprovider
```

Expected: PASS. Evidence comes from a post-baseline final wheel installed into fresh test targets.

- [ ] **Step 14: Run focused type/lint**

```powershell
uv run --frozen --with mypy==1.17.1 python -m mypy src/mingli_engine/domain_calibration.py src/mingli_engine/domain_calibration_release.py src/mingli_engine/models.py src/mingli_engine/cli.py --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check src/mingli_engine/domain_calibration.py src/mingli_engine/domain_calibration_release.py src/mingli_engine/models.py src/mingli_engine/cli.py tests/unit/test_domain_calibration_release.py tests/integration/test_installed_real_use.py tests/contract/test_wheel_runtime_assets.py tests/integration/test_installed_package_baseline.py
```

Expected: mypy reports no issues, Ruff reports no findings.

- [ ] **Step 15: Commit**

```powershell
git add pyproject.toml src/mingli_engine/domain_calibration_release.py src/mingli_engine/data/domain_calibration/calibration_baseline.json tests/unit/test_domain_calibration_release.py tests/integration/test_installed_real_use.py tests/contract/test_wheel_runtime_assets.py tests/integration/test_installed_package_baseline.py
git commit -m "release: package calibrated application v1"
```

Expected: commit created with 0.2.0 version, final baseline, final-wheel tests, and release writer. The committed `dist/` directory is not staged.

## Task 6: Close Formal Spec Kit Governance And Documentation

**Files:**
- Move: `specs/_drafts/019-bazi-domain-validation-and-application-v1/` to `specs/019-bazi-domain-validation-and-application-v1/`
- Modify: `.specify/feature.json`
- Modify: `src/mingli_engine/project_completion.py`
- Modify: `tests/unit/test_project_completion.py`
- Modify: `tests/contract/test_project_completion_cli_contract.py`
- Modify: `docs/classical_sources/README.md`
- Create: `docs/classical_sources/domain_calibration.md`
- Create: `docs/classical_sources/real_use_application.md`

- [ ] **Step 1: Write failing formal closure tests**

Modify `tests/unit/test_project_completion.py` top-level expected assertions:

```python
def test_project_completion_summary_certifies_local_delivery():
    summary = build_project_completion_summary()

    assert summary.baseline_id == "project_completion_v2_019"
    assert summary.completion_status == "complete_with_guardrails"
    assert summary.feature_count == 18
    assert summary.spec_count == 18
    assert summary.plan_count == 18
    assert _feature(summary, "019-bazi-domain-validation-and-application-v1").artifact_status == "complete"
    assert _feature(summary, "019-bazi-domain-validation-and-application-v1").task_tracking_status == "complete"
    assert summary.release_id == "domain_calibration_v1"
    assert summary.release_status == "ready_with_guardrails"
    assert summary.remaining_local_blockers == []
```

Append:

```python
def test_formal_019_has_no_draft_copy_and_documents_claim_boundary():
    formal = REPO_ROOT / "specs" / "019-bazi-domain-validation-and-application-v1"
    draft = REPO_ROOT / "specs" / "_drafts" / "019-bazi-domain-validation-and-application-v1"
    assert formal.is_dir()
    assert not draft.exists()
    for name in (
        "spec.md",
        "plan.md",
        "research.md",
        "data-model.md",
        "quickstart.md",
        "tasks.md",
    ):
        assert (formal / name).is_file()
    text = (formal / "quickstart.md").read_text(encoding="utf-8")
    assert "agent-independent" in text
    assert "not scientific" in text
    assert "true solar time" in text
    assert "Birth-profile and report data are not stored by the engine" in text
```

Modify `tests/contract/test_project_completion_cli_contract.py` expected payload:

```python
assert payload["baseline_id"] == "project_completion_v2_019"
assert payload["feature_count"] == 18
assert payload["release_id"] == "domain_calibration_v1"
assert payload["release_status"] == "ready_with_guardrails"
```

- [ ] **Step 2: Run formal closure tests and confirm red**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_project_completion.py tests/contract/test_project_completion_cli_contract.py -q -p no:cacheprovider
```

Expected: FAIL because 019 remains under `_drafts`, project-completion counts still expect 17 features, and docs do not yet include 019 closure pages.

- [ ] **Step 3: Move Spec Kit to formal path**

```powershell
New-Item -ItemType Directory -Force specs | Out-Null
Move-Item -LiteralPath specs/_drafts/019-bazi-domain-validation-and-application-v1 -Destination specs/019-bazi-domain-validation-and-application-v1
```

Expected: formal path exists and draft path no longer exists.

- [ ] **Step 4: Update `.specify/feature.json`**

Set the feature directory to:

```json
{
  "feature_directory": "specs/019-bazi-domain-validation-and-application-v1"
}
```

Preserve any additional existing keys exactly if the file already contains them.

- [ ] **Step 5: Close 019 tasks and checklists**

In `specs/019-bazi-domain-validation-and-application-v1/tasks.md`, replace every `- [ ]` with `- [X]` for T001 through T090. In `specs/019-bazi-domain-validation-and-application-v1/checklists/requirements.md`, replace every open requirement item with checked `- [X]`.

Expected: no unchecked `- [ ]` remains in the formal 019 Spec Kit.

- [ ] **Step 6: Add documentation**

Create `docs/classical_sources/domain_calibration.md`:

```markdown
# Domain Calibration V1

Feature 019 publishes an internal, agent-independent traditional-method conformance calibration for deterministic structural Bazi outputs. The calibration compares packaged synthetic cases, blinded reviewer records, adjudication, and engine outputs against traceable rule and evidence IDs.

The permitted claim is independent agent-based domain-conformance calibration of deterministic structural outputs against tracked traditional-method evidence and blinded reviewer labels. It is not scientific validation, causal validation, predictive validation, real-world outcome validation, human expert review, or universal school agreement.

Reviewer records use `reviewer_kind=agent_independent`. The blindness is procedural: reviewers received canonical packet bytes without tools, filesystem reads, peer labels, or engine output. This is not an operating-system sandbox claim.

The final release evidence is valid only when the final installed wheel supplies the resource SHA map, source isolation result, calibration summary, release decision, and exact version-set equality for final run, final baseline, and release decision.
```

Create `docs/classical_sources/real_use_application.md`:

```markdown
# Real Use Application V1

Feature 019 adds the local `real-use` application boundary for synthetic or authorized use. Requests use `real-use-request-v1`; responses use `real-use-response-v1`; authorization and safety run before calculation.

Birth-profile and report data are not stored by the engine. A terminal, caller, shell redirection, or host operating system may retain output.

The application does not provide HTTP, browser UI, database storage, external chart input, geographic timezone lookup, true-solar-time calculation, scientific prediction, or professional advice. JSON, Markdown, and HTML reports preserve source and evidence traceability while using conditional and uncertainty language.
```

Update `docs/classical_sources/README.md` by adding links:

```markdown
- [Real Use Application V1](real_use_application.md)
- [Domain Calibration V1](domain_calibration.md)
```

- [ ] **Step 7: Update project completion baseline**

In `src/mingli_engine/project_completion.py`, update the existing constants by editing the literal values:

```python
BASELINE_ID = "project_completion_v2_019"
EXPECTED_FEATURE_IDS = (
    "001-ingestion-foundation",
    "002-source-intake",
    "003-source-registry",
    "004-markdown-normalization",
    "005-materials-audit",
    "006-classical-sources",
    "007-evidence-corpus",
    "008-formal-rules",
    "009-bazi-calculation",
    "010-html-visual-report",
    "011-report-acceptance",
    "012-report-release",
    "013-source-window",
    "014-learning-queue",
    "015-queue-refresh",
    "016-report-readiness",
    "017-learning-reference-curation",
    "019-bazi-domain-validation-and-application-v1",
)
```

Replace release integration to use domain calibration release at closure:

```python
from mingli_engine.domain_calibration_release import build_domain_calibration_summary

domain_calibration = build_domain_calibration_summary(
    baseline=load_final_calibration_baseline(),
)
release_ready = domain_calibration.release_status in {"ready", "ready_with_guardrails"}
```

Set returned `release_id`, `release_status`, and `action_track_count` from the domain calibration summary in the 019 closure branch.

- [ ] **Step 8: Run closure tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_project_completion.py tests/contract/test_project_completion_cli_contract.py tests/unit/test_domain_calibration_release.py -q -p no:cacheprovider
```

Expected: PASS. Formal 019 appears exactly once, no draft copy exists, project-completion release status is `ready_with_guardrails`, and no Feature 020 path is referenced.

- [ ] **Step 9: Commit**

```powershell
git add specs/019-bazi-domain-validation-and-application-v1 .specify/feature.json docs/classical_sources/README.md docs/classical_sources/domain_calibration.md docs/classical_sources/real_use_application.md src/mingli_engine/project_completion.py tests/unit/test_project_completion.py tests/contract/test_project_completion_cli_contract.py
git add -u specs/_drafts/019-bazi-domain-validation-and-application-v1
git commit -m "docs: complete calibrated application v1 governance"
```

Expected: commit created with formal governance closure only.

## Task 7: Final Full Verification, Audit, And Fresh Review

**Files:**
- Read all changed Feature 019 files
- Modify only if Critical or Important final review findings require fixes

- [ ] **Step 1: Run complete pytest suite**

Use a 900000 ms controller timeout:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest -q -p no:cacheprovider
```

Expected: PASS for the full repository test suite.

- [ ] **Step 2: Run type, lint, and release commands**

```powershell
uv run --frozen --with mypy==1.17.1 python -m mypy src/mingli_engine --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check src tests
python -m mingli_engine.cli knowledge-activation-summary
python -m mingli_engine.cli report-acceptance-summary
python -m mingli_engine.cli report-release-summary
python -m mingli_engine.cli domain-calibration-summary
python -m mingli_engine.cli project-completion-summary
```

Expected: mypy reports no issues, Ruff reports no findings, each CLI command exits 0, and both `domain-calibration-summary` and `project-completion-summary` report `ready_with_guardrails` or `complete_with_guardrails` as applicable.

- [ ] **Step 3: Run privacy, package, and repository audit**

```powershell
git diff --check
git status --short
git status --short -- "资料原文" "资料整理" "Markdown" "*.pdf"
Get-ChildItem -Recurse -File -Include *.pdf,*.doc,*.docx,*.xls,*.xlsx,*.ppt,*.pptx | Select-Object -ExpandProperty FullName
Get-ChildItem -Recurse -File tmp,.codex-test-logs -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '(birth.?profile|real.?use|generated.?report|calibration.?run)' } | Select-Object -ExpandProperty FullName
git grep -n -I -E '(199[0-9]-[01][0-9]-[0-3][0-9].*(出生|birth)|真实姓名|身份证|手机号)' -- ':!tests/fixtures/**' ':!docs/superpowers/**'
```

Expected: `git diff --check` is clean; raw-material status is empty; Office/PDF scan produces no new runtime artifact requiring review; temporary privacy scan is empty; grep finds no unapproved real personal data outside allowed fixtures/docs.

- [ ] **Step 4: Inspect final wheel manifest**

```powershell
$script = @'
from pathlib import Path
from zipfile import ZipFile

wheels = sorted(Path("dist").glob("mingli_engine-0.2.0-*.whl"))
assert len(wheels) == 1, wheels
with ZipFile(wheels[0]) as wheel:
    names = set(wheel.namelist())
required = {
    "mingli_engine/data/domain_calibration/calibration_baseline.json",
    "mingli_engine/data/domain_calibration/calibration_assertions.json",
    "mingli_engine/data/domain_calibration/adjudication.json",
    "mingli_engine/data/calculation/school_profiles.json",
    "mingli_engine/data/classical_sources/evidence_units.json",
}
missing = sorted(required - names)
assert not missing, missing
print(wheels[0])
'@
$script | python -
```

Expected: prints the single final 0.2.0 wheel path and no assertion fails.

- [ ] **Step 5: Run fresh final review**

Review the complete closure commit range from Task 15 through Task 17:

```powershell
git log --oneline d7d05b1..HEAD
git diff --stat d7d05b1..HEAD
```

Expected: changes are limited to Feature 019 closure files and contain no Feature 020 files.

Perform a fresh whole-feature review covering:

- `src/mingli_engine/domain_calibration.py`
- `src/mingli_engine/domain_calibration_models.py`
- `src/mingli_engine/domain_calibration_release.py`
- `src/mingli_engine/application_*`
- `src/mingli_engine/packaging_validation.py`
- `src/mingli_engine/cli.py`
- `src/mingli_engine/project_completion.py`
- `src/mingli_engine/data/domain_calibration/*.json`
- `tests/unit/test_domain_calibration_release.py`
- `tests/integration/test_domain_calibration_pipeline.py`
- `tests/integration/test_installed_real_use.py`
- `tests/contract/test_wheel_runtime_assets.py`
- `tests/integration/test_installed_package_baseline.py`
- `specs/019-bazi-domain-validation-and-application-v1/**`
- `docs/classical_sources/domain_calibration.md`
- `docs/classical_sources/real_use_application.md`

Expected: no Critical or Important findings. If such findings exist, fix them in the closure worktree, rerun Steps 1-4, and commit the fixes before marking Feature 019 closed.

- [ ] **Step 6: Final commit if review fixes were needed**

If review fixes changed files:

```powershell
git add <review-fix-files>
git commit -m "fix: address calibrated application closure review"
```

Expected: commit created only when review fixes exist.

## Release Sequence Reconciliation Checklist

- Task 14 remains candidate-only and does not write final baseline.
- Task 15 proves deterministic release logic and non-version gates while release can remain blocked.
- Version changes to 0.2.0 only after non-version gates pass.
- Pre-baseline wheel exists only to run fresh final calibration and snapshot.
- Final baseline is frozen only by `freeze_final_calibration_baseline()`.
- Pre-baseline wheel is discarded before final evidence.
- Post-baseline final wheel is rebuilt after `calibration_baseline.json` exists.
- Fresh final installation supplies manifest, calibration summary, release decision, resource SHA map, source isolation, and exact version-set equality.
- Formal Spec Kit closure happens after final release evidence.
- Full tests, type checks, lint, privacy audit, package audit, and fresh final review close the feature.
