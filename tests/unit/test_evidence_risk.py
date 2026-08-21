"""Tests for the independent evidence-content risk classifier and promotion gate.

The classifier governs KNOWLEDGE EVIDENCE content (candidate extracts, learning
records, evidence units). It is deliberately separate from
``high_risk.classify_high_risk_request`` which governs user requests.
"""

import json
from pathlib import Path

import pytest

from mingli_engine import evidence_curation, promotion, source_intake
from mingli_engine.classical_sources import load_classical_sources, load_evidence_units, load_source_conflicts
from mingli_engine.evidence_risk import (
    DESCRIPTIVE_DEATH_CONTENT,
    EXACT_DEATH_LIFESPAN_RULE,
    ORDINARY_CONTENT,
    REQUIRED_DESCRIPTIVE_DEATH_LIMITATION,
    EvidenceContentRiskError,
    classify_evidence_content,
    enforce_promotion_content_gate,
)
from mingli_engine.source_intake import load_candidate_extracts

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Classifier: exact death/lifespan rules are never promotable
# ---------------------------------------------------------------------------


def test_classify_predictable_death_juncture_is_exact() -> None:
    risk = classify_evidence_content(
        "通过排命宫、大限、小限、月限，结合十二流年神煞，可预测死亡关口等信息。",
        ["为传统命理方法，无系统性实证"],
    )
    assert risk.risk_class == EXACT_DEATH_LIFESPAN_RULE


def test_classify_fatality_rate_verse_is_exact() -> None:
    risk = classify_evidence_content(
        "書稱「十有七亡」。",
        ["屬死亡壽夭斷語，僅描述性轉錄，需本地裁決"],
    )
    assert risk.risk_class == EXACT_DEATH_LIFESPAN_RULE


def test_classify_early_death_verse_is_exact() -> None:
    risk = classify_evidence_content(
        "書稱「早死無生」。",
        ["屬死亡斷語，僅描述性轉錄"],
    )
    assert risk.risk_class == EXACT_DEATH_LIFESPAN_RULE


def test_classify_lifespan_verdicts_are_exact() -> None:
    samples = [
        "父壽短；若在地支逢刑尅則母壽短",
        "书中以加总得数断寿终或成婚之岁。",
        "书内据此推得具体寿数断语（134例'55+1=55岁亡'）。",
        "传统程序视为死期信号，以命宫与限行推之。",
        "依次斷為富貴雙全、兄弟壽不長、老敗淒涼",
        "原文称单有此关不为大恶；组合情形主短命，男、女主短命分列",
    ]
    for meaning in samples:
        risk = classify_evidence_content(meaning, ["仅作描述"])
        assert risk.risk_class == EXACT_DEATH_LIFESPAN_RULE, meaning


def test_classify_untimely_death_is_exact() -> None:
    samples = [
        "子緣薄；若干支皆傷則兒女夭亡",
        "源文斷語：非夭則貧。",
        "Traditional verse pairs these respectively with 縱發而早年夭折.",
    ]
    for meaning in samples:
        risk = classify_evidence_content(meaning, ["仅作描述"])
        assert risk.risk_class == EXACT_DEATH_LIFESPAN_RULE, meaning


def test_classify_death_date_is_exact() -> None:
    risk = classify_evidence_content("以此法可断其死期。", ["仅作描述"])
    assert risk.risk_class == EXACT_DEATH_LIFESPAN_RULE


def test_classify_life_death_juncture_is_exact() -> None:
    risk = classify_evidence_content(
        "文本主张绳索被冲断时对应六亲有灾，甚至为生死关口。",
        ["仅作描述"],
    )
    assert risk.risk_class == EXACT_DEATH_LIFESPAN_RULE


def test_classify_quoted_death_verdicts_are_exact_even_with_framing() -> None:
    """A quoted condition→death verdict stays exact; descriptive framing in the
    limitations cannot downgrade an actionable fatality rule."""
    samples = [
        "書稱「父死他鄉」。",
        "源文稱若逢此殺必主死亡，並引書云辰戌為羅網。",
        "书中称必离婚或配偶死亡。",
        "第147页歌诀称“投江而死”",
        "文本谓七杀无制而身旺硬扛者一般不得善终、凶死于突发之灾。",
    ]
    for meaning in samples:
        risk = classify_evidence_content(meaning, ["僅作描述性轉錄，需本地裁決"])
        assert risk.risk_class == EXACT_DEATH_LIFESPAN_RULE, meaning


# ---------------------------------------------------------------------------
# Classifier: descriptive transcription -> high-risk, never ordinary
# ---------------------------------------------------------------------------


def test_classify_descriptive_case_transcription_is_descriptive() -> None:
    """The safe control: a clearly framed historical-case transcription with an
    explicit prohibition of real-world prediction stays learnable, but only as
    high-risk descriptive content."""
    risk = classify_evidence_content(
        "原书以此三层「克夫基因」加大运流年「引爆点」解释案例78丈夫死亡一事，仅作来源描述性记录",
        [
            "涉及死亡事件，属描述性内容，不构成生死推断规则",
            REQUIRED_DESCRIPTIVE_DEATH_LIMITATION,
        ],
    )
    assert risk.risk_class == DESCRIPTIVE_DEATH_CONTENT


def test_classify_risk_marker_framing_is_descriptive() -> None:
    risk = classify_evidence_content(
        "文本主张此为配偶易见疾病、离异或死亡的风险标记。",
        ["含死亡类断语，仅描述性转录，不作现实预测"],
    )
    assert risk.risk_class == DESCRIPTIVE_DEATH_CONTENT


def test_classify_death_adjacent_and_unclear_content_is_descriptive() -> None:
    samples = [
        (
            "书中断为凶命，所幸戊癸合绊不至于早夭，戊癸合被打破时应凶",
            ["单一坤造案例", "含夭折表述，仅作描述"],
        ),
        (
            "原文稱犯此關者子難求，囑勿入齋壇、休入喪孝家",
            ["「不幸者死亡」之語僅作描述，標記供本地裁定"],
        ),
        (
            "原文列出月份與日干之天德貴人對應，並以長壽、世世長年為斷語。",
            ["壽元內容僅描述性轉錄並標記本地裁決"],
        ),
        (
            "文本认为，在此情形下命主在该限运内可能应凶，案例包括意外死亡、自杀等。",
            ["不建议据此进行现实风险判断，仅作文化研究参考"],
        ),
    ]
    for meaning, limitations in samples:
        risk = classify_evidence_content(meaning, limitations)
        assert risk.risk_class == DESCRIPTIVE_DEATH_CONTENT, meaning


# ---------------------------------------------------------------------------
# Classifier: structural terms, negations, non-death content stay ordinary
# ---------------------------------------------------------------------------


def test_classify_negation_context_is_ordinary() -> None:
    risk = classify_evidence_content(
        "作为候选规则：书称冲破主大凶、冲去主该神离开命主而不主死亡",
        ["应验式表述无反例检验"],
    )
    assert risk.risk_class == ORDINARY_CONTENT


def test_classify_twelve_stage_terms_are_ordinary() -> None:
    risk = classify_evidence_content(
        "该书为各阶段配修持提示：临官防得意忘形、帝旺防盛极而衰、衰病死当乐天知命、墓库冲开则发",
        ["为譬喻式劝诫而非推断规则"],
    )
    assert risk.risk_class == ORDINARY_CONTENT


def test_classify_structural_terms_are_ordinary() -> None:
    samples = [
        "日主坐空亡之地则一生做事只怕有劳无功",
        "亡神入命与七杀同柱主耗散",
        "日主处死绝之地需看救应",
        "页面称金木相战多筋骨之伤, 水火相战多烧烫血光",
    ]
    for meaning in samples:
        risk = classify_evidence_content(meaning, ["无统计验证", "不构成事故预言"])
        assert risk.risk_class == ORDINARY_CONTENT, meaning


def test_classify_unrelated_content_is_ordinary() -> None:
    risk = classify_evidence_content(
        "按作者体系，刑冲即开库门之意；库空则开门收外物，库满则开门放出库中物。",
        ["库空库满的判定原文仅以仓库比喻说明"],
    )
    assert risk.risk_class == ORDINARY_CONTENT


# ---------------------------------------------------------------------------
# Promotion content gate
# ---------------------------------------------------------------------------


def test_gate_rejects_exact_content_at_any_tier() -> None:
    with pytest.raises(EvidenceContentRiskError):
        enforce_promotion_content_gate(
            meaning="書稱「父死他鄉」。",
            limitations=["僅作描述性轉錄"],
            risk_tier="high_risk",
            rule_family="high_risk_signal",
            owner_id="test",
        )


def test_gate_rejects_descriptive_content_as_ordinary() -> None:
    with pytest.raises(EvidenceContentRiskError):
        enforce_promotion_content_gate(
            meaning="原书以此解释案例78丈夫死亡一事，仅作来源描述性记录",
            limitations=[REQUIRED_DESCRIPTIVE_DEATH_LIMITATION],
            risk_tier="ordinary",
            rule_family="ten_god_relation",
            owner_id="test",
        )


def test_gate_rejects_descriptive_content_without_required_limitation() -> None:
    with pytest.raises(EvidenceContentRiskError):
        enforce_promotion_content_gate(
            meaning="原书以此解释案例78丈夫死亡一事，仅作来源描述性记录",
            limitations=["仅作描述"],
            risk_tier="high_risk",
            rule_family="high_risk_signal",
            owner_id="test",
        )


def test_gate_accepts_descriptive_content_in_governed_shape() -> None:
    enforce_promotion_content_gate(
        meaning="原书以此解释案例78丈夫死亡一事，仅作来源描述性记录",
        limitations=[REQUIRED_DESCRIPTIVE_DEATH_LIMITATION],
        risk_tier="high_risk",
        rule_family="high_risk_signal",
        owner_id="test",
    )


def test_gate_accepts_ordinary_content() -> None:
    enforce_promotion_content_gate(
        meaning="按作者体系，刑冲即开库门之意。",
        limitations=["无操作细则"],
        risk_tier="ordinary",
        rule_family="branch_interaction",
        owner_id="test",
    )


# ---------------------------------------------------------------------------
# Gate wiring: promotion.plan_promotion
# ---------------------------------------------------------------------------


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_gate_fixture(tmp_path: Path, *, meaning: str, risk_tier: str, family: str, limitations: list[str]) -> tuple[Path, Path]:
    intake_dir = tmp_path / "source_intake"
    corpus_dir = tmp_path / "classical_sources"
    intake_dir.mkdir()
    corpus_dir.mkdir()
    _write_json(
        intake_dir / "source_materials.json",
        [
            {
                "material_id": "material_test_pdf",
                "title": "Test Material",
                "material_type": "pdf",
                "file_label": "test.pdf",
                "tracking_status": "external_untracked",
                "preparation_status": "reviewed",
                "related_source_id": "source_test",
                "scope_notes": "Test scope.",
                "rights_notes": "Concise paraphrases only.",
                "gap_reason": "",
            }
        ],
    )
    _write_json(
        intake_dir / "candidate_extracts.json",
        [
            {
                "candidate_id": "candidate_test_001",
                "material_id": "material_test_pdf",
                "source_locator": "review-note:test#signal",
                "extracted_meaning": meaning,
                "proposed_rule_family": family,
                "risk_tier": risk_tier,
                "status": "approved",
                "proposed_limitations": limitations,
                "short_quote": "",
                "related_evidence_ids": [],
                "related_conflict_ids": [],
                "related_gap_ids": [],
                "duplicate_of": "",
                "created_by": "maintainer",
                "created_at": "2026-05-28",
            }
        ],
    )
    _write_json(
        intake_dir / "review_decisions.json",
        [
            {
                "decision_id": "review_candidate_test_001",
                "candidate_id": "candidate_test_001",
                "decision": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-05-28",
                "rationale": "Reviewable candidate.",
                "required_changes": [],
                "rejection_reason": "",
                "approval_limitations": ["Keep as conditional only."],
                "source_quality": "review_note",
                "confidence": "moderate",
            }
        ],
    )
    _write_json(
        intake_dir / "promotion_batches.json",
        [
            {
                "promotion_batch_id": "promotion_test_001",
                "candidate_ids": ["candidate_test_001"],
                "target_evidence_ids": ["evidence_test_001"],
                "review_status": "reviewed",
                "review_notes": "Approved for promotion.",
                "unresolved_issues": [],
            }
        ],
    )
    _write_json(
        corpus_dir / "sources.json",
        [
            {
                "source_id": "source_test",
                "title": "Test Source",
                "file_name": "test.pdf",
                "source_type": "pdf",
                "extraction_status": "converted",
                "review_status": "approved",
                "scope_notes": "Test source scope.",
                "risk_notes": ["high_risk_signal"],
                "curation_gap_reason": "",
                "review_reference": "",
            }
        ],
    )
    _write_json(corpus_dir / "evidence_units.json", [])
    _write_json(corpus_dir / "curation_batches.json", [])
    return intake_dir, corpus_dir


def test_plan_promotion_rejects_exact_death_candidate(tmp_path: Path) -> None:
    intake_dir, corpus_dir = _make_gate_fixture(
        tmp_path,
        meaning="書稱「父死他鄉」。",
        risk_tier="high_risk",
        family="high_risk_signal",
        limitations=["僅作描述性轉錄，不得作保證性斷言"],
    )
    with pytest.raises(promotion.PromotionError, match="not promotable"):
        promotion.plan_promotion(
            intake_dir=intake_dir,
            corpus_dir=corpus_dir,
            promotion_batch_id="promotion_test_001",
            evidence_overrides={
                "evidence_test_001": {
                    "theme": "high_risk_signal",
                    "applicability": ["结构条件"],
                    "school": "test",
                }
            },
            curation_batch_id="batch_test",
        )


def test_plan_promotion_rejects_descriptive_candidate_as_ordinary(tmp_path: Path) -> None:
    intake_dir, corpus_dir = _make_gate_fixture(
        tmp_path,
        meaning="原书以此解释案例78丈夫死亡一事，仅作来源描述性记录",
        risk_tier="ordinary",
        family="ten_god_relation",
        limitations=["仅作描述"],
    )
    with pytest.raises(promotion.PromotionError, match="high_risk"):
        promotion.plan_promotion(
            intake_dir=intake_dir,
            corpus_dir=corpus_dir,
            promotion_batch_id="promotion_test_001",
            evidence_overrides={
                "evidence_test_001": {
                    "theme": "ten_god_relation",
                    "applicability": ["结构条件"],
                    "school": "test",
                }
            },
            curation_batch_id="batch_test",
        )


# ---------------------------------------------------------------------------
# Real-data invariants (acceptance criteria)
# ---------------------------------------------------------------------------


def test_no_promoted_ordinary_candidate_carries_death_content() -> None:
    violations = []
    for candidate in load_candidate_extracts():
        if candidate.status not in {"approved", "promoted"}:
            continue
        if candidate.risk_tier != "ordinary":
            continue
        risk = classify_evidence_content(
            candidate.extracted_meaning, candidate.proposed_limitations
        )
        if risk.risk_class != ORDINARY_CONTENT:
            violations.append((candidate.candidate_id, risk.risk_class, risk.matched_marker))
    assert violations == []


def test_descriptive_candidates_use_governed_high_risk_shape() -> None:
    violations = []
    for candidate in load_candidate_extracts():
        if candidate.status not in {"approved", "promoted"}:
            continue
        risk = classify_evidence_content(
            candidate.extracted_meaning, candidate.proposed_limitations
        )
        if risk.risk_class != DESCRIPTIVE_DEATH_CONTENT:
            continue
        if candidate.risk_tier != "high_risk":
            violations.append((candidate.candidate_id, "risk_tier", candidate.risk_tier))
        if candidate.proposed_rule_family != "high_risk_signal":
            violations.append((candidate.candidate_id, "rule_family", candidate.proposed_rule_family))
        if candidate.candidate_id.startswith("candidate_batch_20260714_"):
            if REQUIRED_DESCRIPTIVE_DEATH_LIMITATION not in candidate.proposed_limitations:
                violations.append((candidate.candidate_id, "limitation", "missing"))
    assert violations == []


def test_no_ordinary_evidence_unit_carries_death_content() -> None:
    violations = []
    for unit in load_evidence_units():
        if unit.risk_tier != "ordinary":
            continue
        risk = classify_evidence_content(unit.summary, unit.limitations)
        if risk.risk_class != ORDINARY_CONTENT:
            violations.append((unit.evidence_id, risk.risk_class, risk.matched_marker))
    assert violations == []


def test_descriptive_evidence_units_carry_required_limitation() -> None:
    violations = []
    for unit in load_evidence_units():
        risk = classify_evidence_content(unit.summary, unit.limitations)
        if risk.risk_class != DESCRIPTIVE_DEATH_CONTENT:
            continue
        if unit.risk_tier != "high_risk":
            violations.append((unit.evidence_id, "risk_tier", unit.risk_tier))
        if unit.rule_family != "high_risk_signal":
            violations.append((unit.evidence_id, "rule_family", unit.rule_family))
        joined = " ".join(unit.limitations)
        if not any(marker in joined for marker in ("精确", "不输出", "拒绝", "不得")):
            violations.append((unit.evidence_id, "limitation", "missing boundary marker"))
        if unit.evidence_id.startswith("b20260714_evidence_"):
            if REQUIRED_DESCRIPTIVE_DEATH_LIMITATION not in unit.limitations:
                violations.append((unit.evidence_id, "limitation", "missing"))
    assert violations == []


def test_intake_and_curation_quality_gates_pass() -> None:
    assert source_intake.validate_intake_quality() == []
    sources = load_classical_sources()
    units = load_evidence_units()
    conflicts = load_source_conflicts()
    assert evidence_curation.validate_curation_quality(sources, units, conflicts) == []
