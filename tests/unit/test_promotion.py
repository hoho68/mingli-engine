import json
from pathlib import Path

import pytest

from mingli_engine import classical_sources, promotion


def _write_json(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_intake_dir(tmp_path: Path) -> Path:
    """Build a minimal source_intake data dir with one approved candidate."""
    intake_dir = tmp_path / "source_intake"
    intake_dir.mkdir()
    _write_json(
        intake_dir / "source_materials.json",
        [
            {
                "material_id": "material_test_pdf",
                "title": "Test Material",
                "material_type": "pdf",
                "file_label": "test.pdf",
                "tracking_status": "external_untracked",
                "preparation_status": "reviewed",
                "related_source_id": "source_test",
                "scope_notes": "Test scope.",
                "rights_notes": "Concise paraphrases only.",
                "gap_reason": "",
            }
        ],
    )
    _write_json(
        intake_dir / "candidate_extracts.json",
        [
            {
                "candidate_id": "candidate_test_001",
                "material_id": "material_test_pdf",
                "source_locator": "review-note:test#signal",
                "extracted_meaning": "A concise test signal for pattern strength.",
                "proposed_rule_family": "pattern_strength",
                "risk_tier": "ordinary",
                "status": "approved",
                "proposed_limitations": ["Requires structure context."],
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
    _write_json(
        intake_dir / "review_decisions.json",
        [
            {
                "decision_id": "review_candidate_test_001",
                "candidate_id": "candidate_test_001",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-05-28",
                "rationale": "Reviewable candidate.",
                "required_changes": [],
                "rejection_reason": "",
                "approval_limitations": ["Keep as conditional only."],
                "source_quality": "review_note",
                "confidence": "moderate",
            }
        ],
    )
    _write_json(
        intake_dir / "promotion_batches.json",
        [
            {
                "promotion_batch_id": "promotion_test_001",
                "candidate_ids": ["candidate_test_001"],
                "target_evidence_ids": ["evidence_test_001"],
                "review_status": "reviewed",
                "review_notes": "Approved for promotion.",
                "unresolved_issues": [],
            }
        ],
    )
    return intake_dir


def _make_corpus_dir(tmp_path: Path) -> Path:
    """Build a minimal classical_sources corpus with one approved source."""
    corpus_dir = tmp_path / "classical_sources"
    corpus_dir.mkdir()
    _write_json(
        corpus_dir / "sources.json",
        [
            {
                "source_id": "source_test",
                "title": "Test Source",
                "file_name": "test.pdf",
                "source_type": "pdf",
                "extraction_status": "converted",
                "review_status": "approved",
                "scope_notes": "Test source scope.",
                "risk_notes": ["pattern_strength"],
                "curation_gap_reason": "",
                "review_reference": "",
            }
        ],
    )
    _write_json(corpus_dir / "evidence_units.json", [])
    _write_json(
        corpus_dir / "curation_batches.json",
        [
            {
                "batch_id": "batch_promotion_test_001",
                "source_ids": ["source_test"],
                "evidence_ids": ["evidence_test_001"],
                "review_status": "reviewed",
                "review_notes": "Promotion batch.",
                "unresolved_issues": [],
            }
        ],
    )
    _write_json(corpus_dir / "source_conflicts.json", [])
    return corpus_dir


def _overrides():
    return {
        "evidence_test_001": {
            "theme": "Test pattern",
            "applicability": ["four_pillars_complete"],
            "school": "test_school",
        }
    }


def test_plan_promotion_maps_approved_candidate_to_evidence_unit(tmp_path):
    intake_dir = _make_intake_dir(tmp_path)
    corpus_dir = _make_corpus_dir(tmp_path)

    plan = promotion.plan_promotion(
        intake_dir=intake_dir,
        corpus_dir=corpus_dir,
        promotion_batch_id="promotion_test_001",
        evidence_overrides=_overrides(),
    )

    assert len(plan.evidence_units) == 1
    unit = plan.evidence_units[0]
    assert unit.evidence_id == "evidence_test_001"
    assert unit.source_id == "source_test"
    assert unit.source_ref == "review-note:test#signal"
    assert unit.rule_family == "pattern_strength"
    assert unit.risk_tier == "ordinary"
    assert unit.summary == "A concise test signal for pattern strength."
    assert "Requires structure context." in unit.limitations
    assert "Keep as conditional only." in unit.limitations
    assert unit.theme == "Test pattern"
    assert unit.school == "test_school"
    assert unit.source_quality == "review_note"
    assert unit.confidence == "moderate"


def test_plan_promotion_rejects_batch_with_unapproved_candidate(tmp_path):
    intake_dir = _make_intake_dir(tmp_path)
    corpus_dir = _make_corpus_dir(tmp_path)
    candidates = json.loads(
        (intake_dir / "candidate_extracts.json").read_text(encoding="utf-8")
    )
    candidates[0]["status"] = "pending_review"
    _write_json(intake_dir / "candidate_extracts.json", candidates)
    with pytest.raises(promotion.PromotionError, match="not approved"):
        promotion.plan_promotion(
            intake_dir=intake_dir,
            corpus_dir=corpus_dir,
            promotion_batch_id="promotion_test_001",
            evidence_overrides=_overrides(),
        )


def test_plan_promotion_rejects_non_approved_source(tmp_path):
    intake_dir = _make_intake_dir(tmp_path)
    corpus_dir = _make_corpus_dir(tmp_path)
    sources = json.loads((corpus_dir / "sources.json").read_text(encoding="utf-8"))
    sources[0]["review_status"] = "reviewed"
    _write_json(corpus_dir / "sources.json", sources)

    with pytest.raises(promotion.PromotionError, match="report-usable source"):
        promotion.plan_promotion(
            intake_dir=intake_dir,
            corpus_dir=corpus_dir,
            promotion_batch_id="promotion_test_001",
            evidence_overrides=_overrides(),
        )


def test_plan_promotion_requires_theme_applicability_school_overrides(tmp_path):
    intake_dir = _make_intake_dir(tmp_path)
    corpus_dir = _make_corpus_dir(tmp_path)

    with pytest.raises(promotion.PromotionError, match="theme"):
        promotion.plan_promotion(
            intake_dir=intake_dir,
            corpus_dir=corpus_dir,
            promotion_batch_id="promotion_test_001",
            evidence_overrides={},
        )


def test_plan_promotion_rejects_duplicate_target_evidence_id(tmp_path):
    intake_dir = _make_intake_dir(tmp_path)
    corpus_dir = _make_corpus_dir(tmp_path)
    _write_json(
        corpus_dir / "evidence_units.json",
        [
            {
                "evidence_id": "evidence_test_001",
                "source_id": "source_test",
                "source_ref": "review-note:test#existing",
                "theme": "Existing",
                "rule_family": "pattern_strength",
                "risk_tier": "ordinary",
                "summary": "An existing evidence unit.",
                "applicability": ["four_pillars_complete"],
                "limitations": ["Requires context."],
                "school": "test_school",
                "curation_batch_id": "batch_promotion_test_001",
                "confidence": "moderate",
                "source_quality": "review_note",
                "conflict_ids": [],
            }
        ],
    )

    with pytest.raises(promotion.PromotionError, match="already exists"):
        promotion.plan_promotion(
            intake_dir=intake_dir,
            corpus_dir=corpus_dir,
            promotion_batch_id="promotion_test_001",
            evidence_overrides=_overrides(),
        )


def test_apply_promotion_writes_evidence_and_marks_candidate_promoted(tmp_path):
    intake_dir = _make_intake_dir(tmp_path)
    corpus_dir = _make_corpus_dir(tmp_path)

    result = promotion.apply_promotion(
        intake_dir=intake_dir,
        corpus_dir=corpus_dir,
        promotion_batch_id="promotion_test_001",
        evidence_overrides=_overrides(),
    )

    assert result.promoted_count == 1
    assert result.target_evidence_ids == ["evidence_test_001"]

    units = classical_sources.load_approved_evidence_units(corpus_dir)
    assert any(u.evidence_id == "evidence_test_001" for u in units)

    raw_candidates = json.loads(
        (intake_dir / "candidate_extracts.json").read_text(encoding="utf-8")
    )
    assert raw_candidates[0]["status"] == "promoted"


def test_plan_promotion_is_dry_run_and_does_not_write(tmp_path):
    intake_dir = _make_intake_dir(tmp_path)
    corpus_dir = _make_corpus_dir(tmp_path)

    plan = promotion.plan_promotion(
        intake_dir=intake_dir,
        corpus_dir=corpus_dir,
        promotion_batch_id="promotion_test_001",
        evidence_overrides=_overrides(),
    )
    assert plan.promoted_count == 0
    units = classical_sources.load_approved_evidence_units(corpus_dir)
    assert not any(u.evidence_id == "evidence_test_001" for u in units)


def test_apply_promotion_rejects_high_risk_without_limitation_markers(tmp_path):
    intake_dir = _make_intake_dir(tmp_path)
    corpus_dir = _make_corpus_dir(tmp_path)
    candidates = json.loads(
        (intake_dir / "candidate_extracts.json").read_text(encoding="utf-8")
    )
    candidates[0]["risk_tier"] = "high_risk"
    candidates[0]["proposed_limitations"] = ["A generic note without boundary words."]
    _write_json(intake_dir / "candidate_extracts.json", candidates)

    with pytest.raises(promotion.PromotionError, match="high_risk"):
        promotion.apply_promotion(
            intake_dir=intake_dir,
            corpus_dir=corpus_dir,
            promotion_batch_id="promotion_test_001",
            evidence_overrides=_overrides(),
        )
