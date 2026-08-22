"""Deterministic source-intake loading and validation for candidate evidence."""

from collections import Counter
from contextvars import ContextVar
import json
import functools
from pathlib import Path
from typing import Any

from mingli_engine.classical_sources import (
    derive_curation_gaps,
    load_classical_sources,
    load_evidence_units,
    load_source_conflicts,
)
from mingli_engine.models import (
    CANDIDATE_EXTRACT_STATUSES,
    CandidateExtract,
    CandidateReviewActionQueueItem,
    CandidateReviewApplicationAuditSummary,
    CandidateReviewApplicationGuardResult,
    CandidateReviewApplicationPacket,
    CandidateReviewDecisionPacket,
    CandidateReviewDraftValidationResult,
    CandidateReviewInputTemplate,
    CandidateReviewManualApplicationClosureItem,
    CandidateReviewManualApplicationClosurePacket,
    CandidateReviewManualActionDashboard,
    CandidateReviewManualApplicationDryRunGuide,
    CandidateReviewManualApplicationDryRunStep,
    CandidateReviewManualApplicationHandoffItem,
    CandidateReviewManualApplicationHandoffSummary,
    CandidateReviewManualApplicationNextSessionStarter,
    CandidateReviewManualApplicationNextSessionStarterItem,
    CandidateReviewManualApplicationNextSessionPacket,
    CandidateReviewManualApplicationNextSessionPacketItem,
    CandidateReviewManualApplicationNextSessionAuditSummary,
    CandidateReviewManualApplicationNextSessionOperatorChecklist,
    CandidateReviewManualApplicationNextSessionOperatorChecklistItem,
    CandidateReviewManualApplicationNextSessionExecutionHandoff,
    CandidateReviewManualApplicationNextSessionCompletionCriteria,
    CandidateReviewManualApplicationNextSessionRetryPlanner,
    CandidateReviewManualApplicationNextSessionFinalReadinessSummary,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchNote,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbook,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacket,
    CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionOperatorGoNoGoSealLaunchReceipt,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacket,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceipt,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacket,
    CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSealStartDocket,
    CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSealFinalStartPacket,
    CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSealStartAuthorizationPacket,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacket,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorization,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacket,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSeal,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacket,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAudit,
    CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAuditSeal,
    CandidateReviewManualApplicationPostSessionVerificationItem,
    CandidateReviewManualApplicationPostSessionVerificationReport,
    CandidateReviewManualApplicationPreflightCheck,
    CandidateReviewManualApplicationPreflightReport,
    CandidateReviewManualApplicationReconciliationDashboard,
    CandidateReviewManualApplicationReconciliationItem,
    CandidateReviewManualApplicationReadinessLedger,
    CandidateReviewManualApplicationReadinessLedgerRow,
    CandidateReviewManualApplicationSessionAction,
    CandidateReviewManualApplicationSessionOutcomeItem,
    CandidateReviewManualApplicationSessionOutcomePreview,
    CandidateReviewManualApplicationSessionPacket,
    CandidateReviewPacketSummary,
    CandidateReviewWorkItem,
    CONFIDENCE_LEVELS,
    IntakeProgressReport,
    MATERIAL_PREPARATION_STATUSES,
    MATERIAL_TRACKING_STATUSES,
    MATERIAL_TYPES,
    PROMOTION_BATCH_REVIEW_STATUSES,
    PromotionBatch,
    RISK_TIERS,
    RULE_FAMILIES,
    REVIEW_DECISIONS,
    ReviewDecision,
    SOURCE_QUALITIES,
    SourceMaterial,
)


class SourceIntakeError(ValueError):
    pass


_DATA_DIR = Path(__file__).resolve().parent / "data" / "source_intake"
EXTRACTED_MEANING_LIMIT = 280
SHORT_QUOTE_LIMIT = 80
DURABLE_REASON_MIN_LENGTH = 20
NON_DURABLE_REASON_MARKERS = frozenset(
    {"n/a", "na", "none", "todo", "tbd", "待查", "待补", "未知"}
)
ABSOLUTE_OUTCOME_PHRASES = (
    "必定",
    "注定",
    "一定会",
    "死定",
)


REVIEW_DECISION_OPTIONS = ["approved", "returned", "rejected", "blocked"]
REVIEW_DECISION_REQUIRED_INPUTS = [
    "reviewer",
    "reviewed_at",
    "rationale",
    "source_quality",
    "confidence",
    "review_outcome",
    "approval_limitations_if_approved",
    "required_changes_if_returned",
    "rejection_reason_if_rejected_or_blocked",
]
REVIEW_INPUT_TEMPLATE_BASE_FIELDS = [
    "reviewer",
    "reviewed_at",
    "source_locator",
    "source_quality",
    "confidence",
    "review_outcome",
    "rationale",
]
REVIEW_INPUT_TEMPLATE_OUTCOME_FIELDS = {
    "approved": ["approval_limitations"],
    "returned": ["required_changes"],
    "rejected": ["rejection_reason"],
    "blocked": ["rejection_reason"],
}
REVIEW_INPUT_TEMPLATE_CONDITIONAL_FIELDS = frozenset(
    {
        "source_page_or_section_locator",
        "uncertainty_and_limitation_language",
        "duplicate_or_reuse_resolution",
        "conflict_context_resolution",
        "gap_context_resolution",
    }
)
REVIEW_INPUT_TEMPLATE_BOUNDARY_NOTES = [
    "Input templates are not review decisions.",
    "Input templates do not write review_decisions.json or formal evidence.",
]
REVIEW_DRAFT_VALIDATION_BOUNDARY_NOTES = [
    "Draft validation does not write review_decisions.json.",
    "Draft validation does not update candidates, promotion batches, or formal evidence.",
]
REVIEW_APPLICATION_GUARD_BOUNDARY_NOTES = [
    "Application guard previews manual changes only.",
    "Application guard does not write review_decisions.json or candidate_extracts.json.",
    "Application guard does not promote or alter formal evidence.",
]
REVIEW_APPLICATION_PACKET_BOUNDARY_NOTES = [
    "Application packets are export-only manual instructions.",
    "Application packets do not write review_decisions.json or candidate_extracts.json.",
    "Application packets do not promote or alter formal evidence.",
]
REVIEW_APPLICATION_PACKET_CHECKLIST = [
    "append_review_decision_entry",
    "update_candidate_status",
    "run_source_intake_tests",
    "verify_formal_evidence_delta_zero",
]
REVIEW_APPLICATION_AUDIT_BOUNDARY_NOTES = [
    "Audit summary is read-only planning metadata.",
    "Audit summary does not write review_decisions.json or candidate_extracts.json.",
    "Audit summary does not promote or alter formal evidence.",
]
REVIEW_MANUAL_ACTION_DASHBOARD_ACTION_SEQUENCE = [
    "apply_manual_application_packet",
    "resolve_draft_blocking_issues",
    "fill_review_input_template",
]
REVIEW_MANUAL_ACTION_DASHBOARD_BOUNDARY_NOTES = [
    "Manual action dashboard is read-only planning metadata.",
    "Manual action dashboard does not write review_decisions.json or candidate_extracts.json.",
    "Manual action dashboard does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_DRY_RUN_BOUNDARY_NOTES = [
    "Manual application dry-run guide is read-only planning metadata.",
    "Manual application dry-run guide does not write review_decisions.json or candidate_extracts.json.",
    "Manual application dry-run guide does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_PREFLIGHT_BOUNDARY_NOTES = [
    "Manual application preflight report is read-only planning metadata.",
    "Manual application preflight report does not write review_decisions.json or candidate_extracts.json.",
    "Manual application preflight report does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_HANDOFF_BOUNDARY_NOTES = [
    "Manual application handoff summary is read-only planning metadata.",
    "Manual application handoff summary does not write review_decisions.json or candidate_extracts.json.",
    "Manual application handoff summary does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_READINESS_LEDGER_BOUNDARY_NOTES = [
    "Readiness ledger is read-only planning metadata.",
    "Readiness ledger does not write review_decisions.json or candidate_extracts.json.",
    "Readiness ledger does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_SESSION_PACKET_BOUNDARY_NOTES = [
    "Manual application session packet is read-only planning metadata.",
    "Manual application session packet does not write review_decisions.json or candidate_extracts.json.",
    "Manual application session packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_SESSION_POST_VERIFICATION = [
    "run_source_intake_tests",
    "verify_formal_evidence_delta_zero",
    "rerun_readiness_ledger",
    "confirm_manual_changes_only",
]
REVIEW_MANUAL_APPLICATION_SESSION_OUTCOME_BOUNDARY_NOTES = [
    "Session outcome preview is read-only planning metadata.",
    "Session outcome preview does not write review_decisions.json or candidate_extracts.json.",
    "Session outcome preview does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_SESSION_OUTCOME_NEXT_ACTIONS = [
    "rerun_source_intake_tests",
    "rerun_readiness_ledger",
    "resolve_blocked_follow_ups",
    "fill_missing_draft_templates",
]
REVIEW_MANUAL_APPLICATION_POST_SESSION_VERIFICATION_BOUNDARY_NOTES = [
    "Post-session verification report is read-only planning metadata.",
    "Post-session verification report does not write review_decisions.json or candidate_extracts.json.",
    "Post-session verification report does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_RECONCILIATION_BOUNDARY_NOTES = [
    "Reconciliation dashboard is read-only planning metadata.",
    "Reconciliation dashboard does not write review_decisions.json or candidate_extracts.json.",
    "Reconciliation dashboard does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_RECONCILIATION_ACTION_SEQUENCE = [
    "append_missing_review_decision",
    "correct_candidate_status",
    "investigate_follow_up_mismatch",
    "continue_follow_up_processing",
    "verified_complete",
]
REVIEW_MANUAL_APPLICATION_CLOSURE_BOUNDARY_NOTES = [
    "Closure packet is read-only planning metadata.",
    "Closure packet does not write review_decisions.json or candidate_extracts.json.",
    "Closure packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_CLOSURE_ACTION_SEQUENCE = [
    "carry_forward_missing_review_decision",
    "carry_forward_candidate_status_correction",
    "carry_forward_follow_up_investigation",
    "carry_forward_follow_up_processing",
    "close_verified_candidate_session_item",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_BOUNDARY_NOTES = [
    "Next-session starter is read-only planning metadata.",
    "Next-session starter does not write review_decisions.json or candidate_extracts.json.",
    "Next-session starter does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LANES = [
    "missing_review_decision",
    "candidate_status_correction",
    "follow_up_mismatch_investigation",
    "follow_up_processing",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_PACKET_BOUNDARY_NOTES = [
    "Next-session packet is read-only planning metadata.",
    "Next-session packet does not write review_decisions.json or candidate_extracts.json.",
    "Next-session packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_PACKET_POST_SESSION_VERIFICATION = [
    "rerun_post_session_verification",
    "rerun_reconciliation_dashboard",
    "rerun_closure_packet",
    "rerun_next_session_starter",
    "rerun_next_session_packet",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_PACKET_CORRECTION_LANES = [
    "missing_review_decision",
    "candidate_status_correction",
    "follow_up_mismatch_investigation",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_AUDIT_BOUNDARY_NOTES = [
    "Next-session audit summary is read-only planning metadata.",
    "Next-session audit summary does not write review_decisions.json or candidate_extracts.json.",
    "Next-session audit summary does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_OPERATOR_BOUNDARY_NOTES = [
    "Next-session operator checklist is read-only planning metadata.",
    "Next-session operator checklist does not write review_decisions.json or candidate_extracts.json.",
    "Next-session operator checklist does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_EXECUTION_BOUNDARY_NOTES = [
    "Next-session execution handoff is read-only planning metadata.",
    "Next-session execution handoff does not write review_decisions.json or candidate_extracts.json.",
    "Next-session execution handoff does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_COMPLETION_BOUNDARY_NOTES = [
    "Next-session completion criteria is read-only planning metadata.",
    "Next-session completion criteria does not write review_decisions.json or candidate_extracts.json.",
    "Next-session completion criteria does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_RETRY_BOUNDARY_NOTES = [
    "Next-session retry planner is read-only planning metadata.",
    "Next-session retry planner does not write review_decisions.json or candidate_extracts.json.",
    "Next-session retry planner does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_FINAL_READINESS_BOUNDARY_NOTES = [
    "Next-session final readiness summary is read-only planning metadata.",
    "Next-session final readiness summary does not write review_decisions.json or candidate_extracts.json.",
    "Next-session final readiness summary does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_NOTE_BOUNDARY_NOTES = [
    "Next-session manual execution launch note is read-only planning metadata.",
    "Next-session manual execution launch note does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution launch note does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution launch audit is read-only planning metadata.",
    "Next-session manual execution launch audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution launch audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution launch seal is read-only planning metadata.",
    "Next-session manual execution launch seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution launch seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RUNBOOK_BOUNDARY_NOTES = [
    "Next-session manual execution launch runbook is read-only planning metadata.",
    "Next-session manual execution launch runbook does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution launch runbook does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RUNBOOK_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution launch runbook audit is read-only planning metadata.",
    "Next-session manual execution launch runbook audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution launch runbook audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RUNBOOK_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution launch runbook audit seal is read-only planning metadata.",
    "Next-session manual execution launch runbook audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution launch runbook audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_FINAL_LAUNCH_PACKET_BOUNDARY_NOTES = [
    "Next-session manual execution final launch packet is read-only planning metadata.",
    "Next-session manual execution final launch packet does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution final launch packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_FINAL_LAUNCH_PACKET_HANDOFF_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution final launch packet handoff audit is read-only planning metadata.",
    "Next-session manual execution final launch packet handoff audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution final launch packet handoff audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_FINAL_LAUNCH_PACKET_HANDOFF_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution final launch packet handoff audit seal is read-only planning metadata.",
    "Next-session manual execution final launch packet handoff audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution final launch packet handoff audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_OPERATOR_GO_NO_GO_SEAL_LAUNCH_RECEIPT_BOUNDARY_NOTES = [
    "Next-session manual execution operator go/no-go seal launch receipt is read-only planning metadata.",
    "Next-session manual execution operator go/no-go seal launch receipt does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution operator go/no-go seal launch receipt does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RECEIPT_FINAL_BOUNDARY_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution launch receipt final boundary audit is read-only planning metadata.",
    "Next-session manual execution launch receipt final boundary audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution launch receipt final boundary audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RECEIPT_FINAL_BOUNDARY_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution launch receipt final boundary audit seal is read-only planning metadata.",
    "Next-session manual execution launch receipt final boundary audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution launch receipt final boundary audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RECEIPT_FINAL_BOUNDARY_AUDIT_SEAL_OPERATOR_START_PACKET_BOUNDARY_NOTES = [
    "Next-session manual execution operator start packet is read-only planning metadata.",
    "Next-session manual execution operator start packet does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution operator start packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_OPERATOR_START_PACKET_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution operator start packet audit is read-only planning metadata.",
    "Next-session manual execution operator start packet audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution operator start packet audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_OPERATOR_START_PACKET_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution operator start packet audit seal is read-only planning metadata.",
    "Next-session manual execution operator start packet audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution operator start packet audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_START_AUTHORIZATION_RECEIPT_BOUNDARY_NOTES = [
    "Next-session manual execution start authorization receipt is read-only planning metadata.",
    "Next-session manual execution start authorization receipt does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start authorization receipt does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_START_AUTHORIZATION_RECEIPT_COVERAGE_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution start authorization receipt coverage audit is read-only planning metadata.",
    "Next-session manual execution start authorization receipt coverage audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start authorization receipt coverage audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_START_AUTHORIZATION_RECEIPT_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution start authorization receipt coverage audit seal is read-only planning metadata.",
    "Next-session manual execution start authorization receipt coverage audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start authorization receipt coverage audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_AUTHORIZATION_PACKET_BOUNDARY_NOTES = [
    "Next-session manual execution authorization packet is read-only planning metadata.",
    "Next-session manual execution authorization packet does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution authorization packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_AUTHORIZATION_PACKET_COVERAGE_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution authorization packet coverage audit is read-only planning metadata.",
    "Next-session manual execution authorization packet coverage audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution authorization packet coverage audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_AUTHORIZATION_PACKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution authorization packet coverage audit seal is read-only planning metadata.",
    "Next-session manual execution authorization packet coverage audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution authorization packet coverage audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_DOCKET_BOUNDARY_NOTES = [
    "Next-session manual execution start docket is read-only planning metadata.",
    "Next-session manual execution start docket does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start docket does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_DOCKET_COVERAGE_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution start docket coverage audit is read-only planning metadata.",
    "Next-session manual execution start docket coverage audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start docket coverage audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_DOCKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution start docket coverage audit seal is read-only planning metadata.",
    "Next-session manual execution start docket coverage audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start docket coverage audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_FINAL_START_PACKET_BOUNDARY_NOTES = [
    "Next-session manual execution final start packet is read-only planning metadata.",
    "Next-session manual execution final start packet does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution final start packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_FINAL_START_PACKET_HANDOFF_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution final start packet handoff audit is read-only planning metadata.",
    "Next-session manual execution final start packet handoff audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution final start packet handoff audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_FINAL_START_PACKET_HANDOFF_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution final start packet handoff audit seal is read-only planning metadata.",
    "Next-session manual execution final start packet handoff audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution final start packet handoff audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_AUTHORIZATION_PACKET_BOUNDARY_NOTES = [
    "Next-session manual execution start authorization packet is read-only planning metadata.",
    "Next-session manual execution start authorization packet does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start authorization packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_AUTHORIZATION_PACKET_COVERAGE_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution start authorization packet coverage audit is read-only planning metadata.",
    "Next-session manual execution start authorization packet coverage audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start authorization packet coverage audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_AUTHORIZATION_PACKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution start authorization packet coverage audit seal is read-only planning metadata.",
    "Next-session manual execution start authorization packet coverage audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start authorization packet coverage audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_BOUNDARY_NOTES = [
    "Next-session manual execution start clearance packet is read-only planning metadata.",
    "Next-session manual execution start clearance packet does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start clearance packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_COVERAGE_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution start clearance packet coverage audit is read-only planning metadata.",
    "Next-session manual execution start clearance packet coverage audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start clearance packet coverage audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution start clearance packet coverage audit seal is read-only planning metadata.",
    "Next-session manual execution start clearance packet coverage audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start clearance packet coverage audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_FINAL_START_AUTHORIZATION_BOUNDARY_NOTES = [
    "Next-session manual execution start clearance packet final start authorization is read-only planning metadata.",
    "Next-session manual execution start clearance packet final start authorization does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start clearance packet final start authorization does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_FINAL_START_AUTHORIZATION_COVERAGE_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution start clearance packet final start authorization coverage audit is read-only planning metadata.",
    "Next-session manual execution start clearance packet final start authorization coverage audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start clearance packet final start authorization coverage audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_FINAL_START_AUTHORIZATION_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution start clearance packet final start authorization coverage audit seal is read-only planning metadata.",
    "Next-session manual execution start clearance packet final start authorization coverage audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start clearance packet final start authorization coverage audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_HANDOFF_PACKET_BOUNDARY_NOTES = [
    "Next-session manual execution start handoff packet is read-only planning metadata.",
    "Next-session manual execution start handoff packet does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start handoff packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_HANDOFF_PACKET_COVERAGE_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution start handoff packet coverage audit is read-only planning metadata.",
    "Next-session manual execution start handoff packet coverage audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start handoff packet coverage audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_HANDOFF_PACKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution start handoff packet coverage audit seal is read-only planning metadata.",
    "Next-session manual execution start handoff packet coverage audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start handoff packet coverage audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_PACKET_BOUNDARY_NOTES = [
    "Next-session manual execution start packet is read-only planning metadata.",
    "Next-session manual execution start packet does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start packet does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_PACKET_COVERAGE_AUDIT_BOUNDARY_NOTES = [
    "Next-session manual execution start packet coverage audit is read-only planning metadata.",
    "Next-session manual execution start packet coverage audit does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start packet coverage audit does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_PACKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES = [
    "Next-session manual execution start packet coverage audit seal is read-only planning metadata.",
    "Next-session manual execution start packet coverage audit seal does not write review_decisions.json or candidate_extracts.json.",
    "Next-session manual execution start packet coverage audit seal does not promote or alter formal evidence.",
]
REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_NOTE_VERIFICATION_COMMANDS = [
    "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
    "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
    "uv run --with pytest python -m pytest",
]


def _data_dir(data_dir: Path | str | None) -> Path:
    return Path(data_dir) if data_dir is not None else _DATA_DIR


_SOURCE_INTAKE_CALL_CACHE: ContextVar[
    dict[tuple[Any, ...], tuple[Any, ...]] | None
] = ContextVar("source_intake_call_cache", default=None)


def _source_intake_call_cache_key(
    cache_name: str,
    data_dir: Path | str | None,
    *parts: Any,
) -> tuple[Any, ...]:
    return (cache_name, str(_data_dir(data_dir)), *parts)


_SOURCE_INTAKE_FALLBACK_CACHE: dict[tuple[Any, ...], tuple[Any, ...]] = {}


def _source_intake_call_cache_get(
    key: tuple[Any, ...],
) -> tuple[Any, ...] | None:
    cache = _SOURCE_INTAKE_CALL_CACHE.get()
    if cache is not None:
        return cache.get(key)
    return _SOURCE_INTAKE_FALLBACK_CACHE.get(key)


def _source_intake_call_cache_store(
    key: tuple[Any, ...],
    values: list[Any],
) -> None:
    cache = _SOURCE_INTAKE_CALL_CACHE.get()
    if cache is not None:
        cache[key] = tuple(values)
    else:
        _SOURCE_INTAKE_FALLBACK_CACHE[key] = tuple(values)


def _source_intake_file_signature(path: Path) -> tuple[Any, ...] | None:
    try:
        stat = path.stat()
    except OSError:
        return None
    return (stat.st_mtime_ns, stat.st_size)


def _source_intake_drafts_cache_key(
    cache_name: str,
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None,
) -> tuple[Any, ...]:
    return (cache_name, str(_data_dir(data_dir)), json.dumps(drafts, sort_keys=True, ensure_ascii=False))


def _cache_drafts_builder(func):
    cache_name = func.__name__

    @functools.wraps(func)
    def wrapper(drafts, data_dir=None, **kwargs):
        if kwargs:
            return func(drafts, data_dir, **kwargs)
        resolved_dir = _data_dir(data_dir)
        key = _source_intake_drafts_cache_key(cache_name, drafts, resolved_dir) + (
            _source_intake_file_signature(resolved_dir / "candidate_extracts.json"),
            _source_intake_file_signature(resolved_dir / "source_materials.json"),
        )
        cached = _source_intake_call_cache_get(key)
        if cached is not None:
            return cached[0]
        result = func(drafts, data_dir)
        _source_intake_call_cache_store(key, [result])
        return result

    return wrapper


def _start_source_intake_call_cache():
    if _SOURCE_INTAKE_CALL_CACHE.get() is not None:
        return None
    return _SOURCE_INTAKE_CALL_CACHE.set({})


def _end_source_intake_call_cache(token) -> None:
    if token is not None:
        _SOURCE_INTAKE_CALL_CACHE.reset(token)


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    try:
        raw_payload = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise SourceIntakeError(f"missing data file: {path.name}") from error

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as error:
        raise SourceIntakeError(f"invalid JSON in {path.name}: {error}") from error

    if not isinstance(payload, list):
        raise SourceIntakeError(f"{path.name} must contain a JSON array")
    if not all(isinstance(item, dict) for item in payload):
        raise SourceIntakeError(f"{path.name} entries must be JSON objects")
    return payload


def _read_optional_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return _read_json_list(path)


def _require_text(value: str, field_name: str, entry_id: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SourceIntakeError(f"{entry_id} has empty {field_name}")


def _require_string_list(value: Any, field_name: str, entry_id: str) -> None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise SourceIntakeError(f"{entry_id} has invalid {field_name}")


def _ensure_unique(ids: list[str], id_name: str) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise SourceIntakeError(f"duplicate {id_name}: {item_id}")
        seen.add(item_id)


def _is_durable_reason(value: str) -> bool:
    reason = value.strip()
    if len(reason) < DURABLE_REASON_MIN_LENGTH:
        return False
    return reason.lower() not in NON_DURABLE_REASON_MARKERS


def _known_source_ids() -> set[str]:
    return {source.source_id for source in load_classical_sources()}


def _source_material_from_dict(
    data: dict[str, Any],
    known_source_ids: set[str] | None,
) -> SourceMaterial:
    try:
        material = SourceMaterial(**data)
    except TypeError as error:
        raise SourceIntakeError(f"invalid source material: {error}") from error

    for field_name in (
        "material_id",
        "title",
        "material_type",
        "file_label",
        "tracking_status",
        "preparation_status",
    ):
        _require_text(
            getattr(material, field_name),
            field_name,
            material.material_id or "?",
        )
    if material.material_type not in MATERIAL_TYPES:
        raise SourceIntakeError(
            f"{material.material_id} has invalid material_type: "
            f"{material.material_type}"
        )
    if material.tracking_status not in MATERIAL_TRACKING_STATUSES:
        raise SourceIntakeError(
            f"{material.material_id} has invalid tracking_status: "
            f"{material.tracking_status}"
        )
    if material.preparation_status not in MATERIAL_PREPARATION_STATUSES:
        raise SourceIntakeError(
            f"{material.material_id} has invalid preparation_status: "
            f"{material.preparation_status}"
        )
    if material.preparation_status == "blocked" and not material.gap_reason.strip():
        raise SourceIntakeError(
            f"{material.material_id} blocked material requires gap_reason"
        )
    if (
        material.related_source_id
        and known_source_ids is not None
        and material.related_source_id not in known_source_ids
    ):
        raise SourceIntakeError(
            f"{material.material_id} references unknown source: "
            f"{material.related_source_id}"
        )
    return material


def load_source_materials(
    data_dir: Path | str | None = None,
    known_source_ids: set[str] | None = None,
) -> list[SourceMaterial]:
    intake_dir = _data_dir(data_dir)
    known_source_key: tuple[str, ...] | None = (
        None if known_source_ids is None else tuple(sorted(known_source_ids))
    )
    cache_key = _source_intake_call_cache_key(
        "load_source_materials",
        intake_dir,
        known_source_key,
        _source_intake_file_signature(intake_dir / "source_materials.json"),
    )
    cached_materials = _source_intake_call_cache_get(cache_key)
    if cached_materials is not None:
        return list(cached_materials)

    source_ids = _known_source_ids() if known_source_ids is None else known_source_ids
    materials = [
        _source_material_from_dict(item, source_ids)
        for item in _read_json_list(intake_dir / "source_materials.json")
    ]
    _ensure_unique([material.material_id for material in materials], "material_id")
    _source_intake_call_cache_store(cache_key, materials)
    return materials


def _candidate_extract_from_dict(
    data: dict[str, Any],
    material_ids: set[str],
) -> CandidateExtract:
    try:
        candidate = CandidateExtract(**data)
    except TypeError as error:
        raise SourceIntakeError(f"invalid candidate extract: {error}") from error

    for field_name in ("candidate_id", "material_id", "status"):
        _require_text(
            getattr(candidate, field_name),
            field_name,
            candidate.candidate_id or "?",
        )
    if candidate.material_id not in material_ids:
        raise SourceIntakeError(
            f"{candidate.candidate_id} references unknown material: "
            f"{candidate.material_id}"
        )
    if candidate.status not in CANDIDATE_EXTRACT_STATUSES:
        raise SourceIntakeError(
            f"{candidate.candidate_id} has invalid status: {candidate.status}"
        )
    if candidate.proposed_rule_family and candidate.proposed_rule_family not in RULE_FAMILIES:
        raise SourceIntakeError(
            f"{candidate.candidate_id} has unsupported proposed_rule_family: "
            f"{candidate.proposed_rule_family}"
        )
    if candidate.risk_tier and candidate.risk_tier not in RISK_TIERS:
        raise SourceIntakeError(
            f"{candidate.candidate_id} has invalid risk_tier: {candidate.risk_tier}"
        )
    if candidate.status == "pending_review":
        for field_name in (
            "source_locator",
            "extracted_meaning",
            "proposed_rule_family",
            "risk_tier",
        ):
            _require_text(
                getattr(candidate, field_name),
                field_name,
                candidate.candidate_id,
            )
    if len(candidate.extracted_meaning) > EXTRACTED_MEANING_LIMIT:
        raise SourceIntakeError(
            f"{candidate.candidate_id} extracted_meaning is too long"
        )
    if len(candidate.short_quote) > SHORT_QUOTE_LIMIT:
        raise SourceIntakeError(f"{candidate.candidate_id} short_quote is too long")
    candidate_text = " ".join(
        (
            candidate.extracted_meaning,
            candidate.short_quote,
            " ".join(candidate.proposed_limitations),
        )
    )
    if any(phrase in candidate_text for phrase in ABSOLUTE_OUTCOME_PHRASES):
        raise SourceIntakeError(
            f"{candidate.candidate_id} contains prohibited absolute language"
        )
    _require_string_list(
        candidate.proposed_limitations,
        "proposed_limitations",
        candidate.candidate_id,
    )
    _require_string_list(
        candidate.related_evidence_ids,
        "related_evidence_ids",
        candidate.candidate_id,
    )
    _require_string_list(
        candidate.related_conflict_ids,
        "related_conflict_ids",
        candidate.candidate_id,
    )
    _require_string_list(
        candidate.related_gap_ids,
        "related_gap_ids",
        candidate.candidate_id,
    )
    return candidate


def load_candidate_extracts(
    data_dir: Path | str | None = None,
) -> list[CandidateExtract]:
    intake_dir = _data_dir(data_dir)
    cache_key = (
        "load_candidate_extracts",
        str(intake_dir),
        _source_intake_file_signature(intake_dir / "candidate_extracts.json"),
        _source_intake_file_signature(intake_dir / "source_materials.json"),
    )
    cached_candidates = _source_intake_call_cache_get(cache_key)
    if cached_candidates is not None:
        return list(cached_candidates)

    materials = load_source_materials(intake_dir)
    material_ids = {material.material_id for material in materials}
    candidates = [
        _candidate_extract_from_dict(item, material_ids)
        for item in _read_json_list(intake_dir / "candidate_extracts.json")
    ]
    _ensure_unique(
        [candidate.candidate_id for candidate in candidates],
        "candidate_id",
    )
    _source_intake_call_cache_store(cache_key, candidates)
    return candidates


def _review_decision_from_dict(
    data: dict[str, Any],
    candidates_by_id: dict[str, CandidateExtract],
) -> ReviewDecision:
    try:
        decision = ReviewDecision(**data)
    except TypeError as error:
        raise SourceIntakeError(f"invalid review decision: {error}") from error

    for field_name in (
        "decision_id",
        "candidate_id",
        "decision",
        "reviewer",
        "reviewed_at",
        "rationale",
    ):
        _require_text(
            getattr(decision, field_name),
            field_name,
            decision.decision_id or "?",
        )
    if decision.candidate_id not in candidates_by_id:
        raise SourceIntakeError(
            f"{decision.decision_id} references unknown candidate: "
            f"{decision.candidate_id}"
        )
    if decision.decision not in REVIEW_DECISIONS:
        raise SourceIntakeError(
            f"{decision.decision_id} has invalid decision: {decision.decision}"
        )
    if decision.source_quality not in SOURCE_QUALITIES:
        raise SourceIntakeError(
            f"{decision.decision_id} has invalid source_quality: "
            f"{decision.source_quality}"
        )
    if decision.confidence not in CONFIDENCE_LEVELS:
        raise SourceIntakeError(
            f"{decision.decision_id} has invalid confidence: {decision.confidence}"
        )
    _require_string_list(
        decision.required_changes,
        "required_changes",
        decision.decision_id,
    )
    _require_string_list(
        decision.approval_limitations,
        "approval_limitations",
        decision.decision_id,
    )
    if decision.decision == "approved" and not decision.approval_limitations:
        raise SourceIntakeError(
            f"{decision.decision_id} approved decision requires "
            "approval_limitations"
        )
    if decision.decision == "approved":
        candidate = candidates_by_id[decision.candidate_id]
        if decision.source_quality == "needs_recheck":
            raise SourceIntakeError(
                f"{decision.decision_id} cannot approve source_quality "
                "needs_recheck"
            )
        if candidate.risk_tier == "high_risk" and not candidate.proposed_limitations:
            raise SourceIntakeError(
                f"{decision.decision_id} approved high-risk candidate requires "
                "proposed_limitations"
            )
    if decision.decision == "returned" and not decision.required_changes:
        raise SourceIntakeError(
            f"{decision.decision_id} returned decision requires required_changes"
        )
    if decision.decision in {"rejected", "blocked"} and not (
        isinstance(decision.rejection_reason, str)
        and decision.rejection_reason.strip()
    ):
        raise SourceIntakeError(
            f"{decision.decision_id} {decision.decision} decision requires "
            "rejection_reason"
        )
    if decision.decision in {"rejected", "blocked"} and not _is_durable_reason(
        decision.rejection_reason
    ):
        raise SourceIntakeError(
            f"{decision.decision_id} {decision.decision} decision requires a "
            "durable rejection_reason"
        )
    return decision


def _validate_review_status_alignment(
    candidates: list[CandidateExtract],
    decisions: list[ReviewDecision],
) -> None:
    decisions_by_candidate: dict[str, set[str]] = {}
    for decision in decisions:
        decisions_by_candidate.setdefault(decision.candidate_id, set()).add(
            decision.decision
        )

    required_decision_by_status = {
        "approved": "approved",
        "promoted": "approved",
        "returned": "returned",
        "rejected": "rejected",
        "blocked": "blocked",
    }
    for candidate in candidates:
        required_decision = required_decision_by_status.get(candidate.status)
        if required_decision and required_decision not in decisions_by_candidate.get(
            candidate.candidate_id,
            set(),
        ):
            raise SourceIntakeError(
                f"{candidate.candidate_id} status {candidate.status} requires "
                f"{required_decision} review decision"
            )

    candidates_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    allowed_statuses_by_decision = {
        "approved": {"approved", "promoted"},
        "returned": {"returned"},
        "rejected": {"rejected"},
        "blocked": {"blocked"},
    }
    for decision in decisions:
        candidate_status = candidates_by_id[decision.candidate_id].status
        if candidate_status not in allowed_statuses_by_decision[decision.decision]:
            raise SourceIntakeError(
                f"{decision.decision_id} decision {decision.decision} does not "
                f"match candidate status {candidate_status}"
            )


def load_review_decisions(
    data_dir: Path | str | None = None,
) -> list[ReviewDecision]:
    intake_dir = _data_dir(data_dir)
    cache_key = (
        "load_review_decisions",
        str(intake_dir),
        _source_intake_file_signature(intake_dir / "review_decisions.json"),
        _source_intake_file_signature(intake_dir / "candidate_extracts.json"),
    )
    cached_decisions = _source_intake_call_cache_get(cache_key)
    if cached_decisions is not None:
        return list(cached_decisions)

    candidates = load_candidate_extracts(intake_dir)
    candidates_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    decisions = [
        _review_decision_from_dict(item, candidates_by_id)
        for item in _read_json_list(intake_dir / "review_decisions.json")
    ]
    _ensure_unique(
        [decision.decision_id for decision in decisions],
        "decision_id",
    )
    _validate_review_status_alignment(candidates, decisions)
    _source_intake_call_cache_store(cache_key, decisions)
    return decisions


def _promotion_batch_from_dict(
    data: dict[str, Any],
    approved_candidate_ids: set[str],
) -> PromotionBatch:
    try:
        batch = PromotionBatch(**data)
    except TypeError as error:
        raise SourceIntakeError(f"invalid promotion batch: {error}") from error

    for field_name in ("promotion_batch_id", "review_status", "review_notes"):
        _require_text(
            getattr(batch, field_name),
            field_name,
            batch.promotion_batch_id or "?",
        )
    _require_string_list(
        batch.candidate_ids,
        "candidate_ids",
        batch.promotion_batch_id,
    )
    _require_string_list(
        batch.target_evidence_ids,
        "target_evidence_ids",
        batch.promotion_batch_id,
    )
    _require_string_list(
        batch.unresolved_issues,
        "unresolved_issues",
        batch.promotion_batch_id,
    )
    if not batch.candidate_ids:
        raise SourceIntakeError(
            f"{batch.promotion_batch_id} requires candidate_ids"
        )
    if batch.review_status not in PROMOTION_BATCH_REVIEW_STATUSES:
        raise SourceIntakeError(
            f"{batch.promotion_batch_id} has invalid review_status: "
            f"{batch.review_status}"
        )
    _ensure_unique(batch.candidate_ids, "candidate_id")
    _ensure_unique(batch.target_evidence_ids, "target_evidence_id")
    for candidate_id in batch.candidate_ids:
        if candidate_id not in approved_candidate_ids:
            raise SourceIntakeError(
                f"{batch.promotion_batch_id} includes non-approved candidate: "
                f"{candidate_id}"
            )
    if batch.review_status == "blocked":
        if batch.target_evidence_ids:
            raise SourceIntakeError(
                f"{batch.promotion_batch_id} blocked batch cannot target evidence"
            )
        if not batch.unresolved_issues:
            raise SourceIntakeError(
                f"{batch.promotion_batch_id} blocked batch requires unresolved_issues"
            )
    elif not batch.target_evidence_ids:
        raise SourceIntakeError(
            f"{batch.promotion_batch_id} requires target_evidence_ids"
        )
    return batch


def load_promotion_batches(
    data_dir: Path | str | None = None,
) -> list[PromotionBatch]:
    intake_dir = _data_dir(data_dir)
    decisions = load_review_decisions(intake_dir)
    approved_candidate_ids = {
        decision.candidate_id
        for decision in decisions
        if decision.decision == "approved"
    }
    batches = [
        _promotion_batch_from_dict(item, approved_candidate_ids)
        for item in _read_json_list(intake_dir / "promotion_batches.json")
    ]
    _ensure_unique(
        [batch.promotion_batch_id for batch in batches],
        "promotion_batch_id",
    )
    return batches


def list_approved_candidates_for_promotion(
    data_dir: Path | str | None = None,
) -> list[CandidateExtract]:
    intake_dir = _data_dir(data_dir)
    candidates = load_candidate_extracts(intake_dir)
    decisions = load_review_decisions(intake_dir)
    batches = load_promotion_batches(intake_dir)

    approved_candidate_ids = {
        decision.candidate_id
        for decision in decisions
        if decision.decision == "approved"
    }
    batched_candidate_ids = {
        candidate_id
        for batch in batches
        for candidate_id in batch.candidate_ids
    }
    return [
        candidate
        for candidate in candidates
        if candidate.candidate_id in approved_candidate_ids
        and candidate.candidate_id not in batched_candidate_ids
        and candidate.status == "approved"
    ]


def _pending_review_actions(
    candidate: CandidateExtract,
    duplicate_related_ids: set[str],
) -> list[str]:
    actions = [
        "verify_source_locator",
        "review_candidate_meaning",
        "decide_review_outcome",
    ]
    if candidate.source_locator.startswith("learning-reference:"):
        actions.append("replace_learning_reference_locator_with_source_locator")
    if candidate.risk_tier in {"sensitive", "high_risk"}:
        actions.append("confirm_uncertainty_and_limitation_language")
    if (
        candidate.candidate_id in duplicate_related_ids
        or bool(candidate.duplicate_of.strip())
    ):
        actions.append("review_duplicate_or_reuse_context")
    if candidate.related_conflict_ids:
        actions.append("review_conflict_context")
    if candidate.related_gap_ids:
        actions.append("review_gap_context")
    return actions


def _pending_review_boundary_notes(candidate: CandidateExtract) -> list[str]:
    notes = ["Pending review candidates are not formal report evidence."]
    if candidate.source_locator.startswith("learning-reference:"):
        notes.append(
            "Learning-reference locators must be replaced with source page, "
            "section, or review-note anchors before approval."
        )
    if candidate.risk_tier in {"sensitive", "high_risk"}:
        notes.append(
            "Sensitive and high-risk candidates require uncertainty and "
            "limitation language before approval."
        )
    return notes


def list_pending_candidate_review_worklist(
    data_dir: Path | str | None = None,
) -> list[CandidateReviewWorkItem]:
    intake_dir = _data_dir(data_dir)
    candidates = load_candidate_extracts(intake_dir)
    duplicate_related_ids = {
        candidate_id
        for pair in find_duplicate_candidates(intake_dir)
        for candidate_id in pair
    }

    return [
        CandidateReviewWorkItem(
            candidate_id=candidate.candidate_id,
            material_id=candidate.material_id,
            status=candidate.status,
            proposed_rule_family=candidate.proposed_rule_family,
            risk_tier=candidate.risk_tier,
            source_locator=candidate.source_locator,
            required_review_actions=_pending_review_actions(
                candidate,
                duplicate_related_ids,
            ),
            boundary_notes=_pending_review_boundary_notes(candidate),
        )
        for candidate in candidates
        if candidate.status == "pending_review"
    ]


def _decision_packet_required_inputs(
    candidate: CandidateExtract,
    actions: list[str],
) -> list[str]:
    inputs = list(REVIEW_DECISION_REQUIRED_INPUTS)
    if "replace_learning_reference_locator_with_source_locator" in actions:
        inputs.append("source_page_or_section_locator")
    if "confirm_uncertainty_and_limitation_language" in actions:
        inputs.append("uncertainty_and_limitation_language")
    if "review_duplicate_or_reuse_context" in actions:
        inputs.append("duplicate_or_reuse_resolution")
    if candidate.related_conflict_ids:
        inputs.append("conflict_context_resolution")
    if candidate.related_gap_ids:
        inputs.append("gap_context_resolution")
    return inputs


def _decision_packet_approval_blockers(actions: list[str]) -> list[str]:
    blockers = [
        "source_locator_not_verified",
        "candidate_meaning_not_verified",
        "review_outcome_not_selected",
    ]
    if "replace_learning_reference_locator_with_source_locator" in actions:
        blockers.append("learning_reference_locator_not_replaced")
    if "confirm_uncertainty_and_limitation_language" in actions:
        blockers.append("uncertainty_limitations_not_confirmed")
    if "review_duplicate_or_reuse_context" in actions:
        blockers.append("duplicate_or_reuse_resolution_before_approval")
    if "review_conflict_context" in actions:
        blockers.append("conflict_context_not_resolved")
    if "review_gap_context" in actions:
        blockers.append("gap_context_not_resolved")
    return blockers


def _decision_packet_boundary_notes(work_item: CandidateReviewWorkItem) -> list[str]:
    notes = [
        "Review decision packets are not formal report evidence.",
        "Packets do not write review_decisions.json or promotion_batches.json.",
    ]
    notes.extend(work_item.boundary_notes)
    return list(dict.fromkeys(notes))


def list_pending_candidate_review_decision_packets(
    data_dir: Path | str | None = None,
) -> list[CandidateReviewDecisionPacket]:
    intake_dir = _data_dir(data_dir)
    packets_cache_key = _source_intake_call_cache_key(
        "list_pending_candidate_review_decision_packets",
        intake_dir,
        _source_intake_file_signature(intake_dir / "candidate_extracts.json"),
        _source_intake_file_signature(intake_dir / "source_materials.json"),
    )
    cached_packets = _source_intake_call_cache_get(packets_cache_key)
    if cached_packets is not None:
        return [packet for packet in cached_packets]
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in load_candidate_extracts(intake_dir)
    }
    packets: list[CandidateReviewDecisionPacket] = []
    for work_item in list_pending_candidate_review_worklist(intake_dir):
        candidate = candidates_by_id[work_item.candidate_id]
        packets.append(
            CandidateReviewDecisionPacket(
                candidate_id=work_item.candidate_id,
                material_id=work_item.material_id,
                candidate_status=work_item.status,
                decision_options=list(REVIEW_DECISION_OPTIONS),
                required_review_inputs=_decision_packet_required_inputs(
                    candidate,
                    work_item.required_review_actions,
                ),
                approval_blockers=_decision_packet_approval_blockers(
                    work_item.required_review_actions,
                ),
                packet_actions=[
                    *work_item.required_review_actions,
                    "draft_review_decision_after_manual_checks",
                ],
                boundary_notes=_decision_packet_boundary_notes(work_item),
            )
        )
    _source_intake_call_cache_store(packets_cache_key, packets)
    return packets


def build_pending_candidate_review_packet_summary(
    data_dir: Path | str | None = None,
) -> CandidateReviewPacketSummary:
    packets = list_pending_candidate_review_decision_packets(data_dir)
    decision_options: Counter[str] = Counter()
    required_inputs: Counter[str] = Counter()
    approval_blockers: Counter[str] = Counter()
    packet_actions: Counter[str] = Counter()

    for packet in packets:
        decision_options.update(packet.decision_options)
        required_inputs.update(packet.required_review_inputs)
        approval_blockers.update(packet.approval_blockers)
        packet_actions.update(packet.packet_actions)

    return CandidateReviewPacketSummary(
        packet_count=len(packets),
        candidate_ids=[packet.candidate_id for packet in packets],
        decision_option_counts=dict(decision_options),
        required_input_counts=dict(required_inputs),
        approval_blocker_counts=dict(approval_blockers),
        packet_action_counts=dict(packet_actions),
        review_decision_delta=0,
        formal_evidence_delta=0,
    )


def _primary_action_from_packet(
    packet: CandidateReviewDecisionPacket,
) -> tuple[str, str, list[str]]:
    if "duplicate_or_reuse_resolution_before_approval" in packet.approval_blockers:
        return (
            "resolve_duplicate_or_reuse_context",
            (
                "Resolve duplicate or reuse context before any review decision "
                "can be written."
            ),
            ["duplicate_or_reuse_resolution"],
        )
    if "learning_reference_locator_not_replaced" in packet.approval_blockers:
        return (
            "replace_learning_reference_locator",
            (
                "Replace the learning-reference locator with a source page, "
                "section, or review-note anchor before approval can be considered."
            ),
            ["source_page_or_section_locator"],
        )
    if "uncertainty_limitations_not_confirmed" in packet.approval_blockers:
        return (
            "confirm_uncertainty_and_limitation_language",
            (
                "Confirm uncertainty and limitation language before approval can "
                "be considered."
            ),
            ["uncertainty_and_limitation_language"],
        )
    return (
        "select_review_outcome",
        "Select a review outcome after locator and meaning checks are complete.",
        ["review_outcome"],
    )


def build_pending_candidate_review_action_queue(
    data_dir: Path | str | None = None,
) -> list[CandidateReviewActionQueueItem]:
    queue: list[CandidateReviewActionQueueItem] = []
    for packet in list_pending_candidate_review_decision_packets(data_dir):
        primary_action, reason, blocking_inputs = _primary_action_from_packet(packet)
        queue.append(
            CandidateReviewActionQueueItem(
                candidate_id=packet.candidate_id,
                priority="high",
                primary_action=primary_action,
                reason=reason,
                blocking_inputs=blocking_inputs,
                boundary_notes=[
                    "Action queue items are planning metadata only.",
                    "Action queue items do not write review decisions or formal evidence.",
                ],
            )
        )
    return queue


def _format_inline_list(values: list[str]) -> str:
    if not values:
        return "`none`"
    return ", ".join(f"`{value}`" for value in values)


def render_pending_candidate_review_action_queue_markdown(
    data_dir: Path | str | None = None,
) -> str:
    summary = build_pending_candidate_review_packet_summary(data_dir)
    queue = build_pending_candidate_review_action_queue(data_dir)
    lines = [
        "# Pending Candidate Review Action Queue",
        "",
        "## Summary",
        "",
        f"- Queue items: `{len(queue)}`",
        f"- Review packet count: `{summary.packet_count}`",
        f"- Review decision delta: `{summary.review_decision_delta}`",
        f"- Formal evidence delta: `{summary.formal_evidence_delta}`",
        "",
        "## Action Items",
        "",
    ]
    if not queue:
        lines.append("No pending candidate review actions.")
        return "\n".join(lines) + "\n"

    for item in queue:
        lines.extend(
            [
                f"- [ ] Candidate: `{item.candidate_id}`",
                f"  - Priority: `{item.priority}`",
                f"  - Primary action: `{item.primary_action}`",
                f"  - Blocking inputs: {_format_inline_list(item.blocking_inputs)}",
                f"  - Reason: {item.reason}",
                f"  - Boundary: {' '.join(item.boundary_notes)}",
            ]
        )
    return "\n".join(lines) + "\n"


def _decision_id_hint(candidate_id: str) -> str:
    return f"review_{candidate_id}"


def _input_template_conditional_fields(
    packet: CandidateReviewDecisionPacket,
) -> list[str]:
    return [
        input_name
        for input_name in packet.required_review_inputs
        if input_name in REVIEW_INPUT_TEMPLATE_CONDITIONAL_FIELDS
    ]


def list_pending_candidate_review_input_templates(
    data_dir: Path | str | None = None,
) -> list[CandidateReviewInputTemplate]:
    intake_dir = _data_dir(data_dir)
    templates_cache_key = _source_intake_call_cache_key(
        "list_pending_candidate_review_input_templates",
        intake_dir,
        _source_intake_file_signature(intake_dir / "candidate_extracts.json"),
        _source_intake_file_signature(intake_dir / "source_materials.json"),
    )
    cached_templates = _source_intake_call_cache_get(templates_cache_key)
    if cached_templates is not None:
        return [template for template in cached_templates]
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in load_candidate_extracts(intake_dir)
    }

    templates: list[CandidateReviewInputTemplate] = []
    for packet in list_pending_candidate_review_decision_packets(intake_dir):
        candidate = candidates_by_id[packet.candidate_id]
        conditional_fields = _input_template_conditional_fields(packet)
        templates.append(
            CandidateReviewInputTemplate(
                candidate_id=packet.candidate_id,
                material_id=packet.material_id,
                candidate_status=packet.candidate_status,
                decision_id_hint=_decision_id_hint(packet.candidate_id),
                current_source_locator=candidate.source_locator,
                base_fields=list(REVIEW_INPUT_TEMPLATE_BASE_FIELDS),
                outcome_fields={
                    outcome: list(fields)
                    for outcome, fields in REVIEW_INPUT_TEMPLATE_OUTCOME_FIELDS.items()
                },
                conditional_fields=conditional_fields,
                blocking_inputs=list(conditional_fields),
                boundary_notes=list(REVIEW_INPUT_TEMPLATE_BOUNDARY_NOTES),
            )
        )
    _source_intake_call_cache_store(templates_cache_key, templates)
    return templates


def _append_template_fields(lines: list[str], fields: list[str], indent: str) -> None:
    for field_name in fields:
        lines.append(f"{indent}- {field_name}:")


def render_pending_candidate_review_input_templates_markdown(
    data_dir: Path | str | None = None,
) -> str:
    summary = build_pending_candidate_review_packet_summary(data_dir)
    templates = list_pending_candidate_review_input_templates(data_dir)
    lines = [
        "# Pending Candidate Review Input Templates",
        "",
        "## Summary",
        "",
        f"- Template count: `{len(templates)}`",
        f"- Review packet count: `{summary.packet_count}`",
        f"- Review decision delta: `{summary.review_decision_delta}`",
        f"- Formal evidence delta: `{summary.formal_evidence_delta}`",
        "- Boundary: Input templates are not review decisions.",
        "",
        "## Templates",
        "",
    ]
    if not templates:
        lines.append("No pending candidate review input templates.")
        return "\n".join(lines) + "\n"

    for template in templates:
        lines.extend(
            [
                f"- [ ] Candidate: `{template.candidate_id}`",
                f"  - Decision id hint: `{template.decision_id_hint}`",
                f"  - Current source locator: `{template.current_source_locator}`",
                "  - Base fields:",
            ]
        )
        _append_template_fields(lines, template.base_fields, "    ")
        lines.append("  - Outcome fields:")
        for outcome, fields in template.outcome_fields.items():
            lines.append(f"    - {outcome}:")
            _append_template_fields(lines, fields, "      ")
        lines.append("  - Conditional fields:")
        if template.conditional_fields:
            _append_template_fields(lines, template.conditional_fields, "    ")
        else:
            lines.append("    - none")
        lines.append(
            f"  - Blocking inputs: {_format_inline_list(template.blocking_inputs)}"
        )
        lines.append(f"  - Boundary: {' '.join(template.boundary_notes)}")
    return "\n".join(lines) + "\n"


def _draft_text(draft: dict[str, Any], field_name: str) -> str:
    value = draft.get(field_name, "")
    return value.strip() if isinstance(value, str) else ""


def _draft_string_list(draft: dict[str, Any], field_name: str) -> list[str]:
    value = draft.get(field_name, [])
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _missing_text_fields(
    draft: dict[str, Any],
    field_names: list[str],
) -> list[str]:
    return [field_name for field_name in field_names if not _draft_text(draft, field_name)]


def _review_draft_normalized_decision(
    draft: dict[str, Any],
    review_outcome: str,
) -> dict[str, object]:
    return {
        "decision_id": _draft_text(draft, "decision_id"),
        "candidate_id": _draft_text(draft, "candidate_id"),
        "decision": review_outcome,
        "reviewer": _draft_text(draft, "reviewer"),
        "reviewed_at": _draft_text(draft, "reviewed_at"),
        "rationale": _draft_text(draft, "rationale"),
        "required_changes": _draft_string_list(draft, "required_changes"),
        "rejection_reason": _draft_text(draft, "rejection_reason"),
        "approval_limitations": _draft_string_list(draft, "approval_limitations"),
        "source_quality": _draft_text(draft, "source_quality"),
        "confidence": _draft_text(draft, "confidence"),
    }


def validate_pending_candidate_review_decision_draft(
    draft: dict[str, Any],
    data_dir: Path | str | None = None,
) -> CandidateReviewDraftValidationResult:
    templates_by_id = {
        template.candidate_id: template
        for template in list_pending_candidate_review_input_templates(data_dir)
    }
    candidate_id = _draft_text(draft, "candidate_id")
    decision_id = _draft_text(draft, "decision_id")
    review_outcome = _draft_text(draft, "review_outcome")
    missing_fields = _missing_text_fields(
        draft,
        ["decision_id", "candidate_id", *REVIEW_INPUT_TEMPLATE_BASE_FIELDS],
    )
    blocking_issues: list[str] = []

    template = templates_by_id.get(candidate_id)
    if template is None:
        blocking_issues.append("candidate_not_pending_review")

    if review_outcome not in REVIEW_DECISION_OPTIONS:
        blocking_issues.append("invalid_review_outcome")
    if _draft_text(draft, "source_quality") not in SOURCE_QUALITIES:
        blocking_issues.append("invalid_source_quality")
    if _draft_text(draft, "confidence") not in CONFIDENCE_LEVELS:
        blocking_issues.append("invalid_confidence")

    if review_outcome == "approved":
        approval_limitations = _draft_string_list(draft, "approval_limitations")
        if not approval_limitations:
            missing_fields.append("approval_limitations")
            blocking_issues.append("approved_candidate_requires_approval_limitations")
        if template is not None:
            for conditional_field in template.conditional_fields:
                if not _draft_text(draft, conditional_field):
                    missing_fields.append(conditional_field)
                    blocking_issues.append(f"{conditional_field}_required")
            if (
                "source_page_or_section_locator" in template.conditional_fields
                and _draft_text(draft, "source_locator").startswith("learning-reference:")
            ):
                blocking_issues.append(
                    "approved_candidate_source_locator_still_learning_reference"
                )
        if _draft_text(draft, "source_quality") == "needs_recheck":
            blocking_issues.append("approved_candidate_cannot_use_needs_recheck")
    elif review_outcome == "returned":
        if not _draft_string_list(draft, "required_changes"):
            missing_fields.append("required_changes")
            blocking_issues.append("returned_candidate_requires_required_changes")
    elif review_outcome in {"rejected", "blocked"}:
        if not _is_durable_reason(_draft_text(draft, "rejection_reason")):
            missing_fields.append("rejection_reason")
            blocking_issues.append(f"{review_outcome}_candidate_requires_durable_reason")

    missing_fields = list(dict.fromkeys(missing_fields))
    blocking_issues = list(dict.fromkeys(blocking_issues))
    ready = not missing_fields and not blocking_issues
    normalized_decision = (
        _review_draft_normalized_decision(draft, review_outcome) if ready else {}
    )

    return CandidateReviewDraftValidationResult(
        candidate_id=candidate_id,
        decision_id=decision_id,
        review_outcome=review_outcome,
        ready_for_manual_application=ready,
        missing_fields=missing_fields,
        blocking_issues=blocking_issues,
        normalized_review_decision=normalized_decision,
        review_decision_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_DRAFT_VALIDATION_BOUNDARY_NOTES),
    )


def validate_pending_candidate_review_decision_drafts(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> list[CandidateReviewDraftValidationResult]:
    drafts_cache_key = _source_intake_drafts_cache_key(
        "validate_pending_candidate_review_decision_drafts",
        drafts,
        data_dir,
    ) + (
        _source_intake_file_signature(_data_dir(data_dir) / "candidate_extracts.json"),
        _source_intake_file_signature(_data_dir(data_dir) / "source_materials.json"),
    )
    cached_validations = _source_intake_call_cache_get(drafts_cache_key)
    if cached_validations is not None:
        return [validation for validation in cached_validations]
    validations = [
        validate_pending_candidate_review_decision_draft(draft, data_dir)
        for draft in drafts
    ]
    _source_intake_call_cache_store(drafts_cache_key, validations)
    return validations


def render_pending_candidate_review_draft_validation_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    results = validate_pending_candidate_review_decision_drafts(drafts, data_dir)
    ready_count = sum(1 for result in results if result.ready_for_manual_application)
    blocked_count = len(results) - ready_count
    lines = [
        "# Pending Candidate Review Draft Validation",
        "",
        "## Summary",
        "",
        f"- Draft count: `{len(results)}`",
        f"- Ready for manual application: `{ready_count}`",
        f"- Blocked drafts: `{blocked_count}`",
        "- Review decision delta: `0`",
        "- Formal evidence delta: `0`",
        "- Boundary: Draft validation does not write review_decisions.json.",
        "",
        "## Results",
        "",
    ]
    if not results:
        lines.append("No pending candidate review drafts were provided.")
        return "\n".join(lines) + "\n"

    for result in results:
        status = (
            "ready_for_manual_application"
            if result.ready_for_manual_application
            else "blocked"
        )
        lines.extend(
            [
                f"- Candidate: `{result.candidate_id}`",
                f"  - Decision id: `{result.decision_id}`",
                f"  - Review outcome: `{result.review_outcome}`",
                f"  - Status: `{status}`",
                f"  - Missing fields: {_format_inline_list(result.missing_fields)}",
                f"  - Blocking issues: {_format_inline_list(result.blocking_issues)}",
                f"  - Boundary: {' '.join(result.boundary_notes)}",
            ]
        )
    return "\n".join(lines) + "\n"


def _candidate_status_by_id(
    data_dir: Path | str | None = None,
) -> dict[str, str]:
    return {
        candidate.candidate_id: candidate.status
        for candidate in load_candidate_extracts(data_dir)
    }


def build_pending_candidate_review_application_guard(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> list[CandidateReviewApplicationGuardResult]:
    drafts_cache_key = _source_intake_drafts_cache_key(
        "build_pending_candidate_review_application_guard",
        drafts,
        data_dir,
    ) + (
        _source_intake_file_signature(_data_dir(data_dir) / "candidate_extracts.json"),
        _source_intake_file_signature(_data_dir(data_dir) / "source_materials.json"),
    )
    cached_results = _source_intake_call_cache_get(drafts_cache_key)
    if cached_results is not None:
        return [result for result in cached_results]
    candidate_statuses = _candidate_status_by_id(data_dir)
    results: list[CandidateReviewApplicationGuardResult] = []
    for validation in validate_pending_candidate_review_decision_drafts(
        drafts,
        data_dir,
    ):
        current_status = candidate_statuses.get(validation.candidate_id, "")
        if not validation.ready_for_manual_application:
            results.append(
                CandidateReviewApplicationGuardResult(
                    candidate_id=validation.candidate_id,
                    decision_id=validation.decision_id,
                    review_outcome=validation.review_outcome,
                    ready_to_apply=False,
                    current_candidate_status=current_status,
                    validation_missing_fields=list(validation.missing_fields),
                    blocking_issues=list(validation.blocking_issues),
                    boundary_notes=list(REVIEW_APPLICATION_GUARD_BOUNDARY_NOTES),
                )
            )
            continue

        next_status = validation.review_outcome
        status_preview = {
            "candidate_id": validation.candidate_id,
            "from_status": current_status,
            "to_status": next_status,
        }
        results.append(
            CandidateReviewApplicationGuardResult(
                candidate_id=validation.candidate_id,
                decision_id=validation.decision_id,
                review_outcome=validation.review_outcome,
                ready_to_apply=True,
                current_candidate_status=current_status,
                next_candidate_status=next_status,
                review_decision_preview=dict(validation.normalized_review_decision),
                candidate_status_preview=status_preview,
                preview_review_decision_delta=1,
                preview_candidate_status_delta=(
                    1 if current_status != next_status else 0
                ),
                applied_review_decision_delta=0,
                applied_candidate_status_delta=0,
                formal_evidence_delta=0,
                boundary_notes=list(REVIEW_APPLICATION_GUARD_BOUNDARY_NOTES),
            )
        )
    _source_intake_call_cache_store(drafts_cache_key, results)
    return results


def render_pending_candidate_review_application_guard_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    guards = build_pending_candidate_review_application_guard(drafts, data_dir)
    ready_count = sum(1 for guard in guards if guard.ready_to_apply)
    blocked_count = len(guards) - ready_count
    preview_review_decisions = sum(
        guard.preview_review_decision_delta for guard in guards
    )
    preview_status_updates = sum(
        guard.preview_candidate_status_delta for guard in guards
    )
    lines = [
        "# Pending Candidate Review Application Guard",
        "",
        "## Summary",
        "",
        f"- Draft count: `{len(guards)}`",
        f"- Ready previews: `{ready_count}`",
        f"- Blocked previews: `{blocked_count}`",
        f"- Preview review decision additions: `{preview_review_decisions}`",
        f"- Preview candidate status updates: `{preview_status_updates}`",
        "- Applied review decision delta: `0`",
        "- Applied candidate status delta: `0`",
        "- Formal evidence delta: `0`",
        "- Boundary: Application guard previews manual changes only.",
        "",
        "## Previews",
        "",
    ]
    if not guards:
        lines.append("No pending candidate review application previews.")
        return "\n".join(lines) + "\n"

    for guard in guards:
        status = "ready_to_apply" if guard.ready_to_apply else "blocked"
        status_preview = (
            f"`{guard.current_candidate_status}` -> `{guard.next_candidate_status}`"
            if guard.ready_to_apply
            else "`none`"
        )
        lines.extend(
            [
                f"- Candidate: `{guard.candidate_id}`",
                f"  - Decision id: `{guard.decision_id}`",
                f"  - Review outcome: `{guard.review_outcome}`",
                f"  - Status: `{status}`",
                f"  - Candidate status preview: {status_preview}",
                (
                    "  - Review decision preview: "
                    f"`{guard.preview_review_decision_delta}`"
                ),
                (
                    "  - Missing fields: "
                    f"{_format_inline_list(guard.validation_missing_fields)}"
                ),
                f"  - Blocking issues: {_format_inline_list(guard.blocking_issues)}",
                f"  - Boundary: {' '.join(guard.boundary_notes)}",
            ]
        )
    return "\n".join(lines) + "\n"


def _application_packet_rollback_notes(
    status_update: dict[str, str],
) -> list[str]:
    return [
        "Remove the appended review decision entry if manual application is abandoned.",
        (
            "Restore candidate status from "
            f"{status_update.get('to_status', '')} to "
            f"{status_update.get('from_status', '')} if manual application is abandoned."
        ),
    ]


def build_pending_candidate_review_application_packets(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> list[CandidateReviewApplicationPacket]:
    drafts_cache_key = _source_intake_drafts_cache_key(
        "build_pending_candidate_review_application_packets",
        drafts,
        data_dir,
    ) + (
        _source_intake_file_signature(_data_dir(data_dir) / "candidate_extracts.json"),
        _source_intake_file_signature(_data_dir(data_dir) / "source_materials.json"),
    )
    cached_packets = _source_intake_call_cache_get(drafts_cache_key)
    if cached_packets is not None:
        return [packet for packet in cached_packets]
    packets: list[CandidateReviewApplicationPacket] = []
    for guard in build_pending_candidate_review_application_guard(drafts, data_dir):
        if not guard.ready_to_apply:
            packets.append(
                CandidateReviewApplicationPacket(
                    candidate_id=guard.candidate_id,
                    decision_id=guard.decision_id,
                    ready_to_export=False,
                    manual_checklist=["resolve_blocking_issues_before_manual_export"],
                    blocking_issues=list(guard.blocking_issues),
                    boundary_notes=list(REVIEW_APPLICATION_PACKET_BOUNDARY_NOTES),
                )
            )
            continue

        status_update = dict(guard.candidate_status_preview)
        packets.append(
            CandidateReviewApplicationPacket(
                candidate_id=guard.candidate_id,
                decision_id=guard.decision_id,
                ready_to_export=True,
                review_decision_json=dict(guard.review_decision_preview),
                candidate_status_update=status_update,
                manual_checklist=list(REVIEW_APPLICATION_PACKET_CHECKLIST),
                rollback_notes=_application_packet_rollback_notes(status_update),
                preview_review_decision_delta=guard.preview_review_decision_delta,
                preview_candidate_status_delta=guard.preview_candidate_status_delta,
                applied_review_decision_delta=0,
                applied_candidate_status_delta=0,
                formal_evidence_delta=0,
                boundary_notes=list(REVIEW_APPLICATION_PACKET_BOUNDARY_NOTES),
            )
        )
    _source_intake_call_cache_store(drafts_cache_key, packets)
    return packets


def _format_json_block(payload: dict[str, object] | dict[str, str]) -> list[str]:
    return [
        "```json",
        *json.dumps(payload, ensure_ascii=False, indent=2).splitlines(),
        "```",
    ]


def render_pending_candidate_review_application_packets_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    packets = build_pending_candidate_review_application_packets(drafts, data_dir)
    exportable_count = sum(1 for packet in packets if packet.ready_to_export)
    blocked_count = len(packets) - exportable_count
    preview_review_decisions = sum(
        packet.preview_review_decision_delta for packet in packets
    )
    preview_status_updates = sum(
        packet.preview_candidate_status_delta for packet in packets
    )
    lines = [
        "# Pending Candidate Review Application Packets",
        "",
        "## Summary",
        "",
        f"- Packet count: `{len(packets)}`",
        f"- Exportable packets: `{exportable_count}`",
        f"- Blocked packets: `{blocked_count}`",
        f"- Preview review decision additions: `{preview_review_decisions}`",
        f"- Preview candidate status updates: `{preview_status_updates}`",
        "- Applied review decision delta: `0`",
        "- Applied candidate status delta: `0`",
        "- Formal evidence delta: `0`",
        "- Boundary: Application packets are export-only manual instructions.",
        "",
        "## Packets",
        "",
    ]
    if not packets:
        lines.append("No pending candidate review application packets.")
        return "\n".join(lines) + "\n"

    for packet in packets:
        status = "exportable" if packet.ready_to_export else "blocked"
        lines.extend(
            [
                f"- Candidate: `{packet.candidate_id}`",
                f"  - Decision id: `{packet.decision_id}`",
                f"  - Status: `{status}`",
                f"  - Blocking issues: {_format_inline_list(packet.blocking_issues)}",
                "  - Review decision JSON:",
            ]
        )
        if packet.review_decision_json:
            lines.extend(f"    {line}" for line in _format_json_block(packet.review_decision_json))
        else:
            lines.append("    `none`")
        lines.append("  - Candidate status update:")
        if packet.candidate_status_update:
            lines.extend(
                f"    {line}" for line in _format_json_block(packet.candidate_status_update)
            )
        else:
            lines.append("    `none`")
        lines.append("  - Manual checklist:")
        for item in packet.manual_checklist:
            lines.append(f"    - {item}")
        lines.append("  - Rollback notes:")
        if packet.rollback_notes:
            for note in packet.rollback_notes:
                lines.append(f"    - {note}")
        else:
            lines.append("    - none")
        lines.append(f"  - Boundary: {' '.join(packet.boundary_notes)}")
    return "\n".join(lines) + "\n"


def build_pending_candidate_review_application_audit_summary(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> CandidateReviewApplicationAuditSummary:
    drafts_cache_key = _source_intake_drafts_cache_key(
        "build_pending_candidate_review_application_audit_summary",
        drafts,
        data_dir,
    ) + (
        _source_intake_file_signature(_data_dir(data_dir) / "candidate_extracts.json"),
        _source_intake_file_signature(_data_dir(data_dir) / "source_materials.json"),
    )
    cached_summary = _source_intake_call_cache_get(drafts_cache_key)
    if cached_summary is not None:
        return cached_summary[0]
    templates = list_pending_candidate_review_input_templates(data_dir)
    validations = validate_pending_candidate_review_decision_drafts(drafts, data_dir)
    guards = build_pending_candidate_review_application_guard(drafts, data_dir)
    packets = build_pending_candidate_review_application_packets(drafts, data_dir)

    pending_candidate_ids = [template.candidate_id for template in templates]
    draft_candidate_ids = [result.candidate_id for result in validations]
    exportable_candidate_ids = [
        packet.candidate_id for packet in packets if packet.ready_to_export
    ]
    blocked_candidate_ids = [
        packet.candidate_id for packet in packets if not packet.ready_to_export
    ]
    missing_draft_candidate_ids = [
        candidate_id
        for candidate_id in pending_candidate_ids
        if candidate_id not in set(draft_candidate_ids)
    ]

    candidate_next_actions = {
        candidate_id: "fill_review_input_template"
        for candidate_id in missing_draft_candidate_ids
    }
    candidate_next_actions.update(
        {candidate_id: "resolve_draft_blocking_issues" for candidate_id in blocked_candidate_ids}
    )
    candidate_next_actions.update(
        {candidate_id: "apply_manual_application_packet" for candidate_id in exportable_candidate_ids}
    )

    summary = CandidateReviewApplicationAuditSummary(
        pending_template_count=len(templates),
        draft_count=len(drafts),
        validation_ready_count=sum(
            1 for result in validations if result.ready_for_manual_application
        ),
        validation_blocked_count=sum(
            1 for result in validations if not result.ready_for_manual_application
        ),
        guard_ready_count=sum(1 for guard in guards if guard.ready_to_apply),
        packet_exportable_count=len(exportable_candidate_ids),
        packet_blocked_count=len(blocked_candidate_ids),
        pending_candidate_ids=pending_candidate_ids,
        draft_candidate_ids=draft_candidate_ids,
        exportable_candidate_ids=exportable_candidate_ids,
        blocked_candidate_ids=blocked_candidate_ids,
        missing_draft_candidate_ids=missing_draft_candidate_ids,
        candidate_next_actions=candidate_next_actions,
        preview_review_decision_delta=sum(
            packet.preview_review_decision_delta for packet in packets
        ),
        preview_candidate_status_delta=sum(
            packet.preview_candidate_status_delta for packet in packets
        ),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_APPLICATION_AUDIT_BOUNDARY_NOTES),
    )
    _source_intake_call_cache_store(drafts_cache_key, [summary])
    return summary


def _append_candidate_actions(
    lines: list[str],
    candidate_ids: list[str],
    actions: dict[str, str],
) -> None:
    if not candidate_ids:
        lines.append("- `none`")
        return
    for candidate_id in candidate_ids:
        lines.append(f"- `{candidate_id}`: `{actions[candidate_id]}`")


def render_pending_candidate_review_application_audit_summary_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    summary = build_pending_candidate_review_application_audit_summary(
        drafts,
        data_dir,
    )
    lines = [
        "# Pending Candidate Review Application Audit Summary",
        "",
        "## Summary",
        "",
        f"- Pending templates: `{summary.pending_template_count}`",
        f"- Drafts supplied: `{summary.draft_count}`",
        f"- Validation ready: `{summary.validation_ready_count}`",
        f"- Validation blocked: `{summary.validation_blocked_count}`",
        f"- Guard ready: `{summary.guard_ready_count}`",
        f"- Exportable application packets: `{summary.packet_exportable_count}`",
        f"- Blocked application packets: `{summary.packet_blocked_count}`",
        f"- Missing draft candidates: `{len(summary.missing_draft_candidate_ids)}`",
        f"- Preview review decision additions: `{summary.preview_review_decision_delta}`",
        f"- Preview candidate status updates: `{summary.preview_candidate_status_delta}`",
        f"- Applied review decision delta: `{summary.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{summary.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{summary.formal_evidence_delta}`",
        "- Boundary: Audit summary is read-only planning metadata.",
        "",
        "## Exportable Candidates",
        "",
    ]
    _append_candidate_actions(
        lines,
        summary.exportable_candidate_ids,
        summary.candidate_next_actions,
    )
    lines.extend(["", "## Blocked Candidates", ""])
    _append_candidate_actions(
        lines,
        summary.blocked_candidate_ids,
        summary.candidate_next_actions,
    )
    lines.extend(["", "## Missing Draft Candidates", ""])
    _append_candidate_actions(
        lines,
        summary.missing_draft_candidate_ids,
        summary.candidate_next_actions,
    )
    lines.extend(["", f"Boundary notes: {' '.join(summary.boundary_notes)}"])
    return "\n".join(lines) + "\n"


@_cache_drafts_builder
def build_pending_candidate_review_manual_action_dashboard(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> CandidateReviewManualActionDashboard:
    summary = build_pending_candidate_review_application_audit_summary(
        drafts,
        data_dir,
    )
    action_sequence = list(REVIEW_MANUAL_ACTION_DASHBOARD_ACTION_SEQUENCE)
    candidates_by_action: dict[str, list[str]] = {
        action: [] for action in action_sequence
    }
    for candidate_id in summary.pending_candidate_ids:
        action = summary.candidate_next_actions[candidate_id]
        if action not in candidates_by_action:
            candidates_by_action[action] = []
            action_sequence.append(action)
        candidates_by_action[action].append(candidate_id)

    action_counts = {
        action: len(candidates_by_action[action]) for action in action_sequence
    }
    recommended_processing_order = [
        candidate_id
        for action in action_sequence
        for candidate_id in candidates_by_action[action]
    ]

    return CandidateReviewManualActionDashboard(
        pending_candidate_count=len(summary.pending_candidate_ids),
        action_counts=action_counts,
        candidates_by_action=candidates_by_action,
        recommended_action_sequence=action_sequence,
        recommended_processing_order=recommended_processing_order,
        preview_review_decision_delta=summary.preview_review_decision_delta,
        preview_candidate_status_delta=summary.preview_candidate_status_delta,
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_ACTION_DASHBOARD_BOUNDARY_NOTES),
    )


def _dashboard_action_for_candidate(
    dashboard: CandidateReviewManualActionDashboard,
    candidate_id: str,
) -> str:
    for action in dashboard.recommended_action_sequence:
        if candidate_id in dashboard.candidates_by_action.get(action, []):
            return action
    return ""


def render_pending_candidate_review_manual_action_dashboard_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    dashboard = build_pending_candidate_review_manual_action_dashboard(
        drafts,
        data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Action Dashboard",
        "",
        "## Summary",
        "",
        f"- Pending candidates: `{dashboard.pending_candidate_count}`",
    ]
    for action in dashboard.recommended_action_sequence:
        lines.append(f"- `{action}`: `{dashboard.action_counts[action]}`")
    lines.extend(
        [
            f"- Preview review decision additions: `{dashboard.preview_review_decision_delta}`",
            f"- Preview candidate status updates: `{dashboard.preview_candidate_status_delta}`",
            f"- Applied review decision delta: `{dashboard.applied_review_decision_delta}`",
            f"- Applied candidate status delta: `{dashboard.applied_candidate_status_delta}`",
            f"- Formal evidence delta: `{dashboard.formal_evidence_delta}`",
            "- Boundary: Manual action dashboard is read-only planning metadata.",
            "",
            "## Candidates By Action",
        ]
    )

    for action in dashboard.recommended_action_sequence:
        lines.extend(["", f"### {action}", ""])
        candidate_ids = dashboard.candidates_by_action[action]
        if not candidate_ids:
            lines.append("- `none`")
            continue
        for candidate_id in candidate_ids:
            lines.append(f"- `{candidate_id}`")

    lines.extend(["", "## Recommended Processing Order", ""])
    if not dashboard.recommended_processing_order:
        lines.append("No pending candidate manual actions.")
    for index, candidate_id in enumerate(dashboard.recommended_processing_order, 1):
        action = _dashboard_action_for_candidate(dashboard, candidate_id)
        lines.append(f"{index}. `{candidate_id}`: `{action}`")
    lines.extend(["", f"Boundary notes: {' '.join(dashboard.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _dry_run_required_inputs_for_template(
    template: CandidateReviewInputTemplate,
) -> list[str]:
    return list(dict.fromkeys([*template.base_fields, *template.conditional_fields]))


def _dry_run_step_for_action(
    candidate_id: str,
    action: str,
    templates_by_id: dict[str, CandidateReviewInputTemplate],
    validations_by_id: dict[str, CandidateReviewDraftValidationResult],
    packets_by_id: dict[str, CandidateReviewApplicationPacket],
) -> CandidateReviewManualApplicationDryRunStep:
    boundary_notes = list(REVIEW_MANUAL_APPLICATION_DRY_RUN_BOUNDARY_NOTES)
    if action == "apply_manual_application_packet":
        packet = packets_by_id[candidate_id]
        return CandidateReviewManualApplicationDryRunStep(
            candidate_id=candidate_id,
            action=action,
            dry_run_status="ready_for_manual_application",
            manual_steps=[
                item
                for item in packet.manual_checklist
                if item in {"append_review_decision_entry", "update_candidate_status"}
            ],
            ready_criteria=[
                "application_packet_ready_to_export",
                "review_decision_json_available",
                "candidate_status_update_available",
            ],
            post_apply_checks=[
                item
                for item in packet.manual_checklist
                if item in {"run_source_intake_tests", "verify_formal_evidence_delta_zero"}
            ],
            rollback_notes=list(packet.rollback_notes),
            boundary_notes=boundary_notes,
        )
    if action == "resolve_draft_blocking_issues":
        validation = validations_by_id[candidate_id]
        return CandidateReviewManualApplicationDryRunStep(
            candidate_id=candidate_id,
            action=action,
            dry_run_status="blocked_until_draft_issues_resolved",
            required_inputs=list(validation.missing_fields),
            manual_steps=[
                "resolve_draft_blocking_issues",
                "rerun_draft_validation",
                "rerun_application_guard",
            ],
            ready_criteria=[
                "all_missing_fields_filled",
                "all_blocking_issues_cleared",
                "application_guard_ready",
            ],
            blocking_issues=list(validation.blocking_issues),
            boundary_notes=boundary_notes,
        )

    template = templates_by_id[candidate_id]
    return CandidateReviewManualApplicationDryRunStep(
        candidate_id=candidate_id,
        action=action,
        dry_run_status="needs_review_input_template",
        required_inputs=_dry_run_required_inputs_for_template(template),
        manual_steps=[
            "fill_review_input_template",
            "run_draft_validation",
            "run_application_guard",
        ],
        ready_criteria=[
            "review_input_template_completed",
            "draft_validation_ready",
            "application_guard_ready",
        ],
        boundary_notes=boundary_notes,
    )


@_cache_drafts_builder
def build_pending_candidate_review_manual_application_dry_run_guide(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationDryRunGuide:
    dashboard = build_pending_candidate_review_manual_action_dashboard(
        drafts,
        data_dir,
    )
    templates_by_id = {
        template.candidate_id: template
        for template in list_pending_candidate_review_input_templates(data_dir)
    }
    validations_by_id = {
        validation.candidate_id: validation
        for validation in validate_pending_candidate_review_decision_drafts(
            drafts,
            data_dir,
        )
    }
    packets_by_id = {
        packet.candidate_id: packet
        for packet in build_pending_candidate_review_application_packets(
            drafts,
            data_dir,
        )
    }

    steps = [
        _dry_run_step_for_action(
            candidate_id,
            _dashboard_action_for_candidate(dashboard, candidate_id),
            templates_by_id,
            validations_by_id,
            packets_by_id,
        )
        for candidate_id in dashboard.recommended_processing_order
    ]
    return CandidateReviewManualApplicationDryRunGuide(
        pending_candidate_count=dashboard.pending_candidate_count,
        step_count=len(steps),
        steps=steps,
        recommended_processing_order=list(dashboard.recommended_processing_order),
        preview_review_decision_delta=dashboard.preview_review_decision_delta,
        preview_candidate_status_delta=dashboard.preview_candidate_status_delta,
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_DRY_RUN_BOUNDARY_NOTES),
    )


def _append_markdown_list(
    lines: list[str],
    values: list[str],
    *,
    indent: str = "    ",
) -> None:
    if not values:
        lines.append(f"{indent}- none")
        return
    for value in values:
        lines.append(f"{indent}- {value}")


def render_pending_candidate_review_manual_application_dry_run_guide_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    guide = build_pending_candidate_review_manual_application_dry_run_guide(
        drafts,
        data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Dry-Run Guide",
        "",
        "## Summary",
        "",
        f"- Pending candidates: `{guide.pending_candidate_count}`",
        f"- Dry-run steps: `{guide.step_count}`",
        f"- Preview review decision additions: `{guide.preview_review_decision_delta}`",
        f"- Preview candidate status updates: `{guide.preview_candidate_status_delta}`",
        f"- Applied review decision delta: `{guide.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{guide.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{guide.formal_evidence_delta}`",
        "- Boundary: Manual application dry-run guide is read-only planning metadata.",
        "",
        "## Dry-Run Steps",
        "",
    ]
    if not guide.steps:
        lines.append("No pending candidate dry-run steps.")
    for step in guide.steps:
        lines.extend(
            [
                f"- Candidate: `{step.candidate_id}`",
                f"  - Action: `{step.action}`",
                f"  - Status: `{step.dry_run_status}`",
                "  - Required inputs:",
            ]
        )
        _append_markdown_list(lines, step.required_inputs)
        lines.append("  - Manual steps:")
        _append_markdown_list(lines, step.manual_steps)
        lines.append("  - Ready criteria:")
        _append_markdown_list(lines, step.ready_criteria)
        lines.append("  - Post-apply checks:")
        _append_markdown_list(lines, step.post_apply_checks)
        lines.append("  - Rollback notes:")
        _append_markdown_list(lines, step.rollback_notes)
        lines.append("  - Blocking issues:")
        _append_markdown_list(lines, step.blocking_issues)
        lines.append(f"  - Boundary: {' '.join(step.boundary_notes)}")

    lines.extend(["", "## Recommended Processing Order", ""])
    if not guide.recommended_processing_order:
        lines.append("No pending candidate manual application dry-run steps.")
    for index, step in enumerate(guide.steps, 1):
        lines.append(f"{index}. `{step.candidate_id}`: `{step.action}`")
    lines.extend(["", f"Boundary notes: {' '.join(guide.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _draft_decision_id_counts(
    drafts: list[dict[str, Any]],
) -> Counter[str]:
    return Counter(str(draft.get("decision_id", "")).strip() for draft in drafts)


def _preflight_review_decision_id_unique(
    decision_id: str,
    draft_decision_id_counts: Counter[str],
    existing_review_decision_ids: set[str],
) -> bool:
    if not decision_id:
        return False
    return (
        draft_decision_id_counts.get(decision_id, 0) == 1
        and decision_id not in existing_review_decision_ids
    )


def _preflight_candidate_status_patch_matches_pending(
    candidate_id: str,
    packet: CandidateReviewApplicationPacket,
    candidate_statuses: dict[str, str],
) -> bool:
    status_update = packet.candidate_status_update
    review_decision = str(packet.review_decision_json.get("decision", ""))
    return (
        status_update.get("candidate_id") == candidate_id
        and status_update.get("from_status") == candidate_statuses.get(candidate_id)
        and status_update.get("from_status") == "pending_review"
        and status_update.get("to_status") == review_decision
    )


def _preflight_packet_delta_matches_preview(
    packet: CandidateReviewApplicationPacket,
) -> bool:
    status_update = packet.candidate_status_update
    expected_review_delta = 1 if packet.review_decision_json else 0
    expected_status_delta = (
        1
        if status_update
        and status_update.get("from_status") != status_update.get("to_status")
        else 0
    )
    return (
        packet.preview_review_decision_delta == expected_review_delta
        and packet.preview_candidate_status_delta == expected_status_delta
    )


def _preflight_expected_status_delta(
    status_update: dict[str, str],
) -> int:
    if not status_update:
        return 0
    return 1 if status_update.get("from_status") != status_update.get("to_status") else 0


def _preflight_blockers_for_ready_packet(
    decision_id_unique: bool,
    candidate_status_patch_matches_pending: bool,
    packet_delta_matches_preview: bool,
) -> list[str]:
    blockers: list[str] = []
    if not decision_id_unique:
        blockers.append("review_decision_id_not_unique")
    if not candidate_status_patch_matches_pending:
        blockers.append("candidate_status_patch_not_pending_match")
    if not packet_delta_matches_preview:
        blockers.append("packet_delta_does_not_match_preview")
    return blockers


def _preflight_check_for_step(
    step: CandidateReviewManualApplicationDryRunStep,
    packets_by_id: dict[str, CandidateReviewApplicationPacket],
    draft_decision_id_counts: Counter[str],
    existing_review_decision_ids: set[str],
    candidate_statuses: dict[str, str],
) -> CandidateReviewManualApplicationPreflightCheck:
    boundary_notes = list(REVIEW_MANUAL_APPLICATION_PREFLIGHT_BOUNDARY_NOTES)
    packet = packets_by_id.get(step.candidate_id)
    if packet is None:
        return CandidateReviewManualApplicationPreflightCheck(
            candidate_id=step.candidate_id,
            decision_id="",
            ready_for_manual_application=False,
            decision_id_unique=False,
            candidate_status_patch_matches_pending=False,
            packet_delta_matches_preview=False,
            preflight_blockers=[
                "manual_application_packet_missing",
                *step.blocking_issues,
            ],
            boundary_notes=boundary_notes,
        )

    decision_id_unique = _preflight_review_decision_id_unique(
        packet.decision_id,
        draft_decision_id_counts,
        existing_review_decision_ids,
    )
    if not packet.ready_to_export:
        blockers = [
            "manual_application_packet_not_exportable",
            *packet.blocking_issues,
            *step.blocking_issues,
        ]
        return CandidateReviewManualApplicationPreflightCheck(
            candidate_id=step.candidate_id,
            decision_id=packet.decision_id,
            ready_for_manual_application=False,
            decision_id_unique=decision_id_unique,
            candidate_status_patch_matches_pending=False,
            packet_delta_matches_preview=False,
            preflight_blockers=list(dict.fromkeys(blockers)),
            boundary_notes=boundary_notes,
        )

    status_update = dict(packet.candidate_status_update)
    candidate_status_patch_matches_pending = (
        _preflight_candidate_status_patch_matches_pending(
            step.candidate_id,
            packet,
            candidate_statuses,
        )
    )
    packet_delta_matches_preview = _preflight_packet_delta_matches_preview(packet)
    blockers = _preflight_blockers_for_ready_packet(
        decision_id_unique,
        candidate_status_patch_matches_pending,
        packet_delta_matches_preview,
    )
    expected_review_delta = 1 if packet.review_decision_json else 0
    expected_status_delta = _preflight_expected_status_delta(status_update)
    return CandidateReviewManualApplicationPreflightCheck(
        candidate_id=step.candidate_id,
        decision_id=packet.decision_id,
        ready_for_manual_application=not blockers,
        decision_id_unique=decision_id_unique,
        candidate_status_patch_matches_pending=candidate_status_patch_matches_pending,
        packet_delta_matches_preview=packet_delta_matches_preview,
        expected_review_decision_delta=expected_review_delta,
        expected_candidate_status_delta=expected_status_delta,
        expected_candidate_status_update=status_update,
        preflight_blockers=blockers,
        boundary_notes=boundary_notes,
    )


@_cache_drafts_builder
def build_pending_candidate_review_manual_application_preflight_report(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationPreflightReport:
    guide = build_pending_candidate_review_manual_application_dry_run_guide(
        drafts,
        data_dir,
    )
    packets_by_id = {
        packet.candidate_id: packet
        for packet in build_pending_candidate_review_application_packets(
            drafts,
            data_dir,
        )
    }
    draft_decision_id_counts = _draft_decision_id_counts(drafts)
    existing_review_decision_ids = {
        decision.decision_id for decision in load_review_decisions(data_dir)
    }
    candidate_statuses = _candidate_status_by_id(data_dir)
    checks = [
        _preflight_check_for_step(
            step,
            packets_by_id,
            draft_decision_id_counts,
            existing_review_decision_ids,
            candidate_statuses,
        )
        for step in guide.steps
    ]
    ready_candidate_ids = [
        check.candidate_id for check in checks if check.ready_for_manual_application
    ]
    blocked_candidate_ids = [
        check.candidate_id
        for check in checks
        if not check.ready_for_manual_application
    ]
    return CandidateReviewManualApplicationPreflightReport(
        pending_candidate_count=guide.pending_candidate_count,
        preflight_check_count=len(checks),
        checks=checks,
        ready_candidate_ids=ready_candidate_ids,
        blocked_candidate_ids=blocked_candidate_ids,
        preview_review_decision_delta=sum(
            check.expected_review_decision_delta
            for check in checks
            if check.ready_for_manual_application
        ),
        preview_candidate_status_delta=sum(
            check.expected_candidate_status_delta
            for check in checks
            if check.ready_for_manual_application
        ),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_PREFLIGHT_BOUNDARY_NOTES),
    )


def render_pending_candidate_review_manual_application_preflight_report_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    report = build_pending_candidate_review_manual_application_preflight_report(
        drafts,
        data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Preflight Report",
        "",
        "## Summary",
        "",
        f"- Pending candidates: `{report.pending_candidate_count}`",
        f"- Preflight checks: `{report.preflight_check_count}`",
        f"- Ready candidates: `{len(report.ready_candidate_ids)}`",
        f"- Blocked candidates: `{len(report.blocked_candidate_ids)}`",
        f"- Preview review decision additions: `{report.preview_review_decision_delta}`",
        f"- Preview candidate status updates: `{report.preview_candidate_status_delta}`",
        f"- Applied review decision delta: `{report.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{report.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{report.formal_evidence_delta}`",
        "- Boundary: Manual application preflight report is read-only planning metadata.",
        "",
        "## Ready Candidates",
        "",
    ]
    if not report.ready_candidate_ids:
        lines.append("- `none`")
    for candidate_id in report.ready_candidate_ids:
        lines.append(f"- `{candidate_id}`")

    lines.extend(["", "## Blocked Candidates", ""])
    if not report.blocked_candidate_ids:
        lines.append("- `none`")
    for candidate_id in report.blocked_candidate_ids:
        lines.append(f"- `{candidate_id}`")

    lines.extend(["", "## Preflight Checks", ""])
    if not report.checks:
        lines.append("No pending candidate preflight checks.")
    for check in report.checks:
        lines.extend(
            [
                f"- Candidate: `{check.candidate_id}`",
                f"  - Decision id: `{check.decision_id or 'none'}`",
                f"  - Ready: `{check.ready_for_manual_application}`",
                (
                    "  - Checks: "
                    f"decision_id_unique=`{check.decision_id_unique}`, "
                    "candidate_status_patch_matches_pending="
                    f"`{check.candidate_status_patch_matches_pending}`, "
                    "packet_delta_matches_preview="
                    f"`{check.packet_delta_matches_preview}`"
                ),
                (
                    "  - Expected deltas: "
                    f"review_decision=`{check.expected_review_decision_delta}`, "
                    f"candidate_status=`{check.expected_candidate_status_delta}`"
                ),
                "  - Expected candidate status update:",
            ]
        )
        if check.expected_candidate_status_update:
            lines.extend(
                f"    {line}"
                for line in _format_json_block(check.expected_candidate_status_update)
            )
        else:
            lines.append("    - none")
        lines.append("  - Preflight blockers:")
        _append_markdown_list(lines, check.preflight_blockers)
        lines.append(f"  - Boundary: {' '.join(check.boundary_notes)}")

    lines.extend(["", f"Boundary notes: {' '.join(report.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _handoff_preflight_checks(
    check: CandidateReviewManualApplicationPreflightCheck,
) -> list[str]:
    checks: list[str] = []
    if check.decision_id_unique:
        checks.append("decision_id_unique")
    if check.candidate_status_patch_matches_pending:
        checks.append("candidate_status_patch_matches_pending")
    if check.packet_delta_matches_preview:
        checks.append("packet_delta_matches_preview")
    return checks


def _handoff_readiness_status(
    step: CandidateReviewManualApplicationDryRunStep,
    check: CandidateReviewManualApplicationPreflightCheck,
) -> str:
    if check.ready_for_manual_application:
        return "ready_for_manual_application"
    if step.action == "fill_review_input_template":
        return "needs_review_input_template"
    if step.action == "resolve_draft_blocking_issues":
        return "blocked_until_draft_issues_resolved"
    if check.preflight_blockers:
        return "blocked_until_preflight_issues_resolved"
    return step.dry_run_status


def _handoff_item(
    step: CandidateReviewManualApplicationDryRunStep,
    check: CandidateReviewManualApplicationPreflightCheck,
) -> CandidateReviewManualApplicationHandoffItem:
    blocking_issues = list(
        dict.fromkeys([*step.blocking_issues, *check.preflight_blockers])
    )
    return CandidateReviewManualApplicationHandoffItem(
        candidate_id=step.candidate_id,
        action=step.action,
        readiness_status=_handoff_readiness_status(step, check),
        shortest_next_action=step.action,
        decision_id=check.decision_id,
        required_inputs=list(step.required_inputs),
        manual_steps=list(step.manual_steps),
        preflight_checks=_handoff_preflight_checks(check),
        post_apply_checks=list(step.post_apply_checks),
        rollback_notes=list(step.rollback_notes),
        blocking_issues=blocking_issues,
        expected_candidate_status_update=dict(check.expected_candidate_status_update),
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_HANDOFF_BOUNDARY_NOTES),
    )


@_cache_drafts_builder
def build_pending_candidate_review_manual_application_handoff_summary(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationHandoffSummary:
    dashboard = build_pending_candidate_review_manual_action_dashboard(
        drafts,
        data_dir,
    )
    guide = build_pending_candidate_review_manual_application_dry_run_guide(
        drafts,
        data_dir,
    )
    preflight = build_pending_candidate_review_manual_application_preflight_report(
        drafts,
        data_dir,
    )
    checks_by_id = {check.candidate_id: check for check in preflight.checks}
    steps_by_id = {step.candidate_id: step for step in guide.steps}
    items = [
        _handoff_item(steps_by_id[candidate_id], checks_by_id[candidate_id])
        for candidate_id in dashboard.recommended_processing_order
    ]
    ready_candidate_ids = [
        item.candidate_id
        for item in items
        if item.readiness_status == "ready_for_manual_application"
    ]
    missing_draft_candidate_ids = [
        item.candidate_id
        for item in items
        if item.action == "fill_review_input_template"
    ]
    blocked_candidate_ids = [
        item.candidate_id
        for item in items
        if item.candidate_id not in ready_candidate_ids
        and item.candidate_id not in missing_draft_candidate_ids
    ]
    return CandidateReviewManualApplicationHandoffSummary(
        pending_candidate_count=dashboard.pending_candidate_count,
        handoff_item_count=len(items),
        items=items,
        ready_candidate_ids=ready_candidate_ids,
        blocked_candidate_ids=blocked_candidate_ids,
        missing_draft_candidate_ids=missing_draft_candidate_ids,
        recommended_processing_order=list(dashboard.recommended_processing_order),
        preview_review_decision_delta=preflight.preview_review_decision_delta,
        preview_candidate_status_delta=preflight.preview_candidate_status_delta,
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_HANDOFF_BOUNDARY_NOTES),
    )


def _append_handoff_candidate_lines(
    lines: list[str],
    items: list[CandidateReviewManualApplicationHandoffItem],
) -> None:
    if not items:
        lines.append("- `none`")
        return
    for item in items:
        lines.extend(
            [
                f"- `{item.candidate_id}`: `{item.shortest_next_action}`",
                f"  - Status: `{item.readiness_status}`",
                "  - Required inputs:",
            ]
        )
        _append_markdown_list(lines, item.required_inputs)
        lines.append("  - Manual steps:")
        _append_markdown_list(lines, item.manual_steps)
        lines.append("  - Preflight checks:")
        _append_markdown_list(lines, item.preflight_checks)
        lines.append("  - Post-apply checks:")
        _append_markdown_list(lines, item.post_apply_checks)
        lines.append("  - Blocking issues:")
        _append_markdown_list(lines, item.blocking_issues)
        if item.expected_candidate_status_update:
            lines.append("  - Expected candidate status update:")
            lines.extend(
                f"    {line}"
                for line in _format_json_block(item.expected_candidate_status_update)
            )


def render_pending_candidate_review_manual_application_handoff_summary_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    summary = build_pending_candidate_review_manual_application_handoff_summary(
        drafts,
        data_dir,
    )
    items_by_id = {item.candidate_id: item for item in summary.items}
    ready_items = [items_by_id[candidate_id] for candidate_id in summary.ready_candidate_ids]
    blocked_items = [
        items_by_id[candidate_id] for candidate_id in summary.blocked_candidate_ids
    ]
    missing_items = [
        items_by_id[candidate_id]
        for candidate_id in summary.missing_draft_candidate_ids
    ]
    lines = [
        "# Pending Candidate Review Manual Application Handoff Summary",
        "",
        "## Summary",
        "",
        f"- Pending candidates: `{summary.pending_candidate_count}`",
        f"- Handoff items: `{summary.handoff_item_count}`",
        f"- Ready candidates: `{len(summary.ready_candidate_ids)}`",
        f"- Blocked candidates: `{len(summary.blocked_candidate_ids)}`",
        f"- Missing draft candidates: `{len(summary.missing_draft_candidate_ids)}`",
        f"- Preview review decision additions: `{summary.preview_review_decision_delta}`",
        f"- Preview candidate status updates: `{summary.preview_candidate_status_delta}`",
        f"- Applied review decision delta: `{summary.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{summary.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{summary.formal_evidence_delta}`",
        "- Boundary: Manual application handoff summary is read-only planning metadata.",
        "",
        "## Ready Candidates",
        "",
    ]
    _append_handoff_candidate_lines(lines, ready_items)
    lines.extend(["", "## Blocked Candidates", ""])
    _append_handoff_candidate_lines(lines, blocked_items)
    lines.extend(["", "## Missing Draft Candidates", ""])
    _append_handoff_candidate_lines(lines, missing_items)

    lines.extend(["", "## Recommended Processing Order", ""])
    if not summary.recommended_processing_order:
        lines.append("No pending candidate handoff items.")
    for index, candidate_id in enumerate(summary.recommended_processing_order, 1):
        item = items_by_id[candidate_id]
        lines.append(f"{index}. `{candidate_id}`: `{item.shortest_next_action}`")
    lines.extend(["", f"Boundary notes: {' '.join(summary.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _ledger_status_for_handoff_item(
    item: CandidateReviewManualApplicationHandoffItem,
) -> str:
    if item.readiness_status == "ready_for_manual_application":
        return "ready_to_apply_manual_packet"
    if item.action == "resolve_draft_blocking_issues":
        return "blocked_resolve_draft_issues"
    if item.action == "fill_review_input_template":
        return "needs_review_input_template"
    return "blocked_resolve_preflight_issues"


def _ledger_checkboxes_for_handoff_item(
    item: CandidateReviewManualApplicationHandoffItem,
) -> list[str]:
    if item.readiness_status == "ready_for_manual_application":
        return list(
            dict.fromkeys(
                [
                    *(f"confirm_{check}" for check in item.preflight_checks),
                    *item.manual_steps,
                    *item.post_apply_checks,
                ]
            )
        )
    if item.action == "resolve_draft_blocking_issues":
        return [
            "resolve_draft_blocking_issues",
            "rerun_draft_validation",
            "rerun_application_guard",
            "rerun_preflight_report",
            "rerun_handoff_summary",
        ]
    return [
        "fill_review_input_template",
        "run_draft_validation",
        "run_application_guard",
        "rerun_preflight_report",
        "rerun_handoff_summary",
    ]


def _ledger_row_from_handoff_item(
    item: CandidateReviewManualApplicationHandoffItem,
    sequence_number: int,
) -> CandidateReviewManualApplicationReadinessLedgerRow:
    return CandidateReviewManualApplicationReadinessLedgerRow(
        candidate_id=item.candidate_id,
        sequence_number=sequence_number,
        ledger_status=_ledger_status_for_handoff_item(item),
        action=item.action,
        checkboxes=_ledger_checkboxes_for_handoff_item(item),
        required_inputs=list(item.required_inputs),
        blocking_issues=list(item.blocking_issues),
        expected_candidate_status_update=dict(item.expected_candidate_status_update),
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_READINESS_LEDGER_BOUNDARY_NOTES),
    )


@_cache_drafts_builder
def build_pending_candidate_review_manual_application_readiness_ledger(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationReadinessLedger:
    handoff = build_pending_candidate_review_manual_application_handoff_summary(
        drafts,
        data_dir,
    )
    rows = [
        _ledger_row_from_handoff_item(item, index)
        for index, item in enumerate(handoff.items, 1)
    ]
    return CandidateReviewManualApplicationReadinessLedger(
        pending_candidate_count=handoff.pending_candidate_count,
        ledger_row_count=len(rows),
        rows=rows,
        ready_candidate_ids=list(handoff.ready_candidate_ids),
        blocked_candidate_ids=list(handoff.blocked_candidate_ids),
        missing_draft_candidate_ids=list(handoff.missing_draft_candidate_ids),
        recommended_processing_order=list(handoff.recommended_processing_order),
        unchecked_checkbox_count=sum(len(row.checkboxes) for row in rows),
        preview_review_decision_delta=handoff.preview_review_decision_delta,
        preview_candidate_status_delta=handoff.preview_candidate_status_delta,
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_READINESS_LEDGER_BOUNDARY_NOTES),
    )


def _append_ledger_row_markdown(
    lines: list[str],
    row: CandidateReviewManualApplicationReadinessLedgerRow,
) -> None:
    lines.extend(
        [
            (
                f"{row.sequence_number}. `{row.candidate_id}`: "
                f"`{row.ledger_status}`"
            ),
            f"   - Action: `{row.action}`",
            "   - Checkboxes:",
        ]
    )
    if not row.checkboxes:
        lines.append("     - [ ] none")
    for checkbox in row.checkboxes:
        lines.append(f"     - [ ] {checkbox}")
    lines.append("   - Required inputs:")
    _append_markdown_list(lines, row.required_inputs, indent="     ")
    lines.append("   - Blocking issues:")
    _append_markdown_list(lines, row.blocking_issues, indent="     ")
    if row.expected_candidate_status_update:
        lines.append("   - Expected candidate status update:")
        lines.extend(
            f"     {line}"
            for line in _format_json_block(row.expected_candidate_status_update)
        )
    lines.append(f"   - Boundary: {' '.join(row.boundary_notes)}")


def render_pending_candidate_review_manual_application_readiness_ledger_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    ledger = build_pending_candidate_review_manual_application_readiness_ledger(
        drafts,
        data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Readiness Ledger",
        "",
        "## Summary",
        "",
        f"- Pending candidates: `{ledger.pending_candidate_count}`",
        f"- Ledger rows: `{ledger.ledger_row_count}`",
        f"- Ready rows: `{len(ledger.ready_candidate_ids)}`",
        f"- Blocked rows: `{len(ledger.blocked_candidate_ids)}`",
        f"- Missing draft rows: `{len(ledger.missing_draft_candidate_ids)}`",
        f"- Unchecked checkbox count: `{ledger.unchecked_checkbox_count}`",
        f"- Preview review decision additions: `{ledger.preview_review_decision_delta}`",
        f"- Preview candidate status updates: `{ledger.preview_candidate_status_delta}`",
        f"- Applied review decision delta: `{ledger.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{ledger.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{ledger.formal_evidence_delta}`",
        "- Boundary: Readiness ledger is read-only planning metadata.",
        "",
        "## Ledger Rows",
        "",
    ]
    if not ledger.rows:
        lines.append("No pending candidate readiness ledger rows.")
    for row in ledger.rows:
        _append_ledger_row_markdown(lines, row)

    lines.extend(["", "## Recommended Processing Order", ""])
    if not ledger.recommended_processing_order:
        lines.append("No pending candidate readiness ledger rows.")
    for index, candidate_id in enumerate(ledger.recommended_processing_order, 1):
        row = next(row for row in ledger.rows if row.candidate_id == candidate_id)
        lines.append(f"{index}. `{candidate_id}`: `{row.ledger_status}`")
    lines.extend(["", f"Boundary notes: {' '.join(ledger.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _session_action_from_ledger_row(
    row: CandidateReviewManualApplicationReadinessLedgerRow,
) -> CandidateReviewManualApplicationSessionAction:
    return CandidateReviewManualApplicationSessionAction(
        candidate_id=row.candidate_id,
        sequence_number=row.sequence_number,
        action_type=row.action,
        ledger_status=row.ledger_status,
        checkboxes=list(row.checkboxes),
        blocking_issues=list(row.blocking_issues),
        expected_candidate_status_update=dict(row.expected_candidate_status_update),
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_SESSION_PACKET_BOUNDARY_NOTES),
    )


@_cache_drafts_builder
def build_pending_candidate_review_manual_application_session_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationSessionPacket:
    ledger = build_pending_candidate_review_manual_application_readiness_ledger(
        drafts,
        data_dir,
    )
    rows_by_id = {row.candidate_id: row for row in ledger.rows}
    ready_action_queue = [
        _session_action_from_ledger_row(rows_by_id[candidate_id])
        for candidate_id in ledger.ready_candidate_ids
    ]
    blocked_follow_ups = [
        _session_action_from_ledger_row(rows_by_id[candidate_id])
        for candidate_id in ledger.blocked_candidate_ids
    ]
    missing_draft_follow_ups = [
        _session_action_from_ledger_row(rows_by_id[candidate_id])
        for candidate_id in ledger.missing_draft_candidate_ids
    ]
    return CandidateReviewManualApplicationSessionPacket(
        session_id="pending_review_manual_application_session",
        session_title="Pending Review Manual Application Session",
        session_scope="ready_first_manual_application",
        pending_candidate_count=ledger.pending_candidate_count,
        ready_action_queue=ready_action_queue,
        blocked_follow_ups=blocked_follow_ups,
        missing_draft_follow_ups=missing_draft_follow_ups,
        post_session_verification=list(REVIEW_MANUAL_APPLICATION_SESSION_POST_VERIFICATION),
        recommended_processing_order=list(ledger.recommended_processing_order),
        unchecked_checkbox_count=ledger.unchecked_checkbox_count,
        preview_review_decision_delta=ledger.preview_review_decision_delta,
        preview_candidate_status_delta=ledger.preview_candidate_status_delta,
        ready_action_count=len(ready_action_queue),
        blocked_follow_up_count=len(blocked_follow_ups),
        missing_draft_follow_up_count=len(missing_draft_follow_ups),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_SESSION_PACKET_BOUNDARY_NOTES),
    )


def _append_session_action_markdown(
    lines: list[str],
    actions: list[CandidateReviewManualApplicationSessionAction],
) -> None:
    if not actions:
        lines.append("- `none`")
        return
    for action in actions:
        lines.extend(
            [
                (
                    f"{action.sequence_number}. `{action.candidate_id}`: "
                    f"`{action.action_type}`"
                ),
                f"   - Ledger status: `{action.ledger_status}`",
                "   - Checkboxes:",
            ]
        )
        if not action.checkboxes:
            lines.append("     - [ ] none")
        for checkbox in action.checkboxes:
            lines.append(f"     - [ ] {checkbox}")
        lines.append("   - Blocking issues:")
        _append_markdown_list(lines, action.blocking_issues, indent="     ")
        if action.expected_candidate_status_update:
            lines.append("   - Expected candidate status update:")
            lines.extend(
                f"     {line}"
                for line in _format_json_block(action.expected_candidate_status_update)
            )
        lines.append(f"   - Boundary: {' '.join(action.boundary_notes)}")


def render_pending_candidate_review_manual_application_session_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_session_packet(
        drafts,
        data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Session Packet",
        "",
        "## Session Header",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Session title: `{packet.session_title}`",
        f"- Session scope: `{packet.session_scope}`",
        f"- Pending candidates: `{packet.pending_candidate_count}`",
        f"- Ready actions: `{packet.ready_action_count}`",
        f"- Blocked follow-ups: `{packet.blocked_follow_up_count}`",
        f"- Missing draft follow-ups: `{packet.missing_draft_follow_up_count}`",
        f"- Unchecked checkbox count: `{packet.unchecked_checkbox_count}`",
        f"- Preview review decision additions: `{packet.preview_review_decision_delta}`",
        f"- Preview candidate status updates: `{packet.preview_candidate_status_delta}`",
        f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
        "- Boundary: Manual application session packet is read-only planning metadata.",
        "",
        "## Ready-First Action Queue",
        "",
    ]
    _append_session_action_markdown(lines, packet.ready_action_queue)
    lines.extend(["", "## Blocked Follow-Ups", ""])
    _append_session_action_markdown(lines, packet.blocked_follow_ups)
    lines.extend(["", "## Missing Draft Follow-Ups", ""])
    _append_session_action_markdown(lines, packet.missing_draft_follow_ups)

    lines.extend(["", "## Post-Session Verification", ""])
    if not packet.post_session_verification:
        lines.append("- [ ] none")
    for item in packet.post_session_verification:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Recommended Processing Order", ""])
    if not packet.recommended_processing_order:
        lines.append("No pending candidate session actions.")
    for index, candidate_id in enumerate(packet.recommended_processing_order, 1):
        lines.append(f"{index}. `{candidate_id}`")
    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _session_outcome_item_from_action(
    action: CandidateReviewManualApplicationSessionAction,
    session_lane: str,
    candidate_statuses: dict[str, str],
) -> CandidateReviewManualApplicationSessionOutcomeItem:
    current_status = candidate_statuses.get(action.candidate_id, "")
    projected_status = current_status
    projected_review_delta = 0
    projected_status_delta = 0
    remaining_follow_up_action = action.action_type

    if session_lane == "ready_action":
        projected_status = action.expected_candidate_status_update.get(
            "to_status",
            current_status,
        )
        projected_review_delta = 1
        projected_status_delta = int(
            bool(current_status) and current_status != projected_status
        )
        remaining_follow_up_action = ""

    projected_outcome = (
        "leaves_pending_review"
        if current_status == "pending_review" and projected_status != "pending_review"
        else "remains_pending_review"
    )

    return CandidateReviewManualApplicationSessionOutcomeItem(
        candidate_id=action.candidate_id,
        sequence_number=action.sequence_number,
        session_lane=session_lane,
        action_type=action.action_type,
        current_candidate_status=current_status,
        projected_candidate_status=projected_status,
        projected_outcome=projected_outcome,
        projected_review_decision_delta=projected_review_delta,
        projected_candidate_status_delta=projected_status_delta,
        remaining_follow_up_action=remaining_follow_up_action,
        blocking_issues=list(action.blocking_issues),
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_SESSION_OUTCOME_BOUNDARY_NOTES),
    )


@_cache_drafts_builder
def build_pending_candidate_review_manual_application_session_outcome_preview(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationSessionOutcomePreview:
    packet = build_pending_candidate_review_manual_application_session_packet(
        drafts,
        data_dir,
    )
    candidate_statuses = _candidate_status_by_id(data_dir)
    items = [
        *(
            _session_outcome_item_from_action(
                action,
                "ready_action",
                candidate_statuses,
            )
            for action in packet.ready_action_queue
        ),
        *(
            _session_outcome_item_from_action(
                action,
                "blocked_follow_up",
                candidate_statuses,
            )
            for action in packet.blocked_follow_ups
        ),
        *(
            _session_outcome_item_from_action(
                action,
                "missing_draft_follow_up",
                candidate_statuses,
            )
            for action in packet.missing_draft_follow_ups
        ),
    ]
    projected_non_pending_candidate_ids = [
        item.candidate_id
        for item in items
        if item.projected_outcome == "leaves_pending_review"
    ]
    projected_remaining_pending_candidate_ids = [
        item.candidate_id
        for item in items
        if item.projected_candidate_status == "pending_review"
    ]

    return CandidateReviewManualApplicationSessionOutcomePreview(
        session_id=packet.session_id,
        preview_scope="ready_actions_only",
        pending_candidate_count=packet.pending_candidate_count,
        preview_item_count=len(items),
        items=items,
        ready_applied_candidate_ids=list(projected_non_pending_candidate_ids),
        projected_non_pending_candidate_ids=projected_non_pending_candidate_ids,
        projected_remaining_pending_candidate_ids=projected_remaining_pending_candidate_ids,
        follow_up_candidate_ids=list(projected_remaining_pending_candidate_ids),
        post_session_next_actions=list(
            REVIEW_MANUAL_APPLICATION_SESSION_OUTCOME_NEXT_ACTIONS
        ),
        recommended_processing_order=list(packet.recommended_processing_order),
        projected_review_decision_delta=sum(
            item.projected_review_decision_delta for item in items
        ),
        projected_candidate_status_delta=sum(
            item.projected_candidate_status_delta for item in items
        ),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_SESSION_OUTCOME_BOUNDARY_NOTES),
    )


def _append_session_outcome_projected_changes_markdown(
    lines: list[str],
    items: list[CandidateReviewManualApplicationSessionOutcomeItem],
) -> None:
    projected_changes = [
        item for item in items if item.projected_outcome == "leaves_pending_review"
    ]
    if not projected_changes:
        lines.append("- `none`")
        return
    for item in projected_changes:
        lines.append(
            (
                f"- `{item.candidate_id}`: "
                f"`{item.current_candidate_status}` -> "
                f"`{item.projected_candidate_status}`"
            )
        )
        lines.append(f"  - Session lane: `{item.session_lane}`")
        lines.append(f"  - Action: `{item.action_type}`")
        lines.append(
            f"  - Review decision delta: `{item.projected_review_decision_delta}`"
        )
        lines.append(
            f"  - Candidate status delta: `{item.projected_candidate_status_delta}`"
        )


def _append_session_outcome_follow_ups_markdown(
    lines: list[str],
    items: list[CandidateReviewManualApplicationSessionOutcomeItem],
) -> None:
    follow_ups = [
        item for item in items if item.projected_candidate_status == "pending_review"
    ]
    if not follow_ups:
        lines.append("- `none`")
        return
    for item in follow_ups:
        lines.append(
            f"- `{item.candidate_id}`: `{item.remaining_follow_up_action}`"
        )
        lines.append(f"  - Session lane: `{item.session_lane}`")
        lines.append(f"  - Projected outcome: `{item.projected_outcome}`")
        lines.append("  - Blocking issues:")
        _append_markdown_list(lines, item.blocking_issues, indent="    ")


def render_pending_candidate_review_manual_application_session_outcome_preview_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
) -> str:
    preview = build_pending_candidate_review_manual_application_session_outcome_preview(
        drafts,
        data_dir,
    )
    items_by_id = {item.candidate_id: item for item in preview.items}
    lines = [
        "# Pending Candidate Review Manual Application Session Outcome Preview",
        "",
        "## Summary",
        "",
        f"- Session id: `{preview.session_id}`",
        f"- Preview scope: `{preview.preview_scope}`",
        f"- Pending candidates: `{preview.pending_candidate_count}`",
        f"- Preview items: `{preview.preview_item_count}`",
        (
            "- Projected non-pending candidates: "
            f"`{len(preview.projected_non_pending_candidate_ids)}`"
        ),
        (
            "- Projected remaining pending candidates: "
            f"`{len(preview.projected_remaining_pending_candidate_ids)}`"
        ),
        f"- Projected review decision additions: `{preview.projected_review_decision_delta}`",
        f"- Projected candidate status updates: `{preview.projected_candidate_status_delta}`",
        f"- Applied review decision delta: `{preview.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{preview.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{preview.formal_evidence_delta}`",
        "- Boundary: Session outcome preview is read-only planning metadata.",
        "",
        "## Projected Status Changes",
        "",
    ]
    _append_session_outcome_projected_changes_markdown(lines, preview.items)
    lines.extend(["", "## Remaining Pending Follow-Ups", ""])
    _append_session_outcome_follow_ups_markdown(lines, preview.items)

    lines.extend(["", "## Post-Session Next Actions", ""])
    if not preview.post_session_next_actions:
        lines.append("- [ ] none")
    for action in preview.post_session_next_actions:
        lines.append(f"- [ ] {action}")

    lines.extend(["", "## Recommended Processing Order", ""])
    if not preview.recommended_processing_order:
        lines.append("No pending candidate session outcome items.")
    for index, candidate_id in enumerate(preview.recommended_processing_order, 1):
        item = items_by_id[candidate_id]
        follow_up_action = item.remaining_follow_up_action or item.action_type
        lines.append(f"{index}. `{candidate_id}`: `{follow_up_action}`")
    lines.extend(["", f"Boundary notes: {' '.join(preview.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _review_decision_payloads_by_candidate_id(
    data_dir: Path | str | None = None,
) -> dict[str, dict[str, Any]]:
    decisions_by_candidate_id: dict[str, dict[str, Any]] = {}
    for item in _read_json_list(_data_dir(data_dir) / "review_decisions.json"):
        candidate_id = str(item.get("candidate_id", ""))
        if candidate_id and candidate_id not in decisions_by_candidate_id:
            decisions_by_candidate_id[candidate_id] = item
    return decisions_by_candidate_id


def _post_session_ready_item(
    preview_item: CandidateReviewManualApplicationSessionOutcomeItem,
    draft: dict[str, Any],
    candidate_statuses: dict[str, str],
    decisions_by_candidate_id: dict[str, dict[str, Any]],
) -> CandidateReviewManualApplicationPostSessionVerificationItem:
    candidate_id = preview_item.candidate_id
    actual_status = candidate_statuses.get(candidate_id, "")
    actual_decision = decisions_by_candidate_id.get(candidate_id, {})
    expected_decision_id = _draft_text(draft, "decision_id")
    expected_review_decision = _draft_text(draft, "review_outcome")
    actual_decision_id = str(actual_decision.get("decision_id", ""))
    actual_review_decision = str(actual_decision.get("decision", ""))
    blocking_issues: list[str] = []

    if actual_decision_id != expected_decision_id:
        blocking_issues.append(
            "review_decision_missing"
            if not actual_decision_id
            else "review_decision_id_mismatch"
        )
    if actual_review_decision != expected_review_decision:
        if actual_review_decision:
            blocking_issues.append("review_decision_outcome_mismatch")
    if actual_status != preview_item.projected_candidate_status:
        blocking_issues.append(
            "candidate_status_not_updated"
            if actual_status == preview_item.current_candidate_status
            else "candidate_status_mismatch"
        )

    if not blocking_issues:
        verification_status = "verified_applied"
    elif {
        "review_decision_missing",
        "candidate_status_not_updated",
    }.issubset(blocking_issues):
        verification_status = "manual_application_missing"
    else:
        verification_status = "manual_application_mismatch"

    return CandidateReviewManualApplicationPostSessionVerificationItem(
        candidate_id=candidate_id,
        sequence_number=preview_item.sequence_number,
        verification_lane="ready_action",
        expected_candidate_status=preview_item.projected_candidate_status,
        actual_candidate_status=actual_status,
        expected_review_decision_id=expected_decision_id,
        actual_review_decision_id=actual_decision_id,
        actual_review_decision=actual_review_decision,
        verification_status=verification_status,
        blocking_issues=blocking_issues,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_POST_SESSION_VERIFICATION_BOUNDARY_NOTES
        ),
    )


def _post_session_follow_up_item(
    preview_item: CandidateReviewManualApplicationSessionOutcomeItem,
    candidate_statuses: dict[str, str],
    decisions_by_candidate_id: dict[str, dict[str, Any]],
) -> CandidateReviewManualApplicationPostSessionVerificationItem:
    candidate_id = preview_item.candidate_id
    actual_status = candidate_statuses.get(candidate_id, "")
    actual_decision = decisions_by_candidate_id.get(candidate_id, {})
    actual_decision_id = str(actual_decision.get("decision_id", ""))
    actual_review_decision = str(actual_decision.get("decision", ""))
    blocking_issues: list[str] = []

    if actual_status != "pending_review":
        blocking_issues.append("follow_up_status_changed")
    if actual_decision_id:
        blocking_issues.append("unexpected_review_decision")

    verification_status = (
        "verified_pending_follow_up"
        if not blocking_issues
        else "follow_up_mismatch"
    )
    return CandidateReviewManualApplicationPostSessionVerificationItem(
        candidate_id=candidate_id,
        sequence_number=preview_item.sequence_number,
        verification_lane="follow_up_pending",
        expected_candidate_status="pending_review",
        actual_candidate_status=actual_status,
        actual_review_decision_id=actual_decision_id,
        actual_review_decision=actual_review_decision,
        verification_status=verification_status,
        blocking_issues=blocking_issues,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_POST_SESSION_VERIFICATION_BOUNDARY_NOTES
        ),
    )


def build_pending_candidate_review_manual_application_post_session_verification_report(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationPostSessionVerificationReport:
    preview = build_pending_candidate_review_manual_application_session_outcome_preview(
        drafts,
        preview_data_dir if preview_data_dir is not None else data_dir,
    )
    drafts_by_candidate_id = {
        _draft_text(draft, "candidate_id"): draft for draft in drafts
    }
    candidate_statuses = _candidate_status_by_id(data_dir)
    decisions_by_candidate_id = _review_decision_payloads_by_candidate_id(data_dir)
    items: list[CandidateReviewManualApplicationPostSessionVerificationItem] = []
    for preview_item in preview.items:
        if preview_item.session_lane == "ready_action":
            items.append(
                _post_session_ready_item(
                    preview_item,
                    drafts_by_candidate_id.get(preview_item.candidate_id, {}),
                    candidate_statuses,
                    decisions_by_candidate_id,
                )
            )
        else:
            items.append(
                _post_session_follow_up_item(
                    preview_item,
                    candidate_statuses,
                    decisions_by_candidate_id,
                )
            )

    verified_ready_candidate_ids = [
        item.candidate_id
        for item in items
        if item.verification_lane == "ready_action"
        and item.verification_status == "verified_applied"
    ]
    blocked_ready_candidate_ids = [
        item.candidate_id
        for item in items
        if item.verification_lane == "ready_action"
        and item.verification_status != "verified_applied"
    ]
    verified_follow_up_candidate_ids = [
        item.candidate_id
        for item in items
        if item.verification_lane == "follow_up_pending"
        and item.verification_status == "verified_pending_follow_up"
    ]
    blocked_follow_up_candidate_ids = [
        item.candidate_id
        for item in items
        if item.verification_lane == "follow_up_pending"
        and item.verification_status != "verified_pending_follow_up"
    ]
    post_session_status = (
        "verified"
        if not blocked_ready_candidate_ids and not blocked_follow_up_candidate_ids
        else "blocked"
    )

    return CandidateReviewManualApplicationPostSessionVerificationReport(
        session_id=preview.session_id,
        verification_scope="ready_actions_only_post_session",
        post_session_status=post_session_status,
        verification_item_count=len(items),
        items=items,
        expected_ready_candidate_count=len(preview.ready_applied_candidate_ids),
        verified_ready_candidate_ids=verified_ready_candidate_ids,
        blocked_ready_candidate_ids=blocked_ready_candidate_ids,
        verified_follow_up_candidate_ids=verified_follow_up_candidate_ids,
        blocked_follow_up_candidate_ids=blocked_follow_up_candidate_ids,
        expected_review_decision_delta=preview.projected_review_decision_delta,
        expected_candidate_status_delta=preview.projected_candidate_status_delta,
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_POST_SESSION_VERIFICATION_BOUNDARY_NOTES
        ),
    )


def _append_post_session_verification_items_markdown(
    lines: list[str],
    items: list[CandidateReviewManualApplicationPostSessionVerificationItem],
) -> None:
    if not items:
        lines.append("- `none`")
        return
    for item in items:
        lines.append(f"- `{item.candidate_id}`: `{item.verification_status}`")
        lines.append(
            (
                f"  - Expected status: `{item.expected_candidate_status}`; "
                f"actual status: `{item.actual_candidate_status}`"
            )
        )
        if item.expected_review_decision_id:
            lines.append(
                f"  - Expected review decision id: `{item.expected_review_decision_id}`"
            )
        if item.actual_review_decision_id or item.actual_review_decision:
            lines.append(
                (
                    f"  - Actual review decision: "
                    f"`{item.actual_review_decision_id}` "
                    f"`{item.actual_review_decision}`"
                )
            )
        lines.append("  - Blocking issues:")
        _append_markdown_list(lines, item.blocking_issues, indent="    ")


def render_pending_candidate_review_manual_application_post_session_verification_report_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    report = build_pending_candidate_review_manual_application_post_session_verification_report(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    ready_items = [
        item for item in report.items if item.verification_lane == "ready_action"
    ]
    follow_up_items = [
        item
        for item in report.items
        if item.verification_lane == "follow_up_pending"
    ]
    lines = [
        "# Pending Candidate Review Manual Application Post-Session Verification Report",
        "",
        "## Summary",
        "",
        f"- Session id: `{report.session_id}`",
        f"- Verification scope: `{report.verification_scope}`",
        f"- Post-session status: `{report.post_session_status}`",
        f"- Verification items: `{report.verification_item_count}`",
        f"- Expected ready candidates: `{report.expected_ready_candidate_count}`",
        f"- Verified ready candidates: `{len(report.verified_ready_candidate_ids)}`",
        f"- Blocked ready candidates: `{len(report.blocked_ready_candidate_ids)}`",
        (
            "- Verified follow-up pending candidates: "
            f"`{len(report.verified_follow_up_candidate_ids)}`"
        ),
        (
            "- Blocked follow-up pending candidates: "
            f"`{len(report.blocked_follow_up_candidate_ids)}`"
        ),
        f"- Expected review decision additions: `{report.expected_review_decision_delta}`",
        f"- Expected candidate status updates: `{report.expected_candidate_status_delta}`",
        f"- Applied review decision delta: `{report.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{report.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{report.formal_evidence_delta}`",
        "- Boundary: Post-session verification report is read-only planning metadata.",
        "",
        "## Ready Action Verification",
        "",
    ]
    _append_post_session_verification_items_markdown(lines, ready_items)
    lines.extend(["", "## Follow-Up Pending Verification", ""])
    _append_post_session_verification_items_markdown(lines, follow_up_items)
    lines.extend(["", f"Boundary notes: {' '.join(report.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _reconciliation_action_for_verification_item(
    item: CandidateReviewManualApplicationPostSessionVerificationItem,
) -> tuple[str, list[str]]:
    if item.verification_status == "verified_applied":
        return "verified_complete", ["ready_action_verified"]
    if "review_decision_missing" in item.blocking_issues:
        return "append_missing_review_decision", list(item.blocking_issues)
    if (
        "candidate_status_not_updated" in item.blocking_issues
        or "candidate_status_mismatch" in item.blocking_issues
    ):
        return "correct_candidate_status", list(item.blocking_issues)
    if item.verification_status == "verified_pending_follow_up":
        return "continue_follow_up_processing", ["follow_up_still_pending"]
    if item.verification_lane == "follow_up_pending":
        return "investigate_follow_up_mismatch", list(item.blocking_issues)
    return "correct_candidate_status", list(item.blocking_issues)


def _reconciliation_item_from_verification_item(
    item: CandidateReviewManualApplicationPostSessionVerificationItem,
) -> CandidateReviewManualApplicationReconciliationItem:
    action, reason_codes = _reconciliation_action_for_verification_item(item)
    return CandidateReviewManualApplicationReconciliationItem(
        candidate_id=item.candidate_id,
        sequence_number=item.sequence_number,
        source_verification_lane=item.verification_lane,
        verification_status=item.verification_status,
        recommended_action=action,
        reason_codes=list(dict.fromkeys(reason_codes)),
        blocking_issues=list(item.blocking_issues),
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_RECONCILIATION_BOUNDARY_NOTES),
    )


def build_pending_candidate_review_manual_application_reconciliation_dashboard(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationReconciliationDashboard:
    report = build_pending_candidate_review_manual_application_post_session_verification_report(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    items = [
        _reconciliation_item_from_verification_item(item)
        for item in report.items
    ]
    candidates_by_action = {
        action: [
            item.candidate_id
            for item in items
            if item.recommended_action == action
        ]
        for action in REVIEW_MANUAL_APPLICATION_RECONCILIATION_ACTION_SEQUENCE
    }
    action_counts = {
        action: len(candidate_ids)
        for action, candidate_ids in candidates_by_action.items()
    }
    recommended_processing_order = [
        candidate_id
        for action in REVIEW_MANUAL_APPLICATION_RECONCILIATION_ACTION_SEQUENCE
        for candidate_id in candidates_by_action[action]
    ]
    return CandidateReviewManualApplicationReconciliationDashboard(
        session_id=report.session_id,
        reconciliation_scope="post_session_manual_application",
        post_session_status=report.post_session_status,
        reconciliation_item_count=len(items),
        items=items,
        action_counts=action_counts,
        candidates_by_action=candidates_by_action,
        recommended_action_sequence=list(
            REVIEW_MANUAL_APPLICATION_RECONCILIATION_ACTION_SEQUENCE
        ),
        recommended_processing_order=recommended_processing_order,
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_RECONCILIATION_BOUNDARY_NOTES),
    )


def _reconciliation_item_for_candidate(
    dashboard: CandidateReviewManualApplicationReconciliationDashboard,
    candidate_id: str,
) -> CandidateReviewManualApplicationReconciliationItem:
    return next(item for item in dashboard.items if item.candidate_id == candidate_id)


def render_pending_candidate_review_manual_application_reconciliation_dashboard_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    dashboard = build_pending_candidate_review_manual_application_reconciliation_dashboard(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Reconciliation Dashboard",
        "",
        "## Summary",
        "",
        f"- Session id: `{dashboard.session_id}`",
        f"- Reconciliation scope: `{dashboard.reconciliation_scope}`",
        f"- Post-session status: `{dashboard.post_session_status}`",
        f"- Reconciliation items: `{dashboard.reconciliation_item_count}`",
    ]
    for action in dashboard.recommended_action_sequence:
        lines.append(f"- `{action}`: `{dashboard.action_counts[action]}`")
    lines.extend(
        [
            f"- Applied review decision delta: `{dashboard.applied_review_decision_delta}`",
            f"- Applied candidate status delta: `{dashboard.applied_candidate_status_delta}`",
            f"- Formal evidence delta: `{dashboard.formal_evidence_delta}`",
            "- Boundary: Reconciliation dashboard is read-only planning metadata.",
            "",
            "## Candidates By Action",
        ]
    )

    for action in dashboard.recommended_action_sequence:
        lines.extend(["", f"### {action}", ""])
        candidate_ids = dashboard.candidates_by_action[action]
        if not candidate_ids:
            lines.append("- `none`")
            continue
        for candidate_id in candidate_ids:
            item = _reconciliation_item_for_candidate(dashboard, candidate_id)
            lines.append(f"- `{candidate_id}`")
            lines.append(f"  - Verification status: `{item.verification_status}`")
            lines.append("  - Reason codes:")
            _append_markdown_list(lines, item.reason_codes, indent="    ")
            lines.append("  - Blocking issues:")
            _append_markdown_list(lines, item.blocking_issues, indent="    ")

    lines.extend(["", "## Recommended Processing Order", ""])
    if not dashboard.recommended_processing_order:
        lines.append("No pending reconciliation actions.")
    for index, candidate_id in enumerate(dashboard.recommended_processing_order, 1):
        item = _reconciliation_item_for_candidate(dashboard, candidate_id)
        lines.append(f"{index}. `{candidate_id}`: `{item.recommended_action}`")
    lines.extend(["", f"Boundary notes: {' '.join(dashboard.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _closure_action_for_reconciliation_item(
    item: CandidateReviewManualApplicationReconciliationItem,
) -> tuple[str, str, str]:
    action_map = {
        "append_missing_review_decision": (
            "carry_forward",
            "carry_forward_missing_review_decision",
            "carry_forward_to_next_session",
        ),
        "correct_candidate_status": (
            "carry_forward",
            "carry_forward_candidate_status_correction",
            "carry_forward_to_next_session",
        ),
        "investigate_follow_up_mismatch": (
            "carry_forward",
            "carry_forward_follow_up_investigation",
            "carry_forward_to_next_session",
        ),
        "continue_follow_up_processing": (
            "carry_forward",
            "carry_forward_follow_up_processing",
            "carry_forward_to_next_session",
        ),
        "verified_complete": (
            "session_closure",
            "close_verified_candidate_session_item",
            "ready_to_close",
        ),
    }
    return action_map[item.recommended_action]


def _closure_item_from_reconciliation_item(
    item: CandidateReviewManualApplicationReconciliationItem,
) -> CandidateReviewManualApplicationClosureItem:
    closure_lane, closure_action, closure_status = (
        _closure_action_for_reconciliation_item(item)
    )
    return CandidateReviewManualApplicationClosureItem(
        candidate_id=item.candidate_id,
        sequence_number=item.sequence_number,
        closure_lane=closure_lane,
        closure_action=closure_action,
        closure_status=closure_status,
        source_reconciliation_action=item.recommended_action,
        reason_codes=list(item.reason_codes),
        blocking_issues=list(item.blocking_issues),
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_CLOSURE_BOUNDARY_NOTES),
    )


def _closure_status_for_items(
    items: list[CandidateReviewManualApplicationClosureItem],
) -> str:
    close_count = sum(1 for item in items if item.closure_lane == "session_closure")
    carry_forward_count = sum(
        1 for item in items if item.closure_lane == "carry_forward"
    )
    if close_count and carry_forward_count:
        return "partial_closure_ready"
    if close_count:
        return "session_closure_ready"
    return "carry_forward_required"


def _closure_next_session_setup(
    closure_action_counts: dict[str, int],
) -> list[str]:
    setup_by_action = {
        "carry_forward_missing_review_decision": (
            "prepare_missing_review_decision_application"
        ),
        "carry_forward_candidate_status_correction": (
            "prepare_candidate_status_correction"
        ),
        "carry_forward_follow_up_investigation": (
            "investigate_follow_up_mismatches"
        ),
        "carry_forward_follow_up_processing": (
            "prepare_next_session_for_follow_up_processing"
        ),
        "close_verified_candidate_session_item": (
            "close_verified_candidate_session_items"
        ),
    }
    setup_action_sequence = [
        "close_verified_candidate_session_item",
        "carry_forward_missing_review_decision",
        "carry_forward_candidate_status_correction",
        "carry_forward_follow_up_investigation",
        "carry_forward_follow_up_processing",
    ]
    return [
        setup_by_action[action]
        for action in setup_action_sequence
        if closure_action_counts.get(action, 0)
    ]


def build_pending_candidate_review_manual_application_closure_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationClosurePacket:
    dashboard = build_pending_candidate_review_manual_application_reconciliation_dashboard(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    items = [
        _closure_item_from_reconciliation_item(item)
        for item in dashboard.items
    ]
    candidates_by_closure_action = {
        action: [
            item.candidate_id
            for item in items
            if item.closure_action == action
        ]
        for action in REVIEW_MANUAL_APPLICATION_CLOSURE_ACTION_SEQUENCE
    }
    closure_action_counts = {
        action: len(candidate_ids)
        for action, candidate_ids in candidates_by_closure_action.items()
    }
    close_candidate_ids = [
        item.candidate_id
        for item in items
        if item.closure_lane == "session_closure"
    ]
    carry_forward_candidate_ids = [
        item.candidate_id
        for item in items
        if item.closure_lane == "carry_forward"
    ]
    return CandidateReviewManualApplicationClosurePacket(
        session_id=dashboard.session_id,
        closure_scope="manual_application_session_closure",
        closure_status=_closure_status_for_items(items),
        closure_item_count=len(items),
        items=items,
        close_candidate_ids=close_candidate_ids,
        carry_forward_candidate_ids=carry_forward_candidate_ids,
        closure_action_counts=closure_action_counts,
        candidates_by_closure_action=candidates_by_closure_action,
        recommended_next_session_setup=_closure_next_session_setup(
            closure_action_counts,
        ),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_CLOSURE_BOUNDARY_NOTES),
    )


def _append_closure_items_markdown(
    lines: list[str],
    items: list[CandidateReviewManualApplicationClosureItem],
) -> None:
    if not items:
        lines.append("- `none`")
        return
    for item in items:
        lines.append(f"- `{item.candidate_id}`: `{item.closure_action}`")
        lines.append(f"  - Closure status: `{item.closure_status}`")
        lines.append(
            f"  - Source reconciliation action: `{item.source_reconciliation_action}`"
        )
        lines.append("  - Reason codes:")
        _append_markdown_list(lines, item.reason_codes, indent="    ")
        lines.append("  - Blocking issues:")
        _append_markdown_list(lines, item.blocking_issues, indent="    ")


def render_pending_candidate_review_manual_application_closure_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_closure_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    closure_items = [
        item for item in packet.items if item.closure_lane == "session_closure"
    ]
    carry_forward_items = [
        item for item in packet.items if item.closure_lane == "carry_forward"
    ]
    lines = [
        "# Pending Candidate Review Manual Application Closure Packet",
        "",
        "## Summary",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Closure scope: `{packet.closure_scope}`",
        f"- Closure status: `{packet.closure_status}`",
        f"- Closure items: `{packet.closure_item_count}`",
        f"- Close candidates: `{len(packet.close_candidate_ids)}`",
        f"- Carry-forward candidates: `{len(packet.carry_forward_candidate_ids)}`",
    ]
    for action in REVIEW_MANUAL_APPLICATION_CLOSURE_ACTION_SEQUENCE:
        lines.append(f"- `{action}`: `{packet.closure_action_counts[action]}`")
    lines.extend(
        [
            f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
            f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
            f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
            "- Boundary: Closure packet is read-only planning metadata.",
            "",
            "## Session Closure Candidates",
            "",
        ]
    )
    _append_closure_items_markdown(lines, closure_items)
    lines.extend(["", "## Carry Forward Candidates", ""])
    _append_closure_items_markdown(lines, carry_forward_items)

    lines.extend(["", "## Recommended Next Session Setup", ""])
    if not packet.recommended_next_session_setup:
        lines.append("- [ ] none")
    for item in packet.recommended_next_session_setup:
        lines.append(f"- [ ] {item}")
    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_starter_spec_for_closure_action(
    closure_action: str,
) -> tuple[str, str, list[str]]:
    specs = {
        "carry_forward_missing_review_decision": (
            "missing_review_decision",
            "prepare_missing_review_decision_application",
            [
                "recover_ready_manual_application_packet",
                "append_missing_review_decision",
                "rerun_post_session_verification",
                "rerun_reconciliation_dashboard",
                "rerun_closure_packet",
            ],
        ),
        "carry_forward_candidate_status_correction": (
            "candidate_status_correction",
            "prepare_candidate_status_correction",
            [
                "verify_review_decision_present",
                "apply_candidate_status_patch",
                "rerun_post_session_verification",
                "rerun_reconciliation_dashboard",
                "rerun_closure_packet",
            ],
        ),
        "carry_forward_follow_up_investigation": (
            "follow_up_mismatch_investigation",
            "investigate_follow_up_mismatch",
            [
                "inspect_unexpected_follow_up_change",
                "resolve_or_revert_manual_mismatch",
                "rerun_post_session_verification",
                "rerun_reconciliation_dashboard",
                "rerun_closure_packet",
            ],
        ),
        "carry_forward_follow_up_processing": (
            "follow_up_processing",
            "continue_follow_up_processing",
            [
                "fill_or_revise_review_input_template",
                "run_draft_validation",
                "run_application_guard",
                "rerun_manual_action_dashboard",
                "prepare_next_session_packet",
            ],
        ),
    }
    return specs[closure_action]


def _next_session_item_from_closure_item(
    item: CandidateReviewManualApplicationClosureItem,
) -> CandidateReviewManualApplicationNextSessionStarterItem:
    starter_lane, starter_action, checklist = (
        _next_session_starter_spec_for_closure_action(item.closure_action)
    )
    return CandidateReviewManualApplicationNextSessionStarterItem(
        candidate_id=item.candidate_id,
        sequence_number=item.sequence_number,
        starter_lane=starter_lane,
        starter_action=starter_action,
        starter_status="ready_to_start",
        source_closure_action=item.closure_action,
        checklist=checklist,
        reason_codes=list(item.reason_codes),
        blocking_issues=list(item.blocking_issues),
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_NEXT_SESSION_BOUNDARY_NOTES),
    )


def _next_session_kickoff_checklist(
    closure_packet: CandidateReviewManualApplicationClosurePacket,
    starter_item_count: int,
) -> list[str]:
    checklist: list[str] = []
    if closure_packet.close_candidate_ids:
        checklist.append("close_verified_candidate_session_items")
    if starter_item_count:
        checklist.extend(
            [
                "review_carry_forward_items",
                "run_required_starter_lane_checklists",
                "rerun_next_session_starter",
            ]
        )
    return checklist or ["no_carry_forward_items"]


def build_pending_candidate_review_manual_application_next_session_starter(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionStarter:
    closure_packet = build_pending_candidate_review_manual_application_closure_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    items = [
        _next_session_item_from_closure_item(item)
        for item in closure_packet.items
        if item.closure_lane == "carry_forward"
    ]
    candidates_by_starter_lane = {
        lane: [
            item.candidate_id
            for item in items
            if item.starter_lane == lane
        ]
        for lane in REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LANES
    }
    starter_lane_counts = {
        lane: len(candidate_ids)
        for lane, candidate_ids in candidates_by_starter_lane.items()
    }
    recommended_start_order = [
        candidate_id
        for lane in REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LANES
        for candidate_id in candidates_by_starter_lane[lane]
    ]
    return CandidateReviewManualApplicationNextSessionStarter(
        session_id=closure_packet.session_id,
        starter_scope="manual_application_next_session",
        starter_status=(
            "ready_for_next_manual_session"
            if items
            else "no_carry_forward_items"
        ),
        starter_item_count=len(items),
        items=items,
        starter_lane_counts=starter_lane_counts,
        candidates_by_starter_lane=candidates_by_starter_lane,
        recommended_start_order=recommended_start_order,
        kickoff_checklist=_next_session_kickoff_checklist(
            closure_packet,
            len(items),
        ),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_NEXT_SESSION_BOUNDARY_NOTES),
    )


def _starter_item_for_candidate(
    starter: CandidateReviewManualApplicationNextSessionStarter,
    candidate_id: str,
) -> CandidateReviewManualApplicationNextSessionStarterItem:
    return next(item for item in starter.items if item.candidate_id == candidate_id)


def render_pending_candidate_review_manual_application_next_session_starter_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    starter = build_pending_candidate_review_manual_application_next_session_starter(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Starter",
        "",
        "## Summary",
        "",
        f"- Session id: `{starter.session_id}`",
        f"- Starter scope: `{starter.starter_scope}`",
        f"- Starter status: `{starter.starter_status}`",
        f"- Starter items: `{starter.starter_item_count}`",
    ]
    for lane in REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LANES:
        lines.append(f"- `{lane}`: `{starter.starter_lane_counts[lane]}`")
    lines.extend(
        [
            f"- Applied review decision delta: `{starter.applied_review_decision_delta}`",
            f"- Applied candidate status delta: `{starter.applied_candidate_status_delta}`",
            f"- Formal evidence delta: `{starter.formal_evidence_delta}`",
            "- Boundary: Next-session starter is read-only planning metadata.",
            "",
            "## Candidates By Starter Lane",
        ]
    )
    for lane in REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LANES:
        lines.extend(["", f"### {lane}", ""])
        candidate_ids = starter.candidates_by_starter_lane[lane]
        if not candidate_ids:
            lines.append("- `none`")
            continue
        for candidate_id in candidate_ids:
            item = _starter_item_for_candidate(starter, candidate_id)
            lines.append(f"- `{candidate_id}`: `{item.starter_action}`")
            lines.append(f"  - Starter status: `{item.starter_status}`")
            lines.append(f"  - Source closure action: `{item.source_closure_action}`")
            lines.append("  - Checklist:")
            for checklist_item in item.checklist:
                lines.append(f"    - [ ] {checklist_item}")
            lines.append("  - Reason codes:")
            _append_markdown_list(lines, item.reason_codes, indent="    ")
            lines.append("  - Blocking issues:")
            _append_markdown_list(lines, item.blocking_issues, indent="    ")

    lines.extend(["", "## Recommended Start Order", ""])
    if not starter.recommended_start_order:
        lines.append("No carry-forward candidates for the next manual session.")
    for index, candidate_id in enumerate(starter.recommended_start_order, 1):
        item = _starter_item_for_candidate(starter, candidate_id)
        lines.append(f"{index}. `{candidate_id}`: `{item.starter_action}`")

    lines.extend(["", "## Kickoff Checklist", ""])
    for item in starter.kickoff_checklist:
        lines.append(f"- [ ] {item}")
    lines.extend(["", f"Boundary notes: {' '.join(starter.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_packet_lane_for_starter_lane(starter_lane: str) -> str:
    if starter_lane in REVIEW_MANUAL_APPLICATION_NEXT_SESSION_PACKET_CORRECTION_LANES:
        return "correction_queue"
    if starter_lane == "follow_up_processing":
        return "follow_up_queue"
    raise SourceIntakeError(f"unsupported next-session starter lane: {starter_lane}")


def _next_session_packet_item_from_starter_item(
    item: CandidateReviewManualApplicationNextSessionStarterItem,
) -> CandidateReviewManualApplicationNextSessionPacketItem:
    return CandidateReviewManualApplicationNextSessionPacketItem(
        candidate_id=item.candidate_id,
        sequence_number=item.sequence_number,
        packet_lane=_next_session_packet_lane_for_starter_lane(item.starter_lane),
        starter_lane=item.starter_lane,
        packet_action=item.starter_action,
        starter_action=item.starter_action,
        packet_status="ready_for_manual_action",
        source_closure_action=item.source_closure_action,
        checklist=list(item.checklist),
        reason_codes=list(item.reason_codes),
        blocking_issues=list(item.blocking_issues),
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_PACKET_BOUNDARY_NOTES
        ),
    )


def build_pending_candidate_review_manual_application_next_session_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionPacket:
    starter = build_pending_candidate_review_manual_application_next_session_starter(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    items = [
        _next_session_packet_item_from_starter_item(item)
        for item in starter.items
    ]
    correction_queue = [
        item for item in items if item.packet_lane == "correction_queue"
    ]
    follow_up_queue = [
        item for item in items if item.packet_lane == "follow_up_queue"
    ]
    correction_candidate_ids = [
        item.candidate_id for item in correction_queue
    ]
    follow_up_candidate_ids = [
        item.candidate_id for item in follow_up_queue
    ]
    return CandidateReviewManualApplicationNextSessionPacket(
        session_id=starter.session_id,
        packet_scope="manual_application_next_session_packet",
        packet_status=(
            "ready_for_next_manual_session"
            if items
            else "no_next_session_actions"
        ),
        packet_item_count=len(items),
        items=items,
        correction_queue=correction_queue,
        follow_up_queue=follow_up_queue,
        correction_candidate_ids=correction_candidate_ids,
        follow_up_candidate_ids=follow_up_candidate_ids,
        recommended_processing_order=(
            correction_candidate_ids + follow_up_candidate_ids
        ),
        kickoff_checklist=list(starter.kickoff_checklist),
        post_session_verification=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_PACKET_POST_SESSION_VERIFICATION
        ),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_PACKET_BOUNDARY_NOTES
        ),
    )


def _append_next_session_packet_queue_markdown(
    lines: list[str],
    items: list[CandidateReviewManualApplicationNextSessionPacketItem],
) -> None:
    if not items:
        lines.append("- `none`")
        return
    for item in items:
        lines.append(f"- `{item.candidate_id}`: `{item.packet_action}`")
        lines.append(f"  - Packet status: `{item.packet_status}`")
        lines.append(f"  - Starter lane: `{item.starter_lane}`")
        lines.append(f"  - Source closure action: `{item.source_closure_action}`")
        lines.append("  - Checklist:")
        for checklist_item in item.checklist:
            lines.append(f"    - [ ] {checklist_item}")
        lines.append("  - Reason codes:")
        _append_markdown_list(lines, item.reason_codes, indent="    ")
        lines.append("  - Blocking issues:")
        _append_markdown_list(lines, item.blocking_issues, indent="    ")


def _next_session_packet_item_for_candidate(
    packet: CandidateReviewManualApplicationNextSessionPacket,
    candidate_id: str,
) -> CandidateReviewManualApplicationNextSessionPacketItem:
    return next(item for item in packet.items if item.candidate_id == candidate_id)


def render_pending_candidate_review_manual_application_next_session_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_next_session_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Packet",
        "",
        "## Summary",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Packet scope: `{packet.packet_scope}`",
        f"- Packet status: `{packet.packet_status}`",
        f"- Packet items: `{packet.packet_item_count}`",
        f"- Correction queue: `{len(packet.correction_queue)}`",
        f"- Follow-up queue: `{len(packet.follow_up_queue)}`",
        f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
        "- Boundary: Next-session packet is read-only planning metadata.",
        "",
        "## Correction Queue",
        "",
    ]
    _append_next_session_packet_queue_markdown(lines, packet.correction_queue)
    lines.extend(["", "## Follow-Up Queue", ""])
    _append_next_session_packet_queue_markdown(lines, packet.follow_up_queue)

    lines.extend(["", "## Recommended Processing Order", ""])
    if not packet.recommended_processing_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(packet.recommended_processing_order, 1):
        item = _next_session_packet_item_for_candidate(packet, candidate_id)
        lines.append(f"{index}. `{candidate_id}`: `{item.packet_action}`")

    lines.extend(["", "## Kickoff Checklist", ""])
    for item in packet.kickoff_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Session Verification", ""])
    for item in packet.post_session_verification:
        lines.append(f"- [ ] {item}")
    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_audit_coverage_checks(
    closure_packet: CandidateReviewManualApplicationClosurePacket,
    starter: CandidateReviewManualApplicationNextSessionStarter,
    packet: CandidateReviewManualApplicationNextSessionPacket,
) -> dict[str, str]:
    return {
        "closure_carry_forward_to_starter": (
            "covered"
            if closure_packet.carry_forward_candidate_ids
            == starter.recommended_start_order
            else "missing"
        ),
        "starter_to_packet_order": (
            "covered"
            if starter.recommended_start_order
            == packet.recommended_processing_order
            else "missing"
        ),
        "correction_queue": (
            "covered"
            if len(packet.correction_candidate_ids) == len(packet.correction_queue)
            else "missing"
        ),
        "follow_up_queue": (
            "covered"
            if len(packet.follow_up_candidate_ids) == len(packet.follow_up_queue)
            else "missing"
        ),
        "kickoff_checklist": (
            "covered" if packet.kickoff_checklist else "missing"
        ),
        "post_session_verification": (
            "covered" if packet.post_session_verification else "missing"
        ),
    }


def _next_session_audit_status(
    packet: CandidateReviewManualApplicationNextSessionPacket,
    coverage_checks: dict[str, str],
) -> str:
    if any(status != "covered" for status in coverage_checks.values()):
        return "audit_blocked"
    if packet.packet_item_count:
        return "ready_for_next_manual_session"
    return "no_next_session_actions"


def _next_session_audit_shortest_next_actions(
    closure_packet: CandidateReviewManualApplicationClosurePacket,
    packet: CandidateReviewManualApplicationNextSessionPacket,
) -> list[str]:
    actions: list[str] = []
    if closure_packet.close_candidate_ids:
        actions.append("close_verified_candidate_session_items")
    if packet.correction_queue:
        actions.append("apply_correction_queue_first")
    if packet.follow_up_queue:
        actions.append("continue_follow_up_queue")
    if not actions:
        return ["no_next_session_actions"]
    actions.append("rerun_post_session_verification_chain")
    return actions


def build_pending_candidate_review_manual_application_next_session_audit_summary(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionAuditSummary:
    closure_packet = build_pending_candidate_review_manual_application_closure_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    starter = build_pending_candidate_review_manual_application_next_session_starter(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    packet = build_pending_candidate_review_manual_application_next_session_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    coverage_checks = _next_session_audit_coverage_checks(
        closure_packet,
        starter,
        packet,
    )
    return CandidateReviewManualApplicationNextSessionAuditSummary(
        session_id=packet.session_id,
        audit_scope="manual_application_next_session_audit",
        audit_status=_next_session_audit_status(packet, coverage_checks),
        closure_status=closure_packet.closure_status,
        starter_status=starter.starter_status,
        packet_status=packet.packet_status,
        closure_item_count=closure_packet.closure_item_count,
        starter_item_count=starter.starter_item_count,
        packet_item_count=packet.packet_item_count,
        correction_queue_count=len(packet.correction_queue),
        follow_up_queue_count=len(packet.follow_up_queue),
        correction_candidate_ids=list(packet.correction_candidate_ids),
        follow_up_candidate_ids=list(packet.follow_up_candidate_ids),
        recommended_processing_order=list(packet.recommended_processing_order),
        shortest_next_actions=_next_session_audit_shortest_next_actions(
            closure_packet,
            packet,
        ),
        coverage_checks=coverage_checks,
        kickoff_checklist=list(packet.kickoff_checklist),
        post_session_verification=list(packet.post_session_verification),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_NEXT_SESSION_AUDIT_BOUNDARY_NOTES),
    )


def render_pending_candidate_review_manual_application_next_session_audit_summary_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    summary = build_pending_candidate_review_manual_application_next_session_audit_summary(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Audit Summary",
        "",
        "## Summary",
        "",
        f"- Session id: `{summary.session_id}`",
        f"- Audit scope: `{summary.audit_scope}`",
        f"- Audit status: `{summary.audit_status}`",
        f"- Closure status: `{summary.closure_status}`",
        f"- Starter status: `{summary.starter_status}`",
        f"- Packet status: `{summary.packet_status}`",
        f"- Closure items: `{summary.closure_item_count}`",
        f"- Starter items: `{summary.starter_item_count}`",
        f"- Packet items: `{summary.packet_item_count}`",
        f"- Correction queue: `{summary.correction_queue_count}`",
        f"- Follow-up queue: `{summary.follow_up_queue_count}`",
        f"- Applied review decision delta: `{summary.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{summary.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{summary.formal_evidence_delta}`",
        "- Boundary: Next-session audit summary is read-only planning metadata.",
        "",
        "## Coverage Checks",
        "",
    ]
    for check, status in summary.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Shortest Next Actions", ""])
    for action in summary.shortest_next_actions:
        lines.append(f"- [ ] {action}")

    lines.extend(["", "## Recommended Processing Order", ""])
    if not summary.recommended_processing_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(summary.recommended_processing_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Kickoff Checklist", ""])
    for item in summary.kickoff_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Session Verification", ""])
    for item in summary.post_session_verification:
        lines.append(f"- [ ] {item}")

    lines.extend(["", f"Boundary notes: {' '.join(summary.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_operator_targets_for_action(
    action: str,
    summary: CandidateReviewManualApplicationNextSessionAuditSummary,
    closure_packet: CandidateReviewManualApplicationClosurePacket,
) -> list[str]:
    if action == "close_verified_candidate_session_items":
        return list(closure_packet.close_candidate_ids)
    if action == "apply_correction_queue_first":
        return list(summary.correction_candidate_ids)
    if action == "continue_follow_up_queue":
        return list(summary.follow_up_candidate_ids)
    if action == "rerun_post_session_verification_chain":
        return list(closure_packet.close_candidate_ids) + list(
            summary.recommended_processing_order
        )
    return []


def _next_session_operator_item_spec(
    action: str,
    summary: CandidateReviewManualApplicationNextSessionAuditSummary,
) -> tuple[list[str], list[str], list[str]]:
    if action == "close_verified_candidate_session_items":
        return (
            ["closure_packet_has_verified_items", "session_item_verified_complete"],
            [
                "open_closure_packet",
                "close_verified_items_before_follow_up",
                "confirm_no_candidate_or_evidence_auto_write",
            ],
            [
                "rerun_closure_packet",
                "rerun_next_session_audit_summary",
            ],
        )
    if action == "apply_correction_queue_first":
        return (
            ["next_session_audit_ready", "correction_queue_not_empty"],
            [
                "open_next_session_packet",
                "apply_correction_candidates_in_recommended_order",
                "finish_corrections_before_follow_up",
            ],
            list(summary.post_session_verification),
        )
    if action == "continue_follow_up_queue":
        return (
            ["next_session_audit_ready", "follow_up_queue_not_empty"],
            [
                "open_next_session_packet",
                "fill_or_revise_review_input_templates",
                "run_draft_validation",
                "run_application_guard",
                "prepare_next_session_packet",
            ],
            list(summary.post_session_verification),
        )
    if action == "rerun_post_session_verification_chain":
        return (
            ["manual_actions_completed", "post_session_verification_available"],
            list(summary.post_session_verification),
            [
                "confirm_review_decision_delta_zero",
                "confirm_candidate_status_delta_zero",
                "confirm_formal_evidence_delta_zero",
            ],
        )
    return (
        ["no_next_session_actions"],
        ["no_operator_action_required"],
        ["confirm_next_session_operator_checklist_empty"],
    )


def _next_session_operator_checklist_status(
    summary: CandidateReviewManualApplicationNextSessionAuditSummary,
) -> str:
    if summary.shortest_next_actions == ["no_next_session_actions"]:
        return "no_operator_actions"
    if summary.audit_status == "ready_for_next_manual_session":
        return "ready_for_operator"
    return "operator_blocked"


def _next_session_operator_checklist_item(
    action: str,
    sequence_number: int,
    summary: CandidateReviewManualApplicationNextSessionAuditSummary,
    closure_packet: CandidateReviewManualApplicationClosurePacket,
) -> CandidateReviewManualApplicationNextSessionOperatorChecklistItem:
    ready_criteria, operator_checklist, verification_checklist = (
        _next_session_operator_item_spec(action, summary)
    )
    return CandidateReviewManualApplicationNextSessionOperatorChecklistItem(
        action_id=f"next_session_operator_action_{sequence_number:03d}",
        sequence_number=sequence_number,
        operator_action=action,
        action_status="ready_for_operator",
        target_candidates=_next_session_operator_targets_for_action(
            action,
            summary,
            closure_packet,
        ),
        ready_criteria=ready_criteria,
        operator_checklist=operator_checklist,
        verification_checklist=verification_checklist,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_OPERATOR_BOUNDARY_NOTES
        ),
    )


def build_pending_candidate_review_manual_application_next_session_operator_checklist(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionOperatorChecklist:
    summary = build_pending_candidate_review_manual_application_next_session_audit_summary(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    closure_packet = build_pending_candidate_review_manual_application_closure_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    items = [
        _next_session_operator_checklist_item(
            action,
            sequence_number,
            summary,
            closure_packet,
        )
        for sequence_number, action in enumerate(summary.shortest_next_actions, 1)
    ]
    return CandidateReviewManualApplicationNextSessionOperatorChecklist(
        session_id=summary.session_id,
        checklist_scope="manual_application_next_session_operator",
        checklist_status=_next_session_operator_checklist_status(summary),
        checklist_item_count=len(items),
        items=items,
        action_sequence=[item.operator_action for item in items],
        target_candidates_by_action={
            item.operator_action: list(item.target_candidates) for item in items
        },
        recommended_processing_order=list(summary.recommended_processing_order),
        kickoff_checklist=list(summary.kickoff_checklist),
        verification_checklist=list(summary.post_session_verification),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_OPERATOR_BOUNDARY_NOTES
        ),
    )


def _append_operator_checklist_item_markdown(
    lines: list[str],
    item: CandidateReviewManualApplicationNextSessionOperatorChecklistItem,
) -> None:
    lines.extend(
        [
            f"### {item.sequence_number}. {item.operator_action}",
            "",
            f"- Action id: `{item.action_id}`",
            f"- Action status: `{item.action_status}`",
            "- Target candidates:",
        ]
    )
    _append_markdown_list(lines, item.target_candidates, indent="  ")
    lines.append("- Ready criteria:")
    _append_markdown_list(lines, item.ready_criteria, indent="  ")
    lines.append("- Operator checklist:")
    for checklist_item in item.operator_checklist:
        lines.append(f"  - [ ] {checklist_item}")
    lines.append("- Verification checklist:")
    for checklist_item in item.verification_checklist:
        lines.append(f"  - [ ] {checklist_item}")


def render_pending_candidate_review_manual_application_next_session_operator_checklist_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    checklist = build_pending_candidate_review_manual_application_next_session_operator_checklist(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Operator Checklist",
        "",
        "## Summary",
        "",
        f"- Session id: `{checklist.session_id}`",
        f"- Checklist scope: `{checklist.checklist_scope}`",
        f"- Checklist status: `{checklist.checklist_status}`",
        f"- Checklist items: `{checklist.checklist_item_count}`",
        f"- Applied review decision delta: `{checklist.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{checklist.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{checklist.formal_evidence_delta}`",
        "- Boundary: Next-session operator checklist is read-only planning metadata.",
        "",
        "## Operator Actions",
        "",
    ]
    if not checklist.items:
        lines.append("- `none`")
    for item in checklist.items:
        _append_operator_checklist_item_markdown(lines, item)
        lines.append("")

    lines.extend(["## Recommended Processing Order", ""])
    if not checklist.recommended_processing_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(checklist.recommended_processing_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Kickoff Checklist", ""])
    for item in checklist.kickoff_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Verification Checklist", ""])
    for item in checklist.verification_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", f"Boundary notes: {' '.join(checklist.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _dedupe_preserving_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _next_session_execution_handoff_status(
    checklist: CandidateReviewManualApplicationNextSessionOperatorChecklist,
) -> str:
    if checklist.checklist_status == "ready_for_operator":
        return "ready_for_execution"
    if checklist.checklist_status == "no_operator_actions":
        return "no_execution_actions"
    return "execution_blocked"


def _next_session_execution_blocked_conditions(
    checklist: CandidateReviewManualApplicationNextSessionOperatorChecklist,
) -> list[str]:
    if checklist.checklist_status == "ready_for_operator":
        return []
    if checklist.checklist_status == "no_operator_actions":
        return ["no_operator_actions"]
    return ["operator_checklist_blocked"]


def build_pending_candidate_review_manual_application_next_session_execution_handoff(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionExecutionHandoff:
    checklist = build_pending_candidate_review_manual_application_next_session_operator_checklist(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    first_item = checklist.items[0] if checklist.items else None
    first_action = first_item.operator_action if first_item else "none"
    ready_conditions = (
        _dedupe_preserving_order(
            ["operator_checklist_ready"] + list(first_item.ready_criteria)
        )
        if first_item
        else []
    )
    target_candidates = _dedupe_preserving_order(
        [
            candidate_id
            for action in checklist.action_sequence
            for candidate_id in checklist.target_candidates_by_action.get(
                action,
                [],
            )
        ]
    )
    return CandidateReviewManualApplicationNextSessionExecutionHandoff(
        session_id=checklist.session_id,
        handoff_scope="manual_application_next_session_execution",
        handoff_status=_next_session_execution_handoff_status(checklist),
        first_action=first_action,
        first_action_targets=(
            list(first_item.target_candidates) if first_item else []
        ),
        ready_conditions=ready_conditions,
        blocked_conditions=_next_session_execution_blocked_conditions(checklist),
        action_sequence=list(checklist.action_sequence),
        target_candidates=target_candidates,
        recommended_processing_order=list(checklist.recommended_processing_order),
        kickoff_checklist=list(checklist.kickoff_checklist),
        verification_chain=list(checklist.verification_checklist),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_EXECUTION_BOUNDARY_NOTES
        ),
    )


def _append_code_markdown_list(lines: list[str], values: list[str]) -> None:
    if not values:
        lines.append("- `none`")
        return
    for value in values:
        lines.append(f"- `{value}`")


def render_pending_candidate_review_manual_application_next_session_execution_handoff_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    handoff = build_pending_candidate_review_manual_application_next_session_execution_handoff(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Execution Handoff",
        "",
        "## Summary",
        "",
        f"- Session id: `{handoff.session_id}`",
        f"- Handoff scope: `{handoff.handoff_scope}`",
        f"- Handoff status: `{handoff.handoff_status}`",
        f"- First action: `{handoff.first_action}`",
        f"- Applied review decision delta: `{handoff.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{handoff.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{handoff.formal_evidence_delta}`",
        "- Boundary: Next-session execution handoff is read-only planning metadata.",
        "",
        "## First Action Targets",
        "",
    ]
    _append_code_markdown_list(lines, handoff.first_action_targets)
    lines.extend(["", "## Ready Conditions", ""])
    _append_code_markdown_list(lines, handoff.ready_conditions)
    lines.extend(["", "## Blocked Conditions", ""])
    _append_code_markdown_list(lines, handoff.blocked_conditions)

    lines.extend(["", "## Action Sequence", ""])
    if not handoff.action_sequence:
        lines.append("- `none`")
    for index, action in enumerate(handoff.action_sequence, 1):
        lines.append(f"{index}. `{action}`")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, handoff.target_candidates)

    lines.extend(["", "## Recommended Processing Order", ""])
    if not handoff.recommended_processing_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(handoff.recommended_processing_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Kickoff Checklist", ""])
    for item in handoff.kickoff_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Verification Chain", ""])
    for item in handoff.verification_chain:
        lines.append(f"- [ ] {item}")

    lines.extend(["", f"Boundary notes: {' '.join(handoff.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_completion_criteria_status(
    handoff: CandidateReviewManualApplicationNextSessionExecutionHandoff,
) -> str:
    if handoff.handoff_status == "ready_for_execution":
        return "ready_for_completion_check"
    if handoff.handoff_status == "no_execution_actions":
        return "no_completion_actions"
    return "completion_blocked"


def _next_session_completion_done_conditions(
    handoff: CandidateReviewManualApplicationNextSessionExecutionHandoff,
) -> list[str]:
    if handoff.handoff_status == "no_execution_actions":
        return ["no_next_session_actions_remaining"]
    return [
        "complete_first_action",
        "complete_remaining_action_sequence",
        "run_verification_entrypoints",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]


def _next_session_completion_retry_conditions(
    handoff: CandidateReviewManualApplicationNextSessionExecutionHandoff,
) -> list[str]:
    if handoff.handoff_status == "no_execution_actions":
        return ["rerun_completion_criteria_if_new_actions_appear"]
    return [
        "retry_first_action_if_verification_fails",
        "rerun_execution_handoff_after_manual_changes",
    ]


def build_pending_candidate_review_manual_application_next_session_completion_criteria(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionCompletionCriteria:
    handoff = build_pending_candidate_review_manual_application_next_session_execution_handoff(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    return CandidateReviewManualApplicationNextSessionCompletionCriteria(
        session_id=handoff.session_id,
        criteria_scope="manual_application_next_session_completion",
        criteria_status=_next_session_completion_criteria_status(handoff),
        first_action=handoff.first_action,
        first_action_targets=list(handoff.first_action_targets),
        target_candidates=list(handoff.target_candidates),
        done_conditions=_next_session_completion_done_conditions(handoff),
        blocked_conditions=list(handoff.blocked_conditions),
        retry_conditions=_next_session_completion_retry_conditions(handoff),
        verification_entrypoints=list(handoff.verification_chain),
        action_sequence=list(handoff.action_sequence),
        recommended_processing_order=list(handoff.recommended_processing_order),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_COMPLETION_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_completion_criteria_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    criteria = build_pending_candidate_review_manual_application_next_session_completion_criteria(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Completion Criteria",
        "",
        "## Summary",
        "",
        f"- Session id: `{criteria.session_id}`",
        f"- Criteria scope: `{criteria.criteria_scope}`",
        f"- Criteria status: `{criteria.criteria_status}`",
        f"- First action: `{criteria.first_action}`",
        f"- Applied review decision delta: `{criteria.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{criteria.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{criteria.formal_evidence_delta}`",
        "- Boundary: Next-session completion criteria is read-only planning metadata.",
        "",
        "## First Action Targets",
        "",
    ]
    _append_code_markdown_list(lines, criteria.first_action_targets)
    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, criteria.target_candidates)

    lines.extend(["", "## Done Conditions", ""])
    _append_code_markdown_list(lines, criteria.done_conditions)
    lines.extend(["", "## Blocked Conditions", ""])
    _append_code_markdown_list(lines, criteria.blocked_conditions)
    lines.extend(["", "## Retry Conditions", ""])
    _append_code_markdown_list(lines, criteria.retry_conditions)

    lines.extend(["", "## Action Sequence", ""])
    if not criteria.action_sequence:
        lines.append("- `none`")
    for index, action in enumerate(criteria.action_sequence, 1):
        lines.append(f"{index}. `{action}`")

    lines.extend(["", "## Recommended Processing Order", ""])
    if not criteria.recommended_processing_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(criteria.recommended_processing_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Entrypoints", ""])
    for item in criteria.verification_entrypoints:
        lines.append(f"- [ ] {item}")

    lines.extend(["", f"Boundary notes: {' '.join(criteria.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_retry_failure_entrypoints(
    retry_conditions: list[str],
) -> list[str]:
    entrypoint_by_condition = {
        "retry_first_action_if_verification_fails": (
            "first_action_verification_failed"
        ),
        "rerun_execution_handoff_after_manual_changes": (
            "execution_handoff_stale_after_manual_changes"
        ),
        "rerun_completion_criteria_if_new_actions_appear": (
            "new_next_session_actions_detected"
        ),
    }
    return [
        entrypoint_by_condition[condition]
        for condition in retry_conditions
        if condition in entrypoint_by_condition
    ]


def _next_session_retry_sequence(
    retry_conditions: list[str],
) -> list[str]:
    sequence = list(retry_conditions)
    if "rerun_completion_criteria" not in sequence:
        sequence.append("rerun_completion_criteria")
    return sequence


def _next_session_retry_status(
    criteria: CandidateReviewManualApplicationNextSessionCompletionCriteria,
) -> str:
    if criteria.retry_conditions:
        return "ready_for_retry_planning"
    return "no_retry_actions"


def build_pending_candidate_review_manual_application_next_session_retry_planner(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionRetryPlanner:
    criteria = build_pending_candidate_review_manual_application_next_session_completion_criteria(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    return CandidateReviewManualApplicationNextSessionRetryPlanner(
        session_id=criteria.session_id,
        retry_scope="manual_application_next_session_retry",
        retry_status=_next_session_retry_status(criteria),
        first_action=criteria.first_action,
        first_action_targets=list(criteria.first_action_targets),
        failure_entrypoints=_next_session_retry_failure_entrypoints(
            criteria.retry_conditions
        ),
        retry_conditions=list(criteria.retry_conditions),
        retry_sequence=_next_session_retry_sequence(criteria.retry_conditions),
        target_candidates=list(criteria.target_candidates),
        verification_entrypoints=list(criteria.verification_entrypoints),
        return_to_handoff_path=[
            "render_next_session_execution_handoff",
            "render_next_session_completion_criteria",
        ],
        recommended_processing_order=list(criteria.recommended_processing_order),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(REVIEW_MANUAL_APPLICATION_NEXT_SESSION_RETRY_BOUNDARY_NOTES),
    )


def render_pending_candidate_review_manual_application_next_session_retry_planner_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    planner = build_pending_candidate_review_manual_application_next_session_retry_planner(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Retry Planner",
        "",
        "## Summary",
        "",
        f"- Session id: `{planner.session_id}`",
        f"- Retry scope: `{planner.retry_scope}`",
        f"- Retry status: `{planner.retry_status}`",
        f"- First action: `{planner.first_action}`",
        f"- Applied review decision delta: `{planner.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{planner.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{planner.formal_evidence_delta}`",
        "- Boundary: Next-session retry planner is read-only planning metadata.",
        "",
        "## First Action Targets",
        "",
    ]
    _append_code_markdown_list(lines, planner.first_action_targets)
    lines.extend(["", "## Failure Entrypoints", ""])
    _append_code_markdown_list(lines, planner.failure_entrypoints)
    lines.extend(["", "## Retry Conditions", ""])
    _append_code_markdown_list(lines, planner.retry_conditions)

    lines.extend(["", "## Retry Sequence", ""])
    for item in planner.retry_sequence:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, planner.target_candidates)

    lines.extend(["", "## Recommended Processing Order", ""])
    if not planner.recommended_processing_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(planner.recommended_processing_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Entrypoints", ""])
    for item in planner.verification_entrypoints:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Return To Handoff Path", ""])
    for item in planner.return_to_handoff_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", f"Boundary notes: {' '.join(planner.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_final_readiness_conditions(
    criteria: CandidateReviewManualApplicationNextSessionCompletionCriteria,
    planner: CandidateReviewManualApplicationNextSessionRetryPlanner,
) -> list[str]:
    conditions: list[str] = []
    if criteria.criteria_status == "ready_for_completion_check":
        conditions.append("completion_criteria_ready")
    if planner.retry_status == "ready_for_retry_planning":
        conditions.append("retry_plan_ready")
    if planner.verification_entrypoints:
        conditions.append("verification_entrypoints_present")
    if planner.first_action_targets:
        conditions.append("first_action_targets_present")
    return conditions


def _next_session_final_readiness_status(
    criteria: CandidateReviewManualApplicationNextSessionCompletionCriteria,
    planner: CandidateReviewManualApplicationNextSessionRetryPlanner,
    ready_conditions: list[str],
) -> str:
    required_conditions = [
        "completion_criteria_ready",
        "retry_plan_ready",
        "verification_entrypoints_present",
        "first_action_targets_present",
    ]
    if criteria.blocked_conditions:
        return "blocked_before_next_manual_session"
    if all(condition in ready_conditions for condition in required_conditions):
        return "ready_to_start_next_manual_session"
    if planner.retry_status == "no_retry_actions":
        return "no_next_session_retry_actions"
    return "readiness_incomplete"


def _next_session_final_start_gate(readiness_status: str) -> str:
    if readiness_status == "ready_to_start_next_manual_session":
        return "start_with_first_action"
    if readiness_status == "no_next_session_retry_actions":
        return "no_start_action_required"
    return "resolve_blocked_conditions_before_start"


def build_pending_candidate_review_manual_application_next_session_final_readiness_summary(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionFinalReadinessSummary:
    criteria = build_pending_candidate_review_manual_application_next_session_completion_criteria(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    planner = build_pending_candidate_review_manual_application_next_session_retry_planner(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    ready_conditions = _next_session_final_readiness_conditions(criteria, planner)
    readiness_status = _next_session_final_readiness_status(
        criteria,
        planner,
        ready_conditions,
    )
    return CandidateReviewManualApplicationNextSessionFinalReadinessSummary(
        session_id=criteria.session_id,
        readiness_scope="manual_application_next_session_final_readiness",
        readiness_status=readiness_status,
        start_gate=_next_session_final_start_gate(readiness_status),
        first_action=criteria.first_action,
        first_action_targets=list(criteria.first_action_targets),
        ready_conditions=ready_conditions,
        blocked_conditions=list(criteria.blocked_conditions),
        retry_conditions=list(planner.retry_conditions),
        failure_entrypoints=list(planner.failure_entrypoints),
        verification_entrypoints=list(planner.verification_entrypoints),
        return_to_handoff_path=list(planner.return_to_handoff_path),
        target_candidates=list(planner.target_candidates),
        recommended_processing_order=list(criteria.recommended_processing_order),
        final_readiness_checks=[
            "confirm_completion_criteria_ready",
            "confirm_retry_plan_ready",
            "confirm_first_action_targets_present",
            "confirm_verification_entrypoints_present",
            "confirm_read_only_boundaries",
        ],
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_FINAL_READINESS_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_final_readiness_summary_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    summary = build_pending_candidate_review_manual_application_next_session_final_readiness_summary(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Final Readiness Summary",
        "",
        "## Summary",
        "",
        f"- Session id: `{summary.session_id}`",
        f"- Readiness scope: `{summary.readiness_scope}`",
        f"- Readiness status: `{summary.readiness_status}`",
        f"- Start gate: `{summary.start_gate}`",
        f"- First action: `{summary.first_action}`",
        f"- Applied review decision delta: `{summary.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{summary.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{summary.formal_evidence_delta}`",
        "- Boundary: Next-session final readiness summary is read-only planning metadata.",
        "",
        "## Final Readiness Checks",
        "",
    ]
    for item in summary.final_readiness_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## First Action Targets", ""])
    _append_code_markdown_list(lines, summary.first_action_targets)
    lines.extend(["", "## Ready Conditions", ""])
    _append_code_markdown_list(lines, summary.ready_conditions)
    lines.extend(["", "## Blocked Conditions", ""])
    _append_code_markdown_list(lines, summary.blocked_conditions)
    lines.extend(["", "## Retry Conditions", ""])
    _append_code_markdown_list(lines, summary.retry_conditions)
    lines.extend(["", "## Failure Entrypoints", ""])
    _append_code_markdown_list(lines, summary.failure_entrypoints)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, summary.target_candidates)

    lines.extend(["", "## Recommended Processing Order", ""])
    if not summary.recommended_processing_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(summary.recommended_processing_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Entrypoints", ""])
    for item in summary.verification_entrypoints:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Return To Handoff Path", ""])
    for item in summary.return_to_handoff_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", f"Boundary notes: {' '.join(summary.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_launch_status(
    summary: CandidateReviewManualApplicationNextSessionFinalReadinessSummary,
) -> str:
    if (
        summary.readiness_status == "ready_to_start_next_manual_session"
        and summary.start_gate == "start_with_first_action"
    ):
        return "ready_to_launch_manual_execution"
    if summary.start_gate == "no_start_action_required":
        return "no_launch_action_required"
    return "launch_blocked"


def _next_session_first_command(
    summary: CandidateReviewManualApplicationNextSessionFinalReadinessSummary,
) -> str:
    if summary.start_gate == "start_with_first_action":
        return f"execute_{summary.first_action}"
    if summary.start_gate == "no_start_action_required":
        return "no_manual_execution_command"
    return "resolve_launch_blockers"


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_note(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchNote:
    summary = build_pending_candidate_review_manual_application_next_session_final_readiness_summary(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchNote(
        session_id=summary.session_id,
        launch_scope="manual_application_next_session_launch_note",
        launch_status=_next_session_launch_status(summary),
        start_gate=summary.start_gate,
        first_command=_next_session_first_command(summary),
        first_command_targets=list(summary.first_action_targets),
        candidate_order=_dedupe_preserving_order(
            list(summary.first_action_targets)
            + list(summary.recommended_processing_order)
        ),
        abort_conditions=[
            "abort_if_launch_status_not_ready",
            "abort_if_first_command_targets_missing",
            "abort_if_boundary_delta_nonzero",
            *summary.blocked_conditions,
        ],
        return_paths=_dedupe_preserving_order(
            list(summary.return_to_handoff_path)
            + ["render_next_session_final_readiness_summary"]
        ),
        verification_commands=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_NOTE_VERIFICATION_COMMANDS
        ),
        target_candidates=list(summary.target_candidates),
        launch_checks=[
            "confirm_start_gate_open",
            "confirm_first_command_targets_present",
            "confirm_abort_conditions_understood",
            "confirm_verification_commands_available",
            "confirm_read_only_boundaries",
        ],
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_NOTE_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    note = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_note(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Note",
        "",
        "## Summary",
        "",
        f"- Session id: `{note.session_id}`",
        f"- Launch scope: `{note.launch_scope}`",
        f"- Launch status: `{note.launch_status}`",
        f"- Start gate: `{note.start_gate}`",
        f"- First command: `{note.first_command}`",
        f"- Applied review decision delta: `{note.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{note.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{note.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution launch note is read-only planning metadata.",
        "",
        "## Launch Checks",
        "",
    ]
    for item in note.launch_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## First Command Targets", ""])
    _append_code_markdown_list(lines, note.first_command_targets)

    lines.extend(["", "## Candidate Order", ""])
    if not note.candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(note.candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Abort Conditions", ""])
    for item in note.abort_conditions:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Return Paths", ""])
    for item in note.return_paths:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Verification Commands", ""])
    for item in note.verification_commands:
        lines.append(f"- [ ] `{item}`")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, note.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(note.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _sequence_covers(ordered_items: list[str], expected_items: list[str]) -> bool:
    position = 0
    for expected in expected_items:
        try:
            position = ordered_items.index(expected, position) + 1
        except ValueError:
            return False
    return True


def _next_session_launch_audit_coverage_checks(
    summary: CandidateReviewManualApplicationNextSessionFinalReadinessSummary,
    note: CandidateReviewManualApplicationNextSessionManualExecutionLaunchNote,
) -> dict[str, str]:
    expected_first_command = _next_session_first_command(summary)
    boundary_delta_zero = (
        note.applied_review_decision_delta == 0
        and note.applied_candidate_status_delta == 0
        and note.formal_evidence_delta == 0
        and summary.applied_review_decision_delta == 0
        and summary.applied_candidate_status_delta == 0
        and summary.formal_evidence_delta == 0
    )
    return {
        "start_gate_to_launch_note": (
            "covered" if note.start_gate == summary.start_gate else "missing"
        ),
        "first_action_to_first_command": (
            "covered" if note.first_command == expected_first_command else "missing"
        ),
        "candidate_order_covers_recommended_processing_order": (
            "covered"
            if _sequence_covers(
                note.candidate_order,
                summary.recommended_processing_order,
            )
            else "missing"
        ),
        "abort_conditions_present": (
            "covered" if note.abort_conditions else "missing"
        ),
        "return_paths_include_final_readiness": (
            "covered"
            if "render_next_session_final_readiness_summary" in note.return_paths
            and _sequence_covers(note.return_paths, summary.return_to_handoff_path)
            else "missing"
        ),
        "verification_commands_present": (
            "covered" if note.verification_commands else "missing"
        ),
        "target_candidates_preserved": (
            "covered"
            if note.target_candidates == summary.target_candidates
            else "missing"
        ),
        "read_only_boundary_preserved": (
            "covered" if boundary_delta_zero else "missing"
        ),
    }


def _next_session_launch_audit_status(
    note: CandidateReviewManualApplicationNextSessionManualExecutionLaunchNote,
    coverage_checks: dict[str, str],
) -> str:
    if any(status != "covered" for status in coverage_checks.values()):
        return "launch_audit_blocked"
    if note.launch_status == "ready_to_launch_manual_execution":
        return "launch_audit_ready"
    if note.launch_status == "no_launch_action_required":
        return "launch_audit_no_action"
    return "launch_audit_blocked"


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchAudit:
    summary = build_pending_candidate_review_manual_application_next_session_final_readiness_summary(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    note = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_note(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    coverage_checks = _next_session_launch_audit_coverage_checks(summary, note)
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchAudit(
        session_id=note.session_id,
        audit_scope="manual_application_next_session_launch_audit",
        audit_status=_next_session_launch_audit_status(note, coverage_checks),
        readiness_status=summary.readiness_status,
        launch_status=note.launch_status,
        start_gate=note.start_gate,
        first_command=note.first_command,
        coverage_checks=coverage_checks,
        missing_coverage=[
            check for check, status in coverage_checks.items() if status != "covered"
        ],
        boundary_checks=[
            "applied_review_decision_delta_zero",
            "applied_candidate_status_delta_zero",
            "formal_evidence_delta_zero",
        ],
        candidate_order=list(note.candidate_order),
        return_paths=list(note.return_paths),
        verification_commands=list(note.verification_commands),
        target_candidates=list(note.target_candidates),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Readiness status: `{audit.readiness_status}`",
        f"- Launch status: `{audit.launch_status}`",
        f"- Start gate: `{audit.start_gate}`",
        f"- First command: `{audit.first_command}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution launch audit is read-only planning metadata.",
        "",
        "## Coverage Checks",
        "",
    ]
    for check, status in audit.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage:
        lines.append("No missing launch-note coverage.")
    else:
        _append_code_markdown_list(lines, audit.missing_coverage)

    lines.extend(["", "## Boundary Checks", ""])
    for item in audit.boundary_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Candidate Order", ""])
    if not audit.candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Return Paths", ""])
    for item in audit.return_paths:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Verification Commands", ""])
    for item in audit.verification_commands:
        lines.append(f"- [ ] `{item}`")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_launch_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionLaunchAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.audit_status != "launch_audit_ready":
        reasons.append("launch_audit_not_ready")
    reasons.extend(audit.missing_coverage)
    if not audit.first_command:
        reasons.append("sealed_first_command_missing")
    if not audit.verification_commands:
        reasons.append("verification_commands_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_launch_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionLaunchAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution"
    if audit.launch_status == "no_launch_action_required":
        return "sealed_no_manual_action_required"
    return "sealed_for_manual_execution"


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_launch_seal_blocked_reasons(audit)
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_launch_seal",
        seal_status=_next_session_launch_seal_status(audit, blocked_reasons),
        audit_status=audit.audit_status,
        launch_status=audit.launch_status,
        start_gate=audit.start_gate,
        sealed_first_command=audit.first_command,
        sealed_candidate_order=list(audit.candidate_order),
        blocked_reasons=blocked_reasons,
        seal_checks=[
            "confirm_launch_audit_ready",
            "confirm_launch_coverage_complete",
            "confirm_first_command_sealed",
            "confirm_verification_commands_present",
            "confirm_boundary_delta_zero",
        ],
        verification_commands=list(audit.verification_commands),
        rollback_entrypoints=list(audit.return_paths),
        target_candidates=list(audit.target_candidates),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Launch status: `{seal.launch_status}`",
        f"- Start gate: `{seal.start_gate}`",
        f"- Sealed first command: `{seal.sealed_first_command}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution launch seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No launch seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Commands", ""])
    for item in seal.verification_commands:
        lines.append(f"- [ ] `{item}`")

    lines.extend(["", "## Rollback Entrypoints", ""])
    for item in seal.rollback_entrypoints:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_launch_runbook_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchSeal,
) -> str:
    if seal.seal_status == "sealed_for_manual_execution":
        return "ready_for_manual_execution_runbook"
    if seal.seal_status == "sealed_no_manual_action_required":
        return "no_manual_execution_required_runbook"
    return "blocked_before_manual_execution_runbook"


def _next_session_launch_runbook_execution_order(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchSeal,
) -> list[str]:
    order = [seal.sealed_first_command]
    order.extend(seal.sealed_candidate_order)
    order.extend(
        [
            "run_focused_source_intake_tests",
            "run_boundary_regression_tests",
            "run_full_suite",
            "rerun_launch_seal",
        ]
    )
    return [item for item in order if item]


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbook:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    first_step = seal.sealed_first_command
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbook(
        session_id=seal.session_id,
        runbook_scope="manual_application_next_session_launch_runbook",
        runbook_status=_next_session_launch_runbook_status(seal),
        seal_status=seal.seal_status,
        start_gate=seal.start_gate,
        first_step=first_step,
        execution_order=_next_session_launch_runbook_execution_order(seal),
        step_verification={
            first_step: list(seal.verification_commands),
            "candidate_order": ["confirm_candidate_order_matches_launch_seal"],
            "post_completion": ["rerun_launch_seal"],
        },
        failure_rollback=list(seal.rollback_entrypoints),
        post_completion_review=[
            "rerun_launch_seal",
            "confirm_review_decision_delta_zero",
            "confirm_candidate_status_delta_zero",
            "confirm_formal_evidence_delta_zero",
        ],
        target_candidates=list(seal.target_candidates),
        runbook_checks=[
            "confirm_launch_seal_ready",
            "confirm_first_step_present",
            "confirm_execution_order_present",
            "confirm_step_verification_present",
            "confirm_failure_rollback_present",
            "confirm_post_completion_review_present",
            "confirm_read_only_boundaries",
        ],
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RUNBOOK_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    runbook = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Runbook",
        "",
        "## Summary",
        "",
        f"- Session id: `{runbook.session_id}`",
        f"- Runbook scope: `{runbook.runbook_scope}`",
        f"- Runbook status: `{runbook.runbook_status}`",
        f"- Seal status: `{runbook.seal_status}`",
        f"- Start gate: `{runbook.start_gate}`",
        f"- First step: `{runbook.first_step}`",
        f"- Applied review decision delta: `{runbook.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{runbook.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{runbook.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution launch runbook is read-only planning metadata.",
        "",
        "## Runbook Checks",
        "",
    ]
    for item in runbook.runbook_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Execution Order", ""])
    if not runbook.execution_order:
        lines.append("No manual execution steps are queued.")
    for index, item in enumerate(runbook.execution_order, 1):
        lines.append(f"{index}. `{item}`")

    lines.extend(["", "## Step Verification", ""])
    for step, verifications in runbook.step_verification.items():
        lines.append(f"- `{step}`")
        for item in verifications:
            if item.startswith("uv run "):
                lines.append(f"  - [ ] `{item}`")
            else:
                lines.append(f"  - [ ] {item}")

    lines.extend(["", "## Failure Rollback", ""])
    for item in runbook.failure_rollback:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in runbook.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, runbook.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(runbook.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _flatten_step_verification(
    step_verification: dict[str, list[str]],
) -> list[str]:
    return [
        item
        for verifications in step_verification.values()
        for item in verifications
    ]


def _next_session_launch_runbook_audit_coverage_checks(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchSeal,
    runbook: CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbook,
) -> dict[str, str]:
    flattened_verification = _flatten_step_verification(runbook.step_verification)
    expected_post_completion_review = [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    boundary_delta_zero = (
        seal.applied_review_decision_delta == 0
        and seal.applied_candidate_status_delta == 0
        and seal.formal_evidence_delta == 0
        and runbook.applied_review_decision_delta == 0
        and runbook.applied_candidate_status_delta == 0
        and runbook.formal_evidence_delta == 0
    )
    execution_starts_with_first_step = (
        not runbook.first_step
        or (
            bool(runbook.execution_order)
            and runbook.execution_order[0] == runbook.first_step
        )
    )
    return {
        "seal_status_to_runbook": (
            "covered" if runbook.seal_status == seal.seal_status else "missing"
        ),
        "start_gate_preserved": (
            "covered" if runbook.start_gate == seal.start_gate else "missing"
        ),
        "first_step_matches_sealed_first_command": (
            "covered"
            if runbook.first_step == seal.sealed_first_command
            else "missing"
        ),
        "execution_order_starts_with_first_step": (
            "covered" if execution_starts_with_first_step else "missing"
        ),
        "execution_order_covers_sealed_candidate_order": (
            "covered"
            if _sequence_covers(
                runbook.execution_order,
                seal.sealed_candidate_order,
            )
            else "missing"
        ),
        "verification_commands_covered": (
            "covered"
            if all(
                command in flattened_verification
                for command in seal.verification_commands
            )
            else "missing"
        ),
        "failure_rollback_covers_rollback_entrypoints": (
            "covered"
            if _sequence_covers(runbook.failure_rollback, seal.rollback_entrypoints)
            else "missing"
        ),
        "post_completion_review_present": (
            "covered"
            if all(
                item in runbook.post_completion_review
                for item in expected_post_completion_review
            )
            else "missing"
        ),
        "target_candidates_preserved": (
            "covered"
            if runbook.target_candidates == seal.target_candidates
            else "missing"
        ),
        "read_only_boundary_preserved": (
            "covered" if boundary_delta_zero else "missing"
        ),
    }


def _next_session_launch_runbook_audit_status(
    runbook: CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbook,
    coverage_checks: dict[str, str],
) -> str:
    if any(status != "covered" for status in coverage_checks.values()):
        return "runbook_audit_blocked"
    if runbook.runbook_status == "ready_for_manual_execution_runbook":
        return "runbook_audit_ready"
    if runbook.runbook_status == "no_manual_execution_required_runbook":
        return "runbook_audit_no_action"
    return "runbook_audit_blocked"


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAudit:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    runbook = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    coverage_checks = _next_session_launch_runbook_audit_coverage_checks(
        seal,
        runbook,
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAudit(
        session_id=runbook.session_id,
        audit_scope="manual_application_next_session_launch_runbook_audit",
        audit_status=_next_session_launch_runbook_audit_status(
            runbook,
            coverage_checks,
        ),
        runbook_status=runbook.runbook_status,
        seal_status=seal.seal_status,
        start_gate=runbook.start_gate,
        first_step=runbook.first_step,
        coverage_checks=coverage_checks,
        missing_coverage=[
            check for check, status in coverage_checks.items() if status != "covered"
        ],
        boundary_checks=[
            "applied_review_decision_delta_zero",
            "applied_candidate_status_delta_zero",
            "formal_evidence_delta_zero",
        ],
        candidate_order=list(seal.sealed_candidate_order),
        execution_order=list(runbook.execution_order),
        step_verification={
            step: list(verifications)
            for step, verifications in runbook.step_verification.items()
        },
        failure_rollback=list(runbook.failure_rollback),
        post_completion_review=list(runbook.post_completion_review),
        verification_commands=list(seal.verification_commands),
        target_candidates=list(runbook.target_candidates),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RUNBOOK_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Runbook Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Runbook status: `{audit.runbook_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Start gate: `{audit.start_gate}`",
        f"- First step: `{audit.first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution launch runbook audit is read-only planning metadata.",
        "",
        "## Coverage Checks",
        "",
    ]
    for check, status in audit.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage:
        lines.append("No missing runbook coverage.")
    else:
        _append_code_markdown_list(lines, audit.missing_coverage)

    lines.extend(["", "## Boundary Checks", ""])
    for item in audit.boundary_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Candidate Order", ""])
    if not audit.candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Execution Order", ""])
    if not audit.execution_order:
        lines.append("No manual execution steps are queued.")
    for index, item in enumerate(audit.execution_order, 1):
        lines.append(f"{index}. `{item}`")

    lines.extend(["", "## Step Verification", ""])
    for step, verifications in audit.step_verification.items():
        lines.append(f"- `{step}`")
        for item in verifications:
            if item.startswith("uv run "):
                lines.append(f"  - [ ] `{item}`")
            else:
                lines.append(f"  - [ ] {item}")

    lines.extend(["", "## Failure Rollback", ""])
    for item in audit.failure_rollback:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Verification Commands", ""])
    for item in audit.verification_commands:
        lines.append(f"- [ ] `{item}`")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_launch_runbook_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.audit_status != "runbook_audit_ready":
        reasons.append("runbook_audit_not_ready")
    reasons.extend(audit.missing_coverage)
    if not audit.first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.verification_commands:
        reasons.append("verification_commands_missing")
    if not audit.failure_rollback:
        reasons.append("failure_rollback_missing")
    if not audit.post_completion_review:
        reasons.append("post_completion_review_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_launch_runbook_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_runbook_audit"
    if audit.audit_status == "runbook_audit_no_action":
        return "sealed_no_manual_execution_required_runbook_audit"
    return "sealed_for_manual_execution_runbook_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAuditSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_launch_runbook_audit_seal_blocked_reasons(audit)
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAuditSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_launch_runbook_audit_seal",
        seal_status=_next_session_launch_runbook_audit_seal_status(
            audit,
            blocked_reasons,
        ),
        audit_status=audit.audit_status,
        runbook_status=audit.runbook_status,
        launch_seal_status=audit.seal_status,
        start_gate=audit.start_gate,
        sealed_first_step=audit.first_step,
        sealed_candidate_order=list(audit.candidate_order),
        blocked_reasons=blocked_reasons,
        seal_checks=[
            "confirm_runbook_audit_ready",
            "confirm_runbook_coverage_complete",
            "confirm_first_step_sealed",
            "confirm_verification_commands_present",
            "confirm_failure_rollback_present",
            "confirm_post_completion_review_present",
            "confirm_boundary_delta_zero",
        ],
        verification_commands=list(audit.verification_commands),
        rollback_entrypoints=list(audit.failure_rollback),
        post_completion_review=list(audit.post_completion_review),
        target_candidates=list(audit.target_candidates),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RUNBOOK_AUDIT_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Runbook Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Runbook status: `{seal.runbook_status}`",
        f"- Launch seal status: `{seal.launch_seal_status}`",
        f"- Start gate: `{seal.start_gate}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution launch runbook audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No runbook audit seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Commands", ""])
    for item in seal.verification_commands:
        lines.append(f"- [ ] `{item}`")

    lines.extend(["", "## Rollback Entrypoints", ""])
    for item in seal.rollback_entrypoints:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_final_launch_packet_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAuditSeal,
) -> str:
    if seal.blocked_reasons:
        return "blocked_before_final_manual_launch_packet"
    if seal.seal_status == "sealed_no_manual_execution_required_runbook_audit":
        return "no_manual_execution_required_final_launch_packet"
    return "ready_for_final_manual_launch_packet"


def build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacket:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    boundary_confirmation = [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    return CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacket(
        session_id=seal.session_id,
        launch_packet_scope="manual_application_next_session_final_launch_packet",
        launch_packet_status=_next_session_final_launch_packet_status(seal),
        audit_seal_status=seal.seal_status,
        sealed_first_step=seal.sealed_first_step,
        candidate_order=list(seal.sealed_candidate_order),
        operator_start_checklist=[
            "confirm_audit_seal_ready",
            "confirm_sealed_first_step",
            "confirm_candidate_order",
            "execute_sealed_first_step",
        ],
        verification_checklist=[
            *seal.verification_commands,
            "confirm_boundary_confirmation",
        ],
        rollback_path=list(seal.rollback_entrypoints),
        post_completion_review=list(seal.post_completion_review),
        boundary_confirmation=boundary_confirmation,
        target_candidates=list(seal.target_candidates),
        blocked_reasons=list(seal.blocked_reasons),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_FINAL_LAUNCH_PACKET_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Launch Packet",
        "",
        "## Summary",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Launch packet scope: `{packet.launch_packet_scope}`",
        f"- Launch packet status: `{packet.launch_packet_status}`",
        f"- Audit seal status: `{packet.audit_seal_status}`",
        f"- Sealed first step: `{packet.sealed_first_step}`",
        f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution final launch packet is read-only planning metadata.",
        "",
        "## Operator Start Checklist",
        "",
    ]
    for item in packet.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Candidate Order", ""])
    if not packet.candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(packet.candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in packet.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in packet.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in packet.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in packet.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not packet.blocked_reasons:
        lines.append("No final launch packet blockers.")
    else:
        _append_code_markdown_list(lines, packet.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, packet.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_final_launch_packet_handoff_coverage_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacket,
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchRunbookAuditSeal,
) -> dict[str, str]:
    expected_operator_start_checklist = [
        "confirm_audit_seal_ready",
        "confirm_sealed_first_step",
        "confirm_candidate_order",
        "execute_sealed_first_step",
    ]
    expected_boundary_confirmation = [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    return {
        "launch_packet_ready": (
            "covered"
            if packet.launch_packet_status
            in {
                "ready_for_final_manual_launch_packet",
                "no_manual_execution_required_final_launch_packet",
            }
            else "missing"
        ),
        "audit_seal_status_preserved": (
            "covered" if packet.audit_seal_status == seal.seal_status else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered" if packet.sealed_first_step == seal.sealed_first_step else "missing"
        ),
        "candidate_order_preserved": (
            "covered"
            if packet.candidate_order == seal.sealed_candidate_order
            else "missing"
        ),
        "operator_start_checklist_complete": (
            "covered"
            if all(item in packet.operator_start_checklist for item in expected_operator_start_checklist)
            else "missing"
        ),
        "verification_checklist_covers_commands": (
            "covered"
            if all(item in packet.verification_checklist for item in seal.verification_commands)
            else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if packet.rollback_path == seal.rollback_entrypoints else "missing"
        ),
        "post_completion_review_preserved": (
            "covered"
            if packet.post_completion_review == seal.post_completion_review
            else "missing"
        ),
        "target_candidates_preserved": (
            "covered" if packet.target_candidates == seal.target_candidates else "missing"
        ),
        "boundary_confirmation_complete": (
            "covered"
            if all(item in packet.boundary_confirmation for item in expected_boundary_confirmation)
            else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                packet.applied_review_decision_delta == 0
                and packet.applied_candidate_status_delta == 0
                and packet.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_final_launch_packet_handoff_readiness(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacket,
    missing_coverage: list[str],
) -> str:
    if packet.blocked_reasons or missing_coverage:
        return "blocked_before_operator_handoff"
    if packet.launch_packet_status == "no_manual_execution_required_final_launch_packet":
        return "no_manual_execution_required_operator_handoff"
    return "ready_for_operator_handoff"


def build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAudit:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    coverage_checks = _next_session_final_launch_packet_handoff_coverage_checks(
        packet,
        seal,
    )
    missing_coverage = [
        check for check, status in coverage_checks.items() if status != "covered"
    ]
    return CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAudit(
        session_id=packet.session_id,
        handoff_audit_scope="manual_application_next_session_final_launch_packet_handoff_audit",
        handoff_readiness=_next_session_final_launch_packet_handoff_readiness(
            packet,
            missing_coverage,
        ),
        launch_packet_status=packet.launch_packet_status,
        audit_seal_status=packet.audit_seal_status,
        sealed_first_step=packet.sealed_first_step,
        coverage_checks=coverage_checks,
        missing_coverage=missing_coverage,
        operator_safe_start_boundary=[
            "confirm_handoff_readiness",
            "confirm_launch_packet_ready",
            "confirm_audit_seal_status_preserved",
            "confirm_sealed_first_step_preserved",
            "confirm_candidate_order_preserved",
            "confirm_boundary_confirmation_before_execution",
        ],
        candidate_order=list(packet.candidate_order),
        operator_start_checklist=list(packet.operator_start_checklist),
        verification_checklist=list(packet.verification_checklist),
        rollback_path=list(packet.rollback_path),
        post_completion_review=list(packet.post_completion_review),
        boundary_confirmation=list(packet.boundary_confirmation),
        target_candidates=list(packet.target_candidates),
        blocked_reasons=list(packet.blocked_reasons),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_FINAL_LAUNCH_PACKET_HANDOFF_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Handoff audit scope: `{audit.handoff_audit_scope}`",
        f"- Handoff readiness: `{audit.handoff_readiness}`",
        f"- Launch packet status: `{audit.launch_packet_status}`",
        f"- Audit seal status: `{audit.audit_seal_status}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution final launch packet handoff audit is read-only planning metadata.",
        "",
        "## Coverage Checks",
        "",
    ]
    for check, status in audit.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage:
        lines.append("No missing final launch packet handoff coverage.")
    else:
        _append_code_markdown_list(lines, audit.missing_coverage)

    lines.extend(["", "## Operator-Safe Start Boundary", ""])
    for item in audit.operator_safe_start_boundary:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Candidate Order", ""])
    if not audit.candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in audit.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No final launch packet handoff blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_final_launch_packet_handoff_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.handoff_readiness not in {
        "ready_for_operator_handoff",
        "no_manual_execution_required_operator_handoff",
    }:
        reasons.append("handoff_readiness_not_ready")
    reasons.extend(audit.missing_coverage)
    reasons.extend(audit.blocked_reasons)
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.operator_safe_start_boundary:
        reasons.append("operator_safe_start_boundary_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.rollback_path:
        reasons.append("rollback_path_missing")
    if not audit.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_final_launch_packet_handoff_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_operator_go_no_go_seal"
    if audit.handoff_readiness == "no_manual_execution_required_operator_handoff":
        return "sealed_no_manual_execution_required_operator_go_no_go"
    return "sealed_for_operator_manual_execution_go"


def _next_session_final_launch_packet_handoff_audit_go_no_go_decision(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "no_go_operator_manual_execution"
    if audit.handoff_readiness == "no_manual_execution_required_operator_handoff":
        return "no_manual_execution_required"
    return "go_for_operator_manual_execution"


def build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAuditSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_final_launch_packet_handoff_audit_seal_blocked_reasons(
        audit
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAuditSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_final_launch_packet_handoff_audit_seal",
        seal_status=_next_session_final_launch_packet_handoff_audit_seal_status(
            audit,
            blocked_reasons,
        ),
        handoff_readiness=audit.handoff_readiness,
        go_no_go_decision=_next_session_final_launch_packet_handoff_audit_go_no_go_decision(
            audit,
            blocked_reasons,
        ),
        launch_packet_status=audit.launch_packet_status,
        audit_seal_status=audit.audit_seal_status,
        sealed_first_step=audit.sealed_first_step,
        sealed_candidate_order=list(audit.candidate_order),
        blocked_reasons=blocked_reasons,
        seal_checks=[
            "confirm_handoff_readiness_ready",
            "confirm_launch_packet_ready",
            "confirm_go_no_go_decision_go",
            "confirm_operator_safe_start_boundary_present",
            "confirm_sealed_first_step_present",
            "confirm_verification_checklist_present",
            "confirm_rollback_path_present",
            "confirm_post_completion_review_present",
            "confirm_boundary_confirmation_present",
            "confirm_boundary_delta_zero",
        ],
        operator_safe_start_boundary=list(audit.operator_safe_start_boundary),
        verification_checklist=list(audit.verification_checklist),
        rollback_path=list(audit.rollback_path),
        post_completion_review=list(audit.post_completion_review),
        boundary_confirmation=list(audit.boundary_confirmation),
        target_candidates=list(audit.target_candidates),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_FINAL_LAUNCH_PACKET_HANDOFF_AUDIT_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Handoff readiness: `{seal.handoff_readiness}`",
        f"- Go/no-go decision: `{seal.go_no_go_decision}`",
        f"- Launch packet status: `{seal.launch_packet_status}`",
        f"- Audit seal status: `{seal.audit_seal_status}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution final launch packet handoff audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No operator go/no-go seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Operator-Safe Start Boundary", ""])
    for item in seal.operator_safe_start_boundary:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_operator_go_no_go_seal_launch_receipt_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAuditSeal,
) -> str:
    if seal.blocked_reasons or seal.go_no_go_decision == "no_go_operator_manual_execution":
        return "blocked_before_operator_launch_receipt"
    if seal.go_no_go_decision == "no_manual_execution_required":
        return "no_manual_execution_required_launch_receipt"
    return "ready_for_operator_launch_receipt"


def _next_session_operator_go_no_go_seal_launch_receipt_decision(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAuditSeal,
) -> str:
    if seal.blocked_reasons or seal.go_no_go_decision == "no_go_operator_manual_execution":
        return "receipt_blocked_no_start"
    if seal.go_no_go_decision == "no_manual_execution_required":
        return "receipt_no_manual_execution_required"
    return "receipt_ready_to_start_manual_execution"


def build_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionOperatorGoNoGoSealLaunchReceipt:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionOperatorGoNoGoSealLaunchReceipt(
        session_id=seal.session_id,
        receipt_scope="manual_application_next_session_operator_go_no_go_seal_launch_receipt",
        receipt_status=_next_session_operator_go_no_go_seal_launch_receipt_status(
            seal
        ),
        seal_status=seal.seal_status,
        handoff_readiness=seal.handoff_readiness,
        go_no_go_decision=seal.go_no_go_decision,
        receipt_decision=_next_session_operator_go_no_go_seal_launch_receipt_decision(
            seal
        ),
        signed_first_step=seal.sealed_first_step,
        signed_candidate_order=list(seal.sealed_candidate_order),
        operator_receipt_checklist=[
            "confirm_go_no_go_seal_ready",
            "confirm_receipt_decision",
            "confirm_signed_first_step",
            "confirm_signed_candidate_order",
            "confirm_pre_execution_confirmation",
        ],
        pre_execution_confirmation=[
            "confirm_no_review_decision_auto_write",
            "confirm_no_candidate_extract_auto_write",
            "confirm_no_promotion_auto_apply",
            "confirm_formal_evidence_unchanged",
            "confirm_operator_executes_manual_steps_only_after_receipt",
        ],
        verification_checklist=list(seal.verification_checklist),
        rollback_path=list(seal.rollback_path),
        post_completion_review=list(seal.post_completion_review),
        boundary_confirmation=list(seal.boundary_confirmation),
        target_candidates=list(seal.target_candidates),
        blocked_reasons=list(seal.blocked_reasons),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_OPERATOR_GO_NO_GO_SEAL_LAUNCH_RECEIPT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    receipt = build_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Operator Go/No-Go Seal Launch Receipt",
        "",
        "## Summary",
        "",
        f"- Session id: `{receipt.session_id}`",
        f"- Receipt scope: `{receipt.receipt_scope}`",
        f"- Receipt status: `{receipt.receipt_status}`",
        f"- Seal status: `{receipt.seal_status}`",
        f"- Handoff readiness: `{receipt.handoff_readiness}`",
        f"- Go/no-go decision: `{receipt.go_no_go_decision}`",
        f"- Receipt decision: `{receipt.receipt_decision}`",
        f"- Signed first step: `{receipt.signed_first_step}`",
        f"- Applied review decision delta: `{receipt.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{receipt.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{receipt.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution operator go/no-go seal launch receipt is read-only planning metadata.",
        "",
        "## Operator Receipt Checklist",
        "",
    ]
    for item in receipt.operator_receipt_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Pre-Execution Confirmation", ""])
    for item in receipt.pre_execution_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not receipt.blocked_reasons:
        lines.append("No operator launch receipt blockers.")
    else:
        _append_code_markdown_list(lines, receipt.blocked_reasons)

    lines.extend(["", "## Signed Candidate Order", ""])
    if not receipt.signed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(receipt.signed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in receipt.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in receipt.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in receipt.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in receipt.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, receipt.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(receipt.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_launch_receipt_final_boundary_coverage_checks(
    receipt: CandidateReviewManualApplicationNextSessionManualExecutionOperatorGoNoGoSealLaunchReceipt,
    seal: CandidateReviewManualApplicationNextSessionManualExecutionFinalLaunchPacketHandoffAuditSeal,
) -> dict[str, str]:
    expected_operator_receipt_checklist = [
        "confirm_go_no_go_seal_ready",
        "confirm_receipt_decision",
        "confirm_signed_first_step",
        "confirm_signed_candidate_order",
        "confirm_pre_execution_confirmation",
    ]
    expected_pre_execution_confirmation = [
        "confirm_no_review_decision_auto_write",
        "confirm_no_candidate_extract_auto_write",
        "confirm_no_promotion_auto_apply",
        "confirm_formal_evidence_unchanged",
        "confirm_operator_executes_manual_steps_only_after_receipt",
    ]
    expected_boundary_confirmation = [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    return {
        "receipt_ready": (
            "covered"
            if receipt.receipt_status
            in {
                "ready_for_operator_launch_receipt",
                "no_manual_execution_required_launch_receipt",
            }
            else "missing"
        ),
        "seal_status_preserved": (
            "covered" if receipt.seal_status == seal.seal_status else "missing"
        ),
        "go_no_go_decision_preserved": (
            "covered"
            if receipt.go_no_go_decision == seal.go_no_go_decision
            else "missing"
        ),
        "receipt_decision_ready": (
            "covered"
            if receipt.receipt_decision
            in {
                "receipt_ready_to_start_manual_execution",
                "receipt_no_manual_execution_required",
            }
            else "missing"
        ),
        "signed_first_step_preserved": (
            "covered"
            if receipt.signed_first_step == seal.sealed_first_step
            else "missing"
        ),
        "signed_candidate_order_preserved": (
            "covered"
            if receipt.signed_candidate_order == seal.sealed_candidate_order
            else "missing"
        ),
        "operator_receipt_checklist_complete": (
            "covered"
            if all(
                item in receipt.operator_receipt_checklist
                for item in expected_operator_receipt_checklist
            )
            else "missing"
        ),
        "pre_execution_confirmation_complete": (
            "covered"
            if all(
                item in receipt.pre_execution_confirmation
                for item in expected_pre_execution_confirmation
            )
            else "missing"
        ),
        "verification_checklist_preserved": (
            "covered"
            if receipt.verification_checklist == seal.verification_checklist
            else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if receipt.rollback_path == seal.rollback_path else "missing"
        ),
        "post_completion_review_preserved": (
            "covered"
            if receipt.post_completion_review == seal.post_completion_review
            else "missing"
        ),
        "target_candidates_preserved": (
            "covered"
            if receipt.target_candidates == seal.target_candidates
            else "missing"
        ),
        "boundary_confirmation_complete": (
            "covered"
            if all(
                item in receipt.boundary_confirmation
                for item in expected_boundary_confirmation
            )
            else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                receipt.applied_review_decision_delta == 0
                and receipt.applied_candidate_status_delta == 0
                and receipt.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_launch_receipt_final_boundary_readiness(
    receipt: CandidateReviewManualApplicationNextSessionManualExecutionOperatorGoNoGoSealLaunchReceipt,
    missing_coverage: list[str],
) -> str:
    if receipt.blocked_reasons or missing_coverage:
        return "blocked_before_final_boundary_audit"
    if receipt.receipt_status == "no_manual_execution_required_launch_receipt":
        return "no_manual_execution_required_final_boundary_audit"
    return "ready_for_final_boundary_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAudit:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    receipt = build_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    coverage_checks = _next_session_launch_receipt_final_boundary_coverage_checks(
        receipt,
        seal,
    )
    missing_coverage = [
        check for check, status in coverage_checks.items() if status != "covered"
    ]
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAudit(
        session_id=receipt.session_id,
        boundary_audit_scope="manual_application_next_session_launch_receipt_final_boundary_audit",
        final_boundary_readiness=_next_session_launch_receipt_final_boundary_readiness(
            receipt,
            missing_coverage,
        ),
        receipt_status=receipt.receipt_status,
        seal_status=receipt.seal_status,
        go_no_go_decision=receipt.go_no_go_decision,
        receipt_decision=receipt.receipt_decision,
        signed_first_step=receipt.signed_first_step,
        receipt_coverage_checks=coverage_checks,
        missing_coverage=missing_coverage,
        final_boundary_confirmation=[
            "confirm_receipt_ready",
            "confirm_go_no_go_preserved",
            "confirm_signed_first_step_preserved",
            "confirm_pre_execution_boundary",
            "confirm_boundary_delta_zero",
            "confirm_receipt_read_only",
        ],
        signed_candidate_order=list(receipt.signed_candidate_order),
        operator_receipt_checklist=list(receipt.operator_receipt_checklist),
        pre_execution_confirmation=list(receipt.pre_execution_confirmation),
        verification_checklist=list(receipt.verification_checklist),
        rollback_path=list(receipt.rollback_path),
        post_completion_review=list(receipt.post_completion_review),
        boundary_confirmation=list(receipt.boundary_confirmation),
        target_candidates=list(receipt.target_candidates),
        blocked_reasons=list(receipt.blocked_reasons),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RECEIPT_FINAL_BOUNDARY_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Boundary audit scope: `{audit.boundary_audit_scope}`",
        f"- Final boundary readiness: `{audit.final_boundary_readiness}`",
        f"- Receipt status: `{audit.receipt_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Go/no-go decision: `{audit.go_no_go_decision}`",
        f"- Receipt decision: `{audit.receipt_decision}`",
        f"- Signed first step: `{audit.signed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution launch receipt final boundary audit is read-only planning metadata.",
        "",
        "## Receipt Coverage Checks",
        "",
    ]
    for check, status in audit.receipt_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage:
        lines.append("No missing launch receipt boundary coverage.")
    else:
        _append_code_markdown_list(lines, audit.missing_coverage)

    lines.extend(["", "## Final Boundary Confirmation", ""])
    for item in audit.final_boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Pre-Execution Confirmation", ""])
    for item in audit.pre_execution_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Signed Candidate Order", ""])
    if not audit.signed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.signed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No launch receipt final boundary blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_launch_receipt_final_boundary_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.final_boundary_readiness not in {
        "ready_for_final_boundary_audit",
        "no_manual_execution_required_final_boundary_audit",
    }:
        reasons.append("final_boundary_readiness_not_ready")
    reasons.extend(audit.missing_coverage)
    reasons.extend(audit.blocked_reasons)
    if not audit.signed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.signed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.final_boundary_confirmation:
        reasons.append("final_boundary_confirmation_missing")
    if not audit.pre_execution_confirmation:
        reasons.append("pre_execution_confirmation_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_launch_receipt_final_boundary_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_launch_receipt_final_boundary_seal"
    if audit.final_boundary_readiness == "no_manual_execution_required_final_boundary_audit":
        return "sealed_no_manual_execution_required_launch_receipt_final_boundary"
    return "sealed_for_launch_receipt_final_boundary"


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_launch_receipt_final_boundary_audit_seal_blocked_reasons(
        audit
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_launch_receipt_final_boundary_audit_seal",
        seal_status=_next_session_launch_receipt_final_boundary_audit_seal_status(
            audit,
            blocked_reasons,
        ),
        final_boundary_readiness=audit.final_boundary_readiness,
        receipt_status=audit.receipt_status,
        go_no_go_decision=audit.go_no_go_decision,
        receipt_decision=audit.receipt_decision,
        sealed_first_step=audit.signed_first_step,
        sealed_candidate_order=list(audit.signed_candidate_order),
        receipt_coverage_checks=dict(audit.receipt_coverage_checks),
        missing_coverage=list(audit.missing_coverage),
        final_boundary_confirmation=list(audit.final_boundary_confirmation),
        pre_execution_confirmation=list(audit.pre_execution_confirmation),
        verification_checklist=list(audit.verification_checklist),
        rollback_path=list(audit.rollback_path),
        post_completion_review=list(audit.post_completion_review),
        boundary_confirmation=list(audit.boundary_confirmation),
        target_candidates=list(audit.target_candidates),
        blocked_reasons=blocked_reasons,
        seal_checks=[
            "confirm_final_boundary_readiness_ready",
            "confirm_receipt_coverage_complete",
            "confirm_receipt_ready",
            "confirm_go_no_go_decision_preserved",
            "confirm_signed_first_step_sealed",
            "confirm_final_boundary_confirmation_present",
            "confirm_pre_execution_confirmation_present",
            "confirm_verification_checklist_present",
            "confirm_boundary_delta_zero",
        ],
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RECEIPT_FINAL_BOUNDARY_AUDIT_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Final boundary readiness: `{seal.final_boundary_readiness}`",
        f"- Receipt status: `{seal.receipt_status}`",
        f"- Go/no-go decision: `{seal.go_no_go_decision}`",
        f"- Receipt decision: `{seal.receipt_decision}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution launch receipt final boundary audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Receipt Coverage Checks", ""])
    for check, status in seal.receipt_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage and not seal.blocked_reasons:
        lines.append("No launch receipt final boundary seal blockers.")
    else:
        _append_code_markdown_list(
            lines,
            _dedupe_preserving_order([*seal.missing_coverage, *seal.blocked_reasons]),
        )

    lines.extend(["", "## Final Boundary Confirmation", ""])
    for item in seal.final_boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Pre-Execution Confirmation", ""])
    for item in seal.pre_execution_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_launch_receipt_final_boundary_audit_seal_operator_start_packet_blocked_reasons(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSeal,
) -> list[str]:
    reasons: list[str] = []
    if seal.seal_status not in {
        "sealed_for_launch_receipt_final_boundary",
        "sealed_no_manual_execution_required_launch_receipt_final_boundary",
    }:
        reasons.append("launch_receipt_final_boundary_audit_seal_not_ready")
    reasons.extend(seal.blocked_reasons)
    if not seal.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not seal.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not seal.pre_execution_confirmation:
        reasons.append("pre_execution_confirmation_missing")
    if not seal.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not seal.rollback_path:
        reasons.append("rollback_path_missing")
    if not seal.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        seal.applied_review_decision_delta != 0
        or seal.applied_candidate_status_delta != 0
        or seal.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_launch_receipt_final_boundary_audit_seal_operator_start_packet_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSeal,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_operator_start_packet"
    if seal.seal_status == "sealed_no_manual_execution_required_launch_receipt_final_boundary":
        return "no_manual_execution_required_operator_start_packet"
    return "ready_for_operator_start_packet"


def _next_session_launch_receipt_final_boundary_audit_seal_operator_start_authorization(
    packet_status: str,
) -> str:
    if packet_status == "ready_for_operator_start_packet":
        return "authorized_to_start_manual_execution"
    if packet_status == "no_manual_execution_required_operator_start_packet":
        return "no_manual_execution_required"
    return "not_authorized_to_start_manual_execution"


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacket:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_launch_receipt_final_boundary_audit_seal_operator_start_packet_blocked_reasons(
        seal
    )
    packet_status = _next_session_launch_receipt_final_boundary_audit_seal_operator_start_packet_status(
        seal,
        blocked_reasons,
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacket(
        session_id=seal.session_id,
        packet_scope="manual_application_next_session_launch_receipt_final_boundary_audit_seal_operator_start_packet",
        packet_status=packet_status,
        seal_status=seal.seal_status,
        final_boundary_readiness=seal.final_boundary_readiness,
        receipt_status=seal.receipt_status,
        go_no_go_decision=seal.go_no_go_decision,
        receipt_decision=seal.receipt_decision,
        start_authorization=_next_session_launch_receipt_final_boundary_audit_seal_operator_start_authorization(
            packet_status
        ),
        sealed_first_step=seal.sealed_first_step,
        sealed_candidate_order=list(seal.sealed_candidate_order),
        operator_start_checklist=[
            "confirm_final_boundary_audit_seal_ready",
            "confirm_start_authorization",
            "confirm_sealed_first_step",
            "confirm_sealed_candidate_order",
            "confirm_pre_execution_boundary",
            "confirm_manual_only_execution",
        ],
        pre_execution_confirmation=list(seal.pre_execution_confirmation),
        verification_checklist=list(seal.verification_checklist),
        rollback_path=list(seal.rollback_path),
        post_completion_review=list(seal.post_completion_review),
        boundary_confirmation=list(seal.boundary_confirmation),
        target_candidates=list(seal.target_candidates),
        blocked_reasons=blocked_reasons,
        packet_checks=[
            "confirm_launch_receipt_final_boundary_audit_seal_ready",
            "confirm_start_authorization_ready",
            "confirm_sealed_first_step_ready",
            "confirm_operator_start_checklist_present",
            "confirm_verification_checklist_present",
            "confirm_rollback_path_present",
            "confirm_boundary_confirmation_present",
            "confirm_boundary_delta_zero",
        ],
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_LAUNCH_RECEIPT_FINAL_BOUNDARY_AUDIT_SEAL_OPERATOR_START_PACKET_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal Operator Start Packet",
        "",
        "## Summary",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Packet scope: `{packet.packet_scope}`",
        f"- Packet status: `{packet.packet_status}`",
        f"- Seal status: `{packet.seal_status}`",
        f"- Final boundary readiness: `{packet.final_boundary_readiness}`",
        f"- Receipt status: `{packet.receipt_status}`",
        f"- Go/no-go decision: `{packet.go_no_go_decision}`",
        f"- Receipt decision: `{packet.receipt_decision}`",
        f"- Start authorization: `{packet.start_authorization}`",
        f"- Sealed first step: `{packet.sealed_first_step}`",
        f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution operator start packet is read-only planning metadata.",
        "",
        "## Packet Checks",
        "",
    ]
    for item in packet.packet_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in packet.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Pre-Execution Confirmation", ""])
    for item in packet.pre_execution_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not packet.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(packet.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in packet.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in packet.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in packet.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in packet.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not packet.blocked_reasons:
        lines.append("No operator start packet blockers.")
    else:
        _append_code_markdown_list(lines, packet.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, packet.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_operator_start_packet_audit_coverage_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacket,
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSeal,
) -> dict[str, str]:
    expected_operator_start_checklist = [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    return {
        "packet_ready": (
            "covered"
            if packet.packet_status
            in {
                "ready_for_operator_start_packet",
                "no_manual_execution_required_operator_start_packet",
            }
            else "missing"
        ),
        "seal_status_preserved": (
            "covered" if packet.seal_status == seal.seal_status else "missing"
        ),
        "start_authorization_ready": (
            "covered"
            if packet.start_authorization
            in {
                "authorized_to_start_manual_execution",
                "no_manual_execution_required",
            }
            else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered" if packet.sealed_first_step == seal.sealed_first_step else "missing"
        ),
        "sealed_candidate_order_preserved": (
            "covered"
            if packet.sealed_candidate_order == seal.sealed_candidate_order
            else "missing"
        ),
        "operator_start_checklist_complete": (
            "covered"
            if all(
                item in packet.operator_start_checklist
                for item in expected_operator_start_checklist
            )
            else "missing"
        ),
        "verification_checklist_preserved": (
            "covered"
            if packet.verification_checklist == seal.verification_checklist
            else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if packet.rollback_path == seal.rollback_path else "missing"
        ),
        "post_completion_review_preserved": (
            "covered"
            if packet.post_completion_review == seal.post_completion_review
            else "missing"
        ),
        "target_candidates_preserved": (
            "covered" if packet.target_candidates == seal.target_candidates else "missing"
        ),
        "blocked_reasons_preserved": (
            "covered" if packet.blocked_reasons == seal.blocked_reasons else "missing"
        ),
        "boundary_confirmation_preserved": (
            "covered"
            if packet.boundary_confirmation == seal.boundary_confirmation
            else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                packet.applied_review_decision_delta == 0
                and packet.applied_candidate_status_delta == 0
                and packet.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_operator_start_packet_audit_boundary_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacket,
) -> dict[str, str]:
    return {
        "applied_review_decision_delta_zero": (
            "covered" if packet.applied_review_decision_delta == 0 else "missing"
        ),
        "applied_candidate_status_delta_zero": (
            "covered" if packet.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if packet.formal_evidence_delta == 0 else "missing"
        ),
        "operator_start_packet_read_only": (
            "covered"
            if (
                packet.applied_review_decision_delta == 0
                and packet.applied_candidate_status_delta == 0
                and packet.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_operator_start_packet_audit_status(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacket,
    missing_coverage: list[str],
) -> str:
    if packet.blocked_reasons or missing_coverage:
        return "blocked_before_operator_start_packet_audit"
    if packet.packet_status == "no_manual_execution_required_operator_start_packet":
        return "no_manual_execution_required_operator_start_packet_audit"
    return "operator_start_packet_audit_ready"


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAudit:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    coverage_checks = _next_session_operator_start_packet_audit_coverage_checks(
        packet,
        seal,
    )
    missing_coverage = [
        check for check, status in coverage_checks.items() if status != "covered"
    ]
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAudit(
        session_id=packet.session_id,
        audit_scope="manual_application_next_session_operator_start_packet_audit",
        audit_status=_next_session_operator_start_packet_audit_status(
            packet,
            missing_coverage,
        ),
        packet_status=packet.packet_status,
        seal_status=packet.seal_status,
        start_authorization=packet.start_authorization,
        coverage_checks=coverage_checks,
        missing_coverage=missing_coverage,
        boundary_checks=_next_session_operator_start_packet_audit_boundary_checks(
            packet
        ),
        sealed_first_step=packet.sealed_first_step,
        sealed_candidate_order=list(packet.sealed_candidate_order),
        operator_start_checklist=list(packet.operator_start_checklist),
        verification_checklist=list(packet.verification_checklist),
        rollback_path=list(packet.rollback_path),
        post_completion_review=list(packet.post_completion_review),
        target_candidates=list(packet.target_candidates),
        blocked_reasons=list(packet.blocked_reasons),
        boundary_confirmation=list(packet.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_OPERATOR_START_PACKET_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Operator Start Packet Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Packet status: `{audit.packet_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Start authorization: `{audit.start_authorization}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution operator start packet audit is read-only planning metadata.",
        "",
        "## Coverage Checks",
        "",
    ]
    for check, status in audit.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage and not audit.blocked_reasons:
        lines.append("No missing operator start packet audit coverage.")
    else:
        _append_code_markdown_list(
            lines,
            _dedupe_preserving_order([*audit.missing_coverage, *audit.blocked_reasons]),
        )

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in audit.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in audit.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not audit.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No operator start packet audit blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_operator_start_packet_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.audit_status not in {
        "operator_start_packet_audit_ready",
        "no_manual_execution_required_operator_start_packet_audit",
    }:
        reasons.append("operator_start_packet_audit_not_ready")
    reasons.extend(audit.missing_coverage)
    reasons.extend(audit.blocked_reasons)
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.operator_start_checklist:
        reasons.append("operator_start_checklist_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_operator_start_packet_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_operator_start_packet_audit_seal"
    if audit.audit_status == "no_manual_execution_required_operator_start_packet_audit":
        return "sealed_no_manual_execution_required_operator_start_packet_audit"
    return "sealed_for_operator_start_packet_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAuditSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_operator_start_packet_audit_seal_blocked_reasons(
        audit
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAuditSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_operator_start_packet_audit_seal",
        seal_status=_next_session_operator_start_packet_audit_seal_status(
            audit,
            blocked_reasons,
        ),
        audit_status=audit.audit_status,
        packet_status=audit.packet_status,
        start_authorization=audit.start_authorization,
        blocked_reasons=blocked_reasons,
        seal_checks=[
            "confirm_operator_start_packet_audit_ready",
            "confirm_coverage_complete",
            "confirm_boundary_checks_complete",
            "confirm_start_authorization_preserved",
            "confirm_sealed_first_step_preserved",
            "confirm_operator_start_checklist_present",
            "confirm_verification_checklist_present",
            "confirm_boundary_delta_zero",
        ],
        coverage_checks=dict(audit.coverage_checks),
        missing_coverage=list(audit.missing_coverage),
        boundary_checks=dict(audit.boundary_checks),
        sealed_first_step=audit.sealed_first_step,
        sealed_candidate_order=list(audit.sealed_candidate_order),
        operator_start_checklist=list(audit.operator_start_checklist),
        verification_checklist=list(audit.verification_checklist),
        rollback_path=list(audit.rollback_path),
        post_completion_review=list(audit.post_completion_review),
        target_candidates=list(audit.target_candidates),
        boundary_confirmation=list(audit.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_OPERATOR_START_PACKET_AUDIT_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Operator Start Packet Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Packet status: `{seal.packet_status}`",
        f"- Start authorization: `{seal.start_authorization}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution operator start packet audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Checks", ""])
    for check, status in seal.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage and not seal.blocked_reasons:
        lines.append("No operator start packet audit seal blockers.")
    else:
        _append_code_markdown_list(
            lines,
            _dedupe_preserving_order([*seal.missing_coverage, *seal.blocked_reasons]),
        )

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in seal.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in seal.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No operator start packet audit seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_start_authorization_receipt_blocked_reasons(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAuditSeal,
) -> list[str]:
    reasons: list[str] = []
    if seal.seal_status not in {
        "sealed_for_operator_start_packet_audit",
        "sealed_no_manual_execution_required_operator_start_packet_audit",
    }:
        reasons.append("operator_start_packet_audit_seal_not_ready")
    reasons.extend(seal.blocked_reasons)
    if seal.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    if not seal.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not seal.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not seal.operator_start_checklist:
        reasons.append("operator_start_checklist_missing")
    if not seal.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not seal.rollback_path:
        reasons.append("rollback_path_missing")
    if not seal.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        seal.applied_review_decision_delta != 0
        or seal.applied_candidate_status_delta != 0
        or seal.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_start_authorization_receipt_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAuditSeal,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_authorization_receipt"
    if seal.seal_status == "sealed_no_manual_execution_required_operator_start_packet_audit":
        return "no_manual_execution_required_start_authorization_receipt"
    return "ready_for_manual_execution_start_authorization_receipt"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceipt:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_start_authorization_receipt_blocked_reasons(
        seal
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceipt(
        session_id=seal.session_id,
        receipt_scope="manual_application_next_session_manual_execution_start_authorization_receipt",
        receipt_status=_next_session_start_authorization_receipt_status(
            seal,
            blocked_reasons,
        ),
        seal_status=seal.seal_status,
        audit_status=seal.audit_status,
        packet_status=seal.packet_status,
        start_authorization=seal.start_authorization,
        sealed_first_step=seal.sealed_first_step,
        sealed_candidate_order=list(seal.sealed_candidate_order),
        operator_start_checklist=list(seal.operator_start_checklist),
        verification_checklist=list(seal.verification_checklist),
        rollback_path=list(seal.rollback_path),
        post_completion_review=list(seal.post_completion_review),
        target_candidates=list(seal.target_candidates),
        blocked_reasons=blocked_reasons,
        receipt_checks=[
            "confirm_operator_start_packet_audit_seal_ready",
            "confirm_start_authorization",
            "confirm_sealed_first_step",
            "confirm_sealed_candidate_order",
            "confirm_operator_start_checklist",
            "confirm_verification_checklist",
            "confirm_rollback_path",
            "confirm_boundary_confirmation",
            "confirm_boundary_delta_zero",
        ],
        boundary_confirmation=list(seal.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_START_AUTHORIZATION_RECEIPT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    receipt = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Receipt",
        "",
        "## Summary",
        "",
        f"- Session id: `{receipt.session_id}`",
        f"- Receipt scope: `{receipt.receipt_scope}`",
        f"- Receipt status: `{receipt.receipt_status}`",
        f"- Seal status: `{receipt.seal_status}`",
        f"- Audit status: `{receipt.audit_status}`",
        f"- Packet status: `{receipt.packet_status}`",
        f"- Start authorization: `{receipt.start_authorization}`",
        f"- Sealed first step: `{receipt.sealed_first_step}`",
        f"- Applied review decision delta: `{receipt.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{receipt.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{receipt.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start authorization receipt is read-only planning metadata.",
        "",
        "## Receipt Checks",
        "",
    ]
    for item in receipt.receipt_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in receipt.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not receipt.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(receipt.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in receipt.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in receipt.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in receipt.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in receipt.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not receipt.blocked_reasons:
        lines.append("No start authorization receipt blockers.")
    else:
        _append_code_markdown_list(lines, receipt.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, receipt.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(receipt.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_start_authorization_receipt_coverage_checks(
    receipt: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceipt,
    seal: CandidateReviewManualApplicationNextSessionManualExecutionLaunchReceiptFinalBoundaryAuditSealOperatorStartPacketAuditSeal,
) -> dict[str, str]:
    expected_receipt_checks = [
        "confirm_operator_start_packet_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_operator_start_checklist",
        "confirm_verification_checklist",
        "confirm_rollback_path",
        "confirm_boundary_confirmation",
        "confirm_boundary_delta_zero",
    ]
    return {
        "receipt_ready": (
            "covered"
            if receipt.receipt_status
            in {
                "ready_for_manual_execution_start_authorization_receipt",
                "no_manual_execution_required_start_authorization_receipt",
            }
            else "missing"
        ),
        "seal_status_preserved": (
            "covered" if receipt.seal_status == seal.seal_status else "missing"
        ),
        "operator_start_packet_audit_status_preserved": (
            "covered" if receipt.audit_status == seal.audit_status else "missing"
        ),
        "packet_status_preserved": (
            "covered" if receipt.packet_status == seal.packet_status else "missing"
        ),
        "start_authorization_preserved": (
            "covered"
            if receipt.start_authorization == seal.start_authorization
            else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered" if receipt.sealed_first_step == seal.sealed_first_step else "missing"
        ),
        "sealed_candidate_order_preserved": (
            "covered"
            if receipt.sealed_candidate_order == seal.sealed_candidate_order
            else "missing"
        ),
        "operator_start_checklist_preserved": (
            "covered"
            if receipt.operator_start_checklist == seal.operator_start_checklist
            else "missing"
        ),
        "verification_checklist_preserved": (
            "covered"
            if receipt.verification_checklist == seal.verification_checklist
            else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if receipt.rollback_path == seal.rollback_path else "missing"
        ),
        "post_completion_review_preserved": (
            "covered"
            if receipt.post_completion_review == seal.post_completion_review
            else "missing"
        ),
        "target_candidates_preserved": (
            "covered" if receipt.target_candidates == seal.target_candidates else "missing"
        ),
        "blocked_reasons_preserved": (
            "covered" if receipt.blocked_reasons == seal.blocked_reasons else "missing"
        ),
        "receipt_checks_present": (
            "covered"
            if all(item in receipt.receipt_checks for item in expected_receipt_checks)
            else "missing"
        ),
        "boundary_confirmation_preserved": (
            "covered"
            if receipt.boundary_confirmation == seal.boundary_confirmation
            else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                receipt.applied_review_decision_delta == 0
                and receipt.applied_candidate_status_delta == 0
                and receipt.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_start_authorization_receipt_coverage_audit_boundary_checks(
    receipt: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceipt,
) -> dict[str, str]:
    return {
        "start_authorization_receipt_read_only": (
            "covered"
            if (
                receipt.applied_review_decision_delta == 0
                and receipt.applied_candidate_status_delta == 0
                and receipt.formal_evidence_delta == 0
            )
            else "missing"
        ),
        "review_decision_delta_zero": (
            "covered" if receipt.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if receipt.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if receipt.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_start_authorization_receipt_coverage_audit_status(
    receipt: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceipt,
    missing_coverage: list[str],
) -> str:
    if receipt.blocked_reasons or missing_coverage:
        return "blocked_before_start_authorization_receipt_coverage_audit"
    if receipt.receipt_status == "no_manual_execution_required_start_authorization_receipt":
        return "no_manual_execution_required_start_authorization_receipt_coverage_audit"
    return "start_authorization_receipt_coverage_audit_ready"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAudit:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    receipt = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    coverage_checks = _next_session_start_authorization_receipt_coverage_checks(
        receipt,
        seal,
    )
    boundary_checks = (
        _next_session_start_authorization_receipt_coverage_audit_boundary_checks(
            receipt
        )
    )
    missing_coverage = [
        check
        for check, status in {
            **coverage_checks,
            **boundary_checks,
        }.items()
        if status != "covered"
    ]
    return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAudit(
        session_id=receipt.session_id,
        audit_scope="manual_application_next_session_start_authorization_receipt_coverage_audit",
        coverage_audit_status=_next_session_start_authorization_receipt_coverage_audit_status(
            receipt,
            missing_coverage,
        ),
        receipt_status=receipt.receipt_status,
        seal_status=receipt.seal_status,
        operator_start_packet_audit_status=receipt.audit_status,
        packet_status=receipt.packet_status,
        start_authorization=receipt.start_authorization,
        coverage_checks=coverage_checks,
        missing_coverage=missing_coverage,
        boundary_checks=boundary_checks,
        sealed_first_step=receipt.sealed_first_step,
        sealed_candidate_order=list(receipt.sealed_candidate_order),
        operator_start_checklist=list(receipt.operator_start_checklist),
        verification_checklist=list(receipt.verification_checklist),
        rollback_path=list(receipt.rollback_path),
        post_completion_review=list(receipt.post_completion_review),
        target_candidates=list(receipt.target_candidates),
        blocked_reasons=list(receipt.blocked_reasons),
        boundary_confirmation=list(receipt.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_START_AUTHORIZATION_RECEIPT_COVERAGE_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Coverage audit status: `{audit.coverage_audit_status}`",
        f"- Receipt status: `{audit.receipt_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Operator start packet audit status: `{audit.operator_start_packet_audit_status}`",
        f"- Packet status: `{audit.packet_status}`",
        f"- Start authorization: `{audit.start_authorization}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start authorization receipt coverage audit is read-only planning metadata.",
        "",
        "## Coverage Checks",
        "",
    ]
    for check, status in audit.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage and not audit.blocked_reasons:
        lines.append("No start authorization receipt coverage gaps.")
    else:
        _append_code_markdown_list(
            lines,
            _dedupe_preserving_order([*audit.missing_coverage, *audit.blocked_reasons]),
        )

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in audit.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in audit.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not audit.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No start authorization receipt coverage audit blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_start_authorization_receipt_coverage_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.coverage_audit_status not in {
        "start_authorization_receipt_coverage_audit_ready",
        "no_manual_execution_required_start_authorization_receipt_coverage_audit",
    }:
        reasons.append("start_authorization_receipt_coverage_audit_not_ready")
    reasons.extend(audit.blocked_reasons)
    reasons.extend(audit.missing_coverage)
    if any(status != "covered" for status in audit.coverage_checks.values()):
        reasons.append("coverage_checks_incomplete")
    if any(status != "covered" for status in audit.boundary_checks.values()):
        reasons.append("boundary_checks_incomplete")
    if audit.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.operator_start_checklist:
        reasons.append("operator_start_checklist_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.rollback_path:
        reasons.append("rollback_path_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_start_authorization_receipt_coverage_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_start_authorization_receipt_coverage_audit_seal"
    if audit.coverage_audit_status == "no_manual_execution_required_start_authorization_receipt_coverage_audit":
        return "sealed_no_manual_execution_required_start_authorization_receipt_coverage_audit"
    return "sealed_for_start_authorization_receipt_coverage_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAuditSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = (
        _next_session_start_authorization_receipt_coverage_audit_seal_blocked_reasons(
            audit
        )
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAuditSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_start_authorization_receipt_coverage_audit_seal",
        seal_status=_next_session_start_authorization_receipt_coverage_audit_seal_status(
            audit,
            blocked_reasons,
        ),
        coverage_audit_status=audit.coverage_audit_status,
        receipt_status=audit.receipt_status,
        operator_start_packet_audit_seal_status=audit.seal_status,
        operator_start_packet_audit_status=audit.operator_start_packet_audit_status,
        packet_status=audit.packet_status,
        start_authorization=audit.start_authorization,
        blocked_reasons=blocked_reasons,
        seal_checks=[
            "confirm_start_authorization_receipt_coverage_audit_ready",
            "confirm_receipt_ready",
            "confirm_coverage_complete",
            "confirm_boundary_checks_complete",
            "confirm_start_authorization_preserved",
            "confirm_sealed_first_step_preserved",
            "confirm_sealed_candidate_order_preserved",
            "confirm_boundary_delta_zero",
        ],
        coverage_checks=dict(audit.coverage_checks),
        missing_coverage=list(audit.missing_coverage),
        boundary_checks=dict(audit.boundary_checks),
        sealed_first_step=audit.sealed_first_step,
        sealed_candidate_order=list(audit.sealed_candidate_order),
        operator_start_checklist=list(audit.operator_start_checklist),
        verification_checklist=list(audit.verification_checklist),
        rollback_path=list(audit.rollback_path),
        post_completion_review=list(audit.post_completion_review),
        target_candidates=list(audit.target_candidates),
        boundary_confirmation=list(audit.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_START_AUTHORIZATION_RECEIPT_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Coverage audit status: `{seal.coverage_audit_status}`",
        f"- Receipt status: `{seal.receipt_status}`",
        f"- Operator start packet audit seal status: `{seal.operator_start_packet_audit_seal_status}`",
        f"- Operator start packet audit status: `{seal.operator_start_packet_audit_status}`",
        f"- Packet status: `{seal.packet_status}`",
        f"- Start authorization: `{seal.start_authorization}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start authorization receipt coverage audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Checks", ""])
    for check, status in seal.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage and not seal.blocked_reasons:
        lines.append("No start authorization receipt coverage audit seal blockers.")
    else:
        _append_code_markdown_list(
            lines,
            _dedupe_preserving_order([*seal.missing_coverage, *seal.blocked_reasons]),
        )

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in seal.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in seal.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No start authorization receipt coverage audit seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_authorization_packet_blocked_reasons(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAuditSeal,
) -> list[str]:
    reasons: list[str] = []
    if seal.seal_status not in {
        "sealed_for_start_authorization_receipt_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_receipt_coverage_audit",
    }:
        reasons.append("start_authorization_receipt_coverage_audit_seal_not_ready")
    reasons.extend(seal.blocked_reasons)
    if seal.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    if not seal.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not seal.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not seal.operator_start_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not seal.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not seal.rollback_path:
        reasons.append("rollback_path_missing")
    if not seal.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        seal.applied_review_decision_delta != 0
        or seal.applied_candidate_status_delta != 0
        or seal.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_authorization_packet_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAuditSeal,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_authorization_packet"
    if seal.seal_status == "sealed_no_manual_execution_required_start_authorization_receipt_coverage_audit":
        return "no_manual_execution_required_authorization_packet"
    return "ready_for_manual_execution_authorization_packet"


def build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacket:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_manual_execution_authorization_packet_blocked_reasons(
        seal
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacket(
        session_id=seal.session_id,
        packet_scope="manual_application_next_session_manual_execution_authorization_packet",
        packet_status=_next_session_manual_execution_authorization_packet_status(
            seal,
            blocked_reasons,
        ),
        seal_status=seal.seal_status,
        coverage_audit_status=seal.coverage_audit_status,
        receipt_status=seal.receipt_status,
        operator_start_packet_audit_status=seal.operator_start_packet_audit_status,
        start_authorization=seal.start_authorization,
        sealed_first_step=seal.sealed_first_step,
        authorization_checks=[
            "confirm_start_authorization_receipt_coverage_audit_seal_ready",
            "confirm_start_authorization",
            "confirm_sealed_first_step",
            "confirm_sealed_candidate_order",
            "confirm_operator_authorization_checklist",
            "confirm_verification_checklist",
            "confirm_rollback_path",
            "confirm_boundary_confirmation",
            "confirm_boundary_delta_zero",
        ],
        sealed_candidate_order=list(seal.sealed_candidate_order),
        operator_authorization_checklist=list(seal.operator_start_checklist),
        verification_checklist=list(seal.verification_checklist),
        rollback_path=list(seal.rollback_path),
        post_completion_review=list(seal.post_completion_review),
        target_candidates=list(seal.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(seal.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_AUTHORIZATION_PACKET_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet",
        "",
        "## Summary",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Packet scope: `{packet.packet_scope}`",
        f"- Packet status: `{packet.packet_status}`",
        f"- Seal status: `{packet.seal_status}`",
        f"- Coverage audit status: `{packet.coverage_audit_status}`",
        f"- Receipt status: `{packet.receipt_status}`",
        f"- Operator start packet audit status: `{packet.operator_start_packet_audit_status}`",
        f"- Start authorization: `{packet.start_authorization}`",
        f"- Sealed first step: `{packet.sealed_first_step}`",
        f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution authorization packet is read-only planning metadata.",
        "",
        "## Authorization Checks",
        "",
    ]
    for item in packet.authorization_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in packet.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not packet.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(packet.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in packet.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in packet.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in packet.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in packet.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not packet.blocked_reasons:
        lines.append("No manual execution authorization packet blockers.")
    else:
        _append_code_markdown_list(lines, packet.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, packet.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_authorization_packet_coverage_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacket,
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationReceiptCoverageAuditSeal,
) -> dict[str, str]:
    expected_authorization_checks = [
        "confirm_start_authorization_receipt_coverage_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_operator_authorization_checklist",
        "confirm_verification_checklist",
        "confirm_rollback_path",
        "confirm_boundary_confirmation",
        "confirm_boundary_delta_zero",
    ]
    return {
        "packet_ready": (
            "covered"
            if packet.packet_status
            in {
                "ready_for_manual_execution_authorization_packet",
                "no_manual_execution_required_authorization_packet",
            }
            else "missing"
        ),
        "seal_status_preserved": (
            "covered" if packet.seal_status == seal.seal_status else "missing"
        ),
        "coverage_audit_status_preserved": (
            "covered"
            if packet.coverage_audit_status == seal.coverage_audit_status
            else "missing"
        ),
        "receipt_status_preserved": (
            "covered" if packet.receipt_status == seal.receipt_status else "missing"
        ),
        "operator_start_packet_audit_status_preserved": (
            "covered"
            if packet.operator_start_packet_audit_status
            == seal.operator_start_packet_audit_status
            else "missing"
        ),
        "start_authorization_preserved": (
            "covered"
            if packet.start_authorization == seal.start_authorization
            else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered" if packet.sealed_first_step == seal.sealed_first_step else "missing"
        ),
        "sealed_candidate_order_preserved": (
            "covered"
            if packet.sealed_candidate_order == seal.sealed_candidate_order
            else "missing"
        ),
        "operator_authorization_checklist_preserved": (
            "covered"
            if packet.operator_authorization_checklist == seal.operator_start_checklist
            else "missing"
        ),
        "verification_checklist_preserved": (
            "covered"
            if packet.verification_checklist == seal.verification_checklist
            else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if packet.rollback_path == seal.rollback_path else "missing"
        ),
        "post_completion_review_preserved": (
            "covered"
            if packet.post_completion_review == seal.post_completion_review
            else "missing"
        ),
        "target_candidates_preserved": (
            "covered" if packet.target_candidates == seal.target_candidates else "missing"
        ),
        "blocked_reasons_preserved": (
            "covered" if packet.blocked_reasons == seal.blocked_reasons else "missing"
        ),
        "authorization_checks_present": (
            "covered"
            if all(
                item in packet.authorization_checks
                for item in expected_authorization_checks
            )
            else "missing"
        ),
        "boundary_confirmation_preserved": (
            "covered"
            if packet.boundary_confirmation == seal.boundary_confirmation
            else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                packet.applied_review_decision_delta == 0
                and packet.applied_candidate_status_delta == 0
                and packet.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_manual_execution_authorization_packet_coverage_audit_boundary_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacket,
) -> dict[str, str]:
    return {
        "authorization_packet_read_only": (
            "covered"
            if (
                packet.applied_review_decision_delta == 0
                and packet.applied_candidate_status_delta == 0
                and packet.formal_evidence_delta == 0
            )
            else "missing"
        ),
        "review_decision_delta_zero": (
            "covered" if packet.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if packet.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if packet.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_authorization_packet_coverage_audit_status(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacket,
    missing_coverage: list[str],
) -> str:
    if packet.blocked_reasons or missing_coverage:
        return "blocked_before_manual_execution_authorization_packet_coverage_audit"
    if packet.packet_status == "no_manual_execution_required_authorization_packet":
        return "no_manual_execution_required_authorization_packet_coverage_audit"
    return "manual_execution_authorization_packet_coverage_audit_ready"


def build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAudit:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    packet_coverage_checks = (
        _next_session_manual_execution_authorization_packet_coverage_checks(
            packet,
            seal,
        )
    )
    boundary_checks = (
        _next_session_manual_execution_authorization_packet_coverage_audit_boundary_checks(
            packet
        )
    )
    missing_coverage = [
        check
        for check, status in {
            **packet_coverage_checks,
            **boundary_checks,
        }.items()
        if status != "covered"
    ]
    return CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAudit(
        session_id=packet.session_id,
        audit_scope="manual_application_next_session_manual_execution_authorization_packet_coverage_audit",
        audit_status=_next_session_manual_execution_authorization_packet_coverage_audit_status(
            packet,
            missing_coverage,
        ),
        packet_status=packet.packet_status,
        seal_status=packet.seal_status,
        coverage_audit_status=packet.coverage_audit_status,
        receipt_status=packet.receipt_status,
        operator_start_packet_audit_status=packet.operator_start_packet_audit_status,
        start_authorization=packet.start_authorization,
        packet_coverage_checks=packet_coverage_checks,
        missing_coverage=missing_coverage,
        boundary_checks=boundary_checks,
        sealed_first_step=packet.sealed_first_step,
        sealed_candidate_order=list(packet.sealed_candidate_order),
        operator_authorization_checklist=list(
            packet.operator_authorization_checklist
        ),
        verification_checklist=list(packet.verification_checklist),
        rollback_path=list(packet.rollback_path),
        post_completion_review=list(packet.post_completion_review),
        target_candidates=list(packet.target_candidates),
        blocked_reasons=list(packet.blocked_reasons),
        boundary_confirmation=list(packet.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_AUTHORIZATION_PACKET_COVERAGE_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Packet status: `{audit.packet_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Coverage audit status: `{audit.coverage_audit_status}`",
        f"- Receipt status: `{audit.receipt_status}`",
        f"- Operator start packet audit status: `{audit.operator_start_packet_audit_status}`",
        f"- Start authorization: `{audit.start_authorization}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution authorization packet coverage audit is read-only planning metadata.",
        "",
        "## Packet Coverage Checks",
        "",
    ]
    for check, status in audit.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage and not audit.blocked_reasons:
        lines.append("No manual execution authorization packet coverage gaps.")
    else:
        _append_code_markdown_list(
            lines,
            _dedupe_preserving_order([*audit.missing_coverage, *audit.blocked_reasons]),
        )

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in audit.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in audit.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not audit.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No manual execution authorization packet coverage audit blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_authorization_packet_coverage_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.audit_status not in {
        "manual_execution_authorization_packet_coverage_audit_ready",
        "no_manual_execution_required_authorization_packet_coverage_audit",
    }:
        reasons.append("manual_execution_authorization_packet_coverage_audit_not_ready")
    if audit.packet_status not in {
        "ready_for_manual_execution_authorization_packet",
        "no_manual_execution_required_authorization_packet",
    }:
        reasons.append("manual_execution_authorization_packet_not_ready")
    reasons.extend(audit.blocked_reasons)
    reasons.extend(audit.missing_coverage)
    if any(status != "covered" for status in audit.packet_coverage_checks.values()):
        reasons.append("packet_coverage_checks_incomplete")
    if any(status != "covered" for status in audit.boundary_checks.values()):
        reasons.append("boundary_checks_incomplete")
    if audit.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.rollback_path:
        reasons.append("rollback_path_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_authorization_packet_coverage_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_authorization_packet_coverage_audit_seal"
    if audit.audit_status == "no_manual_execution_required_authorization_packet_coverage_audit":
        return "sealed_no_manual_execution_required_manual_execution_authorization_packet_coverage_audit"
    return "sealed_for_manual_execution_authorization_packet_coverage_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_manual_execution_authorization_packet_coverage_audit_seal_blocked_reasons(
        audit
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal",
        seal_status=_next_session_manual_execution_authorization_packet_coverage_audit_seal_status(
            audit,
            blocked_reasons,
        ),
        audit_status=audit.audit_status,
        packet_status=audit.packet_status,
        authorization_packet_seal_status=audit.seal_status,
        coverage_audit_status=audit.coverage_audit_status,
        receipt_status=audit.receipt_status,
        operator_start_packet_audit_status=audit.operator_start_packet_audit_status,
        start_authorization=audit.start_authorization,
        seal_checks=[
            "confirm_manual_execution_authorization_packet_coverage_audit_ready",
            "confirm_packet_ready",
            "confirm_coverage_complete",
            "confirm_boundary_checks_complete",
            "confirm_start_authorization_preserved",
            "confirm_sealed_first_step_preserved",
            "confirm_sealed_candidate_order_preserved",
            "confirm_boundary_delta_zero",
        ],
        packet_coverage_checks=dict(audit.packet_coverage_checks),
        missing_coverage=list(audit.missing_coverage),
        boundary_checks=dict(audit.boundary_checks),
        sealed_first_step=audit.sealed_first_step,
        sealed_candidate_order=list(audit.sealed_candidate_order),
        operator_authorization_checklist=list(
            audit.operator_authorization_checklist
        ),
        verification_checklist=list(audit.verification_checklist),
        rollback_path=list(audit.rollback_path),
        post_completion_review=list(audit.post_completion_review),
        target_candidates=list(audit.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(audit.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_AUTHORIZATION_PACKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Packet status: `{seal.packet_status}`",
        f"- Authorization packet seal status: `{seal.authorization_packet_seal_status}`",
        f"- Coverage audit status: `{seal.coverage_audit_status}`",
        f"- Receipt status: `{seal.receipt_status}`",
        f"- Operator start packet audit status: `{seal.operator_start_packet_audit_status}`",
        f"- Start authorization: `{seal.start_authorization}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution authorization packet coverage audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in seal.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage and not seal.blocked_reasons:
        lines.append("No manual execution authorization packet coverage audit seal blockers.")
    else:
        _append_code_markdown_list(
            lines,
            _dedupe_preserving_order([*seal.missing_coverage, *seal.blocked_reasons]),
        )

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in seal.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in seal.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No manual execution authorization packet coverage audit seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_docket_blocked_reasons(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSeal,
) -> list[str]:
    reasons: list[str] = []
    if seal.seal_status not in {
        "sealed_for_manual_execution_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_manual_execution_authorization_packet_coverage_audit",
    }:
        reasons.append("manual_execution_authorization_packet_coverage_audit_seal_not_ready")
    if seal.audit_status not in {
        "manual_execution_authorization_packet_coverage_audit_ready",
        "no_manual_execution_required_authorization_packet_coverage_audit",
    }:
        reasons.append("manual_execution_authorization_packet_coverage_audit_not_ready")
    if seal.packet_status not in {
        "ready_for_manual_execution_authorization_packet",
        "no_manual_execution_required_authorization_packet",
    }:
        reasons.append("manual_execution_authorization_packet_not_ready")
    reasons.extend(seal.blocked_reasons)
    reasons.extend(seal.missing_coverage)
    if any(status != "covered" for status in seal.packet_coverage_checks.values()):
        reasons.append("packet_coverage_checks_incomplete")
    if any(status != "covered" for status in seal.boundary_checks.values()):
        reasons.append("boundary_checks_incomplete")
    if seal.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    if not seal.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not seal.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not seal.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not seal.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not seal.rollback_path:
        reasons.append("rollback_path_missing")
    if not seal.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        seal.applied_review_decision_delta != 0
        or seal.applied_candidate_status_delta != 0
        or seal.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_docket_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSeal,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_docket"
    if seal.seal_status == "sealed_no_manual_execution_required_manual_execution_authorization_packet_coverage_audit":
        return "no_manual_execution_required_start_docket"
    return "ready_for_manual_execution_start_docket"


def build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSealStartDocket:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_manual_execution_start_docket_blocked_reasons(
        seal
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSealStartDocket(
        session_id=seal.session_id,
        docket_scope="manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket",
        docket_status=_next_session_manual_execution_start_docket_status(
            seal,
            blocked_reasons,
        ),
        seal_status=seal.seal_status,
        audit_status=seal.audit_status,
        packet_status=seal.packet_status,
        authorization_packet_seal_status=seal.authorization_packet_seal_status,
        coverage_audit_status=seal.coverage_audit_status,
        receipt_status=seal.receipt_status,
        operator_start_packet_audit_status=seal.operator_start_packet_audit_status,
        start_authorization=seal.start_authorization,
        docket_checks=[
            "confirm_authorization_packet_coverage_audit_seal_ready",
            "confirm_audit_ready",
            "confirm_packet_ready",
            "confirm_start_authorization",
            "confirm_sealed_first_step",
            "confirm_sealed_candidate_order",
            "confirm_operator_authorization_checklist",
            "confirm_verification_checklist",
            "confirm_rollback_path",
            "confirm_boundary_confirmation",
            "confirm_boundary_delta_zero",
        ],
        sealed_first_step=seal.sealed_first_step,
        sealed_candidate_order=list(seal.sealed_candidate_order),
        operator_authorization_checklist=list(
            seal.operator_authorization_checklist
        ),
        verification_checklist=list(seal.verification_checklist),
        rollback_path=list(seal.rollback_path),
        post_completion_review=list(seal.post_completion_review),
        target_candidates=list(seal.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(seal.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_DOCKET_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    docket = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit Seal Start Docket",
        "",
        "## Summary",
        "",
        f"- Session id: `{docket.session_id}`",
        f"- Docket scope: `{docket.docket_scope}`",
        f"- Docket status: `{docket.docket_status}`",
        f"- Seal status: `{docket.seal_status}`",
        f"- Audit status: `{docket.audit_status}`",
        f"- Packet status: `{docket.packet_status}`",
        f"- Authorization packet seal status: `{docket.authorization_packet_seal_status}`",
        f"- Coverage audit status: `{docket.coverage_audit_status}`",
        f"- Receipt status: `{docket.receipt_status}`",
        f"- Operator start packet audit status: `{docket.operator_start_packet_audit_status}`",
        f"- Start authorization: `{docket.start_authorization}`",
        f"- Sealed first step: `{docket.sealed_first_step}`",
        f"- Applied review decision delta: `{docket.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{docket.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{docket.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start docket is read-only planning metadata.",
        "",
        "## Docket Checks",
        "",
    ]
    for item in docket.docket_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in docket.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not docket.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(docket.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in docket.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in docket.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in docket.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in docket.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not docket.blocked_reasons:
        lines.append("No manual execution start docket blockers.")
    else:
        _append_code_markdown_list(lines, docket.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, docket.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(docket.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_docket_coverage_checks(
    docket: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSealStartDocket,
    seal: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSeal,
) -> dict[str, str]:
    expected_docket_checks = {
        "confirm_authorization_packet_coverage_audit_seal_ready",
        "confirm_audit_ready",
        "confirm_packet_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_operator_authorization_checklist",
        "confirm_verification_checklist",
        "confirm_rollback_path",
        "confirm_boundary_confirmation",
        "confirm_boundary_delta_zero",
    }
    return {
        "docket_ready": (
            "covered"
            if docket.docket_status
            in {
                "ready_for_manual_execution_start_docket",
                "no_manual_execution_required_start_docket",
            }
            else "missing"
        ),
        "seal_status_preserved": (
            "covered" if docket.seal_status == seal.seal_status else "missing"
        ),
        "audit_status_preserved": (
            "covered" if docket.audit_status == seal.audit_status else "missing"
        ),
        "packet_status_preserved": (
            "covered" if docket.packet_status == seal.packet_status else "missing"
        ),
        "authorization_packet_seal_status_preserved": (
            "covered"
            if docket.authorization_packet_seal_status
            == seal.authorization_packet_seal_status
            else "missing"
        ),
        "coverage_audit_status_preserved": (
            "covered"
            if docket.coverage_audit_status == seal.coverage_audit_status
            else "missing"
        ),
        "receipt_status_preserved": (
            "covered" if docket.receipt_status == seal.receipt_status else "missing"
        ),
        "operator_start_packet_audit_status_preserved": (
            "covered"
            if docket.operator_start_packet_audit_status
            == seal.operator_start_packet_audit_status
            else "missing"
        ),
        "start_authorization_preserved": (
            "covered"
            if docket.start_authorization == seal.start_authorization
            else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered"
            if docket.sealed_first_step == seal.sealed_first_step
            else "missing"
        ),
        "sealed_candidate_order_preserved": (
            "covered"
            if docket.sealed_candidate_order == seal.sealed_candidate_order
            else "missing"
        ),
        "operator_authorization_checklist_preserved": (
            "covered"
            if docket.operator_authorization_checklist
            == seal.operator_authorization_checklist
            else "missing"
        ),
        "verification_checklist_preserved": (
            "covered"
            if docket.verification_checklist == seal.verification_checklist
            else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if docket.rollback_path == seal.rollback_path else "missing"
        ),
        "post_completion_review_preserved": (
            "covered"
            if docket.post_completion_review == seal.post_completion_review
            else "missing"
        ),
        "target_candidates_preserved": (
            "covered"
            if docket.target_candidates == seal.target_candidates
            else "missing"
        ),
        "blocked_reasons_preserved": (
            "covered"
            if docket.blocked_reasons == seal.blocked_reasons
            else "missing"
        ),
        "docket_checks_present": (
            "covered"
            if expected_docket_checks.issubset(set(docket.docket_checks))
            else "missing"
        ),
        "boundary_confirmation_preserved": (
            "covered"
            if docket.boundary_confirmation == seal.boundary_confirmation
            else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                docket.applied_review_decision_delta == 0
                and docket.applied_candidate_status_delta == 0
                and docket.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_manual_execution_start_docket_coverage_audit_boundary_checks(
    docket: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSealStartDocket,
) -> dict[str, str]:
    return {
        "start_docket_read_only": (
            "covered"
            if (
                docket.applied_review_decision_delta == 0
                and docket.applied_candidate_status_delta == 0
                and docket.formal_evidence_delta == 0
            )
            else "missing"
        ),
        "review_decision_delta_zero": (
            "covered" if docket.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if docket.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if docket.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_docket_coverage_audit_status(
    docket: CandidateReviewManualApplicationNextSessionManualExecutionAuthorizationPacketCoverageAuditSealStartDocket,
    missing_coverage: list[str],
) -> str:
    if docket.blocked_reasons or missing_coverage:
        return "blocked_before_manual_execution_start_docket_coverage_audit"
    if docket.docket_status == "no_manual_execution_required_start_docket":
        return "no_manual_execution_required_start_docket_coverage_audit"
    return "manual_execution_start_docket_coverage_audit_ready"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAudit:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    docket = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    docket_coverage_checks = _next_session_manual_execution_start_docket_coverage_checks(
        docket,
        seal,
    )
    boundary_checks = (
        _next_session_manual_execution_start_docket_coverage_audit_boundary_checks(
            docket
        )
    )
    missing_coverage = [
        check
        for check, status in {
            **docket_coverage_checks,
            **boundary_checks,
        }.items()
        if status != "covered"
    ]
    return CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAudit(
        session_id=docket.session_id,
        audit_scope="manual_application_next_session_manual_execution_start_docket_coverage_audit",
        audit_status=_next_session_manual_execution_start_docket_coverage_audit_status(
            docket,
            missing_coverage,
        ),
        docket_status=docket.docket_status,
        seal_status=docket.seal_status,
        audit_source_status=docket.audit_status,
        packet_status=docket.packet_status,
        authorization_packet_seal_status=docket.authorization_packet_seal_status,
        coverage_audit_status=docket.coverage_audit_status,
        receipt_status=docket.receipt_status,
        operator_start_packet_audit_status=docket.operator_start_packet_audit_status,
        start_authorization=docket.start_authorization,
        docket_coverage_checks=docket_coverage_checks,
        missing_coverage=missing_coverage,
        boundary_checks=boundary_checks,
        sealed_first_step=docket.sealed_first_step,
        sealed_candidate_order=list(docket.sealed_candidate_order),
        operator_authorization_checklist=list(
            docket.operator_authorization_checklist
        ),
        verification_checklist=list(docket.verification_checklist),
        rollback_path=list(docket.rollback_path),
        post_completion_review=list(docket.post_completion_review),
        target_candidates=list(docket.target_candidates),
        blocked_reasons=list(docket.blocked_reasons),
        boundary_confirmation=list(docket.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_DOCKET_COVERAGE_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Docket status: `{audit.docket_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Audit source status: `{audit.audit_source_status}`",
        f"- Packet status: `{audit.packet_status}`",
        f"- Authorization packet seal status: `{audit.authorization_packet_seal_status}`",
        f"- Coverage audit status: `{audit.coverage_audit_status}`",
        f"- Receipt status: `{audit.receipt_status}`",
        f"- Operator start packet audit status: `{audit.operator_start_packet_audit_status}`",
        f"- Start authorization: `{audit.start_authorization}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start docket coverage audit is read-only planning metadata.",
        "",
        "## Docket Coverage Checks",
        "",
    ]
    for check, status in audit.docket_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage and not audit.blocked_reasons:
        lines.append("No manual execution start docket coverage gaps.")
    else:
        _append_code_markdown_list(
            lines,
            _dedupe_preserving_order([*audit.missing_coverage, *audit.blocked_reasons]),
        )

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in audit.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in audit.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not audit.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No manual execution start docket coverage audit blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_docket_coverage_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.audit_status not in {
        "manual_execution_start_docket_coverage_audit_ready",
        "no_manual_execution_required_start_docket_coverage_audit",
    }:
        reasons.append("manual_execution_start_docket_coverage_audit_not_ready")
    if audit.docket_status not in {
        "ready_for_manual_execution_start_docket",
        "no_manual_execution_required_start_docket",
    }:
        reasons.append("manual_execution_start_docket_not_ready")
    reasons.extend(audit.blocked_reasons)
    reasons.extend(audit.missing_coverage)
    if any(status != "covered" for status in audit.docket_coverage_checks.values()):
        reasons.append("docket_coverage_checks_incomplete")
    if any(status != "covered" for status in audit.boundary_checks.values()):
        reasons.append("boundary_checks_incomplete")
    if audit.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.rollback_path:
        reasons.append("rollback_path_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_docket_coverage_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_docket_coverage_audit_seal"
    if audit.audit_status == "no_manual_execution_required_start_docket_coverage_audit":
        return "sealed_no_manual_execution_required_start_docket_coverage_audit"
    return "sealed_for_manual_execution_start_docket_coverage_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = (
        _next_session_manual_execution_start_docket_coverage_audit_seal_blocked_reasons(
            audit
        )
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_manual_execution_start_docket_coverage_audit_seal",
        seal_status=_next_session_manual_execution_start_docket_coverage_audit_seal_status(
            audit,
            blocked_reasons,
        ),
        audit_status=audit.audit_status,
        docket_status=audit.docket_status,
        source_seal_status=audit.seal_status,
        audit_source_status=audit.audit_source_status,
        packet_status=audit.packet_status,
        authorization_packet_seal_status=audit.authorization_packet_seal_status,
        coverage_audit_status=audit.coverage_audit_status,
        receipt_status=audit.receipt_status,
        operator_start_packet_audit_status=audit.operator_start_packet_audit_status,
        start_authorization=audit.start_authorization,
        seal_checks=[
            "confirm_manual_execution_start_docket_coverage_audit_ready",
            "confirm_start_docket_ready",
            "confirm_coverage_complete",
            "confirm_boundary_checks_complete",
            "confirm_start_authorization_preserved",
            "confirm_sealed_first_step_preserved",
            "confirm_sealed_candidate_order_preserved",
            "confirm_boundary_delta_zero",
        ],
        docket_coverage_checks=dict(audit.docket_coverage_checks),
        missing_coverage=list(audit.missing_coverage),
        boundary_checks=dict(audit.boundary_checks),
        sealed_first_step=audit.sealed_first_step,
        sealed_candidate_order=list(audit.sealed_candidate_order),
        operator_authorization_checklist=list(
            audit.operator_authorization_checklist
        ),
        verification_checklist=list(audit.verification_checklist),
        rollback_path=list(audit.rollback_path),
        post_completion_review=list(audit.post_completion_review),
        target_candidates=list(audit.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(audit.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_DOCKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Docket status: `{seal.docket_status}`",
        f"- Source seal status: `{seal.source_seal_status}`",
        f"- Audit source status: `{seal.audit_source_status}`",
        f"- Packet status: `{seal.packet_status}`",
        f"- Authorization packet seal status: `{seal.authorization_packet_seal_status}`",
        f"- Coverage audit status: `{seal.coverage_audit_status}`",
        f"- Receipt status: `{seal.receipt_status}`",
        f"- Operator start packet audit status: `{seal.operator_start_packet_audit_status}`",
        f"- Start authorization: `{seal.start_authorization}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start docket coverage audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Docket Coverage Checks", ""])
    for check, status in seal.docket_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage and not seal.blocked_reasons:
        lines.append("No manual execution start docket coverage audit seal blockers.")
    else:
        _append_code_markdown_list(
            lines,
            _dedupe_preserving_order([*seal.missing_coverage, *seal.blocked_reasons]),
        )

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in seal.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in seal.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No manual execution start docket coverage audit seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_final_start_packet_blocked_reasons(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSeal,
) -> list[str]:
    reasons: list[str] = []
    if seal.seal_status not in {
        "sealed_for_manual_execution_start_docket_coverage_audit",
        "sealed_no_manual_execution_required_start_docket_coverage_audit",
    }:
        reasons.append("manual_execution_start_docket_coverage_audit_seal_not_ready")
    if seal.audit_status not in {
        "manual_execution_start_docket_coverage_audit_ready",
        "no_manual_execution_required_start_docket_coverage_audit",
    }:
        reasons.append("manual_execution_start_docket_coverage_audit_not_ready")
    if seal.docket_status not in {
        "ready_for_manual_execution_start_docket",
        "no_manual_execution_required_start_docket",
    }:
        reasons.append("manual_execution_start_docket_not_ready")
    reasons.extend(seal.blocked_reasons)
    if seal.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    if not seal.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not seal.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not seal.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not seal.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not seal.rollback_path:
        reasons.append("rollback_path_missing")
    if not seal.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        seal.applied_review_decision_delta != 0
        or seal.applied_candidate_status_delta != 0
        or seal.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_final_start_packet_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSeal,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_final_start_packet"
    if seal.seal_status == "sealed_no_manual_execution_required_start_docket_coverage_audit":
        return "no_manual_execution_required_final_start_packet"
    return "ready_for_manual_execution_final_start_packet"


def _next_session_manual_execution_final_start_packet_from_seal(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSeal,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSealFinalStartPacket:
    blocked_reasons = _next_session_manual_execution_final_start_packet_blocked_reasons(
        seal
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSealFinalStartPacket(
        session_id=seal.session_id,
        packet_scope="manual_application_next_session_manual_execution_final_start_packet",
        packet_status=_next_session_manual_execution_final_start_packet_status(
            seal,
            blocked_reasons,
        ),
        seal_status=seal.seal_status,
        audit_status=seal.audit_status,
        docket_status=seal.docket_status,
        source_seal_status=seal.source_seal_status,
        audit_source_status=seal.audit_source_status,
        packet_source_status=seal.packet_status,
        authorization_packet_seal_status=seal.authorization_packet_seal_status,
        coverage_audit_status=seal.coverage_audit_status,
        receipt_status=seal.receipt_status,
        operator_start_packet_audit_status=seal.operator_start_packet_audit_status,
        start_authorization=seal.start_authorization,
        packet_checks=[
            "confirm_start_docket_coverage_audit_seal_ready",
            "confirm_start_docket_ready",
            "confirm_start_authorization",
            "confirm_sealed_first_step",
            "confirm_sealed_candidate_order",
            "confirm_operator_authorization_checklist",
            "confirm_verification_checklist",
            "confirm_rollback_path",
            "confirm_boundary_confirmation",
            "confirm_boundary_delta_zero",
        ],
        sealed_first_step=seal.sealed_first_step,
        sealed_candidate_order=list(seal.sealed_candidate_order),
        operator_authorization_checklist=list(
            seal.operator_authorization_checklist
        ),
        verification_checklist=list(seal.verification_checklist),
        rollback_path=list(seal.rollback_path),
        post_completion_review=list(seal.post_completion_review),
        target_candidates=list(seal.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(seal.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_FINAL_START_PACKET_BOUNDARY_NOTES
        ),
    )


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSealFinalStartPacket:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    return _next_session_manual_execution_final_start_packet_from_seal(seal)


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Start Packet",
        "",
        "## Summary",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Packet scope: `{packet.packet_scope}`",
        f"- Packet status: `{packet.packet_status}`",
        f"- Seal status: `{packet.seal_status}`",
        f"- Audit status: `{packet.audit_status}`",
        f"- Docket status: `{packet.docket_status}`",
        f"- Source seal status: `{packet.source_seal_status}`",
        f"- Audit source status: `{packet.audit_source_status}`",
        f"- Packet source status: `{packet.packet_source_status}`",
        f"- Authorization packet seal status: `{packet.authorization_packet_seal_status}`",
        f"- Coverage audit status: `{packet.coverage_audit_status}`",
        f"- Receipt status: `{packet.receipt_status}`",
        f"- Operator start packet audit status: `{packet.operator_start_packet_audit_status}`",
        f"- Start authorization: `{packet.start_authorization}`",
        f"- Sealed first step: `{packet.sealed_first_step}`",
        f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution final start packet is read-only planning metadata.",
        "",
        "## Packet Checks",
        "",
    ]
    for item in packet.packet_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in packet.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not packet.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(packet.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in packet.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in packet.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in packet.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in packet.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not packet.blocked_reasons:
        lines.append("No manual execution final start packet blockers.")
    else:
        _append_code_markdown_list(lines, packet.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, packet.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_final_start_packet_handoff_coverage_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSealFinalStartPacket,
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSeal,
) -> dict[str, str]:
    expected_packet_checks = [
        "confirm_start_docket_coverage_audit_seal_ready",
        "confirm_start_docket_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_operator_authorization_checklist",
        "confirm_verification_checklist",
        "confirm_rollback_path",
        "confirm_boundary_confirmation",
        "confirm_boundary_delta_zero",
    ]
    expected_boundary_confirmation = [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    return {
        "final_start_packet_ready": (
            "covered"
            if packet.packet_status
            in {
                "ready_for_manual_execution_final_start_packet",
                "no_manual_execution_required_final_start_packet",
            }
            else "missing"
        ),
        "start_docket_coverage_audit_seal_status_preserved": (
            "covered" if packet.seal_status == seal.seal_status else "missing"
        ),
        "audit_status_preserved": (
            "covered" if packet.audit_status == seal.audit_status else "missing"
        ),
        "docket_status_preserved": (
            "covered" if packet.docket_status == seal.docket_status else "missing"
        ),
        "packet_source_status_preserved": (
            "covered" if packet.packet_source_status == seal.packet_status else "missing"
        ),
        "start_authorization_preserved": (
            "covered"
            if packet.start_authorization == seal.start_authorization
            else "missing"
        ),
        "packet_checks_complete": (
            "covered"
            if all(item in packet.packet_checks for item in expected_packet_checks)
            else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered"
            if packet.sealed_first_step == seal.sealed_first_step
            else "missing"
        ),
        "sealed_candidate_order_preserved": (
            "covered"
            if packet.sealed_candidate_order == seal.sealed_candidate_order
            else "missing"
        ),
        "operator_authorization_checklist_preserved": (
            "covered"
            if packet.operator_authorization_checklist
            == seal.operator_authorization_checklist
            else "missing"
        ),
        "verification_checklist_preserved": (
            "covered"
            if packet.verification_checklist == seal.verification_checklist
            else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if packet.rollback_path == seal.rollback_path else "missing"
        ),
        "post_completion_review_preserved": (
            "covered"
            if packet.post_completion_review == seal.post_completion_review
            else "missing"
        ),
        "target_candidates_preserved": (
            "covered" if packet.target_candidates == seal.target_candidates else "missing"
        ),
        "blocked_reasons_preserved": (
            "covered" if packet.blocked_reasons == seal.blocked_reasons else "missing"
        ),
        "boundary_confirmation_complete": (
            "covered"
            if all(item in packet.boundary_confirmation for item in expected_boundary_confirmation)
            else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                packet.applied_review_decision_delta == 0
                and packet.applied_candidate_status_delta == 0
                and packet.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_manual_execution_final_start_packet_handoff_boundary_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSealFinalStartPacket,
) -> dict[str, str]:
    return {
        "final_start_packet_handoff_audit_read_only": "covered",
        "review_decision_delta_zero": (
            "covered" if packet.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if packet.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if packet.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_final_start_packet_handoff_readiness(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartDocketCoverageAuditSealFinalStartPacket,
    missing_coverage: list[str],
    boundary_checks: dict[str, str],
) -> str:
    if (
        packet.blocked_reasons
        or missing_coverage
        or any(status != "covered" for status in boundary_checks.values())
    ):
        return "blocked_before_manual_execution_final_start_packet_handoff"
    if packet.packet_status == "no_manual_execution_required_final_start_packet":
        return "no_manual_execution_required_final_start_packet_handoff"
    return "ready_for_manual_execution_final_start_packet_handoff"


def build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAudit:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    packet = _next_session_manual_execution_final_start_packet_from_seal(seal)
    coverage_checks = (
        _next_session_manual_execution_final_start_packet_handoff_coverage_checks(
            packet,
            seal,
        )
    )
    missing_coverage = [
        check for check, status in coverage_checks.items() if status != "covered"
    ]
    boundary_checks = (
        _next_session_manual_execution_final_start_packet_handoff_boundary_checks(
            packet
        )
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAudit(
        session_id=packet.session_id,
        handoff_audit_scope="manual_application_next_session_manual_execution_final_start_packet_handoff_audit",
        handoff_readiness=_next_session_manual_execution_final_start_packet_handoff_readiness(
            packet,
            missing_coverage,
            boundary_checks,
        ),
        packet_status=packet.packet_status,
        seal_status=packet.seal_status,
        audit_status=packet.audit_status,
        docket_status=packet.docket_status,
        source_seal_status=packet.source_seal_status,
        audit_source_status=packet.audit_source_status,
        packet_source_status=packet.packet_source_status,
        authorization_packet_seal_status=packet.authorization_packet_seal_status,
        coverage_audit_status=packet.coverage_audit_status,
        receipt_status=packet.receipt_status,
        operator_start_packet_audit_status=packet.operator_start_packet_audit_status,
        start_authorization=packet.start_authorization,
        coverage_checks=coverage_checks,
        missing_coverage=missing_coverage,
        boundary_checks=boundary_checks,
        operator_safe_start_boundary=[
            "confirm_final_start_packet_ready",
            "confirm_start_docket_coverage_audit_seal_preserved",
            "confirm_start_authorization",
            "confirm_sealed_first_step",
            "confirm_sealed_candidate_order",
            "confirm_boundary_confirmation_before_execution",
        ],
        sealed_first_step=packet.sealed_first_step,
        sealed_candidate_order=list(packet.sealed_candidate_order),
        operator_authorization_checklist=list(
            packet.operator_authorization_checklist
        ),
        verification_checklist=list(packet.verification_checklist),
        rollback_path=list(packet.rollback_path),
        post_completion_review=list(packet.post_completion_review),
        target_candidates=list(packet.target_candidates),
        blocked_reasons=list(packet.blocked_reasons),
        boundary_confirmation=list(packet.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_FINAL_START_PACKET_HANDOFF_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Handoff audit scope: `{audit.handoff_audit_scope}`",
        f"- Handoff readiness: `{audit.handoff_readiness}`",
        f"- Packet status: `{audit.packet_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Docket status: `{audit.docket_status}`",
        f"- Source seal status: `{audit.source_seal_status}`",
        f"- Audit source status: `{audit.audit_source_status}`",
        f"- Packet source status: `{audit.packet_source_status}`",
        f"- Authorization packet seal status: `{audit.authorization_packet_seal_status}`",
        f"- Coverage audit status: `{audit.coverage_audit_status}`",
        f"- Receipt status: `{audit.receipt_status}`",
        f"- Operator start packet audit status: `{audit.operator_start_packet_audit_status}`",
        f"- Start authorization: `{audit.start_authorization}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution final start packet handoff audit is read-only planning metadata.",
        "",
        "## Coverage Checks",
        "",
    ]
    for check, status in audit.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage:
        lines.append("No manual execution final start packet handoff coverage gaps.")
    else:
        _append_code_markdown_list(lines, audit.missing_coverage)

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in audit.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Operator-Safe Start Boundary", ""])
    for item in audit.operator_safe_start_boundary:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in audit.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not audit.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No manual execution final start packet handoff blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_final_start_packet_handoff_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.handoff_readiness not in {
        "ready_for_manual_execution_final_start_packet_handoff",
        "no_manual_execution_required_final_start_packet_handoff",
    }:
        reasons.append("handoff_readiness_not_ready")
    if audit.packet_status not in {
        "ready_for_manual_execution_final_start_packet",
        "no_manual_execution_required_final_start_packet",
    }:
        reasons.append("final_start_packet_not_ready")
    if audit.seal_status not in {
        "sealed_for_manual_execution_start_docket_coverage_audit",
        "sealed_no_manual_execution_required_start_docket_coverage_audit",
    }:
        reasons.append("start_docket_coverage_audit_seal_not_ready")
    reasons.extend(audit.missing_coverage)
    reasons.extend(audit.blocked_reasons)
    if any(status != "covered" for status in audit.coverage_checks.values()):
        reasons.append("coverage_checks_incomplete")
    if any(status != "covered" for status in audit.boundary_checks.values()):
        reasons.append("boundary_checks_incomplete")
    if not audit.operator_safe_start_boundary:
        reasons.append("operator_safe_start_boundary_missing")
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.rollback_path:
        reasons.append("rollback_path_missing")
    if not audit.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_final_start_packet_handoff_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_final_start_packet_handoff_audit_seal"
    if audit.handoff_readiness == "no_manual_execution_required_final_start_packet_handoff":
        return "sealed_no_manual_execution_required_final_start_packet_handoff"
    return "sealed_for_manual_execution_final_start_packet_handoff"


def _next_session_manual_execution_final_start_packet_handoff_audit_start_decision(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "no_go_for_operator_manual_execution"
    if audit.handoff_readiness == "no_manual_execution_required_final_start_packet_handoff":
        return "no_manual_execution_required"
    return "go_for_operator_manual_execution"


def build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_manual_execution_final_start_packet_handoff_audit_seal_blocked_reasons(
        audit
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal",
        seal_status=_next_session_manual_execution_final_start_packet_handoff_audit_seal_status(
            audit,
            blocked_reasons,
        ),
        handoff_readiness=audit.handoff_readiness,
        go_no_go_start_decision=_next_session_manual_execution_final_start_packet_handoff_audit_start_decision(
            audit,
            blocked_reasons,
        ),
        packet_status=audit.packet_status,
        seal_source_status=audit.seal_status,
        audit_status=audit.audit_status,
        docket_status=audit.docket_status,
        start_authorization=audit.start_authorization,
        seal_checks=[
            "confirm_handoff_readiness_ready",
            "confirm_final_start_packet_ready",
            "confirm_start_docket_coverage_audit_seal_preserved",
            "confirm_go_no_go_start_decision_go",
            "confirm_operator_safe_start_boundary_present",
            "confirm_sealed_first_step_present",
            "confirm_sealed_candidate_order_present",
            "confirm_operator_authorization_checklist_present",
            "confirm_verification_checklist_present",
            "confirm_rollback_path_present",
            "confirm_post_completion_review_present",
            "confirm_boundary_confirmation_present",
            "confirm_boundary_delta_zero",
        ],
        coverage_checks=dict(audit.coverage_checks),
        missing_coverage=list(audit.missing_coverage),
        boundary_checks=dict(audit.boundary_checks),
        operator_safe_start_boundary=list(audit.operator_safe_start_boundary),
        sealed_first_step=audit.sealed_first_step,
        sealed_candidate_order=list(audit.sealed_candidate_order),
        operator_authorization_checklist=list(
            audit.operator_authorization_checklist
        ),
        verification_checklist=list(audit.verification_checklist),
        rollback_path=list(audit.rollback_path),
        post_completion_review=list(audit.post_completion_review),
        target_candidates=list(audit.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(audit.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_FINAL_START_PACKET_HANDOFF_AUDIT_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Handoff readiness: `{seal.handoff_readiness}`",
        f"- Go/no-go start decision: `{seal.go_no_go_start_decision}`",
        f"- Packet status: `{seal.packet_status}`",
        f"- Seal source status: `{seal.seal_source_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Docket status: `{seal.docket_status}`",
        f"- Start authorization: `{seal.start_authorization}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution final start packet handoff audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Checks", ""])
    for check, status in seal.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage:
        lines.append("No manual execution final start packet handoff audit seal coverage gaps.")
    else:
        _append_code_markdown_list(lines, seal.missing_coverage)

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in seal.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No manual execution final start packet handoff audit seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Operator-Safe Start Boundary", ""])
    for item in seal.operator_safe_start_boundary:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in seal.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_authorization_packet_blocked_reasons(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSeal,
) -> list[str]:
    reasons: list[str] = []
    if seal.seal_status not in {
        "sealed_for_manual_execution_final_start_packet_handoff",
        "sealed_no_manual_execution_required_final_start_packet_handoff",
    }:
        reasons.append("final_start_packet_handoff_audit_seal_not_ready")
    if seal.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if seal.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(seal.blocked_reasons)
    reasons.extend(seal.missing_coverage)
    if any(status != "covered" for status in seal.boundary_checks.values()):
        reasons.append("boundary_checks_incomplete")
    if not seal.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not seal.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not seal.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not seal.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not seal.rollback_path:
        reasons.append("rollback_path_missing")
    if not seal.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        seal.applied_review_decision_delta != 0
        or seal.applied_candidate_status_delta != 0
        or seal.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_authorization_packet_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSeal,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_authorization_packet"
    if seal.seal_status == "sealed_no_manual_execution_required_final_start_packet_handoff":
        return "no_manual_execution_required_start_authorization_packet"
    return "ready_for_manual_execution_start_authorization_packet"


def build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSealStartAuthorizationPacket:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_manual_execution_start_authorization_packet_blocked_reasons(
        seal
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSealStartAuthorizationPacket(
        session_id=seal.session_id,
        packet_scope="manual_application_next_session_manual_execution_start_authorization_packet",
        packet_status=_next_session_manual_execution_start_authorization_packet_status(
            seal,
            blocked_reasons,
        ),
        seal_status=seal.seal_status,
        handoff_readiness=seal.handoff_readiness,
        go_no_go_start_decision=seal.go_no_go_start_decision,
        start_authorization=seal.start_authorization,
        audit_status=seal.audit_status,
        docket_status=seal.docket_status,
        authorization_checklist=[
            "confirm_final_start_packet_handoff_audit_seal_ready",
            "confirm_go_no_go_start_decision",
            "confirm_start_authorization",
            "confirm_sealed_first_step",
            "confirm_sealed_candidate_order",
            "confirm_operator_authorization_checklist",
            "confirm_verification_checklist",
            "confirm_rollback_path",
            "confirm_boundary_confirmation",
            "confirm_boundary_delta_zero",
        ],
        sealed_first_step=seal.sealed_first_step,
        sealed_candidate_order=list(seal.sealed_candidate_order),
        operator_authorization_checklist=list(
            seal.operator_authorization_checklist
        ),
        verification_checklist=list(seal.verification_checklist),
        rollback_path=list(seal.rollback_path),
        post_completion_review=list(seal.post_completion_review),
        target_candidates=list(seal.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(seal.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_AUTHORIZATION_PACKET_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Packet",
        "",
        "## Summary",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Packet scope: `{packet.packet_scope}`",
        f"- Packet status: `{packet.packet_status}`",
        f"- Seal status: `{packet.seal_status}`",
        f"- Handoff readiness: `{packet.handoff_readiness}`",
        f"- Go/no-go start decision: `{packet.go_no_go_start_decision}`",
        f"- Start authorization: `{packet.start_authorization}`",
        f"- Audit status: `{packet.audit_status}`",
        f"- Docket status: `{packet.docket_status}`",
        f"- Sealed first step: `{packet.sealed_first_step}`",
        f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start authorization packet is read-only planning metadata.",
        "",
        "## Authorization Checklist",
        "",
    ]
    for item in packet.authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in packet.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not packet.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(packet.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in packet.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in packet.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in packet.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in packet.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not packet.blocked_reasons:
        lines.append("No manual execution start authorization packet blockers.")
    else:
        _append_code_markdown_list(lines, packet.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, packet.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_authorization_packet_coverage_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSealStartAuthorizationPacket,
    seal: CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSeal,
) -> dict[str, str]:
    expected_authorization_checklist = {
        "confirm_final_start_packet_handoff_audit_seal_ready",
        "confirm_go_no_go_start_decision",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_operator_authorization_checklist",
        "confirm_verification_checklist",
        "confirm_rollback_path",
        "confirm_boundary_confirmation",
        "confirm_boundary_delta_zero",
    }
    return {
        "start_authorization_packet_ready": (
            "covered"
            if packet.packet_status
            in {
                "ready_for_manual_execution_start_authorization_packet",
                "no_manual_execution_required_start_authorization_packet",
            }
            else "missing"
        ),
        "final_start_packet_handoff_audit_seal_status_preserved": (
            "covered" if packet.seal_status == seal.seal_status else "missing"
        ),
        "handoff_readiness_preserved": (
            "covered"
            if packet.handoff_readiness == seal.handoff_readiness
            else "missing"
        ),
        "go_no_go_start_decision_preserved": (
            "covered"
            if packet.go_no_go_start_decision == seal.go_no_go_start_decision
            else "missing"
        ),
        "start_authorization_preserved": (
            "covered"
            if packet.start_authorization == seal.start_authorization
            else "missing"
        ),
        "source_audit_status_preserved": (
            "covered" if packet.audit_status == seal.audit_status else "missing"
        ),
        "docket_status_preserved": (
            "covered" if packet.docket_status == seal.docket_status else "missing"
        ),
        "authorization_checklist_complete": (
            "covered"
            if expected_authorization_checklist.issubset(
                set(packet.authorization_checklist)
            )
            else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered"
            if packet.sealed_first_step == seal.sealed_first_step
            else "missing"
        ),
        "sealed_candidate_order_preserved": (
            "covered"
            if packet.sealed_candidate_order == seal.sealed_candidate_order
            else "missing"
        ),
        "operator_authorization_checklist_preserved": (
            "covered"
            if packet.operator_authorization_checklist
            == seal.operator_authorization_checklist
            else "missing"
        ),
        "verification_checklist_preserved": (
            "covered"
            if packet.verification_checklist == seal.verification_checklist
            else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if packet.rollback_path == seal.rollback_path else "missing"
        ),
        "post_completion_review_preserved": (
            "covered"
            if packet.post_completion_review == seal.post_completion_review
            else "missing"
        ),
        "target_candidates_preserved": (
            "covered" if packet.target_candidates == seal.target_candidates else "missing"
        ),
        "blocked_reasons_preserved": (
            "covered"
            if all(reason in packet.blocked_reasons for reason in seal.blocked_reasons)
            else "missing"
        ),
        "boundary_confirmation_preserved": (
            "covered"
            if packet.boundary_confirmation == seal.boundary_confirmation
            else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                packet.applied_review_decision_delta == 0
                and packet.applied_candidate_status_delta == 0
                and packet.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_manual_execution_start_authorization_packet_coverage_audit_boundary_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSealStartAuthorizationPacket,
) -> dict[str, str]:
    return {
        "start_authorization_packet_coverage_audit_read_only": (
            "covered"
            if (
                packet.applied_review_decision_delta == 0
                and packet.applied_candidate_status_delta == 0
                and packet.formal_evidence_delta == 0
            )
            else "missing"
        ),
        "review_decision_delta_zero": (
            "covered" if packet.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if packet.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if packet.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_authorization_packet_coverage_audit_status(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionFinalStartPacketHandoffAuditSealStartAuthorizationPacket,
    missing_coverage: list[str],
) -> str:
    if packet.blocked_reasons or missing_coverage:
        return "blocked_before_manual_execution_start_authorization_packet_coverage_audit"
    if packet.packet_status == "no_manual_execution_required_start_authorization_packet":
        return "no_manual_execution_required_start_authorization_packet_coverage_audit"
    return "manual_execution_start_authorization_packet_coverage_audit_ready"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAudit:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    packet_coverage_checks = (
        _next_session_manual_execution_start_authorization_packet_coverage_checks(
            packet,
            seal,
        )
    )
    boundary_checks = _next_session_manual_execution_start_authorization_packet_coverage_audit_boundary_checks(
        packet
    )
    missing_coverage = [
        check
        for check, status in {
            **packet_coverage_checks,
            **boundary_checks,
        }.items()
        if status != "covered"
    ]
    return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAudit(
        session_id=packet.session_id,
        audit_scope="manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit",
        audit_status=_next_session_manual_execution_start_authorization_packet_coverage_audit_status(
            packet,
            missing_coverage,
        ),
        packet_status=packet.packet_status,
        seal_status=packet.seal_status,
        handoff_readiness=packet.handoff_readiness,
        go_no_go_start_decision=packet.go_no_go_start_decision,
        start_authorization=packet.start_authorization,
        source_audit_status=packet.audit_status,
        docket_status=packet.docket_status,
        packet_coverage_checks=packet_coverage_checks,
        missing_coverage=missing_coverage,
        boundary_checks=boundary_checks,
        authorization_checklist=list(packet.authorization_checklist),
        sealed_first_step=packet.sealed_first_step,
        sealed_candidate_order=list(packet.sealed_candidate_order),
        operator_authorization_checklist=list(
            packet.operator_authorization_checklist
        ),
        verification_checklist=list(packet.verification_checklist),
        rollback_path=list(packet.rollback_path),
        post_completion_review=list(packet.post_completion_review),
        target_candidates=list(packet.target_candidates),
        blocked_reasons=list(packet.blocked_reasons),
        boundary_confirmation=list(packet.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_AUTHORIZATION_PACKET_COVERAGE_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Packet status: `{audit.packet_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Handoff readiness: `{audit.handoff_readiness}`",
        f"- Go/no-go start decision: `{audit.go_no_go_start_decision}`",
        f"- Start authorization: `{audit.start_authorization}`",
        f"- Source audit status: `{audit.source_audit_status}`",
        f"- Docket status: `{audit.docket_status}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start authorization packet coverage audit is read-only planning metadata.",
        "",
        "## Packet Coverage Checks",
        "",
    ]
    for check, status in audit.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in audit.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage:
        lines.append("No manual execution start authorization packet coverage gaps.")
    else:
        _append_code_markdown_list(lines, audit.missing_coverage)

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No manual execution start authorization packet coverage audit blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Authorization Checklist", ""])
    for item in audit.authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in audit.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not audit.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_authorization_packet_coverage_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.audit_status not in {
        "manual_execution_start_authorization_packet_coverage_audit_ready",
        "no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("manual_execution_start_authorization_packet_coverage_audit_not_ready")
    if audit.packet_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if audit.seal_status not in {
        "sealed_for_manual_execution_final_start_packet_handoff",
        "sealed_no_manual_execution_required_final_start_packet_handoff",
    }:
        reasons.append("final_start_packet_handoff_audit_seal_not_ready")
    if audit.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if audit.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(audit.blocked_reasons)
    reasons.extend(audit.missing_coverage)
    if any(status != "covered" for status in audit.packet_coverage_checks.values()):
        reasons.append("packet_coverage_checks_incomplete")
    if any(status != "covered" for status in audit.boundary_checks.values()):
        reasons.append("boundary_checks_incomplete")
    if not audit.authorization_checklist:
        reasons.append("authorization_checklist_missing")
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.rollback_path:
        reasons.append("rollback_path_missing")
    if not audit.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_authorization_packet_coverage_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_authorization_packet_coverage_audit_seal"
    if audit.audit_status == "no_manual_execution_required_start_authorization_packet_coverage_audit":
        return "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit"
    return "sealed_for_manual_execution_start_authorization_packet_coverage_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_manual_execution_start_authorization_packet_coverage_audit_seal_blocked_reasons(
        audit
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal",
        seal_status=_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_status(
            audit,
            blocked_reasons,
        ),
        audit_status=audit.audit_status,
        packet_status=audit.packet_status,
        seal_source_status=audit.seal_status,
        handoff_readiness=audit.handoff_readiness,
        go_no_go_start_decision=audit.go_no_go_start_decision,
        start_authorization=audit.start_authorization,
        source_audit_status=audit.source_audit_status,
        docket_status=audit.docket_status,
        seal_checks=[
            "confirm_manual_execution_start_authorization_packet_coverage_audit_ready",
            "confirm_start_authorization_packet_ready",
            "confirm_final_start_packet_handoff_audit_seal_preserved",
            "confirm_go_no_go_start_decision_go",
            "confirm_start_authorization_preserved",
            "confirm_coverage_complete",
            "confirm_boundary_checks_complete",
            "confirm_authorization_checklist_preserved",
            "confirm_sealed_first_step_preserved",
            "confirm_sealed_candidate_order_preserved",
            "confirm_boundary_delta_zero",
        ],
        packet_coverage_checks=dict(audit.packet_coverage_checks),
        missing_coverage=list(audit.missing_coverage),
        boundary_checks=dict(audit.boundary_checks),
        authorization_checklist=list(audit.authorization_checklist),
        sealed_first_step=audit.sealed_first_step,
        sealed_candidate_order=list(audit.sealed_candidate_order),
        operator_authorization_checklist=list(
            audit.operator_authorization_checklist
        ),
        verification_checklist=list(audit.verification_checklist),
        rollback_path=list(audit.rollback_path),
        post_completion_review=list(audit.post_completion_review),
        target_candidates=list(audit.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(audit.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_AUTHORIZATION_PACKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Packet status: `{seal.packet_status}`",
        f"- Seal source status: `{seal.seal_source_status}`",
        f"- Handoff readiness: `{seal.handoff_readiness}`",
        f"- Go/no-go start decision: `{seal.go_no_go_start_decision}`",
        f"- Start authorization: `{seal.start_authorization}`",
        f"- Source audit status: `{seal.source_audit_status}`",
        f"- Docket status: `{seal.docket_status}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start authorization packet coverage audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in seal.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in seal.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage:
        lines.append("No manual execution start authorization packet coverage audit seal gaps.")
    else:
        _append_code_markdown_list(lines, seal.missing_coverage)

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No manual execution start authorization packet coverage audit seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Authorization Checklist", ""])
    for item in seal.authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in seal.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_clearance_packet_blocked_reasons(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSeal,
) -> list[str]:
    reasons: list[str] = []
    no_manual_execution_required = seal.seal_status == (
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit"
    ) or seal.audit_status == (
        "no_manual_execution_required_start_authorization_packet_coverage_audit"
    )
    if seal.seal_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if seal.audit_status not in {
        "manual_execution_start_authorization_packet_coverage_audit_ready",
        "no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("manual_execution_start_authorization_packet_coverage_audit_not_ready")
    if seal.packet_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if seal.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if seal.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(seal.blocked_reasons)
    reasons.extend(seal.missing_coverage)
    if any(status != "covered" for status in seal.packet_coverage_checks.values()):
        reasons.append("packet_coverage_checks_incomplete")
    if any(status != "covered" for status in seal.boundary_checks.values()):
        reasons.append("boundary_checks_incomplete")
    if not seal.seal_checks:
        reasons.append("seal_checks_missing")
    if not seal.authorization_checklist:
        reasons.append("authorization_checklist_missing")
    if not seal.sealed_first_step and not no_manual_execution_required:
        reasons.append("sealed_first_step_missing")
    if not seal.sealed_candidate_order and not no_manual_execution_required:
        reasons.append("sealed_candidate_order_missing")
    if not seal.operator_authorization_checklist and not no_manual_execution_required:
        reasons.append("operator_authorization_checklist_missing")
    if not seal.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not seal.rollback_path:
        reasons.append("rollback_path_missing")
    if not seal.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not seal.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        seal.applied_review_decision_delta != 0
        or seal.applied_candidate_status_delta != 0
        or seal.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_clearance_packet_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSeal,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_clearance_packet"
    if seal.seal_status == (
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit"
    ):
        return "no_manual_execution_required_start_clearance_packet"
    return "ready_for_manual_execution_start_clearance_packet"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacket:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_manual_execution_start_clearance_packet_blocked_reasons(
        seal
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacket(
        session_id=seal.session_id,
        packet_scope="manual_application_next_session_manual_execution_start_clearance_packet",
        packet_status=_next_session_manual_execution_start_clearance_packet_status(
            seal,
            blocked_reasons,
        ),
        seal_status=seal.seal_status,
        audit_status=seal.audit_status,
        packet_source_status=seal.packet_status,
        handoff_readiness=seal.handoff_readiness,
        go_no_go_start_decision=seal.go_no_go_start_decision,
        start_authorization=seal.start_authorization,
        source_audit_status=seal.source_audit_status,
        docket_status=seal.docket_status,
        clearance_checklist=[
            "confirm_start_authorization_packet_coverage_audit_seal_ready",
            "confirm_start_clearance_packet_ready",
            "confirm_go_no_go_start_decision",
            "confirm_start_authorization",
            "confirm_sealed_first_step",
            "confirm_sealed_candidate_order",
            "confirm_operator_authorization_checklist",
            "confirm_verification_checklist",
            "confirm_rollback_path",
            "confirm_boundary_confirmation",
            "confirm_boundary_delta_zero",
        ],
        sealed_first_step=seal.sealed_first_step,
        sealed_candidate_order=list(seal.sealed_candidate_order),
        operator_authorization_checklist=list(
            seal.operator_authorization_checklist
        ),
        verification_checklist=list(seal.verification_checklist),
        rollback_path=list(seal.rollback_path),
        post_completion_review=list(seal.post_completion_review),
        target_candidates=list(seal.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(seal.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet",
        "",
        "## Summary",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Packet scope: `{packet.packet_scope}`",
        f"- Packet status: `{packet.packet_status}`",
        f"- Seal status: `{packet.seal_status}`",
        f"- Audit status: `{packet.audit_status}`",
        f"- Packet source status: `{packet.packet_source_status}`",
        f"- Handoff readiness: `{packet.handoff_readiness}`",
        f"- Go/no-go start decision: `{packet.go_no_go_start_decision}`",
        f"- Start authorization: `{packet.start_authorization}`",
        f"- Source audit status: `{packet.source_audit_status}`",
        f"- Docket status: `{packet.docket_status}`",
        f"- Sealed first step: `{packet.sealed_first_step}`",
        f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start clearance packet is read-only planning metadata.",
        "",
        "## Clearance Checklist",
        "",
    ]
    for item in packet.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in packet.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not packet.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(packet.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in packet.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in packet.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in packet.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in packet.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not packet.blocked_reasons:
        lines.append("No manual execution start clearance packet blockers.")
    else:
        _append_code_markdown_list(lines, packet.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, packet.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_clearance_packet_coverage_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacket,
) -> dict[str, str]:
    return {
        "start_clearance_packet_ready": (
            "covered"
            if packet.packet_status
            in {
                "ready_for_manual_execution_start_clearance_packet",
                "no_manual_execution_required_start_clearance_packet",
            }
            else "missing"
        ),
        "coverage_audit_seal_status_preserved": (
            "covered" if packet.seal_status else "missing"
        ),
        "coverage_audit_status_preserved": (
            "covered" if packet.audit_status else "missing"
        ),
        "packet_source_status_preserved": (
            "covered" if packet.packet_source_status else "missing"
        ),
        "handoff_readiness_preserved": (
            "covered" if packet.handoff_readiness else "missing"
        ),
        "go_no_go_start_decision_preserved": (
            "covered" if packet.go_no_go_start_decision else "missing"
        ),
        "start_authorization_preserved": (
            "covered" if packet.start_authorization else "missing"
        ),
        "source_audit_status_preserved": (
            "covered" if packet.source_audit_status else "missing"
        ),
        "docket_status_preserved": (
            "covered" if packet.docket_status else "missing"
        ),
        "clearance_checklist_complete": (
            "covered" if packet.clearance_checklist else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered" if packet.sealed_first_step else "missing"
        ),
        "sealed_candidate_order_preserved": (
            "covered" if packet.sealed_candidate_order else "missing"
        ),
        "operator_authorization_checklist_preserved": (
            "covered" if packet.operator_authorization_checklist else "missing"
        ),
        "verification_checklist_preserved": (
            "covered" if packet.verification_checklist else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if packet.rollback_path else "missing"
        ),
        "post_completion_review_preserved": (
            "covered" if packet.post_completion_review else "missing"
        ),
        "target_candidates_preserved": (
            "covered" if packet.target_candidates else "missing"
        ),
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": (
            "covered" if packet.boundary_confirmation else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                packet.applied_review_decision_delta == 0
                and packet.applied_candidate_status_delta == 0
                and packet.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_manual_execution_start_clearance_packet_coverage_audit_boundary_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacket,
) -> dict[str, str]:
    return {
        "start_clearance_packet_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": (
            "covered" if packet.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if packet.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if packet.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_clearance_packet_missing_coverage(
    packet_coverage_checks: dict[str, str],
    boundary_checks: dict[str, str],
) -> list[str]:
    missing = [
        check
        for check, status in packet_coverage_checks.items()
        if status != "covered"
    ]
    missing.extend(
        check for check, status in boundary_checks.items() if status != "covered"
    )
    return _dedupe_preserving_order(missing)


def _next_session_manual_execution_start_clearance_packet_coverage_audit_blocked_reasons(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacket,
    missing_coverage: list[str],
) -> list[str]:
    reasons: list[str] = []
    if packet.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if packet.seal_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if packet.audit_status not in {
        "manual_execution_start_authorization_packet_coverage_audit_ready",
        "no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_not_ready")
    if packet.packet_source_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if packet.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if packet.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(packet.blocked_reasons)
    reasons.extend(missing_coverage)
    if not packet.clearance_checklist:
        reasons.append("clearance_checklist_missing")
    if not packet.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not packet.rollback_path:
        reasons.append("rollback_path_missing")
    if not packet.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not packet.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        packet.applied_review_decision_delta != 0
        or packet.applied_candidate_status_delta != 0
        or packet.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_clearance_packet_coverage_audit_status(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacket,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_clearance_packet_coverage_audit"
    if packet.packet_status == "no_manual_execution_required_start_clearance_packet":
        return "no_manual_execution_required_start_clearance_packet_coverage_audit"
    return "manual_execution_start_clearance_packet_coverage_audit_ready"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAudit:
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    packet_coverage_checks = (
        _next_session_manual_execution_start_clearance_packet_coverage_checks(
            packet
        )
    )
    boundary_checks = _next_session_manual_execution_start_clearance_packet_coverage_audit_boundary_checks(
        packet
    )
    missing_coverage = (
        _next_session_manual_execution_start_clearance_packet_missing_coverage(
            packet_coverage_checks,
            boundary_checks,
        )
    )
    blocked_reasons = _next_session_manual_execution_start_clearance_packet_coverage_audit_blocked_reasons(
        packet,
        missing_coverage,
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAudit(
        session_id=packet.session_id,
        audit_scope="manual_application_next_session_manual_execution_start_clearance_packet_coverage_audit",
        audit_status=_next_session_manual_execution_start_clearance_packet_coverage_audit_status(
            packet,
            blocked_reasons,
        ),
        packet_status=packet.packet_status,
        seal_status=packet.seal_status,
        packet_source_status=packet.packet_source_status,
        handoff_readiness=packet.handoff_readiness,
        go_no_go_start_decision=packet.go_no_go_start_decision,
        start_authorization=packet.start_authorization,
        source_audit_status=packet.source_audit_status,
        docket_status=packet.docket_status,
        packet_coverage_checks=packet_coverage_checks,
        missing_coverage=missing_coverage,
        boundary_checks=boundary_checks,
        clearance_checklist=list(packet.clearance_checklist),
        sealed_first_step=packet.sealed_first_step,
        sealed_candidate_order=list(packet.sealed_candidate_order),
        operator_authorization_checklist=list(
            packet.operator_authorization_checklist
        ),
        verification_checklist=list(packet.verification_checklist),
        rollback_path=list(packet.rollback_path),
        post_completion_review=list(packet.post_completion_review),
        target_candidates=list(packet.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(packet.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_COVERAGE_AUDIT_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Packet status: `{audit.packet_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Packet source status: `{audit.packet_source_status}`",
        f"- Handoff readiness: `{audit.handoff_readiness}`",
        f"- Go/no-go start decision: `{audit.go_no_go_start_decision}`",
        f"- Start authorization: `{audit.start_authorization}`",
        f"- Source audit status: `{audit.source_audit_status}`",
        f"- Docket status: `{audit.docket_status}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start clearance packet coverage audit is read-only planning metadata.",
        "",
        "## Packet Coverage Checks",
        "",
    ]
    for check, status in audit.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in audit.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage:
        lines.append("No manual execution start clearance packet coverage gaps.")
    else:
        _append_code_markdown_list(lines, audit.missing_coverage)

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No manual execution start clearance packet coverage audit blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Clearance Checklist", ""])
    for item in audit.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in audit.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not audit.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_clearance_packet_coverage_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAudit,
) -> list[str]:
    reasons: list[str] = []
    if audit.audit_status not in {
        "manual_execution_start_clearance_packet_coverage_audit_ready",
        "no_manual_execution_required_start_clearance_packet_coverage_audit",
    }:
        reasons.append("manual_execution_start_clearance_packet_coverage_audit_not_ready")
    if audit.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if audit.seal_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if audit.packet_source_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if audit.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if audit.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(audit.blocked_reasons)
    reasons.extend(audit.missing_coverage)
    if any(status != "covered" for status in audit.packet_coverage_checks.values()):
        reasons.append("packet_coverage_checks_incomplete")
    if any(status != "covered" for status in audit.boundary_checks.values()):
        reasons.append("boundary_checks_incomplete")
    if not audit.clearance_checklist:
        reasons.append("clearance_checklist_missing")
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.rollback_path:
        reasons.append("rollback_path_missing")
    if not audit.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_clearance_packet_coverage_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_clearance_packet_coverage_audit_seal"
    if audit.audit_status == "no_manual_execution_required_start_clearance_packet_coverage_audit":
        return "sealed_no_manual_execution_required_start_clearance_packet_coverage_audit"
    return "sealed_for_manual_execution_start_clearance_packet_coverage_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSeal:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    blocked_reasons = _next_session_manual_execution_start_clearance_packet_coverage_audit_seal_blocked_reasons(
        audit
    )
    return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSeal(
        session_id=audit.session_id,
        seal_scope="manual_application_next_session_manual_execution_start_clearance_packet_coverage_audit_seal",
        seal_status=_next_session_manual_execution_start_clearance_packet_coverage_audit_seal_status(
            audit,
            blocked_reasons,
        ),
        audit_status=audit.audit_status,
        packet_status=audit.packet_status,
        seal_source_status=audit.seal_status,
        packet_source_status=audit.packet_source_status,
        handoff_readiness=audit.handoff_readiness,
        go_no_go_start_decision=audit.go_no_go_start_decision,
        start_authorization=audit.start_authorization,
        source_audit_status=audit.source_audit_status,
        docket_status=audit.docket_status,
        seal_checks=[
            "confirm_manual_execution_start_clearance_packet_coverage_audit_ready",
            "confirm_start_clearance_packet_ready",
            "confirm_start_authorization_packet_coverage_audit_seal_preserved",
            "confirm_packet_source_status_preserved",
            "confirm_go_no_go_start_decision_go",
            "confirm_start_authorization_preserved",
            "confirm_coverage_complete",
            "confirm_boundary_checks_complete",
            "confirm_clearance_checklist_preserved",
            "confirm_sealed_first_step_preserved",
            "confirm_sealed_candidate_order_preserved",
            "confirm_boundary_delta_zero",
        ],
        packet_coverage_checks=dict(audit.packet_coverage_checks),
        missing_coverage=list(audit.missing_coverage),
        boundary_checks=dict(audit.boundary_checks),
        clearance_checklist=list(audit.clearance_checklist),
        sealed_first_step=audit.sealed_first_step,
        sealed_candidate_order=list(audit.sealed_candidate_order),
        operator_authorization_checklist=list(
            audit.operator_authorization_checklist
        ),
        verification_checklist=list(audit.verification_checklist),
        rollback_path=list(audit.rollback_path),
        post_completion_review=list(audit.post_completion_review),
        target_candidates=list(audit.target_candidates),
        blocked_reasons=blocked_reasons,
        boundary_confirmation=list(audit.boundary_confirmation),
        applied_review_decision_delta=0,
        applied_candidate_status_delta=0,
        formal_evidence_delta=0,
        boundary_notes=list(
            REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES
        ),
    )


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Packet status: `{seal.packet_status}`",
        f"- Seal source status: `{seal.seal_source_status}`",
        f"- Packet source status: `{seal.packet_source_status}`",
        f"- Handoff readiness: `{seal.handoff_readiness}`",
        f"- Go/no-go start decision: `{seal.go_no_go_start_decision}`",
        f"- Start authorization: `{seal.start_authorization}`",
        f"- Source audit status: `{seal.source_audit_status}`",
        f"- Docket status: `{seal.docket_status}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start clearance packet coverage audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in seal.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in seal.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage:
        lines.append("No manual execution start clearance packet coverage audit seal gaps.")
    else:
        _append_code_markdown_list(lines, seal.missing_coverage)

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No manual execution start clearance packet coverage audit seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Clearance Checklist", ""])
    for item in seal.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in seal.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_blocked_reasons(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSeal,
) -> list[str]:
    reasons: list[str] = []
    if seal.seal_status not in {
        "sealed_for_manual_execution_start_clearance_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_clearance_packet_coverage_audit",
    }:
        reasons.append("start_clearance_packet_coverage_audit_seal_not_ready")
    if seal.audit_status not in {
        "manual_execution_start_clearance_packet_coverage_audit_ready",
        "no_manual_execution_required_start_clearance_packet_coverage_audit",
    }:
        reasons.append("manual_execution_start_clearance_packet_coverage_audit_not_ready")
    if seal.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if seal.seal_source_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if seal.packet_source_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if seal.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if seal.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(seal.blocked_reasons)
    reasons.extend(seal.missing_coverage)
    if any(status != "covered" for status in seal.packet_coverage_checks.values()):
        reasons.append("packet_coverage_checks_incomplete")
    if any(status != "covered" for status in seal.boundary_checks.values()):
        reasons.append("boundary_checks_incomplete")
    if not seal.seal_checks:
        reasons.append("seal_checks_missing")
    if not seal.clearance_checklist:
        reasons.append("clearance_checklist_missing")
    if not seal.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not seal.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not seal.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not seal.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not seal.rollback_path:
        reasons.append("rollback_path_missing")
    if not seal.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not seal.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        seal.applied_review_decision_delta != 0
        or seal.applied_candidate_status_delta != 0
        or seal.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSeal,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_clearance_packet_final_start_authorization"
    if (
        seal.seal_status
        == "sealed_no_manual_execution_required_start_clearance_packet_coverage_audit"
    ):
        return "no_manual_execution_required_start_clearance_packet_final_start_authorization"
    return "authorized_for_manual_execution_start_from_clearance_packet"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorization:
    cache_token = _start_source_intake_call_cache()
    try:
        seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal(
            drafts,
            data_dir,
            preview_data_dir=preview_data_dir,
        )
        blocked_reasons = _next_session_manual_execution_start_clearance_packet_final_start_authorization_blocked_reasons(
            seal
        )
        return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorization(
            session_id=seal.session_id,
            authorization_scope="manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization",
            authorization_status=_next_session_manual_execution_start_clearance_packet_final_start_authorization_status(
                seal,
                blocked_reasons,
            ),
            seal_status=seal.seal_status,
            audit_status=seal.audit_status,
            packet_status=seal.packet_status,
            seal_source_status=seal.seal_source_status,
            packet_source_status=seal.packet_source_status,
            handoff_readiness=seal.handoff_readiness,
            go_no_go_start_decision=seal.go_no_go_start_decision,
            start_authorization=seal.start_authorization,
            source_audit_status=seal.source_audit_status,
            docket_status=seal.docket_status,
            authorization_checks=[
                "confirm_start_clearance_packet_coverage_audit_seal_ready",
                "confirm_final_start_authorization_ready",
                "confirm_go_no_go_start_decision_go",
                "confirm_start_authorization_preserved",
                "confirm_sealed_first_step_preserved",
                "confirm_sealed_candidate_order_preserved",
                "confirm_operator_authorization_checklist_preserved",
                "confirm_verification_checklist_preserved",
                "confirm_rollback_path_preserved",
                "confirm_boundary_delta_zero",
            ],
            seal_checks=list(seal.seal_checks),
            packet_coverage_checks=dict(seal.packet_coverage_checks),
            missing_coverage=list(seal.missing_coverage),
            boundary_checks={
                "start_clearance_packet_final_start_authorization_read_only": "covered",
                "review_decision_delta_zero": "covered",
                "candidate_status_delta_zero": "covered",
                "formal_evidence_delta_zero": "covered",
            },
            clearance_checklist=list(seal.clearance_checklist),
            sealed_first_step=seal.sealed_first_step,
            sealed_candidate_order=list(seal.sealed_candidate_order),
            operator_authorization_checklist=list(
                seal.operator_authorization_checklist
            ),
            verification_checklist=list(seal.verification_checklist),
            rollback_path=list(seal.rollback_path),
            post_completion_review=list(seal.post_completion_review),
            target_candidates=list(seal.target_candidates),
            blocked_reasons=blocked_reasons,
            boundary_confirmation=list(seal.boundary_confirmation),
            applied_review_decision_delta=0,
            applied_candidate_status_delta=0,
            formal_evidence_delta=0,
            boundary_notes=list(
                REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_FINAL_START_AUTHORIZATION_BOUNDARY_NOTES
            ),
        )
    finally:
        _end_source_intake_call_cache(cache_token)


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    authorization = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization",
        "",
        "## Summary",
        "",
        f"- Session id: `{authorization.session_id}`",
        f"- Authorization scope: `{authorization.authorization_scope}`",
        f"- Authorization status: `{authorization.authorization_status}`",
        f"- Seal status: `{authorization.seal_status}`",
        f"- Audit status: `{authorization.audit_status}`",
        f"- Packet status: `{authorization.packet_status}`",
        f"- Seal source status: `{authorization.seal_source_status}`",
        f"- Packet source status: `{authorization.packet_source_status}`",
        f"- Handoff readiness: `{authorization.handoff_readiness}`",
        f"- Go/no-go start decision: `{authorization.go_no_go_start_decision}`",
        f"- Start authorization: `{authorization.start_authorization}`",
        f"- Source audit status: `{authorization.source_audit_status}`",
        f"- Docket status: `{authorization.docket_status}`",
        f"- Sealed first step: `{authorization.sealed_first_step}`",
        f"- Applied review decision delta: `{authorization.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{authorization.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{authorization.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start clearance packet final start authorization is read-only planning metadata.",
        "",
        "## Authorization Checks",
        "",
    ]
    for item in authorization.authorization_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Seal Checks", ""])
    for item in authorization.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in authorization.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in authorization.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not authorization.missing_coverage:
        lines.append(
            "No manual execution start clearance packet final start authorization gaps."
        )
    else:
        _append_code_markdown_list(lines, authorization.missing_coverage)

    lines.extend(["", "## Blocked Reasons", ""])
    if not authorization.blocked_reasons:
        lines.append(
            "No manual execution start clearance packet final start authorization blockers."
        )
    else:
        _append_code_markdown_list(lines, authorization.blocked_reasons)

    lines.extend(["", "## Clearance Checklist", ""])
    for item in authorization.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in authorization.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not authorization.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(authorization.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in authorization.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in authorization.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in authorization.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in authorization.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, authorization.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(authorization.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_checks(
    authorization: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorization,
) -> dict[str, str]:
    return {
        "final_start_authorization_ready": (
            "covered"
            if authorization.authorization_status
            in {
                "authorized_for_manual_execution_start_from_clearance_packet",
                "no_manual_execution_required_start_clearance_packet_final_start_authorization",
            }
            else "missing"
        ),
        "coverage_audit_seal_status_preserved": (
            "covered" if authorization.seal_status else "missing"
        ),
        "coverage_audit_status_preserved": (
            "covered" if authorization.audit_status else "missing"
        ),
        "packet_status_preserved": (
            "covered" if authorization.packet_status else "missing"
        ),
        "seal_source_status_preserved": (
            "covered" if authorization.seal_source_status else "missing"
        ),
        "packet_source_status_preserved": (
            "covered" if authorization.packet_source_status else "missing"
        ),
        "handoff_readiness_preserved": (
            "covered" if authorization.handoff_readiness else "missing"
        ),
        "go_no_go_start_decision_preserved": (
            "covered" if authorization.go_no_go_start_decision else "missing"
        ),
        "start_authorization_preserved": (
            "covered" if authorization.start_authorization else "missing"
        ),
        "source_audit_status_preserved": (
            "covered" if authorization.source_audit_status else "missing"
        ),
        "docket_status_preserved": (
            "covered" if authorization.docket_status else "missing"
        ),
        "authorization_checks_complete": (
            "covered" if authorization.authorization_checks else "missing"
        ),
        "seal_checks_complete": (
            "covered" if authorization.seal_checks else "missing"
        ),
        "packet_coverage_checks_complete": (
            "covered"
            if authorization.packet_coverage_checks
            and all(
                status == "covered"
                for status in authorization.packet_coverage_checks.values()
            )
            else "missing"
        ),
        "boundary_checks_complete": (
            "covered"
            if authorization.boundary_checks
            and all(status == "covered" for status in authorization.boundary_checks.values())
            else "missing"
        ),
        "clearance_checklist_complete": (
            "covered" if authorization.clearance_checklist else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered" if authorization.sealed_first_step else "missing"
        ),
        "sealed_candidate_order_preserved": (
            "covered" if authorization.sealed_candidate_order else "missing"
        ),
        "operator_authorization_checklist_preserved": (
            "covered"
            if authorization.operator_authorization_checklist
            else "missing"
        ),
        "verification_checklist_preserved": (
            "covered" if authorization.verification_checklist else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if authorization.rollback_path else "missing"
        ),
        "post_completion_review_preserved": (
            "covered" if authorization.post_completion_review else "missing"
        ),
        "target_candidates_preserved": (
            "covered" if authorization.target_candidates else "missing"
        ),
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": (
            "covered" if authorization.boundary_confirmation else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                authorization.applied_review_decision_delta == 0
                and authorization.applied_candidate_status_delta == 0
                and authorization.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_boundary_checks(
    authorization: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorization,
) -> dict[str, str]:
    return {
        "start_clearance_packet_final_start_authorization_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": (
            "covered"
            if authorization.applied_review_decision_delta == 0
            else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered"
            if authorization.applied_candidate_status_delta == 0
            else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if authorization.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_missing_coverage(
    authorization_coverage_checks: dict[str, str],
    boundary_checks: dict[str, str],
) -> list[str]:
    missing = [
        check
        for check, status in authorization_coverage_checks.items()
        if status != "covered"
    ]
    missing.extend(
        check for check, status in boundary_checks.items() if status != "covered"
    )
    return _dedupe_preserving_order(missing)


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_blocked_reasons(
    authorization: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorization,
    missing_coverage: list[str],
) -> list[str]:
    reasons: list[str] = []
    if authorization.authorization_status not in {
        "authorized_for_manual_execution_start_from_clearance_packet",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization",
    }:
        reasons.append("final_start_authorization_not_ready")
    if authorization.seal_status not in {
        "sealed_for_manual_execution_start_clearance_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_clearance_packet_coverage_audit",
    }:
        reasons.append("start_clearance_packet_coverage_audit_seal_not_ready")
    if authorization.audit_status not in {
        "manual_execution_start_clearance_packet_coverage_audit_ready",
        "no_manual_execution_required_start_clearance_packet_coverage_audit",
    }:
        reasons.append("start_clearance_packet_coverage_audit_not_ready")
    if authorization.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if authorization.seal_source_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if authorization.packet_source_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if authorization.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if authorization.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(authorization.blocked_reasons)
    reasons.extend(missing_coverage)
    if not authorization.authorization_checks:
        reasons.append("authorization_checks_missing")
    if not authorization.seal_checks:
        reasons.append("seal_checks_missing")
    if not authorization.clearance_checklist:
        reasons.append("clearance_checklist_missing")
    if not authorization.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not authorization.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not authorization.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not authorization.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not authorization.rollback_path:
        reasons.append("rollback_path_missing")
    if not authorization.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not authorization.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        authorization.applied_review_decision_delta != 0
        or authorization.applied_candidate_status_delta != 0
        or authorization.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_status(
    authorization: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorization,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"
    if (
        authorization.authorization_status
        == "no_manual_execution_required_start_clearance_packet_final_start_authorization"
    ):
        return "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit"
    return "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAudit:
    cache_token = _start_source_intake_call_cache()
    try:
        authorization = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization(
            drafts,
            data_dir,
            preview_data_dir=preview_data_dir,
        )
        authorization_coverage_checks = _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_checks(
            authorization
        )
        boundary_checks = _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_boundary_checks(
            authorization
        )
        missing_coverage = _next_session_manual_execution_start_clearance_packet_final_start_authorization_missing_coverage(
            authorization_coverage_checks,
            boundary_checks,
        )
        blocked_reasons = _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_blocked_reasons(
            authorization,
            missing_coverage,
        )
        return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAudit(
            session_id=authorization.session_id,
            audit_scope="manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit",
            audit_status=_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_status(
                authorization,
                blocked_reasons,
            ),
            authorization_status=authorization.authorization_status,
            seal_status=authorization.seal_status,
            packet_status=authorization.packet_status,
            seal_source_status=authorization.seal_source_status,
            packet_source_status=authorization.packet_source_status,
            handoff_readiness=authorization.handoff_readiness,
            go_no_go_start_decision=authorization.go_no_go_start_decision,
            start_authorization=authorization.start_authorization,
            source_audit_status=authorization.source_audit_status,
            docket_status=authorization.docket_status,
            authorization_coverage_checks=dict(authorization_coverage_checks),
            authorization_checks=list(authorization.authorization_checks),
            seal_checks=list(authorization.seal_checks),
            packet_coverage_checks=dict(authorization.packet_coverage_checks),
            missing_coverage=list(missing_coverage),
            boundary_checks=dict(boundary_checks),
            clearance_checklist=list(authorization.clearance_checklist),
            sealed_first_step=authorization.sealed_first_step,
            sealed_candidate_order=list(authorization.sealed_candidate_order),
            operator_authorization_checklist=list(
                authorization.operator_authorization_checklist
            ),
            verification_checklist=list(authorization.verification_checklist),
            rollback_path=list(authorization.rollback_path),
            post_completion_review=list(authorization.post_completion_review),
            target_candidates=list(authorization.target_candidates),
            blocked_reasons=blocked_reasons,
            boundary_confirmation=list(authorization.boundary_confirmation),
            applied_review_decision_delta=0,
            applied_candidate_status_delta=0,
            formal_evidence_delta=0,
            boundary_notes=list(
                REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_FINAL_START_AUTHORIZATION_COVERAGE_AUDIT_BOUNDARY_NOTES
            ),
        )
    finally:
        _end_source_intake_call_cache(cache_token)


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Authorization status: `{audit.authorization_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Packet status: `{audit.packet_status}`",
        f"- Seal source status: `{audit.seal_source_status}`",
        f"- Packet source status: `{audit.packet_source_status}`",
        f"- Handoff readiness: `{audit.handoff_readiness}`",
        f"- Go/no-go start decision: `{audit.go_no_go_start_decision}`",
        f"- Start authorization: `{audit.start_authorization}`",
        f"- Source audit status: `{audit.source_audit_status}`",
        f"- Docket status: `{audit.docket_status}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start clearance packet final start authorization coverage audit is read-only planning metadata.",
        "",
        "## Authorization Coverage Checks",
        "",
    ]
    for check, status in audit.authorization_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Authorization Checks", ""])
    for item in audit.authorization_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Seal Checks", ""])
    for item in audit.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in audit.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in audit.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage:
        lines.append(
            "No manual execution start clearance packet final start authorization coverage gaps."
        )
    else:
        _append_code_markdown_list(lines, audit.missing_coverage)

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append(
            "No manual execution start clearance packet final start authorization coverage audit blockers."
        )
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Clearance Checklist", ""])
    for item in audit.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in audit.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not audit.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_checks() -> list[str]:
    return [
        "confirm_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready",
        "confirm_final_start_authorization_ready",
        "confirm_start_clearance_packet_coverage_audit_seal_preserved",
        "confirm_authorization_status_preserved",
        "confirm_go_no_go_start_decision_go",
        "confirm_start_authorization_preserved",
        "confirm_authorization_coverage_complete",
        "confirm_boundary_checks_complete",
        "confirm_clearance_checklist_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_sealed_candidate_order_preserved",
        "confirm_boundary_delta_zero",
    ]


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_boundary_checks(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAudit,
) -> dict[str, str]:
    return {
        "start_clearance_packet_final_start_authorization_coverage_audit_seal_read_only": "covered",
        "review_decision_delta_zero": (
            "covered" if audit.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if audit.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if audit.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAudit,
    boundary_checks: dict[str, str],
) -> list[str]:
    reasons: list[str] = []
    if audit.audit_status not in {
        "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_not_ready")
    if audit.authorization_status not in {
        "authorized_for_manual_execution_start_from_clearance_packet",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization",
    }:
        reasons.append("final_start_authorization_not_ready")
    if audit.seal_status not in {
        "sealed_for_manual_execution_start_clearance_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_clearance_packet_coverage_audit",
    }:
        reasons.append("start_clearance_packet_coverage_audit_seal_not_ready")
    if audit.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if audit.seal_source_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if audit.packet_source_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if audit.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if audit.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(audit.blocked_reasons)
    reasons.extend(audit.missing_coverage)
    reasons.extend(
        check
        for check, status in audit.authorization_coverage_checks.items()
        if status != "covered"
    )
    reasons.extend(
        check for check, status in audit.packet_coverage_checks.items() if status != "covered"
    )
    reasons.extend(
        check for check, status in audit.boundary_checks.items() if status != "covered"
    )
    reasons.extend(
        check for check, status in boundary_checks.items() if status != "covered"
    )
    if not audit.authorization_checks:
        reasons.append("authorization_checks_missing")
    if not audit.seal_checks:
        reasons.append("coverage_seal_checks_missing")
    if not audit.clearance_checklist:
        reasons.append("clearance_checklist_missing")
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.rollback_path:
        reasons.append("rollback_path_missing")
    if not audit.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal"
    if (
        audit.audit_status
        == "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit"
    ):
        return "sealed_no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit"
    return "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSeal:
    cache_token = _start_source_intake_call_cache()
    try:
        audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit(
            drafts,
            data_dir,
            preview_data_dir=preview_data_dir,
        )
        boundary_checks = _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_boundary_checks(
            audit
        )
        blocked_reasons = _next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_blocked_reasons(
            audit,
            boundary_checks,
        )
        return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSeal(
            session_id=audit.session_id,
            seal_scope="manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal",
            seal_status=_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_status(
                audit,
                blocked_reasons,
            ),
            audit_status=audit.audit_status,
            authorization_status=audit.authorization_status,
            seal_source_status=audit.seal_source_status,
            packet_status=audit.packet_status,
            packet_source_status=audit.packet_source_status,
            handoff_readiness=audit.handoff_readiness,
            go_no_go_start_decision=audit.go_no_go_start_decision,
            start_authorization=audit.start_authorization,
            source_audit_status=audit.source_audit_status,
            docket_status=audit.docket_status,
            seal_checks=_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_checks(),
            authorization_coverage_checks=dict(audit.authorization_coverage_checks),
            authorization_checks=list(audit.authorization_checks),
            coverage_seal_checks=list(audit.seal_checks),
            packet_coverage_checks=dict(audit.packet_coverage_checks),
            missing_coverage=list(audit.missing_coverage),
            boundary_checks=dict(boundary_checks),
            clearance_checklist=list(audit.clearance_checklist),
            sealed_first_step=audit.sealed_first_step,
            sealed_candidate_order=list(audit.sealed_candidate_order),
            operator_authorization_checklist=list(audit.operator_authorization_checklist),
            verification_checklist=list(audit.verification_checklist),
            rollback_path=list(audit.rollback_path),
            post_completion_review=list(audit.post_completion_review),
            target_candidates=list(audit.target_candidates),
            blocked_reasons=blocked_reasons,
            boundary_confirmation=list(audit.boundary_confirmation),
            applied_review_decision_delta=0,
            applied_candidate_status_delta=0,
            formal_evidence_delta=0,
            boundary_notes=list(
                REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_CLEARANCE_PACKET_FINAL_START_AUTHORIZATION_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES
            ),
        )
    finally:
        _end_source_intake_call_cache(cache_token)


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Authorization status: `{seal.authorization_status}`",
        f"- Packet status: `{seal.packet_status}`",
        f"- Seal source status: `{seal.seal_source_status}`",
        f"- Packet source status: `{seal.packet_source_status}`",
        f"- Handoff readiness: `{seal.handoff_readiness}`",
        f"- Go/no-go start decision: `{seal.go_no_go_start_decision}`",
        f"- Start authorization: `{seal.start_authorization}`",
        f"- Source audit status: `{seal.source_audit_status}`",
        f"- Docket status: `{seal.docket_status}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start clearance packet final start authorization coverage audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Authorization Coverage Checks", ""])
    for check, status in seal.authorization_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Authorization Checks", ""])
    for item in seal.authorization_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Seal Checks", ""])
    for item in seal.coverage_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in seal.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in seal.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage:
        lines.append(
            "No manual execution start clearance packet final start authorization coverage audit seal gaps."
        )
    else:
        _append_code_markdown_list(lines, seal.missing_coverage)

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append(
            "No manual execution start clearance packet final start authorization coverage audit seal blockers."
        )
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Clearance Checklist", ""])
    for item in seal.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in seal.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_handoff_packet_handoff_checks() -> list[str]:
    return [
        "confirm_final_start_authorization_coverage_audit_seal_ready",
        "confirm_manual_execution_start_handoff_packet_ready",
        "confirm_final_start_authorization_ready",
        "confirm_go_no_go_start_decision_go",
        "confirm_start_authorization_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_sealed_candidate_order_preserved",
        "confirm_operator_authorization_checklist_preserved",
        "confirm_operator_start_checklist_ready",
        "confirm_verification_checklist_preserved",
        "confirm_rollback_path_preserved",
        "confirm_boundary_delta_zero",
    ]


def _next_session_manual_execution_start_handoff_packet_operator_start_checklist() -> list[str]:
    return [
        "confirm_final_start_authorization_coverage_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_go_no_go_start_decision",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_operator_authorization_checklist",
        "confirm_verification_checklist",
        "confirm_rollback_path",
        "confirm_manual_only_execution",
        "confirm_boundary_delta_zero",
    ]


def _next_session_manual_execution_start_handoff_packet_boundary_checks(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSeal,
) -> dict[str, str]:
    return {
        "start_clearance_packet_final_start_authorization_coverage_audit_seal_start_handoff_packet_read_only": "covered",
        "review_decision_delta_zero": (
            "covered" if seal.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if seal.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if seal.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_handoff_packet_blocked_reasons(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSeal,
    boundary_checks: dict[str, str],
) -> list[str]:
    reasons: list[str] = []
    if seal.seal_status not in {
        "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit",
        "sealed_no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_seal_not_ready")
    if seal.audit_status not in {
        "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_not_ready")
    if seal.authorization_status not in {
        "authorized_for_manual_execution_start_from_clearance_packet",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization",
    }:
        reasons.append("final_start_authorization_not_ready")
    if seal.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if seal.seal_source_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if seal.packet_source_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if seal.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if seal.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(seal.blocked_reasons)
    reasons.extend(seal.missing_coverage)
    reasons.extend(
        check
        for check, status in seal.authorization_coverage_checks.items()
        if status != "covered"
    )
    reasons.extend(
        check for check, status in seal.packet_coverage_checks.items() if status != "covered"
    )
    reasons.extend(
        check for check, status in seal.boundary_checks.items() if status != "covered"
    )
    reasons.extend(
        check for check, status in boundary_checks.items() if status != "covered"
    )
    if not seal.seal_checks:
        reasons.append("seal_checks_missing")
    if not seal.authorization_checks:
        reasons.append("authorization_checks_missing")
    if not seal.coverage_seal_checks:
        reasons.append("coverage_seal_checks_missing")
    if not seal.clearance_checklist:
        reasons.append("clearance_checklist_missing")
    if not seal.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not seal.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not seal.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not seal.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not seal.rollback_path:
        reasons.append("rollback_path_missing")
    if not seal.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not seal.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        seal.applied_review_decision_delta != 0
        or seal.applied_candidate_status_delta != 0
        or seal.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_handoff_packet_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSeal,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_handoff_packet"
    if (
        seal.seal_status
        == "sealed_no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit"
    ):
        return "no_manual_execution_required_start_handoff_packet"
    return "ready_for_manual_execution_start_handoff_packet"


def _next_session_manual_execution_start_handoff_status(
    handoff_packet_status: str,
) -> str:
    if handoff_packet_status == "ready_for_manual_execution_start_handoff_packet":
        return "ready_for_operator_manual_execution_start_handoff"
    if handoff_packet_status == "no_manual_execution_required_start_handoff_packet":
        return "no_manual_execution_required_start_handoff"
    return "blocked_before_operator_manual_execution_start_handoff"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacket:
    cache_token = _start_source_intake_call_cache()
    try:
        seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal(
            drafts,
            data_dir,
            preview_data_dir=preview_data_dir,
        )
        boundary_checks = _next_session_manual_execution_start_handoff_packet_boundary_checks(
            seal
        )
        blocked_reasons = _next_session_manual_execution_start_handoff_packet_blocked_reasons(
            seal,
            boundary_checks,
        )
        handoff_packet_status = _next_session_manual_execution_start_handoff_packet_status(
            seal,
            blocked_reasons,
        )
        return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacket(
            session_id=seal.session_id,
            packet_scope="manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_start_handoff_packet",
            handoff_packet_status=handoff_packet_status,
            handoff_status=_next_session_manual_execution_start_handoff_status(
                handoff_packet_status
            ),
            seal_status=seal.seal_status,
            audit_status=seal.audit_status,
            authorization_status=seal.authorization_status,
            seal_source_status=seal.seal_source_status,
            packet_status=seal.packet_status,
            packet_source_status=seal.packet_source_status,
            handoff_readiness=seal.handoff_readiness,
            go_no_go_start_decision=seal.go_no_go_start_decision,
            start_authorization=seal.start_authorization,
            source_audit_status=seal.source_audit_status,
            docket_status=seal.docket_status,
            handoff_checks=_next_session_manual_execution_start_handoff_packet_handoff_checks(),
            seal_checks=list(seal.seal_checks),
            authorization_coverage_checks=dict(seal.authorization_coverage_checks),
            authorization_checks=list(seal.authorization_checks),
            coverage_seal_checks=list(seal.coverage_seal_checks),
            packet_coverage_checks=dict(seal.packet_coverage_checks),
            missing_coverage=list(seal.missing_coverage),
            boundary_checks=dict(boundary_checks),
            clearance_checklist=list(seal.clearance_checklist),
            sealed_first_step=seal.sealed_first_step,
            sealed_candidate_order=list(seal.sealed_candidate_order),
            operator_authorization_checklist=list(
                seal.operator_authorization_checklist
            ),
            operator_start_checklist=_next_session_manual_execution_start_handoff_packet_operator_start_checklist(),
            verification_checklist=list(seal.verification_checklist),
            rollback_path=list(seal.rollback_path),
            post_completion_review=list(seal.post_completion_review),
            target_candidates=list(seal.target_candidates),
            blocked_reasons=blocked_reasons,
            boundary_confirmation=list(seal.boundary_confirmation),
            applied_review_decision_delta=0,
            applied_candidate_status_delta=0,
            formal_evidence_delta=0,
            boundary_notes=list(
                REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_HANDOFF_PACKET_BOUNDARY_NOTES
            ),
        )
    finally:
        _end_source_intake_call_cache(cache_token)


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit Seal Start Handoff Packet",
        "",
        "## Summary",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Packet scope: `{packet.packet_scope}`",
        f"- Handoff packet status: `{packet.handoff_packet_status}`",
        f"- Handoff status: `{packet.handoff_status}`",
        f"- Seal status: `{packet.seal_status}`",
        f"- Audit status: `{packet.audit_status}`",
        f"- Authorization status: `{packet.authorization_status}`",
        f"- Packet status: `{packet.packet_status}`",
        f"- Seal source status: `{packet.seal_source_status}`",
        f"- Packet source status: `{packet.packet_source_status}`",
        f"- Handoff readiness: `{packet.handoff_readiness}`",
        f"- Go/no-go start decision: `{packet.go_no_go_start_decision}`",
        f"- Start authorization: `{packet.start_authorization}`",
        f"- Source audit status: `{packet.source_audit_status}`",
        f"- Docket status: `{packet.docket_status}`",
        f"- Sealed first step: `{packet.sealed_first_step}`",
        f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start handoff packet is read-only planning metadata.",
        "",
        "## Handoff Checks",
        "",
    ]
    for item in packet.handoff_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Seal Checks", ""])
    for item in packet.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Authorization Coverage Checks", ""])
    for check, status in packet.authorization_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Authorization Checks", ""])
    for item in packet.authorization_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Seal Checks", ""])
    for item in packet.coverage_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in packet.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in packet.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not packet.missing_coverage:
        lines.append(
            "No manual execution start clearance packet final start authorization coverage audit seal start handoff packet gaps."
        )
    else:
        _append_code_markdown_list(lines, packet.missing_coverage)

    lines.extend(["", "## Blocked Reasons", ""])
    if not packet.blocked_reasons:
        lines.append(
            "No manual execution start clearance packet final start authorization coverage audit seal start handoff packet blockers."
        )
    else:
        _append_code_markdown_list(lines, packet.blocked_reasons)

    lines.extend(["", "## Clearance Checklist", ""])
    for item in packet.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in packet.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in packet.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not packet.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(packet.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in packet.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in packet.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in packet.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in packet.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, packet.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_handoff_packet_coverage_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacket,
) -> dict[str, str]:
    return {
        "start_handoff_packet_ready": (
            "covered"
            if packet.handoff_packet_status
            in {
                "ready_for_manual_execution_start_handoff_packet",
                "no_manual_execution_required_start_handoff_packet",
            }
            else "missing"
        ),
        "handoff_status_ready": (
            "covered"
            if packet.handoff_status
            in {
                "ready_for_operator_manual_execution_start_handoff",
                "no_manual_execution_required_start_handoff",
            }
            else "missing"
        ),
        "final_start_authorization_coverage_audit_seal_status_preserved": (
            "covered"
            if packet.seal_status
            in {
                "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit",
                "sealed_no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
            }
            else "missing"
        ),
        "coverage_audit_status_preserved": (
            "covered"
            if packet.audit_status
            in {
                "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready",
                "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
            }
            else "missing"
        ),
        "authorization_status_preserved": (
            "covered"
            if packet.authorization_status
            in {
                "authorized_for_manual_execution_start_from_clearance_packet",
                "no_manual_execution_required_start_clearance_packet_final_start_authorization",
            }
            else "missing"
        ),
        "packet_status_preserved": (
            "covered"
            if packet.packet_status
            in {
                "ready_for_manual_execution_start_clearance_packet",
                "no_manual_execution_required_start_clearance_packet",
            }
            else "missing"
        ),
        "seal_source_status_preserved": (
            "covered" if packet.seal_source_status else "missing"
        ),
        "packet_source_status_preserved": (
            "covered" if packet.packet_source_status else "missing"
        ),
        "handoff_readiness_preserved": (
            "covered" if packet.handoff_readiness else "missing"
        ),
        "go_no_go_start_decision_preserved": (
            "covered"
            if packet.go_no_go_start_decision
            in {"go_for_operator_manual_execution", "no_manual_execution_required"}
            else "missing"
        ),
        "start_authorization_preserved": (
            "covered"
            if packet.start_authorization
            in {"authorized_to_start_manual_execution", "no_manual_execution_required"}
            else "missing"
        ),
        "source_audit_status_preserved": (
            "covered" if packet.source_audit_status else "missing"
        ),
        "docket_status_preserved": (
            "covered" if packet.docket_status else "missing"
        ),
        "handoff_checks_complete": (
            "covered" if packet.handoff_checks else "missing"
        ),
        "seal_checks_complete": "covered" if packet.seal_checks else "missing",
        "authorization_coverage_checks_complete": (
            "covered"
            if packet.authorization_coverage_checks
            and all(
                status == "covered"
                for status in packet.authorization_coverage_checks.values()
            )
            else "missing"
        ),
        "authorization_checks_complete": (
            "covered" if packet.authorization_checks else "missing"
        ),
        "coverage_seal_checks_complete": (
            "covered" if packet.coverage_seal_checks else "missing"
        ),
        "packet_coverage_checks_complete": (
            "covered"
            if packet.packet_coverage_checks
            and all(status == "covered" for status in packet.packet_coverage_checks.values())
            else "missing"
        ),
        "boundary_checks_complete": (
            "covered"
            if packet.boundary_checks
            and all(status == "covered" for status in packet.boundary_checks.values())
            else "missing"
        ),
        "clearance_checklist_complete": (
            "covered" if packet.clearance_checklist else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered" if packet.sealed_first_step else "missing"
        ),
        "sealed_candidate_order_preserved": (
            "covered" if packet.sealed_candidate_order else "missing"
        ),
        "operator_authorization_checklist_preserved": (
            "covered" if packet.operator_authorization_checklist else "missing"
        ),
        "operator_start_checklist_preserved": (
            "covered" if packet.operator_start_checklist else "missing"
        ),
        "verification_checklist_preserved": (
            "covered" if packet.verification_checklist else "missing"
        ),
        "rollback_path_preserved": "covered" if packet.rollback_path else "missing",
        "post_completion_review_preserved": (
            "covered" if packet.post_completion_review else "missing"
        ),
        "target_candidates_preserved": (
            "covered" if packet.target_candidates else "missing"
        ),
        "blocked_reasons_preserved": (
            "covered" if packet.blocked_reasons == [] else "missing"
        ),
        "boundary_confirmation_preserved": (
            "covered" if packet.boundary_confirmation else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if (
                packet.applied_review_decision_delta == 0
                and packet.applied_candidate_status_delta == 0
                and packet.formal_evidence_delta == 0
            )
            else "missing"
        ),
    }


def _next_session_manual_execution_start_handoff_packet_coverage_audit_boundary_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacket,
) -> dict[str, str]:
    return {
        "start_handoff_packet_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": (
            "covered" if packet.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if packet.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if packet.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_handoff_packet_coverage_missing(
    coverage_checks: dict[str, str],
    boundary_checks: dict[str, str],
    packet_missing_coverage: list[str],
) -> list[str]:
    missing = [
        check for check, status in coverage_checks.items() if status != "covered"
    ]
    missing.extend(
        check for check, status in boundary_checks.items() if status != "covered"
    )
    missing.extend(packet_missing_coverage)
    return _dedupe_preserving_order(missing)


def _next_session_manual_execution_start_handoff_packet_coverage_audit_blocked_reasons(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacket,
    missing_coverage: list[str],
) -> list[str]:
    reasons: list[str] = []
    if packet.handoff_packet_status not in {
        "ready_for_manual_execution_start_handoff_packet",
        "no_manual_execution_required_start_handoff_packet",
    }:
        reasons.append("start_handoff_packet_not_ready")
    if packet.handoff_status not in {
        "ready_for_operator_manual_execution_start_handoff",
        "no_manual_execution_required_start_handoff",
    }:
        reasons.append("start_handoff_not_ready")
    if packet.seal_status not in {
        "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit",
        "sealed_no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_seal_not_ready")
    if packet.audit_status not in {
        "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_not_ready")
    if packet.authorization_status not in {
        "authorized_for_manual_execution_start_from_clearance_packet",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization",
    }:
        reasons.append("final_start_authorization_not_ready")
    if packet.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if packet.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if packet.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(packet.blocked_reasons)
    reasons.extend(missing_coverage)
    if (
        packet.applied_review_decision_delta != 0
        or packet.applied_candidate_status_delta != 0
        or packet.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_handoff_packet_coverage_audit_status(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacket,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_handoff_packet_coverage_audit"
    if packet.handoff_packet_status == "no_manual_execution_required_start_handoff_packet":
        return "no_manual_execution_required_start_handoff_packet_coverage_audit"
    return "manual_execution_start_handoff_packet_coverage_audit_ready"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAudit:
    cache_token = _start_source_intake_call_cache()
    try:
        packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet(
            drafts,
            data_dir,
            preview_data_dir=preview_data_dir,
        )
        coverage_checks = _next_session_manual_execution_start_handoff_packet_coverage_checks(
            packet
        )
        boundary_checks = _next_session_manual_execution_start_handoff_packet_coverage_audit_boundary_checks(
            packet
        )
        missing_coverage = _next_session_manual_execution_start_handoff_packet_coverage_missing(
            coverage_checks,
            boundary_checks,
            packet.missing_coverage,
        )
        blocked_reasons = _next_session_manual_execution_start_handoff_packet_coverage_audit_blocked_reasons(
            packet,
            missing_coverage,
        )
        return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAudit(
            session_id=packet.session_id,
            audit_scope="manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit",
            audit_status=_next_session_manual_execution_start_handoff_packet_coverage_audit_status(
                packet,
                blocked_reasons,
            ),
            handoff_packet_status=packet.handoff_packet_status,
            handoff_status=packet.handoff_status,
            seal_status=packet.seal_status,
            coverage_audit_status=packet.audit_status,
            authorization_status=packet.authorization_status,
            packet_status=packet.packet_status,
            seal_source_status=packet.seal_source_status,
            packet_source_status=packet.packet_source_status,
            handoff_readiness=packet.handoff_readiness,
            go_no_go_start_decision=packet.go_no_go_start_decision,
            start_authorization=packet.start_authorization,
            source_audit_status=packet.source_audit_status,
            docket_status=packet.docket_status,
            coverage_checks=dict(coverage_checks),
            missing_coverage=list(missing_coverage),
            boundary_checks=dict(boundary_checks),
            handoff_checks=list(packet.handoff_checks),
            seal_checks=list(packet.seal_checks),
            authorization_coverage_checks=dict(packet.authorization_coverage_checks),
            authorization_checks=list(packet.authorization_checks),
            coverage_seal_checks=list(packet.coverage_seal_checks),
            packet_coverage_checks=dict(packet.packet_coverage_checks),
            clearance_checklist=list(packet.clearance_checklist),
            sealed_first_step=packet.sealed_first_step,
            sealed_candidate_order=list(packet.sealed_candidate_order),
            operator_authorization_checklist=list(
                packet.operator_authorization_checklist
            ),
            operator_start_checklist=list(packet.operator_start_checklist),
            verification_checklist=list(packet.verification_checklist),
            rollback_path=list(packet.rollback_path),
            post_completion_review=list(packet.post_completion_review),
            target_candidates=list(packet.target_candidates),
            blocked_reasons=blocked_reasons,
            boundary_confirmation=list(packet.boundary_confirmation),
            applied_review_decision_delta=0,
            applied_candidate_status_delta=0,
            formal_evidence_delta=0,
            boundary_notes=list(
                REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_HANDOFF_PACKET_COVERAGE_AUDIT_BOUNDARY_NOTES
            ),
        )
    finally:
        _end_source_intake_call_cache(cache_token)


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Handoff packet status: `{audit.handoff_packet_status}`",
        f"- Handoff status: `{audit.handoff_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Coverage audit status: `{audit.coverage_audit_status}`",
        f"- Authorization status: `{audit.authorization_status}`",
        f"- Packet status: `{audit.packet_status}`",
        f"- Seal source status: `{audit.seal_source_status}`",
        f"- Packet source status: `{audit.packet_source_status}`",
        f"- Handoff readiness: `{audit.handoff_readiness}`",
        f"- Go/no-go start decision: `{audit.go_no_go_start_decision}`",
        f"- Start authorization: `{audit.start_authorization}`",
        f"- Source audit status: `{audit.source_audit_status}`",
        f"- Docket status: `{audit.docket_status}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start handoff packet coverage audit is read-only planning metadata.",
        "",
        "## Coverage Checks",
        "",
    ]
    for check, status in audit.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage:
        lines.append("No manual execution start handoff packet coverage gaps.")
    else:
        _append_code_markdown_list(lines, audit.missing_coverage)

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in audit.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Handoff Checks", ""])
    for item in audit.handoff_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Seal Checks", ""])
    for item in audit.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Authorization Coverage Checks", ""])
    for check, status in audit.authorization_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Authorization Checks", ""])
    for item in audit.authorization_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Seal Checks", ""])
    for item in audit.coverage_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in audit.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Clearance Checklist", ""])
    for item in audit.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in audit.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in audit.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not audit.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No manual execution start handoff packet coverage audit blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_handoff_packet_coverage_audit_seal_checks() -> list[str]:
    return [
        "confirm_manual_execution_start_handoff_packet_coverage_audit_ready",
        "confirm_start_handoff_packet_ready",
        "confirm_final_start_authorization_coverage_audit_seal_preserved",
        "confirm_handoff_status_preserved",
        "confirm_go_no_go_start_decision_go",
        "confirm_start_authorization_preserved",
        "confirm_coverage_checks_complete",
        "confirm_boundary_checks_complete",
        "confirm_handoff_checks_preserved",
        "confirm_operator_start_checklist_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_sealed_candidate_order_preserved",
        "confirm_boundary_delta_zero",
    ]


def _next_session_manual_execution_start_handoff_packet_coverage_audit_seal_boundary_checks(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAudit,
) -> dict[str, str]:
    return {
        "start_handoff_packet_coverage_audit_seal_read_only": "covered",
        "review_decision_delta_zero": (
            "covered" if audit.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if audit.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if audit.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_handoff_packet_coverage_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAudit,
    boundary_checks: dict[str, str],
) -> list[str]:
    reasons: list[str] = []
    if audit.audit_status not in {
        "manual_execution_start_handoff_packet_coverage_audit_ready",
        "no_manual_execution_required_start_handoff_packet_coverage_audit",
    }:
        reasons.append("start_handoff_packet_coverage_audit_not_ready")
    if audit.handoff_packet_status not in {
        "ready_for_manual_execution_start_handoff_packet",
        "no_manual_execution_required_start_handoff_packet",
    }:
        reasons.append("start_handoff_packet_not_ready")
    if audit.handoff_status not in {
        "ready_for_operator_manual_execution_start_handoff",
        "no_manual_execution_required_start_handoff",
    }:
        reasons.append("start_handoff_not_ready")
    if audit.seal_status not in {
        "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit",
        "sealed_no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_seal_not_ready")
    if audit.coverage_audit_status not in {
        "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_not_ready")
    if audit.authorization_status not in {
        "authorized_for_manual_execution_start_from_clearance_packet",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization",
    }:
        reasons.append("final_start_authorization_not_ready")
    if audit.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if audit.seal_source_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if audit.packet_source_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if audit.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if audit.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(audit.blocked_reasons)
    reasons.extend(audit.missing_coverage)
    reasons.extend(
        check for check, status in audit.coverage_checks.items() if status != "covered"
    )
    reasons.extend(
        check for check, status in audit.boundary_checks.items() if status != "covered"
    )
    reasons.extend(
        check for check, status in boundary_checks.items() if status != "covered"
    )
    if not audit.handoff_checks:
        reasons.append("handoff_checks_missing")
    if not audit.seal_checks:
        reasons.append("source_seal_checks_missing")
    if not audit.authorization_coverage_checks:
        reasons.append("authorization_coverage_checks_missing")
    if not audit.authorization_checks:
        reasons.append("authorization_checks_missing")
    if not audit.coverage_seal_checks:
        reasons.append("coverage_seal_checks_missing")
    if not audit.packet_coverage_checks:
        reasons.append("packet_coverage_checks_missing")
    if not audit.clearance_checklist:
        reasons.append("clearance_checklist_missing")
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not audit.operator_start_checklist:
        reasons.append("operator_start_checklist_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.rollback_path:
        reasons.append("rollback_path_missing")
    if not audit.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_handoff_packet_coverage_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_handoff_packet_coverage_audit_seal"
    if audit.audit_status == "no_manual_execution_required_start_handoff_packet_coverage_audit":
        return "sealed_no_manual_execution_required_start_handoff_packet_coverage_audit"
    return "sealed_for_manual_execution_start_handoff_packet_coverage_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSeal:
    cache_token = _start_source_intake_call_cache()
    try:
        audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit(
            drafts,
            data_dir,
            preview_data_dir=preview_data_dir,
        )
        boundary_checks = _next_session_manual_execution_start_handoff_packet_coverage_audit_seal_boundary_checks(
            audit
        )
        blocked_reasons = _next_session_manual_execution_start_handoff_packet_coverage_audit_seal_blocked_reasons(
            audit,
            boundary_checks,
        )
        return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSeal(
            session_id=audit.session_id,
            seal_scope="manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_seal",
            seal_status=_next_session_manual_execution_start_handoff_packet_coverage_audit_seal_status(
                audit,
                blocked_reasons,
            ),
            audit_status=audit.audit_status,
            handoff_packet_status=audit.handoff_packet_status,
            handoff_status=audit.handoff_status,
            final_start_authorization_coverage_audit_seal_status=audit.seal_status,
            coverage_audit_status=audit.coverage_audit_status,
            authorization_status=audit.authorization_status,
            packet_status=audit.packet_status,
            seal_source_status=audit.seal_source_status,
            packet_source_status=audit.packet_source_status,
            handoff_readiness=audit.handoff_readiness,
            go_no_go_start_decision=audit.go_no_go_start_decision,
            start_authorization=audit.start_authorization,
            source_audit_status=audit.source_audit_status,
            docket_status=audit.docket_status,
            seal_checks=_next_session_manual_execution_start_handoff_packet_coverage_audit_seal_checks(),
            coverage_checks=dict(audit.coverage_checks),
            missing_coverage=list(audit.missing_coverage),
            boundary_checks=dict(boundary_checks),
            handoff_checks=list(audit.handoff_checks),
            source_seal_checks=list(audit.seal_checks),
            authorization_coverage_checks=dict(audit.authorization_coverage_checks),
            authorization_checks=list(audit.authorization_checks),
            coverage_seal_checks=list(audit.coverage_seal_checks),
            packet_coverage_checks=dict(audit.packet_coverage_checks),
            clearance_checklist=list(audit.clearance_checklist),
            sealed_first_step=audit.sealed_first_step,
            sealed_candidate_order=list(audit.sealed_candidate_order),
            operator_authorization_checklist=list(
                audit.operator_authorization_checklist
            ),
            operator_start_checklist=list(audit.operator_start_checklist),
            verification_checklist=list(audit.verification_checklist),
            rollback_path=list(audit.rollback_path),
            post_completion_review=list(audit.post_completion_review),
            target_candidates=list(audit.target_candidates),
            blocked_reasons=blocked_reasons,
            boundary_confirmation=list(audit.boundary_confirmation),
            applied_review_decision_delta=0,
            applied_candidate_status_delta=0,
            formal_evidence_delta=0,
            boundary_notes=list(
                REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_HANDOFF_PACKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES
            ),
        )
    finally:
        _end_source_intake_call_cache(cache_token)


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Handoff packet status: `{seal.handoff_packet_status}`",
        f"- Handoff status: `{seal.handoff_status}`",
        f"- Final start authorization coverage audit seal status: `{seal.final_start_authorization_coverage_audit_seal_status}`",
        f"- Coverage audit status: `{seal.coverage_audit_status}`",
        f"- Authorization status: `{seal.authorization_status}`",
        f"- Packet status: `{seal.packet_status}`",
        f"- Seal source status: `{seal.seal_source_status}`",
        f"- Packet source status: `{seal.packet_source_status}`",
        f"- Handoff readiness: `{seal.handoff_readiness}`",
        f"- Go/no-go start decision: `{seal.go_no_go_start_decision}`",
        f"- Start authorization: `{seal.start_authorization}`",
        f"- Source audit status: `{seal.source_audit_status}`",
        f"- Docket status: `{seal.docket_status}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start handoff packet coverage audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Checks", ""])
    for check, status in seal.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage:
        lines.append("No manual execution start handoff packet coverage audit seal gaps.")
    else:
        _append_code_markdown_list(lines, seal.missing_coverage)

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in seal.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Handoff Checks", ""])
    for item in seal.handoff_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Source Seal Checks", ""])
    for item in seal.source_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Authorization Coverage Checks", ""])
    for check, status in seal.authorization_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Authorization Checks", ""])
    for item in seal.authorization_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Seal Checks", ""])
    for item in seal.coverage_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in seal.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Clearance Checklist", ""])
    for item in seal.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in seal.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in seal.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No manual execution start handoff packet coverage audit seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_packet_start_checks() -> list[str]:
    return [
        "confirm_manual_execution_start_handoff_packet_coverage_audit_seal_ready",
        "confirm_operator_manual_execution_start_packet_ready",
        "confirm_start_handoff_packet_ready",
        "confirm_operator_start_checklist_ready",
        "confirm_go_no_go_start_decision_go",
        "confirm_start_authorization_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_sealed_candidate_order_preserved",
        "confirm_target_candidates_preserved",
        "confirm_verification_checklist_preserved",
        "confirm_rollback_path_preserved",
        "confirm_boundary_delta_zero",
    ]


def _next_session_manual_execution_start_packet_boundary_checks(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSeal,
) -> dict[str, str]:
    return {
        "start_handoff_packet_coverage_audit_seal_start_packet_read_only": "covered",
        "review_decision_delta_zero": (
            "covered" if seal.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if seal.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if seal.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_packet_blocked_reasons(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSeal,
    boundary_checks: dict[str, str],
) -> list[str]:
    reasons: list[str] = []
    if seal.seal_status not in {
        "sealed_for_manual_execution_start_handoff_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_handoff_packet_coverage_audit",
    }:
        reasons.append("start_handoff_packet_coverage_audit_seal_not_ready")
    if seal.audit_status not in {
        "manual_execution_start_handoff_packet_coverage_audit_ready",
        "no_manual_execution_required_start_handoff_packet_coverage_audit",
    }:
        reasons.append("start_handoff_packet_coverage_audit_not_ready")
    if seal.handoff_packet_status not in {
        "ready_for_manual_execution_start_handoff_packet",
        "no_manual_execution_required_start_handoff_packet",
    }:
        reasons.append("start_handoff_packet_not_ready")
    if seal.handoff_status not in {
        "ready_for_operator_manual_execution_start_handoff",
        "no_manual_execution_required_start_handoff",
    }:
        reasons.append("operator_start_handoff_not_ready")
    if seal.final_start_authorization_coverage_audit_seal_status not in {
        "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit",
        "sealed_no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_seal_not_ready")
    if seal.coverage_audit_status not in {
        "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_not_ready")
    if seal.authorization_status not in {
        "authorized_for_manual_execution_start_from_clearance_packet",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization",
    }:
        reasons.append("final_start_authorization_not_ready")
    if seal.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if seal.seal_source_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if seal.packet_source_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if seal.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if seal.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(seal.blocked_reasons)
    reasons.extend(seal.missing_coverage)
    reasons.extend(
        check for check, status in seal.coverage_checks.items() if status != "covered"
    )
    reasons.extend(
        check for check, status in seal.boundary_checks.items() if status != "covered"
    )
    reasons.extend(
        check for check, status in boundary_checks.items() if status != "covered"
    )
    if not seal.seal_checks:
        reasons.append("seal_checks_missing")
    if not seal.handoff_checks:
        reasons.append("handoff_checks_missing")
    if not seal.source_seal_checks:
        reasons.append("source_seal_checks_missing")
    if not seal.authorization_coverage_checks:
        reasons.append("authorization_coverage_checks_missing")
    if not seal.authorization_checks:
        reasons.append("authorization_checks_missing")
    if not seal.coverage_seal_checks:
        reasons.append("coverage_seal_checks_missing")
    if not seal.packet_coverage_checks:
        reasons.append("packet_coverage_checks_missing")
    if not seal.clearance_checklist:
        reasons.append("clearance_checklist_missing")
    if not seal.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not seal.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not seal.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not seal.operator_start_checklist:
        reasons.append("operator_start_checklist_missing")
    if not seal.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not seal.rollback_path:
        reasons.append("rollback_path_missing")
    if not seal.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not seal.target_candidates:
        reasons.append("target_candidates_missing")
    if not seal.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        seal.applied_review_decision_delta != 0
        or seal.applied_candidate_status_delta != 0
        or seal.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_packet_status(
    seal: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSeal,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_operator_manual_execution_start_packet"
    if seal.seal_status == "sealed_no_manual_execution_required_start_handoff_packet_coverage_audit":
        return "no_manual_execution_required_start_packet"
    return "ready_for_operator_manual_execution_start_packet"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacket:
    cache_token = _start_source_intake_call_cache()
    try:
        seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal(
            drafts,
            data_dir,
            preview_data_dir=preview_data_dir,
        )
        boundary_checks = _next_session_manual_execution_start_packet_boundary_checks(
            seal
        )
        blocked_reasons = _next_session_manual_execution_start_packet_blocked_reasons(
            seal,
            boundary_checks,
        )
        return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacket(
            session_id=seal.session_id,
            packet_scope="manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_seal_start_packet",
            start_packet_status=_next_session_manual_execution_start_packet_status(
                seal,
                blocked_reasons,
            ),
            seal_status=seal.seal_status,
            audit_status=seal.audit_status,
            handoff_packet_status=seal.handoff_packet_status,
            handoff_status=seal.handoff_status,
            final_start_authorization_coverage_audit_seal_status=seal.final_start_authorization_coverage_audit_seal_status,
            coverage_audit_status=seal.coverage_audit_status,
            authorization_status=seal.authorization_status,
            packet_status=seal.packet_status,
            seal_source_status=seal.seal_source_status,
            packet_source_status=seal.packet_source_status,
            handoff_readiness=seal.handoff_readiness,
            go_no_go_start_decision=seal.go_no_go_start_decision,
            start_authorization=seal.start_authorization,
            source_audit_status=seal.source_audit_status,
            docket_status=seal.docket_status,
            start_checks=_next_session_manual_execution_start_packet_start_checks(),
            seal_checks=list(seal.seal_checks),
            coverage_checks=dict(seal.coverage_checks),
            missing_coverage=list(seal.missing_coverage),
            boundary_checks=dict(boundary_checks),
            handoff_checks=list(seal.handoff_checks),
            source_seal_checks=list(seal.source_seal_checks),
            authorization_coverage_checks=dict(seal.authorization_coverage_checks),
            authorization_checks=list(seal.authorization_checks),
            coverage_seal_checks=list(seal.coverage_seal_checks),
            packet_coverage_checks=dict(seal.packet_coverage_checks),
            clearance_checklist=list(seal.clearance_checklist),
            sealed_first_step=seal.sealed_first_step,
            sealed_candidate_order=list(seal.sealed_candidate_order),
            operator_authorization_checklist=list(
                seal.operator_authorization_checklist
            ),
            operator_start_checklist=list(seal.operator_start_checklist),
            verification_checklist=list(seal.verification_checklist),
            rollback_path=list(seal.rollback_path),
            post_completion_review=list(seal.post_completion_review),
            target_candidates=list(seal.target_candidates),
            blocked_reasons=blocked_reasons,
            boundary_confirmation=list(seal.boundary_confirmation),
            applied_review_decision_delta=0,
            applied_candidate_status_delta=0,
            formal_evidence_delta=0,
            boundary_notes=list(
                REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_PACKET_BOUNDARY_NOTES
            ),
        )
    finally:
        _end_source_intake_call_cache(cache_token)


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Packet",
        "",
        "## Summary",
        "",
        f"- Session id: `{packet.session_id}`",
        f"- Packet scope: `{packet.packet_scope}`",
        f"- Start packet status: `{packet.start_packet_status}`",
        f"- Seal status: `{packet.seal_status}`",
        f"- Audit status: `{packet.audit_status}`",
        f"- Handoff packet status: `{packet.handoff_packet_status}`",
        f"- Handoff status: `{packet.handoff_status}`",
        f"- Final start authorization coverage audit seal status: `{packet.final_start_authorization_coverage_audit_seal_status}`",
        f"- Coverage audit status: `{packet.coverage_audit_status}`",
        f"- Authorization status: `{packet.authorization_status}`",
        f"- Packet status: `{packet.packet_status}`",
        f"- Seal source status: `{packet.seal_source_status}`",
        f"- Packet source status: `{packet.packet_source_status}`",
        f"- Handoff readiness: `{packet.handoff_readiness}`",
        f"- Go/no-go start decision: `{packet.go_no_go_start_decision}`",
        f"- Start authorization: `{packet.start_authorization}`",
        f"- Source audit status: `{packet.source_audit_status}`",
        f"- Docket status: `{packet.docket_status}`",
        f"- Sealed first step: `{packet.sealed_first_step}`",
        f"- Applied review decision delta: `{packet.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{packet.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{packet.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start packet is read-only planning metadata.",
        "",
        "## Start Checks",
        "",
    ]
    for item in packet.start_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Seal Checks", ""])
    for item in packet.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Checks", ""])
    for check, status in packet.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not packet.missing_coverage:
        lines.append("No manual execution start packet gaps.")
    else:
        _append_code_markdown_list(lines, packet.missing_coverage)

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in packet.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Handoff Checks", ""])
    for item in packet.handoff_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Source Seal Checks", ""])
    for item in packet.source_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Authorization Coverage Checks", ""])
    for check, status in packet.authorization_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Authorization Checks", ""])
    for item in packet.authorization_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Seal Checks", ""])
    for item in packet.coverage_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in packet.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Clearance Checklist", ""])
    for item in packet.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in packet.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in packet.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not packet.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(packet.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in packet.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in packet.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in packet.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in packet.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not packet.blocked_reasons:
        lines.append("No manual execution start packet blockers.")
    else:
        _append_code_markdown_list(lines, packet.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, packet.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(packet.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_packet_coverage_audit_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacket,
) -> dict[str, str]:
    return {
        "start_packet_ready": (
            "covered"
            if packet.start_packet_status
            in {
                "ready_for_operator_manual_execution_start_packet",
                "no_manual_execution_required_start_packet",
            }
            else "missing"
        ),
        "start_packet_source_audit_status_preserved": (
            "covered"
            if packet.audit_status
            in {
                "manual_execution_start_handoff_packet_coverage_audit_ready",
                "no_manual_execution_required_start_handoff_packet_coverage_audit",
            }
            else "missing"
        ),
        "start_handoff_packet_coverage_audit_seal_status_preserved": (
            "covered"
            if packet.seal_status
            in {
                "sealed_for_manual_execution_start_handoff_packet_coverage_audit",
                "sealed_no_manual_execution_required_start_handoff_packet_coverage_audit",
            }
            else "missing"
        ),
        "handoff_packet_status_preserved": (
            "covered"
            if packet.handoff_packet_status
            in {
                "ready_for_manual_execution_start_handoff_packet",
                "no_manual_execution_required_start_handoff_packet",
            }
            else "missing"
        ),
        "handoff_status_preserved": (
            "covered"
            if packet.handoff_status
            in {
                "ready_for_operator_manual_execution_start_handoff",
                "no_manual_execution_required_start_handoff",
            }
            else "missing"
        ),
        "final_start_authorization_coverage_audit_seal_status_preserved": (
            "covered"
            if packet.final_start_authorization_coverage_audit_seal_status
            in {
                "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit",
                "sealed_no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
            }
            else "missing"
        ),
        "coverage_audit_status_preserved": (
            "covered"
            if packet.coverage_audit_status
            in {
                "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready",
                "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
            }
            else "missing"
        ),
        "authorization_status_preserved": (
            "covered"
            if packet.authorization_status
            in {
                "authorized_for_manual_execution_start_from_clearance_packet",
                "no_manual_execution_required_start_clearance_packet_final_start_authorization",
            }
            else "missing"
        ),
        "packet_status_preserved": (
            "covered"
            if packet.packet_status
            in {
                "ready_for_manual_execution_start_clearance_packet",
                "no_manual_execution_required_start_clearance_packet",
            }
            else "missing"
        ),
        "seal_source_status_preserved": (
            "covered"
            if packet.seal_source_status
            in {
                "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
                "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
            }
            else "missing"
        ),
        "packet_source_status_preserved": (
            "covered"
            if packet.packet_source_status
            in {
                "ready_for_manual_execution_start_authorization_packet",
                "no_manual_execution_required_start_authorization_packet",
            }
            else "missing"
        ),
        "handoff_readiness_preserved": (
            "covered" if packet.handoff_readiness else "missing"
        ),
        "go_no_go_start_decision_preserved": (
            "covered"
            if packet.go_no_go_start_decision
            in {
                "go_for_operator_manual_execution",
                "no_manual_execution_required",
            }
            else "missing"
        ),
        "start_authorization_preserved": (
            "covered"
            if packet.start_authorization
            in {
                "authorized_to_start_manual_execution",
                "no_manual_execution_required",
            }
            else "missing"
        ),
        "source_audit_status_preserved": (
            "covered"
            if packet.source_audit_status
            in {
                "manual_execution_start_docket_coverage_audit_ready",
                "no_manual_execution_required_start_docket_coverage_audit",
            }
            else "missing"
        ),
        "docket_status_preserved": (
            "covered"
            if packet.docket_status
            in {
                "ready_for_manual_execution_start_docket",
                "no_manual_execution_required_start_docket",
            }
            else "missing"
        ),
        "start_checks_complete": (
            "covered" if packet.start_checks else "missing"
        ),
        "seal_checks_complete": "covered" if packet.seal_checks else "missing",
        "source_coverage_checks_complete": (
            "covered"
            if packet.coverage_checks
            and all(status == "covered" for status in packet.coverage_checks.values())
            else "missing"
        ),
        "boundary_checks_complete": (
            "covered"
            if packet.boundary_checks
            and all(status == "covered" for status in packet.boundary_checks.values())
            else "missing"
        ),
        "handoff_checks_complete": (
            "covered" if packet.handoff_checks else "missing"
        ),
        "source_seal_checks_complete": (
            "covered" if packet.source_seal_checks else "missing"
        ),
        "authorization_coverage_checks_complete": (
            "covered"
            if packet.authorization_coverage_checks
            and all(
                status == "covered"
                for status in packet.authorization_coverage_checks.values()
            )
            else "missing"
        ),
        "authorization_checks_complete": (
            "covered" if packet.authorization_checks else "missing"
        ),
        "coverage_seal_checks_complete": (
            "covered" if packet.coverage_seal_checks else "missing"
        ),
        "packet_coverage_checks_complete": (
            "covered"
            if packet.packet_coverage_checks
            and all(
                status == "covered" for status in packet.packet_coverage_checks.values()
            )
            else "missing"
        ),
        "clearance_checklist_complete": (
            "covered" if packet.clearance_checklist else "missing"
        ),
        "sealed_first_step_preserved": (
            "covered" if packet.sealed_first_step else "missing"
        ),
        "sealed_candidate_order_preserved": (
            "covered" if packet.sealed_candidate_order else "missing"
        ),
        "operator_authorization_checklist_preserved": (
            "covered" if packet.operator_authorization_checklist else "missing"
        ),
        "operator_start_checklist_preserved": (
            "covered" if packet.operator_start_checklist else "missing"
        ),
        "verification_checklist_preserved": (
            "covered" if packet.verification_checklist else "missing"
        ),
        "rollback_path_preserved": (
            "covered" if packet.rollback_path else "missing"
        ),
        "post_completion_review_preserved": (
            "covered" if packet.post_completion_review else "missing"
        ),
        "target_candidates_preserved": (
            "covered" if packet.target_candidates else "missing"
        ),
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": (
            "covered" if packet.boundary_confirmation else "missing"
        ),
        "boundary_delta_zero": (
            "covered"
            if packet.applied_review_decision_delta == 0
            and packet.applied_candidate_status_delta == 0
            and packet.formal_evidence_delta == 0
            else "missing"
        ),
    }


def _next_session_manual_execution_start_packet_coverage_audit_boundary_checks(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacket,
) -> dict[str, str]:
    return {
        "start_packet_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": (
            "covered" if packet.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if packet.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if packet.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_packet_coverage_missing(
    coverage_checks: dict[str, str],
    boundary_checks: dict[str, str],
    packet_missing_coverage: list[str],
) -> list[str]:
    missing = [
        check for check, status in coverage_checks.items() if status != "covered"
    ]
    missing.extend(
        check for check, status in boundary_checks.items() if status != "covered"
    )
    missing.extend(packet_missing_coverage)
    return _dedupe_preserving_order(missing)


def _next_session_manual_execution_start_packet_coverage_audit_blocked_reasons(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacket,
    missing_coverage: list[str],
) -> list[str]:
    reasons: list[str] = []
    if packet.start_packet_status not in {
        "ready_for_operator_manual_execution_start_packet",
        "no_manual_execution_required_start_packet",
    }:
        reasons.append("operator_manual_execution_start_packet_not_ready")
    if packet.audit_status not in {
        "manual_execution_start_handoff_packet_coverage_audit_ready",
        "no_manual_execution_required_start_handoff_packet_coverage_audit",
    }:
        reasons.append("start_packet_source_coverage_audit_not_ready")
    if packet.seal_status not in {
        "sealed_for_manual_execution_start_handoff_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_handoff_packet_coverage_audit",
    }:
        reasons.append("start_handoff_packet_coverage_audit_seal_not_ready")
    if packet.handoff_packet_status not in {
        "ready_for_manual_execution_start_handoff_packet",
        "no_manual_execution_required_start_handoff_packet",
    }:
        reasons.append("start_handoff_packet_not_ready")
    if packet.handoff_status not in {
        "ready_for_operator_manual_execution_start_handoff",
        "no_manual_execution_required_start_handoff",
    }:
        reasons.append("operator_start_handoff_not_ready")
    if packet.final_start_authorization_coverage_audit_seal_status not in {
        "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit",
        "sealed_no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_seal_not_ready")
    if packet.coverage_audit_status not in {
        "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_not_ready")
    if packet.authorization_status not in {
        "authorized_for_manual_execution_start_from_clearance_packet",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization",
    }:
        reasons.append("final_start_authorization_not_ready")
    if packet.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if packet.seal_source_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if packet.packet_source_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if packet.source_audit_status not in {
        "manual_execution_start_docket_coverage_audit_ready",
        "no_manual_execution_required_start_docket_coverage_audit",
    }:
        reasons.append("source_docket_coverage_audit_not_ready")
    if packet.docket_status not in {
        "ready_for_manual_execution_start_docket",
        "no_manual_execution_required_start_docket",
    }:
        reasons.append("start_docket_not_ready")
    if packet.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if packet.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(packet.blocked_reasons)
    reasons.extend(missing_coverage)
    if (
        packet.applied_review_decision_delta != 0
        or packet.applied_candidate_status_delta != 0
        or packet.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_packet_coverage_audit_status(
    packet: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacket,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_packet_coverage_audit"
    if packet.start_packet_status == "no_manual_execution_required_start_packet":
        return "no_manual_execution_required_start_packet_coverage_audit"
    return "manual_execution_start_packet_coverage_audit_ready"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAudit:
    cache_token = _start_source_intake_call_cache()
    try:
        packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet(
            drafts,
            data_dir,
            preview_data_dir=preview_data_dir,
        )
        coverage_checks = _next_session_manual_execution_start_packet_coverage_audit_checks(
            packet
        )
        boundary_checks = (
            _next_session_manual_execution_start_packet_coverage_audit_boundary_checks(
                packet
            )
        )
        missing_coverage = _next_session_manual_execution_start_packet_coverage_missing(
            coverage_checks,
            boundary_checks,
            packet.missing_coverage,
        )
        blocked_reasons = (
            _next_session_manual_execution_start_packet_coverage_audit_blocked_reasons(
                packet,
                missing_coverage,
            )
        )
        return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAudit(
            session_id=packet.session_id,
            audit_scope="manual_application_next_session_manual_execution_start_packet_coverage_audit",
            audit_status=_next_session_manual_execution_start_packet_coverage_audit_status(
                packet,
                blocked_reasons,
            ),
            start_packet_status=packet.start_packet_status,
            seal_status=packet.seal_status,
            start_packet_source_audit_status=packet.audit_status,
            handoff_packet_status=packet.handoff_packet_status,
            handoff_status=packet.handoff_status,
            final_start_authorization_coverage_audit_seal_status=packet.final_start_authorization_coverage_audit_seal_status,
            coverage_audit_status=packet.coverage_audit_status,
            authorization_status=packet.authorization_status,
            packet_status=packet.packet_status,
            seal_source_status=packet.seal_source_status,
            packet_source_status=packet.packet_source_status,
            handoff_readiness=packet.handoff_readiness,
            go_no_go_start_decision=packet.go_no_go_start_decision,
            start_authorization=packet.start_authorization,
            source_audit_status=packet.source_audit_status,
            docket_status=packet.docket_status,
            coverage_checks=dict(coverage_checks),
            source_coverage_checks=dict(packet.coverage_checks),
            missing_coverage=missing_coverage,
            boundary_checks=dict(boundary_checks),
            start_checks=list(packet.start_checks),
            seal_checks=list(packet.seal_checks),
            handoff_checks=list(packet.handoff_checks),
            source_seal_checks=list(packet.source_seal_checks),
            authorization_coverage_checks=dict(packet.authorization_coverage_checks),
            authorization_checks=list(packet.authorization_checks),
            coverage_seal_checks=list(packet.coverage_seal_checks),
            packet_coverage_checks=dict(packet.packet_coverage_checks),
            clearance_checklist=list(packet.clearance_checklist),
            sealed_first_step=packet.sealed_first_step,
            sealed_candidate_order=list(packet.sealed_candidate_order),
            operator_authorization_checklist=list(
                packet.operator_authorization_checklist
            ),
            operator_start_checklist=list(packet.operator_start_checklist),
            verification_checklist=list(packet.verification_checklist),
            rollback_path=list(packet.rollback_path),
            post_completion_review=list(packet.post_completion_review),
            target_candidates=list(packet.target_candidates),
            blocked_reasons=blocked_reasons,
            boundary_confirmation=list(packet.boundary_confirmation),
            applied_review_decision_delta=0,
            applied_candidate_status_delta=0,
            formal_evidence_delta=0,
            boundary_notes=list(
                REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_PACKET_COVERAGE_AUDIT_BOUNDARY_NOTES
            ),
        )
    finally:
        _end_source_intake_call_cache(cache_token)


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit",
        "",
        "## Summary",
        "",
        f"- Session id: `{audit.session_id}`",
        f"- Audit scope: `{audit.audit_scope}`",
        f"- Audit status: `{audit.audit_status}`",
        f"- Start packet status: `{audit.start_packet_status}`",
        f"- Seal status: `{audit.seal_status}`",
        f"- Start packet source audit status: `{audit.start_packet_source_audit_status}`",
        f"- Handoff packet status: `{audit.handoff_packet_status}`",
        f"- Handoff status: `{audit.handoff_status}`",
        f"- Final start authorization coverage audit seal status: `{audit.final_start_authorization_coverage_audit_seal_status}`",
        f"- Coverage audit status: `{audit.coverage_audit_status}`",
        f"- Authorization status: `{audit.authorization_status}`",
        f"- Packet status: `{audit.packet_status}`",
        f"- Seal source status: `{audit.seal_source_status}`",
        f"- Packet source status: `{audit.packet_source_status}`",
        f"- Handoff readiness: `{audit.handoff_readiness}`",
        f"- Go/no-go start decision: `{audit.go_no_go_start_decision}`",
        f"- Start authorization: `{audit.start_authorization}`",
        f"- Source audit status: `{audit.source_audit_status}`",
        f"- Docket status: `{audit.docket_status}`",
        f"- Sealed first step: `{audit.sealed_first_step}`",
        f"- Applied review decision delta: `{audit.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{audit.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{audit.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start packet coverage audit is read-only planning metadata.",
        "",
        "## Coverage Checks",
        "",
    ]
    for check, status in audit.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Source Coverage Checks", ""])
    for check, status in audit.source_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not audit.missing_coverage:
        lines.append("No manual execution start packet coverage audit gaps.")
    else:
        _append_code_markdown_list(lines, audit.missing_coverage)

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in audit.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Start Checks", ""])
    for item in audit.start_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Seal Checks", ""])
    for item in audit.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Handoff Checks", ""])
    for item in audit.handoff_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Source Seal Checks", ""])
    for item in audit.source_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Authorization Coverage Checks", ""])
    for check, status in audit.authorization_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Authorization Checks", ""])
    for item in audit.authorization_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Seal Checks", ""])
    for item in audit.coverage_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in audit.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Clearance Checklist", ""])
    for item in audit.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in audit.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in audit.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not audit.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(audit.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in audit.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in audit.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in audit.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in audit.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not audit.blocked_reasons:
        lines.append("No manual execution start packet coverage audit blockers.")
    else:
        _append_code_markdown_list(lines, audit.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, audit.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(audit.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def _next_session_manual_execution_start_packet_coverage_audit_seal_checks() -> list[str]:
    return [
        "confirm_manual_execution_start_packet_coverage_audit_ready",
        "confirm_operator_manual_execution_start_packet_ready",
        "confirm_start_packet_source_audit_status_preserved",
        "confirm_start_handoff_packet_coverage_audit_seal_preserved",
        "confirm_coverage_checks_complete",
        "confirm_source_coverage_checks_complete",
        "confirm_boundary_checks_complete",
        "confirm_start_checks_preserved",
        "confirm_operator_start_checklist_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_sealed_candidate_order_preserved",
        "confirm_boundary_delta_zero",
    ]


def _next_session_manual_execution_start_packet_coverage_audit_seal_boundary_checks(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAudit,
) -> dict[str, str]:
    return {
        "start_packet_coverage_audit_seal_read_only": "covered",
        "review_decision_delta_zero": (
            "covered" if audit.applied_review_decision_delta == 0 else "missing"
        ),
        "candidate_status_delta_zero": (
            "covered" if audit.applied_candidate_status_delta == 0 else "missing"
        ),
        "formal_evidence_delta_zero": (
            "covered" if audit.formal_evidence_delta == 0 else "missing"
        ),
    }


def _next_session_manual_execution_start_packet_coverage_audit_seal_blocked_reasons(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAudit,
    boundary_checks: dict[str, str],
) -> list[str]:
    reasons: list[str] = []
    if audit.audit_status not in {
        "manual_execution_start_packet_coverage_audit_ready",
        "no_manual_execution_required_start_packet_coverage_audit",
    }:
        reasons.append("start_packet_coverage_audit_not_ready")
    if audit.start_packet_status not in {
        "ready_for_operator_manual_execution_start_packet",
        "no_manual_execution_required_start_packet",
    }:
        reasons.append("operator_manual_execution_start_packet_not_ready")
    if audit.start_packet_source_audit_status not in {
        "manual_execution_start_handoff_packet_coverage_audit_ready",
        "no_manual_execution_required_start_handoff_packet_coverage_audit",
    }:
        reasons.append("start_packet_source_coverage_audit_not_ready")
    if audit.seal_status not in {
        "sealed_for_manual_execution_start_handoff_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_handoff_packet_coverage_audit",
    }:
        reasons.append("start_handoff_packet_coverage_audit_seal_not_ready")
    if audit.handoff_packet_status not in {
        "ready_for_manual_execution_start_handoff_packet",
        "no_manual_execution_required_start_handoff_packet",
    }:
        reasons.append("start_handoff_packet_not_ready")
    if audit.handoff_status not in {
        "ready_for_operator_manual_execution_start_handoff",
        "no_manual_execution_required_start_handoff",
    }:
        reasons.append("operator_start_handoff_not_ready")
    if audit.final_start_authorization_coverage_audit_seal_status not in {
        "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit",
        "sealed_no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_seal_not_ready")
    if audit.coverage_audit_status not in {
        "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization_coverage_audit",
    }:
        reasons.append("final_start_authorization_coverage_audit_not_ready")
    if audit.authorization_status not in {
        "authorized_for_manual_execution_start_from_clearance_packet",
        "no_manual_execution_required_start_clearance_packet_final_start_authorization",
    }:
        reasons.append("final_start_authorization_not_ready")
    if audit.packet_status not in {
        "ready_for_manual_execution_start_clearance_packet",
        "no_manual_execution_required_start_clearance_packet",
    }:
        reasons.append("start_clearance_packet_not_ready")
    if audit.seal_source_status not in {
        "sealed_for_manual_execution_start_authorization_packet_coverage_audit",
        "sealed_no_manual_execution_required_start_authorization_packet_coverage_audit",
    }:
        reasons.append("start_authorization_packet_coverage_audit_seal_not_ready")
    if audit.packet_source_status not in {
        "ready_for_manual_execution_start_authorization_packet",
        "no_manual_execution_required_start_authorization_packet",
    }:
        reasons.append("start_authorization_packet_not_ready")
    if audit.source_audit_status not in {
        "manual_execution_start_docket_coverage_audit_ready",
        "no_manual_execution_required_start_docket_coverage_audit",
    }:
        reasons.append("source_docket_coverage_audit_not_ready")
    if audit.docket_status not in {
        "ready_for_manual_execution_start_docket",
        "no_manual_execution_required_start_docket",
    }:
        reasons.append("start_docket_not_ready")
    if audit.go_no_go_start_decision not in {
        "go_for_operator_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("go_no_go_start_decision_not_ready")
    if audit.start_authorization not in {
        "authorized_to_start_manual_execution",
        "no_manual_execution_required",
    }:
        reasons.append("start_authorization_not_ready")
    reasons.extend(audit.blocked_reasons)
    reasons.extend(audit.missing_coverage)
    reasons.extend(
        check for check, status in audit.coverage_checks.items() if status != "covered"
    )
    reasons.extend(
        check
        for check, status in audit.source_coverage_checks.items()
        if status != "covered"
    )
    reasons.extend(
        check for check, status in audit.boundary_checks.items() if status != "covered"
    )
    reasons.extend(
        check for check, status in boundary_checks.items() if status != "covered"
    )
    if not audit.start_checks:
        reasons.append("start_checks_missing")
    if not audit.seal_checks:
        reasons.append("source_seal_checks_missing")
    if not audit.handoff_checks:
        reasons.append("handoff_checks_missing")
    if not audit.source_seal_checks:
        reasons.append("source_handoff_seal_checks_missing")
    if not audit.authorization_coverage_checks:
        reasons.append("authorization_coverage_checks_missing")
    if not audit.authorization_checks:
        reasons.append("authorization_checks_missing")
    if not audit.coverage_seal_checks:
        reasons.append("coverage_seal_checks_missing")
    if not audit.packet_coverage_checks:
        reasons.append("packet_coverage_checks_missing")
    if not audit.clearance_checklist:
        reasons.append("clearance_checklist_missing")
    if not audit.sealed_first_step:
        reasons.append("sealed_first_step_missing")
    if not audit.sealed_candidate_order:
        reasons.append("sealed_candidate_order_missing")
    if not audit.operator_authorization_checklist:
        reasons.append("operator_authorization_checklist_missing")
    if not audit.operator_start_checklist:
        reasons.append("operator_start_checklist_missing")
    if not audit.verification_checklist:
        reasons.append("verification_checklist_missing")
    if not audit.rollback_path:
        reasons.append("rollback_path_missing")
    if not audit.post_completion_review:
        reasons.append("post_completion_review_missing")
    if not audit.boundary_confirmation:
        reasons.append("boundary_confirmation_missing")
    if (
        audit.applied_review_decision_delta != 0
        or audit.applied_candidate_status_delta != 0
        or audit.formal_evidence_delta != 0
    ):
        reasons.append("boundary_delta_nonzero")
    return _dedupe_preserving_order(reasons)


def _next_session_manual_execution_start_packet_coverage_audit_seal_status(
    audit: CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAudit,
    blocked_reasons: list[str],
) -> str:
    if blocked_reasons:
        return "blocked_before_manual_execution_start_packet_coverage_audit_seal"
    if audit.audit_status == "no_manual_execution_required_start_packet_coverage_audit":
        return "sealed_no_manual_execution_required_start_packet_coverage_audit"
    return "sealed_for_manual_execution_start_packet_coverage_audit"


def build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAuditSeal:
    cache_token = _start_source_intake_call_cache()
    try:
        audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit(
            drafts,
            data_dir,
            preview_data_dir=preview_data_dir,
        )
        boundary_checks = (
            _next_session_manual_execution_start_packet_coverage_audit_seal_boundary_checks(
                audit
            )
        )
        blocked_reasons = (
            _next_session_manual_execution_start_packet_coverage_audit_seal_blocked_reasons(
                audit,
                boundary_checks,
            )
        )
        return CandidateReviewManualApplicationNextSessionManualExecutionStartAuthorizationPacketCoverageAuditSealStartClearancePacketCoverageAuditSealFinalStartAuthorizationCoverageAuditSealStartHandoffPacketCoverageAuditSealStartPacketCoverageAuditSeal(
            session_id=audit.session_id,
            seal_scope="manual_application_next_session_manual_execution_start_packet_coverage_audit_seal",
            seal_status=_next_session_manual_execution_start_packet_coverage_audit_seal_status(
                audit,
                blocked_reasons,
            ),
            audit_status=audit.audit_status,
            start_packet_status=audit.start_packet_status,
            start_packet_source_audit_status=audit.start_packet_source_audit_status,
            start_handoff_packet_coverage_audit_seal_status=audit.seal_status,
            handoff_packet_status=audit.handoff_packet_status,
            handoff_status=audit.handoff_status,
            final_start_authorization_coverage_audit_seal_status=audit.final_start_authorization_coverage_audit_seal_status,
            coverage_audit_status=audit.coverage_audit_status,
            authorization_status=audit.authorization_status,
            packet_status=audit.packet_status,
            seal_source_status=audit.seal_source_status,
            packet_source_status=audit.packet_source_status,
            handoff_readiness=audit.handoff_readiness,
            go_no_go_start_decision=audit.go_no_go_start_decision,
            start_authorization=audit.start_authorization,
            source_audit_status=audit.source_audit_status,
            docket_status=audit.docket_status,
            seal_checks=_next_session_manual_execution_start_packet_coverage_audit_seal_checks(),
            coverage_checks=dict(audit.coverage_checks),
            source_coverage_checks=dict(audit.source_coverage_checks),
            missing_coverage=list(audit.missing_coverage),
            boundary_checks=dict(boundary_checks),
            start_checks=list(audit.start_checks),
            source_seal_checks=list(audit.seal_checks),
            handoff_checks=list(audit.handoff_checks),
            authorization_coverage_checks=dict(audit.authorization_coverage_checks),
            authorization_checks=list(audit.authorization_checks),
            coverage_seal_checks=list(audit.coverage_seal_checks),
            packet_coverage_checks=dict(audit.packet_coverage_checks),
            clearance_checklist=list(audit.clearance_checklist),
            sealed_first_step=audit.sealed_first_step,
            sealed_candidate_order=list(audit.sealed_candidate_order),
            operator_authorization_checklist=list(
                audit.operator_authorization_checklist
            ),
            operator_start_checklist=list(audit.operator_start_checklist),
            verification_checklist=list(audit.verification_checklist),
            rollback_path=list(audit.rollback_path),
            post_completion_review=list(audit.post_completion_review),
            target_candidates=list(audit.target_candidates),
            blocked_reasons=blocked_reasons,
            boundary_confirmation=list(audit.boundary_confirmation),
            applied_review_decision_delta=0,
            applied_candidate_status_delta=0,
            formal_evidence_delta=0,
            boundary_notes=list(
                REVIEW_MANUAL_APPLICATION_NEXT_SESSION_MANUAL_EXECUTION_START_PACKET_COVERAGE_AUDIT_SEAL_BOUNDARY_NOTES
            ),
        )
    finally:
        _end_source_intake_call_cache(cache_token)


def render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal_markdown(
    drafts: list[dict[str, Any]],
    data_dir: Path | str | None = None,
    *,
    preview_data_dir: Path | str | None = None,
) -> str:
    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal(
        drafts,
        data_dir,
        preview_data_dir=preview_data_dir,
    )
    lines = [
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit Seal",
        "",
        "## Summary",
        "",
        f"- Session id: `{seal.session_id}`",
        f"- Seal scope: `{seal.seal_scope}`",
        f"- Seal status: `{seal.seal_status}`",
        f"- Audit status: `{seal.audit_status}`",
        f"- Start packet status: `{seal.start_packet_status}`",
        f"- Start packet source audit status: `{seal.start_packet_source_audit_status}`",
        f"- Start handoff packet coverage audit seal status: `{seal.start_handoff_packet_coverage_audit_seal_status}`",
        f"- Handoff packet status: `{seal.handoff_packet_status}`",
        f"- Handoff status: `{seal.handoff_status}`",
        f"- Final start authorization coverage audit seal status: `{seal.final_start_authorization_coverage_audit_seal_status}`",
        f"- Coverage audit status: `{seal.coverage_audit_status}`",
        f"- Authorization status: `{seal.authorization_status}`",
        f"- Packet status: `{seal.packet_status}`",
        f"- Seal source status: `{seal.seal_source_status}`",
        f"- Packet source status: `{seal.packet_source_status}`",
        f"- Handoff readiness: `{seal.handoff_readiness}`",
        f"- Go/no-go start decision: `{seal.go_no_go_start_decision}`",
        f"- Start authorization: `{seal.start_authorization}`",
        f"- Source audit status: `{seal.source_audit_status}`",
        f"- Docket status: `{seal.docket_status}`",
        f"- Sealed first step: `{seal.sealed_first_step}`",
        f"- Applied review decision delta: `{seal.applied_review_decision_delta}`",
        f"- Applied candidate status delta: `{seal.applied_candidate_status_delta}`",
        f"- Formal evidence delta: `{seal.formal_evidence_delta}`",
        "- Boundary: Next-session manual execution start packet coverage audit seal is read-only planning metadata.",
        "",
        "## Seal Checks",
        "",
    ]
    for item in seal.seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Checks", ""])
    for check, status in seal.coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Source Coverage Checks", ""])
    for check, status in seal.source_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Missing Coverage", ""])
    if not seal.missing_coverage:
        lines.append("No manual execution start packet coverage audit seal gaps.")
    else:
        _append_code_markdown_list(lines, seal.missing_coverage)

    lines.extend(["", "## Boundary Checks", ""])
    for check, status in seal.boundary_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Start Checks", ""])
    for item in seal.start_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Source Seal Checks", ""])
    for item in seal.source_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Handoff Checks", ""])
    for item in seal.handoff_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Authorization Coverage Checks", ""])
    for check, status in seal.authorization_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Authorization Checks", ""])
    for item in seal.authorization_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Coverage Seal Checks", ""])
    for item in seal.coverage_seal_checks:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Packet Coverage Checks", ""])
    for check, status in seal.packet_coverage_checks.items():
        lines.append(f"- `{check}`: `{status}`")

    lines.extend(["", "## Clearance Checklist", ""])
    for item in seal.clearance_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Authorization Checklist", ""])
    for item in seal.operator_authorization_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Operator Start Checklist", ""])
    for item in seal.operator_start_checklist:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Sealed Candidate Order", ""])
    if not seal.sealed_candidate_order:
        lines.append("No candidates queued for the next manual session.")
    for index, candidate_id in enumerate(seal.sealed_candidate_order, 1):
        lines.append(f"{index}. `{candidate_id}`")

    lines.extend(["", "## Verification Checklist", ""])
    for item in seal.verification_checklist:
        if item.startswith("uv run "):
            lines.append(f"- [ ] `{item}`")
        else:
            lines.append(f"- [ ] {item}")

    lines.extend(["", "## Rollback Path", ""])
    for item in seal.rollback_path:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Post-Completion Review", ""])
    for item in seal.post_completion_review:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Boundary Confirmation", ""])
    for item in seal.boundary_confirmation:
        lines.append(f"- [ ] {item}")

    lines.extend(["", "## Blocked Reasons", ""])
    if not seal.blocked_reasons:
        lines.append("No manual execution start packet coverage audit seal blockers.")
    else:
        _append_code_markdown_list(lines, seal.blocked_reasons)

    lines.extend(["", "## Target Candidates", ""])
    _append_code_markdown_list(lines, seal.target_candidates)

    lines.extend(["", f"Boundary notes: {' '.join(seal.boundary_notes)}"])
    return "\n".join(lines) + "\n"


def find_duplicate_candidates(
    data_dir: Path | str | None = None,
) -> list[tuple[str, str]]:
    cache_key = _source_intake_call_cache_key("find_duplicate_candidates", data_dir)
    cached_duplicate_pairs = _source_intake_call_cache_get(cache_key)
    if cached_duplicate_pairs is not None:
        return list(cached_duplicate_pairs)

    candidates = load_candidate_extracts(data_dir)
    first_candidate_by_key: dict[tuple[str, str, str, str], CandidateExtract] = {}
    duplicate_pairs: list[tuple[str, str]] = []
    for candidate in candidates:
        key = (
            candidate.material_id,
            candidate.source_locator,
            candidate.proposed_rule_family,
            candidate.extracted_meaning,
        )
        original = first_candidate_by_key.get(key)
        if original is None:
            first_candidate_by_key[key] = candidate
        else:
            duplicate_pairs.append((original.candidate_id, candidate.candidate_id))
    _source_intake_call_cache_store(cache_key, duplicate_pairs)
    return duplicate_pairs


def validate_candidate_links(
    data_dir: Path | str | None = None,
    classical_data_dir: Path | str | None = None,
) -> None:
    candidates = load_candidate_extracts(data_dir)
    sources = load_classical_sources(classical_data_dir)
    evidence_units = load_evidence_units(classical_data_dir)
    source_conflicts = load_source_conflicts(classical_data_dir)
    curation_gaps = derive_curation_gaps(sources, evidence_units)

    evidence_ids = {unit.evidence_id for unit in evidence_units}
    conflict_ids = {conflict.conflict_id for conflict in source_conflicts}
    gap_ids = {gap.gap_id for gap in curation_gaps}

    for candidate in candidates:
        for evidence_id in candidate.related_evidence_ids:
            if evidence_id not in evidence_ids:
                raise SourceIntakeError(
                    f"{candidate.candidate_id} references unknown evidence: "
                    f"{evidence_id}"
                )
        for conflict_id in candidate.related_conflict_ids:
            if conflict_id not in conflict_ids:
                raise SourceIntakeError(
                    f"{candidate.candidate_id} references unknown conflict: "
                    f"{conflict_id}"
                )
        for gap_id in candidate.related_gap_ids:
            if gap_id not in gap_ids:
                raise SourceIntakeError(
                    f"{candidate.candidate_id} references unknown gap: {gap_id}"
                )


def build_intake_progress_report(
    data_dir: Path | str | None = None,
) -> IntakeProgressReport:
    intake_dir = _data_dir(data_dir)
    materials = load_source_materials(intake_dir)
    candidates = load_candidate_extracts(intake_dir)
    ready_candidates = list_approved_candidates_for_promotion(intake_dir)
    detected_duplicate_ids = {
        duplicate_id for _, duplicate_id in find_duplicate_candidates(intake_dir)
    }
    explicit_duplicate_ids = {
        candidate.candidate_id for candidate in candidates if candidate.duplicate_of
    }
    duplicate_ids = detected_duplicate_ids | explicit_duplicate_ids

    material_counts = Counter(
        material.preparation_status for material in materials
    )
    candidate_counts = Counter(candidate.status for candidate in candidates)
    risk_tier_counts = Counter(
        candidate.risk_tier for candidate in candidates if candidate.risk_tier
    )
    rule_family_counts = Counter(
        candidate.proposed_rule_family
        for candidate in candidates
        if candidate.proposed_rule_family
    )

    return IntakeProgressReport(
        material_counts=dict(material_counts),
        candidate_counts=dict(candidate_counts),
        risk_tier_counts=dict(risk_tier_counts),
        rule_family_counts=dict(rule_family_counts),
        pending_review_count=candidate_counts.get("pending_review", 0),
        approved_not_promoted_count=len(ready_candidates),
        blocked_or_rejected_count=(
            candidate_counts.get("blocked", 0) + candidate_counts.get("rejected", 0)
        ),
        duplicate_candidates=[
            candidate.candidate_id
            for candidate in candidates
            if candidate.candidate_id in duplicate_ids
        ],
        conflict_link_count=sum(
            1 for candidate in candidates if candidate.related_conflict_ids
        ),
        gap_link_count=sum(1 for candidate in candidates if candidate.related_gap_ids),
    )


def validate_intake_quality(
    data_dir: Path | str | None = None,
    classical_data_dir: Path | str | None = None,
) -> list[str]:
    intake_dir = _data_dir(data_dir)
    failures: list[str] = []

    try:
        candidates = load_candidate_extracts(intake_dir)
        load_review_decisions(intake_dir)
        batches = load_promotion_batches(intake_dir)
        validate_candidate_links(intake_dir, classical_data_dir)
    except SourceIntakeError as error:
        return [str(error)]

    promoted_candidate_ids = {
        candidate_id
        for batch in batches
        if batch.review_status in {"reviewed", "approved"}
        for candidate_id in batch.candidate_ids
    }
    for candidate in candidates:
        if (
            candidate.status == "promoted"
            and candidate.candidate_id not in promoted_candidate_ids
        ):
            failures.append(
                f"{candidate.candidate_id} promoted candidate requires "
                "reviewed or approved promotion batch"
            )

    from mingli_engine.evidence_risk import (
        ORDINARY_CONTENT,
        classify_evidence_content,
    )

    for candidate in candidates:
        if candidate.status not in {"approved", "promoted"}:
            continue
        if candidate.risk_tier != "ordinary":
            continue
        risk = classify_evidence_content(
            candidate.extracted_meaning, candidate.proposed_limitations
        )
        if risk.risk_class != ORDINARY_CONTENT:
            failures.append(
                f"{candidate.candidate_id} ordinary report-usable candidate "
                f"carries {risk.risk_class} content ({risk.matched_marker})"
            )
    return failures
