from __future__ import annotations

from collections.abc import Callable, Mapping
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Any, Protocol, cast

from mingli_engine.application_serialization import response_status_from_json_bytes
from mingli_engine.application_service import handle_real_use_json
from mingli_engine.domain_calibration import canonical_json_bytes
from mingli_engine.domain_calibration_v2_models import (
    CALIBRATION_EXTRACTION_SCHEMA_V2,
    CALIBRATION_OBSERVATION_SCHEMA_V2,
    DOMAIN_CALIBRATION_SUITE_V2,
    CalibrationActualStatusV2,
    CalibrationExtractionV2,
    CalibrationObservationV2,
)
from mingli_engine.formal_interpretation import (
    get_formal_interpretation_rule_families,
)


JsonObject = dict[str, Any]
ExtractorV2 = Callable[[CalibrationObservationV2], CalibrationExtractionV2]

_DEPENDENCY_ERROR_CODES = frozenset(
    {"calculation_failed", "knowledge_unavailable"}
)
_TERMINAL_ERROR_CODES = frozenset({"unsupported_input"})


class CalibrationObservationErrorV2(ValueError):
    pass


class CalibrationExtractionErrorV2(ValueError):
    pass


class CalibrationApplicationExecutionErrorV2(CalibrationObservationErrorV2):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"calibration application execution failed: {code}")


class ApplicationJsonExecutorV2(Protocol):
    def execute(self, payload: bytes) -> bytes: ...


class _HandleRealUseJsonExecutorV2:
    def execute(self, payload: bytes) -> bytes:
        return handle_real_use_json(payload)


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> JsonObject:
    result: JsonObject = {}
    for key, value in pairs:
        if key in result:
            raise CalibrationObservationErrorV2("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise CalibrationObservationErrorV2("non-finite JSON value")


def _canonical_mapping(payload: bytes, context: str) -> JsonObject:
    if type(payload) is not bytes:
        raise TypeError(f"{context} must be bytes")
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, ValueError, RecursionError):
        raise CalibrationObservationErrorV2(f"{context} is invalid JSON") from None
    if not isinstance(value, dict) or canonical_json_bytes(value) != payload:
        raise CalibrationObservationErrorV2(f"{context} is not canonical JSON")
    return cast(JsonObject, value)


def _validate_request_pair(
    analysis_request_json: bytes,
    report_request_json: bytes,
) -> None:
    analysis = _canonical_mapping(analysis_request_json, "analysis request")
    report = _canonical_mapping(report_request_json, "report request")
    if analysis.get("operation") != "analysis" or report.get("operation") != "report":
        raise CalibrationObservationErrorV2("request operations are invalid")
    if analysis.get("options") != {
        "include_profile_in_report": False,
        "report_format": None,
    }:
        raise CalibrationObservationErrorV2("analysis request options are invalid")
    if report.get("options") != {
        "include_profile_in_report": False,
        "report_format": "json",
    }:
        raise CalibrationObservationErrorV2("report request options are invalid")
    analysis_comparable = dict(analysis)
    report_comparable = dict(report)
    analysis_comparable.pop("operation", None)
    report_comparable.pop("operation", None)
    analysis_comparable.pop("options", None)
    report_comparable.pop("options", None)
    if analysis_comparable != report_comparable:
        raise CalibrationObservationErrorV2(
            "analysis and report requests must use the same synthetic profile"
        )


def _validated_response(payload: bytes, context: str) -> JsonObject:
    try:
        response_status_from_json_bytes(payload)
        return _canonical_mapping(payload, context)
    except Exception:
        raise CalibrationObservationErrorV2(
            f"{context} is not a canonical application response"
        ) from None


def _error_code(response: JsonObject) -> str | None:
    error = response.get("error")
    if not isinstance(error, dict):
        return None
    code = error.get("code")
    return code if isinstance(code, str) else None


def _validate_response_pair(
    analysis_payload: bytes,
    report_payload: bytes,
) -> tuple[JsonObject, JsonObject]:
    analysis = _validated_response(analysis_payload, "analysis response")
    report = _validated_response(report_payload, "report response")
    if analysis.get("status") != report.get("status"):
        raise CalibrationObservationErrorV2("response statuses do not match")
    status = analysis.get("status")
    if status == "ok":
        if analysis.get("operation") != "analysis" or report.get("operation") != "report":
            raise CalibrationObservationErrorV2("success response operations are invalid")
        if analysis.get("provenance") != report.get("provenance"):
            raise CalibrationObservationErrorV2("response provenance does not match")
        result = analysis.get("result")
        provenance = analysis.get("provenance")
        if not isinstance(result, dict) or not isinstance(provenance, dict):
            raise CalibrationObservationErrorV2("success response structure is invalid")
        calculation = result.get("calculation")
        if not isinstance(calculation, dict) or (
            calculation.get("engine_version") != provenance.get("engine_version")
            or calculation.get("ruleset_version") != provenance.get("ruleset_version")
        ):
            raise CalibrationObservationErrorV2("calculation provenance is invalid")
        return analysis, report
    analysis_code = _error_code(analysis)
    report_code = _error_code(report)
    if analysis_code != report_code or analysis_code is None:
        raise CalibrationObservationErrorV2("terminal response codes do not match")
    if status == "refused":
        if (
            analysis_code != "unsafe_request"
            or analysis.get("operation") != "analysis"
            or report.get("operation") != "report"
        ):
            raise CalibrationObservationErrorV2("refusal response is not supported")
        return analysis, report
    if analysis_code in _DEPENDENCY_ERROR_CODES:
        raise CalibrationApplicationExecutionErrorV2(analysis_code)
    if (
        status == "error"
        and analysis_code in _TERMINAL_ERROR_CODES
        and analysis.get("operation") is None
        and report.get("operation") is None
    ):
        return analysis, report
    raise CalibrationObservationErrorV2("application error is not observable")


def collect_calibration_observation_v2(
    observation_id: str,
    analysis_request_json: bytes,
    report_request_json: bytes,
    executor: ApplicationJsonExecutorV2 | None = None,
) -> CalibrationObservationV2:
    """Execute one synthetic request pair through the strict JSON application."""
    _validate_request_pair(analysis_request_json, report_request_json)
    active_executor = executor or _HandleRealUseJsonExecutorV2()
    analysis_response = active_executor.execute(analysis_request_json)
    report_response = active_executor.execute(report_request_json)
    _validate_response_pair(analysis_response, report_response)
    return CalibrationObservationV2(
        schema_version=CALIBRATION_OBSERVATION_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        observation_id=observation_id,
        analysis_request_sha256=sha256(analysis_request_json).hexdigest(),
        report_request_sha256=sha256(report_request_json).hexdigest(),
        analysis_response_sha256=sha256(analysis_response).hexdigest(),
        report_response_sha256=sha256(report_response).hexdigest(),
        analysis_response_json=analysis_response,
        report_response_json=report_response,
    )


def _mapping(value: object, context: str) -> JsonObject:
    if not isinstance(value, dict):
        raise CalibrationExtractionErrorV2(f"{context} must be an object")
    return cast(JsonObject, value)


def _sequence(value: object, context: str) -> list[object]:
    if not isinstance(value, list):
        raise CalibrationExtractionErrorV2(f"{context} must be a list")
    return value


def _text(value: object, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise CalibrationExtractionErrorV2(f"{context} must be a nonempty string")
    return value


def _number_token(value: object, context: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CalibrationExtractionErrorV2(f"{context} must be numeric")
    return json.dumps(value, allow_nan=False, separators=(",", ":"))


def _extraction(
    observation: CalibrationObservationV2,
    rule_family: str,
    *,
    availability: str = "available",
    status: str = "not_computed",
    values: tuple[str, ...] = (),
    rule_ids: tuple[str, ...] = (),
    evidence_ids: tuple[str, ...] = (),
    failure_codes: tuple[str, ...] = (),
) -> CalibrationExtractionV2:
    return CalibrationExtractionV2(
        schema_version=CALIBRATION_EXTRACTION_SCHEMA_V2,
        suite_version=DOMAIN_CALIBRATION_SUITE_V2,
        observation_id=observation.observation_id,
        rule_family=rule_family,
        availability=availability,  # type: ignore[arg-type]
        actual_status=status,  # type: ignore[arg-type]
        actual_values=values,
        actual_rule_ids=rule_ids,
        actual_evidence_ids=evidence_ids,
        failure_codes=failure_codes,
        response_sha256s=(
            observation.analysis_response_sha256,
            observation.report_response_sha256,
        ),
    )


def _response_pair_for_extraction(
    observation: CalibrationObservationV2,
) -> tuple[JsonObject, JsonObject]:
    if not isinstance(observation, CalibrationObservationV2):
        raise TypeError("observation must be CalibrationObservationV2")
    try:
        return _validate_response_pair(
            observation.analysis_response_json,
            observation.report_response_json,
        )
    except CalibrationApplicationExecutionErrorV2:
        raise CalibrationExtractionErrorV2(
            "application execution errors cannot produce domain extraction"
        ) from None
    except CalibrationObservationErrorV2:
        raise CalibrationExtractionErrorV2("observation responses are invalid") from None


def _terminal_extraction(
    observation: CalibrationObservationV2,
    rule_family: str,
    analysis: JsonObject,
    report: JsonObject,
) -> CalibrationExtractionV2 | None:
    status = analysis.get("status")
    if status == "ok":
        return None
    if _error_code(analysis) != _error_code(report):
        raise CalibrationExtractionErrorV2("terminal response codes do not match")
    code = _error_code(analysis)
    if status == "error" and code == "unsupported_input":
        return _extraction(
            observation,
            rule_family,
            failure_codes=("unsupported_input",),
        )
    if status == "refused" and code == "unsafe_request":
        safety = _mapping(analysis.get("safety"), "analysis safety")
        report_safety = _mapping(report.get("safety"), "report safety")
        if safety.get("categories") != report_safety.get("categories"):
            raise CalibrationExtractionErrorV2("safety categories do not match")
        categories = tuple(
            f"safety_category:{_text(item, 'safety category')}"
            for item in _sequence(safety.get("categories"), "safety categories")
        )
        return _extraction(
            observation,
            rule_family,
            values=categories,
            failure_codes=("unsafe_request",),
        )
    raise CalibrationExtractionErrorV2("application error has no domain result")


def _calculation_and_trace(
    analysis: JsonObject,
    report: JsonObject,
    rule_family: str,
) -> tuple[JsonObject, JsonObject, CalibrationActualStatusV2]:
    analysis_result = _mapping(analysis.get("result"), "analysis result")
    calculation = _mapping(analysis_result.get("calculation"), "calculation")
    report_result = _mapping(report.get("result"), "report result")
    report_body = _mapping(report_result.get("report"), "report body")
    expanded = _mapping(report_body.get("expanded_evidence"), "expanded evidence")
    conclusions = _sequence(expanded.get("formal_conclusions"), "formal conclusions")
    matching = [
        _mapping(item, "formal conclusion")
        for item in conclusions
        if isinstance(item, dict) and item.get("rule_family") == rule_family
    ]
    if len(matching) != 1:
        raise CalibrationExtractionErrorV2(
            "rule family must have exactly one formal conclusion"
        )
    conclusion = matching[0]
    expected_conclusion_id = f"formal_{rule_family}"
    if conclusion.get("conclusion_id") != expected_conclusion_id:
        raise CalibrationExtractionErrorV2("formal conclusion ID is invalid")
    trace = _mapping(conclusion.get("trace"), "formal trace")
    if trace.get("conclusion_id") != expected_conclusion_id:
        raise CalibrationExtractionErrorV2("formal trace crosses rule families")
    status = trace.get("calculation_status")
    if status not in {"not_computed", "computed", "indeterminate", "disputed"}:
        raise CalibrationExtractionErrorV2("formal status is invalid")
    return calculation, trace, cast(CalibrationActualStatusV2, status)


def _trace_ids(trace: JsonObject) -> tuple[tuple[str, ...], tuple[str, ...]]:
    rule_ids = tuple(
        _text(item, "rule ID")
        for item in _sequence(trace.get("rule_ids"), "rule IDs")
    )
    evidence_ids = tuple(
        _text(item, "evidence ID")
        for item in _sequence(trace.get("evidence_ids"), "evidence IDs")
    )
    return rule_ids, evidence_ids


def _sorted_values(values: list[str]) -> tuple[str, ...]:
    if any(not value for value in values):
        raise CalibrationExtractionErrorV2("actual value must be nonempty")
    return tuple(sorted(set(values)))


def _pattern_values(calculation: JsonObject, _status: str) -> tuple[str, ...]:
    strength = _mapping(calculation.get("strength"), "strength")
    values = [f"strength_label:{_text(strength.get('label'), 'strength label')}"]
    for item in _sequence(calculation.get("patterns"), "patterns"):
        pattern = _mapping(item, "pattern")
        values.append(
            "pattern:"
            f"{_text(pattern.get('pattern_id'), 'pattern ID')}:"
            f"rank={_number_token(pattern.get('rank'), 'pattern rank')}"
        )
    for item in _sequence(calculation.get("schools"), "schools"):
        school = _mapping(item, "school")
        school_id = _text(school.get("school_id"), "school ID")
        for pattern_id in _sequence(
            school.get("preferred_pattern_ids"), "preferred pattern IDs"
        ):
            values.append(
                f"school:{school_id}:pattern:{_text(pattern_id, 'pattern ID')}"
            )
    return _sorted_values(values)


def _five_element_values(calculation: JsonObject, _status: str) -> tuple[str, ...]:
    strength = _mapping(calculation.get("strength"), "strength")
    values = [
        f"strength_label:{_text(strength.get('label'), 'strength label')}",
        f"strength_score:{_number_token(strength.get('score'), 'strength score')}",
        f"strength_lower:{_number_token(strength.get('lower_bound'), 'lower bound')}",
        f"strength_upper:{_number_token(strength.get('upper_bound'), 'upper bound')}",
    ]
    for item in _sequence(strength.get("contributions"), "strength contributions"):
        contribution = _mapping(item, "strength contribution")
        values.append(
            "contribution:"
            f"{_text(contribution.get('category'), 'contribution category')}:"
            f"{_text(contribution.get('signal'), 'contribution signal')}:"
            f"{_number_token(contribution.get('value'), 'contribution value')}"
        )
    return _sorted_values(values)


def _useful_god_values(calculation: JsonObject, _status: str) -> tuple[str, ...]:
    values: list[str] = []
    for item in _sequence(calculation.get("useful_gods"), "useful gods"):
        candidate = _mapping(item, "useful god")
        values.append(
            "candidate:"
            f"{_text(candidate.get('method'), 'useful god method')}:"
            f"{_text(candidate.get('element'), 'useful god element')}:"
            f"rank={_number_token(candidate.get('rank'), 'useful god rank')}"
        )
    for item in _sequence(calculation.get("schools"), "schools"):
        school = _mapping(item, "school")
        school_id = _text(school.get("school_id"), "school ID")
        for element in _sequence(
            school.get("preferred_useful_god_elements"),
            "preferred useful god elements",
        ):
            values.append(
                f"school:{school_id}:useful_god:{_text(element, 'element')}"
            )
    return _sorted_values(values)


def _ten_god_values(calculation: JsonObject, _status: str) -> tuple[str, ...]:
    facts = _mapping(calculation.get("facts"), "facts")
    values: list[str] = []
    for item in _sequence(facts.get("exposed_stems"), "exposed stems"):
        fact = _mapping(item, "exposed stem")
        values.append(
            "exposed:"
            f"{_text(fact.get('pillar_name'), 'pillar name')}:"
            f"{_text(fact.get('stem'), 'stem')}:"
            f"{_text(fact.get('ten_god'), 'ten god')}"
        )
    for item in _sequence(facts.get("hidden_stems"), "hidden stems"):
        fact = _mapping(item, "hidden stem")
        values.append(
            "hidden:"
            f"{_text(fact.get('pillar_name'), 'pillar name')}:"
            f"{_text(fact.get('branch'), 'branch')}:"
            f"{_text(fact.get('stem'), 'stem')}:"
            f"{_text(fact.get('role'), 'hidden role')}:"
            f"{_text(fact.get('ten_god'), 'ten god')}"
        )
    return _sorted_values(values)


def _branch_values(calculation: JsonObject, _status: str) -> tuple[str, ...]:
    relations = _sequence(calculation.get("branch_relations"), "branch relations")
    if not relations:
        return ("branch_relations:none",)
    values: list[str] = []
    for item in relations:
        relation = _mapping(item, "branch relation")
        branches = ",".join(
            _text(value, "relation branch")
            for value in _sequence(relation.get("branches"), "relation branches")
        )
        pillars = ",".join(
            _text(value, "relation pillar")
            for value in _sequence(
                relation.get("pillar_names"), "relation pillar names"
            )
        )
        values.append(
            "relation:"
            f"{_text(relation.get('relation_type'), 'relation type')}:"
            f"{branches}:{pillars}:{_text(relation.get('state'), 'relation state')}"
        )
    return _sorted_values(values)


def _luck_cycle_values(calculation: JsonObject, status: str) -> tuple[str, ...]:
    if status == "not_computed":
        return ()
    luck = _mapping(calculation.get("luck_cycles"), "luck cycles")
    forward = luck.get("forward")
    if type(forward) is not bool:
        raise CalibrationExtractionErrorV2("luck direction must be boolean")
    values = [
        f"direction:{'forward' if forward else 'reverse'}",
        "start:"
        f"{_number_token(luck.get('start_years'), 'start years')}:"
        f"{_number_token(luck.get('start_months'), 'start months')}:"
        f"{_number_token(luck.get('start_days'), 'start days')}:"
        f"{_text(luck.get('start_solar'), 'start solar')}",
    ]
    for item in _sequence(luck.get("pillars"), "luck pillars"):
        pillar = _mapping(item, "luck pillar")
        values.append(
            "pillar:"
            f"{_number_token(pillar.get('index'), 'luck index')}:"
            f"{_text(pillar.get('gan_zhi'), 'luck gan zhi')}:"
            f"{_number_token(pillar.get('start_year'), 'luck start year')}:"
            f"{_number_token(pillar.get('end_year'), 'luck end year')}"
        )
    return _sorted_values(values)


def _extract_available_family(
    observation: CalibrationObservationV2,
    rule_family: str,
    value_builder: Callable[[JsonObject, str], tuple[str, ...]],
) -> CalibrationExtractionV2:
    analysis, report = _response_pair_for_extraction(observation)
    terminal = _terminal_extraction(observation, rule_family, analysis, report)
    if terminal is not None:
        return terminal
    calculation, trace, status = _calculation_and_trace(
        analysis,
        report,
        rule_family,
    )
    rule_ids, evidence_ids = _trace_ids(trace)
    return _extraction(
        observation,
        rule_family,
        status=status,
        values=value_builder(calculation, status),
        rule_ids=rule_ids,
        evidence_ids=evidence_ids,
    )


def _extract_pattern_strength(
    observation: CalibrationObservationV2,
) -> CalibrationExtractionV2:
    return _extract_available_family(
        observation, "pattern_strength", _pattern_values
    )


def _extract_five_element_balance(
    observation: CalibrationObservationV2,
) -> CalibrationExtractionV2:
    return _extract_available_family(
        observation, "five_element_balance", _five_element_values
    )


def _extract_useful_god_candidate(
    observation: CalibrationObservationV2,
) -> CalibrationExtractionV2:
    return _extract_available_family(
        observation, "useful_god_candidate", _useful_god_values
    )


def _extract_ten_god_relation(
    observation: CalibrationObservationV2,
) -> CalibrationExtractionV2:
    return _extract_available_family(
        observation, "ten_god_relation", _ten_god_values
    )


def _extract_branch_interaction(
    observation: CalibrationObservationV2,
) -> CalibrationExtractionV2:
    return _extract_available_family(
        observation, "branch_interaction", _branch_values
    )


def _extract_luck_cycle(
    observation: CalibrationObservationV2,
) -> CalibrationExtractionV2:
    return _extract_available_family(
        observation, "luck_cycle", _luck_cycle_values
    )


def _trace_family_values(
    trace: JsonObject,
    prefixes: tuple[str, ...],
    status: str,
) -> tuple[str, ...]:
    values = _sorted_values(
        [
            _text(item, "family supporting signal")
            for item in _sequence(
                trace.get("supporting_signals"),
                "family supporting signals",
            )
            if isinstance(item, str) and item.startswith(prefixes)
        ]
    )
    if status != "not_computed" and not values:
        raise CalibrationExtractionErrorV2(
            "explicit family output has no family-scoped values"
        )
    return values


def _extract_trace_family(
    observation: CalibrationObservationV2,
    rule_family: str,
    prefixes: tuple[str, ...],
) -> CalibrationExtractionV2:
    analysis, report = _response_pair_for_extraction(observation)
    terminal = _terminal_extraction(observation, rule_family, analysis, report)
    if terminal is not None:
        return terminal
    _calculation, trace, status = _calculation_and_trace(
        analysis,
        report,
        rule_family,
    )
    rule_ids, evidence_ids = _trace_ids(trace)
    return _extraction(
        observation,
        rule_family,
        status=status,
        values=_trace_family_values(trace, prefixes, status),
        rule_ids=rule_ids,
        evidence_ids=evidence_ids,
    )


def _extract_taboo_god_candidate(
    observation: CalibrationObservationV2,
) -> CalibrationExtractionV2:
    return _extract_trace_family(
        observation,
        "taboo_god_candidate",
        ("taboo_candidate:",),
    )


def _extract_blind_image_method(
    observation: CalibrationObservationV2,
) -> CalibrationExtractionV2:
    return _extract_trace_family(
        observation,
        "blind_image_method",
        ("blind_image:",),
    )


def _extract_remedy_boundary(
    observation: CalibrationObservationV2,
) -> CalibrationExtractionV2:
    return _extract_trace_family(
        observation,
        "remedy_boundary",
        ("remedy_condition:", "remedy_boundary:", "remedy_stop:"),
    )


def _extract_high_risk_signal(
    observation: CalibrationObservationV2,
) -> CalibrationExtractionV2:
    analysis, report = _response_pair_for_extraction(observation)
    terminal = _terminal_extraction(
        observation,
        "high_risk_signal",
        analysis,
        report,
    )
    if terminal is not None:
        return terminal
    _calculation, trace, status = _calculation_and_trace(
        analysis,
        report,
        "high_risk_signal",
    )
    if status != "not_computed":
        raise CalibrationExtractionErrorV2(
            "high-risk signal cannot become a computed prediction"
        )
    rule_ids, evidence_ids = _trace_ids(trace)
    return _extraction(
        observation,
        "high_risk_signal",
        status=status,
        rule_ids=rule_ids,
        evidence_ids=evidence_ids,
    )


_EXTRACTORS: dict[str, ExtractorV2] = {
    "pattern_strength": _extract_pattern_strength,
    "five_element_balance": _extract_five_element_balance,
    "useful_god_candidate": _extract_useful_god_candidate,
    "taboo_god_candidate": _extract_taboo_god_candidate,
    "ten_god_relation": _extract_ten_god_relation,
    "branch_interaction": _extract_branch_interaction,
    "blind_image_method": _extract_blind_image_method,
    "luck_cycle": _extract_luck_cycle,
    "remedy_boundary": _extract_remedy_boundary,
    "high_risk_signal": _extract_high_risk_signal,
}


def get_calibration_extractor_registry_v2() -> Mapping[str, ExtractorV2]:
    authoritative = get_formal_interpretation_rule_families()
    if tuple(_EXTRACTORS) != authoritative:
        raise CalibrationExtractionErrorV2(
            "V2 extractors do not match authoritative rule families"
        )
    return MappingProxyType(_EXTRACTORS)


def extract_calibration_family_v2(
    observation: CalibrationObservationV2,
    rule_family: str,
) -> CalibrationExtractionV2:
    try:
        extractor = get_calibration_extractor_registry_v2()[rule_family]
    except (KeyError, TypeError):
        raise CalibrationExtractionErrorV2(
            "rule family is not authoritative"
        ) from None
    return extractor(observation)
