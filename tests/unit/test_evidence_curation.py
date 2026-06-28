from mingli_engine.models import ClassicalSource, EvidenceUnit, SourceConflict


def test_project_corpus_coverage_exposes_per_source_counts_and_gaps():
    from mingli_engine.classical_sources import (
        load_approved_evidence_units,
        load_classical_sources,
    )
    from mingli_engine.evidence_curation import build_coverage_report

    sources = load_classical_sources()
    evidence_units = load_approved_evidence_units()

    report = build_coverage_report(sources, evidence_units)

    assert set(report.source_counts) == {source.source_id for source in sources}
    for source in sources:
        if report.source_counts[source.source_id] == 0:
            assert source.curation_gap_reason, source.source_id
            assert source.source_id in report.sources_with_gaps


def test_project_corpus_meets_taxonomy_and_risk_tier_targets():
    from mingli_engine.classical_sources import (
        load_approved_evidence_units,
        load_classical_sources,
    )
    from mingli_engine.evidence_curation import build_coverage_report

    report = build_coverage_report(
        load_classical_sources(),
        load_approved_evidence_units(),
    )

    assert report.approved_evidence_count >= 60
    assert len(report.rule_family_counts) >= 8
    assert {
        "pattern_strength",
        "useful_god_candidate",
        "taboo_god_candidate",
        "ten_god_relation",
        "branch_interaction",
        "blind_image_method",
        "luck_cycle",
        "remedy_boundary",
        "high_risk_signal",
    }.issubset(report.rule_family_counts)
    assert {"ordinary", "sensitive", "high_risk"}.issubset(
        report.risk_tier_counts
    )


def test_build_coverage_report_counts_sources_families_risks_and_gaps():
    from mingli_engine.evidence_curation import build_coverage_report

    sources = [
        ClassicalSource(
            source_id="source_with_evidence",
            title="Source With Evidence",
            file_name="source.pdf",
            source_type="pdf",
            extraction_status="converted",
            review_status="approved",
            scope_notes="Reviewed source.",
            risk_notes=[],
        ),
        ClassicalSource(
            source_id="source_with_gap",
            title="Source With Gap",
            file_name="gap.pdf",
            source_type="pdf",
            extraction_status="failed",
            review_status="blocked",
            scope_notes="Extraction failed.",
            risk_notes=[],
            curation_gap_reason="Extraction failed.",
        ),
    ]
    evidence_units = [
        EvidenceUnit(
            evidence_id="ordinary_signal",
            source_id="source_with_evidence",
            source_ref="review-note:ordinary",
            theme="鏍煎眬",
            rule_family="pattern_strength",
            risk_tier="ordinary",
            summary="A concise ordinary signal.",
            applicability=["four_pillars_complete"],
            limitations=["Use as candidate."],
        ),
        EvidenceUnit(
            evidence_id="high_risk_signal",
            source_id="source_with_evidence",
            source_ref="review-note:risk",
            theme="椋庨櫓",
            rule_family="high_risk_signal",
            risk_tier="high_risk",
            summary="A concise high-risk signal.",
            applicability=["high_risk_context_allowed"],
            limitations=[],
        ),
    ]
    conflicts = [
        SourceConflict(
            conflict_id="conflict_001",
            rule_family="pattern_strength",
            evidence_ids=["ordinary_signal"],
            conflict_type="school_difference",
            reader_note="Documented difference.",
            severity="moderate",
            resolution_status="open",
        )
    ]

    report = build_coverage_report(sources, evidence_units, conflicts)

    assert report.source_counts == {"source_with_evidence": 2, "source_with_gap": 0}
    assert report.rule_family_counts["pattern_strength"] == 1
    assert report.rule_family_counts["high_risk_signal"] == 1
    assert report.risk_tier_counts["ordinary"] == 1
    assert report.risk_tier_counts["high_risk"] == 1
    assert report.approved_evidence_count == 2
    assert report.sources_with_gaps == ["source_with_gap"]
    assert report.open_conflicts == ["conflict_001"]
    assert report.high_risk_without_limitations == ["high_risk_signal"]


def test_validate_curation_quality_reports_blocking_failures():
    from mingli_engine.evidence_curation import validate_curation_quality

    sources = [
        ClassicalSource(
            source_id="approved_source",
            title="Approved Source",
            file_name="approved.pdf",
            source_type="pdf",
            extraction_status="converted",
            review_status="approved",
            scope_notes="Reviewed source.",
            risk_notes=[],
        )
    ]
    evidence_units = [
        EvidenceUnit(
            evidence_id="long_signal",
            source_id="approved_source",
            source_ref="review-note:long",
            theme="鏍煎眬",
            rule_family="pattern_strength",
            risk_tier="ordinary",
            summary="x" * 281,
            applicability=["four_pillars_complete"],
            limitations=["Use as candidate."],
        ),
        EvidenceUnit(
            evidence_id="high_risk_without_limits",
            source_id="approved_source",
            source_ref="review-note:risk",
            theme="椋庨櫓",
            rule_family="high_risk_signal",
            risk_tier="high_risk",
            summary="A high-risk signal.",
            applicability=["high_risk_context_allowed"],
            limitations=[],
        ),
    ]

    failures = validate_curation_quality(sources, evidence_units)

    assert "long_signal summary is too long" in failures
    assert "high_risk_without_limits high_risk unit requires limitations" in failures


def test_project_curation_quality_report_includes_conflicts_and_has_no_failures():
    from mingli_engine.classical_sources import (
        load_approved_evidence_units,
        load_classical_sources,
        load_source_conflicts,
    )
    from mingli_engine.evidence_curation import (
    build_coverage_report,
    validate_curation_quality,
    )

    sources = load_classical_sources()
    evidence_units = load_approved_evidence_units()
    conflicts = load_source_conflicts()

    report = build_coverage_report(sources, evidence_units, conflicts)

    evidence_by_id = {unit.evidence_id: unit for unit in evidence_units}
    blind_life_boundary = evidence_by_id["blind_life_manual_high_risk_boundary_001"]

    assert report.approved_evidence_count == 96
    assert report.open_conflicts == ["conflict_high_risk_scope_001"]
    assert set(report.sources_with_gaps) == {
        "blind_life_manual",
        "immortal_fortune_jianghu_secret",
    }
    assert blind_life_boundary.source_id == "blind_life_manual"
    assert (
        blind_life_boundary.source_ref
        == "review-note:blind_life_manual.md#source-window-high-risk-boundary"
    )
    assert blind_life_boundary.rule_family == "high_risk_signal"
    assert blind_life_boundary.risk_tier == "high_risk"
    assert (
        blind_life_boundary.curation_batch_id
        == "batch_blind_life_manual_high_risk_boundary_001"
    )
    assert blind_life_boundary.conflict_ids == ["conflict_high_risk_scope_001"]
    assert any(
        marker in limitation
        for limitation in blind_life_boundary.limitations
        for marker in ("拒绝", "不得", "exact death")
    )
    assert validate_curation_quality(sources, evidence_units, conflicts) == []


def test_validate_curation_quality_reports_unusable_source_failures():
    from mingli_engine.evidence_curation import validate_curation_quality

    sources = [
        ClassicalSource(
            source_id="blocked_source",
            title="Blocked Source",
            file_name="blocked.pdf",
            source_type="pdf",
            extraction_status="converted",
            review_status="blocked",
            scope_notes="Blocked source.",
            risk_notes=[],
        )
    ]
    evidence_units = [
        EvidenceUnit(
            evidence_id="blocked_signal",
            source_id="blocked_source",
            source_ref="review-note:blocked",
            theme="鏍煎眬",
            rule_family="pattern_strength",
            risk_tier="ordinary",
            summary="A signal that should not be report usable.",
            applicability=["four_pillars_complete"],
            limitations=["Blocked source."],
        ),
        EvidenceUnit(
            evidence_id="unknown_signal",
            source_id="unknown_source",
            source_ref="review-note:unknown",
            theme="鏍煎眬",
            rule_family="pattern_strength",
            risk_tier="ordinary",
            summary="A signal with missing source.",
            applicability=["four_pillars_complete"],
            limitations=["Missing source."],
        ),
    ]

    failures = validate_curation_quality(sources, evidence_units)

    assert "blocked_signal references non-report-usable source blocked_source" in failures
    assert "unknown_signal references unknown source unknown_source" in failures
