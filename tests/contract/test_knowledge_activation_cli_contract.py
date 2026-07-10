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


def test_knowledge_activation_summary_cli_outputs_enabled_packet():
    result = _run_cli("knowledge-activation-summary")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["activation_status"] == "enabled_with_guardrails"
    assert payload["source_count"] == 29
    assert payload["report_usable_source_count"] == 28
    assert payload["approved_evidence_count"] == 111
    assert len(payload["enabled_rule_families"]) == 10
    assert payload["missing_rule_families"] == []
    assert payload["unavailable_conclusion_count"] == 0
    assert payload["open_conflicts"] == ["conflict_high_risk_scope_001"]
    assert payload["quality_failures"] == []
    assert (
        payload["next_action"]
        == "enable_for_reports_with_high_risk_guardrails"
    )
    assert any("high-risk" in guardrail for guardrail in payload["guardrails"])
