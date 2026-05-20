# Data Model: 报告证据说明层

## EvidenceNotesSection

Represents the reader-facing `观察依据` content in a formal safe report.

Fields:

- `source_basis`: Explains that observations start from chart source and assumptions.
- `pillar_basis`: Explains that four-pillar observations come from year, month, day, and hour structure positions and combinations.
- `element_basis`: Explains that five-element observations come from visible signals, hidden-stem signals, and total counted signals.
- `ten_god_basis`: Explains that ten-god observations are relationship signals across pillar positions.
- `action_basis`: Explains that action reflection turns observable structure signals into review prompts rather than predictions.

Validation rules:

- Must be non-empty for every formal safe report.
- Must use reader-facing labels.
- Must not include selected raw machine labels such as `auto_calculated`, `external_verified`, `medium`, or `gregorian`.
- Must not include absolute destiny phrases such as `必定`, `注定`, `一定会`, or `死定`.
- Must not introduce new Bazi conclusions, useful-god verdicts, strength verdicts, luck-cycle judgments, or event predictions.

## Report

Existing formal report object that will include the evidence-note section.

New field:

- `evidence_notes`: String representation of `EvidenceNotesSection`, ready for Markdown rendering and safety review.

Validation rules:

- `evidence_notes` is required whenever a formal safe report is built.
- `evidence_notes` participates in the report safety review along with other formal report sections.
- Existing fields, source disclosure, disclaimer, and four-layer order remain required.

## ReportEvidenceContractCheck

Represents automated checks that protect the new report contract.

Safe Markdown checks:

- Formal Markdown report includes `### 观察依据`.
- The section appears after `### 十神摘要` and before `### 结构分析`.
- The section includes stable labels or wording for source basis, four-pillar basis, five-element basis, ten-god basis, and action basis.
- The section avoids selected raw labels and absolute destiny phrases.
- Automatic and external verified reports keep their existing source-specific wording.

Safety JSON checks:

- Unsafe red-line examples still return safety JSON instead of formal Markdown.
- Safety JSON output does not contain `### 观察依据`.

State transitions:

1. Safe chart input is converted to the existing report object.
2. Evidence-note content is assembled from existing report/chart concepts.
3. Safety review includes the evidence-note content.
4. Markdown renderer places the evidence-note section in the structure-observation layer.
5. Regression tests verify safe reports include the section and unsafe inputs do not receive a formal report.
