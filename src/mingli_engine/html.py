from html import escape

from mingli_engine.models import Report


_STYLE = """
:root {
  color-scheme: light;
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
  color: #24302f;
  background: #f6f1e7;
}

body {
  margin: 0;
  background: #f6f1e7;
}

main {
  max-width: 920px;
  margin: 0 auto;
  padding: 40px 24px 56px;
}

h1,
h2,
h3 {
  line-height: 1.35;
}

h1 {
  margin: 0 0 28px;
  font-size: 2rem;
  color: #1e3a36;
}

h2 {
  margin: 30px 0 14px;
  padding-top: 18px;
  border-top: 1px solid #d7cfc0;
  font-size: 1.3rem;
  color: #36564e;
}

h3 {
  margin: 22px 0 10px;
  font-size: 1.05rem;
  color: #5a4632;
}

.report-text {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.75;
}

@media print {
  body {
    background: #fff;
  }

  main {
    padding: 0;
  }
}
""".strip()


def _text(value: str) -> str:
    return escape(value, quote=True)


def _block(value: str) -> str:
    return f'<div class="report-text">{_text(value)}</div>'


def _section(heading: str, body: str) -> str:
    return f"<section>\n<h2>{_text(heading)}</h2>\n{body}\n</section>"


def _subsection(heading: str, text: str) -> str:
    return f"<section>\n<h3>{_text(heading)}</h3>\n{_block(text)}\n</section>"


def _has_reasoned_analysis(report: Report) -> bool:
    audit = report.report_evidence_audit
    return bool(
        audit.computed_rule_family_count
        or audit.indeterminate_rule_family_count
        or audit.disputed_rule_family_count
    )


def _compact(values: list[str]) -> str:
    return "、".join(values) or "不可用"


def _reasoned_list(lines: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f"<li><strong>{_text(label)}：</strong>{_text(value)}</li>"
        for label, value in lines
    )
    return f"<ul>\n{items}\n</ul>"


def _reasoned_analysis(report: Report) -> str:
    conclusion_blocks: list[str] = []
    school_views: list[str] = []
    evidence_lines: list[tuple[str, str]] = []
    for conclusion in report.expanded_evidence.formal_conclusions:
        trace = conclusion.trace
        for view in trace.school_views:
            if view not in school_views:
                school_views.append(view)
        details = _reasoned_list(
            [
                ("规则族", conclusion.rule_family),
                ("计算状态", trace.calculation_status),
                ("可信度", trace.calculation_confidence),
                ("支持信号", _compact(trace.supporting_signals)),
                ("反对信号", _compact(trace.opposing_signals)),
                ("规则 ID", _compact(trace.rule_ids)),
                ("证据 ID", _compact(trace.evidence_ids)),
                ("假设", _compact(trace.assumptions)),
                ("缺失输入", _compact(trace.missing_inputs)),
                ("分歧说明", trace.disagreement_note or "不可用"),
            ]
        )
        conclusion_blocks.append(
            "\n".join(
                [
                    "<article>",
                    f"<h4>{_text(conclusion.title)}</h4>",
                    _block(conclusion.body),
                    details,
                    "</article>",
                ]
            )
        )
        evidence_lines.append((conclusion.title, _compact(trace.evidence_ids)))

    body = "\n".join(
        [
            _subsection(
                "盘面事实",
                f"{report.chart_card}\n{report.four_pillars_summary}",
            ),
            "<section>\n<h3>"
            + _text("计算结果")
            + "</h3>\n"
            + "\n".join(conclusion_blocks)
            + "\n</section>",
            "<section>\n<h3>"
            + _text("流派视角")
            + "</h3>\n"
            + _reasoned_list(
                [("流派视角", view) for view in school_views]
                or [("流派视角", "不可用")]
            )
            + "\n</section>",
            "<section>\n<h3>"
            + _text("证据依据")
            + "</h3>\n"
            + _reasoned_list(evidence_lines or [("证据", "不可用")])
            + "\n</section>",
            _subsection(
                "解读与安全边界",
                f"{report.interpretation_boundaries}\n{report.ethics_reminder}",
            ),
        ]
    )
    return _section("推理分析", body)


def render_html_report(report: Report) -> str:
    basic_data = "\n".join(
        [
            _subsection("命造卡片", report.chart_card),
            _subsection("排盘来源与假设", report.assumptions),
        ]
    )
    structure_observation = "\n".join(
        [
            _subsection(
                "四柱与五行摘要",
                f"{report.four_pillars_summary}\n{report.five_elements_summary}",
            ),
            _subsection("十神摘要", report.ten_gods_summary),
            _subsection("观察依据", report.evidence_notes),
            _subsection("正式知识综合", report.formal_synthesis),
            _subsection("综合脉络", report.integrated_synthesis),
            _subsection("结构分析", report.structure_analysis),
            _subsection("性格倾向", report.personality_tendencies),
        ]
    )
    action_reflection = "\n".join(
        [
            _subsection("优势与议题", report.strengths_and_issues),
            _subsection("阶段概览", report.phase_overview),
            _subsection("行动建议", report.action_suggestions),
        ]
    )
    sections = "\n".join(
        [
            _section("免责声明", _block(report.disclaimer)),
            _section("快速导读", _block(report.quick_guide)),
            _section("第一层：基础资料", basic_data),
            _section("第二层：结构观察", structure_observation),
            _section("第三层：解读边界", _block(report.interpretation_boundaries)),
            _section("第四层：行动反思", action_reflection),
            _section("术语简注", _block(report.glossary)),
            _section("伦理边界提醒", _block(report.ethics_reminder)),
        ]
    )
    if _has_reasoned_analysis(report):
        sections = "\n".join([sections, _reasoned_analysis(report)])

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="zh-CN">',
            "<head>",
            '<meta charset="utf-8">',
            "<title>" + _text(report.title) + "</title>",
            "<style>",
            _STYLE,
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>" + _text(report.title) + "</h1>",
            sections,
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )
