# Feature 019 Evidence-Trust Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Feature 019's self-confirming calibration path with a versioned observation pipeline whose values, rule traces, response hashes, and pillar comparisons come only from real application output.

**Architecture:** Work from a new branch based on closure commit `fb8ea64`, leaving both dirty user worktrees untouched. Execute each synthetic fixture once through `handle_real_use_json`, freeze the canonical response, project actual observations through a code-owned registry that cannot access expected labels, then compare the frozen observations with adjudication. Keep historical V1 assets immutable and add one packaged V2 pillar-reference asset.

**Tech Stack:** Python 3.12, frozen dataclasses, standard-library JSON/SHA-256, existing `mingli_engine` V1 application facade, pytest 8.4.1, mypy 1.17.1, Ruff 0.12.11, setuptools/uv wheel tooling.

---

## Execution Rules

- Execute this plan from `E:\命理演绎` initially, then from the isolated worktree created in Task 1.
- Do not modify or stage the existing V2 prototype, raw PDFs, external materials, or the dirty materials-audit changes.
- Use `apply_patch` for source, test, JSON, and documentation edits.
- Commit only the files named by each task.
- Do not generate a release-ready decision, version bump, tag, push, or final baseline in this plan.
- A lower corrected match or trace metric is not a test failure. Fabricated completeness is a failure.

## File Map

**Create**

- `src/mingli_engine/domain_calibration_observations.py`: immutable application snapshots, actual observation models, response validation, and code-owned projectors.
- `src/mingli_engine/data/domain_calibration/verified_pillar_expectations_v2.json`: packaged cross-provider pillar truth for the one V1 provider-agreement fixture.
- `tests/unit/test_domain_calibration_observations.py`: observation-model, parser, projector, and isolation tests.
- `specs/_drafts/019-bazi-domain-validation-and-application-v1/calibration-evidence-integrity-note.md`: historical-evidence limitation and corrected-suite semantics.

**Modify**

- `src/mingli_engine/domain_calibration_models.py`: pillar-reference/result models and response-binding fields on calibration results/runs.
- `src/mingli_engine/domain_calibration.py`: observation integration, injected application runner, real pillar comparison, and corrected metric computation.
- `src/mingli_engine/packaging_validation.py`: exact runtime asset manifest.
- `tests/unit/test_domain_calibration_models.py`: new model invariants and updated run factory.
- `tests/integration/test_domain_calibration_pipeline.py`: replace self-confirming assertions with adversarial evidence tests.
- `tests/unit/test_domain_calibration_release.py`: preserve legacy blocking semantics under truthful metrics.
- `tests/contract/test_wheel_runtime_assets.py`: require the pillar-reference asset in the wheel.
- `specs/_drafts/019-bazi-domain-validation-and-application-v1/contracts/domain-calibration-v1-contract.md`: corrected observation-suite addendum.
- `docs/superpowers/specs/2026-07-18-feature-019-evidence-trust-recovery-design.md`: mark implementation start after the isolated branch is created.

## Task 1: Protect Dirty Work and Create the Isolated Closure Worktree

**Files:**

- No tracked file changes.
- Create ignored worktree directory: `E:\命理演绎\.superpowers\worktrees\019-evidence-trust-closure`

- [ ] **Step 1: Load the required worktree safety instructions**

Read `C:\Users\lei\.codex\superpowers\skills\using-git-worktrees\SKILL.md` completely before running a Git worktree command.

- [ ] **Step 2: Record both dirty worktrees before isolation**

Run:

```powershell
git -C 'E:\命理演绎' status --short --branch
git -C 'E:\命理演绎' diff --name-only
Get-FileHash -Algorithm SHA256 -LiteralPath `
  'E:\命理演绎\src\mingli_engine\domain_calibration_v2.py', `
  'E:\命理演绎\src\mingli_engine\domain_calibration_v2_models.py'
git -C 'E:\mingli-019-closure' status --short --branch
git -C 'E:\mingli-019-closure' diff --name-only
Get-FileHash -Algorithm SHA256 -LiteralPath `
  'E:\mingli-019-closure\pyproject.toml', `
  'E:\mingli-019-closure\src\mingli_engine\materials_audit.py', `
  'E:\mingli-019-closure\tests\unit\test_materials_audit.py'
```

Expected: the main worktree reports only its existing V2 tracked modifications plus untracked V2/material files; the closure worktree reports only its existing materials-audit/build changes. Save the terminal output in the task checkpoint message.

- [ ] **Step 3: Verify the target is safe and absent**

Run:

```powershell
$target = 'E:\命理演绎\.superpowers\worktrees\019-evidence-trust-closure'
if (Test-Path -LiteralPath $target) { throw "worktree target already exists: $target" }
git -C 'E:\命理演绎' show --no-patch --format='%H %s' fb8ea64
git -C 'E:\命理演绎' branch --list 'codex/019-evidence-trust-closure'
git -C 'E:\命理演绎' check-ignore -v '.superpowers/worktrees/019-evidence-trust-closure'
```

Expected: commit `fb8ea64fdbc771ee2b4af17b91b5058851c2ee8b` resolves, the branch list is empty, and `.superpowers/` is ignored.

- [ ] **Step 4: Create the isolated branch and worktree**

Run:

```powershell
git -C 'E:\命理演绎' worktree add `
  -b 'codex/019-evidence-trust-closure' `
  'E:\命理演绎\.superpowers\worktrees\019-evidence-trust-closure' `
  fb8ea64
```

Expected: Git reports a new worktree at `fb8ea64` on `codex/019-evidence-trust-closure`.

- [ ] **Step 5: Bring only the approved design and this plan into the worktree**

Run:

```powershell
$source = 'E:\命理演绎'
$target = 'E:\命理演绎\.superpowers\worktrees\019-evidence-trust-closure'
$designAddCommit = git -C $source log --diff-filter=A -1 --format='%H' -- `
  'docs/superpowers/specs/2026-07-18-feature-019-evidence-trust-recovery-design.md'
$planCommit = git -C $source log -1 --format='%H' -- `
  'docs/superpowers/plans/2026-07-18-feature-019-evidence-trust-recovery.md'
git -C $target cherry-pick $designAddCommit
if ($planCommit -ne $designAddCommit) { git -C $target cherry-pick $planCommit }
git -C $target status --short --branch
```

Expected: the isolated worktree is clean and contains the two recovery documents; no V2 or materials-audit changes appear.

- [ ] **Step 6: Re-run the dirty-worktree inventories**

Repeat Step 2. Expected: the status entries and SHA-256 values match the pre-isolation output exactly.

- [ ] **Step 7: Report the checkpoint**

Tell the user: isolation is complete, both original worktrees are unchanged, release is still unsafe, and no user action is required before Task 2.

## Task 2: Add Corrected Evidence Models and Packaged Pillar Truth

**Files:**

- Modify: `src/mingli_engine/domain_calibration_models.py`
- Modify: `src/mingli_engine/domain_calibration.py`
- Create: `src/mingli_engine/data/domain_calibration/verified_pillar_expectations_v2.json`
- Modify: `tests/unit/test_domain_calibration_models.py`

- [ ] **Step 1: Write failing model tests**

Add these tests to `tests/unit/test_domain_calibration_models.py`:

```python
def test_pillar_expectation_v2_requires_four_ordered_pillars() -> None:
    from mingli_engine.domain_calibration_models import PillarExpectationV2

    item = PillarExpectationV2(
        fixture_id="fixture-calendrical-verified-001",
        source_fixture_id="synthetic_01_19961215_0930",
        source_fixture_sha256="a" * 64,
        expected_pillars=("丙子", "庚子", "丙戌", "癸巳"),
    )
    assert item.expected_pillars == ("丙子", "庚子", "丙戌", "癸巳")
    with pytest.raises(ValueError, match="exactly four"):
        replace(item, expected_pillars=("丙子",))


def test_pillar_comparison_v2_binds_actual_response_hash() -> None:
    from mingli_engine.domain_calibration_models import CalibrationPillarResultV2

    result = CalibrationPillarResultV2(
        fixture_id="fixture-calendrical-verified-001",
        expected_pillars=("丙子", "庚子", "丙戌", "癸巳"),
        actual_pillars=("丙子", "庚子", "丙戌", "癸巳"),
        source_response_sha256="b" * 64,
        matched=True,
    )
    assert result.matched is True
    with pytest.raises(ValueError, match="matched must equal"):
        replace(result, actual_pillars=("甲子", "庚子", "丙戌", "癸巳"))
```

Ensure the test file imports `replace` from `dataclasses` and `pytest`.

- [ ] **Step 2: Run the tests to prove the models are missing**

Run:

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_domain_calibration_models.py `
  -q -p no:cacheprovider
```

Expected: FAIL because `PillarExpectationV2` and `CalibrationPillarResultV2` are not importable.

- [ ] **Step 3: Add the two models**

Add the following immediately before `ExactVersionSet` in `src/mingli_engine/domain_calibration_models.py`:

```python
@dataclass(frozen=True)
class PillarExpectationV2:
    fixture_id: str
    source_fixture_id: str
    source_fixture_sha256: str
    expected_pillars: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_str(self.fixture_id, "fixture_id")
        _require_str(self.source_fixture_id, "source_fixture_id")
        _require_sha256(self.source_fixture_sha256, "source_fixture_sha256")
        pillars = _string_tuple(
            self.expected_pillars,
            "expected_pillars",
            unique=False,
        )
        if len(pillars) != 4:
            raise ValueError("expected_pillars must contain exactly four values")
        object.__setattr__(self, "expected_pillars", pillars)


@dataclass(frozen=True)
class CalibrationPillarResultV2:
    fixture_id: str
    expected_pillars: tuple[str, ...]
    actual_pillars: tuple[str, ...]
    source_response_sha256: str
    matched: bool

    def __post_init__(self) -> None:
        _require_str(self.fixture_id, "fixture_id")
        expected = _string_tuple(
            self.expected_pillars,
            "expected_pillars",
            unique=False,
        )
        actual = _string_tuple(
            self.actual_pillars,
            "actual_pillars",
            unique=False,
        )
        if len(expected) != 4 or len(actual) != 4:
            raise ValueError("pillar comparison requires exactly four values")
        _require_sha256(self.source_response_sha256, "source_response_sha256")
        _require_bool(self.matched, "matched")
        if self.matched != (expected == actual):
            raise ValueError("matched must equal the actual pillar comparison")
        object.__setattr__(self, "expected_pillars", expected)
        object.__setattr__(self, "actual_pillars", actual)
```

Add `PillarExpectationV2: "fixture_id"` to `_PRIMARY_ID_FIELDS` in `domain_calibration.py` after importing the model.

- [ ] **Step 4: Bind assertion results and runs to actual observations**

Replace the `CalibrationAssertionResult` and `CalibrationRun` declarations with:

```python
@dataclass(frozen=True)
class CalibrationAssertionResult:
    assertion_id: str
    observed_field_path: str
    source_response_sha256: str
    actual_status: str
    actual_values: tuple[str, ...]
    actual_rule_ids: tuple[str, ...]
    actual_evidence_ids: tuple[str, ...]
    matched: bool
    failure_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_str(self.assertion_id, "assertion_id")
        _require_str(self.observed_field_path, "observed_field_path")
        _require_sha256(self.source_response_sha256, "source_response_sha256")
        _require_str(self.actual_status, "actual_status")
        for field_name in (
            "actual_values",
            "actual_rule_ids",
            "actual_evidence_ids",
            "failure_codes",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )
        _require_bool(self.matched, "matched")


@dataclass(frozen=True)
class CalibrationRun:
    run_id: str
    observation_suite_version: str
    observation_sha256: str
    version_set: ExactVersionSet
    assertion_results: tuple[CalibrationAssertionResult, ...]
    pillar_results: tuple[CalibrationPillarResultV2, ...]

    def __post_init__(self) -> None:
        _require_str(self.run_id, "run_id")
        _require_str(self.observation_suite_version, "observation_suite_version")
        _require_sha256(self.observation_sha256, "observation_sha256")
        if not isinstance(self.version_set, ExactVersionSet):
            raise TypeError("version_set must be ExactVersionSet")
        object.__setattr__(
            self,
            "assertion_results",
            _model_tuple(
                self.assertion_results,
                CalibrationAssertionResult,
                "assertion_results",
            ),
        )
        object.__setattr__(
            self,
            "pillar_results",
            _model_tuple(
                self.pillar_results,
                CalibrationPillarResultV2,
                "pillar_results",
            ),
        )
```

Update `_nested_record()` in `domain_calibration.py` so the `CalibrationRun` branch also converts `pillar_results` to `CalibrationPillarResultV2` records. Update the test run factory with the new required fields using deterministic 64-character hashes.

Use these exact test helper values:

```python
def _assertion_result(**changes: object) -> CalibrationAssertionResult:
    values: dict[str, object] = {
        "assertion_id": "assertion-001",
        "observed_field_path": "analysis.rule_families.pattern_strength",
        "source_response_sha256": HASH_A,
        "actual_status": "computed",
        "actual_values": ["strength.label=weak"],
        "actual_rule_ids": ["patterns.follow_strength"],
        "actual_evidence_ids": [],
        "matched": False,
        "failure_codes": ["claim_evidence_trace_missing"],
    }
    values.update(changes)
    return CalibrationAssertionResult(**values)  # type: ignore[arg-type]


def _run(**changes: object) -> CalibrationRun:
    values: dict[str, object] = {
        "run_id": "candidate-observation-v2-run-001",
        "observation_suite_version": "domain-calibration-observation-suite-v2",
        "observation_sha256": HASH_B,
        "version_set": _version_set(),
        "assertion_results": [_assertion_result()],
        "pillar_results": [],
    }
    values.update(changes)
    return CalibrationRun(**values)  # type: ignore[arg-type]
```

- [ ] **Step 5: Add the exact packaged pillar reference**

Create `src/mingli_engine/data/domain_calibration/verified_pillar_expectations_v2.json` with this canonical one-line JSON:

```json
{"contains_real_personal_data":false,"generated_from":["ba63d6cfe16782c6bb43d22242a0b25abc361f34624fcc9ea495ccd9c4c858e5"],"payload_sha256":"77804f9c7115dd4bd2b61b9fdc42112975d9b321f2da5ca8008c882907087ae4","records":[{"expected_pillars":["丙子","庚子","丙戌","癸巳"],"fixture_id":"fixture-calendrical-verified-001","source_fixture_id":"synthetic_01_19961215_0930","source_fixture_sha256":"ba63d6cfe16782c6bb43d22242a0b25abc361f34624fcc9ea495ccd9c4c858e5"}],"schema_version":"domain-calibration-file-v1","suite_version":"domain-calibration-observation-suite-v2"}
```

Add `("verified_pillar_expectations_v2.json", PillarExpectationV2)` to `_CALIBRATION_ASSETS` and change `_FIXTURE_VERSION` from `calibration-fixtures-v1` to `calibration-fixtures-v2`.

- [ ] **Step 6: Run model and loader tests**

Run:

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_domain_calibration_models.py `
  tests/unit/test_domain_calibration_corpus.py `
  -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 7: Commit the models and reference**

```powershell
git add -- `
  src/mingli_engine/domain_calibration_models.py `
  src/mingli_engine/domain_calibration.py `
  src/mingli_engine/data/domain_calibration/verified_pillar_expectations_v2.json `
  tests/unit/test_domain_calibration_models.py
git commit -m "feat: add truthful calibration evidence models"
```

## Task 3: Build Immutable Application Snapshots

**Files:**

- Create: `src/mingli_engine/domain_calibration_observations.py`
- Create: `tests/unit/test_domain_calibration_observations.py`

- [ ] **Step 1: Write parser and boundary tests**

Create `tests/unit/test_domain_calibration_observations.py` with:

```python
from __future__ import annotations

import json

import pytest

from mingli_engine.application_service import handle_real_use_json
from mingli_engine.domain_calibration_observations import (
    CalibrationObservationError,
    OBSERVATION_SUITE_VERSION,
    build_application_snapshot,
)


VALID_PAYLOAD = {
    "birth_datetime": "1996-12-15T09:30:00",
    "gender": "female",
    "focus_question": "traditional structural overview",
}


def test_valid_fixture_snapshot_contains_canonical_real_response() -> None:
    snapshot = build_application_snapshot(
        "fixture-calendrical-verified-001",
        VALID_PAYLOAD,
        handle_real_use_json,
    )
    decoded = json.loads(snapshot.response_payload.decode("utf-8"))
    assert snapshot.state == "ok"
    assert decoded["status"] == "ok"
    assert decoded["result"]["chart"]["pillars"]
    assert len(snapshot.source_response_sha256) == 64
    assert snapshot.suite_version == OBSERVATION_SUITE_VERSION


def test_aware_datetime_is_rejected_without_calling_application() -> None:
    called = False

    def forbidden(_request: bytes) -> bytes:
        nonlocal called
        called = True
        raise AssertionError("application must not run")

    snapshot = build_application_snapshot(
        "fixture-aware-datetime-utc-001",
        {"birth_datetime": "1996-12-15T01:30:00+00:00"},
        forbidden,
    )
    assert snapshot.state == "unsupported_input"
    assert called is False


def test_case_signal_only_fixture_is_not_presented_as_engine_output() -> None:
    snapshot = build_application_snapshot(
        "fixture-severe-conflict-001",
        {"case_signal": "severe_high_risk_scope_conflict"},
        handle_real_use_json,
    )
    assert snapshot.state == "fixture_not_executable"
    assert snapshot.response_payload is None


@pytest.mark.parametrize(
    "payload",
    (b"not-json", b'{"status":"ok","result":null}'),
)
def test_malformed_or_incomplete_application_response_fails_closed(
    payload: bytes,
) -> None:
    with pytest.raises(CalibrationObservationError):
        build_application_snapshot("fixture", VALID_PAYLOAD, lambda _request: payload)
```

- [ ] **Step 2: Run the tests to prove the module is absent**

Run:

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_domain_calibration_observations.py `
  -q -p no:cacheprovider
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement immutable snapshot creation**

Create `src/mingli_engine/domain_calibration_observations.py` with this initial content:

```python
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Literal, cast


ApplicationRunner = Callable[[bytes], bytes]
SnapshotState = Literal[
    "ok",
    "refused",
    "unsupported_input",
    "fixture_not_executable",
]
OBSERVATION_SUITE_VERSION = "domain-calibration-observation-suite-v2"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class CalibrationObservationError(ValueError):
    pass


def _canonical_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        raise CalibrationObservationError("value is not canonical JSON") from None


def _strict_object(payload: bytes) -> dict[str, object]:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise CalibrationObservationError("duplicate application response key")
            result[key] = value
        return result

    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=reject_duplicates)
    except (UnicodeError, json.JSONDecodeError):
        raise CalibrationObservationError("application response is invalid JSON") from None
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CalibrationObservationError("application response must be an object")
    return cast(dict[str, object], value)


@dataclass(frozen=True)
class ApplicationCalibrationSnapshotV2:
    fixture_id: str
    suite_version: str
    state: SnapshotState
    response_payload: bytes | None
    source_response_sha256: str
    failure_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.fixture_id or self.fixture_id != self.fixture_id.strip():
            raise ValueError("fixture_id must be a nonempty trimmed string")
        if self.suite_version != OBSERVATION_SUITE_VERSION:
            raise ValueError("snapshot suite_version is invalid")
        if _SHA256.fullmatch(self.source_response_sha256) is None:
            raise ValueError("source_response_sha256 must be lowercase SHA-256")
        if tuple(sorted(set(self.failure_codes))) != self.failure_codes:
            raise ValueError("failure_codes must be sorted and unique")
        if self.response_payload is not None:
            canonical = _canonical_bytes(_strict_object(self.response_payload))
            if canonical != self.response_payload:
                raise ValueError("response_payload must be canonical JSON")
            if sha256(canonical).hexdigest() != self.source_response_sha256:
                raise ValueError("response payload hash mismatch")


def _boundary_snapshot(
    fixture_id: str,
    state: SnapshotState,
    failure_code: str,
) -> ApplicationCalibrationSnapshotV2:
    identity = _canonical_bytes({"fixture_id": fixture_id, "state": state})
    return ApplicationCalibrationSnapshotV2(
        fixture_id=fixture_id,
        suite_version=OBSERVATION_SUITE_VERSION,
        state=state,
        response_payload=None,
        source_response_sha256=sha256(identity).hexdigest(),
        failure_codes=(failure_code,),
    )


def build_application_snapshot(
    fixture_id: str,
    request_payload: Mapping[str, object],
    application_runner: ApplicationRunner,
) -> ApplicationCalibrationSnapshotV2:
    birth_value = request_payload.get("birth_datetime")
    if not isinstance(birth_value, str):
        return _boundary_snapshot(
            fixture_id,
            "fixture_not_executable",
            "fixture_not_executable",
        )
    try:
        birth_datetime = datetime.fromisoformat(birth_value)
    except ValueError:
        return _boundary_snapshot(fixture_id, "unsupported_input", "unsupported_input")
    if birth_datetime.utcoffset() is not None:
        return _boundary_snapshot(fixture_id, "unsupported_input", "unsupported_input")

    gender = request_payload.get("gender", "unknown")
    focus = request_payload.get("focus_question", "traditional structural overview")
    request = {
        "schema_version": "real-use-request-v1",
        "request_id": f"calibration-{fixture_id}",
        "operation": "analysis",
        "profile": {
            "calendar_type": "gregorian",
            "birth_date": birth_datetime.date().isoformat(),
            "birth_time": birth_datetime.strftime("%H:%M"),
            "birthplace": "Synthetic Calibration Place",
            "gender": gender if isinstance(gender, str) else "unknown",
            "focus_topic": focus if isinstance(focus, str) else "",
        },
        "authorization": {"subject_relation": "self", "attested": True},
        "options": {"report_format": None, "include_profile_in_report": False},
    }
    response = _strict_object(application_runner(_canonical_bytes(request)))
    status = response.get("status")
    if status == "error":
        raise CalibrationObservationError("calibration application execution failed")
    if status not in {"ok", "refused"}:
        raise CalibrationObservationError("calibration application status is invalid")
    if status == "ok":
        result = response.get("result")
        if not isinstance(result, dict):
            raise CalibrationObservationError("ok response requires a result object")
        if not isinstance(result.get("chart"), dict) or not isinstance(
            result.get("calculation"), dict
        ):
            raise CalibrationObservationError("analysis result is structurally incomplete")
    elif response.get("result") is not None:
        raise CalibrationObservationError("refused response must not contain a result")
    canonical = _canonical_bytes(response)
    return ApplicationCalibrationSnapshotV2(
        fixture_id=fixture_id,
        suite_version=OBSERVATION_SUITE_VERSION,
        state=cast(SnapshotState, status),
        response_payload=canonical,
        source_response_sha256=sha256(canonical).hexdigest(),
        failure_codes=() if status == "ok" else ("safety_refusal",),
    )


def snapshot_response(
    snapshot: ApplicationCalibrationSnapshotV2,
) -> dict[str, object] | None:
    if snapshot.response_payload is None:
        return None
    return _strict_object(snapshot.response_payload)
```

- [ ] **Step 4: Run the parser tests**

Run the Task 3 test command again. Expected: PASS.

- [ ] **Step 5: Commit immutable snapshots**

```powershell
git add -- `
  src/mingli_engine/domain_calibration_observations.py `
  tests/unit/test_domain_calibration_observations.py
git commit -m "feat: capture immutable calibration application snapshots"
```

## Task 4: Add Code-Owned Actual-Observation Projectors

**Files:**

- Modify: `src/mingli_engine/domain_calibration_observations.py`
- Modify: `tests/unit/test_domain_calibration_observations.py`

- [ ] **Step 1: Write failing projection tests**

Append:

```python
from mingli_engine.domain_calibration_observations import build_observation_index


def test_supported_observations_come_from_real_calculation_fields() -> None:
    snapshot = build_application_snapshot(
        "fixture-calendrical-verified-001",
        VALID_PAYLOAD,
        handle_real_use_json,
    )
    observations = build_observation_index(
        snapshot,
        ("ziping", "liang_xiangrun", "duan"),
    )
    strength = observations["analysis.rule_families.pattern_strength"]
    assert strength.actual_status in {"computed", "indeterminate"}
    assert any(value.startswith("strength.label=") for value in strength.actual_values)
    assert strength.actual_evidence_ids == ()
    assert "claim_evidence_trace_missing" in strength.failure_codes
    unsupported = observations["analysis.rule_families.high_risk_signal"]
    assert unsupported.actual_status == "not_computed"
    assert unsupported.actual_values == ()


def test_refusal_never_projects_domain_values() -> None:
    snapshot = build_application_snapshot(
        "fixture-safety-high-risk-lifespan-refusal-001",
        {
            "birth_datetime": "1996-12-15T09:30:00",
            "focus_question": "哪年会死",
        },
        handle_real_use_json,
    )
    observations = build_observation_index(snapshot, ("ziping",))
    assert snapshot.state == "refused"
    assert all(item.actual_status == "not_computed" for item in observations.values())
    assert all(item.actual_values == () for item in observations.values())


def test_observation_module_has_no_expected_label_dependency() -> None:
    import ast
    import inspect
    import mingli_engine.domain_calibration_observations as module

    tree = ast.parse(inspect.getsource(module))
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert names.isdisjoint(
        {
            "CalibrationAssertion",
            "AdjudicationDecision",
            "CalibrationReview",
            "acceptable_values",
            "acceptable_statuses",
            "required_rule_ids",
            "required_evidence_ids",
        }
    )
```

- [ ] **Step 2: Run to prove projection is absent**

Expected: FAIL because `build_observation_index` is not importable.

- [ ] **Step 3: Add observation model and canonical helpers**

Add to `domain_calibration_observations.py`:

```python
ObservationStatus = Literal["computed", "indeterminate", "disputed", "not_computed"]
_OBSERVATION_STATUSES = frozenset(
    {"computed", "indeterminate", "disputed", "not_computed"}
)
_FAMILY_PATHS = (
    "analysis.rule_families.pattern_strength",
    "analysis.rule_families.five_element_balance",
    "analysis.rule_families.useful_god_candidate",
    "analysis.rule_families.taboo_god_candidate",
    "analysis.rule_families.ten_god_relation",
    "analysis.rule_families.branch_interaction",
    "analysis.rule_families.blind_image_method",
    "analysis.rule_families.luck_cycle",
    "analysis.rule_families.remedy_boundary",
    "analysis.rule_families.high_risk_signal",
)
_UNSUPPORTED_FAMILY_PATHS = frozenset(
    {
        "analysis.rule_families.taboo_god_candidate",
        "analysis.rule_families.blind_image_method",
        "analysis.rule_families.remedy_boundary",
        "analysis.rule_families.high_risk_signal",
    }
)


@dataclass(frozen=True)
class CalibrationObservationV2:
    fixture_id: str
    field_path: str
    actual_status: ObservationStatus
    actual_values: tuple[str, ...]
    actual_rule_ids: tuple[str, ...]
    actual_evidence_ids: tuple[str, ...]
    failure_codes: tuple[str, ...]
    source_response_sha256: str

    def __post_init__(self) -> None:
        for field_name in ("fixture_id", "field_path"):
            value = getattr(self, field_name)
            if not value or value != value.strip():
                raise ValueError(f"{field_name} must be a nonempty trimmed string")
        if self.actual_status not in _OBSERVATION_STATUSES:
            raise ValueError("actual_status is unsupported")
        for field_name in (
            "actual_values",
            "actual_rule_ids",
            "actual_evidence_ids",
            "failure_codes",
        ):
            values = tuple(getattr(self, field_name))
            if tuple(sorted(set(values))) != values:
                raise ValueError(f"{field_name} must be sorted and unique")
            if any(not value or value != value.strip() for value in values):
                raise ValueError(f"{field_name} contains an invalid value")
        if _SHA256.fullmatch(self.source_response_sha256) is None:
            raise ValueError("source_response_sha256 must be lowercase SHA-256")


def _mapping(value: object, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CalibrationObservationError(f"{field_name} must be an object")
    return cast(dict[str, object], value)


def _sequence(value: object, field_name: str) -> list[object]:
    if not isinstance(value, list):
        raise CalibrationObservationError(f"{field_name} must be a list")
    return value


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise CalibrationObservationError(f"{field_name} must be a nonempty string")
    return value


def _number(value: object, field_name: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CalibrationObservationError(f"{field_name} must be numeric")
    return json.dumps(value, allow_nan=False, separators=(",", ":"))


def _reasoning(value: object) -> tuple[ObservationStatus, tuple[str, ...]]:
    reasoning = _mapping(value, "reasoning")
    status = _text(reasoning.get("status"), "reasoning.status")
    if status not in _OBSERVATION_STATUSES:
        raise CalibrationObservationError("reasoning.status is unsupported")
    rule_values = _sequence(reasoning.get("rule_ids"), "reasoning.rule_ids")
    rule_ids = tuple(sorted({_text(item, "rule_id") for item in rule_values}))
    return cast(ObservationStatus, status), rule_ids


def _aggregate_status(statuses: list[ObservationStatus]) -> ObservationStatus:
    for status in ("computed", "disputed", "indeterminate"):
        if status in statuses:
            return cast(ObservationStatus, status)
    return "not_computed"


def _observation(
    snapshot: ApplicationCalibrationSnapshotV2,
    field_path: str,
    status: ObservationStatus,
    values: set[str],
    rule_ids: set[str],
    failure_codes: set[str],
) -> CalibrationObservationV2:
    if status != "not_computed":
        failure_codes.add("claim_evidence_trace_missing")
    return CalibrationObservationV2(
        fixture_id=snapshot.fixture_id,
        field_path=field_path,
        actual_status=status,
        actual_values=tuple(sorted(values)),
        actual_rule_ids=tuple(sorted(rule_ids)),
        actual_evidence_ids=(),
        failure_codes=tuple(sorted(failure_codes)),
        source_response_sha256=snapshot.source_response_sha256,
    )
```

- [ ] **Step 4: Implement all projectors and the registry**

Add these concrete projector functions for the six supported families and school views. Each function reads only real response fields:

```python
def _project_pattern_strength(
    snapshot: ApplicationCalibrationSnapshotV2,
    calculation: dict[str, object],
) -> CalibrationObservationV2:
    strength = _mapping(calculation.get("strength"), "calculation.strength")
    status, strength_rules = _reasoning(strength.get("reasoning"))
    values = {
        f"strength.status={status}",
        f"strength.label={_text(strength.get('label'), 'strength.label')}",
        f"strength.score={_number(strength.get('score'), 'strength.score')}",
    }
    rules = set(strength_rules)
    for value in _sequence(calculation.get("patterns"), "calculation.patterns"):
        item = _mapping(value, "pattern")
        item_status, item_rules = _reasoning(item.get("reasoning"))
        values.add(
            "pattern="
            f"{_text(item.get('pattern_id'), 'pattern.pattern_id')}|"
            f"{_number(item.get('rank'), 'pattern.rank')}|{item_status}"
        )
        rules.update(item_rules)
    return _observation(
        snapshot,
        "analysis.rule_families.pattern_strength",
        status,
        values,
        rules,
        set(),
    )


def _project_five_elements(
    snapshot: ApplicationCalibrationSnapshotV2,
    chart: dict[str, object],
    calculation: dict[str, object],
) -> CalibrationObservationV2:
    summary = _mapping(chart.get("five_elements_summary"), "five_elements_summary")
    strength = _mapping(calculation.get("strength"), "calculation.strength")
    status, rules = _reasoning(strength.get("reasoning"))
    values = {
        f"five_element.{name}={_number(value, f'five_elements_summary.{name}') }"
        for name, value in summary.items()
    }
    values.add(f"strength.status={status}")
    values.add(f"strength.label={_text(strength.get('label'), 'strength.label')}")
    return _observation(
        snapshot,
        "analysis.rule_families.five_element_balance",
        status,
        values,
        set(rules),
        set(),
    )


def _project_useful_gods(
    snapshot: ApplicationCalibrationSnapshotV2,
    calculation: dict[str, object],
) -> CalibrationObservationV2:
    records = _sequence(calculation.get("useful_gods"), "calculation.useful_gods")
    statuses: list[ObservationStatus] = []
    values: set[str] = set()
    rules: set[str] = set()
    for value in records:
        item = _mapping(value, "useful_god")
        status, item_rules = _reasoning(item.get("reasoning"))
        statuses.append(status)
        rules.update(item_rules)
        values.add(
            "useful_god="
            f"{_text(item.get('method'), 'useful_god.method')}|"
            f"{_text(item.get('element'), 'useful_god.element')}|"
            f"{_number(item.get('rank'), 'useful_god.rank')}|{status}"
        )
    status = _aggregate_status(statuses)
    failures = set() if records else {"engine_output_empty"}
    return _observation(
        snapshot,
        "analysis.rule_families.useful_god_candidate",
        status,
        values,
        rules,
        failures,
    )


def _project_ten_gods(
    snapshot: ApplicationCalibrationSnapshotV2,
    calculation: dict[str, object],
) -> CalibrationObservationV2:
    facts = _mapping(calculation.get("facts"), "calculation.facts")
    values: set[str] = set()
    exposed = _sequence(facts.get("exposed_stems"), "facts.exposed_stems")
    hidden = _sequence(facts.get("hidden_stems"), "facts.hidden_stems")
    for value in exposed:
        item = _mapping(value, "exposed_stem")
        values.add(
            "ten_god.exposed="
            f"{_text(item.get('pillar_name'), 'pillar_name')}|"
            f"{_text(item.get('stem'), 'stem')}|"
            f"{_text(item.get('ten_god'), 'ten_god')}"
        )
    for value in hidden:
        item = _mapping(value, "hidden_stem")
        values.add(
            "ten_god.hidden="
            f"{_text(item.get('pillar_name'), 'pillar_name')}|"
            f"{_text(item.get('stem'), 'stem')}|"
            f"{_text(item.get('ten_god'), 'ten_god')}"
        )
    values.add(f"ten_god.exposed_count={len(exposed)}")
    values.add(f"ten_god.hidden_count={len(hidden)}")
    return _observation(
        snapshot,
        "analysis.rule_families.ten_god_relation",
        "computed",
        values,
        set(),
        set(),
    )


def _project_branch_relations(
    snapshot: ApplicationCalibrationSnapshotV2,
    calculation: dict[str, object],
) -> CalibrationObservationV2:
    records = _sequence(
        calculation.get("branch_relations"),
        "calculation.branch_relations",
    )
    values = {f"branch_relation.count={len(records)}"}
    rules: set[str] = set()
    for value in records:
        item = _mapping(value, "branch_relation")
        branches = tuple(
            _text(branch, "branch")
            for branch in _sequence(item.get("branches"), "branch_relation.branches")
        )
        rule_id = _text(item.get("rule_id"), "branch_relation.rule_id")
        rules.add(rule_id)
        values.add(
            "branch_relation="
            f"{_text(item.get('relation_type'), 'relation_type')}|"
            f"{','.join(branches)}|"
            f"{_text(item.get('state'), 'state')}|{rule_id}"
        )
    return _observation(
        snapshot,
        "analysis.rule_families.branch_interaction",
        "computed",
        values,
        rules,
        set(),
    )


def _project_luck_cycle(
    snapshot: ApplicationCalibrationSnapshotV2,
    calculation: dict[str, object],
) -> CalibrationObservationV2:
    luck = _mapping(calculation.get("luck_cycles"), "calculation.luck_cycles")
    status, reasoning_rules = _reasoning(luck.get("reasoning"))
    forward = luck.get("forward")
    if type(forward) is not bool:
        raise CalibrationObservationError("luck_cycles.forward must be bool")
    values = {
        f"luck_cycle.status={status}",
        f"luck_cycle.forward={str(forward).lower()}",
        f"luck_cycle.start_years={_number(luck.get('start_years'), 'start_years')}",
        f"luck_cycle.start_months={_number(luck.get('start_months'), 'start_months')}",
        f"luck_cycle.start_days={_number(luck.get('start_days'), 'start_days')}",
        f"luck_cycle.start_solar={_text(luck.get('start_solar'), 'start_solar')}",
    }
    rules = set(reasoning_rules)
    for value in _sequence(luck.get("pillars"), "luck_cycles.pillars"):
        item = _mapping(value, "luck_cycle.pillar")
        values.add(
            "luck_cycle.pillar="
            f"{_number(item.get('index'), 'pillar.index')}|"
            f"{_text(item.get('gan_zhi'), 'pillar.gan_zhi')}|"
            f"{_number(item.get('start_year'), 'pillar.start_year')}|"
            f"{_number(item.get('end_year'), 'pillar.end_year')}"
        )
    for value in _sequence(
        luck.get("selected_year_relations"),
        "luck_cycles.selected_year_relations",
    ):
        item = _mapping(value, "selected_year_relation")
        rules.add(_text(item.get("rule_id"), "selected_year_relation.rule_id"))
    return _observation(
        snapshot,
        "analysis.rule_families.luck_cycle",
        status,
        values,
        rules,
        set(),
    )


def _project_school(
    snapshot: ApplicationCalibrationSnapshotV2,
    school_id: str,
    school_records: list[object],
) -> CalibrationObservationV2:
    path = f"analysis.school_views.{school_id}"
    for value in school_records:
        item = _mapping(value, "school")
        if item.get("school_id") != school_id:
            continue
        status, rules = _reasoning(item.get("reasoning"))
        patterns = tuple(
            sorted(
                _text(entry, "preferred_pattern_id")
                for entry in _sequence(
                    item.get("preferred_pattern_ids"),
                    "preferred_pattern_ids",
                )
            )
        )
        elements = tuple(
            sorted(
                _text(entry, "preferred_useful_god_element")
                for entry in _sequence(
                    item.get("preferred_useful_god_elements"),
                    "preferred_useful_god_elements",
                )
            )
        )
        values = {
            f"school={school_id}|status={status}|patterns={','.join(patterns)}|"
            f"useful_elements={','.join(elements)}"
        }
        return _observation(snapshot, path, status, values, set(rules), set())
    return _observation(
        snapshot,
        path,
        "not_computed",
        set(),
        set(),
        {"school_output_missing"},
    )
```

Then add the exact public registry function:

```python
def build_observation_index(
    snapshot: ApplicationCalibrationSnapshotV2,
    school_ids: tuple[str, ...],
) -> dict[str, CalibrationObservationV2]:
    paths = (*_FAMILY_PATHS, *(f"analysis.school_views.{item}" for item in school_ids))
    if snapshot.state != "ok":
        code = snapshot.failure_codes[0]
        return {
            path: _observation(snapshot, path, "not_computed", set(), set(), {code})
            for path in paths
        }

    response = snapshot_response(snapshot)
    assert response is not None
    result = _mapping(response.get("result"), "result")
    chart = _mapping(result.get("chart"), "result.chart")
    calculation = _mapping(result.get("calculation"), "result.calculation")
    observations = {
        "analysis.rule_families.pattern_strength": _project_pattern_strength(
            snapshot, calculation
        ),
        "analysis.rule_families.five_element_balance": _project_five_elements(
            snapshot, chart, calculation
        ),
        "analysis.rule_families.useful_god_candidate": _project_useful_gods(
            snapshot, calculation
        ),
        "analysis.rule_families.ten_god_relation": _project_ten_gods(
            snapshot, calculation
        ),
        "analysis.rule_families.branch_interaction": _project_branch_relations(
            snapshot, calculation
        ),
        "analysis.rule_families.luck_cycle": _project_luck_cycle(
            snapshot, calculation
        ),
    }
    for path in _UNSUPPORTED_FAMILY_PATHS:
        observations[path] = _observation(
            snapshot,
            path,
            "not_computed",
            set(),
            set(),
            {"unsupported_observation_path"},
        )
    school_records = _sequence(calculation.get("schools"), "calculation.schools")
    for school_id in school_ids:
        observations[f"analysis.school_views.{school_id}"] = _project_school(
            snapshot,
            school_id,
            school_records,
        )
    if set(observations) != set(paths):
        raise CalibrationObservationError("observation registry coverage is incomplete")
    return dict(sorted(observations.items()))
```

Every private projector ends by calling `_observation`; none may accept a calibration assertion, review, citation, or adjudication argument.

- [ ] **Step 5: Run projector tests**

Run:

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_domain_calibration_observations.py `
  -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 6: Run static checks on the new module**

```powershell
uv run --frozen --with mypy==1.17.1 python -m mypy `
  src/mingli_engine/domain_calibration_observations.py `
  --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check `
  src/mingli_engine/domain_calibration_observations.py `
  tests/unit/test_domain_calibration_observations.py
```

Expected: both commands return 0.

- [ ] **Step 7: Commit projectors**

```powershell
git add -- `
  src/mingli_engine/domain_calibration_observations.py `
  tests/unit/test_domain_calibration_observations.py
git commit -m "feat: project calibration observations from engine output"
```

## Task 5: Replace the Self-Confirming Candidate Runner

**Files:**

- Modify: `src/mingli_engine/domain_calibration.py`
- Modify: `tests/integration/test_domain_calibration_pipeline.py`

- [ ] **Step 1: Write the payload-tamper integration test**

Add:

```python
def test_candidate_run_changes_when_engine_payload_changes(version_set) -> None:
    from mingli_engine.application_service import handle_real_use_json

    baseline = calibration.execute_candidate_calibration(
        version_set,
        application_runner=handle_real_use_json,
    )

    def tampered_runner(request: bytes) -> bytes:
        response = json.loads(handle_real_use_json(request).decode("utf-8"))
        if response["status"] == "ok":
            response["result"]["calculation"]["strength"]["label"] = "tampered"
        return calibration.canonical_json_bytes(response)

    tampered = calibration.execute_candidate_calibration(
        version_set,
        application_runner=tampered_runner,
    )
    assert tampered != baseline
    assert tampered.run_id != baseline.run_id
    assert tampered.observation_sha256 != baseline.observation_sha256
```

Import `json` at the top of the test file.

- [ ] **Step 2: Run the new test to prove the injected runner is absent**

Run only the named test. Expected: FAIL because `application_runner` is not accepted.

- [ ] **Step 3: Replace candidate execution**

Import `ApplicationRunner`, `OBSERVATION_SUITE_VERSION`, `build_application_snapshot`, and `build_observation_index` from the new module. Replace `_candidate_status_and_values` and `execute_candidate_calibration` with an implementation that follows this exact order. Retain `_application_fixture_state` only until Task 6 so the old pillar metric remains executable during this intermediate commit; Task 6 removes its final call and then deletes the helper.

```python
def execute_candidate_calibration(
    version_set: ExactVersionSet,
    *,
    application_runner: ApplicationRunner = handle_real_use_json,
) -> CalibrationRun:
    if version_set != build_candidate_version_set(version_set.application_version):
        raise CalibrationProtocolError("candidate version_set is not authoritative")
    fixtures = _load_packaged("input_fixtures.json", CalibrationInputFixture).records
    cases = _load_packaged("calibration_cases.json", CalibrationCase).records
    assertions = _load_packaged(
        "calibration_assertions.json",
        CalibrationAssertion,
    ).records
    _profile_version, school_ids = load_authoritative_school_profile_identity()
    try:
        snapshots = {
            fixture.fixture_id: build_application_snapshot(
                fixture.fixture_id,
                fixture.request_payload,
                application_runner,
            )
            for fixture in fixtures
        }
        observations = {
            fixture_id: build_observation_index(snapshot, school_ids)
            for fixture_id, snapshot in snapshots.items()
        }
    except CalibrationObservationError as error:
        raise CalibrationProtocolError(str(error)) from None

    observation_payload = tuple(
        observation
        for fixture_id in sorted(observations)
        for observation in observations[fixture_id].values()
    )
    observation_sha256 = sha256(canonical_json_bytes(observation_payload)).hexdigest()

    adjudications = _load_packaged(
        "adjudication.json",
        AdjudicationDecision,
    ).records
    fixture_by_id = {item.fixture_id: item for item in fixtures}
    case_by_id = {item.case_id: item for item in cases}
    decision_by_id = {item.assertion_id: item for item in adjudications}
    results: list[CalibrationAssertionResult] = []
    for assertion in assertions:
        case = case_by_id[assertion.case_id]
        fixture = fixture_by_id[case.input_fixture_id]
        observation = observations[fixture.fixture_id].get(assertion.field_path)
        if observation is None:
            raise CalibrationProtocolError("assertion observation path is unsupported")
        decision = decision_by_id[assertion.assertion_id]
        matched = _matches_adjudication(
            observation.actual_status,
            observation.actual_values,
            decision,
        )
        failure_codes = set(observation.failure_codes)
        if observation.actual_status not in decision.final_statuses:
            failure_codes.add("status_not_adjudicated")
        if not matched:
            failure_codes.add("value_not_adjudicated")
        results.append(
            CalibrationAssertionResult(
                assertion_id=assertion.assertion_id,
                observed_field_path=observation.field_path,
                source_response_sha256=observation.source_response_sha256,
                actual_status=observation.actual_status,
                actual_values=observation.actual_values,
                actual_rule_ids=observation.actual_rule_ids,
                actual_evidence_ids=observation.actual_evidence_ids,
                matched=matched,
                failure_codes=tuple(sorted(failure_codes)),
            )
        )
    ordered_results = tuple(sorted(results, key=lambda item: item.assertion_id))
    run_hash = sha256(
        canonical_json_bytes(
            (
                OBSERVATION_SUITE_VERSION,
                observation_sha256,
                version_set,
                ordered_results,
            )
        )
    ).hexdigest()[:24]
    return CalibrationRun(
        run_id=f"candidate-observation-v2-run-{run_hash}",
        observation_suite_version=OBSERVATION_SUITE_VERSION,
        observation_sha256=observation_sha256,
        version_set=version_set,
        assertion_results=ordered_results,
        pillar_results=(),
    )
```

The function may load assertions before execution to obtain coverage, but no assertion object or field except `field_path` may enter snapshot or projector construction. Adjudications are loaded only after `observation_payload` has been frozen.

- [ ] **Step 4: Replace self-confirming trace expectations**

In `test_results_have_complete_traces_and_stable_failure_codes`, remove assertions that required IDs are subsets of actual IDs. Assert instead:

```python
assert result.observed_field_path == assertion.field_path
assert len(result.source_response_sha256) == 64
assert result.actual_evidence_ids == ()
assert result.failure_codes == tuple(sorted(set(result.failure_codes)))
```

Replace the school-alternative test with an assertion that no projector manufactures `school_alternative_retained` from assertion kind.

Replace the old monkeypatch-based application-error test with explicit dependency injection:

```python
def test_application_error_fails_closed_without_candidate_results(version_set) -> None:
    with pytest.raises(
        CalibrationProtocolError,
        match="calibration application execution failed",
    ):
        calibration.execute_candidate_calibration(
            version_set,
            application_runner=lambda _payload: b'{"status":"error"}',
        )
```

- [ ] **Step 5: Run runner-focused tests**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_domain_calibration_observations.py `
  tests/integration/test_domain_calibration_pipeline.py `
  -q -p no:cacheprovider
```

Expected: tests unrelated to pillar metrics pass; the old pillar/trace metric expectation may remain red until Task 6.

- [ ] **Step 6: Commit truthful execution**

```powershell
git add -- `
  src/mingli_engine/domain_calibration.py `
  tests/integration/test_domain_calibration_pipeline.py
git commit -m "fix: derive calibration results from application output"
```

## Task 6: Compute Pillar Agreement from Four Actual Pillars

**Files:**

- Modify: `src/mingli_engine/domain_calibration.py`
- Modify: `tests/integration/test_domain_calibration_pipeline.py`

- [ ] **Step 1: Write a tampered-pillar metric test**

Add a test that executes a baseline run and a run whose injected application response changes only `result.chart.pillars[0].gan_zhi` to `甲子`. Assert:

```python
assert baseline.pillar_results[0].matched is True
assert tampered.pillar_results[0].matched is False
baseline_snapshot = calibration.build_candidate_metric_snapshot(baseline, baseline)
tampered_snapshot = calibration.build_candidate_metric_snapshot(tampered, tampered)
assert baseline_snapshot.pillar_agreement_rate == 1.0
assert tampered_snapshot.pillar_agreement_rate == 0.0
```

- [ ] **Step 2: Run the test to prove actual pillars are not stored**

Expected: FAIL because `pillar_results` is empty.

- [ ] **Step 3: Build pillar comparisons during execution**

Import `snapshot_response`, `ApplicationCalibrationSnapshotV2`, `PillarExpectationV2`, and `CalibrationPillarResultV2`. Add this private helper, which validates actual pillar names in the exact order `year`, `month`, `day`, `hour`:

```python
def _build_pillar_results(
    snapshots: Mapping[str, ApplicationCalibrationSnapshotV2],
) -> tuple[CalibrationPillarResultV2, ...]:
    expectations = _load_packaged(
        "verified_pillar_expectations_v2.json",
        PillarExpectationV2,
    ).records
    results: list[CalibrationPillarResultV2] = []
    for expectation in expectations:
        snapshot = snapshots.get(expectation.fixture_id)
        if snapshot is None or snapshot.state != "ok":
            raise CalibrationProtocolError("pillar reference fixture was not executed")
        response = snapshot_response(snapshot)
        if response is None or not isinstance(response.get("result"), dict):
            raise CalibrationProtocolError("pillar response result is unavailable")
        result = cast(dict[str, object], response["result"])
        chart = result.get("chart")
        if not isinstance(chart, dict) or not isinstance(chart.get("pillars"), list):
            raise CalibrationProtocolError("pillar response chart is malformed")
        pillar_objects = chart["pillars"]
        if len(pillar_objects) != 4 or not all(
            isinstance(item, dict) for item in pillar_objects
        ):
            raise CalibrationProtocolError("pillar response must contain four pillars")
        names = tuple(cast(dict[str, object], item).get("name") for item in pillar_objects)
        if names != ("year", "month", "day", "hour"):
            raise CalibrationProtocolError("pillar response order is invalid")
        actual_values = tuple(
            cast(dict[str, object], item).get("gan_zhi") for item in pillar_objects
        )
        if not all(isinstance(item, str) and item for item in actual_values):
            raise CalibrationProtocolError("pillar gan-zhi value is invalid")
        actual_pillars = cast(tuple[str, ...], actual_values)
        results.append(
            CalibrationPillarResultV2(
                fixture_id=expectation.fixture_id,
                expected_pillars=expectation.expected_pillars,
                actual_pillars=actual_pillars,
                source_response_sha256=snapshot.source_response_sha256,
                matched=actual_pillars == expectation.expected_pillars,
            )
        )
    if not results:
        raise CalibrationProtocolError("pillar agreement has an empty denominator")
    return tuple(sorted(results, key=lambda item: item.fixture_id))
```

Call `_build_pillar_results(snapshots)` after observation construction. Include the returned `pillar_results` in the observation hash, run hash, and returned `CalibrationRun`. Do not use `source_fixture_file`, fixture filename equality, response status alone, or source hash equality as the match result. After replacing the final metric call, delete `_application_fixture_state` because no corrected evidence path may depend on status-only execution.

- [ ] **Step 4: Replace metadata-only metric computation**

In `build_candidate_metric_snapshot`, replace the existing `provider_cases` expression with:

```python
if not run.pillar_results:
    raise CalibrationProtocolError("pillar agreement has an empty denominator")
if run.pillar_results != repeated_run.pillar_results:
    raise CalibrationProtocolError("repeated run pillar results differ")
pillar_agreement_rate = sum(item.matched for item in run.pillar_results) / len(
    run.pillar_results
)
```

- [ ] **Step 5: Run pipeline tests**

Run the full `test_domain_calibration_pipeline.py`. Expected: PASS after old trace expectations are changed to truthful values:

```python
assert snapshot.pillar_agreement_rate == 1.0
assert snapshot.evidence_trace_completeness_rate == 0.0
assert 0.0 <= snapshot.rule_trace_completeness_rate < 1.0
```

- [ ] **Step 6: Commit real pillar comparison**

```powershell
git add -- `
  src/mingli_engine/domain_calibration.py `
  tests/integration/test_domain_calibration_pipeline.py
git commit -m "fix: compare calibration pillars from actual responses"
```

## Task 7: Complete the Adversarial Evidence Test Matrix

**Files:**

- Modify: `tests/unit/test_domain_calibration_observations.py`
- Modify: `tests/integration/test_domain_calibration_pipeline.py`
- Modify: `tests/unit/test_domain_calibration_release.py`

- [ ] **Step 1: Add all remaining adversarial tests**

Implement one named test for each invariant:

```text
test_whole_result_replacement_fails_closed
test_acceptable_values_cannot_change_actual_observation
test_required_ids_are_not_copied_into_actual_trace
test_removed_actual_rule_lowers_rule_completeness
test_missing_claim_trace_is_incomplete_and_not_inherited
test_changed_actual_pillar_lowers_pillar_agreement
test_unordered_structures_have_stable_canonical_observations
test_malformed_application_json_fails_closed
test_refusal_never_reports_computed_domain_values
test_observation_module_has_no_label_or_adjudication_dependency
```

For expected-value independence, load an assertion, create a `dataclasses.replace()` copy with different `acceptable_values`, and prove the already-built observation index is byte-for-byte equal because the projector API has no assertion parameter. For required-ID independence, assert at least one result's actual rule IDs differ from its required IDs and all current claim-specific evidence IDs are empty rather than copied.

- [ ] **Step 2: Make legacy release tests expect honest blocking**

Update tests that previously treated 100% copied traces as release evidence. Preserve these facts:

- legacy calibration status remains blocked or non-release;
- corrected evidence trace completeness is zero until claim-level traces exist;
- the new source-grounded application decision remains `not_evaluated` unless raw hard-gate producers have run;
- reviewer/adjudication artifacts are unchanged;
- no test lowers a threshold or rewrites historical metrics.

- [ ] **Step 3: Run the adversarial and release suites**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_domain_calibration_observations.py `
  tests/integration/test_domain_calibration_pipeline.py `
  tests/unit/test_domain_calibration_release.py `
  tests/unit/test_domain_calibration_maturity.py `
  -q -p no:cacheprovider
```

Expected: PASS. The output must not contain skipped adversarial tests.

- [ ] **Step 4: Re-run the original tamper experiment**

Execute a read-only probe that replaces every successful response's `result` with `{"tampered":"not-engine-output"}` while preserving status. Expected: `CalibrationProtocolError`; equality with the baseline run is forbidden.

- [ ] **Step 5: Commit adversarial coverage**

```powershell
git add -- `
  tests/unit/test_domain_calibration_observations.py `
  tests/integration/test_domain_calibration_pipeline.py `
  tests/unit/test_domain_calibration_release.py
git commit -m "test: prove calibration cannot certify expected labels"
```

## Task 8: Package the Corrected Reference and Document Historical Limits

**Files:**

- Modify: `src/mingli_engine/packaging_validation.py`
- Modify: `tests/contract/test_wheel_runtime_assets.py`
- Create: `specs/_drafts/019-bazi-domain-validation-and-application-v1/calibration-evidence-integrity-note.md`
- Modify: `specs/_drafts/019-bazi-domain-validation-and-application-v1/contracts/domain-calibration-v1-contract.md`
- Modify: `docs/superpowers/specs/2026-07-18-feature-019-evidence-trust-recovery-design.md`

- [ ] **Step 1: Write the failing package-manifest assertion**

Add this exact path to the expected wheel asset set in `test_wheel_runtime_assets.py`:

```python
"mingli_engine/data/domain_calibration/verified_pillar_expectations_v2.json"
```

Run the named contract test. Expected: FAIL because `EXPECTED_RUNTIME_JSON_ASSETS` does not contain it.

- [ ] **Step 2: Update the runtime manifest**

Add this sorted entry after `reviewer_packets.json` in `packaging_validation.py`:

```python
"data/domain_calibration/verified_pillar_expectations_v2.json",
```

Run the contract test again. Expected: PASS.

- [ ] **Step 3: Document evidence integrity without rewriting history**

Create `calibration-evidence-integrity-note.md` with these explicit statements:

- the historical V1 runner used assertion-derived actual values and copied required traces;
- historical bytes, hashes, reviews, adjudications, and recorded metrics remain immutable;
- historical `0.4418604651162791` is not interpreted as a proven engine-output match rate;
- corrected suite ID is `domain-calibration-observation-suite-v2`;
- corrected values and rule IDs come from real application output;
- claim evidence trace is currently absent and therefore incomplete, not 100%;
- internal release remains blocked/not-evaluated until the subsequent source-trace stage supplies real hard-gate evidence.

Add the same corrected-suite rules to the calibration contract and change the recovery design status to `Implementation started on isolated closure branch`.

- [ ] **Step 4: Prove historical V1 JSON assets are unchanged**

Run:

```powershell
git diff --exit-code fb8ea64 -- `
  src/mingli_engine/data/domain_calibration/adjudication.json `
  src/mingli_engine/data/domain_calibration/calibration_assertions.json `
  src/mingli_engine/data/domain_calibration/calibration_cases.json `
  src/mingli_engine/data/domain_calibration/calibration_citations.json `
  src/mingli_engine/data/domain_calibration/input_fixtures.json `
  src/mingli_engine/data/domain_calibration/reviewer_a_assignments.json `
  src/mingli_engine/data/domain_calibration/reviewer_a_reviews.json `
  src/mingli_engine/data/domain_calibration/reviewer_b_assignments.json `
  src/mingli_engine/data/domain_calibration/reviewer_b_reviews.json `
  src/mingli_engine/data/domain_calibration/reviewer_packets.json
```

Expected: exit 0 and no diff.

- [ ] **Step 5: Run packaging tests**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/contract/test_wheel_runtime_assets.py `
  tests/unit/test_application_validation.py `
  -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 6: Commit packaging and integrity documentation**

```powershell
git add -- `
  src/mingli_engine/packaging_validation.py `
  tests/contract/test_wheel_runtime_assets.py `
  specs/_drafts/019-bazi-domain-validation-and-application-v1/calibration-evidence-integrity-note.md `
  specs/_drafts/019-bazi-domain-validation-and-application-v1/contracts/domain-calibration-v1-contract.md `
  docs/superpowers/specs/2026-07-18-feature-019-evidence-trust-recovery-design.md
git commit -m "docs: record corrected calibration evidence boundary"
```

## Task 9: Verify Stage 1 and Obtain Independent Review

**Files:**

- No planned source changes; review fixes are committed separately if required.

- [ ] **Step 1: Run the complete focused evidence suite**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/unit/test_domain_calibration_models.py `
  tests/unit/test_domain_calibration_observations.py `
  tests/integration/test_domain_calibration_pipeline.py `
  tests/unit/test_domain_calibration_release.py `
  tests/unit/test_domain_calibration_maturity.py `
  tests/contract/test_wheel_runtime_assets.py `
  tests/unit/test_application_validation.py `
  -q -p no:cacheprovider
```

Expected: zero failures and zero adversarial-test skips.

- [ ] **Step 2: Run touched-file static gates**

```powershell
uv run --frozen --with mypy==1.17.1 python -m mypy `
  src/mingli_engine/domain_calibration.py `
  src/mingli_engine/domain_calibration_models.py `
  src/mingli_engine/domain_calibration_observations.py `
  src/mingli_engine/packaging_validation.py `
  --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check `
  src/mingli_engine/domain_calibration.py `
  src/mingli_engine/domain_calibration_models.py `
  src/mingli_engine/domain_calibration_observations.py `
  src/mingli_engine/packaging_validation.py `
  tests/unit/test_domain_calibration_models.py `
  tests/unit/test_domain_calibration_observations.py `
  tests/integration/test_domain_calibration_pipeline.py `
  tests/unit/test_domain_calibration_release.py `
  tests/contract/test_wheel_runtime_assets.py
git diff --check fb8ea64...HEAD
```

Expected: all three commands return 0. Existing unrelated repository-wide debt is not imported into touched files.

- [ ] **Step 3: Build and inspect the wheel**

```powershell
New-Item -ItemType Directory -Force -Path 'build\evidence-trust-wheel' | Out-Null
uv build --wheel --out-dir 'build\evidence-trust-wheel'
uv run --frozen --with pytest==8.4.1 python -m pytest `
  tests/contract/test_wheel_runtime_assets.py `
  -q -p no:cacheprovider
```

Install the wheel into a fresh temporary environment and verify the packaged reference from outside the checkout:

```powershell
$wheel = Get-ChildItem -LiteralPath 'build\evidence-trust-wheel' -Filter '*.whl' |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$installRoot = Join-Path $env:TEMP ("mingli-019-evidence-" + [guid]::NewGuid())
uv venv $installRoot --python 3.12
$installedPython = Join-Path $installRoot 'Scripts\python.exe'
uv pip install --python $installedPython --no-deps $wheel.FullName
$probe = @'
from hashlib import sha256
import json
from pathlib import Path
import sysconfig

asset = (
    Path(sysconfig.get_paths()["purelib"])
    / "mingli_engine"
    / "data"
    / "domain_calibration"
    / "verified_pillar_expectations_v2.json"
)
payload = asset.read_bytes()
root = json.loads(payload.decode("utf-8"))
assert root["suite_version"] == "domain-calibration-observation-suite-v2"
assert root["records"][0]["expected_pillars"] == ["丙子", "庚子", "丙戌", "癸巳"]
print(sha256(payload).hexdigest())
'@
& $installedPython -c $probe
```

Expected: one wheel is built, the contract suite passes, and the isolated installed probe prints one SHA-256 hash without importing the source checkout.

- [ ] **Step 4: Run the full suite and compare with the closure baseline**

```powershell
uv run --frozen --with pytest==8.4.1 python -m pytest `
  -q -p no:cacheprovider
```

Expected: no new calibration, packaging, or application failures. If the known closure environment failures remain, classify them separately: missing installed-wheel interpreter, missing external material paths, and materials-audit integration. Do not call the whole suite green while any failure remains.

- [ ] **Step 5: Request independent two-part review**

Use two fresh reviewers:

1. specification reviewer: compare implementation with all 12 design sections and ten adversarial invariants;
2. code-quality reviewer: search for any dataflow from acceptable/required/adjudication fields into actual observations, verify actual pillar comparison, and inspect package isolation.

Fix every Critical or Important finding through a failing test, minimal implementation, focused verification, and a separate commit. Re-run Steps 1–4 after fixes.

- [ ] **Step 6: Verify original dirty worktrees again**

Repeat Task 1 Step 2. Expected: exact same status entries and tracked-file SHA-256 values as before isolation.

- [ ] **Step 7: Report the Stage 1 checkpoint to the user**

Report exactly:

1. completed: calibration can no longer certify itself from expected labels;
2. evidence: adversarial suite, real pillar comparison, wheel manifest, commit list, and independent reviews;
3. risk: Feature 019 is still not releasable because claim-level evidence traces and source-grounded hard gates remain incomplete;
4. user's one next action: approve starting Stage 2, the source-rule tracing and hard-gate implementation.

## Plan Self-Review

- Design sections 1–5 map to Task 1 and Execution Rules.
- Observation model, snapshot, registry, canonical values, and trace rules map to Tasks 2–5.
- Actual pillar comparison maps to Tasks 2 and 6.
- All ten adversarial invariants map to Task 7.
- Error handling maps to Tasks 3–5.
- Unit, integration, packaging, installed-artifact, static, full-suite, and independent-review gates map to Tasks 8–9.
- Historical asset immutability maps to Task 8 Step 4.
- Beginner-facing checkpoint protocol maps to Tasks 1 Step 7 and 9 Step 7.
- No Feature 020, release version, final baseline, tag, push, deletion, or raw-material work is included.
