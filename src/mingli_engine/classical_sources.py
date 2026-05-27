import json
from pathlib import Path
from typing import Any

from mingli_engine.models import (
    EXTRACTION_STATUSES,
    REPORT_USABLE_REVIEW_STATUS,
    REVIEW_STATUSES,
    RISK_TIERS,
    RULE_FAMILIES,
    SOURCE_TYPES,
    ClassicalSource,
    EvidenceUnit,
)


class ClassicalEvidenceError(ValueError):
    pass


_DATA_DIR = Path(__file__).resolve().parent / "data" / "classical_sources"


def _data_dir(data_dir: Path | str | None) -> Path:
    return Path(data_dir) if data_dir is not None else _DATA_DIR


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    try:
        raw_payload = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ClassicalEvidenceError(f"missing data file: {path.name}") from error

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as error:
        raise ClassicalEvidenceError(f"invalid JSON in {path.name}: {error}") from error

    if not isinstance(payload, list):
        raise ClassicalEvidenceError(f"{path.name} must contain a JSON array")
    if not all(isinstance(item, dict) for item in payload):
        raise ClassicalEvidenceError(f"{path.name} entries must be JSON objects")
    return payload


def _require_text(value: str, field_name: str, entry_id: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ClassicalEvidenceError(f"{entry_id} has empty {field_name}")


def _require_string_list(value: Any, field_name: str, entry_id: str) -> None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ClassicalEvidenceError(f"{entry_id} has invalid {field_name}")


def _source_from_dict(data: dict[str, Any]) -> ClassicalSource:
    try:
        source = ClassicalSource(**data)
    except TypeError as error:
        raise ClassicalEvidenceError(f"invalid source entry: {error}") from error

    for field_name in (
        "source_id",
        "title",
        "file_name",
        "source_type",
        "extraction_status",
        "review_status",
        "scope_notes",
    ):
        _require_text(getattr(source, field_name), field_name, source.source_id or "?")
    _require_string_list(source.risk_notes, "risk_notes", source.source_id)
    if source.source_type not in SOURCE_TYPES:
        raise ClassicalEvidenceError(
            f"{source.source_id} has unsupported source_type: {source.source_type}"
        )
    if source.extraction_status not in EXTRACTION_STATUSES:
        raise ClassicalEvidenceError(
            f"{source.source_id} has invalid extraction_status: "
            f"{source.extraction_status}"
        )
    if source.review_status not in REVIEW_STATUSES:
        raise ClassicalEvidenceError(
            f"{source.source_id} has invalid review_status: {source.review_status}"
        )
    return source


def _evidence_unit_from_dict(data: dict[str, Any]) -> EvidenceUnit:
    try:
        unit = EvidenceUnit(**data)
    except TypeError as error:
        raise ClassicalEvidenceError(f"invalid evidence unit: {error}") from error

    for field_name in (
        "evidence_id",
        "source_id",
        "source_ref",
        "theme",
        "rule_family",
        "risk_tier",
        "summary",
    ):
        _require_text(getattr(unit, field_name), field_name, unit.evidence_id or "?")
    _require_string_list(unit.applicability, "applicability", unit.evidence_id)
    _require_string_list(unit.limitations, "limitations", unit.evidence_id)
    if unit.rule_family not in RULE_FAMILIES:
        raise ClassicalEvidenceError(
            f"{unit.evidence_id} has unsupported rule_family: {unit.rule_family}"
        )
    if unit.risk_tier not in RISK_TIERS:
        raise ClassicalEvidenceError(
            f"{unit.evidence_id} has invalid risk_tier: {unit.risk_tier}"
        )
    if unit.risk_tier == "high_risk" and not unit.limitations:
        raise ClassicalEvidenceError(
            f"{unit.evidence_id} high_risk unit requires limitations"
        )
    if len(unit.summary) > 280:
        raise ClassicalEvidenceError(
            f"{unit.evidence_id} summary is too long for an evidence unit"
        )
    return unit


def _ensure_unique(ids: list[str], id_name: str) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise ClassicalEvidenceError(f"duplicate {id_name}: {item_id}")
        seen.add(item_id)


def load_classical_sources(data_dir: Path | str | None = None) -> list[ClassicalSource]:
    path = _data_dir(data_dir) / "sources.json"
    sources = [_source_from_dict(item) for item in _read_json_list(path)]
    _ensure_unique([source.source_id for source in sources], "source_id")
    return sources


def load_evidence_units(data_dir: Path | str | None = None) -> list[EvidenceUnit]:
    corpus_dir = _data_dir(data_dir)
    sources = load_classical_sources(corpus_dir)
    sources_by_id = {source.source_id: source for source in sources}
    path = corpus_dir / "evidence_units.json"
    units = [_evidence_unit_from_dict(item) for item in _read_json_list(path)]
    _ensure_unique([unit.evidence_id for unit in units], "evidence_id")
    for unit in units:
        source = sources_by_id.get(unit.source_id)
        if source is None:
            raise ClassicalEvidenceError(
                f"{unit.evidence_id} references unknown source: {unit.source_id}"
            )
        if source.review_status != REPORT_USABLE_REVIEW_STATUS:
            raise ClassicalEvidenceError(
                f"{unit.evidence_id} requires an approved source, "
                f"got {source.review_status}: {unit.source_id}"
            )
    return units


def load_approved_evidence_units(
    data_dir: Path | str | None = None,
) -> list[EvidenceUnit]:
    return load_evidence_units(data_dir)
