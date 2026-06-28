import json
from pathlib import Path

import pytest

from mingli_engine import models
from mingli_engine import source_library


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _minimal_entry(entry_id: str = "entry_001") -> dict[str, object]:
    return {
        "entry_id": entry_id,
        "material_id": "material_001",
        "title": "Material One",
        "material_type": "pdf",
        "local_reference": "material-one.pdf",
        "tracking_status": "external_untracked",
        "readiness_status": "not_started",
        "topic_tags": [],
        "rule_families": [],
        "source_quality_notes": "",
        "rights_notes": "Do not copy long passages.",
        "risk_tier": "ordinary",
        "risk_notes": [],
        "priority_level": "medium",
        "next_action": "prepare_material",
        "outcome_reason": "",
        "created_at": "2026-05-28",
        "updated_at": "2026-05-28",
    }


def _minimal_assessment(
    assessment_id: str = "priority_001",
) -> dict[str, object]:
    return {
        "assessment_id": assessment_id,
        "entry_id": "entry_001",
        "priority_level": "medium",
        "expected_value": "fills_gap",
        "target_gap_ids": ["gap_001"],
        "target_rule_families": [],
        "source_quality": "moderate",
        "effort_level": "medium",
        "risk_tier": "ordinary",
        "rationale": "This source may fill a documented evidence gap.",
        "assessed_by": "maintainer",
        "assessed_at": "2026-05-28",
    }


def _minimal_batch(batch_plan_id: str = "batch_plan_001") -> dict[str, object]:
    return {
        "batch_plan_id": batch_plan_id,
        "title": "Initial Source Batch",
        "goal": "Prepare source entries that can fill a documented gap.",
        "entry_ids": ["entry_001"],
        "target_gap_ids": ["gap_001"],
        "target_rule_families": [],
        "risk_boundary": "ordinary",
        "expected_output": ["candidate_extracts"],
        "status": "planned",
        "review_capacity": "Small review batch.",
        "completion_summary": "",
        "recommended_next_batch": "",
    }


def _value_entry(
    entry_id: str,
    material_id: str,
    readiness_status: str = "review_completed",
    next_action: str = "review_candidates",
    outcome_reason: str = "",
) -> dict[str, object]:
    entry = _minimal_entry(entry_id)
    entry.update(
        {
            "material_id": material_id,
            "title": f"Value Fixture {entry_id}",
            "readiness_status": readiness_status,
            "topic_tags": ["value-summary"],
            "rule_families": ["blind_image_method"],
            "source_quality_notes": "Reviewable source notes.",
            "rights_notes": "Do not copy long passages.",
            "next_action": next_action,
            "outcome_reason": outcome_reason,
        }
    )
    return entry


def _source_material(material_id: str) -> dict[str, object]:
    return {
        "material_id": material_id,
        "title": f"Material {material_id}",
        "material_type": "pdf",
        "file_label": f"{material_id}.pdf",
        "tracking_status": "external_untracked",
        "preparation_status": "partially_reviewed",
        "related_source_id": "",
        "scope_notes": "Temporary source material for value-summary tests.",
        "rights_notes": "Do not copy long passages.",
        "gap_reason": "",
    }


def _candidate_extract(
    candidate_id: str,
    material_id: str,
    status: str,
    rule_family: str = "blind_image_method",
    related_evidence_ids: list[str] | None = None,
    related_conflict_ids: list[str] | None = None,
    related_gap_ids: list[str] | None = None,
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "material_id": material_id,
        "source_locator": f"review-note:{candidate_id}",
        "extracted_meaning": "A bounded candidate meaning for source value tests.",
        "short_quote": "",
        "proposed_rule_family": rule_family,
        "risk_tier": "ordinary",
        "status": status,
        "proposed_limitations": ["Use only as bounded traditional signal material."],
        "related_evidence_ids": related_evidence_ids or [],
        "related_conflict_ids": related_conflict_ids or [],
        "related_gap_ids": related_gap_ids or [],
        "duplicate_of": "",
        "created_by": "maintainer",
        "created_at": "2026-05-28",
    }


def _review_decision(candidate_id: str, decision: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "decision_id": f"review_{candidate_id}",
        "candidate_id": candidate_id,
        "decision": decision,
        "reviewer": "maintainer",
        "reviewed_at": "2026-05-28",
        "rationale": "Decision recorded for source value summary testing.",
        "required_changes": [],
        "rejection_reason": "",
        "approval_limitations": [],
        "source_quality": "review_note",
        "confidence": "moderate",
    }
    if decision == "approved":
        payload["approval_limitations"] = [
            "Use only with source locator and uncertainty language."
        ]
    elif decision == "returned":
        payload["required_changes"] = ["Add narrower source locator before approval."]
    elif decision in {"rejected", "blocked"}:
        payload["rejection_reason"] = (
            f"{decision.title()} during source value testing with durable rationale."
        )
    return payload


def _formal_source(source_id: str = "formal_source_001") -> dict[str, object]:
    return {
        "source_id": source_id,
        "title": "Formal Source",
        "file_name": "formal-source.pdf",
        "source_type": "pdf",
        "extraction_status": "partial",
        "review_status": "approved",
        "scope_notes": "Reviewed source used by value summary tests.",
        "risk_notes": [],
        "curation_gap_reason": "",
        "review_reference": "docs/classical_sources/extracts/formal_source.md",
    }


def _formal_evidence(
    evidence_id: str,
    source_id: str = "formal_source_001",
    rule_family: str = "blind_image_method",
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "source_id": source_id,
        "source_ref": "review-note:value-summary",
        "theme": "Value Summary",
        "rule_family": rule_family,
        "risk_tier": "ordinary",
        "summary": "Formal reviewed evidence used for value-summary tests.",
        "applicability": ["formal_report_requested"],
        "limitations": ["Use only as bounded reviewed evidence."],
        "school": "test",
        "curation_batch_id": "",
        "confidence": "moderate",
        "source_quality": "review_note",
        "conflict_ids": [],
    }


def _write_value_summary_fixture(
    tmp_path: Path,
    *,
    entries: list[dict[str, object]],
    candidates: list[dict[str, object]] | None = None,
    decisions: list[dict[str, object]] | None = None,
    promotion_batches: list[dict[str, object]] | None = None,
    batch_plans: list[dict[str, object]] | None = None,
    evidence_units: list[dict[str, object]] | None = None,
) -> Path:
    source_library_dir = tmp_path / "source_library"
    source_intake_dir = tmp_path / "source_intake"
    classical_sources_dir = tmp_path / "classical_sources"
    source_library_dir.mkdir()
    source_intake_dir.mkdir()
    classical_sources_dir.mkdir()

    material_ids = sorted(
        {
            str(entry["material_id"])
            for entry in entries
            if isinstance(entry.get("material_id"), str) and entry["material_id"]
        }
    )
    _write_json(source_library_dir / "source_library_entries.json", entries)
    _write_json(source_library_dir / "source_priority_assessments.json", [])
    _write_json(source_library_dir / "curation_batch_plans.json", batch_plans or [])
    _write_json(
        source_intake_dir / "source_materials.json",
        [_source_material(material_id) for material_id in material_ids],
    )
    _write_json(source_intake_dir / "candidate_extracts.json", candidates or [])
    _write_json(source_intake_dir / "review_decisions.json", decisions or [])
    _write_json(source_intake_dir / "promotion_batches.json", promotion_batches or [])
    _write_json(classical_sources_dir / "sources.json", [_formal_source()])
    _write_json(classical_sources_dir / "evidence_units.json", evidence_units or [])
    _write_json(classical_sources_dir / "curation_batches.json", [])
    _write_json(classical_sources_dir / "source_conflicts.json", [])
    return source_library_dir


def test_source_library_constants_cover_contract_values():
    assert models.SOURCE_LIBRARY_MATERIAL_TYPES == frozenset(
        {"pdf", "markdown", "review_note", "book_excerpt", "other"}
    )
    assert models.SOURCE_LIBRARY_READINESS_STATUSES == frozenset(
        {
            "not_started",
            "needs_preparation",
            "ready_for_extraction",
            "in_extraction",
            "review_completed",
            "exhausted",
            "deferred",
            "duplicate",
            "blocked",
        }
    )
    assert models.SOURCE_LIBRARY_PRIORITY_LEVELS == frozenset(
        {"critical", "high", "medium", "low", "deferred"}
    )
    assert models.SOURCE_LIBRARY_EXPECTED_VALUES == frozenset(
        {
            "fills_gap",
            "clarifies_conflict",
            "confirms_existing_rule",
            "improves_high_risk_boundary",
            "broadens_school_coverage",
            "documents_non_usefulness",
        }
    )
    assert models.SOURCE_LIBRARY_EFFORT_LEVELS == frozenset(
        {"low", "medium", "high"}
    )
    assert models.SOURCE_LIBRARY_NEXT_ACTIONS == frozenset(
        {
            "prepare_material",
            "extract_candidates",
            "review_candidates",
            "promote_approved",
            "revisit_conflict",
            "defer",
            "block",
            "no_action",
        }
    )
    assert models.SOURCE_LIBRARY_BATCH_STATUSES == frozenset(
        {"planned", "active", "review_ready", "completed", "deferred", "blocked"}
    )
    assert models.SOURCE_LIBRARY_VALUE_STATUSES == frozenset(
        {
            "not_started",
            "in_progress",
            "value_produced",
            "non_useful_documented",
            "deferred",
            "blocked",
        }
    )


def test_source_library_dataclasses_construct_with_defaults():
    entry = models.SourceLibraryEntry(
        entry_id="entry_001",
        title="Material One",
        material_type="pdf",
        local_reference="material-one.pdf",
        tracking_status="external_untracked",
        readiness_status="not_started",
    )
    assessment = models.SourcePriorityAssessment(
        assessment_id="priority_001",
        entry_id=entry.entry_id,
        priority_level="medium",
        expected_value="fills_gap",
        rationale="This source may fill a documented evidence gap.",
    )
    batch = models.CurationBatchPlan(
        batch_plan_id="batch_plan_001",
        title="Initial Source Batch",
        goal="Prepare source entries that can fill a documented gap.",
        entry_ids=[entry.entry_id],
    )
    gap = models.EvidenceGapTarget(
        gap_target_id="gap_target_001",
        description="Weak coverage for a rule family.",
    )
    value = models.SourceValueSummary(
        subject_id=entry.entry_id,
        subject_type="source",
    )
    report = models.SourceLibraryProgressReport(
        readiness_counts={"not_started": 1},
        priority_counts={"medium": 1},
        risk_tier_counts={"ordinary": 1},
        rule_family_counts={},
    )

    assert entry.topic_tags == []
    assert entry.risk_tier == "ordinary"
    assert assessment.target_gap_ids == []
    assert assessment.effort_level == "medium"
    assert batch.target_gap_ids == []
    assert batch.status == "planned"
    assert gap.source_entry_ids == []
    assert value.candidate_count == 0
    assert report.ready_for_extraction_count == 0


def test_read_json_list_reports_missing_invalid_and_non_array_payloads(tmp_path):
    with pytest.raises(source_library.SourceLibraryError, match="missing data file"):
        source_library._read_json_list(tmp_path / "missing.json")

    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{", encoding="utf-8")
    with pytest.raises(source_library.SourceLibraryError, match="invalid JSON"):
        source_library._read_json_list(invalid_json)

    object_payload = tmp_path / "object.json"
    _write_json(object_payload, {"not": "a list"})
    with pytest.raises(source_library.SourceLibraryError, match="JSON array"):
        source_library._read_json_list(object_payload)

    scalar_entries = tmp_path / "scalars.json"
    _write_json(scalar_entries, ["not an object"])
    with pytest.raises(
        source_library.SourceLibraryError,
        match="entries must be JSON objects",
    ):
        source_library._read_json_list(scalar_entries)


def test_read_optional_json_list_returns_empty_for_missing_file(tmp_path):
    assert source_library._read_optional_json_list(tmp_path / "missing.json") == []


def test_ensure_unique_rejects_duplicate_ids():
    with pytest.raises(source_library.SourceLibraryError, match="duplicate entry_id"):
        source_library._ensure_unique(["entry_001", "entry_001"], "entry_id")


def test_public_source_library_functions_exist():
    for function_name in (
        "load_source_library_entries",
        "load_source_priority_assessments",
        "load_curation_batch_plans",
        "build_source_library_progress_report",
        "build_source_value_summary",
        "build_batch_value_summary",
        "validate_source_library_quality",
    ):
        assert callable(getattr(source_library, function_name))


def test_load_source_library_entries_loads_current_registered_sources():
    entries = source_library.load_source_library_entries()
    by_id = {entry.entry_id: entry for entry in entries}

    assert len(entries) == 21
    assert set(by_id) == {
        "entry_northeast_blind_peak_pdf",
        "entry_duan_plain_mingxue_outline_pdf",
        "entry_blind_school_secret_pdf",
        "entry_blind_life_manual_pdf",
        "entry_mingli_true_formula_teacher_pdf",
        "entry_mingxue_golden_voice_pdf",
        "entry_fortune_reading_hongfu_qitian_pdf",
        "entry_immortal_fortune_jianghu_secret_pdf",
        "entry_life_death_book_100_pages_pdf",
        "entry_bazi_general_lecture_textbook_pdf",
        "entry_bazi_general_beichen_intro_pdf",
        "entry_bazi_general_ziping_orthodox_pair_pdf",
        "entry_bazi_general_ditiansui_selected_pdf",
        "entry_bazi_general_qiongtong_selected_pdf",
        "entry_bazi_general_true_spirit_positioning_pdf",
        "entry_bazi_general_mingli_wangdoujing_pdf",
        "entry_markdown_source_batch_001",
        "entry_markdown_source_batch_002_core",
        "entry_markdown_source_batch_004",
        "entry_markdown_source_batch_005",
        "entry_knowledge_skeleton",
    }
    assert by_id["entry_blind_life_manual_pdf"].material_id == (
        "material_blind_life_manual_pdf"
    )
    assert by_id["entry_blind_life_manual_pdf"].tracking_status == (
        "external_untracked"
    )
    assert by_id["entry_blind_life_manual_pdf"].readiness_status == (
        "needs_preparation"
    )
    assert "blind_image_method" in by_id["entry_blind_life_manual_pdf"].rule_families
    assert by_id["entry_life_death_book_100_pages_pdf"].risk_tier == "high_risk"
    assert by_id["entry_bazi_general_lecture_textbook_pdf"].material_id == (
        "material_bazi_general_lecture_textbook_pdf"
    )
    assert by_id["entry_bazi_general_lecture_textbook_pdf"].readiness_status == (
        "review_completed"
    )
    assert by_id["entry_bazi_general_ziping_orthodox_pair_pdf"].local_reference == (
        "子平命理正宗电子版上.pdf; 子平命理正宗电子版下.pdf"
    )
    assert by_id["entry_bazi_general_ditiansui_selected_pdf"].material_id == (
        "material_bazi_general_ditiansui_selected_pdf"
    )
    assert by_id["entry_bazi_general_ditiansui_selected_pdf"].local_reference == (
        "滴天髓.pdf"
    )
    assert by_id["entry_bazi_general_ditiansui_selected_pdf"].readiness_status == (
        "review_completed"
    )
    assert by_id["entry_bazi_general_ditiansui_selected_pdf"].next_action == (
        "no_action"
    )
    assert by_id["entry_bazi_general_qiongtong_selected_pdf"].material_id == (
        "material_bazi_general_qiongtong_selected_pdf"
    )
    assert by_id["entry_bazi_general_qiongtong_selected_pdf"].local_reference == (
        "穷通宝鉴/窮通寶鑒.pdf"
    )
    assert by_id["entry_bazi_general_qiongtong_selected_pdf"].readiness_status == (
        "review_completed"
    )
    assert by_id["entry_bazi_general_qiongtong_selected_pdf"].next_action == (
        "no_action"
    )
    assert by_id["entry_bazi_general_true_spirit_positioning_pdf"].material_id == (
        "material_bazi_general_true_spirit_positioning_pdf"
    )
    assert by_id["entry_bazi_general_true_spirit_positioning_pdf"].local_reference == (
        "八字/07、真神在哪里？定位八字真神【万千周易网zhouyi666.com，9米每套 】.pdf"
    )
    assert by_id["entry_bazi_general_true_spirit_positioning_pdf"].readiness_status == (
        "review_completed"
    )
    assert by_id["entry_bazi_general_true_spirit_positioning_pdf"].next_action == (
        "no_action"
    )
    assert by_id["entry_bazi_general_mingli_wangdoujing_pdf"].material_id == (
        "material_bazi_general_mingli_wangdoujing_pdf"
    )
    assert by_id["entry_bazi_general_mingli_wangdoujing_pdf"].local_reference == (
        "1_命理望斗经(1).pdf"
    )
    assert by_id["entry_bazi_general_mingli_wangdoujing_pdf"].readiness_status == (
        "review_completed"
    )
    assert by_id["entry_bazi_general_mingli_wangdoujing_pdf"].next_action == (
        "no_action"
    )


def test_bazi_general_registered_entries_match_registration_prep_metadata():
    from mingli_engine import materials_audit

    prep_items = materials_audit.load_raw_text_source_registration_prep_items()
    entries_by_id = {
        entry.entry_id: entry for entry in source_library.load_source_library_entries()
    }

    for item in prep_items:
        entry = entries_by_id[item.proposed_entry_id]
        assert entry.material_id == item.proposed_material_id
        assert entry.title == item.proposed_title
        assert entry.material_type == item.proposed_material_type
        assert entry.local_reference == "; ".join(item.proposed_local_references)
        assert entry.tracking_status == item.proposed_tracking_status
        assert entry.topic_tags == item.topic_tags
        assert entry.rule_families == item.rule_families
        assert entry.rights_notes == item.rights_notes
        assert entry.risk_tier == item.risk_tier
        assert entry.risk_notes == item.risk_notes
        assert entry.priority_level in {"high", "medium"}
        assert entry.readiness_status in {
            item.proposed_readiness_status,
            "ready_for_extraction",
            "review_completed",
        }
        assert entry.next_action in {
            item.proposed_next_action,
            "extract_candidates",
            "review_candidates",
            "promote_approved",
            "no_action",
        }


def test_bazi_general_registration_does_not_duplicate_gated_identity_records():
    entries = source_library.load_source_library_entries()
    entry_ids = [entry.entry_id for entry in entries]

    assert entry_ids.count("entry_markdown_source_batch_001") == 1
    for gated_fragment in (
        "youran",
        "tianma",
        "huntian",
    ):
        assert not any(
            entry_id.startswith("entry_bazi_general_")
            and gated_fragment in entry_id
            for entry_id in entry_ids
        )


def test_load_source_library_entries_rejects_duplicate_and_invalid_enums(tmp_path):
    entries = [_minimal_entry(), _minimal_entry()]
    _write_json(tmp_path / "source_library_entries.json", entries)

    with pytest.raises(source_library.SourceLibraryError, match="duplicate entry_id"):
        source_library.load_source_library_entries(tmp_path)

    invalid_cases = [
        ("material_type", "unknown", "material_type"),
        ("tracking_status", "missing", "tracking_status"),
        ("readiness_status", "done", "readiness_status"),
        ("priority_level", "urgent", "priority_level"),
        ("next_action", "ship_it", "next_action"),
        ("risk_tier", "danger", "risk_tier"),
        ("rule_families", ["unknown_rule"], "rule_family"),
    ]
    for field_name, value, message in invalid_cases:
        entry = _minimal_entry(f"entry_bad_{field_name}")
        entry[field_name] = value
        _write_json(tmp_path / "source_library_entries.json", [entry])

        with pytest.raises(source_library.SourceLibraryError, match=message):
            source_library.load_source_library_entries(tmp_path)


def test_ready_for_extraction_requires_reviewable_metadata(tmp_path):
    required_fields = (
        "topic_tags",
        "rule_families",
        "source_quality_notes",
        "rights_notes",
    )
    for field_name in required_fields:
        entry = _minimal_entry(f"entry_missing_{field_name}")
        entry.update(
            {
                "readiness_status": "ready_for_extraction",
                "topic_tags": ["blind-school"],
                "rule_families": ["blind_image_method"],
                "source_quality_notes": "Reviewable source notes.",
                "rights_notes": "Do not copy long passages.",
                "next_action": "extract_candidates",
            }
        )
        entry[field_name] = [] if field_name in {"topic_tags", "rule_families"} else ""
        _write_json(tmp_path / "source_library_entries.json", [entry])

        with pytest.raises(source_library.SourceLibraryError, match=field_name):
            source_library.load_source_library_entries(tmp_path)


def test_external_untracked_entries_do_not_require_raw_file_access(tmp_path):
    entry = _minimal_entry("entry_external_only")
    entry["local_reference"] = str(tmp_path / "missing-user-source.pdf")
    entry["tracking_status"] = "external_untracked"
    _write_json(tmp_path / "source_library_entries.json", [entry])

    loaded = source_library.load_source_library_entries(tmp_path)

    assert loaded[0].entry_id == "entry_external_only"
    assert loaded[0].local_reference.endswith("missing-user-source.pdf")
    assert not Path(loaded[0].local_reference).exists()


def test_high_risk_and_terminal_entries_require_durable_reasons(tmp_path):
    high_risk_entry = _minimal_entry("entry_high_risk")
    high_risk_entry["risk_tier"] = "high_risk"
    _write_json(tmp_path / "source_library_entries.json", [high_risk_entry])

    with pytest.raises(source_library.SourceLibraryError, match="risk_notes"):
        source_library.load_source_library_entries(tmp_path)

    for status in ("exhausted", "deferred", "duplicate", "blocked"):
        terminal_entry = _minimal_entry(f"entry_{status}")
        terminal_entry["readiness_status"] = status
        terminal_entry["outcome_reason"] = "n/a"
        _write_json(tmp_path / "source_library_entries.json", [terminal_entry])

        with pytest.raises(source_library.SourceLibraryError, match="outcome_reason"):
            source_library.load_source_library_entries(tmp_path)


def test_build_source_library_progress_report_counts_registered_entries(tmp_path):
    ready = _minimal_entry("entry_ready")
    ready.update(
        {
            "readiness_status": "ready_for_extraction",
            "topic_tags": ["blind-school"],
            "rule_families": ["blind_image_method", "high_risk_signal"],
            "source_quality_notes": "Reviewable source notes.",
            "rights_notes": "Do not copy long passages.",
            "risk_tier": "high_risk",
            "risk_notes": ["May contain high-risk signal language."],
            "priority_level": "high",
            "next_action": "extract_candidates",
        }
    )
    blocked = _minimal_entry("entry_blocked")
    blocked.update(
        {
            "readiness_status": "blocked",
            "priority_level": "deferred",
            "next_action": "block",
            "outcome_reason": "Blocked until source identity can be clarified.",
        }
    )
    _write_json(tmp_path / "source_library_entries.json", [ready, blocked])

    report = source_library.build_source_library_progress_report(tmp_path)

    assert report.readiness_counts == {"ready_for_extraction": 1, "blocked": 1}
    assert report.priority_counts == {"high": 1, "deferred": 1}
    assert report.risk_tier_counts == {"high_risk": 1, "ordinary": 1}
    assert report.rule_family_counts == {
        "blind_image_method": 1,
        "high_risk_signal": 1,
    }
    assert report.ready_for_extraction_count == 1
    assert report.high_priority_count == 1
    assert report.blocked_or_deferred_count == 1
    assert report.high_risk_entry_ids == ["entry_ready"]


def test_load_source_priority_assessments_loads_default_assessments():
    assessments = source_library.load_source_priority_assessments()
    by_id = {assessment.assessment_id: assessment for assessment in assessments}

    assert len(assessments) == 19
    assert "priority_blind_life_manual_001" in by_id
    assert "priority_bazi_general_lecture_textbook_001" in by_id
    assert "priority_bazi_general_ziping_orthodox_pair_001" in by_id
    assert by_id["priority_bazi_general_ditiansui_selected_001"].entry_id == (
        "entry_bazi_general_ditiansui_selected_pdf"
    )
    assert by_id["priority_bazi_general_qiongtong_selected_001"].entry_id == (
        "entry_bazi_general_qiongtong_selected_pdf"
    )
    assert by_id["priority_bazi_general_true_spirit_positioning_001"].entry_id == (
        "entry_bazi_general_true_spirit_positioning_pdf"
    )
    assert by_id["priority_bazi_general_true_spirit_positioning_001"].expected_value == (
        "broadens_school_coverage"
    )
    assert by_id["priority_bazi_general_mingli_wangdoujing_001"].entry_id == (
        "entry_bazi_general_mingli_wangdoujing_pdf"
    )
    assert by_id["priority_bazi_general_mingli_wangdoujing_001"].target_rule_families == [
        "branch_interaction"
    ]
    assert by_id["priority_blind_life_manual_001"].entry_id == (
        "entry_blind_life_manual_pdf"
    )
    assert by_id["priority_blind_life_manual_001"].priority_level == "high"
    assert by_id["priority_blind_life_manual_001"].expected_value == (
        "improves_high_risk_boundary"
    )
    assert "high_risk_signal" in by_id[
        "priority_blind_life_manual_001"
    ].target_rule_families


def test_priority_assessments_validate_references_targets_and_high_priority(
    tmp_path,
):
    entry = _minimal_entry("entry_high")
    entry["priority_level"] = "high"
    _write_json(tmp_path / "source_library_entries.json", [entry])
    _write_json(tmp_path / "source_priority_assessments.json", [])

    with pytest.raises(source_library.SourceLibraryError, match="priority assessment"):
        source_library.load_source_priority_assessments(tmp_path)

    assessment = _minimal_assessment("priority_missing_entry")
    assessment["entry_id"] = "missing_entry"
    _write_json(tmp_path / "source_priority_assessments.json", [assessment])

    with pytest.raises(source_library.SourceLibraryError, match="unknown entry"):
        source_library.load_source_priority_assessments(tmp_path)

    assessment = _minimal_assessment("priority_no_targets")
    assessment["priority_level"] = "high"
    assessment["target_gap_ids"] = []
    assessment["target_rule_families"] = []
    _write_json(tmp_path / "source_priority_assessments.json", [assessment])

    with pytest.raises(source_library.SourceLibraryError, match="target"):
        source_library.load_source_priority_assessments(tmp_path)


def test_priority_assessments_validate_source_quality_and_high_risk_boundary(
    tmp_path,
):
    entry = _minimal_entry("entry_critical")
    entry["priority_level"] = "critical"
    entry["risk_tier"] = "high_risk"
    entry["risk_notes"] = ["Contains high-risk source material."]
    _write_json(tmp_path / "source_library_entries.json", [entry])

    assessment = _minimal_assessment("priority_critical_needs_recheck")
    assessment["entry_id"] = "entry_critical"
    assessment["priority_level"] = "critical"
    assessment["source_quality"] = "needs_recheck"
    _write_json(tmp_path / "source_priority_assessments.json", [assessment])

    with pytest.raises(source_library.SourceLibraryError, match="needs_recheck"):
        source_library.load_source_priority_assessments(tmp_path)

    assessment["source_quality"] = "moderate"
    assessment["risk_tier"] = "high_risk"
    assessment["rationale"] = "High value source."
    _write_json(tmp_path / "source_priority_assessments.json", [assessment])

    with pytest.raises(source_library.SourceLibraryError, match="review boundary"):
        source_library.load_source_priority_assessments(tmp_path)


def test_load_curation_batch_plans_loads_default_batch_plans():
    plans = source_library.load_curation_batch_plans()
    by_id = {plan.batch_plan_id: plan for plan in plans}

    assert set(by_id) == {
        "batch_plan_high_risk_boundaries_001",
        "batch_plan_blind_image_method_001",
    }
    high_risk_plan = by_id["batch_plan_high_risk_boundaries_001"]
    assert high_risk_plan.risk_boundary == "high_risk"
    assert "entry_blind_life_manual_pdf" in high_risk_plan.entry_ids
    assert "high_risk_signal" in high_risk_plan.target_rule_families


def test_curation_batch_plans_require_entries_targets_outputs_and_valid_status(
    tmp_path,
):
    ready = _minimal_entry("entry_ready")
    ready.update(
        {
            "readiness_status": "ready_for_extraction",
            "topic_tags": ["blind-school"],
            "rule_families": ["blind_image_method"],
            "source_quality_notes": "Reviewable source notes.",
            "rights_notes": "Do not copy long passages.",
        }
    )
    _write_json(tmp_path / "source_library_entries.json", [ready])
    _write_json(tmp_path / "source_priority_assessments.json", [])

    invalid_cases = [
        ("entry_ids", [], "entry_ids"),
        ("target_gap_ids", [], "target"),
        ("expected_output", [], "expected_output"),
        ("status", "done", "status"),
    ]
    for field_name, value, message in invalid_cases:
        batch = _minimal_batch(f"batch_bad_{field_name}")
        batch[field_name] = value
        if field_name == "target_gap_ids":
            batch["target_rule_families"] = []
        _write_json(tmp_path / "curation_batch_plans.json", [batch])

        with pytest.raises(source_library.SourceLibraryError, match=message):
            source_library.load_curation_batch_plans(tmp_path)


def test_high_risk_batch_plans_require_risk_notes_on_included_entries(tmp_path):
    risky = _minimal_entry("entry_risky")
    risky.update(
        {
            "readiness_status": "ready_for_extraction",
            "topic_tags": ["life-risk"],
            "rule_families": ["high_risk_signal"],
            "source_quality_notes": "Reviewable high-risk source notes.",
            "rights_notes": "Do not copy long passages.",
            "risk_tier": "high_risk",
            "risk_notes": [],
        }
    )
    _write_json(tmp_path / "source_library_entries.json", [risky])
    batch = _minimal_batch("batch_high_risk")
    batch.update(
        {
            "entry_ids": ["entry_risky"],
            "target_gap_ids": [],
            "target_rule_families": ["high_risk_signal"],
            "risk_boundary": "high_risk",
        }
    )
    _write_json(tmp_path / "curation_batch_plans.json", [batch])

    with pytest.raises(source_library.SourceLibraryError, match="risk_notes"):
        source_library.load_curation_batch_plans(tmp_path)


def test_list_next_source_candidates_orders_ready_sources_by_priority():
    next_sources = source_library.list_next_source_candidates(limit=5)

    assert next_sources == [
        "entry_northeast_blind_peak_pdf",
        "entry_mingli_true_formula_teacher_pdf",
        "entry_life_death_book_100_pages_pdf",
        "entry_markdown_source_batch_002_core",
        "entry_markdown_source_batch_001",
    ]


def test_source_value_summary_counts_linked_downstream_outcomes(tmp_path):
    entry = _value_entry("entry_value_source", "material_value_source")
    promoted = _candidate_extract(
        "candidate_promoted_001",
        "material_value_source",
        "promoted",
        related_conflict_ids=["conflict_value_001"],
        related_gap_ids=["gap_closed_001"],
    )
    rejected = _candidate_extract(
        "candidate_rejected_001",
        "material_value_source",
        "rejected",
        related_gap_ids=["gap_remaining_001"],
    )
    blocked = _candidate_extract(
        "candidate_blocked_001",
        "material_value_source",
        "blocked",
    )
    source_library_dir = _write_value_summary_fixture(
        tmp_path,
        entries=[entry],
        candidates=[promoted, rejected, blocked],
        decisions=[
            _review_decision("candidate_promoted_001", "approved"),
            _review_decision("candidate_rejected_001", "rejected"),
            _review_decision("candidate_blocked_001", "blocked"),
        ],
        promotion_batches=[
            {
                "promotion_batch_id": "promotion_value_001",
                "candidate_ids": ["candidate_promoted_001"],
                "target_evidence_ids": ["evidence_promoted_001"],
                "review_status": "reviewed",
                "review_notes": "Reviewed promotion batch for value summary.",
                "unresolved_issues": [],
            }
        ],
        evidence_units=[_formal_evidence("evidence_promoted_001")],
    )

    summary = source_library.build_source_value_summary(
        "entry_value_source",
        source_library_dir,
    )

    assert summary.candidate_count == 3
    assert summary.approved_candidate_count == 1
    assert summary.rejected_or_blocked_count == 2
    assert summary.conflict_count == 1
    assert summary.gap_count == 2
    assert summary.promoted_evidence_count == 1
    assert summary.value_status == "value_produced"


def test_source_value_summary_keeps_sources_without_downstream_from_value_produced(
    tmp_path,
):
    ready = _value_entry(
        "entry_ready_without_candidates",
        "material_ready_without_candidates",
        readiness_status="ready_for_extraction",
        next_action="extract_candidates",
    )
    in_progress = _value_entry(
        "entry_in_progress_without_candidates",
        "material_in_progress_without_candidates",
        readiness_status="in_extraction",
        next_action="review_candidates",
    )
    source_library_dir = _write_value_summary_fixture(
        tmp_path,
        entries=[ready, in_progress],
    )

    ready_summary = source_library.build_source_value_summary(
        "entry_ready_without_candidates",
        source_library_dir,
    )
    in_progress_summary = source_library.build_source_value_summary(
        "entry_in_progress_without_candidates",
        source_library_dir,
    )

    assert ready_summary.candidate_count == 0
    assert ready_summary.value_status == "not_started"
    assert in_progress_summary.candidate_count == 0
    assert in_progress_summary.value_status == "in_progress"
    assert "value_produced" not in {
        ready_summary.value_status,
        in_progress_summary.value_status,
    }


def test_approved_unpromoted_candidates_do_not_count_as_formal_evidence(tmp_path):
    entry = _value_entry(
        "entry_approved_unpromoted",
        "material_approved_unpromoted",
        next_action="promote_approved",
    )
    candidate = _candidate_extract(
        "candidate_approved_unpromoted_001",
        "material_approved_unpromoted",
        "approved",
    )
    source_library_dir = _write_value_summary_fixture(
        tmp_path,
        entries=[entry],
        candidates=[candidate],
        decisions=[_review_decision("candidate_approved_unpromoted_001", "approved")],
    )

    summary = source_library.build_source_value_summary(
        "entry_approved_unpromoted",
        source_library_dir,
    )

    assert summary.candidate_count == 1
    assert summary.approved_candidate_count == 1
    assert summary.promoted_evidence_count == 0
    assert summary.value_status == "value_produced"


def test_gap_only_returned_candidates_remain_in_progress(tmp_path):
    entry = _value_entry(
        "entry_gap_only",
        "material_gap_only",
        next_action="review_candidates",
    )
    candidate = _candidate_extract(
        "candidate_gap_only_001",
        "material_gap_only",
        "returned",
        related_gap_ids=["gap_gap_only_001"],
    )
    source_library_dir = _write_value_summary_fixture(
        tmp_path,
        entries=[entry],
        candidates=[candidate],
        decisions=[_review_decision("candidate_gap_only_001", "returned")],
    )

    summary = source_library.build_source_value_summary(
        "entry_gap_only",
        source_library_dir,
    )

    assert summary.candidate_count == 1
    assert summary.approved_candidate_count == 0
    assert summary.gap_count == 1
    assert summary.promoted_evidence_count == 0
    assert summary.value_status == "in_progress"


def test_terminal_source_outcomes_remain_visible_with_durable_reasons(tmp_path):
    terminal_entries = [
        _value_entry(
            "entry_duplicate",
            "material_duplicate",
            readiness_status="duplicate",
            next_action="no_action",
            outcome_reason="Reviewed as duplicate of an existing source-library item.",
        ),
        _value_entry(
            "entry_deferred",
            "material_deferred",
            readiness_status="deferred",
            next_action="defer",
            outcome_reason="Deferred until a better edition or locator is available.",
        ),
        _value_entry(
            "entry_exhausted",
            "material_exhausted",
            readiness_status="exhausted",
            next_action="no_action",
            outcome_reason="Reviewed and exhausted without producing usable candidates.",
        ),
        _value_entry(
            "entry_blocked",
            "material_blocked",
            readiness_status="blocked",
            next_action="block",
            outcome_reason="Blocked until source rights and locator boundaries are clear.",
        ),
    ]
    source_library_dir = _write_value_summary_fixture(
        tmp_path,
        entries=terminal_entries,
    )

    summaries = {
        entry.entry_id: source_library.build_source_value_summary(
            entry.entry_id,
            source_library_dir,
        )
        for entry in source_library.load_source_library_entries(source_library_dir)
    }

    assert summaries["entry_duplicate"].value_status == "non_useful_documented"
    assert summaries["entry_exhausted"].value_status == "non_useful_documented"
    assert summaries["entry_deferred"].value_status == "deferred"
    assert summaries["entry_blocked"].value_status == "blocked"
    assert all(entry["outcome_reason"] for entry in terminal_entries)


def test_completed_batch_value_summary_aggregates_entries_and_next_focus(tmp_path):
    improved = _value_entry("entry_batch_improved", "material_batch_improved")
    remaining_gap = _value_entry(
        "entry_batch_remaining_gap",
        "material_batch_remaining_gap",
        next_action="review_candidates",
    )
    approved = _candidate_extract(
        "candidate_batch_approved_001",
        "material_batch_improved",
        "promoted",
        rule_family="blind_image_method",
    )
    returned_gap = _candidate_extract(
        "candidate_batch_gap_001",
        "material_batch_remaining_gap",
        "returned",
        rule_family="high_risk_signal",
        related_gap_ids=["gap_batch_remaining_001"],
    )
    batch = _minimal_batch("batch_plan_completed_value_001")
    batch.update(
        {
            "entry_ids": ["entry_batch_improved", "entry_batch_remaining_gap"],
            "target_gap_ids": ["gap_batch_remaining_001"],
            "target_rule_families": ["blind_image_method", "high_risk_signal"],
            "status": "completed",
            "completion_summary": (
                "Completed review found one promoted evidence path and one "
                "remaining high-risk gap."
            ),
            "recommended_next_batch": "Focus next on high-risk boundary gaps.",
        }
    )
    source_library_dir = _write_value_summary_fixture(
        tmp_path,
        entries=[improved, remaining_gap],
        candidates=[approved, returned_gap],
        decisions=[
            _review_decision("candidate_batch_approved_001", "approved"),
            _review_decision("candidate_batch_gap_001", "returned"),
        ],
        promotion_batches=[
            {
                "promotion_batch_id": "promotion_batch_value_001",
                "candidate_ids": ["candidate_batch_approved_001"],
                "target_evidence_ids": ["evidence_batch_promoted_001"],
                "review_status": "reviewed",
                "review_notes": "Reviewed promotion batch for batch summary.",
                "unresolved_issues": [],
            }
        ],
        batch_plans=[batch],
        evidence_units=[_formal_evidence("evidence_batch_promoted_001")],
    )

    summary = source_library.build_batch_value_summary(
        "batch_plan_completed_value_001",
        source_library_dir,
    )

    assert summary.subject_type == "batch"
    assert summary.candidate_count == 2
    assert summary.approved_candidate_count == 1
    assert summary.gap_count == 1
    assert summary.promoted_evidence_count == 1
    assert summary.value_status == "value_produced"
    assert summary.recommended_next_action == "Focus next on high-risk boundary gaps."


def test_source_library_quality_rejects_report_evidence_boundary_leaks(tmp_path):
    entry = _minimal_entry("entry_report_boundary")
    entry["source_quality_notes"] = (
        "This registered source should be treated as formal report evidence."
    )
    batch = _minimal_batch("batch_report_boundary")
    batch["entry_ids"] = ["entry_report_boundary"]
    batch["expected_output"] = ["candidate_extracts", "formal_evidence"]
    _write_json(tmp_path / "source_library_entries.json", [entry])
    _write_json(tmp_path / "source_priority_assessments.json", [])
    _write_json(tmp_path / "curation_batch_plans.json", [batch])

    failures = source_library.validate_source_library_quality(tmp_path)

    assert any("report evidence boundary" in failure for failure in failures)


def test_source_library_quality_rejects_long_copied_source_passages(tmp_path):
    entry = _minimal_entry("entry_long_copied_passage")
    entry["source_quality_notes"] = " ".join(
        ["copied source passage with too much source text"] * 20
    )
    _write_json(tmp_path / "source_library_entries.json", [entry])
    _write_json(tmp_path / "source_priority_assessments.json", [])
    _write_json(tmp_path / "curation_batch_plans.json", [])

    failures = source_library.validate_source_library_quality(tmp_path)

    assert any("too long" in failure for failure in failures)
