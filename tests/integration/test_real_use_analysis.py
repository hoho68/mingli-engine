import builtins
from copy import copy, deepcopy
import gc
import importlib
import logging
from pathlib import Path
import pickle
from types import ModuleType
from typing import Any, NoReturn
from uuid import UUID
import weakref

import pytest

import mingli_engine
from mingli_engine.application_models import (
    REAL_USE_REQUEST_SCHEMA_VERSION,
    ApplicationAnalysisResultV1,
    ApplicationPrivacyV1,
    ApplicationSafetyV1,
    AuthorizationAttestationV1,
    RealUseOptionsV1,
    RealUseProfileV1,
    RealUseRequestV1,
)
from mingli_engine.bazi.analysis import (
    PROVENANCE_ERROR,
    analyze_bazi_chart,
)
from mingli_engine.chart_calculator import calculate_bazi_chart
from mingli_engine.classical_sources import load_approved_evidence_units
from mingli_engine.models import BirthProfile


TRACE_ID = "550e8400-e29b-41d4-a716-446655440000"
PROFILE_SENTINEL = "PRIVATE-ANALYSIS-PROFILE-SENTINEL"


def _service() -> ModuleType:
    return importlib.import_module("mingli_engine.application_service")


def _request(*, focus_topic: str = "traditional structural overview") -> RealUseRequestV1:
    return RealUseRequestV1(
        schema_version=REAL_USE_REQUEST_SCHEMA_VERSION,
        request_id="synthetic-analysis-test",
        operation="analysis",
        profile=RealUseProfileV1(
            calendar_type="gregorian",
            birth_date="1996-12-15",
            birth_time="09:30",
            birthplace="Synthetic UTC+08 Place",
            gender="unknown",
            focus_topic=focus_topic,
        ),
        authorization=AuthorizationAttestationV1(
            subject_relation="self",
            attested=True,
        ),
        options=RealUseOptionsV1(
            report_format=None,
            include_profile_in_report=False,
        ),
    )


def _birth_profile(*, birth_date: str = "1996-12-15") -> BirthProfile:
    return BirthProfile(
        calendar_type="gregorian",
        birth_date=birth_date,
        birth_time="09:30",
        birthplace="Synthetic UTC+08 Place",
        gender="unknown",
        focus_topic="traditional structural overview",
    )


def _forbid_engine_writes(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    attempts: list[str] = []
    original_open = builtins.open

    def guarded_open(
        file: Any,
        mode: str = "r",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if any(marker in mode for marker in ("w", "a", "x", "+")):
            attempts.append(str(file))
            raise AssertionError("engine-managed write attempted")
        return original_open(file, mode, *args, **kwargs)

    def forbidden_path_write(*_args: object, **_kwargs: object) -> NoReturn:
        attempts.append("path-write")
        raise AssertionError("engine-managed write attempted")

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(Path, "write_text", forbidden_path_write)
    monkeypatch.setattr(Path, "write_bytes", forbidden_path_write)
    monkeypatch.setattr(Path, "touch", forbidden_path_write)
    monkeypatch.setattr(Path, "mkdir", forbidden_path_write)
    return attempts


def test_real_use_analysis_succeeds_with_complete_public_result_and_provenance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _service()
    monkeypatch.setattr(service, "uuid4", lambda: UUID(TRACE_ID))

    response = service.handle_real_use(_request())

    assert response.status == "ok"
    assert response.trace_id == TRACE_ID
    assert response.operation == "analysis"
    assert isinstance(response.result, ApplicationAnalysisResultV1)
    assert response.safety == ApplicationSafetyV1(True, "allowed", (), "", False)
    assert response.error is None
    assert response.warnings == ()
    assert response.privacy == ApplicationPrivacyV1(
        "not_stored_by_engine",
        False,
    )
    assert response.provenance is not None
    assert response.provenance.engine_version == response.result.calculation[
        "engine_version"
    ]
    assert response.provenance.ruleset_version == response.result.calculation[
        "ruleset_version"
    ]
    assert response.provenance.provider_version == "lunar-python-1.4.8"
    assert response.provenance.chart_source_type == "calculated"
    assert (
        response.provenance.chart_source_confidence
        == "deterministic_supported_range"
    )
    assert response.provenance.evidence_baseline_id == "report_acceptance_v1"
    assert response.provenance.evidence_ids == tuple(
        sorted(unit.evidence_id for unit in load_approved_evidence_units())
    )
    assert set(response.result.chart) == {
        "chart_source",
        "pillars",
        "day_master",
        "five_elements_summary",
        "ten_gods_summary",
        "strength_assessment",
        "pattern_candidates",
        "useful_god_candidates",
        "luck_cycle_summary",
    }
    assert "birth_profile" not in response.result.chart
    assert set(response.result.calculation) == {
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


def test_analysis_keeps_original_profile_chart_and_bundle_in_one_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _service()
    monkeypatch.setattr(service, "uuid4", lambda: UUID(TRACE_ID))
    original_calculate = service.calculate_bazi_chart
    original_analyze = service.analyze_bazi_chart
    original_validate = service.validate_calculation_binding
    original_chart_serializer = service.serialize_chart
    original_bundle_serializer = service.serialize_calculation_bundle
    observed: dict[str, object] = {}

    def calculate(profile: BirthProfile):
        observed["profile"] = profile
        chart = original_calculate(profile)
        observed["chart"] = chart
        return chart

    def analyze(chart: object, **kwargs: object):
        assert chart is observed["chart"]
        bundle = original_analyze(chart, **kwargs)
        observed["bundle"] = bundle
        return bundle

    def validate(chart: object, bundle: object) -> None:
        assert chart is observed["chart"]
        assert bundle is observed["bundle"]
        original_validate(chart, bundle)

    def serialize_public_chart(chart: object):
        assert chart is observed["chart"]
        return original_chart_serializer(chart)

    def serialize_public_bundle(bundle: object):
        assert bundle is observed["bundle"]
        return original_bundle_serializer(bundle)

    monkeypatch.setattr(service, "calculate_bazi_chart", calculate)
    monkeypatch.setattr(service, "analyze_bazi_chart", analyze)
    monkeypatch.setattr(service, "validate_calculation_binding", validate)
    monkeypatch.setattr(service, "serialize_chart", serialize_public_chart)
    monkeypatch.setattr(
        service,
        "serialize_calculation_bundle",
        serialize_public_bundle,
    )

    response = service.handle_real_use(_request())

    assert response.status == "ok"
    assert isinstance(observed["profile"], BirthProfile)


def test_cross_request_calculation_bundle_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _service()
    foreign_chart = calculate_bazi_chart(_birth_profile(birth_date="1995-12-15"))
    foreign_bundle = analyze_bazi_chart(foreign_chart)
    monkeypatch.setattr(service, "analyze_bazi_chart", lambda *_args, **_kwargs: foreign_bundle)

    response = service.handle_real_use(_request())

    assert response.status == "error"
    assert response.result is None
    assert response.provenance is None
    assert response.error is not None
    assert response.error.code == "internal_error"
    assert PROVENANCE_ERROR not in response.error.message


@pytest.mark.parametrize("forgery", ["copy", "deepcopy", "pickle"])
def test_copied_or_reconstructed_bundle_cannot_forge_provenance(
    monkeypatch: pytest.MonkeyPatch,
    forgery: str,
) -> None:
    service = _service()
    original_analyze = analyze_bazi_chart

    def forge(chart: object, **kwargs: object):
        bundle = original_analyze(chart, **kwargs)
        if forgery == "copy":
            return copy(bundle)
        if forgery == "deepcopy":
            return deepcopy(bundle)
        return pickle.loads(pickle.dumps(bundle))

    monkeypatch.setattr(service, "analyze_bazi_chart", forge)

    response = service.handle_real_use(_request())

    assert response.status == "error"
    assert response.result is None
    assert response.provenance is None
    assert response.error is not None
    assert response.error.code == "internal_error"


def test_weak_provenance_registry_releases_bundle_after_gc() -> None:
    analysis_module = importlib.import_module("mingli_engine.bazi.analysis")
    chart = calculate_bazi_chart(_birth_profile())
    bundle = analyze_bazi_chart(chart)
    bundle_id = id(bundle)
    bundle_reference = weakref.ref(bundle)

    assert bundle_id in analysis_module._PROVENANCE
    del bundle
    gc.collect()

    assert bundle_reference() is None
    assert bundle_id not in analysis_module._PROVENANCE


def test_success_path_writes_and_logs_nothing(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    attempts = _forbid_engine_writes(monkeypatch)
    caplog.set_level(logging.DEBUG)

    response = _service().handle_real_use(_request())

    captured = capsys.readouterr()
    assert response.status == "ok"
    assert attempts == []
    assert caplog.records == []
    assert captured.out == ""
    assert captured.err == ""


def test_injected_calculation_exception_is_controlled_and_non_leaking(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    service = _service()
    attempts = _forbid_engine_writes(monkeypatch)
    caplog.set_level(logging.DEBUG)

    def explode(_profile: BirthProfile) -> NoReturn:
        raise RuntimeError(f"provider failed for {PROFILE_SENTINEL}")

    monkeypatch.setattr(service, "calculate_bazi_chart", explode)

    response = service.handle_real_use(_request(focus_topic=PROFILE_SENTINEL))

    captured = capsys.readouterr()
    assert response.status == "error"
    assert response.result is None
    assert response.provenance is None
    assert response.error is not None
    assert response.error.code == "internal_error"
    assert response.error.message == "Request processing failed."
    assert attempts == []
    assert caplog.records == []
    assert captured.out == ""
    assert captured.err == ""
    assert PROFILE_SENTINEL not in repr(response)


def test_root_package_exports_typed_analysis_surface() -> None:
    assert mingli_engine.handle_real_use is _service().handle_real_use
    assert mingli_engine.RealUseRequestV1 is RealUseRequestV1
    assert mingli_engine.RealUseResponseV1.__name__ == "RealUseResponseV1"
    assert mingli_engine.ApplicationAnalysisResultV1 is ApplicationAnalysisResultV1
