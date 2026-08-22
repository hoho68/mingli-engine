# Contract: Liuyao V1 CLI and JSON Boundary

**Date**: 2026-08-19 | **Feature**: specs/020-liuyao-najia-engine

## Commands

### `mingli-engine liuyao-calculate --input <json-file>`

Reads a bounded JSON cast request (≤ 32 KiB, depth ≤ 8), assembles the chart, and prints the chart JSON to stdout.

### `mingli-engine liuyao-report --input <json-file>`

Reads the same request, assembles and analyzes the chart, and prints the deterministic Markdown report to stdout.

Both commands:

- exit 0 on success with stdout payload only;
- exit 1 with a single stderr line `Liuyao error: <reason>` on any validation, safety, or boundary failure;
- never write, cache, or log request or report content;
- accept `--pretty` to pretty-print chart JSON (report stays canonical Markdown).

## Request JSON Schema (V1)

```json
{
  "cast_mode": "explicit | time | number",
  "cast_datetime": "YYYY-MM-DDTHH:MM",
  "lines": [
    {"position": 1, "yin_yang": "yang", "moving": false}
  ],
  "numbers": [7, 9],
  "request_id": null
}
```

Mode-specific rules:

- `explicit`: `lines` required with exactly six unique positions 1-6; `numbers` must be absent; `cast_datetime` required.
- `time`: `lines` must be absent; `cast_datetime` required; `numbers` must be absent.
- `number`: `numbers` required with exactly two positive integers; `lines` must be absent; `cast_datetime` required (used for month/day states and six spirits).

Unknown fields, wrong types, out-of-range values, and mode/field mismatches are rejected before any computation. `request_id` is echoed in the chart JSON but never persisted.

## Chart JSON Response (V1)

```json
{
  "cast_mode": "explicit",
  "cast_datetime": "1990-01-01T08:30",
  "request_id": null,
  "ben_gua": {"gua_name": "火天大有", "upper_trigram": "离", "lower_trigram": "乾", "palace": "乾", "palace_sequence": 7, "shi_position": 3, "ying_position": 6},
  "bian_gua": null,
  "hu_gua": {"gua_name": "泽天夬", "upper_trigram": "兑", "lower_trigram": "乾", "palace": "坤", "palace_sequence": 5, "shi_position": 4, "ying_position": 1},
  "month_command": "丑",
  "day_ganzhi": "丙寅",
  "xun_void_branches": ["戌", "亥"],
  "lines": [
    {"position": 1, "yin_yang": "yang", "moving": false, "ganzhi": "甲子", "element": "水", "six_relation": "父母", "six_spirit": "青龙", "shi_ying": "", "hidden_spirit": null, "void": false, "month_break": false, "day_break": false}
  ],
  "assumptions": ["gregorian_utc_plus_8_wall_time", "no_true_solar_time", "plum_blossom_numeric_casting_documented"]
}
```

Field notes:

- `lines` always contains exactly six entries ordered by `position` ascending.
- `bian_gua` is `null` when no line is moving; `hu_gua` is always present.
- `hidden_spirit` is `null` except on lines that carry a borrowed hidden spirit, where it contains `{"ganzhi": "...", "six_relation": "...", "attached_position": n}`.

## Report Contract (V1)

- Deterministic Markdown; identical requests produce byte-identical documents.
- Sections in fixed order: 免责声明 → 起卦信息 → 装卦 → 逐爻明细 → 各族观察（八族固定顺序）→ 边界说明.
- Every family section carries status (`computed`/`degraded`/`not_computed`), at least one limitation, and evidence-present or evidence-pending wording.
- Prohibited absolute wording （必定/注定/一定会/死定 and English equivalents) must never appear; the report generator and its tests both enforce this.
- High-risk requests are refused with a redirect message or narrowed with explicit boundary notes; refusal leaves no partial output.

## Error Contract

| Case | Behavior |
|---|---|
| Malformed JSON / oversize / over-deep | exit 1, `Liuyao error: invalid request envelope` |
| Unknown or missing fields | exit 1, `Liuyao error: invalid request fields` |
| Mode/field mismatch | exit 1, `Liuyao error: cast mode requirements are not met` |
| Date out of range | exit 1, `Liuyao error: cast datetime is out of range` |
| Safety or high-risk refusal | exit 1, `Liuyao error: request cannot be answered within the safety boundary` |

## Versioning

- The V1 schema adds no fields silently; any future field addition requires a new schema version and a migration note.
- The contract is independent of the bazi application envelope; bazi contracts remain unchanged.
