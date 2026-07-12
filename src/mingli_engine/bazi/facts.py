from mingli_engine.bazi.constants import (
    CONTROLS,
    GENERATES,
    HIDDEN_STEMS,
    STEM_ELEMENT,
    STEM_POLARITY,
    STEMS,
    growth_phase,
)
from mingli_engine.bazi.result_models import (
    ChartFacts,
    HiddenStemFact,
    RootFact,
    StemFact,
)
from mingli_engine.models import BaziChart, Pillar


def _validate_stem(stem: str) -> None:
    if stem not in STEMS:
        raise ValueError(f"Invalid stem: {stem!r}")


def ten_god(day_master: str, target_stem: str) -> str:
    _validate_stem(day_master)
    _validate_stem(target_stem)

    day_element = STEM_ELEMENT[day_master]
    target_element = STEM_ELEMENT[target_stem]
    same_polarity = STEM_POLARITY[day_master] == STEM_POLARITY[target_stem]

    if target_element == day_element:
        return "比肩" if same_polarity else "劫财"
    if GENERATES[target_element] == day_element:
        return "偏印" if same_polarity else "正印"
    if GENERATES[day_element] == target_element:
        return "食神" if same_polarity else "伤官"
    if CONTROLS[day_element] == target_element:
        return "偏财" if same_polarity else "正财"
    if CONTROLS[target_element] == day_element:
        return "七杀" if same_polarity else "正官"
    raise ValueError("unreachable five-element relation")


def _canonical_hidden_stems(pillar: Pillar) -> tuple[tuple[str, str], ...]:
    try:
        hidden_stems = HIDDEN_STEMS[pillar.earthly_branch]
    except KeyError as exc:
        raise ValueError(
            f"Invalid branch: {pillar.earthly_branch!r}"
        ) from exc

    canonical_stems = tuple(stem for stem, _role in hidden_stems)
    if tuple(pillar.hidden_stems) != canonical_stems:
        raise ValueError("provider hidden stems do not match canonical table")
    return hidden_stems


def build_chart_facts(chart: BaziChart) -> ChartFacts:
    if len(chart.pillars) != 4:
        raise ValueError("expected exactly four pillars")

    day_pillars = [pillar for pillar in chart.pillars if pillar.name == "day"]
    if len(day_pillars) != 1:
        raise ValueError("expected exactly one day pillar")
    day_pillar = day_pillars[0]
    if chart.day_master != day_pillar.heavenly_stem:
        raise ValueError("day master does not match day pillar")
    _validate_stem(chart.day_master)

    month_pillars = [
        pillar for pillar in chart.pillars if pillar.name == "month"
    ]
    if len(month_pillars) != 1:
        raise ValueError("expected exactly one month pillar")

    exposed_stems = []
    canonical_hidden_by_pillar = []
    hidden_stem_facts = []
    for pillar in chart.pillars:
        _validate_stem(pillar.heavenly_stem)
        exposed_stems.append(
            StemFact(
                pillar_name=pillar.name,
                stem=pillar.heavenly_stem,
                element=STEM_ELEMENT[pillar.heavenly_stem],
                polarity=STEM_POLARITY[pillar.heavenly_stem],
                ten_god=ten_god(chart.day_master, pillar.heavenly_stem),
            )
        )

        canonical_hidden = _canonical_hidden_stems(pillar)
        canonical_hidden_by_pillar.append((pillar, canonical_hidden))
        hidden_stem_facts.extend(
            HiddenStemFact(
                pillar_name=pillar.name,
                branch=pillar.earthly_branch,
                stem=stem,
                role=role,
                element=STEM_ELEMENT[stem],
                polarity=STEM_POLARITY[stem],
                ten_god=ten_god(chart.day_master, stem),
            )
            for stem, role in canonical_hidden
        )

    roots = []
    for stem_fact in exposed_stems:
        for branch_pillar, canonical_hidden in canonical_hidden_by_pillar:
            roots.extend(
                RootFact(
                    stem=stem_fact.stem,
                    stem_pillar=stem_fact.pillar_name,
                    branch=branch_pillar.earthly_branch,
                    branch_pillar=branch_pillar.name,
                    role=role,
                    exact_stem_root=True,
                )
                for hidden_stem, role in canonical_hidden
                if hidden_stem == stem_fact.stem
            )

    source = chart.chart_source
    return ChartFacts(
        day_master=chart.day_master,
        month_branch=month_pillars[0].earthly_branch,
        exposed_stems=tuple(exposed_stems),
        hidden_stems=tuple(hidden_stem_facts),
        roots=tuple(roots),
        twelve_growth_by_pillar=tuple(
            (
                pillar.name,
                growth_phase(chart.day_master, pillar.earthly_branch),
            )
            for pillar in chart.pillars
        ),
        assumptions=(
            source.calendar_assumption,
            source.timezone_assumption,
            source.solar_terms_assumption,
            f"true_solar_time_applied={source.true_solar_time_applied!r}",
            "No longitude or true-solar-time conversion was inferred from birthplace.",
        ),
    )
