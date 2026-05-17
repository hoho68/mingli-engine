# 八字自动排盘层 MVP 设计

**日期**: 2026-05-17

## 背景

当前项目已经完成第一阶段：输入已验证的 `BaziChart`，可以生成结构化 Markdown 命理报告，并内置伦理红线、绝对化语言检查、CLI 合同和测试套件。

下一阶段要补上“自动排盘层”：用户不再必须手动提供四柱，而是输入公历出生资料，由系统自动计算年柱、月柱、日柱、时柱，再复用现有报告引擎。

## 用户已确认的关键选择

- 第一版只支持公历输入。
- 第一版按中国标准时间 `UTC+08:00` 处理，不做海外时区。
- 第一版不做真太阳时。
- 同时提供单独排盘 JSON 和一键生成报告两条能力。
- 使用成熟历法库，不手写核心干支/节气算法。
- 自动排盘结果采用保守可信度：可以直接生成报告，但必须明确“由本引擎自动计算，未人工复核”。

## 方案比较

### 方案 A: 用 `lunar_python` 做历法适配器

`lunar_python` 是纯 Python 历法库，PyPI 当前版本为 `1.4.8`，发布时间为 2025-11-05。项目 README 说明它支持公历、农历、干支、节气、八字、五行、十神等能力，许可证为 MIT。

优点：

- 纯 Python，适合 Windows 本地开发环境。
- 依赖安装简单，减少编译和平台问题。
- 能覆盖本阶段需要的公历转干支与八字基础能力。
- 以后可以被包在项目自己的 adapter 后面，避免第三方 API 泄漏到业务层。

缺点：

- 仍需要用固定样例验证库输出是否符合本项目采用的规则。
- 库升级可能改变细节，需要锁版本和回归测试。

### 方案 B: 用 `sxtwl` 等底层历法库

优点是命理/节气能力较强，适合更底层的历法控制。缺点是平台和安装复杂度更高，第一版容易被环境问题拖慢。

### 方案 C: 自己手写干支算法

优点是完全可控。缺点是节气换月、立春换年、日柱推算等细节很容易出错，不适合作为当前 MVP 的第一步。

## 决策

采用方案 A：用 `lunar_python`，但只在 `calendar_provider` 适配层直接调用第三方库。

项目内部其他模块只依赖自己的 `BaziChart`、`ChartSource`、`Pillar` 等模型。这样以后如果换库、补真太阳时、加入农历输入，改动范围会集中在排盘层。

参考资料：

- PyPI: https://pypi.org/project/lunar_python/
- GitHub: https://github.com/6tail/lunar-python

## 功能范围

### 新增能力 1: 自动排盘 JSON

新增 CLI 命令：

```text
mingli-engine calculate-chart --input birth-profile.json
```

输入仍使用现有 `BirthProfile` 字段：

- `calendar_type`
- `birth_date`
- `birth_time`
- `birthplace`
- `gender`
- `focus_topic`

第一版要求：

- `calendar_type` 必须是公历相关值，例如 `gregorian` 或 `公历`。
- `birth_date` 使用 `YYYY-MM-DD`。
- `birth_time` 使用 `HH:MM`。
- `birthplace` 第一版只用于报告展示和假设说明，不做经纬度计算。

输出为完整 `BaziChart` JSON，包含：

- `birth_profile`
- `chart_source`
- 四个 `pillars`
- `day_master`
- `five_elements_summary`
- `ten_gods_summary`
- `strength_assessment`
- `pattern_candidates`
- `useful_god_candidates`
- `luck_cycle_summary`

其中 `strength_assessment`、`pattern_candidates`、`useful_god_candidates`、`luck_cycle_summary` 第一版可以是保守摘要，明确说明“自动排盘层只提供基础结构，深入格局判断仍为候选”。

### 新增能力 2: 自动排盘并生成报告

新增 CLI 命令：

```text
mingli-engine calculate-report --input birth-profile.json --format markdown
```

流程：

1. 校验出生资料。
2. 检查 `focus_topic` 是否触发安全红线。
3. 调用自动排盘层生成 `BaziChart`。
4. 调用现有 `build_report`。
5. 调用现有 Markdown renderer 输出报告。

如果输入不完整，继续沿用当前 CLI 风格：输出 JSON 错误信息并返回非 0。  
如果安全审查失败，输出 `SafetyReviewResult` JSON 并返回非 0。  
如果第三方历法库无法计算，输出稳定 `Invalid input` 或 `Calculation error`，不得输出 Python traceback。

## ChartSource 规则

自动排盘结果的 `chart_source` 固定采用保守透明说明：

- `source_type`: `auto_calculated`
- `source_note`: `由本引擎调用 lunar_python 自动计算，未人工复核`
- `calendar_assumption`: `公历输入，按节气边界计算年柱和月柱`
- `timezone_assumption`: `中国标准时间 UTC+08:00`
- `solar_terms_assumption`: `节气数据由 lunar_python 提供`
- `true_solar_time_applied`: `False`
- `confidence`: `medium`

报告中必须展示这些假设，避免让自动计算结果看起来像人工复核后的高可信结论。

## 模块设计

### `calendar_provider.py`

职责：隔离第三方库。

输入：Python `datetime` 或拆分后的年月日时分。  
输出：一个内部中间对象，至少包含四柱干支、日主、可能的十神/五行信息。

这个模块是唯一直接 import `lunar_python` 的地方。

### `chart_calculator.py`

职责：把 `BirthProfile` 转成现有 `BaziChart`。

它负责：

- 校验公历日期和时间格式。
- 调用 `calendar_provider`。
- 组装 `ChartSource`。
- 组装四个 `Pillar`。
- 生成五行摘要、十神摘要和保守候选说明。

### `cli.py`

新增两个命令：

- `calculate-chart`
- `calculate-report`

它们复用现有 `_read_json`、错误处理、`validate_birth_profile`、`safety_check`、`build_report` 和 `render_markdown_report`。

## 数据流

```text
BirthProfile JSON
  -> validate_birth_profile
  -> safety_check(focus_topic)
  -> calculate_bazi_chart
  -> BaziChart with ChartSource(auto_calculated)
  -> build_report
  -> render_markdown_report
```

单独排盘命令在 `calculate_bazi_chart` 后停止并输出 JSON。  
一键报告命令继续走现有报告链路。

## 错误处理

必须稳定处理以下情况：

- 缺少出生日期、出生时间、出生地、关注主题等必填字段。
- `calendar_type` 不是公历。
- 日期格式不是 `YYYY-MM-DD`。
- 时间格式不是 `HH:MM`。
- 时间超出范围，例如 `25:99`。
- 第三方库抛出异常。
- 用户关注主题触发安全红线。

所有 CLI 错误都应输出稳定信息，不应显示 traceback。

## 测试计划

### Unit tests

- 公历日期和时间格式校验。
- `calendar_provider` 对固定样例返回稳定四柱。
- `chart_calculator` 能生成完整 `BaziChart`，且 `pillars` 数量为 4。
- `ChartSource` 使用 `auto_calculated` 和 `confidence=medium`。

### Contract tests

- `calculate-chart` 输出合法 JSON。
- `calculate-report` 输出完整 Markdown，并包含自动计算来源说明。
- `calculate-report` 在红线主题下返回安全审查 JSON。
- 非公历输入返回稳定错误。
- 无效日期/时间返回稳定错误。

### Regression sample

第一版至少放入 2 个固定样例：

1. 普通现代日期，例如 `1992-08-18 09:30`。
2. 接近节气边界但不做真太阳时的日期，用来确认来源假设和边界说明可见。

这些样例不用于宣称命理结论，只用于防止第三方库升级或适配层改动导致输出悄悄变化。

## 不做范围

第一版不做：

- 农历输入。
- 真太阳时。
- 海外时区。
- 经纬度解析。
- 多流派规则选择。
- 大运起运岁数精算。
- 自动判断完整格局、旺衰、用神定论。
- 紫微斗数或六爻。
- Web UI。

## 后续扩展

后续可以按这个顺序增强：

1. 增加农历输入。
2. 增加出生地经纬度和真太阳时选项。
3. 增加更多回归样例。
4. 增加大运起运计算。
5. 增加可解释的格局/旺衰候选规则。
6. 接入 Web 输入界面。

## 自检

- 没有未完成标记或未解释内容。
- 设计保持单一目标：自动排盘层 MVP。
- 没有把农历、真太阳时、海外时区、Web UI 混入第一版。
- 第三方库被限制在适配层，后续可替换。
- 输出可信度和来源假设保持透明。
- 所有关键行为都能转换为 Spec Kit 验收条件和测试任务。
