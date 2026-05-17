# Report Readability Layer Design

## Goal

Improve the Markdown Bazi report so it feels layered and easy to scan. The feature reorganizes and lightly rewrites existing report content, but does not add new divination rules, new conclusions, new CLI options, or new report data requirements.

The target reading experience is a "layered reading version": a user can first read a short guide, then inspect source assumptions, then read structure observations, then see boundaries and practical reflection prompts.

## User Experience

The report should answer three reader questions in order:

1. What should I notice first?
2. What chart facts support the observation?
3. What should I avoid over-reading, and what can I reflect on next?

The first screen of the Markdown report should include a concise quick guide after the disclaimer or near the top of the report. It should summarize the most important safe observations in three to five bullets:

- one bullet for chart source and confidence
- one bullet for the primary five-elements observation
- one bullet for day-master or ten-god observation
- one bullet for the boundary of interpretation
- optionally one bullet for the user's focus topic

## Report Structure

The final Markdown should keep the current public report shape recognizable, while adding clearer reading layers:

1. `# 八字结构化报告`
2. `## 免责声明`
3. `## 快速导读`
4. `## 第一层：基础资料`
5. `## 第二层：结构观察`
6. `## 第三层：解读边界`
7. `## 第四层：行动反思`
8. `## 术语简注`
9. `## 伦理边界提醒`

Within these layers, existing content can remain as subsections or bold labels. For example:

- `命造卡片` and `排盘来源与假设` belong under `第一层：基础资料`.
- `四柱与五行摘要`, `十神摘要`, `结构分析`, and `性格倾向` belong under `第二层：结构观察`.
- The limitation text currently embedded in structure and phase overview should be easy to find under `第三层：解读边界`.
- `优势与议题`, `阶段概览`, and `行动建议` belong under `第四层：行动反思`.

## Section Writing Pattern

Important sections should follow a simple pattern when the content supports it:

```text
观察：
依据：
边界：
提示：
```

This is a writing pattern, not a rigid schema. The renderer can use bold labels such as `**观察：**` in Markdown. Sections that are purely factual, such as source assumptions, do not need all four labels.

The wording should stay plain and beginner-friendly. It should avoid long paragraphs where a short bullet list is clearer.

## Data And Responsibility Boundaries

The feature should reuse the existing `Report` object and existing interpretation summary text. It may add fields to `Report` only if that clearly reduces duplication or keeps the renderer simple.

The renderer remains responsible for Markdown section layout. The report schema remains responsible for preparing safe report text. The interpretation module remains responsible for deterministic structure observations.

No new external service, LLM call, prompt generation, database, or file format is introduced.

## Safety Boundaries

The readability layer must preserve all existing safety behavior:

- every formal report still includes the disclaimer
- unsafe focus topics still refuse formal Markdown output
- source disclosure remains visible
- output still avoids absolute destiny language such as `必定`, `注定`, `一定会`, and `死定`
- wording must not turn element absence, repeated ten-gods, or structural concentration into fate verdicts

The new quick guide must be especially conservative because readers may only skim that section.

## Testing Strategy

Tests should cover the user-facing Markdown contract:

- the report contains `## 快速导读`
- the report contains the four reading layers in order
- source disclosure remains visible
- structure observations remain visible
- boundary language remains visible and not duplicated excessively
- action reflection still includes the user's focus topic
- unsafe focus topics still return safety JSON instead of Markdown
- prohibited deterministic phrases do not appear in generated reports

Unit tests can cover renderer structure. Integration tests should cover both `generate-report` and `calculate-report` paths.

## Non-Goals

- Do not add new Bazi rules.
- Do not calculate pattern, useful god, luck cycles, annual cycles, or auspiciousness.
- Do not change existing CLI command names, flags, or input JSON shapes.
- Do not create a web UI or visual report.
- Do not make the report shorter by removing required source, disclaimer, or safety content.

## Open Decisions Resolved

- The chosen direction is the layered reading version.
- The output remains Markdown-only.
- The feature prioritizes clearer hierarchy over adding more content.
- Existing report data and safety gates remain authoritative.
