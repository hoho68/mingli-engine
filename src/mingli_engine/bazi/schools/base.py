from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Protocol, cast, runtime_checkable

from mingli_engine.bazi.constants import ELEMENTS
from mingli_engine.bazi.patterns import calculate_pattern_candidates
from mingli_engine.bazi.result_models import (
    ChartFacts,
    ComputationStatus,
    PatternCandidateResult,
    ReasonedResult,
    SchoolInterpretation,
    StrengthResult,
    UsefulGodCandidateResult,
)
from mingli_engine.bazi.useful_gods import calculate_useful_god_candidates


PROFILE_VERSION = "school-profiles-v1"
_PROFILE_IDS = frozenset({"ziping", "liang_xiangrun", "duan"})
_METHODS = frozenset(
    {
        "support_control",
        "seasonal_adjustment",
        "mediation",
        "illness_remedy",
        "pattern_context",
        "structural_flow",
    }
)
_PROFILE_METHODS: Mapping[str, frozenset[str]] = MappingProxyType(
    {
        "ziping": frozenset(
            {
                "support_control",
                "seasonal_adjustment",
                "mediation",
                "illness_remedy",
            }
        ),
        "liang_xiangrun": frozenset(
            {"pattern_context", "seasonal_adjustment", "support_control"}
        ),
        "duan": frozenset({"structural_flow", "support_control", "pattern_context"}),
    }
)
_ACTIVE_STATUSES = frozenset({"computed", "indeterminate", "disputed"})
_STATUS_PRECEDENCE = {"computed": 0, "indeterminate": 1, "disputed": 2}
_DEFAULT_PROFILE_PATH = (
    Path(__file__).parents[2] / "data" / "calculation" / "school_profiles.json"
)


@dataclass(frozen=True)
class SchoolProfile:
    school_id: str
    priority: int
    method_order: tuple[str, ...]


@dataclass(frozen=True)
class SchoolProfilesConfig:
    version: str
    enabled: tuple[str, ...]
    profiles: Mapping[str, SchoolProfile]


@dataclass(frozen=True)
class _ValidatedSchoolInputs:
    facts: ChartFacts
    strength: StrengthResult
    patterns: tuple[PatternCandidateResult, ...]
    useful_gods: tuple[UsefulGodCandidateResult, ...]


@runtime_checkable
class SchoolAdapter(Protocol):
    school_id: str
    profile_version: str

    def interpret(
        self,
        *,
        facts: ChartFacts,
        strength: StrengthResult,
        patterns: tuple[PatternCandidateResult, ...],
        useful_gods: tuple[UsefulGodCandidateResult, ...],
    ) -> SchoolInterpretation: ...


class SchoolAdapterBase:
    school_id: str

    def __init__(self, profile: SchoolProfile, profile_version: str) -> None:
        if profile.school_id != self.school_id:
            raise ValueError(
                f"profile {profile.school_id!r} cannot configure {self.school_id!r}"
            )
        if profile_version != PROFILE_VERSION:
            raise ValueError(f"unsupported school profile version: {profile_version!r}")
        self.profile = profile
        self.profile_version = profile_version

    def interpret(
        self,
        *,
        facts: ChartFacts,
        strength: StrengthResult,
        patterns: tuple[PatternCandidateResult, ...],
        useful_gods: tuple[UsefulGodCandidateResult, ...],
    ) -> SchoolInterpretation:
        inputs = _validate_school_inputs(
            facts=facts,
            strength=strength,
            patterns=patterns,
            useful_gods=useful_gods,
        )
        return self._interpret_validated(inputs)

    def _interpret_validated(
        self, inputs: _ValidatedSchoolInputs
    ) -> SchoolInterpretation:
        raise NotImplementedError


def _require_exact_keys(
    value: object, expected: frozenset[str], context: str
) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"school profiles {context} must be an object")
    if frozenset(value) != expected:
        raise ValueError(
            f"school profiles {context} keys must be exactly {sorted(expected)!r}"
        )
    return value


def _string_list(value: object, context: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"school profiles {context} must be a nonempty list")
    if not all(
        isinstance(item, str) and item and item == item.strip() for item in value
    ):
        raise ValueError(f"school profiles {context} must contain nonempty strings")
    result = tuple(value)
    if len(set(result)) != len(result):
        raise ValueError(f"school profiles {context} values must be unique")
    return result


def load_school_profiles_config(
    path: str | Path | None = None,
) -> SchoolProfilesConfig:
    source = Path(path) if path is not None else _DEFAULT_PROFILE_PATH
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(
            f"unable to read school profiles from {source}: {exc}"
        ) from exc
    try:
        raw: object = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"unable to parse school profiles JSON at {source}: {exc}"
        ) from exc

    root = _require_exact_keys(
        raw, frozenset({"version", "enabled", "profiles"}), "top-level"
    )
    version = root["version"]
    if version != PROFILE_VERSION:
        raise ValueError(
            f"unsupported school profiles version: {version!r}; "
            f"expected {PROFILE_VERSION!r}"
        )
    enabled = _string_list(root["enabled"], "enabled")
    if not set(enabled) <= _PROFILE_IDS:
        raise ValueError("school profiles enabled must contain only known ids")

    raw_profiles = _require_exact_keys(root["profiles"], _PROFILE_IDS, "profile ids")
    parsed: dict[str, SchoolProfile] = {}
    priorities: set[int] = set()
    for school_id in sorted(_PROFILE_IDS):
        raw_profile = _require_exact_keys(
            raw_profiles[school_id],
            frozenset({"priority", "method_order"}),
            f"{school_id} profile",
        )
        priority = raw_profile["priority"]
        if isinstance(priority, bool) or not isinstance(priority, int) or priority <= 0:
            raise ValueError(
                f"school profiles {school_id} priority must be a positive integer"
            )
        if priority in priorities:
            raise ValueError("school profile priorities must be unique")
        priorities.add(priority)
        method_order = _string_list(
            raw_profile["method_order"], f"{school_id} method_order"
        )
        unknown = set(method_order) - _METHODS
        if unknown:
            raise ValueError(
                f"school profiles method vocabulary contains unknown method: "
                f"{sorted(unknown)!r}"
            )
        unsupported = set(method_order) - _PROFILE_METHODS[school_id]
        if unsupported:
            raise ValueError(
                f"school profiles {school_id} method_order contains unsupported "
                f"methods: {sorted(unsupported)!r}"
            )
        parsed[school_id] = SchoolProfile(school_id, priority, method_order)
    return SchoolProfilesConfig(
        version=version,
        enabled=enabled,
        profiles=MappingProxyType(parsed.copy()),
    )


def _validate_reasoning(reasoning: ReasonedResult, context: str) -> None:
    if reasoning.status not in {
        "not_computed",
        "computed",
        "indeterminate",
        "disputed",
    }:
        raise ValueError(f"invalid {context} status: {reasoning.status!r}")
    if reasoning.confidence not in {"high", "medium", "low"}:
        raise ValueError(f"invalid {context} confidence: {reasoning.confidence!r}")


def _validate_school_inputs(
    *,
    facts: ChartFacts,
    strength: StrengthResult,
    patterns: tuple[PatternCandidateResult, ...],
    useful_gods: tuple[UsefulGodCandidateResult, ...],
) -> _ValidatedSchoolInputs:
    if not isinstance(patterns, tuple) or not isinstance(useful_gods, tuple):
        raise ValueError("school adapter pattern and useful-god inputs must be tuples")
    _validate_reasoning(strength.reasoning, "strength")

    pattern_ids = tuple(item.pattern_id for item in patterns)
    pattern_ranks = tuple(item.rank for item in patterns)
    if len(set(pattern_ids)) != len(pattern_ids):
        raise ValueError("duplicate pattern ids are not allowed")
    if len(set(pattern_ranks)) != len(pattern_ranks):
        raise ValueError("duplicate pattern ranks are not allowed")
    if pattern_ranks != tuple(range(1, len(patterns) + 1)):
        raise ValueError("pattern ranks must be contiguous")
    for item in patterns:
        _validate_reasoning(item.reasoning, f"pattern {item.pattern_id}")

    canonical_patterns = calculate_pattern_candidates(facts, strength)
    canonical_ids = tuple(item.pattern_id for item in canonical_patterns)
    if pattern_ids != canonical_ids:
        raise ValueError(
            "supplied patterns must match canonical pattern identities: "
            f"expected={canonical_ids!r}; supplied={pattern_ids!r}"
        )
    canonical_by_id = {item.pattern_id: item for item in canonical_patterns}
    for item in patterns:
        expected = canonical_by_id[item.pattern_id]
        for field_name in (
            "name",
            "rank",
            "formation_conditions",
            "damage_conditions",
            "rescue_conditions",
        ):
            if getattr(item, field_name) != getattr(expected, field_name):
                raise ValueError(
                    f"canonical pattern mismatch for {item.pattern_id}: "
                    f"{field_name} differs"
                )

    useful_keys = tuple((item.method, item.element) for item in useful_gods)
    useful_ranks = tuple(item.rank for item in useful_gods)
    if len(set(useful_keys)) != len(useful_keys):
        raise ValueError("duplicate useful-god keys are not allowed")
    if len(set(useful_ranks)) != len(useful_ranks):
        raise ValueError("duplicate useful-god ranks are not allowed")
    if useful_ranks != tuple(range(1, len(useful_gods) + 1)):
        raise ValueError("useful-god ranks must be contiguous")
    for useful_item in useful_gods:
        if useful_item.element and useful_item.element not in ELEMENTS:
            raise ValueError(f"invalid useful-god element: {useful_item.element!r}")
        _validate_reasoning(useful_item.reasoning, f"useful-god {useful_item.method}")

    canonical_useful = calculate_useful_god_candidates(facts, strength, patterns)
    if useful_gods != canonical_useful:
        raise ValueError("supplied useful gods must match canonical useful-god results")
    return _ValidatedSchoolInputs(facts, strength, patterns, useful_gods)


def conservative_status(
    reasonings: tuple[ReasonedResult, ...],
) -> ComputationStatus:
    active = tuple(
        item.status for item in reasonings if item.status in _ACTIVE_STATUSES
    )
    if not active:
        return "not_computed"
    return cast(ComputationStatus, max(active, key=_STATUS_PRECEDENCE.__getitem__))


def distinct(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def not_computed_interpretation(
    *,
    school_id: str,
    profile_version: str,
    conclusion: str,
    missing_inputs: tuple[str, ...],
    rule_id: str,
    assumptions: tuple[str, ...] = (),
) -> SchoolInterpretation:
    return SchoolInterpretation(
        school_id=school_id,
        profile_version=profile_version,
        reasoning=ReasonedResult(
            status="not_computed",
            conclusion=conclusion,
            confidence="low",
            assumptions=assumptions,
            missing_inputs=missing_inputs,
            rule_ids=(rule_id,),
        ),
        preferred_pattern_ids=(),
        preferred_useful_god_elements=(),
    )


def load_enabled_school_adapters(
    path: str | Path | None = None,
) -> tuple[SchoolAdapter, ...]:
    from mingli_engine.bazi.schools.duan import DuanSchoolAdapter
    from mingli_engine.bazi.schools.liang_xiangrun import (
        LiangXiangrunSchoolAdapter,
    )
    from mingli_engine.bazi.schools.ziping import ZipingSchoolAdapter

    config = load_school_profiles_config(path)
    registry = {
        "ziping": ZipingSchoolAdapter,
        "liang_xiangrun": LiangXiangrunSchoolAdapter,
        "duan": DuanSchoolAdapter,
    }
    enabled_profiles = sorted(
        (config.profiles[school_id] for school_id in config.enabled),
        key=lambda item: (-item.priority, item.school_id),
    )
    return tuple(
        registry[profile.school_id](profile, config.version)
        for profile in enabled_profiles
    )


def _adapter_failure(adapter: SchoolAdapter, exc: Exception) -> SchoolInterpretation:
    return not_computed_interpretation(
        school_id=adapter.school_id,
        profile_version=adapter.profile_version,
        conclusion="school adapter failed in isolation",
        missing_inputs=(f"adapter_error:{type(exc).__name__}",),
        rule_id="school.adapter.isolated_failure",
    )


def _mark_disagreements(
    results: tuple[SchoolInterpretation, ...],
    field_name: str,
    label: str,
) -> tuple[SchoolInterpretation, ...]:
    involved = tuple(
        (index, item, getattr(item, field_name))
        for index, item in enumerate(results)
        if item.reasoning.status in _ACTIVE_STATUSES and getattr(item, field_name)
    )
    if len({frozenset(values) for _, _, values in involved}) < 2:
        return results
    occurrence = ";".join(
        f"{index}:{item.school_id}={','.join(values)}"
        for index, item, values in involved
    )
    signal = f"cross_school_disagreement:{label}:{occurrence}"
    rule_id = f"school.cross_school_disagreement.{label}"
    involved_indexes = {index for index, _, _ in involved}
    return tuple(
        replace(
            item,
            reasoning=replace(
                item.reasoning,
                status="disputed",
                opposing_signals=distinct((*item.reasoning.opposing_signals, signal)),
                rule_ids=distinct((*item.reasoning.rule_ids, rule_id)),
            ),
        )
        if index in involved_indexes and item.reasoning.status != "not_computed"
        else item
        for index, item in enumerate(results)
    )


def interpret_with_enabled_schools(
    *,
    facts: ChartFacts,
    strength: StrengthResult,
    patterns: tuple[PatternCandidateResult, ...],
    useful_gods: tuple[UsefulGodCandidateResult, ...],
    adapters: tuple[SchoolAdapter, ...] | None = None,
    path: str | Path | None = None,
) -> tuple[SchoolInterpretation, ...]:
    inputs = _validate_school_inputs(
        facts=facts,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
    )
    selected_adapters = (
        adapters if adapters is not None else load_enabled_school_adapters(path)
    )
    results: list[SchoolInterpretation] = []
    for adapter in selected_adapters:
        try:
            result = (
                adapter._interpret_validated(inputs)
                if isinstance(adapter, SchoolAdapterBase)
                else adapter.interpret(
                    facts=facts,
                    strength=strength,
                    patterns=patterns,
                    useful_gods=useful_gods,
                )
            )
            if result.school_id != adapter.school_id:
                raise ValueError("adapter result school id mismatch")
            results.append(result)
        except Exception as exc:
            results.append(_adapter_failure(adapter, exc))
    marked = _mark_disagreements(
        tuple(results), "preferred_pattern_ids", "pattern_preferences"
    )
    return _mark_disagreements(
        marked, "preferred_useful_god_elements", "useful_god_preferences"
    )
