from mingli_engine.models import BirthProfile, IntakeValidationResult


_FIELD_ORDER = (
    "calendar_type",
    "birth_date",
    "birth_time",
    "birthplace",
    "gender",
    "focus_topic",
)

_CLARIFICATION_QUESTIONS = {
    "calendar_type": "请确认出生日期使用的是公历还是农历？",
    "birth_date": "请提供出生日期。",
    "birth_time": "请提供出生时间。",
    "birthplace": "请提供出生地。",
    "gender": "请提供性别信息。",
    "focus_topic": "请说明本次报告想重点关注的主题。",
}


def validate_birth_profile(profile: BirthProfile) -> IntakeValidationResult:
    missing_fields = [
        field_name
        for field_name in _FIELD_ORDER
        if not getattr(profile, field_name).strip()
    ]
    clarification_questions = [
        _CLARIFICATION_QUESTIONS[field_name] for field_name in missing_fields
    ]

    return IntakeValidationResult(
        report_ready=not missing_fields,
        missing_fields=missing_fields,
        clarification_questions=clarification_questions,
    )
