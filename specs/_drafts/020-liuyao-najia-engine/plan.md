# Implementation Plan: Liuyao Najia Calculation Engine V1

**Branch**: `020-liuyao-najia-engine` | **Date**: 2026-08-19 | **Spec**: [spec.md](spec.md)

**Input**: Owner-approved scope: najia-only method, three casting modes (explicit lines, time casting, number casting), independent rule-family namespace, reuse extracted batch candidates first and supplement 《增删卜易》《卜筮正宗》 later.

## Summary

Build a deterministic, fully offline najia (六爻纳甲) calculation engine as a sibling package to the existing bazi core: explicit six-line input, time casting, and number casting all resolve to one canonical `LiuyaoChart`; a najia assembly layer computes palace, ganzhi, six-relations, shi/ying, hidden spirits, six spirits, month-command/day-hour states (kong, po); an analysis layer produces governed rule-family observations; and a boundary-guarded report layer mirrors the bazi report's disclaimer, weakening, and high-risk refusal behavior. The 64-gua najia tables are derived programmatically from first-principle trigram/palace rules and frozen by golden test vectors rather than hand-transcribed. Knowledge promotion and calibration reuse the proven batch_20260714 pipeline patterns in a separate liuyao namespace so every bazi chain, calibration baseline, and report remains bit-identical.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Python standard library, existing `mingli_engine` modules (`calendar_provider` for solar terms/day ganzhi, `safety`, `high_risk`, plain-language helpers), `lunar-python==1.4.8` for lunar-date conversion in time casting; no HTTP, UI, database, or new runtime service.

**Storage**: Tracked canonical JSON reference tables under `src/mingli_engine/data/liuyao/`; no engine-managed persistence of requests, charts, or reports.

**Testing**: pytest 8.4.1, mypy 1.17.1, Ruff 0.12.11; golden vectors from classical reference charts; full-suite and focused gates.

**Target Platform**: Local Python library and CLI, Windows first and portable.

**Project Type**: Python library and CLI package.

**Performance Goals**: Chart assembly is O(64-entry) table work; no measurable performance concern. Casting and analysis stay strictly deterministic and allocation-light.

**Constraints**: Gregorian dates 1901-01-01 through 2099-12-31; documented UTC+08 wall-time assumption; no true solar time; no random simulation of the tossing process; no persistence of inputs or outputs; no scientific or predictive claims; high-risk topics refused or narrowed.

**Scale/Scope**: V1 ships explicit-line + time + number casting, full najia assembly, 8 independent liuyao rule families (structural analysis with graceful degradation before evidence promotion), boundary-guarded Markdown report, and golden-vector tests. Evidence promotion from extracted batch candidates and the calibration corpus follow as separate governed stages inside this feature.

## Constitution Check

*GATE: Must pass before Phase 0 research and be re-checked after Phase 1 design.*

- Evidence-based traditional analysis: PASS. All interpretive outputs are framed as traditional-method observations with rule-family, strength, limitation, and uncertainty wording; no absolute wording （必定/注定/一定会/死定） is permitted anywhere.
- Transparent calculation and evidence boundary: PASS. Casting inputs, calendar assumptions (UTC+08, no true solar time), conversion rules, and every assembled field are explicit and independently recomputable.
- Expanded high-risk boundaries: PASS. The existing safety/high-risk classifiers gate every report; lifespan, death-timing, medical, legal, psychological, investment, and coercive requests are refused or narrowed exactly as in the bazi boundary.
- Reviewable classical evidence and reports: PASS. Assembly fields trace to frozen reference tables; analysis conclusions degrade explicitly when evidence is absent; promoted knowledge later carries source locators.
- Test-first quality gates: PASS. Every phase starts with failing tests (golden vectors, boundary, determinism, refusal), and closes with pytest, mypy, and Ruff.
- Privacy: PASS. No persistence of casting inputs or reports; calibration uses only synthetic cases.

## Project Structure

### Documentation (this feature)

```text
specs/020-liuyao-najia-engine/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── liuyao-v1-contract.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/mingli_engine/
├── liuyao/
│   ├── __init__.py          # public API re-exports
│   ├── constants.py         # trigram/gua/najia primitives and enums
│   ├── result_models.py     # frozen dataclasses for chart and analysis
│   ├── casting.py           # explicit/time/number casting → six lines
│   ├── najia.py             # palace assembly: ganzhi, relations, shi/ying, hidden, spirits
│   ├── calendar_bridge.py   # month-command/day-hour states via calendar_provider
│   ├── analysis.py          # governed rule-family observations
│   ├── report.py            # report model + boundary checks
│   └── report_markdown.py   # Markdown renderer
├── data/liuyao/
│   ├── gua_reference.json   # frozen 64-gua structural reference (names, palaces, sequence)
│   └── analysis_config.json # governed family enablement and wording boundaries
├── cli.py                   # add liuyao-calculate / liuyao-report commands
tests/
├── unit/test_liuyao_*.py
├── integration/test_liuyao_cli.py
└── fixtures/liuyao/
```

**Structure Decision**: A new `liuyao` subpackage keeps the bazi engine untouched; reference tables live in tracked JSON so installed wheels carry them through the existing package-data rules; CLI gains additive subcommands following the established `calculate-chart`/`calculate-report` pattern.

## Complexity Tracking

No constitution violations. A separate subpackage and separate rule-family namespace are required precisely to satisfy the "zero disturbance to bazi chains and calibration" constraint; merging into the bazi modules was rejected because it would perturb the frozen 019 baselines.

## Phase 0: Research Summary

Research decisions are documented in [research.md](research.md):

- Derive the 64-gua najia tables programmatically from trigram-najia and palace rules; freeze with golden vectors instead of hand transcription.
- Adopt the 京房八宫 sequence （本宫/一至五世/游魂/归魂） for shi/ying; hidden spirits borrow from the palace head gua when a six-relation is absent.
- Six spirits start by day stem （甲乙青龙…壬癸玄武） from the bottom line upward.
- Time and number casting use the documented plum-blossom numeric conversion to obtain lines, then analyze with najia — an explicitly documented assumption, not a claim of classical uniqueness.
- Reuse `calendar_provider` for month-command and day ganzhi; reuse safety/high-risk classifiers for every output.
- Independent `LIUYAO_RULE_FAMILIES` namespace with eight families; bazi chains remain bit-identical.

## Phase 1: Design Summary

Detailed models, the CLI/JSON contract, and the operator workflow are defined in:

- [data-model.md](data-model.md)
- [contracts/liuyao-v1-contract.md](contracts/liuyao-v1-contract.md)
- [quickstart.md](quickstart.md)

## Release Gates (V1)

- Golden vectors: at least 20 classical reference charts pass field-exact assembly (100%).
- Determinism: identical inputs produce byte-identical outputs across 20 repetitions for all three casting modes.
- Boundary: high-risk refusal/narrowing 100%; zero absolute-wording occurrences in generated reports; disclaimer always present.
- Privacy: no-write verification for casting/report paths.
- Zero disturbance: every pre-existing test, the bazi knowledge chains, and the 019 calibration baseline remain unchanged.
- Focused mypy/Ruff clean; full pytest suite passes.

## Verification Commands

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_liuyao_constants.py tests/unit/test_liuyao_casting.py tests/unit/test_liuyao_najia.py tests/unit/test_liuyao_analysis.py tests/unit/test_liuyao_report.py tests/integration/test_liuyao_cli.py -q -p no:cacheprovider
uv run --frozen --with mypy==1.17.1 python -m mypy src/mingli_engine/liuyao --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check src/mingli_engine/liuyao tests/unit/test_liuyao_constants.py tests/unit/test_liuyao_casting.py tests/unit/test_liuyao_najia.py tests/unit/test_liuyao_analysis.py tests/unit/test_liuyao_report.py tests/integration/test_liuyao_cli.py
uv run --frozen --with pytest==8.4.1 python -m pytest -m "not task8_post_audit" -q -p no:cacheprovider
git diff --check
```

## Post-Design Constitution Check

- Evidence-based traditional analysis: PASS. Data model and contract keep every conclusion family-scoped, strength-labeled, and limitation-bound.
- Transparent calculation and evidence boundary: PASS. Casting conversion rules, calendar assumptions, and every assembled field are documented and independently recomputable.
- Expanded high-risk boundaries: PASS. The reused classifier pair plus the report error contract guarantee refusal or narrowing before any output.
- Reviewable classical evidence and reports: PASS. Golden vectors, frozen reference tables, and evidence-pending degradation wording preserve a complete audit path.
- Test-first quality gates: PASS. The plan's release gates are all test-enforced (vectors, determinism, boundary, privacy, zero-disturbance).
- Privacy: PASS. The contract forbids persistence; synthetic-only calibration is reserved for the later stage.
