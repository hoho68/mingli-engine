# Research: 报告层间衔接语优化

## Decision: Add Transition Wording In Report Assembly

**Decision**: Add concise transition wording in `src/mingli_engine/report_schema.py`.

**Rationale**: `report_schema.py` already turns chart and interpretation objects into reader-facing report fields. This is the right place to add connective prose before Markdown layout and safety review happen.

**Alternatives considered**:

- Add transition text directly in `markdown.py`: rejected because it would put domain prose in the renderer and blur layout responsibility.
- Add a new transition model or service: rejected because the feature is small and deterministic.
- Rewrite interpretation text in `interpretation.py`: rejected for most transitions because 007 is about the whole report path, not new structure interpretation.

## Decision: Preserve Existing Heading Order

**Decision**: Keep the 004 heading order exactly as it is and put transitions inside existing report fields.

**Rationale**: Users and tests already rely on the layered report structure. Adding new top-level sections would increase scope and reduce comparability with earlier features.

**Alternatives considered**:

- Add separate "how to read this report" section: rejected because it changes the report structure and may add bulk.
- Rename headings: rejected because it would churn existing contracts without solving a real problem.

## Decision: Keep Quick Guide Concise

**Decision**: Keep the quick guide within the existing concise bullet pattern and add the reading path as one short cue.

**Rationale**: The quick guide is meant to be skimmable. A longer explanation belongs in the body, not in a large introductory block.

**Alternatives considered**:

- Add a full paragraph before the quick guide: rejected because it risks making the report feel wordy.
- Remove existing quick guide bullets to make room: rejected because current bullets carry source, structure, day-master, boundary, and reflection information.

## Decision: Preserve 005 And 006 Wording Contracts

**Decision**: 007 tests must assert that 005 reader-facing labels and 006 structure observation phrases remain visible.

**Rationale**: This feature should improve continuity without regressing previous readability work.

**Alternatives considered**:

- Allow minor rewrites of 006 structure text: rejected because the user selected whole-report transitions, not another structure observation pass.
- Revisit 005 label fallback rules: rejected because labels are already covered and out of scope.

## Decision: Verify Through Final Markdown And Safety Tests

**Decision**: Add report schema assertions for transition fields, integration assertions for final Markdown in both CLI paths, and keep safety tests mandatory.

**Rationale**: Transitions affect final reader-facing output and safety posture. Unit-only tests would not prove that the final Markdown report reads correctly.

**Alternatives considered**:

- Snapshot testing the full report: rejected because focused phrases are easier to maintain for prose changes.
- Manual-only sample review: rejected because language regressions should be automatically guarded.
