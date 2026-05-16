# Research: 八字知识与报告引擎 MVP

## Decision: Python library with JSON CLI contract

**Rationale**: The first product slice is a knowledge and report engine, not a Web app. A Python package keeps the implementation small, easy to test, and friendly to future calendrical libraries if automatic chart calculation is added later. A JSON CLI gives the engine a stable executable contract without committing to a frontend.

**Alternatives considered**:

- Web app first: rejected because UI would distract from the core knowledge, safety, and report contracts.
- TypeScript library first: viable later for frontend sharing, but Python is simpler for local text processing and future calendrical tooling.
- Prompt-only skill: rejected because the project needs reviewable data objects and tests, not unstructured prose.

## Decision: Accept verified chart data in MVP

**Rationale**: Automatic calendrical calculation is a separate high-risk layer involving calendar type, solar terms, timezone, birthplace, and true solar time. The MVP can still validate report generation by accepting a verified chart object with explicit provenance.

**Alternatives considered**:

- Full automatic排盘 in MVP: rejected because it would enlarge scope and make testing harder before the report contract is stable.
- Manual prose input only: rejected because it would blur calculation facts and interpretation.

## Decision: Standard library data structures first

**Rationale**: Dataclasses, enums, and typed dictionaries are enough for the MVP data model. Avoiding runtime dependencies keeps setup simple and makes tests focus on domain behavior.

**Alternatives considered**:

- Pydantic: useful for stronger runtime validation, but not necessary for the first local engine.
- JSON Schema generator first: useful later for external integrations, but a documented CLI JSON contract is enough now.

## Decision: Markdown as first report format

**Rationale**: Markdown is readable, reviewable in Git, easy to test with string assertions, and can later transform to HTML/PDF/PNG. It also keeps the MVP independent from frontend styling decisions.

**Alternatives considered**:

- HTML first: attractive for visual reports, but too early before report content and safety checks stabilize.
- Plain text first: simpler, but weaker for structured reports and later transformations.

## Decision: Safety review is a first-class engine step

**Rationale**: The constitution requires red-line refusals, disclaimers, and non-absolute language. Modeling safety as a first-class result makes it testable and prevents report generation from treating ethics as copywriting.

**Alternatives considered**:

- Final proofreading only: rejected because unsafe requests should be blocked before full report generation.
- Prompt instructions only: rejected because prohibited phrases and red-line categories need deterministic tests.

## Decision: No persistent storage in MVP

**Rationale**: Birth data is sensitive. The MVP only needs file/stdin inputs and generated outputs, so it can avoid retention until a later feature explicitly scopes user-controlled storage.

**Alternatives considered**:

- Local case archive: useful for sample regression testing, but should use anonymized samples and a separate feature.
- Database: unnecessary for a single-report engine.
