from typing import TYPE_CHECKING

from mingli_engine.bazi.result_models import (
    CalculationBundle,
    ComputationStatus,
    Confidence,
    ReasonedResult,
)

if TYPE_CHECKING:
    from mingli_engine.bazi.analysis import (
        ENGINE_VERSION,
        RULESET_VERSION,
        analyze_bazi_chart,
    )
    from mingli_engine.bazi.legacy_adapter import (
        apply_calculation_bundle,
        build_legacy_not_computed_bundle,
    )


def __getattr__(name: str) -> object:
    if name in {"ENGINE_VERSION", "RULESET_VERSION", "analyze_bazi_chart"}:
        from mingli_engine.bazi import analysis

        value = getattr(analysis, name)
    elif name in {
        "apply_calculation_bundle",
        "build_legacy_not_computed_bundle",
    }:
        from mingli_engine.bazi import legacy_adapter

        value = getattr(legacy_adapter, name)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = value
    return value

__all__ = [
    "CalculationBundle",
    "ComputationStatus",
    "Confidence",
    "ENGINE_VERSION",
    "ReasonedResult",
    "RULESET_VERSION",
    "analyze_bazi_chart",
    "apply_calculation_bundle",
    "build_legacy_not_computed_bundle",
]
