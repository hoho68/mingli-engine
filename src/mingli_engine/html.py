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
