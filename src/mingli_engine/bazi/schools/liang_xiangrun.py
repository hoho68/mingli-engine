from mingli_engine.bazi.result_models import ReasonedResult, SchoolInterpretation
from mingli_engine.bazi.schools.base import (
    SchoolAdapterBase,
    _ValidatedSchoolInputs,
    distinct,
    not_computed_interpretation,
)


class LiangXiangrunSchoolAdapter(SchoolAdapterBase):
    __slots__ = ()
    _SCHOOL_ID = "liang_xiangrun"

    def _interpret_validated(
        self, inputs: _ValidatedSchoolInputs
    ) -> SchoolInterpretation:
        pattern_enabled = "pattern_context" in self.profile.method_order
        selected_patterns = tuple(
            item
            for item in inputs.patterns
            if pattern_enabled
            and item.reasoning.status == "computed"
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
        excluded_patterns = (
            tuple(
                f"excluded_pattern:{item.pattern_id}:{item.reasoning.status}:"
                f"{'latent_or_unexposed' if not any(value.startswith('exposed:') for value in item.formation_conditions) else 'noncomputed'}"
                for item in inputs.patterns
                if item not in selected_patterns
            )
            if pattern_enabled
            else ("method_not_configured:pattern_context",)
        )
        configured_useful_methods = {
            method
            for method in self.profile.method_order
            if method in {"seasonal_adjustment", "support_control"}
        }
        excluded_useful = tuple(
            f"excluded_useful:{item.method}:{item.element or 'none'}:"
            f"{item.reasoning.status}"
            for item in inputs.useful_gods
            if item.method in configured_useful_methods and item not in selected_useful
        ) + tuple(
            f"method_not_configured:{method}"
            for method in ("seasonal_adjustment", "support_control")
            if method not in configured_useful_methods
        )
        excluded = (*excluded_patterns, *excluded_useful)
        if not selected_patterns and not preferred_elements:
            return not_computed_interpretation(
                school_id=self.school_id,
                profile_version=self.profile_version,
                conclusion="Liang profile has no exposed computed pattern or supported useful preference",
                missing_inputs=("supported_computed_preference",),
                rule_id="school.liang_xiangrun.no_supported_preference",
                assumptions=excluded,
            )
        used_methods = tuple(
            method
            for method in self.profile.method_order
            if (
                method == "pattern_context"
                and bool(selected_patterns)
                or any(item.method == method for item in selected_useful)
            )
        )
        rule_by_method = {
            "pattern_context": "school.liang_xiangrun.exposed_pattern_context",
            "seasonal_adjustment": "school.liang_xiangrun.seasonal_adjustment",
            "support_control": "school.liang_xiangrun.support_control",
        }
        supporting_signals = tuple(
            signal
            for method in used_methods
            for signal in (
                tuple(
                    f"exposed_pattern:{item.rank}:{item.pattern_id}"
                    for item in selected_patterns
                )
                if method == "pattern_context"
                else tuple(
                    f"supported_useful:{item.method}:{item.element}:rank={item.rank}"
                    for item in selected_useful
                    if item.method == method
                )
            )
        )
        return SchoolInterpretation(
            school_id=self.school_id,
            profile_version=self.profile_version,
            reasoning=ReasonedResult(
                status="computed",
                conclusion=(
                    "Liang profile applies configured methods: "
                    + ", ".join(used_methods)
                ),
                confidence="medium",
                supporting_signals=supporting_signals,
                assumptions=excluded,
                rule_ids=tuple(rule_by_method[method] for method in used_methods),
            ),
            preferred_pattern_ids=tuple(item.pattern_id for item in selected_patterns),
            preferred_useful_god_elements=preferred_elements,
        )
