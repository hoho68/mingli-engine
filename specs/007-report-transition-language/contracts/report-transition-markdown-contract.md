# Report Transition Markdown Contract: 报告层间衔接语优化

## Scope

This contract updates wording in the existing Markdown report. It does not add new commands, flags, input fields, output formats, storage behavior, chart calculations, headings, or interpretation conclusions.

Supported commands remain unchanged:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

## Required Heading Compatibility

Successful complete Markdown reports MUST keep the existing heading order:

```text
# 八字结构化报告
## 免责声明
## 快速导读
## 第一层：基础资料
## 第二层：结构观察
## 第三层：解读边界
## 第四层：行动反思
## 术语简注
## 伦理边界提醒
```

## Required Transition Wording

Successful complete Markdown reports MUST include concise wording that communicates these meanings:

- Reading path: first check source data and assumptions, then read structure observations, then review boundaries, then turn observations into reflection prompts.
- Source basis: birth data, source type, calendar, timezone, solar terms, and true-solar-time status are basis and assumptions, not conclusions.
- Structure boundary: structure observations are clues or materials, not final judgments.
- Boundary action bridge: interpretation boundaries prevent overclaiming and lead into action reflection.
- Action reflection: action suggestions are review prompts or organizing directions, not promised outcomes.

The exact text may evolve, but each meaning must be visible in final Markdown.

## Compatibility With Earlier Features

Successful complete Markdown reports MUST continue to include feature 005 reader-facing labels for known values:

```text
系统自动排盘
外部排盘已核对
中等可信度
公历
年柱
月柱
日柱
时柱
```

Successful complete Markdown reports MUST continue to include feature 006 structure observation wording:

```text
五行数量可以先作为结构观察材料来看
十神关系可以先按四个柱位理解为结构线索
基础结构可以先看分布是否集中
```

## Safety Contract

Unsafe focus topics keep existing behavior:

- CLI returns exit code `3`.
- CLI outputs safety JSON instead of Markdown.
- The payload includes `allowed: false` and the matching red-line category.

Safe formal reports MUST NOT include prohibited absolute destiny phrases:

- `必定`
- `注定`
- `一定会`
- `死定`

Transition wording MUST NOT introduce pattern verdicts, useful-god verdicts, strength verdicts, luck-cycle judgments, auspiciousness claims, or real-world outcome predictions.
