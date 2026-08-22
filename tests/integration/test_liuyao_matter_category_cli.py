"""End-to-end CLI tests for the optional matter category input (021 follow-up)."""

import json
import subprocess
import sys

_BASE_PAYLOAD = {
    "cast_mode": "explicit",
    "cast_datetime": "1990-02-28T08:30",
    "lines": [
        {"position": 1, "yin_yang": "yang", "moving": False},
        {"position": 2, "yin_yang": "yang", "moving": False},
        {"position": 3, "yin_yang": "yang", "moving": False},
        {"position": 4, "yin_yang": "yang", "moving": True},
        {"position": 5, "yin_yang": "yin", "moving": False},
        {"position": 6, "yin_yang": "yin", "moving": False},
    ],
    "request_id": None,
}


def _run_cli(*args: str, payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "mingli_engine.cli", *args],
        capture_output=True,
        text=True,
        input=json.dumps(payload),
        timeout=60,
        check=False,
    )


def _payload(**overrides) -> dict:
    payload = dict(_BASE_PAYLOAD)
    payload.update(overrides)
    return payload


def test_report_with_supported_category_renders_citations() -> None:
    result = _run_cli(
        "liuyao-report",
        "--input",
        "-",
        payload=_payload(matter_category="weather"),
    )
    assert result.returncode == 0, result.stderr
    markdown = result.stdout
    assert "所问事项类别：天气晴雨。" in markdown
    assert "证据引用：liuyao_evidence_batch_20260714_0012" in markdown
    assert "liuyao_source_batch_20260714_001" in markdown
    assert "page:129-160" in markdown
    assert "（已观察）" in markdown


def test_report_without_category_matches_v1_output() -> None:
    absent = _run_cli("liuyao-report", "--input", "-", payload=_payload())
    explicit_null = _run_cli(
        "liuyao-report",
        "--input",
        "-",
        payload=_payload(matter_category=None),
    )
    assert absent.returncode == 0, absent.stderr
    assert explicit_null.returncode == 0, explicit_null.stderr
    assert absent.stdout == explicit_null.stdout
    assert "未提供事项类别输入" in absent.stdout


def test_report_rejects_unknown_matter_category() -> None:
    result = _run_cli(
        "liuyao-report",
        "--input",
        "-",
        payload=_payload(matter_category="astrology"),
    )
    assert result.returncode == 1
    assert "Liuyao error: unsupported matter category" in result.stderr
    assert result.stdout == ""


def test_report_rejects_non_string_matter_category() -> None:
    result = _run_cli(
        "liuyao-report",
        "--input",
        "-",
        payload=_payload(matter_category=7),
    )
    assert result.returncode == 1
    assert "Liuyao error: invalid request fields" in result.stderr
    assert result.stdout == ""


def test_report_refuses_high_risk_matter_category() -> None:
    for category in ("medical", "legal", "investment", "lifespan"):
        result = _run_cli(
            "liuyao-report",
            "--input",
            "-",
            payload=_payload(matter_category=category),
        )
        assert result.returncode == 1, category
        assert (
            "request cannot be answered within the safety boundary"
            in result.stderr
        ), category
        assert result.stdout == "", category


def test_calculate_accepts_supported_category_without_chart_change() -> None:
    with_category = _run_cli(
        "liuyao-calculate",
        "--input",
        "-",
        payload=_payload(matter_category="agriculture"),
    )
    without_category = _run_cli(
        "liuyao-calculate", "--input", "-", payload=_payload()
    )
    assert with_category.returncode == 0, with_category.stderr
    assert with_category.stdout == without_category.stdout
    payload = json.loads(with_category.stdout)
    assert "matter_category" not in payload
    assert payload["ben_gua"]["gua_name"] == "雷天大壮"


def test_calculate_refuses_high_risk_matter_category() -> None:
    result = _run_cli(
        "liuyao-calculate",
        "--input",
        "-",
        payload=_payload(matter_category="lifespan"),
    )
    assert result.returncode == 1
    assert (
        "request cannot be answered within the safety boundary"
        in result.stderr
    )
    assert result.stdout == ""


def test_calculate_rejects_unknown_matter_category() -> None:
    result = _run_cli(
        "liuyao-calculate",
        "--input",
        "-",
        payload=_payload(matter_category="astrology"),
    )
    assert result.returncode == 1
    assert "Liuyao error: unsupported matter category" in result.stderr
    assert result.stdout == ""


def test_report_with_category_is_deterministic() -> None:
    first = _run_cli(
        "liuyao-report",
        "--input",
        "-",
        payload=_payload(matter_category="lost_items"),
    )
    assert first.returncode == 0, first.stderr
    for _ in range(2):
        again = _run_cli(
            "liuyao-report",
            "--input",
            "-",
            payload=_payload(matter_category="lost_items"),
        )
        assert again.stdout == first.stdout
