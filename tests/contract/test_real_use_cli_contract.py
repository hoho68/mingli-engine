from __future__ import annotations

from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from typing import Any

import pytest

import mingli_engine.cli as cli


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "application"
MAX_REQUEST_BYTES = 32 * 1024


def _run_cli(
    input_source: str,
    *,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    src_path = str(REPO_ROOT / "src")
    environment["PYTHONPATH"] = (
        src_path
        if not environment.get("PYTHONPATH")
        else os.pathsep.join([src_path, environment["PYTHONPATH"]])
    )
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "mingli_engine.cli",
            "real-use",
            "--input",
            input_source,
        ],
        cwd=REPO_ROOT,
        env=environment,
        input=input_bytes,
        capture_output=True,
        check=False,
        timeout=30,
    )


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _decoded(completed: subprocess.CompletedProcess[bytes]) -> dict[str, Any]:
    assert completed.stderr == b""
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    assert completed.stdout == _canonical_bytes(payload)
    return payload


@pytest.mark.parametrize("input_source", ["path", "stdin"])
def test_real_use_cli_accepts_one_bounded_path_or_stdin_request(
    input_source: str,
) -> None:
    fixture = FIXTURES / "valid_analysis_request.json"
    completed = (
        _run_cli(str(fixture))
        if input_source == "path"
        else _run_cli("-", input_bytes=fixture.read_bytes())
    )
    response = _decoded(completed)

    assert completed.returncode == 0
    assert response["operation"] == "analysis"
    assert response["status"] == "ok"


@pytest.mark.parametrize(
    ("payload_mutator", "expected_status", "expected_exit"),
    [
        (lambda payload: payload, "ok", 0),
        (
            lambda payload: {
                **payload,
                "authorization": {
                    "subject_relation": "self",
                    "attested": False,
                },
            },
            "refused",
            3,
        ),
    ],
)
def test_real_use_cli_operation_source_status_and_exit_code_are_consistent(
    payload_mutator: Any,
    expected_status: str,
    expected_exit: int,
) -> None:
    request = json.loads(
        (FIXTURES / "valid_report_request.json").read_text(encoding="utf-8")
    )
    completed = _run_cli(
        "-",
        input_bytes=_canonical_bytes(payload_mutator(request)),
    )
    response = _decoded(completed)

    assert completed.returncode == expected_exit
    assert response["operation"] == "report"
    assert response["status"] == expected_status


def test_real_use_cli_invalid_input_returns_one_error_envelope() -> None:
    completed = _run_cli("-", input_bytes=b"{")
    response = _decoded(completed)

    assert completed.returncode == 1
    assert response["operation"] is None
    assert response["status"] == "error"
    assert response["error"]["code"] == "invalid_json"


class _ReadSpy(BytesIO):
    def __init__(self, payload: bytes) -> None:
        super().__init__(payload)
        self.read_sizes: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.read_sizes.append(size)
        return super().read(size)


def test_real_use_file_reader_requests_only_limit_plus_sentinel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stream = _ReadSpy(b"x" * (MAX_REQUEST_BYTES + 128))
    monkeypatch.setattr(Path, "open", lambda *_args, **_kwargs: stream)

    payload = cli._read_real_use_input(Path("synthetic-request.json"))

    assert len(payload) == MAX_REQUEST_BYTES + 1
    assert stream.read_sizes == [MAX_REQUEST_BYTES + 1]


def test_real_use_stdin_reader_requests_only_limit_plus_sentinel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stream = _ReadSpy(b"x" * (MAX_REQUEST_BYTES + 128))
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=stream))

    payload = cli._read_real_use_input(Path("-"))

    assert len(payload) == MAX_REQUEST_BYTES + 1
    assert stream.read_sizes == [MAX_REQUEST_BYTES + 1]


def test_real_use_cli_oversized_input_is_controlled_and_does_not_leak_tail() -> None:
    tail = b"PRIVATE-CLI-TAIL-SENTINEL"
    completed = _run_cli(
        "-",
        input_bytes=b" " * (MAX_REQUEST_BYTES + 1) + tail,
    )
    response = _decoded(completed)

    assert completed.returncode == 1
    assert response["status"] == "error"
    assert response["error"]["code"] == "payload_too_large"
    assert tail not in completed.stdout
