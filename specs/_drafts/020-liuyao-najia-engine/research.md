# Phase 0 Research: Liuyao Najia Calculation Engine V1

**Date**: 2026-08-19 | **Feature**: specs/020-liuyao-najia-engine

## R1: 64-Gua Najia Table Construction

**Decision**: Derive the complete 64-gua najia data (per-line ganzhi, element, palace, sequence) programmatically from first-principle rules, and freeze the derived output with golden test vectors from classical reference charts.

**Rationale**: The trigram najia assignments are fixed classical constants （乾内甲子外壬午、坎内戊寅外戊申、艮内丙辰外丙戌、震内庚子外庚午、巽内辛丑外辛未、离内己卯外己酉、坤内乙未外癸丑、兑内丁巳外丁亥）, and palace membership plus sequence fully determine every derived field. Programmatic derivation from eight trigram rules eliminates transcription errors; golden vectors （火天大有、水山蹇、天风姤 等文献可考卦例） independently confirm correctness.

**Alternatives considered**: Hand-typing a 384-cell table — rejected: high transcription risk and unverifiable provenance.

## R2: Shi/Ying Positions and Palace Sequence

**Decision**: Adopt the 京房八宫 sequence: 本宫（世六）、一世（世初）、二世、三世、四世、五世、游魂（世四）、归魂（世三）; 应爻 is always three positions away from 世爻. Each of the 64 gua belongs to exactly one of the eight palaces with a sequence index 0-7.

**Rationale**: This is the universally used najia convention, consistent across the batch sources （断易天机、易隐、易冒） and the modern textbook.

**Alternatives considered**: none — no competing convention is in scope for V1.

## R3: Hidden Spirits (伏神)

**Decision**: When a gua's six-relation set is incomplete (palace element relation missing among the six lines), the missing relation's hidden spirit is borrowed from the corresponding line of the palace head gua （本宫首卦）, attached under the matching line position.

**Rationale**: Standard najia rule; needed for complete six-relation analysis.

## R4: Six Spirits (六神)

**Decision**: Six spirits are assigned bottom-up starting from the spirit determined by the day stem: 甲乙日起青龙、丙丁日朱雀、戊日勾陈、己日螣蛇、庚辛日白虎、壬癸日玄武； order fixed as 青龙→朱雀→勾陈→螣蛇→白虎→玄武.

**Rationale**: Universal convention; day stem comes from the existing calendar provider, no new dependency.

## R5: Casting Modes

**Decision**: Three input modes resolve to one canonical six-line model:

1. **Explicit lines**: six lines with yin/yang and moving flags; the trust root (no randomness in the engine).
2. **Time casting**: upper gua = (lunar year branch index + lunar month + lunar day) mod 8, lower gua = (same + hour branch index) mod 8, moving line = total mod 6; remainder 0 maps to 8 or 6 respectively.
3. **Number casting**: upper = first number mod 8, lower = second number mod 8, moving = (first + second) mod 6; same zero mapping.

**Rationale**: The numeric conversion is the widely documented plum-blossom method for obtaining lines; V1 explicitly documents that lines obtained this way are then analyzed with the najia assembly — a declared, reviewable assumption rather than a claim that this is the only classical conversion. Trigram index mapping follows the 先天 sequence （乾1 兑2 离3 震4 巽5 坎6 艮7 坤8).

**Alternatives considered**: coin-toss simulation — rejected (engine never simulates randomness); multiple competing time-casting rules — rejected (one documented rule keeps calibration exact).

## R6: Calendar Bridge

**Decision**: Reuse `calendar_provider` for solar-term month-command (月建), day ganzhi (日辰), and lunar-python for lunar date fields needed by time casting. Document the same UTC+08 wall-time, no-true-solar-time assumption and 1901-2099 range as the bazi engine. 空亡 is computed from the day ganzhi's xun (旬); 月破 is the branch opposing the month command; 日破 requires day-branch clash assessment against line branches.

**Rationale**: Zero new calendar code; identical documented assumptions keep cross-engine consistency auditable.

## R7: Independent Rule-Family Namespace

**Decision**: Define `LIUYAO_RULE_FAMILIES` with eight families in a separate module and data namespace: `yong_shen_selection`, `shi_ying_relation`, `moving_line_dynamics`, `six_spirits_attachment`, `month_day_strength`, `void_break_state`, `yingqi_timing`, `category_judgment`.

**Rationale**: Spec FR-4 requires zero disturbance to bazi chains; a separate namespace guarantees bazi validators, knowledge activation, and the 019 calibration baseline are bit-identical after liuyao ships.

**Alternatives considered**: extending the shared `RULE_FAMILIES` enum — rejected: perturbs frozen baselines and report activation logic.

## R8: Boundary and Report Safety

**Decision**: Reuse `safety_check` and `classify_high_risk_request` on every analysis/report output; the liuyao report carries the same disclaimer family, uncertainty wording, and high-risk refusal/narrowing behavior as the bazi report, plus the explicit statement that content is traditional cultural interpretation, not prediction.

**Rationale**: One classifier pair, one boundary contract — no parallel safety stack to drift.

## R9: Application Boundary (V1)

**Decision**: V1 exposes a typed Python API plus additive CLI subcommands (`liuyao-calculate`, `liuyao-report`) following the `calculate-chart`/`calculate-report` pattern with bounded JSON input. A strict frozen JSON envelope (like `real-use`) is deferred to the calibration stage.

**Rationale**: Matches the spec's FR-10 while keeping V1 minimal; the bazi feature followed the same evolution.

## R10: Knowledge Promotion Sequencing

**Decision**: V1 analysis degrades gracefully with explicit "evidence not yet promoted" wording when the liuyao evidence namespace is empty; promotion of the 101 extracted liuyao candidates (and later the two supplement books) is a separate governed stage inside this feature that reuses the batch_20260714 pipeline contracts with a liuyao family map.

**Rationale**: The owner chose "existing materials first, supplement books later"; structural analysis must be shippable before evidence promotion to keep the critical path testable.
