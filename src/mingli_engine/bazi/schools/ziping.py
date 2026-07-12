from mingli_engine.bazi.result_models import ReasonedResult, SchoolInterpretation
from mingli_engine.bazi.schools.base import (
    SchoolAdapterBase,
    _ValidatedSchoolInputs,
    conservative_status,
    distinct,
    not_computed_interpretation,
)


class ZipingSchoolAdapter(SchoolAdapterBase):
    _SCHOOL_ID = "ziping"

    def _interpret_validated(
        self, inputs: _ValidatedSchoolInputs
    ) -> SchoolInterpretation:
        patterns = tuple(sorted(inputs.patterns, key=lambda item: item.rank))
        method_priority = {
            method: index for index, method in enumerate(self.profile.method_order)
        }
        selected_useful = tuple(
            sorted(
                (
                    candidate
                    for candidate in inputs.useful_gods
                    if candidate.method in method_priority
                    and candidate.element
                    and candidate.reasoning.status
                    in {"computed", "indeterminate", "disputed"}
                ),
                key=lambda candidate: (
                    method_priority[candidate.method],
                    candidate.reasoning.status != "computed",
                    candidate.rank,
                ),
            )
        )
        preferred_elements = distinct(tuple(item.element for item in selected_useful))
        if not patterns or not preferred_elements:
            missing = (
                *(("pattern_candidates",) if not patterns else ()),
                *(("useful_god_preferences",) if not preferred_elements else ()),
            )
            return not_computed_interpretation(
                school_id=self.school_id,
                profile_version=self.profile_version,
                conclusion="Ziping baseline lacks required pattern or useful-god input",
                missing_inputs=missing,
                rule_id="school.ziping.missing_inputs",
            )
        selected_reasonings = tuple(item.reasoning for item in patterns) + tuple(
            item.reasoning for item in selected_useful
        )
        status = conservative_status(selected_reasonings)
        pattern_trace = tuple(
            f"pattern_state:{item.rank}:{item.pattern_id}:{item.reasoning.status}"
            for item in patterns
        )
        useful_trace = tuple(
            f"useful_state:{item.rank}:{item.method}:{item.element}:"
            f"{item.reasoning.status}"
            for item in selected_useful
        )
        opposition = tuple(
            f"selected_noncomputed_state:{item.pattern_id}:{item.reasoning.status}"
            for item in patterns
            if item.reasoning.status in {"indeterminate", "disputed"}
        ) + tuple(
            f"selected_noncomputed_state:{item.method}:{item.element}:"
            f"{item.reasoning.status}"
            for item in selected_useful
            if item.reasoning.status in {"indeterminate", "disputed"}
        )
        return SchoolInterpretation(
            school_id=self.school_id,
            profile_version=self.profile_version,
            reasoning=ReasonedResult(
                status=status,
                conclusion="Ziping baseline rank and configured useful methods preserved",
                confidence="medium" if status == "computed" else "low",
                supporting_signals=(*pattern_trace, *useful_trace),
                opposing_signals=opposition,
                assumptions=("school_profile_method_order_applied",),
                rule_ids=(
                    "school.ziping.baseline_rank",
                    "school.ziping.configured_useful_method_order",
                ),
            ),
            preferred_pattern_ids=tuple(item.pattern_id for item in patterns),
            preferred_useful_god_elements=preferred_elements,
        )
