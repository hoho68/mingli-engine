from mingli_engine.models import BirthProfile
from mingli_engine.validation import validate_birth_profile


def test_complete_birth_profile_is_report_ready():
    profile = BirthProfile(
        calendar_type="solar",
        birth_date="1990-01-01",
        birth_time="08:30",
        birthplace="北京",
        gender="female",
        focus_topic="事业",
    )

    result = validate_birth_profile(profile)

    assert result.report_ready is True
    assert result.missing_fields == []
    assert result.clarification_questions == []


def test_missing_birth_time_and_birthplace_require_clarification():
    profile = BirthProfile(
        calendar_type="solar",
        birth_date="1990-01-01",
        birth_time=" ",
        birthplace="",
        gender="female",
        focus_topic="事业",
    )

    result = validate_birth_profile(profile)

    assert result.report_ready is False
    assert result.missing_fields == ["birth_time", "birthplace"]
    assert len(result.clarification_questions) == 2
    assert "出生时间" in result.clarification_questions[0]
    assert "出生地" in result.clarification_questions[1]
