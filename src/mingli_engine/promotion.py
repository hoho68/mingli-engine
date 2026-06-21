"""Explicit, controlled promotion of approved candidate extracts into formal evidence.

This module is the single place that writes candidate-derived evidence units into
``evidence_units.json``. It is intentionally separate from ``source_intake`` so the
read-only planning/preview boundary of the 013 review chain stays intact: nothing
here runs automatically. Callers must explicitly request ``apply_promotion`` and
must provide the ``theme``/``applicability``/``school`` fields that candidates do
not carry, so every promoted unit is a deliberate human decision.
"""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from mingli_engine import classical_sources
from mingli_engine.models import (
    CandidateExtract,
    EvidenceUnit,
    PromotionBatch,
    PromotionPlan,
    PromotionResult,
    ReviewDecision,
    SourceMaterial,
    REPORT_USABLE_REVIEW_STATUS,
)


class PromotionError(ValueError):
    pass


_HIGH_RISK_LIMITATION_MARKERS = ("精确", "不输出", "拒绝", "不得")
_SUMMARY_LIMIT = 280


def _intake_dir(intake_dir: Path | str | None) -> Path:
    if intake_dir is not None:
        return Path(intake_dir)
    from mingli_engine import source_intake

    return source_intake._DATA_DIR


def _corpus_dir(corpus_dir: Path | str | None) -> Path:
    if corpus_dir is not None:
        return Path(corpus_dir)
    return classical_sources._DATA_DIR


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise PromotionError(f"missing data file: {path.name}") from error
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise PromotionError(f"invalid JSON in {path.name}: {error}") from error
    if not isinstance(payload, list) or not all(
        isinstance(item, dict) for item in payload
    ):
        raise PromotionError(f"{path.name} must contain a JSON array of objects")
    return payload


def _load_intake(
    intake: Path,
) -> tuple[
    list[PromotionBatch],
    dict[str, CandidateExtract],
    dict[str, ReviewDecision],
    dict[str, SourceMaterial],
]:
    """Read intake JSON directly, bypassing source_intake's corpus coupling.

    source_intake.load_* validates that each material's related_source_id exists
    in the real classical_sources corpus. Promotion works against an explicit
    corpus_dir and must not be coupled to the default corpus, so we read the raw
    intake JSON here and resolve source ids against the provided corpus ourselves.
    """
    materials = [
        SourceMaterial(**m) for m in _read_json_list(intake / "source_materials.json")
    ]
    material_by_id = {m.material_id: m for m in materials}

    candidates = [
        CandidateExtract(**c)
        for c in _read_json_list(intake / "candidate_extracts.json")
    ]
    candidate_by_id = {c.candidate_id: c for c in candidates}

    decisions = [
        ReviewDecision(**d)
        for d in _read_json_list(intake / "review_decisions.json")
    ]
    review_by_candidate = {d.candidate_id: d for d in decisions}

    batches = [
        PromotionBatch(**b) for b in _read_json_list(intake / "promotion_batches.json")
    ]

    return batches, candidate_by_id, review_by_candidate, material_by_id


def _build_evidence_unit(
    candidate: CandidateExtract,
    review: ReviewDecision | None,
    material_by_id: dict[str, SourceMaterial],
    sources_by_id: dict[str, Any],
    target_evidence_id: str,
    override: dict[str, Any],
    curation_batch_id: str,
) -> EvidenceUnit:
    if candidate.status != "approved":
        raise PromotionError(
            f"{candidate.candidate_id} is not approved for promotion: {candidate.status}"
        )
    material = material_by_id.get(candidate.material_id)
    if material is None:
        raise PromotionError(
            f"{candidate.candidate_id} references unknown material: {candidate.material_id}"
        )
    source_id = material.related_source_id
    source = sources_by_id.get(source_id)
    if source is None:
        raise PromotionError(
            f"{candidate.candidate_id} maps to unknown source: {source_id}"
        )
    if source.review_status != REPORT_USABLE_REVIEW_STATUS:
        raise PromotionError(
            f"{candidate.candidate_id} maps to non-report-usable source "
            f"{source_id} (review_status={source.review_status})"
        )

    if not override.get("theme"):
        raise PromotionError(
            f"{target_evidence_id} requires a non-empty theme override"
        )
    applicability = override.get("applicability")
    if not applicability or not isinstance(applicability, list):
        raise PromotionError(
            f"{target_evidence_id} requires an applicability override list"
        )
    school = override.get("school", "")

    limitations = list(candidate.proposed_limitations)
    if review is not None and review.approval_limitations:
        limitations.extend(review.approval_limitations)

    if candidate.risk_tier == "high_risk":
        if not limitations:
            raise PromotionError(
                f"{target_evidence_id} high_risk unit requires limitations"
            )
        joined = " ".join(limitations).lower()
        if not any(marker in joined for marker in _HIGH_RISK_LIMITATION_MARKERS):
            raise PromotionError(
                f"{target_evidence_id} high_risk unit requires non-exact boundary limitations"
            )

    summary = candidate.extracted_meaning
    if len(summary) > _SUMMARY_LIMIT:
        raise PromotionError(
            f"{target_evidence_id} summary exceeds {_SUMMARY_LIMIT} characters"
        )

    unit = EvidenceUnit(
        evidence_id=target_evidence_id,
        source_id=source_id,
        source_ref=candidate.source_locator,
        theme=override["theme"],
        rule_family=candidate.proposed_rule_family,
        risk_tier=candidate.risk_tier,
        summary=summary,
        applicability=list(applicability),
        limitations=limitations,
        school=school,
        curation_batch_id=curation_batch_id,
        confidence=review.confidence if review is not None else "moderate",
        source_quality=review.source_quality if review is not None else "review_note",
        conflict_ids=list(candidate.related_conflict_ids),
    )
    # Validate through classical_sources' own validator so any rejection happens
    # here, during planning, before apply_promotion writes anything to disk.
    from dataclasses import asdict as _asdict

    classical_sources._evidence_unit_from_dict(_asdict(unit))
    return unit


def plan_promotion(
    intake_dir: Path | str | None = None,
    corpus_dir: Path | str | None = None,
    promotion_batch_id: str = "",
    evidence_overrides: dict[str, dict[str, Any]] | None = None,
    curation_batch_id: str = "",
) -> PromotionPlan:
    """Build a read-only promotion plan without writing anything.

    ``evidence_overrides`` maps each target evidence id to the candidate-absent
    fields (``theme``, ``applicability``, ``school``) a maintainer must supply.
    """
    intake = _intake_dir(intake_dir)
    corpus = _corpus_dir(corpus_dir)
    if not promotion_batch_id:
        raise PromotionError("promotion_batch_id is required")
    overrides = evidence_overrides or {}

    batches, candidate_by_id, review_by_candidate, material_by_id = _load_intake(intake)
    batch = next(
        (b for b in batches if b.promotion_batch_id == promotion_batch_id), None
    )
    if batch is None:
        raise PromotionError(f"unknown promotion batch: {promotion_batch_id}")

    sources = classical_sources.load_classical_sources(corpus)
    sources_by_id = {s.source_id: s for s in sources}

    existing_ids = {
        u.evidence_id
        for u in classical_sources._load_evidence_units_without_batch_validation(corpus)
    }

    evidence_units: list[EvidenceUnit] = []
    for candidate_id, target_evidence_id in zip(
        batch.candidate_ids, batch.target_evidence_ids
    ):
        if target_evidence_id in existing_ids:
            raise PromotionError(
                f"target evidence {target_evidence_id} already exists in evidence_units.json"
            )
        candidate = candidate_by_id.get(candidate_id)
        if candidate is None:
            raise PromotionError(
                f"{promotion_batch_id} references unknown candidate: {candidate_id}"
            )
        review = review_by_candidate.get(candidate_id)
        override = overrides.get(target_evidence_id, {})
        evidence_units.append(
            _build_evidence_unit(
                candidate,
                review,
                material_by_id,
                sources_by_id,
                target_evidence_id,
                override,
                curation_batch_id,
            )
        )

    return PromotionPlan(
        promotion_batch_id=promotion_batch_id,
        evidence_units=evidence_units,
        promoted_count=0,
        target_evidence_ids=batch.target_evidence_ids,
    )


def apply_promotion(
    intake_dir: Path | str | None = None,
    corpus_dir: Path | str | None = None,
    promotion_batch_id: str = "",
    evidence_overrides: dict[str, dict[str, Any]] | None = None,
    curation_batch_id: str = "",
) -> PromotionResult:
    """Execute a planned promotion: write evidence units and mark candidates promoted.

    This is the only function in the engine that mutates ``evidence_units.json``
    via candidate-derived data. It requires an explicit call.
    """
    intake = _intake_dir(intake_dir)
    corpus = _corpus_dir(corpus_dir)
    plan = plan_promotion(
        intake_dir=intake,
        corpus_dir=corpus,
        promotion_batch_id=promotion_batch_id,
        evidence_overrides=evidence_overrides,
        curation_batch_id=curation_batch_id,
    )

    units_path = corpus / "evidence_units.json"
    existing_raw = _read_json_list(units_path)
    for unit in plan.evidence_units:
        existing_raw.append(asdict(unit))
    units_path.write_text(
        json.dumps(existing_raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    classical_sources.load_evidence_units(corpus)

    candidate_path = intake / "candidate_extracts.json"
    candidates_raw = _read_json_list(candidate_path)
    promoted_candidate_ids = list(batch_candidate_ids_for_plan(plan, intake))
    promoted_id_set = set(promoted_candidate_ids)
    for entry in candidates_raw:
        if entry.get("candidate_id") in promoted_id_set:
            entry["status"] = "promoted"
    candidate_path.write_text(
        json.dumps(candidates_raw, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return PromotionResult(
        promotion_batch_id=promotion_batch_id,
        promoted_count=len(plan.evidence_units),
        target_evidence_ids=plan.target_evidence_ids,
        promoted_candidate_ids=promoted_candidate_ids,
    )


def batch_candidate_ids_for_plan(plan: PromotionPlan, intake: Path) -> list[str]:
    """Resolve which candidate ids belong to a plan's promotion batch."""
    batches, _, _, _ = _load_intake(intake)
    batch = next(
        (b for b in batches if b.promotion_batch_id == plan.promotion_batch_id), None
    )
    if batch is None:
        return []
    target_set = set(plan.target_evidence_ids)
    return [
        cid
        for cid, tid in zip(batch.candidate_ids, batch.target_evidence_ids)
        if tid in target_set
    ]
