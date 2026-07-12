from mingli_engine.bazi.result_models import (
    PatternCandidateResult,
    ReasonedResult,
    SchoolInterpretation,
    UsefulGodCandidateResult,
)
from mingli_engine.bazi.schools.base import (
    SchoolAdapterBase,
    _ValidatedSchoolInputs,
    conservative_status,
    distinct,
    not_computed_interpretation,
)


_STRUCTURED_PREFIXES = (
    "exposed:",
    "hidden:",
    "strength_label:",
    "day_element:",
    "relation:",
)


class DuanSchoolAdapter(SchoolAdapterBase):
    school_id = "duan"

    def _interpret_validated(
        self, inputs: _ValidatedSchoolInputs
    ) -> SchoolInterpretation:
        structural_patterns = tuple(
            item
            for item in inputs.patterns
            if item.formation_conditions
            and item.damage_conditions
            and all(
                condition in item.reasoning.opposing_signals
                for condition in item.damage_conditions
            )
        )
        structural_useful = tuple(
            item
            for item in inputs.useful_gods
            if item.method in {"mediation", "support_control"}
            and item.reasoning.status == "computed"
            and item.element
            and any(
                signal.startswith(_STRUCTURED_PREFIXES)
                for signal in item.reasoning.supporting_signals
            )
        )
        if not structural_patterns or not structural_useful:
            missing = (
                *(
                    ("structural_conditions",)
                    if not any(item.formation_conditions for item in inputs.patterns)
                    else ()
                ),
                *(("structural_counterconditions",) if not structural_patterns else ()),
                *(("structured_useful_provenance",) if not structural_useful else ()),
            )
            return not_computed_interpretation(
                school_id=self.school_id,
                profile_version=self.profile_version,
                conclusion="Duan structural-flow prerequisites are not established",
                missing_inputs=missing,
                rule_id="school.duan.structural_flow_prerequisites_missing",
            )

        selected_useful: list[UsefulGodCandidateResult] = []
        for method in self.profile.method_order:
            if method == "structural_flow":
                selected_useful.extend(
                    item for item in structural_useful if item.method == "mediation"
                )
                if not selected_useful:
                    selected_useful.extend(
                        item
                        for item in structural_useful
                        if item.method == "support_control"
                    )
            elif method == "support_control":
                selected_useful.extend(
                    item
                    for item in structural_useful
                    if item.method == "support_control"
                )
        selected_useful_tuple = tuple(dict.fromkeys(selected_useful))
        selected_patterns: list[PatternCandidateResult] = []
        for method in self.profile.method_order:
            if method == "structural_flow":
                selected_patterns.extend(structural_patterns)
            elif method == "pattern_context":
                selected_patterns.extend(
                    item
                    for item in inputs.patterns
                    if item.formation_conditions
                    and item.reasoning.status
                    in {"computed", "indeterminate", "disputed"}
                )
        selected_patterns_tuple = tuple(dict.fromkeys(selected_patterns))
        preferred_elements = distinct(
            tuple(item.element for item in selected_useful_tuple)
        )
        status = conservative_status(
            tuple(item.reasoning for item in selected_patterns_tuple)
            + tuple(item.reasoning for item in selected_useful_tuple)
        )
        return SchoolInterpretation(
            school_id=self.school_id,
            profile_version=self.profile_version,
            reasoning=ReasonedResult(
                status=status,
                conclusion="Duan structural flow is grounded in explicit conditions and counterconditions",
                confidence="medium" if status == "computed" else "low",
                supporting_signals=tuple(
                    f"formation_condition:{item.pattern_id}:{condition}"
                    for item in structural_patterns
                    for condition in item.formation_conditions
                )
                + tuple(
                    f"structured_useful:{item.method}:{item.element}:{signal}"
                    for item in selected_useful_tuple
                    for signal in item.reasoning.supporting_signals
                    if signal.startswith(_STRUCTURED_PREFIXES)
                ),
                opposing_signals=tuple(
                    f"countercondition:{item.pattern_id}:{condition}"
                    for item in structural_patterns
                    for condition in item.damage_conditions
                ),
                assumptions=("no_structural_flow_inferred_from_prose",),
                rule_ids=(
                    "school.duan.structural_flow",
                    "school.duan.explicit_countercondition_gate",
                    "school.duan.gated_pattern_context",
                ),
            ),
            preferred_pattern_ids=tuple(
                item.pattern_id for item in selected_patterns_tuple
            ),
            preferred_useful_god_elements=preferred_elements,
        )
