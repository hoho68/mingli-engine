# Bazi Domain Calibration And Benchmark V2 Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Do not use sealed holdout data, do not modify Feature 019 artifacts, and stop immediately if the Feature 019 closure gate fails.

**Goal:** Freeze the Feature 020 V2 calibration protocol: layered assertion DTOs, benchmark split governance, expert workflow DTOs, metrics/error/release DTOs, canonical JSON, strict loaders, privacy checks, package-resource validation, and V1-to-V2 migration protocol.

**Architecture:** Extend the existing `domain_calibration_v2_models.py` and `domain_calibration_v2.py` style: frozen dataclasses, literal schema identities, tuple normalization, exact field validation, canonical JSON bytes, and read-only package resources. Keep migration code separate in `domain_calibration_v2_migration.py` so the protocol can map V1 artifacts without changing engine rules or benchmark labels. This plan creates protocol infrastructure only; relabeling, expert pilot, Benchmark V1 data growth, rule correction, and sealed evaluation are gated child plans in the master roadmap.

**Tech Stack:** Python 3.12+, standard library dataclasses, `typing.Literal`, `json`, `hashlib.sha256`, `importlib.resources`, existing `mingli_engine.domain_calibration` canonical helpers, pytest 8.4.1, mypy 1.17.1, Ruff 0.12.11.

---

## Scope Check

This child plan implements only Phase 1: Protocol And Migration. It creates schemas, validators, and migration machinery. It does not create the 300 assertion benchmark, does not expose sealed holdout data, does not perform expert labeling, does not compute a real Error Matrix beyond migration smoke checks, and does not change domain rules.

## File Structure

- Modify: `src/mingli_engine/domain_calibration_v2_models.py`  
  Owns V2 literal values, frozen DTOs, exact-field model validation, tuple normalization, and privacy/hash invariants.
- Modify: `src/mingli_engine/domain_calibration_v2.py`  
  Owns strict canonical JSON loading, duplicate-key rejection, file envelope validation, split governance checks, and package-resource access.
- Create: `src/mingli_engine/domain_calibration_v2_migration.py`  
  Owns V1-to-V2 migration protocol functions. It maps existing V1 assertions into draft V2 assertion records without modifying engine rules or claiming expert labels.
- Create: `tests/unit/test_domain_calibration_v2_protocol_models.py`  
  Tests exact DTO fields, literal values, frozen behavior, label status, layer, split, school scope, and privacy validation.
- Create: `tests/unit/test_domain_calibration_v2_loader.py`  
  Tests canonical JSON, duplicate key, non-finite number, exact envelope fields, hash mismatch, and forbidden privacy data rejection.
- Create: `tests/unit/test_domain_calibration_v2_split_governance.py`  
  Tests split manifest roles, access declarations, leakage invalidation, permitted metric uses, and sealed holdout protection.
- Create: `tests/unit/test_domain_calibration_v2_migration_protocol.py`  
  Tests V1-to-V2 migration defaults, explicit unmigrated status, unchanged-engine boundary, and no fabricated Error Matrix content.
- Create: `tests/integration/test_domain_calibration_v2_protocol_package.py`  
  Tests that V2 protocol resources load from package resources and do not rely on checkout paths.

## Standard Test Prologue

Run this before every pytest command:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
```

## Task 0: Enforce Feature 019 Closure Before Feature 020 Protocol Work

**Files:**
- Create: `tests/unit/test_domain_calibration_v2_prerequisites.py`
- Create: `src/mingli_engine/domain_calibration_v2_prerequisites.py`

- [ ] **Step 1: Write the failing prerequisite test**

Create `tests/unit/test_domain_calibration_v2_prerequisites.py`:

```python
from __future__ import annotations

from mingli_engine.domain_calibration_v2_prerequisites import (
    Feature020PrerequisiteStatus,
    verify_feature_020_prerequisites,
)


def test_feature_020_requires_closed_feature_019() -> None:
    status = verify_feature_020_prerequisites()
    assert isinstance(status, Feature020PrerequisiteStatus)
    assert status.package_version == "0.2.0"
    assert status.feature_019_formal_path.endswith(
        "specs/019-bazi-domain-validation-and-application-v1"
    )
    assert status.feature_019_closed is True
    assert status.feature_020_allowed_to_start is True
    assert status.blockers == ()
```

- [ ] **Step 2: Run the test to verify it fails**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_prerequisites.py -q -p no:cacheprovider
```

Expected: FAIL with `ModuleNotFoundError: No module named 'mingli_engine.domain_calibration_v2_prerequisites'`.

- [ ] **Step 3: Write the minimal prerequisite module**

Create `src/mingli_engine/domain_calibration_v2_prerequisites.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


@dataclass(frozen=True)
class Feature020PrerequisiteStatus:
    package_version: str
    feature_019_formal_path: str
    feature_019_closed: bool
    feature_020_allowed_to_start: bool
    blockers: tuple[str, ...]


def _package_version() -> str:
    try:
        return version("mingli-engine")
    except PackageNotFoundError:
        pyproject = Path("pyproject.toml")
        if not pyproject.exists():
            return "unknown"
        for line in pyproject.read_text(encoding="utf-8").splitlines():
            if line.startswith("version = "):
                return line.split("=", 1)[1].strip().strip('"')
        return "unknown"


def verify_feature_020_prerequisites(
    *,
    repo_root: Path | None = None,
) -> Feature020PrerequisiteStatus:
    root = repo_root or Path.cwd()
    formal = root / "specs" / "019-bazi-domain-validation-and-application-v1"
    draft = root / "specs" / "_drafts" / "019-bazi-domain-validation-and-application-v1"
    package_version = _package_version()
    blockers: list[str] = []
    if package_version != "0.2.0":
        blockers.append("Feature 019 package version is not 0.2.0")
    if not formal.exists():
        blockers.append("Feature 019 formal Spec Kit path is missing")
    if draft.exists():
        blockers.append("Feature 019 still has a draft Spec Kit path")
    closed = not blockers
    return Feature020PrerequisiteStatus(
        package_version=package_version,
        feature_019_formal_path=str(formal),
        feature_019_closed=closed,
        feature_020_allowed_to_start=closed,
        blockers=tuple(blockers),
    )
```

- [ ] **Step 4: Run the prerequisite test**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_prerequisites.py -q -p no:cacheprovider
```

Expected before Feature 019 closure: FAIL with an assertion showing blockers. Stop execution here and return to Feature 019 closure. Expected after Feature 019 closure: PASS with `1 passed`.

- [ ] **Step 5: Run focused regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_project_completion.py tests/contract/test_project_completion_cli_contract.py tests/unit/test_domain_calibration_v2_prerequisites.py -q -p no:cacheprovider
```

Expected after Feature 019 closure: PASS for project completion and prerequisite tests.

- [ ] **Step 6: Commit**

```powershell
git add src/mingli_engine/domain_calibration_v2_prerequisites.py tests/unit/test_domain_calibration_v2_prerequisites.py
git commit -m "test: gate feature 020 on feature 019 closure"
```

Expected: commit created only after the gate is green.

## Task 1: Add Protocol Literals And Exact DTO Field Contracts

**Files:**
- Modify: `src/mingli_engine/domain_calibration_v2_models.py`
- Create: `tests/unit/test_domain_calibration_v2_protocol_models.py`

- [ ] **Step 1: Write the failing model contract test**

Create `tests/unit/test_domain_calibration_v2_protocol_models.py`:

```python
from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from mingli_engine.domain_calibration_v2_models import (
    BENCHMARK_ASSERTION_SCHEMA_V2,
    BENCHMARK_CASE_SCHEMA_V2,
    BENCHMARK_SPLIT_MANIFEST_SCHEMA_V2,
    DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
    DOMAIN_CALIBRATION_SUITE_V2,
    CalibrationAssertionV2,
    CalibrationCaseV2,
    BenchmarkSplitManifestV2,
)


HASH_A = "a" * 64
HASH_B = "b" * 64


def _case() -> CalibrationCaseV2:
    return CalibrationCaseV2(
        schema_version=BENCHMARK_CASE_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        benchmark_name=DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
        case_id="case-v2-001",
        case_version="case-v2",
        synthetic_case_facts={"day_master": "jia", "month_branch": "zi"},
        minimum_input_requirements=("birth_date", "birth_time", "gender"),
        source_lineage_hashes=(HASH_A,),
        contains_real_personal_data=False,
    )


def _assertion() -> CalibrationAssertionV2:
    return CalibrationAssertionV2(
        schema_version=BENCHMARK_ASSERTION_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        benchmark_name=DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
        assertion_id="assertion-v2-001",
        case_id="case-v2-001",
        layer="L2",
        rule_family="pattern_strength",
        school_scope=("ziping",),
        claim_concepts=("strength_tendency:balanced",),
        polarity="positive",
        conditions=("month command is available",),
        required_evidence_ids=("mingxue_pattern_strength_001",),
        acceptable_alternatives=("strength_tendency:slightly_weak",),
        explicit_contradictions=("strength_tendency:extreme_strong",),
        abstention_policy="abstain_when_required_evidence_missing",
        minimum_input_requirements=("birth_date", "birth_time", "gender"),
        confidence_band="medium",
        safety_critical=False,
        complexity_tier="compound",
        scenario_tags=("school_specific",),
        benchmark_split="development",
        label_status="acceptable_set",
    )


def _manifest() -> BenchmarkSplitManifestV2:
    return BenchmarkSplitManifestV2(
        schema_version=BENCHMARK_SPLIT_MANIFEST_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        benchmark_name=DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
        benchmark_version="benchmark-v1",
        split_role="development",
        case_ids=("case-v2-001",),
        assertion_ids=("assertion-v2-001",),
        canonical_payload_hashes=(HASH_A,),
        source_lineage_hashes=(HASH_B,),
        created_at="2026-07-14T00:00:00Z",
        frozen_at="2026-07-14T01:00:00Z",
        author_ids=("maintainer-001",),
        reviewer_ids=("reviewer-001",),
        adjudicator_ids=("adjudicator-001",),
        controller_ids=("controller-001",),
        engine_access_declarations=("engine_output_absent",),
        exposed_to_implementation_context=False,
        permitted_metric_uses=("debug_regression",),
        permitted_release_uses=(),
        privacy_declaration="synthetic data only",
    )


def test_protocol_models_have_exact_fields() -> None:
    assert tuple(item.name for item in fields(CalibrationCaseV2)) == (
        "schema_version",
        "suite_version",
        "benchmark_name",
        "case_id",
        "case_version",
        "synthetic_case_facts",
        "minimum_input_requirements",
        "source_lineage_hashes",
        "contains_real_personal_data",
    )
    assert tuple(item.name for item in fields(CalibrationAssertionV2)) == (
        "schema_version",
        "suite_version",
        "benchmark_name",
        "assertion_id",
        "case_id",
        "layer",
        "rule_family",
        "school_scope",
        "claim_concepts",
        "polarity",
        "conditions",
        "required_evidence_ids",
        "acceptable_alternatives",
        "explicit_contradictions",
        "abstention_policy",
        "minimum_input_requirements",
        "confidence_band",
        "safety_critical",
        "complexity_tier",
        "scenario_tags",
        "benchmark_split",
        "label_status",
    )
    assert tuple(item.name for item in fields(BenchmarkSplitManifestV2)) == (
        "schema_version",
        "suite_version",
        "benchmark_name",
        "benchmark_version",
        "split_role",
        "case_ids",
        "assertion_ids",
        "canonical_payload_hashes",
        "source_lineage_hashes",
        "created_at",
        "frozen_at",
        "author_ids",
        "reviewer_ids",
        "adjudicator_ids",
        "controller_ids",
        "engine_access_declarations",
        "exposed_to_implementation_context",
        "permitted_metric_uses",
        "permitted_release_uses",
        "privacy_declaration",
    )


def test_protocol_models_are_frozen_and_normalize_sequences() -> None:
    assertion = _assertion()
    assert assertion.school_scope == ("ziping",)
    assert assertion.acceptable_alternatives == ("strength_tendency:slightly_weak",)
    with pytest.raises(FrozenInstanceError):
        assertion.layer = "L3"  # type: ignore[misc]


@pytest.mark.parametrize(
    "changes",
    [
        {"layer": "L5"},
        {"benchmark_split": "public"},
        {"label_status": "single_truth"},
        {"confidence_band": "certain"},
        {"school_scope": ["ziping", "ziping"]},
        {"contains_real_personal_data": True},
    ],
)
def test_protocol_models_reject_invalid_boundaries(changes: dict[str, object]) -> None:
    values = _assertion().__dict__ | changes
    with pytest.raises((TypeError, ValueError)):
        CalibrationAssertionV2(**values)  # type: ignore[arg-type]


def test_split_manifest_rejects_sealed_holdout_developer_exposure() -> None:
    values = _manifest().__dict__ | {
        "split_role": "sealed_holdout",
        "exposed_to_implementation_context": True,
        "permitted_release_uses": ("final_release_evidence",),
    }
    with pytest.raises(ValueError, match="sealed holdout exposure invalidates split"):
        BenchmarkSplitManifestV2(**values)  # type: ignore[arg-type]
```

- [ ] **Step 2: Run the test to verify it fails**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_protocol_models.py -q -p no:cacheprovider
```

Expected: FAIL with `ImportError` for `CalibrationAssertionV2` or the new schema constants.

- [ ] **Step 3: Add protocol constants and DTOs**

Append these definitions to `src/mingli_engine/domain_calibration_v2_models.py` after the existing fixture classes:

```python
DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL: Literal[
    "Bazi Calibration Benchmark V1 (Internal)"
] = "Bazi Calibration Benchmark V1 (Internal)"
BENCHMARK_CASE_SCHEMA_V2: Literal[
    "domain-calibration-benchmark-case-v2"
] = "domain-calibration-benchmark-case-v2"
BENCHMARK_ASSERTION_SCHEMA_V2: Literal[
    "domain-calibration-benchmark-assertion-v2"
] = "domain-calibration-benchmark-assertion-v2"
BENCHMARK_SPLIT_MANIFEST_SCHEMA_V2: Literal[
    "domain-calibration-split-manifest-v2"
] = "domain-calibration-split-manifest-v2"

ReasoningLayerV2 = Literal["L0", "L1", "L2", "L3", "L4"]
BenchmarkSplitRoleV2 = Literal[
    "development", "validation", "sealed_holdout", "challenge"
]
LabelStatusV2 = Literal[
    "consensus",
    "acceptable_set",
    "school_dependent",
    "expert_disputed",
    "insufficient_input",
    "excluded",
]
ConfidenceBandV2 = Literal["low", "medium", "high"]
ComplexityTierV2 = Literal["simple", "compound", "adversarial"]
PolarityV2 = Literal["positive", "negative", "counterexample", "boundary"]

_LAYERS = frozenset({"L0", "L1", "L2", "L3", "L4"})
_SPLITS = frozenset({"development", "validation", "sealed_holdout", "challenge"})
_LABEL_STATUSES = frozenset(
    {
        "consensus",
        "acceptable_set",
        "school_dependent",
        "expert_disputed",
        "insufficient_input",
        "excluded",
    }
)
_CONFIDENCE_BANDS = frozenset({"low", "medium", "high"})
_COMPLEXITY_TIERS = frozenset({"simple", "compound", "adversarial"})
_POLARITIES = frozenset({"positive", "negative", "counterexample", "boundary"})


def _require_literal_member(value: object, allowed: frozenset[str], field_name: str) -> None:
    _require_string(value, field_name)
    if value not in allowed:
        raise ValueError(f"{field_name} is not supported")


def _require_bool(value: object, field_name: str) -> None:
    if type(value) is not bool:
        raise TypeError(f"{field_name} must be bool")


def _require_string_mapping(value: object, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"{field_name} must be a string-keyed dict")
    return dict(value)


@dataclass(frozen=True)
class CalibrationCaseV2:
    schema_version: Literal["domain-calibration-benchmark-case-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    benchmark_name: Literal["Bazi Calibration Benchmark V1 (Internal)"]
    case_id: str
    case_version: str
    synthetic_case_facts: dict[str, object]
    minimum_input_requirements: tuple[str, ...]
    source_lineage_hashes: tuple[str, ...]
    contains_real_personal_data: bool

    def __post_init__(self) -> None:
        if self.schema_version != BENCHMARK_CASE_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 benchmark case schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        if self.benchmark_name != DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL:
            raise ValueError("benchmark_name is not the internal benchmark")
        _require_string(self.case_id, "case_id")
        _require_string(self.case_version, "case_version")
        object.__setattr__(
            self,
            "synthetic_case_facts",
            _require_string_mapping(self.synthetic_case_facts, "synthetic_case_facts"),
        )
        object.__setattr__(
            self,
            "minimum_input_requirements",
            _string_tuple(self.minimum_input_requirements, "minimum_input_requirements"),
        )
        object.__setattr__(
            self,
            "source_lineage_hashes",
            _string_tuple(self.source_lineage_hashes, "source_lineage_hashes"),
        )
        for index, value in enumerate(self.source_lineage_hashes):
            _require_sha256(value, f"source_lineage_hashes[{index}]")
        _require_bool(self.contains_real_personal_data, "contains_real_personal_data")
        if self.contains_real_personal_data:
            raise ValueError("V2 tracked benchmark cases must be synthetic")


@dataclass(frozen=True)
class CalibrationAssertionV2:
    schema_version: Literal["domain-calibration-benchmark-assertion-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    benchmark_name: Literal["Bazi Calibration Benchmark V1 (Internal)"]
    assertion_id: str
    case_id: str
    layer: ReasoningLayerV2
    rule_family: str
    school_scope: tuple[str, ...]
    claim_concepts: tuple[str, ...]
    polarity: PolarityV2
    conditions: tuple[str, ...]
    required_evidence_ids: tuple[str, ...]
    acceptable_alternatives: tuple[str, ...]
    explicit_contradictions: tuple[str, ...]
    abstention_policy: str
    minimum_input_requirements: tuple[str, ...]
    confidence_band: ConfidenceBandV2
    safety_critical: bool
    complexity_tier: ComplexityTierV2
    scenario_tags: tuple[str, ...]
    benchmark_split: BenchmarkSplitRoleV2
    label_status: LabelStatusV2

    def __post_init__(self) -> None:
        if self.schema_version != BENCHMARK_ASSERTION_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 assertion schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        if self.benchmark_name != DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL:
            raise ValueError("benchmark_name is not the internal benchmark")
        _require_string(self.assertion_id, "assertion_id")
        _require_string(self.case_id, "case_id")
        _require_literal_member(self.layer, _LAYERS, "layer")
        _require_string(self.rule_family, "rule_family")
        _require_literal_member(self.polarity, _POLARITIES, "polarity")
        _require_string(self.abstention_policy, "abstention_policy")
        _require_literal_member(self.confidence_band, _CONFIDENCE_BANDS, "confidence_band")
        _require_bool(self.safety_critical, "safety_critical")
        _require_literal_member(self.complexity_tier, _COMPLEXITY_TIERS, "complexity_tier")
        _require_literal_member(self.benchmark_split, _SPLITS, "benchmark_split")
        _require_literal_member(self.label_status, _LABEL_STATUSES, "label_status")
        for field_name in (
            "school_scope",
            "claim_concepts",
            "conditions",
            "required_evidence_ids",
            "acceptable_alternatives",
            "explicit_contradictions",
            "minimum_input_requirements",
            "scenario_tags",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )


@dataclass(frozen=True)
class BenchmarkSplitManifestV2:
    schema_version: Literal["domain-calibration-split-manifest-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    benchmark_name: Literal["Bazi Calibration Benchmark V1 (Internal)"]
    benchmark_version: str
    split_role: BenchmarkSplitRoleV2
    case_ids: tuple[str, ...]
    assertion_ids: tuple[str, ...]
    canonical_payload_hashes: tuple[str, ...]
    source_lineage_hashes: tuple[str, ...]
    created_at: str
    frozen_at: str
    author_ids: tuple[str, ...]
    reviewer_ids: tuple[str, ...]
    adjudicator_ids: tuple[str, ...]
    controller_ids: tuple[str, ...]
    engine_access_declarations: tuple[str, ...]
    exposed_to_implementation_context: bool
    permitted_metric_uses: tuple[str, ...]
    permitted_release_uses: tuple[str, ...]
    privacy_declaration: str

    def __post_init__(self) -> None:
        if self.schema_version != BENCHMARK_SPLIT_MANIFEST_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 split manifest schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        if self.benchmark_name != DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL:
            raise ValueError("benchmark_name is not the internal benchmark")
        _require_string(self.benchmark_version, "benchmark_version")
        _require_literal_member(self.split_role, _SPLITS, "split_role")
        _require_string(self.created_at, "created_at")
        _require_string(self.frozen_at, "frozen_at")
        _require_bool(
            self.exposed_to_implementation_context,
            "exposed_to_implementation_context",
        )
        _require_string(self.privacy_declaration, "privacy_declaration")
        for field_name in (
            "case_ids",
            "assertion_ids",
            "canonical_payload_hashes",
            "source_lineage_hashes",
            "author_ids",
            "reviewer_ids",
            "adjudicator_ids",
            "controller_ids",
            "engine_access_declarations",
            "permitted_metric_uses",
            "permitted_release_uses",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )
        for field_name in ("canonical_payload_hashes", "source_lineage_hashes"):
            for index, value in enumerate(getattr(self, field_name)):
                _require_sha256(value, f"{field_name}[{index}]")
        if self.split_role == "sealed_holdout" and self.exposed_to_implementation_context:
            raise ValueError("sealed holdout exposure invalidates split")
```

- [ ] **Step 4: Run the model contract test**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_protocol_models.py -q -p no:cacheprovider
```

Expected: PASS with all protocol model tests green.

- [ ] **Step 5: Run focused regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_models.py tests/unit/test_domain_calibration_v2_fixture_models.py tests/unit/test_domain_calibration_v2_protocol_models.py -q -p no:cacheprovider
```

Expected: PASS for existing v2 fixture/model tests and new protocol model tests.

- [ ] **Step 6: Commit**

```powershell
git add src/mingli_engine/domain_calibration_v2_models.py tests/unit/test_domain_calibration_v2_protocol_models.py
git commit -m "feat: freeze domain calibration v2 protocol models"
```

Expected: commit created with only the model and test files staged.

## Task 2: Add Expert Review And Adjudication DTOs

**Files:**
- Modify: `src/mingli_engine/domain_calibration_v2_models.py`
- Modify: `tests/unit/test_domain_calibration_v2_protocol_models.py`

- [ ] **Step 1: Extend the failing test with review and adjudication DTOs**

Append to `tests/unit/test_domain_calibration_v2_protocol_models.py`:

```python
from mingli_engine.domain_calibration_v2_models import (
    ADJUDICATION_RECORD_SCHEMA_V2,
    EXPERT_REVIEW_SCHEMA_V2,
    ExpertReviewV2,
    AdjudicationRecordV2,
)


def test_expert_review_and_adjudication_have_exact_fields() -> None:
    assert tuple(item.name for item in fields(ExpertReviewV2)) == (
        "schema_version",
        "suite_version",
        "review_id",
        "round_id",
        "reviewer_id",
        "reviewer_school_scope",
        "assertion_id",
        "packet_sha256",
        "candidate_output_sha256",
        "label_status",
        "accepted_claim_concepts",
        "conditions",
        "acceptable_alternatives",
        "explicit_contradictions",
        "confidence_band",
        "evidence_ids",
        "abstention_decision",
        "structural_compatibility",
        "safety_flags",
        "engine_output_seen",
        "peer_labels_seen",
        "conflict_disclosure_id",
    )
    assert tuple(item.name for item in fields(AdjudicationRecordV2)) == (
        "schema_version",
        "suite_version",
        "adjudication_id",
        "assertion_id",
        "review_ids",
        "final_label_status",
        "common_core_claims",
        "accepted_alternatives",
        "school_conflicts",
        "expert_disagreement_level",
        "excluded_from_single_answer_supervision",
        "change_log",
        "adjudicator_ids",
        "engine_output_seen",
    )


def test_expert_review_preserves_blindness_and_adjudication_blocks_engine_influence() -> None:
    review = ExpertReviewV2(
        schema_version=EXPERT_REVIEW_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        review_id="review-v2-001",
        round_id="round-a",
        reviewer_id="reviewer-ziping-001",
        reviewer_school_scope=("ziping",),
        assertion_id="assertion-v2-001",
        packet_sha256=HASH_A,
        candidate_output_sha256=None,
        label_status="consensus",
        accepted_claim_concepts=("strength_tendency:balanced",),
        conditions=("month command available",),
        acceptable_alternatives=(),
        explicit_contradictions=("strength_tendency:extreme_strong",),
        confidence_band="high",
        evidence_ids=("mingxue_pattern_strength_001",),
        abstention_decision="score",
        structural_compatibility="compatible",
        safety_flags=(),
        engine_output_seen=False,
        peer_labels_seen=False,
        conflict_disclosure_id="conflict-none-001",
    )
    assert review.round_id == "round-a"
    with pytest.raises(FrozenInstanceError):
        review.peer_labels_seen = True  # type: ignore[misc]

    with pytest.raises(ValueError, match="engine output must not influence adjudication"):
        AdjudicationRecordV2(
            schema_version=ADJUDICATION_RECORD_SCHEMA_V2,
            suite_version=DOMAIN_CALIBRATION_SUITE_V2,
            adjudication_id="adjudication-v2-001",
            assertion_id="assertion-v2-001",
            review_ids=("review-v2-001",),
            final_label_status="consensus",
            common_core_claims=("strength_tendency:balanced",),
            accepted_alternatives=(),
            school_conflicts=(),
            expert_disagreement_level="low",
            excluded_from_single_answer_supervision=False,
            change_log=("preserved consensus label",),
            adjudicator_ids=("adjudicator-001",),
            engine_output_seen=True,
        )
```

- [ ] **Step 2: Run the test to verify it fails**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_protocol_models.py -q -p no:cacheprovider
```

Expected: FAIL with `ImportError` for `ExpertReviewV2`.

- [ ] **Step 3: Add review and adjudication DTOs**

Append to `src/mingli_engine/domain_calibration_v2_models.py`:

```python
EXPERT_REVIEW_SCHEMA_V2: Literal[
    "domain-calibration-expert-review-v2"
] = "domain-calibration-expert-review-v2"
ADJUDICATION_RECORD_SCHEMA_V2: Literal[
    "domain-calibration-adjudication-v2"
] = "domain-calibration-adjudication-v2"

ReviewRoundV2 = Literal["round-a", "round-b"]
ExpertDisagreementLevelV2 = Literal["low", "medium", "high"]

_REVIEW_ROUNDS = frozenset({"round-a", "round-b"})
_DISAGREEMENT_LEVELS = frozenset({"low", "medium", "high"})


@dataclass(frozen=True)
class ExpertReviewV2:
    schema_version: Literal["domain-calibration-expert-review-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    review_id: str
    round_id: ReviewRoundV2
    reviewer_id: str
    reviewer_school_scope: tuple[str, ...]
    assertion_id: str
    packet_sha256: str
    candidate_output_sha256: str | None
    label_status: LabelStatusV2
    accepted_claim_concepts: tuple[str, ...]
    conditions: tuple[str, ...]
    acceptable_alternatives: tuple[str, ...]
    explicit_contradictions: tuple[str, ...]
    confidence_band: ConfidenceBandV2
    evidence_ids: tuple[str, ...]
    abstention_decision: str
    structural_compatibility: str
    safety_flags: tuple[str, ...]
    engine_output_seen: bool
    peer_labels_seen: bool
    conflict_disclosure_id: str

    def __post_init__(self) -> None:
        if self.schema_version != EXPERT_REVIEW_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 expert review schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        _require_string(self.review_id, "review_id")
        _require_literal_member(self.round_id, _REVIEW_ROUNDS, "round_id")
        _require_string(self.reviewer_id, "reviewer_id")
        _require_string(self.assertion_id, "assertion_id")
        _require_sha256(self.packet_sha256, "packet_sha256")
        if self.candidate_output_sha256 is not None:
            _require_sha256(self.candidate_output_sha256, "candidate_output_sha256")
        _require_literal_member(self.label_status, _LABEL_STATUSES, "label_status")
        _require_literal_member(self.confidence_band, _CONFIDENCE_BANDS, "confidence_band")
        _require_string(self.abstention_decision, "abstention_decision")
        _require_string(self.structural_compatibility, "structural_compatibility")
        _require_bool(self.engine_output_seen, "engine_output_seen")
        _require_bool(self.peer_labels_seen, "peer_labels_seen")
        _require_string(self.conflict_disclosure_id, "conflict_disclosure_id")
        if self.round_id == "round-a" and self.candidate_output_sha256 is not None:
            raise ValueError("Round A must not include candidate output")
        if self.round_id == "round-a" and self.engine_output_seen:
            raise ValueError("Round A must be independent of engine output")
        for field_name in (
            "reviewer_school_scope",
            "accepted_claim_concepts",
            "conditions",
            "acceptable_alternatives",
            "explicit_contradictions",
            "evidence_ids",
            "safety_flags",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )


@dataclass(frozen=True)
class AdjudicationRecordV2:
    schema_version: Literal["domain-calibration-adjudication-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    adjudication_id: str
    assertion_id: str
    review_ids: tuple[str, ...]
    final_label_status: LabelStatusV2
    common_core_claims: tuple[str, ...]
    accepted_alternatives: tuple[str, ...]
    school_conflicts: tuple[str, ...]
    expert_disagreement_level: ExpertDisagreementLevelV2
    excluded_from_single_answer_supervision: bool
    change_log: tuple[str, ...]
    adjudicator_ids: tuple[str, ...]
    engine_output_seen: bool

    def __post_init__(self) -> None:
        if self.schema_version != ADJUDICATION_RECORD_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 adjudication schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        _require_string(self.adjudication_id, "adjudication_id")
        _require_string(self.assertion_id, "assertion_id")
        _require_literal_member(self.final_label_status, _LABEL_STATUSES, "final_label_status")
        _require_literal_member(
            self.expert_disagreement_level,
            _DISAGREEMENT_LEVELS,
            "expert_disagreement_level",
        )
        _require_bool(
            self.excluded_from_single_answer_supervision,
            "excluded_from_single_answer_supervision",
        )
        _require_bool(self.engine_output_seen, "engine_output_seen")
        if self.engine_output_seen:
            raise ValueError("engine output must not influence adjudication")
        if self.final_label_status in {"expert_disputed", "insufficient_input", "excluded"}:
            if not self.excluded_from_single_answer_supervision:
                raise ValueError("unstable targets must be excluded from single-answer supervision")
        for field_name in (
            "review_ids",
            "common_core_claims",
            "accepted_alternatives",
            "school_conflicts",
            "change_log",
            "adjudicator_ids",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )
```

- [ ] **Step 4: Run the protocol model tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_protocol_models.py -q -p no:cacheprovider
```

Expected: PASS for assertion, case, split, review, and adjudication DTO tests.

- [ ] **Step 5: Run focused regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_models.py tests/unit/test_domain_calibration_v2_fixture_models.py tests/unit/test_domain_calibration_v2_protocol_models.py -q -p no:cacheprovider
```

Expected: PASS for existing v2 tests and review/adjudication DTO tests.

- [ ] **Step 6: Commit**

```powershell
git add src/mingli_engine/domain_calibration_v2_models.py tests/unit/test_domain_calibration_v2_protocol_models.py
git commit -m "feat: add calibration v2 expert review protocol"
```

Expected: commit created with only protocol model changes staged.

## Task 3: Add Metric, Error Matrix, And Release DTOs

**Files:**
- Modify: `src/mingli_engine/domain_calibration_v2_models.py`
- Modify: `tests/unit/test_domain_calibration_v2_protocol_models.py`

- [ ] **Step 1: Add failing tests for metric, error, and release DTOs**

Append to `tests/unit/test_domain_calibration_v2_protocol_models.py`:

```python
from mingli_engine.domain_calibration_v2_models import (
    ERROR_MATRIX_ENTRY_SCHEMA_V2,
    METRIC_SNAPSHOT_SCHEMA_V2,
    RELEASE_DECISION_SCHEMA_V2,
    ErrorMatrixEntryV2,
    MetricSnapshotV2,
    ReleaseDecisionV2,
)


def test_metric_error_and_release_dtos_are_layered_and_version_bound() -> None:
    metric = MetricSnapshotV2(
        schema_version=METRIC_SNAPSHOT_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        snapshot_id="metric-v2-001",
        benchmark_version="benchmark-v1",
        split_role="validation",
        version_set_id="versions-0.3.0",
        layer="L2",
        rule_family="pattern_strength",
        school_scope=("ziping",),
        denominator=12,
        numerator=10,
        rate=0.8333333333333334,
        expert_target_stability="stable_acceptable_set",
        high_confidence_error_count=1,
        abstention_audit_count=0,
    )
    assert metric.rate == 0.8333333333333334

    error = ErrorMatrixEntryV2(
        schema_version=ERROR_MATRIX_ENTRY_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        error_id="error-v2-001",
        assertion_id="assertion-v2-001",
        case_id="case-v2-001",
        layer="L2",
        rule_family="pattern_strength",
        school_scope=("ziping",),
        complexity_tier="compound",
        scenario_tags=("school_specific",),
        confidence_band="high",
        benchmark_split="validation",
        primary_error_code="acceptable_alternative_missed",
        contributing_error_codes=("confidence_too_high",),
        evidence_source_ids=("mingxue_pattern_strength_001",),
        sealed_holdout_identity_exposed=False,
    )
    assert error.primary_error_code == "acceptable_alternative_missed"

    release = ReleaseDecisionV2(
        schema_version=RELEASE_DECISION_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        release_id="release-v2-001",
        application_version="0.3.0",
        benchmark_version="benchmark-v1",
        final_wheel_sha256=HASH_A,
        sealed_manifest_sha256=HASH_B,
        exact_version_set_id="versions-0.3.0",
        release_status="blocked",
        blockers=("L2 acceptable-set threshold below gate",),
        benchmark_card_path="docs/superpowers/reports/benchmark-card-v1-internal.md",
        claim_boundary="internal traditional-method conformance benchmark",
    )
    assert release.release_status == "blocked"
```

- [ ] **Step 2: Run the test to verify it fails**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_protocol_models.py -q -p no:cacheprovider
```

Expected: FAIL with `ImportError` for `MetricSnapshotV2`.

- [ ] **Step 3: Add metric, error, and release DTOs**

Append to `src/mingli_engine/domain_calibration_v2_models.py`:

```python
METRIC_SNAPSHOT_SCHEMA_V2: Literal[
    "domain-calibration-metric-snapshot-v2"
] = "domain-calibration-metric-snapshot-v2"
ERROR_MATRIX_ENTRY_SCHEMA_V2: Literal[
    "domain-calibration-error-matrix-entry-v2"
] = "domain-calibration-error-matrix-entry-v2"
RELEASE_DECISION_SCHEMA_V2: Literal[
    "domain-calibration-release-decision-v2"
] = "domain-calibration-release-decision-v2"

ErrorCodeV2 = Literal[
    "calendar_fact_error",
    "derived_fact_error",
    "rule_condition_missing",
    "rule_condition_invented",
    "school_misattribution",
    "acceptable_alternative_missed",
    "contradicted_consensus",
    "false_positive_conclusion",
    "false_negative_conclusion",
    "incorrect_abstention",
    "missing_abstention",
    "confidence_too_high",
    "confidence_too_low",
    "evidence_trace_error",
    "rule_trace_error",
    "expression_overreach",
    "safety_boundary_error",
    "evaluation_label_defect",
    "expert_target_unstable",
]
ReleaseStatusV2 = Literal["blocked", "ready", "ready_with_guardrails"]

_ERROR_CODES = frozenset(
    {
        "calendar_fact_error",
        "derived_fact_error",
        "rule_condition_missing",
        "rule_condition_invented",
        "school_misattribution",
        "acceptable_alternative_missed",
        "contradicted_consensus",
        "false_positive_conclusion",
        "false_negative_conclusion",
        "incorrect_abstention",
        "missing_abstention",
        "confidence_too_high",
        "confidence_too_low",
        "evidence_trace_error",
        "rule_trace_error",
        "expression_overreach",
        "safety_boundary_error",
        "evaluation_label_defect",
        "expert_target_unstable",
    }
)
_RELEASE_STATUSES_V2 = frozenset({"blocked", "ready", "ready_with_guardrails"})


def _require_count(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be int")
    if value < 0:
        raise ValueError(f"{field_name} must be nonnegative")


def _require_rate(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be numeric")
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{field_name} must be between 0 and 1")


@dataclass(frozen=True)
class MetricSnapshotV2:
    schema_version: Literal["domain-calibration-metric-snapshot-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    snapshot_id: str
    benchmark_version: str
    split_role: BenchmarkSplitRoleV2
    version_set_id: str
    layer: ReasoningLayerV2
    rule_family: str
    school_scope: tuple[str, ...]
    denominator: int
    numerator: int
    rate: float
    expert_target_stability: str
    high_confidence_error_count: int
    abstention_audit_count: int

    def __post_init__(self) -> None:
        if self.schema_version != METRIC_SNAPSHOT_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 metric schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        _require_string(self.snapshot_id, "snapshot_id")
        _require_string(self.benchmark_version, "benchmark_version")
        _require_literal_member(self.split_role, _SPLITS, "split_role")
        _require_string(self.version_set_id, "version_set_id")
        _require_literal_member(self.layer, _LAYERS, "layer")
        _require_string(self.rule_family, "rule_family")
        object.__setattr__(self, "school_scope", _string_tuple(self.school_scope, "school_scope"))
        _require_count(self.denominator, "denominator")
        _require_count(self.numerator, "numerator")
        if self.denominator == 0:
            raise ValueError("denominator must be positive")
        if self.numerator > self.denominator:
            raise ValueError("numerator must not exceed denominator")
        _require_rate(self.rate, "rate")
        _require_string(self.expert_target_stability, "expert_target_stability")
        _require_count(self.high_confidence_error_count, "high_confidence_error_count")
        _require_count(self.abstention_audit_count, "abstention_audit_count")


@dataclass(frozen=True)
class ErrorMatrixEntryV2:
    schema_version: Literal["domain-calibration-error-matrix-entry-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    error_id: str
    assertion_id: str
    case_id: str
    layer: ReasoningLayerV2
    rule_family: str
    school_scope: tuple[str, ...]
    complexity_tier: ComplexityTierV2
    scenario_tags: tuple[str, ...]
    confidence_band: ConfidenceBandV2
    benchmark_split: BenchmarkSplitRoleV2
    primary_error_code: ErrorCodeV2
    contributing_error_codes: tuple[str, ...]
    evidence_source_ids: tuple[str, ...]
    sealed_holdout_identity_exposed: bool

    def __post_init__(self) -> None:
        if self.schema_version != ERROR_MATRIX_ENTRY_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 error matrix schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        _require_string(self.error_id, "error_id")
        _require_string(self.assertion_id, "assertion_id")
        _require_string(self.case_id, "case_id")
        _require_literal_member(self.layer, _LAYERS, "layer")
        _require_string(self.rule_family, "rule_family")
        _require_literal_member(self.complexity_tier, _COMPLEXITY_TIERS, "complexity_tier")
        _require_literal_member(self.confidence_band, _CONFIDENCE_BANDS, "confidence_band")
        _require_literal_member(self.benchmark_split, _SPLITS, "benchmark_split")
        _require_literal_member(self.primary_error_code, _ERROR_CODES, "primary_error_code")
        _require_bool(self.sealed_holdout_identity_exposed, "sealed_holdout_identity_exposed")
        if self.sealed_holdout_identity_exposed:
            raise ValueError("sealed holdout identity must not be exposed")
        for field_name in (
            "school_scope",
            "scenario_tags",
            "contributing_error_codes",
            "evidence_source_ids",
        ):
            object.__setattr__(
                self,
                field_name,
                _string_tuple(getattr(self, field_name), field_name),
            )
        for code in self.contributing_error_codes:
            _require_literal_member(code, _ERROR_CODES, "contributing_error_codes")


@dataclass(frozen=True)
class ReleaseDecisionV2:
    schema_version: Literal["domain-calibration-release-decision-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    release_id: str
    application_version: str
    benchmark_version: str
    final_wheel_sha256: str
    sealed_manifest_sha256: str
    exact_version_set_id: str
    release_status: ReleaseStatusV2
    blockers: tuple[str, ...]
    benchmark_card_path: str
    claim_boundary: str

    def __post_init__(self) -> None:
        if self.schema_version != RELEASE_DECISION_SCHEMA_V2:
            raise ValueError("schema_version is not the V2 release decision schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        _require_string(self.release_id, "release_id")
        _require_string(self.application_version, "application_version")
        _require_string(self.benchmark_version, "benchmark_version")
        _require_sha256(self.final_wheel_sha256, "final_wheel_sha256")
        _require_sha256(self.sealed_manifest_sha256, "sealed_manifest_sha256")
        _require_string(self.exact_version_set_id, "exact_version_set_id")
        _require_literal_member(self.release_status, _RELEASE_STATUSES_V2, "release_status")
        object.__setattr__(self, "blockers", _string_tuple(self.blockers, "blockers"))
        _require_string(self.benchmark_card_path, "benchmark_card_path")
        _require_string(self.claim_boundary, "claim_boundary")
        if "internal" not in self.claim_boundary:
            raise ValueError("release claim boundary must identify the benchmark as internal")
```

- [ ] **Step 4: Run the protocol model tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_protocol_models.py -q -p no:cacheprovider
```

Expected: PASS for all DTO model tests.

- [ ] **Step 5: Run focused regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_models.py tests/unit/test_domain_calibration_v2_fixture_models.py tests/unit/test_domain_calibration_v2_protocol_models.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add src/mingli_engine/domain_calibration_v2_models.py tests/unit/test_domain_calibration_v2_protocol_models.py
git commit -m "feat: add calibration v2 metric and release records"
```

Expected: commit created with DTO changes only.

## Task 4: Add Strict Canonical JSON Loader And V2 File Envelope

**Files:**
- Modify: `src/mingli_engine/domain_calibration_v2_models.py`
- Modify: `src/mingli_engine/domain_calibration_v2.py`
- Create: `tests/unit/test_domain_calibration_v2_loader.py`

- [ ] **Step 1: Write failing loader tests**

Create `tests/unit/test_domain_calibration_v2_loader.py`:

```python
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pytest

from mingli_engine.domain_calibration import canonical_json_bytes, records_payload_sha256
from mingli_engine.domain_calibration_v2 import (
    CalibrationProtocolErrorV2,
    load_v2_calibration_file,
)
from mingli_engine.domain_calibration_v2_models import (
    BENCHMARK_CASE_SCHEMA_V2,
    DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
    DOMAIN_CALIBRATION_SUITE_V2,
    V2_FILE_ENVELOPE_SCHEMA,
    CalibrationCaseV2,
    CalibrationFileEnvelopeV2,
)


HASH_A = "a" * 64


def _case() -> CalibrationCaseV2:
    return CalibrationCaseV2(
        schema_version=BENCHMARK_CASE_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        benchmark_name=DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
        case_id="case-v2-001",
        case_version="case-v2",
        synthetic_case_facts={"day_master": "jia"},
        minimum_input_requirements=("birth_date",),
        source_lineage_hashes=(HASH_A,),
        contains_real_personal_data=False,
    )


def _write(path: Path, records: list[dict[str, object]]) -> None:
    envelope = {
        "schema_version": V2_FILE_ENVELOPE_SCHEMA,
        "suite_version": DOMAIN_CALIBRATION_SUITE_V2,
        "benchmark_name": DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
        "record_schema_version": BENCHMARK_CASE_SCHEMA_V2,
        "generated_from": (HASH_A,),
        "contains_real_personal_data": False,
        "payload_sha256": records_payload_sha256(records),
        "records": records,
    }
    path.write_bytes(canonical_json_bytes(envelope))


def test_v2_loader_accepts_canonical_private_hashed_file(tmp_path: Path) -> None:
    path = tmp_path / "cases.json"
    _write(path, [asdict(_case())])
    envelope = load_v2_calibration_file(path, CalibrationCaseV2)
    assert isinstance(envelope, CalibrationFileEnvelopeV2)
    assert envelope.record_schema_version == BENCHMARK_CASE_SCHEMA_V2
    assert envelope.records[0].case_id == "case-v2-001"


@pytest.mark.parametrize(
    "payload",
    [
        b'{"schema_version":"domain-calibration-file-v2","schema_version":"x"}',
        b'{"number":NaN}',
        b'{ "schema_version" : "domain-calibration-file-v2" }',
    ],
)
def test_v2_loader_rejects_noncanonical_or_unsafe_json(
    tmp_path: Path,
    payload: bytes,
) -> None:
    path = tmp_path / "bad.json"
    path.write_bytes(payload)
    with pytest.raises(CalibrationProtocolErrorV2):
        load_v2_calibration_file(path, CalibrationCaseV2)


def test_v2_loader_rejects_hash_mismatch_and_personal_data(tmp_path: Path) -> None:
    path = tmp_path / "bad-hash.json"
    record = asdict(_case())
    envelope = {
        "schema_version": V2_FILE_ENVELOPE_SCHEMA,
        "suite_version": DOMAIN_CALIBRATION_SUITE_V2,
        "benchmark_name": DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
        "record_schema_version": BENCHMARK_CASE_SCHEMA_V2,
        "generated_from": (HASH_A,),
        "contains_real_personal_data": True,
        "payload_sha256": "b" * 64,
        "records": [record],
    }
    path.write_bytes(canonical_json_bytes(envelope))
    with pytest.raises(CalibrationProtocolErrorV2, match="personal data"):
        load_v2_calibration_file(path, CalibrationCaseV2)
```

- [ ] **Step 2: Run loader tests to verify they fail**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_loader.py -q -p no:cacheprovider
```

Expected: FAIL with `ImportError` for `CalibrationProtocolErrorV2` or `V2_FILE_ENVELOPE_SCHEMA`.

- [ ] **Step 3: Add the envelope DTO**

Append to `src/mingli_engine/domain_calibration_v2_models.py`:

```python
V2_FILE_ENVELOPE_SCHEMA: Literal[
    "domain-calibration-file-v2"
] = "domain-calibration-file-v2"


@dataclass(frozen=True)
class CalibrationFileEnvelopeV2:
    schema_version: Literal["domain-calibration-file-v2"]
    suite_version: Literal["domain-calibration-suite-v2"]
    benchmark_name: Literal["Bazi Calibration Benchmark V1 (Internal)"]
    record_schema_version: str
    generated_from: tuple[str, ...]
    contains_real_personal_data: bool
    payload_sha256: str
    records: tuple[object, ...]

    def __post_init__(self) -> None:
        if self.schema_version != V2_FILE_ENVELOPE_SCHEMA:
            raise ValueError("schema_version is not the V2 file envelope schema")
        if self.suite_version != DOMAIN_CALIBRATION_SUITE_V2:
            raise ValueError("suite_version is not the V2 calibration suite")
        if self.benchmark_name != DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL:
            raise ValueError("benchmark_name is not the internal benchmark")
        _require_string(self.record_schema_version, "record_schema_version")
        object.__setattr__(self, "generated_from", _string_tuple(self.generated_from, "generated_from"))
        for index, value in enumerate(self.generated_from):
            _require_sha256(value, f"generated_from[{index}]")
        _require_bool(self.contains_real_personal_data, "contains_real_personal_data")
        if self.contains_real_personal_data:
            raise ValueError("V2 calibration files must not contain personal data")
        _require_sha256(self.payload_sha256, "payload_sha256")
        if not isinstance(self.records, (list, tuple)):
            raise TypeError("records must be a sequence")
        object.__setattr__(self, "records", tuple(self.records))
```

- [ ] **Step 4: Add strict loader functions**

Add to `src/mingli_engine/domain_calibration_v2.py`:

```python
from dataclasses import asdict

from mingli_engine.domain_calibration_v2_models import (
    DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
    V2_FILE_ENVELOPE_SCHEMA,
    CalibrationFileEnvelopeV2,
)


class CalibrationProtocolErrorV2(ValueError):
    pass


class _DuplicateKeyErrorV2(ValueError):
    pass


def _reject_duplicate_keys_v2(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyErrorV2("duplicate key")
        result[key] = value
    return result


def _reject_nonfinite_v2(_value: str) -> object:
    raise ValueError("non-finite number")


def _strict_canonical_json_v2(payload: bytes) -> object:
    try:
        decoded = payload.decode("utf-8", errors="strict")
        value = json.loads(
            decoded,
            object_pairs_hook=_reject_duplicate_keys_v2,
            parse_constant=_reject_nonfinite_v2,
        )
    except (UnicodeError, ValueError, RecursionError):
        raise CalibrationProtocolErrorV2("calibration file is not strict JSON") from None
    if canonical_json_bytes(value) != payload:
        raise CalibrationProtocolErrorV2("calibration file is not canonical JSON")
    return value


def load_v2_calibration_file(path: Path, record_type: type[object]) -> CalibrationFileEnvelopeV2:
    value = _strict_canonical_json_v2(path.read_bytes())
    expected_fields = {
        "schema_version",
        "suite_version",
        "benchmark_name",
        "record_schema_version",
        "generated_from",
        "contains_real_personal_data",
        "payload_sha256",
        "records",
    }
    if not isinstance(value, dict) or set(value) != expected_fields:
        raise CalibrationProtocolErrorV2("V2 file envelope fields are not exact")
    if value["schema_version"] != V2_FILE_ENVELOPE_SCHEMA:
        raise CalibrationProtocolErrorV2("V2 file envelope schema is invalid")
    if value["benchmark_name"] != DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL:
        raise CalibrationProtocolErrorV2("benchmark must remain internal")
    if value["contains_real_personal_data"] is not False:
        raise CalibrationProtocolErrorV2("V2 file contains personal data")
    records_value = value["records"]
    if not isinstance(records_value, list):
        raise CalibrationProtocolErrorV2("V2 file records must be a list")
    records = tuple(record_type(**item) for item in records_value)
    record_payload = [asdict(item) for item in records]
    if records_payload_sha256(record_payload) != value["payload_sha256"]:
        raise CalibrationProtocolErrorV2("V2 file payload hash mismatch")
    return CalibrationFileEnvelopeV2(
        schema_version=value["schema_version"],
        suite_version=value["suite_version"],
        benchmark_name=value["benchmark_name"],
        record_schema_version=value["record_schema_version"],
        generated_from=value["generated_from"],
        contains_real_personal_data=value["contains_real_personal_data"],
        payload_sha256=value["payload_sha256"],
        records=records,
    )
```

- [ ] **Step 5: Run loader tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_loader.py -q -p no:cacheprovider
```

Expected: PASS for canonical loader tests.

- [ ] **Step 6: Run focused regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_models.py tests/unit/test_domain_calibration_v2_fixture_models.py tests/unit/test_domain_calibration_v2_protocol_models.py tests/unit/test_domain_calibration_v2_loader.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 7: Commit**

```powershell
git add src/mingli_engine/domain_calibration_v2.py src/mingli_engine/domain_calibration_v2_models.py tests/unit/test_domain_calibration_v2_loader.py
git commit -m "feat: add strict calibration v2 file loader"
```

Expected: commit created with loader and model changes only.

## Task 5: Add Split Governance Validation

**Files:**
- Modify: `src/mingli_engine/domain_calibration_v2.py`
- Create: `tests/unit/test_domain_calibration_v2_split_governance.py`

- [ ] **Step 1: Write failing split governance tests**

Create `tests/unit/test_domain_calibration_v2_split_governance.py`:

```python
from __future__ import annotations

import pytest

from mingli_engine.domain_calibration_v2 import (
    CalibrationProtocolErrorV2,
    validate_split_manifest_v2,
)
from mingli_engine.domain_calibration_v2_models import (
    BENCHMARK_SPLIT_MANIFEST_SCHEMA_V2,
    DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
    DOMAIN_CALIBRATION_SUITE_V2,
    BenchmarkSplitManifestV2,
)


HASH_A = "a" * 64
HASH_B = "b" * 64


def _manifest(**changes: object) -> BenchmarkSplitManifestV2:
    values: dict[str, object] = {
        "schema_version": BENCHMARK_SPLIT_MANIFEST_SCHEMA_V2,
        "suite_version": DOMAIN_CALIBRATION_SUITE_V2,
        "benchmark_name": DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
        "benchmark_version": "benchmark-v1",
        "split_role": "sealed_holdout",
        "case_ids": ("case-v2-001",),
        "assertion_ids": ("assertion-v2-001",),
        "canonical_payload_hashes": (HASH_A,),
        "source_lineage_hashes": (HASH_B,),
        "created_at": "2026-07-14T00:00:00Z",
        "frozen_at": "2026-07-14T01:00:00Z",
        "author_ids": ("author-001",),
        "reviewer_ids": ("reviewer-001",),
        "adjudicator_ids": ("adjudicator-001",),
        "controller_ids": ("controller-001",),
        "engine_access_declarations": ("engine_output_absent",),
        "exposed_to_implementation_context": False,
        "permitted_metric_uses": ("final_release_evidence",),
        "permitted_release_uses": ("final_release_evidence",),
        "privacy_declaration": "synthetic data only",
    }
    values.update(changes)
    return BenchmarkSplitManifestV2(**values)  # type: ignore[arg-type]


def test_sealed_holdout_manifest_is_release_only_and_hidden() -> None:
    manifest = _manifest()
    validate_split_manifest_v2(manifest)


@pytest.mark.parametrize(
    "changes",
    [
        {"exposed_to_implementation_context": True},
        {"permitted_metric_uses": ("debug_regression",)},
        {"permitted_release_uses": ()},
    ],
)
def test_sealed_holdout_rejects_leakage_and_wrong_use(changes: dict[str, object]) -> None:
    with pytest.raises((ValueError, CalibrationProtocolErrorV2)):
        validate_split_manifest_v2(_manifest(**changes))


def test_development_split_cannot_be_final_release_evidence() -> None:
    manifest = _manifest(
        split_role="development",
        permitted_metric_uses=("debug_regression",),
        permitted_release_uses=("final_release_evidence",),
    )
    with pytest.raises(CalibrationProtocolErrorV2, match="development split"):
        validate_split_manifest_v2(manifest)
```

- [ ] **Step 2: Run split governance tests to verify they fail**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_split_governance.py -q -p no:cacheprovider
```

Expected: FAIL with `ImportError` for `validate_split_manifest_v2`.

- [ ] **Step 3: Add split governance validation**

Add to `src/mingli_engine/domain_calibration_v2.py`:

```python
from mingli_engine.domain_calibration_v2_models import BenchmarkSplitManifestV2


def validate_split_manifest_v2(manifest: BenchmarkSplitManifestV2) -> None:
    if manifest.split_role == "sealed_holdout":
        if manifest.exposed_to_implementation_context:
            raise CalibrationProtocolErrorV2("sealed holdout exposure invalidates split")
        if manifest.permitted_release_uses != ("final_release_evidence",):
            raise CalibrationProtocolErrorV2("sealed holdout must be final release evidence")
        if "final_release_evidence" not in manifest.permitted_metric_uses:
            raise CalibrationProtocolErrorV2("sealed holdout metrics must be release-bound")
    if manifest.split_role == "development" and "final_release_evidence" in manifest.permitted_release_uses:
        raise CalibrationProtocolErrorV2("development split must not be final release evidence")
    if manifest.split_role == "challenge" and "headline_accuracy" in manifest.permitted_metric_uses:
        raise CalibrationProtocolErrorV2("challenge split must not feed headline accuracy")
    if manifest.privacy_declaration != "synthetic data only":
        raise CalibrationProtocolErrorV2("V2 benchmark manifests must declare synthetic data only")
```

- [ ] **Step 4: Run split governance tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_split_governance.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 5: Run focused regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_loader.py tests/unit/test_domain_calibration_v2_split_governance.py tests/unit/test_domain_calibration_v2_protocol_models.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add src/mingli_engine/domain_calibration_v2.py tests/unit/test_domain_calibration_v2_split_governance.py
git commit -m "feat: enforce calibration v2 split governance"
```

Expected: commit created with split governance changes only.

## Task 6: Add V1-To-V2 Migration Protocol Without Rule Changes

**Files:**
- Create: `src/mingli_engine/domain_calibration_v2_migration.py`
- Create: `tests/unit/test_domain_calibration_v2_migration_protocol.py`

- [ ] **Step 1: Write failing migration protocol tests**

Create `tests/unit/test_domain_calibration_v2_migration_protocol.py`:

```python
from __future__ import annotations

from mingli_engine.domain_calibration_models import CalibrationAssertion
from mingli_engine.domain_calibration_v2_migration import (
    MigrationDecisionV2,
    migrate_v1_assertion_to_v2,
)


def _v1_assertion(**changes: object) -> CalibrationAssertion:
    values: dict[str, object] = {
        "assertion_id": "assertion-001",
        "case_id": "case-001",
        "rule_family": "pattern_strength",
        "school_id": "ziping",
        "assertion_kind": "positive",
        "field_path": "$.result.calculation.pattern_candidates.status",
        "acceptable_statuses": ("computed",),
        "acceptable_values": ("follow_strength",),
        "required_rule_ids": ("patterns.follow_strength",),
        "required_evidence_ids": ("mingxue_pattern_strength_001",),
        "limitations": ("synthetic fixture",),
    }
    values.update(changes)
    return CalibrationAssertion(**values)  # type: ignore[arg-type]


def test_migration_marks_existing_v1_assertion_as_development_and_needing_relabel() -> None:
    decision = migrate_v1_assertion_to_v2(_v1_assertion())
    assert isinstance(decision, MigrationDecisionV2)
    assert decision.source_assertion_id == "assertion-001"
    assert decision.v2_assertion.assertion_id == "v2-assertion-001"
    assert decision.v2_assertion.layer == "L2"
    assert decision.v2_assertion.benchmark_split == "development"
    assert decision.v2_assertion.label_status == "insufficient_input"
    assert decision.requires_expert_relabel is True
    assert decision.rule_change_allowed is False
    assert decision.initial_error_matrix_claim == "not generated by migration"


def test_migration_does_not_fabricate_acceptable_alternatives_or_contradictions() -> None:
    decision = migrate_v1_assertion_to_v2(_v1_assertion())
    assert decision.v2_assertion.acceptable_alternatives == ()
    assert decision.v2_assertion.explicit_contradictions == ()
```

- [ ] **Step 2: Run migration tests to verify they fail**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_migration_protocol.py -q -p no:cacheprovider
```

Expected: FAIL with `ModuleNotFoundError` for `mingli_engine.domain_calibration_v2_migration`.

- [ ] **Step 3: Add migration protocol module**

Create `src/mingli_engine/domain_calibration_v2_migration.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from mingli_engine.domain_calibration_models import CalibrationAssertion
from mingli_engine.domain_calibration_v2_models import (
    BENCHMARK_ASSERTION_SCHEMA_V2,
    DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
    DOMAIN_CALIBRATION_SUITE_V2,
    CalibrationAssertionV2,
)


@dataclass(frozen=True)
class MigrationDecisionV2:
    source_assertion_id: str
    v2_assertion: CalibrationAssertionV2
    requires_expert_relabel: bool
    rule_change_allowed: bool
    initial_error_matrix_claim: str


_FIELD_LAYER_MAP = (
    ("pillars", "L0"),
    ("hidden_stems", "L1"),
    ("ten_god", "L1"),
    ("branch", "L1"),
    ("pattern", "L2"),
    ("useful_god", "L2"),
    ("taboo_god", "L2"),
    ("blind", "L2"),
    ("remedy", "L2"),
    ("report", "L3"),
    ("luck", "L4"),
)


def _infer_layer(assertion: CalibrationAssertion) -> str:
    text = f"{assertion.rule_family} {assertion.field_path}".lower()
    for marker, layer in _FIELD_LAYER_MAP:
        if marker in text:
            return layer
    return "L2"


def migrate_v1_assertion_to_v2(assertion: CalibrationAssertion) -> MigrationDecisionV2:
    school_scope = (assertion.school_id,) if assertion.school_id is not None else ("cross_school",)
    v2 = CalibrationAssertionV2(
        schema_version=BENCHMARK_ASSERTION_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        benchmark_name=DOMAIN_CALIBRATION_BENCHMARK_V1_INTERNAL,
        assertion_id=f"v2-{assertion.assertion_id}",
        case_id=assertion.case_id,
        layer=_infer_layer(assertion),  # type: ignore[arg-type]
        rule_family=assertion.rule_family,
        school_scope=school_scope,
        claim_concepts=tuple(assertion.acceptable_values),
        polarity="positive" if assertion.assertion_kind == "positive" else "boundary",
        conditions=tuple(assertion.limitations),
        required_evidence_ids=tuple(assertion.required_evidence_ids),
        acceptable_alternatives=(),
        explicit_contradictions=(),
        abstention_policy="requires_expert_relabel_before_scoring",
        minimum_input_requirements=("real-use-request-v1",),
        confidence_band="low",
        safety_critical=False,
        complexity_tier="simple",
        scenario_tags=(f"migrated_from_v1:{assertion.assertion_kind}",),
        benchmark_split="development",
        label_status="insufficient_input",
    )
    return MigrationDecisionV2(
        source_assertion_id=assertion.assertion_id,
        v2_assertion=v2,
        requires_expert_relabel=True,
        rule_change_allowed=False,
        initial_error_matrix_claim="not generated by migration",
    )
```

- [ ] **Step 4: Run migration tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_migration_protocol.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 5: Run focused regression**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_models.py tests/unit/test_domain_calibration_v2_protocol_models.py tests/unit/test_domain_calibration_v2_migration_protocol.py -q -p no:cacheprovider
```

Expected: PASS; V1 model tests remain unchanged and migration tests prove no rule changes are allowed by migration.

- [ ] **Step 6: Commit**

```powershell
git add src/mingli_engine/domain_calibration_v2_migration.py tests/unit/test_domain_calibration_v2_migration_protocol.py
git commit -m "feat: add calibration v2 migration protocol"
```

Expected: commit created with only migration protocol files staged.

## Task 7: Verify V2 Protocol Package Loading, Type Checks, Lint, And Diff Hygiene

**Files:**
- Create: `tests/integration/test_domain_calibration_v2_protocol_package.py`
- Modify: `src/mingli_engine/domain_calibration_v2.py`

- [ ] **Step 1: Write failing package-resource test**

Create `tests/integration/test_domain_calibration_v2_protocol_package.py`:

```python
from __future__ import annotations

from importlib import resources

from mingli_engine.domain_calibration_v2 import load_packaged_v2_resource_bytes


def test_v2_protocol_loader_reads_package_resource_without_checkout_path() -> None:
    payload = load_packaged_v2_resource_bytes("data/domain_calibration/v2/executable_fixtures.json")
    assert payload.startswith(b"{")
    assert resources.files("mingli_engine").joinpath(
        "data/domain_calibration/v2/executable_fixtures.json"
    ).is_file()
```

- [ ] **Step 2: Run the package-resource test to verify it fails**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/integration/test_domain_calibration_v2_protocol_package.py -q -p no:cacheprovider
```

Expected: FAIL with `ImportError` for `load_packaged_v2_resource_bytes`.

- [ ] **Step 3: Add package-resource reader**

Add to `src/mingli_engine/domain_calibration_v2.py`:

```python
def load_packaged_v2_resource_bytes(resource_path: str) -> bytes:
    if not resource_path.startswith("data/domain_calibration/v2/"):
        raise CalibrationProtocolErrorV2("resource path must be inside V2 calibration data")
    return resources.files("mingli_engine").joinpath(resource_path).read_bytes()
```

- [ ] **Step 4: Run package-resource test**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/integration/test_domain_calibration_v2_protocol_package.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 5: Run all protocol tests**

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_prerequisites.py tests/unit/test_domain_calibration_v2_models.py tests/unit/test_domain_calibration_v2_fixture_models.py tests/unit/test_domain_calibration_v2_protocol_models.py tests/unit/test_domain_calibration_v2_loader.py tests/unit/test_domain_calibration_v2_split_governance.py tests/unit/test_domain_calibration_v2_migration_protocol.py tests/integration/test_domain_calibration_v2_fixtures.py tests/integration/test_domain_calibration_v2_protocol_package.py -q -p no:cacheprovider
```

Expected after Feature 019 closure: PASS for all listed tests.

- [ ] **Step 6: Run type, lint, and diff hygiene checks**

```powershell
uv run --with mypy==1.17.1 python -m mypy src/mingli_engine/domain_calibration_v2.py src/mingli_engine/domain_calibration_v2_models.py src/mingli_engine/domain_calibration_v2_migration.py src/mingli_engine/domain_calibration_v2_prerequisites.py --follow-imports=skip
uv run --with ruff==0.12.11 ruff check src/mingli_engine/domain_calibration_v2.py src/mingli_engine/domain_calibration_v2_models.py src/mingli_engine/domain_calibration_v2_migration.py src/mingli_engine/domain_calibration_v2_prerequisites.py tests/unit/test_domain_calibration_v2_prerequisites.py tests/unit/test_domain_calibration_v2_protocol_models.py tests/unit/test_domain_calibration_v2_loader.py tests/unit/test_domain_calibration_v2_split_governance.py tests/unit/test_domain_calibration_v2_migration_protocol.py tests/integration/test_domain_calibration_v2_protocol_package.py
git diff --check
```

Expected: mypy reports no issues in the listed modules, Ruff reports no findings for the listed files, and `git diff --check` reports no whitespace errors.

- [ ] **Step 7: Commit**

```powershell
git add src/mingli_engine/domain_calibration_v2.py tests/integration/test_domain_calibration_v2_protocol_package.py
git commit -m "test: verify packaged calibration v2 protocol resources"
```

Expected: commit created with package-resource verification only.

## Protocol Completion Gate

Run the final protocol gate:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --with pytest==8.4.1 python -m pytest tests/unit/test_domain_calibration_v2_prerequisites.py tests/unit/test_domain_calibration_v2_models.py tests/unit/test_domain_calibration_v2_fixture_models.py tests/unit/test_domain_calibration_v2_protocol_models.py tests/unit/test_domain_calibration_v2_loader.py tests/unit/test_domain_calibration_v2_split_governance.py tests/unit/test_domain_calibration_v2_migration_protocol.py tests/integration/test_domain_calibration_v2_fixtures.py tests/integration/test_domain_calibration_v2_protocol_package.py -q -p no:cacheprovider
uv run --with mypy==1.17.1 python -m mypy src/mingli_engine/domain_calibration_v2.py src/mingli_engine/domain_calibration_v2_models.py src/mingli_engine/domain_calibration_v2_migration.py src/mingli_engine/domain_calibration_v2_prerequisites.py --follow-imports=skip
uv run --with ruff==0.12.11 ruff check src/mingli_engine/domain_calibration_v2.py src/mingli_engine/domain_calibration_v2_models.py src/mingli_engine/domain_calibration_v2_migration.py src/mingli_engine/domain_calibration_v2_prerequisites.py tests/unit/test_domain_calibration_v2_prerequisites.py tests/unit/test_domain_calibration_v2_protocol_models.py tests/unit/test_domain_calibration_v2_loader.py tests/unit/test_domain_calibration_v2_split_governance.py tests/unit/test_domain_calibration_v2_migration_protocol.py tests/integration/test_domain_calibration_v2_protocol_package.py
git diff --check
```

Expected after Feature 019 closure: all pytest targets pass, mypy reports no issues for listed modules, Ruff reports no findings for listed files, and diff hygiene passes.

## Handoff To Next Child Plan

Create the existing-baseline relabeling plan only after the protocol completion gate is green. That next plan must migrate the existing 43 assertions, add layer-aware labels, preserve acceptable alternatives and school-dependent states, and generate an initial Error Matrix from unchanged engine output. It must not prescribe rule corrections until the real Error Matrix exists.

