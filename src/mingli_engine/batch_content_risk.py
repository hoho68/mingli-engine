"""Governed content-risk rebuild for batch_20260714 derived records.

This module re-derives ONLY batch-derived records — ``candidate_batch_20260714_*``,
``review_candidate_batch_20260714_*``, ``b20260714_evidence_*`` and the batch
promotion/curation entries — after the evidence-content risk gate
(:mod:`mingli_engine.evidence_risk`) was added to the promotion pipeline:

- ``exact_death_lifespan_rule`` records are rejected (``rejected_safety``,
  candidate ``rejected``, evidence unit removed) — they keep their learning
  record but never reach the report-usable chain;
- ``descriptive_death_content`` records stay promoted but are relabelled
  ``high_risk`` + ``high_risk_signal`` and gain the required boundary
  limitation;
- ``ordinary_content`` records are untouched.

Legacy (non-batch) records are snapshotted before the rebuild and verified
byte-identical afterwards; any failure restores every mutated file. The
transform is deterministic and idempotent: a second run produces byte-identical
files.
"""

import json
from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

from mingli_engine import classical_sources, source_intake
from mingli_engine.evidence_risk import (
    DESCRIPTIVE_DEATH_CONTENT,
    EXACT_DEATH_LIFESPAN_GATE_REASON,
    EXACT_DEATH_LIFESPAN_RULE,
    ORDINARY_CONTENT,
    REQUIRED_DESCRIPTIVE_DEATH_LIMITATION,
    EvidenceContentRisk,
    classify_evidence_content,
)
from mingli_engine.evidence_curation import validate_curation_quality
from mingli_engine.new_material_learning import (
    DEFAULT_BATCH_ID,
    ManifestError,
    _load_extraction_ledger_chain,
    _write_json_array,
    build_multi_tranche_file_results,
    load_file_results,
    load_learning_records,
    write_file_results,
    write_learning_records,
)

REPORT_SCHEMA_VERSION = "batch-content-risk-dispositions-v1"

PROMOTION_BATCH_ID = "promotion_batch_20260714_001"
CURATION_BATCH_ID = "batch_new_material_20260714_001"

ACTION_REJECT_NOT_PROMOTED = "reject_not_promoted"
ACTION_PROMOTE_AS_HIGH_RISK_SIGNAL = "promote_as_high_risk_signal"
ACTION_KEEP_ORDINARY = "keep_ordinary"

CONTENT_RISK_REJECTION_REASON = (
    "Rejected under the batch_20260714 content-risk remediation: exact death "
    "or lifespan prediction content is not promotable to report-usable "
    "knowledge."
)

_BATCH_ID_PREFIXES = (
    "candidate_batch_20260714_",
    "review_candidate_batch_20260714_",
    "b20260714_evidence_",
    "material_batch_20260714_",
    "source_batch_20260714_",
    "promotion_batch_20260714_",
    "batch_new_material_20260714_",
)

_ENTRY_ID_KEYS = (
    "candidate_id",
    "decision_id",
    "evidence_id",
    "material_id",
    "source_id",
    "promotion_batch_id",
    "batch_id",
)


@dataclass(frozen=True)
class ContentRiskDisposition:
    record_id: str
    candidate_id: str
    evidence_id: str
    risk_class: str
    matched_marker: str
    matched_field: str
    promotion_action: str
    final_risk_tier: str
    final_rule_family: str
    report_usable: bool
    required_limitation: str


@dataclass(frozen=True)
class ContentRiskRebuildReport:
    batch_id: str
    eligible_total: int
    exact_rejected_count: int
    descriptive_relabelled_count: int
    ordinary_kept_count: int
    dispositions: tuple[ContentRiskDisposition, ...]
    report_path: str


def _is_batch_entry(entry: dict[str, Any]) -> bool:
    for key in _ENTRY_ID_KEYS:
        value = entry.get(key)
        if isinstance(value, str) and any(
            value.startswith(prefix) for prefix in _BATCH_ID_PREFIXES
        ):
            return True
    return False


def _legacy_fingerprint(entries: Iterable[dict[str, Any]]) -> str:
    legacy = [entry for entry in entries if not _is_batch_entry(entry)]
    canonical = json.dumps(legacy, ensure_ascii=False, sort_keys=True)
    return sha256(canonical.encode("utf-8")).hexdigest()


def _read_array(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not all(isinstance(i, dict) for i in payload):
        raise ManifestError(f"{path.name} must contain a JSON array of objects")
    return payload


def rebuild_batch_content_risk_dispositions(
    *,
    data_root: Path | str,
    intake_dir: Path | str,
    corpus_dir: Path | str,
    batch_id: str = DEFAULT_BATCH_ID,
    confirm_governed_rebuild: bool = False,
) -> ContentRiskRebuildReport:
    if not confirm_governed_rebuild:
        raise ValueError(
            "the governed content-risk rebuild requires "
            "confirm_governed_rebuild=True"
        )
    if batch_id != DEFAULT_BATCH_ID:
        raise ManifestError("the requested learning batch is unsupported")

    data_root = Path(data_root)
    intake_dir = Path(intake_dir)
    corpus_dir = Path(corpus_dir)
    ledger_path = data_root / f"{batch_id}_learning_records.json"
    file_results_path = data_root / f"{batch_id}_file_results.json"
    report_path = data_root / f"{batch_id}_content_risk_dispositions.json"
    candidates_path = intake_dir / "candidate_extracts.json"
    reviews_path = intake_dir / "review_decisions.json"
    batches_path = intake_dir / "promotion_batches.json"
    sources_path = corpus_dir / "sources.json"
    evidence_path = corpus_dir / "evidence_units.json"
    curation_path = corpus_dir / "curation_batches.json"

    ledger = load_learning_records(ledger_path)
    (
        manifest,
        authorizations,
        probe,
        tranches,
        _,
        _,
        outputs,
        _,
    ) = _load_extraction_ledger_chain(data_root, batch_id)

    candidates_raw = _read_array(candidates_path)
    reviews_raw = _read_array(reviews_path)
    batches_raw = _read_array(batches_path)
    sources_raw = _read_array(sources_path)
    evidence_raw = _read_array(evidence_path)
    curation_raw = _read_array(curation_path)

    legacy_before = {
        path.name: _legacy_fingerprint(payload)
        for path, payload in (
            (candidates_path, candidates_raw),
            (reviews_path, reviews_raw),
            (batches_path, batches_raw),
            (sources_path, sources_raw),
            (evidence_path, evidence_raw),
            (curation_path, curation_raw),
        )
    }

    # --- classify every promoted rule candidate ---------------------------
    record_by_id = {record.record_id: record for record in ledger.records}
    eligible_risks: dict[str, EvidenceContentRisk] = {}
    for record in ledger.records:
        if record.kind != "rule_candidate":
            continue
        if record.gate_decision == "eligible":
            risk = classify_evidence_content(
                record.payload["conclusion"], record.payload["limitations"]
            )
            eligible_risks[record.record_id] = risk

    exact_ids = {
        record_id
        for record_id, risk in eligible_risks.items()
        if risk.risk_class == EXACT_DEATH_LIFESPAN_RULE
    }
    descriptive_ids = {
        record_id
        for record_id, risk in eligible_risks.items()
        if risk.risk_class == DESCRIPTIVE_DEATH_CONTENT
    }

    exact_candidate_ids = {
        record_by_id[record_id].promoted_candidate_id for record_id in exact_ids
    }
    exact_evidence_ids = {
        record_by_id[record_id].promoted_evidence_id for record_id in exact_ids
    }
    descriptive_candidate_ids = {
        record_by_id[record_id].promoted_candidate_id
        for record_id in descriptive_ids
    }
    descriptive_evidence_ids = {
        record_by_id[record_id].promoted_evidence_id
        for record_id in descriptive_ids
    }

    mutable_paths = [
        candidates_path,
        reviews_path,
        batches_path,
        sources_path,
        evidence_path,
        curation_path,
        ledger_path,
        file_results_path,
    ]
    rollback_bytes = {path: path.read_bytes() for path in mutable_paths}
    report_existed = report_path.exists()
    report_bytes = report_path.read_bytes() if report_existed else b""

    try:
        # --- learning records --------------------------------------------
        new_records = []
        for record in ledger.records:
            if record.record_id in exact_ids:
                new_records.append(
                    replace(
                        record,
                        mapping_outcome="high_risk_signal",
                        gate_decision="rejected_safety",
                        gate_reason=EXACT_DEATH_LIFESPAN_GATE_REASON,
                        risk_tier="high_risk",
                        promoted_candidate_id="",
                        promoted_evidence_id="",
                    )
                )
            elif record.record_id in descriptive_ids:
                new_records.append(
                    replace(
                        record,
                        mapping_outcome="high_risk_signal",
                        risk_tier="high_risk",
                    )
                )
            else:
                new_records.append(record)
        new_ledger = replace(ledger, records=tuple(new_records))

        # --- candidates ---------------------------------------------------
        for entry in candidates_raw:
            candidate_id = entry.get("candidate_id", "")
            if candidate_id in exact_candidate_ids:
                entry["status"] = "rejected"
                entry["risk_tier"] = "high_risk"
                entry["related_evidence_ids"] = []
            elif candidate_id in descriptive_candidate_ids:
                entry["risk_tier"] = "high_risk"
                entry["proposed_rule_family"] = "high_risk_signal"
                if (
                    REQUIRED_DESCRIPTIVE_DEATH_LIMITATION
                    not in entry["proposed_limitations"]
                ):
                    entry["proposed_limitations"].append(
                        REQUIRED_DESCRIPTIVE_DEATH_LIMITATION
                    )

        # --- review decisions ---------------------------------------------
        for entry in reviews_raw:
            if entry.get("candidate_id", "") in exact_candidate_ids:
                entry["decision"] = "rejected"
                entry["rejection_reason"] = CONTENT_RISK_REJECTION_REASON
                entry["approval_limitations"] = []

        # --- promotion batch ----------------------------------------------
        for entry in batches_raw:
            if entry.get("promotion_batch_id") == PROMOTION_BATCH_ID:
                pairs = [
                    (candidate_id, evidence_id)
                    for candidate_id, evidence_id in zip(
                        entry["candidate_ids"], entry["target_evidence_ids"]
                    )
                    if candidate_id not in exact_candidate_ids
                ]
                entry["candidate_ids"] = [candidate for candidate, _ in pairs]
                entry["target_evidence_ids"] = [evidence for _, evidence in pairs]

        # --- evidence units ------------------------------------------------
        evidence_raw = [
            unit
            for unit in evidence_raw
            if unit.get("evidence_id", "") not in exact_evidence_ids
        ]
        for unit in evidence_raw:
            if unit.get("evidence_id", "") in descriptive_evidence_ids:
                unit["risk_tier"] = "high_risk"
                unit["rule_family"] = "high_risk_signal"
                if REQUIRED_DESCRIPTIVE_DEATH_LIMITATION not in unit["limitations"]:
                    unit["limitations"].append(REQUIRED_DESCRIPTIVE_DEATH_LIMITATION)

        # --- curation batch -------------------------------------------------
        for entry in curation_raw:
            if entry.get("batch_id") == CURATION_BATCH_ID:
                entry["evidence_ids"] = [
                    evidence_id
                    for evidence_id in entry["evidence_ids"]
                    if evidence_id not in exact_evidence_ids
                ]

        # --- batch source risk notes (mirrors promote_learning_records) ----
        high_risk_paths = {
            record.relative_path
            for record in new_records
            if record.kind == "rule_candidate"
            and record.gate_decision == "eligible"
            and record.risk_tier == "high_risk"
        }
        manifest_index_by_path = {
            item.relative_path: index
            for index, item in enumerate(manifest.files, start=1)
        }
        sha_by_path = {item.relative_path: item.sha256 for item in manifest.files}
        high_risk_source_ids = {
            f"source_batch_20260714_{sha_by_path[path][:12].lower()}_"
            f"{manifest_index_by_path[path]:03d}"
            for path in high_risk_paths
            if path in sha_by_path
        }
        for entry in sources_raw:
            source_id = entry.get("source_id", "")
            if source_id.startswith("source_batch_20260714_"):
                entry["risk_notes"] = (
                    ["high_risk_signal"]
                    if source_id in high_risk_source_ids
                    else []
                )

        # --- file results (regenerated from the transformed ledger) -------
        file_results = build_multi_tranche_file_results(
            manifest,
            authorizations,
            probe,
            tranches,
            new_ledger,
            generated_at=load_file_results(file_results_path).generated_at,
        )

        # --- disposition report (derived from the post-rebuild state so the
        # report itself is idempotent: a second run yields identical bytes) --
        dispositions: list[ContentRiskDisposition] = []
        post_eligible_total = 0
        post_descriptive_count = 0
        post_ordinary_count = 0
        post_exact_rejected_count = 0
        for record in new_records:
            if record.kind != "rule_candidate":
                continue
            risk = classify_evidence_content(
                record.payload["conclusion"], record.payload["limitations"]
            )
            if record.gate_decision == "eligible":
                post_eligible_total += 1
                if risk.risk_class == DESCRIPTIVE_DEATH_CONTENT:
                    post_descriptive_count += 1
                    dispositions.append(
                        ContentRiskDisposition(
                            record_id=record.record_id,
                            candidate_id=record.promoted_candidate_id,
                            evidence_id=record.promoted_evidence_id,
                            risk_class=risk.risk_class,
                            matched_marker=risk.matched_marker,
                            matched_field=risk.matched_field,
                            promotion_action=ACTION_PROMOTE_AS_HIGH_RISK_SIGNAL,
                            final_risk_tier="high_risk",
                            final_rule_family="high_risk_signal",
                            report_usable=True,
                            required_limitation=REQUIRED_DESCRIPTIVE_DEATH_LIMITATION,
                        )
                    )
                elif risk.risk_class == ORDINARY_CONTENT:
                    post_ordinary_count += 1
            elif (
                record.gate_decision == "rejected_safety"
                and record.gate_reason == EXACT_DEATH_LIFESPAN_GATE_REASON
            ):
                post_exact_rejected_count += 1
                dispositions.append(
                    ContentRiskDisposition(
                        record_id=record.record_id,
                        candidate_id="",
                        evidence_id="",
                        risk_class=EXACT_DEATH_LIFESPAN_RULE,
                        matched_marker=risk.matched_marker,
                        matched_field=risk.matched_field,
                        promotion_action=ACTION_REJECT_NOT_PROMOTED,
                        final_risk_tier="high_risk",
                        final_rule_family="",
                        report_usable=False,
                        required_limitation="",
                    )
                )

        report_payload = {
            "schema_version": REPORT_SCHEMA_VERSION,
            "batch_id": batch_id,
            "generated_at": ledger.generated_at,
            "summary": {
                "eligible_total": post_eligible_total,
                "exact_rejected": post_exact_rejected_count,
                "descriptive_relabelled": post_descriptive_count,
                "ordinary_kept": post_ordinary_count,
            },
            "legacy_knowledge_sha256": legacy_before,
            "dispositions": [
                {
                    "record_id": item.record_id,
                    "candidate_id": item.candidate_id,
                    "evidence_id": item.evidence_id,
                    "risk_class": item.risk_class,
                    "matched_marker": item.matched_marker,
                    "matched_field": item.matched_field,
                    "promotion_action": item.promotion_action,
                    "final_risk_tier": item.final_risk_tier,
                    "final_rule_family": item.final_rule_family,
                    "report_usable": item.report_usable,
                    "required_limitation": item.required_limitation,
                }
                for item in sorted(dispositions, key=lambda item: item.record_id)
            ],
        }

        # --- write everything ---------------------------------------------
        _write_json_array(candidates_path, candidates_raw)
        _write_json_array(reviews_path, reviews_raw)
        _write_json_array(batches_path, batches_raw)
        _write_json_array(sources_path, sources_raw)
        _write_json_array(evidence_path, evidence_raw)
        _write_json_array(curation_path, curation_raw)
        write_learning_records(
            ledger_path, new_ledger, intake_root=manifest.intake_root
        )
        write_file_results(
            file_results_path, file_results, intake_root=manifest.intake_root
        )
        report_path.write_text(
            json.dumps(
                report_payload, ensure_ascii=False, indent=2, sort_keys=True
            )
            + "\n",
            encoding="utf-8",
        )

        # --- verification ---------------------------------------------------
        failures: list[str] = []
        legacy_after = {
            path.name: _legacy_fingerprint(_read_array(path))
            for path in (
                candidates_path,
                reviews_path,
                batches_path,
                sources_path,
                evidence_path,
                curation_path,
            )
        }
        if legacy_after != legacy_before:
            failures.append("legacy knowledge records changed during rebuild")

        try:
            classical_sources.load_classical_sources(corpus_dir)
            units = classical_sources.load_evidence_units(corpus_dir)
            classical_sources.load_curation_batches(corpus_dir)
            conflicts = classical_sources.load_source_conflicts(corpus_dir)
            source_intake.load_candidate_extracts(intake_dir)
            source_intake.load_review_decisions(intake_dir)
            source_intake.load_promotion_batches(intake_dir)
            source_intake.validate_candidate_links(intake_dir, corpus_dir)
        except (
            classical_sources.ClassicalEvidenceError,
            source_intake.SourceIntakeError,
        ) as error:
            failures.append(str(error))
        else:
            intake_issues = source_intake.validate_intake_quality(
                intake_dir, classical_data_dir=corpus_dir
            )
            failures.extend(intake_issues)
            sources = classical_sources.load_classical_sources(corpus_dir)
            failures.extend(validate_curation_quality(sources, units, conflicts))

        load_learning_records(ledger_path)
        load_file_results(file_results_path)

        if failures:
            raise ManifestError(
                "the content-risk rebuild failed verification: "
                + "; ".join(failures)
            )
    except Exception:
        for path, data in rollback_bytes.items():
            path.write_bytes(data)
        if report_existed:
            report_path.write_bytes(report_bytes)
        elif report_path.exists():
            report_path.unlink()
        raise

    return ContentRiskRebuildReport(
        batch_id=batch_id,
        eligible_total=post_eligible_total,
        exact_rejected_count=post_exact_rejected_count,
        descriptive_relabelled_count=post_descriptive_count,
        ordinary_kept_count=post_ordinary_count,
        dispositions=tuple(dispositions),
        report_path=str(report_path),
    )
