"""Deterministic source-intake loading and validation for candidate evidence."""

from collections import Counter
import json
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


def _data_dir(data_dir: Path | str | None) -> Path:
    return Path(data_dir) if data_dir is not None else _DATA_DIR


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
    source_ids = _known_source_ids() if known_source_ids is None else known_source_ids
    materials = [
        _source_material_from_dict(item, source_ids)
        for item in _read_json_list(intake_dir / "source_materials.json")
    ]
    _ensure_unique([material.material_id for material in materials], "material_id")
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


def find_duplicate_candidates(
    data_dir: Path | str | None = None,
) -> list[tuple[str, str]]:
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
    return failures
