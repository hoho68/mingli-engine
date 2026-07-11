# Bazi Core Inference Engine V1 Design

**Date:** 2026-07-12
**Target:** `018-bazi-core-inference-engine-v1`
**Status:** Approved design

## Purpose

Build a deterministic, traceable, and testable Bazi inference core on top of
the existing chart, evidence, safety, and report pipeline. The engine will use
a common Ziping baseline for calculation and keep Liang Xiangrun, Duan, and
other lineages in explicit adapters. It will not treat evidence coverage as
proof that a chart-specific calculation has completed.

The V1 target covers structural Bazi calculation only. It does not add a web
application, AI calls, a database, a vector store, commercial features, other
divination systems, or deterministic real-world predictions.

## Architectural Principles

1. Calculation facts, evidence coverage, interpretation readiness, and report
   wording are separate states.
2. Raw sources and curated evidence cannot alter chart facts.
3. A downstream calculation cannot bypass an incomplete prerequisite.
4. School adapters may interpret or reprioritize candidates, but cannot rewrite
   the chart or silently merge incompatible rules.
5. Every conclusion must expose its inputs, rule identifiers, supporting and
   opposing signals, assumptions, missing inputs, confidence, and status.
6. Missing or conflicting information produces an explicit degraded state, not
   a guessed answer.
7. Personal birth data and generated reports remain in memory unless a future,
   separately approved feature defines storage.

## System Layers

### 1. Chart Facts

This layer owns deterministic facts: four pillars, hidden stems, stem and
branch elements, yin and yang, ten-god relations, month command, exposed stems,
roots, twelve growth phases, and configured time assumptions. It extends the
current `calendar_provider.py` and `chart_calculator.py` behavior without making
interpretive claims.

The existing Gregorian path remains supported. Timezone and true-solar-time
assumptions must be explicit. Birthplace cannot imply a longitude or timezone
calculation unless the required data is available.

### 2. Core Inference

The common Ziping baseline computes:

- branch combinations, meetings, clashes, punishments, harms, and breaks;
- whether a relation is present, active, blocked, transformed, or uncertain;
- day-master support through season, roots, companions, production, control,
  draining, and exhaustion;
- strength intervals and sensitivity, rather than an unexplained score;
- pattern candidates, formation conditions, pattern damage, rescue, and
  follow-structure candidates;
- useful- and taboo-god candidates through support/control, seasonal
  adjustment, mediation, and illness/remedy methods;
- luck-cycle direction, start timing, pillars, and natal/luck/year interaction.

Core inference produces candidates and reasoned states. It does not generate
domain claims about marriage, wealth, health, lifespan, or guaranteed events.

### 3. School Adapters

The Ziping adapter represents the default common baseline. Liang Xiangrun and
Duan adapters consume the same core analysis and return named adjustments,
terminology, priorities, assumptions, and disagreements. They cannot mutate
chart facts or hide differences behind one synthetic result.

New school adapters require their own reviewed rules and counterexamples. They
are not added merely because a source exists in the library.

### 4. Knowledge And Reports

The current classical evidence corpus explains methods, limitations, school
differences, and source provenance. It does not calculate missing chart facts.
Reports display five independent dimensions:

- calculation status;
- evidence status;
- interpretation status;
- confidence;
- safety boundary.

A placeholder such as "luck cycles not calculated" must remain
`not_computed`, even when the evidence corpus has complete luck-cycle coverage.

## Proposed Package Layout

```text
src/mingli_engine/
|-- bazi/
|   |-- __init__.py
|   |-- result_models.py
|   |-- constants.py
|   |-- facts.py
|   |-- branch_relations.py
|   |-- strength.py
|   |-- patterns.py
|   |-- useful_gods.py
|   |-- luck_cycles.py
|   |-- analysis.py
|   `-- schools/
|       |-- __init__.py
|       |-- base.py
|       |-- ziping.py
|       |-- liang_xiangrun.py
|       `-- duan.py
|-- data/calculation/
|   |-- strength_weights.json
|   `-- school_profiles.json
|-- chart_calculator.py
|-- formal_interpretation.py
`-- report_schema.py

tests/
|-- unit/bazi/
|-- integration/
|   |-- test_bazi_analysis_pipeline.py
|   `-- test_reasoned_report_pipeline.py
`-- fixtures/bazi_calculation/
    |-- verified_charts.json
    |-- strength_boundary_cases.json
    |-- pattern_counterexamples.json
    `-- luck_cycle_boundary_cases.json
```

New result models live inside `bazi/result_models.py`; they do not enlarge the
existing `models.py`. The large source-intake and materials-audit modules remain
outside this work unless a narrowly required interface change is unavoidable.

## Result Protocol

All reasoned results share this semantic contract:

```python
@dataclass(frozen=True)
class ReasonedResult:
    status: Literal[
        "not_computed",
        "computed",
        "indeterminate",
        "disputed",
    ]
    conclusion: str
    confidence: Literal["high", "medium", "low"]
    supporting_signals: list[str]
    opposing_signals: list[str]
    assumptions: list[str]
    missing_inputs: list[str]
    rule_ids: list[str]
```

Specialized immutable results include `ChartFacts`, `BranchRelationResult`,
`StrengthResult`, `PatternCandidateResult`, `UsefulGodCandidateResult`,
`LuckCycleResult`, `SchoolInterpretation`, and `CalculationBundle`.

`CalculationBundle` also records `engine_version`, `ruleset_version`, input
assumptions, stage statuses, rule hits, and disagreements. It is the only object
passed from the inference pipeline to knowledge/report integration.

## Data Flow

```text
BirthProfile
  -> calendar provider and chart calculator
  -> ChartFacts
  -> BranchRelationResult records
  -> StrengthResult
  -> PatternCandidateResult records
  -> UsefulGodCandidateResult records
  -> LuckCycleResult
  -> SchoolInterpretation records
  -> CalculationBundle
  -> curated evidence and report integration
```

The current `BaziChart` remains temporarily compatible. A bounded adapter maps
new results into legacy fields until report consumers migrate. Compatibility
fields cannot be used as the source of truth for new calculations.

## Delivery Phases

### Phase 1: State Semantics And Baseline

Introduce the result protocol, version fields, dependency states, and legacy
adapter. Prevent placeholder text from becoming a candidate conclusion. Freeze
the existing 964-test baseline and representative report outputs.

### Phase 2: Structural Facts

Implement hidden-stem ten gods, month command, exposed stems, roots, twelve
growth phases, and conditional branch relations. Cover solar-term boundaries,
late-night inputs, repeated branches, and incomplete time assumptions.

### Phase 3: Strength

Compute season, roots, support, control, draining, and exhaustion as separate
contributions. Return strong, weak, relatively balanced, follow-structure
candidate, or indeterminate results with sensitivity information. Version and
validate all configurable weights.

### Phase 4: Patterns And Useful Gods

Implement month-command pattern candidates, formation, damage, rescue, and
follow-pattern checks. Generate support/control, seasonal-adjustment,
mediation, and illness/remedy candidates only when prerequisites allow. Add the
Ziping, Liang Xiangrun, and Duan adapters with explicit disagreements.

### Phase 5: Luck Cycles

Implement direction, start timing, luck pillars, and selected-year structural
interactions. Outputs describe activated structural themes and conditions, not
guaranteed events, disaster dates, or lifespan.

### Phase 6: Reports And Case Calibration

Integrate `CalculationBundle` into Markdown, HTML, CLI, evidence audit,
acceptance, release, and project-completion gates. Add privacy-safe verified
charts, boundary cases, counterexamples, and a feedback format that records the
algorithm output before real-world feedback.

## Error And Degradation Rules

- Invalid date, time, or calendar input stops calculation as `invalid_input`.
- Invalid rule configuration stops inference as `configuration_error`.
- Missing timezone or solar-time inputs remain visible assumptions.
- Near-boundary strength returns `indeterminate` with both sides' signals.
- Conflicting pattern candidates return `disputed` without forced selection.
- Incomplete strength blocks or degrades pattern and useful-god calculation.
- Missing school prerequisites return `not_computed` for that adapter.
- Evidence without a chart result remains explanatory knowledge only.
- High-risk or deterministic requests continue through the existing refusal and
  guarded-language pipeline.

## Quality Gates

1. Determinism: identical inputs and versions produce identical results.
2. Dependency integrity: downstream stages cannot bypass prerequisites.
3. Counterexamples: important rules have positive, negative, and boundary
   cases.
4. School isolation: every adjustment names its adapter and rule identifiers.
5. Evidence isolation: calculation and evidence statuses are tested separately.
6. Safety: existing lifespan, disaster, medical, investment, and deterministic
   matching boundaries remain enforced.
7. Compatibility: all existing 964 tests continue to pass.
8. Release: CLI, Markdown, HTML, acceptance, release, and completion gates pass.

Implementation follows test-driven development. Each capability starts with a
verified fixture and failing test, adds the smallest deterministic rule, then
adds counterexamples and boundary cases before the next dependency begins.

## V1 Completion Criteria

The long target is complete only when:

- chart facts are complete, immutable, and versioned;
- hidden-stem ten gods, exposed stems, roots, month command, and twelve growth
  phases are calculated;
- branch relations include participants, conditions, blockers, and status;
- strength includes contribution details, an interval, and sensitivity;
- patterns include formation, damage, rescue, and follow candidates;
- useful-god candidates cover the four approved methods without forcing one
  answer;
- the Ziping baseline and at least Liang Xiangrun and Duan adapters run side by
  side;
- luck-cycle direction, start timing, pillars, and selected-year structural
  interaction are calculated;
- reports separate facts, calculation, school interpretation, evidence, and
  action reflection;
- at least 30 verified charts and 20 boundary or counterexample cases exist;
- all existing and new tests pass;
- no AI, database, web, commercial, or other-divination scope is introduced;
- no personal profile or report is persisted;
- the final release status is `ready_with_guardrails` and the worktree is clean.

## Explicitly Deferred Work

- marriage, wealth, career, health, and other domain-specific inference;
- web UI, mobile app, accounts, payments, and commercial delivery;
- LLM integration, embeddings, vector retrieval, and databases;
- Ziwei, Qimen, Feng Shui, and other systems;
- broad new-material intake unrelated to a required rule or counterexample;
- general refactoring of the existing large governance modules.

## Risk Controls

The engine validates consistency with a declared traditional rule system; it
does not claim scientific prediction. Weight configurations are versioned
assumptions, not objective truth. Case feedback is captured only after the
algorithm output to reduce outcome-fitting. School differences stay explicit,
and high-risk conclusions remain downgraded or refused.
