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
