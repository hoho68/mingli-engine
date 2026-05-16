from dataclasses import dataclass, field


@dataclass(frozen=True)
class BirthProfile:
    calendar_type: str
    birth_date: str
    birth_time: str
    birthplace: str
    gender: str
    focus_topic: str


@dataclass(frozen=True)
class IntakeValidationResult:
    report_ready: bool
    missing_fields: list[str] = field(default_factory=list)
    clarification_questions: list[str] = field(default_factory=list)
