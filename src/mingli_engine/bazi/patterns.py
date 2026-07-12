from types import MappingProxyType
from typing import Final, Literal, Mapping

from mingli_engine.bazi.constants import BRANCHES
from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    ChartFacts,
    HiddenStemFact,
    PatternCandidateResult,
    ReasonedResult,
    StemFact,
    StrengthResult,
)


TEN_GOD_PATTERN_NAMES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "正官": "正官格",
        "七杀": "七杀格",
        "正财": "正财格",
        "偏财": "偏财格",
        "正印": "正印格",
        "偏印": "偏印格",
        "食神": "食神格",
        "伤官": "伤官格",
    }
)
PATTERN_DAMAGE: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        "正官格": ("伤官",),
        "七杀格": (),
        "正财格": ("比肩", "劫财"),
        "偏财格": ("比肩", "劫财"),
        "正印格": ("正财", "偏财"),
        "偏印格": ("正财", "偏财"),
        "食神格": ("偏印",),
        "伤官格": ("正官",),
    }
)
PATTERN_RESCUE: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        "正官格": ("正印", "偏印"),
        "七杀格": ("食神", "正印", "偏印"),
        "正财格": ("正官", "七杀", "食神", "伤官"),
        "偏财格": ("正官", "七杀", "食神", "伤官"),
        "正印格": ("比肩", "劫财", "正官", "七杀"),
        "偏印格": ("比肩", "劫财", "正官", "七杀"),
        "食神格": ("正财", "偏财"),
        "伤官格": ("正财", "偏财", "正印", "偏印"),
    }
)


_PATTERN_IDS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "正官": "standard.zhengguan",
        "七杀": "standard.qisha",
        "正财": "standard.zhengcai",
        "偏财": "standard.piancai",
        "正印": "standard.zhengyin",
        "偏印": "standard.pianyin",
        "食神": "standard.shishen",
        "伤官": "standard.shangguan",
        "比肩": "special.jianlu",
        "劫财": "special.yuejie",
    }
)
_SPECIAL_NAMES: Final[Mapping[str, str]] = MappingProxyType(
    {"比肩": "建禄格候选", "劫财": "月劫格候选"}
)
_ROLE_ORDER: Final[Mapping[str, int]] = MappingProxyType(
    {"main": 0, "middle": 1, "residual": 2}
)
_KNOWN_TEN_GODS: Final[frozenset[str]] = frozenset(
    {*TEN_GOD_PATTERN_NAMES, "比肩", "劫财"}
)


def _hidden_provenance(item: HiddenStemFact) -> str:
    return (
        f"hidden:{item.pillar_name}:{item.branch}:{item.role}:"
        f"{item.stem}:{item.ten_god}"
    )


def _exposed_provenance(item: StemFact) -> str:
    return f"exposed:{item.pillar_name}:{item.stem}:{item.ten_god}"


def _distinct(items: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def _signal_index(
    facts: ChartFacts,
) -> tuple[
    Mapping[str, tuple[str, ...]], Mapping[str, tuple[str, ...]]
]:
    exposed_signals: dict[str, list[str]] = {}
    hidden_signals: dict[str, list[str]] = {}
    for item in facts.exposed_stems:
        if item.pillar_name != "day":
            exposed_signals.setdefault(item.ten_god, []).append(
                _exposed_provenance(item)
            )
    for item in facts.hidden_stems:
        hidden_signals.setdefault(item.ten_god, []).append(
            _hidden_provenance(item)
        )

    def freeze(
        values: dict[str, list[str]],
    ) -> Mapping[str, tuple[str, ...]]:
        return MappingProxyType(
            {
                ten_god: _distinct(tuple(provenance))
                for ten_god, provenance in values.items()
            }
        )

    return freeze(exposed_signals), freeze(hidden_signals)


def _conditions_for(
    ten_gods: tuple[str, ...], signals: Mapping[str, tuple[str, ...]]
) -> tuple[str, ...]:
    return tuple(
        provenance
        for ten_god in ten_gods
        for provenance in signals.get(ten_god, ())
    )


def _relation_trace(
    relations: tuple[BranchRelationResult, ...],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], bool]:
    assumptions: list[str] = []
    opposing: list[str] = []
    rule_ids: list[str] = []
    has_transformation = False
    for relation in relations:
        if not relation.blockers and not relation.transformed_element:
            continue
        occurrence = (
            f"{relation.rule_id}|pillars={','.join(relation.pillar_names)}"
            f"|branches={','.join(relation.branches)}"
        )
        assumptions.append(
            f"relation:{occurrence}:state={relation.state}:"
            f"transformed_element={relation.transformed_element}; "
            "V1 pattern effect not implemented"
        )
        opposing.extend(
            f"relation:{occurrence}:blocker={blocker}"
            for blocker in relation.blockers
        )
        if relation.transformed_element:
            has_transformation = True
            opposing.append(
                f"relation:{occurrence}:transformed_element="
                f"{relation.transformed_element}"
            )
            rule_ids.append(
                "pattern.relation.transformed_modifier_unimplemented:"
                f"{occurrence}"
            )
        else:
            rule_ids.append(f"pattern.relation.trace:{occurrence}")
    return (
        tuple(assumptions),
        tuple(opposing),
        tuple(rule_ids),
        has_transformation,
    )


def _upstream_status(
    strength: StrengthResult,
    default_status: Literal["computed", "indeterminate", "disputed"],
    default_confidence: Literal["high", "medium", "low"],
    has_transformation: bool,
) -> tuple[str, str, tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    status = strength.reasoning.status
    if status == "computed" and not has_transformation:
        return default_status, default_confidence, (), (), ()
    if status in {"disputed", "not_computed"}:
        result_status = status
    else:
        result_status = "indeterminate"
    prerequisite = (
        (f"prerequisite:strength:{status}",)
        if status != "computed"
        else ()
    )
    return (
        result_status,
        "low",
        prerequisite,
        (
            ("strength_result_computed",)
            if status in {"indeterminate", "not_computed"}
            else ()
        ),
        (
            (f"pattern.prerequisite.strength.{status}",)
            if status != "computed"
            else ()
        ),
    )


def _standard_candidate(
    *,
    ten_god: str,
    role: str,
    month_hidden: HiddenStemFact,
    rank: int,
    facts: ChartFacts,
    strength: StrengthResult,
    signals: Mapping[str, tuple[str, ...]],
    hidden_signals: Mapping[str, tuple[str, ...]],
    relation_assumptions: tuple[str, ...],
    relation_opposition: tuple[str, ...],
    relation_rule_ids: tuple[str, ...],
    has_transformation: bool,
) -> PatternCandidateResult:
    name = TEN_GOD_PATTERN_NAMES.get(ten_god, _SPECIAL_NAMES.get(ten_god))
    if name is None:
        raise ValueError(f"unknown month ten god: {ten_god!r}")

    exposed_formation = signals.get(ten_god, ())
    formation_conditions = (
        _hidden_provenance(month_hidden),
        *(exposed_formation or (f"exposure:none:{ten_god}",)),
    )
    damage = _conditions_for(PATTERN_DAMAGE.get(name, ()), signals)
    rescue = _conditions_for(PATTERN_RESCUE.get(name, ()), signals)

    if damage:
        default_status: Literal["computed", "disputed"] = "disputed"
        default_confidence: Literal["high", "medium", "low"] = (
            "medium" if rescue else "low"
        )
    else:
        default_status = "computed"
        default_confidence = (
            "high" if role == "main" and exposed_formation else "medium"
        )
    status, confidence, prerequisite, missing, prerequisite_rules = _upstream_status(
        strength, default_status, default_confidence, has_transformation
    )

    latent_assumption = (
        (f"formation:latent:{ten_god}",) if not exposed_formation else ()
    )
    candidate_only = (
        ("candidate_only:not_final_pattern",) if ten_god in _SPECIAL_NAMES else ()
    )
    latent_damage_context = tuple(
        f"latent_damage_context:{item}"
        for item in _conditions_for(PATTERN_DAMAGE.get(name, ()), hidden_signals)
    )
    latent_rescue_context = tuple(
        f"latent_rescue_context:{item}"
        for item in _conditions_for(PATTERN_RESCUE.get(name, ()), hidden_signals)
    )
    relation_missing = (
        ("transformed_relation_pattern_modifier",)
        if has_transformation
        else ()
    )
    supporting = (
        *exposed_formation,
        *rescue,
    )
    rule_ids = (
        f"pattern.formation.month_{role}.{_PATTERN_IDS[ten_god]}",
        *(f"pattern.damage.{name}.{item.rsplit(':', 1)[-1]}" for item in damage),
        *(f"pattern.rescue.{name}.{item.rsplit(':', 1)[-1]}" for item in rescue),
        *prerequisite_rules,
        *relation_rule_ids,
    )
    return PatternCandidateResult(
        pattern_id=_PATTERN_IDS[ten_god],
        name=name,
        rank=rank,
        reasoning=ReasonedResult(
            status=status,
            conclusion=(
                f"{name}: damaged with rescue evidence"
                if damage and rescue
                else f"{name}: damaged"
                if damage
                else f"{name}: candidate"
            ),
            confidence=confidence,
            supporting_signals=_distinct(supporting),
            opposing_signals=_distinct((*damage, *relation_opposition)),
            assumptions=(
                *facts.assumptions,
                *latent_assumption,
                *candidate_only,
                *latent_damage_context,
                *latent_rescue_context,
                *prerequisite,
                *relation_assumptions,
            ),
            missing_inputs=_distinct((*missing, *relation_missing)),
            rule_ids=_distinct(rule_ids),
        ),
        formation_conditions=formation_conditions,
        damage_conditions=damage,
        rescue_conditions=rescue,
    )


def _follow_candidate(
    *,
    label: str,
    rank: int,
    facts: ChartFacts,
    strength: StrengthResult,
    relation_assumptions: tuple[str, ...],
    relation_opposition: tuple[str, ...],
    relation_rule_ids: tuple[str, ...],
    has_transformation: bool,
) -> PatternCandidateResult:
    is_strong = label == "强"
    pattern_id = "follow.congqiang" if is_strong else "follow.congruo"
    name = "从强候选" if is_strong else "从弱候选"
    direction = "strong" if is_strong else "weak"
    status, confidence, prerequisite, missing, prerequisite_rules = _upstream_status(
        strength, "indeterminate", "low", has_transformation
    )
    relation_missing = (
        ("transformed_relation_pattern_modifier",)
        if has_transformation
        else ()
    )
    return PatternCandidateResult(
        pattern_id=pattern_id,
        name=name,
        rank=rank,
        reasoning=ReasonedResult(
            status=status,
            conclusion=f"{name}: guarded V1 candidate",
            confidence=confidence,
            supporting_signals=(f"strength:label:{label}",),
            opposing_signals=(
                f"countercondition:{direction}:independent_opposition:not_evaluated",
                *relation_opposition,
            ),
            assumptions=(
                *facts.assumptions,
                "follow:v1_never_auto_confirm",
                *prerequisite,
                *relation_assumptions,
            ),
            missing_inputs=_distinct(
                (
                    f"follow_{direction}_necessary_conditions_verified",
                    f"follow_{direction}_counterconditions_excluded",
                    *missing,
                    *relation_missing,
                )
            ),
            rule_ids=(
                f"pattern.follow.{direction}.guarded_v1",
                *prerequisite_rules,
                *relation_rule_ids,
            ),
        ),
        formation_conditions=(
            f"necessary:strength_label:{label}",
            f"necessary:{direction}:exclusive_structure:unverified",
        ),
        damage_conditions=(
            f"countercondition:{direction}:independent_opposition:not_evaluated",
        ),
        rescue_conditions=(),
    )


def calculate_pattern_candidates(
    facts: ChartFacts,
    strength: StrengthResult,
    relations: tuple[BranchRelationResult, ...] = (),
) -> tuple[PatternCandidateResult, ...]:
    if facts.month_branch not in BRANCHES:
        raise ValueError(f"invalid month branch: {facts.month_branch!r}")
    month_hidden = tuple(
        item
        for item in facts.hidden_stems
        if item.pillar_name == "month"
    )
    month_main = tuple(item for item in month_hidden if item.role == "main")
    if len(month_main) != 1:
        raise ValueError("expected exactly one month main hidden stem")
    for item in month_hidden:
        if item.branch != facts.month_branch:
            raise ValueError(
                "month hidden stem branch must match month_branch: "
                f"{item.branch!r} != {facts.month_branch!r}"
            )
        if item.role not in _ROLE_ORDER:
            raise ValueError(f"unknown month hidden stem role: {item.role!r}")
        if item.ten_god not in _KNOWN_TEN_GODS:
            qualifier = "main " if item.role == "main" else ""
            raise ValueError(f"unknown month {qualifier}ten god: {item.ten_god!r}")

    signals, hidden_signals = _signal_index(facts)
    (
        relation_assumptions,
        relation_opposition,
        relation_rule_ids,
        has_transformation,
    ) = _relation_trace(relations)
    eligible = [month_main[0]]
    eligible.extend(
        item
        for item in sorted(month_hidden, key=lambda value: _ROLE_ORDER[value.role])
        if item.role != "main"
        and item.ten_god in TEN_GOD_PATTERN_NAMES
        and any(
            provenance.startswith("exposed:")
            for provenance in signals.get(item.ten_god, ())
        )
    )

    results: list[PatternCandidateResult] = []
    seen_pattern_ids: set[str] = set()
    for item in eligible:
        pattern_id = _PATTERN_IDS[item.ten_god]
        if pattern_id in seen_pattern_ids:
            continue
        seen_pattern_ids.add(pattern_id)
        results.append(
            _standard_candidate(
                ten_god=item.ten_god,
                role=item.role,
                month_hidden=item,
                rank=len(results) + 1,
                facts=facts,
                strength=strength,
                signals=signals,
                hidden_signals=hidden_signals,
                relation_assumptions=relation_assumptions,
                relation_opposition=relation_opposition,
                relation_rule_ids=relation_rule_ids,
                has_transformation=has_transformation,
            )
        )

    if strength.label in {"强", "弱"}:
        results.append(
            _follow_candidate(
                label=strength.label,
                rank=len(results) + 1,
                facts=facts,
                strength=strength,
                relation_assumptions=relation_assumptions,
                relation_opposition=relation_opposition,
                relation_rule_ids=relation_rule_ids,
                has_transformation=has_transformation,
            )
        )
    return tuple(results)
