from mingli_engine.models import Report


def render_markdown_report(report: Report) -> str:
    sections = [
        f"# {report.title}",
        "## 免责声明",
        report.disclaimer,
        "## 命造卡片",
        report.chart_card,
        "## 排盘来源与假设",
        report.assumptions,
        "## 四柱与五行摘要",
        report.four_pillars_summary,
        report.five_elements_summary,
        "## 十神摘要",
        report.ten_gods_summary,
        "## 结构分析",
        report.structure_analysis,
        "## 性格倾向",
        report.personality_tendencies,
        "## 优势与议题",
        report.strengths_and_issues,
        "## 阶段概览",
        report.phase_overview,
        "## 行动建议",
        report.action_suggestions,
        "## 术语简注",
        report.glossary,
        "## 伦理边界提醒",
        report.ethics_reminder,
    ]
    return "\n\n".join(sections) + "\n"
