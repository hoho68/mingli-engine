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
    markdown_punctuation = frozenset("\\`*_{}[]()#+-.!|")
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
        for signal in trace.chart_signals:
            if signal.startswith("school_view:") and signal not in school_views:
                school_views.append(signal)
        opposing = [trace.disagreement_note] if trace.disagreement_note else []
        calculation_lines.extend(
            [
                f"#### {_markdown_text(conclusion.title)}",
                _markdown_text(conclusion.body),
                f"- 规则族：{_markdown_text(conclusion.rule_family)}",
                f"- 计算状态：{_markdown_text(trace.calculation_status)}",
                f"- 可信度：{_markdown_text(trace.calculation_confidence)}",
                f"- 支持信号：{_compact(trace.chart_signals)}",
                f"- 反对信号：{_compact(opposing)}",
                "- 规则 ID：不可用",
                f"- 证据 ID：{_compact(trace.evidence_ids)}",
                f"- 假设：{_compact(trace.assumptions)}",
                "- 缺失输入：不可用",
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
    evidence_notes = report.evidence_notes
    formal_synthesis = report.formal_synthesis
    integrated_synthesis = report.integrated_synthesis
    if has_reasoned_analysis:
        evidence_notes = _markdown_text(evidence_notes)
        formal_synthesis = _markdown_text(formal_synthesis)
        integrated_synthesis = _markdown_text(integrated_synthesis)
    sections = [
        f"# {report.title}",
        "## 免责声明",
        report.disclaimer,
        "## 快速导读",
        report.quick_guide,
        "## 第一层：基础资料",
        "### 命造卡片",
        report.chart_card,
        "### 排盘来源与假设",
        report.assumptions,
        "## 第二层：结构观察",
        "### 四柱与五行摘要",
        report.four_pillars_summary,
        report.five_elements_summary,
        "### 十神摘要",
        report.ten_gods_summary,
        "### 观察依据",
        evidence_notes,
        "### 正式知识综合",
        formal_synthesis,
        "### 综合脉络",
        integrated_synthesis,
        "### 结构分析",
        report.structure_analysis,
        "### 性格倾向",
        report.personality_tendencies,
        "## 第三层：解读边界",
        report.interpretation_boundaries,
        "## 第四层：行动反思",
        "### 优势与议题",
        report.strengths_and_issues,
        "### 阶段概览",
        report.phase_overview,
        "### 行动建议",
        report.action_suggestions,
        "## 术语简注",
        report.glossary,
        "## 伦理边界提醒",
        report.ethics_reminder,
    ]
    if has_reasoned_analysis:
        sections.extend(_reasoned_analysis(report))
    return "\n\n".join(sections) + "\n"
