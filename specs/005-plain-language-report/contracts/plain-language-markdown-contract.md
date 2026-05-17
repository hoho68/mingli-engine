# Plain-Language Markdown Contract: 八字报告白话表达优化

## Scope

This contract updates wording in existing Markdown reports. It does not add new CLI commands, flags, input fields, output formats, storage behavior, chart calculations, or interpretation conclusions.

Existing supported commands remain:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

## Required Reader-Facing Labels

Successful complete Markdown reports MUST use reader-facing Chinese wording for known values:

```text
auto_calculated -> 系统自动排盘
external_verified -> 外部排盘已核对
medium -> 中等可信度
gregorian -> 公历
year -> 年柱
month -> 月柱
day -> 日柱
hour -> 时柱
```

## Prohibited Raw Labels In Formal Markdown

Successful complete Markdown reports MUST NOT expose these selected raw labels in reader-facing body text:

```text
auto_calculated
external_verified
medium
gregorian
year：
month：
day：
hour：
```

## Required Heading Compatibility

The feature 004 heading order remains unchanged:

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

## Required Source Transparency

`## 第一层：基础资料` MUST still include:

- `命造卡片`
- `排盘来源与假设`
- source type in reader-facing wording
- source note
- calendar assumption
- timezone assumption
- solar-term assumption
- true-solar-time disclosure
- confidence in reader-facing wording

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

The wording polish MUST NOT introduce pattern verdicts, useful-god verdicts, strength verdicts, luck-cycle judgments, auspiciousness claims, or real-world outcome predictions.

## Compatibility Contract

The following remain unchanged:

- command names
- command flags
- JSON input shapes
- safety refusal payload shape
- missing-input validation behavior
- report title
- disclaimer presence
- chart-source disclosure requirement
