# CLI JSON Contract: 八字知识与报告引擎 MVP

## Command Shape

The MVP exposes a local command that accepts JSON from a file or standard input and writes JSON or Markdown to standard output.

```text
mingli-engine validate-intake --input birth-profile.json
mingli-engine generate-report --input bazi-chart.json --format markdown
mingli-engine safety-check --input report-or-request.json
```

## validate-intake Input

```json
{
  "calendar_type": "gregorian",
  "birth_date": "1990-05-01",
  "birth_time": "10:15",
  "birthplace": "山西省太原市",
  "gender": "female",
  "focus_topic": "整体与事业"
}
```

## validate-intake Success Output

```json
{
  "report_ready": true,
  "missing_fields": [],
  "clarification_questions": []
}
```

## validate-intake Missing Fields Output

```json
{
  "report_ready": false,
  "missing_fields": ["birth_time", "birthplace"],
  "clarification_questions": [
    "请补充出生时间，若只知道时辰也可以说明。",
    "请补充出生地，至少到城市。"
  ]
}
```

## generate-report Input

```json
{
  "birth_profile": {
    "calendar_type": "gregorian",
    "birth_date": "1990-05-01",
    "birth_time": "10:15",
    "birthplace": "山西省太原市",
    "gender": "female",
    "focus_topic": "整体与事业"
  },
  "chart_source": {
    "source_type": "external_verified",
    "source_note": "用户提供并确认的四柱排盘结果",
    "calendar_assumption": "公历日期，按节气定月柱",
    "timezone_assumption": "中国标准时间 UTC+08:00",
    "solar_terms_assumption": "以节气作为年柱和月柱边界",
    "true_solar_time_applied": false,
    "confidence": "medium"
  },
  "pillars": [
    {
      "name": "year",
      "heavenly_stem": "庚",
      "earthly_branch": "午",
      "hidden_stems": ["丁", "己"],
      "ten_god": "示例",
      "element": "金"
    },
    {
      "name": "month",
      "heavenly_stem": "庚",
      "earthly_branch": "辰",
      "hidden_stems": ["戊", "乙", "癸"],
      "ten_god": "示例",
      "element": "金"
    },
    {
      "name": "day",
      "heavenly_stem": "丙",
      "earthly_branch": "寅",
      "hidden_stems": ["甲", "丙", "戊"],
      "ten_god": "日主",
      "element": "火"
    },
    {
      "name": "hour",
      "heavenly_stem": "癸",
      "earthly_branch": "巳",
      "hidden_stems": ["丙", "戊", "庚"],
      "ten_god": "示例",
      "element": "水"
    }
  ],
  "day_master": "丙",
  "five_elements_summary": {
    "wood": "medium",
    "fire": "medium",
    "earth": "medium",
    "metal": "strong",
    "water": "present"
  },
  "ten_gods_summary": "示例十神摘要，供报告引擎测试结构使用。",
  "strength_assessment": "日主强弱待复核，按外部排盘来源标记为中等置信。",
  "pattern_candidates": ["示例格局候选"],
  "useful_god_candidates": ["示例用神候选"],
  "luck_cycle_summary": "示例大运流年摘要，仅用于合同测试。"
}
```

## generate-report Markdown Output

The command writes Markdown containing these section headings:

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

## safety-check Input

```json
{
  "text": "我什么时候会死？",
  "context": "user_request"
}
```

## safety-check Blocked Output

```json
{
  "allowed": false,
  "red_line_categories": ["lifespan_or_death_timing"],
  "prohibited_phrases": [],
  "disclaimer_present": false,
  "redirect_message": "命理报告不预测寿命或死亡时间。可以改为讨论当前阶段的身心节律、风险意识和可行动的生活安排。"
}
```

## Contract Requirements

- Commands return a non-zero exit code when required input JSON is malformed.
- `generate-report` refuses full report generation when intake or safety review fails.
- `generate-report` never emits a formal report without a disclaimer.
- `safety-check` detects red-line categories before report rendering.
