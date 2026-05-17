# CLI Contract: 八字自动排盘层 MVP

## Command Shape

```text
mingli-engine calculate-chart --input birth-profile.json
mingli-engine calculate-chart --input -
mingli-engine calculate-report --input birth-profile.json --format markdown
mingli-engine calculate-report --input - --format markdown
```

Both commands read UTF-8 JSON from a file or stdin. Both commands write either JSON or Markdown to stdout and stable errors to stderr.

## calculate-chart Input

```json
{
  "calendar_type": "gregorian",
  "birth_date": "1992-08-18",
  "birth_time": "09:30",
  "birthplace": "上海市",
  "gender": "未指定",
  "focus_topic": "职业规划与长期学习节奏"
}
```

## calculate-chart Success Output

```json
{
  "birth_profile": {
    "calendar_type": "gregorian",
    "birth_date": "1992-08-18",
    "birth_time": "09:30",
    "birthplace": "上海市",
    "gender": "未指定",
    "focus_topic": "职业规划与长期学习节奏"
  },
  "chart_source": {
    "source_type": "auto_calculated",
    "source_note": "由本引擎调用历法库自动计算，未人工复核",
    "calendar_assumption": "公历输入，按节气边界计算年柱和月柱",
    "timezone_assumption": "中国标准时间 UTC+08:00",
    "solar_terms_assumption": "节气数据由历法库提供",
    "true_solar_time_applied": false,
    "confidence": "medium"
  },
  "pillars": [
    {
      "name": "year",
      "heavenly_stem": "壬",
      "earthly_branch": "申",
      "hidden_stems": ["庚", "壬", "戊"],
      "ten_god": "七杀",
      "element": "水金"
    },
    {
      "name": "month",
      "heavenly_stem": "戊",
      "earthly_branch": "申",
      "hidden_stems": ["庚", "壬", "戊"],
      "ten_god": "食神",
      "element": "土金"
    },
    {
      "name": "day",
      "heavenly_stem": "丙",
      "earthly_branch": "寅",
      "hidden_stems": ["甲", "丙", "戊"],
      "ten_god": "日主",
      "element": "火木"
    },
    {
      "name": "hour",
      "heavenly_stem": "癸",
      "earthly_branch": "巳",
      "hidden_stems": ["丙", "庚", "戊"],
      "ten_god": "正官",
      "element": "水火"
    }
  ],
  "day_master": "丙",
  "five_elements_summary": {
    "year": "水金",
    "month": "土金",
    "day": "火木",
    "hour": "水火"
  },
  "ten_gods_summary": "自动排盘提供十神基础信息；深入解读需结合报告语境审慎阅读。",
  "strength_assessment": "自动排盘层不直接给出旺衰定论；此处保留为候选分析入口。",
  "pattern_candidates": ["自动排盘未做完整格局定论"],
  "useful_god_candidates": ["自动排盘未做用神定论"],
  "luck_cycle_summary": "自动排盘层暂不计算大运起运；阶段内容仅作后续扩展入口。"
}
```

## calculate-chart Error Output

Unsafe focus topic:

```json
{
  "allowed": false,
  "red_line_categories": ["lifespan_or_death_timing"],
  "prohibited_phrases": [],
  "disclaimer_present": false,
  "redirect_message": "不预测寿命或死亡时间。可以改为讨论风险意识、身心节律与生活安排，帮助你用更稳妥的方式照顾当下。"
}
```

Unsupported calendar:

```text
Invalid input: calendar_type must be gregorian/solar/公历 for automatic calculation
```

Invalid date:

```text
Invalid input: birth_date must use YYYY-MM-DD
```

Invalid time:

```text
Invalid input: birth_time must use HH:MM
```

Incomplete profile:

```json
{
  "report_ready": false,
  "missing_fields": ["birth_time"],
  "clarification_questions": ["请提供出生时间。"]
}
```

## calculate-report Success Output

Markdown report containing at least:

```markdown
# 八字结构化报告
## 免责声明
## 命造卡片
## 排盘来源与假设
## 四柱与五行摘要
## 十神摘要
## 结构分析
## 性格倾向
## 优势与议题
## 阶段概览
## 行动建议
## 术语简注
## 伦理边界提醒
```

The Markdown must include the automatic-calculation source note and medium confidence.

## calculate-report Safety Block

For a red-line focus topic, command returns non-zero and writes safety JSON:

```json
{
  "allowed": false,
  "red_line_categories": ["lifespan_or_death_timing"],
  "prohibited_phrases": [],
  "disclaimer_present": true,
  "redirect_message": "不预测寿命或死亡时间。可以改为讨论风险意识、身心节律与生活安排，帮助你用更稳妥的方式照顾当下。"
}
```

## Contract Requirements

- `calculate-chart` must never emit a partial chart.
- `calculate-chart` must output exactly four pillars on success.
- `calculate-chart` must refuse red-line focus topics before emitting a full chart.
- `calculate-report` must reuse existing report safety behavior.
- Both commands must support `--input -`.
- Invalid JSON, unsupported calendar, invalid date/time, and provider failures must return non-zero without traceback.
- Automatic reports must disclose automatic source and assumptions.
