import json
import time
from pathlib import Path

import pytest

from mingli_engine import extraction_queue_intake
from mingli_engine import models


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _minimal_work_package(package_id: str = "package_001") -> dict[str, object]:
    return {
        "package_id": package_id,
        "package_label": "Next extraction package",
        "source_queue_snapshot_ids": [],
        "selected_task_ids": [],
        "backlog_record_ids": [],
        "status": "planned",
        "created_at": "2026-05-31",
        "updated_at": "2026-05-31",
        "notes": "Foundational fixture.",
    }


def _minimal_extraction_task(
    task_id: str = "task_001",
    package_id: str = "package_001",
) -> dict[str, object]:
    return {
        "task_id": task_id,
        "package_id": package_id,
        "queue_item_id": "queue_001",
        "audit_id": "audit_001",
        "source_library_entry_id": "entry_001",
        "intended_source_material_id": "material_001",
        "priority_level": "medium",
        "priority_rationale": "Ready queue item with clear review boundary.",
        "target_rule_families": ["blind_image_method"],
        "target_gap_ids": [],
        "risk_boundary": "ordinary",
        "locator_requirement": "page_or_section",
        "source_quality_note": "Review source locator before extraction.",
        "rights_note": "Do not copy long passages.",
        "pre_extraction_checks": ["confirm source locator"],
        "overlap_warnings": [],
        "status": "planned",
        "created_at": "2026-05-31",
        "updated_at": "2026-05-31",
    }


def _minimal_candidate_draft_slot(
    draft_slot_id: str = "slot_001",
    task_id: str = "task_001",
) -> dict[str, object]:
    return {
        "draft_slot_id": draft_slot_id,
        "task_id": task_id,
        "intended_candidate_label": "Future manual candidate",
        "target_rule_family": "blind_image_method",
        "target_gap_id": "",
        "locator_requirement": "page_or_section",
        "expected_review_notes": ["Record exact locator during extraction."],
        "risk_boundary": "ordinary",
        "safety_requirements": ["No absolute destiny language."],
        "status": "planned",
    }


def _minimal_backlog_record(
    backlog_id: str = "backlog_001",
    package_id: str = "package_001",
) -> dict[str, object]:
    return {
        "backlog_id": backlog_id,
        "package_id": package_id,
        "queue_item_id": "queue_002",
        "audit_id": "audit_002",
        "backlog_type": "registration",
        "missing_prerequisites": ["source_library_registration"],
        "durable_reason": "Source-library registration is required before extraction.",
        "recommended_action": "register_source",
        "risk_boundary": "ordinary",
        "status": "planned",
        "created_at": "2026-05-31",
        "updated_at": "2026-05-31",
    }


def _minimal_candidate_extract(
    candidate_id: str = "candidate_overlap_001",
    *,
    material_id: str = "material_001",
    status: str = "pending_review",
    proposed_rule_family: str = "blind_image_method",
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "material_id": material_id,
        "source_locator": f"review-note:{candidate_id}",
        "extracted_meaning": "A concise conditional candidate signal.",
        "proposed_rule_family": proposed_rule_family,
        "risk_tier": "ordinary",
        "status": status,
        "proposed_limitations": ["Use only as conditional traditional evidence."],
        "short_quote": "",
        "related_evidence_ids": [],
        "related_conflict_ids": [],
        "related_gap_ids": [],
        "duplicate_of": "",
        "created_by": "maintainer",
        "created_at": "2026-05-28",
    }


def _write_extraction_queue_intake_fixture(
    tmp_path: Path,
    *,
    packages: list[dict[str, object]] | None = None,
    tasks: list[dict[str, object]] | None = None,
    draft_slots: list[dict[str, object]] | None = None,
    backlog_records: list[dict[str, object]] | None = None,
) -> Path:
    data_dir = tmp_path / "extraction_queue_intake"
    data_dir.mkdir(exist_ok=True)
    _write_json(data_dir / "extraction_work_packages.json", packages or [])
    _write_json(data_dir / "extraction_tasks.json", tasks or [])
    _write_json(data_dir / "candidate_draft_slots.json", draft_slots or [])
    _write_json(
        data_dir / "prerequisite_backlog_records.json",
        backlog_records or [],
    )
    return data_dir


def _minimal_audit_record(audit_id: str = "audit_001") -> dict[str, object]:
    return {
        "audit_id": audit_id,
        "canonical_title": "Material One",
        "alternate_titles": [],
        "material_scope": "bazi",
        "primary_material_type": "pdf",
        "representations": ["repr_001"],
        "source_library_entry_id": "entry_001",
        "source_identity_confidence": "confirmed",
        "preparation_state": "ready_for_extraction_review",
        "source_boundary": "external_untracked",
        "topic_tags": ["blind-school"],
        "rule_families": ["blind_image_method"],
        "risk_tier": "ordinary",
        "risk_notes": [],
        "rights_notes": "Do not copy long passages.",
        "missing_prerequisites": [],
        "recommended_next_action": "extract_candidates",
        "outcome_reason": "",
        "created_at": "2026-05-31",
        "updated_at": "2026-05-31",
    }


def _minimal_representation(
    representation_id: str = "repr_001",
    audit_id: str = "audit_001",
) -> dict[str, object]:
    return {
        "representation_id": representation_id,
        "audit_id": audit_id,
        "representation_type": "root_pdf",
        "local_reference": "material-one.pdf",
        "tracking_status": "external_untracked",
        "text_quality": "usable",
        "locator_quality": "page_or_section",
        "size_hint": "root PDF present",
        "modified_hint": "",
        "contains_images": False,
        "notes": "External preparation material.",
    }


def _minimal_alignment(
    alignment_id: str = "align_001",
    audit_id: str = "audit_001",
) -> dict[str, object]:
    return {
        "alignment_id": alignment_id,
        "audit_id": audit_id,
        "match_type": "exact",
        "source_library_entry_id": "entry_001",
        "source_material_id": "material_001",
        "confidence": "strong",
        "evidence": "The audit record and source-library entry describe the same source.",
        "registration_recommendation": "none",
        "duplicate_or_variant_notes": "",
        "reviewer": "maintainer",
        "reviewed_at": "2026-05-31",
    }


def _minimal_readiness(
    readiness_id: str = "ready_001",
    audit_id: str = "audit_001",
) -> dict[str, object]:
    return {
        "readiness_id": readiness_id,
        "audit_id": audit_id,
        "readiness_state": "ready_for_extraction_review",
        "text_preparation_status": "prepared",
        "locator_confidence": "strong",
        "source_quality": "strong",
        "risk_boundary": "ordinary",
        "missing_prerequisites": [],
        "ready_reasons": ["Source-library entry, rights notes, and targets are present."],
        "blockers": [],
        "recommended_next_action": "extract_candidates",
        "assessed_by": "maintainer",
        "assessed_at": "2026-05-31",
    }


def _minimal_queue_item(
    queue_item_id: str = "queue_001",
    audit_id: str = "audit_001",
) -> dict[str, object]:
    return {
        "queue_item_id": queue_item_id,
        "audit_id": audit_id,
        "queue_type": "extraction_ready",
        "priority_level": "medium",
        "priority_rationale": "Ready source with enough metadata for manual extraction.",
        "target_rule_families": ["blind_image_method"],
        "target_gap_ids": [],
        "risk_boundary": "ordinary",
        "pre_extraction_checks": ["confirm source locator"],
        "recommended_action": "extract_candidates",
        "depends_on": [],
        "status": "planned",
        "created_at": "2026-05-31",
        "updated_at": "2026-05-31",
    }


def _minimal_source_library_entry(entry_id: str = "entry_001") -> dict[str, object]:
    return {
        "entry_id": entry_id,
        "title": "Material One",
        "material_type": "pdf",
        "local_reference": "material-one.pdf",
        "tracking_status": "external_untracked",
        "readiness_status": "ready_for_extraction",
        "material_id": "material_001",
        "topic_tags": ["blind-school"],
        "rule_families": ["blind_image_method"],
        "source_quality_notes": "Reviewed enough for manual extraction planning.",
        "rights_notes": "Do not copy long passages.",
        "risk_tier": "ordinary",
        "risk_notes": [],
        "priority_level": "medium",
        "next_action": "extract_candidates",
        "outcome_reason": "",
        "created_at": "2026-05-31",
        "updated_at": "2026-05-31",
    }


def _minimal_source_material(material_id: str = "material_001") -> dict[str, object]:
    return {
        "material_id": material_id,
        "title": "Material One",
        "material_type": "pdf",
        "file_label": "material-one.pdf",
        "tracking_status": "external_untracked",
        "preparation_status": "partially_reviewed",
        "related_source_id": "",
        "scope_notes": "Source material for manual extraction planning.",
        "rights_notes": "Do not copy long passages.",
        "gap_reason": "",
    }


def _write_us1_fixture(
    tmp_path: Path,
    *,
    packages: list[dict[str, object]] | None = None,
    tasks: list[dict[str, object]] | None = None,
    draft_slots: list[dict[str, object]] | None = None,
    audit_records: list[dict[str, object]] | None = None,
    representations: list[dict[str, object]] | None = None,
    alignments: list[dict[str, object]] | None = None,
    readiness: list[dict[str, object]] | None = None,
    queue_items: list[dict[str, object]] | None = None,
    source_entries: list[dict[str, object]] | None = None,
    source_materials: list[dict[str, object]] | None = None,
    backlog_records: list[dict[str, object]] | None = None,
    candidate_extracts: list[dict[str, object]] | None = None,
) -> Path:
    intake_dir = _write_extraction_queue_intake_fixture(
        tmp_path,
        packages=packages if packages is not None else [
            {
                **_minimal_work_package(),
                "source_queue_snapshot_ids": ["queue_001"],
                "selected_task_ids": ["task_001"],
            }
        ],
        tasks=tasks if tasks is not None else [_minimal_extraction_task()],
        draft_slots=draft_slots,
        backlog_records=backlog_records,
    )

    materials_dir = tmp_path / "materials_audit"
    materials_dir.mkdir(exist_ok=True)
    _write_json(
        materials_dir / "material_audit_records.json",
        audit_records if audit_records is not None else [_minimal_audit_record()],
    )
    _write_json(
        materials_dir / "material_representations.json",
        representations if representations is not None else [_minimal_representation()],
    )
    _write_json(
        materials_dir / "source_alignment_findings.json",
        alignments if alignments is not None else [_minimal_alignment()],
    )
    _write_json(
        materials_dir / "preparation_readiness_findings.json",
        readiness if readiness is not None else [_minimal_readiness()],
    )
    _write_json(
        materials_dir / "extraction_queue_items.json",
        queue_items if queue_items is not None else [_minimal_queue_item()],
    )

    source_library_dir = tmp_path / "source_library"
    source_library_dir.mkdir(exist_ok=True)
    _write_json(
        source_library_dir / "source_library_entries.json",
        source_entries if source_entries is not None else [_minimal_source_library_entry()],
    )

    source_intake_dir = tmp_path / "source_intake"
    source_intake_dir.mkdir(exist_ok=True)
    _write_json(
        source_intake_dir / "source_materials.json",
        source_materials if source_materials is not None else [_minimal_source_material()],
    )
    _write_json(
        source_intake_dir / "candidate_extracts.json",
        candidate_extracts if candidate_extracts is not None else [],
    )
    _write_json(source_intake_dir / "review_decisions.json", [])
    _write_json(source_intake_dir / "promotion_batches.json", [])

    return intake_dir


def _backlog_fixture_parts(
    *,
    backlog_type: str = "registration",
    queue_type: str = "registration_backlog",
    readiness_state: str = "needs_source_registration",
    recommended_action: str = "register_source",
    missing_prerequisites: list[str] | None = None,
    risk_boundary: str = "ordinary",
    status: str = "planned",
) -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    prerequisites = (
        missing_prerequisites
        if missing_prerequisites is not None
        else ["source_library_registration"]
    )
    package = {
        **_minimal_work_package(),
        "source_queue_snapshot_ids": ["queue_002"],
        "selected_task_ids": [],
        "backlog_record_ids": ["backlog_001"],
    }
    record = {
        **_minimal_backlog_record(),
        "backlog_type": backlog_type,
        "missing_prerequisites": prerequisites,
        "recommended_action": recommended_action,
        "risk_boundary": risk_boundary,
        "status": status,
    }
    queue_item = {
        **_minimal_queue_item("queue_002", "audit_002"),
        "queue_type": queue_type,
        "priority_level": "high" if risk_boundary == "high_risk" else "medium",
        "target_rule_families": ["high_risk_signal"]
        if risk_boundary == "high_risk"
        else [],
        "target_gap_ids": prerequisites,
        "risk_boundary": risk_boundary,
        "pre_extraction_checks": [
            "complete prerequisite review before extraction",
        ],
        "recommended_action": recommended_action,
        "depends_on": prerequisites,
        "status": status,
    }
    readiness = {
        **_minimal_readiness("ready_002", "audit_002"),
        "readiness_state": readiness_state,
        "risk_boundary": risk_boundary,
        "missing_prerequisites": prerequisites,
        "ready_reasons": [],
        "blockers": [
            "Prerequisite backlog must be resolved before routine extraction.",
        ],
        "recommended_next_action": recommended_action,
    }
    return package, record, queue_item, readiness


def test_extraction_queue_intake_constants_cover_contract_values():
    assert models.EXTRACTION_PACKAGE_STATUSES == frozenset(
        {"planned", "active", "completed", "deferred", "blocked"}
    )
    assert models.EXTRACTION_TASK_STATUSES == frozenset(
        {"planned", "active", "completed", "deferred", "blocked"}
    )
    assert models.CANDIDATE_DRAFT_SLOT_STATUSES == frozenset(
        {"planned", "ready_for_manual_extraction", "deferred", "blocked"}
    )
    assert models.PREREQUISITE_BACKLOG_TYPES == frozenset(
        {
            "registration",
            "preparation",
            "locator_review",
            "risk_review",
            "deferred",
            "blocked",
        }
    )
    assert models.EXTRACTION_PACKAGE_PRIORITY_LEVELS == frozenset(
        {"critical", "high", "medium", "low"}
    )
    assert models.EXTRACTION_PACKAGE_RISK_BOUNDARIES == models.RISK_TIERS
    assert models.EXTRACTION_PACKAGE_LOCATOR_REQUIREMENTS == frozenset(
        {"file_only", "heading", "line_window", "page_or_section", "review_anchor"}
    )
    assert models.EXTRACTION_PACKAGE_MANUAL_ACTIONS == frozenset(
        {
            "extract_candidates",
            "register_source",
            "clarify_identity",
            "prepare_text",
            "review_cleaned_text",
            "risk_review",
            "defer",
            "block",
            "no_action",
        }
    )


def test_loader_reports_missing_file(tmp_path):
    data_dir = tmp_path / "extraction_queue_intake"
    data_dir.mkdir()

    with pytest.raises(
        extraction_queue_intake.ExtractionQueueIntakeError,
        match="missing data file",
    ):
        extraction_queue_intake.load_extraction_work_packages(data_dir)


def test_loader_reports_malformed_json(tmp_path):
    data_dir = tmp_path / "extraction_queue_intake"
    data_dir.mkdir()
    (data_dir / "extraction_work_packages.json").write_text("{", encoding="utf-8")

    with pytest.raises(
        extraction_queue_intake.ExtractionQueueIntakeError,
        match="invalid JSON",
    ):
        extraction_queue_intake.load_extraction_work_packages(data_dir)


def test_loader_requires_json_array(tmp_path):
    data_dir = tmp_path / "extraction_queue_intake"
    data_dir.mkdir()
    _write_json(data_dir / "extraction_work_packages.json", {})

    with pytest.raises(
        extraction_queue_intake.ExtractionQueueIntakeError,
        match="JSON array",
    ):
        extraction_queue_intake.load_extraction_work_packages(data_dir)


def test_loader_requires_json_object_entries(tmp_path):
    data_dir = tmp_path / "extraction_queue_intake"
    data_dir.mkdir()
    _write_json(data_dir / "extraction_work_packages.json", ["package_001"])

    with pytest.raises(
        extraction_queue_intake.ExtractionQueueIntakeError,
        match="JSON objects",
    ):
        extraction_queue_intake.load_extraction_work_packages(data_dir)


def test_public_loader_stubs_return_empty_collections(tmp_path):
    data_dir = _write_extraction_queue_intake_fixture(tmp_path)

    assert extraction_queue_intake.load_extraction_work_packages(data_dir) == []
    assert extraction_queue_intake.load_extraction_tasks(data_dir) == []
    assert extraction_queue_intake.load_candidate_draft_slots(data_dir) == []
    assert extraction_queue_intake.load_prerequisite_backlog_records(data_dir) == []
    assert extraction_queue_intake.validate_extraction_package_quality(data_dir) == []

    summary = extraction_queue_intake.build_package_progress_summary(data_dir)

    assert summary == models.PackageProgressSummary(
        package_counts={},
        task_counts={},
        draft_slot_counts={},
        backlog_counts={},
        risk_boundary_counts={},
        overlap_warning_count=0,
        extraction_task_count=0,
        candidate_draft_slot_count=0,
        blocked_or_deferred_count=0,
        next_manual_action_ids=[],
    )


def test_package_progress_summary_loads_under_300ms(tmp_path):
    data_dir = _write_extraction_queue_intake_fixture(tmp_path)

    started_at = time.perf_counter()
    summary = extraction_queue_intake.build_package_progress_summary(data_dir)
    elapsed = time.perf_counter() - started_at

    assert elapsed < 0.3
    assert summary.extraction_task_count == 0
    assert summary.candidate_draft_slot_count == 0


def test_valid_work_package_and_extraction_task_load_with_trace_links(tmp_path):
    data_dir = _write_us1_fixture(tmp_path)

    packages = extraction_queue_intake.load_extraction_work_packages(data_dir)
    tasks = extraction_queue_intake.load_extraction_tasks(data_dir)

    assert [package.package_id for package in packages] == ["package_001"]
    assert packages[0].selected_task_ids == ["task_001"]
    assert [task.task_id for task in tasks] == ["task_001"]
    assert tasks[0].queue_item_id == "queue_001"
    assert tasks[0].source_library_entry_id == "entry_001"
    assert tasks[0].intended_source_material_id == "material_001"


def test_seeded_extraction_queue_includes_duan_ready_learning_package():
    packages = extraction_queue_intake.load_extraction_work_packages()
    tasks = extraction_queue_intake.load_extraction_tasks()
    slots = extraction_queue_intake.load_candidate_draft_slots()
    backlog_records = extraction_queue_intake.load_prerequisite_backlog_records()

    packages_by_id = {package.package_id: package for package in packages}
    tasks_by_id = {task.task_id: task for task in tasks}
    slots_by_id = {slot.draft_slot_id: slot for slot in slots}
    backlog_by_id = {record.backlog_id: record for record in backlog_records}

    assert "package_next_candidates_002" in packages_by_id
    assert packages_by_id["package_next_candidates_002"].selected_task_ids == [
        "task_duan_plain_mingxue_outline_extract_001"
    ]
    assert packages_by_id["package_next_candidates_003"].selected_task_ids == [
        "task_mingxue_golden_voice_extract_001",
        "task_fortune_reading_hongfu_qitian_extract_001",
    ]
    assert packages_by_id["package_next_candidates_003"].backlog_record_ids == [
        "backlog_markdown_batch_003_registration_001",
       "backlog_immortal_fortune_jianghu_secret_risk_review_001",
       "backlog_life_death_book_100_pages_risk_review_001",
       "backlog_source_processing_status_deferred_001",
    ]

    task = tasks_by_id["task_duan_plain_mingxue_outline_extract_001"]
    assert task.queue_item_id == "queue_duan_plain_mingxue_outline_extract"
    assert task.source_library_entry_id == "entry_duan_plain_mingxue_outline_pdf"
    assert task.intended_source_material_id == "material_duan_plain_mingxue_outline_pdf"
    assert task.risk_boundary == "ordinary"
    assert task.overlap_warnings == [
        "013 candidate overlap: candidate_duan_ten_god_relation_017_001 pending_review for material_duan_plain_mingxue_outline_pdf ten_god_relation."
    ]

    slot = slots_by_id["slot_duan_ten_god_relation_001"]
    assert slot.task_id == task.task_id
    assert slot.target_rule_family == "ten_god_relation"

    mingxue_task = tasks_by_id["task_mingxue_golden_voice_extract_001"]
    assert mingxue_task.queue_item_id == "queue_mingxue_golden_voice_extract"
    assert mingxue_task.source_library_entry_id == "entry_mingxue_golden_voice_pdf"
    assert mingxue_task.intended_source_material_id == "material_mingxue_golden_voice_pdf"
    assert mingxue_task.risk_boundary == "ordinary"
    assert mingxue_task.overlap_warnings == [
        "013 candidate overlap: candidate_mingxue_golden_voice_scope_001 rejected for material_mingxue_golden_voice_pdf pattern_strength.",
        "013 candidate overlap: candidate_mingxue_five_element_balance_017_001 pending_review for material_mingxue_golden_voice_pdf five_element_balance."
    ]

    hongfu_task = tasks_by_id["task_fortune_reading_hongfu_qitian_extract_001"]
    assert hongfu_task.queue_item_id == "queue_fortune_reading_hongfu_qitian_extract"
    assert hongfu_task.source_library_entry_id == (
        "entry_fortune_reading_hongfu_qitian_pdf"
    )
    assert hongfu_task.intended_source_material_id == (
        "material_fortune_reading_hongfu_qitian_pdf"
    )
    assert hongfu_task.risk_boundary == "sensitive"
    assert hongfu_task.overlap_warnings == [
        "013 candidate overlap: candidate_hongfu_remedy_boundary_017_001 pending_review for material_fortune_reading_hongfu_qitian_pdf remedy_boundary."
    ]

    assert slots_by_id["slot_mingxue_five_element_balance_001"].task_id == (
        mingxue_task.task_id
    )
    assert (
        slots_by_id["slot_mingxue_five_element_balance_001"].target_rule_family
        == "five_element_balance"
    )
    assert slots_by_id["slot_hongfu_remedy_boundary_001"].task_id == (
        hongfu_task.task_id
    )
    assert (
        slots_by_id["slot_hongfu_remedy_boundary_001"].target_rule_family
        == "remedy_boundary"
    )

    non_ready_queue_ids = {
            "queue_markdown_source_batch_003_register",
            "queue_immortal_fortune_jianghu_secret_risk_review",
            "queue_life_death_book_100_pages_risk_review",
            "queue_source_processing_status_deferred",
        }
    assert non_ready_queue_ids.isdisjoint({task.queue_item_id for task in tasks})
    assert {
        record.queue_item_id
        for record in backlog_by_id.values()
        if record.package_id == "package_next_candidates_003"
    } == non_ready_queue_ids
    assert extraction_queue_intake.validate_extraction_package_quality() == []


def test_bazi_general_source_preparation_reading_has_completed_extraction_package():
    packages = extraction_queue_intake.load_extraction_work_packages()
    tasks = extraction_queue_intake.load_extraction_tasks()
    slots = extraction_queue_intake.load_candidate_draft_slots()

    packages_by_id = {package.package_id: package for package in packages}
    tasks_by_id = {task.task_id: task for task in tasks}
    slots_by_id = {slot.draft_slot_id: slot for slot in slots}

    package = packages_by_id["package_bazi_general_source_preparation_reading_001"]
    expected_tasks = [
        "task_bazi_general_lecture_pattern_strength_001",
        "task_bazi_general_beichen_branch_interaction_001",
        "task_bazi_general_ziping_useful_god_001",
    ]
    assert package.status == "completed"
    assert package.source_queue_snapshot_ids == [
        "queue_bazi_general_lecture_textbook_extract",
        "queue_bazi_general_beichen_intro_extract",
        "queue_bazi_general_ziping_orthodox_pair_extract",
    ]
    assert package.selected_task_ids == expected_tasks
    assert package.backlog_record_ids == []

    for task_id in expected_tasks:
        task = tasks_by_id[task_id]
        assert task.package_id == package.package_id
        assert task.status == "completed"
        assert task.risk_boundary == "ordinary"
        assert task.locator_requirement == "page_or_section"
        assert task.overlap_warnings == []

    assert tasks_by_id["task_bazi_general_lecture_pattern_strength_001"].queue_item_id == (
        "queue_bazi_general_lecture_textbook_extract"
    )
    assert tasks_by_id[
        "task_bazi_general_beichen_branch_interaction_001"
    ].intended_source_material_id == "material_bazi_general_beichen_intro_pdf"
    assert tasks_by_id[
        "task_bazi_general_ziping_useful_god_001"
    ].source_library_entry_id == "entry_bazi_general_ziping_orthodox_pair_pdf"

    assert slots_by_id[
        "slot_bazi_general_lecture_pattern_strength_001"
    ].target_rule_family == "pattern_strength"
    assert slots_by_id[
        "slot_bazi_general_beichen_branch_interaction_001"
    ].target_rule_family == "branch_interaction"
    assert slots_by_id[
        "slot_bazi_general_ziping_useful_god_001"
    ].target_rule_family == "useful_god_candidate"


def test_seeded_extraction_queue_tracks_markdown_batch_005_completed_risk_review_backlog():
    packages = extraction_queue_intake.load_extraction_work_packages()
    tasks = extraction_queue_intake.load_extraction_tasks()
    backlog_records = extraction_queue_intake.load_prerequisite_backlog_records()
    summary = extraction_queue_intake.build_package_progress_summary()

    packages_by_id = {package.package_id: package for package in packages}
    backlog_by_id = {record.backlog_id: record for record in backlog_records}

    package = packages_by_id["package_next_candidates_004"]
    assert package.source_queue_snapshot_ids == [
        "queue_markdown_source_batch_005_risk_review"
    ]
    assert package.selected_task_ids == []
    assert package.backlog_record_ids == [
        "backlog_markdown_batch_005_risk_review_001"
    ]
    assert package.status == "completed"

    record = backlog_by_id["backlog_markdown_batch_005_risk_review_001"]
    assert record.package_id == package.package_id
    assert record.queue_item_id == "queue_markdown_source_batch_005_risk_review"
    assert record.audit_id == "audit_markdown_source_batch_005"
    assert record.backlog_type == "risk_review"
    assert record.missing_prerequisites == ["risk_boundary_review"]
    assert record.recommended_action == "risk_review"
    assert record.risk_boundary == "high_risk"
    assert record.status == "completed"

    assert record.backlog_id not in summary.next_manual_action_ids
    assert (
        "queue_markdown_source_batch_005_risk_review"
        in summary.selected_source_queue_ids
    )
    assert not any(
        task.queue_item_id == "queue_markdown_source_batch_005_risk_review"
        for task in tasks
    )


def test_seeded_risk_review_sweep_closes_backlog_records_without_tasks():
    packages = extraction_queue_intake.load_extraction_work_packages()
    tasks = extraction_queue_intake.load_extraction_tasks()
    backlog_records = extraction_queue_intake.load_prerequisite_backlog_records()
    summary = extraction_queue_intake.build_package_progress_summary()

    packages_by_id = {package.package_id: package for package in packages}
    backlog_by_id = {record.backlog_id: record for record in backlog_records}
    completed_backlog_ids = {
        "backlog_blind_life_manual_risk_review_001",
        "backlog_immortal_fortune_jianghu_secret_risk_review_001",
        "backlog_life_death_book_100_pages_risk_review_001",
        "backlog_markdown_batch_005_risk_review_001",
    }
    completed_queue_ids = {
        "queue_blind_life_manual_risk_review",
        "queue_immortal_fortune_jianghu_secret_risk_review",
        "queue_life_death_book_100_pages_risk_review",
        "queue_markdown_source_batch_005_risk_review",
    }

    assert packages_by_id["package_next_candidates_004"].status == "completed"
    assert {
        backlog_id
        for backlog_id in completed_backlog_ids
        if backlog_by_id[backlog_id].status == "completed"
    } == completed_backlog_ids
    assert completed_backlog_ids.isdisjoint(summary.next_manual_action_ids)
    assert summary.backlog_counts["risk_review"] == 4
    assert summary.backlog_counts["status:completed"] == 4
    assert not any(task.queue_item_id in completed_queue_ids for task in tasks)


@pytest.mark.parametrize(
    ("packages", "tasks", "expected"),
    [
        (
            [_minimal_work_package("package_001"), _minimal_work_package("package_001")],
            None,
            "duplicate package_id",
        ),
        (
            None,
            [_minimal_extraction_task("task_001"), _minimal_extraction_task("task_001")],
            "duplicate task_id",
        ),
        (
            [{**_minimal_work_package(), "status": "unknown"}],
            None,
            "invalid status",
        ),
        (
            None,
            [{**_minimal_extraction_task(), "status": "unknown"}],
            "invalid status",
        ),
        (
            None,
            [{**_minimal_extraction_task(), "priority_level": "deferred"}],
            "invalid priority_level",
        ),
        (
            None,
            [{**_minimal_extraction_task(), "risk_boundary": "unbounded"}],
            "invalid risk_boundary",
        ),
        (
            None,
            [{**_minimal_extraction_task(), "recommended_action": "auto_extract"}],
            "invalid recommended_action",
        ),
    ],
)
def test_invalid_package_or_task_metadata_fails_validation(
    tmp_path,
    packages,
    tasks,
    expected,
):
    data_dir = _write_us1_fixture(tmp_path, packages=packages, tasks=tasks)

    with pytest.raises(extraction_queue_intake.ExtractionQueueIntakeError, match=expected):
        if packages is not None:
            extraction_queue_intake.load_extraction_work_packages(data_dir)
        else:
            extraction_queue_intake.load_extraction_tasks(data_dir)


@pytest.mark.parametrize(
    ("tasks", "audit_records", "readiness", "alignments", "expected"),
    [
        (
            [{**_minimal_extraction_task(), "queue_item_id": "queue_missing"}],
            None,
            None,
            None,
            "unknown 015 queue item",
        ),
        (
            [{**_minimal_extraction_task(), "audit_id": "audit_missing"}],
            None,
            None,
            None,
            "audit mismatch",
        ),
        (
            None,
            [],
            None,
            None,
            "unknown audit",
        ),
        (
            None,
            None,
            [],
            None,
            "requires readiness finding",
        ),
        (
            None,
            None,
            None,
            [],
            "requires source-library alignment",
        ),
    ],
)
def test_extraction_tasks_require_current_015_audit_readiness_and_alignment(
    tmp_path,
    tasks,
    audit_records,
    readiness,
    alignments,
    expected,
):
    data_dir = _write_us1_fixture(
        tmp_path,
        tasks=tasks,
        audit_records=audit_records,
        readiness=readiness,
        alignments=alignments,
    )

    with pytest.raises(extraction_queue_intake.ExtractionQueueIntakeError, match=expected):
        extraction_queue_intake.load_extraction_tasks(data_dir)


def test_non_extraction_ready_queue_items_cannot_be_scheduled_as_tasks(tmp_path):
    queue_item = {
        **_minimal_queue_item(),
        "queue_type": "registration_backlog",
        "target_rule_families": [],
        "target_gap_ids": ["gap_source_registration"],
        "recommended_action": "register_source",
        "depends_on": ["source_library_registration"],
    }
    readiness = {
        **_minimal_readiness(),
        "readiness_state": "needs_source_registration",
        "missing_prerequisites": ["source_library_registration"],
        "ready_reasons": [],
        "blockers": ["Source-library registration is required before extraction."],
        "recommended_next_action": "register_source",
    }
    data_dir = _write_us1_fixture(
        tmp_path,
        queue_items=[queue_item],
        readiness=[readiness],
    )

    with pytest.raises(
        extraction_queue_intake.ExtractionQueueIntakeError,
        match="requires extraction_ready queue item",
    ):
        extraction_queue_intake.load_extraction_tasks(data_dir)


@pytest.mark.parametrize(
    ("task_update", "expected"),
    [
        ({"source_library_entry_id": ""}, "source_library_entry_id"),
        ({"target_rule_families": [], "target_gap_ids": []}, "requires target"),
        ({"locator_requirement": ""}, "locator_requirement"),
        ({"source_quality_note": ""}, "source_quality_note"),
        ({"rights_note": ""}, "rights_note"),
        ({"risk_boundary": ""}, "risk_boundary"),
        ({"pre_extraction_checks": []}, "pre_extraction_checks"),
    ],
)
def test_extraction_tasks_require_source_target_locator_quality_rights_and_checks(
    tmp_path,
    task_update,
    expected,
):
    task = {**_minimal_extraction_task(), **task_update}
    data_dir = _write_us1_fixture(tmp_path, tasks=[task])

    with pytest.raises(extraction_queue_intake.ExtractionQueueIntakeError, match=expected):
        extraction_queue_intake.load_extraction_tasks(data_dir)


def test_extraction_task_loading_does_not_mutate_upstream_data(tmp_path):
    data_dir = _write_us1_fixture(tmp_path)
    upstream_files = [
        tmp_path / "materials_audit" / "extraction_queue_items.json",
        tmp_path / "materials_audit" / "material_audit_records.json",
        tmp_path / "materials_audit" / "preparation_readiness_findings.json",
        tmp_path / "materials_audit" / "source_alignment_findings.json",
        tmp_path / "source_library" / "source_library_entries.json",
        tmp_path / "source_intake" / "source_materials.json",
    ]
    before = {path: path.read_text(encoding="utf-8") for path in upstream_files}

    extraction_queue_intake.load_extraction_tasks(data_dir)

    after = {path: path.read_text(encoding="utf-8") for path in upstream_files}
    assert after == before


def test_package_progress_summary_counts_us1_package_tasks_and_queue_ids(tmp_path):
    data_dir = _write_us1_fixture(tmp_path)

    summary = extraction_queue_intake.build_package_progress_summary(data_dir)

    assert summary.package_counts == {"planned": 1}
    assert summary.task_counts == {"planned": 1}
    assert summary.priority_counts == {"medium": 1}
    assert summary.risk_boundary_counts == {"ordinary": 1}
    assert summary.extraction_task_count == 1
    assert summary.selected_source_queue_ids == ["queue_001"]
    assert summary.next_manual_action_ids == ["task_001"]


def test_candidate_draft_slots_load_and_reference_existing_extraction_tasks(tmp_path):
    data_dir = _write_us1_fixture(
        tmp_path,
        draft_slots=[_minimal_candidate_draft_slot()],
    )

    slots = extraction_queue_intake.load_candidate_draft_slots(data_dir)

    assert [slot.draft_slot_id for slot in slots] == ["slot_001"]
    assert slots[0].task_id == "task_001"


def test_candidate_draft_slots_reject_unknown_extraction_task(tmp_path):
    data_dir = _write_us1_fixture(
        tmp_path,
        draft_slots=[_minimal_candidate_draft_slot(task_id="task_missing")],
    )

    with pytest.raises(
        extraction_queue_intake.ExtractionQueueIntakeError,
        match="unknown extraction task",
    ):
        extraction_queue_intake.load_candidate_draft_slots(data_dir)


@pytest.mark.parametrize(
    "forbidden_field",
    [
        "source_passage",
        "copied_source_passage",
        "extracted_meaning",
        "review_decision",
        "approval_status",
        "promotion_status",
        "formal_evidence_id",
    ],
)
def test_candidate_draft_slots_reject_candidate_or_evidence_state_fields(
    tmp_path,
    forbidden_field,
):
    slot = _minimal_candidate_draft_slot() | {forbidden_field: "not allowed"}
    data_dir = _write_us1_fixture(tmp_path, draft_slots=[slot])

    with pytest.raises(
        extraction_queue_intake.ExtractionQueueIntakeError,
        match="forbidden draft slot field",
    ):
        extraction_queue_intake.load_candidate_draft_slots(data_dir)


@pytest.mark.parametrize(
    ("slot_update", "expected"),
    [
        (
            {"expected_review_notes": ["This includes extracted meaning text."]},
            "extracted meaning",
        ),
        (
            {"expected_review_notes": ["Reviewer should set approval status."]},
            "review-state leakage",
        ),
        (
            {"safety_requirements": ["Promote as formal report evidence."]},
            "report evidence boundary",
        ),
    ],
)
def test_candidate_draft_slots_reject_leaked_candidate_or_evidence_wording(
    tmp_path,
    slot_update,
    expected,
):
    slot = _minimal_candidate_draft_slot() | slot_update
    data_dir = _write_us1_fixture(tmp_path, draft_slots=[slot])

    failures = extraction_queue_intake.validate_extraction_package_quality(data_dir)

    assert any(expected in failure for failure in failures)


@pytest.mark.parametrize(
    ("slot_update", "expected"),
    [
        ({"status": "ready_for_manual_extraction", "locator_requirement": ""}, "locator_requirement"),
        ({"status": "ready_for_manual_extraction", "expected_review_notes": []}, "expected_review_notes"),
        ({"status": "ready_for_manual_extraction", "safety_requirements": []}, "safety_requirements"),
    ],
)
def test_ready_candidate_draft_slots_require_locator_notes_and_safety(
    tmp_path,
    slot_update,
    expected,
):
    slot = _minimal_candidate_draft_slot() | slot_update
    data_dir = _write_us1_fixture(tmp_path, draft_slots=[slot])

    with pytest.raises(extraction_queue_intake.ExtractionQueueIntakeError, match=expected):
        extraction_queue_intake.load_candidate_draft_slots(data_dir)


def test_ready_candidate_draft_slots_require_parent_task_pre_extraction_checks(
    tmp_path,
):
    task = _minimal_extraction_task() | {"pre_extraction_checks": []}
    slot = _minimal_candidate_draft_slot() | {"status": "ready_for_manual_extraction"}
    data_dir = _write_us1_fixture(tmp_path, tasks=[task], draft_slots=[slot])

    with pytest.raises(
        extraction_queue_intake.ExtractionQueueIntakeError,
        match="pre_extraction_checks",
    ):
        extraction_queue_intake.load_candidate_draft_slots(data_dir)


@pytest.mark.parametrize(
    ("risk_boundary", "safety_requirements", "expected"),
    [
        ("sensitive", ["No absolute destiny language."], "uncertainty"),
        (
            "sensitive",
            ["State uncertainty.", "No absolute destiny language."],
            "limitation",
        ),
        (
            "high_risk",
            ["State uncertainty.", "Include limitation notes."],
            "risk-review",
        ),
    ],
)
def test_sensitive_and_high_risk_draft_slots_require_safety_boundaries(
    tmp_path,
    risk_boundary,
    safety_requirements,
    expected,
    ):
    task = _minimal_extraction_task() | {"risk_boundary": risk_boundary}
    slot = _minimal_candidate_draft_slot() | {
        "risk_boundary": risk_boundary,
        "safety_requirements": safety_requirements,
    }
    data_dir = _write_extraction_queue_intake_fixture(
        tmp_path,
        packages=[
            {
                **_minimal_work_package(),
                "source_queue_snapshot_ids": ["queue_001"],
                "selected_task_ids": ["task_001"],
            }
        ],
        tasks=[task],
        draft_slots=[slot],
    )

    with pytest.raises(extraction_queue_intake.ExtractionQueueIntakeError, match=expected):
        extraction_queue_intake.load_candidate_draft_slots(data_dir)


def test_package_progress_summary_counts_candidate_draft_slot_readiness(tmp_path):
    slot = _minimal_candidate_draft_slot() | {
        "status": "ready_for_manual_extraction",
        "safety_requirements": [
            "State uncertainty.",
            "Include limitation notes.",
        ],
    }
    data_dir = _write_us1_fixture(tmp_path, draft_slots=[slot])

    summary = extraction_queue_intake.build_package_progress_summary(data_dir)

    assert summary.candidate_draft_slot_count == 1
    assert summary.draft_slot_counts == {"ready_for_manual_extraction": 1}
    assert summary.draft_slot_rule_family_counts == {"blind_image_method": 1}
    assert summary.draft_slot_readiness_counts == {"ready": 1}


def test_prerequisite_backlog_records_load_with_package_queue_and_audit_links(
    tmp_path,
):
    package, record, queue_item, readiness = _backlog_fixture_parts()
    data_dir = _write_us1_fixture(
        tmp_path,
        packages=[package],
        tasks=[],
        backlog_records=[record],
        audit_records=[
            _minimal_audit_record("audit_002") | {"representations": ["repr_002"]}
        ],
        representations=[_minimal_representation("repr_002", "audit_002")],
        alignments=[],
        readiness=[readiness],
        queue_items=[queue_item],
    )

    records = extraction_queue_intake.load_prerequisite_backlog_records(data_dir)

    assert [item.backlog_id for item in records] == ["backlog_001"]
    assert records[0].package_id == "package_001"
    assert records[0].queue_item_id == "queue_002"
    assert records[0].audit_id == "audit_002"


@pytest.mark.parametrize(
    ("record_update", "package_update", "queue_items", "expected"),
    [
        ({"package_id": "package_missing"}, {}, None, "unknown package"),
        ({}, {"backlog_record_ids": []}, None, "not listed by package"),
        ({"queue_item_id": "queue_missing"}, {}, None, "unknown 015 queue item"),
        ({"audit_id": "audit_mismatch"}, {}, None, "audit mismatch"),
        ({}, {"source_queue_snapshot_ids": []}, None, "source queue snapshot"),
    ],
)
def test_prerequisite_backlog_records_reject_broken_package_queue_or_audit_links(
    tmp_path,
    record_update,
    package_update,
    queue_items,
    expected,
):
    package, record, queue_item, readiness = _backlog_fixture_parts()
    data_dir = _write_us1_fixture(
        tmp_path,
        packages=[package | package_update],
        tasks=[],
        backlog_records=[record | record_update],
        audit_records=[
            _minimal_audit_record("audit_002") | {"representations": ["repr_002"]}
        ],
        representations=[_minimal_representation("repr_002", "audit_002")],
        alignments=[],
        readiness=[readiness],
        queue_items=queue_items if queue_items is not None else [queue_item],
    )

    with pytest.raises(extraction_queue_intake.ExtractionQueueIntakeError, match=expected):
        extraction_queue_intake.load_prerequisite_backlog_records(data_dir)


@pytest.mark.parametrize(
    (
        "backlog_type",
        "queue_type",
        "readiness_state",
        "recommended_action",
        "risk_boundary",
        "status",
        "record_update",
        "expected",
    ),
    [
        (
            "registration",
            "registration_backlog",
            "needs_source_registration",
            "register_source",
            "ordinary",
            "planned",
            {"missing_prerequisites": []},
            "requires missing_prerequisites",
        ),
        (
            "preparation",
            "preparation_backlog",
            "preparation_backlog",
            "prepare_text",
            "ordinary",
            "planned",
            {"missing_prerequisites": []},
            "requires missing_prerequisites",
        ),
        (
            "locator_review",
            "preparation_backlog",
            "needs_locator_review",
            "clarify_identity",
            "sensitive",
            "planned",
            {"missing_prerequisites": []},
            "requires missing_prerequisites",
        ),
        (
            "risk_review",
            "risk_review_backlog",
            "needs_risk_review",
            "risk_review",
            "high_risk",
            "planned",
            {"missing_prerequisites": []},
            "requires missing_prerequisites",
        ),
        (
            "deferred",
            "blocked_backlog",
            "deferred",
            "defer",
            "ordinary",
            "deferred",
            {"durable_reason": "todo"},
            "durable_reason",
        ),
        (
            "blocked",
            "blocked_backlog",
            "blocked",
            "block",
            "sensitive",
            "blocked",
            {"durable_reason": "todo"},
            "durable_reason",
        ),
    ],
)
def test_backlog_records_require_type_specific_prerequisites_or_durable_reasons(
    tmp_path,
    backlog_type,
    queue_type,
    readiness_state,
    recommended_action,
    risk_boundary,
    status,
    record_update,
    expected,
):
    package, record, queue_item, readiness = _backlog_fixture_parts(
        backlog_type=backlog_type,
        queue_type=queue_type,
        readiness_state=readiness_state,
        recommended_action=recommended_action,
        missing_prerequisites=["risk_review"]
        if risk_boundary == "high_risk"
        else ["source_prerequisite"],
        risk_boundary=risk_boundary,
        status=status,
    )
    audit = _minimal_audit_record("audit_002") | {
        "representations": ["repr_002"],
        "risk_tier": risk_boundary,
        "risk_notes": ["Risk boundary review required."]
        if risk_boundary == "high_risk"
        else [],
    }
    data_dir = _write_us1_fixture(
        tmp_path,
        packages=[package],
        tasks=[],
        backlog_records=[record | record_update],
        audit_records=[audit],
        representations=[_minimal_representation("repr_002", "audit_002")],
        alignments=[],
        readiness=[readiness],
        queue_items=[queue_item],
    )

    with pytest.raises(extraction_queue_intake.ExtractionQueueIntakeError, match=expected):
        extraction_queue_intake.load_prerequisite_backlog_records(data_dir)


@pytest.mark.parametrize("backlog_type", ["risk_review", "deferred", "blocked"])
def test_restricted_backlog_records_cannot_also_be_routine_extraction_tasks(
    tmp_path,
    backlog_type,
):
    status = "planned" if backlog_type == "risk_review" else backlog_type
    recommended_action = {
        "risk_review": "risk_review",
        "deferred": "defer",
        "blocked": "block",
    }[backlog_type]
    record = _minimal_backlog_record() | {
        "queue_item_id": "queue_001",
        "audit_id": "audit_001",
        "backlog_type": backlog_type,
        "recommended_action": recommended_action,
        "missing_prerequisites": ["risk_review"],
        "status": status,
    }
    package = {
        **_minimal_work_package(),
        "source_queue_snapshot_ids": ["queue_001"],
        "selected_task_ids": ["task_001"],
        "backlog_record_ids": ["backlog_001"],
    }
    data_dir = _write_us1_fixture(
        tmp_path,
        packages=[package],
        backlog_records=[record],
    )

    with pytest.raises(
        extraction_queue_intake.ExtractionQueueIntakeError,
        match="cannot also be scheduled",
    ):
        extraction_queue_intake.load_prerequisite_backlog_records(data_dir)


def test_candidate_overlap_warnings_are_detected_for_existing_013_candidates(
    tmp_path,
):
    candidate_statuses = ["pending_review", "approved", "rejected", "blocked"]
    candidates = [
        _minimal_candidate_extract(
            f"candidate_overlap_{status}",
            status=status,
        )
        for status in candidate_statuses
    ]
    data_dir = _write_us1_fixture(tmp_path, candidate_extracts=candidates)

    summary = extraction_queue_intake.build_package_progress_summary(data_dir)

    assert summary.overlap_warning_count == len(candidate_statuses)


def test_package_progress_summary_counts_tasks_slots_backlog_risk_and_actions(
    tmp_path,
):
    package, record, queue_item, readiness = _backlog_fixture_parts()
    package = package | {
        "source_queue_snapshot_ids": ["queue_001", "queue_002"],
        "selected_task_ids": ["task_001"],
        "backlog_record_ids": ["backlog_001"],
    }
    slot = _minimal_candidate_draft_slot() | {
        "status": "ready_for_manual_extraction",
        "safety_requirements": [
            "State uncertainty.",
            "Include limitation notes.",
        ],
    }
    data_dir = _write_us1_fixture(
        tmp_path,
        packages=[package],
        draft_slots=[slot],
        backlog_records=[record],
        audit_records=[
            _minimal_audit_record("audit_001"),
            _minimal_audit_record("audit_002") | {"representations": ["repr_002"]},
        ],
        representations=[
            _minimal_representation("repr_001", "audit_001"),
            _minimal_representation("repr_002", "audit_002"),
        ],
        readiness=[_minimal_readiness(), readiness],
        queue_items=[_minimal_queue_item(), queue_item],
        candidate_extracts=[
            _minimal_candidate_extract("candidate_overlap_pending"),
        ],
    )

    summary = extraction_queue_intake.build_package_progress_summary(data_dir)

    assert summary.extraction_task_count == 1
    assert summary.candidate_draft_slot_count == 1
    assert summary.task_counts == {"planned": 1}
    assert summary.draft_slot_counts == {"ready_for_manual_extraction": 1}
    assert summary.backlog_counts["registration"] == 1
    assert summary.backlog_counts["status:planned"] == 1
    assert summary.risk_boundary_counts == {"ordinary": 3}
    assert summary.overlap_warning_count == 1
    assert summary.next_manual_action_ids == ["task_001", "backlog_001"]
