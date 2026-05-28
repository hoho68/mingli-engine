import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from mingli_engine import source_intake
from mingli_engine.safety import safety_check
from mingli_engine.classical_sources import load_approved_evidence_units


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


def test_high_risk_evidence_units_have_non_exact_limitations():
    high_risk_units = [
        unit
        for unit in load_approved_evidence_units()
        if unit.risk_tier == "high_risk"
    ]

    assert len(high_risk_units) >= 4
    for unit in high_risk_units:
        limitation_text = "；".join(unit.limitations)
        assert "精确" in limitation_text or "不输出" in limitation_text
        for prohibited_phrase in ("必定", "注定", "一定会", "死定"):
            assert prohibited_phrase not in unit.summary
            assert prohibited_phrase not in limitation_text


def test_expanded_corpus_summaries_avoid_absolute_destiny_phrases():
    for unit in load_approved_evidence_units():
        combined = "；".join([unit.summary, *unit.limitations])
        for prohibited_phrase in ("必定", "注定", "一定会", "死定"):
            assert prohibited_phrase not in combined


@pytest.mark.parametrize(
    "prohibited_phrase",
    [
        "\u5fc5\u5b9a",
        "\u6ce8\u5b9a",
        "\u4e00\u5b9a\u4f1a",
        "\u6b7b\u5b9a",
    ],
)
def test_candidate_extracts_reject_absolute_outcome_language(
    tmp_path,
    prohibited_phrase,
):
    (tmp_path / "source_materials.json").write_text(
        json.dumps(
            [
                {
                    "material_id": "material_001",
                    "title": "Material One",
                    "material_type": "pdf",
                    "file_label": "material-one.pdf",
                    "tracking_status": "external_untracked",
                    "preparation_status": "indexed",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "candidate_extracts.json").write_text(
        json.dumps(
            [
                {
                    "candidate_id": "candidate_absolute",
                    "material_id": "material_001",
                    "source_locator": "review-note:absolute",
                    "extracted_meaning": (
                        f"Candidate language claims the outcome {prohibited_phrase} "
                        "happen."
                    ),
                    "proposed_rule_family": "high_risk_signal",
                    "risk_tier": "high_risk",
                    "status": "pending_review",
                    "proposed_limitations": [
                        "Reject exact outcome and lifespan language."
                    ],
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(source_intake.SourceIntakeError, match="absolute language"):
        source_intake.load_candidate_extracts(tmp_path)
