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


def test_project_completion_summary_cli_outputs_final_local_packet():
    result = _run_cli("project-completion-summary")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["baseline_id"] == "project_completion_v1"
    assert payload["completion_status"] == "complete_with_guardrails"
    assert payload["feature_count"] == 17
    assert payload["spec_count"] == 17
    assert payload["plan_count"] == 17
    assert payload["task_tracked_feature_count"] == 12
    assert payload["legacy_feature_count"] == 5
    assert payload["functional_requirement_count"] == 240
    assert payload["success_criteria_count"] == 122
    assert payload["checked_task_count"] == 1081
    assert payload["unchecked_task_count"] == 0
    assert payload["checked_checklist_item_count"] == 272
    assert payload["unchecked_checklist_item_count"] == 0
    assert payload["release_id"] == "report_release_v1"
    assert payload["release_status"] == "ready_with_guardrails"
    assert payload["acceptance_baseline_id"] == "report_acceptance_v1"
    assert payload["acceptance_status"] == "ready_with_guardrails"
    assert payload["remaining_local_blockers"] == []
    assert payload["next_action"] == (
        "local_delivery_complete_wait_for_new_material_or_explicit_remote_request"
    )
    assert all(value == "passed" for value in payload["quality_checks"].values())
    assert all(
        value == "passed" for value in payload["completion_checks"].values()
    )

    serialized = json.dumps(payload, ensure_ascii=False)
    for token in (
        "birth_date",
        "birth_time",
        "birthplace",
        "focus_topic",
        "1992-08-18",
        "上海市",
        "资料原文/",
        ".pdf",
        "https://",
        "origin/",
    ):
        assert token not in serialized
