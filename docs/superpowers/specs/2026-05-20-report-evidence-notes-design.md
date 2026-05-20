# Report Evidence Notes Design

## Context

The project can already generate safe, layered Bazi Markdown reports from automatic
charts and externally verified charts. Features 004 through 008 improved the
report structure, reader-facing language, structure-observation wording,
inter-layer transitions, and regression coverage.

Feature 009 should make the report more reviewable. The current report tells
readers what the structure observations are, but it does not yet give a compact
reader-facing explanation of what those observations are based on. The next
increment should add an evidence-note layer that helps readers connect report
statements back to chart source, four pillars, element signals, ten-god signals,
and action-reflection boundaries.

## Goal

Add a small "observation basis" section to the formal Markdown report. This
section should explain, in plain language, which existing chart and report
signals support the current observations.

The feature must improve transparency without adding new fortune-telling
judgments, new calculations, new CLI behavior, or new export formats.

## Recommended Feature Name

- Branch/spec short name: `report-evidence-notes`
- Feature number: `009`
- Chinese name: `报告证据说明层`

## User Value

Readers should be able to answer a simple question while reading the report:
"Where did this observation come from?"

Maintainers should also get a clearer contract for future report changes. If a
later change adds or moves report text, tests should catch whether the report
still explains the basis for its structural observations.

## Scope

### In Scope

- Add one reader-facing evidence-note section to generated Markdown reports.
- Place the section inside `第二层：结构观察`, after the report has shown core
  structure information and before deeper interpretation text.
- Use plain-language bullet points to connect existing observations to:
  - chart source and assumptions
  - four pillars
  - visible, hidden, and total five-element signals
  - ten-god relationship signals
  - action reflection as review prompts rather than predictions
- Keep the language conservative and non-deterministic.
- Extend tests and regression checks so safe Markdown reports must include the
  new evidence-note section.

### Out of Scope

- No new Bazi conclusions, auspiciousness claims, strength verdicts, useful-god
  verdicts, pattern verdicts, luck-cycle judgments, or event predictions.
- No new chart calculation rules.
- No new CLI command, flag, or input data shape.
- No HTML, PDF, PNG, or visual export.
- No long-term report archive or personal data storage.
- No full Markdown snapshots.

## Proposed Report Placement

The Markdown report should keep the existing main layer order:

1. `免责声明`
2. `快速导读`
3. `第一层：基础资料`
4. `第二层：结构观察`
5. `第三层：解读边界`
6. `第四层：行动反思`
7. glossary and ethics reminder

Within `第二层：结构观察`, the new section should be added as:

```text
### 观察依据
```

Recommended placement:

```text
## 第二层：结构观察
### 四柱与五行摘要
...
### 十神摘要
...
### 观察依据
...
### 结构分析
...
### 性格倾向
...
```

This placement lets the reader first see the raw structural summaries, then see
how to read those summaries before moving into broader structure analysis.

## Evidence Note Content

The section should be concise. A good first version is a short bullet list. The
exact text can evolve, but it should cover these stable ideas:

- The report starts from chart source and assumptions, not unsupported certainty.
- Four-pillar observations come from the year, month, day, and hour pillars.
- Five-element observations come from visible stems, hidden stems, and total
  counted signals.
- Ten-god observations are relationship signals across pillar positions.
- Action reflection turns structural signals into review prompts; it does not
  promise outcomes.

Example wording direction:

```text
- 来源依据：先看排盘来源与历法、时区、节气等假设，避免把前提当成结论。
- 四柱依据：年柱、月柱、日柱、时柱只提供结构位置和组合线索，不单独断事。
- 五行依据：明面信号、藏干信号和合计信号用于观察分布，不用于给人生下定论。
- 十神依据：十神关系按柱位理解为关系线索，需要结合解读边界一起阅读。
- 行动依据：行动反思只把可观察线索转成复盘问题，不预测具体结果。
```

The implementation may refine exact wording, but it should preserve the
reader-facing meaning and avoid machine labels.

## Data And Report Shape

The project currently uses a `Report` dataclass and a Markdown renderer. The
cleanest design is to add one report field for the evidence-note text and render
it in the existing Markdown flow.

The field should be derived from existing chart and interpretation objects. It
should not require new user input and should not compute new Bazi judgments.

## Safety And Ethics

The evidence-note section must reinforce the project constitution:

- Cultural interpretation, not fate verdict.
- Transparent calculation boundary.
- Ethical red lines and professional-domain boundaries.
- Reviewable reports.
- Test-first quality gates.

The section should explicitly avoid absolute destiny language such as `必定`,
`注定`, `一定会`, and `死定`.

## Testing Strategy

Use test-first implementation.

Recommended tests:

- Unit test that `build_report` returns a non-empty evidence-note field.
- Unit test that the evidence-note text mentions source assumptions, four
  pillars, five-element signals, ten-god signals, and action-reflection boundary.
- Markdown renderer test that `### 观察依据` appears inside `第二层：结构观察` in
  the intended order.
- Safety test or existing report-language test extension confirming the evidence
  note does not introduce absolute destiny language.
- Integration regression update so `examples/report-regression-cases.json` safe
  Markdown cases continue to protect the new section.
- Full suite verification after implementation.

## Success Criteria

- Every formal safe Markdown report includes `### 观察依据`.
- The evidence-note section appears in the structure-observation layer, after
  structure summaries and before broader interpretation text.
- Safe report regression cases verify the section for both automatic and
  externally verified report paths.
- The feature introduces no new CLI commands, flags, input shapes, chart
  calculations, or interpretation conclusions.
- All existing tests and the new tests pass.

## Risks And Mitigations

- Risk: The new section becomes another place for hidden judgment.
  - Mitigation: Keep wording focused on basis, boundaries, and review prompts.
- Risk: Report gets too long.
  - Mitigation: Keep the section to a compact bullet list.
- Risk: Tests over-freeze wording.
  - Mitigation: Assert durable phrases and placement, not a full Markdown
    snapshot.

## Recommended Next Step

Create the Spec Kit feature specification for `009-report-evidence-notes`, then
plan implementation tasks around the evidence-note field, renderer placement,
and regression updates.
