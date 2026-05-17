# Bazi Interpretation Rules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic basic interpretation summaries to existing Bazi reports.

**Architecture:** Create a focused `interpretation.py` rules module that consumes `BaziChart` and returns structured text summaries. `report_schema.py` remains the report assembly boundary, the CLI commands stay unchanged, and existing safety review remains the final gate.

**Tech Stack:** Python 3.12+, dataclasses, existing CLI/report modules, pytest, no new runtime dependencies.

---

## File Structure

- Create: `src/mingli_engine/interpretation.py`
  - Owns five-elements counting, ten-gods placement extraction, neutral structure observations, limitation text, and reflection suggestions.
- Modify: `src/mingli_engine/__init__.py`
  - Exposes the new module name in `__all__`.
- Modify: `src/mingli_engine/report_schema.py`
  - Calls `build_basic_interpretation(chart)` and uses its output in the existing report fields.
- Create: `tests/unit/test_interpretation.py`
  - Covers the rules module directly with fixed chart objects.
- Modify: `tests/unit/test_report_schema.py`
  - Verifies built reports include richer interpretation and remain safe.
- Modify: `tests/integration/test_generate_markdown_report.py`
  - Verifies external complete chart reports include interpretation text and unchanged source disclosure.
- Modify: `tests/integration/test_calculate_report_cli.py`
  - Verifies automatically calculated reports include interpretation text and preserve safety wording.
- Modify if needed: `tests/safety/test_red_lines_and_language.py`
  - Adds generated-report assertions only if existing safety coverage does not already scan the new text.

## Task 1: Add Five-Elements Counting Rules

**Files:**
- Create: `src/mingli_engine/interpretation.py`
- Create: `tests/unit/test_interpretation.py`

- [ ] **Step 1: Write the failing unit tests**

Create `tests/unit/test_interpretation.py` with:

```python
from mingli_engine.interpretation import (
    count_element_distribution,
    build_basic_interpretation,
)
from mingli_engine.models import BaziChart, BirthProfile, ChartSource, Pillar


def make_chart(pillars: list[Pillar], day_master: str = "戊") -> BaziChart:
    return BaziChart(
        birth_profile=BirthProfile(
            calendar_type="solar",
            birth_date="1992-08-18",
            birth_time="14:30",
            birthplace="上海",
            gender="unspecified",
            focus_topic="事业发展",
        ),
        chart_source=ChartSource(
            source_type="test",
            source_note="固定测试盘",
            calendar_assumption="固定测试",
            timezone_assumption="UTC+08:00",
            solar_terms_assumption="固定测试",
            true_solar_time_applied=False,
            confidence="test",
        ),
        pillars=pillars,
        day_master=day_master,
        five_elements_summary={},
        ten_gods_summary="",
        strength_assessment="",
        pattern_candidates=[],
        useful_god_candidates=[],
        luck_cycle_summary="",
    )


def balanced_chart() -> BaziChart:
    return make_chart(
        [
            Pillar("year", "甲", "子", ["癸"], "七杀", "木水"),
            Pillar("month", "丙", "寅", ["甲", "丙", "戊"], "食神", "火木"),
            Pillar("day", "戊", "申", ["庚", "壬", "戊"], "日主", "土金"),
            Pillar("hour", "辛", "酉", ["辛"], "伤官", "金金"),
        ],
        day_master="戊",
    )


def concentrated_chart() -> BaziChart:
    return make_chart(
        [
            Pillar("year", "甲", "寅", ["甲", "丙", "戊"], "比肩", "木木"),
            Pillar("month", "乙", "卯", ["乙"], "劫财", "木木"),
            Pillar("day", "甲", "寅", ["甲", "丙", "戊"], "日主", "木木"),
            Pillar("hour", "乙", "卯", ["乙"], "劫财", "木木"),
        ],
        day_master="甲",
    )


def test_count_element_distribution_distinguishes_direct_and_hidden_signals():
    distribution = count_element_distribution(balanced_chart())

    assert distribution.direct_counts == {
        "木": 2,
        "火": 1,
        "土": 1,
        "金": 3,
        "水": 1,
    }
    assert distribution.hidden_counts == {
        "木": 1,
        "火": 1,
        "土": 2,
        "金": 2,
        "水": 2,
    }
    assert distribution.total_counts == {
        "木": 3,
        "火": 2,
        "土": 3,
        "金": 5,
        "水": 3,
    }
    assert distribution.dominant_elements == ["金"]
    assert distribution.missing_elements == []
    assert distribution.unknown_signals == []


def test_count_element_distribution_records_missing_and_concentrated_signals():
    distribution = count_element_distribution(concentrated_chart())

    assert distribution.dominant_elements == ["木"]
    assert distribution.missing_elements == ["金", "水"]
    assert distribution.total_counts["木"] == 12
    assert distribution.total_counts["金"] == 0
    assert distribution.total_counts["水"] == 0
```

- [ ] **Step 2: Run the new tests and verify they fail**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_interpretation.py -v
```

Expected: import failure because `mingli_engine.interpretation` does not exist yet.

- [ ] **Step 3: Implement element distribution data and counting**

Create `src/mingli_engine/interpretation.py` with:

```python
from dataclasses import dataclass, field

from mingli_engine.models import BaziChart


ELEMENTS = ("木", "火", "土", "金", "水")

STEM_ELEMENTS = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}

BRANCH_ELEMENTS = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}

PILLAR_DISPLAY_NAMES = {
    "year": "年柱",
    "month": "月柱",
    "day": "日柱",
    "hour": "时柱",
    "年柱": "年柱",
    "月柱": "月柱",
    "日柱": "日柱",
    "时柱": "时柱",
}


@dataclass(frozen=True)
class ElementDistribution:
    direct_counts: dict[str, int]
    hidden_counts: dict[str, int]
    total_counts: dict[str, int]
    dominant_elements: list[str]
    missing_elements: list[str]
    unknown_signals: list[str] = field(default_factory=list)


def _empty_counts() -> dict[str, int]:
    return {element: 0 for element in ELEMENTS}


def _add_signal(
    counts: dict[str, int],
    signal: str,
    mapping: dict[str, str],
    unknown_signals: list[str],
) -> None:
    element = mapping.get(signal.strip())
    if element:
        counts[element] += 1
    elif signal.strip():
        unknown_signals.append(signal)


def _dominant_elements(total_counts: dict[str, int]) -> list[str]:
    highest = max(total_counts.values())
    if highest == 0:
        return []
    return [element for element in ELEMENTS if total_counts[element] == highest]


def count_element_distribution(chart: BaziChart) -> ElementDistribution:
    direct_counts = _empty_counts()
    hidden_counts = _empty_counts()
    unknown_signals: list[str] = []

    for pillar in chart.pillars:
        _add_signal(
            direct_counts,
            pillar.heavenly_stem,
            STEM_ELEMENTS,
            unknown_signals,
        )
        _add_signal(
            direct_counts,
            pillar.earthly_branch,
            BRANCH_ELEMENTS,
            unknown_signals,
        )
        for hidden_stem in pillar.hidden_stems:
            _add_signal(hidden_counts, hidden_stem, STEM_ELEMENTS, unknown_signals)

    total_counts = {
        element: direct_counts[element] + hidden_counts[element]
        for element in ELEMENTS
    }
    return ElementDistribution(
        direct_counts=direct_counts,
        hidden_counts=hidden_counts,
        total_counts=total_counts,
        dominant_elements=_dominant_elements(total_counts),
        missing_elements=[element for element in ELEMENTS if total_counts[element] == 0],
        unknown_signals=unknown_signals,
    )
```

- [ ] **Step 4: Run Task 1 tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_interpretation.py -v
```

Expected: the two element distribution tests pass; the imported `build_basic_interpretation` still fails if Task 2 tests are already present.

- [ ] **Step 5: Commit Task 1**

Run:

```powershell
git add src\mingli_engine\interpretation.py tests\unit\test_interpretation.py
git commit -m "feat: count bazi element distribution"
```

## Task 2: Build The Basic Interpretation Summary

**Files:**
- Modify: `src/mingli_engine/interpretation.py`
- Modify: `tests/unit/test_interpretation.py`

- [ ] **Step 1: Add failing interpretation summary tests**

Append to `tests/unit/test_interpretation.py`:

```python
def test_build_basic_interpretation_explains_day_master_and_ten_gods():
    summary = build_basic_interpretation(balanced_chart())

    assert "五行信号观察" in summary.five_elements_summary
    assert "明面信号" in summary.five_elements_summary
    assert "藏干" in summary.five_elements_summary
    assert "日主戊" in summary.day_master_summary
    assert "观察中心" in summary.day_master_summary
    assert "年柱：七杀" in summary.ten_gods_summary
    assert "月柱：食神" in summary.ten_gods_summary
    assert "日柱：日主" in summary.ten_gods_summary
    assert "时柱：伤官" in summary.ten_gods_summary
    assert "基础结构观察" in "\n".join(summary.structure_observations)
    assert "不做格局定论" in "\n".join(summary.limitations)
    assert "不做用神定论" in "\n".join(summary.limitations)
    assert "不做大运流年判断" in "\n".join(summary.limitations)


def test_build_basic_interpretation_uses_neutral_language_for_missing_signals():
    summary = build_basic_interpretation(concentrated_chart())
    joined = "\n".join(
        [
            summary.five_elements_summary,
            summary.structure_observations,
            summary.focus_suggestions,
        ]
    )

    assert "金、水暂未形成可计数信号" in joined
    assert "不等于现实能力缺失" in joined
    for prohibited_phrase in ("必定", "注定", "一定会", "死定"):
        assert prohibited_phrase not in joined
```

- [ ] **Step 2: Run the tests and verify summary behavior is missing**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_interpretation.py -v
```

Expected: failures because `build_basic_interpretation` and summary dataclasses are not implemented.

- [ ] **Step 3: Implement summary dataclasses and text builders**

Append these definitions to `src/mingli_engine/interpretation.py`:

```python
@dataclass(frozen=True)
class TenGodPlacement:
    ten_god: str
    pillars: list[str]


@dataclass(frozen=True)
class BasicInterpretationSummary:
    element_distribution: ElementDistribution
    five_elements_summary: str
    day_master_summary: str
    ten_gods_summary: str
    structure_observations: str
    focus_suggestions: str
    limitations: str


def _format_counts(counts: dict[str, int]) -> str:
    return "、".join(f"{element}{counts[element]}" for element in ELEMENTS)


def _format_elements(elements: list[str]) -> str:
    return "、".join(elements) if elements else "无"


def _pillar_display_name(name: str) -> str:
    return PILLAR_DISPLAY_NAMES.get(name, name or "未知柱")


def summarize_ten_god_placements(chart: BaziChart) -> list[TenGodPlacement]:
    placements: dict[str, list[str]] = {}
    for pillar in chart.pillars:
        ten_god = pillar.ten_god.strip()
        if not ten_god:
            continue
        placements.setdefault(ten_god, []).append(_pillar_display_name(pillar.name))
    return [
        TenGodPlacement(ten_god=ten_god, pillars=pillars)
        for ten_god, pillars in placements.items()
    ]


def _five_elements_text(distribution: ElementDistribution) -> str:
    dominant = _format_elements(distribution.dominant_elements)
    missing = _format_elements(distribution.missing_elements)
    unknown = _format_elements(distribution.unknown_signals)
    return (
        "五行信号观察："
        f"明面信号为{_format_counts(distribution.direct_counts)}；"
        f"藏干支持信号为{_format_counts(distribution.hidden_counts)}；"
        f"合并可计数信号为{_format_counts(distribution.total_counts)}。"
        f"当前较集中的信号是{dominant}，暂未形成可计数信号的是{missing}。"
        "这些数字只说明本盘中可见符号的出现次数，不等于旺衰定论，"
        "也不等于现实能力缺失。"
        f"未知信号：{unknown}。"
    )


def _day_master_text(chart: BaziChart) -> str:
    day_master = chart.day_master.strip() or "未说明"
    return (
        f"日主{day_master}是这张盘的观察中心，用来承接其他天干地支与十神关系。"
        "这里把日主作为结构分析的参照点，不把它写成性格标签、命运结论或结果保证。"
    )


def _ten_gods_text(chart: BaziChart) -> str:
    placements = summarize_ten_god_placements(chart)
    if not placements:
        return "十神结构观察：当前资料未提供可用十神名称，因此只记录限制，不补推十神。"

    by_pillar = []
    repeated = []
    for placement in placements:
        pillars = "、".join(placement.pillars)
        by_pillar.append(f"{pillars}：{placement.ten_god}")
        if len(placement.pillars) > 1:
            repeated.append(f"{placement.ten_god}见于{pillars}")

    repeated_text = (
        f"重复信号：{'；'.join(repeated)}。"
        if repeated
        else "重复信号：暂无同一十神跨多柱重复。"
    )
    return (
        "十神结构观察："
        f"{'；'.join(by_pillar)}。"
        f"{repeated_text}"
        "十神用于观察关系、资源与行动风格的结构位置，不作为固定人格判断。"
    )


def _structure_text(distribution: ElementDistribution) -> str:
    dominant = _format_elements(distribution.dominant_elements)
    missing = _format_elements(distribution.missing_elements)
    return (
        "基础结构观察："
        f"本层只根据四柱天干、地支与藏干做符号分布整理。较集中的信号是{dominant}；"
        f"{missing}暂未形成可计数信号。"
        "集中或稀疏只代表观察入口，需要结合现实经验继续验证。"
    )


def _suggestion_text(chart: BaziChart, distribution: ElementDistribution) -> str:
    focus_topic = chart.birth_profile.focus_topic.strip() or "当前关注主题"
    dominant = _format_elements(distribution.dominant_elements)
    missing = _format_elements(distribution.missing_elements)
    return (
        f"围绕“{focus_topic}”，可把{dominant}相关的高频结构当作自我观察线索，"
        f"把{missing}相关的稀疏结构当作提醒问题：哪些资源、节奏或表达方式需要在现实中补充验证。"
        "建议记录事实证据、行动反馈和外部专业意见，不把单一结构信号当成决定。"
    )


def _limitations_text() -> str:
    return (
        "限制说明：当前功能只做基础结构观察，"
        "不做格局定论，不做用神定论，不做日主强弱定论，"
        "不做大运流年判断，不判断吉凶，也不预测具体事件结果。"
    )


def build_basic_interpretation(chart: BaziChart) -> BasicInterpretationSummary:
    distribution = count_element_distribution(chart)
    return BasicInterpretationSummary(
        element_distribution=distribution,
        five_elements_summary=_five_elements_text(distribution),
        day_master_summary=_day_master_text(chart),
        ten_gods_summary=_ten_gods_text(chart),
        structure_observations=_structure_text(distribution),
        focus_suggestions=_suggestion_text(chart, distribution),
        limitations=_limitations_text(),
    )
```

- [ ] **Step 4: Run Task 2 tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_interpretation.py -v
```

Expected: all interpretation unit tests pass.

- [ ] **Step 5: Commit Task 2**

Run:

```powershell
git add src\mingli_engine\interpretation.py tests\unit\test_interpretation.py
git commit -m "feat: build bazi interpretation summary"
```

## Task 3: Integrate Interpretation Into Report Schema

**Files:**
- Modify: `src/mingli_engine/__init__.py`
- Modify: `src/mingli_engine/report_schema.py`
- Modify: `tests/unit/test_report_schema.py`

- [ ] **Step 1: Add failing report schema assertions**

Append to `tests/unit/test_report_schema.py`:

```python
def test_build_report_includes_basic_interpretation_sections(sample_bazi_chart):
    report = build_report(sample_bazi_chart)
    combined = "\n".join(
        [
            report.five_elements_summary,
            report.ten_gods_summary,
            report.structure_analysis,
            report.personality_tendencies,
            report.strengths_and_issues,
            report.action_suggestions,
        ]
    )

    assert "五行信号观察" in report.five_elements_summary
    assert "明面信号" in report.five_elements_summary
    assert "藏干" in report.five_elements_summary
    assert "观察中心" in report.personality_tendencies
    assert "十神结构观察" in report.ten_gods_summary
    assert "基础结构观察" in report.structure_analysis
    assert "不做格局定论" in combined
    assert "不做用神定论" in combined
    assert "不做大运流年判断" in combined
```

- [ ] **Step 2: Run report schema tests and verify failure**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_report_schema.py -v
```

Expected: the new assertions fail because `build_report` still uses generic report text.

- [ ] **Step 3: Expose the new module**

Modify `src/mingli_engine/__init__.py` so `__all__` includes:

```python
    "interpretation",
```

- [ ] **Step 4: Import the interpretation builder**

In `src/mingli_engine/report_schema.py`, add:

```python
from mingli_engine.interpretation import build_basic_interpretation
```

- [ ] **Step 5: Use interpretation output in `build_report`**

Inside `build_report`, after `four_pillars_summary = _build_four_pillars_summary(chart)`, add:

```python
    interpretation = build_basic_interpretation(chart)
```

Then replace the report body assignments for these fields with:

```python
    five_elements_summary = interpretation.five_elements_summary
    ten_gods_summary = interpretation.ten_gods_summary
    structure_analysis = "\n".join(
        [
            interpretation.structure_observations,
            interpretation.limitations,
        ]
    )
    personality_tendencies = interpretation.day_master_summary
    strengths_and_issues = interpretation.focus_suggestions
    phase_overview = (
        f"{chart.luck_cycle_summary} 阶段概览只描述可反思的主题变化，"
        "不推断具体事件结果。当前基础结构解读层不做大运流年判断。"
    )
    action_suggestions = (
        f"{interpretation.focus_suggestions} "
        "行动上建议先把观察转成可记录的小步骤，再用现实反馈复盘。"
    )
```

Keep the existing `disclaimer`, `chart_card`, `assumptions`, `four_pillars_summary`, `glossary`, `ethics_reminder`, and safety review flow unchanged.

- [ ] **Step 6: Run report schema tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_report_schema.py -v
```

Expected: all report schema unit tests pass.

- [ ] **Step 7: Commit Task 3**

Run:

```powershell
git add src\mingli_engine\__init__.py src\mingli_engine\report_schema.py tests\unit\test_report_schema.py
git commit -m "feat: include interpretation in reports"
```

## Task 4: Cover CLI Output And Safety Regression

**Files:**
- Modify: `tests/integration/test_generate_markdown_report.py`
- Modify: `tests/integration/test_calculate_report_cli.py`
- Modify if needed: `tests/safety/test_red_lines_and_language.py`

- [ ] **Step 1: Add external chart CLI assertions**

In `tests/integration/test_generate_markdown_report.py`, extend `test_generate_report_outputs_expected_markdown_sections_and_source_note` with:

```python
    assert "五行信号观察" in markdown
    assert "明面信号" in markdown
    assert "藏干" in markdown
    assert "观察中心" in markdown
    assert "十神结构观察" in markdown
    assert "基础结构观察" in markdown
    assert "不做格局定论" in markdown
    assert "不做用神定论" in markdown
    assert "不做大运流年判断" in markdown
```

- [ ] **Step 2: Add automatic chart CLI assertions**

In `tests/integration/test_calculate_report_cli.py`, extend `test_calculate_report_outputs_markdown_from_birth_profile` with:

```python
    assert "五行信号观察" in markdown
    assert "明面信号" in markdown
    assert "藏干" in markdown
    assert "观察中心" in markdown
    assert "十神结构观察" in markdown
    assert "基础结构观察" in markdown
    assert "不做格局定论" in markdown
    assert "不做用神定论" in markdown
    assert "不做大运流年判断" in markdown
```

Keep the existing prohibited phrase loop.

- [ ] **Step 3: Run integration tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py -v
```

Expected: all integration tests pass, including the existing exit code `3` safety cases.

- [ ] **Step 4: Run safety tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\safety\test_red_lines_and_language.py -v
```

Expected: all safety tests pass. If this file does not scan generated reports, add one focused assertion that the generated Markdown for `examples\birth-profile.auto-gregorian.json` does not include `必定`, `注定`, `一定会`, or `死定`, then rerun.

- [ ] **Step 5: Commit Task 4**

Run:

```powershell
git add tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py tests\safety\test_red_lines_and_language.py
git commit -m "test: cover interpreted report output"
```

## Task 5: Full Verification

**Files:**
- Read: `specs/003-bazi-interpretation-rules/spec.md`
- Read: `specs/003-bazi-interpretation-rules/contracts/report-interpretation-contract.md`

- [ ] **Step 1: Run focused verification**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_interpretation.py tests\unit\test_report_schema.py tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py tests\safety\test_red_lines_and_language.py -v
```

Expected: all selected tests pass.

- [ ] **Step 2: Run the full suite**

Run:

```powershell
uv run --with pytest python -m pytest
```

Expected: all tests pass.

- [ ] **Step 3: Inspect generated Markdown manually**

Run:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Expected: output includes source disclosure, five-elements counts, day-master observation center wording, ten-gods placement, basic structure limitation text, and no prohibited absolute destiny language.

- [ ] **Step 4: Confirm worktree status**

Run:

```powershell
git status --short --branch
```

Expected: the branch is `003-bazi-interpretation-rules` and there are no uncommitted implementation changes.
