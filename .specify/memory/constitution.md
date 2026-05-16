<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles: placeholder principles -> domain-specific constitution
Added sections: Domain Boundaries; Development Workflow and Quality Gates
Removed sections: none
Templates requiring updates:
- updated: .specify/templates/plan-template.md
- updated: .specify/templates/spec-template.md
- updated: .specify/templates/tasks-template.md
- not applicable: .specify/templates/commands/*.md (directory absent)
Deferred follow-ups: none
-->

# 命理演绎 Constitution

## Core Principles

### I. Cultural Tool, Not Fate Verdict

Every feature MUST present 命理 as a traditional cultural interpretation and
self-reflection tool, not as scientific prediction or destiny enforcement.
Reports MUST use language such as tendency, structure, phase, reminder, and
suggestion. Reports MUST NOT use absolute claims such as 必定, 注定, 一定会,
死定, or other wording that removes user agency.

Rationale: The project must be honest about epistemic limits while still
making traditional knowledge useful and readable.

### II. Transparent Calculation Boundary

Calculation, interpretation, and report writing MUST remain separate concerns.
Any generated report MUST expose the source of its chart data and the rules or
assumptions used, including calendar type, birth time precision, birthplace
handling, timezone, solar terms, and whether true solar time was applied.
Missing required birth data MUST stop full report generation and return a clear
request for the missing fields.

Rationale: Users and maintainers need to audit how a conclusion was reached,
especially where calendrical rules differ across schools.

### III. Ethical Red Lines

The system MUST refuse, redirect, or safely narrow requests involving lifespan,
death timing, major disaster prediction, deterministic marriage matching,
medical advice, legal advice, psychological treatment, investment instruction,
unauthorized third-party full-chart analysis, anxiety creation, or paid remedy
upsells. Every formal report MUST include a disclaimer that decisions remain
with the user and that professional domains require qualified professionals.

Rationale: A 命理 product can be reflective and helpful only if it avoids
high-risk claims and coercive behavior.

### IV. Reviewable Knowledge and Reports

Knowledge rules, intermediate objects, and report sections MUST be structured
so each major conclusion can be traced to input data or an explicit assumption.
Report generation MUST include a safety and language review step before output.
When a conclusion is uncertain or school-dependent, the output MUST say so
instead of hiding uncertainty behind authoritative wording.

Rationale: The core product value is not mystical authority; it is a readable,
auditable synthesis.

### V. Test-First Quality Gates

Calculation rules, report schema transformations, missing-input handling,
ethical refusals, and absolute-language filtering MUST have tests before
implementation. Tests MUST include representative happy paths and red-line
requests. A feature is not ready if it can produce an unreviewed full report,
omit a disclaimer, or pass through prohibited deterministic language.

Rationale: This domain is especially prone to confident but unsafe prose, so
quality gates must cover both data behavior and language behavior.

## Domain Boundaries

The first product slice is the 八字 knowledge and report engine. It may accept
manually supplied chart data or externally verified chart outputs during MVP,
but the product contract must keep room for automatic calendrical calculation.
紫微斗数, 六爻, HTML visualization, PNG/PDF export, Web UI, accounts, payments,
and long-term case archives are future extensions unless a feature spec
explicitly scopes them in.

All personal birth data is sensitive. Features MUST minimize storage by
default, avoid retaining identifiable data unless the user explicitly requests
it, and keep sample cases anonymized.

## Development Workflow and Quality Gates

Every feature spec MUST state user value, required inputs, output boundaries,
ethical red lines, and measurable success criteria. Implementation plans MUST
include a Constitution Check covering calculation transparency, ethical
handling, report traceability, privacy, and tests. Task lists MUST include
validation of red-line refusals and non-absolute report language for every
report-producing feature.

The preferred delivery order is: constitution alignment, feature specification,
clarification if needed, implementation plan, tasks, test-first implementation,
and verification before completion claims.

## Governance

This constitution supersedes conflicting project habits, prompts, examples, or
reference materials. Amendments require a documented reason, semantic version
bump, updated dependent templates when relevant, and a review of existing specs
for compatibility.

Versioning follows semantic versioning:

- MAJOR for removing or redefining core safety or governance rules.
- MINOR for adding new principles, domain modules, or mandatory quality gates.
- PATCH for clarifications that do not change obligations.

All specs, plans, and reviews MUST verify compliance with this constitution.
Any exception must be documented in the relevant plan with risk, rationale, and
the simpler compliant alternative that was rejected.

**Version**: 1.0.0 | **Ratified**: 2026-05-16 | **Last Amended**: 2026-05-16
