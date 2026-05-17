# Quickstart: 八字自动排盘层 MVP

## Prerequisites

- Python 3.12+
- Project dependencies installed, including the automatic calendar dependency

During development, run tests with:

```powershell
uv run --with pytest python -m pytest
```

If dependency installation is being tested before it is committed to `pyproject.toml`, use:

```powershell
uv run --no-project --with pytest --with lunar-python python -m pytest
```

## Example: Calculate Chart JSON

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

Run:

```powershell
$env:PYTHONPATH='src'
python -m mingli_engine.cli calculate-chart --input examples\birth-profile.auto-gregorian.json
```

Expected result:

- JSON output
- `chart_source.source_type` is `auto_calculated`
- `chart_source.confidence` is `medium`
- `chart_source.true_solar_time_applied` is `false`
- exactly four `pillars`
- for the reference case, pillars are `壬申`, `戊申`, `丙寅`, `癸巳`

## Example: Calculate Report

Run:

```powershell
$env:PYTHONPATH='src'
python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Expected result:

- Markdown report
- existing required report sections
- automatic chart source disclosure
- medium confidence visible in the assumptions section
- no prohibited absolute phrases

## Example: Unsupported Calendar

Create or use a profile with:

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

Run:

```powershell
$env:PYTHONPATH='src'
python -m mingli_engine.cli calculate-chart --input examples\birth-profile.unsupported-lunar.json
```

Expected result:

- non-zero exit code
- stable `Invalid input` message
- no traceback
- no partial chart JSON

## Example: Unsafe Focus Topic

Create or use a profile whose `focus_topic` is `寿命`.

Run:

```powershell
$env:PYTHONPATH='src'
python -m mingli_engine.cli calculate-report --input examples\birth-profile.unsafe-focus.json --format markdown
```

Expected result:

- non-zero exit code
- safety JSON output
- `allowed` is `false`
- no formal Markdown report

## Verification

Run the complete suite:

```powershell
uv run --with pytest python -m pytest
```

Expected result:

```text
all tests pass
```
