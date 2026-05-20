# Report Evidence Notes Contract: 报告证据说明层

## Scope

This contract defines the new reader-facing evidence-note section for formal safe Markdown reports. It does not add new user-facing commands, flags, input schemas, chart calculations, storage behavior, export formats, or interpretation conclusions.

## Markdown Section Contract

Every formal safe Markdown report MUST include this subsection:

```text
### 观察依据
```

The subsection MUST appear inside `## 第二层：结构观察`.

Required order:

```text
## 第二层：结构观察
### 四柱与五行摘要
### 十神摘要
### 观察依据
### 结构分析
### 性格倾向
```

The section MUST contain concise reader-facing lines that cover:

- `来源依据`
- `四柱依据`
- `五行依据`
- `十神依据`
- `行动依据`

The section SHOULD preserve these meanings:

- Source basis: report observations start from chart source and assumptions, not unsupported certainty.
- Four-pillar basis: year, month, day, and hour pillars provide structure positions and combinations.
- Five-element basis: visible, hidden-stem, and total signals are used for distribution observation.
- Ten-god basis: ten-god relationships are relationship signals across pillar positions.
- Action basis: action reflection converts observable signals into review prompts and does not predict outcomes.

## Source-Specific Compatibility

Safe automatic-chart reports MUST still include reader-facing automatic source wording such as:

```text
系统自动排盘
```

Safe external-verified reports MUST still include reader-facing external source wording such as:

```text
外部排盘已核对
```

Safe external-verified reports MUST NOT be mislabeled as automatic chart output.

## Safety Contract

The evidence-note section MUST NOT include selected raw labels:

- `auto_calculated`
- `external_verified`
- `medium`
- `gregorian`

The evidence-note section MUST NOT include selected absolute destiny phrases:

- `必定`
- `注定`
- `一定会`
- `死定`

The evidence-note section MUST NOT add:

- auspiciousness claims
- useful-god verdicts
- strength verdicts
- luck-cycle judgments
- real-world event predictions
- professional medical, legal, psychological, or investment advice

Unsafe red-line report requests MUST continue to return safety JSON and MUST NOT generate a formal Markdown report with `### 观察依据`.

## Regression Contract

Every `safe_markdown` case listed in `examples/report-regression-cases.json` MUST exercise the evidence-note section through the existing CLI command and `--format markdown`.

Regression validation MUST verify:

- the section exists
- the section appears in the required order
- all five evidence basis meanings are visible
- selected raw labels and absolute destiny phrases remain absent
- existing safety JSON cases still return safety JSON

## Compatibility

Users should not need to learn any new command or flag. Existing report-generation commands continue to work:

```powershell
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```
