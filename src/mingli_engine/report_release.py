from collections import Counter
import hashlib
from html import escape
import json
from pathlib import Path
from typing import Any

from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.calculation_validation import build_calculation_checks
from mingli_engine.high_risk import classify_high_risk_request
from mingli_engine.html import render_html_report
from mingli_engine.markdown import render_markdown_report
from mingli_engine.models import (
    BaziChart,
    BirthProfile,
    Report,
    ReportAcceptanceSummary,
    ReportReleaseCaseResult,
    ReportReleaseSummary,
)
from mingli_engine.report_acceptance import build_report_acceptance_summary
from mingli_engine.report_inputs import birth_profile_from_dict, chart_from_dict
from mingli_engine.report_schema import build_report
from mingli_engine.safety import safety_check
from mingli_engine.validation import validate_birth_profile


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = REPO_ROOT / "examples" / "report-regression-cases.json"
RELEASE_ID = "report_release_v1"
REQUIRED_CASE_FIELDS = frozenset({"id", "kind", "command", "input", "purpose"})
SUPPORTED_KINDS = frozenset(
    {"safe_markdown", "high_risk_markdown", "safety_json"}
)
SUPPORTED_COMMANDS = frozenset({"calculate-report", "generate-report"})
SAFE_SOURCE_TYPES = frozenset({"auto_calculated", "external_verified"})
ACTION_IDS = (
    "structure_calibration",
    "relationship_process_review",
    "selection_experiment",
    "stage_review",
)
EXPECTED_CASE_IDS = (
    "safe-auto-gregorian",
    "safe-external-verified",
    "unsafe-lifespan-focus",
    "high-risk-general-lifespan",
    "unsafe-exact-lifespan",
)
EXPECTED_CASE_CONTRACTS = {
    "safe-auto-gregorian": {
        "kind": "safe_markdown",
        "command": "calculate-report",
        "input": "examples/birth-profile.auto-gregorian.json",
        "source_type": "auto_calculated",
    },
    "safe-external-verified": {
        "kind": "safe_markdown",
        "command": "generate-report",
        "input": "examples/bazi-chart.external-verified.json",
        "source_type": "external_verified",
    },
    "unsafe-lifespan-focus": {
        "kind": "safety_json",
        "command": "calculate-report",
        "input": "examples/birth-profile.unsafe-focus.json",
        "expected_category": "lifespan_or_death_timing",
    },
    "high-risk-general-lifespan": {
        "kind": "high_risk_markdown",
        "command": "calculate-report",
        "input": "examples/birth-profile.high-risk-general.json",
        "source_type": "auto_calculated",
    },
    "unsafe-exact-lifespan": {
        "kind": "safety_json",
        "command": "calculate-report",
        "input": "examples/birth-profile.exact-lifespan.json",
        "expected_category": "lifespan_or_death_timing",
    },
}
INTERNAL_MARKERS = (
    "traditional_high_risk_signal_boundary",
    "focus_topic:",
    "stage_signal:",
)
MARKDOWN_LAYER_HEADINGS = (
    "## 快速导读",
    "## 第一层：基础资料",
    "## 第二层：结构观察",
    "## 第三层：解读边界",
    "## 第四层：行动反思",
    "## 术语简注",
    "## 伦理边界提醒",
)
HTML_LAYER_HEADINGS = tuple(
    heading.removeprefix("## ") for heading in MARKDOWN_LAYER_HEADINGS
)
PASS = "passed"
FAIL = "failed"


class ReportReleaseError(ValueError):
    pass


def _check(condition: bool) -> str:
    return PASS if condition else FAIL


def _status(checks: dict[str, str]) -> str:
    return PASS if checks and all(value == PASS for value in checks.values()) else FAIL


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReportReleaseError("report release fixture is unavailable") from error
    if not isinstance(payload, dict):
        raise ReportReleaseError("report release fixture has invalid shape")
    return payload


def _resolve_case_input(input_ref: str) -> Path:
    if not input_ref or Path(input_ref).is_absolute():
        raise ReportReleaseError("release case input must be a relative repository path")
    resolved = (REPO_ROOT / input_ref).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as error:
        raise ReportReleaseError("release case input escapes repository root") from error
    if not resolved.is_file():
        raise ReportReleaseError("report release case input is unavailable")
    return resolved


def _validate_case(case: Any) -> dict[str, Any]:
    if not isinstance(case, dict):
        raise ReportReleaseError("release manifest cases must be objects")
    if not REQUIRED_CASE_FIELDS.issubset(case):
        raise ReportReleaseError("release case is missing required fields")
    if not all(isinstance(case[field], str) for field in REQUIRED_CASE_FIELDS):
        raise ReportReleaseError("release case required fields must be strings")
    if not case["id"] or not case["purpose"]:
        raise ReportReleaseError("release case id and purpose must be non-empty")
    if case["kind"] not in SUPPORTED_KINDS:
        raise ReportReleaseError("report release case kind is unsupported")
    if case["command"] not in SUPPORTED_COMMANDS:
        raise ReportReleaseError("report release command is unsupported")
    _resolve_case_input(case["input"])

    if case["kind"] in {"safe_markdown", "high_risk_markdown"}:
        if case.get("source_type") not in SAFE_SOURCE_TYPES:
            raise ReportReleaseError("report release case has invalid source type")
    if case["kind"] == "safety_json":
        if not isinstance(case.get("expected_category"), str) or not case.get(
            "expected_category"
        ):
            raise ReportReleaseError("safety release case needs expected_category")
    return case


def load_report_release_manifest(
    manifest_path: Path | None = None,
) -> list[dict[str, Any]]:
    path = manifest_path or DEFAULT_MANIFEST_PATH
    try:
        cases = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReportReleaseError("cannot read report release manifest") from error
    if not isinstance(cases, list) or not cases:
        raise ReportReleaseError("report release manifest must be a non-empty list")

    validated = [_validate_case(case) for case in cases]
    case_ids = [case["id"] for case in validated]
    if len(case_ids) != len(set(case_ids)):
        raise ReportReleaseError("report release case ids must be unique")
    if case_ids != list(EXPECTED_CASE_IDS):
        raise ReportReleaseError("report release manifest does not match v1 case baseline")
    for case in validated:
        expected = EXPECTED_CASE_CONTRACTS[case["id"]]
        if any(case.get(field) != value for field, value in expected.items()):
            raise ReportReleaseError(
                "report release case does not match v1 contract"
            )
    return validated


def _load_case_chart(case: dict[str, Any]) -> tuple[BirthProfile, BaziChart | None]:
    payload = _load_json_object(_resolve_case_input(case["input"]))
    if case["command"] == "calculate-report":
        profile = birth_profile_from_dict(payload)
        return profile, None
    chart = chart_from_dict(payload)
    intake_review = validate_birth_profile(chart.birth_profile)
    if not intake_review.report_ready:
        raise ReportReleaseError("release chart fixture is not report ready")
    return chart.birth_profile, chart


def _request_categories(profile: BirthProfile) -> tuple[bool, list[str], bool]:
    high_risk = classify_high_risk_request(profile.focus_topic)
    safety = safety_check(profile.focus_topic, disclaimer_present=True)
    categories = list(dict.fromkeys([*high_risk.categories, *safety.red_line_categories]))
    return high_risk.allowed and safety.allowed, categories, high_risk.requires_narrowing


def _evidence_contract(report: Report) -> bool:
    audit = report.report_evidence_audit
    activation = report.knowledge_activation
    return (
        audit.audit_status in {"complete", "complete_with_guardrails"}
        and audit.traced_evidence_unit_count == activation.approved_evidence_count
        and audit.rule_family_count == len(activation.enabled_rule_families)
        and set(audit.enabled_rule_families)
        == set(activation.enabled_rule_families)
        and not audit.missing_rule_families
        and activation.activation_status in {"enabled", "enabled_with_guardrails"}
    )


def _action_contract(report: Report) -> bool:
    family_counts = Counter(
        family
        for item in report.action_reflection_items
        for family in item.rule_families
    )
    return (
        [item.action_id for item in report.action_reflection_items] == list(ACTION_IDS)
        and family_counts
        == Counter(
            {family: 1 for family in report.knowledge_activation.enabled_rule_families}
        )
        and all(
            item.status in {"ready", "ready_with_guardrails"}
            and item.evidence_ids
            and item.conditions
            and item.observation_prompt
            and item.feedback_metric
            and item.stop_boundary
            for item in report.action_reflection_items
        )
        and all(
            report.action_suggestions.count(f"{item.title}｜状态：") == 1
            for item in report.action_reflection_items
        )
        and "医疗、法律、心理、财务或寿命问题" in report.action_suggestions
        and all(marker not in report.action_suggestions for marker in INTERNAL_MARKERS)
    )


def _reader_sections(report: Report) -> tuple[str, ...]:
    return (
        report.disclaimer,
        report.quick_guide,
        report.chart_card,
        report.assumptions,
        report.four_pillars_summary,
        report.five_elements_summary,
        report.ten_gods_summary,
        report.evidence_notes,
        report.formal_synthesis,
        report.integrated_synthesis,
        report.structure_analysis,
        report.personality_tendencies,
        report.strengths_and_issues,
        report.phase_overview,
        report.action_suggestions,
        report.interpretation_boundaries,
        report.glossary,
        report.ethics_reminder,
    )


def _markdown_contract(report: Report, markdown: str) -> bool:
    return (
        markdown.startswith("# 八字结构化报告")
        and markdown.count("### 正式知识综合") == 1
        and markdown.count("### 综合脉络") == 1
        and markdown.count("### 行动建议") == 1
        and markdown.count(report.formal_synthesis) == 1
        and markdown.count(report.integrated_synthesis) == 1
        and markdown.count(report.action_suggestions) == 1
    )


def _html_contract(report: Report, html: str) -> bool:
    normalized = html.lower()
    return (
        html.startswith("<!doctype html>")
        and html.count("<main") == 1
        and html.count("<h3>正式知识综合</h3>") == 1
        and html.count("<h3>综合脉络</h3>") == 1
        and html.count("<h3>行动建议</h3>") == 1
        and html.count(report.formal_synthesis) == 1
        and html.count(report.integrated_synthesis) == 1
        and html.count(report.action_suggestions) == 1
        and "<script" not in normalized
        and "http://" not in normalized
        and "https://" not in normalized
    )


def _headings_are_unique_and_ordered(
    text: str,
    headings: tuple[str, ...],
) -> bool:
    cursor = 0
    for heading in headings:
        if text.count(heading) != 1:
            return False
        position = text.find(heading, cursor)
        if position == -1:
            return False
        cursor = position + len(heading)
    return True


def _report_fingerprint(report: Report) -> str:
    text = "\n".join(_reader_sections(report))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _evaluate_rejected_case(
    case: dict[str, Any],
    profile: BirthProfile,
) -> tuple[ReportReleaseCaseResult, None, int]:
    allowed, categories, _ = _request_categories(profile)
    checks = {
        "request_rejected": _check(not allowed),
        "expected_category": _check(case["expected_category"] in categories),
        "report_withheld": _check(not allowed),
    }
    return (
        ReportReleaseCaseResult(
            case_id=case["id"],
            scenario_type="rejected_request",
            status=_status(checks),
            output_formats=["json"],
            checks=checks,
            guardrails=["unsafe_report_not_constructed"],
        ),
        None,
        0,
    )


def _evaluate_report_case(
    case: dict[str, Any],
    profile: BirthProfile,
    chart: BaziChart | None,
) -> tuple[ReportReleaseCaseResult, str | None, int]:
    allowed, _, requires_narrowing = _request_categories(profile)
    if not allowed:
        checks = {"pre_report_safety": FAIL}
        return (
            ReportReleaseCaseResult(
                case_id=case["id"],
                scenario_type="release_case_error",
                status=FAIL,
                output_formats=[],
                checks=checks,
                guardrails=["unexpected_rejection_stopped_before_report"],
            ),
            None,
            0,
        )
    resolved_chart = chart or calculate_bazi_chart(profile)
    report = build_report(resolved_chart)
    markdown = render_markdown_report(report)
    html = render_html_report(report)
    internal_markers_filtered = all(
        marker not in markdown and marker not in html for marker in INTERNAL_MARKERS
    )
    checks = {
        "report_safety": _check(allowed and report.safety_review.allowed),
        "source_type_contract": _check(
            resolved_chart.chart_source.source_type == case["source_type"]
        ),
        "evidence_contract": _check(_evidence_contract(report)),
        "action_reflection": _check(_action_contract(report)),
        "markdown_contract": _check(_markdown_contract(report, markdown)),
        "html_contract": _check(_html_contract(report, html)),
        "cross_format_consistency": _check(
            _headings_are_unique_and_ordered(markdown, MARKDOWN_LAYER_HEADINGS)
            and _headings_are_unique_and_ordered(html, HTML_LAYER_HEADINGS)
            and all(
                markdown.count(text) == 1
                and html.count(escape(text, quote=True)) == 1
                for text in _reader_sections(report)
            )
        ),
        "internal_markers_filtered": _check(internal_markers_filtered),
    }
    scenario_type = "safe_report"
    guardrails = ["synthetic_fixture_not_persisted"]
    if case["kind"] == "high_risk_markdown":
        scenario_type = "guarded_high_risk_report"
        checks["high_risk_narrowing"] = _check(
            requires_narrowing
            and "高风险材料边界" in markdown
            and "高风险材料边界" in html
            and "传统风险信号" in markdown
            and "传统风险信号" in html
            and "不输出精确结果" in markdown
            and "不输出精确结果" in html
            and "不预测精确事件或寿命" in report.action_suggestions
        )
        guardrails.append("non_deterministic_high_risk_language")

    result = ReportReleaseCaseResult(
        case_id=case["id"],
        scenario_type=scenario_type,
        status=_status(checks),
        output_formats=["markdown", "html"],
        checks=checks,
        guardrails=guardrails,
    )
    fingerprint = _report_fingerprint(report) if result.status == PASS else None
    return result, fingerprint, len(report.action_reflection_items)


def _evaluate_case(
    case: dict[str, Any],
) -> tuple[ReportReleaseCaseResult, str | None, int]:
    try:
        profile, chart = _load_case_chart(case)
        if case["kind"] == "safety_json":
            return _evaluate_rejected_case(case, profile)
        return _evaluate_report_case(case, profile, chart)
    # This command is a privacy boundary: case failures become opaque results.
    except Exception:
        checks = {"case_execution": FAIL}
        return (
            ReportReleaseCaseResult(
                case_id=case["id"],
                scenario_type="release_case_error",
                status=FAIL,
                output_formats=[],
                checks=checks,
                guardrails=["fail_closed_without_profile_output"],
            ),
            None,
            0,
        )


def build_report_release_summary(
    manifest_path: Path | None = None,
    *,
    calculation_checks: dict[str, str] | None = None,
    acceptance_summary: ReportAcceptanceSummary | None = None,
) -> ReportReleaseSummary:
    manifest = load_report_release_manifest(manifest_path)
    resolved_calculation_checks = (
        dict(calculation_checks)
        if calculation_checks is not None
        else build_calculation_checks()
    )
    acceptance = acceptance_summary or build_report_acceptance_summary(
        calculation_checks=resolved_calculation_checks,
    )
    calculation_ready = bool(resolved_calculation_checks) and all(
        value == PASS for value in resolved_calculation_checks.values()
    )
    evaluations = [_evaluate_case(case) for case in manifest]
    cases = [result for result, _, _ in evaluations]
    fingerprints = {
        fingerprint for _, fingerprint, _ in evaluations if fingerprint is not None
    }
    action_counts = {count for _, _, count in evaluations if count}
    passed_case_count = sum(case.status == PASS for case in cases)

    expected_report_count = sum(
        case["kind"] != "safety_json" for case in manifest
    )
    outputs_distinct = len(fingerprints) == expected_report_count
    matrix_passed = passed_case_count == len(cases) and outputs_distinct
    acceptance_ready = acceptance.acceptance_status in {
        "ready",
        "ready_with_guardrails",
    }
    if not matrix_passed or not acceptance_ready or not calculation_ready:
        release_status = "blocked"
    elif acceptance.acceptance_status == "ready_with_guardrails":
        release_status = "ready_with_guardrails"
    else:
        release_status = "ready"

    if not calculation_ready:
        next_action = "repair_calculation_validation"
    elif not acceptance_ready:
        next_action = "repair_report_acceptance"
    elif not matrix_passed:
        next_action = "repair_report_release_matrix"
    elif release_status == "ready_with_guardrails":
        next_action = "enable_report_cli_with_guardrails"
    else:
        next_action = "enable_report_cli"

    return ReportReleaseSummary(
        release_id=RELEASE_ID,
        release_status=release_status,
        manifest_case_count=len(manifest),
        passed_case_count=passed_case_count,
        failed_case_count=len(cases) - passed_case_count,
        safe_report_case_count=sum(
            case["kind"] == "safe_markdown" for case in manifest
        ),
        guarded_report_case_count=sum(
            case["kind"] == "high_risk_markdown" for case in manifest
        ),
        rejected_request_case_count=sum(
            case["kind"] == "safety_json" for case in manifest
        ),
        distinct_report_output_count=len(fingerprints),
        acceptance_baseline_id=acceptance.baseline_id,
        acceptance_status=acceptance.acceptance_status,
        approved_evidence_count=acceptance.approved_evidence_count,
        rule_family_count=acceptance.rule_family_count,
        action_track_count=(next(iter(action_counts)) if len(action_counts) == 1 else 0),
        cases=cases,
        guardrails=[
            "synthetic_fixtures_not_persisted",
            "release_summary_excludes_profile_and_report_content",
            "source_library_013_012_read_only",
            "high_risk_outputs_require_narrowing_or_rejection",
        ],
        next_action=next_action,
    )
