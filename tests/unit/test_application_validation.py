import builtins
from dataclasses import FrozenInstanceError, asdict
import logging
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


EXPECTED_SCENARIOS = (
    "success",
    "refusal",
    "validation_failure",
    "internal_error",
)


def _validation() -> ModuleType:
    import mingli_engine.application_validation as validation

    return validation


def test_application_verification_is_complete_deterministic_and_frozen() -> None:
    validation = _validation()

    first = validation.build_application_verification()
    second = validation.build_application_verification()

    assert first == second
    assert first.overall_status == "verified"
    assert tuple(item.name for item in first.scenarios) == EXPECTED_SCENARIOS
    assert all(item.contract_status == "verified" for item in first.scenarios)
    assert all(item.privacy_status == "verified" for item in first.scenarios)
    assert all(item.write_count == 0 for item in first.scenarios)
    assert all(item.leak_count == 0 for item in first.scenarios)
    assert tuple(key for key, _value in first.version_identifiers) == (
        "engine_version",
        "ruleset_version",
        "provider_version",
        "evidence_baseline_id",
    )
    assert all(value for _key, value in first.version_identifiers)
    with pytest.raises(FrozenInstanceError):
        first.overall_status = "failed"


def test_application_verification_contains_no_request_or_report_body() -> None:
    verification = asdict(_validation().build_application_verification())
    prohibited_keys = {
        "birth_date",
        "birth_time",
        "birthplace",
        "focus_topic",
        "profile",
        "report",
        "content",
        "request_id",
        "trace_id",
    }

    def collect_keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return set(value) | {
                nested
                for item in value.values()
                for nested in collect_keys(item)
            }
        if isinstance(value, (list, tuple)):
            return {
                nested for item in value for nested in collect_keys(item)
            }
        return set()

    assert collect_keys(verification).isdisjoint(prohibited_keys)
    flattened = repr(verification)
    assert "Synthetic Verification Place" not in flattened
    assert "1996-12-15" not in flattened


def test_application_verification_is_read_only_silent_and_non_logging(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write_attempts: list[str] = []
    original_open = builtins.open

    def guarded_open(*args: Any, **kwargs: Any):
        mode = kwargs.get("mode", args[1] if len(args) > 1 else "r")
        if any(marker in mode for marker in ("w", "a", "x", "+")):
            write_attempts.append(str(args[0]))
            raise AssertionError("application verification attempted a write")
        return original_open(*args, **kwargs)

    def forbidden_write(*_args: object, **_kwargs: object) -> None:
        write_attempts.append("path-write")
        raise AssertionError("application verification attempted a write")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(Path, "write_text", forbidden_write)
    monkeypatch.setattr(Path, "write_bytes", forbidden_write)
    monkeypatch.setattr(Path, "touch", forbidden_write)
    monkeypatch.setattr(Path, "mkdir", forbidden_write)
    caplog.set_level(logging.DEBUG)

    verification = _validation().build_application_verification()

    captured = capsys.readouterr()
    assert verification.overall_status == "verified"
    assert write_attempts == []
    assert list(tmp_path.iterdir()) == []
    assert caplog.records == []
    assert captured.out == ""
    assert captured.err == ""
