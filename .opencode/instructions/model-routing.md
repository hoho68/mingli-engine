# Model Routing

Minimize use of the primary GPT-5.6-Sol context while preserving deterministic
and privacy-bounded execution.

## Default Delegation

Delegate ordinary authorized source-facing work to `scan-reader` before the
primary agent reads or analyzes the material body. Batch related pages or text
chunks when source locators remain unambiguous.

`scan-reader` owns the first pass for:

- scanned-page transcription and OCR correction candidates;
- visual layout, table, vertical-text, and cross-page interpretation;
- page and chunk summaries;
- candidate learning points and rule structures;
- preliminary duplicate, conflict, limitation, and risk signals;
- normalization of Kimi output into the declared JSON candidate shape.

The primary agent supplies only metadata needed for routing: authorization
state, risk tier, file SHA-256, and exact page or chunk locators. It should
consume Kimi's structured result rather than repeat the full source reading.

## Primary-Agent Responsibilities

Keep these tasks with Build/GPT-5.6-Sol or deterministic local tools:

- file inventory, hashing, source mutation checks, and text-quality routing;
- rights, privacy, and remote-processing authorization decisions;
- implementation, tests, schemas, loaders, transactions, and release gates;
- source-locator verification against the original page;
- final conflict adjudication and formal knowledge promotion;
- code review through `code-review`.

Do not send private, rights-unclear, or high-risk material to Kimi. Do not send
whole PDFs; render and dispatch only the selected authorized pages. Every Kimi
result remains a candidate.

## Owner Rights Reclassification

For `batch_20260714`, the workspace owner explicitly authorizes remote-model
processing for every exact file listed in the frozen manifest. The manifest
file SHA-256 is
`dcec5b55971905f8d48a80faa2e685cea1a5f880613a7c22e91fe37720c8cea3`.
Embedded or filename wording such as `内部资料`, `绝密资料`, `注意保存`,
`禁止外传`, `不能外泄`, `confidential`, or equivalent non-disclosure wording
does not establish the current rights classification and must not, by itself,
create or retain a remote-processing hold for those manifest-bound bytes.

This batch-wide owner reclassification supersedes the earlier two-file
exception. It is bound to the exact frozen manifest and does not automatically
apply to new, changed, or unmanifested files. Existing holds based solely on
such wording must be re-adjudicated through the governed policy and coverage
transaction before dispatch.

The owner rights reclassification does not waive independent privacy, safety,
or technical controls. Contact identifiers and other private data still require
local redaction or a separate explicit privacy clearance. High-risk content,
source conflicts, whole-file upload, page-boundary enforcement, input-size
limits, retry limits, and candidate-only status remain governed as before.

Escalate from Kimi to GPT only when the result is unreadable, structurally
invalid after retry, high-risk, source-conflicted, or requires a final governed
decision.
