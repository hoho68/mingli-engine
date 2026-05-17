import os
import subprocess
import sys
from pathlib import Path

from mingli_engine.safety import safety_check


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


def test_generated_auto_report_avoids_absolute_or_fatalistic_phrases():
    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--format",
        "markdown",
    )

    assert result.returncode == 0, result.stderr
    markdown = result.stdout
    assert "## 快速导读" in markdown.splitlines()
    assert "## 第三层：解读边界" in markdown.splitlines()
    for prohibited_phrase in ("必定", "注定", "一定会", "死定"):
        assert prohibited_phrase not in markdown


def test_safety_check_blocks_lifespan_or_death_timing_request():
    result = safety_check("我什么时候会死？")

    assert result.allowed is False
    assert result.red_line_categories == ["lifespan_or_death_timing"]
    assert (
        "寿命或死亡时间" in result.redirect_message
        or "不预测寿命或死亡时间" in result.redirect_message
    )


def test_safety_check_blocks_common_lifespan_or_death_timing_questions():
    for text in ("我哪年会死？", "我几岁去世？"):
        result = safety_check(text)

        assert result.allowed is False
        assert "lifespan_or_death_timing" in result.red_line_categories


def test_safety_check_blocks_major_disaster_prediction():
    result = safety_check("我今年会不会出车祸？")

    assert result.allowed is False
    assert "major_disaster_prediction" in result.red_line_categories


def test_safety_check_blocks_deterministic_marriage_matching():
    result = safety_check("我们是不是命中注定结婚？")

    assert result.allowed is False
    assert "deterministic_marriage_matching" in result.red_line_categories


def test_safety_check_blocks_professional_advice_request():
    result = safety_check("这个八字能给我投资建议吗？")

    assert result.allowed is False
    assert "professional_advice" in result.red_line_categories


def test_safety_check_blocks_unauthorized_third_party_chart_request():
    result = safety_check("帮我看他的完整八字命盘，他没有同意。")

    assert result.allowed is False
    assert "unauthorized_third_party" in result.red_line_categories


def test_safety_check_blocks_paid_remedy_request():
    result = safety_check("我想买法器做法事来化解。")

    assert result.allowed is False
    assert "paid_remedy" in result.red_line_categories


def test_safety_check_blocks_absolute_or_fatalistic_phrases():
    result = safety_check("你今年一定会破财，这是注定的。")

    assert result.allowed is False
    assert {"注定", "一定会"}.issubset(set(result.prohibited_phrases))


def test_safety_check_allows_safe_disclaimer_with_absolute_phrase():
    result = safety_check("本报告不保证一定会发生，仅供自我观察。")

    assert result.allowed is True
    assert result.prohibited_phrases == []


def test_safety_check_allows_non_predictive_lifespan_statement():
    result = safety_check("本报告不预测寿命，只讨论风险意识和生活安排。")

    assert result.allowed is True
    assert result.red_line_categories == []


def test_safety_check_blocks_later_unsafe_phrase_after_safe_disclaimer():
    result = safety_check("本报告不保证一定会发生，但你今年一定会破财。")

    assert result.allowed is False
    assert "一定会" in result.prohibited_phrases


def test_safety_check_blocks_later_lifespan_prediction_after_safe_disclaimer():
    result = safety_check("本报告不预测寿命，但你想让我预测寿命也可以。")

    assert result.allowed is False
    assert result.red_line_categories == ["lifespan_or_death_timing"]
