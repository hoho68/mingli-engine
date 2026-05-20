import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"
MANIFEST_PATH = EXAMPLES_DIR / "report-regression-cases.json"

REQUIRED_FIELDS = {"id", "kind", "command", "input", "purpose"}
SUPPORTED_KINDS = {"safe_markdown", "safety_json"}
SUPPORTED_COMMANDS = {"calculate-report", "generate-report"}
SAFE_SOURCE_TYPES = {"auto_calculated", "external_verified"}
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
ABSOLUTE_DESTINY_PHRASES = ("必定", "注定", "一定会", "死定")
LAYER_HEADINGS = (
    "## 快速导读",
    "## 第一层：基础资料",
    "## 第二层：结构观察",
    "## 第三层：解读边界",
    "## 第四层：行动反思",
)


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


def _load_cases() -> list[dict[str, Any]]:
    assert MANIFEST_PATH.exists(), "Missing report regression manifest"
    cases = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(cases, list)
    assert cases
    return cases


def _assert_in_order(text: str, headings: tuple[str, ...]) -> None:
    search_from = 0
    for heading in headings:
        position = text.find(heading, search_from)
        assert position != -1, heading
        search_from = position + len(heading)


def _safe_markdown_cases() -> list[dict[str, Any]]:
    cases = [
        case for case in _load_cases() if case.get("kind") == "safe_markdown"
    ]
    source_types = {case.get("source_type") for case in cases}
    assert "auto_calculated" in source_types
    assert "external_verified" in source_types
    return cases


def _safety_json_cases() -> list[dict[str, Any]]:
    cases = [case for case in _load_cases() if case.get("kind") == "safety_json"]
    assert cases
    return cases


def _assert_safe_case_shape(case: dict[str, Any]) -> None:
    _assert_manifest_case_shape(case)
    assert case.get("kind") == "safe_markdown"


def _assert_safety_case_shape(case: dict[str, Any]) -> None:
    _assert_manifest_case_shape(case)
    assert case.get("kind") == "safety_json"


def _assert_manifest_case_shape(case: dict[str, Any]) -> None:
    assert REQUIRED_FIELDS.issubset(case), case
    assert case.get("id")
    assert case.get("kind") in SUPPORTED_KINDS
    assert case.get("command") in SUPPORTED_COMMANDS
    assert case.get("purpose")
    input_ref = case.get("input")
    assert isinstance(input_ref, str)
    assert (REPO_ROOT / input_ref).exists(), case
    if case["kind"] == "safe_markdown":
        assert case.get("source_type") in SAFE_SOURCE_TYPES
    if case["kind"] == "safety_json":
        assert case.get("expected_category")


def _assert_safe_markdown(
    case: dict[str, Any], result: subprocess.CompletedProcess[str]
) -> None:
    assert result.returncode == 0, result.stderr
    markdown = result.stdout
    assert markdown.startswith("# 八字结构化报告")
    assert "## 免责声明" in markdown
    _assert_in_order(markdown, LAYER_HEADINGS)
    assert "### 排盘来源与假设" in markdown.splitlines()
    assert "### 四柱与五行摘要" in markdown.splitlines()
    assert "### 行动建议" in markdown.splitlines()
    assert "公历" in markdown
    for pillar_name in ("年柱", "月柱", "日柱", "时柱"):
        assert f"- {pillar_name}：" in markdown
    assert "五行数量可以先作为结构观察材料来看" in markdown
    assert "十神关系可以先按四个柱位理解为结构线索" in markdown
    assert "基础结构可以先看分布是否集中" in markdown
    assert "先核对资料与假设" in markdown
    assert "结构观察提供的是线索，不是最终判断" in markdown
    assert "这些边界是为了防止过度断言" in markdown
    assert "行动反思只作为复盘提示" in markdown
    for raw_label in RAW_READER_LABELS:
        assert raw_label not in markdown
    for phrase in ABSOLUTE_DESTINY_PHRASES:
        assert phrase not in markdown
    if case["source_type"] == "auto_calculated":
        assert "系统自动排盘" in markdown
        assert "中等可信度" in markdown
    if case["source_type"] == "external_verified":
        assert "外部排盘已核对" in markdown
        assert "来源类型：系统自动排盘" not in markdown


def _assert_safety_json(
    case: dict[str, Any], result: subprocess.CompletedProcess[str]
) -> None:
    assert result.returncode == 3, result.stderr
    assert not result.stdout.startswith("# 八字结构化报告")
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert case["expected_category"] in payload["red_line_categories"]


def test_manifest_lists_safe_markdown_regression_cases():
    cases = _safe_markdown_cases()
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids))
    for case in cases:
        _assert_safe_case_shape(case)


def test_manifest_lists_safety_json_regression_cases():
    for case in _safety_json_cases():
        _assert_safety_case_shape(case)


def test_report_regression_manifest_is_self_validating():
    cases = _load_cases()
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids))
    for case in cases:
        _assert_manifest_case_shape(case)
    assert any(
        case["kind"] == "safe_markdown"
        and case.get("source_type") == "auto_calculated"
        for case in cases
    )
    assert any(
        case["kind"] == "safe_markdown"
        and case.get("source_type") == "external_verified"
        for case in cases
    )
    assert any(case["kind"] == "safety_json" for case in cases)


def test_manifest_validation_rejects_invalid_case_shapes():
    valid_case = {
        "id": "safe-auto-gregorian",
        "kind": "safe_markdown",
        "command": "calculate-report",
        "input": "examples/birth-profile.auto-gregorian.json",
        "purpose": "Guards a valid safe Markdown case.",
        "source_type": "auto_calculated",
    }
    invalid_cases = (
        valid_case | {"id": ""},
        valid_case | {"kind": "unsupported"},
        valid_case | {"command": "new-command"},
        valid_case | {"input": "examples/missing-case.json"},
        valid_case | {"purpose": ""},
        valid_case | {"source_type": "raw"},
        {
            "id": "unsafe-lifespan-focus",
            "kind": "safety_json",
            "command": "calculate-report",
            "input": "examples/birth-profile.unsafe-focus.json",
            "purpose": "Guards safety JSON cases.",
        },
    )

    for case in invalid_cases:
        with pytest.raises(AssertionError):
            _assert_manifest_case_shape(case)


def test_safe_markdown_regression_cases_keep_report_contracts():
    for case in _safe_markdown_cases():
        result = _run_cli(
            case["command"],
            "--input",
            str(REPO_ROOT / case["input"]),
            "--format",
            "markdown",
        )
        _assert_safe_markdown(case, result)


def test_safety_json_regression_cases_keep_refusal_contracts():
    for case in _safety_json_cases():
        result = _run_cli(
            case["command"],
            "--input",
            str(REPO_ROOT / case["input"]),
            "--format",
            "markdown",
        )
        _assert_safety_json(case, result)
