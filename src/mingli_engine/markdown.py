from html import escape

from mingli_engine.models import Report


def _has_reasoned_analysis(report: Report) -> bool:
    audit = report.report_evidence_audit
    return bool(
        audit.computed_rule_family_count
        or audit.indeterminate_rule_family_count
        or audit.disputed_rule_family_count
    )


def _markdown_text(value: str) -> str:
    escaped = escape(value, quote=False)
    markdown_punctuation = frozenset("\\`*_{}[]()#+-.!|~=")
    return "".join(
        f"\\{character}" if character in markdown_punctuation else character
        for character in escaped
    )


def _compact(values: list[str]) -> str:
    return "、".join(_markdown_text(value) for value in values) or "不可用"


def _reasoned_analysis(report: Report) -> list[str]:
    conclusions = report.expanded_evidence.formal_conclusions
    calculation_lines: list[str] = []
    school_views: list[str] = []
    evidence_lines: list[str] = []
    for conclusion in conclusions:
        trace = conclusion.trace
        for view in trace.school_views:
            if view not in school_views:
                school_views.append(view)
        calculation_lines.extend(
            [
                f"#### {_markdown_text(conclusion.title)}",
                _markdown_text(conclusion.body),
                f"- 规则族：{_markdown_text(conclusion.rule_family)}",
                f"- 计算状态：{_markdown_text(trace.calculation_status)}",
                f"- 可信度：{_markdown_text(trace.calculation_confidence)}",
                f"- 支持信号：{_compact(trace.supporting_signals)}",
                f"- 反对信号：{_compact(trace.opposing_signals)}",
                f"- 规则 ID：{_compact(trace.rule_ids)}",
                f"- 证据 ID：{_compact(trace.evidence_ids)}",
                f"- 假设：{_compact(trace.assumptions)}",
                f"- 缺失输入：{_compact(trace.missing_inputs)}",
                "- 分歧说明："
                + (
                    _markdown_text(trace.disagreement_note)
                    if trace.disagreement_note
                    else "不可用"
                ),
                "",
            ]
        )
        evidence_lines.append(
            f"- {_markdown_text(conclusion.title)}：{_compact(trace.evidence_ids)}"
        )

    return [
        "## 推理分析",
        "### 盘面事实",
        _markdown_text(f"{report.chart_card}\n{report.four_pillars_summary}"),
        "### 计算结果",
        "\n".join(calculation_lines).rstrip(),
        "### 流派视角",
        "\n".join(f"- {_markdown_text(view)}" for view in school_views)
        or "- 不可用",
        "### 证据依据",
        "\n".join(evidence_lines) or "- 不可用",
        "### 解读与安全边界",
        _markdown_text(
            f"{report.interpretation_boundaries}\n{report.ethics_reminder}"
        ),
    ]


def render_markdown_report(report: Report) -> str:
    has_reasoned_analysis = _has_reasoned_analysis(report)
    render_text = _markdown_text if has_reasoned_analysis else lambda value: value
    sections = [
        f"# {render_text(report.title)}",
        "## 免责声明",
        render_text(report.disclaimer),
        "## 快速导读",
        render_text(report.quick_guide),
        "## 第一层：基础资料",
        "### 命造卡片",
        render_text(report.chart_card),
        "### 排盘来源与假设",
        render_text(report.assumptions),
        "## 第二层：结构观察",
        "### 四柱与五行摘要",
        render_text(report.four_pillars_summary),
        render_text(report.five_elements_summary),
        "### 十神摘要",
        render_text(report.ten_gods_summary),
        "### 观察依据",
        render_text(report.evidence_notes),
        "### 正式知识综合",
        render_text(report.formal_synthesis),
        "### 综合脉络",
        render_text(report.integrated_synthesis),
        "### 结构分析",
        render_text(report.structure_analysis),
        "### 性格倾向",
        render_text(report.personality_tendencies),
        "## 第三层：解读边界",
        render_text(report.interpretation_boundaries),
        "## 第四层：行动反思",
        "### 优势与议题",
        render_text(report.strengths_and_issues),
        "### 阶段概览",
        render_text(report.phase_overview),
        "### 行动建议",
        render_text(report.action_suggestions),
        "## 术语简注",
        render_text(report.glossary),
        "## 伦理边界提醒",
        render_text(report.ethics_reminder),
    ]
    if has_reasoned_analysis:
        sections.extend(_reasoned_analysis(report))
    return "\n\n".join(sections) + "\n"
