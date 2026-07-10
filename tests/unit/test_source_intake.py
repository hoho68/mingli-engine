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



def _manual_application_candidate_ids() -> list[str]:
    return [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]


PROMOTED_MARKDOWN_LEARNING_CANDIDATE_IDS = {
    "candidate_markdown_batch_001_pattern_strength_001",
    "candidate_markdown_batch_001_ten_god_relation_001",
    "candidate_markdown_batch_001_branch_interaction_001",
    "candidate_markdown_batch_001_blind_image_method_001",
    "candidate_markdown_batch_002_useful_god_001",
    "candidate_markdown_batch_002_pattern_strength_001",
    "candidate_markdown_batch_002_luck_cycle_001",
    "candidate_markdown_batch_002_ten_god_relation_001",
    "candidate_markdown_batch_002_branch_route_001",
    "candidate_markdown_batch_002_useful_god_types_001",
    "candidate_markdown_batch_002_day_master_strength_basis_001",
    "candidate_markdown_batch_004_useful_god_001",
    "candidate_markdown_batch_004_pattern_strength_001",
    "candidate_markdown_batch_004_branch_interaction_001",
    "candidate_markdown_batch_004_luck_cycle_001",
    "candidate_markdown_batch_005_ten_god_relation_001",
    "candidate_markdown_batch_005_blind_image_method_001",
    "candidate_markdown_batch_005_branch_interaction_001",
}


PROMOTED_KSKELETON_CANDIDATE_IDS = {
    "candidate_kskeleton_q001_foundation_tables_001",
    "candidate_kskeleton_q002_yushi_tiaohou_001",
    "candidate_kskeleton_q002_shen_pattern_001",
    "candidate_kskeleton_q002_yuanhai_bilateral_001",
    "candidate_kskeleton_q003_geju_selection_001",
    "candidate_kskeleton_q003_day_master_strength_001",
    "candidate_kskeleton_q003_congwang_congshi_001",
    "candidate_kskeleton_q006_interaction_structure_001",
    "candidate_kskeleton_q004_mechanism_layer_001",
    "candidate_kskeleton_q004_cross_dependency_001",
    "candidate_kskeleton_q004_q006_dependency_001",
}


def _assert_markdown_line_locator(locator):
    assert locator.startswith("review-note:Markdown/source_batch_")
    assert "#L" in locator

    source_path_text, line_text = locator.removeprefix("review-note:").rsplit("#L", 1)
    line_number = int(line_text)
    source_path = Path(source_path_text)

    assert source_path.exists(), source_path
    assert 1 <= line_number <= len(source_path.read_text(encoding="utf-8").splitlines())


def _manual_application_candidate_payloads() -> list[dict[str, object]]:
    """Replicate the four 017 pending_review candidates as fixture seed data."""
    return [
        {
            "candidate_id": "candidate_mingli_pattern_strength_017_001",
            "material_id": "material_mingli_true_formula_teacher_pdf",
            "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001; locator_requirement=page_or_section_required",
            "extracted_meaning": "Pattern strength material should stay conditional until source locator and chart context are reviewed.",
            "short_quote": "",
            "proposed_rule_family": "pattern_strength",
            "risk_tier": "sensitive",
            "status": "pending_review",
            "proposed_limitations": [
                "State uncertainty for timing and pattern interpretation.",
                "Include limitation language; do not guarantee outcome timing.",
            ],
            "related_evidence_ids": [],
            "related_conflict_ids": [],
            "related_gap_ids": [],
            "duplicate_of": "",
            "created_by": "learning_reference_curation",
            "created_at": "2026-06-01",
        },
        {
            "candidate_id": "candidate_duan_ten_god_relation_017_001",
            "material_id": "material_duan_plain_mingxue_outline_pdf",
            "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001; locator_requirement=page_or_section_required",
            "extracted_meaning": "Duan Plain Mingxue Outline can organize ten-god relationships and pattern-strength review as source-backed taxonomy.",
            "short_quote": "",
            "proposed_rule_family": "ten_god_relation",
            "risk_tier": "ordinary",
            "status": "pending_review",
            "proposed_limitations": [
                "Keep as structural taxonomy until locator and chart context are reviewed.",
            ],
            "related_evidence_ids": [],
            "related_conflict_ids": [],
            "related_gap_ids": [],
            "duplicate_of": "",
            "created_by": "learning_reference_curation",
            "created_at": "2026-06-01",
        },
        {
            "candidate_id": "candidate_mingxue_five_element_balance_017_001",
            "material_id": "material_mingxue_golden_voice_pdf",
            "source_locator": "learning-reference:note_mingxue_golden_voice_001#lp_mingxue_five_element_balance_001; locator_requirement=page_or_section_required",
            "extracted_meaning": "Mingxue Golden Voice can support five-element terminology only after narrower locator review.",
            "short_quote": "",
            "proposed_rule_family": "five_element_balance",
            "risk_tier": "ordinary",
            "status": "pending_review",
            "proposed_limitations": [
                "Keep as terminology taxonomy until locator and chart context are reviewed.",
            ],
            "related_evidence_ids": [],
            "related_conflict_ids": [],
            "related_gap_ids": [],
            "duplicate_of": "",
            "created_by": "learning_reference_curation",
            "created_at": "2026-06-01",
        },
        {
            "candidate_id": "candidate_hongfu_remedy_boundary_017_001",
            "material_id": "material_fortune_reading_hongfu_qitian_pdf",
            "source_locator": "learning-reference:note_fortune_reading_hongfu_qitian_001#lp_hongfu_remedy_boundary_001; locator_requirement=page_or_section_required",
            "extracted_meaning": "Hongfu Qitian remedy-boundary material should stay conditional until locator and safety context are reviewed.",
            "short_quote": "",
            "proposed_rule_family": "remedy_boundary",
            "risk_tier": "sensitive",
            "status": "pending_review",
            "proposed_limitations": [
                "State uncertainty for remedy-boundary interpretation.",
                "Include limitation language; avoid certainty about effects.",
            ],
            "related_evidence_ids": [],
            "related_conflict_ids": [],
            "related_gap_ids": [],
            "duplicate_of": "",
            "created_by": "learning_reference_curation",
            "created_at": "2026-06-01",
        },
    ]


def _write_manual_application_materials(path: Path) -> None:
    _write_json(
        path / "source_materials.json",
        [
            {
                "material_id": material_id,
                "title": title,
                "material_type": "pdf",
                "file_label": file_label,
                "tracking_status": "external_untracked",
                "preparation_status": "indexed",
            }
            for material_id, title, file_label in [
                ("material_mingli_true_formula_teacher_pdf", "Mingli True Formula Teacher", "mingli-true-formula-teacher.pdf"),
                ("material_duan_plain_mingxue_outline_pdf", "Duan Plain Mingxue Outline", "duan-plain-mingxue-outline.pdf"),
                ("material_mingxue_golden_voice_pdf", "Mingxue Golden Voice", "mingxue-golden-voice.pdf"),
                ("material_fortune_reading_hongfu_qitian_pdf", "Fortune Reading Hongfu Qitian", "fortune-reading-hongfu-qitian.pdf"),
            ]
        ],
    )


def _write_manual_application_fixture(path: Path) -> None:
    """Seed a tmp_path with the four pending_review candidates."""
    _write_manual_application_materials(path)
    _write_json(path / "candidate_extracts.json", _manual_application_candidate_payloads())
    _write_json(path / "review_decisions.json", [])


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


def test_list_pending_candidate_review_worklist_surfaces_checked_in_pending_candidates(tmp_path):
    _write_manual_application_fixture(tmp_path)
    worklist = source_intake.list_pending_candidate_review_worklist(tmp_path)

    assert [item.candidate_id for item in worklist] == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert all(item.status == "pending_review" for item in worklist)
    assert all(
        {"verify_source_locator", "review_candidate_meaning", "decide_review_outcome"}
        <= set(item.required_review_actions)
        for item in worklist
    )

    actions_by_id = {
        item.candidate_id: set(item.required_review_actions) for item in worklist
    }
    for candidate_id in (
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ):
        assert (
            "replace_learning_reference_locator_with_source_locator"
            in actions_by_id[candidate_id]
        )
    assert (
        "confirm_uncertainty_and_limitation_language"
        in actions_by_id["candidate_mingli_pattern_strength_017_001"]
    )
    assert (
        "confirm_uncertainty_and_limitation_language"
        in actions_by_id["candidate_hongfu_remedy_boundary_017_001"]
    )


def test_list_pending_candidate_review_worklist_excludes_non_pending_candidates(
    tmp_path,
):
    candidates = [
        _candidate_payload("candidate_pending"),
        _candidate_payload("candidate_approved", status="approved"),
        _candidate_payload("candidate_rejected", status="rejected"),
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
                "reviewed_at": "2026-06-01",
                "rationale": "Locator and conditional wording are reviewable.",
                "required_changes": [],
                "rejection_reason": "",
                "approval_limitations": ["Keep the report wording conditional."],
                "source_quality": "review_note",
                "confidence": "moderate",
            },
            {
                "decision_id": "review_candidate_rejected",
                "candidate_id": "candidate_rejected",
                "decision": "rejected",
                "reviewer": "maintainer",
                "reviewed_at": "2026-06-01",
                "rationale": "The candidate duplicates already captured intake material.",
                "required_changes": [],
                "rejection_reason": (
                    "Rejected because this duplicate is already represented."
                ),
                "approval_limitations": [],
                "source_quality": "review_note",
                "confidence": "moderate",
            },
        ],
    )
    _write_json(tmp_path / "promotion_batches.json", [])

    worklist = source_intake.list_pending_candidate_review_worklist(tmp_path)

    assert [item.candidate_id for item in worklist] == ["candidate_pending"]
    assert worklist[0].required_review_actions == [
        "verify_source_locator",
        "review_candidate_meaning",
        "decide_review_outcome",
    ]


def test_list_pending_candidate_review_decision_packets_prepare_manual_review_inputs(tmp_path):
    _write_manual_application_fixture(tmp_path)
    packets = source_intake.list_pending_candidate_review_decision_packets(tmp_path)

    assert [packet.candidate_id for packet in packets] == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert all(packet.candidate_status == "pending_review" for packet in packets)
    assert all(
        packet.decision_options == ["approved", "returned", "rejected", "blocked"]
        for packet in packets
    )
    assert all(
        {
            "reviewer",
            "reviewed_at",
            "rationale",
            "source_quality",
            "confidence",
            "review_outcome",
            "approval_limitations_if_approved",
        }
        <= set(packet.required_review_inputs)
        for packet in packets
    )
    assert all(
        "Review decision packets are not formal report evidence."
        in packet.boundary_notes
        for packet in packets
    )

    packets_by_id = {packet.candidate_id: packet for packet in packets}
    assert (
        "uncertainty_limitations_not_confirmed"
        in packets_by_id[
            "candidate_mingli_pattern_strength_017_001"
        ].approval_blockers
    )
    for candidate_id in (
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ):
        packet = packets_by_id[candidate_id]
        assert "source_page_or_section_locator" in packet.required_review_inputs
        assert (
            "learning_reference_locator_not_replaced"
            in packet.approval_blockers
        )
    assert (
        "uncertainty_limitations_not_confirmed"
        in packets_by_id[
            "candidate_hongfu_remedy_boundary_017_001"
        ].approval_blockers
    )


def test_list_pending_candidate_review_decision_packets_exclude_non_pending_candidates(
    tmp_path,
):
    candidates = [
        _candidate_payload("candidate_pending"),
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
                "reviewed_at": "2026-06-01",
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
                "reviewed_at": "2026-06-01",
                "rationale": "The locator needs a narrower anchor.",
                "required_changes": ["Add a page or heading-level locator."],
                "rejection_reason": "",
                "approval_limitations": [],
                "source_quality": "review_note",
                "confidence": "weak",
            },
        ],
    )
    _write_json(tmp_path / "promotion_batches.json", [])

    packets = source_intake.list_pending_candidate_review_decision_packets(tmp_path)

    assert [packet.candidate_id for packet in packets] == ["candidate_pending"]
    assert packets[0].approval_blockers == [
        "source_locator_not_verified",
        "candidate_meaning_not_verified",
        "review_outcome_not_selected",
    ]


def test_build_pending_candidate_review_packet_summary_counts_blockers_and_inputs(tmp_path):
    _write_manual_application_fixture(tmp_path)
    summary = source_intake.build_pending_candidate_review_packet_summary(tmp_path)

    assert summary.packet_count == 4
    assert summary.candidate_ids == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert summary.decision_option_counts == {
        "approved": 4,
        "returned": 4,
        "rejected": 4,
        "blocked": 4,
    }
    assert summary.required_input_counts["reviewer"] == 4
    assert summary.required_input_counts["reviewed_at"] == 4
    assert summary.required_input_counts["source_page_or_section_locator"] == 4
    assert summary.required_input_counts["uncertainty_and_limitation_language"] == 2
    assert summary.approval_blocker_counts == {
        "source_locator_not_verified": 4,
        "candidate_meaning_not_verified": 4,
        "review_outcome_not_selected": 4,
        "uncertainty_limitations_not_confirmed": 2,
        "learning_reference_locator_not_replaced": 4,
    }
    assert summary.packet_action_counts["draft_review_decision_after_manual_checks"] == 4
    assert summary.review_decision_delta == 0
    assert summary.formal_evidence_delta == 0


def test_build_pending_candidate_review_packet_summary_handles_no_pending_candidates(
    tmp_path,
):
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
                "reviewed_at": "2026-06-01",
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
                "reviewed_at": "2026-06-01",
                "rationale": "The locator needs a narrower anchor.",
                "required_changes": ["Add a page or heading-level locator."],
                "rejection_reason": "",
                "approval_limitations": [],
                "source_quality": "review_note",
                "confidence": "weak",
            },
        ],
    )
    _write_json(tmp_path / "promotion_batches.json", [])

    summary = source_intake.build_pending_candidate_review_packet_summary(tmp_path)

    assert summary.packet_count == 0
    assert summary.candidate_ids == []
    assert summary.decision_option_counts == {}
    assert summary.required_input_counts == {}
    assert summary.approval_blocker_counts == {}
    assert summary.packet_action_counts == {}
    assert summary.review_decision_delta == 0
    assert summary.formal_evidence_delta == 0


def test_build_pending_candidate_review_action_queue_prioritizes_next_manual_steps(tmp_path):
    _write_manual_application_fixture(tmp_path)
    queue = source_intake.build_pending_candidate_review_action_queue(tmp_path)

    assert [item.candidate_id for item in queue] == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert [item.primary_action for item in queue] == [
        "replace_learning_reference_locator",
        "replace_learning_reference_locator",
        "replace_learning_reference_locator",
        "replace_learning_reference_locator",
    ]
    assert all(item.priority == "high" for item in queue)
    for item in queue:
        assert "source_page_or_section_locator" in item.blocking_inputs
    assert all(
        "Action queue items are planning metadata only." in item.boundary_notes
        for item in queue
    )
    assert queue[1].reason == (
        "Replace the learning-reference locator with a source page, section, "
        "or review-note anchor before approval can be considered."
    )


def test_build_pending_candidate_review_action_queue_handles_no_pending_candidates(
    tmp_path,
):
    candidates = [_candidate_payload("candidate_approved", status="approved")]
    _write_candidate_extracts(tmp_path, candidates)
    _write_json(
        tmp_path / "review_decisions.json",
        [
            {
                "decision_id": "review_candidate_approved",
                "candidate_id": "candidate_approved",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-06-01",
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

    assert source_intake.build_pending_candidate_review_action_queue(tmp_path) == []


def test_render_pending_candidate_review_action_queue_markdown_lists_summary_and_tasks(tmp_path):
    _write_manual_application_fixture(tmp_path)
    markdown = source_intake.render_pending_candidate_review_action_queue_markdown(tmp_path)

    assert markdown.startswith("# Pending Candidate Review Action Queue\n")
    assert "- Queue items: `4`" in markdown
    assert "- Review decision delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "## Action Items" in markdown
    assert markdown.count("- [ ] Candidate: `") == 4
    for candidate_id in (
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ):
        assert f"- [ ] Candidate: `{candidate_id}`" in markdown
    assert markdown.count("Primary action: `replace_learning_reference_locator`") == 4
    assert "Action queue items are planning metadata only." in markdown
    assert "Action queue items do not write review decisions or formal evidence." in markdown


def test_render_pending_candidate_review_action_queue_markdown_handles_empty_queue(
    tmp_path,
):
    candidates = [_candidate_payload("candidate_approved", status="approved")]
    _write_candidate_extracts(tmp_path, candidates)
    _write_json(
        tmp_path / "review_decisions.json",
        [
            {
                "decision_id": "review_candidate_approved",
                "candidate_id": "candidate_approved",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-06-01",
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

    markdown = source_intake.render_pending_candidate_review_action_queue_markdown(
        tmp_path
    )

    assert "- Queue items: `0`" in markdown
    assert "No pending candidate review actions." in markdown


def test_list_pending_candidate_review_input_templates_prepare_fillable_fields(tmp_path):
    _write_manual_application_fixture(tmp_path)
    templates = source_intake.list_pending_candidate_review_input_templates(tmp_path)

    assert [template.candidate_id for template in templates] == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert all(template.candidate_status == "pending_review" for template in templates)
    assert all(
        template.base_fields == [
            "reviewer",
            "reviewed_at",
            "source_locator",
            "source_quality",
            "confidence",
            "review_outcome",
            "rationale",
        ]
        for template in templates
    )
    assert all(
        template.outcome_fields == {
            "approved": ["approval_limitations"],
            "returned": ["required_changes"],
            "rejected": ["rejection_reason"],
            "blocked": ["rejection_reason"],
        }
        for template in templates
    )
    assert all(
        "Input templates are not review decisions." in template.boundary_notes
        for template in templates
    )
    assert all(
        "Input templates do not write review_decisions.json or formal evidence."
        in template.boundary_notes
        for template in templates
    )

    templates_by_id = {template.candidate_id: template for template in templates}
    mingli = templates_by_id["candidate_mingli_pattern_strength_017_001"]
    assert (
        mingli.decision_id_hint
        == "review_candidate_mingli_pattern_strength_017_001"
    )
    assert mingli.current_source_locator
    assert "uncertainty_and_limitation_language" in mingli.conditional_fields
    assert "uncertainty_and_limitation_language" in mingli.blocking_inputs

    for candidate_id in (
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ):
        template = templates_by_id[candidate_id]
        assert "source_page_or_section_locator" in template.conditional_fields
        assert "source_page_or_section_locator" in template.blocking_inputs


def test_render_pending_candidate_review_input_templates_markdown_lists_fields(tmp_path):
    _write_manual_application_fixture(tmp_path)
    markdown = source_intake.render_pending_candidate_review_input_templates_markdown(tmp_path)

    assert markdown.startswith("# Pending Candidate Review Input Templates\n")
    assert "- Template count: `4`" in markdown
    assert "- Review decision delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "## Templates" in markdown
    assert markdown.count("- [ ] Candidate: `") == 4
    assert (
        "- [ ] Candidate: `candidate_mingli_pattern_strength_017_001`\n"
        "  - Decision id hint: `review_candidate_mingli_pattern_strength_017_001`"
    ) in markdown
    for field_name in (
        "reviewer:",
        "reviewed_at:",
        "source_locator:",
        "source_quality:",
        "confidence:",
        "review_outcome:",
        "rationale:",
        "approval_limitations:",
        "required_changes:",
        "rejection_reason:",
        "source_page_or_section_locator:",
        "uncertainty_and_limitation_language:",
    ):
        assert field_name in markdown
    assert "Input templates are not review decisions." in markdown
    assert "Input templates do not write review_decisions.json or formal evidence." in markdown


def test_pending_candidate_review_input_templates_handle_empty_queue(tmp_path):
    candidates = [_candidate_payload("candidate_approved", status="approved")]
    _write_candidate_extracts(tmp_path, candidates)
    _write_json(
        tmp_path / "review_decisions.json",
        [
            {
                "decision_id": "review_candidate_approved",
                "candidate_id": "candidate_approved",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-06-01",
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

    templates = source_intake.list_pending_candidate_review_input_templates(tmp_path)
    markdown = source_intake.render_pending_candidate_review_input_templates_markdown(
        tmp_path
    )

    assert templates == []
    assert "- Template count: `0`" in markdown
    assert "No pending candidate review input templates." in markdown


def test_validate_pending_candidate_review_decision_draft_accepts_complete_approval(tmp_path):
    _write_manual_application_fixture(tmp_path)
    draft = {
        "decision_id": "review_candidate_hongfu_remedy_boundary_017_001",
        "candidate_id": "candidate_hongfu_remedy_boundary_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "source:hongfu-qitian#section-remedy-boundary",
        "source_page_or_section_locator": "source:hongfu-qitian#section-remedy-boundary",
        "source_quality": "review_note",
        "confidence": "moderate",
        "rationale": "Locator and conditional safety language are reviewable.",
        "approval_limitations": [
            "Use only as conditional traditional remedy-boundary context."
        ],
        "uncertainty_and_limitation_language": (
            "Frame as uncertain traditional context, not guaranteed effect."
        ),
        "required_changes": [],
        "rejection_reason": "",
    }

    result = source_intake.validate_pending_candidate_review_decision_draft(draft, tmp_path)

    assert result.ready_for_manual_application is True
    assert result.candidate_id == "candidate_hongfu_remedy_boundary_017_001"
    assert result.decision_id == "review_candidate_hongfu_remedy_boundary_017_001"
    assert result.review_outcome == "approved"
    assert result.missing_fields == []
    assert result.blocking_issues == []
    assert result.normalized_review_decision == {
        "decision_id": "review_candidate_hongfu_remedy_boundary_017_001",
        "candidate_id": "candidate_hongfu_remedy_boundary_017_001",
        "decision": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "rationale": "Locator and conditional safety language are reviewable.",
        "required_changes": [],
        "rejection_reason": "",
        "approval_limitations": [
            "Use only as conditional traditional remedy-boundary context."
        ],
        "source_quality": "review_note",
        "confidence": "moderate",
    }
    assert result.review_decision_delta == 0
    assert result.formal_evidence_delta == 0
    assert (
        "Draft validation does not write review_decisions.json."
        in result.boundary_notes
    )


def test_validate_pending_candidate_review_decision_draft_blocks_unresolved_approval(tmp_path):
    _write_manual_application_fixture(tmp_path)
    draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    result = source_intake.validate_pending_candidate_review_decision_draft(draft, tmp_path)

    assert result.ready_for_manual_application is False
    assert result.normalized_review_decision == {}
    assert result.missing_fields == [
        "approval_limitations",
        "source_page_or_section_locator",
        "uncertainty_and_limitation_language",
    ]
    assert result.blocking_issues == [
        "approved_candidate_requires_approval_limitations",
        "source_page_or_section_locator_required",
        "uncertainty_and_limitation_language_required",
        "approved_candidate_source_locator_still_learning_reference",
        "approved_candidate_cannot_use_needs_recheck",
    ]
    assert result.review_decision_delta == 0
    assert result.formal_evidence_delta == 0


def test_render_pending_candidate_review_draft_validation_markdown_summarizes_results(tmp_path):
    _write_manual_application_fixture(tmp_path)
    valid_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_northeast_blind_image_001",
        "candidate_id": "candidate_northeast_blind_image_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "review-note:northeast_blind_peak.md#blind-image-method",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks duplicate and safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
        "duplicate_or_reuse_resolution": "",
    }

    markdown = source_intake.render_pending_candidate_review_draft_validation_markdown(
        [valid_draft, blocked_draft], tmp_path)

    assert markdown.startswith("# Pending Candidate Review Draft Validation\n")
    assert "- Draft count: `2`" in markdown
    assert "- Ready for manual application: `1`" in markdown
    assert "- Blocked drafts: `1`" in markdown
    assert "- Review decision delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "Candidate: `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "Status: `ready_for_manual_application`" in markdown
    assert "Candidate: `candidate_northeast_blind_image_001`" in markdown
    assert "approved_candidate_cannot_use_needs_recheck" in markdown
    assert "Draft validation does not write review_decisions.json." in markdown


def test_build_pending_candidate_review_application_guard_previews_ready_draft(tmp_path):
    _write_manual_application_fixture(tmp_path)
    draft = {
        "decision_id": "review_candidate_hongfu_remedy_boundary_017_001",
        "candidate_id": "candidate_hongfu_remedy_boundary_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "source:hongfu-qitian#section-remedy-boundary",
        "source_page_or_section_locator": "source:hongfu-qitian#section-remedy-boundary",
        "source_quality": "review_note",
        "confidence": "moderate",
        "rationale": "Locator and conditional safety language are reviewable.",
        "approval_limitations": [
            "Use only as conditional traditional remedy-boundary context."
        ],
        "uncertainty_and_limitation_language": (
            "Frame as uncertain traditional context, not guaranteed effect."
        ),
        "required_changes": [],
        "rejection_reason": "",
    }

    guards = source_intake.build_pending_candidate_review_application_guard([draft], tmp_path)

    assert len(guards) == 1
    guard = guards[0]
    assert guard.ready_to_apply is True
    assert guard.candidate_id == "candidate_hongfu_remedy_boundary_017_001"
    assert guard.current_candidate_status == "pending_review"
    assert guard.next_candidate_status == "approved"
    assert guard.review_decision_preview["decision"] == "approved"
    assert guard.candidate_status_preview == {
        "candidate_id": "candidate_hongfu_remedy_boundary_017_001",
        "from_status": "pending_review",
        "to_status": "approved",
    }
    assert guard.preview_review_decision_delta == 1
    assert guard.preview_candidate_status_delta == 1
    assert guard.applied_review_decision_delta == 0
    assert guard.applied_candidate_status_delta == 0
    assert guard.formal_evidence_delta == 0
    assert guard.blocking_issues == []
    assert (
        "Application guard previews manual changes only."
        in guard.boundary_notes
    )


def test_build_pending_candidate_review_application_guard_blocks_invalid_draft(tmp_path):
    _write_manual_application_fixture(tmp_path)
    draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    guard = source_intake.build_pending_candidate_review_application_guard([draft], tmp_path)[0]

    assert guard.ready_to_apply is False
    assert guard.review_decision_preview == {}
    assert guard.candidate_status_preview == {}
    assert guard.preview_review_decision_delta == 0
    assert guard.preview_candidate_status_delta == 0
    assert guard.applied_review_decision_delta == 0
    assert guard.applied_candidate_status_delta == 0
    assert guard.formal_evidence_delta == 0
    assert guard.validation_missing_fields == [
        "approval_limitations",
        "source_page_or_section_locator",
        "uncertainty_and_limitation_language",
    ]
    assert "approved_candidate_cannot_use_needs_recheck" in guard.blocking_issues


def test_render_pending_candidate_review_application_guard_markdown_lists_preview(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_northeast_blind_image_001",
        "candidate_id": "candidate_northeast_blind_image_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "review-note:northeast_blind_peak.md#blind-image-method",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks duplicate and safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
        "duplicate_or_reuse_resolution": "",
    }

    markdown = source_intake.render_pending_candidate_review_application_guard_markdown(
        [ready_draft, blocked_draft], tmp_path)

    assert markdown.startswith("# Pending Candidate Review Application Guard\n")
    assert "- Draft count: `2`" in markdown
    assert "- Ready previews: `1`" in markdown
    assert "- Blocked previews: `1`" in markdown
    assert "- Preview review decision additions: `1`" in markdown
    assert "- Preview candidate status updates: `1`" in markdown
    assert "- Applied review decision delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "Candidate: `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "Candidate status preview: `pending_review` -> `returned`" in markdown
    assert "Candidate: `candidate_northeast_blind_image_001`" in markdown
    assert "Status: `blocked`" in markdown
    assert "Application guard previews manual changes only." in markdown


def test_build_pending_candidate_review_application_packets_exports_ready_snippets(tmp_path):
    _write_manual_application_fixture(tmp_path)
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packets = source_intake.build_pending_candidate_review_application_packets([draft], tmp_path)

    assert len(packets) == 1
    packet = packets[0]
    assert packet.ready_to_export is True
    assert packet.candidate_id == "candidate_duan_ten_god_relation_017_001"
    assert packet.review_decision_json["decision"] == "returned"
    assert packet.candidate_status_update == {
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "from_status": "pending_review",
        "to_status": "returned",
    }
    assert packet.manual_checklist == [
        "append_review_decision_entry",
        "update_candidate_status",
        "run_source_intake_tests",
        "verify_formal_evidence_delta_zero",
    ]
    assert packet.rollback_notes == [
        "Remove the appended review decision entry if manual application is abandoned.",
        "Restore candidate status from returned to pending_review if manual application is abandoned.",
    ]
    assert packet.preview_review_decision_delta == 1
    assert packet.preview_candidate_status_delta == 1
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert (
        "Application packets are export-only manual instructions."
        in packet.boundary_notes
    )


def test_build_pending_candidate_review_application_packets_blocks_invalid_preview():
    draft = {
        "decision_id": "review_candidate_northeast_blind_image_001",
        "candidate_id": "candidate_northeast_blind_image_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "review-note:northeast_blind_peak.md#blind-image-method",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks duplicate and safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
        "duplicate_or_reuse_resolution": "",
    }

    packet = source_intake.build_pending_candidate_review_application_packets([draft])[0]

    assert packet.ready_to_export is False
    assert packet.review_decision_json == {}
    assert packet.candidate_status_update == {}
    assert packet.manual_checklist == [
        "resolve_blocking_issues_before_manual_export"
    ]
    assert "approved_candidate_cannot_use_needs_recheck" in packet.blocking_issues
    assert packet.preview_review_decision_delta == 0
    assert packet.preview_candidate_status_delta == 0
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_render_pending_candidate_review_application_packets_markdown_exports_json(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_northeast_blind_image_001",
        "candidate_id": "candidate_northeast_blind_image_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "review-note:northeast_blind_peak.md#blind-image-method",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks duplicate and safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
        "duplicate_or_reuse_resolution": "",
    }

    markdown = source_intake.render_pending_candidate_review_application_packets_markdown(
        [ready_draft, blocked_draft], tmp_path)

    assert markdown.startswith("# Pending Candidate Review Application Packets\n")
    assert "- Packet count: `2`" in markdown
    assert "- Exportable packets: `1`" in markdown
    assert "- Blocked packets: `1`" in markdown
    assert "- Preview review decision additions: `1`" in markdown
    assert "- Applied review decision delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "Candidate: `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "```json" in markdown
    assert '"decision": "returned"' in markdown
    assert '"to_status": "returned"' in markdown
    assert "Manual checklist" in markdown
    assert "Rollback notes" in markdown
    assert "Candidate: `candidate_northeast_blind_image_001`" in markdown
    assert "approved_candidate_cannot_use_needs_recheck" in markdown
    assert "Application packets are export-only manual instructions." in markdown


def test_build_pending_candidate_review_application_audit_summary_counts_layers(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    summary = source_intake.build_pending_candidate_review_application_audit_summary(
        [ready_draft, blocked_draft], tmp_path)

    assert summary.pending_template_count == 4
    assert summary.draft_count == 2
    assert summary.validation_ready_count == 1
    assert summary.validation_blocked_count == 1
    assert summary.guard_ready_count == 1
    assert summary.packet_exportable_count == 1
    assert summary.packet_blocked_count == 1
    assert summary.exportable_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert summary.blocked_candidate_ids == ["candidate_mingli_pattern_strength_017_001"]
    assert summary.missing_draft_candidate_ids == [
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert summary.candidate_next_actions[
        "candidate_duan_ten_god_relation_017_001"
    ] == "apply_manual_application_packet"
    assert summary.candidate_next_actions[
        "candidate_mingli_pattern_strength_017_001"
    ] == "resolve_draft_blocking_issues"
    assert summary.candidate_next_actions[
        "candidate_hongfu_remedy_boundary_017_001"
    ] == "fill_review_input_template"
    assert summary.preview_review_decision_delta == 1
    assert summary.preview_candidate_status_delta == 1
    assert summary.applied_review_decision_delta == 0
    assert summary.applied_candidate_status_delta == 0
    assert summary.formal_evidence_delta == 0
    assert (
        "Audit summary is read-only planning metadata."
        in summary.boundary_notes
    )


def test_render_pending_candidate_review_application_audit_summary_markdown(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    markdown = (
        source_intake.render_pending_candidate_review_application_audit_summary_markdown(
            [ready_draft, blocked_draft], tmp_path)
    )

    assert markdown.startswith("# Pending Candidate Review Application Audit Summary\n")
    assert "- Pending templates: `4`" in markdown
    assert "- Drafts supplied: `2`" in markdown
    assert "- Exportable application packets: `1`" in markdown
    assert "- Blocked application packets: `1`" in markdown
    assert "- Missing draft candidates: `2`" in markdown
    assert "- Applied review decision delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "## Exportable Candidates" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`: `apply_manual_application_packet`" in markdown
    assert "## Blocked Candidates" in markdown
    assert "`candidate_mingli_pattern_strength_017_001`: `resolve_draft_blocking_issues`" in markdown
    assert "## Missing Draft Candidates" in markdown
    assert "`candidate_hongfu_remedy_boundary_017_001`: `fill_review_input_template`" in markdown
    assert "Audit summary is read-only planning metadata." in markdown


def test_pending_candidate_review_application_audit_summary_handles_no_drafts(tmp_path):
    _write_manual_application_fixture(tmp_path)
    summary = source_intake.build_pending_candidate_review_application_audit_summary([], tmp_path)

    assert summary.pending_template_count == 4
    assert summary.draft_count == 0
    assert summary.packet_exportable_count == 0
    assert summary.packet_blocked_count == 0
    assert summary.missing_draft_candidate_ids == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert set(summary.candidate_next_actions.values()) == {
        "fill_review_input_template"
    }
    assert summary.applied_review_decision_delta == 0
    assert summary.formal_evidence_delta == 0


def test_build_pending_candidate_review_manual_action_dashboard_groups_shortest_actions(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    dashboard = source_intake.build_pending_candidate_review_manual_action_dashboard(
        [ready_draft, blocked_draft], tmp_path)

    assert dashboard.pending_candidate_count == 4
    assert dashboard.action_counts == {
        "apply_manual_application_packet": 1,
        "resolve_draft_blocking_issues": 1,
        "fill_review_input_template": 2,
    }
    assert dashboard.candidates_by_action == {
        "apply_manual_application_packet": [
            "candidate_duan_ten_god_relation_017_001"
        ],
        "resolve_draft_blocking_issues": [
            "candidate_mingli_pattern_strength_017_001"
        ],
        "fill_review_input_template": [
            "candidate_mingxue_five_element_balance_017_001",
            "candidate_hongfu_remedy_boundary_017_001",
        ],
    }
    assert dashboard.recommended_action_sequence == [
        "apply_manual_application_packet",
        "resolve_draft_blocking_issues",
        "fill_review_input_template",
    ]
    assert dashboard.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert dashboard.preview_review_decision_delta == 1
    assert dashboard.preview_candidate_status_delta == 1
    assert dashboard.applied_review_decision_delta == 0
    assert dashboard.applied_candidate_status_delta == 0
    assert dashboard.formal_evidence_delta == 0
    assert (
        "Manual action dashboard is read-only planning metadata."
        in dashboard.boundary_notes
    )


def test_render_pending_candidate_review_manual_action_dashboard_markdown(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    markdown = source_intake.render_pending_candidate_review_manual_action_dashboard_markdown(
        [ready_draft, blocked_draft], tmp_path)

    assert markdown.startswith("# Pending Candidate Review Manual Action Dashboard\n")
    assert "- Pending candidates: `4`" in markdown
    assert "- `apply_manual_application_packet`: `1`" in markdown
    assert "- `resolve_draft_blocking_issues`: `1`" in markdown
    assert "- `fill_review_input_template`: `2`" in markdown
    assert "- Applied review decision delta: `0`" in markdown
    assert "- Applied candidate status delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "## Candidates By Action" in markdown
    assert "### apply_manual_application_packet" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`" in markdown
    assert "### resolve_draft_blocking_issues" in markdown
    assert "`candidate_mingli_pattern_strength_017_001`" in markdown
    assert "### fill_review_input_template" in markdown
    assert "`candidate_hongfu_remedy_boundary_017_001`" in markdown
    assert "## Recommended Processing Order" in markdown
    assert (
        "1. `candidate_duan_ten_god_relation_017_001`: "
        "`apply_manual_application_packet`"
    ) in markdown
    assert (
        "2. `candidate_mingli_pattern_strength_017_001`: "
        "`resolve_draft_blocking_issues`"
    ) in markdown
    assert (
        "4. `candidate_hongfu_remedy_boundary_017_001`: "
        "`fill_review_input_template`"
    ) in markdown
    assert "Manual action dashboard is read-only planning metadata." in markdown


def test_pending_candidate_review_manual_action_dashboard_handles_no_drafts(tmp_path):
    _write_manual_application_fixture(tmp_path)
    dashboard = source_intake.build_pending_candidate_review_manual_action_dashboard([], tmp_path)

    assert dashboard.action_counts == {
        "apply_manual_application_packet": 0,
        "resolve_draft_blocking_issues": 0,
        "fill_review_input_template": 4,
    }
    assert dashboard.candidates_by_action["fill_review_input_template"] == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert dashboard.recommended_processing_order == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert dashboard.applied_review_decision_delta == 0
    assert dashboard.applied_candidate_status_delta == 0
    assert dashboard.formal_evidence_delta == 0


def test_build_pending_candidate_review_manual_application_dry_run_guide_lists_steps(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    guide = source_intake.build_pending_candidate_review_manual_application_dry_run_guide(
        [ready_draft, blocked_draft], tmp_path)

    assert guide.pending_candidate_count == 4
    assert guide.step_count == 4
    assert guide.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]

    steps_by_id = {step.candidate_id: step for step in guide.steps}
    ready_step = steps_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_step.action == "apply_manual_application_packet"
    assert ready_step.dry_run_status == "ready_for_manual_application"
    assert ready_step.manual_steps == [
        "append_review_decision_entry",
        "update_candidate_status",
    ]
    assert ready_step.ready_criteria == [
        "application_packet_ready_to_export",
        "review_decision_json_available",
        "candidate_status_update_available",
    ]
    assert ready_step.post_apply_checks == [
        "run_source_intake_tests",
        "verify_formal_evidence_delta_zero",
    ]
    assert ready_step.rollback_notes == [
        "Remove the appended review decision entry if manual application is abandoned.",
        "Restore candidate status from returned to pending_review if manual application is abandoned.",
    ]

    blocked_step = steps_by_id["candidate_mingli_pattern_strength_017_001"]
    assert blocked_step.action == "resolve_draft_blocking_issues"
    assert blocked_step.dry_run_status == "blocked_until_draft_issues_resolved"
    assert blocked_step.required_inputs == [
        "approval_limitations",
        "source_page_or_section_locator",
        "uncertainty_and_limitation_language",
    ]
    assert "approved_candidate_cannot_use_needs_recheck" in blocked_step.blocking_issues
    assert blocked_step.manual_steps == [
        "resolve_draft_blocking_issues",
        "rerun_draft_validation",
        "rerun_application_guard",
    ]

    missing_step = steps_by_id["candidate_hongfu_remedy_boundary_017_001"]
    assert missing_step.action == "fill_review_input_template"
    assert missing_step.dry_run_status == "needs_review_input_template"
    assert missing_step.required_inputs == [
        "reviewer",
        "reviewed_at",
        "source_locator",
        "source_quality",
        "confidence",
        "review_outcome",
        "rationale",
        "source_page_or_section_locator",
        "uncertainty_and_limitation_language",
    ]
    assert missing_step.manual_steps == [
        "fill_review_input_template",
        "run_draft_validation",
        "run_application_guard",
    ]
    assert guide.preview_review_decision_delta == 1
    assert guide.preview_candidate_status_delta == 1
    assert guide.applied_review_decision_delta == 0
    assert guide.applied_candidate_status_delta == 0
    assert guide.formal_evidence_delta == 0
    assert (
        "Manual application dry-run guide is read-only planning metadata."
        in guide.boundary_notes
    )


def test_render_pending_candidate_review_manual_application_dry_run_guide_markdown(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    markdown = (
        source_intake.render_pending_candidate_review_manual_application_dry_run_guide_markdown(
            [ready_draft, blocked_draft], tmp_path)
    )

    assert markdown.startswith("# Pending Candidate Review Manual Application Dry-Run Guide\n")
    assert "- Pending candidates: `4`" in markdown
    assert "- Dry-run steps: `4`" in markdown
    assert "- Applied review decision delta: `0`" in markdown
    assert "- Applied candidate status delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "## Dry-Run Steps" in markdown
    assert "Candidate: `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "Status: `ready_for_manual_application`" in markdown
    assert "append_review_decision_entry" in markdown
    assert "verify_formal_evidence_delta_zero" in markdown
    assert "Candidate: `candidate_mingli_pattern_strength_017_001`" in markdown
    assert "Status: `blocked_until_draft_issues_resolved`" in markdown
    assert "approved_candidate_cannot_use_needs_recheck" in markdown
    assert "Candidate: `candidate_hongfu_remedy_boundary_017_001`" in markdown
    assert "Status: `needs_review_input_template`" in markdown
    assert "source_page_or_section_locator" in markdown
    assert "## Recommended Processing Order" in markdown
    assert (
        "1. `candidate_duan_ten_god_relation_017_001`: "
        "`apply_manual_application_packet`"
    ) in markdown
    assert "Manual application dry-run guide is read-only planning metadata." in markdown


def test_pending_candidate_review_manual_application_dry_run_guide_handles_no_drafts(tmp_path):
    _write_manual_application_fixture(tmp_path)
    guide = source_intake.build_pending_candidate_review_manual_application_dry_run_guide(
        [], tmp_path)

    assert guide.pending_candidate_count == 4
    assert guide.step_count == 4
    assert guide.recommended_processing_order == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert {step.dry_run_status for step in guide.steps} == {
        "needs_review_input_template"
    }
    assert all(step.action == "fill_review_input_template" for step in guide.steps)
    assert guide.applied_review_decision_delta == 0
    assert guide.applied_candidate_status_delta == 0
    assert guide.formal_evidence_delta == 0


def test_build_pending_candidate_review_manual_application_preflight_report_checks_ready_packet(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    report = (
        source_intake.build_pending_candidate_review_manual_application_preflight_report(
            [ready_draft, blocked_draft], tmp_path)
    )

    assert report.pending_candidate_count == 4
    assert report.preflight_check_count == 4
    assert report.ready_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert "candidate_mingli_pattern_strength_017_001" in report.blocked_candidate_ids
    assert "candidate_hongfu_remedy_boundary_017_001" in report.blocked_candidate_ids

    checks_by_id = {check.candidate_id: check for check in report.checks}
    ready_check = checks_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_check.decision_id == "review_candidate_duan_ten_god_relation_017_001"
    assert ready_check.ready_for_manual_application is True
    assert ready_check.decision_id_unique is True
    assert ready_check.candidate_status_patch_matches_pending is True
    assert ready_check.packet_delta_matches_preview is True
    assert ready_check.expected_review_decision_delta == 1
    assert ready_check.expected_candidate_status_delta == 1
    assert ready_check.expected_candidate_status_update == {
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "from_status": "pending_review",
        "to_status": "returned",
    }
    assert ready_check.preflight_blockers == []

    blocked_check = checks_by_id["candidate_mingli_pattern_strength_017_001"]
    assert blocked_check.ready_for_manual_application is False
    assert "manual_application_packet_not_exportable" in blocked_check.preflight_blockers
    assert (
        "approved_candidate_cannot_use_needs_recheck"
        in blocked_check.preflight_blockers
    )

    missing_check = checks_by_id["candidate_hongfu_remedy_boundary_017_001"]
    assert missing_check.ready_for_manual_application is False
    assert "manual_application_packet_missing" in missing_check.preflight_blockers
    assert report.preview_review_decision_delta == 1
    assert report.preview_candidate_status_delta == 1
    assert report.applied_review_decision_delta == 0
    assert report.applied_candidate_status_delta == 0
    assert report.formal_evidence_delta == 0


def test_build_pending_candidate_review_manual_application_preflight_report_blocks_duplicate_decision_id(tmp_path):
    _write_manual_application_fixture(tmp_path)
    duan_draft = {
        "decision_id": "review_duplicate_pending_manual_decision",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    mingxue_draft = {
        "decision_id": "review_duplicate_pending_manual_decision",
        "candidate_id": "candidate_mingxue_five_element_balance_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingxue_golden_voice_001#lp_mingxue_five_element_balance_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    report = (
        source_intake.build_pending_candidate_review_manual_application_preflight_report(
            [duan_draft, mingxue_draft], tmp_path)
    )

    checks_by_id = {check.candidate_id: check for check in report.checks}
    for candidate_id in (
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
    ):
        check = checks_by_id[candidate_id]
        assert check.ready_for_manual_application is False
        assert check.decision_id_unique is False
        assert "review_decision_id_not_unique" in check.preflight_blockers
    assert report.ready_candidate_ids == []
    assert report.preview_review_decision_delta == 0
    assert report.preview_candidate_status_delta == 0
    assert report.applied_review_decision_delta == 0
    assert report.formal_evidence_delta == 0


def test_render_pending_candidate_review_manual_application_preflight_report_markdown(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    markdown = source_intake.render_pending_candidate_review_manual_application_preflight_report_markdown(
        [ready_draft, blocked_draft], tmp_path)

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Preflight Report\n"
    )
    assert "- Pending candidates: `4`" in markdown
    assert "- Preflight checks: `4`" in markdown
    assert "- Ready candidates: `1`" in markdown
    assert "- Blocked candidates: `3`" in markdown
    assert "- Applied review decision delta: `0`" in markdown
    assert "- Applied candidate status delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "## Ready Candidates" in markdown
    assert "- `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "decision_id_unique=`True`" in markdown
    assert "candidate_status_patch_matches_pending=`True`" in markdown
    assert "packet_delta_matches_preview=`True`" in markdown
    assert "## Blocked Candidates" in markdown
    assert "manual_application_packet_not_exportable" in markdown
    assert "manual_application_packet_missing" in markdown
    assert "Manual application preflight report is read-only planning metadata." in markdown


def test_pending_candidate_review_manual_application_preflight_report_handles_no_drafts(tmp_path):
    _write_manual_application_fixture(tmp_path)
    report = (
        source_intake.build_pending_candidate_review_manual_application_preflight_report(
            [], tmp_path)
    )

    assert report.pending_candidate_count == 4
    assert report.preflight_check_count == 4
    assert report.ready_candidate_ids == []
    assert report.blocked_candidate_ids == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert all(
        "manual_application_packet_missing" in check.preflight_blockers
        for check in report.checks
    )
    assert report.applied_review_decision_delta == 0
    assert report.applied_candidate_status_delta == 0
    assert report.formal_evidence_delta == 0


def test_build_pending_candidate_review_manual_application_handoff_summary_groups_execution_lanes(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    summary = (
        source_intake.build_pending_candidate_review_manual_application_handoff_summary(
            [ready_draft, blocked_draft], tmp_path)
    )

    assert summary.pending_candidate_count == 4
    assert summary.handoff_item_count == 4
    assert summary.ready_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert summary.blocked_candidate_ids == ["candidate_mingli_pattern_strength_017_001"]
    assert summary.missing_draft_candidate_ids == [
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert summary.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]

    items_by_id = {item.candidate_id: item for item in summary.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.action == "apply_manual_application_packet"
    assert ready_item.readiness_status == "ready_for_manual_application"
    assert ready_item.shortest_next_action == "apply_manual_application_packet"
    assert ready_item.manual_steps == [
        "append_review_decision_entry",
        "update_candidate_status",
    ]
    assert ready_item.preflight_checks == [
        "decision_id_unique",
        "candidate_status_patch_matches_pending",
        "packet_delta_matches_preview",
    ]
    assert ready_item.post_apply_checks == [
        "run_source_intake_tests",
        "verify_formal_evidence_delta_zero",
    ]
    assert ready_item.expected_candidate_status_update == {
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "from_status": "pending_review",
        "to_status": "returned",
    }
    assert ready_item.blocking_issues == []

    blocked_item = items_by_id["candidate_mingli_pattern_strength_017_001"]
    assert blocked_item.action == "resolve_draft_blocking_issues"
    assert blocked_item.readiness_status == "blocked_until_draft_issues_resolved"
    assert blocked_item.shortest_next_action == "resolve_draft_blocking_issues"
    assert "manual_application_packet_not_exportable" in blocked_item.blocking_issues
    assert "approved_candidate_cannot_use_needs_recheck" in blocked_item.blocking_issues

    missing_item = items_by_id["candidate_hongfu_remedy_boundary_017_001"]
    assert missing_item.action == "fill_review_input_template"
    assert missing_item.readiness_status == "needs_review_input_template"
    assert missing_item.shortest_next_action == "fill_review_input_template"
    assert "manual_application_packet_missing" in missing_item.blocking_issues
    assert "source_page_or_section_locator" in missing_item.required_inputs
    assert summary.preview_review_decision_delta == 1
    assert summary.preview_candidate_status_delta == 1
    assert summary.applied_review_decision_delta == 0
    assert summary.applied_candidate_status_delta == 0
    assert summary.formal_evidence_delta == 0
    assert (
        "Manual application handoff summary is read-only planning metadata."
        in summary.boundary_notes
    )


def test_render_pending_candidate_review_manual_application_handoff_summary_markdown(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    markdown = source_intake.render_pending_candidate_review_manual_application_handoff_summary_markdown(
        [ready_draft, blocked_draft], tmp_path)

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Handoff Summary\n"
    )
    assert "- Pending candidates: `4`" in markdown
    assert "- Ready candidates: `1`" in markdown
    assert "- Blocked candidates: `1`" in markdown
    assert "- Missing draft candidates: `2`" in markdown
    assert "- Applied review decision delta: `0`" in markdown
    assert "- Applied candidate status delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "## Ready Candidates" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`: `apply_manual_application_packet`" in markdown
    assert "decision_id_unique" in markdown
    assert "candidate_status_patch_matches_pending" in markdown
    assert "packet_delta_matches_preview" in markdown
    assert "## Blocked Candidates" in markdown
    assert "manual_application_packet_not_exportable" in markdown
    assert "## Missing Draft Candidates" in markdown
    assert "source_page_or_section_locator" in markdown
    assert "## Recommended Processing Order" in markdown
    assert (
        "1. `candidate_duan_ten_god_relation_017_001`: "
        "`apply_manual_application_packet`"
    ) in markdown
    assert "Manual application handoff summary is read-only planning metadata." in markdown


def test_pending_candidate_review_manual_application_handoff_summary_handles_no_drafts(tmp_path):
    _write_manual_application_fixture(tmp_path)
    summary = (
        source_intake.build_pending_candidate_review_manual_application_handoff_summary(
            [], tmp_path)
    )

    assert summary.pending_candidate_count == 4
    assert summary.handoff_item_count == 4
    assert summary.ready_candidate_ids == []
    assert summary.blocked_candidate_ids == []
    assert summary.missing_draft_candidate_ids == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert all(item.action == "fill_review_input_template" for item in summary.items)
    assert all(
        "manual_application_packet_missing" in item.blocking_issues
        for item in summary.items
    )
    assert summary.applied_review_decision_delta == 0
    assert summary.applied_candidate_status_delta == 0
    assert summary.formal_evidence_delta == 0


def test_build_pending_candidate_review_manual_application_readiness_ledger_lists_checkboxes(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    ledger = (
        source_intake.build_pending_candidate_review_manual_application_readiness_ledger(
            [ready_draft, blocked_draft], tmp_path)
    )

    assert ledger.pending_candidate_count == 4
    assert ledger.ledger_row_count == 4
    assert ledger.ready_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert ledger.blocked_candidate_ids == ["candidate_mingli_pattern_strength_017_001"]
    assert ledger.missing_draft_candidate_ids == [
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert ledger.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]

    rows_by_id = {row.candidate_id: row for row in ledger.rows}
    ready_row = rows_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_row.sequence_number == 1
    assert ready_row.ledger_status == "ready_to_apply_manual_packet"
    assert ready_row.action == "apply_manual_application_packet"
    assert ready_row.checkboxes == [
        "confirm_decision_id_unique",
        "confirm_candidate_status_patch_matches_pending",
        "confirm_packet_delta_matches_preview",
        "append_review_decision_entry",
        "update_candidate_status",
        "run_source_intake_tests",
        "verify_formal_evidence_delta_zero",
    ]
    assert ready_row.blocking_issues == []
    assert ready_row.expected_candidate_status_update == {
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "from_status": "pending_review",
        "to_status": "returned",
    }

    blocked_row = rows_by_id["candidate_mingli_pattern_strength_017_001"]
    assert blocked_row.sequence_number == 2
    assert blocked_row.ledger_status == "blocked_resolve_draft_issues"
    assert blocked_row.checkboxes == [
        "resolve_draft_blocking_issues",
        "rerun_draft_validation",
        "rerun_application_guard",
        "rerun_preflight_report",
        "rerun_handoff_summary",
    ]
    assert "manual_application_packet_not_exportable" in blocked_row.blocking_issues
    assert "approved_candidate_cannot_use_needs_recheck" in blocked_row.blocking_issues

    missing_row = rows_by_id["candidate_hongfu_remedy_boundary_017_001"]
    assert missing_row.ledger_status == "needs_review_input_template"
    assert missing_row.checkboxes == [
        "fill_review_input_template",
        "run_draft_validation",
        "run_application_guard",
        "rerun_preflight_report",
        "rerun_handoff_summary",
    ]
    assert "source_page_or_section_locator" in missing_row.required_inputs
    assert "manual_application_packet_missing" in missing_row.blocking_issues
    assert ledger.unchecked_checkbox_count == sum(
        len(row.checkboxes) for row in ledger.rows
    )
    assert ledger.preview_review_decision_delta == 1
    assert ledger.preview_candidate_status_delta == 1
    assert ledger.applied_review_decision_delta == 0
    assert ledger.applied_candidate_status_delta == 0
    assert ledger.formal_evidence_delta == 0


def test_render_pending_candidate_review_manual_application_readiness_ledger_markdown(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    markdown = source_intake.render_pending_candidate_review_manual_application_readiness_ledger_markdown(
        [ready_draft, blocked_draft], tmp_path)

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Readiness Ledger\n"
    )
    assert "- Pending candidates: `4`" in markdown
    assert "- Ledger rows: `4`" in markdown
    assert "- Ready rows: `1`" in markdown
    assert "- Blocked rows: `1`" in markdown
    assert "- Missing draft rows: `2`" in markdown
    assert "- Unchecked checkbox count: `22`" in markdown
    assert "- Applied review decision delta: `0`" in markdown
    assert "- Applied candidate status delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "## Ledger Rows" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`: `ready_to_apply_manual_packet`" in markdown
    assert "- [ ] confirm_decision_id_unique" in markdown
    assert "- [ ] append_review_decision_entry" in markdown
    assert "2. `candidate_mingli_pattern_strength_017_001`: `blocked_resolve_draft_issues`" in markdown
    assert "- [ ] resolve_draft_blocking_issues" in markdown
    assert "manual_application_packet_not_exportable" in markdown
    assert "`candidate_hongfu_remedy_boundary_017_001`: `needs_review_input_template`" in markdown
    assert "- [ ] fill_review_input_template" in markdown
    assert "## Recommended Processing Order" in markdown
    assert "Readiness ledger is read-only planning metadata." in markdown


def test_pending_candidate_review_manual_application_readiness_ledger_handles_no_drafts(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ledger = (
        source_intake.build_pending_candidate_review_manual_application_readiness_ledger(
            [], tmp_path)
    )

    assert ledger.pending_candidate_count == 4
    assert ledger.ledger_row_count == 4
    assert ledger.ready_candidate_ids == []
    assert ledger.blocked_candidate_ids == []
    assert ledger.missing_draft_candidate_ids == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert {row.ledger_status for row in ledger.rows} == {
        "needs_review_input_template"
    }
    assert all("fill_review_input_template" in row.checkboxes for row in ledger.rows)
    assert all(
        "manual_application_packet_missing" in row.blocking_issues
        for row in ledger.rows
    )
    assert ledger.applied_review_decision_delta == 0
    assert ledger.applied_candidate_status_delta == 0
    assert ledger.formal_evidence_delta == 0


def test_build_pending_candidate_review_manual_application_session_packet_groups_session_work(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    packet = (
        source_intake.build_pending_candidate_review_manual_application_session_packet(
            [ready_draft, blocked_draft], tmp_path)
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert packet.session_title == "Pending Review Manual Application Session"
    assert packet.session_scope == "ready_first_manual_application"
    assert packet.pending_candidate_count == 4
    assert packet.ready_action_count == 1
    assert packet.blocked_follow_up_count == 1
    assert packet.missing_draft_follow_up_count == 2
    assert packet.unchecked_checkbox_count == 22
    assert packet.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]

    ready_action = packet.ready_action_queue[0]
    assert ready_action.candidate_id == "candidate_duan_ten_god_relation_017_001"
    assert ready_action.sequence_number == 1
    assert ready_action.action_type == "apply_manual_application_packet"
    assert ready_action.ledger_status == "ready_to_apply_manual_packet"
    assert ready_action.checkboxes == [
        "confirm_decision_id_unique",
        "confirm_candidate_status_patch_matches_pending",
        "confirm_packet_delta_matches_preview",
        "append_review_decision_entry",
        "update_candidate_status",
        "run_source_intake_tests",
        "verify_formal_evidence_delta_zero",
    ]
    assert ready_action.expected_candidate_status_update == {
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "from_status": "pending_review",
        "to_status": "returned",
    }

    blocked_follow_up = packet.blocked_follow_ups[0]
    assert blocked_follow_up.candidate_id == "candidate_mingli_pattern_strength_017_001"
    assert blocked_follow_up.action_type == "resolve_draft_blocking_issues"
    assert blocked_follow_up.ledger_status == "blocked_resolve_draft_issues"
    assert "manual_application_packet_not_exportable" in blocked_follow_up.blocking_issues

    missing_follow_up_ids = [
        action.candidate_id for action in packet.missing_draft_follow_ups
    ]
    assert missing_follow_up_ids == [
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.post_session_verification == [
        "run_source_intake_tests",
        "verify_formal_evidence_delta_zero",
        "rerun_readiness_ledger",
        "confirm_manual_changes_only",
    ]
    assert packet.preview_review_decision_delta == 1
    assert packet.preview_candidate_status_delta == 1
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert (
        "Manual application session packet is read-only planning metadata."
        in packet.boundary_notes
    )


def test_render_pending_candidate_review_manual_application_session_packet_markdown(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    markdown = source_intake.render_pending_candidate_review_manual_application_session_packet_markdown(
        [ready_draft, blocked_draft], tmp_path)

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Session Packet\n"
    )
    assert "## Session Header" in markdown
    assert "- Session id: `pending_review_manual_application_session`" in markdown
    assert "- Session scope: `ready_first_manual_application`" in markdown
    assert "- Ready actions: `1`" in markdown
    assert "- Blocked follow-ups: `1`" in markdown
    assert "- Missing draft follow-ups: `2`" in markdown
    assert "- Applied review decision delta: `0`" in markdown
    assert "- Applied candidate status delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "## Ready-First Action Queue" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`: `apply_manual_application_packet`" in markdown
    assert "- [ ] append_review_decision_entry" in markdown
    assert "## Blocked Follow-Ups" in markdown
    assert "`candidate_mingli_pattern_strength_017_001`: `resolve_draft_blocking_issues`" in markdown
    assert "manual_application_packet_not_exportable" in markdown
    assert "## Missing Draft Follow-Ups" in markdown
    assert "`candidate_hongfu_remedy_boundary_017_001`: `fill_review_input_template`" in markdown
    assert "## Post-Session Verification" in markdown
    assert "- [ ] rerun_readiness_ledger" in markdown
    assert "## Recommended Processing Order" in markdown
    assert "Manual application session packet is read-only planning metadata." in markdown


def test_pending_candidate_review_manual_application_session_packet_handles_no_drafts(tmp_path):
    _write_manual_application_fixture(tmp_path)
    packet = (
        source_intake.build_pending_candidate_review_manual_application_session_packet(
            [], tmp_path)
    )

    assert packet.pending_candidate_count == 4
    assert packet.ready_action_count == 0
    assert packet.blocked_follow_up_count == 0
    assert packet.missing_draft_follow_up_count == 4
    assert packet.ready_action_queue == []
    assert packet.blocked_follow_ups == []
    assert [
        action.candidate_id for action in packet.missing_draft_follow_ups
    ] == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert all(
        action.action_type == "fill_review_input_template"
        for action in packet.missing_draft_follow_ups
    )
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_build_pending_candidate_review_manual_application_session_outcome_preview_projects_ready_actions_only(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    preview = source_intake.build_pending_candidate_review_manual_application_session_outcome_preview(
        [ready_draft, blocked_draft], tmp_path)

    assert preview.session_id == "pending_review_manual_application_session"
    assert preview.preview_scope == "ready_actions_only"
    assert preview.pending_candidate_count == 4
    assert preview.preview_item_count == 4
    assert preview.projected_review_decision_delta == 1
    assert preview.projected_candidate_status_delta == 1
    assert preview.ready_applied_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert preview.projected_non_pending_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert preview.projected_remaining_pending_candidate_ids == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert preview.follow_up_candidate_ids == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert preview.post_session_next_actions == [
        "rerun_source_intake_tests",
        "rerun_readiness_ledger",
        "resolve_blocked_follow_ups",
        "fill_missing_draft_templates",
    ]

    items_by_id = {item.candidate_id: item for item in preview.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.session_lane == "ready_action"
    assert ready_item.current_candidate_status == "pending_review"
    assert ready_item.projected_candidate_status == "returned"
    assert ready_item.projected_outcome == "leaves_pending_review"
    assert ready_item.projected_review_decision_delta == 1
    assert ready_item.projected_candidate_status_delta == 1
    assert ready_item.remaining_follow_up_action == ""

    blocked_item = items_by_id["candidate_mingli_pattern_strength_017_001"]
    assert blocked_item.session_lane == "blocked_follow_up"
    assert blocked_item.projected_candidate_status == "pending_review"
    assert blocked_item.projected_outcome == "remains_pending_review"
    assert blocked_item.remaining_follow_up_action == "resolve_draft_blocking_issues"
    assert "manual_application_packet_not_exportable" in blocked_item.blocking_issues

    missing_item = items_by_id["candidate_hongfu_remedy_boundary_017_001"]
    assert missing_item.session_lane == "missing_draft_follow_up"
    assert missing_item.projected_candidate_status == "pending_review"
    assert missing_item.remaining_follow_up_action == "fill_review_input_template"
    assert preview.applied_review_decision_delta == 0
    assert preview.applied_candidate_status_delta == 0
    assert preview.formal_evidence_delta == 0


def test_render_pending_candidate_review_manual_application_session_outcome_preview_markdown(tmp_path):
    _write_manual_application_fixture(tmp_path)
    ready_draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }
    blocked_draft = {
        "decision_id": "review_candidate_mingli_pattern_strength_017_001",
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001",
        "source_quality": "needs_recheck",
        "confidence": "moderate",
        "rationale": "Draft still lacks safety resolution.",
        "approval_limitations": [],
        "uncertainty_and_limitation_language": "",
    }

    markdown = source_intake.render_pending_candidate_review_manual_application_session_outcome_preview_markdown(
        [ready_draft, blocked_draft], tmp_path)

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Session Outcome Preview\n"
    )
    assert "- Preview scope: `ready_actions_only`" in markdown
    assert "- Projected review decision additions: `1`" in markdown
    assert "- Projected candidate status updates: `1`" in markdown
    assert "- Applied review decision delta: `0`" in markdown
    assert "- Formal evidence delta: `0`" in markdown
    assert "## Projected Status Changes" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`: `pending_review` -> `returned`" in markdown
    assert "## Remaining Pending Follow-Ups" in markdown
    assert "`candidate_mingli_pattern_strength_017_001`: `resolve_draft_blocking_issues`" in markdown
    assert "`candidate_hongfu_remedy_boundary_017_001`: `fill_review_input_template`" in markdown
    assert "## Post-Session Next Actions" in markdown
    assert "- [ ] rerun_readiness_ledger" in markdown
    assert "Session outcome preview is read-only planning metadata." in markdown


def test_pending_candidate_review_manual_application_session_outcome_preview_handles_no_drafts(tmp_path):
    _write_manual_application_fixture(tmp_path)
    preview = source_intake.build_pending_candidate_review_manual_application_session_outcome_preview(
        [], tmp_path)

    assert preview.pending_candidate_count == 4
    assert preview.preview_item_count == 4
    assert preview.ready_applied_candidate_ids == []
    assert preview.projected_non_pending_candidate_ids == []
    assert preview.projected_remaining_pending_candidate_ids == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert {
        item.projected_outcome for item in preview.items
    } == {"remains_pending_review"}
    assert {
        item.remaining_follow_up_action for item in preview.items
    } == {"fill_review_input_template"}
    assert preview.projected_review_decision_delta == 0
    assert preview.projected_candidate_status_delta == 0
    assert preview.applied_review_decision_delta == 0
    assert preview.applied_candidate_status_delta == 0
    assert preview.formal_evidence_delta == 0


def _post_session_candidate_ids() -> list[str]:
    return [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]


def _write_post_session_verification_fixture(
    path: Path,
    *,
    duan_status: str = "pending_review",
    include_duan_review_decision: bool = False,
    status_overrides: dict[str, str] | None = None,
) -> None:
    status_overrides = status_overrides or {}
    _write_candidate_extracts(
        path,
        [
            _candidate_payload(
                candidate_id,
                status=status_overrides.get(
                    candidate_id,
                    duan_status
                    if candidate_id == "candidate_duan_ten_god_relation_017_001"
                    else "pending_review",
                ),
            )
            for candidate_id in _post_session_candidate_ids()
        ],
    )
    decisions = []
    if include_duan_review_decision:
        decisions.append(
            {
                "decision_id": "review_candidate_duan_ten_god_relation_017_001",
                "candidate_id": "candidate_duan_ten_god_relation_017_001",
                "decision": "returned",
                "reviewer": "maintainer",
                "reviewed_at": "2026-06-01",
                "rationale": "Returned until source page or section locator is supplied.",
                "required_changes": [
                    "Replace learning-reference locator before approval."
                ],
                "rejection_reason": "",
                "approval_limitations": [],
                "source_quality": "review_note",
                "confidence": "weak",
            }
        )
    _write_json(path / "review_decisions.json", decisions)


def _ready_duan_review_draft() -> dict[str, object]:
    return {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }


def test_build_pending_candidate_review_manual_application_post_session_verification_report_verifies_ready_application(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    report = source_intake.build_pending_candidate_review_manual_application_post_session_verification_report(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert report.session_id == "pending_review_manual_application_session"
    assert report.verification_scope == "ready_actions_only_post_session"
    assert report.post_session_status == "verified"
    assert report.expected_ready_candidate_count == 1
    assert report.verification_item_count == 5
    assert report.expected_review_decision_delta == 1
    assert report.expected_candidate_status_delta == 1
    assert report.verified_ready_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert report.blocked_ready_candidate_ids == []
    assert report.verified_follow_up_candidate_ids == [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert report.blocked_follow_up_candidate_ids == []

    items_by_id = {item.candidate_id: item for item in report.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.verification_lane == "ready_action"
    assert ready_item.expected_candidate_status == "returned"
    assert ready_item.actual_candidate_status == "returned"
    assert ready_item.expected_review_decision_id == (
        "review_candidate_duan_ten_god_relation_017_001"
    )
    assert ready_item.actual_review_decision_id == (
        "review_candidate_duan_ten_god_relation_017_001"
    )
    assert ready_item.actual_review_decision == "returned"
    assert ready_item.verification_status == "verified_applied"
    assert ready_item.blocking_issues == []

    follow_up_item = items_by_id["candidate_hongfu_remedy_boundary_017_001"]
    assert follow_up_item.verification_lane == "follow_up_pending"
    assert follow_up_item.expected_candidate_status == "pending_review"
    assert follow_up_item.actual_candidate_status == "pending_review"
    assert follow_up_item.verification_status == "verified_pending_follow_up"
    assert follow_up_item.blocking_issues == []
    assert report.applied_review_decision_delta == 0
    assert report.applied_candidate_status_delta == 0
    assert report.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_post_session_verification_report_flags_missing_manual_application(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    report = source_intake.build_pending_candidate_review_manual_application_post_session_verification_report(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert report.post_session_status == "blocked"
    assert report.verified_ready_candidate_ids == []
    assert report.blocked_ready_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    items_by_id = {item.candidate_id: item for item in report.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.actual_candidate_status == "pending_review"
    assert ready_item.actual_review_decision_id == ""
    assert ready_item.verification_status == "manual_application_missing"
    assert "review_decision_missing" in ready_item.blocking_issues
    assert "candidate_status_not_updated" in ready_item.blocking_issues
    assert report.verified_follow_up_candidate_ids == [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert report.applied_review_decision_delta == 0
    assert report.applied_candidate_status_delta == 0
    assert report.formal_evidence_delta == 0


def test_render_pending_candidate_review_manual_application_post_session_verification_report_markdown(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    markdown = source_intake.render_pending_candidate_review_manual_application_post_session_verification_report_markdown(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Post-Session Verification Report\n"
    )
    assert "- Verification scope: `ready_actions_only_post_session`" in markdown
    assert "- Post-session status: `verified`" in markdown
    assert "- Expected review decision additions: `1`" in markdown
    assert "- Verified ready candidates: `1`" in markdown
    assert "## Ready Action Verification" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`: `verified_applied`" in markdown
    assert "Expected status: `returned`; actual status: `returned`" in markdown
    assert "## Follow-Up Pending Verification" in markdown
    assert "`candidate_hongfu_remedy_boundary_017_001`: `verified_pending_follow_up`" in markdown
    assert "Post-session verification report is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_reconciliation_dashboard_groups_verified_and_follow_up_actions(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    dashboard = source_intake.build_pending_candidate_review_manual_application_reconciliation_dashboard(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert dashboard.session_id == "pending_review_manual_application_session"
    assert dashboard.reconciliation_scope == "post_session_manual_application"
    assert dashboard.post_session_status == "verified"
    assert dashboard.reconciliation_item_count == 5
    assert dashboard.action_counts == {
        "append_missing_review_decision": 0,
        "correct_candidate_status": 0,
        "investigate_follow_up_mismatch": 0,
        "continue_follow_up_processing": 4,
        "verified_complete": 1,
    }
    assert dashboard.candidates_by_action["verified_complete"] == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert dashboard.candidates_by_action["continue_follow_up_processing"] == [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert dashboard.recommended_processing_order == [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
        "candidate_duan_ten_god_relation_017_001",
    ]

    items_by_id = {item.candidate_id: item for item in dashboard.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.recommended_action == "verified_complete"
    assert ready_item.verification_status == "verified_applied"
    assert ready_item.reason_codes == ["ready_action_verified"]
    follow_up_item = items_by_id["candidate_hongfu_remedy_boundary_017_001"]
    assert follow_up_item.recommended_action == "continue_follow_up_processing"
    assert follow_up_item.reason_codes == ["follow_up_still_pending"]
    assert dashboard.applied_review_decision_delta == 0
    assert dashboard.applied_candidate_status_delta == 0
    assert dashboard.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_reconciliation_dashboard_prioritizes_blockers(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        status_overrides={"candidate_northeast_blind_image_001": "returned"},
    )

    dashboard = source_intake.build_pending_candidate_review_manual_application_reconciliation_dashboard(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert dashboard.post_session_status == "blocked"
    assert dashboard.action_counts["append_missing_review_decision"] == 1
    assert dashboard.action_counts["investigate_follow_up_mismatch"] == 1
    assert dashboard.action_counts["continue_follow_up_processing"] == 3
    assert dashboard.action_counts["verified_complete"] == 0
    assert dashboard.recommended_processing_order[:2] == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
    ]
    items_by_id = {item.candidate_id: item for item in dashboard.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.recommended_action == "append_missing_review_decision"
    assert "review_decision_missing" in ready_item.reason_codes
    follow_up_item = items_by_id["candidate_northeast_blind_image_001"]
    assert follow_up_item.recommended_action == "investigate_follow_up_mismatch"
    assert "follow_up_status_changed" in follow_up_item.reason_codes


def test_pending_candidate_review_manual_application_reconciliation_dashboard_suggests_candidate_status_correction(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        include_duan_review_decision=True,
    )

    dashboard = source_intake.build_pending_candidate_review_manual_application_reconciliation_dashboard(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert dashboard.action_counts["correct_candidate_status"] == 1
    assert dashboard.candidates_by_action["correct_candidate_status"] == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    items_by_id = {item.candidate_id: item for item in dashboard.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.recommended_action == "correct_candidate_status"
    assert ready_item.reason_codes == ["candidate_status_not_updated"]
    assert ready_item.blocking_issues == ["candidate_status_not_updated"]


def test_render_pending_candidate_review_manual_application_reconciliation_dashboard_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_reconciliation_dashboard_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Reconciliation Dashboard\n"
    )
    assert "- Reconciliation scope: `post_session_manual_application`" in markdown
    assert "- Post-session status: `blocked`" in markdown
    assert "- `append_missing_review_decision`: `1`" in markdown
    assert "- `continue_follow_up_processing`: `4`" in markdown
    assert "## Candidates By Action" in markdown
    assert "### append_missing_review_decision" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Recommended Processing Order" in markdown
    assert "Reconciliation dashboard is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_closure_packet_splits_closure_and_carry_forward(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    packet = source_intake.build_pending_candidate_review_manual_application_closure_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert packet.closure_scope == "manual_application_session_closure"
    assert packet.closure_status == "partial_closure_ready"
    assert packet.closure_item_count == 5
    assert packet.close_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert packet.carry_forward_candidate_ids == [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.closure_action_counts == {
        "carry_forward_missing_review_decision": 0,
        "carry_forward_candidate_status_correction": 0,
        "carry_forward_follow_up_investigation": 0,
        "carry_forward_follow_up_processing": 4,
        "close_verified_candidate_session_item": 1,
    }
    assert packet.recommended_next_session_setup == [
        "close_verified_candidate_session_items",
        "prepare_next_session_for_follow_up_processing",
    ]

    items_by_id = {item.candidate_id: item for item in packet.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.closure_lane == "session_closure"
    assert ready_item.closure_action == "close_verified_candidate_session_item"
    assert ready_item.closure_status == "ready_to_close"
    assert ready_item.source_reconciliation_action == "verified_complete"
    follow_up_item = items_by_id["candidate_hongfu_remedy_boundary_017_001"]
    assert follow_up_item.closure_lane == "carry_forward"
    assert follow_up_item.closure_action == "carry_forward_follow_up_processing"
    assert follow_up_item.closure_status == "carry_forward_to_next_session"
    assert follow_up_item.source_reconciliation_action == "continue_follow_up_processing"
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_closure_packet_carries_forward_blockers(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    packet = source_intake.build_pending_candidate_review_manual_application_closure_packet(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert packet.closure_status == "carry_forward_required"
    assert packet.close_candidate_ids == []
    assert packet.carry_forward_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.closure_action_counts["carry_forward_missing_review_decision"] == 1
    assert packet.closure_action_counts["carry_forward_follow_up_processing"] == 4
    assert packet.recommended_next_session_setup == [
        "prepare_missing_review_decision_application",
        "prepare_next_session_for_follow_up_processing",
    ]
    items_by_id = {item.candidate_id: item for item in packet.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.closure_action == "carry_forward_missing_review_decision"
    assert "review_decision_missing" in ready_item.reason_codes


def test_pending_candidate_review_manual_application_closure_packet_maps_status_correction_and_follow_up_investigation(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        include_duan_review_decision=True,
        status_overrides={"candidate_northeast_blind_image_001": "returned"},
    )

    packet = source_intake.build_pending_candidate_review_manual_application_closure_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.closure_status == "carry_forward_required"
    assert packet.closure_action_counts["carry_forward_candidate_status_correction"] == 1
    assert packet.closure_action_counts["carry_forward_follow_up_investigation"] == 1
    assert packet.recommended_next_session_setup[:2] == [
        "prepare_candidate_status_correction",
        "investigate_follow_up_mismatches",
    ]
    items_by_id = {item.candidate_id: item for item in packet.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.closure_action == "carry_forward_candidate_status_correction"
    follow_up_item = items_by_id["candidate_northeast_blind_image_001"]
    assert follow_up_item.closure_action == "carry_forward_follow_up_investigation"


def test_render_pending_candidate_review_manual_application_closure_packet_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_closure_packet_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Closure Packet\n"
    )
    assert "- Closure scope: `manual_application_session_closure`" in markdown
    assert "- Closure status: `carry_forward_required`" in markdown
    assert "- `carry_forward_missing_review_decision`: `1`" in markdown
    assert "- `carry_forward_follow_up_processing`: `4`" in markdown
    assert "## Session Closure Candidates" in markdown
    assert "## Carry Forward Candidates" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`: `carry_forward_missing_review_decision`" in markdown
    assert "## Recommended Next Session Setup" in markdown
    assert "- [ ] prepare_missing_review_decision_application" in markdown
    assert "Closure packet is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_starter_groups_carry_forward_lanes(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    starter = source_intake.build_pending_candidate_review_manual_application_next_session_starter(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert starter.session_id == "pending_review_manual_application_session"
    assert starter.starter_scope == "manual_application_next_session"
    assert starter.starter_status == "ready_for_next_manual_session"
    assert starter.starter_item_count == 5
    assert starter.starter_lane_counts == {
        "missing_review_decision": 1,
        "candidate_status_correction": 0,
        "follow_up_mismatch_investigation": 0,
        "follow_up_processing": 4,
    }
    assert starter.candidates_by_starter_lane["missing_review_decision"] == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert starter.candidates_by_starter_lane["follow_up_processing"] == [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert starter.recommended_start_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert starter.kickoff_checklist == [
        "review_carry_forward_items",
        "run_required_starter_lane_checklists",
        "rerun_next_session_starter",
    ]

    items_by_id = {item.candidate_id: item for item in starter.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.starter_lane == "missing_review_decision"
    assert ready_item.starter_action == "prepare_missing_review_decision_application"
    assert ready_item.starter_status == "ready_to_start"
    assert ready_item.source_closure_action == "carry_forward_missing_review_decision"
    assert ready_item.checklist == [
        "recover_ready_manual_application_packet",
        "append_missing_review_decision",
        "rerun_post_session_verification",
        "rerun_reconciliation_dashboard",
        "rerun_closure_packet",
    ]
    follow_up_item = items_by_id["candidate_hongfu_remedy_boundary_017_001"]
    assert follow_up_item.starter_lane == "follow_up_processing"
    assert follow_up_item.starter_action == "continue_follow_up_processing"
    assert "run_draft_validation" in follow_up_item.checklist
    assert starter.applied_review_decision_delta == 0
    assert starter.applied_candidate_status_delta == 0
    assert starter.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_starter_maps_status_correction_and_follow_up_investigation(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        include_duan_review_decision=True,
        status_overrides={"candidate_northeast_blind_image_001": "returned"},
    )

    starter = source_intake.build_pending_candidate_review_manual_application_next_session_starter(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert starter.starter_lane_counts["candidate_status_correction"] == 1
    assert starter.starter_lane_counts["follow_up_mismatch_investigation"] == 1
    assert starter.recommended_start_order[:2] == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
    ]
    items_by_id = {item.candidate_id: item for item in starter.items}
    ready_item = items_by_id["candidate_duan_ten_god_relation_017_001"]
    assert ready_item.starter_lane == "candidate_status_correction"
    assert ready_item.starter_action == "prepare_candidate_status_correction"
    assert ready_item.checklist == [
        "verify_review_decision_present",
        "apply_candidate_status_patch",
        "rerun_post_session_verification",
        "rerun_reconciliation_dashboard",
        "rerun_closure_packet",
    ]
    follow_up_item = items_by_id["candidate_northeast_blind_image_001"]
    assert follow_up_item.starter_lane == "follow_up_mismatch_investigation"
    assert follow_up_item.starter_action == "investigate_follow_up_mismatch"
    assert "inspect_unexpected_follow_up_change" in follow_up_item.checklist


def test_pending_candidate_review_manual_application_next_session_starter_omits_closed_candidates(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    starter = source_intake.build_pending_candidate_review_manual_application_next_session_starter(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert starter.starter_item_count == 4
    assert "candidate_duan_ten_god_relation_017_001" not in starter.recommended_start_order
    assert starter.starter_lane_counts == {
        "missing_review_decision": 0,
        "candidate_status_correction": 0,
        "follow_up_mismatch_investigation": 0,
        "follow_up_processing": 4,
    }
    assert starter.kickoff_checklist == [
        "close_verified_candidate_session_items",
        "review_carry_forward_items",
        "run_required_starter_lane_checklists",
        "rerun_next_session_starter",
    ]


def test_render_pending_candidate_review_manual_application_next_session_starter_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_starter_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Starter\n"
    )
    assert "- Starter scope: `manual_application_next_session`" in markdown
    assert "- Starter status: `ready_for_next_manual_session`" in markdown
    assert "- `missing_review_decision`: `1`" in markdown
    assert "- `follow_up_processing`: `4`" in markdown
    assert "## Candidates By Starter Lane" in markdown
    assert "### missing_review_decision" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`: `prepare_missing_review_decision_application`" in markdown
    assert "## Kickoff Checklist" in markdown
    assert "- [ ] run_required_starter_lane_checklists" in markdown
    assert "Next-session starter is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_packet_groups_correction_and_follow_up_queues(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_packet(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert packet.packet_scope == "manual_application_next_session_packet"
    assert packet.packet_status == "ready_for_next_manual_session"
    assert packet.packet_item_count == 5
    assert packet.correction_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert packet.follow_up_candidate_ids == [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.kickoff_checklist == [
        "review_carry_forward_items",
        "run_required_starter_lane_checklists",
        "rerun_next_session_starter",
    ]
    assert packet.post_session_verification == [
        "rerun_post_session_verification",
        "rerun_reconciliation_dashboard",
        "rerun_closure_packet",
        "rerun_next_session_starter",
        "rerun_next_session_packet",
    ]

    correction_item = packet.correction_queue[0]
    assert correction_item.candidate_id == "candidate_duan_ten_god_relation_017_001"
    assert correction_item.packet_lane == "correction_queue"
    assert correction_item.starter_lane == "missing_review_decision"
    assert correction_item.packet_action == "prepare_missing_review_decision_application"
    assert "append_missing_review_decision" in correction_item.checklist
    follow_up_item = packet.follow_up_queue[-1]
    assert follow_up_item.candidate_id == "candidate_hongfu_remedy_boundary_017_001"
    assert follow_up_item.packet_lane == "follow_up_queue"
    assert follow_up_item.starter_lane == "follow_up_processing"
    assert follow_up_item.packet_action == "continue_follow_up_processing"
    assert "run_draft_validation" in follow_up_item.checklist
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_packet_keeps_closed_candidates_out_of_queues(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.packet_item_count == 4
    assert packet.correction_candidate_ids == []
    assert packet.follow_up_candidate_ids == [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert "candidate_duan_ten_god_relation_017_001" not in (
        packet.recommended_processing_order
    )
    assert packet.kickoff_checklist == [
        "close_verified_candidate_session_items",
        "review_carry_forward_items",
        "run_required_starter_lane_checklists",
        "rerun_next_session_starter",
    ]


def test_pending_candidate_review_manual_application_next_session_packet_prioritizes_correction_lanes(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        include_duan_review_decision=True,
        status_overrides={"candidate_northeast_blind_image_001": "returned"},
    )

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.correction_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
    ]
    assert packet.follow_up_candidate_ids == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.recommended_processing_order[:2] == packet.correction_candidate_ids
    assert packet.correction_queue[0].starter_lane == "candidate_status_correction"
    assert packet.correction_queue[0].packet_action == (
        "prepare_candidate_status_correction"
    )
    assert packet.correction_queue[1].starter_lane == (
        "follow_up_mismatch_investigation"
    )
    assert packet.correction_queue[1].packet_action == "investigate_follow_up_mismatch"


def test_render_pending_candidate_review_manual_application_next_session_packet_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_packet_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Packet\n"
    )
    assert "- Packet scope: `manual_application_next_session_packet`" in markdown
    assert "- Packet status: `ready_for_next_manual_session`" in markdown
    assert "- Correction queue: `1`" in markdown
    assert "- Follow-up queue: `4`" in markdown
    assert "## Correction Queue" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`: `prepare_missing_review_decision_application`" in markdown
    assert "## Follow-Up Queue" in markdown
    assert "`candidate_hongfu_remedy_boundary_017_001`: `continue_follow_up_processing`" in markdown
    assert "## Recommended Processing Order" in markdown
    assert "## Kickoff Checklist" in markdown
    assert "## Post-Session Verification" in markdown
    assert "- [ ] rerun_next_session_packet" in markdown
    assert "Next-session packet is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_audit_summary_tracks_packet_coverage(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    summary = source_intake.build_pending_candidate_review_manual_application_next_session_audit_summary(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert summary.session_id == "pending_review_manual_application_session"
    assert summary.audit_scope == "manual_application_next_session_audit"
    assert summary.audit_status == "ready_for_next_manual_session"
    assert summary.closure_status == "carry_forward_required"
    assert summary.starter_status == "ready_for_next_manual_session"
    assert summary.packet_status == "ready_for_next_manual_session"
    assert summary.closure_item_count == 5
    assert summary.starter_item_count == 5
    assert summary.packet_item_count == 5
    assert summary.correction_queue_count == 1
    assert summary.follow_up_queue_count == 4
    assert summary.correction_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert summary.follow_up_candidate_ids == [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert summary.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert summary.coverage_checks == {
        "closure_carry_forward_to_starter": "covered",
        "starter_to_packet_order": "covered",
        "correction_queue": "covered",
        "follow_up_queue": "covered",
        "kickoff_checklist": "covered",
        "post_session_verification": "covered",
    }
    assert summary.shortest_next_actions == [
        "apply_correction_queue_first",
        "continue_follow_up_queue",
        "rerun_post_session_verification_chain",
    ]
    assert summary.applied_review_decision_delta == 0
    assert summary.applied_candidate_status_delta == 0
    assert summary.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_audit_summary_keeps_closed_candidates_out_of_queues(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    summary = source_intake.build_pending_candidate_review_manual_application_next_session_audit_summary(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert summary.closure_status == "partial_closure_ready"
    assert summary.packet_item_count == 4
    assert summary.correction_queue_count == 0
    assert summary.follow_up_queue_count == 4
    assert "candidate_duan_ten_god_relation_017_001" not in (
        summary.recommended_processing_order
    )
    assert summary.shortest_next_actions == [
        "close_verified_candidate_session_items",
        "continue_follow_up_queue",
        "rerun_post_session_verification_chain",
    ]
    assert summary.coverage_checks["closure_carry_forward_to_starter"] == "covered"
    assert summary.coverage_checks["starter_to_packet_order"] == "covered"


def test_pending_candidate_review_manual_application_next_session_audit_summary_prioritizes_correction_queue(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        include_duan_review_decision=True,
        status_overrides={"candidate_northeast_blind_image_001": "returned"},
    )

    summary = source_intake.build_pending_candidate_review_manual_application_next_session_audit_summary(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert summary.correction_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
    ]
    assert summary.follow_up_candidate_ids == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert summary.recommended_processing_order[:2] == (
        summary.correction_candidate_ids
    )
    assert summary.shortest_next_actions[0] == "apply_correction_queue_first"


def test_render_pending_candidate_review_manual_application_next_session_audit_summary_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_audit_summary_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Audit Summary\n"
    )
    assert "- Audit scope: `manual_application_next_session_audit`" in markdown
    assert "- Audit status: `ready_for_next_manual_session`" in markdown
    assert "- Closure status: `carry_forward_required`" in markdown
    assert "- Correction queue: `1`" in markdown
    assert "- Follow-up queue: `4`" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `starter_to_packet_order`: `covered`" in markdown
    assert "## Shortest Next Actions" in markdown
    assert "- [ ] apply_correction_queue_first" in markdown
    assert "## Recommended Processing Order" in markdown
    assert "## Kickoff Checklist" in markdown
    assert "## Post-Session Verification" in markdown
    assert "Next-session audit summary is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_operator_checklist_expands_audit_actions(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    checklist = source_intake.build_pending_candidate_review_manual_application_next_session_operator_checklist(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert checklist.session_id == "pending_review_manual_application_session"
    assert checklist.checklist_scope == "manual_application_next_session_operator"
    assert checklist.checklist_status == "ready_for_operator"
    assert checklist.checklist_item_count == 3
    assert checklist.action_sequence == [
        "apply_correction_queue_first",
        "continue_follow_up_queue",
        "rerun_post_session_verification_chain",
    ]
    assert checklist.target_candidates_by_action == {
        "apply_correction_queue_first": [
            "candidate_duan_ten_god_relation_017_001"
        ],
        "continue_follow_up_queue": [
            "candidate_northeast_blind_image_001",
            "candidate_mingli_pattern_strength_017_001",
            "candidate_mingxue_five_element_balance_017_001",
            "candidate_hongfu_remedy_boundary_017_001",
        ],
        "rerun_post_session_verification_chain": [
            "candidate_duan_ten_god_relation_017_001",
            "candidate_northeast_blind_image_001",
            "candidate_mingli_pattern_strength_017_001",
            "candidate_mingxue_five_element_balance_017_001",
            "candidate_hongfu_remedy_boundary_017_001",
        ],
    }
    assert checklist.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]

    correction_item = checklist.items[0]
    assert correction_item.operator_action == "apply_correction_queue_first"
    assert correction_item.target_candidates == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert correction_item.ready_criteria == [
        "next_session_audit_ready",
        "correction_queue_not_empty",
    ]
    assert "finish_corrections_before_follow_up" in (
        correction_item.operator_checklist
    )
    assert "rerun_post_session_verification" in (
        correction_item.verification_checklist
    )
    assert checklist.applied_review_decision_delta == 0
    assert checklist.applied_candidate_status_delta == 0
    assert checklist.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_operator_checklist_targets_closed_candidates(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    checklist = source_intake.build_pending_candidate_review_manual_application_next_session_operator_checklist(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert checklist.action_sequence == [
        "close_verified_candidate_session_items",
        "continue_follow_up_queue",
        "rerun_post_session_verification_chain",
    ]
    assert checklist.target_candidates_by_action[
        "close_verified_candidate_session_items"
    ] == ["candidate_duan_ten_god_relation_017_001"]
    assert "candidate_duan_ten_god_relation_017_001" not in (
        checklist.recommended_processing_order
    )
    close_item = checklist.items[0]
    assert close_item.ready_criteria == [
        "closure_packet_has_verified_items",
        "session_item_verified_complete",
    ]
    assert "close_verified_items_before_follow_up" in (
        close_item.operator_checklist
    )


def test_pending_candidate_review_manual_application_next_session_operator_checklist_prioritizes_correction_targets(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        include_duan_review_decision=True,
        status_overrides={"candidate_northeast_blind_image_001": "returned"},
    )

    checklist = source_intake.build_pending_candidate_review_manual_application_next_session_operator_checklist(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert checklist.action_sequence[0] == "apply_correction_queue_first"
    assert checklist.target_candidates_by_action["apply_correction_queue_first"] == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
    ]
    assert checklist.target_candidates_by_action["continue_follow_up_queue"] == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert checklist.items[0].operator_checklist[0] == (
        "open_next_session_packet"
    )


def test_render_pending_candidate_review_manual_application_next_session_operator_checklist_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_operator_checklist_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Operator Checklist\n"
    )
    assert "- Checklist scope: `manual_application_next_session_operator`" in markdown
    assert "- Checklist status: `ready_for_operator`" in markdown
    assert "- Checklist items: `3`" in markdown
    assert "## Operator Actions" in markdown
    assert "### 1. apply_correction_queue_first" in markdown
    assert "- Target candidates:" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Recommended Processing Order" in markdown
    assert "## Kickoff Checklist" in markdown
    assert "## Verification Checklist" in markdown
    assert "Next-session operator checklist is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_execution_handoff_condenses_operator_checklist(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    handoff = source_intake.build_pending_candidate_review_manual_application_next_session_execution_handoff(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert handoff.session_id == "pending_review_manual_application_session"
    assert handoff.handoff_scope == "manual_application_next_session_execution"
    assert handoff.handoff_status == "ready_for_execution"
    assert handoff.first_action == "apply_correction_queue_first"
    assert handoff.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert handoff.ready_conditions == [
        "operator_checklist_ready",
        "next_session_audit_ready",
        "correction_queue_not_empty",
    ]
    assert handoff.blocked_conditions == []
    assert handoff.action_sequence == [
        "apply_correction_queue_first",
        "continue_follow_up_queue",
        "rerun_post_session_verification_chain",
    ]
    assert handoff.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert handoff.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert handoff.verification_chain == [
        "rerun_post_session_verification",
        "rerun_reconciliation_dashboard",
        "rerun_closure_packet",
        "rerun_next_session_starter",
        "rerun_next_session_packet",
    ]
    assert handoff.applied_review_decision_delta == 0
    assert handoff.applied_candidate_status_delta == 0
    assert handoff.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_execution_handoff_surfaces_close_first_action(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    handoff = source_intake.build_pending_candidate_review_manual_application_next_session_execution_handoff(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert handoff.first_action == "close_verified_candidate_session_items"
    assert handoff.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert handoff.ready_conditions == [
        "operator_checklist_ready",
        "closure_packet_has_verified_items",
        "session_item_verified_complete",
    ]
    assert "candidate_duan_ten_god_relation_017_001" in handoff.target_candidates
    assert "candidate_duan_ten_god_relation_017_001" not in (
        handoff.recommended_processing_order
    )


def test_pending_candidate_review_manual_application_next_session_execution_handoff_prioritizes_correction_targets(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        include_duan_review_decision=True,
        status_overrides={"candidate_northeast_blind_image_001": "returned"},
    )

    handoff = source_intake.build_pending_candidate_review_manual_application_next_session_execution_handoff(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert handoff.first_action == "apply_correction_queue_first"
    assert handoff.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
    ]
    assert handoff.recommended_processing_order[:2] == handoff.first_action_targets
    assert handoff.action_sequence[0] == "apply_correction_queue_first"


def test_render_pending_candidate_review_manual_application_next_session_execution_handoff_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_execution_handoff_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Execution Handoff\n"
    )
    assert "- Handoff scope: `manual_application_next_session_execution`" in markdown
    assert "- Handoff status: `ready_for_execution`" in markdown
    assert "- First action: `apply_correction_queue_first`" in markdown
    assert "## First Action Targets" in markdown
    assert "`candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Ready Conditions" in markdown
    assert "- `operator_checklist_ready`" in markdown
    assert "## Blocked Conditions" in markdown
    assert "- `none`" in markdown
    assert "## Action Sequence" in markdown
    assert "## Verification Chain" in markdown
    assert "Next-session execution handoff is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_completion_criteria_from_handoff(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    criteria = source_intake.build_pending_candidate_review_manual_application_next_session_completion_criteria(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert criteria.session_id == "pending_review_manual_application_session"
    assert criteria.criteria_scope == "manual_application_next_session_completion"
    assert criteria.criteria_status == "ready_for_completion_check"
    assert criteria.first_action == "apply_correction_queue_first"
    assert criteria.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert criteria.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert criteria.done_conditions == [
        "complete_first_action",
        "complete_remaining_action_sequence",
        "run_verification_entrypoints",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert criteria.blocked_conditions == []
    assert criteria.retry_conditions == [
        "retry_first_action_if_verification_fails",
        "rerun_execution_handoff_after_manual_changes",
    ]
    assert criteria.verification_entrypoints == [
        "rerun_post_session_verification",
        "rerun_reconciliation_dashboard",
        "rerun_closure_packet",
        "rerun_next_session_starter",
        "rerun_next_session_packet",
    ]
    assert criteria.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert criteria.applied_review_decision_delta == 0
    assert criteria.applied_candidate_status_delta == 0
    assert criteria.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_completion_criteria_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    criteria = source_intake.build_pending_candidate_review_manual_application_next_session_completion_criteria(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert criteria.first_action == "close_verified_candidate_session_items"
    assert criteria.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert "candidate_duan_ten_god_relation_017_001" in criteria.target_candidates
    assert "candidate_duan_ten_god_relation_017_001" not in (
        criteria.recommended_processing_order
    )
    assert criteria.done_conditions[0] == "complete_first_action"
    assert criteria.blocked_conditions == []


def test_pending_candidate_review_manual_application_next_session_completion_criteria_prioritizes_correction_targets(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        include_duan_review_decision=True,
        status_overrides={"candidate_northeast_blind_image_001": "returned"},
    )

    criteria = source_intake.build_pending_candidate_review_manual_application_next_session_completion_criteria(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert criteria.first_action == "apply_correction_queue_first"
    assert criteria.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
    ]
    assert criteria.recommended_processing_order[:2] == criteria.first_action_targets
    assert criteria.retry_conditions == [
        "retry_first_action_if_verification_fails",
        "rerun_execution_handoff_after_manual_changes",
    ]


def test_render_pending_candidate_review_manual_application_next_session_completion_criteria_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_completion_criteria_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Completion Criteria\n"
    )
    assert "- Criteria scope: `manual_application_next_session_completion`" in markdown
    assert "- Criteria status: `ready_for_completion_check`" in markdown
    assert "- First action: `apply_correction_queue_first`" in markdown
    assert "## Done Conditions" in markdown
    assert "- `complete_first_action`" in markdown
    assert "## Blocked Conditions" in markdown
    assert "- `none`" in markdown
    assert "## Retry Conditions" in markdown
    assert "- `retry_first_action_if_verification_fails`" in markdown
    assert "## Verification Entrypoints" in markdown
    assert "- [ ] rerun_post_session_verification" in markdown
    assert "Next-session completion criteria is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_retry_planner_expands_completion_retry_conditions(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    planner = source_intake.build_pending_candidate_review_manual_application_next_session_retry_planner(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert planner.session_id == "pending_review_manual_application_session"
    assert planner.retry_scope == "manual_application_next_session_retry"
    assert planner.retry_status == "ready_for_retry_planning"
    assert planner.first_action == "apply_correction_queue_first"
    assert planner.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert planner.failure_entrypoints == [
        "first_action_verification_failed",
        "execution_handoff_stale_after_manual_changes",
    ]
    assert planner.retry_conditions == [
        "retry_first_action_if_verification_fails",
        "rerun_execution_handoff_after_manual_changes",
    ]
    assert planner.retry_sequence == [
        "retry_first_action_if_verification_fails",
        "rerun_execution_handoff_after_manual_changes",
        "rerun_completion_criteria",
    ]
    assert planner.return_to_handoff_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
    ]
    assert planner.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert planner.verification_entrypoints == [
        "rerun_post_session_verification",
        "rerun_reconciliation_dashboard",
        "rerun_closure_packet",
        "rerun_next_session_starter",
        "rerun_next_session_packet",
    ]
    assert planner.applied_review_decision_delta == 0
    assert planner.applied_candidate_status_delta == 0
    assert planner.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_retry_planner_surfaces_close_first_targets(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    planner = source_intake.build_pending_candidate_review_manual_application_next_session_retry_planner(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert planner.first_action == "close_verified_candidate_session_items"
    assert planner.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert "candidate_duan_ten_god_relation_017_001" in planner.target_candidates
    assert "candidate_duan_ten_god_relation_017_001" not in (
        planner.recommended_processing_order
    )
    assert planner.failure_entrypoints[0] == "first_action_verification_failed"


def test_pending_candidate_review_manual_application_next_session_retry_planner_prioritizes_correction_targets(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        include_duan_review_decision=True,
        status_overrides={"candidate_northeast_blind_image_001": "returned"},
    )

    planner = source_intake.build_pending_candidate_review_manual_application_next_session_retry_planner(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert planner.first_action == "apply_correction_queue_first"
    assert planner.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
    ]
    assert planner.recommended_processing_order[:2] == planner.first_action_targets
    assert planner.retry_sequence[0] == "retry_first_action_if_verification_fails"


def test_render_pending_candidate_review_manual_application_next_session_retry_planner_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_retry_planner_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Retry Planner\n"
    )
    assert "- Retry scope: `manual_application_next_session_retry`" in markdown
    assert "- Retry status: `ready_for_retry_planning`" in markdown
    assert "- First action: `apply_correction_queue_first`" in markdown
    assert "## Failure Entrypoints" in markdown
    assert "- `first_action_verification_failed`" in markdown
    assert "## Retry Sequence" in markdown
    assert "- [ ] retry_first_action_if_verification_fails" in markdown
    assert "## Return To Handoff Path" in markdown
    assert "- [ ] render_next_session_execution_handoff" in markdown
    assert "## Verification Entrypoints" in markdown
    assert "Next-session retry planner is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_final_readiness_summary_combines_criteria_and_retry_plan(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    summary = source_intake.build_pending_candidate_review_manual_application_next_session_final_readiness_summary(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert summary.session_id == "pending_review_manual_application_session"
    assert summary.readiness_scope == "manual_application_next_session_final_readiness"
    assert summary.readiness_status == "ready_to_start_next_manual_session"
    assert summary.start_gate == "start_with_first_action"
    assert summary.first_action == "apply_correction_queue_first"
    assert summary.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert summary.ready_conditions == [
        "completion_criteria_ready",
        "retry_plan_ready",
        "verification_entrypoints_present",
        "first_action_targets_present",
    ]
    assert summary.blocked_conditions == []
    assert summary.retry_conditions == [
        "retry_first_action_if_verification_fails",
        "rerun_execution_handoff_after_manual_changes",
    ]
    assert summary.failure_entrypoints == [
        "first_action_verification_failed",
        "execution_handoff_stale_after_manual_changes",
    ]
    assert summary.verification_entrypoints == [
        "rerun_post_session_verification",
        "rerun_reconciliation_dashboard",
        "rerun_closure_packet",
        "rerun_next_session_starter",
        "rerun_next_session_packet",
    ]
    assert summary.return_to_handoff_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
    ]
    assert summary.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert summary.recommended_processing_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert summary.final_readiness_checks == [
        "confirm_completion_criteria_ready",
        "confirm_retry_plan_ready",
        "confirm_first_action_targets_present",
        "confirm_verification_entrypoints_present",
        "confirm_read_only_boundaries",
    ]
    assert summary.applied_review_decision_delta == 0
    assert summary.applied_candidate_status_delta == 0
    assert summary.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_final_readiness_summary_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    summary = source_intake.build_pending_candidate_review_manual_application_next_session_final_readiness_summary(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert summary.first_action == "close_verified_candidate_session_items"
    assert summary.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert "candidate_duan_ten_god_relation_017_001" in summary.target_candidates
    assert "candidate_duan_ten_god_relation_017_001" not in (
        summary.recommended_processing_order
    )
    assert summary.start_gate == "start_with_first_action"
    assert summary.blocked_conditions == []


def test_pending_candidate_review_manual_application_next_session_final_readiness_summary_prioritizes_correction_targets(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        include_duan_review_decision=True,
        status_overrides={"candidate_northeast_blind_image_001": "returned"},
    )

    summary = source_intake.build_pending_candidate_review_manual_application_next_session_final_readiness_summary(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert summary.first_action == "apply_correction_queue_first"
    assert summary.first_action_targets == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
    ]
    assert summary.recommended_processing_order[:2] == summary.first_action_targets
    assert summary.readiness_status == "ready_to_start_next_manual_session"


def test_render_pending_candidate_review_manual_application_next_session_final_readiness_summary_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_final_readiness_summary_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Final Readiness Summary\n"
    )
    assert "- Readiness scope: `manual_application_next_session_final_readiness`" in markdown
    assert "- Readiness status: `ready_to_start_next_manual_session`" in markdown
    assert "- Start gate: `start_with_first_action`" in markdown
    assert "- First action: `apply_correction_queue_first`" in markdown
    assert "## Final Readiness Checks" in markdown
    assert "- [ ] confirm_completion_criteria_ready" in markdown
    assert "## Ready Conditions" in markdown
    assert "- `completion_criteria_ready`" in markdown
    assert "## Failure Entrypoints" in markdown
    assert "- `first_action_verification_failed`" in markdown
    assert "## Return To Handoff Path" in markdown
    assert "Next-session final readiness summary is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_condenses_readiness_summary(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    note = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_note(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert note.session_id == "pending_review_manual_application_session"
    assert note.launch_scope == "manual_application_next_session_launch_note"
    assert note.launch_status == "ready_to_launch_manual_execution"
    assert note.start_gate == "start_with_first_action"
    assert note.first_command == "execute_apply_correction_queue_first"
    assert note.first_command_targets == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert note.candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert note.abort_conditions == [
        "abort_if_launch_status_not_ready",
        "abort_if_first_command_targets_missing",
        "abort_if_boundary_delta_nonzero",
    ]
    assert note.return_paths == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert note.verification_commands == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
    ]
    assert note.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert note.applied_review_decision_delta == 0
    assert note.applied_candidate_status_delta == 0
    assert note.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    note = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_note(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert note.first_command == "execute_close_verified_candidate_session_items"
    assert note.first_command_targets == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert note.candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert note.launch_status == "ready_to_launch_manual_execution"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Note\n"
    )
    assert "- Launch scope: `manual_application_next_session_launch_note`" in markdown
    assert "- Launch status: `ready_to_launch_manual_execution`" in markdown
    assert "- Start gate: `start_with_first_action`" in markdown
    assert "- First command: `execute_apply_correction_queue_first`" in markdown
    assert "## First Command Targets" in markdown
    assert "- `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Abort Conditions" in markdown
    assert "- [ ] abort_if_boundary_delta_nonzero" in markdown
    assert "## Verification Commands" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Return Paths" in markdown
    assert "- [ ] render_next_session_final_readiness_summary" in markdown
    assert "Next-session manual execution launch note is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_tracks_launch_note_coverage(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert audit.audit_scope == "manual_application_next_session_launch_audit"
    assert audit.audit_status == "launch_audit_ready"
    assert audit.readiness_status == "ready_to_start_next_manual_session"
    assert audit.launch_status == "ready_to_launch_manual_execution"
    assert audit.start_gate == "start_with_first_action"
    assert audit.first_command == "execute_apply_correction_queue_first"
    assert audit.coverage_checks == {
        "start_gate_to_launch_note": "covered",
        "first_action_to_first_command": "covered",
        "candidate_order_covers_recommended_processing_order": "covered",
        "abort_conditions_present": "covered",
        "return_paths_include_final_readiness": "covered",
        "verification_commands_present": "covered",
        "target_candidates_preserved": "covered",
        "read_only_boundary_preserved": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == [
        "applied_review_decision_delta_zero",
        "applied_candidate_status_delta_zero",
        "formal_evidence_delta_zero",
    ]
    assert audit.candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.return_paths == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.verification_commands == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.first_command == "execute_close_verified_candidate_session_items"
    assert audit.candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert audit.coverage_checks["first_action_to_first_command"] == "covered"
    assert audit.audit_status == "launch_audit_ready"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_launch_audit`" in markdown
    assert "- Audit status: `launch_audit_ready`" in markdown
    assert "- Launch status: `ready_to_launch_manual_execution`" in markdown
    assert "- First command: `execute_apply_correction_queue_first`" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `first_action_to_first_command`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No missing launch-note coverage." in markdown
    assert "## Boundary Checks" in markdown
    assert "- [ ] applied_review_decision_delta_zero" in markdown
    assert "## Verification Commands" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "Next-session manual execution launch audit is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_freezes_ready_launch(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert seal.seal_scope == "manual_application_next_session_launch_seal"
    assert seal.seal_status == "sealed_for_manual_execution"
    assert seal.audit_status == "launch_audit_ready"
    assert seal.launch_status == "ready_to_launch_manual_execution"
    assert seal.start_gate == "start_with_first_action"
    assert seal.sealed_first_command == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.blocked_reasons == []
    assert seal.seal_checks == [
        "confirm_launch_audit_ready",
        "confirm_launch_coverage_complete",
        "confirm_first_command_sealed",
        "confirm_verification_commands_present",
        "confirm_boundary_delta_zero",
    ]
    assert seal.verification_commands == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
    ]
    assert seal.rollback_entrypoints == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert seal.sealed_first_command == "execute_close_verified_candidate_session_items"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert seal.seal_status == "sealed_for_manual_execution"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_launch_seal`" in markdown
    assert "- Seal status: `sealed_for_manual_execution`" in markdown
    assert "- Audit status: `launch_audit_ready`" in markdown
    assert "- Sealed first command: `execute_apply_correction_queue_first`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_launch_audit_ready" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No launch seal blockers." in markdown
    assert "## Verification Commands" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Rollback Entrypoints" in markdown
    assert "- [ ] render_next_session_final_readiness_summary" in markdown
    assert "Next-session manual execution launch seal is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_expands_launch_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    runbook = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert runbook.session_id == "pending_review_manual_application_session"
    assert runbook.runbook_scope == "manual_application_next_session_launch_runbook"
    assert runbook.runbook_status == "ready_for_manual_execution_runbook"
    assert runbook.seal_status == "sealed_for_manual_execution"
    assert runbook.start_gate == "start_with_first_action"
    assert runbook.first_step == "execute_apply_correction_queue_first"
    assert runbook.execution_order == [
        "execute_apply_correction_queue_first",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
        "run_focused_source_intake_tests",
        "run_boundary_regression_tests",
        "run_full_suite",
        "rerun_launch_seal",
    ]
    assert runbook.step_verification == {
        "execute_apply_correction_queue_first": [
            "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
            "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
            "uv run --with pytest python -m pytest",
        ],
        "candidate_order": ["confirm_candidate_order_matches_launch_seal"],
        "post_completion": ["rerun_launch_seal"],
    }
    assert runbook.failure_rollback == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert runbook.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert runbook.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert runbook.runbook_checks == [
        "confirm_launch_seal_ready",
        "confirm_first_step_present",
        "confirm_execution_order_present",
        "confirm_step_verification_present",
        "confirm_failure_rollback_present",
        "confirm_post_completion_review_present",
        "confirm_read_only_boundaries",
    ]
    assert runbook.applied_review_decision_delta == 0
    assert runbook.applied_candidate_status_delta == 0
    assert runbook.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    runbook = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert runbook.first_step == "execute_close_verified_candidate_session_items"
    assert runbook.execution_order[0] == "execute_close_verified_candidate_session_items"
    assert runbook.execution_order[1] == "candidate_duan_ten_god_relation_017_001"
    assert runbook.runbook_status == "ready_for_manual_execution_runbook"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Runbook\n"
    )
    assert "- Runbook scope: `manual_application_next_session_launch_runbook`" in markdown
    assert "- Runbook status: `ready_for_manual_execution_runbook`" in markdown
    assert "- Seal status: `sealed_for_manual_execution`" in markdown
    assert "- First step: `execute_apply_correction_queue_first`" in markdown
    assert "## Execution Order" in markdown
    assert "1. `execute_apply_correction_queue_first`" in markdown
    assert "## Step Verification" in markdown
    assert "- `execute_apply_correction_queue_first`" in markdown
    assert (
        "  - [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Failure Rollback" in markdown
    assert "- [ ] render_next_session_final_readiness_summary" in markdown
    assert "## Post-Completion Review" in markdown
    assert "- [ ] confirm_formal_evidence_delta_zero" in markdown
    assert "Next-session manual execution launch runbook is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_checks_runbook_coverage(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert audit.audit_scope == "manual_application_next_session_launch_runbook_audit"
    assert audit.audit_status == "runbook_audit_ready"
    assert audit.runbook_status == "ready_for_manual_execution_runbook"
    assert audit.seal_status == "sealed_for_manual_execution"
    assert audit.start_gate == "start_with_first_action"
    assert audit.first_step == "execute_apply_correction_queue_first"
    assert audit.coverage_checks == {
        "seal_status_to_runbook": "covered",
        "start_gate_preserved": "covered",
        "first_step_matches_sealed_first_command": "covered",
        "execution_order_starts_with_first_step": "covered",
        "execution_order_covers_sealed_candidate_order": "covered",
        "verification_commands_covered": "covered",
        "failure_rollback_covers_rollback_entrypoints": "covered",
        "post_completion_review_present": "covered",
        "target_candidates_preserved": "covered",
        "read_only_boundary_preserved": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == [
        "applied_review_decision_delta_zero",
        "applied_candidate_status_delta_zero",
        "formal_evidence_delta_zero",
    ]
    assert audit.candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.verification_commands == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
    ]
    assert audit.failure_rollback == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.first_step == "execute_close_verified_candidate_session_items"
    assert audit.execution_order[0] == "execute_close_verified_candidate_session_items"
    assert audit.candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert audit.coverage_checks["first_step_matches_sealed_first_command"] == "covered"
    assert audit.audit_status == "runbook_audit_ready"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Runbook Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_launch_runbook_audit`" in markdown
    assert "- Audit status: `runbook_audit_ready`" in markdown
    assert "- Runbook status: `ready_for_manual_execution_runbook`" in markdown
    assert "- First step: `execute_apply_correction_queue_first`" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `first_step_matches_sealed_first_command`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No missing runbook coverage." in markdown
    assert "## Candidate Order" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Failure Rollback" in markdown
    assert "- [ ] render_next_session_final_readiness_summary" in markdown
    assert "## Post-Completion Review" in markdown
    assert "- [ ] confirm_formal_evidence_delta_zero" in markdown
    assert "Next-session manual execution launch runbook audit is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_freezes_ready_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert seal.seal_scope == "manual_application_next_session_launch_runbook_audit_seal"
    assert seal.seal_status == "sealed_for_manual_execution_runbook_audit"
    assert seal.audit_status == "runbook_audit_ready"
    assert seal.runbook_status == "ready_for_manual_execution_runbook"
    assert seal.launch_seal_status == "sealed_for_manual_execution"
    assert seal.start_gate == "start_with_first_action"
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.blocked_reasons == []
    assert seal.seal_checks == [
        "confirm_runbook_audit_ready",
        "confirm_runbook_coverage_complete",
        "confirm_first_step_sealed",
        "confirm_verification_commands_present",
        "confirm_failure_rollback_present",
        "confirm_post_completion_review_present",
        "confirm_boundary_delta_zero",
    ]
    assert seal.verification_commands == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
    ]
    assert seal.rollback_entrypoints == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert seal.seal_status == "sealed_for_manual_execution_runbook_audit"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Runbook Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_launch_runbook_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_runbook_audit`" in markdown
    assert "- Audit status: `runbook_audit_ready`" in markdown
    assert "- Runbook status: `ready_for_manual_execution_runbook`" in markdown
    assert "- Sealed first step: `execute_apply_correction_queue_first`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_runbook_audit_ready" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No runbook audit seal blockers." in markdown
    assert "## Verification Commands" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Rollback Entrypoints" in markdown
    assert "- [ ] render_next_session_final_readiness_summary" in markdown
    assert "## Post-Completion Review" in markdown
    assert "- [ ] confirm_formal_evidence_delta_zero" in markdown
    assert "Next-session manual execution launch runbook audit seal is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_compresses_audit_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert packet.launch_packet_scope == "manual_application_next_session_final_launch_packet"
    assert packet.launch_packet_status == "ready_for_final_manual_launch_packet"
    assert packet.audit_seal_status == "sealed_for_manual_execution_runbook_audit"
    assert packet.sealed_first_step == "execute_apply_correction_queue_first"
    assert packet.candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.operator_start_checklist == [
        "confirm_audit_seal_ready",
        "confirm_sealed_first_step",
        "confirm_candidate_order",
        "execute_sealed_first_step",
    ]
    assert packet.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert packet.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert packet.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert packet.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert packet.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert packet.candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert packet.launch_packet_status == "ready_for_final_manual_launch_packet"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Launch Packet\n"
    )
    assert "- Launch packet scope: `manual_application_next_session_final_launch_packet`" in markdown
    assert "- Launch packet status: `ready_for_final_manual_launch_packet`" in markdown
    assert "- Audit seal status: `sealed_for_manual_execution_runbook_audit`" in markdown
    assert "- Sealed first step: `execute_apply_correction_queue_first`" in markdown
    assert "## Operator Start Checklist" in markdown
    assert "- [ ] execute_sealed_first_step" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Rollback Path" in markdown
    assert "- [ ] render_next_session_final_readiness_summary" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "Next-session manual execution final launch packet is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_checks_packet_coverage(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert audit.handoff_audit_scope == "manual_application_next_session_final_launch_packet_handoff_audit"
    assert audit.handoff_readiness == "ready_for_operator_handoff"
    assert audit.launch_packet_status == "ready_for_final_manual_launch_packet"
    assert audit.audit_seal_status == "sealed_for_manual_execution_runbook_audit"
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.coverage_checks == {
        "launch_packet_ready": "covered",
        "audit_seal_status_preserved": "covered",
        "sealed_first_step_preserved": "covered",
        "candidate_order_preserved": "covered",
        "operator_start_checklist_complete": "covered",
        "verification_checklist_covers_commands": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "boundary_confirmation_complete": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.operator_safe_start_boundary == [
        "confirm_handoff_readiness",
        "confirm_launch_packet_ready",
        "confirm_audit_seal_status_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_candidate_order_preserved",
        "confirm_boundary_confirmation_before_execution",
    ]
    assert audit.candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.operator_start_checklist == [
        "confirm_audit_seal_ready",
        "confirm_sealed_first_step",
        "confirm_candidate_order",
        "execute_sealed_first_step",
    ]
    assert audit.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert audit.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert audit.candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert audit.handoff_readiness == "ready_for_operator_handoff"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit\n"
    )
    assert "- Handoff audit scope: `manual_application_next_session_final_launch_packet_handoff_audit`" in markdown
    assert "- Handoff readiness: `ready_for_operator_handoff`" in markdown
    assert "- Launch packet status: `ready_for_final_manual_launch_packet`" in markdown
    assert "- Audit seal status: `sealed_for_manual_execution_runbook_audit`" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `candidate_order_preserved`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No missing final launch packet handoff coverage." in markdown
    assert "## Operator-Safe Start Boundary" in markdown
    assert "- [ ] confirm_boundary_confirmation_before_execution" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "Next-session manual execution final launch packet handoff audit is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_freezes_go_decision(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert seal.seal_scope == "manual_application_next_session_final_launch_packet_handoff_audit_seal"
    assert seal.seal_status == "sealed_for_operator_manual_execution_go"
    assert seal.handoff_readiness == "ready_for_operator_handoff"
    assert seal.go_no_go_decision == "go_for_operator_manual_execution"
    assert seal.launch_packet_status == "ready_for_final_manual_launch_packet"
    assert seal.audit_seal_status == "sealed_for_manual_execution_runbook_audit"
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.blocked_reasons == []
    assert seal.seal_checks == [
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
    ]
    assert seal.operator_safe_start_boundary == [
        "confirm_handoff_readiness",
        "confirm_launch_packet_ready",
        "confirm_audit_seal_status_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_candidate_order_preserved",
        "confirm_boundary_confirmation_before_execution",
    ]
    assert seal.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert seal.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert seal.seal_status == "sealed_for_operator_manual_execution_go"
    assert seal.go_no_go_decision == "go_for_operator_manual_execution"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_final_launch_packet_handoff_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_operator_manual_execution_go`" in markdown
    assert "- Handoff readiness: `ready_for_operator_handoff`" in markdown
    assert "- Go/no-go decision: `go_for_operator_manual_execution`" in markdown
    assert "- Sealed first step: `execute_apply_correction_queue_first`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_go_no_go_decision_go" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No operator go/no-go seal blockers." in markdown
    assert "## Operator-Safe Start Boundary" in markdown
    assert "- [ ] confirm_boundary_confirmation_before_execution" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "Next-session manual execution final launch packet handoff audit seal is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_signs_ready_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    receipt = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert receipt.session_id == "pending_review_manual_application_session"
    assert receipt.receipt_scope == "manual_application_next_session_operator_go_no_go_seal_launch_receipt"
    assert receipt.receipt_status == "ready_for_operator_launch_receipt"
    assert receipt.seal_status == "sealed_for_operator_manual_execution_go"
    assert receipt.handoff_readiness == "ready_for_operator_handoff"
    assert receipt.go_no_go_decision == "go_for_operator_manual_execution"
    assert receipt.receipt_decision == "receipt_ready_to_start_manual_execution"
    assert receipt.signed_first_step == "execute_apply_correction_queue_first"
    assert receipt.signed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert receipt.operator_receipt_checklist == [
        "confirm_go_no_go_seal_ready",
        "confirm_receipt_decision",
        "confirm_signed_first_step",
        "confirm_signed_candidate_order",
        "confirm_pre_execution_confirmation",
    ]
    assert receipt.pre_execution_confirmation == [
        "confirm_no_review_decision_auto_write",
        "confirm_no_candidate_extract_auto_write",
        "confirm_no_promotion_auto_apply",
        "confirm_formal_evidence_unchanged",
        "confirm_operator_executes_manual_steps_only_after_receipt",
    ]
    assert receipt.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert receipt.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert receipt.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert receipt.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert receipt.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert receipt.blocked_reasons == []
    assert receipt.applied_review_decision_delta == 0
    assert receipt.applied_candidate_status_delta == 0
    assert receipt.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    receipt = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert receipt.signed_first_step == "execute_close_verified_candidate_session_items"
    assert receipt.signed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert receipt.receipt_status == "ready_for_operator_launch_receipt"
    assert receipt.receipt_decision == "receipt_ready_to_start_manual_execution"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Operator Go/No-Go Seal Launch Receipt\n"
    )
    assert "- Receipt scope: `manual_application_next_session_operator_go_no_go_seal_launch_receipt`" in markdown
    assert "- Receipt status: `ready_for_operator_launch_receipt`" in markdown
    assert "- Seal status: `sealed_for_operator_manual_execution_go`" in markdown
    assert "- Go/no-go decision: `go_for_operator_manual_execution`" in markdown
    assert "- Receipt decision: `receipt_ready_to_start_manual_execution`" in markdown
    assert "- Signed first step: `execute_apply_correction_queue_first`" in markdown
    assert "## Operator Receipt Checklist" in markdown
    assert "- [ ] confirm_pre_execution_confirmation" in markdown
    assert "## Pre-Execution Confirmation" in markdown
    assert "- [ ] confirm_operator_executes_manual_steps_only_after_receipt" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No operator launch receipt blockers." in markdown
    assert "## Signed Candidate Order" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "Next-session manual execution operator go/no-go seal launch receipt is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_checks_receipt_coverage(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert audit.boundary_audit_scope == "manual_application_next_session_launch_receipt_final_boundary_audit"
    assert audit.final_boundary_readiness == "ready_for_final_boundary_audit"
    assert audit.receipt_status == "ready_for_operator_launch_receipt"
    assert audit.seal_status == "sealed_for_operator_manual_execution_go"
    assert audit.go_no_go_decision == "go_for_operator_manual_execution"
    assert audit.receipt_decision == "receipt_ready_to_start_manual_execution"
    assert audit.signed_first_step == "execute_apply_correction_queue_first"
    assert audit.receipt_coverage_checks == {
        "receipt_ready": "covered",
        "seal_status_preserved": "covered",
        "go_no_go_decision_preserved": "covered",
        "receipt_decision_ready": "covered",
        "signed_first_step_preserved": "covered",
        "signed_candidate_order_preserved": "covered",
        "operator_receipt_checklist_complete": "covered",
        "pre_execution_confirmation_complete": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "boundary_confirmation_complete": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.final_boundary_confirmation == [
        "confirm_receipt_ready",
        "confirm_go_no_go_preserved",
        "confirm_signed_first_step_preserved",
        "confirm_pre_execution_boundary",
        "confirm_boundary_delta_zero",
        "confirm_receipt_read_only",
    ]
    assert audit.signed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.operator_receipt_checklist == [
        "confirm_go_no_go_seal_ready",
        "confirm_receipt_decision",
        "confirm_signed_first_step",
        "confirm_signed_candidate_order",
        "confirm_pre_execution_confirmation",
    ]
    assert audit.pre_execution_confirmation == [
        "confirm_no_review_decision_auto_write",
        "confirm_no_candidate_extract_auto_write",
        "confirm_no_promotion_auto_apply",
        "confirm_formal_evidence_unchanged",
        "confirm_operator_executes_manual_steps_only_after_receipt",
    ]
    assert audit.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert audit.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.blocked_reasons == []
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.signed_first_step == "execute_close_verified_candidate_session_items"
    assert audit.signed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert audit.final_boundary_readiness == "ready_for_final_boundary_audit"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit\n"
    )
    assert "- Boundary audit scope: `manual_application_next_session_launch_receipt_final_boundary_audit`" in markdown
    assert "- Final boundary readiness: `ready_for_final_boundary_audit`" in markdown
    assert "- Receipt status: `ready_for_operator_launch_receipt`" in markdown
    assert "- Receipt decision: `receipt_ready_to_start_manual_execution`" in markdown
    assert "- Signed first step: `execute_apply_correction_queue_first`" in markdown
    assert "## Receipt Coverage Checks" in markdown
    assert "- `signed_candidate_order_preserved`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No missing launch receipt boundary coverage." in markdown
    assert "## Final Boundary Confirmation" in markdown
    assert "- [ ] confirm_receipt_read_only" in markdown
    assert "## Pre-Execution Confirmation" in markdown
    assert "- [ ] confirm_operator_executes_manual_steps_only_after_receipt" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "Next-session manual execution launch receipt final boundary audit is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_freezes_ready_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert seal.seal_scope == "manual_application_next_session_launch_receipt_final_boundary_audit_seal"
    assert seal.seal_status == "sealed_for_launch_receipt_final_boundary"
    assert seal.final_boundary_readiness == "ready_for_final_boundary_audit"
    assert seal.receipt_status == "ready_for_operator_launch_receipt"
    assert seal.go_no_go_decision == "go_for_operator_manual_execution"
    assert seal.receipt_decision == "receipt_ready_to_start_manual_execution"
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.receipt_coverage_checks["receipt_ready"] == "covered"
    assert seal.receipt_coverage_checks["signed_candidate_order_preserved"] == "covered"
    assert seal.missing_coverage == []
    assert seal.blocked_reasons == []
    assert seal.seal_checks == [
        "confirm_final_boundary_readiness_ready",
        "confirm_receipt_coverage_complete",
        "confirm_receipt_ready",
        "confirm_go_no_go_decision_preserved",
        "confirm_signed_first_step_sealed",
        "confirm_final_boundary_confirmation_present",
        "confirm_pre_execution_confirmation_present",
        "confirm_verification_checklist_present",
        "confirm_boundary_delta_zero",
    ]
    assert seal.final_boundary_confirmation == [
        "confirm_receipt_ready",
        "confirm_go_no_go_preserved",
        "confirm_signed_first_step_preserved",
        "confirm_pre_execution_boundary",
        "confirm_boundary_delta_zero",
        "confirm_receipt_read_only",
    ]
    assert seal.pre_execution_confirmation == [
        "confirm_no_review_decision_auto_write",
        "confirm_no_candidate_extract_auto_write",
        "confirm_no_promotion_auto_apply",
        "confirm_formal_evidence_unchanged",
        "confirm_operator_executes_manual_steps_only_after_receipt",
    ]
    assert seal.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert seal.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert seal.seal_status == "sealed_for_launch_receipt_final_boundary"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_launch_receipt_final_boundary_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_launch_receipt_final_boundary`" in markdown
    assert "- Final boundary readiness: `ready_for_final_boundary_audit`" in markdown
    assert "- Receipt status: `ready_for_operator_launch_receipt`" in markdown
    assert "- Receipt decision: `receipt_ready_to_start_manual_execution`" in markdown
    assert "- Sealed first step: `execute_apply_correction_queue_first`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_receipt_coverage_complete" in markdown
    assert "## Receipt Coverage Checks" in markdown
    assert "- `receipt_ready`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No launch receipt final boundary seal blockers." in markdown
    assert "## Final Boundary Confirmation" in markdown
    assert "- [ ] confirm_receipt_read_only" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "Next-session manual execution launch receipt final boundary audit seal is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert packet.packet_scope == "manual_application_next_session_launch_receipt_final_boundary_audit_seal_operator_start_packet"
    assert packet.packet_status == "ready_for_operator_start_packet"
    assert packet.seal_status == "sealed_for_launch_receipt_final_boundary"
    assert packet.final_boundary_readiness == "ready_for_final_boundary_audit"
    assert packet.receipt_status == "ready_for_operator_launch_receipt"
    assert packet.go_no_go_decision == "go_for_operator_manual_execution"
    assert packet.receipt_decision == "receipt_ready_to_start_manual_execution"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.sealed_first_step == "execute_apply_correction_queue_first"
    assert packet.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.operator_start_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert packet.pre_execution_confirmation == [
        "confirm_no_review_decision_auto_write",
        "confirm_no_candidate_extract_auto_write",
        "confirm_no_promotion_auto_apply",
        "confirm_formal_evidence_unchanged",
        "confirm_operator_executes_manual_steps_only_after_receipt",
    ]
    assert packet.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert packet.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert packet.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert packet.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert packet.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.blocked_reasons == []
    assert packet.packet_checks == [
        "confirm_launch_receipt_final_boundary_audit_seal_ready",
        "confirm_start_authorization_ready",
        "confirm_sealed_first_step_ready",
        "confirm_operator_start_checklist_present",
        "confirm_verification_checklist_present",
        "confirm_rollback_path_present",
        "confirm_boundary_confirmation_present",
        "confirm_boundary_delta_zero",
    ]
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.packet_status == "ready_for_operator_start_packet"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert packet.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal Operator Start Packet\n"
    )
    assert "- Packet scope: `manual_application_next_session_launch_receipt_final_boundary_audit_seal_operator_start_packet`" in markdown
    assert "- Packet status: `ready_for_operator_start_packet`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "- Sealed first step: `execute_apply_correction_queue_first`" in markdown
    assert "## Operator Start Checklist" in markdown
    assert "- [ ] confirm_start_authorization" in markdown
    assert "## Sealed Candidate Order" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Blocked Reasons" in markdown
    assert "No operator start packet blockers." in markdown
    assert "Next-session manual execution operator start packet is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_operator_start_packet_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert audit.audit_scope == "manual_application_next_session_operator_start_packet_audit"
    assert audit.audit_status == "operator_start_packet_audit_ready"
    assert audit.packet_status == "ready_for_operator_start_packet"
    assert audit.seal_status == "sealed_for_launch_receipt_final_boundary"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.coverage_checks == {
        "packet_ready": "covered",
        "seal_status_preserved": "covered",
        "start_authorization_ready": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_start_checklist_complete": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == {
        "applied_review_decision_delta_zero": "covered",
        "applied_candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
        "operator_start_packet_read_only": "covered",
    }
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.operator_start_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert audit.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert audit.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.blocked_reasons == []
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_operator_start_packet_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.audit_status == "operator_start_packet_audit_ready"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert audit.coverage_checks["sealed_first_step_preserved"] == "covered"
    assert audit.coverage_checks["sealed_candidate_order_preserved"] == "covered"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_operator_start_packet_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Operator Start Packet Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_operator_start_packet_audit`" in markdown
    assert "- Audit status: `operator_start_packet_audit_ready`" in markdown
    assert "- Packet status: `ready_for_operator_start_packet`" in markdown
    assert "- Seal status: `sealed_for_launch_receipt_final_boundary`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `sealed_first_step_preserved`: `covered`" in markdown
    assert "- `operator_start_checklist_complete`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No missing operator start packet audit coverage." in markdown
    assert "## Boundary Checks" in markdown
    assert "- `formal_evidence_delta_zero`: `covered`" in markdown
    assert "## Operator Start Checklist" in markdown
    assert "- [ ] confirm_start_authorization" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "Next-session manual execution operator start packet audit is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_operator_start_packet_audit_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert seal.seal_scope == "manual_application_next_session_operator_start_packet_audit_seal"
    assert seal.seal_status == "sealed_for_operator_start_packet_audit"
    assert seal.audit_status == "operator_start_packet_audit_ready"
    assert seal.packet_status == "ready_for_operator_start_packet"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.blocked_reasons == []
    assert seal.seal_checks == [
        "confirm_operator_start_packet_audit_ready",
        "confirm_coverage_complete",
        "confirm_boundary_checks_complete",
        "confirm_start_authorization_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_operator_start_checklist_present",
        "confirm_verification_checklist_present",
        "confirm_boundary_delta_zero",
    ]
    assert seal.coverage_checks["packet_ready"] == "covered"
    assert seal.coverage_checks["sealed_candidate_order_preserved"] == "covered"
    assert seal.coverage_checks["blocked_reasons_preserved"] == "covered"
    assert seal.missing_coverage == []
    assert seal.boundary_checks == {
        "applied_review_decision_delta_zero": "covered",
        "applied_candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
        "operator_start_packet_read_only": "covered",
    }
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.operator_start_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert seal.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert seal.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_operator_start_packet_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert seal.seal_status == "sealed_for_operator_start_packet_audit"
    assert seal.audit_status == "operator_start_packet_audit_ready"
    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.coverage_checks["sealed_first_step_preserved"] == "covered"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_operator_start_packet_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Operator Start Packet Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_operator_start_packet_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_operator_start_packet_audit`" in markdown
    assert "- Audit status: `operator_start_packet_audit_ready`" in markdown
    assert "- Packet status: `ready_for_operator_start_packet`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_coverage_complete" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `boundary_confirmation_preserved`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No operator start packet audit seal blockers." in markdown
    assert "## Boundary Checks" in markdown
    assert "- `operator_start_packet_read_only`: `covered`" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "Next-session manual execution operator start packet audit seal is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    receipt = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert receipt.session_id == "pending_review_manual_application_session"
    assert receipt.receipt_scope == "manual_application_next_session_manual_execution_start_authorization_receipt"
    assert receipt.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert receipt.seal_status == "sealed_for_operator_start_packet_audit"
    assert receipt.audit_status == "operator_start_packet_audit_ready"
    assert receipt.packet_status == "ready_for_operator_start_packet"
    assert receipt.start_authorization == "authorized_to_start_manual_execution"
    assert receipt.sealed_first_step == "execute_apply_correction_queue_first"
    assert receipt.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert receipt.operator_start_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert receipt.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert receipt.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert receipt.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert receipt.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert receipt.blocked_reasons == []
    assert receipt.receipt_checks == [
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
    assert receipt.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert receipt.applied_review_decision_delta == 0
    assert receipt.applied_candidate_status_delta == 0
    assert receipt.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    receipt = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert receipt.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert receipt.start_authorization == "authorized_to_start_manual_execution"
    assert receipt.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert receipt.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Receipt\n"
    )
    assert "- Receipt scope: `manual_application_next_session_manual_execution_start_authorization_receipt`" in markdown
    assert "- Receipt status: `ready_for_manual_execution_start_authorization_receipt`" in markdown
    assert "- Seal status: `sealed_for_operator_start_packet_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "- Sealed first step: `execute_apply_correction_queue_first`" in markdown
    assert "## Receipt Checks" in markdown
    assert "- [ ] confirm_start_authorization" in markdown
    assert "## Sealed Candidate Order" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Blocked Reasons" in markdown
    assert "No start authorization receipt blockers." in markdown
    assert "Next-session manual execution start authorization receipt is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert audit.audit_scope == "manual_application_next_session_start_authorization_receipt_coverage_audit"
    assert audit.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert audit.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert audit.seal_status == "sealed_for_operator_start_packet_audit"
    assert audit.operator_start_packet_audit_status == "operator_start_packet_audit_ready"
    assert audit.packet_status == "ready_for_operator_start_packet"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.coverage_checks == {
        "receipt_ready": "covered",
        "seal_status_preserved": "covered",
        "operator_start_packet_audit_status_preserved": "covered",
        "packet_status_preserved": "covered",
        "start_authorization_preserved": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_start_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "receipt_checks_present": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == {
        "start_authorization_receipt_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.operator_start_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert audit.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert audit.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.blocked_reasons == []
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert audit.coverage_checks["sealed_first_step_preserved"] == "covered"
    assert audit.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_start_authorization_receipt_coverage_audit`" in markdown
    assert "- Coverage audit status: `start_authorization_receipt_coverage_audit_ready`" in markdown
    assert "- Receipt status: `ready_for_manual_execution_start_authorization_receipt`" in markdown
    assert "- Seal status: `sealed_for_operator_start_packet_audit`" in markdown
    assert "- Operator start packet audit status: `operator_start_packet_audit_ready`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `operator_start_packet_audit_status_preserved`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No start authorization receipt coverage gaps." in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_authorization_receipt_read_only`: `covered`" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "Next-session manual execution start authorization receipt coverage audit is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert seal.seal_scope == "manual_application_next_session_start_authorization_receipt_coverage_audit_seal"
    assert seal.seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert seal.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert seal.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert seal.operator_start_packet_audit_seal_status == "sealed_for_operator_start_packet_audit"
    assert seal.operator_start_packet_audit_status == "operator_start_packet_audit_ready"
    assert seal.packet_status == "ready_for_operator_start_packet"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.seal_checks == [
        "confirm_start_authorization_receipt_coverage_audit_ready",
        "confirm_receipt_ready",
        "confirm_coverage_complete",
        "confirm_boundary_checks_complete",
        "confirm_start_authorization_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_sealed_candidate_order_preserved",
        "confirm_boundary_delta_zero",
    ]
    assert seal.coverage_checks == {
        "receipt_ready": "covered",
        "seal_status_preserved": "covered",
        "operator_start_packet_audit_status_preserved": "covered",
        "packet_status_preserved": "covered",
        "start_authorization_preserved": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_start_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "receipt_checks_present": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert seal.missing_coverage == []
    assert seal.boundary_checks == {
        "start_authorization_receipt_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.operator_start_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert seal.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert seal.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.blocked_reasons == []
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert seal.seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert seal.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.coverage_checks["sealed_first_step_preserved"] == "covered"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_start_authorization_receipt_coverage_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_start_authorization_receipt_coverage_audit`" in markdown
    assert "- Coverage audit status: `start_authorization_receipt_coverage_audit_ready`" in markdown
    assert "- Receipt status: `ready_for_manual_execution_start_authorization_receipt`" in markdown
    assert "- Operator start packet audit seal status: `sealed_for_operator_start_packet_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_coverage_complete" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `operator_start_packet_audit_status_preserved`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No start authorization receipt coverage audit seal blockers." in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_authorization_receipt_read_only`: `covered`" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "Next-session manual execution start authorization receipt coverage audit seal is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert packet.packet_scope == "manual_application_next_session_manual_execution_authorization_packet"
    assert packet.packet_status == "ready_for_manual_execution_authorization_packet"
    assert packet.seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert packet.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert packet.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert packet.operator_start_packet_audit_status == "operator_start_packet_audit_ready"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.authorization_checks == [
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
    assert packet.sealed_first_step == "execute_apply_correction_queue_first"
    assert packet.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert packet.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert packet.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert packet.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert packet.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.blocked_reasons == []
    assert packet.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.packet_status == "ready_for_manual_execution_authorization_packet"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert packet.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet\n"
    )
    assert "- Packet scope: `manual_application_next_session_manual_execution_authorization_packet`" in markdown
    assert "- Packet status: `ready_for_manual_execution_authorization_packet`" in markdown
    assert "- Seal status: `sealed_for_start_authorization_receipt_coverage_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "- Sealed first step: `execute_apply_correction_queue_first`" in markdown
    assert "## Authorization Checks" in markdown
    assert "- [ ] confirm_start_authorization" in markdown
    assert "## Operator Authorization Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Sealed Candidate Order" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "## Blocked Reasons" in markdown
    assert "No manual execution authorization packet blockers." in markdown
    assert "Next-session manual execution authorization packet is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert audit.audit_scope == "manual_application_next_session_manual_execution_authorization_packet_coverage_audit"
    assert audit.audit_status == "manual_execution_authorization_packet_coverage_audit_ready"
    assert audit.packet_status == "ready_for_manual_execution_authorization_packet"
    assert audit.seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert audit.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert audit.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert audit.operator_start_packet_audit_status == "operator_start_packet_audit_ready"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.packet_coverage_checks == {
        "packet_ready": "covered",
        "seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "receipt_status_preserved": "covered",
        "operator_start_packet_audit_status_preserved": "covered",
        "start_authorization_preserved": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "authorization_checks_present": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == {
        "authorization_packet_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert audit.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert audit.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.blocked_reasons == []
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.audit_status == "manual_execution_authorization_packet_coverage_audit_ready"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert audit.packet_coverage_checks["sealed_first_step_preserved"] == "covered"
    assert audit.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_manual_execution_authorization_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_authorization_packet_coverage_audit_ready`" in markdown
    assert "- Packet status: `ready_for_manual_execution_authorization_packet`" in markdown
    assert "- Seal status: `sealed_for_start_authorization_receipt_coverage_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Packet Coverage Checks" in markdown
    assert "- `authorization_checks_present`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution authorization packet coverage gaps." in markdown
    assert "## Boundary Checks" in markdown
    assert "- `authorization_packet_read_only`: `covered`" in markdown
    assert "## Operator Authorization Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "Next-session manual execution authorization packet coverage audit is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert seal.seal_scope == "manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal"
    assert seal.seal_status == "sealed_for_manual_execution_authorization_packet_coverage_audit"
    assert seal.audit_status == "manual_execution_authorization_packet_coverage_audit_ready"
    assert seal.packet_status == "ready_for_manual_execution_authorization_packet"
    assert seal.authorization_packet_seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert seal.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert seal.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert seal.operator_start_packet_audit_status == "operator_start_packet_audit_ready"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.seal_checks == [
        "confirm_manual_execution_authorization_packet_coverage_audit_ready",
        "confirm_packet_ready",
        "confirm_coverage_complete",
        "confirm_boundary_checks_complete",
        "confirm_start_authorization_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_sealed_candidate_order_preserved",
        "confirm_boundary_delta_zero",
    ]
    assert seal.packet_coverage_checks == {
        "packet_ready": "covered",
        "seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "receipt_status_preserved": "covered",
        "operator_start_packet_audit_status_preserved": "covered",
        "start_authorization_preserved": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "authorization_checks_present": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert seal.missing_coverage == []
    assert seal.boundary_checks == {
        "authorization_packet_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert seal.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert seal.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.blocked_reasons == []
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert seal.seal_status == "sealed_for_manual_execution_authorization_packet_coverage_audit"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.packet_coverage_checks["sealed_first_step_preserved"] == "covered"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_authorization_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_authorization_packet_coverage_audit_ready`" in markdown
    assert "- Packet status: `ready_for_manual_execution_authorization_packet`" in markdown
    assert "- Authorization packet seal status: `sealed_for_start_authorization_receipt_coverage_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_coverage_complete" in markdown
    assert "## Packet Coverage Checks" in markdown
    assert "- `authorization_checks_present`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution authorization packet coverage audit seal blockers." in markdown
    assert "## Boundary Checks" in markdown
    assert "- `authorization_packet_read_only`: `covered`" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "Next-session manual execution authorization packet coverage audit seal is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    docket = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert docket.session_id == "pending_review_manual_application_session"
    assert docket.docket_scope == "manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket"
    assert docket.docket_status == "ready_for_manual_execution_start_docket"
    assert docket.seal_status == "sealed_for_manual_execution_authorization_packet_coverage_audit"
    assert docket.audit_status == "manual_execution_authorization_packet_coverage_audit_ready"
    assert docket.packet_status == "ready_for_manual_execution_authorization_packet"
    assert docket.authorization_packet_seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert docket.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert docket.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert docket.operator_start_packet_audit_status == "operator_start_packet_audit_ready"
    assert docket.start_authorization == "authorized_to_start_manual_execution"
    assert docket.docket_checks == [
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
    ]
    assert docket.sealed_first_step == "execute_apply_correction_queue_first"
    assert docket.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert docket.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert docket.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert docket.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert docket.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert docket.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert docket.blocked_reasons == []
    assert docket.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert docket.applied_review_decision_delta == 0
    assert docket.applied_candidate_status_delta == 0
    assert docket.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    docket = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert docket.docket_status == "ready_for_manual_execution_start_docket"
    assert docket.start_authorization == "authorized_to_start_manual_execution"
    assert docket.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert docket.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit Seal Start Docket\n"
    )
    assert "- Docket scope: `manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket`" in markdown
    assert "- Docket status: `ready_for_manual_execution_start_docket`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_authorization_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_authorization_packet_coverage_audit_ready`" in markdown
    assert "- Packet status: `ready_for_manual_execution_authorization_packet`" in markdown
    assert "- Authorization packet seal status: `sealed_for_start_authorization_receipt_coverage_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Docket Checks" in markdown
    assert "- [ ] confirm_authorization_packet_coverage_audit_seal_ready" in markdown
    assert "## Operator Authorization Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Sealed Candidate Order" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start docket blockers." in markdown
    assert "Next-session manual execution start docket is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert audit.audit_scope == "manual_application_next_session_manual_execution_start_docket_coverage_audit"
    assert audit.audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert audit.docket_status == "ready_for_manual_execution_start_docket"
    assert audit.seal_status == "sealed_for_manual_execution_authorization_packet_coverage_audit"
    assert audit.authorization_packet_seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert audit.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert audit.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert audit.operator_start_packet_audit_status == "operator_start_packet_audit_ready"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.docket_coverage_checks == {
        "docket_ready": "covered",
        "seal_status_preserved": "covered",
        "audit_status_preserved": "covered",
        "packet_status_preserved": "covered",
        "authorization_packet_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "receipt_status_preserved": "covered",
        "operator_start_packet_audit_status_preserved": "covered",
        "start_authorization_preserved": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "docket_checks_present": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == {
        "start_docket_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert audit.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert audit.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.blocked_reasons == []
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert audit.docket_coverage_checks["sealed_first_step_preserved"] == "covered"
    assert audit.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_manual_execution_start_docket_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_docket_coverage_audit_ready`" in markdown
    assert "- Docket status: `ready_for_manual_execution_start_docket`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_authorization_packet_coverage_audit`" in markdown
    assert "- Authorization packet seal status: `sealed_for_start_authorization_receipt_coverage_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Docket Coverage Checks" in markdown
    assert "- `docket_checks_present`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start docket coverage gaps." in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_docket_read_only`: `covered`" in markdown
    assert "## Operator Authorization Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Verification Checklist" in markdown
    assert (
        "- [ ] `uv run --with pytest python -m pytest tests/unit/test_source_intake.py`"
        in markdown
    )
    assert "Next-session manual execution start docket coverage audit is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert seal.seal_scope == "manual_application_next_session_manual_execution_start_docket_coverage_audit_seal"
    assert seal.seal_status == "sealed_for_manual_execution_start_docket_coverage_audit"
    assert seal.audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert seal.docket_status == "ready_for_manual_execution_start_docket"
    assert seal.source_seal_status == "sealed_for_manual_execution_authorization_packet_coverage_audit"
    assert seal.audit_source_status == "manual_execution_authorization_packet_coverage_audit_ready"
    assert seal.packet_status == "ready_for_manual_execution_authorization_packet"
    assert seal.authorization_packet_seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert seal.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert seal.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert seal.operator_start_packet_audit_status == "operator_start_packet_audit_ready"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.seal_checks == [
        "confirm_manual_execution_start_docket_coverage_audit_ready",
        "confirm_start_docket_ready",
        "confirm_coverage_complete",
        "confirm_boundary_checks_complete",
        "confirm_start_authorization_preserved",
        "confirm_sealed_first_step_preserved",
        "confirm_sealed_candidate_order_preserved",
        "confirm_boundary_delta_zero",
    ]
    assert seal.docket_coverage_checks == {
        "docket_ready": "covered",
        "seal_status_preserved": "covered",
        "audit_status_preserved": "covered",
        "packet_status_preserved": "covered",
        "authorization_packet_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "receipt_status_preserved": "covered",
        "operator_start_packet_audit_status_preserved": "covered",
        "start_authorization_preserved": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "docket_checks_present": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert seal.missing_coverage == []
    assert seal.boundary_checks == {
        "start_docket_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert seal.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert seal.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.blocked_reasons == []
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert seal.seal_status == "sealed_for_manual_execution_start_docket_coverage_audit"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.docket_coverage_checks["sealed_first_step_preserved"] == "covered"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_manual_execution_start_docket_coverage_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_docket_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_docket_coverage_audit_ready`" in markdown
    assert "- Docket status: `ready_for_manual_execution_start_docket`" in markdown
    assert "- Source seal status: `sealed_for_manual_execution_authorization_packet_coverage_audit`" in markdown
    assert "- Audit source status: `manual_execution_authorization_packet_coverage_audit_ready`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_manual_execution_start_docket_coverage_audit_ready" in markdown
    assert "## Docket Coverage Checks" in markdown
    assert "- `docket_checks_present`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start docket coverage audit seal blockers." in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_docket_read_only`: `covered`" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "Next-session manual execution start docket coverage audit seal is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert packet.packet_scope == "manual_application_next_session_manual_execution_final_start_packet"
    assert packet.packet_status == "ready_for_manual_execution_final_start_packet"
    assert packet.seal_status == "sealed_for_manual_execution_start_docket_coverage_audit"
    assert packet.audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert packet.docket_status == "ready_for_manual_execution_start_docket"
    assert packet.source_seal_status == "sealed_for_manual_execution_authorization_packet_coverage_audit"
    assert packet.audit_source_status == "manual_execution_authorization_packet_coverage_audit_ready"
    assert packet.packet_source_status == "ready_for_manual_execution_authorization_packet"
    assert packet.authorization_packet_seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert packet.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert packet.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert packet.operator_start_packet_audit_status == "operator_start_packet_audit_ready"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.packet_checks == [
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
    assert packet.sealed_first_step == "execute_apply_correction_queue_first"
    assert packet.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert packet.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert packet.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert packet.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert packet.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.blocked_reasons == []
    assert packet.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.packet_status == "ready_for_manual_execution_final_start_packet"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert packet.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Start Packet\n"
    )
    assert "- Packet scope: `manual_application_next_session_manual_execution_final_start_packet`" in markdown
    assert "- Packet status: `ready_for_manual_execution_final_start_packet`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_docket_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_docket_coverage_audit_ready`" in markdown
    assert "- Docket status: `ready_for_manual_execution_start_docket`" in markdown
    assert "- Source seal status: `sealed_for_manual_execution_authorization_packet_coverage_audit`" in markdown
    assert "- Audit source status: `manual_execution_authorization_packet_coverage_audit_ready`" in markdown
    assert "- Packet source status: `ready_for_manual_execution_authorization_packet`" in markdown
    assert "- Authorization packet seal status: `sealed_for_start_authorization_receipt_coverage_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Packet Checks" in markdown
    assert "- [ ] confirm_start_docket_coverage_audit_seal_ready" in markdown
    assert "## Operator Authorization Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Sealed Candidate Order" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution final start packet blockers." in markdown
    assert "Next-session manual execution final start packet is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_checks_packet_coverage(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert audit.handoff_audit_scope == "manual_application_next_session_manual_execution_final_start_packet_handoff_audit"
    assert audit.handoff_readiness == "ready_for_manual_execution_final_start_packet_handoff"
    assert audit.packet_status == "ready_for_manual_execution_final_start_packet"
    assert audit.seal_status == "sealed_for_manual_execution_start_docket_coverage_audit"
    assert audit.audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert audit.docket_status == "ready_for_manual_execution_start_docket"
    assert audit.source_seal_status == "sealed_for_manual_execution_authorization_packet_coverage_audit"
    assert audit.audit_source_status == "manual_execution_authorization_packet_coverage_audit_ready"
    assert audit.packet_source_status == "ready_for_manual_execution_authorization_packet"
    assert audit.authorization_packet_seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert audit.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert audit.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert audit.operator_start_packet_audit_status == "operator_start_packet_audit_ready"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.coverage_checks == {
        "final_start_packet_ready": "covered",
        "start_docket_coverage_audit_seal_status_preserved": "covered",
        "audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "start_authorization_preserved": "covered",
        "packet_checks_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_complete": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == {
        "final_start_packet_handoff_audit_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert audit.operator_safe_start_boundary == [
        "confirm_final_start_packet_ready",
        "confirm_start_docket_coverage_audit_seal_preserved",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_boundary_confirmation_before_execution",
    ]
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert audit.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert audit.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.blocked_reasons == []
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.handoff_readiness == "ready_for_manual_execution_final_start_packet_handoff"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert audit.coverage_checks["sealed_first_step_preserved"] == "covered"
    assert audit.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit\n"
    )
    assert "- Handoff audit scope: `manual_application_next_session_manual_execution_final_start_packet_handoff_audit`" in markdown
    assert "- Handoff readiness: `ready_for_manual_execution_final_start_packet_handoff`" in markdown
    assert "- Packet status: `ready_for_manual_execution_final_start_packet`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_docket_coverage_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `final_start_packet_ready`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution final start packet handoff coverage gaps." in markdown
    assert "## Boundary Checks" in markdown
    assert "- `final_start_packet_handoff_audit_read_only`: `covered`" in markdown
    assert "## Operator-Safe Start Boundary" in markdown
    assert "- [ ] confirm_boundary_confirmation_before_execution" in markdown
    assert "## Operator Authorization Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Sealed Candidate Order" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution final start packet handoff blockers." in markdown
    assert "Next-session manual execution final start packet handoff audit is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_freezes_start_decision(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert seal.seal_scope == "manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal"
    assert seal.seal_status == "sealed_for_manual_execution_final_start_packet_handoff"
    assert seal.handoff_readiness == "ready_for_manual_execution_final_start_packet_handoff"
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.packet_status == "ready_for_manual_execution_final_start_packet"
    assert seal.seal_source_status == "sealed_for_manual_execution_start_docket_coverage_audit"
    assert seal.audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert seal.docket_status == "ready_for_manual_execution_start_docket"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.seal_checks == [
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
    ]
    assert seal.coverage_checks == {
        "final_start_packet_ready": "covered",
        "start_docket_coverage_audit_seal_status_preserved": "covered",
        "audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "start_authorization_preserved": "covered",
        "packet_checks_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_complete": "covered",
        "boundary_delta_zero": "covered",
    }
    assert seal.missing_coverage == []
    assert seal.boundary_checks == {
        "final_start_packet_handoff_audit_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert seal.operator_safe_start_boundary == [
        "confirm_final_start_packet_ready",
        "confirm_start_docket_coverage_audit_seal_preserved",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_boundary_confirmation_before_execution",
    ]
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert seal.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert seal.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.blocked_reasons == []
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert seal.seal_status == "sealed_for_manual_execution_final_start_packet_handoff"
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.coverage_checks["sealed_first_step_preserved"] == "covered"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_final_start_packet_handoff`" in markdown
    assert "- Handoff readiness: `ready_for_manual_execution_final_start_packet_handoff`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Packet status: `ready_for_manual_execution_final_start_packet`" in markdown
    assert "- Seal source status: `sealed_for_manual_execution_start_docket_coverage_audit`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_go_no_go_start_decision_go" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `final_start_packet_ready`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `final_start_packet_handoff_audit_read_only`: `covered`" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution final start packet handoff audit seal blockers." in markdown
    assert "## Operator-Safe Start Boundary" in markdown
    assert "- [ ] confirm_boundary_confirmation_before_execution" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "Next-session manual execution final start packet handoff audit seal is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert packet.packet_scope == "manual_application_next_session_manual_execution_start_authorization_packet"
    assert packet.packet_status == "ready_for_manual_execution_start_authorization_packet"
    assert packet.seal_status == "sealed_for_manual_execution_final_start_packet_handoff"
    assert packet.handoff_readiness == "ready_for_manual_execution_final_start_packet_handoff"
    assert packet.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert packet.docket_status == "ready_for_manual_execution_start_docket"
    assert packet.authorization_checklist == [
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
    ]
    assert packet.sealed_first_step == "execute_apply_correction_queue_first"
    assert packet.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert packet.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert packet.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert packet.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert packet.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.blocked_reasons == []
    assert packet.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.packet_status == "ready_for_manual_execution_start_authorization_packet"
    assert packet.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert packet.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Packet\n"
    )
    assert "- Packet scope: `manual_application_next_session_manual_execution_start_authorization_packet`" in markdown
    assert "- Packet status: `ready_for_manual_execution_start_authorization_packet`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_final_start_packet_handoff`" in markdown
    assert "- Handoff readiness: `ready_for_manual_execution_final_start_packet_handoff`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Authorization Checklist" in markdown
    assert "- [ ] confirm_final_start_packet_handoff_audit_seal_ready" in markdown
    assert "## Operator Authorization Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Sealed Candidate Order" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start authorization packet blockers." in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "Next-session manual execution start authorization packet is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert (
        audit.audit_scope
        == "manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert (
        audit.audit_status
        == "manual_execution_start_authorization_packet_coverage_audit_ready"
    )
    assert (
        audit.packet_status
        == "ready_for_manual_execution_start_authorization_packet"
    )
    assert audit.seal_status == "sealed_for_manual_execution_final_start_packet_handoff"
    assert (
        audit.handoff_readiness
        == "ready_for_manual_execution_final_start_packet_handoff"
    )
    assert audit.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.source_audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert audit.docket_status == "ready_for_manual_execution_start_docket"
    assert audit.packet_coverage_checks == {
        "start_authorization_packet_ready": "covered",
        "final_start_packet_handoff_audit_seal_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "authorization_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == {
        "start_authorization_packet_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert audit.authorization_checklist == [
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
    ]
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert audit.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert audit.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.blocked_reasons == []
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert (
        audit.audit_status
        == "manual_execution_start_authorization_packet_coverage_audit_ready"
    )
    assert audit.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert audit.packet_coverage_checks["sealed_first_step_preserved"] == "covered"
    assert audit.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_authorization_packet_coverage_audit_ready`" in markdown
    assert "- Packet status: `ready_for_manual_execution_start_authorization_packet`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_final_start_packet_handoff`" in markdown
    assert "- Handoff readiness: `ready_for_manual_execution_final_start_packet_handoff`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Packet Coverage Checks" in markdown
    assert "- `start_authorization_packet_ready`: `covered`" in markdown
    assert "- `authorization_checklist_complete`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_authorization_packet_coverage_audit_read_only`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start authorization packet coverage gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start authorization packet coverage audit blockers." in markdown
    assert "## Authorization Checklist" in markdown
    assert "- [ ] confirm_boundary_delta_zero" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "Next-session manual execution start authorization packet coverage audit is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert (
        seal.seal_scope
        == "manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal"
    )
    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert (
        seal.audit_status
        == "manual_execution_start_authorization_packet_coverage_audit_ready"
    )
    assert (
        seal.packet_status
        == "ready_for_manual_execution_start_authorization_packet"
    )
    assert seal.seal_source_status == "sealed_for_manual_execution_final_start_packet_handoff"
    assert (
        seal.handoff_readiness
        == "ready_for_manual_execution_final_start_packet_handoff"
    )
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.source_audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert seal.docket_status == "ready_for_manual_execution_start_docket"
    assert seal.seal_checks == [
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
    ]
    assert seal.packet_coverage_checks == {
        "start_authorization_packet_ready": "covered",
        "final_start_packet_handoff_audit_seal_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "authorization_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert seal.missing_coverage == []
    assert seal.boundary_checks == {
        "start_authorization_packet_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert seal.authorization_checklist == [
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
    ]
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert seal.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert seal.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.blocked_reasons == []
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.packet_coverage_checks["sealed_first_step_preserved"] == "covered"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_authorization_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_authorization_packet_coverage_audit_ready`" in markdown
    assert "- Packet status: `ready_for_manual_execution_start_authorization_packet`" in markdown
    assert "- Seal source status: `sealed_for_manual_execution_final_start_packet_handoff`" in markdown
    assert "- Handoff readiness: `ready_for_manual_execution_final_start_packet_handoff`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_manual_execution_start_authorization_packet_coverage_audit_ready" in markdown
    assert "## Packet Coverage Checks" in markdown
    assert "- `start_authorization_packet_ready`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_authorization_packet_coverage_audit_read_only`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start authorization packet coverage audit seal gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start authorization packet coverage audit seal blockers." in markdown
    assert "## Authorization Checklist" in markdown
    assert "- [ ] confirm_boundary_delta_zero" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert "Next-session manual execution start authorization packet coverage audit seal is read-only planning metadata." in markdown


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert (
        packet.packet_scope
        == "manual_application_next_session_manual_execution_start_clearance_packet"
    )
    assert packet.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        packet.seal_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert (
        packet.audit_status
        == "manual_execution_start_authorization_packet_coverage_audit_ready"
    )
    assert (
        packet.packet_source_status
        == "ready_for_manual_execution_start_authorization_packet"
    )
    assert (
        packet.handoff_readiness
        == "ready_for_manual_execution_final_start_packet_handoff"
    )
    assert packet.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert (
        packet.source_audit_status
        == "manual_execution_start_docket_coverage_audit_ready"
    )
    assert packet.docket_status == "ready_for_manual_execution_start_docket"
    assert packet.clearance_checklist == [
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
    ]
    assert packet.sealed_first_step == "execute_apply_correction_queue_first"
    assert packet.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert packet.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert packet.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert packet.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert packet.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.blocked_reasons == []
    assert packet.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert packet.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert (
        packet.sealed_first_step
        == "execute_close_verified_candidate_session_items"
    )
    assert (
        packet.sealed_candidate_order[0]
        == "candidate_duan_ten_god_relation_017_001"
    )


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet\n"
    )
    assert "- Packet scope: `manual_application_next_session_manual_execution_start_clearance_packet`" in markdown
    assert "- Packet status: `ready_for_manual_execution_start_clearance_packet`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_authorization_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_authorization_packet_coverage_audit_ready`" in markdown
    assert "- Packet source status: `ready_for_manual_execution_start_authorization_packet`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Clearance Checklist" in markdown
    assert "- [ ] confirm_start_clearance_packet_ready" in markdown
    assert "## Operator Authorization Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Sealed Candidate Order" in markdown
    assert "1. `candidate_duan_ten_god_relation_017_001`" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start clearance packet blockers." in markdown
    assert (
        "Next-session manual execution start clearance packet is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert (
        audit.audit_scope
        == "manual_application_next_session_manual_execution_start_clearance_packet_coverage_audit"
    )
    assert (
        audit.audit_status
        == "manual_execution_start_clearance_packet_coverage_audit_ready"
    )
    assert audit.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        audit.seal_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert (
        audit.packet_source_status
        == "ready_for_manual_execution_start_authorization_packet"
    )
    assert (
        audit.handoff_readiness
        == "ready_for_manual_execution_final_start_packet_handoff"
    )
    assert audit.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert (
        audit.source_audit_status
        == "manual_execution_start_docket_coverage_audit_ready"
    )
    assert audit.docket_status == "ready_for_manual_execution_start_docket"
    assert audit.packet_coverage_checks == {
        "start_clearance_packet_ready": "covered",
        "coverage_audit_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "clearance_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == {
        "start_clearance_packet_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert audit.clearance_checklist == [
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
    ]
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert audit.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert audit.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.blocked_reasons == []
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert (
        audit.audit_status
        == "manual_execution_start_clearance_packet_coverage_audit_ready"
    )
    assert audit.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert (
        audit.sealed_first_step
        == "execute_close_verified_candidate_session_items"
    )
    assert audit.packet_coverage_checks["sealed_first_step_preserved"] == "covered"
    assert (
        audit.sealed_candidate_order[0]
        == "candidate_duan_ten_god_relation_017_001"
    )


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_manual_execution_start_clearance_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_clearance_packet_coverage_audit_ready`" in markdown
    assert "- Packet status: `ready_for_manual_execution_start_clearance_packet`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_authorization_packet_coverage_audit`" in markdown
    assert "- Packet source status: `ready_for_manual_execution_start_authorization_packet`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Packet Coverage Checks" in markdown
    assert "- `start_clearance_packet_ready`: `covered`" in markdown
    assert "- `clearance_checklist_complete`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_clearance_packet_coverage_audit_read_only`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start clearance packet coverage gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start clearance packet coverage audit blockers." in markdown
    assert "## Clearance Checklist" in markdown
    assert "- [ ] confirm_start_clearance_packet_ready" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert (
        "Next-session manual execution start clearance packet coverage audit is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert (
        seal.seal_scope
        == "manual_application_next_session_manual_execution_start_clearance_packet_coverage_audit_seal"
    )
    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_clearance_packet_coverage_audit"
    )
    assert (
        seal.audit_status
        == "manual_execution_start_clearance_packet_coverage_audit_ready"
    )
    assert seal.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        seal.seal_source_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert (
        seal.packet_source_status
        == "ready_for_manual_execution_start_authorization_packet"
    )
    assert (
        seal.handoff_readiness
        == "ready_for_manual_execution_final_start_packet_handoff"
    )
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert (
        seal.source_audit_status
        == "manual_execution_start_docket_coverage_audit_ready"
    )
    assert seal.docket_status == "ready_for_manual_execution_start_docket"
    assert seal.seal_checks == [
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
    ]
    assert seal.packet_coverage_checks == {
        "start_clearance_packet_ready": "covered",
        "coverage_audit_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "clearance_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert seal.missing_coverage == []
    assert seal.boundary_checks == {
        "start_clearance_packet_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert seal.clearance_checklist == [
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
    ]
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert seal.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert seal.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.blocked_reasons == []
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_clearance_packet_coverage_audit"
    )
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert (
        seal.sealed_first_step
        == "execute_close_verified_candidate_session_items"
    )
    assert seal.packet_coverage_checks["sealed_first_step_preserved"] == "covered"
    assert (
        seal.sealed_candidate_order[0]
        == "candidate_duan_ten_god_relation_017_001"
    )


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_manual_execution_start_clearance_packet_coverage_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_clearance_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_clearance_packet_coverage_audit_ready`" in markdown
    assert "- Packet status: `ready_for_manual_execution_start_clearance_packet`" in markdown
    assert "- Seal source status: `sealed_for_manual_execution_start_authorization_packet_coverage_audit`" in markdown
    assert "- Packet source status: `ready_for_manual_execution_start_authorization_packet`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_manual_execution_start_clearance_packet_coverage_audit_ready" in markdown
    assert "## Packet Coverage Checks" in markdown
    assert "- `start_clearance_packet_ready`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_clearance_packet_coverage_audit_read_only`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start clearance packet coverage audit seal gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start clearance packet coverage audit seal blockers." in markdown
    assert "## Clearance Checklist" in markdown
    assert "- [ ] confirm_start_clearance_packet_ready" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert (
        "Next-session manual execution start clearance packet coverage audit seal is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    authorization = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert authorization.session_id == "pending_review_manual_application_session"
    assert (
        authorization.authorization_scope
        == "manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization"
    )
    assert (
        authorization.authorization_status
        == "authorized_for_manual_execution_start_from_clearance_packet"
    )
    assert (
        authorization.seal_status
        == "sealed_for_manual_execution_start_clearance_packet_coverage_audit"
    )
    assert (
        authorization.audit_status
        == "manual_execution_start_clearance_packet_coverage_audit_ready"
    )
    assert authorization.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        authorization.seal_source_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert (
        authorization.packet_source_status
        == "ready_for_manual_execution_start_authorization_packet"
    )
    assert (
        authorization.handoff_readiness
        == "ready_for_manual_execution_final_start_packet_handoff"
    )
    assert authorization.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert authorization.start_authorization == "authorized_to_start_manual_execution"
    assert (
        authorization.source_audit_status
        == "manual_execution_start_docket_coverage_audit_ready"
    )
    assert authorization.docket_status == "ready_for_manual_execution_start_docket"
    assert authorization.authorization_checks == [
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
    ]
    assert authorization.seal_checks == [
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
    ]
    assert authorization.packet_coverage_checks == {
        "start_clearance_packet_ready": "covered",
        "coverage_audit_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "clearance_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert authorization.missing_coverage == []
    assert authorization.boundary_checks == {
        "start_clearance_packet_final_start_authorization_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert authorization.clearance_checklist == [
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
    ]
    assert authorization.sealed_first_step == "execute_apply_correction_queue_first"
    assert authorization.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert authorization.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert authorization.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert authorization.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert authorization.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert authorization.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert authorization.blocked_reasons == []
    assert authorization.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert authorization.applied_review_decision_delta == 0
    assert authorization.applied_candidate_status_delta == 0
    assert authorization.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    authorization = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert (
        authorization.authorization_status
        == "authorized_for_manual_execution_start_from_clearance_packet"
    )
    assert authorization.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert authorization.start_authorization == "authorized_to_start_manual_execution"
    assert (
        authorization.sealed_first_step
        == "execute_close_verified_candidate_session_items"
    )
    assert (
        authorization.packet_coverage_checks["sealed_first_step_preserved"]
        == "covered"
    )
    assert (
        authorization.sealed_candidate_order[0]
        == "candidate_duan_ten_god_relation_017_001"
    )


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization\n"
    )
    assert "- Authorization scope: `manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization`" in markdown
    assert "- Authorization status: `authorized_for_manual_execution_start_from_clearance_packet`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_clearance_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_clearance_packet_coverage_audit_ready`" in markdown
    assert "- Packet status: `ready_for_manual_execution_start_clearance_packet`" in markdown
    assert "- Seal source status: `sealed_for_manual_execution_start_authorization_packet_coverage_audit`" in markdown
    assert "- Packet source status: `ready_for_manual_execution_start_authorization_packet`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Authorization Checks" in markdown
    assert "- [ ] confirm_start_clearance_packet_coverage_audit_seal_ready" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_manual_execution_start_clearance_packet_coverage_audit_ready" in markdown
    assert "## Packet Coverage Checks" in markdown
    assert "- `start_clearance_packet_ready`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_clearance_packet_final_start_authorization_read_only`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start clearance packet final start authorization gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start clearance packet final start authorization blockers." in markdown
    assert "## Clearance Checklist" in markdown
    assert "- [ ] confirm_start_clearance_packet_ready" in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert (
        "Next-session manual execution start clearance packet final start authorization is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert (
        audit.audit_scope
        == "manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"
    )
    assert (
        audit.audit_status
        == "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert (
        audit.authorization_status
        == "authorized_for_manual_execution_start_from_clearance_packet"
    )
    assert (
        audit.seal_status
        == "sealed_for_manual_execution_start_clearance_packet_coverage_audit"
    )
    assert audit.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        audit.seal_source_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert (
        audit.packet_source_status
        == "ready_for_manual_execution_start_authorization_packet"
    )
    assert (
        audit.handoff_readiness
        == "ready_for_manual_execution_final_start_packet_handoff"
    )
    assert audit.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert (
        audit.source_audit_status
        == "manual_execution_start_docket_coverage_audit_ready"
    )
    assert audit.docket_status == "ready_for_manual_execution_start_docket"
    assert audit.authorization_coverage_checks == {
        "final_start_authorization_ready": "covered",
        "coverage_audit_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "packet_status_preserved": "covered",
        "seal_source_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "authorization_checks_complete": "covered",
        "seal_checks_complete": "covered",
        "packet_coverage_checks_complete": "covered",
        "boundary_checks_complete": "covered",
        "clearance_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.authorization_checks == [
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
    ]
    assert audit.seal_checks == [
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
    ]
    assert audit.packet_coverage_checks == {
        "start_clearance_packet_ready": "covered",
        "coverage_audit_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "clearance_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == {
        "start_clearance_packet_final_start_authorization_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert audit.clearance_checklist == [
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
    ]
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert audit.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert audit.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert audit.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert audit.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert audit.blocked_reasons == []
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert (
        audit.audit_status
        == "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert audit.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert (
        audit.sealed_first_step
        == "execute_close_verified_candidate_session_items"
    )
    assert (
        audit.authorization_coverage_checks["sealed_first_step_preserved"]
        == "covered"
    )
    assert (
        audit.sealed_candidate_order[0]
        == "candidate_duan_ten_god_relation_017_001"
    )


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`" in markdown
    assert "- Authorization status: `authorized_for_manual_execution_start_from_clearance_packet`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_clearance_packet_coverage_audit`" in markdown
    assert "- Packet status: `ready_for_manual_execution_start_clearance_packet`" in markdown
    assert "- Seal source status: `sealed_for_manual_execution_start_authorization_packet_coverage_audit`" in markdown
    assert "- Packet source status: `ready_for_manual_execution_start_authorization_packet`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Authorization Coverage Checks" in markdown
    assert "- `final_start_authorization_ready`: `covered`" in markdown
    assert "- `authorization_checks_complete`: `covered`" in markdown
    assert "## Authorization Checks" in markdown
    assert "- [ ] confirm_final_start_authorization_ready" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_manual_execution_start_clearance_packet_coverage_audit_ready" in markdown
    assert "## Packet Coverage Checks" in markdown
    assert "- `start_clearance_packet_ready`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_clearance_packet_final_start_authorization_coverage_audit_read_only`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start clearance packet final start authorization coverage gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start clearance packet final start authorization coverage audit blockers." in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert (
        "Next-session manual execution start clearance packet final start authorization coverage audit is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert (
        seal.seal_scope
        == "manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal"
    )
    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"
    )
    assert (
        seal.audit_status
        == "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert (
        seal.authorization_status
        == "authorized_for_manual_execution_start_from_clearance_packet"
    )
    assert (
        seal.seal_source_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert seal.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        seal.packet_source_status
        == "ready_for_manual_execution_start_authorization_packet"
    )
    assert (
        seal.handoff_readiness
        == "ready_for_manual_execution_final_start_packet_handoff"
    )
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert (
        seal.source_audit_status
        == "manual_execution_start_docket_coverage_audit_ready"
    )
    assert seal.docket_status == "ready_for_manual_execution_start_docket"
    assert seal.seal_checks == [
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
    assert seal.authorization_coverage_checks == {
        "final_start_authorization_ready": "covered",
        "coverage_audit_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "packet_status_preserved": "covered",
        "seal_source_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "authorization_checks_complete": "covered",
        "seal_checks_complete": "covered",
        "packet_coverage_checks_complete": "covered",
        "boundary_checks_complete": "covered",
        "clearance_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert seal.authorization_checks == [
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
    ]
    assert seal.coverage_seal_checks == [
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
    ]
    assert seal.packet_coverage_checks == {
        "start_clearance_packet_ready": "covered",
        "coverage_audit_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "clearance_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert seal.missing_coverage == []
    assert seal.boundary_checks == {
        "start_clearance_packet_final_start_authorization_coverage_audit_seal_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert seal.clearance_checklist == [
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
    ]
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert seal.verification_checklist == [
        "uv run --with pytest python -m pytest tests/unit/test_source_intake.py",
        "uv run --with pytest python -m pytest tests/integration/test_report_regression_cases.py tests/safety/test_expanded_high_risk_language.py",
        "uv run --with pytest python -m pytest",
        "confirm_boundary_confirmation",
    ]
    assert seal.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert seal.post_completion_review == [
        "rerun_launch_seal",
        "confirm_review_decision_delta_zero",
        "confirm_candidate_status_delta_zero",
        "confirm_formal_evidence_delta_zero",
    ]
    assert seal.target_candidates == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert seal.blocked_reasons == []
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"
    )
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert (
        seal.sealed_first_step
        == "execute_close_verified_candidate_session_items"
    )
    assert (
        seal.authorization_coverage_checks["sealed_first_step_preserved"]
        == "covered"
    )
    assert (
        seal.sealed_candidate_order[0]
        == "candidate_duan_ten_god_relation_017_001"
    )


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`" in markdown
    assert "- Authorization status: `authorized_for_manual_execution_start_from_clearance_packet`" in markdown
    assert "- Packet status: `ready_for_manual_execution_start_clearance_packet`" in markdown
    assert "- Seal source status: `sealed_for_manual_execution_start_authorization_packet_coverage_audit`" in markdown
    assert "- Packet source status: `ready_for_manual_execution_start_authorization_packet`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready" in markdown
    assert "## Authorization Coverage Checks" in markdown
    assert "- `final_start_authorization_ready`: `covered`" in markdown
    assert "## Authorization Checks" in markdown
    assert "- [ ] confirm_final_start_authorization_ready" in markdown
    assert "## Coverage Seal Checks" in markdown
    assert "- [ ] confirm_manual_execution_start_clearance_packet_coverage_audit_ready" in markdown
    assert "## Packet Coverage Checks" in markdown
    assert "- `start_clearance_packet_ready`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_clearance_packet_final_start_authorization_coverage_audit_seal_read_only`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start clearance packet final start authorization coverage audit seal gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start clearance packet final start authorization coverage audit seal blockers." in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert (
        "Next-session manual execution start clearance packet final start authorization coverage audit seal is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert (
        packet.packet_scope
        == "manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_start_handoff_packet"
    )
    assert (
        packet.handoff_packet_status
        == "ready_for_manual_execution_start_handoff_packet"
    )
    assert (
        packet.handoff_status
        == "ready_for_operator_manual_execution_start_handoff"
    )
    assert (
        packet.seal_status
        == "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"
    )
    assert (
        packet.audit_status
        == "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert (
        packet.authorization_status
        == "authorized_for_manual_execution_start_from_clearance_packet"
    )
    assert (
        packet.seal_source_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert packet.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        packet.packet_source_status
        == "ready_for_manual_execution_start_authorization_packet"
    )
    assert (
        packet.handoff_readiness
        == "ready_for_manual_execution_final_start_packet_handoff"
    )
    assert packet.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert (
        packet.source_audit_status
        == "manual_execution_start_docket_coverage_audit_ready"
    )
    assert packet.docket_status == "ready_for_manual_execution_start_docket"
    assert packet.handoff_checks == [
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
    assert packet.seal_checks[0] == (
        "confirm_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert packet.authorization_coverage_checks["final_start_authorization_ready"] == "covered"
    assert packet.authorization_checks[1] == "confirm_final_start_authorization_ready"
    assert packet.coverage_seal_checks[0] == (
        "confirm_manual_execution_start_clearance_packet_coverage_audit_ready"
    )
    assert packet.packet_coverage_checks["start_clearance_packet_ready"] == "covered"
    assert packet.missing_coverage == []
    assert packet.boundary_checks == {
        "start_clearance_packet_final_start_authorization_coverage_audit_seal_start_handoff_packet_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert packet.clearance_checklist[0] == (
        "confirm_start_authorization_packet_coverage_audit_seal_ready"
    )
    assert packet.sealed_first_step == "execute_apply_correction_queue_first"
    assert packet.sealed_candidate_order == [
        "candidate_duan_ten_god_relation_017_001",
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert packet.operator_authorization_checklist == [
        "confirm_final_boundary_audit_seal_ready",
        "confirm_start_authorization",
        "confirm_sealed_first_step",
        "confirm_sealed_candidate_order",
        "confirm_pre_execution_boundary",
        "confirm_manual_only_execution",
    ]
    assert packet.operator_start_checklist == [
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
    assert packet.verification_checklist[-1] == "confirm_boundary_confirmation"
    assert packet.rollback_path == [
        "render_next_session_execution_handoff",
        "render_next_session_completion_criteria",
        "render_next_session_final_readiness_summary",
    ]
    assert packet.post_completion_review[-1] == "confirm_formal_evidence_delta_zero"
    assert packet.target_candidates == packet.sealed_candidate_order
    assert packet.blocked_reasons == []
    assert packet.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert (
        packet.handoff_packet_status
        == "ready_for_manual_execution_start_handoff_packet"
    )
    assert (
        packet.handoff_status
        == "ready_for_operator_manual_execution_start_handoff"
    )
    assert (
        packet.sealed_first_step
        == "execute_close_verified_candidate_session_items"
    )
    assert "confirm_sealed_first_step" in packet.operator_start_checklist
    assert (
        packet.sealed_candidate_order[0]
        == "candidate_duan_ten_god_relation_017_001"
    )


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit Seal Start Handoff Packet\n"
    )
    assert "- Packet scope: `manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_start_handoff_packet`" in markdown
    assert "- Handoff packet status: `ready_for_manual_execution_start_handoff_packet`" in markdown
    assert "- Handoff status: `ready_for_operator_manual_execution_start_handoff`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`" in markdown
    assert "- Authorization status: `authorized_for_manual_execution_start_from_clearance_packet`" in markdown
    assert "- Packet status: `ready_for_manual_execution_start_clearance_packet`" in markdown
    assert "- Seal source status: `sealed_for_manual_execution_start_authorization_packet_coverage_audit`" in markdown
    assert "- Packet source status: `ready_for_manual_execution_start_authorization_packet`" in markdown
    assert "- Go/no-go start decision: `go_for_operator_manual_execution`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Handoff Checks" in markdown
    assert "- [ ] confirm_final_start_authorization_coverage_audit_seal_ready" in markdown
    assert "## Operator Start Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Seal Checks" in markdown
    assert "## Authorization Coverage Checks" in markdown
    assert "## Authorization Checks" in markdown
    assert "## Coverage Seal Checks" in markdown
    assert "## Packet Coverage Checks" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_clearance_packet_final_start_authorization_coverage_audit_seal_start_handoff_packet_read_only`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start clearance packet final start authorization coverage audit seal start handoff packet gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start clearance packet final start authorization coverage audit seal start handoff packet blockers." in markdown
    assert "## Boundary Confirmation" in markdown
    assert "- [ ] final_launch_packet_read_only" in markdown
    assert (
        "Next-session manual execution start handoff packet is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert (
        audit.audit_scope
        == "manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit"
    )
    assert audit.audit_status == "manual_execution_start_handoff_packet_coverage_audit_ready"
    assert audit.handoff_packet_status == "ready_for_manual_execution_start_handoff_packet"
    assert audit.handoff_status == "ready_for_operator_manual_execution_start_handoff"
    assert (
        audit.seal_status
        == "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"
    )
    assert (
        audit.coverage_audit_status
        == "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert audit.authorization_status == "authorized_for_manual_execution_start_from_clearance_packet"
    assert audit.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        audit.seal_source_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert audit.packet_source_status == "ready_for_manual_execution_start_authorization_packet"
    assert audit.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.coverage_checks == {
        "start_handoff_packet_ready": "covered",
        "handoff_status_ready": "covered",
        "final_start_authorization_coverage_audit_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "authorization_status_preserved": "covered",
        "packet_status_preserved": "covered",
        "seal_source_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "handoff_checks_complete": "covered",
        "seal_checks_complete": "covered",
        "authorization_coverage_checks_complete": "covered",
        "authorization_checks_complete": "covered",
        "coverage_seal_checks_complete": "covered",
        "packet_coverage_checks_complete": "covered",
        "boundary_checks_complete": "covered",
        "clearance_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "operator_start_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.missing_coverage == []
    assert audit.boundary_checks == {
        "start_handoff_packet_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert audit.handoff_checks[0] == "confirm_final_start_authorization_coverage_audit_seal_ready"
    assert audit.operator_start_checklist[-1] == "confirm_boundary_delta_zero"
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert audit.target_candidates == audit.sealed_candidate_order
    assert audit.blocked_reasons == []
    assert audit.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.audit_status == "manual_execution_start_handoff_packet_coverage_audit_ready"
    assert audit.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert audit.coverage_checks["sealed_first_step_preserved"] == "covered"
    assert audit.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_handoff_packet_coverage_audit_ready`" in markdown
    assert "- Handoff packet status: `ready_for_manual_execution_start_handoff_packet`" in markdown
    assert "- Handoff status: `ready_for_operator_manual_execution_start_handoff`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`" in markdown
    assert "- Coverage audit status: `manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `start_handoff_packet_ready`: `covered`" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start handoff packet coverage gaps." in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_handoff_packet_coverage_audit_read_only`: `covered`" in markdown
    assert "## Handoff Checks" in markdown
    assert "- [ ] confirm_final_start_authorization_coverage_audit_seal_ready" in markdown
    assert "## Operator Start Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start handoff packet coverage audit blockers." in markdown
    assert (
        "Next-session manual execution start handoff packet coverage audit is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert (
        seal.seal_scope
        == "manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_seal"
    )
    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_handoff_packet_coverage_audit"
    )
    assert seal.audit_status == "manual_execution_start_handoff_packet_coverage_audit_ready"
    assert seal.handoff_packet_status == "ready_for_manual_execution_start_handoff_packet"
    assert seal.handoff_status == "ready_for_operator_manual_execution_start_handoff"
    assert (
        seal.final_start_authorization_coverage_audit_seal_status
        == "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"
    )
    assert (
        seal.coverage_audit_status
        == "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert seal.authorization_status == "authorized_for_manual_execution_start_from_clearance_packet"
    assert seal.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        seal.seal_source_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert seal.packet_source_status == "ready_for_manual_execution_start_authorization_packet"
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.seal_checks == [
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
    assert seal.coverage_checks == {
        "start_handoff_packet_ready": "covered",
        "handoff_status_ready": "covered",
        "final_start_authorization_coverage_audit_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "authorization_status_preserved": "covered",
        "packet_status_preserved": "covered",
        "seal_source_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "handoff_checks_complete": "covered",
        "seal_checks_complete": "covered",
        "authorization_coverage_checks_complete": "covered",
        "authorization_checks_complete": "covered",
        "coverage_seal_checks_complete": "covered",
        "packet_coverage_checks_complete": "covered",
        "boundary_checks_complete": "covered",
        "clearance_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "operator_start_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert seal.missing_coverage == []
    assert seal.boundary_checks == {
        "start_handoff_packet_coverage_audit_seal_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert seal.handoff_checks[0] == "confirm_final_start_authorization_coverage_audit_seal_ready"
    assert seal.operator_start_checklist[-1] == "confirm_boundary_delta_zero"
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert seal.target_candidates == seal.sealed_candidate_order
    assert seal.blocked_reasons == []
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_handoff_packet_coverage_audit"
    )
    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.coverage_checks["sealed_first_step_preserved"] == "covered"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_handoff_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_handoff_packet_coverage_audit_ready`" in markdown
    assert "- Handoff packet status: `ready_for_manual_execution_start_handoff_packet`" in markdown
    assert "- Handoff status: `ready_for_operator_manual_execution_start_handoff`" in markdown
    assert "- Final start authorization coverage audit seal status: `sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`" in markdown
    assert "- Coverage audit status: `manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_manual_execution_start_handoff_packet_coverage_audit_ready" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `start_handoff_packet_ready`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_handoff_packet_coverage_audit_seal_read_only`: `covered`" in markdown
    assert "## Handoff Checks" in markdown
    assert "- [ ] confirm_final_start_authorization_coverage_audit_seal_ready" in markdown
    assert "## Operator Start Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start handoff packet coverage audit seal gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start handoff packet coverage audit seal blockers." in markdown
    assert (
        "Next-session manual execution start handoff packet coverage audit seal is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_packet(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert packet.session_id == "pending_review_manual_application_session"
    assert (
        packet.packet_scope
        == "manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_seal_start_packet"
    )
    assert packet.start_packet_status == "ready_for_operator_manual_execution_start_packet"
    assert (
        packet.seal_status
        == "sealed_for_manual_execution_start_handoff_packet_coverage_audit"
    )
    assert packet.audit_status == "manual_execution_start_handoff_packet_coverage_audit_ready"
    assert packet.handoff_packet_status == "ready_for_manual_execution_start_handoff_packet"
    assert packet.handoff_status == "ready_for_operator_manual_execution_start_handoff"
    assert (
        packet.final_start_authorization_coverage_audit_seal_status
        == "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"
    )
    assert (
        packet.coverage_audit_status
        == "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert packet.authorization_status == "authorized_for_manual_execution_start_from_clearance_packet"
    assert packet.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        packet.seal_source_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert packet.packet_source_status == "ready_for_manual_execution_start_authorization_packet"
    assert packet.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.start_checks == [
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
    assert packet.seal_checks[0] == (
        "confirm_manual_execution_start_handoff_packet_coverage_audit_ready"
    )
    assert packet.coverage_checks["start_handoff_packet_ready"] == "covered"
    assert packet.missing_coverage == []
    assert packet.boundary_checks == {
        "start_handoff_packet_coverage_audit_seal_start_packet_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert packet.handoff_checks[0] == "confirm_final_start_authorization_coverage_audit_seal_ready"
    assert packet.operator_start_checklist[-1] == "confirm_boundary_delta_zero"
    assert packet.sealed_first_step == "execute_apply_correction_queue_first"
    assert packet.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert packet.target_candidates == packet.sealed_candidate_order
    assert packet.blocked_reasons == []
    assert packet.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    packet = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert packet.start_packet_status == "ready_for_operator_manual_execution_start_packet"
    assert packet.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert "confirm_sealed_first_step" in packet.operator_start_checklist
    assert packet.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Packet\n"
    )
    assert "- Packet scope: `manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_seal_start_packet`" in markdown
    assert "- Start packet status: `ready_for_operator_manual_execution_start_packet`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_handoff_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_handoff_packet_coverage_audit_ready`" in markdown
    assert "- Handoff packet status: `ready_for_manual_execution_start_handoff_packet`" in markdown
    assert "- Handoff status: `ready_for_operator_manual_execution_start_handoff`" in markdown
    assert "- Final start authorization coverage audit seal status: `sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Start Checks" in markdown
    assert "- [ ] confirm_operator_manual_execution_start_packet_ready" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_manual_execution_start_handoff_packet_coverage_audit_ready" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `start_handoff_packet_ready`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_handoff_packet_coverage_audit_seal_start_packet_read_only`: `covered`" in markdown
    assert "## Operator Start Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start packet gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start packet blockers." in markdown
    assert (
        "Next-session manual execution start packet is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_coverage_audit(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert audit.session_id == "pending_review_manual_application_session"
    assert (
        audit.audit_scope
        == "manual_application_next_session_manual_execution_start_packet_coverage_audit"
    )
    assert audit.audit_status == "manual_execution_start_packet_coverage_audit_ready"
    assert audit.start_packet_status == "ready_for_operator_manual_execution_start_packet"
    assert (
        audit.seal_status
        == "sealed_for_manual_execution_start_handoff_packet_coverage_audit"
    )
    assert (
        audit.start_packet_source_audit_status
        == "manual_execution_start_handoff_packet_coverage_audit_ready"
    )
    assert audit.handoff_packet_status == "ready_for_manual_execution_start_handoff_packet"
    assert audit.handoff_status == "ready_for_operator_manual_execution_start_handoff"
    assert (
        audit.final_start_authorization_coverage_audit_seal_status
        == "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"
    )
    assert (
        audit.coverage_audit_status
        == "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert audit.authorization_status == "authorized_for_manual_execution_start_from_clearance_packet"
    assert audit.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert (
        audit.seal_source_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert audit.packet_source_status == "ready_for_manual_execution_start_authorization_packet"
    assert audit.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert audit.start_authorization == "authorized_to_start_manual_execution"
    assert audit.source_audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert audit.docket_status == "ready_for_manual_execution_start_docket"
    assert audit.coverage_checks == {
        "start_packet_ready": "covered",
        "start_packet_source_audit_status_preserved": "covered",
        "start_handoff_packet_coverage_audit_seal_status_preserved": "covered",
        "handoff_packet_status_preserved": "covered",
        "handoff_status_preserved": "covered",
        "final_start_authorization_coverage_audit_seal_status_preserved": "covered",
        "coverage_audit_status_preserved": "covered",
        "authorization_status_preserved": "covered",
        "packet_status_preserved": "covered",
        "seal_source_status_preserved": "covered",
        "packet_source_status_preserved": "covered",
        "handoff_readiness_preserved": "covered",
        "go_no_go_start_decision_preserved": "covered",
        "start_authorization_preserved": "covered",
        "source_audit_status_preserved": "covered",
        "docket_status_preserved": "covered",
        "start_checks_complete": "covered",
        "seal_checks_complete": "covered",
        "source_coverage_checks_complete": "covered",
        "boundary_checks_complete": "covered",
        "handoff_checks_complete": "covered",
        "source_seal_checks_complete": "covered",
        "authorization_coverage_checks_complete": "covered",
        "authorization_checks_complete": "covered",
        "coverage_seal_checks_complete": "covered",
        "packet_coverage_checks_complete": "covered",
        "clearance_checklist_complete": "covered",
        "sealed_first_step_preserved": "covered",
        "sealed_candidate_order_preserved": "covered",
        "operator_authorization_checklist_preserved": "covered",
        "operator_start_checklist_preserved": "covered",
        "verification_checklist_preserved": "covered",
        "rollback_path_preserved": "covered",
        "post_completion_review_preserved": "covered",
        "target_candidates_preserved": "covered",
        "blocked_reasons_preserved": "covered",
        "boundary_confirmation_preserved": "covered",
        "boundary_delta_zero": "covered",
    }
    assert audit.source_coverage_checks["start_handoff_packet_ready"] == "covered"
    assert audit.missing_coverage == []
    assert audit.boundary_checks == {
        "start_packet_coverage_audit_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert audit.start_checks[1] == "confirm_operator_manual_execution_start_packet_ready"
    assert audit.operator_start_checklist[-1] == "confirm_boundary_delta_zero"
    assert audit.sealed_first_step == "execute_apply_correction_queue_first"
    assert audit.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert audit.target_candidates == audit.sealed_candidate_order
    assert audit.blocked_reasons == []
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_coverage_audit_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    audit = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert audit.audit_status == "manual_execution_start_packet_coverage_audit_ready"
    assert audit.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert audit.coverage_checks["sealed_first_step_preserved"] == "covered"
    assert audit.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_coverage_audit_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit\n"
    )
    assert "- Audit scope: `manual_application_next_session_manual_execution_start_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_packet_coverage_audit_ready`" in markdown
    assert "- Start packet status: `ready_for_operator_manual_execution_start_packet`" in markdown
    assert "- Start packet source audit status: `manual_execution_start_handoff_packet_coverage_audit_ready`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_handoff_packet_coverage_audit`" in markdown
    assert "- Handoff packet status: `ready_for_manual_execution_start_handoff_packet`" in markdown
    assert "- Handoff status: `ready_for_operator_manual_execution_start_handoff`" in markdown
    assert "- Final start authorization coverage audit seal status: `sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `start_packet_ready`: `covered`" in markdown
    assert "## Source Coverage Checks" in markdown
    assert "- `start_handoff_packet_ready`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_packet_coverage_audit_read_only`: `covered`" in markdown
    assert "## Start Checks" in markdown
    assert "- [ ] confirm_operator_manual_execution_start_packet_ready" in markdown
    assert "## Operator Start Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start packet coverage audit gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start packet coverage audit blockers." in markdown
    assert (
        "Next-session manual execution start packet coverage audit is read-only planning metadata."
        in markdown
    )


def test_build_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_coverage_audit_seal(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert seal.session_id == "pending_review_manual_application_session"
    assert (
        seal.seal_scope
        == "manual_application_next_session_manual_execution_start_packet_coverage_audit_seal"
    )
    assert seal.seal_status == "sealed_for_manual_execution_start_packet_coverage_audit"
    assert seal.audit_status == "manual_execution_start_packet_coverage_audit_ready"
    assert seal.start_packet_status == "ready_for_operator_manual_execution_start_packet"
    assert (
        seal.start_packet_source_audit_status
        == "manual_execution_start_handoff_packet_coverage_audit_ready"
    )
    assert (
        seal.seal_source_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert seal.packet_source_status == "ready_for_manual_execution_start_authorization_packet"
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.start_authorization == "authorized_to_start_manual_execution"
    assert seal.seal_checks == [
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
    assert seal.coverage_checks["start_packet_ready"] == "covered"
    assert seal.source_coverage_checks["start_handoff_packet_ready"] == "covered"
    assert seal.missing_coverage == []
    assert seal.boundary_checks == {
        "start_packet_coverage_audit_seal_read_only": "covered",
        "review_decision_delta_zero": "covered",
        "candidate_status_delta_zero": "covered",
        "formal_evidence_delta_zero": "covered",
    }
    assert seal.start_checks[1] == "confirm_operator_manual_execution_start_packet_ready"
    assert seal.operator_start_checklist[-1] == "confirm_boundary_delta_zero"
    assert seal.sealed_first_step == "execute_apply_correction_queue_first"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"
    assert seal.target_candidates == seal.sealed_candidate_order
    assert seal.blocked_reasons == []
    assert seal.boundary_confirmation == [
        "review_decision_delta_zero",
        "candidate_status_delta_zero",
        "formal_evidence_delta_zero",
        "final_launch_packet_read_only",
    ]
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_coverage_audit_seal_surfaces_close_first(
    tmp_path,
):
    preview_dir = tmp_path / "before"
    post_session_dir = tmp_path / "after"
    preview_dir.mkdir()
    post_session_dir.mkdir()
    _write_post_session_verification_fixture(preview_dir)
    _write_post_session_verification_fixture(
        post_session_dir,
        duan_status="returned",
        include_duan_review_decision=True,
    )

    seal = source_intake.build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal(
        [_ready_duan_review_draft()],
        post_session_dir,
        preview_data_dir=preview_dir,
    )

    assert seal.seal_status == "sealed_for_manual_execution_start_packet_coverage_audit"
    assert seal.sealed_first_step == "execute_close_verified_candidate_session_items"
    assert seal.coverage_checks["sealed_first_step_preserved"] == "covered"
    assert seal.sealed_candidate_order[0] == "candidate_duan_ten_god_relation_017_001"


def test_render_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_coverage_audit_seal_markdown(
    tmp_path,
):
    _write_post_session_verification_fixture(tmp_path)

    markdown = source_intake.render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal_markdown(
        [_ready_duan_review_draft()],
        tmp_path,
        preview_data_dir=tmp_path,
    )

    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit Seal\n"
    )
    assert "- Seal scope: `manual_application_next_session_manual_execution_start_packet_coverage_audit_seal`" in markdown
    assert "- Seal status: `sealed_for_manual_execution_start_packet_coverage_audit`" in markdown
    assert "- Audit status: `manual_execution_start_packet_coverage_audit_ready`" in markdown
    assert "- Start packet status: `ready_for_operator_manual_execution_start_packet`" in markdown
    assert "- Start packet source audit status: `manual_execution_start_handoff_packet_coverage_audit_ready`" in markdown
    assert "- Start authorization: `authorized_to_start_manual_execution`" in markdown
    assert "## Seal Checks" in markdown
    assert "- [ ] confirm_manual_execution_start_packet_coverage_audit_ready" in markdown
    assert "## Coverage Checks" in markdown
    assert "- `start_packet_ready`: `covered`" in markdown
    assert "## Source Coverage Checks" in markdown
    assert "- `start_handoff_packet_ready`: `covered`" in markdown
    assert "## Boundary Checks" in markdown
    assert "- `start_packet_coverage_audit_seal_read_only`: `covered`" in markdown
    assert "## Start Checks" in markdown
    assert "- [ ] confirm_operator_manual_execution_start_packet_ready" in markdown
    assert "## Operator Start Checklist" in markdown
    assert "- [ ] confirm_manual_only_execution" in markdown
    assert "## Missing Coverage" in markdown
    assert "No manual execution start packet coverage audit seal gaps." in markdown
    assert "## Blocked Reasons" in markdown
    assert "No manual execution start packet coverage audit seal blockers." in markdown
    assert (
        "Next-session manual execution start packet coverage audit seal is read-only planning metadata."
        in markdown
    )


def test_seeded_review_and_promotion_records_reference_existing_candidates():
    candidates = source_intake.load_candidate_extracts()
    candidate_ids = {candidate.candidate_id for candidate in candidates}

    reviews = source_intake.load_review_decisions()
    batches = source_intake.load_promotion_batches()

    assert reviews
    assert batches
    assert all(review.candidate_id in candidate_ids for review in reviews)
    assert all(
        candidate_id in candidate_ids
        for batch in batches
        for candidate_id in batch.candidate_ids
    )


def test_bazi_general_source_preparation_reading_intake_records_are_promoted():
    materials = source_intake.load_source_materials()
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    batches = source_intake.load_promotion_batches()

    materials_by_id = {material.material_id: material for material in materials}
    candidates_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    reviews_by_id = {review.decision_id: review for review in reviews}
    batches_by_id = {batch.promotion_batch_id: batch for batch in batches}

    expected_materials = {
        "material_bazi_general_lecture_textbook_pdf": (
            "source_bazi_general_lecture_textbook_pdf",
            "reviewed",
        ),
        "material_bazi_general_beichen_intro_pdf": (
            "source_bazi_general_beichen_intro_pdf",
            "reviewed",
        ),
        "material_bazi_general_ziping_orthodox_pair_pdf": (
            "source_bazi_general_ziping_orthodox_pair_pdf",
            "reviewed",
        ),
    }
    for material_id, (source_id, preparation_status) in expected_materials.items():
        material = materials_by_id[material_id]
        assert material.related_source_id == source_id
        assert material.preparation_status == preparation_status

    expected_candidates = {
        "candidate_bazi_general_lecture_pattern_strength_001": (
            "material_bazi_general_lecture_textbook_pdf",
            "pattern_strength",
            "bazi_general_lecture_pattern_strength_001",
        ),
        "candidate_bazi_general_beichen_branch_interaction_001": (
            "material_bazi_general_beichen_intro_pdf",
            "branch_interaction",
            "bazi_general_beichen_branch_interaction_001",
        ),
        "candidate_bazi_general_ziping_useful_god_001": (
            "material_bazi_general_ziping_orthodox_pair_pdf",
            "useful_god_candidate",
            "bazi_general_ziping_useful_god_001",
        ),
    }
    for candidate_id, (material_id, rule_family, evidence_id) in expected_candidates.items():
        candidate = candidates_by_id[candidate_id]
        assert candidate.material_id == material_id
        assert candidate.proposed_rule_family == rule_family
        assert candidate.risk_tier == "ordinary"
        assert candidate.status == "promoted"
        assert candidate.related_evidence_ids == [evidence_id]
        assert len(candidate.extracted_meaning) <= 280
        assert len(candidate.short_quote) <= 80

        review = reviews_by_id[f"review_{candidate_id.removeprefix('candidate_')}"]
        assert review.candidate_id == candidate_id
        assert review.decision == "approved"
        assert review.confidence == "moderate"
        assert review.approval_limitations

    batch = batches_by_id["promotion_bazi_general_source_preparation_reading_001"]
    assert batch.review_status == "reviewed"
    assert batch.candidate_ids == list(expected_candidates)
    assert batch.target_evidence_ids == [
        "bazi_general_lecture_pattern_strength_001",
        "bazi_general_beichen_branch_interaction_001",
        "bazi_general_ziping_useful_god_001",
    ]
    assert batch.unresolved_issues == []


def test_bazi_general_selected_variant_intake_records_are_promoted():
    materials = source_intake.load_source_materials()
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    batches = source_intake.load_promotion_batches()

    materials_by_id = {material.material_id: material for material in materials}
    candidates_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    reviews_by_id = {review.decision_id: review for review in reviews}
    batches_by_id = {batch.promotion_batch_id: batch for batch in batches}

    expected_materials = {
        "material_bazi_general_ditiansui_selected_pdf": (
            "source_bazi_general_ditiansui_selected_pdf",
            "reviewed",
        ),
        "material_bazi_general_qiongtong_selected_pdf": (
            "source_bazi_general_qiongtong_selected_pdf",
            "reviewed",
        ),
    }
    for material_id, (source_id, preparation_status) in expected_materials.items():
        material = materials_by_id[material_id]
        assert material.related_source_id == source_id
        assert material.preparation_status == preparation_status

    expected_candidates = {
        "candidate_bazi_general_ditiansui_pattern_strength_001": (
            "material_bazi_general_ditiansui_selected_pdf",
            "pattern_strength",
            "bazi_general_ditiansui_pattern_strength_001",
        ),
        "candidate_bazi_general_qiongtong_useful_god_001": (
            "material_bazi_general_qiongtong_selected_pdf",
            "useful_god_candidate",
            "bazi_general_qiongtong_useful_god_001",
        ),
    }
    for candidate_id, (material_id, rule_family, evidence_id) in expected_candidates.items():
        candidate = candidates_by_id[candidate_id]
        assert candidate.material_id == material_id
        assert candidate.source_locator.startswith("page:")
        assert candidate.proposed_rule_family == rule_family
        assert candidate.risk_tier == "ordinary"
        assert candidate.status == "promoted"
        assert candidate.related_evidence_ids == [evidence_id]
        assert len(candidate.extracted_meaning) <= 280
        assert len(candidate.short_quote) <= 80

        review = reviews_by_id[f"review_{candidate_id.removeprefix('candidate_')}"]
        assert review.candidate_id == candidate_id
        assert review.decision == "approved"
        assert review.source_quality == "review_note"
        assert review.confidence == "weak"
        assert review.approval_limitations

    batch = batches_by_id["promotion_bazi_general_selected_variant_preparation_001"]
    assert batch.review_status == "reviewed"
    assert batch.candidate_ids == list(expected_candidates)
    assert batch.target_evidence_ids == [
        "bazi_general_ditiansui_pattern_strength_001",
        "bazi_general_qiongtong_useful_god_001",
    ]
    assert batch.unresolved_issues == []


def test_bazi_general_next_cycle_cluster_source_intake_records_are_promoted():
    materials = source_intake.load_source_materials()
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    batches = source_intake.load_promotion_batches()

    materials_by_id = {material.material_id: material for material in materials}
    candidates_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    reviews_by_id = {review.decision_id: review for review in reviews}
    batches_by_id = {batch.promotion_batch_id: batch for batch in batches}

    expected_materials = {
        "material_bazi_general_true_spirit_positioning_pdf": (
            "source_bazi_general_true_spirit_positioning_pdf",
            "reviewed",
        ),
        "material_bazi_general_mingli_wangdoujing_pdf": (
            "source_bazi_general_mingli_wangdoujing_pdf",
            "reviewed",
        ),
    }
    for material_id, (source_id, preparation_status) in expected_materials.items():
        material = materials_by_id[material_id]
        assert material.related_source_id == source_id
        assert material.preparation_status == preparation_status

    expected_candidates = {
        "candidate_bazi_general_true_spirit_useful_god_001": (
            "material_bazi_general_true_spirit_positioning_pdf",
            "useful_god_candidate",
            "bazi_general_true_spirit_useful_god_001",
        ),
        "candidate_bazi_general_wangdoujing_branch_interaction_001": (
            "material_bazi_general_mingli_wangdoujing_pdf",
            "branch_interaction",
            "bazi_general_wangdoujing_branch_interaction_001",
        ),
    }
    for candidate_id, (material_id, rule_family, evidence_id) in expected_candidates.items():
        candidate = candidates_by_id[candidate_id]
        assert candidate.material_id == material_id
        assert candidate.source_locator.startswith("page:")
        assert candidate.proposed_rule_family == rule_family
        assert candidate.risk_tier == "ordinary"
        assert candidate.status == "promoted"
        assert candidate.related_evidence_ids == [evidence_id]
        assert len(candidate.extracted_meaning) <= 280
        assert len(candidate.short_quote) <= 80

        review = reviews_by_id[f"review_{candidate_id.removeprefix('candidate_')}"]
        assert review.candidate_id == candidate_id
        assert review.decision == "approved"
        assert review.source_quality == "review_note"
        assert review.confidence == "weak"
        assert review.approval_limitations

    batch = batches_by_id["promotion_bazi_general_next_cycle_cluster_source_001"]
    assert batch.review_status == "reviewed"
    assert batch.candidate_ids == list(expected_candidates)
    assert batch.target_evidence_ids == [
        "bazi_general_true_spirit_useful_god_001",
        "bazi_general_wangdoujing_branch_interaction_001",
    ]
    assert batch.unresolved_issues == []


def test_bazi_general_next_cycle_followup_intake_records_are_promoted():
    materials = source_intake.load_source_materials()
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    batches = source_intake.load_promotion_batches()

    materials_by_id = {material.material_id: material for material in materials}
    candidates_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    reviews_by_id = {review.decision_id: review for review in reviews}
    batches_by_id = {batch.promotion_batch_id: batch for batch in batches}

    expected_materials = {
        "material_bazi_general_xinpai_essence_part2_pdf": (
            "source_bazi_general_xinpai_essence_part2_pdf",
            "reviewed",
        ),
        "material_bazi_general_xingming_shuozheng_vol1_pdf": (
            "source_bazi_general_xingming_shuozheng_vol1_pdf",
            "reviewed",
        ),
    }
    for material_id, (source_id, preparation_status) in expected_materials.items():
        material = materials_by_id[material_id]
        assert material.related_source_id == source_id
        assert material.preparation_status == preparation_status

    expected_candidates = {
        "candidate_bazi_general_xinpai_essence_pattern_strength_001": (
            "material_bazi_general_xinpai_essence_part2_pdf",
            "pattern_strength",
            "bazi_general_xinpai_essence_pattern_strength_001",
        ),
        "candidate_bazi_general_xingming_shuozheng_branch_interaction_001": (
            "material_bazi_general_xingming_shuozheng_vol1_pdf",
            "branch_interaction",
            "bazi_general_xingming_shuozheng_branch_interaction_001",
        ),
    }
    for candidate_id, (material_id, rule_family, evidence_id) in expected_candidates.items():
        candidate = candidates_by_id[candidate_id]
        assert candidate.material_id == material_id
        assert candidate.source_locator.startswith("page:")
        assert candidate.proposed_rule_family == rule_family
        assert candidate.risk_tier == "ordinary"
        assert candidate.status == "promoted"
        assert candidate.related_evidence_ids == [evidence_id]
        assert len(candidate.extracted_meaning) <= 280
        assert len(candidate.short_quote) <= 80

        review = reviews_by_id[f"review_{candidate_id.removeprefix('candidate_')}"]
        assert review.candidate_id == candidate_id
        assert review.decision == "approved"
        assert review.source_quality == "review_note"
        assert review.confidence == "weak"
        assert review.approval_limitations

    batch = batches_by_id["promotion_bazi_general_next_cycle_followup_001"]
    assert batch.review_status == "reviewed"
    assert batch.candidate_ids == list(expected_candidates)
    assert batch.target_evidence_ids == [
        "bazi_general_xinpai_essence_pattern_strength_001",
        "bazi_general_xingming_shuozheng_branch_interaction_001",
    ]
    assert batch.unresolved_issues == []


def test_blind_life_manual_high_risk_boundary_candidate_is_promoted():
    materials = source_intake.load_source_materials()
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    batches = source_intake.load_promotion_batches()

    materials_by_id = {material.material_id: material for material in materials}
    candidates_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    reviews_by_id = {review.decision_id: review for review in reviews}
    batches_by_id = {batch.promotion_batch_id: batch for batch in batches}

    material = materials_by_id["material_blind_life_manual_pdf"]
    assert material.preparation_status == "partially_reviewed"

    candidate = candidates_by_id["candidate_blind_life_manual_gap_001"]
    assert (
        candidate.source_locator
        == "review-note:blind_life_manual.md#source-window-high-risk-boundary"
    )
    assert candidate.proposed_rule_family == "high_risk_signal"
    assert candidate.risk_tier == "high_risk"
    assert candidate.status == "promoted"
    assert candidate.related_evidence_ids == ["blind_life_manual_high_risk_boundary_001"]
    assert candidate.related_conflict_ids == ["conflict_high_risk_scope_001"]
    assert candidate.related_gap_ids == ["gap_blind_life_manual"]
    assert any(
        marker in limitation
        for limitation in candidate.proposed_limitations
        for marker in ("拒绝", "不得", "exact death")
    )

    review = reviews_by_id["review_candidate_blind_life_manual_gap_001"]
    assert review.candidate_id == candidate.candidate_id
    assert review.decision == "approved"
    assert review.required_changes == []
    assert review.rejection_reason == ""
    assert review.source_quality == "review_note"
    assert review.confidence == "moderate"
    assert review.approval_limitations

    batch = batches_by_id["promotion_blind_life_manual_high_risk_boundary_001"]
    assert batch.review_status == "reviewed"
    assert batch.candidate_ids == ["candidate_blind_life_manual_gap_001"]
    assert batch.target_evidence_ids == ["blind_life_manual_high_risk_boundary_001"]
    assert batch.unresolved_issues


def test_seeded_intake_progress_report_loads_after_batch_registration():
    report = source_intake.build_intake_progress_report()

    assert report.candidate_counts
    assert report.risk_tier_counts
    assert report.rule_family_counts


def test_seeded_intake_candidate_review_closure_packet_is_documented():
    report = source_intake.build_intake_progress_report()
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    batches = source_intake.load_promotion_batches()
    intake_doc = Path("docs/classical_sources/intake.md").read_text(encoding="utf-8")
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    assert report.pending_review_count == 0
    assert source_intake.list_pending_candidate_review_worklist() == []
    assert source_intake.build_pending_candidate_review_action_queue() == []

    for text in (intake_doc, handoff):
        for marker in (
            "013 Candidate Review Closure Packet",
            "`candidate-review-status=closed_no_pending_review_candidates`",
            f"`013-candidate-extracts={len(candidates)}`",
            f"`013-review-decisions={len(reviews)}`",
            f"`013-promotion-batches={len(batches)}`",
            "`013-pending-review-candidates=0`",
            "`013-approved-not-promoted=0`",
            "`013-promoted-candidates=51`",
            "`013-rejected-candidates=2`",
            "`013-blocked-candidates=1`",
            "`pending-review-worklist-items=0`",
            "`pending-review-action-items=0`",
            "`review-decision-delta=0`",
            "`formal-evidence-delta=0`",
            "`next-work-entry=wait-new-material-or-maintain-promoted-evidence`",
        ):
            assert marker in text
        assert "Current worklist:\n\n- `candidate_" not in text
        assert "Packet count: `5`" not in text


def test_promoted_markdown_learning_candidates_use_source_file_locators():
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in source_intake.load_candidate_extracts()
    }

    assert PROMOTED_MARKDOWN_LEARNING_CANDIDATE_IDS <= set(candidates_by_id)
    for candidate_id in PROMOTED_MARKDOWN_LEARNING_CANDIDATE_IDS:
        source_locator = candidates_by_id[candidate_id].source_locator

        _assert_markdown_line_locator(source_locator)
        assert "learning-reference:" not in source_locator
        assert "note_markdown_batch_005_001" not in source_locator


def test_markdown_batch_002_extension_candidates_are_promoted():
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    batches = source_intake.load_promotion_batches()

    candidates_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    reviews_by_id = {review.decision_id: review for review in reviews}
    batches_by_id = {batch.promotion_batch_id: batch for batch in batches}

    expected_candidates = {
        "candidate_markdown_batch_002_branch_route_001": (
            "branch_interaction",
            "batch002_branch_interaction_route_001",
        ),
        "candidate_markdown_batch_002_useful_god_types_001": (
            "useful_god_candidate",
            "batch002_useful_god_types_001",
        ),
        "candidate_markdown_batch_002_day_master_strength_basis_001": (
            "pattern_strength",
            "batch002_day_master_strength_basis_001",
        ),
    }
    for candidate_id, (rule_family, evidence_id) in expected_candidates.items():
        candidate = candidates_by_id[candidate_id]

        assert candidate.material_id == "material_markdown_source_batch_002_core"
        assert candidate.proposed_rule_family == rule_family
        assert candidate.risk_tier == "ordinary"
        assert candidate.status == "promoted"
        assert candidate.related_evidence_ids == [evidence_id]
        assert candidate.related_conflict_ids == []
        assert candidate.related_gap_ids == []
        _assert_markdown_line_locator(candidate.source_locator)
        assert len(candidate.extracted_meaning) <= 280
        assert len(candidate.short_quote) <= 80

        review = reviews_by_id[f"review_{candidate_id.removeprefix('candidate_')}"]
        assert review.candidate_id == candidate_id
        assert review.decision == "approved"
        assert review.required_changes == []
        assert review.rejection_reason == ""
        assert review.source_quality == "direct_extract"
        assert review.confidence == "moderate"
        assert review.approval_limitations

    batch = batches_by_id["promotion_markdown_batch_002_extension_001"]
    assert batch.review_status == "reviewed"
    assert batch.candidate_ids == list(expected_candidates)
    assert batch.target_evidence_ids == [
        "batch002_branch_interaction_route_001",
        "batch002_useful_god_types_001",
        "batch002_day_master_strength_basis_001",
    ]
    assert batch.unresolved_issues == []


def test_promoted_kskeleton_candidates_use_review_note_locators():
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in source_intake.load_candidate_extracts()
    }

    assert PROMOTED_KSKELETON_CANDIDATE_IDS <= set(candidates_by_id)
    for candidate_id in PROMOTED_KSKELETON_CANDIDATE_IDS:
        source_locator = candidates_by_id[candidate_id].source_locator

        assert source_locator.startswith("review-note:knowledge_skeleton/"), (
            candidate_id,
            source_locator,
        )
        assert "learning-reference:" not in source_locator
        assert (Path("资料整理") / source_locator.removeprefix("review-note:")).exists()


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
