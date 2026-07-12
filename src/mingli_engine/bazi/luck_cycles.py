from collections import Counter
from datetime import datetime

from lunar_python import Solar  # type: ignore[import-untyped]

from mingli_engine.bazi.branch_relations import (
    detect_branch_relations_for_positions,
)
from mingli_engine.bazi.constants import BRANCHES, STEMS
from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    LuckCycleResult,
    LuckPillar,
    ReasonedResult,
)
from mingli_engine.calendar_provider import (
    calculate_provider_luck_cycles,
    calculate_provider_pillars,
)
from mingli_engine.models import BaziChart, Pillar


_EXPECTED_ROLES = Counter({"year": 1, "month": 1, "day": 1, "hour": 1})
_GENDER_ALIASES = {"male": "male", "男": "male", "female": "female", "女": "female"}
_MAX_COUNT = 100


def _validate_options(sect: int, count: int, selected_year: int | None) -> None:
    if isinstance(sect, bool) or not isinstance(sect, int) or sect not in {1, 2}:
        raise ValueError("sect must be 1 or 2")
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or not 1 <= count <= _MAX_COUNT
    ):
        raise ValueError("count must be an integer between 1 and 100")
    if selected_year is not None and (
        isinstance(selected_year, bool)
        or not isinstance(selected_year, int)
        or not 1 <= selected_year <= 9999
    ):
        raise ValueError("selected_year must be an integer between 1 and 9999")


def _validated_chart_pillars(chart: BaziChart) -> tuple[Pillar, ...]:
    if len(chart.pillars) != 4:
        raise ValueError("expected exactly four pillars")
    if Counter(pillar.name for pillar in chart.pillars) != _EXPECTED_ROLES:
        raise ValueError("expected exactly one year, month, day, and hour pillar")
    for pillar in chart.pillars:
        if pillar.heavenly_stem not in STEMS:
            raise ValueError(f"Invalid stem: {pillar.heavenly_stem!r}")
        if pillar.earthly_branch not in BRANCHES:
            raise ValueError(f"Invalid branch: {pillar.earthly_branch!r}")
    return tuple(chart.pillars)


def _not_computed(missing_input: str) -> LuckCycleResult:
    return LuckCycleResult(
        reasoning=ReasonedResult(
            status="not_computed",
            conclusion="Luck cycles were not computed because a required input is unavailable.",
            confidence="low",
            missing_inputs=(missing_input,),
            rule_ids=("luck_cycle.input.requirements",),
        ),
        forward=False,
        start_years=0,
        start_months=0,
        start_days=0,
        start_solar="",
        pillars=(),
    )


def _normalize_gender(gender: object) -> str | None:
    if not isinstance(gender, str):
        return None
    return _GENDER_ALIASES.get(gender.strip().casefold())


def _require_matching_natal_pillars(
    chart_pillars: tuple[Pillar, ...], birth_datetime: datetime
) -> None:
    if not isinstance(birth_datetime, datetime):
        raise ValueError("birth_datetime must be a datetime")
    provider_pillars = calculate_provider_pillars(birth_datetime)
    chart_by_name = {pillar.name: pillar for pillar in chart_pillars}
    provider_by_name = {pillar.name: pillar for pillar in provider_pillars}
    if set(provider_by_name) != set(_EXPECTED_ROLES):
        raise ValueError("provider did not return canonical natal pillars")
    if any(
        (
            chart_by_name[name].heavenly_stem,
            chart_by_name[name].earthly_branch,
        )
        != (
            provider_by_name[name].heavenly_stem,
            provider_by_name[name].earthly_branch,
        )
        for name in _EXPECTED_ROLES
    ):
        raise ValueError("chart pillars do not match birth_datetime")


def _selected_year_gan_zhi(selected_year: int) -> str:
    try:
        gan_zhi = Solar.fromYmd(selected_year, 7, 1).getLunar().getYearInGanZhiExact()
    except Exception as exc:
        raise RuntimeError("selected-year provider calculation failed") from exc
    if (
        not isinstance(gan_zhi, str)
        or len(gan_zhi) != 2
        or gan_zhi[0] not in STEMS
        or gan_zhi[1] not in BRANCHES
    ):
        raise RuntimeError("selected-year provider returned invalid gan_zhi")
    return gan_zhi


def calculate_luck_cycles(
    chart: BaziChart,
    *,
    birth_datetime: datetime | None = None,
    selected_year: int | None = None,
    sect: int = 1,
    count: int = 8,
) -> LuckCycleResult:
    _validate_options(sect, count, selected_year)
    chart_pillars = _validated_chart_pillars(chart)
    if birth_datetime is None:
        return _not_computed("birth_datetime")

    _require_matching_natal_pillars(chart_pillars, birth_datetime)
    gender = _normalize_gender(chart.birth_profile.gender)
    if gender is None:
        return _not_computed("supported_gender")

    provider = calculate_provider_luck_cycles(
        birth_datetime,
        gender,
        sect=sect,
        count=count,
    )
    luck_pillars = tuple(
        LuckPillar(index, gan_zhi, start_year, end_year, start_age, end_age)
        for index, gan_zhi, start_year, end_year, start_age, end_age in provider.pillars
    )

    supporting_signals = [
        f"direction={'forward' if provider.forward else 'reverse'}",
        (
            "start_components="
            f"{provider.start_years}y/{provider.start_months}m/{provider.start_days}d"
        ),
        f"start_hours={provider.start_hours}",
        f"start_solar={provider.start_solar}",
    ]
    assumptions = [f"sect={sect}", f"count={count}"]
    rule_ids = [
        "luck_cycle.provider.lunar_python_1_4_8",
        "luck_cycle.direction",
        "luck_cycle.start",
    ]
    selected_year_relations: tuple[BranchRelationResult, ...] = ()

    if selected_year is not None:
        selected_gan_zhi = _selected_year_gan_zhi(selected_year)
        active = next(
            (
                pillar
                for pillar in luck_pillars
                if pillar.start_year <= selected_year <= pillar.end_year
            ),
            None,
        )
        positions = [(pillar.name, pillar.earthly_branch) for pillar in chart_pillars]
        if active is None:
            supporting_signals.append("no_active_luck_pillar")
        else:
            supporting_signals.append(f"active_luck_pillar={active.index}")
            positions.append((f"active_luck_{active.index}", active.gan_zhi[1]))
        selected_position = f"selected_year_{selected_year}"
        positions.append((selected_position, selected_gan_zhi[1]))
        relations = detect_branch_relations_for_positions(tuple(positions))
        selected_year_relations = tuple(
            relation
            for relation in relations
            if any(
                name.startswith("active_luck_") or name.startswith("selected_year_")
                for name in relation.pillar_names
            )
        )
        assumptions.append(f"selected_year_reference={selected_year}-07-01")
        rule_ids.extend(
            (
                "luck_cycle.selected_year.reference_july_1",
                "luck_cycle.selected_year.branch_relations",
            )
        )

    return LuckCycleResult(
        reasoning=ReasonedResult(
            status="computed",
            conclusion=(
                "Luck-cycle direction, start, pillars, and requested structural "
                "branch relations were calculated."
            ),
            confidence="high",
            supporting_signals=tuple(supporting_signals),
            assumptions=tuple(assumptions),
            rule_ids=tuple(rule_ids),
        ),
        forward=provider.forward,
        start_years=provider.start_years,
        start_months=provider.start_months,
        start_days=provider.start_days,
        start_solar=provider.start_solar,
        pillars=luck_pillars,
        selected_year_relations=selected_year_relations,
    )
