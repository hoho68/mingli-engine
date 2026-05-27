from collections import Counter

from mingli_engine.models import (
    CoverageReport,
    ClassicalSource,
    EvidenceUnit,
    REPORT_USABLE_REVIEW_STATUS,
    SourceConflict,
)


SUMMARY_LIMIT = 280


def build_coverage_report(
    sources: list[ClassicalSource],
    evidence_units: list[EvidenceUnit],
    source_conflicts: list[SourceConflict] | None = None,
) -> CoverageReport:
    source_counts = {source.source_id: 0 for source in sources}
    for unit in evidence_units:
        source_counts[unit.source_id] = source_counts.get(unit.source_id, 0) + 1

    rule_family_counts = Counter(unit.rule_family for unit in evidence_units)
    risk_tier_counts = Counter(unit.risk_tier for unit in evidence_units)
    sources_with_gaps = [
        source.source_id
        for source in sources
        if source_counts.get(source.source_id, 0) == 0
        or bool(source.curation_gap_reason.strip())
    ]
    open_conflicts = [
        conflict.conflict_id
        for conflict in source_conflicts or []
        if conflict.resolution_status == "open"
    ]
    high_risk_without_limitations = [
        unit.evidence_id
        for unit in evidence_units
        if unit.risk_tier == "high_risk" and not unit.limitations
    ]
    long_summary_violations = [
        unit.evidence_id
        for unit in evidence_units
        if len(unit.summary) > SUMMARY_LIMIT
    ]

    return CoverageReport(
        source_counts=source_counts,
        rule_family_counts=dict(rule_family_counts),
        risk_tier_counts=dict(risk_tier_counts),
        approved_evidence_count=len(evidence_units),
        sources_with_gaps=sources_with_gaps,
        open_conflicts=open_conflicts,
        high_risk_without_limitations=high_risk_without_limitations,
        long_summary_violations=long_summary_violations,
    )


def validate_curation_quality(
    sources: list[ClassicalSource],
    evidence_units: list[EvidenceUnit],
    source_conflicts: list[SourceConflict] | None = None,
) -> list[str]:
    report = build_coverage_report(sources, evidence_units, source_conflicts)
    failures: list[str] = []
    sources_by_id = {source.source_id: source for source in sources}

    for evidence_id in report.long_summary_violations:
        failures.append(f"{evidence_id} summary is too long")
    for evidence_id in report.high_risk_without_limitations:
        failures.append(f"{evidence_id} high_risk unit requires limitations")
    for source in sources:
        if report.source_counts.get(source.source_id, 0) == 0 and not source.curation_gap_reason:
            failures.append(f"{source.source_id} has no evidence and no curation gap")
    for unit in evidence_units:
        source = sources_by_id.get(unit.source_id)
        if source is None:
            failures.append(
                f"{unit.evidence_id} references unknown source {unit.source_id}"
            )
        elif source.review_status != REPORT_USABLE_REVIEW_STATUS:
            failures.append(
                f"{unit.evidence_id} references non-report-usable source "
                f"{unit.source_id}"
            )
    return failures
