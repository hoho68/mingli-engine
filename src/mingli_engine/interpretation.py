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


@dataclass(frozen=True)
class TenGodPlacement:
    ten_god: str
    pillars: list[str]


@dataclass(frozen=True)
class BasicInterpretationSummary:
    element_distribution: ElementDistribution
    five_elements_summary: str
    day_master_summary: str
    ten_gods_summary: str
    structure_observations: str
    focus_suggestions: str
    limitations: str


PILLAR_DISPLAY_NAMES = {
    "year": "年柱",
    "month": "月柱",
    "day": "日柱",
    "hour": "时柱",
    "time": "时柱",
}

UNKNOWN_TEN_GODS = frozenset({"unknown", "未知", "未说明", "未标明", "无", "暂无"})


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


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


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
        unknown_signals=_dedupe_preserving_order(unknown_signals),
    )


def _display_pillar_name(name: str) -> str:
    return PILLAR_DISPLAY_NAMES.get(name.strip(), name.strip() or "未知柱")


def _format_counts(counts: dict[str, int]) -> str:
    return "、".join(f"{element}{counts[element]}" for element in FIVE_ELEMENTS)


def _format_missing_elements(elements: list[str]) -> str:
    return "、".join(elements)


def _is_unknown_ten_god(ten_god: str) -> bool:
    normalized = ten_god.strip()
    return not normalized or normalized.casefold() in UNKNOWN_TEN_GODS


def summarize_ten_god_placements(chart: BaziChart) -> list[TenGodPlacement]:
    placement_by_ten_god: dict[str, list[str]] = {}

    for pillar in chart.pillars:
        ten_god = pillar.ten_god.strip()
        if _is_unknown_ten_god(ten_god):
            continue

        placement_by_ten_god.setdefault(ten_god, []).append(
            _display_pillar_name(pillar.name)
        )

    return [
        TenGodPlacement(ten_god=ten_god, pillars=pillars)
        for ten_god, pillars in placement_by_ten_god.items()
    ]


def _build_five_elements_text(distribution: ElementDistribution) -> str:
    direct_text = _format_counts(distribution.direct_counts)
    hidden_text = _format_counts(distribution.hidden_counts)
    total_text = _format_counts(distribution.total_counts)
    parts = [
        f"五行信号观察：明面信号为{direct_text}；藏干信号为{hidden_text}；合计为{total_text}。",
        "这些数量用于观察结构分布，不等同于完整旺衰模型。",
    ]

    if distribution.dominant_elements:
        dominant = "、".join(distribution.dominant_elements)
        parts.append(f"当前可计数信号中，{dominant}较为集中，可作为后续观察重点。")

    if distribution.missing_elements:
        missing = _format_missing_elements(distribution.missing_elements)
        parts.append(
            f"{missing}暂未形成可计数信号；这提示结构中相关表达较少，"
            "不等于现实能力缺失。"
        )

    if distribution.unknown_signals:
        unknown = "、".join(distribution.unknown_signals)
        parts.append(f"另有未识别信号：{unknown}，本层不作推断。")

    return "\n".join(parts)


def _build_day_master_text(chart: BaziChart) -> str:
    day_master = chart.day_master.strip() or "未标明"
    return (
        f"日主{day_master}作为观察中心，用来组织四柱、五行与十神的相对关系。"
        "这里仅说明观察坐标，不据此给出性格或结果定论。"
    )


def _build_ten_gods_text(chart: BaziChart) -> str:
    pillar_lines = []
    missing_pillars = []

    for pillar in chart.pillars:
        pillar_name = _display_pillar_name(pillar.name)
        ten_god = pillar.ten_god.strip()
        if _is_unknown_ten_god(ten_god):
            missing_pillars.append(pillar_name)
            continue
        pillar_lines.append(f"{pillar_name}：{ten_god}")

    if not pillar_lines:
        text = "十神结构观察：当前没有可读的十神信号，本层保留为空白观察。"
        if missing_pillars:
            text += f"\n未识别十神位置：{'、'.join(missing_pillars)}，本层不作补猜。"
        return text

    text = "十神结构观察：\n" + "\n".join(pillar_lines)
    placements = summarize_ten_god_placements(chart)
    repeated = [
        placement
        for placement in placements
        if len(placement.pillars) > 1
    ]
    if repeated:
        repeated_text = "；".join(
            f"{placement.ten_god}见于{'、'.join(placement.pillars)}"
            for placement in repeated
        )
        text += f"\n重复信号：{repeated_text}，表示该类关系可多留意。"
    if missing_pillars:
        text += f"\n未识别十神位置：{'、'.join(missing_pillars)}，本层不作补猜。"
    return text


def _build_structure_text(distribution: ElementDistribution) -> str:
    observations = ["基础结构观察：五行分布先看有无、多少与集中度。"]
    if distribution.dominant_elements:
        dominant = "、".join(distribution.dominant_elements)
        observations.append(f"{dominant}信号相对突出，可观察其在明面与藏干中的来源。")
    if distribution.missing_elements:
        missing = _format_missing_elements(distribution.missing_elements)
        observations.append(f"{missing}暂未形成可计数信号，适合结合具体问题再看表达方式。")
    if not distribution.dominant_elements and not distribution.missing_elements:
        observations.append("五行信号均有出现，可继续比较明面与藏干的层次差异。")
    return "\n".join(observations)


def _build_suggestion_text(
    chart: BaziChart,
    distribution: ElementDistribution,
) -> str:
    focus_topic = chart.birth_profile.focus_topic.strip() or "当前关注主题"
    if distribution.dominant_elements:
        suggestions = [
            f"围绕{focus_topic}，可先把较集中的信号视为稳定出现的观察材料。",
        ]
    else:
        suggestions = [
            f"围绕{focus_topic}，当前暂无可计数五行信号，建议先核对输入来源再继续解读。",
        ]
    if distribution.missing_elements:
        missing = _format_missing_elements(distribution.missing_elements)
        suggestions.append(
            f"对{missing}暂未形成可计数信号的部分，可从环境支持、学习经验与协作资源中观察，"
            "不等于现实能力缺失。"
        )
    suggestions.append("建议把本摘要作为复盘提纲，而不是行动结论。")
    return "\n".join(suggestions)


def _build_limitations_text(distribution: ElementDistribution) -> str:
    limitations = [
        "不做格局定论：本层只整理基础结构信号。",
        "不做用神定论：五行数量不替代完整取用分析。",
        "不做大运流年判断：不推断阶段吉凶或现实结果。",
    ]
    if distribution.unknown_signals:
        limitations.append("存在未识别信号，已作为边界说明保留。")
    return "\n".join(limitations)


def build_basic_interpretation(chart: BaziChart) -> BasicInterpretationSummary:
    distribution = count_element_distribution(chart)
    return BasicInterpretationSummary(
        element_distribution=distribution,
        five_elements_summary=_build_five_elements_text(distribution),
        day_master_summary=_build_day_master_text(chart),
        ten_gods_summary=_build_ten_gods_text(chart),
        structure_observations=_build_structure_text(distribution),
        focus_suggestions=_build_suggestion_text(chart, distribution),
        limitations=_build_limitations_text(distribution),
    )
