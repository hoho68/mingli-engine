# Layered Markdown Contract: 报告分层阅读体验优化

## Scope

This contract updates the Markdown report layout for existing report commands. It does not add new CLI commands, flags, input fields, output formats, or storage behavior.

Existing supported commands remain:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

## Required Markdown Order

For every complete safe report, these headings MUST appear in this order:

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

## Required Layer Content

`## 快速导读` MUST contain three to five bullet lines. The bullets MUST cover:

- chart source or confidence status
- one primary structure observation
- one boundary reminder
- the safe focus topic when available

`## 第一层：基础资料` MUST include:

- `命造卡片`
- `排盘来源与假设`
- source type
- source note
- confidence

`## 第二层：结构观察` MUST include:

- `四柱与五行摘要`
- `五行信号观察`
- `十神结构观察`
- `基础结构观察`
- day-master observation-center wording

`## 第三层：解读边界` MUST include:

- `不做格局定论`
- `不做用神定论`
- `不做大运流年判断`
- wording that avoids event or fate outcomes

`## 第四层：行动反思` MUST include:

- focus-topic wording when available
- practical reflection or review prompt language
- no promise of outcomes

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

## Compatibility Contract

The following remain unchanged:

- command names
- command flags
- JSON input shapes
- safety refusal payload shape
- missing-input validation behavior
- chart-source disclosure requirement
