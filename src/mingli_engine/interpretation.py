from dataclasses import dataclass

from mingli_engine.models import BaziChart


FIVE_ELEMENTS = ("木", "火", "土", "金", "水")

STEM_ELEMENTS = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}

BRANCH_ELEMENTS = {
    "寅": "木",
    "卯": "木",
    "巳": "火",
    "午": "火",
    "辰": "土",
    "戌": "土",
    "丑": "土",
    "未": "土",
    "申": "金",
    "酉": "金",
    "亥": "水",
    "子": "水",
}


@dataclass(frozen=True)
class ElementDistribution:
    direct_counts: dict[str, int]
    hidden_counts: dict[str, int]
    total_counts: dict[str, int]
    dominant_elements: list[str]
    missing_elements: list[str]
    unknown_signals: list[str]


def _empty_counts() -> dict[str, int]:
    return dict.fromkeys(FIVE_ELEMENTS, 0)


def _count_signal(
    counts: dict[str, int],
    signal: str,
    mapping: dict[str, str],
    unknown_signals: list[str],
) -> None:
    signal = signal.strip()
    if not signal:
        return

    element = mapping.get(signal)
    if element is None:
        unknown_signals.append(signal)
        return

    counts[element] += 1


def count_element_distribution(chart: BaziChart) -> ElementDistribution:
    direct_counts = _empty_counts()
    hidden_counts = _empty_counts()
    unknown_signals: list[str] = []

    for pillar in chart.pillars:
        _count_signal(
            direct_counts,
            pillar.heavenly_stem,
            STEM_ELEMENTS,
            unknown_signals,
        )
        _count_signal(
            direct_counts,
            pillar.earthly_branch,
            BRANCH_ELEMENTS,
            unknown_signals,
        )

        for hidden_stem in pillar.hidden_stems:
            _count_signal(
                hidden_counts,
                hidden_stem,
                STEM_ELEMENTS,
                unknown_signals,
            )

    total_counts = {
        element: direct_counts[element] + hidden_counts[element]
        for element in FIVE_ELEMENTS
    }
    highest_count = max(total_counts.values())
    dominant_elements = (
        []
        if highest_count == 0
        else [
            element
            for element in FIVE_ELEMENTS
            if total_counts[element] == highest_count
        ]
    )

    return ElementDistribution(
        direct_counts=direct_counts,
        hidden_counts=hidden_counts,
        total_counts=total_counts,
        dominant_elements=dominant_elements,
        missing_elements=[
            element for element in FIVE_ELEMENTS if total_counts[element] == 0
        ],
        unknown_signals=unknown_signals,
    )


def build_basic_interpretation(chart: BaziChart):
    raise NotImplementedError("Basic interpretation summaries are implemented in a later task.")
