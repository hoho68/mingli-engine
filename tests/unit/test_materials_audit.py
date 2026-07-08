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
            "select_bounded_source",
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

    triage_group = models.RawTextMaterialTriageGroup(
        group_id="raw_text_triage_test",
        source_root="资料原文/文本类/",
        group_label="Test Group",
        triage_status="source_selection_ready",
        risk_boundary="ordinary",
        file_count=1,
        priority_text_candidate_count=1,
        extension_counts={".pdf": 1},
        recommended_next_action="register_source",
    )
    triage_summary = models.RawTextMaterialTriageSummary(
        triage_id="015-raw-text-materials-folder-risk-triage",
        triage_status="triage_completed",
        source_root=triage_group.source_root,
        total_file_count=1,
        priority_text_candidate_count=1,
        triage_group_count=1,
        triage_status_counts={"source_selection_ready": 1},
        risk_boundary_counts={"ordinary": 1},
        extension_counts={".pdf": 1},
        next_group_ids=[triage_group.group_id],
        risk_review_group_ids=[],
        deferred_group_ids=[],
        downstream_mutation_authorized=False,
        next_material_entry="015-next-source-selection",
        boundary_checks={"013_012_not_mutated": "passed"},
    )

    assert triage_group.representative_paths == []
    assert triage_summary.guardrails == []

    selection_item = models.RawTextSourceSelectionItem(
        selection_id="liang_test_source",
        triage_group_id=triage_group.group_id,
        source_root=triage_group.source_root,
        relative_path="梁湘润简体/test.pdf",
        title_label="Liang test source",
        selection_status="ready_for_individual_review",
        risk_boundary="ordinary",
        recommended_next_action="review_cleaned_text",
        source_library_entry_id="entry_markdown_source_batch_004",
        source_material_id="material_markdown_source_batch_004",
        target_rule_families=["pattern_strength"],
    )
    selection_summary = models.RawTextSourceSelectionSummary(
        selection_id="015-liang-bazi-core-source-selection",
        selection_status="source_selection_completed",
        triage_group_id=triage_group.group_id,
        source_root=triage_group.source_root,
        source_selection_item_count=1,
        selected_for_individual_review_count=1,
        existing_batch_covered_count=0,
        variant_review_required_count=0,
        sensitive_boundary_deferred_count=0,
        status_counts={"ready_for_individual_review": 1},
        risk_boundary_counts={"ordinary": 1},
        target_rule_family_counts={"pattern_strength": 1},
        selected_item_ids=[selection_item.selection_id],
        deferred_item_ids=[],
        downstream_mutation_authorized=False,
        next_material_entry="015-next-individual-review",
        boundary_checks={"013_012_not_mutated": "passed"},
    )

    assert selection_item.guardrails == []
    assert selection_item.existing_learning_reference_ids == []
    assert selection_summary.guardrails == []

    cluster_item = models.RawTextSourceClusterSelectionItem(
        cluster_id="bazi_general_test_cluster",
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        cluster_label="Bazi General Test Cluster",
        cluster_status="selected_for_source_selection",
        risk_boundary="ordinary",
        file_count=1,
        priority_text_candidate_count=1,
        extension_counts={".pdf": 1},
        recommended_next_action="clarify_identity",
        target_rule_families=["pattern_strength"],
    )
    cluster_summary = models.RawTextSourceClusterSelectionSummary(
        selection_id="015-bazi-general-source-cluster-selection",
        selection_status="cluster_selection_completed",
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        cluster_count=1,
        clustered_file_count=1,
        clustered_priority_text_candidate_count=1,
        selected_cluster_count=1,
        deferred_cluster_count=0,
        cluster_status_counts={"selected_for_source_selection": 1},
        risk_boundary_counts={"ordinary": 1},
        extension_counts={".pdf": 1},
        target_rule_family_counts={"pattern_strength": 1},
        selected_cluster_ids=[cluster_item.cluster_id],
        deferred_cluster_ids=[],
        downstream_mutation_authorized=False,
        next_material_entry="015-next-cluster-source-selection",
        boundary_checks={"013_012_not_mutated": "passed"},
    )

    assert cluster_item.representative_paths == []
    assert cluster_item.guardrails == []
    assert cluster_summary.guardrails == []

    cluster_source_item = models.RawTextClusterSourceSelectionItem(
        selection_id="bazi_general_test_source",
        cluster_id="bazi_general_foundation_textbook_cluster",
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        title_label="Bazi General Test Source",
        selection_status="selected_for_identity_review",
        risk_boundary="ordinary",
        recommended_next_action="clarify_identity",
        relative_paths=["test.pdf"],
        file_count=1,
        priority_text_candidate_count=1,
        extension_counts={".pdf": 1},
        target_rule_families=["pattern_strength"],
        priority_score=80,
        size_mb_total=1.0,
    )
    cluster_source_summary = models.RawTextClusterSourceSelectionSummary(
        selection_id="015-bazi-general-cluster-source-selection",
        selection_status="cluster_source_selection_completed",
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        selected_cluster_ids=[cluster_source_item.cluster_id],
        source_selection_item_count=1,
        source_file_count=1,
        priority_text_candidate_count=1,
        selected_for_identity_review_count=1,
        variant_identity_review_count=0,
        deferred_after_cluster_selection_count=0,
        status_counts={"selected_for_identity_review": 1},
        risk_boundary_counts={"ordinary": 1},
        extension_counts={".pdf": 1},
        target_rule_family_counts={"pattern_strength": 1},
        selected_item_ids=[cluster_source_item.selection_id],
        variant_review_item_ids=[],
        deferred_item_ids=[],
        downstream_mutation_authorized=False,
        next_material_entry="015-next-source-identity-review",
        boundary_checks={"013_012_not_mutated": "passed"},
    )

    assert cluster_source_item.guardrails == []
    assert cluster_source_item.identity_review_note == ""
    assert cluster_source_summary.guardrails == []

    identity_review_item = models.RawTextSourceIdentityReviewItem(
        review_id="bazi_general_identity_test_source",
        source_selection_id=cluster_source_item.selection_id,
        cluster_id=cluster_source_item.cluster_id,
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        canonical_title_label="Bazi General Test Source",
        identity_status="registration_prep_ready",
        source_library_overlap_status="no_registered_overlap_found",
        registration_readiness="ready_for_registration_prep",
        recommended_next_action="register_source",
        next_review_target="registration_prep",
        target_rule_families=["pattern_strength"],
    )
    identity_review_summary = models.RawTextSourceIdentityReviewSummary(
        review_id="015-bazi-general-source-identity-review",
        review_status="source_identity_review_completed",
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        identity_review_item_count=1,
        existing_batch_overlap_count=0,
        registration_prep_ready_count=1,
        variant_choice_required_count=0,
        deferred_large_source_count=0,
        identity_status_counts={"registration_prep_ready": 1},
        source_library_overlap_counts={"no_registered_overlap_found": 1},
        registration_readiness_counts={"ready_for_registration_prep": 1},
        risk_boundary_counts={"ordinary": 1},
        target_rule_family_counts={"pattern_strength": 1},
        existing_batch_overlap_ids=[],
        registration_prep_item_ids=[identity_review_item.review_id],
        variant_choice_item_ids=[],
        deferred_item_ids=[],
        downstream_mutation_authorized=False,
        next_material_entry="015-next-registration-prep",
        boundary_checks={"013_012_not_mutated": "passed"},
    )

    assert identity_review_item.matched_source_library_entry_ids == []
    assert identity_review_item.guardrails == []
    assert identity_review_summary.guardrails == []

    registration_prep_item = models.RawTextSourceRegistrationPrepItem(
        prep_id="bazi_general_registration_prep_test_source",
        identity_review_id=identity_review_item.review_id,
        source_selection_id=identity_review_item.source_selection_id,
        cluster_id=identity_review_item.cluster_id,
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        registration_status="ready_for_source_registration",
        proposed_entry_id="entry_bazi_general_test_source_pdf",
        proposed_material_id="material_bazi_general_test_source_pdf",
        proposed_title="Bazi General Test Source",
        proposed_material_type="pdf",
        proposed_local_references=["test.pdf"],
        proposed_tracking_status="external_untracked",
        proposed_readiness_status="needs_preparation",
        proposed_priority_level="medium",
        proposed_next_action="prepare_material",
        risk_tier="ordinary",
        topic_tags=["foundation"],
        rule_families=["pattern_strength"],
        source_quality_notes="Registration-prep metadata only.",
        rights_notes="Do not copy long passages.",
        source_library_overlap_policy="new_entry_allowed_after_user_approval",
    )
    registration_prep_summary = models.RawTextSourceRegistrationPrepSummary(
        prep_id="015-bazi-general-registration-prep",
        prep_status="registration_prep_completed",
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        registration_prep_item_count=1,
        proposed_source_file_count=1,
        skipped_existing_batch_overlap_count=0,
        blocked_variant_choice_count=0,
        deferred_large_source_count=0,
        registration_status_counts={"ready_for_source_registration": 1},
        proposed_readiness_counts={"needs_preparation": 1},
        proposed_next_action_counts={"prepare_material": 1},
        risk_tier_counts={"ordinary": 1},
        target_rule_family_counts={"pattern_strength": 1},
        proposed_entry_ids=[registration_prep_item.proposed_entry_id],
        proposed_material_ids=[registration_prep_item.proposed_material_id],
        registration_prep_item_ids=[registration_prep_item.prep_id],
        skipped_existing_batch_overlap_ids=[],
        blocked_variant_choice_ids=[],
        deferred_item_ids=[],
        source_library_mutation_authorized=False,
        downstream_mutation_authorized=False,
        next_material_entry="015-next-source-registration",
        boundary_checks={"013_012_not_mutated": "passed"},
    )

    assert registration_prep_item.risk_notes == []
    assert registration_prep_item.guardrails == []
    assert registration_prep_summary.guardrails == []

    registration_summary = models.RawTextSourceRegistrationSummary(
        registration_id="015-bazi-general-source-registration",
        registration_status="source_registration_completed",
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        registered_entry_count=1,
        registered_source_file_count=1,
        skipped_existing_batch_overlap_count=0,
        blocked_variant_choice_count=0,
        deferred_large_source_count=0,
        registered_entry_ids=["entry_test"],
        registered_material_ids=["material_test"],
        skipped_existing_batch_overlap_ids=[],
        blocked_variant_choice_ids=[],
        deferred_item_ids=[],
        source_library_mutation_authorized=True,
        downstream_mutation_authorized=False,
        next_material_entry="015-bazi-general-source-preparation-reading",
        boundary_checks={"registered_entries_present": "passed"},
    )

    assert registration_summary.guardrails == []

    variant_review_item = models.BaziGeneralVariantDeferredReviewItem(
        item_id="bazi_general_variant_deferred_review_test_source",
        identity_review_id=identity_review_item.review_id,
        source_selection_id=identity_review_item.source_selection_id,
        cluster_id=identity_review_item.cluster_id,
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        review_kind="variant_choice",
        review_status="blocked_pending_variant_choice",
        decision="keep_variant_choice_blocked",
        canonical_choice_status="not_selected",
        local_references=["test-a.pdf", "test-b.pdf"],
        candidate_rule_families=["pattern_strength"],
    )
    variant_review_summary = models.BaziGeneralVariantDeferredReviewSummary(
        review_id="015-bazi-general-variant-choice-and-deferred-review",
        review_status="variant_deferred_review_completed",
        triage_group_id="raw_text_triage_bazi_general",
        source_root=triage_group.source_root,
        review_item_count=1,
        variant_review_item_count=1,
        deferred_review_item_count=0,
        selected_canonical_variant_count=0,
        source_library_registration_authorized_count=0,
        variant_review_item_ids=[variant_review_item.item_id],
        deferred_review_item_ids=[],
        selected_canonical_variant_ids=[],
        source_library_mutation_authorized=False,
        downstream_mutation_authorized=False,
        next_material_entry="015-bazi-general-next-source-batch-preparation",
        boundary_checks={"raw_materials_not_mutated": "passed"},
    )

    assert variant_review_item.selected_source_library_entry_id == ""
    assert variant_review_item.source_library_mutation_authorized is False
    assert variant_review_item.downstream_mutation_authorized is False
    assert variant_review_item.guardrails == []
    assert variant_review_summary.guardrails == []


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
        "load_raw_text_material_triage_groups",
        "build_raw_text_material_triage_summary",
        "render_raw_text_material_triage_markdown",
        "load_raw_text_source_selection_items",
        "build_raw_text_source_selection_summary",
        "render_raw_text_source_selection_markdown",
        "load_raw_text_next_cycle_source_selection_items",
        "build_raw_text_next_cycle_source_selection_summary",
        "render_raw_text_next_cycle_source_selection_markdown",
        "load_raw_text_next_cycle_identity_review_items",
        "build_raw_text_next_cycle_identity_review_summary",
        "render_raw_text_next_cycle_identity_review_markdown",
        "load_raw_text_next_cycle_cluster_source_selection_items",
        "build_raw_text_next_cycle_cluster_source_selection_summary",
        "render_raw_text_next_cycle_cluster_source_selection_markdown",
        "load_raw_text_next_cycle_followup_selection_items",
        "build_raw_text_next_cycle_followup_selection_summary",
        "render_raw_text_next_cycle_followup_selection_markdown",
        "load_raw_text_next_cycle_gated_cluster_review_prep_items",
        "build_raw_text_next_cycle_gated_cluster_review_prep_summary",
        "render_raw_text_next_cycle_gated_cluster_review_prep_markdown",
        "load_raw_text_next_cycle_gated_ordinary_source_selection_items",
        "build_raw_text_next_cycle_gated_ordinary_source_selection_summary",
        "render_raw_text_next_cycle_gated_ordinary_source_selection_markdown",
        "load_raw_text_next_cycle_gated_ordinary_followup_selection_items",
        "build_raw_text_next_cycle_gated_ordinary_followup_selection_summary",
        "render_raw_text_next_cycle_gated_ordinary_followup_selection_markdown",
        "load_raw_text_next_cycle_gated_ordinary_final_selection_items",
        "build_raw_text_next_cycle_gated_ordinary_final_selection_summary",
        "render_raw_text_next_cycle_gated_ordinary_final_selection_markdown",
        "load_raw_text_next_cycle_sensitive_risk_review_prep_items",
        "build_raw_text_next_cycle_sensitive_risk_review_prep_summary",
        "render_raw_text_next_cycle_sensitive_risk_review_prep_markdown",
        "load_raw_text_next_cycle_sensitive_source_level_risk_review_items",
        "build_raw_text_next_cycle_sensitive_source_level_risk_review_summary",
        "render_raw_text_next_cycle_sensitive_source_level_risk_review_markdown",
        "load_raw_text_next_cycle_sensitive_registration_prep_items",
        "build_raw_text_next_cycle_sensitive_registration_prep_summary",
        "render_raw_text_next_cycle_sensitive_registration_prep_markdown",
        "load_raw_text_next_cycle_sensitive_source_registration_items",
        "build_raw_text_next_cycle_sensitive_source_registration_summary",
        "render_raw_text_next_cycle_sensitive_source_registration_markdown",
        "load_raw_text_next_cycle_sensitive_preparation_boundary_items",
        "build_raw_text_next_cycle_sensitive_preparation_boundary_summary",
        "render_raw_text_next_cycle_sensitive_preparation_boundary_markdown",
        "load_raw_text_next_cycle_sensitive_preparation_reading_items",
        "build_raw_text_next_cycle_sensitive_preparation_reading_summary",
        "render_raw_text_next_cycle_sensitive_preparation_reading_markdown",
        "load_explicit_candidate_review_or_queue_refresh_items",
        "build_explicit_candidate_review_or_queue_refresh_summary",
        "render_explicit_candidate_review_or_queue_refresh_markdown",
        "load_external_material_inventory_refresh_confirmation_items",
        "build_external_material_inventory_refresh_confirmation_summary",
        "render_external_material_inventory_refresh_confirmation_markdown",
        "load_new_material_extraction_learning_loop_closure_items",
        "build_new_material_extraction_learning_loop_closure_summary",
        "render_new_material_extraction_learning_loop_closure_markdown",
        "load_new_material_intake_items",
        "build_new_material_intake_summary",
        "render_new_material_intake_markdown",
        "load_new_material_source_identity_review_items",
        "build_new_material_source_identity_review_summary",
        "render_new_material_source_identity_review_markdown",
        "load_new_material_registration_prep_items",
        "build_new_material_registration_prep_summary",
        "render_new_material_registration_prep_markdown",
        "load_new_material_source_registration_items",
        "build_new_material_source_registration_summary",
        "render_new_material_source_registration_markdown",
        "load_new_material_preparation_boundary_items",
        "build_new_material_preparation_boundary_summary",
        "render_new_material_preparation_boundary_markdown",
        "load_new_material_controlled_text_preparation_items",
        "build_new_material_controlled_text_preparation_summary",
        "render_new_material_controlled_text_preparation_markdown",
        "load_new_material_ocr_or_manual_transcription_items",
        "build_new_material_ocr_or_manual_transcription_summary",
        "render_new_material_ocr_or_manual_transcription_markdown",
        "load_new_material_ocr_runtime_setup_items",
        "build_new_material_ocr_runtime_setup_summary",
        "render_new_material_ocr_runtime_setup_markdown",
        "load_new_material_ocr_quality_remediation_items",
        "build_new_material_ocr_quality_remediation_summary",
        "render_new_material_ocr_quality_remediation_markdown",
        "load_new_material_human_corrected_transcription_prep_items",
        "build_new_material_human_corrected_transcription_prep_summary",
        "render_new_material_human_corrected_transcription_prep_markdown",
        "load_new_material_human_corrected_transcription_execution_items",
        "build_new_material_human_corrected_transcription_execution_summary",
        "render_new_material_human_corrected_transcription_execution_markdown",
        "load_new_material_expanded_corrected_transcription_selection_items",
        "build_new_material_expanded_corrected_transcription_selection_summary",
        "render_new_material_expanded_corrected_transcription_selection_markdown",
        "load_new_material_expanded_corrected_transcription_prep_items",
        "build_new_material_expanded_corrected_transcription_prep_summary",
        "render_new_material_expanded_corrected_transcription_prep_markdown",
        "load_new_material_expanded_corrected_transcription_execution_items",
        "build_new_material_expanded_corrected_transcription_execution_summary",
        "render_new_material_expanded_corrected_transcription_execution_markdown",
        "build_bazi_general_source_preparation_reading_summary",
        "render_bazi_general_source_preparation_reading_markdown",
        "load_bazi_general_variant_deferred_review_items",
        "build_bazi_general_variant_deferred_review_summary",
        "render_bazi_general_variant_deferred_review_markdown",
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
        "queue_markdown_source_batch_003_register",
        "queue_markdown_source_batch_004_prepare",
        "queue_duan_plain_mingxue_outline_extract",
    ]
    assert summary.extraction_ready_count == 24
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
        "queue_markdown_source_batch_003_register",
        "queue_markdown_source_batch_004_prepare",
        "queue_duan_plain_mingxue_outline_extract",
    ]


def test_materials_audit_queue_refresh_excludes_covered_016_queue_items():
    summary = materials_audit.build_materials_audit_progress_summary()
    refresh = materials_audit.build_materials_audit_queue_refresh_summary()

    assert refresh.refresh_id == "015-materials-audit-next-action-queue-refresh"
    assert refresh.refresh_status == "covered_or_completed_queue_exhausted"
    assert refresh.queue_item_count == 32
    assert refresh.covered_queue_item_count == 31
    assert refresh.locally_completed_queue_item_ids == [
        "queue_raw_text_materials_folder_triage",
    ]
    assert refresh.uncovered_queue_item_ids == []
    assert refresh.legacy_next_action_ids == summary.next_action_ids
    assert refresh.refreshed_next_action_ids == []
    assert refresh.downstream_mutation_authorized is False
    assert refresh.next_material_entry == "015-external-material-inventory-refresh"
    assert refresh.boundary_checks == {
        "015_queue_loaded": "passed",
        "016_coverage_loaded": "passed",
        "covered_items_excluded": "passed",
        "completed_items_excluded": "passed",
        "post_selected_variant_queue_surface_confirmed": "passed",
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
        "`queue-refresh-status=covered_or_completed_queue_exhausted`",
        "`015-queue-items=32`",
        "`016-covered-queue-items=31`",
        "`015-local-completed-queue-items=1`",
        "`uncovered-queue-items=0`",
        "`refreshed-next-action-ids=0`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-external-material-inventory-refresh`",
        "`post_selected_variant_queue_surface_confirmed`: `passed`",
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
    assert refresh.next_material_entry == "015-raw-text-next-cycle-source-selection"
    assert refresh.boundary_checks == {
        "external_roots_scanned_read_only": "passed",
        "015_metadata_registered": "passed",
        "workflow_artifacts_excluded": "passed",
        "post_queue_refresh_surface_confirmed": "passed",
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
        "`next-material-entry=015-raw-text-next-cycle-source-selection`",
        "`post_queue_refresh_surface_confirmed`: `passed`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_material_triage_groups_load_current_inventory_split():
    groups = materials_audit.load_raw_text_material_triage_groups()
    groups_by_id = {group.group_id: group for group in groups}

    assert len(groups) == 11
    assert sum(group.file_count for group in groups) == 1139
    assert sum(group.priority_text_candidate_count for group in groups) == 832
    assert groups_by_id["raw_text_triage_ritual_remedy_high_risk"].file_count == 428
    assert groups_by_id["raw_text_triage_media_course_deferred"].file_count == 246
    assert groups_by_id["raw_text_triage_bazi_general"].file_count == 184
    assert groups_by_id["raw_text_triage_unclassified_deferred"].file_count == 150
    assert groups_by_id["raw_text_triage_image_assets_deferred"].file_count == 52
    assert groups_by_id["raw_text_triage_fengshui_geo"].file_count == 34
    assert groups_by_id["raw_text_triage_qimen_dunjia"].file_count == 13
    assert groups_by_id["raw_text_triage_liang_bazi_core"].file_count == 12
    assert groups_by_id["raw_text_triage_ziwei_astrology"].file_count == 9
    assert groups_by_id["raw_text_triage_blind_school_sensitive"].file_count == 8
    assert groups_by_id["raw_text_triage_life_death_high_risk"].file_count == 3
    assert groups_by_id["raw_text_triage_liang_bazi_core"].triage_status == (
        "source_selection_ready"
    )
    assert groups_by_id["raw_text_triage_media_course_deferred"].triage_status == (
        "deferred_non_text"
    )
    assert groups_by_id["raw_text_triage_life_death_high_risk"].risk_boundary == (
        "high_risk"
    )


def test_raw_text_material_triage_summary_verifies_inventory_csv_counts():
    summary = materials_audit.build_raw_text_material_triage_summary()

    assert summary.triage_id == "015-raw-text-materials-folder-risk-triage"
    assert summary.triage_status == "triage_completed"
    assert summary.source_root == "资料原文/文本类/"
    assert summary.total_file_count == 1139
    assert summary.priority_text_candidate_count == 832
    assert summary.triage_group_count == 11
    assert summary.triage_status_counts == {
        "risk_review_required": 3,
        "deferred_non_text": 2,
        "source_selection_backlog": 1,
        "source_selection_ready": 1,
        "deferred_domain_review": 3,
        "deferred_unclassified": 1,
    }
    assert summary.risk_boundary_counts == {
        "high_risk": 2,
        "sensitive": 7,
        "ordinary": 2,
    }
    assert summary.extension_counts[".pdf"] == 767
    assert summary.extension_counts[".mp4"] == 218
    assert summary.extension_counts[".flv"] == 28
    assert summary.next_group_ids == ["raw_text_triage_liang_bazi_core"]
    assert summary.risk_review_group_ids == [
        "raw_text_triage_ritual_remedy_high_risk",
        "raw_text_triage_blind_school_sensitive",
        "raw_text_triage_life_death_high_risk",
    ]
    assert summary.deferred_group_ids == [
        "raw_text_triage_media_course_deferred",
        "raw_text_triage_image_assets_deferred",
        "raw_text_triage_fengshui_geo",
        "raw_text_triage_qimen_dunjia",
        "raw_text_triage_ziwei_astrology",
        "raw_text_triage_unclassified_deferred",
    ]
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-liang-bazi-core-source-selection"
    assert summary.boundary_checks == {
        "inventory_csv_loaded": "passed",
        "triage_groups_cover_inventory": "passed",
        "priority_candidates_accounted": "passed",
        "non_text_media_deferred": "passed",
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }


def test_raw_text_material_triage_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_material_triage_summary()
    markdown = materials_audit.render_raw_text_material_triage_markdown(summary)
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Materials Folder Risk Triage",
        "`raw-text-triage-status=triage_completed`",
        "`raw-text-total-files=1139`",
        "`raw-text-priority-candidates=832`",
        "`raw-text-triage-groups=11`",
        "`risk-review-groups=3`",
        "`deferred-groups=6`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-liang-bazi-core-source-selection`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_source_selection_items_load_liang_core_packet():
    items = materials_audit.load_raw_text_source_selection_items()
    items_by_id = {item.selection_id: item for item in items}

    assert len(items) == 12
    assert {
        item.triage_group_id for item in items
    } == {"raw_text_triage_liang_bazi_core"}
    assert all(item.source_root == materials_audit.RAW_TEXT_TRIAGE_SOURCE_ROOT for item in items)
    assert all(item.relative_path.startswith("梁湘润简体/") for item in items)
    assert all(item.source_library_entry_id for item in items)
    assert all(item.source_material_id for item in items)
    assert items_by_id["liang_tianyuan_wuxian_commentary"].selection_status == (
        "ready_for_individual_review"
    )
    assert items_by_id["liang_yushi_yongshen_ciyuan"].selection_status == (
        "ready_for_individual_review"
    )
    assert items_by_id["liang_four_corner_digest"].selection_status == (
        "variant_review_required"
    )
    assert items_by_id["liang_female_destiny_detail"].selection_status == (
        "sensitive_boundary_deferred"
    )
    assert (
        "lp_markdown_batch_004_pattern_strength_001"
        in items_by_id[
            "liang_tianyuan_wuxian_commentary"
        ].existing_learning_reference_ids
    )


def test_raw_text_source_selection_summary_counts_review_surface():
    summary = materials_audit.build_raw_text_source_selection_summary()

    assert summary.selection_id == "015-liang-bazi-core-source-selection"
    assert summary.selection_status == "source_selection_completed"
    assert summary.triage_group_id == "raw_text_triage_liang_bazi_core"
    assert summary.source_selection_item_count == 12
    assert summary.selected_for_individual_review_count == 2
    assert summary.existing_batch_covered_count == 8
    assert summary.variant_review_required_count == 1
    assert summary.sensitive_boundary_deferred_count == 1
    assert summary.status_counts == {
        "existing_batch_covered": 8,
        "ready_for_individual_review": 2,
        "variant_review_required": 1,
        "sensitive_boundary_deferred": 1,
    }
    assert summary.risk_boundary_counts == {
        "ordinary": 10,
        "sensitive": 2,
    }
    assert summary.target_rule_family_counts == {
        "branch_interaction": 3,
        "luck_cycle": 2,
        "pattern_strength": 6,
        "ten_god_relation": 1,
        "useful_god_candidate": 6,
    }
    assert summary.selected_item_ids == [
        "liang_tianyuan_wuxian_commentary",
        "liang_yushi_yongshen_ciyuan",
    ]
    assert summary.deferred_item_ids == [
        "liang_four_corner_digest",
        "liang_female_destiny_detail",
    ]
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-liang-bazi-core-individual-review"
    assert summary.boundary_checks == {
        "selection_items_loaded": "passed",
        "triage_group_loaded": "passed",
        "triage_group_file_count_matched": "passed",
        "existing_source_batches_preserved": "passed",
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }


def test_raw_text_source_selection_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_source_selection_summary()
    markdown = materials_audit.render_raw_text_source_selection_markdown(summary)
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Liang Bazi Core Source Selection",
        "`source-selection-status=source_selection_completed`",
        "`source-selection-items=12`",
        "`existing-batch-covered=8`",
        "`selected-for-individual-review=2`",
        "`variant-review-required=1`",
        "`sensitive-boundary-deferred=1`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-liang-bazi-core-individual-review`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_source_cluster_selection_items_load_bazi_general_packet():
    clusters = materials_audit.load_raw_text_source_cluster_selection_items()
    clusters_by_id = {cluster.cluster_id: cluster for cluster in clusters}

    assert len(clusters) == 7
    assert {
        cluster.triage_group_id for cluster in clusters
    } == {"raw_text_triage_bazi_general"}
    assert all(
        cluster.source_root == materials_audit.RAW_TEXT_TRIAGE_SOURCE_ROOT
        for cluster in clusters
    )
    assert sum(cluster.file_count for cluster in clusters) == 184
    assert sum(cluster.priority_text_candidate_count for cluster in clusters) == 183
    assert clusters_by_id[
        "bazi_general_foundation_textbook_cluster"
    ].cluster_status == "selected_for_source_selection"
    assert clusters_by_id[
        "bazi_general_classical_reference_cluster"
    ].cluster_status == "selected_for_source_selection"
    assert clusters_by_id[
        "bazi_general_sensitive_topic_cluster"
    ].cluster_status == "sensitive_boundary_deferred"
    assert clusters_by_id[
        "bazi_general_misc_identity_review_cluster"
    ].cluster_status == "identity_review_required"
    assert "八字命理讲义教材（299页）.pdf" in clusters_by_id[
        "bazi_general_foundation_textbook_cluster"
    ].representative_paths
    assert "滴天髓.pdf" in clusters_by_id[
        "bazi_general_classical_reference_cluster"
    ].representative_paths


def test_raw_text_source_cluster_selection_summary_counts_bazi_general_clusters():
    summary = materials_audit.build_raw_text_source_cluster_selection_summary()

    assert summary.selection_id == "015-bazi-general-source-cluster-selection"
    assert summary.selection_status == "cluster_selection_completed"
    assert summary.triage_group_id == "raw_text_triage_bazi_general"
    assert summary.cluster_count == 7
    assert summary.clustered_file_count == 184
    assert summary.clustered_priority_text_candidate_count == 183
    assert summary.selected_cluster_count == 2
    assert summary.deferred_cluster_count == 3
    assert summary.cluster_status_counts == {
        "selected_for_source_selection": 2,
        "backlog_cluster": 2,
        "identity_review_required": 2,
        "sensitive_boundary_deferred": 1,
    }
    assert summary.risk_boundary_counts == {
        "ordinary": 6,
        "sensitive": 1,
    }
    assert summary.extension_counts == {
        ".pdf": 148,
        ".doc": 27,
        ".txt": 5,
        ".docx": 3,
        ".ppt": 1,
    }
    assert summary.target_rule_family_counts == {
        "branch_interaction": 3,
        "luck_cycle": 2,
        "pattern_strength": 5,
        "ten_god_relation": 3,
        "useful_god_candidate": 3,
    }
    assert summary.selected_cluster_ids == [
        "bazi_general_foundation_textbook_cluster",
        "bazi_general_classical_reference_cluster",
    ]
    assert summary.deferred_cluster_ids == [
        "bazi_general_modern_method_series_cluster",
        "bazi_general_sensitive_topic_cluster",
        "bazi_general_misc_identity_review_cluster",
    ]
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-bazi-general-cluster-source-selection"
    assert summary.boundary_checks == {
        "cluster_items_loaded": "passed",
        "triage_group_loaded": "passed",
        "triage_group_file_count_matched": "passed",
        "triage_group_priority_count_matched": "passed",
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }


def test_raw_text_source_cluster_selection_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_source_cluster_selection_summary()
    markdown = materials_audit.render_raw_text_source_cluster_selection_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Bazi General Source Cluster Selection",
        "`cluster-selection-status=cluster_selection_completed`",
        "`cluster-selection-items=7`",
        "`clustered-files=184`",
        "`clustered-priority-candidates=183`",
        "`selected-clusters=2`",
        "`deferred-clusters=3`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-bazi-general-cluster-source-selection`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_source_selection_items_load_boundary_plan():
    items = materials_audit.load_raw_text_next_cycle_source_selection_items()
    items_by_id = {item.selection_id: item for item in items}

    assert len(items) == 5
    assert {item.triage_group_id for item in items} == {
        "raw_text_triage_bazi_general"
    }
    assert all(
        item.source_root == materials_audit.RAW_TEXT_TRIAGE_SOURCE_ROOT
        for item in items
    )
    assert {
        item.cluster_id for item in items if item.selection_status == "selected_for_identity_review"
    } == {
        "bazi_general_modern_method_series_cluster",
        "bazi_general_misc_identity_review_cluster",
    }
    assert items_by_id[
        "next_cycle_bazi_modern_method_series"
    ].recommended_next_action == "clarify_identity"
    assert items_by_id[
        "next_cycle_bazi_misc_identity_review"
    ].file_count == 36
    assert items_by_id[
        "next_cycle_bazi_case_collection_deferred"
    ].selection_status == "deferred_case_collection"
    assert items_by_id[
        "next_cycle_bazi_practical_formula_deferred"
    ].recommended_next_action == "defer"
    assert items_by_id[
        "next_cycle_bazi_sensitive_topic_risk_review"
    ].risk_boundary == "sensitive"


def test_raw_text_next_cycle_source_selection_summary_counts_boundary_plan():
    summary = materials_audit.build_raw_text_next_cycle_source_selection_summary()

    assert summary.selection_id == "015-raw-text-next-cycle-source-selection"
    assert summary.selection_status == "next_cycle_source_selection_completed"
    assert summary.triage_group_id == "raw_text_triage_bazi_general"
    assert summary.source_root == materials_audit.RAW_TEXT_TRIAGE_SOURCE_ROOT
    assert summary.selection_item_count == 5
    assert summary.selected_for_identity_review_count == 2
    assert summary.deferred_cluster_count == 2
    assert summary.risk_review_cluster_count == 1
    assert summary.status_counts == {
        "selected_for_identity_review": 2,
        "deferred_case_collection": 1,
        "deferred_formula_review": 1,
        "risk_review_required": 1,
    }
    assert summary.risk_boundary_counts == {
        "ordinary": 4,
        "sensitive": 1,
    }
    assert summary.target_rule_family_counts == {
        "branch_interaction": 3,
        "luck_cycle": 2,
        "pattern_strength": 3,
        "ten_god_relation": 2,
        "useful_god_candidate": 1,
    }
    assert summary.selected_cluster_ids == [
        "bazi_general_modern_method_series_cluster",
        "bazi_general_misc_identity_review_cluster",
    ]
    assert summary.deferred_cluster_ids == [
        "bazi_general_case_collection_cluster",
        "bazi_general_practical_formula_cluster",
    ]
    assert summary.risk_review_cluster_ids == [
        "bazi_general_sensitive_topic_cluster",
    ]
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-raw-text-next-cycle-identity-review"
    assert summary.boundary_checks == {
        "next_cycle_items_loaded": "passed",
        "source_cluster_items_loaded": "passed",
        "external_inventory_entrypoint_confirmed": "passed",
        "selected_clusters_need_identity_review": "passed",
        "deferred_clusters_stay_deferred": "passed",
        "sensitive_clusters_stay_risk_review": "passed",
        "huntian_baolan_deferred": "passed",
        "raw_materials_not_mutated": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }


def test_raw_text_next_cycle_source_selection_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_next_cycle_source_selection_summary()
    markdown = materials_audit.render_raw_text_next_cycle_source_selection_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Source Selection",
        "`next-cycle-source-selection-status=next_cycle_source_selection_completed`",
        "`next-cycle-source-selection-items=5`",
        "`selected-for-identity-review=2`",
        "`deferred-clusters=2`",
        "`risk-review-clusters=1`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-next-cycle-identity-review`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_identity_review_items_load_selected_clusters_only():
    items = materials_audit.load_raw_text_next_cycle_identity_review_items()
    items_by_id = {item.review_id: item for item in items}

    assert len(items) == 2
    assert {item.triage_group_id for item in items} == {
        "raw_text_triage_bazi_general"
    }
    assert {item.source_selection_id for item in items} == {
        "next_cycle_bazi_modern_method_series",
        "next_cycle_bazi_misc_identity_review",
    }
    assert {item.cluster_id for item in items} == {
        "bazi_general_modern_method_series_cluster",
        "bazi_general_misc_identity_review_cluster",
    }
    assert all(
        item.identity_status == "cluster_source_selection_required"
        for item in items
    )
    assert all(
        item.registration_readiness == "needs_cluster_source_selection"
        for item in items
    )
    assert all(not item.matched_source_library_entry_ids for item in items)
    assert items_by_id[
        "next_cycle_identity_bazi_modern_method_series"
    ].file_count == 39
    assert items_by_id[
        "next_cycle_identity_bazi_misc_review"
    ].target_rule_families == ["branch_interaction"]


def test_raw_text_next_cycle_identity_review_summary_counts_selected_clusters():
    summary = materials_audit.build_raw_text_next_cycle_identity_review_summary()

    assert summary.review_id == "015-raw-text-next-cycle-identity-review"
    assert summary.review_status == "next_cycle_identity_review_completed"
    assert summary.triage_group_id == "raw_text_triage_bazi_general"
    assert summary.source_root == materials_audit.RAW_TEXT_TRIAGE_SOURCE_ROOT
    assert summary.identity_review_item_count == 2
    assert summary.cluster_source_selection_required_count == 2
    assert summary.registration_prep_ready_count == 0
    assert summary.source_library_overlap_found_count == 0
    assert summary.identity_status_counts == {
        "cluster_source_selection_required": 2,
    }
    assert summary.source_library_overlap_counts == {
        "no_registered_cluster_overlap_found": 2,
    }
    assert summary.registration_readiness_counts == {
        "needs_cluster_source_selection": 2,
    }
    assert summary.risk_boundary_counts == {"ordinary": 2}
    assert summary.target_rule_family_counts == {
        "branch_interaction": 1,
        "pattern_strength": 1,
        "useful_god_candidate": 1,
    }
    assert summary.cluster_source_selection_required_ids == [
        "next_cycle_identity_bazi_modern_method_series",
        "next_cycle_identity_bazi_misc_review",
    ]
    assert summary.registration_prep_ready_ids == []
    assert summary.source_library_overlap_ids == []
    assert summary.downstream_mutation_authorized is False
    assert summary.source_library_mutation_authorized is False
    assert (
        summary.next_material_entry
        == "015-raw-text-next-cycle-cluster-source-selection"
    )
    assert summary.boundary_checks == {
        "identity_review_items_loaded": "passed",
        "next_cycle_source_selection_items_loaded": "passed",
        "selected_source_selection_references_valid": "passed",
        "selected_clusters_only": "passed",
        "cluster_counts_match_source_selection": "passed",
        "deferred_clusters_remain_out_of_scope": "passed",
        "risk_review_clusters_remain_out_of_scope": "passed",
        "raw_materials_not_mutated": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }


def test_raw_text_next_cycle_identity_review_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_next_cycle_identity_review_summary()
    markdown = materials_audit.render_raw_text_next_cycle_identity_review_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Identity Review",
        "`next-cycle-identity-review-status=next_cycle_identity_review_completed`",
        "`next-cycle-identity-review-items=2`",
        "`cluster-source-selection-required=2`",
        "`registration-prep-ready=0`",
        "`source-library-overlap-found=0`",
        "`source-library-mutation-authorized=false`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-next-cycle-cluster-source-selection`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_cluster_source_selection_items_load_authorized_sources():
    items = materials_audit.load_raw_text_next_cycle_cluster_source_selection_items()
    items_by_id = {item.selection_id: item for item in items}

    assert len(items) == 2
    assert {item.source_selection_id for item in items} == {
        "next_cycle_bazi_modern_method_series",
        "next_cycle_bazi_misc_identity_review",
    }
    assert {item.cluster_id for item in items} == {
        "bazi_general_modern_method_series_cluster",
        "bazi_general_misc_identity_review_cluster",
    }
    assert all(item.selection_status == "selected_for_registration" for item in items)
    assert items_by_id[
        "next_cycle_cluster_source_true_spirit_positioning"
    ].relative_paths == [
        "八字/07、真神在哪里？定位八字真神【万千周易网zhouyi666.com，9米每套 】.pdf"
    ]
    assert items_by_id[
        "next_cycle_cluster_source_mingli_wangdoujing"
    ].relative_paths == ["1_命理望斗经(1).pdf"]


def test_raw_text_next_cycle_cluster_source_selection_summary_counts_authorized_chain():
    summary = materials_audit.build_raw_text_next_cycle_cluster_source_selection_summary()

    assert summary.selection_id == "015-raw-text-next-cycle-cluster-source-selection"
    assert summary.selection_status == "next_cycle_cluster_source_selection_completed"
    assert summary.source_selection_item_count == 2
    assert summary.selected_for_registration_count == 2
    assert summary.registered_source_entry_count == 2
    assert summary.candidate_extract_count == 2
    assert summary.formal_evidence_count == 2
    assert summary.selected_item_ids == [
        "next_cycle_cluster_source_true_spirit_positioning",
        "next_cycle_cluster_source_mingli_wangdoujing",
    ]
    assert summary.registered_entry_ids == [
        "entry_bazi_general_true_spirit_positioning_pdf",
        "entry_bazi_general_mingli_wangdoujing_pdf",
    ]
    assert summary.candidate_ids == [
        "candidate_bazi_general_true_spirit_useful_god_001",
        "candidate_bazi_general_wangdoujing_branch_interaction_001",
    ]
    assert summary.evidence_ids == [
        "bazi_general_true_spirit_useful_god_001",
        "bazi_general_wangdoujing_branch_interaction_001",
    ]
    assert summary.source_library_mutation_authorized is True
    assert summary.downstream_mutation_authorized is True
    assert summary.next_material_entry == "015-raw-text-next-cycle-followup-selection"
    assert summary.boundary_checks == {
        "cluster_source_selection_items_loaded": "passed",
        "identity_review_references_valid": "passed",
        "source_paths_are_relative": "passed",
        "selected_clusters_only": "passed",
        "source_library_entries_registered": "passed",
        "013_candidates_promoted": "passed",
        "012_evidence_promoted": "passed",
        "deferred_clusters_remain_out_of_scope": "passed",
        "risk_review_clusters_remain_out_of_scope": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_cluster_source_selection_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_next_cycle_cluster_source_selection_summary()
    markdown = materials_audit.render_raw_text_next_cycle_cluster_source_selection_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Cluster Source Selection",
        "`next-cycle-cluster-source-selection-status=next_cycle_cluster_source_selection_completed`",
        "`next-cycle-cluster-source-selection-items=2`",
        "`selected-for-registration=2`",
        "`registered-source-entries=2`",
        "`candidate-extracts=2`",
        "`formal-evidence-units=2`",
        "`source-library-mutation-authorized=true`",
        "`downstream-mutation-authorized=true`",
        "`next-material-entry=015-raw-text-next-cycle-followup-selection`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_followup_selection_items_load_authorized_sources():
    items = materials_audit.load_raw_text_next_cycle_followup_selection_items()
    items_by_id = {item.selection_id: item for item in items}

    assert len(items) == 2
    assert {item.source_selection_id for item in items} == {
        "next_cycle_bazi_modern_method_series",
        "next_cycle_bazi_misc_identity_review",
    }
    assert {item.cluster_id for item in items} == {
        "bazi_general_modern_method_series_cluster",
        "bazi_general_misc_identity_review_cluster",
    }
    assert all(item.selection_status == "selected_for_registration" for item in items)
    assert items_by_id[
        "next_cycle_followup_source_xinpai_essence_part2"
    ].relative_paths == [
        "佚名 - 新派命理精髓详解34份/新派命理精髓详解之二.pdf"
    ]
    assert items_by_id[
        "next_cycle_followup_source_xingming_shuozheng_vol1"
    ].relative_paths == ["霍敏卿-星命说证正续合编上册.pdf"]


def test_raw_text_next_cycle_followup_selection_summary_counts_authorized_chain():
    summary = materials_audit.build_raw_text_next_cycle_followup_selection_summary()

    assert summary.selection_id == "015-raw-text-next-cycle-followup-selection"
    assert summary.selection_status == "next_cycle_followup_selection_completed"
    assert summary.source_selection_item_count == 2
    assert summary.selected_for_registration_count == 2
    assert summary.registered_source_entry_count == 2
    assert summary.candidate_extract_count == 2
    assert summary.formal_evidence_count == 2
    assert summary.selected_item_ids == [
        "next_cycle_followup_source_xinpai_essence_part2",
        "next_cycle_followup_source_xingming_shuozheng_vol1",
    ]
    assert summary.registered_entry_ids == [
        "entry_bazi_general_xinpai_essence_part2_pdf",
        "entry_bazi_general_xingming_shuozheng_vol1_pdf",
    ]
    assert summary.candidate_ids == [
        "candidate_bazi_general_xinpai_essence_pattern_strength_001",
        "candidate_bazi_general_xingming_shuozheng_branch_interaction_001",
    ]
    assert summary.evidence_ids == [
        "bazi_general_xinpai_essence_pattern_strength_001",
        "bazi_general_xingming_shuozheng_branch_interaction_001",
    ]
    assert summary.source_library_mutation_authorized is True
    assert summary.downstream_mutation_authorized is True
    assert summary.next_material_entry == (
        "015-raw-text-next-cycle-gated-cluster-review-prep"
    )
    assert summary.boundary_checks == {
        "followup_selection_items_loaded": "passed",
        "cluster_source_selection_references_valid": "passed",
        "source_paths_are_relative": "passed",
        "selected_clusters_only": "passed",
        "source_library_entries_registered": "passed",
        "013_candidates_promoted": "passed",
        "012_evidence_promoted": "passed",
        "case_formula_clusters_remain_deferred": "passed",
        "sensitive_clusters_remain_risk_gated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_followup_selection_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_next_cycle_followup_selection_summary()
    markdown = materials_audit.render_raw_text_next_cycle_followup_selection_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Followup Selection",
        "`next-cycle-followup-selection-status=next_cycle_followup_selection_completed`",
        "`next-cycle-followup-selection-items=2`",
        "`selected-for-registration=2`",
        "`registered-source-entries=2`",
        "`candidate-extracts=2`",
        "`formal-evidence-units=2`",
        "`source-library-mutation-authorized=true`",
        "`downstream-mutation-authorized=true`",
        "`next-material-entry=015-raw-text-next-cycle-gated-cluster-review-prep`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_gated_cluster_review_prep_items_load_boundary_packet():
    items = materials_audit.load_raw_text_next_cycle_gated_cluster_review_prep_items()
    items_by_id = {item.prep_id: item for item in items}

    assert len(items) == 3
    assert {item.source_selection_id for item in items} == {
        "next_cycle_bazi_case_collection_deferred",
        "next_cycle_bazi_practical_formula_deferred",
        "next_cycle_bazi_sensitive_topic_risk_review",
    }
    assert {item.cluster_id for item in items} == {
        "bazi_general_case_collection_cluster",
        "bazi_general_practical_formula_cluster",
        "bazi_general_sensitive_topic_cluster",
    }
    assert items_by_id[
        "gated_prep_case_collection_boundary_001"
    ].prep_status == "prepared_for_bounded_source_selection"
    assert items_by_id[
        "gated_prep_practical_formula_boundary_001"
    ].recommended_next_action == "select_bounded_source"
    assert items_by_id[
        "gated_prep_sensitive_topic_boundary_001"
    ].prep_status == "risk_review_required"
    assert items_by_id[
        "gated_prep_sensitive_topic_boundary_001"
    ].risk_boundary == "sensitive"
    assert all(not item.source_library_mutation_authorized for item in items)
    assert all(not item.downstream_mutation_authorized for item in items)


def test_raw_text_next_cycle_gated_cluster_review_prep_summary_counts_boundaries():
    summary = materials_audit.build_raw_text_next_cycle_gated_cluster_review_prep_summary()

    assert summary.prep_id == "015-raw-text-next-cycle-gated-cluster-review-prep"
    assert summary.prep_status == "gated_cluster_review_prep_completed"
    assert summary.prep_item_count == 3
    assert summary.selected_for_source_selection_count == 2
    assert summary.risk_review_required_count == 1
    assert summary.deferred_after_prep_count == 0
    assert summary.source_library_mutation_authorized is False
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "015-raw-text-next-cycle-gated-ordinary-source-selection"
    )
    assert summary.prepared_source_selection_ids == [
        "gated_prep_case_collection_boundary_001",
        "gated_prep_practical_formula_boundary_001",
    ]
    assert summary.risk_review_item_ids == [
        "gated_prep_sensitive_topic_boundary_001"
    ]
    assert summary.status_counts == {
        "prepared_for_bounded_source_selection": 2,
        "risk_review_required": 1,
    }
    assert summary.risk_boundary_counts == {
        "ordinary": 2,
        "sensitive": 1,
    }
    assert summary.target_rule_family_counts == {
        "branch_interaction": 2,
        "luck_cycle": 2,
        "pattern_strength": 2,
        "ten_god_relation": 2,
    }
    assert summary.boundary_checks == {
        "gated_prep_items_loaded": "passed",
        "source_selection_references_valid": "passed",
        "case_formula_clusters_prepared_only": "passed",
        "sensitive_cluster_stays_risk_review": "passed",
        "no_source_library_mutation": "passed",
        "no_013_012_mutation": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_gated_cluster_review_prep_markdown_and_docs_sync():
    summary = materials_audit.build_raw_text_next_cycle_gated_cluster_review_prep_summary()
    markdown = materials_audit.render_raw_text_next_cycle_gated_cluster_review_prep_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Gated Cluster Review Prep",
        "`gated-cluster-review-prep-status=gated_cluster_review_prep_completed`",
        "`gated-cluster-review-prep-items=3`",
        "`selected-for-source-selection=2`",
        "`risk-review-required=1`",
        "`source-library-mutation-authorized=false`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-next-cycle-gated-ordinary-source-selection`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_gated_ordinary_source_selection_items_load_selected_records():
    items = materials_audit.load_raw_text_next_cycle_gated_ordinary_source_selection_items()
    items_by_id = {item.selection_id: item for item in items}

    assert len(items) == 2
    assert set(items_by_id) == {
        "gated_ordinary_source_mingzao_chunqiu_case_collection",
        "gated_ordinary_source_sizhu_yuce_yaojue_formula",
    }
    assert {
        item.prep_id
        for item in items
    } == {
        "gated_prep_case_collection_boundary_001",
        "gated_prep_practical_formula_boundary_001",
    }
    assert {
        item.cluster_id
        for item in items
    } == {
        "bazi_general_case_collection_cluster",
        "bazi_general_practical_formula_cluster",
    }
    assert all(item.selection_status == "selected_for_registration" for item in items)
    assert all(item.risk_boundary == "ordinary" for item in items)
    assert all(item.source_library_mutation_authorized for item in items)
    assert all(item.downstream_mutation_authorized for item in items)
    assert items_by_id[
        "gated_ordinary_source_mingzao_chunqiu_case_collection"
    ].relative_paths == ["八字18本/命造春秋  188P.pdf"]
    assert items_by_id[
        "gated_ordinary_source_sizhu_yuce_yaojue_formula"
    ].relative_paths == ["四柱预测要诀.pdf"]
    assert all(
        "sensitive" not in item.cluster_id and "sensitive" not in item.selection_id
        for item in items
    )


def test_raw_text_next_cycle_gated_ordinary_source_selection_summary_counts_closure():
    summary = (
        materials_audit.build_raw_text_next_cycle_gated_ordinary_source_selection_summary()
    )

    assert summary.selection_id == (
        "015-raw-text-next-cycle-gated-ordinary-source-selection"
    )
    assert summary.selection_status == "gated_ordinary_source_selection_completed"
    assert summary.source_selection_item_count == 2
    assert summary.source_file_count == 2
    assert summary.priority_text_candidate_count == 2
    assert summary.selected_for_registration_count == 2
    assert summary.registered_source_entry_count == 2
    assert summary.candidate_extract_count == 2
    assert summary.formal_evidence_count == 2
    assert summary.source_library_mutation_authorized is True
    assert summary.downstream_mutation_authorized is True
    assert summary.next_material_entry == (
        "015-raw-text-next-cycle-gated-ordinary-followup-selection"
    )
    assert summary.selected_item_ids == [
        "gated_ordinary_source_mingzao_chunqiu_case_collection",
        "gated_ordinary_source_sizhu_yuce_yaojue_formula",
    ]
    assert summary.prep_item_ids == [
        "gated_prep_case_collection_boundary_001",
        "gated_prep_practical_formula_boundary_001",
    ]
    assert summary.sensitive_risk_review_item_ids == [
        "gated_prep_sensitive_topic_boundary_001"
    ]
    assert summary.registered_entry_ids == [
        "entry_bazi_general_mingzao_chunqiu_case_pdf",
        "entry_bazi_general_sizhu_yuce_yaojue_pdf",
    ]
    assert summary.candidate_ids == [
        "candidate_bazi_general_mingzao_chunqiu_luck_cycle_001",
        "candidate_bazi_general_sizhu_yuce_yaojue_pattern_strength_001",
    ]
    assert summary.evidence_ids == [
        "bazi_general_mingzao_chunqiu_luck_cycle_001",
        "bazi_general_sizhu_yuce_yaojue_pattern_strength_001",
    ]
    assert summary.status_counts == {"selected_for_registration": 2}
    assert summary.risk_boundary_counts == {"ordinary": 2}
    assert summary.target_rule_family_counts == {
        "luck_cycle": 1,
        "pattern_strength": 1,
    }
    assert summary.boundary_checks == {
        "gated_ordinary_selection_items_loaded": "passed",
        "gated_prep_references_valid": "passed",
        "source_paths_are_relative": "passed",
        "ordinary_gated_clusters_only": "passed",
        "source_library_entries_registered": "passed",
        "013_candidates_promoted": "passed",
        "012_evidence_promoted": "passed",
        "sensitive_cluster_remains_risk_review": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_gated_ordinary_source_selection_markdown_and_docs_sync():
    summary = (
        materials_audit.build_raw_text_next_cycle_gated_ordinary_source_selection_summary()
    )
    markdown = (
        materials_audit.render_raw_text_next_cycle_gated_ordinary_source_selection_markdown(
            summary
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Gated Ordinary Source Selection",
        "`gated-ordinary-source-selection-status=gated_ordinary_source_selection_completed`",
        "`gated-ordinary-source-selection-items=2`",
        "`selected-for-registration=2`",
        "`registered-source-entries=2`",
        "`candidate-extracts=2`",
        "`formal-evidence=2`",
        "`source-library-mutation-authorized=true`",
        "`downstream-mutation-authorized=true`",
        "`next-material-entry=015-raw-text-next-cycle-gated-ordinary-followup-selection`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_gated_ordinary_followup_selection_items_load_selected_records():
    items = (
        materials_audit.load_raw_text_next_cycle_gated_ordinary_followup_selection_items()
    )
    items_by_id = {item.selection_id: item for item in items}

    assert len(items) == 2
    assert set(items_by_id) == {
        "gated_ordinary_followup_source_bazi_baijue_case_collection",
        "gated_ordinary_followup_source_mingli_mijue_formula",
    }
    assert {item.prep_id for item in items} == {
        "gated_prep_case_collection_boundary_001",
        "gated_prep_practical_formula_boundary_001",
    }
    assert {item.prior_selection_id for item in items} == {
        "gated_ordinary_source_mingzao_chunqiu_case_collection",
        "gated_ordinary_source_sizhu_yuce_yaojue_formula",
    }
    assert {item.cluster_id for item in items} == {
        "bazi_general_case_collection_cluster",
        "bazi_general_practical_formula_cluster",
    }
    assert all(item.selection_status == "selected_for_registration" for item in items)
    assert all(item.risk_boundary == "ordinary" for item in items)
    assert all(item.source_library_mutation_authorized for item in items)
    assert all(item.downstream_mutation_authorized for item in items)
    assert items_by_id[
        "gated_ordinary_followup_source_bazi_baijue_case_collection"
    ].relative_paths == ["八字18本/八字百诀 上册  214P.pdf"]
    assert items_by_id[
        "gated_ordinary_followup_source_mingli_mijue_formula"
    ].relative_paths == ["命理秘诀(1).pdf"]
    first_paths = {
        path
        for item in materials_audit.load_raw_text_next_cycle_gated_ordinary_source_selection_items()
        for path in item.relative_paths
    }
    assert all(
        path not in first_paths for item in items for path in item.relative_paths
    )


def test_raw_text_next_cycle_gated_ordinary_followup_selection_summary_counts_closure():
    summary = (
        materials_audit.build_raw_text_next_cycle_gated_ordinary_followup_selection_summary()
    )

    assert summary.selection_id == (
        "015-raw-text-next-cycle-gated-ordinary-followup-selection"
    )
    assert summary.selection_status == "gated_ordinary_followup_selection_completed"
    assert summary.source_selection_item_count == 2
    assert summary.source_file_count == 2
    assert summary.priority_text_candidate_count == 2
    assert summary.selected_for_registration_count == 2
    assert summary.registered_source_entry_count == 2
    assert summary.candidate_extract_count == 2
    assert summary.formal_evidence_count == 2
    assert summary.source_library_mutation_authorized is True
    assert summary.downstream_mutation_authorized is True
    assert summary.next_material_entry == (
        "015-raw-text-next-cycle-gated-ordinary-final-selection"
    )
    assert summary.selected_item_ids == [
        "gated_ordinary_followup_source_bazi_baijue_case_collection",
        "gated_ordinary_followup_source_mingli_mijue_formula",
    ]
    assert summary.prior_selection_item_ids == [
        "gated_ordinary_source_mingzao_chunqiu_case_collection",
        "gated_ordinary_source_sizhu_yuce_yaojue_formula",
    ]
    assert summary.sensitive_risk_review_item_ids == [
        "gated_prep_sensitive_topic_boundary_001"
    ]
    assert summary.registered_entry_ids == [
        "entry_bazi_general_bazi_baijue_case_pdf",
        "entry_bazi_general_mingli_mijue_pdf",
    ]
    assert summary.candidate_ids == [
        "candidate_bazi_general_bazi_baijue_ten_god_001",
        "candidate_bazi_general_mingli_mijue_branch_interaction_001",
    ]
    assert summary.evidence_ids == [
        "bazi_general_bazi_baijue_ten_god_001",
        "bazi_general_mingli_mijue_branch_interaction_001",
    ]
    assert summary.status_counts == {"selected_for_registration": 2}
    assert summary.risk_boundary_counts == {"ordinary": 2}
    assert summary.target_rule_family_counts == {
        "branch_interaction": 1,
        "ten_god_relation": 1,
    }
    assert summary.boundary_checks == {
        "gated_ordinary_followup_items_loaded": "passed",
        "gated_prep_references_valid": "passed",
        "prior_selection_references_valid": "passed",
        "source_paths_are_relative": "passed",
        "prior_selected_paths_not_duplicated": "passed",
        "ordinary_gated_clusters_only": "passed",
        "source_library_entries_registered": "passed",
        "013_candidates_promoted": "passed",
        "012_evidence_promoted": "passed",
        "sensitive_cluster_remains_risk_review": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_gated_ordinary_followup_selection_markdown_and_docs_sync():
    summary = (
        materials_audit.build_raw_text_next_cycle_gated_ordinary_followup_selection_summary()
    )
    markdown = (
        materials_audit.render_raw_text_next_cycle_gated_ordinary_followup_selection_markdown(
            summary
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Gated Ordinary Followup Selection",
        "`gated-ordinary-followup-selection-status=gated_ordinary_followup_selection_completed`",
        "`gated-ordinary-followup-selection-items=2`",
        "`selected-for-registration=2`",
        "`registered-source-entries=2`",
        "`candidate-extracts=2`",
        "`formal-evidence=2`",
        "`source-library-mutation-authorized=true`",
        "`downstream-mutation-authorized=true`",
        "`next-material-entry=015-raw-text-next-cycle-gated-ordinary-final-selection`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_gated_ordinary_final_selection_items_load_selected_records():
    items = (
        materials_audit.load_raw_text_next_cycle_gated_ordinary_final_selection_items()
    )
    items_by_id = {item.selection_id: item for item in items}

    assert len(items) == 2
    assert set(items_by_id) == {
        "gated_ordinary_final_source_choujin_bosi_case_collection",
        "gated_ordinary_final_source_bazi_shizhan_mifa_formula",
    }
    assert {item.prep_id for item in items} == {
        "gated_prep_case_collection_boundary_001",
        "gated_prep_practical_formula_boundary_001",
    }
    assert {item.prior_selection_id for item in items} == {
        "gated_ordinary_followup_source_bazi_baijue_case_collection",
        "gated_ordinary_followup_source_mingli_mijue_formula",
    }
    assert {item.cluster_id for item in items} == {
        "bazi_general_case_collection_cluster",
        "bazi_general_practical_formula_cluster",
    }
    assert all(item.selection_status == "selected_for_registration" for item in items)
    assert all(item.risk_boundary == "ordinary" for item in items)
    assert all(item.source_library_mutation_authorized for item in items)
    assert all(item.downstream_mutation_authorized for item in items)
    assert items_by_id[
        "gated_ordinary_final_source_choujin_bosi_case_collection"
    ].relative_paths == ["八字18本/抽筋剥丝讲八字  274P.pdf"]
    assert items_by_id[
        "gated_ordinary_final_source_bazi_shizhan_mifa_formula"
    ].relative_paths == ["八字实战秘法公开.pdf"]
    prior_paths = {
        path
        for item in [
            *materials_audit.load_raw_text_next_cycle_gated_ordinary_source_selection_items(),
            *materials_audit.load_raw_text_next_cycle_gated_ordinary_followup_selection_items(),
        ]
        for path in item.relative_paths
    }
    assert all(
        path not in prior_paths for item in items for path in item.relative_paths
    )


def test_raw_text_next_cycle_gated_ordinary_final_selection_summary_counts_closure():
    summary = (
        materials_audit.build_raw_text_next_cycle_gated_ordinary_final_selection_summary()
    )

    assert summary.selection_id == (
        "015-raw-text-next-cycle-gated-ordinary-final-selection"
    )
    assert summary.selection_status == "gated_ordinary_final_selection_completed"
    assert summary.source_selection_item_count == 2
    assert summary.source_file_count == 2
    assert summary.priority_text_candidate_count == 2
    assert summary.selected_for_registration_count == 2
    assert summary.registered_source_entry_count == 2
    assert summary.candidate_extract_count == 2
    assert summary.formal_evidence_count == 2
    assert summary.source_library_mutation_authorized is True
    assert summary.downstream_mutation_authorized is True
    assert summary.next_material_entry == (
        "015-raw-text-next-cycle-sensitive-risk-review-prep"
    )
    assert summary.selected_item_ids == [
        "gated_ordinary_final_source_choujin_bosi_case_collection",
        "gated_ordinary_final_source_bazi_shizhan_mifa_formula",
    ]
    assert summary.prior_selection_item_ids == [
        "gated_ordinary_followup_source_bazi_baijue_case_collection",
        "gated_ordinary_followup_source_mingli_mijue_formula",
    ]
    assert summary.sensitive_risk_review_item_ids == [
        "gated_prep_sensitive_topic_boundary_001"
    ]
    assert summary.registered_entry_ids == [
        "entry_bazi_general_choujin_bosi_case_pdf",
        "entry_bazi_general_bazi_shizhan_mifa_pdf",
    ]
    assert summary.candidate_ids == [
        "candidate_bazi_general_choujin_bosi_branch_interaction_001",
        "candidate_bazi_general_bazi_shizhan_mifa_luck_cycle_001",
    ]
    assert summary.evidence_ids == [
        "bazi_general_choujin_bosi_branch_interaction_001",
        "bazi_general_bazi_shizhan_mifa_luck_cycle_001",
    ]
    assert summary.status_counts == {"selected_for_registration": 2}
    assert summary.risk_boundary_counts == {"ordinary": 2}
    assert summary.target_rule_family_counts == {
        "branch_interaction": 1,
        "luck_cycle": 1,
    }
    assert summary.boundary_checks == {
        "gated_ordinary_final_items_loaded": "passed",
        "gated_prep_references_valid": "passed",
        "prior_selection_references_valid": "passed",
        "source_paths_are_relative": "passed",
        "prior_selected_paths_not_duplicated": "passed",
        "ordinary_gated_clusters_only": "passed",
        "source_library_entries_registered": "passed",
        "013_candidates_promoted": "passed",
        "012_evidence_promoted": "passed",
        "ordinary_representative_paths_exhausted": "passed",
        "sensitive_cluster_remains_risk_review": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_gated_ordinary_final_selection_markdown_and_docs_sync():
    summary = (
        materials_audit.build_raw_text_next_cycle_gated_ordinary_final_selection_summary()
    )
    markdown = (
        materials_audit.render_raw_text_next_cycle_gated_ordinary_final_selection_markdown(
            summary
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Gated Ordinary Final Selection",
        "`gated-ordinary-final-selection-status=gated_ordinary_final_selection_completed`",
        "`gated-ordinary-final-selection-items=2`",
        "`selected-for-registration=2`",
        "`registered-source-entries=2`",
        "`candidate-extracts=2`",
        "`formal-evidence=2`",
        "`source-library-mutation-authorized=true`",
        "`downstream-mutation-authorized=true`",
        "`next-material-entry=015-raw-text-next-cycle-sensitive-risk-review-prep`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_sensitive_risk_review_prep_items_load_boundary_records():
    items = materials_audit.load_raw_text_next_cycle_sensitive_risk_review_prep_items()
    items_by_id = {item.prep_item_id: item for item in items}

    assert len(items) == 3
    assert set(items_by_id) == {
        "sensitive_risk_prep_bazi_psychology_pdf",
        "sensitive_risk_prep_erotic_fate_collection_pdf",
        "sensitive_risk_prep_bazi_comic_ppt",
    }
    assert {item.prep_id for item in items} == {
        "gated_prep_sensitive_topic_boundary_001"
    }
    assert {item.source_selection_id for item in items} == {
        "next_cycle_bazi_sensitive_topic_risk_review"
    }
    assert {item.cluster_id for item in items} == {
        "bazi_general_sensitive_topic_cluster"
    }
    assert all(item.risk_boundary == "sensitive" for item in items)
    assert all(item.file_count == 1 for item in items)
    assert all(len(item.relative_paths) == 1 for item in items)
    assert all(
        path and not Path(path).is_absolute() and ".." not in Path(path).parts
        for item in items
        for path in item.relative_paths
    )
    assert all(not item.source_library_mutation_authorized for item in items)
    assert all(not item.downstream_mutation_authorized for item in items)
    assert {
        item.prep_status: item.recommended_next_action for item in items
    } == {
        "prepared_for_source_level_risk_review": "risk_review",
        "blocked_after_sensitive_prep": "block",
        "deferred_after_sensitive_prep": "defer",
    }
    assert items_by_id[
        "sensitive_risk_prep_bazi_psychology_pdf"
    ].relative_paths == [
        "陆致极王明谦-《八字心理学》东方心理哲学智慧214页.pdf"
    ]
    assert items_by_id[
        "sensitive_risk_prep_erotic_fate_collection_pdf"
    ].relative_paths == ["情色命理汇总.pdf"]
    assert items_by_id["sensitive_risk_prep_bazi_comic_ppt"].relative_paths == [
        "八字命理漫画.ppt"
    ]


def test_raw_text_next_cycle_sensitive_risk_review_prep_summary_counts_closure():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_risk_review_prep_summary()
    )

    assert summary.selection_id == "015-raw-text-next-cycle-sensitive-risk-review-prep"
    assert summary.selection_status == "sensitive_risk_review_prep_completed"
    assert summary.prep_item_count == 3
    assert summary.source_file_count == 3
    assert summary.priority_text_candidate_count == 3
    assert summary.source_level_risk_review_count == 1
    assert summary.blocked_count == 1
    assert summary.deferred_count == 1
    assert summary.registered_source_entry_count == 0
    assert summary.candidate_extract_count == 0
    assert summary.formal_evidence_count == 0
    assert summary.source_library_mutation_authorized is False
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "015-raw-text-next-cycle-sensitive-source-level-risk-review"
    )
    assert summary.source_level_risk_review_item_ids == [
        "sensitive_risk_prep_bazi_psychology_pdf"
    ]
    assert summary.blocked_item_ids == [
        "sensitive_risk_prep_erotic_fate_collection_pdf"
    ]
    assert summary.deferred_item_ids == ["sensitive_risk_prep_bazi_comic_ppt"]
    assert summary.status_counts == {
        "prepared_for_source_level_risk_review": 1,
        "blocked_after_sensitive_prep": 1,
        "deferred_after_sensitive_prep": 1,
    }
    assert summary.action_counts == {"risk_review": 1, "block": 1, "defer": 1}
    assert summary.risk_boundary_counts == {"sensitive": 3}
    assert summary.target_rule_family_counts == {"ten_god_relation": 3}
    assert summary.boundary_checks == {
        "sensitive_risk_review_prep_items_loaded": "passed",
        "gated_prep_reference_valid": "passed",
        "source_selection_reference_valid": "passed",
        "sensitive_cluster_only": "passed",
        "source_paths_are_relative": "passed",
        "representative_paths_covered": "passed",
        "action_routing_valid": "passed",
        "source_library_mutation_blocked": "passed",
        "downstream_mutation_blocked": "passed",
        "ordinary_final_selection_completed": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_sensitive_risk_review_prep_markdown_and_docs_sync():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_risk_review_prep_summary()
    )
    markdown = (
        materials_audit.render_raw_text_next_cycle_sensitive_risk_review_prep_markdown(
            summary
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Sensitive Risk Review Prep",
        "`sensitive-risk-review-prep-status=sensitive_risk_review_prep_completed`",
        "`sensitive-risk-review-prep-items=3`",
        "`source-level-risk-review=1`",
        "`blocked-after-sensitive-prep=1`",
        "`deferred-after-sensitive-prep=1`",
        "`registered-source-entries=0`",
        "`candidate-extracts=0`",
        "`formal-evidence=0`",
        "`source-library-mutation-authorized=false`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-next-cycle-sensitive-source-level-risk-review`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_sensitive_source_level_risk_review_items_load_review_record():
    items = (
        materials_audit.load_raw_text_next_cycle_sensitive_source_level_risk_review_items()
    )
    items_by_id = {item.review_item_id: item for item in items}

    assert len(items) == 1
    assert set(items_by_id) == {"sensitive_source_review_bazi_psychology_pdf"}
    item = items_by_id["sensitive_source_review_bazi_psychology_pdf"]
    assert item.prep_item_id == "sensitive_risk_prep_bazi_psychology_pdf"
    assert item.prep_id == "gated_prep_sensitive_topic_boundary_001"
    assert item.source_selection_id == "next_cycle_bazi_sensitive_topic_risk_review"
    assert item.cluster_id == "bazi_general_sensitive_topic_cluster"
    assert item.review_status == "cleared_for_sensitive_registration_prep"
    assert item.risk_boundary == "sensitive"
    assert item.recommended_next_action == "register_source"
    assert item.registration_prep_allowed is True
    assert item.source_library_mutation_authorized is False
    assert item.downstream_mutation_authorized is False
    assert item.relative_paths == [
        "陆致极王明谦-《八字心理学》东方心理哲学智慧214页.pdf"
    ]
    assert item.file_count == 1
    assert item.priority_text_candidate_count == 1
    assert item.target_rule_families == ["ten_god_relation"]
    assert "sensitive_risk_prep_erotic_fate_collection_pdf" not in {
        review.prep_item_id for review in items
    }
    assert "sensitive_risk_prep_bazi_comic_ppt" not in {
        review.prep_item_id for review in items
    }


def test_raw_text_next_cycle_sensitive_source_level_risk_review_summary_counts_closure():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_source_level_risk_review_summary()
    )

    assert summary.selection_id == (
        "015-raw-text-next-cycle-sensitive-source-level-risk-review"
    )
    assert summary.selection_status == "sensitive_source_level_risk_review_completed"
    assert summary.review_item_count == 1
    assert summary.source_file_count == 1
    assert summary.priority_text_candidate_count == 1
    assert summary.cleared_for_registration_prep_count == 1
    assert summary.registered_source_entry_count == 0
    assert summary.candidate_extract_count == 0
    assert summary.formal_evidence_count == 0
    assert summary.source_library_mutation_authorized is False
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "015-raw-text-next-cycle-sensitive-registration-prep"
    )
    assert summary.review_item_ids == ["sensitive_source_review_bazi_psychology_pdf"]
    assert summary.cleared_for_registration_prep_item_ids == [
        "sensitive_source_review_bazi_psychology_pdf"
    ]
    assert summary.prep_item_ids == ["sensitive_risk_prep_bazi_psychology_pdf"]
    assert summary.blocked_prep_item_ids == [
        "sensitive_risk_prep_erotic_fate_collection_pdf"
    ]
    assert summary.deferred_prep_item_ids == ["sensitive_risk_prep_bazi_comic_ppt"]
    assert summary.status_counts == {"cleared_for_sensitive_registration_prep": 1}
    assert summary.action_counts == {"register_source": 1}
    assert summary.risk_boundary_counts == {"sensitive": 1}
    assert summary.target_rule_family_counts == {"ten_god_relation": 1}
    assert summary.boundary_checks == {
        "sensitive_source_level_risk_review_items_loaded": "passed",
        "sensitive_risk_review_prep_completed": "passed",
        "only_prepared_prep_items_reviewed": "passed",
        "blocked_and_deferred_prep_retained": "passed",
        "source_paths_are_relative": "passed",
        "action_routing_valid": "passed",
        "source_library_mutation_blocked": "passed",
        "downstream_mutation_blocked": "passed",
        "no_downstream_records_created": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_sensitive_source_level_risk_review_markdown_and_docs_sync():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_source_level_risk_review_summary()
    )
    markdown = (
        materials_audit.render_raw_text_next_cycle_sensitive_source_level_risk_review_markdown(
            summary
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Sensitive Source-Level Risk Review",
        "`sensitive-source-level-risk-review-status=sensitive_source_level_risk_review_completed`",
        "`sensitive-source-level-risk-review-items=1`",
        "`cleared-for-registration-prep=1`",
        "`registered-source-entries=0`",
        "`candidate-extracts=0`",
        "`formal-evidence=0`",
        "`source-library-mutation-authorized=false`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-next-cycle-sensitive-registration-prep`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_sensitive_registration_prep_items_load_prep_record():
    items = materials_audit.load_raw_text_next_cycle_sensitive_registration_prep_items()
    items_by_id = {item.prep_item_id: item for item in items}

    assert len(items) == 1
    assert set(items_by_id) == {"sensitive_registration_prep_bazi_psychology_pdf"}
    item = items_by_id["sensitive_registration_prep_bazi_psychology_pdf"]
    assert item.source_level_review_id == "sensitive_source_review_bazi_psychology_pdf"
    assert item.prep_review_item_id == "sensitive_risk_prep_bazi_psychology_pdf"
    assert item.registration_status == "ready_for_sensitive_source_registration"
    assert item.proposed_entry_id == "entry_bazi_general_bazi_psychology_pdf"
    assert item.proposed_material_id == "material_bazi_general_bazi_psychology_pdf"
    assert item.proposed_title == "Bazi Psychology Lu Wang Source"
    assert item.proposed_material_type == "pdf"
    assert item.proposed_local_references == [
        "陆致极王明谦-《八字心理学》东方心理哲学智慧214页.pdf"
    ]
    assert item.proposed_tracking_status == "external_untracked"
    assert item.proposed_readiness_status == "needs_preparation"
    assert item.proposed_priority_level == "high"
    assert item.proposed_next_action == "prepare_material"
    assert item.risk_tier == "sensitive"
    assert item.source_library_mutation_authorized is False
    assert item.downstream_mutation_authorized is False
    assert item.rule_families == ["ten_god_relation"]
    assert item.source_library_overlap_policy == (
        "new_entry_allowed_after_user_approval"
    )


def test_raw_text_next_cycle_sensitive_registration_prep_summary_counts_closure():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_registration_prep_summary()
    )

    assert summary.prep_id == "015-raw-text-next-cycle-sensitive-registration-prep"
    assert summary.prep_status == "sensitive_registration_prep_completed"
    assert summary.registration_prep_item_count == 1
    assert summary.proposed_source_file_count == 1
    assert summary.registered_source_entry_count == 1
    assert summary.candidate_extract_count == 0
    assert summary.formal_evidence_count == 0
    assert summary.proposed_entry_ids == ["entry_bazi_general_bazi_psychology_pdf"]
    assert summary.proposed_material_ids == [
        "material_bazi_general_bazi_psychology_pdf"
    ]
    assert summary.registration_prep_item_ids == [
        "sensitive_registration_prep_bazi_psychology_pdf"
    ]
    assert summary.source_level_review_item_ids == [
        "sensitive_source_review_bazi_psychology_pdf"
    ]
    assert summary.blocked_prep_item_ids == [
        "sensitive_risk_prep_erotic_fate_collection_pdf"
    ]
    assert summary.deferred_prep_item_ids == ["sensitive_risk_prep_bazi_comic_ppt"]
    assert summary.registration_status_counts == {
        "ready_for_sensitive_source_registration": 1
    }
    assert summary.proposed_readiness_counts == {"needs_preparation": 1}
    assert summary.proposed_next_action_counts == {"prepare_material": 1}
    assert summary.risk_tier_counts == {"sensitive": 1}
    assert summary.target_rule_family_counts == {"ten_god_relation": 1}
    assert summary.source_library_mutation_authorized is False
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "015-raw-text-next-cycle-sensitive-source-registration"
    )
    assert summary.boundary_checks == {
        "sensitive_registration_prep_items_loaded": "passed",
        "source_level_risk_review_completed": "passed",
        "source_level_review_references_valid": "passed",
        "proposed_entries_available": "passed",
        "blocked_and_deferred_prep_retained": "passed",
        "source_paths_are_relative": "passed",
        "source_library_mutation_blocked": "passed",
        "downstream_mutation_blocked": "passed",
        "no_downstream_records_created": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_sensitive_registration_prep_markdown_and_docs_sync():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_registration_prep_summary()
    )
    markdown = materials_audit.render_raw_text_next_cycle_sensitive_registration_prep_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Sensitive Registration Prep",
        "`sensitive-registration-prep-status=sensitive_registration_prep_completed`",
        "`sensitive-registration-prep-items=1`",
        "`proposed-source-files=1`",
        "`registered-source-entries=1`",
        "`candidate-extracts=0`",
        "`formal-evidence=0`",
        "`source-library-mutation-authorized=false`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-next-cycle-sensitive-source-registration`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_sensitive_source_registration_items_load_registered_record():
    items = materials_audit.load_raw_text_next_cycle_sensitive_source_registration_items()
    items_by_id = {item.registration_item_id: item for item in items}

    assert len(items) == 1
    assert set(items_by_id) == {"sensitive_source_registration_bazi_psychology_pdf"}
    item = items_by_id["sensitive_source_registration_bazi_psychology_pdf"]
    assert item.registration_prep_item_id == (
        "sensitive_registration_prep_bazi_psychology_pdf"
    )
    assert item.registered_entry_id == "entry_bazi_general_bazi_psychology_pdf"
    assert item.registered_material_id == "material_bazi_general_bazi_psychology_pdf"
    assert item.registration_status == "registered_sensitive_source_library_entry"
    assert item.registered_local_references == [
        "陆致极王明谦-《八字心理学》东方心理哲学智慧214页.pdf"
    ]
    assert item.source_library_mutation_authorized is True
    assert item.downstream_mutation_authorized is False


def test_raw_text_next_cycle_sensitive_source_registration_summary_counts_closure():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_source_registration_summary()
    )

    assert summary.registration_id == (
        "015-raw-text-next-cycle-sensitive-source-registration"
    )
    assert summary.registration_status == "sensitive_source_registration_completed"
    assert summary.registered_entry_count == 1
    assert summary.registered_source_file_count == 1
    assert summary.candidate_extract_count == 0
    assert summary.formal_evidence_count == 0
    assert summary.registered_entry_ids == ["entry_bazi_general_bazi_psychology_pdf"]
    assert summary.registered_material_ids == [
        "material_bazi_general_bazi_psychology_pdf"
    ]
    assert summary.registration_prep_item_ids == [
        "sensitive_registration_prep_bazi_psychology_pdf"
    ]
    assert summary.blocked_prep_item_ids == [
        "sensitive_risk_prep_erotic_fate_collection_pdf"
    ]
    assert summary.deferred_prep_item_ids == ["sensitive_risk_prep_bazi_comic_ppt"]
    assert summary.source_library_mutation_authorized is True
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "015-raw-text-next-cycle-sensitive-preparation-boundary"
    )
    assert summary.boundary_checks == {
        "sensitive_source_registration_items_loaded": "passed",
        "sensitive_registration_prep_completed": "passed",
        "source_library_entries_loaded": "passed",
        "registered_entries_match_prep_metadata": "passed",
        "blocked_and_deferred_prep_retained": "passed",
        "source_paths_are_relative": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_sensitive_source_registration_markdown_and_docs_sync():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_source_registration_summary()
    )
    markdown = materials_audit.render_raw_text_next_cycle_sensitive_source_registration_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Sensitive Source Registration",
        "`sensitive-source-registration-status=sensitive_source_registration_completed`",
        "`registered-source-entries=1`",
        "`registered-source-files=1`",
        "`candidate-extracts=0`",
        "`formal-evidence=0`",
        "`source-library-mutation-authorized=true`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-next-cycle-sensitive-preparation-boundary`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_sensitive_preparation_boundary_items_load_record():
    items = (
        materials_audit.load_raw_text_next_cycle_sensitive_preparation_boundary_items()
    )
    items_by_id = {item.boundary_item_id: item for item in items}

    assert len(items) == 1
    assert set(items_by_id) == {"sensitive_preparation_boundary_bazi_psychology_pdf"}
    item = items_by_id["sensitive_preparation_boundary_bazi_psychology_pdf"]
    assert item.source_registration_item_id == (
        "sensitive_source_registration_bazi_psychology_pdf"
    )
    assert item.source_library_entry_id == "entry_bazi_general_bazi_psychology_pdf"
    assert item.source_material_id == "material_bazi_general_bazi_psychology_pdf"
    assert item.boundary_status == "cleared_for_sensitive_preparation"
    assert item.risk_boundary == "sensitive"
    assert item.recommended_next_action == "prepare_material"
    assert item.local_references == [
        "陆致极王明谦-《八字心理学》东方心理哲学智慧214页.pdf"
    ]
    assert item.file_count == 1
    assert item.preparation_allowed is True
    assert item.reading_allowed is False
    assert item.downstream_mutation_authorized is False
    assert item.target_rule_families == ["ten_god_relation"]


def test_raw_text_next_cycle_sensitive_preparation_boundary_summary_counts_closure():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_preparation_boundary_summary()
    )

    assert summary.boundary_id == (
        "015-raw-text-next-cycle-sensitive-preparation-boundary"
    )
    assert summary.boundary_status == "sensitive_preparation_boundary_completed"
    assert summary.boundary_item_count == 1
    assert summary.source_file_count == 1
    assert summary.preparation_allowed_count == 1
    assert summary.reading_allowed_count == 0
    assert summary.candidate_extract_count == 0
    assert summary.formal_evidence_count == 0
    assert summary.boundary_item_ids == [
        "sensitive_preparation_boundary_bazi_psychology_pdf"
    ]
    assert summary.source_registration_item_ids == [
        "sensitive_source_registration_bazi_psychology_pdf"
    ]
    assert summary.source_entry_ids == ["entry_bazi_general_bazi_psychology_pdf"]
    assert summary.source_material_ids == [
        "material_bazi_general_bazi_psychology_pdf"
    ]
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "015-raw-text-next-cycle-sensitive-preparation-reading"
    )
    assert summary.boundary_checks == {
        "sensitive_preparation_boundary_items_loaded": "passed",
        "source_registration_completed": "passed",
        "registered_source_references_valid": "passed",
        "source_library_entry_ready_for_preparation": "passed",
        "source_paths_are_relative": "passed",
        "action_routing_valid": "passed",
        "downstream_mutation_blocked": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_sensitive_preparation_boundary_markdown_and_docs_sync():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_preparation_boundary_summary()
    )
    markdown = materials_audit.render_raw_text_next_cycle_sensitive_preparation_boundary_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Sensitive Preparation Boundary",
        "`sensitive-preparation-boundary-status=sensitive_preparation_boundary_completed`",
        "`sensitive-preparation-boundary-items=1`",
        "`preparation-allowed=1`",
        "`reading-allowed=0`",
        "`candidate-extracts=0`",
        "`formal-evidence=0`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-next-cycle-sensitive-preparation-reading`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_next_cycle_sensitive_preparation_reading_items_load_record():
    items = materials_audit.load_raw_text_next_cycle_sensitive_preparation_reading_items()
    items_by_id = {item.reading_item_id: item for item in items}

    assert len(items) == 1
    assert set(items_by_id) == {"sensitive_preparation_reading_bazi_psychology_pdf"}
    item = items_by_id["sensitive_preparation_reading_bazi_psychology_pdf"]
    assert item.boundary_item_id == "sensitive_preparation_boundary_bazi_psychology_pdf"
    assert item.source_library_entry_id == "entry_bazi_general_bazi_psychology_pdf"
    assert item.source_material_id == "material_bazi_general_bazi_psychology_pdf"
    assert item.reading_status == "sensitive_preparation_reading_completed"
    assert item.risk_boundary == "sensitive"
    assert item.local_references == [
        "陆致极王明谦-《八字心理学》东方心理哲学智慧214页.pdf"
    ]
    assert item.safe_reading_note_count == 3
    assert item.candidate_intake_ready is False
    assert item.formal_evidence_ready is False
    assert item.downstream_mutation_authorized is False
    assert item.target_rule_families == ["ten_god_relation"]


def test_raw_text_next_cycle_sensitive_preparation_reading_summary_counts_closure():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_preparation_reading_summary()
    )

    assert summary.reading_id == "015-raw-text-next-cycle-sensitive-preparation-reading"
    assert summary.reading_status == "sensitive_preparation_reading_completed"
    assert summary.reading_item_count == 1
    assert summary.source_file_count == 1
    assert summary.safe_reading_note_count == 3
    assert summary.candidate_intake_ready_count == 0
    assert summary.formal_evidence_ready_count == 0
    assert summary.candidate_extract_count == 0
    assert summary.review_decision_count == 0
    assert summary.promotion_batch_count == 0
    assert summary.formal_evidence_count == 0
    assert summary.reading_item_ids == [
        "sensitive_preparation_reading_bazi_psychology_pdf"
    ]
    assert summary.boundary_item_ids == [
        "sensitive_preparation_boundary_bazi_psychology_pdf"
    ]
    assert summary.source_entry_ids == ["entry_bazi_general_bazi_psychology_pdf"]
    assert summary.source_material_ids == [
        "material_bazi_general_bazi_psychology_pdf"
    ]
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "013-explicit-candidate-review-or-015-queue-refresh"
    )
    assert summary.boundary_checks == {
        "sensitive_preparation_reading_items_loaded": "passed",
        "preparation_boundary_completed": "passed",
        "boundary_references_valid": "passed",
        "source_library_entry_still_preparation_gated": "passed",
        "safe_reading_notes_present": "passed",
        "source_paths_are_relative": "passed",
        "downstream_mutation_blocked": "passed",
        "013_candidate_intake_blocked": "passed",
        "012_formal_evidence_blocked": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_raw_text_next_cycle_sensitive_preparation_reading_markdown_and_docs_sync():
    summary = (
        materials_audit.build_raw_text_next_cycle_sensitive_preparation_reading_summary()
    )
    markdown = materials_audit.render_raw_text_next_cycle_sensitive_preparation_reading_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Raw Text Next Cycle Sensitive Preparation Reading",
        "`sensitive-preparation-reading-status=sensitive_preparation_reading_completed`",
        "`sensitive-preparation-reading-items=1`",
        "`safe-reading-notes=3`",
        "`candidate-intake-ready=0`",
        "`formal-evidence-ready=0`",
        "`candidate-extracts=0`",
        "`formal-evidence=0`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=013-explicit-candidate-review-or-015-queue-refresh`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_explicit_candidate_review_or_queue_refresh_items_load_routing_record():
    items = materials_audit.load_explicit_candidate_review_or_queue_refresh_items()
    items_by_id = {item.routing_item_id: item for item in items}

    assert len(items) == 1
    assert set(items_by_id) == {"explicit_candidate_review_or_queue_refresh_001"}
    item = items_by_id["explicit_candidate_review_or_queue_refresh_001"]
    assert item.routing_entry_id == "013-explicit-candidate-review-or-015-queue-refresh"
    assert item.sensitive_reading_item_id == (
        "sensitive_preparation_reading_bazi_psychology_pdf"
    )
    assert item.authorization_audit_id == (
        "017-candidate-formal-evidence-authorization-audit"
    )
    assert item.queue_refresh_id == "015-materials-audit-next-action-queue-refresh"
    assert item.routing_status == "routed_to_015_queue_refresh"
    assert item.authorization_status == "ready_for_explicit_downstream_authorization"
    assert item.queue_refresh_status == "covered_or_completed_queue_exhausted"
    assert item.selected_next_material_entry == "015-external-material-inventory-refresh"
    assert item.downstream_mutation_authorized is False


def test_explicit_candidate_review_or_queue_refresh_summary_routes_to_inventory_refresh():
    summary = materials_audit.build_explicit_candidate_review_or_queue_refresh_summary()

    assert summary.routing_id == "013-explicit-candidate-review-or-015-queue-refresh"
    assert summary.routing_status == "routed_to_015_queue_refresh"
    assert summary.routing_item_count == 1
    assert summary.authorization_status == "ready_for_explicit_downstream_authorization"
    assert summary.queue_refresh_status == "covered_or_completed_queue_exhausted"
    assert summary.selected_next_material_entry == "015-external-material-inventory-refresh"
    assert summary.candidate_extract_delta_count == 0
    assert summary.review_decision_delta_count == 0
    assert summary.promotion_batch_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-external-material-inventory-refresh"
    assert summary.boundary_checks == {
        "routing_items_loaded": "passed",
        "sensitive_preparation_reading_completed": "passed",
        "authorization_audit_ready": "passed",
        "downstream_mutation_not_authorized": "passed",
        "queue_refresh_completed": "passed",
        "queue_refresh_route_selected": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_explicit_candidate_review_or_queue_refresh_markdown_and_docs_sync():
    summary = materials_audit.build_explicit_candidate_review_or_queue_refresh_summary()
    markdown = materials_audit.render_explicit_candidate_review_or_queue_refresh_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "013 Explicit Candidate Review Or 015 Queue Refresh",
        "`explicit-routing-status=routed_to_015_queue_refresh`",
        "`authorization-status=ready_for_explicit_downstream_authorization`",
        "`queue-refresh-status=covered_or_completed_queue_exhausted`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-external-material-inventory-refresh`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_external_material_inventory_refresh_confirmation_items_load_record():
    items = materials_audit.load_external_material_inventory_refresh_confirmation_items()
    items_by_id = {item.confirmation_item_id: item for item in items}

    assert len(items) == 1
    assert set(items_by_id) == {"external_inventory_refresh_confirmation_001"}
    item = items_by_id["external_inventory_refresh_confirmation_001"]
    assert item.refresh_id == "015-external-material-inventory-refresh"
    assert item.routing_id == "013-explicit-candidate-review-or-015-queue-refresh"
    assert item.confirmation_status == "external_inventory_refresh_confirmed"
    assert item.external_inventory_status == "scoped_metadata_registered"
    assert item.untracked_material_entry_count == 0
    assert item.selected_next_material_entry == "015-raw-text-next-cycle-source-selection"
    assert item.downstream_mutation_authorized is False


def test_external_material_inventory_refresh_confirmation_summary_routes_to_source_selection():
    summary = (
        materials_audit
        .build_external_material_inventory_refresh_confirmation_summary()
    )

    assert summary.confirmation_id == "015-external-material-inventory-refresh"
    assert summary.confirmation_status == "external_inventory_refresh_confirmed"
    assert summary.confirmation_item_count == 1
    assert summary.external_inventory_status == "scoped_metadata_registered"
    assert summary.scanned_entry_count == 31
    assert summary.untracked_material_entry_count == 0
    assert summary.candidate_extract_delta_count == 0
    assert summary.review_decision_delta_count == 0
    assert summary.promotion_batch_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-raw-text-next-cycle-source-selection"
    assert summary.boundary_checks == {
        "confirmation_items_loaded": "passed",
        "explicit_routing_completed": "passed",
        "external_inventory_refresh_completed": "passed",
        "no_untracked_material_entries": "passed",
        "next_cycle_source_selection_selected": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_external_material_inventory_refresh_confirmation_markdown_and_docs_sync():
    summary = (
        materials_audit
        .build_external_material_inventory_refresh_confirmation_summary()
    )
    markdown = (
        materials_audit
        .render_external_material_inventory_refresh_confirmation_markdown(summary)
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 External Material Inventory Refresh Confirmation",
        "`external-inventory-confirmation-status=external_inventory_refresh_confirmed`",
        "`external-inventory-status=scoped_metadata_registered`",
        "`untracked-material-entries=0`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-raw-text-next-cycle-source-selection`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_new_material_extraction_learning_loop_closure_items_load_record():
    items = materials_audit.load_new_material_extraction_learning_loop_closure_items()
    items_by_id = {item.closure_item_id: item for item in items}

    assert len(items) == 1
    assert set(items_by_id) == {"new_material_loop_closure_001"}
    item = items_by_id["new_material_loop_closure_001"]
    assert item.closure_id == "017-new-material-extraction-learning-loop-closure"
    assert item.source_selection_id == "015-raw-text-next-cycle-source-selection"
    assert (
        item.sensitive_reading_id
        == "015-raw-text-next-cycle-sensitive-preparation-reading"
    )
    assert item.authorization_audit_id == (
        "017-candidate-formal-evidence-authorization-audit"
    )
    assert item.routing_id == "013-explicit-candidate-review-or-015-queue-refresh"
    assert item.inventory_confirmation_id == "015-external-material-inventory-refresh"
    assert item.closure_status == "new_material_learning_loop_closed"
    assert (
        item.selected_next_material_entry
        == "013-explicit-candidate-review-or-new-material-intake"
    )
    assert item.completed_stage_count == 16
    assert item.source_selection_item_count == 5
    assert item.registered_source_entry_count == 11
    assert item.preparation_reading_item_count == 1
    assert item.candidate_intake_ready_count == 0
    assert item.candidate_extract_delta_count == 0
    assert item.formal_evidence_delta_count == 0
    assert item.downstream_mutation_authorized is False


def test_new_material_extraction_learning_loop_closure_summary_closes_loop():
    summary = materials_audit.build_new_material_extraction_learning_loop_closure_summary()

    assert summary.closure_id == "017-new-material-extraction-learning-loop-closure"
    assert summary.closure_status == "new_material_learning_loop_closed"
    assert summary.closure_item_count == 1
    assert summary.completed_stage_count == 16
    assert summary.source_selection_item_count == 5
    assert summary.registered_source_entry_count == 11
    assert summary.preparation_reading_item_count == 1
    assert summary.candidate_intake_ready_count == 0
    assert summary.formal_evidence_ready_count == 0
    assert summary.candidate_extract_delta_count == 0
    assert summary.review_decision_delta_count == 0
    assert summary.promotion_batch_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.authorization_status == (
        "ready_for_explicit_downstream_authorization"
    )
    assert summary.downstream_mutation_authorized is False
    assert (
        summary.next_material_entry
        == "013-explicit-candidate-review-or-new-material-intake"
    )
    assert summary.boundary_checks == {
        "closure_items_loaded": "passed",
        "source_selection_completed": "passed",
        "raw_text_next_cycle_completed": "passed",
        "sensitive_preparation_reading_completed": "passed",
        "017_authorization_audit_ready": "passed",
        "explicit_routing_completed": "passed",
        "external_inventory_refresh_confirmed": "passed",
        "no_untracked_material_entries": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_extraction_learning_loop_closure_markdown_and_docs_sync():
    summary = materials_audit.build_new_material_extraction_learning_loop_closure_summary()
    markdown = (
        materials_audit
        .render_new_material_extraction_learning_loop_closure_markdown(summary)
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "017 New Material Extraction Learning Loop Closure",
        "`new-material-learning-loop-status=new_material_learning_loop_closed`",
        "`completed-loop-stages=16`",
        "`registered-source-entries=11`",
        "`preparation-reading-items=1`",
        "`candidate-intake-ready=0`",
        "`formal-evidence-ready=0`",
        "`authorization-status=ready_for_explicit_downstream_authorization`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=013-explicit-candidate-review-or-new-material-intake`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff

    assert (
        "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`"
        in handoff
    )
    assert (
        "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`"
        in quickstart
    )


def test_new_material_intake_items_select_xiahai_suanmingji():
    items = materials_audit.load_new_material_intake_items()
    items_by_id = {item.intake_item_id: item for item in items}

    assert len(items) == 2
    assert set(items_by_id) == {
        "new_material_intake_xiahai_suanmingji_pdf",
        "new_material_intake_bazi_suanming_cangjue_pdf",
    }
    item = items_by_id["new_material_intake_xiahai_suanmingji_pdf"]
    assert item.intake_id == "015-new-material-intake"
    assert item.authorization_id == "013-012-explicit-downstream-authorization"
    assert item.cluster_id == "bazi_general_misc_identity_review_cluster"
    assert item.source_selection_id == "next_cycle_bazi_misc_identity_review"
    assert item.intake_status == "selected_for_source_identity_review"
    assert item.risk_boundary == "ordinary"
    assert item.recommended_next_action == "clarify_identity"
    assert item.relative_paths == ["下海算命记.pdf"]
    assert item.file_count == 1
    assert item.priority_text_candidate_count == 1
    assert item.target_rule_families == ["branch_interaction"]
    assert item.source_library_mutation_authorized is False
    assert item.downstream_mutation_authorized is False
    assert item.selected_next_material_entry == (
        "015-new-material-source-identity-review"
    )

    cangjue = items_by_id["new_material_intake_bazi_suanming_cangjue_pdf"]
    assert cangjue.intake_id == "015-new-material-intake"
    assert cangjue.authorization_id == "013-012-explicit-downstream-authorization"
    assert cangjue.cluster_id == "bazi_general_misc_identity_review_cluster"
    assert cangjue.source_selection_id == "next_cycle_bazi_misc_identity_review"
    assert cangjue.intake_status == "selected_for_source_identity_review"
    assert cangjue.risk_boundary == "ordinary"
    assert cangjue.recommended_next_action == "clarify_identity"
    assert cangjue.relative_paths == ["八字算命藏诀-黑白.pdf"]
    assert cangjue.file_count == 1
    assert cangjue.priority_text_candidate_count == 1
    assert cangjue.target_rule_families == ["branch_interaction"]
    assert cangjue.source_library_mutation_authorized is False
    assert cangjue.downstream_mutation_authorized is False
    assert cangjue.selected_next_material_entry == (
        "015-new-material-source-identity-review"
    )


def test_new_material_intake_summary_routes_to_source_identity_review():
    summary = materials_audit.build_new_material_intake_summary()

    assert summary.intake_id == "015-new-material-intake"
    assert summary.intake_status == "new_material_intake_selected"
    assert summary.intake_item_count == 2
    assert summary.source_file_count == 2
    assert summary.priority_text_candidate_count == 2
    assert summary.selected_for_identity_review_count == 2
    assert summary.authorization_status == "downstream_authorization_consumed"
    assert summary.candidate_extract_delta_count == 0
    assert summary.review_decision_delta_count == 0
    assert summary.promotion_batch_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.source_library_mutation_authorized is False
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-new-material-source-identity-review"
    assert summary.selected_item_ids == [
        "new_material_intake_xiahai_suanmingji_pdf",
        "new_material_intake_bazi_suanming_cangjue_pdf",
    ]
    assert summary.cluster_ids == [
        "bazi_general_misc_identity_review_cluster",
        "bazi_general_misc_identity_review_cluster",
    ]
    assert summary.relative_paths == [
        "下海算命记.pdf",
        "八字算命藏诀-黑白.pdf",
    ]
    assert summary.boundary_checks == {
        "intake_items_loaded": "passed",
        "downstream_authorization_consumed": "passed",
        "selected_cluster_requires_identity_review": "passed",
        "selected_paths_are_cluster_representatives": "passed",
        "selected_paths_are_relative": "passed",
        "single_file_boundary": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_intake_markdown_and_docs_sync():
    summary = materials_audit.build_new_material_intake_summary()
    markdown = materials_audit.render_new_material_intake_markdown(summary)
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material Intake",
        "`new-material-intake-status=new_material_intake_selected`",
        "`intake-items=2`",
        "`selected-source-files=2`",
        "`selected-for-identity-review=2`",
        "`authorization-status=downstream_authorization_consumed`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        "`source-library-mutation-authorized=false`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-new-material-source-identity-review`",
        "`new_material_intake_xiahai_suanmingji_pdf`",
        "`new_material_intake_bazi_suanming_cangjue_pdf`",
        "`bazi_general_misc_identity_review_cluster`",
        "`下海算命记.pdf`",
        "`八字算命藏诀-黑白.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff

    assert "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`" in handoff
    assert "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`" in quickstart


def test_new_material_source_identity_review_item_prepares_registration():
    items = materials_audit.load_new_material_source_identity_review_items()
    items_by_id = {item.review_item_id: item for item in items}

    assert len(items) == 1
    assert set(items_by_id) == {"new_material_identity_xiahai_suanmingji_pdf"}
    item = items_by_id["new_material_identity_xiahai_suanmingji_pdf"]
    assert item.review_id == "015-new-material-source-identity-review"
    assert item.intake_item_id == "new_material_intake_xiahai_suanmingji_pdf"
    assert item.cluster_id == "bazi_general_misc_identity_review_cluster"
    assert item.source_selection_id == "next_cycle_bazi_misc_identity_review"
    assert item.identity_status == "identity_review_completed"
    assert item.source_library_overlap_status == "no_registered_overlap_found"
    assert item.registration_readiness == "ready_for_registration_prep"
    assert item.recommended_next_action == "register_source"
    assert item.risk_boundary == "ordinary"
    assert item.relative_paths == ["下海算命记.pdf"]
    assert item.file_count == 1
    assert item.priority_text_candidate_count == 1
    assert item.target_rule_families == ["branch_interaction"]
    assert item.matched_source_library_entry_ids == []
    assert item.source_library_mutation_authorized is False
    assert item.downstream_mutation_authorized is False
    assert item.selected_next_material_entry == "015-new-material-registration-prep"


def test_new_material_source_identity_review_summary_routes_to_registration_prep():
    summary = materials_audit.build_new_material_source_identity_review_summary()

    assert summary.review_id == "015-new-material-source-identity-review"
    assert summary.review_status == "identity_review_completed"
    assert summary.review_item_count == 1
    assert summary.identity_completed_count == 1
    assert summary.registration_prep_ready_count == 1
    assert summary.source_library_overlap_found_count == 0
    assert summary.source_file_count == 1
    assert summary.priority_text_candidate_count == 1
    assert summary.candidate_extract_delta_count == 0
    assert summary.review_decision_delta_count == 0
    assert summary.promotion_batch_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.source_library_mutation_authorized is False
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-new-material-registration-prep"
    assert summary.review_item_ids == ["new_material_identity_xiahai_suanmingji_pdf"]
    assert summary.intake_item_ids == ["new_material_intake_xiahai_suanmingji_pdf"]
    assert summary.cluster_ids == ["bazi_general_misc_identity_review_cluster"]
    assert summary.relative_paths == ["下海算命记.pdf"]
    assert summary.boundary_checks == {
        "identity_review_items_loaded": "passed",
        "intake_references_valid": "passed",
        "intake_paths_match": "passed",
        "selected_paths_are_relative": "passed",
        "single_file_boundary": "passed",
        "source_library_overlap_references_valid": "passed",
        "no_registered_source_library_overlap": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_source_identity_review_markdown_and_docs_sync():
    summary = materials_audit.build_new_material_source_identity_review_summary()
    markdown = materials_audit.render_new_material_source_identity_review_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material Source Identity Review",
        "`new-material-source-identity-review-status=identity_review_completed`",
        "`identity-review-items=1`",
        "`identity-completed=1`",
        "`registration-prep-ready=1`",
        "`source-library-overlap-found=0`",
        "`reviewed-source-files=1`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        "`source-library-mutation-authorized=false`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-new-material-registration-prep`",
        "`new_material_identity_xiahai_suanmingji_pdf`",
        "`new_material_intake_xiahai_suanmingji_pdf`",
        "`Xiahai Suanmingji`",
        "`下海算命记.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff

    assert "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`" in handoff
    assert "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`" in quickstart


def test_new_material_registration_prep_registers_xiahai_metadata():
    prep_items = materials_audit.load_new_material_registration_prep_items()
    prep_summary = materials_audit.build_new_material_registration_prep_summary()

    assert len(prep_items) == 1
    item = prep_items[0]
    assert item.prep_id == "015-new-material-registration-prep"
    assert item.identity_review_item_id == "new_material_identity_xiahai_suanmingji_pdf"
    assert item.source_library_entry_id == "entry_new_material_xiahai_suanmingji_pdf"
    assert item.source_material_id == "material_new_material_xiahai_suanmingji_pdf"
    assert item.registration_status == "ready_for_source_registration"
    assert item.proposed_local_reference == "下海算命记.pdf"
    assert item.source_library_mutation_authorized is True
    assert item.downstream_mutation_authorized is False
    assert item.selected_next_material_entry == "015-new-material-source-registration"
    assert prep_summary.prep_status == "registration_prep_completed"
    assert prep_summary.registered_source_entry_count == 1
    assert prep_summary.next_material_entry == "015-new-material-source-registration"
    assert prep_summary.boundary_checks == {
        "registration_prep_items_loaded": "passed",
        "source_library_entry_registered": "passed",
        "registered_entries_match_prep": "passed",
        "source_library_mutation_authorized": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_source_registration_and_boundary_block_reading():
    registration_summary = materials_audit.build_new_material_source_registration_summary()
    boundary_summary = materials_audit.build_new_material_preparation_boundary_summary()

    assert registration_summary.registration_status == "source_registration_completed"
    assert registration_summary.registered_entry_ids == [
        "entry_new_material_xiahai_suanmingji_pdf"
    ]
    assert registration_summary.registered_material_ids == [
        "material_new_material_xiahai_suanmingji_pdf"
    ]
    assert registration_summary.local_references == ["下海算命记.pdf"]
    assert registration_summary.candidate_extract_delta_count == 0
    assert registration_summary.formal_evidence_delta_count == 0
    assert registration_summary.source_library_mutation_authorized is True
    assert registration_summary.downstream_mutation_authorized is False
    assert registration_summary.next_material_entry == (
        "015-new-material-preparation-boundary"
    )

    assert boundary_summary.boundary_status == "preparation_boundary_completed"
    assert boundary_summary.text_preparation_required_count == 1
    assert boundary_summary.blocked_reading_count == 1
    assert boundary_summary.source_entry_ids == [
        "entry_new_material_xiahai_suanmingji_pdf"
    ]
    assert boundary_summary.candidate_extract_delta_count == 0
    assert boundary_summary.formal_evidence_delta_count == 0
    assert boundary_summary.source_library_mutation_authorized is False
    assert boundary_summary.downstream_mutation_authorized is False
    assert boundary_summary.next_material_entry == (
        "015-new-material-controlled-text-preparation"
    )


def test_new_material_long_goal_markdown_and_docs_sync():
    prep_summary = materials_audit.build_new_material_registration_prep_summary()
    registration_summary = materials_audit.build_new_material_source_registration_summary()
    boundary_summary = materials_audit.build_new_material_preparation_boundary_summary()
    markdown = "\n".join(
        (
            materials_audit.render_new_material_registration_prep_markdown(
                prep_summary
            ),
            materials_audit.render_new_material_source_registration_markdown(
                registration_summary
            ),
            materials_audit.render_new_material_preparation_boundary_markdown(
                boundary_summary
            ),
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material Registration Prep",
        "`new-material-registration-prep-status=registration_prep_completed`",
        "015 New Material Source Registration",
        "`new-material-source-registration-status=source_registration_completed`",
        "015 New Material Preparation Boundary",
        "`new-material-preparation-boundary-status=preparation_boundary_completed`",
        "`text-preparation-required=1`",
        "`reading-blocked=1`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        "`entry_new_material_xiahai_suanmingji_pdf`",
        "`下海算命记.pdf`",
        "`next-material-entry=015-new-material-controlled-text-preparation`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff

    assert (
        "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`"
        in handoff
    )
    assert (
        "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`"
        in quickstart
    )


def test_new_material_controlled_text_preparation_blocks_on_unusable_text_layer():
    items = materials_audit.load_new_material_controlled_text_preparation_items()
    summary = materials_audit.build_new_material_controlled_text_preparation_summary()

    assert len(items) == 1
    item = items[0]
    assert item.preparation_id == "015-new-material-controlled-text-preparation"
    assert item.boundary_item_id == (
        "new_material_preparation_boundary_xiahai_suanmingji_pdf"
    )
    assert item.preparation_status == "blocked_requires_ocr_or_manual_transcription"
    assert item.probe_method == "pdfplumber_text_layer_probe"
    assert item.local_reference == "下海算命记.pdf"
    assert item.page_count == 84
    assert item.text_layer_nonempty_page_count == 13
    assert item.extracted_text_char_count == 592
    assert item.usable_text_layer is False
    assert item.selected_next_material_entry == (
        "015-new-material-ocr-or-manual-transcription"
    )
    assert item.candidate_extract_delta_count == 0
    assert item.formal_evidence_delta_count == 0

    assert summary.preparation_status == (
        "blocked_requires_ocr_or_manual_transcription"
    )
    assert summary.preparation_item_count == 1
    assert summary.page_count == 84
    assert summary.text_layer_nonempty_page_count == 13
    assert summary.extracted_text_char_count == 592
    assert summary.usable_text_layer_count == 0
    assert summary.blocked_item_count == 1
    assert summary.candidate_extract_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.next_material_entry == (
        "015-new-material-ocr-or-manual-transcription"
    )
    assert summary.boundary_checks == {
        "controlled_text_preparation_items_loaded": "passed",
        "preparation_boundary_completed": "passed",
        "text_layer_probe_completed": "passed",
        "usable_text_layer_absent": "passed",
        "ocr_or_manual_transcription_required": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_controlled_text_preparation_markdown_and_docs_sync():
    summary = materials_audit.build_new_material_controlled_text_preparation_summary()
    markdown = materials_audit.render_new_material_controlled_text_preparation_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material Controlled Text Preparation",
        (
            "`new-material-controlled-text-preparation-status="
            "blocked_requires_ocr_or_manual_transcription`"
        ),
        "`controlled-text-preparation-items=1`",
        "`pdf-pages=84`",
        "`text-layer-nonempty-pages=13`",
        "`text-layer-chars=592`",
        "`usable-text-layer=0`",
        "`blocked-items=1`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        "`next-material-entry=015-new-material-ocr-or-manual-transcription`",
        "`new_material_controlled_text_prep_xiahai_suanmingji_pdf`",
        "`entry_new_material_xiahai_suanmingji_pdf`",
        "`下海算命记.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff

    assert (
        "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`"
        in handoff
    )
    assert (
        "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`"
        in quickstart
    )


def test_new_material_ocr_or_manual_transcription_blocks_on_missing_runtime():
    items = materials_audit.load_new_material_ocr_or_manual_transcription_items()
    summary = materials_audit.build_new_material_ocr_or_manual_transcription_summary()

    assert len(items) == 1
    item = items[0]
    assert item.transcription_id == "015-new-material-ocr-or-manual-transcription"
    assert item.controlled_text_preparation_item_id == (
        "new_material_controlled_text_prep_xiahai_suanmingji_pdf"
    )
    assert item.transcription_status == "blocked_ocr_runtime_unavailable"
    assert item.selected_path == "ocr_runtime_setup"
    assert item.local_reference == "下海算命记.pdf"
    assert item.page_count == 84
    assert item.pdftoppm_available is True
    assert item.tesseract_available is False
    assert item.ocrmypdf_available is False
    assert item.python_ocr_package_available is False
    assert item.prepared_text_artifact_created is False
    assert item.selected_next_material_entry == (
        "015-new-material-ocr-runtime-setup-or-human-transcription"
    )

    assert summary.transcription_status == "blocked_ocr_runtime_unavailable"
    assert summary.transcription_item_count == 1
    assert summary.page_count == 84
    assert summary.pdftoppm_available_count == 1
    assert summary.ocr_runtime_available_count == 0
    assert summary.prepared_text_artifact_count == 0
    assert summary.blocked_item_count == 1
    assert summary.candidate_extract_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.next_material_entry == (
        "015-new-material-ocr-runtime-setup-or-human-transcription"
    )
    assert summary.boundary_checks == {
        "ocr_or_manual_transcription_items_loaded": "passed",
        "controlled_text_preparation_blocked": "passed",
        "pdf_rendering_available": "passed",
        "ocr_runtime_unavailable": "passed",
        "prepared_text_artifact_absent": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_ocr_or_manual_transcription_markdown_and_docs_sync():
    summary = materials_audit.build_new_material_ocr_or_manual_transcription_summary()
    markdown = materials_audit.render_new_material_ocr_or_manual_transcription_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material OCR Or Manual Transcription",
        "`new-material-ocr-or-manual-transcription-status=blocked_ocr_runtime_unavailable`",
        "`ocr-or-manual-transcription-items=1`",
        "`pdf-pages=84`",
        "`pdftoppm-available=1`",
        "`ocr-runtime-available=0`",
        "`prepared-text-artifacts=0`",
        "`blocked-items=1`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        "`next-material-entry=015-new-material-ocr-runtime-setup-or-human-transcription`",
        "`new_material_ocr_or_manual_xiahai_suanmingji_pdf`",
        "`entry_new_material_xiahai_suanmingji_pdf`",
        "`下海算命记.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff

    assert (
        "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`"
        in handoff
    )
    assert (
        "`next-new-material-start=017-new-material-corrected-pilot-learning-entry-evaluation`"
        in quickstart
    )


def test_new_material_ocr_runtime_setup_blocks_on_quality_gate():
    items = materials_audit.load_new_material_ocr_runtime_setup_items()
    summary = materials_audit.build_new_material_ocr_runtime_setup_summary()

    assert len(items) == 1
    item = items[0]
    assert item.setup_id == "015-new-material-ocr-runtime-setup-or-human-transcription"
    assert item.ocr_or_manual_transcription_item_id == (
        "new_material_ocr_or_manual_xiahai_suanmingji_pdf"
    )
    assert item.setup_status == "blocked_ocr_quality_insufficient"
    assert item.selected_path == "local_tesseract_quality_probe"
    assert item.local_reference == "下海算命记.pdf"
    assert item.page_count == 84
    assert item.probe_page_count == 4
    assert item.probe_dpi == 300
    assert item.pdftoppm_available is True
    assert item.tesseract_available is True
    assert item.tesseract_version == "5.5.0.20241111"
    assert item.chi_sim_available is True
    assert item.tessdata_language_codes == ["chi_sim", "eng", "osd"]
    assert item.probe_psm_values == ["4", "6", "11"]
    assert item.prepared_text_artifact_created is False
    assert item.selected_next_material_entry == (
        "015-new-material-ocr-quality-remediation-or-human-transcription"
    )

    assert summary.setup_status == "blocked_ocr_quality_insufficient"
    assert summary.setup_item_count == 1
    assert summary.page_count == 84
    assert summary.probe_page_count == 4
    assert summary.probe_dpi_values == [300]
    assert summary.pdftoppm_available_count == 1
    assert summary.tesseract_available_count == 1
    assert summary.chi_sim_available_count == 1
    assert summary.prepared_text_artifact_count == 0
    assert summary.blocked_item_count == 1
    assert summary.candidate_extract_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.next_material_entry == (
        "015-new-material-ocr-quality-remediation-or-human-transcription"
    )
    assert summary.boundary_checks == {
        "ocr_runtime_setup_items_loaded": "passed",
        "previous_ocr_runtime_blocker_recorded": "passed",
        "pdf_rendering_available": "passed",
        "local_tesseract_available": "passed",
        "chi_sim_tessdata_available": "passed",
        "prepared_text_artifact_absent": "passed",
        "ocr_quality_gate_blocked": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_ocr_runtime_setup_markdown_and_docs_sync():
    summary = materials_audit.build_new_material_ocr_runtime_setup_summary()
    markdown = materials_audit.render_new_material_ocr_runtime_setup_markdown(summary)
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material OCR Runtime Setup Or Human Transcription",
        "`new-material-ocr-runtime-setup-status=blocked_ocr_quality_insufficient`",
        "`ocr-runtime-setup-items=1`",
        "`pdf-pages=84`",
        "`probe-pages=4`",
        "`probe-dpi-values=300`",
        "`tesseract-available=1`",
        "`chi-sim-available=1`",
        "`prepared-text-artifacts=0`",
        "`blocked-items=1`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        (
            "`next-material-entry="
            "015-new-material-ocr-quality-remediation-or-human-transcription`"
        ),
        "`new_material_ocr_runtime_setup_xiahai_suanmingji_pdf`",
        "`new_material_ocr_or_manual_xiahai_suanmingji_pdf`",
        "`entry_new_material_xiahai_suanmingji_pdf`",
        "`下海算命记.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff

    assert (
        "`next-new-material-start="
        "017-new-material-corrected-pilot-learning-entry-evaluation`"
        in handoff
    )
    assert (
        "`next-new-material-start="
        "017-new-material-corrected-pilot-learning-entry-evaluation`"
        in quickstart
    )


def test_new_material_ocr_quality_remediation_requires_human_correction():
    items = materials_audit.load_new_material_ocr_quality_remediation_items()
    summary = materials_audit.build_new_material_ocr_quality_remediation_summary()

    assert len(items) == 1
    item = items[0]
    assert item.remediation_id == (
        "015-new-material-ocr-quality-remediation-or-human-transcription"
    )
    assert item.ocr_runtime_setup_item_id == (
        "new_material_ocr_runtime_setup_xiahai_suanmingji_pdf"
    )
    assert item.remediation_status == "blocked_requires_human_correction"
    assert item.local_reference == "下海算命记.pdf"
    assert item.page_count == 84
    assert item.probe_page_count == 4
    assert item.probe_dpi == 400
    assert item.vertical_tessdata_available is True
    assert "chi_tra_vert" in item.tessdata_language_codes
    assert "vertical_psm5_probe" in item.preprocessing_methods
    assert item.probe_page_numbers == [20, 35, 50, 70]
    assert item.best_probe_region == "page_70_left_page_chi_tra_vert_psm5"
    assert item.best_probe_han_count == 539
    assert item.best_probe_ascii_count == 4
    assert item.best_probe_noise_count == 4
    assert item.assistive_ocr_route_available is True
    assert item.prepared_text_artifact_created is False
    assert item.human_correction_required is True
    assert item.selected_next_material_entry == (
        "015-new-material-human-corrected-transcription-prep"
    )

    assert summary.remediation_status == "blocked_requires_human_correction"
    assert summary.remediation_item_count == 1
    assert summary.page_count == 84
    assert summary.probe_page_count == 4
    assert summary.probe_dpi_values == [400]
    assert summary.vertical_tessdata_available_count == 1
    assert summary.assistive_ocr_route_count == 1
    assert summary.prepared_text_artifact_count == 0
    assert summary.human_correction_required_count == 1
    assert summary.blocked_item_count == 1
    assert summary.candidate_extract_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.next_material_entry == (
        "015-new-material-human-corrected-transcription-prep"
    )
    assert summary.boundary_checks == {
        "ocr_quality_remediation_items_loaded": "passed",
        "previous_ocr_quality_blocker_recorded": "passed",
        "vertical_tessdata_available": "passed",
        "assistive_ocr_route_identified": "passed",
        "prepared_text_artifact_absent": "passed",
        "human_correction_required": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_ocr_quality_remediation_markdown_and_docs_sync():
    summary = materials_audit.build_new_material_ocr_quality_remediation_summary()
    markdown = materials_audit.render_new_material_ocr_quality_remediation_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material OCR Quality Remediation Or Human Transcription",
        "`new-material-ocr-quality-remediation-status=blocked_requires_human_correction`",
        "`ocr-quality-remediation-items=1`",
        "`pdf-pages=84`",
        "`probe-pages=4`",
        "`probe-dpi-values=400`",
        "`vertical-tessdata-available=1`",
        "`assistive-ocr-route=1`",
        "`prepared-text-artifacts=0`",
        "`human-correction-required=1`",
        "`blocked-items=1`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        "`next-material-entry=015-new-material-human-corrected-transcription-prep`",
        "`new_material_ocr_quality_remediation_xiahai_suanmingji_pdf`",
        "`new_material_ocr_runtime_setup_xiahai_suanmingji_pdf`",
        "`entry_new_material_xiahai_suanmingji_pdf`",
        "`下海算命记.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff

    assert (
        "`next-new-material-start="
        "017-new-material-corrected-pilot-learning-entry-evaluation`"
        in handoff
    )
    assert (
        "`next-new-material-start="
        "017-new-material-corrected-pilot-learning-entry-evaluation`"
        in quickstart
    )


def test_new_material_human_corrected_transcription_prep_is_ready_for_correction():
    items = materials_audit.load_new_material_human_corrected_transcription_prep_items()
    summary = (
        materials_audit.build_new_material_human_corrected_transcription_prep_summary()
    )

    assert len(items) == 1
    item = items[0]
    assert item.prep_id == "015-new-material-human-corrected-transcription-prep"
    assert item.ocr_quality_remediation_item_id == (
        "new_material_ocr_quality_remediation_xiahai_suanmingji_pdf"
    )
    assert item.prep_status == "blocked_ready_for_human_correction"
    assert item.local_reference == "下海算命记.pdf"
    assert item.page_count == 84
    assert item.correction_packet_ready is True
    assert item.selected_page_ranges == [
        "full_source_pages_1_84",
        "pilot_vertical_ocr_pages_20_35_50_70",
    ]
    assert item.layout_profile == "traditional_chinese_vertical_two_page_scan"
    assert item.assistive_ocr_method == (
        "400dpi_split_pages_remove_watermark_chi_tra_vert_psm5"
    )
    assert item.planned_output_artifact == (
        "docs/classical_sources/prepared_text/xiahai_suanmingji_corrected.md"
    )
    assert item.uncorrected_ocr_committed is False
    assert item.prepared_text_artifact_created is False
    assert item.human_corrected_text_available is False
    assert item.selected_next_material_entry == (
        "015-new-material-human-corrected-transcription-execution"
    )

    assert summary.prep_status == "blocked_ready_for_human_correction"
    assert summary.prep_item_count == 1
    assert summary.page_count == 84
    assert summary.correction_packet_ready_count == 1
    assert summary.selected_page_range_count == 2
    assert summary.uncorrected_ocr_committed_count == 0
    assert summary.prepared_text_artifact_count == 0
    assert summary.human_corrected_text_available_count == 0
    assert summary.blocked_item_count == 1
    assert summary.candidate_extract_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.next_material_entry == (
        "015-new-material-human-corrected-transcription-execution"
    )
    assert summary.boundary_checks == {
        "human_corrected_transcription_prep_items_loaded": "passed",
        "previous_human_correction_blocker_recorded": "passed",
        "correction_packet_ready": "passed",
        "uncorrected_ocr_not_committed": "passed",
        "corrected_text_not_yet_available": "passed",
        "prepared_text_artifact_absent": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_human_corrected_transcription_prep_markdown_and_docs_sync():
    summary = (
        materials_audit.build_new_material_human_corrected_transcription_prep_summary()
    )
    markdown = (
        materials_audit.render_new_material_human_corrected_transcription_prep_markdown(
            summary
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material Human Corrected Transcription Prep",
        (
            "`new-material-human-corrected-transcription-prep-status="
            "blocked_ready_for_human_correction`"
        ),
        "`human-corrected-transcription-prep-items=1`",
        "`pdf-pages=84`",
        "`correction-packet-ready=1`",
        "`selected-page-ranges=2`",
        "`uncorrected-ocr-committed=0`",
        "`prepared-text-artifacts=0`",
        "`human-corrected-text-available=0`",
        "`blocked-items=1`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        "`next-material-entry=015-new-material-human-corrected-transcription-execution`",
        "`new_material_human_corrected_transcription_prep_xiahai_suanmingji_pdf`",
        "`new_material_ocr_quality_remediation_xiahai_suanmingji_pdf`",
        "`docs/classical_sources/prepared_text/xiahai_suanmingji_corrected.md`",
        "`下海算命记.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff

    assert (
        "`next-new-material-start="
        "017-new-material-corrected-pilot-learning-entry-evaluation`"
        in handoff
    )
    assert (
        "`next-new-material-start="
        "017-new-material-corrected-pilot-learning-entry-evaluation`"
        in quickstart
    )


def test_new_material_human_corrected_transcription_execution_creates_pilot():
    items = materials_audit.load_new_material_human_corrected_transcription_execution_items()
    summary = (
        materials_audit.build_new_material_human_corrected_transcription_execution_summary()
    )
    artifact = Path("docs/classical_sources/prepared_text/xiahai_suanmingji_corrected.md")

    assert artifact.exists()
    artifact_text = artifact.read_text(encoding="utf-8")
    assert "corrected pilot excerpts only" in artifact_text
    assert "卜卦無關乎神鬼" in artifact_text
    assert "積善之家必有餘慶" in artifact_text

    assert len(items) == 1
    item = items[0]
    assert item.execution_id == "015-new-material-human-corrected-transcription-execution"
    assert item.transcription_prep_item_id == (
        "new_material_human_corrected_transcription_prep_xiahai_suanmingji_pdf"
    )
    assert item.execution_status == "pilot_prepared_text_created"
    assert item.prepared_text_artifact == (
        "docs/classical_sources/prepared_text/xiahai_suanmingji_corrected.md"
    )
    assert item.corrected_excerpt_count == 4
    assert item.corrected_character_count == 35
    assert item.page_locator_count == 4
    assert item.uncorrected_ocr_committed is False
    assert item.long_form_transcription_committed is False
    assert item.prepared_text_artifact_created is True
    assert item.human_corrected_text_available is True
    assert item.learning_entry_ready is True
    assert item.selected_next_material_entry == (
        "017-new-material-corrected-pilot-learning-entry-evaluation"
    )

    assert summary.execution_status == "pilot_prepared_text_created"
    assert summary.execution_item_count == 1
    assert summary.prepared_text_artifact_count == 1
    assert summary.corrected_excerpt_count == 4
    assert summary.corrected_character_count == 35
    assert summary.page_locator_count == 4
    assert summary.learning_entry_ready_count == 1
    assert summary.uncorrected_ocr_committed_count == 0
    assert summary.long_form_transcription_committed_count == 0
    assert summary.candidate_extract_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.next_material_entry == (
        "017-new-material-corrected-pilot-learning-entry-evaluation"
    )
    assert summary.boundary_checks == {
        "human_corrected_transcription_execution_items_loaded": "passed",
        "previous_correction_packet_ready": "passed",
        "prepared_text_artifact_created": "passed",
        "uncorrected_ocr_not_committed": "passed",
        "long_form_transcription_absent": "passed",
        "learning_entry_ready": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_human_corrected_transcription_execution_markdown_and_docs_sync():
    summary = (
        materials_audit.build_new_material_human_corrected_transcription_execution_summary()
    )
    markdown = (
        materials_audit.render_new_material_human_corrected_transcription_execution_markdown(
            summary
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material Human Corrected Transcription Execution",
        (
            "`new-material-human-corrected-transcription-execution-status="
            "pilot_prepared_text_created`"
        ),
        "`human-corrected-transcription-execution-items=1`",
        "`prepared-text-artifacts=1`",
        "`corrected-excerpts=4`",
        "`corrected-characters=35`",
        "`page-locators=4`",
        "`learning-entry-ready=1`",
        "`uncorrected-ocr-committed=0`",
        "`long-form-transcription-committed=0`",
        "`candidate-extract-delta=0`",
        "`formal-evidence-delta=0`",
        (
            "`next-material-entry="
            "017-new-material-corrected-pilot-learning-entry-evaluation`"
        ),
        "`new_material_human_corrected_transcription_execution_xiahai_suanmingji_pdf`",
        "`docs/classical_sources/prepared_text/xiahai_suanmingji_corrected.md`",
        "`下海算命记.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff

    assert (
        "`next-new-material-start="
        "017-new-material-corrected-pilot-learning-entry-evaluation`"
        in handoff
    )
    assert (
        "`next-new-material-start="
        "017-new-material-corrected-pilot-learning-entry-evaluation`"
        in quickstart
    )


def test_new_material_expanded_corrected_transcription_selection_selects_bounded_window():
    items = (
        materials_audit
        .load_new_material_expanded_corrected_transcription_selection_items()
    )
    summary = (
        materials_audit
        .build_new_material_expanded_corrected_transcription_selection_summary()
    )

    assert len(items) == 1
    item = items[0]
    assert item.selection_item_id == (
        "new_material_expanded_corrected_transcription_selection_xiahai_suanmingji_pdf"
    )
    assert item.selection_id == (
        "015-new-material-expanded-corrected-transcription-selection"
    )
    assert item.completion_review_item_id == (
        "new_material_corrected_pilot_learning_completion_review_xiahai_suanmingji_pdf"
    )
    assert item.selection_status == "selected_for_expanded_correction_prep"
    assert item.local_reference == "下海算命记.pdf"
    assert item.selected_page_ranges == [
        "pages_18_25_method_discussion_window",
        "pages_66_72_case_examples_window",
    ]
    assert item.selected_page_locators == [
        "page_20_method_context",
        "page_20_topic_context",
        "page_70_case_context",
        "page_72_case_followup_context",
    ]
    assert item.selected_page_count == 15
    assert item.planned_output_artifact == (
        "docs/classical_sources/prepared_text/xiahai_suanmingji_expanded_corrected.md"
    )
    assert item.risk_boundary == "high_risk"
    assert item.candidate_intake_allowed is False
    assert item.correction_prep_allowed is True
    assert item.downstream_mutation_authorized is False
    assert item.candidate_extract_delta_count == 0
    assert item.review_decision_delta_count == 0
    assert item.promotion_batch_delta_count == 0
    assert item.formal_evidence_delta_count == 0
    assert item.selected_next_material_entry == (
        "015-new-material-expanded-corrected-transcription-prep"
    )

    assert summary.selection_status == "selected_for_expanded_correction_prep"
    assert summary.selection_item_count == 1
    assert summary.selected_page_range_count == 2
    assert summary.selected_page_locator_count == 4
    assert summary.selected_page_count == 15
    assert summary.correction_prep_allowed_count == 1
    assert summary.candidate_intake_allowed_count == 0
    assert summary.candidate_extract_delta_count == 0
    assert summary.review_decision_delta_count == 0
    assert summary.promotion_batch_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "015-new-material-expanded-corrected-transcription-prep"
    )
    assert summary.risk_boundary_counts == {"high_risk": 1}
    assert summary.boundary_checks == {
        "expanded_correction_selection_items_loaded": "passed",
        "previous_pilot_learning_closed": "passed",
        "additional_correction_required": "passed",
        "bounded_page_windows_selected": "passed",
        "correction_prep_allowed": "passed",
        "candidate_intake_blocked": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_expanded_corrected_transcription_selection_markdown_and_docs_sync():
    summary = (
        materials_audit
        .build_new_material_expanded_corrected_transcription_selection_summary()
    )
    markdown = (
        materials_audit
        .render_new_material_expanded_corrected_transcription_selection_markdown(
            summary
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material Expanded Corrected Transcription Selection",
        "`new-material-expanded-corrected-transcription-selection-status=selected_for_expanded_correction_prep`",
        "`expanded-correction-selection-items=1`",
        "`selected-page-ranges=2`",
        "`selected-page-locators=4`",
        "`selected-pages=15`",
        "`correction-prep-allowed=1`",
        "`candidate-intake-allowed=0`",
        "`candidate-extract-delta=0`",
        "`review-decision-delta=0`",
        "`promotion-batch-delta=0`",
        "`formal-evidence-delta=0`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-new-material-expanded-corrected-transcription-prep`",
        "`new_material_expanded_corrected_transcription_selection_xiahai_suanmingji_pdf`",
        "`new_material_corrected_pilot_learning_completion_review_xiahai_suanmingji_pdf`",
        "`docs/classical_sources/prepared_text/xiahai_suanmingji_expanded_corrected.md`",
        "`下海算命记.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff
        assert marker in quickstart

    assert (
        "`next-new-material-start=015-new-material-expanded-corrected-transcription-selection`"
        in handoff
    )
    assert (
        "`next-new-material-start=015-new-material-expanded-corrected-transcription-selection`"
        in quickstart
    )


def test_new_material_expanded_corrected_transcription_prep_is_ready_for_execution():
    items = materials_audit.load_new_material_expanded_corrected_transcription_prep_items()
    summary = (
        materials_audit.build_new_material_expanded_corrected_transcription_prep_summary()
    )

    assert len(items) == 1
    item = items[0]
    assert item.prep_item_id == (
        "new_material_expanded_corrected_transcription_prep_xiahai_suanmingji_pdf"
    )
    assert item.prep_id == "015-new-material-expanded-corrected-transcription-prep"
    assert item.selection_item_id == (
        "new_material_expanded_corrected_transcription_selection_xiahai_suanmingji_pdf"
    )
    assert item.prep_status == "ready_for_expanded_correction_execution"
    assert item.local_reference == "下海算命记.pdf"
    assert item.selected_page_count == 15
    assert item.correction_packet_ready is True
    assert item.planned_output_artifact == (
        "docs/classical_sources/prepared_text/xiahai_suanmingji_expanded_corrected.md"
    )
    assert item.uncorrected_ocr_committed is False
    assert item.prepared_text_artifact_created is False
    assert item.human_corrected_text_available is False
    assert item.candidate_intake_allowed is False
    assert item.downstream_mutation_authorized is False
    assert item.candidate_extract_delta_count == 0
    assert item.review_decision_delta_count == 0
    assert item.promotion_batch_delta_count == 0
    assert item.formal_evidence_delta_count == 0
    assert item.selected_next_material_entry == (
        "015-new-material-expanded-corrected-transcription-execution"
    )

    assert summary.prep_status == "ready_for_expanded_correction_execution"
    assert summary.prep_item_count == 1
    assert summary.selected_page_range_count == 2
    assert summary.selected_page_locator_count == 4
    assert summary.selected_page_count == 15
    assert summary.correction_packet_ready_count == 1
    assert summary.uncorrected_ocr_committed_count == 0
    assert summary.prepared_text_artifact_count == 0
    assert summary.human_corrected_text_available_count == 0
    assert summary.candidate_intake_allowed_count == 0
    assert summary.candidate_extract_delta_count == 0
    assert summary.review_decision_delta_count == 0
    assert summary.promotion_batch_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "015-new-material-expanded-corrected-transcription-execution"
    )
    assert summary.boundary_checks == {
        "expanded_correction_prep_items_loaded": "passed",
        "previous_selection_ready": "passed",
        "correction_packet_ready": "passed",
        "uncorrected_ocr_not_committed": "passed",
        "corrected_text_not_yet_available": "passed",
        "candidate_intake_blocked": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_new_material_expanded_corrected_transcription_prep_markdown_and_docs_sync():
    summary = (
        materials_audit.build_new_material_expanded_corrected_transcription_prep_summary()
    )
    markdown = (
        materials_audit.render_new_material_expanded_corrected_transcription_prep_markdown(
            summary
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material Expanded Corrected Transcription Prep",
        "`new-material-expanded-corrected-transcription-prep-status=ready_for_expanded_correction_execution`",
        "`expanded-correction-prep-items=1`",
        "`selected-page-ranges=2`",
        "`selected-page-locators=4`",
        "`selected-pages=15`",
        "`correction-packet-ready=1`",
        "`uncorrected-ocr-committed=0`",
        "`prepared-text-artifacts=0`",
        "`human-corrected-text-available=0`",
        "`candidate-intake-allowed=0`",
        "`candidate-extract-delta=0`",
        "`review-decision-delta=0`",
        "`promotion-batch-delta=0`",
        "`formal-evidence-delta=0`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-new-material-expanded-corrected-transcription-execution`",
        "`new_material_expanded_corrected_transcription_prep_xiahai_suanmingji_pdf`",
        "`new_material_expanded_corrected_transcription_selection_xiahai_suanmingji_pdf`",
        "`docs/classical_sources/prepared_text/xiahai_suanmingji_expanded_corrected.md`",
        "`下海算命记.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff
        assert marker in quickstart

    assert (
        "`next-new-material-start=015-new-material-expanded-corrected-transcription-execution`"
        in handoff
    )
    assert (
        "`next-new-material-start=015-new-material-expanded-corrected-transcription-execution`"
        in quickstart
    )


def test_new_material_expanded_corrected_transcription_execution_creates_artifact():
    items = (
        materials_audit
        .load_new_material_expanded_corrected_transcription_execution_items()
    )
    summary = (
        materials_audit
        .build_new_material_expanded_corrected_transcription_execution_summary()
    )
    artifact = Path(
        "docs/classical_sources/prepared_text/xiahai_suanmingji_expanded_corrected.md"
    )
    artifact_text = artifact.read_text(encoding="utf-8")

    assert len(items) == 1
    item = items[0]
    assert item.execution_item_id == (
        "new_material_expanded_corrected_transcription_execution_xiahai_suanmingji_pdf"
    )
    assert item.execution_id == (
        "015-new-material-expanded-corrected-transcription-execution"
    )
    assert item.prep_item_id == (
        "new_material_expanded_corrected_transcription_prep_xiahai_suanmingji_pdf"
    )
    assert item.execution_status == "expanded_prepared_text_created"
    assert item.local_reference == "下海算命记.pdf"
    assert item.prepared_text_artifact == (
        "docs/classical_sources/prepared_text/xiahai_suanmingji_expanded_corrected.md"
    )
    assert item.selected_page_ranges == [
        "pages_18_25_method_discussion_window",
        "pages_66_72_case_examples_window",
    ]
    assert item.selected_page_locators == [
        "page_20_method_context",
        "page_20_topic_context",
        "page_70_case_context",
        "page_72_case_followup_context",
    ]
    assert item.selected_page_count == 15
    assert item.expanded_window_count == 2
    assert item.corrected_excerpt_count == 3
    assert item.corrected_character_count == 27
    assert item.page_locator_count == 4
    assert item.uncorrected_ocr_committed is False
    assert item.long_form_transcription_committed is False
    assert item.prepared_text_artifact_created is True
    assert item.human_corrected_text_available is True
    assert item.learning_entry_ready is True
    assert item.candidate_intake_allowed is False
    assert item.downstream_mutation_authorized is False
    assert item.candidate_extract_delta_count == 0
    assert item.review_decision_delta_count == 0
    assert item.promotion_batch_delta_count == 0
    assert item.formal_evidence_delta_count == 0
    assert item.selected_next_material_entry == (
        "017-new-material-expanded-corrected-learning-entry-evaluation"
    )

    assert summary.execution_status == "expanded_prepared_text_created"
    assert summary.execution_item_count == 1
    assert summary.source_file_count == 1
    assert summary.prepared_text_artifact_count == 1
    assert summary.selected_page_range_count == 2
    assert summary.selected_page_locator_count == 4
    assert summary.selected_page_count == 15
    assert summary.expanded_window_count == 2
    assert summary.corrected_excerpt_count == 3
    assert summary.corrected_character_count == 27
    assert summary.page_locator_count == 4
    assert summary.learning_entry_ready_count == 1
    assert summary.human_corrected_text_available_count == 1
    assert summary.uncorrected_ocr_committed_count == 0
    assert summary.long_form_transcription_committed_count == 0
    assert summary.candidate_intake_allowed_count == 0
    assert summary.candidate_extract_delta_count == 0
    assert summary.review_decision_delta_count == 0
    assert summary.promotion_batch_delta_count == 0
    assert summary.formal_evidence_delta_count == 0
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "017-new-material-expanded-corrected-learning-entry-evaluation"
    )
    assert summary.boundary_checks == {
        "expanded_corrected_transcription_execution_items_loaded": "passed",
        "previous_expanded_correction_packet_ready": "passed",
        "prepared_text_artifact_created": "passed",
        "corrected_text_available": "passed",
        "uncorrected_ocr_not_committed": "passed",
        "long_form_transcription_absent": "passed",
        "learning_entry_ready": "passed",
        "candidate_intake_blocked": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }
    assert "卜卦無關乎神鬼" in artifact_text
    assert "腦算命的程式" in artifact_text
    assert "以下我且舉幾個實際的卦例來談" in artifact_text
    assert "`uncorrected-ocr-committed=0`" in artifact_text


def test_new_material_expanded_corrected_transcription_execution_markdown_and_docs_sync():
    summary = (
        materials_audit
        .build_new_material_expanded_corrected_transcription_execution_summary()
    )
    markdown = (
        materials_audit
        .render_new_material_expanded_corrected_transcription_execution_markdown(
            summary
        )
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 New Material Expanded Corrected Transcription Execution",
        "`new-material-expanded-corrected-transcription-execution-status=expanded_prepared_text_created`",
        "`expanded-correction-execution-items=1`",
        "`prepared-text-artifacts=1`",
        "`selected-page-ranges=2`",
        "`selected-page-locators=4`",
        "`selected-pages=15`",
        "`expanded-windows=2`",
        "`corrected-excerpts=3`",
        "`corrected-characters=27`",
        "`page-locators=4`",
        "`learning-entry-ready=1`",
        "`human-corrected-text-available=1`",
        "`uncorrected-ocr-committed=0`",
        "`long-form-transcription-committed=0`",
        "`candidate-intake-allowed=0`",
        "`candidate-extract-delta=0`",
        "`review-decision-delta=0`",
        "`promotion-batch-delta=0`",
        "`formal-evidence-delta=0`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=017-new-material-expanded-corrected-learning-entry-evaluation`",
        "`new_material_expanded_corrected_transcription_execution_xiahai_suanmingji_pdf`",
        "`new_material_expanded_corrected_transcription_prep_xiahai_suanmingji_pdf`",
        "`docs/classical_sources/prepared_text/xiahai_suanmingji_expanded_corrected.md`",
        "`下海算命记.pdf`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff
        assert marker in quickstart

    assert (
        "`next-new-material-start=017-new-material-expanded-corrected-learning-entry-evaluation`"
        in handoff
    )
    assert (
        "`next-new-material-start=017-new-material-expanded-corrected-learning-entry-evaluation`"
        in quickstart
    )


def test_raw_text_cluster_source_selection_items_load_bazi_general_sources():
    items = materials_audit.load_raw_text_cluster_source_selection_items()
    items_by_id = {item.selection_id: item for item in items}

    assert len(items) == 8
    assert {item.triage_group_id for item in items} == {"raw_text_triage_bazi_general"}
    assert {item.cluster_id for item in items} == {
        "bazi_general_foundation_textbook_cluster",
        "bazi_general_classical_reference_cluster",
    }
    assert all(
        item.source_root == materials_audit.RAW_TEXT_TRIAGE_SOURCE_ROOT
        for item in items
    )
    assert sum(item.file_count for item in items) == 13
    assert sum(item.priority_text_candidate_count for item in items) == 13
    assert all(path and not path.startswith("/") for item in items for path in item.relative_paths)
    assert all(
        materials_audit.RAW_TEXT_TRIAGE_SOURCE_ROOT not in path
        for item in items
        for path in item.relative_paths
    )
    assert items_by_id[
        "bazi_general_foundation_youran_notes"
    ].selection_status == "selected_for_identity_review"
    assert items_by_id[
        "bazi_general_classical_ditiansui_variant_set"
    ].selection_status == "variant_identity_review"
    assert items_by_id[
        "bazi_general_classical_huntian_baolan_ziping"
    ].selection_status == "deferred_after_cluster_selection"


def test_raw_text_cluster_source_selection_summary_counts_bazi_general_sources():
    summary = materials_audit.build_raw_text_cluster_source_selection_summary()

    assert summary.selection_id == "015-bazi-general-cluster-source-selection"
    assert summary.selection_status == "cluster_source_selection_completed"
    assert summary.triage_group_id == "raw_text_triage_bazi_general"
    assert summary.selected_cluster_ids == [
        "bazi_general_foundation_textbook_cluster",
        "bazi_general_classical_reference_cluster",
    ]
    assert summary.source_selection_item_count == 8
    assert summary.source_file_count == 13
    assert summary.priority_text_candidate_count == 13
    assert summary.selected_for_identity_review_count == 5
    assert summary.variant_identity_review_count == 2
    assert summary.deferred_after_cluster_selection_count == 1
    assert summary.status_counts == {
        "selected_for_identity_review": 5,
        "variant_identity_review": 2,
        "deferred_after_cluster_selection": 1,
    }
    assert summary.risk_boundary_counts == {"ordinary": 8}
    assert summary.extension_counts == {".pdf": 13}
    assert summary.target_rule_family_counts == {
        "branch_interaction": 1,
        "pattern_strength": 7,
        "ten_god_relation": 2,
        "useful_god_candidate": 5,
    }
    assert summary.selected_item_ids == [
        "bazi_general_foundation_youran_notes",
        "bazi_general_foundation_tianma_notes",
        "bazi_general_foundation_lecture_textbook",
        "bazi_general_foundation_beichen_intro",
        "bazi_general_classical_ziping_orthodox_pair",
    ]
    assert summary.variant_review_item_ids == [
        "bazi_general_classical_ditiansui_variant_set",
        "bazi_general_classical_qiongtong_variant_set",
    ]
    assert summary.deferred_item_ids == [
        "bazi_general_classical_huntian_baolan_ziping",
    ]
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-bazi-general-source-identity-review"
    assert summary.boundary_checks == {
        "source_selection_items_loaded": "passed",
        "selected_clusters_loaded": "passed",
        "selected_cluster_references_valid": "passed",
        "source_paths_are_relative": "passed",
        "raw_materials_not_mutated": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }


def test_raw_text_cluster_source_selection_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_cluster_source_selection_summary()
    markdown = materials_audit.render_raw_text_cluster_source_selection_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Bazi General Cluster Source Selection",
        "`cluster-source-selection-status=cluster_source_selection_completed`",
        "`cluster-source-selection-items=8`",
        "`cluster-source-files=13`",
        "`selected-for-identity-review=5`",
        "`variant-identity-review=2`",
        "`deferred-after-cluster-selection=1`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-bazi-general-source-identity-review`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_source_identity_review_items_load_bazi_general_sources():
    items = materials_audit.load_raw_text_source_identity_review_items()
    items_by_id = {item.review_id: item for item in items}

    assert len(items) == 8
    assert {item.triage_group_id for item in items} == {"raw_text_triage_bazi_general"}
    assert {item.cluster_id for item in items} == {
        "bazi_general_foundation_textbook_cluster",
        "bazi_general_classical_reference_cluster",
    }
    assert all(
        item.source_root == materials_audit.RAW_TEXT_TRIAGE_SOURCE_ROOT
        for item in items
    )
    assert items_by_id[
        "bazi_general_identity_youran_notes"
    ].matched_source_library_entry_ids == ["entry_markdown_source_batch_001"]
    assert items_by_id[
        "bazi_general_identity_tianma_notes"
    ].source_library_overlap_status == "existing_markdown_batch_overlap"
    assert items_by_id[
        "bazi_general_identity_lecture_textbook"
    ].identity_status == "registration_prep_ready"
    assert items_by_id[
        "bazi_general_identity_ditiansui_variant_set"
    ].identity_status == "variant_choice_required"
    assert items_by_id[
        "bazi_general_identity_huntian_baolan_ziping"
    ].identity_status == "deferred_large_source"


def test_raw_text_source_identity_review_summary_counts_bazi_general_sources():
    summary = materials_audit.build_raw_text_source_identity_review_summary()

    assert summary.review_id == "015-bazi-general-source-identity-review"
    assert summary.review_status == "source_identity_review_completed"
    assert summary.triage_group_id == "raw_text_triage_bazi_general"
    assert summary.identity_review_item_count == 8
    assert summary.existing_batch_overlap_count == 2
    assert summary.registration_prep_ready_count == 3
    assert summary.variant_choice_required_count == 2
    assert summary.deferred_large_source_count == 1
    assert summary.identity_status_counts == {
        "existing_batch_overlap": 2,
        "registration_prep_ready": 3,
        "variant_choice_required": 2,
        "deferred_large_source": 1,
    }
    assert summary.source_library_overlap_counts == {
        "existing_markdown_batch_overlap": 2,
        "no_registered_overlap_found": 3,
        "variant_set_requires_choice": 2,
        "deferred_large_source": 1,
    }
    assert summary.registration_readiness_counts == {
        "no_registration_needed_existing_batch": 2,
        "ready_for_registration_prep": 3,
        "needs_variant_choice": 2,
        "deferred": 1,
    }
    assert summary.risk_boundary_counts == {"ordinary": 8}
    assert summary.target_rule_family_counts == {
        "branch_interaction": 1,
        "pattern_strength": 7,
        "ten_god_relation": 2,
        "useful_god_candidate": 5,
    }
    assert summary.existing_batch_overlap_ids == [
        "bazi_general_identity_youran_notes",
        "bazi_general_identity_tianma_notes",
    ]
    assert summary.registration_prep_item_ids == [
        "bazi_general_identity_lecture_textbook",
        "bazi_general_identity_beichen_intro",
        "bazi_general_identity_ziping_orthodox_pair",
    ]
    assert summary.variant_choice_item_ids == [
        "bazi_general_identity_ditiansui_variant_set",
        "bazi_general_identity_qiongtong_variant_set",
    ]
    assert summary.deferred_item_ids == [
        "bazi_general_identity_huntian_baolan_ziping",
    ]
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-bazi-general-registration-prep"
    assert summary.boundary_checks == {
        "identity_review_items_loaded": "passed",
        "source_selection_items_loaded": "passed",
        "source_selection_references_valid": "passed",
        "source_library_overlap_references_valid": "passed",
        "raw_materials_not_mutated": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }


def test_raw_text_source_identity_review_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_source_identity_review_summary()
    markdown = materials_audit.render_raw_text_source_identity_review_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Bazi General Source Identity Review",
        "`source-identity-review-status=source_identity_review_completed`",
        "`source-identity-review-items=8`",
        "`existing-batch-overlap=2`",
        "`registration-prep-ready=3`",
        "`variant-choice-required=2`",
        "`deferred-large-source=1`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-bazi-general-registration-prep`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_source_registration_prep_items_load_bazi_general_sources():
    items = materials_audit.load_raw_text_source_registration_prep_items()
    items_by_id = {item.prep_id: item for item in items}

    assert len(items) == 3
    assert {item.triage_group_id for item in items} == {"raw_text_triage_bazi_general"}
    assert {item.registration_status for item in items} == {
        "ready_for_source_registration"
    }
    assert {item.proposed_readiness_status for item in items} == {"needs_preparation"}
    assert {item.proposed_next_action for item in items} == {"prepare_material"}
    assert {item.proposed_tracking_status for item in items} == {
        "external_untracked"
    }
    assert {
        item.identity_review_id for item in items
    } == {
        "bazi_general_identity_lecture_textbook",
        "bazi_general_identity_beichen_intro",
        "bazi_general_identity_ziping_orthodox_pair",
    }
    assert all(
        path and not path.startswith("/")
        for item in items
        for path in item.proposed_local_references
    )
    assert items_by_id[
        "bazi_general_registration_prep_ziping_orthodox_pair"
    ].proposed_local_references == [
        "子平命理正宗电子版上.pdf",
        "子平命理正宗电子版下.pdf",
    ]
    assert items_by_id[
        "bazi_general_registration_prep_lecture_textbook"
    ].proposed_entry_id == "entry_bazi_general_lecture_textbook_pdf"


def test_raw_text_source_registration_prep_summary_counts_bazi_general_sources():
    summary = materials_audit.build_raw_text_source_registration_prep_summary()

    assert summary.prep_id == "015-bazi-general-registration-prep"
    assert summary.prep_status == "registration_prep_completed"
    assert summary.triage_group_id == "raw_text_triage_bazi_general"
    assert summary.registration_prep_item_count == 3
    assert summary.proposed_source_file_count == 4
    assert summary.skipped_existing_batch_overlap_count == 2
    assert summary.blocked_variant_choice_count == 2
    assert summary.deferred_large_source_count == 1
    assert summary.registration_status_counts == {
        "ready_for_source_registration": 3,
    }
    assert summary.proposed_readiness_counts == {"needs_preparation": 3}
    assert summary.proposed_next_action_counts == {"prepare_material": 3}
    assert summary.risk_tier_counts == {"ordinary": 3}
    assert summary.target_rule_family_counts == {
        "branch_interaction": 1,
        "pattern_strength": 3,
        "ten_god_relation": 1,
        "useful_god_candidate": 2,
    }
    assert summary.proposed_entry_ids == [
        "entry_bazi_general_lecture_textbook_pdf",
        "entry_bazi_general_beichen_intro_pdf",
        "entry_bazi_general_ziping_orthodox_pair_pdf",
    ]
    assert summary.registration_prep_item_ids == [
        "bazi_general_registration_prep_lecture_textbook",
        "bazi_general_registration_prep_beichen_intro",
        "bazi_general_registration_prep_ziping_orthodox_pair",
    ]
    assert summary.skipped_existing_batch_overlap_ids == [
        "bazi_general_identity_youran_notes",
        "bazi_general_identity_tianma_notes",
    ]
    assert summary.blocked_variant_choice_ids == [
        "bazi_general_identity_ditiansui_variant_set",
        "bazi_general_identity_qiongtong_variant_set",
    ]
    assert summary.deferred_item_ids == [
        "bazi_general_identity_huntian_baolan_ziping",
    ]
    assert summary.source_library_mutation_authorized is False
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-bazi-general-source-registration"
    assert summary.boundary_checks == {
        "registration_prep_items_loaded": "passed",
        "identity_review_items_loaded": "passed",
        "identity_review_references_valid": "passed",
        "proposed_entries_registered_or_available": "passed",
        "source_paths_are_relative": "passed",
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }


def test_raw_text_source_registration_prep_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_source_registration_prep_summary()
    markdown = materials_audit.render_raw_text_source_registration_prep_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Bazi General Registration Prep",
        "`registration-prep-status=registration_prep_completed`",
        "`registration-prep-items=3`",
        "`proposed-source-files=4`",
        "`skipped-existing-batch-overlap=2`",
        "`blocked-variant-choice=2`",
        "`deferred-large-source=1`",
        "`source-library-mutation-authorized=false`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-bazi-general-source-registration`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_raw_text_source_registration_summary_counts_registered_bazi_general_sources():
    summary = materials_audit.build_raw_text_source_registration_summary()

    assert summary.registration_id == "015-bazi-general-source-registration"
    assert summary.registration_status == "source_registration_completed"
    assert summary.triage_group_id == "raw_text_triage_bazi_general"
    assert summary.registered_entry_count == 3
    assert summary.registered_source_file_count == 4
    assert summary.skipped_existing_batch_overlap_count == 2
    assert summary.blocked_variant_choice_count == 2
    assert summary.deferred_large_source_count == 1
    assert summary.registered_entry_ids == [
        "entry_bazi_general_lecture_textbook_pdf",
        "entry_bazi_general_beichen_intro_pdf",
        "entry_bazi_general_ziping_orthodox_pair_pdf",
    ]
    assert summary.registered_material_ids == [
        "material_bazi_general_lecture_textbook_pdf",
        "material_bazi_general_beichen_intro_pdf",
        "material_bazi_general_ziping_orthodox_pair_pdf",
    ]
    assert summary.skipped_existing_batch_overlap_ids == [
        "bazi_general_identity_youran_notes",
        "bazi_general_identity_tianma_notes",
    ]
    assert summary.blocked_variant_choice_ids == [
        "bazi_general_identity_ditiansui_variant_set",
        "bazi_general_identity_qiongtong_variant_set",
    ]
    assert summary.deferred_item_ids == [
        "bazi_general_identity_huntian_baolan_ziping",
    ]
    assert summary.source_library_mutation_authorized is True
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == "015-bazi-general-source-preparation-reading"
    assert summary.boundary_checks == {
        "registration_prep_items_loaded": "passed",
        "source_library_entries_loaded": "passed",
        "prepared_entries_registered": "passed",
        "registered_entries_match_prep_metadata": "passed",
        "skipped_existing_batch_overlap_not_duplicated": "passed",
        "variant_choice_boundary_respected": "passed",
        "deferred_large_source_not_registered": "passed",
        "raw_materials_not_mutated": "passed",
        "013_012_not_mutated": "passed",
    }


def test_bazi_general_source_preparation_reading_summary_closes_three_source_chain():
    summary = materials_audit.build_bazi_general_source_preparation_reading_summary()

    assert summary.reading_id == "015-bazi-general-source-preparation-reading"
    assert summary.reading_status == "preparation_reading_completed"
    assert summary.source_entry_count == 3
    assert summary.source_file_count == 4
    assert summary.material_audit_record_count == 3
    assert summary.extraction_task_count == 3
    assert summary.learning_note_count == 3
    assert summary.candidate_extract_count == 3
    assert summary.review_decision_count == 3
    assert summary.promotion_batch_count == 1
    assert summary.formal_source_count == 3
    assert summary.formal_evidence_count == 3
    assert summary.source_library_mutation_authorized is True
    assert summary.downstream_mutation_authorized is True
    assert summary.source_entry_ids == [
        "entry_bazi_general_lecture_textbook_pdf",
        "entry_bazi_general_beichen_intro_pdf",
        "entry_bazi_general_ziping_orthodox_pair_pdf",
    ]
    assert summary.source_material_ids == [
        "material_bazi_general_lecture_textbook_pdf",
        "material_bazi_general_beichen_intro_pdf",
        "material_bazi_general_ziping_orthodox_pair_pdf",
    ]
    assert summary.candidate_ids == [
        "candidate_bazi_general_lecture_pattern_strength_001",
        "candidate_bazi_general_beichen_branch_interaction_001",
        "candidate_bazi_general_ziping_useful_god_001",
    ]
    assert summary.evidence_ids == [
        "bazi_general_lecture_pattern_strength_001",
        "bazi_general_beichen_branch_interaction_001",
        "bazi_general_ziping_useful_god_001",
    ]
    assert summary.next_material_entry == (
        "015-bazi-general-variant-choice-and-deferred-review"
    )
    assert summary.boundary_checks == {
        "registered_entries_loaded": "passed",
        "material_preparation_records_loaded": "passed",
        "extraction_tasks_completed": "passed",
        "learning_notes_applied": "passed",
        "013_candidates_reviewed_promoted": "passed",
        "012_formal_evidence_linked": "passed",
        "skipped_existing_batch_overlap_not_duplicated": "passed",
        "variant_choice_boundary_respected": "passed",
        "deferred_large_source_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_bazi_general_source_preparation_reading_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_bazi_general_source_preparation_reading_summary()
    markdown = materials_audit.render_bazi_general_source_preparation_reading_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Bazi General Source Preparation Reading",
        "`source-preparation-reading-status=preparation_reading_completed`",
        "`source-preparation-reading-entries=3`",
        "`source-preparation-reading-files=4`",
        "`candidate-extracts=3`",
        "`formal-evidence-units=3`",
        "`downstream-mutation-authorized=true`",
        "`next-material-entry=015-bazi-general-variant-choice-and-deferred-review`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_bazi_general_variant_deferred_review_items_load_residual_surface():
    items = materials_audit.load_bazi_general_variant_deferred_review_items()
    items_by_id = {item.item_id: item for item in items}

    assert len(items) == 3
    assert set(items_by_id) == {
        "bazi_general_variant_review_ditiansui_variant_set",
        "bazi_general_variant_review_qiongtong_variant_set",
        "bazi_general_deferred_review_huntian_baolan_ziping",
    }
    assert {item.triage_group_id for item in items} == {
        "raw_text_triage_bazi_general"
    }
    assert all(
        item.source_root == materials_audit.RAW_TEXT_TRIAGE_SOURCE_ROOT
        for item in items
    )
    assert all(
        path and not path.startswith("/")
        for item in items
        for path in item.local_references
    )
    assert items_by_id[
        "bazi_general_variant_review_ditiansui_variant_set"
    ].identity_review_id == "bazi_general_identity_ditiansui_variant_set"
    assert items_by_id[
        "bazi_general_variant_review_ditiansui_variant_set"
    ].review_kind == "variant_choice"
    assert items_by_id[
        "bazi_general_variant_review_ditiansui_variant_set"
    ].review_status == "canonical_variant_selected"
    assert items_by_id[
        "bazi_general_variant_review_ditiansui_variant_set"
    ].decision == "select_canonical_variant"
    assert items_by_id[
        "bazi_general_variant_review_ditiansui_variant_set"
    ].canonical_choice_status == "selected_for_registration_prep"
    assert items_by_id[
        "bazi_general_variant_review_ditiansui_variant_set"
    ].selected_local_reference == "滴天髓.pdf"
    assert items_by_id[
        "bazi_general_variant_review_ditiansui_variant_set"
    ].local_references == [
        "滴天髓.pdf",
        "滴天髓-刘伯温注.pdf",
        "滴天髓白话浅释  164P.pdf",
    ]
    assert items_by_id[
        "bazi_general_variant_review_qiongtong_variant_set"
    ].identity_review_id == "bazi_general_identity_qiongtong_variant_set"
    assert items_by_id[
        "bazi_general_variant_review_qiongtong_variant_set"
    ].review_kind == "variant_choice"
    assert items_by_id[
        "bazi_general_variant_review_qiongtong_variant_set"
    ].review_status == "canonical_variant_selected"
    assert items_by_id[
        "bazi_general_variant_review_qiongtong_variant_set"
    ].decision == "select_canonical_variant"
    assert items_by_id[
        "bazi_general_variant_review_qiongtong_variant_set"
    ].canonical_choice_status == "selected_for_registration_prep"
    assert items_by_id[
        "bazi_general_variant_review_qiongtong_variant_set"
    ].selected_local_reference == "穷通宝鉴/窮通寶鑒.pdf"
    assert items_by_id[
        "bazi_general_deferred_review_huntian_baolan_ziping"
    ].identity_review_id == "bazi_general_identity_huntian_baolan_ziping"
    assert items_by_id[
        "bazi_general_deferred_review_huntian_baolan_ziping"
    ].review_kind == "deferred_large_source"
    assert items_by_id[
        "bazi_general_deferred_review_huntian_baolan_ziping"
    ].decision == "keep_large_source_deferred"
    assert items_by_id[
        "bazi_general_deferred_review_huntian_baolan_ziping"
    ].canonical_choice_status == "not_applicable"
    assert items_by_id[
        "bazi_general_deferred_review_huntian_baolan_ziping"
    ].selected_local_reference == ""
    assert all(item.selected_source_library_entry_id == "" for item in items)
    assert all(item.source_library_mutation_authorized is False for item in items)
    assert all(item.downstream_mutation_authorized is False for item in items)


def test_bazi_general_variant_deferred_review_summary_closes_residual_surface():
    summary = materials_audit.build_bazi_general_variant_deferred_review_summary()

    assert summary.review_id == "015-bazi-general-variant-choice-and-deferred-review"
    assert summary.review_status == "variant_deferred_review_completed"
    assert summary.triage_group_id == "raw_text_triage_bazi_general"
    assert summary.review_item_count == 3
    assert summary.variant_review_item_count == 2
    assert summary.deferred_review_item_count == 1
    assert summary.selected_canonical_variant_count == 2
    assert summary.source_library_registration_authorized_count == 0
    assert summary.variant_review_item_ids == [
        "bazi_general_variant_review_ditiansui_variant_set",
        "bazi_general_variant_review_qiongtong_variant_set",
    ]
    assert summary.deferred_review_item_ids == [
        "bazi_general_deferred_review_huntian_baolan_ziping",
    ]
    assert summary.selected_canonical_variant_ids == [
        "bazi_general_variant_review_ditiansui_variant_set",
        "bazi_general_variant_review_qiongtong_variant_set",
    ]
    assert summary.source_library_mutation_authorized is False
    assert summary.downstream_mutation_authorized is False
    assert summary.next_material_entry == (
        "015-bazi-general-selected-variant-registration-prep"
    )
    assert summary.boundary_checks == {
        "variant_deferred_items_loaded": "passed",
        "identity_review_references_valid": "passed",
        "source_selection_references_valid": "passed",
        "variant_records_match_identity_status": "passed",
        "deferred_records_match_identity_status": "passed",
        "source_paths_are_relative": "passed",
        "canonical_variant_choices_recorded": "passed",
        "source_library_not_mutated": "passed",
        "013_012_not_mutated": "passed",
        "raw_materials_not_mutated": "passed",
    }


def test_bazi_general_variant_deferred_review_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_bazi_general_variant_deferred_review_summary()
    markdown = materials_audit.render_bazi_general_variant_deferred_review_markdown(
        summary
    )
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Bazi General Variant Choice And Deferred Review",
        "`variant-deferred-review-status=variant_deferred_review_completed`",
        "`variant-deferred-review-items=3`",
        "`variant-review-items=2`",
        "`deferred-review-items=1`",
        "`selected-canonical-variants=2`",
        "`source-library-registration-authorized=0`",
        "`source-library-mutation-authorized=false`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-bazi-general-selected-variant-registration-prep`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff


def test_bazi_general_selected_variant_registration_chain_is_completed():
    records = materials_audit.load_material_audit_records()
    representations = materials_audit.load_material_representations()
    alignments = materials_audit.load_source_alignment_findings()
    readiness_findings = materials_audit.load_preparation_readiness_findings()
    queue_items = materials_audit.load_extraction_queue_items()

    records_by_id = {record.audit_id: record for record in records}
    representations_by_id = {
        representation.representation_id: representation
        for representation in representations
    }
    alignments_by_id = {alignment.alignment_id: alignment for alignment in alignments}
    readiness_by_id = {
        readiness.readiness_id: readiness for readiness in readiness_findings
    }
    queue_by_id = {item.queue_item_id: item for item in queue_items}

    expected = {
        "audit_bazi_general_ditiansui_selected_pdf": (
            "entry_bazi_general_ditiansui_selected_pdf",
            "material_bazi_general_ditiansui_selected_pdf",
            "滴天髓.pdf",
            "pattern_strength",
            "queue_bazi_general_ditiansui_pattern_strength_extract",
        ),
        "audit_bazi_general_qiongtong_selected_pdf": (
            "entry_bazi_general_qiongtong_selected_pdf",
            "material_bazi_general_qiongtong_selected_pdf",
            "穷通宝鉴/窮通寶鑒.pdf",
            "useful_god_candidate",
            "queue_bazi_general_qiongtong_useful_god_extract",
        ),
    }

    for audit_id, (
        entry_id,
        material_id,
        local_reference,
        rule_family,
        queue_id,
    ) in expected.items():
        record = records_by_id[audit_id]
        assert record.source_library_entry_id == entry_id
        assert record.source_boundary == "external_untracked"
        assert record.preparation_state == "ready_for_extraction_review"
        assert record.risk_tier == "ordinary"
        assert rule_family in record.rule_families

        representation = representations_by_id[f"repr_{audit_id.removeprefix('audit_')}"]
        assert representation.audit_id == audit_id
        assert representation.local_reference == local_reference
        assert representation.tracking_status == "external_untracked"

        alignment = alignments_by_id[f"align_{audit_id.removeprefix('audit_')}"]
        assert alignment.audit_id == audit_id
        assert alignment.source_library_entry_id == entry_id
        assert alignment.source_material_id == material_id

        readiness = readiness_by_id[f"ready_{audit_id.removeprefix('audit_')}"]
        assert readiness.audit_id == audit_id
        assert readiness.readiness_state == "ready_for_extraction_review"
        assert readiness.source_quality == "weak"
        assert readiness.risk_boundary == "ordinary"

        queue_item = queue_by_id[queue_id]
        assert queue_item.audit_id == audit_id
        assert queue_item.queue_type == "extraction_ready"
        assert queue_item.status == "completed"
        assert queue_item.target_rule_families == [rule_family]


def test_raw_text_source_registration_markdown_and_docs_are_in_sync():
    summary = materials_audit.build_raw_text_source_registration_summary()
    markdown = materials_audit.render_raw_text_source_registration_markdown(summary)
    materials_doc = Path("docs/classical_sources/materials_audit.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "015 Bazi General Source Registration",
        "`source-registration-status=source_registration_completed`",
        "`registered-source-entries=3`",
        "`registered-source-files=4`",
        "`skipped-existing-batch-overlap=2`",
        "`blocked-variant-choice=2`",
        "`deferred-large-source=1`",
        "`source-library-mutation-authorized=true`",
        "`downstream-mutation-authorized=false`",
        "`next-material-entry=015-bazi-general-source-preparation-reading`",
    ):
        assert marker in markdown
        assert marker in materials_doc
        assert marker in handoff
