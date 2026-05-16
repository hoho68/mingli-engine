import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"


def _run_cli(
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
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
        input=input_text,
        capture_output=True,
        check=False,
    )


def test_validate_intake_outputs_report_ready_json_for_complete_profile():
    result = _run_cli(
        "validate-intake",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.complete.json"),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["report_ready"] is True


def test_validate_intake_accepts_json_from_stdin():
    profile = (EXAMPLES_DIR / "birth-profile.complete.json").read_text(encoding="utf-8")

    result = _run_cli("validate-intake", "--input", "-", input_text=profile)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["report_ready"] is True


def test_validate_intake_reports_stable_error_for_missing_required_field(tmp_path):
    input_path = tmp_path / "missing-profile.json"
    input_path.write_text(
        json.dumps({"calendar_type": "公历"}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = _run_cli("validate-intake", "--input", str(input_path))

    assert result.returncode != 0
    assert "Invalid input" in result.stderr
    assert "birth_date" in result.stderr
    assert "Traceback" not in result.stderr


def test_safety_check_outputs_lifespan_red_line_json():
    result = _run_cli(
        "safety-check",
        "--input",
        str(EXAMPLES_DIR / "red-line.lifespan.json"),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert "lifespan_or_death_timing" in payload["red_line_categories"]


def test_safety_check_reports_stable_error_for_missing_text(tmp_path):
    input_path = tmp_path / "missing-text.json"
    input_path.write_text("{}", encoding="utf-8")

    result = _run_cli("safety-check", "--input", str(input_path))

    assert result.returncode != 0
    assert "Invalid input" in result.stderr
    assert "text" in result.stderr
    assert "Traceback" not in result.stderr


def test_safety_check_reports_stable_error_for_non_string_text(tmp_path):
    input_path = tmp_path / "non-string-text.json"
    input_path.write_text(
        json.dumps({"text": []}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = _run_cli("safety-check", "--input", str(input_path))

    assert result.returncode != 0
    assert "Invalid input" in result.stderr
    assert "Traceback" not in result.stderr
