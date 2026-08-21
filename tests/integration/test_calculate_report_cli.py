import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import mingli_engine.cli as cli
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.html import render_html_report
from mingli_engine.markdown import render_markdown_report
from mingli_engine.report_inputs import birth_profile_from_dict
from mingli_engine.report_schema import build_report


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
    assert markdown.count("### 综合脉络") == 1
    assert "综合状态：完整（含护栏）" in markdown
    assert "高风险与趋避只构成护栏关系" in markdown
    for title in ("结构校准", "关系过程复盘", "取用小实验", "阶段复盘"):
        assert markdown.count(f"{title}｜状态：") == 1
    assert markdown.count("观察问题：") == 4
    assert markdown.count("反馈记录：") == 4
    assert markdown.count("停止边界：") == 4
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
    assert "traced_evidence_units=996" in markdown
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
    assert "traced_evidence_units=996" in html
    assert html.count("盘面信号：") == 10
    assert "traditional_high_risk_signal_boundary" not in html
    assert html.count("<h3>正式知识综合</h3>") == 1
    assert html.count("<h3>综合脉络</h3>") == 1
    assert "综合状态：完整（含护栏）" in html
    assert "高风险与趋避只构成护栏关系" in html
    for title in ("结构校准", "关系过程复盘", "取用小实验", "阶段复盘"):
        assert html.count(f"{title}｜状态：") == 1
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


def test_calculate_report_analysis_outputs_reasoned_markdown():
    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--format",
        "markdown",
        "--analysis",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.count("# 八字结构化报告") == 1
    assert "## 推理分析" in result.stdout.splitlines()
    assert "### 盘面事实" in result.stdout.splitlines()
    assert "### 计算结果" in result.stdout.splitlines()
    assert "### 流派视角" in result.stdout.splitlines()
    assert "### 证据依据" in result.stdout.splitlines()
    assert "### 解读与安全边界" in result.stdout.splitlines()
    assert "- 计算状态：" in result.stdout
    assert "- 可信度：" in result.stdout
    for school_id in ("ziping", "liang_xiangrun", "duan"):
        escaped_school_id = school_id.replace("_", r"\_")
        assert f"school\\_view:{escaped_school_id}:" in result.stdout
    lowered = result.stdout.lower()
    for excluded in ("sensitivity", "weight", "tuning", "internal_config"):
        assert excluded not in lowered
    assumption_lines = [
        line for line in result.stdout.splitlines() if line.startswith("- 假设：")
    ]
    assert assumption_lines
    assert max(map(len, assumption_lines)) <= 1200
    assert len(result.stdout.splitlines()) <= 450


def test_calculate_report_analysis_outputs_reasoned_html():
    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--format",
        "html",
        "--analysis",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("<!doctype html>")
    assert result.stdout.count("<html") == 1
    assert ">推理分析<" in result.stdout
    assert "计算状态：" in result.stdout
    assert "可信度：" in result.stdout
    for heading in ("盘面事实", "计算结果", "流派视角", "证据依据", "解读与安全边界"):
        assert f">{heading}<" in result.stdout
    lowered = result.stdout.lower()
    for excluded in ("sensitivity", "weight", "tuning", "internal_config"):
        assert excluded not in lowered
    assumption_lines = [
        line for line in result.stdout.splitlines() if "<strong>假设：</strong>" in line
    ]
    assert assumption_lines
    assert max(map(len, assumption_lines)) <= 1200
    assert len(result.stdout.splitlines()) <= 550


def test_calculate_report_without_analysis_keeps_legacy_renderer_output():
    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--format",
        "markdown",
    )

    assert result.returncode == 0, result.stderr
    assert "## 推理分析" not in result.stdout
    assert "- 计算状态：" not in result.stdout


def test_calculate_report_default_markdown_is_byte_exact_renderer_output():
    profile_payload = json.loads(
        (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
            encoding="utf-8"
        )
    )
    report = build_report(
        calculate_bazi_chart(birth_profile_from_dict(profile_payload))
    )
    expected = render_markdown_report(report)

    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--format",
        "markdown",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == expected
    encoded = result.stdout.encode("utf-8")
    assert len(encoded) == 60505
    assert hashlib.sha256(encoded).hexdigest() == (
        "4023bd8b22157f516d9c0e3f6701aa1bfce0e1d1b06d08f107e006a89b52c28b"
    )


def test_calculate_report_default_html_is_byte_exact_renderer_output():
    profile_payload = json.loads(
        (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
            encoding="utf-8"
        )
    )
    report = build_report(
        calculate_bazi_chart(birth_profile_from_dict(profile_payload))
    )
    expected = render_html_report(report)

    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--format",
        "html",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == expected
    encoded = result.stdout.encode("utf-8")
    assert len(encoded) == 62428
    assert hashlib.sha256(encoded).hexdigest() == (
        "49db7416aa0e2fd7c280d840b6981df4113d6e7d34a9f00108938bb7e3c48796"
    )


def test_calculate_report_analysis_keeps_safety_refusal_shape():
    result = _run_cli(
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsafe-focus.json"),
        "--format",
        "html",
        "--analysis",
    )

    assert result.returncode == 3, result.stderr
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert "calculation" not in payload


def test_calculate_report_analysis_flag_does_not_change_refusal_bytes():
    args = (
        "calculate-report",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsafe-focus.json"),
        "--format",
        "markdown",
    )

    default = _run_cli(*args)
    analysis = _run_cli(*args, "--analysis")

    assert default.returncode == analysis.returncode == 3
    assert default.stdout == analysis.stdout
    assert default.stderr == analysis.stderr == ""


@pytest.mark.parametrize(
    "analysis_error",
    [
        ValueError("internal provider path: C:/private/provider.json"),
        RuntimeError("private inference implementation detail"),
    ],
)
def test_calculate_report_analysis_returns_controlled_inference_error(
    monkeypatch,
    analysis_error,
):
    profile = (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
        encoding="utf-8"
    )
    stdout = io.StringIO()
    stderr = io.StringIO()

    def fail_analysis(*args, **kwargs):
        raise analysis_error

    monkeypatch.setattr(cli, "analyze_bazi_chart", fail_analysis)
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(profile))
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    monkeypatch.setattr(cli.sys, "stderr", stderr)

    return_code = cli.main(
        [
            "calculate-report",
            "--input",
            "-",
            "--format",
            "markdown",
            "--analysis",
        ]
    )

    assert return_code == 1
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == "Analysis error: analysis could not be completed\n"
    assert "provider" not in stderr.getvalue().lower()
    assert "private" not in stderr.getvalue().lower()
    assert "traceback" not in stderr.getvalue().lower()


@pytest.mark.parametrize(
    "analysis_error",
    [
        ValueError("internal report config path: C:/private/report.json"),
        RuntimeError("private report synthesis detail"),
    ],
)
def test_calculate_report_analysis_controls_build_errors(
    monkeypatch,
    analysis_error,
):
    profile = (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
        encoding="utf-8"
    )
    stdout = io.StringIO()
    stderr = io.StringIO()

    def fail_build(*args, **kwargs):
        raise analysis_error

    monkeypatch.setattr(cli, "build_report", fail_build)
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(profile))
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    monkeypatch.setattr(cli.sys, "stderr", stderr)

    return_code = cli.main(
        [
            "calculate-report",
            "--input",
            "-",
            "--format",
            "html",
            "--analysis",
        ]
    )

    assert return_code == 1
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == "Analysis error: analysis could not be completed\n"
    assert "config" not in stderr.getvalue().lower()
    assert "private" not in stderr.getvalue().lower()
    assert "traceback" not in stderr.getvalue().lower()
