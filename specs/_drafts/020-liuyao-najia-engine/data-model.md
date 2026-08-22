# Data Model: Liuyao Najia Calculation Engine V1

**Date**: 2026-08-19 | **Feature**: specs/020-liuyao-najia-engine

All models are frozen dataclasses with strict validation in `__post_init__`, mirroring the bazi engine's immutable style. JSON field names are snake_case and stable within V1.

## Input Models

### LiuyaoLineInput

| Field | Type | Rule |
|---|---|---|
| `position` | int | 1-6, bottom-up （初爻..上爻） |
| `yin_yang` | str | `"yang"` or `"yin"` |
| `moving` | bool | exactly 0-6 moving lines per chart |

### LiuyaoCastRequest

| Field | Type | Rule |
|---|---|---|
| `cast_mode` | str | `"explicit"`, `"time"`, or `"number"` |
| `lines` | tuple[LiuyaoLineInput, ...] | required and exactly 6 when `cast_mode == "explicit"`; empty otherwise |
| `cast_datetime` | str | ISO `YYYY-MM-DDTHH:MM` Gregorian; required for `"explicit"` and `"time"`; range 1901-01-01..2099-12-31 |
| `numbers` | tuple[int, ...] | exactly 2 positive integers when `cast_mode == "number"`; empty otherwise |
| `request_id` | str \| None | optional caller label, never persisted |

Validation rejects: wrong line count, out-of-range positions, duplicate positions, missing/extra fields per mode, out-of-range dates, malformed timestamps.

## Chart Models

### TrigramInfo

| Field | Type | Rule |
|---|---|---|
| `name` | str | one of 乾 兑 离 震 巽 坎 艮 坤 |
| `symbol_lines` | tuple[int, ...] | three line values bottom-up, 1=yang 0=yin |
| `element` | str | one of 金 木 水 火 土 |
| `xiantian_index` | int | 1-8 per the 先天 sequence |

### GuaInfo (static reference, from `gua_reference.json`)

| Field | Type | Rule |
|---|---|---|
| `gua_name` | str | e.g. 火天大有 |
| `upper_trigram` / `lower_trigram` | str | trigram names |
| `palace` | str | one of the eight palaces |
| `palace_sequence` | int | 0-7 （本宫/一世…归魂） |
| `shi_position` | int | 1-6, derived from sequence |
| `ying_position` | int | `shi_position ± 3` |

### LiuyaoLine

| Field | Type | Rule |
|---|---|---|
| `position` | int | 1-6 |
| `yin_yang` | str | `"yang"` / `"yin"` |
| `moving` | bool | |
| `ganzhi` | str | najia assignment, e.g. 甲子 |
| `element` | str | branch element |
| `six_relation` | str | one of 父母 兄弟 官鬼 妻财 子孙 (relative to palace element) |
| `six_spirit` | str | one of 青龙 朱雀 勾陈 螣蛇 白虎 玄武 |
| `shi_ying` | str | `"shi"`, `"ying"`, or `""` |
| `hidden_spirit` | HiddenSpirit \| None | present only when a relation is absent from the six lines |
| `void` | bool | day-xun void |
| `month_break` | bool | branch opposes month command |
| `day_break` | bool | branch clashes day branch (weakened marker) |

### HiddenSpirit

| Field | Type | Rule |
|---|---|---|
| `ganzhi` | str | borrowed from palace head gua |
| `six_relation` | str | the absent relation |
| `attached_position` | int | line position it hides under |

### LiuyaoChart

| Field | Type | Rule |
|---|---|---|
| `cast_mode` | str | input mode actually used |
| `cast_datetime` | str | normalized timestamp |
| `ben_gua` | GuaInfo | original chart |
| `bian_gua` | GuaInfo \| None | changed chart, None when no moving lines |
| `hu_gua` | GuaInfo | nuclear chart (lines 2-3-4 lower, 3-4-5 upper) |
| `lines` | tuple[LiuyaoLine, ...] | exactly 6, ordered by position |
| `month_command` | str | month branch from solar terms |
| `day_ganzhi` | str | day stem-branch |
| `xun_void_branches` | tuple[str, ...] | the two day-xun void branches |
| `assumptions` | tuple[str, ...] | documented calendar assumptions |

Determinism rule: identical request ⇒ identical chart, byte-exact.

## Analysis Models

### LiuyaoFamilyObservation

| Field | Type | Rule |
|---|---|---|
| `rule_family` | str | one of the eight `LIUYAO_RULE_FAMILIES` |
| `status` | str | `"computed"`, `"degraded"`, or `"not_computed"` |
| `headline` | str | short neutral headline |
| `observations` | tuple[str, ...] | bounded observation lines, no absolute wording |
| `limitations` | tuple[str, ...] | at least one limitation per family |
| `evidence_note` | str | evidence-present or evidence-pending wording |

### LiuyaoAnalysis

| Field | Type | Rule |
|---|---|---|
| `chart` | LiuyaoChart | |
| `family_observations` | tuple[LiuyaoFamilyObservation, ...] | exactly 8, one per family, fixed order |
| `safety_review` | SafetyReviewResult | reused bazi classifier result |
| `high_risk_review` | HighRiskReview | reused bazi classifier result |

## Report Model

### LiuyaoReport

| Field | Type | Rule |
|---|---|---|
| `title` | str | fixed V1 title |
| `disclaimer` | str | mandatory non-absolute disclaimer |
| `chart_summary` | tuple[str, ...] | human-readable assembly lines |
| `family_sections` | tuple[LiuyaoFamilyObservation, ...] | from analysis |
| `boundary_notes` | tuple[str, ...] | high-risk narrowing / refusal notes |
| `safety_review` | SafetyReviewResult | |

Renderer: `report_markdown.py` produces a deterministic Markdown document with sections 免责声明 / 起卦信息 / 装卦 / 逐爻明细 / 各族观察 / 边界说明. No HTML in V1.

## Reference Data

### `data/liuyao/gua_reference.json`

Frozen structural reference for all 64 gua: `gua_name`, `upper_trigram`, `lower_trigram`, `palace`, `palace_sequence`. Generated programmatically from trigram rules, validated by golden tests, and loaded read-only through `resources.files`.

### `data/liuyao/analysis_config.json`

Governed analysis configuration: the eight families (fixed order), per-family headline templates, evidence-pending wording, and prohibited-wording list reuse (no absolute wording).
