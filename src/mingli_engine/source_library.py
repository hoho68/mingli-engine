"""Deterministic source-library loading and validation for source planning."""

import json
from pathlib import Path
from typing import Any

from mingli_engine import classical_sources, source_intake
from mingli_engine.models import (
    CandidateExtract,
    CurationBatchPlan,
    EvidenceUnit,
    MATERIAL_TRACKING_STATUSES,
    PromotionBatch,
    RISK_TIERS,
    RULE_FAMILIES,
    SOURCE_LIBRARY_BATCH_STATUSES,
    SOURCE_LIBRARY_EFFORT_LEVELS,
    SOURCE_LIBRARY_EXPECTED_VALUES,
    SOURCE_LIBRARY_MATERIAL_TYPES,
    SOURCE_LIBRARY_NEXT_ACTIONS,
    SOURCE_LIBRARY_PRIORITY_LEVELS,
    SOURCE_LIBRARY_READINESS_STATUSES,
    SourceLibraryEntry,
    SourceLibraryProgressReport,
    SourcePriorityAssessment,
    SourceValueSummary,
    ReviewDecision,
)


class SourceLibraryError(ValueError):
    pass


_DATA_DIR = Path(__file__).resolve().parent / "data" / "source_library"
DURABLE_REASON_MIN_LENGTH = 20
NON_DURABLE_REASON_MARKERS = frozenset(
    {"n/a", "na", "none", "todo", "tbd", "待查", "待补", "未知"}
)
SOURCE_LIBRARY_SOURCE_QUALITIES = frozenset(
    {"strong", "moderate", "weak", "needs_recheck"}
)
SOURCE_LIBRARY_TEXT_LIMIT = 280
SOURCE_LIBRARY_REPORT_EVIDENCE_MARKERS = (
    "formal report evidence",
    "formal_evidence",
    "report evidence",
    "report-usable evidence",
    "approved evidence unit",
)
SOURCE_LIBRARY_ABSOLUTE_OUTCOME_PHRASES = (
    "\u5fc5\u5b9a",
    "\u6ce8\u5b9a",
    "\u4e00\u5b9a\u4f1a",
    "\u6b7b\u5b9a",
    "will definitely",
    "guaranteed outcome",
)
SOURCE_LIBRARY_PROHIBITED_HIGH_RISK_PHRASES = (
    "diagnose illness",
    "prescribe treatment",
    "medical treatment",
    "legal instruction",
    "psychological treatment",
    "investment instruction",
    "paid remedy upsell",
    "\u8bca\u65ad",
    "\u6cbb\u7597\u65b9\u6848",
    "\u6295\u8d44\u5efa\u8bae",
    "\u4ed8\u8d39\u5316\u89e3",
)


def _data_dir(data_dir: Path | str | None) -> Path:
    return Path(data_dir) if data_dir is not None else _DATA_DIR


def _sibling_data_dir(source_dir: Path, sibling_name: str) -> Path | None:
    sibling = source_dir.parent / sibling_name
    return sibling if sibling.exists() else None


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    try:
        raw_payload = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise SourceLibraryError(f"missing data file: {path.name}") from error

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as error:
        raise SourceLibraryError(f"invalid JSON in {path.name}: {error}") from error

    if not isinstance(payload, list):
        raise SourceLibraryError(f"{path.name} must contain a JSON array")
    if not all(isinstance(item, dict) for item in payload):
        raise SourceLibraryError(f"{path.name} entries must be JSON objects")
    return payload


def _read_optional_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return _read_json_list(path)


def _require_text(value: str, field_name: str, entry_id: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SourceLibraryError(f"{entry_id} has empty {field_name}")


def _require_string_list(value: Any, field_name: str, entry_id: str) -> None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise SourceLibraryError(f"{entry_id} has invalid {field_name}")


def _ensure_unique(ids: list[str], id_name: str) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise SourceLibraryError(f"duplicate {id_name}: {item_id}")
        seen.add(item_id)


def _is_durable_reason(value: str) -> bool:
    reason = value.strip()
    if len(reason) < DURABLE_REASON_MIN_LENGTH:
        return False
    return reason.lower() not in NON_DURABLE_REASON_MARKERS


def _normalize_boundary_text(value: str) -> str:
    return value.lower().replace("_", " ").replace("-", " ")


def _contains_marker(value: str, markers: tuple[str, ...]) -> bool:
    normalized = _normalize_boundary_text(value)
    return any(_normalize_boundary_text(marker) in normalized for marker in markers)


def _iter_quality_text_fields(
    entries: list[SourceLibraryEntry],
    assessments: list[SourcePriorityAssessment],
    plans: list[CurationBatchPlan],
) -> list[tuple[str, str, str]]:
    fields: list[tuple[str, str, str]] = []
    for entry in entries:
        fields.extend(
            (
                (entry.entry_id, "source_quality_notes", entry.source_quality_notes),
                (entry.entry_id, "rights_notes", entry.rights_notes),
                (entry.entry_id, "outcome_reason", entry.outcome_reason),
            )
        )
        fields.extend(
            (entry.entry_id, "risk_notes", note) for note in entry.risk_notes
        )
    for assessment in assessments:
        fields.append((assessment.assessment_id, "rationale", assessment.rationale))
    for plan in plans:
        fields.extend(
            (
                (plan.batch_plan_id, "goal", plan.goal),
                (plan.batch_plan_id, "review_capacity", plan.review_capacity),
                (plan.batch_plan_id, "completion_summary", plan.completion_summary),
                (
                    plan.batch_plan_id,
                    "recommended_next_batch",
                    plan.recommended_next_batch,
                ),
            )
        )
        fields.extend(
            (plan.batch_plan_id, "expected_output", item)
            for item in plan.expected_output
        )
    return fields


def _validate_source_library_boundary_text(
    entries: list[SourceLibraryEntry],
    assessments: list[SourcePriorityAssessment],
    plans: list[CurationBatchPlan],
) -> list[str]:
    failures: list[str] = []
    for owner_id, field_name, value in _iter_quality_text_fields(
        entries,
        assessments,
        plans,
    ):
        if not value:
            continue
        if len(value) > SOURCE_LIBRARY_TEXT_LIMIT:
            failures.append(
                f"{owner_id} {field_name} is too long for source-library metadata"
            )
        if _contains_marker(value, SOURCE_LIBRARY_REPORT_EVIDENCE_MARKERS):
            failures.append(
                f"{owner_id} {field_name} violates report evidence boundary"
            )
        if _contains_marker(value, SOURCE_LIBRARY_ABSOLUTE_OUTCOME_PHRASES):
            failures.append(f"{owner_id} {field_name} contains absolute language")
        if _contains_marker(value, SOURCE_LIBRARY_PROHIBITED_HIGH_RISK_PHRASES):
            failures.append(
                f"{owner_id} {field_name} contains prohibited high-risk wording"
            )
    return failures


def _source_library_entry_from_dict(data: dict[str, Any]) -> SourceLibraryEntry:
    try:
        entry = SourceLibraryEntry(**data)
    except TypeError as error:
        raise SourceLibraryError(f"invalid source-library entry: {error}") from error

    for field_name in (
        "entry_id",
        "title",
        "material_type",
        "local_reference",
        "tracking_status",
        "readiness_status",
        "risk_tier",
        "priority_level",
        "next_action",
    ):
        _require_text(getattr(entry, field_name), field_name, entry.entry_id or "?")

    if entry.material_type not in SOURCE_LIBRARY_MATERIAL_TYPES:
        raise SourceLibraryError(
            f"{entry.entry_id} has invalid material_type: {entry.material_type}"
        )
    if entry.tracking_status not in MATERIAL_TRACKING_STATUSES:
        raise SourceLibraryError(
            f"{entry.entry_id} has invalid tracking_status: {entry.tracking_status}"
        )
    if entry.readiness_status not in SOURCE_LIBRARY_READINESS_STATUSES:
        raise SourceLibraryError(
            f"{entry.entry_id} has invalid readiness_status: "
            f"{entry.readiness_status}"
        )
    if entry.risk_tier not in RISK_TIERS:
        raise SourceLibraryError(
            f"{entry.entry_id} has invalid risk_tier: {entry.risk_tier}"
        )
    if entry.priority_level not in SOURCE_LIBRARY_PRIORITY_LEVELS:
        raise SourceLibraryError(
            f"{entry.entry_id} has invalid priority_level: {entry.priority_level}"
        )
    if entry.next_action not in SOURCE_LIBRARY_NEXT_ACTIONS:
        raise SourceLibraryError(
            f"{entry.entry_id} has invalid next_action: {entry.next_action}"
        )

    _require_string_list(entry.topic_tags, "topic_tags", entry.entry_id)
    _require_string_list(entry.rule_families, "rule_families", entry.entry_id)
    _require_string_list(entry.risk_notes, "risk_notes", entry.entry_id)
    for rule_family in entry.rule_families:
        if rule_family not in RULE_FAMILIES:
            raise SourceLibraryError(
                f"{entry.entry_id} has unsupported rule_family: {rule_family}"
            )

    if entry.readiness_status == "ready_for_extraction":
        if not entry.topic_tags:
            raise SourceLibraryError(
                f"{entry.entry_id} ready_for_extraction requires topic_tags"
            )
        if not entry.rule_families:
            raise SourceLibraryError(
                f"{entry.entry_id} ready_for_extraction requires rule_families"
            )
        _require_text(
            entry.source_quality_notes,
            "source_quality_notes",
            entry.entry_id,
        )
        _require_text(entry.rights_notes, "rights_notes", entry.entry_id)

    if entry.risk_tier == "high_risk" and not entry.risk_notes:
        raise SourceLibraryError(f"{entry.entry_id} high_risk requires risk_notes")

    if entry.readiness_status in {"exhausted", "deferred", "duplicate", "blocked"}:
        if not _is_durable_reason(entry.outcome_reason):
            raise SourceLibraryError(
                f"{entry.entry_id} {entry.readiness_status} requires durable "
                "outcome_reason"
            )

    return entry


def _source_priority_assessment_from_dict(
    data: dict[str, Any],
    entry_ids: set[str],
) -> SourcePriorityAssessment:
    try:
        assessment = SourcePriorityAssessment(**data)
    except TypeError as error:
        raise SourceLibraryError(
            f"invalid source priority assessment: {error}"
        ) from error

    for field_name in (
        "assessment_id",
        "entry_id",
        "priority_level",
        "expected_value",
        "source_quality",
        "effort_level",
        "risk_tier",
        "rationale",
    ):
        _require_text(
            getattr(assessment, field_name),
            field_name,
            assessment.assessment_id or "?",
        )

    if assessment.entry_id not in entry_ids:
        raise SourceLibraryError(
            f"{assessment.assessment_id} references unknown entry: "
            f"{assessment.entry_id}"
        )
    if assessment.priority_level not in SOURCE_LIBRARY_PRIORITY_LEVELS:
        raise SourceLibraryError(
            f"{assessment.assessment_id} has invalid priority_level: "
            f"{assessment.priority_level}"
        )
    if assessment.expected_value not in SOURCE_LIBRARY_EXPECTED_VALUES:
        raise SourceLibraryError(
            f"{assessment.assessment_id} has invalid expected_value: "
            f"{assessment.expected_value}"
        )
    if assessment.source_quality not in SOURCE_LIBRARY_SOURCE_QUALITIES:
        raise SourceLibraryError(
            f"{assessment.assessment_id} has invalid source_quality: "
            f"{assessment.source_quality}"
        )
    if assessment.effort_level not in SOURCE_LIBRARY_EFFORT_LEVELS:
        raise SourceLibraryError(
            f"{assessment.assessment_id} has invalid effort_level: "
            f"{assessment.effort_level}"
        )
    if assessment.risk_tier not in RISK_TIERS:
        raise SourceLibraryError(
            f"{assessment.assessment_id} has invalid risk_tier: "
            f"{assessment.risk_tier}"
        )
    _require_string_list(
        assessment.target_gap_ids,
        "target_gap_ids",
        assessment.assessment_id,
    )
    _require_string_list(
        assessment.target_rule_families,
        "target_rule_families",
        assessment.assessment_id,
    )
    if not assessment.target_gap_ids and not assessment.target_rule_families:
        raise SourceLibraryError(
            f"{assessment.assessment_id} requires target gaps or target "
            "rule families"
        )
    for rule_family in assessment.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise SourceLibraryError(
                f"{assessment.assessment_id} has unsupported rule_family: "
                f"{rule_family}"
            )
    if (
        assessment.priority_level == "critical"
        and assessment.source_quality == "needs_recheck"
    ):
        raise SourceLibraryError(
            f"{assessment.assessment_id} critical priority cannot use "
            "source_quality needs_recheck"
        )
    if assessment.risk_tier == "high_risk" and "boundary" not in (
        assessment.rationale.lower()
    ):
        raise SourceLibraryError(
            f"{assessment.assessment_id} high_risk assessment must name the "
            "review boundary"
        )
    if assessment.priority_level == "deferred" and not _is_durable_reason(
        assessment.rationale
    ):
        raise SourceLibraryError(
            f"{assessment.assessment_id} deferred priority requires durable "
            "rationale"
        )

    return assessment


def _curation_batch_plan_from_dict(
    data: dict[str, Any],
    entries_by_id: dict[str, SourceLibraryEntry],
) -> CurationBatchPlan:
    try:
        plan = CurationBatchPlan(**data)
    except TypeError as error:
        raise SourceLibraryError(f"invalid curation batch plan: {error}") from error

    for field_name in ("batch_plan_id", "title", "goal", "risk_boundary", "status"):
        _require_text(getattr(plan, field_name), field_name, plan.batch_plan_id or "?")
    _require_string_list(plan.entry_ids, "entry_ids", plan.batch_plan_id)
    _require_string_list(plan.target_gap_ids, "target_gap_ids", plan.batch_plan_id)
    _require_string_list(
        plan.target_rule_families,
        "target_rule_families",
        plan.batch_plan_id,
    )
    _require_string_list(plan.expected_output, "expected_output", plan.batch_plan_id)

    if not plan.entry_ids:
        raise SourceLibraryError(f"{plan.batch_plan_id} requires entry_ids")
    if not plan.target_gap_ids and not plan.target_rule_families:
        raise SourceLibraryError(
            f"{plan.batch_plan_id} requires target gaps or target rule families"
        )
    if not plan.expected_output:
        raise SourceLibraryError(f"{plan.batch_plan_id} requires expected_output")
    if plan.risk_boundary not in RISK_TIERS:
        raise SourceLibraryError(
            f"{plan.batch_plan_id} has invalid risk_boundary: {plan.risk_boundary}"
        )
    if plan.status not in SOURCE_LIBRARY_BATCH_STATUSES:
        raise SourceLibraryError(
            f"{plan.batch_plan_id} has invalid status: {plan.status}"
        )
    _ensure_unique(plan.entry_ids, "entry_id")
    for entry_id in plan.entry_ids:
        if entry_id not in entries_by_id:
            raise SourceLibraryError(
                f"{plan.batch_plan_id} references unknown entry: {entry_id}"
            )
        entry = entries_by_id[entry_id]
        if plan.risk_boundary == "high_risk" and entry.risk_tier == "high_risk":
            if not entry.risk_notes:
                raise SourceLibraryError(
                    f"{plan.batch_plan_id} high_risk entry {entry_id} "
                    "requires risk_notes"
                )
    for rule_family in plan.target_rule_families:
        if rule_family not in RULE_FAMILIES:
            raise SourceLibraryError(
                f"{plan.batch_plan_id} has unsupported rule_family: {rule_family}"
            )
    if plan.status in {"completed", "deferred", "blocked"} and not (
        _is_durable_reason(plan.completion_summary)
    ):
        raise SourceLibraryError(
            f"{plan.batch_plan_id} {plan.status} requires durable "
            "completion_summary"
        )

    return plan


def _load_candidate_extracts(source_dir: Path) -> list[CandidateExtract]:
    intake_dir = _sibling_data_dir(source_dir, "source_intake")
    try:
        return source_intake.load_candidate_extracts(intake_dir)
    except source_intake.SourceIntakeError as error:
        raise SourceLibraryError(f"source-intake candidates invalid: {error}") from error


def _load_review_decisions(source_dir: Path) -> list[ReviewDecision]:
    intake_dir = _sibling_data_dir(source_dir, "source_intake")
    try:
        return source_intake.load_review_decisions(intake_dir)
    except source_intake.SourceIntakeError as error:
        raise SourceLibraryError(f"source-intake reviews invalid: {error}") from error


def _load_promotion_batches(source_dir: Path) -> list[PromotionBatch]:
    intake_dir = _sibling_data_dir(source_dir, "source_intake")
    try:
        return source_intake.load_promotion_batches(intake_dir)
    except source_intake.SourceIntakeError as error:
        raise SourceLibraryError(f"source-intake promotions invalid: {error}") from error


def _load_formal_evidence_units(source_dir: Path) -> list[EvidenceUnit]:
    classical_data_dir = _sibling_data_dir(source_dir, "classical_sources")
    try:
        return classical_sources.load_evidence_units(classical_data_dir)
    except classical_sources.ClassicalEvidenceError as error:
        raise SourceLibraryError(f"classical evidence invalid: {error}") from error


def _value_status_for_counts(
    *,
    readiness_status: str,
    candidate_count: int,
    approved_candidate_count: int,
    rejected_or_blocked_count: int,
    conflict_count: int,
    gap_count: int,
    promoted_evidence_count: int,
) -> str:
    if readiness_status == "blocked":
        return "blocked"
    if readiness_status == "deferred":
        return "deferred"
    if readiness_status in {"duplicate", "exhausted"}:
        return "non_useful_documented"
    if (
        approved_candidate_count
        or conflict_count
        or promoted_evidence_count
    ):
        return "value_produced"
    if rejected_or_blocked_count and rejected_or_blocked_count == candidate_count:
        return "non_useful_documented"
    if candidate_count or readiness_status in {"in_extraction", "review_completed"}:
        return "in_progress"
    return "not_started"


def _summarize_linked_candidates(
    *,
    subject_id: str,
    subject_type: str,
    candidates: list[CandidateExtract],
    decisions: list[ReviewDecision],
    promotion_batches: list[PromotionBatch],
    formal_evidence_ids: set[str],
    readiness_status: str,
    recommended_next_action: str,
) -> SourceValueSummary:
    candidate_ids = {candidate.candidate_id for candidate in candidates}
    approved_candidate_ids = {
        decision.candidate_id
        for decision in decisions
        if decision.candidate_id in candidate_ids and decision.decision == "approved"
    }
    rejected_or_blocked_ids = {
        decision.candidate_id
        for decision in decisions
        if decision.candidate_id in candidate_ids
        and decision.decision in {"rejected", "blocked"}
    }
    promoted_evidence_ids = {
        evidence_id
        for batch in promotion_batches
        if batch.review_status in {"reviewed", "approved"}
        for candidate_id in batch.candidate_ids
        if candidate_id in candidate_ids
        for evidence_id in batch.target_evidence_ids
        if evidence_id in formal_evidence_ids
    }
    conflict_ids = {
        conflict_id
        for candidate in candidates
        for conflict_id in candidate.related_conflict_ids
    }
    gap_ids = {
        gap_id for candidate in candidates for gap_id in candidate.related_gap_ids
    }
    value_status = _value_status_for_counts(
        readiness_status=readiness_status,
        candidate_count=len(candidates),
        approved_candidate_count=len(approved_candidate_ids),
        rejected_or_blocked_count=len(rejected_or_blocked_ids),
        conflict_count=len(conflict_ids),
        gap_count=len(gap_ids),
        promoted_evidence_count=len(promoted_evidence_ids),
    )

    return SourceValueSummary(
        subject_id=subject_id,
        subject_type=subject_type,
        candidate_count=len(candidates),
        approved_candidate_count=len(approved_candidate_ids),
        rejected_or_blocked_count=len(rejected_or_blocked_ids),
        conflict_count=len(conflict_ids),
        gap_count=len(gap_ids),
        promoted_evidence_count=len(promoted_evidence_ids),
        value_status=value_status,
        recommended_next_action=recommended_next_action,
    )


def _source_value_summary_from_loaded(
    entry: SourceLibraryEntry,
    candidates: list[CandidateExtract],
    decisions: list[ReviewDecision],
    promotion_batches: list[PromotionBatch],
    formal_evidence_ids: set[str],
) -> SourceValueSummary:
    linked_candidates = [
        candidate for candidate in candidates if candidate.material_id == entry.material_id
    ]
    return _summarize_linked_candidates(
        subject_id=entry.entry_id,
        subject_type="source",
        candidates=linked_candidates,
        decisions=decisions,
        promotion_batches=promotion_batches,
        formal_evidence_ids=formal_evidence_ids,
        readiness_status=entry.readiness_status,
        recommended_next_action=entry.next_action,
    )


def load_source_library_entries(
    data_dir: Path | str | None = None,
) -> list[SourceLibraryEntry]:
    source_dir = _data_dir(data_dir)
    entries = [
        _source_library_entry_from_dict(item)
        for item in _read_json_list(source_dir / "source_library_entries.json")
    ]
    _ensure_unique([entry.entry_id for entry in entries], "entry_id")
    return entries


def load_source_priority_assessments(
    data_dir: Path | str | None = None,
) -> list[SourcePriorityAssessment]:
    source_dir = _data_dir(data_dir)
    entries = load_source_library_entries(source_dir)
    entry_ids = {entry.entry_id for entry in entries}
    assessments = [
        _source_priority_assessment_from_dict(item, entry_ids)
        for item in _read_json_list(source_dir / "source_priority_assessments.json")
    ]
    _ensure_unique(
        [assessment.assessment_id for assessment in assessments],
        "assessment_id",
    )

    assessed_entry_ids = {assessment.entry_id for assessment in assessments}
    for entry in entries:
        if entry.priority_level in {"critical", "high"}:
            if entry.entry_id not in assessed_entry_ids:
                raise SourceLibraryError(
                    f"{entry.entry_id} high priority requires priority assessment"
                )
    return assessments


def load_curation_batch_plans(
    data_dir: Path | str | None = None,
) -> list[CurationBatchPlan]:
    source_dir = _data_dir(data_dir)
    entries = load_source_library_entries(source_dir)
    entries_by_id = {entry.entry_id: entry for entry in entries}
    plans = [
        _curation_batch_plan_from_dict(item, entries_by_id)
        for item in _read_json_list(source_dir / "curation_batch_plans.json")
    ]
    _ensure_unique([plan.batch_plan_id for plan in plans], "batch_plan_id")
    return plans


def list_next_source_candidates(
    limit: int = 5,
    data_dir: Path | str | None = None,
) -> list[str]:
    priority_rank = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
        "deferred": 4,
    }
    entries = load_source_library_entries(data_dir)
    indexed_entries = [
        (index, entry)
        for index, entry in enumerate(entries)
        if entry.readiness_status == "ready_for_extraction"
        and entry.next_action == "extract_candidates"
    ]
    ranked = sorted(
        indexed_entries,
        key=lambda item: (
            priority_rank[item[1].priority_level],
            item[0],
        ),
    )
    return [entry.entry_id for _, entry in ranked[:limit]]


def build_source_library_progress_report(
    data_dir: Path | str | None = None,
) -> SourceLibraryProgressReport:
    source_dir = _data_dir(data_dir)
    entries = load_source_library_entries(source_dir)
    candidates = _load_candidate_extracts(source_dir)
    decisions = _load_review_decisions(source_dir)
    promotion_batches = _load_promotion_batches(source_dir)
    formal_evidence_ids = {
        unit.evidence_id for unit in _load_formal_evidence_units(source_dir)
    }
    readiness_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    risk_tier_counts: dict[str, int] = {}
    rule_family_counts: dict[str, int] = {}
    value_status_counts: dict[str, int] = {}
    for entry in entries:
        readiness_counts[entry.readiness_status] = (
            readiness_counts.get(entry.readiness_status, 0) + 1
        )
        priority_counts[entry.priority_level] = (
            priority_counts.get(entry.priority_level, 0) + 1
        )
        risk_tier_counts[entry.risk_tier] = risk_tier_counts.get(entry.risk_tier, 0) + 1
        for rule_family in entry.rule_families:
            rule_family_counts[rule_family] = rule_family_counts.get(rule_family, 0) + 1
        value_summary = _source_value_summary_from_loaded(
            entry,
            candidates,
            decisions,
            promotion_batches,
            formal_evidence_ids,
        )
        value_status_counts[value_summary.value_status] = (
            value_status_counts.get(value_summary.value_status, 0) + 1
        )

    return SourceLibraryProgressReport(
        readiness_counts=readiness_counts,
        priority_counts=priority_counts,
        risk_tier_counts=risk_tier_counts,
        rule_family_counts=rule_family_counts,
        ready_for_extraction_count=readiness_counts.get("ready_for_extraction", 0),
        high_priority_count=(
            priority_counts.get("critical", 0) + priority_counts.get("high", 0)
        ),
        blocked_or_deferred_count=(
            readiness_counts.get("blocked", 0)
            + readiness_counts.get("deferred", 0)
        ),
        next_source_ids=list_next_source_candidates(data_dir=data_dir),
        value_status_counts=value_status_counts,
        high_risk_entry_ids=[
            entry.entry_id
            for entry in entries
            if entry.risk_tier == "high_risk"
        ],
    )


def build_source_value_summary(
    entry_id: str,
    data_dir: Path | str | None = None,
) -> SourceValueSummary:
    source_dir = _data_dir(data_dir)
    entries_by_id = {
        entry.entry_id: entry for entry in load_source_library_entries(source_dir)
    }
    if entry_id not in entries_by_id:
        raise SourceLibraryError(f"unknown source-library entry: {entry_id}")

    candidates = _load_candidate_extracts(source_dir)
    decisions = _load_review_decisions(source_dir)
    promotion_batches = _load_promotion_batches(source_dir)
    formal_evidence_ids = {
        unit.evidence_id for unit in _load_formal_evidence_units(source_dir)
    }
    return _source_value_summary_from_loaded(
        entries_by_id[entry_id],
        candidates,
        decisions,
        promotion_batches,
        formal_evidence_ids,
    )


def build_batch_value_summary(
    batch_plan_id: str,
    data_dir: Path | str | None = None,
) -> SourceValueSummary:
    source_dir = _data_dir(data_dir)
    entries_by_id = {
        entry.entry_id: entry for entry in load_source_library_entries(source_dir)
    }
    batch_plans_by_id = {
        plan.batch_plan_id: plan for plan in load_curation_batch_plans(source_dir)
    }
    if batch_plan_id not in batch_plans_by_id:
        raise SourceLibraryError(f"unknown curation batch plan: {batch_plan_id}")

    plan = batch_plans_by_id[batch_plan_id]
    material_ids = {
        entries_by_id[entry_id].material_id
        for entry_id in plan.entry_ids
        if entries_by_id[entry_id].material_id
    }
    candidates = [
        candidate
        for candidate in _load_candidate_extracts(source_dir)
        if candidate.material_id in material_ids
    ]
    decisions = _load_review_decisions(source_dir)
    promotion_batches = _load_promotion_batches(source_dir)
    formal_evidence_ids = {
        unit.evidence_id for unit in _load_formal_evidence_units(source_dir)
    }
    return _summarize_linked_candidates(
        subject_id=plan.batch_plan_id,
        subject_type="batch",
        candidates=candidates,
        decisions=decisions,
        promotion_batches=promotion_batches,
        formal_evidence_ids=formal_evidence_ids,
        readiness_status=plan.status,
        recommended_next_action=plan.recommended_next_batch or "no_action",
    )


def validate_source_library_quality(
    data_dir: Path | str | None = None,
) -> list[str]:
    try:
        entries = load_source_library_entries(data_dir)
        assessments = load_source_priority_assessments(data_dir)
        plans = load_curation_batch_plans(data_dir)
    except SourceLibraryError as error:
        return [str(error)]
    return _validate_source_library_boundary_text(entries, assessments, plans)
