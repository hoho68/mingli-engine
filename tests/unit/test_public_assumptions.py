from mingli_engine.public_assumptions import (
    PUBLIC_ASSUMPTION_LIMIT,
    PUBLIC_ASSUMPTION_TRUNCATION_MARKER,
    project_public_assumptions,
)


def test_public_assumptions_filter_internal_terms_and_preserve_public_inputs():
    values = (
        "calendar:gregorian",
        "timezone:UTC+8",
        "sect=1",
        "count=8",
        "public_boundary:candidate_only",
        "calendar:gregorian",
        "sensitivity_fraction=0.1",
        "root_weight=1.2",
        "tuning_mode=internal",
        "internal_config_path=C:/private/provider.json",
        "score_threshold=0.4",
        "coefficient=1.5",
        PUBLIC_ASSUMPTION_TRUNCATION_MARKER,
        *(f"public_assumption_{index:02d}" for index in range(20)),
    )

    projected = project_public_assumptions(values)

    assert projected[:5] == [
        "calendar:gregorian",
        "timezone:UTC+8",
        "sect=1",
        "count=8",
        "public_boundary:candidate_only",
    ]
    assert len(projected) == PUBLIC_ASSUMPTION_LIMIT
    assert projected[-1] == PUBLIC_ASSUMPTION_TRUNCATION_MARKER
    assert len(projected) == len(set(projected))
    serialized = " ".join(projected).lower()
    for excluded in (
        "sensitivity",
        "weight",
        "tuning",
        "internal_config",
        "threshold",
        "coefficient",
        "private/provider",
    ):
        assert excluded not in serialized


def test_public_assumptions_are_deterministic_and_do_not_add_marker_at_limit():
    values = tuple(f"public_{index}" for index in range(PUBLIC_ASSUMPTION_LIMIT))

    first = project_public_assumptions(values)
    second = project_public_assumptions(values)

    assert first == second == list(values)
    assert PUBLIC_ASSUMPTION_TRUNCATION_MARKER not in first
