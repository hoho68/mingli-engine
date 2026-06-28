import json
from pathlib import Path

import pytest

from mingli_engine.classical_sources import (
    ClassicalEvidenceError,
    load_approved_evidence_units,
    load_classical_sources,
    load_curation_batches,
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

EXPECTED_BAZI_GENERAL_SOURCE_FILES = {
    "source_bazi_general_lecture_textbook_pdf": "八字命理讲义教材（299页）.pdf",
    "source_bazi_general_beichen_intro_pdf": "北宸学派《命理入门》韩雨墨 258页.pdf",
    "source_bazi_general_ziping_orthodox_pair_pdf": (
        "子平命理正宗电子版上.pdf; 子平命理正宗电子版下.pdf"
    ),
}

PROMOTED_MARKDOWN_LEARNING_EVIDENCE_IDS = {
    "batch001_pattern_strength_001",
    "batch001_ten_god_relation_001",
    "batch001_branch_interaction_001",
    "batch001_blind_image_method_001",
    "batch002_useful_god_comparison_001",
    "batch002_pattern_strength_001",
    "batch002_luck_cycle_001",
    "batch002_ten_god_relation_001",
    "batch004_useful_god_001",
    "batch004_pattern_strength_001",
    "batch004_branch_interaction_001",
    "batch004_luck_cycle_001",
    "batch005_ten_god_relation_001",
    "batch005_blind_image_method_001",
    "batch005_branch_interaction_001",
}


REVIEW_NOTE_TOPIC_EVIDENCE_IDS = {
    "blind_branch_interaction_001",
    "blind_branch_interaction_002",
    "blind_branch_interaction_003",
    "blind_branch_interaction_004",
    "blind_high_risk_signal_001",
    "blind_remedy_boundary_001",
    "blind_school_image_001",
    "blind_school_image_002",
    "duan_pattern_strength_001",
    "duan_taboo_god_candidate_001",
    "duan_taboo_god_candidate_002",
    "duan_ten_god_relation_001",
    "duan_ten_god_relation_002",
    "duan_ten_god_relation_003",
    "duan_useful_god_candidate_001",
    "duan_useful_god_candidate_002",
    "fortune_luck_cycle_001",
    "fortune_remedy_boundary_001",
    "fortune_remedy_boundary_002",
    "fortune_remedy_boundary_003",
    "fortune_remedy_boundary_004",
    "fortune_taboo_god_candidate_001",
    "fortune_ten_god_relation_001",
    "fortune_useful_god_candidate_001",
    "life_death_high_risk_signal_001",
    "mingxue_five_element_balance_001",
    "mingxue_five_element_balance_002",
    "mingxue_five_element_balance_003",
    "mingxue_pattern_strength_001",
    "mingxue_taboo_god_candidate_001",
    "mingxue_ten_god_relation_001",
    "mingxue_ten_god_relation_002",
    "mingxue_useful_god_candidate_001",
    "northeast_blind_image_001",
    "northeast_blind_image_002",
    "northeast_blind_image_003",
    "northeast_blind_image_004",
    "northeast_blind_image_005",
    "northeast_blind_image_006",
    "northeast_branch_interaction_001",
    "northeast_high_risk_signal_001",
    "teacher_luck_cycle_trigger_001",
    "teacher_luck_cycle_trigger_002",
    "teacher_pattern_strength_001",
    "teacher_pattern_strength_002",
    "teacher_pattern_strength_003",
    "teacher_taboo_god_candidate_001",
    "teacher_taboo_god_candidate_002",
    "teacher_ten_god_relation_001",
    "teacher_useful_god_candidate_001",
    "teacher_useful_god_candidate_002",
}


FILE_SECTION_EVIDENCE_IDS = {
    "duan_ten_god_relation_004",
    "fortune_remedy_boundary_005",
    "life_death_book_boundary_signal_001",
    "mingxue_five_element_balance_004",
    "northeast_blind_image_007",
    "teacher_pattern_strength_004",
}


REVIEW_NOTE_SOURCE_WINDOW_EVIDENCE_IDS = (
    REVIEW_NOTE_TOPIC_EVIDENCE_IDS
    | FILE_SECTION_EVIDENCE_IDS
    | {"blind_life_manual_high_risk_boundary_001"}
)


def _assert_markdown_line_locator(locator):
    assert locator.startswith("review-note:Markdown/source_batch_")
    assert "#L" in locator

    source_path_text, line_text = locator.removeprefix("review-note:").rsplit("#L", 1)
    line_number = int(line_text)
    source_path = Path(source_path_text)

    assert source_path.exists(), source_path
    assert 1 <= line_number <= len(source_path.read_text(encoding="utf-8").splitlines())


def _assert_review_note_source_window_locator(locator):
    _review_note_source_window_source_locator(locator)


def _review_note_source_window_source_locator(locator):
    assert locator.startswith("review-note:")
    assert ".md#source-window-" in locator

    file_name, anchor = locator.removeprefix("review-note:").split("#", 1)
    note_path = Path("docs/classical_sources/extracts") / file_name
    heading = f"### {anchor}"

    assert note_path.exists(), note_path
    note_text = note_path.read_text(encoding="utf-8")
    assert heading in note_text

    section = _extract_markdown_section(note_text, heading)
    source_locator = _extract_bulleted_field(section, "Source locator")
    _assert_source_locator_is_precise(source_locator)
    _assert_chapter_locator_has_note(section, source_locator)
    return source_locator


def _extract_markdown_section(markdown, heading):
    heading_line = f"{heading}\n"
    start = markdown.index(heading_line)
    rest = markdown[start + len(heading_line) :]
    next_heading = rest.find("\n### ")
    next_major_heading = rest.find("\n## ")
    ends = [idx for idx in (next_heading, next_major_heading) if idx != -1]
    end = min(ends) if ends else len(rest)
    return rest[:end]


def _extract_bulleted_field(section, field_name):
    prefix = f"- {field_name}: `"
    for line in section.splitlines():
        if line.startswith(prefix) and line.endswith("`"):
            return line.removeprefix(prefix).removesuffix("`")
    raise AssertionError(f"missing {field_name}: {section}")


def _assert_chapter_locator_has_note(section, source_locator):
    if not source_locator.startswith("chapter:"):
        return

    locator_note = _extract_bulleted_field(section, "Locator note")
    assert locator_note.startswith("blocked:"), locator_note
    manual_review_note = _extract_bulleted_field(section, "Manual review note")
    assert manual_review_note.startswith("manual-review:"), manual_review_note
    learning_closure_note = _extract_bulleted_field(section, "Learning closure note")
    assert learning_closure_note.startswith("learning-closure:"), learning_closure_note


def _assert_source_locator_is_precise(locator):
    if locator.startswith("page:"):
        assert "source=" in locator
        assert "heading:" in locator or "section:" in locator
        return

    if locator.startswith("chapter:"):
        assert "source=" in locator
        assert "section=" in locator or "heading:" in locator
        return

    if locator.startswith("Markdown/") and "#L" in locator:
        source_path_text, line_text = locator.rsplit("#L", 1)
        line_number = int(line_text)
        source_path = Path(source_path_text)

        assert source_path.exists(), source_path
        assert 1 <= line_number <= len(
            source_path.read_text(encoding="utf-8").splitlines()
        )
        return

    raise AssertionError(locator)


def _write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_source_registry_includes_all_initial_pdfs():
    sources = load_classical_sources()
    by_id = {source.source_id: source for source in sources}

    assert len(sources) == 17
    assert set(by_id) == set(EXPECTED_INITIAL_SOURCE_FILES) | set(
        EXPECTED_BAZI_GENERAL_SOURCE_FILES
    ) | {
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
    for source_id, file_name in EXPECTED_BAZI_GENERAL_SOURCE_FILES.items():
        source = by_id[source_id]
        assert source.file_name == file_name
        assert source.source_type == "pdf"
        assert source.extraction_status == "partial"
        assert source.review_status == "approved"
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


def test_seeded_curation_batches_reference_existing_sources_and_evidence():
    batches = load_curation_batches()
    evidence_ids = {unit.evidence_id for unit in load_evidence_units()}
    source_ids = {source.source_id for source in load_classical_sources()}

    assert batches
    assert all(
        source_id in source_ids
        for batch in batches
        for source_id in batch.source_ids
    )
    assert all(
        evidence_id in evidence_ids
        for batch in batches
        for evidence_id in batch.evidence_ids
    )


def test_bazi_general_source_preparation_reading_evidence_is_formalized():
    sources_by_id = {source.source_id: source for source in load_classical_sources()}
    evidence_by_id = {unit.evidence_id: unit for unit in load_evidence_units()}
    batches_by_id = {batch.batch_id: batch for batch in load_curation_batches()}

    expected_evidence = {
        "bazi_general_lecture_pattern_strength_001": (
            "source_bazi_general_lecture_textbook_pdf",
            "pattern_strength",
        ),
        "bazi_general_beichen_branch_interaction_001": (
            "source_bazi_general_beichen_intro_pdf",
            "branch_interaction",
        ),
        "bazi_general_ziping_useful_god_001": (
            "source_bazi_general_ziping_orthodox_pair_pdf",
            "useful_god_candidate",
        ),
    }
    for evidence_id, (source_id, rule_family) in expected_evidence.items():
        source = sources_by_id[source_id]
        unit = evidence_by_id[evidence_id]

        assert source.review_status == "approved"
        assert unit.source_id == source_id
        assert unit.source_ref.startswith(("page:", "heading:"))
        assert unit.rule_family == rule_family
        assert unit.risk_tier == "ordinary"
        assert unit.curation_batch_id == "batch_bazi_general_source_preparation_001"
        assert len(unit.summary) <= 280
        assert unit.applicability
        assert unit.limitations

    batch = batches_by_id["batch_bazi_general_source_preparation_001"]
    assert batch.review_status == "reviewed"
    assert batch.source_ids == list(EXPECTED_BAZI_GENERAL_SOURCE_FILES)
    assert batch.evidence_ids == list(expected_evidence)
    assert batch.unresolved_issues == []


def test_promoted_markdown_learning_evidence_uses_source_file_locators():
    evidence_by_id = {unit.evidence_id: unit for unit in load_evidence_units()}

    assert PROMOTED_MARKDOWN_LEARNING_EVIDENCE_IDS <= set(evidence_by_id)
    for evidence_id in PROMOTED_MARKDOWN_LEARNING_EVIDENCE_IDS:
        source_ref = evidence_by_id[evidence_id].source_ref

        _assert_markdown_line_locator(source_ref)
        assert "learning-reference:" not in source_ref
        assert "note_markdown_batch_005_001" not in source_ref


def test_review_note_evidence_uses_precise_source_window_locators():
    evidence_by_id = {unit.evidence_id: unit for unit in load_evidence_units()}

    assert REVIEW_NOTE_SOURCE_WINDOW_EVIDENCE_IDS <= set(evidence_by_id)
    for evidence_id in REVIEW_NOTE_SOURCE_WINDOW_EVIDENCE_IDS:
        source_ref = evidence_by_id[evidence_id].source_ref

        _assert_review_note_source_window_locator(source_ref)


def test_formal_evidence_has_no_legacy_file_section_locators():
    evidence_units = load_evidence_units()
    legacy_file_section_refs = [
        (unit.evidence_id, unit.source_ref)
        for unit in evidence_units
        if unit.source_ref.startswith("review-note:")
        and ".md#" in unit.source_ref
        and "#source-window-" not in unit.source_ref
        and not unit.source_ref.startswith("review-note:Markdown/")
    ]

    assert legacy_file_section_refs == []


def test_source_ref_quality_audit_tracks_source_window_references():
    report = Path("docs/classical_sources/source_ref_quality_audit.md").read_text(
        encoding="utf-8"
    )

    assert "REVIEW_NOTE_TOPIC" not in report
    assert "FILE_SECTION" not in report
    assert "| REVIEW_NOTE_SOURCE_WINDOW | 58 | 60.4% |" in report
    assert "| PAGE_LOCATOR | 44 |" in report
    assert "| CHAPTER_LOCATOR | 12 |" in report
    assert "| MARKDOWN_LINE_LOCATOR | 2 |" in report
    assert "| blocked:rendered-review-no-topic-page-match | 4 |" in report
    assert "| blocked:rendered-review-no-remedy-boundary-page-match | 5 |" in report
    assert "| blocked:rendered-review-no-risk-boundary-page-match | 2 |" in report
    assert "| blocked:blind-life-boundary-only-no-page-review | 1 |" in report
    assert "## OCR/Page Review Pass" in report
    assert "| blind_school_secret_pdf | prior-page-reviewed | 1 |" in report
    assert "| duan_plain_mingxue_outline_pdf | page-reviewed | 5 |" in report
    assert "| duan_plain_mingxue_outline_pdf | rendered-review-blocked | 4 |" in report
    assert "| mingxue_golden_voice_pdf | page-reviewed | 9 |" in report
    assert "| fortune_reading_hongfu_qitian_pdf | page-reviewed | 4 |" in report
    assert "| fortune_reading_hongfu_qitian_pdf | rendered-review-blocked | 5 |" in report
    assert "| northeast_blind_peak_pdf | page-reviewed | 7 |" in report
    assert "| northeast_blind_peak_pdf | rendered-review-blocked | 2 |" in report
    assert "## Manual Review Closure Pass" in report
    assert "| duan_plain_mingxue_outline_pdf | no-single-topic-page | 4 |" in report
    assert (
        "| fortune_reading_hongfu_qitian_pdf | no-remedy-boundary-page | 5 |"
        in report
    )
    assert "| northeast_blind_peak_pdf | page-reviewed | 1 |" in report
    assert "| northeast_blind_peak_pdf | no-risk-boundary-page | 2 |" in report
    assert "## Learning Closure Pass" in report
    assert "| duan_plain_mingxue_outline_pdf | learning-paraphrase-ready | 4 |" in report
    assert (
        "| fortune_reading_hongfu_qitian_pdf | policy-boundary-retained | 5 |"
        in report
    )
    assert "| northeast_blind_peak_pdf | safety-boundary-retained | 2 |" in report
    assert "| blind_life_manual_pdf | boundary-only-retained | 1 |" in report
    assert "| Total | retained-chapter-learning-closed | 12 |" in report
    assert "Converted 51 legacy topic-only review-note references" in report
    assert "Converted 6 legacy file-section review-note references" in report

    inventory = report.split("## Detailed Inventory", 1)[1].split(
        "## Recommendations", 1
    )[0]
    for line in inventory.splitlines():
        if not line.startswith("| ") or line.startswith("| Evidence ID"):
            continue
        if set(line.replace("|", "").strip()) == {"-"}:
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        evidence_id = cells[0]
        source_ref = cells[5].strip("`")
        source_locator = cells[6].strip("`")
        precision = cells[7]

        if precision != "REVIEW_NOTE_SOURCE_WINDOW":
            continue

        expected_locator = _review_note_source_window_source_locator(source_ref)
        assert source_locator == expected_locator, evidence_id


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
