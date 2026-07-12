from collections.abc import Iterable


PUBLIC_ASSUMPTION_LIMIT = 12
PUBLIC_ASSUMPTION_TRUNCATION_MARKER = "additional_assumptions_omitted"

_INTERNAL_TERMS = (
    "sensitivity",
    "weight",
    "tuning",
    "internal_config",
    "internal config",
    "config_path",
    "config_file",
    "configuration_path",
    "provider_path",
    "threshold",
    "coefficient",
    "multiplier",
)


def project_public_assumptions(values: Iterable[str]) -> list[str]:
    projected: list[str] = []
    for value in values:
        normalized = value.strip()
        lowered = normalized.lower()
        if (
            not normalized
            or normalized == PUBLIC_ASSUMPTION_TRUNCATION_MARKER
            or any(term in lowered for term in _INTERNAL_TERMS)
            or normalized in projected
        ):
            continue
        projected.append(normalized)

    if len(projected) <= PUBLIC_ASSUMPTION_LIMIT:
        return projected
    return [
        *projected[: PUBLIC_ASSUMPTION_LIMIT - 1],
        PUBLIC_ASSUMPTION_TRUNCATION_MARKER,
    ]
