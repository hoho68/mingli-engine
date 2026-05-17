# Research: 八字基础结构解读规则层

## Decision: Use deterministic project-local interpretation rules

**Rationale**: The feature must be testable, auditable, and conservative. Deterministic rules make it possible to verify exact element counts, repeated ten-gods, limitation text, and absence of prohibited language.

**Alternatives considered**:

- LLM-generated interpretation: rejected because outputs would be harder to make deterministic and safety-reviewable.
- External命理 rules service: rejected because it adds dependency and privacy surface area.
- Large rule engine with pattern/useful-god logic: rejected because first version intentionally excludes advanced determinations.

## Decision: Add one `interpretation.py` module

**Rationale**: Calculation, interpretation, and reporting are separate constitutional concerns. A focused module keeps rule logic reviewable and prevents report assembly from becoming a rules engine.

**Alternatives considered**:

- Put rules directly in `report_schema.py`: rejected because it mixes report formatting with domain rules.
- Extend `chart_calculator.py`: rejected because chart calculation should stay about calendrical facts and chart construction.

## Decision: Count visible and hidden signals separately

**Rationale**: The spec requires five-elements distribution from available chart signals and a distinction between direct visible signals and hidden-stem support. Separate counts let the report say what is visible versus supporting without implying a full strength model.

**Alternatives considered**:

- Count only `Pillar.element`: rejected because it hides which data source produced each element signal.
- Weighted strength calculation: rejected because this feature does not determine day-master strength.

## Decision: Integrate into existing report fields

**Rationale**: Users should get richer reports through existing `generate-report` and `calculate-report` paths without new flags. Existing Markdown section structure remains stable for current tests and users.

**Alternatives considered**:

- Add a new CLI command: rejected because interpretation is report content, not a separate user workflow for the first version.
- Add new Markdown sections: deferred because the existing section structure already has five-elements, ten-gods, structure, tendencies, issues, suggestions, and ethics sections.

## Decision: Preserve safety and source boundaries

**Rationale**: The report must continue to disclose chart source, confidence, calendar assumptions, and safety constraints. The interpretation layer must not rewrite source metadata or bypass safety review.

**Alternatives considered**:

- Interpretation-specific safety layer only: rejected because existing final report safety review should remain authoritative.
- Remove advanced fields from `BaziChart`: rejected because current public chart shape is already used by reports and CLI contracts.
