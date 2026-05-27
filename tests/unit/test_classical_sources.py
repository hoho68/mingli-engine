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

    assert len(sources) == 9
    assert set(by_id) == set(EXPECTED_INITIAL_SOURCE_FILES)
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
            "limitations": ["Do not use blocked sources."],
        }
    ]
    _write_json(tmp_path / "sources.json", sources)
    _write_json(tmp_path / "evidence_units.json", evidence_units)

    with pytest.raises(ClassicalEvidenceError, match="approved source"):
        load_evidence_units(tmp_path)
