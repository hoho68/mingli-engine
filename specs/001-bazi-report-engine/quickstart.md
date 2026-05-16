# Quickstart: 八字知识与报告引擎 MVP

This quickstart describes the expected developer workflow after implementation tasks are generated.

## 1. Create the Python Project

Create the package and test layout from [plan.md](./plan.md):

```text
src/mingli_engine/
tests/unit/
tests/contract/
tests/integration/
tests/safety/
```

## 2. Run Tests First

Before implementation, add failing tests for:

- complete and incomplete birth-profile validation
- report section completeness
- disclaimer presence
- red-line refusal behavior
- prohibited absolute-language filtering
- CLI JSON contract examples

Expected command:

```powershell
python -m pytest
```

Expected initial result: tests fail because the package is not implemented yet.

## 3. Validate Intake

Example command after implementation:

```powershell
mingli-engine validate-intake --input examples/birth-profile.complete.json
```

Expected result:

```json
{
  "report_ready": true,
  "missing_fields": [],
  "clarification_questions": []
}
```

## 4. Generate Markdown Report

Example command after implementation:

```powershell
mingli-engine generate-report --input examples/bazi-chart.external-verified.json --format markdown
```

Expected result: Markdown report with disclaimer, chart card, assumptions, four-pillar summary, five-element summary, ten-god summary, structure analysis, personality tendencies, strengths and issues, phase overview, action suggestions, glossary, and ethics reminder.

## 5. Check Safety Behavior

Example command after implementation:

```powershell
mingli-engine safety-check --input examples/red-line.lifespan.json
```

Expected result: request is blocked with a redirect message and no formal report is generated.

## 6. Completion Gate

The feature is not complete until:

- `python -m pytest` passes
- red-line tests pass
- prohibited absolute phrases are blocked or rewritten
- generated full reports include a visible disclaimer
- generated full reports expose chart source and assumptions
