# Quickstart: Source Extraction Workflow

## Goal

Use 013 to manage source material intake safely before anything becomes formal report evidence.

## Current Boundary

- Root PDF files and root `Markdown/` are external preparation material.
- Do not move, delete, convert, or commit those materials unless the user explicitly asks.
- Candidate extracts are not formal evidence.
- Reports may use only approved and promoted evidence units from the 012 corpus.

## Reviewer Workflow

1. Register source materials with stable `material_id` values and `tracking_status=external_untracked` when the source file remains outside tracked project data.
2. Add candidate extracts with source locator, extracted meaning, proposed rule family, risk tier, limitations, and pending review status.
3. Review candidates one by one.
4. Use the pending candidate review worklist to identify locator, source-quality, duplicate, conflict, gap, and safety checks before writing a review decision.
5. Approve only candidates with reviewable locator, concise meaning, source quality, confidence, limitations, and no unresolved blocking issue.
6. Return candidates that need better locator, safer language, clearer rule family, or duplicate/conflict handling.
7. Reject or block candidates that are unsafe, source-poor, rights-sensitive, too copied, or not convertible into evidence.
8. Place approved candidates into a promotion batch before updating the formal evidence corpus.
9. Re-run intake validation and report regression tests before implementation completion.

## Expected Validation Commands

Run all tests:

```powershell
uv run --with pytest python -m pytest
```

Run focused intake tests after implementation:

```powershell
uv run --with pytest python -m pytest tests/unit/test_source_intake.py
```

Run report boundary regression tests:

```powershell
uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py
```

Run the source-intake quality check from the local package:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import build_intake_progress_report, validate_intake_quality; r=build_intake_progress_report(); print(r); print(validate_intake_quality())"
```

Run the pending candidate review worklist:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import list_pending_candidate_review_worklist; print(list_pending_candidate_review_worklist())"
```

Run the pending candidate review decision packets:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import list_pending_candidate_review_decision_packets; print(list_pending_candidate_review_decision_packets())"
```

Run the pending candidate review packet summary:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import build_pending_candidate_review_packet_summary; print(build_pending_candidate_review_packet_summary())"
```

Run the pending candidate review action queue:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import build_pending_candidate_review_action_queue; print(build_pending_candidate_review_action_queue())"
```

Render the pending candidate review action queue as Markdown:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_action_queue_markdown; print(render_pending_candidate_review_action_queue_markdown())"
```

Render the pending candidate review input templates as Markdown:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_input_templates_markdown; print(render_pending_candidate_review_input_templates_markdown())"
```

Validate a filled pending candidate review decision draft without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_draft_validation_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_draft_validation_markdown(drafts))"
```

Preview manual application of a validated review decision draft without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_application_guard_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_application_guard_markdown(drafts))"
```

Export a manual application packet with copyable JSON snippets without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_application_packets_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_application_packets_markdown(drafts))"
```

Render the manual application audit summary without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_application_audit_summary_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_application_audit_summary_markdown(drafts))"
```

Render the pending review manual action dashboard without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_action_dashboard_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''},{'decision_id':'review_candidate_northeast_blind_image_001','candidate_id':'candidate_northeast_blind_image_001','review_outcome':'approved','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'review-note:northeast_blind_peak.md#blind-image-method','source_quality':'needs_recheck','confidence':'moderate','rationale':'Draft still lacks duplicate and safety resolution.','approval_limitations':[],'uncertainty_and_limitation_language':'','duplicate_or_reuse_resolution':''}]; print(render_pending_candidate_review_manual_action_dashboard_markdown(drafts))"
```

Render the pending review manual application dry-run guide without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_dry_run_guide_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''},{'decision_id':'review_candidate_northeast_blind_image_001','candidate_id':'candidate_northeast_blind_image_001','review_outcome':'approved','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'review-note:northeast_blind_peak.md#blind-image-method','source_quality':'needs_recheck','confidence':'moderate','rationale':'Draft still lacks duplicate and safety resolution.','approval_limitations':[],'uncertainty_and_limitation_language':'','duplicate_or_reuse_resolution':''}]; print(render_pending_candidate_review_manual_application_dry_run_guide_markdown(drafts))"
```

Render the pending review manual application preflight report without writing
data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_preflight_report_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''},{'decision_id':'review_candidate_northeast_blind_image_001','candidate_id':'candidate_northeast_blind_image_001','review_outcome':'approved','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'review-note:northeast_blind_peak.md#blind-image-method','source_quality':'needs_recheck','confidence':'moderate','rationale':'Draft still lacks duplicate and safety resolution.','approval_limitations':[],'uncertainty_and_limitation_language':'','duplicate_or_reuse_resolution':''}]; print(render_pending_candidate_review_manual_application_preflight_report_markdown(drafts))"
```

Render the pending review manual application handoff summary without writing
data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_handoff_summary_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''},{'decision_id':'review_candidate_northeast_blind_image_001','candidate_id':'candidate_northeast_blind_image_001','review_outcome':'approved','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'review-note:northeast_blind_peak.md#blind-image-method','source_quality':'needs_recheck','confidence':'moderate','rationale':'Draft still lacks duplicate and safety resolution.','approval_limitations':[],'uncertainty_and_limitation_language':'','duplicate_or_reuse_resolution':''}]; print(render_pending_candidate_review_manual_application_handoff_summary_markdown(drafts))"
```

Render the pending review manual application readiness ledger without writing
data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_readiness_ledger_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''},{'decision_id':'review_candidate_northeast_blind_image_001','candidate_id':'candidate_northeast_blind_image_001','review_outcome':'approved','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'review-note:northeast_blind_peak.md#blind-image-method','source_quality':'needs_recheck','confidence':'moderate','rationale':'Draft still lacks duplicate and safety resolution.','approval_limitations':[],'uncertainty_and_limitation_language':'','duplicate_or_reuse_resolution':''}]; print(render_pending_candidate_review_manual_application_readiness_ledger_markdown(drafts))"
```

Render the pending review manual application session packet without writing
data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_session_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''},{'decision_id':'review_candidate_northeast_blind_image_001','candidate_id':'candidate_northeast_blind_image_001','review_outcome':'approved','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'review-note:northeast_blind_peak.md#blind-image-method','source_quality':'needs_recheck','confidence':'moderate','rationale':'Draft still lacks duplicate and safety resolution.','approval_limitations':[],'uncertainty_and_limitation_language':'','duplicate_or_reuse_resolution':''}]; print(render_pending_candidate_review_manual_application_session_packet_markdown(drafts))"
```

Render the pending review manual application session outcome preview without
writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_session_outcome_preview_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''},{'decision_id':'review_candidate_northeast_blind_image_001','candidate_id':'candidate_northeast_blind_image_001','review_outcome':'approved','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'review-note:northeast_blind_peak.md#blind-image-method','source_quality':'needs_recheck','confidence':'moderate','rationale':'Draft still lacks duplicate and safety resolution.','approval_limitations':[],'uncertainty_and_limitation_language':'','duplicate_or_reuse_resolution':''}]; print(render_pending_candidate_review_manual_application_session_outcome_preview_markdown(drafts))"
```

Render the pending review manual application post-session verification report
without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_post_session_verification_report_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_post_session_verification_report_markdown(drafts))"
```

Render the pending review manual application reconciliation dashboard without
writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_reconciliation_dashboard_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_reconciliation_dashboard_markdown(drafts))"
```

Render the pending review manual application closure packet without writing
data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_closure_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_closure_packet_markdown(drafts))"
```

Render the pending review manual application next-session starter without
writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_starter_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_starter_markdown(drafts))"
```

Render the pending review manual application next-session packet without
writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_packet_markdown(drafts))"
```

Render the pending review manual application next-session audit summary without
writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_audit_summary_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_audit_summary_markdown(drafts))"
```

Render the pending review manual application next-session operator checklist
without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_operator_checklist_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_operator_checklist_markdown(drafts))"
```

Render the pending review manual application next-session execution handoff
without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_execution_handoff_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_execution_handoff_markdown(drafts))"
```

Render the pending review manual application next-session completion criteria
without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_completion_criteria_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_completion_criteria_markdown(drafts))"
```

Render the pending review manual application next-session retry planner without
writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_retry_planner_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_retry_planner_markdown(drafts))"
```

Render the pending review manual application next-session final readiness summary
without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_final_readiness_summary_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_final_readiness_summary_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
launch note without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
launch audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
launch seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
launch runbook without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
launch runbook audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
launch runbook audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
final launch packet without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
final launch packet handoff audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
final launch packet handoff audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
operator go/no-go seal launch receipt without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
launch receipt final boundary audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
launch receipt final boundary audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
launch receipt final boundary audit seal operator start packet without writing
data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
operator start packet audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
operator start packet audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start authorization receipt without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start authorization receipt coverage audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start authorization receipt coverage audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
authorization packet without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
authorization packet coverage audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
authorization packet coverage audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
authorization packet coverage audit seal start docket without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start docket coverage audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start docket coverage audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
final start packet without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
final start packet handoff audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
final start packet handoff audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start authorization packet without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start authorization packet coverage audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start authorization packet coverage audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start clearance packet without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start clearance packet coverage audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start clearance packet coverage audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start clearance packet final start authorization without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start clearance packet final start authorization coverage audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start clearance packet final start authorization coverage audit seal without
writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start handoff packet without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start handoff packet coverage audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start handoff packet coverage audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start packet without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start packet coverage audit without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_markdown(drafts))"
```

Render the pending review manual application next-session manual execution
start packet coverage audit seal without writing data:

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.source_intake import render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal_markdown; drafts=[{'decision_id':'review_candidate_duan_ten_god_relation_017_001','candidate_id':'candidate_duan_ten_god_relation_017_001','review_outcome':'returned','reviewer':'maintainer','reviewed_at':'2026-06-01','source_locator':'learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001','source_quality':'review_note','confidence':'weak','rationale':'Returned until source page or section locator is supplied.','required_changes':['Replace learning-reference locator before approval.'],'approval_limitations':[],'rejection_reason':''}]; print(render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal_markdown(drafts))"
```

## Expected Intake Snapshot

After 017 candidate application and review-worklist support, the current
source-intake data computes to:

- Source material preparation: `partially_reviewed=7`, `indexed=1`, `not_started=1`.
- Candidate status: `pending_review=5`, `returned=1`, `approved=1`, `rejected=2`, `blocked=1`.
- Risk tiers: `sensitive=5`, `high_risk=2`, `ordinary=3`.
- Rule families: `blind_image_method=4`, `high_risk_signal=1`, `pattern_strength=2`, `ten_god_relation=1`, `five_element_balance=1`, `remedy_boundary=1`.
- Approval readiness: `approved_not_promoted=0`.
- Audit links: `duplicate_candidates=1`, `conflict_link_count=1`, `gap_link_count=1`.
- `validate_intake_quality()` returns an empty list for the checked-in intake data.
- `list_pending_candidate_review_worklist()` returns the five current pending
  candidates with required review actions before any review decision is written.
- `list_pending_candidate_review_decision_packets()` returns the five current
  pending candidates with decision options, required review inputs, approval
  blockers, packet actions, and formal-evidence boundary notes. It does not
  write review decisions or promotion batches.
- `build_pending_candidate_review_packet_summary()` returns
  `packet_count=5`, decision option counts of 5 each for `approved`,
  `returned`, `rejected`, and `blocked`, required locator replacement count
  `source_page_or_section_locator=4`, uncertainty/limitation input count `3`,
  duplicate/reuse input count `1`, and `review_decision_delta=0`,
  `formal_evidence_delta=0`.
- `build_pending_candidate_review_action_queue()` returns five high-priority
  planning items: first resolve duplicate/reuse context for
  `candidate_northeast_blind_image_001`, then replace learning-reference
  locators for the four 017-created candidates. It does not write review
  decisions or formal evidence.
- `render_pending_candidate_review_action_queue_markdown()` returns a stable
  Markdown checklist with `Queue items=5`, `Review packet count=5`,
  `Review decision delta=0`, `Formal evidence delta=0`, and five unchecked
  candidate action items.
- `render_pending_candidate_review_input_templates_markdown()` returns five
  fillable candidate review templates with base review fields, outcome-specific
  fields, conditional blocker fields, `Review decision delta=0`, and
  `Formal evidence delta=0`. The templates are input scaffolds only; they do
  not write `review_decisions.json`.
- `render_pending_candidate_review_draft_validation_markdown()` validates
  filled draft inputs before a maintainer manually writes any data. A returned
  draft with required changes can be ready for manual application; an approved
  draft remains blocked until approval limitations, locator replacement,
  duplicate/reuse resolution, and uncertainty/limitation language are present
  when required. Draft validation reports `Review decision delta=0` and
  `Formal evidence delta=0`.
- `render_pending_candidate_review_application_guard_markdown()` previews the
  manual data changes for drafts that passed validation. A ready returned draft
  shows `Preview review decision additions=1`,
  `Preview candidate status updates=1`, `Applied review decision delta=0`,
  `Applied candidate status delta=0`, and `Formal evidence delta=0`.
- `render_pending_candidate_review_application_packets_markdown()` exports
  copyable manual instructions for ready previews: a review-decision JSON
  snippet, a candidate-status update snippet, manual checklist items, rollback
  notes, and zero applied/formal-evidence deltas.
- `render_pending_candidate_review_application_audit_summary_markdown()`
  summarizes templates, supplied drafts, validation, guard previews, and
  application packets. It names exportable candidates, blocked candidates, and
  candidates still needing filled input templates, while keeping applied
  review-decision, candidate-status, and formal-evidence deltas at zero.
- `render_pending_candidate_review_manual_action_dashboard_markdown()` groups
  the same five pending candidates by shortest next manual action. With one
  exportable returned draft for `candidate_duan_ten_god_relation_017_001` and
  one blocked approved draft for `candidate_northeast_blind_image_001`, it
  reports `apply_manual_application_packet=1`,
  `resolve_draft_blocking_issues=1`, and `fill_review_input_template=3`.
  Recommended processing order is: apply the Duan packet, resolve the
  Northeast blocking issues, then fill templates for
  `candidate_mingli_pattern_strength_017_001`,
  `candidate_mingxue_five_element_balance_017_001`, and
  `candidate_hongfu_remedy_boundary_017_001`. Applied review-decision,
  candidate-status, and formal-evidence deltas remain zero.
- `render_pending_candidate_review_manual_application_dry_run_guide_markdown()`
  expands that dashboard into per-candidate dry-run steps. The exportable Duan
  candidate lists `append_review_decision_entry`, `update_candidate_status`,
  post-apply checks `run_source_intake_tests` and
  `verify_formal_evidence_delta_zero`, plus rollback notes. The blocked
  Northeast draft lists required inputs `approval_limitations`,
  `uncertainty_and_limitation_language`, and
  `duplicate_or_reuse_resolution`, with blocking issues that must clear before
  re-running validation and guard previews. The three missing-draft candidates
  list their template fields and conditional locator/safety inputs. Applied
  review-decision, candidate-status, and formal-evidence deltas remain zero.
- `render_pending_candidate_review_manual_application_preflight_report_markdown()`
  checks the manual application packets before a human applies them. With the
  same sample drafts, the Duan candidate is ready because its review-decision
  id is unique, its candidate-status patch starts from `pending_review`, and
  its expected review-decision/status deltas match the packet preview. The
  Northeast draft is blocked by the non-exportable packet and draft issues;
  the three missing-draft candidates are blocked by missing packets. Ready
  candidate count is `1`, blocked candidate count is `4`, preview deltas are
  `1/1`, and applied review-decision, candidate-status, and formal-evidence
  deltas remain zero.
- `render_pending_candidate_review_manual_application_handoff_summary_markdown()`
  turns the dashboard, dry-run guide, and preflight report into one human
  execution handoff. With the same sample drafts, ready candidates are
  `candidate_duan_ten_god_relation_017_001`; blocked candidates are
  `candidate_northeast_blind_image_001`; missing-draft candidates are the
  remaining three 017-created pending candidates. The Duan item carries manual
  steps, preflight checks, post-apply checks, rollback notes, and the expected
  `pending_review -> returned` status update. Applied review-decision,
  candidate-status, and formal-evidence deltas remain zero.
- `render_pending_candidate_review_manual_application_readiness_ledger_markdown()`
  turns that handoff into an unchecked manual ledger. The same sample drafts
  produce five ledger rows: one `ready_to_apply_manual_packet`, one
  `blocked_resolve_draft_issues`, and three `needs_review_input_template`
  rows. The ready row includes checkboxes for confirming preflight checks,
  appending the review decision, updating candidate status, running tests, and
  verifying formal-evidence delta zero. All checkboxes are planning metadata;
  applied review-decision, candidate-status, and formal-evidence deltas remain
  zero.
- `render_pending_candidate_review_manual_application_session_packet_markdown()`
  compresses the readiness ledger into one manual session packet. The same
  sample drafts produce a `ready_first_manual_application` session with one
  ready action, one blocked follow-up, three missing-draft follow-ups, and
  post-session verification checkboxes for source-intake tests,
  formal-evidence delta zero, rerunning the readiness ledger, and confirming
  manual-only changes. Applied review-decision, candidate-status, and
  formal-evidence deltas remain zero.
- `render_pending_candidate_review_manual_application_session_outcome_preview_markdown()`
  previews the outcome of applying only the ready actions in the session. The
  same sample drafts project the Duan candidate from `pending_review` to
  `returned`, leave the four follow-up candidates in `pending_review`, and
  list post-session next actions to rerun tests, rerun the readiness ledger,
  resolve blocked follow-ups, and fill missing draft templates. Applied
  review-decision, candidate-status, and formal-evidence deltas remain zero.
- `render_pending_candidate_review_manual_application_post_session_verification_report_markdown()`
  checks whether the ready-only session outcome is now visible in the data. On
  the current checked-in data before manual application, the Duan ready action
  is reported as blocked by a missing review decision and unchanged candidate
  status; after a maintainer manually applies the ready packet, the same report
  can verify the Duan decision/status update while confirming the follow-up
  candidates remain `pending_review`. The report itself keeps applied
  review-decision, candidate-status, and formal-evidence deltas at zero.
- `render_pending_candidate_review_manual_application_reconciliation_dashboard_markdown()`
  turns post-session verification results into the next manual processing
  board. It groups candidates into `append_missing_review_decision`,
  `correct_candidate_status`, `investigate_follow_up_mismatch`,
  `continue_follow_up_processing`, and `verified_complete`, then emits a
  recommended processing order. The dashboard itself keeps applied
  review-decision, candidate-status, and formal-evidence deltas at zero.
- `render_pending_candidate_review_manual_application_closure_packet_markdown()`
  turns the reconciliation dashboard into a session closure packet. Verified
  candidates are listed under session closure; candidates needing missing
  review-decision writes, status correction, follow-up investigation, or normal
  follow-up work are carried forward into the next manual session setup. The
  packet itself keeps applied review-decision, candidate-status, and
  formal-evidence deltas at zero.
- `render_pending_candidate_review_manual_application_next_session_starter_markdown()`
  converts closure-packet carry-forward items into the next manual session
  entrypoint. It groups work into missing review-decision, candidate-status
  correction, follow-up mismatch investigation, and follow-up processing lanes,
  with candidate-level checklists and a recommended start order. Closed
  candidates do not re-enter the starter items.
- `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_markdown()`
  audits the manual execution start handoff packet against the final start
  authorization coverage audit seal. It reports
  `manual_execution_start_handoff_packet_coverage_audit_ready`, coverage
  checks, missing coverage, boundary checks, handoff checks, operator start
  checklist, verification checklist, rollback path, post-completion review,
  target candidates, blocked reasons, boundary confirmation, and zero applied
  review-decision, candidate-status, and formal-evidence deltas.
- `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_markdown()`
  freezes the manual execution start handoff packet coverage audit as a
  read-only audit seal. It reports
  `sealed_for_manual_execution_start_handoff_packet_coverage_audit`, the
  source audit status, handoff packet status, handoff status, final start
  authorization coverage audit seal status, coverage checks, boundary checks,
  seal checks, operator start checklist, target candidates, blocked reasons,
  and zero applied review-decision, candidate-status, and formal-evidence
  deltas.
- `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_markdown()`
  compresses the manual execution start handoff packet coverage audit seal
  into a read-only operator-facing start packet. It reports
  `ready_for_operator_manual_execution_start_packet`, start checks, seal
  checks, coverage checks, missing coverage, boundary checks, operator start
  checklist, target candidates, blocked reasons, and zero applied
  review-decision, candidate-status, and formal-evidence deltas.
- `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_markdown()`
  audits that start packet against the start handoff packet coverage audit
  seal. It reports `manual_execution_start_packet_coverage_audit_ready`,
  coverage checks, source coverage checks, missing coverage, boundary checks,
  start checks, operator start checklist, target candidates, blocked reasons,
  and zero applied review-decision, candidate-status, and formal-evidence
  deltas.
- `render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal_markdown()`
  freezes the ready start packet coverage audit into a read-only audit seal.
  It reports `sealed_for_manual_execution_start_packet_coverage_audit`,
  audit status, start packet status, start packet source audit status, seal
  checks, coverage checks, source coverage checks, missing coverage, boundary
  checks, target candidates, blocked reasons, boundary confirmation, and zero
  applied review-decision, candidate-status, and formal-evidence deltas.

## Manual Review Checklist

- Source materials are registered without tracking raw root files.
- Pending candidates include source material, locator, extracted meaning, proposed rule family, risk tier, and status.
- Pending candidate review worklists are planning metadata only; they do not create review decisions or formal evidence.
- Review decision packets list what a human reviewer must fill before writing
  `review_decisions.json`; they must not approve, reject, block, return, or
  promote candidates by themselves.
- Review input templates are fillable scaffolds for a human reviewer; they do
  not write review decisions, promotion batches, or formal evidence.
- Draft validation checks filled template data before manual application; it
  never writes `review_decisions.json` or updates candidate status.
- Application guard previews the exact manual review-decision addition and
  candidate-status update; it still never writes JSON, promotes candidates, or
  updates formal evidence.
- Application packets are copyable manual instructions only; they do not write
  `review_decisions.json`, update `candidate_extracts.json`, promote
  candidates, or change formal evidence.
- Application audit summaries are read-only dashboards that identify the
  shortest next manual action for each pending candidate.
- Manual action dashboards group those shortest next actions into execution
  lanes and recommended processing order; they remain read-only planning
  metadata.
- Manual application dry-run guides expand the recommended order into
  candidate-level steps, ready criteria, post-apply checks, and rollback notes;
  they remain read-only planning metadata.
- Manual application preflight reports verify review-decision id uniqueness,
  pending-status patch alignment, and packet preview delta consistency before
  manual application; they remain read-only planning metadata.
- Manual application handoff summaries combine dashboard lanes, dry-run steps,
  and preflight checks into one read-only human execution sheet.
- Manual application readiness ledgers render that execution sheet as an
  unchecked read-only ledger for a maintainer to follow manually.
- Manual application session packets compress the readiness ledger into a
  ready-first manual session with follow-ups and post-session verification.
- Manual application session outcome previews project ready-action results and
  remaining pending follow-ups without writing review decisions, candidate
  statuses, promotion data, or formal evidence.
- Manual application post-session verification reports check the actual data
  after a manual ready-action application; the report remains read-only and
  does not repair mismatches automatically.
- Manual application reconciliation dashboards group post-session verification
  outcomes into the shortest next human actions while remaining read-only.
- Manual application next-session manual execution start handoff packet
  coverage audits verify that the start handoff packet covers the final start
  authorization coverage audit seal with status, first step, candidate order,
  verification, rollback, post-completion review, target candidates, read-only
  boundary, blocked reasons, and zero applied/formal-evidence deltas.
- Manual application next-session manual execution start handoff packet
  coverage audit seals freeze that ready audit into read-only planning
  metadata with seal status, coverage checks, boundary checks, target
  candidates, blocked reasons, and zero applied/formal-evidence deltas.
- Manual application next-session manual execution start packets compress the
  ready coverage audit seal into operator-facing read-only start metadata with
  start checks, verification, rollback, target candidates, blocked reasons,
  and zero applied/formal-evidence deltas.
- Manual application next-session manual execution start packet coverage
  audits verify that the start packet covers the start handoff packet coverage
  audit seal with status, source audit status, coverage checks, missing
  coverage, boundary checks, operator start checklist, target candidates,
  blocked reasons, and zero applied/formal-evidence deltas.
- Manual application next-session manual execution start packet coverage audit
  seals freeze that ready audit into read-only planning metadata with seal
  status, audit status, start packet status, source audit status, seal checks,
  coverage checks, source coverage checks, boundary confirmation, target
  candidates, blocked reasons, and zero applied/formal-evidence deltas.
- Manual application closure packets separate verified session items that can
  close from carry-forward items for the next manual session.
- Manual application next-session starters turn carry-forward items into
  lane-specific kickoff checklists while remaining read-only.
- Manual application next-session packets compress starter lanes into a
  ready-first execution packet with correction and follow-up queues, kickoff
  checklist, post-session verification checklist, and recommended processing
  order while remaining read-only.
- Manual application next-session audit summaries verify closure-to-starter,
  starter-to-packet, queue, kickoff, and post-session verification coverage
  while preserving the same read-only boundary.
- Manual application next-session operator checklists turn the audit summary's
  shortest next actions into copyable human execution items with target
  candidates, ready criteria, operator checklist, and verification checklist
  while preserving the same read-only boundary.
- Manual application next-session execution handoffs condense the operator
  checklist into a one-page handoff with first action, ready and blocked
  conditions, target candidates, action sequence, verification chain, and
  recommended processing order while preserving the same read-only boundary.
- Manual application next-session completion criteria turn the execution
  handoff into done, blocked, and retry conditions with verification
  entrypoints, target candidates, first action, and recommended processing
  order while preserving the same read-only boundary.
- Manual application next-session retry planners expand retry conditions into
  failure entrypoints, retry sequence, target candidates, verification
  entrypoints, return-to-handoff path, first action, and recommended processing
  order while preserving the same read-only boundary.
- Manual application next-session final readiness summaries combine completion
  criteria and retry planners into a start-gate, first-action,
  ready/blocked/retry, failure-entrypoint, verification-entrypoint,
  return-to-handoff, target-candidate, and recommended-order confirmation sheet
  while preserving the same read-only boundary.
- Manual application next-session manual execution launch notes condense the
  final readiness summary into a one-page launch sheet with launch status,
  start gate, first command, candidate order, abort conditions, return paths,
  verification commands, target candidates, and read-only boundary checks.
- Manual application next-session manual execution launch audits compare the
  final readiness summary and launch note, reporting coverage checks, missing
  coverage, boundary checks, candidate order, return paths, verification
  commands, and target candidates while preserving the same read-only boundary.
- Manual application next-session manual execution launch seals freeze a
  ready launch audit into a final read-only seal with seal status, audit
  status, launch status, start gate, sealed first command, sealed candidate
  order, blocked reasons, seal checks, verification commands, rollback
  entrypoints, and target candidates.
- Manual application next-session manual execution launch runbooks expand the
  launch seal into a read-only execution runbook with runbook status, first
  step, execution order, step verification, failure rollback, post-completion
  review, target candidates, and boundary checks.
- Manual application next-session manual execution launch runbook audits
  compare the launch seal and runbook, reporting coverage checks, missing
  coverage, audit status, candidate order, verification commands, failure
  rollback, post-completion review, target candidates, and read-only boundary
  checks.
- Manual application next-session manual execution launch runbook audit seals
  freeze a ready runbook audit into a final read-only seal with seal status,
  audit status, runbook status, blocked reasons, seal checks, verification
  commands, rollback entrypoints, post-completion review, and target
  candidates.
- Manual application next-session manual execution final launch packets
  compress the audit seal into a read-only launch packet with launch packet
  status, sealed first step, candidate order, operator start checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, and boundary confirmation.
- Manual application next-session manual execution final launch packet
  handoff audits verify that the final launch packet preserves audit seal
  status, sealed first step, candidate order, verification commands,
  rollback path, post-completion review, target candidates, and boundary
  confirmation before the operator starts.
- Manual application next-session manual execution final launch packet
  handoff audit seals freeze the handoff audit into a read-only operator
  go/no-go seal with seal status, handoff readiness, go/no-go decision,
  sealed first step, sealed candidate order, operator-safe start boundary,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, and boundary confirmation.
- Manual application next-session manual execution operator go/no-go seal
  launch receipts compress the operator go/no-go seal into a read-only
  pre-execution receipt with receipt status, receipt decision, signed first
  step, signed candidate order, operator receipt checklist, pre-execution
  confirmation, verification checklist, rollback path, post-completion
  review, target candidates, blocked reasons, and boundary confirmation.
- Manual application next-session manual execution launch receipt final
  boundary audits verify receipt coverage of the operator go/no-go seal with
  final boundary readiness, receipt coverage checks, missing coverage, final
  boundary confirmation, pre-execution confirmation, signed candidate order,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, and read-only boundary notes.
- Manual application next-session manual execution launch receipt final
  boundary audit seals freeze the final boundary audit into a read-only seal
  with seal status, final boundary readiness, receipt status, go/no-go
  decision, receipt decision, sealed first step, sealed candidate order,
  receipt coverage checks, missing coverage, final boundary confirmation,
  pre-execution confirmation, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, and boundary
  confirmation.
- Manual application next-session manual execution launch receipt final
  boundary audit seal operator start packets convert the boundary seal into a
  final read-only operator start sheet with packet status, start
  authorization, sealed first step, sealed candidate order, operator start
  checklist, pre-execution confirmation, verification checklist, rollback
  path, post-completion review, target candidates, blocked reasons, and
  boundary confirmation.
- Manual application next-session manual execution operator start packet
  audits verify that the operator start packet preserves the boundary seal's
  start authorization, sealed first step, sealed candidate order, operator
  start checklist, verification checklist, rollback path, post-completion
  review, target candidates, blocked reasons, and boundary confirmation.
- Manual application next-session manual execution operator start packet
  audit seals freeze a ready operator start packet audit into a read-only seal
  with seal status, audit status, packet status, blocked reasons, seal checks,
  coverage checks, boundary checks, sealed first step, sealed candidate order,
  verification checklist, rollback path, post-completion review, target
  candidates, and boundary confirmation.
- Manual application next-session manual execution start authorization
  receipts compress the audit seal into a final read-only receipt with receipt
  status, seal status, audit status, packet status, start authorization,
  sealed first step, sealed candidate order, operator start checklist,
  verification checklist, rollback path, post-completion review, target
  candidates, blocked reasons, receipt checks, and boundary confirmation.
- Manual application next-session manual execution start clearance packet final
  start authorization coverage audit seals freeze the final start authorization
  coverage audit into a read-only audit seal with seal status, audit status,
  authorization status, packet status, seal source status, packet source status,
  go/no-go start decision, start authorization, seal checks, authorization
  coverage checks, coverage seal checks, packet coverage checks, missing
  coverage, boundary checks, verification checklist, rollback path,
  post-completion review, target candidates, blocked reasons, boundary
  confirmation, and zero applied/formal-evidence deltas.
- Manual application next-session manual execution start handoff packets
  compress the final start authorization coverage audit seal into a read-only
  operator-facing start handoff with handoff packet status, handoff status,
  seal status, audit status, authorization status, source statuses, go/no-go
  start decision, start authorization, handoff checks, operator start
  checklist, verification checklist, rollback path, post-completion review,
  target candidates, blocked reasons, boundary confirmation, and zero
  applied/formal-evidence deltas.
- High-risk candidates include uncertainty and limitation notes.
- Rejected and blocked candidates preserve reasons.
- Approved candidates have reviewer, review date, rationale, source quality, confidence, and approval limitations.
- Promotion batches include only approved candidates.
- Formal report generation ignores unapproved candidates.

## Done Criteria

- Intake data validates deterministically without network access.
- Progress summary separates material coverage, candidate status, approval readiness, risk distribution, rule families, conflicts, and gaps.
- No unapproved candidate can be loaded as report-usable evidence.
- Full test suite passes.
