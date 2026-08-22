"""Independent liuyao evidence namespace and governed promotion (V1).

Mirrors the batch_20260714 review-pipeline contracts in a liuyao-only
namespace: sources, candidates, review decisions, promotion batches, and
evidence units are stored under ``data/liuyao/`` and never touch the bazi
013/012 chains.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import unicodedata

from importlib import resources
from pathlib import Path

from mingli_engine.high_risk import classify_high_risk_request
from mingli_engine.liuyao.constants import LIUYAO_RULE_FAMILIES
from mingli_engine.new_material_learning import (
    BatchLearningRecord,
    RuleCandidate,
    load_file_results,
    load_learning_records,
    rule_candidate_signature,
)
from mingli_engine.safety import safety_check

LIUYAO_PROMOTION_BATCH_ID = "liuyao_promotion_batch_20260714_001"
LIUYAO_CURATION_BATCH_ID = "liuyao_curation_batch_20260714_001"
_LIUYAO_REVIEW_ACTOR = "liuyao_batch_20260714_review_pipeline"
_LIUYAO_REVIEW_DATE = "2026-08-19"
_PROHIBITED_ABSOLUTE_WORDING = (
    "必定",
    "注定",
    "一定会",
    "死定",
    "guaranteed to",
    "will certainly",
)
_TEXT_LIMIT = 280

_FAMILY_MAP_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "liuyao"
    / "batch_20260714_liuyao_family_map.json"
)
_EXPECTED_FAMILY_MAP_SHA256 = (
    "445ab72638bbee3f2829a141748b8c5ca8e92ec41fad1cfca850115da897dd13"
)


class LiuyaoKnowledgeError(ValueError):
    """Raised when a liuyao knowledge record or promotion is invalid."""


@dataclass(frozen=True)
class LiuyaoSource:
    source_id: str
    title: str
    batch_file_result_id: str
    scope_notes: str
    risk_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "risk_notes", tuple(self.risk_notes))
        for value, field_name in (
            (self.source_id, "source_id"),
            (self.title, "title"),
            (self.batch_file_result_id, "batch_file_result_id"),
            (self.scope_notes, "scope_notes"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"liuyao source {field_name} is required")


@dataclass(frozen=True)
class LiuyaoCandidate:
    candidate_id: str
    source_id: str
    source_locator: str
    extracted_meaning: str
    proposed_rule_family: str
    risk_tier: str
    status: str
    proposed_limitations: tuple[str, ...]
    batch_record_id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "proposed_limitations", tuple(self.proposed_limitations))
        for value, field_name in (
            (self.candidate_id, "candidate_id"),
            (self.source_id, "source_id"),
            (self.source_locator, "source_locator"),
            (self.extracted_meaning, "extracted_meaning"),
            (self.batch_record_id, "batch_record_id"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"liuyao candidate {field_name} is required")
        if not self.source_locator.startswith("page:"):
            raise ValueError("liuyao candidate locator must reference a page range")
        if len(self.extracted_meaning) > _TEXT_LIMIT:
            raise ValueError("liuyao candidate meaning exceeds the text boundary")
        if self.proposed_rule_family not in LIUYAO_RULE_FAMILIES:
            raise ValueError("liuyao candidate family is outside the namespace")
        if self.risk_tier not in {"ordinary", "sensitive", "high_risk"}:
            raise ValueError("liuyao candidate risk tier is invalid")
        if self.status not in {"approved", "promoted"}:
            raise ValueError("liuyao candidate status is invalid")
        if not self.proposed_limitations:
            raise ValueError("liuyao candidate requires limitation language")


@dataclass(frozen=True)
class LiuyaoReviewDecision:
    decision_id: str
    candidate_id: str
    decision: str
    reviewer: str
    reviewed_at: str
    rationale: str
    approval_limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "approval_limitations", tuple(self.approval_limitations)
        )
        for value, field_name in (
            (self.decision_id, "decision_id"),
            (self.candidate_id, "candidate_id"),
            (self.reviewer, "reviewer"),
            (self.reviewed_at, "reviewed_at"),
            (self.rationale, "rationale"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"liuyao review {field_name} is required")
        if self.decision != "approved":
            raise ValueError("liuyao review decision must be approved")
        if not self.approval_limitations:
            raise ValueError("liuyao review requires approval limitations")


@dataclass(frozen=True)
class LiuyaoPromotionBatch:
    promotion_batch_id: str
    candidate_ids: tuple[str, ...]
    target_evidence_ids: tuple[str, ...]
    review_status: str
    review_notes: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_ids", tuple(self.candidate_ids))
        object.__setattr__(self, "target_evidence_ids", tuple(self.target_evidence_ids))
        if not self.promotion_batch_id.strip():
            raise ValueError("liuyao promotion batch id is required")
        if self.review_status not in {"reviewed", "approved"}:
            raise ValueError("liuyao promotion batch review status is invalid")
        if not self.review_notes.strip():
            raise ValueError("liuyao promotion batch review notes are required")
        if not self.candidate_ids or len(self.candidate_ids) != len(
            self.target_evidence_ids
        ):
            raise ValueError("liuyao promotion batch links are invalid")
        if len(set(self.candidate_ids)) != len(self.candidate_ids) or len(
            set(self.target_evidence_ids)
        ) != len(self.target_evidence_ids):
            raise ValueError("liuyao promotion batch ids must be unique")


@dataclass(frozen=True)
class LiuyaoEvidenceUnit:
    evidence_id: str
    source_id: str
    source_ref: str
    theme: str
    rule_family: str
    risk_tier: str
    summary: str
    applicability: tuple[str, ...]
    limitations: tuple[str, ...]
    batch_record_id: str
    curation_batch_id: str
    confidence: str = "moderate"

    def __post_init__(self) -> None:
        object.__setattr__(self, "applicability", tuple(self.applicability))
        object.__setattr__(self, "limitations", tuple(self.limitations))
        for value, field_name in (
            (self.evidence_id, "evidence_id"),
            (self.source_id, "source_id"),
            (self.source_ref, "source_ref"),
            (self.theme, "theme"),
            (self.summary, "summary"),
            (self.batch_record_id, "batch_record_id"),
            (self.curation_batch_id, "curation_batch_id"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"liuyao evidence {field_name} is required")
        if not self.source_ref.startswith("page:"):
            raise ValueError("liuyao evidence source_ref must reference a page range")
        if len(self.summary) > _TEXT_LIMIT:
            raise ValueError("liuyao evidence summary exceeds the text boundary")
        if self.rule_family not in LIUYAO_RULE_FAMILIES:
            raise ValueError("liuyao evidence family is outside the namespace")
        if self.risk_tier not in {"ordinary", "sensitive", "high_risk"}:
            raise ValueError("liuyao evidence risk tier is invalid")
        if not self.applicability or not self.limitations:
            raise ValueError("liuyao evidence requires applicability and limitations")
        if self.confidence not in {"strong", "moderate", "weak"}:
            raise ValueError("liuyao evidence confidence is invalid")
        if self.risk_tier == "high_risk":
            joined = " ".join(self.limitations)
            if not any(marker in joined for marker in ("精确", "不输出")):
                raise ValueError(
                    "high_risk liuyao evidence requires non-exact boundary limitations"
                )


def _data_path(name: str, data_dir: Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir) / name
    return Path(
        str(resources.files("mingli_engine").joinpath(f"data/liuyao/{name}"))
    )


def _load_model_list(
    name: str,
    model,
    data_dir: Path | None = None,
) -> tuple:
    path = _data_path(name, data_dir)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LiuyaoKnowledgeError(f"the liuyao {name} ledger is unavailable") from error
    if not isinstance(raw, list):
        raise LiuyaoKnowledgeError(f"the liuyao {name} ledger must be a JSON array")
    try:
        records = tuple(model(**item) for item in raw)
    except (TypeError, ValueError) as error:
        raise LiuyaoKnowledgeError(f"the liuyao {name} ledger is invalid") from error
    return records


def load_liuyao_sources(
    data_dir: Path | None = None,
) -> tuple[LiuyaoSource, ...]:
    return _load_model_list("liuyao_sources.json", LiuyaoSource, data_dir)


def load_liuyao_candidates(
    data_dir: Path | None = None,
) -> tuple[LiuyaoCandidate, ...]:
    return _load_model_list("liuyao_candidates.json", LiuyaoCandidate, data_dir)


def load_liuyao_review_decisions(
    data_dir: Path | None = None,
) -> tuple[LiuyaoReviewDecision, ...]:
    return _load_model_list("liuyao_review_decisions.json", LiuyaoReviewDecision, data_dir)


def load_liuyao_promotion_batches(
    data_dir: Path | None = None,
) -> tuple[LiuyaoPromotionBatch, ...]:
    return _load_model_list(
        "liuyao_promotion_batches.json", LiuyaoPromotionBatch, data_dir
    )


def load_liuyao_evidence_units(
    data_dir: Path | None = None,
) -> tuple[LiuyaoEvidenceUnit, ...]:
    return _load_model_list("liuyao_evidence_units.json", LiuyaoEvidenceUnit, data_dir)


def validate_liuyao_knowledge_chain(data_dir: Path | None = None) -> None:
    """Validate cross-record links across the liuyao namespace."""
    sources = load_liuyao_sources(data_dir)
    candidates = load_liuyao_candidates(data_dir)
    reviews = load_liuyao_review_decisions(data_dir)
    batches = load_liuyao_promotion_batches(data_dir)
    units = load_liuyao_evidence_units(data_dir)
    source_ids = {item.source_id for item in sources}
    candidate_by_id = {item.candidate_id: item for item in candidates}
    if len(candidate_by_id) != len(candidates):
        raise LiuyaoKnowledgeError("liuyao candidate ids must be unique")
    for candidate in candidates:
        if candidate.source_id not in source_ids:
            raise LiuyaoKnowledgeError(
                f"{candidate.candidate_id} references an unknown liuyao source"
            )
    approved = {item.candidate_id for item in reviews}
    for candidate in candidates:
        if candidate.candidate_id not in approved:
            raise LiuyaoKnowledgeError(
                f"{candidate.candidate_id} lacks an approved liuyao review"
            )
    promoted_ids = {
        candidate_id
        for batch in batches
        if batch.review_status in {"reviewed", "approved"}
        for candidate_id in batch.candidate_ids
    }
    for candidate in candidates:
        if candidate.status == "promoted" and candidate.candidate_id not in promoted_ids:
            raise LiuyaoKnowledgeError(
                f"{candidate.candidate_id} requires a reviewed liuyao promotion batch"
            )
    evidence_ids = {item.evidence_id for item in units}
    if len(evidence_ids) != len(units):
        raise LiuyaoKnowledgeError("liuyao evidence ids must be unique")
    for unit in units:
        if unit.source_id not in source_ids:
            raise LiuyaoKnowledgeError(
                f"{unit.evidence_id} references an unknown liuyao source"
            )
    for batch in batches:
        for evidence_id in batch.target_evidence_ids:
            if evidence_id not in evidence_ids:
                raise LiuyaoKnowledgeError(
                    f"{batch.promotion_batch_id} references unknown liuyao evidence"
                )


@dataclass(frozen=True)
class LiuyaoFamilyMap:
    family_rules: tuple[tuple[str, tuple[str, ...]], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "family_rules",
            tuple(
                (family, tuple(keywords)) for family, keywords in self.family_rules
            ),
        )
        if not self.family_rules:
            raise ValueError("the liuyao family map is incomplete")
        for family, keywords in self.family_rules:
            if family not in LIUYAO_RULE_FAMILIES or not keywords:
                raise ValueError("liuyao family map rules are invalid")

    def map_family(self, rule_family: str) -> str:
        normalized = unicodedata.normalize("NFKC", rule_family).casefold()
        for family, keywords in self.family_rules:
            if any(
                unicodedata.normalize("NFKC", keyword).casefold() in normalized
                for keyword in keywords
            ):
                return family
        return "unmapped_family"


def load_liuyao_family_map(path: str | Path | None = None) -> LiuyaoFamilyMap:
    map_path = Path(path) if path is not None else _FAMILY_MAP_PATH
    try:
        payload_bytes = map_path.read_bytes()
        if sha256(payload_bytes).hexdigest() != _EXPECTED_FAMILY_MAP_SHA256:
            raise LiuyaoKnowledgeError("the liuyao family map is not frozen")
        raw = json.loads(
            payload_bytes.decode("utf-8"),
        )
    except LiuyaoKnowledgeError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LiuyaoKnowledgeError(
            "the liuyao family map could not be loaded"
        ) from error
    if not isinstance(raw, dict) or set(raw) != {
        "schema_version",
        "batch_id",
        "family_rules",
    }:
        raise LiuyaoKnowledgeError("the liuyao family map root fields are invalid")
    if (
        raw["schema_version"] != "liuyao-family-map-v1"
        or raw["batch_id"] != "batch_20260714"
    ):
        raise LiuyaoKnowledgeError("the liuyao family map root values are invalid")
    try:
        return LiuyaoFamilyMap(
            family_rules=tuple(
                (str(item["governed_family"]), tuple(item["keywords"]))
                for item in raw["family_rules"]
            )
        )
    except (TypeError, KeyError, ValueError) as error:
        raise LiuyaoKnowledgeError("the liuyao family map values are invalid") from error


def _liuyao_data_dir() -> Path:
    return Path(
        str(resources.files("mingli_engine").joinpath("data/liuyao"))
    )


def _write_model_list(path: Path, records: tuple) -> None:
    path.write_text(
        json.dumps(
            [asdict(item) for item in records],
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _liuyao_gate_candidate(
    meaning: str,
    limitations: tuple[str, ...],
) -> str | None:
    """Return a durable rejection reason, or None when the candidate passes."""
    if not limitations:
        return "the candidate carries no limitation language"
    if len(meaning) > _TEXT_LIMIT or any(len(item) > _TEXT_LIMIT for item in limitations):
        return "the candidate text exceeds the evidence boundary"
    normalized = unicodedata.normalize("NFKC", meaning + " " + " ".join(limitations))
    folded = normalized.casefold()
    if any(marker.casefold() in folded for marker in _PROHIBITED_ABSOLUTE_WORDING):
        return "the candidate contains prohibited absolute wording"
    if not safety_check(folded, disclaimer_present=True).allowed:
        return "the candidate fails the existing safety classifier"
    if not classify_high_risk_request(folded).allowed:
        return "the candidate fails the existing high-risk classifier"
    return None


def promote_liuyao_batch_candidates(
    batch_data_root: Path,
    *,
    generated_at: str,
    data_dir: Path | None = None,
) -> dict[str, object]:
    """Promote mapped batch_20260714 liuyao candidates into the namespace."""
    data_dir = Path(data_dir) if data_dir is not None else _liuyao_data_dir()
    if any(
        item.promotion_batch_id == LIUYAO_PROMOTION_BATCH_ID
        for item in load_liuyao_promotion_batches(data_dir)
    ):
        raise LiuyaoKnowledgeError("the liuyao batch promotion was already applied")
    family_map = load_liuyao_family_map()
    records = load_learning_records(
        batch_data_root / "batch_20260714_learning_records.json"
    )
    file_results = load_file_results(
        batch_data_root / "batch_20260714_file_results.json"
    )
    result_id_by_path = {item.relative_path: item.file_result_id for item in file_results.records}
    liuyao_records = [
        item
        for item in records.records
        if item.kind == "rule_candidate" and item.mapping_outcome == "liuyao"
    ]
    decisions: dict[str, str] = {}
    mapped: list[tuple[BatchLearningRecord, str]] = []
    seen_signatures: set[str] = set()

    for record in liuyao_records:
        mapped_family = family_map.map_family(record.payload["rule_family"])
        if mapped_family == "unmapped_family":
            decisions[record.record_id] = (
                "unmapped_family: no liuyao rule-family mapping covers this candidate"
            )
            continue
        meaning = record.payload["conclusion"]
        limitations = tuple(record.payload["limitations"])
        reason = _liuyao_gate_candidate(meaning, limitations)
        if reason is not None:
            decisions[record.record_id] = f"rejected_boundary: {reason}"
            continue
        signature = rule_candidate_signature(
            RuleCandidate(
                rule_family=mapped_family,
                trigger_conditions=tuple(record.payload["trigger_conditions"]),
                conclusion=meaning,
                limitations=limitations,
            )
        )
        if signature in seen_signatures:
            decisions[record.record_id] = (
                "duplicate_batch: an equivalent liuyao candidate was already retained"
            )
            continue
        seen_signatures.add(signature)
        mapped.append((record, mapped_family))
    if not mapped:
        raise LiuyaoKnowledgeError("no liuyao candidates passed the promotion gates")
    source_paths = sorted({item.relative_path for item, _ in mapped})
    sources = tuple(
        LiuyaoSource(
            source_id=f"liuyao_source_batch_20260714_{index:03d}",
            title=f"batch_20260714 liuyao source {index:03d}",
            batch_file_result_id=result_id_by_path[relative_path],
            scope_notes=(
                "batch_20260714 liuyao extraction source registered by the "
                "governed review pipeline; the tracked relative path is "
                "withheld from packaged assets for privacy."
            ),
            risk_notes=(),
        )
        for index, relative_path in enumerate(source_paths, start=1)
    )
    source_id_by_path = {
        relative_path: source.source_id
        for relative_path, source in zip(source_paths, sources, strict=True)
    }
    candidates: list[LiuyaoCandidate] = []
    reviews: list[LiuyaoReviewDecision] = []
    units: list[LiuyaoEvidenceUnit] = []
    for sequence, (record, mapped_family) in enumerate(mapped, start=1):
        candidate_id = f"liuyao_candidate_batch_20260714_{sequence:04d}"
        evidence_id = f"liuyao_evidence_batch_20260714_{sequence:04d}"
        risk_tier = "high_risk" if mapped_family == "high_risk_signal" else record.risk_tier
        if risk_tier == "high_risk":
            raise LiuyaoKnowledgeError(
                "high-risk liuyao candidates require curated narrowing first"
            )
        source_locator = record.source_locators[0]
        candidates.append(
            LiuyaoCandidate(
                candidate_id=candidate_id,
                source_id=source_id_by_path[record.relative_path],
                source_locator=source_locator,
                extracted_meaning=record.payload["conclusion"],
                proposed_rule_family=mapped_family,
                risk_tier=risk_tier,
                status="promoted",
                proposed_limitations=tuple(record.payload["limitations"]),
                batch_record_id=record.record_id,
            )
        )
        reviews.append(
            LiuyaoReviewDecision(
                decision_id=f"liuyao_review_{candidate_id}",
                candidate_id=candidate_id,
                decision="approved",
                reviewer=_LIUYAO_REVIEW_ACTOR,
                reviewed_at=_LIUYAO_REVIEW_DATE,
                rationale=(
                    "Passes the deterministic liuyao promotion gates: tranche-bound "
                    "page locators, governed namespace family mapping, no prohibited "
                    "absolute wording, safety and high-risk classifiers passed, and "
                    "no batch-internal signature duplicate."
                ),
                approval_limitations=tuple(record.payload["limitations"]),
            )
        )
        units.append(
            LiuyaoEvidenceUnit(
                evidence_id=evidence_id,
                source_id=source_id_by_path[record.relative_path],
                source_ref=source_locator,
                theme=record.payload["rule_family"],
                rule_family=mapped_family,
                risk_tier=risk_tier,
                summary=record.payload["conclusion"],
                applicability=tuple(record.payload["trigger_conditions"]),
                limitations=tuple(record.payload["limitations"]),
                batch_record_id=record.record_id,
                curation_batch_id=LIUYAO_CURATION_BATCH_ID,
            )
        )
        decisions[record.record_id] = f"promoted:{candidate_id}"
    batch = LiuyaoPromotionBatch(
        promotion_batch_id=LIUYAO_PROMOTION_BATCH_ID,
        candidate_ids=tuple(item.candidate_id for item in candidates),
        target_evidence_ids=tuple(item.evidence_id for item in units),
        review_status="reviewed",
        review_notes=(
            "Governed batch_20260714 liuyao review pipeline promotion into the "
            "independent liuyao evidence namespace."
        ),
    )
    paths = {
        "sources": data_dir / "liuyao_sources.json",
        "candidates": data_dir / "liuyao_candidates.json",
        "reviews": data_dir / "liuyao_review_decisions.json",
        "batches": data_dir / "liuyao_promotion_batches.json",
        "evidence": data_dir / "liuyao_evidence_units.json",
    }
    rollback_bytes = {path: path.read_bytes() for path in paths.values()}
    try:
        _write_model_list(paths["sources"], sources)
        _write_model_list(paths["candidates"], tuple(candidates))
        _write_model_list(paths["reviews"], tuple(reviews))
        _write_model_list(paths["batches"], (batch,))
        _write_model_list(paths["evidence"], tuple(units))
        validate_liuyao_knowledge_chain(data_dir)
    except Exception:
        for path, payload in rollback_bytes.items():
            path.write_bytes(payload)
        raise
    decision_counts: dict[str, int] = {}
    for decision in decisions.values():
        key = decision.split(":", maxsplit=1)[0]
        decision_counts[key] = decision_counts.get(key, 0) + 1
    return {
        "batch_id": "batch_20260714",
        "decision_counts": dict(sorted(decision_counts.items())),
        "generated_at": generated_at,
        "promoted_count": len(mapped),
        "registered_source_count": len(sources),
        "reviewed_candidate_count": len(liuyao_records),
    }
