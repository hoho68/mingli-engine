# Bazi Core Inference Engine V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, traceable Bazi calculation core that separates chart calculation, school interpretation, evidence coverage, and report wording.

**Architecture:** Add a focused `mingli_engine.bazi` package that consumes the existing immutable `BaziChart`, produces a versioned `CalculationBundle`, and exposes explicit computed, indeterminate, disputed, or not-computed states. Keep the current JSON evidence pipeline and renderers as consumers; use a compatibility adapter until legacy report fields are no longer treated as calculation truth.

**Tech Stack:** Python 3.12+, dataclasses, `lunar-python==1.4.8`, JSON configuration, argparse, pytest, existing Markdown/HTML renderers.

---

## Scope And Execution Rules

- Implement tasks in order. Tasks 1-10 form the calculation dependency chain.
- Use TDD for every task: failing focused test, minimal implementation, focused pass, regression pass, commit.
- Set `$env:PYTHONPATH='src'` and `$env:PYTHONDONTWRITEBYTECODE='1'` for test commands.
- Use `python -m pytest -p no:cacheprovider` to keep verification read-only apart from intended source edits.
- Do not modify raw PDFs, `Markdown/`, `资料原文/`, or `资料整理/`.
- Do not add AI, persistence, Web, commercial, or non-Bazi functionality.
- Do not split `source_intake.py`, `materials_audit.py`, or `models.py` as part of this feature. Task 15 may append one backward-compatible field to `ProjectCompletionSummary`.
- After each task, run `git diff --check` and inspect only the intended files before committing.

## File Map

**Create:**

- `src/mingli_engine/bazi/__init__.py`
- `src/mingli_engine/bazi/result_models.py`
- `src/mingli_engine/bazi/constants.py`
- `src/mingli_engine/bazi/facts.py`
- `src/mingli_engine/bazi/branch_relations.py`
- `src/mingli_engine/bazi/strength.py`
- `src/mingli_engine/bazi/patterns.py`
- `src/mingli_engine/bazi/useful_gods.py`
- `src/mingli_engine/bazi/luck_cycles.py`
- `src/mingli_engine/bazi/analysis.py`
- `src/mingli_engine/bazi/legacy_adapter.py`
- `src/mingli_engine/bazi/schools/__init__.py`
- `src/mingli_engine/bazi/schools/base.py`
- `src/mingli_engine/bazi/schools/ziping.py`
- `src/mingli_engine/bazi/schools/liang_xiangrun.py`
- `src/mingli_engine/bazi/schools/duan.py`
- `src/mingli_engine/data/calculation/strength_weights.json`
- `src/mingli_engine/data/calculation/school_profiles.json`
- `tests/unit/bazi/` test modules
- `tests/integration/test_bazi_analysis_pipeline.py`
- `tests/integration/test_reasoned_report_pipeline.py`
- `tests/fixtures/bazi_calculation/` fixture files

**Modify:**

- `src/mingli_engine/calendar_provider.py`
- `src/mingli_engine/chart_calculator.py`
- `src/mingli_engine/formal_interpretation.py`
- `src/mingli_engine/report_schema.py`
- `src/mingli_engine/markdown.py`
- `src/mingli_engine/html.py`
- `src/mingli_engine/report_acceptance.py`
- `src/mingli_engine/report_release.py`
- `src/mingli_engine/project_completion.py`
- `src/mingli_engine/models.py`
- relevant existing tests and `docs/classical_sources/README.md`

## Phase 1: State Semantics And Baseline

### Task 1: Introduce The Calculation Result Protocol

**Files:**
- Create: `src/mingli_engine/bazi/__init__.py`
- Create: `src/mingli_engine/bazi/result_models.py`
- Test: `tests/unit/bazi/test_result_models.py`

- [ ] **Step 1: Write the failing result-model tests**

```python
from dataclasses import FrozenInstanceError

import pytest

from mingli_engine.bazi.result_models import ReasonedResult


def test_reasoned_result_exposes_separate_status_and_trace_fields():
    result = ReasonedResult(
        status="indeterminate",
        conclusion="日主强弱处于临界区间",
        confidence="low",
        supporting_signals=("month_command:resource",),
        opposing_signals=("root:none",),
        assumptions=("ruleset:ziping-v1",),
        missing_inputs=(),
        rule_ids=("strength.month_command.resource",),
    )

    assert result.status == "indeterminate"
    assert result.rule_ids == ("strength.month_command.resource",)
    with pytest.raises(FrozenInstanceError):
        result.status = "computed"


def test_reasoned_result_rejects_unknown_status():
    with pytest.raises(ValueError, match="unsupported computation status"):
        ReasonedResult(
            status="candidate",
            conclusion="",
            confidence="low",
        )
```

- [ ] **Step 2: Run the test and verify import failure**

Run: `python -m pytest -q -p no:cacheprovider tests/unit/bazi/test_result_models.py`

Expected: FAIL because `mingli_engine.bazi.result_models` does not exist.

- [ ] **Step 3: Implement immutable shared models**

Create `result_models.py` with the following public contract. Use tuple fields so
results cannot be mutated after calculation.

```python
from dataclasses import dataclass, field
from typing import Literal


ComputationStatus = Literal[
    "not_computed", "computed", "indeterminate", "disputed"
]
Confidence = Literal["high", "medium", "low"]

_STATUSES = frozenset({"not_computed", "computed", "indeterminate", "disputed"})
_CONFIDENCES = frozenset({"high", "medium", "low"})


@dataclass(frozen=True)
class ReasonedResult:
    status: ComputationStatus
    conclusion: str
    confidence: Confidence
    supporting_signals: tuple[str, ...] = field(default_factory=tuple)
    opposing_signals: tuple[str, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    missing_inputs: tuple[str, ...] = field(default_factory=tuple)
    rule_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.status not in _STATUSES:
            raise ValueError(f"unsupported computation status: {self.status}")
        if self.confidence not in _CONFIDENCES:
            raise ValueError(f"unsupported confidence: {self.confidence}")


@dataclass(frozen=True)
class StemFact:
    pillar_name: str
    stem: str
    element: str
    polarity: str
    ten_god: str


@dataclass(frozen=True)
class HiddenStemFact:
    pillar_name: str
    branch: str
    stem: str
    role: str
    element: str
    polarity: str
    ten_god: str


@dataclass(frozen=True)
class RootFact:
    stem: str
    stem_pillar: str
    branch: str
    branch_pillar: str
    role: str
    exact_stem_root: bool


@dataclass(frozen=True)
class ChartFacts:
    day_master: str
    month_branch: str
    exposed_stems: tuple[StemFact, ...]
    hidden_stems: tuple[HiddenStemFact, ...]
    roots: tuple[RootFact, ...]
    twelve_growth_by_pillar: tuple[tuple[str, str], ...]
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class BranchRelationResult:
    relation_type: str
    branches: tuple[str, ...]
    pillar_names: tuple[str, ...]
    state: str
    transformed_element: str
    conditions: tuple[str, ...]
    blockers: tuple[str, ...]
    rule_id: str


@dataclass(frozen=True)
class StrengthContribution:
    category: str
    signal: str
    value: float
    rule_id: str


@dataclass(frozen=True)
class StrengthResult:
    reasoning: ReasonedResult
    score: float
    lower_bound: float
    upper_bound: float
    label: str
    contributions: tuple[StrengthContribution, ...]


@dataclass(frozen=True)
class PatternCandidateResult:
    pattern_id: str
    name: str
    rank: int
    reasoning: ReasonedResult
    formation_conditions: tuple[str, ...]
    damage_conditions: tuple[str, ...]
    rescue_conditions: tuple[str, ...]


@dataclass(frozen=True)
class UsefulGodCandidateResult:
    method: str
    element: str
    rank: int
    reasoning: ReasonedResult


@dataclass(frozen=True)
class LuckPillar:
    index: int
    gan_zhi: str
    start_year: int
    end_year: int
    start_age: int
    end_age: int


@dataclass(frozen=True)
class LuckCycleResult:
    reasoning: ReasonedResult
    forward: bool
    start_years: int
    start_months: int
    start_days: int
    start_solar: str
    pillars: tuple[LuckPillar, ...]
    selected_year_relations: tuple[BranchRelationResult, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SchoolInterpretation:
    school_id: str
    profile_version: str
    reasoning: ReasonedResult
    preferred_pattern_ids: tuple[str, ...]
    preferred_useful_god_elements: tuple[str, ...]


@dataclass(frozen=True)
class CalculationBundle:
    engine_version: str
    ruleset_version: str
    facts: ChartFacts
    branch_relations: tuple[BranchRelationResult, ...]
    strength: StrengthResult
    patterns: tuple[PatternCandidateResult, ...]
    useful_gods: tuple[UsefulGodCandidateResult, ...]
    luck_cycles: LuckCycleResult
    schools: tuple[SchoolInterpretation, ...]
```

Export only `CalculationBundle`, `ComputationStatus`, `Confidence`, and
`ReasonedResult` from `bazi/__init__.py`.

- [ ] **Step 4: Run the focused test**

Expected: `2 passed`.

- [ ] **Step 5: Run the existing model/report tests**

Run: `python -m pytest -q -p no:cacheprovider tests/unit/test_report_schema.py tests/unit/test_formal_interpretation.py`

Expected: all existing tests pass unchanged.

- [ ] **Step 6: Commit**

```powershell
git add src/mingli_engine/bazi tests/unit/bazi/test_result_models.py
git commit -m "feat: add bazi calculation result protocol"
```

### Task 2: Separate Calculation, Evidence, And Interpretation States

**Files:**
- Modify: `src/mingli_engine/formal_interpretation.py`
- Test: `tests/unit/test_formal_interpretation.py`

- [ ] **Step 1: Add a failing placeholder-state regression test**

Create a chart whose `strength_assessment` is the current placeholder and whose
`luck_cycle_summary` says it is not calculated. Assert that helper functions
classify both as `not_computed`, even when matching evidence units exist.

```python
def test_placeholder_chart_signals_are_not_treated_as_computed(sample_chart):
    statuses = classify_chart_calculation_states(sample_chart)
    assert statuses["pattern_strength"] == "not_computed"
    assert statuses["luck_cycle"] == "not_computed"
```

- [ ] **Step 2: Run the focused test and verify the missing helper failure**

- [ ] **Step 3: Add explicit placeholder classification**

```python
_NOT_COMPUTED_MARKERS = (
    "暂未",
    "未计算",
    "未展开评估",
    "not calculated",
    "not computed",
)


def _is_computed_signal(value: str) -> bool:
    text = value.strip().casefold()
    return bool(text) and not any(marker.casefold() in text for marker in _NOT_COMPUTED_MARKERS)


def classify_chart_calculation_states(chart: BaziChart) -> dict[str, str]:
    return {
        "pattern_strength": (
            "computed" if _is_computed_signal(chart.strength_assessment) else "not_computed"
        ),
        "useful_god_candidate": (
            "computed" if chart.useful_god_candidates else "not_computed"
        ),
        "taboo_god_candidate": "not_computed",
        "luck_cycle": (
            "computed" if _is_computed_signal(chart.luck_cycle_summary) else "not_computed"
        ),
    }
```

Use this state when choosing formal-conclusion strength. Evidence with no
computed chart signal becomes `weakly_supported`, never `candidate`.

- [ ] **Step 4: Run formal interpretation and report schema tests**

- [ ] **Step 5: Commit**

```powershell
git add src/mingli_engine/formal_interpretation.py tests/unit/test_formal_interpretation.py
git commit -m "fix: separate evidence coverage from chart calculation"
```

## Phase 2: Structural Facts

### Task 3: Add Canonical Stem, Branch, Hidden-Stem, And Growth Constants

**Files:**
- Create: `src/mingli_engine/bazi/constants.py`
- Test: `tests/unit/bazi/test_constants.py`

- [ ] **Step 1: Write parameterized failing tests for all ten stems**

Test element, polarity, hidden-stem role order, and these growth anchors:
`甲亥`, `乙午`, `丙寅`, `丁酉`, `戊寅`, `己酉`, `庚巳`, `辛子`, `壬申`, `癸卯`.

- [ ] **Step 2: Implement canonical tables**

```python
STEMS = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
BRANCHES = ("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥")
ELEMENTS = ("木", "火", "土", "金", "水")
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
STEM_ELEMENT = dict(zip(STEMS, ("木", "木", "火", "火", "土", "土", "金", "金", "水", "水")))
STEM_POLARITY = dict(zip(STEMS, ("yang", "yin", "yang", "yin", "yang", "yin", "yang", "yin", "yang", "yin")))
BRANCH_ELEMENT = dict(zip(BRANCHES, ("水", "土", "木", "木", "土", "火", "火", "土", "金", "金", "土", "水")))
HIDDEN_STEMS = {
    "子": (("癸", "main"),),
    "丑": (("己", "main"), ("癸", "middle"), ("辛", "residual")),
    "寅": (("甲", "main"), ("丙", "middle"), ("戊", "residual")),
    "卯": (("乙", "main"),),
    "辰": (("戊", "main"), ("乙", "middle"), ("癸", "residual")),
    "巳": (("丙", "main"), ("戊", "middle"), ("庚", "residual")),
    "午": (("丁", "main"), ("己", "middle")),
    "未": (("己", "main"), ("丁", "middle"), ("乙", "residual")),
    "申": (("庚", "main"), ("壬", "middle"), ("戊", "residual")),
    "酉": (("辛", "main"),),
    "戌": (("戊", "main"), ("辛", "middle"), ("丁", "residual")),
    "亥": (("壬", "main"), ("甲", "middle")),
}
GROWTH_PHASES = ("长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养")
GROWTH_START = {"甲": "亥", "乙": "午", "丙": "寅", "丁": "酉", "戊": "寅", "己": "酉", "庚": "巳", "辛": "子", "壬": "申", "癸": "卯"}
```

Implement `growth_phase(stem, branch)` by walking forward for yang stems and
backward for yin stems from `GROWTH_START`.

- [ ] **Step 3: Run constants tests and commit**

Commit: `feat: add canonical bazi fact tables`.

### Task 4: Build Chart Facts And Hidden-Stem Ten Gods

**Files:**
- Create: `src/mingli_engine/bazi/facts.py`
- Test: `tests/unit/bazi/test_facts.py`

- [ ] **Step 1: Write failing tests using the verified 壬申/戊申/丙寅/癸巳 chart**

Assert:

- day master is `丙` and month branch is `申`;
- hidden `申` stems are `庚/壬/戊` with 财/杀/食 categories relative to 丙;
- `丙` has an exact root in `寅` and `巳`;
- every pillar has a twelve-growth value;
- birthplace is not silently converted into longitude.

- [ ] **Step 2: Implement the ten-god relation function**

```python
def ten_god(day_master: str, target_stem: str) -> str:
    day_element = STEM_ELEMENT[day_master]
    target_element = STEM_ELEMENT[target_stem]
    same_polarity = STEM_POLARITY[day_master] == STEM_POLARITY[target_stem]
    if target_element == day_element:
        return "比肩" if same_polarity else "劫财"
    if GENERATES[target_element] == day_element:
        return "偏印" if same_polarity else "正印"
    if GENERATES[day_element] == target_element:
        return "食神" if same_polarity else "伤官"
    if CONTROLS[day_element] == target_element:
        return "偏财" if same_polarity else "正财"
    if CONTROLS[target_element] == day_element:
        return "七杀" if same_polarity else "正官"
    raise ValueError("unreachable five-element relation")
```

- [ ] **Step 3: Implement `build_chart_facts(chart: BaziChart) -> ChartFacts`**

Use the four existing pillars as the source of pillar order. Rebuild hidden
stems from the canonical table and compare them with provider values; mismatch
raises `ValueError("provider hidden stems do not match canonical table")`.
Create root facts for every exposed stem found in every branch's hidden stems.
Record the existing chart-source timezone and true-solar-time statements as
assumptions without adding inferred coordinates.

- [ ] **Step 4: Run facts, calendar-provider, and chart-calculator tests**

- [ ] **Step 5: Commit**

Commit: `feat: derive traceable bazi chart facts`.

### Task 5: Detect Conditional Branch Relations

**Files:**
- Create: `src/mingli_engine/bazi/branch_relations.py`
- Test: `tests/unit/bazi/test_branch_relations.py`

- [ ] **Step 1: Write failing table tests**

Cover every six-combination and clash pair, all harm and break pairs, `子卯`
punishment, `寅巳申` and `丑未戌` complete/incomplete groups, self-punishment,
all four three-combinations, and all four three-meetings.

- [ ] **Step 2: Implement explicit relation tables**

```python
SIX_COMBINATIONS = {frozenset(pair) for pair in ("子丑", "寅亥", "卯戌", "辰酉", "巳申", "午未")}
SIX_CLASHES = {frozenset(pair) for pair in ("子午", "丑未", "寅申", "卯酉", "辰戌", "巳亥")}
SIX_HARMS = {frozenset(pair) for pair in ("子未", "丑午", "寅巳", "卯辰", "申亥", "酉戌")}
SIX_BREAKS = {frozenset(pair) for pair in ("子酉", "卯午", "辰丑", "未戌", "寅亥", "巳申")}
THREE_COMBINATIONS = {
    frozenset("申子辰"): "水", frozenset("亥卯未"): "木",
    frozenset("寅午戌"): "火", frozenset("巳酉丑"): "金",
}
THREE_MEETINGS = {
    frozenset("亥子丑"): "水", frozenset("寅卯辰"): "木",
    frozenset("巳午未"): "火", frozenset("申酉戌"): "金",
}
```

Return `state="present"` for pair relations and complete punishment groups.
Return `state="active"` for complete three-combinations/meetings, but keep
`transformed_element=""` unless a later transformation rule proves it.
For incomplete groups, return no relation rather than inventing a half-result.
Preserve duplicate pillar positions in `pillar_names`.

- [ ] **Step 3: Run focused and interpretation tests**

- [ ] **Step 4: Commit**

Commit: `feat: detect conditional branch relations`.

## Phase 3: Strength

### Task 6: Implement Versioned Strength Configuration And Sensitivity

**Files:**
- Create: `src/mingli_engine/data/calculation/strength_weights.json`
- Create: `src/mingli_engine/bazi/strength.py`
- Test: `tests/unit/bazi/test_strength.py`

- [ ] **Step 1: Write failing configuration tests**

Reject missing version, unknown categories, non-numeric weights, negative
uncertainty, and thresholds that are not strictly ordered.

- [ ] **Step 2: Add the initial transparent profile**

```json
{
  "version": "ziping-strength-v1",
  "month_command": {
    "same_element": 30,
    "resource": 24,
    "output": -18,
    "wealth": -20,
    "officer": -24
  },
  "root": {"main": 18, "middle": 12, "residual": 6},
  "exposed": {"companion": 8, "resource": 7, "output": -7, "wealth": -8, "officer": -9},
  "hidden_factor": 0.5,
  "thresholds": {"weak": -25, "balanced_low": -10, "balanced_high": 10, "strong": 25},
  "sensitivity_fraction": 0.1
}
```

- [ ] **Step 3: Write failing strength behavior tests**

Use synthetic facts to prove:

- season and roots are separate contributions;
- a clearly supported chart is `偏强`;
- a clearly drained/controlled chart is `偏弱`;
- `[-10, 10]` is `较平衡`;
- crossing a classification boundary under plus/minus 10 percent sensitivity
  returns `indeterminate`;
- every contribution has a rule id.

- [ ] **Step 4: Implement `calculate_strength`**

Map each element relative to the day master into `companion`, `resource`,
`output`, `wealth`, or `officer`. Calculate a central score and recompute with
all configurable magnitudes at `0.9` and `1.1`. Use the central and sensitivity
labels to build `StrengthResult`; never collapse contributions into report
text inside this module.

- [ ] **Step 5: Run focused tests and the existing report regression tests**

- [ ] **Step 6: Commit**

Commit: `feat: calculate traceable day-master strength`.

## Phase 4: Patterns, Useful Gods, And Schools

### Task 7: Add Pattern Candidate, Damage, And Rescue Rules

**Files:**
- Create: `src/mingli_engine/bazi/patterns.py`
- Test: `tests/unit/bazi/test_patterns.py`
- Create: `tests/fixtures/bazi_calculation/pattern_counterexamples.json`

- [ ] **Step 1: Add failing formation and counterexample tests**

Cover exposed and latent month-command patterns, 建禄/月劫, 官见伤官,
杀见食神/印, 财见比劫, 印见财, 食神见偏印, and indeterminate strength.

- [ ] **Step 2: Implement named rule tables**

```python
TEN_GOD_PATTERN_NAMES = {
    "正官": "正官格", "七杀": "七杀格", "正财": "正财格", "偏财": "偏财格",
    "正印": "正印格", "偏印": "偏印格", "食神": "食神格", "伤官": "伤官格",
}
PATTERN_DAMAGE = {
    "正官格": ("伤官",), "七杀格": (), "正财格": ("比肩", "劫财"),
    "偏财格": ("比肩", "劫财"), "正印格": ("正财", "偏财"),
    "偏印格": ("正财", "偏财"), "食神格": ("偏印",), "伤官格": ("正官",),
}
PATTERN_RESCUE = {
    "正官格": ("正印", "偏印"), "七杀格": ("食神", "正印", "偏印"),
    "正财格": ("正官", "七杀", "食神", "伤官"),
    "偏财格": ("正官", "七杀", "食神", "伤官"),
    "正印格": ("比肩", "劫财", "正官", "七杀"),
    "偏印格": ("比肩", "劫财", "正官", "七杀"),
    "食神格": ("正财", "偏财"), "伤官格": ("正财", "偏财", "正印", "偏印"),
}
```

Month-command main hidden stem defines the first candidate. If it is exposed,
mark the formation signal; otherwise mark it latent. Day-master month branches
that map to 比肩/劫财 produce 建禄/月劫 candidates. A damaged candidate remains
visible with opposing signals; a matching rescue signal lowers, but does not
erase, the damage. If strength is `indeterminate`, all pattern conclusions are
`indeterminate`.

- [ ] **Step 3: Run pattern and strength tests**

- [ ] **Step 4: Commit**

Commit: `feat: derive guarded pattern candidates`.

### Task 8: Add Four Useful-God Candidate Methods

**Files:**
- Create: `src/mingli_engine/bazi/useful_gods.py`
- Test: `tests/unit/bazi/test_useful_gods.py`

- [ ] **Step 1: Write failing prerequisite and method tests**

Assert that incomplete strength blocks support/control; a strong chart favors
output/wealth/officer candidates; a weak chart favors resource/companion;
winter branches can nominate fire for seasonal adjustment, summer branches can
nominate water; mediation requires a detected controlling bottleneck; and
illness/remedy output stays low confidence.

- [ ] **Step 2: Implement exact method boundaries**

```python
WINTER_BRANCHES = frozenset({"亥", "子", "丑"})
SUMMER_BRANCHES = frozenset({"巳", "午", "未"})


def calculate_useful_god_candidates(
    facts: ChartFacts,
    strength: StrengthResult,
    patterns: tuple[PatternCandidateResult, ...],
) -> tuple[UsefulGodCandidateResult, ...]:
    if strength.reasoning.status != "computed":
        return (_blocked_candidate("support_control", "strength_not_computed"),)
    candidates = list(_support_control_candidates(facts, strength))
    candidates.extend(_seasonal_adjustment_candidates(facts))
    candidates.extend(_mediation_candidates(facts))
    candidates.extend(_illness_remedy_candidates(facts, strength, patterns))
    return _deduplicate_and_rank(candidates)
```

Define every helper in the same module with these exact responsibilities:

- `_blocked_candidate(method, reason)` returns one `not_computed` result with no
  nominated elements and the prerequisite reason in `reason_codes`.
- `_support_control_candidates(facts, strength)` maps strong charts to
  output/wealth/officer element candidates and weak charts to
  resource/companion candidates; borderline results remain `indeterminate`.
- `_seasonal_adjustment_candidates(facts)` nominates fire only for winter month
  branches and water only for summer month branches.
- `_mediation_candidates(facts)` returns a computed candidate only when
  `ChartFacts` exposes a controlling-cycle bottleneck; otherwise it returns a
  `not_computed` result.
- `_illness_remedy_candidates(facts, strength, patterns)` emits only low-
  confidence candidates and records the triggering excess or damaged pattern.
- `_deduplicate_and_rank(candidates)` deduplicates by `(method, element)`, keeps
  all disagreements, and sorts by status, confidence, method, then element.

Seasonal adjustment V1 makes no automatic spring/autumn choice. It returns a
`not_computed` seasonal candidate outside winter/summer instead of inventing a
universal rule. No method returns a unique final god.

- [ ] **Step 3: Run focused tests and formal-interpretation regressions**

- [ ] **Step 4: Commit**

Commit: `feat: add conditional useful-god methods`.

### Task 9: Implement School Adapter Isolation

**Files:**
- Create: `src/mingli_engine/data/calculation/school_profiles.json`
- Create: `src/mingli_engine/bazi/schools/base.py`
- Create: `src/mingli_engine/bazi/schools/ziping.py`
- Create: `src/mingli_engine/bazi/schools/liang_xiangrun.py`
- Create: `src/mingli_engine/bazi/schools/duan.py`
- Test: `tests/unit/bazi/test_school_adapters.py`

- [ ] **Step 1: Write failing protocol and isolation tests**

Prove that adapters receive immutable facts/results, identify their profile
version and rule ids, cannot change facts, and can disagree without deleting the
baseline candidate.

- [ ] **Step 2: Add validated profiles**

```json
{
  "version": "school-profiles-v1",
  "enabled": ["ziping", "liang_xiangrun", "duan"],
  "profiles": {
    "ziping": {"priority": 100, "method_order": ["support_control", "seasonal_adjustment", "mediation", "illness_remedy"]},
    "liang_xiangrun": {"priority": 80, "method_order": ["pattern_context", "seasonal_adjustment", "support_control"]},
    "duan": {"priority": 70, "method_order": ["structural_flow", "support_control", "pattern_context"]}
  }
}
```

- [ ] **Step 3: Define and implement the adapter protocol**

```python
from typing import Protocol


class SchoolAdapter(Protocol):
    school_id: str
    profile_version: str

    def interpret(
        self,
        *,
        facts: ChartFacts,
        strength: StrengthResult,
        patterns: tuple[PatternCandidateResult, ...],
        useful_gods: tuple[UsefulGodCandidateResult, ...],
    ) -> SchoolInterpretation: ...
```

Ziping preserves baseline rank. Liang prioritizes explicit pattern context and
seasonal adjustment only when those candidates are computed. Duan prioritizes
structural flow and requires conditions plus counterconditions. If reviewed
rules do not support a preference, the adapter returns `not_computed` rather
than hard-coded doctrine.

Add `load_enabled_school_adapters() -> tuple[SchoolAdapter, ...]` to validate
the JSON version, enabled ids, priorities, and method names. Add
`interpret_with_enabled_schools(...) -> tuple[SchoolInterpretation, ...]` to
call each enabled adapter in descending priority order and preserve every
adapter result, including disagreement and `not_computed` states.

- [ ] **Step 4: Run school, pattern, and useful-god tests**

- [ ] **Step 5: Commit**

Commit: `feat: isolate bazi school interpretations`.

## Phase 5: Luck Cycles

### Task 10: Expose Provider Luck Data And Build Luck Results

**Files:**
- Modify: `src/mingli_engine/calendar_provider.py`
- Create: `src/mingli_engine/bazi/luck_cycles.py`
- Test: `tests/unit/bazi/test_luck_cycles.py`
- Create: `tests/fixtures/bazi_calculation/luck_cycle_boundary_cases.json`

- [ ] **Step 1: Write failing direction and start-time tests**

Cover yang-year male/yin-year female forward, yin-year male/yang-year female
reverse, unsupported gender, exact solar-term boundaries, and the existing
verified chart. Compare output to manually recorded `lunar-python` values.

- [ ] **Step 2: Add a provider DTO and function**

```python
@dataclass(frozen=True)
class ProviderLuckCycle:
    forward: bool
    start_years: int
    start_months: int
    start_days: int
    start_hours: int
    start_solar: str
    pillars: tuple[tuple[int, str, int, int, int, int], ...]


def calculate_provider_luck_cycles(
    birth_datetime: datetime,
    gender: str,
    *,
    sect: int = 1,
    count: int = 8,
) -> ProviderLuckCycle:
    gender_value = {"male": 1, "男": 1, "female": 0, "女": 0}.get(gender.strip().lower())
    if gender_value is None:
        raise ValueError("gender must be male/female or 男/女 for luck-cycle calculation")
    eight_char = Solar.fromYmdHms(
        birth_datetime.year,
        birth_datetime.month,
        birth_datetime.day,
        birth_datetime.hour,
        birth_datetime.minute,
        birth_datetime.second,
    ).getLunar().getEightChar()
    yun = eight_char.getYun(gender_value, sect)
    da_yun = tuple(
        (item.getIndex(), item.getGanZhi(), item.getStartYear(), item.getEndYear(), item.getStartAge(), item.getEndAge())
        for item in yun.getDaYun(count + 1)
        if item.getIndex() > 0
    )
    return ProviderLuckCycle(
        forward=yun.isForward(),
        start_years=yun.getStartYear(),
        start_months=yun.getStartMonth(),
        start_days=yun.getStartDay(),
        start_hours=yun.getStartHour(),
        start_solar=yun.getStartSolar().toYmdHms(),
        pillars=da_yun,
    )
```

- [ ] **Step 3: Implement `calculate_luck_cycles`**

Map provider pillars into immutable `LuckPillar` records. For an optional
selected Gregorian year, calculate its stem/branch through `lunar-python` and
reuse `detect_branch_relations` against natal and active-luck branches. Keep
the conclusion structural: list relations and activated positions, never event
predictions.

- [ ] **Step 4: Run calendar, chart, and luck tests**

- [ ] **Step 5: Commit**

Commit: `feat: calculate start and bazi luck cycles`.

## Phase 6: Orchestration, Reports, And Calibration

### Task 11: Build The Calculation Bundle Orchestrator

**Files:**
- Create: `src/mingli_engine/bazi/analysis.py`
- Create: `src/mingli_engine/bazi/legacy_adapter.py`
- Modify: `src/mingli_engine/chart_calculator.py`
- Test: `tests/integration/test_bazi_analysis_pipeline.py`

- [ ] **Step 1: Write a failing end-to-end calculation test**

Assert stage order, version fields, immutable output, no personal-data write,
and prerequisite degradation using both a complete and unsupported-gender
profile.

- [ ] **Step 2: Implement orchestration with no circular imports**

```python
ENGINE_VERSION = "bazi-core-v1"
RULESET_VERSION = "ziping-v1"


def analyze_bazi_chart(
    chart: BaziChart,
    *,
    birth_datetime: datetime | None = None,
    selected_year: int | None = None,
) -> CalculationBundle:
    facts = build_chart_facts(chart)
    relations = detect_branch_relations(chart)
    strength = calculate_strength(facts, relations)
    patterns = calculate_pattern_candidates(facts, strength, relations)
    useful_gods = calculate_useful_god_candidates(facts, strength, patterns)
    luck = calculate_luck_cycles(chart, birth_datetime=birth_datetime, selected_year=selected_year)
    schools = interpret_with_enabled_schools(facts, strength, patterns, useful_gods)
    return CalculationBundle(
        engine_version=ENGINE_VERSION,
        ruleset_version=RULESET_VERSION,
        facts=facts,
        branch_relations=relations,
        strength=strength,
        patterns=patterns,
        useful_gods=useful_gods,
        luck_cycles=luck,
        schools=schools,
    )
```

- [ ] **Step 3: Implement a one-way legacy adapter**

`apply_calculation_bundle(chart, bundle) -> BaziChart` uses `dataclasses.replace`
to populate legacy summary fields for existing consumers. Prefix every adapted
summary with a machine-readable state token such as
`[calculation_status=computed]`. New modules must never read those adapted text
fields back into calculations.

Also implement
`build_legacy_not_computed_bundle(chart) -> CalculationBundle`. It preserves
only chart facts that can be reconstructed losslessly and marks strength,
patterns, useful gods, luck cycles, and school interpretations as
`not_computed` with reason code `legacy_report_without_calculation_bundle`.
Task 12 uses this helper when callers omit the new calculation argument.

- [ ] **Step 4: Run pipeline and all existing chart/report tests**

- [ ] **Step 5: Commit**

Commit: `feat: orchestrate versioned bazi inference`.

### Task 12: Integrate CalculationBundle With Formal Evidence

**Files:**
- Modify: `src/mingli_engine/formal_interpretation.py`
- Modify: `src/mingli_engine/report_schema.py`
- Test: `tests/unit/test_formal_interpretation.py`
- Test: `tests/unit/test_report_schema.py`
- Test: `tests/integration/test_reasoned_report_pipeline.py`

- [ ] **Step 1: Write failing separation tests**

For each formal rule family assert distinct fields for calculation status,
evidence count, interpretation status, and confidence. Prove that evidence with
`not_computed` calculation cannot become `candidate`; prove computed results
with evidence can become `candidate`; prove a school disagreement becomes
`disputed` without deleting either view.

- [ ] **Step 2: Extend the report construction API**

```python
def build_report(
    chart: BaziChart,
    calculation: CalculationBundle | None = None,
) -> Report:
    calculation = calculation or build_legacy_not_computed_bundle(chart)
```

Map each rule family to the corresponding reasoned result. Preserve evidence
ids and conflicts from the existing corpus. Formal conclusion strength is
derived from both dimensions:

```python
if calculation_status == "not_computed":
    strength = "weakly_supported" if evidence_ids else "unavailable"
elif calculation_status == "indeterminate":
    strength = "weakly_supported"
elif calculation_status == "disputed" or has_open_severe_conflict:
    strength = "disputed"
else:
    strength = "candidate" if evidence_ids else "unavailable"
```

- [ ] **Step 3: Add report evidence-audit checks for status separation**

The audit must count computed, indeterminate, disputed, and not-computed rule
families independently from enabled evidence families.

- [ ] **Step 4: Run formal, report, integration, and safety tests**

- [ ] **Step 5: Commit**

Commit: `feat: connect bazi calculations to formal evidence`.

### Task 13: Update Markdown, HTML, And CLI Output

**Files:**
- Modify: `src/mingli_engine/markdown.py`
- Modify: `src/mingli_engine/html.py`
- Modify: `src/mingli_engine/cli.py`
- Test: `tests/unit/test_markdown_renderer.py`
- Test: `tests/unit/test_html_renderer.py`
- Test: `tests/contract/test_auto_chart_cli_contract.py`
- Test: `tests/integration/test_calculate_report_cli.py`

- [ ] **Step 1: Add failing renderer tests for the five visible dimensions**

Require sections for chart facts, calculation result, school views, evidence
basis, and interpretation/safety boundary. Require status labels in both
Markdown and HTML. Require HTML escaping for school and rule text.

- [ ] **Step 2: Extend CLI JSON without breaking existing fields**

Add an opt-in `--analysis` flag to `calculate-chart` and `calculate-report`.
Without the flag, retain current output during migration. With the flag,
serialize `CalculationBundle` under a top-level `calculation` key for chart JSON
and use it in report generation.

- [ ] **Step 3: Render reasoned details compactly**

Each conclusion displays status, confidence, supporting signals, opposing
signals, rule ids, evidence ids, assumptions, and missing inputs. Do not print
weight configuration or internal Python representations directly.

- [ ] **Step 4: Run renderer, CLI contract, integration, and safety tests**

- [ ] **Step 5: Commit**

Commit: `feat: render reasoned bazi analysis`.

### Task 14: Build Verified And Boundary Fixture Sets

**Files:**
- Create: `tests/fixtures/bazi_calculation/verified_charts.json`
- Create: `tests/fixtures/bazi_calculation/strength_boundary_cases.json`
- Expand: `tests/fixtures/bazi_calculation/pattern_counterexamples.json`
- Expand: `tests/fixtures/bazi_calculation/luck_cycle_boundary_cases.json`
- Test: `tests/integration/test_bazi_analysis_pipeline.py`

- [ ] **Step 1: Define the privacy-safe fixture schema**

```json
{
  "case_id": "verified_001",
  "input": {
    "calendar_type": "gregorian",
    "birth_date": "1992-08-16",
    "birth_time": "09:30",
    "birthplace": "UTC+08 test fixture",
    "gender": "male",
    "focus_topic": "structure review"
  },
  "ruleset_version": "ziping-v1",
  "expected_facts": {},
  "expected_relations": [],
  "expected_strength": {},
  "expected_patterns": [],
  "expected_luck": {},
  "verification": {
    "chart_source": "independently checked fixture",
    "review_status": "reviewed",
    "contains_real_personal_data": false
  }
}
```

- [ ] **Step 2: Add at least 30 verified chart cases**

Cover all day-master elements and polarities, all month branches, forward and
reverse luck directions, repeated branches, and no-relation charts. Values must
be independently checked before marking `reviewed`.

- [ ] **Step 3: Add at least 20 boundary/counterexample cases**

Cover near-threshold strength, latent versus exposed patterns, damaged and
rescued patterns, incomplete three-groups, school disagreement, solar-term
boundaries, unknown gender, and unsupported time assumptions.

- [ ] **Step 4: Parameterize the integration tests over all fixtures**

Assert exact facts and statuses, but only assert numeric strength ranges where
the fixture is intended as a sensitivity case.

- [ ] **Step 5: Commit**

Commit: `test: add verified bazi calculation fixtures`.

### Task 15: Extend Acceptance, Release, And Completion Gates

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/report_acceptance.py`
- Modify: `src/mingli_engine/report_release.py`
- Modify: `src/mingli_engine/project_completion.py`
- Modify: `tests/unit/test_report_acceptance.py`
- Modify: `tests/unit/test_report_release.py`
- Modify: `tests/unit/test_project_completion.py`
- Modify: `tests/contract/test_project_completion_cli_contract.py`
- Modify: `docs/classical_sources/README.md`

- [ ] **Step 1: Add failing gate tests**

Require:

- all calculation stages present;
- no placeholder upgraded to computed;
- 30 verified and 20 boundary fixtures;
- three school profiles loaded;
- evidence/calculation separation complete;
- current high-risk guardrails preserved;
- no persisted birth-profile or report artifacts.

- [ ] **Step 2: Extend the existing summary model minimally**

Append `calculation_checks: dict[str, str]` to `ProjectCompletionSummary` in
`models.py`, populate it in `build_project_completion_summary`, and serialize
it as a new top-level CLI JSON key. Do not add another family of generic
dataclasses. Existing keys and meanings remain unchanged.

- [ ] **Step 3: Update the maintainer documentation**

Document the calculation/evidence boundary, `--analysis` usage, ruleset
versions, fixture review process, and explicit V1 exclusions. Do not describe
the engine as scientifically predictive or as a full domain-report system.

- [ ] **Step 4: Run all 964 legacy tests plus new tests**

Run:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest -q -p no:cacheprovider
```

Expected: all legacy and new tests pass. Because the suite currently takes
longer than three minutes, use a command timeout of at least ten minutes.

- [ ] **Step 5: Run the read-only release commands**

```powershell
python -m mingli_engine.cli knowledge-activation-summary
python -m mingli_engine.cli report-acceptance-summary
python -m mingli_engine.cli report-release-summary
python -m mingli_engine.cli project-completion-summary
```

Expected final statuses:

- knowledge activation: `enabled_with_guardrails` or stricter;
- acceptance: `ready_with_guardrails` or stricter;
- release: `ready_with_guardrails` or stricter;
- project completion: `complete_with_guardrails` or stricter;
- calculation gate: all required V1 checks pass.

- [ ] **Step 6: Verify scope and repository cleanliness**

Run `git diff --check`, inspect `git status --short`, and confirm no files under
raw-material roots changed and no personal report/profile artifact was created.

- [ ] **Step 7: Commit**

```powershell
git add src/mingli_engine tests docs/classical_sources/README.md
git commit -m "feat: complete bazi core inference engine v1"
```

## Long-Goal Checkpoints

The goal remains `018-bazi-core-inference-engine-v1` throughout execution.
Report these checkpoints without closing the goal:

1. `018-A`: state protocol and evidence separation complete;
2. `018-B`: structural facts and branch relations complete;
3. `018-C`: strength calculation complete;
4. `018-D`: patterns, useful gods, and school adapters complete;
5. `018-E`: luck cycles complete;
6. `018-F`: reports, fixtures, and release gates complete.

Mark the long goal complete only after Task 15 passes. At each checkpoint, tell
the user the next checkpoint explicitly. If a rule cannot be validated, return
an explicit degraded result and continue with independent tasks; do not invent
the missing rule to satisfy the schedule.
