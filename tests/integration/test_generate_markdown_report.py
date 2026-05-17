import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"


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


def test_generate_report_outputs_expected_markdown_sections_and_source_note():
    result = _run_cli(
        "generate-report",
        "--input",
        str(EXAMPLES_DIR / "bazi-chart.external-verified.json"),
        "--format",
        "markdown",
    )

    assert result.returncode == 0, result.stderr
    markdown = result.stdout
    assert "# 八字结构化报告" in markdown
    assert "## 免责声明" in markdown
    assert "## 排盘来源与假设" in markdown
    assert "## 术语简注" in markdown
    assert "## 伦理边界提醒" in markdown
    assert "示例排盘由外部工具核对，仅用于 CLI 合约测试" in markdown
    assert "五行信号观察" in markdown
    assert "明面信号" in markdown
    assert "藏干" in markdown
    assert "观察中心" in markdown
    assert "十神结构观察" in markdown
    assert "基础结构观察" in markdown
    assert "不做格局定论" in markdown
    assert "不做用神定论" in markdown
    assert "不做大运流年判断" in markdown


def test_generate_report_returns_exit_2_json_for_incomplete_birth_profile(tmp_path):
    chart = json.loads(
        (EXAMPLES_DIR / "bazi-chart.external-verified.json").read_text(encoding="utf-8")
    )
    del chart["birth_profile"]["birth_time"]
    del chart["birth_profile"]["birthplace"]
    input_path = tmp_path / "chart-missing-birth-fields.json"
    input_path.write_text(json.dumps(chart, ensure_ascii=False), encoding="utf-8")

    result = _run_cli(
        "generate-report",
        "--input",
        str(input_path),
        "--format",
        "markdown",
    )

    assert result.returncode == 2, result.stderr
    payload = json.loads(result.stdout)
    assert payload["report_ready"] is False
    assert "birth_time" in payload["missing_fields"]
    assert "birthplace" in payload["missing_fields"]


def test_generate_report_returns_exit_3_json_for_unsafe_focus_topic(tmp_path):
    chart = json.loads(
        (EXAMPLES_DIR / "bazi-chart.external-verified.json").read_text(encoding="utf-8")
    )
    chart["birth_profile"]["focus_topic"] = "寿命"
    input_path = tmp_path / "chart-unsafe-focus-topic.json"
    input_path.write_text(json.dumps(chart, ensure_ascii=False), encoding="utf-8")

    result = _run_cli(
        "generate-report",
        "--input",
        str(input_path),
        "--format",
        "markdown",
    )

    assert result.returncode == 3, result.stderr
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert "lifespan_or_death_timing" in payload["red_line_categories"]


def test_generate_report_reports_stable_error_for_non_object_birth_profile(tmp_path):
    chart = json.loads(
        (EXAMPLES_DIR / "bazi-chart.external-verified.json").read_text(encoding="utf-8")
    )
    chart["birth_profile"] = []
    input_path = tmp_path / "chart-list-birth-profile.json"
    input_path.write_text(json.dumps(chart, ensure_ascii=False), encoding="utf-8")

    result = _run_cli(
        "generate-report",
        "--input",
        str(input_path),
        "--format",
        "markdown",
    )

    assert result.returncode != 0
    assert "Invalid input" in result.stderr
    assert "Traceback" not in result.stderr


def test_generate_report_reports_stable_error_for_non_list_pillars(tmp_path):
    chart = json.loads(
        (EXAMPLES_DIR / "bazi-chart.external-verified.json").read_text(encoding="utf-8")
    )
    chart["pillars"] = {}
    input_path = tmp_path / "chart-object-pillars.json"
    input_path.write_text(json.dumps(chart, ensure_ascii=False), encoding="utf-8")

    result = _run_cli(
        "generate-report",
        "--input",
        str(input_path),
        "--format",
        "markdown",
    )

    assert result.returncode != 0
    assert "Invalid input" in result.stderr
    assert "Traceback" not in result.stderr


def test_generate_report_reports_stable_error_for_empty_pillars(tmp_path):
    chart = json.loads(
        (EXAMPLES_DIR / "bazi-chart.external-verified.json").read_text(encoding="utf-8")
    )
    chart["pillars"] = []
    input_path = tmp_path / "chart-empty-pillars.json"
    input_path.write_text(json.dumps(chart, ensure_ascii=False), encoding="utf-8")

    result = _run_cli(
        "generate-report",
        "--input",
        str(input_path),
        "--format",
        "markdown",
    )

    assert result.returncode == 1
    assert "Invalid input" in result.stderr
    assert "Traceback" not in result.stderr
    assert not result.stdout.startswith("# ")
