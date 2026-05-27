# Research: 典籍证据核心与放大报告口径

## Decision: Use Curated Evidence Files, Not PDFs At Runtime

The report engine will not parse raw PDFs during report generation. Raw PDFs and converted Markdown are preparation inputs. The runtime report engine will load curated source and evidence files from the project package.

**Rationale**: PDF extraction can produce table noise, broken line order, and unreadable fragments. A formal report must not silently rely on unreviewed extraction. Curated files keep runtime deterministic and testable.

**Alternatives considered**:

- Parse PDFs on demand: rejected because extraction quality varies and would add runtime dependency and latency.
- Store only source titles without evidence cards: rejected because report conclusions would not be reviewable enough.

## Decision: Source Entries Must Track Extraction And Review Status

Each of the nine books will be represented as a `ClassicalSource` entry with title, file identity, extraction status, review status, scope notes, and risk notes.

**Rationale**: The user wants the corpus to be core evidence, but some sources may be unreadable or partially converted. Review status prevents accidental use of bad extraction as report evidence.

**Alternatives considered**:

- Treat every provided PDF as fully trusted immediately: rejected because extraction errors would become false authority.
- Require full manual annotation before any use: rejected because it delays MVP unnecessarily.

## Decision: Evidence Units Summarize Rules Instead Of Copying Long Passages

Report-supporting knowledge will be stored as concise evidence units with source references, themes, rule families, risk tiers, and short summaries.

**Rationale**: Evidence units are easier to test and safer for generated reports. They also avoid turning reports into long copied source text.

**Alternatives considered**:

- Store long direct excerpts: rejected because report output should synthesize evidence rather than reproduce books.
- Store unstructured notes: rejected because major conclusions need machine-checkable traces.

## Decision: Extend The Existing Report Object

The feature will extend the existing `Report` schema with formal judgment and evidence fields, then update Markdown and HTML renderers to use the same object.

**Rationale**: The current project already routes safe report output through a `Report` model. Keeping that as the contract preserves existing CLI paths and lets safety checks inspect the full report body.

**Alternatives considered**:

- Add a separate report command: rejected for MVP because it would split report behavior and tests.
- Render evidence only in Markdown: rejected because HTML must stay aligned with formal report content.

## Decision: Use Conclusion Strength For Expanded Judgment Language

Formal judgments will be labeled as `decided`, `candidate`, `weakly_supported`, `disputed`, or `unavailable`.

**Rationale**: The expanded constitution permits stronger traditional analysis, but every major conclusion still needs a visible confidence boundary.

**Alternatives considered**:

- Use only free-text caveats: rejected because tests cannot reliably inspect them.
- Use numeric confidence scores: rejected for the first version because source quality and school disagreement are qualitative.

## Decision: Use Risk Tiers For High-Risk Traditional Material

Evidence units and report conclusions will use risk tiers: `ordinary`, `sensitive`, and `high_risk`.

**Rationale**: Some corpus material discusses death, illness, disasters, and remedies. Risk tiers allow the corpus to remain core evidence while preventing exact-outcome or professional-advice outputs.

**Alternatives considered**:

- Exclude high-risk source material: rejected because the user explicitly wants the books to serve as core evidence.
- Allow all high-risk wording unchanged: rejected because it would create fear, overclaiming, and professional-advice risk.

## Decision: Keep Source Preparation Separate From User Data

The feature stores source/evidence knowledge in the project. It does not retain user birth data or generated case reports unless a future feature explicitly scopes that in.

**Rationale**: Corpus data and personal birth data have different privacy profiles. This feature should not introduce a long-term case archive.

**Alternatives considered**:

- Store generated reports for audit: rejected as out of scope and privacy-sensitive.
- Store only user-independent examples: accepted for regression tests where examples are already anonymized.
