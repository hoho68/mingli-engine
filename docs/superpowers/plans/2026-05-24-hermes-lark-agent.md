# Hermes Lark Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Hermes Agent project at `E:\hermes-mingli-agent` that connects to Feishu/Lark through Hermes WebSocket mode and exposes the Mingli report engine as a safe report-generation tool.

**Architecture:** Keep `E:\命理演绎` as the core Mingli engine. Create a separate Hermes project that contains a small Python package, a stdio MCP server named `mingli_report`, and runtime folders for temporary inputs/outputs. Hermes loads the MCP server through `~\.hermes\config.yaml`, then the Feishu gateway calls the exposed `generate_mingli_report` tool during chat.

**Tech Stack:** Windows PowerShell, Hermes Agent native Windows install, Feishu/Lark WebSocket gateway, Python 3.12+, uv, pytest, MCP Python SDK, existing `mingli_engine` CLI.

---

## References

- Hermes Windows install: `https://hermes-agent.nousresearch.com/docs/getting-started/installation/`
- Hermes Feishu/Lark WebSocket mode: `https://hermes-agent.nousresearch.com/docs/user-guide/messaging/feishu`
- Hermes MCP/toolset configuration: `https://hermes-agent.nousresearch.com/docs/reference/toolsets-reference`
- Current Mingli engine design: `E:\命理演绎\docs\superpowers\specs\2026-05-24-hermes-lark-agent-design.md`

## Target File Structure

```text
E:\hermes-mingli-agent\
|-- .gitignore
|-- README.md
|-- pyproject.toml
|-- .env.example
|-- config\
|   |-- hermes-config-snippet.yaml
|   `-- feishu-env.example
|-- src\
|   `-- mingli_agent\
|       |-- __init__.py
|       |-- models.py
|       |-- parser.py
|       |-- report_tool.py
|       `-- mcp_server.py
|-- tests\
|   |-- test_parser.py
|   |-- test_report_tool.py
|   `-- test_mcp_server.py
`-- runtime\
    |-- inputs\
    |-- outputs\
    `-- logs\
```

`E:\命理演绎` should only receive this implementation plan and any later engine-side changes that prove necessary. The first Hermes implementation happens in `E:\hermes-mingli-agent`.

## Task 1: Create The Hermes Project Skeleton

**Files:**
- Create: `E:\hermes-mingli-agent\.gitignore`
- Create: `E:\hermes-mingli-agent\README.md`
- Create: `E:\hermes-mingli-agent\pyproject.toml`
- Create: `E:\hermes-mingli-agent\.env.example`
- Create: `E:\hermes-mingli-agent\config\feishu-env.example`
- Create: `E:\hermes-mingli-agent\config\hermes-config-snippet.yaml`
- Create: `E:\hermes-mingli-agent\src\mingli_agent\__init__.py`

- [ ] **Step 1: Create directories**

Run:

```powershell
New-Item -ItemType Directory -Force `
  E:\hermes-mingli-agent\config, `
  E:\hermes-mingli-agent\src\mingli_agent, `
  E:\hermes-mingli-agent\tests, `
  E:\hermes-mingli-agent\runtime\inputs, `
  E:\hermes-mingli-agent\runtime\outputs, `
  E:\hermes-mingli-agent\runtime\logs
```

Expected: directories exist and no error is printed.

- [ ] **Step 2: Initialize git**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
git init
git branch -M main
```

Expected: `Initialized empty Git repository` or `Reinitialized existing Git repository`.

- [ ] **Step 3: Create `.gitignore`**

Create `E:\hermes-mingli-agent\.gitignore`:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Local secrets and Hermes runtime data
.env
*.secret
runtime/inputs/*
runtime/outputs/*
runtime/logs/*
!runtime/inputs/.gitkeep
!runtime/outputs/.gitkeep
!runtime/logs/.gitkeep
```

- [ ] **Step 4: Add runtime keep files**

Run:

```powershell
New-Item -ItemType File -Force `
  E:\hermes-mingli-agent\runtime\inputs\.gitkeep, `
  E:\hermes-mingli-agent\runtime\outputs\.gitkeep, `
  E:\hermes-mingli-agent\runtime\logs\.gitkeep
```

Expected: all three `.gitkeep` files exist.

- [ ] **Step 5: Create `pyproject.toml`**

Create `E:\hermes-mingli-agent\pyproject.toml`:

```toml
[project]
name = "hermes-mingli-agent"
version = "0.1.0"
description = "Hermes MCP tool wrapper for the Mingli report engine"
requires-python = ">=3.12"
dependencies = [
  "mcp>=1.6.0",
]

[project.scripts]
mingli-report-mcp = "mingli_agent.mcp_server:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 6: Create `README.md`**

Create `E:\hermes-mingli-agent\README.md`:

````markdown
# Hermes Mingli Agent

Hermes Agent project for connecting the Mingli report engine to Feishu/Lark.

The Mingli engine remains in `E:\命理演绎`. This project exposes a local MCP tool named `generate_mingli_report` for Hermes.

## Local Commands

```powershell
uv run --with pytest python -m pytest
uv run mingli-report-mcp
```

## Required Environment

```powershell
$env:MINGLI_ENGINE_ROOT='E:\命理演绎'
```

Hermes Feishu credentials belong in `~\.hermes\.env`, not in this repository.
````

- [ ] **Step 7: Create `.env.example`**

Create `E:\hermes-mingli-agent\.env.example`:

```dotenv
MINGLI_ENGINE_ROOT=E:\命理演绎
MINGLI_AGENT_RUNTIME_DIR=E:\hermes-mingli-agent\runtime
```

- [ ] **Step 8: Create Feishu env example**

Create `E:\hermes-mingli-agent\config\feishu-env.example`:

```dotenv
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=replace_with_secret_in_user_hermes_env
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_ALLOWED_USERS=ou_xxx
FEISHU_GROUP_POLICY=allowlist
FEISHU_REQUIRE_MENTION=true
```

- [ ] **Step 9: Create Hermes MCP config snippet**

Create `E:\hermes-mingli-agent\config\hermes-config-snippet.yaml`:

```yaml
mcp_servers:
  mingli_report:
    command: uv
    args:
      - run
      - --project
      - E:\hermes-mingli-agent
      - mingli-report-mcp
    env:
      MINGLI_ENGINE_ROOT: E:\命理演绎
      MINGLI_AGENT_RUNTIME_DIR: E:\hermes-mingli-agent\runtime
```

- [ ] **Step 10: Create package init file**

Create `E:\hermes-mingli-agent\src\mingli_agent\__init__.py`:

```python
"""Hermes MCP wrapper for the Mingli report engine."""
```

- [ ] **Step 11: Install project dependencies**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
uv sync
```

Expected: `mcp` installs and `.venv` is created.

- [ ] **Step 12: Commit the skeleton**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
git add .
git commit -m "chore: scaffold hermes mingli agent"
```

Expected: commit succeeds.

## Task 2: Implement Structured Feishu Request Parsing

**Files:**
- Create: `E:\hermes-mingli-agent\src\mingli_agent\models.py`
- Create: `E:\hermes-mingli-agent\src\mingli_agent\parser.py`
- Create: `E:\hermes-mingli-agent\tests\test_parser.py`

- [ ] **Step 1: Write parser tests**

Create `E:\hermes-mingli-agent\tests\test_parser.py`:

```python
from mingli_agent.parser import parse_report_request


def test_parse_structured_report_request():
    text = "\n".join(
        [
            "生成报告",
            "公历 1990-01-01 08:30",
            "北京",
            "女",
            "关注：事业发展",
        ]
    )

    result = parse_report_request(text)

    assert result.ok is True
    assert result.missing_fields == []
    assert result.payload == {
        "calendar_type": "gregorian",
        "birth_date": "1990-01-01",
        "birth_time": "08:30",
        "birthplace": "北京",
        "gender": "女",
        "focus_topic": "事业发展",
        "format": "html",
    }


def test_parse_ping_command():
    result = parse_report_request("ping")

    assert result.ok is True
    assert result.command == "ping"
    assert result.payload == {}


def test_parse_missing_birth_time():
    text = "\n".join(
        [
            "生成报告",
            "公历 1990-01-01",
            "北京",
            "女",
            "关注：事业发展",
        ]
    )

    result = parse_report_request(text)

    assert result.ok is False
    assert result.command == "generate_report"
    assert result.missing_fields == ["birth_time"]
    assert result.message == "请补充出生时间，例如：公历 1990-01-01 08:30。"


def test_parse_non_report_text():
    result = parse_report_request("你好")

    assert result.ok is False
    assert result.command == "unknown"
    assert result.message == "请发送“生成报告”并按固定格式补充出生资料。"
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
uv run --with pytest python -m pytest tests/test_parser.py -v
```

Expected: FAIL with `ModuleNotFoundError` or missing `parse_report_request`.

- [ ] **Step 3: Create models**

Create `E:\hermes-mingli-agent\src\mingli_agent\models.py`:

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParsedRequest:
    ok: bool
    command: str
    payload: dict[str, str] = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    message: str = ""
```

- [ ] **Step 4: Create parser implementation**

Create `E:\hermes-mingli-agent\src\mingli_agent\parser.py`:

```python
from __future__ import annotations

import re

from mingli_agent.models import ParsedRequest


_DATE_TIME_RE = re.compile(
    r"(?P<calendar>公历|阳历|gregorian)\s+"
    r"(?P<date>\d{4}-\d{2}-\d{2})"
    r"(?:\s+(?P<time>\d{2}:\d{2}))?"
)


def parse_report_request(text: str) -> ParsedRequest:
    normalized_lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not normalized_lines:
        return ParsedRequest(
            ok=False,
            command="unknown",
            message="请发送“生成报告”并按固定格式补充出生资料。",
        )

    first_line = normalized_lines[0].lower()
    if first_line == "ping":
        return ParsedRequest(ok=True, command="ping")

    if "生成报告" not in normalized_lines[0]:
        return ParsedRequest(
            ok=False,
            command="unknown",
            message="请发送“生成报告”并按固定格式补充出生资料。",
        )

    payload = {
        "calendar_type": "gregorian",
        "birth_date": "",
        "birth_time": "",
        "birthplace": "",
        "gender": "",
        "focus_topic": "",
        "format": "html",
    }

    for line in normalized_lines[1:]:
        date_match = _DATE_TIME_RE.search(line)
        if date_match:
            payload["calendar_type"] = "gregorian"
            payload["birth_date"] = date_match.group("date") or ""
            payload["birth_time"] = date_match.group("time") or ""
            continue
        if line.startswith("关注：") or line.startswith("关注:"):
            payload["focus_topic"] = line.split("：", 1)[-1].split(":", 1)[-1].strip()
            continue
        if line in {"男", "女", "male", "female"}:
            payload["gender"] = line
            continue
        if not payload["birthplace"]:
            payload["birthplace"] = line

    missing = [field for field in ("birth_date", "birth_time", "birthplace", "gender", "focus_topic") if not payload[field]]
    if missing:
        return ParsedRequest(
            ok=False,
            command="generate_report",
            payload=payload,
            missing_fields=missing,
            message=_missing_message(missing[0]),
        )

    return ParsedRequest(ok=True, command="generate_report", payload=payload)


def _missing_message(field: str) -> str:
    messages = {
        "birth_date": "请补充出生日期，例如：公历 1990-01-01 08:30。",
        "birth_time": "请补充出生时间，例如：公历 1990-01-01 08:30。",
        "birthplace": "请补充出生地点，例如：北京。",
        "gender": "请补充性别标记，例如：男 或 女。",
        "focus_topic": "请补充关注主题，例如：关注：事业发展。",
    }
    return messages[field]
```

- [ ] **Step 5: Run parser tests and verify GREEN**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
uv run --with pytest python -m pytest tests/test_parser.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit parser**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
git add src/mingli_agent/models.py src/mingli_agent/parser.py tests/test_parser.py
git commit -m "feat: parse mingli report requests"
```

Expected: commit succeeds.

## Task 3: Implement The Mingli CLI Tool Wrapper

**Files:**
- Create: `E:\hermes-mingli-agent\src\mingli_agent\report_tool.py`
- Create: `E:\hermes-mingli-agent\tests\test_report_tool.py`

- [ ] **Step 1: Write report tool tests**

Create `E:\hermes-mingli-agent\tests\test_report_tool.py`:

```python
import json
import subprocess
from pathlib import Path

from mingli_agent.report_tool import generate_mingli_report


def test_generate_mingli_report_writes_html_artifact(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="<!doctype html>\n<h1>八字结构化报告</h1>\n<h2>快速导读</h2>\n<div>- 来源：系统自动排盘</div>\n<h2>第一层：基础资料</h2>\n",
            stderr="",
        )

    monkeypatch.setenv("MINGLI_ENGINE_ROOT", "E:\\命理演绎")
    monkeypatch.setenv("MINGLI_AGENT_RUNTIME_DIR", str(tmp_path))
    monkeypatch.setattr("subprocess.run", fake_run)

    result = generate_mingli_report(
        {
            "calendar_type": "gregorian",
            "birth_date": "1990-01-01",
            "birth_time": "08:30",
            "birthplace": "北京",
            "gender": "女",
            "focus_topic": "事业发展",
            "format": "html",
        }
    )

    assert result["ok"] is True
    assert result["report_ready"] is True
    assert result["allowed"] is True
    assert result["format"] == "html"
    assert "系统自动排盘" in result["summary"]
    artifact_path = Path(result["artifact_path"])
    assert artifact_path.exists()
    assert artifact_path.read_text(encoding="utf-8").startswith("<!doctype html>")


def test_generate_mingli_report_returns_safety_refusal(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=3,
            stdout=json.dumps(
                {
                    "allowed": False,
                    "red_line_categories": ["lifespan_or_death_timing"],
                    "redirect_message": "不预测寿命或死亡时间。",
                },
                ensure_ascii=False,
            ),
            stderr="",
        )

    monkeypatch.setenv("MINGLI_ENGINE_ROOT", "E:\\命理演绎")
    monkeypatch.setenv("MINGLI_AGENT_RUNTIME_DIR", str(tmp_path))
    monkeypatch.setattr("subprocess.run", fake_run)

    result = generate_mingli_report(
        {
            "calendar_type": "gregorian",
            "birth_date": "1990-01-01",
            "birth_time": "08:30",
            "birthplace": "北京",
            "gender": "女",
            "focus_topic": "寿命",
            "format": "html",
        }
    )

    assert result["ok"] is True
    assert result["report_ready"] is False
    assert result["allowed"] is False
    assert result["red_line_categories"] == ["lifespan_or_death_timing"]
    assert result["message"] == "不预测寿命或死亡时间。"


def test_generate_mingli_report_hides_runtime_errors(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr="Traceback: secret path C:\\Users\\lei\\.hermes\\.env",
        )

    monkeypatch.setenv("MINGLI_ENGINE_ROOT", "E:\\命理演绎")
    monkeypatch.setenv("MINGLI_AGENT_RUNTIME_DIR", str(tmp_path))
    monkeypatch.setattr("subprocess.run", fake_run)

    result = generate_mingli_report(
        {
            "calendar_type": "gregorian",
            "birth_date": "1990-01-01",
            "birth_time": "08:30",
            "birthplace": "北京",
            "gender": "女",
            "focus_topic": "事业发展",
            "format": "html",
        }
    )

    assert result == {
        "ok": False,
        "message": "报告生成暂时不可用，请稍后重试。",
    }
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
uv run --with pytest python -m pytest tests/test_report_tool.py -v
```

Expected: FAIL with missing `mingli_agent.report_tool`.

- [ ] **Step 3: Implement `report_tool.py`**

Create `E:\hermes-mingli-agent\src\mingli_agent\report_tool.py`:

```python
from __future__ import annotations

import json
import os
import re
import subprocess
import uuid
from html import unescape
from pathlib import Path
from typing import Any


def generate_mingli_report(payload: dict[str, str]) -> dict[str, Any]:
    runtime_dir = Path(os.environ.get("MINGLI_AGENT_RUNTIME_DIR", "E:\\hermes-mingli-agent\\runtime"))
    run_id = uuid.uuid4().hex
    input_dir = runtime_dir / "inputs" / run_id
    output_dir = runtime_dir / "outputs" / run_id
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = input_dir / "birth-profile.json"
    input_payload = {
        "calendar_type": payload.get("calendar_type", "gregorian"),
        "birth_date": payload.get("birth_date", ""),
        "birth_time": payload.get("birth_time", ""),
        "birthplace": payload.get("birthplace", ""),
        "gender": payload.get("gender", ""),
        "focus_topic": payload.get("focus_topic", ""),
    }
    input_path.write_text(
        json.dumps(input_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    completed = _run_mingli_cli(input_path, payload.get("format", "html"))
    if completed.returncode == 0:
        artifact_path = output_dir / "report.html"
        artifact_path.write_text(completed.stdout, encoding="utf-8")
        return {
            "ok": True,
            "report_ready": True,
            "allowed": True,
            "summary": _extract_summary(completed.stdout),
            "format": "html",
            "artifact_path": str(artifact_path),
        }

    if completed.returncode in {2, 3} and completed.stdout.strip():
        return _normalize_json_response(completed.stdout)

    _write_runtime_error(runtime_dir, run_id, completed.stderr)
    return {
        "ok": False,
        "message": "报告生成暂时不可用，请稍后重试。",
    }


def _run_mingli_cli(input_path: Path, report_format: str) -> subprocess.CompletedProcess[str]:
    engine_root = Path(os.environ.get("MINGLI_ENGINE_ROOT", "E:\\命理演绎"))
    env = os.environ.copy()
    env["PYTHONPATH"] = str(engine_root / "src")
    return subprocess.run(
        [
            "uv",
            "run",
            "--project",
            str(engine_root),
            "python",
            "-m",
            "mingli_engine.cli",
            "calculate-report",
            "--input",
            str(input_path),
            "--format",
            report_format,
        ],
        cwd=engine_root,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def _normalize_json_response(stdout: str) -> dict[str, Any]:
    data = json.loads(stdout)
    if data.get("allowed") is False:
        return {
            "ok": True,
            "report_ready": False,
            "allowed": False,
            "red_line_categories": data.get("red_line_categories", []),
            "message": data.get("redirect_message") or "这个主题不适合生成正式报告。",
        }
    if data.get("report_ready") is False:
        missing_fields = data.get("missing_fields", [])
        return {
            "ok": True,
            "report_ready": False,
            "allowed": True,
            "missing_fields": missing_fields,
            "message": _missing_field_message(missing_fields),
        }
    return {
        "ok": False,
        "message": "报告生成暂时不可用，请稍后重试。",
    }


def _missing_field_message(missing_fields: list[str]) -> str:
    labels = {
        "birth_date": "出生日期",
        "birth_time": "出生时间",
        "birthplace": "出生地点",
        "gender": "性别标记",
        "focus_topic": "关注主题",
    }
    if not missing_fields:
        return "请补充完整出生资料。"
    readable = "、".join(labels.get(field, field) for field in missing_fields)
    return f"请补充{readable}。"


def _extract_summary(html: str) -> str:
    text = _strip_tags(html)
    quick_guide = _between(text, "快速导读", "第一层：基础资料")
    lines = [line.strip() for line in quick_guide.splitlines() if line.strip()]
    selected = lines[:4]
    if not selected:
        selected = ["报告已生成，请查看完整附件。"]
    return "\n".join(["八字结构化报告已生成", "", *selected])


def _between(text: str, start: str, end: str) -> str:
    start_index = text.find(start)
    if start_index == -1:
        return ""
    start_index += len(start)
    end_index = text.find(end, start_index)
    if end_index == -1:
        return text[start_index:]
    return text[start_index:end_index]


def _strip_tags(html: str) -> str:
    without_tags = re.sub(r"<[^>]+>", "\n", html)
    collapsed = re.sub(r"\n{2,}", "\n", without_tags)
    return unescape(collapsed)


def _write_runtime_error(runtime_dir: Path, run_id: str, stderr: str) -> None:
    log_dir = runtime_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{run_id}.log").write_text(stderr, encoding="utf-8")
```

- [ ] **Step 4: Run report tool tests and verify GREEN**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
uv run --with pytest python -m pytest tests/test_report_tool.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit report tool**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
git add src/mingli_agent/report_tool.py tests/test_report_tool.py
git commit -m "feat: wrap mingli report generation"
```

Expected: commit succeeds.

## Task 4: Expose The Tool Through A Local MCP Server

**Files:**
- Create: `E:\hermes-mingli-agent\src\mingli_agent\mcp_server.py`
- Create: `E:\hermes-mingli-agent\tests\test_mcp_server.py`

- [ ] **Step 1: Write MCP server smoke test**

Create `E:\hermes-mingli-agent\tests\test_mcp_server.py`:

```python
from mingli_agent.mcp_server import build_mcp_server


def test_build_mcp_server_has_name():
    server = build_mcp_server()

    assert server.name == "mingli-report"
```

- [ ] **Step 2: Run test and verify RED**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
uv run --with pytest python -m pytest tests/test_mcp_server.py -v
```

Expected: FAIL with missing `mingli_agent.mcp_server`.

- [ ] **Step 3: Create MCP server**

Create `E:\hermes-mingli-agent\src\mingli_agent\mcp_server.py`:

```python
from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from mingli_agent.report_tool import generate_mingli_report as _generate_mingli_report


def build_mcp_server() -> FastMCP:
    server = FastMCP("mingli-report")

    @server.tool()
    def generate_mingli_report(
        calendar_type: str,
        birth_date: str,
        birth_time: str,
        birthplace: str,
        gender: str,
        focus_topic: str,
        format: str = "html",
    ) -> dict[str, Any]:
        """Generate a safe Mingli report and return a chat summary plus artifact path."""

        return _generate_mingli_report(
            {
                "calendar_type": calendar_type,
                "birth_date": birth_date,
                "birth_time": birth_time,
                "birthplace": birthplace,
                "gender": gender,
                "focus_topic": focus_topic,
                "format": format,
            }
        )

    return server


def main() -> None:
    build_mcp_server().run()
```

- [ ] **Step 4: Run MCP server test and verify GREEN**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
uv run --with pytest python -m pytest tests/test_mcp_server.py -v
```

Expected: PASS.

- [ ] **Step 5: Run the full Hermes wrapper test suite**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
uv run --with pytest python -m pytest
```

Expected: all tests pass.

- [ ] **Step 6: Verify the MCP script starts**

Run a bounded startup check:

```powershell
Set-Location E:\hermes-mingli-agent
$p = Start-Process -FilePath "uv" -ArgumentList @("run", "mingli-report-mcp") -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 3
if ($p.HasExited) { throw "MCP server exited early with code $($p.ExitCode)" }
Stop-Process -Id $p.Id
```

Expected: no exception is thrown.

- [ ] **Step 7: Commit MCP server**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
git add src/mingli_agent/mcp_server.py tests/test_mcp_server.py pyproject.toml
git commit -m "feat: expose mingli report mcp server"
```

Expected: commit succeeds.

## Task 5: Verify Real Mingli Engine Invocation

**Files:**
- Create: `E:\hermes-mingli-agent\tests\test_real_mingli_engine.py`

- [ ] **Step 1: Write real integration tests**

Create `E:\hermes-mingli-agent\tests\test_real_mingli_engine.py`:

```python
import os
from pathlib import Path

import pytest

from mingli_agent.report_tool import generate_mingli_report


ENGINE_ROOT = Path(os.environ.get("MINGLI_ENGINE_ROOT", "E:\\命理演绎"))


pytestmark = pytest.mark.skipif(
    not (ENGINE_ROOT / "src" / "mingli_engine" / "cli.py").exists(),
    reason="Mingli engine checkout is not available",
)


def test_real_engine_generates_html_report(tmp_path, monkeypatch):
    monkeypatch.setenv("MINGLI_ENGINE_ROOT", str(ENGINE_ROOT))
    monkeypatch.setenv("MINGLI_AGENT_RUNTIME_DIR", str(tmp_path))

    result = generate_mingli_report(
        {
            "calendar_type": "gregorian",
            "birth_date": "1990-01-01",
            "birth_time": "08:30",
            "birthplace": "北京",
            "gender": "女",
            "focus_topic": "事业发展",
            "format": "html",
        }
    )

    assert result["ok"] is True
    assert result["report_ready"] is True
    assert result["allowed"] is True
    artifact_path = Path(result["artifact_path"])
    assert artifact_path.exists()
    html = artifact_path.read_text(encoding="utf-8")
    assert html.startswith("<!doctype html>")
    assert "快速导读" in html


def test_real_engine_refuses_unsafe_focus(tmp_path, monkeypatch):
    monkeypatch.setenv("MINGLI_ENGINE_ROOT", str(ENGINE_ROOT))
    monkeypatch.setenv("MINGLI_AGENT_RUNTIME_DIR", str(tmp_path))

    result = generate_mingli_report(
        {
            "calendar_type": "gregorian",
            "birth_date": "1990-01-01",
            "birth_time": "08:30",
            "birthplace": "北京",
            "gender": "女",
            "focus_topic": "寿命",
            "format": "html",
        }
    )

    assert result["ok"] is True
    assert result["report_ready"] is False
    assert result["allowed"] is False
    assert "lifespan_or_death_timing" in result["red_line_categories"]
    assert "寿命" in result["message"]
```

- [ ] **Step 2: Run real integration tests**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
$env:MINGLI_ENGINE_ROOT='E:\命理演绎'
uv run --with pytest python -m pytest tests/test_real_mingli_engine.py -v
```

Expected: PASS with two tests.

- [ ] **Step 3: Run both project test suites**

Run:

```powershell
Set-Location E:\命理演绎
uv run --with pytest python -m pytest

Set-Location E:\hermes-mingli-agent
uv run --with pytest python -m pytest
```

Expected: Mingli tests pass and Hermes wrapper tests pass.

- [ ] **Step 4: Commit integration tests**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
git add tests/test_real_mingli_engine.py
git commit -m "test: verify real mingli engine calls"
```

Expected: commit succeeds.

## Task 6: Install And Configure Hermes Locally

**Files:**
- Read: `E:\hermes-mingli-agent\config\feishu-env.example`
- Read: `E:\hermes-mingli-agent\config\hermes-config-snippet.yaml`
- Modify user config: `~\.hermes\.env`
- Modify user config: `~\.hermes\config.yaml`

- [ ] **Step 1: Install Hermes Agent on native Windows**

Run in PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Expected: installer finishes and tells you to open a new PowerShell session.

- [ ] **Step 2: Open a new PowerShell and verify Hermes**

Run:

```powershell
hermes doctor
```

Expected: Hermes prints diagnostics. Resolve any missing provider/model setup before continuing.

- [ ] **Step 3: Configure a model provider**

Run:

```powershell
hermes model
```

Expected: Hermes saves a working LLM provider. Verify with:

```powershell
hermes chat
```

Send:

```text
ping
```

Expected: Hermes replies normally. Exit chat after the check.

- [ ] **Step 4: Configure Feishu/Lark gateway**

Run:

```powershell
hermes gateway setup
```

Choose Feishu/Lark. If QR scan setup is available, use it. If the wizard asks for manual credentials, use the Feishu app's App ID and App Secret. Do not paste App Secret into this repository.

Expected: Hermes writes Feishu credentials to `~\.hermes\.env`.

- [ ] **Step 5: Force WebSocket mode**

Open `~\.hermes\.env` and ensure these lines exist:

```dotenv
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_GROUP_POLICY=allowlist
FEISHU_REQUIRE_MENTION=true
```

If you know your Feishu Open ID, also set:

```dotenv
FEISHU_ALLOWED_USERS=ou_xxx
```

Expected: no credentials are written into `E:\命理演绎` or `E:\hermes-mingli-agent`.

- [ ] **Step 6: Register the MCP server**

Edit `~\.hermes\config.yaml` and add the `mcp_servers` block from `E:\hermes-mingli-agent\config\hermes-config-snippet.yaml`:

```yaml
mcp_servers:
  mingli_report:
    command: uv
    args:
      - run
      - --project
      - E:\hermes-mingli-agent
      - mingli-report-mcp
    env:
      MINGLI_ENGINE_ROOT: E:\命理演绎
      MINGLI_AGENT_RUNTIME_DIR: E:\hermes-mingli-agent\runtime
```

Expected: YAML remains valid.

- [ ] **Step 7: Enable the MCP toolset for Feishu**

Run:

```powershell
hermes tools
```

Enable the dynamic MCP toolset named `mcp-mingli_report` for the Feishu/Lark gateway platform. Keep unrelated powerful toolsets disabled for the Feishu bot unless you explicitly need them.

Expected: Hermes saves the tool configuration to `~\.hermes\config.yaml`.

- [ ] **Step 8: Verify Hermes sees the tool in CLI**

Run:

```powershell
hermes chat --toolsets mcp-mingli_report
```

Send:

```text
请使用 generate_mingli_report 生成一份报告：公历 1990-01-01 08:30，北京，女，关注事业发展。只返回工具结果摘要。
```

Expected: Hermes calls `generate_mingli_report` and returns an output containing `report_ready: true` or an equivalent summary.

## Task 7: Start Feishu WebSocket Gateway And Test Ping

**Files:**
- Read user config: `~\.hermes\.env`
- Read user config: `~\.hermes\config.yaml`
- Read logs: `~\.hermes\logs\gateway.log`

- [ ] **Step 1: Start Hermes gateway**

Run:

```powershell
hermes gateway
```

Expected: gateway starts without requesting a public webhook URL.

- [ ] **Step 2: Send direct Feishu message**

In Feishu, send the Hermes bot:

```text
ping
```

Expected: Hermes replies in the direct message.

- [ ] **Step 3: Set home chat**

In the same Feishu chat, send:

```text
/set-home
```

Expected: Hermes confirms the home channel.

- [ ] **Step 4: Test group mention policy**

In a Feishu group that contains the bot, send:

```text
@Hermes ping
```

Expected: Hermes replies only when mentioned. If it replies without a mention, check `FEISHU_REQUIRE_MENTION=true`.

- [ ] **Step 5: Check gateway logs**

Run in a second PowerShell:

```powershell
Get-Content -Path "$HOME\.hermes\logs\gateway.log" -Tail 80
```

Expected: no credential values are printed; message processing appears without repeated connection failures.

## Task 8: Test Mingli Report UX In Feishu

**Files:**
- Read: `E:\hermes-mingli-agent\runtime\outputs\`
- Read: `~\.hermes\logs\gateway.log`

- [ ] **Step 1: Send a safe structured request**

In Feishu direct message, send:

```text
生成报告
公历 1990-01-01 08:30
北京
女
关注：事业发展
```

Expected: Hermes replies with a concise summary and references a generated HTML report artifact.

- [ ] **Step 2: Verify local artifact**

Run:

```powershell
Get-ChildItem -Recurse E:\hermes-mingli-agent\runtime\outputs -Filter report.html | Sort-Object LastWriteTime -Descending | Select-Object -First 1 FullName
```

Expected: latest `report.html` exists.

- [ ] **Step 3: Open the latest HTML file**

Run:

```powershell
$latest = Get-ChildItem -Recurse E:\hermes-mingli-agent\runtime\outputs -Filter report.html | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Start-Process $latest.FullName
```

Expected: browser opens a report that starts with a complete HTML document and contains `快速导读`.

- [ ] **Step 4: Send a red-line request**

In Feishu direct message, send:

```text
生成报告
公历 1990-01-01 08:30
北京
女
关注：寿命
```

Expected: Hermes replies with a safety redirect message and does not create a new `report.html` for that request.

- [ ] **Step 5: Send an incomplete request**

In Feishu direct message, send:

```text
生成报告
公历 1990-01-01
北京
女
关注：事业发展
```

Expected: Hermes asks for birth time and does not create a formal report.

- [ ] **Step 6: Capture acceptance notes**

Run this command to append dated acceptance notes to `E:\hermes-mingli-agent\README.md`:

```powershell
$today = Get-Date -Format yyyy-MM-dd
@"

## Local Acceptance Notes

- `ping -> pong`: verified on $today
- Safe structured report: verified on $today
- Red-line focus topic refusal: verified on $today
- Incomplete request clarification: verified on $today
"@ | Add-Content -LiteralPath E:\hermes-mingli-agent\README.md -Encoding utf8
```

- [ ] **Step 7: Commit acceptance documentation**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
git add README.md
git commit -m "docs: record local feishu acceptance checks"
```

Expected: commit succeeds.

## Task 9: Final Verification And Handoff

**Files:**
- Read: `E:\命理演绎`
- Read: `E:\hermes-mingli-agent`

- [ ] **Step 1: Verify Mingli engine is still clean and tested**

Run:

```powershell
Set-Location E:\命理演绎
git status --short --branch
uv run --with pytest python -m pytest
```

Expected: current branch is clean, and all Mingli tests pass.

- [ ] **Step 2: Verify Hermes wrapper is clean and tested**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
git status --short --branch
uv run --with pytest python -m pytest
```

Expected: current branch is clean, and all Hermes wrapper tests pass.

- [ ] **Step 3: Verify Hermes gateway can start**

Run:

```powershell
hermes gateway
```

Expected: gateway starts in WebSocket mode and accepts Feishu messages.

- [ ] **Step 4: Record remaining operational items**

Create `E:\hermes-mingli-agent\OPERATIONS.md`:

````markdown
# Operations

## Start Local Gateway

```powershell
hermes gateway
```

## Required Local Paths

- Mingli engine: `E:\命理演绎`
- Hermes project: `E:\hermes-mingli-agent`

## Required Secrets

Secrets live in `~\.hermes\.env`, not in this repository.

Required Feishu settings:

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_DOMAIN=feishu`
- `FEISHU_CONNECTION_MODE=websocket`

## Report Retention

Generated HTML reports are written to `runtime\outputs`. Delete old files manually during local testing:

```powershell
Get-ChildItem -Recurse E:\hermes-mingli-agent\runtime\outputs -File | Remove-Item
```
````

- [ ] **Step 5: Commit operations guide**

Run:

```powershell
Set-Location E:\hermes-mingli-agent
git add OPERATIONS.md
git commit -m "docs: add local operations guide"
```

Expected: commit succeeds.

- [ ] **Step 6: Summarize handoff**

Report these items to the user:

```text
Hermes project path: E:\hermes-mingli-agent
Mingli engine path: E:\命理演绎
Feishu mode: websocket
Mingli tool exposure: MCP server mcp-mingli_report
Validation:
- Mingli pytest: pass
- Hermes wrapper pytest: pass
- Feishu ping: pass
- Safe report request: pass
- Red-line refusal: pass
Remaining follow-up:
- PDF delivery feature
- Production retention policy
- Server deployment
```
