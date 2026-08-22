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
import re
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
LIUYAO_GAP_PROMOTION_BATCH_ID = "liuyao_promotion_batch_20260714_002"
LIUYAO_GAP_CURATION_BATCH_ID = "liuyao_curation_batch_20260822_001"
LIUYAO_CLASSICS_PROMOTION_BATCH_ID = "liuyao_promotion_batch_20260822_001"
LIUYAO_CLASSICS_CURATION_BATCH_ID = "liuyao_curation_batch_20260822_002"
_LIUYAO_REVIEW_ACTOR = "liuyao_batch_20260714_review_pipeline"
_LIUYAO_REVIEW_DATE = "2026-08-19"
_LIUYAO_GAP_REVIEW_DATE = "2026-08-22"
_LIUYAO_CLASSICS_REVIEW_DATE = "2026-08-22"

# Governed adjudications closing the two zero-evidence families (021 round 3).
# Each entry binds an already-extracted batch_20260714 rule candidate (gated
# out_of_scope_system -> liuyao by the intake pipeline but left unpromoted by
# the frozen keyword family map) to its governed family. The selections were
# adjudicated by direct reading of the recorded payloads: every entry carries
# a tranche-bound page locator and directly addresses the target family. No
# promoted category_judgment unit is re-scoped, and no rule is fabricated.
LIUYAO_GAP_PROMOTION_ADJUDICATIONS: tuple[tuple[str, str], ...] = (
    (
        # 世应爻位由八宫卦序固定口诀确定（含游魂、归魂特例）——世应结构规则
        "batch_20260714-02ae584ac6d1-006-o022-candidate-004",
        "shi_ying_relation",
    ),
    (
        # 世应相生相合为吉、相冲相克为凶（婚姻占断语境）——世应关系动态
        "batch_20260714-02ae584ac6d1-006-o027-candidate-002",
        "shi_ying_relation",
    ),
    (
        # 应期以用神旺衰并结合空亡、动爻状态判定——应期推断规则
        "batch_20260714-a0787a7d7f59-013-o002-candidate-004",
        "yingqi_timing",
    ),
)
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


@dataclass(frozen=True)
class LiuyaoClassicsReviewRecord:
    record_id: str
    work_title: str
    source_ref: str
    theme: str
    rule_family: str
    risk_tier: str
    confidence: str
    summary: str
    applicability: tuple[str, ...]
    limitations: tuple[str, ...]
    conflict_status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "applicability", tuple(self.applicability))
        object.__setattr__(self, "limitations", tuple(self.limitations))
        for value, field_name in (
            (self.record_id, "record_id"),
            (self.work_title, "work_title"),
            (self.source_ref, "source_ref"),
            (self.theme, "theme"),
            (self.summary, "summary"),
            (self.conflict_status, "conflict_status"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"liuyao classics review {field_name} is required")
        if not self.source_ref.startswith("page:") or "-" in self.source_ref:
            raise ValueError("liuyao classics review locator must be a single page")
        if self.rule_family not in LIUYAO_RULE_FAMILIES:
            raise ValueError("liuyao classics review family is outside the namespace")
        if self.risk_tier != "ordinary":
            raise ValueError("liuyao classics review risk tier must be ordinary")
        if self.confidence != "moderate":
            raise ValueError("liuyao classics review confidence must be moderate")
        if not self.applicability or not self.limitations:
            raise ValueError(
                "liuyao classics review requires applicability and limitations"
            )


@dataclass(frozen=True)
class LiuyaoClassicsCoverageDecision:
    source_ref: str
    disposition: str
    rationale: str
    linked_record_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "linked_record_ids", tuple(self.linked_record_ids)
        )
        for value, field_name in (
            (self.source_ref, "source_ref"),
            (self.disposition, "disposition"),
            (self.rationale, "rationale"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"liuyao classics coverage {field_name} is required"
                )
        if not self.source_ref.startswith("page:"):
            raise ValueError(
                "liuyao classics coverage locator must reference a page range"
            )
        if self.disposition not in {
            "promote",
            "promote_and_duplicate",
            "duplicate",
            "duplicate_and_conflict",
            "support_only",
            "conflict_logged",
        }:
            raise ValueError("liuyao classics coverage disposition is invalid")


@dataclass(frozen=True)
class LiuyaoTargetedClassicsReviewLedger:
    schema_version: str
    review_id: str
    source_id: str
    promotion_records: tuple[LiuyaoClassicsReviewRecord, ...]
    coverage: tuple[LiuyaoClassicsCoverageDecision, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "promotion_records", tuple(self.promotion_records)
        )
        object.__setattr__(self, "coverage", tuple(self.coverage))


_LIUYAO_CLASSICS_REVIEW_SCHEMA = "liuyao-targeted-classics-review-v1"
_LIUYAO_CLASSICS_REVIEW_ID = "liuyao_targeted_classics_review_20260822_001"
_LIUYAO_CLASSICS_SOURCE_ID = "liuyao_source_batch_20260714_001"
_LIUYAO_CLASSICS_RECORD_IDS = tuple(
    f"liuyao_classics_review_20260822_{index:04d}" for index in range(1, 8)
)
_LIUYAO_CLASSICS_SINGLE_PAGE = re.compile(r"page:[1-9][0-9]*")
_LIUYAO_CLASSICS_PAGE_RANGE = re.compile(
    r"page:([1-9][0-9]*)(?:-([1-9][0-9]*))?"
)
_LIUYAO_CLASSICS_REVIEW_RECORD_FIELDS = {
    "record_id",
    "work_title",
    "source_ref",
    "theme",
    "rule_family",
    "risk_tier",
    "confidence",
    "summary",
    "applicability",
    "limitations",
    "conflict_status",
}
_LIUYAO_CLASSICS_COVERAGE_FIELDS = {
    "source_ref",
    "disposition",
    "rationale",
    "linked_record_ids",
}
_LIUYAO_CLASSICS_RECORD_SCALAR_FIELDS = (
    _LIUYAO_CLASSICS_REVIEW_RECORD_FIELDS - {"applicability", "limitations"}
)


def _liuyao_classics_str_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _liuyao_classics_page_range_valid(locator: str) -> bool:
    match = _LIUYAO_CLASSICS_PAGE_RANGE.fullmatch(locator)
    if match is None:
        return False
    start, end = match.groups()
    return end is None or int(start) <= int(end)


def load_liuyao_targeted_classics_reviews(
    path: str | Path | None = None,
) -> LiuyaoTargetedClassicsReviewLedger:
    ledger_path = (
        Path(path)
        if path is not None
        else _data_path("liuyao_targeted_classics_reviews.json")
    )
    try:
        raw = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics review ledger is unavailable"
        ) from error
    if not isinstance(raw, dict) or set(raw) != {
        "schema_version",
        "review_id",
        "source_id",
        "promotion_records",
        "coverage",
    }:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics review root fields are invalid"
        )
    if raw["schema_version"] != _LIUYAO_CLASSICS_REVIEW_SCHEMA:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics review schema version is invalid"
        )
    if raw["review_id"] != _LIUYAO_CLASSICS_REVIEW_ID:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics review id is invalid"
        )
    if raw["source_id"] != _LIUYAO_CLASSICS_SOURCE_ID:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics review references an unknown source"
        )
    raw_records = raw["promotion_records"]
    raw_coverage = raw["coverage"]
    if not isinstance(raw_records, list) or not isinstance(raw_coverage, list):
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics review sections are invalid"
        )
    if len(raw_records) != 7:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics review must carry exactly 7 records"
        )
    for item in raw_records:
        if (
            not isinstance(item, dict)
            or set(item) != _LIUYAO_CLASSICS_REVIEW_RECORD_FIELDS
        ):
            raise LiuyaoKnowledgeError(
                "the liuyao targeted classics review record fields are invalid"
            )
        if not all(
            isinstance(item[key], str)
            for key in _LIUYAO_CLASSICS_RECORD_SCALAR_FIELDS
        ) or not (
            _liuyao_classics_str_list(item["applicability"])
            and _liuyao_classics_str_list(item["limitations"])
        ):
            raise LiuyaoKnowledgeError(
                "the liuyao targeted classics review record values are invalid"
            )
    for item in raw_coverage:
        if not isinstance(item, dict) or set(item) != _LIUYAO_CLASSICS_COVERAGE_FIELDS:
            raise LiuyaoKnowledgeError(
                "the liuyao targeted classics coverage fields are invalid"
            )
        if not all(
            isinstance(item[key], str)
            for key in ("source_ref", "disposition", "rationale")
        ) or not (
            isinstance(item["linked_record_ids"], list)
            and all(
                isinstance(link, str) and link.strip()
                for link in item["linked_record_ids"]
            )
        ):
            raise LiuyaoKnowledgeError(
                "the liuyao targeted classics coverage values are invalid"
            )
    try:
        records = tuple(
            LiuyaoClassicsReviewRecord(**item) for item in raw_records
        )
        coverage = tuple(
            LiuyaoClassicsCoverageDecision(**item) for item in raw_coverage
        )
    except (TypeError, ValueError) as error:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics review ledger is invalid"
        ) from error
    if tuple(item.record_id for item in records) != _LIUYAO_CLASSICS_RECORD_IDS:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics review record ids are not the "
            "frozen sequence"
        )
    for record in records:
        if _LIUYAO_CLASSICS_SINGLE_PAGE.fullmatch(record.source_ref) is None:
            raise LiuyaoKnowledgeError(
                "the liuyao targeted classics review locator is not a "
                "canonical single page"
            )
    for decision in coverage:
        if not _liuyao_classics_page_range_valid(decision.source_ref):
            raise LiuyaoKnowledgeError(
                "the liuyao targeted classics coverage locator is not a "
                "canonical page range"
            )
    known_ids = set(_LIUYAO_CLASSICS_RECORD_IDS)
    for decision in coverage:
        if not set(decision.linked_record_ids) <= known_ids:
            raise LiuyaoKnowledgeError(
                "the liuyao targeted classics coverage links an unknown record"
            )
    return LiuyaoTargetedClassicsReviewLedger(
        schema_version=raw["schema_version"],
        review_id=raw["review_id"],
        source_id=raw["source_id"],
        promotion_records=records,
        coverage=coverage,
    )


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
    classics_prefix = "liuyao_classics_review_"
    if any(
        item.batch_record_id.startswith(classics_prefix)
        for item in candidates
    ) or any(
        item.batch_record_id.startswith(classics_prefix)
        for item in units
    ):
        ledger = load_liuyao_targeted_classics_reviews(
            _data_path("liuyao_targeted_classics_reviews.json", data_dir)
        )
        record_by_id = {
            item.record_id: item for item in ledger.promotion_records
        }
        for candidate in candidates:
            if not candidate.batch_record_id.startswith(classics_prefix):
                continue
            record = record_by_id.get(candidate.batch_record_id)
            if record is None:
                raise LiuyaoKnowledgeError(
                    f"{candidate.candidate_id} references an unknown "
                    "liuyao classics review record"
                )
            if (
                candidate.source_id != ledger.source_id
                or candidate.source_locator != record.source_ref
                or candidate.proposed_rule_family != record.rule_family
                or candidate.extracted_meaning != record.summary
                or candidate.proposed_limitations != record.limitations
            ):
                raise LiuyaoKnowledgeError(
                    f"{candidate.candidate_id} diverges from its liuyao "
                    "classics review record"
                )
        for unit in units:
            if not unit.batch_record_id.startswith(classics_prefix):
                continue
            record = record_by_id.get(unit.batch_record_id)
            if record is None:
                raise LiuyaoKnowledgeError(
                    f"{unit.evidence_id} references an unknown "
                    "liuyao classics review record"
                )
            if (
                unit.source_id != ledger.source_id
                or unit.source_ref != record.source_ref
                or unit.rule_family != record.rule_family
                or unit.summary != record.summary
                or unit.limitations != record.limitations
            ):
                raise LiuyaoKnowledgeError(
                    f"{unit.evidence_id} diverges from its liuyao "
                    "classics review record"
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


def _liuyao_gate_classics_context(
    record: LiuyaoClassicsReviewRecord,
) -> str | None:
    """Gate the theme and applicability texts copied into formal evidence."""
    texts = (record.theme, *record.applicability)
    if any(len(item) > _TEXT_LIMIT for item in texts):
        return "the candidate text exceeds the evidence boundary"
    folded = unicodedata.normalize("NFKC", " ".join(texts)).casefold()
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


def promote_liuyao_family_gap_candidates(
    batch_data_root: Path,
    *,
    generated_at: str,
    data_dir: Path | None = None,
) -> dict[str, object]:
    """Promote adjudicated gap candidates into the namespace (append-only).

    Closes the two zero-evidence families (``shi_ying_relation`` and
    ``yingqi_timing``) using the governed adjudications in
    ``LIUYAO_GAP_PROMOTION_ADJUDICATIONS``. Reuses the same deterministic
    gates as the base promotion; existing records stay byte-identical in
    order, and any failure rolls the five ledgers back.
    """
    data_dir = Path(data_dir) if data_dir is not None else _liuyao_data_dir()
    sources = load_liuyao_sources(data_dir)
    candidates = list(load_liuyao_candidates(data_dir))
    reviews = list(load_liuyao_review_decisions(data_dir))
    batches = list(load_liuyao_promotion_batches(data_dir))
    units = list(load_liuyao_evidence_units(data_dir))
    batch_ids = {item.promotion_batch_id for item in batches}
    if LIUYAO_GAP_PROMOTION_BATCH_ID in batch_ids:
        raise LiuyaoKnowledgeError("the liuyao gap promotion was already applied")
    if LIUYAO_PROMOTION_BATCH_ID not in batch_ids:
        raise LiuyaoKnowledgeError(
            "the liuyao gap promotion requires the base promotion first"
        )
    records = load_learning_records(
        Path(batch_data_root) / "batch_20260714_learning_records.json"
    )
    file_results = load_file_results(
        Path(batch_data_root) / "batch_20260714_file_results.json"
    )
    result_id_by_path = {
        item.relative_path: item.file_result_id for item in file_results.records
    }
    source_id_by_result_id = {
        item.batch_file_result_id: item.source_id for item in sources
    }
    record_by_id = {item.record_id: item for item in records.records}
    promoted_record_ids = {item.batch_record_id for item in candidates}
    # The base ledger stores no trigger conditions on candidates, so the
    # cross-ledger duplicate check compares conclusion+limitations against the
    # existing rows, while full signatures dedupe the new gap rows themselves.
    base_text_pairs = {
        (item.extracted_meaning, item.proposed_limitations) for item in candidates
    }
    seen_signatures: set[str] = set()
    family_counts: dict[str, int] = {}
    for record_id, family in LIUYAO_GAP_PROMOTION_ADJUDICATIONS:
        if family not in LIUYAO_RULE_FAMILIES:
            raise LiuyaoKnowledgeError(
                "the liuyao gap adjudication targets a family outside the namespace"
            )
        record = record_by_id.get(record_id)
        if record is None:
            raise LiuyaoKnowledgeError(
                f"the liuyao gap adjudication references an unknown record {record_id}"
            )
        if record.kind != "rule_candidate" or record.mapping_outcome != "liuyao":
            raise LiuyaoKnowledgeError(
                f"{record_id} is not a liuyao-mapped rule candidate"
            )
        if record_id in promoted_record_ids:
            raise LiuyaoKnowledgeError(f"{record_id} is already promoted")
        meaning = record.payload["conclusion"]
        limitations = tuple(record.payload["limitations"])
        reason = _liuyao_gate_candidate(meaning, limitations)
        if reason is not None:
            raise LiuyaoKnowledgeError(f"rejected_boundary: {reason}")
        signature = rule_candidate_signature(
            RuleCandidate(
                rule_family=family,
                trigger_conditions=tuple(record.payload["trigger_conditions"]),
                conclusion=meaning,
                limitations=limitations,
            )
        )
        if signature in seen_signatures or (meaning, limitations) in base_text_pairs:
            raise LiuyaoKnowledgeError(
                "duplicate_batch: an equivalent liuyao candidate was already retained"
            )
        seen_signatures.add(signature)
        source_id = source_id_by_result_id.get(
            result_id_by_path.get(record.relative_path, "")
        )
        if source_id is None:
            raise LiuyaoKnowledgeError(
                f"{record_id} maps to no registered liuyao source"
            )
        sequence = len(candidates) + 1
        candidate_id = f"liuyao_candidate_batch_20260714_{sequence:04d}"
        evidence_id = f"liuyao_evidence_batch_20260714_{sequence:04d}"
        source_locator = record.source_locators[0]
        candidates.append(
            LiuyaoCandidate(
                candidate_id=candidate_id,
                source_id=source_id,
                source_locator=source_locator,
                extracted_meaning=meaning,
                proposed_rule_family=family,
                risk_tier=record.risk_tier,
                status="promoted",
                proposed_limitations=limitations,
                batch_record_id=record.record_id,
            )
        )
        reviews.append(
            LiuyaoReviewDecision(
                decision_id=f"liuyao_review_{candidate_id}",
                candidate_id=candidate_id,
                decision="approved",
                reviewer=_LIUYAO_REVIEW_ACTOR,
                reviewed_at=_LIUYAO_GAP_REVIEW_DATE,
                rationale=(
                    "Passes the deterministic liuyao promotion gates under the "
                    "021 round-3 gap adjudication: tranche-bound page locators, "
                    "governed namespace family assignment recorded in "
                    "LIUYAO_GAP_PROMOTION_ADJUDICATIONS, no prohibited absolute "
                    "wording, safety and high-risk classifiers passed, and no "
                    "ledger-internal signature duplicate."
                ),
                approval_limitations=limitations,
            )
        )
        units.append(
            LiuyaoEvidenceUnit(
                evidence_id=evidence_id,
                source_id=source_id,
                source_ref=source_locator,
                theme=record.payload["rule_family"],
                rule_family=family,
                risk_tier=record.risk_tier,
                summary=meaning,
                applicability=tuple(record.payload["trigger_conditions"]),
                limitations=limitations,
                batch_record_id=record.record_id,
                curation_batch_id=LIUYAO_GAP_CURATION_BATCH_ID,
            )
        )
        family_counts[family] = family_counts.get(family, 0) + 1
    new_candidate_ids = tuple(
        item.candidate_id for item in candidates[-len(LIUYAO_GAP_PROMOTION_ADJUDICATIONS):]
    )
    new_evidence_ids = tuple(
        item.evidence_id for item in units[-len(LIUYAO_GAP_PROMOTION_ADJUDICATIONS):]
    )
    batches.append(
        LiuyaoPromotionBatch(
            promotion_batch_id=LIUYAO_GAP_PROMOTION_BATCH_ID,
            candidate_ids=new_candidate_ids,
            target_evidence_ids=new_evidence_ids,
            review_status="reviewed",
            review_notes=(
                "Governed 021 round-3 gap promotion closing the zero-evidence "
                "families shi_ying_relation and yingqi_timing inside the "
                "independent liuyao evidence namespace; append-only over the "
                "frozen base batch."
            ),
        )
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
        _write_model_list(paths["batches"], tuple(batches))
        _write_model_list(paths["evidence"], tuple(units))
        validate_liuyao_knowledge_chain(data_dir)
    except Exception:
        for path, payload in rollback_bytes.items():
            path.write_bytes(payload)
        raise
    return {
        "batch_id": "batch_20260714",
        "family_counts": dict(sorted(family_counts.items())),
        "generated_at": generated_at,
        "promoted_count": len(LIUYAO_GAP_PROMOTION_ADJUDICATIONS),
        "promotion_batch_id": LIUYAO_GAP_PROMOTION_BATCH_ID,
        "total_evidence_count": len(units),
    }


def promote_liuyao_targeted_classics_candidates(
    *,
    generated_at: str,
    data_dir: Path | None = None,
) -> dict[str, object]:
    """Promote the 7 adjudicated classics review records (append-only).

    Reads the frozen targeted classics review ledger (a read-only input that
    stays outside the five-ledger rollback write set), reuses the same
    deterministic gates as the base and gap promotions, and appends the
    candidates, review decisions, promotion batch, and evidence units. Any
    failure rolls all five ledgers back to their pre-call bytes.
    """
    data_dir = Path(data_dir) if data_dir is not None else _liuyao_data_dir()
    sources = load_liuyao_sources(data_dir)
    candidates = list(load_liuyao_candidates(data_dir))
    reviews = list(load_liuyao_review_decisions(data_dir))
    batches = list(load_liuyao_promotion_batches(data_dir))
    units = list(load_liuyao_evidence_units(data_dir))
    batch_ids = {item.promotion_batch_id for item in batches}
    if LIUYAO_CLASSICS_PROMOTION_BATCH_ID in batch_ids:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics promotion was already applied"
        )
    if LIUYAO_PROMOTION_BATCH_ID not in batch_ids:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics promotion requires the base "
            "promotion first"
        )
    if LIUYAO_GAP_PROMOTION_BATCH_ID not in batch_ids:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics promotion requires the gap "
            "promotion first"
        )
    if tuple(item.promotion_batch_id for item in batches) != (
        LIUYAO_PROMOTION_BATCH_ID,
        LIUYAO_GAP_PROMOTION_BATCH_ID,
    ):
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics promotion requires the frozen "
            "base-then-gap batch sequence"
        )
    if len(candidates) != 70 or len(reviews) != 70 or len(units) != 70:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics promotion requires the frozen "
            "70-record predecessor state"
        )
    if tuple(item.candidate_id for item in candidates) != tuple(
        f"liuyao_candidate_batch_20260714_{index:04d}" for index in range(1, 71)
    ) or tuple(item.evidence_id for item in units) != tuple(
        f"liuyao_evidence_batch_20260714_{index:04d}" for index in range(1, 71)
    ):
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics promotion requires the frozen "
            "predecessor id sequence"
        )
    ledger = load_liuyao_targeted_classics_reviews(
        _data_path("liuyao_targeted_classics_reviews.json", data_dir)
    )
    if ledger.source_id not in {item.source_id for item in sources}:
        raise LiuyaoKnowledgeError(
            "the liuyao targeted classics review references an unknown "
            "liuyao source"
        )
    existing_signatures = {
        rule_candidate_signature(
            RuleCandidate(
                rule_family=item.rule_family,
                trigger_conditions=item.applicability,
                conclusion=item.summary,
                limitations=item.limitations,
            )
        )
        for item in units
    }
    seen_signatures: set[str] = set()
    family_counts: dict[str, int] = {}
    for record in ledger.promotion_records:
        if record.rule_family not in LIUYAO_RULE_FAMILIES:
            raise LiuyaoKnowledgeError(
                "the liuyao classics review targets a family outside the "
                "namespace"
            )
        if record.risk_tier != "ordinary":
            raise LiuyaoKnowledgeError(
                "the liuyao classics promotion only accepts ordinary records"
            )
        if "-" in record.source_ref:
            raise LiuyaoKnowledgeError(
                "the liuyao classics promotion requires a single page locator"
            )
        reason = _liuyao_gate_candidate(record.summary, record.limitations)
        if reason is None:
            reason = _liuyao_gate_classics_context(record)
        if reason is not None:
            raise LiuyaoKnowledgeError(f"rejected_boundary: {reason}")
        signature = rule_candidate_signature(
            RuleCandidate(
                rule_family=record.rule_family,
                trigger_conditions=record.applicability,
                conclusion=record.summary,
                limitations=record.limitations,
            )
        )
        if signature in seen_signatures or signature in existing_signatures:
            raise LiuyaoKnowledgeError(
                "duplicate_batch: an equivalent liuyao candidate was already "
                "retained"
            )
        seen_signatures.add(signature)
        sequence = len(candidates) + 1
        candidate_id = f"liuyao_candidate_batch_20260714_{sequence:04d}"
        evidence_id = f"liuyao_evidence_batch_20260714_{sequence:04d}"
        candidates.append(
            LiuyaoCandidate(
                candidate_id=candidate_id,
                source_id=ledger.source_id,
                source_locator=record.source_ref,
                extracted_meaning=record.summary,
                proposed_rule_family=record.rule_family,
                risk_tier=record.risk_tier,
                status="promoted",
                proposed_limitations=record.limitations,
                batch_record_id=record.record_id,
            )
        )
        reviews.append(
            LiuyaoReviewDecision(
                decision_id=f"liuyao_review_{candidate_id}",
                candidate_id=candidate_id,
                decision="approved",
                reviewer=_LIUYAO_REVIEW_ACTOR,
                reviewed_at=_LIUYAO_CLASSICS_REVIEW_DATE,
                rationale=(
                    "Passes the deterministic liuyao promotion gates under "
                    "the 022 targeted classics review: adjudicated single-page "
                    "locator verified against the original page, governed "
                    "namespace family assignment, conditionally narrowed "
                    "wording, no prohibited absolute wording, safety and "
                    "high-risk classifiers passed, unified without conflict, "
                    "and no ledger-internal signature duplicate."
                ),
                approval_limitations=record.limitations,
            )
        )
        units.append(
            LiuyaoEvidenceUnit(
                evidence_id=evidence_id,
                source_id=ledger.source_id,
                source_ref=record.source_ref,
                theme=record.theme,
                rule_family=record.rule_family,
                risk_tier=record.risk_tier,
                summary=record.summary,
                applicability=record.applicability,
                limitations=record.limitations,
                batch_record_id=record.record_id,
                curation_batch_id=LIUYAO_CLASSICS_CURATION_BATCH_ID,
            )
        )
        family_counts[record.rule_family] = (
            family_counts.get(record.rule_family, 0) + 1
        )
    promoted_total = len(ledger.promotion_records)
    batches.append(
        LiuyaoPromotionBatch(
            promotion_batch_id=LIUYAO_CLASSICS_PROMOTION_BATCH_ID,
            candidate_ids=tuple(
                item.candidate_id for item in candidates[-promoted_total:]
            ),
            target_evidence_ids=tuple(
                item.evidence_id for item in units[-promoted_total:]
            ),
            review_status="reviewed",
            review_notes=(
                "Governed 022 targeted classics promotion appending 7 "
                "single-page evidence units from the frozen review ledger "
                "inside the independent liuyao evidence namespace; evidence "
                "only, no inference interface or status change; append-only "
                "over the frozen base and gap batches."
            ),
        )
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
        _write_model_list(paths["batches"], tuple(batches))
        _write_model_list(paths["evidence"], tuple(units))
        validate_liuyao_knowledge_chain(data_dir)
    except Exception:
        for path, payload in rollback_bytes.items():
            path.write_bytes(payload)
        raise
    return {
        "family_counts": dict(sorted(family_counts.items())),
        "generated_at": generated_at,
        "promoted_count": promoted_total,
        "promotion_batch_id": LIUYAO_CLASSICS_PROMOTION_BATCH_ID,
        "total_evidence_count": len(units),
    }
