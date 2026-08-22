"""End-to-end CLI coverage for liuyao knowledge activation (021, Task 5)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "mingli_engine.cli", *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_liuyao_report_emits_governed_evidence_citations() -> None:
    result = _run_cli(
        "liuyao-report",
        "--input",
        str(EXAMPLES_DIR / "liuyao-cast.explicit.json"),
    )
    assert result.returncode == 0, result.stderr
    markdown = result.stdout
    citation_lines = [
        line for line in markdown.splitlines() if line.startswith("- 证据引用：")
    ]
    # 9 + 3 + 5 + 3 + 4 + 2 + 4 citations across the seven evidence families.
    assert len(citation_lines) == 30
    for line in citation_lines:
        assert "liuyao_evidence_batch_20260714_" in line
        assert "liuyao_source_batch_20260714_" in line
        assert "page:" in line
        assert "限制：" in line
    # Boundary markers stay absent with citations included.
    for marker in ("必定", "注定", "一定会", "死定"):
        assert marker not in markdown


def test_liuyao_report_citation_families_match_frozen_distribution() -> None:
    result = _run_cli(
        "liuyao-report",
        "--input",
        str(EXAMPLES_DIR / "liuyao-cast.explicit.json"),
    )
    assert result.returncode == 0, result.stderr
    counts: dict[str, int] = {}
    for line in result.stdout.splitlines():
        if line.startswith("- 证据引用："):
            family = line.split("（", 1)[1].split("，", 1)[0]
            counts[family] = counts.get(family, 0) + 1
    assert counts == {
        "yong_shen_selection": 9,
        "shi_ying_relation": 3,
        "moving_line_dynamics": 5,
        "six_spirits_attachment": 3,
        "month_day_strength": 4,
        "void_break_state": 2,
        "yingqi_timing": 4,
    }
    # category_judgment without a matter category keeps the pending note.
    assert "证据链尚未晋升" in result.stdout


def test_liuyao_report_is_deterministic_across_runs() -> None:
    args = (
        "liuyao-report",
        "--input",
        str(EXAMPLES_DIR / "liuyao-cast.explicit.json"),
    )
    first = _run_cli(*args)
    second = _run_cli(*args)
    assert first.returncode == 0 and second.returncode == 0
    assert first.stdout == second.stdout
