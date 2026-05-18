# Structure Observation Markdown Contract: 第二层结构观察表达优化

## Scope

This contract updates wording in the existing Markdown report. It does not add commands, flags, input fields, output formats, storage behavior, chart calculations, or new interpretation conclusions.

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

## Required Structure Layer Behavior

`## 第二层：结构观察` MUST continue to include:

- day-master observation text
- five-element observation text
- ten-god observation text
- basic structure observation text

The five-element observation text MUST:

- show direct counts
- show hidden-stem counts
- show total counts
- explain that counts are observation material
- avoid presenting counts as a full strength model or final conclusion

The ten-god observation text MUST:

- show readable pillar ten-god relationships when available
- describe those relationships as structural clues
- disclose missing or unknown ten-god positions without guessing

The basic structure observation text MUST:

- describe distribution, concentration, and presence/absence in natural report prose
- avoid internal-sounding phrasing
- avoid deterministic or predictive conclusions

## Prohibited System-Like Phrases

Successful complete Markdown reports MUST NOT include these phrases in reader-facing body text:

```text
五行信号观察：明面信号为
这些数量用于观察结构分布
基础结构观察：五行分布先看有无、多少与集中度。
```

## Compatibility With Feature 005

Successful complete Markdown reports MUST continue to avoid selected raw machine labels in reader-facing body text:

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
