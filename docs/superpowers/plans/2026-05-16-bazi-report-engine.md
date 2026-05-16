# 八字知识与报告引擎 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Python knowledge and report engine that validates八字 inputs, accepts verified chart data, applies safety review, and renders a structured Markdown report.

**Architecture:** Use a small Python package with separated modules for data models, intake validation, safety review, report assembly, Markdown rendering, and CLI I/O. Keep automatic排盘 out of MVP; chart provenance is explicit through `ChartSource`.

**Tech Stack:** Python 3.12+, standard library dataclasses/enums/json/argparse, pytest.

---

## Files

- Create: `pyproject.toml`
- Create: `src/mingli_engine/__init__.py`
- Create: `src/mingli_engine/models.py`
- Create: `src/mingli_engine/validation.py`
- Create: `src/mingli_engine/safety.py`
- Create: `src/mingli_engine/report_schema.py`
- Create: `src/mingli_engine/markdown.py`
- Create: `src/mingli_engine/cli.py`
- Create: `tests/unit/test_birth_profile_validation.py`
- Create: `tests/unit/test_report_schema.py`
- Create: `tests/unit/test_markdown_renderer.py`
- Create: `tests/safety/test_red_lines_and_language.py`
- Create: `tests/contract/test_cli_json_contract.py`
- Create: `tests/integration/test_generate_markdown_report.py`
- Create: `examples/birth-profile.complete.json`
- Create: `examples/bazi-chart.external-verified.json`
- Create: `examples/red-line.lifespan.json`

### Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `src/mingli_engine/__init__.py`

- [ ] **Step 1: Write package metadata**

```toml
[project]
name = "mingli-engine"
version = "0.1.0"
description = "Local bazi knowledge and markdown report engine"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
mingli-engine = "mingli_engine.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Add package init**

```python
"""Bazi knowledge and report engine."""

__all__ = [
    "models",
    "validation",
    "safety",
    "report_schema",
    "markdown",
]
```

- [ ] **Step 3: Run scaffold check**

Run: `python -m pytest`

Expected: FAIL or no tests collected, because tests are not written yet.

- [ ] **Step 4: Commit scaffold**

Run: `git add pyproject.toml src/mingli_engine/__init__.py && git commit -m "chore: scaffold mingli engine package"`

### Task 2: Birth Profile Validation

**Files:**
- Create: `src/mingli_engine/models.py`
- Create: `src/mingli_engine/validation.py`
- Test: `tests/unit/test_birth_profile_validation.py`

- [ ] **Step 1: Write failing tests**

```python
from mingli_engine.models import BirthProfile
from mingli_engine.validation import validate_birth_profile


def test_complete_birth_profile_is_report_ready():
    profile = BirthProfile(
        calendar_type="gregorian",
        birth_date="1990-05-01",
        birth_time="10:15",
        birthplace="山西省太原市",
        gender="female",
        focus_topic="整体与事业",
    )

    result = validate_birth_profile(profile)

    assert result.report_ready is True
    assert result.missing_fields == []
    assert result.clarification_questions == []


def test_missing_birth_time_and_place_blocks_full_report():
    profile = BirthProfile(
        calendar_type="gregorian",
        birth_date="1990-05-01",
        birth_time="",
        birthplace="",
        gender="female",
        focus_topic="整体与事业",
    )

    result = validate_birth_profile(profile)

    assert result.report_ready is False
    assert result.missing_fields == ["birth_time", "birthplace"]
    assert "出生时间" in result.clarification_questions[0]
    assert "出生地" in result.clarification_questions[1]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/unit/test_birth_profile_validation.py -v`

Expected: FAIL with import errors or missing implementation.

- [ ] **Step 3: Implement minimal models and validation**

```python
# src/mingli_engine/models.py
from dataclasses import dataclass, field


@dataclass(frozen=True)
class BirthProfile:
    calendar_type: str
    birth_date: str
    birth_time: str
    birthplace: str
    gender: str
    focus_topic: str


@dataclass(frozen=True)
class IntakeValidationResult:
    report_ready: bool
    missing_fields: list[str] = field(default_factory=list)
    clarification_questions: list[str] = field(default_factory=list)
```

```python
# src/mingli_engine/validation.py
from mingli_engine.models import BirthProfile, IntakeValidationResult


_FIELD_QUESTIONS = {
    "calendar_type": "请说明出生日期是公历还是农历。",
    "birth_date": "请补充出生年月日。",
    "birth_time": "请补充出生时间，若只知道时辰也可以说明。",
    "birthplace": "请补充出生地，至少到城市。",
    "gender": "请补充性别，用于判断大运顺逆等规则。",
    "focus_topic": "请说明本次主要关注主题。",
}


def validate_birth_profile(profile: BirthProfile) -> IntakeValidationResult:
    values = {
        "calendar_type": profile.calendar_type,
        "birth_date": profile.birth_date,
        "birth_time": profile.birth_time,
        "birthplace": profile.birthplace,
        "gender": profile.gender,
        "focus_topic": profile.focus_topic,
    }
    missing = [field for field, value in values.items() if not str(value).strip()]
    questions = [_FIELD_QUESTIONS[field] for field in missing]
    return IntakeValidationResult(
        report_ready=not missing,
        missing_fields=missing,
        clarification_questions=questions,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_birth_profile_validation.py -v`

Expected: PASS.

- [ ] **Step 5: Commit validation slice**

Run: `git add src/mingli_engine/models.py src/mingli_engine/validation.py tests/unit/test_birth_profile_validation.py && git commit -m "feat: validate bazi birth profile intake"`

### Task 3: Safety Review

**Files:**
- Modify: `src/mingli_engine/models.py`
- Create: `src/mingli_engine/safety.py`
- Test: `tests/safety/test_red_lines_and_language.py`

- [ ] **Step 1: Write failing safety tests**

```python
from mingli_engine.safety import safety_check


def test_lifespan_question_is_blocked_with_redirect():
    result = safety_check("我什么时候会死？")

    assert result.allowed is False
    assert result.red_line_categories == ["lifespan_or_death_timing"]
    assert "不预测寿命或死亡时间" in result.redirect_message


def test_absolute_language_is_detected():
    result = safety_check("你今年一定会破财，这是注定的。")

    assert result.allowed is False
    assert result.prohibited_phrases == ["注定", "一定会"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/safety/test_red_lines_and_language.py -v`

Expected: FAIL with missing `safety_check` or model.

- [ ] **Step 3: Add model and safety implementation**

```python
# Add to src/mingli_engine/models.py
@dataclass(frozen=True)
class SafetyReviewResult:
    allowed: bool
    red_line_categories: list[str] = field(default_factory=list)
    prohibited_phrases: list[str] = field(default_factory=list)
    disclaimer_present: bool = False
    redirect_message: str = ""
```

```python
# src/mingli_engine/safety.py
from mingli_engine.models import SafetyReviewResult


PROHIBITED_PHRASES = ["必定", "注定", "一定会", "死定"]

RED_LINE_PATTERNS = [
    ("lifespan_or_death_timing", ["什么时候会死", "能活到几岁", "寿命", "死期"]),
    ("major_disaster_prediction", ["车祸", "大灾", "重病"]),
    ("deterministic_marriage_matching", ["注定结婚", "能不能结婚", "命中注定在一起"]),
    ("professional_advice", ["诊断", "官司会赢", "投资建议"]),
    ("paid_remedy", ["化解收费", "买法器", "做法事"]),
]


REDIRECTS = {
    "lifespan_or_death_timing": "命理报告不预测寿命或死亡时间。可以改为讨论当前阶段的身心节律、风险意识和可行动的生活安排。",
    "major_disaster_prediction": "命理报告不预测具体重大灾祸。可以改为讨论风险意识和稳妥安排。",
    "deterministic_marriage_matching": "命理报告不做婚配定论。可以改为讨论你自己的关系模式和当前阶段。",
    "professional_advice": "命理报告不能替代医疗、法律、心理或投资专业建议。",
    "paid_remedy": "本项目不提供付费化解、法事或物品销售建议。",
}


def safety_check(text: str, *, disclaimer_present: bool = False) -> SafetyReviewResult:
    categories = [
        category
        for category, patterns in RED_LINE_PATTERNS
        if any(pattern in text for pattern in patterns)
    ]
    phrases = [phrase for phrase in PROHIBITED_PHRASES if phrase in text]
    allowed = not categories and not phrases
    redirect = REDIRECTS.get(categories[0], "") if categories else ""
    return SafetyReviewResult(
        allowed=allowed,
        red_line_categories=categories,
        prohibited_phrases=phrases,
        disclaimer_present=disclaimer_present,
        redirect_message=redirect,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/safety/test_red_lines_and_language.py -v`

Expected: PASS.

- [ ] **Step 5: Commit safety slice**

Run: `git add src/mingli_engine/models.py src/mingli_engine/safety.py tests/safety/test_red_lines_and_language.py && git commit -m "feat: enforce mingli safety review"`

### Task 4: Report Schema and Markdown Rendering

**Files:**
- Modify: `src/mingli_engine/models.py`
- Create: `src/mingli_engine/report_schema.py`
- Create: `src/mingli_engine/markdown.py`
- Test: `tests/unit/test_report_schema.py`
- Test: `tests/unit/test_markdown_renderer.py`

- [ ] **Step 1: Write failing report tests**

```python
from mingli_engine.markdown import render_markdown_report
from mingli_engine.report_schema import build_report


def test_report_requires_all_sections(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    assert report.disclaimer
    assert report.chart_card
    assert report.assumptions
    assert report.action_suggestions
    assert report.safety_review.allowed is True


def test_markdown_contains_required_headings(sample_bazi_chart):
    report = build_report(sample_bazi_chart)
    markdown = render_markdown_report(report)

    for heading in [
        "## 免责声明",
        "## 命造卡片",
        "## 排盘来源与假设",
        "## 四柱与五行摘要",
        "## 行动建议",
        "## 伦理边界提醒",
    ]:
        assert heading in markdown
```

- [ ] **Step 2: Add a `sample_bazi_chart` fixture**

Create `tests/conftest.py`:

```python
import pytest

from mingli_engine.models import BaziChart, BirthProfile, ChartSource, Pillar


@pytest.fixture
def sample_bazi_chart():
    return BaziChart(
        birth_profile=BirthProfile(
            calendar_type="gregorian",
            birth_date="1990-05-01",
            birth_time="10:15",
            birthplace="山西省太原市",
            gender="female",
            focus_topic="整体与事业",
        ),
        chart_source=ChartSource(
            source_type="external_verified",
            source_note="用户提供并确认的四柱排盘结果",
            calendar_assumption="公历日期，按节气定月柱",
            timezone_assumption="中国标准时间 UTC+08:00",
            solar_terms_assumption="以节气作为年柱和月柱边界",
            true_solar_time_applied=False,
            confidence="medium",
        ),
        pillars=[
            Pillar("year", "庚", "午", ["丁", "己"], "示例", "金"),
            Pillar("month", "庚", "辰", ["戊", "乙", "癸"], "示例", "金"),
            Pillar("day", "丙", "寅", ["甲", "丙", "戊"], "日主", "火"),
            Pillar("hour", "癸", "巳", ["丙", "戊", "庚"], "示例", "水"),
        ],
        day_master="丙",
        five_elements_summary={"wood": "medium", "fire": "medium", "earth": "medium", "metal": "strong", "water": "present"},
        ten_gods_summary="示例十神摘要。",
        strength_assessment="日主强弱待复核。",
        pattern_candidates=["示例格局候选"],
        useful_god_candidates=["示例用神候选"],
        luck_cycle_summary="示例大运流年摘要。",
    )
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py -v`

Expected: FAIL with missing chart/report models.

- [ ] **Step 4: Implement chart and report models**

Add this code to `src/mingli_engine/models.py`:

```python
@dataclass(frozen=True)
class ChartSource:
    source_type: str
    source_note: str
    calendar_assumption: str
    timezone_assumption: str
    solar_terms_assumption: str
    true_solar_time_applied: bool | None
    confidence: str


@dataclass(frozen=True)
class Pillar:
    name: str
    heavenly_stem: str
    earthly_branch: str
    hidden_stems: list[str]
    ten_god: str
    element: str


@dataclass(frozen=True)
class BaziChart:
    birth_profile: BirthProfile
    chart_source: ChartSource
    pillars: list[Pillar]
    day_master: str
    five_elements_summary: dict[str, str]
    ten_gods_summary: str
    strength_assessment: str
    pattern_candidates: list[str]
    useful_god_candidates: list[str]
    luck_cycle_summary: str


@dataclass(frozen=True)
class Report:
    title: str
    disclaimer: str
    chart_card: str
    assumptions: str
    four_pillars_summary: str
    five_elements_summary: str
    ten_gods_summary: str
    structure_analysis: str
    personality_tendencies: str
    strengths_and_issues: str
    phase_overview: str
    action_suggestions: str
    glossary: str
    ethics_reminder: str
    safety_review: SafetyReviewResult
```

Create `src/mingli_engine/report_schema.py`:

```python
from mingli_engine.models import BaziChart, Report
from mingli_engine.safety import safety_check


DISCLAIMER = (
    "本报告基于传统命理知识作结构化解读，用于文化研究与自我反思，"
    "不构成科学预测、医疗、法律、心理或投资建议。重大决定仍由你自主判断。"
)


def build_report(chart: BaziChart) -> Report:
    pillar_lines = [
        f"{pillar.name}: {pillar.heavenly_stem}{pillar.earthly_branch}"
        for pillar in chart.pillars
    ]
    assumptions = "\n".join(
        [
            f"来源: {chart.chart_source.source_note}",
            f"历法: {chart.chart_source.calendar_assumption}",
            f"时区: {chart.chart_source.timezone_assumption}",
            f"节气: {chart.chart_source.solar_terms_assumption}",
            f"真太阳时: {chart.chart_source.true_solar_time_applied}",
            f"置信度: {chart.chart_source.confidence}",
        ]
    )
    action = "先把本报告作为结构化自我观察清单，选择一条最容易执行的建议实践两周，再回看反馈。"
    body_for_review = "\n".join([DISCLAIMER, assumptions, action])
    review = safety_check(body_for_review, disclaimer_present=True)
    return Report(
        title="八字结构化报告",
        disclaimer=DISCLAIMER,
        chart_card=(
            f"{chart.birth_profile.birth_date} {chart.birth_profile.birth_time} | "
            f"{chart.birth_profile.birthplace} | 关注: {chart.birth_profile.focus_topic}"
        ),
        assumptions=assumptions,
        four_pillars_summary="\n".join(pillar_lines),
        five_elements_summary=", ".join(f"{key}: {value}" for key, value in chart.five_elements_summary.items()),
        ten_gods_summary=chart.ten_gods_summary,
        structure_analysis=(
            f"日主 {chart.day_master}。{chart.strength_assessment} "
            f"格局候选: {'、'.join(chart.pattern_candidates)}。"
            f"用神候选: {'、'.join(chart.useful_god_candidates)}。"
        ),
        personality_tendencies="此处以结构倾向表达性格侧面，避免把倾向说成定论。",
        strengths_and_issues="优势与议题需结合五行、十神和格局候选交叉观察。",
        phase_overview=chart.luck_cycle_summary,
        action_suggestions=action,
        glossary="日主: 以日干作为观察中心。用神: 用来平衡结构的候选方向。",
        ethics_reminder="本项目不预测寿命、死亡时间、重大灾祸，不做婚配定论，不替代专业建议。",
        safety_review=review,
    )
```

Create `src/mingli_engine/markdown.py`:

```python
from mingli_engine.models import Report


def render_markdown_report(report: Report) -> str:
    sections = [
        f"# {report.title}",
        "## 免责声明",
        report.disclaimer,
        "## 命造卡片",
        report.chart_card,
        "## 排盘来源与假设",
        report.assumptions,
        "## 四柱与五行摘要",
        report.four_pillars_summary,
        report.five_elements_summary,
        "## 十神摘要",
        report.ten_gods_summary,
        "## 结构分析",
        report.structure_analysis,
        "## 性格倾向",
        report.personality_tendencies,
        "## 优势与议题",
        report.strengths_and_issues,
        "## 阶段概览",
        report.phase_overview,
        "## 行动建议",
        report.action_suggestions,
        "## 术语简注",
        report.glossary,
        "## 伦理边界提醒",
        report.ethics_reminder,
    ]
    return "\n\n".join(sections).strip() + "\n"
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py -v`

Expected: PASS.

- [ ] **Step 6: Commit report slice**

Run: `git add src/mingli_engine/models.py src/mingli_engine/report_schema.py src/mingli_engine/markdown.py tests/conftest.py tests/unit/test_report_schema.py tests/unit/test_markdown_renderer.py && git commit -m "feat: render structured bazi markdown report"`

### Task 5: CLI Contract

**Files:**
- Create: `src/mingli_engine/cli.py`
- Test: `tests/contract/test_cli_json_contract.py`
- Test: `tests/integration/test_generate_markdown_report.py`

- [ ] **Step 1: Write failing contract tests**

```python
import json
import subprocess
import sys


def test_validate_intake_cli_accepts_complete_profile(tmp_path):
    payload = {
        "calendar_type": "gregorian",
        "birth_date": "1990-05-01",
        "birth_time": "10:15",
        "birthplace": "山西省太原市",
        "gender": "female",
        "focus_topic": "整体与事业",
    }
    input_path = tmp_path / "birth-profile.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "mingli_engine.cli", "validate-intake", "--input", str(input_path)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert json.loads(result.stdout)["report_ready"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/contract/test_cli_json_contract.py -v`

Expected: FAIL with missing CLI implementation.

- [ ] **Step 3: Implement CLI**

Create `src/mingli_engine/cli.py`:

```python
import argparse
import json
from pathlib import Path
from typing import Any

from mingli_engine.markdown import render_markdown_report
from mingli_engine.models import BaziChart, BirthProfile, ChartSource, Pillar
from mingli_engine.report_schema import build_report
from mingli_engine.safety import safety_check
from mingli_engine.validation import validate_birth_profile


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _birth_profile(data: dict[str, Any]) -> BirthProfile:
    return BirthProfile(
        calendar_type=data.get("calendar_type", ""),
        birth_date=data.get("birth_date", ""),
        birth_time=data.get("birth_time", ""),
        birthplace=data.get("birthplace", ""),
        gender=data.get("gender", ""),
        focus_topic=data.get("focus_topic", ""),
    )


def _chart(data: dict[str, Any]) -> BaziChart:
    source = data["chart_source"]
    return BaziChart(
        birth_profile=_birth_profile(data["birth_profile"]),
        chart_source=ChartSource(
            source_type=source["source_type"],
            source_note=source["source_note"],
            calendar_assumption=source["calendar_assumption"],
            timezone_assumption=source["timezone_assumption"],
            solar_terms_assumption=source["solar_terms_assumption"],
            true_solar_time_applied=source["true_solar_time_applied"],
            confidence=source["confidence"],
        ),
        pillars=[
            Pillar(
                item["name"],
                item["heavenly_stem"],
                item["earthly_branch"],
                item["hidden_stems"],
                item["ten_god"],
                item["element"],
            )
            for item in data["pillars"]
        ],
        day_master=data["day_master"],
        five_elements_summary=data["five_elements_summary"],
        ten_gods_summary=data["ten_gods_summary"],
        strength_assessment=data["strength_assessment"],
        pattern_candidates=data["pattern_candidates"],
        useful_god_candidates=data["useful_god_candidates"],
        luck_cycle_summary=data["luck_cycle_summary"],
    )


def _print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="mingli-engine")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-intake")
    validate.add_argument("--input", required=True)

    safety = sub.add_parser("safety-check")
    safety.add_argument("--input", required=True)

    report = sub.add_parser("generate-report")
    report.add_argument("--input", required=True)
    report.add_argument("--format", choices=["markdown"], default="markdown")

    args = parser.parse_args()

    if args.command == "validate-intake":
        result = validate_birth_profile(_birth_profile(_load_json(args.input)))
        _print_json(
            {
                "report_ready": result.report_ready,
                "missing_fields": result.missing_fields,
                "clarification_questions": result.clarification_questions,
            }
        )
        return

    if args.command == "safety-check":
        payload = _load_json(args.input)
        result = safety_check(payload.get("text", ""))
        _print_json(
            {
                "allowed": result.allowed,
                "red_line_categories": result.red_line_categories,
                "prohibited_phrases": result.prohibited_phrases,
                "disclaimer_present": result.disclaimer_present,
                "redirect_message": result.redirect_message,
            }
        )
        return

    if args.command == "generate-report":
        chart = _chart(_load_json(args.input))
        intake = validate_birth_profile(chart.birth_profile)
        if not intake.report_ready:
            _print_json(
                {
                    "report_ready": False,
                    "missing_fields": intake.missing_fields,
                    "clarification_questions": intake.clarification_questions,
                }
            )
            raise SystemExit(2)
        generated = build_report(chart)
        if not generated.safety_review.allowed:
            _print_json(
                {
                    "allowed": False,
                    "red_line_categories": generated.safety_review.red_line_categories,
                    "prohibited_phrases": generated.safety_review.prohibited_phrases,
                    "redirect_message": generated.safety_review.redirect_message,
                }
            )
            raise SystemExit(3)
        print(render_markdown_report(generated), end="")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Add example JSON files**

Create `examples/birth-profile.complete.json`:

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

Create `examples/red-line.lifespan.json`:

```json
{
  "text": "我什么时候会死？",
  "context": "user_request"
}
```

Create `examples/bazi-chart.external-verified.json`:

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

- [ ] **Step 5: Run contract and integration tests**

Run: `python -m pytest tests/contract tests/integration -v`

Expected: PASS.

- [ ] **Step 6: Commit CLI slice**

Run: `git add src/mingli_engine/cli.py examples/ tests/contract/test_cli_json_contract.py tests/integration/test_generate_markdown_report.py && git commit -m "feat: add mingli engine cli contract"`

### Task 6: Full Verification

**Files:**
- Modify only if verification exposes gaps.

- [ ] **Step 1: Run complete test suite**

Run: `python -m pytest`

Expected: all tests pass.

- [ ] **Step 2: Run safety spot checks**

Run: `python -m mingli_engine.cli safety-check --input examples/red-line.lifespan.json`

Expected: blocked output with `allowed: false`.

- [ ] **Step 3: Run report generation spot check**

Run: `python -m mingli_engine.cli generate-report --input examples/bazi-chart.external-verified.json --format markdown`

Expected: Markdown contains disclaimer, assumptions, required sections, and no prohibited absolute phrases.

- [ ] **Step 4: Commit verification fixes**

Run: `git status --short`

Expected: clean, or commit any verification fixes with `git commit -m "test: verify bazi report engine mvp"`.

## Self-Review

- Spec coverage: US1 maps to Task 2 and Task 5; US2 maps to Task 4 and Task 5; US3 maps to Task 3 and Task 6.
- Placeholder scan: no unresolved placeholders remain.
- Type consistency: model names match `specs/001-bazi-report-engine/data-model.md`.
