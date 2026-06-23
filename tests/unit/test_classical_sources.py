import json

import pytest

from mingli_engine.classical_sources import (
    ClassicalEvidenceError,
    load_approved_evidence_units,
    load_classical_sources,
    load_evidence_units,
)


EXPECTED_INITIAL_SOURCE_FILES = {
    "northeast_blind_peak": "东北盲派巅峰.pdf",
    "duan_plain_mingxue_outline": "段氏白話命學綱要（2014年，心一堂出版，段方撰，编号82132）.pdf",
    "blind_school_secret": "盲派绝学.pdf",
    "blind_life_manual": "盲人断命秘典.pdf",
    "mingli_true_formula_teacher": "命理真诀师传.pdf",
    "mingxue_golden_voice": "命學金聲（2016，心一堂出版，黃雲樵作，编号150788）.pdf",
    "fortune_reading_hongfu_qitian": "算命一讀通：鴻福齊天（2013年，心一堂出版，不空居士, 覺先居士合纂，编号85862）.pdf",
    "immortal_fortune_jianghu_secret": "[神仙算命术江湖秘本.pdf",
    "life_death_book_100_pages": "2800.《命理生死之书》100页.pdf",
}


def _write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_source_registry_includes_all_initial_pdfs():
    sources = load_classical_sources()
    by_id = {source.source_id: source for source in sources}

    assert len(sources) == 14
    assert set(by_id) == set(EXPECTED_INITIAL_SOURCE_FILES) | {
        "markdown_source_batch_001",
        "markdown_source_batch_002_core",
        "markdown_source_batch_004",
        "markdown_source_batch_005",
        "knowledge_skeleton",
    }
    assert len(by_id) == len(sources)
    for source_id, file_name in EXPECTED_INITIAL_SOURCE_FILES.items():
        source = by_id[source_id]
        assert source.file_name == file_name
        assert source.source_type == "pdf"
        assert source.extraction_status in {
            "not_started",
            "converted",
            "partial",
            "failed",
        }
        assert source.review_status in {
            "unreviewed",
            "reviewed",
            "approved",
            "blocked",
        }
        assert source.scope_notes


def test_each_initial_source_has_approved_evidence_or_explicit_gap_reason():
    sources = load_classical_sources()
    evidence_units = load_approved_evidence_units()
    evidence_source_ids = {unit.source_id for unit in evidence_units}

    for source in sources:
        if source.source_id not in evidence_source_ids:
            assert source.curation_gap_reason, source.source_id


def test_approved_evidence_units_link_only_to_approved_sources():
    sources_by_id = {source.source_id: source for source in load_classical_sources()}
    evidence_units = load_approved_evidence_units()

    assert evidence_units
    assert {"ordinary", "sensitive", "high_risk"}.issubset(
        {unit.risk_tier for unit in evidence_units}
    )
    for unit in evidence_units:
        assert unit.source_id in sources_by_id
        assert sources_by_id[unit.source_id].review_status == "approved"
        assert unit.evidence_id
        assert unit.source_ref
        assert unit.rule_family
        assert unit.summary
        assert len(unit.summary) <= 280
        assert unit.curation_batch_id
        assert unit.applicability
        if unit.risk_tier == "high_risk":
            assert unit.limitations


def test_loader_rejects_duplicate_source_ids(tmp_path):
    duplicate_sources = [
        {
            "source_id": "same",
            "title": "First",
            "file_name": "first.pdf",
            "source_type": "pdf",
            "extraction_status": "converted",
            "review_status": "approved",
            "scope_notes": "First reviewed source.",
            "risk_notes": [],
        },
        {
            "source_id": "same",
            "title": "Second",
            "file_name": "second.pdf",
            "source_type": "pdf",
            "extraction_status": "converted",
            "review_status": "approved",
            "scope_notes": "Second reviewed source.",
            "risk_notes": [],
        },
    ]
    _write_json(tmp_path / "sources.json", duplicate_sources)

    with pytest.raises(ClassicalEvidenceError, match="duplicate source_id"):
        load_classical_sources(tmp_path)


def test_blocked_or_unreviewed_sources_cannot_support_evidence_units(tmp_path):
    sources = [
        {
            "source_id": "blocked_source",
            "title": "Blocked Source",
            "file_name": "blocked.pdf",
            "source_type": "pdf",
            "extraction_status": "converted",
            "review_status": "blocked",
            "scope_notes": "Registered but blocked.",
            "risk_notes": ["high_risk_signal"],
        }
    ]
    evidence_units = [
        {
            "evidence_id": "blocked_signal",
            "source_id": "blocked_source",
            "source_ref": "review-note:blocked",
            "theme": "high-risk signal",
            "rule_family": "high_risk_signal",
            "risk_tier": "high_risk",
            "school": "test",
            "summary": "Blocked sources cannot support conclusions.",
            "applicability": ["four_pillars_complete"],
            "limitations": ["拒绝精确结果；Do not use blocked sources."],
        }
    ]
    _write_json(tmp_path / "sources.json", sources)
    _write_json(tmp_path / "evidence_units.json", evidence_units)

    with pytest.raises(ClassicalEvidenceError, match="approved source"):
        load_evidence_units(tmp_path)


def test_expanded_curation_metadata_is_loaded(tmp_path):
    sources = [
        {
            "source_id": "approved_source",
            "title": "Approved Source",
            "file_name": "approved.pdf",
            "source_type": "pdf",
            "extraction_status": "converted",
            "review_status": "approved",
            "scope_notes": "Reviewed source.",
            "risk_notes": [],
            "curation_gap_reason": "",
            "review_reference": "docs/classical_sources/extracts/approved_source.md",
        }
    ]
    evidence_units = [
        {
            "evidence_id": "approved_signal",
            "source_id": "approved_source",
            "source_ref": "page:12; heading:格局",
            "theme": "格局",
            "rule_family": "pattern_strength",
            "risk_tier": "ordinary",
            "school": "test",
            "summary": "格局判断需要结合月令、根气与干支配合。",
            "applicability": ["four_pillars_complete"],
            "limitations": ["证据不足时只列候选。"],
            "curation_batch_id": "batch_001",
            "confidence": "moderate",
            "source_quality": "direct_extract",
            "conflict_ids": [],
        }
    ]
    batches = [
        {
            "batch_id": "batch_001",
            "source_ids": ["approved_source"],
            "evidence_ids": ["approved_signal"],
            "review_status": "approved",
            "review_notes": "Initial approved test batch.",
            "unresolved_issues": [],
        }
    ]
    _write_json(tmp_path / "sources.json", sources)
    _write_json(tmp_path / "evidence_units.json", evidence_units)
    _write_json(tmp_path / "curation_batches.json", batches)
    _write_json(tmp_path / "source_conflicts.json", [])

    source = load_classical_sources(tmp_path)[0]
    unit = load_evidence_units(tmp_path)[0]

    assert source.curation_gap_reason == ""
    assert source.review_reference.endswith("approved_source.md")
    assert unit.curation_batch_id == "batch_001"
    assert unit.confidence == "moderate"
    assert unit.source_quality == "direct_extract"
    assert unit.conflict_ids == []


def test_loader_rejects_evidence_without_a_source_reference_prefix(tmp_path):
    sources = [
        {
            "source_id": "approved_source",
            "title": "Approved Source",
            "file_name": "approved.pdf",
            "source_type": "pdf",
            "extraction_status": "converted",
            "review_status": "approved",
            "scope_notes": "Reviewed source.",
            "risk_notes": [],
        }
    ]
    evidence_units = [
        {
            "evidence_id": "bad_ref",
            "source_id": "approved_source",
            "source_ref": "unanchored note",
            "theme": "格局",
            "rule_family": "pattern_strength",
            "risk_tier": "ordinary",
            "school": "test",
            "summary": "Missing a usable source reference prefix.",
            "applicability": ["four_pillars_complete"],
            "limitations": ["Needs a source reference."],
        }
    ]
    _write_json(tmp_path / "sources.json", sources)
    _write_json(tmp_path / "evidence_units.json", evidence_units)

    with pytest.raises(ClassicalEvidenceError, match="source_ref"):
        load_evidence_units(tmp_path)


def test_curation_batch_loader_validates_cross_references(tmp_path):
    from mingli_engine.classical_sources import load_curation_batches

    sources = [
        {
            "source_id": "approved_source",
            "title": "Approved Source",
            "file_name": "approved.pdf",
            "source_type": "pdf",
            "extraction_status": "converted",
            "review_status": "approved",
            "scope_notes": "Reviewed source.",
            "risk_notes": [],
        }
    ]
    evidence_units = [
        {
            "evidence_id": "approved_signal",
            "source_id": "approved_source",
            "source_ref": "review-note:approved",
            "theme": "格局",
            "rule_family": "pattern_strength",
            "risk_tier": "ordinary",
            "school": "test",
            "summary": "A reviewed signal.",
            "applicability": ["four_pillars_complete"],
            "limitations": ["Use as candidate."],
            "curation_batch_id": "batch_001",
        }
    ]
    batches = [
        {
            "batch_id": "batch_001",
            "source_ids": ["missing_source"],
            "evidence_ids": ["approved_signal"],
            "review_status": "approved",
            "review_notes": "Invalid source reference.",
            "unresolved_issues": [],
        }
    ]
    _write_json(tmp_path / "sources.json", sources)
    _write_json(tmp_path / "evidence_units.json", evidence_units)
    _write_json(tmp_path / "curation_batches.json", batches)

    with pytest.raises(ClassicalEvidenceError, match="unknown source"):
        load_curation_batches(tmp_path)


def test_source_conflict_loader_validates_evidence_references(tmp_path):
    from mingli_engine.classical_sources import load_source_conflicts

    sources = [
        {
            "source_id": "approved_source",
            "title": "Approved Source",
            "file_name": "approved.pdf",
            "source_type": "pdf",
            "extraction_status": "converted",
            "review_status": "approved",
            "scope_notes": "Reviewed source.",
            "risk_notes": [],
        }
    ]
    evidence_units = [
        {
            "evidence_id": "approved_signal",
            "source_id": "approved_source",
            "source_ref": "review-note:approved",
            "theme": "格局",
            "rule_family": "pattern_strength",
            "risk_tier": "ordinary",
            "school": "test",
            "summary": "A reviewed signal.",
            "applicability": ["four_pillars_complete"],
            "limitations": ["Use as candidate."],
        }
    ]
    conflicts = [
        {
            "conflict_id": "conflict_001",
            "rule_family": "pattern_strength",
            "evidence_ids": ["approved_signal", "missing_signal"],
            "conflict_type": "school_difference",
            "reader_note": "Different schools use different priority.",
            "severity": "moderate",
            "resolution_status": "documented",
        }
    ]
    _write_json(tmp_path / "sources.json", sources)
    _write_json(tmp_path / "evidence_units.json", evidence_units)
    _write_json(tmp_path / "source_conflicts.json", conflicts)

    with pytest.raises(ClassicalEvidenceError, match="unknown evidence"):
        load_source_conflicts(tmp_path)


def test_source_conflict_loader_allows_documented_and_open_conflicts(tmp_path):
    from mingli_engine.classical_sources import load_source_conflicts

    sources = [
        {
            "source_id": "approved_source",
            "title": "Approved Source",
            "file_name": "approved.pdf",
            "source_type": "pdf",
            "extraction_status": "converted",
            "review_status": "approved",
            "scope_notes": "Reviewed source.",
            "risk_notes": [],
        }
    ]
    evidence_units = [
        {
            "evidence_id": "signal_a",
            "source_id": "approved_source",
            "source_ref": "review-note:a",
            "theme": "格局",
            "rule_family": "pattern_strength",
            "risk_tier": "ordinary",
            "school": "school a",
            "summary": "A reviewed signal.",
            "applicability": ["four_pillars_complete"],
            "limitations": ["Use as candidate."],
        },
        {
            "evidence_id": "signal_b",
            "source_id": "approved_source",
            "source_ref": "review-note:b",
            "theme": "格局",
            "rule_family": "pattern_strength",
            "risk_tier": "ordinary",
            "school": "school b",
            "summary": "Another reviewed signal.",
            "applicability": ["four_pillars_complete"],
            "limitations": ["Use as candidate."],
        },
    ]
    conflicts = [
        {
            "conflict_id": "conflict_documented",
            "rule_family": "pattern_strength",
            "evidence_ids": ["signal_a", "signal_b"],
            "conflict_type": "school_difference",
            "reader_note": "Different schools prioritize structure differently.",
            "severity": "moderate",
            "resolution_status": "documented",
        },
        {
            "conflict_id": "conflict_open",
            "rule_family": "pattern_strength",
            "evidence_ids": ["signal_a", "signal_b"],
            "conflict_type": "textual_disagreement",
            "reader_note": "Open severe conflict.",
            "severity": "severe",
            "resolution_status": "open",
        },
    ]
    _write_json(tmp_path / "sources.json", sources)
    _write_json(tmp_path / "evidence_units.json", evidence_units)
    _write_json(tmp_path / "source_conflicts.json", conflicts)

    loaded = load_source_conflicts(tmp_path)

    assert [conflict.conflict_id for conflict in loaded] == [
        "conflict_documented",
        "conflict_open",
    ]
