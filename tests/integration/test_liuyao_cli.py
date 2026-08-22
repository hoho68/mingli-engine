import json
import subprocess
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


def _run_cli(*args: str, stdin_text: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "mingli_engine.cli", *args],
        capture_output=True,
        text=True,
        input=stdin_text,
        timeout=60,
    )


def test_liuyao_calculate_outputs_chart_json() -> None:
    result = _run_cli(
        "liuyao-calculate",
        "--input",
        str(EXAMPLES_DIR / "liuyao-cast.explicit.json"),
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["cast_mode"] == "explicit"
    assert payload["ben_gua"]["gua_name"] == "雷天大壮"
    assert payload["bian_gua"]["gua_name"] == "地天泰"
    assert payload["hu_gua"]["gua_name"] == "泽天夬"
    assert len(payload["lines"]) == 6
    assert payload["lines"][3]["moving"] is True
    assert payload["xun_void_branches"] == ["戌", "亥"]
    assert payload["assumptions"]


def test_liuyao_report_outputs_boundary_guarded_markdown() -> None:
    result = _run_cli(
        "liuyao-report",
        "--input",
        str(EXAMPLES_DIR / "liuyao-cast.explicit.json"),
    )
    assert result.returncode == 0, result.stderr
    markdown = result.stdout
    assert "## 免责声明" in markdown
    assert "## 装卦" in markdown
    assert "## 逐爻明细" in markdown
    assert "## 各族观察" in markdown
    assert "## 边界说明" in markdown
    for marker in ("必定", "注定", "一定会", "死定"):
        assert marker not in markdown


def test_liuyao_cli_rejects_invalid_envelope() -> None:
    bad = EXAMPLES_DIR / "liuyao-cast.invalid.json"
    bad.write_text("{not json", encoding="utf-8")
    try:
        result = _run_cli("liuyao-calculate", "--input", str(bad))
        assert result.returncode == 1
        assert "Liuyao error: invalid request envelope" in result.stderr
        assert result.stdout == ""
    finally:
        bad.unlink()


def test_liuyao_cli_rejects_mode_field_mismatch() -> None:
    result = _run_cli(
        "liuyao-calculate",
        "--input",
        "-",
        stdin_text=json.dumps(
            {
                "cast_mode": "number",
                "cast_datetime": "1990-02-28T08:30",
                "numbers": [7],
            }
        ),
    )
    assert result.returncode == 1
    assert "Liuyao error: cast mode requirements are not met" in result.stderr


def test_liuyao_cli_rejects_out_of_range_datetime() -> None:
    result = _run_cli(
        "liuyao-calculate",
        "--input",
        "-",
        stdin_text=json.dumps(
            {
                "cast_mode": "time",
                "cast_datetime": "2101-01-01T00:00",
            }
        ),
    )
    assert result.returncode == 1
    assert "out of range" in result.stderr


def test_liuyao_cli_is_deterministic() -> None:
    first = _run_cli(
        "liuyao-report",
        "--input",
        str(EXAMPLES_DIR / "liuyao-cast.explicit.json"),
    )
    for _ in range(3):
        again = _run_cli(
            "liuyao-report",
            "--input",
            str(EXAMPLES_DIR / "liuyao-cast.explicit.json"),
        )
        assert again.stdout == first.stdout
