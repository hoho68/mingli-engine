# Research: Source Extraction Workflow

## Decision: Keep raw PDF and Markdown materials external to the reviewed corpus

**Rationale**: The user explicitly identified root PDF files and the root `Markdown/` directory as provided source material that must not be moved, deleted, or submitted without instruction. 013 should register source material identity and preparation status, while leaving physical files untouched.

**Alternatives considered**:

- Track root materials in Git: rejected because the user explicitly asked not to submit these materials and the files may be large or rights-sensitive.
- Move materials into `docs/`: rejected because it changes user-provided file organization before an explicit user request.
- Parse materials at report runtime: rejected because report generation must remain deterministic and evidence-backed, not dependent on live document parsing.

## Decision: Use a candidate extract queue before formal evidence units

**Rationale**: 012 already established formal evidence units as reviewed report-usable knowledge. Candidate material from source reading needs a quarantine state so incomplete, disputed, duplicated, or high-risk material cannot leak into reports.

**Alternatives considered**:

- Add draft evidence units directly to `evidence_units.json`: rejected because it weakens the report-usable evidence boundary.
- Use free-form review notes only: rejected because progress, validation, and promotion readiness need structured status and required fields.

## Decision: Require human review decisions for approval

**Rationale**: Candidate extraction can be assisted by tooling, but source meaning, safety rewriting, conflict handling, and report suitability require reviewer judgment. Approval must record reviewer, date, rationale, limitations, and batch.

**Alternatives considered**:

- Auto-approve low-risk candidates: rejected because source locator, interpretation scope, and duplicate/conflict checks still need human review.
- Single boolean approval field: rejected because returned, rejected, blocked, and pending states carry different follow-up meanings.

## Decision: Preserve rejected and blocked candidates

**Rationale**: Rejected material documents coverage boundaries and prevents future maintainers from repeatedly reconsidering the same unsafe or unusable content without context. Blocked candidates also reveal extraction gaps.

**Alternatives considered**:

- Delete rejected records: rejected because it erases audit history and source coverage information.
- Store only aggregate rejected counts: rejected because reviewers need specific reasons and source locators.

## Decision: Link candidates to duplicate, conflict, and gap records explicitly

**Rationale**: Classical materials can contain overlapping or school-dependent statements. Explicit links make it clear whether a candidate is redundant, disputed, insufficiently located, or unsafe.

**Alternatives considered**:

- Infer conflicts only from text similarity: rejected because similar wording can reflect different schools or scopes.
- Store conflicts only after promotion: rejected because unresolved conflicts may be the reason a candidate never gets promoted.

## Decision: Build progress summaries from structured intake data

**Rationale**: Maintainers need phase-by-phase visibility into pending, approved, rejected, blocked, duplicate, and gap-related candidates. Computing this from records avoids stale hand-maintained counts.

**Alternatives considered**:

- Maintain progress notes manually: rejected because counts can drift from the candidate queue.
- Use report coverage only: rejected because 012 coverage intentionally ignores unapproved candidate material.
