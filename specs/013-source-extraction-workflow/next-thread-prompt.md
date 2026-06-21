# Next Thread Prompt

请用中文交流。工作目录是 `E:\命理演绎`，当前分支是
`016-extraction-queue-intake`。

继续采用“目标模式”：自主推进当前目标；每一步开始前简短告诉我下一步
做什么；目标完成后汇报结果并提出下一个目标。不要推送远程；除非我
明确要求，不要本地提交。

根目录 PDF、根目录 `Markdown/`、`资料原文/`、`资料整理/` 是外部
原始/准备资料，只能读取，不要移动、删除、转换、改写或提交。

当前工作区是脏状态，包含既有 tracked 修改与外部未跟踪资料；不要
revert 用户/既有改动。外部原始资料仍未跟踪、未改写。

请先读取：

- `AGENTS.md`
- `specs/017-learning-reference-curation/plan.md`
- `specs/013-source-extraction-workflow/tasks.md`
- `specs/013-source-extraction-workflow/quickstart.md`
- `docs/classical_sources/intake.md`
- `src/mingli_engine/models.py`
- `src/mingli_engine/source_intake.py`
- `tests/unit/test_source_intake.py`
- `tests/integration/test_report_regression_cases.py`

当前状态：

- 016、017 以及 013 后续人工审查准备链路已经推进到 013 Phase 76。
- `specs/013-source-extraction-workflow/tasks.md` 已完成 T001-T470。
- 最新 full suite：`uv run --with pytest python -m pytest`，结果
  `680 passed in 10812.87s (3:00:12)`。
- 最新 focused source-intake suite：
  `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`，
  结果 `237 passed in 11086.49s (3:04:46)`。
- 最新 boundary suite：
  `uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py`，
  结果 `128 passed in 4915.40s (1:21:55)`。
- 最新 targeted Phase 76 suite：
  `uv run --with pytest python -m pytest tests/unit/test_source_intake.py tests/integration/test_report_regression_cases.py -k "start_packet_coverage_audit" -vv`，
  结果 `4 passed`。
- `git diff --check` 最近只有 CRLF warning。
- 当前没有提交、没有推送。

最近完成的 013 Phase 76：

- Pending Review Manual Application Next-Session Manual Execution Start
  Packet Coverage Audit。
- 新增只读模型：
  `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAudit`。
- 新增只读 builder：
  `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit()`。
- 新增 Markdown renderer：
  `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_markdown()`。
- audit 基于 Phase 75 start packet，审计 Phase 75 是否完整覆盖 Phase 74
  start handoff packet coverage audit seal。
- 输出 `audit_status`、`coverage_checks`、`source_coverage_checks`、
  `missing_coverage`、`boundary_checks`、`blocked_reasons`、start checks、
  seal checks、handoff checks、source seal checks、authorization coverage
  checks、authorization checks、coverage seal checks、packet coverage checks、
  clearance checklist、sealed first step、sealed candidate order、operator
  authorization/start checklist、verification checklist、rollback path、
  post-completion review、target candidates、boundary confirmation 和 zero
  deltas。
- 保持 applied review decision delta=0、candidate status delta=0、formal
  evidence delta=0。
- 不自动写 `review_decisions.json`，不改 `candidate_extracts.json`，不
  promotion，不改变 formal evidence。

Phase 76 关键落点：

- `src/mingli_engine/models.py`
- `src/mingli_engine/source_intake.py`
- `tests/unit/test_source_intake.py`
- `tests/integration/test_report_regression_cases.py`
- `specs/013-source-extraction-workflow/quickstart.md`
- `docs/classical_sources/intake.md`
- `specs/013-source-extraction-workflow/tasks.md`

下一步建议目标：

完成 013 Phase 77 pending review manual execution start packet coverage
audit seal 闭环。目标是冻结 Phase 76 start packet coverage audit，输出
seal status、audit status、start packet status、start packet source audit
status、seal checks、coverage checks、source coverage checks、missing
coverage、boundary checks、blocked reasons、target candidates、boundary
confirmation 和 zero deltas。继续 TDD：先写红灯测试，再实现模型、
builder、renderer，再更新 quickstart、docs、tasks，最后跑 targeted、
focused、boundary、full tests。保持只读规划/预览边界，不自动写
`review_decisions.json`、不改 `candidate_extracts.json`、不 promotion、
不改变 formal evidence。

建议 Phase 77 命名：

- Model:
  `CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAuditSeal`
- Builder:
  `build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal`
- Renderer:
  `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal_markdown`

注意：

- 测试非常慢；focused source-intake 和 full suite 可能各需数小时。若
  普通工具超时，改用更长 timeout 或临时日志轮询，但不要把无摘要的
  中断输出当作通过证据。
- 若 `git status` 看到外部 PDF、`Markdown/`、`资料原文/`、`资料整理/`
  未跟踪，保持只读和未提交。
- 不要清理、格式化或 revert 与本目标无关的既有脏改动。
