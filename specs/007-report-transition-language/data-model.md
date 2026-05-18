# Data Model: 报告层间衔接语优化

## ReportTransitionText

Represents concise connective prose added to existing report fields.

Fields:

- `reading_path`: Tells the reader how to move from source assumptions to structure observation, interpretation boundaries, and action reflection.
- `source_basis_note`: Explains that birth data, source type, calendar assumptions, timezone, solar terms, and true solar time are report basis and assumptions, not conclusions.
- `structure_boundary_note`: Explains that structure observations are clues or materials, not final judgments.
- `boundary_action_note`: Explains that boundaries prevent overclaiming and lead into reflection.
- `reflection_prompt_note`: Explains that action content is a review prompt or organizing direction, not a promised result.

Validation rules:

- Each transition must be concise.
- Each transition must avoid deterministic or fate-verdict language.
- Each transition must not add new Bazi interpretation depth.

## Report

Existing output object consumed by the Markdown renderer.

Fields relevant to this feature:

- `quick_guide`: Should include the reading path cue.
- `assumptions`: Should include the source-as-basis note or equivalent wording.
- `structure_analysis`: Should preserve 006 structure wording and may include a bridge to boundaries.
- `interpretation_boundaries`: Should preserve existing boundary text and may include a bridge to action reflection.
- `strengths_and_issues` or `action_suggestions`: Should make clear that action content is reflection-oriented.

Validation rules:

- 004 heading order remains unchanged.
- 005 reader-facing labels remain unchanged.
- 006 structure observation wording remains unchanged.
- Safety review must still run over the final assembled report body.

## Markdown Report

Final report text shown to users.

Required behavior:

1. Starts with disclaimer and quick guide.
2. Shows first-layer source data and assumptions as input basis.
3. Shows second-layer structure observations as clues.
4. Shows third-layer boundaries as protection against overreading.
5. Shows fourth-layer action reflection as review prompts.
6. Keeps ethics reminder and safety boundaries visible.

State transitions:

1. Chart and interpretation data are assembled into `Report`.
2. Transition wording is added inside existing report fields.
3. Safety review checks the assembled report body.
4. Markdown renderer places existing fields under unchanged headings.
5. CLI returns Markdown for safe reports or safety JSON for red-line focus topics.
