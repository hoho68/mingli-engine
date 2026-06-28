import json
from collections import Counter
import re
import shutil
import time
from pathlib import Path

import pytest

from mingli_engine import classical_sources
from mingli_engine import learning_reference_curation
from mingli_engine import models
from mingli_engine import source_intake


PROJECT_DATA_DIR = Path(__file__).resolve().parents[2] / "src" / "mingli_engine" / "data"
CONTEXT_DATA_DIRS = (
    "extraction_queue_intake",
    "materials_audit",
    "source_library",
    "source_intake",
)
SOURCE_WINDOW_CLOSURE_EXTRACTS = (
    Path("docs/classical_sources/extracts/duan_plain_mingxue_outline.md"),
    Path("docs/classical_sources/extracts/fortune_reading_hongfu_qitian.md"),
    Path("docs/classical_sources/extracts/northeast_blind_peak.md"),
)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _source_window_learning_closure_counts() -> dict[str, int]:
    closure_counts: Counter[str] = Counter()
    for extract_path in SOURCE_WINDOW_CLOSURE_EXTRACTS:
        extract = extract_path.read_text(encoding="utf-8")
        closure_counts.update(
            re.findall(r"Learning closure note: `learning-closure:([^;`]+)", extract)
        )
    return dict(closure_counts)


def _write_learning_reference_fixture(
    tmp_path: Path,
    *,
    notes: list[dict[str, object]] | None = None,
    learning_points: list[dict[str, object]] | None = None,
    decisions: list[dict[str, object]] | None = None,
    action_notes: list[dict[str, object]] | None = None,
) -> Path:
    data_dir = tmp_path / "learning_reference_curation"
    data_dir.mkdir(exist_ok=True)
    _write_json(data_dir / "learning_reference_notes.json", notes or [])
    _write_json(data_dir / "learning_points.json", learning_points or [])
    _write_json(data_dir / "candidate_intake_decisions.json", decisions or [])
    _write_json(data_dir / "prerequisite_action_notes.json", action_notes or [])
    return data_dir


def _remove_unapplied_candidate_records(
    intake_dir: Path,
    decisions: list[dict[str, object]] | None,
) -> set[str]:
    if decisions is None:
        return set()
    unapplied_candidate_ids = {
        str(decision.get("candidate_id"))
        for decision in decisions
        if decision.get("decision") == "create_candidate"
        and decision.get("status", "planned") != "applied"
        and decision.get("candidate_id")
    }
    if not unapplied_candidate_ids:
        return set()
    candidate_path = intake_dir / "candidate_extracts.json"
    candidates = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidates = [
        candidate
        for candidate in candidates
        if candidate["candidate_id"] not in unapplied_candidate_ids
    ]
    _write_json(candidate_path, candidates)
    return unapplied_candidate_ids


def _remove_unapplied_candidate_overlap_warnings(
    extraction_dir: Path,
    candidate_ids: set[str],
) -> None:
    if not candidate_ids:
        return
    task_path = extraction_dir / "extraction_tasks.json"
    tasks = json.loads(task_path.read_text(encoding="utf-8"))
    for task in tasks:
        task["overlap_warnings"] = [
            warning
            for warning in task.get("overlap_warnings", [])
            if not any(candidate_id in warning for candidate_id in candidate_ids)
        ]
    _write_json(task_path, tasks)


def _strip_unapplied_candidate_ids_from_notes(
    notes: list[dict[str, object]] | None,
    candidate_ids: set[str],
) -> list[dict[str, object]] | None:
    if notes is None or not candidate_ids:
        return notes
    stripped_notes: list[dict[str, object]] = []
    for note in notes:
        stripped_note = dict(note)
        stripped_note["overlap_candidate_ids"] = [
            candidate_id
            for candidate_id in note.get("overlap_candidate_ids", [])
            if candidate_id not in candidate_ids
        ]
        stripped_notes.append(stripped_note)
    return stripped_notes


def _copy_learning_reference_project_fixture(
    tmp_path: Path,
    *,
    notes: list[dict[str, object]] | None = None,
    learning_points: list[dict[str, object]] | None = None,
    decisions: list[dict[str, object]] | None = None,
    action_notes: list[dict[str, object]] | None = None,
) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    for dirname in CONTEXT_DATA_DIRS:
        shutil.copytree(PROJECT_DATA_DIR / dirname, tmp_path / dirname)
    removed_candidate_ids = _remove_unapplied_candidate_records(
        tmp_path / "source_intake",
        decisions,
    )
    _remove_unapplied_candidate_overlap_warnings(
        tmp_path / "extraction_queue_intake",
        removed_candidate_ids,
    )
    notes = _strip_unapplied_candidate_ids_from_notes(notes, removed_candidate_ids)
    return _write_learning_reference_fixture(
        tmp_path,
        notes=notes,
        learning_points=learning_points,
        decisions=decisions,
        action_notes=action_notes,
    )


def _valid_learning_reference_notes() -> list[dict[str, object]]:
    return [
        {
            "note_id": "note_northeast_blind_peak_001",
            "task_id": "task_northeast_blind_peak_extract_001",
            "package_id": "package_next_candidates_001",
            "queue_item_id": "queue_northeast_blind_peak_extract",
            "audit_id": "audit_northeast_blind_peak",
            "source_library_entry_id": "entry_northeast_blind_peak_pdf",
            "source_material_id": "material_northeast_blind_peak_pdf",
            "source_title": "Northeast Blind Peak",
            "target_rule_families": [
                "blind_image_method",
                "branch_interaction",
            ],
            "locator_requirement": "page_or_section",
            "risk_boundary": "sensitive",
            "rights_note": "Do not copy long passages; store concise paraphrases only.",
            "source_quality_note": (
                "Confirm page or section locator before manual extraction."
            ),
            "learning_points": ["lp_northeast_blind_image_001"],
            "overlap_candidate_ids": [
                "candidate_northeast_blind_image_001",
                "candidate_northeast_blind_image_duplicate_001",
            ],
            "status": "draft",
            "created_at": "2026-05-31",
            "updated_at": "2026-05-31",
        },
        {
            "note_id": "note_mingli_true_formula_teacher_001",
            "task_id": "task_mingli_true_formula_teacher_extract_001",
            "package_id": "package_next_candidates_001",
            "queue_item_id": "queue_mingli_true_formula_teacher_extract",
            "audit_id": "audit_mingli_true_formula_teacher",
            "source_library_entry_id": "entry_mingli_true_formula_teacher_pdf",
            "source_material_id": "material_mingli_true_formula_teacher_pdf",
            "source_title": "Mingli True Formula Teacher",
            "target_rule_families": [
                "pattern_strength",
                "useful_god_candidate",
                "luck_cycle",
            ],
            "locator_requirement": "page_or_section",
            "risk_boundary": "sensitive",
            "rights_note": "Do not copy long passages; store concise paraphrases only.",
            "source_quality_note": "Confirm locator anchors before manual extraction.",
            "learning_points": ["lp_mingli_pattern_strength_001"],
            "overlap_candidate_ids": [
                "candidate_mingli_pattern_strength_017_001"
            ],
            "status": "draft",
            "created_at": "2026-05-31",
            "updated_at": "2026-05-31",
        },
    ]


def _valid_learning_points() -> list[dict[str, object]]:
    return [
        {
            "learning_point_id": "lp_northeast_blind_image_001",
            "note_id": "note_northeast_blind_peak_001",
            "point_label": "Blind image method conditional signal",
            "source_locator": "page_or_section_required",
            "summary": (
                "Blind image statements should be framed as conditional traditional "
                "signals tied to chart structure."
            ),
            "proposed_rule_family": "blind_image_method",
            "risk_tier": "sensitive",
            "limitations": [
                "State uncertainty and school dependency.",
                "Include limitation language; do not use as standalone verdict.",
            ],
            "candidate_readiness": "duplicate_review",
            "candidate_decision_id": "decision_northeast_blind_image_001",
        },
        {
            "learning_point_id": "lp_mingli_pattern_strength_001",
            "note_id": "note_mingli_true_formula_teacher_001",
            "point_label": "Pattern strength candidate framing",
            "source_locator": "page_or_section_required",
            "summary": (
                "Pattern strength material should stay conditional until source "
                "locator and chart context are reviewed."
            ),
            "proposed_rule_family": "pattern_strength",
            "risk_tier": "sensitive",
            "limitations": [
                "State uncertainty for timing and pattern interpretation.",
                "Include limitation language; do not guarantee outcome timing.",
            ],
            "candidate_readiness": "ready",
            "candidate_decision_id": "decision_mingli_pattern_strength_001",
        },
    ]


def _valid_candidate_intake_decisions() -> list[dict[str, object]]:
    return [
        {
            "decision_id": "decision_northeast_blind_image_001",
            "learning_point_id": "lp_northeast_blind_image_001",
            "decision": "manual_review",
            "source_material_id": "material_northeast_blind_peak_pdf",
            "candidate_id": "",
            "overlap_candidate_ids": [
                "candidate_northeast_blind_image_001",
                "candidate_northeast_blind_image_duplicate_001",
            ],
            "rationale": (
                "Existing pending and rejected candidates overlap this source and "
                "rule family; reviewer must decide reuse or replacement."
            ),
            "status": "planned",
            "created_at": "2026-05-31",
            "updated_at": "2026-05-31",
        },
        {
            "decision_id": "decision_mingli_pattern_strength_001",
            "learning_point_id": "lp_mingli_pattern_strength_001",
            "decision": "create_candidate",
            "source_material_id": "material_mingli_true_formula_teacher_pdf",
            "candidate_id": "candidate_mingli_pattern_strength_017_001",
            "overlap_candidate_ids": [],
            "rationale": (
                "No existing 013 candidate overlaps this source and rule family; "
                "create a planned candidate only after manual extraction."
            ),
            "status": "planned",
            "created_at": "2026-05-31",
            "updated_at": "2026-05-31",
        },
    ]


def _valid_prerequisite_action_notes() -> list[dict[str, object]]:
    return [
        {
            "action_note_id": "action_blind_life_manual_risk_review_001",
            "backlog_id": "backlog_blind_life_manual_risk_review_001",
            "package_id": "package_next_candidates_001",
            "queue_item_id": "queue_blind_life_manual_risk_review",
            "audit_id": "audit_blind_life_manual",
            "action_type": "risk_review",
            "missing_prerequisites": ["risk_review"],
            "durable_reason": (
                "Boundary screening completed: aphoristic high-risk material "
                "stays prerequisite-only and no routine extraction task is "
                "created."
            ),
            "recommended_action": "risk_review",
            "risk_boundary": "high_risk",
            "status": "completed",
            "created_at": "2026-05-31",
            "updated_at": "2026-06-27",
        },
        {
            "action_note_id": "action_blind_school_secret_blocked_001",
            "backlog_id": "backlog_blind_school_secret_blocked_001",
            "package_id": "package_next_candidates_001",
            "queue_item_id": "queue_blind_school_secret_blocked",
            "audit_id": "audit_blind_school_secret",
            "action_type": "blocked",
            "missing_prerequisites": [
                "source_access_clarification",
                "quotation_boundary_review",
            ],
            "durable_reason": (
                "Source remains blocked until access and quotation boundaries are "
                "clarified."
            ),
            "recommended_action": "block",
            "risk_boundary": "sensitive",
            "status": "blocked",
            "created_at": "2026-05-31",
            "updated_at": "2026-05-31",
        },
    ]


def test_learning_reference_curation_constants_cover_contract_values():
    assert models.LEARNING_REFERENCE_NOTE_STATUSES == frozenset(
        {
            "draft",
            "ready_for_candidate_intake",
            "candidate_intake_started",
            "deferred",
            "blocked",
        }
    )
    assert models.LEARNING_POINT_READINESSES == frozenset(
        {
            "ready",
            "needs_locator",
            "needs_risk_review",
            "duplicate_review",
            "deferred",
            "blocked",
        }
    )
    assert models.CANDIDATE_INTAKE_DECISIONS == frozenset(
        {
            "create_candidate",
            "reuse_existing",
            "avoid_duplicate",
            "defer",
            "manual_review",
        }
    )
    assert models.CANDIDATE_INTAKE_DECISION_STATUSES == frozenset(
        {"planned", "applied", "deferred", "blocked"}
    )
    assert models.PREREQUISITE_ACTION_TYPES == frozenset(
        {
            "registration",
            "preparation",
            "locator_review",
            "risk_review",
            "deferred",
            "blocked",
        }
    )
    assert models.PREREQUISITE_ACTION_STATUSES == frozenset(
        {"planned", "active", "completed", "deferred", "blocked"}
    )
    assert models.LEARNING_REFERENCE_MANUAL_ACTIONS == frozenset(
        {
            "create_candidate",
            "reuse_existing",
            "avoid_duplicate",
            "manual_review",
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


def test_package_exports_learning_reference_workflow_modules():
    import mingli_engine

    assert {
        "source_intake",
        "source_library",
        "materials_audit",
        "extraction_queue_intake",
        "learning_reference_curation",
    }.issubset(set(mingli_engine.__all__))


def test_loader_reports_missing_file(tmp_path):
    data_dir = tmp_path / "learning_reference_curation"
    data_dir.mkdir()

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="missing data file",
    ):
        learning_reference_curation.load_learning_reference_notes(data_dir)


def test_loader_reports_malformed_json(tmp_path):
    data_dir = tmp_path / "learning_reference_curation"
    data_dir.mkdir()
    (data_dir / "learning_reference_notes.json").write_text("{", encoding="utf-8")

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="invalid JSON",
    ):
        learning_reference_curation.load_learning_reference_notes(data_dir)


def test_loader_requires_json_array(tmp_path):
    data_dir = tmp_path / "learning_reference_curation"
    data_dir.mkdir()
    _write_json(data_dir / "learning_reference_notes.json", {})

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="JSON array",
    ):
        learning_reference_curation.load_learning_reference_notes(data_dir)


def test_loader_requires_json_object_entries(tmp_path):
    data_dir = tmp_path / "learning_reference_curation"
    data_dir.mkdir()
    _write_json(data_dir / "learning_reference_notes.json", ["note_001"])

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="JSON objects",
    ):
        learning_reference_curation.load_learning_reference_notes(data_dir)


def test_public_loader_stubs_return_empty_collections(tmp_path):
    data_dir = _write_learning_reference_fixture(tmp_path)

    assert learning_reference_curation.load_learning_reference_notes(data_dir) == []
    assert learning_reference_curation.load_learning_points(data_dir) == []
    assert learning_reference_curation.load_candidate_intake_decisions(data_dir) == []
    assert learning_reference_curation.load_prerequisite_action_notes(data_dir) == []
    assert learning_reference_curation.validate_learning_reference_quality(data_dir) == []

    summary = learning_reference_curation.build_learning_reference_progress_summary(
        data_dir
    )

    assert summary == models.LearningReferenceProgressSummary(
        note_counts={},
        learning_point_counts={},
        decision_counts={},
        prerequisite_action_counts={},
        risk_tier_counts={},
        overlap_warning_count=0,
        candidate_ready_count=0,
        candidate_decision_count=0,
        formal_evidence_delta=0,
        next_action_ids=[],
    )


def test_learning_reference_summary_loads_under_300ms(tmp_path):
    data_dir = _write_learning_reference_fixture(tmp_path)

    started_at = time.perf_counter()
    summary = learning_reference_curation.build_learning_reference_progress_summary(
        data_dir
    )
    elapsed = time.perf_counter() - started_at

    assert elapsed < 0.3
    assert summary.candidate_ready_count == 0
    assert summary.formal_evidence_delta == 0


def test_seeded_learning_reference_notes_load_for_current_ready_016_tasks():
    notes = learning_reference_curation.load_learning_reference_notes()

    assert [note.task_id for note in notes] == [
        "task_northeast_blind_peak_extract_001",
        "task_mingli_true_formula_teacher_extract_001",
        "task_duan_plain_mingxue_outline_extract_001",
        "task_mingxue_golden_voice_extract_001",
        "task_fortune_reading_hongfu_qitian_extract_001",
        "task_markdown_batch_002_core_extract_001",
        "task_markdown_batch_001_extract_001",
        "task_markdown_batch_004_extract_001",
        "task_kskeleton_q001_foundation_tables_001",
        "task_kskeleton_q002_yongshen_tiaohou_001",
        "task_kskeleton_q003_geju_strength_001",
        "task_kskeleton_q006_branch_interaction_001",
        "task_kskeleton_q004_luck_cycle_001",
        "task_kskeleton_q008_high_risk_boundary_001",
        "task_markdown_batch_004_extract_001",
        "task_markdown_batch_004_extract_001",
        "task_bazi_general_lecture_pattern_strength_001",
        "task_bazi_general_beichen_branch_interaction_001",
        "task_bazi_general_ziping_useful_god_001",
        "task_bazi_general_ditiansui_pattern_strength_001",
        "task_bazi_general_qiongtong_useful_god_001",
        "task_bazi_general_true_spirit_useful_god_001",
        "task_bazi_general_wangdoujing_branch_interaction_001",
        "task_bazi_general_xinpai_essence_pattern_strength_001",
        "task_bazi_general_xingming_shuozheng_branch_interaction_001",
    ]
    assert [note.note_id for note in notes] == [
       "note_northeast_blind_peak_001",
       "note_mingli_true_formula_teacher_001",
       "note_duan_plain_mingxue_outline_001",
       "note_mingxue_golden_voice_001",
       "note_fortune_reading_hongfu_qitian_001",
       "note_markdown_batch_002_useful_god_001",
       "note_markdown_batch_001_pattern_strength_001",
       "note_markdown_batch_004_001",
       "note_kskeleton_q001_foundation_tables_001",
       "note_kskeleton_q002_yongshen_tiaohou_001",
       "note_kskeleton_q003_geju_strength_001",
       "note_kskeleton_q006_branch_interaction_001",
       "note_kskeleton_q004_luck_cycle_001",
       "note_kskeleton_q008_high_risk_boundary_001",
       "note_liang_tianyuan_wuxian_individual_review_001",
       "note_liang_yushi_yongshen_individual_review_001",
       "note_bazi_general_lecture_pattern_strength_001",
       "note_bazi_general_beichen_branch_interaction_001",
       "note_bazi_general_ziping_useful_god_001",
       "note_bazi_general_ditiansui_pattern_strength_001",
       "note_bazi_general_qiongtong_useful_god_001",
       "note_bazi_general_true_spirit_useful_god_001",
       "note_bazi_general_wangdoujing_branch_interaction_001",
       "note_bazi_general_xinpai_essence_pattern_strength_001",
       "note_bazi_general_xingming_shuozheng_branch_interaction_001",
    ]
    assert all(
        note.status == "candidate_intake_started"
        for note in notes
    )
    assert all(note.learning_points for note in notes)
    assert all(note.learning_points for note in notes)
    assert notes[0].source_material_id == "material_northeast_blind_peak_pdf"
    assert notes[1].source_material_id == "material_mingli_true_formula_teacher_pdf"
    assert notes[2].source_material_id == "material_duan_plain_mingxue_outline_pdf"
    assert notes[2].overlap_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert notes[3].source_material_id == "material_mingxue_golden_voice_pdf"
    assert notes[3].overlap_candidate_ids == [
        "candidate_mingxue_golden_voice_scope_001",
        "candidate_mingxue_five_element_balance_017_001",
    ]
    assert notes[4].source_material_id == (
        "material_fortune_reading_hongfu_qitian_pdf"
    )
    assert notes[4].overlap_candidate_ids == [
        "candidate_hongfu_remedy_boundary_017_001"
    ]
    assert notes[5].source_material_id == (
        "material_markdown_source_batch_002_core"
    )
    assert notes[5].overlap_candidate_ids == []
    assert learning_reference_curation.validate_learning_reference_quality() == []


def test_bazi_general_source_preparation_reading_learning_notes_are_applied():
    notes = learning_reference_curation.load_learning_reference_notes()
    points = learning_reference_curation.load_learning_points()
    decisions = learning_reference_curation.load_candidate_intake_decisions()

    notes_by_id = {note.note_id: note for note in notes}
    points_by_id = {point.learning_point_id: point for point in points}
    decisions_by_id = {decision.decision_id: decision for decision in decisions}

    expected = {
        "note_bazi_general_lecture_pattern_strength_001": (
            "lp_bazi_general_lecture_pattern_strength_001",
            "decision_bazi_general_lecture_pattern_strength_001",
            "candidate_bazi_general_lecture_pattern_strength_001",
            "pattern_strength",
        ),
        "note_bazi_general_beichen_branch_interaction_001": (
            "lp_bazi_general_beichen_branch_interaction_001",
            "decision_bazi_general_beichen_branch_interaction_001",
            "candidate_bazi_general_beichen_branch_interaction_001",
            "branch_interaction",
        ),
        "note_bazi_general_ziping_useful_god_001": (
            "lp_bazi_general_ziping_useful_god_001",
            "decision_bazi_general_ziping_useful_god_001",
            "candidate_bazi_general_ziping_useful_god_001",
            "useful_god_candidate",
        ),
    }

    for note_id, (point_id, decision_id, candidate_id, rule_family) in expected.items():
        note = notes_by_id[note_id]
        point = points_by_id[point_id]
        decision = decisions_by_id[decision_id]

        assert note.status == "candidate_intake_started"
        assert note.learning_points == [point_id]
        assert note.risk_boundary == "ordinary"
        assert note.overlap_candidate_ids == []
        assert point.note_id == note_id
        assert point.proposed_rule_family == rule_family
        assert point.risk_tier == "ordinary"
        assert point.candidate_readiness == "ready"
        assert point.candidate_decision_id == decision_id
        assert decision.learning_point_id == point_id
        assert decision.decision == "create_candidate"
        assert decision.status == "applied"
        assert decision.candidate_id == candidate_id


def test_bazi_general_selected_variant_learning_notes_are_applied():
    notes = learning_reference_curation.load_learning_reference_notes()
    points = learning_reference_curation.load_learning_points()
    decisions = learning_reference_curation.load_candidate_intake_decisions()

    notes_by_id = {note.note_id: note for note in notes}
    points_by_id = {point.learning_point_id: point for point in points}
    decisions_by_id = {decision.decision_id: decision for decision in decisions}

    expected = {
        "note_bazi_general_ditiansui_pattern_strength_001": (
            "lp_bazi_general_ditiansui_pattern_strength_001",
            "decision_bazi_general_ditiansui_pattern_strength_001",
            "candidate_bazi_general_ditiansui_pattern_strength_001",
            "pattern_strength",
        ),
        "note_bazi_general_qiongtong_useful_god_001": (
            "lp_bazi_general_qiongtong_useful_god_001",
            "decision_bazi_general_qiongtong_useful_god_001",
            "candidate_bazi_general_qiongtong_useful_god_001",
            "useful_god_candidate",
        ),
    }

    for note_id, (point_id, decision_id, candidate_id, rule_family) in expected.items():
        note = notes_by_id[note_id]
        point = points_by_id[point_id]
        decision = decisions_by_id[decision_id]

        assert note.status == "candidate_intake_started"
        assert note.learning_points == [point_id]
        assert note.risk_boundary == "ordinary"
        assert note.locator_requirement == "page_or_section"
        assert note.overlap_candidate_ids == []
        assert point.note_id == note_id
        assert point.source_locator.startswith("page:")
        assert point.proposed_rule_family == rule_family
        assert point.risk_tier == "ordinary"
        assert point.candidate_readiness == "ready"
        assert point.candidate_decision_id == decision_id
        assert decision.learning_point_id == point_id
        assert decision.decision == "create_candidate"
        assert decision.status == "applied"
        assert decision.candidate_id == candidate_id


def test_bazi_general_next_cycle_cluster_source_learning_notes_are_applied():
    notes = learning_reference_curation.load_learning_reference_notes()
    points = learning_reference_curation.load_learning_points()
    decisions = learning_reference_curation.load_candidate_intake_decisions()

    notes_by_id = {note.note_id: note for note in notes}
    points_by_id = {point.learning_point_id: point for point in points}
    decisions_by_id = {decision.decision_id: decision for decision in decisions}

    expected = {
        "note_bazi_general_true_spirit_useful_god_001": (
            "lp_bazi_general_true_spirit_useful_god_001",
            "decision_bazi_general_true_spirit_useful_god_001",
            "candidate_bazi_general_true_spirit_useful_god_001",
            "useful_god_candidate",
        ),
        "note_bazi_general_wangdoujing_branch_interaction_001": (
            "lp_bazi_general_wangdoujing_branch_interaction_001",
            "decision_bazi_general_wangdoujing_branch_interaction_001",
            "candidate_bazi_general_wangdoujing_branch_interaction_001",
            "branch_interaction",
        ),
    }

    for note_id, (point_id, decision_id, candidate_id, rule_family) in expected.items():
        note = notes_by_id[note_id]
        point = points_by_id[point_id]
        decision = decisions_by_id[decision_id]

        assert note.status == "candidate_intake_started"
        assert note.learning_points == [point_id]
        assert note.risk_boundary == "ordinary"
        assert note.locator_requirement == "page_or_section"
        assert note.overlap_candidate_ids == []
        assert point.note_id == note_id
        assert point.source_locator.startswith("page:")
        assert point.proposed_rule_family == rule_family
        assert point.risk_tier == "ordinary"
        assert point.candidate_readiness == "ready"
        assert point.candidate_decision_id == decision_id
        assert decision.learning_point_id == point_id
        assert decision.decision == "create_candidate"
        assert decision.status == "applied"
        assert decision.candidate_id == candidate_id


def test_bazi_general_next_cycle_followup_learning_notes_are_applied():
    notes = learning_reference_curation.load_learning_reference_notes()
    points = learning_reference_curation.load_learning_points()
    decisions = learning_reference_curation.load_candidate_intake_decisions()

    notes_by_id = {note.note_id: note for note in notes}
    points_by_id = {point.learning_point_id: point for point in points}
    decisions_by_id = {decision.decision_id: decision for decision in decisions}

    expected = {
        "note_bazi_general_xinpai_essence_pattern_strength_001": (
            "lp_bazi_general_xinpai_essence_pattern_strength_001",
            "decision_bazi_general_xinpai_essence_pattern_strength_001",
            "candidate_bazi_general_xinpai_essence_pattern_strength_001",
            "pattern_strength",
        ),
        "note_bazi_general_xingming_shuozheng_branch_interaction_001": (
            "lp_bazi_general_xingming_shuozheng_branch_interaction_001",
            "decision_bazi_general_xingming_shuozheng_branch_interaction_001",
            "candidate_bazi_general_xingming_shuozheng_branch_interaction_001",
            "branch_interaction",
        ),
    }

    for note_id, (point_id, decision_id, candidate_id, rule_family) in expected.items():
        note = notes_by_id[note_id]
        point = points_by_id[point_id]
        decision = decisions_by_id[decision_id]

        assert note.status == "candidate_intake_started"
        assert note.learning_points == [point_id]
        assert note.risk_boundary == "ordinary"
        assert note.locator_requirement == "page_or_section"
        assert note.overlap_candidate_ids == []
        assert point.note_id == note_id
        assert point.source_locator.startswith("page:")
        assert point.proposed_rule_family == rule_family
        assert point.risk_tier == "ordinary"
        assert point.candidate_readiness == "ready"
        assert point.candidate_decision_id == decision_id
        assert decision.learning_point_id == point_id
        assert decision.decision == "create_candidate"
        assert decision.status == "applied"
        assert decision.candidate_id == candidate_id


def test_learning_reference_notes_reject_duplicate_note_ids(tmp_path):
    notes = _valid_learning_reference_notes()
    notes[1]["note_id"] = notes[0]["note_id"]
    data_dir = _copy_learning_reference_project_fixture(tmp_path, notes=notes)

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="duplicate note_id",
    ):
        learning_reference_curation.load_learning_reference_notes(data_dir)


@pytest.mark.parametrize(
    ("field_name", "bad_value", "message"),
    [
        ("status", "approved", "invalid status"),
        ("risk_boundary", "fatalistic", "invalid risk_boundary"),
        ("locator_requirement", "entire_pdf", "invalid locator_requirement"),
        ("target_rule_families", ["unsupported_family"], "unsupported rule_family"),
    ],
)
def test_learning_reference_notes_reject_invalid_contract_fields(
    tmp_path,
    field_name,
    bad_value,
    message,
):
    notes = _valid_learning_reference_notes()
    notes[0][field_name] = bad_value
    data_dir = _copy_learning_reference_project_fixture(tmp_path, notes=notes)

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match=message,
    ):
        learning_reference_curation.load_learning_reference_notes(data_dir)


def test_learning_reference_notes_require_learning_point_ids(tmp_path):
    notes = _valid_learning_reference_notes()
    notes[0]["learning_points"] = []
    data_dir = _copy_learning_reference_project_fixture(tmp_path, notes=notes)

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="requires learning_points",
    ):
        learning_reference_curation.load_learning_reference_notes(data_dir)


@pytest.mark.parametrize(
    ("field_name", "bad_value", "message"),
    [
        ("task_id", "task_missing_001", "unknown 016 extraction task"),
        ("package_id", "package_missing_001", "unknown 016 package"),
        ("queue_item_id", "queue_missing_001", "unknown 015 queue item"),
        ("audit_id", "audit_missing_001", "unknown 015 audit"),
        (
            "source_library_entry_id",
            "entry_missing_001",
            "unknown 014 source-library entry",
        ),
        ("source_material_id", "material_missing_001", "unknown 013 source material"),
    ],
)
def test_learning_reference_notes_require_upstream_trace_links(
    tmp_path,
    field_name,
    bad_value,
    message,
):
    notes = _valid_learning_reference_notes()
    notes[0][field_name] = bad_value
    data_dir = _copy_learning_reference_project_fixture(tmp_path, notes=notes)

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match=message,
    ):
        learning_reference_curation.load_learning_reference_notes(data_dir)


def test_learning_reference_notes_cannot_use_prerequisite_backlog_records(tmp_path):
    notes = _valid_learning_reference_notes()
    notes[0]["task_id"] = "backlog_markdown_batch_001_registration_001"
    notes[0]["queue_item_id"] = "queue_markdown_source_batch_001_register"
    notes[0]["audit_id"] = "audit_markdown_source_batch_001"
    data_dir = _copy_learning_reference_project_fixture(tmp_path, notes=notes)

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="prerequisite backlog|not a 016 extraction task|unknown 016 extraction task",
    ):
        learning_reference_curation.load_learning_reference_notes(data_dir)


def test_learning_reference_notes_preserve_overlap_candidate_ids(tmp_path):
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=_valid_candidate_intake_decisions(),
    )

    notes = learning_reference_curation.load_learning_reference_notes(data_dir)
    notes_by_id = {note.note_id: note for note in notes}

    assert notes_by_id["note_northeast_blind_peak_001"].overlap_candidate_ids == [
        "candidate_northeast_blind_image_001",
        "candidate_northeast_blind_image_duplicate_001",
    ]
    assert notes_by_id["note_mingli_true_formula_teacher_001"].overlap_candidate_ids == []


def test_learning_reference_notes_reject_missing_or_unknown_overlap_ids(tmp_path):
    missing_overlap = _valid_learning_reference_notes()
    missing_overlap[0]["overlap_candidate_ids"] = [
        "candidate_northeast_blind_image_001"
    ]
    missing_dir = _copy_learning_reference_project_fixture(
        tmp_path / "missing",
        notes=missing_overlap,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="missing overlap candidate",
    ):
        learning_reference_curation.load_learning_reference_notes(missing_dir)

    unknown_overlap = _valid_learning_reference_notes()
    unknown_overlap[0]["overlap_candidate_ids"] = ["candidate_missing_001"]
    unknown_dir = _copy_learning_reference_project_fixture(
        tmp_path / "unknown",
        notes=unknown_overlap,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="unknown overlap candidate",
    ):
        learning_reference_curation.load_learning_reference_notes(unknown_dir)


def test_learning_reference_note_loading_does_not_mutate_upstream_data(tmp_path):
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=_valid_candidate_intake_decisions(),
    )
    root = data_dir.parent
    tracked_files = [
        "extraction_queue_intake/extraction_tasks.json",
        "extraction_queue_intake/extraction_work_packages.json",
        "materials_audit/extraction_queue_items.json",
        "materials_audit/material_audit_records.json",
        "source_library/source_library_entries.json",
        "source_intake/source_materials.json",
        "source_intake/candidate_extracts.json",
    ]
    before = {
        filename: (root / filename).read_text(encoding="utf-8")
        for filename in tracked_files
    }

    learning_reference_curation.load_learning_reference_notes(data_dir)
    learning_reference_curation.validate_learning_reference_quality(data_dir)

    after = {
        filename: (root / filename).read_text(encoding="utf-8")
        for filename in tracked_files
    }
    assert after == before


def test_learning_reference_summary_includes_seeded_note_counts_and_task_ids():
    summary = learning_reference_curation.build_learning_reference_progress_summary()

    assert summary.note_counts == {"candidate_intake_started": 25}
    assert summary.risk_tier_counts == {
        "sensitive": 44,
        "ordinary": 29,
        "high_risk": 4,
    }
    assert summary.note_rule_family_counts == {
        "blind_image_method": 2,
        "branch_interaction": 7,
        "pattern_strength": 13,
        "useful_god_candidate": 8,
        "luck_cycle": 4,
        "ten_god_relation": 4,
        "five_element_balance": 1,
        "remedy_boundary": 1,
        "high_risk_signal": 1,
    }
    assert summary.selected_task_ids == [
        "task_northeast_blind_peak_extract_001",
        "task_mingli_true_formula_teacher_extract_001",
        "task_duan_plain_mingxue_outline_extract_001",
        "task_mingxue_golden_voice_extract_001",
        "task_fortune_reading_hongfu_qitian_extract_001",
        "task_markdown_batch_002_core_extract_001",
        "task_markdown_batch_001_extract_001",
        "task_markdown_batch_004_extract_001",
        "task_kskeleton_q001_foundation_tables_001",
        "task_kskeleton_q002_yongshen_tiaohou_001",
        "task_kskeleton_q003_geju_strength_001",
        "task_kskeleton_q006_branch_interaction_001",
        "task_kskeleton_q004_luck_cycle_001",
        "task_kskeleton_q008_high_risk_boundary_001",
        "task_markdown_batch_004_extract_001",
        "task_markdown_batch_004_extract_001",
        "task_bazi_general_lecture_pattern_strength_001",
        "task_bazi_general_beichen_branch_interaction_001",
        "task_bazi_general_ziping_useful_god_001",
        "task_bazi_general_ditiansui_pattern_strength_001",
        "task_bazi_general_qiongtong_useful_god_001",
        "task_bazi_general_true_spirit_useful_god_001",
        "task_bazi_general_wangdoujing_branch_interaction_001",
        "task_bazi_general_xinpai_essence_pattern_strength_001",
        "task_bazi_general_xingming_shuozheng_branch_interaction_001",
    ]
    assert summary.next_action_ids == []


@pytest.mark.parametrize(
    ("field_name", "bad_value", "message"),
    [
        (
            "source_quality_note",
            "copied source passage " * 30,
            "too long",
        ),
        (
            "source_quality_note",
            "This note contains copied source passage content.",
            "copied passage",
        ),
        (
            "source_quality_note",
            "Do not store extracted_meaning in learning notes.",
            "extracted meaning",
        ),
        (
            "source_quality_note",
            "This text leaks review decision and approval status.",
            "review-state leakage",
        ),
        (
            "source_quality_note",
            "This text leaks promotion status.",
            "promotion-state leakage",
        ),
        (
            "source_quality_note",
            "This note claims formal report evidence.",
            "report evidence boundary",
        ),
    ],
)
def test_learning_reference_quality_rejects_note_boundary_leakage(
    tmp_path,
    field_name,
    bad_value,
    message,
):
    notes = _valid_learning_reference_notes()
    notes[0][field_name] = bad_value
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=notes,
        learning_points=_valid_learning_points(),
        decisions=_valid_candidate_intake_decisions(),
    )

    failures = learning_reference_curation.validate_learning_reference_quality(data_dir)

    assert any(message in failure for failure in failures), failures


def test_seeded_learning_points_load_and_reference_learning_notes():
    points = learning_reference_curation.load_learning_points()

    assert [point.learning_point_id for point in points] == [
        "lp_northeast_blind_image_001",
        "lp_mingli_pattern_strength_001",
        "lp_duan_ten_god_relation_001",
        "lp_mingxue_five_element_balance_001",
        "lp_hongfu_remedy_boundary_001",
        "lp_markdown_batch_002_useful_god_001",
        "lp_markdown_batch_001_pattern_strength_001",
        "lp_markdown_batch_001_ten_god_relation_001",
        "lp_markdown_batch_001_branch_interaction_001",
        "lp_markdown_batch_001_blind_image_method_001",
        "lp_markdown_batch_002_pattern_strength_001",
        "lp_markdown_batch_002_luck_cycle_001",
        "lp_markdown_batch_002_ten_god_relation_001",
        "lp_markdown_batch_004_useful_god_001",
        "lp_markdown_batch_004_pattern_strength_001",
        "lp_markdown_batch_004_branch_interaction_001",
        "lp_markdown_batch_004_luck_cycle_001",
        "lp_kskeleton_q001_foundation_tables_001",
        "lp_kskeleton_q002_yushi_tiaohou_001",
        "lp_kskeleton_q002_shen_pattern_001",
        "lp_kskeleton_q002_yuanhai_bilateral_001",
        "lp_kskeleton_q003_geju_selection_001",
        "lp_kskeleton_q003_day_master_strength_001",
        "lp_kskeleton_q003_congwang_congshi_001",
        "lp_kskeleton_q006_interaction_structure_001",
        "lp_kskeleton_q004_mechanism_layer_001",
        "lp_kskeleton_q004_cross_dependency_001",
        "lp_kskeleton_q004_q006_dependency_001",
        "lp_kskeleton_q008_family_boundary_001",
        "lp_kskeleton_q008_mortality_boundary_001",
        "lp_kskeleton_q008_other_high_risk_boundary_001",
        "lp_kskeleton_q008_health_medical_boundary_001",
        "lp_kskeleton_q008_branch_interaction_safety_boundary_001",
        "lp_kskeleton_q008_relationship_family_boundary_001",
        "lp_liang_tianyuan_wuxian_day_master_use_god_001",
        "lp_liang_yushi_month_branch_use_god_taxonomy_001",
        "lp_bazi_general_lecture_pattern_strength_001",
        "lp_bazi_general_beichen_branch_interaction_001",
        "lp_bazi_general_ziping_useful_god_001",
        "lp_bazi_general_ditiansui_pattern_strength_001",
        "lp_bazi_general_qiongtong_useful_god_001",
        "lp_bazi_general_true_spirit_useful_god_001",
        "lp_bazi_general_wangdoujing_branch_interaction_001",
        "lp_bazi_general_xinpai_essence_pattern_strength_001",
        "lp_bazi_general_xingming_shuozheng_branch_interaction_001",
    ]
    assert [point.note_id for point in points] == [
        "note_northeast_blind_peak_001",
        "note_mingli_true_formula_teacher_001",
        "note_duan_plain_mingxue_outline_001",
        "note_mingxue_golden_voice_001",
        "note_fortune_reading_hongfu_qitian_001",
        "note_markdown_batch_002_useful_god_001",
        "note_markdown_batch_001_pattern_strength_001",
        "note_markdown_batch_001_pattern_strength_001",
        "note_markdown_batch_001_pattern_strength_001",
        "note_markdown_batch_001_pattern_strength_001",
        "note_markdown_batch_002_useful_god_001",
        "note_markdown_batch_002_useful_god_001",
        "note_markdown_batch_002_useful_god_001",
        "note_markdown_batch_004_001",
        "note_markdown_batch_004_001",
        "note_markdown_batch_004_001",
        "note_markdown_batch_004_001",
        "note_kskeleton_q001_foundation_tables_001",
        "note_kskeleton_q002_yongshen_tiaohou_001",
        "note_kskeleton_q002_yongshen_tiaohou_001",
        "note_kskeleton_q002_yongshen_tiaohou_001",
        "note_kskeleton_q003_geju_strength_001",
        "note_kskeleton_q003_geju_strength_001",
        "note_kskeleton_q003_geju_strength_001",
        "note_kskeleton_q006_branch_interaction_001",
        "note_kskeleton_q004_luck_cycle_001",
        "note_kskeleton_q004_luck_cycle_001",
        "note_kskeleton_q004_luck_cycle_001",
        "note_kskeleton_q008_high_risk_boundary_001",
        "note_kskeleton_q008_high_risk_boundary_001",
        "note_kskeleton_q008_high_risk_boundary_001",
        "note_kskeleton_q008_high_risk_boundary_001",
        "note_kskeleton_q008_high_risk_boundary_001",
        "note_kskeleton_q008_high_risk_boundary_001",
        "note_liang_tianyuan_wuxian_individual_review_001",
        "note_liang_yushi_yongshen_individual_review_001",
        "note_bazi_general_lecture_pattern_strength_001",
        "note_bazi_general_beichen_branch_interaction_001",
            "note_bazi_general_ziping_useful_god_001",
            "note_bazi_general_ditiansui_pattern_strength_001",
            "note_bazi_general_qiongtong_useful_god_001",
            "note_bazi_general_true_spirit_useful_god_001",
            "note_bazi_general_wangdoujing_branch_interaction_001",
            "note_bazi_general_xinpai_essence_pattern_strength_001",
            "note_bazi_general_xingming_shuozheng_branch_interaction_001",
        ]
    assert points[0].candidate_readiness == "duplicate_review"
    assert points[1].candidate_readiness == "ready"
    assert points[2].candidate_readiness == "ready"
    assert points[3].candidate_readiness == "ready"
    assert points[4].candidate_readiness == "ready"
    assert points[5].candidate_readiness == "ready"
    assert all(point.candidate_readiness == "ready" for point in points[6:28])
    assert all(point.candidate_readiness == "deferred" for point in points[28:34])
    assert all(
        point.candidate_readiness == "duplicate_review"
        for point in points[34:36]
    )
    assert all(point.candidate_readiness == "ready" for point in points[36:])


def test_learning_points_reject_unknown_note_references(tmp_path):
    points = _valid_learning_points()
    points[0]["note_id"] = "note_missing_001"
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=points,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="unknown learning reference note",
    ):
        learning_reference_curation.load_learning_points(data_dir)


@pytest.mark.parametrize(
    ("field_name", "bad_value", "message"),
    [
        ("source_locator", "", "source_locator"),
        ("summary", "", "empty summary"),
        ("proposed_rule_family", "unsupported_family", "unsupported proposed_rule_family"),
        ("risk_tier", "fatalistic", "invalid risk_tier"),
        ("limitations", [], "requires limitations"),
        ("candidate_readiness", "approved", "invalid candidate_readiness"),
    ],
)
def test_learning_points_require_candidate_ready_metadata(
    tmp_path,
    field_name,
    bad_value,
    message,
):
    points = _valid_learning_points()
    points[0][field_name] = bad_value
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=points,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match=message,
    ):
        learning_reference_curation.load_learning_points(data_dir)


@pytest.mark.parametrize(
    ("risk_tier", "limitations", "message"),
    [
        ("sensitive", ["Include limitation language only."], "requires uncertainty"),
        ("high_risk", ["State uncertainty only."], "requires limitation"),
    ],
)
def test_sensitive_and_high_risk_learning_points_require_boundaries(
    tmp_path,
    risk_tier,
    limitations,
    message,
):
    points = _valid_learning_points()
    points[0]["risk_tier"] = risk_tier
    points[0]["limitations"] = limitations
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=points,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match=message,
    ):
        learning_reference_curation.load_learning_points(data_dir)


def test_seeded_candidate_intake_decisions_load_and_reference_learning_points():
    decisions = learning_reference_curation.load_candidate_intake_decisions()

    assert [decision.decision_id for decision in decisions] == [
        "decision_northeast_blind_image_001",
        "decision_mingli_pattern_strength_001",
        "decision_duan_ten_god_relation_001",
        "decision_mingxue_five_element_balance_001",
        "decision_hongfu_remedy_boundary_001",
        "decision_markdown_batch_002_useful_god_001",
        "decision_markdown_batch_001_pattern_strength_001",
        "decision_markdown_batch_001_ten_god_relation_001",
        "decision_markdown_batch_001_branch_interaction_001",
        "decision_markdown_batch_001_blind_image_method_001",
        "decision_markdown_batch_002_pattern_strength_001",
        "decision_markdown_batch_002_luck_cycle_001",
        "decision_markdown_batch_002_ten_god_relation_001",
        "decision_markdown_batch_004_useful_god_001",
        "decision_markdown_batch_004_pattern_strength_001",
        "decision_markdown_batch_004_branch_interaction_001",
        "decision_markdown_batch_004_luck_cycle_001",
        "decision_kskeleton_q001_foundation_tables_001",
        "decision_kskeleton_q002_yushi_tiaohou_001",
        "decision_kskeleton_q002_shen_pattern_001",
        "decision_kskeleton_q002_yuanhai_bilateral_001",
        "decision_kskeleton_q003_geju_selection_001",
        "decision_kskeleton_q003_day_master_strength_001",
        "decision_kskeleton_q003_congwang_congshi_001",
        "decision_kskeleton_q006_interaction_structure_001",
        "decision_kskeleton_q004_mechanism_layer_001",
        "decision_kskeleton_q004_cross_dependency_001",
        "decision_kskeleton_q004_q006_dependency_001",
        "decision_liang_tianyuan_wuxian_reuse_batch004_pattern_001",
        "decision_liang_yushi_yongshen_reuse_batch004_useful_god_001",
        "decision_bazi_general_lecture_pattern_strength_001",
        "decision_bazi_general_beichen_branch_interaction_001",
        "decision_bazi_general_ziping_useful_god_001",
        "decision_bazi_general_ditiansui_pattern_strength_001",
        "decision_bazi_general_qiongtong_useful_god_001",
        "decision_bazi_general_true_spirit_useful_god_001",
        "decision_bazi_general_wangdoujing_branch_interaction_001",
        "decision_bazi_general_xinpai_essence_pattern_strength_001",
        "decision_bazi_general_xingming_shuozheng_branch_interaction_001",
    ]
    assert [decision.learning_point_id for decision in decisions] == [
        "lp_northeast_blind_image_001",
        "lp_mingli_pattern_strength_001",
        "lp_duan_ten_god_relation_001",
        "lp_mingxue_five_element_balance_001",
        "lp_hongfu_remedy_boundary_001",
        "lp_markdown_batch_002_useful_god_001",
        "lp_markdown_batch_001_pattern_strength_001",
        "lp_markdown_batch_001_ten_god_relation_001",
        "lp_markdown_batch_001_branch_interaction_001",
        "lp_markdown_batch_001_blind_image_method_001",
        "lp_markdown_batch_002_pattern_strength_001",
        "lp_markdown_batch_002_luck_cycle_001",
        "lp_markdown_batch_002_ten_god_relation_001",
        "lp_markdown_batch_004_useful_god_001",
        "lp_markdown_batch_004_pattern_strength_001",
        "lp_markdown_batch_004_branch_interaction_001",
        "lp_markdown_batch_004_luck_cycle_001",
        "lp_kskeleton_q001_foundation_tables_001",
        "lp_kskeleton_q002_yushi_tiaohou_001",
        "lp_kskeleton_q002_shen_pattern_001",
        "lp_kskeleton_q002_yuanhai_bilateral_001",
        "lp_kskeleton_q003_geju_selection_001",
        "lp_kskeleton_q003_day_master_strength_001",
        "lp_kskeleton_q003_congwang_congshi_001",
        "lp_kskeleton_q006_interaction_structure_001",
        "lp_kskeleton_q004_mechanism_layer_001",
        "lp_kskeleton_q004_cross_dependency_001",
        "lp_kskeleton_q004_q006_dependency_001",
        "lp_liang_tianyuan_wuxian_day_master_use_god_001",
        "lp_liang_yushi_month_branch_use_god_taxonomy_001",
        "lp_bazi_general_lecture_pattern_strength_001",
        "lp_bazi_general_beichen_branch_interaction_001",
            "lp_bazi_general_ziping_useful_god_001",
            "lp_bazi_general_ditiansui_pattern_strength_001",
            "lp_bazi_general_qiongtong_useful_god_001",
            "lp_bazi_general_true_spirit_useful_god_001",
            "lp_bazi_general_wangdoujing_branch_interaction_001",
            "lp_bazi_general_xinpai_essence_pattern_strength_001",
            "lp_bazi_general_xingming_shuozheng_branch_interaction_001",
        ]
    assert decisions[0].decision == "reuse_existing"
    assert decisions[1].decision == "create_candidate"
    assert decisions[2].decision == "create_candidate"
    assert decisions[3].decision == "create_candidate"
    assert decisions[4].decision == "create_candidate"
    assert decisions[5].decision == "create_candidate"
    assert all(decision.status == "applied" for decision in decisions)
    assert [decision.candidate_id for decision in decisions] == [
        "candidate_northeast_blind_image_001",
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
        "candidate_markdown_batch_002_useful_god_001",
        "candidate_markdown_batch_001_pattern_strength_001",
        "candidate_markdown_batch_001_ten_god_relation_001",
        "candidate_markdown_batch_001_branch_interaction_001",
        "candidate_markdown_batch_001_blind_image_method_001",
        "candidate_markdown_batch_002_pattern_strength_001",
        "candidate_markdown_batch_002_luck_cycle_001",
        "candidate_markdown_batch_002_ten_god_relation_001",
        "candidate_markdown_batch_004_useful_god_001",
        "candidate_markdown_batch_004_pattern_strength_001",
        "candidate_markdown_batch_004_branch_interaction_001",
        "candidate_markdown_batch_004_luck_cycle_001",
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
        "candidate_markdown_batch_004_pattern_strength_001",
        "candidate_markdown_batch_004_useful_god_001",
        "candidate_bazi_general_lecture_pattern_strength_001",
        "candidate_bazi_general_beichen_branch_interaction_001",
            "candidate_bazi_general_ziping_useful_god_001",
            "candidate_bazi_general_ditiansui_pattern_strength_001",
            "candidate_bazi_general_qiongtong_useful_god_001",
            "candidate_bazi_general_true_spirit_useful_god_001",
            "candidate_bazi_general_wangdoujing_branch_interaction_001",
            "candidate_bazi_general_xinpai_essence_pattern_strength_001",
            "candidate_bazi_general_xingming_shuozheng_branch_interaction_001",
        ]


def test_apply_candidate_intake_decisions_creates_selected_candidate_and_marks_decision_applied(
    tmp_path,
):
    from mingli_engine import source_intake

    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=_valid_candidate_intake_decisions(),
        action_notes=_valid_prerequisite_action_notes(),
    )
    intake_dir = data_dir.parent / "source_intake"

    created = learning_reference_curation.apply_candidate_intake_decisions(
        ["decision_mingli_pattern_strength_001"],
        data_dir,
        applied_at="2026-06-01",
    )

    assert [candidate.candidate_id for candidate in created] == [
        "candidate_mingli_pattern_strength_017_001"
    ]
    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in source_intake.load_candidate_extracts(intake_dir)
    }
    candidate = candidates_by_id["candidate_mingli_pattern_strength_017_001"]
    assert candidate.material_id == "material_mingli_true_formula_teacher_pdf"
    assert candidate.source_locator == (
        "learning-reference:note_mingli_true_formula_teacher_001#"
        "lp_mingli_pattern_strength_001; locator_requirement=page_or_section_required"
    )
    assert candidate.extracted_meaning == (
        "Pattern strength material should stay conditional until source "
        "locator and chart context are reviewed."
    )
    assert candidate.proposed_rule_family == "pattern_strength"
    assert candidate.risk_tier == "sensitive"
    assert candidate.status == "pending_review"
    assert candidate.proposed_limitations == [
        "State uncertainty for timing and pattern interpretation.",
        "Include limitation language; do not guarantee outcome timing.",
    ]
    assert candidate.created_by == "learning_reference_curation"
    assert candidate.created_at == "2026-06-01"

    decisions_by_id = {
        decision.decision_id: decision
        for decision in learning_reference_curation.load_candidate_intake_decisions(
            data_dir
        )
    }
    assert decisions_by_id["decision_mingli_pattern_strength_001"].status == "applied"
    assert decisions_by_id["decision_northeast_blind_image_001"].status == "planned"


def test_apply_candidate_intake_decisions_marks_reuse_decision_applied_without_new_candidate(
    tmp_path,
):
    from mingli_engine import source_intake

    decisions = _valid_candidate_intake_decisions()
    decisions[0]["decision"] = "reuse_existing"
    decisions[0]["candidate_id"] = "candidate_northeast_blind_image_001"
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=decisions,
        action_notes=_valid_prerequisite_action_notes(),
    )
    intake_dir = data_dir.parent / "source_intake"
    before_candidate_ids = {
        candidate.candidate_id
        for candidate in source_intake.load_candidate_extracts(intake_dir)
    }

    created = learning_reference_curation.apply_candidate_intake_decisions(
        [
            "decision_northeast_blind_image_001",
            "decision_mingli_pattern_strength_001",
        ],
        data_dir,
        applied_at="2026-06-01",
    )

    assert [candidate.candidate_id for candidate in created] == [
        "candidate_mingli_pattern_strength_017_001"
    ]
    after_candidate_ids = {
        candidate.candidate_id
        for candidate in source_intake.load_candidate_extracts(intake_dir)
    }
    assert after_candidate_ids == before_candidate_ids | {
        "candidate_mingli_pattern_strength_017_001"
    }
    decisions_by_id = {
        decision.decision_id: decision
        for decision in learning_reference_curation.load_candidate_intake_decisions(
            data_dir
        )
    }
    assert decisions_by_id["decision_northeast_blind_image_001"].status == "applied"
    assert decisions_by_id["decision_mingli_pattern_strength_001"].status == "applied"


def test_apply_candidate_intake_decisions_requires_actionable_selection(
    tmp_path,
):
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=_valid_candidate_intake_decisions(),
        action_notes=_valid_prerequisite_action_notes(),
    )

    assert learning_reference_curation.apply_candidate_intake_decisions([], data_dir) == []
    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="requires actionable candidate-intake decision",
    ):
        learning_reference_curation.apply_candidate_intake_decisions(
            ["decision_northeast_blind_image_001"],
            data_dir,
        )


def test_candidate_intake_decisions_reject_unknown_learning_points(tmp_path):
    decisions = _valid_candidate_intake_decisions()
    decisions[0]["learning_point_id"] = "lp_missing_001"
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=decisions,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="unknown learning point",
    ):
        learning_reference_curation.load_candidate_intake_decisions(data_dir)


def test_create_candidate_decisions_require_ready_learning_points(tmp_path):
    decisions = _valid_candidate_intake_decisions()
    decisions[0]["decision"] = "create_candidate"
    decisions[0]["candidate_id"] = "candidate_duplicate_review_should_not_create"
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=decisions,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="create_candidate requires ready learning point",
    ):
        learning_reference_curation.load_candidate_intake_decisions(data_dir)


@pytest.mark.parametrize("decision_type", ["reuse_existing", "avoid_duplicate"])
def test_reuse_and_avoid_duplicate_decisions_require_existing_overlap_ids(
    tmp_path,
    decision_type,
):
    decisions = _valid_candidate_intake_decisions()
    decisions[0]["decision"] = decision_type
    decisions[0]["candidate_id"] = "candidate_northeast_blind_image_001"
    decisions[0]["overlap_candidate_ids"] = []
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=decisions,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="requires overlap_candidate_ids",
    ):
        learning_reference_curation.load_candidate_intake_decisions(data_dir)

    decisions = _valid_candidate_intake_decisions()
    decisions[0]["decision"] = decision_type
    decisions[0]["candidate_id"] = "candidate_missing_001"
    decisions[0]["overlap_candidate_ids"] = ["candidate_missing_001"]
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path / "unknown",
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=decisions,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="unknown overlap candidate",
    ):
        learning_reference_curation.load_candidate_intake_decisions(data_dir)


@pytest.mark.parametrize(
    ("field_name", "bad_value", "message"),
    [
        ("rationale", "This text leaks review decision.", "review-state leakage"),
        ("rationale", "This text leaks approval status.", "review-state leakage"),
        ("rationale", "This text leaks promotion status.", "promotion-state leakage"),
        ("rationale", "This text claims formal evidence.", "report evidence boundary"),
    ],
)
def test_candidate_intake_decision_quality_rejects_boundary_leakage(
    tmp_path,
    field_name,
    bad_value,
    message,
):
    decisions = _valid_candidate_intake_decisions()
    decisions[0][field_name] = bad_value
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=decisions,
    )

    failures = learning_reference_curation.validate_learning_reference_quality(data_dir)

    assert any(message in failure for failure in failures), failures


def test_learning_reference_summary_includes_learning_points_and_decisions():
    summary = learning_reference_curation.build_learning_reference_progress_summary()

    assert summary.learning_point_counts == {"duplicate_review": 3, "ready": 36, "deferred": 6}
    assert summary.decision_counts == {
        "reuse_existing": 3,
        "create_candidate": 36,
        "status:applied": 39,
    }
    assert summary.candidate_ready_count == 36
    assert summary.candidate_decision_count == 39
    assert summary.overlap_warning_count == 9


def test_liang_bazi_individual_review_notes_reuse_existing_batch_004_candidates():
    notes = learning_reference_curation.load_learning_reference_notes()
    points = learning_reference_curation.load_learning_points()
    decisions = learning_reference_curation.load_candidate_intake_decisions()

    notes_by_id = {note.note_id: note for note in notes}
    points_by_id = {point.learning_point_id: point for point in points}
    decisions_by_id = {decision.decision_id: decision for decision in decisions}

    tianyuan_note = notes_by_id["note_liang_tianyuan_wuxian_individual_review_001"]
    yushi_note = notes_by_id["note_liang_yushi_yongshen_individual_review_001"]

    assert tianyuan_note.task_id == "task_markdown_batch_004_extract_001"
    assert yushi_note.task_id == "task_markdown_batch_004_extract_001"
    assert tianyuan_note.status == "candidate_intake_started"
    assert yushi_note.status == "candidate_intake_started"
    assert tianyuan_note.learning_points == [
        "lp_liang_tianyuan_wuxian_day_master_use_god_001"
    ]
    assert yushi_note.learning_points == [
        "lp_liang_yushi_month_branch_use_god_taxonomy_001"
    ]
    assert tianyuan_note.overlap_candidate_ids == [
        "candidate_markdown_batch_004_pattern_strength_001"
    ]
    assert yushi_note.overlap_candidate_ids == [
        "candidate_markdown_batch_004_useful_god_001"
    ]

    tianyuan_point = points_by_id[
        "lp_liang_tianyuan_wuxian_day_master_use_god_001"
    ]
    yushi_point = points_by_id[
        "lp_liang_yushi_month_branch_use_god_taxonomy_001"
    ]

    assert tianyuan_point.source_locator == (
        "review-note:Markdown/source_batch_004_cleaned/"
        "简体 梁湘润《天元巫咸经》注释.md#L34"
    )
    assert yushi_point.source_locator == (
        "review-note:Markdown/source_batch_004_cleaned/"
        "简体《余氏用神辞渊》梁湘润(1).md#L57"
    )
    assert tianyuan_point.candidate_readiness == "duplicate_review"
    assert yushi_point.candidate_readiness == "duplicate_review"
    assert tianyuan_point.candidate_decision_id == (
        "decision_liang_tianyuan_wuxian_reuse_batch004_pattern_001"
    )
    assert yushi_point.candidate_decision_id == (
        "decision_liang_yushi_yongshen_reuse_batch004_useful_god_001"
    )

    tianyuan_decision = decisions_by_id[
        "decision_liang_tianyuan_wuxian_reuse_batch004_pattern_001"
    ]
    yushi_decision = decisions_by_id[
        "decision_liang_yushi_yongshen_reuse_batch004_useful_god_001"
    ]

    assert tianyuan_decision.decision == "reuse_existing"
    assert yushi_decision.decision == "reuse_existing"
    assert tianyuan_decision.candidate_id == (
        "candidate_markdown_batch_004_pattern_strength_001"
    )
    assert yushi_decision.candidate_id == (
        "candidate_markdown_batch_004_useful_god_001"
    )
    assert tianyuan_decision.status == "applied"
    assert yushi_decision.status == "applied"


def test_seeded_prerequisite_action_notes_load_and_reference_016_backlog():
    action_notes = learning_reference_curation.load_prerequisite_action_notes()

    assert [action.action_note_id for action in action_notes] == [
        "action_blind_life_manual_risk_review_001",
        "action_blind_school_secret_blocked_001",
        "action_markdown_batch_003_registration_001",
        "action_immortal_fortune_jianghu_secret_risk_review_001",
        "action_life_death_book_100_pages_risk_review_001",
        "action_source_processing_status_deferred_001",
        "action_markdown_batch_005_risk_review_001",
    ]
    assert [action.backlog_id for action in action_notes] == [
        "backlog_blind_life_manual_risk_review_001",
        "backlog_blind_school_secret_blocked_001",
        "backlog_markdown_batch_003_registration_001",
        "backlog_immortal_fortune_jianghu_secret_risk_review_001",
        "backlog_life_death_book_100_pages_risk_review_001",
        "backlog_source_processing_status_deferred_001",
        "backlog_markdown_batch_005_risk_review_001",
    ]
    assert [action.package_id for action in action_notes] == [
        "package_next_candidates_001",
        "package_next_candidates_001",
        "package_next_candidates_003",
        "package_next_candidates_003",
        "package_next_candidates_003",
        "package_next_candidates_003",
        "package_next_candidates_004",
    ]
    assert [action.queue_item_id for action in action_notes] == [
        "queue_blind_life_manual_risk_review",
        "queue_blind_school_secret_blocked",
        "queue_markdown_source_batch_003_register",
        "queue_immortal_fortune_jianghu_secret_risk_review",
        "queue_life_death_book_100_pages_risk_review",
        "queue_source_processing_status_deferred",
        "queue_markdown_source_batch_005_risk_review",
    ]
    assert [action.audit_id for action in action_notes] == [
        "audit_blind_life_manual",
        "audit_blind_school_secret",
        "audit_markdown_source_batch_003",
        "audit_immortal_fortune_jianghu_secret",
        "audit_life_death_book_100_pages",
        "audit_source_processing_status",
        "audit_markdown_source_batch_005",
    ]


def test_learning_reference_routes_markdown_batch_005_risk_review_as_prerequisite_action():
    action_notes = learning_reference_curation.load_prerequisite_action_notes()
    summary = learning_reference_curation.build_learning_reference_progress_summary()

    actions_by_id = {action.action_note_id: action for action in action_notes}
    action = actions_by_id["action_markdown_batch_005_risk_review_001"]

    assert action.backlog_id == "backlog_markdown_batch_005_risk_review_001"
    assert action.package_id == "package_next_candidates_004"
    assert action.queue_item_id == "queue_markdown_source_batch_005_risk_review"
    assert action.audit_id == "audit_markdown_source_batch_005"
    assert action.action_type == "risk_review"
    assert action.missing_prerequisites == ["risk_boundary_review"]
    assert action.recommended_action == "risk_review"
    assert action.risk_boundary == "high_risk"
    assert action.status == "completed"

    assert action.action_note_id not in summary.next_action_ids
    assert summary.prerequisite_action_counts["risk_review"] == 4
    assert summary.prerequisite_action_counts["status:completed"] == 4
    assert summary.risk_tier_counts["high_risk"] == 4
    assert summary.formal_evidence_delta == 0


def test_learning_reference_risk_review_sweep_closes_actions_without_evidence_changes():
    action_notes = learning_reference_curation.load_prerequisite_action_notes()
    summary = learning_reference_curation.build_learning_reference_progress_summary()
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    promotion_batches = source_intake.load_promotion_batches()
    evidence_units = classical_sources.load_evidence_units()

    actions_by_id = {action.action_note_id: action for action in action_notes}
    completed_action_ids = {
        "action_blind_life_manual_risk_review_001",
        "action_immortal_fortune_jianghu_secret_risk_review_001",
        "action_life_death_book_100_pages_risk_review_001",
        "action_markdown_batch_005_risk_review_001",
    }

    assert {
        action_id
        for action_id in completed_action_ids
        if actions_by_id[action_id].status == "completed"
    } == completed_action_ids
    assert completed_action_ids.isdisjoint(summary.next_action_ids)
    assert summary.next_action_ids == []
    assert summary.prerequisite_action_counts == {
        "risk_review": 4,
        "deferred": 2,
        "blocked": 1,
        "status:completed": 4,
        "status:deferred": 2,
        "status:blocked": 1,
    }
    assert summary.formal_evidence_delta == 0
    assert len(candidates) == 48
    assert len(reviews) == 48
    assert len(promotion_batches) == 31
    assert len(evidence_units) == 105


def test_learning_reference_closes_remaining_draft_notes_without_evidence_changes():
    notes = learning_reference_curation.load_learning_reference_notes()
    summary = learning_reference_curation.build_learning_reference_progress_summary()
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    promotion_batches = source_intake.load_promotion_batches()
    evidence_units = classical_sources.load_evidence_units()

    closed_note_ids = {
        "note_northeast_blind_peak_001",
        "note_mingli_true_formula_teacher_001",
        "note_duan_plain_mingxue_outline_001",
        "note_mingxue_golden_voice_001",
        "note_fortune_reading_hongfu_qitian_001",
        "note_markdown_batch_002_useful_god_001",
        "note_markdown_batch_001_pattern_strength_001",
    }
    notes_by_id = {note.note_id: note for note in notes}

    assert {
        note_id
        for note_id in closed_note_ids
        if notes_by_id[note_id].status == "candidate_intake_started"
    } == closed_note_ids
    assert summary.note_counts == {"candidate_intake_started": 25}
    assert summary.next_action_ids == []
    assert summary.formal_evidence_delta == 0
    assert len(candidates) == 48
    assert len(reviews) == 48
    assert len(promotion_batches) == 31
    assert len(evidence_units) == 105


@pytest.mark.parametrize(
    ("field_name", "bad_value", "message"),
    [
        ("backlog_id", "backlog_missing_001", "unknown 016 backlog record"),
        ("package_id", "package_missing_001", "unknown 016 package"),
        ("queue_item_id", "queue_missing_001", "unknown 015 queue item"),
        ("audit_id", "audit_missing_001", "unknown 015 audit"),
    ],
)
def test_prerequisite_action_notes_require_upstream_backlog_trace_links(
    tmp_path,
    field_name,
    bad_value,
    message,
):
    action_notes = _valid_prerequisite_action_notes()
    action_notes[0][field_name] = bad_value
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=_valid_candidate_intake_decisions(),
        action_notes=action_notes,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match=message,
    ):
        learning_reference_curation.load_prerequisite_action_notes(data_dir)


@pytest.mark.parametrize(
    "action_type",
    [
        "registration",
        "preparation",
        "locator_review",
        "risk_review",
        "deferred",
        "blocked",
    ],
)
def test_prerequisite_action_notes_require_prerequisites_or_durable_reasons(
    tmp_path,
    action_type,
):
    action_notes = [
        {
            "action_note_id": f"action_{action_type}_missing_reason",
            "backlog_id": f"backlog_{action_type}_missing_reason",
            "package_id": "package_next_candidates_001",
            "queue_item_id": f"queue_{action_type}_missing_reason",
            "audit_id": f"audit_{action_type}_missing_reason",
            "action_type": action_type,
            "missing_prerequisites": [],
            "durable_reason": "todo",
            "recommended_action": "defer" if action_type == "deferred" else "block",
            "risk_boundary": "ordinary",
            "status": "planned",
            "created_at": "2026-05-31",
            "updated_at": "2026-05-31",
        }
    ]
    data_dir = _write_learning_reference_fixture(tmp_path, action_notes=action_notes)

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="missing_prerequisites or durable_reason",
    ):
        learning_reference_curation.load_prerequisite_action_notes(data_dir)


@pytest.mark.parametrize(
    ("action_type", "recommended_action", "risk_boundary"),
    [
        ("risk_review", "risk_review", "high_risk"),
        ("blocked", "block", "sensitive"),
    ],
)
def test_prerequisite_action_notes_preserve_backlog_action_and_risk_boundary(
    tmp_path,
    action_type,
    recommended_action,
    risk_boundary,
):
    action_notes = _valid_prerequisite_action_notes()
    target = next(action for action in action_notes if action["action_type"] == action_type)
    target["recommended_action"] = "no_action"
    target["risk_boundary"] = "ordinary" if risk_boundary != "ordinary" else "sensitive"
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=_valid_learning_points(),
        decisions=_valid_candidate_intake_decisions(),
        action_notes=action_notes,
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="recommended_action|risk_boundary",
    ):
        learning_reference_curation.load_prerequisite_action_notes(data_dir)


@pytest.mark.parametrize(
    ("action_note_id", "backlog_id"),
    [
        (
            "action_blind_life_manual_risk_review_001",
            "backlog_blind_life_manual_risk_review_001",
        ),
        (
            "action_blind_school_secret_blocked_001",
            "backlog_blind_school_secret_blocked_001",
        ),
    ],
)
def test_blocking_prerequisite_actions_cannot_become_learning_points_or_decisions(
    tmp_path,
    action_note_id,
    backlog_id,
):
    points = _valid_learning_points()
    points[0]["learning_point_id"] = f"lp_{action_note_id}"
    points[0]["note_id"] = action_note_id
    decisions = _valid_candidate_intake_decisions()
    decisions[0]["learning_point_id"] = action_note_id
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path,
        notes=_valid_learning_reference_notes(),
        learning_points=points,
        decisions=decisions,
        action_notes=_valid_prerequisite_action_notes(),
    )

    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="prerequisite action cannot become learning point",
    ):
        learning_reference_curation.load_learning_points(data_dir)
    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="prerequisite action cannot create candidate decision|unknown learning point",
    ):
        learning_reference_curation.load_candidate_intake_decisions(data_dir)

    points = _valid_learning_points()
    points[0]["note_id"] = backlog_id
    data_dir = _copy_learning_reference_project_fixture(
        tmp_path / "backlog",
        notes=_valid_learning_reference_notes(),
        learning_points=points,
        decisions=_valid_candidate_intake_decisions(),
        action_notes=_valid_prerequisite_action_notes(),
    )
    with pytest.raises(
        learning_reference_curation.LearningReferenceCurationError,
        match="prerequisite action cannot become learning point",
    ):
        learning_reference_curation.load_learning_points(data_dir)


def test_learning_reference_summary_includes_prerequisite_action_counts():
    summary = learning_reference_curation.build_learning_reference_progress_summary()

    assert summary.note_counts == {"candidate_intake_started": 25}
    assert summary.learning_point_counts == {"duplicate_review": 3, "ready": 36, "deferred": 6}
    assert summary.decision_counts == {
        "reuse_existing": 3,
        "create_candidate": 36,
        "status:applied": 39,
    }
    assert summary.prerequisite_action_counts == {
        "risk_review": 4,
        "deferred": 2,
        "blocked": 1,
        "status:completed": 4,
        "status:deferred": 2,
        "status:blocked": 1,
    }
    assert summary.risk_tier_counts == {
        "sensitive": 44,
        "ordinary": 29,
        "high_risk": 4,
    }
    assert summary.overlap_warning_count == 9
    assert summary.candidate_ready_count == 36
    assert summary.candidate_decision_count == 39
    assert summary.formal_evidence_delta == 0
    assert summary.next_action_ids == []


def test_learning_reference_docs_track_source_window_learning_closure_sync():
    closure_counts = _source_window_learning_closure_counts()
    summary = learning_reference_curation.build_learning_reference_progress_summary()

    assert closure_counts == {
        "learning-paraphrase-ready": 4,
        "policy-boundary-retained": 5,
        "safety-boundary-retained": 2,
    }
    assert len(summary.selected_task_ids) == 25
    assert summary.formal_evidence_delta == 0
    assert summary.next_action_ids == []
    assert "action_blind_school_secret_blocked_001" not in summary.next_action_ids
    assert "action_markdown_batch_003_registration_001" not in summary.next_action_ids
    assert "action_source_processing_status_deferred_001" not in summary.next_action_ids

    overview = Path("docs/classical_sources/learning_reference_curation.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )

    for document in (overview, quickstart):
        assert "Source-Window Learning Closure Sync" in document
        assert "`selected-ready-learning-notes=25`" in document
        assert "`retained-chapter-learning-closed=11`" in document
        assert "`learning-paraphrase-ready=4`" in document
        assert "`policy-boundary-retained=5`" in document
        assert "`safety-boundary-retained=2`" in document
        assert "`closed-draft-learning-notes=7`" in document
        assert "`next_action_ids=0`" in document
        assert "`planned-risk-review-actions=0`" in document
        assert "`completed-risk-review-actions=4`" in document
        assert "`formal_evidence_delta=0`" in document
        assert "No new candidate-intake decisions" in document
        assert "no 013 candidate extracts" in document
        assert "no promotion batches" in document


def test_learning_reference_candidate_formal_evidence_boundary_audit_snapshot():
    summary = learning_reference_curation.build_learning_reference_progress_summary()
    decisions = learning_reference_curation.load_candidate_intake_decisions()
    candidates = {
        candidate.candidate_id: candidate
        for candidate in source_intake.load_candidate_extracts()
    }
    reviews = source_intake.load_review_decisions()
    promotion_batches = source_intake.load_promotion_batches()
    evidence_units = classical_sources.load_evidence_units()

    create_candidate_ids = [
        decision.candidate_id
        for decision in decisions
        if decision.decision == "create_candidate"
    ]
    reuse_candidate_ids = [
        decision.candidate_id
        for decision in decisions
        if decision.decision == "reuse_existing"
    ]

    assert summary.decision_counts == {
        "reuse_existing": 3,
        "create_candidate": 36,
        "status:applied": 39,
    }
    assert summary.formal_evidence_delta == 0
    assert len(create_candidate_ids) == 36
    assert reuse_candidate_ids == [
        "candidate_northeast_blind_image_001",
        "candidate_markdown_batch_004_pattern_strength_001",
        "candidate_markdown_batch_004_useful_god_001",
    ]
    assert set(create_candidate_ids + reuse_candidate_ids) <= set(candidates)

    assert len(candidates) == 48
    assert Counter(candidate.status for candidate in candidates.values()) == {
        "promoted": 45,
        "rejected": 2,
        "blocked": 1,
    }
    assert Counter(candidates[candidate_id].status for candidate_id in create_candidate_ids) == {
        "promoted": 36
    }
    assert all(
        candidates[candidate_id].source_locator.startswith(("review-note:", "page:"))
        for candidate_id in create_candidate_ids
    )
    assert all(
        "learning-reference:" not in candidates[candidate_id].source_locator
        for candidate_id in create_candidate_ids
    )

    assert len(reviews) == 48
    assert Counter(review.decision for review in reviews) == {
        "approved": 45,
        "rejected": 2,
        "blocked": 1,
    }
    assert Counter(
        review.decision
        for review in reviews
        if review.candidate_id in create_candidate_ids
    ) == {"approved": 36}

    assert len(promotion_batches) == 31
    assert Counter(batch.review_status for batch in promotion_batches) == {
        "reviewed": 31
    }

    assert len(evidence_units) == 105
    assert Counter(unit.curation_batch_id for unit in evidence_units) == {
        "batch_012_seed_001": 8,
        "batch_012_taxonomy_001": 58,
        "batch_markdown_registration_001": 15,
        "batch_kskeleton_taxonomy_001": 11,
        "batch_bazi_general_source_preparation_001": 3,
        "batch_blind_life_manual_high_risk_boundary_001": 1,
        "batch_markdown_batch_002_extension_001": 3,
        "batch_bazi_general_selected_variant_001": 2,
        "batch_bazi_general_next_cycle_cluster_source_001": 2,
        "batch_bazi_general_next_cycle_followup_001": 2,
    }
    assert not any(
        unit.source_ref.startswith("learning-reference:")
        or "candidate_" in unit.source_ref
        or "learning-closure:" in unit.source_ref
        for unit in evidence_units
    )

    overview = Path("docs/classical_sources/learning_reference_curation.md").read_text(
        encoding="utf-8"
    )
    for marker in (
        "Candidate/Formal Evidence Boundary Audit",
        "`017-applied-decisions=39`",
        "`017-create-candidate-decisions=36`",
        "`013-candidate-extracts=48`",
        "`013-review-decisions=48`",
        "`013-promotion-batches=31`",
        "`012-formal-evidence-units=105`",
        "`formal_evidence_delta=0`",
        "`learning-reference-source-refs-in-012=0`",
        "`candidate-id-source-refs-in-012=0`",
        "`learning-closure-source-refs-in-012=0`",
    ):
        assert marker in overview


def test_learning_reference_authorization_audit_confirms_local_boundary_clearance():
    audit = learning_reference_curation.build_learning_reference_authorization_audit()

    assert audit.audit_id == "017-candidate-formal-evidence-authorization-audit"
    assert (
        audit.authorization_status
        == "ready_for_explicit_downstream_authorization"
    )
    assert audit.downstream_mutation_authorized is False
    assert audit.note_counts == {"candidate_intake_started": 25}
    assert audit.next_action_ids == []
    assert audit.decision_counts == {
        "reuse_existing": 3,
        "create_candidate": 36,
        "status:applied": 39,
    }
    assert audit.candidate_status_counts == {
        "promoted": 45,
        "rejected": 2,
        "blocked": 1,
    }
    assert audit.review_decision_counts == {
        "approved": 45,
        "rejected": 2,
        "blocked": 1,
    }
    assert audit.promotion_review_status_counts == {"reviewed": 31}
    assert audit.formal_evidence_unit_count == 105
    assert audit.formal_evidence_delta == 0
    assert audit.leakage_counts == {
        "learning_reference_source_refs_in_012": 0,
        "candidate_id_source_refs_in_012": 0,
        "learning_closure_source_refs_in_012": 0,
    }
    assert audit.clearance_checks == {
        "017_notes_closed": "passed",
        "017_no_active_next_actions": "passed",
        "017_decisions_applied": "passed",
        "013_candidate_review_promotion_counts_aligned": "passed",
        "012_formal_evidence_boundary_clean": "passed",
        "downstream_mutation_requires_explicit_request": "passed",
    }


def test_learning_reference_authorization_audit_markdown_and_docs_are_in_sync():
    audit = learning_reference_curation.build_learning_reference_authorization_audit()
    markdown = (
        learning_reference_curation
        .render_learning_reference_authorization_audit_markdown(audit)
    )
    overview = Path("docs/classical_sources/learning_reference_curation.md").read_text(
        encoding="utf-8"
    )
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(
        encoding="utf-8"
    )
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(
        encoding="utf-8"
    )

    for marker in (
        "Authorization Audit Packet",
        "`authorization-status=ready_for_explicit_downstream_authorization`",
        "`downstream-mutation-authorized=false`",
        "`017-notes-closed=25`",
        "`017-next-action-ids=0`",
        "`012-boundary-leakage=0`",
        "`next-downstream-entry=013-explicit-candidate-review-or-015-queue-refresh`",
    ):
        assert marker in markdown
        assert marker in overview
        assert marker in quickstart
        assert marker in handoff


def test_new_material_learning_handoff_tracks_final_state():
    closure_counts = _source_window_learning_closure_counts()
    summary = learning_reference_curation.build_learning_reference_progress_summary()
    candidates = source_intake.load_candidate_extracts()
    reviews = source_intake.load_review_decisions()
    promotion_batches = source_intake.load_promotion_batches()
    evidence_units = classical_sources.load_evidence_units()

    handoff_path = Path("docs/classical_sources/new_material_learning_handoff.md")
    assert handoff_path.exists()
    handoff = handoff_path.read_text(encoding="utf-8")
    readme = Path("docs/classical_sources/README.md").read_text(encoding="utf-8")

    assert "[new_material_learning_handoff.md](new_material_learning_handoff.md)" in readme
    for marker in (
        "New Material Learning Handoff",
        "Completed Checkpoints",
        "Current Frozen Snapshot",
        "Continuation Entry Points",
        "Remaining Optional Precision Work",
        "Next Long Goal",
        "Guardrails",
        "`source-window-review-note-items=57`",
        "`page-locators=44`",
        "`chapter-locators=11`",
        f"`selected-ready-learning-notes={len(summary.selected_task_ids)}`",
        "`closed-draft-learning-notes=7`",
        f"`next_action_ids={len(summary.next_action_ids)}`",
        f"`retained-chapter-learning-closed={sum(closure_counts.values())}`",
        f"`learning-paraphrase-ready={closure_counts['learning-paraphrase-ready']}`",
        f"`policy-boundary-retained={closure_counts['policy-boundary-retained']}`",
        f"`safety-boundary-retained={closure_counts['safety-boundary-retained']}`",
        f"`017-applied-decisions={summary.decision_counts['status:applied']}`",
        f"`017-create-candidate-decisions={summary.decision_counts['create_candidate']}`",
        "`authorization-status=ready_for_explicit_downstream_authorization`",
        "`downstream-mutation-authorized=false`",
            "`017-notes-closed=25`",
        "`017-next-action-ids=0`",
        "`012-boundary-leakage=0`",
        "`next-downstream-entry=013-explicit-candidate-review-or-015-queue-refresh`",
        f"`013-candidate-extracts={len(candidates)}`",
        f"`013-review-decisions={len(reviews)}`",
        f"`013-promotion-batches={len(promotion_batches)}`",
        f"`012-formal-evidence-units={len(evidence_units)}`",
        f"`formal_evidence_delta={summary.formal_evidence_delta}`",
        "`next-new-material-start=015-raw-text-next-cycle-gated-cluster-review-prep`",
        "Do not mutate root PDFs, root `Markdown/`, `资料原文/`, or `资料整理/`",
        "Do not create candidates, review decisions, promotion batches, or formal evidence unless explicitly requested",
        "Do not push remote work from this handoff",
    ):
        assert marker in handoff
