# Report Regression Cases Contract: 报告回归样例清单

## Scope

This contract defines a local regression case manifest and expected validation behavior. It does not add new user-facing commands, flags, input schemas, chart calculations, storage behavior, report sections, or interpretation conclusions.

## Manifest Location

The initial manifest should live at:

```text
examples/report-regression-cases.json
```

## Manifest Shape

The manifest is a JSON array of case objects.

Required fields for every case:

```json
{
  "id": "safe-auto-gregorian",
  "kind": "safe_markdown",
  "command": "calculate-report",
  "input": "examples/birth-profile.auto-gregorian.json",
  "purpose": "Guards automatic chart Markdown report structure and wording."
}
```

Supported `kind` values:

- `safe_markdown`
- `safety_json`

Supported `command` values:

- `calculate-report`
- `generate-report`

Additional required fields by kind:

- `safe_markdown` cases require `source_type`.
- `safety_json` cases require `expected_category`.

Supported `source_type` values:

- `auto_calculated`
- `external_verified`

## Required Initial Cases

The manifest MUST include at least these semantic cases:

- A safe automatic chart case using `examples/birth-profile.auto-gregorian.json`.
- A safe external verified chart case using `examples/bazi-chart.external-verified.json`.
- An unsafe red-line focus case using `examples/birth-profile.unsafe-focus.json` or an equivalent existing unsafe example.

## Safe Markdown Contract

For each `safe_markdown` case, validation MUST run the listed command with the listed input and `--format markdown`.

The output MUST:

- Exit successfully.
- Include `# 八字结构化报告`.
- Include `## 快速导读`.
- Include these headings in order:
  - `## 第一层：基础资料`
  - `## 第二层：结构观察`
  - `## 第三层：解读边界`
  - `## 第四层：行动反思`
- Include feature 006 wording:
  - `五行数量可以先作为结构观察材料来看`
  - `十神关系可以先按四个柱位理解为结构线索`
  - `基础结构可以先看分布是否集中`
- Include feature 007 wording:
  - `先核对资料与假设`
  - `结构观察提供的是线索，不是最终判断`
  - `这些边界是为了防止过度断言`
  - `行动反思只作为复盘提示`
- Avoid selected raw labels:
  - `auto_calculated`
  - `external_verified`
  - `medium`
  - `gregorian`
  - `year：`
  - `month：`
  - `day：`
  - `hour：`
- Avoid selected absolute destiny phrases:
  - `必定`
  - `注定`
  - `一定会`
  - `死定`

Source-specific checks:

- `auto_calculated` cases MUST include `系统自动排盘`.
- `external_verified` cases MUST include `外部排盘已核对` and MUST NOT include `来源类型：系统自动排盘`.

## Safety JSON Contract

For each `safety_json` case, validation MUST run the listed command with the listed input and `--format markdown`.

The output MUST:

- Exit with the existing safety refusal code.
- Parse as JSON.
- Include `allowed` as `false`.
- Include the expected red-line category.
- Not start with `# 八字结构化报告`.

## Compatibility

The manifest and regression validation MUST preserve existing report-generation commands. Users should not need a new command or flag to benefit from this guardrail.
