import json
import time
from pathlib import Path

import pytest

from mingli_engine import materials_audit
from mingli_engine import models


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _minimal_audit_record(audit_id: str = "audit_001") -> dict[str, object]:
    return {
        "audit_id": audit_id,
        "canonical_title": "Material One",
        "alternate_titles": [],
        "material_scope": "bazi",
        "primary_material_type": "pdf",
        "representations": ["repr_001"],
        "source_library_entry_id": "",
        "source_identity_confidence": "uncertain",
        "preparation_state": "raw_available",
        "source_boundary": "external_untracked",
        "topic_tags": [],
        "rule_families": [],
        "risk_tier": "ordinary",
        "risk_notes": [],
        "rights_notes": "Do not copy long passages.",
        "missing_prerequisites": ["source_library_registration"],
        "recommended_next_action": "register_source",
        "outcome_reason": "",
        "created_at": "2026-05-30",
        "updated_at": "2026-05-30",
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
        "text_quality": "not_text",
        "locator_quality": "file_only",
        "size_hint": "root PDF present",
        "modified_hint": "",
        "contains_images": True,
        "notes": "Raw PDF is external preparation material.",
    }


def _minimal_alignment(
    alignment_id: str = "align_001",
    audit_id: str = "audit_001",
) -> dict[str, object]:
    return {
        "alignment_id": alignment_id,
        "audit_id": audit_id,
        "match_type": "missing_source_library_entry",
        "source_library_entry_id": "",
        "source_material_id": "",
        "confidence": "moderate",
        "evidence": "No matching 014 source-library entry exists yet.",
        "registration_recommendation": "Create source-library entry before extraction.",
        "duplicate_or_variant_notes": "",
        "reviewer": "maintainer",
        "reviewed_at": "2026-05-30",
    }


def _minimal_source_library_entry(
    entry_id: str = "entry_001",
    material_id: str = "material_001",
) -> dict[str, object]:
    return {
        "entry_id": entry_id,
        "material_id": material_id,
        "title": "Material One",
        "material_type": "pdf",
        "local_reference": "material-one.pdf",
        "tracking_status": "external_untracked",
        "readiness_status": "ready_for_extraction",
        "topic_tags": ["blind-school"],
        "rule_families": ["blind_image_method"],
        "source_quality_notes": "Partially reviewed source metadata.",
        "rights_notes": "Do not copy long passages.",
        "risk_tier": "ordinary",
        "risk_notes": [],
        "priority_level": "medium",
        "next_action": "extract_candidates",
        "outcome_reason": "",
        "created_at": "2026-05-30",
        "updated_at": "2026-05-30",
    }


def _minimal_readiness(
    readiness_id: str = "ready_001",
    audit_id: str = "audit_001",
) -> dict[str, object]:
    return {
        "readiness_id": readiness_id,
        "audit_id": audit_id,
        "readiness_state": "needs_source_registration",
        "text_preparation_status": "raw_only",
        "locator_confidence": "weak",
        "source_quality": "moderate",
        "risk_boundary": "ordinary",
        "missing_prerequisites": ["source_library_registration"],
        "ready_reasons": [],
        "blockers": ["Missing source-library entry."],
        "recommended_next_action": "register_source",
        "assessed_by": "maintainer",
        "assessed_at": "2026-05-30",
    }


def _minimal_queue_item(
    queue_item_id: str = "queue_001",
    audit_id: str = "audit_001",
) -> dict[str, object]:
    return {
        "queue_item_id": queue_item_id,
        "audit_id": audit_id,
        "queue_type": "registration_backlog",
        "priority_level": "medium",
        "priority_rationale": "Material needs source-library registration first.",
        "target_rule_families": [],
        "target_gap_ids": [],
        "risk_boundary": "ordinary",
        "pre_extraction_checks": ["register source-library entry"],
        "recommended_action": "register_source",
        "depends_on": [],
        "status": "planned",
        "created_at": "2026-05-30",
        "updated_at": "2026-05-30",
    }


def _write_materials_audit_fixture(
    tmp_path: Path,
    *,
    records: list[dict[str, object]] | None = None,
    representations: list[dict[str, object]] | None = None,
    alignments: list[dict[str, object]] | None = None,
    readiness: list[dict[str, object]] | None = None,
    queue_items: list[dict[str, object]] | None = None,
) -> Path:
    data_dir = tmp_path / "materials_audit"
    data_dir.mkdir(exist_ok=True)
    _write_json(data_dir / "material_audit_records.json", records or [])
    _write_json(data_dir / "material_representations.json", representations or [])
    _write_json(data_dir / "source_alignment_findings.json", alignments or [])
    _write_json(data_dir / "preparation_readiness_findings.json", readiness or [])
    _write_json(data_dir / "extraction_queue_items.json", queue_items or [])
    return data_dir


def _write_source_library_fixture(
    tmp_path: Path,
    *,
    entries: list[dict[str, object]] | None = None,
) -> Path:
    data_dir = tmp_path / "source_library"
    data_dir.mkdir(exist_ok=True)
    _write_json(data_dir / "source_library_entries.json", entries or [])
    return data_dir


def test_materials_audit_constants_cover_contract_values():
    assert models.MATERIAL_AUDIT_SCOPES == frozenset(
        {"bazi", "ziwei", "qimen", "ritual_remedy", "mixed", "out_of_scope"}
    )
    assert models.MATERIAL_REPRESENTATION_TYPES == frozenset(
        {
            "root_pdf",
            "raw_markdown",
            "cleaned_markdown",
            "learning_note",
            "processing_status_note",
            "knowledge_skeleton",
            "image_asset",
            "raw_folder",
            "other",
        }
    )
    assert models.MATERIAL_AUDIT_SOURCE_BOUNDARIES == frozenset(
        {"external_untracked", "project_tracked_metadata", "derived_note_only"}
    )
    assert models.MATERIAL_AUDIT_IDENTITY_CONFIDENCES == frozenset(
        {"confirmed", "likely", "uncertain", "conflicting"}
    )
    assert models.MATERIAL_AUDIT_PREPARATION_STATES == frozenset(
        {
            "not_started",
            "raw_available",
            "prepared_text_available",
            "cleaned_text_available",
            "notes_available",
            "candidate_skeleton_available",
            "ready_for_extraction_review",
            "deferred",
            "blocked",
        }
    )
    assert models.MATERIAL_AUDIT_MATCH_TYPES == frozenset(
        {
            "exact",
            "likely",
            "possible_duplicate",
            "edition_variant",
            "missing_source_library_entry",
            "blocked_source_library_entry",
            "out_of_scope",
            "uncertain",
        }
    )
    assert models.MATERIAL_AUDIT_READINESS_STATES == frozenset(
        {
            "ready_for_extraction_review",
            "needs_cleaning",
            "needs_locator_review",
            "needs_source_registration",
            "needs_identity_clarification",
            "needs_rights_review",
            "needs_risk_review",
            "preparation_backlog",
            "deferred",
            "blocked",
        }
    )
    assert models.MATERIAL_AUDIT_QUEUE_TYPES == frozenset(
        {
            "extraction_ready",
            "preparation_backlog",
            "registration_backlog",
            "risk_review_backlog",
            "blocked_backlog",
        }
    )
    assert models.MATERIAL_AUDIT_ACTIONS == frozenset(
        {
            "register_source",
            "clarify_identity",
            "prepare_text",
            "review_cleaned_text",
            "risk_review",
            "extract_candidates",
            "defer",
            "block",
            "no_action",
        }
    )


def test_materials_audit_dataclasses_construct_with_defaults():
    record = models.MaterialAuditRecord(
        audit_id="audit_001",
        canonical_title="Material One",
        material_scope="bazi",
        primary_material_type="pdf",
        source_identity_confidence="uncertain",
        preparation_state="raw_available",
        source_boundary="external_untracked",
    )
    representation = models.MaterialRepresentation(
        representation_id="repr_001",
        audit_id=record.audit_id,
        representation_type="root_pdf",
        local_reference="material-one.pdf",
        tracking_status="external_untracked",
    )
    alignment = models.SourceAlignmentFinding(
        alignment_id="align_001",
        audit_id=record.audit_id,
        match_type="missing_source_library_entry",
        confidence="moderate",
        evidence="No source-library entry exists yet.",
    )
    readiness = models.PreparationReadinessFinding(
        readiness_id="ready_001",
        audit_id=record.audit_id,
        readiness_state="needs_source_registration",
        text_preparation_status="raw_only",
        locator_confidence="weak",
        source_quality="moderate",
        risk_boundary="ordinary",
    )
    queue_item = models.ExtractionQueueItem(
        queue_item_id="queue_001",
        audit_id=record.audit_id,
        queue_type="registration_backlog",
        priority_level="medium",
        priority_rationale="Register before extraction.",
        risk_boundary="ordinary",
        recommended_action="register_source",
    )
    summary = models.AuditProgressSummary(
        material_group_counts={"raw_available": 1},
        representation_counts={"root_pdf": 1},
        source_alignment_counts={"missing_source_library_entry": 1},
        readiness_counts={"needs_source_registration": 1},
        queue_counts={"registration_backlog": 1},
        risk_tier_counts={"ordinary": 1},
    )

    assert record.alternate_titles == []
    assert record.risk_tier == "ordinary"
    assert representation.text_quality == "unknown"
    assert alignment.registration_recommendation == ""
    assert readiness.missing_prerequisites == []
    assert queue_item.status == "planned"
    assert summary.next_action_ids == []

    external_refresh = models.ExternalMaterialInventoryRefreshSummary(
        refresh_id="015-external-material-inventory-refresh",
        refresh_status="scoped_metadata_registered",
        external_entry_counts={"root_pdf": 1},
        scanned_entry_count=1,
        tracked_external_entry_ids=["material-one.pdf"],
        untracked_material_entry_ids=[],
        excluded_work_artifact_ids=[],
        newly_registered_representation_ids=["repr_001"],
        new_queue_item_ids=[],
        downstream_mutation_authorized=False,
        next_material_entry="015-next-step",
        boundary_checks={"013_012_not_mutated": "passed"},
    )

    assert external_refresh.guardrails == []


def test_read_json_list_reports_missing_invalid_and_non_array_payloads(tmp_path):
    with pytest.raises(materials_audit.MaterialsAuditError, match="missing data file"):
        materials_audit._read_json_list(tmp_path / "missing.json")

    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{", encoding="utf-8")
    with pytest.raises(materials_audit.MaterialsAuditError, match="invalid JSON"):
        materials_audit._read_json_list(invalid_json)

    object_payload = tmp_path / "object.json"
    _write_json(object_payload, {"not": "a list"})
    with pytest.raises(materials_audit.MaterialsAuditError, match="JSON array"):
        materials_audit._read_json_list(object_payload)

    scalar_entries = tmp_path / "scalars.json"
    _write_json(scalar_entries, ["not an object"])
    with pytest.raises(
        materials_audit.MaterialsAuditError,
        match="entries must be JSON objects",
    ):
        materials_audit._read_json_list(scalar_entries)


def test_read_optional_json_list_returns_empty_for_missing_file(tmp_path):
    assert materials_audit._read_optional_json_list(tmp_path / "missing.json") == []


def test_ensure_unique_rejects_duplicate_ids():
    with pytest.raises(materials_audit.MaterialsAuditError, match="duplicate audit_id"):
        materials_audit._ensure_unique(["audit_001", "audit_001"], "audit_id")


def test_public_materials_audit_functions_exist():
    for function_name in (
        "load_material_audit_records",
        "load_material_representations",
        "load_source_alignment_findings",
        "load_preparation_readiness_findings",
        "load_extraction_queue_items",
        "build_materials_audit_progress_summary",
        "validate_materials_audit_quality",
        "build_external_material_inventory_refresh_summary",
        "render_external_material_inventory_refresh_markdown",
    ):
        assert callable(getattr(materials_audit, function_name))


def test_load_material_audit_records_and_representations_load_current_inventory():
    records = materials_audit.load_material_audit_records()
    representations = materials_audit.load_material_representations()
    records_by_id = {record.audit_id: record for record in records}
    representations_by_id = {
        representation.representation_id: representation
        for representation in representations
    }

    assert len(records) >= 16
    assert "audit_northeast_blind_peak" in records_by_id
    assert "audit_markdown_source_batch_001" in records_by_id
    assert "audit_source_processing_status" in records_by_id
    assert "audit_knowledge_skeleton" in records_by_id
    assert records_by_id["audit_northeast_blind_peak"].source_library_entry_id == (
        "entry_northeast_blind_peak_pdf"
    )
    assert records_by_id["audit_northeast_blind_peak"].source_boundary == (
        "external_untracked"
    )
    assert records_by_id["audit_markdown_source_batch_001"].preparation_state == (
        "ready_for_extraction_review"
    )
    assert "repr_northeast_blind_peak_root_pdf" in representations_by_id
    assert "repr_life_death_book_100_pages_markdown_extract" in representations_by_id
    assert "audit_raw_text_materials_folder" in records_by_id
    assert representations_by_id[
        "repr_northeast_blind_peak_root_pdf"
    ].tracking_status == "external_untracked"
    assert representations_by_id[
        "repr_life_death_book_100_pages_markdown_extract"
    ].local_reference == "Markdown/2800.《命理生死之书》100页.md"
    assert records_by_id["audit_life_death_book_100_pages"].representations == [
        "repr_life_death_book_100_pages_root_pdf",
        "repr_life_death_book_100_pages_markdown_extract",
    ]
    assert records_by_id["audit_raw_text_materials_folder"].recommended_next_action == (
        "risk_review"
    )
    assert representations_by_id[
        "repr_markdown_source_batch_001_cleaned"
    ].representation_type == "cleaned_markdown"


def test_material_audit_records_reject_duplicate_and_invalid_enums(tmp_path):
    duplicate = [_minimal_audit_record(), _minimal_audit_record()]
    _write_materials_audit_fixture(
        tmp_path,
        records=duplicate,
        representations=[_minimal_representation()],
    )

    with pytest.raises(materials_audit.MaterialsAuditError, match="duplicate audit_id"):
        materials_audit.load_material_audit_records(tmp_path / "materials_audit")

    invalid_cases = [
        ("material_scope", "unknown", "material_scope"),
        ("primary_material_type", "unknown", "primary_material_type"),
        ("source_identity_confidence", "sure", "source_identity_confidence"),
        ("preparation_state", "done", "preparation_state"),
        ("source_boundary", "local", "source_boundary"),
        ("risk_tier", "danger", "risk_tier"),
        ("recommended_next_action", "ship_it", "recommended_next_action"),
        ("rule_families", ["unknown_rule"], "rule_family"),
    ]
    for field_name, value, message in invalid_cases:
        record = _minimal_audit_record(f"audit_bad_{field_name}")
        representation = _minimal_representation(audit_id=record["audit_id"])
        record[field_name] = value
        _write_materials_audit_fixture(
            tmp_path,
            records=[record],
            representations=[representation],
        )

        with pytest.raises(materials_audit.MaterialsAuditError, match=message):
            materials_audit.load_material_audit_records(tmp_path / "materials_audit")


def test_material_representations_reject_duplicate_invalid_and_unknown_audit(
    tmp_path,
):
    record = _minimal_audit_record()
    duplicate_representations = [
        _minimal_representation(),
        _minimal_representation(),
    ]
    _write_materials_audit_fixture(
        tmp_path,
        records=[record],
        representations=duplicate_representations,
    )

    with pytest.raises(
        materials_audit.MaterialsAuditError,
        match="duplicate representation_id",
    ):
        materials_audit.load_material_representations(tmp_path / "materials_audit")

    invalid = _minimal_representation("repr_bad")
    invalid["representation_type"] = "scan"
    _write_materials_audit_fixture(
        tmp_path,
        records=[record],
        representations=[invalid],
    )
    with pytest.raises(materials_audit.MaterialsAuditError, match="representation_type"):
        materials_audit.load_material_representations(tmp_path / "materials_audit")

    unknown = _minimal_representation("repr_unknown", audit_id="audit_missing")
    _write_materials_audit_fixture(
        tmp_path,
        records=[record],
        representations=[unknown],
    )
    with pytest.raises(materials_audit.MaterialsAuditError, match="unknown audit"):
        materials_audit.load_material_representations(tmp_path / "materials_audit")


def test_audit_record_requires_representation_or_derived_note_boundary(tmp_path):
    record = _minimal_audit_record("audit_without_repr")
    record["representations"] = []
    _write_materials_audit_fixture(tmp_path, records=[record], representations=[])

    with pytest.raises(materials_audit.MaterialsAuditError, match="representation"):
        materials_audit.load_material_audit_records(tmp_path / "materials_audit")

    record["source_boundary"] = "derived_note_only"
    record["recommended_next_action"] = "no_action"
    _write_materials_audit_fixture(tmp_path, records=[record], representations=[])

    loaded = materials_audit.load_material_audit_records(tmp_path / "materials_audit")

    assert loaded[0].source_boundary == "derived_note_only"
    assert loaded[0].representations == []


def test_external_untracked_references_do_not_require_raw_file_access(tmp_path):
    missing_raw_file = tmp_path / "missing-user-source.pdf"
    record = _minimal_audit_record("audit_external_only")
    representation = _minimal_representation("repr_external_only", record["audit_id"])
    representation["local_reference"] = str(missing_raw_file)
    representation["tracking_status"] = "external_untracked"
    _write_materials_audit_fixture(
        tmp_path,
        records=[record],
        representations=[representation],
    )

    loaded_representations = materials_audit.load_material_representations(
        tmp_path / "materials_audit"
    )

    assert loaded_representations[0].local_reference.endswith("missing-user-source.pdf")
    assert not missing_raw_file.exists()


def test_ready_audit_records_require_reviewable_metadata(tmp_path):
    required_fields = (
        "topic_tags",
        "rule_families",
        "rights_notes",
        "source_identity_confidence",
        "source_library_entry_id",
    )
    for field_name in required_fields:
        record = _minimal_audit_record(f"audit_ready_missing_{field_name}")
        record.update(
            {
                "preparation_state": "ready_for_extraction_review",
                "topic_tags": ["blind-school"],
                "rule_families": ["blind_image_method"],
                "rights_notes": "Do not copy long passages.",
                "source_identity_confidence": "confirmed",
                "source_library_entry_id": "entry_001",
                "recommended_next_action": "extract_candidates",
            }
        )
        record[field_name] = (
            []
            if field_name in {"topic_tags", "rule_families"}
            else ""
        )
        representation = _minimal_representation(audit_id=record["audit_id"])
        _write_materials_audit_fixture(
            tmp_path,
            records=[record],
            representations=[representation],
        )

        with pytest.raises(materials_audit.MaterialsAuditError, match=field_name):
            materials_audit.load_material_audit_records(tmp_path / "materials_audit")


def test_terminal_conflicting_and_high_risk_records_require_reasons(tmp_path):
    high_risk = _minimal_audit_record("audit_high_risk")
    high_risk["risk_tier"] = "high_risk"
    _write_materials_audit_fixture(
        tmp_path,
        records=[high_risk],
        representations=[_minimal_representation(audit_id="audit_high_risk")],
    )
    with pytest.raises(materials_audit.MaterialsAuditError, match="risk_notes"):
        materials_audit.load_material_audit_records(tmp_path / "materials_audit")

    conflicting = _minimal_audit_record("audit_conflicting")
    conflicting["source_identity_confidence"] = "conflicting"
    conflicting["missing_prerequisites"] = []
    _write_materials_audit_fixture(
        tmp_path,
        records=[conflicting],
        representations=[_minimal_representation(audit_id="audit_conflicting")],
    )
    with pytest.raises(materials_audit.MaterialsAuditError, match="conflicting"):
        materials_audit.load_material_audit_records(tmp_path / "materials_audit")

    for state in ("deferred", "blocked"):
        terminal = _minimal_audit_record(f"audit_{state}")
        terminal["preparation_state"] = state
        terminal["recommended_next_action"] = "defer" if state == "deferred" else "block"
        terminal["outcome_reason"] = "n/a"
        _write_materials_audit_fixture(
            tmp_path,
            records=[terminal],
            representations=[_minimal_representation(audit_id=terminal["audit_id"])],
        )

        with pytest.raises(materials_audit.MaterialsAuditError, match="outcome_reason"):
            materials_audit.load_material_audit_records(tmp_path / "materials_audit")


def test_build_materials_audit_progress_summary_counts_inventory(tmp_path):
    ready = _minimal_audit_record("audit_ready")
    ready.update(
        {
            "preparation_state": "ready_for_extraction_review",
            "source_identity_confidence": "confirmed",
            "source_library_entry_id": "entry_ready",
            "topic_tags": ["blind-school"],
            "rule_families": ["blind_image_method"],
            "risk_tier": "sensitive",
            "risk_notes": ["Image-method wording needs conditional review."],
            "recommended_next_action": "extract_candidates",
        }
    )
    blocked = _minimal_audit_record("audit_blocked")
    blocked.update(
        {
            "preparation_state": "blocked",
            "recommended_next_action": "block",
            "outcome_reason": "Blocked until source identity and rights are clarified.",
        }
    )
    ready["representations"] = ["repr_ready"]
    blocked["representations"] = ["repr_blocked"]
    ready_alignment = _minimal_alignment("align_ready", "audit_ready")
    ready_alignment.update(
        {
            "match_type": "exact",
            "source_library_entry_id": "entry_ready",
            "source_material_id": "material_ready",
            "registration_recommendation": "none",
        }
    )
    blocked_alignment = _minimal_alignment("align_blocked", "audit_blocked")
    _write_materials_audit_fixture(
        tmp_path,
        records=[ready, blocked],
        representations=[
            _minimal_representation("repr_ready", "audit_ready"),
            _minimal_representation("repr_blocked", "audit_blocked"),
        ],
        alignments=[ready_alignment, blocked_alignment],
    )
    _write_source_library_fixture(
        tmp_path,
        entries=[_minimal_source_library_entry("entry_ready", "material_ready")],
    )

    summary = materials_audit.build_materials_audit_progress_summary(
        tmp_path / "materials_audit"
    )

    assert summary.material_group_counts == {
        "ready_for_extraction_review": 1,
        "blocked": 1,
    }
    assert summary.representation_counts == {"root_pdf": 2}
    assert summary.source_alignment_counts == {
        "exact": 1,
        "missing_source_library_entry": 1,
    }
    assert summary.risk_tier_counts == {"sensitive": 1, "ordinary": 1}


def test_build_materials_audit_progress_summary_stays_under_plan_budget():
    materials_audit.build_materials_audit_progress_summary()

    start = time.perf_counter()
    materials_audit.build_materials_audit_progress_summary()
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 300.0


def test_source_alignment_findings_load_and_reference_audit_records():
    alignments = materials_audit.load_source_alignment_findings()
    audit_ids = {
        record.audit_id for record in materials_audit.load_material_audit_records()
    }
    alignments_by_id = {alignment.alignment_id: alignment for alignment in alignments}

    assert len(alignments) >= 12
    assert "align_northeast_blind_peak_exact" in alignments_by_id
    assert alignments_by_id["align_northeast_blind_peak_exact"].audit_id in audit_ids
    assert all(alignment.audit_id in audit_ids for alignment in alignments)


def test_source_alignment_findings_reject_unknown_audit_records(tmp_path):
    _write_materials_audit_fixture(
        tmp_path,
        records=[_minimal_audit_record()],
        representations=[_minimal_representation()],
        alignments=[_minimal_alignment(audit_id="audit_missing")],
    )
    _write_source_library_fixture(tmp_path, entries=[_minimal_source_library_entry()])

    with pytest.raises(materials_audit.MaterialsAuditError, match="unknown audit"):
        materials_audit.load_source_alignment_findings(tmp_path / "materials_audit")


def test_exact_and_likely_alignment_findings_require_existing_source_library_entries(
    tmp_path,
):
    record = _minimal_audit_record()
    _write_source_library_fixture(tmp_path, entries=[_minimal_source_library_entry()])

    for match_type in ("exact", "likely"):
        alignment = _minimal_alignment(f"align_{match_type}")
        alignment.update(
            {
                "match_type": match_type,
                "source_library_entry_id": "",
                "source_material_id": "material_001",
                "registration_recommendation": "",
            }
        )
        _write_materials_audit_fixture(
            tmp_path,
            records=[record],
            representations=[_minimal_representation()],
            alignments=[alignment],
        )

        with pytest.raises(
            materials_audit.MaterialsAuditError,
            match="source_library_entry_id",
        ):
            materials_audit.load_source_alignment_findings(
                tmp_path / "materials_audit"
            )

    unknown = _minimal_alignment("align_unknown")
    unknown.update(
        {
            "match_type": "exact",
            "source_library_entry_id": "entry_missing",
            "source_material_id": "material_missing",
            "registration_recommendation": "",
        }
    )
    _write_materials_audit_fixture(
        tmp_path,
        records=[record],
        representations=[_minimal_representation()],
        alignments=[unknown],
    )

    with pytest.raises(materials_audit.MaterialsAuditError, match="source-library"):
        materials_audit.load_source_alignment_findings(tmp_path / "materials_audit")


def test_missing_source_library_alignment_requires_registration_recommendation(
    tmp_path,
):
    missing = _minimal_alignment("align_missing")
    missing["registration_recommendation"] = ""
    _write_materials_audit_fixture(
        tmp_path,
        records=[_minimal_audit_record()],
        representations=[_minimal_representation()],
        alignments=[missing],
    )
    _write_source_library_fixture(tmp_path, entries=[_minimal_source_library_entry()])

    with pytest.raises(
        materials_audit.MaterialsAuditError,
        match="registration_recommendation",
    ):
        materials_audit.load_source_alignment_findings(tmp_path / "materials_audit")


def test_special_source_alignment_findings_require_explanatory_notes(tmp_path):
    _write_source_library_fixture(tmp_path, entries=[_minimal_source_library_entry()])
    explanatory_cases = [
        ("possible_duplicate", "duplicate_or_variant_notes"),
        ("edition_variant", "duplicate_or_variant_notes"),
        ("uncertain", "evidence"),
        ("blocked_source_library_entry", "evidence"),
        ("out_of_scope", "evidence"),
    ]

    for match_type, required_field in explanatory_cases:
        alignment = _minimal_alignment(f"align_{match_type}")
        alignment.update(
            {
                "match_type": match_type,
                "source_library_entry_id": "",
                "source_material_id": "",
                "registration_recommendation": "",
                "duplicate_or_variant_notes": "",
                "evidence": "n/a",
            }
        )
        _write_materials_audit_fixture(
            tmp_path,
            records=[_minimal_audit_record()],
            representations=[_minimal_representation()],
            alignments=[alignment],
        )

        with pytest.raises(
            materials_audit.MaterialsAuditError,
            match=required_field,
        ):
            materials_audit.load_source_alignment_findings(
                tmp_path / "materials_audit"
            )


def test_source_alignment_loading_does_not_mutate_source_library_records():
    source_library_path = (
        Path("src")
        / "mingli_engine"
        / "data"
        / "source_library"
        / "source_library_entries.json"
    )
    before = source_library_path.read_text(encoding="utf-8")

    materials_audit.load_source_alignment_findings()

    assert source_library_path.read_text(encoding="utf-8") == before


def test_preparation_readiness_findings_load_and_reference_audit_records():
    findings = materials_audit.load_preparation_readiness_findings()
    audit_ids = {
        record.audit_id for record in materials_audit.load_material_audit_records()
    }
    findings_by_id = {finding.readiness_id: finding for finding in findings}

    assert len(findings) >= 12
    assert "ready_northeast_blind_peak" in findings_by_id
    assert findings_by_id["ready_northeast_blind_peak"].audit_id in audit_ids
    assert all(finding.audit_id in audit_ids for finding in findings)


def test_preparation_readiness_findings_reject_unknown_audit_records(tmp_path):
    _write_materials_audit_fixture(
        tmp_path,
        records=[_minimal_audit_record()],
        representations=[_minimal_representation()],
        readiness=[_minimal_readiness(audit_id="audit_missing")],
    )

    with pytest.raises(materials_audit.MaterialsAuditError, match="unknown audit"):
        materials_audit.load_preparation_readiness_findings(
            tmp_path / "materials_audit"
        )


def test_extraction_ready_readiness_requires_preconditions_from_audit_records(
    tmp_path,
):
    record = _minimal_audit_record("audit_ready")
    record.update(
        {
            "preparation_state": "ready_for_extraction_review",
            "source_identity_confidence": "confirmed",
            "source_library_entry_id": "entry_ready",
            "topic_tags": ["blind-school"],
            "rule_families": ["blind_image_method"],
            "recommended_next_action": "extract_candidates",
        }
    )
    record["representations"] = ["repr_ready"]
    ready = _minimal_readiness("ready_001", "audit_ready")
    ready.update(
        {
            "readiness_state": "ready_for_extraction_review",
            "text_preparation_status": "cleaned",
            "locator_confidence": "strong",
            "source_quality": "strong",
            "risk_boundary": "ordinary",
            "missing_prerequisites": [],
            "ready_reasons": [
                "Audit record has source-library alignment, clean text, and locator anchors."
            ],
            "blockers": [],
            "recommended_next_action": "extract_candidates",
        }
    )
    _write_materials_audit_fixture(
        tmp_path,
        records=[record],
        representations=[_minimal_representation("repr_ready", "audit_ready")],
        readiness=[ready],
    )

    loaded = materials_audit.load_preparation_readiness_findings(
        tmp_path / "materials_audit"
    )

    assert loaded[0].readiness_state == "ready_for_extraction_review"

    invalid_cases = [
        ("ready_reasons", [], "ready_reasons"),
        ("blockers", ["Needs locator review."], "blockers"),
        ("locator_confidence", "weak", "locator_confidence"),
        ("source_quality", "needs_recheck", "source_quality"),
    ]
    for field_name, value, message in invalid_cases:
        invalid = ready | {field_name: value}
        _write_materials_audit_fixture(
            tmp_path,
            records=[record],
            representations=[_minimal_representation("repr_ready", "audit_ready")],
            readiness=[invalid],
        )

        with pytest.raises(materials_audit.MaterialsAuditError, match=message):
            materials_audit.load_preparation_readiness_findings(
                tmp_path / "materials_audit"
            )

    not_ready_record = record | {
        "preparation_state": "cleaned_text_available",
        "source_library_entry_id": "",
        "recommended_next_action": "register_source",
    }
    _write_materials_audit_fixture(
        tmp_path,
        records=[not_ready_record],
        representations=[_minimal_representation("repr_ready", "audit_ready")],
        readiness=[ready],
    )

    with pytest.raises(materials_audit.MaterialsAuditError, match="audit record"):
        materials_audit.load_preparation_readiness_findings(
            tmp_path / "materials_audit"
        )


def test_not_ready_readiness_states_require_missing_prerequisites_or_blockers(
    tmp_path,
):
    not_ready_states = (
        "needs_cleaning",
        "needs_locator_review",
        "needs_source_registration",
        "needs_identity_clarification",
        "needs_rights_review",
        "needs_risk_review",
        "preparation_backlog",
        "deferred",
        "blocked",
    )
    for state in not_ready_states:
        finding = _minimal_readiness(f"ready_{state}")
        finding.update(
            {
                "readiness_state": state,
                "missing_prerequisites": [],
                "blockers": [],
            }
        )
        _write_materials_audit_fixture(
            tmp_path,
            records=[_minimal_audit_record()],
            representations=[_minimal_representation()],
            readiness=[finding],
        )

        with pytest.raises(materials_audit.MaterialsAuditError, match="prerequisites"):
            materials_audit.load_preparation_readiness_findings(
                tmp_path / "materials_audit"
            )


def test_high_risk_readiness_requires_risk_review_and_non_routine_action(tmp_path):
    high_risk = _minimal_audit_record("audit_high_risk_ready")
    high_risk.update(
        {
            "risk_tier": "high_risk",
            "risk_notes": ["Life-risk material requires bounded review."],
            "missing_prerequisites": ["risk_review"],
            "recommended_next_action": "risk_review",
        }
    )
    high_risk["representations"] = ["repr_high_risk"]
    finding = _minimal_readiness("ready_high_risk", "audit_high_risk_ready")
    finding.update(
        {
            "readiness_state": "needs_risk_review",
            "risk_boundary": "high_risk",
            "missing_prerequisites": ["risk_review"],
            "blockers": ["Needs high-risk boundary review before extraction."],
            "recommended_next_action": "risk_review",
        }
    )
    _write_materials_audit_fixture(
        tmp_path,
        records=[high_risk],
        representations=[_minimal_representation("repr_high_risk", high_risk["audit_id"])],
        readiness=[finding],
    )

    loaded = materials_audit.load_preparation_readiness_findings(
        tmp_path / "materials_audit"
    )

    assert loaded[0].recommended_next_action == "risk_review"

    routine = finding | {
        "missing_prerequisites": ["cleaned_text"],
        "blockers": ["Needs ordinary text cleanup."],
        "recommended_next_action": "extract_candidates",
    }
    _write_materials_audit_fixture(
        tmp_path,
        records=[high_risk],
        representations=[_minimal_representation("repr_high_risk", high_risk["audit_id"])],
        readiness=[routine],
    )

    with pytest.raises(materials_audit.MaterialsAuditError, match="high_risk"):
        materials_audit.load_preparation_readiness_findings(
            tmp_path / "materials_audit"
        )


def test_materials_audit_progress_summary_counts_readiness_dimensions(tmp_path):
    ready_record = _minimal_audit_record("audit_ready_summary")
    ready_record.update(
        {
            "preparation_state": "ready_for_extraction_review",
            "source_identity_confidence": "confirmed",
            "source_library_entry_id": "entry_ready",
            "topic_tags": ["blind-school"],
            "rule_families": ["blind_image_method"],
            "recommended_next_action": "extract_candidates",
        }
    )
    ready_record["representations"] = ["repr_ready_summary"]
    ready = _minimal_readiness("ready_summary", "audit_ready_summary")
    ready.update(
        {
            "readiness_state": "ready_for_extraction_review",
            "text_preparation_status": "cleaned",
            "locator_confidence": "strong",
            "source_quality": "strong",
            "risk_boundary": "ordinary",
            "missing_prerequisites": [],
            "ready_reasons": ["Clean text and source-library alignment are present."],
            "blockers": [],
            "recommended_next_action": "extract_candidates",
        }
    )
    backlog = _minimal_readiness("ready_backlog", "audit_001")
    backlog.update(
        {
            "readiness_state": "preparation_backlog",
            "text_preparation_status": "raw_only",
            "locator_confidence": "weak",
            "source_quality": "moderate",
            "missing_prerequisites": ["cleaned_text"],
            "blockers": ["Cleaned text is not available yet."],
        }
    )
    _write_materials_audit_fixture(
        tmp_path,
        records=[ready_record, _minimal_audit_record()],
        representations=[
            _minimal_representation("repr_ready_summary", "audit_ready_summary"),
            _minimal_representation(),
        ],
        readiness=[ready, backlog],
    )
    _write_source_library_fixture(
        tmp_path,
        entries=[_minimal_source_library_entry("entry_ready", "material_ready")],
    )

    summary = materials_audit.build_materials_audit_progress_summary(
        tmp_path / "materials_audit"
    )

    assert summary.readiness_counts == {
        "ready_for_extraction_review": 1,
        "preparation_backlog": 1,
    }
    assert summary.text_preparation_counts == {"cleaned": 1, "raw_only": 1}
    assert summary.locator_confidence_counts == {"strong": 1, "weak": 1}
    assert summary.source_quality_counts == {"strong": 1, "moderate": 1}
    assert summary.risk_boundary_counts == {"ordinary": 2}
    assert summary.missing_prerequisite_counts == {"cleaned_text": 1}


def test_extraction_queue_items_load_and_reference_audit_records():
    queue_items = materials_audit.load_extraction_queue_items()
    audit_ids = {
        record.audit_id for record in materials_audit.load_material_audit_records()
    }
    queue_items_by_id = {item.queue_item_id: item for item in queue_items}

    assert len(queue_items) >= 6
    assert "queue_northeast_blind_peak_extract" in queue_items_by_id
    assert all(item.audit_id in audit_ids for item in queue_items)


def test_knowledge_skeleton_enters_preparation_backlog_queue():
    queue_items = materials_audit.load_extraction_queue_items()
    queue_items_by_id = {item.queue_item_id: item for item in queue_items}

    item = queue_items_by_id["queue_knowledge_skeleton_prepare"]
    assert item.audit_id == "audit_knowledge_skeleton"
    assert item.queue_type == "extraction_ready"
    assert item.recommended_action == "extract_candidates"
    assert set(item.depends_on) == {"component_source_links", "candidate_review"}


def test_extraction_queue_items_reject_unknown_audit_records(tmp_path):
    _write_materials_audit_fixture(
        tmp_path,
        records=[_minimal_audit_record()],
        representations=[_minimal_representation()],
        queue_items=[_minimal_queue_item(audit_id="audit_missing")],
    )

    with pytest.raises(materials_audit.MaterialsAuditError, match="unknown audit"):
        materials_audit.load_extraction_queue_items(tmp_path / "materials_audit")


def test_extraction_ready_queue_items_require_alignment_readiness_and_checks(
    tmp_path,
):
    record = _minimal_audit_record("audit_ready_queue")
    record.update(
        {
            "preparation_state": "ready_for_extraction_review",
            "source_identity_confidence": "confirmed",
            "source_library_entry_id": "entry_ready_queue",
            "topic_tags": ["blind-school"],
            "rule_families": ["blind_image_method"],
            "recommended_next_action": "extract_candidates",
        }
    )
    record["representations"] = ["repr_ready_queue"]
    alignment = _minimal_alignment("align_ready_queue", "audit_ready_queue")
    alignment.update(
        {
            "match_type": "exact",
            "source_library_entry_id": "entry_ready_queue",
            "source_material_id": "material_ready_queue",
            "registration_recommendation": "none",
        }
    )
    readiness = _minimal_readiness("ready_queue", "audit_ready_queue")
    readiness.update(
        {
            "readiness_state": "ready_for_extraction_review",
            "text_preparation_status": "cleaned",
            "locator_confidence": "strong",
            "source_quality": "strong",
            "missing_prerequisites": [],
            "ready_reasons": [
                "Source-library alignment and locator-ready text are present."
            ],
            "blockers": [],
            "recommended_next_action": "extract_candidates",
        }
    )
    queue_item = _minimal_queue_item("queue_ready", "audit_ready_queue")
    queue_item.update(
        {
            "queue_type": "extraction_ready",
            "priority_level": "high",
            "priority_rationale": (
                "Ready source with strong locator confidence and reviewed "
                "source-library alignment."
            ),
            "target_rule_families": ["blind_image_method"],
            "risk_boundary": "ordinary",
            "pre_extraction_checks": [
                "confirm source-library alignment",
                "keep concise paraphrases",
            ],
            "recommended_action": "extract_candidates",
        }
    )
    _write_source_library_fixture(
        tmp_path,
        entries=[_minimal_source_library_entry("entry_ready_queue", "material_ready_queue")],
    )

    def write_queue_case(*, alignments=None, readiness_items=None, item=None):
        _write_materials_audit_fixture(
            tmp_path,
            records=[record],
            representations=[_minimal_representation("repr_ready_queue", record["audit_id"])],
            alignments=alignments if alignments is not None else [alignment],
            readiness=readiness_items if readiness_items is not None else [readiness],
            queue_items=[item or queue_item],
        )

    write_queue_case()
    loaded = materials_audit.load_extraction_queue_items(tmp_path / "materials_audit")
    assert loaded[0].queue_type == "extraction_ready"

    invalid_cases = [
        (queue_item | {"target_rule_families": [], "target_gap_ids": []}, "target"),
        (queue_item | {"pre_extraction_checks": []}, "pre_extraction_checks"),
    ]
    for invalid, message in invalid_cases:
        write_queue_case(item=invalid)
        with pytest.raises(materials_audit.MaterialsAuditError, match=message):
            materials_audit.load_extraction_queue_items(tmp_path / "materials_audit")

    write_queue_case(alignments=[])
    with pytest.raises(materials_audit.MaterialsAuditError, match="alignment"):
        materials_audit.load_extraction_queue_items(tmp_path / "materials_audit")

    write_queue_case(readiness_items=[])
    with pytest.raises(materials_audit.MaterialsAuditError, match="readiness"):
        materials_audit.load_extraction_queue_items(tmp_path / "materials_audit")


def test_high_risk_queue_items_require_risk_review_prerequisites(tmp_path):
    record = _minimal_audit_record("audit_high_risk_queue")
    record.update(
        {
            "risk_tier": "high_risk",
            "risk_notes": ["Needs bounded high-risk handling."],
            "missing_prerequisites": ["risk_review"],
            "recommended_next_action": "risk_review",
        }
    )
    record["representations"] = ["repr_high_risk_queue"]
    readiness = _minimal_readiness("ready_high_risk_queue", record["audit_id"])
    readiness.update(
        {
            "readiness_state": "needs_risk_review",
            "risk_boundary": "high_risk",
            "missing_prerequisites": ["risk_review"],
            "blockers": ["Needs high-risk boundary review before extraction."],
            "recommended_next_action": "risk_review",
        }
    )
    queue_item = _minimal_queue_item("queue_high_risk", record["audit_id"])
    queue_item.update(
        {
            "queue_type": "risk_review_backlog",
            "priority_level": "high",
            "priority_rationale": (
                "High-risk boundary review is required before extraction."
            ),
            "risk_boundary": "high_risk",
            "pre_extraction_checks": [
                "complete risk boundary review",
                "reject exact outcome wording",
            ],
            "recommended_action": "risk_review",
        }
    )
    _write_materials_audit_fixture(
        tmp_path,
        records=[record],
        representations=[_minimal_representation("repr_high_risk_queue", record["audit_id"])],
        readiness=[readiness],
        queue_items=[queue_item],
    )

    loaded = materials_audit.load_extraction_queue_items(tmp_path / "materials_audit")
    assert loaded[0].queue_type == "risk_review_backlog"

    routine = queue_item | {
        "queue_type": "extraction_ready",
        "recommended_action": "extract_candidates",
    }
    _write_materials_audit_fixture(
        tmp_path,
        records=[record],
        representations=[_minimal_representation("repr_high_risk_queue", record["audit_id"])],
        readiness=[readiness],
        queue_items=[routine],
    )
    with pytest.raises(materials_audit.MaterialsAuditError, match="high_risk"):
        materials_audit.load_extraction_queue_items(tmp_path / "materials_audit")

    weak_rationale = queue_item | {"priority_rationale": "n/a"}
    _write_materials_audit_fixture(
        tmp_path,
        records=[record],
        representations=[_minimal_representation("repr_high_risk_queue", record["audit_id"])],
        readiness=[readiness],
        queue_items=[weak_rationale],
    )
    with pytest.raises(materials_audit.MaterialsAuditError, match="priority_rationale"):
        materials_audit.load_extraction_queue_items(tmp_path / "materials_audit")


def test_backlog_queue_items_require_prerequisites_or_reasons(tmp_path):
    backlog_types = (
        "preparation_backlog",
        "registration_backlog",
        "risk_review_backlog",
        "blocked_backlog",
    )
    for queue_type in backlog_types:
        record = _minimal_audit_record(f"audit_{queue_type}")
        record["representations"] = [f"repr_{queue_type}"]
        readiness = _minimal_readiness(f"ready_{queue_type}", record["audit_id"])
        readiness.update(
            {
                "readiness_state": "preparation_backlog",
                "missing_prerequisites": [],
                "blockers": [],
            }
        )
        queue_item = _minimal_queue_item(f"queue_{queue_type}", record["audit_id"])
        queue_item.update(
            {
                "queue_type": queue_type,
                "priority_rationale": "n/a",
                "pre_extraction_checks": [],
            }
        )
        _write_materials_audit_fixture(
            tmp_path,
            records=[record],
            representations=[_minimal_representation(f"repr_{queue_type}", record["audit_id"])],
            readiness=[readiness],
            queue_items=[queue_item],
        )

        with pytest.raises(materials_audit.MaterialsAuditError, match="prerequisites"):
            materials_audit.load_extraction_queue_items(
                tmp_path / "materials_audit"
            )


def test_audit_progress_summary_includes_next_five_queue_items_and_backlog_counts():
    summary = materials_audit.build_materials_audit_progress_summary()

    assert summary.next_action_ids == [
        "queue_northeast_blind_peak_extract",
        "queue_mingli_true_formula_teacher_extract",
        "queue_raw_text_materials_folder_triage",
        "queue_markdown_source_batch_003_register",
        "queue_markdown_source_batch_004_prepare",
    ]
    assert summary.extraction_ready_count == 9
    assert summary.preparation_backlog_count == 0
    assert summary.registration_backlog_count == 0
    assert summary.risk_review_backlog_count == 5
    assert summary.deferred_queue_count == 2
    assert summary.blocked_queue_count == 1


def test_seeded_risk_review_sweep_marks_high_risk_queue_items_completed():
    queue_items = materials_audit.load_extraction_queue_items()
    summary = materials_audit.build_materials_audit_progress_summary()

    queue_items_by_id = {item.queue_item_id: item for item in queue_items}
    completed_risk_review_queue_ids = {
        "queue_blind_life_manual_risk_review",
        "queue_immortal_fortune_jianghu_secret_risk_review",
        "queue_life_death_book_100_pages_risk_review",
        "queue_markdown_source_batch_005_risk_review",
    }

    assert {
        queue_id
        for queue_id in completed_risk_review_queue_ids
        if queue_items_by_id[queue_id].status == "completed"
    } == completed_risk_review_queue_ids
    assert completed_risk_review_queue_ids.isdisjoint(summary.next_action_ids)
    assert summary.next_action_ids == [
        "queue_northeast_blind_peak_extract",
        "queue_mingli_true_formula_teacher_extract",
        "queue_raw_text_materials_folder_triage",
        "queue_markdown_source_batch_003_register",
        "queue_markdown_source_batch_004_prepare",
    ]


def test_materials_audit_queue_refresh_excludes_covered_016_queue_items():
    summary = materials_audit.build_materials_audit_progress_summary()
    refresh = materials_audit.build_materials_audit_queue_refresh_summary()

    assert refresh.refresh_id == "015-materials-audit-next-action-queue-refresh"
    assert refresh.refresh_status == "uncovered_queue_items_available"
    assert refresh.queue_item_count == 17
    assert refresh.covered_queue_item_count == 16
    assert refresh.uncovered_queue_item_ids == [
        "queue_raw_text_materials_folder_triage",
    ]
    assert refresh.legacy_next_action_ids == summary.next_action_ids
    assert refresh.refreshed_next_action_ids == [
        "queue_raw_text_materials_folder_triage",
    ]
    assert refresh.downstream_mutation_authorized is False
    assert refresh.next_material_entry == "015-raw-text-materials-folder-risk-triage"
    assert refresh.boundary_checks == {
        "015_queue_loaded": "passed",
        "016_coverage_loaded": "passed",
        "covered_items_excluded": "passed",
        "013_012_not_mutated": "passed",
    }


def test_materials_audit_queue_refresh_markdown_and_docs_are_in_sync():
    refresh = materials_audit.build_materials_audit_queue_refresh_summary()
    markdown = materials_audit.render_materials_audit_queue_refresh_markdown(refresh)
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Queue Refresh",
        "`queue-refresh-status=uncovered_queue_items_available`",
        "`015-queue-items=17`",
        "`016-covered-queue-items=16`",
        "`uncovered-queue-items=1`",
        "`refreshed-next-action-ids=1`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-materials-folder-risk-triage`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_external_material_inventory_refresh_summarizes_scoped_metadata():
    refresh = materials_audit.build_external_material_inventory_refresh_summary()

    assert refresh.refresh_id == "015-external-material-inventory-refresh"
    assert refresh.refresh_status == "scoped_metadata_registered"
    assert refresh.external_entry_counts == {
        "root_pdf": 9,
        "markdown_root": 11,
        "raw_source_root": 1,
        "preparation_root": 10,
    }
    assert refresh.scanned_entry_count == 31
    assert "Markdown/2800.《命理生死之书》100页.md" in (
        refresh.tracked_external_entry_ids
    )
    assert "资料原文/文本类/" in refresh.tracked_external_entry_ids
    assert refresh.untracked_material_entry_ids == []
    assert refresh.excluded_work_artifact_ids == [
        "资料整理/_inventory/",
        "资料整理/new_thread_prompt_2026-05-29.md",
        "资料整理/thread_handoff_2026-05-29.md",
    ]
    assert refresh.newly_registered_representation_ids == [
        "repr_life_death_book_100_pages_markdown_extract",
        "repr_raw_text_materials_folder",
    ]
    assert refresh.new_queue_item_ids == ["queue_raw_text_materials_folder_triage"]
    assert refresh.downstream_mutation_authorized is False
    assert refresh.next_material_entry == "015-raw-text-materials-folder-risk-triage"
    assert refresh.boundary_checks == {
        "external_roots_scanned_read_only": "passed",
        "015_metadata_registered": "passed",
        "workflow_artifacts_excluded": "passed",
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }


def test_external_material_inventory_refresh_markdown_and_docs_are_in_sync():
    refresh = materials_audit.build_external_material_inventory_refresh_summary()
    markdown = materials_audit.render_external_material_inventory_refresh_markdown(
        refresh
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 External Material Inventory Refresh",
        "`external-inventory-status=scoped_metadata_registered`",
        "`external-entries=31`",
        "`new-015-representations=2`",
        "`new-015-queue-items=1`",
        "`untracked-material-entries=0`",
        "`excluded-work-artifacts=3`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-materials-folder-risk-triage`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff
