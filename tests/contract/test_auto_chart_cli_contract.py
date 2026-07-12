import io
import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import mingli_engine.cli as cli
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.report_inputs import birth_profile_from_dict


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"


def _run_cli(
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
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
        input=input_text,
        capture_output=True,
        check=False,
    )


def test_calculate_chart_outputs_auto_calculated_bazi_chart():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["chart_source"]["source_type"] == "auto_calculated"
    assert payload["chart_source"]["confidence"] == "medium"
    assert payload["chart_source"]["true_solar_time_applied"] is False
    assert "未人工复核" in payload["chart_source"]["source_note"]
    assert [pillar["gan_zhi"] for pillar in payload["pillars"]] == [
        "壬申",
        "戊申",
        "丙寅",
        "癸巳",
    ]


def test_calculate_chart_accepts_profile_from_stdin():
    profile = (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
        encoding="utf-8"
    )

    result = _run_cli("calculate-chart", "--input", "-", input_text=profile)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload["pillars"]) == 4


def test_calculate_chart_main_accepts_stringio_streams(monkeypatch):
    profile = (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
        encoding="utf-8"
    )
    stdout = io.StringIO()
    stderr = io.StringIO()
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(profile))
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    monkeypatch.setattr(cli.sys, "stderr", stderr)

    return_code = cli.main(["calculate-chart", "--input", "-"])

    assert return_code == 0, stderr.getvalue()
    payload = json.loads(stdout.getvalue())
    assert len(payload["pillars"]) == 4


def test_calculate_chart_reports_stable_error_for_unsupported_lunar_calendar():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsupported-lunar.json"),
    )

    assert result.returncode == 1
    assert "Invalid input" in result.stderr
    assert "calendar_type" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_chart_rejects_invalid_date(tmp_path):
    payload = json.loads(
        (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
            encoding="utf-8"
        )
    )
    payload["birth_date"] = "1992-02-31"
    input_path = tmp_path / "invalid-date.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    result = _run_cli("calculate-chart", "--input", str(input_path))

    assert result.returncode == 1
    assert "Invalid input" in result.stderr
    assert "birth_date" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_chart_rejects_invalid_time(tmp_path):
    payload = json.loads(
        (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
            encoding="utf-8"
        )
    )
    payload["birth_time"] = "25:99"
    input_path = tmp_path / "invalid-time.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    result = _run_cli("calculate-chart", "--input", str(input_path))

    assert result.returncode == 1
    assert "Invalid input" in result.stderr
    assert "birth_time" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_chart_outputs_safety_review_for_unsafe_focus():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsafe-focus.json"),
    )

    assert result.returncode == 3, result.stderr
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert "lifespan_or_death_timing" in payload["red_line_categories"]


def test_calculate_chart_analysis_adds_versioned_calculation_envelope():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--analysis",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload["pillars"]) == 4
    assert all(pillar["gan_zhi"] for pillar in payload["pillars"])
    calculation = payload["calculation"]
    assert calculation["engine_version"]
    assert calculation["ruleset_version"]
    assert calculation["strength"]["reasoning"]["status"] in {
        "computed",
        "indeterminate",
        "disputed",
        "not_computed",
    }
    assert isinstance(calculation["schools"], list)
    assert isinstance(calculation["facts"]["twelve_growth_by_pillar"], list)
    assert "provenance" not in result.stdout.lower()


def test_calculate_chart_analysis_uses_public_whitelist_projection():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
        "--analysis",
    )

    assert result.returncode == 0, result.stderr
    calculation = json.loads(result.stdout)["calculation"]
    assert set(calculation) == {
        "engine_version",
        "ruleset_version",
        "facts",
        "branch_relations",
        "strength",
        "patterns",
        "useful_gods",
        "luck_cycles",
        "schools",
    }
    assert set(calculation["strength"]) == {"reasoning", "label"}
    required_reasoning = {
        "status",
        "conclusion",
        "confidence",
        "supporting_signals",
        "opposing_signals",
        "assumptions",
        "missing_inputs",
        "rule_ids",
    }
    reasonings = [
        calculation["strength"]["reasoning"],
        calculation["luck_cycles"]["reasoning"],
        *(item["reasoning"] for item in calculation["patterns"]),
        *(item["reasoning"] for item in calculation["useful_gods"]),
        *(item["reasoning"] for item in calculation["schools"]),
    ]
    assert reasonings
    assert all(set(reasoning) == required_reasoning for reasoning in reasonings)
    assert calculation["facts"]["day_master"]
    assert calculation["facts"]["exposed_stems"]
    assert calculation["branch_relations"]
    assert calculation["patterns"]
    assert calculation["useful_gods"]
    assert isinstance(calculation["luck_cycles"]["pillars"], list)
    assert calculation["schools"]

    def all_keys(value):
        if isinstance(value, dict):
            for key, item in value.items():
                yield key
                yield from all_keys(item)
        elif isinstance(value, list):
            for item in value:
                yield from all_keys(item)

    keys = set(all_keys(calculation))
    assert keys.isdisjoint(
        {"score", "lower_bound", "upper_bound", "contributions", "value"}
    )
    assert not any("weight" in key.lower() for key in keys)
    assert not any("sensitivity" in key.lower() for key in keys)
    serialized = json.dumps(calculation, ensure_ascii=False).lower()
    assert "sensitivity_fraction" not in serialized
    assert "weight_config" not in serialized
    assert "reasonedresult(" not in serialized
    assert "calculationbundle(" not in serialized
    assert "provenance" not in serialized


def test_calculate_chart_without_analysis_preserves_legacy_shape():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.auto-gregorian.json"),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "calculation" not in payload
    assert all("gan_zhi" in pillar for pillar in payload["pillars"])


def test_calculate_chart_without_analysis_is_byte_exact_legacy_json():
    input_text = (EXAMPLES_DIR / "birth-profile.auto-gregorian.json").read_text(
        encoding="utf-8"
    )
    chart = calculate_bazi_chart(birth_profile_from_dict(json.loads(input_text)))
    expected_payload = asdict(chart)
    for pillar in expected_payload["pillars"]:
        pillar["gan_zhi"] = pillar["heavenly_stem"] + pillar["earthly_branch"]
    expected = json.dumps(expected_payload, ensure_ascii=False, indent=2) + "\n"

    result = _run_cli("calculate-chart", "--input", "-", input_text=input_text)

    assert result.returncode == 0, result.stderr
    assert result.stdout == expected


def test_calculate_chart_analysis_refuses_unsafe_focus_before_analysis():
    result = _run_cli(
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsafe-focus.json"),
        "--analysis",
    )

    assert result.returncode == 3, result.stderr
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert "calculation" not in payload


def test_calculate_chart_analysis_flag_does_not_change_refusal_bytes():
    args = (
        "calculate-chart",
        "--input",
        str(EXAMPLES_DIR / "birth-profile.unsafe-focus.json"),
    )

    default = _run_cli(*args)
    analysis = _run_cli(*args, "--analysis")

    assert default.returncode == analysis.returncode == 3
    assert default.stdout == analysis.stdout
    assert default.stderr == analysis.stderr == ""
