# Personalized Formal Synthesis Design

## Goal

Make every formal rule-family explanation visibly depend on the current chart while preserving the existing approved-evidence body, conclusion strength, conflict trace, and safety boundaries.

## Approaches Considered

1. Append raw `EvidenceTrace.chart_signals` to the report. This is small but leaks machine markers, English pillar keys, placeholders, and high-risk focus text.
2. Rewrite each formal conclusion body inside `formal_interpretation.py`. This can produce fluent text but mixes chart-specific presentation with evidence construction and makes the evidence layer harder to audit.
3. Add one reader-facing signal formatter in `report_schema.py` and use it in both formal synthesis and observation evidence. This preserves the evidence model while giving all report surfaces consistent, sanitized personalization. This is the chosen approach.

## Signal Formatting

Each available formal conclusion receives one `盘面信号` segment. The formatter:

- preserves stable signal order and removes duplicates;
- translates `year`, `month`, `day`, and `hour` prefixes to Chinese pillar labels;
- preserves already-readable Chinese pillar labels;
- translates `traditional_high_risk_signal_boundary` to a conditional reader boundary;
- removes empty values and placeholders such as `unknown`, `unspecified`, `none`, and `null`;
- limits each conclusion to five visible signals;
- reports `当前未形成可用盘面信号` when no safe signal remains;
- for `high_risk_signal`, exposes only the stage statement and translated boundary marker, never the user's focus topic.

The underlying `EvidenceTrace` remains unchanged for audit use.

## Report Integration

`build_formal_synthesis()` adds the formatted signal segment before the existing approved-evidence body. `_format_expanded_evidence_notes()` uses the same formatter so internal markers do not remain visible in the report's observation-evidence section.

Unavailable conclusions retain their current unavailable wording and do not invent chart signals.

## Personalization Contract

For a complete report:

- all ten formal rule-family entries contain a reader-facing signal segment;
- no raw machine marker or English pillar prefix is visible;
- pattern, useful-god, and luck-cycle synthesis text changes when those chart inputs change;
- evidence ids, counts, conflict notes, strengths, and activation status remain unchanged;
- high-risk language stays conditional and non-exact.

The report acceptance baseline adds a `personalized_chart_signals` check and remains `ready_with_guardrails` only when this contract passes.

## Boundaries

- No new interpretation rules or evidence units.
- No source-library, 013, 012, or raw-material mutation.
- No persistence of chart profiles or generated reports.
- No user focus topic in the high-risk synthesis signal segment.
- No exact event, lifespan, medical, legal, psychological, or financial conclusion.

## Verification

Tests cover signal translation, placeholder filtering, high-risk sanitization, all-ten-family coverage, two-chart output differences, renderer and CLI visibility, acceptance-baseline integration, safety suites, quality scans, and the full repository regression.
