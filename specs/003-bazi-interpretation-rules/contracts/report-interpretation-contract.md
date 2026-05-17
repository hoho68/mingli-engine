# Report Interpretation Contract: 八字基础结构解读规则层

## Scope

This feature extends the existing formal report content. It does not add a new CLI command, input field, output format, web API, or storage contract.

Existing supported entry points remain unchanged:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

## Markdown Output Contract

For a complete chart with an allowed focus topic, the generated Markdown report MUST keep the existing report title and section shape, including:

- `# 八字结构化报告`
- `## 免责声明`
- `## 排盘来源与假设`
- `## 四柱与五行摘要`
- `## 五行结构观察`
- `## 十神结构观察`
- `## 结构分析`
- `## 性格与行为倾向`
- `## 优势与议题`
- `## 阶段概览`
- `## 行动建议`
- `## 术语简注`
- `## 伦理边界提醒`

The five-elements section MUST include:

- A non-empty `五行信号观察` summary.
- Wording that distinguishes `明面信号` from `藏干` support signals.
- Neutral language for dominant, sparse, or missing signals.
- Limitation wording that says these counts are observation signals, not a complete strength model.

The day-master-related wording MUST include:

- The chart day master.
- A plain-language explanation that the day master is the `观察中心`.
- No claim that the day master determines fate, personality, or outcome.

The ten-gods section MUST include:

- A readable placement summary when ten-god data is present.
- Pillar placement labels such as `年柱`, `月柱`, `日柱`, and `时柱` when the source names can be mapped.
- Neutral wording when one ten-god repeats across pillars.
- Explicit limitation wording when ten-god data is blank or unknown.

The structure analysis and suggestions MUST include:

- The phrase `基础结构观察` or equivalent wording.
- Limitation wording that this feature does not decide `格局`, `用神`, `大运流年`, auspiciousness, or fate outcomes.
- Practical reflection prompts tied to the safe focus topic and observed structure signals.

## Safety Contract

For a red-line focus topic, existing refusal behavior remains authoritative:

- The CLI returns exit code `3`.
- The CLI outputs a safety JSON payload instead of a formal Markdown report.
- The payload includes `allowed: false` and the matching red-line category.

For safe formal reports, the output MUST NOT contain prohibited absolute destiny phrases, including:

- `必定`
- `注定`
- `一定会`
- `死定`

## Error Contract

Malformed chart input MUST keep stable user-facing errors:

- No Python traceback is printed for malformed user input.
- Existing invalid input paths remain non-zero.
- Interpretation failures caused by missing optional interpretation signals are represented as limitation text, not internal exceptions.
