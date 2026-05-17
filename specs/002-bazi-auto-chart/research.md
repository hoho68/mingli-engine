# Research: 八字自动排盘层 MVP

## Decision: Use `lunar-python==1.4.8` for first-version chart calculation

**Rationale**: The package is pure Python, installable in the current Windows-first local environment, and exposes direct八字 methods through `Solar.fromYmdHms(...).getLunar().getEightChar()`. Local API probing confirmed fixed sample output for `1992-08-18 09:30`: `壬申 戊申 丙寅 癸巳`. PyPI lists version `1.4.8`; the GitHub project documents support for公历,农历,干支,节气,八字,五行,十神, and related calendar functions.

**Alternatives considered**:

- `sxtwl`: more low-level calendar control, but greater platform/installation risk for this first MVP slice.
- Hand-written干支 algorithms: full control, but high risk around solar terms, Li Chun/year boundaries, month boundaries, and day-pillar calculation.
- Placeholder/approximate rules: faster, but would weaken calculation transparency and user trust.

## Decision: Isolate third-party calls in `calendar_provider.py`

**Rationale**: Existing code already separates models, validation, safety, report assembly, Markdown, and CLI. Keeping `lunar_python` behind an adapter preserves that boundary and lets later versions replace the library or add true solar time without changing report generation.

**Alternatives considered**:

- Import library directly in `cli.py`: simpler initially, but couples user interface to provider API.
- Import library directly in `report_schema.py`: rejected because report assembly must not own calculation.

## Decision: Convert provider results into existing `BaziChart`

**Rationale**: The current report engine already consumes `BaziChart`, validates four pillars, and exposes `ChartSource`. Reusing this shape keeps automatic reports on the same safety and rendering path as externally verified charts.

**Alternatives considered**:

- Add a second report schema for automatic charts: rejected because it would duplicate safety and Markdown behavior.
- Return only raw third-party output: rejected because users and tests need stable project-owned JSON.

## Decision: First version supports only公历 + China standard time, no true solar time

**Rationale**: This matches the confirmed scope and keeps the feature independently testable. It also avoids pretending to use birthplace longitude before the project has a proper location model.

**Alternatives considered**:

- Add农历 input: useful later, but expands validation and conversion scope.
- Add true solar time: more precise for some schools, but requires longitude and user-facing rule choices.
- Add overseas timezone: useful later, but requires timezone parsing and clearer location semantics.

## Decision: Automatic chart confidence is `medium`

**Rationale**: The chart is calculated by the engine but not manually reviewed. `medium` confidence and explicit `auto_calculated` provenance preserve the constitution's transparent calculation boundary.

**Alternatives considered**:

- `high`: rejected because the result is not manually verified.
- `low`: too conservative for complete supported inputs backed by a fixed library and regression cases.

## Decision: Conservative summaries for advanced interpretation fields

**Rationale**: `BaziChart` currently requires strength, pattern, useful-god, and luck-cycle summary fields. The automatic calculation MVP should populate them with safe, explicit conservative summaries rather than attempt full格局 or大运 analysis.

**Alternatives considered**:

- Leave fields blank: would weaken report completeness and may fail downstream expectations.
- Implement full旺衰/格局/用神/大运 logic now: too broad for the automatic chart MVP.
