import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from mingli_engine import (
    extraction_queue_intake,
    learning_reference_curation,
    materials_audit,
    source_intake,
    source_library,
)
from mingli_engine.safety import safety_check
from mingli_engine.classical_sources import load_approved_evidence_units


REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_DATA_DIR = REPO_ROOT / "src" / "mingli_engine" / "data"


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_path = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else os.pathsep.join([src_path, env["PYTHONPATH"]])
    )
    return subprocess.run(
        [sys.executable, "-m", "mingli_engine.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def test_safety_check_allows_general_high_risk_signal_language():
    result = safety_check("请分析重大灾厄信号，作为传统风险信号，不保证发生。")

    assert result.allowed is True
    assert result.red_line_categories == []


def test_safety_check_still_blocks_exact_outcome_and_diagnosis_requests():
    cases = {
        "请算我能活到几岁": "lifespan_or_death_timing",
        "请诊断我是什么病并给治疗方案": "professional_advice",
    }

    for text, category in cases.items():
        result = safety_check(text)

        assert result.allowed is False
        assert category in result.red_line_categories


def test_cli_allows_lifespan_focus_as_narrowed_markdown(tmp_path):
    profile_path = tmp_path / "lifespan-focus.json"
    profile_path.write_text(
        json.dumps(
            {
                "calendar_type": "gregorian",
                "birth_date": "1992-08-18",
                "birth_time": "09:30",
                "birthplace": "上海市",
                "gender": "未指定",
                "focus_topic": "寿命",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = _run_cli(
        "calculate-report",
        "--input",
        str(profile_path),
        "--format",
        "markdown",
    )

    assert result.returncode == 0, result.stderr
    assert "高风险材料边界" in result.stdout
    assert "传统风险信号" in result.stdout
    for prohibited_phrase in ("必定", "注定", "一定会", "死定"):
        assert prohibited_phrase not in result.stdout


def test_high_risk_evidence_units_have_non_exact_limitations():
    high_risk_units = [
        unit
        for unit in load_approved_evidence_units()
        if unit.risk_tier == "high_risk"
    ]

    assert len(high_risk_units) >= 4
    for unit in high_risk_units:
        limitation_text = "；".join(unit.limitations)
        assert "精确" in limitation_text or "不输出" in limitation_text
        for prohibited_phrase in ("必定", "注定", "一定会", "死定"):
            assert prohibited_phrase not in unit.summary
            assert prohibited_phrase not in limitation_text


def test_expanded_corpus_summaries_avoid_absolute_destiny_phrases():
    for unit in load_approved_evidence_units():
        combined = "；".join([unit.summary, *unit.limitations])
        for prohibited_phrase in ("必定", "注定", "一定会", "死定"):
            assert prohibited_phrase not in combined


@pytest.mark.parametrize(
    "prohibited_phrase",
    [
        "\u5fc5\u5b9a",
        "\u6ce8\u5b9a",
        "\u4e00\u5b9a\u4f1a",
        "\u6b7b\u5b9a",
    ],
)
def test_candidate_extracts_reject_absolute_outcome_language(
    tmp_path,
    prohibited_phrase,
):
    (tmp_path / "source_materials.json").write_text(
        json.dumps(
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
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "candidate_extracts.json").write_text(
        json.dumps(
            [
                {
                    "candidate_id": "candidate_absolute",
                    "material_id": "material_001",
                    "source_locator": "review-note:absolute",
                    "extracted_meaning": (
                        f"Candidate language claims the outcome {prohibited_phrase} "
                        "happen."
                    ),
                    "proposed_rule_family": "high_risk_signal",
                    "risk_tier": "high_risk",
                    "status": "pending_review",
                    "proposed_limitations": [
                        "Reject exact outcome and lifespan language."
                    ],
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(source_intake.SourceIntakeError, match="absolute language"):
        source_intake.load_candidate_extracts(tmp_path)


def _write_source_library_quality_fixture(
    tmp_path: Path,
    source_quality_notes: str = "Reviewable source notes.",
    risk_notes: list[str] | None = None,
) -> None:
    (tmp_path / "source_library_entries.json").write_text(
        json.dumps(
            [
                {
                    "entry_id": "entry_high_risk_language",
                    "material_id": "material_high_risk_language",
                    "title": "High Risk Language Source",
                    "material_type": "pdf",
                    "local_reference": "high-risk-language.pdf",
                    "tracking_status": "external_untracked",
                    "readiness_status": "ready_for_extraction",
                    "topic_tags": ["high-risk"],
                    "rule_families": ["high_risk_signal"],
                    "source_quality_notes": source_quality_notes,
                    "rights_notes": "Do not copy long passages.",
                    "risk_tier": "high_risk",
                    "risk_notes": risk_notes or ["Needs high-risk review boundary."],
                    "priority_level": "medium",
                    "next_action": "extract_candidates",
                    "outcome_reason": "",
                    "created_at": "2026-05-28",
                    "updated_at": "2026-05-28",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "source_priority_assessments.json").write_text(
        "[]",
        encoding="utf-8",
    )
    (tmp_path / "curation_batch_plans.json").write_text("[]", encoding="utf-8")


def test_source_library_quality_rejects_absolute_destiny_language(tmp_path):
    _write_source_library_quality_fixture(
        tmp_path,
        source_quality_notes=(
            "Unsafe source summary claims the outcome \u5fc5\u5b9a happens."
        ),
    )

    failures = source_library.validate_source_library_quality(tmp_path)

    assert any("absolute language" in failure for failure in failures)


def test_source_library_quality_rejects_prohibited_high_risk_wording(tmp_path):
    _write_source_library_quality_fixture(
        tmp_path,
        risk_notes=[
            "Unsafe note says to diagnose illness and prescribe treatment."
        ],
    )

    failures = source_library.validate_source_library_quality(tmp_path)

    assert any("prohibited high-risk wording" in failure for failure in failures)


def _write_materials_audit_quality_fixture(
    tmp_path: Path,
    *,
    readiness_note: str,
) -> None:
    (tmp_path / "material_audit_records.json").write_text(
        json.dumps(
            [
                {
                    "audit_id": "audit_quality",
                    "canonical_title": "Quality Fixture",
                    "alternate_titles": [],
                    "material_scope": "bazi",
                    "primary_material_type": "pdf",
                    "representations": ["repr_quality"],
                    "source_library_entry_id": "",
                    "source_identity_confidence": "uncertain",
                    "preparation_state": "raw_available",
                    "source_boundary": "external_untracked",
                    "topic_tags": [],
                    "rule_families": [],
                    "risk_tier": "high_risk",
                    "risk_notes": ["Needs high-risk boundary review."],
                    "rights_notes": "Do not copy long passages.",
                    "missing_prerequisites": ["risk_review"],
                    "recommended_next_action": "risk_review",
                    "outcome_reason": "",
                    "created_at": "2026-05-30",
                    "updated_at": "2026-05-30",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "material_representations.json").write_text(
        json.dumps(
            [
                {
                    "representation_id": "repr_quality",
                    "audit_id": "audit_quality",
                    "representation_type": "root_pdf",
                    "local_reference": "quality-fixture.pdf",
                    "tracking_status": "external_untracked",
                    "text_quality": "not_text",
                    "locator_quality": "file_only",
                    "size_hint": "",
                    "modified_hint": "",
                    "contains_images": True,
                    "notes": "Raw PDF remains preparation material.",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "source_alignment_findings.json").write_text("[]", encoding="utf-8")
    (tmp_path / "preparation_readiness_findings.json").write_text(
        json.dumps(
            [
                {
                    "readiness_id": "ready_quality",
                    "audit_id": "audit_quality",
                    "readiness_state": "needs_risk_review",
                    "text_preparation_status": "raw_only",
                    "locator_confidence": "weak",
                    "source_quality": "moderate",
                    "risk_boundary": "high_risk",
                    "missing_prerequisites": ["risk_review"],
                    "ready_reasons": [],
                    "blockers": [readiness_note],
                    "recommended_next_action": "risk_review",
                    "assessed_by": "maintainer",
                    "assessed_at": "2026-05-30",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "extraction_queue_items.json").write_text("[]", encoding="utf-8")


@pytest.mark.parametrize(
    ("unsafe_note", "expected_marker"),
    [
        ("Unsafe readiness note says the outcome \u5fc5\u5b9a happens.", "absolute language"),
        ("Unsafe readiness note predicts exact death timing.", "exact death"),
        ("Unsafe readiness note tells reviewer to diagnose illness.", "prohibited high-risk wording"),
        ("Unsafe readiness note gives legal instruction.", "prohibited high-risk wording"),
        ("Unsafe readiness note gives psychological treatment.", "prohibited high-risk wording"),
        ("Unsafe readiness note gives investment instruction.", "prohibited high-risk wording"),
        ("Unsafe readiness note uses coercive matching language.", "prohibited high-risk wording"),
        ("Unsafe readiness note is designed to create anxiety.", "prohibited high-risk wording"),
        ("Unsafe readiness note promotes a paid remedy upsell.", "prohibited high-risk wording"),
    ],
)
def test_materials_audit_readiness_quality_rejects_high_risk_language(
    tmp_path,
    unsafe_note,
    expected_marker,
):
    _write_materials_audit_quality_fixture(tmp_path, readiness_note=unsafe_note)

    failures = materials_audit.validate_materials_audit_quality(tmp_path)

    assert any(expected_marker in failure for failure in failures)


def _write_extraction_queue_quality_fixture(
    tmp_path: Path,
    *,
    task_note: str = "Ready source with clear boundary.",
    draft_note: str = "State uncertainty and limitation during manual review.",
) -> None:
    (tmp_path / "extraction_work_packages.json").write_text(
        json.dumps(
            [
                {
                    "package_id": "package_quality",
                    "package_label": "Quality package",
                    "source_queue_snapshot_ids": ["queue_quality"],
                    "selected_task_ids": ["task_quality"],
                    "backlog_record_ids": [],
                    "status": "planned",
                    "created_at": "2026-05-31",
                    "updated_at": "2026-05-31",
                    "notes": "Safety fixture package.",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "extraction_tasks.json").write_text(
        json.dumps(
            [
                {
                    "task_id": "task_quality",
                    "package_id": "package_quality",
                    "queue_item_id": "queue_quality",
                    "audit_id": "audit_quality",
                    "source_library_entry_id": "entry_quality",
                    "intended_source_material_id": "material_quality",
                    "priority_level": "high",
                    "priority_rationale": task_note,
                    "target_rule_families": ["high_risk_signal"],
                    "target_gap_ids": [],
                    "risk_boundary": "high_risk",
                    "locator_requirement": "page_or_section",
                    "source_quality_note": "Review before extraction.",
                    "rights_note": "Do not copy long passages.",
                    "pre_extraction_checks": [
                        "complete risk-review boundary",
                        "store concise paraphrases only",
                    ],
                    "overlap_warnings": [],
                    "recommended_action": "extract_candidates",
                    "status": "planned",
                    "created_at": "2026-05-31",
                    "updated_at": "2026-05-31",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "candidate_draft_slots.json").write_text(
        json.dumps(
            [
                {
                    "draft_slot_id": "slot_quality",
                    "task_id": "task_quality",
                    "intended_candidate_label": "High-risk boundary slot",
                    "target_rule_family": "high_risk_signal",
                    "target_gap_id": "",
                    "locator_requirement": "page_or_section",
                    "expected_review_notes": [draft_note],
                    "risk_boundary": "high_risk",
                    "safety_requirements": [
                        "State uncertainty.",
                        "Include limitation notes.",
                        "Complete risk-review boundary.",
                    ],
                    "status": "planned",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "prerequisite_backlog_records.json").write_text(
        "[]",
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("unsafe_text", "expected_marker"),
    [
        ("Unsafe note says the outcome \u5fc5\u5b9a happens.", "absolute language"),
        ("Unsafe note predicts exact death timing.", "exact death"),
        ("Unsafe note predicts exact lifespan.", "exact death"),
        ("Unsafe note tells reviewer to diagnose illness.", "prohibited high-risk wording"),
        ("Unsafe note gives legal instruction.", "prohibited high-risk wording"),
        ("Unsafe note gives psychological treatment.", "prohibited high-risk wording"),
        ("Unsafe note gives investment instruction.", "prohibited high-risk wording"),
        ("Unsafe note uses coercive matching language.", "prohibited high-risk wording"),
        ("Unsafe note is designed to create anxiety.", "prohibited high-risk wording"),
        ("Unsafe note promotes a paid remedy upsell.", "prohibited high-risk wording"),
    ],
)
def test_extraction_package_quality_rejects_high_risk_language(
    tmp_path,
    unsafe_text,
    expected_marker,
):
    _write_extraction_queue_quality_fixture(tmp_path, task_note=unsafe_text)

    failures = extraction_queue_intake.validate_extraction_package_quality(tmp_path)

    assert any(expected_marker in failure for failure in failures)


def test_extraction_draft_slot_quality_rejects_high_risk_language(tmp_path):
    _write_extraction_queue_quality_fixture(
        tmp_path,
        draft_note="Draft note promotes paid remedy upsell pressure.",
    )

    failures = extraction_queue_intake.validate_extraction_package_quality(tmp_path)

    assert any("prohibited high-risk wording" in failure for failure in failures)


def _write_learning_reference_quality_fixture(
    tmp_path: Path,
    *,
    point_summary: str = (
        "Pattern material should remain conditional until locator and chart "
        "context are reviewed."
    ),
    decision_rationale: str = (
        "No existing 013 candidate overlaps this source and rule family."
    ),
) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    for dirname in (
        "extraction_queue_intake",
        "materials_audit",
        "source_library",
        "source_intake",
    ):
        shutil.copytree(PROJECT_DATA_DIR / dirname, tmp_path / dirname)
    candidate_path = tmp_path / "source_intake" / "candidate_extracts.json"
    candidate_records = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate_records = [
        candidate
        for candidate in candidate_records
        if candidate["candidate_id"] != "candidate_mingli_pattern_strength_017_001"
    ]
    candidate_path.write_text(
        json.dumps(candidate_records, ensure_ascii=False),
        encoding="utf-8",
    )
    task_path = tmp_path / "extraction_queue_intake" / "extraction_tasks.json"
    task_records = json.loads(task_path.read_text(encoding="utf-8"))
    for task in task_records:
        task["overlap_warnings"] = [
            warning
            for warning in task.get("overlap_warnings", [])
            if "candidate_mingli_pattern_strength_017_001" not in warning
        ]
    task_path.write_text(
        json.dumps(task_records, ensure_ascii=False),
        encoding="utf-8",
    )
    data_dir = tmp_path / "learning_reference_curation"
    data_dir.mkdir()
    (data_dir / "learning_reference_notes.json").write_text(
        json.dumps(
            [
                {
                    "note_id": "note_mingli_true_formula_teacher_001",
                    "task_id": "task_mingli_true_formula_teacher_extract_001",
                    "package_id": "package_next_candidates_001",
                    "queue_item_id": "queue_mingli_true_formula_teacher_extract",
                    "audit_id": "audit_mingli_true_formula_teacher",
                    "source_library_entry_id": "entry_mingli_true_formula_teacher_pdf",
                    "source_material_id": "material_mingli_true_formula_teacher_pdf",
                    "source_title": "Mingli True Formula Teacher",
                    "target_rule_families": ["pattern_strength"],
                    "locator_requirement": "page_or_section",
                    "risk_boundary": "sensitive",
                    "rights_note": "Do not copy long passages.",
                    "source_quality_note": "Confirm locator anchors.",
                    "learning_points": ["lp_mingli_pattern_strength_001"],
                    "overlap_candidate_ids": [],
                    "status": "draft",
                    "created_at": "2026-05-31",
                    "updated_at": "2026-05-31",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (data_dir / "learning_points.json").write_text(
        json.dumps(
            [
                {
                    "learning_point_id": "lp_mingli_pattern_strength_001",
                    "note_id": "note_mingli_true_formula_teacher_001",
                    "point_label": "Pattern strength candidate framing",
                    "source_locator": "page_or_section_required",
                    "summary": point_summary,
                    "proposed_rule_family": "pattern_strength",
                    "risk_tier": "sensitive",
                    "limitations": [
                        "State uncertainty for pattern interpretation.",
                        "Include limitation language before candidate review.",
                    ],
                    "candidate_readiness": "ready",
                    "candidate_decision_id": "decision_mingli_pattern_strength_001",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (data_dir / "candidate_intake_decisions.json").write_text(
        json.dumps(
            [
                {
                    "decision_id": "decision_mingli_pattern_strength_001",
                    "learning_point_id": "lp_mingli_pattern_strength_001",
                    "decision": "create_candidate",
                    "source_material_id": "material_mingli_true_formula_teacher_pdf",
                    "candidate_id": "candidate_mingli_pattern_strength_017_001",
                    "overlap_candidate_ids": [],
                    "rationale": decision_rationale,
                    "status": "planned",
                    "created_at": "2026-05-31",
                    "updated_at": "2026-05-31",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (data_dir / "prerequisite_action_notes.json").write_text("[]", encoding="utf-8")
    return data_dir


@pytest.mark.parametrize(
    ("unsafe_text", "expected_marker"),
    [
        ("Unsafe learning text says the outcome \u5fc5\u5b9a happens.", "absolute language"),
        ("Unsafe learning text predicts exact death timing.", "exact death"),
        ("Unsafe learning text predicts exact lifespan.", "exact death"),
        ("Unsafe learning text tells reviewer to diagnose illness.", "prohibited high-risk wording"),
        ("Unsafe learning text gives legal instruction.", "prohibited high-risk wording"),
        ("Unsafe learning text gives psychological treatment.", "prohibited high-risk wording"),
        ("Unsafe learning text gives investment instruction.", "prohibited high-risk wording"),
        ("Unsafe learning text uses coercive matching language.", "prohibited high-risk wording"),
        ("Unsafe learning text is designed to create anxiety.", "prohibited high-risk wording"),
        ("Unsafe learning text promotes a paid remedy upsell.", "prohibited high-risk wording"),
    ],
)
def test_learning_reference_quality_rejects_high_risk_learning_point_language(
    tmp_path,
    unsafe_text,
    expected_marker,
):
    data_dir = _write_learning_reference_quality_fixture(
        tmp_path,
        point_summary=unsafe_text,
    )

    failures = learning_reference_curation.validate_learning_reference_quality(data_dir)

    assert any(expected_marker in failure for failure in failures)


def test_learning_reference_quality_rejects_high_risk_decision_rationale(tmp_path):
    data_dir = _write_learning_reference_quality_fixture(
        tmp_path,
        decision_rationale="Unsafe decision rationale promotes paid remedy upsell.",
    )

    failures = learning_reference_curation.validate_learning_reference_quality(data_dir)

    assert any("prohibited high-risk wording" in failure for failure in failures)
