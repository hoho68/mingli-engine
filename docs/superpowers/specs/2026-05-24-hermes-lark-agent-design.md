# Hermes Lark Agent Integration Design

## Summary

Add an integration path that lets a Hermes Agent, exposed to users as a Feishu/Lark bot, call the existing Mingli report engine. The Hermes runtime will live in a separate project directory at `E:\hermes-mingli-agent`, while this repository remains the core calculation, safety, and report-rendering engine.

The first milestone is a local long-connection setup: Hermes receives Feishu messages through Lark's long connection/event stream, calls this project as a tool, replies with a short report summary in chat, and delivers the full report as an HTML attachment or file link.

## Goals

- Keep `E:\命理演绎` focused on Mingli calculation, safety checks, Markdown rendering, and HTML rendering.
- Create a separate Hermes project at `E:\hermes-mingli-agent` for Feishu bot configuration, long-connection runtime, prompts, tool wrappers, logs, and deployment settings.
- Use Feishu/Lark long connection for local development instead of public HTTPS webhook tunnels.
- Expose one initial Hermes tool: `generate_mingli_report`.
- Return concise chat-friendly summaries in Feishu, while preserving full reports as files.
- Preserve all existing red-line refusal behavior and report safety boundaries.

## Non-Goals

- Do not build a separate custom Feishu bot backend outside Hermes.
- Do not move Mingli engine source code into the Hermes project.
- Do not store user birth data in this repository.
- Do not add new Mingli interpretations, chart calculations, or deterministic claims.
- Do not require public webhook infrastructure for the local prototype.
- Do not implement PDF export in this milestone; PDF can be a follow-up feature after HTML attachment delivery works.

## Project Layout

```text
E:\
|-- 命理演绎\
|   |-- src\mingli_engine\
|   |-- tests\
|   |-- specs\
|   `-- pyproject.toml
|
`-- hermes-mingli-agent\
    |-- hermes configuration
    |-- feishu/lark long-connection configuration
    |-- tools\
    |   `-- generate_mingli_report
    |-- prompts\
    |-- runtime\
    |   |-- inputs\
    |   |-- outputs\
    |   `-- logs\
    `-- README.md
```

The Hermes project may call the Mingli engine by CLI during the prototype:

```powershell
$env:PYTHONPATH='E:\命理演绎\src'
uv run --project E:\命理演绎 python -m mingli_engine.cli calculate-report --input <input.json> --format html
```

After the integration stabilizes, the tool wrapper can switch to direct Python imports or package installation if that makes deployment cleaner.

## User Flow

1. A user sends a structured request to the Hermes bot in Feishu.
2. Hermes identifies the request as a Mingli report request.
3. Hermes extracts or asks for required fields:
   - calendar type
   - birth date
   - birth time
   - birthplace
   - gender label
   - focus topic
4. Hermes invokes `generate_mingli_report`.
5. The tool creates a temporary birth-profile JSON file and calls the Mingli CLI.
6. If the Mingli engine returns a safety refusal or validation result, Hermes replies with that safe message and does not attach a formal report.
7. If the report is safe, Hermes replies with a concise summary and attaches or links the full HTML report.

Example Feishu request:

```text
生成报告
公历 1990-01-01 08:30
北京
女
关注：事业发展
```

Example Feishu reply:

```text
八字结构化报告已生成

本报告仅作传统命理文化解读与自我反思，不作为科学预测或专业建议。

快速导读：
- 来源：系统自动排盘，当前标记为中等可信度
- 路径：先核对资料与假设，再看结构观察，最后转成行动反思

完整报告见附件：八字结构化报告.html
```

## Tool Contract

### Tool Name

`generate_mingli_report`

### Input

```json
{
  "calendar_type": "gregorian",
  "birth_date": "1990-01-01",
  "birth_time": "08:30",
  "birthplace": "北京",
  "gender": "female",
  "focus_topic": "事业发展",
  "format": "html"
}
```

### Output

Safe report:

```json
{
  "ok": true,
  "report_ready": true,
  "allowed": true,
  "summary": "chat-friendly summary text",
  "format": "html",
  "artifact_path": "runtime/outputs/<id>/report.html"
}
```

Safety refusal:

```json
{
  "ok": true,
  "report_ready": false,
  "allowed": false,
  "red_line_categories": ["lifespan_or_death_timing"],
  "message": "不预测寿命或死亡时间。可以改为讨论风险意识、身心节律与生活安排。"
}
```

Invalid input:

```json
{
  "ok": true,
  "report_ready": false,
  "allowed": true,
  "missing_fields": ["birth_time"],
  "message": "请补充出生时间。"
}
```

Runtime failure:

```json
{
  "ok": false,
  "message": "报告生成暂时不可用，请稍后重试。"
}
```

The tool must not expose stack traces, local secrets, app credentials, or raw token values to Feishu users.

## Feishu/Lark Long Connection

The local prototype should use long connection/event consumption instead of webhook tunnels. The relevant event stream is message receive, such as `im.message.receive_v1`, consumed as bot identity.

For local diagnostics, a bounded event listener can be used:

```powershell
lark-cli event consume im.message.receive_v1 --max-events 1 --timeout 30s --as bot
```

The Hermes runtime should manage long-running consumption, dispatch events to the agent, and perform graceful shutdown. The implementation should avoid duplicate event handling and should ignore messages sent by the bot itself.

## Message Handling

Hermes should initially support a small, explicit command surface:

- `ping`: reply with a simple health response.
- `生成报告 ...`: attempt to parse a structured report request.
- incomplete report requests: ask for the missing field instead of guessing.
- red-line topics: return the Mingli engine's safety redirect message.

The first version does not need broad natural-language extraction. It should prefer stable structured input and clear clarification prompts.

## Report Delivery

Feishu chat messages should not contain the full HTML document inline. Hermes should send:

- a concise text or card summary in the chat
- the full HTML report as an uploaded file or stable file link

HTML is the first full-report artifact because this project already supports pure static HTML. PDF export is a future milestone once HTML file delivery is reliable.

## Safety And Privacy

- The Mingli engine remains the authority for red-line refusal and report wording safety.
- Hermes must not generate a formal report if the engine returns safety JSON or invalid-input JSON.
- Birth data and generated reports should be treated as sensitive personal data.
- Runtime input/output files should live under the Hermes project runtime directory, not in this repository.
- Retention should be short by default for local testing; production deployment should define explicit retention and deletion rules.
- Feishu replies must preserve the report disclaimer and avoid deterministic language.

## Error Handling

- Missing fields: ask one concise follow-up question.
- Unsupported calendar input: return the engine's existing invalid-input behavior.
- Mingli CLI failure: log internally, return a generic user-facing failure.
- Feishu upload failure: send the summary and tell the user the full report attachment failed.
- Long-connection disconnect: Hermes should reconnect according to its runtime strategy; duplicate events should be deduplicated if event IDs are available.

## Testing Strategy

This repository:

- Keep the existing Mingli full suite passing.
- Add tests only if this repository gains a dedicated adapter or helper for Hermes.

Hermes project:

- Unit-test request parsing from sample Feishu text.
- Unit-test `generate_mingli_report` with safe, invalid, and red-line inputs.
- Integration-test CLI invocation against `E:\命理演绎`.
- Manual local acceptance test: `ping -> pong`.
- Manual local acceptance test: structured birth data -> summary plus HTML artifact.
- Manual local acceptance test: unsafe focus topic -> safety message and no report artifact.

## Milestones

### 011A: Hermes Local Skeleton

- Create `E:\hermes-mingli-agent`.
- Install and configure Hermes for local development.
- Configure Feishu long connection credentials.
- Verify `ping -> pong`.

### 011B: Mingli Tool Wrapper

- Add `generate_mingli_report`.
- Convert structured input into birth-profile JSON.
- Call the Mingli CLI.
- Normalize safe, invalid, and safety outputs.

### 011C: Feishu Report UX

- Parse the first fixed request format.
- Reply with concise summary.
- Attach or link the generated HTML file.
- Handle red-line and invalid-input cases without generating a formal report.

### Future: PDF Delivery

- Add PDF export after HTML delivery is stable.
- Prefer PDF attachment for non-technical Feishu users.

## Open Questions

- Which exact Hermes Agent distribution and configuration format will be used locally?
- Does Hermes provide a native tool schema format that should wrap `generate_mingli_report`?
- Should the first HTML file be uploaded directly to Feishu, or stored locally with a temporary link?
- What retention period should local generated reports use during testing?
