import json
from pathlib import Path

import pytest

from mingli_engine.report_inputs import (
    InputContractError,
    birth_profile_from_dict,
    chart_from_dict,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_example(name: str):
    return json.loads((REPO_ROOT / "examples" / name).read_text(encoding="utf-8"))


def test_birth_profile_parser_matches_calculate_report_contract():
    payload = _load_example("birth-profile.auto-gregorian.json")

    profile = birth_profile_from_dict(payload)

    assert profile.calendar_type == "gregorian"
    assert profile.focus_topic == "职业规划与长期学习节奏"


def test_chart_parser_matches_generate_report_contract():
    payload = _load_example("bazi-chart.external-verified.json")

    chart = chart_from_dict(payload)

    assert chart.chart_source.source_type == "external_verified"
    assert len(chart.pillars) == 4
    assert chart.pillars[0].heavenly_stem == "壬"
    assert chart.birth_profile.focus_topic == "职业规划与长期学习节奏"


def test_birth_profile_parser_can_preserve_generate_report_missing_fields():
    profile = birth_profile_from_dict(
        {"focus_topic": "学习规划"},
        allow_missing=True,
    )

    assert profile.focus_topic == "学习规划"
    assert profile.birth_date == ""


def test_report_input_parsers_reject_invalid_shapes():
    with pytest.raises(TypeError, match="birth_profile must be an object"):
        birth_profile_from_dict([])

    payload = _load_example("bazi-chart.external-verified.json")
    payload["pillars"] = payload["pillars"][:3]

    with pytest.raises(InputContractError, match="exactly four"):
        chart_from_dict(payload)
