from typing import Any

from mingli_engine.models import BaziChart, BirthProfile, ChartSource, Pillar


BIRTH_PROFILE_FIELDS = (
    "calendar_type",
    "birth_date",
    "birth_time",
    "birthplace",
    "gender",
    "focus_topic",
)


class InputContractError(ValueError):
    pass


def require_fields(data: dict[str, Any], fields: tuple[str, ...]) -> None:
    missing_fields = [field for field in fields if field not in data]
    if missing_fields:
        raise InputContractError(
            "missing required field(s): " + ", ".join(missing_fields)
        )


def _require_object(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{field_name} must be an object")
    return value


def birth_profile_from_dict(
    data: dict[str, Any],
    *,
    allow_missing: bool = False,
) -> BirthProfile:
    data = _require_object(data, "birth_profile")
    if not allow_missing:
        require_fields(data, BIRTH_PROFILE_FIELDS)

    return BirthProfile(
        calendar_type=data.get("calendar_type", ""),
        birth_date=data.get("birth_date", ""),
        birth_time=data.get("birth_time", ""),
        birthplace=data.get("birthplace", ""),
        gender=data.get("gender", ""),
        focus_topic=data.get("focus_topic", ""),
    )


def chart_from_dict(data: dict[str, Any]) -> BaziChart:
    require_fields(
        data,
        (
            "birth_profile",
            "chart_source",
            "pillars",
            "day_master",
            "five_elements_summary",
            "ten_gods_summary",
            "strength_assessment",
            "pattern_candidates",
            "useful_god_candidates",
            "luck_cycle_summary",
        ),
    )
    if not isinstance(data["pillars"], list):
        raise TypeError("pillars must be a list")
    if len(data["pillars"]) != 4:
        raise InputContractError("pillars must contain exactly four items")
    return BaziChart(
        birth_profile=birth_profile_from_dict(
            data["birth_profile"],
            allow_missing=True,
        ),
        chart_source=ChartSource(
            **_require_object(data["chart_source"], "chart_source")
        ),
        pillars=[
            Pillar(
                **{
                    key: value
                    for key, value in pillar.items()
                    if key != "gan_zhi"
                }
            )
            for pillar in data["pillars"]
        ],
        day_master=data["day_master"],
        five_elements_summary=data["five_elements_summary"],
        ten_gods_summary=data["ten_gods_summary"],
        strength_assessment=data["strength_assessment"],
        pattern_candidates=data["pattern_candidates"],
        useful_god_candidates=data["useful_god_candidates"],
        luck_cycle_summary=data["luck_cycle_summary"],
    )
