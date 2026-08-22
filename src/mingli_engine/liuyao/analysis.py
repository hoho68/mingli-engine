"""Governed structural analysis over the eight liuyao rule families."""

from __future__ import annotations

import json
from importlib import resources
from dataclasses import dataclass

from mingli_engine.liuyao.constants import (
    BRANCH_ELEMENTS,
    KE_CYCLE,
    LIUYAO_RULE_FAMILIES,
    SHENG_CYCLE,
    six_relation,
)
from mingli_engine.liuyao.knowledge_activation import (
    EVIDENCE_ACTIVATED_NOTE,
    LiuyaoEvidenceCitation,
    LiuyaoEvidenceIndex,
    build_liuyao_evidence_index,
    build_liuyao_matter_category_index,
    citation_from_unit,
    resolve_matter_category,
)
from mingli_engine.liuyao.result_models import LiuyaoChart


class AnalysisConfigError(ValueError):
    """Raised when the liuyao analysis configuration is invalid."""


@dataclass(frozen=True)
class FamilyConfig:
    rule_family: str
    label: str
    headline: str


@dataclass(frozen=True)
class AnalysisConfig:
    families: tuple[FamilyConfig, ...]
    evidence_pending_note: str
    shared_limitations: tuple[str, ...]
    evidence_activated_note: str = EVIDENCE_ACTIVATED_NOTE

    def __post_init__(self) -> None:
        object.__setattr__(self, "families", tuple(self.families))
        object.__setattr__(self, "shared_limitations", tuple(self.shared_limitations))
        if tuple(item.rule_family for item in self.families) != LIUYAO_RULE_FAMILIES:
            raise ValueError("analysis config families must match the governed order")
        if not self.evidence_pending_note.strip() or not self.shared_limitations:
            raise ValueError("analysis config boundary wording is incomplete")
        for item in self.families:
            if not item.label.strip() or not item.headline.strip():
                raise ValueError("analysis config family wording is incomplete")

    def family(self, rule_family: str) -> FamilyConfig:
        return {item.rule_family: item for item in self.families}[rule_family]


def load_analysis_config() -> AnalysisConfig:
    path = resources.files("mingli_engine").joinpath(
        "data/liuyao/analysis_config.json"
    )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AnalysisConfigError("the liuyao analysis config is unavailable") from error
    if not isinstance(raw, dict) or raw.get("schema_version") != (
        "liuyao-analysis-config-v1"
    ):
        raise AnalysisConfigError("the liuyao analysis config is invalid")
    try:
        return AnalysisConfig(
            families=tuple(
                FamilyConfig(
                    rule_family=str(item["rule_family"]),
                    label=str(item["label"]),
                    headline=str(item["headline"]),
                )
                for item in raw["families"]
            ),
            evidence_pending_note=str(raw["evidence_pending_note"]),
            shared_limitations=tuple(
                str(item) for item in raw["shared_limitations"]
            ),
            evidence_activated_note=str(
                raw.get("evidence_activated_note") or EVIDENCE_ACTIVATED_NOTE
            ),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise AnalysisConfigError("the liuyao analysis config is invalid") from error


@dataclass(frozen=True)
class LiuyaoFamilyObservation:
    rule_family: str
    status: str
    headline: str
    observations: tuple[str, ...]
    limitations: tuple[str, ...]
    evidence_note: str
    evidence_citations: tuple[LiuyaoEvidenceCitation, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "observations", tuple(self.observations))
        object.__setattr__(self, "limitations", tuple(self.limitations))
        object.__setattr__(
            self, "evidence_citations", tuple(self.evidence_citations)
        )
        if self.rule_family not in LIUYAO_RULE_FAMILIES:
            raise ValueError("unknown liuyao rule family")
        if self.status not in {"computed", "degraded", "not_computed"}:
            raise ValueError("unsupported observation status")
        if not self.headline.strip():
            raise ValueError("observation headline is required")
        if not self.limitations:
            raise ValueError("observations require limitation language")
        if not self.evidence_note.strip():
            raise ValueError("observation evidence note is required")
        for citation in self.evidence_citations:
            if not isinstance(citation, LiuyaoEvidenceCitation):
                raise TypeError(
                    "evidence citations must be LiuyaoEvidenceCitation values"
                )
            if citation.rule_family != self.rule_family:
                raise ValueError(
                    "evidence citation family must match the observation family"
                )


@dataclass(frozen=True)
class LiuyaoAnalysis:
    chart: LiuyaoChart
    family_observations: tuple[LiuyaoFamilyObservation, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "family_observations", tuple(self.family_observations)
        )
        if not isinstance(self.chart, LiuyaoChart):
            raise TypeError("analysis requires a LiuyaoChart")
        families = tuple(item.rule_family for item in self.family_observations)
        if families != LIUYAO_RULE_FAMILIES:
            raise ValueError("analysis must cover the eight governed families in order")


def _element_relation_text(source: str, target: str) -> str:
    if source == target:
        return "同气"
    if SHENG_CYCLE[source] == target:
        return "相生"
    if KE_CYCLE[source] == target:
        return "相克"
    return "无异动"


def _yong_shen_selection(chart: LiuyaoChart) -> tuple[str, ...]:
    counts: dict[str, int] = {}
    for line in chart.lines:
        counts[line.six_relation] = counts.get(line.six_relation, 0) + 1
    parts = [f"{name}{count}现" for name, count in sorted(counts.items())]
    hidden = [
        f"{line.hidden_spirit.six_relation}伏于{line.position}爻"
        for line in chart.lines
        if line.hidden_spirit is not None
    ]
    observations = ["六亲分布：" + "、".join(parts) + "。"]
    if hidden:
        observations.append("伏神：" + "、".join(hidden) + "。")
    else:
        observations.append("六亲齐备，无需借伏。")
    return tuple(observations)


def _shi_ying_relation(chart: LiuyaoChart) -> tuple[str, ...]:
    shi = chart.lines[chart.ben_gua.shi_position - 1]
    ying = chart.lines[chart.ben_gua.ying_position - 1]
    relation = _element_relation_text(shi.element, ying.element)
    return (
        f"世爻居{shi.position}爻（{shi.ganzhi}{shi.element}），应爻居{ying.position}爻（{ying.ganzhi}{ying.element}）。",
        f"世应五行关系：{relation}。",
    )


def _moving_line_dynamics(chart: LiuyaoChart) -> tuple[str, ...]:
    moving = [line for line in chart.lines if line.moving]
    if not moving:
        return ("本卦安静无动爻，无生克变动。",)
    parts = []
    for line in moving:
        changed = chart.bian_gua
        assert changed is not None
        changed_ganzhi = _changed_line_ganzhi(chart, line.position)
        changed_relation = six_relation(
            _palace_element(chart), changed_ganzhi[1]
        )
        returning = _element_relation_text(
            BRANCH_ELEMENTS[changed_ganzhi[1]], line.element
        )
        parts.append(
            f"{line.position}爻{line.six_relation}{line.ganzhi}动，"
            f"变出{changed_ganzhi}（{changed_relation}），变爻与本爻{returning}。"
        )
    return tuple(parts)


def _changed_line_ganzhi(chart: LiuyaoChart, position: int) -> str:
    from mingli_engine.liuyao.najia import _line_ganzhi

    bian = chart.bian_gua
    assert bian is not None
    return _line_ganzhi(bian, position)


def _palace_element(chart: LiuyaoChart) -> str:
    from mingli_engine.liuyao.constants import TRIGRAM_ELEMENTS

    return TRIGRAM_ELEMENTS[chart.ben_gua.palace]


def _six_spirits_attachment(chart: LiuyaoChart) -> tuple[str, ...]:
    key_lines = []
    for line in chart.lines:
        if line.shi_ying or line.moving:
            role = {"shi": "世爻", "ying": "应爻"}.get(line.shi_ying, "动爻")
            key_lines.append(f"{line.six_spirit}临{line.position}爻（{role}）")
    if not key_lines:
        return ("六神无临世应动爻。",)
    return ("、".join(key_lines) + "。",)


def _month_day_strength(chart: LiuyaoChart) -> tuple[str, ...]:
    month = chart.month_command
    day = chart.day_ganzhi[1]
    month_element = BRANCH_ELEMENTS[month]
    day_element = BRANCH_ELEMENTS[day]
    shi = chart.lines[chart.ben_gua.shi_position - 1]
    same_month = [line for line in chart.lines if line.element == month_element]
    same_day = [line for line in chart.lines if line.element == day_element]
    return (
        f"月建{month}（{month_element}），日辰{day}（{day_element}）。",
        f"世爻五行{shi.element}，与月建{_element_relation_text(shi.element, month_element)}，与日辰{_element_relation_text(shi.element, day_element)}。",
        f"与月建同气之爻{len(same_month)}个，与日辰同气之爻{len(same_day)}个。",
    )


def _void_break_state(chart: LiuyaoChart) -> tuple[str, ...]:
    void = [f"{line.position}爻" for line in chart.lines if line.void]
    month_break = [f"{line.position}爻" for line in chart.lines if line.month_break]
    day_break = [f"{line.position}爻" for line in chart.lines if line.day_break]
    return (
        f"旬空：{chart.xun_void_branches[0]}{chart.xun_void_branches[1]}；临空爻：{'、'.join(void) if void else '无'}。",
        f"月破爻：{'、'.join(month_break) if month_break else '无'}；日破（静爻逢冲）：{'、'.join(day_break) if day_break else '无'}。",
    )


def analyze_liuyao_chart(
    chart: LiuyaoChart,
    *,
    config: AnalysisConfig | None = None,
    evidence_index: LiuyaoEvidenceIndex | None = None,
    matter_category: str | None = None,
) -> LiuyaoAnalysis:
    """Produce governed structural observations for the eight families.

    When ``evidence_index`` is omitted, the governed evidence index is built
    from the frozen knowledge ledgers (failing closed on corruption). Each
    computed family with governed evidence carries the full citations of its
    family; observation text and family statuses are unchanged from V1.

    The optional ``matter_category`` activates the category_judgment family:
    a supported category yields a computed observation carrying that
    category's governed citations; a high-risk category is refused through
    the existing safety mechanism before any analysis; an unknown category
    raises an input validation error. When omitted, the family keeps its V1
    ``not_computed`` behavior.
    """
    if not isinstance(chart, LiuyaoChart):
        raise TypeError("analysis requires a LiuyaoChart")
    gate = resolve_matter_category(matter_category)
    config = config or load_analysis_config()
    if evidence_index is None:
        evidence_index = build_liuyao_evidence_index()
    if not isinstance(evidence_index, LiuyaoEvidenceIndex):
        raise TypeError("evidence_index must be a LiuyaoEvidenceIndex")
    category_index = (
        build_liuyao_matter_category_index(evidence_index)
        if gate.status == "accepted"
        else None
    )
    observations: dict[str, tuple[str, ...]] = {
        "yong_shen_selection": _yong_shen_selection(chart),
        "shi_ying_relation": _shi_ying_relation(chart),
        "moving_line_dynamics": _moving_line_dynamics(chart),
        "six_spirits_attachment": _six_spirits_attachment(chart),
        "month_day_strength": _month_day_strength(chart),
        "void_break_state": _void_break_state(chart),
    }
    family_observations: list[LiuyaoFamilyObservation] = []
    for family in config.families:
        if family.rule_family == "yingqi_timing":
            family_observations.append(
                LiuyaoFamilyObservation(
                    rule_family=family.rule_family,
                    status="degraded",
                    headline=family.headline,
                    observations=(
                        "应期推断需要明确所问事项与更多传统证据，现阶段只提示空亡、月破、动爻等候选位置。",
                    ),
                    limitations=config.shared_limitations,
                    evidence_note=config.evidence_pending_note,
                )
            )
            continue
        if family.rule_family == "category_judgment":
            if gate.status != "accepted":
                family_observations.append(
                    LiuyaoFamilyObservation(
                        rule_family=family.rule_family,
                        status="not_computed",
                        headline=family.headline,
                        observations=(
                            "V1 未提供事项类别输入，分类占断不启用。",
                        ),
                        limitations=config.shared_limitations,
                        evidence_note=config.evidence_pending_note,
                    )
                )
                continue
            assert category_index is not None
            assert gate.category is not None
            category_units = category_index.units_for(gate.category)
            category_citations = tuple(
                citation_from_unit(unit) for unit in category_units
            )
            family_observations.append(
                LiuyaoFamilyObservation(
                    rule_family=family.rule_family,
                    status="computed",
                    headline=family.headline,
                    observations=(
                        f"所问事项类别：{gate.label}。",
                        (
                            f"本族按事项类别激活{len(category_citations)}条"
                            "已晋升的分类占断证据，仅呈现传统文献信号，"
                            "不作现实预测。"
                        ),
                    ),
                    limitations=config.shared_limitations,
                    evidence_note=config.evidence_activated_note,
                    evidence_citations=category_citations,
                )
            )
            continue
        family_units = evidence_index.family(family.rule_family)
        citations = tuple(citation_from_unit(unit) for unit in family_units)
        family_observations.append(
            LiuyaoFamilyObservation(
                rule_family=family.rule_family,
                status="computed",
                headline=family.headline,
                observations=observations[family.rule_family],
                limitations=config.shared_limitations,
                evidence_note=(
                    config.evidence_activated_note
                    if citations
                    else config.evidence_pending_note
                ),
                evidence_citations=citations,
            )
        )
    return LiuyaoAnalysis(
        chart=chart,
        family_observations=tuple(family_observations),
    )
