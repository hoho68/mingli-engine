# Research: Existing Materials Audit and Preparation

## Decision: Store audit metadata in project-local JSON

**Rationale**: Existing evidence, source-intake, and source-library features use deterministic JSON records that are easy to review in Git and validate without a database or network. 015 should follow that pattern so the audit can be tested and reviewed before any implementation touches extraction workflows.

**Alternatives considered**:

- Tracking raw PDFs and preparation folders: rejected because the user explicitly wants existing materials handled without pushing or mutating external files.
- SQLite or another local database: rejected because the expected scale is modest and the project already has successful JSON validation patterns.
- Freeform Markdown-only notes: rejected because alignment, readiness, queue, and progress checks need structured validation.

## Decision: Model material groups separately from source-library entries

**Rationale**: A material group may include several representations: root PDF, prepared Markdown, cleaned Markdown, learning notes, and knowledge-skeleton artifacts. A 014 source-library entry is a planning record for future evidence work, not a complete inventory of every local representation. Separating them lets maintainers audit messy local materials while preserving 014 as the curated source-planning layer.

**Alternatives considered**:

- Add all audit fields directly to `SourceLibraryEntry`: rejected because it would make 014 carry transient filesystem and preparation details.
- Treat every file as a 013 source material: rejected because raw files and notes are not candidate extraction inputs until grouped and reviewed.
- Store only directory summaries: rejected because future maintainers need traceability from each material group to source-library and extraction queue decisions.

## Decision: Use explicit source-alignment findings instead of automatic fuzzy merges

**Rationale**: Existing materials use mixed Chinese titles, English labels, batch folders, cleaned variants, and knowledge-skeleton names. Automatic merging could silently combine different editions or unrelated notes. The audit should record exact, likely, duplicate, edition-variant, and uncertain relationships explicitly so a maintainer can review them.

**Alternatives considered**:

- Automatic filename-only matching: rejected because filenames are inconsistent and may be translated or shortened.
- Manual-only alignment with no helper records: rejected because gaps and duplicates would remain hard to audit.
- Silent merge into one canonical id: rejected because edition variants and uncertain source identity are important review facts.

## Decision: Separate preparation readiness from extraction readiness and formal evidence readiness

**Rationale**: A cleaned Markdown file is useful preparation, but it is not automatically a safe extraction source, and it is never formal report evidence. The audit needs distinct readiness states for text cleanup, source identity, locator confidence, rights notes, risk review, extraction readiness, and formal evidence status.

**Alternatives considered**:

- Single ready/not-ready flag: rejected because it hides why a material cannot move forward.
- Reusing source-library readiness only: rejected because 014 readiness describes source-planning status, while 015 must describe local representation and preparation quality.
- Treating cleaned Markdown as extraction-ready by default: rejected because cleaned text may be incomplete, context-poor, or high-risk.

## Decision: Treat high-risk discovery as a pre-extraction safety gate

**Rationale**: Existing materials include life-death, illness, disaster, remedy, and absolute-verdict themes. These can be useful for boundary work, but they must not be processed like routine low-risk theory material. 015 should label them before they enter any extraction-ready queue.

**Alternatives considered**:

- Detect high risk only during candidate review: rejected because reviewers need to know before selecting extraction work.
- Exclude all high-risk material from the audit: rejected because the project needs visibility into deferred and boundary-only material.
- Allow high-risk material in the queue with no separate prerequisites: rejected because this would violate the project constitution.

## Decision: Produce an extraction-ready queue and a preparation backlog

**Rationale**: The user goal is to "make existing materials ready." That requires both a small prioritized queue of safe next extraction candidates and a backlog of useful materials that need cleaning, locator review, source registration, or risk review first.

**Alternatives considered**:

- One combined priority list: rejected because extraction-ready and preparation-needed work require different next actions.
- Only report counts: rejected because counts do not tell a reviewer what to do next.
- Immediately create candidate extracts: rejected because 015 is an audit/preparation feature, not an extraction feature.

## Decision: Keep filesystem discovery read-only and metadata-only

**Rationale**: The current workspace contains large PDFs and many local preparation files. 015 can discover names, folder relationships, file sizes, and labels without opening large binary content or modifying files. Text content sampling, OCR, conversion, and source passage copying are out of scope.

**Alternatives considered**:

- Runtime PDF parsing: rejected because it is slow, dependency-heavy, and outside the 015 audit scope.
- Automatic OCR or Markdown conversion: rejected because it mutates preparation workflow scope and could create noisy text that looks more reliable than it is.
- Hashing full large files by default: rejected because it can be expensive; stable labels and optional lightweight metadata are sufficient for the first audit layer.
