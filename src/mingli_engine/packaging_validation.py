from __future__ import annotations

import csv
from dataclasses import dataclass
from hashlib import sha256
from io import StringIO
from importlib import metadata, resources
from importlib.resources.abc import Traversable
import json
from pathlib import Path
import re
import sys
from typing import Iterator


_DISTRIBUTION_NAME = "mingli-engine"
_VERSION_PATTERN = re.compile(
    r"^[0-9]+(?:\.[0-9]+)*(?:(?:a|b|rc)[0-9]+)?"
    r"(?:\.post[0-9]+)?(?:\.dev[0-9]+)?"
    r"(?:\+[a-z0-9]+(?:[._-][a-z0-9]+)*)?$",
    re.IGNORECASE,
)
EXPECTED_RUNTIME_JSON_ASSETS = (
    "data/calculation/school_profiles.json",
    "data/calculation/strength_weights.json",
    "data/classical_sources/curation_batches.json",
    "data/classical_sources/evidence_units.json",
    "data/classical_sources/source_conflicts.json",
    "data/classical_sources/sources.json",
    "data/extraction_queue_intake/candidate_draft_slots.json",
    "data/extraction_queue_intake/extraction_tasks.json",
    "data/extraction_queue_intake/extraction_work_packages.json",
    "data/extraction_queue_intake/prerequisite_backlog_records.json",
    "data/learning_reference_curation/candidate_intake_decisions.json",
    "data/learning_reference_curation/downstream_authorization_receipts.json",
    "data/learning_reference_curation/learning_points.json",
    "data/learning_reference_curation/learning_reference_notes.json",
    "data/learning_reference_curation/new_material_corrected_pilot_learning_completion_review_items.json",
    "data/learning_reference_curation/new_material_corrected_pilot_learning_entry_evaluation_items.json",
    "data/learning_reference_curation/new_material_corrected_pilot_learning_note_draft_items.json",
    "data/learning_reference_curation/new_material_corrected_pilot_learning_note_prep_items.json",
    "data/learning_reference_curation/new_material_expanded_corrected_learning_completion_review_items.json",
    "data/learning_reference_curation/new_material_expanded_corrected_learning_entry_evaluation_items.json",
    "data/learning_reference_curation/new_material_expanded_corrected_learning_note_draft_items.json",
    "data/learning_reference_curation/new_material_expanded_corrected_learning_note_prep_items.json",
    "data/learning_reference_curation/prerequisite_action_notes.json",
    "data/materials_audit/bazi_general_variant_deferred_review_items.json",
    "data/materials_audit/explicit_candidate_review_or_queue_refresh_items.json",
    "data/materials_audit/external_material_inventory_refresh_confirmation_items.json",
    "data/materials_audit/extraction_queue_items.json",
    "data/materials_audit/material_audit_records.json",
    "data/materials_audit/material_representations.json",
    "data/materials_audit/new_material_controlled_text_preparation_items.json",
    "data/materials_audit/new_material_expanded_corrected_transcription_execution_items.json",
    "data/materials_audit/new_material_expanded_corrected_transcription_prep_items.json",
    "data/materials_audit/new_material_expanded_corrected_transcription_selection_items.json",
    "data/materials_audit/new_material_extraction_learning_loop_closure_items.json",
    "data/materials_audit/new_material_human_corrected_transcription_execution_items.json",
    "data/materials_audit/new_material_human_corrected_transcription_prep_items.json",
    "data/materials_audit/new_material_intake_items.json",
    "data/materials_audit/new_material_ocr_or_manual_transcription_items.json",
    "data/materials_audit/new_material_ocr_quality_remediation_items.json",
    "data/materials_audit/new_material_ocr_runtime_setup_items.json",
    "data/materials_audit/new_material_preparation_boundary_items.json",
    "data/materials_audit/new_material_registration_prep_items.json",
    "data/materials_audit/new_material_source_identity_review_items.json",
    "data/materials_audit/new_material_source_registration_items.json",
    "data/materials_audit/preparation_readiness_findings.json",
    "data/materials_audit/raw_text_cluster_source_selection_items.json",
    "data/materials_audit/raw_text_material_triage_groups.json",
    "data/materials_audit/raw_text_next_cycle_cluster_source_selection_items.json",
    "data/materials_audit/raw_text_next_cycle_followup_selection_items.json",
    "data/materials_audit/raw_text_next_cycle_gated_cluster_review_prep_items.json",
    "data/materials_audit/raw_text_next_cycle_gated_ordinary_final_selection_items.json",
    "data/materials_audit/raw_text_next_cycle_gated_ordinary_followup_selection_items.json",
    "data/materials_audit/raw_text_next_cycle_gated_ordinary_source_selection_items.json",
    "data/materials_audit/raw_text_next_cycle_identity_review_items.json",
    "data/materials_audit/raw_text_next_cycle_sensitive_preparation_boundary_items.json",
    "data/materials_audit/raw_text_next_cycle_sensitive_preparation_reading_items.json",
    "data/materials_audit/raw_text_next_cycle_sensitive_registration_prep_items.json",
    "data/materials_audit/raw_text_next_cycle_sensitive_risk_review_prep_items.json",
    "data/materials_audit/raw_text_next_cycle_sensitive_source_level_risk_review_items.json",
    "data/materials_audit/raw_text_next_cycle_sensitive_source_registration_items.json",
    "data/materials_audit/raw_text_next_cycle_source_selection_items.json",
    "data/materials_audit/raw_text_source_cluster_selection_items.json",
    "data/materials_audit/raw_text_source_identity_review_items.json",
    "data/materials_audit/raw_text_source_registration_prep_items.json",
    "data/materials_audit/raw_text_source_selection_items.json",
    "data/materials_audit/source_alignment_findings.json",
    "data/source_intake/candidate_extracts.json",
    "data/source_intake/promotion_batches.json",
    "data/source_intake/review_decisions.json",
    "data/source_intake/source_materials.json",
    "data/source_library/curation_batch_plans.json",
    "data/source_library/source_library_entries.json",
    "data/source_library/source_priority_assessments.json",
)


@dataclass(frozen=True)
class PackagingVerification:
    asset_sha256: dict[str, str]
    distribution_version: str
    source_isolated: bool
    overall_status: str


def _iter_json_assets(
    directory: Traversable,
    relative_directory: str,
) -> Iterator[tuple[str, bytes]]:
    for child in sorted(directory.iterdir(), key=lambda item: item.name):
        relative_path = f"{relative_directory}/{child.name}"
        if child.is_dir():
            yield from _iter_json_assets(child, relative_path)
        elif child.is_file() and child.name.endswith(".json"):
            yield relative_path, child.read_bytes()


def _load_asset_hashes(package_root: Traversable) -> tuple[dict[str, str], bool]:
    try:
        assets = {
            relative_path: sha256(payload).hexdigest()
            for relative_path, payload in _iter_json_assets(
                package_root.joinpath("data"),
                "data",
            )
        }
    except Exception:
        return {}, False
    return assets, tuple(assets) == EXPECTED_RUNTIME_JSON_ASSETS


def _iter_python_modules(
    directory: Traversable,
    relative_directory: str = "",
) -> Iterator[str]:
    for child in sorted(directory.iterdir(), key=lambda item: item.name):
        relative_path = (
            f"{relative_directory}/{child.name}"
            if relative_directory
            else child.name
        )
        if child.is_dir():
            yield from _iter_python_modules(child, relative_path)
        elif child.is_file() and child.name.endswith(".py"):
            yield f"mingli_engine/{relative_path}"


def _expected_distribution_files(
    package_root: Traversable | None,
) -> frozenset[str] | None:
    if package_root is None:
        return None
    try:
        modules = frozenset(_iter_python_modules(package_root))
    except Exception:
        return None
    if "mingli_engine/packaging_validation.py" not in modules:
        return None
    runtime_assets = {
        f"mingli_engine/{path}" for path in EXPECTED_RUNTIME_JSON_ASSETS
    }
    return modules | runtime_assets


def _normalized_distribution_name(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return re.sub(r"[-_.]+", "-", value.strip()).lower()


def _valid_distribution_version(value: object) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip():
        return None
    return value if _VERSION_PATTERN.fullmatch(value) else None


def _record_paths(record: str) -> frozenset[str] | None:
    try:
        rows = tuple(csv.reader(StringIO(record)))
    except (csv.Error, TypeError):
        return None
    if not rows or any(not row or not row[0] for row in rows):
        return None
    return frozenset(row[0].replace("\\", "/") for row in rows)


def _contains_dist_info_file(paths: frozenset[str], filename: str) -> bool:
    return any(path.endswith(f".dist-info/{filename}") for path in paths)


def _valid_direct_url(distribution: metadata.Distribution) -> bool:
    direct_url = distribution.read_text("direct_url.json")
    if direct_url is None:
        return True
    try:
        payload = json.loads(direct_url)
    except (TypeError, ValueError):
        return False
    if not isinstance(payload, dict):
        return False
    dir_info = payload.get("dir_info")
    if not isinstance(dir_info, dict) or "editable" not in dir_info:
        return False
    editable = dir_info["editable"]
    return isinstance(editable, bool) and editable is False


def _valid_wheel_metadata(
    distribution: metadata.Distribution,
    expected_package_files: frozenset[str] | None,
) -> bool:
    if expected_package_files is None:
        return False
    wheel_metadata = distribution.read_text("WHEEL")
    record = distribution.read_text("RECORD")
    if not wheel_metadata or not record:
        return False
    distribution_files = distribution.files
    if distribution_files is None:
        return False
    file_paths = frozenset(
        str(path).replace("\\", "/") for path in distribution_files
    )
    recorded_paths = _record_paths(record)
    if recorded_paths is None:
        return False
    metadata_files_present = all(
        _contains_dist_info_file(file_paths, filename)
        and _contains_dist_info_file(recorded_paths, filename)
        for filename in ("WHEEL", "RECORD")
    )
    return (
        metadata_files_present
        and expected_package_files.issubset(file_paths)
        and expected_package_files.issubset(recorded_paths)
        and _valid_direct_url(distribution)
    )


def _load_distribution(
    expected_package_files: frozenset[str] | None,
) -> tuple[str, Path | None, Path | None, bool]:
    try:
        distribution = metadata.distribution(_DISTRIBUTION_NAME)
        distribution_name = _normalized_distribution_name(
            distribution.metadata.get("Name")
        )
        metadata_version = _valid_distribution_version(
            distribution.metadata.get("Version")
        )
        distribution_version = _valid_distribution_version(distribution.version)
        if (
            distribution_name != _DISTRIBUTION_NAME
            or metadata_version is None
            or distribution_version != metadata_version
        ):
            raise ValueError("invalid distribution identity")
        distribution_root = Path(str(distribution.locate_file(""))).resolve()
        installed_package_root = Path(
            str(distribution.locate_file("mingli_engine"))
        ).resolve()
        valid_wheel_metadata = _valid_wheel_metadata(
            distribution,
            expected_package_files,
        )
    except Exception:
        return "not_installed", None, None, False
    return (
        distribution_version,
        distribution_root,
        installed_package_root,
        valid_wheel_metadata,
    )


def _loaded_package_paths() -> tuple[Path, ...]:
    paths: list[Path] = []
    for module_name, module in sorted(sys.modules.items()):
        if module_name != "mingli_engine" and not module_name.startswith(
            "mingli_engine."
        ):
            continue
        module_file = getattr(module, "__file__", None)
        if module_file is not None:
            paths.append(Path(module_file).resolve())
    return tuple(paths)


def _is_source_isolated(
    *,
    package_root: Traversable | None,
    distribution_root: Path | None,
    metadata_package_root: Path | None,
    valid_wheel_metadata: bool,
) -> bool:
    if (
        package_root is None
        or distribution_root is None
        or metadata_package_root is None
        or not valid_wheel_metadata
    ):
        return False
    try:
        resource_root = Path(str(package_root)).resolve()
        module_paths = _loaded_package_paths()
    except Exception:
        return False
    return (
        resource_root == metadata_package_root
        and metadata_package_root.is_relative_to(distribution_root)
        and bool(module_paths)
        and all(path.is_relative_to(metadata_package_root) for path in module_paths)
    )


def build_packaging_verification() -> PackagingVerification:
    try:
        package_root: Traversable | None = resources.files("mingli_engine")
    except Exception:
        package_root = None

    if package_root is None:
        assets: dict[str, str] = {}
        manifest_complete = False
    else:
        assets, manifest_complete = _load_asset_hashes(package_root)
    expected_distribution_files = _expected_distribution_files(package_root)

    (
        distribution_version,
        distribution_root,
        metadata_package_root,
        valid_wheel_metadata,
    ) = _load_distribution(expected_distribution_files)
    source_isolated = _is_source_isolated(
        package_root=package_root,
        distribution_root=distribution_root,
        metadata_package_root=metadata_package_root,
        valid_wheel_metadata=valid_wheel_metadata,
    )
    verified = (
        manifest_complete
        and distribution_version != "not_installed"
        and source_isolated
    )
    return PackagingVerification(
        asset_sha256=assets,
        distribution_version=distribution_version,
        source_isolated=source_isolated,
        overall_status="verified" if verified else "failed",
    )
