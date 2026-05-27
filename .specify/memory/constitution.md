<!--
Sync Impact Report
Version change: 1.0.0 -> 2.0.0
Modified principles:
- I. Cultural Tool, Not Fate Verdict -> Evidence-Based Traditional Analysis, Not Unbounded Authority
- II. Transparent Calculation Boundary -> Transparent Calculation and Evidence Boundary
- III. Ethical Red Lines -> Expanded High-Risk Boundaries
- IV. Reviewable Knowledge and Reports -> Reviewable Classical Evidence and Reports
- V. Test-First Quality Gates -> Test-First Quality Gates
Added sections: Classical Source Corpus and Report Scope
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

### I. Evidence-Based Traditional Analysis, Not Unbounded Authority

Every formal report MAY make substantive traditional 命理 judgments when those
judgments are backed by chart data and classical evidence. Permitted judgment
families include pattern candidates, strength tendency, useful-god and taboo-god
candidates, ten-god combinations, body-use relations, branch interactions,
blind-school image methods, luck-cycle themes, and timing triggers.

Every such judgment MUST remain framed as traditional evidence analysis, not as
scientific proof, destiny enforcement, or guaranteed real-world outcome.
Reports MUST NOT use absolute claims such as 必定, 注定, 一定会, 死定, or other
wording that removes user agency.

Rationale: The project is moving from light reflection into formal traditional
analysis while keeping epistemic honesty and user agency visible.

### II. Transparent Calculation and Evidence Boundary

Calculation, evidence selection, interpretation, and report writing MUST remain
separate concerns. Any generated report MUST expose the source of its chart data
and the rules or assumptions used, including calendar type, birth time precision,
birthplace handling, timezone, solar terms, and whether true solar time was
applied.

Any major interpretive conclusion MUST be traceable to one or more of: chart
data, derived intermediate structure, an explicit school rule, or a named source
from the classical evidence corpus. Missing required birth data MUST stop full
report generation and return a clear request for the missing fields.

Rationale: Users and maintainers need to audit how a conclusion was reached,
especially where calendrical rules and schools differ.

### III. Expanded High-Risk Boundaries

The system MAY discuss traditionally high-risk signals, including health
tendencies, disaster risk language, major relationship risk, financial pressure,
and life-death materials, when the user requests a formal 命理 report and when
the analysis is source-backed. Such content MUST be labeled as traditional
high-risk signal analysis and MUST use probability, condition, evidence, and
uncertainty language.

The system MUST refuse, redirect, or narrow requests that ask for guaranteed
death timing, exact lifespan, medical diagnosis or treatment, legal instruction,
psychological treatment, investment instruction, coercive marriage matching,
unauthorized third-party harm, anxiety creation, or paid-remedy upsells. Remedy
or adjustment content MAY describe traditional claims, but MUST NOT promise
guaranteed effects or pressure the user to buy services.

Every formal report MUST include a disclaimer that decisions remain with the
user and that professional domains require qualified professionals.

Rationale: The product can use the full traditional corpus as evidence while
still blocking coercive, absolute, or professional-advice outputs.

### IV. Reviewable Classical Evidence and Reports

Knowledge rules, intermediate objects, source excerpts, evidence cards, and
report sections MUST be structured so each major conclusion can be traced to
input data or explicit evidence. Report generation MUST include source,
confidence, disagreement, and language review before output.

When a conclusion is uncertain, school-dependent, textually disputed, or based
on high-risk material, the output MUST say so instead of hiding uncertainty
behind authoritative wording.

Rationale: The core product value is a readable, auditable synthesis of
traditional evidence, not unsupported mystical authority.

### V. Test-First Quality Gates

Calculation rules, report schema transformations, missing-input handling,
ethical refusals, and absolute-language filtering MUST have tests before
implementation. Tests MUST include representative happy paths and red-line
requests. A feature is not ready if it can produce an unreviewed full report,
omit a disclaimer, or pass through prohibited deterministic language.

Rationale: This domain is especially prone to confident but unsafe prose, so
quality gates must cover both data behavior and language behavior.

## Classical Source Corpus and Report Scope

The primary product scope is the 八字 knowledge and report engine. It may accept
manually supplied chart data, externally verified chart outputs, or automatic
calendrical calculation. Classical source material MAY become first-class
evidence for formal reports when it is converted into reviewable source entries
and evidence cards.

Initial report scope MAY include formal traditional analysis across pattern,
strength, useful-god candidates, ten-god relations, branch interactions,
blind-school image methods, luck-cycle themes, and high-risk signal review.
紫微斗数, 六爻, PNG/PDF export, Web UI, accounts, payments, and long-term case
archives are future extensions unless a feature spec explicitly scopes them in.

All personal birth data is sensitive. Features MUST minimize storage by
default, avoid retaining identifiable data unless the user explicitly requests
it, and keep sample cases anonymized.

## Development Workflow and Quality Gates

Every feature spec MUST state user value, required inputs, output boundaries,
classical evidence scope, high-risk handling, and measurable success criteria.
Implementation plans MUST include a Constitution Check covering calculation
transparency, evidence traceability, high-risk narrowing, privacy, and tests.
Task lists MUST include validation of source-backed conclusions, high-risk
content handling, disclaimer presence, and non-absolute report language for
every report-producing feature.

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

**Version**: 2.0.0 | **Ratified**: 2026-05-16 | **Last Amended**: 2026-05-27
