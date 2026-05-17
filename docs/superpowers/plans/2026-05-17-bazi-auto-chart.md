# 八字自动排盘层 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add automatic公历八字 chart calculation and one-command report generation on top of the existing report engine.

**Architecture:** Keep third-party calendar logic isolated in `calendar_provider.py`. Convert provider output into the existing `BaziChart` shape in `chart_calculator.py`, then reuse existing validation, safety, report assembly, Markdown rendering, and CLI error normalization.

**Tech Stack:** Python 3.12+, `lunar-python==1.4.8`, standard library `datetime/json/argparse/dataclasses`, pytest.

---

## Files

- Modify: `pyproject.toml`
- Modify: `src/mingli_engine/__init__.py`
- Create: `src/mingli_engine/calendar_provider.py`
- Create: `src/mingli_engine/chart_calculator.py`
- Modify: `src/mingli_engine/cli.py`
- Create: `tests/unit/test_calendar_provider.py`
- Create: `tests/unit/test_chart_calculator.py`
- Create: `tests/contract/test_auto_chart_cli_contract.py`
- Create: `tests/integration/test_calculate_report_cli.py`
- Create: `examples/birth-profile.auto-gregorian.json`
- Create: `examples/birth-profile.near-solar-term.json`
- Create: `examples/birth-profile.unsupported-lunar.json`
- Create: `examples/birth-profile.unsafe-focus.json`

### Task 1: Calendar Provider Adapter

**Files:**
- Modify: `pyproject.toml`
- Create: `src/mingli_engine/calendar_provider.py`
- Test: `tests/unit/test_calendar_provider.py`

- [ ] **Step 1: Write the failing provider test**

Create `tests/unit/test_calendar_provider.py`:

```python
from datetime import datetime

from mingli_engine.calendar_provider import calculate_provider_pillars


def test_provider_calculates_reference_four_pillars():
    pillars = calculate_provider_pillars(datetime(1992, 8, 18, 9, 30))

    assert [pillar.gan_zhi for pillar in pillars] == ["壬申", "戊申", "丙寅", "癸巳"]
    assert [pillar.name for pillar in pillars] == ["year", "month", "day", "hour"]
    assert pillars[0].hidden_stems == ["庚", "壬", "戊"]
    assert pillars[2].ten_god == "日主"
    assert pillars[3].element == "水火"
```

- [ ] **Step 2: Run the test to verify RED**

Run:

```powershell
uv run --no-project --with pytest --with lunar-python python -m pytest tests/unit/test_calendar_provider.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'mingli_engine.calendar_provider'`.

- [ ] **Step 3: Add the dependency**

Update `pyproject.toml`:

```toml
dependencies = [
    "lunar-python==1.4.8",
]
```

- [ ] **Step 4: Implement the provider adapter**

Create `src/mingli_engine/calendar_provider.py`:

```python
from dataclasses import dataclass
from datetime import datetime

from lunar_python import Solar


@dataclass(frozen=True)
class ProviderPillar:
    name: str
    heavenly_stem: str
    earthly_branch: str
    hidden_stems: list[str]
    ten_god: str
    element: str

    @property
    def gan_zhi(self) -> str:
        return f"{self.heavenly_stem}{self.earthly_branch}"


def calculate_provider_pillars(birth_datetime: datetime) -> list[ProviderPillar]:
    eight_char = Solar.fromYmdHms(
        birth_datetime.year,
        birth_datetime.month,
        birth_datetime.day,
        birth_datetime.hour,
        birth_datetime.minute,
        birth_datetime.second,
    ).getLunar().getEightChar()

    return [
        ProviderPillar(
            name="year",
            heavenly_stem=eight_char.getYearGan(),
            earthly_branch=eight_char.getYearZhi(),
            hidden_stems=list(eight_char.getYearHideGan()),
            ten_god=eight_char.getYearShiShenGan(),
            element=eight_char.getYearWuXing(),
        ),
        ProviderPillar(
            name="month",
            heavenly_stem=eight_char.getMonthGan(),
            earthly_branch=eight_char.getMonthZhi(),
            hidden_stems=list(eight_char.getMonthHideGan()),
            ten_god=eight_char.getMonthShiShenGan(),
            element=eight_char.getMonthWuXing(),
        ),
        ProviderPillar(
            name="day",
            heavenly_stem=eight_char.getDayGan(),
            earthly_branch=eight_char.getDayZhi(),
            hidden_stems=list(eight_char.getDayHideGan()),
            ten_god=eight_char.getDayShiShenGan(),
            element=eight_char.getDayWuXing(),
        ),
        ProviderPillar(
            name="hour",
            heavenly_stem=eight_char.getTimeGan(),
            earthly_branch=eight_char.getTimeZhi(),
            hidden_stems=list(eight_char.getTimeHideGan()),
            ten_god=eight_char.getTimeShiShenGan(),
            element=eight_char.getTimeWuXing(),
        ),
    ]
```

- [ ] **Step 5: Run the provider test to verify GREEN**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_calendar_provider.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit provider slice**

Run:

```powershell
git add pyproject.toml src/mingli_engine/calendar_provider.py tests/unit/test_calendar_provider.py
git commit -m "feat: add bazi calendar provider"
```

### Task 2: Chart Calculator

**Files:**
- Create: `src/mingli_engine/chart_calculator.py`
- Modify: `src/mingli_engine/__init__.py`
- Test: `tests/unit/test_chart_calculator.py`

- [ ] **Step 1: Write failing chart calculator tests**

Create `tests/unit/test_chart_calculator.py`:

```python
import pytest

from mingli_engine.chart_calculator import ChartCalculationError, calculate_bazi_chart
from mingli_engine.models import BirthProfile


def complete_profile(**overrides):
    values = {
        "calendar_type": "gregorian",
        "birth_date": "1992-08-18",
        "birth_time": "09:30",
        "birthplace": "上海市",
        "gender": "未指定",
        "focus_topic": "职业规划与长期学习节奏",
    }
    values.update(overrides)
    return BirthProfile(**values)


def test_calculate_bazi_chart_returns_complete_auto_chart():
    chart = calculate_bazi_chart(complete_profile())

    assert chart.chart_source.source_type == "auto_calculated"
    assert chart.chart_source.confidence == "medium"
    assert chart.chart_source.true_solar_time_applied is False
    assert "未人工复核" in chart.chart_source.source_note
    assert len(chart.pillars) == 4
    assert [p.heavenly_stem + p.earthly_branch for p in chart.pillars] == [
        "壬申",
        "戊申",
        "丙寅",
        "癸巳",
    ]
    assert chart.day_master == "丙"


def test_calculate_bazi_chart_rejects_lunar_calendar():
    with pytest.raises(ChartCalculationError, match="calendar_type"):
        calculate_bazi_chart(complete_profile(calendar_type="lunar"))


def test_calculate_bazi_chart_rejects_invalid_date():
    with pytest.raises(ChartCalculationError, match="birth_date"):
        calculate_bazi_chart(complete_profile(birth_date="1992-02-31"))


def test_calculate_bazi_chart_rejects_invalid_time():
    with pytest.raises(ChartCalculationError, match="birth_time"):
        calculate_bazi_chart(complete_profile(birth_time="25:99"))
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_chart_calculator.py -v
```

Expected: FAIL with missing `chart_calculator`.

- [ ] **Step 3: Implement chart calculator**

Create `src/mingli_engine/chart_calculator.py`:

```python
import re
from datetime import datetime

from mingli_engine.calendar_provider import ProviderPillar, calculate_provider_pillars
from mingli_engine.models import BaziChart, BirthProfile, ChartSource, Pillar
from mingli_engine.validation import validate_birth_profile


SUPPORTED_GREGORIAN_VALUES = {"gregorian", "solar", "公历"}
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
TIME_PATTERN = re.compile(r"\d{2}:\d{2}")


class ChartCalculationError(ValueError):
    pass


def _parse_birth_datetime(profile: BirthProfile) -> datetime:
    if not DATE_PATTERN.fullmatch(profile.birth_date):
        raise ChartCalculationError("birth_date must use YYYY-MM-DD")

    if not TIME_PATTERN.fullmatch(profile.birth_time):
        raise ChartCalculationError("birth_time must use HH:MM")

    try:
        date_part = datetime.strptime(profile.birth_date, "%Y-%m-%d").date()
    except ValueError as error:
        raise ChartCalculationError("birth_date must use YYYY-MM-DD") from error

    try:
        time_part = datetime.strptime(profile.birth_time, "%H:%M").time()
    except ValueError as error:
        raise ChartCalculationError("birth_time must use HH:MM") from error

    return datetime.combine(date_part, time_part)


def _validate_supported_profile(profile: BirthProfile) -> None:
    intake = validate_birth_profile(profile)
    if not intake.report_ready:
        raise ChartCalculationError(
            "missing required field(s): " + ", ".join(intake.missing_fields)
        )

    if profile.calendar_type.strip().lower() not in SUPPORTED_GREGORIAN_VALUES:
        raise ChartCalculationError(
            "calendar_type must be gregorian/solar/公历 for automatic calculation"
        )


def _to_pillar(provider_pillar: ProviderPillar) -> Pillar:
    return Pillar(
        name=provider_pillar.name,
        heavenly_stem=provider_pillar.heavenly_stem,
        earthly_branch=provider_pillar.earthly_branch,
        hidden_stems=provider_pillar.hidden_stems,
        ten_god=provider_pillar.ten_god,
        element=provider_pillar.element,
    )


def _five_elements_summary(provider_pillars: list[ProviderPillar]) -> dict[str, str]:
    return {pillar.name: pillar.element for pillar in provider_pillars}


def calculate_bazi_chart(profile: BirthProfile) -> BaziChart:
    _validate_supported_profile(profile)
    birth_datetime = _parse_birth_datetime(profile)
    provider_pillars = calculate_provider_pillars(birth_datetime)
    if len(provider_pillars) != 4:
        raise ChartCalculationError("calculation must produce exactly four pillars")

    pillars = [_to_pillar(pillar) for pillar in provider_pillars]
    day_pillar = next(pillar for pillar in provider_pillars if pillar.name == "day")

    return BaziChart(
        birth_profile=profile,
        chart_source=ChartSource(
            source_type="auto_calculated",
            source_note="由本引擎调用 lunar_python 自动计算，未人工复核",
            calendar_assumption="公历输入，按节气边界计算年柱和月柱",
            timezone_assumption="中国标准时间 UTC+08:00",
            solar_terms_assumption="节气数据由 lunar_python 提供",
            true_solar_time_applied=False,
            confidence="medium",
        ),
        pillars=pillars,
        day_master=day_pillar.heavenly_stem,
        five_elements_summary=_five_elements_summary(provider_pillars),
        ten_gods_summary="自动排盘提供十神基础信息；深入解读需结合报告语境审慎阅读。",
        strength_assessment="自动排盘层不直接给出旺衰定论；此处保留为候选分析入口。",
        pattern_candidates=["自动排盘未做完整格局定论"],
        useful_god_candidates=["自动排盘未做用神定论"],
        luck_cycle_summary="自动排盘层暂不计算大运起运；阶段内容仅作后续扩展入口。",
    )
```

- [ ] **Step 4: Export module name**

Update `src/mingli_engine/__init__.py`:

```python
__all__ = [
    "models",
    "validation",
    "safety",
    "report_schema",
    "markdown",
    "calendar_provider",
    "chart_calculator",
]
```

- [ ] **Step 5: Run chart calculator tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_chart_calculator.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit chart calculator slice**

Run:

```powershell
git add src/mingli_engine/chart_calculator.py src/mingli_engine/__init__.py tests/unit/test_chart_calculator.py
git commit -m "feat: calculate bazi chart from birth profile"
```

### Task 3: calculate-chart CLI Contract

**Files:**
- Modify: `src/mingli_engine/cli.py`
- Create: `tests/contract/test_auto_chart_cli_contract.py`
- Create: `examples/birth-profile.auto-gregorian.json`
- Create: `examples/birth-profile.unsupported-lunar.json`
- Create: `examples/birth-profile.unsafe-focus.json`

- [ ] **Step 1: Add example birth profiles**

Create `examples/birth-profile.auto-gregorian.json`:

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

Create `examples/birth-profile.unsupported-lunar.json`:

```json
{
  "calendar_type": "lunar",
  "birth_date": "1992-07-20",
  "birth_time": "09:30",
  "birthplace": "上海市",
  "gender": "未指定",
  "focus_topic": "职业规划"
}
```

Create `examples/birth-profile.unsafe-focus.json`:

```json
{
  "calendar_type": "gregorian",
  "birth_date": "1992-08-18",
  "birth_time": "09:30",
  "birthplace": "上海市",
  "gender": "未指定",
  "focus_topic": "寿命"
}
```

- [ ] **Step 2: Write failing contract tests**

Create `tests/contract/test_auto_chart_cli_contract.py`:

```python
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"


def _run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_path = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else os.pathsep.join([src_path, env["PYTHONPATH"]])
    )
    return subprocess.run(
        [sys.executable, "-m", "mingli_engine.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        input=input_text,
        capture_output=True,
        check=False,
    )


def test_calculate_chart_outputs_auto_calculated_chart_json():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["chart_source"]["source_type"] == "auto_calculated"
    assert payload["chart_source"]["confidence"] == "medium"
    assert payload["chart_source"]["true_solar_time_applied"] is False
    assert "未人工复核" in payload["chart_source"]["source_note"]
    assert [p["heavenly_stem"] + p["earthly_branch"] for p in payload["pillars"]] == [
        "壬申",
        "戊申",
        "丙寅",
        "癸巳",
    ]


def test_calculate_chart_accepts_stdin():
    profile = (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(encoding="utf-8")

    result = _run_cli("calculate-chart", "--input", "-", input_text=profile)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload["pillars"]) == 4


def test_calculate_chart_rejects_unsupported_lunar_calendar():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsupported-lunar.json"),
    )

    assert result.returncode == 1
    assert "Invalid input" in result.stderr
    assert "calendar_type" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_chart_rejects_unsafe_focus_topic():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsafe-focus.json"),
    )

    assert result.returncode == 3
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert "lifespan_or_death_timing" in payload["red_line_categories"]
```

- [ ] **Step 3: Run tests to verify RED**

Run:

```powershell
uv run --with pytest python -m pytest tests/contract/test_auto_chart_cli_contract.py -v
```

Expected: FAIL because `calculate-chart` command does not exist.

- [ ] **Step 4: Implement CLI command**

Modify `src/mingli_engine/cli.py`:

```python
from mingli_engine.chart_calculator import ChartCalculationError, calculate_bazi_chart
from mingli_engine.models import SafetyReviewResult
```

Add handlers:

```python
def _safety_review_focus_topic(profile: BirthProfile, *, disclaimer_present: bool) -> SafetyReviewResult:
    result = safety_check(profile.focus_topic, disclaimer_present=disclaimer_present)
    return result


def _calculate_chart(args: argparse.Namespace) -> int:
    profile = _birth_profile_from_dict(_read_json(args.input))
    safety_review = _safety_review_focus_topic(profile, disclaimer_present=False)
    if not safety_review.allowed:
        _write_json(safety_review)
        return 3

    chart = calculate_bazi_chart(profile)
    _write_json(chart)
    return 0
```

Add parser:

```python
    chart_parser = subparsers.add_parser("calculate-chart")
    chart_parser.add_argument("--input", required=True, type=Path)
    chart_parser.set_defaults(handler=_calculate_chart)
```

Add exception handling:

```python
    except ChartCalculationError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
```

- [ ] **Step 5: Run contract tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/contract/test_auto_chart_cli_contract.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit calculate-chart slice**

Run:

```powershell
git add src/mingli_engine/cli.py tests/contract/test_auto_chart_cli_contract.py examples/birth-profile.auto-gregorian.json examples/birth-profile.unsupported-lunar.json examples/birth-profile.unsafe-focus.json
git commit -m "feat: add calculate-chart cli"
```

### Task 4: calculate-report CLI Integration

**Files:**
- Modify: `src/mingli_engine/cli.py`
- Create: `tests/integration/test_calculate_report_cli.py`

- [ ] **Step 1: Write failing integration tests**

Create `tests/integration/test_calculate_report_cli.py`:

```python
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_path = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else os.pathsep.join([src_path, env["PYTHONPATH"]])
    )
    return subprocess.run(
        [sys.executable, "-m", "mingli_engine.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def test_calculate_report_generates_markdown_with_auto_source():
    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--format",
        "markdown",
    )

    assert result.returncode == 0, result.stderr
    markdown = result.stdout
    assert "# 八字结构化报告" in markdown
    assert "## 排盘来源与假设" in markdown
    assert "auto_calculated" in markdown
    assert "未人工复核" in markdown
    assert "medium" in markdown
    for phrase in ("必定", "注定", "一定会", "死定"):
        assert phrase not in markdown


def test_calculate_report_rejects_unsafe_focus_topic():
    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsafe-focus.json"),
        "--format",
        "markdown",
    )

    assert result.returncode == 3
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert "lifespan_or_death_timing" in payload["red_line_categories"]
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
uv run --with pytest python -m pytest tests/integration/test_calculate_report_cli.py -v
```

Expected: FAIL because `calculate-report` command does not exist.

- [ ] **Step 3: Implement calculate-report**

Modify `src/mingli_engine/cli.py`:

```python
def _calculate_report(args: argparse.Namespace) -> int:
    profile = _birth_profile_from_dict(_read_json(args.input))
    safety_review = _safety_review_focus_topic(profile, disclaimer_present=True)
    if not safety_review.allowed:
        _write_json(safety_review)
        return 3

    chart = calculate_bazi_chart(profile)
    report = build_report(chart)
    if not report.safety_review.allowed:
        _write_json(report.safety_review)
        return 3

    sys.stdout.write(render_markdown_report(report))
    return 0
```

Add parser:

```python
    calculate_report_parser = subparsers.add_parser("calculate-report")
    calculate_report_parser.add_argument("--input", required=True, type=Path)
    calculate_report_parser.add_argument("--format", choices=["markdown"], required=True)
    calculate_report_parser.set_defaults(handler=_calculate_report)
```

- [ ] **Step 4: Run integration tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/integration/test_calculate_report_cli.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit calculate-report slice**

Run:

```powershell
git add src/mingli_engine/cli.py tests/integration/test_calculate_report_cli.py
git commit -m "feat: add calculate-report cli"
```

### Task 5: Error Cases and Regression Examples

**Files:**
- Create: `examples/birth-profile.near-solar-term.json`
- Modify: `tests/unit/test_chart_calculator.py`
- Modify: `tests/contract/test_auto_chart_cli_contract.py`

- [ ] **Step 1: Add near solar-term example**

Create `examples/birth-profile.near-solar-term.json`:

```json
{
  "calendar_type": "gregorian",
  "birth_date": "1992-02-04",
  "birth_time": "04:50",
  "birthplace": "北京市",
  "gender": "未指定",
  "focus_topic": "整体结构观察"
}
```

- [ ] **Step 2: Add failing regression and error tests**

Append to `tests/unit/test_chart_calculator.py`:

```python
def test_calculate_bazi_chart_discloses_no_true_solar_time_for_boundary_case():
    chart = calculate_bazi_chart(
        complete_profile(
            birth_date="1992-02-04",
            birth_time="04:50",
            birthplace="北京市",
            focus_topic="整体结构观察",
        )
    )

    assert len(chart.pillars) == 4
    assert chart.chart_source.true_solar_time_applied is False
    assert "节气" in chart.chart_source.calendar_assumption
    assert "UTC+08:00" in chart.chart_source.timezone_assumption
```

Append to `tests/contract/test_auto_chart_cli_contract.py`:

```python
def test_calculate_chart_rejects_invalid_date(tmp_path):
    payload = json.loads((EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(encoding="utf-8"))
    payload["birth_date"] = "1992-02-31"
    input_path = tmp_path / "invalid-date.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    result = _run_cli("calculate-chart", "--input", str(input_path))

    assert result.returncode == 1
    assert "Invalid input" in result.stderr
    assert "birth_date" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_chart_rejects_invalid_time(tmp_path):
    payload = json.loads((EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(encoding="utf-8"))
    payload["birth_time"] = "25:99"
    input_path = tmp_path / "invalid-time.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    result = _run_cli("calculate-chart", "--input", str(input_path))

    assert result.returncode == 1
    assert "Invalid input" in result.stderr
    assert "birth_time" in result.stderr
    assert "Traceback" not in result.stderr
```

- [ ] **Step 3: Run tests to verify RED or GREEN**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_chart_calculator.py tests/contract/test_auto_chart_cli_contract.py -v
```

Expected: PASS if earlier validation already covers these cases, or FAIL with a specific missing disclosure/error behavior.

- [ ] **Step 4: Fix only failing behavior**

If boundary disclosure fails, update `ChartSource` strings in `chart_calculator.py` exactly:

```python
calendar_assumption="公历输入，按节气边界计算年柱和月柱",
timezone_assumption="中国标准时间 UTC+08:00",
```

If invalid date/time traceback appears, keep `ChartCalculationError` caught in `cli.py`.

- [ ] **Step 5: Run regression tests**

Run:

```powershell
uv run --with pytest python -m pytest tests/unit/test_chart_calculator.py tests/contract/test_auto_chart_cli_contract.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit regression slice**

Run:

```powershell
git add examples/birth-profile.near-solar-term.json tests/unit/test_chart_calculator.py tests/contract/test_auto_chart_cli_contract.py src/mingli_engine/chart_calculator.py src/mingli_engine/cli.py
git commit -m "test: cover automatic chart edge cases"
```

### Task 6: Full Verification

**Files:**
- Modify only if verification exposes gaps.

- [ ] **Step 1: Run complete test suite**

Run:

```powershell
uv run --with pytest python -m pytest
```

Expected: all tests pass.

- [ ] **Step 2: Run chart CLI spot check**

Run:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-chart --input examples\birth-profile.auto-gregorian.json
```

Expected: JSON contains `auto_calculated`, `medium`, and four pillars.

- [ ] **Step 3: Run report CLI spot check**

Run:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Expected: Markdown contains `# 八字结构化报告`, `## 排盘来源与假设`, `未人工复核`, `medium`, and no prohibited absolute phrases.

- [ ] **Step 4: Run unsafe focus spot check**

Run:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.unsafe-focus.json --format markdown
```

Expected: non-zero exit and JSON safety response with `allowed: false`.

- [ ] **Step 5: Clean generated caches and inspect status**

Run:

```powershell
$root = (Resolve-Path .).Path
Get-ChildItem -Recurse -Directory -Filter __pycache__ | ForEach-Object {
    $resolved = $_.FullName
    if (-not ($resolved.StartsWith($root))) { throw "Refusing to remove path outside workspace: $resolved" }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
git status --short --branch
```

Expected: clean working tree.

## Self-Review

- Spec coverage: US1 maps to Tasks 1, 2, 3, 5; US2 maps to Task 4; US3 maps to Tasks 2, 3, 4, 5.
- Constitution coverage: transparent `ChartSource`, safety review before automatic report, no storage, tests for invalid input and red lines.
- Marker scan: no unresolved planning markers remain.
- Type consistency: provider `ProviderPillar` converts to existing `Pillar`; calculator returns existing `BaziChart`; CLI writes dataclasses through existing `_write_json`.
