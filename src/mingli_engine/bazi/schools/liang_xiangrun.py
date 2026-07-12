from mingli_engine.bazi.result_models import ReasonedResult, SchoolInterpretation
from mingli_engine.bazi.schools.base import (
    SchoolAdapterBase,
    _ValidatedSchoolInputs,
    distinct,
    not_computed_interpretation,
)


class LiangXiangrunSchoolAdapter(SchoolAdapterBase):
    school_id = "liang_xiangrun"

    def _interpret_validated(
        self, inputs: _ValidatedSchoolInputs
    ) -> SchoolInterpretation:
        selected_patterns = tuple(
            item
            for item in inputs.patterns
            if item.reasoning.status == "computed"
            and any(
                condition.startswith("exposed:")
                for condition in item.formation_conditions
            )
        )
        selected_useful = tuple(
            item
            for method in self.profile.method_order
            if method in {"seasonal_adjustment", "support_control"}
            for item in inputs.useful_gods
            if item.method == method
            and item.reasoning.status == "computed"
            and item.element
        )
        preferred_elements = distinct(tuple(item.element for item in selected_useful))
        excluded = tuple(
            f"excluded_pattern:{item.pattern_id}:{item.reasoning.status}:"
            f"{'latent_or_unexposed' if not any(value.startswith('exposed:') for value in item.formation_conditions) else 'noncomputed'}"
            for item in inputs.patterns
            if item not in selected_patterns
        ) + tuple(
            f"excluded_useful:{item.method}:{item.element or 'none'}:"
            f"{item.reasoning.status}"
            for item in inputs.useful_gods
            if item not in selected_useful
        )
        if not selected_patterns and not preferred_elements:
            return not_computed_interpretation(
                school_id=self.school_id,
                profile_version=self.profile_version,
                conclusion="Liang profile has no exposed computed pattern or supported useful preference",
                missing_inputs=("supported_computed_preference",),
                rule_id="school.liang_xiangrun.no_supported_preference",
                assumptions=excluded,
            )
        return SchoolInterpretation(
            school_id=self.school_id,
            profile_version=self.profile_version,
            reasoning=ReasonedResult(
                status="computed",
                conclusion="Liang profile uses exposed pattern context and computed seasonal/support candidates",
                confidence="medium",
                supporting_signals=(
                    *(
                        f"exposed_pattern:{item.rank}:{item.pattern_id}"
                        for item in selected_patterns
                    ),
                    *(
                        f"supported_useful:{item.method}:{item.element}:rank={item.rank}"
                        for item in selected_useful
                    ),
                ),
                assumptions=excluded,
                rule_ids=(
                    "school.liang_xiangrun.exposed_pattern_context",
                    "school.liang_xiangrun.seasonal_then_support",
                ),
            ),
            preferred_pattern_ids=tuple(item.pattern_id for item in selected_patterns),
            preferred_useful_god_elements=preferred_elements,
        )
