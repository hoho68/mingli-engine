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


def test_report_release_summary_cli_outputs_private_release_packet():
    result = _run_cli("report-release-summary")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["release_id"] == "report_release_v1"
    assert payload["release_status"] == "ready_with_guardrails"
    assert payload["manifest_case_count"] == 5
    assert payload["passed_case_count"] == 5
    assert payload["failed_case_count"] == 0
    assert payload["safe_report_case_count"] == 2
    assert payload["guarded_report_case_count"] == 1
    assert payload["rejected_request_case_count"] == 2
    assert payload["distinct_report_output_count"] == 3
    assert payload["acceptance_baseline_id"] == "report_acceptance_v1"
    assert payload["acceptance_status"] == "ready_with_guardrails"
    assert payload["approved_evidence_count"] == 111
    assert payload["rule_family_count"] == 10
    assert payload["action_track_count"] == 4
    assert all(case["status"] == "passed" for case in payload["cases"])
    assert payload["next_action"] == "enable_report_cli_with_guardrails"

    serialized = json.dumps(payload, ensure_ascii=False)
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
