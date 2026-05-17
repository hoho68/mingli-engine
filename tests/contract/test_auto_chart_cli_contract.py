import io
import json
import os
import subprocess
import sys
from pathlib import Path

import mingli_engine.cli as cli


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


def test_calculate_chart_outputs_auto_calculated_bazi_chart():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["chart_source"]["source_type"] == "auto_calculated"
    assert payload["chart_source"]["confidence"] == "medium"
    assert payload["chart_source"]["true_solar_time_applied"] is False
    assert "未人工复核" in payload["chart_source"]["source_note"]
    assert [pillar["gan_zhi"] for pillar in payload["pillars"]] == [
        "壬申",
        "戊申",
        "丙寅",
        "癸巳",
    ]


def test_calculate_chart_accepts_profile_from_stdin():
    profile = (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
        encoding="utf-8"
    )

    result = _run_cli("calculate-chart", "--input", "-", input_text=profile)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload["pillars"]) == 4


def test_calculate_chart_main_accepts_stringio_streams(monkeypatch):
    profile = (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
        encoding="utf-8"
    )
    stdout = io.StringIO()
    stderr = io.StringIO()
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(profile))
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    monkeypatch.setattr(cli.sys, "stderr", stderr)

    return_code = cli.main(["calculate-chart", "--input", "-"])

    assert return_code == 0, stderr.getvalue()
    payload = json.loads(stdout.getvalue())
    assert len(payload["pillars"]) == 4


def test_calculate_chart_reports_stable_error_for_unsupported_lunar_calendar():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsupported-lunar.json"),
    )

    assert result.returncode == 1
    assert "Invalid input" in result.stderr
    assert "calendar_type" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_chart_rejects_invalid_date(tmp_path):
    payload = json.loads(
        (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
            encoding="utf-8"
        )
    )
    payload["birth_date"] = "1992-02-31"
    input_path = tmp_path / "invalid-date.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    result = _run_cli("calculate-chart", "--input", str(input_path))

    assert result.returncode == 1
    assert "Invalid input" in result.stderr
    assert "birth_date" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_chart_rejects_invalid_time(tmp_path):
    payload = json.loads(
        (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
            encoding="utf-8"
        )
    )
    payload["birth_time"] = "25:99"
    input_path = tmp_path / "invalid-time.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    result = _run_cli("calculate-chart", "--input", str(input_path))

    assert result.returncode == 1
    assert "Invalid input" in result.stderr
    assert "birth_time" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_chart_outputs_safety_review_for_unsafe_focus():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsafe-focus.json"),
    )

    assert result.returncode == 3, result.stderr
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert "lifespan_or_death_timing" in payload["red_line_categories"]
