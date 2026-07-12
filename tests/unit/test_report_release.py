import json
from dataclasses import asdict, replace

import pytest

from mingli_engine import report_release
from mingli_engine import cli
from mingli_engine.report_acceptance import build_report_acceptance_summary
from mingli_engine.report_release import (
    ReportReleaseError,
    build_report_release_summary,
    load_report_release_manifest,
)
from mingli_engine.report_inputs import birth_profile_from_dict


EXPECTED_CASE_IDS = [
    "safe-auto-gregorian",
    "safe-external-verified",
    "unsafe-lifespan-focus",
    "high-risk-general-lifespan",
    "unsafe-exact-lifespan",
]


def _case_by_id(summary, case_id: str):
    return next(case for case in summary.cases if case.case_id == case_id)


def _write_manifest(path, cases) -> None:
    path.write_text(json.dumps(cases, ensure_ascii=False), encoding="utf-8")


def _valid_case() -> dict[str, str]:
    return {
        "id": "safe-auto-gregorian",
        "kind": "safe_markdown",
        "command": "calculate-report",
        "input": "examples/birth-profile.auto-gregorian.json",
        "purpose": "Guards a synthetic safe report.",
        "source_type": "auto_calculated",
    }


def test_release_summary_certifies_tracked_anonymous_matrix():
    summary = build_report_release_summary()

    assert summary.release_id == "report_release_v1"
    assert summary.release_status == "ready_with_guardrails"
    assert summary.manifest_case_count == 5
    assert summary.passed_case_count == 5
    assert summary.failed_case_count == 0
    assert summary.safe_report_case_count == 2
    assert summary.guarded_report_case_count == 1
    assert summary.rejected_request_case_count == 2
    assert summary.distinct_report_output_count == 3
    assert summary.acceptance_baseline_id == "report_acceptance_v1"
    assert summary.acceptance_status == "ready_with_guardrails"
    assert summary.approved_evidence_count == 111
    assert summary.rule_family_count == 10
    assert summary.action_track_count == 4
    assert [case.case_id for case in summary.cases] == EXPECTED_CASE_IDS
    assert all(case.status == "passed" for case in summary.cases)
    assert summary.next_action == "enable_report_cli_with_guardrails"
    assert "synthetic_fixtures_not_persisted" in summary.guardrails
    assert "source_library_013_012_read_only" in summary.guardrails


def test_safe_release_cases_cover_evidence_actions_and_both_formats():
    summary = build_report_release_summary()

    for case_id in ("safe-auto-gregorian", "safe-external-verified"):
        case = _case_by_id(summary, case_id)
        assert case.scenario_type == "safe_report"
        assert case.output_formats == ["markdown", "html"]
        assert case.checks == {
            "report_safety": "passed",
            "source_type_contract": "passed",
            "evidence_contract": "passed",
            "action_reflection": "passed",
            "markdown_contract": "passed",
            "html_contract": "passed",
            "cross_format_consistency": "passed",
            "internal_markers_filtered": "passed",
        }


def test_guarded_and_rejected_release_cases_keep_narrow_boundaries():
    summary = build_report_release_summary()
    guarded = _case_by_id(summary, "high-risk-general-lifespan")

    assert guarded.scenario_type == "guarded_high_risk_report"
    assert guarded.output_formats == ["markdown", "html"]
    assert guarded.checks["high_risk_narrowing"] == "passed"
    assert guarded.checks["action_reflection"] == "passed"
    assert "non_deterministic_high_risk_language" in guarded.guardrails

    for case_id in ("unsafe-lifespan-focus", "unsafe-exact-lifespan"):
        case = _case_by_id(summary, case_id)
        assert case.scenario_type == "rejected_request"
        assert case.output_formats == ["json"]
        assert case.checks == {
            "request_rejected": "passed",
            "expected_category": "passed",
            "report_withheld": "passed",
        }


def test_release_summary_serialization_excludes_fixture_inputs_and_profile_data():
    serialized = json.dumps(
        asdict(build_report_release_summary()),
        ensure_ascii=False,
    )

    for private_token in (
        "birth_date",
        "birth_time",
        "birthplace",
        "gender",
        "focus_topic",
        "1992-08-18",
        "09:30",
        "上海市",
        "职业规划与长期学习节奏",
        "寿命多长",
        "examples/",
    ):
        assert private_token not in serialized


@pytest.mark.parametrize(
    "cases",
    [
        {"not": "a list"},
        [],
        [_valid_case(), _valid_case()],
        [_valid_case() | {"id": ""}],
        [_valid_case() | {"kind": "unsupported"}],
        [_valid_case() | {"command": "unknown-command"}],
        [_valid_case() | {"input": "../outside.json"}],
        [_valid_case() | {"purpose": ""}],
        [_valid_case() | {"source_type": "raw"}],
    ],
)
def test_manifest_validation_fails_closed(tmp_path, cases):
    manifest = tmp_path / "release-cases.json"
    _write_manifest(manifest, cases)

    with pytest.raises(ReportReleaseError):
        load_report_release_manifest(manifest)


def test_manifest_cannot_drop_or_rename_required_release_cases(tmp_path):
    cases = load_report_release_manifest()
    reduced_manifest = tmp_path / "reduced-release.json"
    renamed_manifest = tmp_path / "renamed-release.json"
    _write_manifest(reduced_manifest, cases[:-1])
    _write_manifest(
        renamed_manifest,
        [cases[0] | {"id": "case-1992-08-18"}, *cases[1:]],
    )

    with pytest.raises(ReportReleaseError):
        load_report_release_manifest(reduced_manifest)
    with pytest.raises(ReportReleaseError):
        load_report_release_manifest(renamed_manifest)


def test_manifest_cannot_replace_fixed_case_definitions(tmp_path):
    cases = load_report_release_manifest()
    first = cases[0]
    second = cases[1]
    cases[0] = first | {
        "command": second["command"],
        "input": second["input"],
        "source_type": second["source_type"],
    }
    cases[1] = second | {
        "command": first["command"],
        "input": first["input"],
        "source_type": first["source_type"],
    }
    manifest = tmp_path / "replaced-cases.json"
    _write_manifest(manifest, cases)

    with pytest.raises(ReportReleaseError):
        load_report_release_manifest(manifest)


def test_manifest_errors_do_not_echo_input_references(tmp_path):
    cases = load_report_release_manifest()
    private_ref = "examples/missing-private-1992-08-18.json"
    cases[0] = cases[0] | {"input": private_ref}
    manifest = tmp_path / "missing-input.json"
    _write_manifest(manifest, cases)

    with pytest.raises(ReportReleaseError) as error:
        load_report_release_manifest(manifest)

    assert private_ref not in str(error.value)
    assert "1992-08-18" not in str(error.value)


def test_release_matrix_blocks_source_type_mismatch(tmp_path):
    cases = load_report_release_manifest()
    cases[0] = cases[0] | {"source_type": "external_verified"}
    manifest = tmp_path / "source-mismatch.json"
    _write_manifest(manifest, cases)

    with pytest.raises(ReportReleaseError):
        build_report_release_summary(manifest)


def test_release_matrix_blocks_cross_format_content_loss(monkeypatch):
    original = report_release.render_html_report

    def render_without_disclaimer(report):
        return original(report).replace(report.disclaimer, "")

    monkeypatch.setattr(report_release, "render_html_report", render_without_disclaimer)

    summary = build_report_release_summary()

    assert summary.release_status == "blocked"
    assert any(
        case.checks.get("cross_format_consistency") == "failed"
        for case in summary.cases
    )


def test_release_matrix_blocks_cross_format_heading_reordering(monkeypatch):
    original = report_release.render_html_report

    def render_with_reordered_sections(report):
        html = original(report)
        return html.replace("第三层：解读边界", "TEMP_HEADING").replace(
            "第四层：行动反思",
            "第三层：解读边界",
        ).replace("TEMP_HEADING", "第四层：行动反思")

    monkeypatch.setattr(report_release, "render_html_report", render_with_reordered_sections)

    summary = build_report_release_summary()

    assert summary.release_status == "blocked"
    assert any(
        case.checks.get("cross_format_consistency") == "failed"
        for case in summary.cases
    )


def test_release_matrix_requires_high_risk_boundary_in_html(monkeypatch):
    original = report_release.render_html_report

    def render_without_high_risk_boundary(report):
        return original(report).replace("高风险材料边界", "")

    monkeypatch.setattr(
        report_release,
        "render_html_report",
        render_without_high_risk_boundary,
    )

    summary = build_report_release_summary()
    guarded = _case_by_id(summary, "high-risk-general-lifespan")

    assert summary.release_status == "blocked"
    assert guarded.checks["high_risk_narrowing"] == "failed"


def test_release_matrix_requires_each_action_rule_family_once(monkeypatch):
    original = report_release.build_report

    def build_with_duplicate_action_family(chart):
        report = original(chart)
        first = report.action_reflection_items[0]
        duplicated = replace(
            first,
            rule_families=[*first.rule_families, first.rule_families[0]],
        )
        return replace(
            report,
            action_reflection_items=[duplicated, *report.action_reflection_items[1:]],
        )

    monkeypatch.setattr(report_release, "build_report", build_with_duplicate_action_family)

    summary = build_report_release_summary()

    assert summary.release_status == "blocked"
    assert any(
        case.checks.get("action_reflection") == "failed"
        for case in summary.cases
    )


def test_rejected_case_never_calls_report_builder_or_renderers(monkeypatch):
    case = next(
        case
        for case in load_report_release_manifest()
        if case["kind"] == "safety_json"
    )

    def unexpected_call(*args, **kwargs):
        raise AssertionError("rejected request reached report construction")

    monkeypatch.setattr(report_release, "build_report", unexpected_call)
    monkeypatch.setattr(report_release, "render_markdown_report", unexpected_call)
    monkeypatch.setattr(report_release, "render_html_report", unexpected_call)

    result, fingerprint, action_count = report_release._evaluate_case(case)

    assert result.status == "passed"
    assert result.checks["report_withheld"] == "passed"
    assert fingerprint is None
    assert action_count == 0


def test_unexpected_rejection_in_report_case_stops_before_construction(monkeypatch):
    case = load_report_release_manifest()[0]
    payload = json.loads(
        (
            report_release.REPO_ROOT
            / "examples"
            / "birth-profile.exact-lifespan.json"
        ).read_text(encoding="utf-8")
    )
    profile = birth_profile_from_dict(payload)

    def unexpected_call(*args, **kwargs):
        raise AssertionError("rejected request reached report construction")

    monkeypatch.setattr(report_release, "calculate_bazi_chart", unexpected_call)
    monkeypatch.setattr(report_release, "build_report", unexpected_call)

    result, fingerprint, action_count = report_release._evaluate_report_case(
        case,
        profile,
        None,
    )

    assert result.status == "failed"
    assert result.checks == {"pre_report_safety": "failed"}
    assert fingerprint is None
    assert action_count == 0


def test_release_matrix_blocks_when_report_outputs_collapse(monkeypatch):
    monkeypatch.setattr(report_release, "_report_fingerprint", lambda report: "same")

    summary = build_report_release_summary()

    assert summary.distinct_report_output_count == 1
    assert summary.release_status == "blocked"
    assert summary.next_action == "repair_report_release_matrix"


def test_release_matrix_converts_unexpected_case_error_to_private_failure(
    monkeypatch,
):
    def fail_renderer(report):
        raise RuntimeError("private path E:/secret/profile.json")

    monkeypatch.setattr(report_release, "render_html_report", fail_renderer)

    summary = build_report_release_summary()
    serialized = json.dumps(asdict(summary), ensure_ascii=False)

    assert summary.release_status == "blocked"
    assert any(case.checks == {"case_execution": "failed"} for case in summary.cases)
    assert "E:/secret/profile.json" not in serialized
    assert "RuntimeError" not in serialized


def test_release_summary_blocks_when_report_acceptance_is_blocked(monkeypatch):
    blocked = replace(
        build_report_acceptance_summary(),
        acceptance_status="blocked",
    )
    monkeypatch.setattr(
        report_release,
        "build_report_acceptance_summary",
        lambda: blocked,
    )

    summary = build_report_release_summary()

    assert summary.release_status == "blocked"
    assert summary.passed_case_count == 5
    assert summary.acceptance_status == "blocked"
    assert summary.next_action == "repair_report_acceptance"


def test_release_summary_blocks_failed_calculation_validation(monkeypatch):
    monkeypatch.setattr(
        report_release,
        "build_calculation_checks",
        lambda: {"stages_present": "failed"},
    )

    summary = build_report_release_summary()

    assert summary.release_status == "blocked"
    assert summary.next_action == "repair_calculation_validation"


def test_release_cli_handler_returns_nonzero_for_blocked_packet(
    monkeypatch,
    capsys,
):
    blocked = replace(
        build_report_release_summary(),
        release_status="blocked",
        next_action="repair_report_release_matrix",
    )
    monkeypatch.setattr(cli, "build_report_release_summary", lambda: blocked)

    exit_code = cli._report_release_summary(None)
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 4
    assert payload["release_status"] == "blocked"
