import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INTAKE_DIR = REPO_ROOT / "src" / "mingli_engine" / "data" / "source_intake"
CORPUS_DIR = REPO_ROOT / "src" / "mingli_engine" / "data" / "classical_sources"


def _run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
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
        input=input_text,
        capture_output=True,
        check=False,
    )


def _overrides_for(target_evidence_id: str) -> dict:
    return {
        target_evidence_id: {
            "theme": "CLI test theme",
            "applicability": ["four_pillars_complete"],
            "school": "test_school",
        }
    }


def _write_json_file(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_cli_fixture(tmp_path: Path) -> tuple[Path, Path]:
    intake_dir = tmp_path / "source_intake"
    intake_dir.mkdir()
    _write_json_file(
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
    _write_json_file(
        intake_dir / "candidate_extracts.json",
        [
            {
                "candidate_id": "candidate_test_cli_001",
                "material_id": "material_test_pdf",
                "source_locator": "review-note:test#signal",
                "extracted_meaning": "A concise CLI test signal for pattern strength.",
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
                "created_at": "2026-06-21",
            }
        ],
    )
    _write_json_file(
        intake_dir / "review_decisions.json",
        [
            {
                "decision_id": "review_candidate_test_cli_001",
                "candidate_id": "candidate_test_cli_001",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-06-21",
                "rationale": "Reviewable candidate.",
                "required_changes": [],
                "rejection_reason": "",
                "approval_limitations": ["Keep as conditional only."],
                "source_quality": "review_note",
                "confidence": "moderate",
            }
        ],
    )
    _write_json_file(
        intake_dir / "promotion_batches.json",
        [
            {
                "promotion_batch_id": "promotion_test_cli_001",
                "candidate_ids": ["candidate_test_cli_001"],
                "target_evidence_ids": ["evidence_test_cli_001"],
                "review_status": "reviewed",
                "review_notes": "Approved for promotion.",
                "unresolved_issues": [],
            }
        ],
    )

    corpus_dir = tmp_path / "classical_sources"
    corpus_dir.mkdir()
    _write_json_file(
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
    _write_json_file(corpus_dir / "evidence_units.json", [])
    _write_json_file(
        corpus_dir / "curation_batches.json",
        [
            {
                "batch_id": "batch_promotion_test_cli_001",
                "source_ids": ["source_test"],
                "evidence_ids": ["evidence_test_cli_001"],
                "review_status": "reviewed",
                "review_notes": "Promotion batch.",
                "unresolved_issues": [],
            }
        ],
    )
    _write_json_file(corpus_dir / "source_conflicts.json", [])
    return intake_dir, corpus_dir


def test_promote_dry_run_outputs_plan_json_without_writing(tmp_path):
    intake_dir, corpus_dir = _build_cli_fixture(tmp_path)
    overrides_path = tmp_path / "overrides.json"
    overrides_path.write_text(
        json.dumps(_overrides_for("evidence_test_cli_001"), ensure_ascii=False),
        encoding="utf-8",
    )

    result = _run_cli(
        "promote",
        "--batch",
        "promotion_test_cli_001",
        "--overrides",
        str(overrides_path),
        "--intake-dir",
        str(intake_dir),
        "--corpus-dir",
        str(corpus_dir),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["promotion_batch_id"] == "promotion_test_cli_001"
    assert payload["promoted_count"] == 0
    assert len(payload["evidence_units"]) == 1
    assert payload["evidence_units"][0]["evidence_id"] == "evidence_test_cli_001"
    # dry-run does not write evidence
    units = json.loads((corpus_dir / "evidence_units.json").read_text(encoding="utf-8"))
    assert units == []


def test_promote_requires_batch(tmp_path):
    overrides_path = tmp_path / "overrides.json"
    overrides_path.write_text("{}", encoding="utf-8")

    result = _run_cli(
        "promote",
        "--overrides",
        str(overrides_path),
    )

    assert result.returncode != 0
    assert "Traceback" not in result.stderr


def test_promote_requires_overrides():
    result = _run_cli("promote", "--batch", "promotion_013_seed_001")

    assert result.returncode != 0
    assert "Traceback" not in result.stderr


def test_promote_dry_run_on_real_batch_outputs_plan_json():
    overrides_path = REPO_ROOT / "examples" / "promote-overrides.dry-run.json"
    overrides_path.write_text(
        json.dumps(
            {
                "evidence_promote_cli_dryrun_001": {
                    "theme": "CLI dry-run theme",
                    "applicability": ["four_pillars_complete"],
                    "school": "test_school",
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    try:
        result = _run_cli(
            "promote",
            "--batch",
            "promotion_013_seed_001",
            "--overrides",
            str(overrides_path),
        )
        # The target evidence id does not match the batch, so promotion rejects.
        assert result.returncode != 0
        assert "Traceback" not in result.stderr
    finally:
        overrides_path.unlink(missing_ok=True)


def test_promote_apply_writes_evidence_and_marks_candidate_promoted(tmp_path):
    intake_dir, corpus_dir = _build_cli_fixture(tmp_path)
    overrides_path = tmp_path / "overrides.json"
    overrides_path.write_text(
        json.dumps(_overrides_for("evidence_test_cli_001"), ensure_ascii=False),
        encoding="utf-8",
    )

    result = _run_cli(
        "promote",
        "--batch",
        "promotion_test_cli_001",
        "--overrides",
        str(overrides_path),
        "--intake-dir",
        str(intake_dir),
        "--corpus-dir",
        str(corpus_dir),
        "--apply",
        "--curation-batch",
        "batch_promotion_test_cli_001",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["promoted_count"] == 1
    assert payload["target_evidence_ids"] == ["evidence_test_cli_001"]

    units = json.loads((corpus_dir / "evidence_units.json").read_text(encoding="utf-8"))
    assert any(u["evidence_id"] == "evidence_test_cli_001" for u in units)

    candidates = json.loads(
        (intake_dir / "candidate_extracts.json").read_text(encoding="utf-8")
    )
    assert candidates[0]["status"] == "promoted"
