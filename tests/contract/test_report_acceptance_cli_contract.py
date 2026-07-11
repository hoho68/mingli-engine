import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_path = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else os.pathsep.join([src_path, env["PYTHONPATH"]])
    )
    return subprocess.run(
        [sys.executable, "-m", "mingli_engine.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def test_report_acceptance_summary_cli_outputs_release_baseline():
    result = _run_cli("report-acceptance-summary")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["baseline_id"] == "report_acceptance_v1"
    assert payload["acceptance_status"] == "ready_with_guardrails"
    assert payload["case_count"] == 4
    assert payload["passed_case_count"] == 4
    assert payload["activation_status"] == "enabled_with_guardrails"
    assert payload["report_audit_status"] == "complete_with_guardrails"
    assert payload["approved_evidence_count"] == 111
    assert payload["rule_family_count"] == 10
    assert payload["traced_evidence_unit_count"] == 111
    assert payload["missing_rule_families"] == []
    assert payload["open_conflicts"] == ["conflict_high_risk_scope_001"]
    assert [case["case_id"] for case in payload["cases"]] == [
        "ordinary_production_report",
        "conflict_guardrail",
        "high_risk_rejection",
        "unavailable_degradation",
    ]
    assert all(case["status"] == "passed" for case in payload["cases"])
    ordinary_case = next(
        case
        for case in payload["cases"]
        if case["case_id"] == "ordinary_production_report"
    )
    assert ordinary_case["checks"]["personalized_chart_signals"] == "passed"
    assert ordinary_case["checks"]["integrated_cross_family_synthesis"] == (
        "passed"
    )
    assert payload["next_action"] == "release_reports_with_guardrails"

    serialized = json.dumps(payload, ensure_ascii=False)
    for private_field in (
        "birth_date",
        "birth_time",
        "birthplace",
        "gender",
        "focus_topic",
    ):
        assert private_field not in serialized
