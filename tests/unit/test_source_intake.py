import json
from pathlib import Path

import pytest

from mingli_engine import models
from mingli_engine import source_intake


def test_source_intake_constants_cover_contract_values():
    assert models.MATERIAL_TYPES == frozenset(
        {"pdf", "markdown", "review_note", "other"}
    )
    assert models.MATERIAL_TRACKING_STATUSES == frozenset(
        {"external_untracked", "project_tracked", "derived_note"}
    )
    assert models.MATERIAL_PREPARATION_STATUSES == frozenset(
        {"not_started", "indexed", "partially_reviewed", "reviewed", "blocked"}
    )
    assert models.CANDIDATE_EXTRACT_STATUSES == frozenset(
        {
            "draft",
            "pending_review",
            "returned",
            "approved",
            "rejected",
            "blocked",
            "promoted",
        }
    )
    assert models.REVIEW_DECISIONS == frozenset(
        {"approved", "returned", "rejected", "blocked"}
    )
    assert models.PROMOTION_BATCH_REVIEW_STATUSES == frozenset(
        {"draft", "reviewed", "approved", "blocked"}
    )


def test_source_intake_dataclasses_construct_with_defaults():
    material = models.SourceMaterial(
        material_id="material_001",
        title="Material",
        material_type="pdf",
        file_label="material.pdf",
        tracking_status="external_untracked",
        preparation_status="not_started",
    )
    candidate = models.CandidateExtract(
        candidate_id="candidate_001",
        material_id=material.material_id,
        source_locator="review-note:material#one",
        extracted_meaning="A concise candidate signal.",
        proposed_rule_family="pattern_strength",
        risk_tier="ordinary",
        status="pending_review",
    )
    decision = models.ReviewDecision(
        decision_id="review_candidate_001",
        candidate_id=candidate.candidate_id,
        decision="approved",
        reviewer="maintainer",
        reviewed_at="2026-05-28",
        rationale="Source locator and limitations are reviewable.",
    )
    batch = models.PromotionBatch(
        promotion_batch_id="promotion_001",
        candidate_ids=[candidate.candidate_id],
        target_evidence_ids=["evidence_001"],
        review_status="draft",
        review_notes="Initial batch.",
    )
    report = models.IntakeProgressReport(
        material_counts={"not_started": 1},
        candidate_counts={"pending_review": 1},
        risk_tier_counts={"ordinary": 1},
        rule_family_counts={"pattern_strength": 1},
        pending_review_count=1,
        approved_not_promoted_count=0,
        blocked_or_rejected_count=0,
        duplicate_candidates=[],
        conflict_link_count=0,
        gap_link_count=0,
    )

    assert material.related_source_id == ""
    assert candidate.proposed_limitations == []
    assert candidate.related_evidence_ids == []
    assert decision.required_changes == []
    assert decision.approval_limitations == []
    assert batch.unresolved_issues == []
    assert report.pending_review_count == 1


def _write_json(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_read_json_list_reports_missing_invalid_and_non_array_payloads(tmp_path):
    with pytest.raises(source_intake.SourceIntakeError, match="missing data file"):
        source_intake._read_json_list(tmp_path / "missing.json")

    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{", encoding="utf-8")
    with pytest.raises(source_intake.SourceIntakeError, match="invalid JSON"):
        source_intake._read_json_list(invalid_json)

    object_payload = tmp_path / "object.json"
    _write_json(object_payload, {"not": "a list"})
    with pytest.raises(source_intake.SourceIntakeError, match="JSON array"):
        source_intake._read_json_list(object_payload)

    scalar_entries = tmp_path / "scalars.json"
    _write_json(scalar_entries, ["not an object"])
    with pytest.raises(source_intake.SourceIntakeError, match="entries must be JSON objects"):
        source_intake._read_json_list(scalar_entries)


def test_read_optional_json_list_returns_empty_for_missing_file(tmp_path):
    assert source_intake._read_optional_json_list(tmp_path / "missing.json") == []


def test_ensure_unique_rejects_duplicate_ids():
    with pytest.raises(source_intake.SourceIntakeError, match="duplicate material_id"):
        source_intake._ensure_unique(["material_001", "material_001"], "material_id")


def test_load_source_materials_accepts_external_registered_materials(tmp_path):
    materials = [
        {
            "material_id": "material_001",
            "title": "Material One",
            "material_type": "pdf",
            "file_label": "material-one.pdf",
            "tracking_status": "external_untracked",
            "preparation_status": "indexed",
            "related_source_id": "source_001",
            "scope_notes": "Can support candidate extraction after review.",
            "rights_notes": "Do not copy long passages.",
            "gap_reason": "",
        }
    ]
    _write_json(tmp_path / "source_materials.json", materials)

    loaded = source_intake.load_source_materials(
        tmp_path,
        known_source_ids={"source_001"},
    )

    assert loaded[0].material_id == "material_001"
    assert loaded[0].tracking_status == "external_untracked"
    assert loaded[0].related_source_id == "source_001"


def test_load_source_materials_rejects_invalid_statuses_and_blocked_without_gap(
    tmp_path,
):
    invalid_status = [
        {
            "material_id": "material_bad_status",
            "title": "Bad Status",
            "material_type": "pdf",
            "file_label": "bad.pdf",
            "tracking_status": "external_untracked",
            "preparation_status": "unknown",
        }
    ]
    _write_json(tmp_path / "source_materials.json", invalid_status)

    with pytest.raises(source_intake.SourceIntakeError, match="preparation_status"):
        source_intake.load_source_materials(tmp_path)

    blocked_without_gap = [
        {
            "material_id": "material_blocked",
            "title": "Blocked",
            "material_type": "pdf",
            "file_label": "blocked.pdf",
            "tracking_status": "external_untracked",
            "preparation_status": "blocked",
        }
    ]
    _write_json(tmp_path / "source_materials.json", blocked_without_gap)

    with pytest.raises(source_intake.SourceIntakeError, match="gap_reason"):
        source_intake.load_source_materials(tmp_path)


def test_load_source_materials_rejects_unknown_related_source(tmp_path):
    materials = [
        {
            "material_id": "material_unknown_source",
            "title": "Unknown Source",
            "material_type": "pdf",
            "file_label": "unknown.pdf",
            "tracking_status": "external_untracked",
            "preparation_status": "indexed",
            "related_source_id": "missing_source",
        }
    ]
    _write_json(tmp_path / "source_materials.json", materials)

    with pytest.raises(source_intake.SourceIntakeError, match="unknown source"):
        source_intake.load_source_materials(
            tmp_path,
            known_source_ids={"source_001"},
        )


def _write_minimal_materials(path: Path):
    _write_json(
        path / "source_materials.json",
        [
            {
                "material_id": "material_001",
                "title": "Material One",
                "material_type": "pdf",
                "file_label": "material-one.pdf",
                "tracking_status": "external_untracked",
                "preparation_status": "indexed",
            }
        ],
    )


def _candidate_payload(
    candidate_id: str,
    *,
    status: str = "pending_review",
    risk_tier: str = "ordinary",
    proposed_limitations: list[str] | None = None,
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "material_id": "material_001",
        "source_locator": f"review-note:{candidate_id}",
        "extracted_meaning": "A concise conditional candidate signal.",
        "proposed_rule_family": "pattern_strength",
        "risk_tier": risk_tier,
        "status": status,
        "proposed_limitations": proposed_limitations
        if proposed_limitations is not None
        else ["Use only as conditional traditional evidence."],
        "short_quote": "",
        "related_evidence_ids": [],
        "related_conflict_ids": [],
        "related_gap_ids": [],
        "duplicate_of": "",
        "created_by": "maintainer",
        "created_at": "2026-05-28",
    }


def _write_candidate_extracts(path: Path, candidates: list[dict[str, object]]) -> None:
    _write_minimal_materials(path)
    _write_json(path / "candidate_extracts.json", candidates)


def test_load_candidate_extracts_accepts_pending_review_candidates(tmp_path):
    _write_minimal_materials(tmp_path)
    _write_json(
        tmp_path / "candidate_extracts.json",
        [
            {
                "candidate_id": "candidate_001",
                "material_id": "material_001",
                "source_locator": "review-note:material#candidate-001",
                "extracted_meaning": "A concise conditional candidate signal.",
                "proposed_rule_family": "pattern_strength",
                "risk_tier": "ordinary",
                "status": "pending_review",
                "proposed_limitations": ["Use as a candidate only."],
                "short_quote": "",
                "related_evidence_ids": [],
                "related_conflict_ids": [],
                "related_gap_ids": [],
                "duplicate_of": "",
                "created_by": "maintainer",
                "created_at": "2026-05-28",
            }
        ],
    )

    loaded = source_intake.load_candidate_extracts(tmp_path)

    assert loaded[0].candidate_id == "candidate_001"
    assert loaded[0].status == "pending_review"
    assert loaded[0].material_id == "material_001"


def test_load_candidate_extracts_requires_pending_review_fields(tmp_path):
    _write_minimal_materials(tmp_path)
    _write_json(
        tmp_path / "candidate_extracts.json",
        [
            {
                "candidate_id": "candidate_missing_locator",
                "material_id": "material_001",
                "source_locator": "",
                "extracted_meaning": "A concise candidate signal.",
                "proposed_rule_family": "pattern_strength",
                "risk_tier": "ordinary",
                "status": "pending_review",
            }
        ],
    )

    with pytest.raises(source_intake.SourceIntakeError, match="source_locator"):
        source_intake.load_candidate_extracts(tmp_path)


def test_load_candidate_extracts_rejects_invalid_status_and_unknown_material(
    tmp_path,
):
    _write_minimal_materials(tmp_path)
    _write_json(
        tmp_path / "candidate_extracts.json",
        [
            {
                "candidate_id": "candidate_bad_status",
                "material_id": "material_001",
                "source_locator": "review-note:bad-status",
                "extracted_meaning": "A concise candidate signal.",
                "proposed_rule_family": "pattern_strength",
                "risk_tier": "ordinary",
                "status": "ready",
            }
        ],
    )

    with pytest.raises(source_intake.SourceIntakeError, match="status"):
        source_intake.load_candidate_extracts(tmp_path)

    _write_json(
        tmp_path / "candidate_extracts.json",
        [
            {
                "candidate_id": "candidate_unknown_material",
                "material_id": "missing_material",
                "source_locator": "review-note:missing-material",
                "extracted_meaning": "A concise candidate signal.",
                "proposed_rule_family": "pattern_strength",
                "risk_tier": "ordinary",
                "status": "pending_review",
            }
        ],
    )

    with pytest.raises(source_intake.SourceIntakeError, match="unknown material"):
        source_intake.load_candidate_extracts(tmp_path)


def test_load_candidate_extracts_rejects_long_copied_passages(tmp_path):
    _write_minimal_materials(tmp_path)
    _write_json(
        tmp_path / "candidate_extracts.json",
        [
            {
                "candidate_id": "candidate_long_meaning",
                "material_id": "material_001",
                "source_locator": "review-note:long-meaning",
                "extracted_meaning": "x" * 281,
                "proposed_rule_family": "pattern_strength",
                "risk_tier": "ordinary",
                "status": "pending_review",
            }
        ],
    )

    with pytest.raises(source_intake.SourceIntakeError, match="extracted_meaning"):
        source_intake.load_candidate_extracts(tmp_path)

    _write_json(
        tmp_path / "candidate_extracts.json",
        [
            {
                "candidate_id": "candidate_long_quote",
                "material_id": "material_001",
                "source_locator": "review-note:long-quote",
                "extracted_meaning": "A concise candidate signal.",
                "short_quote": "x" * 81,
                "proposed_rule_family": "pattern_strength",
                "risk_tier": "ordinary",
                "status": "pending_review",
            }
        ],
    )

    with pytest.raises(source_intake.SourceIntakeError, match="short_quote"):
        source_intake.load_candidate_extracts(tmp_path)


def test_load_candidate_extracts_rejects_absolute_outcome_language(tmp_path):
    _write_minimal_materials(tmp_path)
    _write_json(
        tmp_path / "candidate_extracts.json",
        [
            {
                "candidate_id": "candidate_absolute",
                "material_id": "material_001",
                "source_locator": "review-note:absolute",
                "extracted_meaning": "此候选一定会应验。",
                "proposed_rule_family": "high_risk_signal",
                "risk_tier": "high_risk",
                "status": "pending_review",
                "proposed_limitations": ["Do not use for exact outcomes."],
            }
        ],
    )

    with pytest.raises(source_intake.SourceIntakeError, match="absolute language"):
        source_intake.load_candidate_extracts(tmp_path)


def test_load_review_decisions_accepts_outcomes_and_requires_metadata(tmp_path):
    candidates = [
        _candidate_payload("candidate_approved", status="approved"),
        _candidate_payload("candidate_returned", status="returned"),
        _candidate_payload("candidate_rejected", status="rejected"),
        _candidate_payload("candidate_blocked", status="blocked"),
    ]
    _write_candidate_extracts(tmp_path, candidates)
    decisions = [
        {
            "decision_id": "review_candidate_approved",
            "candidate_id": "candidate_approved",
            "decision": "approved",
            "reviewer": "maintainer",
            "reviewed_at": "2026-05-28",
            "rationale": "Locator and conditional wording are reviewable.",
            "required_changes": [],
            "rejection_reason": "",
            "approval_limitations": ["Keep the report wording conditional."],
            "source_quality": "review_note",
            "confidence": "moderate",
        },
        {
            "decision_id": "review_candidate_returned",
            "candidate_id": "candidate_returned",
            "decision": "returned",
            "reviewer": "maintainer",
            "reviewed_at": "2026-05-28",
            "rationale": "The locator needs a narrower anchor.",
            "required_changes": ["Add a page or heading-level locator."],
            "rejection_reason": "",
            "approval_limitations": [],
            "source_quality": "review_note",
            "confidence": "weak",
        },
        {
            "decision_id": "review_candidate_rejected",
            "candidate_id": "candidate_rejected",
            "decision": "rejected",
            "reviewer": "maintainer",
            "reviewed_at": "2026-05-28",
            "rationale": "The candidate is not convertible into evidence.",
            "required_changes": [],
            "rejection_reason": "The summary cannot be made source-specific.",
            "approval_limitations": [],
            "source_quality": "secondary_index",
            "confidence": "weak",
        },
        {
            "decision_id": "review_candidate_blocked",
            "candidate_id": "candidate_blocked",
            "decision": "blocked",
            "reviewer": "maintainer",
            "reviewed_at": "2026-05-28",
            "rationale": "Rights and locator review are blocked.",
            "required_changes": [],
            "rejection_reason": "Source access must be clarified first.",
            "approval_limitations": [],
            "source_quality": "needs_recheck",
            "confidence": "weak",
        },
    ]
    _write_json(tmp_path / "review_decisions.json", decisions)

    loaded = source_intake.load_review_decisions(tmp_path)

    assert [decision.decision for decision in loaded] == [
        "approved",
        "returned",
        "rejected",
        "blocked",
    ]

    decisions[0]["approval_limitations"] = []
    _write_json(tmp_path / "review_decisions.json", decisions)
    with pytest.raises(source_intake.SourceIntakeError, match="approval_limitations"):
        source_intake.load_review_decisions(tmp_path)
    decisions[0]["approval_limitations"] = ["Keep the report wording conditional."]

    decisions[1]["required_changes"] = []
    _write_json(tmp_path / "review_decisions.json", decisions)
    with pytest.raises(source_intake.SourceIntakeError, match="required_changes"):
        source_intake.load_review_decisions(tmp_path)
    decisions[1]["required_changes"] = ["Add a page or heading-level locator."]

    decisions[2]["rejection_reason"] = ""
    _write_json(tmp_path / "review_decisions.json", decisions)
    with pytest.raises(source_intake.SourceIntakeError, match="rejection_reason"):
        source_intake.load_review_decisions(tmp_path)
    decisions[2]["rejection_reason"] = "The summary cannot be made source-specific."

    decisions[3]["rejection_reason"] = ""
    _write_json(tmp_path / "review_decisions.json", decisions)
    with pytest.raises(source_intake.SourceIntakeError, match="rejection_reason"):
        source_intake.load_review_decisions(tmp_path)


def test_load_review_decisions_enforces_high_risk_approval_controls(tmp_path):
    candidates = [
        _candidate_payload(
            "candidate_high_risk",
            status="approved",
            risk_tier="high_risk",
            proposed_limitations=[],
        )
    ]
    _write_candidate_extracts(tmp_path, candidates)
    decisions = [
        {
            "decision_id": "review_candidate_high_risk",
            "candidate_id": "candidate_high_risk",
            "decision": "approved",
            "reviewer": "maintainer",
            "reviewed_at": "2026-05-28",
            "rationale": "The candidate is bounded and reviewable.",
            "required_changes": [],
            "rejection_reason": "",
            "approval_limitations": ["Use uncertainty language in reports."],
            "source_quality": "review_note",
            "confidence": "moderate",
        }
    ]
    _write_json(tmp_path / "review_decisions.json", decisions)

    with pytest.raises(source_intake.SourceIntakeError, match="proposed_limitations"):
        source_intake.load_review_decisions(tmp_path)

    candidates[0]["proposed_limitations"] = [
        "Use only as bounded traditional high-risk signal evidence."
    ]
    _write_candidate_extracts(tmp_path, candidates)
    decisions[0]["source_quality"] = "needs_recheck"
    _write_json(tmp_path / "review_decisions.json", decisions)

    with pytest.raises(source_intake.SourceIntakeError, match="needs_recheck"):
        source_intake.load_review_decisions(tmp_path)


def test_load_promotion_batches_accepts_only_approved_candidates(tmp_path):
    candidates = [
        _candidate_payload("candidate_approved", status="approved"),
        _candidate_payload("candidate_returned", status="returned"),
    ]
    _write_candidate_extracts(tmp_path, candidates)
    _write_json(
        tmp_path / "review_decisions.json",
        [
            {
                "decision_id": "review_candidate_approved",
                "candidate_id": "candidate_approved",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-05-28",
                "rationale": "Locator and conditional wording are reviewable.",
                "required_changes": [],
                "rejection_reason": "",
                "approval_limitations": ["Keep the report wording conditional."],
                "source_quality": "review_note",
                "confidence": "moderate",
            },
            {
                "decision_id": "review_candidate_returned",
                "candidate_id": "candidate_returned",
                "decision": "returned",
                "reviewer": "maintainer",
                "reviewed_at": "2026-05-28",
                "rationale": "The locator needs a narrower anchor.",
                "required_changes": ["Add a page or heading-level locator."],
                "rejection_reason": "",
                "approval_limitations": [],
                "source_quality": "review_note",
                "confidence": "weak",
            },
        ],
    )
    batches = [
        {
            "promotion_batch_id": "promotion_001",
            "candidate_ids": ["candidate_approved"],
            "target_evidence_ids": ["evidence_future_001"],
            "review_status": "reviewed",
            "review_notes": "Approved candidate ready for formal evidence update.",
            "unresolved_issues": [],
        }
    ]
    _write_json(tmp_path / "promotion_batches.json", batches)

    loaded = source_intake.load_promotion_batches(tmp_path)

    assert loaded[0].candidate_ids == ["candidate_approved"]

    batches[0]["candidate_ids"] = ["candidate_returned"]
    _write_json(tmp_path / "promotion_batches.json", batches)
    with pytest.raises(source_intake.SourceIntakeError, match="approved"):
        source_intake.load_promotion_batches(tmp_path)

    batches[0]["candidate_ids"] = ["candidate_approved"]
    batches[0]["review_status"] = "ready"
    _write_json(tmp_path / "promotion_batches.json", batches)
    with pytest.raises(source_intake.SourceIntakeError, match="review_status"):
        source_intake.load_promotion_batches(tmp_path)

    batches[0]["review_status"] = "blocked"
    batches[0]["unresolved_issues"] = ["Resolve source access before promotion."]
    _write_json(tmp_path / "promotion_batches.json", batches)
    with pytest.raises(source_intake.SourceIntakeError, match="blocked"):
        source_intake.load_promotion_batches(tmp_path)


def test_list_approved_candidates_for_promotion_excludes_batched_candidates(tmp_path):
    candidates = [
        _candidate_payload("candidate_ready", status="approved"),
        _candidate_payload("candidate_batched", status="approved"),
    ]
    _write_candidate_extracts(tmp_path, candidates)
    _write_json(
        tmp_path / "review_decisions.json",
        [
            {
                "decision_id": "review_candidate_ready",
                "candidate_id": "candidate_ready",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-05-28",
                "rationale": "Locator and conditional wording are reviewable.",
                "required_changes": [],
                "rejection_reason": "",
                "approval_limitations": ["Keep the report wording conditional."],
                "source_quality": "review_note",
                "confidence": "moderate",
            },
            {
                "decision_id": "review_candidate_batched",
                "candidate_id": "candidate_batched",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-05-28",
                "rationale": "Locator and conditional wording are reviewable.",
                "required_changes": [],
                "rejection_reason": "",
                "approval_limitations": ["Keep the report wording conditional."],
                "source_quality": "review_note",
                "confidence": "moderate",
            },
        ],
    )
    _write_json(
        tmp_path / "promotion_batches.json",
        [
            {
                "promotion_batch_id": "promotion_001",
                "candidate_ids": ["candidate_batched"],
                "target_evidence_ids": ["evidence_future_001"],
                "review_status": "reviewed",
                "review_notes": "Candidate already prepared in a batch.",
                "unresolved_issues": [],
            }
        ],
    )

    ready = source_intake.list_approved_candidates_for_promotion(tmp_path)

    assert [candidate.candidate_id for candidate in ready] == ["candidate_ready"]


def test_find_duplicate_candidates_matches_candidate_source_and_meaning(tmp_path):
    duplicate_candidates = [
        _candidate_payload("candidate_duplicate_a"),
        _candidate_payload("candidate_duplicate_b"),
        _candidate_payload("candidate_distinct", risk_tier="sensitive"),
    ]
    duplicate_candidates[1]["source_locator"] = duplicate_candidates[0][
        "source_locator"
    ]
    duplicate_candidates[2]["extracted_meaning"] = "A different candidate signal."
    _write_candidate_extracts(tmp_path, duplicate_candidates)

    duplicates = source_intake.find_duplicate_candidates(tmp_path)

    assert duplicates == [
        ("candidate_duplicate_a", "candidate_duplicate_b"),
    ]


def test_validate_candidate_links_accepts_existing_evidence_conflict_and_gap(tmp_path):
    candidate = _candidate_payload("candidate_linked")
    candidate["related_evidence_ids"] = ["northeast_blind_image_001"]
    candidate["related_conflict_ids"] = ["conflict_high_risk_scope_001"]
    candidate["related_gap_ids"] = ["gap_blind_life_manual"]
    _write_candidate_extracts(tmp_path, [candidate])

    source_intake.validate_candidate_links(tmp_path)


def test_validate_candidate_links_rejects_unknown_evidence_conflict_and_gap(tmp_path):
    candidate = _candidate_payload("candidate_bad_evidence")
    candidate["related_evidence_ids"] = ["missing_evidence"]
    _write_candidate_extracts(tmp_path, [candidate])

    with pytest.raises(source_intake.SourceIntakeError, match="unknown evidence"):
        source_intake.validate_candidate_links(tmp_path)

    candidate = _candidate_payload("candidate_bad_conflict")
    candidate["related_conflict_ids"] = ["missing_conflict"]
    _write_candidate_extracts(tmp_path, [candidate])

    with pytest.raises(source_intake.SourceIntakeError, match="unknown conflict"):
        source_intake.validate_candidate_links(tmp_path)

    candidate = _candidate_payload("candidate_bad_gap")
    candidate["related_gap_ids"] = ["missing_gap"]
    _write_candidate_extracts(tmp_path, [candidate])

    with pytest.raises(source_intake.SourceIntakeError, match="unknown gap"):
        source_intake.validate_candidate_links(tmp_path)


def test_rejected_and_blocked_review_decisions_require_durable_reasons(tmp_path):
    candidates = [
        _candidate_payload("candidate_rejected", status="rejected"),
        _candidate_payload("candidate_blocked", status="blocked"),
    ]
    _write_candidate_extracts(tmp_path, candidates)
    decisions = [
        {
            "decision_id": "review_candidate_rejected",
            "candidate_id": "candidate_rejected",
            "decision": "rejected",
            "reviewer": "maintainer",
            "reviewed_at": "2026-05-28",
            "rationale": "The candidate does not map cleanly to a source-backed rule.",
            "required_changes": [],
            "rejection_reason": "n/a",
            "approval_limitations": [],
            "source_quality": "secondary_index",
            "confidence": "weak",
        },
        {
            "decision_id": "review_candidate_blocked",
            "candidate_id": "candidate_blocked",
            "decision": "blocked",
            "reviewer": "maintainer",
            "reviewed_at": "2026-05-28",
            "rationale": "Source access must be clarified.",
            "required_changes": [],
            "rejection_reason": "待查",
            "approval_limitations": [],
            "source_quality": "needs_recheck",
            "confidence": "weak",
        },
    ]
    _write_json(tmp_path / "review_decisions.json", decisions)

    with pytest.raises(source_intake.SourceIntakeError, match="durable"):
        source_intake.load_review_decisions(tmp_path)

    decisions[0][
        "rejection_reason"
    ] = "Reject because the locator is too broad for evidence use."
    _write_json(tmp_path / "review_decisions.json", decisions)

    with pytest.raises(source_intake.SourceIntakeError, match="durable"):
        source_intake.load_review_decisions(tmp_path)


def test_build_intake_progress_report_counts_material_candidate_risk_and_rule(
    tmp_path,
):
    _write_json(
        tmp_path / "source_materials.json",
        [
            {
                "material_id": "material_001",
                "title": "Material One",
                "material_type": "pdf",
                "file_label": "material-one.pdf",
                "tracking_status": "external_untracked",
                "preparation_status": "indexed",
            },
            {
                "material_id": "material_002",
                "title": "Material Two",
                "material_type": "pdf",
                "file_label": "material-two.pdf",
                "tracking_status": "external_untracked",
                "preparation_status": "blocked",
                "gap_reason": "Awaiting a reviewable source locator.",
            },
        ],
    )
    _write_json(
        tmp_path / "candidate_extracts.json",
        [
            _candidate_payload("candidate_pending_one"),
            _candidate_payload("candidate_pending_two", risk_tier="sensitive"),
            {
                **_candidate_payload("candidate_draft"),
                "material_id": "material_002",
                "status": "draft",
                "proposed_rule_family": "high_risk_signal",
                "risk_tier": "high_risk",
            },
        ],
    )
    _write_json(tmp_path / "review_decisions.json", [])
    _write_json(tmp_path / "promotion_batches.json", [])

    report = source_intake.build_intake_progress_report(tmp_path)

    assert report.material_counts == {"indexed": 1, "blocked": 1}
    assert report.candidate_counts == {"pending_review": 2, "draft": 1}
    assert report.risk_tier_counts == {
        "ordinary": 1,
        "sensitive": 1,
        "high_risk": 1,
    }
    assert report.rule_family_counts == {
        "pattern_strength": 2,
        "high_risk_signal": 1,
    }
    assert report.pending_review_count == 2


def test_build_intake_progress_report_counts_readiness_duplicates_and_links(
    tmp_path,
):
    candidates = [
        _candidate_payload("candidate_ready", status="approved"),
        _candidate_payload("candidate_batched", status="approved"),
        _candidate_payload("candidate_duplicate", status="rejected"),
        _candidate_payload("candidate_conflict"),
        _candidate_payload("candidate_gap"),
    ]
    candidates[2]["duplicate_of"] = "candidate_ready"
    candidates[3]["related_conflict_ids"] = ["conflict_high_risk_scope_001"]
    candidates[4]["related_gap_ids"] = ["gap_blind_life_manual"]
    _write_candidate_extracts(tmp_path, candidates)
    _write_json(
        tmp_path / "review_decisions.json",
        [
            {
                "decision_id": "review_candidate_ready",
                "candidate_id": "candidate_ready",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-05-28",
                "rationale": "Locator and conditional wording are reviewable.",
                "required_changes": [],
                "rejection_reason": "",
                "approval_limitations": ["Keep the report wording conditional."],
                "source_quality": "review_note",
                "confidence": "moderate",
            },
            {
                "decision_id": "review_candidate_batched",
                "candidate_id": "candidate_batched",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-05-28",
                "rationale": "Locator and conditional wording are reviewable.",
                "required_changes": [],
                "rejection_reason": "",
                "approval_limitations": ["Keep the report wording conditional."],
                "source_quality": "review_note",
                "confidence": "moderate",
            },
            {
                "decision_id": "review_candidate_duplicate",
                "candidate_id": "candidate_duplicate",
                "decision": "rejected",
                "reviewer": "maintainer",
                "reviewed_at": "2026-05-28",
                "rationale": "The candidate duplicates already captured intake material.",
                "required_changes": [],
                "rejection_reason": "Rejected because this duplicate is already represented by candidate_ready.",
                "approval_limitations": [],
                "source_quality": "review_note",
                "confidence": "moderate",
            },
        ],
    )
    _write_json(
        tmp_path / "promotion_batches.json",
        [
            {
                "promotion_batch_id": "promotion_001",
                "candidate_ids": ["candidate_batched"],
                "target_evidence_ids": ["evidence_future_001"],
                "review_status": "reviewed",
                "review_notes": "Candidate already prepared in a batch.",
                "unresolved_issues": [],
            }
        ],
    )

    report = source_intake.build_intake_progress_report(tmp_path)

    assert report.approved_not_promoted_count == 1
    assert report.blocked_or_rejected_count == 1
    assert report.duplicate_candidates == ["candidate_duplicate"]
    assert report.conflict_link_count == 1
    assert report.gap_link_count == 1


def test_validate_intake_quality_reports_blocking_failures(tmp_path):
    promoted_candidate = _candidate_payload("candidate_promoted", status="promoted")
    _write_candidate_extracts(tmp_path, [promoted_candidate])
    _write_json(
        tmp_path / "review_decisions.json",
        [
            {
                "decision_id": "review_candidate_promoted",
                "candidate_id": "candidate_promoted",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-05-28",
                "rationale": "Locator and conditional wording are reviewable.",
                "required_changes": [],
                "rejection_reason": "",
                "approval_limitations": ["Keep the report wording conditional."],
                "source_quality": "review_note",
                "confidence": "moderate",
            }
        ],
    )
    _write_json(tmp_path / "promotion_batches.json", [])

    failures = source_intake.validate_intake_quality(tmp_path)

    assert (
        "candidate_promoted promoted candidate requires reviewed or approved "
        "promotion batch"
    ) in failures

    linked_candidate = _candidate_payload("candidate_bad_gap")
    linked_candidate["related_gap_ids"] = ["missing_gap"]
    _write_candidate_extracts(tmp_path, [linked_candidate])
    _write_json(tmp_path / "review_decisions.json", [])
    _write_json(tmp_path / "promotion_batches.json", [])

    failures = source_intake.validate_intake_quality(tmp_path)

    assert any("unknown gap" in failure for failure in failures)
