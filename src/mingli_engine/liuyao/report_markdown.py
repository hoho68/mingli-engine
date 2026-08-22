"""Deterministic Markdown renderer for liuyao reports (V1)."""

from __future__ import annotations

from mingli_engine.liuyao.report import LiuyaoReport

_CAST_MODE_LABELS = {
    "explicit": "显式爻录入",
    "time": "时间起卦",
    "number": "数字起卦",
}
_STATUS_LABELS = {
    "computed": "已观察",
    "degraded": "降级观察",
    "not_computed": "未启用",
}


def render_liuyao_markdown(report: LiuyaoReport) -> str:
    """Render a report into deterministic Markdown."""
    if not isinstance(report, LiuyaoReport):
        raise TypeError("render requires a LiuyaoReport")
    chart = report.analysis.chart
    ben = chart.ben_gua
    lines: list[str] = [
        f"# {report.title}",
        "",
        "## 免责声明",
        "",
        report.disclaimer,
        "",
        "## 起卦信息",
        "",
        f"- 起卦方式：{_CAST_MODE_LABELS[chart.cast_mode]}",
        f"- 起卦时刻：{chart.cast_datetime}（公历，UTC+08 墙钟假设，未用真太阳时）",
        f"- 月建：{chart.month_command}；日辰：{chart.day_ganzhi}；旬空：{chart.xun_void_branches[0]}{chart.xun_void_branches[1]}",
        "",
        "## 装卦",
        "",
        f"- 本卦：{ben.gua_name}（{ben.palace}宫，{'本宫' if ben.palace_sequence == 0 else f'序列{ben.palace_sequence}'}）",
        f"- 世爻：{ben.shi_position} 爻；应爻：{ben.ying_position} 爻",
        f"- 变卦：{chart.bian_gua.gua_name if chart.bian_gua else '无（静卦）'}",
        f"- 互卦：{chart.hu_gua.gua_name}",
        "",
        "## 逐爻明细",
        "",
        "| 爻位 | 干支 | 五行 | 六亲 | 六神 | 世应 | 状态 |",
        "|---|---|---|---|---|---|---|",
    ]
    for line in reversed(chart.lines):
        marks: list[str] = []
        if line.moving:
            marks.append("动")
        if line.void:
            marks.append("空")
        if line.month_break:
            marks.append("月破")
        if line.day_break:
            marks.append("日破")
        if line.hidden_spirit is not None:
            marks.append(f"伏{line.hidden_spirit.six_relation}{line.hidden_spirit.ganzhi}")
        lines.append(
            f"| {line.position}爻 | {line.ganzhi} | {line.element} | "
            f"{line.six_relation} | {line.six_spirit} | "
            f"{ {'shi': '世', 'ying': '应'}.get(line.shi_ying, '') } | "
            f"{'、'.join(marks) if marks else '平'} |"
        )
    lines.extend(("", "## 各族观察", ""))
    for observation in report.analysis.family_observations:
        lines.append(f"### {observation.headline}（{_STATUS_LABELS[observation.status]}）")
        lines.append("")
        for text in observation.observations:
            lines.append(f"- {text}")
        for limitation in observation.limitations:
            lines.append(f"- 限制：{limitation}")
        lines.append(f"- 证据说明：{observation.evidence_note}")
        lines.append("")
    lines.extend(
        (
            "## 边界说明",
            "",
            "- 本报告不输出精确断语；涉及寿命、疾病、法律、财务等主题时仅保留传统文献信号并附边界，或不予回答。",
            "- 起卦与断法口径存在流派差异；本报告按文档化的纳甲通例装卦。",
            "",
        )
    )
    return "\n".join(lines)
