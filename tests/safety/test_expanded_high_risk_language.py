import json
import os
import subprocess
import sys
from pathlib import Path

from mingli_engine.safety import safety_check


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


def test_safety_check_allows_general_high_risk_signal_language():
    result = safety_check("请分析重大灾厄信号，作为传统风险信号，不保证发生。")

    assert result.allowed is True
    assert result.red_line_categories == []


def test_safety_check_still_blocks_exact_outcome_and_diagnosis_requests():
    cases = {
        "请算我能活到几岁": "lifespan_or_death_timing",
        "请诊断我是什么病并给治疗方案": "professional_advice",
    }

    for text, category in cases.items():
        result = safety_check(text)

        assert result.allowed is False
        assert category in result.red_line_categories


def test_cli_allows_lifespan_focus_as_narrowed_markdown(tmp_path):
    profile_path = tmp_path / "lifespan-focus.json"
    profile_path.write_text(
        json.dumps(
            {
                "calendar_type": "gregorian",
                "birth_date": "1992-08-18",
                "birth_time": "09:30",
                "birthplace": "上海市",
                "gender": "未指定",
                "focus_topic": "寿命",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = _run_cli(
        "calculate-report",
        "--input",
        str(profile_path),
        "--format",
        "markdown",
    )

    assert result.returncode == 0, result.stderr
    assert "高风险材料边界" in result.stdout
    assert "传统风险信号" in result.stdout
    for prohibited_phrase in ("必定", "注定", "一定会", "死定"):
        assert prohibited_phrase not in result.stdout
