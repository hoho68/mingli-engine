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


def _assert_in_order(text: str, headings: tuple[str, ...]) -> None:
    lines = text.splitlines()
    positions = [lines.index(heading) for heading in headings]
    assert positions == sorted(positions)


RAW_READER_LABELS = (
    "auto_calculated",
    "external_verified",
    "medium",
    "gregorian",
    "year：",
    "month：",
    "day：",
    "hour：",
)


def _assert_plain_language_report(markdown: str) -> None:
    assert "公历" in markdown
    for pillar_name in ("年柱", "月柱", "日柱", "时柱"):
        assert f"- {pillar_name}：" in markdown
    for raw_label in RAW_READER_LABELS:
        assert raw_label not in markdown


def test_calculate_report_outputs_markdown_from_birth_profile():
    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--format",
        "markdown",
    )

    assert result.returncode == 0, result.stderr
    markdown = result.stdout
    assert "# 八字结构化报告" in markdown
    _assert_in_order(
        markdown,
        (
            "## 快速导读",
            "## 第一层：基础资料",
            "## 第二层：结构观察",
            "## 第三层：解读边界",
            "## 第四层：行动反思",
        ),
    )
    assert "### 排盘来源与假设" in markdown.splitlines()
    assert "### 四柱与五行摘要" in markdown.splitlines()
    assert "### 行动建议" in markdown.splitlines()
    assert markdown.count("### 正式知识综合") == 1
    _assert_plain_language_report(markdown)
    assert "系统自动排盘" in markdown
    assert "未人工复核" in markdown
    assert "中等可信度" in markdown
    assert "先核对资料与假设" in markdown
    assert "再看结构观察" in markdown
    assert "最后转成行动反思" in markdown
    assert "这些基础资料只说明排盘依据与采用假设，不直接构成命理结论" in markdown
    assert "结构观察提供的是线索，不是最终判断" in markdown
    assert "这些边界是为了防止过度断言" in markdown
    assert "行动反思只作为复盘提示" in markdown
    assert "五行数量可以先作为结构观察材料来看" in markdown
    assert "明面信号：" in markdown
    assert "藏干信号：" in markdown
    assert "合计信号：" in markdown
    assert "观察中心" in markdown
    assert "十神关系可以先按四个柱位理解为结构线索" in markdown
    assert "基础结构可以先看分布是否集中" in markdown
    assert "不做格局定论" in markdown
    assert "不做用神定论" in markdown
    assert "不做大运流年判断" in markdown
    assert "Knowledge activation: status=enabled_with_guardrails" in markdown
    assert "missing_rule_families=0" in markdown
    assert "conflict_high_risk_scope_001" in markdown
    assert "Report evidence audit: status=complete_with_guardrails" in markdown
    assert "traced_evidence_units=111" in markdown
    assert "rule_family=high_risk_signal" in markdown
    assert markdown.count("盘面信号：") == 10
    assert "traditional_high_risk_signal_boundary" not in markdown
    for old_phrase in (
        "五行信号观察：明面信号为",
        "这些数量用于观察结构分布",
        "基础结构观察：五行分布先看有无、多少与集中度。",
    ):
        assert old_phrase not in markdown
    for prohibited_phrase in ("必定", "注定", "一定会", "死定"):
        assert prohibited_phrase not in markdown


def test_calculate_report_outputs_complete_html_from_birth_profile():
    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--format",
        "html",
    )

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    html = result.stdout
    assert html.startswith("<!doctype html>")
    assert '<html lang="zh-CN">' in html
    assert '<meta charset="utf-8">' in html
    assert "<title>" in html
    assert "<style>" in html
    assert html.count("<main") == 1
    assert html.rstrip().endswith("</html>")
    assert "# " not in html
    assert "Knowledge activation: status=enabled_with_guardrails" in html
    assert "missing_rule_families=0" in html
    assert "Report evidence audit: status=complete_with_guardrails" in html
    assert "traced_evidence_units=111" in html
    assert html.count("盘面信号：") == 10
    assert "traditional_high_risk_signal_boundary" not in html
    assert html.count("<h3>正式知识综合</h3>") == 1
    assert "rule_family=high_risk_signal" in html
    _assert_plain_language_report(html)
    assert "<script" not in html.lower()
    assert "onclick=" not in html.lower()


def test_calculate_report_returns_exit_3_json_for_unsafe_focus_topic():
    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsafe-focus.json"),
        "--format",
        "markdown",
    )

    assert result.returncode == 3, result.stderr
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert "lifespan_or_death_timing" in payload["red_line_categories"]
