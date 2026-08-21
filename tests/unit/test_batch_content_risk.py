"""Tests for the governed batch_20260714 content-risk rebuild.

The rebuild re-derives ONLY batch-derived records (candidates, reviews,
promotion batch, evidence units, curation batch, learning records) by
replaying the deterministic pipeline with the evidence-content risk gate.
Legacy (non-batch) records must remain byte-identical.
"""

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from mingli_engine import source_intake
from mingli_engine.batch_content_risk import (
    rebuild_batch_content_risk_dispositions,
)
from mingli_engine.classical_sources import (
    load_curation_batches,
    load_evidence_units,
)
from mingli_engine.evidence_risk import (
    DESCRIPTIVE_DEATH_CONTENT,
    EXACT_DEATH_LIFESPAN_RULE,
    ORDINARY_CONTENT,
    REQUIRED_DESCRIPTIVE_DEATH_LIMITATION,
    classify_evidence_content,
)
from mingli_engine.new_material_learning import load_learning_records
from mingli_engine.source_intake import load_candidate_extracts

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "src" / "mingli_engine" / "data"

BATCH_PREFIXES = (
    "candidate_batch_20260714_",
    "review_candidate_batch_20260714_",
    "b20260714_evidence_",
    "material_batch_20260714_",
    "source_batch_20260714_",
    "promotion_batch_20260714_",
    "batch_new_material_20260714_",
)


def _is_batch_entry(entry: dict) -> bool:
    for key in (
        "candidate_id",
        "decision_id",
        "evidence_id",
        "material_id",
        "source_id",
        "promotion_batch_id",
        "batch_id",
    ):
        value = entry.get(key)
        if isinstance(value, str) and any(value.startswith(p) for p in BATCH_PREFIXES):
            return True
    return False


def _legacy_snapshot(data_dir: Path) -> dict[str, str]:
    """Map file name -> sha256 of the canonical JSON of its legacy entries."""
    snapshot: dict[str, str] = {}
    for subdir, names in (
        (
            "source_intake",
            ("candidate_extracts", "review_decisions", "promotion_batches", "source_materials"),
        ),
        ("classical_sources", ("evidence_units", "curation_batches", "sources", "source_conflicts")),
    ):
        for name in names:
            path = data_dir / subdir / f"{name}.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            legacy = [entry for entry in payload if not _is_batch_entry(entry)]
            canonical = json.dumps(legacy, ensure_ascii=False, sort_keys=True)
            snapshot[f"{subdir}/{name}"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return snapshot


def _expected_dispositions(data_dir: Path) -> dict[str, set[str]]:
    """State-agnostic expectations derived from the learning records.

    Returns sets of record ids: ``exact`` (records rejected by the content-risk
    gate), ``descriptive`` (eligible records with descriptive death content),
    ``ordinary`` (eligible records with ordinary content).
    """
    from mingli_engine.evidence_risk import EXACT_DEATH_LIFESPAN_GATE_REASON

    ledger = load_learning_records(
        data_dir / "new_material_learning" / "batch_20260714_learning_records.json"
    )
    expected: dict[str, set[str]] = {"exact": set(), "descriptive": set(), "ordinary": set()}
    for record in ledger.records:
        if record.kind != "rule_candidate":
            continue
        risk = classify_evidence_content(
            record.payload["conclusion"], record.payload["limitations"]
        )
        if (
            record.gate_decision == "rejected_safety"
            and record.gate_reason == EXACT_DEATH_LIFESPAN_GATE_REASON
        ):
            assert risk.risk_class == EXACT_DEATH_LIFESPAN_RULE, record.record_id
            expected["exact"].add(record.record_id)
        elif record.gate_decision == "eligible":
            if risk.risk_class == DESCRIPTIVE_DEATH_CONTENT:
                expected["descriptive"].add(record.record_id)
            elif risk.risk_class == ORDINARY_CONTENT:
                expected["ordinary"].add(record.record_id)
            else:
                raise AssertionError(
                    f"eligible record carries exact content: {record.record_id}"
                )
    return expected


@pytest.fixture()
def rebuilt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    data_dir = tmp_path / "data"
    shutil.copytree(DATA_DIR, data_dir)
    legacy_before = _legacy_snapshot(data_dir)
    dispositions = _expected_dispositions(data_dir)
    report = rebuild_batch_content_risk_dispositions(
        data_root=data_dir / "new_material_learning",
        intake_dir=data_dir / "source_intake",
        corpus_dir=data_dir / "classical_sources",
        batch_id="batch_20260714",
        confirm_governed_rebuild=True,
    )
    monkeypatch.setattr("mingli_engine.source_intake._DATA_DIR", data_dir / "source_intake")
    monkeypatch.setattr("mingli_engine.classical_sources._DATA_DIR", data_dir / "classical_sources")
    return data_dir, legacy_before, dispositions, report


def test_rebuild_requires_confirmation(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    shutil.copytree(DATA_DIR, data_dir)
    with pytest.raises(ValueError, match="confirm"):
        rebuild_batch_content_risk_dispositions(
            data_root=data_dir / "new_material_learning",
            intake_dir=data_dir / "source_intake",
            corpus_dir=data_dir / "classical_sources",
            batch_id="batch_20260714",
        )


def test_rebuild_rejects_exact_death_content(rebuilt) -> None:
    data_dir, _, dispositions, report = rebuilt
    exact_ids = dispositions["exact"]
    assert exact_ids, "fixture expectation: at least one exact record"
    assert report.exact_rejected_count == len(exact_ids)

    candidates = {c.candidate_id: c for c in load_candidate_extracts()}
    units = {u.evidence_id: u for u in load_evidence_units()}
    ledger = load_learning_records(
        data_dir / "new_material_learning" / "batch_20260714_learning_records.json"
    )
    by_record = {r.record_id: r for r in ledger.records}
    promoted_evidence_ids = set()
    for record in ledger.records:
        if record.promoted_evidence_id:
            promoted_evidence_ids.add(record.promoted_evidence_id)
    for record_id in exact_ids:
        record = by_record[record_id]
        assert record.gate_decision == "rejected_safety", record_id
        assert record.risk_tier == "high_risk", record_id
        assert record.mapping_outcome == "high_risk_signal", record_id
        assert not record.promoted_candidate_id and not record.promoted_evidence_id, record_id
    # no batch candidate may carry exact content in a report-usable state, and
    # no ordinary candidate at all may carry death/lifespan content
    for candidate in candidates.values():
        if candidate.status not in {"approved", "promoted"}:
            continue
        risk = classify_evidence_content(candidate.extracted_meaning, candidate.proposed_limitations)
        if candidate.candidate_id.startswith("candidate_batch_20260714_"):
            assert risk.risk_class != EXACT_DEATH_LIFESPAN_RULE, candidate.candidate_id
        if candidate.risk_tier == "ordinary":
            assert risk.risk_class == ORDINARY_CONTENT, candidate.candidate_id
    for unit in units.values():
        risk = classify_evidence_content(unit.summary, unit.limitations)
        assert risk.risk_class != EXACT_DEATH_LIFESPAN_RULE or unit.risk_tier != "ordinary", unit.evidence_id
    # promotion batch and curation batch only cover surviving pairs
    batches = json.loads(
        (data_dir / "source_intake" / "promotion_batches.json").read_text(encoding="utf-8")
    )
    batch = next(b for b in batches if b["promotion_batch_id"] == "promotion_batch_20260714_001")
    assert len(batch["candidate_ids"]) == len(dispositions["descriptive"]) + len(
        dispositions["ordinary"]
    )
    assert len(batch["candidate_ids"]) == len(batch["target_evidence_ids"])
    curations = load_curation_batches(data_dir / "classical_sources")
    curation = next(b for b in curations if b.batch_id == "batch_new_material_20260714_001")
    assert set(curation.evidence_ids) == set(batch["target_evidence_ids"])


def test_rebuild_relabels_descriptive_content(rebuilt) -> None:
    _, _, dispositions, report = rebuilt
    descriptive_ids = dispositions["descriptive"]
    assert descriptive_ids, "fixture expectation: at least one descriptive record"
    assert report.descriptive_relabelled_count == len(descriptive_ids)

    candidates = {c.candidate_id: c for c in load_candidate_extracts()}
    units = {u.evidence_id: u for u in load_evidence_units()}
    ledger_candidates = [
        c for c in candidates.values() if c.candidate_id.startswith("candidate_batch_20260714_")
    ]
    descriptive_candidates = [
        c
        for c in ledger_candidates
        if classify_evidence_content(c.extracted_meaning, c.proposed_limitations).risk_class
        == DESCRIPTIVE_DEATH_CONTENT
    ]
    assert len(descriptive_candidates) == len(descriptive_ids)
    for candidate in descriptive_candidates:
        assert candidate.status == "promoted", candidate.candidate_id
        assert candidate.risk_tier == "high_risk", candidate.candidate_id
        assert candidate.proposed_rule_family == "high_risk_signal", candidate.candidate_id
        assert REQUIRED_DESCRIPTIVE_DEATH_LIMITATION in candidate.proposed_limitations
        for evidence_id in candidate.related_evidence_ids:
            unit = units[evidence_id]
            assert unit.risk_tier == "high_risk", evidence_id
            assert unit.rule_family == "high_risk_signal", evidence_id
            assert REQUIRED_DESCRIPTIVE_DEATH_LIMITATION in unit.limitations, evidence_id


def test_rebuild_keeps_ordinary_content_unchanged(rebuilt) -> None:
    _, _, dispositions, _ = rebuilt
    ordinary_ids = dispositions["ordinary"]
    assert ordinary_ids, "fixture expectation: ordinary records dominate"
    candidates = [
        c
        for c in load_candidate_extracts()
        if c.candidate_id.startswith("candidate_batch_20260714_")
    ]
    ordinary_candidates = [
        c
        for c in candidates
        if classify_evidence_content(c.extracted_meaning, c.proposed_limitations).risk_class
        == ORDINARY_CONTENT
    ]
    assert len(ordinary_candidates) == len(ordinary_ids)
    for candidate in ordinary_candidates:
        assert candidate.status == "promoted", candidate.candidate_id
        assert candidate.risk_tier == "ordinary", candidate.candidate_id
        assert candidate.proposed_rule_family != "high_risk_signal", candidate.candidate_id


def test_rebuild_preserves_legacy_records(rebuilt) -> None:
    data_dir, legacy_before, _, _ = rebuilt
    assert _legacy_snapshot(data_dir) == legacy_before


def test_rebuild_leaves_no_dangling_or_duplicate_references(rebuilt) -> None:
    data_dir, _, _, _ = rebuilt
    assert source_intake.validate_intake_quality(
        data_dir=data_dir / "source_intake",
        classical_data_dir=data_dir / "classical_sources",
    ) == []
    candidates = json.loads(
        (data_dir / "source_intake" / "candidate_extracts.json").read_text(encoding="utf-8")
    )
    units = json.loads(
        (data_dir / "classical_sources" / "evidence_units.json").read_text(encoding="utf-8")
    )
    candidate_ids = [c["candidate_id"] for c in candidates]
    evidence_ids = [u["evidence_id"] for u in units]
    assert len(candidate_ids) == len(set(candidate_ids))
    assert len(evidence_ids) == len(set(evidence_ids))


def test_rebuild_is_idempotent(rebuilt, tmp_path: Path) -> None:
    data_dir, _, _, _ = rebuilt

    def _fingerprint() -> dict[str, str]:
        result: dict[str, str] = {}
        for path in sorted(data_dir.rglob("*.json")):
            result[str(path.relative_to(data_dir))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
        return result

    before = _fingerprint()
    rebuild_batch_content_risk_dispositions(
        data_root=data_dir / "new_material_learning",
        intake_dir=data_dir / "source_intake",
        corpus_dir=data_dir / "classical_sources",
        batch_id="batch_20260714",
        confirm_governed_rebuild=True,
    )
    assert _fingerprint() == before
